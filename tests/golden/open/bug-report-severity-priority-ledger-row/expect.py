#!/usr/bin/env python3
"""expect.py for bug-report-severity-priority-ledger-row.

Contract under test: implementation/knowledge/commands/bug-report.md --
  the `Use this format:` block's nine declared `###` sections of `## Bug Report`, and
  `### Task Creation` step 1, verbatim: "Create a TASK entry for tracking this bug: Add to
  `docs/tasks/active-tasks.md` with state `pending`; Assign severity-appropriate priority; Use
  the NEXT sequential `T<NNN>` ID. NEVER invent a `BUG-` prefix ...; Format (7 columns, exact
  order): `| T<NNN> | BUG: <title> | <owner-slug> | pending | P0|P1|P2 | <dep-ids or -> |
  YYYY-MM-DD |`; Map severity -> priority: critical->P0, high->P0, medium->P1, low->P2".

The load-bearing assertion is cross-artifact: the `### Severity` the report states must map,
through the command's own declared table, to the priority the ledger row carries. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# The nine `###` sections of the declared `Use this format:` block, in declared order.
DECLARED_SECTIONS = (
    "### Title",
    "### Severity",
    "### Environment",
    "### Steps to Reproduce",
    "### Expected Behavior",
    "### Actual Behavior",
    "### Root Cause Analysis",
    "### Suggested Fix",
    "### Related Files",
)
# "Map severity -> priority: critical->P0, high->P0, medium->P1, low->P2", verbatim.
SEVERITY_TO_PRIORITY = {"critical": "P0", "high": "P0", "medium": "P1", "low": "P2"}
TASK_ID_RE = re.compile(r"^T\d{3,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NUMBERED_STEP_RE = re.compile(r"^\s*\d+\.\s+\S", re.MULTILINE)
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")
BUG_TITLE_PREFIX = "BUG: "


def _section_bodies(text: str) -> dict[str, str] | None:
    """Bodies of the nine declared sections, or None if any is missing or out of order."""
    positions: list[int] = []
    for heading in DECLARED_SECTIONS:
        idx = text.find(heading)
        if idx == -1:
            return None
        positions.append(idx)
    if positions != sorted(positions):
        return None  # "Use this format" declares an order; a shuffled report is not that format
    bodies: dict[str, str] = {}
    for i, heading in enumerate(DECLARED_SECTIONS):
        start = positions[i] + len(heading)
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        bodies[heading] = text[start:end].strip()
    return bodies


def _declared_severity(body: str) -> str | None:
    """The severity token, which the format declares as `[Critical | High | Medium | Low] --
    with justification`, so a bare token with no justification does not satisfy it."""
    first_line = body.splitlines()[0] if body.splitlines() else ""
    match = re.match(r"^(Critical|High|Medium|Low)\b(.*)$", first_line.strip())
    if not match:
        return None
    justification = match.group(2).strip(" -—–:")
    remainder = "\n".join(body.splitlines()[1:]).strip()
    if not justification and not remainder:
        return None
    return match.group(1).lower()


def _ledger_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or cells[0] == "ID" or SEPARATOR_ROW_RE.match(stripped):
            continue
        rows.append(cells)
    return rows


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    report_path = fixture / "bug-report.md"
    ledger_path = fixture / "docs" / "tasks" / "active-tasks.md"
    if not report_path.is_file() or not ledger_path.is_file():
        return False

    text = report_path.read_text(encoding="utf-8")
    if "## Bug Report" not in text:
        return False
    bodies = _section_bodies(text)
    if bodies is None:
        return False
    if any(not body for body in bodies.values()):
        return False
    if len(NUMBERED_STEP_RE.findall(bodies["### Steps to Reproduce"])) < 2:
        return False  # "1. [Precise step 1] 2. [Precise step 2] 3. ..."

    severity = _declared_severity(bodies["### Severity"])
    if severity is None:
        return False

    rows = _ledger_rows(ledger_path)
    if not rows:
        return False
    # "NEVER invent a `BUG-` prefix" -- no row anywhere may carry one as its ID.
    if any(row[0].upper().startswith("BUG-") for row in rows):
        return False

    bug_rows = [row for row in rows if len(row) > 1 and row[1].startswith(BUG_TITLE_PREFIX)]
    if len(bug_rows) != 1:
        return False
    bug_row = bug_rows[0]
    if len(bug_row) != 7:
        return False  # "Format (7 columns, exact order)"

    task_id, title, owner, status, priority, _depends, last_update = bug_row
    if not TASK_ID_RE.match(task_id):
        return False
    if not title[len(BUG_TITLE_PREFIX):].strip():
        return False
    if not owner:
        return False
    if status != "pending":
        return False  # "Add to docs/tasks/active-tasks.md with state `pending`"
    if priority != SEVERITY_TO_PRIORITY[severity]:
        return False  # the declared severity -> priority map
    if not DATE_RE.match(last_update):
        return False

    # "Use the NEXT sequential T<NNN> ID" -- checkable, from this ledger alone, as: strictly
    # greater than every other ID it contains. See brief.md for why this is the available
    # reading rather than the stronger max(both ledgers) + 1.
    others = [int(row[0][1:]) for row in rows if row is not bug_row and TASK_ID_RE.match(row[0])]
    return bool(others) and int(task_id[1:]) > max(others)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
