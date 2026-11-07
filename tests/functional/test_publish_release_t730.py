"""T730 (LOW batch G) -- scripts/publish-release.py.

  - SEC-T716-02: the reserved Default_Ignorable_Code_Point ranges are removed by number, so a newer Unicode database
    that assigns a code point there cannot bring it back; the release image's Unicode version is asserted;
  - SEC-T716-03: GitLab references (``@user``, ``#123``, ``!12``, ``~label``, ``%milestone``, ``$snippet``, ``^alert``)
    are backslash-escaped and bare URLs become code spans, outside code spans only;
  - SEC-T730-05: a run of more than 32 backticks opens no code span, so it is escaped and its inside is neutralised;
  - SEC-T716-04: ``ApiCredential`` is not a tuple; no ``tuple()``, unpacking, ``_asdict()``, ``vars()``,
    ``%``-formatting, pickling or copying exposes the token.
Every guard has a mutation proof (the guard is removed from a copy of the source and the condition must then FAIL).
"""
from __future__ import annotations

import copy
import dataclasses
import pickle
import random
import re
import sys
import time
import types
import unicodedata
import unittest
from unittest import mock

from tests._helpers.repo import repo_root
from tests.functional.test_publish_release_remainders import PR, mutated
from tests.functional.test_publish_release_t716 import commonmark, subjects

# The Unicode database of each CPython minor the release image may use (unicodedata.unidata_version).
PYTHON_UNICODE = {"3.12": "15.0.0", "3.13": "15.1.0", "3.14": "16.0.0"}
RESERVED = [0x2065, 0xFFF0, 0xFFF8, 0xE0000, 0xE0002, 0xE001F, 0xE0080, 0xE00FF, 0xE01F0, 0xE0FFF]
SECRET = "tok-secret-fake-t730"
LONG_RUN_PAYLOAD = "[x](https://evil.invalid) <img src=x> https://evil.invalid"
URL_HINT = re.compile(r"://|(?<![A-Za-z0-9])www\.", re.IGNORECASE)


def reference_code_span_parts(text: str) -> list[tuple[bool, str]]:
    """The pairwise algorithm code_span_parts had before T730 (a run is closed by the next run of the same length)."""
    runs = list(re.finditer(r"`+", text))
    parts, start, i = [], 0, 0
    while i < len(runs):
        closer = next((j for j in range(i + 1, len(runs)) if len(runs[j].group()) == len(runs[i].group())), None)
        if closer is None:
            i += 1
            continue
        parts += [(False, text[start:runs[i].start()]), (True, text[runs[i].start():runs[closer].end()])]
        start, i = runs[closer].end(), closer + 1
    return parts + [(False, text[start:])]


def release_image_python() -> str:
    """The Python minor of the `release:` job image in .gitlab-ci.yml (e.g. ``3.12``)."""
    text = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")
    job = re.search(r"^release:\n((?:[ \t]+.*\n|\n)+)", text, re.MULTILINE)
    assert job, "no release job in .gitlab-ci.yml"
    image = re.search(r"^\s+image:\s*python:(\d+\.\d+)-alpine@sha256:[0-9a-f]{64}\s*$", job.group(1), re.MULTILINE)
    assert image, "the release job image is not a digest-pinned python:X.Y-alpine"
    return image.group(1)


class AssignedEverything(types.SimpleNamespace):
    """A stand-in for a NEWER Unicode database that has assigned every reserved code point (as a letter)."""

    @staticmethod
    def category(char: str) -> str:
        return "Lo" if any(lo <= ord(char) <= hi for lo, hi in PR.SUBJECT_RESERVED_IGNORABLE_RANGES) else \
            unicodedata.category(char)


