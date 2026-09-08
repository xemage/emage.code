# Task T409 — Extend the T415 failure taxonomy to ingest Harbor trajectories

**ID:** T409
**Owner:** devops-engineer
**Status:** in_progress
**Priority:** P0
**Depends on:** T415 (done — `docs/artifacts/failure-taxonomy-v1.md`), T407 (done — Terminal-Bench
delta measurement, 2026-09-08, `docs/benchmarks/tb-delta-v6.12.0.md`). Both satisfied; T409 is the
last open item of Phase 1's Layer 2 (plan-035 §2.4).
**Created:** 2026-09-08
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1, Layer 2 table, `T41C` row
(renamed `T409` in this repo's ledger, see `active-tasks.md`'s "Task ID note"): *"Extend the T415
failure taxonomy to ingest Harbor trajectories, so Terminal-Bench failures cluster in the same
`cause × behavior × mechanism` scheme as golden failures. One taxonomy, two sources."*
`docs/artifacts/failure-taxonomy-v1.md` §7 ("Reuse notes for T409"), which was written by T415
specifically anticipating this task.

## Why this task is gating, not optional

Phase 1's own acceptance-criteria checklist (`plan-035` §2.4, immediately before "Gate G1 closes
here") has ten bullets. Nine are independently verified `done`. The tenth —
**"Terminal-Bench and golden failures appear in one taxonomy"** — is this task's sole deliverable
and is not yet met: `docs/artifacts/failure-taxonomy-v1.md` currently classifies only the 9
golden-suite `known_failing` cases; no Harbor/Terminal-Bench trajectory has ever been run through
the three axes. Per plan-035's own wording, **Gate G1 does not close until this bullet is
checked**, regardless of T407's Inconclusive classification (ADR-004 confirms T409 is unaffected
by that outcome — see "Depends on" above). This task's completion, independently verified, is
what closes G1.

## Scope discipline — read before starting

This is classification/tooling work over **data that already exists on disk**. No new Terminal-
Bench trials, no new paid API calls, no new Harbor dispatches of any kind. If at any point
completing this task seems to require running new trials (e.g., "we need more failure examples"),
stop and report a `type: unclear_requirements`, `severity: minor` blocker rather than dispatching
anything — that decision does not belong to this task per the orchestrator's own constraints this
session.

## Source data (already on disk — do not re-fetch or re-run anything)

Two independent T407 measurements produced real Harbor trajectories, both usable:

1. **Original k=3 single-pass run (2026-08-14)** — local, already in this repo's canonical
   worktree structure (not the isolated `docs-t409-dispatch` worktree this brief lives in —
   create your own fresh worktree per the Git Workflow section below, and copy or reference these
   paths from `develop`'s checkout, or from
   `/home/emage/Code/emage/worktrees/t407-tb-delta/jobs/tb-delta-20260814T111217Z-arm-{A,B}/`
   if that worktree still exists at dispatch time — verify it exists before relying on it, it is
   a leftover working directory, not a tracked artifact). Each task-trial subdirectory contains a
   `result.json` with `task_id.name`, `verifier_result.rewards.reward`, `exception_info`
   (`null` for a genuine task-level outcome, non-null for an infrastructure error), and
   `agent_result` fields. 76 subdirectories per arm (75 trials + 1 top-level aggregate
   `result.json`).
