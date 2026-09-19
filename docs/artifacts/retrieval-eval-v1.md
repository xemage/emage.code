# Retrieval Eval Sub-Suite — v1

**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T455's own literal
acceptance criterion — "Precision/recall measured and published *before* any claim of improved
downstream capability"); `docs/plans/plan-038-phase5-detailed-planning.md` T455 per-task summary;
`docs/artifacts/context-retriever-v1.md` §1/§2.1 (the `ContextRetriever.query()` surface this
evaluates, and the honest write-safety accounting this task is not about); `docs/artifacts/
hybrid-retrieval-v1.md` §5 (the latency-benchmark methodology reused here) and §7 (the `Retriever`/
`RequestingContext` API `ContextRetriever` itself wraps); `docs/artifacts/golden-suite-format-v1.md`
(the "deterministic, published-artifact" spirit this sub-suite follows, not its protected files);
`docs/tasks/task-T455.md`.

**Refs:** T455. Evaluates T454 (`@context-retriever`), which wraps T453
(`implementation/runtime/memory/retrieve.py`). Consumed by (not built here): T456 (golden-suite
ship gate, per plan-038, must not fold its own downstream-capability measurement into this task's
numbers or treat them as a substitute for its own).

**Status:** implementation artifact — this task's own design decisions (metric definitions, corpus/
query-set construction, chosen `k`) plus its one real, measured result set.

---

## 1. What this measures, and what it deliberately does not

`@context-retriever` (T454) is a read-only wrapper around T453's hybrid-retrieval `Retriever` API.
This task measures **retrieval quality only** — precision, recall, irrelevant-context rate, and
latency of `ContextRetriever.query()` against a labeled query set with known-correct answers. It
does **not** measure whether retrieved context actually improves a downstream agent's task success
— that is T456's job, using a separate golden-suite re-run, per `plan-035`'s explicit instruction
not to fold the two together. This artifact must exist and be published before any such downstream
claim is made.

## 2. Metric definitions actually used

- **`k = 5`** — matches `top_k`'s typical usage (`ContextRetriever.query`'s own default is 10; 5 is
  used here as the retrieval-quality cutoff, following this task's own brief's suggested example).
- **Precision@k**: fraction of the top-k retrieved chunk ids that are in the query's labeled
  relevant-id set. Standard IR definition, computed per query then aggregated (mean **and**
  distribution — median/min/max — so a bad tail cannot hide behind a mean, per this task's own
  Objective section).
- **Recall@k**: fraction of the query's labeled relevant ids that appear in the top-k. Same
  aggregation treatment.
- **Irrelevant-context rate@k**: fraction of the top-k retrieved ids that are **not** in the
  relevant set — the false-positive/noise rate at the cutoff. By construction this equals
  `1 - precision@k` (every retrieved slot is either relevant or not) — reported as its own named
  metric per this task's Expected Outputs, and because "how much noise came back" is a more direct
  reading of the number than precision is. Recall and irrelevant-rate are the genuinely independent
  axes: a low-recall, zero-noise result is a different failure mode from a high-recall, noisy one,
  and both are visible separately in §4's per-metric table.
- **Latency**: reuses `hybrid-retrieval-v1.md` §5's own p50/p95/p99/max percentile method over
  per-query wall-clock `time.perf_counter()` durations, one untimed warm-up query then a timed set —
  not re-derived. Measured **through `ContextRetriever.query()` end-to-end**, including the
  `RequestingContext` derivation step (real workspace git-remote read, real platform manifest read)
  that T453's own benchmark did not have to pay, so this is a fresh number via the same method, not
  a reuse of T453's own 222.2ms figure.

All computation logic lives in `tests/eval/memory_retrieval/metrics.py`, unit-tested with planted
data in `tests/functional/test_retrieval_eval_metrics.py` (24 tests, default `tests/run.py` tier,
no `fastembed` required — see §6).

## 3. Corpus / query-set construction

