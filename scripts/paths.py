#!/usr/bin/env python3
"""Canonical repository path constants for scripts and tests."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMPLEMENTATION = REPO_ROOT / "implementation"


def repo_root_from_implementation(implementation_root: Path) -> Path:
    """Resolve repository root from a --root implementation directory."""
    root = implementation_root.resolve()
    for candidate in (root, *root.parents):
        if (candidate / ".gitlab-ci.yml").is_file():
            return candidate
    return root.parent
