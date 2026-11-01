"""T675 (TL-T649-12): the release-docs gate rejects an unfilled Gate Verdicts / RELEASE VERDICT.

T703 (SEC-T662-01): it also fails when a release document install.sh points users to is missing
or lacks its Cursor migration item.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from tests._helpers.repo import repo_root


def _load():
    path = repo_root() / "scripts" / "verify-release-docs.py"
    spec = importlib.util.spec_from_file_location("verify_release_docs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load verify-release-docs module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_past_release_without_markers(test: unittest.TestCase, tag: str) -> tuple[int, str]:
    """Run main() for a past release tag on this tree with the marker check patched out.

    T704: once the tree's `Latest release:` markers name a newer release, the marker check
    fails for the past tag by design. This helper first proves that the marker check is the
    only reason (it reports exactly the MARKER_FILES for the past tag and nothing for the
    tree's own marker), then runs the rest of the gate for the past tag.
    """
    readme = (repo_root() / "README.md").read_text(encoding="utf-8")
    current = next(line.strip() for line in readme.splitlines() if line.startswith("Latest release:"))
    past: list[str] = []
    test.mod.check_markers(f"Latest release: {tag}", past)
    if current != f"Latest release: {tag}":
        test.assertEqual(past, [f"missing marker 'Latest release: {tag}' in {f}" for f in test.mod.MARKER_FILES])
    own: list[str] = []
    test.mod.check_markers(current, own)
    test.assertEqual(own, [])
    with mock.patch.object(test.mod, "check_markers"):
        return test._run_main(tag)


GOOD = """# Release v1.2.3

## Gate Verdicts

- Architecture: PASS on 2026-10-15 (T649)
- Release: CONDITIONAL_PASS on 2026-10-15 (the pending items are tracked)

## RELEASE VERDICT

- **Version**: v1.2.3
- **Status**: CONDITIONAL_PASS
- **Features included**: 3
- **Timestamp**: 2026-10-16T01:19:10Z

## Rollback Plan

Nothing is pending here and YYYY-MM-DD outside the verdict sections is not checked.
"""


class VerdictPlaceholderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def problems(self, text: str) -> list[str]:
        return self.mod.verdict_placeholder_problems(text)

    def test_a_filled_document_passes(self):
        self.assertEqual(self.problems(GOOD), [])

    def test_the_published_release_documents_pass(self):
        for name in ("v8.0.0", "v7.0.1", "v6.10.0"):
            with self.subTest(tag=name):
                text = (repo_root() / "docs" / "releases" / f"{name}.md").read_text(encoding="utf-8")
                self.assertEqual(self.problems(text), [])

    def test_the_unfilled_template_fails(self):
        text = (repo_root() / "docs" / "releases" / "_template.md").read_text(encoding="utf-8")
        found = " ".join(self.problems(text))
        for marker in ("YYYY-MM-DD", "<count>", "<ISO-8601>", "<PASS/CONDITIONAL_PASS>", "PASS | CONDITIONAL_PASS | FAIL"):
            self.assertIn(marker, found)

    def test_status_pending_fails(self):
        for status in ("pending", "Pending", "**pending**", "`pending`", "pending (T651)"):
            with self.subTest(status=status):
                found = self.problems(GOOD.replace("**Status**: CONDITIONAL_PASS", f"**Status**: {status}"))
                self.assertEqual(len(found), 1)
                self.assertIn("still pending", found[0])

    def test_a_gate_row_that_is_pending_fails(self):
        for row in ("- Security: pending", "- Security: PASS on pending", "* Security: Pending review"):
            with self.subTest(row=row):
                self.assertTrue(self.problems(GOOD.replace("- Architecture: PASS on 2026-10-15 (T649)", row)))

    def test_a_date_placeholder_fails_in_either_section(self):
        for old, new in (
            ("- Architecture: PASS on 2026-10-15 (T649)", "- Architecture: PASS on YYYY-MM-DD"),
            ("**Timestamp**: 2026-10-16T01:19:10Z", "**Timestamp**: YYYY-MM-DD"),
        ):
            with self.subTest(new=new):
                self.assertTrue(self.problems(GOOD.replace(old, new)))

    def test_placeholders_in_a_fenced_block_or_another_section_do_not_count(self):
        fenced = GOOD.replace("## Rollback Plan", "## Rollback Plan\n\n```\n- Status: pending on YYYY-MM-DD\n```\n")
        self.assertEqual(self.problems(fenced), [])
        quoted = GOOD.replace("## Gate Verdicts", "## Gate Verdicts\n\n```\n- x: pending\n```\n")
        self.assertEqual(self.problems(quoted), [])

    def test_prose_that_mentions_pending_is_not_a_field_value(self):
        text = GOOD.replace("- **Version**: v1.2.3", "No pending item remains.\n\n- **Version**: v1.2.3")
        self.assertEqual(self.problems(text), [])

    def test_section_text_stops_at_the_next_level_two_heading(self):
        self.assertIn("Features included", self.mod.section_text(GOOD, "## RELEASE VERDICT"))
        self.assertNotIn("Rollback", self.mod.section_text(GOOD, "## RELEASE VERDICT"))
        self.assertEqual(self.mod.section_text(GOOD, "## Missing"), "")

    def test_more_template_placeholders_fail(self):
        for old, new in (
            ("**Features included**: 3", "**Features included**: TBD"),
            ("**Features included**: 3", "**Features included**: TODO count"),
            ("- Architecture: PASS on 2026-10-15 (T649)", "- Architecture: TBD"),
            ("**Version**: v1.2.3", "**Version**: v1.2.3\n- **Quality gates passed**: [list gates: code-review]"),
            ("**Version**: v1.2.3", "**Version**: v1.2.3\n- **Blocker IDs**: [if FAIL - list blocking issues]"),
        ):
            with self.subTest(new=new[-40:]):
                self.assertTrue(self.problems(GOOD.replace(old, new)))

    def test_a_field_without_a_value_fails_unless_a_sub_list_follows(self):
        empty = GOOD.replace("**Features included**: 3", "**Features included**:")
        self.assertTrue(any("no value" in p for p in self.problems(empty)))
        self.assertTrue(self.problems(GOOD.replace("- Architecture: PASS on 2026-10-15 (T649)", "- Architecture:")))
        nested = GOOD.replace("**Features included**: 3", "**Features included**:\n  - a\n  - b")
        self.assertEqual(self.problems(nested), [])

    def test_the_words_tbd_and_todo_must_stand_alone(self):
        text = GOOD.replace("- **Version**: v1.2.3", "- **Version**: v1.2.3 (subtodo, TBDx, ATODO)")
        self.assertEqual(self.problems(text), [])

    def test_a_present_but_empty_or_fenced_section_is_an_error(self):
        empty = "# R\n\n## RELEASE VERDICT\n\n## Rollback Plan\n\ntext\n"
        self.assertTrue(any("empty or only inside a code block" in p for p in self.problems(empty)))
        fenced = "# R\n\n```\n## RELEASE VERDICT\n\n- **Status**: PASS\n```\n"
        self.assertTrue(any("empty or only inside a code block" in p for p in self.problems(fenced)))
        self.assertTrue(any("empty or only inside a code block" in p for p in self.problems("## Gate Verdicts\n")))
        self.assertEqual(self.problems("# R\n\nno verdict sections at all\n"), [])

    def test_a_heading_with_trailing_spaces_is_still_checked(self):
        text = GOOD.replace("## RELEASE VERDICT", "## RELEASE VERDICT   ").replace("CONDITIONAL_PASS\n- **Features", "pending\n- **Features")
        self.assertTrue(any("still pending" in p for p in self.problems(text)))

    def test_field_matching_does_not_backtrack_on_long_whitespace_lines(self):
        import time
        line = "- " + "a" + " " * 60000 + "x"
        start = time.monotonic()
        self.mod.verdict_placeholder_problems("## RELEASE VERDICT\n\n" + line + "\n")
        self.assertLess(time.monotonic() - start, 1.0)  # a lazy label with [ \\t]* takes ~3 s, \\s* ~5 s here

    def test_a_document_without_a_gate_verdicts_section_is_not_newly_rejected(self):
        self.assertEqual(self.problems(GOOD.replace("## Gate Verdicts", "## Other")), [])


class GateWiringTests(unittest.TestCase):
    """main() applies the placeholder check to the release document of the tag."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def _run_main(self, tag: str) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["verify-release-docs.py", "--tag", tag]), \
                mock.patch.object(self.mod, "check_version_consistency"), \
                contextlib.redirect_stdout(out):
            return self.mod.main(), out.getvalue()

    def test_the_published_v8_document_passes_the_gate(self):
        code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual((code, "all documentation checks passed" in output), (0, True))

    def test_an_unfilled_verdict_fails_the_gate_with_a_clear_message(self):
        real = self.mod.verdict_placeholder_problems
        with mock.patch.object(
            self.mod, "verdict_placeholder_problems",
            side_effect=lambda text: real(text.replace("**Status**: CONDITIONAL_PASS", "**Status**: pending")),
        ):
            code, output = self._run_main("v8.0.0")
        self.assertEqual(code, 1)
        self.assertIn("unfilled verdict in docs/releases/v8.0.0.md", output)
        self.assertIn("still pending", output)


CURSOR_ITEM_DOC = """# Release v9.0.0

## Migration Guide

**Migration from v8.0.0 to v9.0.0.** Do the steps in order.

**Migration Guide item M-3. Cursor is no longer supported.**

- What changed: `--platform cursor` exits 1.

## Changelog
"""

INSTALL_SH = (
    'echo "error: platform \'cursor\' was removed in v9.0.0 (see the Cursor migration item in docs/releases/v9.0.0.md)."\n'
    'echo "  see the Cursor migration item in docs/releases/v9.0.0.md." >&2\n'
)


class MigrationPointerTests(unittest.TestCase):
    """T703 (SEC-T662-01): a release document install.sh points users to exists and carries its Cursor item."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def _pointer_errors(self, tag: str, document: str | None, install: str = INSTALL_SH) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "install.sh").write_text(install, encoding="utf-8")
            if document is not None:
                (root / "docs" / "releases").mkdir(parents=True)
                (root / "docs" / "releases" / "v9.0.0.md").write_text(document, encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_migration_pointers(tag, errors)
            return errors

    def _run_main(self, tag: str) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["verify-release-docs.py", "--tag", tag]), \
                mock.patch.object(self.mod, "check_version_consistency"), \
                contextlib.redirect_stdout(out):
            return self.mod.main(), out.getvalue()

    def test_install_sh_on_this_tree_points_to_the_v9_document_for_cursor(self):
        text = (repo_root() / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertEqual(self.mod.install_sh_pointers(text).get("docs/releases/v9.0.0.md"), True)

    def test_verifying_v9_fails_while_the_pointed_document_is_missing(self):
        if (repo_root() / "docs" / "releases" / "v9.0.0.md").exists():
            self.skipTest("docs/releases/v9.0.0.md exists (T705 landed); the synthetic test below still pins the rule")
        code, output = self._run_main("v9.0.0")
        self.assertEqual(code, 1)
        self.assertIn("scripts/install.sh points users to docs/releases/v9.0.0.md, which does not exist", output)

    def test_a_missing_pointed_document_fails(self):
        errors = self._pointer_errors("v9.0.0", None)
        self.assertEqual(len(errors), 1)
        self.assertIn("docs/releases/v9.0.0.md, which does not exist", errors[0])

    def test_a_document_without_the_cursor_item_fails(self):
        for document in (
            CURSOR_ITEM_DOC.replace("Cursor is no longer", "The platform is no longer"),
            CURSOR_ITEM_DOC.replace("## Migration Guide", "## Upgrading"),
            "# Release v9.0.0\n\n## Highlights\n\n**Cursor is no longer supported.**\n\n## Migration Guide\n\nNone.\n",
            "# Release v9.0.0\n\n## Migration Guide\n\nCursor users: see below.\n```\n### Cursor\n```\n",
            "# Release v9.0.0\n\n## Migration Guide\n\n**M-3. Platform removal.** Cursor is gone.\n",
        ):
            with self.subTest(document=document[:60]):
                errors = self._pointer_errors("v9.0.0", document)
                self.assertEqual(len(errors), 1)
                self.assertIn("lacks its Cursor migration item", errors[0])

    def test_a_document_with_the_cursor_item_passes(self):
        for document in (
            CURSOR_ITEM_DOC,
            CURSOR_ITEM_DOC.replace("**Migration Guide item M-3. Cursor is no longer supported.**", "### M-3. Cursor removed"),
            CURSOR_ITEM_DOC.replace("**Migration Guide item M-3.", "- **Migration Guide item M-3."),
        ):
            with self.subTest(document=document[40:120]):
                self.assertEqual(self._pointer_errors("v9.0.0", document), [])

    def test_the_adr_010_appendix_a_item_satisfies_the_anchor(self):
        adr = next((repo_root() / "docs" / "decisions").glob("ADR-010-*.md")).read_text(encoding="utf-8")
        item = next(line for line in adr.splitlines() if line.startswith("**Migration Guide item"))
        self.assertTrue(self.mod.has_cursor_migration_item(f"## Migration Guide\n\n{item}\n"))

    def test_a_pointer_without_cursor_on_its_line_needs_only_existence(self):
        install = "see docs/releases/v9.0.0.md\n"
        self.assertEqual(self._pointer_errors("v9.0.0", "# Release v9.0.0\n", install), [])

    def test_a_pointer_to_a_newer_version_is_not_enforced(self):
        for tag in ("v8.0.0", "v8.9.9", "v8.0.1-rc.1"):
            with self.subTest(tag=tag):
                self.assertEqual(self._pointer_errors(tag, None), [])

    def test_a_pointer_to_the_same_or_an_older_version_is_enforced(self):
        for tag in ("v9.0.0", "v9.0.0-rc.1", "v9.1.0", "v10.0.0", "not-a-tag"):
            with self.subTest(tag=tag):
                self.assertEqual(len(self._pointer_errors(tag, None)), 1)

    def test_develop_is_unaffected_v8_still_passes_on_this_tree(self):
        errors: list[str] = []
        self.mod.check_migration_pointers("v8.0.0", errors)
        self.assertEqual(errors, [])
        code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual((code, "all documentation checks passed" in output), (0, True))

    def test_the_gate_runs_in_ci_only_on_release_tag_pipelines(self):
        ci = yaml.safe_load((repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8"))
        callers = {
            name: job for name, job in ci.items()
            if isinstance(job, dict) and "verify-release-docs.py" in str(job.get("script", ""))
        }
        self.assertEqual(sorted(callers), ["release-docs-gate"])
        rules = callers["release-docs-gate"]["rules"]
        self.assertEqual(len(rules), 1)
        self.assertIn("$CI_COMMIT_TAG =~", rules[0]["if"])
        self.assertNotIn("when", rules[0])


if __name__ == "__main__":
    unittest.main()
