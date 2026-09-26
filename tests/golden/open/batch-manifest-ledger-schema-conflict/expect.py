#!/usr/bin/env python3
"""expect.py for batch-manifest-ledger-schema-conflict.

Contract under test: implementation/knowledge/commands/batch.md `## Instructions` --
  step 2 "Decompose into independent units -- each unit must be: Self-contained (no cross-unit
  dependencies within a batch); Independently testable; Small enough for a single agent session",
  step 3 "Create worktree isolation -- ... Branch naming: `batch/<slug>/<unit-number>-<short-
  description>`",
  step 5 "Track progress -- update `docs/tasks/active-tasks.md` with the full batch manifest:
  Unit ID, description, assigned agent, branch, status".

Expected to return False. Assertions A (step 2, independence) and B (step 3, branch naming) hold
on the fixture; assertion C (step 5) cannot be satisfied by any ledger that conforms to the
7-column `active-tasks.md` schema that AGENTS.md pins and `docs/tasks/validate-tasks.py:195`
enforces, because that schema has no `branch` field. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Step 3's declared branch naming: batch/<slug>/<unit-number>-<short-description>.
BRANCH_RE = re.compile(r"^batch/[a-z0-9][a-z0-9-]*/\d+-[a-z0-9][a-z0-9-]*$")
UNIT_ID_RE = re.compile(r"^U\d+$", re.IGNORECASE)
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")
NO_DEPENDENCY_TOKENS = frozenset({"—", "–", "-", "--", "", "none", "None"})

# The five fields step 5 declares the manifest must carry, matched by concept.
MANIFEST_CONCEPTS = (
    re.compile(r"unit", re.IGNORECASE),
    re.compile(r"description|title", re.IGNORECASE),
    re.compile(r"agent|owner|assign", re.IGNORECASE),
    re.compile(r"branch", re.IGNORECASE),
    re.compile(r"status|state", re.IGNORECASE),
)
DEPENDS_CONCEPTS = (
    re.compile(r"unit", re.IGNORECASE),
    re.compile(r"depend|blocked", re.IGNORECASE),
)


def _cells(line: str) -> list[str]:
    return [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]


def _tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every pipe table as (header_cells, data_rows)."""
    tables: list[tuple[list[str], list[list[str]]]] = []
    header: list[str] | None = None
    rows: list[list[str]] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("|"):
            if SEPARATOR_ROW_RE.match(stripped):
                continue
            if header is None:
                header = _cells(stripped)
            else:
                rows.append(_cells(stripped))
            continue
        if header is not None:
            tables.append((header, rows))
        header, rows = None, []
    if header is not None:
        tables.append((header, rows))
    return tables


def _table_matching(text: str, concepts: tuple[re.Pattern[str], ...]) -> list[list[str]] | None:
    for header, rows in _tables(text):
        if len(header) != len(concepts):
            continue
        if all(c.search(cell) for c, cell in zip(concepts, header)) and rows:
            return rows
    return None


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    decomposition = fixture / "decomposition.md"
    ledger = fixture / "docs" / "tasks" / "active-tasks.md"
    if not decomposition.is_file() or not ledger.is_file():
        return False
    plan_text = decomposition.read_text(encoding="utf-8")

    units = _table_matching(plan_text, MANIFEST_CONCEPTS)
    if not units or len(units) < 2:
        return False  # a batch is a decomposition into units, plural
    parsed: list[dict[str, str]] = []
    for row in units:
        if len(row) != len(MANIFEST_CONCEPTS):
            return False
        unit_id, description, agent, branch, status = row
        if not (UNIT_ID_RE.match(unit_id) and description and agent and status):
            return False
        parsed.append(
            {"id": unit_id, "description": description, "agent": agent,
             "branch": branch, "status": status}
        )
    unit_ids = {u["id"].upper() for u in parsed}
    if len(unit_ids) != len(parsed):
        return False

    # Assertion B -- step 3's declared branch naming.
    if any(not BRANCH_RE.match(u["branch"]) for u in parsed):
        return False

    # Assertion A -- step 2: "Self-contained (no cross-unit dependencies within a batch)".
    depends_rows = _table_matching(plan_text, DEPENDS_CONCEPTS)
    if depends_rows is None:
        return False  # independence is declared per unit; with no such table it is unverifiable
    declared_for = {row[0].upper() for row in depends_rows if len(row) == 2}
    if declared_for != unit_ids:
        return False
    for row in depends_rows:
        if len(row) != 2:
            return False
        for entry in row[1].split(","):
            token = entry.strip()
            if token in NO_DEPENDENCY_TOKENS:
                continue
            if token.upper() in unit_ids:
                return False  # a cross-unit dependency inside the batch

    # Assertion C -- step 5: active-tasks.md carries the full manifest, including `branch`.
    ledger_rows = [row for _header, rows in _tables(ledger.read_text(encoding="utf-8"))
                   for row in rows]
    for unit in parsed:
        carried = any(
            unit["branch"] in row
            and any(cell.upper() == unit["id"].upper() for cell in row)
            and unit["agent"] in row
            and unit["status"] in row
            for row in ledger_rows
        )
        if not carried:
            return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