class TestReservedIgnorableRanges(unittest.TestCase):
    def test_the_release_image_unicode_version_is_the_reviewed_one(self):
        minor = release_image_python()
        self.assertEqual(PYTHON_UNICODE.get(minor), PR.SUBJECT_REVIEWED_UNICODE_VERSION,
                         "the release image changed: re-read the Default_Ignorable list, then update the table")
        if f"{sys.version_info[0]}.{sys.version_info[1]}" == minor:  # the unit-tests job runs this image's Python
            self.assertEqual(unicodedata.unidata_version, PR.SUBJECT_REVIEWED_UNICODE_VERSION)

    def test_the_ranges_are_the_reserved_default_ignorable_ones(self):
        self.assertEqual(PR.SUBJECT_RESERVED_IGNORABLE_RANGES, ((0x2065, 0x2065), (0xFFF0, 0xFFF8), (0xE0000, 0xE0FFF)))

    def test_reserved_code_points_are_removed_even_when_a_newer_database_assigns_them(self):
        with mock.patch.object(PR, "unicodedata", AssignedEverything()):
            self.assertEqual(PR.unicodedata.category("￰"), "Lo")
            for code in RESERVED:
                with self.subTest(codepoint=f"U+{code:04X}"):
                    self.assertTrue(PR.subject_char_is_unsafe(chr(code)))
            self.assertFalse(PR.subject_char_is_unsafe("a"))

    def test_mutation_dropping_the_ranges_is_detected(self):
        mutant = mutated("    if any(lo <= ord(char) <= hi for lo, hi in SUBJECT_RESERVED_IGNORABLE_RANGES):\n"
                         "        return True\n", "")
        with mock.patch.object(mutant, "unicodedata", AssignedEverything()):
            self.assertFalse(mutant.subject_char_is_unsafe("￰"))  # a newer database would let it through
        with mock.patch.object(PR, "unicodedata", AssignedEverything()):
            self.assertEqual(subjects(PR, "feat: a⁥b￰c\U000e0fffd"), ["feat: abcd"])


