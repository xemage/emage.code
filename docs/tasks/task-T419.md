# Task T419 (+ T408) — Two-arm Terminal-Bench delta runner + budget guard

**ID:** T419 (primary), T408 (budget guard, implemented alongside per plan-035's own sequencing
note — see brief below)
**Owner:** devops-engineer
**Status:** in_progress
**Priority:** P0 (T419), P1 (T408)
**Depends on:** T418 (done — `docs/benchmarks/tb-subset.json`, `docs/benchmarks/tb-subset.md`)
**Created:** 2026-08-13
**Completed:** —
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 2 table, rows
T419 and — under its original, now-renamed ID — `T41B`; see `docs/tasks/active-tasks.md`'s "Task
ID note" for the T41B→T408 rename). Also `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1
("Terminal-Bench: measure the delta, not the score") for the full mechanics rationale.

This brief is self-contained. Read `docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`
and `docs/tasks/task-T418.md` (including its Completion addendum) for the Harbor environment
already verified working in this repo and the frozen subset you'll iterate against.

## Objective
Build `scripts/tb-delta.sh`: a two-arm Terminal-Bench runner that measures emage.code's
contribution as `score(B) - score(A)`, where:
- **Arm A (control):** stock `claude-code` (Harbor's built-in agent), no emage.code projection.
- **Arm B (treatment):** identical in every other respect, with the emage.code projection applied
  to the container workspace before the agent runs.
- Same model, dataset, timeouts, resources, seed, and `-k` across both arms.
- Both arms run against `docs/benchmarks/tb-subset.json`'s frozen 25-task subset (not the full
  89-task dataset — that's a release-baseline concern, out of scope here).

Alongside this, implement **T408's budget guard**: a hard cost/time cap per invocation of
`tb-delta.sh`, abort-on-projected-overrun, economy model as the default for iteration, frontier
model reserved for release baselines only. Per the plan's own note, this is "likely implemented
alongside T419 rather than as a fully separate artifact" — build it as part of the same script
(e.g. a pre-flight budget check before the arms run), not a separate file, unless you find a strong
reason to split it.

## The one non-negotiable acceptance criterion
**The two arms must differ ONLY in whether the emage.code projection is applied — nothing else.**
Same model, same dataset slice, same timeouts, same resource limits, same seed, same `-k`,
same everything except the projection. You must be able to **prove** this by diffing the two arms'
actual Harbor run configurations (not just asserting it in prose) — any other difference between
the arms is a defect in your runner, not an acceptable variable. Build this proof into the script's
own output (e.g. dump both configs and diff them programmatically as part of every run, fail loudly
if they differ in anything beyond the projection).

## What "applying the emage.code projection" means (research required)
`claude-code` is a Harbor built-in agent — Arm A needs no custom agent code. For Arm B, you need to
get the emage.code projection (this repo's `.claude/` tree — agents, skills, commands, rules,
`.mcp.json`) into the container's workspace before/as the agent starts, without changing the model,
timeouts, or any other run parameter. Research current Harbor mechanics via WebFetch/live docs
before assuming anything (mirror T417's own practice — Harbor's docs/CLI may have moved since
training data cutoff). Plausible starting points, verify all of them against current docs:
- Harbor's `BaseInstalledAgent`/`BaseAgent` subclassing and `--agent-import-path` (per plan-035
  §2.2.1's "Mechanics" citation) — likely relevant for *custom* agents, may or may not have a
  lighter-weight workspace-setup hook usable with a stock built-in agent like `claude-code`.
  Sources cited in plan-035 §2.2.1: `https://www.harborframework.com/docs/`,
  `https://www.tbench.ai/docs/`. Re-verify these are still current.
- Harbor task/environment definitions typically include a `Dockerfile`/`environment/` per task
  (confirmed present in the local cache from T417/T418's work,
  e.g. `~/.cache/harbor/tasks/packages/terminal-bench/dna-assembly/*/environment/Dockerfile`) —
  there may be a supported way to layer an additional setup step (copy files into the workspace,
  run a setup script) without modifying the task's own environment definition, which must stay
  identical between arms per the non-negotiable criterion above.
- If Harbor has no clean supported mechanism for this, that is a genuine `type: technical`,
  `severity: major` blocker — report it with what you found, rather than hacking around it in a
  way that risks silently changing something else between the arms.

## T408 — budget guard specifics
- **Hard cap per invocation:** a configurable ceiling (time and/or estimated cost — your call on
  which is more practical to enforce given Harbor's actual output, but time is likely more directly
  measurable; note the estimated-cost angle as a stretch goal if time doesn't get you there).
- **Abort on projected overrun:** after a small number of completed task-runs, extrapolate the
  remaining cost/time and abort before committing to the full run if it would blow the cap — don't
  just fail after the fact.
- **Economy model default:** `tb-delta.sh` should default to an economy-tier model for iteration
  runs (not the frontier model), with an explicit flag/parameter to opt into a frontier model for
  release-baseline runs. Since Arm A is `claude-code` per the plan's resolved Open Question 3, "the
  model" here means the underlying model `claude-code` is configured to use — research how Harbor's
  `claude-code` built-in agent selects/is passed a model, and make it a runner parameter.
- **Verify the guard is actually exercised, not just declared:** prove it triggers (e.g. set an
  artificially low cap and confirm the script aborts before completing an over-budget run) as part
  of your own testing, not just code review.

## Scope boundary for THIS task — do not run the real measurement here
T419/T408 is infrastructure. **Do not run a full `k>=3` measurement across all 25 subset tasks as
part of this task** — that is T407's job (a separate, later task, not yet dispatched). Validate
your runner with the smallest, cheapest smoke test that actually proves it works end-to-end: e.g.
`-k 1` against 1-2 tasks from the subset, economy model, both arms. This is validation of the
mechanism, not a result to publish.

## Resource awareness (read before touching Docker)
This is a shared host. Before any Docker-heavy step (smoke-testing the runner), run `free -h` and
`timeout 8 docker ps` yourself and confirm the daemon is responsive and swap has meaningful headroom
(prior blocker: swap fully saturated — see `docs/benchmarks/environment.md`'s 2026-08-12 incident).
If you hit the same class of failure, report it honestly per the Blocker Protocol below — do not
force through, do not fabricate a pass.

## Inputs
- `docs/benchmarks/tb-subset.json`, `docs/benchmarks/tb-subset.md` (T418, done)
- `docs/benchmarks/environment.md` (T417 — Harbor/Docker versions, host resource history, both the
  2026-08-12 blocker and the 2026-08-13 successful retry)
- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1 in full
- This repo's `.claude/` tree (what "the emage.code projection" actually consists of)

## Expected outputs
- `scripts/tb-delta.sh` — the two-arm runner, with the budget guard built in.
- Output format: since `scripts/scorecard.py` (T413, Layer 1, not yet built) is meant to share a
  common JSON scorecard format per the plan, and Layer 1/Layer 2 are running in parallel, **define
  a reasonable, self-documented JSON schema now** (fields at minimum: per-arm results, `k`, model,
  dataset subset reference, delta, spread, cost/time, timestamp) rather than blocking on T413. Note
  explicitly in your completion report that this needs a reconciliation pass once T413 lands (a
  small follow-up, not a redesign, if the shapes differ) — flag this as `type: dependency`,
  `severity: minor`, tracked not silently absorbed.
- A short doc, `docs/benchmarks/tb-delta-runner.md` or similar (your call on name) documenting: how
  to invoke the script, what the budget guard does and how to configure it, and — critically — how
  the "projection applied vs. not" mechanism actually works technically (this is load-bearing
  documentation; a future reader auditing "did the arms really only differ in projection" needs
  this to verify your claim).

## Acceptance criteria
1. `scripts/tb-delta.sh` runs both arms and emits a scorecard JSON with Arm A, Arm B, delta, and
   spread fields present (even if the smoke test's `k` is too low for a meaningful spread — the
   *field* must exist and be computed correctly for whatever `k` was actually run).
2. **The two arms' actual Harbor run configs are diffed programmatically as part of the run, and
   the diff is empty except for the projection-related difference.** This must be demonstrated, not
   asserted — include the actual diff output in your completion report.
3. Budget guard demonstrably aborts an artificially-capped run before it completes (shown, not
   just described).
4. Economy model is the default; a frontier-model override exists and is documented.
5. A cheap smoke test (`k=1`, 1-2 tasks) actually ran successfully end-to-end on this host,
   producing real output — not simulated.
6. `docs/benchmarks/tb-delta-runner.md` documents the projection mechanism clearly enough for an
   independent reviewer to audit criterion 2's claim without re-deriving your research.
7. `python3 tests/run.py` still exits 0 (no regression in the existing suite).

## Blocker protocol
- Harbor has no clean, supported way to apply a workspace projection without risking a difference
  beyond "projection applied" between the arms -> `type: technical`, `severity: major` — report
  what you found and what options exist; do not hack around it silently.
- Host resource exhaustion (Docker daemon unreachable, swap saturated) during smoke-testing ->
  `type: external`, `severity: critical`, per T417's established precedent — report honestly, do
  not force through.
- If `claude-code`'s model selection mechanism in Harbor is unclear or undocumented ->
  `type: unclear_requirements`, `severity: minor`.

## Git workflow
1. `cd /home/emage/Code/emage/worktrees/phase1-tb-delta` (existing worktree, branch
   `feature/T418-phase1-tb-delta-harness-v6.12.0`, commit `fb136c2` already on it — do not create a
   new worktree/branch).
2. Build, test, verify per the acceptance criteria above.
3. Commit with a Conventional Commit message (`feat(benchmarks): two-arm Terminal-Bench delta
   runner + budget guard... Refs T419, T408`).
4. Do not push, do not open an MR. Report worktree path (unchanged), branch name (unchanged),
   commit SHA(s), the config-diff proof (criterion 2), and the budget-guard abort proof
   (criterion 3) back to the orchestrator.

## Constraints
- Token budget: ~55k tokens (large scope per the plan — real infrastructure work, budget
  accordingly).
- File ownership: `scripts/tb-delta.sh`, `docs/benchmarks/tb-delta-runner.md` (or your chosen
  name). Do not modify `docs/benchmarks/tb-subset.json`/`.md` (frozen, T418) or
  `docs/benchmarks/environment.md` (T417's).
