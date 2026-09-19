"""Hybrid retrieval — T453.

Queries T452's derived vector index (`indexing-pipeline-v1.md` §2) and
returns a ranked result set fusing three independent signals: semantic
(`embed.py`'s `LocalEmbedder` + cosine similarity), lexical (`lexical.py`,
BM25 over text/symbol/tags), and structural (`structural.py`, enrichment-
metadata boosts). A mandatory scope pre-filter (`scope_filter.py`,
`memory-scope-model-v1.md` §4.2) always runs BEFORE ranking.

Per-query cost is kept off repeatedly-paid, per-candidate Python loops
wherever an index-wide result can instead be precomputed once at
`MemoryIndex` load time and reused: chunk vectors are stacked into one numpy
matrix for a single vectorized cosine-similarity pass per query, and BM25
token bags are tokenized once, not on every `.search()` call — see
`docs/artifacts/hybrid-retrieval-v1.md` §5 for the latency budget this is
built to meet and the measurement methodology.

numpy is an optional dependency (this repo only pulls it in transitively via
`fastembed`, `embed.py`'s dependency — see that module's own docstring).
`_import_numpy()` below is used by both `MemoryIndex.vector_matrix()` and
`_semantic_scores()` so this module can also be imported and exercised with
no `numpy` installed at all: when it's unavailable, `vector_matrix()` stores
a plain list of tuples instead of stacking an array, and `_semantic_scores`
falls back to a per-candidate Python dot-product loop that returns the exact
same cosine-similarity values, just without vectorization. This is what lets
`tests/functional/test_hybrid_retrieval.py` exercise the real
`Retriever.search()` path (via its `FakeEmbedder`, over tiny 2-9-chunk
candidate sets) in this repo's dependency-light default test tier. The
numpy-backed path remains the default whenever numpy IS available — that is
what the real `<500ms` p95 latency measurement against a ~13,000-chunk index
depends on; the pure-Python fallback is never exercised in production.

See `docs/artifacts/hybrid-retrieval-v1.md` for the full design, the query-
time-filter call-order proof, and the latency benchmark methodology/results.
This module is the integration surface for T454 (`@context-retriever`).
"""
from __future__ import annotations

import heapq
import json
from dataclasses import dataclass
from pathlib import Path

from implementation.runtime.memory.embed import LocalEmbedder
from implementation.runtime.memory.lexical import corpus_token_bags, score_lexical_precomputed, tokenize
from implementation.runtime.memory.rank import RankWeights, fuse_scores
from implementation.runtime.memory.scope_filter import RequestingContext, filter_indices
from implementation.runtime.memory.structural import score_structural_terms


def _import_numpy():
    """Local, optional import of numpy — mirrors `embed.py`'s "local
    import: optional dependency" convention. Returns `None` (rather than
    raising) when numpy isn't installed, so `MemoryIndex.vector_matrix()`
    and `_semantic_scores()` can each fall back to a pure-Python
    computation instead of failing. Production always has numpy available
    transitively via `fastembed` (`embed.py`'s own required dependency);
    this fallback exists solely so this module stays importable and
    exercisable — via `FakeEmbedder`, over small candidate sets — in this
    repo's dependency-light default test tier
    (`tests/functional/test_hybrid_retrieval.py`).
    """
    try:
        import numpy as np
    except ImportError:
        return None
    return np


@dataclass(frozen=True)
class RetrievalResult:
    """One ranked hit. `chunk` is the full on-disk chunk record (§2.1 of
    `indexing-pipeline-v1.md`, includes `vector`); `to_summary()` drops the
    vector for logging/display use.
    """

    chunk: dict
    score: float
    semantic_score: float
    lexical_score: float
    structural_score: float

    def to_summary(self) -> dict:
        return {k: v for k, v in self.chunk.items() if k != "vector"} | {
            "score": self.score,
            "semantic_score": self.semantic_score,
            "lexical_score": self.lexical_score,
            "structural_score": self.structural_score,
        }


