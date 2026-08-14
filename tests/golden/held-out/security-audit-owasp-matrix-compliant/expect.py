#!/usr/bin/env python3
"""expect.py for security-audit-owasp-matrix-compliant.

Contract under test: implementation/knowledge/commands/security-audit.md -- OWASP Coverage
Matrix (10 rows A01-A10) plus a "## VERDICT" block with Status/CRITICAL findings/HIGH
findings/MEDIUM findings/LOW findings/OWASP coverage/Blocker IDs/Auditor/Timestamp fields.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

OWASP_CATEGORIES = [f"A{i:02d}" for i in range(1, 11)]
REQUIRED_VERDICT_FIELDS = [
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

    for field in REQUIRED_VERDICT_FIELDS:
        if not re.search(rf"\*\*{re.escape(field)}\*\*\s*:", section):
            return False

    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
