#!/usr/bin/env python3
"""Release documentation verification gate for emage.code.

Checks that required documentation exists, includes the current release marker,
contains key usage sections, and has resolvable local/internal links.

The release document's ``## Gate Verdicts`` and ``## RELEASE VERDICT`` sections must
also be filled in (TL-T649-12): a field (a list item ``label: value``, see ``MIGRATION_POINTER_HELP``) that is
still ``pending``, and any line of those sections, table rows included, that carries a template placeholder (``YYYY-MM-DD``, ``<count>``, ``<ISO-8601>``,
``<PASS/CONDITIONAL_PASS>``, the unfilled ``PASS | CONDITIONAL_PASS | FAIL``) fails
the gate. The gate does not require the Gate Verdicts section to exist (only the
RELEASE VERDICT section, as before) and does not check the field-level contract, which the
golden suite encodes. The sections are found with markdown-it-py (T747, plan-142, SEC-T739-07), not by line rules; which
lines are fields is still read line by line, from their source lines. See ``MIGRATION_POINTER_HELP``.

Migration pointers (T703, SEC-T662-01): every ``docs/releases/v*.md`` path that
``scripts/install.sh`` names must exist, and a document named on an install.sh line that
mentions "Cursor" must carry its Cursor migration item. See ``MIGRATION_POINTER_HELP``
for the anchor, for what stays open, and for how a pointer to a version newer than the tag is treated.

The Cursor item is looked for with markdown-it-py (T739, plan-136), so the gate reads the same blocks as a
CommonMark renderer, up to the parser's nesting limit. A document that reaches it is refused; on a direct call nothing past it counts as an anchor (SEC-T739-09). Only
``markdown_tokens`` calls it, for ``document_refusal``, ``has_cursor_migration_item`` and the verdict sections, and it
never parses a text over the size cap (SEC-T745-01), a long line (TD-T739-01) or the same text twice. ``main()`` refuses to run without it, on every run; there is no fallback
to line rules and no skip. The ``release-docs-gate`` job installs it from ``ci/requirements-release.txt``.

A release document the gate reads may hold no HTML other than comments, anywhere (SEC-T745-03): ``document_refusal``
refuses it from the parser's tokens, after the size and line limits. See ``MIGRATION_POINTER_HELP``.

Every printed line passes through ``printable``: control, bidi and zero-width characters of an
``install.sh`` line, a release document or a tag become ``?`` in the CI log (SEC-T715-04).

Every file the gate reads in this process must be valid UTF-8 (SEC-T739-01): the gate exits 1 on the first one that is
not, naming its path and the file offset of the first invalid byte and never its content, and no check runs on that
file. Newlines are read as before: CRLF and CR become LF, except that ``scripts/install.sh`` must hold no CR at all
(SEC-T738-02). ``scripts/check-version-consistency.py`` runs as a child process with its own reads, and this does not
cover them.

This gate cannot check that ``main`` already carries the release. That duty (merge the
release branch to ``develop`` and ``main`` before the tag, stated in CONTRIBUTING.md) is
enforced on the tag pipeline, without a grace window, by ``scripts/check-release-tag-tree.py``:
the tree of the tag's commit must equal the tree of ``origin/main``. It runs in the blocking
``main-develop-drift-gate`` job, next to ``scripts/check-main-develop-drift.py``, whose
one-release grace window applies only to ``main`` lagging ``develop`` (SEC-T685-03).
"""

from __future__ import annotations

import argparse
import functools
import html
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

try:
    from markdown_it import MarkdownIt
except ImportError:  # main() reports it; nothing else may run without the parser (T739)
    MarkdownIt = None

ROOT = Path(__file__).resolve().parent.parent

MARKER_FILES = [
    Path("README.md"),
    Path("docs/wiki/README.md"),
    Path("docs/wiki/home.md"),
]

def release_brief_path(tag: str) -> Path:
    return Path("docs/releases") / f"{tag}.md"


REQUIRED_FILES = [
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("docs/wiki/README.md"),
    Path("docs/wiki/home.md"),
    Path("docs/wiki/quick-start.md"),
    Path("docs/wiki/agents-overview.md"),
    Path("docs/wiki/implementation-guide.md"),
    Path("implementation/README.md"),
    Path("scripts/install.sh"),
    Path("docs/releases/_template.md"),
]

SECTION_REQUIREMENTS: dict[Path, list[str]] = {
    Path("README.md"): [
        "## Install",
        "## Quick start",
        "## Use emage.code in practice",
        "## Documentation release contract",
        "### Implementation",
        "scripts/install.sh",
        "docs/releases/",
    ],
    Path("CONTRIBUTING.md"): [
        "## Releasing",
        "### Cutting a release",
        "## Working with implementation",
        "release-docs-gate",
        "verify-release-docs.py",
    ],
    Path("docs/wiki/home.md"): [
        "## Wiki contents",
        "## Project links",
        "implementation-guide",
    ],
    Path("docs/wiki/quick-start.md"): [
        "## 1. Install",
        "## 4. Invoke the orchestrator",
        "/new-project",
        "scripts/install.sh",
    ],
    Path("docs/wiki/README.md"): [
        "## Sync to live Wiki",
        "## Release documentation contract",
        "implementation-guide",
    ],
    Path("docs/wiki/agents-overview.md"): [
        "schema-first runtime model",
        "managed cookbooks",
    ],
    Path("docs/wiki/implementation-guide.md"): [
        "## Validate",
        "python3 implementation/scripts/check.py",
        "node implementation/scripts/verify.mjs",
        "scripts/install.sh",
    ],
    Path("implementation/README.md"): [
        "## Install",
        "## Validation commands",
        "## Package workflow",
        "## Trigger workflow",
        "## Adapter smoke workflow",
    ],
}

VERDICT_SECTIONS = ("## Gate Verdicts", "## RELEASE VERDICT")
REQUIRED_VERDICT_SECTION = "## RELEASE VERDICT"
PLACEHOLDER_MARKERS = (
    "YYYY-MM-DD",
    "<PASS/CONDITIONAL_PASS>",
    "<count>",
    "<ISO-8601>",
    "PASS | CONDITIONAL_PASS | FAIL",
    "<tech-lead",  # SEC-T751-09: the template's '<tech-lead | orchestrator | top-level session>' is not HTML
)
# The label cannot start or end with a space or tab, so there is exactly one way to match it
# (linear time on a long run of spaces; a lazy label followed by `[ \t]*:` is quadratic).
# SEC-T748-06: a list item of any marker ('-', '*', '+', '1.', '1)'), optionally inside '>' blockquote markers. The
# prefix has one way to match: '>' groups and the marker are told apart by their first character.
LIST_ITEM_PREFIX = r"^[ \t]*(?:>[ \t]*)*(?P<marker>[-*+]|\d{1,9}[.)])"
FIELD_RE = re.compile(LIST_ITEM_PREFIX + r"[ \t]+(?P<label>[^:\n \t](?:[^:\n]*[^:\n \t])?)[ \t]*:[ \t]*(?P<value>.*)$")
LIST_ITEM_RE = re.compile(LIST_ITEM_PREFIX + r"(?:[ \t]+(?P<text>.*))?$")
# SEC-T748-06: what is stripped from both ends of a value before it is tested, after entities are resolved.
VALUE_EDGE_CHARS = "*_`~()[]\"' \t"
# SEC-T748-12: characters that are letters to str.isalnum() and render as nothing. U+2800, U+034F and the variation
# selectors are not alphanumeric, so the allowlist already leaves them out; they are listed for the reader.
INVISIBLE_LETTERS = frozenset("\u115f\u1160\u3164\uffa0\u2800\u034f") | frozenset(map(chr, range(0xFE00, 0xFE10)))
WORD_MARKER_RE = re.compile(r"\b(?:TBD|TODO)\b")
TEMPLATE_PROSE_MARKERS = ("[list ", "[if FAIL")
PENDING_ON_RE = re.compile(r"\bon\s+pending\b", re.IGNORECASE)

