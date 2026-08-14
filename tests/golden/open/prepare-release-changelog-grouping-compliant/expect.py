#!/usr/bin/env python3
"""expect.py for prepare-release-changelog-grouping-compliant.

Contract under test: implementation/knowledge/commands/prepare-release.md -- changelog grouped
by Features/Fixes/Breaking Changes/Internal, with task IDs included under Features and Fixes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADERS = ["## Features", "## Fixes", "## Breaking Changes", "## Internal"]
TASK_ID_RE = re.compile(r"\bT\d+\b")


def _section(text: str, header: str) -> str:
    idx = text.find(header)
    if idx == -1:
        return ""
    rest = text[idx + len(header):]
    next_heading = re.search(r"\n#{1,2}\s", rest)
    return rest[: next_heading.start()] if next_heading else rest


def check(case_dir: Path) -> bool:
    changelog_file = case_dir / "fixture" / "changelog.md"
    if not changelog_file.is_file():
        return False
    text = changelog_file.read_text(encoding="utf-8")

    if not all(header in text for header in REQUIRED_HEADERS):
        return False

    features_section = _section(text, "## Features")
    fixes_section = _section(text, "## Fixes")

    return bool(TASK_ID_RE.search(features_section)) and bool(TASK_ID_RE.search(fixes_section))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
