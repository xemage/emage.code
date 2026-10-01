#!/usr/bin/env python3
"""expect.py for validate-workflow-gate-verdict-sources.

Contract under test: implementation/knowledge/commands/validate-workflow.md
`## Validation Gate References` steps 5 and 6, verbatim in brief.md:

  5. Check all validation gates. Gate types, executors and the VERDICT format are defined in the
     `validation-gates` skill (SS Gate Types, SS Verdict Format) ... Each gate below names where it
     is defined: [six gates, each with a cited definition]
  6. For each gate, verify: ... Gate produces a VERDICT ...

This check performs step 6's second verification deterministically, gate by gate, against
byte-identical copies of the three files step 5 cites. A gate "produces a VERDICT" iff its cited
definition either (a) is a row of the `validation-gates` skill's Gate Types table whose gate kind is
admitted by that skill's Verdict Format `**Gate:**` field -- the format step 5 names -- or (b) itself
declares a VERDICT. All six must, or the declared `Status: PASS` is unreachable: the command's own
Failure mode makes a gate that "doesn't produce a VERDICT" force the overall VERDICT to FAIL.

Expected today: False (known_failing / tracked_defect, parked item P9). See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

KNOWLEDGE = Path("implementation/knowledge")
VG = KNOWLEDGE / "skills/validation-gates/SKILL.md"
PAE = KNOWLEDGE / "skills/plan-approve-execute/SKILL.md"
ORCH = KNOWLEDGE / "agents/orchestrator.md"

# Step 5's six gates, each with the definition it cites: (file, heading path, row/step selector).
GATES = {
    "Plan approval gate": (PAE, ("## The Three Phases", "### Phase 2: Approve"), None),
    "Architecture briefing gate": (
        ORCH, ("## Core Workflow", "### Phase 3: Development (Parallel Execution)"), "step:1"),
    "Integration checkpoint gate": (VG, ("## Gate Types",), "row:Integration"),
    "Code review gate": (VG, ("## Gate Types",), "row:Implementation"),
    "Security audit gate": (VG, ("## Gate Types",), "row:Security"),
    "Release gate": (VG, ("## Gate Types",), "row:Release"),
}
VERDICT_WORD_RE = re.compile(r"\bverdict\b", re.IGNORECASE)
GATE_FIELD_RE = re.compile(r"^\*\*Gate:\*\*\s*(.+)$", re.MULTILINE)


def _unfenced_lines(text: str) -> list[tuple[str, bool]]:
    """(line, is_inside_code_fence) for every line."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append((line, True))
            continue
        out.append((line, fenced))
    return out


def _section(text: str, path: tuple[str, ...]) -> str | None:
    """Body of the heading path's last heading, stopping at the next heading of equal/higher level."""
    lines, idx = _unfenced_lines(text), 0
    for heading in path:
        level = heading.split(" ", 1)[0]
        idx = next((i for i in range(idx, len(lines))
                    if not lines[i][1] and lines[i][0].strip() == heading), None)
        if idx is None:
            return None
        idx += 1
    body = []
    for line, fenced in lines[idx:]:
        m = re.match(r"^(#{1,6}) ", line)
        if m and not fenced and len(m.group(1)) <= len(level):
            break
        body.append(line)
    return "\n".join(body)


def _select(section: str, selector: str | None) -> str | None:
    if selector is None:
        return section
    kind, key = selector.split(":", 1)
    for line in section.splitlines():
        if kind == "step" and re.match(rf"^{re.escape(key)}\.\s", line):
            return line
        if kind == "row" and re.match(rf"^\|\s*\*\*{re.escape(key)}\*\*\s*\|", line):
            return line
    return None


def _verdict_gate_kinds(vg_text: str) -> set[str]:
    fmt = _section(vg_text, ("## Verdict Format",)) or ""
    if not re.search(r"every gate must produce a verdict", fmt, re.IGNORECASE):
        return set()
    m = GATE_FIELD_RE.search(fmt)
    return {k.strip().lower() for k in m.group(1).split("|")} if m else set()


def gate_produces_verdict(fixture: Path, gate: str) -> bool:
    rel, path, selector = GATES[gate]
    try:
        text = (fixture / rel).read_text(encoding="utf-8")
        vg_text = (fixture / VG).read_text(encoding="utf-8")
    except OSError:
        return False
    section = _section(text, path)
    definition = _select(section, selector) if section is not None else None
    if definition is None:
        return False  # the citation does not resolve to a definition
    if rel == VG and selector and selector.startswith("row:"):
        if selector.split(":", 1)[1].lower() in _verdict_gate_kinds(vg_text):
            return True
    return bool(VERDICT_WORD_RE.search(definition))


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    return all(gate_produces_verdict(fixture, gate) for gate in GATES)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    case_dir = Path(sys.argv[1]).resolve()
    for gate in GATES:
        print(f"{gate}: produces VERDICT = {gate_produces_verdict(case_dir / 'fixture', gate)}")
    return 0 if check(case_dir) else 1


if __name__ == "__main__":
    sys.exit(main())
