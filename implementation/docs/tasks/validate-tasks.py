#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

ID_RE = re.compile(r"^T\d{3,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUS_SET = {"pending", "in_progress", "blocked", "in_review", "done", "cancelled"}
PRIORITY_SET = {"P0", "P1", "P2"}
EXACT_BRIEF_RE = re.compile(r"^task-(T\d{3,})\.md$")
ANY_BRIEF_RE = re.compile(r"^task-(T\d{3,}).*\.md$")
STATUS_LINE_RE = re.compile(r"^\*\*Status:\*\*\s*([A-Za-z_]+)\s*$", re.MULTILINE)
ALT_STATUS_LINE_RE = re.compile(r"^\*\*Status\*\*:\s*([A-Za-z_]+)\s*$", re.MULTILINE)

# C11 -- declared `**Affects:**` field (T516).
#
# `maturity-promotion-criteria-v2.md` section 3.5 decides whether a component
# has an open defect by reading this field, and nothing else. It is mandatory
# on every active P0/P1 brief: an absent field must never be read as "this
# task affects nothing", because that turns a loud false positive (a component
# wrongly blocked) into a silent false negative (a component with a real open
# defect promoted while the gate still prints PASS).
#
# Kept deliberately in sync with, but independent of, the same parsing in
# implementation/scripts/check-maturity.py -- this validator ships standalone
# into target repos that have no copy of that script.
AFFECTS_LINE_RE = re.compile(r"^\*\*Affects:\*\*[ \t]*(.*)$", re.MULTILINE)
ALT_AFFECTS_LINE_RE = re.compile(r"^\*\*Affects\*\*:[ \t]*(.*)$", re.MULTILINE)
AFFECTS_NONE_TOKENS = {"—", "–", "-", "--"}
AFFECTS_CATEGORIES = ("agent", "command", "instruction", "skill")
AFFECTS_ENTRY_RE = re.compile(
    r"^(" + "|".join(AFFECTS_CATEGORIES) + r")/([A-Za-z0-9][A-Za-z0-9._-]*)$"
)
AFFECTS_REQUIRED_PRIORITIES = {"P0", "P1"}

# C12 -- a declared `Depends on` must resolve to a real task (T537).
#
# Before T537 the sixth cell of an active row was destructured into `_` and
# never read, so a row declaring a dependency on a task present in *neither*
# ledger passed `TASK LEDGER: PASS` in silence. Those edges are what
# `/sprint-status` reconstructs its dependency DAG from, and queue ordering has
# leaned on them: an unvalidated edge is a dependency nobody is checking.
#
# Resolution is against the union of BOTH ledgers. A *satisfied* dependency
# normally points into `completed-tasks.md` -- resolving against the active
# ledger alone would flag every satisfied dependency as dangling and make the
# check worse than useless.
#
# Extraction is deliberately token-based rather than shape-based. The corpus
# writes this cell as the `—` em-dash placeholder, as a bare `T531`, and
# historically also as `None`, `none`, `T454 (done), T455 (done), T458
# (pending)`, and prose such as `none (soft: T505)`. Only ID-shaped tokens are
# resolved and every other character is ignored, so the check fires on exactly
# the defect it names -- an ID that resolves to nothing -- and never on the
# annotation style wrapped around it.
DEPENDS_ID_RE = re.compile(r"\bT\d{3,}\b")

# C13 -- no active row declares a dependency on itself (T540).
#
# A self-dependency satisfies C12: the ID resolves, because the row's own ID is
# in `active_ids`. It is still never a real edge -- it is a length-one cycle
# that leaves the row permanently unschedulable, and in practice it reads as the
# ID cell copied into the dependency cell. It gets its own code rather than an
# extension of C12 because the operator's fix differs (delete the edge, not
# correct its target) and because C12 carries exactly one message -- "exists in
# neither ledger" -- which is actively false for this defect.
#
# C14 -- the active dependency graph is acyclic (T540).
#
# `/sprint-status` reconstructs a DAG from these edges and orders the queue from
# it. A cycle has no topological order, so it breaks that consumer outright
# rather than merely misinforming it. Its own code, because the failure belongs
# to a set of rows rather than to one row: the message names the whole chain,
# since no single row in a cycle is the one at fault.
#
# The search covers active rows only. `completed-tasks.md` has no dependency
# column, so an edge pointing into it is a leaf and can never close a cycle.
# Self-edges are excluded here and left to C13, so each defect is reported once,
# under the more specific of the two codes.


class Row:
    def __init__(self, line_no: int, cells: list[str]) -> None:
        self.line_no = line_no
        self.cells = cells



def pick_base_dir() -> Path:
    cwd_tasks = Path.cwd() / "docs" / "tasks"
    if cwd_tasks.is_dir():
        return cwd_tasks
    return Path(__file__).resolve().parent



def parse_table_rows(path: Path) -> list[Row]:
    if not path.exists():
        return []

    rows: list[Row] = []
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped.startswith("|"):
            continue
        parts = [p.strip() for p in stripped.split("|")]
        if len(parts) < 3:
            continue
        cells = parts[1:-1]
        if not cells:
            continue

        id_cell = cells[0]
        if id_cell == "ID":
            continue
        if id_cell and set(id_cell) <= {"-", ":"}:
            continue

        rows.append(Row(idx, cells))
    return rows



def parse_date(raw: str) -> dt.date | None:
    if not DATE_RE.fullmatch(raw):
        return None
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        return None



def get_brief_status(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    m = STATUS_LINE_RE.search(text)
    if m:
        return m.group(1).strip().lower()
    m = ALT_STATUS_LINE_RE.search(text)
    if m:
        return m.group(1).strip().lower()
    return None



def get_brief_affects(path: Path) -> str | None:
    """Return the raw right-hand side of a brief's `**Affects:**` line."""
    text = path.read_text(encoding="utf-8")
    m = AFFECTS_LINE_RE.search(text) or ALT_AFFECTS_LINE_RE.search(text)
    return m.group(1).strip() if m else None


def known_component_keys(base: Path) -> set[str]:
    """`{"<category>/<id>", ...}` from the registry index, when one is present.

    Best effort on purpose: this validator also ships into target repos that
    carry no registry. When the set comes back empty, C11 still enforces the
    field's presence and shape; `check-maturity.py` remains authoritative for
    rejecting entries that name a component which does not exist.
    """
    for candidate in (base, *base.parents):
        index = candidate / "implementation" / "registry" / "index.json"
        if not index.is_file():
            continue
        try:
            data = json.loads(index.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return set()
        keys = set()
        for entry in data.get("entries", []):
            category, ident = entry.get("category"), entry.get("id")
            if category and ident:
                keys.add(f"{category}/{ident}")
        return keys
    return set()


def affects_errors(raw: str, known: set[str]) -> list[str]:
    """Validate one `**Affects:**` value; returns a list of human-readable errors."""
    if not raw:
        return ["`**Affects:**` is present but empty (use `—` for 'no component')"]
    if raw in AFFECTS_NONE_TOKENS:
        return []

    errors: list[str] = []
    declared = 0
    for part in raw.split(","):
        entry = part.strip().strip("`")
        if not entry:
            continue
        if entry in AFFECTS_NONE_TOKENS:
            errors.append("`—` cannot be combined with other entries")
            continue
        if not AFFECTS_ENTRY_RE.match(entry):
            errors.append(
                f"malformed `**Affects:**` entry '{entry}' (expected `<category>/<id>` with "
                f"category one of {'/'.join(AFFECTS_CATEGORIES)}, or `—`)"
            )
            continue
        if known and entry not in known:
            errors.append(f"`**Affects:**` entry '{entry}' names no existing component")
            continue
        declared += 1
    if not declared and not errors:
        errors.append(f"`**Affects:**` value '{raw}' declares nothing (use `—` for 'no component')")
    return errors


def dependency_cycles(edges: dict[str, set[str]]) -> list[list[str]]:
    """Return every dependency cycle in `edges` as an ordered list of node IDs.

    Iterative depth-first search. On a back edge into the current path, the path
    is sliced from the revisited node onward, which yields the actual chain an
    operator has to break rather than an unordered component. Roots and
    neighbours are walked in sorted order and each cycle is keyed on its node
    set, so repeated runs over one ledger report the same cycles in the same
    order, and report each of them once.
    """
    cycles: list[list[str]] = []
    reported: set[frozenset[str]] = set()
    done: set[str] = set()

    for root in sorted(edges):
        if root in done:
            continue
        path = [root]
        on_path = {root}
        stack = [(root, iter(sorted(edges[root])))]
        while stack:
            node, pending = stack[-1]
            descended = False
            for nxt in pending:
                if nxt == node or nxt not in edges or nxt in done:
                    continue
                if nxt in on_path:
                    cycle = path[path.index(nxt):]
                    key = frozenset(cycle)
                    if key not in reported:
                        reported.add(key)
                        cycles.append(cycle)
                    continue
                stack.append((nxt, iter(sorted(edges[nxt]))))
                path.append(nxt)
                on_path.add(nxt)
                descended = True
                break
            if not descended:
                stack.pop()
                done.add(node)
                on_path.discard(node)
                path.pop()
    return cycles


def add_fail(fails: list[tuple[str, str]], code: str, msg: str) -> None:
    fails.append((code, msg))



def main() -> int:
    base = pick_base_dir()
    active_path = base / "active-tasks.md"
    completed_path = base / "completed-tasks.md"

    fails: list[tuple[str, str]] = []

    if not active_path.exists():
        add_fail(fails, "C2", f"missing file: {active_path}")
    if not completed_path.exists():
        add_fail(fails, "C2", f"missing file: {completed_path}")

    active_rows = parse_table_rows(active_path)
    completed_rows = parse_table_rows(completed_path)

    active_ids: list[str] = []
    completed_ids: list[str] = []
    active_priorities: list[tuple[int, str, str]] = []
    active_depends: list[tuple[int, str, str]] = []

    # C1, C2, C3, C4, C10 for active
    for row in active_rows:
        if len(row.cells) != 7:
            add_fail(
                fails,
                "C2",
                f"active-tasks.md:{row.line_no} has {len(row.cells)} cells (expected 7)",
            )
            continue

        task_id, _, _, status, priority, depends_on, last_update = row.cells
        active_ids.append(task_id)
        active_priorities.append((row.line_no, task_id, priority))
        active_depends.append((row.line_no, task_id, depends_on))

        if status in {"done", "cancelled"}:
            add_fail(
                fails,
                "C1",
                f"active-tasks.md:{row.line_no} has terminal status '{status}' for {task_id}",
            )

        if not ID_RE.fullmatch(task_id):
            add_fail(fails, "C3", f"active-tasks.md:{row.line_no} invalid ID '{task_id}'")

        if status not in STATUS_SET:
            add_fail(fails, "C4", f"active-tasks.md:{row.line_no} invalid Status '{status}'")

        if priority not in PRIORITY_SET:
            add_fail(fails, "C4", f"active-tasks.md:{row.line_no} invalid Priority '{priority}'")

        if parse_date(last_update) is None:
            add_fail(
                fails,
                "C10",
                f"active-tasks.md:{row.line_no} invalid date '{last_update}'",
            )

    # C2, C3, C10 for completed
    completed_dates: list[tuple[int, str, dt.date | None]] = []
    for row in completed_rows:
        if len(row.cells) != 5:
            add_fail(
                fails,
                "C2",
                f"completed-tasks.md:{row.line_no} has {len(row.cells)} cells (expected 5)",
            )
            continue

        task_id, _, _, done_on, _ = row.cells
        completed_ids.append(task_id)

        if not ID_RE.fullmatch(task_id):
            add_fail(fails, "C3", f"completed-tasks.md:{row.line_no} invalid ID '{task_id}'")

        parsed = parse_date(done_on)
        if parsed is None:
            add_fail(fails, "C10", f"completed-tasks.md:{row.line_no} invalid date '{done_on}'")
        completed_dates.append((row.line_no, done_on, parsed))

    # C5 duplicates and overlap
    active_counts = Counter(active_ids)
    completed_counts = Counter(completed_ids)

    for task_id, count in active_counts.items():
        if count > 1:
            add_fail(fails, "C5", f"duplicate in active-tasks.md: {task_id} appears {count} times")

    for task_id, count in completed_counts.items():
        if count > 1:
            add_fail(fails, "C5", f"duplicate in completed-tasks.md: {task_id} appears {count} times")

    overlap = sorted(set(active_ids) & set(completed_ids))
    for task_id in overlap:
        add_fail(fails, "C5", f"ID appears in both ledgers: {task_id}")

    # C6 every task-T*.md appears in exactly one ledger
    any_briefs = sorted(p for p in base.glob("task-T*.md") if p.is_file())
    for brief in any_briefs:
        m = ANY_BRIEF_RE.fullmatch(brief.name)
        if not m:
            continue
        task_id = m.group(1)
        where = int(task_id in active_counts) + int(task_id in completed_counts)
        if where != 1:
            add_fail(
                fails,
                "C6",
                f"{brief.name} has ID {task_id} present in {where} ledgers (expected 1)",
            )

    # C7 every ledger ID has matching task-<ID>.md
    for task_id in sorted(set(active_ids + completed_ids)):
        exact = base / f"task-{task_id}.md"
        if not exact.exists():
            add_fail(fails, "C7", f"missing brief file: task-{task_id}.md")

    # C8 status cross-check
    exact_briefs = sorted(p for p in base.glob("task-T*.md") if p.is_file() and EXACT_BRIEF_RE.fullmatch(p.name))
    done_in_briefs: set[str] = set()
    status_map: dict[str, str | None] = {}

    for brief in exact_briefs:
        m = EXACT_BRIEF_RE.fullmatch(brief.name)
        if not m:
            continue
        task_id = m.group(1)
        status = get_brief_status(brief)
        status_map[task_id] = status
        if status == "done":
            done_in_briefs.add(task_id)

    for task_id in sorted(done_in_briefs):
        if task_id not in completed_counts:
            add_fail(
                fails,
                "C8",
                f"task-{task_id}.md says done but {task_id} is not in completed-tasks.md",
            )

    for task_id in sorted(set(completed_ids)):
        status = status_map.get(task_id)
        if status not in {"done", "cancelled"}:
            add_fail(
                fails,
                "C8",
                f"completed ID {task_id} has brief status '{status}' (expected done or cancelled)",
            )

    # C11 every active P0/P1 brief declares a well-formed `**Affects:**` field
    known = known_component_keys(base)
    for line_no, task_id, priority in active_priorities:
        brief = base / f"task-{task_id}.md"
        if not brief.is_file():
            if priority in AFFECTS_REQUIRED_PRIORITIES:
                add_fail(
                    fails,
                    "C11",
                    f"active-tasks.md:{line_no} {task_id} is {priority} but task-{task_id}.md "
                    "is missing, so its `**Affects:**` field cannot be read",
                )
            continue
        raw = get_brief_affects(brief)
        if raw is None:
            if priority in AFFECTS_REQUIRED_PRIORITIES:
                add_fail(
                    fails,
                    "C11",
                    f"task-{task_id}.md has no `**Affects:**` field; it is mandatory for "
                    f"{priority} briefs (declare `—` if the task indicts no component)",
                )
            continue
        for err in affects_errors(raw, known):
            add_fail(fails, "C11", f"task-{task_id}.md: {err}")

    # C9 completed done_on non-decreasing
    prev_date: dt.date | None = None
    prev_raw: str | None = None
    prev_line: int | None = None
    for line_no, raw, parsed in completed_dates:
        if parsed is None:
            continue
        if prev_date is not None and parsed < prev_date:
            add_fail(
                fails,
                "C9",
                f"completed-tasks.md:{line_no} date {raw} is earlier than {prev_raw} at line {prev_line}",
            )
        prev_date = parsed
        prev_raw = raw
        prev_line = line_no

    # C12 every ID named in an active row's `Depends on` exists in some ledger
    # C13 no active row declares a dependency on itself
    known_ids = set(active_ids) | set(completed_ids)
    active_id_set = set(active_ids)
    first_line: dict[str, int] = {}
    edges: dict[str, set[str]] = {task_id: set() for task_id in active_id_set}
    for line_no, task_id, raw_depends in active_depends:
        first_line.setdefault(task_id, line_no)
        for dep in DEPENDS_ID_RE.findall(raw_depends):
            if dep == task_id:
                add_fail(
                    fails,
                    "C13",
                    f"active-tasks.md:{line_no} {task_id} declares Depends on itself",
                )
                continue
            if dep in active_id_set:
                edges[task_id].add(dep)
                continue
            if dep in known_ids:
                continue
            add_fail(
                fails,
                "C12",
                f"active-tasks.md:{line_no} {task_id} declares Depends on '{dep}', "
                "which exists in neither ledger",
            )

    # C14 the active dependency graph is acyclic
    for cycle in dependency_cycles(edges):
        chain = " \u2192 ".join([*cycle, cycle[0]])
        add_fail(
            fails,
            "C14",
            f"active-tasks.md:{first_line[cycle[0]]} dependency cycle {chain} "
            "has no order that satisfies it; one of its edges must be removed",
        )

    if fails:
        for code, msg in fails:
            print(f"FAIL {code}: {msg}")
        print(f"TASK LEDGER: FAIL ({len(fails)} violations)")
        return 1

    print(f"TASK LEDGER: PASS ({len(active_rows)} active, {len(completed_rows)} completed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
