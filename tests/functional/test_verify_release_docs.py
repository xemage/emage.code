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

T738: scripts/install.sh is inside the line-separator refusal (SEC-T731-07), and the end of an HTML
block is searched on the whole start line, so <!--> and <?> close on their own line (SEC-T731-09(a)).

T739 (plan-136): the Migration Guide check reads the document with markdown-it-py. That closes SEC-T731-09(b),
SEC-T738-01, SEC-T738-03 and SEC-T731-08, and a run without the parser exits 1 (ParserMissingTests).

T741 (SEC-T739-01): a file the gate reads that is not valid UTF-8 ends the run with exit 1 (StrictReadTests).
"""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import os
import subprocess
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


def require_parser(case: unittest.TestCase) -> None:
    """The gate's parser. As in test_publish_release_t716.py: with ``CI`` set a missing markdown-it-py FAILS the test
    (ci/requirements-ci.txt provides it); only outside CI does the test skip, and it says so."""
    if case.mod.MarkdownIt is not None:
        return
    if os.environ.get("CI"):
        case.fail("markdown-it-py is not installed although CI is set: ci/requirements-ci.txt must provide it")
    case.skipTest("markdown-it-py is not installed (outside CI only; CI fails here)")


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
        require_parser(self)
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


# SEC-T741-08: reading a file by any of these goes round read_strict.
_FORBIDDEN_READ_NAMES = {"open", "getattr", "__import__", "eval", "exec"}
_FORBIDDEN_READ_MODULES = {"io", "os", "codecs", "fileinput", "mmap", "tempfile", "importlib", "shutil"}


def _forbidden_read_nodes(tree: ast.AST) -> list[str]:
    """What no function of the gate may hold, read_strict included: a lenient route, or a module that offers one."""
    problems: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _FORBIDDEN_READ_NAMES:
            problems.append(f"line {node.lineno}: {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr in ("open", "read_text"):
            problems.append(f"line {node.lineno}: .{node.attr}")
        elif isinstance(node, ast.Call) and any(keyword.arg == "errors" for keyword in node.keywords):
            problems.append(f"line {node.lineno}: an errors keyword")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            problems += [f"line {node.lineno}: import {n}" for n in names if n.split(".")[0] in _FORBIDDEN_READ_MODULES]
    return problems


def _read_route_problems(source: str) -> list[str]:
    """Each way ``source`` reads or decodes a file other than through ``read_strict`` (SEC-T741-08).

    ``read_bytes`` and ``decode`` occur exactly once each, in ``read_strict``, and that decode takes only the codec.
    """
    tree = ast.parse(source)
    problems = _forbidden_read_nodes(tree)
    strict = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "read_strict"]
    if len(strict) != 1:
        return [*problems, "not exactly one read_strict"]
    inside = {id(node) for node in ast.walk(strict[0])}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in ("read_bytes", "decode") and id(node) not in inside:
            problems.append(f"line {node.lineno}: .{node.attr} outside read_strict")
    inner = [node for node in ast.walk(strict[0]) if isinstance(node, ast.Attribute)]
    for name in ("read_bytes", "decode"):
        if sum(node.attr == name for node in inner) != 1:
            problems.append(f"read_strict does not hold exactly one .{name}")
    decodes = [node for node in ast.walk(strict[0]) if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Attribute) and node.func.attr == "decode"]
    if any(len(call.args) != 1 or call.keywords for call in decodes):
        problems.append("the decode in read_strict takes more than the codec")
    return problems


class VerdictPlaceholderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def setUp(self):
        require_parser(self)

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


class VerdictSectionTokenTests(unittest.TestCase):
    """T747 (plan-142, SEC-T739-07): the verdict sections come from the parser's tokens, the field logic is unchanged."""

    PENDING = "- Status: pending"
    STILL_PENDING = "RELEASE VERDICT: value is still pending: - Status: pending"
    SECOND_HEADING = "RELEASE VERDICT: 2 top-level headings have this name; the gate reads the first, so keep one"
    EMPTY = "RELEASE VERDICT: the heading is present but the section is empty or only inside a code block"
    ABSENT = "missing required content in doc.md: ## RELEASE VERDICT"
    OPENING = "# Release v9.0.0\n\nLatest release: v9.0.0\n\n## Install\n\nx\n\n## Highlights\n\nx\n\n"

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def setUp(self):
        require_parser(self)

    def problems(self, body: str) -> list[str]:
        return self.mod.verdict_placeholder_problems(f"# R\n\n{body}\n")

    def in_section(self, body: str) -> list[str]:
        return self.problems(f"## RELEASE VERDICT\n\n- Version: v9.0.0\n\n{body}")

    def gate_errors(self, body: str) -> list[str]:
        """The errors of check_release_brief, the gate's own route, on a document with ``body`` as its verdict."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "doc.md").write_text(self.OPENING + body + "\n", encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_release_brief("v9.0.0", Path("doc.md"), errors)
            return errors

    def unfilled(self, problem: str) -> str:
        return f"unfilled verdict in doc.md: {problem}"

    def test_control_a_heading_and_a_pending_field(self):
        self.assertEqual(self.gate_errors(f"## RELEASE VERDICT\n\n{self.PENDING}"), [self.unfilled(self.STILL_PENDING)])

    def test_shape_a_the_heading_first_inside_a_comment(self):
        body = f"<!--\n## RELEASE VERDICT\n-->\n\n## RELEASE VERDICT\n\n{self.PENDING}"
        self.assertEqual(self.gate_errors(body), [self.unfilled(self.STILL_PENDING)])

    def test_shape_b_a_comment_holding_a_heading_line(self):
        body = f"## RELEASE VERDICT\n\n<!--\n## x\n-->\n\n{self.PENDING}"
        self.assertEqual(self.gate_errors(body), [self.unfilled(self.STILL_PENDING)])

    def test_shape_c_two_fence_marks_in_paragraphs_pair_up_around_the_field(self):
        """SEC-T739-07 (c): "FENCED_CODE_RE pairing two ``` in a paragraph"."""
        body = f"## RELEASE VERDICT\n\nSee the ``` mark.\n\n{self.PENDING}\n\nThe other ``` mark."
        self.assertNotIn("Status", self.mod.FENCED_CODE_RE.sub("", body))  # what the line rules read
        self.assertEqual(self.gate_errors(body), [self.unfilled(self.STILL_PENDING)])

    def test_shape_d_a_filled_heading_then_a_second_with_the_pending_field(self):
        body = f"## RELEASE VERDICT\n\n- Status: PASS\n\n## RELEASE VERDICT\n\n{self.PENDING}"
        self.assertEqual(self.gate_errors(body), [self.unfilled(self.SECOND_HEADING)])

    def test_the_first_of_two_headings_is_the_one_read(self):
        body = f"## RELEASE VERDICT\n\n{self.PENDING}\n\n## RELEASE VERDICT\n\n- Status: PASS"
        self.assertEqual(self.gate_errors(body), [self.unfilled(self.SECOND_HEADING), self.unfilled(self.STILL_PENDING)])

    def test_a_repeat_of_the_heading_in_code_or_a_comment_is_no_second_heading(self):
        for repeat in ("```\n## RELEASE VERDICT\n```", "<!--\n## RELEASE VERDICT\n-->", "> ## RELEASE VERDICT"):
            with self.subTest(repeat):
                self.assertEqual(self.gate_errors(f"## RELEASE VERDICT\n\n- Status: PASS\n\n{repeat}"), [])

    def test_shape_f_the_heading_and_a_filled_field_only_in_a_comment(self):
        body = "<!--\n## RELEASE VERDICT\n\n- Status: PASS\n-->"
        self.assertEqual(self.gate_errors(body), [self.ABSENT, self.unfilled(self.EMPTY)])

    def test_shape_h_a_setext_heading_fails_on_the_placeholder(self):
        self.assertEqual(self.gate_errors(f"RELEASE VERDICT\n---\n\n{self.PENDING}"), [self.unfilled(self.STILL_PENDING)])

    def test_shape_i_the_heading_only_in_a_blockquote(self):
        self.assertEqual(self.gate_errors("> ## RELEASE VERDICT\n>\n> - Status: PASS"), [self.ABSENT])

    def test_every_form_of_a_real_heading_is_read(self):
        for heading in (" ## RELEASE VERDICT", "## RELEASE VERDICT ##", "##\tRELEASE VERDICT", "## RELEASE&#32;VERDICT",
                        "## `RELEASE VERDICT`", "RELEASE VERDICT\n----"):
            with self.subTest(heading):
                self.assertEqual(self.gate_errors(f"{heading}\n\n{self.PENDING}"), [self.unfilled(self.STILL_PENDING)])

    def test_a_real_heading_with_an_empty_section_stays_a_problem_in_every_form(self):
        for heading in ("## RELEASE VERDICT", " ## RELEASE VERDICT", "RELEASE VERDICT\n---"):
            with self.subTest(heading):
                self.assertEqual(self.gate_errors(f"{heading}\n\n## Next"), [self.unfilled(self.EMPTY)])

    def test_a_section_holding_only_a_heading_that_renders_as_nothing_is_empty(self):
        """SEC-T748-01: the old line rule ended the section at such a heading, which left it empty."""
        for empty in ("## &#32;", "## <!-- x -->", "##", "&#32;\n---", "## &#8203;", "## <span hidden>x</span>"):
            with self.subTest(empty):
                self.assertEqual(self.gate_errors(f"## RELEASE VERDICT\n\n{empty}"), [self.unfilled(self.EMPTY)])

    def test_a_heading_a_reader_cannot_see_does_not_end_a_section(self):
        """SEC-T748-02: format characters survive str.strip, and HTML may hide the heading. Each form, each level."""
        hidden = ("## &#8203;", "## &#8203; &#8203;", "## &shy;", "## &#x2060;", " ## &#8203;", "##\t&#8203;", "# &#8203;", "&#8203;\n---",
                  "&#8203;\n===", "## <span hidden>x</span>", "# <b>x</b>", "<b>x</b>\n---")
        for heading in hidden:
            with self.subTest(heading):
                self.assertEqual(self.in_section(f"{heading}\n\n{self.PENDING}"), [self.STILL_PENDING])

    def test_a_marker_on_the_line_of_a_heading_that_does_not_end_a_section_is_read(self):
        """SEC-T748-10: the old check read these lines, in every form but ``## `` at column 0."""
        for line in ("# <span>TBD</span>", "<span>TBD</span>\n---", " ## <span>TBD</span>", "##\t<span>TBD</span>",
                     "# <b>YYYY-MM-DD</b>", "# <!-- TBD -->", " ## <!-- TBD -->", "# ![TBD](u)", "## <span>TBD</span>"):
            with self.subTest(line):
                self.assertTrue(self.in_section(line))

    def test_a_field_inside_a_setext_heading_that_does_not_end_a_section_is_read(self):
        """SEC-T748-10: a line indented 4 spaces continues the paragraph, so it lies inside the heading's map."""
        self.assertEqual(self.in_section(f"<b>Note</b>\n    {self.PENDING}\n---"), [
            f"RELEASE VERDICT: value is still pending: {self.PENDING}"])

    def test_a_visible_heading_holding_html_ends_the_empty_test(self):
        """SEC-T748-11: an anchor in the next heading must not lend its section's text to an empty verdict."""
        for heading in ('## <a name="x"></a>Rollback Plan', "<b>Rollback Plan</b>\n---"):
            with self.subTest(heading):
                self.assertEqual(self.gate_errors(f"## RELEASE VERDICT\n\n{heading}\n\nSome text"), [self.unfilled(self.EMPTY)])

    def test_a_heading_a_reader_can_see_still_ends_a_section(self):
        for heading in ("## Next", "## Next <!-- x -->", "# Next", "Next\n---", "## `Next`"):
            with self.subTest(heading):
                self.assertEqual(self.in_section(f"{heading}\n\n{self.PENDING}"), [])

    def test_the_heading_line_in_a_displayed_html_block_is_refused(self):
        """SEC-T748-04: the block's text is shown, and the old check read the section from that line."""
        filled = "## RELEASE VERDICT\n\n- Status: PASS"
        problem = "RELEASE VERDICT: its heading line is inside an HTML block, which a reader may see; move it out"
        for block in ("<div>\n## RELEASE VERDICT\n- Status: pending\n</div>", "<details>\n## RELEASE VERDICT  \n</details>"):
            with self.subTest(block):
                self.assertEqual(self.problems(f"{block}\n\n{filled}"), [problem])
        self.assertEqual(self.problems(f"<div>\n- x: y\n</div>\n\n{filled}"), [], "another line in the block")
        self.assertEqual(self.problems(f"<!--\n## RELEASE VERDICT\n- Status: pending\n-->\n\n{filled}"), [], "a comment is hidden")

    def test_a_heading_of_another_level_is_no_section(self):
        for heading in ("# RELEASE VERDICT", "### RELEASE VERDICT", "RELEASE VERDICT\n==="):
            with self.subTest(heading):
                self.assertIn(self.ABSENT, self.gate_errors(f"{heading}\n\n- Status: PASS"))

    def test_the_name_of_a_section_is_exact(self):
        for heading in ("## The RELEASE VERDICT", "## release verdict", "## RELEASE VERDICTS", "## RELEASE VERDICT draft"):
            with self.subTest(heading):
                self.assertIn(self.ABSENT, self.gate_errors(f"{heading}\n\n- Status: PASS"))

    def test_an_empty_heading_does_not_end_a_section(self):
        for empty in ("## &#32;", "## <!-- x -->", "##", "# &#32;", "## ![alt](u)", "&#32;\n---"):
            with self.subTest(empty):
                self.assertEqual(self.in_section(f"{empty}\n\n{self.PENDING}"), [self.STILL_PENDING])

    def test_a_heading_with_text_ends_a_section_in_either_form_and_at_either_level(self):
        for heading in ("## Next", "# Next", "Next\n---", "Next\n===", "## `code`"):
            with self.subTest(heading):
                self.assertEqual(self.in_section(f"{heading}\n\n{self.PENDING}"), [])

    def test_what_is_not_a_top_level_level_one_or_two_heading_does_not_end_a_section(self):
        for line in ("### Next", "###### Next", "> ## Next", "- ## Next", "<!--\n## Next\n-->", "```\n## Next\n```",
                     "    ## Next"):
            with self.subTest(line):
                self.assertEqual(self.in_section(f"{line}\n\n{self.PENDING}"), [self.STILL_PENDING])

    def test_a_field_in_a_closed_backtick_fence_is_skipped_at_any_depth_and_a_field_after_it_is_read(self):
        field = "- Date: YYYY-MM-DD"
        for code in (f"```\n{field}\n```", f"```\n{field}\n```  \t", f"```\n{field}\n`````", f"````\n{field}\n````",
                     f"``` info\n{field}\n```", f"Text.\n\n  ```\n{field}\n  ```", f"- item\n\n  ```\n  {field}\n  ```",
                     f"- ```\n  {field}\n  ```", f"> ```\n> {field}\n> ```", f"- item\n\n  > ```\n  > {field}\n  > ```",
                     f"> - ```\n>   {field}\n>   ```", f"1. item\n\n   ```\n   {field}\n   ```"):
            with self.subTest(code):
                self.assertEqual(self.in_section(code), [])
                self.assertEqual(self.in_section(f"{code}\n\nAfter.\n\n{self.PENDING}"), [self.STILL_PENDING])

    def test_a_closed_fence_at_the_very_end_of_the_document_is_skipped(self):
        text = f"## RELEASE VERDICT\n\n- Version: 1\n\n```\n{self.PENDING}\n```"
        self.assertEqual(self.mod.verdict_placeholder_problems(text), [])

    def test_other_code_is_read_like_any_other_lines(self):
        for code in (f"~~~\n{self.PENDING}\n~~~", f"```\n{self.PENDING}", f"```\n{self.PENDING}\n``` trailing",
                     f"````\n{self.PENDING}\n```", f"Text.\n\n    {self.PENDING}", f"- item\n\n      {self.PENDING}",
                     f"- item\n\n  ```\n  {self.PENDING}\n\nAfter.", f"```\n{self.PENDING}\n     ```",
                     f"```\n{self.PENDING}\n> ```", f"~~~\n{self.PENDING}\n```"):
            with self.subTest(code):
                self.assertEqual(self.in_section(code), [self.STILL_PENDING])

    def test_an_unclosed_fence_in_a_blockquote_is_read(self):
        """The field rule does not read a ``> `` line, so a placeholder stands in for the pending field."""
        found = self.in_section("> ```\n> - Date: YYYY-MM-DD\n\nAfter.")
        self.assertEqual(found, ["RELEASE VERDICT: unfilled placeholder 'YYYY-MM-DD': > - Date: YYYY-MM-DD"])

    def test_an_unclosed_fence_at_the_end_of_a_document_with_no_final_newline_is_read(self):
        marker = "RELEASE VERDICT: unfilled placeholder 'YYYY-MM-DD': "
        for tail, line in ((f"```\n{self.PENDING}", None), (f"```\n{self.PENDING}\n   ", None),
                           (f"- ```\n  {self.PENDING}\n  ", None), ("> ```\n> YYYY-MM-DD\n>", "> YYYY-MM-DD")):
            with self.subTest(tail):
                text = f"## RELEASE VERDICT\n\n{tail}"
                wanted = self.STILL_PENDING if line is None else marker + line
                self.assertEqual(self.mod.verdict_placeholder_problems(text), [wanted])

    def test_a_section_with_only_an_indented_block_is_read_as_lines(self):
        self.assertEqual(self.problems("## RELEASE VERDICT\n\n    - Status: PASS"), [])

    def test_a_code_line_outside_the_section_changes_nothing_inside_it(self):
        self.assertEqual(self.problems(f"```\nx\n```\n\n## RELEASE VERDICT\n\n{self.PENDING}"), [self.STILL_PENDING])

    def test_a_block_that_ends_with_its_container_leaves_the_next_line_a_field(self):
        self.assertEqual(self.in_section(f"> ```\n{self.PENDING}"), [self.STILL_PENDING])

    def test_html_lines_stay_scanned(self):
        for html in (f"<!--\n{self.PENDING}\n-->", f"<div hidden>\n{self.PENDING}\n</div>", "<!-- TBD -->"):
            with self.subTest(html):
                self.assertTrue(self.in_section(html))

    def test_a_code_block_is_blanked_and_does_not_join_the_lines_around_it(self):
        """As with the old blanking, a sub-list after a block is not the value of the field before the block."""
        found = self.in_section("- Features:\n```\nx\n```\n  - a")
        self.assertEqual(found, ["RELEASE VERDICT: field has no value: - Features:"])

    def test_a_section_with_only_code_is_empty(self):
        self.assertEqual(self.problems("## RELEASE VERDICT\n\n```\n- Status: PASS\n```"), [self.EMPTY])

    def test_gate_verdicts_stays_optional_and_a_raw_heading_with_no_real_one_is_a_problem(self):
        self.assertEqual(self.problems("no sections"), [])
        empty = "Gate Verdicts: the heading is present but the section is empty or only inside a code block"
        for swallowed in ("```\n## Gate Verdicts\n\n- x: PASS", "<!--\n## Gate Verdicts\n\n- x: PASS"):
            with self.subTest(swallowed):
                self.assertEqual(self.problems(swallowed), [empty])

    def test_a_misspelt_optional_heading_still_passes(self):
        """plan-142 § Not changed: visible to a reader, and the name is exact."""
        self.assertEqual(self.problems("## Gate verdicts\n\n- x: pending"), [])

    def test_a_heading_past_the_nesting_limit_is_absent(self):
        self.assertEqual(self.gate_errors("- " * 9 + "x\n\n## RELEASE VERDICT\n\n- Status: PASS"), [])
        body = "- " * 10 + "x\n\n## RELEASE VERDICT\n\n- Status: PASS"
        self.assertEqual(self.gate_errors(body), [self.ABSENT, self.unfilled(self.EMPTY)])

    def test_a_section_runs_on_past_the_nesting_limit(self):
        self.assertEqual(self.in_section("- " * 9 + f"x\n\n## Next\n\n{self.PENDING}"), [])
        self.assertEqual(self.in_section("- " * 10 + f"x\n\n## Next\n\n{self.PENDING}"), [self.STILL_PENDING])

    def test_a_character_that_only_splitlines_breaks_at_keeps_the_lines_aligned(self):
        """Reached directly; the gate itself refuses such a document in check_line_breaks (SEC-T731-02)."""
        for char in ("\f", "\u2028", "\v", "\x85"):
            with self.subTest(char=hex(ord(char))):
                above = f"a{char * 9}b\n\n## RELEASE VERDICT\n\n{self.PENDING}\n\n## Next\n\nx\n"
                self.assertEqual(self.mod.verdict_placeholder_problems(above), [self.STILL_PENDING])
                inside = f"## RELEASE VERDICT\n\n```\nx{char * 9}\n```\n\n{self.PENDING}\n"
                self.assertEqual(self.mod.verdict_placeholder_problems(inside), [self.STILL_PENDING])

    def test_such_a_character_still_splits_a_field_for_the_field_logic(self):
        """What the old check caught when reached directly stays caught."""
        self.assertEqual(self.in_section(f"text\f{self.PENDING}"), [self.STILL_PENDING])

    def test_a_carriage_return_reached_directly_keeps_the_lines_aligned(self):
        for ending in ("\r", "\r\n"):
            with self.subTest(ending=repr(ending)):
                text = f"a{ending}b{ending}{ending}## RELEASE VERDICT{ending}{ending}{self.PENDING}{ending}"
                self.assertEqual(self.mod.verdict_placeholder_problems(text), [self.STILL_PENDING])

    def test_a_long_line_is_never_parsed_and_the_direct_call_fails_closed(self):
        document = f"## RELEASE VERDICT\n\n- Status: PASS\n\n{'x' * (self.mod.MAX_LINE_CHARS + 1)}\n"
        with mock.patch.object(self.mod, "MarkdownIt", side_effect=AssertionError("the parser ran")):
            found = self.mod.verdict_placeholder_problems(document)
            self.assertEqual(self.mod.section_text(document, "## RELEASE VERDICT"), "")
        self.assertEqual(len(found), 1)
        self.assertIn(f"longer than {self.mod.MAX_LINE_CHARS} characters", found[0])

    def _parses_of_a_run(self, documents: dict[str, str], tag: str) -> int:
        """How often the parser runs over check_migration_pointers and check_release_brief, as run_checks calls them."""
        install = "#!/bin/sh\n" + "".join(f"echo 'the Cursor item in docs/releases/{name}.md'\n" for name in documents)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / self.mod.INSTALL_SH).write_text(install, encoding="utf-8")
            (root / "docs" / "releases").mkdir(parents=True)
            for name, text in documents.items():
                (root / "docs" / "releases" / f"{name}.md").write_text(text, encoding="utf-8")
            self.mod.markdown_tokens.cache_clear()
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root), \
                    mock.patch.object(self.mod, "MarkdownIt", wraps=self.mod.MarkdownIt) as parser:
                self.mod.check_migration_pointers(tag, errors)
                self.mod.check_release_brief(tag, Path(f"docs/releases/{tag}.md"), errors)
            self.assertEqual(errors, [])
            return parser.call_count

    def _release_document(self, tag: str) -> str:
        return (f"# Release {tag}\n\nLatest release: {tag}\n\n## Install\n\nx\n\n## Highlights\n\nx\n\n"
                "## Gate Verdicts\n\n- Security: PASS\n\n## RELEASE VERDICT\n\n- Status: PASS\n\n"
                "## Migration Guide\n\n### M-3. Cursor removed\n")

    def test_the_document_is_parsed_once_per_run(self):
        self.assertEqual(self._parses_of_a_run({"v9.0.0": self._release_document("v9.0.0")}, "v9.0.0"), 1)

    def test_the_own_document_is_parsed_once_when_another_sorts_after_it(self):
        """'v10.0.0' sorts before 'v9.0.0', so a cache of the last text alone would parse the own document twice."""
        documents = {name: self._release_document(name) for name in ("v10.0.0", "v9.0.0")}
        self.assertEqual(self._parses_of_a_run(documents, "v10.0.0"), 2)

    def test_the_help_and_the_docstring_describe_this_check(self):
        collapsed = " ".join(self.mod.MIGRATION_POINTER_HELP.split())
        for phrase in ("(T747, SEC-T739-07)", "the first top-level level 2 heading", "whose text is not empty", "format characters such as U+200B",
                       "inside an HTML block other than comments",
                       "A second top-level heading with the same name is an error",
                       "Only the lines of a closed ``` fence, at any depth, do not count", "An indented code block",
                       "a ~~~ fence", "an unclosed fence", "trailing text or too few backticks",
                       "a hidden 'pending' still fails", "RELEASE VERDICT must be a real top-level heading",
                       "Gate Verdicts is optional", "both fail closed"):
            with self.subTest(phrase):
                self.assertIn(phrase, collapsed)
        docstring = " ".join(self.mod.__doc__.split())
        self.assertIn("``markdown_tokens`` calls it", docstring)
        self.assertIn("the verdict sections", docstring)
        self.assertNotIn("``has_cursor_migration_item`` uses it", docstring)


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
        with mock.patch.object(self.mod, "read_strict", return_value=broken):
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
        require_parser(self)
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
        require_parser(self)
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
        require_parser(self)
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



