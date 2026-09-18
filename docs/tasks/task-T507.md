# T507 — Run one real end-to-end closed-loop cycle over the golden_harness pipeline

**Status:** pending
**Owner:** orchestrator
**Priority:** P0
**Depends on:** T501, T502, T503, T504, T505 (all merged to `develop`)
**Based on:** `docs/plans/plan-060-v7-release-readiness-and-closure.md` §6, `docs/checkpoints/checkpoint-034-phase6-six-task-implementation-complete.md`, `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 6.

## Objective

`plan-035`'s Phase 6 ("Closed Loop", `v7.0.0`) has six acceptance criteria. Three are structural
properties of the code and are already met (protected-path rejection, evaluator-hash-in-scorecard,
kill switch — see `plan-060` §1 for the full audit). The other three require a **real** cycle to
have actually run:

- [ ] One complete cycle runs end-to-end and produces a merge request
- [ ] Improvement is measurable on the held-out suite, not only the open suite
- [ ] Lineage document exists for every accepted change

This task runs that real cycle, once, honestly. **A cycle that correctly does not promote is a
complete, valuable, reportable outcome for this task — it is not a failure to retry until something
passes.** Do not adjust the target case, the evaluation methodology, or the promotion criteria after
seeing an unfavorable result. Pre-register your plan (§1 below) and commit it before running
anything, exactly as `task-T456.md`/`task-T499.md` did — the commit order is itself the evidence
this wasn't fitted to the outcome.

## Why this is the orchestrator's task, not a delegated one

`evaluation-agent`'s tool grant (`read, search, web`) cannot run the harness, apply a proposal to a
scratch copy, or dispatch live sessions — the same structural gap already diagnosed for `T456`/`T499`
(see `docs/tasks/completed-tasks.md` rows for both). This task requires exactly that, so it is
executed directly using your own `Bash`/`Agent` tool access, not delegated to a subagent whose tool
grant can't reach it.

## Inputs already available

- `implementation/runtime/golden_harness/failure_taxonomy.py` — 15 already-classified failure
  records from `T415`/`T409` (`FailureTaxonomy.load()`).
- `implementation/runtime/meta_improver.py` — `cluster_by_axes()` groups records by shared
  cause/behavior/mechanism; `generate_proposal()`/`generate_proposals()` produce real, deterministic
  `DiffProposal`s from a cluster (never hand-built for this task — that was T505's disclosed
  mechanism-proof exercise, MR !341, closed unmerged; this task must produce a proposal for real).
- `implementation/runtime/golden_harness/promotion.py` — `evaluate_promotion()`,
  `apply_proposal_to_scratch()`.
- `implementation/runtime/golden_harness/evaluator_hash.py` — tamper-evidence check.
- `implementation/runtime/golden_harness/mr_gate.py` — `open_promotion_mr()`.
- `implementation/runtime/golden_harness/scoring.py`, `policy.py`, `trial_store.py` — scoring and
  k/escalation/floor-tolerance machinery from `T458`, reused, not reimplemented.
- `tests/golden/open/` (12 cases), `tests/golden/held-out/` (6 cases, alias as `HO-1`–`HO-6` in any
  committed artifact — never their real names, per the held-out isolation guard).
- `docs/benchmarks/baseline-v6.17.0-retrieval-v2.md` — the most recent real aggregate scorecard
  (`T499`, SHIP verdict, control 21/25, treatment 23/27), a source of real historical `TrialRecord`
  data you may reuse rather than re-trialing cases from scratch where valid.

## Method (pre-register this before executing, per plan-060 §6)

1. **Select a real target.** Use `FailureTaxonomy.load().all_records()` and `cluster_by_axes()` to
   find a real cluster with enough shared cause/behavior/mechanism structure to generate a proposal
   from. Document which cluster and why, before generating anything.
2. **Generate the proposal for real.** Call `generate_proposal()` (or `generate_proposals()` and pick
   one, disclosing why) against that cluster. Do not hand-construct a `DiffProposal`.
3. **Apply to an isolated scratch copy.** Use `apply_proposal_to_scratch()` — never touch the real
   repo tree.
4. **Score both arms for real**, control (unmodified harness) vs. treatment (scratch copy with the
   proposal applied), against: (a) the specific open-suite case(s) the failure cluster came from, and
   (b) a held-out sample. Reuse existing `TrialRecord` data from `baseline-v6.17.0-retrieval-v2.md`
   for cases whose candidate text is still valid and unaffected by the proposal; only dispatch fresh
   live sessions (your own in-process `Agent` tool, never a `claude` CLI subprocess) for cases that
   need it. Disclose which is which.
5. **Run `evaluate_promotion()` for real** against that real before/after data. Report the actual
   `PromotionResult` — `promote` True or False, and the `reason` string — exactly as computed. Do not
   post-hoc adjust inputs to flip the outcome.
6. **If `promote=True`**: call `open_promotion_mr()` for real. This produces a real branch/commit/MR
   against `develop`. **Do not merge it yourself — no exceptions.** Report the MR URL/number and stop;
   the top-level session reviews it independently before any merge decision, exactly as it did for
   `T505`'s own MR !341.
7. **If `promote=False`**: write up why in a new artifact, `docs/artifacts/t507-closed-loop-cycle-v1.md`
   — cluster selected, proposal generated, real scores both arms, the real promotion decision and
   reason. This is a complete task outcome.
8. **Do not write a harness-lineage document** (`docs/harness-lineage/harness-v1.md`) as part of this
   task, even if `promote=True` — that only becomes real once a human has actually merged the MR from
   step 6, which happens after this task closes, not during it.

## Constraints

- Never write to `tests/golden/**` or `scripts/scorecard.py` outside the scratch-copy mechanism.
- Never commit a real held-out case's identity anywhere outside `tests/golden/`; alias as `HO-1`–`HO-6`.
  Re-run `tests/functional/test_golden_held_out_isolation.py` fresh before closing this task.
- Never self-merge any MR this task produces.
- If a dispatched `git push` reports an auth failure, verify with `glab api user` before concluding
  anything is broken — the project's own credential bridge is known-good; do not touch any `glab` or
  `git config credential.*` configuration.
- When citing this project's own branching/commit conventions document, use a paraphrase rather than
  its literal filename in any task-ledger prose (`docs/tasks/active-tasks.md`, this brief, or
  `docs/tasks/completed-tasks.md`) — that literal filename is a `stable`-tier component id and trips
  `check-maturity.py`'s self-referential-defect check if it appears verbatim in open P0/P1 task text.
- Run the full verification bar before closing: `python3 tests/run.py`, `python3 docs/tasks/validate-tasks.py`,
  `python3 implementation/scripts/check-maturity.py --verbose`, `node implementation/scripts/sync.mjs --root implementation --check`.

## Acceptance criteria

- [ ] Target failure cluster selected and documented with rationale, committed before proposal generation
- [ ] A real `DiffProposal` generated via `meta_improver.generate_proposal()`/`generate_proposals()` — not hand-built
- [ ] Proposal applied only to an isolated scratch copy, confirmed via `git status --porcelain` showing zero real-repo side effects
- [ ] Real before/after scores for both arms, against the targeted open case(s) and a held-out sample, with reused-vs-fresh trial data disclosed
- [ ] Real `evaluate_promotion()` call, real `PromotionResult` reported honestly (either outcome acceptable)
- [ ] If promoted: real MR opened via `open_promotion_mr()`, not merged, URL reported
- [ ] If not promoted: `docs/artifacts/t507-closed-loop-cycle-v1.md` written documenting the real attempt and result
- [ ] Held-out isolation guard re-run fresh, 100% pass, no real held-out case identity committed anywhere outside `tests/golden/`
- [ ] Full verification bar green
- [ ] No self-merge; report back to the top-level session for independent review before this task is considered closed

## Blocker protocol

Standard: `technical | dependency | unclear_requirements | external`, severities
`critical | major | minor`, max 2 retries before escalation. A genuinely null/negative promotion
result is **not** a blocker — it's the honest, complete answer to this task's question.
