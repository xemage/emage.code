# T458 Infrastructure Requirements — What It Takes to Run a Live Golden-Suite Harness

> Summary artifact, written to answer "what infrastructure does T458 actually need before it can be
> dispatched." Synthesized directly from `docs/tasks/task-T458.md` and
> `docs/plans/plan-040-t458-golden-live-harness-followup.md` (both already committed, neither
> modified by this document) — not a new decision, a readable consolidation of what those two
> documents already specify.

## The one-sentence answer

**T458 needs no new hosts, no new Docker infrastructure, and no paid API access** — it deliberately
reuses this repo's existing Claude Code agent-dispatch mechanism (the same one every task in this
entire session ran through) instead of anything Terminal-Bench-shaped. What it needs instead is new
*software*: a trial-isolation/orchestration layer, a way to selectively expose `@context-retriever`
per session, and a bridge into the golden suite's existing `expect.py` contract.

## Why this is a different shape of infrastructure than T407's Terminal-Bench harness

T417–T419 (the closest precedent this repo has for "build a live-trial harness") needed Docker
containers per trial, a remote daemon, host resource provisioning, and eventually a second
dedicated host after resource contention forced a migration. **T458 explicitly does not follow that
model.** Terminal-Bench trials execute untrusted, isolated shell sessions inside disposable
containers because the tasks themselves are arbitrary terminal work. T458's trials are Claude Code
agent sessions working against this repo's own golden-suite fixtures — the same kind of work every
subagent dispatched this session already does in an isolated git worktree. The brief is explicit
that trial isolation should be *"adapted to whatever isolation mechanism fits a live Claude Code
session rather than a Docker container, since this is not a Terminal-Bench-style sandboxed task
execution."*

## What actually needs to be built (software, not hardware)

1. **A two-arm session dispatcher.** For each golden case (or a disclosed subset), launch two live
   agent sessions — a control arm without `@context-retriever` available, and a treatment arm with
   it wired in per `context-retriever-v1.md`'s real interface. This almost certainly means using
   this session's own Agent-dispatch primitive twice per case, with each arm's dispatch controlling
   which agents are visible to that session — not a new dispatch mechanism, a new *pattern* of using
   the existing one.
2. **Per-trial isolation**, mirroring the git-worktree pattern this entire session used for every
   subagent dispatch: each of the (cases × 2 arms) sessions needs its own clean workspace so trials
   don't interfere with each other's file state, exactly like every T450-T458 implementer already
   worked in its own worktree/branch.
3. **A prompt-to-candidate-output pipeline**: feed each case's real `brief.md` as the literal
   session prompt (the format spec already anticipates this reuse — no new prompt authoring), and
   capture whatever the live session actually produces as a real candidate-output directory.
4. **A bridge into `expect.py`'s existing contract**, pointed at the live run's candidate directory
   instead of the checked-in `fixture/`. This is the one piece with a real, disclosed risk: if
   `expect.py`'s `check(case_dir)` signature can't cleanly accept an alternate directory without
   modification, that's a **protected-path exception request** (per `protected-paths-v1.md`'s
   documented process) — pre-approval required before any such edit, not a silent workaround, and
   `scripts/scorecard.py`/`tests/golden/**` themselves stay untouched regardless.
5. **A pre-registered "measurably improve" threshold**, written down *before* any comparison run —
   mirroring T407's own frozen-decision-rule discipline, specifically to close the exact
   "ship-gate-applied-loosely" risk `plan-038` already flagged for T456.
6. **Test tiering**: the harness's own non-agent logic (isolation setup, scoring, threshold
   comparison) needs default-tier, no-agent-invocation tests; anything that actually invokes a live
   session needs to be opt-in/env-var-gated, matching the `EMAGE_*`-gated pattern T452 already
   established for its own expensive optional test tier.

## What it explicitly does *not* need

- No new Docker daemon, no container runtime, no host resizing or provisioning.
- No paid/metered model API — live sessions run through the existing interactive dispatch
  mechanism. (If a design genuinely needs a separate metered endpoint, the brief treats that as a
  `type: external`, `severity: critical` blocker requiring explicit cost authorization first,
  mirroring T407's money-gate — not something to assume is pre-approved.)
- No changes to `tests/golden/**`, `scripts/scorecard.py`, or `docs/benchmarks/tb-subset.json`/`.md`
  — the harness must consume the existing case format and `expect.py` contract exactly as-is (import
  and call, the same way `scripts/scorecard.py` itself already does), not fork or reimplement it.
- No new secrets, and specifically no `.mcp.json` involvement at all.

## Honest scope risk, carried forward from the brief itself

Both `task-T458.md` and `plan-040` explicitly refuse to pre-commit to "this is a medium task."
T407's own history (a first design that had to be re-scoped mid-flight into "Design A" after the
original approach proved insufficient) is the named precedent for what could happen here too — the
brief instructs the implementer to report a real need for multi-task re-sequencing as an *expected*
outcome, not a failure, rather than force the whole harness into a single dispatch that doesn't fit.
Live-session non-determinism (an agent doing genuinely different things across nominally-identical
runs) is called out as a real possibility requiring a designed response — e.g. multiple trials per
case per arm, the same `k`-run shape T407 itself used — rather than a single noisy run reported as
conclusive.

## Bottom line for whoever dispatches T458

This is a same-machine, no-new-infrastructure task in the hardware sense, but a real, possibly
multi-task software-engineering effort in the design sense — closer to "build a small evaluation
framework" than "stand up a benchmark harness." The existing `t407-tb-delta` worktree and the
`10.10.160.11`/`10.10.160.12` host topology are irrelevant to it; nothing there needs to be reused
or touched. Dispatch it the same way every Phase 5/Phase 3 task was dispatched this session —
`devops-engineer`, its own worktree off `develop`, tool-grant verified first, independent
adversarial verification before merging.
