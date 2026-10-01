#!/usr/bin/env python3
"""expect.py for evaluate-poc-verdict-debt-reconciliation.

Contract under test: implementation/knowledge/commands/evaluate-poc.md, verbatim in brief.md --
step 9's `## POC VERDICT` block (eight fields, three enums, a severity-broken-down count), step 11's
Debt Summary table, step 10's handoff checklist ("If recommending `proceed` or
`proceed_with_constraints`"), step 6's "top 5 minimum" backlog, and the `## Rails` Failure mode
("If evidence strength is weak, ... returns `INVALIDATED` with `Evidence strength: weak`"), asserted
in full as "weak evidence => INVALIDATED". The value scales are the contract as amended by T564
(poc-contract-resolution-v1.md SS3b, SS5): a binary Status, three severities CRITICAL/MEDIUM/LOW,
effort S/M/L. `INCONCLUSIVE`, `HIGH` and `XL` are rejected outright, never ignored (SS9.2). The
load-bearing assertion is that the VERDICT's `Debt items` count and per-severity breakdown
reconcile with the Debt Summary rows.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

FIELDS = ("Hypothesis", "Status", "Production recommendation", "Evidence strength", "Debt items",
          "Residual risks", "Evaluator", "Timestamp")
STATUS = {"VALIDATED", "INVALIDATED"}
RECOMMENDATION = {"proceed", "proceed_with_constraints", "do_not_proceed"}
STRENGTH = {"strong", "moderate", "weak"}
SEVERITIES = ("CRITICAL", "MEDIUM", "LOW")
EFFORT = {"S", "M", "L"}
IMPACT = {"blocks", "degrades", "cosmetic"}
DEBT_HEADER = ["#", "Debt Item", "Severity", "Effort", "Risk", "Owner", "Production Impact"]
DEBT_ITEMS_RE = re.compile(
    r"^(\d+) \(CRITICAL: (\d+), MEDIUM: (\d+), LOW: (\d+)\)$")
CHECKLIST = (
    "All CRITICAL debt items have remediation plans with owners",
    "Architecture decisions documented in `docs/decisions/`",
    "Security audit completed (or scheduled for Phase 1)",
    "Performance baselines established",
    "Test coverage plan defined for production code",
    "Data migration/seeding strategy defined (if applicable)",
    "Monitoring and alerting requirements captured",
    "Production infrastructure requirements documented",
)
FIELD_RE = re.compile(r"^- \*\*(.+?)\*\*:\s*(.*?)\s*$")


def _section(text: str, heading: str) -> str | None:
    hits = list(re.finditer(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE))
    if len(hits) != 1:
        return None
    rest = text[hits[0].end():]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


def _verdict(text: str) -> dict[str, str] | None:
    block = _section(text, "POC VERDICT")
    if block is None:
        return None
    pairs = [FIELD_RE.match(ln).groups() for ln in block.splitlines() if FIELD_RE.match(ln)]
    if [k for k, _ in pairs] != list(FIELDS):
        return None
    return dict(pairs)


def _debt_rows(text: str) -> list[list[str]] | None:
    block = _section(text, "Debt Summary")
    if block is None:
        return None
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith("|")]
    cells = [[c.strip() for c in ln.strip("|").split("|")] for ln in lines]
    if len(cells) < 2 or cells[0] != DEBT_HEADER or not re.fullmatch(r"[\s:|-]+", lines[1]):
        return None
    return cells[2:]


def _iso8601(value: str) -> bool:
    if "T" not in value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _rows_valid(rows: list[list[str]]) -> bool:
    for n, row in enumerate(rows, start=1):
        if len(row) != 7 or row[0] != str(n):
            return False
        _, item, sev, effort, risk, owner, impact = row
        if not (item and risk and owner) or sev not in SEVERITIES:
            return False
        if effort not in EFFORT or impact not in IMPACT:
            return False
    return True


def _backlog_size(text: str) -> int:
    hits = [m for m in re.finditer(r"^## (.*backlog.*)$", text, re.MULTILINE | re.IGNORECASE)]
    if len(hits) != 1:
        return 0
    body = _section(text, hits[0].group(1).strip()) or ""
    return len(re.findall(r"^\d+\.\s+\S", body, re.MULTILINE))


def check(case_dir: Path) -> bool:
    report = case_dir / "fixture" / "poc-evaluation.md"
    if not report.is_file():
        return False
    text = report.read_text(encoding="utf-8")
    v = _verdict(text)
    if v is None or not v["Hypothesis"]:
        return False
    if v["Status"] not in STATUS or v["Production recommendation"] not in RECOMMENDATION:
        return False
    if v["Evidence strength"] not in STRENGTH:
        return False
    if v["Evidence strength"] == "weak" and v["Status"] != "INVALIDATED":
        # Rails Failure mode, in full: weak evidence returns INVALIDATED (poc-guidelines Rules 3-4).
        return False
    if not re.fullmatch(r"\d+", v["Residual risks"]) or v["Evaluator"] != "poc-orchestrator":
        return False
    if not _iso8601(v["Timestamp"]):
        return False

    m = DEBT_ITEMS_RE.match(v["Debt items"])
    rows = _debt_rows(text)
    if not m or rows is None or not _rows_valid(rows):
        return False
    total, *by_sev = (int(g) for g in m.groups())
    if total != sum(by_sev) or total != len(rows):
        return False
    if by_sev != [sum(1 for r in rows if r[2] == s) for s in SEVERITIES]:
        return False  # the VERDICT's breakdown reconciles with the table, severity by severity

    if v["Production recommendation"] in {"proceed", "proceed_with_constraints"}:
        boxes = set(re.findall(r"^- \[[ xX]\] (.+?)\s*$", text, re.MULTILINE))
        if any(item not in boxes for item in CHECKLIST):
            return False
    return _backlog_size(text) >= 5


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
