#!/usr/bin/env python3
"""expect.py for security-audit-verdict-fields-compliant.

Contract under test: implementation/knowledge/commands/security-audit.md -- VERDICT field
value-level format strictness (Status enum, ISO-8601 Timestamp, Blocker IDs "none" when
Status is PASS), on a full 10/10 audit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

OWASP_CATEGORIES = [f"A{i:02d}" for i in range(1, 11)]
REQUIRED_FIELDS = [
    "Status",
    "CRITICAL findings",
    "HIGH findings",
    "MEDIUM findings",
    "LOW findings",
    "OWASP coverage",
    "Blocker IDs",
    "Auditor",
    "Timestamp",
]
ALLOWED_STATUS = {"PASS", "CONDITIONAL_PASS", "FAIL"}
ISO8601_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def check(case_dir: Path) -> bool:
    audit_file = case_dir / "fixture" / "audit.md"
    if not audit_file.is_file():
        return False
    text = audit_file.read_text(encoding="utf-8")

    for cat in OWASP_CATEGORIES:
        if not re.search(rf"\|\s*{cat}\s*\|", text):
            return False

    verdict_idx = text.find("## VERDICT")
    if verdict_idx == -1:
        return False
    section = text[verdict_idx:]

    for field in REQUIRED_FIELDS:
        if not re.search(rf"\*\*{re.escape(field)}\*\*\s*:", section):
            return False

    status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", section)
    if not status_match or status_match.group(1) not in ALLOWED_STATUS:
        return False

    coverage_match = re.search(r"\*\*OWASP coverage\*\*\s*:\s*(\d+)\s*/\s*10", section)
    if not coverage_match or coverage_match.group(1) != "10":
        return False

    timestamp_match = re.search(r"\*\*Timestamp\*\*\s*:\s*(\S+)", section)
    if not timestamp_match or not ISO8601_RE.match(timestamp_match.group(1)):
        return False

    if status_match.group(1) == "PASS":
        blocker_match = re.search(r"\*\*Blocker IDs\*\*\s*:\s*(.+)", section)
        if not blocker_match or blocker_match.group(1).strip().lower() != "none":
            return False

    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
