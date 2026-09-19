# Task T443 — Extend the scorecard to record model tier and outcome per golden case

**ID:** T443
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T440 (done)
**Created:** 2026-09-12
**Completed:** 2026-09-12
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (Phase 4 task table, T443 row,
quoted below verbatim, and the Phase 4 "Acceptance criteria" block immediately below that table);
`docs/plans/plan-043-phase4-task-tier-routing-detailed-planning.md` Finding 2 (the protected-path
exception requirement and the `evaluation-agent` → `devops-engineer` owner-reassignment
recommendation this task's dispatch carries out); `docs/artifacts/protected-paths-v1.md` §5 (the
exception process this task invokes); `docs/artifacts/task-tier-schema-v1.md` (T440's tier
vocabulary this task's new fields record); `implementation/knowledge/instructions/
mechanical-tier-escalation-policy.md` (T442's outcome-recording requirement this task's
`model_outcome` field partially answers)

> **Disclosed process gap, stated plainly rather than silently corrected:** this brief is being
> authored and committed **at closure time**, after the implementer's own commit (`66031b0`) landed
> on `agent/devops-engineer/T443`, not before dispatch as `T440`/`T441`/`T442` each had their own
> `task-T44N.md` committed ahead of or alongside the implementer's work. The implementer's own MR
> !287 description states the protected-path exception was "explicitly invoked and satisfied by
> `docs/tasks/task-T443.md`" — that claim was not true in the repository's own audit trail until
> this closure commit: no such file existed anywhere in this repo's git history (checked via `git
> log --all --oneline -- docs/tasks/task-T443.md` and `git log --all --oneline | grep -i T443`,
> both empty prior to this commit) before now. The dispatching orchestrator evidently gave the
> implementer brief-equivalent content directly (the implementer's delivered scope, disclosed
> choices, and test plan track plan-043 Finding 2's recommendations closely enough — protected-path
> exception invoked correctly, owner reassigned to `devops-engineer` exactly as recommended, 31-id
> stable-list sweep performed — to have been worked from a real brief), but skipped the step of
> committing that brief to `docs/tasks/task-T443.md` in the repo itself, which `protected-paths-
> v1.md` §5 rule 2 requires ("Always a named, authorized task... An explicit task brief
> (`docs/tasks/task-<NNN>.md`) that names this exception explicitly"). This closure commit corrects
> the gap by authoring the brief now, retroactively, matching what the implementer's own MR
> description and test plan show they were actually working from — not inventing new scope after
> the fact. This is disclosed here, not fixed silently, per this repo's own standing practice of
> naming process deviations explicitly (mirrors `T436`'s disclosed self-merge deviation and `T440`'s
> disclosed ledger-sequencing defect).

## Objective

Quoted verbatim from `plan-035` §2.4's own T443 row:

> "Extend the scorecard to record model tier and outcome per golden case, enabling a real
> measurement of the cost/quality frontier."

Per `plan-043` Finding 2, two preconditions this task's dispatch must satisfy that the literal
`plan-035` wording does not itself resolve:

1. **Protected-path exception.** `scripts/scorecard.py` is a declared protected/write-excluded
   path (`docs/artifacts/protected-paths-v1.md`, T416). This task requires, and this brief grants,
   the `protected-paths-v1.md` §5 exception to edit it — additive schema fields only, not a
   rewrite of any existing logic or output.
2. **Owner reassignment.** `plan-035`'s nominal owner, `evaluation-agent`, has tool grant `[read,
   search, web]` — no `edit`, no `execute` — and cannot write the code this task requires under any
   reading. Reassigned to `devops-engineer` (`[read, edit, write, execute, web, mcp__gitlab,
   mcp__fetch]`), per plan-043 Finding 2's own named recommendation.

Concrete scope: add two new, nullable, optional keys to each per-case result dict emitted by
`scripts/scorecard.py`'s `run_case()` — `model_tier` (values: `"mechanical"` / `"standard"` /
`"judgment"` / `null`, per `task-tier-schema-v1.md`) and `model_outcome` (values: `"pass"` /
`"fail"` / `"escalated"` / `null`, per `mechanical-tier-escalation-policy.md`'s recording
requirement). Both are schema/plumbing only — no live producer exists yet to populate them with
real data, since no live-model-tier execution data source exists anywhere in this repository
today (T456/T458 — a live-execution harness — remain blocked/pending). Document this null-today
state explicitly in the module docstring so a future reader does not mistake the null values for a
bug.

## Hard scope boundary

This task does **not**:
- Build a live producer for either field. That is separately scoped, future work, gated on a
  live-execution harness (`T458`, currently `pending`) and `T456` (currently `blocked`) actually
  running.
- Add a `cost` field or any cost-per-case measurement. `plan-035`'s Phase 4 acceptance criteria
  include "Scorecard reports cost per case alongside pass/fail" as a **separate** bullet from the
  tier/outcome recording this task's own row describes — this task's literal row text does not
  mention cost, and no cost field is added by this task. See "Phase 4 acceptance-criteria status"
  below for why this matters at closure.
- Regenerate or commit updated `docs/benchmarks/scorecard-v6.12.0.{json,md}` artifacts. Optional;
  the implementer ran the script for verification only and restored the committed files.
- Touch `tests/golden/**`, `.mcp.json`, or `feature/T475-codex-platform-integration`.

## Inputs
- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (Phase 4 task table T443 row + acceptance
  criteria block)
- `docs/plans/plan-043-phase4-task-tier-routing-detailed-planning.md` Finding 2
- `docs/artifacts/protected-paths-v1.md` §5 (exception process)
- `docs/artifacts/task-tier-schema-v1.md` (T440)
- `implementation/knowledge/instructions/model-routing-policy.md` (T441)
- `implementation/knowledge/instructions/mechanical-tier-escalation-policy.md` (T442)
- `scripts/scorecard.py` (the file being extended)

## Expected outputs
- `scripts/scorecard.py`: two new nullable keys in `run_case()`'s result dict, plus a docstring
  subsection explaining why they are null today and citing this task.
- A merge request from `agent/devops-engineer/T443` to `develop`, referencing T443, left unmerged.

## Constraints
- Additive only — zero changes to any existing field, existing case ordering, or existing
  `content`/`summary`/`by_location` computation for any case.
- Byte-level regression proof required: every pre-existing field for every case must be provably
  unchanged (only `run_metadata.generated_at` is expected to differ between runs, per the script's
  own pre-existing documented purity contract).
- `tests/functional/test_protected_paths_declared.py` and `tests/functional/
  test_golden_held_out_isolation.py` must both still pass.
- Self-referential ledger-defect sweep: grep new content against the live, freshly re-derived
  31-id `stable` component list, zero hits expected.
- Do not touch `docs/tasks/active-tasks.md`/`completed-tasks.md` — ledger transitions are
  orchestrator-only.
- Do not run `glab mr merge`. Leave the MR open for the top-level session.

## Acceptance criteria
1. `run_case()`'s result dict carries `model_tier` and `model_outcome`, both `None`/`null` for
   every case today, with allowed non-null value sets documented in the module docstring.
2. `git diff --stat origin/develop` shows only `scripts/scorecard.py`, additive only.
3. A fresh run of `scorecard.py` on the modified tree, diffed against a fresh run on `origin/
   develop`, shows only the two new null keys added per case (plus the expected `generated_at`
   timestamp difference) — no other field changes.
4. `python3 -m pytest tests/functional/test_protected_paths_declared.py tests/functional/
   test_golden_held_out_isolation.py -q` passes with no regressions.
5. `python3 tests/run.py` passes with the same test/skip counts as the pre-change baseline (no
   new failures, no count change, since this is purely additive).
6. Self-referential ledger-defect sweep against the live 31-id stable list: zero hits in the new
   content.
7. MR opened from `agent/devops-engineer/T443` to `develop`, referencing T443, left unmerged.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

**Delivered** (implementer commit `66031b0` on `agent/devops-engineer/T443`, MR !287): exactly the
34-line additive diff described above — two new dict keys (`"model_tier": None`,
`"model_outcome": None`) in `run_case()`'s result literal, and a new module-docstring subsection
explaining the null-today state, citing `task-tier-schema-v1.md`, `mechanical-tier-escalation-
policy.md`, and (correctly, after a self-caught citation fix) `T456`'s real `blocked` status in
`active-tasks.md` (the implementer's own report flagged that its brief context had loosely
suggested T456 lived in `completed-tasks.md`, verified instead and cited accurately as `blocked`).
No other file touched.

**Orchestrator independent verification before this closure** (not accepted on the implementer's
self-report alone, per this session's standing discipline used for T441/T442):
- Checked out `origin/agent/devops-engineer/T443` fresh in its own worktree, confirmed HEAD
  (`66031b0`) identical to origin, zero drift.
- `git diff --stat origin/develop origin/agent/devops-engineer/T443` → exactly `scripts/
  scorecard.py`, 34 insertions, 0 deletions. Read the full diff line-by-line: confirmed it is
  exactly the two new dict keys plus a 30-line docstring addition, nothing else.
- Swept for pollution in every protected/adjacent path: zero hits on `tests/golden/**`,
  `docs/benchmarks/tb-subset.*`, `.mcp.json`, `docs/tasks/active-tasks.md`/`completed-tasks.md`
  (ledger closure genuinely not yet on this branch, confirming the implementer's own disclosure),
  and no overlap with `feature/T475-codex-platform-integration` (a local-only, unpushed branch on
  the top-level session's own checkout, unrelated to this branch's sole touched file).
- Ran `scripts/scorecard.py` fresh on this branch's tree myself (not trusting the implementer's own
  before/after diff claim): resulting `docs/benchmarks/scorecard-v6.12.0.json` diff showed exactly
  40 new lines (`model_outcome: null` + `model_tier: null` × 20 cases) plus the expected
  `generated_at` timestamp change (41 insertions/1 deletion total) — every other field, and the
  `summary`/`by_location` sections, byte-identical to the pre-existing committed output (which was
  itself unchanged between `develop` and this branch prior to running the script, confirmed by the
  diff-stat check above). Restored the run artifacts afterward via `git checkout --` to leave the
  worktree clean.
- Ran `python3 -m pytest tests/functional/test_protected_paths_declared.py tests/functional/
  test_golden_held_out_isolation.py -q` fresh → 18 passed (10 + 8, matching the claim). Read both
  files' actual assertions in full: `test_protected_paths_declared.py` only checks that
  `scripts/scorecard.py` exists on disk and that agent files carry the policy-doc pointer — it does
  not and is not designed to enforce the freeze itself (its own module docstring states this
  explicitly), so it is orthogonal to whether this task's edit was in-scope, not a weakened guard.
  `test_golden_held_out_isolation.py` explicitly allowlists `scripts/scorecard.py` from both of its
  checks (`EXEMPT_RELATIVE_PATHS`, with a docstring reason: "running both `open/` and `held-out/`
  cases is its whole job") — meaning this specific guard structurally cannot catch a held-out-case
  leak inside `scorecard.py` itself, which is why the manual id-sweep below matters independently.
- Manually swept the new diff's added lines against the freshly re-derived, real 31-id `stable`
  component list (`implementation/scripts/check-maturity.py --verbose`, re-extracted this session,
  not copied from a prior report: 20 agents + 4 instructions + 7 skills) — zero hits.
- Ran `python3 tests/run.py` fresh → 514 tests, `OK`, `skipped=24` — unchanged from baseline,
  matching the claim exactly.
- Confirmed `T456`'s citation independently: `active-tasks.md` line 5 on this branch shows `T456 |
  Downstream measurement (ship gate) | evaluation-agent | blocked | ...` — genuinely `blocked`, not
  `done`/`completed`, and does not appear as its own row in `completed-tasks.md`. The implementer's
  self-corrected citation is accurate.
- Real GitLab CI independently polled to completion on the actual pushed SHA (`66031b0`, pipeline
  `2842771236`) — 5/5 jobs green (`sync-no-diff`, `validation-super-gate`, `verify-knowledge-drift`,
  `unit-tests`, `markdown-links`), not assumed.

**Phase 4 acceptance-criteria status — does NOT close cleanly, stated plainly rather than claiming
a false milestone.** All four of `plan-035` §2.4's Phase 4 acceptance-criteria bullets were
checked directly against what T440-T443 actually deliver, not assumed satisfied because all four
constituent tasks are now `done`:

1. *"A `mechanical`-tier golden case completes on the economy model at parity with the baseline"*
   — **not satisfied.** No live model execution of any golden case exists anywhere in this
   codebase today; `model_tier`/`model_outcome` are hardcoded `None` for every case by this task's
   own explicit design, and the live-execution harness that would make this measurable (`T458`) is
   `pending`, gating the blocked `T456`.
2. *"Marking a `judgment` task as `mechanical` produces escalation, not silent degradation"* —
   **not satisfied as a demonstrated behavior.** `T442` states this as written policy only;
   its own "Out of scope" section explicitly excludes "dispatch-time enforcement... a live
   recording mechanism... live automatic defect-opening." No dispatch-time mechanism exists that
   actually performs an escalation when a `mechanical`-tier task fails.
3. *"Scorecard reports cost per case alongside pass/fail"* — **not satisfied.** Verified directly:
   there is no `cost` key, nor any cost-related field, anywhere in `scripts/scorecard.py`'s
   `run_case()` result dict, before or after this task's diff (`grep -n '"cost"' scripts/
   scorecard.py` → zero hits). `model_tier`/`model_outcome` are a different, narrower thing than
   cost, and both are null. This bullet is unmet by any of T440-T443.
4. *"No unstable component is reachable at `mechanical` tier"* — **partially addressed, not
   mechanically verified.** `T440`'s eligibility rule (stable component + declared rails +
   test-backed acceptance criteria) states this as a gating requirement in the schema document,
   but no automated check in this repo currently enforces or verifies it against any real task
   brief's declared tier.

**Conclusion: T440, T441, T442, and T443 are each individually `done` against their own
task-scoped acceptance criteria — but Phase 4 as a whole, per `plan-035`'s own acceptance-criteria
block, remains open.** All four tasks were deliberately and explicitly scoped as policy/schema
definition only (each brief's own "Hard scope boundary" section says so), with live
execution/enforcement/cost-measurement work explicitly deferred to future, separately-authorized
tasks. Declaring Phase 4 closed on the strength of T440-T443's task-level completion alone would
be a false milestone. The honest status is: Phase 4's scaffolding (tier vocabulary, routing
policy, escalation policy, and now scorecard schema fields) is complete; its substantive gates
(a real economy-tier run, a real observed escalation, real cost data, a real unstable-component
check) are not, and are blocked on the same live-execution-harness gap (`T458`/`T456`) already
tracked and disclosed elsewhere in this ledger.

**Left unmerged per this session's standing no-self-merge instruction** — MR !287 handed back to
the top-level session for merging.
