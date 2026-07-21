"""Functional tests for Task T232: Release Gate + Ed25519 Witness Signing."""
from __future__ import annotations

import base64
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Module loading (mirrors T230 pattern)
# ---------------------------------------------------------------------------
_gate_path = (
    Path(__file__).parent.parent.parent
    / "implementation" / "adapters" / "sia-target" / "release_gate.py"
)
_spec = importlib.util.spec_from_file_location("release_gate", _gate_path)
release_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release_gate)
sys.modules["release_gate"] = release_gate

evaluate_release_candidate = release_gate.evaluate_release_candidate
sign_witness = release_gate.sign_witness
verify_witness = release_gate.verify_witness
promote = release_gate.promote
generate_keypair = release_gate.generate_keypair
ReleaseGateError = release_gate.ReleaseGateError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dataset_manifest(grpo_count: int = 10, mean_reward: float = 0.5) -> dict:
    return {
        "version": "ds-2026.06.23",
        "grpo": {
            "count": grpo_count,
            "path": "/tmp/grpo_dataset.jsonl",
            "reward_stats": {"min": -0.9, "max": 0.99, "mean": mean_reward},
        },
        "sft": {"count": grpo_count, "path": "/tmp/sft.jsonl", "reward_threshold": 0.0},
        "total_trajectories": grpo_count * 2,
        "provenance": {
            "store_path": "/tmp/store",
            "output_path": "/tmp/out",
            "generated_at": "2026-06-23T10:15:00+00:00",
        },
    }


def _model_manifest(eval_score: float = 0.85, version: str = "0.1.0-synthetic") -> dict:
    return {
        "model_id": "sia-coder",
        "version": version,
        "artifact_path": "model.bin",
        "artifact_sha256": "deadbeef",
        "eval": {"score": eval_score, "metric": "pass@1"},
    }


def _write_json(directory: Path, name: str, data: dict) -> str:
    path = directory / name
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(path)


def _make_candidate(directory: Path, dataset: dict, model: dict) -> tuple[str, str]:
    ds_path = _write_json(directory, "dataset_manifest.json", dataset)
    model_path = _write_json(directory, "model_manifest.json", model)
    return ds_path, model_path


