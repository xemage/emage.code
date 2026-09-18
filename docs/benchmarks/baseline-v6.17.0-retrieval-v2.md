# Baseline v6.17.0 — Retrieval-Enabled Golden Suite Measurement, v2 (T499 re-measurement)

**Based on:** `docs/benchmarks/baseline-v6.17.0-retrieval.md` (v1, T456's original closed
measurement — control 20/29 = 68.97%, treatment 19/31 = 61.29%, `policy.floor_met()` = `False`,
verdict **NO-SHIP**; this document supersedes its verdict, not its methodology, and cites its
14 unaffected rows directly rather than re-deriving them); `docs/tasks/task-T499.md`
(pre-registered threshold — reused verbatim from `task-T456.md` — and full execution log);
`docs/tasks/task-T498.md` / `docs/plans/plan-052-t498-golden-checker-brittleness-fixes.md` (the
checker fix this re-measurement is downstream of, merge `8c10fca`); `docs/plans/
plan-048-t458-k-threshold-decision.md` §7 (the k/escalation/floor-tolerance policy, unchanged,
reused as-is via `implementation/runtime/golden_harness/policy.py`).

**Status:** Complete re-measurement. **Verdict: SHIP** — both pre-registered criteria are met on
the full, 19-of-20-case aggregate. Reported plainly, per this task's own "state the verdict either
way" discipline, exactly as `baseline-v6.17.0-retrieval.md` reported its NO-SHIP verdict plainly.

## 1. What changed since v1, and why this document exists rather than editing v1

