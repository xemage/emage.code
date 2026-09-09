# Task T457 — Scoped, non-`Bash` execution/read primitive for `@security-engineer` and `@context-retriever`

**ID:** T457
**Owner:** solution-architect (design first; implementation owner(s) — likely `devops-engineer`
and/or `backend-developer` for the scoped-tool mechanism itself — to be assigned once the design
lands and the `.mcp.json` question below is resolved)
**Status:** pending — **NOT DISPATCHED.** Recorded as a properly-scoped backlog item per explicit
user instruction during T454's closeout MR review (2026-09-09); do not dispatch without first
re-confirming this session's (or the then-current session's) standing constraint on touching
`.mcp.json` still applies, since that constraint gates this task's real fix.
**Priority:** P1 (real, disclosed security/tool-scoping gap on two already-shipped read-only agents
— important, but does not block Phase 5's critical path; see "Does this block T455/T456?" below)
**Depends on:** None structurally. Practically benefits from being scoped after any MCP-server
design precedent Phase 3 (Maturity Ladder, not yet approved) or other in-flight MCP work might set,
but is not blocked by either.
**Created:** 2026-09-09
**Completed:** —
**Based on:** `docs/artifacts/context-retriever-v1.md` §2/§2.1 (the honest accounting of what T454's
three `ALLOW_WRITE=false` layers actually enforce in this repo's current, non-containerized
deployment — corrected during this task's own creation, same session); `docs/tasks/task-T454.md`'s
completion addendum (acceptance criterion 1 honest downgrade, same date); `docs/decisions/ADR-005-
memory-layer-design.md`'s Validation-section addendum (same date, same finding, ADR-level record);
`implementation/knowledge/agents/security-engineer.md` (the pre-existing "read-only mode" agent
whose enforcement model this task generalizes from — `tools: [read, search, execute, web,
mcp__fetch]`, same `execute` → `Bash` gap, older and un-flagged until this session); `implementation/
knowledge/agents/context-retriever.md` (the newer agent carrying the identical gap, found and
honestly documented, not silently shipped, during T454); `implementation/platforms/claude-code.json`
(the `toolMap` mapping `"execute": "Bash"` that is the concrete mechanism of the gap for both
agents on this one platform — the same mapping likely needs checking per-platform, see Objective).

## Objective

Give both `@security-engineer` and `@context-retriever` a genuinely scoped, non-`Bash` execution/
read primitive, so that their existing "read-only" / "no write path" prose claims become claims a
tool-scoping mechanism actually enforces, rather than claims that rest entirely on the underlying
LLM choosing to follow an instruction while holding unrestricted shell access. This is explicitly a
**design-then-build task, not a quick flag flip** — the current `tools: [..., execute, ...]` grant
on both agents maps, on at least the Claude Code platform (`implementation/platforms/claude-code.json`
`toolMap`: `"execute": "Bash"`), to fully unrestricted `Bash`, and there is currently no narrower,
scoped "run this specific read-only command, nothing else" primitive in this repo's tool vocabulary
to grant instead. Building one is the real work here.

**This task is being recorded now, not dispatched now.** Per this session's own standing
constraint, `.mcp.json` may not be touched, and the most likely genuine fix — a dedicated MCP server
(or an equivalent scoped-tool mechanism registered the same way this repo's other MCP servers are)
exposing a narrow, read-only, non-shell query/search primitive — would need to touch `.mcp.json` in
some form to register it. That makes this task un-dispatchable under the current session's
constraints regardless of priority. It is recorded here so it is not lost, not so it can be started
immediately.

## Context

T454 (`@context-retriever` read-only agent wrapper, `docs/tasks/task-T454.md`) shipped with a
three-layer `ALLOW_WRITE=false` design (agent-definition tool-scoping, server-module API absence,
deployment-manifest read-only declaration) modeled explicitly on this repo's pre-existing
`security-engineer.md` "read-only mode" precedent. MR review of T454's implementation (this same
session, 2026-09-09) found that the agent-definition layer for *both* agents is declarative/prose
only, not a technical restriction: both agents' `tools:` lists include `execute`, which the Claude
Code platform's own `toolMap` translates to unrestricted `Bash` — confirmed live for
`context-retriever` (`implementation/.claude/agents/context-retriever.md` grants `tools: Read,
Bash`) and structurally identical for `security-engineer` (same `toolMap` entry, same platform,
same `execute` token in its own source `tools:` list). Neither agent's read-only/no-write claim is
backed by a technical tool-scoping restriction on this platform; both rest on the model following
the agent definition's own instruction.

This is not a new problem introduced by T454 — `security-engineer.md` has carried this exact same
gap since before this task existed, un-flagged until T454's review surfaced the pattern by
comparison. The user's own decision on how to treat this (see `docs/artifacts/context-retriever-v1.md`
§2.1 and the ADR-005/task-T454.md addenda) was: **accept prose-only enforcement for now, matching
the existing `security-engineer.md` precedent already in this repo**, correct the overclaiming
documentation that had asserted otherwise, and open this follow-up task to track the real fix
properly rather than leaving it undocumented. This task is that tracking record.

## Inputs

- `docs/artifacts/context-retriever-v1.md` §2 ("Three independent `ALLOW_WRITE=false` layers") and
  §2.1 ("Honest note on what is and is not technically enforced today") — the concrete, current-state
  description of the gap this task must close.
- `docs/tasks/task-T454.md`'s completion addendum — the honest downgrade of T454's own acceptance
  criterion 1, and why.
- `docs/decisions/ADR-005-memory-layer-design.md`'s Validation-section addendum (2026-09-09) — the
  ADR-level record of the same finding.
- `implementation/knowledge/agents/security-engineer.md` and `implementation/knowledge/agents/
  context-retriever.md` — the two agent source files whose `tools:` grants need a genuinely scoped
  alternative to `execute`/`Bash` for their read-only/audit-only use cases.
- `implementation/platforms/*.json` (all 7 platform manifests, not just `claude-code.json`) — the
  `execute` → shell-tool mapping needs checking per platform, not assumed uniform; different
  platforms may already have narrower primitives or may all share the same gap.
- `docs/artifacts/mcp-platform-contract-v1.md` (T420) — the existing per-platform MCP contract this
  task's likely MCP-server-based fix would need to conform to.
- `.mcp.json` (read-only reference — **do not modify**, see Constraints) — the current core/extended
  MCP server registration this task's real fix would eventually need to extend, once dispatched
  under a session where that constraint does not apply.

## Constraints

- **Do not touch `.mcp.json`, for any reason, in this task's initial dispatch** under the standing
  constraint that gated this task's creation. If a future dispatch of this task occurs under a
  session where that constraint has been explicitly lifted by the user, re-confirm that lift
  explicitly in the dispatch brief before proceeding — do not assume it carries over silently.
- Do not weaken or remove `security-engineer.md`'s or `context-retriever.md`'s existing prose
  read-only instructions while this task is pending — the declarative layer, while not technically
  enforced, is still the only enforcement that exists today and must not regress.
- Do not silently narrow this task's scope to only one of the two agents — the brief that actually
  dispatches this work must address both `security-engineer.md` and `context-retriever.md` together,
  since they share the identical gap and a fix designed for one should be validated against both
  before being called done.
- This task's real fix is expected to require a genuine architecture decision (new MCP server vs.
  some other scoped-tool mechanism vs. a per-platform tool-map change vs. something else not yet
  considered) — do not dispatch this directly to a developer agent as an implementation task without
  a `solution-architect` design pass first, per this repo's own Architecture Gate discipline.

