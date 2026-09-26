"""Checks C13 and C14 of docs/tasks/validate-tasks.py: self-edges and cycles.

`C12` (T537) proved that a declared `Depends on` names a task that exists. It
deliberately left two defects unreported, and T540 closes both:

* **C13 -- self-dependency.** `Depends on: <the row's own ID>` satisfies C12,
  because the row's own ID is in `active_ids`. It is still a length-one cycle
  that leaves the row permanently unschedulable.
* **C14 -- cycles.** `/sprint-status` reconstructs a dependency DAG from these
  edges and orders its queue from it. A cycle has no topological order, so it
  breaks that consumer rather than merely misinforming it.

Both properties matter in both directions, and the second is the one that can
break the repository: `validate-tasks.py` gates every ledger edit and runs in
CI's `validation-super-gate`, so a false positive here blocks all work. The
acyclic shapes below (a chain, a diamond, several rows sharing one completed
dependency) are ordinary ledger shapes, not edge cases.

A multi-row chain is exercised explicitly. A two-row cycle is the easy case and
a naive implementation can catch it while missing longer ones, so `A -> B -> C
-> A` and `A -> B -> C -> D -> A` are covered, as is a cycle reachable only
behind an acyclic prefix.

Every case drives the real, shipped validator as a subprocess against a
synthetic `docs/tasks/` tree, so it exercises exit codes and operator-visible
messages rather than helper functions.
"""
from __future__ import annotations

import subprocess
import sys
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


def _brief(task_id: str, status: str, created: str) -> str:
    return (
        f"# {task_id} — A synthetic task\n\n"
        f"**ID:** {task_id}\n"
        "**Owner:** demo-agent\n"
        f"**Status:** {status}\n"
        "**Priority:** P2\n"
        "**Affects:** —\n"
        f"**Created:** {created}\n"
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(tmp: Path, rows: list[tuple[str, str]]) -> subprocess.CompletedProcess[str]:
    """Drive the validator over `rows` of `(id, depends)` plus completed T900."""
    tasks = tmp / "docs" / "tasks"
    _write(
        tasks / "active-tasks.md",
        ACTIVE_HEADER
        + "".join(
            f"| {task_id} | A synthetic task | demo-agent | pending | P2 | {depends} | 2026-09-26 |\n"
            for task_id, depends in rows
        ),
    )
    _write(
        tasks / "completed-tasks.md",
        COMPLETED_HEADER
        + "| T900 | A synthetic completed task | demo-agent | 2026-09-25 | done |\n",
    )
    _write(tasks / "task-T900.md", _brief("T900", "done", "2026-09-25"))
    for task_id, _ in rows:
        _write(tasks / f"task-{task_id}.md", _brief(task_id, "pending", "2026-09-26"))
    return subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=str(tmp),
        capture_output=True,
        text=True,
    )


class _LedgerCase(unittest.TestCase):
    def _stdout(self, rows: list[tuple[str, str]]) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), rows)
        return proc.returncode, proc.stdout + proc.stderr

    def _expect_clean(self, rows: list[tuple[str, str]]) -> None:
        code, out = self._stdout(rows)
        self.assertEqual(code, 0, out)
        self.assertIn("TASK LEDGER: PASS", out)
        self.assertNotIn("C13", out)
        self.assertNotIn("C14", out)


