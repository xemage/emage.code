#!/usr/bin/env python3
"""expect.py for prepare-release-verdict-compliant.

Contract under test: implementation/knowledge/commands/prepare-release.md -- "## RELEASE
VERDICT" block with Version/Status/Features included/Fixes included/Breaking changes/Open
blockers/Quality gates passed/Quality gates failed/Blocker IDs/Release manager/Timestamp
fields.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "Version",
    "Status",
    "Features included",
    "Fixes included",
    "Breaking changes",
    "Open blockers",
    "Quality gates passed",
    "Quality gates failed",
    "Blocker IDs",
    "Release manager",
    "Timestamp",
]
ALLOWED_STATUS = {"PASS", "CONDITIONAL_PASS", "FAIL"}
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")


def _verdict_section(text: str) -> str | None:
    idx = text.find("## RELEASE VERDICT")
    if idx == -1:
        return None
    rest = text[idx + len("## RELEASE VERDICT"):]

    # Skip heading-boundary matches that fall inside a fenced code block -- a fence may
    # legitimately reproduce a "## RELEASE VERDICT" heading (e.g. a template example) without
    # that being the real section's end; only a heading outside any fence really ends it.
    fence_spans = [m.span() for m in re.finditer(r"```.*?```", rest, re.DOTALL)]

    def _in_fence(pos: int) -> bool:
        return any(start <= pos < end for start, end in fence_spans)

    next_heading = None
    for m in re.finditer(r"\n#{1,2}\s", rest):
        if not _in_fence(m.start()):
            next_heading = m
            break

    return rest[: next_heading.start()] if next_heading else rest


def check(case_dir: Path) -> bool:
    notes_file = case_dir / "fixture" / "release-notes.md"
    if not notes_file.is_file():
        return False
    text = notes_file.read_text(encoding="utf-8")

    section = _verdict_section(text)
    if section is None:
        return False

    for field in REQUIRED_FIELDS:
        if not re.search(rf"\*\*{re.escape(field)}\*\*\s*:", section):
            return False

    status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", section)
    if not status_match or status_match.group(1) not in ALLOWED_STATUS:
        return False

    version_match = re.search(r"\*\*Version\*\*\s*:\s*(\S+)", section)
    if not version_match or not VERSION_RE.match(version_match.group(1)):
        return False

    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
