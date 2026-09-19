# Plan 047 — T458 scaling: resolving (and partly not resolving) the `k` and threshold questions `plan-045` deferred

> Filename: `plan-047-t458-k-threshold-resolution.md`

**Date:** 2026-09-13

**Status:** proposed — a decision/design document only. It does not dispatch the full 20-case
harness, any new live trial, or any change to `docs/tasks/active-tasks.md`. It does not touch
`tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`, or
`feature/T475-codex-platform-integration`. T456, T457, T458, and T483 remain untouched.

**Based on:** `docs/plans/plan-045-t458-scaling.md` (re-read in full, fresh, from `origin/develop`
this session — specifically Finding 2's deferral of a `k` value for the full harness ("Do not
pre-commit a `k` value for the eventual 20-case full harness in this document... set it only after
Tier 2's real spread number exists") and Finding 3's deferral of a numeric "measurably improve"
threshold ("A quantitative percentage-point threshold is deliberately deferred, to be set as a
**dated successor** to this document... once Tier 1 (case breadth) and Tier 2 (the noise probe)
produce real numbers to calibrate against") — this document is that named successor);
`docs/tasks/task-T488.md` (re-read in full, fresh — the real Tier 1 results, `k=1`, 5 cases);
`docs/tasks/task-T489.md` (re-read in full, fresh — the real Tier 2 results, `k=3`, 1 case);
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (re-read fresh — the frozen-block/dated-
successor-block supersession mechanism this document's own numbering and posture mirror, though
this document is a separate numbered file rather than an appended block in `plan-045` itself,
matching how `plan-044` and `plan-045` already relate to each other as separate successor
documents); `docs/decisions/ADR-004-tb-inconclusive-guardrail-demotion.md` (re-read fresh — the
precedent for admitting an instrument is under-resolution rather than manufacturing a number to
close the gap, and for pre-committing consequences before further spend is considered).

## 0. Re-verified start conditions (fresh this session, not trusted from any prior summary)

- `origin/develop` HEAD independently re-verified via `git fetch origin develop` +
  `git rev-parse origin/develop`: **`266ec58c3071cb86227b392459266837f25fd48f`**
  (`Merge branch 'agent/orchestrator/T489' into 'develop'`).
- `docs/tasks/active-tasks.md` re-read fresh: four non-terminal rows unchanged since before T488/
  T489 (`T456` blocked, `T457` pending, `T458` pending, `T483` pending), plus closure notes for
  T488 and T489 recorded above the table. T488 and T489 are `done` in `completed-tasks.md`.
  Nothing about this ledger state is modified by this document.
- The current interactive-session working branch (`feature/T475-codex-platform-integration`, with
  its own pre-existing uncommitted changes) was **not touched** — this document was authored in a
  fresh git worktree (`docs/plan-047-t458-k-threshold`, branched from `origin/develop`), per this
  project's standing instruction to never touch that branch.
- Max existing plan number on `origin/develop` is `046` (`plan-046-t458-tier1-dispatch.md`, the
  retrospective dispatch record for T488) — this document is `plan-047`, the next free number.

## 1. What T488 and T489 actually showed, restated precisely (not overstated)

**T488 (Tier 1, `k=1`, 5 cases, all five golden-suite command families):** control 5/5, treatment
3/5. The non-regression floor (`plan-045` Finding 3) was **not met**. Both treatment shortfalls
(`code-review-fail-blocker-details`, `security-audit-coverage-consistency`) were independently
traced to per-trial formatting choices — a table-header field vs. a literal bolded field; a merged
verdict/status line vs. the template's own two-field pattern — confirmed unrelated to the
substantive content retrieval contributed. One case (`plan-required-sections-compliant`) showed a
clear, directly traceable retrieval influence (three distinct claims in a treatment-only section,
each tracing to a distinct retrieved chunk). The other two cases retrieved real, topically-relevant
content that produced no output distinguishable from what an un-retrieved control independently
produced.

**T489 (Tier 2, `k=3`, 1 case, the suite's easiest and already-proven case):** control 3/3,
treatment 3/3. Both arms sit at the metric's ceiling. T489's own text is explicit that this is
"a ceiling-effect data point, not a spread measurement" — six real trials produced zero observed
variance in the binary `expect.py` outcome. The real, measurable variance in this batch was
entirely qualitative/structural: three treatment trials, given the identical "you may consult
retrieval and use your own judgment" instruction, made three different choices about whether and
how to narrate retrieval use *inside the produced artifact itself* — one wrote a traceable
retrieval-attributable bullet into the doc; one disclosed a genuine retrieval failure transparently
in a dedicated section; one succeeded at retrieval, judged the results off-topic, and left **zero**
mention of the attempt anywhere in the artifact, with the only record of it existing in the
session's own chat transcript.

**The combined implication, already named by T489's own brief, restated here as this document's
starting premise:** binary `expect.py` pass/fail is too coarse an instrument to measure retrieval's
effect at low `k` on easy cases. At `k=1`, a single stylistic choice flips the boolean (T488). At
`k=3` on an easy, well-saturated case, the metric hits a ceiling with zero discriminating signal
(T489). Both results are real and both must be held together — they are not in tension, they are
two symptoms of the same underlying problem: **the binary metric's resolution floor is coarser
than the effect this comparison is trying to detect**, at least at the scale and on the case types
measured so far.

## 2. What this evidence does — and does not — settle about `k`

Three candidate responses to the coarseness finding were named in this document's own brief:
raise `k` (to average out formatting noise), adopt a richer scoring signal than binary pass/fail,
or select harder/more-discriminating cases. Each is examined against the actual numbers above, not
in the abstract.

**Does raising `k` fix it?** T489 is direct evidence that the answer is not simply "yes, raise
`k`, uniformly." T489 *did* raise `k` to 3, and it produced no new discriminating information —
because the case it ran on (`new-feature-plan-doc-compliant`) was already unanimous at `k=1`
across both arms (T484's control, T487's treatment) before T489 ever ran. Raising `k` cannot
create spread on a case that has none to find; it can only measure spread where spread exists.
This is not a criticism of Tier 2's design — `plan-045` Finding 2 explicitly picked "one
already-proven, cheap case" for exactly the reason of keeping the probe cheap — but it does mean
Tier 2's result answers a narrower question than "does `k=3` resolve the coarseness problem." It
answers "does `k=3` reveal variance on a case with none," and the honest answer is no, because
there was none to reveal.

**The genuinely missing experiment.** T488, not T489, is where real spread was observed — on two
specific cases (`code-review-fail-blocker-details`, `security-audit-coverage-consistency`), each
run exactly once per arm. We do not know, and cannot honestly claim to know from the data on hand,
whether either treatment failure represents:
(a) a roughly 50/50 formatting-style coin flip an individual live session makes regardless of
    retrieval, in which case a higher `k` on *these specific cases* would show a mix of pass/fail
    outcomes on both arms, converging toward a stable proportion, not a persistent one-sided
    failure; or
(b) something retrieval-adjacent that happened not to be substantively traceable in this one
    trial each but recurs more often than chance under repetition.
Both are live possibilities on the actual evidence — the diagnosis in `task-T488.md` (independently
confirmed to trace to formatting, not content) makes (a) considerably more likely than (b), but
"more likely" is not "measured," and a single trial per arm per case cannot distinguish a stable
50/50 formatting split from a one-off. **This is the concrete, specific additional evidence this
document identifies as still missing**: `k ≥ 3` per arm on the two cases that actually showed
spread in Tier 1, not a further probe of the case that already showed none.

**Does this argue for a single fixed `k` for the full 20-case harness?** No — and forcing one here
would repeat exactly the failure mode `plan-035` §2.2.1 and ADR-004 already named for a different
metric: a number that looks rigorous but was not earned by the data. The two real data points
available point in different directions on the *value* of raising `k`, precisely because they were
measured on cases in different regimes (one saturated, one showing real spread) — that is itself
informative, but it is informative about **case regime**, not about a portable scalar. A uniform
`k` applied to all 20 cases would, per T489's own finding, waste real trial budget on cases that
behave like the ceiling case (unanimous at `k=1`, no signal gained by more trials) while
under-sampling cases that behave like the two brittle T488 cases (where `k=1` cannot distinguish
noise from a real effect).

**Recommendation on `k` — an adaptive escalation rule, not a single number:**

1. **Default `k=1`** for an initial breadth pass across any new case set, matching what T488 already
   did and matching the actual cost profile plan-045 Finding 6 already established as tractable for
   this session-dispatch mechanism (unlike Terminal-Bench's containerized batch model).
2. **Escalate a specific case to `k ≥ 3` only when its `k=1` result is ambiguous** — defined
   concretely, not vaguely, as: the two arms disagree (one passes, one fails) **and** the failure
   is not yet independently diagnosed to a cause unrelated to retrieval content, or the failure
   diagnosis itself is uncertain. Once a case is escalated, run the additional trials, then
   classify: if the same arm keeps failing for the same diagnosed reason across all `k` trials,
   that is now a real, replicated finding (about the checker's brittleness to that formatting
   choice, or about retrieval, whichever it traces to); if the arms' pass/fail outcomes fluctuate
   across the additional trials, that confirms a formatting coin-flip rather than a persistent
   effect, and the case should be treated as a floor near-miss, not a real regression.
3. **Do not escalate a case whose `k=1` result is unanimous across arms** (both pass or both fail).
   T489 is direct evidence this yields no return — the resource is better spent either on
   escalating an ambiguous case elsewhere or on the case-selection work in §4 below.
4. **This still leaves the full-harness `k` genuinely unresolved as a single number**, because it
   is now explicitly a function of what each case's own `k=1` result looks like, discoverable only
   by running it — which is honest given the evidence, not evasive. What is resolved, and can be
   stated now: uniform `k=1` alone is insufficient (T488 proves it), and uniform `k=3` is not
   automatically sufficient either and is wasteful where unneeded (T489 proves it) — the two
   uniform options this project's own Terminal-Bench precedent (`plan-035` §2.4, a single frozen
   `k=3` for all subset tasks) might have suggested copying are each independently shown, by this
   project's own data, not to transfer cleanly to this metric and cost structure. That in itself is
   a real, evidence-grounded finding plan-045's Finding 2 could not have stated in advance.

## 3. What this evidence does — and does not — settle about a "measurably improve" threshold

`plan-045` Finding 3 already predicted, before any Tier 1/2 data existed, that a numeric
percentage-point threshold invented at 5-6 cases and `k=1` would be exactly the kind of
"looks rigorous, measures nothing" number this project's roadmap warns against, and that a
pass-rate-only definition of "improve" would misdescribe T487's already-observed genuine content
influence. T488 and T489 do not merely fail to resolve that prediction — they **confirm it
empirically, on both counts**:

1. **Statistical resolution, confirmed.** T488's own two failures are a direct demonstration of
   the exact 5-case, `k=1` fragility Finding 3 predicted: a single case flipping is a 20-percentage-
   point swing, and here two of five flipped for reasons having nothing to do with the thing being
   measured. Any percentage-point number set against this batch's own 3/5 would be measuring
   formatting variance, not retrieval effect.
2. **Pass-rate-only "improve" would misdescribe the real evidence, confirmed a second time.**
   T489 adds a second, independent instance of the same problem Finding 3 named for T487 alone: a
   pass-rate-only lens reports "no effect" (3/3 both arms) on a batch that in fact contained real,
   directly observable differences in how retrieval was used and disclosed across three treatment
   trials. A threshold that only reads the binary signal would call this "no change" twice now,
   not once, despite genuine, inspectable behavioral differences existing in both instances.

**Recommendation on the threshold — the process Finding 3 proposed, now confirmed and specified
further, still not reduced to an invented percentage:**

1. **The non-regression floor stands, unchanged in wording, now empirically exercised rather than
   merely stated:** treatment pass rate must not be lower than control pass rate, per case set
   actually run, using whatever per-case `k` the escalation rule in §2 assigns. T488's real
   3/5-vs-5/5 result is the floor's first real test, and it correctly flagged something worth
   investigating (the two formatting-brittle cases) rather than being silently absorbed — the floor
   is doing its job as a trip-wire, not as a final verdict, exactly as Finding 3 intended.
2. **The qualitative signal is promoted from "supplementary" to co-primary, because the evidence now
   shows it is where the real information already lives.** Every substantive, non-formatting
   finding in both T488 and T489 came from the manual, traceable-diff method T487 originated, not
   from the binary metric: T488's one clear influence case, and T489's three-way disclosure-pattern
   difference. This document recommends formalizing that method into a small, fixed rubric — seeded
   directly from the categories T487-T489 already produced in practice, not invented — so it stops
   being an ad hoc narrative and becomes a comparable, per-trial classification:
   - **No retrieval attributable** — retrieval not consulted, or consulted with no discernible
     effect on output (T488 cases 2, 5; T489 control arm, trivially, since it never has retrieval).
   - **Retrieval consulted, real content returned, output not distinguishable from an unretrieved
     baseline** (T488 cases 2, 5 more specifically — real, topically-relevant hits, no
     distinguishable influence on the written artifact).
   - **Retrieval used, traceable positive influence on the artifact** (T488 case 1; T489's
     treatment-1/T487).
   - **Retrieval attempted and failed, disclosed transparently in the artifact itself** (T489's
     treatment-2).
   - **Retrieval attempted and either succeeded or failed, with no disclosure of the attempt
     anywhere in the artifact** (T489's treatment-3) — flagged as its own category specifically
     because it is a real, disclosed transparency gap distinct from the outcome of the retrieval
     itself, and one this evidence shows occurs even under an explicit "report verbatim whether you
     queried" instruction to the underlying session.
3. **A numeric percentage-point threshold on either the pass-rate floor or the qualitative rubric is
   still not set by this document.** Setting one now, even having confirmed Finding 3's predicted
   failure mode twice, would still mean picking a number off two small, non-uniform-`k`, non-
   uniform-difficulty batches — the exact thing Finding 3, `plan-035` §2.2.1, and ADR-004 all argue
   against. What is different from `plan-045`'s own framing is that the missing evidence is now
   named specifically, not generically: a qualitative-rubric base rate needs at least one batch of
   cases run at the escalated `k` from §2 (the two brittle T488 cases, plus a repeat of the one
   clear-influence case to see whether that influence reproduces under repetition or was itself a
   one-off), classified under the rubric above, before a "what fraction of cases must show a
   traceable positive influence to count as improvement" number can be set honestly.

## 4. Case selection — a real, distinct axis from `k`, and also not yet resolved

`plan-045` Finding 1 already flagged that the easiest 5-6 cases (shape (a)) were deliberately
chosen for cheapness, and Finding 5 predicted (incorrectly, as T488 showed — every query's top hit
was a real, relevant vault entry across all 5 cases) that vault coverage would be thin for the new
cases. Neither finding anticipated the specific problem T489 surfaced: that the *original* case
(`new-feature-plan-doc-compliant`) is not merely easy in the sense of "cheap to author a fixture
for," but easy in the more consequential sense of being **saturated** — unanimous across every
arm and every trial run against it so far (T484, T487, T489 ×4 — six trials, zero disagreement).
A case that behaves this way cannot function as this project's calibration case for `k`, because
there is structurally nothing for a higher `k` to find on it. The two T488 cases that showed real
spread did so not because they were selected for difficulty (they were selected, per Finding 1, for
being the same cheap shape as the others) but incidentally, because their `expect.py` checks happen
to be more format-sensitive than the others' — a property of the checker, discovered empirically,
not something Finding 1's case-selection criteria screened for in advance.

**Recommendation:** any future case-diversity or `k`-calibration work should explicitly distinguish
two different properties that this evidence shows do not correlate the way one might assume:
"cheap/easy to author a fixture for" (Finding 1's actual selection axis) and "sensitive enough to a
manipulation to produce measurable spread" (the property that actually matters for calibrating `k`
or a threshold, and one Finding 1 did not screen for because it could not have been known without
running trials first). This document does not propose a new case-selection procedure to detect the
second property in advance — doing so honestly would likely require deliberately probing several
cases' `expect.py` implementations for format-sensitivity before any live trial, which is new scope
beyond what this document was asked to resolve. It is named here as a second concrete piece of
missing evidence, alongside the `k`-escalation experiment in §2.

## 5. What this document actually resolves, stated plainly

- **A single fixed `k` for the full 20-case harness is not set, and should not be** — not because
  the question was ducked, but because the two real data points on hand actively demonstrate that
  neither of the two "obvious" uniform choices (`k=1`, or a Terminal-Bench-style `k=3` for
  everything) is well-supported: `k=1` is shown insufficient (T488), and `k=3` is shown to yield
  zero return when applied to a case with no spread to find (T489).
- **What is set instead is a concrete escalation rule** (§2): default `k=1`, escalate to `k≥3` only
  on cases whose `k=1` result is ambiguous by the stated definition, don't escalate cases with
  unanimous `k=1` results. This is a real decision, not a further deferral — it is falsifiable and
  actionable the next time any Tier 1-shaped batch runs.
- **A numeric "measurably improve" threshold is still not set**, for the same reason plan-045
  originally deferred it, now with direct empirical confirmation rather than prediction alone. What
  is set instead is a concrete, five-category qualitative rubric (§3.2), seeded from real prior
  results rather than invented, promoted to co-primary status alongside the (unchanged)
  non-regression floor.
- **The single most valuable next experiment this document identifies, specifically** (not a
  generic "more data needed"): `k ≥ 3` per arm on `code-review-fail-blocker-details` and
  `security-audit-coverage-consistency` (the two cases that actually showed spread in T488), to
  determine whether their treatment failures are a stable formatting coin-flip or a persistent
  pattern — plus a repeat of `plan-required-sections-compliant`'s clear-influence trial at
  `k ≥ 3` to test whether that influence reproduces. This document does not dispatch that
  experiment; it names it as the concrete evidence a future dispatch would need to produce before
  either a numeric `k` or a numeric threshold could be set without repeating the mistake this
  document was written to avoid.

## What this document does not resolve (explicitly deferred, not silently dropped)

- The exact case-hardness screening procedure named in §4 (how to tell in advance which cases are
  "sensitive enough to show spread" rather than discovering it after the fact).
- Any decision about shapes (b), (c), or (d) from `plan-045` Finding 1 — unchanged, still deferred.
- Whether or how to grow the knowledge vault — unchanged from `plan-045` Finding 5; this document
  proposes no vault content change.
- The eventual numeric "measurably improve" threshold itself — still deferred, now to whichever
  document reports the results of the §2/§5 escalation experiment on the two brittle cases plus the
  repeated clear-influence case.
- Whether `devops-engineer` should ever become the real executing owner for a harness at this
  scale, versus the orchestrator continuing to execute bounded slices directly — unchanged from
  `plan-044` Finding 3 and `plan-045`'s own unresolved item.

## What this document is not

- It is not `docs/tasks/task-T458.md`'s dispatch, and it does not modify that brief.
- It is not a new task brief — no `docs/tasks/task-T4xx.md` is authored by this document, and
  `docs/tasks/active-tasks.md`/`completed-tasks.md` are untouched.
- It does not authorize any live trial, any vault-content change, or any `k`-run measurement,
  including the specific escalation experiment named in §5 — that remains a separate dispatch
  decision, not made here.
- It does not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/
  `.md`, `.mcp.json`, or `feature/T475-codex-platform-integration`.
- It does not authorize any paid/metered API usage.
- It is not an approval of `plan-040`, `plan-045`, or `task-T458.md` — all remain exactly as found,
  `proposed`/`pending`, unapproved for full dispatch.