class TestSelfDependencyCheck(_LedgerCase):
    def _expect_self_edge(self, rows: list[tuple[str, str]], task_id: str) -> None:
        code, out = self._stdout(rows)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL C13", out)
        self.assertIn(f"{task_id} declares Depends on itself", out)
        self.assertNotIn("FAIL C14", out)

    def test_a_row_depending_on_its_own_id_fires(self):
        self._expect_self_edge([("T901", "T901")], "T901")

    def test_own_id_among_annotated_siblings_fires(self):
        """The corpus writes `T454 (done), T455 (done)`; a self-edge can hide there."""
        self._expect_self_edge([("T901", "T900 (done), T901 (pending)")], "T901")

    def test_own_id_embedded_in_prose_fires(self):
        """`none (soft: T505)` appears in the corpus: a real edge inside prose."""
        self._expect_self_edge([("T901", "none (soft: T901)")], "T901")

    def test_a_dependency_on_a_different_active_row_is_clean(self):
        self._expect_clean([("T901", "T902"), ("T902", "—")])

    def test_a_dependency_on_a_completed_row_is_clean(self):
        self._expect_clean([("T901", "T900")])

    def test_placeholders_declare_no_self_edge(self):
        for depends in ("—", "None", "none", "None structurally"):
            with self.subTest(depends=depends):
                self._expect_clean([("T901", depends)])

    def test_an_id_that_merely_prefixes_the_row_id_is_not_a_self_edge(self):
        """`T9010` contains `T901`; token extraction must not confuse the two."""
        self._expect_clean([("T901", "T9010"), ("T9010", "—")])


class TestDependencyCycleCheck(_LedgerCase):
    def _expect_cycle(self, rows: list[tuple[str, str]], chain: str) -> None:
        code, out = self._stdout(rows)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL C14", out)
        self.assertIn(f"dependency cycle {chain}", out)

    def test_two_row_cycle_fires(self):
        self._expect_cycle(
            [("T901", "T902"), ("T902", "T901")],
            "T901 → T902 → T901",
        )

    def test_three_row_cycle_fires(self):
        """The case a two-node-only implementation misses."""
        self._expect_cycle(
            [("T901", "T902"), ("T902", "T903"), ("T903", "T901")],
            "T901 → T902 → T903 → T901",
        )

    def test_four_row_cycle_fires(self):
        self._expect_cycle(
            [("T901", "T902"), ("T902", "T903"), ("T903", "T904"), ("T904", "T901")],
            "T901 → T902 → T903 → T904 → T901",
        )

    def test_cycle_behind_an_acyclic_prefix_fires_and_names_only_the_cycle(self):
        """`T901` leads into the cycle but is not part of it."""
        rows = [("T901", "T902"), ("T902", "T903"), ("T903", "T904"), ("T904", "T902")]
        self._expect_cycle(rows, "T902 → T903 → T904 → T902")
        _, out = self._stdout(rows)
        self.assertNotIn("T901 →", out)

    def test_two_disjoint_cycles_are_reported_separately(self):
        rows = [("T901", "T902"), ("T902", "T901"), ("T903", "T904"), ("T904", "T903")]
        code, out = self._stdout(rows)
        self.assertEqual(code, 1, out)
        self.assertIn("dependency cycle T901 → T902 → T901", out)
        self.assertIn("dependency cycle T903 → T904 → T903", out)
        self.assertEqual(out.count("FAIL C14"), 2, out)

    def test_annotated_cells_still_form_the_cycle(self):
        self._expect_cycle(
            [("T901", "T902 (pending)"), ("T902", "T901 (in_review)")],
            "T901 → T902 → T901",
        )

    def test_a_linear_chain_is_clean(self):
        self._expect_clean(
            [("T901", "T902"), ("T902", "T903"), ("T903", "T904"), ("T904", "—")]
        )

    def test_a_diamond_is_clean(self):
        """Two paths reconverging is not a cycle; a naive visited-set can say it is."""
        self._expect_clean(
            [("T901", "T902, T903"), ("T902", "T904"), ("T903", "T904"), ("T904", "—")]
        )

    def test_several_rows_sharing_one_completed_dependency_is_clean(self):
        self._expect_clean([("T901", "T900"), ("T902", "T900")])

    def test_a_dangling_id_is_c12_not_c14(self):
        code, out = self._stdout([("T901", "T999")])
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL C12", out)
        self.assertNotIn("FAIL C14", out)


class TestRealLedgerIsUnaffected(unittest.TestCase):
    """The guard against C13/C14 blocking the repository they ship in."""

    def test_real_repo_ledger_passes(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=str(repo_root()),
            capture_output=True,
            text=True,
        )
        out = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, out)
        self.assertIn("TASK LEDGER: PASS", out)
        self.assertNotIn("C13", out)
        self.assertNotIn("C14", out)


if __name__ == "__main__":
    unittest.main()
