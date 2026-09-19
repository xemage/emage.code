# Task T453 — Hybrid retrieval (semantic + lexical + structural, ranked) over T452's index

**ID:** T453
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T452 (done — `implementation/runtime/memory/`, `docs/artifacts/indexing-pipeline-v1.md`)
**Created:** 2026-09-09
**Completed:** 2026-09-09
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T453 row: "Hybrid
retrieval: semantic + lexical + structural, ranked", and Phase 5's own headline acceptance
criterion "`<500ms` p95 retrieval on a 100K LOC repo"); `docs/plans/plan-038-phase5-detailed-
planning.md` (approved, merged `develop`) — T453 per-task summary ("ranking combines all three
signals, not semantic alone"; the recurring-cost note, resolved negative by ADR-005 Decision 2)
and its 75k token budget; `docs/decisions/ADR-005-memory-layer-design.md` (accepted 2026-09-09) —
Decision 2 (local embeddings, zero cost) and its "Validation" section naming T453's latency
measurement directly; `docs/artifacts/indexing-pipeline-v1.md` (T452, this task's primary
functional input — on-disk index format, chunk metadata schema, embedding model/runtime, §6
"what T452 guarantees, what T453 still needs to do"); `docs/artifacts/memory-scope-model-v1.md`
(T451, accepted design) — §4.2 (the mandatory query-time filter this task must implement), §4.3
(same predicate as §4.1, different data), §8 (the cross-project-unreachability and shared-scope-
reachability probes named explicitly for T452+T453 to build).

This brief is self-contained. Read `docs/checkpoints/checkpoint-024-phase5-t452-complete.md` for
the immediate prior-session context — you do not need the full Phase 5 execution history beyond
that checkpoint plus the input documents above.

## Objective

Build the retrieval layer that queries T452's derived vector index and returns a ranked result
set, fusing three independent signals — **semantic** (vector similarity against the local
embedding model T452 already wired up), **lexical** (exact/near-exact keyword or symbol-name
matching — e.g. BM25 or equivalent over each chunk's `text`/`symbol`/`tags` fields), and
**structural** (boosting based on the enrichment metadata T452 persists per chunk: `path`,
`symbol`, `ast_type`, `parents`, `language`, proximity to previously-referenced files, etc.) — into
a single ranked list. Semantic similarity alone is explicitly insufficient per `plan-038`'s own
acceptance-criteria wording ("ranking combines all three signals, not semantic alone"); your
fusion strategy (weighted linear combination, reciprocal rank fusion, a learned re-ranker, or
another approach) is your own implementation choice to make and document, the same latitude T452
had over its own index format and chunking library.

This is `plan-038`'s own second and final `large`-scope task in Phase 5 with real design
uncertainty (its words: "ranking-fusion strategy across semantic/lexical/structural signals is not
yet designed") — genuine implementation choices are yours; the index format, chunk schema, and
embedding model are already fixed by T452 and must not be re-derived or second-guessed.

**Second, independent scope-enforcement point (do not treat T452's structural guarantee as
sufficient on its own).** `memory-scope-model-v1.md` §4.2 requires this task to implement a
**mandatory query-time pre-filter**, applying the identical `include(chunk_metadata,
requesting_context)` predicate T452 already applies structurally at build time — but here, applied
independently, at query time, against the metadata T452 persisted on every chunk (`scope`,
`project_id`, `shared_consumers`). This is defense in depth, not redundant busywork: §4.2 states
explicitly that if the storage substrate ever migrates to a shared multi-project index (a
documented future alternative in ADR-005), T452's per-project structural partitioning would no
longer hold on its own, and the query-time filter is what continues to protect isolation in that
scenario. Build it as if T452's own guarantee did not exist — filtering must happen on this task's
own candidate set, before ranking, not as a courtesy check assuming the index is already clean.

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) is approved (`plan-038`). T450 (ADR-005, accepted),
T451 (scope model), and T452 (indexing pipeline) are all done — see
`docs/checkpoints/checkpoint-024-phase5-t452-complete.md`. T452 delivered
`implementation/runtime/memory/` and `docs/artifacts/indexing-pipeline-v1.md`. No real vault
content exists on `develop` yet (`implementation/knowledge/memory/{general,project,shared}/` is
structure-only, per T452's own scoping) — you will need synthetic fixtures for both the
scope-enforcement probes and the latency benchmark, the same pattern T452 used for its own
cross-project fixture pair (`tests/fixtures/memory/`).

## Inputs

- `docs/artifacts/indexing-pipeline-v1.md` — §2 (on-disk index format: `index.jsonl` chunk schema,
  including `vector`/`embedding_model`/`embedding_dim` and the scope fields `scope`/`project_id`/
  `shared_consumers`), §4 (embedding model/runtime: `fastembed`, `nomic-embed-text-v1.5` primary —
  your query-time embedding step must use the **same model** an index was built with; refuse to
  compare vectors from a mismatched `embedding_model`, the manifest already records this per chunk
  for exactly this reason), §6 ("what T452 guarantees, what T453 still needs to do" — read this
  section first, it is written directly for you).
- `docs/artifacts/memory-scope-model-v1.md` — §4.2 (the query-time filter contract: mandatory
  `requesting_context={project_id, platform}` argument on every retrieval call, no default/
  omitted/unfiltered code path; filter applied as a pre-filter on the candidate set before ranking,
  not after), §4.3 (why this is the same predicate as T452's, not a second mechanism), §8 (the
  cross-project-unreachability probe and shared-scope-reachability probe — build both as your own
  acceptance tests, not just T452's).
- `docs/decisions/ADR-005-memory-layer-design.md` — Decision 2 (local embeddings, zero cost — your
  query-time embedding call must not introduce any paid or network-dependent embeddings provider);
  "Validation" section's latency item (`<500ms` p95 on a 100K-LOC repo is this ADR's own stated
  validation check for this task, not a new requirement invented here).
- `plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 — the literal acceptance criterion list (`<500ms`
  p95 retrieval on a 100K LOC repo; a `project`-scoped entry provably unreachable from a different
  project's session — restated here as this task's own responsibility for the query-time half of
  that guarantee).
- `plan-038-phase5-detailed-planning.md` — T453's per-task summary (75k token budget, "Cost note"
  on recurring per-query cost — resolved negative by ADR-005 Decision 2, so no user
  cost-authorization gate applies to this task).

## Constraints

- **Token budget:** 75k (`plan-038`'s own `large`-scope estimate). If you find yourself genuinely
  exceeding this mid-work, that is a checkpoint-worthy event per this repo's Token Governance rules
  — report back, do not silently absorb the overrun.
- **No paid or recurring-cost API calls of any kind**, at query time or otherwise. ADR-005 Decision
  2 is a hard constraint here exactly as it was for T452: query-time embedding must run locally
  (the same model class T452 already wired up — reuse `implementation/runtime/memory/embed.py` or
  an equivalent local call, do not introduce a second embedding pathway). If you find any part of
  this design genuinely requires a paid API call or unavoidable network egress, **stop and report a
  blocker** (`type: technical`, `severity: critical`) rather than proceeding or silently stubbing
  the embedding step.
- **File ownership:** you may create the retrieval implementation (a natural location is
  `implementation/runtime/memory/`, alongside T452's existing modules — e.g. `retrieve.py`/
  `rank.py`/`lexical.py` — but state your actual choice in your completion report if different,
  same disclosure norm T452 used for its own location deviation), its tests, a benchmark script/
  fixture for the latency measurement, and a short design-note artifact (e.g.
  `docs/artifacts/hybrid-retrieval-v1.md`) documenting the fusion strategy, the query-time filter
  implementation, and the latency benchmark methodology and results — T454 (not your task) will
  consume this document the same way you consumed T452's.
- **Do not touch:** `.mcp.json` anywhere, for any reason. `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.json`/`.md` (frozen, unrelated to this task). `ADR-005-memory-layer-
  design.md`, `memory-scope-model-v1.md`, and `docs/artifacts/indexing-pipeline-v1.md` themselves
  (consume, do not revise — if any is genuinely underspecified for something you need, that is a
  `type: unclear_requirements` blocker to report with a proposed resolution, not a license to
  silently edit the prior artifacts). `implementation/runtime/memory/{scanner,validate,chunker,
  chunk_code,enrich,embed,index_writer,build}.py` (T452's own modules) — you may **import and call**
  them (in particular `embed.py`'s embedding function, for query-time embedding parity with the
  index), but do not modify their behavior; if T452's code genuinely needs a change to support
  retrieval, that is a blocker to report, not a silent edit. `feature/T475-codex-platform-
  integration` (out of scope, unrelated branch). Do not start any Phase 3 work.
- **Work in your own worktree/branch:** `agent/backend-developer/T453`, created from `develop`.
  Commit as you go; run the full test suite (`python3 tests/run.py`) and confirm no regressions
  before reporting completion. **Do not self-merge** — push and open a merge request, then stop;
  the orchestrator independently verifies and merges.
- Follow this repo's coding standards (max 50-line functions, max 4 parameters, early returns) and
  Conventional Commits.

## Expected Outputs

1. Retrieval implementation: a documented query function/CLI that accepts a query string, a
   `requesting_context={project_id, platform}` argument (mandatory — no default, no code path that
   omits it), and an index directory (T452's `index.jsonl`), and returns a ranked list of chunks
   fusing semantic + lexical + structural signals.
2. The query-time scope pre-filter (`memory-scope-model-v1.md` §4.2), applied to the candidate set
   before ranking, using the identical `include(chunk_metadata, requesting_context)` predicate
   T452 already implements structurally — implemented independently here, not by calling back into
   T452's scanner.
3. A latency benchmark: a real ~100K-LOC (or larger) corpus built into an index via T452's own
   pipeline, a representative query set, and a measured p95 latency figure with the methodology
   documented (how the corpus was assembled, how queries were chosen, how p95 was computed — e.g.
   N runs, percentile method).
4. `docs/artifacts/hybrid-retrieval-v1.md` (or equivalent, name stated in your completion report):
   fusion strategy and why it was chosen, query interface signature, the query-time filter
   implementation, and the latency benchmark methodology and results — written so T454 can wrap it
   into an agent without re-deriving your design, mirroring `indexing-pipeline-v1.md`'s own role
   for T452.
5. Tests: the two `memory-scope-model-v1.md` §8 probes (cross-project unreachability at query
   time; shared-scope reachability at query time) as your own acceptance tests, plus unit coverage
   for the fusion logic, wired into `tests/` following this repo's existing conventions
   (`tests/run.py`).

## Acceptance Criteria

1. **Ranking combines all three signals, not semantic alone**: demonstrate with a concrete example
   query where a lexical or structural signal changes the top-ranked result relative to
   pure-semantic ranking (e.g. an exact symbol-name match outranking a semantically-similar but
   textually-unrelated chunk) — not just an assertion that three scores are computed and summed.
2. **Query-time scope pre-filter is mandatory and independent of T452's structural guarantee**: the
   retrieval function has no code path, default parameter, or query mode that omits
   `requesting_context`. The filter is applied to the candidate set *before* ranking runs — confirm
   this by inspecting the actual call order (filter function called and candidate set reduced prior
   to any ranking-score computation), not merely by checking that excluded chunks don't appear in
   final output (a post-hoc filter would satisfy a weaker, wrong test — same distinction T452's own
   acceptance criterion 3 drew for the structural control).
3. **Cross-project unreachability holds at query time, adversarially**: build (or reuse) a
   `P1`/`P2` fixture pair with a `project`-scoped entry unique to `P1`; issue a `P2`-context query
   deliberately crafted to target that entry's exact content/keywords (a hostile query, not a
   generic one); assert zero hits, even though the term-level lexical signal would otherwise match
   it strongly. This must hold even in a hypothetical scenario where the entry *is* present in the
   candidate index (e.g. simulate the shared-index migration ADR-005 names as a future alternative,
   by constructing a test index containing both P1 and P2 content) — the query-time filter, not
   T452's ingestion-time exclusion, must be what blocks it in that test.
4. **Shared-scope reachability works via the identical mechanism**: the same fixture's
   `shared`-scoped entry (naming `P2` in `shared_consumers.projects`) *is* retrievable by a
   `P2`-context query, proving the same predicate produces both outcomes at query time too, not
   just at T452's build time.
5. **`<500ms` p95 retrieval on a 100K LOC repo** — measured, not asserted. Include the exact corpus
   size (LOC and/or chunk count), query set, benchmark commands, and raw/aggregated results in your
   completion report. If the measured p95 exceeds 500ms, report this as the actual result (do not
   adjust the benchmark methodology to produce a passing number) and flag it as a blocker
   (`type: technical`, `severity: major`) with what you tried and what you believe the bottleneck
   is — this is a real, testable constraint per `plan-035`'s own headline acceptance criterion, not
   a target to be waved through.
6. **No embeddings-provider credential or network egress required at query time**: demonstrate
   directly (e.g. run a query with network access to any embedding API host blocked/absent, model
   cache already warm) that retrieval still works and produces real, non-stubbed similarity scores
   — mirroring T452's own acceptance criterion 6 and its demonstrated method (`HF_HUB_OFFLINE=1`/
   proxy-blackhole technique documented in `indexing-pipeline-v1.md` §4).
7. **Feeds T454**: the query interface and fusion/filter design are documented clearly enough that
   T454 (read-only agent wrapper, not your task) could integrate it without re-deriving your
   design.
8. `python3 tests/run.py` passes with no regressions from your branch's baseline; new tests you add
   are included in that run, not a separate ad hoc script.
9. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Specific cases already anticipated:

- If anything in this design genuinely requires a paid/recurring-cost API call to satisfy an
  acceptance criterion (contrary to ADR-005 Decision 2): **stop immediately** and report
  `type: technical`, `severity: critical` — this is a hard stop per this brief's Constraints, not a
  judgment call to resolve on your own.
- If the measured p95 latency genuinely exceeds 500ms after reasonable optimization effort: report
  `type: technical`, `severity: major`, with the real measured figure, what was tried, and your
  best assessment of the bottleneck (index size, lexical-index structure, embedding-model inference
  time, fusion overhead, I/O). Do not narrow the benchmark corpus or query set to avoid triggering
  this — a smaller, easier corpus that happens to pass is not evidence the acceptance criterion is
  met.
- If `indexing-pipeline-v1.md` or `memory-scope-model-v1.md` is genuinely underspecified for
  something you need to implement (e.g. exact lexical-index library, exact fusion weighting): both
  documents explicitly leave implementation choices to you where they say so — this is not a
  blocker, make and document the choice. Only escalate if the *scope-enforcement* or *cost*
  decisions themselves (not implementation details) seem contradictory or infeasible as written.
- If local embedding-model reuse from T452's `embed.py` is not feasible as-is (e.g. it is not
  structured for a single-query call rather than a batch-build call) and requires more than a
  thin, non-behavior-changing wrapper: report `type: technical`, appropriate severity, rather than
  duplicating or forking the embedding logic silently.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)

## Completion addendum (2026-09-09)

`implementation/runtime/memory/{scope_filter,lexical,structural,rank,retrieve}.py` (a mandatory
query-time scope predicate that runs before any embedding/ranking work; BM25 lexical scoring; a
structural enrichment-metadata boost signal; weighted linear fusion; the `MemoryIndex`/`Retriever`
query API for T454), `docs/artifacts/hybrid-retrieval-v1.md` (fusion strategy with a worked
example, query-time filter design, latency benchmark methodology/results), and new tests
(`tests/functional/test_hybrid_retrieval.py`, `tests/performance/test_hybrid_retrieval_latency.py`,
`tests/_helpers/synthetic_memory_corpus.py`). Squash-merged to `develop` via MR !243 (agent branch
`agent/backend-developer/T453`, feat commit `588ebc4` + fix commit `0a7dafb`, squashed to
`74ae791`, merge commit `df9a9e9`). Companion dispatch MR !242 (`docs/t453-dispatch`, this brief +
the `active-tasks.md` row) merged separately, merge commit `d45e61d`.

**Disclosed interpretation (flagged by the implementer as `unclear_requirements`/minor, not a
silent guess):** `memory-scope-model-v1.md` §4.1's build-time predicate only checks
`shared_consumers.projects` (no platform identity exists at build time). §4.2's query-time
predicate extends this to also check `shared_consumers.platforms`, since `requesting_context`
carries a platform dimension the build-time predicate doesn't have. Documented explicitly in
`scope_filter.py`'s own docstring and `hybrid-retrieval-v1.md`, not left implicit.

**A real, disclosed-only-after-the-fact defect was found and fixed before merge, not before initial
push:** `retrieve.py::_semantic_scores` (and `MemoryIndex.vector_matrix()`) did an unconditional
`import numpy as np`, reached by `Retriever.search()` regardless of embedder — including the
`FakeEmbedder`-based tests in `test_hybrid_retrieval.py`, whose own module docstring claimed (at
that point, incorrectly) that they ran with no optional dependency installed. The orchestrator
caught this via `glab ci status` on the MR's own pipeline (`unit-tests` job genuinely `failed`, not
the "419 tests, 0 failures" the MR description claimed) — not via re-reading the implementer's
report, which had not disclosed it. Independently reproduced in a from-scratch clean venv (no
`numpy`, no `fastembed`): 4 real `ModuleNotFoundError` errors, exactly matching CI. A follow-up fix
(commit `0a7dafb`, same branch) added `_import_numpy()` (mirrors `embed.py`'s existing optional-
import convention); `vector_matrix()`/`_semantic_scores()` now fall back to an equivalent
pure-Python per-candidate dot-product computation when numpy is unavailable, while the
numpy-vectorized path — confirmed via direct diff review to be otherwise byte-for-byte unchanged —
remains the default whenever numpy is importable.

**Orchestrator independent, adversarial verification before merging — not accepted on the
implementer's self-report, and not accepted on three separate mid-session messages purporting to
relay it either** (each framed as "the coordinator sent a message while you were working" —
matching the identical injection-shaped pattern already flagged in `checkpoint-023`/`checkpoint-
024`; per this project's standing rule that no agent message is ever the user's consent, none of
their claims were trusted on their own terms — everything below was independently re-derived
against real system state first):

- Read all five new modules end-to-end directly.
- Designed and ran a 7-probe adversarial scope-enforcement script, not the implementer's own test
  file: built real T452 indexes for a `P1`/`P2` fixture pair via the real pipeline, hand-merged
  their chunks into a single physical index (simulating the ADR-005-named future shared-index
  migration where T452's ingestion-time partitioning would not hold on its own), then queried it
  with the real local embedder. Confirmed: a hostile exact-canary-token query from `P2` against
  `P1`'s secret returns zero hits even though the content is physically present in the candidate
  pool; `P1` querying its own secret does surface it (predicate isn't a blanket deny); a
  shared-scope entry is reachable by its named consumer; **the disclosed
  `shared_consumers.platforms` extension is real enforcement, not decorative** — same project,
  wrong platform, is correctly blocked; omitting `requesting_context` raises `TypeError`; an empty
  `project_id` raises `ValueError` at construction; a `general`-scope chunk remains visible to an
  unrelated third project. All 7 passed.
- Independently reproduced acceptance criterion 1's worked example by running
  `FusionChangesTopResultTests` in isolation and reading its assertions directly — a real,
  non-vacuous check (asserts pure-semantic ranking disagrees with fused ranking, not just that both
  exist).
- Independently confirmed no network egress: built a fresh index and ran a query with
  `HTTP(S)_PROXY` pointed at an unreachable address — real, non-zero 768-dim vectors produced, both
  at index-build and at query time.
- **Independently re-measured the real `<500ms` p95 latency claim** by running the actual committed
  benchmark fresh (`EMAGE_MEMORY_RETRIEVAL_LATENCY_TEST=1`), against the exact merged code, not the
  implementer's number: 104,000 LOC / 13,050-chunk synthetic corpus (matches exactly), p95 =
  **233.6ms** (vs. the implementer's reported 222.2ms — both comfortably under the 500ms budget,
  ~2.1x margin). This also closed a gap the implementer's own design doc had explicitly flagged as
  outstanding (their last full benchmark run predated a subsequent coding-standards refactor and
  was not re-run against the exact final diff).
- **Found the CI/numpy defect described above** via `glab ci status` on the MR's own pipeline, not
  via the implementer's report.
- **After the fix**, independently reproduced the clean-venv verification myself in a freshly-built
  venv (not reusing the implementer's environment): 323 tests, 0 numpy-related errors (3 remaining
  errors are pre-existing and unrelated — `requests`/`pyarrow`/`cryptography` missing, predate this
  task). Individually re-ran the 4 previously-failing tests — all pass. Confirmed the real GitLab CI
  pipeline on the fix commit shows `success` across all jobs, not just `unit-tests`. Ran
  `python3 tests/run.py` in the normal environment: 419 tests, `OK`, no regressions. Reviewed the
  fix's diff directly and confirmed the numpy-available path is unchanged (same array construction,
  same matmul, only the `.tolist()` call site moved) — on that basis, judged a second full
  ~19-minute latency re-run unnecessary rather than reflexively re-running it, an explicit,
  evidence-backed engineering judgment call, not a shortcut.
- Confirmed `git diff --stat develop..HEAD` scoped to exactly the files the brief allowed; no
  `.mcp.json`, golden tests, scorecard, or unrelated files touched; no secrets (only synthetic
  fixture "canary" tokens).

**All 9 acceptance criteria independently confirmed met**, including the three most safety-critical
(criterion 2, mandatory filter-before-rank call order; criterion 3, adversarial cross-project
unreachability under a simulated worst-case merged-index scenario; criterion 5, the real measured
`<500ms` p95 latency). T454 (`@context-retriever`, read-only agent wrapper) is next in `plan-038`'s
dependency graph — not dispatched this session.
