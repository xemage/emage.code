#!/usr/bin/env python3
"""
Release gate + Ed25519 witness signing for the SIA model-promotion lifecycle.

Wraps curate -> train -> eval -> deploy: a model artifact cannot be promoted
unless it passes an evaluator gate, and every successful promotion emits a
cryptographically signed witness manifest tying the dataset version to the
model version.

T232: sia-harness Release Gate + Ed25519 Witness Signing

Security:
- Real Ed25519 signing via the ``cryptography`` package (no hand-rolled crypto).
- Private keys are loaded from a path supplied by argument or the
  ``SIA_WITNESS_PRIVATE_KEY`` environment variable. No key material in source.
- All writes are confined to ``output_path`` (no path traversal).
"""

import base64
import binascii
import hashlib
import json
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ALGORITHM = "Ed25519"
ENV_PRIVATE_KEY = "SIA_WITNESS_PRIVATE_KEY"

# Committed dev trust anchor (public key only) resolved relative to this module.
# Production verification must pin its own KMS/HSM-managed public key instead.
_DEFAULT_TRUST_ANCHOR = (
    pathlib.Path(__file__).resolve().parent / "keys" / "witness-dev.pub"
)

# Default gate criteria — callers override via gate_config.
DEFAULT_GATE_CONFIG: Dict[str, Any] = {
    "min_grpo_count": 1,
    "min_mean_reward": 0.0,
    "min_eval_score": 0.0,
    "required_fields": [
        "model.model_id",
        "model.version",
        "model.artifact_sha256",
    ],
}


class ReleaseGateError(Exception):
    """Raised on invalid release-gate inputs (missing/corrupt manifests)."""


# ---------------------------------------------------------------------------
# Path safety helper
# ---------------------------------------------------------------------------

def _assert_safe_path(candidate: str, root: str) -> pathlib.Path:
    """Resolve ``candidate`` and verify it does not escape ``root``."""
    root_path = pathlib.Path(root).resolve()
    resolved = pathlib.Path(candidate).resolve()
    try:
        resolved.relative_to(root_path)
    except ValueError as exc:
        raise ReleaseGateError(
            f"Path traversal detected: {candidate!r} escapes root {root!r}"
        ) from exc
    return resolved


# ---------------------------------------------------------------------------
# Manifest loading + dotted-path resolution
# ---------------------------------------------------------------------------