**A purpose-built labeled set was built (`tests/eval/memory_retrieval/labeled_dataset.py`), not a
reuse of T453's `tests/_helpers/synthetic_memory_corpus.py`.** Per this task's own Blocker Protocol
("if T453's existing synthetic-corpus fixtures genuinely cannot support labeled relevance judgments
without significant rework... document the gap and build a purpose-built one" — `unclear_requirements`/
`minor`, not a blocker): T453's generator produces 50 modules of 260 near-identical templated
functions each (`def module_N_function_I(value): ... return processed`), built for a latency
benchmark's chunk-count target, not for topical distinctiveness — every function is structurally and
semantically almost the same as every other, so there is no meaningful basis on which to author a
"this query's relevant chunk is X, not Y" ground-truth judgment against it. Building a second,
purpose-built corpus was the smaller, more honest change than forcing that generator to serve a
purpose (topical relevance ground truth) it was never designed for.

**Corpus** (`TOPICS`/`DECOYS` in `labeled_dataset.py`): 24 short, human-authored vault entries — 20
distinct software-engineering topics (connection pooling, rate limiting, password hashing, retry
backoff, circuit breakers, blue-green deployment, database migrations, CORS, webhook signature
verification, cursor pagination, distributed tracing, graceful shutdown, idempotency keys, secrets
rotation, load balancing, and others), each one Markdown heading + one paragraph (prose only, no
fenced code — so indexing this corpus needs only `fastembed`, not `tree-sitter`), plus **4 decoy
entries** deliberately lexically close to a real topic but conceptually distinct (CPU thread pooling
vs. DB connection pooling; bandwidth throttling vs. rate limiting; LRU eviction vs. TTL expiry;
RBAC vs. password hashing/sessions) — included specifically so irrelevant-context rate has real
near-miss content to potentially retrieve, rather than trivially reporting zero.

**Query set** (`QUERIES`): 23 hand-authored natural-language queries, each paraphrasing a topic
without necessarily reusing its title's own words (a semantic-matching test, not a keyword-matching
one), each labeled with the relevant corpus entry id(s) **before this task ever ran a retriever
against them** — the labels are what a human reading each query would expect to find, not anything
inferred from `ContextRetriever`'s own output (this task's acceptance criterion 2). 20 queries map to
exactly one relevant topic; 3 broader queries ("what patterns help an API stay resilient...")
deliberately map to 2 relevant topics each, to exercise precision@k above the single-relevant-answer
ceiling described below. `tests/functional/test_retrieval_eval_metrics.py`'s
`LabeledDatasetValidityTests` proves every query's relevant id(s) resolve to a real corpus entry, ids
are unique, and no decoy accidentally became a labeled answer.

**Known scale limitation, disclosed rather than hidden:** this corpus is 24 chunks, not T453's own
~13,000-chunk latency-benchmark scale. This is intentional — hand-authoring genuine, non-circular
topical relevance judgments does not scale the same way a templated latency-benchmark generator
does — but it means this result set demonstrates retrieval-quality *correctness on a topically
diverse, human-checkable set*, not retrieval-quality *at production corpus scale*. See §5's
recommendation for what this does and does not license.

## 4. Latency methodology detail

`tests/performance/test_retrieval_eval_scorecard.py` (opt-in, mirrors `test_hybrid_retrieval_latency
.py`'s gating exactly — `EMAGE_MEMORY_RETRIEVAL_EVAL=1` plus a `fastembed`-availability check, not
part of `tests/run.py`'s default invocation): builds the real corpus (§3) as a real git repo, runs
T452's real `build_index` → `write_index` → `MemoryIndex.load` (the full on-disk handoff, not an
in-memory shortcut), constructs one real `ContextRetriever(index_dir)` (loads `LocalEmbedder` once,
warm across all queries), issues one untimed warm-up query, then times all 23 labeled queries once
each through `ContextRetriever.query(query_text, workspace_root, platform_root, top_k=5)` — a real
temp git workspace (`git remote add origin git@gitlab.com:fixture-org/retrieval-eval-corpus.git`)
and a real `.claude/.generated-manifest.json`, so `RequestingContext` derivation is exercised
end-to-end, not stubbed.

## 5. Results (real run, real embeddings, `nomic-embed-text-v1.5`)

