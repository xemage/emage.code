# Promotion "Improvement" Conjunct Hardening — Design Pass (T509)

**Status:** Proposed (design-only pass — no `promotion.py`/`policy.py`/`schema.py`/test-file change;
no decision made on which option to build; all deferred, see §6).
**Owner:** solution-architect
**Task:** T509
**Based on:**
- `docs/tasks/task-T509.md` (this task's own brief) — read in full; its root-cause framing and its
  four candidate options are treated as a starting hypothesis to verify, not a pre-verified
  citation, per the brief's own explicit instruction and the `T508` precedent it names.
- `implementation/runtime/golden_harness/policy.py` (read in full this session, current source) —
  `floor_met()` (lines 59-62), `classify_k_plus_outcome()` (lines 82-112), `_require_min_k()`
  (lines 115-120), `is_floor_miss_actionable()`/`count_cause_occurrences()` (lines 65-79),
  `should_escalate()` (lines 40-50), `compute_base_rate()` (lines 131-152), `MIN_ESCALATED_K = 3`
  (line 23).
- `implementation/runtime/golden_harness/promotion.py` (read in full this session, current source) —
  `evaluate_promotion()` (lines 198-249), `check_no_critical_regression()` (lines 69-146),
  `_build_promotion_reason()` (lines 170-195).
- `implementation/runtime/golden_harness/schema.py` (read in full this session, current source) —
  `TrialRecord` (lines 47-88) and its field-semantics docstring (lines 8-26); confirmed there is no
  provenance-of-trial field anywhere in the schema.
- `docs/artifacts/t507-closed-loop-cycle-v1.md` (read in full this session) — the real, disclosed
  evidence this design responds to; §3.1, §3.3, §3.5, §3.6, §3.7 are load-bearing for this document.
- `docs/plans/plan-048-t458-k-threshold-decision.md` (read in full this session) — the decided
  policy `policy.py` implements; §3-§5 establish that `MIN_ESCALATED_K`, the three-outcome
  regression classification, and the qualitative `category` rubric (including its own documented
  finding that category-3 did not reproduce on retest, 0 of 2) are all real, prior, decided
  infrastructure this design should build on rather than duplicate.
- `docs/artifacts/security-engineer-audit-server-design-v1.md` (T496) — structural precedent this
  document mirrors (explicit options with trade-offs, a labeled, non-binding recommendation, a
  concrete acceptance-criteria sketch, an explicit "what this document does not decide" section).

---

## 0. Scope of this document

This is a design artifact only. It does not modify `promotion.py`, `policy.py`, `schema.py`, or any
test file; it does not decide which option (if any) gets implemented; it does not authorize any
future implementation task's dispatch. It answers `task-T509.md`'s four required elements: a
verified root-cause framing, at least two evaluable hardening options, a labeled recommendation, and
an acceptance-criteria sketch — including the brief's explicit question of whether the fix should
extend to `check_no_critical_regression` too.

## 1. Root-cause framing, independently verified

### 1.1 The brief's core claim, confirmed exactly as stated

`floor_met()` (`policy.py` lines 59-62) is:

```python
def floor_met(control_trials, treatment_trials) -> bool:
    return pass_rate(treatment_trials) >= pass_rate(control_trials)
```

a **non-strict** `>=` comparison, taking whatever `list[TrialRecord]` is handed to it, with **no**
call to `_require_min_k` and **no** awareness of `MIN_ESCALATED_K` at all. `evaluate_promotion()`
(`promotion.py` line 231) calls it directly: `floor_ok = policy.floor_met(control_trials,
treatment_trials)`. There is no gate anywhere between a caller's raw trial lists and this
non-strict-`>=` test. The brief's claim that this is "not a bug against its own spec" is also
confirmed: `floor_met()`'s docstring cites `plan-048` §4 verbatim ("the non-regression floor is met
when the treatment arm's pass rate is not below the control arm's"), and `plan-048` §4 (re-read
directly, not from the brief's paraphrase) does define exactly that test, with the *actionability*
of a floor **miss** gated by the recurrence rule (`is_floor_miss_actionable`) — but says nothing
about gating a floor **met** result on evidence volume. `floor_met()` is a faithful implementation of
a regression floor; `promotion.py` repurposes it, unmodified, as the sole test for "improvement,"
which it was never designed to detect. Confirmed as stated.

### 1.2 A sharper, additional finding the brief did not fully state: pooling across cases

`evaluate_promotion()` passes its *entire* `control_trials`/`treatment_trials` arguments — which, per
`check_no_critical_regression()`'s own `_group_by_case()` step immediately below it in the same
function, can and typically do span **multiple distinct `case_id`s** — straight into `floor_met()`
as one pooled list each. `pass_rate()` (`policy.py` line 56) computes `sum(result)/len(trials)` over
whatever it is given, with no per-case grouping at all. So conjunct 1's evidentiary unit is not "one
case, replicated," it is "however many trials, across however many unrelated cases, happen to be in
the caller's combined list" — a materially different (and weaker) evidentiary unit than conjunct 2
uses.

This is directly demonstrated, not hypothetical: T507's real pooled arrays were exactly 3 trials per
arm — **one trial each from three different cases** (`code-review-conditional-pass-conditions-gap`,
`prepare-release-conditional-pass-conditions-gap`, `HO-2`), k=1 per case per arm. `pass_rate` on
`[True, False, True]` (control) vs `[True, True, True]` (treatment) gives exactly the reported
66.7%/100%.

**This matters concretely for evaluating Option A below.** A careless reading of "require >= 3
trials before promoting" as a pooled, case-agnostic count would **not** have prevented T507's
promotion — T507's pooled arrays already had exactly 3 trials per arm, satisfying a naive `len(trials)
>= MIN_ESCALATED_K` check, even though every individual case had exactly k=1, zero replication. A
correct minimum-evidence gate must be **per-`case_id`**, mirroring `check_no_critical_regression`'s
own `_group_by_case()` step, not a check on the raw pooled list length. This is a load-bearing
correction to how the brief's own Option-A candidate must be built, not just a restatement of it.

### 1.3 A second sharper finding: the "asymmetry" claim is only half true

The brief's compounding factor 1 states "the codebase already has a higher evidentiary bar for
detecting harm than for detecting benefit," citing that `check_no_critical_regression` requires
`MIN_ESCALATED_K` before classifying a *confirmed* regression. Re-reading `check_no_critical_
regression()` directly (lines 123-138) shows this is **only true once a case has actually reached
k>=3 in both arms**. For any case where **neither** arm reaches `MIN_ESCALATED_K` (line 138's own
comment: `# else: neither arm escalated for this case -- vacuously fine`), conjunct 2 treats that
case as **vacuously non-regressing** — permissively, exactly the same shape of "thin evidence treated
as sufficient" that the brief criticizes conjunct 1 for. T507's real regression-conjunct result
confirms this directly: `no_critical_regression: True (no case reached k>=3 in either arm; vacuously
satisfied)` (`t507-closed-loop-cycle-v1.md` §3.6). **The three-outcome classification rigor
(`classify_k_plus_outcome`) is real and is genuinely absent on the improvement side — but it only
ever *fires* once a case is already escalated to k>=3, and nothing in the current codebase requires
escalation to happen before a promotion can be granted.** Both conjuncts are equally permissive at
k<3 today; conjunct 2's extra rigor is real but conditional on an escalation trigger
(`should_escalate`) that this task's own evidence shows is not itself required before `promote=True`
can fire. This refines "the regression side already has a higher bar" to the more precise: **the
regression side has a higher bar for cases that happen to already be escalated, but the closed loop
currently has no requirement that any case be escalated at all before a promotion decision is
trusted, and this gap is present in both conjuncts, not conjunct 1 alone.**

### 1.4 Refined root-cause statement

`evaluate_promotion()`'s three-conjunct rule treats a promotion decision as valid at whatever
evidentiary depth (`k`) the caller happened to supply, for both conjuncts, with no floor on `k` and
no per-case evidentiary decomposition for conjunct 1 specifically. `floor_met()` additionally
conflates "improvement" with "not measurably worse," a test it was correctly designed for
(regression-floor checking) and incorrectly reused for (improvement detection) — a causally inert
proposal reliably clears it whenever noise or an asymmetric-evidence-collection artifact nudges a
thin, pooled, cross-case aggregate upward, exactly as T507 demonstrated. Separately, and
orthogonally, neither conjunct is aware of **how** any given trial's data was produced (fresh
dispatch vs. reused historical record) — `TrialRecord` (`schema.py`) carries no such field — so
`evaluate_promotion()` cannot detect or flag a comparison whose apparent effect is actually explained
by a provenance mismatch across arms, the second, independent mechanism T507 §3.5 disclosed for the
same false promotion.

