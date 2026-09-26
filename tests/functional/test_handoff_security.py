"""Security checks for v3 handoff validation and routing."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.repo import current_implementation_root, repo_root


class TestV3HandoffSecurity(unittest.TestCase):
    def _load_validator(self):
        import importlib.util
        import sys

        validator_path = current_implementation_root() / "runtime" / "handoff" / "validator.py"
        spec = importlib.util.spec_from_file_location("v3_handoff_validator", validator_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def _load_valid_payload(self) -> dict:
        payload_path = (
            current_implementation_root()
            / "runtime"
            / "handoff"
            / "examples"
            / "valid-handoff.json"
        )
        return json.loads(payload_path.read_text(encoding="utf-8"))

    def test_valid_payload_and_route_pass(self):
        module = self._load_validator()
        payload = self._load_valid_payload()
        result = module.validate_handoff_payload(payload)
        self.assertTrue(result.ok, msg=f"expected valid payload, got: {result.errors}")

        cookbook_path = (
            current_implementation_root()
            / "cookbooks"
            / "core-delivery"
            / "agent.yaml"
        )
        routes = module.load_allow_routes_from_cookbook(cookbook_path)
        self.assertTrue(module.route_allowed("orchestrator", "backend-engineer", routes))

    def test_secret_like_keys_are_rejected(self):
        module = self._load_validator()
        payload = self._load_valid_payload()
        payload["payload"]["apiKey"] = "abc123"
        result = module.validate_handoff_payload(payload)
        self.assertFalse(result.ok)
        self.assertIn("secret-like", " ".join(result.errors))

    def test_unknown_route_is_denied(self):
        module = self._load_validator()
        cookbook_path = (
            current_implementation_root()
            / "cookbooks"
            / "core-delivery"
            / "agent.yaml"
        )
        routes = module.load_allow_routes_from_cookbook(cookbook_path)
        self.assertFalse(module.route_allowed("backend-engineer", "orchestrator", routes))

    def test_missing_required_keys_fail_closed(self):
        module = self._load_validator()
        payload = self._load_valid_payload()
        del payload["trace"]
        result = module.validate_handoff_payload(payload)
        self.assertFalse(result.ok)
        self.assertIn("missing keys", " ".join(result.errors))

    def _load_schema(self) -> dict:
        schema_path = (
            current_implementation_root() / "runtime" / "handoff" / "schema-v1.json"
        )
        return json.loads(schema_path.read_text(encoding="utf-8"))

    def _schema_validator(self):
        from jsonschema import Draft202012Validator, FormatChecker

        return Draft202012Validator(self._load_schema(), format_checker=FormatChecker())

    def test_schema_bounds_constraint_lists_asymmetrically(self):
        """writablePaths is a grant and must be non-empty; forbiddenActions is a
        denial list, where the empty array is a meaningful state (T529)."""
        constraints = self._load_schema()["properties"]["constraints"]["properties"]
        self.assertEqual(constraints["writablePaths"].get("minItems"), 1)
        self.assertEqual(constraints["forbiddenActions"].get("minItems"), 0)

    def test_empty_writable_paths_rejected_by_schema_and_validator(self):
        payload = self._load_valid_payload()
        payload["constraints"]["writablePaths"] = []

        self.assertTrue(
            list(self._schema_validator().iter_errors(payload)),
            msg="schema must reject a handoff granting zero writable paths",
        )
        result = self._load_validator().validate_handoff_payload(payload)
        self.assertFalse(result.ok)
        self.assertIn("writablePaths", " ".join(result.errors))

    def test_empty_forbidden_actions_accepted(self):
        payload = self._load_valid_payload()
        payload["constraints"]["forbiddenActions"] = []

        self.assertEqual(list(self._schema_validator().iter_errors(payload)), [])
        result = self._load_validator().validate_handoff_payload(payload)
        self.assertTrue(result.ok, msg=f"unexpected errors: {result.errors}")

    def test_malformed_constraint_lists_fail_closed(self):
        module = self._load_validator()
        for field, value in (
            ("writablePaths", "docs/**"),
            ("writablePaths", [""]),
            ("forbiddenActions", {"a": 1}),
            ("forbiddenActions", [None]),
        ):
            with self.subTest(field=field, value=value):
                payload = self._load_valid_payload()
                payload["constraints"][field] = value
                result = module.validate_handoff_payload(payload)
                self.assertFalse(result.ok)
                self.assertIn(field, " ".join(result.errors))

    def test_real_handoff_artifacts_conform_to_schema(self):
        """The two committed handoff records must stay valid under the schema (T529)."""
        checkpoints = repo_root() / "docs" / "checkpoints"
        artifacts = sorted(checkpoints.glob("handoff-*.json"))
        self.assertTrue(artifacts, msg="expected committed handoff artifacts")

        validator = self._schema_validator()
        module = self._load_validator()
        for artifact in artifacts:
            with self.subTest(artifact=artifact.name):
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                errors = [
                    f"{list(e.path)}: {e.message}" for e in validator.iter_errors(payload)
                ]
                self.assertEqual(errors, [])
                self.assertTrue(payload["constraints"]["writablePaths"])
                self.assertTrue(module.validate_handoff_payload(payload).ok)


if __name__ == "__main__":
    unittest.main()
