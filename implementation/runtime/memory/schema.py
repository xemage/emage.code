"""Shared data types for the knowledge-vault indexing pipeline (T452).

Consumed by every stage of the pipeline (scan -> validate -> chunk -> enrich ->
embed -> write). Kept dependency-free (stdlib only) so it can be imported by
tests without requiring the heavier optional runtime deps (fastembed,
tree-sitter) to be installed.

See `docs/artifacts/memory-scope-model-v1.md` §3 for the frontmatter schema
this mirrors, and `docs/artifacts/indexing-pipeline-v1.md` for the on-disk
index format these types are serialized into.
"""
from __future__ import annotations

from dataclasses import dataclass, field

VALID_SCOPES = ("general", "project", "shared")


@dataclass(frozen=True)
class SharedConsumers:
    """`shared_consumers` block — required, both sub-fields required, if scope == shared."""

    projects: tuple[str, ...]
    platforms: tuple[str, ...]


@dataclass(frozen=True)
class EntryFrontmatter:
    """Parsed, not-yet-validated frontmatter for one vault entry."""

    scope: str | None
    project_id: str | None
    origin_project_id: str | None
    shared_consumers: SharedConsumers | None
    title: str | None
    tags: tuple[str, ...]
    raw: dict


@dataclass(frozen=True)
class SourceLocation:
    """Where a vault entry physically came from, for enrichment + audit."""

    repo_root: str          # absolute path to the repo checkout that was scanned
    repo_id: str             # project_id-style slug identifying that repo
    relative_path: str       # path of the entry file relative to repo_root
    commit: str              # git commit SHA of repo_root at scan time (or fallback marker)


@dataclass(frozen=True)
class ParsedEntry:
    """A vault entry that passed §5 write-time validation and is chunk-eligible."""

    frontmatter: EntryFrontmatter
    body: str
    location: SourceLocation


@dataclass(frozen=True)
class RawChunk:
    """Output of the chunking stage, before enrichment/embedding.

    `line_range` is 1-indexed and inclusive, relative to the entry's body
    text (the content after the frontmatter block).
    """

    text: str
    content_type: str            # "code" | "prose"
    language: str | None
    symbol: str | None
    ast_type: str | None
    parents: tuple[str, ...]
    imports: tuple[str, ...]
    line_range: tuple[int, int]


@dataclass(frozen=True)
class RejectionRecord:
    """One §5 write-time-validation failure. Never silent — always logged."""

    source_path: str
    repo_id: str
    commit: str
    reason: str
    scope_attempted: str | None


@dataclass(frozen=True)
class ChunkRecord:
    """One indexed, embedded chunk. Field set matches
    `docs/artifacts/indexing-pipeline-v1.md`'s chunk metadata schema.
    """

    chunk_id: str
    text: str
    vector: tuple[float, ...]
    embedding_model: str
    embedding_dim: int

    # provenance / plan-035 enrichment fields
    path: str
    repo_id: str
    commit: str
    content_type: str            # "code" | "prose"
    language: str | None
    symbol: str | None
    ast_type: str | None
    parents: tuple[str, ...]
    imports: tuple[str, ...]
    line_range: tuple[int, int]

    # entry-level fields
    title: str | None
    tags: tuple[str, ...]

    # scope metadata (memory-scope-model-v1.md §4.2) — immutable, write-time-only
    scope: str = field(default="general")
    project_id: str | None = None
    shared_consumers: SharedConsumers | None = None