## 2. Options

### Option A — Per-case minimum-evidence gate

Require every `case_id` present in a promotion-relevant comparison to reach `policy.MIN_ESCALATED_K`
in **both** arms before `evaluate_promotion()` can return `promote=True` — applied per case (per
§1.2's correction), not as a pooled trial count. Concretely: a new function, grouping trials by
`case_id` (reusing `check_no_critical_regression`'s existing `_group_by_case` pattern), that
classifies each case as `escalated` (both arms >= k) or `insufficient_evidence` (either arm < k), and
requires zero `insufficient_evidence` cases before conjunct 1 (or, per §3 below, the whole
promotion) can fire.

**Trade-offs:**
- *For:* Directly closes the exact gap T507 hit (all 3 cases were k=1, none escalated). Small,
  additive implementation surface — reuses `MIN_ESCALATED_K` and the existing per-case grouping
  pattern verbatim, no new constants or schema fields.
- *Against:* Raises the live-trial budget of every future closed-loop cycle substantially — every
  case must reach k=3 in both arms before any promotion is possible, a 3x-or-more increase in
  dispatch cost per cycle versus today's k=1 default. Purely quantitative: even at k=3, if every
  trial in one arm shares the same provenance-driven bias (§2.3), the gate adds real evidence volume
  but does not by itself distinguish "genuine proposal effect" from "systematic collection artifact."
  It also does not, by itself, give conjunct 1 any qualitative signal — a case reaching k=3 by pure
  luck (3/3 pass in treatment, 2/3 in control, no diagnosable reason) still clears a bare `floor_met`
  re-check with no classification rigor at all.

### Option B — Symmetric "confirmed positive effect" classification, reusing the existing `category` rubric

Add a classification function parallel to `classify_k_plus_outcome()`, applied once a case is
escalated (implying Option A's gate as a precondition — see interaction note below), that requires
not just `floor_met()` but a **qualitative, traceable** signal: `TrialRecord.category ==
CATEGORY_TRACEABLE_POSITIVE_INFLUENCE` ("3") recurring across `>= 2` of the case's treatment trials
— mirroring `is_floor_miss_actionable`'s existing `>= 2` recurrence rule, applied to `category`
instead of `diagnosed_cause`. Three symmetric outcomes: `CONFIRMED_POSITIVE_EFFECT` (floor met AND
category-3 recurs `>=2`), `CONFIRMED_COIN_FLIP` (floor met, no recurring category-3 — the existing
constant, reused, not renamed), and (for a case that misses the floor, already conjunct 2's concern)
no new outcome needed here.

**Verification that this infrastructure already exists and is not a new concept:** `category` and
`CATEGORY_TRACEABLE_POSITIVE_INFLUENCE = "3"` are both already real, defined fields (`policy.py` line
25, `schema.py` line 40), already used by `should_escalate()`'s Trigger 2 and by
`compute_base_rate()`. `plan-048` §5 (re-read directly) already computed a real base rate for this
exact category **and already found it did not reproduce on the one retest performed**: "the one
reproducibility test run so far returned 0 of 2." `evaluate_promotion()` currently never reads
`TrialRecord.category` at all — conjunct 1 is purely a pass/fail statistic, strictly weaker than the
qualitative signal the codebase already collects and already has one disclosed, cautionary finding
about.

**Trade-offs:**
- *For:* Gives conjunct 1 the same architectural rigor conjunct 2 already has (a named,
  multi-outcome classification, not a bare boolean), using a field (`category`) that already exists
  in the schema — zero schema changes required. It would have independently prevented T507's
  promotion: none of T507's treatment trials were qualitatively categorized at all (`t507-closed-
  loop-cycle-v1.md` §3.3's table has no `category` column populated), so `CONFIRMED_POSITIVE_EFFECT`
  could not have fired regardless of the floor result.
- *Against:* `category` is populated by qualitative, currently manual (human/LLM-judgment) rubric
  application to a trial's own transcript, not a mechanical check — this option's rigor is only as
  good as that judgment call's own reliability, and `plan-048` §5's disclosed 0-of-2 retest result
  means the current empirical base rate for a *reproducible* category-3 finding is low. In practice
  this option is a genuinely conservative bar: given today's evidence base, few real proposals would
  currently qualify as `CONFIRMED_POSITIVE_EFFECT`, which is arguably correct (it should be hard to
  confirm a real improvement) but is a real velocity trade-off the recommendation in §4 weighs
  explicitly. It also depends on trials actually being qualitatively categorized at dispatch time —
  a process discipline requirement, not just a policy-function change; a case whose trials are never
  categorized (like all of T507's) can never reach `CONFIRMED_POSITIVE_EFFECT` even if a real
  improvement occurred, which could produce false negatives absent that process discipline.

### Option C — Provenance-homogeneity requirement

Add a provenance field to trial records (e.g. `TrialRecord.provenance: Literal["fresh", "reused",
"unknown"]`, default `"unknown"` for backward-compatible deserialization of any already-persisted
record) and a comparison-level check — mirroring `check_no_critical_regression`'s existing
`known_arm_agnostic_case_ids` override pattern exactly — that fails closed by default: a case whose
control-arm and treatment-arm trials do not share uniform provenance (or where either arm's
provenance is `"unknown"`) is flagged as provenance-mismatched and blocks `promote=True` unless the
caller explicitly supplies the case's id in a `known_compatible_provenance_case_ids` override,
analogous to today's `known_arm_agnostic_case_ids`.

**Trade-offs:**
- *For:* Directly targets the second, independent mechanism T507 §3.5 disclosed (reused-historical
  control vs. freshly-dispatched treatment, a real prompt-fidelity confound, not a proposal effect).
  Reapplied to T507's real numbers: both open-suite cases mix `reused` control / `fresh` treatment;
  with no override supplied, this option alone — independent of Options A/B — would have flagged
  those two cases and blocked the promotion. Stylistically consistent with the codebase's existing
  fail-closed, human-attestation-required override convention.
- *Against:* Requires an actual `schema.py` field addition — `to_dict`/`from_dict` must be updated,
  and every already-persisted historical `TrialRecord` (e.g. the ones `t507-closed-loop-cycle-v1.md`
  §3.3 cites from `baseline-v6.17.0-retrieval.md`) predates this field and must deserialize to
  `"unknown"`, which this design deliberately treats as mismatched-by-default rather than
  compatible-by-default (a real, disclosed design choice: permissive-by-default on unknown
  provenance would silently reopen exactly the gap this option exists to close). This also adds a
  manual data-entry burden on every future live dispatch — whoever produces a `TrialRecord` must
  correctly tag its provenance, a process-discipline requirement with no automated verification
  path proposed here (a mis-tagged `"fresh"` record claiming to be `"reused"`, or vice versa, is not
  detectable by this check).

### Interaction between options

The three options are not mutually exclusive; each independently would have prevented T507's actual
false promotion (Option A: no case reached k=3; Option B: no case was ever qualitatively
categorized; Option C: two of three cases mixed provenance across arms), but each targets a
**different** failure mode and none subsumes the other two. A future proposal could plausibly (a)
reach k=3 with homogeneous provenance but never get qualitatively categorized (Option B still
needed), (b) get a real, recurring category-3 finding but only at k=1 (Option A still needed), or (c)
reach k=3 with real category-3 recurrence but via a provenance-mismatched comparison (Option C still
needed). Option B's classification function structurally presupposes Option A's k>=3 gate (a
`>=2`-of-3 recurrence claim is meaningless below k=3), so if B is pursued, A should be built first or
alongside it, not skipped.

## 3. Should this extend to `check_no_critical_regression` too?

**Recommendation: provenance-homogeneity (Option C) should extend to the regression conjunct;
the minimum-evidence question is, on inspection, already a promotion-level (not conjunct-1-only)
concern per §1.3, not a separate extension decision.**

**Provenance, argued directly:** `check_no_critical_regression` has exactly the same structural blind
spot as conjunct 1 — it groups trials by `case_id` and classifies outcomes purely from `result`/
`diagnosed_cause`, with no awareness of how any trial was produced. A provenance mismatch could
equally produce a **false regression alarm** (control reused from an easier historical dispatch
context, treatment freshly dispatched under a harder one, making treatment look worse than it
structurally is) or **mask a real regression** (the reverse arrangement). The second failure mode —
a masked regression — is arguably more safety-critical than conjunct 1's failure mode, since
conjunct 2 is the harness's dedicated harm-detection gate; the case for symmetry here is if anything
stronger than for conjunct 1. This design recommends implementing provenance-homogeneity **once, as
a single shared pre-check** consumed by both conjuncts (mirroring `context_retriever.py`'s
single-choke-point discipline, already cited as this codebase's own precedent in
`security-engineer-audit-server-design-v1.md` §0) — not duplicated as two separate implementations
inside `floor_met`-adjacent code and `check_no_critical_regression` independently.

**Minimum evidence, reframed per §1.3:** the brief poses this as "does the regression side need
extending too," but §1.3's finding shows the regression side's vacuous-pass-at-k<3 behavior is
already exactly the same shape of gap. This design recommends **not** treating Option A as a
conjunct-1-local patch, but as a single promotion-level precondition: *"every `case_id` present in
the compared trial set must reach `MIN_ESCALATED_K` in both arms before `evaluate_promotion()` can
return `promote=True` at all”* — evaluated once, ahead of both conjuncts, rather than bolted onto
conjunct 1 alone while conjunct 2 keeps its own independent vacuous-pass path. This both closes
T507's specific finding and closes the previously unstated, equally-real low-evidence gap on the
regression side identified in §1.3.

## 4. Recommendation (recommendation only — not a decision)

This is the solution architect's own recommendation; per this task's constraints and this project's
Plan-Approve-Execute discipline, the choice of which option(s) to build belongs to the user, exactly
as `T496`'s Option A/B/C framing did.

**Recommended: build Options A and C together as a first increment (a promotion-level minimum-
evidence gate, applied per-case, plus a shared provenance-homogeneity pre-check consumed by both
conjuncts), and treat Option B as a deliberately separate, second increment.**

Rationale: A and C are both schema-light-to-schema-moderate (A needs no schema change; C needs one
additive, backward-compatible field), both directly and independently close T507's two disclosed
mechanisms, and both would have blocked T507's real promotion on their own. B is real and valuable
but depends on a process-discipline change (consistent qualitative categorization at dispatch time)
that neither A nor C requires, and B's own conservative bar (per §2's trade-off discussion) means its
absence does not leave the loop unsafe if A and C are in place — a thin, non-escalated, or
provenance-confounded comparison is already blocked by A/C regardless of whether it also lacks a
qualitative signal. B is best sequenced as a follow-up once A/C's process impact (increased trial
budget, provenance-tagging discipline) has been observed in at least one more real cycle.

## 5. Acceptance-criteria sketch (for a future implementation task brief)

This sketch assumes the §4 recommendation (A+C first); it can be trivially re-scoped by a future
implementer/orchestrator if the user chooses a different combination — each numbered item below is
already tagged by which option it belongs to.

1. **[A]** A new `policy.py` (or `promotion.py`) function, e.g. `check_minimum_evidence(control_trials,
   treatment_trials) -> EvidenceCheckResult`, grouping by `case_id` (reusing `_group_by_case`'s
   existing pattern) and reporting, per case, whether both arms reached `MIN_ESCALATED_K`; a
   `NamedTuple` result (not a bare bool), matching this codebase's existing `RegressionCheckResult`/
   `PromotionResult` convention of always reporting *which* case(s) failed, never just a boolean.
2. **[A]** `evaluate_promotion()` gains a new precondition, evaluated before (or alongside)
   conjuncts 1-2: `promote=False` with a `reason` naming every `case_id` with insufficient evidence,
   if any exists — independent of what `floor_met`/`check_no_critical_regression` would otherwise
   return for that same data.
3. **[A]** A unit test that reconstructs T507's real numbers (3 cases, k=1 per arm each, control 2/3
   pooled / treatment 3/3 pooled) and asserts `evaluate_promotion()` now returns `promote=False` with
   an `insufficient_evidence`-naming reason — a regression test pinned to the real, disclosed
   incident, not a synthetic case invented for the test alone.
4. **[A]** A unit test confirming a **naive pooled-count** implementation would *not* catch this
   (i.e., a test asserting the gate is per-`case_id`, not `len(trials) >= MIN_ESCALATED_K` on the
   raw pooled list) — directly encodes §1.2's finding so a future refactor cannot silently regress
   to the naive, insufficient form.
5. **[C]** `schema.py`: `TrialRecord` gains a `provenance` field (name/exact literal values are an
   implementation-task decision, not fixed by this sketch) defaulting to an explicit "unknown" value
   on `from_dict()` for any record lacking the key, preserving deserialization of every existing
   persisted record without silently mis-tagging it as `"fresh"` or `"reused"`.
6. **[C]** A new shared pre-check (e.g. `check_provenance_homogeneity(...)` in `promotion.py`),
   grouped by `case_id`, fail-closed by default (mismatched or `"unknown"`-provenance arms block),
   with a `known_compatible_provenance_case_ids` override parameter mirroring
   `known_arm_agnostic_case_ids`'s exact signature/semantics (frozenset of case ids, explicit,
   caller-supplied, never inferred).
7. **[C, extends conjunct 2 per §3]** `evaluate_promotion()`'s call to `check_no_critical_regression`
   and its own floor/evidence checks both consume the **same** `check_provenance_homogeneity()`
   result — implemented once, not duplicated — and `PromotionResult` gains a
   `provenance_homogeneous: bool` field plus a `provenance_mismatched_case_ids: tuple[str, ...]`
   field, following the existing `confirmed_regression_case_ids`/`mismatched_escalation_case_ids`
   naming convention.
8. **[C]** A unit test reconstructing T507's real provenance pattern (2 of 3 cases: reused control /
   fresh treatment; 1 of 3 cases: fresh/fresh) and asserting the new check flags exactly the 2
   mismatched cases and blocks `promote=True` with no override supplied.
9. **[A+C combined]** An end-to-end unit test combining both new preconditions against T507's full
   real dataset (`t507-closed-loop-cycle-v1.md` §3.3's table, transcribed as literal `TrialRecord`
   fixtures) confirming `evaluate_promotion()` now returns `promote=False`, with both the
   insufficient-evidence and provenance-mismatch reasons present in `PromotionResult.reason`.
10. **[Process]** `t507-closed-loop-cycle-v1.md` itself (or a superseding note) is updated to record
    that a subsequent implementation task closed the gap it disclosed — mirroring how `T496`'s
    closure note in `completed-tasks.md` names the implementation task (`T497`) that built from it.
    This item is explicitly a documentation/ledger follow-up, not a code acceptance criterion, and
    belongs to whichever task actually implements this design, not to this design pass.
11. **[Deferred, Option B]** If/when Option B is separately authorized: a
    `classify_k_plus_improvement_outcome()` function and `CONFIRMED_POSITIVE_EFFECT` constant, unit
    tests mirroring `classify_k_plus_outcome`'s existing test coverage (once located — this design
    pass did not have directory-listing access to confirm the exact existing test file path for
    `policy.py`/`promotion.py`; the future implementation task should locate and extend it directly,
    not assume a path).

Every item above should be independently verifiable by a reviewer without needing to trust this
document's own framing — each cites the exact existing function/pattern it mirrors or extends.

## 6. What this document does not decide

- Which option(s) (A, B, C, or some subset/combination) actually get implemented — reserved for the
  user, per this task's own constraint.
- The exact new field names, constant names, or `NamedTuple` shapes proposed in §5 — sketched at the
  level of "what must exist and why," not fixed as final API surface; a future implementation task
  has latitude on naming as long as the behavior matches.
- Whether `MIN_ESCALATED_K`'s current value (3) itself should change — out of scope; this design
  only proposes *requiring* that threshold be reached before promoting, not changing its value.
- Whether the existing `should_escalate()` trigger logic (Part A / Trigger 2) needs any change to
  make cases reach k>=3 more often in practice — a related but distinct question this design does
  not address; today, nothing *requires* a case to be escalated past k=1 before a comparison is
  reported as "done," and Option A's gate would mean such a comparison simply cannot promote, not
  that it would automatically trigger further dispatch. Whether the closed loop should also gain an
  automatic "keep dispatching until every case reaches k>=3" behavior is a separate, future design
  question, not decided or scoped here.
- This task does not decide whether the closed loop is "trusted" for a real merge decision going
  forward — unchanged from the brief's own explicit constraint.

## 7. Blockers

None. This design pass was completed without needing to block: the brief's own citations were
verified directly against current source and found accurate (with the two refinements in §1.2-§1.3
added, both consistent with, not contradicting, the brief's framing), and the required design
elements (root-cause framing, >=2 options with trade-offs, a labeled recommendation, the regression-
side extension question, and an acceptance-criteria sketch) are all produced above. One minor,
disclosed limitation: this session had no directory-listing tool available in this environment, so
§5 item 11 could not confirm the exact existing test-file path for `policy.py`/`promotion.py`'s
current test coverage — flagged explicitly in that item rather than guessed at.
