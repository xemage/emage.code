#!/usr/bin/env python3
"""expect.py for new-feature-plan-doc-compliant.

Contract under test: implementation/knowledge/commands/new-feature.md Phase 1 step 1 -- a plan
doc at docs/plans/feature-<slug>.md with Objective/Affected Components/Task Breakdown/
Dependency Impact sections.
"""
from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "## Objective",
    "## Affected Components",
    "## Task Breakdown",
    "## Dependency Impact",
]


def check(case_dir: Path) -> bool:
    plans_dir = case_dir / "fixture" / "docs" / "plans"
    if not plans_dir.is_dir():
        return False
    candidates = sorted(plans_dir.glob("feature-*.md"))
    if len(candidates) != 1:
        return False
    text = candidates[0].read_text(encoding="utf-8")
    return all(header in text for header in REQUIRED_HEADERS)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