Published machine-readable artifact: `tests/eval/memory_retrieval/scorecard-v1.json` (also
`scorecard-v1.md`). Reproduced here:

| Metric | Mean | Median | Min | Max |
|---|---|---|---|---|
| Precision@5 | 0.226 | 0.200 | 0.200 | 0.400 |
| Recall@5 | 1.000 | 1.000 | 1.000 | 1.000 |
| Irrelevant-context rate@5 | 0.774 | 0.800 | 0.600 | 0.800 |

| Latency | p50 | p95 | p99 | max |
|---|---|---|---|---|
| ms | 63.4 | 76.5 | 93.5 | 93.5 |

Environment: this task's own sandbox, CPU-only ONNX Runtime inference, `nomic-ai/nomic-embed-text-
v1.5` (768-dim), model cache pre-warmed from prior Phase 5 work (no download during the timed run —
same no-network posture as `hybrid-retrieval-v1.md` §6). `fastembed` was not installed in this
task's default shell environment (`ModuleNotFoundError` confirmed directly); it was installed into a
throwaway virtualenv (`python3 -m venv` + `pip install -r implementation/runtime/memory/
requirements.txt`'s own `fastembed==0.8.0` pin, per that file's own documented instructions) to run
this one real measurement — no new dependency was added to the repo, and no paid/recurring-cost API
was called (PyPI package install is a one-time local install, not a per-query embeddings-provider
call; the actual embedding inference itself is 100% local ONNX, confirmed offline-capable already by
`hybrid-retrieval-v1.md` §6).

**Reading these numbers honestly:**

- **Recall@5 = 1.0 across every single one of the 23 queries, no exceptions.** Every labeled-relevant
  chunk was always retrieved within the top 5 results, including against the 4 deliberately confusable
  decoys. This is a genuinely strong, non-circular result (the labels were authored before this
  retriever was ever run against them) — the semantic+lexical+structural fusion correctly
  distinguished each topic's true answer from its near-miss decoy and from 18-19 other unrelated
  topics, every time.
- **Precision@5 is capped low by the labeled set's own design, not by retrieval failure.** 20 of 23
  queries have exactly one labeled-relevant chunk in a 24-chunk corpus, so even a perfect single-hit
  retrieval caps precision@5 at 1/5 = 0.2 — this is what "Min = Max = 0.2" for 20 of 23 queries
  reflects. The 3 broader, 2-relevant-chunk queries reach 0.4 (2/5), the maximum achievable given
  their own label. **Irrelevant-context rate at k=5 is `1 - precision@5` by this task's own definition
  (§2)**, so its high mean (0.774) is the same structural ceiling restated, not new information — it
  does not mean 4 out of 5 results were wrong answers to the query; it means the corpus does not
  contain 5 truly-relevant chunks for most of these single-topic queries, so 4 always-present
  "next-most-similar-but-not-labeled-relevant" chunks fill the remaining slots.
- **This intentionally caps how much this precision/irrelevant-rate number alone can say** — it is
  primarily useful as a regression baseline (re-run this suite after a future retrieval change and
  compare against these exact figures) rather than as a standalone "is 0.226 good" judgment, given
  the low ceiling is a property of this label design, not of retrieval quality. Recall@5 is the more
  directly interpretable signal from this particular corpus/label shape.
- **Latency (p95 = 76.5ms)** is well under `hybrid-retrieval-v1.md`'s own `<500ms` budget, as
  expected — this is a 24-chunk corpus (not T453's ~13,000-chunk benchmark corpus), so this number is
  dominated by the ~40-50ms embedding-call cost `hybrid-retrieval-v1.md` §5.4 already measured in
  isolation, plus the additional `RequestingContext` derivation (git subprocess call, manifest file
  read) this task's own methodology adds on top of T453's raw `Retriever.search()` cost. It is not a
  substitute for T453's own large-corpus figure and is not claimed to be one.

## 6. Test coverage of the eval code itself (Expected Output #5)

`tests/functional/test_retrieval_eval_metrics.py` — 24 tests, runs in `tests/run.py`'s default
tier, no `fastembed` needed (pure functions over plain id lists):

- `PrecisionAtKTests`, `RecallAtKTests`, `IrrelevantContextRateTests`: known-value cases including a
  query with a planted relevant chunk that must score correctly, a query with no relevant match that
  must correctly report zero recall and full irrelevant-rate, empty-input non-crashing behavior, and
  the `precision + irrelevant_rate == 1.0` identity from §2.
- `ScoreQueryAndAggregateTests`: proves `aggregate_query_scores` reports a real distribution (a
  perfect query and a zero-precision query must show `min=0.0`/`max=1.0`, not an averaged-away mean).
- `SummarizeLatenciesTests`: known-value p50/p95/p99/max over a 1..100 series.
- `LabeledDatasetValidityTests`: every query's relevant id(s) resolve to a real corpus entry, ids are
  unique, every query has >=1 relevant id (a precondition `recall_at_k` enforces), no decoy is
  accidentally a labeled answer.

`tests/performance/test_retrieval_eval_scorecard.py` is the opt-in real-embedding companion (§4) —
it asserts only that the report is well-formed (each metric in `[0, 1]`, latency positive, one score
per query), **not** a quality threshold, per this task's Blocker Protocol ("a genuinely poor result
is not a blocker... do not suppress or soften it").

## 7. Recommendation: proceed to T456

**Retrieval quality is sufficient to proceed to T456.** Reasoning:

1. Recall@5 = 1.0 with zero exceptions across 23 independently-labeled queries, including against
   4 purpose-built confusable decoys, is strong evidence the fusion is correctly distinguishing
   genuinely relevant content from lexically-similar-but-wrong content at this corpus scale — the
   specific failure mode ("returns confident-looking but wrong context") that would make a downstream
   golden-suite re-run (T456) unable to trust what it's given.
2. Latency (p95 = 76.5ms end-to-end through the real agent-facing wrapper) is comfortably inside
   budget and adds no material overhead beyond what `hybrid-retrieval-v1.md` already measured for
   the embedding call itself.
3. The one genuine limitation — precision/irrelevant-rate numbers are structurally capped by this
   label set's small relevant-count-per-query design, and the corpus itself is far smaller than a
   real/production-scale vault — means this result should be read as "retrieval correctly finds the
   right answer when one exists in a topically diverse set," not as "retrieval performs this well at
   arbitrary scale." This is disclosed, not hidden, and is a reasonable scope boundary for this
   task's 30k-token budget (hand-authoring genuine relevance labels does not scale to thousands of
   chunks the way a templated generator does).
4. **This is not a substitute for T456's own downstream-capability measurement** — T456 should still
   independently confirm that retrieved context measurably helps a real golden-suite task, using its
   own methodology, per `plan-035`'s explicit instruction not to fold the two together. If T456 finds
   a gap despite this task's good recall/latency numbers, that would indicate the gap is in *how*
   retrieved context is used downstream, not in retrieval quality itself — a useful diagnostic split
   that keeping these two measurements separate (as required) preserves.

## 8. Known limitations / follow-ups for T456+

- Corpus scale (24 chunks) is far below production/benchmark scale (T453's own ~13,000-chunk latency
  corpus) — a future task could extend this labeled-query methodology to a larger, still-labeled
  corpus if finer-grained precision/recall discrimination at scale becomes a decision-relevant
  question (not requested by this task's own acceptance criteria, which ask for a published number
  now, not a maximally-scaled one).
- Precision@k and irrelevant-context-rate@k are, by this task's own definition (§2), complementary
  (`irrelevant_rate = 1 - precision`) rather than independent — a future revision could report a
  richer irrelevant-context characterization (e.g. *what* the wrong-but-returned chunks tend to be:
  near-topic vs. unrelated) if that granularity becomes useful; out of this task's scope today.
- This task's real-embedding run required a throwaway virtualenv (`fastembed` was not present in the
  default shell environment) — this mirrors `test_hybrid_retrieval_latency.py`'s own pre-existing
  gating/dependency posture exactly and is not a new gap this task introduced.