class MismatchedEmbeddingModelError(ValueError):
    """Raised when an index directory mixes chunks embedded with different
    models — `indexing-pipeline-v1.md` §2.1 names this exact refusal as a
    required T453 behavior (per-chunk `embedding_model`/`embedding_dim`
    exist precisely so this can be detected).
    """


class MemoryIndex:
    """A loaded, in-memory index — load once (`MemoryIndex.load`), then run
    many queries against it via `Retriever`. Loading is separate from
    querying so a long-lived process (T454) pays the JSONL-parse cost, the
    vector-matrix stack, and the BM25 tokenization pass exactly once.
    """

    def __init__(self, chunks: list[dict], embedding_model: str) -> None:
        self.chunks = chunks
        self.embedding_model = embedding_model
        self._vector_matrix = None
        self._token_bags = None
        self._token_lengths = None

    @classmethod
    def load(cls, index_dir: Path) -> "MemoryIndex":
        manifest = json.loads((index_dir / "manifest.json").read_text(encoding="utf-8"))
        chunks = _read_jsonl(index_dir / "index.jsonl")
        _assert_single_embedding_model(chunks, manifest["embedding_model"])
        return cls(chunks, manifest["embedding_model"])

    def vector_matrix(self):
        """Lazily stacked `(len(chunks), embedding_dim)` numpy array, row-
        aligned with `self.chunks`. Only called once real ranking is needed
        (never during `MemoryIndex.load` itself), and only by
        `Retriever.search` — normally requires numpy, already an indirect
        dependency of `embed.py`'s `fastembed` whenever a real `Retriever`
        (not just the dependency-free `scope_filter`/`lexical`/`structural`
        modules) is in use. When numpy isn't installed (this repo's
        dependency-light test tier — see `_import_numpy`), this instead
        caches a plain list of `tuple`s row-aligned the same way, which
        `_semantic_scores`'s pure-Python fallback consumes directly.
        """
        if self._vector_matrix is None:
            np = _import_numpy()
            if np is not None:
                self._vector_matrix = np.array([c["vector"] for c in self.chunks], dtype=np.float32)
            else:
                self._vector_matrix = [tuple(c["vector"]) for c in self.chunks]
        return self._vector_matrix

    def token_bags(self):
        """Lazily computed, cached BM25 token bags — see `lexical.
        corpus_token_bags`. Computed once per `MemoryIndex` instance, reused
        by every `Retriever.search` call against it.
        """
        if self._token_bags is None:
            self._token_bags, self._token_lengths = corpus_token_bags(self.chunks)
        return self._token_bags, self._token_lengths


