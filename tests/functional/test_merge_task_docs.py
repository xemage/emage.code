"""Unit tests for scripts/merge-task-docs.py."""
from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from unittest import mock
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


class TestSyncTaskDocsRefusesSymlinks(unittest.TestCase):
    """SEC-001 (T636): nothing is written through a symlinked destination."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="emage-task-docs-symlink-")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.template = self.tmp / "template"
        self.template.mkdir()
        for name in ("active-tasks.md", "completed-tasks.md", "_template.md"):
            (self.template / name).write_text(f"# {name}\n")
        self.outside = self.tmp / "outside"
        self.outside.mkdir()
        (self.outside / "canary.txt").write_text("canary\n")

    def _assert_refused(self, dest_dir: Path, victim: Path) -> None:
        before = sorted(p.name for p in dest_dir.resolve().parent.rglob("*"))
        for dry_run in (False, True):
            with self.assertRaises(_merge.SymlinkRefused):
                sync_task_docs(self.template, dest_dir, dry_run=dry_run)
        self.assertEqual((self.outside / "canary.txt").read_text(), "canary\n")
        self.assertEqual(sorted(p.name for p in dest_dir.resolve().parent.rglob("*")), before)
        self.assertTrue(victim.is_symlink())

    def test_symlinked_ledger_is_refused_before_any_file_is_written(self):
        dest = self.tmp / "dest"
        dest.mkdir()
        target_file = self.outside / "ledger.md"
        target_file.write_text("| outside |\n")
        (dest / "completed-tasks.md").symlink_to(target_file)
        self._assert_refused(dest, dest / "completed-tasks.md")
        self.assertEqual(target_file.read_text(), "| outside |\n")
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["completed-tasks.md"])

    def test_dangling_symlink_support_file_is_refused(self):
        dest = self.tmp / "dest"
        dest.mkdir()
        (dest / "_template.md").symlink_to(self.outside / "missing.md")
        self._assert_refused(dest, dest / "_template.md")
        self.assertFalse((self.outside / "missing.md").exists())

    def test_symlinked_dest_dir_is_refused(self):
        dest = self.tmp / "dest"
        dest.symlink_to(self.outside)
        self._assert_refused(dest, dest)
        self.assertEqual([p.name for p in self.outside.iterdir()], ["canary.txt"])

    def test_main_exits_one_with_a_message(self):
        dest = self.tmp / "dest"
        dest.symlink_to(self.outside)
        argv = ["merge-task-docs.py", "--template-dir", str(self.template), "--dest-dir", str(dest)]
        stderr = io.StringIO()
        with mock.patch("sys.argv", argv), redirect_stderr(stderr):
            self.assertEqual(_merge.main(), 1)
        self.assertIn("refusing to write through a symlink", stderr.getvalue())

    def test_ordinary_dest_is_seeded_and_merged(self):
        dest = self.tmp / "dest"
        actions = sync_task_docs(self.template, dest)
        self.assertEqual(len(actions), 3)
        self.assertTrue((dest / "active-tasks.md").is_file())


TEMPLATE_LEDGER = """# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|

> This ledger starts EMPTY.
"""


class TestTableBoundIsTheLedgerHeader(unittest.TestCase):
    """T672 (TL-T649-08): a legend table before the ledger is not the ledger."""

    LEGEND_LEDGER = """# Active Tasks

Legend:

| Code | Meaning |
|------|---------|
| P0 | critical path |
| P1 | important |

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T001 | First | orchestrator | pending | P0 | -- | 2026-10-16 |
| T002 | Second | qa-engineer | pending | P1 | T001 | 2026-10-16 |

