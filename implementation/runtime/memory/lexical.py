"""Lexical scoring — T453's second retrieval signal.

BM25-style keyword/symbol matching over each candidate chunk's `text`,
`symbol`, `tags`, and `title` fields (indexing-pipeline-v1.md §2.1's chunk
schema). Pure stdlib — no dependency on the optional embedding/tree-sitter
stack, so this module (and `scope_filter.py`) can be unit-tested without
`fastembed`/`tree-sitter` installed, matching this repo's existing
optional-dependency test convention (`test_memory_indexing_pipeline.py`).

See `docs/artifacts/hybrid-retrieval-v1.md` "Fusion strategy" for why BM25
(rather than plain substring/exact match) was chosen for this signal.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")

BM25_K1 = 1.5
BM25_B = 0.75

# A query term hitting a chunk's `symbol` (its own identifier name) is a much
# stronger, more specific signal than the same term appearing in prose body
# text — weighted accordingly by inflating that field's term frequency.
_FIELD_WEIGHTS = {"text": 1.0, "symbol": 3.0, "tags": 2.0, "title": 1.5}


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in _TOKEN_RE.findall(text or "")]


def _field_text(chunk: dict, field: str) -> str:
    value = chunk.get(field)
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value or "")


def _weighted_tokens(chunk: dict) -> Counter:
    """Weighted token bag across `_FIELD_WEIGHTS`' fields for one chunk."""
    bag: Counter = Counter()
    for field, weight in _FIELD_WEIGHTS.items():
        for tok in tokenize(_field_text(chunk, field)):
            bag[tok] += weight
    return bag


def corpus_token_bags(chunks: list[dict]) -> tuple[list[Counter], list[float]]:
    """Precompute each chunk's weighted token bag + length once. Content-
    derived (independent of any query or `requesting_context`), so a caller
    that queries the same index repeatedly (`retrieve.MemoryIndex`) can
    compute this once and reuse it across every `score_lexical_precomputed`
    call instead of re-tokenizing the whole candidate set on every query.
    """
    bags = [_weighted_tokens(c) for c in chunks]
    lengths = [sum(bag.values()) for bag in bags]
    return bags, lengths


def score_lexical(chunks: list[dict], query_text: str) -> list[float]:
    """BM25 score per chunk against `query_text`'s terms — convenience
    wrapper that tokenizes `chunks` fresh each call (used by tests and any
    one-off caller). `retrieve.Retriever` uses `score_lexical_precomputed`
    with a cached `corpus_token_bags(...)` result instead, for repeated
    queries against the same index.
    """
    bags, lengths = corpus_token_bags(chunks)
    return score_lexical_precomputed(bags, lengths, query_text)


def score_lexical_precomputed(bags: list[Counter], lengths: list[float], query_text: str) -> list[float]:
    """Same BM25 scoring as `score_lexical`, taking already-tokenized
    `bags`/`lengths` (§ `corpus_token_bags`) for the ALREADY SCOPE-FILTERED
    candidate set. IDF is computed over exactly this candidate set, not the
    whole index — matching this task's mandatory filter-before-rank call
    order (a chunk excluded by the scope filter cannot influence another
    candidate's IDF via its term frequencies, because it was never included
    in `bags` in the first place).
    """
    query_terms = set(tokenize(query_text))
    if not query_terms or not bags:
        return [0.0] * len(bags)
    avg_len = sum(lengths) / len(lengths) if lengths else 0.0
    ctx = _Bm25QueryContext(query_terms, idf=_compute_idf(bags, query_terms), avg_len=avg_len)
    raw = [_bm25_score(bag, length, ctx) for bag, length in zip(bags, lengths)]
    peak = max(raw) if raw else 0.0
    return [score / peak if peak > 0 else 0.0 for score in raw]


def _compute_idf(docs: list[Counter], query_terms: set[str]) -> dict[str, float]:
    n = len(docs)
    idf = {}
    for term in query_terms:
        df = sum(1 for bag in docs if bag.get(term, 0) > 0)
        idf[term] = math.log(1 + (n - df + 0.5) / (df + 0.5)) if n else 0.0
    return idf


@dataclass(frozen=True)
class _Bm25QueryContext:
    """Bundles the per-query BM25 invariants (query terms, their IDF, and
    the candidate set's average document length) threaded through
    `_bm25_score`, so that function stays within this repo's max-4-
    parameters convention (mirrors `chunk_code.py`'s `_CodeContext`).
    """

    query_terms: set[str]
    idf: dict[str, float]
    avg_len: float


def _bm25_score(bag: Counter, length: float, ctx: _Bm25QueryContext) -> float:
    score = 0.0
    norm_len = length / ctx.avg_len if ctx.avg_len else 1.0
    for term in ctx.query_terms:
        freq = bag.get(term, 0)
        if freq == 0:
            continue
        denom = freq + BM25_K1 * (1 - BM25_B + BM25_B * norm_len)
        score += ctx.idf[term] * (freq * (BM25_K1 + 1)) / denom
    return score
