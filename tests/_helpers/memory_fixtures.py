"""Test helper: materialize a T452 fixture vault tree as a real, committed
git repo in a temp directory, so pipeline tests exercise genuine `git`
commit resolution (`implementation/runtime/memory/scanner.resolve_commit`)
rather than a synthetic placeholder.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def materialize_git_repo(source_dir: Path, dest_dir: Path) -> Path:
    """Copy `source_dir` into `dest_dir` and commit it as a fresh git repo.

    `dest_dir` should be a caller-owned temp directory (e.g. from
    `tempfile.TemporaryDirectory()`); this function does not clean up after
    itself.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
    _run_git(dest_dir, ["init", "-q"])
    _run_git(dest_dir, ["config", "user.email", "t452-fixture@example.invalid"])
    _run_git(dest_dir, ["config", "user.name", "T452 Fixture"])
    _run_git(dest_dir, ["add", "-A"])
    _run_git(dest_dir, ["commit", "-q", "-m", "fixture: initial commit"])
    return dest_dir


def _run_git(cwd: Path, args: list[str]) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)
