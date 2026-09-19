# Task T499 — Re-measure Phase 5's ship gate (T498 checker-fix delta)

**ID:** T499
**Owner:** orchestrator (executed directly — same structural reason `task-T456.md` already
established: `evaluation-agent`'s tool grant is `[read, search, web]` per
`implementation/knowledge/agents/evaluation-agent.md` — no `Bash`, no `Agent` tool, structurally
unable to run the golden harness or dispatch live trials. This task follows the `T456`/`T484`–
`T494` precedent of direct orchestrator execution rather than dispatching to `evaluation-agent`
and hitting the same wall a second time.)
**Status:** done
**Closure note (2026-09-18):** re-measurement complete, **verdict SHIP**. See "Pre-registered
ship-gate threshold" below (reused verbatim from `task-T456.md`, committed before any new trial or
re-score) and "Execution log" for the full methodology. `docs/benchmarks/
baseline-v6.17.0-retrieval-v2.md` holds the full report.
**Priority:** P0 (unchanged from `plan-035`/`task-T456.md` — this is Phase 5's literal ship gate)
**Depends on:** T456 (done, NO-SHIP), T498 (done — the checker fix this re-measurement is
downstream of)
**Created:** 2026-09-18
**Completed:** 2026-09-18
**Based on:** `docs/tasks/task-T456.md` (the original measurement, its pre-registered threshold
reused verbatim below, its run scope, its held-out isolation discipline);
`docs/benchmarks/baseline-v6.17.0-retrieval.md` (T456's closed report — all 19 measured cases'
per-case results, root-cause analysis, and the checker-brittleness findings that motivated T498);
`docs/tasks/task-T498.md` and `docs/plans/plan-052-t498-golden-checker-brittleness-fixes.md` (the
just-landed fix, merge `8c10fca`); `docs/plans/plan-048-t458-k-threshold-decision.md` §7 (the
k/escalation/floor-tolerance policy, unchanged, reused as-is); `docs/plans/plan-053-t499-ship-gate-
remeasurement.md` (this task's own backing plan).

## Pre-registered ship-gate threshold (committed 2026-09-18, before any new trial or re-score)

Reused **verbatim** from `task-T456.md`'s own pre-registered threshold — this task does not
invent a new numeric threshold, per the same "pre-register what 'improve' means before the run"
discipline `task-T456.md` itself followed, and per the explicit user instruction that this is a
re-run of T456 (same gate, same criteria, only the checker changed):

**T499 passes (ships) if, over the full golden suite's aggregate results:**

1. `implementation/runtime/golden_harness/policy.floor_met()` is `True` — aggregate treatment pass
   rate across all measured cases' final trial sets is `>=` aggregate control pass rate — **AND**
2. No case is classified `policy.CONFIRMED_PERSISTENT_EFFECT` by
   `policy.classify_k_plus_outcome()` in a way that constitutes a **real regression** — i.e., a
   persistent-effect cause that hurts the treatment arm *specifically*, not an arm-agnostic
   checker-brittleness bug. Judgment applied consistent with how `T493`/`T456` characterized this
   distinction, disclosed explicitly per-case if it applies to any case in this run.

No additional numeric percentage-point cutoff is pre-registered beyond this reused policy.

## Pre-registered run scope (committed 2026-09-18, before any new trial or re-score)

- **14 of the 19 previously-measured cases are structurally unaffected by T498's fix and are
  carried forward unchanged**, cited directly from `baseline-v6.17.0-retrieval.md` §4's own
  per-case table, not re-derived: `plan-required-sections-compliant`,
  `new-feature-plan-doc-compliant`, `prepare-release-changelog-grouping-compliant`,
  `security-audit-verdict-fields-compliant`, `code-review-fail-blocker-details`,
  `new-feature-checkpoint-line-compliant`, `new-feature-real-checkpoint-format-drift`,
  `plan-real-doc-header-drift`, `code-review-conditional-pass-conditions-gap`,
  `prepare-release-conditional-pass-conditions-gap`, `HO-1`, `HO-2`, `HO-3`, `HO-4`. Verified
  mechanically before relying on this, not assumed: `git diff cc77974 origin/develop --
  'tests/golden/**/expect.py' --stat` shows exactly five files changed by T498, and none of these
  14 cases' `expect.py` is among them.
- **Exactly 5 cases are re-measured**, matching `task-T498.md`'s own five-file list exactly:
  `security-audit-coverage-consistency`, `prepare-release-real-verdict-missing`, `HO-5`, `HO-6`,
  `security-audit-critical-not-fail`.
- **1 case remains excluded**, same reason and same disclosure as `task-T456.md` §2:
  `plan-task-creation-precondition-real` (tied to one specific historical artifact's literal
  identity, not organically reproducible by a fresh session or a re-score). This document's
  aggregate, like `baseline-v6.17.0-retrieval.md`'s own, covers 19 of the golden suite's 20 cases.

## Held-out isolation guard — re-verified, not re-assumed

`tests/functional/test_golden_held_out_isolation.py` was re-confirmed still passing on
`origin/develop` before this task began. The two held-out real directory names behind `HO-5`/`HO-6`
were independently re-derived by reading every `expect.py` under `tests/golden/held-out/` directly
and matching mechanism/command-surface/status against `baseline-v6.17.0-retrieval.md`'s own
descriptions (same discipline `task-T498.md` required of itself) — **never asserted from memory**.
The real names are used only in this session's own local, uncommitted reasoning; every artifact
this task commits (this file, `plan-053`, the new report) refers to the two cases only as `HO-5`
and `HO-6`.

## Execution log

Working in `agent/orchestrator/T499` (from `origin/develop` @ `8c10fca`). No self-merge — branch
pushed and an MR opened against `develop` for independent top-level review, per this project's
standing no-self-merge rule.

**Constraints confirmed for this dispatch:** did not touch `tests/golden/**`, `scripts/
scorecard.py`, `.mcp.json`, `docs/benchmarks/tb-subset.json`/`.md`,
`feature/T475-codex-platform-integration`. All scoring used
`implementation/runtime/golden_harness/scoring.py`'s real `score_scratch_dir()` (the same
`expect.py`-reuse call shape `T456`/`T458` established) — no by-hand `importlib` mechanism, no
edits to any `expect.py`.

1. **Diff verification (before any trial or re-score):** `git diff cc77974 origin/develop --
   'tests/golden/**/expect.py' --stat` run directly — confirmed exactly the 5 files `task-T498.md`
   names, zero others, mechanically (not assumed from the dispatch brief's own claim).
2. **Recovery check (before dispatching any fresh trial):** this task happened to continue in the
   *same* orchestrator session that originally ran `T456`. Checked this session's own scratch
   directory for the raw candidate markdown files T456's live dispatch groups produced. Found:
   the original, unmodified candidate text for 4 of the 5 affected cases was still present —
   `prepare-release-real-verdict-missing` and its held-out sibling `HO-5` (shared candidate, per
   `baseline-v6.17.0-retrieval.md` §3's own disclosed "dispatch economy" — both check the same
   `_verdict_section()` contract), `security-audit-critical-not-fail`, and `HO-6`. The 5th case,
   `security-audit-coverage-consistency`, was one of `T456`'s 6 *historical* cases (backfilled
   from `task-T488.md`–`task-T493.md` prose, never given a fresh live dispatch by T456 itself in
   this session) — no candidate text exists to recover for it.
3. **Re-scored the 4 recovered candidates against the fixed checkers**, via
   `scoring.score_scratch_dir()`, using the exact original T456 candidate files, unmodified:

   | Case | Control (re-scored) | Treatment (re-scored) |
   |---|---|---|
   | `prepare-release-real-verdict-missing` | **True** (was `False` pre-fix) | **True** (was `False` pre-fix) |
   | `HO-5` | **True** (was `False` pre-fix) | **True** (was `False` pre-fix) |
   | `security-audit-critical-not-fail` | **True** (was `False` pre-fix) | **True** (was `False` pre-fix) |
   | `HO-6` | **True** (was `False` pre-fix) | **True** (was `False` pre-fix) |

   One real setup mistake caught and fixed during this step, disclosed rather than silently
   corrected: the first scratch-directory build for `prepare-release-real-verdict-missing`
   doubled the `docs/checkpoints/` path segment (`fixture/docs/checkpoints/docs/checkpoints/...`),
   causing `expect.py`'s own `ckpt_dir.glob("*.md")` to find zero candidates and return `False` by
   construction, not by the checker's real logic. Caught by inspecting the empty `candidates` list
   directly before trusting the result; rebuilt correctly and re-scored.
4. **Dispatched one fresh live control/treatment pair at k=1** for `security-audit-coverage-
   consistency`, per this task's own pre-registered scope — the case's historical k=5 escalation
   record does **not** carry forward (that escalation was itself triggered by the pre-fix checker's
   disagreement pattern; `policy.should_escalate()` is applied fresh against the new checker).
   Both arms used the orchestrator's own in-process `Agent` tool (never a `claude` CLI subprocess),
   against the case's own `brief.md` scope ("Perform a security audit on the internal admin CLI's
   authentication and authorization paths only"). Treatment arm used the same real memory index
   T456 built this session (`fastembed`/`nomic-embed-text-v1.5`, 25 chunks, `entry_count: 11`,
   independently re-confirmed still functional before dispatch) via the real
   `context_retriever.py` CLI invocation shape.
   - **Control result:** `True` (declared `**OWASP coverage**: 8/10`; matrix lists all 10 A0X rows
     — `8 <= 10` under the fixed self-consistency rule).
   - **Treatment result:** `True` (declared `8/10` against a 10-row matrix; same self-consistency
     pattern). Treatment session disclosed invoking retrieval twice (queries on admin-CLI
     authn/authz findings patterns and on OWASP coverage-matrix scoping semantics); both returned
     real results, but the returned content was this repo's own process/meta documentation, not
     application-security domain knowledge — **no material influence on findings, severities, or
     the declared coverage number**, disclosed honestly by the dispatched session rather than
     overstated. Qualitatively this is rubric category 2 (`plan-048` §5: "consulted, real content,
     no distinguishable influence"), not category 3.
   - `policy.should_escalate(control_k1, treatment_k1)`: `result` agrees (`True == True`) and
     `category` is not `"3"` → **no escalation** (`EscalationDecision(False, None)`), correctly
     stays at k=1 per policy, not by omission.
5. **New aggregate computed via the real `policy.floor_met()`/`pass_rate()` functions**, not hand
   arithmetic — `TrialRecord`s built from (a) the 14 unaffected cases' own historical pass/total
   counts, cited directly from `baseline-v6.17.0-retrieval.md` §4, and (b) the 5 re-measured
   cases' fresh results above:
   - **Aggregate control pass rate: 21/25 = 84.00%**
   - **Aggregate treatment pass rate: 23/27 = 85.19%**
   - **`policy.floor_met()`: `True`**
   - No case in this new aggregate is classified `CONFIRMED_PERSISTENT_EFFECT` — the one case that
     held that classification in the original measurement (`security-audit-coverage-consistency`)
     is now measured fresh at k=1 (unanimous pass, not escalated, therefore not eligible for
     `classify_k_plus_outcome()`, which requires k>=3 per arm), and none of the 14 carried-forward
     cases held that classification either (per `baseline-v6.17.0-retrieval.md` §4's own table:
     `confirmed_coin_flip` for `plan-required-sections-compliant`, `new-feature-plan-doc-
     compliant`, `code-review-fail-blocker-details`; no classification recorded for the rest,
     since none were escalated).
   - **Both pre-registered criteria met: verdict SHIP.**
6. **Full report written** to `docs/benchmarks/baseline-v6.17.0-retrieval-v2.md` (new version, per
   this repo's Artifact Versioning convention — the original is not overwritten), citing the
   original report's 14 unaffected rows directly and documenting the 5 re-measured rows'
   before/after delta, methodology, and the SHIP verdict.
7. **Gate G3 (`plan-035` §2.4, Phase 5's memory gate) now closes** — this task's own honest
   conclusion, not asserted lightly: both pre-registered criteria are met on the full,
   19-of-20-case aggregate, with the previously sole `CONFIRMED_PERSISTENT_EFFECT` case now
   resolved (fresh-measured, unanimous, not persistent) rather than worked around or excluded.
8. **Verification bar run:** `tests/run.py`, `validate-tasks.py`, `check-maturity.py --verbose`,
   `sync.mjs --root implementation --check` — see closure note / MR description for output. This
   task's own brief text was swept for any literal, currently-stable, hyphenated component id
   named as a bare word before commit (the recurring self-referential-ledger-defect class this
   session has hit before) — see the sweep note in the closing commit.

## Acceptance Criteria

1. Exactly the 5 named cases re-measured; the other 14 cases' `baseline-v6.17.0-retrieval.md`
   results cited, not re-derived, and mechanically confirmed unaffected via a direct `expect.py`
   diff.
2. `tests/golden/**` and `scripts/scorecard.py` untouched by this task (measurement only).
3. `docs/benchmarks/baseline-v6.17.0-retrieval-v2.md` created as a new version — the original is
   not overwritten — citing it as `Based on:` and stating plainly which cases changed and why.
4. The pre-registered threshold applied honestly, verdict stated plainly either way (this task's
   own instruction: a genuine SHIP or a genuine, honestly-measured continued NO-SHIP are both
   legitimate `done` closures — not a reason to leave the task open).
5. `HO-5`/`HO-6` real directory names never appear in any file this task commits outside
   `tests/golden/`.
6. No self-merge — branch + MR only, left for independent top-level review.

## Blocker Protocol record

None encountered. The one real setup mistake (step 3's doubled path segment) was caught and
corrected before trusting any result, not a blocker requiring escalation.
