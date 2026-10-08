#!/usr/bin/env python3
"""expect.py for security-audit-critical-not-fail (known_failing / capability_gap).

Contract under test: implementation/knowledge/commands/security-audit.md -- "If any CRITICAL
or HIGH finding exists, … the verdict MUST be FAIL" (as amended by T582, B3). Expected to return
False today -- see brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _verdict_section(text: str) -> str:
    # Scope matching to the real "## VERDICT" block so an earlier, informal field mention
    # elsewhere in the document (e.g. in a "## Summary" section) is never picked up instead of
    # the real, later field. Falls back to the whole document if no "## VERDICT" heading is
    # present, preserving prior behavior for documents without one.
    idx = text.find("## VERDICT")
    return text[idx:] if idx != -1 else text


def check(case_dir: Path) -> bool:
    audit_file = case_dir / "fixture" / "audit.md"
    if not audit_file.is_file():
        return False
    text = audit_file.read_text(encoding="utf-8")
    verdict_text = _verdict_section(text)

    critical_match = re.search(r"\*\*CRITICAL findings\*\*\s*:\s*(\d+)", text)
    status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", verdict_text)
    if not critical_match or not status_match:
        return False

    critical_count = int(critical_match.group(1))
    status = status_match.group(1)

    if critical_count > 0:
        return status == "FAIL"
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
