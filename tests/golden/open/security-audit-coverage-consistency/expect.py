#!/usr/bin/env python3
"""expect.py for security-audit-coverage-consistency.

Contract under test: implementation/knowledge/commands/security-audit.md -- the declared
"OWASP coverage: n/10 categories assessed" field must be self-consistent with the matrix: it
must never exceed the number of distinct A0X rows actually present (that would be an inflated,
unsupported coverage claim), but it MAY legitimately be less than the row count -- the matrix is
allowed to list all 10 categories for completeness (including out-of-scope/not-assessed ones)
while the declared field honestly reports a narrower assessed/in-scope subset.
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
    # Self-consistency, not strict equality: the declared count can never exceed the number of
    # rows actually shown (an inflated claim), but a narrower declared count is legitimate when
    # the matrix lists additional rows for completeness (e.g. out-of-scope categories).
    return declared_n <= len(rows)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