UNSAFE_SAMPLES = "\x00\x07\t\x1b\x7f\x85\x9b\u061c\u200b\u200e\u200f\u2028\u2029\u202a\u202e\u2060\u2066\u2069\ufeff"


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
    """T731 (SEC-T715-03): an anchor inside a CommonMark raw HTML block does not count. T739: the parser decides."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def setUp(self):
        require_parser(self)

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
        for previous in ("> ---", "> # h", "> ```", "*", "+", "1.", ">>>"):
            with self.subTest(previous=previous):
                self.assertFalse(self.has_item(f"{previous}\n<span>\n**M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"{previous}\n<span>\n- a\n- **M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"{previous}\n<span>\n### h\n**M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"{previous}\n<span>\n### h\n### M-3. Cursor removed"))

    def test_a_table_row_is_a_paragraph_line_and_a_tag_line_after_it_is_live_html(self):
        """T739: the commonmark preset has no tables. '| a | b |' is a paragraph, and '<span>' cannot interrupt one.
        So the tag is inline HTML in that paragraph, and since T743's ruling it ends the search."""
        self.assertFalse(self.has_item("| a | b |\n<span>\n**M-3. Cursor removed.**"))  # one paragraph: no lead
        self.assertFalse(self.has_item("| a | b |\n<span>\n- a\n- **M-3. Cursor removed.**"))
        self.assertFalse(self.has_item("| a | b |\n<span>\n### h\n**M-3. Cursor removed.**"))
        self.assertFalse(self.has_item("| a | b |\n<span>\n### h\n### M-3. Cursor removed"))
        self.assertTrue(self.has_item("| a | b |\n- a\n- **M-3. Cursor removed.**"))
        self.assertTrue(self.has_item("| a | b |\n### M-3. Cursor removed"))

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

    def test_a_lead_inside_a_paragraph_is_not_a_lead(self):
        """The line joins the paragraph, so the strong span does not open it (T731's false FAIL, now by the parser)."""
        for body in ("Some text\n<span>\n**M-3. Cursor removed.**", "Some text\n**M-3. Cursor removed.**"):
            with self.subTest(body=body[:30]):
                self.assertFalse(self.has_item(body))

    def test_a_heading_or_a_list_that_interrupts_a_paragraph_counts(self):
        """T739: batch G's deliberate false FAILs are gone: CommonMark renders these as a heading and a list."""
        for body in ("Some text\n### M-3. Cursor removed", "x\n- a\n- **M-3. Cursor removed.**"):
            with self.subTest(body=body[:30]):
                self.assertTrue(self.has_item(body))

    def test_an_anchor_outside_an_html_block_still_counts(self):
        for body in (
            "<!-- note -->\n### M-3. Cursor removed",
            "- a\n- **M-3. Cursor removed.**",
            "1. a\n2. **M-3. Cursor removed.**",
            "### h\n**M-3. Cursor removed.**",
            "```\n<div>\n```\n### M-3. Cursor removed",
        ):
            with self.subTest(body=body[:40]):
                self.assertTrue(self.has_item(body))

    def test_a_block_whose_end_overlaps_its_start_closes_on_the_start_line(self):
        """SEC-T731-09(a): CommonMark searches the whole start line; the gate stayed open and hid too much."""
        for opener, end in (("<!-->", "-->"), ("<!--->", "-->"), ("<?>", "?>")):
            with self.subTest(opener=opener):
                self.assertFalse(self.has_item(f'{opener}\n<a title="\n{end}\n**M-3. Cursor removed.**\n">'))
                # SEC-T739-03: a raw block that is not a comment stops the search, even one that closes at once.
                self.assertIs(self.has_item(f"{opener}\n### M-3. Cursor removed"), opener != "<?>")

    def test_other_html_block_ends_are_unchanged_by_the_whole_line_search(self):
        for body in ("<!-- x\n### Cursor\n-->", "<!--\n### Cursor\n-->", "<?php\n### Cursor\n?>"):
            with self.subTest(spans_lines=body[:20]):
                self.assertFalse(self.has_item(body))
        for body in (
            "<!-- x\n-->\n### M-3. Cursor removed",
            "<!-- note -->\n### M-3. Cursor removed",
        ):
            with self.subTest(closes=body[:20]):
                self.assertTrue(self.has_item(body))
        for body in (  # SEC-T739-03: these close too, and they are not comments, so nothing after them counts
            "<?php x ?>\n### M-3. Cursor removed",
            "<pre>code</pre>\n### M-3. Cursor removed",
            "<![CDATA[x]]>\n### M-3. Cursor removed",
            "<!DOCTYPE x>\n### M-3. Cursor removed",
        ):
            with self.subTest(raw=body[:20]):
                self.assertFalse(self.has_item(body))

    def test_a_non_blank_start_line_does_not_end_a_block_of_type_6_or_7(self):
        for line in ("<div>", "  <div>  ", "</div>", "<span>", "<custom-tag data-x='1'/>"):
            with self.subTest(line=line):
                self.assertFalse(self.has_item(f"{line}\n### M-3. Cursor removed"))

    def test_the_former_false_passes_are_refused(self):
        """CommonMark hides each anchor, and the hand-written rules counted it (T739 flipped these asserts)."""
        for name, body in (
            ("SEC-T731-09(b), fence", "- a\n  ```\nx\n  ```\n**M-3. Cursor removed.**"),
            ("SEC-T731-09(b), no fence", "- a\n  <!--\nx\n<? -->\n\n**M-3. Cursor removed.**\n?>"),
            ("SEC-T738-01, fence", "Some text\n<span>\n```\n\n**M-3. Cursor removed.**\n```"),
            ("SEC-T738-01, <?", "Some text\n<span>\n<?\n\n**M-3. Cursor removed.**\n?>"),
        ):
            with self.subTest(name):
                self.assertFalse(self.has_item(body))

    def test_only_commonmark_line_ends_end_a_line(self):
        """SEC-T731-02: str.splitlines() also split at these, which ended the block or made a line start."""
        for char in ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"):
            with self.subTest(char=hex(ord(char))):
                body = f"<details>\n{char}\n**Migration Guide item M-3. Cursor removed.**\n</details>"
                self.assertFalse(self.has_item(body))
                self.assertFalse(self.has_item(f"Some text{char}**Migration Guide item M-3. Cursor removed.**"))
        for end in ("\n", "\r\n", "\r"):
            with self.subTest(end=repr(end)):
                self.assertTrue(self.has_item(f"Some text{end}{end}**M-3. Cursor removed.**"))
                self.assertFalse(self.has_item(f"Some text{end}**M-3. Cursor removed.**"))
                self.assertTrue(self.has_item(f"<!-- x{end}-->{end}### M-3. Cursor removed"))
                self.assertFalse(self.has_item(f"<!-- x{end}### M-3. Cursor removed{end}-->"))

    def test_a_long_tag_line_does_not_slow_the_gate(self):
        import time
        start = time.monotonic()
        lines = ("<a" + " " * 60000 + "!", "<a" + " b=c" * 16000 + " !", "<a" + " b" * 30000 + "!",
                 "<a" + ' x="y"' * 10900 + "!")
        for line in lines:
            self.assertLessEqual(len(line), self.mod.MAX_LINE_CHARS)  # past the limit nothing is parsed (TD-T739-01)
            self.assertFalse(self.has_item(line))
        # Catches a hang, not a slow runner: this took 1.23 s under load in CI (pipeline 3031259271), about 0.2 s locally.
        self.assertLess(time.monotonic() - start, 5.0)

    def test_the_v9_document_keeps_its_cursor_item(self):
        text = (repo_root() / "docs" / "releases" / "v9.0.0.md").read_text(encoding="utf-8")
        self.assertTrue(self.mod.has_cursor_migration_item(text))