> footer
"""

    def test_rows_of_a_ledger_after_a_legend_table_are_not_dropped(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            merged = merge_ledger(TEMPLATE_LEDGER, self.LEGEND_LEDGER)
        self.assertEqual(merged, self.LEGEND_LEDGER, "a healthy ledger round-trips byte for byte")
        self.assertEqual(stderr.getvalue(), "", "no row may be reported as dropped")

    def test_legend_rows_are_never_taken_for_task_rows_nor_the_ledger_for_legend(self):
        existing = self.LEGEND_LEDGER.replace("| T002 | Second", "| BUG-9 | Second")
        stderr = io.StringIO()
        dropped: list[str] = []
        with redirect_stderr(stderr):
            merged = merge_ledger(TEMPLATE_LEDGER, existing, dropped)
        self.assertEqual(dropped, [ln for ln in existing.splitlines() if ln.startswith("| BUG-9")])
        self.assertIn("| P0 | critical path |", merged)
        self.assertIn("| T001 | First |", merged)
        self.assertNotIn("BUG-9", merged)

    def test_a_ledger_with_a_legend_table_only_before_it_keeps_the_old_meaning_without_a_header(self):
        """No `| ID | Title |` header: the first separator is the table, as before T672."""
        existing = "| Code | Meaning |\n|---|---|\n| T001 | row |\n"
        self.assertEqual(merge_ledger(TEMPLATE_LEDGER, existing), existing)

    def test_header_with_a_separator_not_directly_below_is_not_the_ledger(self):
        """The `| ID | Title |` line has no separator under it, so it is not the table: the first
        separator (the Code/Meaning table) is, as before T672 -- and its non-task row is dropped."""
        existing = "| ID | Title |\n\n| Code | Meaning |\n|---|---|\n| X | y |\n"
        dropped: list[str] = []
        with redirect_stderr(io.StringIO()):
            merged = merge_ledger(TEMPLATE_LEDGER, existing, dropped)
        self.assertEqual(dropped, ["| X | y |"])
        self.assertEqual(merged, "| ID | Title |\n\n| Code | Meaning |\n|---|---|\n")


class TestLedgerBackupAndAtomicWrite(unittest.TestCase):
    """T672 (SEC-006): rows are only dropped with a copy of the ledger as it was; writes are atomic."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.template = self.tmp / "template"
        self.template.mkdir()
        (self.template / "active-tasks.md").write_text(TEMPLATE_LEDGER, encoding="utf-8")
        self.dest = self.tmp / "dest"
        self.dest.mkdir()
        self.ledger = self.dest / "active-tasks.md"
        self.with_bad_row = TEMPLATE_LEDGER.replace(
            "\n> This ledger", "| T001 | ok | a | pending | P1 | -- | d |\n| bad | row |\n\n> This ledger")

    def test_dropped_row_means_a_backup_of_the_original(self):
        self.ledger.write_text(self.with_bad_row, encoding="utf-8")
        with redirect_stderr(io.StringIO()):
            actions = sync_task_docs(self.template, self.dest)
        backup = self.dest / "active-tasks.md.bak"
        self.assertEqual(backup.read_text(encoding="utf-8"), self.with_bad_row)
        self.assertNotIn("| bad | row |", self.ledger.read_text(encoding="utf-8"))
        self.assertTrue(any(a.startswith("back up ") and "1 row(s) dropped" in a for a in actions), actions)

    def test_an_earlier_backup_is_never_overwritten(self):
        (self.dest / "active-tasks.md.bak").write_text("older\n", encoding="utf-8")
        self.ledger.write_text(self.with_bad_row, encoding="utf-8")
        with redirect_stderr(io.StringIO()):
            sync_task_docs(self.template, self.dest)
        self.assertEqual((self.dest / "active-tasks.md.bak").read_text(encoding="utf-8"), "older\n")
        self.assertEqual((self.dest / "active-tasks.md.bak.2").read_text(encoding="utf-8"), self.with_bad_row)

    def test_a_healthy_ledger_gets_no_backup(self):
        self.ledger.write_text(TEMPLATE_LEDGER, encoding="utf-8")
        sync_task_docs(self.template, self.dest)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["active-tasks.md"])

    def test_dry_run_writes_no_backup(self):
        self.ledger.write_text(self.with_bad_row, encoding="utf-8")
        with redirect_stderr(io.StringIO()):
            actions = sync_task_docs(self.template, self.dest, dry_run=True)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ["active-tasks.md"])
        self.assertEqual(self.ledger.read_text(encoding="utf-8"), self.with_bad_row)
        self.assertTrue(any(a.startswith("back up ") for a in actions))

    def test_symlinked_backup_name_is_refused_before_any_write(self):
        self.ledger.write_text(self.with_bad_row, encoding="utf-8")
        (self.dest / "active-tasks.md.bak").symlink_to(self.tmp / "elsewhere")
        with self.assertRaises(_merge.SymlinkRefused):
            sync_task_docs(self.template, self.dest)
        self.assertEqual(self.ledger.read_text(encoding="utf-8"), self.with_bad_row)

    def test_failed_replace_leaves_the_ledger_and_no_temp_file(self):
        self.ledger.write_text(self.with_bad_row, encoding="utf-8")
        with mock.patch.object(_merge.os, "replace", side_effect=OSError("disk gone")):
            with self.assertRaises(OSError), redirect_stderr(io.StringIO()):
                sync_task_docs(self.template, self.dest)
        self.assertEqual(self.ledger.read_text(encoding="utf-8"), self.with_bad_row)
        self.assertNotIn(".tmp", "".join(p.name for p in self.dest.iterdir()))

    def test_temp_file_has_the_old_mode_before_content_and_a_random_name(self):
        """SEC-T672-01: never more readable than the ledger it replaces; unpredictable name."""
        import os
        self.ledger.write_text(self.with_bad_row, encoding="utf-8")
        self.ledger.chmod(0o600)
        seen = {}
        real_fchmod, real_replace = os.fchmod, os.replace
        def fchmod(fd, mode):
            seen["size"] = os.fstat(fd).st_size
            seen["mode_before"] = os.fstat(fd).st_mode & 0o7777
            return real_fchmod(fd, mode)
        def replace(src, dst):
            seen["mode"] = os.stat(src).st_mode & 0o7777
            seen["name"] = os.path.basename(src)
            return real_replace(src, dst)
        with mock.patch.object(_merge.os, "fchmod", side_effect=fchmod), \
             mock.patch.object(_merge.os, "replace", side_effect=replace), redirect_stderr(io.StringIO()):
            sync_task_docs(self.template, self.dest)
        self.assertEqual(seen["size"], 0)
        self.assertEqual(seen["mode_before"], 0o600)
        self.assertEqual(seen["mode"], 0o600)
        self.assertNotIn(str(os.getpid()), seen["name"])
        self.assertTrue(seen["name"].startswith(".active-tasks.md.") and seen["name"].endswith(".tmp"))

    def test_ledger_keeps_its_mode(self):
        self.ledger.write_text(TEMPLATE_LEDGER.rstrip("\n"), encoding="utf-8")
        self.ledger.chmod(0o640)
        sync_task_docs(self.template, self.dest)
        self.assertEqual(self.ledger.stat().st_mode & 0o7777, 0o640)

    def test_seeded_files_are_not_group_or_world_writable(self):
        (self.template / "validate-tasks.py").write_text("print(1)\n", encoding="utf-8")
        (self.template / "validate-tasks.py").chmod(0o777)
        sync_task_docs(self.template, self.tmp / "fresh")
        self.assertEqual((self.tmp / "fresh" / "validate-tasks.py").stat().st_mode & 0o022, 0)


if __name__ == "__main__":
    unittest.main()
