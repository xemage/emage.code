# T511 — Implement promotion hardening Option B: symmetric positive-effect classification

**Status:** pending
**Owner:** backend-developer
**Priority:** P1
**Depends on:** T510 (done — the minimum-evidence gate this task's own required precondition builds on)
**Based on:** `docs/artifacts/promotion-improvement-hardening-design-v1.md` (T509's design, §2 "Option B" and §5 item 11), `docs/artifacts/t507-closed-loop-cycle-v1.md`, `implementation/runtime/golden_harness/policy.py`, `implementation/runtime/golden_harness/promotion.py`.

## Objective

Build Option B from `T509`'s design, per the user's explicit instruction ("Build B"), completing
all three hardening options `T509` scoped after `T507`'s real finding. `T510` already built and
merged Options A (per-case minimum-evidence gate) and C (provenance-homogeneity check). This task
adds the third: a qualitative "was this actually a traceable positive effect" classification,
giving the improvement conjunct the same architectural rigor `classify_k_plus_outcome()` already
gives the regression conjunct, instead of `floor_met()`'s bare "not measurably worse" test standing
in for it alone.

**Read `docs/artifacts/promotion-improvement-hardening-design-v1.md` §2 "Option B" and §5 item 11 in
full before writing any code.** This brief translates that design into a concrete implementation
scope, including several concrete decisions the design itself deliberately left open — read the
"Design decisions this brief makes" section below and verify each against the real, current source
yourself; disclose if your own reading finds a better approach, the same way `T510`'s implementer
found and corrected real gaps in its own brief rather than following it blindly.

## Design decisions this brief makes (disclosed, not silent)

The design's own §2 "Option B" text left several mechanics unresolved for "a future implementation
task." This brief resolves them as follows — verify each against real source before building, and
flag any you'd resolve differently:

1. **Placement**: `classify_k_plus_improvement_outcome()` (the design's own suggested name) belongs
   in `policy.py`, immediately after `classify_k_plus_outcome()` — it is conceptually parallel
   infrastructure (a k≥3 classification function), not promotion-decision glue, mirroring where
   `classify_k_plus_outcome()` itself already lives.
2. **Precondition**: reuses `_require_min_k()` exactly as `classify_k_plus_outcome()` does — this
   function requires `MIN_ESCALATED_K` in both arms, same as its regression-side sibling. This is
   why the design's own "Interaction between options" section says Option B structurally
   presupposes Option A: `T510`'s `check_minimum_evidence()` gate is now a hard precondition
   `evaluate_promotion()` enforces before promotion can ever fire, so by the time this new
   classification is called in that real pipeline, its own `_require_min_k` precondition is already
   guaranteed satisfied — but the function itself must still enforce it directly (raise
   `ValueError`, exactly like `classify_k_plus_outcome()`), since it is also independently callable
   and testable on its own.
3. **The four-outcome shape**: the design's own text describes only the floor-met branch
   concretely (`CONFIRMED_POSITIVE_EFFECT` vs. the existing `CONFIRMED_COIN_FLIP`, reused not
   renamed) and says a floor-missed case needs "no new outcome" since that's already
   `classify_k_plus_outcome()`'s concern. This brief resolves that as: for a floor-missed case,
   `classify_k_plus_improvement_outcome()` delegates to `classify_k_plus_outcome()` directly and
   returns its result verbatim (`CONFIRMED_PERSISTENT_EFFECT` or `ELEVATED_BUT_HETEROGENEOUS`) —
   reuse, not reimplementation, consistent with this module's own established convention (`policy.py`'s
   own docstring: "this module implements an already-decided policy; it does not re-derive it").
   The result is one function giving the complete four-outcome picture for any k≥3 case, not two
   functions callers must remember to call together.
4. **The recurrence rule**: category-3 (`policy.CATEGORY_TRACEABLE_POSITIVE_INFLUENCE`) must recur
   across `>= 2` of the case's **treatment** trials specifically (not control — a category-3 finding
   is about the treatment arm's own qualitative behavior, per `should_escalate()`'s existing Trigger
   2 semantics, which already reads only `treatment_k1.category`). Reuse the existing `Counter`-based
   recurrence-counting shape from `count_cause_occurrences()`/`is_floor_miss_actionable()`, applied to
   `category` instead of `diagnosed_cause`, rather than writing new counting logic — a new helper
   (e.g. `count_category_occurrences()`) mirroring `count_cause_occurrences()`'s exact shape is
   preferred over inlining a one-off count.
5. **Wiring into `evaluate_promotion()`**: this brief's own judgment call, disclosed — the new
   classification becomes a **sixth required conjunct**, not merely an advisory/reported field.
   `evaluate_promotion()`'s call path already requires `check_minimum_evidence()` to pass (T510)
   before promotion can fire, so every real promotion decision already has k≥3 evidence available
   for every compared case — call `classify_k_plus_improvement_outcome()` per case (grouping via the
   existing `_group_by_case` pattern) and require every case's result to be
   `CONFIRMED_POSITIVE_EFFECT` for `promote` to be `True`.
   **This is intentionally conservative** — per the design's own disclosed trade-off, most real
   proposals will not qualify today, since qualitative categorization at dispatch time isn't yet a
   consistent practice. That is an accepted, disclosed consequence of building B as a real gate
   rather than a report-only field: a closed loop that cannot promote almost anything is safer than
   one that promotes things it cannot actually justify, and this project's own established posture
   throughout `T507`–`T510` has been to fail closed rather than open. If you find a strong,
   well-argued reason this should be report-only instead, disclose it explicitly and explain why
   rather than silently picking the less conservative path.

## What to build

1. `policy.py`: `count_category_occurrences(trials, category)` (or equivalent — mirroring
   `count_cause_occurrences`'s shape) and `CONFIRMED_POSITIVE_EFFECT = "confirmed_positive_effect"`
   constant, following the existing `CONFIRMED_COIN_FLIP`/`CONFIRMED_PERSISTENT_EFFECT`/
   `ELEVATED_BUT_HETEROGENEOUS` naming convention exactly.
2. `policy.py`: `classify_k_plus_improvement_outcome(trials: list[TrialRecord]) -> str`, per design
   decisions 2-4 above. Docstring should state the four possible return values and when each fires,
   mirroring `classify_k_plus_outcome()`'s own docstring style.
3. `promotion.py`: wire this into `evaluate_promotion()` per design decision 5. `PromotionResult`
   gains new fields reporting this conjunct's result per case — since this is a per-case
   classification (unlike the existing boolean conjuncts), report it as e.g.
   `improvement_classifications: dict[str, str]` (case_id -> outcome) or a `NamedTuple`-per-case
   tuple, your call on the exact shape, but it must let a caller see *every* case's classification,
   not just an aggregate boolean — following this module's established "never just a bare boolean,
   always name which case(s)" convention.
4. Update `_build_promotion_reason()` to name any case(s) that didn't reach
   `CONFIRMED_POSITIVE_EFFECT` when this is what blocks promotion, distinct from the existing
   evidence/provenance/floor/regression/hash failure messages.

## Tests to build

Locate and extend the existing test files: `tests/functional/test_golden_harness_policy.py` (for
`classify_k_plus_improvement_outcome`/`count_category_occurrences`, mirroring
`classify_k_plus_outcome`'s own existing test coverage there) and
`tests/functional/test_golden_harness_promotion.py` (for the new conjunct's wiring into
`evaluate_promotion()`).

- A test asserting `CONFIRMED_POSITIVE_EFFECT` fires when the floor is met and category-3 recurs
  across `>=2` treatment trials at k≥3.
- A test asserting `CONFIRMED_COIN_FLIP` fires when the floor is met but category-3 does not recur
  (zero or one occurrence).
- Tests asserting a floor-missed case correctly delegates to and returns exactly
  `classify_k_plus_outcome()`'s own result (both `CONFIRMED_PERSISTENT_EFFECT` and
  `ELEVATED_BUT_HETEROGENEOUS` branches).
- A test asserting `ValueError` on fewer than `MIN_ESCALATED_K` trials in either arm, mirroring
  `classify_k_plus_outcome()`'s existing precondition test.
- **A regression test using `T507`'s real data**: read `t507-closed-loop-cycle-v1.md` §3.3 again —
  none of T507's real treatment trials had a `category` recorded at all (unset/`None`). Construct
  the equivalent scenario (a case meeting the floor with zero category-3 occurrences in treatment)
  and confirm it classifies as `CONFIRMED_COIN_FLIP`, not `CONFIRMED_POSITIVE_EFFECT` — directly
  confirming this design element alone would also have correctly withheld promotion from `T507`'s
  real proposal, independent of `T510`'s already-built gates.
- An end-to-end `evaluate_promotion()` test confirming `promote=False` when every other conjunct
  (including `T510`'s two gates) passes but no case reaches `CONFIRMED_POSITIVE_EFFECT`, and a
  separate positive test confirming `promote=True` is still reachable in principle when a case
  genuinely does (construct a case with floor met, k=3 both arms, homogeneous known provenance, and
  category-3 recurring twice in treatment).

## Constraints

- Real code changes to `implementation/runtime/golden_harness/policy.py` and
  `implementation/runtime/golden_harness/promotion.py` are in scope. Read both files in full,
  current state (already includes `T510`'s changes) before editing.
- Do not touch `tests/golden/**` or `scripts/scorecard.py`.
- Preserve every existing function's current behavior for callers not touching the new
  classification — `classify_k_plus_outcome()` itself must not change.
- Standard worktree/branch/MR workflow (`agent/backend-developer/T511`, branched from `develop`). No
  self-merge — hand back to the top-level session for independent review and merge.
- Run the full verification bar before opening your MR: `python3 tests/run.py`,
  `python3 docs/tasks/validate-tasks.py`, `python3 implementation/scripts/check-maturity.py --verbose`,
  `node implementation/scripts/sync.mjs --root implementation --check`.

## Acceptance criteria

- [ ] `classify_k_plus_improvement_outcome()` (or equivalently named) exists in `policy.py`,
      requires `MIN_ESCALATED_K` per arm (raises otherwise), returns one of four outcomes per
      design decisions 2-4
- [ ] `CONFIRMED_POSITIVE_EFFECT` constant added, following existing naming convention
- [ ] Category-3 recurrence counted via a helper mirroring `count_cause_occurrences()`'s shape, not
      new one-off logic
- [ ] `evaluate_promotion()` requires `CONFIRMED_POSITIVE_EFFECT` on every compared case to promote
      (per design decision 5, or a disclosed, argued alternative)
- [ ] `PromotionResult` reports every case's classification, not just an aggregate boolean
- [ ] All tests listed above pass, including the real-T507-data regression test and the
      positive-path test proving promotion is still reachable in principle
- [ ] Every existing test in `test_golden_harness_policy.py`/`test_golden_harness_promotion.py`
      still passes (update fixtures only where the new conjunct genuinely requires it, disclosing
      exactly which and why, per `T510`'s own precedent)
- [ ] Full verification bar green

## Blocker protocol

Standard: `technical | dependency | unclear_requirements | external`, severities
`critical | major | minor`, max 2 retries before escalation.
