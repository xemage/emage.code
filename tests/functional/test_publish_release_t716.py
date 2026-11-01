"""T716 (LOW batch B) -- scripts/publish-release.py.

  - SEC-T685-02: a commit subject loses every Default_Ignorable_Code_Point (the full Unicode 15.0 list, which is the
    database of Python 3.12) through a category test (Cc, Cf, Cs, Co, Cn, Zl, Zp) plus the Mn/Lo/So members;
  - SEC-T675-10: a changelog entry cannot become Markdown structure (HTML, comment, link, image, character reference,
    heading, list, rule, fence); code spans and emphasis are kept; the release description holds no subject;
  - TL-T708-06: gitlab_request and create_or_update_release take at most four parameters, and the token is not in a repr;
  - D-T710-2: the new entry goes BELOW ``## [Unreleased]`` (Keep a Changelog order);
  - T717-D3: the previous tag is found by semantic-version order, so a pre-release sorts before its final.
Every guard has a mutation proof (the guard is removed from a copy of the source and the condition must then FAIL).
"""
from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.functional.test_publish_release_remainders import PR, mutated

# DerivedCoreProperties.txt, Unicode 15.0.0, property Default_Ignorable_Code_Point (all 27 lines).
DEFAULT_IGNORABLE = [(0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C), (0x115F, 0x1160), (0x17B4, 0x17B5),
                     (0x180B, 0x180D), (0x180E, 0x180E), (0x180F, 0x180F), (0x200B, 0x200F), (0x202A, 0x202E),
                     (0x2060, 0x2064), (0x2065, 0x2065), (0x2066, 0x206F), (0x3164, 0x3164), (0xFE00, 0xFE0F),
                     (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3), (0x1D173, 0x1D17A),
                     (0xE0000, 0xE0000), (0xE0001, 0xE0001), (0xE0002, 0xE001F), (0xE0020, 0xE007F),
                     (0xE0080, 0xE00FF), (0xE0100, 0xE01EF), (0xE01F0, 0xE0FFF)]


def subjects(module, *log_subjects: str) -> list[str]:
    framed = "".join(subject + "\x00" for subject in log_subjects)  # what `git log --pretty=%s%x00` prints
    with mock.patch.object(module, "run_git", lambda args: framed if args[0] == "log" else "1"):
        return module.get_commit_subjects("v1.2.3", None)


class TestDefaultIgnorableCodePoints(unittest.TestCase):
    def test_every_default_ignorable_code_point_is_removed(self):
        missed = [f"U+{c:04X}" for lo, hi in DEFAULT_IGNORABLE for c in range(lo, hi + 1)
                  if not PR.subject_char_is_unsafe(chr(c))]
        self.assertEqual(missed, [])

    def test_the_code_points_the_old_class_missed_are_removed_from_a_subject(self):
        for char in ("\u180b", "\u180e", "\u180f", "\u206a", "\u206f", "\ufff0", "\ufff8", "\U0001bca0", "\U0001d173",
                     "\U000e0080", "\U000e0fff", "\ue000", "\U0010fffd", "\u0378"):
            with self.subTest(codepoint=f"U+{ord(char):04X}"):
                self.assertEqual(subjects(PR, f"feat: pay{char}load"), ["feat: payload"])

    def test_letters_marks_symbols_and_spaces_of_real_subjects_are_kept(self):
        line = "fix(ui): café naïve 中文 العربية हिन्दी e\u0301 \u2764 \U0001f600 a-b_c `x` [y](z) 100%"
        self.assertEqual(subjects(PR, line), [line])

    def test_mutation_dropping_the_category_test_is_detected(self):
        mutant = mutated("    return unicodedata.category(char) in SUBJECT_UNSAFE_CATEGORIES or char in SUBJECT_INVISIBLE_MARKS",
                         "    return char in SUBJECT_INVISIBLE_MARKS")
        self.assertEqual(subjects(PR, "feat: a\u206ab\ufff0c"), ["feat: abc"])
        self.assertEqual(subjects(mutant, "feat: a\u206ab\ufff0c"), ["feat: a\u206ab\ufff0c"])

    def test_mutation_dropping_the_unassigned_category_is_detected(self):
        mutant = mutated('"Co", "Cn", ', '"Co", ')
        self.assertEqual(subjects(PR, "feat: a\ufff0b\U000e0fffc"), ["feat: abc"])
        self.assertEqual(subjects(mutant, "feat: a\ufff0b\U000e0fffc"), ["feat: a\ufff0b\U000e0fffc"])

    def test_mutation_dropping_the_mongolian_selectors_is_detected(self):
        mutant = mutated("\\u180b\\u180c\\u180d\\u180f", "")
        self.assertEqual(subjects(PR, "feat: a\u180bb\u180fc"), ["feat: abc"])
        self.assertEqual(subjects(mutant, "feat: a\u180bb\u180fc"), ["feat: a\u180bb\u180fc"])


