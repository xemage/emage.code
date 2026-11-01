#!/usr/bin/env python3
"""Check that a release tag carries exactly the content of ``origin/main`` (T685; TL-T649-13, QA-T648-03).

The release procedure (CONTRIBUTING.md "Cutting a release", docs/artifacts/release-documents-ruling-v1.md step 7)
merges ``release/vX.Y.Z`` to ``develop`` and to ``main`` and only then tags the release branch's tip. The tip and
``origin/main`` hold the same files. ``scripts/check-main-develop-drift.py`` tolerates ``main`` being one release
behind (a grace window) and only reads the ``Latest release`` marker, so a tag pushed before the ``main`` merge, or a
tag on a commit that never reached ``main``, still passed. This script closes that gap: the tree of the tag's commit
must be identical to the tree of ``origin/main``.

Why a TREE comparison and not commit ancestry (``git merge-base --is-ancestor``): GitLab's merge through the API can
create a new commit with an identical tree instead of using the branch tip as a parent, so the tag commit is not an
ancestor of ``main`` even for a correct release (see check-main-develop-drift.py and docs/tasks/task-T331.md). A git
tree id is a hash of the content, so equal ids mean equal files and modes, whatever the history looks like.

Shallow clones: the tag pipeline fetches ``main`` with ``--depth=1``. Comparing two tree ids needs only the two commits
and their trees, which a depth-1 fetch brings; no history, no merge base and no unshallowing is involved.

Fails closed (exit 1): a tag that is not a release tag name (the CI tag rule), a tag or ``--main-ref`` that does not
resolve to a commit (for example because ``main`` was not fetched: an offline run proves nothing), and any difference.
Exit 2: git itself is unavailable. The script only reads the repository. Run it after
``git fetch origin main --depth=1`` and ``git fetch --force origin 'refs/tags/*:refs/tags/*'`` (the CI job does).

Known limit: ``main`` moving after the tag was pushed (a hotfix, the next release) makes a RE-RUN of the tag pipeline
fail, by design: the gate states that the tag matched ``main`` when the pipeline ran. Re-tag from the right commit.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys

TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$")  # the CI tag rule
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")  # no leading dash, no revision syntax
MAX_LISTED_PATHS = 20
UNSAFE_RE = re.compile("[\x00-\x1f\x7f-\x9f\u061c\u200b-\u200f\u2028\u2029\u202a-\u202e\u2060-\u2069\ufeff]")


class CheckError(Exception):
    """A usage or environment error (exit code 2); never carries file contents."""


def run_git(args: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=False, shell=False)
    except OSError as exc:
        raise CheckError("git is not available") from exc


def resolve_tree(rev: str) -> str | None:
    """The tree id of a commit-ish (annotated tags are peeled), or None when it does not resolve to a commit."""
    if run_git(["rev-parse", "--verify", "--quiet", "--end-of-options", f"{rev}^{{commit}}"]).returncode != 0:
        return None  # a missing ref, or a tag that points at a tree or a blob
    done = run_git(["rev-parse", "--verify", "--quiet", "--end-of-options", f"{rev}^{{tree}}"])
    out = done.stdout.strip()
    return out if done.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", out) else None


def differing_paths(tree_a: str, tree_b: str) -> list[str]:
    """Paths that differ between two tree ids (capped, control characters removed)."""
    done = run_git(["diff-tree", "-r", "--name-only", "--no-renames", "-z", "--end-of-options", tree_a, tree_b])
    names = [UNSAFE_RE.sub("?", n) for n in done.stdout.split("\x00") if n]
    shown = names[:MAX_LISTED_PATHS]
    return shown + ([f"... and {len(names) - MAX_LISTED_PATHS} more"] if len(names) > MAX_LISTED_PATHS else [])


def evaluate(tag: str, main_ref: str, tag_tree: str | None, main_tree: str | None, diff: list[str] | None = None) -> tuple[int, list[str]]:
    """Pure evaluation. Returns (exit_code, message_lines)."""
    if tag_tree is None:
        return 1, [f"release-tree: FAIL - tag {tag} does not resolve to a commit (fetch the tags first)"]
    if main_tree is None:
        return 1, [f"release-tree: FAIL - {main_ref} does not resolve to a commit "
                   "(run `git fetch origin main --depth=1` first: an offline run proves nothing)"]
    if tag_tree != main_tree:
        lines = [f"release-tree: FAIL - the tree of {tag} ({tag_tree[:12]}) differs from the tree of {main_ref} ({main_tree[:12]}).",
                 "release-tree: the release content must be on main BEFORE the tag is pushed (CONTRIBUTING.md, Cutting a release);",
                 "release-tree: merge release/vX.Y.Z to develop and to main, then tag the release branch tip. Paths that differ:"]
        return 1, lines + [f"  {name}" for name in (diff or [])]
    return 0, [f"release-tree: PASS - {tag} and {main_ref} have the same tree ({main_tree[:12]})"]


def check(tag: str, main_ref: str) -> tuple[int, list[str]]:
    if not TAG_RE.fullmatch(tag):
        return 1, [f"release-tree: FAIL - {UNSAFE_RE.sub('?', tag)!r} is not a release tag name"]
    if not REF_RE.fullmatch(main_ref):
        return 1, [f"release-tree: FAIL - {UNSAFE_RE.sub('?', main_ref)!r} is not a plain ref name"]
    tag_tree = resolve_tree(f"refs/tags/{tag}")
    main_tree = resolve_tree(main_ref)
    diff = differing_paths(tag_tree, main_tree) if tag_tree and main_tree and tag_tree != main_tree else None
    return evaluate(tag, main_ref, tag_tree, main_tree, diff)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--tag", required=True, help="the release tag, vX.Y.Z (CI_COMMIT_TAG)")
    parser.add_argument("--main-ref", default="origin/main")
    args = parser.parse_args(argv)
    try:
        code, lines = check(args.tag, args.main_ref)
    except CheckError as exc:
        print(f"release-tree: error: {exc}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    print(f"RELEASE TAG TREE: {'PASS' if code == 0 else 'FAIL'}")
    return code


if __name__ == "__main__":
    sys.exit(main())
