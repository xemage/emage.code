# Baseline v6.17.0 — Retrieval-Enabled Golden Suite Measurement (T456)

**Based on:** `docs/tasks/task-T456.md` (pre-registered ship-gate threshold and run scope,
committed 2026-09-17 before any new trial was dispatched — see that file's "Pre-registered
ship-gate threshold" / "Pre-registered run scope" / "Held-out isolation guard" sections);
`docs/plans/plan-048-t458-k-threshold-decision.md` §7 (the k/escalation/floor-tolerance
policy this measurement applies, implemented as `implementation/runtime/golden_harness/policy.py`);
`docs/benchmarks/baseline-v6.12.0.md` (T414, the Phase 1 static-scorecard baseline this
document is downstream of, per `plan-035`'s literal ship-gate wording); `implementation/runtime/
golden_harness/` (T458, the live-execution harness used for every new trial in this document).

**Status:** Complete measurement. **Verdict: NO-SHIP** against the literal, pre-registered
threshold — reported plainly, per this task's own "no fabricated pass" discipline. See
"Root-cause analysis" below for what is actually driving the miss; that analysis is disclosed
as context, not used to override the pre-registered verdict.

## 1. What this document measures

Re-runs the Phase 1 golden-suite baseline concept — but, unlike `baseline-v6.12.0.md` (a static
`scripts/scorecard.py` run with no live model completion at all, per `golden-suite-format-v1.md`
§2.2's deliberate Phase 1 design), every result below comes from a **real, live-dispatched
control/treatment trial pair**, scored by the real, unmodified `expect.py` for each case via
`implementation/runtime/golden_harness/scoring.py`. Control arm: no `@context-retriever`
available. Treatment arm: `@context-retriever` available via its real CLI invocation shape
(`docs/artifacts/context-retriever-v1.md` §1), against a freshly-built, real memory index (25
chunks, 11 entries — byte-for-byte reproducing `T486`/`T487`'s historical manifest numbers).

## 2. Scope: 20 golden cases, 19 with live-trial data

- **6 cases** had real historical live trials already on record (`T484`, `T487`–`T490`,
  `T493`–`T494`) and were **not re-trialed** — their existing results are folded into this
  document's aggregate as-is (backfilled into a local `TrialRecord` store): `plan-required-
  sections-compliant`, `new-feature-plan-doc-compliant`, `prepare-release-changelog-grouping-
  compliant`, `security-audit-verdict-fields-compliant`, `code-review-fail-blocker-details`,
  `security-audit-coverage-consistency`.
- **13 cases** had zero live trials on record before this document; each got a real, fresh
  control/treatment pair dispatched via the orchestrator's own in-process `Agent` tool (never a
  `claude` CLI subprocess), using `implementation/runtime/golden_harness/` throughout.
- **1 case is excluded, disclosed here rather than silently dropped:** `plan-task-creation-
  precondition-real`. Its `expect.py` checks that the literal string `T365` appears in a specific
  historical plan document and that a task brief's `Based on:` field names that exact plan file —
  a property inherently tied to one specific, already-existing historical artifact (task T365 /
  plan-030), not something any fresh live session could organically reproduce (a new session has
  no reason to invent task ID `T365` or write a `task-T365.md` file). Dispatching a "trial" against
  this case would not measure anything about retrieval; it was excluded rather than faked. This is
  a genuine, disclosed scope gap: **this document's aggregate covers 19 of the golden suite's 20
  cases**, not all 20.

Six of the 20 cases are from the suite's `held-out/` set (`docs/artifacts/protected-paths-v1.md`,
`tests/functional/test_golden_held_out_isolation.py`). Per that guard's own Check B (verified
empirically against this worktree before any held-out trial was dispatched — see
`task-T456.md`'s "Held-out isolation guard" section), any file outside `tests/golden/` that names
a held-out case ID literally is flagged and would fail `tests/run.py`. This document therefore
refers to the six held-out cases by alias (`HO-1` through `HO-6`, described by command surface and
expected status only) rather than by literal ID. **Live trial execution itself was independently
verified not to trip the guard** (the harness's `scoring.py` resolves case directories dynamically
at call time and hardcodes no held-out path or case ID). The real alias mapping was disclosed
directly to the user in the dispatching session's chat transcript, not committed to any repo file.

## 3. Methodology

- **Mechanism:** `implementation/runtime/golden_harness/scratch.py` (isolated plain scratch
  directories, never a git worktree), `scoring.py` (`expect.py` reuse via
  `importlib.util.spec_from_file_location`, exact `scripts/scorecard.py` pattern), `policy.py`
  (`plan-048` §7's decided k/escalation/floor-tolerance rules as callable functions).
- **New trials (13 cases, k=1 default per `plan-048` §7 Part A):** none of the 13 new cases'
  control/treatment k=1 pair disagreed, so none triggered `policy.should_escalate()`'s
  disagreement trigger; none of the new treatment trials were classified category-3
  ("traceable positive influence"), so none triggered the reproducibility-check escalation
  trigger either. All 13 new cases therefore correctly stayed at k=1 per the pre-registered
  policy, not by omission.
- **Historical trials (6 cases):** backfilled from `task-T484.md` through `task-T494.md`'s own
  prose closure records and `plan-048` §5's category table, reconstructed as real `TrialRecord`s.
  Reconstruction was independently cross-checked against `plan-048`/`T494`'s own stated base-rate
  figures before use (see "Verification of the historical backfill" below) — not accepted as
  correct by construction.
- **Retrieval index:** rebuilt fresh in a throwaway venv this session (`fastembed`/`tree-sitter`,
  no paid API, per `T458`'s own constraint) — `25 chunks, 0 rejections`, `entry_count: 11`, exact
  byte-for-byte match to `T486`/`T487`'s historical manifest.
- **Dispatch economy (disclosed judgment call):** several new cases share an *identical*
  underlying structural check against different fixture paths (e.g. a checkpoint-format check
  applied to a hand-authored-compliant case and a real-historical-drift sibling case with the same
  contract). Where a shared live session's candidate output could be honestly scored against more
  than one case's real `expect.py` without altering its content, one live dispatch was reused
  across those case IDs rather than dispatching a redundant, informationally-identical second
  session. This reduced 13 cases × 2 arms (26 conceptual trials) to 16 actual live dispatches
  (8 dispatch groups × 2 arms), each candidate scored against every case ID it structurally
  applies to. Disclosed here in full rather than left implicit.

### Verification of the historical backfill

Reconstructed 34 historical `TrialRecord`s from the 6 already-tried cases' closure prose.
Independently cross-checked by computing `policy.compute_base_rate()` over the reconstruction and
comparing against `T494`'s own stated figure ("Updated base rate: 2 of 13 classified treatment
trials now show category 3 (~15.4%)") — **the reconstruction reproduced this exactly**
(`classified_count=13, category_3_count=2, rate_of_classified=0.1538...`), and independently
reproduced `T493`'s `security-audit-coverage-consistency` classification
(`confirmed_persistent_effect`) and `plan-048`'s `code-review-fail-blocker-details` classification
(`confirmed_coin_flip`) via `policy.classify_k_plus_outcome()`, not asserted by hand.

## 4. Full per-case results

19 rows below — one per case with live-trial data (6 historical + 13 new this session). The six
held-out cases are identified only by alias (`HO-1`–`HO-6`); see §2 for why.

| Case | Command | Control | Treatment | k≥3 classification | Notes |
|---|---|---|---|---|---|
| `plan-required-sections-compliant` | `/plan` | 3/3 | 3/3 | confirmed_coin_flip | historical (T488, T490) |
| `new-feature-plan-doc-compliant` | `/new-feature` | 3/3 | 5/5 | confirmed_coin_flip | historical (T484, T487, T489, T494) |
| `prepare-release-changelog-grouping-compliant` | `/prepare-release` | 1/1 | 1/1 | — | historical (T488) |
| `security-audit-verdict-fields-compliant` | `/security-audit` | 1/1 | 1/1 | — | historical (T488) |
| `code-review-fail-blocker-details` | `/code-review` | 1/3 | 1/3 | confirmed_coin_flip | historical (T488, T490) |
| `security-audit-coverage-consistency` | `/security-audit` | 4/5 | 1/5 | **confirmed_persistent_effect** | historical (T488, T490, T493); see §5 — arm-agnostic checker-brittleness bug (`matrix_self_consistency_slip`), not judged a retrieval-attributable regression |
| `new-feature-checkpoint-line-compliant` | `/new-feature` | 1/1 | 1/1 | — | new this session |
| `new-feature-real-checkpoint-format-drift` | `/new-feature` | 1/1 | 1/1 | — | new; live sessions satisfy the declared `[CHECKPOINT] id=...` contract unlike the historical corpus this case's static fixture was built from |
| `plan-real-doc-header-drift` | `/plan` | 1/1 | 1/1 | — | new; live sessions follow the command's declared header set exactly, unlike the historical drifted document this case's static fixture documents |
| `prepare-release-real-verdict-missing` | `/prepare-release` | 0/1 | 0/1 | — | new; both arms hit a newly-found, arm-agnostic checker-brittleness bug — see §7 item 1 |
| `code-review-conditional-pass-conditions-gap` | `/code-review` | 1/1 | 1/1 | — | new; **unexpected** — both live sessions spontaneously structured their informal follow-up as a `**Conditions**:` field despite being told not to deliberately engineer one; the static fixture's `capability_gap` prediction did not hold live |
| `prepare-release-conditional-pass-conditions-gap` | `/prepare-release` | 0/1 | 0/1 | — | new; capability gap confirmed live |
| `security-audit-critical-not-fail` | `/security-audit` | 0/1 | 0/1 | — | new; both arms correctly concluded a genuine `FAIL` verdict when a CRITICAL finding existed, but both hit a newly-found, arm-agnostic checker-brittleness bug — see §7 item 3 |
| `HO-1` (`/code-review`, expected_pass) | `/code-review` | 1/1 | 1/1 | — | new, held-out |
| `HO-2` (`/code-review`, tracked_defect drift) | `/code-review` | 1/1 | 1/1 | — | new, held-out; same "live sessions satisfy the declared contract" pattern as the other `-real-` drift cases |
| `HO-3` (`/new-feature`, tracked_defect drift) | `/new-feature` | 1/1 | 1/1 | — | new, held-out; live sessions default to `major.minor` artifact versioning, unlike the historical corpus's single-integer convention this case's static fixture documents |
| `HO-4` (`/plan`, capability_gap) | `/plan` | 0/1 | 0/1 | — | new, held-out; capability gap confirmed live — neither arm spontaneously added an `## Approval` marker the command never asks for |
| `HO-5` (`/prepare-release`, expected_pass) | `/prepare-release` | 0/1 | 0/1 | — | new, held-out; both arms hit the same newly-found checker-brittleness bug as `prepare-release-real-verdict-missing` — see §7 item 1 |
| `HO-6` (`/security-audit`, expected_pass) | `/security-audit` | 0/1 | 0/1 | — | new, held-out; both arms hit a newly-found, arm-agnostic checker-brittleness bug — see §7 item 2 |

**Excluded (not trialed, not counted in the aggregate below):** `plan-task-creation-precondition-
real` — see §2.

## 5. Aggregate and pre-registered threshold, applied honestly

- **Aggregate control pass rate: 20/29 = 68.97%**
- **Aggregate treatment pass rate: 19/31 = 61.29%**
- **`policy.floor_met()` (treatment ≥ control): `False`**

Per `task-T456.md`'s pre-registered threshold (committed before any new trial was dispatched):

> T456 passes (ships) if, over the full golden suite's aggregate results: (a) `floor_met()` is
> `True` — **AND** (b) no case is classified `CONFIRMED_PERSISTENT_EFFECT` in a way that
> constitutes a real, retrieval-attributable regression.

- **Criterion (a): FALSE.** The raw aggregate floor is missed.
- **Criterion (b):** only one case reaches `CONFIRMED_PERSISTENT_EFFECT` —
  `security-audit-coverage-consistency`. Per the pre-registered judgment framework (mirroring
  `T493`'s own characterization of this exact case): its recurring cause
  (`matrix_self_consistency_slip` — a declared-count-vs-matrix-row-count self-consistency check
  in the OWASP coverage matrix) hits **both** arms (control-4 as well as treatment-2/4/5 in the
  full k=5 record), making it an arm-agnostic checker/template-brittleness bug, not a
  retrieval-specific regression. Criterion (b) is therefore satisfied (no case fails as a
  *retrieval-attributable* persistent effect).

**Because criterion (a) and (b) are ANDed, and (a) is literally `False` on the raw aggregate, the
pre-registered threshold is not met. Verdict: NO-SHIP.** This is reported exactly as measured,
without adjusting the pre-registered criteria after seeing the result.

## 6. Root-cause analysis (disclosed context — does not override §5's verdict)

The floor miss is not diffuse across the suite. Of the 19 cases in this aggregate, **18 have
byte-identical control and treatment pass counts** (either both arms passed every trial, or both
arms failed every trial, on every one of those 18 cases). The entire net deficit — control's 20
passes vs. treatment's 19, despite treatment having 2 more total trials — is arithmetically
attributable to exactly one case: `security-audit-coverage-consistency` (control 4/5, treatment
1/5), the same case §5 just discussed and the same case `T493` already classified as an
arm-agnostic checker-brittleness bug **before this session began**.

Recomputed with that one case excluded (disclosed as supplementary analysis only, not a
substitute verdict): control 16/24 = 66.67%, treatment 18/26 = 69.23%, `floor_met() = True`.
This is not used to override §5's literal verdict — the pre-registered criteria did not include
an "excluding already-diagnosed brittleness cases" clause, and retroactively adding one now would
be exactly the post-hoc rationalization the pre-registration discipline exists to prevent. It is
reported because an honest report should show *why* the number lands where it does, not just that
it does.

## 7. New findings this session (disclosed, not previously known)

Three new, real, **arm-symmetric** checker-brittleness bugs were found while dispatching this
batch — each affects both control and treatment identically, so none of them bias `floor_met()`
in either direction, but each is a genuine expect.py/format-detection fragility worth a future
fix:

1. **Nested-fence heading truncation** (`prepare-release-real-verdict-missing` and its held-out
   sibling **HO-5**): when a live session's `## RELEASE VERDICT` heading
   is followed by a fenced-code-block reproduction of the same heading+fields (a structure both
   the real command template's own source and this trial's dispatch instructions visually
   suggest), `_verdict_section()`'s heading-boundary regex (`\n#{1,2}\s`) matches the *inner*
   fenced "## RELEASE VERDICT" line and truncates the section before any field bullets are
   reached — even though the real field data is present in the document.
2. **Numeric-index-vs-literal-A0N mismatch** (held-out case **HO-6**):
   both live sessions numbered OWASP matrix rows `1`–`10` in the `#` column and folded the
   category code into the category-name cell (`| 1 | A01: Broken Access Control | ...`) rather
   than using the literal `A01`–`A10` tokens as their own cell (`| A01 | Broken Access Control |
   ...`), which `expect.py`'s `\|\s*A01\s*\|`-style regex requires. This reproduced on the *third*
   dispatch (Group H) even after the dispatch prompt was corrected to explicitly require the
   literal-`A0N`-per-cell format — a live-session formatting default that resists a one-line
   instruction fix, itself a mildly interesting finding about how reliably a command template's
   own illustrative example is followed.
3. **First-regex-match status field** (`security-audit-critical-not-fail`): `expect.py` finds the
   *first* `**Status**:` occurrence in the whole document via `re.search`, not one scoped to the
   `## VERDICT` section. Both live sessions wrote an informal `**Status**: Fail` (title case) in
   an earlier `## Summary` section before their correct, later `**Status**: FAIL` (upper case) in
   the real `## VERDICT` block — the checker matched the earlier, differently-cased one and
   returned `False` even though both sessions correctly concluded, and correctly formatted,
   `FAIL` in the field the command template actually specifies.

None of these three bugs are retrieval-attributable (both arms hit each one identically). All
three are candidate follow-up fixes for whichever future task owns `expect.py`
maintenance/`docs/artifacts/protected-paths-v1.md`'s disclosed-exception process — not made here,
since this document's task-T456 scope is measurement, not `tests/golden/**` modification (a
protected path, untouched by this measurement).

## 8. Two live-session behavioral findings independent of pass/fail

- **`code-review-conditional-pass-conditions-gap`**: both live sessions passed this
  `capability_gap` case unexpectedly — despite being explicitly told not to deliberately engineer
  a structured field, both Tech Lead sessions still naturally itemized their informal follow-up
  under a `**Conditions**:` bullet list. The static fixture's `known_failing` prediction (built
  around a hand-authored, deliberately-unstructured example) did not hold for a live session's own
  natural writing style.
- **The three `-real-...-drift` cases dispatched this session** (`new-feature-real-checkpoint-
  format-drift`, `plan-real-doc-header-drift`, and HO-2) **all passed live**, even though their
  static, historically-sourced fixtures are `known_failing`. A fresh live session, explicitly
  given the command's own declared contract, follows that contract — the historical drift these
  cases document reflects how this repo's *actual past practice* diverged from the command
  definition over time, not a property a fresh session reproduces by default.

## 9. Recommendation

**Do not present Phase 5's RAG feature as having formally cleared its `plan-035` ship gate** —
the pre-registered criterion is not met, per §5, and this document does not attempt to soften that
conclusion. At the same time, §6's analysis shows the miss is narrowly attributable to one
already-diagnosed, arm-agnostic checker-brittleness bug in a single case's `expect.py`, not to a
diffuse or retrieval-caused quality problem — of 19 measured cases, 18 show retrieval having zero
observable effect on pass/fail (in either direction), and the one asymmetric case is a known
template/checker defect, not a regression.

Suggested next step (not performed here, out of this task's protected-path scope): fix
`security-audit-coverage-consistency`'s `matrix_self_consistency_slip` root cause (the declared
finding-count vs. matrix-row-count self-consistency check, per `plan-048` §6 item 1's own
already-open recommendation) and the three new brittleness bugs in §7, then re-run this
measurement. Given §6's exclusion analysis, fixing just the one already-diagnosed case would be
expected to clear the floor on a re-run, though that is a prediction, not a re-measured fact, and
should not be treated as one.

## 10. Disclosed judgment calls and limitations, summarized

1. `plan-task-creation-precondition-real` excluded from live trialing (§2) — a real, structural
   scope gap in this document's coverage (19/20 cases, not 20/20).
2. Held-out cases referenced by alias, not literal ID, in this document (§2) — a mechanical
   requirement of `tests/functional/test_golden_held_out_isolation.py`'s Check B, verified
   empirically before any held-out trial was dispatched.
3. Dispatch economy: several cases share one live session's candidate output rather than each
   getting an independently-dispatched session (§3) — disclosed, not hidden.
4. Historical backfill (6 cases, 34 trials) reconstructed from prose closure records, not from
   raw stored trial data (§3) — independently cross-checked against `T494`'s own stated figures
   before use, not merely asserted correct.
5. §6's "excluding one case" recomputation is disclosed context, explicitly **not** used to
   override §5's literal, pre-registered NO-SHIP verdict.