INSTALL_SH = Path("scripts/install.sh")
# TD-T739-01: the parser's time on one long tag grows worse than linearly, so a longer line is refused unparsed.
MAX_LINE_CHARS = 65536
# SEC-T745-01, TD-T739-01: lines join into a paragraph, so a line limit does not bound the parser's time. 128 KiB is about
# twice the largest release document (v8.0.0.md, 66,745 characters). A longer text is refused unparsed.
MAX_DOCUMENT_CHARS = 131072
# SEC-T739-09: passed to the parser as its maxNesting, so the parser and ``nesting_limit_line`` read one value. It is the
# commonmark preset's own value on 3.0.0 and 4.2.0, and a test holds that.
MAX_NESTING = 20
# SEC-T739-04: what opens front matter in GitLab's lib/gitlab/front_matter.rb (PATTERN_UNTRUSTED, read 2026-11-06), an
# optional "coding:" line, then white space, then a delimiter at the start of a line with anything after it. The BOM is
# dropped first: that pattern leaves it to whatever runs before it. No closing delimiter is required here: fail closed.
# SEC-T745-02: this is the part after the optional line; ``opens_with_front_matter`` handles that line, in linear time.
FRONT_MATTER_BODY_RE = re.compile(r"\s*^(?:---|\+\+\+|;;;)", re.MULTILINE)
# SEC-T739-02, -03: HTML that is nothing but comments. An HTML parser ends a comment at "--!>", and at once in the short
# "<!-->" and "<!--->", where CommonMark may read on, so a tag after those could be live: such text is no comment here.
COMMENTS_ONLY_RE = re.compile(r"\s*(?:(?:<!---?>|<!--(?!-?>)(?:(?!--!?>).)*-->)\s*)*", re.DOTALL)
MIGRATION_SECTION = "## Migration Guide"
MIGRATION_SECTION_TITLE = "Migration Guide"
PARSER_INSTALL_COMMAND = (
    "python3 -m pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt"
)
PARSER_MISSING = (
    "the CommonMark parser markdown-it-py is not installed, and this gate has no fallback; "
    f"install it with: {PARSER_INSTALL_COMMAND}"
)
POINTER_RE = re.compile(r"docs/releases/(?P<tag>v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)\.md")
# SEC-T703-02: "the v8.0.0 release notes" names a release document in prose; it must exist too.
PROSE_POINTER_RE = re.compile(r"\b(?P<tag>v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?) release notes\b")
# Anything that looks like a pointer to a release document; each hit must lie inside a parsed pointer.
# SEC-T715-01: also a versioned .md file name, 'release-notes' and its variants, any 'releases' path
# segment ('doc/releases'), a shell variable named for a release document ('$REL_DOC', '$RELEASE_NOTES';
# not '$DOCS_EXCLUDES' or '$rel', which name the docs tree and a relative path) and a URL
# that names a wiki or a release, including a GitLab '/-/wikis' path.
POINTER_LIKE_RE = re.compile(
    r"\bv\d[\w.-]*\.md\b"
    r"|\brelease[-_ ]?notes?\b"
    r"|\breleases?[/\\]|[/\\]releases?\b"
    r"|\$\{?(?:[A-Za-z0-9]*_)*(?:rel(?:eases?)?_?(?:docs?|notes?)|releases?|notes?|changelog)(?![A-Za-z0-9])"
    r"|https?://[^\s\"'<>]*(?:wiki|release)|/-/wikis?\b",
    re.IGNORECASE,
)
TAG_CORE_RE = re.compile(r"v(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?")
CURSOR_WORD_RE = re.compile(r"\bCursor\b")
# SEC-T731-02: CommonMark ends a line only at \n, \r\n or \r; str.splitlines() also splits at
# \v, \f, \x1c-\x1e, \x85, U+2028 and U+2029, which would start a line early.
LINE_END_RE = re.compile(r"\r\n|\r|\n")
# SEC-T751-08: the blockquote markers before a line that may belong to a GFM table (see ``may_be_table_line``).
QUOTE_PREFIX_RE = re.compile(r"[ \t]*(?:>[ \t]*)*")
DELIMITER_CELL_RE = re.compile(r":?-+:?")


# The characters str.splitlines() treats as a line end and neither CommonMark nor a shell does. A checked
# document (SEC-T731-02) or scripts/install.sh (SEC-T731-07) that holds one fails the gate, so none of them
# splits a line in two for a check: a pointer split from the word "Cursor" would drop the Cursor requirement.
NON_COMMONMARK_BREAK_RE = re.compile("[\v\f\x1c\x1d\x1e\x85\u2028\u2029]")


def markdown_lines(text: str) -> list[str]:
    """The lines of ``text`` as CommonMark splits them (SEC-T731-02); a trailing newline gives a last ''."""
    return LINE_END_RE.split(text)
