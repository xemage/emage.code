#!/usr/bin/env python3
"""expect.py for security-audit-coverage-consistency.

Contract under test: implementation/knowledge/commands/security-audit.md -- the declared
"OWASP coverage: n/10 categories assessed" field must match the actual number of distinct A0X
rows present in the matrix (a scoped, less-than-10 audit is legitimate; the field must be
self-consistent regardless).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check(case_dir: Path) -> bool:
    audit_file = case_dir / "fixture" / "audit.md"
    if not audit_file.is_file():
        return False
    text = audit_file.read_text(encoding="utf-8")

    rows = set(re.findall(r"\|\s*(A(?:0[1-9]|10))\s*\|", text))
    coverage_match = re.search(r"\*\*OWASP coverage\*\*\s*:\s*(\d+)\s*/\s*10", text)
    if not coverage_match:
        return False

    declared_n = int(coverage_match.group(1))
    return declared_n == len(rows)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
