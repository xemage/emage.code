# T509 — Design pass: harden the closed loop's improvement detection

**Status:** pending
**Owner:** solution-architect
**Priority:** P1
**Depends on:** none (design-only, no code dependency)
**Based on:** `docs/tasks/completed-tasks.md`'s `T507` row, `docs/artifacts/t507-closed-loop-cycle-v1.md`, `implementation/runtime/golden_harness/promotion.py`, `implementation/runtime/golden_harness/policy.py`, `docs/plans/plan-048-t458-k-threshold-decision.md`.

## Objective

**This is a design/scoping pass, not an implementation task** — mirrors `T496`'s own precedent
(a design-completion artifact concrete enough for a future, separately-dispatched implementation
task to build from). Produce a written design that resolves the real gap named below, presenting
concrete options with tradeoffs. **Do not decide which option to implement** — that decision, like
`T496`'s Option A/B/C choice, belongs to the user.

## The real gap, precisely

`T507` ran a real closed-loop cycle and got `promote=True` from `evaluate_promotion()` for a
proposal its own generating task disclosed was almost certainly not a genuine improvement (see
`t507-closed-loop-cycle-v1.md` §3.5/§3.7). This was not a bug in the sense of code disagreeing with
its own spec — `policy.floor_met()` did exactly what `plan-048` §4 defines: *"the non-regression
floor is met when the treatment arm's pass rate is not below the control arm's"* (`policy.py` line
59-62, a non-strict `>=` comparison, by design). The real gap is a **mismatch of purpose**:
`floor_met()` was designed and decided (`plan-048`) to answer *"is this safe to ship / not worse
than before"* — a regression gate. `promotion.py` reuses it as `evaluate_promotion()`'s sole
"improvement" conjunct (conjunct 1 of `plan-035`'s literal rule, *"improvement > regression"*), but
`floor_met()` never actually tests for improvement — only for "not measurably worse," which a
causally-inert proposal can satisfy purely on noise, as `T507` demonstrated with a real measured
instance.

Two compounding factors T507 surfaced, both real and both in scope for this design pass:

1. **No minimum evidentiary bar for a promotion decision.** `T507`'s aggregate was 3 cases, k=1
   each (one case's arms 1/1 vs 1/1, one 0/1 vs 1/1, one 1/1 vs 1/1) — `floor_met()` has no
   concept of sample size or confidence, and nothing in `evaluate_promotion()` requires escalation
   (`policy.MIN_ESCALATED_K = 3`) before a promotion can fire. Contrast: `check_no_critical
   regression()` (conjunct 2) *does* require `MIN_ESCALATED_K` before it will classify a
   *regression* as confirmed (`promotion.py` lines 128-138) — the asymmetry is that the codebase
   already has a higher evidentiary bar for detecting harm than for detecting benefit.
2. **No provenance-homogeneity check.** `T507`'s control trials were reused from historical data
   and its treatment trials were freshly dispatched in the same session — a real, disclosed
   confound (prompt-fidelity difference between the two dispatch contexts), not a proposal effect.
   Nothing in `TrialRecord` (`schema.py`) or `evaluate_promotion()` flags or restricts this kind of
   mixed-provenance comparison.

## What to produce

A design artifact (`docs/artifacts/promotion-improvement-hardening-design-v1.md`, mirroring
`T496`'s own artifact-naming precedent) covering:

1. **Root-cause framing**, refined from the above if your own reading of the code finds a sharper
   or more precise statement of the gap — don't just restate this brief, verify it against the real
   `policy.py`/`promotion.py` source yourself first.
2. **At least two concrete, evaluable options** for closing the gap, each with a real tradeoff
   analysis. Candidates worth evaluating (not a mandate — add, drop, or merge these as your own
   analysis warrants):
   - A minimum-evidence gate: require every case in a promotion-relevant comparison to reach
     `MIN_ESCALATED_K` before `evaluate_promotion()` can return `promote=True`, with `floor_met()`
     at k<3 downgraded to "insufficient evidence, escalate" rather than treated as sufficient.
   - A symmetric "confirmed positive effect" classification, parallel to
     `classify_k_plus_outcome()`'s existing three regression-oriented outcomes
     (`CONFIRMED_COIN_FLIP` / `CONFIRMED_PERSISTENT_EFFECT` / `ELEVATED_BUT_HETEROGENEOUS`), so the
     improvement conjunct has the same rigor the regression conjunct already has, instead of
     borrowing a "not worse" check and calling it "better."
   - A provenance-homogeneity requirement: `TrialRecord` or a comparison-level wrapper records
     how each trial was produced (fresh dispatch vs. reused historical record) and
     `evaluate_promotion()` refuses (or at minimum flags) a comparison mixing provenance across
     arms without an explicit, human-supplied compatibility attestation — mirroring
     `check_no_critical_regression`'s existing `known_arm_agnostic_case_ids` override pattern.
   - Explicitly evaluate and state a recommendation on whether any of the above should apply
     retroactively to `check_no_critical_regression`'s existing logic too, or only to the new
     improvement conjunct — the regression side already has a k-threshold; does it need a
     provenance-homogeneity requirement as well?
3. **A recommendation**, clearly labeled as your own recommendation, not a decision — same posture
   `T496`'s own artifact took on the `@security-engineer` options.
4. **A concrete acceptance-criteria sketch** for whichever option(s) a future implementation task
   would build, detailed enough that a future task brief could be written directly from it (per
   `T496`'s own precedent enabling `T497`).

## Constraints

- Design-only. Do not modify `implementation/runtime/golden_harness/promotion.py`,
  `policy.py`, `schema.py`, or any test file.
- Read the real, current source of `promotion.py`, `policy.py`, and `schema.py` yourself before
  writing anything — do not take this brief's own code citations as pre-verified; confirm them
  directly, the same discipline every other task this session has followed.
- Read `docs/artifacts/t507-closed-loop-cycle-v1.md` in full for the real, disclosed evidence this
  design pass is responding to — do not re-derive the T507 finding from scratch.
- This task does not itself decide whether the closed loop is "trusted" for a real merge decision
  going forward — that remains a separate, future call once an implementation task (if any) is
  built from this design and its own acceptance criteria are met.

## Acceptance criteria

- [ ] Root-cause framing independently verified against real, current source (not assumed from
      this brief)
- [ ] At least two concrete, evaluable hardening options presented with real tradeoffs
- [ ] A clearly-labeled recommendation, distinct from a decision
- [ ] Explicit treatment of whether provenance-homogeneity should extend to the existing regression
      conjunct
- [ ] Acceptance-criteria sketch detailed enough for a future implementation task brief to be
      written directly from it
- [ ] No code file modified

## Blocker protocol

Standard: `technical | dependency | unclear_requirements | external`, severities
`critical | major | minor`, max 2 retries before escalation.
