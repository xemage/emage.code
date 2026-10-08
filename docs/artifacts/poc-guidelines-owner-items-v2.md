# Artifact: poc-guidelines-owner-items-v2.md

> Filename: `poc-guidelines-owner-items-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T598
- **Created**: 2026-10-08
- **Supersedes**: `docs/artifacts/poc-guidelines-owner-items-v1.md`, which is left unchanged. This v2 is the **single
  implementation input**. The D5 records, the step analysis and the options' rationale stay in v1 §§3–4 and are not
  repeated here.
- **Based on:**
  - `docs/artifacts/poc-guidelines-owner-items-v1.md`.
  - The user's decisions of 2026-10-08, relayed by the orchestrator. The option labels are verbatim:
    - Q-A: **"PoC's own top dir (Recommended)"** (A2 + A2-b);
    - Q-B: **"Add Severity column (Recommended)"** (B1 + B1-b);
    - Q-C: **"Required, by narrator (Recommended)"** (C1).
  - The Security Engineer review, **CONDITIONAL_PASS**, recorded by the orchestrator as
    `docs/artifacts/security-review-poc-guidelines-owner-items-v1.md` and adopted by it verbatim. Its conditions are
    C-1 (SEC-001, MEDIUM), SEC-002 (O3, MEDIUM), I-1 and I-2. I did not read that file; its content reached me through
    the orchestrator's relay, which I reproduce verbatim in E-B1-rule and E-O3 **(the review file itself is
    unverified)**.
  - `docs/tasks/task-T598.md`; `docs/plans/plan-110-poc-guidelines-owner-items.md`;
    `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted).
- **Read at**: the worktree `/home/emage/Code/emage/worktrees/agent-solution-architect-T598`, which the orchestrator
  states is `develop` `7685de0`. Every Before text below was read from source there. Line numbers refer to that state,
  before any edit.

## 1. Decisions