def _section(body: str) -> str:
    return f"# Release v9.0.0\n\n## Migration Guide\n\n{body}\n"


class ParserAnchorTests(unittest.TestCase):
    """T739 (plan-136): what the parser gives for each listed shape, on the section and on the anchor."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def setUp(self):
        require_parser(self)

    def _assert_all(self, wanted: bool, documents: dict[str, str]) -> None:
        for name, document in documents.items():
            with self.subTest(name):
                self.assertIs(self.mod.has_cursor_migration_item(document), wanted)

    def test_the_section_ends_at_the_next_top_level_heading_of_any_form(self):
        """SEC-T731-08, SEC-T738-03: the anchor is visible, in the wrong section."""
        self._assert_all(False, {
            "setext h2": _section("Next\n---\n\n### M-3. Cursor removed"),
            "setext h1": _section("Next\n===\n\n### M-3. Cursor removed"),
            "indented ATX": _section(" ## Next\n\n### M-3. Cursor removed"),
            "tab after the marks": _section("##\tNext\n\n### M-3. Cursor removed"),
            "level 1": _section("# Next\n\n### M-3. Cursor removed"),
            "x <!--> then a section": _section("x <!-->\n## Other\n-->\n\n### M-3. Cursor removed"),
            "x <!-- then a section": _section("x <!--\n## Other\n-->\n\n### M-3. Cursor removed"),
            "x <!---> then a section": _section("x <!--->\n## Other\n-->\n\n### M-3. Cursor removed"),
            "x <!--> then a section, lead": _section("x <!-->\n## Other\n-->\n\n**M-3. Cursor removed.**"),
            "x <!-- then a section, lead": _section("x <!--\n## Other\n-->\n\n**M-3. Cursor removed.**"),
        })

    def test_a_nested_heading_neither_opens_nor_ends_the_section(self):
        self._assert_all(True, {
            "in a blockquote": _section("> ## Next\n\n### M-3. Cursor removed"),
            "in a list": _section("- ## Next\n\n### M-3. Cursor removed"),
            "in a fence": _section("```\n## Next\n```\n\n### M-3. Cursor removed"),
            "in a comment": _section("<!--\n## Next\n-->\n\n### M-3. Cursor removed"),
            "level 3": _section("### Next\n\n### M-3. Cursor removed"),
        })
        self._assert_all(False, {
            "open in a blockquote": "> ## Migration Guide\n\n### M-3. Cursor removed\n",
            "open in a list": "- ## Migration Guide\n\n### M-3. Cursor removed\n",
            "open in a fence": "```\n## Migration Guide\n```\n\n### M-3. Cursor removed\n",
        })

    def test_only_the_first_exact_level_two_heading_is_the_section(self):
        self._assert_all(True, {
            "setext": "Migration Guide\n---\n\n### M-3. Cursor removed\n",
            "closing marks": "## Migration Guide ##\n\n### M-3. Cursor removed\n",
            "inline comment": "## Migration Guide <!-- x -->\n\n### M-3. Cursor removed\n",
            "a later section after the anchor": _section("### M-3. Cursor removed\n\n## Next\n\nText."),
        })
        self._assert_all(False, {
            "a second section": "## Migration Guide\n\nNone.\n\n## Migration Guide\n\n### M-3. Cursor removed\n",
            "level 1": "# Migration Guide\n\n### M-3. Cursor removed\n",
            "level 3": "### Migration Guide\n\n### M-3. Cursor removed\n",
            "more text": "## Migration Guide notes\n\n### M-3. Cursor removed\n",
            "another case": "## migration guide\n\n### M-3. Cursor removed\n",
            "image alt": "## ![Migration Guide](u)\n\n### M-3. Cursor removed\n",
            "before the section": "### M-3. Cursor removed\n\n## Migration Guide\n\nNone.\n",
            "no section": "### M-3. Cursor removed\n",
        })

    def test_an_anchor_is_a_top_level_heading_or_a_lead_with_only_list_containers(self):
        self._assert_all(True, {
            "heading": _section("### M-3. Cursor removed"),
            "level 6": _section("###### M-3. Cursor removed"),
            "lead": _section("**M-3. Cursor removed.**"),
            "lead and more": _section("**M-3. Cursor removed.** Do this."),
            "bullet": _section("- **M-3. Cursor removed.**"),
            "tight list, second item": _section("- a\n- **M-3. Cursor removed.**"),
            "ordered": _section("1. **M-3. Cursor removed.**"),
            "nested lists": _section("- a\n  1. **M-3. Cursor removed.**"),
            "second paragraph of an item": _section("- a\n\n  **M-3. Cursor removed.**"),
        })
        self._assert_all(False, {
            "blockquote lead": _section("> **M-3. Cursor removed.**"),
            "blockquote heading": _section("> ### M-3. Cursor removed"),
            "list in a blockquote": _section("> - **M-3. Cursor removed.**"),
            "blockquote in a list": _section("- > **M-3. Cursor removed.**"),
            "heading in a list": _section("- ### M-3. Cursor removed"),
            "__bold__": _section("__M-3. Cursor removed.__"),
            "*em*": _section("*M-3. Cursor removed.*"),
            "plain": _section("Cursor removed."),
            "another case": _section("### M-3. cursor removed"),
            "part of a word": _section("### M-3. Cursors removed"),
        })

    def test_only_the_text_inside_the_opening_span_counts(self):
        self._assert_all(True, {
            "nested em": _section("**M-3. *Cursor* removed.**"),
            "nested link": _section("**M-3. [Cursor](u) removed.**"),
            "nested code": _section("**M-3. `Cursor` removed.**"),
            "nested strong, name after it": _section("**a **b** Cursor**"),
            "soft break": _section("**M-3.\nCursor removed.**"),
            "hard break": _section("**M-3.  \nCursor removed.**"),
            "entity": _section("**&#67;ursor removed.**"),
        })
        self._assert_all(False, {
            "name after the span": _section("**M-3.** Cursor removed."),
            "name after a nested span": _section("**a **b** c** Cursor"),
            "span not first": _section("M-3. **Cursor removed.**"),
            "escaped": _section("\\*\\*Cursor removed.\\*\\*"),
            "entity space first": _section("&#32;**Cursor removed.**"),
            "unclosed": _section("**Cursor removed."),
            "an inline tag first": _section("<span></span>**Cursor removed.**"),
            "broken word": _section("**Curs\nor removed.**"),
        })

    def test_image_alt_text_and_inline_html_never_count(self):
        self._assert_all(False, {
            "alt in a lead": _section("**![Cursor](u)**"),
            "alt as a paragraph": _section("![**Cursor**](u)"),
            "alt in a heading": _section("### ![Cursor](u)"),
            "comment in a lead": _section("**M-3 <!-- Cursor -->**"),
            "comment in a heading": _section("### M-3 <!-- Cursor -->"),
            "attribute in a heading": _section('### <span title="Cursor">x</span>'),
        })
        self.assertTrue(self.mod.has_cursor_migration_item(_section("### ![x](u) Cursor <!-- y -->")))

    def test_a_real_anchor_after_a_block_that_closes_on_its_start_line_counts(self):
        """The review's <!--> and <?> shapes (SEC-T731-09(a)): the true results stay, and the hidden one stays hidden."""
        self._assert_all(True, {
            "<!-->": _section("<!-->\n### M-3. Cursor removed"),
            "<!--> and a lead": _section("<!-->\n\n**M-3. Cursor removed.**"),
            "SEC-T738-03's false FAIL": _section("x <!-->\n\n### M-3. Cursor removed\n\n-->"),
            "the same with <!--->": _section("x <!--->\n\n### M-3. Cursor removed\n\n-->"),
            "the same in a list item": _section("- x <!-->\n\n### M-3. Cursor removed\n\n-->"),
            "the same in a blockquote": _section("> x <!-->\n\n### M-3. Cursor removed\n\n-->"),
        })
        self._assert_all(False, {
            "<!-->, hidden": _section('<!-->\n<a title="\n-->\n**M-3. Cursor removed.**\n">'),
            "<?>, hidden": _section('<?>\n<a title="\n?>\n**M-3. Cursor removed.**\n">'),
            "<?>, SEC-T739-03": _section("<?>\n### M-3. Cursor removed"),
            "<?> and a lead, SEC-T739-03": _section("<?>\n\n**M-3. Cursor removed.**"),
        })

    def test_an_anchor_holding_inline_html_does_not_count(self):
        """SEC-T739-02. Both sides of the word, and a tag inside a link, which is in the same flat token list."""
        self._assert_all(False, {
            "the finding, a lead": _section("**<span hidden>Cursor</span>**"),
            "the finding, a heading": _section('### <span style="display:none">Cursor</span>'),
            "in a list": _section("- **<span hidden>Cursor</span>**"),
            "tag after the word": _section("**Cursor <span hidden>x</span>**"),
            "tag before the word": _section("**<span hidden>x</span> Cursor**"),
            "a closing tag": _section("### Cursor </span>"),
            "opened inside, closed outside": _section("**<span hidden>Cursor**</span>"),
            "in a link": _section("**[<span hidden>Cursor</span>](u)**"),
            "nested strong": _section("**a **<b>**b** Cursor**"),
            "a void tag": _section("**<br>Cursor**"),
            "a processing instruction": _section("**<?x y?> Cursor**"),
            "a declaration": _section("**<!X y> Cursor**"),
            "a CDATA section": _section("**<![CDATA[x]]> Cursor**"),
            "a comment an HTML parser ends early": _section("**Cursor <!-- x --!> <b> y -->**"),
        })

    def test_what_is_not_inline_html_stays_allowed(self):
        self._assert_all(True, {
            "a comment before the word": _section("**<!-- x --> Cursor**"),
            "a comment in a heading": _section("### Cursor <!-- y -->"),
            "a code span in a lead": _section("**`<span hidden>` Cursor**"),
            "a code span in a heading": _section("### `<br>` Cursor"),
            "a code span holding the word": _section("**`Cursor`**"),
            "alt text with a tag": _section("**![<span>x</span>](u) Cursor**"),
            "alt text with a tag, heading": _section("### ![<b>x</b>](u) Cursor"),
            "a link": _section("**[Cursor](u)**"),
            "a link title with a tag": _section('**[x](u "<span hidden>") Cursor**'),
            "an autolink": _section("**<https://example.com> Cursor**"),
            "an escaped tag": _section("**\\<span hidden> Cursor**"),
            "an entity": _section("**&lt;span hidden&gt; Cursor**"),
            "a tag after the span": _section("**Cursor** <span>x</span>"),
        })

    def test_an_anchor_after_a_raw_html_block_does_not_count(self):
        """SEC-T739-03, fail closed: no tag balancing, so a block that closes itself stops the search as well."""
        self._assert_all(False, {
            "the finding": _section("<div hidden>\n\n### M-3. Cursor removed"),
            "details": _section("<details>\n\n**M-3. Cursor removed.**"),
            "closed": _section("<details>\n<summary>x</summary>\n</details>\n\n**M-3. Cursor removed.**"),
            "a closing tag": _section("</details>\n\n### M-3. Cursor removed"),
            "a comment first": _section("<!-- x -->\n<div hidden>\n\n### M-3. Cursor removed"),
            "a tag after a comment": _section("<!-- x --> <div hidden>\n\n### M-3. Cursor removed"),
            "a tag after the short comment": _section("<!--> <div hidden>\n\n### M-3. Cursor removed"),
            "a tag in a short comment": _section("<!--><div hidden>-->\n\n### M-3. Cursor removed"),
            "a tag after --!>": _section("<!-- x --!> <div hidden> -->\n\n### M-3. Cursor removed"),
            "in a blockquote": _section("> <div hidden>\n\n### M-3. Cursor removed"),
            "in a list": _section("- <div hidden>\n\n**M-3. Cursor removed.**"),
        })

    def test_a_comment_or_code_or_a_later_block_does_not_trip_the_raw_block_rule(self):
        self._assert_all(True, {
            "a comment": _section("<!-- x -->\n\n### M-3. Cursor removed"),
            "over lines": _section("<!-- x\ny\n-->\n\n**M-3. Cursor removed.**"),
            "two on a line": _section("<!-- a --><!-- b -->\n\n### M-3. Cursor removed"),
            "empty": _section("<!---->\n\n### M-3. Cursor removed"),
            "short": _section("<!-->\n\n### M-3. Cursor removed"),
            "short, a dash more": _section("<!--->\n\n### M-3. Cursor removed"),
            "a block after the anchor": _section("### M-3. Cursor removed\n\n<div hidden>"),
            "in a fence": _section("```\n<div hidden>\n```\n\n### M-3. Cursor removed"),
            "indented code": _section("    <div hidden>\n\n### M-3. Cursor removed"),
            "a code span": _section("`<div hidden>`\n\n### M-3. Cursor removed"),
        })

    def test_holds_only_comments(self):
        for html in ("", " \n", "<!-- x -->", "<!---->", "<!-->", "<!--->", "<!-- a --> <!-- b -->\n", "<!-- <!-- -->"):
            with self.subTest(html):
                self.assertTrue(self.mod.holds_only_comments(html))
        for html in ("<b>", "x", "<!-- x", "<!-- x --> y", "y <!-- x -->", "<!-- x --!>", "<!-- x --!> y -->",
                     "<!-->x-->", "<!--->x-->", "<!-- x --><b>", "<?x?>", "<!X y>", "<![CDATA[x]]>"):
            with self.subTest(html):
                self.assertFalse(self.mod.holds_only_comments(html))

    def test_a_long_comment_does_not_slow_the_check(self):
        import time
        start = time.monotonic()
        self.assertTrue(self.mod.holds_only_comments("<!--" + "-" * 65000 + " -->"))
        self.assertFalse(self.mod.holds_only_comments("<!--" + "- " * 32000))
        self.assertFalse(self.mod.holds_only_comments("<!-- -->" * 8000 + "<b>"))
        self.assertLess(time.monotonic() - start, 5.0)  # catches a hang, not a slow runner

    def test_live_html_anywhere_before_the_anchor_ends_the_search(self):
        """The orchestrator's ruling on T743: one rule from the start of the document, not a list of dangerous places."""
        anchor = "### M-3. Cursor removed"
        self._assert_all(False, {
            "a paragraph in the section": _section(f"text <div hidden>\n\n{anchor}"),
            "a raw block above the section": f"<div hidden>\n\n{_section(anchor)}",
            "the section's own title": f"# R\n\n## <span hidden>Migration Guide</span>\n\n{anchor}\n",
            "a tag after the title": f"# R\n\n## Migration Guide <span>x</span>\n\n{anchor}\n",
            "a paragraph above the section": f"text <div hidden>\n\n{_section(anchor)}",
            "a list item above the section": f"- text <div hidden>\n\n{_section(anchor)}",
            "a blockquote above the section": f"> text <div hidden>\n\n{_section(anchor)}",
            "a raw block in a list above": f"- <div hidden>\n\n{_section(anchor)}",
            "the level 1 heading above": f"# <b>R</b>\n\n## Migration Guide\n\n{anchor}\n",
            "a level 2 heading above": f"# R\n\n## <b>Other</b>\n\n## Migration Guide\n\n{anchor}\n",
            "a level 3 heading above": f"### <b>x</b>\n\n{_section(anchor)}",
            "a list item in the section": _section(f"- text <b>x</b>\n\n{anchor}"),
            "a blockquote in the section": _section(f"> text <b>x</b>\n\n{anchor}"),
            "a closed tag in the section": _section(f"Text with <span>inline</span> HTML.\n\n{anchor}"),
            "before a lead": _section("text <b>x</b>\n\n**M-3. Cursor removed.**"),
        })

    def test_html_after_the_anchor_or_only_comments_or_not_html_stays_true(self):
        anchor = "### M-3. Cursor removed"
        self._assert_all(True, {
            "a block after": _section(f"{anchor}\n\n<div hidden>"),
            "inline after": _section(f"{anchor}\n\ntext <div hidden>"),
            "in the lead's paragraph, after its span": _section("**M-3. Cursor removed.** <div hidden>"),
            "after the section": f"{_section(anchor)}\n## Other\n\n<div hidden>\n",
            "a comment in the title": f"# R\n\n## Migration Guide <!-- x -->\n\n{anchor}\n",
            "a comment block above": f"<!-- x -->\n\n{_section(anchor)}",
            "a comment inline above": f"text <!-- x -->\n\n{_section(anchor)}",
            "a comment inline in a list above": f"- text <!-- x -->\n\n{_section(anchor)}",
            "a code span above": f"`<div hidden>`\n\n{_section(anchor)}",
            "a fence above": f"```\n<div hidden>\n```\n\n{_section(anchor)}",
            "alt text above": f"![<div hidden>](u)\n\n{_section(anchor)}",
            "an autolink above": f"<https://example.com>\n\n{_section(anchor)}",
        })

    def test_an_anchor_above_the_section_does_not_count(self):
        """Control: the walk starts at the document's start, and an anchor only counts inside the section."""
        self.assertFalse(self.mod.has_cursor_migration_item("### M-3. Cursor removed\n\n" + _section("No item.")))
        self.assertFalse(self.mod.has_cursor_migration_item("**M-3. Cursor removed.**\n\n" + _section("No item.")))
        self.assertFalse(self.mod.has_cursor_migration_item("# R\n\nNo section, **Cursor**.\n\n### Cursor\n"))

    def test_nesting_past_the_limit_fails_closed(self):
        """SEC-T739-09. The word '20' in --help is this limit; a parser release that changes it fails here."""
        self.assertEqual(self.mod.MarkdownIt("commonmark").options.maxNesting, 20)
        self._assert_all(False, {"a lead": _section("- " * 25 + "**M-3. Cursor removed.**"),
                                 "a heading": _section("- " * 25 + "### M-3. Cursor removed"),
                                 "a blockquote": _section("> " * 25 + "**M-3. Cursor removed.**")})
        self.assertTrue(self.mod.has_cursor_migration_item(_section("- " * 9 + "**M-3. Cursor removed.**")))
        self.assertFalse(self.mod.has_cursor_migration_item(_section("- " * 10 + "**M-3. Cursor removed.**")))
        # The parser skips the rest of the document there, so an anchor after it is gone too. A nest above the limit
        # fails closed; one below it hides nothing.
        self.assertTrue(self.mod.has_cursor_migration_item(_section("- " * 9 + "x\n\n### M-3. Cursor removed")))
        self.assertFalse(self.mod.has_cursor_migration_item(_section("- " * 10 + "x\n\n### M-3. Cursor removed")))

    def test_an_anchor_in_a_reference_definition_title_does_not_count(self):
        """SEC-T739-09: a definition renders nothing."""
        self._assert_all(False, {"a lead": _section('[x]: /u "**Cursor**"'), "a heading": _section('[x]: /u "### Cursor"'),
                                 "on the next line": _section('[x]: /u\n"**Cursor**"')})

    def test_lazy_continuation(self):
        """SEC-T739-09: a lazy line joins the paragraph above it, so it opens nothing, and a span may run through it."""
        self._assert_all(False, {"a blockquote": _section("> text\n**M-3. Cursor removed.**"),
                                 "a list item": _section("- text\n**M-3. Cursor removed.**"),
                                 "a span lazily out of a blockquote": _section("> **M-3.\nCursor removed.**")})
        self.assertTrue(self.mod.has_cursor_migration_item(_section("- **M-3.\nCursor removed.**")))

    def test_the_real_v9_document(self):
        text = (repo_root() / "docs" / "releases" / "v9.0.0.md").read_text(encoding="utf-8")
        self.assertTrue(self.mod.has_cursor_migration_item(text))


