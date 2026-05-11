#!/usr/bin/env python3
"""Single test entry point used by CI, Make, and humans.

Usage:
    python3 tests/run.py                  # all suites
    python3 tests/run.py --suite functional
    python3 tests/run.py --suite performance
    python3 tests/run.py -v               # verbose

Exits with non-zero status on any failure.
"""
from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

# Ensure the repo root is on sys.path so `tests.*` and `tests._helpers.*` import
HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

SUITES = {
    "functional": "tests/functional",
    "performance": "tests/performance",
}


def build_suite(suite_name: str | None) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    if suite_name:
        if suite_name not in SUITES:
            raise SystemExit(f"unknown suite: {suite_name}. Choose from {sorted(SUITES)}")
        return loader.discover(start_dir=str(REPO_ROOT / SUITES[suite_name]),
                               top_level_dir=str(REPO_ROOT))
    combined = unittest.TestSuite()
    for path in SUITES.values():
        combined.addTests(loader.discover(start_dir=str(REPO_ROOT / path),
                                          top_level_dir=str(REPO_ROOT)))
    return combined


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--suite", choices=sorted(SUITES))
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    suite = build_suite(args.suite)
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
