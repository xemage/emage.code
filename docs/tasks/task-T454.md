# Task T454 — `@context-retriever` read-only agent wrapper around T453's retrieval interface

**ID:** T454
**Owner:** backend-developer
**Status:** pending
**Priority:** P0
**Depends on:** T453 (done — `implementation/runtime/memory/{scope_filter,lexical,structural,rank,
retrieve}.py`, `docs/artifacts/hybrid-retrieval-v1.md`)
**Created:** 2026-09-09
**Completed:** —
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T454 row: "`@context-
retriever` agent — read-only. `ALLOW_WRITE=false` asserted in the agent definition, the server
config, and the deployment manifest."); `docs/plans/plan-038-phase5-detailed-planning.md`
(approved, merged `develop`) — T454 per-task summary ("Wrap T453's retrieval into a read-only
agent... per `plan-035`'s own explicit redundancy requirement (not one flag, three)") and its 30k
token budget ("Wrapping + the three-place read-only assertion"); `docs/decisions/ADR-005-memory-
layer-design.md` — Decision 3 (read-only-by-default: no agent, including `@context-retriever`, may
write to the canonical knowledge base or its derived index; three independent `ALLOW_WRITE=false`
assertion points; mirrors the existing `docs/artifacts/protected-paths-v1.md` three-control
pattern) and the Validation section's T454 item ("the three-place `ALLOW_WRITE=false` assertion is
live-tested — attempt a write through `@context-retriever` and confirm it is rejected at all three
layers — mirroring the live-removal-probe verification pattern already established for T416's
protected paths"); `docs/artifacts/memory-scope-model-v1.md` §6 ("Composition with ADR-005
Decision 3" — this task introduces no new write path) and §8's fifth verification item ("No-write-
path confirmation (T454)... confirm it is rejected at all three of ADR-005 Decision 3's existing
assertion points, and additionally confirm no tool call exists that would let it set scope in the
first place"); `docs/artifacts/hybrid-retrieval-v1.md` §7 ("Interface for T454" — the concrete
`MemoryIndex`/`Retriever`/`RequestingContext` API this task wraps) and §8 (known limitations for
T454+, including the `platform`-matching predicate extension needing ratification once a real
agent surface exercises it).

This brief is self-contained. Read `docs/checkpoints/checkpoint-025-phase5-t453-complete.md` for
the immediate prior-session context — you do not need the full Phase 5 execution history beyond
that checkpoint plus the input documents above.

## Objective

Build `@context-retriever`: the agent surface other agents (and, transitively, the orchestrator on
their behalf) invoke to pull scoped context out of the memory layer, wrapping T453's `Retriever`
API (`implementation/runtime/memory/retrieve.py`) so that no caller needs to touch T453's Python
interface directly. This is explicitly a **wrapper task, not a new retrieval implementation** —
`plan-038`'s own words: "Wrap T453's retrieval into a read-only agent." Do not re-derive fusion,
ranking, or scope-filtering logic; call T453's existing `MemoryIndex`/`Retriever`/
`RequestingContext` API exactly as documented in `hybrid-retrieval-v1.md` §7. If wrapping that API
as-is turns out to be insufficient for a real agent surface, that is a `type: technical` blocker to
report, not a license to fork or duplicate T453's logic.

**The core deliverable is the read-only guarantee, not the wrapping mechanics.** Per `plan-035`'s
literal, non-negotiable wording (restated verbatim in `plan-038` and ADR-005 Decision 3):
`ALLOW_WRITE=false` must be asserted in **three independent places** — the agent definition, the
server config, and the deployment manifest — "per `plan-035`'s own explicit redundancy requirement
(not one flag, three)". Independent means: each of the three places must, on its own, be capable
of blocking a write attempt, using a mechanism distinct from the other two — not one boolean
constant imported or referenced from three files. A single shared `ALLOW_WRITE` constant that all
three layers read does **not** satisfy this requirement, because disabling or bypassing that one
constant would silently disable all three at once. Concretely (you may refine this design, but the
independence property is not negotiable and must be preserved under whatever concrete design you
choose):

1. **Agent definition** (`implementation/knowledge/agents/context-retriever.md`, the 28th agent
   source file, following the existing convention of the other 27 files in that directory —
   frontmatter `name`/`description`/`tools`/`user-invocable`, prose body): the `tools` list must
   not grant any write/edit-capable tool — no `edit`, no `write` — only read/query-capable tools
   (e.g. `read`, `search`, `execute` if a read-only query script is invoked via CLI, `mcp__fetch` if
   genuinely needed — justify any tool you include). This is the **declarative, LLM-facing**
   control: even if an agent session is prompted or manipulated into attempting a write, there is no
   tool grant through which to express that action. This mirrors T416's existing protected-paths
   agent-definition pointer convention — and per `tests/functional/test_protected_paths_declared.py`
   Check A, **every** file under `implementation/knowledge/agents/*.md` must contain the literal
   token `docs/artifacts/protected-paths-v1.md` somewhere in its body, including a newly-added
   28th file, or that existing repo-wide static guard fails. Add the pointer to keep this test
   green — do not weaken or special-case the guard itself.
2. **Server config**: the actual Python-level wrapper module (a natural location is
   `implementation/runtime/memory/`, alongside T452/T453's existing modules — e.g.
   `context_retriever.py` — state your actual choice in your completion report if different) must
   expose **no write/mutate function in its public API surface at all** — not "a write function
   that checks a flag and refuses," but the literal absence of any code path that could write to
   the canonical store or the derived index. This is the **application-level** control: independent
   of what the agent definition declares, because even a compromised or misconfigured caller has
   nothing to call.
3. **Deployment manifest**: a manifest artifact declaring this component's actual runtime/
   deployment permissions (a natural location is `deploy/`, following this repo's existing
   `deploy/docker-compose-t226*.yml` convention, or a manifest colocated with the module — state
   your actual choice) must declare the knowledge vault and derived index as read-only at the
   infrastructure level for this component (e.g. read-only filesystem mount/permissions, no write
   credentials to the canonical git remote, no database write role if applicable). This is the
   **infrastructure-level** control: independent of both the agent definition and the application
   code, because even a hypothetical successful application-level write attempt would still be
   rejected by the runtime environment itself.

Each layer must be **individually testable** as actually blocking a write — not merely declared.
Your own test suite must prove this (see Expected Outputs #4 and Acceptance Criteria below); the
orchestrator will separately design and run its own adversarial probe against your merged
implementation before this task is considered verified, mirroring the independent-verification
discipline already applied to every prior Phase 5 task (T452's symlink-escape probe, T453's
7-probe scope-enforcement script) — do not treat your own tests as the final word.

**Query-time scope filter reuse (not a bypass, not a parallel implementation).** `@context-
retriever` must derive a `RequestingContext(project_id, platform)` per `memory-scope-model-v1.md`
§9 point 2's proposed resolution (this task is the one that actually implements that derivation,
per that section's own words: "T454's own brief should adopt this derivation explicitly, since
T454... is the task that actually implements the agent surface this identity flows through") and
pass it into T453's existing `Retriever.search(query_text, context, top_k)` call unmodified — do
not add a second scope-filtering step, do not construct `RequestingContext` from query text or any
other user-editable input, and do not add any code path that omits it or supplies a default.
`project_id` comes from the calling session's own workspace git remote (normalized `<org>/<repo>`
slug, mirroring `memory-scope-model-v1.md` §3's existing normalization); `platform` comes from a
build-time-injected constant in each platform's own projected agent config (the same mechanism
`implementation/scripts/sync.mjs` already uses to produce platform-specific projections from the
27 — soon 28 — source agent definitions in `implementation/knowledge/agents/`), never a
runtime-settable parameter a query or prompt could influence.

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) is approved (`plan-038`). T450 (ADR-005, accepted),
T451 (scope model), T452 (indexing pipeline), and T453 (hybrid retrieval) are all done — see
`docs/checkpoints/checkpoint-025-phase5-t453-complete.md`. T453 delivered
`implementation/runtime/memory/{scope_filter,lexical,structural,rank,retrieve}.py` and
`docs/artifacts/hybrid-retrieval-v1.md`, whose §7 gives the exact `MemoryIndex`/`Retriever`/
`RequestingContext` interface this task wraps. No real vault content exists on `develop` yet
(`implementation/knowledge/memory/{general,project,shared}/` is structure-only) — reuse T452/T453's
existing synthetic fixtures (`tests/fixtures/memory/`) for your own adversarial write-attempt
tests rather than fabricating new ones, unless a genuine gap requires an addition.

## Inputs

- `docs/artifacts/hybrid-retrieval-v1.md` §7 ("Interface for T454") — the exact `MemoryIndex.load`/
  `Retriever(index)`/`retriever.search(query_text, context, top_k)` call shape to wrap, and its own
  explicit note that a `Retriever` should be constructed once per long-lived process, not per
  query.
- `docs/artifacts/memory-scope-model-v1.md` §9 point 2 — the proposed (not yet implemented)
  `project_id`/`platform` derivation mechanism this task must actually build; §4.2/§4.3 (why the
  query-time filter is one predicate, reused, not reimplemented); §8's fifth verification item
  (no-write-path confirmation, the three-layer live test).
- `docs/decisions/ADR-005-memory-layer-design.md` Decision 3 (the three-place `ALLOW_WRITE=false`
  requirement, verbatim) and its Validation section (the live-test expectation, explicitly
  mirroring T416's live-removal-probe pattern).
- `docs/artifacts/protected-paths-v1.md` — read this as the structural precedent for "three
  independent controls, not one," even though its subject matter (protected test paths) differs
  from this task's (a read-only agent's write scope). §2 ("Why three controls, not one") is the
  reasoning to carry over.
- `tests/functional/test_protected_paths_declared.py` — the existing repo-wide static guard your
  new 28th agent file must satisfy (Check A: literal pointer token present).
- `implementation/knowledge/agents/security-engineer.md` — the closest existing precedent for a
  read-only-by-tools-list agent definition in this repo (no `edit` in its `tools` list, explicit
  "you operate in read-only mode" prose) — model your frontmatter/prose discipline on it, adapted
  for this task's specific three-layer requirement.
- `implementation/scripts/sync.mjs` — how the 27 (soon 28) source agent definitions in
  `implementation/knowledge/agents/` get projected into each platform's own agent directory
  (`.claude/agents/`, `.codex/agents/`, etc.); your new agent file must project cleanly through the
  existing pipeline, not require pipeline changes.

## Constraints

- **Token budget:** 30k (`plan-038`'s own `medium`-scope estimate — "Wrapping + the three-place
  read-only assertion"). If you find yourself genuinely exceeding this mid-work, that is a
  checkpoint-worthy event per this repo's Token Governance rules — report back, do not silently
  absorb the overrun.
- **No paid or recurring-cost API calls of any kind.** This task only wraps T453's existing local
  retrieval call; it must not introduce any new embeddings provider, network dependency, or paid
  service.
- **Do not modify T452 or T453's own modules**
  (`implementation/runtime/memory/{scanner,validate,chunker,chunk_code,enrich,embed,index_writer,
  build,scope_filter,lexical,structural,rank,retrieve}.py`) — you may **import and call** them
  (in particular `retrieve.py`'s `MemoryIndex`/`Retriever` and `scope_filter.py`'s
  `RequestingContext`), but do not change their behavior. If T453's interface genuinely cannot
  support a read-only agent wrapper as documented, that is a `type: technical` blocker to report,
  not a silent edit to T453's code.
- **Do not revise** `ADR-005-memory-layer-design.md`, `memory-scope-model-v1.md`, or
  `hybrid-retrieval-v1.md` themselves (consume, do not edit) — if any is genuinely underspecified
  for something you need, that is a `type: unclear_requirements` blocker with a proposed
  resolution, not a license to silently edit the prior artifacts.
- **Do not touch:** `.mcp.json` anywhere, for any reason. `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.json`/`.md` (frozen, unrelated to this task). `feature/T475-codex-
  platform-integration` (out of scope, unrelated branch). Do not start any Phase 3 work.
- **File ownership:** you may create the new agent source file
  (`implementation/knowledge/agents/context-retriever.md`), its server-config/wrapper module(s)
  (natural location `implementation/runtime/memory/`), its deployment manifest (natural location
  `deploy/`, or colocated with the module — state your choice), tests, and a short design-note
  artifact (e.g. `docs/artifacts/context-retriever-v1.md`) documenting the three-layer design, the
  `RequestingContext` derivation mechanism, and your own live-test methodology/results — T455/T456
  (not your task) will consume the working agent surface this produces.
- **Work in your own worktree/branch:** `agent/backend-developer/T454`, created from `develop`
  (after this dispatch brief itself is merged). Commit as you go; run the full test suite
  (`python3 tests/run.py`) and confirm no regressions before reporting completion, including the
  existing `test_protected_paths_declared.py` guard. **Do not self-merge** — push and open a merge
  request, then stop; the orchestrator independently verifies and merges.
- Follow this repo's coding standards (max 50-line functions, max 4 parameters, early returns) and
  Conventional Commits.

## Expected Outputs

1. `implementation/knowledge/agents/context-retriever.md` — the new 28th agent source file:
   `tools` list contains no write/edit-capable tool; prose states the read-only-by-construction
   guarantee and points at `docs/artifacts/protected-paths-v1.md` (required by the existing static
   guard) and this task's own new design artifact; `user-invocable: false` (per `AGENTS.md`, only
   orchestrators are user-invocable — `@context-retriever` is a subagent other agents/the
   orchestrator invoke on their behalf).
2. A server-config/wrapper module (natural location `implementation/runtime/memory/`) implementing
   the actual `@context-retriever` callable surface: constructs exactly one `Retriever` per
   long-lived process, derives `RequestingContext` per the mechanism above, exposes a query
   function/CLI, and has **no write/mutate function in its public API** — not a guarded one, an
   absent one.
3. A deployment manifest artifact declaring this component's runtime permissions as read-only
   against the canonical knowledge base and derived index, independent of the other two layers.
4. Tests proving all three layers actually block a write attempt: (a) a static check that the new
   agent definition's `tools` list contains no write-capable tool (extending or mirroring
   `test_protected_paths_declared.py`'s existing static-guard pattern); (b) a check that the
   wrapper module's public API has no write/mutate function (e.g. enumerate exported callables and
   assert none match a write/mutate naming or capability pattern); (c) a check that the deployment
   manifest declares read-only access (parse the manifest and assert its write-permission fields
   are false/absent); and (d) an end-to-end adversarial probe — attempt an actual write through
   `@context-retriever`'s real callable surface (not a mock) and confirm it is rejected, mirroring
   ADR-005's Validation section wording exactly ("attempt a write through `@context-retriever` and
   confirm it is rejected at all three layers").
5. `docs/artifacts/context-retriever-v1.md` (or equivalent, name stated in your completion report):
   the three-layer design and why each is independent of the other two, the `RequestingContext`
   derivation mechanism (`project_id` from workspace git remote, `platform` from build-time
   sync.mjs projection), and your live-test methodology/results.

## Acceptance Criteria

1. **No write path from any agent into the canonical knowledge base** (Phase 5's own literal
   acceptance criterion, `plan-035` §2.4) — demonstrated by the end-to-end adversarial probe
   (Expected Output #4d), not merely asserted.
2. **Three independently-enforced `ALLOW_WRITE=false` assertions**, each capable of blocking a
   write on its own, using a distinct mechanism from the other two (declarative tool-scoping in the
   agent definition; absent write API in the server-config wrapper module; infrastructure-level
   read-only declaration in the deployment manifest) — not one shared constant referenced three
   times. Your completion report must explain concretely why disabling or bypassing any single one
   of the three would not, by itself, make a write possible.
3. **Correctly reuses T453's query-time scope filter, not a bypass or a parallel implementation**:
   `@context-retriever` calls `Retriever.search(query_text, context, top_k)` exactly as
   `hybrid-retrieval-v1.md` §7 documents, with a `RequestingContext` built per the derivation
   mechanism above; no second/duplicate scope-filtering logic exists anywhere in this task's new
   code, and no code path constructs `RequestingContext` from query text, prompt content, or any
   other caller-editable input.
4. **`RequestingContext` derivation is non-spoofable by design**: `project_id` is derived from the
   calling session's own workspace git remote (not a parameter the caller supplies directly);
   `platform` is derived from a build-time-injected constant in each platform's projected agent
   config (not a runtime parameter). Demonstrate both derivations with a concrete example.
5. **New agent definition passes the existing repo-wide static guard**
   (`tests/functional/test_protected_paths_declared.py`) without modification to that guard's own
   logic — the new file includes the required policy-doc pointer token.
6. **`python3 tests/run.py` passes with no regressions** from your branch's baseline; new tests you
   add (Expected Output #4's four checks, at minimum) are included in that run, not a separate ad
   hoc script.
7. `sync.mjs`'s existing projection pipeline produces a valid per-platform projection of the new
   agent definition with no pipeline changes required — run the sync and confirm the new agent
   appears correctly in at least the Claude Code projection (`.claude/agents/context-retriever.md`)
   with its `tools` list correctly reflecting the read-only grant.
8. **Feeds T455/T456**: the working `@context-retriever` surface (query function/CLI) is documented
   clearly enough that T455 (retrieval eval sub-suite) and T456 (downstream measurement) could
   invoke it without re-deriving this task's design.
9. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Specific cases already anticipated:

- If T453's `Retriever`/`MemoryIndex`/`RequestingContext` interface genuinely cannot support a
  read-only agent wrapper as documented in `hybrid-retrieval-v1.md` §7 (e.g. it requires a
  capability that would force a write path): report `type: technical`, `severity: critical` — this
  is a hard stop, not something to route around by editing T453's code or inventing a parallel
  retrieval path.
- If achieving genuine independence between the three `ALLOW_WRITE=false` layers (Objective, point
  by point above) turns out to be infeasible in this repo's current deployment model (e.g. no real
  "deployment manifest" concept exists yet for a component like this): this is a `type:
  unclear_requirements`, `severity: minor` finding — propose a concrete resolution (e.g. the
  manifest is a new, minimal artifact this task introduces, following the closest existing
  precedent named in Inputs) rather than silently collapsing to two layers or one.
- If `sync.mjs`'s existing projection pipeline does not handle the new 28th agent file cleanly
  (e.g. a hardcoded count, an allowlist that needs updating): report `type: technical`,
  `severity: major`, with the specific failure — do not silently patch the pipeline's own logic
  without flagging it, since that pipeline is shared infrastructure other in-flight work may also
  depend on.
- If deriving `platform` from a "build-time-injected constant in each platform's own projected
  agent config" is genuinely ambiguous given how `sync.mjs` currently structures per-platform
  frontmatter: this is exactly the ambiguity `memory-scope-model-v1.md` §9 point 2 flagged and
  explicitly deferred to this task to resolve — make and document a concrete choice, this is not a
  blocker on its own unless the chosen mechanism turns out to be spoofable by caller-editable
  input, which would be `type: technical`, `severity: major`.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