## Expected Outputs (once actually dispatched — not required to open this backlog record)

1. A design artifact (e.g. `docs/artifacts/scoped-execution-primitive-v1.md`) evaluating at least:
   (a) a dedicated MCP server exposing a narrow, read-only, non-shell query/search primitive; (b) a
   per-platform tool-map change that maps a new abstract tool name (e.g. `read_execute` or similar)
   to a genuinely scoped command allowlist rather than full `Bash`; (c) any other viable mechanism
   this repo's existing MCP/tool infrastructure already supports that was not obvious at task-creation
   time. Recommend one, with the same "why this and not the alternatives" rigor this repo's other
   ADRs (e.g. ADR-005) already apply.
2. Updated `tools:` grants for both `security-engineer.md` and `context-retriever.md` source files,
   replacing `execute` with the new scoped primitive (or narrowing `execute`'s own meaning, per
   whichever design is chosen) — regenerated through `sync.mjs` across all 7 platforms with no drift.
3. A live adversarial test proving the new primitive actually blocks a write attempt for both
   agents on at least the Claude Code platform (mirroring T454's own live-test discipline, this time
   against a real scoped tool grant, not a module-level API surface) — the test this task's own
   design must satisfy that T454's `EndToEndAdversarialWriteProbeTests` could not.
4. Updated cross-references: `docs/artifacts/context-retriever-v1.md` §2.1 and `docs/decisions/
   ADR-005-memory-layer-design.md`'s Validation addendum should each get a short "resolved by T457"
   note once this lands, without deleting the honest history of the gap being found and initially
   accepted as prose-only.

## Acceptance Criteria (once actually dispatched)

1. Both `security-engineer.md` and `context-retriever.md` carry a `tools:` grant that, on every
   platform this repo projects to, maps to something narrower than unrestricted shell access for
   their read-only/audit-only use case — demonstrated per platform, not asserted for one and assumed
   for the rest.
2. A live adversarial write-attempt test exists and passes for both agents against the new
   primitive, on at least Claude Code (and ideally at least one other platform with a genuinely
   different tool-map mechanism, to avoid a single-platform false sense of coverage).
3. `.mcp.json` (if the chosen design touches it) is modified only with explicit, current-session user
   authorization to do so — this task must not silently treat T457's own existence as blanket
   pre-authorization for a constraint that was explicitly still in force when this brief was written.
4. No regression to either agent's existing declarative read-only prose — the new technical control
   is additive to, not a replacement for, the existing instruction-level guidance.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Anticipated:

- If, at actual dispatch time, `.mcp.json` still may not be touched and no non-`.mcp.json`-touching
  design proves viable after genuine investigation: report `type: unclear_requirements`,
  `severity: major` — this may mean the task stays open/backlog indefinitely until the constraint
  lifts, which is a legitimate outcome to report back, not a failure to route around.

## Does this block T455/T456?

**No, confirmed against their actual acceptance criteria in `docs/plans/plan-038-phase5-detailed-
planning.md`,** not assumed. T455 (retrieval eval sub-suite: precision/recall/irrelevant-context-rate/
latency, owner `evaluation-agent`, depends only on T454) and T456 (downstream measurement/ship gate:
re-run the Phase 1 golden-suite baseline with retrieval enabled, owner `evaluation-agent`, depends on
T454 + T455) both measure **retrieval quality and downstream task-success impact** — neither task's
own acceptance criteria (plan-038 lines ~236-254) reference write-safety, tool-scoping, or
`ALLOW_WRITE` enforcement at all. T457 is purely about hardening an already-accepted (if newly
honestly-documented) declarative-enforcement gap; it does not sit on T455/T456's dependency path.