2. **Design A's 3 successful passes (2026-09-08)** — remote only, **not copied to this repo**
   (161MB, deliberately left in place per T407's closeout "Artifact reconciliation" note — see
   `docs/tasks/task-T407.md` and `docs/tasks/completed-tasks.md`'s T407 row). Reachable at
   `10.10.160.11:/root/emage-code-t407/jobs/tb-delta-{20260907T162617Z,20260907T203448Z,20260908T001726Z}-arm-{A,B}/*/result.json`.
   Read-only access to this host for this purpose is in scope (this is reading existing files, not
   dispatching new work); do not run `harbor` or any Docker command against this host as part of
   this task.
3. **The two failed Design A attempts** (`10.10.160.11`'s bind-mount-stranded runs, and the
   2026-09-05 host-exhaustion-halted attempt, both 100% `RewardFileNotFoundError`/
   `AgentTimeoutError`) are also real trajectory data, of a different (infrastructure-failure)
   kind — per `task-T407.md`'s closing note, whether these are useful for taxonomy purposes is
   explicitly left as this task's own judgment call, not pre-decided. A reasonable default: they
   are out of scope for the `cause × behavior × mechanism` scheme (that scheme classifies *task
   outcome* failures, not harness/infra failures — see Objective 1 below), but note this
   explicitly in your deliverable rather than silently omitting them without comment.

Use whichever of source (1) and (2) actually contains genuine task-level failures
(`exception_info: null`, `reward: 0.0`) — both should, per T407's own closing numbers (Arm A pass
means `[0.36, 0.28, 0.28]`, i.e. most trials across all 4 runs did not pass).

## Objective

1. **Read `docs/artifacts/failure-taxonomy-v1.md` in full**, especially §3 (axis definitions) and
   §7 (reuse notes already written for this task). The three axes (`cause`, `behavior`,
   `mechanism`) are defined in terms of observable document/output shape, not golden-suite-
   specific mechanics, and are expected to transfer — but this is a hypothesis to verify against
   real Harbor failures, not an assumption to take on faith.
2. **Extract real Terminal-Bench task-level failures** from the source data above: for each arm/
   pass, identify trials where `exception_info` is `null` (a genuine verifier outcome, not an
   infra error) and `verifier_result.rewards.reward == 0.0`. For each such failing trial, read
   enough of the trial's actual output (agent transcript, verifier logs — whatever is present in
   the trial directory) to determine *why* it failed in the same sense golden-suite failures were
   classified: root cause (`cause`), observable symptom (`behavior`), structural mechanism
   (`mechanism`).
3. **Classify each real Terminal-Bench failure along the existing three axes.** For each failure,
   decide: does it fit one of the 9 existing enumerated axis values (§3's tables), or does it
   genuinely require a new value? Per §7's own framing, this decision is explicitly this task's
   call — extend an axis's value set with a new row (following the existing tables' format: value
   name, definition, real cases) rather than forcing a bad fit, and do **not** invent a fourth axis
   unless a real failure genuinely cannot be described by `cause`/`behavior`/`mechanism` at all
   (unlikely, but the possibility is explicitly not foreclosed by §7).
4. **Do not classify infrastructure/harness failures** (bind-mount stranding, host exhaustion,
   `AgentTimeoutError` at the harness level, `RewardFileNotFoundError`) under this scheme — those
   are not task-outcome failures and classifying them would conflate two different kinds of
   failure the golden-suite scheme was never designed to cover. Note their existence and exclusion
   explicitly (see source (3) above) rather than silently dropping them.
5. **Deliverable format** — extend, do not replace, the existing artifacts:
   - Update `docs/artifacts/failure-taxonomy-v1.md`: bump to a new version if you materially
     change axis definitions/values (`failure-taxonomy-v2.md`, cross-linked from v1 as superseded)
     or add a clearly-marked new section if the existing axes suffice unchanged with only new
     value rows added — your call, document which you chose and why. Either way, the existing
     golden-suite classification content (§§1-6 of v1) must remain intact and correct; this is
     additive work, not a rewrite.
   - Add Terminal-Bench trajectory classifications under `docs/benchmarks/failures/` (or a new
     `docs/benchmarks/failures/terminal-bench/` subdirectory — your call, keep golden-suite and
     Terminal-Bench entries distinguishable at a glance either way), one file per distinct failure
     pattern or per representative failing task (your call on granularity — with ~50-100+ failing
     trials across 4 runs, per-trial files would be noise; classify by distinct failure *pattern*,
     citing which real task names exhibit each pattern).
   - Update `docs/benchmarks/failures/README.md`'s index to reflect both sources.
