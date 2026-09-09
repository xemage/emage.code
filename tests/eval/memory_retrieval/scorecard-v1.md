# T455 Retrieval Eval Scorecard — v1

k = 5, 23 labeled queries, real `ContextRetriever.query()` calls against a real built index (real `nomic-embed-text-v1.5` embeddings, no FakeEmbedder).

| Metric | Mean | Median | Min | Max |
|---|---|---|---|---|
| Precision@k | 0.226 | 0.200 | 0.200 | 0.400 |
| Recall@k | 1.000 | 1.000 | 1.000 | 1.000 |
| Irrelevant-context rate@k | 0.774 | 0.800 | 0.600 | 0.800 |

| Latency | p50 | p95 | p99 | max |
|---|---|---|---|---|
| ms | 63.4 | 76.5 | 93.5 | 93.5 |

See `docs/artifacts/retrieval-eval-v1.md` for methodology and interpretation.
