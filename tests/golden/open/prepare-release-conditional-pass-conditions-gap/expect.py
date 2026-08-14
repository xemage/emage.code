#!/usr/bin/env python3
"""expect.py for prepare-release-conditional-pass-conditions-gap (known_failing /
capability_gap).

Contract under test: implementation/knowledge/commands/prepare-release.md step 9 -- "If
CONDITIONAL_PASS, list conditions that must be met before deployment." Checks for a structured
"**Conditions**:" field or a "## Conditions" section. Expected to return False today -- see
brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check(case_dir: Path) -> bool:
    notes_file = case_dir / "fixture" / "release-notes.md"
    if not notes_file.is_file():
        return False
    text = notes_file.read_text(encoding="utf-8")

    status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", text)
    if not status_match or status_match.group(1) != "CONDITIONAL_PASS":
        return False

    has_conditions_field = bool(re.search(r"\*\*Conditions\*\*\s*:\s*\S", text))
    has_conditions_section = bool(
        re.search(r"##\s*Conditions\b.*?\n\s*-\s+\S", text, re.DOTALL)
    )
    return has_conditions_field or has_conditions_section


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