6. **Prove "one taxonomy, two sources" concretely**: your final deliverable must make it possible
   to look at the combined index and see golden-suite and Terminal-Bench failures sharing the same
   `cause`/`behavior`/`mechanism` value space (with genuinely new values added where warranted,
   not where convenient).

## Held-out isolation — does not apply here, confirm explicitly

Terminal-Bench trajectories are not `tests/golden/held-out/` content and are not subject to
`tests/functional/test_golden_held_out_isolation.py`. Run that test suite anyway after your
changes (it should be unaffected — zero diff to `tests/golden/**`) to confirm you have not
accidentally touched anything under that guard's scope; `tests/golden/**` and
`scripts/scorecard.py` remain protected/read-only per T416 regardless of this task's own scope.

## Inputs

- `docs/artifacts/failure-taxonomy-v1.md` (T415) — the scheme to extend.
- `docs/benchmarks/failures/*.md` + `README.md` (T415) — the existing per-case classification
  files and index to extend, not replace.
- Source trajectory data — see "Source data" section above.
- `docs/benchmarks/tb-delta-v6.12.0.md` (T407) — aggregate numbers and run history, useful context
  for which tasks/passes are worth reading in detail.
- `docs/benchmarks/tb-subset.json` (T418) — the frozen 25-task subset and each task's declared
  `category`, useful for grouping failure patterns.

## Expected outputs

- Extended/versioned taxonomy document (see Objective 5 for the versioning decision).
- New classification files under `docs/benchmarks/failures/` (or a subdirectory) for real
  Terminal-Bench failure patterns, each citing real task names and which run/pass they came from.
- Updated `docs/benchmarks/failures/README.md` index covering both sources.
- A short explicit note on infrastructure-failure exclusion (Objective 4).

## Acceptance criteria

1. At least one real, genuine (non-infra) Terminal-Bench task-level failure from the source data
   is classified along all three axes (`cause`, `behavior`, `mechanism`), citing the real task
   name and run/pass it came from.
2. Every classified Terminal-Bench failure either maps to an existing axis value (cite which) or
   is accompanied by a documented new value added to the relevant axis's table, following the
   existing tables' format (value, definition, real cases).
3. The golden-suite content already in `docs/artifacts/failure-taxonomy-v1.md` and
   `docs/benchmarks/failures/*.md` is unchanged in substance (only additive edits — cross-links,
   version bump, new sections) — verify with `git diff` before finishing that no existing
   classification row's axis values were altered.
4. Infrastructure/harness failures are explicitly noted as out of scope for this classification
   pass, not silently omitted.
5. `python3 tests/run.py` passes with no new failures.
6. `tests/functional/test_golden_held_out_isolation.py` still passes, zero diff to
   `tests/golden/**`/`scripts/scorecard.py`.
7. No new Terminal-Bench trial, Docker container run, or paid API call was made in the course of
   this task (this is a hard constraint, not just a preference — verify and state this explicitly
   in your completion report).

## Git Workflow

Refactor/tooling-adjacent classification work — treat as `docs`+`tooling` combined; since this
touches both documentation artifacts and potentially small analysis scripts, follow the stricter
rule: create a feature branch from `develop` (`feature/T409-tb-harbor-taxonomy`), open an MR, do
not commit directly to `develop`. If you write any throwaway analysis scripts to parse
`result.json` files, either keep them out of the commit (scratch-only) or, if genuinely reusable,
commit them under `scripts/` with a clear docstring — your call, but do not leave the repo dirty
with untracked debris at completion.

## Blocker Protocol

Report blockers with `type` (`technical` | `dependency` | `unclear_requirements` | `external`) and
`severity` (`critical` | `major` | `minor`). If the remote host (`10.10.160.11`) is unreachable
for reading the Design A trajectory data, that is a `type: external`, `severity: major` blocker —
report it rather than substituting synthetic data or skipping source (2) silently; the original
k=3 local run (source 1) alone may still be sufficient to satisfy the acceptance criteria if it
contains genuine task-level failures, but do not silently narrow scope without flagging it.
