#!/usr/bin/env python3
"""expect.py for consolidate-memory-recommendation-table-grounded.

Contract under test: implementation/knowledge/commands/consolidate-memory.md `## Instructions` --
  step 1 "Read all MCP Memory entries -- use `mcp__memory` to retrieve the full set of stored
  memories",
  step 2 "Categorize each entry -- assign one of: Keep / Promote / Prune",
  step 3 "Present recommendations -- show a table with: Memory key/identifier; Current content
  summary (one line); Recommended action (Keep / Promote / Prune); Rationale (why this action)".

The load-bearing assertion is steps 1+3 together: the table must cover the retrieved entry set
exactly -- no invented key, no silently dropped entry. Step 3's column *labels* are not declared
by the command, so the header is matched by concept rather than by literal string; step 4
("Wait for user approval") is a human interaction with no declared artifact and is not checked.
See brief.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Step 2's declared vocabulary, exactly as the command names the three categories.
DECLARED_ACTIONS = frozenset({"Keep", "Promote", "Prune"})

# Step 3's four declared columns, matched by concept -- the command declares column *content*,
# never header labels, so an exact-string header check would assert an undeclared contract.
COLUMN_CONCEPTS = (
    re.compile(r"key|identifier", re.IGNORECASE),
    re.compile(r"summary|content", re.IGNORECASE),
    re.compile(r"action|recommend", re.IGNORECASE),
    re.compile(r"rationale|why|reason", re.IGNORECASE),
)
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")


def _row_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_header(cells: list[str]) -> bool:
    return len(cells) == len(COLUMN_CONCEPTS) and all(
        concept.search(cell) for concept, cell in zip(COLUMN_CONCEPTS, cells)
    )


def _declared_table_rows(text: str) -> list[list[str]] | None:
    """Data rows of the first 4-column table whose header identifies all four declared
    concepts. None if no such table exists."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if not _is_header(_row_cells(stripped)):
            continue
        rows: list[list[str]] = []
        for follow in lines[idx + 1:]:
            candidate = follow.strip()
            if not candidate.startswith("|"):
                break
            if SEPARATOR_ROW_RE.match(candidate):
                continue
            rows.append(_row_cells(candidate))
        return rows
    return None


def _retrieved_keys(entries_path: Path) -> list[str] | None:
    try:
        data = json.loads(entries_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        return None
    keys: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("key"), str) or not entry["key"]:
            return None
        keys.append(entry["key"])
    return keys


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    recommendations = fixture / "recommendations.md"
    if not recommendations.is_file():
        return False

    retrieved = _retrieved_keys(fixture / "memory-entries.json")
    if retrieved is None:
        return False  # step 1 could not have been satisfied
    if len(retrieved) != len(set(retrieved)):
        return False  # a malformed entry set makes coverage undecidable

    rows = _declared_table_rows(recommendations.read_text(encoding="utf-8"))
    if not rows:
        return False  # no declared table, or a table with no recommendations in it

    tabled_keys: list[str] = []
    for cells in rows:
        if len(cells) != len(COLUMN_CONCEPTS):
            return False
        key, summary, action, rationale = cells
        key = key.strip("`").strip()
        if action not in DECLARED_ACTIONS:
            return False  # outside step 2's declared vocabulary
        if not summary or "\n" in summary:
            return False  # step 3: "Current content summary (one line)"
        if not rationale:
            return False  # step 3: "Rationale (why this action)"
        tabled_keys.append(key)

    if len(tabled_keys) != len(set(tabled_keys)):
        return False  # one entry recommended twice is two conflicting recommendations
    # Steps 1 + 3: the table covers the retrieved set exactly -- in both directions.
    return set(tabled_keys) == set(retrieved)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
