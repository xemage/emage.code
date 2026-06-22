#!/usr/bin/env python3
"""Regenerate the Pattern A integration report from current test outcomes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.pattern_a_report import build_pattern_a_report
from tests._helpers.repo import repo_root


REPORT_PATH = Path("tests/_reports/pattern-a-integration-report-v1.json")


def main() -> int:
    report_path = repo_root() / REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_pattern_a_report()
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"updated {REPORT_PATH}")
    print(
        "summary: "
        f"passed={payload['summary']['passed']} "
        f"failed={payload['summary']['failed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
