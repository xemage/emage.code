#!/usr/bin/env python3
"""expect.py contract proof for the golden-suite scaffold case.

Canonical contract (see docs/artifacts/golden-suite-format-v1.md §4):
    check(case_dir: Path) -> bool

`check` must be:
  - deterministic: same fixture/ content -> same result, every run
  - side-effect-free outside of case_dir (no network calls, no live model
    calls, no writes back into fixture/)
  - importable: scripts/scorecard.py (T413) loads this file directly via
    importlib.util and calls `check(case_dir)`; it does not shell out to
    this file as a subprocess.

A `python3 expect.py <case_dir>` CLI entry point is also provided below for
local debugging/authoring convenience — it exits 0/1 to mirror `check`'s
bool — but the CLI path is a thin wrapper, not the contract itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_LINE = "Status: DONE"


def check(case_dir: Path) -> bool:
    """Return True iff fixture/workspace/STATUS.md contains a `Status: DONE` line."""
    status_file = case_dir / "fixture" / "workspace" / "STATUS.md"
    if not status_file.is_file():
        return False
    lines = {line.strip() for line in status_file.read_text(encoding="utf-8").splitlines()}
    return REQUIRED_LINE in lines


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    case_dir = Path(sys.argv[1]).resolve()
    return 0 if check(case_dir) else 1


if __name__ == "__main__":
    sys.exit(main())