`task-T498.md` fixed four checker-brittleness bugs, diagnosed by `baseline-v6.17.0-retrieval.md`
§6/§7 and by `task-T493.md` (bug 1's original diagnosis), across exactly five `expect.py` files —
independently re-confirmed this session via `git diff cc77974 origin/develop --
'tests/golden/**/expect.py' --stat`, which shows exactly those five files changed and zero others.
Those five files correspond to exactly five of the 19 golden cases v1 measured. **This document
re-measures only those five cases.** The other 14 cases' `expect.py` files are mechanically
unchanged since v1's measurement, so their results are cited directly from
`baseline-v6.17.0-retrieval.md` §4, not re-derived. Per this repo's Artifact Versioning
convention (`AGENTS.md`: "revisions create new versions, never overwrite"), this is a new
versioned document, not an edit to v1 — v1 remains the accurate historical record of what was
measured, and when, against the pre-fix checkers.

## 2. Scope: same 19-of-20 cases as v1, 14 cited + 5 re-measured

Identical scope to v1 (§2 of that document): 19 of the golden suite's 20 cases are measured;
`plan-task-creation-precondition-real` remains excluded for the same reason v1 gave (tied to one
specific historical artifact's literal identity — task ID `T365` — not organically reproducible by
a fresh live session or a re-score). Six of the 19 are held-out cases, referred to only by alias
(`HO-1`–`HO-6`) for the same `test_golden_held_out_isolation.py` Check B reason v1 disclosed.

**14 cases cited unchanged from `baseline-v6.17.0-retrieval.md` §4** (mechanically confirmed their
`expect.py` is byte-identical since v1's measurement commit): `plan-required-sections-compliant`,
`new-feature-plan-doc-compliant`, `prepare-release-changelog-grouping-compliant`,
`security-audit-verdict-fields-compliant`, `code-review-fail-blocker-details`,
`new-feature-checkpoint-line-compliant`, `new-feature-real-checkpoint-format-drift`,
`plan-real-doc-header-drift`, `code-review-conditional-pass-conditions-gap`,
`prepare-release-conditional-pass-conditions-gap`, `HO-1`, `HO-2`, `HO-3`, `HO-4`.

**5 cases re-measured**, matching `task-T498.md`'s own five-file list exactly:
`security-audit-coverage-consistency`, `prepare-release-real-verdict-missing`, `HO-5`, `HO-6`,
`security-audit-critical-not-fail`.

## 3. Methodology for the 5 re-measured cases — two different mechanisms, both disclosed

**4 of the 5 cases were re-scored against their original T456 candidate text, unmodified.** This
re-measurement happened to continue in the same orchestrator session that originally ran T456;
this session's own scratch directory still held the raw, unmodified markdown candidates T456's
live dispatch groups produced for `prepare-release-real-verdict-missing` (and its held-out
sibling `HO-5`, which shares an identical `_verdict_section()` contract and, per v1 §3's own
disclosed "dispatch economy," was originally scored against the same candidate), `security-audit-
critical-not-fail`, and `HO-6`. Each candidate was re-scored via
`implementation/runtime/golden_harness/scoring.py`'s real `score_scratch_dir()` — the same
`expect.py`-reuse call shape v1 itself used — against the now-fixed `expect.py`, with **zero
change to the candidate text itself**. This is deliberately the more rigorous of the two options
available (re-score vs. fresh re-dispatch): it isolates the checker-fix's effect completely from
any live-session non-determinism, since the exact same candidate is being re-graded and only the
grader changed. One real setup mistake was caught and corrected before trusting any result: the
first scratch-directory build for `prepare-release-real-verdict-missing` doubled a path segment
(`fixture/docs/checkpoints/docs/checkpoints/...`), causing `expect.py`'s own glob to find zero
candidates and return `False` by construction, not by checker logic — caught by inspecting the
empty candidate list directly, rebuilt correctly, re-scored.

**1 of the 5 cases (`security-audit-coverage-consistency`) required a fresh live trial**, because
it was one of v1's 6 *historical* cases (backfilled from `task-T488.md`–`task-T493.md`'s prose,
never given a fresh live dispatch by T456 in this session) — there was no candidate text to
recover. Dispatched fresh at **k=1** per `plan-048` §7's default policy: the case's historical
k=5 escalation record does not carry forward, because that escalation was itself triggered by the
pre-fix checker's disagreement pattern between arms (v1 §5/§6); `policy.should_escalate()` was
applied fresh to the new k=1 pair under the fixed checker, not assumed to still require k>=3.
Both arms used the orchestrator's own in-process `Agent` tool (never a `claude` CLI subprocess),
against the case's real `brief.md` scope ("Perform a security audit on the internal admin CLI's
authentication and authorization paths only"). The treatment arm used the same real memory index
T456 built this session (`fastembed`/`nomic-embed-text-v1.5`, 25 chunks, `entry_count: 11`,
independently re-confirmed still functional before dispatch) via the real `context_retriever.py`
CLI invocation shape.

## 4. Per-case results for the 5 re-measured cases (before/after)

| Case | Control (pre-fix, v1) | Treatment (pre-fix, v1) | Control (post-fix, this doc) | Treatment (post-fix, this doc) | Mechanism |
|---|---|---|---|---|---|
| `prepare-release-real-verdict-missing` | 0/1 | 0/1 | **1/1** | **1/1** | re-scored original candidate |
| `HO-5` | 0/1 | 0/1 | **1/1** | **1/1** | re-scored original candidate (shared with the case above) |
| `security-audit-critical-not-fail` | 0/1 | 0/1 | **1/1** | **1/1** | re-scored original candidate |
| `HO-6` | 0/1 | 0/1 | **1/1** | **1/1** | re-scored original candidate |
| `security-audit-coverage-consistency` | 4/5 | 1/5 | **1/1** | **1/1** | fresh live k=1 pair (escalation not triggered — see §3) |

All five cases flip from failing (or, for `security-audit-coverage-consistency`, asymmetrically
failing more often in the treatment arm) to passing unanimously in both arms under the fixed
checkers. This is consistent with `baseline-v6.17.0-retrieval.md` §6's own root-cause finding that
these failures were arm-agnostic checker-brittleness bugs, not retrieval-attributable — the fix
resolves them symmetrically, which is exactly what a true checker-brittleness diagnosis predicts
and what a real retrieval-quality regression would not have predicted.

**`security-audit-coverage-consistency`'s treatment arm, qualitative disclosure:** the dispatched
session invoked retrieval twice (queries on admin-CLI authn/authz findings patterns, and on OWASP
coverage-matrix scoping semantics); both calls returned real results, but the returned content was
this repo's own process/meta documentation (memory-layer architecture, held-out isolation guards,
validation-gate protocol), not application-security domain knowledge — disclosed as **no material
influence** on findings, severities, or the declared coverage number, honestly reported by the
dispatched session rather than overstated. This is rubric category 2 (`plan-048` §5: "consulted,
real content, no distinguishable influence"), not category 3 — consistent with `plan-048` §5's own
finding that this evidence base's retrieved content tends to be general good practice a competent
session can often reconstruct without it, not a case-specific fact retrieval uniquely supplied.

## 5. New aggregate, computed via the real `policy` functions (not hand arithmetic)

`TrialRecord`s were built for all 19 measured cases — the 14 unaffected cases' `TrialRecord`s
reconstructed from `baseline-v6.17.0-retrieval.md` §4's own cited pass/total counts, the 5
re-measured cases' `TrialRecord`s from §4 above — and passed through the real
`implementation/runtime/golden_harness/policy.pass_rate()` / `policy.floor_met()` functions:

- **Aggregate control pass rate: 21/25 = 84.00%** (14 unaffected cases: 16/20, cited from v1 §4;
  5 re-measured cases: 5/5, this document)
- **Aggregate treatment pass rate: 23/27 = 85.19%** (14 unaffected cases: 18/22, cited from v1 §4;
  5 re-measured cases: 5/5, this document)
- **`policy.floor_met()` (treatment >= control): `True`**

Per `task-T499.md`'s pre-registered threshold (reused verbatim from `task-T456.md`, committed
before any new trial or re-score):

