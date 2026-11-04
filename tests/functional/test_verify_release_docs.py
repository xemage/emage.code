"""T675 (TL-T649-12): the release-docs gate rejects an unfilled Gate Verdicts / RELEASE VERDICT.

T703 (SEC-T662-01): it also fails when a release document install.sh points users to is missing
or lacks its Cursor migration item.

T715: the anchor counts only outside fenced code and HTML comments (SEC-T703-01), a pointer in a
form the gate cannot parse fails (SEC-T703-02), a pointer to a newer version fails unless
--allow-newer-pointers is given (SEC-T703-03), main() is pinned to call check_section_requirements
(SEC-T677-02), and the gate-wiring tests no longer depend on the current release (TL-T708-04/-05).

T731: more unparsed pointer forms fail (SEC-T715-01), a "vX.Y.Z release notes" phrase on a Cursor line
needs the Cursor item (SEC-T715-02), an anchor in a raw HTML block does not count (SEC-T715-03), and
every printed line is stripped of control and bidi characters (SEC-T715-04).
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

    ``--allow-newer-pointers`` is passed because this tree's install.sh may name a newer release
    document than the past tag (SEC-T703-03 makes that an error otherwise).

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
        return test._run_main(tag, "--allow-newer-pointers")


def _error_lines(output: str) -> list[str]:
    """The error lines of a gate run (notes and the success lines excluded)."""
    return [
        line for line in output.splitlines()
        if line.startswith("release-docs-verify: ") and not line.startswith("release-docs-verify: note: ")
    ]


class _MainRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def _run_main(self, tag: str, *extra: str) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["verify-release-docs.py", "--tag", tag, *extra]), \
                mock.patch.object(self.mod, "check_version_consistency"), \
                contextlib.redirect_stdout(out):
            return self.mod.main(), out.getvalue()

    def _run_with_install_sh(self, tag: str, install: str, *extra: str) -> tuple[int, str]:
        """main() on this tree for ``tag``, markers patched out, with a synthetic install.sh (an absolute INSTALL_SH)."""
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "install.sh"
            script.write_text(install, encoding="utf-8")
            with mock.patch.object(self.mod, "INSTALL_SH", script), mock.patch.object(self.mod, "check_markers"):
                return self._run_main(tag, *extra)


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


class GateWiringTests(_MainRunner):
    """main() applies the placeholder check to the release document of the tag."""

    def test_the_published_v8_document_passes_the_gate(self):
        code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual((code, "all documentation checks passed" in output), (0, True))

    def test_an_unfilled_verdict_fails_the_gate_with_a_clear_message(self):
        """TL-T708-04: the placeholder error must be the ONLY error, whatever the tree's current release is."""
        real = self.mod.verdict_placeholder_problems
        with mock.patch.object(
            self.mod, "verdict_placeholder_problems",
            side_effect=lambda text: real(text.replace("**Status**: CONDITIONAL_PASS", "**Status**: pending")),
        ):
            code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual(code, 1)
        errors = _error_lines(output)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("unfilled verdict in docs/releases/v8.0.0.md", errors[0])
        self.assertIn("still pending", errors[0])

    def test_main_calls_check_section_requirements(self):
        """SEC-T677-02: dropping the call from main() makes this test fail."""
        def inject(errors):
            errors.append("missing required content in README.md: <injected by the test>")

        with mock.patch.object(self.mod, "check_section_requirements", side_effect=inject) as section_check:
            code, output = _run_past_release_without_markers(self, "v8.0.0")
        section_check.assert_called_once()
        self.assertEqual(code, 1)
        self.assertEqual(_error_lines(output), ["release-docs-verify: missing required content in README.md: <injected by the test>"])

    def test_the_real_section_requirements_hold_on_this_tree(self):
        errors: list[str] = []
        self.mod.check_section_requirements(errors)
        self.assertEqual(errors, [])


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


