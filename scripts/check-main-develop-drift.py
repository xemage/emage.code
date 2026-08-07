#!/usr/bin/env python3
"""Detect content/version drift between origin/main and origin/develop.

Compares the `Latest release: vX.Y.Z` marker embedded in README.md on each branch. Uses the
full sorted list of semver git tags to compute how many releases `main` is behind `develop`.

This intentionally does NOT use git commit-SHA ancestry (`git merge-base --is-ancestor`) as the
drift signal: GitLab's merge-via-API can materialize a new commit object with an identical
tree/message rather than reusing the source branch's tip commit as a direct parent, producing a
false "not an ancestor" result even for a content-correct, freshly performed release/* -> main
merge. See docs/tasks/task-T331.md and docs/plans/plan-019-main-develop-drift-detection.md §3.1.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

MARKER_RE = re.compile(r"Latest release:\s*(v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?)")
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-([A-Za-z0-9.-]+))?$")
GRACE_RELEASES = 1  # main may lag develop by up to 1 release (the normal window between
                     # develop's tag and the release/*->main sync MR) before this is drift.


def run_git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout


def read_file_at_ref(ref: str, path: str) -> str:
    return run_git(["show", f"{ref}:{path}"])


def parse_marker(text: str) -> str | None:
    m = MARKER_RE.search(text)
    return m.group(1) if m else None


def semver_key(tag: str) -> tuple[int, int, int, int] | None:
    m = TAG_RE.match(tag)
    if not m:
        return None
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    is_final = 0 if m.group(4) else 1
    return (major, minor, patch, is_final)


def sorted_valid_tags(all_tags: list[str]) -> list[str]:
    keyed = [(semver_key(t), t) for t in all_tags]
    keyed = [(k, t) for k, t in keyed if k is not None]
    keyed.sort(key=lambda pair: pair[0])
    return [t for _, t in keyed]


def releases_behind(main_version: str, develop_version: str, tags: list[str]) -> int:
    """How many releases main_version is behind develop_version within tags (ascending order).

    Raises ValueError if either version is not a known tag, or if main_version sorts AFTER
    develop_version (main ahead of develop, an invariant violation under GitFlow).
    """
    if main_version not in tags:
        raise ValueError(f"main marker version {main_version} is not a known git tag")
    if develop_version not in tags:
        raise ValueError(f"develop marker version {develop_version} is not a known git tag")
    main_idx = tags.index(main_version)
    develop_idx = tags.index(develop_version)
    if main_idx > develop_idx:
        raise ValueError(
            f"main marker ({main_version}) is AHEAD of develop marker ({develop_version}) "
            "— invariant violation"
        )
    return develop_idx - main_idx


def evaluate(
    main_version: str | None, develop_version: str | None, tags: list[str]
) -> tuple[int, list[str]]:
    """Pure evaluation. Returns (exit_code, message_lines)."""
    lines: list[str] = []
    if develop_version is None:
        lines.append("drift-check: could not parse 'Latest release' marker on develop")
        return 1, lines
    if main_version is None:
        lines.append("drift-check: could not parse 'Latest release' marker on main")
        return 1, lines

    try:
        behind = releases_behind(main_version, develop_version, tags)
    except ValueError as exc:
        lines.append(f"drift-check: {exc}")
        return 1, lines

    lines.append(
        f"drift-check: main={main_version} develop={develop_version} releases_behind={behind}"
    )

    if behind > GRACE_RELEASES:
        missing = tags[tags.index(main_version) + 1 : tags.index(develop_version) + 1]
        lines.append(
            f"drift-check: FAIL — main is {behind} releases behind develop "
            f"(grace={GRACE_RELEASES}); missing releases on main: {', '.join(missing)}"
        )
        lines.append(
            "drift-check: remediation — branch release/vX.Y.Z from develop, open an MR to main "
            "per CONTRIBUTING.md § Releasing, get it merged before the next release ships."
        )
        return 1, lines

    lines.append("drift-check: PASS — main is within the allowed 1-release grace window")
    return 0, lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-ref", default="origin/main")
    parser.add_argument("--develop-ref", default="origin/develop")
    parser.add_argument("--marker-file", default="README.md")
    args = parser.parse_args()

    main_text = read_file_at_ref(args.main_ref, args.marker_file)
    develop_text = read_file_at_ref(args.develop_ref, args.marker_file)
    main_version = parse_marker(main_text)
    develop_version = parse_marker(develop_text)

    all_tags = run_git(["tag"]).splitlines()
    tags = sorted_valid_tags(all_tags)

    exit_code, lines = evaluate(main_version, develop_version, tags)
    for line in lines:
        print(line)
    print(f"MAIN-DEVELOP DRIFT: {'PASS' if exit_code == 0 else 'FAIL'}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
