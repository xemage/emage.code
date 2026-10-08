# T592 — Refresh residual golden staleness (FU-8) under a user-approved v17

**ID:** T592
**Owner:** qa-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-106-golden-residual-staleness.md`
- `docs/plans/plan-101-golden-quote-refresh.md` §4 (the definition of FU-8)
- `docs/artifacts/protected-paths-v1.md` §5
- The user's decision of 2026-10-08: "Next item: approving a v17 baseline - continue with FU-8"

## 1. What and why

T583 (FU-2) left some golden-case text stale on purpose, because it fell outside that task's grant. Since then T585,
T587 and T589 have amended `validation-gates`, so its fixture copy lags further.

This task makes every claim in the two cases below true again. **No `check()` logic changes.** Every case result and
status must stay exactly as it is. If any of them would change, stop and report it.

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T592, is the authorizing task** for edits to exactly these files, and only to the text named in §3:

| Case (`tests/golden/open/…`) | Files |
|---|---|
| `validate-workflow-gate-verdict-sources` | `fixture/implementation/knowledge/commands/validate-workflow.md` and `fixture/implementation/knowledge/skills/validation-gates/SKILL.md` (both re-copied byte-identical from the source); `brief.md` (§ Provenance only); `expect.py` (module docstring only, and only if a claim in it is untrue after the re-copy) |
| `security-audit-critical-not-fail` | `expect.py` (module docstring line 2 only); `case.yaml` (`known_failing_reason` only); `brief.md` (the "The rule must not be amended" bullet only) |

**Not authorized:**
- any `check()` body or constant;
- any `status`, `known_failing_category` or `tags` field;
- any other file or case;
- `tests/golden/held-out/` (do not open it; prune it from every traversal);
- `scripts/scorecard.py`;
- `evaluator_hash.py` and `evaluator-hash-known-good-v*.json`.

## 3. The refreshes (orchestrator-verified on `develop` `d76438a`)

1. **`validate-workflow-gate-verdict-sources`: fixtures.** `cmp` shows that both fixture copies differ from their
   sources:
   - `commands/validate-workflow.md` differs in its frontmatter `maturity`, since T569.
   - `skills/validation-gates/SKILL.md` differs because of T585 N1, T587 FB1/FD1 and T589 E-A1.

   Re-copy both from `implementation/knowledge/` at the `develop` commit your worktree is on, and confirm each with
   `cmp`.
2. **`validate-workflow-gate-verdict-sources`: `brief.md` § Provenance** (around `:166–177`). Rewrite the two
   bullets so that both copies are byte-identical at the `develop` commit you name.
   - Drop "this copy was not refreshed".
   - Record, in one line each, what changed in the source since the last copy, and that `check()` does not read it.
     The facts are: `maturity` (T569); § Verdict Rules note N1 (T585); § Severity Definitions FB1 (T587); § Procedures
     FD1 (T587); § Severity Definitions grading pointer E-A1 (T589).
3. **`validate-workflow-gate-verdict-sources`: `expect.py` docstring** (`:13`). It says "byte-identical fixture
   copies". After step 1 that claim is true again, so leave the docstring unchanged unless something in it is still
   false.
4. **`security-audit-critical-not-fail`: `expect.py:2`.** Change `(known_failing / tracked_defect)` to
   `(known_failing / capability_gap)`. The case was reclassified at T520, and `case.yaml` already says
   `known_failing_category: capability_gap`.
5. **`security-audit-critical-not-fail`: "must not be amended".**
   - In `case.yaml` `known_failing_reason` (around `:12`) and in the `brief.md` bullet (around `:42`), "the rule
     must not be amended" means the rule must not be *relaxed*. T582 (B3) did amend the rule, but only to make it
     stricter.
   - Reword both so they say the rule must not be relaxed. You may note that T582 tightened it.
   - Keep everything else in those passages verbatim.

## 4. Controls

- **No result changes.**
  - Before and after your edits, run both cases' `check()` and record the results. Expected:
    `validate-workflow-gate-verdict-sources` is **True** (expected_pass) and `security-audit-critical-not-fail` is
    **False** (known_failing).
  - Run `python3 scripts/scorecard.py --check` before and after. Both runs must report 34 cases / 26 pass /
    0 regressions.
  - **The re-copied `validation-gates` matters most.** `check()` reads § Gate Types, the Verdict Format's first
    `**Gate:**` line and "Every gate MUST produce a verdict". Confirm the result is unchanged with the new copy. If it
    changes, stop and report.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline.** Report both digests post-commit
  against **v16**: `tests_golden` must change from `3c50b447…`; `scripts_scorecard` must stay `45346c17…`. The
  orchestrator writes v17, which the user has pre-approved, after verifying your work.
- **Gates and suite:**
  - run `test_golden_held_out_isolation`, `test_golden_suite_format` and `validate-tasks.py`;
  - run `python3 tests/run.py`, redirecting output to a file (never `| tail`);
  - expect 904 tests with **exactly** the 2 hash failures, and name every failing test.

## 5. Constraints

- **Write scope:** §2, plus this brief's `**Status:**` line (set it to `in_review`).
- Do not read `.env*`, credential or key files. Any search reaching `tests/` must prune `tests/golden/held-out`
  first.
- Commit locally as one Conventional Commit, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  **Do not push. Never run `glab mr merge` or any merge/approve API, with no exception.**

## 6. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). If any case result would change, stop and report it.