class TestReferencesAndUrls(unittest.TestCase):
    CASES = {"thanks @admin": "thanks \\@admin", "fixes #123": "fixes \\#123", "see !12": "see \\!12",
             "label ~bug": "label \\~bug", "in %v1.0": "in \\%v1.0", "snippet $7": "snippet \\$7",
             "alert ^alert#3": "alert \\^alert\\#3", "group/project#5": "group/project\\#5",
             "see https://evil.invalid/x?a=1": "see `https://evil.invalid/x?a=1`",
             "(HTTP://A.invalid)": "`(HTTP://A.invalid)`", "go www.evil.invalid now": "go `www.evil.invalid` now",
             "x`y https://a.invalid": "x\\`y `https://a.invalid`", "awww.x": "awww.x",
             # T730 (SEC-T730-01): GFM also starts a www autolink after ( * _ ~
             "see (www.evil.invalid)": "see `(www.evil.invalid)`", "_www.evil.invalid_": "`_www.evil.invalid_`",
             "*www.a.invalid* ~www.b.invalid": "`*www.a.invalid*` `~www.b.invalid`", "a1www.x": "a1www.x"}
    # T730 (SEC-T730-01): a wrapped token next to a kept code span is set off by one space (raw -> (escaped, shown)).
    NEXT_TO_CODE = {"``c``https://evil.invalid": ("``c`` `https://evil.invalid`", "c https://evil.invalid"),
                    "https://evil.invalid``c``": ("`https://evil.invalid` ``c``", "https://evil.invalid c"),
                    "`k`www.e.invalid`k`": ("`k` `www.e.invalid` `k`", "k www.e.invalid k")}

    def test_sigils_and_urls_are_neutralised_exactly(self):
        for raw, escaped in self.CASES.items():
            with self.subTest(raw=raw):
                self.assertEqual(PR.markdown_entry(raw), escaped)

    def test_code_spans_are_kept(self):
        for line in ("`@user #1 !2 ~3 %4 https://x.invalid`", "run `curl https://x.invalid`"):
            with self.subTest(line=line):
                self.assertEqual(PR.markdown_entry(line), line)

    def test_a_url_next_to_a_kept_code_span_is_wrapped_and_set_off(self):
        for raw, (escaped, _shown) in self.NEXT_TO_CODE.items():
            with self.subTest(raw=raw):
                self.assertEqual(PR.markdown_entry(raw), escaped)

    def assert_links_nothing(self, md, entry: str) -> list:
        tokens = md.parse(f"- {entry}\n")
        inline = [c for t in tokens if t.type == "inline" for c in t.children]
        self.assertFalse({"link_open", "html_inline", "image"} & {c.type for c in inline})
        self.assertFalse([c.content for c in inline if c.type == "text" and URL_HINT.search(c.content)])
        return inline

    def test_commonmark_renders_the_text_unchanged_and_links_nothing(self):
        md = commonmark(self)
        for raw, shown in [*((r, r) for r in self.CASES), *((r, v[1]) for r, v in self.NEXT_TO_CODE.items())]:
            with self.subTest(raw=raw):
                inline = self.assert_links_nothing(md, PR.markdown_entry(raw))
                self.assertEqual("".join(c.content for c in inline if c.type in ("text", "code_inline")), shown)
                for child in inline:
                    if "://" in child.content or re.search(r"(?:^|\s)www\.", child.content, re.IGNORECASE):
                        self.assertEqual(child.type, "code_inline")  # GitLab links nothing inside a code span

    def test_mutation_dropping_the_sigils_is_detected(self):
        mutant = mutated(' + REFERENCE_SIGILS})', '})')
        self.assertEqual(mutant.markdown_entry("fixes #123"), "fixes #123")
        self.assertEqual(PR.markdown_entry("fixes #123"), "fixes \\#123")

    def test_mutation_dropping_the_space_next_to_a_code_span_is_detected(self):
        md = commonmark(self)
        mutant = mutated('            out.append((" " if last_wrapped else "") + part)', '            out.append(part)')
        self.assert_links_nothing(md, PR.markdown_entry("https://evil.invalid``c``"))
        bare = md.parse(f"- {mutant.markdown_entry('https://evil.invalid``c``')}\n")
        texts = [c.content for t in bare if t.type == "inline" for c in t.children if c.type == "text"]
        self.assertTrue([text for text in texts if "://" in text])  # the URL lands in a text node

    def test_a_bare_url_left_by_the_wrapping_falls_back_to_escaping_only(self):
        with mock.patch.object(PR, "wrapped_entry", lambda text: "see https://x.invalid <b>"):
            self.assertEqual(PR.markdown_entry("see https://x.invalid <b>"), "see https://x.invalid \\<b\\>")
        mutant = mutated("    if any(URL_HINT_RE.search(part) for is_code, part in rendered_code_parts(out) if not is_code):",
                         "    if False:")
        with mock.patch.object(mutant, "wrapped_entry", lambda text: "see https://x.invalid <b>"):
            self.assertEqual(mutant.markdown_entry("see https://x.invalid <b>"), "see https://x.invalid <b>")

    def test_the_output_parser_honours_escapes_outside_code_spans_only(self):
        self.assertEqual(PR.rendered_code_parts("\\``u`"), [(False, "\\`"), (True, "`u`"), (False, "")])
        self.assertEqual(PR.rendered_code_parts("`a\\` b"), [(False, ""), (True, "`a\\`"), (False, " b")])
        self.assertEqual(PR.rendered_code_parts("\\`a`"), [(False, "\\`a`")])

    def test_code_span_parts_matches_the_pairwise_reference(self):
        rng = random.Random(730)  # at most 24 characters, so no run reaches the 32-backtick limit of SEC-T730-05
        for _ in range(400):
            text = "".join(rng.choice("``ab ") for _ in range(rng.randint(0, 24)))
            with self.subTest(text=text):
                self.assertEqual(PR.code_span_parts(text), reference_code_span_parts(text))

    def test_long_subjects_are_neutralised_in_linear_time(self):
        """T730 (SEC-T730-02): the old URL regex took about 35 s on 100k characters without whitespace."""
        shapes = ["a" * 100_000, "https://" + "a" * 99_992, "www." * 25_000, "`a" * 50_000, "@#" * 50_000,
                  "".join("`" * (k % 50 + 1) + "x" for k in range(4_000))[:100_000],
                  "`" * 100_000, ("`" * 33 + "x") * 2_941]
        for shape in shapes:
            with self.subTest(shape=shape[:12]):
                started = time.perf_counter()
                PR.markdown_entry(shape)
                self.assertLess(time.perf_counter() - started, 1.0)

    def long_run_entry(self, ticks: int) -> tuple[str, str]:
        """(subject, the exact escaped entry) for the payload between two runs of ``ticks`` backticks."""
        run, escaped = "`" * ticks, "\\`" * ticks
        return (f"{run}{LONG_RUN_PAYLOAD}{run}",
                f"{escaped}`[x](https://evil.invalid)` \\<img src=x\\> `https://evil.invalid`{escaped}")

    def test_a_run_longer_than_32_backticks_opens_no_code_span(self):
        """T730 (SEC-T730-05): comrak reads an opening run above 80 backticks, cmark above 1000, as literal text (read
        from their source, not run), so such a "code span" would be parsed as Markdown. markdown-it-py has no such
        limit (it shows a code span either way), so the exact output is what pins this."""
        md = commonmark(self)
        for ticks in (33, 81, 1001):
            with self.subTest(ticks=ticks):
                raw, escaped = self.long_run_entry(ticks)
                self.assertEqual(PR.markdown_entry(raw), escaped)
                inline = self.assert_links_nothing(md, escaped)
                self.assertEqual("".join(c.content for c in inline if c.type in ("text", "code_inline")), raw)

    def test_a_run_of_exactly_32_backticks_stays_a_code_span(self):
        md = commonmark(self)
        raw, _escaped = self.long_run_entry(32)
        self.assertEqual(PR.markdown_entry(raw), raw)
        self.assert_links_nothing(md, raw)
        self.assertEqual([part[0] for part in PR.code_span_parts(raw)], [False, True, False])

    def test_the_output_parser_applies_the_same_limit(self):
        for ticks, is_code in ((32, True), (33, False), (81, False), (1001, False)):
            with self.subTest(ticks=ticks):
                text = "`" * ticks + "x" + "`" * ticks
                self.assertEqual(any(code for code, _part in PR.rendered_code_parts(text)), is_code)
                self.assertEqual(any(code for code, _part in PR.code_span_parts(text)), is_code)

    def test_mutation_dropping_the_input_limit_is_detected(self):
        mutant = mutated("        if opener.start() < start or len(opener.group()) > MAX_CODE_SPAN_BACKTICKS:",
                         "        if opener.start() < start:")
        raw, escaped = self.long_run_entry(81)
        self.assertEqual(PR.markdown_entry(raw), escaped)
        self.assertEqual(mutant.markdown_entry(raw), raw)  # kept verbatim: the renderer may parse the inside

    def test_mutation_dropping_the_output_limit_is_detected(self):
        mutant = mutated(' and len(found.group()) <= MAX_CODE_SPAN_BACKTICKS\n', '\n')
        text = "`" * 81 + "https://evil.invalid" + "`" * 81
        self.assertFalse(any(code for code, _part in PR.rendered_code_parts(text)))
        self.assertTrue(any(code for code, _part in mutant.rendered_code_parts(text)))

    def test_mutation_dropping_the_url_code_span_is_detected(self):
        mutant = mutated('f"`{chunk}`" if wrapped else ', 'chunk if wrapped else ')
        self.assertEqual(mutant.markdown_entry("see https://x.invalid"), "see https://x.invalid")
        self.assertEqual(PR.markdown_entry("see https://x.invalid"), "see `https://x.invalid`")


