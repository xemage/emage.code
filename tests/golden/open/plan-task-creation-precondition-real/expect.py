#!/usr/bin/env python3
"""expect.py for plan-task-creation-precondition-real.

Contract under test: implementation/knowledge/commands/plan.md "Task Creation Precondition" —
every task ID created from a plan must (a) cite that plan via a "Based on:" reference and
(b) appear literally in the plan document's own text.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check(case_dir: Path) -> bool:
    task_file = case_dir / "fixture" / "docs" / "tasks" / "task-T365.md"
    if not task_file.is_file():
        return False
    task_text = task_file.read_text(encoding="utf-8")

    id_match = re.search(r"^\*\*ID:\*\*\s*(\S+)", task_text, re.MULTILINE)
    based_on_match = re.search(r"^\*\*Based on:\*\*\s*(\S+)", task_text, re.MULTILINE)
    if not id_match or not based_on_match:
        return False
    if id_match.group(1) != "T365":
        return False

    plan_ref = based_on_match.group(1).strip("`")
    plan_file = case_dir / "fixture" / plan_ref
    if not plan_file.is_file():
        return False

    plan_text = plan_file.read_text(encoding="utf-8")
    return "T365" in plan_text


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