# SEC-T715-04: the characters check-release-tag-tree.py strips from what it prints (C0/C1 controls,
# the bidi controls and marks, zero-width characters and the BOM).
UNSAFE_RE = re.compile("[\x00-\x1f\x7f-\x9f\u061c\u200b-\u200f\u2028\u2029\u202a-\u202e\u2060-\u2069\ufeff]")
MIGRATION_POINTER_HELP = """\
Migration pointers (T703, SEC-T662-01). Every docs/releases/v*.md path named in
scripts/install.sh, and every "vX.Y.Z release notes" it names, must exist in the tree.
A line that names a release document in any other form fails the gate: write the
literal path docs/releases/vX.Y.Z.md (SEC-T703-02). Such forms are a 'releases' path
segment without the literal path (doc/releases, releases/v, a missing patch number),
'release notes' or 'release-notes' without a version, a versioned file name alone
(v9.0.0.md), a shell variable named for a release document ("$REL_DOC") and a URL
that names a wiki or a release (SEC-T715-01). A document named, by path or as
"vX.Y.Z release notes", on an install.sh line that contains the word "Cursor" must
carry a Cursor migration item (SEC-T715-02).
Anchor: the gate reads the document with markdown-it-py's CommonMark parser (T739). The
section is the first top-level level 2 heading whose text is exactly 'Migration Guide',
in ATX or setext form. It ends at the next top-level level 1 or 2 heading, in either
form. A heading inside a blockquote or a list neither opens nor ends it. An anchor is,
in that section, with text that contains the word "Cursor" (case-sensitive), either:
  - a top-level heading of level 3 to 6, for example '### M-3. Cursor removed';
  - a paragraph, top-level or with only list containers around it, that opens with a
    '**' strong span, for example '**Migration Guide item M-3. Cursor is no longer
    supported.**'. Only the text inside that span counts.
Text means text and inline code, with a line break read as a space. An image's alt text
never counts. What the parser reads as code, an HTML comment or a raw HTML block is not
an anchor (SEC-T703-01, SEC-T715-03). '__bold__', an anchor in a blockquote and a heading
in a list do not count either.
HTML (SEC-T745-03, SEC-T739-02, SEC-T739-03): the gate does not balance tags, so it refuses
rather than models. A release document the gate reads may hold no HTML other than comments,
anywhere, at any depth, before or after an anchor: no raw HTML block and no inline tag, such
as '<details>', 'text <div hidden>' or '<style>', even if the tag closes itself. The parser
decides what is HTML, so prose such as <your-project> outside code counts too: put it in a
code span. The document is refused, as below, and a direct call of the anchor check gives
False for it. An anchor that holds a tag does not count either, on either side of the word,
as in '**<span hidden>Cursor</span>**'. A comment is allowed and its text does not count; a
tag in a code span is code, not HTML, and neither is an image's alt text.
Nesting (SEC-T739-09): the parser stops at 20 nested levels (maxNesting), where a list
item counts as two. In a list it skips the rest of the document, or of the blockquote around
the list, and in a blockquote the rest of that blockquote, so no HTML, anchor or verdict
there has tokens. The gate therefore refuses a document that reaches the limit, as below. A
paragraph one level short of it counts too, though nothing is skipped there. On a direct
call no anchor that deep or later counts, which fails closed.
A refused document: a release document the gate reads, which is the tag's own and any
named on a line with the word "Cursor", is refused, naming its path, in six cases, in this
order. If it is longer than 131072 characters, before any parsing (SEC-T745-01). If a line
is longer than 65536 characters, named with its number and no content, before any parsing
(TD-T739-01). If it opens with '---', '+++' or ';;;', optionally after a BOM, white space or
a 'coding:' line, because GitLab may read what follows as front matter and hide it, in the
Release description too (unverified) (SEC-T739-04). If it reaches the nesting limit, named
with the line of the block that does and no content (SEC-T739-09). If the parser finds HTML other than
comments, named with the line its block starts on and no content (SEC-T745-03). If a paragraph
that may be a GFM table (a line starts with '|' or is a delimiter row) holds a code span with
'|' and a code span with '<', the same span or two, named with its first line: the commonmark preset has no tables, and GitLab
may split the span at the '|' (unverified), so this fails closed (SEC-T751-08). Then, for a text holding
a '|', the same text is parsed a second time with the GFM table rule, and the nesting and HTML rules apply to
that parse too (SEC-T751-08, T887); it adds a second parse, about the same cost as the first if the table rule costs no more (not measured). A refused
document is not checked for links (SEC-T751-06).
Time (SEC-T745-01): the cap limits the parser's time and does not make it small; the job's
timeout is what stops a run. Measured on 2026-11-06 on one machine, with markdown-it-py 4.2.0
and the whole gate on one crafted document at the cap: the worst of 41 shapes tried, unclosed
'<?' repeated in one paragraph of 1 KB lines, took 48 s. That is a measurement, not a bound:
another machine or a shape not tried may differ, and each document parsed adds its own time.
scripts/install.sh must hold no CR, CRLF included: a shell does not end a line at a CR,
and the gate's per-line rules would. The gate refuses it from the unconverted text and
names the line (SEC-T738-02).
What stays open. The gate reads CommonMark, and GitLab's renderer may differ (unverified,
SEC-T716-03). The install.sh rules are per line and do not defend against a
crafted script: they catch an omission on one line, and a pointer on a line without the
word "Cursor" needs no item. A document named only on such lines, other than the tag's
own, is checked for existence only: the gate does not read it, so none of these rules
reaches it (SEC-T741-07).
Newer versions: a pointer to a version (major.minor.patch, any pre-release suffix
ignored) newer than the tag being verified is an error, because the tagged tree points
users to a document it does not ship (SEC-T703-03). --allow-newer-pointers turns that
error into a printed note; it exists for verifying a past tag on a later tree (tests)
and is not used by the CI job. A tag that is not vX.Y.Z[-pre] enforces every pointer.
Encoding (SEC-T739-01): every file the gate reads in this process must be valid UTF-8.
The gate exits 1 on the first one that is not, naming its path and the file offset of the
first invalid byte and never its content, and no check runs on that file. Newlines are
read as before: CRLF and CR become LF, apart from the install.sh rule above.
scripts/check-version-consistency.py runs as a child process with its own reads, and this
does not cover them.
Verdict sections (T747, SEC-T739-07): '## Gate Verdicts' and '## RELEASE VERDICT' are found
with the same parser. A section starts at the first top-level level 2 heading whose text is
exactly its name, in ATX or setext form, and ends at the next top-level level 1 or 2 heading
whose text is not empty, in either form; if that is a setext or '# ' heading, that is an error
(SEC-T748-03). Text is as above, and a heading has text only if it holds a letter or digit
that renders (SEC-T748-12), so a heading such as '## &#32;', '## <!-- x -->' or '## ---' does
not end a section. Nor does one holding only format characters such as U+200B or fillers such
as U+3164, or, on a direct call (the gate refuses the document first), one holding any HTML
other than comments. Such a heading's own line is still read. A section is empty if it holds nothing but closed fences and headings with no text
before the next top-level level 1 or 2 heading with text. A second top-level heading with the same name is an
error, and so are a heading at any level or depth that reads as the name (case, white space and
format characters ignored) but is not the real form (SEC-T748-05), the heading's raw line in a
block that is no heading, such as a ~~~ fence (SEC-T748-04), and, on a direct call, the heading's
line inside an HTML block other than comments. Only the lines of a closed ``` fence, at any depth, do not count. An indented code
block, a ~~~ fence, an unclosed fence and a fence whose last line has trailing text or too
few backticks are read like any other lines, and so are HTML lines, so inside a section a
hidden 'pending' still fails; above a section it does not. Fields: a line is a field if it is
a list item ('-', '*', '+', '1.' or '1)', also inside '>' blockquote markers) of the form
'label: value'. Plain text, headings and table rows are not fields; only the placeholder
markers are looked for in them. A value is read with its entities resolved and '*', '_', '`',
'~', brackets and quotes stripped at its ends; an empty value takes the list items right under
it as its value (SEC-T748-06). RELEASE VERDICT must be a real top-level heading. Gate Verdicts
is optional, but a '## Gate Verdicts' line at column 0 with no real heading is an error, so a
section swallowed by an unclosed fence or comment fails. On a direct call, past the nesting
limit the parser gives no tokens: a section with no later heading runs to the end of the
document, which fails closed, and a heading there is absent, which fails closed for RELEASE
VERDICT only; an absent Gate Verdicts is not checked."""

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
# SEC-T751-06: no "[" in the text, so a run of "[" costs linear time, not quadratic. T887 (SEC-T885-01): no "(" or
# line break in the target, so each attempt stops at the next "(" and a run of "[a](" costs linear time too.
LINK_RE = re.compile(r"\[[^\[\]]+\]\(([^()\n]+)\)")


class NotUtf8Error(Exception):
    """A file the gate reads is not valid UTF-8. The message holds its path and an offset, never its content."""


def read_strict(path: Path, keep_cr: bool = False) -> str:
    """The text of ``path``, or NotUtf8Error (SEC-T739-01). Every read in this process goes through here.

    The whole file is decoded at once, so the offset counts from the start of the file and nothing partly decoded
    is ever returned. The newlines are translated as text mode translates them, unless ``keep_cr`` asks for the text
    as the file holds it, which is how a CR in install.sh is seen at all (SEC-T738-02).
    """
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as failure:
        shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        raise NotUtf8Error(
            f"{shown} is not valid UTF-8: the first invalid byte is at file offset {failure.start} (from 0); "
            "the gate refuses this file, fix its encoding (SEC-T739-01)"
        ) from None
    return text if keep_cr else text.replace("\r\n", "\n").replace("\r", "\n")


