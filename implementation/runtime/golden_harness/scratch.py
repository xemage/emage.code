"""Scratch-isolation helper (T458 Objective #1).

Formalizes the exact isolation shape every one of the 28 real trials behind
`plan-048` already used by hand (see `task-T484.md`'s Execution notes: "two
nested sessions ... each confined by instruction to its own isolated plain
scratch directory ... neither under the repo, neither a git worktree"): a
plain temp directory, never a git worktree, never the main checkout, laid out
so the case's real `expect.py` can be pointed at it unmodified
(`<case_dir>/fixture/<relative-path>`, per `golden-suite-format-v1.md` §4.1).

This module creates directories only. It never invokes, dispatches, or waits
on any live agent session -- populating `fixture/` with whatever a live
session actually produced is the caller's (orchestrator's) job, using
`write_candidate_file` / `copy_candidate_file` below after that session
completes.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


def _scratch_leaf_name(case_id: str, arm: str, k_index: int) -> str:
    return f"{case_id}__{arm}-{k_index}"


def create_scratch_case_dir(case_id: str, arm: str, k_index: int, base_dir: Path | None = None) -> Path:
    """Create an isolated plain scratch directory for one trial and return its
    `case_dir` (the directory that will contain `fixture/`, never a git
    worktree, never the main checkout).

    `base_dir`, if given, is the root new scratch dirs are created under
    (e.g. an orchestrator's own session scratchpad); if omitted, a fresh
    temp root is created via `tempfile.mkdtemp`. Either way, the returned
    `case_dir` is unique per (case_id, arm, k_index) and already has an
    empty `fixture/` subdirectory ready for a live session's produced output.
    """
    root = base_dir if base_dir is not None else Path(tempfile.mkdtemp(prefix="golden-harness-"))
    case_dir = root / _scratch_leaf_name(case_id, arm, k_index)
    (case_dir / "fixture").mkdir(parents=True, exist_ok=False)
    return case_dir


def write_candidate_file(case_dir: Path, relative_path: str, content: str) -> Path:
    """Write `content` to `case_dir / "fixture" / relative_path`, creating any
    needed parent directories. Returns the written file's path. Use this when
    the live session's output is already captured as text (e.g. read from its
    own transcript/tool output) rather than as a file the session itself wrote
    to disk."""
    target = case_dir / "fixture" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def copy_candidate_file(case_dir: Path, relative_path: str, source_path: Path) -> Path:
    """Copy an existing on-disk file (e.g. a file a live session wrote
    directly into its own working directory) to
    `case_dir / "fixture" / relative_path`. Returns the copied file's path."""
    target = case_dir / "fixture" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, target)
    return target


def cleanup_scratch_dir(case_dir: Path) -> None:
    """Remove one trial's scratch `case_dir` (not its `base_dir` parent, which
    may hold sibling trials). Safe to call on an already-removed path."""
    shutil.rmtree(case_dir, ignore_errors=True)