class MarkerTokenTests(_MainRunner):
    """T717-D2: the `Latest release:` marker is a whole token, so a leftover rc marker fails the final tag."""

    def test_has_marker_matches_the_whole_tag_only(self):
        marker = "Latest release: v9.0.0"
        for text in ("Latest release: v9.0.0\n", "Latest release: v9.0.0", "x (Latest release: v9.0.0).",
                     "Latest release: v9.0.0. Next line", "`Latest release: v9.0.0`"):
            with self.subTest(text=text):
                self.assertTrue(self.mod.has_marker(text, marker))
        for text in ("Latest release: v9.0.0-rc.1\n", "Latest release: v9.0.0-rc1", "Latest release: v9.0.01",
                     "Latest release: v9.0.0.1", "Latest release: v9.0.0rc1", "Latest release: v9.0"):
            with self.subTest(text=text):
                self.assertFalse(self.mod.has_marker(text, marker))

    def test_an_rc_marker_fails_the_final_tag_in_check_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in self.mod.MARKER_FILES:
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_text("# Doc\n\nLatest release: v9.1.0-rc.1\n", encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_markers("Latest release: v9.1.0", errors)
                self.assertEqual(len(errors), len(self.mod.MARKER_FILES), errors)
                rc_errors: list[str] = []
                self.mod.check_markers("Latest release: v9.1.0-rc.1", rc_errors)
                self.assertEqual(rc_errors, [])

    def test_an_rc_marker_in_the_release_document_fails_the_final_tag(self):
        doc = (repo_root() / "docs" / "releases" / "v8.0.0.md").read_text(encoding="utf-8")
        self.assertIn("Latest release: v8.0.0\n", doc)
        broken = doc.replace("Latest release: v8.0.0\n", "Latest release: v8.0.0-rc.1\n")
        with mock.patch.object(Path, "read_text", side_effect=lambda *a, **k: broken):
            errors: list[str] = []
            self.mod.check_release_brief("v8.0.0", "docs/releases/v8.0.0.md", errors)
        self.assertEqual(errors, ["missing required content in docs/releases/v8.0.0.md: Latest release: v8.0.0"])

    def test_the_current_tree_markers_pass(self):
        readme = (repo_root() / "README.md").read_text(encoding="utf-8")
        current = next(line.strip() for line in readme.splitlines() if line.startswith("Latest release:"))
        errors: list[str] = []
        self.mod.check_markers(current, errors)
        self.assertEqual(errors, [])


class MigrationPointerTests(_MainRunner):
    """T703 (SEC-T662-01): a release document install.sh points users to exists and carries its Cursor item."""

    allow_newer = False  # passed to check_migration_pointers; a test sets it on its own instance

    def _pointer_errors(self, tag: str, document: str | None, install: str = INSTALL_SH) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "install.sh").write_text(install, encoding="utf-8")
            if document is not None:
                (root / "docs" / "releases").mkdir(parents=True)
                (root / "docs" / "releases" / "v9.0.0.md").write_text(document, encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
                self.mod.check_migration_pointers(tag, errors, self.allow_newer)
            return errors

    def test_install_sh_on_this_tree_points_to_the_v9_document_for_cursor(self):
        text = (repo_root() / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertEqual(self.mod.install_sh_pointers(text).get("docs/releases/v9.0.0.md"), True)

    def test_main_fails_when_a_pointed_document_is_missing(self):
        """TL-T708-05: replaces the test that skipped once v9.0.0.md existed; a synthetic install.sh names an
        older, never-written document, so main() fails on any tree."""
        code, output = self._run_with_install_sh("v8.0.0", "see docs/releases/v7.99.0.md\n", "--allow-newer-pointers")
        self.assertEqual(code, 1)
        self.assertEqual(len(_error_lines(output)), 1, output)
        self.assertIn("points users to docs/releases/v7.99.0.md, which does not exist", output)

    def test_main_fails_on_a_newer_pointer_unless_allowed(self):
        """SEC-T703-03 through main(): the CI job passes no flag, so a dead pointer fails the tag pipeline."""
        install = "see docs/releases/v99.0.0.md\n"
        code, output = self._run_with_install_sh("v8.0.0", install)
        self.assertEqual(code, 1)
        self.assertIn("docs/releases/v99.0.0.md, a version newer than v8.0.0", output)
        code, output = self._run_with_install_sh("v8.0.0", install, "--allow-newer-pointers")
        self.assertEqual(code, 0, output)
        self.assertIn("release-docs-verify: note: ", output)

    def test_the_ci_job_does_not_allow_newer_pointers(self):
        ci = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("--allow-newer-pointers", ci)

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
            # SEC-T703-01: an anchor a reader does not see does not count
            "# Release v9.0.0\n\n## Migration Guide\n\n~~~\n### Cursor\n~~~\n",
            "# Release v9.0.0\n\n## Migration Guide\n\n````md\n**Cursor removed.**\n```\nstill code\n````\n",
            "# Release v9.0.0\n\n## Migration Guide\n\n<!--\n**Migration Guide item M-3. Cursor is no longer supported.**\n-->\n",
            "# Release v9.0.0\n\n## Migration Guide\n\n<!-- draft\n### M-3. Cursor removed\n",
            "# Release v9.0.0\n\n## Migration Guide\n\n```\nunclosed\n### M-3. Cursor removed\n",
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
            CURSOR_ITEM_DOC.replace("## Migration Guide\n", "## Migration Guide\n\n<!-- note -->\n~~~\ncode\n~~~\n"),
            CURSOR_ITEM_DOC.replace("## Migration Guide\n", "## Migration Guide\n\nUse ```inline``` code.\n"),
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

    def test_a_pointer_to_a_newer_version_fails_unless_allowed(self):
        """SEC-T703-03: it used to be skipped silently."""
        for tag in ("v8.0.0", "v8.9.9", "v8.0.1-rc.1"):
            with self.subTest(tag=tag):
                errors = self._pointer_errors(tag, None)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(f"a version newer than {tag}", errors[0])
                self.allow_newer = True
                self.assertEqual(self._pointer_errors(tag, None), [])
                self.allow_newer = False

    def test_a_pointer_in_a_form_the_gate_cannot_parse_fails(self):
        """SEC-T703-02: such a pointer used to make the gate pass vacuously."""
        for line in (
            'echo "see docs/releases/${VERSION}.md"',
            "see docs/releases/v9.0.md",
            "see releases/v9.0.0.md for Cursor",
            "see Docs/Releases/v9.0.0.md",
            "see the release notes for Cursor",
            "the docs/releases folder",
        ):
            with self.subTest(line=line):
                errors = self._pointer_errors("v9.0.0", CURSOR_ITEM_DOC, install=INSTALL_SH + line + "\n")
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("scripts/install.sh:3 names a release document in a form the gate cannot check", errors[0])

    def test_a_release_notes_phrase_with_a_version_must_name_an_existing_document(self):
        install = INSTALL_SH + "see M-9 of the v8.0.0 release notes\n"
        errors = self._pointer_errors("v9.0.0", CURSOR_ITEM_DOC, install=install)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("docs/releases/v8.0.0.md, which does not exist", errors[0])
        self.assertNotIn("Cursor", errors[0])

    def test_install_sh_on_this_tree_has_only_parsed_pointers(self):
        text = (repo_root() / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertEqual(self.mod.unparsed_pointer_lines(text), [])
        self.assertEqual(self.mod.install_sh_pointers(text).get("docs/releases/v8.0.0.md"), False)

    def test_a_pointer_to_the_same_or_an_older_version_is_enforced(self):
        for tag in ("v9.0.0", "v9.0.0-rc.1", "v9.1.0", "v10.0.0", "not-a-tag"):
            with self.subTest(tag=tag):
                self.assertEqual(len(self._pointer_errors(tag, None)), 1)

    def test_develop_is_unaffected_v8_still_passes_on_this_tree(self):
        errors: list[str] = []
        with contextlib.redirect_stdout(io.StringIO()):
            self.mod.check_migration_pointers("v8.0.0", errors, allow_newer=True)
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



UNSAFE_SAMPLES = "\x00\x07\t\x1b\x7f\x85\x9b؜​‎‏  ‪‮⁠⁦⁩﻿"


class PointerFormTests(_MainRunner):
    """T731 (SEC-T715-01, SEC-T715-02): more pointer forms fail; a prose pointer on a Cursor line needs the item."""

    allow_newer = False
    _pointer_errors = MigrationPointerTests._pointer_errors

    def test_more_pointer_forms_the_gate_cannot_parse_fail(self):
        """SEC-T715-01: each of these forms used to pass unchecked."""
        for line in (
            "see v9.0.0.md for Cursor",
            "see the release-notes",
            "see RELEASE_NOTES.md",
            "see doc/releases",
            "see docs\\releases\\v9.0.0.md",
            'echo "see $REL_DOC"',
            'echo "see ${RELEASE_NOTES} for Cursor"',
            'echo "see $release_doc"',
            "see https://gitlab.com/emage/emage.code/-/wikis/Release-v9",
            "see https://example.org/wiki/Migration",
            "see gitlab.com/emage/emage.code/-/wikis/home",
            "see https://gitlab.com/emage/emage.code/-/releases/v9.0.0",
        ):
            with self.subTest(line=line):
                errors = self._pointer_errors("v9.0.0", CURSOR_ITEM_DOC, install=INSTALL_SH + line + "\n")
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("scripts/install.sh:3 names a release document in a form the gate cannot check", errors[0])

    def test_lines_that_name_no_release_document_still_pass(self):
        for line in (
            'for e in "${DOCS_EXCLUDES[@]}"; do',
            'rel="$rel/x"; req_rel="$req_rel"',
            "the v8.x releases are the last that support it",
            "see AGENTS.md and docs/wiki/quick-start.md",
            "see M-9 of the v8.0.0 release notes and docs/releases/v8.0.0.md",
        ):
            with self.subTest(line=line):
                self.assertEqual(self.mod.unparsed_pointer_lines(line + "\n"), [])

    def test_a_release_notes_phrase_on_a_cursor_line_needs_the_cursor_item(self):
        """SEC-T715-02: the phrase form used to be checked for existence only."""
        install = "see the Cursor item in the v9.0.0 release notes\n"
        self.assertEqual(self.mod.install_sh_pointers(install), {"docs/releases/v9.0.0.md": True})
        broken = CURSOR_ITEM_DOC.replace("Cursor is no longer", "The platform is no longer")
        errors = self._pointer_errors("v9.0.0", broken, install=install)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("lacks its Cursor migration item", errors[0])
        self.assertEqual(self._pointer_errors("v9.0.0", CURSOR_ITEM_DOC, install=install), [])

    def test_no_prose_pointer_on_this_tree_sits_on_a_cursor_line(self):
        """T723 reworded install.sh so the v8.0.0 phrase is on a line without the word Cursor."""
        text = (repo_root() / "scripts" / "install.sh").read_text(encoding="utf-8")
        prose = [line for line in text.splitlines() if self.mod.PROSE_POINTER_RE.search(line)]
        self.assertTrue(prose)
        self.assertEqual([line for line in prose if self.mod.CURSOR_WORD_RE.search(line)], [])


class HtmlBlockAnchorTests(unittest.TestCase):
    """T731 (SEC-T715-03): an anchor inside a CommonMark raw HTML block does not count."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def has_item(self, body: str) -> bool:
        return self.mod.has_cursor_migration_item(f"# Release v9.0.0\n\n## Migration Guide\n\n{body}\n\n## Changelog\n")

    def test_an_anchor_inside_an_html_block_does_not_count(self):
        for body in (
            "<details>\n**Migration Guide item M-3. Cursor is no longer supported.**\n</details>",
            "<div>\n### M-3. Cursor removed",
            "  <DIV class=\"x\">\n**Cursor removed.**",
            "<pre>\n### Cursor\n</pre>",
            "<script type=\"text/plain\">\n\n### Cursor\n\n</script>",
            "<?php\n### Cursor\n?>",
            "<!DOCTYPE note\n### Cursor\n>",
            "<![CDATA[\n### Cursor\n]]>",
            "<!-- x\n### Cursor\n-->",
            "<span class=\"note\">\n### M-3. Cursor removed",
            "<custom-tag data-x='1'/>\n**Cursor removed.**",
            "</section>\n**Cursor removed.**",
            # SEC-T731-01: a type 7 block may follow any block that is not a paragraph
            "***\n<span>\n**Migration Guide item M-3. Cursor removed.**",
            "Title\n=====\n<span>\n**Migration Guide item M-3. Cursor removed.**",
            "    indented code\n<span>\n**Migration Guide item M-3. Cursor removed.**",
        ):
            with self.subTest(body=body[:40]):
                self.assertFalse(self.has_item(body))

    def test_a_tag_line_after_a_line_that_is_no_paragraph_hides_the_anchor(self):
        """SEC-T731-01: these previous lines end the paragraph, so the tag line opens a type 7 block."""
        for previous in ("> ---", "> # h", "> ```", "*", "+", "1.", "| a | b |", ">>>"):
            with self.subTest(previous=previous):
                self.assertFalse(self.has_item(f"{previous}\n<span>\n**M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"{previous}\n<span>\n- a\n- **M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"{previous}\n<span>\n### h\n**M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"{previous}\n<span>\n### h\n### M-3. Cursor removed"))

    def test_an_anchor_inside_a_multi_line_inline_construct_does_not_count(self):
        """SEC-T731-06: the reader sees no bold lead; the closing part is on the line after the anchor."""
        for body in (
            '[x]: /u "\n**M-3. Cursor removed.**\n"',
            '<a title="\n**M-3. Cursor removed.**\n">',
            "x <?\n**M-3. Cursor removed.**\n?>",
            "![\n**M-3. Cursor removed.**\n](u)",
            "x <?\n2. a\n3. **M-3. Cursor removed.**\n?>",
            "x <?\n    <!-- c -->\n**M-3. Cursor removed.**\n?>",
            "x <?  <!--\nc -->\n**M-3. Cursor removed.**\n?>",
            "x <?\n``` a ```\n**M-3. Cursor removed.**\n?>",
            *(f"x <?\n{char}\n**M-3. Cursor removed.**\n?>" for char in ("\v", "\f", "\x85", "\u2028")),
        ):
            with self.subTest(body=body[:30]):
                self.assertFalse(self.has_item(body))

    def test_an_anchor_right_after_a_paragraph_line_is_a_false_fail_by_design(self):
        """T731: the rule cannot tell these visible anchors from the hidden ones above, so they do not count."""
        for body in (
            "Some text\n<span>\n**M-3. Cursor removed.**",  # counted before: type 7 cannot interrupt a paragraph
            "Some text\n**M-3. Cursor removed.**",
            "Some text\n### M-3. Cursor removed",
            "x\n- a\n- **M-3. Cursor removed.**",
        ):
            with self.subTest(body=body[:30]):
                self.assertFalse(self.has_item(body))

    def test_an_anchor_outside_an_html_block_still_counts(self):
        for body in (
            "<details>\n<summary>x</summary>\n</details>\n\n**Migration Guide item M-3. Cursor is no longer supported.**",
            "<pre>code</pre>\n### M-3. Cursor removed",
            "<!-- note -->\n### M-3. Cursor removed",
            "- a\n- **M-3. Cursor removed.**",
            "1. a\n2. **M-3. Cursor removed.**",
            "### h\n**M-3. Cursor removed.**",
            "Text with <span>inline</span> HTML.\n\n### M-3. Cursor removed",
            "<div>\n</div>\n\n```\n<div>\n```\n### M-3. Cursor removed",
        ):
            with self.subTest(body=body[:40]):
                self.assertTrue(self.has_item(body))

    def test_only_commonmark_line_ends_end_a_line(self):
        """SEC-T731-02: str.splitlines() also split at these, which ended the block or made a line start."""
        for char in ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"):
            with self.subTest(char=hex(ord(char))):
                body = f"<details>\n{char}\n**Migration Guide item M-3. Cursor removed.**\n</details>"
                self.assertFalse(self.has_item(body))
                self.assertFalse(self.has_item(f"Some text{char}**Migration Guide item M-3. Cursor removed.**"))
        for end in ("\n", "\r\n", "\r"):
            with self.subTest(end=repr(end)):
                self.assertTrue(self.has_item(f"<div>{end}{end}### M-3. Cursor removed"))
                self.assertEqual(len(self.mod.strip_hidden_markdown(f"a{end}<div>{end}b{end}{end}c").split("\n")), 5)

    def test_the_line_count_is_kept(self):
        text = "a\n<div>\nb\n\nc\n<pre>\nd\n</pre>\ne"
        stripped = self.mod.strip_hidden_markdown(text)
        self.assertEqual(stripped.split("\n"), ["a", "", "", "", "c", "", "", "", "e"])

    def test_tag_line_matching_does_not_backtrack_on_long_lines(self):
        import time
        start = time.monotonic()
        for line in ("<a" + " " * 60000 + "!", "<a" + " b=c" * 20000 + " !", "<a" + " b" * 30000 + "!"):
            self.mod.strip_hidden_markdown("\n" + line + "\n")
        self.assertLess(time.monotonic() - start, 1.0)

    def test_the_v9_document_keeps_its_cursor_item(self):
        text = (repo_root() / "docs" / "releases" / "v9.0.0.md").read_text(encoding="utf-8")
        self.assertTrue(self.mod.has_cursor_migration_item(text))


class LineBreakCharacterTests(_MainRunner):
    """T731 (SEC-T731-02 follow-up): a checked document holding a non-CommonMark line separator fails the gate."""

    CHARS = ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", " ", " ")

    def _errors(self, relative: str, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_text(text, encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_line_breaks([*self.mod.MARKER_FILES, Path("docs/releases/v9.0.0.md")], errors)
            return errors

    def test_each_character_in_the_release_document_fails(self):
        for char in self.CHARS:
            with self.subTest(char=hex(ord(char))):
                text = f"# R\r\n\n## RELEASE VERDICT\r- **Status**: PASS{char}- **Status**: pending\n{char}\n"
                errors = self._errors("docs/releases/v9.0.0.md", text)
                self.assertEqual(errors, [
                    f"docs/releases/v9.0.0.md:4 holds U+{ord(char):04X}, a line separator that Markdown does not "
                    "treat as a line end; remove it (SEC-T731-02)"
                ])
                self.assertNotIn(char, errors[0])

    def test_a_marker_file_with_the_character_fails(self):
        errors = self._errors("docs/wiki/home.md", "# Home\n\nLatest release: v9.0.0 \n")
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith("docs/wiki/home.md:3 holds U+2028"), errors[0])

    def test_clean_documents_pass(self):
        self.assertEqual(self._errors("README.md", "# R\r\n\tok\n"), [])
        errors: list[str] = []
        self.mod.check_line_breaks([*self.mod.MARKER_FILES, Path("docs/releases/v9.0.0.md")], errors)
        self.assertEqual(errors, [])

    def test_main_checks_the_release_document_and_the_marker_files(self):
        with mock.patch.object(self.mod, "check_line_breaks") as check:
            code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual(code, 0, output)
        check.assert_called_once()
        self.assertEqual(check.call_args.args[0], [*self.mod.MARKER_FILES, Path("docs/releases/v8.0.0.md")])


class PrintableOutputTests(_MainRunner):
    """T731 (SEC-T715-04): no control or bidi character of a checked file reaches the CI log."""

    def assert_clean(self, output: str) -> None:
        self.assertEqual([c for c in UNSAFE_SAMPLES if c in output.replace("\n", "")], [])

    def test_printable_replaces_each_unsafe_character(self):
        self.assertEqual(self.mod.printable("a" + UNSAFE_SAMPLES + "b"), "a" + "?" * len(UNSAFE_SAMPLES) + "b")
        self.assertEqual(self.mod.printable("plain v9.0.0 text: ok"), "plain v9.0.0 text: ok")

    def test_the_pattern_matches_check_release_tag_tree(self):
        path = repo_root() / "scripts" / "check-release-tag-tree.py"
        spec = importlib.util.spec_from_file_location("check_release_tag_tree", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(self.mod.UNSAFE_RE.pattern, module.UNSAFE_RE.pattern)

    def test_an_install_sh_line_is_printed_without_control_characters(self):
        install = "see \x1b[2Jdocs/releases‮/v9.0.md\x07 now\n"
        code, output = self._run_with_install_sh("v8.0.0", install, "--allow-newer-pointers")
        self.assertEqual(code, 1)
        self.assertIn("names a release document in a form the gate cannot check", output)
        self.assertIn("see ?[2Jdocs/releases?/v9.0.md? now", output)
        self.assert_clean(output)

    def test_a_verdict_line_is_printed_without_control_characters(self):
        real = self.mod.verdict_placeholder_problems
        dirty = "**Status**: pending \x1b]8;;https://x\x07⁦x⁩"
        with mock.patch.object(
            self.mod, "verdict_placeholder_problems",
            side_effect=lambda text: real(text.replace("**Status**: CONDITIONAL_PASS", dirty)),
        ):
            code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual(code, 1)
        self.assertIn("still pending", output)
        self.assert_clean(output)

if __name__ == "__main__":
    unittest.main()
