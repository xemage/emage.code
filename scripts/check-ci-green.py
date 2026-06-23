#!/usr/bin/env python3
"""CI pipeline gate.

Verifies the latest GitLab CI pipeline for a branch is green before
development continues. This is the canonical enforcement of the rule:

    "Do not continue development (start/delegate new work, cut a release,
     or open a merge request) without confirming the latest CI pipeline
     on the target branch is GREEN."

The gate is intentionally tool-based (not advisory prose) so it can be
wired into the workflow via `make ci-gate` and run programmatically by
the orchestrator before delegating new tasks.

Usage:
    python3 scripts/check-ci-green.py                 # check current branch
    python3 scripts/check-ci-green.py --ref develop   # check a specific branch
    python3 scripts/check-ci-green.py --wait          # poll until terminal state
    python3 scripts/check-ci-green.py --wait --timeout 900

Exit codes:
    0  pipeline succeeded (GREEN — safe to continue)
    1  pipeline failed or canceled (RED — must fix before continuing)
    2  pipeline still running/pending (NOT YET GREEN — wait or re-run)
    3  tooling/lookup error (glab missing, no pipeline, bad ref)

Requires: `glab` authenticated against the project (HTTPS, no SSH).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from typing import Any, Optional

# Terminal states reported by the GitLab pipelines API.
_TERMINAL_OK = {"success"}
_TERMINAL_BAD = {"failed", "canceled"}
_PENDING = {"created", "waiting_for_resource", "preparing", "pending", "running", "scheduled"}

_EXIT_GREEN = 0
_EXIT_RED = 1
_EXIT_PENDING = 2
_EXIT_ERROR = 3


def _run_glab(args: list[str]) -> Optional[str]:
    """Run a `glab` command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["glab", *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        print("ERROR: `glab` CLI not found on PATH.", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("ERROR: `glab` command timed out.", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"ERROR: glab {' '.join(args)} failed:\n{result.stderr.strip()}", file=sys.stderr)
        return None
    return result.stdout


def _current_branch() -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    branch = out.stdout.strip()
    return branch or None


def _latest_pipeline(ref: str) -> Optional[dict[str, Any]]:
    raw = _run_glab(["api", f"/projects/:id/pipelines?ref={ref}&per_page=1"])
    if raw is None:
        return None
    try:
        pipelines = json.loads(raw)
    except json.JSONDecodeError:
        print("ERROR: could not parse pipeline list response.", file=sys.stderr)
        return None
    if not pipelines:
        print(f"ERROR: no pipelines found for ref '{ref}'.", file=sys.stderr)
        return None
    return pipelines[0]


def _failed_jobs(pipeline_id: int) -> list[str]:
    raw = _run_glab(["api", f"/projects/:id/pipelines/{pipeline_id}/jobs", "--paginate"])
    if raw is None:
        return []
    try:
        jobs = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [f"{j.get('name')}: {j.get('status')}" for j in jobs if j.get("status") in _TERMINAL_BAD]


def _report(pipeline: dict[str, Any]) -> int:
    status = pipeline.get("status", "unknown")
    pid = pipeline.get("id")
    sha = (pipeline.get("sha") or "")[:8]
    web = pipeline.get("web_url", "")
    header = f"Pipeline #{pid} ({sha}) on '{pipeline.get('ref')}' -> {status}"
    if status in _TERMINAL_OK:
        print(f"GREEN: {header}")
        return _EXIT_GREEN
    if status in _TERMINAL_BAD:
        print(f"RED: {header}")
        for line in _failed_jobs(pid):
            print(f"  - {line}")
        if web:
            print(f"  {web}")
        return _EXIT_RED
    print(f"PENDING: {header}")
    return _EXIT_PENDING


def check(ref: str, wait: bool, timeout: int, poll: int) -> int:
    deadline = time.time() + timeout
    while True:
        pipeline = _latest_pipeline(ref)
        if pipeline is None:
            return _EXIT_ERROR
        code = _report(pipeline)
        if code != _EXIT_PENDING or not wait:
            return code
        if time.time() >= deadline:
            print(f"TIMEOUT: pipeline still pending after {timeout}s.", file=sys.stderr)
            return _EXIT_PENDING
        time.sleep(poll)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the latest CI pipeline is green.")
    parser.add_argument("--ref", default=None, help="Branch/ref to check (default: current branch).")
    parser.add_argument("--wait", action="store_true", help="Poll until the pipeline reaches a terminal state.")
    parser.add_argument("--timeout", type=int, default=900, help="Max seconds to wait when --wait is set.")
    parser.add_argument("--poll", type=int, default=15, help="Seconds between polls when --wait is set.")
    args = parser.parse_args()

    ref = args.ref or _current_branch()
    if not ref:
        print("ERROR: could not determine ref; pass --ref explicitly.", file=sys.stderr)
        return _EXIT_ERROR

    return check(ref, args.wait, args.timeout, args.poll)


if __name__ == "__main__":
    sys.exit(main())
