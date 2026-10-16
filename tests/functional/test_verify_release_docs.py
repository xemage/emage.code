"""T675 (TL-T649-12): the release-docs gate rejects an unfilled Gate Verdicts / RELEASE VERDICT."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import unittest
from unittest import mock

from tests._helpers.repo import repo_root


def _load():
    path = repo_root() / "scripts" / "verify-release-docs.py"
    spec = importlib.util.spec_from_file_location("verify_release_docs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load verify-release-docs module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        code, output = self._run_main("v8.0.0")
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


if __name__ == "__main__":
    unittest.main()
