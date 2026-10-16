#!/usr/bin/env python3
"""expect.py for validate-tasks-fail-lines-verbatim.

Contract under test: implementation/knowledge/commands/validate-tasks.md, the two exit-code
bullets of its body --

    - Exit 0 -> report "TASK LEDGER: PASS".
    - Exit 1 -> report every `FAIL C<n>` line verbatim, then propose one fix per
      violation. Do NOT auto-fix C5, C6, or C8 -- ask the user which ledger is correct.

Both branches are checked. The fail branch's assertion is verbatim-completeness: every
`FAIL C<n>` line the real validator emitted must appear, byte for byte, in the agent's report.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FAIL_LINE_RE = re.compile(r"^FAIL C\d+: .+$")
PASS_HEADLINE = "TASK LEDGER: PASS"
NO_AUTOFIX_CODES = ("C5", "C6", "C8")
# Quoted from the contract sentence itself, not an invented report format. Matched
# case-insensitively: the phrase reads mid-sentence in the contract but naturally starts a
# sentence in a report, and letter case is not part of what the contract declares.
ASK_USER_PHRASE = "which ledger is correct"


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _fail_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if FAIL_LINE_RE.match(line)]


def _check_pass_run(run_dir: Path) -> bool:
    exit_code = _read(run_dir / "exit-code.txt")
    output = _read(run_dir / "validator-output.txt")
    report = _read(run_dir / "report.md")
    if exit_code is None or output is None or report is None:
        return False
    if exit_code.strip() != "0":
        return False
    if PASS_HEADLINE not in output:
        return False
    # Exit 0 -> report "TASK LEDGER: PASS", and no violation lines to carry over.
    return PASS_HEADLINE in report and not _fail_lines(report)


def _check_fail_run(run_dir: Path) -> bool:
    exit_code = _read(run_dir / "exit-code.txt")
    output = _read(run_dir / "validator-output.txt")
    report = _read(run_dir / "report.md")
    if exit_code is None or output is None or report is None:
        return False
    if exit_code.strip() != "1":
        return False

    emitted = _fail_lines(output)
    if not emitted:
        return False  # a vacuous violation set must not pass
    if any(line not in report for line in emitted):
        return False
    if PASS_HEADLINE in report:
        return False

    needs_user_question = any(
        line.startswith(f"FAIL {code}: ") for line in emitted for code in NO_AUTOFIX_CODES
    )
    if needs_user_question and ASK_USER_PHRASE not in report.lower():
        return False
    return True


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    return _check_pass_run(fixture / "pass-run") and _check_fail_run(fixture / "fail-run")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
