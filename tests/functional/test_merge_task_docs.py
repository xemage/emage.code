"""Unit tests for scripts/merge-task-docs.py."""
from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from tests._helpers.repo import repo_root


def _load_merge_module():
    path = repo_root() / "scripts" / "merge-task-docs.py"
    spec = importlib.util.spec_from_file_location("merge_task_docs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_merge = _load_merge_module()
merge_ledger = _merge.merge_ledger
sync_task_docs = _merge.sync_task_docs


class TestMergeTaskDocs(unittest.TestCase):
    def test_merge_preserves_completed_rows_and_existing_prose(self):
        """T518: the existing ledger's prose is the project's, not the template's.

        This test previously asserted the inverse -- that "Old intro text." and
        "> Old footer." were *gone* and the template's replaced them. That
        encoded the bug: substituting template prose for project prose is
        exactly what destroyed active-tasks.md on every --update.
        """
        template = """# Completed Tasks

Intro from template.

| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|

> Template footer line.
"""
        existing = """# Completed Tasks

Old intro text.

| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
| T001 | First task | qa-engineer | 2026-01-01 | docs/artifacts/a.md |
| T002 | Second task | backend-developer | 2026-01-02 | docs/artifacts/b.md |

> Old footer.
"""
        merged = merge_ledger(template, existing)
        self.assertIn("| T001 | First task |", merged)
        self.assertIn("| T002 | Second task |", merged)
        self.assertIn("Old intro text.", merged)
        self.assertIn("> Old footer.", merged)
        self.assertNotIn("Intro from template.", merged)
        self.assertNotIn("> Template footer line.", merged)
        self.assertEqual(merged, existing)

    def test_merge_keeps_real_rows_and_never_injects_template_prose(self):
        """T518: previously asserted the template's postamble replaced the
        target's "> Custom note." -- the same encoded bug as above."""
        template = (Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
            encoding="utf-8"
        )
        existing = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T009 | Real work | orchestrator | in_progress | P0 | — | 2026-06-01 |

> Custom note.
"""
        merged = merge_ledger(template, existing)
        self.assertIn("| T009 | Real work |", merged)
        self.assertNotIn("_Example:", merged)
        self.assertIn("> Custom note.", merged)
        self.assertNotIn("Per-task briefs live alongside", merged)
        self.assertNotIn("ledger starts EMPTY", merged)

    # -- T518 regression: prose preservation ------------------------------
    # Each of the three below fails against the pre-T518 merge_ledger().

    def test_zero_row_populated_ledger_survives_byte_identical(self):
        """The worst case: a *healthy* ledger with no active rows. There is
        nothing to preserve row-wise, so the template used to win outright and
        overwrite a 90-line project record with an 11-line fresh-install stub."""
        template = (Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
            encoding="utf-8"
        )
        existing = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|

> **0 active rows.** 511 real tasks have already run to completion; see
> `completed-tasks.md`. Do not treat an empty table as "no history exists".

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done`

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
"""
        merged = merge_ledger(template, existing)
        self.assertEqual(merged, existing)

    def test_false_fresh_install_claim_never_written_into_existing_ledger(self):
        """The template asserts the ledger starts empty and the first task is
        `T001`. In a target with completed history that is actively false, and
        active-tasks.md is the file a cold session reads first."""
        template = (Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("ledger starts EMPTY", template, "template precondition")
        existing = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|

> 316 tasks already completed. This is not a fresh project.
"""
        merged = merge_ledger(template, existing)
        self.assertNotIn("ledger starts EMPTY", merged)
        self.assertNotIn("The first real task is", merged)
        self.assertIn("316 tasks already completed", merged)

    def test_existing_ledger_without_table_falls_back_to_template(self):
        """A dest with no markdown table has nothing to splice into, so the
        template is still the best available scaffold there."""
        template = (Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
            encoding="utf-8"
        )
        merged = merge_ledger(template, "# Active Tasks\n\ntruncated, no table\n")
        self.assertIn("| ID | Title | Owner | Status |", merged)
        self.assertIn("ledger starts EMPTY", merged)

    def test_sync_seeds_missing_ledger_from_template_verbatim(self):
        """Fresh-install path is unchanged: a missing ledger gets the full
        template text, guidance prose included."""
        template_dir = Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks"
        with tempfile.TemporaryDirectory() as tmp:
            dest_dir = Path(tmp) / "dest"
            sync_task_docs(template_dir, dest_dir)
            self.assertEqual(
                (dest_dir / "active-tasks.md").read_text(encoding="utf-8"),
                (template_dir / "active-tasks.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "ledger starts EMPTY",
                (dest_dir / "active-tasks.md").read_text(encoding="utf-8"),
            )

    def test_sync_seeds_missing_and_skips_existing_non_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            template_dir = Path(tmp) / "template"
            dest_dir = Path(tmp) / "dest"
            template_dir.mkdir()
            dest_dir.mkdir()
            (template_dir / "completed-tasks.md").write_text("# Completed Tasks\n", encoding="utf-8")
            (template_dir / "active-tasks.md").write_text("# Active Tasks\n", encoding="utf-8")
            (dest_dir / "task-T099.md").write_text("user brief", encoding="utf-8")

            actions = sync_task_docs(template_dir, dest_dir)
            self.assertTrue((dest_dir / "completed-tasks.md").is_file())
            self.assertTrue((dest_dir / "active-tasks.md").is_file())
            self.assertEqual((dest_dir / "task-T099.md").read_text(encoding="utf-8"), "user brief")
            self.assertEqual(len(actions), 2)

    def test_sync_seeds_non_md_files_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            template_dir = Path(tmp) / "template"
            dest_dir = Path(tmp) / "dest"
            template_dir.mkdir()
            dest_dir.mkdir()
            (template_dir / "completed-tasks.md").write_text("# Completed Tasks\n", encoding="utf-8")
            (template_dir / "active-tasks.md").write_text("# Active Tasks\n", encoding="utf-8")
            (template_dir / "validate-tasks.py").write_text("print('ok')\n", encoding="utf-8")
            (template_dir / "__pycache__").mkdir()
            (template_dir / "__pycache__" / "validate-tasks.cpython-312.pyc").write_bytes(b"\x00")

            actions = sync_task_docs(template_dir, dest_dir)
            self.assertTrue((dest_dir / "validate-tasks.py").is_file())
            self.assertEqual(
                (dest_dir / "validate-tasks.py").read_text(encoding="utf-8"), "print('ok')\n"
            )
            self.assertFalse((dest_dir / "__pycache__").exists())
            self.assertEqual(len(actions), 3)

    def test_sync_skips_existing_non_md_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            template_dir = Path(tmp) / "template"
            dest_dir = Path(tmp) / "dest"
            template_dir.mkdir()
            dest_dir.mkdir()
            (template_dir / "completed-tasks.md").write_text("# Completed Tasks\n", encoding="utf-8")
            (template_dir / "active-tasks.md").write_text("# Active Tasks\n", encoding="utf-8")
            (template_dir / "validate-tasks.py").write_text("print('new')\n", encoding="utf-8")
            (dest_dir / "validate-tasks.py").write_text("print('local edits')\n", encoding="utf-8")

            actions = sync_task_docs(template_dir, dest_dir)
            self.assertEqual(
                (dest_dir / "validate-tasks.py").read_text(encoding="utf-8"), "print('local edits')\n"
            )
            self.assertEqual(len(actions), 2)

    def test_four_digit_ids_survive_merge(self):
        template = (Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
            encoding="utf-8"
        )
        existing = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T1001 | four digit id | owner | pending | P1 | — | 2026-07-27 |
"""
        merged = merge_ledger(template, existing)
        self.assertIn("T1001", merged)

    def test_bug_prefixed_row_warns(self):
        template = (Path(__file__).resolve().parents[2] / "implementation" / "docs" / "tasks" / "active-tasks.md").read_text(
            encoding="utf-8"
        )
        existing = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| BUG-7 | bad row | owner | pending | P1 | — | 2026-07-27 |
"""
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            merged = merge_ledger(template, existing)
        self.assertNotIn("BUG-7", merged)
        self.assertIn("warning: dropping non-conforming", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
