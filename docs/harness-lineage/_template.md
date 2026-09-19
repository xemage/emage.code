# Harness Lineage — Template

**Do not copy this file's own header verbatim into a real instance without updating it.** This is
the structural template every real `docs/harness-lineage/harness-v<N>.md` document must follow.
See `docs/harness-lineage/README.md` for the directory's purpose and the `harness-v<N>.md`
naming/versioning convention.

**Based on:** `docs/tasks/task-T506.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal `T465`,
`docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's `T465-equiv` row —
literal acceptance criterion: *"Harness lineage: `docs/harness-lineage/harness-v<N>.md` — what
changed, which failure motivated it, before/after scorecard."*), `docs/artifacts/failure-taxonomy-v1.md`
(the real `cause`/`behavior`/`mechanism` scheme §2 below cites directly),
`implementation/runtime/meta_improver.py` (the real `DiffProposal`/`FailureCluster` shapes §1–2
below cite), `implementation/runtime/golden_harness/promotion.py` (the real `PromotionResult`
shape §3 below cites).

---

# Harness Lineage: `<short-slug>` — v`<N>`

**Status:** `<Merged | Open | Rejected>`
**Date:** `<YYYY-MM-DD>` — the date the MR referenced in §4 was opened, or (once merged) the date
it merged. State explicitly which.
**Accepting reviewer:** `<name/handle, or "not yet reviewed" if the MR is still open>`

## 1. What changed

- **Target file:** `<repo-root-relative POSIX path — `DiffProposal.target_path`>`
- **Target file class:** `<agent | skill | command | instruction — `DiffProposal.target_file_class`>`
- **Diff summary:** a short prose description of the change, plus either the real
  `DiffProposal.diff_text()` output embedded in a fenced diff block, or a link to it (e.g. the MR's
  own diff view). Do not hand-summarize the diff without also citing or embedding the real
  generated text — a reader must be able to verify the summary against the actual change.

```diff
<embed the real DiffProposal.diff_text() output here, or link to the MR diff>
```

- **Rationale (as generated):** the real `DiffProposal.rationale` string this proposal carried at
  generation time (see `implementation/runtime/meta_improver.py`'s `DiffProposal.rationale` field
  and `generate_proposal()`'s rationale-construction logic).

## 2. Which failure motivated it

Cites `docs/artifacts/failure-taxonomy-v1.md`'s real `cause` × `behavior` × `mechanism` scheme
directly — do not reinvent a different taxonomy for this section.

- **Triggering case id(s):** `<DiffProposal.based_on — the FailureRecord.case_id values>`
- **Cluster axis triple** (`FailureCluster.cause` / `.behavior` / `.mechanism`, per
  `implementation/runtime/meta_improver.py`'s `FailureCluster`):
  - **Cause:** `<one of failure-taxonomy-v1.md §3.1's enumerated values>`
  - **Behavior:** `<one of failure-taxonomy-v1.md §3.2's enumerated values>`
  - **Mechanism:** `<one of failure-taxonomy-v1.md §3.3's enumerated values>`
- **Link to the taxonomy entry:** point to the specific row(s) in
  `docs/artifacts/failure-taxonomy-v1.md` §4's case-by-case axis-assignment table (or, for a
  Terminal-Bench-sourced cluster, §8.4's pattern table) that the triggering case id(s) above
  correspond to.

## 3. Before/after scorecard

Cites the real `PromotionResult` fields from `implementation/runtime/golden_harness/promotion.py`'s
`evaluate_promotion()` — present these as an actual before/after comparison, not merely a
pass/fail restatement.

| Conjunct | Field | Result |
|---|---|---|
| 1 — improvement > regression | `PromotionResult.floor_met` | `<True/False>` |
| 2 — no critical regression | `PromotionResult.no_critical_regression` | `<True/False>` |
| 3 — evaluator hash unchanged | `PromotionResult.evaluator_hash_unchanged` | `<True/False>` |
| Overall | `PromotionResult.promote` | `<True/False>` |
| Reason (verbatim) | `PromotionResult.reason` | `<the real reason string>` |

If either conjunct 2 produced any non-empty case-id tuples, list them:

- `PromotionResult.confirmed_regression_case_ids`: `<tuple, or "()" if empty>`
- `PromotionResult.mismatched_escalation_case_ids`: `<tuple, or "()" if empty>`

**Underlying pass-rate numbers (if available):** control-arm and treatment-arm aggregate pass
rates (and per-case k-count where relevant), sourced from the same `TrialRecord` set passed into
`evaluate_promotion()`. Include these whenever the validation run that produced this
`PromotionResult` also recorded them — do not omit real numbers that exist just because the
`PromotionResult` fields alone are sufficient to satisfy the letter of this section.

## 4. MR reference

- **MR:** `<real MR number/URL>`
- **Merge status:** `<Merged (commit `<sha>`) | Open, not yet merged | Rejected>` — state this
  explicitly; never imply a merge that has not happened.
- **Merge commit SHA:** `<sha, once merged; omit or mark "N/A — not yet merged" otherwise>`

## 5. Date and accepting reviewer

- **Date approved/merged:** `<YYYY-MM-DD>`
- **Accepting reviewer:** `<name/handle>` — per `plan-035`'s own literal T464 acceptance criterion
  ("no path exists by which a proposal reaches `develop` without human approval"), this section is
  part of that human-approval trail's own record, not an independent claim. The reviewer named here
  must match the real approver recorded on the MR referenced in §4.
