#!/usr/bin/env python3
"""Release documentation verification gate for emage.code.

Checks that required documentation exists, includes the current release marker,
contains key usage sections, and has resolvable local/internal links.

The release document's ``## Gate Verdicts`` and ``## RELEASE VERDICT`` sections must
also be filled in (TL-T649-12): a row or field that is still ``pending`` or carries a
template placeholder (``YYYY-MM-DD``, ``<count>``, ``<ISO-8601>``,
``<PASS/CONDITIONAL_PASS>``, the unfilled ``PASS | CONDITIONAL_PASS | FAIL``) fails
the gate. The gate does not require the Gate Verdicts section to exist (only the
RELEASE VERDICT section, as before) and does not check the field-level contract, which the
golden suite encodes.

Migration pointers (T703, SEC-T662-01): every ``docs/releases/v*.md`` path that
``scripts/install.sh`` names must exist, and a document named on an install.sh line that
mentions "Cursor" must carry its Cursor migration item. See ``MIGRATION_POINTER_HELP``
for the anchor, for what stays open, and for how a pointer to a version newer than the tag is treated.

The Cursor item is looked for with markdown-it-py (T739, plan-136), so the gate reads the same blocks as a
CommonMark renderer. Only ``has_cursor_migration_item`` uses it. ``main()`` refuses to run without it, on every
run; there is no fallback to line rules and no skip. The ``release-docs-gate`` job installs it from
``ci/requirements-release.txt``.

Every printed line passes through ``printable``: control, bidi and zero-width characters of an
``install.sh`` line, a release document or a tag become ``?`` in the CI log (SEC-T715-04).

Every file the gate reads in this process must be valid UTF-8 (SEC-T739-01): the gate exits 1 on the first one that is
not, naming its path and the file offset of the first invalid byte and never its content, and no check runs on that
file. Newlines are read as before: CRLF and CR become LF. ``scripts/check-version-consistency.py`` runs as a child
process with its own reads, and this does not cover them.

This gate cannot check that ``main`` already carries the release. That duty (merge the
release branch to ``develop`` and ``main`` before the tag, stated in CONTRIBUTING.md) is
enforced on the tag pipeline, without a grace window, by ``scripts/check-release-tag-tree.py``:
the tree of the tag's commit must equal the tree of ``origin/main``. It runs in the blocking
``main-develop-drift-gate`` job, next to ``scripts/check-main-develop-drift.py``, whose
one-release grace window applies only to ``main`` lagging ``develop`` (SEC-T685-03).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
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
PLACEHOLDER_MARKERS = (
    "YYYY-MM-DD",
    "<PASS/CONDITIONAL_PASS>",
    "<count>",
    "<ISO-8601>",
    "PASS | CONDITIONAL_PASS | FAIL",
)
# The label cannot start or end with a space or tab, so there is exactly one way to match it
# (linear time on a long run of spaces; a lazy label followed by `[ \t]*:` is quadratic).
FIELD_RE = re.compile(r"^[ \t]*[-*][ \t]+(?P<label>[^:\n \t](?:[^:\n]*[^:\n \t])?)[ \t]*:[ \t]*(?P<value>.*)$")
WORD_MARKER_RE = re.compile(r"\b(?:TBD|TODO)\b")
TEMPLATE_PROSE_MARKERS = ("[list ", "[if FAIL")
PENDING_ON_RE = re.compile(r"\bon\s+pending\b", re.IGNORECASE)

INSTALL_SH = Path("scripts/install.sh")
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
and inline HTML never count. What the parser reads as code, an HTML comment or a raw
HTML block is not an anchor (SEC-T703-01, SEC-T715-03). '__bold__', an anchor in a
blockquote and a heading in a list do not count either.
What stays open (SEC-T738-04). The gate reads CommonMark, and GitLab's renderer may
differ, for example on front matter at the start of a document (unverified). Raw HTML
around an anchor, such as '<details>' or '<div hidden>' followed by a blank line, is not
modelled, so such an anchor counts because CommonMark parses it as live. The install.sh
rules are per line and do not defend against a crafted script: they catch an omission on
one line, and a pointer on a line without the word "Cursor" needs no item.
Newer versions: a pointer to a version (major.minor.patch, any pre-release suffix
ignored) newer than the tag being verified is an error, because the tagged tree points
users to a document it does not ship (SEC-T703-03). --allow-newer-pointers turns that
error into a printed note; it exists for verifying a past tag on a later tree (tests)
and is not used by the CI job. A tag that is not vX.Y.Z[-pre] enforces every pointer.
Encoding (SEC-T739-01): every file the gate reads in this process must be valid UTF-8.
The gate exits 1 on the first one that is not, naming its path and the file offset of the
first invalid byte and never its content, and no check runs on that file. Newlines are
read as before: CRLF and CR become LF. scripts/check-version-consistency.py runs as a
child process with its own reads, and this does not cover them."""

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class NotUtf8Error(Exception):
    """A file the gate reads is not valid UTF-8. The message holds its path and an offset, never its content."""


