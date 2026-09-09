# Task T451 — Three enforced memory scopes (general / project / shared)

**ID:** T451
**Owner:** solution-architect
**Status:** pending
**Priority:** P0
**Depends on:** T450 (done — `docs/decisions/ADR-005-memory-layer-design.md`, status `Accepted`)
**Created:** 2026-09-09
**Completed:** —
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T451 row — enforced
scope model, "scope is set at write time and cannot be inferred at read time" acceptance
criterion); `docs/plans/plan-038-phase5-detailed-planning.md` (approved, MR !228, merged
`develop`) — specifically its T451 per-task summary and task-graph dependency note; `docs/
decisions/ADR-005-memory-layer-design.md` (accepted 2026-09-09, MR !232) — Decision 1 (git-
versioned Markdown/frontmatter knowledge store, scope tag lives in frontmatter, set at write
time) and Decision 3 (read-only-by-default; no agent write path into the canonical store).

## Objective

Define, as an explicit scope-enforcement design, the three enforced memory scopes `plan-035`
and `plan-038` already name but do not yet design in detail:

1. **`general`** — harness-level knowledge, curated (not project-specific).
2. **`project`** — scoped to a single repository/project; must be provably unreachable from a
   different project's session.
3. **`shared`** — explicitly cross-platform (Claude Code, Codex, Gemini, etc. — this repo's
   7-platform projection model) and multi-consumer (readable by more than one concurrent agent
   session); entry into this scope is opt-in per entry, not a default.

