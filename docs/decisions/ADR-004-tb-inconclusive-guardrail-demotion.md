# ADR-004 — Treat T407's Inconclusive Terminal-Bench delta as Null-equivalent; demote to no-harm guardrail

> Filename: `ADR-004-tb-inconclusive-guardrail-demotion.md`

- **Status**: Accepted
- **Date**: 2026-09-08
- **Decider(s)**: user, orchestrator
- **Tasks**: T407 (this decision's trigger), T408, T409 (unaffected — see Consequences)
- **Evidence**: `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1's frozen decision-rule
  block and its 2026-09-08 dated successor block (immediately below the frozen block);
  `docs/benchmarks/tb-delta-v6.12.0.md` §§6-7; `docs/tasks/completed-tasks.md` T407 row; MR !211
  (T407 closeout), MR !212 (cost correction)

## Context

`plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1 registers a decision rule for classifying the
first Terminal-Bench two-arm delta measurement (`T41A`/`T407`) as Inconclusive, Null, or
Positive/Negative, based on cross-run spread and aggregate delta magnitude. That rule is
explicitly frozen at authoring time and pre-commits specific consequences for a **Null**
classification — Terminal-Bench demoted from improvement signal to no-harm guardrail, golden
suite remains sole load-bearing signal, no subset re-cutting, no G1 relaxation — but says nothing
about what follows an **Inconclusive** classification specifically.

T407 ran (`docs/benchmarks/tb-delta-v6.12.0.md` §6): 3 independent full-subset passes (Design A,
`-k 1 -l 25`). Arm A's cross-pass spread came out to exactly 8.0pp — landing precisely on the
frozen rule's own `≥ 8pp` Inconclusive threshold (inclusive of equality). Aggregate delta (B−A)
was −1.33pp. Per the rule's own text ("Do not report as null"), this is not a Null result, and
the published document does not report it as one.

The rule's prescribed action for Inconclusive is "raise `k`, or reduce nondeterminism, before any
interpretation is recorded" — i.e., a costlier re-run ("Design B," on the order of ~450 trials)
to chase a classification the rule's machinery could actually resolve. That re-run was evaluated
and rejected for this release cycle; this ADR records why, and what happens instead.

## Decision

Inconclusive is treated identically to how the frozen block pre-committed to treat a Null delta.
Concretely:

1. **No further Design A/B re-run is dispatched at this time.** Three reasons, in order of
   weight:
   - The plan's own prediction, registered before any T407 measurement existed, was "small
     positive, plausibly under the resolution floor" — the plan's authors already anticipated
     Terminal-Bench might not resolve emage.code's effect, since the projection targets
     multi-agent planning discipline rather than lone-terminal-task completion. An 8.0pp spread
     and a −1.33pp aggregate delta is consistent with exactly that prediction.
   - Gate G1 closes on T407/T408/T409's acceptance criteria being **met** (harness works, delta +
     spread + cost published), not on any particular classification outcome. The frozen block
     separately states a null delta "does not relax G1... is not grounds for promoting any
     component out of beta" — meaning even the best realistic outcome (a clean Null) would not
     have required further measurement. Inconclusive requires no more.
   - Real additional cost: T407's total across all attempts already reached ≈$100
     (`tb-delta-v6.12.0.md` §7.2), and a higher-`k` redesign would cost materially more plus 13+
     hours of additional wall-clock, to sharpen an instrument the plan's own authors already
     flagged as plausibly under-resolution. Poor expected value against the golden suite, already
     frozen and load-bearing under G1 as actually defined.
2. **Terminal-Bench is demoted from improvement signal to no-harm guardrail.** Subsequent
   releases must not show a delta below −4pp (the Null block's own threshold, reused verbatim,
   not a new number).
3. **The golden suite remains the sole load-bearing progress signal.** Phase 6's improvement loop
   (T460-T466, not yet built) optimises against the golden suite only, with the Terminal-Bench
   guardrail as a merge precondition.
4. **`tb-subset.json` is not re-cut, re-stratified, or extended** in response to this
   classification.
5. A free observational follow-up (the `predicted_effect: positive` vs. `neutral` split, per the
   frozen block's own "record this, but do not act on it" instruction) is recorded in
   `tb-delta-v6.12.0.md` as context only — explicitly not used to reopen this classification.

The full, dated text of this decision — written to satisfy the frozen block's own supersession
mechanism ("may not be edited after the first T41A run — only superseded by a dated successor
block") — lives in `plan-035-roadmap-v7-ground-up.md` §2.4, immediately after the frozen block.
This ADR is the companion decision record; the plan block is the authoritative, plan-governing
text.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| Dispatch "Design B" (higher `k`, ~450 trials) to force a clean Inconclusive/Null/Positive/Negative classification | Literal compliance with the rule's own prescribed Inconclusive action; might resolve the ambiguity | ≈$100+ additional real cost, 13+ hours more wall-clock, on an instrument the plan's own registered prediction already expected to be under-resolution; delays Phase 2+ for a signal G1 does not require | Rejected — poor expected value; not required by G1 |
| Leave Inconclusive unaddressed (no successor block, no guardrail) | No immediate cost | Leaves Terminal-Bench with no defined role going forward; silently drops the "no-harm guardrail" safety property the Null branch was designed to guarantee; violates the frozen block's own supersession requirement once a gap is identified | Rejected — the frozen block explicitly requires a dated successor once a gap like this is found, not silence |
| Treat Inconclusive as Positive/Negative by some reinterpretation of the spread statistic | Would allow a definitive call | Already explicitly rejected in `tb-delta-v6.12.0.md` §3.3 as a category error (Bernoulli per-trial stdev is not a valid substitute for cross-run spread) and re-confirmed not applicable in §6.4 | Rejected — not what the data actually shows |

## Consequences

- **Positive**: Terminal-Bench retains a defined, useful role (no-harm guardrail) rather than
  being silently abandoned after an ambiguous result; the golden suite's status as sole
  load-bearing signal is reaffirmed and unambiguous; no further real API spend is committed this
  cycle; G1 remains closed exactly as it already was.
- **Negative**: Terminal-Bench never actually confirms or denies emage.code's effect on
  lone-terminal-task completion this cycle — that question is deferred, not answered.
- **Risks introduced**: none beyond what the frozen Null block already accepted for its own
  branch; this decision explicitly inherits, not expands, that risk profile.
- **Follow-ups**: T409 (Harbor-trajectory taxonomy ingestion) is unaffected — it depends on T407
  genuinely completing, not on classification outcome, and remains a separate dispatch decision
  not made by this ADR. No new task is created by this ADR.

## Validation

This decision is self-validating in the sense the frozen block already defines: the guardrail
(no release delta below −4pp) is checked at every future Terminal-Bench measurement against the
golden-suite-driven improvement work in Phase 6, once that phase exists. There is no separate
metric this ADR itself introduces to confirm — it is a scope and process decision, not a technical
one.
