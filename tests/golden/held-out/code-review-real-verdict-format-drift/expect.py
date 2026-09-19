#!/usr/bin/env python3
"""expect.py for code-review-real-verdict-format-drift (known_failing / tracked_defect).

Same VERDICT-field contract as code-review-verdict-compliant/expect.py, applied to a real
verdict (docs/tasks/task-T365.md) instead of a hand-authored one. Expected to return False
today -- see brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "Status",
    "Reviewed artifacts",
    "Must Fix count",
    "Should Fix count",
    "Nice to Have count",
    "Blocker IDs",
    "Reviewer",
    "Timestamp",
]
ALLOWED_STATUS = {"PASS", "CONDITIONAL_PASS", "FAIL"}


def _verdict_section(text: str) -> str | None:
    idx = text.find("## VERDICT")
    if idx == -1:
        return None
    rest = text[idx + len("## VERDICT"):]
    next_heading = re.search(r"\n#{1,2}\s", rest)
    return rest[: next_heading.start()] if next_heading else rest


def check(case_dir: Path) -> bool:
    task_file = case_dir / "fixture" / "docs" / "tasks" / "task-T365.md"
    if not task_file.is_file():
        return False
    text = task_file.read_text(encoding="utf-8")

    section = _verdict_section(text)
    if section is None:
        return False

    for field in REQUIRED_FIELDS:
        if not re.search(rf"\*\*{re.escape(field)}\*\*\s*:", section):
            return False

    status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", section)
    if not status_match or status_match.group(1) not in ALLOWED_STATUS:
        return False

    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
