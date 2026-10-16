#!/usr/bin/env python3
"""expect.py for validate-workflow-gate-verdict-sources.

Contract under test: implementation/knowledge/commands/validate-workflow.md
`## Validation Gate References` steps 5 and 6, as amended by T567, verbatim in brief.md:

  5. Check all validation gates. Gate types, executors and the VERDICT format are defined in the
     `validation-gates` skill (SS Gate Types, SS Verdict Format) ... Each gate below names where it
     is defined: [the skill's five gate types, each with a cited Gate Types row, in the order of
     the skill's SS Procedures > 4. Gate Pipeline for a Release]
  6. For each gate, verify: ... Gate produces a VERDICT ...

check() is the AND of three predicates, all evaluated against byte-identical fixture copies of the
command file and of the `validation-gates` skill it cites:

  1. Per-gate (unchanged from the pre-T568 check): step 6's second verification, gate by gate. A
     gate "produces a VERDICT" iff its cited definition either (a) is a row of the skill's Gate
     Types table whose gate kind is admitted by that skill's Verdict Format `**Gate:**` field -- the
     format step 5 names -- or (b) itself declares a VERDICT. Every gate must, or the declared
     `Status: PASS` is unreachable: the Failure mode makes a gate that "doesn't produce a VERDICT"
     force the overall VERDICT to FAIL.
  2. Completeness: the `row:` kinds in GATES equal the non-empty set of kinds the Verdict Format's
     `**Gate:**` field admits, so a list that omits any gate kind fails ("Check all validation
     gates").
  3. Ordered list fidelity: the gate names listed under the fixture command's step 5 equal
     list(GATES), in order, so this check's mirror of step 5 cannot drift from the command.

Expected today: True (expected_pass), resolved by
docs/artifacts/validate-workflow-gate-resolution-v1.md. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

KNOWLEDGE = Path("implementation/knowledge")
VG = KNOWLEDGE / "skills/validation-gates/SKILL.md"
CMD = KNOWLEDGE / "commands/validate-workflow.md"

# Step 5's five gates, in its order, each with the definition it cites:
# (file, heading path, row/step selector).
GATES = {
    "Architecture review gate": (VG, ("## Gate Types",), "row:Architecture"),
    "Code review gate": (VG, ("## Gate Types",), "row:Implementation"),
    "Integration checkpoint gate": (VG, ("## Gate Types",), "row:Integration"),
    "Security audit gate": (VG, ("## Gate Types",), "row:Security"),
    "Release gate": (VG, ("## Gate Types",), "row:Release"),
}
STEP5_ANCHOR = "5. **Check all validation gates.**"
STEP5_BULLET_RE = re.compile(r"^   - (.+?) — ")
NEXT_STEP_RE = re.compile(r"^\d+\. ")
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


def gates_complete(fixture: Path) -> bool:
    """GATES' row kinds equal the (non-empty) kinds the Verdict Format's **Gate:** field admits."""
    try:
        vg_text = (fixture / VG).read_text(encoding="utf-8")
    except OSError:
        return False
    admitted = _verdict_gate_kinds(vg_text)
    listed = {sel.split(":", 1)[1].lower()
              for _rel, _path, sel in GATES.values() if sel and sel.startswith("row:")}
    return bool(admitted) and listed == admitted


def step5_gate_names(fixture: Path) -> list[str] | None:
    """Ordered gate names in the fixture command's step 5 list, or None if step 5 is absent."""
    try:
        text = (fixture / CMD).read_text(encoding="utf-8")
    except OSError:
        return None
    lines = _unfenced_lines(text)
    start = next((i for i, (line, fenced) in enumerate(lines)
                  if not fenced and line.startswith(STEP5_ANCHOR)), None)
    if start is None:
        return None
    names = []
    for line, _fenced in lines[start + 1:]:
        if NEXT_STEP_RE.match(line):
            break
        m = STEP5_BULLET_RE.match(line)
        if m:
            names.append(m.group(1))
    return names


def list_matches_command(fixture: Path) -> bool:
    """The command's step 5 gate list equals list(GATES), in order."""
    return step5_gate_names(fixture) == list(GATES)


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    per_gate = all(gate_produces_verdict(fixture, gate) for gate in GATES)
    return per_gate and gates_complete(fixture) and list_matches_command(fixture)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    case_dir = Path(sys.argv[1]).resolve()
    fixture = case_dir / "fixture"
    for gate in GATES:
        print(f"{gate}: produces VERDICT = {gate_produces_verdict(fixture, gate)}")
    print(f"completeness (GATES kinds == Verdict Format kinds) = {gates_complete(fixture)}")
    print(f"ordered list fidelity (step 5 list == GATES) = {list_matches_command(fixture)}")
    return 0 if check(case_dir) else 1


if __name__ == "__main__":
    sys.exit(main())
