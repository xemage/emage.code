"""Structural repo-boundary scanning — `memory-scope-model-v1.md` §4.1.

This is the primary control. It must be *structural*, not filtered: building
project P's index never even calls `glob`/`rglob`/`open` against a directory
outside the explicit set of roots this module is handed. There is no "scan
everything, discard what doesn't match" step anywhere in this file — the only
directories ever walked are:

  1. `own_repo_root`'s own `.../memory/project/` subtree           (project scope)
  2. `general_repo_root`'s `.../memory/general/` subtree            (general scope)
  3. each `shared_source_roots[i]`'s `.../memory/shared/` subtree   (shared scope)

Note (3): even when a foreign repo IS configured as a shared source (the
positive/reachability case, criterion 4), only that repo's `shared/`
subdirectory is ever touched — its `project/` subtree is never read, by
construction, regardless of configuration. This is what keeps "shared-scope
reachability" and "project-scope unreachability" the product of the identical
mechanism (memory-scope-model-v1.md §4.3): the same walk-one-named-subdir
primitive, pointed at a different subdir name.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

VAULT_SUBDIR = "implementation/knowledge/memory"


@dataclass(frozen=True)
class ScanRoot:
    """One repo checkout this build is explicitly configured to read from."""

    repo_root: Path
    repo_id: str


def resolve_commit(repo_root: Path, override: str | None = None) -> str:
    """Best-effort commit SHA for `repo_root`, or an explicit fallback marker.

    Mirrors memory-scope-model-v1.md §9's flagged assumption for project_id
    derivation: a bare checkout with no git history has no other reliable
    identity source, so callers may supply `--commit-override` explicitly.
    """
    if override:
        return override
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "no-git-commit-available"


def _scan_subdir(repo_root: Path, subdir_name: str) -> list[Path]:
    """The ONLY filesystem-walking primitive in this module. Touches exactly
    one named subdirectory of one named repo root — never anything else.
    """
    target = repo_root / VAULT_SUBDIR / subdir_name
    if not target.is_dir():
        return []
    return sorted(target.rglob("*.md"))


def scan_project_scope(own_repo: ScanRoot) -> list[Path]:
    """Files under own_repo's own `project/` subtree only."""
    return _scan_subdir(own_repo.repo_root, "project")


def scan_general_scope(general_repo: ScanRoot) -> list[Path]:
    """Files under the single harness repo's `general/` subtree only."""
    return _scan_subdir(general_repo.repo_root, "general")


def scan_shared_scope(shared_source: ScanRoot) -> list[Path]:
    """Files under one configured shared-source repo's `shared/` subtree only.

    Structural guarantee: a repo not passed here is never touched by this
    function at all — not walked, not opened, not stat'd.
    """
    return _scan_subdir(shared_source.repo_root, "shared")