> T499 passes (ships) if: (a) `floor_met()` is `True` — **AND** (b) no case is classified
> `CONFIRMED_PERSISTENT_EFFECT` in a way that constitutes a real, retrieval-attributable
> regression.

- **Criterion (a): TRUE.** The aggregate floor is met, with a positive margin (treatment leads
  control by 1.19 percentage points).
- **Criterion (b): TRUE, and now vacuously so in a stronger sense than v1's own "satisfied but
  disclosed" finding.** v1's aggregate had exactly one case reaching
  `CONFIRMED_PERSISTENT_EFFECT` (`security-audit-coverage-consistency`), which v1 itself judged to
  be an arm-agnostic checker-brittleness bug rather than a real regression. In this document,
  that case is no longer even eligible for that classification: it was re-measured fresh at k=1,
  landed unanimous (both arms pass), was correctly not escalated per `policy.should_escalate()`
  (no disagreement, no category-3 finding), and `policy.classify_k_plus_outcome()` requires k>=3
  per arm to classify anything at all. No case in this new 19-case aggregate holds
  `CONFIRMED_PERSISTENT_EFFECT`, full stop — not merely "holds it but judged non-retrieval," as
  in v1.

**Both criteria are met. Verdict: SHIP.** Reported exactly as measured, without adjusting the
pre-registered criteria after seeing the result — the same discipline v1 applied to its own
NO-SHIP outcome.

## 6. Why this result is not a post-hoc rationalization of v1's NO-SHIP

v1 §6 already showed, as *disclosed supplementary analysis* (explicitly not used to override its
own literal verdict), that excluding the one persistent-effect case flipped the aggregate to
`floor_met() = True` (16/24 vs 18/26) — and predicted in §9 that "fixing just the one
already-diagnosed case would be expected to clear the floor on a re-run, though that is a
prediction, not a re-measured fact." This document is that re-measured fact, arrived at through
the pre-registered process v1 itself specified for exactly this situation (fix the diagnosed
bugs, then re-run), not by re-including or re-excluding cases after the fact. The margin is
slightly different from v1 §6's supplementary prediction (85.19% vs. control's 84.00%, a 1.19pp
lead, versus v1 §6's excluded-case recomputation of 69.23% vs. 66.67%, a 2.56pp lead) because this
document's aggregate includes all 19 cases at their real, current, fixed-checker results — three
cases beyond `security-audit-coverage-consistency` (`prepare-release-real-verdict-missing`, `HO-5`,
`HO-6`, `security-audit-critical-not-fail`) also flipped from failing to passing, which v1 §6's
supplementary recomputation did not anticipate (it only excluded the one case it had already
diagnosed, not the three others T498's fix also happened to resolve).

## 7. Recommendation

**Phase 5's `plan-035` ship gate (Gate G3) closes.** Both pre-registered criteria are met on the
full, honestly-measured 19-of-20-case aggregate: the non-regression floor holds with a positive
margin, and no case shows a retrieval-attributable persistent effect — the one case that
previously showed an arm-agnostic checker-brittleness effect is now resolved, not merely
explained away. Phase 5's RAG feature (`@context-retriever`, T450–T455) may now be presented as
having cleared its formal ship gate. This does not retroactively change what was true when
`baseline-v6.17.0-retrieval.md` was written — that measurement was real, honest, and correctly
blocked promotion at the time; this document is the equally honest record of what changed once the
diagnosed checker bugs were actually fixed, not a reversal of the original finding's validity at
the time it was made.

## 8. Disclosed judgment calls and limitations, summarized

1. Two different re-measurement mechanisms used across the 5 cases (re-score vs. fresh dispatch),
   disclosed in §3 rather than presented uniformly — the re-score mechanism is the more rigorous
   of the two where it was available (isolates the checker-fix effect completely), not a
   shortcut.
2. `security-audit-coverage-consistency`'s treatment-arm retrieval calls returned real but
   unhelpful content (this repo's own meta-documentation, not application-security knowledge) —
   disclosed as a null result, not omitted or spun as evidence of retrieval quality either way.
3. `plan-task-creation-precondition-real` remains excluded from this document's aggregate, same
   reason as v1 — this document's coverage is 19/20 cases, not 20/20, identical to v1.
4. Held-out cases referenced by alias only (`HO-5`, `HO-6`, plus the four carried-forward aliases),
   real directory names independently re-derived and never committed outside `tests/golden/`.
5. This document does not re-verify the 14 carried-forward cases' original trial-level detail
   (individual `k`-indexed pass/fail sequences) — only their aggregate pass/total counts, cited
   directly from v1 §4's own published table, which is itself the authoritative record for those
   cases and was not re-derived here.
