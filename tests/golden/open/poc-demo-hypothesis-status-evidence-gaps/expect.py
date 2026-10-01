#!/usr/bin/env python3
"""expect.py for poc-demo-hypothesis-status-evidence-gaps.

Contract under test: implementation/knowledge/commands/poc-demo.md, verbatim in brief.md --
`## Hypothesis Validation Status` step 8's `## Hypothesis Status` block (five fields, two enums),
the `## Rails` Failure mode ("If the demo cannot show evidence for the stated hypothesis, reports the
evidence gap explicitly in the Hypothesis Status block rather than omitting it"), and the Demo
Package deliverables 1-6 plus step 10's mocked/simulated call-out. Step 7's artifact links are not
asserted: every path it names is contested (P11, P12, checkpoint path) -- see brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BLOCK_HEADING = "## Hypothesis Status"
FIELDS = ("Hypothesis", "Validation status", "Key evidence demonstrated", "Evidence gaps",
          "Confidence level")
STATUS_VALUES = {"VALIDATED", "INVALIDATED", "INCONCLUSIVE", "IN_PROGRESS"}
CONFIDENCE_VALUES = {"HIGH", "MEDIUM", "LOW"}
# Statuses under which the demo has not shown evidence for the hypothesis (Failure mode).
NO_EVIDENCE_STATUSES = {"INCONCLUSIVE", "IN_PROGRESS"}
# Statuses that claim a decided outcome, which must be backed by demonstrated evidence.
DECIDED_STATUSES = {"VALIDATED", "INVALIDATED"}
NONE_LIKE = {"", "none", "n/a", "na", "-", "—", "–", "[]", "nothing", "tbd"}
# Demo Package items 1-6 and step 10, matched by concept against headings (no heading text is
# declared by the command, only the deliverables).
DELIVERABLES = (
    (r"walkthrough|script",),
    (r"sample data|input sequence",),
    (r"expected.*outcome|visible outcome",),
    (r"presenter", r"fallback"),
    (r"shortcut",),
    (r"production transition|transition note",),
    (r"mock|simulat",),
)
FIELD_RE = re.compile(r"^- \*\*(.+?)\*\*:\s*(.*)$")


def _headings(text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"^#{2,6}\s+(.+?)\s*$", text, re.MULTILINE)]


def _block(text: str) -> str | None:
    starts = [m for m in re.finditer(rf"^{re.escape(BLOCK_HEADING)}\s*$", text, re.MULTILINE)]
    if len(starts) != 1:
        return None
    rest = text[starts[0].end():]
    nxt = re.search(r"^#{1,2}\s", rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


def _fields(block: str) -> list[tuple[str, list[str]]]:
    """[(label, [inline value + sub-bullet items])] in order; continuation lines are folded."""
    out: list[tuple[str, list[str]]] = []
    for line in block.splitlines():
        m = FIELD_RE.match(line)
        if m:
            out.append((m.group(1), [m.group(2).strip()] if m.group(2).strip() else []))
        elif out and re.match(r"^\s+[-*]\s+\S", line):
            out[-1][1].append(re.sub(r"^\s+[-*]\s+", "", line).strip())
        elif out and line.startswith(" ") and line.strip() and out[-1][1]:
            out[-1][1][-1] += " " + line.strip()
    return out


def _present(values: list[str]) -> bool:
    return any(v.strip().strip(".").lower() not in NONE_LIKE for v in values)


def check(case_dir: Path) -> bool:
    demo = case_dir / "fixture" / "poc-demo.md"
    if not demo.is_file():
        return False
    text = demo.read_text(encoding="utf-8")

    headings = " | ".join(_headings(text)).lower()
    for concepts in DELIVERABLES:
        if not all(re.search(c, headings) for c in concepts):
            return False

    block = _block(text)
    if block is None:
        return False
    fields = _fields(block)
    if [label for label, _ in fields] != list(FIELDS):
        return False  # all five, each once, in declared order
    values = dict(fields)
    if not _present(values["Hypothesis"]):
        return False
    status = values["Validation status"]
    confidence = values["Confidence level"]
    if len(status) != 1 or status[0] not in STATUS_VALUES:
        return False
    if len(confidence) != 1 or confidence[0] not in CONFIDENCE_VALUES:
        return False
    if status[0] in NO_EVIDENCE_STATUSES and not _present(values["Evidence gaps"]):
        return False  # Failure mode: the gap is reported explicitly, never omitted
    if status[0] in DECIDED_STATUSES and not _present(values["Key evidence demonstrated"]):
        return False  # a decided outcome with nothing demonstrated is unsupported
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
