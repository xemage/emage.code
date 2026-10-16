# Artifact: security-review-t608-placeholder-flag-text-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no write tool). Recorded by the orchestrator from the reviewer's two reports.
- **Task**: T608 (plan-114), applied diff of E-P1, E-O1 and E-P2. First review on commit `07ecbb9`, re-check on the amended commit `8d3663d`.
- **Based on**: `placeholder-flag-ruling-v3.md`, `security-review-placeholder-flag-ruling-v3.md`.
- **Date**: 2026-10-09. The reviewer read the files; it ran no tests and no `git diff`.

## Round 1 (07ecbb9): CONDITIONAL_PASS

The edits were faithful to v3 §6 and satisfied V3-1, V3-3, V3-4, V3-5 and V3-8. 0 critical, 0 high, 1 medium, 4 low.

| ID | Grade | Concern | Outcome |
|---|---|---|---|
| SEC-1 | MEDIUM | The second list (paths the reviewed branch changed against `develop`) failed open: with no list in the brief, "the register path is not among them" is vacuously true. | Fixed: E-P1 voids the flag when the list is unavailable or unstated; E-O1 says "if either list is unavailable, say so, and every flag is void"; pins added. |
| SEC-2 | LOW | "Real at once" side effects: file-name hits for non-template names, and "looks like a placeholder" wording. | Fixed: two real-at-once cases added; the held sentence was merged into the criteria sentence; wording is "unresolved hit, proposed flag, unverified by the reviewer". |
| SEC-3 | LOW | Provider-token rules not enumerated. | Fixed: 11 ids listed once; a test checks them against `poc_scan.RULES`. |
| SEC-4 | LOW | `dummy-word` listed for `bearer-token`; E-P2 punctuation. | Fixed. |
| SEC-5 | LOW | Missing pins (user-only creator, register on `develop`, blocker wording, and others). | Fixed: 20 pins. |

## Round 2 re-check (8d3663d): PASS

SEC-1..SEC-5 closed. The "If no flag exists, every hit stays unresolved or blocking" rewrite is not weaker. The merged
SEC-2 sentence gives every hit exactly one of two states (real at once, or unresolved with a proposal). F-8, E1-b, E1-c and
both tool lists are unchanged. No required control is weakened and no Immutable Security Constraint is breached. 0 critical,
0 high, 0 medium, 3 low.

| ID | Grade | Concern | Owner / disposition |
|---|---|---|---|
| SEC-6 | LOW | The re-read of the line is optional for content-rule hits that fit no class, so the reviewer's duty to classify is narrower than in the held edit (gate effect unchanged: still FAIL). | Tracked debt; picked up in T609 (it edits the same bullets). |
| SEC-7 | LOW | The "unverified by the reviewer" label would also be put on class proposals the reviewer did re-read. | Tracked debt; T609. |
| SEC-8 | LOW | "Provider-token rules may be flagged only when..." is not tied to the enumerated list; a future provider rule would be flaggable as plain user-attested. | Tracked debt; T609 (reword to "the rules listed above" and add a drift test over the provider ids in `RULES`). |

Observation: the E-P2 clause "a URL whose scheme is 32 or more characters long" slightly overstates the blind spot (the regex is
unanchored). It errs on the safe side and is pinned by V3-8.

**Scan-limit statement:** a clean scan covers only the fixed rule set of the `poc_scan` tool and excludes the blind-spot values listed in E-P2.
