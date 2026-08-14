#!/usr/bin/env python3
"""expect.py for plan-approval-marker-gap (known_failing / capability_gap).

Checks for an explicit, machine-checkable approval record (a "## Approval" section containing
a "**Approved**" line) in the fixture plan document. Expected to return False today: see
brief.md for why this documents a capability gap in the command surface rather than a fixable
defect in the fixture itself.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check(case_dir: Path) -> bool:
    plans_dir = case_dir / "fixture" / "docs" / "plans"
    if not plans_dir.is_dir():
        return False
    candidates = sorted(plans_dir.glob("*.md"))
    if len(candidates) != 1:
        return False
    text = candidates[0].read_text(encoding="utf-8")

    approval_idx = text.find("## Approval")
    if approval_idx == -1:
        return False
    section = text[approval_idx:]
    return bool(re.search(r"\*\*Approved\*\*", section))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