try:  # a CommonMark renderer, when one is installed, shows what GitLab would draw (GitLab itself is not tested here)
    from markdown_it import MarkdownIt
except ImportError:  # pragma: no cover
    MarkdownIt = None


class TestMarkdownEscaping(unittest.TestCase):
    HOSTILE = ["<!-- hides every later entry", "<img src=x onerror=alert(1)>", "<http://x.invalid>",
               "[docs](javascript:alert(1))", "![pixel](https://t.invalid/p.png)", "a &#8238; b &amp; c",
               "# heading", "## [v9.9.9] - 2099-01-01", "1. ordered", "12) ordered", "- bullet", "+ bullet",
               "* bullet", "***", "- - -", "___", "```fence", "~~~fence", "> quote", "x\\", "C:\\dir\\<x>",
               "\\`a`", "<span title='`'>x`", "`x <a b='`'>"]

    def test_hostile_entries_are_escaped_exactly(self):
        cases = {"<!-- c": "\\<!-- c", "[a](b)": "\\[a\\](b)", "&#8238;": "\\&#8238;", "# h": "\\# h", "1. o": "1\\. o",
                 "- b": "\\- b", "***": "\\***", "```f": "\\`\\`\\`f", "~~~": "\\~~~", "> q": "\\> q",
                 "a\\b": "a\\\\b", "x `a<b>` <c>": "x `a<b>` \\<c\\>"}
        for raw, escaped in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(PR.markdown_entry(raw), escaped)

    def test_code_spans_emphasis_and_plain_text_are_kept(self):
        for line in ("use `code` and *em* and _under_ and snake_case", "``a`b`` stays one span", "100% done, a/b-c",
                     "-1 is not a list", "**bold** first", "v1.2.3 (#42)"):
            with self.subTest(line=line):
                self.assertEqual(PR.markdown_entry(line), line)

    def test_the_rendered_section_escapes_every_entry(self):
        grouped = {"Features": ["<!-- x", "[a](b)"], "Other": ["# h"]}
        text = PR.render_changelog_section("v1.0.0", grouped)
        self.assertIn("- \\<!-- x\n- \\[a\\](b)\n", text)
        self.assertIn("- \\# h\n", text)

    @unittest.skipUnless(MarkdownIt, "markdown-it-py is not installed")
    def test_commonmark_renders_each_hostile_entry_as_one_plain_list_item(self):
        md = MarkdownIt("commonmark")
        for raw in self.HOSTILE:
            with self.subTest(raw=raw):
                tokens = md.parse(f"- {PR.markdown_entry(raw)}\n- next\n")
                types_ = [t.type for t in tokens]
                self.assertEqual(types_.count("list_item_open"), 2)
                self.assertFalse({"html_block", "heading_open", "blockquote_open", "fence", "hr",
                                  "ordered_list_open"} & set(types_))
                inline = [c for t in tokens if t.type == "inline" for c in t.children]
                self.assertFalse({"html_inline", "link_open", "image"} & {c.type for c in inline})
                self.assertNotIn("\u202e", md.render(f"- {PR.markdown_entry(raw)}\n"))

    def test_mutation_dropping_the_escape_is_detected(self):
        mutant = mutated("    out = \"\".join(part if is_code else part.translate(MARKDOWN_ESCAPES)",
                         "    out = \"\".join(part if is_code else part")
        self.assertEqual(mutant.markdown_entry("<!-- x"), "<!-- x")
        self.assertEqual(PR.markdown_entry("<!-- x"), "\\<!-- x")

    def test_mutation_escaping_inside_code_spans_is_detected(self):
        mutant = mutated("    out = \"\".join(part if is_code else part.translate(MARKDOWN_ESCAPES)",
                         "    out = \"\".join(part.translate(MARKDOWN_ESCAPES)")
        self.assertEqual(PR.markdown_entry("`a<b>`"), "`a<b>`")
        self.assertNotEqual(mutant.markdown_entry("`a<b>`"), "`a<b>`")

    def test_mutation_dropping_the_leading_block_rule_is_detected(self):
        mutant = mutated("    if lead:\n", "    if False:\n")
        self.assertEqual(PR.markdown_entry("# h"), "\\# h")
        self.assertEqual(mutant.markdown_entry("# h"), "# h")

    def test_the_release_description_holds_no_subject(self):
        brief = "# Release v1.2.3\n\nbody\n"
        self.assertIs(PR.render_release_description(brief), brief)
        source = inspect.getsource(PR.main)
        self.assertIn("description = render_release_description(brief)", source)
        self.assertNotIn("subjects", source.split("description = ", 1)[1].split("\n", 1)[0])