def normalize_target(current_file: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
        return None

    target = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not target:
        return None

    # Wiki slug links such as [Quick Start](quick-start)
    if current_file.parts[:2] == ("docs", "wiki"):
        if "/" not in target and not target.endswith(".md"):
            return ROOT / "docs" / "wiki" / f"{target}.md"

    return (ROOT / current_file.parent / target).resolve()


def strip_code(text: str) -> str:
    text = FENCED_CODE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


@functools.lru_cache(maxsize=None)
def markdown_tokens(text: str, tables: bool = False) -> list | None:
    """The tokens of ``text``, or None over MAX_DOCUMENT_CHARS or for a line over MAX_LINE_CHARS: never parsed.

    SEC-T745-01, TD-T739-01: the limits are checked here, so no route reaches the parser without them.

    The only call of the parser. Every text is remembered, not only the last: check_migration_pointers reads the
    pointed documents in sorted order and check_release_brief reads the tag's own after them, so with v9.0.0 and
    v10.0.0 both pointed to, a cache of one would parse v10.0.0 twice and double SEC-T745-01's worst case. A run holds
    few documents and ends. The list is shared, so a caller must not change it. Pass ``tables`` by position, so the
    cache holds one entry per text and kind.

    ``tables`` (T887, SEC-T751-08) enables the GFM ``table`` rule; only ``table_html_refusal`` reads those tokens. GFM
    splits a table cell at every unescaped '|', inside a code span too, and parses each cell on its own, so a '|' in one
    span can leave a later span's '<b>' as a live tag; markdown-it-py's table rule splits cells the same way. Not
    confirmed against GitLab (no GitLab call).
    """
    if len(text) > MAX_DOCUMENT_CHARS or long_line_number(text) is not None:
        return None
    parser = MarkdownIt("commonmark", {"maxNesting": MAX_NESTING})
    return (parser.enable("table") if tables else parser).parse(text)


def heading_text(tokens: list, index: int) -> str:
    """The text of the heading whose ``heading_open`` is ``tokens[index]``: its inline token follows it."""
    return inline_text(tokens[index + 1].children or []).strip()


def section_heading_indexes(tokens: list, title: str) -> list[int]:
    """The index of each top-level level 2 ``heading_open`` whose text is exactly ``title``, in ATX or setext form."""
    return [
        index for index, token in enumerate(tokens)
        if token.type == "heading_open" and token.level == 0 and token.tag == "h2"
        and heading_text(tokens, index) == title
    ]


def is_top_heading(token) -> bool:
    """``token`` opens a top-level heading of level 1 or 2."""
    return token.type == "heading_open" and token.level == 0 and token.tag in ("h1", "h2")


def is_visible_char(char: str) -> bool:
    """``char`` is a letter or digit that renders as something (SEC-T748-12): an allowlist, not a list of what is hidden.

    Format characters (U+200B, U+00AD, U+2060), white space and punctuation are not alphanumeric; INVISIBLE_LETTERS
    are, and render as nothing. A heading of punctuation or symbols alone therefore counts as having no text.
    """
    return char.isalnum() and char not in INVISIBLE_LETTERS


def heading_has_text(tokens: list, index: int) -> bool:
    """The heading at ``tokens[index]`` holds a visible character (``is_visible_char``; SEC-T748-02, -12)."""
    return any(is_visible_char(char) for char in heading_text(tokens, index))


def folded(text: str) -> str:
    """``text`` as a reader may take it (SEC-T748-05): case folded first, then compatibility forms such as full-width
    letters decomposed (NFKD), format characters and combining marks dropped, invisible letters read as a blank, the rest
    recomposed (NFKC), case folded again (SEC-T894-01: a mathematical or letterlike capital only becomes a capital 'V' at
    the NFKD step, after the first fold) and white space (``&nbsp;``) collapsed.

    The order matters (SEC-T888-02(a)): case folding first makes 'İ' an 'i' and a U+0307, which the drop then removes,
    so it reads as 'I' and the folded text keeps the length of the name; ligatures such as U+FB01 and 'ǆ' expand the
    same way. Folding last left that U+0307 in the text."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    kept = "".join(" " if c in INVISIBLE_LETTERS else c for c in decomposed
                   if unicodedata.category(c) not in ("Cf", "Mn", "Me") or c in INVISIBLE_LETTERS)
    return " ".join(unicodedata.normalize("NFKC", kept).casefold().split())


def reads_as(text: str, title: str) -> bool:
    """``text`` folded reads as ``title`` folded, where a non-ASCII letter may stand for any letter (SEC-T885-02, T887).

    A wildcard, not a confusables table: a Cyrillic 'Е' or a Greek 'Ε' passes for 'E', and so does any other letter
    from outside ASCII, which fails closed. The names this is called with are ASCII."""
    shown, name = folded(text), folded(title)
    return len(shown) == len(name) and all(
        a == b or (not a.isascii() and a.isalpha() and b.isalpha()) for a, b in zip(shown, name))


def look_alike_heading_lines(tokens: list, title: str) -> list[int]:
    """The line of each heading, at any level or depth, that reads as ``title`` but is not its real form (SEC-T748-05,
    SEC-T885-02)."""
    real = set(section_heading_indexes(tokens, title))
    return [
        token.map[0] + 1 for index, token in enumerate(tokens)
        if token.type == "heading_open" and index not in real and reads_as(heading_text(tokens, index), title)
    ]


def heading_is_visible(tokens: list, index: int) -> bool:
    """The heading at ``tokens[index]`` ends a section for the field scan: it has text and holds no live HTML.

    HTML such as ``<span hidden>x</span>`` may hide a heading, so the scan reads on past it, which fails closed.
    """
    return heading_has_text(tokens, index) and not holds_live_html(tokens[index + 1])


def section_line_span(tokens: list, start: int, line_count: int) -> tuple[int, int]:
    """The source lines ``[first, end)`` below the heading at ``tokens[start]``.

    They end at the next visible top-level level 1 or 2 heading, so a heading that renders as nothing does not end a
    section. A later heading past the nesting limit has no token, so the section runs on: that fails closed.
    """
    first = tokens[start].map[1]
    index = section_end_index(tokens, start)
    return (first, line_count) if index is None else (first, tokens[index].map[0])


def section_end_index(tokens: list, start: int) -> int | None:
    """The index of the heading that ends the section at ``tokens[start]`` for the field scan; None at the end."""
    return next(
        (index for index in range(start + 1, len(tokens)) if is_top_heading(tokens[index]) and heading_is_visible(tokens, index)),
        None,
    )


def stray_heading_lines(tokens: list, lines: list[str], heading: str) -> list[int]:
    """Lines that are exactly ``heading`` at column 0 and are no heading, code of a closed ``` fence or HTML (SEC-T748-04).

    Such a line stands in a ~~~ fence (shown as code), an unclosed fence, a reference definition's title or anything
    else the parser does not read as a heading, so a reader may see a second verdict there. An HTML block other than
    comments has its own message (``html_block_holds_line``); a comment is hidden (ruling 3) and stays allowed.
    """
    covered = {token.map[0] for token in tokens if token.type == "heading_open" and token.map}
    for token in tokens:
        if token.map and (is_closed_backtick_fence(token, lines) or token.type == "html_block"):
            covered.update(range(*token.map))
    return [number + 1 for number, line in enumerate(lines) if line.rstrip(" \t") == heading and number not in covered]


def html_block_holds_line(tokens: list, line: str) -> bool:
    """An HTML block other than comments holds ``line``: a reader may see it, and the parser reads no heading in it."""
    return any(
        token.type == "html_block" and holds_live_html(token)
        and line in (raw.rstrip(" \t") for raw in token.content.split("\n"))
        for token in tokens
    )


def is_closed_backtick_fence(token, lines: list[str]) -> bool:
    """``token`` is a ``` fence that the parser closed.

    The parser decides what closes a fence (length, indent, containers, trailing text), and it records the decision
    only in the numbers: ``map`` holds the opening line, the content lines and a closing line if there is one, while
    ``content`` holds the content lines alone, so two lines more than the content means closed. The last content line
    of a document with no final newline has no LF. The closing line must also end with the opening markup, as a closing
    fence does (SEC-T748-07): if the numbers and the source disagree, the fence is read, which fails closed. Tested on
    the locked version (``ci/requirements-release.txt``); CI runs no other version.
    """
    if token.type != "fence" or not token.markup.startswith("`") or not token.map:
        return False
    first, end = token.map
    content_lines = token.content.count("\n") + (1 if token.content and not token.content.endswith("\n") else 0)
    return end - first - content_lines == 2 and lines[end - 1].rstrip(" \t").endswith(token.markup)


def section_text(text: str, heading: str) -> str:
    """The source of the first real section ``heading`` (``## name``) as defined in MIGRATION_POINTER_HELP; '' when absent.

    The lines of a closed ``` fence are blanked, not dropped, so the line after it is not read as following the line
    before it. Nothing else is skipped: a heading that does not end the section is read too (SEC-T748-10). The lines are split where the parser splits them, so that its ``map`` numbers fit them. A character that only
    str.splitlines() treats as a line end (SEC-T731-02) cannot move a line here.
    """
    tokens = markdown_tokens(text) or []
    starts = section_heading_indexes(tokens, heading[3:])
    if not starts:
        return ""
    lines = markdown_lines(text)
    first, end = section_line_span(tokens, starts[0], len(lines))
    code = {number for token in tokens if is_closed_backtick_fence(token, lines) for number in range(*token.map)}
    kept = lines[first:end]
    return "\n".join("" if first + i in code else line.rstrip(" \t") for i, line in enumerate(kept))


def section_is_empty(tokens: list, text: str, start: int) -> bool:
    """The real section at ``tokens[start]`` holds nothing but closed fences and headings with no text.

    It ends here at the next top-level heading with text, even one holding live HTML: what follows such a heading is
    not the verdict's content (SEC-T748-01, -11). The field scan reads further, so the two spans differ on purpose.
    """
    lines = markdown_lines(text)
    first = tokens[start].map[1]
    end = next(
        (tokens[i].map[0] for i in range(start + 1, len(tokens)) if is_top_heading(tokens[i]) and heading_has_text(tokens, i)),
        len(lines),
    )
    skipped = {
        number for index, token in enumerate(tokens)
        if is_closed_backtick_fence(token, lines) or (is_top_heading(token) and not heading_has_text(tokens, index))
        for number in range(*token.map)
    }
    return not any(lines[number].strip() for number in range(first, end) if number not in skipped)


def verdict_placeholder_problems(text: str) -> list[str]:
    """Problems for each unfilled row or field in the Gate Verdicts / RELEASE VERDICT sections, and a repeated heading."""
    tokens = markdown_tokens(text)
    if tokens is None:
        return [
            f"the document is longer than {MAX_DOCUMENT_CHARS} characters or a line is longer than {MAX_LINE_CHARS} "
            "characters, so the verdict sections were not read (SEC-T745-01, TD-T739-01)"
        ]
    problems: list[str] = []
    for heading in VERDICT_SECTIONS:
        problems.extend(_heading_problems(tokens, text, heading))
        lines = section_text(text, heading).splitlines()
        for i, line in enumerate(lines):
            problems.extend(_line_problems(heading[3:], line, sub_items(lines, i)))
    return problems


def _heading_problems(tokens: list, text: str, heading: str) -> list[str]:
    """Problems of the heading of one verdict section: repeated, look-alike, quoted, empty, or a weak end."""
    title = heading[3:]
    starts = section_heading_indexes(tokens, title)
    problems: list[str] = []
    if len(starts) > 1:
        problems.append(f"{title}: {len(starts)} top-level headings have this name; the gate reads the first, so keep one")
    problems.extend(
        f"{title}: the heading on line {number} reads as this section's name but is not a top-level '## {title}' heading; "
        "rename it or make it the real one (SEC-T748-05)"
        for number in look_alike_heading_lines(tokens, title)
    )
    if starts and html_block_holds_line(tokens, heading):
        problems.append(f"{title}: its heading line is inside an HTML block, which a reader may see; move it out")
    if starts:
        problems.extend(
            f"{title}: line {number} repeats the heading line in a block that is no heading, such as a ~~~ fence, which a "
            "reader may see; remove it (SEC-T748-04)"
            for number in stray_heading_lines(tokens, markdown_lines(text), heading)
        )
    if section_is_empty(tokens, text, starts[0]) if starts else re.search(rf"^{re.escape(heading)}", text, re.M):
        problems.append(f"{title}: the heading is present but the section is empty or only inside a code block")
    end = section_end_index(tokens, starts[0]) if starts else None
    if end is not None and tokens[end].markup != "##":
        problems.append(
            f"{title}: the section ends at a setext or '# ' heading on line {tokens[end].map[0] + 1}, which may be a "
            "paragraph above a '---' line; end it with a '## ' heading (SEC-T748-03)"
        )
    return problems


def sub_items(lines: list[str], index: int) -> list[str] | None:
    """The texts of the list items nested under the field on ``lines[index]``; None when that line is no field.

    A sub-item is a list item whose marker stands further right than the field's, on the lines right after it; the first
    other line, a blank one included, ends them, as before (a blanked code block must not join the lines around it).
    SEC-T748-06: an empty field's sub-items are its value.
    """
    field = FIELD_RE.match(lines[index])
    if field is None:
        return None
    found: list[str] = []
    for line in lines[index + 1:]:
        item = LIST_ITEM_RE.match(line)
        if item is None or item.start("marker") <= field.start("marker"):
            break
        found.append(item.group("text") or "")
    return found


def normalized_value(raw: str) -> str:
    """A field value as tested (SEC-T748-06): entities resolved, '*' and '`' removed, VALUE_EDGE_CHARS stripped."""
    return html.unescape(raw).replace("*", "").replace("`", "").strip(VALUE_EDGE_CHARS)


def is_pending(value: str) -> bool:
    """A normalized value that still says pending."""
    return value.lower().startswith("pending") or PENDING_ON_RE.search(value) is not None


def _line_problems(section: str, line: str, nested: list[str] | None = None) -> list[str]:
    """Placeholder problems of one line of a verdict section (``nested``: the texts of the sub-items under it)."""
    found = [
        f"{section}: unfilled placeholder {marker!r}: {line.strip()[:80]}"
        for marker in (*PLACEHOLDER_MARKERS, *TEMPLATE_PROSE_MARKERS)
        if marker in line
    ]
    if WORD_MARKER_RE.search(line):
        found.append(f"{section}: unfilled placeholder TBD/TODO: {line.strip()[:80]}")
    field = FIELD_RE.match(line)
    if not field:
        return found
    value = normalized_value(field.group("value"))
    if not value:
        values = [normalized_value(text) for text in nested or []]
        if not any(values):
            found.append(f"{section}: field has no value: {line.strip()[:80]}")
        if any(is_pending(item) for item in values):
            found.append(f"{section}: value is still pending in a sub-item: {line.strip()[:80]}")
    if is_pending(value):
        found.append(f"{section}: value is still pending: {line.strip()[:80]}")
    return found


def check_links(file_path: Path, errors: list[str]) -> None:
    text = read_strict(file_path)
    visible_text = strip_code(text)

    rel = file_path.relative_to(ROOT)
    for match in LINK_RE.finditer(visible_text):
        raw_target = match.group(1)
        normalized = normalize_target(rel, raw_target)
        if normalized is None:
            continue
        if not normalized.exists():
            errors.append(f"broken link in {rel}: {raw_target}")


def check_version_consistency(errors: list[str]) -> None:
    """Run scripts/check-version-consistency.py (T400, Gate G0) as a subprocess and
    fold any failure into `errors`, so a release tag cannot be cut while any
    non-archived doc still references a stale release.

    Fails loudly (appends to `errors`) rather than silently skipping if the script
    is missing or cannot be executed at all — an environment where T400 hasn't
    landed should not be treated as a passing version-consistency check.
    """
    script = ROOT / "scripts" / "check-version-consistency.py"
    if not script.is_file():
        errors.append(
            f"cannot run version-consistency check: missing {script.relative_to(ROOT)}"
        )
        return

    try:
        result = subprocess.run(
            [sys.executable, "-I", str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        errors.append(f"cannot run version-consistency check: {exc}")
        return

    if result.returncode == 0:
        return

    errors.append(
        "version-consistency check failed "
        f"(scripts/check-version-consistency.py exited {result.returncode}):"
    )
    for line in (result.stdout + result.stderr).splitlines():
        if line.strip():
            errors.append(f"  {line}")


# T717-D2: the marker is a whole token. A tag character after it (``-rc.1``, ``.1``, a further digit) means a
# different tag, so a leftover ``Latest release: v1.2.3-rc.1`` does not satisfy ``v1.2.3``; a sentence-ending
# period or a closing bracket after the tag is still accepted.
MARKER_END = r"(?![0-9A-Za-z]|[.-][0-9A-Za-z])"


def has_marker(text: str, marker: str) -> bool:
    """``marker`` occurs in ``text`` as a whole token (see MARKER_END)."""
    return re.search(re.escape(marker) + MARKER_END, text) is not None


def check_markers(marker: str, errors: list[str]) -> None:
    """Every MARKER_FILES entry carries the `Latest release: <tag>` marker as a whole token."""
    for relative in MARKER_FILES:
        text = read_strict(ROOT / relative)
        if not has_marker(text, marker):
            errors.append(f"missing marker '{marker}' in {relative}")


def check_section_requirements(errors: list[str]) -> None:
    """Every SECTION_REQUIREMENTS file holds each of its required snippets."""
    for relative, required_snippets in SECTION_REQUIREMENTS.items():
        text = read_strict(ROOT / relative)
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f"missing required content in {relative}: {snippet}")


def check_line_breaks(relatives: list[Path], errors: list[str]) -> None:
    """Each existing file in ``relatives`` that holds a NON_COMMONMARK_BREAK_RE character is an error.

    The error names the file, the line (CommonMark lines) and the code point of the first one,
    never the character itself.
    """
    for relative in relatives:
        path = ROOT / relative
        if not path.is_file():
            continue
        text = read_strict(path)
        found = NON_COMMONMARK_BREAK_RE.search(text)
        if found is None:
            continue
        number = len(LINE_END_RE.findall(text, 0, found.start())) + 1
        errors.append(
            f"{relative}:{number} holds U+{ord(found.group(0)):04X}, which str.splitlines() treats as a line end "
            "and neither Markdown nor a shell does; remove it (SEC-T731-02, SEC-T731-07)"
        )


def long_line_number(text: str) -> int | None:
    """The number of the first line of ``text`` longer than MAX_LINE_CHARS; None when there is none (TD-T739-01)."""
    for number, line in enumerate(text.split("\n"), start=1):
        if len(line) > MAX_LINE_CHARS:
            return number
    return None


def opens_with_front_matter(text: str) -> bool:
    """``text`` opens as front matter does (SEC-T739-04), in linear time (SEC-T745-02): with or without a "coding:" line."""
    text = text.removeprefix("\ufeff")
    first, _, rest = text.partition("\n")
    if "coding:" in first and FRONT_MATTER_BODY_RE.match(rest) is not None:
        return True
    return FRONT_MATTER_BODY_RE.match(text) is not None


def live_html_line(tokens: list) -> int | None:
    """The line on which the first block holding HTML other than comments starts; None when there is none (SEC-T745-03)."""
    for token in tokens:
        if holds_live_html(token):
            return token.map[0] + 1
    return None


def may_be_table_line(line: str) -> bool:
    """``line`` starts with '|' after blockquote markers, or is a delimiter row such as '--- | :---:' (SEC-T751-08)."""
    rest = line[QUOTE_PREFIX_RE.match(line).end():].strip(" \t")
    if rest.startswith("|"):
        return True
    cells = rest.split("|")
    return "|" in rest and all(DELIMITER_CELL_RE.fullmatch(cell.strip(" \t")) for cell in cells if cell.strip(" \t"))


def table_code_html_line(tokens: list, lines: list[str]) -> int | None:
    """The first line of a paragraph that may be a GFM table and holds a code span with '|' and a code span with '<',
    the same span or two (SEC-T751-08; T887 widened it from one span to the paragraph).

    The commonmark preset has no tables. In a GFM table a '|' inside a code span may end the cell, and the backticks
    after it pair anew, so a later span's '<' could be read as a live tag (`` | `a|` `<b>` | ``). The table-rule parse
    (``markdown_tokens(text, True)``) catches a real table; this rule also fails closed where the cell counts or another
    detail decide whether a renderer sees a table (GitLab's rendering is not confirmed, no GitLab call). A paragraph
    with no code span holding '|' cannot be split inside a span, so '<dir>' in a table cell's code span stays allowed
    (v8.0.0.md has such cells). A paragraph may be a table if one of its lines starts with '|' (after blockquote
    markers) or is a delimiter row.
    """
    for index, token in enumerate(tokens):
        if token.type != "inline" or not token.map or tokens[index - 1].type != "paragraph_open":
            continue
        spans = [child.content for child in token.children or [] if child.type == "code_inline"]
        if not (any("|" in span for span in spans) and any("<" in span for span in spans)):
            continue
        if any(may_be_table_line(line) for line in lines[token.map[0]:token.map[1]]):
            return token.map[0] + 1
    return None


def nesting_limit_line(tokens: list) -> int | None:
    """The line of the first block that reaches the parser's nesting limit; None when none does (SEC-T739-09).

    At the limit the block parser reads no further in that container, and a list takes the rest of what holds it along,
    so nothing there has tokens. Only a pushed token with ``nesting`` 1 raises the level, so the opener that reaches the
    limit is always in the list. A paragraph or heading one level short counts too, though nothing is skipped: fail closed.
    A table cell opener has no line map (T887), so it takes the line of the last token that has one, its row.
    """
    line = 1
    for token in tokens:
        if token.map:
            line = token.map[0] + 1
        if token.level + token.nesting >= MAX_NESTING:
            return line
    return None


def document_refusal(relative: Path, text: str) -> str | None:
    """Why the gate refuses this release document; None when it does not.

    The size and line limits and the front matter check read the text as it is, in that order, before any parsing. Only
    the nesting and HTML rules then parse it, through ``markdown_tokens``, which remembers the tokens, so the checks that
    follow do not parse it again. Nesting comes first because the tokens stop at that limit: whatever lies past it, the
    document is refused, so the HTML rule never passes a text it could not read. This is not the first read of the tag's own document: ``check_line_breaks`` runs before it, and
    ``check_links`` runs after it only if it is not refused (SEC-T751-06). Each message holds the path and at most a line number, never the content.
    """
    if len(text) > MAX_DOCUMENT_CHARS:
        return (
            f"{relative} is longer than {MAX_DOCUMENT_CHARS} characters; the gate refuses it before parsing, because "
            "parsing time grows worse than linearly with the size of a paragraph (SEC-T745-01)"
        )
    number = long_line_number(text)
    if number is not None:
        return (
            f"{relative}:{number} is longer than {MAX_LINE_CHARS} characters; the gate refuses it before parsing, "
            "because parsing time grows worse than linearly with such a line (TD-T739-01)"
        )
    if opens_with_front_matter(text):
        return (
            f"{relative} opens with a front matter delimiter ('---', '+++' or ';;;'); GitLab may read what follows as "
            "front matter and hide it, so start the document with '# Release' (SEC-T739-04)"
        )
    return parsed_refusal(relative, text)


def parsed_refusal(relative: Path, text: str) -> str | None:
    """The refusals that read tokens, for ``document_refusal``, in order: nesting, HTML, HTML in a table (SEC-T751-08).

    The table-rule parse is a second parse of the same text under the same limits, only of a text holding a '|'; it adds a
    second parse, about the same cost as the first if the table rule costs no more (not measured). Its nesting is checked too, since a table adds levels and its tokens stop at the limit.
    """
    tokens = markdown_tokens(text)
    number = nesting_limit_line(tokens)
    if number is not None:
        return (
            f"{relative}:{number} reaches the parser's limit of {MAX_NESTING} nested levels, where a list item counts as "
            "two; the gate cannot read what lies past it, so nest less (SEC-T739-09)"
        )
    number = live_html_line(tokens)
    if number is not None:
        return (
            f"{relative}:{number} the block that starts on this line holds HTML other than comments, which can hide text "
            "from a reader; a release document may hold none, so remove the tag or replace the placeholder with its value, "
            "and put only literal text in a code span (SEC-T745-03)"
        )
    number = table_code_html_line(tokens, markdown_lines(text))
    if number is not None:
        return (
            f"{relative}:{number} the paragraph that starts on this line may be a table and holds a code span with '|' and "
            "a code span with '<'; the '|' may end the cell and leave a live tag, so take the '|' or the '<' out of the code "
            "spans, or take the line out of the table (SEC-T751-08)"
        )
    # A GFM table needs a '|' on its header line, so a text without one has no table and is not parsed again.
    return table_html_refusal(relative, markdown_tokens(text, True)) if "|" in text else None


def table_html_refusal(relative: Path, tokens: list) -> str | None:
    """SEC-T751-08 (T887): the nesting and HTML rules once more, on the parse with the GFM table rule enabled."""
    number = nesting_limit_line(tokens)
    if number is not None:
        return (
            f"{relative}:{number} read as GFM tables, the document reaches the parser's limit of {MAX_NESTING} nested "
            "levels, since a table adds levels; the gate cannot read what lies past it, so nest less (SEC-T751-08)"
        )
    number = live_html_line(tokens)
    if number is not None:
        return (
            f"{relative}:{number} read as a GFM table, the block that starts on this line holds HTML other than comments: "
            "a '|' inside a code span ends the cell, so a later span's '<' becomes a live tag; take the '|' out of the code "
            "span (SEC-T751-08)"
        )
    return None


def check_release_brief(tag: str, release_brief: Path, errors: list[str]) -> bool:
    """The release notes document has the required sections and no unfilled verdict. False when it is refused."""
    brief_text = read_strict(ROOT / release_brief)
    refusal = document_refusal(release_brief, brief_text)
    if refusal is not None:
        errors.append(refusal)
        return False
    if not has_marker(brief_text, f"Latest release: {tag}"):
        errors.append(f"missing required content in {release_brief}: Latest release: {tag}")
    tokens = markdown_tokens(brief_text) or []
    for snippet in ("## Install", "## Highlights"):  # SEC-T748-09: a real top-level heading, not a substring
        if not section_heading_indexes(tokens, snippet[3:]):
            errors.append(f"missing required content in {release_brief}: {snippet}")
    # Placement of the release gate VERDICT, declared by step 7 of
    # implementation/knowledge/commands/prepare-release.md: the release notes
    # document is the block's home. Presence of the section is checked here, as a real
    # top-level heading (T747); the field-level contract (11 fields, Status enum) is encoded
    # once, in the golden suite, and is deliberately not duplicated in this gate.
    if not section_heading_indexes(tokens, REQUIRED_VERDICT_SECTION[3:]):
        errors.append(f"missing required content in {release_brief}: {REQUIRED_VERDICT_SECTION}")

    for problem in verdict_placeholder_problems(brief_text):
        errors.append(f"unfilled verdict in {release_brief}: {problem}")
    return True


def install_sh_pointers(text: str) -> dict[str, bool]:
    """Each release document install.sh text names, mapped to whether a line naming it mentions Cursor.

    A ``docs/releases/vX.Y.Z.md`` path and a ``vX.Y.Z release notes`` phrase both name
    ``docs/releases/vX.Y.Z.md``; either form on a line with the word "Cursor" carries the
    Cursor-item requirement (SEC-T715-02: the phrase form used to be checked for existence only).
    """
    pointers: dict[str, bool] = {}
    for line in text.splitlines():
        cursor = CURSOR_WORD_RE.search(line) is not None
        paths = [m.group(0) for m in POINTER_RE.finditer(line)]
        paths += [f"docs/releases/{m.group('tag')}.md" for m in PROSE_POINTER_RE.finditer(line)]
        for path in paths:
            pointers[path] = pointers.get(path, False) or cursor
    return pointers


def unparsed_pointer_lines(text: str) -> list[tuple[int, str]]:
    """``(line number, line)`` for each line naming a release document in a form the pointer patterns do not parse."""
    unparsed: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        spans = [m.span() for pattern in (POINTER_RE, PROSE_POINTER_RE) for m in pattern.finditer(line)]
        for hit in POINTER_LIKE_RE.finditer(line):
            if not any(start <= hit.start() < end for start, end in spans):
                unparsed.append((number, line.strip()))
                break
    return unparsed


def tag_core(tag: str) -> tuple[int, int, int] | None:
    """``(major, minor, patch)`` of a ``vX.Y.Z[-pre]`` tag; None for any other string."""
    match = TAG_CORE_RE.fullmatch(tag)
    if match is None:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def pointer_applies(pointed_tag: str, tag: str) -> bool:
    """True unless the pointed version is newer than the tag being verified (fail-closed on an unparseable tag)."""
    pointed, verified = tag_core(pointed_tag), tag_core(tag)
    if pointed is None or verified is None:
        return True
    return pointed <= verified


def inline_text(children: list) -> str:
    """The text of inline tokens: ``text`` and ``code_inline``, a soft or hard break as a space, nothing else.

    An image's alt text and ``html_inline`` never count. The parser has already resolved entities and backslash
    escapes into ``text`` (both on markdown-it-py 3.0.0 and 4.2.0).
    """
    parts: list[str] = []
    for token in children:
        if token.type in ("text", "code_inline"):
            parts.append(token.content)
        elif token.type in ("softbreak", "hardbreak"):
            parts.append(" ")
    return "".join(parts)


def holds_only_comments(html: str) -> bool:
    """The raw HTML ``html`` is nothing but comments and white space (see COMMENTS_ONLY_RE)."""
    return COMMENTS_ONLY_RE.fullmatch(html) is not None


def anchor_text(children: list) -> str:
    """``inline_text`` of an anchor, or '' when it holds inline HTML other than a comment (SEC-T739-02).

    Only the flat list is walked: the tag inside a link is in it, and an image's alt text is not HTML, so what is
    nested in an ``image`` token is not looked at. A code span is ``code_inline``, an autolink is ``link_open``.
    """
    if any(token.type == "html_inline" and not holds_only_comments(token.content) for token in children):
        return ""
    return inline_text(children)


def bold_lead_text(children: list) -> str:
    """The text inside the ``**`` span that opens ``children``, or '' when no such span opens them.

    The parser emits an empty ``text`` token before a span at the start of a paragraph, so empty ones are skipped.
    ``__bold__`` is also ``strong_open``, and only its ``markup`` tells it apart. A span can nest another: its end
    is found by depth.
    """
    tokens = [token for token in children if token.type != "text" or token.content]
    if not tokens or tokens[0].type != "strong_open" or tokens[0].markup != "**":
        return ""
    depth = 0
    for index, token in enumerate(tokens):
        depth += {"strong_open": 1, "strong_close": -1}.get(token.type, 0)
        if depth == 0:
            return anchor_text(tokens[:index])
    return ""


def migration_section_span(tokens: list) -> tuple[int, int] | None:
    """Where the Migration Guide section lies, as MIGRATION_POINTER_HELP defines it: ``tokens[start:end]``, or None.

    ``level == 0`` keeps out a heading inside a blockquote or a list. A heading token is followed by its inline token,
    and ``start`` is that inline token of the title.
    """
    start: int | None = None
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.level != 0 or token.tag not in ("h1", "h2"):
            continue
        if start is not None:
            return start, index
        if token.tag == "h2" and inline_text(tokens[index + 1].children or []).strip() == MIGRATION_SECTION_TITLE:
            start = index + 1
    return None if start is None else (start, len(tokens))


def holds_live_html(token) -> bool:
    """A block token that is, or an inline token that holds, HTML other than comments (SEC-T739-02, -03).

    The token list is flat, so a list item or a blockquote needs no descent. An image's children are not walked: alt
    text is not HTML (see ``anchor_text``).
    """
    if token.type == "html_block":
        return not holds_only_comments(token.content)
    if token.type != "inline":
        return False
    return any(child.type == "html_inline" and not holds_only_comments(child.content) for child in token.children or [])


def has_cursor_migration_item(text: str) -> bool:
    """The Migration Guide section holds a heading or bold lead that names Cursor (see MIGRATION_POINTER_HELP).

    The commonmark preset has two block containers, blockquotes and lists, so "only list containers around it"
    means no open blockquote. ``paragraph_open`` is ``hidden`` in a tight list and is still rendered, so it counts.
    A paragraph or heading token is followed by its inline token. Without tag balancing nothing tells what live HTML
    leaves open, so any in the document, before or after an anchor, gives False (SEC-T745-03, SEC-T739-02, -03):
    ``document_refusal`` names it for the gate, and this holds for a direct call. A text over the limits is never parsed
    (SEC-T745-01, TD-T739-01): ``document_refusal`` names that too, and this keeps any other caller off the parser.
    """
    tokens = markdown_tokens(text)
    if tokens is None or live_html_line(tokens) is not None:
        return False
    span = migration_section_span(tokens)
    if span is None:
        return False
    start, end = span
    quotes = 0
    for index, token in enumerate(tokens[start:end], start):
        quotes += {"blockquote_open": 1, "blockquote_close": -1}.get(token.type, 0)
        anchor = ""
        if token.type == "heading_open" and token.level == 0 and token.tag in ("h3", "h4", "h5", "h6"):
            anchor = anchor_text(tokens[index + 1].children or [])
        elif token.type == "paragraph_open" and quotes == 0:
            anchor = bold_lead_text(tokens[index + 1].children or [])
        if CURSOR_WORD_RE.search(anchor):
            return True
    return False


def install_sh_cr_problem(raw: str) -> str | None:
    """The refusal of a CR in install.sh text read with ``keep_cr`` (SEC-T738-02), by line as a shell counts lines."""
    position = raw.find("\r")
    if position < 0:
        return None
    number = raw.count("\n", 0, position) + 1
    return (
        f"{INSTALL_SH}:{number} holds a CR (U+000D): a shell does not end a line there, and the gate's per-line rules "
        "would, so a pointer could be split from the word 'Cursor'; use LF line ends only (SEC-T738-02)"
    )


def cursor_item_problem(path: str) -> str | None:
    """Why the release document ``path``, named on a line with the word "Cursor", fails; None when it passes."""
    text = read_strict(ROOT / path)
    refusal = document_refusal(Path(path), text)
    if refusal is not None:
        return refusal
    if has_cursor_migration_item(text):
        return None
    return (
        f"{path} lacks its Cursor migration item ({INSTALL_SH} points users to it): add, under '{MIGRATION_SECTION}', "
        "a '### ... Cursor ...' heading or a paragraph that opens with a '**' span holding the word, optionally in a "
        "list"
    )


def check_migration_pointers(tag: str, errors: list[str], allow_newer: bool = False) -> None:
    """Every release document install.sh points users to exists and, if pointed to for Cursor, has the item.

    ``allow_newer`` (``--allow-newer-pointers``) reports a pointer newer than ``tag`` as a note instead of an error.
    """
    install = ROOT / INSTALL_SH
    if not install.is_file():
        return  # reported as a missing required file
    text = read_strict(install, keep_cr=True)
    cr_problem = install_sh_cr_problem(text)
    if cr_problem is not None:
        errors.append(cr_problem)
        return
    for number, line in unparsed_pointer_lines(text):
        errors.append(
            f"{INSTALL_SH}:{number} names a release document in a form the gate cannot check; "
            f"write the literal path docs/releases/vX.Y.Z.md: {line[:120]}"
        )
    for path, needs_cursor in sorted(install_sh_pointers(text).items()):
        if not pointer_applies(Path(path).stem, tag):
            message = f"{INSTALL_SH} points users to {path}, a version newer than {tag}, which this tag does not ship"
            if allow_newer:
                print(f"release-docs-verify: note: {printable(message)} (allowed by --allow-newer-pointers)")
            else:
                errors.append(f"{message}; remove the pointer or tag the newer release")
            continue
        document = ROOT / path
        if not document.is_file():
            errors.append(f"{INSTALL_SH} points users to {path}, which does not exist; write it before the tag is cut")
            continue
        problem = cursor_item_problem(path) if needs_cursor else None
        if problem is not None:
            errors.append(problem)


def printable(text: str) -> str:
    """``text`` with each UNSAFE_RE character replaced by '?', for the CI log (SEC-T715-04)."""
    return UNSAFE_RE.sub("?", text)


def print_errors(errors: list[str]) -> None:
    """Print each error as one ``release-docs-verify:`` line, made printable."""
    for error in errors:
        print(f"release-docs-verify: {printable(error)}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Release documentation verification gate.",
        epilog=MIGRATION_POINTER_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tag", required=True, help="Release tag, e.g. v1.0.1")
    parser.add_argument(
        "--allow-newer-pointers", action="store_true",
        help="report an install.sh pointer to a version newer than --tag as a note, not an error "
        "(for verifying a past tag on a later tree; never in CI)",
    )
    return parser.parse_args()


def run_checks(tag: str, allow_newer: bool, errors: list[str]) -> None:
    """Every check, in order, into ``errors``. A missing file or a pointer error ends the run before the others."""
    release_brief = release_brief_path(tag)
    required_for_tag = [*REQUIRED_FILES, release_brief]

    for relative in required_for_tag:
        absolute = ROOT / relative
        if not absolute.is_file():
            errors.append(f"missing required file: {relative}")
    check_migration_pointers(tag, errors, allow_newer)

    if errors:
        return

    check_markers(f"Latest release: {tag}", errors)
    check_line_breaks([*MARKER_FILES, release_brief, INSTALL_SH], errors)
    check_section_requirements(errors)
    read = check_release_brief(tag, release_brief, errors)

    for relative in required_for_tag:
        if relative != release_brief or read:  # SEC-T751-06: a refused document is read no further
            check_links(ROOT / relative, errors)

    check_version_consistency(errors)


def main() -> int:
    args = parse_arguments()
    if MarkdownIt is None:
        print_errors([PARSER_MISSING])
        return 1

    errors: list[str] = []
    try:
        run_checks(args.tag, args.allow_newer_pointers, errors)
    except NotUtf8Error as refused:  # ends the run: the errors so far are reported, and no later check runs
        errors.append(str(refused))

    if errors:
        print_errors(errors)
        return 1

    print("release-docs-verify: all documentation checks passed")
    marker = f"Latest release: {args.tag}"
    print(f"release-docs-verify: verified marker '{printable(marker)}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
