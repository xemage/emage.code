#!/usr/bin/env python3
"""expect.py for plan-real-doc-header-drift (known_failing / tracked_defect).

Same contract as plan-required-sections-compliant/expect.py, applied to a real plan document
(docs/plans/plan-030-mcp-remote-transport-alignment.md) instead of a hand-authored one. Expected
to return False today — see brief.md for the real header-name drift this documents.
"""
from __future__ import annotations

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
    """True iff the fixture plan doc contains all six required headers, in order."""
    plans_dir = case_dir / "fixture" / "docs" / "plans"
    if not plans_dir.is_dir():
        return False
    candidates = sorted(plans_dir.glob("*.md"))
    if len(candidates) != 1:
        return False
    text = candidates[0].read_text(encoding="utf-8")

    positions = [text.find(h) for h in REQUIRED_HEADERS]
    if any(p == -1 for p in positions):
        return False
    return positions == sorted(positions)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
