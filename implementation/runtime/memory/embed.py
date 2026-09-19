"""Local embedding step — ADR-005 Decision 2.

Wraps `fastembed` (ONNX Runtime CPU inference, ships as a pure pip package
with no `torch` dependency) around the two candidate models ADR-005 names:
`nomic-ai/nomic-embed-text-v1.5` (primary) and `BAAI/bge-small-en-v1.5`
(fallback). Both run fully offline once their weights are cached locally —
no API key, no embeddings-provider network call at query/index time. See
`docs/artifacts/indexing-pipeline-v1.md` "No-cost / no-network confirmation"
for the exact commands that demonstrate this.

This module requires the optional `fastembed` dependency (see
`implementation/runtime/memory/requirements.txt`). Callers must handle
ImportError for environments where it is not installed.
"""
from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from implementation.runtime.memory.schema import ChunkRecord

PRIMARY_MODEL = "nomic-ai/nomic-embed-text-v1.5"
FALLBACK_MODEL = "BAAI/bge-small-en-v1.5"

DEFAULT_CACHE_DIR = Path(
    os.environ.get("EMAGE_MEMORY_MODEL_CACHE", str(Path.home() / ".cache" / "emage-memory-embeddings"))
)


class LocalEmbedder:
    """Thin wrapper: one loaded model, unit-normalized output vectors."""

    def __init__(self, model_name: str = PRIMARY_MODEL, cache_dir: Path | None = None) -> None:
        from fastembed import TextEmbedding  # local import: optional dependency

        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name, cache_dir=str(cache_dir or DEFAULT_CACHE_DIR))
        self.dim = len(next(self._model.embed(["dimension probe"])))

    def embed_texts(self, texts: list[str]) -> list[tuple[float, ...]]:
        if not texts:
            return []
        import numpy as np

        vectors = list(self._model.embed(texts))
        normalized = []
        for vec in vectors:
            norm = float(np.linalg.norm(vec))
            unit = vec / norm if norm > 0 else vec
            normalized.append(tuple(float(x) for x in unit))
        return normalized


def embed_chunks(chunks: list[ChunkRecord], embedder: LocalEmbedder) -> list[ChunkRecord]:
    """Return new `ChunkRecord`s with `vector`/`embedding_model`/`embedding_dim`
    populated. Chunks are frozen dataclasses — this never mutates in place.
    """
    if not chunks:
        return []
    vectors = embedder.embed_texts([c.text for c in chunks])
    return [
        dataclasses.replace(
            chunk, vector=vec, embedding_model=embedder.model_name, embedding_dim=embedder.dim,
        )
        for chunk, vec in zip(chunks, vectors)
    ]
