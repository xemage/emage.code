"""Repo-root and file-walking helpers used by tests."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def repo_root() -> Path:
    """Return the absolute path to the repo root (regardless of cwd)."""
    here = Path(__file__).resolve()
    # tests/_helpers/repo.py → parents[2] = repo root
    return here.parents[2]


def current_implementation_root() -> Path:
    """Current version-independent implementation tree."""
    return repo_root() / "implementation"


def v2_implementation_root() -> Path:
    """Archived v2 implementation (CI drift gate)."""
    return repo_root() / "archive" / "v2" / "implementation"


def knowledge_root() -> Path:
    return v2_implementation_root() / "knowledge"


def implementation_root() -> Path:
    """Default implementation root for v2 projection tests."""
    return v2_implementation_root()


def docs_root() -> Path:
    return repo_root() / "docs"


def iter_markdown(directory: Path, *, exclude_dirs: Iterable[str] = ()) -> list[Path]:
    """Yield .md files under directory, skipping any path containing an excluded dir name."""
    excluded = set(exclude_dirs)
    return sorted(
        p for p in directory.rglob("*.md")
        if not any(part in excluded for part in p.parts)
    )


def list_agents() -> list[Path]:
    return sorted((knowledge_root() / "agents").glob("*.md"))


def list_skills() -> list[Path]:
    return sorted((knowledge_root() / "skills").glob("*/SKILL.md"))


def list_commands() -> list[Path]:
    return sorted((knowledge_root() / "commands").glob("*.md"))


def list_instructions() -> list[Path]:
    return sorted((knowledge_root() / "instructions").glob("*.md"))


def list_platform_manifests() -> list[Path]:
    return sorted(
        p for p in (implementation_root() / "platforms").glob("*.json")
        if not p.name.startswith("_")
    )
