"""Check C11 of docs/tasks/validate-tasks.py: the declared `**Affects:**` field.

T516 moved the ledger half of `maturity-promotion-criteria-v2.md` §3.5 off a
free-text scan of brief bodies and onto an explicitly declared field. That is
only safe if a *missing* declaration is loud: "no field means this task affects
nothing" would turn a loud false positive (a component wrongly blocked) into a
silent false negative (a component with a real open defect promoted while the
gate prints PASS). C11 is where that loudness lives for the ledger.

Every case here drives the real, shipped validator as a subprocess against a
synthetic `docs/tasks/` tree, so it exercises exit codes and operator-visible
messages, not just helper functions.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

VALIDATOR = repo_root() / "docs" / "tasks" / "validate-tasks.py"
SHIPPED_VALIDATOR = repo_root() / "implementation" / "docs" / "tasks" / "validate-tasks.py"

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

BRIEF = """# T901 — A synthetic task

**ID:** T901
**Owner:** demo-agent
**Status:** pending
**Priority:** {priority}
**Depends on:** —
{affects_line}
**Created:** 2026-09-24
**Completed:** —

## Objective
Exercise the ledger validator.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(tmp: Path, priority: str, affects: str | None, registry: bool = False):
    tasks = tmp / "docs" / "tasks"
    _write(
        tasks / "active-tasks.md",
        ACTIVE_HEADER
        + f"| T901 | A synthetic task | demo-agent | pending | {priority} | — | 2026-09-24 |\n",
    )
    _write(tasks / "completed-tasks.md", COMPLETED_HEADER)
    affects_line = "" if affects is None else f"**Affects:** {affects}"
    _write(tasks / "task-T901.md", BRIEF.format(priority=priority, affects_line=affects_line))
    if registry:
        _write(
            tmp / "implementation" / "registry" / "index.json",
            json.dumps(
                {
                    "entries": [
                        {"id": "demo-agent", "category": "agent", "maturity": "stable"},
                        {"id": "demo-command", "category": "command", "maturity": "stable"},
                    ]
                }
            ),
        )
    return subprocess.run(
        ["python3", str(VALIDATOR)],
        cwd=str(tmp),
        capture_output=True,
        text=True,
    )


class TestAffectsLedgerCheck(unittest.TestCase):
    def test_p1_brief_without_affects_field_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P1", None)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("FAIL C11", proc.stdout)
        self.assertIn("task-T901.md", proc.stdout)
        self.assertIn("mandatory", proc.stdout)

    def test_p0_brief_without_affects_field_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P0", None)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("FAIL C11", proc.stdout)

    def test_p2_brief_need_not_declare(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P2", None)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("TASK LEDGER: PASS", proc.stdout)

    def test_em_dash_is_a_valid_declaration(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P1", "—")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_empty_value_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P1", "")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("C11", proc.stdout)

    def test_bare_id_without_category_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P1", "demo-agent")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("malformed", proc.stdout)

    def test_declared_entries_pass_when_they_name_real_components(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P1", "agent/demo-agent, command/demo-command", registry=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_misspelled_component_id_is_rejected_against_the_registry(self):
        """A typo would otherwise silently protect the component it was meant
        to indict -- the field would parse, match nothing, and block nothing.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            proc = _run(Path(tmp_str), "P1", "agent/demo-agnet", registry=True)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("names no existing component", proc.stdout)

    def test_real_repo_ledger_passes(self):
        proc = subprocess.run(
            ["python3", str(VALIDATOR)],
            cwd=str(repo_root()),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("TASK LEDGER: PASS", proc.stdout)

    def test_shipped_copy_matches_the_repo_copy(self):
        """`implementation/docs/tasks/validate-tasks.py` is the copy installed
        into target repos; it must not drift from the one this repo runs.
        """
        self.assertEqual(
            SHIPPED_VALIDATOR.read_text(encoding="utf-8"),
            VALIDATOR.read_text(encoding="utf-8"),
        )

    def test_shipped_template_declares_the_affects_field(self):
        for template in (
            repo_root() / "docs" / "tasks" / "_template.md",
            repo_root() / "implementation" / "docs" / "tasks" / "_template.md",
        ):
            self.assertIn("**Affects:**", template.read_text(encoding="utf-8"), str(template))


if __name__ == "__main__":
    unittest.main()