class TestParameterLimit(unittest.TestCase):
    def test_the_api_functions_take_at_most_four_parameters(self):
        for func in (PR.gitlab_request, PR.create_or_update_release):
            with self.subTest(func=func.__name__):
                self.assertLessEqual(len(inspect.signature(func).parameters), 4)

    def test_the_token_is_not_in_the_repr_of_the_credential_or_the_target(self):
        credential = PR.ApiCredential("tok-secret-fake", "JOB-TOKEN")
        target = PR.ApiTarget("https://gitlab.invalid/api/v4", "7", credential, "gitlab.invalid")
        self.assertNotIn("tok-secret-fake", repr(credential) + repr(target) + str(target))
        self.assertIn("JOB-TOKEN", repr(target))

    def test_the_default_header_is_private_token(self):
        self.assertEqual(PR.ApiCredential("t").header, "PRIVATE-TOKEN")


class TestUnreleasedStaysOnTop(unittest.TestCase):
    INTRO = "# Changelog\n\nIntro.\n\n"
    UNRELEASED = "## [Unreleased]\n\nUpcoming text.\n"

    def update(self, module, existing: str) -> str:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(module, "ROOT", Path(tmp)):
            (Path(tmp) / "CHANGELOG.md").write_text(existing, encoding="utf-8")
            return module.update_changelog("v1.2.3", "## Changelog\n\n### Features\n- new\n")

    def test_the_new_entry_goes_below_unreleased_when_it_is_the_only_heading(self):
        text = self.update(PR, self.INTRO + self.UNRELEASED)
        self.assertLess(text.index("## [Unreleased]"), text.index("## [v1.2.3]"))
        self.assertIn("Upcoming text.\n\n## [v1.2.3] - ", text)

    def test_the_new_entry_goes_between_unreleased_and_the_newest_release(self):
        text = self.update(PR, self.INTRO + self.UNRELEASED + "\n## [v1.2.2] - 2026-01-01\n\n- old\n")
        order = [text.index(h) for h in ("## [Unreleased]", "## [v1.2.3]", "## [v1.2.2]")]
        self.assertEqual(order, sorted(order))

    def test_without_unreleased_the_entry_still_goes_above_the_newest_release(self):
        text = self.update(PR, self.INTRO + "## [v1.2.2] - 2026-01-01\n\n- old\n")
        self.assertLess(text.index("## [v1.2.3]"), text.index("## [v1.2.2]"))
        self.assertTrue(text.startswith(self.INTRO))

    def test_the_committed_changelog_keeps_unreleased_on_top(self):
        repo = Path(PR.__file__).resolve().parent.parent
        text = self.update(PR, (repo / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertLess(text.index("## [Unreleased]"), text.index("## [v1.2.3]"))

    def test_mutation_treating_unreleased_as_an_entry_is_detected(self):
        mutant = mutated("        first_entry = RELEASED_HEADING_RE.search(existing)",
                         "        first_entry = re.search(r\"^## \", existing, re.M)")
        text = self.update(mutant, self.INTRO + self.UNRELEASED)
        self.assertGreater(text.index("## [Unreleased]"), text.index("## [v1.2.3]"))  # the old K-10 order


class TestSemanticTagOrder(unittest.TestCase):
    def tags(self, module, listing: str) -> list[str]:
        with mock.patch.object(module, "run_git", lambda args: listing):
            return module.get_tag_list()

    def test_a_pre_release_sorts_before_its_final(self):
        tags = self.tags(PR, "v1.0.0\nv1.1.0\nv1.0.0-rc.1\n")
        self.assertEqual(tags, ["v1.1.0", "v1.0.0", "v1.0.0-rc.1"])
        self.assertEqual(PR.resolve_previous_tag("v1.1.0", tags), "v1.0.0")
        self.assertEqual(PR.resolve_previous_tag("v1.0.0", tags), "v1.0.0-rc.1")

    def test_git_version_sort_order_as_input_gives_the_same_result(self):
        """What `git tag --sort=-v:refname` prints without versionsort.suffix (observed with git 2.x, 2026-11-01)."""
        self.assertEqual(self.tags(PR, "v1.1.0\nv1.0.0-rc.1\nv1.0.0\n"), ["v1.1.0", "v1.0.0", "v1.0.0-rc.1"])

    def test_pre_release_identifiers_follow_semver(self):
        listing = "v2.0.0-rc.10\nv2.0.0-rc.2\nv2.0.0-beta\nv2.0.0-alpha.1\nv2.0.0-alpha\nv2.0.0\nv1.10.0\nv1.9.0\n"
        self.assertEqual(self.tags(PR, listing), ["v2.0.0", "v2.0.0-rc.10", "v2.0.0-rc.2", "v2.0.0-beta",
                                                  "v2.0.0-alpha.1", "v2.0.0-alpha", "v1.10.0", "v1.9.0"])

    def test_the_order_matches_the_drift_script_on_the_final_versus_pre_release_rule(self):
        import importlib.util
        path = Path(PR.__file__).resolve().parent / "check-main-develop-drift.py"
        spec = importlib.util.spec_from_file_location("drift_t716", path)
        drift = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drift)
        for a, b in (("v1.0.0-rc.1", "v1.0.0"), ("v1.0.0", "v1.1.0"), ("v1.9.0", "v1.10.0")):
            with self.subTest(pair=(a, b)):
                self.assertLess(drift.semver_key(a), drift.semver_key(b))
                self.assertLess(PR.tag_sort_key(a), PR.tag_sort_key(b))

    def test_mutation_trusting_the_listing_order_is_detected(self):
        mutant = mutated("    return sorted(tags, key=tag_sort_key, reverse=True)", "    return tags")
        listing = "v1.1.0\nv1.0.0-rc.1\nv1.0.0\n"
        self.assertEqual(PR.resolve_previous_tag("v1.1.0", self.tags(PR, listing)), "v1.0.0")
        self.assertEqual(mutant.resolve_previous_tag("v1.1.0", self.tags(mutant, listing)), "v1.0.0-rc.1")


if __name__ == "__main__":
    unittest.main()
