#!/usr/bin/env python3
"""expect.py for sprint-status-dag-ledger-grounded.

Contract under test: implementation/knowledge/commands/sprint-status.md `## Task DAG
Visualization` step 8 and its four sub-bullets, verbatim:

  8. Produce a task dependency graph (Mermaid format)
     - Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes
     - Read `docs/tasks/completed-tasks.md` for `done` nodes -- `active-tasks.md` NEVER contains
       `done`
     - Reconstruct dependency edges for done nodes from the `Depends on` cells of active rows
     - Color code: done=green, in_progress=yellow, blocked=red, pending=gray

plus the command's four declared `##` section headings. The load-bearing assertion is that every
node resolves to a real row in the *correct* ledger and carries the class its real status maps to.
See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DECLARED_SECTIONS = (
    "## Sprint Metrics",
    "## Task DAG Visualization",
    "## Checkpoint Metrics",
    "## Token Spend Summary",
)
# "Color code: done=green, in_progress=yellow, blocked=red, pending=gray" -- the four classes,
# named as the command's own template names them.
STATUS_TO_CLASS = {
    "pending": "pending",
    "in_progress": "inProgress",
    "blocked": "blocked",
}
DECLARED_CLASSDEFS = ("done", "inProgress", "blocked", "pending")
DONE_CLASS = "done"

MERMAID_FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
GRAPH_DECL_RE = re.compile(r"^\s*(graph|flowchart)\s+\w+", re.MULTILINE)
NODE_DECL_RE = re.compile(r"\b(T\d{3,})\s*[\[(]")
CLASS_ASSIGN_RE = re.compile(r"^\s*class\s+([T\d,\s]+?)\s+(\w+)\s*$", re.MULTILINE)
CLASSDEF_RE = re.compile(r"^\s*classDef\s+(\w+)\b", re.MULTILINE)
EDGE_RE = re.compile(r"\b(T\d{3,})\b[^\n]*?-{2,}>(?:\|[^|]*\|)?\s*\b(T\d{3,})\b")
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")
NO_DEPENDENCY_TOKENS = frozenset({"—", "–", "-", "--", ""})


def _ledger_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows
    for raw in lines:
        stripped = raw.strip()
        if not stripped.startswith("|") or SEPARATOR_ROW_RE.match(stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or cells[0] == "ID":
            continue
        rows.append(cells)
    return rows


def _active_index(path: Path) -> tuple[dict[str, str], dict[str, set[str]]]:
    """{task_id: status} and {task_id: declared dependency ids} from the 7-column active ledger."""
    statuses: dict[str, str] = {}
    depends: dict[str, set[str]] = {}
    for cells in _ledger_rows(path):
        if len(cells) != 7:
            continue
        task_id, _title, _owner, status, _priority, depends_on, _updated = cells
        if not re.fullmatch(r"T\d{3,}", task_id):
            continue
        statuses[task_id] = status
        deps = {
            token.strip()
            for token in depends_on.split(",")
            if token.strip() not in NO_DEPENDENCY_TOKENS
        }
        depends[task_id] = deps
    return statuses, depends


def _completed_ids(path: Path) -> set[str]:
    return {
        cells[0]
        for cells in _ledger_rows(path)
        if cells and re.fullmatch(r"T\d{3,}", cells[0])
    }


def _class_assignments(body: str) -> dict[str, list[str]]:
    assignments: dict[str, list[str]] = {}
    for ids, cls in CLASS_ASSIGN_RE.findall(body):
        for raw in ids.split(","):
            node = raw.strip()
            if node:
                assignments.setdefault(node, []).append(cls)
    return assignments


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    report_path = fixture / "sprint-status.md"
    active_path = fixture / "docs" / "tasks" / "active-tasks.md"
    completed_path = fixture / "docs" / "tasks" / "completed-tasks.md"
    if not report_path.is_file():
        return False
    text = report_path.read_text(encoding="utf-8")
    if any(section not in text for section in DECLARED_SECTIONS):
        return False

    fences = [body for body in MERMAID_FENCE_RE.findall(text) if GRAPH_DECL_RE.search(body)]
    if len(fences) != 1:
        return False
    body = fences[0]

    if any(name not in CLASSDEF_RE.findall(body) for name in DECLARED_CLASSDEFS):
        return False

    nodes = set(NODE_DECL_RE.findall(body))
    if not nodes:
        return False

    active_statuses, active_depends = _active_index(active_path)
    completed = _completed_ids(completed_path)
    if not active_statuses or not completed:
        return False  # both ledgers are named by the clause; neither may be unreadable

    assignments = _class_assignments(body)
    if set(assignments) != nodes:
        return False  # every node classed exactly once, and no class for an undeclared node
    for node, classes in assignments.items():
        if len(classes) != 1:
            return False
        cls = classes[0]
        if cls == DONE_CLASS:
            # "Read completed-tasks.md for done nodes -- active-tasks.md NEVER contains done"
            if node not in completed or node in active_statuses:
                return False
            continue
        if node not in active_statuses or node in completed:
            return False
        if STATUS_TO_CLASS.get(active_statuses[node]) != cls:
            return False

    # "Reconstruct dependency edges ... from the `Depends on` cells of active rows" -- and the
    # command's Rails: omit an unreconstructable edge rather than invent it.
    for source, target in EDGE_RE.findall(body):
        if source not in nodes or target not in nodes:
            return False
        if target not in active_depends.get(source, set()):
            return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
