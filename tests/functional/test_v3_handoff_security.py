"""Security checks for v3 handoff validation and routing."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestV3HandoffSecurity(unittest.TestCase):
    def _load_validator(self):
        import importlib.util
        import sys

        validator_path = repo_root() / "v3" / "implementation" / "runtime" / "handoff" / "validator.py"
        spec = importlib.util.spec_from_file_location("v3_handoff_validator", validator_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def _load_valid_payload(self) -> dict:
        payload_path = (
            repo_root()
            / "v3"
            / "implementation"
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
            repo_root()
            / "v3"
            / "implementation"
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
            repo_root()
            / "v3"
            / "implementation"
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


if __name__ == "__main__":
    unittest.main()
