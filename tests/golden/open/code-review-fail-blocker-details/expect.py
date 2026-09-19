#!/usr/bin/env python3
"""expect.py for code-review-fail-blocker-details.

Contract under test: implementation/knowledge/commands/code-review.md -- "If status is fail,
include blocker details, owner, and retry attempt guidance."
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check(case_dir: Path) -> bool:
    review_file = case_dir / "fixture" / "review.md"
    if not review_file.is_file():
        return False
    text = review_file.read_text(encoding="utf-8")

    status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", text)
    if not status_match or status_match.group(1) != "FAIL":
        return False

    blocker_match = re.search(r"\*\*Blocker IDs\*\*\s*:\s*(.+)", text)
    if not blocker_match or blocker_match.group(1).strip().lower() in ("", "none", "[]"):
        return False

    has_owner = bool(re.search(r"\*\*Owner\*\*\s*:", text))
    has_retry = "retry" in text.lower()
    return has_owner and has_retry


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
