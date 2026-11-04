#!/usr/bin/env python3
"""Detect content/version drift between origin/main and origin/develop.

Compares the `Latest release: vX.Y.Z` marker embedded in README.md on each branch. Uses the
full sorted list of semver git tags to compute how many releases `main` is behind `develop`.

This intentionally does NOT use git commit-SHA ancestry (`git merge-base --is-ancestor`) as the
drift signal: GitLab's merge-via-API can materialize a new commit object with an identical
tree/message rather than reusing the source branch's tip commit as a direct parent, producing a
false "not an ancestor" result even for a content-correct, freshly performed release/* -> main
merge. See docs/tasks/task-T331.md and docs/plans/plan-019-main-develop-drift-detection.md §3.1.

Limits (T675, QA-T648-03 / TL-T649-13):

* The check compares what the two refs *contain*. Run offline, or with two refs that
  hold the same README.md (a fresh clone whose ``origin/main`` and ``origin/develop`` were
  not fetched, or the same ref twice), it reports ``releases_behind=0`` and passes
  without having looked at the real remote ``main``: such a run proves nothing. Fetch
  both branches first (the CI jobs do: ``git fetch origin main develop``).
* ``GRACE_RELEASES = 1`` is unchanged: a tag pushed while ``main`` is exactly one release
  behind still passes. That is a tolerance for the window between the two release MRs,
  not a step of the procedure: the duty is that the release branch is merged to
  ``develop`` and then to ``main`` BEFORE the tag is pushed (CONTRIBUTING.md § Cutting a
  release, steps 5 to 7). The gate prints a NOTE whenever ``main`` is behind, so the
  tag pipeline's output shows it.
* T685: the tolerance above is for the marker check only. The tag job also runs
  ``scripts/check-release-tag-tree.py``, which requires the tag commit's TREE to equal the tree of
  ``origin/main`` (a tree comparison, for the same reason as above: SHA ancestry is unreliable after a GitLab
  API merge). A tag pushed before the release reached ``main`` therefore fails there even though this check passes.
* T730 (SEC-T716-01): the two refs are read EXACTLY. git's short-name search tries ``refs/tags/<name>`` before
  ``refs/remotes/<name>``, and the jobs fetch every tag, so a tag named ``origin/main`` would otherwise stand in for
  the remote-tracking branch. ``origin/main`` means ``refs/remotes/origin/main`` (a ``refs/...`` name stays as
  given); it is resolved with ``git show-ref --verify --hash``, which does no search, and the marker file is read
  by object id, as ``scripts/check-release-tag-tree.py`` does. A ref that does not exist exactly fails the check.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

MARKER_RE = re.compile(r"Latest release:\s*(v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?)")
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-([A-Za-z0-9.-]+))?$")
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")  # no leading dash, no revision syntax
OID_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
GRACE_RELEASES = 1  # main may lag develop by up to 1 release (the normal window between
                     # develop's tag and the release/*->main sync MR) before this is drift.


def run_git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout


class RefError(Exception):
    """A ref that is not a plain name or that does not exist exactly (never carries file contents)."""


def full_ref_name(ref: str) -> str:
    """``origin/main`` is the remote-tracking branch ``refs/remotes/origin/main``; a ``refs/...`` name stays as given."""
    return ref if ref.startswith("refs/") else f"refs/remotes/{ref}"


def ref_object(full_ref: str) -> str | None:
    """The object id of exactly ``full_ref``, or None: ``show-ref --verify`` does no short-name search."""
    done = subprocess.run(["git", "show-ref", "--verify", "--hash", full_ref], capture_output=True, text=True,
                          check=False, shell=False)
    out = done.stdout.strip()
    return out if done.returncode == 0 and OID_RE.fullmatch(out) else None


def read_file_at_ref(ref: str, path: str) -> str:
    """The content of ``path`` in the commit that exactly ``ref`` names, read by object id (SEC-T716-01)."""
    if not REF_RE.fullmatch(ref) or ".." in ref:
        raise RefError(f"{ref!r} is not a plain ref name")
    full_ref = full_ref_name(ref)
    oid = ref_object(full_ref)
    if oid is None:
        raise RefError(f"{full_ref} does not exist (exact ref; fetch the branch first)")
    return run_git(["show", "--end-of-options", f"{oid}:{path}"])


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

    if behind > 0:
        lines.append(
            f"drift-check: NOTE — main is {behind} release behind develop (grace={GRACE_RELEASES}). "
            "Duty: merge release/vX.Y.Z to develop and to main BEFORE pushing the tag; this PASS "
            "is a tolerance, not a confirmation that main carries the release."
        )
    lines.append("drift-check: PASS — main is within the allowed 1-release grace window")
    return 0, lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-ref", default="origin/main")
    parser.add_argument("--develop-ref", default="origin/develop")
    parser.add_argument("--marker-file", default="README.md")
    args = parser.parse_args()

    try:
        main_text = read_file_at_ref(args.main_ref, args.marker_file)
        develop_text = read_file_at_ref(args.develop_ref, args.marker_file)
    except RefError as exc:
        print(f"drift-check: {exc}")
        print("MAIN-DEVELOP DRIFT: FAIL")
        return 1
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
