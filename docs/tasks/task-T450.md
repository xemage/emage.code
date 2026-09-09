# Task T450 — Memory-layer ADR (storage/format decision + embeddings-provider decision)

**ID:** T450
**Owner:** solution-architect
**Status:** in_progress
**Priority:** P0
**Depends on:** none (Phase 5's only precondition is Gate G0, already closed — `plan-035` §2.3)
**Created:** 2026-09-09
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T450 row, design summary
"tree-sitter → chunk → embed → hybrid retrieve, <500ms on 100K LOC, `@context-retriever`");
`docs/plans/plan-038-phase5-detailed-planning.md` (approved, MR !228, merged to `develop`) —
specifically its T450 per-task summary and its "embeddings-API cost question" framing section;
`docs/decisions/_template.md`.

## Objective

Produce `docs/decisions/ADR-005-memory-layer-design.md` (status `proposed` — human approval
required to advance; this ADR does not self-authorize downstream dispatch) resolving three things,
all required, none of which may be left implicit:

1. **The "SoloMD" storage/format comparison.** `plan-035`'s T450 row uses the label "SoloMD" for
   one side of a comparison but the term does not resolve anywhere in this repository or (per
   `plan-038`'s own check) in a general web search. **This is now partially resolved outside this
   task:** the orchestrator has confirmed directly (https://solomd.app/) that SoloMD is a real,
   free/open-source (MIT-licensed) local-first Markdown editor with on-device semantic search —
   embeddings run entirely locally, no network calls, "$0 forever," no paid tiers. It bundles an
   MCP server exposing **read-only** tools to agents, supports 14 BYOK LLM providers, but has no
   multi-user sync and no API for external systems to persistently write structured data back. Cite
   this as one concrete comparison point in the ADR's alternatives table — do not re-derive it from
   scratch, but **do not stop at citing it either.** SoloMD is a single-device personal-note tool;
   emage.code is a multi-agent orchestration system with team/shared-memory requirements (three
   enforced scopes per T451: `general`/`project`/`shared`, the last explicitly cross-platform and
   multi-consumer). That mismatch is real and must be addressed directly in the ADR's own reasoning
   — name at least one other alternative (e.g. a conventional vector-DB-backed store, a
   git-versioned plain-text/frontmatter store, etc.) and explain concretely where SoloMD's
   single-device design does and does not transfer to emage.code's actual requirements. An ADR that
   treats "SoloMD does X so we will do X" as sufficient reasoning does not meet this task's
   acceptance criteria (see below) and will not be accepted.
2. **The embeddings-provider decision: paid hosted API vs. local/open-source embedding model.**
   State explicitly which is chosen, and its cost profile (one-off / recurring / none). This is the
   one decision in Phase 5 with a real-money profile — SoloMD's own zero-cost local-embeddings
   approach is one concrete existence proof that a free path is viable in principle, but it is not
   a substitute for evaluating emage.code's own requirements (a multi-agent system doing indexing
   at write-time across three scopes plus retrieval at every `@context-retriever` query — the
   volume and multi-consumer profile differs from a single user's personal notes). Ground any local
   embedding model claims (specific model name, quality benchmarks, hardware/latency requirements)
   and any paid-API claims (specific provider, real current per-token/per-call pricing) in sources
   you actually check, not assumed figures.
3. **The read-only-by-default architectural principle** that will govern T454's
   `@context-retriever` agent (no write path from any agent into the canonical knowledge base).

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) was approved by the user via `plan-038`
(MR !228, merged `develop`). T450 is the first task in the phase's dependency graph — T451
(scope model) and T452 (indexing pipeline, gated separately, see below) both depend on this ADR's
storage-substrate and embeddings decisions. Latest checkpoint: `checkpoint-022-phase2-complete.md`
(Phase 2 close-out; Phase 5 flagged proposable but not yet planned to execution-ready detail at
that point — `plan-038` has since done that planning and is this task's immediate parent).

## Inputs

- `plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (task table, acceptance criteria, Gate G3)
- `plan-038-phase5-detailed-planning.md` (T450 per-task summary; "embeddings-API cost question —
  framed, not resolved" section; task graph)
- `docs/decisions/_template.md`
- SoloMD reference: https://solomd.app/ (confirmed by the orchestrator directly; see Objective §1
  above for the specific claims already verified — do not re-verify what's already stated here as
  confirmed, but do independently verify anything you add beyond it, e.g. specific local embedding
  model choices or specific paid-API pricing)

## Constraints

- Token budget: 30k (per `plan-038`'s own per-task budget table)
- File ownership: this task may only create `docs/decisions/ADR-005-memory-layer-design.md`. Do
  not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`
  (frozen, unrelated to this task). Do not modify `plan-035`, `plan-038`, or any other existing
  plan/checkpoint/ADR — this is a new ADR, not a revision of an existing one.
- Work in your own worktree/branch: `agent/solution-architect/T450`, created from `develop`. Do not
  self-merge — push and stop; the orchestrator reviews and merges after independent verification.
- ADR status must be `proposed`, not `accepted` — this ADR requires human (user) approval before
  any downstream task treats its conclusion as final, per `plan-038`'s own explicit instruction.
- Ground every factual/technical claim (model availability, cost figures, latency figures) in a
  real source you actually checked (WebFetch/WebSearch), not asserted from training-data recall
  alone — this repo's standing practice is independent verification of technical claims, and this
  ADR will itself be independently re-checked against real sources before being accepted (see
  Acceptance Criteria).

## Expected Outputs

- `docs/decisions/ADR-005-memory-layer-design.md`, using `docs/decisions/_template.md`'s structure
  (Context / Decision / Alternatives considered / Consequences / Validation), `Status: proposed`,
  `Tasks: T450, T451, T452, T453, T454` (all downstream tasks this decision governs).

## Acceptance Criteria

1. ADR explicitly states the embeddings-provider decision (paid hosted API vs. local/open-source
   model) and its cost profile (one-off / recurring / none) — not left implicit or hedged.
2. ADR explicitly names the SoloMD-vs-alternatives comparison, not just the label: at least SoloMD
   itself and one other concrete alternative are named and compared on real properties (storage
   format, embeddings locality, multi-user/scope support, write-back capability).
3. ADR explicitly addresses why emage.code's multi-agent/shared-memory requirements (three enforced
   scopes, cross-platform `shared` scope, multi-consumer read access via `@context-retriever`) do
   or do not favor a different path than SoloMD's single-device personal-note design — this is not
   optional framing, it is a required section of the reasoning, not a caveat appended after the
   fact.
4. ADR states the read-only-by-default principle that will govern T454.
5. Status is `proposed`, explicitly pending human approval — the ADR must not claim or imply
   `accepted` status.
6. If the ADR concludes a paid embeddings API is required: it must state the specific provider,
   the real current per-token/per-call unit cost (sourced, not assumed), and explicitly flag that
   this is a **recurring** cost (incurred at every T452 indexing run and every T453/T454 retrieval
   query thereafter) — not a one-off cost comparable to T407's bounded benchmark spend. This is the
   trigger condition the orchestrator will check before authoring T452's brief; see Blocker
   Protocol note below.
7. If the ADR concludes a local/open-source embedding model is sufficient: it must name the
   specific model(s) considered and state the basis (quality/latency/hardware) for judging it
   sufficient for a <500ms p95 retrieval target on a 100K LOC repo (T453's own headline acceptance
   criterion) — not merely asserted as "good enough."

## Blocker Protocol

- If the true original meaning of "SoloMD" (as used in whatever external source `plan-035`
  synthesized from) cannot be recovered beyond what the orchestrator has already confirmed
  (https://solomd.app/), that is **not** a blocker — proceed by treating the confirmed SoloMD
  product page as the comparison target and defining the actual alternatives compared from first
  principles, per `plan-038`'s own pre-cleared guidance on this exact scenario.
- Report any other blocker with `type` (`technical` | `dependency` | `unclear_requirements` |
  `external`) and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol.
  Max 2 retries before escalating to the orchestrator.

## Downstream gate (informational — not this task's responsibility to enforce)

Per `plan-038`'s own gate: if this ADR concludes emage.code needs a paid embeddings API, T452
(indexing pipeline) must **not** be dispatched — and its brief must not even be authored — until
the user has explicitly authorized that recurring cost, mirroring T407's authorization pattern.
The orchestrator enforces this after reviewing this ADR; this task's job is only to produce a
well-reasoned, well-sourced answer to the question, not to pre-empt the gate either way.
