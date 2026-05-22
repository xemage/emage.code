#!/usr/bin/env python3
"""v3 validation super-gate.

Checks v3 implementation contracts for:
- required artifact presence,
- cookbook schema and reference integrity,
- projection drift via verify-v3.mjs.

Usage:
    python3 scripts/check-v3.py
    python3 scripts/check-v3.py --schemas --cookbooks
    python3 scripts/check-v3.py --projection --root ../../../v2/implementation
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")

REQUIRED_COOKBOOK_FILES = ("agent.yaml", "README.md", "steering-examples.json")
REQUIRED_SCRIPTS = ("sync-v3.mjs", "verify-v3.mjs", "check-v3.py")


class GateResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checked: int = 0

    def err(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def ok(self) -> bool:
        return not self.errors


def _load_yaml(path: Path, result: GateResult) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # broad by design for concise gate reporting
        result.err(f"yaml: {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        result.err(f"yaml: {path}: root must be mapping")
        return {}
    return data


def _check_semver(value: str, label: str, result: GateResult) -> None:
    if not SEMVER_RE.match(value):
        result.err(f"{label}: invalid semver {value!r}")


def _check_required(root: Path, result: GateResult) -> None:
    scripts = root / "scripts"
    cookbooks = root / "cookbooks"

    if not scripts.is_dir():
        result.err(f"required: missing directory {scripts}")
    else:
        for name in REQUIRED_SCRIPTS:
            result.checked += 1
            if not (scripts / name).is_file():
                result.err(f"required: missing file {scripts / name}")

    result.checked += 1
    if not cookbooks.is_dir():
        result.err(f"required: missing directory {cookbooks}")
        return

    result.checked += 1
    if not (cookbooks / "README.md").is_file():
        result.err(f"required: missing file {cookbooks / 'README.md'}")


def _resolve_ref(base_dir: Path, rel_path: str, compat_knowledge_root: Path | None) -> Path:
    direct = (base_dir / rel_path).resolve()
    if direct.exists() or compat_knowledge_root is None:
        return direct

    marker = "knowledge/"
    normalized = rel_path.replace('\\', '/')
    if marker in normalized:
        suffix = normalized.split(marker, 1)[1]
        compat = (compat_knowledge_root / suffix).resolve()
        if compat.exists():
            return compat
    return direct


def _check_cookbooks(root: Path, compat_knowledge_root: Path | None, result: GateResult) -> None:
    cookbooks = root / "cookbooks"
    result.checked += 1
    if not cookbooks.is_dir():
        result.err(f"cookbooks: missing directory {cookbooks}")
        return

    dirs = sorted([d for d in cookbooks.iterdir() if d.is_dir()])
    if not dirs:
        result.warn("cookbooks: no cookbook directories found")

    for directory in dirs:
        for required in REQUIRED_COOKBOOK_FILES:
            result.checked += 1
            path = directory / required
            if not path.is_file():
                result.err(f"cookbooks: {directory.name} missing {required}")

        agent_path = directory / "agent.yaml"
        if not agent_path.is_file():
            continue

        data = _load_yaml(agent_path, result)
        if not data:
            continue

        required_fields = {
            "schema",
            "schemaVersion",
            "cookbookId",
            "name",
            "version",
            "description",
            "orchestrator",
            "workers",
            "handoffPolicy",
            "security",
        }
        missing = sorted(required_fields - set(data))
        if missing:
            result.err(f"cookbooks: {agent_path}: missing keys {missing}")
            continue

        _check_semver(str(data["schemaVersion"]), f"cookbooks: {agent_path}: schemaVersion", result)
        _check_semver(str(data["version"]), f"cookbooks: {agent_path}: version", result)

        cookbook_id = str(data["cookbookId"])
        if not ID_RE.match(cookbook_id):
            result.err(f"cookbooks: {agent_path}: invalid cookbookId {cookbook_id!r}")

        orchestrator = data["orchestrator"]
        if not isinstance(orchestrator, dict):
            result.err(f"cookbooks: {agent_path}: orchestrator must be mapping")
            continue

        orchestrator_ref = orchestrator.get("ref")
        if not isinstance(orchestrator_ref, str) or not orchestrator_ref:
            result.err(f"cookbooks: {agent_path}: orchestrator.ref must be non-empty string")

        workers = data["workers"]
        if not isinstance(workers, list) or not workers:
            result.err(f"cookbooks: {agent_path}: workers must be non-empty list")
            continue

        worker_refs: set[str] = set()
        for idx, worker in enumerate(workers):
            if not isinstance(worker, dict):
                result.err(f"cookbooks: {agent_path}: workers[{idx}] must be mapping")
                continue
            ref = worker.get("ref")
            max_concurrency = worker.get("maxConcurrency")
            if not isinstance(ref, str) or not ref:
                result.err(f"cookbooks: {agent_path}: workers[{idx}].ref must be non-empty string")
            elif ref in worker_refs:
                result.err(f"cookbooks: {agent_path}: duplicate worker ref {ref!r}")
            else:
                worker_refs.add(ref)

            if not isinstance(max_concurrency, int) or max_concurrency < 1:
                result.err(
                    f"cookbooks: {agent_path}: workers[{idx}].maxConcurrency must be int >= 1"
                )

            for skill_path in worker.get("skills", []):
                if not isinstance(skill_path, str):
                    result.err(
                        f"cookbooks: {agent_path}: workers[{idx}].skills entries must be strings"
                    )
                    continue
                resolved = _resolve_ref(directory, skill_path, compat_knowledge_root)
                result.checked += 1
                if not resolved.exists():
                    result.err(
                        f"cookbooks: {agent_path}: unresolved workers[{idx}].skills path {skill_path}"
                    )

        for instruction_path in orchestrator.get("instructions", []):
            if not isinstance(instruction_path, str):
                result.err(f"cookbooks: {agent_path}: orchestrator.instructions entries must be strings")
                continue
            resolved = _resolve_ref(directory, instruction_path, compat_knowledge_root)
            result.checked += 1
            if not resolved.exists():
                result.err(
                    f"cookbooks: {agent_path}: unresolved orchestrator.instructions path {instruction_path}"
                )

        for skill_path in orchestrator.get("skills", []):
            if not isinstance(skill_path, str):
                result.err(f"cookbooks: {agent_path}: orchestrator.skills entries must be strings")
                continue
            resolved = _resolve_ref(directory, skill_path, compat_knowledge_root)
            result.checked += 1
            if not resolved.exists():
                result.err(
                    f"cookbooks: {agent_path}: unresolved orchestrator.skills path {skill_path}"
                )

        handoff = data.get("handoffPolicy")
        if not isinstance(handoff, dict):
            result.err(f"cookbooks: {agent_path}: handoffPolicy must be mapping")
        else:
            default_action = handoff.get("defaultAction")
            if default_action not in {"deny", "ask", "allow"}:
                result.err(
                    f"cookbooks: {agent_path}: handoffPolicy.defaultAction must be deny|ask|allow"
                )
            routes = handoff.get("allowRoutes")
            if not isinstance(routes, list) or not routes:
                result.err(f"cookbooks: {agent_path}: handoffPolicy.allowRoutes must be non-empty list")
            else:
                for i, route in enumerate(routes):
                    if not isinstance(route, dict):
                        result.err(f"cookbooks: {agent_path}: allowRoutes[{i}] must be mapping")
                        continue
                    from_ref = route.get("from")
                    to_ref = route.get("to")
                    if from_ref != orchestrator_ref:
                        result.err(
                            f"cookbooks: {agent_path}: allowRoutes[{i}].from must match orchestrator.ref"
                        )
                    if not isinstance(to_ref, str) or to_ref not in worker_refs:
                        result.err(
                            f"cookbooks: {agent_path}: allowRoutes[{i}].to must reference a worker ref"
                        )

        security = data.get("security")
        if not isinstance(security, dict):
            result.err(f"cookbooks: {agent_path}: security must be mapping")
        else:
            allow_secrets = security.get("allowSecretsInPayload")
            require_schema = security.get("requireSchemaValidation")
            if allow_secrets is not False:
                result.err(
                    f"cookbooks: {agent_path}: security.allowSecretsInPayload must be false"
                )
            if require_schema is not True:
                result.err(
                    f"cookbooks: {agent_path}: security.requireSchemaValidation must be true"
                )

        steering_path = directory / "steering-examples.json"
        if steering_path.is_file():
            result.checked += 1
            try:
                steering = json.loads(steering_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                result.err(f"cookbooks: {steering_path}: invalid json: {exc}")
                steering = {}
            if isinstance(steering, dict):
                examples = steering.get("examples")
                if not isinstance(examples, list) or not examples:
                    result.err(f"cookbooks: {steering_path}: examples must be non-empty array")


def _check_projection(target_root: Path, gate_root: Path, result: GateResult) -> None:
    verify_script = gate_root / "scripts" / "verify-v3.mjs"
    result.checked += 1
    if not verify_script.is_file():
        result.err(f"projection: missing verify script {verify_script}")
        return

    proc = subprocess.run(
        ["node", str(verify_script), f"--root={target_root}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        output = (proc.stdout + proc.stderr).strip()
        result.err(f"projection: drift or sync failure\n{output}")


def _load_validator_module(path: Path):
    import sys

    spec = importlib.util.spec_from_file_location("v3_handoff_validator", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"unable to load validator module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _check_handoff_security(root: Path, result: GateResult) -> None:
    runtime_dir = root / "runtime" / "handoff"
    schema_path = runtime_dir / "schema-v1.json"
    validator_path = runtime_dir / "validator.py"
    example_path = runtime_dir / "examples" / "valid-handoff.json"
    cookbook_path = root / "cookbooks" / "core-delivery" / "agent.yaml"
    artifact_path = root.parents[1] / "docs" / "artifacts" / "v3-handoff-security-model-v1.md"

    for path in (schema_path, validator_path, example_path, cookbook_path, artifact_path):
        result.checked += 1
        if not path.is_file():
            result.err(f"handoff-security: missing required file {path}")

    if result.errors:
        return

    try:
        json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.err(f"handoff-security: invalid json schema {schema_path}: {exc}")
        return

    try:
        payload = json.loads(example_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.err(f"handoff-security: invalid example payload json {example_path}: {exc}")
        return

    try:
        validator = _load_validator_module(validator_path)
    except Exception as exc:  # broad by design for gate output
        result.err(f"handoff-security: unable to import validator: {exc}")
        return

    verdict = validator.validate_handoff_payload(payload)
    result.checked += 1
    if not getattr(verdict, "ok", False):
        result.err(f"handoff-security: valid payload rejected: {getattr(verdict, 'errors', [])}")

    routes = validator.load_allow_routes_from_cookbook(cookbook_path)
    result.checked += 1
    if not validator.route_allowed("orchestrator", "backend-engineer", routes):
        result.err("handoff-security: expected allow route orchestrator->backend-engineer not found")

    result.checked += 1
    if validator.route_allowed("backend-engineer", "orchestrator", routes):
        result.err("handoff-security: reverse route backend-engineer->orchestrator must be denied")

    bad_payload = json.loads(json.dumps(payload))
    bad_payload["payload"]["token"] = "should-not-pass"
    bad_verdict = validator.validate_handoff_payload(bad_payload)
    result.checked += 1
    if getattr(bad_verdict, "ok", True):
        result.err("handoff-security: payload containing secret-like key must be rejected")


def _check_hook_policy_spec(root: Path, result: GateResult) -> None:
    spec_path = root.parents[1] / "docs" / "artifacts" / "v3-hook-policy-spec-v1.md"
    result.checked += 1
    if not spec_path.is_file():
        result.err(f"hook-policy: missing artifact {spec_path}")
        return

    text = spec_path.read_text(encoding="utf-8")

    required_markers = {
        "inspect": "hook-policy: missing inspect hook taxonomy",
        "decide": "hook-policy: missing decide hook taxonomy",
        "transform": "hook-policy: missing transform hook taxonomy",
        "Lifecycle Timing": "hook-policy: missing lifecycle timing section",
        "Policy Precedence": "hook-policy: missing policy precedence section",
        "Fail-Closed": "hook-policy: missing fail-closed semantics section",
        "Copilot": "hook-policy: missing Copilot compatibility note",
        "Gemini": "hook-policy: missing Gemini compatibility note",
        "Opencode": "hook-policy: missing Opencode compatibility note",
    }
    for marker, error_message in required_markers.items():
        result.checked += 1
        if marker not in text:
            result.err(error_message)


def _check_telemetry(root: Path, result: GateResult) -> None:
    telemetry_dir = root / "runtime" / "telemetry"
    schema_path = telemetry_dir / "schema-v1.json"
    replay_path = telemetry_dir / "replay.py"
    baseline_path = telemetry_dir / "examples" / "baseline-run.json"
    candidate_path = telemetry_dir / "examples" / "candidate-run.json"
    artifact_path = root.parents[1] / "docs" / "artifacts" / "v3-telemetry-schema-v1.md"

    required = (schema_path, replay_path, baseline_path, candidate_path, artifact_path)
    for path in required:
        result.checked += 1
        if not path.is_file():
            result.err(f"telemetry: missing required file {path}")

    if result.errors:
        return

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.err(f"telemetry: invalid json fixture or schema: {exc}")
        return

    result.checked += 1
    if "events" not in baseline or not isinstance(baseline["events"], list):
        result.err("telemetry: baseline fixture missing events array")
    result.checked += 1
    if "events" not in candidate or not isinstance(candidate["events"], list):
        result.err("telemetry: candidate fixture missing events array")

    result.checked += 1
    if schema.get("title") != "emage.code v3 telemetry trajectory":
        result.err("telemetry: schema title does not match expected contract")

    report_path = telemetry_dir / "examples" / "telemetry-replay-report.json"
    proc = subprocess.run(
        [
            "python3",
            str(replay_path),
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--out",
            str(report_path),
        ],
        capture_output=True,
        text=True,
    )
    result.checked += 1
    if proc.returncode == 0:
        result.err("telemetry: replay expected regression for fixture pair but returned success")

    result.checked += 1
    if not report_path.is_file():
        result.err("telemetry: replay did not emit report artifact")
        return

    report = json.loads(report_path.read_text(encoding="utf-8"))
    result.checked += 1
    if not report.get("summary", {}).get("hasRegression", False):
        result.err("telemetry: replay report must mark hasRegression=true for fixture pair")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--required", action="store_true", help="check required files")
    parser.add_argument("--schemas", action="store_true", help="check schema-level metadata")
    parser.add_argument("--cookbooks", action="store_true", help="check cookbook manifests")
    parser.add_argument("--projection", action="store_true", help="check projection drift")
    parser.add_argument(
        "--handoff-security",
        action="store_true",
        help="check handoff schema, route allowlists, and fail-closed behavior",
    )
    parser.add_argument(
        "--hook-policy",
        action="store_true",
        help="check hook and policy taxonomy artifact coverage",
    )
    parser.add_argument(
        "--telemetry",
        action="store_true",
        help="check telemetry schema, fixtures, and replay report generation",
    )
    parser.add_argument(
        "--compat-knowledge-root",
        default="",
        help="optional fallback knowledge root used to resolve cookbook references during migration",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    compat_knowledge_root = Path(args.compat_knowledge_root).resolve() if args.compat_knowledge_root else None
    if compat_knowledge_root is None:
        candidate = root.parents[1] / "v2" / "implementation" / "knowledge"
        if candidate.is_dir():
            compat_knowledge_root = candidate

    selected = {
        "required": args.required,
        "schemas": args.schemas,
        "cookbooks": args.cookbooks,
        "projection": args.projection,
        "handoff-security": args.handoff_security,
        "hook-policy": args.hook_policy,
        "telemetry": args.telemetry,
    }
    run_all = not any(selected.values())

    result = GateResult()

    if run_all or selected["required"]:
        _check_required(root, result)

    if run_all or selected["schemas"]:
        schema_doc = root.parents[1] / "docs" / "artifacts" / "v3-schema-contract-v1.md"
        result.checked += 1
        if not schema_doc.is_file():
            result.err(f"schemas: missing contract artifact {schema_doc}")

    if run_all or selected["cookbooks"]:
        _check_cookbooks(root, compat_knowledge_root, result)

    if run_all or selected["projection"]:
        _check_projection(root, Path(__file__).resolve().parents[1], result)

    if run_all or selected["handoff-security"]:
        _check_handoff_security(root, result)

    if run_all or selected["hook-policy"]:
        _check_hook_policy_spec(root, result)

    if run_all or selected["telemetry"]:
        _check_telemetry(root, result)

    if result.warnings:
        print(f"WARN - {len(result.warnings)} warning(s):")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.errors:
        print(f"FAIL - {len(result.errors)} error(s) across {result.checked} checks:")
        for error in result.errors:
            print(f"  - {error}")
        return 1

    print(f"OK - {result.checked} checks passed, 0 errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