class ParserMissingTests(unittest.TestCase):
    """T739: without the parser the gate exits 1 with one clear error, on every run. There is no fallback and no skip."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def _main_without_parser(self, root: Path) -> tuple[int, str]:
        out = io.StringIO()
        with mock.patch.object(self.mod, "MarkdownIt", None), mock.patch.object(self.mod, "ROOT", root), \
                mock.patch.object(sys, "argv", ["verify-release-docs.py", "--tag", "v9.0.0"]), \
                contextlib.redirect_stdout(out):
            return self.mod.main(), out.getvalue()

    def _assert_only_the_parser_error(self, code: int, output: str) -> None:
        self.assertEqual(code, 1, output)
        self.assertEqual(_error_lines(output), [f"release-docs-verify: {self.mod.PARSER_MISSING}"])
        self.assertIn("markdown-it-py", output)
        self.assertIn(self.mod.PARSER_INSTALL_COMMAND, output)
        self.assertNotIn("Traceback", output)

    def test_a_tree_with_no_cursor_pointer_still_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "install.sh").write_text("#!/bin/sh\necho hello\n", encoding="utf-8")
            self._assert_only_the_parser_error(*self._main_without_parser(root))

    def test_a_tree_with_a_cursor_pointer_fails_the_same_way(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "install.sh").write_text(INSTALL_SH, encoding="utf-8")
            self._assert_only_the_parser_error(*self._main_without_parser(root))

    def test_this_tree_fails_the_same_way(self):
        self._assert_only_the_parser_error(*self._main_without_parser(repo_root()))

    def test_a_real_process_without_the_module_exits_1_with_no_traceback(self):
        """The import itself fails here (sys.modules[name] = None), so this also proves the guarded import."""
        code = (
            "import runpy, sys\n"
            "sys.modules['markdown_it'] = None\n"
            "sys.argv = ['verify-release-docs.py', '--tag', 'v9.0.0']\n"
            f"runpy.run_path({str(repo_root() / 'scripts' / 'verify-release-docs.py')!r}, run_name='__main__')\n"
        )
        run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertNotIn("Traceback", run.stdout + run.stderr)
        self.assertEqual(_error_lines(run.stdout), [f"release-docs-verify: {self.mod.PARSER_MISSING}"])

    def test_the_help_still_prints_without_the_module(self):
        code = (
            "import runpy, sys\n"
            "sys.modules['markdown_it'] = None\n"
            "sys.argv = ['verify-release-docs.py', '--help']\n"
            f"runpy.run_path({str(repo_root() / 'scripts' / 'verify-release-docs.py')!r}, run_name='__main__')\n"
        )
        run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("markdown-it-py", run.stdout)


class HelpTextTests(unittest.TestCase):
    """T739 (SEC-T738-04): --help describes the parser, drops the blank-line rule and says what stays open."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def _collapsed_help(self) -> str:
        return " ".join(self.mod.MIGRATION_POINTER_HELP.split())

    def test_the_help_states_what_stays_open(self):
        text = self._collapsed_help()
        for phrase in ("markdown-it-py", "GitLab's renderer may differ", "(unverified, SEC-T716-03)",
                       "What stays open.", "do not defend against a crafted script",
                       "they catch an omission on one line"):
            with self.subTest(phrase):
                self.assertIn(phrase, text)

    def test_the_help_states_each_rule_of_batch_s(self):
        text = self._collapsed_help()
        for phrase in (
            "(SEC-T739-02, SEC-T739-03)", "the gate does not balance tags, so it refuses rather than models",
            "from its start", "that is not only comments", "'<details>'", "'text <div hidden>'",
            "above the section, in its title or in the section", "at any depth", "even if the tag closes itself",
            "An anchor above it still counts", "HTML after an anchor does not matter",
            "An anchor that holds a tag does not count", "A comment is allowed",
            "a tag in a code span is code, not HTML", "an image's alt text",
            "(SEC-T739-09)", "20 nested levels (maxNesting)", "a list item counts as two",
            "skips the rest of the document", "the gate fails closed",
            "(SEC-T739-04)", "'---', '+++' or ';;;'", "front matter", "in the Release description too (unverified)",
            "(TD-T739-01)", "longer than 65536 characters", "no content", "before any parsing",
            "(SEC-T738-02)", "must hold no CR, CRLF included", "names the line",
            "(SEC-T741-07)", "checked for existence only", "the gate does not read it",
        ):
            with self.subTest(phrase):
                self.assertIn(phrase, text)

    def test_the_limit_in_the_help_is_the_limit_in_the_code(self):
        self.assertIn(f"longer than {self.mod.MAX_LINE_CHARS} characters", self._collapsed_help())

    def test_the_old_claims_are_gone(self):
        text = self._collapsed_help()
        for phrase in ("are ignored", "the line before it is blank", "at the start of a line", "up to the next '## '",
                       "(SEC-T738-04)", "counts because CommonMark parses it as live", "inline HTML never count",
                       "are not modelled", "Raw HTML above the section", "inline HTML in an earlier paragraph"):
            with self.subTest(phrase):
                self.assertNotIn(phrase, text)