| Subject | Decided | Dropped (not to be applied) |
|---|---|---|
| (a) PoC root | **A2** (the PoC's own top-level directory) + **A2-b** (plan bullet) | A1, A3 |
| (b) Per-item severity | **B1** (Severity column + Scorecard Rule 5, worded as the review's C-1) + **B1-b** (with I-2) | B2, B3 |
| (c) Legacy section | **C1** (`TECHNICAL-DEBT.md` required, written by the narrator) | C2 (with C2-b), C3, C4 (with C4-b, C4-c, C4-d) |
| (d) Three registers | **D1** (narrator note), which follows from C1 | — |
| O3 (security findings in the ledger) | **E-O3**, the review's SEC-002 | — (O3 is resolved and no longer parked) |
| Row 1 severity | **`Critical`**, kept (the review's I-1) | — |

## 2. Summary

| ID | File | Anchor (lines before any edit) | Kind | Golden quote / fixture / result | Security impact |
|---|---|---|---|---|---|
| E-A2 | `implementation/knowledge/instructions/poc-guidelines.md` | `:115–116` | Tier-1, user-decided | None | None |
| E-A2-b | `implementation/knowledge/agents/poc-orchestrator.md` | `:28–29` | Step A note | None | None |
| E-B1-table | `implementation/knowledge/instructions/poc-guidelines.md` | `:129–133` | Tier-1, user-decided | None | Row 1 (Security category) is graded `Critical`, the stricter tier |
| E-B1-rule | `implementation/knowledge/instructions/poc-guidelines.md` | `:148–149` | Tier-1, user-decided; text from the review's C-1 | None | Strengthens: it separates the debt scale from `SECURITY:*` and keeps each finding's handling |
| E-B1-b | `implementation/knowledge/skills/technical-debt-tracking/SKILL.md` | one sentence in `:145` | Step B consequence of E-B1-rule | None | None |
| E-C1 | `implementation/knowledge/instructions/poc-guidelines.md` | `:151–154` | Tier-1, user-decided | None | None |
| E-D1 | `implementation/knowledge/agents/technical-debt-narrator.md` | `:14` | Step A note | None | None |
| E-O3 | `implementation/knowledge/skills/technical-debt-tracking/SKILL.md` | `:61–64` | Security review condition (SEC-002), adopted | None | Strengthens: blocking findings are never recorded as debt, and a `SECURITY:MEDIUM` finding becomes `critical` / `must_fix_pre_prod` |

There are eight edits in four files. None touches a command, `tests/golden/**` or `scripts/scorecard.py`. No
protected-path grant is needed, and neither is an evaluator-hash v19.

**Anchors.**
- **Uniqueness.** Each Before text occurs exactly once in its file. The orchestrator verified all of v1's anchors; E-O3's
  anchor is new and I counted it by reading.
- **No overlap within a file.**
  - `poc-guidelines.md`: `:115–116`, `:129–133`, `:148–149` and `:151–154`.
  - `technical-debt-tracking`: `:61–64` (E-O3) and the `:145` sentence (E-B1-b).
- **Order.** The edits may be applied in any order. Match by text, not by line number.

## 3. Final edit texts

### E-A2 — `implementation/knowledge/instructions/poc-guidelines.md`, § Debt Scorecard › Scorecard Format

````
Before:
### Scorecard Format
Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:

After:
### Scorecard Format
The PoC root is the top-level directory of the PoC's code: the repository root when the PoC has its own repository, otherwise the directory that the PoC plan (`docs/plans/plan-<ID>.md`) names as the PoC root. Each PoC has its own PoC root and its own scorecard.

Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:
````

### E-A2-b — `implementation/knowledge/agents/poc-orchestrator.md`, § PLAN PHASE item 3

Each line starts with three spaces, as in the source.

````
Before:
   - Key risks and assumptions
   - PoC token budget

After:
   - Key risks and assumptions
   - PoC root, when the PoC does not have its own repository (`poc-guidelines.md` § Debt Scorecard › Scorecard Format)
   - PoC token budget
````

### E-B1-table — `implementation/knowledge/instructions/poc-guidelines.md`, the Debt Inventory table

The `—` in the effort cells is U+2014, as in the source.

````
Before:
| # | File | Line | Category | Description | Production Effort |
|---|------|------|----------|-------------|-------------------|
| 1 | src/db.py | 12 | Security | Hardcoded local database URL (no credentials) | S — read URL from configuration, credentials from vault |
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Reliability | No retry logic | M — add retry with backoff |

After:
| # | File | Line | Category | Description | Severity | Production Effort |
|---|------|------|----------|-------------|----------|-------------------|
| 1 | src/db.py | 12 | Security | Hardcoded local database URL (no credentials) | Critical | S — read URL from configuration, credentials from vault |
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | Critical | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Reliability | No retry logic | Medium | M — add retry with backoff |
````

### E-B1-rule — `implementation/knowledge/instructions/poc-guidelines.md`, § Scorecard Rules

The text of Rule 5 is the review's C-1, verbatim. Like Rules 1–4, it has no closing period.

````
Before:
3. The scorecard must be reviewed by the Tech Lead before the PoC is closed
4. No PoC task may be marked complete without a finalized scorecard

After:
3. The scorecard must be reviewed by the Tech Lead before the PoC is closed
4. No PoC task may be marked complete without a finalized scorecard
5. Each item must have a severity: `Critical` (must fix before production), `Medium` (should fix before production) or `Low` (nice to have). In the `## Summary`, `Total debt items` is the number of Debt Inventory rows, and each tier's count is the number of rows with that `Severity`. This severity is the debt scale, not the `SECURITY:*` scale of `security-guidelines.md` § Security Review Workflow: a debt item's `Critical` is not a `SECURITY:CRITICAL` grade, and no tag or severity here makes a shortcut that `security-guidelines.md` forbids permissible (§ Allowed Shortcuts). A security finding keeps its `SECURITY:*` grade and the handling that grade requires (`poc-orchestrator.md` § Security Findings), and its debt severity never lowers that handling: a blocking security finding is never recorded as debt, and a `SECURITY:MEDIUM` finding, whose fix is due no later than the production handoff, is `Critical` here
````

### E-B1-b — `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`, a sentence inside `:145`

This replaces one sentence inside line 145; the rest of the line is unchanged. The added "(capitalised as in Scorecard
Rule 5)" is the review's I-2.

````
Before:
Count the `## Summary` tiers from the debt ledger's per-item severity.

After:
Fill the Debt Inventory's `Severity` column with each item's debt-ledger severity (capitalised as in Scorecard Rule 5), and count the `## Summary` tiers from that column (`poc-guidelines.md` Scorecard Rule 5).
````

### E-C1 — `implementation/knowledge/instructions/poc-guidelines.md`, the Legacy section

````
Before:
## Required Debt Marking (Legacy)
When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`.

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.

After:
## Narrative Debt Register (`TECHNICAL-DEBT.md`)
Every PoC must also produce `TECHNICAL-DEBT.md`, a narrative register that explains the PoC's debt to the team that inherits it. `@technical-debt-narrator` writes it at the PoC's Debt Narration step (`poc-orchestrator.md` § PoC Workflow), from the `POC-DEBT` tags and the debt scorecard. It is not a scorecard and does not replace one: every shortcut is still recorded by its `POC-DEBT` tag when it is introduced (§ Inline Debt Tags) and inventoried in the debt scorecard (§ Debt Scorecard).

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.
````

### E-D1 — `implementation/knowledge/agents/technical-debt-narrator.md:14`

````
Before:
- TECHNICAL-DEBT.md with categorized debt

After:
- TECHNICAL-DEBT.md with categorized debt: the PoC's narrative debt register (`poc-guidelines.md`). It explains the items that `POC-DEBT-SCORECARD.md` inventories and, where the technical-debt-tracking skill's debt ledger (`docs/artifacts/debt-ledger-v{N}.md`) exists, the items that ledger records. Where it states an item's severity, effort or disposition, it uses the value the ledger records for that item, or the scorecard's value where there is no ledger. It is neither the scorecard nor the ledger, and it substitutes for neither.
````

### E-O3 — `implementation/knowledge/skills/technical-debt-tracking/SKILL.md:61–64`, Step 3

The new paragraph is the review's SEC-002, verbatim. The four Before lines are kept unchanged, and the paragraph follows
after one blank line. The emoji in `:62` are U+1F534 and U+1F7E1, as in the source.

````
Before:
Merge POC-DEBT scan results with:
- Code review findings (🔴 Must Fix and 🟡 Should Fix items)
- PoC evaluation refactoring backlog items
- Security scan findings

After:
Merge POC-DEBT scan results with:
- Code review findings (🔴 Must Fix and 🟡 Should Fix items)
- PoC evaluation refactoring backlog items
- Security scan findings

A blocking security finding, from any of these sources (`poc-orchestrator` § Security Findings: any breach of an Immutable Security Constraint in `security-guidelines.md`, any security control it requires that is omitted, removed, disabled or weakened, tagged or not, and any `SECURITY:CRITICAL` or `SECURITY:HIGH` finding), is never recorded as debt: it enters the ledger only as `resolved`, after `@poc-security-engineer` confirms the fix, never as `open`, `in-progress` or `accepted-risk` (rapid-prototyping skill § Mandatory Debt Tagging, Enforcement). Any other security finding keeps its `SECURITY:*` grade, recorded in the item's **Impact**, and its debt severity never lowers what that grade requires: a `SECURITY:MEDIUM` finding, whose fix is due no later than the production handoff, is `critical`, with disposition `must_fix_pre_prod`.
````

In the source, `:65` is blank and `:66` is "**Step 4: Produce consolidated debt ledger, then the scorecard**". After the
edit, the new paragraph is followed by that blank line and then the Step 4 heading.

## 4. Per-edit statements

**Upward.** The only tier-1 edits are E-A2, E-B1-table, E-B1-rule and E-C1. All four are user-decided instruction
changes, argued on `poc-guidelines.md`'s own text (v1 §4), not made to match a lower document. Every other edit falls on
an agent or skill, toward texts that govern it, so none is upward. No command is edited.

**Relaxation.** No check is relaxed by any edit:
- E-B1-rule adds a required field and a reconciliation rule.
- E-O3 adds a prohibition.
- E-C1 moves the `TECHNICAL-DEBT.md` documentation duty from "when introducing shortcuts" to the narrator at Debt
  Narration, as the user decided. No rule, gate or test checks that file. The checked per-shortcut record, the
  `POC-DEBT` tag (Debt Tag Rule 2; Scorecard Rule 1), is untouched.

**Golden coupling.**
- No case quotes `poc-guidelines.md:113–154`. The open cases quote only `:35–40` and `:54–56`.
- No `check()` reads any knowledge file. Each reads only its own `fixture/`.
- No golden case cites `technical-debt-tracking`, `technical-debt-narrator` or `poc-orchestrator`, so no golden quote,
  fixture or result changes for any edit.
- Descriptive texts stay true:
  - `evaluate-poc-verdict-debt-reconciliation/brief.md:77`, `:78` and `:89–90`;
  - `new-poc-plan-hypothesis-format/brief.md:70` and `:83–84`.
- **Non-golden tests.** `tests/functional/test_golden_harness_scoring.py` loads only
  `new-feature-plan-doc-compliant/expect.py` (`REAL_CASE_ID`, `:29`), which none of these edits touches, so it is
  unaffected. The orchestrator verified that no non-golden test asserts a removed string.

| Edit | Upward? | Relaxes? | Golden quote / fixture / result | Non-golden test loading a golden `expect.py` | Security impact |
|---|---|---|---|---|---|
| E-A2 | Tier-1, user-decided | No | No / No / No | Not affected | None. It defines a location only |
| E-A2-b | No (agent) | No | No / No / No | Not affected | None |
| E-B1-table | Tier-1, user-decided | No (a field is added) | No / No / No | Not affected | Row 1 (Security category, not a finding) is `Critical`, the stricter tier (I-1) |
| E-B1-rule | Tier-1, user-decided | No (it adds a requirement and a reconciliation) | No / No / No | Not affected | Strengthening: the debt tier never lowers a `SECURITY:*` handling; a blocking finding is never debt; `SECURITY:MEDIUM` ⇒ `Critical`. It restates § Allowed Shortcuts `:68` and is consistent with `poc-orchestrator.md:65–67` |
| E-B1-b | No (skill, toward the tier-1 Rule 5) | No | No / No / No | Not affected | None |
| E-C1 | Tier-1, user-decided | No check; the duty moves as decided | No / No / No | Not affected | None |
| E-D1 | No (agent) | No | No / No / No | Not affected | None |
| E-O3 | No (skill, toward `poc-orchestrator` § Security Findings, `poc-security-engineer.md:22–23` and `rapid-prototyping:74`) | No (it adds a prohibition) | No / No / No | Not affected | Strengthening. It closes O3: blocking findings enter the ledger only as `resolved`, and a `SECURITY:MEDIUM` finding is `critical` / `must_fix_pre_prod`, which the existing coupling at `:104` (`critical` ⇒ `must_fix_pre_prod`) already requires |

**Consistency checks between the new texts.**
- E-B1-rule maps `SECURITY:MEDIUM` to `Critical`, and E-O3 maps it to `critical`. These are the same tier, lowercase in
  the ledger, and E-B1-b capitalises it when it is copied into the column.
- E-O3's "must_fix_pre_prod" matches the skill's existing coupling at `:34` and `:104`.
- E-B1-rule's "§ Allowed Shortcuts" and "§ Security Review Workflow" point to sections that exist: `poc-guidelines.md`
  `## Allowed Shortcuts` (`:63`) and `security-guidelines.md` § Security Review Workflow.
- E-O3's "§ Mandatory Debt Tagging, Enforcement" exists at `rapid-prototyping:29` and `:71`.

**Tooling.**
- Regenerate the mirrors with `node implementation/scripts/sync.mjs --root implementation`.
- Regenerate the registry with `python3 implementation/scripts/generate-registry.py`.
- Run both `--check` gates.
- Declare root-projection drift in `tests/_baselines/root-install-drift.json` for the four source files, exactly as
  `--print-drift` reports it. The path count is **(unverified)**.

## 5. Hit counts

These counts were made **by reading, not with `grep`**, because I had no shell. Matching is case-sensitive. The
implementer must re-count mechanically before and after editing; see the T585 erratum precedent.

**Before texts.** Every Before text occurs once in its file: 1 occurrence, spread over 2, 2, 5, 2, 1 (inside `:145`), 4,
1 and 4 lines for E-A2, E-A2-b, E-B1-table, E-B1-rule, E-B1-b, E-C1, E-D1 and E-O3 respectively.

**Term counts, before → after all eight edits:**

| Term | File | Before (lines / occurrences) | After (lines / occurrences) | Source of the change |
|---|---|---|---|---|
| `PoC root` | `poc-guidelines.md` | 1 / 1 | 2 / 4 | E-A2's definition line adds 3 |
| | `poc-orchestrator.md` | 0 / 0 | 1 / 1 | E-A2-b |
| | `technical-debt-tracking` | 2 / 2 | 2 / 2 | unchanged |
| | `new-poc.md`, `poc-demo.md`, `poc-evaluation` | 1 / 1 each | unchanged | — |
| `TECHNICAL-DEBT.md` | `poc-guidelines.md` | 1 / 1 | 2 / 2 | E-C1: one in the heading, one in the body |
| | `technical-debt-narrator.md` | 1 / 1 | 1 / 1 | E-D1 does not repeat it |
| | `poc-orchestrator.md` | 2 / 2 | 2 / 2 | unchanged |
| `debt-ledger` | `technical-debt-tracking` | 5 / 5 | **6 / 6** | E-B1-b adds "debt-ledger severity" to `:145`, which before read "debt ledger's", with a space. E-O3 says "the ledger", without a hyphen |
| | `technical-debt-narrator.md` | 0 / 0 | 1 / 1 | E-D1 |
| `POC-DEBT-SCORECARD` | `technical-debt-narrator.md` | 0 / 0 | 1 / 1 | E-D1 |
| | `poc-guidelines.md` | 1 / 1 | 1 / 1 | unchanged |
| | `technical-debt-tracking` | 4 / 4 | 4 / 4 | unchanged |
| `Severity` | `poc-guidelines.md` | 0 / 0 | 2 / 2 | the table header and Rule 5's "`Severity`" |
| `Critical` | `poc-guidelines.md` | 1 / 1 (`:137`) | 4 / 6 | rows 1 and 2 (1 each); `:137` (1); Rule 5 (3: "`Critical` (must fix", "debt item's `Critical`", "is `Critical` here") |
| `SECURITY:*` | `poc-guidelines.md` | 0 / 0 | 1 / 2 | Rule 5 |
| | `technical-debt-tracking` | 0 / 0 | 1 / 1 | E-O3 |
| `SECURITY:CRITICAL` | `poc-guidelines.md` | 0 / 0 | 1 / 1 | Rule 5 |
| | `technical-debt-tracking` | 0 / 0 | 1 / 1 | E-O3 |
| `SECURITY:HIGH` | `technical-debt-tracking` | 0 / 0 | 1 / 1 | E-O3 |
| `SECURITY:MEDIUM` | `poc-guidelines.md` | 0 / 0 | 1 / 1 | Rule 5 |
| | `technical-debt-tracking` | 0 / 0 | 1 / 1 | E-O3 |
| `must_fix_pre_prod` | `technical-debt-tracking` | 7 / 8 | 8 / 9 | E-O3 adds 1 |
| `Required Debt Marking` | `poc-guidelines.md` | 1 / 1 | 0 / 0 | E-C1 removes it |

Before the edits, `must_fix_pre_prod` occurs at `:14`, `:34` (twice), `:91`, `:104`, `:114`, `:120` and `:154`.

## 6. Change log against v1

1. **Decisions recorded** (§1). The edit set is reduced to the decided options. A1, A3, B2, B3, C2, C2-b, C3, C4 and
   C4-b to C4-d are dropped. Their texts remain in v1 for the record only.
2. **E-B1-rule.** v1's Rule 5 is replaced with the review's C-1 text, verbatim. It adds the `SECURITY:*` scale reference,
   the preservation of each finding's grade and handling, "a blocking security finding is never recorded as debt", and
   `SECURITY:MEDIUM` ⇒ `Critical`.
3. **E-B1-b.** "(capitalised as in Scorecard Rule 5)" is added, per the review's I-2.
4. **E-O3 is new**, per the review's SEC-002. O3 is resolved and removed from the parked list.
5. **I-1.** Row 1 stays `Critical`; there is no textual change from v1.
6. **Quote correction.** v1 §4.2 quoted Debt Tag Rule 1 (`poc-guidelines.md:106`) without the source's bold. The
   verbatim text is: "1. Every `POC-DEBT` tag must describe **what** the shortcut is and **what** the production solution
   needs". In v1 the row tiers were derived from "**what** the production solution needs"; that derivation is unchanged.
7. **Hit counts recomputed** for the new texts (§5). In v1, the `debt-ledger` after-count was already 6 / 6. New rows
   cover `Severity`, `Critical`, the `SECURITY:*` grades, `must_fix_pre_prod` and `Required Debt Marking`.
8. **Unchanged from v1:** E-A2, E-A2-b, E-B1-table, E-C1 and E-D1, byte for byte. Edit IDs gain an `E-` prefix.

## 7. Parked observations (not ruled)

These are carried over from v1 §8. O3 is resolved by E-O3.

- **O1. Category sets differ.** `poc-guidelines.md:131–133` uses the example Categories "Validation" and "Reliability".
  The skill's closed set (`technical-debt-tracking:82`) has neither. This is a specialisation of an open column, not a
  conflict.
- **O2. Unversioned deliverables.** `technical-debt-narrator.md:41` says "Name output artifacts: `<type>-vN.md`", but
  `TECHNICAL-DEBT.md` and `POC-DEBT-SCORECARD.md` are unversioned single files. This is a same-file tension in boilerplate
  shared by the PoC agents.
- **O4. Indentation.** `poc-orchestrator.md:102` is indented with three spaces, while its sibling bullets use two. No v2
  edit touches it.
- **O5. Scan scope undefined.** Scorecard Rule 1 ("in the codebase") and `technical-debt-tracking:48`, which scans `.`,
  leave the scan scope undefined. E-A2 defines the PoC root, not the scan scope.
- **O6. Severity source for `/evaluate-poc`.** `/evaluate-poc`'s Debt Summary severities (`:57–59`) are not stated to
  equal the ledger's or the scorecard's values. Any note would fall on `poc-evaluation` (P2), not on the command.

## 8. Unverified

- The commit `7685de0`.
- The content of `docs/artifacts/security-review-poc-guidelines-owner-items-v1.md`. I used the orchestrator's verbatim
  relay of C-1, SEC-002, I-1 and I-2.
- Every count in §5, which I made by reading, not mechanically.
- The root-drift path count.

## 9. Blockers

None.
