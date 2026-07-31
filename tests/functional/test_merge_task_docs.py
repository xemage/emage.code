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
    def test_merge_preserves_completed_rows_and_updates_footer(self):
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
        self.assertIn("Intro from template.", merged)
        self.assertIn("| T001 | First task |", merged)
        self.assertIn("| T002 | Second task |", merged)
        self.assertIn("> Template footer line.", merged)
        self.assertNotIn("Old intro text.", merged)
        self.assertNotIn("> Old footer.", merged)

    def test_merge_drops_template_example_row_but_keeps_real_rows(self):
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
        self.assertIn("Per-task briefs live alongside", merged)

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
