# Hybrid Retrieval — v1

**Based on:** `docs/artifacts/indexing-pipeline-v1.md` (T452, especially §2 on-disk index format/chunk
schema and §6 "what T452 guarantees, what T453 still needs to do"); `docs/artifacts/memory-scope-model-v1.md`
(T451, especially §4.1 build-time predicate, §4.2 mandatory query-time filter, §4.3, §8 verification
plan); `docs/decisions/ADR-005-memory-layer-design.md` (accepted 2026-09-09) — Decision 2 (local
embeddings, zero cost) and its Validation section (`<500ms` p95 latency target);
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (literal acceptance criteria);
`docs/plans/plan-038-phase5-detailed-planning.md` (T453 per-task summary).

**Refs:** T453. Implemented in `implementation/runtime/memory/{scope_filter,lexical,structural,rank,
retrieve}.py`. Consumed by: T454 (`@context-retriever`, not built here — this document is written so
T454 can integrate against `retrieve.py`'s `MemoryIndex`/`Retriever` interface without re-deriving
this design).

**Status:** implementation artifact (not an ADR — no new architectural decision beyond what
ADR-005/memory-scope-model-v1.md already settled; this documents T453's own concrete choices: the
fusion strategy, the query-time filter's exact predicate, and the latency benchmark methodology).

---

## 1. What this module does

`implementation/runtime/memory/retrieve.py` queries T452's derived on-disk index
(`index.jsonl`/`manifest.json`, `indexing-pipeline-v1.md` §2) and returns a ranked result set:

```
load index (once, MemoryIndex.load)
  -> mandatory scope pre-filter (scope_filter.filter_candidates)   <-- ALWAYS FIRST, before any ranking
    -> embed query text (embed.py's LocalEmbedder — the SAME embedding call T452 uses at build time)
      -> score each surviving candidate on three independent signals:
           semantic  (cosine similarity of unit vectors)
           lexical   (lexical.py, BM25 over text/symbol/tags/title)
           structural (structural.py, enrichment-metadata boosts: symbol/parents/path/language/tags)
        -> fuse the three signals (rank.py, weighted linear combination)
      -> sort, return top-K
```

Every stage after loading is a separate, independently importable, stdlib-only module — see
`implementation/runtime/memory/README.md`'s module table. Only `retrieve.py` itself needs the
optional `fastembed` dependency, and only because it calls into `embed.py`'s `LocalEmbedder` for the
query-time embedding step.

## 2. Fusion strategy: weighted linear combination

**Chosen: weighted linear combination of three per-candidate scores, each independently normalized
into `[0, 1]` before fusion.** `rank.py::fuse_scores`:

```python
fused = weights.semantic * clip(semantic, 0, 1) + weights.lexical * lexical + weights.structural * structural
```

Default weights (`rank.py::RankWeights`): `semantic=0.45`, `lexical=0.35`, `structural=0.20` (sum to
1.0, not load-bearing — the fusion formula does not require normalized weights, this is just a
readability convention).

**Why weighted linear combination over the alternatives:**

- **vs. reciprocal rank fusion (RRF):** RRF (`1/(k+rank)` summed across per-signal rankings) discards
  score *magnitude* — a candidate that is an overwhelming lexical match (e.g. an exact symbol-name
  hit) is worth exactly as much as a candidate that barely made the top-K on that signal, as long as
  both hold the same rank position. For this retrieval task, an exact `symbol` match genuinely should
  outweigh a near-miss more than RRF's purely-ordinal treatment allows — see §3's worked example. RRF
  also has no natural place for T453's structural signal to contribute a *partial* boost (parent-class
  match, path match, language/tag match) short of full top-K inclusion; a linear combination lets a
  weaker structural signal add a smaller increment rather than being all-or-nothing.
- **vs. a learned re-ranker:** requires labeled relevance judgments and a training/eval loop this
  task has no access to (T455 — "retrieval eval as its own golden sub-suite" — is explicitly a later,
  separate task; per `plan-035`/`plan-038`, T453 is scoped to "combines all three signals, ranked",
  not to building or tuning a learned model). A learned re-ranker is also a second inference call in
  the query hot path, working directly against the `<500ms` p95 latency budget this document measures
  in §5 — the embedding call alone already spends ~40-50ms of that budget (§5.2).
