"""Enrichment: combine a `RawChunk` with its parsed entry to build the
metadata every chunk carries in the derived index — plan-035's enrichment
field list (path, symbol, language, AST type, parents, imports, line range,
commit) plus memory-scope-model-v1.md §4.2's scope metadata.
"""
from __future__ import annotations

import hashlib

from implementation.runtime.memory.schema import ChunkRecord, ParsedEntry, RawChunk


def _chunk_id(entry: ParsedEntry, index: int, raw: RawChunk) -> str:
    digest_input = f"{entry.location.repo_id}:{entry.location.relative_path}:{index}:{raw.line_range}"
    digest = hashlib.sha1(digest_input.encode("utf-8")).hexdigest()[:12]
    return f"{entry.location.relative_path}::chunk{index}::{digest}"


def build_chunk_records(entry: ParsedEntry, raw_chunks: list[RawChunk]) -> list[ChunkRecord]:
    """Attach entry-level + scope metadata to each raw chunk. Vector/embedding
    fields are left as placeholders — `embed.py` fills them in a later stage
    (chunking and embedding are kept as independent, testable stages).
    """
    return [_to_record(entry, i, raw) for i, raw in enumerate(raw_chunks)]


def _to_record(entry: ParsedEntry, index: int, raw: RawChunk) -> ChunkRecord:
    fm = entry.frontmatter
    loc = entry.location
    return ChunkRecord(
        chunk_id=_chunk_id(entry, index, raw),
        text=raw.text,
        vector=(),
        embedding_model="",
        embedding_dim=0,
        path=loc.relative_path,
        repo_id=loc.repo_id,
        commit=loc.commit,
        content_type=raw.content_type,
        language=raw.language,
        symbol=raw.symbol,
        ast_type=raw.ast_type,
        parents=raw.parents,
        imports=raw.imports,
        line_range=raw.line_range,
        title=fm.title,
        tags=fm.tags,
        scope=fm.scope,
        project_id=fm.project_id,
        shared_consumers=fm.shared_consumers,
    )
