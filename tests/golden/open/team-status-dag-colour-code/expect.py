#!/usr/bin/env python3
"""expect.py for team-status-dag-colour-code.

Contract under test: implementation/knowledge/commands/team-status.md `## Task DAG Visualization`
step 7 and its four sub-bullets, verbatim:

  7. Produce a task dependency graph (Mermaid format)
     - Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes
     - Read `docs/tasks/completed-tasks.md` for `done` nodes -- `active-tasks.md` NEVER contains
       `done`
     - Reconstruct dependency edges for done nodes from the `Depends on` cells of active rows
     - Color code: done=green, in_progress=yellow, blocked=red, pending=gray, in_review=blue

plus the command's declared `Output format` headings. The load-bearing assertion is the colour code
itself: each node's class must resolve, through its `classDef ... fill:`, to the colour *family* the
node's real ledger status maps to. Class names are not asserted -- the clause declares colours, not
names. See brief.md for the hue bands and every reading deliberately not asserted.
"""
from __future__ import annotations

import colorsys
import re
import sys
from pathlib import Path

DECLARED_HEADINGS = (
    "## Team Status", "### Active Streams", "### Blockers", "### Role Workload",
    "### Recommended Next Actions", "### Checkpoint Delta", "### Task DAG", "### Velocity",
    "### Portfolio Dependencies",
)
# "Color code: done=green, in_progress=yellow, blocked=red, pending=gray, in_review=blue"
STATUS_TO_COLOUR = {
    "done": "green", "in_progress": "yellow", "blocked": "red",
    "pending": "gray", "in_review": "blue",
}
ACTIVE_STATUSES = ("pending", "in_progress", "blocked", "in_review")

MERMAID_FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
GRAPH_DECL_RE = re.compile(r"^\s*(graph|flowchart)\s+\w+", re.MULTILINE)
NODE_DECL_RE = re.compile(r"\b(T\d{3,})\s*[\[(]")
CLASS_ASSIGN_RE = re.compile(r"^\s*class\s+([T\d,\s]+?)\s+(\w+)\s*$", re.MULTILINE)
CLASSDEF_FILL_RE = re.compile(
    r"^\s*classDef\s+(\w+)\b[^\n]*?\bfill:\s*#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", re.MULTILINE
)
EDGE_RE = re.compile(r"\b(T\d{3,})\b[^\n]*?-{2,}>(?:\|[^|]*\|)?\s*\b(T\d{3,})\b")
DEPENDS_ID_RE = re.compile(r"\bT\d{3,}\b")  # as docs/tasks/validate-tasks.py tokenises it
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")


def colour_family(hex_code: str) -> str | None:
    """Classify a fill colour into the clause's five colour words by HSV hue band."""
    if len(hex_code) == 3:
        hex_code = "".join(ch * 2 for ch in hex_code)
    r, g, b = (int(hex_code[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, sat, _val = colorsys.rgb_to_hsv(r, g, b)
    if sat < 0.15:
        return "gray"
    deg = hue * 360
    bands = (("red", 0, 20), ("yellow", 40, 70), ("green", 75, 165), ("blue", 180, 260),
             ("red", 340, 360.1))
    return next((name for name, lo, hi in bands if lo <= deg < hi), None)


def _rows(path: Path) -> list[list[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows = []
    for raw in lines:
        s = raw.strip()
        if s.startswith("|") and not SEPARATOR_ROW_RE.match(s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and re.fullmatch(r"T\d{3,}", cells[0]):
                rows.append(cells)
    return rows


def _dag_section(text: str) -> str | None:
    m = re.search(r"^### Task DAG\s*$", text, re.MULTILINE)
    if not m:
        return None
    nxt = re.search(r"^#{2,3} ", text[m.end():], re.MULTILINE)
    return text[m.end():m.end() + nxt.start()] if nxt else text[m.end():]


def _headings_in_order(text: str) -> bool:
    pos = -1
    for heading in DECLARED_HEADINGS:
        m = re.search(rf"^{re.escape(heading)}\s*$", text[pos + 1:], re.MULTILINE)
        if not m:
            return False
        pos = pos + 1 + m.start()
    return True


def _node_colour_grounded(
    node: str, colour: str, active: dict[str, list[str]], completed: set[str]
) -> bool:
    """A done-coloured node is only in the completed ledger; any other colour must be the colour
    the node's real active-ledger status maps to."""
    if colour == STATUS_TO_COLOUR["done"]:
        return node in completed and node not in active
    if node not in active or node in completed:
        return False
    status = active[node][3]
    return status != "done" and STATUS_TO_COLOUR.get(status) == colour


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    report = fixture / "team-status.md"
    if not report.is_file():
        return False
    text = report.read_text(encoding="utf-8")
    if not _headings_in_order(text):
        return False
    if len([b for b in MERMAID_FENCE_RE.findall(text) if GRAPH_DECL_RE.search(b)]) != 1:
        return False
    section = _dag_section(text)
    fences = [b for b in MERMAID_FENCE_RE.findall(section or "") if GRAPH_DECL_RE.search(b)]
    if len(fences) != 1:
        return False  # the one graph must sit under `### Task DAG`
    body = fences[0]

    active = {r[0]: r for r in _rows(fixture / "docs/tasks/active-tasks.md") if len(r) == 7}
    completed = {r[0] for r in _rows(fixture / "docs/tasks/completed-tasks.md")}
    if not active or not completed:
        return False
    class_colour = {name: colour_family(h) for name, h in CLASSDEF_FILL_RE.findall(body)}

    nodes = set(NODE_DECL_RE.findall(body))
    assigned: dict[str, list[str]] = {}
    for ids, cls in CLASS_ASSIGN_RE.findall(body):
        for node in (n.strip() for n in ids.split(",")):
            if node:
                assigned.setdefault(node, []).append(cls)
    if not nodes or set(assigned) != nodes:
        return False
    for node, classes in assigned.items():
        if len(classes) != 1 or class_colour.get(classes[0]) is None:
            return False
        if not _node_colour_grounded(node, class_colour[classes[0]], active, completed):
            return False
    # Every pending/in_progress/blocked/in_review row of the active ledger is drawn.
    if any(r[3] in ACTIVE_STATUSES and tid not in nodes for tid, r in active.items()):
        return False
    # Every edge is backed by its source row's real `Depends on` cell -- never invented.
    for source, target in EDGE_RE.findall(body):
        if source not in active or target not in nodes:
            return False
        if target not in DEPENDS_ID_RE.findall(active[source][5]):
            return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