class _TempCase(unittest.TestCase):
    """Base case providing a self-cleaning tempdir + ephemeral keypair."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="t232_")
        self.tmp = Path(self._tmp)
        keys = generate_keypair(str(self.tmp / "keys"))
        self.private_key_path = keys["private_key_path"]
        self.public_key_path = keys["public_key_path"]

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------

class TestGateEvaluation(_TempCase):
    """evaluate_release_candidate — criteria pass/fail behaviour."""

    def _eval(self, dataset: dict, model: dict, config: dict | None = None) -> dict:
        ds_path, model_path = _make_candidate(self.tmp, dataset, model)
        return evaluate_release_candidate(ds_path, model_path, config)

    def test_gate_passes_when_all_criteria_met(self) -> None:
        result = self._eval(_dataset_manifest(), _model_manifest(), {
            "min_grpo_count": 5, "min_mean_reward": 0.2, "min_eval_score": 0.5,
        })
        self.assertTrue(result["passed"])
        self.assertEqual(result["reasons"], [])

    def test_gate_fails_when_grpo_count_below_threshold(self) -> None:
        result = self._eval(_dataset_manifest(grpo_count=2), _model_manifest(), {
            "min_grpo_count": 10,
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("min_grpo_count" in r for r in result["reasons"]))

    def test_gate_fails_when_mean_reward_below_threshold(self) -> None:
        result = self._eval(_dataset_manifest(mean_reward=0.1), _model_manifest(), {
            "min_mean_reward": 0.5,
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("min_mean_reward" in r for r in result["reasons"]))

    def test_gate_fails_when_eval_score_below_threshold(self) -> None:
        result = self._eval(_dataset_manifest(), _model_manifest(eval_score=0.3), {
            "min_eval_score": 0.8,
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("min_eval_score" in r for r in result["reasons"]))

    def test_gate_fails_on_missing_required_field(self) -> None:
        model = _model_manifest()
        del model["version"]
        result = self._eval(_dataset_manifest(), model, {
            "required_fields": ["model.model_id", "model.version"],
        })
        self.assertFalse(result["passed"])
        self.assertTrue(any("model.version" in r for r in result["reasons"]))

    def test_multiple_failures_all_listed(self) -> None:
        result = self._eval(_dataset_manifest(grpo_count=1, mean_reward=0.0),
                            _model_manifest(eval_score=0.1), {
            "min_grpo_count": 10, "min_mean_reward": 0.5, "min_eval_score": 0.8,
        })
        self.assertFalse(result["passed"])
        self.assertGreaterEqual(len(result["reasons"]), 3)

    def test_checked_dict_records_observations(self) -> None:
        result = self._eval(_dataset_manifest(), _model_manifest())
        self.assertIn("min_grpo_count", result["checked"])
        self.assertEqual(result["checked"]["min_grpo_count"]["observed"], 10)

    def test_missing_manifest_raises(self) -> None:
        with self.assertRaises(ReleaseGateError):
            evaluate_release_candidate(
                str(self.tmp / "nope.json"), str(self.tmp / "nope2.json"), {}
            )

    def test_corrupt_manifest_raises(self) -> None:
        bad = self.tmp / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        good = _write_json(self.tmp, "model_manifest.json", _model_manifest())
        with self.assertRaises(ReleaseGateError):
            evaluate_release_candidate(str(bad), good, {})

    def test_default_config_applied_when_none(self) -> None:
        result = self._eval(_dataset_manifest(), _model_manifest(), None)
        self.assertTrue(result["passed"])


# ---------------------------------------------------------------------------
# Signing + verification
# ---------------------------------------------------------------------------

class TestWitnessSigning(_TempCase):
    """sign_witness / verify_witness — cryptographic behaviour."""

    def _sign(self, payload: dict | None = None) -> dict:
        payload = payload or {"dataset": {"version": "v1"}, "model": {"version": "m1"}}
        return sign_witness(payload, self.private_key_path)

    def test_sign_produces_non_null_base64_signature(self) -> None:
        witness = self._sign()
        self.assertTrue(witness["signature"])
        decoded = base64.b64decode(witness["signature"], validate=True)
        self.assertEqual(len(decoded), 64)  # Ed25519 signature length

    def test_sign_includes_algorithm_and_timestamp(self) -> None:
        witness = self._sign()
        self.assertEqual(witness["algorithm"], "Ed25519")
        self.assertIn("signed_at", witness)
        self.assertIn("public_key", witness)

    def test_verify_true_for_fresh_manifest(self) -> None:
        witness = self._sign()
        self.assertTrue(verify_witness(witness, public_key_path=self.public_key_path))

    def test_verify_with_explicit_public_key_pem(self) -> None:
        witness = self._sign()
        self.assertTrue(verify_witness(witness, public_key_path=self.public_key_path))

    def test_verify_false_when_payload_tampered(self) -> None:
        witness = self._sign({"model": {"version": "m1"}})
        witness["payload"]["model"]["version"] = "m2-tampered"
        self.assertFalse(verify_witness(witness, public_key_path=self.public_key_path))

    def test_verify_false_when_signature_corrupted(self) -> None:
        witness = self._sign()
        raw = bytearray(base64.b64decode(witness["signature"]))
        raw[0] ^= 0xFF
        witness["signature"] = base64.b64encode(bytes(raw)).decode("ascii")
        self.assertFalse(verify_witness(witness, public_key_path=self.public_key_path))

    def test_verify_false_when_signature_missing(self) -> None:
        witness = self._sign()
        witness["signature"] = ""
        self.assertFalse(verify_witness(witness))

    def test_verify_false_when_signature_key_absent(self) -> None:
        witness = self._sign()
        del witness["signature"]
        self.assertFalse(verify_witness(witness))

    def test_verify_false_with_wrong_public_key(self) -> None:
        witness = self._sign()
        other = generate_keypair(str(self.tmp / "keys2"))
        self.assertFalse(verify_witness(witness, public_key_path=other["public_key_path"]))

    def test_verify_false_on_non_dict(self) -> None:
        self.assertFalse(verify_witness("not a dict"))  # type: ignore[arg-type]

    def test_verify_false_on_garbage_signature(self) -> None:
        witness = self._sign()
        witness["signature"] = "!!!not-base64!!!"
        self.assertFalse(verify_witness(witness))

    def test_verify_false_on_corrupt_embedded_public_key(self) -> None:
        witness = self._sign()
        witness["public_key"] = "!!!not-base64!!!"
        # Even in explicit integrity-only mode a corrupt embedded key fails.
        self.assertFalse(verify_witness(witness, trust_embedded_key=True))

    def test_sign_rejects_non_dict_payload(self) -> None:
        with self.assertRaises(ReleaseGateError):
            sign_witness("not a dict", self.private_key_path)  # type: ignore[arg-type]

    def test_sign_missing_private_key_raises(self) -> None:
        with self.assertRaises(ReleaseGateError):
            sign_witness({"a": 1}, str(self.tmp / "missing.key"))

    def test_determinism_same_payload_verifies(self) -> None:
        payload = {"dataset": {"version": "v1"}, "model": {"version": "m1"}}
        w1 = sign_witness(payload, self.private_key_path)
        w2 = sign_witness(payload, self.private_key_path)
        self.assertTrue(verify_witness(w1, public_key_path=self.public_key_path))
        self.assertTrue(verify_witness(w2, public_key_path=self.public_key_path))


# ---------------------------------------------------------------------------
# Promotion orchestration
# ---------------------------------------------------------------------------

class TestPromotion(_TempCase):
    """promote — gated deploy + witness emission."""

    def _promote(self, dataset: dict, model: dict, config: dict | None = None) -> dict:
        ds_path, model_path = _make_candidate(self.tmp, dataset, model)
        out_dir = self.tmp / "promote_out"
        return promote(
            ds_path, model_path, config, self.private_key_path, str(out_dir),
            trusted_public_key_path=self.public_key_path,
        )

    def test_promote_blocks_when_gate_fails(self) -> None:
        result = self._promote(_dataset_manifest(grpo_count=1), _model_manifest(), {
            "min_grpo_count": 100,
        })
        self.assertFalse(result["promoted"])
        self.assertIsNone(result["witness_path"])
        self.assertTrue(result["reasons"])
        self.assertFalse((self.tmp / "promote_out" / "witness.json").exists())

    def test_promote_emits_witness_when_gate_passes(self) -> None:
        result = self._promote(_dataset_manifest(), _model_manifest(), {
            "min_grpo_count": 5, "min_eval_score": 0.5,
        })
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["witness_path"])
        self.assertTrue(Path(result["witness_path"]).exists())

    def test_emitted_witness_verifies(self) -> None:
        result = self._promote(_dataset_manifest(), _model_manifest())
        witness = json.loads(Path(result["witness_path"]).read_text(encoding="utf-8"))
        self.assertTrue(verify_witness(witness, public_key_path=self.public_key_path))

    def test_witness_binds_dataset_and_model_versions(self) -> None:
        result = self._promote(_dataset_manifest(), _model_manifest(version="9.9.9"))
        witness = json.loads(Path(result["witness_path"]).read_text(encoding="utf-8"))
        payload = witness["payload"]
        self.assertEqual(payload["dataset"]["version"], "ds-2026.06.23")
        self.assertEqual(payload["model"]["version"], "9.9.9")
        self.assertIn("hash", payload["dataset"])
        self.assertTrue(payload["gate"]["passed"])

    def test_end_to_end_generate_promote_verify(self) -> None:
        work = Path(tempfile.mkdtemp(prefix="t232_e2e_"))
        try:
            keys = generate_keypair(str(work / "keys"))
            ds_path, model_path = _make_candidate(work, _dataset_manifest(), _model_manifest())
            result = promote(
                ds_path, model_path,
                {"min_grpo_count": 1, "min_eval_score": 0.5},
                keys["private_key_path"], str(work / "out"),
                trusted_public_key_path=keys["public_key_path"],
            )
            self.assertTrue(result["promoted"])
            witness = json.loads(Path(result["witness_path"]).read_text(encoding="utf-8"))
            self.assertTrue(verify_witness(witness, public_key_path=keys["public_key_path"]))
            # Tamper -> verification must fail.
            witness["payload"]["model"]["eval_score"] = 0.0
            self.assertFalse(verify_witness(witness, public_key_path=keys["public_key_path"]))
        finally:
            import shutil
            shutil.rmtree(work, ignore_errors=True)

    def test_keypair_private_key_not_world_readable(self) -> None:
        import stat
        mode = Path(self.private_key_path).stat().st_mode
        self.assertEqual(stat.S_IMODE(mode) & 0o077, 0)


# ---------------------------------------------------------------------------
# Trust anchor + artifact binding (SEC-001 / SEC-002)
# ---------------------------------------------------------------------------

class TestWitnessTrustAnchor(_TempCase):
    """verify_witness trust model + artifact-hash binding (security review fixes)."""

    def _sign(self, payload: dict, private_key_path: str | None = None) -> dict:
        return sign_witness(payload, private_key_path or self.private_key_path)

    def test_forgery_rejected_against_trusted_key(self) -> None:
        # Legitimate witness signed by trusted key A.
        legit = self._sign({"gate": {"passed": False}, "model": {"version": "m1"}})
        self.assertTrue(verify_witness(legit, public_key_path=self.public_key_path))
        # Attacker forges payload, signs with their OWN key B, embeds B's pubkey.
        attacker = generate_keypair(str(self.tmp / "attacker"))
        forged = self._sign(
            {"gate": {"passed": True}, "model": {"version": "evil-swap"}},
            private_key_path=attacker["private_key_path"],
        )
        # The forged witness self-verifies (integrity-only) but NOT against A.
        self.assertTrue(verify_witness(forged, trust_embedded_key=True))
        self.assertFalse(verify_witness(forged, public_key_path=self.public_key_path))

    def test_fail_closed_when_no_trust_anchor(self) -> None:
        witness = self._sign({"model": {"version": "m1"}})
        # No public_key_path and default trust_embedded_key=False -> fail closed.
        self.assertFalse(verify_witness(witness))

    def test_integrity_only_mode_verifies_untampered(self) -> None:
        witness = self._sign({"model": {"version": "m1"}})
        self.assertTrue(verify_witness(witness, trust_embedded_key=True))

    def test_freshly_generated_key_verifies_against_written_pub(self) -> None:
        keys = generate_keypair(str(self.tmp / "fresh"))
        witness = sign_witness({"model": {"version": "m1"}}, keys["private_key_path"])
        self.assertTrue(verify_witness(witness, public_key_path=keys["public_key_path"]))

    def test_committed_dev_anchor_is_valid_ed25519(self) -> None:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed
        anchor = (
            Path(__file__).parent.parent.parent
            / "implementation" / "adapters" / "sia-target" / "keys" / "witness-dev.pub"
        )
        key = load_pem_public_key(anchor.read_bytes())
        self.assertIsInstance(key, _ed.Ed25519PublicKey)

    def test_signed_payload_binds_artifact_sha256(self) -> None:
        ds_path, model_path = _make_candidate(self.tmp, _dataset_manifest(), _model_manifest())
        out_dir = self.tmp / "out_bind"
        result = promote(
            ds_path, model_path, {"min_grpo_count": 1, "min_eval_score": 0.5},
            self.private_key_path, str(out_dir),
            trusted_public_key_path=self.public_key_path,
        )
        self.assertTrue(result["promoted"])
        witness = json.loads(Path(result["witness_path"]).read_text(encoding="utf-8"))
        self.assertIn("artifact_sha256", witness["payload"]["model"])
        # Mutating the bound artifact hash invalidates the signature.
        witness["payload"]["model"]["artifact_sha256"] = "0" * 64
        self.assertFalse(verify_witness(witness, public_key_path=self.public_key_path))

    def test_artifact_path_hash_mismatch_blocks_promote(self) -> None:
        # Real artifact whose bytes do NOT match the declared artifact_sha256.
        (self.tmp / "model.bin").write_bytes(b"real model bytes that differ")
        model = _model_manifest()  # declares artifact_sha256="deadbeef"
        ds_path, model_path = _make_candidate(self.tmp, _dataset_manifest(), model)
        out_dir = self.tmp / "out_mismatch"
        result = promote(
            ds_path, model_path, {"min_grpo_count": 1, "min_eval_score": 0.5},
            self.private_key_path, str(out_dir),
            trusted_public_key_path=self.public_key_path,
        )
        self.assertFalse(result["promoted"])
        self.assertIsNone(result["witness_path"])
        self.assertFalse((out_dir / "witness.json").exists())


if __name__ == "__main__":
    unittest.main()
