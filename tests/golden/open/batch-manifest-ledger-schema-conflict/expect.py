#!/usr/bin/env python3
"""expect.py for batch-manifest-ledger-schema-conflict.

Contract under test: implementation/knowledge/commands/batch.md `## Instructions`, as amended by
`T535` and adjudicated in `docs/artifacts/batch-manifest-resolution-v1.md` --

  step 2 "Decompose into independent units -- each unit must be: Self-contained (no cross-unit
  dependencies within a batch) ... Write the decomposition to a plan document at
  `docs/plans/plan-<ID>.md` ... plus one additional required section: **Batch Manifest** -- one row
  per unit: `| Task ID | Description | Assigned agent | Branch |`. This is where the branch is
  written down; `docs/tasks/active-tasks.md` is not (step 5). Each `Branch` cell must equal
  `agent/<Assigned agent>/<Task ID>`, so the manifest cannot drift from the ledger row it
  describes.",

  step 3 "Create worktree isolation -- ... Branch naming: `agent/<agent-name>/<task-id>`, per
  `git-workflow.md` SS 'Agent Worktree Branch Naming' and the worktree-isolation skill's own
  convention",

  step 5 "Track progress -- record each unit as a task in `docs/tasks/active-tasks.md`, using that
  file's own 7-column schema (`AGENTS.md` SS Task Protocol) and never a five-field manifest row ...
  `| T<NNN> | BATCH <slug>: <description> | <agent-slug> | pending | P0|P1|P2 | <dep-ids or -> |
  YYYY-MM-DD |` ... Use the NEXT sequential `T<NNN>` ID for every unit. NEVER a `U<n>` or any other
  non-`T` unit ID -- non-`T` rows fail `docs/tasks/validate-tasks.py` check `C3` ... `Depends on`
  must not name another unit of the same batch -- that is step 2's independence constraint, and
  `validate-tasks.py` checks `C12`/`C13`/`C14` are what enforce it. A dependency on a task *outside*
  the batch is permitted. ... The branch is **not** a ledger column. ... The ledger is authoritative
  for status; the manifest is not a second status record."

Re-derived element-for-element under `docs/tasks/task-T541.md` SS1, against the specification in
`batch-manifest-resolution-v1.md` SS7. The three superseded elements were `UNIT_ID_RE = ^U\\d+$`,
`BRANCH_RE = ^batch/...$` and an assertion C requiring a `branch` inside a ledger row that the
amended contract says has none; all three asserted forms no document declares any more, which is why
the superseded checker would have returned False even against a fully conforming artifact.

**Not asserted, deliberately.** `batch-manifest-resolution-v1.md` SS7's sixth row offers one net
addition -- that the decomposition live at step 2's declared `docs/plans/plan-<ID>.md` and carry
`/plan` step 5's six section headers -- and instructs that it be omitted, and the
omission stated here, if SS4.1's counter-reading is taken. It is omitted, for two reasons stated so
that a reviewer can reject them: `ADR-007` Validation criterion 1 requires the replacement to assert
"the same number of structural elements", which is a ceiling as much as a floor, and SS4.1 itself
records that no case outcome and no promotion outcome moves either way. That choice is recorded in
brief.md SS "What is deliberately not asserted", where it can be overruled. Step 5's `<slug>` is
asserted kebab-case since `T544` -- by the repository's convention for every slug it names, not by a
declaration in `batch.md`, which still declares none; brief.md records that basis and its limit.

Expected to return True: five structural elements, all five of step 5's declared manifest fields
homed exactly once (four in the plan document's Batch Manifest, `status` in the ledger row, per
`batch-manifest-resolution-v1.md` SS4.4), and nothing loosened. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Step 5's declared unit ID -- `T<NNN>`, never `U<n>`. This is byte-for-byte the regex
# `docs/tasks/validate-tasks.py:11` applies as `ID_RE`, which its check `C3` (line 307) enforces on
# every `active-tasks.md` row, and it is case-sensitive here for the same reason it is there: a
# lowercase `t534` is a row the real validator rejects.
UNIT_ID_RE = re.compile(r"^T\d{3,}$")
# Step 3's declared branch naming: agent/<agent-name>/<task-id>, with <agent-name> the kebab-case
# agent role name `git-workflow.md` SS "Agent Worktree Branch Naming" declares.
BRANCH_RE = re.compile(r"^agent/[a-z0-9][a-z0-9-]*/T\d{3,}$")
# Step 5's declared Title form: `BATCH <slug>: <description>`, with <slug> a single kebab-case
# token -- the same class `BRANCH_RE` applies to <agent-name> -- and a non-empty description.
# `batch.md` does not itself declare <slug>'s character set; the class is the repository's
# convention (see brief.md). Tightened at `T544` from `^BATCH [^:\s][^:]*: \S`, which admitted a
# space inside the slug and so accepted the abolished `U<n>` unit-ID residue
# (`BATCH structured-logging U1: ...`) this fixture carried until then. Every Title this regex
# accepts, the one it replaces accepted too.
LEDGER_TITLE_RE = re.compile(r"^BATCH [a-z0-9][a-z0-9-]*: \S")
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")
# Step 5's `Depends on`, tokenised exactly the way `validate-tasks.py:61` tokenises it as
# `DEPENDS_ID_RE` for checks `C12`/`C13`/`C14` -- the checks step 5 itself names as the enforcement
# home for step 2's independence constraint.
DEPENDS_ID_RE = re.compile(r"\bT\d{3,}\b")

# Step 2's Batch Manifest columns, verbatim: | Task ID | Description | Assigned agent | Branch |.
# Matched by concept, as the superseded five-concept tuple was.
MANIFEST_CONCEPTS = (
    re.compile(r"task\s*id", re.IGNORECASE),
    re.compile(r"description|title", re.IGNORECASE),
    re.compile(r"agent|owner|assign", re.IGNORECASE),
    re.compile(r"branch", re.IGNORECASE),
)
# `docs/tasks/active-tasks.md`'s own 7-column schema, in the order `AGENTS.md` SS Task Protocol pins
# and step 5 cites: `ID | Title | Owner | Status | Priority | Depends on | Last update`. The fifth of
# the manifest's declared fields, `status`, is asserted here rather than on the manifest, because
# step 5 makes the ledger authoritative for it and forbids a second status record.
LEDGER_CONCEPTS = (
    re.compile(r"\bid\b", re.IGNORECASE),
    re.compile(r"title|description", re.IGNORECASE),
    re.compile(r"owner|agent|assign", re.IGNORECASE),
    re.compile(r"status|state", re.IGNORECASE),
    re.compile(r"priorit", re.IGNORECASE),
    re.compile(r"depend|blocked", re.IGNORECASE),
    re.compile(r"update|date", re.IGNORECASE),
)
LEDGER_ID, LEDGER_TITLE, LEDGER_OWNER, LEDGER_STATUS, LEDGER_DEPENDS = 0, 1, 2, 3, 5


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
        unit_id, description, agent, branch = row
        if not (UNIT_ID_RE.match(unit_id) and description and agent):
            return False
        parsed.append(
            {"id": unit_id, "description": description, "agent": agent, "branch": branch}
        )
    unit_ids = {u["id"] for u in parsed}
    if len(unit_ids) != len(parsed):
        return False

    # Assertion B -- step 3's declared branch naming, plus step 2's constraint that each `Branch`
    # cell *equal* `agent/<Assigned agent>/<Task ID>` rather than merely be well-formed.
    for unit in parsed:
        if not BRANCH_RE.match(unit["branch"]):
            return False
        if unit["branch"] != f"agent/{unit['agent']}/{unit['id']}":
            return False

    # Assertion C -- step 5: every unit is a row of `active-tasks.md` in that file's own 7-column
    # schema, carrying the unit's ID, its agent as `Owner` and its `Status` -- and no `branch`.
    ledger_rows = _table_matching(ledger.read_text(encoding="utf-8"), LEDGER_CONCEPTS)
    if not ledger_rows:
        return False
    by_id: dict[str, list[str]] = {}
    for row in ledger_rows:
        if len(row) != len(LEDGER_CONCEPTS):
            return False  # the cell count `validate-tasks.py:287` hard-fails as `C2`
        by_id[row[LEDGER_ID]] = row
    rows_for: dict[str, list[str]] = {}
    for unit in parsed:
        row = by_id.get(unit["id"])
        if row is None:
            return False
        if not UNIT_ID_RE.match(row[LEDGER_ID]):
            return False
        if not LEDGER_TITLE_RE.match(row[LEDGER_TITLE]):
            return False
        if row[LEDGER_OWNER] != unit["agent"]:
            return False
        if not row[LEDGER_STATUS]:
            return False
        rows_for[unit["id"]] = row

    # Assertion A -- step 2: "Self-contained (no cross-unit dependencies within a batch)", read from
    # the ledger row's own `Depends on` cell, which step 5 declares is where it lives. A dependency
    # on a task *outside* the batch is explicitly permitted and is not a violation.
    for unit in parsed:
        for dep in DEPENDS_ID_RE.findall(rows_for[unit["id"]][LEDGER_DEPENDS]):
            if dep in unit_ids and dep != unit["id"]:
                return False  # a cross-unit dependency inside the batch
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
