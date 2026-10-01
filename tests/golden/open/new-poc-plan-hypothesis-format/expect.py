#!/usr/bin/env python3
"""expect.py for new-poc-plan-hypothesis-format.

Contract under test: implementation/knowledge/commands/new-poc.md `## Phase 0: Lightweight Plan`
step 1, verbatim in brief.md:

  1. Create a lightweight PoC plan before execution:
     - Hypothesis: Restate the hypothesis clearly with measurable success criteria
     - Validation path: Define what evidence proves/disproves the hypothesis
     - 3-step plan: (a) Feasibility check -> (b) Core build -> (c) Evaluate & demo
     ...
     - Reference protocol: ...; hypothesis format: `poc-guidelines.md` SS Hypothesis-First Validation

and the format that clause imports from poc-guidelines.md SS Hypothesis Format:

  HYPOTHESIS: / VALIDATION: / SUCCESS CRITERIA: / FAILURE CRITERIA:

with that section's Rule 2, "One hypothesis per PoC". The plan's *path* is deliberately not
asserted (parked item P11) -- see brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FIELDS = ("HYPOTHESIS", "VALIDATION", "SUCCESS CRITERIA", "FAILURE CRITERIA")
FIELD_RE = re.compile(r"^\s*(HYPOTHESIS|VALIDATION|SUCCESS CRITERIA|FAILURE CRITERIA):(.*)$")
MEASURABLE_RE = re.compile(r"\d")
# Step 1's three declared steps, in declared order; `&` and `and` are the same word.
PLAN_STEPS = (r"feasibility\s+check", r"core\s+build", r"evaluate\s+(?:&|and)\s+demo")
ITEM_LEAD_RE = re.compile(
    r"^\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)?(?:\*\*)?\(?([a-c])?\)?[.)]?\s*(?:\*\*)?\s*(.*)$",
    re.IGNORECASE,
)


def _fields(text: str) -> list[tuple[str, str]] | None:
    """[(label, value)] in document order; continuation lines join the preceding field."""
    found: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        m = FIELD_RE.match(line)
        if m:
            found.append((m.group(1), [m.group(2).strip()]))
        elif found and line.startswith((" ", "\t")) and line.strip() and not line.strip().startswith("```"):
            found[-1][1].append(line.strip())
        elif found and (not line.strip() or line.strip().startswith("```")):
            found.append(("", []))  # a blank line or fence ends a field
    return [(label, " ".join(v).strip()) for label, v in found if label]


def _plan_step_positions(text: str) -> list[int] | None:
    lines = text.splitlines()
    positions = []
    for idx, (step, letter) in enumerate(zip(PLAN_STEPS, "abc")):
        hits = []
        for no, line in enumerate(lines):
            m = ITEM_LEAD_RE.match(line)
            if not m or not re.match(step, m.group(2), re.IGNORECASE):
                continue
            if m.group(1) and m.group(1).lower() != letter:
                continue  # an explicit (a)/(b)/(c) label must be the declared one
            hits.append(no)
        if len(hits) != 1:
            return None
        positions.append(hits[0])
    return positions


def check(case_dir: Path) -> bool:
    plans = sorted((case_dir / "fixture" / "docs" / "plans").glob("*.md"))
    if len(plans) != 1:
        return False
    text = plans[0].read_text(encoding="utf-8")

    fields = _fields(text) or []
    labels = [label for label, _ in fields]
    if labels != list(FIELDS):
        return False  # all four, each exactly once (one hypothesis per PoC), in declared order
    values = dict(fields)
    if any(not values[f] for f in FIELDS):
        return False
    if not (MEASURABLE_RE.search(values["SUCCESS CRITERIA"])
            and MEASURABLE_RE.search(values["FAILURE CRITERIA"])):
        return False  # "measurable" -- each criterion carries a quantitative threshold

    positions = _plan_step_positions(text)
    return positions is not None and positions == sorted(positions)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