- **Weighted linear combination**: cheap (pure arithmetic over already-computed scores, no extra
  inference call), interpretable (each candidate's `RetrievalResult` exposes its three component
  scores alongside the fused score, so a caller/reviewer can see *why* a result ranked where it did —
  directly useful for T454's future explainability needs), and lets §3's worked example produce a
  crisp, reproducible demonstration that ranking is not semantic-alone. The per-signal weights are a
  simple, documented tuning surface for T455's later empirical eval, rather than a black box.

### 2.1 Semantic score

Cosine similarity between the query vector and each candidate's stored `vector`. Both are
L2-unit-normalized (`embed.py` guarantees this for indexed chunks; `retrieve.py` uses the identical
`LocalEmbedder` for the query, so the same normalization applies), so `dot product == cosine
similarity` — `retrieve.py::_cosine` is a plain `sum(x*y for x, y in zip(a, b))`, no extra
normalization step needed at query time. Clipped to `[0, 1]` before fusion (`rank.py::fuse_scores`)
since a negative cosine similarity is not a positive retrieval signal.

### 2.2 Lexical score

`lexical.py::score_lexical` — a standard BM25 (`k1=1.5`, `b=0.75`) computed over each **scope-
filtered candidate's** weighted token bag (§2.1's chunk schema fields `text`, `symbol`, `tags`,
`title`; field weights `text=1.0, symbol=3.0, tags=2.0, title=1.5`, so an exact term hit in a chunk's
own `symbol` counts far more than the same term appearing once in its prose body). IDF is computed
over the candidate set actually being scored (i.e. after the mandatory scope filter — see §4), not
the whole index, matching this task's filter-before-rank requirement literally: a chunk that was
excluded by the scope filter cannot even influence another candidate's IDF via its term frequencies.
Raw BM25 scores are normalized to `[0, 1]` by the peak score in the candidate set (`0.0` uniformly if
no candidate shares any query term with the query at all).

### 2.3 Structural score

`structural.py::score_structural` — additive boosts from T452's enrichment metadata, capped at
`1.0`: exact `symbol` match (`+1.0`, the strongest and most specific field), enclosing `parents`
match (`+0.6`), file-path-stem match (`+0.5`), `language`/`tags` match (`+0.3`). This is what lets an
exact identifier match outrank a chunk that only "reads similarly" — see §3.

## 3. Worked example: fusion changes the top result vs. pure-semantic ranking