class TestCredentialExposesNoToken(unittest.TestCase):
    def setUp(self):
        self.credential = PR.ApiCredential(SECRET, "JOB-TOKEN")
        self.target = PR.ApiTarget("https://gitlab.invalid/api/v4", "7", self.credential, "gitlab.invalid")

    def test_the_fields_stay_readable(self):
        self.assertEqual((self.credential.token, self.credential.header), (SECRET, "JOB-TOKEN"))
        self.assertEqual(PR.ApiCredential("t").header, "PRIVATE-TOKEN")

    def test_tuple_iteration_unpacking_and_asdict_are_refused(self):
        for form in (tuple, list, iter, lambda c: [*c], lambda c: c._asdict(), lambda c: c[0], vars,
                     dataclasses.asdict, dataclasses.astuple):
            with self.subTest(form=getattr(form, "__name__", "lambda")):
                with self.assertRaises((TypeError, AttributeError)):
                    form(self.credential)

    def test_formatting_shows_the_header_only(self):
        shown = [repr(self.credential), str(self.credential), f"{self.credential}", "%s" % (self.credential,),
                 "%r" % (self.credential,), "{}".format(self.credential), repr(self.target), str(self.target)]
        self.assertFalse([text for text in shown if SECRET in text])
        self.assertIn("JOB-TOKEN", repr(self.credential))
        with self.assertRaises(TypeError):
            "%s %s" % self.credential  # noqa: B018 -- a NamedTuple would format token and header here

    def test_pickling_copying_and_mutation_are_refused(self):
        for form in (pickle.dumps, copy.copy, copy.deepcopy, lambda c: pickle.dumps(self.target)):
            with self.subTest(form=getattr(form, "__name__", "lambda")):
                with self.assertRaises(TypeError):
                    form(self.credential)
        with self.assertRaises(AttributeError):
            self.credential.token = "other"
        with self.assertRaises(AttributeError):
            del self.credential.header

    def test_mutation_back_to_a_named_tuple_is_detected(self):
        source = (repo_root() / "scripts" / "publish-release.py").read_text(encoding="utf-8")
        start = source.index("class ApiCredential:")
        end = source.index("class ApiTarget(NamedTuple):")
        named = ('class ApiCredential(NamedTuple):\n    token: str\n    header: str = DEFAULT_TOKEN_HEADER\n\n'
                 '    def __repr__(self) -> str:\n        return f"ApiCredential(header={self.header!r})"\n\n\n')
        mutant = mutated(source[start:end], named)
        self.assertIn(SECRET, tuple(mutant.ApiCredential(SECRET)))
        with self.assertRaises(TypeError):
            tuple(self.credential)


if __name__ == "__main__":
    unittest.main()
