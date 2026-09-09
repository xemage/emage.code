# Task T455 — Retrieval eval sub-suite (precision/recall/irrelevant-context-rate/latency)

**ID:** T455
**Owner:** qa-engineer (reassigned from `plan-038`'s nominal `evaluation-agent` — see "Owner
reassignment" below)
**Status:** pending
**Priority:** P0
**Depends on:** T454 (done — `implementation/knowledge/agents/context-retriever.md`,
`implementation/runtime/memory/context_retriever.py`, `docs/artifacts/context-retriever-v1.md`)
**Created:** 2026-09-09
**Completed:** —
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T455's own literal
acceptance criterion: "Precision/recall measured and published *before* any claim of improved
downstream capability"); `docs/plans/plan-038-phase5-detailed-planning.md` T455 per-task summary
("Independent golden sub-suite measuring precision, recall, irrelevant-context rate, and latency —
as its own signal, not folded into T456's downstream measurement") and its 30k token budget
("Eval sub-suite authoring"); `docs/artifacts/context-retriever-v1.md` (the working `@context-
retriever` agent surface this task evaluates — `ContextRetriever.query()`, `implementation/runtime/
memory/context_retriever.py`); `docs/artifacts/hybrid-retrieval-v1.md` (the underlying `Retriever`/
`MemoryIndex` this component wraps, and its own existing latency-benchmark methodology, reused
rather than re-derived); `docs/artifacts/protected-paths-v1.md` (this task's output must **not**
touch the protected `tests/golden/**`/`scripts/scorecard.py` paths — this is a new, separate eval
sub-suite for the memory/retrieval subsystem, not an extension of the Phase 1 code-editing golden
suite); `docs/checkpoints/checkpoint-026-phase5-t454-complete.md` — read this for the immediate
prior-session context; you do not need the full Phase 5 T450-T454 execution history beyond it plus
the artifacts named above.

## Owner reassignment (read before starting)

`plan-038` names `evaluation-agent` as this task's owner. **This repo's actual registered
`evaluation-agent`** (`implementation/knowledge/agents/evaluation-agent.md`) grants only
`[read, search, web]` — no `execute`/Bash, no `edit`/write. This task requires writing real test/
eval code, running it against a real `@context-retriever` index, and producing a scorecard artifact
— none of which `evaluation-agent`'s tool grant supports. This is the same gap this repo's own
ledger already documents for T415/T418 (see `docs/tasks/active-tasks.md`'s "Owner corrections and
closure history" section, 2026-08-13), which were reassigned to `qa-engineer`/`devops-engineer`
rather than widening `evaluation-agent`'s tool grant (a registry-wide change with a much larger
blast radius than one task). **T455 is reassigned to `qa-engineer`** on the same basis — it already
owns this repo's Phase 1 golden-suite/failure-taxonomy authoring work (T411, T412, T415) and holds
a full `read, search, edit, execute, web, mcp__playwright, mcp__gitlab` grant. `evaluation-agent`'s
tool grant is unchanged. **T456 needs the same check repeated at its own dispatch time** — do not
assume this reassignment carries over automatically; confirm `evaluation-agent`'s grant again then.

## Objective

Build an independent eval sub-suite that measures `@context-retriever`'s retrieval quality —
**precision, recall, irrelevant-context rate, and latency** — as its own standalone signal,
published *before* any claim that retrieval improves downstream task success (that claim, and its
measurement, is T456's job, not this task's). Per `plan-035`'s own literal Phase 5 acceptance
criterion, this number must exist and be published ahead of T456's golden-suite re-run — do not
fold the two together or treat T456's eventual result as a substitute for this task's own,
separately-published numbers.

**This evaluates the real, merged `@context-retriever` agent surface, not T453's raw `Retriever`
API directly.** Call `implementation.runtime.memory.context_retriever.ContextRetriever.query(...)`
(the same surface `@context-retriever` itself calls, per `context-retriever-v1.md` §1) — this is
the actual object under test, per `plan-038`'s own framing ("Inputs: T454's working agent"). Do not
bypass it and call `Retriever.search()` directly; if `ContextRetriever.query()` proves insufficient
for something this task genuinely needs, that is a `type: technical` blocker to report, not a
license to test around it.

**Read `docs/artifacts/context-retriever-v1.md` §2.1 before starting.** T454's own write-safety
enforcement was found, during its own MR review, to be prose/declarative-only in this repo's real
deployment (matches the pre-existing `security-engineer.md` trust model, tracked as follow-up T457,
not blocking this task). This is unrelated to what T455 measures (retrieval *quality*, not
write-safety) — noted here only so you have accurate context on what "T454's working agent" means
and does not silently assume a stronger technical guarantee than what actually exists.

### What "precision, recall, irrelevant-context rate, and latency" mean here (define, do not assume)

`plan-035`/`plan-038` name these four metrics but do not define them precisely enough to compute
without a design decision — this task makes and documents that decision, mirroring T453's own
"fusion weights are the implementer's documented choice" precedent:

1. **A labeled query set is required** — a set of `(query, relevant_chunk_ids)` pairs against a
   real (likely synthetic, since no real vault content exists on `develop` yet — see Context below)
   corpus, where "relevant" is a ground-truth judgment made when the corpus/query set is authored,
   not inferred from the retriever's own output. Reuse T453's `synthetic_memory_corpus.py`
   generation approach if it fits (`tests/fixtures/memory/`, `implementation/runtime/memory/`'s own
   test fixtures) rather than inventing a second synthetic-corpus mechanism — if it does not fit
   this task's needs (e.g. it lacks per-query relevance labels), extend it or build a
   purpose-built one, and document which you chose and why.
2. **Precision@k / Recall@k** (state your chosen `k`, e.g. `k=5` matching `top_k`'s typical usage)
   against that labeled set — standard IR definitions, computed per query then aggregated (mean,
   plus report the distribution, not just a mean that could hide a bad tail).
3. **Irrelevant-context rate**: the fraction of returned results that are *not* in the query's
   relevant set — the false-positive rate at the top-k cutoff, distinct from recall (a low recall
   with zero irrelevant results is a different failure mode than a high recall with lots of noise,
   and both should be visible separately).
4. **Latency**: reuse `hybrid-retrieval-v1.md`'s own existing p95 latency-measurement methodology
   (already proven against a real 104,000-LOC/13,050-chunk synthetic corpus at 233.6ms p95) rather
   than re-deriving a new one — this task's own measurement is end-to-end through
   `ContextRetriever.query()` (including the `RequestingContext` derivation step T453's own
   benchmark did not have to do), so a fresh number is still required, just via the same method.

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) is approved (`plan-038`). T450-T454 are done — see
`checkpoint-026-phase5-t454-complete.md`. No real vault content exists on `develop` yet
(`implementation/knowledge/memory/{general,project,shared}/` is structure-only, per T452's own
brief) — this task, like T452/T453/T454 before it, must build and use synthetic fixtures for its
labeled query set and corpus, not wait for real content that does not exist yet.

## Inputs

- `docs/artifacts/context-retriever-v1.md` §1 (the exact `ContextRetriever.query()` call shape to
  test) and §2.1 (the honest write-safety accounting — context only, not this task's subject).
- `docs/artifacts/hybrid-retrieval-v1.md` §7 (the `MemoryIndex`/`Retriever`/`RequestingContext` API
  underneath) and its own latency-benchmark methodology/results (reuse the method, not the number —
  this task measures through a different entry point).
- `docs/artifacts/protected-paths-v1.md` (this task's new eval artifacts must live outside
  `tests/golden/**`/`scripts/scorecard.py` — pick a new location, e.g. `tests/eval/memory-
  retrieval/` or similar, state your actual choice in your completion report).
- `docs/artifacts/golden-suite-format-v1.md` (Phase 1's scorecard-format precedent — "consistent
  with existing golden-suite conventions from Phase 1" per `plan-038`'s own T455 summary means
  matching its *spirit* — binary/numeric, deterministic, reproducible, published as a checked-in
  artifact — not literally reusing its protected files or exact schema, which govern a different
  subsystem).
- `tests/fixtures/memory/` and `implementation/runtime/memory/synthetic_memory_corpus.py` (T453's
  existing synthetic-corpus fixtures/generator — reuse or extend, do not duplicate a second
  mechanism without disclosing why the existing one didn't fit).

## Constraints

- **Token budget:** 30k (`plan-038`'s own `medium`-scope estimate — "Eval sub-suite authoring"). If
  you find yourself genuinely exceeding this mid-work, that is a checkpoint-worthy event per this
  repo's Token Governance rules — report back, do not silently absorb the overrun.
- **No paid or recurring-cost API calls of any kind.** Use the same local embeddings this component
  already uses (`nomic-embed-text-v1.5`/`bge-small-en-v1.5` per ADR-005 Decision 2) — do not
  introduce a new provider.
- **Do not modify T450-T454's own modules** (`implementation/runtime/memory/{scanner,validate,
  chunker,chunk_code,enrich,embed,index_writer,build,scope_filter,lexical,structural,rank,retrieve,
  context_retriever}.py`) — import and call them, do not change their behavior. If
  `ContextRetriever.query()`'s interface genuinely cannot support what this eval needs, that is a
  `type: technical` blocker to report, not a silent edit.
- **Do not touch:** `.mcp.json` anywhere, for any reason. `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.json`/`.md` (frozen, unrelated to this task, and — for
  `tests/golden/**`/`scripts/scorecard.py` specifically — protected paths per
  `protected-paths-v1.md`, not just "unrelated"). `feature/T475-codex-platform-integration` (out of
  scope, unrelated branch). Do not start any Phase 3 work.
- **File ownership:** you may create the new eval sub-suite's test/scorecard code, its synthetic
  labeled query-set/corpus fixtures (or extensions to T453's existing ones), and a design/results
  artifact (e.g. `docs/artifacts/retrieval-eval-v1.md`) documenting the metric definitions above,
  your methodology, and your results — T456 (not your task) is the next consumer, as a pre-check
  before its own downstream measurement, not something you build here.
- **Work in your own worktree/branch:** `agent/qa-engineer/T455`, created from `develop`. Commit as
  you go; run the full test suite (`python3 tests/run.py`) and confirm no regressions before
  reporting completion, including `tests/functional/test_protected_paths_declared.py` and any
  golden-suite-isolation guards (confirm your new files are genuinely outside their scope, do not
  just assume). **Do not self-merge** — push and open a merge request, then stop; the orchestrator
  independently verifies and merges.
- Follow this repo's coding standards (max 50-line functions, max 4 parameters, early returns) and
  Conventional Commits.

## Expected Outputs

1. A labeled synthetic query set + corpus (reusing/extending T453's fixtures per the Objective
   section above), with documented, human-authored relevance judgments — not inferred from the
   retriever's own output (that would make precision/recall vacuously perfect).
2. Eval/scorecard code (natural location `tests/eval/memory-retrieval/` or state your own choice)
   computing precision@k, recall@k, irrelevant-context rate, and p95 latency against that labeled
   set, calling `ContextRetriever.query()` as the system under test.
3. A published scorecard artifact (JSON and/or Markdown, your choice, consistent in spirit with
   Phase 1's golden-suite scorecard conventions) with the actual measured numbers — this is the
   artifact `plan-035`'s acceptance criterion requires to exist "before any claim of improved
   downstream capability."
4. `docs/artifacts/retrieval-eval-v1.md` (or equivalent, name stated in your completion report): the
   metric definitions actually used (precision@k's `k`, how "relevant" was judged, how irrelevant-
   context rate is computed, the latency methodology reused from `hybrid-retrieval-v1.md`), the
   corpus/query-set construction, and the results with interpretation (are the numbers good enough
   to proceed to T456? Say so explicitly, with reasoning, not just report raw numbers).
5. Tests wired into `python3 tests/run.py` (not a separate ad hoc script) proving the eval code
   itself is correct — e.g. a query with a known, planted relevant chunk actually scores it
   correctly, a query with no relevant match correctly reports zero irrelevant/zero recall
   contribution, etc.

## Acceptance Criteria

1. **Precision, recall, irrelevant-context rate, and latency are all measured and published**, as
   this task's own standalone artifact, before any T456 downstream-capability claim exists — the
   literal `plan-035` acceptance criterion this task exists to satisfy.
2. **Metrics are computed against a genuine, human-authored labeled query set**, not inferred
   circularly from the retriever's own output — demonstrated by showing the label-authoring process
   in `retrieval-eval-v1.md`, not merely asserted.
3. **Evaluates the real `@context-retriever` surface** (`ContextRetriever.query()`), not a bypass to
   T453's raw `Retriever` API directly, unless a disclosed, justified blocker required otherwise.
4. **New eval artifacts live entirely outside `tests/golden/**`/`scripts/scorecard.py`** — confirmed
   by `tests/functional/test_protected_paths_declared.py` and any golden-suite isolation guard still
   passing unmodified, and by your own completion report stating the actual paths chosen.
5. **`python3 tests/run.py` passes with no regressions** from your branch's baseline; new tests you
   add (Expected Output #5) are included in that run, not a separate ad hoc script.
6. **No paid/recurring-cost API calls** — reuses the existing local embedding model(s) only.
7. **Results include an explicit, reasoned judgment on whether retrieval quality is sufficient to
   proceed to T456** — not just raw numbers with no interpretation.
8. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Specific cases already anticipated:

- If `ContextRetriever.query()`'s interface genuinely cannot support what this eval needs (e.g. it
  hides information T453's own `Retriever.search()` exposes that this task requires): report
  `type: technical`, `severity: major` — propose the smallest possible justified exception (e.g.
  reading an additional already-returned field) rather than bypassing the wrapper entirely, unless
  no such exception exists, in which case escalate as `severity: critical`.
- If T453's existing synthetic-corpus fixtures genuinely cannot support labeled relevance judgments
  without significant rework: this is a `type: unclear_requirements`, `severity: minor` finding —
  document the gap and build a purpose-built labeled set instead, rather than silently forcing an
  ill-fitting reuse.
- If the measured retrieval quality is genuinely poor (e.g. near-random precision/recall): **this is
  not a blocker** — report the real numbers plainly per Expected Output #4/Acceptance Criterion 7,
  with your own reasoned "should T456 proceed" recommendation. A bad result is a valid, useful
  result; do not suppress or soften it to appear more favorable.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