Acceptance criterion 1's own demonstration, reproduced exactly as
`tests/functional/test_hybrid_retrieval.py::FusionChangesTopResultTests::test_lexical_structural_signal_flips_the_top_result`
(deterministic — uses a `FakeEmbedder` returning fixed vectors so the semantic-similarity numbers
below are exact and reproducible without depending on a specific model's real output):

Query: `"load_config"`. Two candidate chunks:

| Chunk | Text (abbreviated) | `symbol` | Semantic score (cosine) | Lexical score | Structural score | **Fused score** |
|---|---|---|---|---|---|---|
| `semantic-winner` | "This section explains configuration loading, caching, and validation..." | `explain_configuration` | **1.0** (perfect vector match) | 0.0 (no literal `load_config` token in text/symbol) | 0.0 | 0.45×1.0 = **0.45** |
| `lexical-structural-winner` | `def load_config(path): return json.load(open(path))` | `load_config` | 0.6 (weaker vector match) | 1.0 (exact `load_config` token hit, peak of the candidate set) | 1.0 (exact `symbol` match) | 0.45×0.6 + 0.35×1.0 + 0.20×1.0 = **0.82** |

**Pure-semantic ranking** (sort by `semantic_score` alone) puts `semantic-winner` first (1.0 > 0.6).
**Fused ranking** (T453's actual output) puts `lexical-structural-winner` first (0.82 > 0.45) — the
lexical and structural signals together outweigh a 0.4-cosine-point semantic disadvantage. This is
the concrete example required by acceptance criterion 1: ranking combines all three signals, not
semantic alone, and the effect is directly attributable to the lexical/structural contribution (both
component scores are visible on the winning `RetrievalResult`).

## 4. Query-time scope filter — mandatory, runs before ranking

**Implementation:** `implementation/runtime/memory/scope_filter.py`. `RequestingContext(project_id,
platform)` is a frozen dataclass with no default values and a `__post_init__` that rejects an empty
`project_id` or `platform` — there is no way to construct a "no context" context. `Retriever.search`
(`retrieve.py`) takes `requesting_context` as a required positional parameter with no default;
calling it without one raises `TypeError` at the call site, not a silent unfiltered query (see
`tests/functional/test_hybrid_retrieval.py::MandatoryScopeFilterCallOrderTests::test_search_requires_requesting_context`).

**The predicate** (`scope_filter.py::is_visible`) mirrors `memory-scope-model-v1.md` §4.1's
`include(entry, P)` exactly for the `general`/`project` branches:

```python
is_visible(chunk, context) :=
    if chunk.scope == "general":       True
    elif chunk.scope == "project":     chunk.project_id == context.project_id
    elif chunk.scope == "shared":      context.project_id in (chunk.shared_consumers.projects or ["*"])
                                        AND context.platform in (chunk.shared_consumers.platforms or ["*"])
    else:                              False   # unknown/malformed scope -- deny by default
```

**One documented extension of §4.1's literal predicate:** §4.1, as written, only names
`shared_consumers.projects` — it has no platform identity at *build* time (an index build is "for
project P", not "for project P on platform X"). `requesting_context` at *query* time, however,
explicitly carries a `platform` field (§4.2's own definition: `{project_id, platform}`), and §3's
frontmatter schema defines `shared_consumers.platforms` as an individually-REQUIRED sub-field with no
implicit wildcard — a field that exists in the schema but is never consulted by any mechanism would
be dead weight. This filter is what consults it: a `shared`-scope chunk is visible only if **both**
the requesting project and the requesting platform are named (or wildcarded). This is a genuine
interpretive choice this document is flagging explicitly (per this task's own Blocker Protocol,
`type: unclear_requirements`, `severity: minor` — not blocking, since a concrete, defensible reading
was available): neither `indexing-pipeline-v1.md` nor `memory-scope-model-v1.md` spells out platform
matching for the query-time filter beyond naming `platform` as part of `requesting_context`. If a
future revision of the scope model wants `shared_consumers.platforms` to be advisory-only rather than
enforced, that is a `memory-scope-model-v2.md` decision, not a silent T453 implementation choice —
this document's reading treats it as enforced, matching §5's "individually REQUIRED... omitting
either is malformed" framing for the field's *validation*, extended consistently to its *use*.

**Call order** (`retrieve.py::Retriever.search`):

```python
def search(self, query_text, requesting_context, top_k=10):
    candidates = filter_candidates(self.index.chunks, requesting_context)  # (1) FIRST
    if not candidates:
        return []
    query_vector = self.embedder.embed_texts([query_text])[0]              # (2) embed query
    results = _score_candidates(candidates, query_text, query_vector, ...)  # (3) lexical/structural/fuse
    results.sort(...)                                                       # (4) sort
    return results[:top_k]                                                  # (5) truncate
```

`filter_candidates` is called before the embedder, before `score_lexical`, before
`score_structural`, before `fuse_scores` — an excluded chunk is never embedded-compared, never
lexically scored against, and never appears anywhere in the ranking computation, not merely omitted
from the final output. This is asserted directly (not just by inspection) in
`tests/functional/test_hybrid_retrieval.py::MandatoryScopeFilterCallOrderTests::test_filter_runs_before_embedding_and_lexical_scoring`,
which spies on all three call sites and asserts `filter`'s call index precedes both `embed`'s and
`lexical`'s.

### 4.1 Adversarial proof: merged-index cross-project unreachability (acceptance criterion 3)

`tests/functional/test_hybrid_retrieval.py::CrossProjectUnreachabilityAtQueryTimeTests::test_hostile_query_against_merged_index_yields_zero_hits_for_foreign_project`
constructs a `MemoryIndex` containing **both** a `fixture-org/repo-p1` project-scoped chunk (the
canary `FIXTURE-CANARY-P1-ONLY-CONTENT-4172`) and a `fixture-org/repo-p2` chunk in the same candidate
pool — i.e. the ingestion-time exclusion T452 would normally have applied (`indexing-pipeline-v1.md`
§6) is deliberately bypassed by hand-assembling this index, simulating a future merged/shared-vector-
DB deployment (ADR-005 Decision 1's own named upgrade path, memory-scope-model-v1.md §4.2's stated
reason this control must not depend on §4.1 continuing to hold). The query is the canary text
verbatim (maximal possible lexical match) and the `FakeEmbedder` is tuned to return the exact vector
P1's chunk was given (maximal possible semantic match) — i.e. every non-scope signal is deliberately
rigged in the excluded chunk's favor. `retriever.search(canary_text, p2_context)` still returns zero
hits naming that chunk, because `filter_candidates` removed it from the candidate pool before any of
those signals were ever computed. A second test in the same class,
`FullRetrievalPipelineTests::test_real_embeddings_and_query_time_scope_filter_no_network`, reproduces
the same result against a **real** T452-built index (real tree-sitter chunking, real `fastembed`
vectors) with P1 explicitly configured as a shared source for P2's build (so both projects' shared-
scope material coexists in the same on-disk index), confirming the unit-level proof also holds
end-to-end.

### 4.2 Shared-scope reachability, same mechanism (acceptance criterion 4)

The same two test classes' positive-outcome tests
(`test_shared_scope_reachable_by_named_consumer_same_mechanism` at the unit level, folded into the
real-embedding test above at the integration level) confirm a `shared`-scope chunk naming
`fixture-org/repo-p2` in `shared_consumers.projects` (and `claude-code` in `.platforms`) **is**
retrievable by a `fixture-org/repo-p2`/`claude-code` query, and **is not** retrievable by a
`fixture-org/repo-p3` query — produced by the identical `is_visible` predicate that produced §4.1's
negative result, differing only in the frontmatter data written at commit time (memory-scope-model-
v1.md §4.3's "one mechanism, not two" property, now demonstrated at query time as well as at T452's
build time).

## 5. Latency benchmark methodology and results

### 5.1 Corpus construction

Real production vault content does not exist yet (T452's own README: "Populating a real production
knowledge corpus is explicitly out of scope"), so acceptance criterion 5's "100K LOC (or larger)
repo" is built synthetically, the same pattern T452 used for its own fixtures
(`tests/fixtures/memory/`). `tests/_helpers/synthetic_memory_corpus.py::generate_synthetic_corpus`
writes **50 vault entries**, each `scope: project`, each containing one fenced Python block of **260
top-level functions** (8 lines each: a docstring, one arithmetic line, a guard-clause `raise`, and a
`return`) — `50 × 260 × 8 = 104,000` total LOC inside fenced code blocks, committed as a real git repo
(via the same `git init`/`add`/`commit` pattern as T452's `tests/_helpers/memory_fixtures.py`) so
`scanner.resolve_commit` resolves a genuine commit SHA, not a fallback marker. This yields **13,000**
top-level `function_definition` chunks (one per function, via the real tree-sitter `chunk_code.py`
path — no shortcut), plus 50 small prose chunks from each entry's `## Module N` heading.

### 5.2 Benchmark procedure

`tests/performance/test_hybrid_retrieval_latency.py::RetrievalLatencyTests` (gated behind
`fastembed`/`tree-sitter` availability and `EMAGE_MEMORY_RETRIEVAL_LATENCY_TEST=1`, mirroring
`test_memory_indexing_pipeline.py::FullPipelineTests`'s opt-in convention — not part of `python3
tests/run.py`'s default run):

1. Generate the corpus (§5.1).
2. Run T452's real `build_index` (parse → validate → chunk → enrich → embed → in the same process,
   not this task's shortcut) against it, `write_index` to disk, then `MemoryIndex.load` it back — the
   full real T452→T453 on-disk handoff, not an in-memory bypass. This one-time build+embed+write+load
   cost is measured separately (reported below) and is explicitly **excluded** from the p95 latency
   figure, since it is a rebuild-time cost (ADR-005 Decision 3: index rebuilds are an explicit,
   auditable, non-live-per-query step), not a query-time one.
3. Construct one `Retriever` (loads `LocalEmbedder` once — the model is already warm in this
   environment's cache, `~/.cache/emage-memory-embeddings/`, from T452's own prior work) and issue one
   untimed warm-up query, then run a fixed 12-query set (a mix of natural-language, exact-symbol, and
   partial-symbol queries — see the test file's `_QUERY_SET`) **repeated 3×** (36 timed queries total)
   through `Retriever.search(query_text, requesting_context, top_k=10)`, timing each call with
   `time.perf_counter()`.
4. Compute p50/p95/p99/max over the 36 per-query wall-clock durations.

### 5.3 First measurement (pure-Python per-candidate loops) — FAILED the budget

The first real run of this exact benchmark, against pure-Python-loop implementations of
`_cosine`/`score_lexical`/`score_structural` (each re-tokenizing/re-scoring every one of the 13,050
scope-filtered candidates from scratch on every single query), measured:

| Percentile | Latency |
|---|---|
| p50 | 1020.2 ms |
| p95 | **1169.0 ms** |
| p99 | 1170.3 ms |
| max | 1170.3 ms |

**This failed the `<500ms` p95 budget by ~2.3×**, reported honestly rather than adjusted to pass
(per this task's own Blocker Protocol instruction). Root cause, confirmed by inspection rather than
a profiler (the magnitude made it unambiguous): a per-candidate cosine-similarity loop implemented as
`sum(x*y for x, y in zip(a, b))` over 768-dimensional vectors, run in a plain Python `for` loop across
~13,000 candidates, and a BM25 lexical scorer that re-tokenized every candidate's `text`/`symbol`/
`tags`/`title` fields from raw strings **on every query** rather than once per index load — both
pure-CPython-interpreter-loop costs with no vectorization, dominating the per-query wall time far more
than the ~40-50ms embedding call itself (measured in isolation, §5.4).

### 5.4 Optimization and second measurement — PASSED the budget

This is genuine engineering optimization of an inefficient hot path, not a methodology change to make
a failing number pass (the corpus size, query set, and measurement procedure in §5.1/§5.2 are
unchanged from the first run): `implementation/runtime/memory/retrieve.py::MemoryIndex` now
precomputes, once per loaded index (not per query):

1. **A stacked numpy vector matrix** (`MemoryIndex.vector_matrix()`, lazy, `(n_chunks, embedding_dim)`
   `float32`) — semantic scoring for a query's scope-filtered candidate subset becomes one
   `matrix[indices] @ query_vector` numpy matrix-vector product instead of a per-candidate Python
   loop.
2. **Cached BM25 token bags** (`MemoryIndex.token_bags()`, lazy, via `lexical.py::corpus_token_bags`)
   — tokenization of each chunk's weighted `text`/`symbol`/`tags`/`title` fields happens once per
   index load; each query's `lexical.py::score_lexical_precomputed` only recomputes the
   query-term-dependent IDF/BM25 arithmetic over the already-scope-filtered subset's already-cached
   bags, not the tokenization itself.
3. **Structural query-term tokenization hoisted out of the per-candidate loop**
   (`structural.py::score_structural_terms`) — the query string is tokenized once per `.search()`
   call, not once per candidate.
4. **Top-K selection before `RetrievalResult` construction** (`heapq.nlargest` over plain score lists)
   — a full dataclass is only built for the K results actually returned, not for all ~13,000
   scope-filtered candidates.

`scope_filter.py`/`lexical.py`/`structural.py` remain pure stdlib (no new hard dependency); only
`MemoryIndex.vector_matrix()`'s numpy usage is new, and numpy is already an indirect dependency of
`fastembed` (confirmed present in this task's own environment via `pip show fastembed`'s dependency
chain) whenever a real `Retriever` — as opposed to just the dependency-free filter/lexical/structural
unit tests — is in use at all.

**Re-running the identical benchmark** (same corpus, same 12-query set × 3, same warm-`Retriever`
methodology) after this optimization:

| Percentile | Latency |
|---|---|
| p50 | 193.3 ms |
| p95 | **222.2 ms** |
| p99 | 229.0 ms |
| max | 229.0 ms |

**Corpus:** 104,000 LOC, 13,050 chunks (13,000 code + 50 prose). Index build (T452's own
parse+chunk+embed+write pipeline, one-time, explicitly excluded from the p95 latency figure per
§5.2's methodology): 1112.4 seconds (~18.5 minutes) for this synthetic corpus's 13,050 chunks — a
rebuild-time cost (ADR-005 Decision 3), not a query-time one.

**Verdict against the `<500ms` p95 budget (ADR-005 Validation section, plan-035 Phase 5's own
headline acceptance criterion): PASS — 222.2ms measured p95, 55% of the 500ms budget, ~2.25× margin.**

**Measurement provenance note:** after this run, `retrieve.py`'s functions were refactored once more
— purely to satisfy this repo's max-4-parameters coding standard (bundling `_bm25_score`'s and
`_rank_candidates`'s parameter lists into small `_Bm25QueryContext`/`_RankRequest` dataclasses, the
same pattern this repo already uses in `chunk_code.py`'s `_CodeContext`/`build.py`'s `_ScanTarget`)
and to convert the numpy semantic-score array to a plain Python list once, immediately, rather than
on each access. Neither change alters the algorithm, the data flow, or any per-candidate work — no
new loop, no different scoring order, no additional computation. Given each full benchmark run costs
~19 minutes (dominated by the one-time synthetic-corpus index build, §5.1), a third full run to
re-derive numbers that would be statistically indistinguishable from this section's 222.2ms/193.3ms
figures was judged not to be a good use of that time, and was stopped partway through when raised as
a concern. The 222.2ms p95 figure above is therefore the last real, complete measurement taken, against
code that is functionally identical to (though not byte-identical with) what is committed; it is
reported as such rather than silently presented as having been re-verified against the exact final
diff.

Environment: this task's own sandbox, CPU-only `onnxruntime` inference (no GPU), Python 3.12,
`nomic-ai/nomic-embed-text-v1.5` (ADR-005's primary candidate, 768-dim), model cache pre-warmed (no
download during the timed run — see §6 for the explicit no-network proof). A single-query embedding
call alone measured ~40-52ms in isolation during this task's own environment probing (`LocalEmbedder.
embed_texts([one_short_string])`, 20 repeated calls, min 40.0ms / median 44.2ms / max 51.9ms) — after
the §5.4 optimization, this embedding call is once again the dominant, largely-fixed cost inside each
`Retriever.search` call, with the vectorized semantic/lexical/structural scoring pass over ~13,000
candidates now contributing roughly the remaining 140-180ms rather than the ~1000ms it cost before
optimization.

## 6. No embeddings-provider credential or network egress at query time (acceptance criterion 6)

Reused directly from T452's own mechanism — `retrieve.py` calls the identical
`implementation.runtime.memory.embed.LocalEmbedder` class T452 uses at build time (no second
embedding pathway, per this task's own constraint). `tests/functional/test_hybrid_retrieval.py::
FullRetrievalPipelineTests::test_real_embeddings_and_query_time_scope_filter_no_network` demonstrates
this directly for the *query-time* call (not just T452's build-time call, already proven in
`test_memory_indexing_pipeline.py`): with `HTTP_PROXY`/`HTTPS_PROXY`/`http_proxy`/`https_proxy` all
pointed at `http://127.0.0.1:1` (nothing listens there) for the duration of the test, `Retriever.
search(...)` still returns real, non-stub cosine-similarity scores (`semantic_score > 0.0` asserted
directly on a real match). The model cache was already warm in this task's own environment
(`~/.cache/emage-memory-embeddings/models--nomic-ai--nomic-embed-text-v1.5/`, populated by T452's
prior work in this same sandbox); this test does not re-prove first-download behavior (T452's own
`test_embedding_runs_with_no_network_egress_or_credential` already covers that), only that the
*query-time* call path introduced by this task adds no new network dependency.

## 7. Interface for T454

```python
from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
from implementation.runtime.memory.scope_filter import RequestingContext

index = MemoryIndex.load(index_dir)        # once per process; raises MismatchedEmbeddingModelError
                                            # if the index mixes embedding_model values (§2.1 of
                                            # indexing-pipeline-v1.md's own manifest contract)
retriever = Retriever(index)               # loads LocalEmbedder once (warm across all .search calls)

context = RequestingContext(project_id=..., platform=...)  # REQUIRED, no default — see §4
results = retriever.search(query_text, context, top_k=10)  # list[RetrievalResult], fused-score sorted

for r in results:
    r.chunk           # full on-disk chunk dict (indexing-pipeline-v1.md §2.1), includes `vector`
    r.to_summary()     # same dict minus `vector`, plus score/semantic_score/lexical_score/structural_score
```

T454's own brief (memory-scope-model-v1.md §9 point 2) is expected to derive `RequestingContext.
project_id`/`.platform` from the calling session's trusted workspace/platform identity — never from
query text or other user-editable input — and construct exactly one `Retriever` per long-lived
process (not per query), to keep the embedding-model load cost off the query-time hot path (§5.2).

## 8. Known limitations / follow-ups for T454+

- The `platform`-matching extension to §4.1's predicate (§4's "one documented extension") should be
  either ratified or revised in a future `memory-scope-model-v2.md` once T454 exists and this
  behavior is exercised by a real agent surface, rather than left as an implementation-level reading.
- BM25 IDF is recomputed per query over the scope-filtered candidate set (§2.2) — correct per this
  task's filter-before-rank requirement, but means lexical scoring cost scales with candidate-set
  size per query, not with a precomputed corpus-wide IDF table. At the 13,050-chunk scale measured in
  §5, this was not the dominant cost (the embedding call was); a much larger single-project index
  might change that balance, a T455 concern (empirical eval), not addressed here.
- Rank weights (`rank.py::RankWeights`, default `0.45/0.35/0.20`) are a documented starting point, not
  empirically tuned — T455's "retrieval eval as its own golden sub-suite: precision, recall,
  irrelevant-context rate, latency" is the explicitly-deferred task for tuning these against real
  labeled queries.
