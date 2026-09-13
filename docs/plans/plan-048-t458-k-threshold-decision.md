# Plan 048 — T458 `k`/threshold: an actual decision, drawn from the combined T488+T489+T490 evidence

> Filename: `plan-048-t458-k-threshold-decision.md`

**Date:** 2026-09-13

**Status:** proposed — a decision/design document only. It does not dispatch the full 20-case
harness, any new live trial, any vault change, or any change to `docs/tasks/active-tasks.md`. It
does not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`,
`.mcp.json`, or `feature/T475-codex-platform-integration`. T456, T457, T458, and T483 remain
untouched.

**Based on:** `docs/plans/plan-047-t458-k-threshold-resolution.md` (re-read in full, fresh, from
`origin/develop` this session — the document this one supersedes on the specific questions §5
deferred, exactly as `plan-047` itself superseded `plan-045`'s deferred items); `docs/tasks/
task-T488.md`, `docs/tasks/task-T489.md`, `docs/tasks/task-T490.md` (re-read in full, fresh, from
`origin/develop` this session, not from any prior summary — the complete real evidence base this
document reasons from).

## 0. Re-verified start conditions (fresh this session, not trusted from any prior summary)

- `origin/develop` HEAD independently re-verified via `git fetch origin develop` +
  `git rev-parse origin/develop`: **`fd8a09962170f571e8044778197dd18c127561d4`**
  (`Merge branch 'agent/orchestrator/T490' into 'develop'`) — matches the instructing session's
  stated expectation exactly.
- `docs/tasks/active-tasks.md` re-read fresh from `origin/develop`: the ledger invariant holds —
  four non-terminal rows, unchanged since before T488 (`T456` blocked, `T457` pending, `T458`
  pending, `T483` pending), plus closure notes for T488/T489/T490 recorded above the table as
  prose, not as table rows. T488, T489, and T490 are `done` in `completed-tasks.md`. Nothing about
  this ledger state is modified by this document.
- Max existing plan number on `origin/develop` is `047`; this document is `plan-048`, the next
  free number.
- The current interactive-session working branch (`feature/T475-codex-platform-integration`) was
  **not touched** — this document was authored in a fresh git worktree
  (`docs-plan-048-t458-k-decision`, branch `docs/plan-048-t458-k-threshold-decision`, from
  `origin/develop` @ `fd8a099`), confirmed clean (`git status --short` empty, `git diff
  origin/develop --stat` empty) before any work began.
- `tests/golden/held-out/` re-listed fresh (6 entries) — no held-out case ID is named anywhere in
  this document; every case discussed below is one of the 6 real, `open`, non-held-out cases
  T488/T489/T490 actually dispatched against.

## 1. A correction to the instructing session's own recap, made before reasoning from it

The instructing session's restatement of T488/T489/T490 asked to be independently checked against
the real briefs rather than trusted, and two counts in it do not survive that check:

**"3 cases with real k=3 data" is undercounted — the real number is 4.** Re-deriving from the
actual briefs: `code-review-fail-blocker-details` and `security-audit-coverage-consistency` were
escalated to k=3 in T490 (2 cases); `plan-required-sections-compliant` was also escalated to k=3 in
T490, as a **reproducibility check** on its T488 clear-influence finding, not as an ambiguity
escalation (3 cases from T490's own scope); and `new-feature-plan-doc-compliant` was independently
escalated to k=3 in T489, predating T490 and plan-047's own formal escalation-rule wording. That is
**4** distinct cases with real k=3 data (`plan-required-sections-compliant`,
`new-feature-plan-doc-compliant`, `code-review-fail-blocker-details`,
`security-audit-coverage-consistency`), not 3. The remaining 2 of the 6 total cases exercised so far
(`prepare-release-changelog-grouping-compliant`, `security-audit-verdict-fields-compliant`) remain
at k=1 only, correctly un-escalated because both were unanimous (control = treatment) at k=1.

**"20 trials run so far" undercounts the real total — the real number is 28 unique live trials, of
which 26 were newly dispatched inside T488/T489/T490 and 2 (T484's control, T487's treatment) are
earlier trials T489 folds into its own k=3 tally for `new-feature-plan-doc-compliant`.** Built by
direct enumeration of every trial row in all three briefs' own tables, de-duplicating trials T490
explicitly reuses from T488 ("(T488, on record)" rows) and the trial T489 explicitly reuses from
T487/T484: T488 contributes 10 (5 cases × 2 arms, k=1), T489 contributes 4 new trials (plus the 2
reused, counted once), T490 contributes 12 new trials (plus 6 reused from T488, counted once).
10 + 4 + 12 = 26 new; +2 reused-but-real = **28 total**. This document's every count below is
derived from this 28-trial inventory, built fresh from the source tables, not asserted.

Both corrections matter for what follows: the case-count correction changes the answer to question
1 below (the escalation rule now has one more real, independent application than credited), and the
trial-count correction changes the denominator for the failure-cause and category-3 base-rate
arguments in questions 2 and 3.

## 2. The 28-trial inventory, by case, with every failure's diagnosed cause

| Case | Command / role | Control (k) | Treatment (k) | Failures (arm, cause) |
|---|---|---|---|---|
| `plan-required-sections-compliant` | `/plan`, orchestrator | 3/3 | 3/3 | none |
| `new-feature-plan-doc-compliant` | `/new-feature`, orchestrator | 3/3 | 3/3 | none |
| `prepare-release-changelog-grouping-compliant` | `/prepare-release`, orchestrator | 1/1 | 1/1 | none |
| `security-audit-verdict-fields-compliant` | `/security-audit`, security-engineer | 1/1 | 1/1 | none |
| `code-review-fail-blocker-details` | `/code-review`, tech-lead | 1/3 | 1/3 | control-2: verdict severity (`CONDITIONAL_PASS` not `FAIL`); control-3: inline-prose `Owner` field; treatment-1: `Owner` as table column header; treatment-3: inline-prose `Owner` field (same pattern as control-3) |
| `security-audit-coverage-consistency` | `/security-audit`, security-engineer | 3/3 | 1/3 | treatment-1: coverage field as bolded sentence, not literal field-label; treatment-2: matrix self-consistency slip (declared 9, matrix has 10 rows) |

**28 trials total, 6 failures (21%), 0 of 6 traced to retrieval content.** All 6 trace to one of
three mechanisms: literal-field-format non-compliance (4: `code-review` treatment-1, control-3,
treatment-3; `security-audit-coverage` treatment-1), verdict-severity disagreement (1:
`code-review` control-2), or matrix/declared-count self-consistency (1: `security-audit-coverage`
treatment-2). This is the real, re-derived version of the instructing session's claim that "every
failure traced to formatting/verdict-severity/self-consistency issues, none to retrieval content" —
the claim itself is correct; only its stated denominator (20 rather than 28) needed correcting.

## 3. Question 1 — is a uniform `k` now justified? Is the escalation rule final?

**Decision: yes, the escalation rule from `plan-047` §2 is adopted as final, with one addition
made explicit rather than left implicit, and one refinement to its post-escalation classification
step.**

The rule has two independently-testable parts, and both now have real supporting evidence, not
merely a hypothesis:

**Part A — default `k=1`, escalate only on ambiguity (arms disagree at `k=1`).** This part has
exactly 2 direct applications in the real data (`code-review-fail-blocker-details`,
`security-audit-coverage-consistency`, both of which disagreed at `k=1` in T488 and were correctly
escalated in T490) and 2 direct non-applications that the rule correctly withheld escalation from
(`prepare-release-changelog-grouping-compliant`, `security-audit-verdict-fields-compliant`, both
unanimous at `k=1`, never escalated). The cost side of the rule's own justification — that
escalating a unanimous case wastes trial budget for no return — is independently confirmed by
`new-feature-plan-doc-compliant`'s own k=3 result (T489): 6/6 trials passed, zero discriminating
signal, on a case escalated for a different original reason (T489 predates the rule's formal
wording and was framed as a noise probe, not an ambiguity escalation) but whose own result is
exactly the outcome the rule now predicts for any unanimous case. Four for four: escalate-on-
disagreement fired correctly twice, withhold-on-unanimity was correctly followed twice, and the one
case where a unanimous result was escalated anyway (for an unrelated reason) confirms in hindsight
that doing so would have been wasted budget under the rule. This is enough real, converging
evidence to call Part A decided, not hypothesized.

**Part B — post-escalation classification (same-cause recurrence = real effect; fluctuation = a
confirmed coin-flip).** `code-review-fail-blocker-details` is a clean confirmation of the
fluctuation branch: pass/fail moved in both arms across the 3 trials (control: True, False, False;
treatment: False, True, False), with the failures splitting across two distinct causes (a
verdict-severity flip and an `Owner`-field formatting flip), and the non-regression floor held
(1/3 vs 1/3). `security-audit-coverage-consistency`, however, is a genuine gap in the two-outcome
classification as originally written: it is not "same cause recurring across all `k` trials" (the
two treatment failures have two independently diagnosed causes), and it is not "fluctuates" either
(the control arm never failed once — 3/3 — while the treatment arm failed twice — 1/3). `plan-047`
itself already reported this case as "neither of the rule's two named outcomes fits cleanly," and
that gap survives independent re-verification here.

**Addition made explicit: a second, legitimate escalation trigger exists in practice and should be
named as such rather than left implicit.** T490 escalated `plan-required-sections-compliant` to
k=3 for a reason Part A's disagreement trigger does not cover — it was unanimous at k=1 (both arms
True) — specifically to test whether a *qualitative* category-3 finding (traceable positive
influence, not a pass/fail disagreement) reproduces under repetition. This produced a real,
substantive answer (it did not reproduce — see §5) that Part A's trigger, applied mechanically,
would never have surfaced, because a unanimous pass/fail result gives Part A no reason to escalate.
This document names this as **Trigger 2: reproducibility-check escalation** — escalate a case to
k≥3 regardless of its k=1 pass/fail unanimity when its k=1 result produced a qualitative category-3
(traceable positive influence) finding, specifically to test whether that influence is a stable
property of the case or a one-off. This is now a second, decided, named trigger alongside Part A's
disagreement trigger — not a hedge, a second real rule with one real supporting application.

**Refinement to Part B: add a third classification outcome.** `security-audit-coverage-
consistency`'s pattern — one arm structurally worse across k=3 trials, but via causes that don't
repeat — is real and will recur on other cases; forcing it into "coin-flip" or "confirmed bug"
misdescribes it either way. This document adds a third outcome to `plan-047` §2's rule:
**elevated-but-heterogeneous** — the treatment (or control) arm's failure rate is durably higher
than the other arm's across k≥3 trials, but the individual failures do not share a diagnosed cause.
This outcome is treated as neither "resolved as noise" nor "confirmed regression" — it is treated
as **still open**, requiring the specific additional evidence named in §6 before it can be closed
either way. `security-audit-coverage-consistency` is reclassified under this new outcome, replacing
`plan-047`'s honest-but-unresolved "fits neither" description with a named category that has a
defined next step.

**On a single fixed `k` for the full 20-case harness:** still not set as a single number, and this
document affirms `plan-047`'s reasoning that it should not be — the escalation policy itself (Part
A + Trigger 2 + the three-outcome classification) is now the decided rule, in the same sense
`plan-047` asked for: "that itself is a real k decision (a policy, not a single number, but a
decided one)." This document states plainly, per the instructing session's own framing, that this
is decided, not deferred: **default k=1 for every new case; escalate to k≥3 on k=1 arm
disagreement (Part A); separately escalate any unanimous case whose k=1 treatment trial showed a
category-3 qualitative finding, to test reproducibility (Trigger 2); classify every k≥3 result into
one of three outcomes (confirmed coin-flip / confirmed persistent effect / elevated-but-
heterogeneous, open) rather than forcing a binary call.**

## 4. Question 2 — a numeric non-regression floor tolerance

**Decision: yes, a specific tolerance is now justified, grounded in the recurrence pattern actually
observed across the 6 real failures in the 28-trial inventory (§2), not invented.**

The failure-cause data shows exactly one case where the *same* diagnosed root cause repeated across
independent trials: the inline-prose-`Owner`-field pattern in `code-review-fail-blocker-details`
(control-3 and treatment-3, independently, in different arms). Every other failure cause in the
entire 28-trial inventory occurred exactly once. This is the concrete signal the tolerance below is
built from: this evidence base has, in fact, already distinguished "a checker-brittleness pattern
real enough to recur under repetition" from "a single-trial fluke" exactly once, and the mechanism
that did the distinguishing was recurrence count, not floor-miss count.

**Tolerance rule:** a non-regression floor miss (treatment pass rate below control pass rate at
whatever `k` the escalation rule in §3 assigns) is **not, by itself, actionable/blocking**. It
becomes actionable — treated as a confirmed regression or a confirmed checker-brittleness bug
requiring a fix — **only when the same diagnosed root cause is independently observed recurring
across ≥2 trials within that case's own evidence set** (regardless of which arm each occurrence
falls in, since a cause recurring across arms, as the `Owner`-field pattern did, is stronger
evidence of checker brittleness than retrieval effect). A floor miss whose contributing failures
each have a distinct, independently-diagnosed cause occurring exactly once is held as **open, not
resolved** in either direction — not dismissed as noise, and not treated as a confirmed regression
— pending the additional trials named in §6.

Applied retroactively to the two cases that actually missed the floor at some point in this
evidence base:
- `code-review-fail-blocker-details`: floor is **met** at k=3 (1/3 vs 1/3) and the tolerance rule
  additionally confirms *why* it's safe to treat the k=1 miss as non-actionable — the recurring
  `Owner`-field cause is a real, repeat-observed checker brittleness, but it strikes both arms
  roughly evenly, so it is not a retrieval-attributable regression.
- `security-audit-coverage-consistency`: floor is **not met** at k=3 (1/3 vs 3/3), and under this
  tolerance rule it stays **open, not dismissed** — neither of its two causes has recurred a second
  time, so neither can yet be called a confirmed, stable bug, but the case cannot be waved through
  as "just noise" either, because unlike `code-review`, the *control* arm has never once failed
  across all 6 of its own trials (T488 + T490 combined) while the treatment arm has failed in 2 of
  3. This tolerance rule does not resolve this case; it correctly keeps it flagged as the one case
  in the current evidence base that still needs the specific next step named in §6.

This is a real, stated number, grounded in the actual recurrence data (1 of 6 failure causes has
recurred; 5 of 6 have occurred exactly once), not a percentage invented to flatter or worsen either
result.

## 5. Question 3 — is there a defensible base-rate statement for the qualitative rubric?

Re-deriving the population fresh: of the 14 total treatment-arm trials in the 28-trial inventory,
**11 have an explicit, source-grounded qualitative-influence classification** stated in their own
brief's text (the remaining 3 — `code-review-fail-blocker-details` treatment-2/treatment-3's
pass-only report, and `security-audit-coverage-consistency` treatment-3's pass-only report — are
not qualitatively characterized in T490's own text beyond their pass/fail outcome and are **not**
force-classified here).

| Category | Count (of 11 classified) | Trials |
|---|---|---|
| 1 — No retrieval attributable | 0 | — |
| 2 — Consulted, real content, no distinguishable influence | 5 | `prepare-release-changelog-grouping-compliant` treatment; `code-review-fail-blocker-details` treatment-1; `security-audit-coverage-consistency` treatment-1; `security-audit-coverage-consistency` treatment-2; `security-audit-verdict-fields-compliant` treatment |
| 3 — Traceable positive influence | 2 | `plan-required-sections-compliant` treatment-1 (T488 on-record); `new-feature-plan-doc-compliant` treatment-1 (T487, on-record) |
| 4 — Attempted and failed, disclosed transparently | 1 | `new-feature-plan-doc-compliant` treatment-2 |
| 5 — Attempted, no disclosure of the attempt | 3 | `plan-required-sections-compliant` treatment-2, treatment-3; `new-feature-plan-doc-compliant` treatment-3 |

**Base-rate statement (defensible, from the real count): 2 of 11 classified treatment trials
(18%) — or, conservatively including the 3 unclassified trials as non-category-3, 2 of 14 (14%) —
showed a traceable positive influence (category 3) so far.** Both category-3 occurrences were each
case's *first-ever* treatment trial. The one case where reproducibility was actually tested
(`plan-required-sections-compliant`, retested twice in T490) scored 0 of 2 on repeat — both landed
in category 5 instead. The other category-3 occurrence (`new-feature-plan-doc-compliant`
treatment-1/T487) has never been retested for reproducibility at all; T489's k=3 batch on that case
tested pass/fail noise, not whether the specific category-3 finding recurs.

This does not yet support a formal pass/fail threshold on the rubric (e.g., "≥X% of trials must
land in category 3 to count as improvement") — 11 classified observations is too small a population
to pin a proportion with any usable confidence interval, and the one reproducibility test run so
far returned 0/2, which pulls the true rate for *stable* (not one-off) category-3 findings toward
something lower than 18%, not higher. What the count does support, stated plainly: **category 3 is
real but rare in the current evidence (roughly 1 in 5 to 1 in 7 treatment trials), and where
retested for stability, it did not hold up** — this is a genuine, specific, evidence-grounded
description this project did not have before T490, and it is a meaningfully different statement
from `plan-047`'s own "T488's clear influence case" framing, which (correctly, per `plan-047`'s own
discipline) did not yet know whether that one instance was stable.

## 6. Question 4 — what would actually change this document's mind

This document's Part A/Trigger 2 escalation-rule decision (§3) is not contingent on further
evidence — it is adopted as final now. The floor-tolerance rule (§4) and the category-3 base rate
(§5) are each one additional, specific, named batch away from a fully numeric threshold — not a
generic "more data" answer:

1. **For `security-audit-coverage-consistency` specifically (the one still-open case):** 2 more
   trials per arm (reaching k=5), because it is the one case in the entire evidence base where the
   floor-tolerance rule in §4 could not yet resolve the pattern one way or the other. If either of
   its two already-diagnosed causes (the bolded-sentence field-format miss, or the matrix
   self-consistency slip) recurs a second time at k=5, that promotes it from "open" to a confirmed,
   real checker-brittleness pattern (§3's "persistent" outcome) requiring an `expect.py` or template
   fix, exactly as `code-review-fail-blocker-details`'s recurring `Owner`-field pattern already was.
   If neither recurs and a third, new, independent cause appears instead, that confirms the
   elevated-but-heterogeneous classification (§3) as this case's genuinely final state rather than
   a still-open one.
2. **For the category-3 base rate specifically:** 2 more trials on `new-feature-plan-doc-
   compliant`'s treatment arm, structured the same way T490 retested `plan-required-sections-
   compliant` — i.e., re-running its own category-3 finding (T487's branch/MR-policy bullet) to see
   whether *it* also fails to reproduce. If it does (a second 0-for-2), the true stable category-3
   rate across this evidence base drops to essentially zero reproducible instances out of two
   tested, a materially stronger and more specific finding than "rare" — it would mean every
   category-3 finding observed so far, on retest, has turned out to be a one-off. If it instead
   reproduces even once, that is the first evidence that category-3 influence can be stable on at
   least one case type, which would justify designing a dedicated case around it rather than
   treating category 3 as noise.
3. **A harder case with genuine, non-generic, vault-dependent content**, named specifically because
   both of this evidence base's category-3 findings and all of its category-2 findings share one
   property: the retrieved content was always *general good practice* (branch/MR policy, retry
   rules, verdict semantics) that a competent session could often reconstruct without retrieval —
   exactly why category 2 ("no distinguishable influence") dominates the current population (5 of
   11). None of the 6 cases run so far were authored with a fact that exists *only* in the vault and
   *cannot* be independently reconstructed (e.g., a project-specific numeric constant, a named
   internal API contract, or a specific past incident) — `plan-047` §4 named this gap without a
   concrete fix; this document makes the fix concrete: author at least one new golden case whose
   `expect.py` requires a specific fact sourced only from a vault entry, with no other plausible
   route to it, and run it at k≥3 both arms. Until this exists, this evidence base structurally
   cannot distinguish "retrieval doesn't help much" from "retrieval hasn't yet been asked to
   contribute anything a session couldn't already guess."
4. **Population size for a formal rubric threshold:** even with items 1-3 above run, a defensible
   numeric percentage-point cutoff on the qualitative rubric (e.g., "≥30% of trials must land in
   category 3") would need roughly 30-50 classified treatment trials total (versus today's 11) to
   support a confidence interval narrow enough to be worth committing to — this document does not
   claim items 1-3 alone reach that population; they are what is needed to correct the two specific
   distortions named above (an unresolved case, and an untested reproducibility gap) before that
   larger population-building effort would even be well-targeted.

## 7. What this document actually resolves, stated plainly

- **The `k` question is decided, not deferred further:** default `k=1`; escalate to `k≥3` on `k=1`
  arm disagreement (Part A, 2-for-2 confirmed, 2-for-2 correctly withheld); separately escalate any
  unanimous case whose treatment trial showed a category-3 finding, to test reproducibility
  (Trigger 2, newly named, 1-for-1 informative); classify every `k≥3` result into one of three
  named outcomes — confirmed coin-flip, confirmed persistent effect, or elevated-but-heterogeneous
  (open) — rather than forcing a two-outcome call the real data (`security-audit-coverage-
  consistency`) has already shown is sometimes wrong to force.
- **A numeric non-regression floor tolerance is set:** a floor miss is actionable only once its
  specific diagnosed cause recurs across ≥2 trials within the same case; a floor miss whose causes
  have each occurred exactly once stays open, neither dismissed nor treated as confirmed
  regression. Applied now: `code-review-fail-blocker-details` closes as resolved noise;
  `security-audit-coverage-consistency` stays open, correctly, pending item 1 in §6.
- **The "measurably improve" threshold is still not set as a numeric percentage**, but a specific,
  real base-rate statement now replaces `plan-047`'s deferral: 2 of 11 classified treatment trials
  (18%, or 14% conservatively) show traceable positive influence, and the one reproducibility test
  run so far returned 0 of 2 — both facts stated plainly, not softened.
- **What is still missing to reach a numeric threshold is named specifically, not generically:**
  items 1-4 in §6, each tied to a named case, a named trial count, and a named reason it would move
  this document's conclusions rather than merely add data.

## What this document does not resolve (explicitly deferred, not silently dropped)

- The exact numeric "measurably improve" percentage-point threshold itself — genuinely still
  deferred, to whichever document reports the results of §6 items 1-3.
- The case-hardness screening procedure `plan-047` §4 named (how to tell in advance which cases are
  "sensitive enough to show spread") — unchanged, still deferred; §6 item 3 proposes a concrete
  first instance of such a case rather than a general screening procedure.
- Any decision about `plan-045` Finding 1's shapes (b), (c), or (d) — unchanged, still deferred.
- Whether or how to grow the knowledge vault — unchanged from `plan-045` Finding 5 and `plan-047`;
  this document proposes no vault content change (§6 item 3's new case would require one, but that
  remains a separate, future dispatch decision, not made here).
- Whether `devops-engineer` should ever become the real executing owner for a harness at this
  scale, versus the orchestrator continuing to execute bounded slices directly — unchanged from
  `plan-044` Finding 3 and every successor document since.

## What this document is not

- It is not `docs/tasks/task-T458.md`'s dispatch, and it does not modify that brief.
- It is not a new task brief — no `docs/tasks/task-T4xx.md` is authored by this document, and
  `docs/tasks/active-tasks.md`/`completed-tasks.md` are untouched.
- It does not authorize any live trial, any vault-content change, or any `k`-run measurement,
  including the specific next-step experiments named in §6 — those remain separate dispatch
  decisions, not made here.
- It does not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/
  `.md`, `.mcp.json`, or `feature/T475-codex-platform-integration`.
- It does not authorize any paid/metered API usage.
- It is not an approval of `plan-040`, `plan-045`, `plan-047`, or `task-T458.md` — all remain
  exactly as found, `proposed`/`pending`, unapproved for full dispatch.
