#!/usr/bin/env python3
"""Verify a `release/vX.Y.Z -> main` merge was NOT silently squashed by GitLab.

GitLab's `/merge` API has twice (T331/MR !103, T339/MR !109) squashed a `release/* -> main`
merge despite an explicit `squash: false` override in the request body, on a project with
`squash_option: default_on`. Squashing on this specific merge produces a `main`-side commit
whose second parent is a GitLab-materialized `squash_commit_sha` rather than the real source
branch tip, corrupting `git merge-base(main, develop)` for the *next* sync (T339's incident).
See docs/tasks/task-T340.md § Findings for the full, independently-verified mechanism.

This script closes the detection loop: run it immediately after every `release/vX.Y.Z -> main`
merge, before considering the sync complete. It fetches the just-merged MR's own record and
asserts `squash == false` and `squash_commit_sha == null` — the two fields GitLab itself uses
to report that squashing occurred (T340 Findings §2-3). If the assertion fails, the merge has
already happened; see CONTRIBUTING.md § Releasing § "Post-merge squash verification" for the
documented recovery procedure.

Usage:
    python3 scripts/verify-main-sync-merge.py <mr_iid>

Exit codes:
    0  verified — squash == false and squash_commit_sha == null (real 2-parent merge)
    1  GitLab squashed the merge despite the override — ancestry is corrupted, recovery needed
    2  tooling/lookup error (glab missing, bad IID, API error, malformed response)

Requires: `glab` authenticated against the project (HTTPS, no SSH) — same as
scripts/check-ci-green.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any, Optional

_EXIT_OK = 0
_EXIT_SQUASHED = 1
_EXIT_ERROR = 2


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


def fetch_mr(mr_iid: str) -> Optional[dict[str, Any]]:
    """Fetch a merge request's record via `GET projects/:id/merge_requests/:iid`.

    Note: `glab api` exits 0 even on HTTP errors (e.g. a 404 for a bad IID), returning the
    error body (`{"message": "..."}`) on stdout instead of a merge request record. Detect that
    shape explicitly rather than misreading it as a valid (and falsely "squashed") MR record.
    """
    raw = _run_glab(["api", f"projects/:id/merge_requests/{mr_iid}"])
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("ERROR: could not parse merge request response.", file=sys.stderr)
        return None
    if not isinstance(data, dict) or "iid" not in data:
        print(
            f"ERROR: unexpected merge request response for IID {mr_iid} "
            f"(not a valid MR record): {raw.strip()}",
            file=sys.stderr,
        )
        return None
    return data


def evaluate(mr: dict[str, Any]) -> tuple[int, list[str]]:
    """Pure evaluation of an MR record. Returns (exit_code, message_lines).

    Asserts `squash == False` and `squash_commit_sha is None` — the two fields GitLab's own
    API uses to report that a squash occurred (docs/tasks/task-T340.md § Findings §2-3), even
    when the caller explicitly requested `squash: false`.
    """
    iid = mr.get("iid", "?")
    squash = mr.get("squash")
    squash_commit_sha = mr.get("squash_commit_sha")
    merge_commit_sha = mr.get("merge_commit_sha")
    lines: list[str] = []

    if squash is False and squash_commit_sha is None:
        lines.append(
            f"verify-main-sync-merge: MR !{iid} PASS — squash=false, squash_commit_sha=null, "
            f"merge_commit_sha={merge_commit_sha}"
        )
        return _EXIT_OK, lines

    lines.append(
        f"verify-main-sync-merge: MR !{iid} FAIL — GitLab squashed this merge despite the "
        f"override (squash={squash}, squash_commit_sha={squash_commit_sha})"
    )
    lines.append(
        "verify-main-sync-merge: main's ancestry is now corrupted for this sync — the next "
        "release's merge-base will resolve incorrectly (see docs/tasks/task-T339.md)."
    )
    lines.append(
        "verify-main-sync-merge: recovery — see CONTRIBUTING.md § Releasing § "
        "'Post-merge squash verification' for the ancestry-restore procedure."
    )
    return _EXIT_SQUASHED, lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mr_iid", help="IID of the merge request to verify (e.g. 103)")
    args = parser.parse_args()

    mr = fetch_mr(args.mr_iid)
    if mr is None:
        return _EXIT_ERROR

    exit_code, lines = evaluate(mr)
    for line in lines:
        print(line)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
