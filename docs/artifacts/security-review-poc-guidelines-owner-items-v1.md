# Artifact: security-review-poc-guidelines-owner-items-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only). The orchestrator recorded this from the reviewer's report, because the
  agent has no write tool.
- **Task**: T598 (plan-110). A security review of the user-chosen edits A2 + A2-b, B1 + B1-b, C1 and D1 in
  `poc-guidelines-owner-items-v1.md`, plus observation O3.
- **Date**: 2026-10-08
- **User decisions under review (2026-10-08)**: Q-A "PoC's own top dir (Recommended)"; Q-B "Add Severity column
  (Recommended)"; Q-C "Required, by narrator (Recommended)".
- **Based on**: `poc-guidelines-owner-items-v1.md`, and these files under `implementation/knowledge/`:
  `instructions/poc-guidelines.md`, `instructions/security-guidelines.md`, `skills/technical-debt-tracking/SKILL.md`,
  `skills/rapid-prototyping/SKILL.md`, `skills/validation-gates/SKILL.md`, `agents/poc-security-engineer.md`,
  `agents/poc-orchestrator.md` and `agents/technical-debt-narrator.md`.

## Verdict

**CONDITIONAL_PASS.** There are 0 critical findings, 0 high and 2 medium. None of the chosen edits removes or weakens
a security control or breaches an Immutable Security Constraint. Rule 5 separates the debt scale from the `SECURITY:*`
scale, and its closing clause keeps a tag from making a forbidden shortcut permissible. Two gaps remain, and the
orchestrator adopted both fixes verbatim in `poc-guidelines-owner-items-v2.md`:

- Rule 5 sets no floor, so a debt tier could understate a security finding (SEC-001).
- The debt-tracking skill merges security findings into its ledger without the blocking-class rule (SEC-002, O3).

## Findings

| ID | Severity | Concerns | Disposition |
|---|---|---|---|
| SEC-001 | `SECURITY:MEDIUM` (A04; condition C-1) | B1's Rule 5 ("grades debt items, not security findings") sets no floor. On the PoC path that does not use the skill, a `SECURITY:MEDIUM` finding, whose fix is due by the production handoff (`poc-orchestrator.md:66`), could be recorded as `Medium` or `Low` debt. That would understate the scorecard's Critical count and its Go/No-Go recommendation. | Adopted. Rule 5 now says: a security finding keeps its `SECURITY:*` grade and handling; a blocking finding is never recorded as debt; a `SECURITY:MEDIUM` finding is `Critical` debt. |
| SEC-002 | `SECURITY:MEDIUM` (A04) | O3. `technical-debt-tracking:61–64` merges "Security scan findings" (and 🔴 Must Fix review findings) into the ledger with no blocking-class exclusion and no rule that they enter only as `resolved`. Its `accepted-risk` status and `monitor_only` disposition would allow an open blocking finding to be recorded as debt, which `poc-orchestrator.md:65`, `poc-security-engineer.md:22`, `rapid-prototyping:74` and `validation-gates:70` all forbid. | Adopted as a new edit, E-O3, in `technical-debt-tracking`. |
| I-1 | informational | Example row 1 (hardcoded local DB URL, no credentials, TLS `verify-full`) is debt `Critical`, while `technical-debt-tracking:101` lists "hardcoded configuration" as `medium`. | Keep `Critical`. It is not a security finding, and on the tag's "must" wording the stricter debt tier is the safe direction. |
| I-2 | informational | B1-b copies the ledger's lowercase values, but Rule 5 uses capitalised tiers. | Adopted: "(capitalised as in Scorecard Rule 5)". |

## C1, D1, A2 and A2-b

None of these touches a security criterion:
- **C1** changes who writes the narrative register.
- **D1** sets the source of the narrative register's values. E-O3 closes the only path by which D1 could carry an
  open blocking finding.
- **A2 and A2-b** only define paths.

## Orchestrator verification of the reviewer's citations

At `develop` `7685de0`, the orchestrator confirmed that each of these says what the review relies on:
- `poc-orchestrator.md:65–67`: the blocking, MEDIUM and LOW handling;
- `poc-security-engineer.md:22–23`;
- `rapid-prototyping/SKILL.md:74`: "It enters the debt ledger only as `resolved`, never as `open`, `in-progress` or
  `accepted-risk`";
- `technical-debt-tracking/SKILL.md:61–64`.

"Security scan findings" appears only at `technical-debt-tracking:64` in the knowledge sources.

## Conditions to carry forward

- **SEC-001 (C-1).** Owner: the implementing task. Due: before its merge.
- **SEC-002 (E-O3).** Owner: the implementing task. Due: before its merge, folded into the same task.

Both are in v2's edit text, so applying v2 verbatim satisfies them. The orchestrator verifies this.
