# Task T500 — Phase 6 SIA readiness audit and detailed planning pass

**Status:** done
**Closure note (2026-09-18):** audit (`docs/artifacts/phase6-sia-readiness-audit-v1.md`) and
planning pass (`docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md`)
delivered and independently re-verified by the top-level session before this closure (not
accepted on the implementer's self-report alone) — see `docs/tasks/completed-tasks.md`'s `T500`
row for the full closure record. **Neither document opens, dispatches, or authors a task brief
for any Phase 6 implementation task** — that remains a separate, future step requiring explicit
user approval.
**Owner:** solution-architect
**Priority:** P0
**Depends on:** none (Phase 6 is gate-reachable — see Context)
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6 ("Closed Loop"), Part 1
"Formalization note (2026-08-12)"; `docs/artifacts/phase2-3-poc-debt-scorecard-v1.md`;
`docs/checkpoints/checkpoint-033-phase4-phase5-complete-gate-g3-closed.md`

## Objective

Produce two artifacts that together determine whether — and how — Phase 6 ("Closed Loop",
v7.0.0) can actually start: (1) a rigorous, evidence-based audit of the existing SIA
(Self-Improvement Agent) infrastructure against the Weakness Mining → Proposal → Validation
model `plan-035` §2.4 Phase 6 describes, and (2) a detailed Phase 6 planning pass at the same
execution-ready granularity `plan-037`/`plan-038`/`plan-041`/`plan-043` produced for their own
phases. This is `plan-035`'s own T460, expanded per this dispatch's explicit instruction to
also include the planning pass in the same task, and renumbered `T500` per this repo's task-ID
ledger (the real next-free ID; `plan-035`'s own `T460`-`T466` placeholders are stale, same
renumbering discipline already applied once to `plan-035`'s `T41A`/`T41B`/`T41C`).

**This task produces the audit and the plan only. It does not open, dispatch, or author task
briefs for any Phase 6 implementation task (weakness mining, `@meta-improver`, validation
rules, the human MR gate, harness lineage docs, or the kill switch). Per this repo's own
established precedent (`plan-037`/`038`/`041`/`043`, most recently reaffirmed in
`checkpoint-033`'s own "Phase 6 ... not started" note), those remain gated on this planning
pass being reviewed and separately approved before any task brief is authored — not on this
task's own completion alone.**

## Context

Current phase: post-Phase-5, pre-Phase-6 planning. Latest checkpoint:
`docs/checkpoints/checkpoint-033-phase4-phase5-complete-gate-g3-closed.md` (written immediately
after T499's merge today, 2026-09-18). That checkpoint's own "Gate status" section: G0/G1/G2/G3
are all closed (G3 closed today, by T499's re-measurement); **G4's evaluator-protection
precondition closed alongside G1** (per `checkpoint-021`/`checkpoint-032`), but `checkpoint-033`
is explicit that "the rest of its own phase's conditions (Phase 6, below) haven't been
reached" — i.e. G4 does not fully close until Phase 6's own acceptance criteria are met: G4 is
the gate *governing* Phase 6, not a precondition satisfied before Phase 6 starts. Per
`plan-035`'s phase graph, Phase 6 has three incoming edges (`P3 --> P6`, `G3 --> P6`,
`G4 --> P6`) and `checkpoint-033` confirms all of P3 (done, `checkpoint-032`) and G3 (done,
today) are satisfied, so **Phase 6 is gate-reachable now** — but `checkpoint-033` is equally
explicit that it "has not been planned to execution-ready detail and is not started," matching
every other phase's own precedent of a dedicated planning pass before any task brief.

`plan-035` §2.4 Phase 6's own text asserts: "This is the source roadmaps' `emage.climb` — but
built as *wiring*, not greenfield. `implementation/sia/`, `sia-executor.py`, reward shaping
(T225), harness capture (T223), and reward attachment (T224) already exist." Part 1's own
"Formalization note (2026-08-12)" immediately qualifies this: those SIA items were
"subsequently reclassified as an **invalidated PoC**" by `docs/plans/plan-016-*`/task T303 (see
`docs/artifacts/phase2-3-poc-debt-scorecard-v1.md`) — "no real model, no real deployment, the
evaluator produced zero discriminative signal." The note states this "does not change the
verdict that the *scaffolding* ... exists ... but it does mean Phase 6 ... inherits a PoC-grade
foundation, not a validated one," and explicitly requires: "T460's audit must read this
scorecard before scoping any new module."

**This task's dispatcher (the orchestrator, this session) independently re-confirmed one of the
debt scorecard's four findings is still true today, unchanged**: `implementation/scripts/
sia-executor.py` on `origin/develop` (870 lines) still contains the `mock_delay` constructor
default, CLI flag, and docstring line the scorecard found over six weeks ago. The dispatcher
also found `docs/tasks/completed-tasks.md`'s own T223/T224/T225/T226/T228/T235 rows already
carry an inline "CORRECTED 2026-07-31 ... reclassified as INVALIDATED PoC ... no real model, no
real deployment, evaluator produced zero discriminative signal" annotation — **this is a
pre-existing ledger fact to verify against the real code, not a new finding of this task, and
not something to accept as settling the code-level question either way**: the ledger correction
addresses the *overall PoC claim chain* (a fabricated fine-tuned-model deployment resting on
zero-signal eval data), not necessarily whether `reward_attachment.py`/`reward_shaping.py`
themselves are individually real, working, reusable code versus fabricated. `implementation/
adapters/sia-target/reward_attachment.py` and `reward_shaping.py` both exist on `origin/develop`
today, each with their own dedicated passing test files per the ledger row (27 and 30 tests
respectively) — whether that is genuine reusable infrastructure or itself implicated in the
same fabrication pattern is exactly the open question this audit must resolve by reading the
actual current files, not by inference from the ledger annotation alone.

## Inputs (read directly, in full, before writing anything)

1. `docs/artifacts/phase2-3-poc-debt-scorecard-v1.md` — the invalidated-PoC verdict this audit
   must ground itself in. Read in full; its 4 debt items and its "Any future attempt at Pattern
   B/C must start from all three of the following, none of which exist today" list are the
   baseline this audit measures against.
2. `implementation/scripts/sia-executor.py` (870 lines, `origin/develop`) — read the whole file,
   not just the previously-confirmed `mock_delay` lines. Understand what a real LLM call path
   would require relative to its current structure.
3. `implementation/sia/__init__.py` (12 lines) and `implementation/sia/util.py` (191 lines) —
   read both in full. Characterize what, if anything, is real reusable infrastructure here.
4. `implementation/adapters/sia-target/reward_attachment.py`, `reward_shaping.py`,
   `harness-entrypoint.py`, `trainer_bridge.py`, `release_gate.py` — read each in full.
5. `docs/tasks/task-T223.md`, `task-T224.md`, `task-T225.md` — read in full, and cross-check
   each against the actual code/test files each claims to have produced (per plan-035's own
   framing: T223 = harness capture, T224 = reward attachment, T225 = reward shaping).
6. `tests/functional/test_t223_sia_harness_capture.py`, `test_t224_reward_attachment.py`,
   `test_t225_reward_shaping.py` (and `test_t222_sia_task_evaluator.py` if present) — read in
   full; run them if runnable in this environment and report actual pass/fail, not the ledger's
   historical claim.
7. `docs/tasks/completed-tasks.md` rows T220–T241 in full (already partially quoted above) —
   confirm no row in that range or beyond it that touches `implementation/sia/`,
   `implementation/scripts/sia-executor.py`, `implementation/adapters/sia-target/`, or
   reward/harness-capture/weakness-mining concepts has been added or changed since the debt
   scorecard's 2026-07-31 date. Search the full ledger (not just T220-T241) for any such row.
8. `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6 (full section, task table T460-T466,
   acceptance criteria, the "Gate G4 governs this entire phase" line) and its Part 1
   "Formalization note (2026-08-12)".
9. `docs/checkpoints/checkpoint-033-phase4-phase5-complete-gate-g3-closed.md` (full document) —
   the latest checkpoint; its "Phase 6" section and "Gate status" section are load-bearing for
   this task's own Context section above.
10. `docs/plans/plan-037-phase2-phase5-sequencing.md`, `plan-038-phase5-detailed-planning.md`,
    `plan-041-phase3-maturity-ladder-detailed-planning.md`,
    `plan-043-phase4-task-tier-routing-detailed-planning.md` — read as structural/rigor
    precedent for the planning-pass document this task also produces (per-task
    objective/inputs/outputs/acceptance-criteria, explicit dependencies, agent assignments,
    token/time budget, "Status: proposed — not approved for task-brief authoring or execution"
    header convention).
11. `implementation/knowledge/agents/*.md` (or the registry `implementation/registry/
    summary.md`/`index.json`) for every agent `plan-035` §2.4 Phase 6's own T460-T466 task table
    nominally assigns as owner — confirm each's real current tool grant before the
    planning-pass document proposes owners, following this repo's own repeatedly-applied
    discipline (T410/T415/T418/T420/T430/T440/T451/T456/T458 precedent: verify tool grants
    directly, do not assume `plan-035`'s nominal owner column is still correct). **Note:** this
    brief deliberately does not spell out those agent names here — two of them are currently
    `stable` components, and this repo's `check-maturity.py` has a known, previously-fixed-
    then-recurring `_ledger_defect()` check that whole-word-matches a `stable` component's
    literal id inside any open P0/P1 task brief and fails it. Read `plan-035` §2.4 Phase 6's
    task table directly for the actual owner list rather than relying on this brief to repeat it.

## Constraints

- Token budget: this task's audit+planning work should stay within `plan-035`'s own Phase 6
  budget line (300k) but is not expected to need anywhere near that for a planning-only pass —
  target well under 100k for this task specifically.
- File ownership: this task may only create/modify files under `docs/artifacts/`,
  `docs/plans/`, and its own `docs/tasks/task-T500.md` status field. It must not modify
  `implementation/**`, `tests/**`, or any other `docs/tasks/*.md` brief.
- Protected paths (do not touch, per the dispatching session's own standing instruction this
  turn): `.mcp.json`, `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`,
  and the branch `feature/T475-codex-platform-integration`.
- No self-merge: work in a dedicated worktree/branch off `origin/develop`
  (`agent/solution-architect/T500`), open a merge request, and stop. Do not merge it.
- Do not accept any prior document's summary (including `plan-035`'s own "already exist"
  framing, and the ledger's own "CORRECTED ... INVALIDATED PoC" annotation) as ground truth
  without independently verifying it against the real, current file content — mirror
  `phase2-3-poc-debt-scorecard-v1.md`'s own "verified directly by reading the file" standard for
  every claim in the audit.
- Do not author task briefs for any Phase 6 implementation task. Do not add rows to
  `docs/tasks/active-tasks.md` beyond what this dispatch's own ledger commit already adds for
  T500 itself.
- Tool grant note: `solution-architect`'s real registered tool grant has no `execute`/Bash. Per
  this repo's own established fallback (T410/T420/T440/T451/T456 precedent, most recently
  T440's ledger row), produce all deliverable content, verification findings, and a clear
  hand-off note describing what remains to be mechanically applied (worktree creation, test
  runs, commit, push, MR). The orchestrator will perform that mechanical follow-through and
  independently re-verify the content first, exactly as in those precedents.

## Expected outputs

1. `docs/artifacts/phase6-sia-readiness-audit-v1.md` — an audit with the same evidentiary rigor
   and structure as `phase2-3-poc-debt-scorecard-v1.md`: a debt/gap inventory (each item backed
   by a direct, cited verification — file, line, what was actually read, not a restated
   assumption), explicit (a)/(b)/(c) determinations for T223/T224/T225-equivalent components
   (genuinely separate and working / implicated in the same fabrication pattern / something
   else), a real gap list against the Weakness Mining → Proposal → Validation model, and a clear
   recommendation (including, if warranted, a recommendation that G4's "the rest of its own
   phase's conditions" are further from closing than `plan-035`'s original draft assumed).
2. `docs/plans/plan-055-phase6-closed-loop-detailed-planning.md` (or a title you judge more
   accurate once the audit is complete — the number `plan-055` is fixed as the real next-free
   ID, confirmed fresh by the dispatching session; the exact title suffix is not) — a Phase 6
   planning pass at `plan-038`/`plan-041`/`plan-043`'s own rigor: execution-ready task
   breakdown grounded in what the audit actually finds (re-scoped from `plan-035`'s original
   T460-T466 draft sketch wherever the audit's findings require it — do not force the original
   six-task list to still fit if the real starting point is rockier), real current task/agent
   IDs (`T501` onward — confirm fresh against the ledger state at commit time, since this task's
   own dispatch will have just consumed `T500`), real verified agent tool-grant checks per
   proposed owner, explicit dependencies, a `"Status: proposed — not approved for task-brief
   authoring or execution"` header matching the established convention, and an explicit
   statement of this document's own limit (does not itself authorize dispatch).
3. A short hand-off note (can be inline in your final report, does not need its own file)
   listing every worktree/test/commit/push/MR step still required, for the orchestrator to
   execute.

## Acceptance criteria

- [ ] Every claim in the audit that could be checked against real file content was checked
      against real file content (not accepted from a prior document's summary) — evidenced by
      specific file paths and line references in the audit document itself.
- [ ] The audit explicitly re-verifies (does not merely cite) the debt scorecard's `mock_delay`
      finding against the current 870-line `sia-executor.py`.
- [ ] The audit reads and characterizes `implementation/sia/__init__.py` and `util.py` in full.
- [ ] The audit reads `task-T223.md`/`task-T224.md`/`task-T225.md` and their corresponding code/
      test files, and states an explicit (a)/(b)/(c) determination for each with direct evidence.
- [ ] The audit confirms (via a ledger search, not assumption) whether anything relevant has
      changed since the debt scorecard's 2026-07-31 date.
- [ ] The audit produces a real gap list against `plan-035`'s Weakness Mining → Proposal →
      Validation model and Phase 6's stated acceptance criteria.
- [ ] The planning-pass document is grounded in the audit's actual findings, not a restatement
      of `plan-035`'s own draft sketch, and explicitly re-scopes anything the audit finds
      unready.
- [ ] The planning-pass document uses real, currently-free task IDs and states its own
      "not approved for task-brief authoring or execution" limit explicitly.
- [ ] Neither document opens, dispatches, or authors a task brief for any Phase 6 implementation
      task.
- [ ] If anything is found that is alarming or ambiguous enough to need a real user decision
      before the audit can conclude, it is reported as a blocker (type + severity), not resolved
      by guessing.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). Given this task's own subject matter (a previously
invalidated self-improvement loop), a genuinely alarming or ambiguous finding should be reported
as a blocker for the orchestrator/user rather than resolved by inference.
