"""Validation tests for v3 super-gate tooling."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, repo_root


def _run_check(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        ["python3", "v3/implementation/scripts/check-v3.py", *args],
        cwd=cwd or repo_root(),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestV3ValidationGate(unittest.TestCase):
    def test_projection_check_passes_against_v2_compat_root(self):
        node_available = shutil.which("node")
        if not node_available:
            self.skipTest("node not available on PATH")

        rc, out = _run_check([
            "--projection",
            "--root",
            "v2/implementation",
        ])
        self.assertEqual(rc, 0, f"projection check should pass against v2 root\n{out}")

    def test_cookbook_reference_failures_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            cookbook = root / "cookbooks" / "broken"
            cookbook.mkdir(parents=True)
            (root / "scripts").mkdir(parents=True)
            (root / "scripts" / "sync-v3.mjs").write_text("", encoding="utf-8")
            (root / "scripts" / "verify-v3.mjs").write_text("", encoding="utf-8")
            (root / "scripts" / "check-v3.py").write_text("", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
