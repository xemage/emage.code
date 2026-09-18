# Task T502 — Kill switch: one documented command halts the loop; a halted loop cannot
self-resume (`plan-035` nominal T466)

**Owner:** devops-engineer
**Status:** done
**Closure note (2026-09-18):** all 7 acceptance criteria independently re-verified by the
top-level session before this closure (not accepted on the implementer's self-report alone),
including the cross-process-boundary persistence requirement. See
`docs/tasks/completed-tasks.md`'s `T502` row for the full closure record.
**Priority:** P0
**Depends on:** none (this task is deliberately independent of T501 and of every other Phase 6
task — see `plan-055` §4's sequencing note)
**Created:** 2026-09-18
**Based on:** `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's
`T466-equiv` row ("this is a local implementation-and-test task with no live-dispatch
requirement... Unchanged from `plan-035`") and §5's artifact-flow diagram (kill switch shown as
independent of the rest of the pipeline); `docs/artifacts/phase6-sia-readiness-audit-v1.md` §4
(the corrected Phase 6 dependency graph this task's design must not silently violate); `plan-035`
§2.4's own literal acceptance criterion for this task: "Kill switch verified by test."

**Do not treat `plan-035` §2.4 Phase 6's own introductory prose ("`implementation/sia/`,
`sia-executor.py`... already exist") as a scoping instruction for this task.** This task has no
dependency on that subsystem, on T501, or on any other not-yet-built Phase 6 component.

## Why this task exists, and why it is scoped narrowly right now

Phase 6's eventual closed loop (a future weakness-miner, a future diff-proposal generator, a
future validation/promotion step) does not exist yet — none of it is built. This task cannot,
therefore, wire a halt check into a real loop-runner today, because there is no loop-runner to
wire into. **This task's real, buildable deliverable is the kill-switch mechanism itself: a
generic, reusable primitive that any future Phase 6 loop-runner will import and check before
acting, built and proven correct in isolation, independent of code that doesn't exist yet.**
State this explicitly wherever you document the mechanism — this is a deliberate scoping decision
(mirroring T501's own disclosed scoping decision in its sibling brief), not an oversight that
skips "the hard part." The hard part (an actual closed loop to halt) is out of scope for every
Phase 6 task dispatched so far, including this one.

## Objective

Build a documented, real, testable kill-switch mechanism with two required properties, both
proven by a real committed test, not merely asserted:

1. **Halt is detectable.** A documented command (a CLI invocation) sets a halt signal. A
   corresponding real Python function — importable by any future code, with no dependency on
   anything this task doesn't itself build — reports whether the system is currently halted. The
   signal must be durable (e.g. file-based or another persistent, process-independent mechanism)
   — not held only in the memory of whatever process set it, since a future loop-runner checking
   the signal will typically run as a separate process/invocation from whatever set the halt.
2. **A halted state cannot self-resume.** Once set, nothing in this task's own deliverable code
   ever clears the halt signal as a side effect of normal operation — specifically, the "check
   whether halted" function must never itself clear or weaken the signal, no matter how many times
   or in what sequence it is called, and there must be no automatic expiry (time-based or
   otherwise). Decide, and explicitly document, whether a resume path exists at all: either (a) no
   programmatic resume command exists in this deliverable at all (a human clears the signal by a
   documented manual step, e.g. deleting a specific file, outside any tool this task builds), or
   (b) a separate, explicitly-named resume command exists but requires a distinct, deliberate
   human invocation, is never called by the halt-check path, and is documented as a conscious
   design choice with its own justification. Either is acceptable; silently building a
   resume/clear command without discussing this trade-off is not.

## Design freedom, and what must be fixed

Your call, document whichever you choose:
- Exact module location (a reasonable default: `implementation/runtime/`, mirroring T458's
  `golden_harness/` precedent of a small, focused, importable module — but a location under
  `implementation/scripts/` for the CLI entry point plus a thin importable library module is
  equally reasonable if you prefer separating the CLI from the library).
- Exact signal storage mechanism (a sentinel file with a documented path is a reasonable default;
  any other durable, process-independent mechanism is acceptable if you can justify it and test
  it without new infrastructure this repo doesn't already have).
- Exact CLI shape (subcommands, flags) — but it must be a single, clearly documented command a
  human can run, per `plan-035`'s own literal wording ("one documented command halts the loop").
- Whether a resume path exists at all, per point 2 above — but the choice must be explicit and
  justified in your documentation, not silent.

Fixed, not your call: the halt-check function must be a real, standalone, generically-importable
Python function with no dependency on `implementation/sia/`, T501's new module, or any other
not-yet-built or invalidated-subsystem code. It must work correctly with nothing else in Phase 6
built yet — prove this by writing its test entirely in terms of the kill-switch mechanism itself
(set halt, check halt, attempt to "resume" via every code path this deliverable exposes, confirm
none of them clear it except whichever explicit path you chose in point 2, if any).

## A short documentation artifact

Produce a short artifact documenting the command, its exact invocation, where the halt signal
lives, and the point-2 resume-path decision and its justification. A reasonable default location
is `docs/artifacts/phase6-kill-switch-v1.md`, mirroring this repo's existing `<slug>-v1.md`
artifact-versioning convention — your call on the exact filename if you have a better one, but it
must exist somewhere real and be referenced from your completion report.

## Inputs

- `docs/artifacts/protected-paths-v1.md` (full document) — a useful style precedent for how this
  repo documents a standing operational control: a short "why this exists," an explicit statement
  of what the control does and does not do, and a scope boundary section. Not a functional
  dependency of this task.
- `implementation/runtime/golden_harness/__init__.py` and any one sibling module (e.g.
  `policy.py`) — style precedent only, for how small, focused, tested modules are structured in
  this part of the codebase.

## Constraints

- Token budget: keep this task well under 40k tokens — `plan-035` itself estimated this task
  "small," and `plan-055` did not revise that estimate.
- File ownership: this task may only create/modify files under `implementation/runtime/**` and/or
  `implementation/scripts/**` (your call per the Design freedom section above), `tests/**` (its
  own new test file), `docs/artifacts/**` (its own new documentation artifact), plus its own
  `docs/tasks/task-T502.md` status field.
- Protected paths — do not touch, no exceptions: `tests/golden/**`, `scripts/scorecard.py`,
  `.mcp.json`, `docs/benchmarks/tb-subset.*`. Do not touch or branch from the
  `feature/T475-codex-platform-integration` branch — it is unrelated, in-flight work.
- Do not build, stub, or reference any part of a future loop-runner, weakness miner, or
  diff-proposal generator. This task's own deliverable must stand alone and be testable with
  nothing else from Phase 6 present.
- No self-merge: work only in this task's own dedicated worktree/branch
  (`agent/devops-engineer/T502`, already created off `develop`). Commit, push, open a merge
  request, and stop. Do not merge it.

## Expected outputs

1. A real, tested kill-switch module/CLI under `implementation/**` (exact location your call, per
   above).
2. A new test file proving both required properties from the Objective section, using only this
   task's own deliverable code.
3. `docs/artifacts/phase6-kill-switch-v1.md` (or your chosen equivalent filename) documenting the
   command, the signal mechanism, and the resume-path decision.
4. A short completion report (in your final message back to the orchestrator) stating the exact
   paths chosen and a one-line summary of the resume-path decision and why.

## Acceptance criteria

- [ ] A single documented command exists that halts the (future) loop.
- [ ] A real, standalone, importable Python function reports the current halt state correctly,
      with no dependency on any code outside this task's own deliverable.
- [ ] The halt signal persists across process boundaries (e.g. surviving a fresh Python process
      invocation checking it after the command that set it has already exited) — proven by the
      test, not asserted.
- [ ] A real, committed test proves: (a) after invoking the halt command, the check function
      reports halted; (b) calling the check function repeatedly, or simulating a future
      loop-runner's normal operation against this deliverable's own exposed API, never clears the
      halt signal; (c) whichever resume-path decision was made in the Objective section's point 2
      is itself exercised and proven correct (either "no resume path exists in this code" or "the
      explicit resume command works and only it clears the signal").
- [ ] The resume-path decision (point 2) is stated explicitly and justified in the documentation
      artifact, not left implicit.
- [ ] No file outside this task's declared file-ownership boundary is modified. Zero hits on any
      protected path.
- [ ] `python3 tests/run.py` passes with no new failures relative to the pre-task baseline on
      `develop`.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). If you find any existing partial "kill switch" or
"halt"-style mechanism already in this repo that this brief's own research missed, report it as a
`dependency` blocker before building a duplicate — do not silently proceed on the assumption
nothing exists if you find evidence otherwise.
