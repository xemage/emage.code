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

This gate cannot check that ``main`` already carries the release: that duty (merge the
release branch to ``develop`` and ``main`` before the tag) is enforced, within its
grace window, by ``scripts/check-main-develop-drift.py`` and stated in CONTRIBUTING.md.
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
    lines = [line.rstrip() for line in FENCED_CODE_RE.sub("", text).splitlines()]
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


def check_markers(marker: str, errors: list[str]) -> None:
    """Every MARKER_FILES entry carries the `Latest release: <tag>` marker."""
    for relative in MARKER_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        if marker not in text:
            errors.append(f"missing marker '{marker}' in {relative}")


def check_section_requirements(errors: list[str]) -> None:
    """Every SECTION_REQUIREMENTS file holds each of its required snippets."""
    for relative, required_snippets in SECTION_REQUIREMENTS.items():
        text = (ROOT / relative).read_text(encoding="utf-8", errors="ignore")
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f"missing required content in {relative}: {snippet}")


def check_release_brief(tag: str, release_brief: str, errors: list[str]) -> None:
    """The release notes document has the required sections and no unfilled verdict."""
    brief_text = (ROOT / release_brief).read_text(encoding="utf-8", errors="ignore")
    for snippet in (
        "## Install",
        "## Highlights",
        # Placement of the release gate VERDICT, declared by step 7 of
        # implementation/knowledge/commands/prepare-release.md: the release notes
        # document is the block's home. Presence of the section is checked here; the
        # field-level contract (11 fields, Status enum) is encoded once, in the golden
        # suite, and is deliberately not duplicated in this gate.
        "## RELEASE VERDICT",
        f"Latest release: {tag}",
    ):
        if snippet not in brief_text:
            errors.append(f"missing required content in {release_brief}: {snippet}")

    for problem in verdict_placeholder_problems(brief_text):
        errors.append(f"unfilled verdict in {release_brief}: {problem}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Release tag, e.g. v1.0.1")
    args = parser.parse_args()

    marker = f"Latest release: {args.tag}"
    errors: list[str] = []

    release_brief = release_brief_path(args.tag)
    required_for_tag = [*REQUIRED_FILES, release_brief]

    for relative in required_for_tag:
        absolute = ROOT / relative
        if not absolute.is_file():
            errors.append(f"missing required file: {relative}")

    if errors:
        for error in errors:
            print(f"release-docs-verify: {error}")
        return 1

    check_markers(marker, errors)
    check_section_requirements(errors)
    check_release_brief(args.tag, release_brief, errors)

    for relative in required_for_tag:
        check_links(ROOT / relative, errors)

    check_version_consistency(errors)

    if errors:
        for error in errors:
            print(f"release-docs-verify: {error}")
        return 1

    print("release-docs-verify: all documentation checks passed")
    print(f"release-docs-verify: verified marker '{marker}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
