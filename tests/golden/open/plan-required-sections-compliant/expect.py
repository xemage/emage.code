#!/usr/bin/env python3
"""expect.py for plan-required-sections-compliant.

Contract under test: implementation/knowledge/commands/plan.md step 5 — the plan document
saved to docs/plans/<slug>-plan.md must contain, in order: Goal, Task Decomposition,
Dependency Graph, Resource Assignments, Risk Assessment, Open Questions; step 2 additionally
requires the Dependency Graph be rendered as a Mermaid diagram.

See docs/artifacts/golden-suite-format-v1.md §4 for the check(case_dir) -> bool contract.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "## Goal",
    "## Task Decomposition",
    "## Dependency Graph",
    "## Resource Assignments",
    "## Risk Assessment",
    "## Open Questions",
]


def check(case_dir: Path) -> bool:
    """True iff exactly one docs/plans/*-plan.md fixture exists with all six required
    headers present in order, and a fenced ```mermaid block under Dependency Graph."""
    plans_dir = case_dir / "fixture" / "docs" / "plans"
    if not plans_dir.is_dir():
        return False
    candidates = sorted(plans_dir.glob("*-plan.md"))
    if len(candidates) != 1:
        return False
    text = candidates[0].read_text(encoding="utf-8")

    positions = [text.find(h) for h in REQUIRED_HEADERS]
    if any(p == -1 for p in positions):
        return False
    if positions != sorted(positions):
        return False

    dep_start = text.find("## Dependency Graph")
    next_header = text.find("## Resource Assignments")
    section = text[dep_start:next_header] if next_header != -1 else text[dep_start:]
    return bool(re.search(r"```mermaid.*?```", section, re.DOTALL))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