The design must build directly on ADR-005's Decision 1 (frontmatter-tagged, git-versioned
Markdown store as canonical source of truth) — scope is a frontmatter field set at authoring/
commit time, enforced by whatever mechanism T452's indexing pipeline and T453's retrieval layer
consume, not inferred, guessed, or overridable at query/read time.

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) was approved by the user via `plan-038` (MR !228,
merged `develop`). T450 (the phase's first task) produced ADR-005, and the user approved all
three of its decisions this session — ADR-005's Status field was flipped from `proposed` to
`Accepted` (MR !232, merged `develop`) immediately before this task's dispatch. T451 is next in
`plan-038`'s dependency graph: T452 (indexing pipeline) depends on both T450's ADR (embeddings/
storage decisions — already resolved, no cost-authorization gate applies per ADR-005 Decision 2)
and this task's scope model, because `plan-035`'s own acceptance criterion ("scope is set at
write time and cannot be inferred at read time") means scope tagging must be designed into the
indexing pipeline from the start — retrofitting scope onto an already-built indexer is exactly
the failure mode `plan-038` flags as being guarded against.

Latest checkpoint context: T450's closure note in `docs/tasks/completed-tasks.md` (this
orchestrator's own independent verification of ADR-005's SoloMD/embeddings claims, dated
2026-09-09) and this session's ADR-005 status-flip commit.

## Inputs

- `plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (task table; scope-related acceptance
  criterion: "A `project`-scoped entry is provably unreachable from a different project's
  session")
- `plan-038-phase5-detailed-planning.md` — T451 per-task summary ("Objective," "Inputs,"
  "Outputs," "Acceptance criteria (summary)" subsections) and the task-graph dependency
  reasoning explaining why T451 must precede T452
- `docs/decisions/ADR-005-memory-layer-design.md` (accepted) — Decision 1 (storage substrate:
  git-versioned Markdown/frontmatter store, canonical writes only via reviewed MRs) and
  Decision 3 (read-only-by-default; canonical store and its derived index have no live agent
  write path)
- `docs/decisions/_template.md` is not applicable here — this task's output is a design doc, not
  a new ADR (no new architectural decision is being made beyond what ADR-005 already settled;
  this task operationalizes ADR-005's Decision 1, it does not revisit it)

## Constraints

- Token budget: 30k (per `plan-038`'s own per-task budget table)
- File ownership: this task may only create the scope-enforcement design doc (suggested path:
  `docs/artifacts/memory-scope-model-v1.md`, following this repo's existing `docs/artifacts/*-v1.md`
  naming convention — e.g. `docs/artifacts/protected-paths-v1.md`, `docs/artifacts/mcp-platform-
  contract-v1.md`). Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/
  tb-subset.json`/`.md` (frozen, unrelated to this task). Do not modify `plan-035`, `plan-038`,
  ADR-005, or any other existing plan/checkpoint/ADR — this task documents a new design artifact,
  it does not revise prior ones.
- Do not touch `.mcp.json` anywhere, for any reason.
- Work in your own worktree/branch: `agent/solution-architect/T451`, created from `develop`. Do
  not self-merge — push and stop; the orchestrator reviews and merges after independent
  verification.
- This task is a design task, not an implementation task — no code, no indexing pipeline, no
  actual enforcement mechanism is built here (that is T452's job, consuming this design). Do not
  presuppose T452's implementation language or storage engine beyond what ADR-005 already fixed
  (git-versioned Markdown/frontmatter).

## Expected Outputs

- `docs/artifacts/memory-scope-model-v1.md` (or equivalent name, stated explicitly in the
  completion report if different), covering, at minimum:
  - The three scopes' definitions (`general` / `project` / `shared`), each with a concrete
    example entry.
  - The frontmatter schema for the `scope:` field (and any scope-qualifying fields the `shared`
    scope's "explicit opt-in per entry" requirement needs — e.g. which platforms/consumers may
    read a given `shared` entry).
  - The enforcement mechanism: how a `project`-scoped entry is made provably unreachable from a
    different project's session (e.g. path/namespace partitioning at index-build time, a
    project-identity check at query time, or both) — stated concretely enough that T452 could
    implement it without re-deriving the design.
  - An explicit statement that scope is set at write time only and cannot be inferred, guessed,
    or overridden at read/query time — the literal `plan-035` acceptance criterion.
  - How this design composes with ADR-005 Decision 3 (read-only-by-default): scope enforcement
    must not introduce any write path into the canonical store or its derived index.

## Acceptance Criteria

1. All three scopes (`general`, `project`, `shared`) are defined with a concrete example entry
   each — not left abstract.
2. The design states, concretely, how a `project`-scoped entry is provably unreachable from a
   different project's session — this is `plan-035`'s own literal Phase 5 acceptance criterion
   and must be addressed as a specific mechanism, not asserted as an outcome.
3. The design states, concretely, how `shared`-scope entries remain reachable across projects/
   platforms while `project`-scope entries do not — the same mechanism must produce both
   outcomes correctly, not two independent, potentially-inconsistent mechanisms.
4. The design states explicitly that scope is set at write time and cannot be inferred or
   overridden at read time — stated as a hard rule with a concrete enforcement point (e.g. "the
   indexing pipeline rejects any entry with a missing or malformed `scope:` frontmatter field
   rather than defaulting it"), not just restated as prose.
5. The design explicitly builds on ADR-005 Decision 1's frontmatter-tagged git-versioned store
   (not a different storage substrate) and does not introduce any write path inconsistent with
   ADR-005 Decision 3's read-only-by-default principle.
6. The design is concrete enough for T452 (indexing pipeline) to implement scope tagging and
   enforcement directly from it, without needing to re-derive the mechanism — this is the actual
   test of "execution-ready," per `plan-038`'s own stated goal for this planning granularity.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` |
`external`) and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol.
Max 2 retries before escalating to the orchestrator. If ADR-005's Decision 1 (storage substrate)
turns out to be underspecified for a concrete scope-enforcement mechanism (e.g. no clear
existing directory/namespace convention to partition by project), that is a `type:
unclear_requirements`, `severity: minor` finding to report alongside a proposed resolution — not
a reason to block without proposing a concrete design of your own.

## Execution notes
<filled during execution>