def read_strict(path: Path) -> str:
    """The text of ``path``, or NotUtf8Error (SEC-T739-01). Every read in this process goes through here.

    The whole file is decoded at once, so the offset counts from the start of the file and nothing partly decoded
    is ever returned. The newlines are translated as text mode translates them: this helper changes what happens to
    invalid bytes and nothing else, so SEC-T738-02 (a CR in install.sh splits its line) stays as it was.
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
    return text.replace("\r\n", "\n").replace("\r", "\n")


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


def section_text(text: str, heading: str) -> str:
    """The body of ``heading`` (a ``## `` line) up to the next ``## `` heading; '' when absent.

    Fenced code is blanked first, so a heading or a placeholder quoted in a code block
    neither opens a section nor counts as an unfilled value.
    """
    lines = [line.rstrip(" \t") for line in markdown_lines(FENCED_CODE_RE.sub("", text))]
    try:
        start = lines.index(heading)
    except ValueError:
        return ""
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1 : end])


def verdict_placeholder_problems(text: str) -> list[str]:
    """Problems for each unfilled row or field in the Gate Verdicts / RELEASE VERDICT sections."""
    problems: list[str] = []
    for heading in VERDICT_SECTIONS:
        body = section_text(text, heading)
        if re.search(rf"^{re.escape(heading)}", text, re.M) and not body.strip():
            problems.append(f"{heading[3:]}: the heading is present but the section is empty or only inside a code block")
        lines = body.splitlines()
        for i, line in enumerate(lines):
            nested = i + 1 < len(lines) and re.match(r"[ \t]+[-*][ \t]", lines[i + 1]) is not None
            problems.extend(_line_problems(heading[3:], line, nested))
    return problems


def _line_problems(section: str, line: str, nested_follows: bool = False) -> list[str]:
    """Placeholder problems of one line of a verdict section (``nested_follows``: a sub-list item comes next)."""
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
    value = field.group("value").replace("*", "").replace("`", "").strip()
    if not value and not nested_follows:
        found.append(f"{section}: field has no value: {line.strip()[:80]}")
    if value.lower().startswith("pending") or PENDING_ON_RE.search(value):
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
            [sys.executable, str(script)],
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


def check_release_brief(tag: str, release_brief: str, errors: list[str]) -> None:
    """The release notes document has the required sections and no unfilled verdict."""
    brief_text = read_strict(ROOT / release_brief)
    if not has_marker(brief_text, f"Latest release: {tag}"):
        errors.append(f"missing required content in {release_brief}: Latest release: {tag}")
    for snippet in (
        "## Install",
        "## Highlights",
        # Placement of the release gate VERDICT, declared by step 7 of
        # implementation/knowledge/commands/prepare-release.md: the release notes
        # document is the block's home. Presence of the section is checked here; the
        # field-level contract (11 fields, Status enum) is encoded once, in the golden
        # suite, and is deliberately not duplicated in this gate.
        "## RELEASE VERDICT",
    ):
        if snippet not in brief_text:
            errors.append(f"missing required content in {release_brief}: {snippet}")

    for problem in verdict_placeholder_problems(brief_text):
        errors.append(f"unfilled verdict in {release_brief}: {problem}")


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
            return inline_text(tokens[:index])
    return ""


def migration_section_tokens(tokens: list) -> list:
    """The block tokens of the Migration Guide section, as MIGRATION_POINTER_HELP defines it; [] when there is none.

    ``level == 0`` keeps out a heading inside a blockquote or a list. A heading token is followed by its inline token.
    """
    start: int | None = None
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.level != 0 or token.tag not in ("h1", "h2"):
            continue
        if start is not None:
            return tokens[start:index]
        if token.tag == "h2" and inline_text(tokens[index + 1].children or []).strip() == MIGRATION_SECTION_TITLE:
            start = index + 1
    return [] if start is None else tokens[start:]


def has_cursor_migration_item(text: str) -> bool:
    """The Migration Guide section holds a heading or bold lead that names Cursor (see MIGRATION_POINTER_HELP).

    The commonmark preset has two block containers, blockquotes and lists, so "only list containers around it"
    means no open blockquote. ``paragraph_open`` is ``hidden`` in a tight list and is still rendered, so it counts.
    A paragraph or heading token is followed by its inline token.
    """
    section = migration_section_tokens(MarkdownIt("commonmark").parse(text))
    quotes = 0
    for index, token in enumerate(section):
        quotes += {"blockquote_open": 1, "blockquote_close": -1}.get(token.type, 0)
        anchor = ""
        if token.type == "heading_open" and token.level == 0 and token.tag in ("h3", "h4", "h5", "h6"):
            anchor = inline_text(section[index + 1].children or [])
        elif token.type == "paragraph_open" and quotes == 0:
            anchor = bold_lead_text(section[index + 1].children or [])
        if CURSOR_WORD_RE.search(anchor):
            return True
    return False


def check_migration_pointers(tag: str, errors: list[str], allow_newer: bool = False) -> None:
    """Every release document install.sh points users to exists and, if pointed to for Cursor, has the item.

    ``allow_newer`` (``--allow-newer-pointers``) reports a pointer newer than ``tag`` as a note instead of an error.
    """
    install = ROOT / INSTALL_SH
    if not install.is_file():
        return  # reported as a missing required file
    text = read_strict(install)
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
        if needs_cursor and not has_cursor_migration_item(read_strict(document)):
            errors.append(
                f"{path} lacks its Cursor migration item ({INSTALL_SH} points users to it): add a "
                f"'### ... Cursor ...' heading or a '**... Cursor ...**' lead line under '{MIGRATION_SECTION}'"
            )


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
    check_release_brief(tag, release_brief, errors)

    for relative in required_for_tag:
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
