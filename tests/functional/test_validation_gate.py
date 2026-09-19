"""Validation tests for super-gate tooling."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


def _run_check(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        ["python3", "implementation/scripts/check.py", *args],
        cwd=cwd or repo_root(),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestValidationGate(unittest.TestCase):
    def test_projection_check_passes_against_implementation_root(self):
        node_available = shutil.which("node")
        if not node_available:
            self.skipTest("node not available on PATH")

        rc, out = _run_check([
            "--projection",
            "--root",
            "implementation",
        ])
        self.assertEqual(rc, 0, f"projection check should pass against implementation root\n{out}")

    def test_cookbook_reference_failures_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            cookbook = root / "cookbooks" / "broken"
            cookbook.mkdir(parents=True)
            (root / "scripts").mkdir(parents=True)
            (root / "scripts" / "sync.mjs").write_text("", encoding="utf-8")
            (root / "scripts" / "verify.mjs").write_text("", encoding="utf-8")
            (root / "scripts" / "check.py").write_text("", encoding="utf-8")
            (root / "cookbooks" / "README.md").write_text("x", encoding="utf-8")

            (cookbook / "README.md").write_text("x", encoding="utf-8")
            (cookbook / "steering-examples.json").write_text(
                json.dumps({"examples": [{"id": "e1"}]}),
                encoding="utf-8",
            )
            (cookbook / "agent.yaml").write_text(
                "\n".join(
                    [
                        "schema: ../../knowledge/schemas/cookbook.schema.json",
                        "schemaVersion: 3.0.0",
                        "cookbookId: broken-cookbook",
                        "name: Broken",
                        "version: 1.0.0",
                        "description: Broken cookbook fixture.",
                        "orchestrator:",
                        "  ref: orchestrator",
                        "  instructions:",
                        "    - ../../missing/instruction.md",
                        "  skills:",
                        "    - ../../missing/skill.md",
                        "workers:",
                        "  - ref: backend-engineer",
                        "    skills:",
                        "      - ../../missing/worker-skill.md",
                        "    maxConcurrency: 1",
                        "handoffPolicy:",
                        "  allowRoutes:",
                        "    - from: orchestrator",
                        "      to: backend-engineer",
                        "  defaultAction: deny",
                        "security:",
                        "  redactFields: [token]",
                        "  allowSecretsInPayload: false",
                        "  requireSchemaValidation: true",
                    ]
                ),
                encoding="utf-8",
            )

            rc, out = _run_check(["--cookbooks", "--root", str(root)])
            self.assertNotEqual(rc, 0, "broken cookbook references must fail")
            self.assertIn("unresolved", out)

    def test_required_gate_fails_when_scripts_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            (root / "cookbooks").mkdir(parents=True)
            (root / "cookbooks" / "README.md").write_text("x", encoding="utf-8")

            rc, out = _run_check(["--required", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing scripts should fail required gate")
            self.assertIn("missing directory", out)

    def test_hook_policy_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--hook-policy", "--root", "implementation"])
        self.assertEqual(rc, 0, f"hook-policy gate should pass\n{out}")

    def test_hook_policy_gate_fails_when_artifact_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--hook-policy", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing hook-policy artifact must fail gate")
            self.assertIn("hook-policy: missing artifact", out)

    def test_telemetry_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--telemetry", "--root", "implementation"])
        self.assertEqual(rc, 0, f"telemetry gate should pass\n{out}")

    def test_telemetry_gate_fails_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--telemetry", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing telemetry files must fail gate")
            self.assertIn("telemetry: missing required file", out)

    def test_benchmarks_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--benchmarks", "--root", "implementation"])
        self.assertEqual(rc, 0, f"benchmarks gate should pass\n{out}")

    def test_benchmarks_gate_fails_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--benchmarks", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing benchmark files must fail gate")
            self.assertIn("benchmarks: missing required file", out)

    def test_registry_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--registry", "--root", "implementation"])
        self.assertEqual(rc, 0, f"registry gate should pass\n{out}")

    def test_registry_gate_fails_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--registry", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing registry files must fail gate")
            self.assertIn("registry: missing required file", out)

    def test_maturity_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--maturity", "--root", "implementation"])
        self.assertEqual(rc, 0, f"maturity gate should pass\n{out}")

    def test_maturity_gate_fails_when_script_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--maturity", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing checker script must fail gate")
            self.assertIn("maturity: missing checker script", out)

    def test_packaging_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--packaging", "--root", "implementation"])
        self.assertEqual(rc, 0, f"packaging gate should pass\n{out}")

    def test_packaging_gate_fails_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--packaging", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing packaging files must fail gate")
            self.assertIn("packaging: missing required file", out)

    def test_triggers_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--triggers", "--root", "implementation"])
        self.assertEqual(rc, 0, f"triggers gate should pass\n{out}")

    def test_triggers_gate_fails_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--triggers", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing trigger files must fail gate")
            self.assertIn("triggers: missing required file", out)

    def test_adapters_gate_passes_for_repo_artifact(self):
        rc, out = _run_check(["--adapters", "--root", "implementation"])
        self.assertEqual(rc, 0, f"adapters gate should pass\n{out}")

    def test_adapters_gate_fails_when_files_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            root.mkdir(parents=True)

            rc, out = _run_check(["--adapters", "--root", str(root)])
            self.assertNotEqual(rc, 0, "missing adapter files must fail gate")
            self.assertIn("adapters: missing required file", out)


if __name__ == "__main__":
    unittest.main()
