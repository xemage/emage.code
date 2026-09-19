"""T455 — pure metric-computation functions for the retrieval eval sub-suite.

Standard IR definitions, computed per query then aggregated (mean + distribution, not
just a mean that could hide a bad tail — this task's own Objective section). No
dependency on any retriever/embedder/index — operates on plain retrieved-id lists and
relevant-id sets, so it is fully unit-testable with planted data (see
`tests/functional/test_retrieval_eval_metrics.py`) without `fastembed` installed.

Definitions (see `docs/artifacts/retrieval-eval-v1.md` for the full write-up):

- precision@k: fraction of the top-k retrieved ids that are in the query's relevant set.
- recall@k: fraction of the query's relevant ids that appear in the top-k.
- irrelevant-context rate@k: fraction of the top-k retrieved ids NOT in the relevant set —
  the false-positive/noise rate at the cutoff. By construction this equals
  `1 - precision@k` (every retrieved slot is either relevant or not); kept as its own named
  metric because "how much noise came back" is the more direct reading this task's
  acceptance criteria ask for, and recall/irrelevant-rate are the two genuinely
  independent axes (a low-recall, zero-noise result is a different failure mode from a
  high-recall, noisy one).
- latency: p50/p95/p99/max over per-query wall-clock durations, same percentile method as
  `hybrid-retrieval-v1.md` §5's own `_summarize` (reused, not re-derived).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryScore:
    """One query's scored result against its labeled relevant-id set."""

    query_text: str
    precision_at_k: float
    recall_at_k: float
    irrelevant_rate_at_k: float
    retrieved_count: int


def precision_at_k(retrieved_ids: list[str], relevant_ids: frozenset[str], k: int) -> float:
    """0.0 if nothing was retrieved (no candidates) rather than a division error."""
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / len(top_k)


def recall_at_k(retrieved_ids: list[str], relevant_ids: frozenset[str], k: int) -> float:
    """Requires a non-empty `relevant_ids` — every query in this task's labeled set has
    at least one relevant chunk by construction (`labeled_dataset.py`)."""
    if not relevant_ids:
        raise ValueError("recall_at_k requires a non-empty relevant_ids set")
    top_k = set(retrieved_ids[:k])
    hits = sum(1 for rid in relevant_ids if rid in top_k)
    return hits / len(relevant_ids)


def irrelevant_context_rate(retrieved_ids: list[str], relevant_ids: frozenset[str], k: int) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    irrelevant = sum(1 for rid in top_k if rid not in relevant_ids)
    return irrelevant / len(top_k)


def score_query(query_text: str, retrieved_ids: list[str], relevant_ids: frozenset[str],
                 k: int) -> QueryScore:
    return QueryScore(
        query_text=query_text,
        precision_at_k=precision_at_k(retrieved_ids, relevant_ids, k),
        recall_at_k=recall_at_k(retrieved_ids, relevant_ids, k),
        irrelevant_rate_at_k=irrelevant_context_rate(retrieved_ids, relevant_ids, k),
        retrieved_count=len(retrieved_ids[:k]),
    )


def _distribution(values: list[float]) -> dict:
    ordered = sorted(values)
    return {
        "mean": statistics.mean(ordered),
        "median": statistics.median(ordered),
        "min": ordered[0],
        "max": ordered[-1],
    }


def aggregate_query_scores(scores: list[QueryScore]) -> dict:
    """Mean/median/min/max distribution per metric across all scored queries — a mean
    alone could hide a bad tail (this task's own Objective section)."""
    if not scores:
        raise ValueError("aggregate_query_scores requires at least one QueryScore")
    return {
        "num_queries": len(scores),
        "precision_at_k": _distribution([s.precision_at_k for s in scores]),
        "recall_at_k": _distribution([s.recall_at_k for s in scores]),
        "irrelevant_rate_at_k": _distribution([s.irrelevant_rate_at_k for s in scores]),
    }


def summarize_latencies_ms(durations_ms: list[float]) -> dict:
    """p50/p95/p99/max, same percentile method as `hybrid-retrieval-v1.md` §5's own
    `_summarize` (`tests/performance/test_hybrid_retrieval_latency.py`) — reused rather
    than re-derived, per this task's own Objective/Inputs instruction."""
    if not durations_ms:
        raise ValueError("summarize_latencies_ms requires at least one duration")
    ordered = sorted(durations_ms)
    return {
        "p50": statistics.median(ordered),
        "p95": ordered[min(int(len(ordered) * 0.95), len(ordered) - 1)],
        "p99": ordered[min(int(len(ordered) * 0.99), len(ordered) - 1)],
        "max": ordered[-1],
    }