class LineBreakCharacterTests(_MainRunner):
    """T731 (SEC-T731-02 follow-up), T738 (SEC-T731-07): a checked file holding one of these line separators fails."""

    CHARS = ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")

    def _errors(self, relative: str, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_text(text, encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_line_breaks(
                    [*self.mod.MARKER_FILES, Path("docs/releases/v9.0.0.md"), self.mod.INSTALL_SH], errors
                )
            return errors

    def _main_on_crafted_tree(self, install: str) -> tuple[int, str]:
        """main() in its real call order: this tree's required files, ``install``, and a v9.0.0 document with no Cursor item.

        The links, the markers and the version consistency check are patched out; they read the rest of the tree.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in self.mod.REQUIRED_FILES:
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_bytes((repo_root() / relative).read_bytes())
            (root / self.mod.INSTALL_SH).write_text(install, encoding="utf-8", newline="")
            (root / "docs/releases/v9.0.0.md").write_text(
                f"Latest release: v9.0.0\n\n## Install\n\n## Highlights\n\n## Migration Guide\n\nNo item.\n\n{GOOD}",
                encoding="utf-8",
            )
            with mock.patch.object(self.mod, "ROOT", root), mock.patch.object(self.mod, "check_links"), \
                    mock.patch.object(self.mod, "check_markers"):
                return self._run_main("v9.0.0")

    def test_each_character_in_the_release_document_fails(self):
        for char in self.CHARS:
            with self.subTest(char=hex(ord(char))):
                text = f"# R\r\n\n## RELEASE VERDICT\r- **Status**: PASS{char}- **Status**: pending\n{char}\n"
                errors = self._errors("docs/releases/v9.0.0.md", text)
                self.assertEqual(errors, [
                    f"docs/releases/v9.0.0.md:4 holds U+{ord(char):04X}, which str.splitlines() treats as a line end "
                    "and neither Markdown nor a shell does; remove it (SEC-T731-02, SEC-T731-07)"
                ])
                self.assertNotIn(char, errors[0])

    def test_a_marker_file_with_the_character_fails(self):
        errors = self._errors("docs/wiki/home.md", "# Home\n\nLatest release: v9.0.0\u2028\n")
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith("docs/wiki/home.md:3 holds U+2028"), errors[0])

    def test_an_install_sh_with_the_character_fails(self):
        for char in self.CHARS:
            with self.subTest(char=hex(ord(char))):
                errors = self._errors("scripts/install.sh", f"#!/bin/sh\necho 'a{char}b'\n")
                self.assertEqual(len(errors), 1, errors)
                self.assertTrue(errors[0].startswith(f"scripts/install.sh:2 holds U+{ord(char):04X}, "), errors[0])
                self.assertIn("a shell", errors[0])
                self.assertNotIn(char, errors[0])

    def test_main_refuses_a_pointer_split_from_cursor_in_install_sh(self):
        """SEC-T731-07: the split pointer passes check_migration_pointers, so check_line_breaks must refuse it."""
        for char in self.CHARS:
            with self.subTest(char=hex(ord(char))):
                code, output = self._main_on_crafted_tree(f"#!/bin/sh\necho 'docs/releases/v9.0.0.md{char}Cursor'\n")
                self.assertEqual(code, 1, output)
                self.assertNotIn("lacks its Cursor migration item", output)
                self.assertIn(f"scripts/install.sh:2 holds U+{ord(char):04X}, ", output)
                self.assertNotIn(char, output)

    def test_the_crafted_tree_fails_only_for_the_reason_under_test(self):
        """Controls for the test above: the same pointer on one plain line needs the item; without Cursor it passes."""
        code, output = self._main_on_crafted_tree("#!/bin/sh\necho 'docs/releases/v9.0.0.md Cursor'\n")
        self.assertEqual(code, 1, output)
        self.assertIn("docs/releases/v9.0.0.md lacks its Cursor migration item", output)
        code, output = self._main_on_crafted_tree("#!/bin/sh\necho 'docs/releases/v9.0.0.md'\n")
        self.assertEqual(code, 0, output)

    def test_the_install_sh_of_this_tree_holds_none(self):
        errors: list[str] = []
        self.mod.check_line_breaks([self.mod.INSTALL_SH], errors)
        self.assertEqual(errors, [])

    def test_clean_documents_pass(self):
        self.assertEqual(self._errors("README.md", "# R\r\n\tok\n"), [])
        errors: list[str] = []
        self.mod.check_line_breaks([*self.mod.MARKER_FILES, Path("docs/releases/v9.0.0.md")], errors)
        self.assertEqual(errors, [])

    def test_main_checks_the_release_document_the_marker_files_and_install_sh(self):
        with mock.patch.object(self.mod, "check_line_breaks") as check:
            code, output = _run_past_release_without_markers(self, "v8.0.0")
        self.assertEqual(code, 0, output)
        check.assert_called_once()
        self.assertEqual(
            check.call_args.args[0], [*self.mod.MARKER_FILES, Path("docs/releases/v8.0.0.md"), self.mod.INSTALL_SH]
        )


RELEASE_DOC = (
    b"Latest release: v9.0.0\n\n## Install\n\n## Highlights\n\n## Migration Guide\n\n### M-3. Cursor removed\n\n"
    + GOOD.encode("utf-8")
)
# SEC-T739-01: the invalid byte is dropped, so the comment closes on its first line and the anchor below it counts.
# A renderer that replaces the byte keeps the comment open down to the last line, and the anchor is hidden.
HIDDEN_ANCHOR_DOC = RELEASE_DOC.replace(
    b"### M-3. Cursor removed\n", b"<!-- x --\xff>\n\n### M-3. Cursor removed\n\n-->\n"
)


def _refusal(relative: object, offset: int) -> str:
    return (f"{relative} is not valid UTF-8: the first invalid byte is at file offset {offset} (from 0); "
            "the gate refuses this file, fix its encoding (SEC-T739-01)")


class StrictReadTests(_MainRunner):
    """T741 (SEC-T739-01): a file the gate reads that is not valid UTF-8 ends the run with exit 1, and that is all."""

    TAG = "v9.0.0"
    DOC = Path("docs/releases/v9.0.0.md")
    MARKER_LINE = b"\nLatest release: v9.0.0\n"

    def _tree(self, root: Path, overrides: dict[object, bytes]) -> None:
        """This tree's required files with a v9.0.0 marker, a Cursor pointer in install.sh, its document, overrides."""
        files: dict[object, bytes] = {
            relative: (repo_root() / relative).read_bytes() for relative in self.mod.REQUIRED_FILES
        }
        for relative in self.mod.MARKER_FILES:
            files[relative] += self.MARKER_LINE
        files[self.mod.INSTALL_SH] = b"#!/bin/sh\necho 'see the Cursor item in docs/releases/v9.0.0.md'\n"
        files[self.DOC] = RELEASE_DOC
        files.update(overrides)
        for relative, raw in files.items():
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_bytes(raw)

    def _main(self, overrides: dict[object, bytes]) -> tuple[int, str]:
        """main() on a crafted tree. Its links are patched out, because they point into the rest of this tree."""
        with tempfile.TemporaryDirectory() as tmp:
            self._tree(Path(tmp), overrides)
            with mock.patch.object(self.mod, "ROOT", Path(tmp)), mock.patch.object(self.mod, "check_links"):
                return self._run_main(self.TAG)

    def _assert_refused(self, overrides: dict[object, bytes], relative: object, offset: int) -> None:
        code, output = self._main(overrides)
        self.assertEqual(code, 1, output)
        self.assertEqual(_error_lines(output), [f"release-docs-verify: {_refusal(relative, offset)}"])
        self.assertNotIn("Traceback", output)

    def _spoiled(self, relative: object) -> tuple[bytes, int]:
        """The bytes of a required file that passes every check if the invalid byte is dropped, and that byte's offset."""
        raw = (repo_root() / relative).read_bytes() + self.MARKER_LINE
        return raw + b"\xff", len(raw)

    def test_the_crafted_tree_passes_without_an_invalid_byte(self):
        code, output = self._main({})
        self.assertEqual((code, _error_lines(output)[0]), (0, "release-docs-verify: all documentation checks passed"))

    def test_the_hidden_comment_shape_is_refused(self):
        offset = HIDDEN_ANCHOR_DOC.index(b"\xff")
        self._assert_refused({self.DOC: HIDDEN_ANCHOR_DOC}, self.DOC, offset)

    def test_the_hidden_comment_shape_is_the_finding(self):
        """Control: the two decodings of this fixture really do disagree on the anchor."""
        require_parser(self)
        self.assertTrue(self.mod.has_cursor_migration_item(HIDDEN_ANCHOR_DOC.decode("utf-8", "ignore")))
        self.assertFalse(self.mod.has_cursor_migration_item(HIDDEN_ANCHOR_DOC.decode("utf-8", "replace")))

    def test_invalid_bytes_in_install_sh_are_refused(self):
        raw = b"#!/bin/sh\necho 'see the Cursor item in docs/releases/v9.0.0.md'\n# \xff\n"
        self._assert_refused({self.mod.INSTALL_SH: raw}, self.mod.INSTALL_SH, raw.index(b"\xff"))

    def test_invalid_bytes_in_a_marker_file_are_refused(self):
        relative = Path("docs/wiki/home.md")
        raw, offset = self._spoiled(relative)
        self._assert_refused({relative: raw}, relative, offset)

    def test_invalid_bytes_in_a_document_install_sh_points_to_are_refused(self):
        older = Path("docs/releases/v8.0.0.md")
        raw = b"## Migration Guide\n\n### Cursor removed\n\xff\n"
        self._assert_refused(
            {self.mod.INSTALL_SH: f"echo 'the Cursor item in {older.as_posix()}'\n".encode(), older: raw},
            older, raw.index(b"\xff"),
        )

    def test_invalid_bytes_in_a_file_read_only_for_its_sections_are_refused(self):
        for relative in (Path("CONTRIBUTING.md"), Path("docs/wiki/quick-start.md"), Path("implementation/README.md")):
            with self.subTest(str(relative)):
                raw, offset = self._spoiled(relative)
                self._assert_refused({relative: raw}, relative, offset)

    def test_each_read_of_the_gate_refuses_on_its_own(self):
        """main() reads most files several times and the first read hides the others, so each call is taken alone."""
        template, section = Path("docs/releases/_template.md"), Path("implementation/README.md")
        home, install = Path("docs/wiki/home.md"), self.mod.INSTALL_SH
        reads = {
            "check_links": (template, lambda root, errors: self.mod.check_links(root / template, errors)),
            "check_markers": (home, lambda root, errors: self.mod.check_markers("Latest release: v9.0.0", errors)),
            "check_section_requirements": (section, lambda root, errors: self.mod.check_section_requirements(errors)),
            "check_line_breaks": (self.DOC, lambda root, errors: self.mod.check_line_breaks([self.DOC], errors)),
            "check_release_brief": (
                self.DOC, lambda root, errors: self.mod.check_release_brief(self.TAG, self.DOC, errors)
            ),
            "install.sh": (install, lambda root, errors: self.mod.check_migration_pointers(self.TAG, errors, False)),
            "pointed document": (
                self.DOC, lambda root, errors: self.mod.check_migration_pointers(self.TAG, errors, False)
            ),
        }
        for name, (relative, call) in reads.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                raw = b"Latest release: v9.0.0 \xff\n"
                self._tree(Path(tmp), {relative: raw})
                with mock.patch.object(self.mod, "ROOT", Path(tmp)), \
                        self.assertRaises(self.mod.NotUtf8Error) as refused:
                    call(Path(tmp), [])
                self.assertEqual(str(refused.exception), _refusal(relative, raw.index(b"\xff")))

    def test_the_offset_past_the_first_decoding_chunk_is_exact(self):
        """A byte offset in the file: the padding is two bytes a character, so a character count is off by half."""
        for size in (8192, 8193, 70000):
            with self.subTest(size):
                raw = RELEASE_DOC + "é".encode("utf-8") * (size // 2) + b"\xff tail\n"
                offset = len(RELEASE_DOC) + 2 * (size // 2)
                self.assertGreater(offset, 8192)
                self._assert_refused({self.DOC: raw}, self.DOC, offset)

    def test_the_first_invalid_byte_is_the_one_named(self):
        raw = RELEASE_DOC + b"\xff middle \xfe\n"
        self._assert_refused({self.DOC: raw}, self.DOC, len(RELEASE_DOC))

    def test_each_form_of_invalid_utf8_is_refused(self):
        forms = {"a bad lead byte": b"\xff", "an overlong form": b"\xc0\xaf", "a surrogate": b"\xed\xa0\x80",
                 "a stray continuation": b"\x80", "a sequence cut at the end of the file": b"\xe2\x82"}
        for name, bad in forms.items():
            with self.subTest(name):
                self._assert_refused({self.DOC: RELEASE_DOC + bad}, self.DOC, len(RELEASE_DOC))

    def test_the_error_holds_no_byte_of_the_content(self):
        raw = RELEASE_DOC + b"SECRET-BEFORE \xfe SECRET-AFTER\n"
        code, output = self._main({self.DOC: raw})
        self.assertEqual(code, 1, output)
        for piece in ("SECRET", "0xfe", "xfe", "�", "Install", "Highlights"):
            with self.subTest(piece):
                self.assertNotIn(piece, output)

    def test_no_later_check_runs_after_a_refusal(self):
        relative = Path("docs/wiki/README.md")
        raw, _ = self._spoiled(relative)
        with tempfile.TemporaryDirectory() as tmp:
            self._tree(Path(tmp), {relative: raw})
            with mock.patch.object(self.mod, "ROOT", Path(tmp)), \
                    mock.patch.object(self.mod, "check_line_breaks") as line_breaks, \
                    mock.patch.object(self.mod, "check_section_requirements") as sections, \
                    mock.patch.object(self.mod, "check_release_brief") as brief, \
                    mock.patch.object(self.mod, "check_links") as links, \
                    mock.patch.object(self.mod, "check_version_consistency") as version:
                with self.assertRaises(self.mod.NotUtf8Error):
                    self.mod.run_checks(self.TAG, False, [])
        for later in (line_breaks, sections, brief, links, version):
            later.assert_not_called()

    def test_errors_found_before_the_refusal_are_still_reported(self):
        home = Path("docs/wiki/home.md")
        raw = b"# no marker\n"
        spoiled = RELEASE_DOC + b"\xff"
        code, output = self._main({home: raw, self.mod.INSTALL_SH: b"#!/bin/sh\n", self.DOC: spoiled})
        self.assertEqual(code, 1, output)
        self.assertEqual(_error_lines(output), [
            f"release-docs-verify: missing marker 'Latest release: v9.0.0' in {home}",
            f"release-docs-verify: {_refusal(self.DOC, len(RELEASE_DOC))}",
        ])

    def test_a_real_process_exits_1_with_one_line_and_no_traceback(self):
        require_parser(self)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, {self.DOC: HIDDEN_ANCHOR_DOC})
            script = root / "scripts" / "verify-release-docs.py"
            script.write_bytes((repo_root() / "scripts" / "verify-release-docs.py").read_bytes())
            run = subprocess.run([sys.executable, str(script), "--tag", self.TAG], capture_output=True, text=True,
                                 timeout=60, check=False)
        self.assertEqual((run.returncode, run.stderr), (1, ""), run.stdout + run.stderr)
        offset = HIDDEN_ANCHOR_DOC.index(b"\xff")
        self.assertEqual(run.stdout.splitlines(), [f"release-docs-verify: {_refusal(self.DOC, offset)}"])

    def test_a_path_outside_the_root_is_shown_whole(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "install.sh"
            outside.write_bytes(b"\xff")
            with mock.patch.object(self.mod, "ROOT", Path(tmp)), self.assertRaises(self.mod.NotUtf8Error) as refused:
                self.mod.read_strict(outside)
        self.assertEqual(str(refused.exception), _refusal(outside, 0))

    def test_newlines_are_read_as_text_mode_reads_them(self):
        """Control: read_text without an errors argument, on CRLF, CR and mixed ends, one across the 8192 boundary."""
        samples = (b"a\r\nb\rc\nd", b"\r", b"\r\n", b"\n\r", b"\r\r\n\n", b"x" * 8191 + b"\r\ny", b"x" * 8192 + b"\ry",
                   b"\xef\xbb\xbfa\r\nb\r", "é\r\n\u2028\r".encode("utf-8"), b"")
        for raw in samples:
            with self.subTest(raw[:20]), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "f"
                path.write_bytes(raw)
                text = self.mod.read_strict(path)
                self.assertEqual(text, path.read_text(encoding="utf-8"))
                self.assertNotIn("\r", text)

    def test_a_tree_with_crlf_still_passes(self):
        """Control: only the invalid bytes are refused. A valid file with CRLF ends passes as it did."""
        crlf = {self.DOC: RELEASE_DOC.replace(b"\n", b"\r\n")}  # install.sh keeps LF: SEC-T738-02 refuses a CR in it
        for relative in self.mod.MARKER_FILES:
            raw = (repo_root() / relative).read_bytes() + self.MARKER_LINE
            crlf[relative] = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        code, output = self._main(crlf)
        self.assertEqual(code, 0, output)
        self.assertEqual(_error_lines(output)[0], "release-docs-verify: all documentation checks passed")

    def test_a_cr_in_install_sh_is_refused_and_names_the_line(self):
        """SEC-T738-02, flipped from test_a_cr_in_install_sh_still_splits_its_line: this shape used to exit 0."""
        document = RELEASE_DOC.replace(b"### M-3. Cursor removed\n", b"No item.\n")
        for name, install, line in (
            ("alone", b"#!/bin/sh\necho 'docs/releases/v9.0.0.md\rCursor'\n", 2),
            ("first line", b"\r#!/bin/sh\n", 1),
            ("CRLF", b"#!/bin/sh\r\necho 'the Cursor item in docs/releases/v9.0.0.md'\r\n", 1),
            ("last byte", b"#!/bin/sh\n\n\r", 3),
        ):
            with self.subTest(name):
                code, output = self._main({self.DOC: document, self.mod.INSTALL_SH: install})
                self.assertEqual(code, 1, output)
                self.assertEqual(_error_lines(output), [
                    f"release-docs-verify: {self.mod.INSTALL_SH}:{line} holds a CR (U+000D): a shell does not end a line "
                    "there, and the gate's per-line rules would, so a pointer could be split from the word 'Cursor'; "
                    "use LF line ends only (SEC-T738-02)"])
                self.assertNotIn("echo", output)

    def test_the_same_install_sh_without_the_cr_fails_for_the_missing_item(self):
        """Control for the test above: the crafted tree holds a real omission, which the CR used to hide."""
        document = RELEASE_DOC.replace(b"### M-3. Cursor removed\n", b"No item.\n")
        code, output = self._main({self.DOC: document, self.mod.INSTALL_SH: b"#!/bin/sh\necho 'docs/releases/v9.0.0.md Cursor'\n"})
        self.assertEqual(code, 1, output)
        self.assertIn("lacks its Cursor migration item", output)

    def test_invalid_bytes_are_named_before_a_cr(self):
        code, output = self._main({self.mod.INSTALL_SH: b"a\rb\xff\n"})
        self.assertEqual(code, 1, output)
        self.assertEqual(_error_lines(output), [f"release-docs-verify: {_refusal(self.mod.INSTALL_SH, 3)}"])

    def test_keep_cr_is_the_only_way_a_cr_comes_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "f"
            path.write_bytes(b"a\r\nb\rc\n")
            self.assertEqual(self.mod.read_strict(path), "a\nb\nc\n")
            self.assertEqual(self.mod.read_strict(path, keep_cr=True), "a\r\nb\rc\n")

    def test_the_install_sh_of_this_tree_holds_no_cr(self):
        self.assertNotIn(b"\r", (repo_root() / self.mod.INSTALL_SH).read_bytes())

    def test_every_file_the_gate_reads_on_this_tree_is_valid_utf8(self):
        reads = {*self.mod.REQUIRED_FILES, *map(Path, self.mod.install_sh_pointers(self.mod.read_strict(
            repo_root() / self.mod.INSTALL_SH)))}
        for relative in sorted(reads):
            with self.subTest(str(relative)):
                self.assertEqual(self.mod.read_strict(repo_root() / relative),
                                 (repo_root() / relative).read_text(encoding="utf-8"))

    def test_the_script_has_one_way_to_read_a_file(self):
        """SEC-T741-08: an AST walk, so a comment or a docstring cannot trip it and quote style cannot hide a call."""
        source = (repo_root() / "scripts" / "verify-release-docs.py").read_text(encoding="utf-8")
        self.assertEqual(_read_route_problems(source), [])

    def test_the_walk_catches_each_way_around_it(self):
        strict = 'def read_strict(path):\n    raw = path.read_bytes()\n    return raw.decode("utf-8")\n'
        self.assertEqual(_read_route_problems(strict), [])
        for name, snippet in {
            "open": 'def f(path):\n    return open(path, errors="replace").read()\n',
            "open, single quotes": "def f(path):\n    return open(path, errors='ignore').read()\n",
            "open, kept as a name": "reader = open\n",
            "a method named open": "def f(path):\n    return path.open().read()\n",
            "read_text": "def f(path):\n    return path.read_text()\n",
            "read_text, kept as a name": "def f(path):\n    reader = path.read_text\n",
            "read_bytes elsewhere": "def f(path):\n    return path.read_bytes()\n",
            "decode elsewhere": 'def f(raw):\n    return raw.decode("utf-8", "ignore")\n',
            "decode at module level": 'value = b"x".decode("utf-8", "ignore")\n',
            "an errors keyword anywhere": 'def f(raw):\n    return str(raw, errors="ignore")\n',
            "import io": "import io\n",
            "from codecs": "from codecs import open as o\n",
            "getattr": 'def f(path):\n    return getattr(path, "read_text")()\n',
        }.items():
            with self.subTest(name):
                self.assertNotEqual(_read_route_problems(strict + snippet), [])
        for name, body in {
            "lenient decode in read_strict": 'raw = path.read_bytes()\n    return raw.decode("utf-8", "ignore")\n',
            "a keyword in read_strict": 'raw = path.read_bytes()\n    return raw.decode("utf-8", errors="replace")\n',
            "two reads in read_strict": 'raw = path.read_bytes()\n    path.read_bytes()\n    return raw.decode("utf-8")\n',
            "no read in read_strict": 'return path.decode("utf-8")\n',
        }.items():
            with self.subTest(name):
                self.assertNotEqual(_read_route_problems(f"def read_strict(path):\n    {body}"), [])

    def test_a_comment_or_a_string_does_not_trip_the_walk(self):
        source = ('def read_strict(path):\n    """path.read_text() and open(path)."""\n'
                  '    raw = path.read_bytes()  # open(path, errors="ignore")\n    return raw.decode("utf-8")\n')
        self.assertEqual(_read_route_problems(source), [])

    def test_the_parser_has_one_call_site(self):
        """TD-T739-01: no route to the parser goes round the long line check."""
        tree = ast.parse((repo_root() / "scripts" / "verify-release-docs.py").read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == "MarkdownIt"]
        self.assertEqual(len(calls), 1)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and any(call in ast.walk(node) for call in calls):
                self.assertEqual(node.name, "markdown_tokens")

    def test_the_only_call_of_the_parser_sits_behind_the_long_line_check(self):
        tree = ast.parse((repo_root() / "scripts" / "verify-release-docs.py").read_text(encoding="utf-8"))
        helper = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "markdown_tokens")
        guard = next(node for node in helper.body if isinstance(node, ast.If))
        self.assertIn("long_line_number", ast.dump(guard.test))
        self.assertTrue(any(isinstance(node, ast.Return) for node in guard.body))
        self.assertNotIn("MarkdownIt", ast.dump(guard))

    def test_the_help_and_the_docstring_say_so(self):
        for name, text in (("--help", self.mod.MIGRATION_POINTER_HELP), ("docstring", self.mod.__doc__)):
            collapsed = " ".join(text.split())
            for phrase in ("(SEC-T739-01)", "reads in this process must be valid UTF-8", "exits 1",
                           "file offset of the first invalid byte", "never its content", "CRLF and CR become LF",
                           "scripts/check-version-consistency.py", "does not cover them"):
                with self.subTest(name=name, phrase=phrase):
                    self.assertIn(phrase, collapsed)


class DocumentRefusalTests(_MainRunner):
    """SEC-T739-04 (front matter) and TD-T739-01 (a long line): the document is refused, by path, on both routes."""

    TAG = "v9.0.0"
    DOC = Path("docs/releases/v9.0.0.md")
    INSTALL = "#!/bin/sh\necho 'see the Cursor item in docs/releases/v9.0.0.md'\n"
    GOOD_DOC = "# Release v9.0.0\n\n## Migration Guide\n\n### M-3. Cursor removed\n"

    def _routes(self, document: str) -> dict[str, list[str]]:
        """The errors of ``document`` as the pointed document and as the tag's own document."""
        require_parser(self)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / self.mod.INSTALL_SH).write_text(self.INSTALL, encoding="utf-8")
            (root / "docs" / "releases").mkdir(parents=True)
            (root / self.DOC).write_bytes(document.encode("utf-8"))
            pointed: list[str] = []
            own: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_migration_pointers(self.TAG, pointed)
                self.mod.check_release_brief(self.TAG, self.DOC, own)
            return {"pointed": pointed, "own": own}

    def _assert_refused(self, document: str, wanted: str) -> None:
        for route, errors in self._routes(document).items():
            with self.subTest(route):
                self.assertEqual(errors, [wanted])

    def test_each_front_matter_opening_is_refused(self):
        wanted = (f"{self.DOC} opens with a front matter delimiter ('---', '+++' or ';;;'); GitLab may read what follows "
                  "as front matter and hide it, so start the document with '# Release' (SEC-T739-04)")
        for opening in ("---\n", "+++\n", ";;;\n", "---", "--- \n", "--- yaml\n", "---yaml\n", "----\n", "\ufeff---\n",
                        "\n\n---\n", "  \n---\n", "\ufeff\n---\n", "# coding: utf-8\n---\n", "\ufeffcoding: x\n\n+++\n"):
            with self.subTest(opening):
                self._assert_refused(f"{opening}\n{self.GOOD_DOC}", wanted)

    def test_crlf_and_cr_are_read_as_lf_before_the_check(self):
        for opening in ("---\r\n", "---\r", "\r\n;;;\r\n"):
            with self.subTest(opening):
                self.assertIn("front matter delimiter", self._routes(f"{opening}{self.GOOD_DOC}")["pointed"][0])

    def test_a_delimiter_elsewhere_is_not_refused(self):
        for document in (f"{self.GOOD_DOC}\n---\n", "# Release\n---\n", "  ---\n", "-- x\n", "+ a\n", "; a\n", "\ufeff# R\n"):
            with self.subTest(document):
                self.assertIsNone(self.mod.document_refusal(self.DOC, document))

    def test_a_line_over_the_limit_is_refused_by_path_and_line_with_no_content(self):
        limit = self.mod.MAX_LINE_CHARS
        document = f"{self.GOOD_DOC}\nSECRETWORD{'x' * limit}\n"
        self._assert_refused(document, (
            f"{self.DOC}:7 is longer than {limit} characters; the gate refuses it before parsing, "
            "because parsing time grows worse than linearly with such a line (TD-T739-01)"))

    def test_the_limit_is_exact_and_counts_characters(self):
        limit = self.mod.MAX_LINE_CHARS
        self.assertIsNone(self.mod.long_line_number("x" * limit))
        self.assertIsNone(self.mod.long_line_number("\U0001F600" * limit))
        self.assertEqual(self.mod.long_line_number("x" * (limit + 1)), 1)
        self.assertEqual(self.mod.long_line_number("a\n\n" + "x" * (limit + 1) + "\n" + "y" * (limit + 1)), 3)
        self.assertEqual(limit, 65536)

    def test_the_long_line_is_refused_before_the_parser_runs(self):
        document = f"{self.GOOD_DOC}\n{'x' * (self.mod.MAX_LINE_CHARS + 1)}\n"
        with mock.patch.object(self.mod, "MarkdownIt", side_effect=AssertionError("the parser ran")):
            self.assertIs(self.mod.has_cursor_migration_item(document), False)
            self.assertIn("is longer than", self._routes(document)["pointed"][0])

    def test_a_document_at_the_limit_is_parsed(self):
        document = f"{self.GOOD_DOC}\n{'x' * self.mod.MAX_LINE_CHARS}\n"
        self.assertEqual(self._routes(document)["pointed"], [])
        self.assertTrue(self.mod.has_cursor_migration_item(document))

    def test_the_gate_as_a_whole_refuses_with_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in self.mod.REQUIRED_FILES:
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_bytes((repo_root() / relative).read_bytes())
            (root / self.mod.INSTALL_SH).write_text(self.INSTALL, encoding="utf-8")
            (root / self.DOC).write_text(f"---\n{self.GOOD_DOC}", encoding="utf-8")
            with mock.patch.object(self.mod, "ROOT", root):
                code, output = self._run_main(self.TAG)
        self.assertEqual(code, 1, output)
        self.assertEqual(len(_error_lines(output)), 1, output)
        self.assertIn("(SEC-T739-04)", output)

    def test_a_document_on_a_line_without_cursor_is_not_read(self):
        """SEC-T741-07: existence only. Neither its bytes nor these rules reach it, as --help says."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / self.mod.INSTALL_SH).write_text("#!/bin/sh\necho 'docs/releases/v9.0.0.md'\n", encoding="utf-8")
            (root / "docs" / "releases").mkdir(parents=True)
            (root / self.DOC).write_bytes(b"---\n\xff\n" + b"x" * (self.mod.MAX_LINE_CHARS + 1))
            errors: list[str] = []
            with mock.patch.object(self.mod, "ROOT", root):
                self.mod.check_migration_pointers(self.TAG, errors)
        self.assertEqual(errors, [])

    def test_no_release_document_of_this_tree_is_refused(self):
        for path in sorted((repo_root() / "docs" / "releases").glob("v*.md")):
            with self.subTest(path.name):
                self.assertIsNone(self.mod.document_refusal(path, self.mod.read_strict(path)))


class AnchorWordingTests(unittest.TestCase):
    """SEC-T739-08: the words a release author reads match the parser, and the gate's commands name the install."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load()

    def test_the_template_and_the_error_say_paragraph(self):
        template = " ".join((repo_root() / "docs/releases/_template.md").read_text(encoding="utf-8").split())
        script = " ".join((repo_root() / "scripts/verify-release-docs.py").read_text(encoding="utf-8").split())
        for name, text in (("template", template), ("script", script)):
            with self.subTest(name):
                self.assertNotIn("lead line", text)
                self.assertNotIn("a line that starts with a bold lead", text)
        self.assertIn("a paragraph that opens with a `**` span holding the word, optionally in a list", template)
        self.assertIn("a paragraph that opens with a '**' span holding the word, optionally in a", script)

    def test_the_error_says_it_too(self):
        require_parser(self)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "v9.md").write_text("# R\n", encoding="utf-8")
            with mock.patch.object(self.mod, "ROOT", Path(tmp)):
                problem = self.mod.cursor_item_problem("v9.md")
        self.assertIn("a paragraph that opens with a '**' span holding the word, optionally in a list", problem)
        self.assertIn("with no HTML other than comments in it or anywhere above it in the document", problem)

    def test_contributing_points_each_gate_command_to_the_install(self):
        text = " ".join((repo_root() / "CONTRIBUTING.md").read_text(encoding="utf-8").split())
        self.assertIn("Then run step 4 again, in the virtual environment that holds step 4's install of `markdown-it-py`:", text)
        self.assertIn("Install `markdown-it-py` as in step 4, then run `python3 scripts/verify-release-docs.py --tag vX.Y.Z-rc.N`", text)


class RawSeparatorTests(unittest.TestCase):
    """SEC-T738-06: this file writes U+2028 and U+2029 as escapes, and the samples still hold them."""

    def test_this_file_holds_neither_character(self):
        raw = Path(__file__).read_bytes()
        self.assertNotIn(b"\xe2\x80\xa8", raw)
        self.assertNotIn(b"\xe2\x80\xa9", raw)

    def test_the_samples_still_hold_them(self):
        self.assertEqual(LineBreakCharacterTests.CHARS[-2:], (chr(0x2028), chr(0x2029)))
        for code in (0x2028, 0x2029, 0x061c, 0x200b, 0x202e, 0x2066, 0xfeff):
            with self.subTest(hex(code)):
                self.assertIn(chr(code), UNSAFE_SAMPLES)

    def test_each_sample_line_of_the_file_is_ascii(self):
        for line in Path(__file__).read_text(encoding="utf-8").splitlines():
            if line.startswith("UNSAFE_SAMPLES = ") or line.lstrip().startswith("CHARS = "):
                self.assertTrue(line.isascii(), line[:40])


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
