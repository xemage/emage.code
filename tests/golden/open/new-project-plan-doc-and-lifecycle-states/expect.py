#!/usr/bin/env python3
"""expect.py for new-project-plan-doc-and-lifecycle-states.

Contract under test: implementation/knowledge/commands/new-project.md --
  Phase 1 step 1 "Create a plan document with task decomposition and dependency graph -- Write
  the plan to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
  -- Include: objective, scope, task DAG
  (Mermaid), risk assessment, estimated phases",
  Phase 5 step 19 "Build an initial task dependency graph with lifecycle states -- Track states:
  `pending -> in_progress -> blocked -> in_review -> done | cancelled` -- The state is spelled
  `in_review`, NOT `review`. -- Write active tasks to `docs/tasks/active-tasks.md`".

Both steps name a file, which is why these two are the checkable pair: step 2's plan presentation
and approval is a chat interaction with no declared artifact. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Step 19's declared state set, verbatim from the arrow chain.
DECLARED_STATES = frozenset(
    {"pending", "in_progress", "blocked", "in_review", "done", "cancelled"}
)
# Step 1's declared plan filename: plan-<ID>.md, <ID> a three-digit number, a hyphen and a slug of
# lowercase letters, digits, hyphens and dots (plan-approve-execute § File Location). This pattern
# predates that form and is unchanged: it admits every such name whose slug has no dot, and also an
# unnumbered plan-<slug>.md. See brief.md § Provenance.
PLAN_NAME_RE = re.compile(r"^plan-[a-z0-9][a-z0-9-]*\.md$")
# Step 1's five declared contents, matched by concept -- the command declares content, not headings.
PLAN_CONTENT_CONCEPTS = (
    re.compile(r"^#{1,3}\s+.*\bobjective\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^#{1,3}\s+.*\bscope\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^#{1,3}\s+.*\b(task\s+dag|dependency\s+graph)\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^#{1,3}\s+.*\brisk\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^#{1,3}\s+.*\bphases?\b", re.IGNORECASE | re.MULTILINE),
)
MERMAID_FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
MERMAID_GRAPH_RE = re.compile(r"^\s*(graph|flowchart)\s+\w+", re.MULTILINE)
MERMAID_EDGE_RE = re.compile(r"-{2,}>")
STATUS_HEADER_RE = re.compile(r"^(status|state)$", re.IGNORECASE)
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _plan_ok(plans_dir: Path) -> bool:
    if not plans_dir.is_dir():
        return False
    plans = sorted(p for p in plans_dir.glob("*.md") if PLAN_NAME_RE.match(p.name))
    if len(plans) != 1:
        return False
    text = plans[0].read_text(encoding="utf-8")
    if any(not concept.search(text) for concept in PLAN_CONTENT_CONCEPTS):
        return False
    # "task DAG (Mermaid)" -- a Mermaid graph with at least one dependency edge, not a prose list.
    for body in MERMAID_FENCE_RE.findall(text):
        if MERMAID_GRAPH_RE.search(body) and MERMAID_EDGE_RE.search(body):
            return True
    return False


def _statuses(ledger_path: Path) -> list[str] | None:
    """Every status cell in the ledger, located from the table's own header row so the check
    does not hardcode a column index. None if no status column can be found."""
    try:
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    status_idx: int | None = None
    statuses: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("|") or SEPARATOR_ROW_RE.match(stripped):
            continue
        cells = _cells(stripped)
        if status_idx is None:
            for idx, cell in enumerate(cells):
                if STATUS_HEADER_RE.match(cell):
                    status_idx = idx
                    break
            continue
        if status_idx >= len(cells):
            return None  # a row that cannot carry a status at all
        statuses.append(cells[status_idx])
    if status_idx is None:
        return None
    return statuses


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    if not _plan_ok(fixture / "docs" / "plans"):
        return False

    statuses = _statuses(fixture / "docs" / "tasks" / "active-tasks.md")
    if not statuses:
        return False  # step 19: active tasks are written to this file
    # Step 19's declared state set, which mechanically excludes the `review` misspelling the
    # command calls out by name.
    return all(status in DECLARED_STATES for status in statuses)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