def _read_jsonl(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _assert_single_embedding_model(chunks: list[dict], expected: str) -> None:
    seen = {c.get("embedding_model") for c in chunks}
    mismatched = seen - {expected}
    if mismatched:
        raise MismatchedEmbeddingModelError(
            f"index contains chunks embedded with {sorted(mismatched)}, manifest declares "
            f"{expected!r} — refusing to compare vectors from a mismatched embedding_model "
            "(indexing-pipeline-v1.md §2.1)"
        )


class Retriever:
    """Holds a loaded `MemoryIndex` and a warm `LocalEmbedder` across
    queries — construct once per process/session, then call `.search(...)`
    repeatedly (this is what makes the `<500ms` p95 latency budget
    achievable: model load, index parse, vector-matrix stacking, and BM25
    tokenization all happen once, not per query).
    """

    def __init__(self, index: MemoryIndex, embedder: LocalEmbedder | None = None,
                 weights: RankWeights = RankWeights()) -> None:
        self.index = index
        self.embedder = embedder or LocalEmbedder(model_name=index.embedding_model)
        self.weights = weights

    def search(self, query_text: str, requesting_context: RequestingContext,
               top_k: int = 10) -> list[RetrievalResult]:
        """Mandatory-scope-filtered, three-signal hybrid retrieval.

        Call order (`memory-scope-model-v1.md` §4.2): `filter_indices` runs
        FIRST, against the full candidate set, before any semantic/lexical/
        structural score is computed for anything — an excluded chunk is
        never embedded-compared, never lexically scored, and never ranked.
        `requesting_context` has no default; omitting it is a `TypeError`,
        not a permissive query mode.
        """
        indices = filter_indices(self.index.chunks, requesting_context)
        if not indices:
            return []
        query_vector = self.embedder.embed_texts([query_text])[0]
        request = _RankRequest(query_text, query_vector, self.weights, top_k)
        return _rank_candidates(self.index, indices, request)


@dataclass(frozen=True)
class _RankRequest:
    """Bundles one `.search()` call's per-query ranking inputs, so
    `_rank_candidates` stays within this repo's max-4-parameters convention
    (mirrors `build.py`'s `_ScanTarget`/`chunk_code.py`'s `_CodeContext`).
    """

    query_text: str
    query_vector: object
    weights: RankWeights
    top_k: int


def _rank_candidates(index: MemoryIndex, indices: list[int], request: _RankRequest) -> list[RetrievalResult]:
    """Score every scope-filtered candidate on all three signals, fuse, and
    return only the top-K as `RetrievalResult`s — the (potentially large)
    scope-filtered candidate set is scored with cheap per-candidate
    primitives (a numpy row, a dict lookup, a few token-set intersections),
    but a full `RetrievalResult` dataclass is only constructed for the K
    results actually returned.
    """
    semantic_scores = _semantic_scores(index, indices, request.query_vector)  # already plain floats
    lexical_scores = _lexical_scores(index, indices, request.query_text)
    structural_scores = _structural_scores(index, indices, request.query_text)
    fused = [
        fuse_scores(sem, lex, struct, request.weights)
        for sem, lex, struct in zip(semantic_scores, lexical_scores, structural_scores)
    ]
    top = heapq.nlargest(request.top_k, range(len(indices)), key=lambda pos: fused[pos])
    return [
        RetrievalResult(index.chunks[indices[pos]], fused[pos], semantic_scores[pos],
                         lexical_scores[pos], structural_scores[pos])
        for pos in top
    ]


def _lexical_scores(index: MemoryIndex, indices: list[int], query_text: str) -> list[float]:
    bags, lengths = index.token_bags()
    sub_bags = [bags[i] for i in indices]
    sub_lengths = [lengths[i] for i in indices]
    return score_lexical_precomputed(sub_bags, sub_lengths, query_text)


def _structural_scores(index: MemoryIndex, indices: list[int], query_text: str) -> list[float]:
    terms = set(tokenize(query_text))
    return [score_structural_terms(index.chunks[i], terms) for i in indices]


def _semantic_scores(index: MemoryIndex, indices: list[int], query_vector) -> list[float]:
    """Cosine similarity (both operands unit-normalized, so dot product ==
    cosine similarity) for exactly the scope-filtered `indices`, returned as
    plain Python floats.

    Preferred path: one numpy matrix-vector product over the whole
    candidate set rather than a per-candidate Python loop — see this
    module's own docstring for why, and for the `<500ms` p95 latency budget
    this is required to meet against a real, ~13,000-chunk index.

    Fallback path (numpy not installed — see `_import_numpy`): a plain
    per-candidate Python dot-product loop over `index.vector_matrix()`'s
    list-of-tuples form. Mathematically identical result to the numpy path;
    only used by this repo's dependency-light test tier
    (`FakeEmbedder`-based tests in `test_hybrid_retrieval.py`, tiny 2-9-chunk
    candidate sets) — never exercised in production, where numpy is always
    available transitively via `fastembed`.
    """
    np = _import_numpy()
    matrix = index.vector_matrix()
    if np is not None:
        sub = matrix[indices]
        q = np.asarray(query_vector, dtype=np.float32)
        return (sub @ q).tolist()
    return [sum(v * qv for v, qv in zip(matrix[i], query_vector)) for i in indices]
