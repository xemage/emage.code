# plan-101 — Fourth root refresh, and the golden quote refresh (FU-2) under a user-approved v16

**Created:** 2026-10-07
**Based on:** the user's decisions of 2026-10-07 ("Root refresh: yes, please"; "FU-2: approval for v16 baseline");
`docs/plans/plan-100-conditional-pass-and-authority-adr.md` §5.
**Scopes:** `T583`.

## 1. Root refresh

The fourth `--projections-only` refresh follows the plan-082 §2 procedure. It was rehearsed first. It refreshed the
51 paths that T582 left stale, and drift is now 0. Recorded in MR !485. It needs no ledger row.

## 2. FU-2: T583

Three open golden cases quote text that T582 amended:

- `code-review-conditional-pass-conditions-gap`
- `security-audit-critical-not-fail`
- `prepare-release-conditional-pass-conditions-gap`

In addition, `validate-workflow-gate-verdict-sources` holds a fixture copy of `validation-gates` that is no longer
byte-identical to its source.

Each `check()` reads only its fixture, so **no result changes**. T583 refreshes the quotes and the provenance, and
re-copies the fixture. It also fixes the `new-poc` docstring that still calls P11 "parked".

- **Owner:** QA Engineer.
- **Grant:** a file-scoped `protected-paths-v1.md` §5 grant.
- **Logic:** no `check()` logic changes.

Two evaluator-hash tests go red as designed. **The user pre-approved v16 on 2026-10-07.** The orchestrator writes the
v16 baseline only after independently verifying T583:

- quotes are verbatim;
- results are unchanged;
- the scorecard is unchanged;
- the fixture copy is `cmp`-identical;
- the suite shows exactly the two hash failures.

## 3. Not in scope

**P44** (the `evaluate-poc` case counts numbered backlog lines while the skill's template uses a table) needs a
`check()` change. It stays parked for its own task.

## 4. Outcome and follow-up (2026-10-07)

- **Done:** root refresh 4 (MR !485), T583 (MR !487), and evaluator-hash baseline **v16** (user-approved, written after
  independent verification). The queue is empty.
- **FU-8 (parked; needs its own protected-path grant).** T583 reported residual staleness outside its grant:
  - the `validate-workflow-gate-verdict-sources` fixture copy of `commands/validate-workflow.md` is still at `a6be6b0`
    (it differs only in frontmatter `maturity`, which `check()` does not read), while its `expect.py` docstring still
    calls the copy "byte-identical";
  - the `security-audit-critical-not-fail` `expect.py` docstring header still says `known_failing / tracked_defect`
    (the case was reclassified to `capability_gap` at T520), and its case text says the rule "must not be amended"
    where "must not be relaxed" is meant.

  Any fix changes `tests_golden` and needs a user-authorized v17.
