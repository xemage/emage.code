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
for the anchor and for how a pointer to a version newer than the tag is treated.

Every printed line passes through ``printable``: control, bidi and zero-width characters of an
``install.sh`` line, a release document or a tag become ``?`` in the CI log (SEC-T715-04).

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
ITEM_HEADING_RE = re.compile(r"^#{3,6}[ \t]+(?P<text>.+)$")
ITEM_BOLD_LEAD_RE = re.compile(r"^(?:[-*][ \t]+|\d+\.[ \t]+)?\*\*(?P<text>[^*\n]+)\*\*")
CURSOR_WORD_RE = re.compile(r"\bCursor\b")
# SEC-T703-01: the anchor counts only where a reader sees it, not in fenced code or an HTML comment.
FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})")
HTML_COMMENT_RE = re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL)
# SEC-T715-03: CommonMark raw HTML blocks (spec 0.31.2, section 4.6). Each rule is (start, end) for
# types 1 to 6; the end pattern is searched on the whole start line, then on each later line, so '<!-->'
# and '<?>' close on their own line (SEC-T731-09). A start line is not blank, so a blank-line end never fits it.
HTML_BLOCK_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|"
    "dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|"
    "iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|"
    "source|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul"
)
BLANK_LINE_RE = re.compile(r"^[ \t]*$")
HTML_BLOCK_RULES = (
    (re.compile(r" {0,3}<(?:script|pre|style|textarea)(?=[ \t>]|$)", re.I),
     re.compile(r"</(?:script|pre|style|textarea)>", re.I)),
    (re.compile(r" {0,3}<!--"), re.compile(r"-->")),
    (re.compile(r" {0,3}<\?"), re.compile(r"\?>")),
    (re.compile(r" {0,3}<![A-Za-z]"), re.compile(r">")),
    (re.compile(r" {0,3}<!\[CDATA\["), re.compile(r"\]\]>")),
    (re.compile(rf" {{0,3}}</?(?:{HTML_BLOCK_TAGS})(?=[ \t]|/?>|$)", re.I), BLANK_LINE_RE),
)
# Type 7: a line that is one complete open or closing tag; it ends at a blank line and cannot
# interrupt a paragraph. Attribute syntax per spec section 6.6; each part has one way to match.
_HTML_ATTR = r"[ \t]+[A-Za-z_:][A-Za-z0-9_.:-]*(?:[ \t]*=[ \t]*(?:[^ \t\"'=<>`]+|'[^'\n]*'|\"[^\"\n]*\"))?"
HTML_TAG_LINE_RE = re.compile(
    rf" {{0,3}}(?:<[A-Za-z][A-Za-z0-9-]*(?:{_HTML_ATTR})*[ \t]*/?>|</[A-Za-z][A-Za-z0-9-]*[ \t]*>)[ \t]*$"
)
ATX_HEADING_RE = re.compile(r" {0,3}#{1,6}(?:[ \t]|$)")
# SEC-T731-01, SEC-T731-06: a list item line may precede a list-form anchor (see has_cursor_migration_item).
LIST_ITEM_RE = re.compile(r" {0,3}(?:[-*+]|\d{1,9}[.)])[ \t]+\S")
# SEC-T731-02: CommonMark ends a line only at \n, \r\n or \r; str.splitlines() also splits at
# \v, \f, \x1c-\x1e, \x85, U+2028 and U+2029, which would end an HTML block or start a line early.
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
Anchor: inside the '## Migration Guide' section (up to the next '## ' heading), a
heading of level 3 to 6 ('### ...') or a bold lead ('**...**' at the start of a line,
optionally after a list marker) whose text contains the word "Cursor" (case-sensitive)
and that starts a block: the line before it is blank or an ATX heading, or a list-form
anchor continues a run of list item lines that started there (SEC-T731-06),
for example '**Migration Guide item M-3. Cursor is no longer supported.**'. Fenced code
(``` or ~~~), HTML comments and raw HTML blocks (CommonMark types 1 to 7, for example
a '<details>' block up to the next blank line) are ignored, so an anchor there does not
count (SEC-T703-01, SEC-T715-03).
Newer versions: a pointer to a version (major.minor.patch, any pre-release suffix
ignored) newer than the tag being verified is an error, because the tagged tree points
users to a document it does not ship (SEC-T703-03). --allow-newer-pointers turns that
error into a printed note; it exists for verifying a past tag on a later tree (tests)
and is not used by the CI job. A tag that is not vX.Y.Z[-pre] enforces every pointer."""

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


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
    text = file_path.read_text(encoding="utf-8", errors="ignore")
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
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        if not has_marker(text, marker):
            errors.append(f"missing marker '{marker}' in {relative}")


def check_section_requirements(errors: list[str]) -> None:
    """Every SECTION_REQUIREMENTS file holds each of its required snippets."""
    for relative, required_snippets in SECTION_REQUIREMENTS.items():
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
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
        text = path.read_text(encoding="utf-8", errors="ignore")
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
    brief_text = (ROOT / release_brief).read_text(encoding="utf-8", errors="ignore")
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


def html_block_opening(line: str) -> re.Pattern[str] | None:
    """The end pattern when ``line`` opens a CommonMark HTML block, else None.

    A type 7 block (a line that is one complete tag) opens whatever the line before it is
    (SEC-T731-01). CommonMark keeps it closed after a paragraph line, but this gate cannot tell a
    paragraph line from a table row, a blockquote or an empty list item. Opening it wrongly hides
    the lines up to the next blank line. That is a false FAIL when an anchor is among them. It can be a
    false PASS when a fence or an HTML block start is among them: in 'Some text', '<span>', '```', '',
    '**M-3. Cursor removed.**', '```' CommonMark hides the anchor and this gate counts it.
    """
    for start, end in HTML_BLOCK_RULES:
        if start.match(line):
            return end
    if HTML_TAG_LINE_RE.match(line):
        return BLANK_LINE_RE
    return None


def _filler_lines(match: re.Match[str]) -> str:
    """One empty comment per line of ``match``: the line count is kept and no line becomes blank."""
    return "\n".join(["<!---->"] * (match.group(0).count("\n") + 1))


def strip_hidden_markdown(text: str) -> str:
    """Blank fenced code (``` and ~~~), raw HTML blocks and HTML comments (CommonMark rules); the line count is kept.

    An unclosed fence, HTML block or comment hides the rest of the document, as a Markdown renderer does.
    A comment or triple-backtick span left at this point sits inside a paragraph, so each of its lines becomes
    an empty comment, not a blank line: a blank line would end the paragraph for the anchor rule (SEC-T731-06).
    A blank line ends an HTML block of type 6 or 7; it is blank either way.
    """
    kept: list[str] = []
    fence = ""
    html_end: re.Pattern[str] | None = None
    for line in markdown_lines(text):
        kept.append("")
        if fence:
            if re.match(rf"^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$", line):
                fence = ""
            continue
        if html_end is not None:
            if html_end.search(line):
                html_end = None
            continue
        opening = FENCE_OPEN_RE.match(line)
        if opening and not (opening.group("fence")[0] == "`" and "`" in line[opening.end():]):
            fence = opening.group("fence")
            continue
        block_end = html_block_opening(line)
        if block_end is not None:
            html_end = None if block_end.search(line) else block_end
            continue
        kept[-1] = line
    return FENCED_CODE_RE.sub(_filler_lines, HTML_COMMENT_RE.sub(_filler_lines, "\n".join(kept)))


def has_cursor_migration_item(text: str) -> bool:
    """The Migration Guide section holds a heading or bold lead that names Cursor (see MIGRATION_POINTER_HELP).

    An anchor counts only where it starts a block, since a line inside a paragraph can be part of a
    multi-line inline construct that the reader does not see (SEC-T731-06): the line before it, after
    blanking, must be blank or an ATX heading, or a list-form anchor must continue a run of list item
    lines that itself started there. Refusing any other anchor can only cause a false FAIL.

    The check as a whole can still give a false PASS, because strip_hidden_markdown can hide too much
    and a blanked line counts as blank here. A crafted document can use this. SEC-T731-09 residual (b):
    the gate can pair two fences that CommonMark does not, so in '- a', '  ```', 'x', '  ```',
    '**M-3. Cursor removed.**' CommonMark hides the anchor and this gate counts it. A wrongly opened
    type 7 block is a second route (see html_block_opening). The gate has no Markdown parser and no model of
    list containers; these are examples, not a full list.
    """
    clear, in_list = True, False
    for line in markdown_lines(section_text(strip_hidden_markdown(text), MIGRATION_SECTION)):
        match = ITEM_HEADING_RE.match(line) or ITEM_BOLD_LEAD_RE.match(line)
        is_list = LIST_ITEM_RE.match(line) is not None
        if match and (clear or (in_list and is_list)) and CURSOR_WORD_RE.search(match.group("text")):
            return True
        in_list = is_list and (clear or in_list)
        clear = BLANK_LINE_RE.match(line) is not None or ATX_HEADING_RE.match(line) is not None
    return False


def check_migration_pointers(tag: str, errors: list[str], allow_newer: bool = False) -> None:
    """Every release document install.sh points users to exists and, if pointed to for Cursor, has the item.

    ``allow_newer`` (``--allow-newer-pointers``) reports a pointer newer than ``tag`` as a note instead of an error.
    """
    install = ROOT / INSTALL_SH
    if not install.is_file():
        return  # reported as a missing required file
    text = install.read_text(encoding="utf-8", errors="ignore")
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
        if needs_cursor and not has_cursor_migration_item(document.read_text(encoding="utf-8", errors="ignore")):
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


def main() -> int:
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
    args = parser.parse_args()

    marker = f"Latest release: {args.tag}"
    errors: list[str] = []

    release_brief = release_brief_path(args.tag)
    required_for_tag = [*REQUIRED_FILES, release_brief]

    for relative in required_for_tag:
        absolute = ROOT / relative
        if not absolute.is_file():
            errors.append(f"missing required file: {relative}")
    check_migration_pointers(args.tag, errors, args.allow_newer_pointers)

    if errors:
        print_errors(errors)
        return 1

    check_markers(marker, errors)
    check_line_breaks([*MARKER_FILES, release_brief, INSTALL_SH], errors)
    check_section_requirements(errors)
    check_release_brief(args.tag, release_brief, errors)

    for relative in required_for_tag:
        check_links(ROOT / relative, errors)

    check_version_consistency(errors)

    if errors:
        print_errors(errors)
        return 1

    print("release-docs-verify: all documentation checks passed")
    print(f"release-docs-verify: verified marker '{printable(marker)}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
