"""Write-time-only scope validation — `memory-scope-model-v1.md` §5.

Hard rule (quoted from §5): scope, project_id, and shared_consumers are
computed exactly once, at index-build time, from the frontmatter of the
canonical git commit being indexed. A malformed/missing value is REJECTED,
never defaulted to any scope. This module is the single enforcement point
for that rule; nothing downstream (chunking, enrichment, embedding) may run
on an entry that fails here.
"""
from __future__ import annotations

import re

import yaml

from implementation.runtime.memory.schema import (
    VALID_SCOPES,
    EntryFrontmatter,
    SharedConsumers,
)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?", re.DOTALL)


class FrontmatterParseError(ValueError):
    """Raised when a file has no parseable YAML frontmatter block at all."""


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (raw_frontmatter_dict, body). Raises FrontmatterParseError if absent."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise FrontmatterParseError("no frontmatter block found")
    raw = yaml.safe_load(m.group(1))
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise FrontmatterParseError(f"frontmatter is not a mapping: {type(raw).__name__}")
    return raw, text[m.end():]


def _parse_shared_consumers(raw: dict) -> SharedConsumers | None:
    block = raw.get("shared_consumers")
    if block is None:
        return None
    if not isinstance(block, dict):
        return None
    projects = block.get("projects")
    platforms = block.get("platforms")
    if not isinstance(projects, list) or not isinstance(platforms, list):
        return None
    return SharedConsumers(projects=tuple(projects), platforms=tuple(platforms))


def to_entry_frontmatter(raw: dict) -> EntryFrontmatter:
    """Structural parse only — does not judge validity, see `validate_entry`."""
    scope = raw.get("scope")
    scope = scope if isinstance(scope, str) else None
    project_id = raw.get("project_id")
    project_id = project_id if isinstance(project_id, str) else None
    origin_project_id = raw.get("origin_project_id")
    origin_project_id = origin_project_id if isinstance(origin_project_id, str) else None
    title = raw.get("title")
    title = title if isinstance(title, str) else None
    tags = raw.get("tags")
    tags = tuple(tags) if isinstance(tags, list) else ()
    return EntryFrontmatter(
        scope=scope,
        project_id=project_id,
        origin_project_id=origin_project_id,
        shared_consumers=_parse_shared_consumers(raw),
        title=title,
        tags=tags,
        raw=raw,
    )


def validate_entry(fm: EntryFrontmatter) -> str | None:
    """Return None if `fm` passes §5's write-time validation, else a rejection reason.

    Reject-not-default: every failure path below means "this entry is excluded
    from every derived index, for every project, full stop" — never a fallback
    to `general` (least restrictive) or `project` (most restrictive).
    """
    reason = _check_scope_literal(fm)
    if reason:
        return reason
    if fm.scope == "project":
        return _check_project_scope(fm)
    if fm.scope == "shared":
        return _check_shared_scope(fm)
    return None


def _check_scope_literal(fm: EntryFrontmatter) -> str | None:
    if fm.scope is None:
        return "missing scope field"
    if fm.scope == "":
        return "empty scope field"
    if fm.scope not in VALID_SCOPES:
        return f"scope {fm.scope!r} is not one of {VALID_SCOPES}"
    return None


def _check_project_scope(fm: EntryFrontmatter) -> str | None:
    if not fm.project_id:
        return "scope: project requires a non-empty project_id"
    return None


def _check_shared_scope(fm: EntryFrontmatter) -> str | None:
    sc = fm.shared_consumers
    if sc is None:
        return "scope: shared requires a shared_consumers block"
    if not sc.projects:
        return "shared_consumers.projects is missing or empty"
    if not sc.platforms:
        return "shared_consumers.platforms is missing or empty"
    return None