def _load_manifest(manifest_path: str) -> Dict[str, Any]:
    """Load a JSON manifest, raising ReleaseGateError on any problem."""
    path = pathlib.Path(manifest_path)
    if not path.is_file():
        raise ReleaseGateError(f"manifest not found: {manifest_path!r}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        raise ReleaseGateError(f"invalid manifest {manifest_path!r}: {exc}") from exc
    if not isinstance(data, dict):
        raise ReleaseGateError(f"manifest must be a JSON object: {manifest_path!r}")
    return data


def _resolve_dotted(context: Dict[str, Any], dotted: str) -> Tuple[bool, Any]:
    """Resolve ``a.b.c`` against nested dicts. Returns (found, value)."""
    current: Any = context
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


# ---------------------------------------------------------------------------
# Gate criterion checks
# ---------------------------------------------------------------------------

def _check_min(
    checked: Dict[str, Any],
    reasons: List[str],
    name: str,
    observed: Any,
    threshold: Any,
) -> None:
    """Record and validate a numeric ``observed >= threshold`` criterion."""
    ok = isinstance(observed, (int, float)) and observed >= threshold
    checked[name] = {"observed": observed, "threshold": threshold, "passed": ok}
    if not ok:
        reasons.append(f"{name}: observed={observed} < required={threshold}")


def _check_required_fields(
    checked: Dict[str, Any],
    reasons: List[str],
    context: Dict[str, Any],
    required_fields: List[str],
) -> None:
    """Record and validate presence of each dotted required field."""
    for field in required_fields:
        found, value = _resolve_dotted(context, field)
        present = found and value is not None
        checked[f"required_field:{field}"] = present
        if not present:
            reasons.append(f"missing required field: {field}")


def evaluate_release_candidate(
    dataset_manifest_path: str,
    model_manifest_path: str,
    gate_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Apply gate criteria to a dataset + model manifest pair.

    Returns ``{"passed": bool, "reasons": [...], "checked": {...}}``.
    On failure, ``reasons`` lists each failed criterion.
    """
    config = {**DEFAULT_GATE_CONFIG, **(gate_config or {})}
    dataset = _load_manifest(dataset_manifest_path)
    model = _load_manifest(model_manifest_path)
    context = {"dataset": dataset, "model": model}

    reasons: List[str] = []
    checked: Dict[str, Any] = {}

    _check_required_fields(checked, reasons, context, config["required_fields"])

    _, grpo_count = _resolve_dotted(dataset, "grpo.count")
    _check_min(checked, reasons, "min_grpo_count", grpo_count, config["min_grpo_count"])

    _, mean_reward = _resolve_dotted(dataset, "grpo.reward_stats.mean")
    _check_min(checked, reasons, "min_mean_reward", mean_reward, config["min_mean_reward"])

    _, eval_score = _resolve_dotted(model, "eval.score")
    _check_min(checked, reasons, "min_eval_score", eval_score, config["min_eval_score"])

    passed = not reasons
    logger.info("release gate: passed=%s reasons=%d", passed, len(reasons))
    return {"passed": passed, "reasons": reasons, "checked": checked}


# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

def generate_keypair(out_dir: str, key_name: str = "witness-dev") -> Dict[str, str]:
    """
    Generate a DEV Ed25519 keypair (PEM) under ``out_dir``.

    Writes ``<key_name>.ed25519.key`` (private, 0600) and ``<key_name>.pub``.
    Never use the generated private key in production — use a KMS/HSM instead.
    """
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    priv_path = out / f"{key_name}.ed25519.key"
    pub_path = out / f"{key_name}.pub"
    priv_path.write_bytes(priv_pem)
    os.chmod(priv_path, 0o600)
    pub_path.write_bytes(pub_pem)

    logger.info("generated dev keypair: %s (+ .pub)", priv_path)
    return {"private_key_path": str(priv_path), "public_key_path": str(pub_path)}


def _load_private_key(private_key_path: str) -> ed25519.Ed25519PrivateKey:
    """Load an Ed25519 private key from a PEM file. Raises on invalid key."""
    path = pathlib.Path(private_key_path)
    if not path.is_file():
        raise ReleaseGateError(f"private key not found: {private_key_path!r}")
    try:
        key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    except (ValueError, TypeError) as exc:
        raise ReleaseGateError(f"invalid private key: {exc}") from exc
    if not isinstance(key, ed25519.Ed25519PrivateKey):
        raise ReleaseGateError("private key is not an Ed25519 key")
    return key


def _load_public_key_pem(public_key_path: str) -> Optional[ed25519.Ed25519PublicKey]:
    """Load an Ed25519 public key from a PEM file, or None on failure."""
    path = pathlib.Path(public_key_path)
    if not path.is_file():
        return None
    try:
        key = serialization.load_pem_public_key(path.read_bytes())
    except (ValueError, TypeError):
        return None
    return key if isinstance(key, ed25519.Ed25519PublicKey) else None


# ---------------------------------------------------------------------------
# Canonicalisation + signing
# ---------------------------------------------------------------------------

def _canonicalize(payload: Dict[str, Any]) -> bytes:
    """Deterministic sorted-key, UTF-8 JSON encoding of ``payload``."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sign_witness(witness_payload: Dict[str, Any], private_key_path: str) -> Dict[str, Any]:
    """
    Sign a canonicalised witness payload with an Ed25519 private key.

    Returns the witness manifest with base64 signature + embedded raw public key.
    """
    if not isinstance(witness_payload, dict):
        raise ReleaseGateError("witness_payload must be a dict")

    private_key = _load_private_key(private_key_path)
    message = _canonicalize(witness_payload)
    signature = private_key.sign(message)

    public_raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return {
        "payload": witness_payload,
        "signature": base64.b64encode(signature).decode("ascii"),
        "public_key": base64.b64encode(public_raw).decode("ascii"),
        "algorithm": ALGORITHM,
        "signed_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def _resolve_public_key(
    witness_manifest: Dict[str, Any],
    public_key_path: Optional[str],
    trust_embedded_key: bool,
) -> Optional[ed25519.Ed25519PublicKey]:
    """
    Resolve the verification key under a fail-closed trust policy.

    A trusted PEM key file (``public_key_path``) is the only authenticity
    anchor. The embedded raw key proves integrity-against-corruption only and is
    used solely when the caller explicitly opts in via ``trust_embedded_key``.
    """
    if public_key_path:
        return _load_public_key_pem(public_key_path)
    if not trust_embedded_key:
        logger.warning(
            "verify_witness: no trust anchor supplied "
            "(public_key_path=None, trust_embedded_key=False); refusing to "
            "verify against the embedded key (fail-closed)"
        )
        return None
    logger.warning(
        "verify_witness: verifying against the EMBEDDED public key — this is "
        "integrity-only, NOT authenticity; an attacker-supplied key would pass"
    )
    embedded = witness_manifest.get("public_key")
    if not isinstance(embedded, str) or not embedded:
        return None
    try:
        raw = base64.b64decode(embedded, validate=True)
        return ed25519.Ed25519PublicKey.from_public_bytes(raw)
    except (binascii.Error, ValueError):
        return None


def verify_witness(
    witness_manifest: Dict[str, Any],
    public_key_path: Optional[str] = None,
    *,
    trust_embedded_key: bool = False,
) -> bool:
    """
    Verify a witness signature against its canonicalised payload.

    Authenticity is established ONLY against a trusted public key supplied via
    ``public_key_path``. By default (``trust_embedded_key=False`` and no
    ``public_key_path``) verification fails closed: the embedded key is never
    trusted implicitly, because an attacker can forge a payload, sign it with
    their own key, and embed that key.

    Set ``trust_embedded_key=True`` only when integrity-against-corruption
    (NOT authenticity) is acceptable — this path is explicitly opt-in.

    Returns True only when the signature is valid for the untampered payload
    under the resolved trusted key; False on any failure.
    """
    if not isinstance(witness_manifest, dict):
        return False
    payload = witness_manifest.get("payload")
    signature_b64 = witness_manifest.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_b64, str) or not signature_b64:
        return False
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (binascii.Error, ValueError):
        return False

    public_key = _resolve_public_key(witness_manifest, public_key_path, trust_embedded_key)
    if public_key is None:
        return False

    try:
        public_key.verify(signature, _canonicalize(payload))
        return True
    except InvalidSignature:
        return False


# ---------------------------------------------------------------------------
# Witness payload + promotion orchestrator
# ---------------------------------------------------------------------------

def _resolve_artifact_hash(model: Dict[str, Any], model_manifest_path: str) -> str:
    """
    Resolve the model artifact sha256, binding the actual bytes when available.

    Prefers the hash of the file at ``artifact_path`` (resolved relative to the
    manifest) over the declared ``artifact_sha256``. A declared hash that
    disagrees with the computed file hash is a fail-closed gate failure
    (defends against swapping model bytes while keeping the witness valid).
    """
    declared = model.get("artifact_sha256")
    artifact_path = model.get("artifact_path")
    computed: Optional[str] = None
    if isinstance(artifact_path, str) and artifact_path:
        candidate = pathlib.Path(model_manifest_path).resolve().parent / artifact_path
        if candidate.is_file():
            computed = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if computed is not None:
        if isinstance(declared, str) and declared and declared.lower() != computed:
            raise ReleaseGateError(
                f"model artifact hash mismatch: declared={declared!r} "
                f"!= computed={computed!r}"
            )
        return computed
    if isinstance(declared, str) and declared:
        return declared
    raise ReleaseGateError(
        "model artifact hash missing: no readable artifact_path bytes and no "
        "declared model.artifact_sha256"
    )


def _build_witness_payload(
    dataset_manifest_path: str,
    model_manifest_path: str,
    gate: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the witness payload binding dataset + model versions and gate result."""
    dataset = _load_manifest(dataset_manifest_path)
    model = _load_manifest(model_manifest_path)

    dataset_bytes = pathlib.Path(dataset_manifest_path).read_bytes()
    dataset_hash = hashlib.sha256(dataset_bytes).hexdigest()
    _, generated_at = _resolve_dotted(dataset, "provenance.generated_at")
    dataset_version = dataset.get("version") or generated_at or "unknown"

    _, grpo_count = _resolve_dotted(dataset, "grpo.count")
    _, mean_reward = _resolve_dotted(dataset, "grpo.reward_stats.mean")
    _, eval_score = _resolve_dotted(model, "eval.score")
    artifact_sha256 = _resolve_artifact_hash(model, model_manifest_path)

    return {
        "dataset": {
            "version": dataset_version,
            "hash": dataset_hash,
            "grpo_count": grpo_count,
            "mean_reward": mean_reward,
        },
        "model": {
            "model_id": model.get("model_id"),
            "version": model.get("version"),
            "eval_score": eval_score,
            "artifact_sha256": artifact_sha256,
        },
        "gate": {
            "passed": gate["passed"],
            "checked_count": len(gate["checked"]),
            "reasons": gate["reasons"],
        },
        "issued_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def promote(
    dataset_manifest_path: str,
    model_manifest_path: str,
    gate_config: Optional[Dict[str, Any]],
    private_key_path: str,
    output_path: str,
    *,
    trusted_public_key_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the release gate; emit a signed witness only when the gate passes.

    Gate failure blocks deploy: no witness is written and ``promoted`` is False
    with the failure reasons attached. After signing, the emitted witness is
    re-verified against ``trusted_public_key_path`` (defaulting to the committed
    dev anchor) as a fail-closed self-check; if that fails, the witness is
    discarded and promotion is reported as failed.
    """
    out_dir = pathlib.Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    gate = evaluate_release_candidate(dataset_manifest_path, model_manifest_path, gate_config)
    if not gate["passed"]:
        logger.warning("promotion blocked: %s", "; ".join(gate["reasons"]))
        return {"promoted": False, "gate": gate, "witness_path": None, "reasons": gate["reasons"]}

    try:
        payload = _build_witness_payload(dataset_manifest_path, model_manifest_path, gate)
    except ReleaseGateError as exc:
        logger.warning("promotion blocked: %s", exc)
        return {"promoted": False, "gate": gate, "witness_path": None, "reasons": [str(exc)]}

    witness = sign_witness(payload, private_key_path)
    witness_path = _assert_safe_path(str(out_dir / "witness.json"), str(out_dir))
    witness_path.write_text(
        json.dumps(witness, indent=2, sort_keys=True), encoding="utf-8"
    )

    anchor = trusted_public_key_path or str(_DEFAULT_TRUST_ANCHOR)
    if not verify_witness(witness, public_key_path=anchor):
        witness_path.unlink(missing_ok=True)
        reason = f"witness self-check failed against trust anchor: {anchor}"
        logger.error("promotion blocked: %s", reason)
        return {"promoted": False, "gate": gate, "witness_path": None, "reasons": [reason]}

    logger.info("promotion succeeded: witness written to %s", witness_path)
    return {"promoted": True, "gate": gate, "witness_path": str(witness_path), "reasons": []}
