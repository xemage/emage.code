# Task T458 — Live-execution harness for the golden suite (unblocks T456)

**ID:** T458
**Owner:** devops-engineer (matches this repo's own precedent for harness-building work — T417/
T418/T419/T407/T408/T409, the Terminal-Bench/Harbor live-trial infrastructure, were all built by
`devops-engineer`, not `evaluation-agent`; confirm this agent's real tool grant before dispatch
per this repo's own now-repeated tool-grant-check discipline, same as T415/T418/T455)
**Status:** pending — recorded and scoped this session, **not dispatched this session** (the memory
layer itself, T450-T454, is already usable without this task; this is infrastructure for a formal
gate, not on any active critical path — see Priority note below)
**Priority:** P1 (blocks Phase 5's formal ship decision and Gate G3's closure; does **not** block
`@context-retriever`/the memory layer from being genuinely usable today — those are already done
and independently verified)
**Depends on:** None structurally (T454's `@context-retriever` agent it will exercise is already
done; the golden suite's `expect.py`/case format it reuses is already frozen/done from Phase 1).
**Blocks:** T456 (cannot be genuinely re-attempted without this task's output)
**Created:** 2026-09-09
**Completed:** —
**Based on:** `docs/tasks/task-T456.md` (the blocker this task exists to resolve — read that first,
it contains the full, cited evidence for why this infrastructure does not already exist);
`docs/artifacts/golden-suite-format-v1.md` (the case format/`expect.py` contract this task must
reuse unmodified — `brief.md`/`fixture/`/`expect.py`, §2.2's own explicit design note that a case's
`brief.md` "may later be reused as the literal input to a live agent run in a *separate* system,"
which is exactly this task); `docs/benchmarks/baseline-v6.12.0.md` (T414's frozen baseline this
task's eventual measurement compares against); `docs/artifacts/context-retriever-v1.md` (the
`ContextRetriever.query()` surface the treatment arm wires in); `docs/tasks/task-T417.md`/
`task-T418.md`/`task-T419.md` and their closure records in `docs/tasks/completed-tasks.md` (the
closest existing precedent in this repo for building a live-trial execution harness — Terminal-
Bench/Harbor, real Docker-based trials, config-diff verification, budget guards — reuse that
precedent's *shape and rigor*, not its Docker/Harbor-specific mechanics, which are a different
domain).

## Why this is scoped as real infrastructure, not a quick task

T456 (`docs/tasks/task-T456.md`) found that the golden suite has **no live-agent execution path by
deliberate Phase 1 design** — `expect.py` is a pure, deterministic function of on-disk fixture
bytes, and `scripts/scorecard.py` never invokes a live model completion (`golden-suite-format-v1.md`
§2.2/§4.2, `scorecard.py`'s own "no subprocess, no shelling out"). Measuring "does retrieval improve
the golden suite" for real requires something that does not exist anywhere in this repo today: a
harness that actually runs a live agent session per case, with and without `@context-retriever`
wired into its tool availability, produces a real candidate output, and checks that candidate
against the case's existing `expect.py`. This is comparable in shape — not mechanics — to what
Terminal-Bench's Layer 2 harness (T417-T419) needed: real trial execution, real config-diff/
determinism verification, a two-arm comparison design, and a pre-registered decision rule to avoid
post-hoc rationalization (mirroring T407's own frozen decision-rule discipline). **Do not treat this
as a "medium" task** — if, once scoped in detail, it turns out to need the kind of multi-task
re-sequencing T407 itself needed (its own "Design A" re-dispatch after the first design proved
insufficient), that is an expected, not a failed, outcome — report it plainly rather than force a
single task to absorb whatever scope is actually required.

## Objective

Build a repeatable, two-arm live-execution harness for the golden suite's 20 existing cases (or a
disclosed, justified subset — see Constraints) that:

1. **Reuses each case's existing `brief.md` as the literal live-agent prompt input** — per
   `golden-suite-format-v1.md` §2.2's own explicit design note anticipating exactly this use, not a
   new prompt-authoring effort.
2. **Runs two arms per case**: a control arm (agent session without `@context-retriever` available)
   and a treatment arm (agent session with `@context-retriever` available, wired in per
   `context-retriever-v1.md` §1's real interface — the actual read-only agent, not a stub).
3. **Produces a real candidate output** (whatever files/state the live session actually writes, in
   an isolated workspace per trial — mirroring Terminal-Bench's own per-trial container isolation
   discipline, adapted to whatever isolation mechanism fits a live Claude Code session rather than a
   Docker container, since this is not a Terminal-Bench-style sandboxed task execution).
4. **Checks that candidate output against the case's existing, unmodified `expect.py`** — reusing
   the exact same `check(case_dir)` contract `scripts/scorecard.py` already uses (§4.1), just pointed
   at the live-run's candidate output directory instead of the checked-in `fixture/`. Do not modify
   `expect.py` itself or any file under `tests/golden/**` to make this work — if a case's `expect.py`
   genuinely cannot be pointed at an alternate directory without modification, that is a `type:
   technical` blocker to report, not license to edit a protected path.
5. **Produces a scored comparison** (control pass-rate vs. treatment pass-rate) with a
   **pre-registered definition of "measurably improve"** stated *before* any run, mirroring T407's
   own pre-committed decision-rule discipline (to avoid exactly the "ship-gate applied loosely"
   risk `plan-038`'s own risk table already names for T456).

**This task builds the harness and, if scope allows within its own budget, may run it once as a
smoke test — it does not itself have to produce T456's final ship/no-ship verdict.** That
measurement is T456's own job, re-attempted once this harness exists. State clearly in your
completion report whether a full 20-case two-arm run was performed as part of this task or is left
for T456's own re-dispatch — either is an acceptable outcome, but it must be stated, not implied.

## Constraints

- **No paid or recurring-cost API calls.** Live agent sessions run through this repo's own existing
  Claude Code / agent-dispatch mechanism (the same mechanism every other task in this project uses),
  not a separate metered API. If your design genuinely requires a metered API call of any kind
  (e.g. a hosted model endpoint distinct from the interactive session mechanism already in use),
  that is a `type: external`, `severity: critical` blocker requiring explicit user cost-authorization
  before any such call, mirroring T407's own authorization gate — do not proceed on the assumption
  it is pre-approved.
- **Do not touch `.mcp.json`**, anywhere, for any reason. Do not touch the main checkout.
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`**
  — reuse `expect.py`'s contract by importing/calling it exactly as `scripts/scorecard.py` already
  does, never by editing it. If you find you must add a small, additive, non-invasive extension
  point (e.g. `expect.py`'s `check()` accepting an optional alternate directory instead of always
  assuming `fixture/`) — that is itself a change to a protected path and requires an explicit,
  disclosed exception request to the orchestrator before any such edit, per
  `docs/artifacts/protected-paths-v1.md`'s own documented exception process. Do not silently work
  around this by copying/forking `expect.py`'s logic instead — report the need for an exception
  instead.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start any Phase 3 work.**
- **Confirm your own tool grant before starting** — this repo has hit the "assigned agent lacks
  Bash/write access" gap four times already this project (T418's original `evaluation-agent`
  misassignment; T410/T420/T451's Bash-less `solution-architect`; T415/T418's reassignment; T455's
  `evaluation-agent` reassignment) — check `implementation/knowledge/agents/<your-owner>.md`
  directly before beginning, and report immediately as a `type: technical` blocker if it is
  insufficient, rather than discovering it mid-task.
- **Work in your own worktree/branch**, created from `develop`. Commit as you go; run the full test
  suite (`python3 tests/run.py`) and confirm no regressions before reporting completion. **Do not
  self-merge** — push and open a merge request, then stop.
- Follow this repo's coding standards (max 50-line functions, max 4 parameters, early returns) and
  Conventional Commits.

## Expected Outputs

1. Harness code (natural location `scripts/` or a new `implementation/runtime/` module — state your
   actual choice) implementing the two-arm live-run/check pipeline described in the Objective.
2. A design/methodology artifact (e.g. `docs/artifacts/golden-live-harness-v1.md`) documenting: how
   trial isolation works, how the control/treatment arms are actually wired (or not) to
   `@context-retriever`, the pre-registered "measurably improve" threshold, and any scope reduction
   (subset of cases, single smoke-test run vs. full comparison) with honest justification.
3. If a full or partial live run was performed as part of this task: real results, honestly reported
   — including if the harness itself reveals new problems (e.g. non-determinism in live sessions that
   complicates comparison, cases whose `expect.py` cannot cleanly point at an alternate directory).
4. Tests proving the harness's own non-agent logic (config/trial-isolation setup, result-scoring,
   comparison-threshold logic) is correct — wired into `python3 tests/run.py`'s default tier where
   feasible; live-agent-invoking tests should be opt-in/gated, mirroring this repo's own established
   `EMAGE_*`-env-var-gated pattern for other optional/expensive test tiers.

## Acceptance Criteria

1. A genuine, reusable two-arm (control/treatment) live-execution mechanism exists for at least a
   disclosed subset of the golden suite's cases, reusing each case's real `brief.md` as input and
   each case's real, unmodified `expect.py` as the pass/fail check.
2. `tests/golden/**` and `scripts/scorecard.py` are untouched; if any exception was genuinely
   required, it was disclosed and explicitly approved before the edit, not applied unilaterally.
3. A "measurably improve" threshold is stated in writing *before* any comparison run is reported as
   a result, not derived after seeing the numbers.
4. No paid/recurring-cost API call was made without explicit prior authorization.
5. `python3 tests/run.py` passes with no regressions.
6. Your completion report states plainly whether T456's actual ship/no-ship measurement was
   performed as part of this task or is left for T456's own re-dispatch, and if performed, reports
   the real numbers regardless of whether they are favorable.
7. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol. Max 2 retries
before escalating to the orchestrator. Specific cases already anticipated:

- If this task's true scope, once you've investigated the live-agent-dispatch mechanics in detail,
  turns out to require re-sequencing into multiple tasks (mirroring T407's own "Design A"
  re-dispatch after its first design proved insufficient): report `type: technical`,
  `severity: major`, with your own proposed re-scoping — this is an expected possible outcome for a
  task of this shape, not a failure.
- If `expect.py`'s existing contract genuinely cannot be pointed at a live-run's candidate output
  without a protected-path edit: report `type: unclear_requirements`, `severity: major`, with the
  smallest possible proposed exception, per the Constraints section above — do not silently fork or
  copy the logic instead.
- If live-agent-session non-determinism makes a clean single-run comparison unreliable: this is a
  real, disclosable finding, not a blocker to route around — report it and propose a design
  (e.g. multiple trials per case per arm, similar to T407's own `k`-run design) rather than silently
  reporting a single noisy run as if it were conclusive.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
