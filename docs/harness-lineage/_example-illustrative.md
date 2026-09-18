> **ILLUSTRATIVE EXAMPLE ONLY — NOT A REAL RECORD.**
> **No real accepted change is recorded in this file. Every case id, diff, MR number, reviewer
> name, and scorecard value below is fictional, invented solely to demonstrate the shape of a
> real `docs/harness-lineage/harness-v<N>.md` document.** As of this file's authoring
> (2026-09-18), T505 (the human-MR-gate mechanism whose real output a real instance of this
> document would record) has not yet completed a live validation exercise, so no real,
> disclosable accepted change exists yet. Do not cite this file as evidence that any harness
> change described here actually happened. See `docs/harness-lineage/_template.md` for the
> structure a real instance must follow, and `docs/harness-lineage/README.md` for the naming
> convention. **This file must never be renamed to `harness-v1.md` or any `harness-v<N>.md`
> pattern.**

# Harness Lineage: illustrative-example — v(none — not a real instance)

**Status:** Illustrative only (fictional)
**Date:** N/A — fictional
**Accepting reviewer:** N/A — fictional

## 1. What changed

- **Target file:** `implementation/knowledge/instructions/coding-standards.md` *(fictional target,
  chosen only because it is a real, existing file of the right class — no real change was proposed
  or applied to it by this document)*
- **Target file class:** `instruction`
- **Diff summary (fictional):** a hypothetical proposal appending a "Known failure pattern" note
  documenting that generated release checklists sometimes omit a required verdict line, based on a
  hypothetical cluster of (fictional) golden-suite cases.

```diff
--- a/implementation/knowledge/instructions/coding-standards.md
+++ b/implementation/knowledge/instructions/coding-standards.md
@@
 ## Existing section (unchanged, fictional excerpt)
 ...

+## Known failure pattern (meta-improver proposal) [FICTIONAL]
+
+_Proposed automatically by `@meta-improver` from a cluster of classified failure records. This
+is a proposal only. Review before merging._
+
+- **Cause:** `established-practice-drift` [illustrative — not a real cluster assignment]
+- **Behavior:** `required-section-absent` [illustrative]
+- **Mechanism:** `whole-block-absence` [illustrative]
+- **Triggering case(s):** `fictional-case-01`, `fictional-case-02`
```

- **Rationale (as generated, fictional):** "2 classified failure record(s) (`fictional-case-01`,
  `fictional-case-02`) share the axis triple cause='established-practice-drift',
  behavior='required-section-absent', mechanism='whole-block-absence'. Target file
  'implementation/knowledge/instructions/coding-standards.md' was selected by keyword-overlap
  score 4 against the cluster's axis-derived keywords among candidate files in the four allowed
  harness-surface classes." *(This entire rationale string is fictional prose written to
  demonstrate the shape a real `DiffProposal.rationale` value takes — it was not produced by a
  real `meta_improver.generate_proposal()` call.)*

## 2. Which failure motivated it

References the real scheme structure defined in `docs/artifacts/failure-taxonomy-v1.md` — but the
specific case ids and axis assignment below are fictional and do not correspond to any real row in
that document's §4 or §8.4 tables.

- **Triggering case id(s) (fictional):** `fictional-case-01`, `fictional-case-02`
- **Cluster axis triple (fictional, but using real enumerated axis values from
  `failure-taxonomy-v1.md` §3.1–§3.3 for illustration):**
  - **Cause:** `established-practice-drift`
  - **Behavior:** `required-section-absent`
  - **Mechanism:** `whole-block-absence`
- **Link to the taxonomy entry:** N/A — `fictional-case-01`/`fictional-case-02` are invented and do
  not appear anywhere in `docs/artifacts/failure-taxonomy-v1.md`'s real §4 or §8.4 tables. A real
  instance of this document must link to a real row in one of those tables.

## 3. Before/after scorecard

Field names below are the real `PromotionResult` fields from
`implementation/runtime/golden_harness/promotion.py`'s `evaluate_promotion()`; the values are
fictional.

| Conjunct | Field | Result (fictional) |
|---|---|---|
| 1 — improvement > regression | `PromotionResult.floor_met` | `True` |
| 2 — no critical regression | `PromotionResult.no_critical_regression` | `True` |
| 3 — evaluator hash unchanged | `PromotionResult.evaluator_hash_unchanged` | `True` |
| Overall | `PromotionResult.promote` | `True` |
| Reason (fictional, verbatim-style) | `PromotionResult.reason` | "PROMOTE: all three conjuncts satisfied (floor met, no critical regression, evaluator hash unchanged)." |

- `PromotionResult.confirmed_regression_case_ids` (fictional): `()`
- `PromotionResult.mismatched_escalation_case_ids` (fictional): `()`

**Underlying pass-rate numbers (fictional):** control arm 27/30 golden cases passing (90.0%),
treatment arm 29/30 (96.7%) — invented numbers illustrating the shape a real before/after
comparison would take, not a measurement of anything real.

## 4. MR reference

- **MR (fictional):** `!000` (`https://gitlab.example.invalid/emage/emage.code/-/merge_requests/000`
  — a deliberately non-resolving placeholder URL)
- **Merge status:** Fictional — not a real MR, neither open nor merged.
- **Merge commit SHA:** N/A — fictional.

## 5. Date and accepting reviewer

- **Date approved/merged (fictional):** 2026-09-30
- **Accepting reviewer (fictional):** `jane-reviewer` — a placeholder name, not a real person or
  repository contributor.

---

> **Reminder:** this file is illustrative only. When a real accepted change exists (per T505's live
> validation exercise producing a real, disclosable MR), author a real `harness-v1.md` following
> `docs/harness-lineage/_template.md` — do not edit this file into a real record; this file stays
> permanently fictional and permanently disclosed as such.
