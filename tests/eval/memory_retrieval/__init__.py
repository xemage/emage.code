"""T455 — independent retrieval-quality eval sub-suite for `@context-retriever`.

Measures precision@k, recall@k, irrelevant-context rate, and p95 latency of
`implementation.runtime.memory.context_retriever.ContextRetriever.query()`
against a labeled synthetic corpus/query set, as its own standalone signal —
see `docs/artifacts/retrieval-eval-v1.md` for the full design and results.

This package lives outside `tests/golden/**` and `scripts/scorecard.py`
(protected paths, `docs/artifacts/protected-paths-v1.md`) — it is a new,
separate eval for the memory/retrieval subsystem, not an extension of the
Phase 1 code-editing golden suite.
"""
