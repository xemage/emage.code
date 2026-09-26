"""Check C12 of docs/tasks/validate-tasks.py: `Depends on` must resolve.

Before T537 the sixth cell of an active row was destructured into `_` and never
read, so a row declaring a dependency on a task present in *neither* ledger
passed `TASK LEDGER: PASS` in silence. Those edges are what `/sprint-status`
reconstructs its dependency DAG from -- an unvalidated edge is a dependency
nobody is checking.

Two properties matter equally here, and the second is the one that can break the
repository:

1. A dangling ID must fire loudly (a check that cannot fail is worth nothing).
2. A *satisfied* dependency normally points into `completed-tasks.md`, so
   resolving against the active ledger alone would flag every satisfied
   dependency as dangling. `validate-tasks.py` gates every ledger edit and runs
   in CI's `validation-super-gate`, so a false positive here blocks all work.

Every case drives the real, shipped validator as a subprocess against a
synthetic `docs/tasks/` tree, so it exercises exit codes and operator-visible
messages rather than helper functions.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

VALIDATOR = repo_root() / "docs" / "tasks" / "validate-tasks.py"

ACTIVE_HEADER = (
    "# Active Tasks\n\n"
    "| ID | Title | Owner | Status | Priority | Depends on | Last update |\n"
    "|----|-------|-------|--------|----------|-----------|-------------|\n"
)
COMPLETED_HEADER = (
    "# Completed Tasks\n\n"
    "| ID | Title | Owner | Done on | Outcome / artifact |\n"
    "|----|-------|-------|---------|-------------------|\n"
)

ACTIVE_BRIEF = """# T901 — A synthetic active task

**ID:** T901
**Owner:** demo-agent
**Status:** pending
**Priority:** P2
**Affects:** —
**Created:** 2026-09-26
"""

COMPLETED_BRIEF = """# T900 — A synthetic completed task

**ID:** T900
**Owner:** demo-agent
**Status:** done
**Priority:** P2
**Affects:** —
**Created:** 2026-09-25
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(tmp: Path, depends: str) -> subprocess.CompletedProcess[str]:
    """Drive the validator over a two-row ledger: active T901, completed T900."""
    tasks = tmp / "docs" / "tasks"
    _write(
        tasks / "active-tasks.md",
        ACTIVE_HEADER
        + f"| T901 | A synthetic active task | demo-agent | pending | P2 | {depends} | 2026-09-26 |\n",
    )
    _write(
        tasks / "completed-tasks.md",
        COMPLETED_HEADER
        + "| T900 | A synthetic completed task | demo-agent | 2026-09-25 | done |\n",
    )
    _write(tasks / "task-T901.md", ACTIVE_BRIEF)
    _write(tasks / "task-T900.md", COMPLETED_BRIEF)
    return subprocess.run(
        ["python3", str(VALIDATOR)],
        cwd=str(tmp),
        capture_output=True,
        text=True,
    )


class TestDependsOnLedgerCheck(unittest.TestCase):
    def _expect_dangling(self, depends: str, dangling_id: str) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), depends)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("FAIL C12", proc.stdout)
        self.assertIn(dangling_id, proc.stdout)
        self.assertIn("exists in neither ledger", proc.stdout)

    def _expect_clean(self, depends: str) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), depends)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("TASK LEDGER: PASS", proc.stdout)
        self.assertNotIn("C12", proc.stdout)

    def test_dependency_on_a_nonexistent_id_fails_loudly(self):
        self._expect_dangling("T999", "T999")

    def test_dependency_on_a_completed_task_is_satisfied_not_dangling(self):
        """The normal case for a satisfied dependency, not an edge case.

        Resolving against `active-tasks.md` alone would flag it and make the
        check worse than useless.
        """
        self._expect_clean("T900")

    def test_dependency_on_another_active_task_resolves(self):
        self._expect_clean("T901")

    def test_em_dash_placeholder_declares_no_dependency(self):
        self._expect_clean("—")

    def test_prose_placeholders_carrying_no_id_declare_no_dependency(self):
        """`None`, `none` and `None structurally` all appear in the real corpus."""
        for depends in ("None", "none", "None structurally"):
            with self.subTest(depends=depends):
                self._expect_clean(depends)

    def test_annotated_multi_dependency_form_resolves_every_id(self):
        """The corpus writes `T454 (done), T455 (done), T458 (pending)`.

        The parenthetical annotations are not part of the edge; each ID inside
        the cell still has to resolve.
        """
        self._expect_clean("T900 (done), T901 (pending)")

    def test_one_dangling_id_among_several_still_fires(self):
        self._expect_dangling("T900 (done), T998 (pending)", "T998")

    def test_id_embedded_in_prose_is_still_resolved(self):
        """`none (soft: T505)` appears in the corpus: a real edge in prose."""
        self._expect_clean("none (soft: T900)")
        self._expect_dangling("none (soft: T997)", "T997")

    def test_real_repo_ledger_passes(self):
        """T532 declares `Depends on: T531`, and T531 is completed.

        This is the guard against C12 blocking the repository it ships in.
        """
        proc = subprocess.run(
            ["python3", str(VALIDATOR)],
            cwd=str(repo_root()),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("TASK LEDGER: PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
