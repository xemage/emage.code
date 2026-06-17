"""Functional tests for scripts/install.sh."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestInstallScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bash = shutil.which("bash")
        if not cls.bash:
            raise unittest.SkipTest("bash not available on PATH")

    def _run_install(self, target: Path, platform: str = "pi", update: bool = False) -> subprocess.CompletedProcess[str]:
        args = [
            self.bash,
            str(repo_root() / "scripts" / "install.sh"),
            "--target",
            str(target),
            "--platform",
            platform,
        ]
        if update:
            args.append("--update")
        return subprocess.run(
            args,
            cwd=repo_root(),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_install_merges_into_existing_platform_and_docs_dirs(self):
        implementation_pi = repo_root() / "implementation" / ".pi"

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / ".pi").mkdir()
            (target / "docs").mkdir()
            (target / ".pi" / "keep-pi.txt").write_text("existing", encoding="utf-8")
            (target / "docs" / "keep-docs.txt").write_text("existing", encoding="utf-8")

            proc = self._run_install(target, platform="pi")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            self.assertFalse(
                (target / ".pi" / ".pi").exists(),
                "install must not nest platform files under .pi/.pi",
            )
            self.assertFalse(
                (target / "docs" / "docs").exists(),
                "install must not nest docs under docs/docs",
            )
            self.assertTrue((target / ".pi" / "keep-pi.txt").is_file())
            self.assertTrue((target / "docs" / "keep-docs.txt").is_file())
            self.assertTrue((target / "AGENTS.md").is_file())

            # Sanity: installed tree contains at least one file from implementation/.pi
            installed_names = {p.name for p in implementation_pi.rglob("*") if p.is_file()}
            copied_names = {p.name for p in (target / ".pi").rglob("*") if p.is_file()}
            self.assertTrue(
                installed_names & copied_names,
                "expected install to copy files from implementation/.pi into target/.pi",
            )

    def test_update_requires_existing_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            proc = self._run_install(target, platform="pi", update=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("AGENTS.md", proc.stderr)

    def test_update_removes_stale_platform_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            (target / ".pi").mkdir()
            (target / ".pi" / "stale-agent.md").write_text("remove me", encoding="utf-8")

            proc = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse((target / ".pi" / "stale-agent.md").exists())
            self.assertIn("Updated emage.code", proc.stdout)

    def test_update_preserves_merged_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            (target / "docs").mkdir()
            (target / "docs" / "custom-task.md").write_text("keep me", encoding="utf-8")

            proc = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((target / "docs" / "custom-task.md").is_file())

    def test_update_preserves_task_ledger_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            (target / "AGENTS.md").write_text("# existing", encoding="utf-8")
            tasks = target / "docs" / "tasks"
            tasks.mkdir(parents=True)
            (tasks / "completed-tasks.md").write_text(
                "\n".join(
                    [
                        "# Completed Tasks",
                        "",
                        "Append-only log.",
                        "",
                        "| ID | Title | Owner | Done on | Outcome / artifact |",
                        "|----|-------|-------|---------|--------------------|",
                        "| T042 | CI gates | devops-engineer | 2026-05-24 | .gitlab-ci.yml |",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (tasks / "active-tasks.md").write_text(
                "\n".join(
                    [
                        "# Active Tasks",
                        "",
                        "| ID | Title | Owner | Status | Priority | Depends on | Last update |",
                        "|----|-------|-------|--------|----------|-----------|-------------|",
                        "| T099 | Open item | orchestrator | in_progress | P0 | — | 2026-06-12 |",
                        "",
                        "> Keep this note.",
                    ]
                ),
                encoding="utf-8",
            )

            proc = self._run_install(target, platform="pi", update=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            completed = (tasks / "completed-tasks.md").read_text(encoding="utf-8")
            active = (tasks / "active-tasks.md").read_text(encoding="utf-8")
            self.assertIn("| T042 | CI gates |", completed)
            self.assertIn("| T099 | Open item |", active)
            self.assertIn("Append-only log. Entries move here", completed)
            self.assertIn("Per-task briefs live alongside", active)
            self.assertNotIn("> Keep this note.", active)


if __name__ == "__main__":
    unittest.main()
