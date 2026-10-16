# T598 — Rule P33 (poc-guidelines owner items and the three debt registers) under ADR-008

**ID:** T598
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-110-poc-guidelines-owner-items.md`
- `docs/artifacts/poc-contract-resolution-v1.md` §7.4 (origin of P33) and the P29 decision (`POC-DEBT-SCORECARD.md`
  in the PoC root; S/M/L effort plus CRITICAL/MEDIUM/LOW severity in `/evaluate-poc`)
- `docs/artifacts/poc-skills-alignment-v1.md` F5 (the three debt registers, folded into P33)
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
  `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- The user's instruction of 2026-10-08: "continue". The recommended next item was P33.

## 1. What and why

`poc-guidelines.md` is a **stable instruction (tier 1)**. Under ADR-008, any change to a tier-1 document's own text is
**never routine**: it is a user decision. Rule each subject below. Where the answer is an edit to `poc-guidelines.md`
itself, write it as a user question with the candidate edits held verbatim.

Rule the four subjects:

- **(a) "PoC root" is undefined.**
  - § Scorecard Format reads "Create a `POC-DEBT-SCORECARD.md` file in the PoC root". Find every document that uses
    "PoC root" or places PoC files, for example `/new-poc` and `poc-orchestrator`.
  - Rule whether any of them defines or places the PoC root. If one does, it may be a Step A note. If none does,
    escalate.
- **(b) The Debt Inventory has no per-item severity column.**
  - The scorecard's Debt Inventory table has `| # | File | Line | Category | Description | Production Effort |`.
  - Its § Summary counts "Critical (must fix before production)", "Medium" and "Low".
  - The P29 decision gave `/evaluate-poc` S/M/L effort plus CRITICAL/MEDIUM/LOW severity.
  - Rule whether the scorecard's Summary is computable from its own table. If it is not, decide what fills the gap.
- **(c) The Legacy section is ambiguous.** "## Required Debt Marking (Legacy)" still says "update
  `TECHNICAL-DEBT.md`", while the note says `POC-DEBT` tags supersede the legacy `DEBT:` format. Rule whether
  `TECHNICAL-DEBT.md` is still required, optional or retired.
- **(d) F5: the three debt registers** are `TECHNICAL-DEBT.md` (the `technical-debt-narrator` agent),
  `debt-ledger-v{N}.md` (the `technical-debt-tracking` skill) and the scorecard's Debt Inventory. No text relates the
  first two. Rule whether they conflict or can coexist, and how they relate.

**Decision only.** Write exactly one file, your artifact. The orchestrator verifies it, and the user decides every
P5 escalation and every change to tier-1 or command text. Implementation is a separate task.

## 2. Output

`docs/artifacts/poc-guidelines-owner-items-v1.md`, containing:

1. **A D5 record per subject (a) to (d).** Each record has:
   - every clause, quoted verbatim with file and line, **on the `develop` commit your worktree is on**;
   - the Step A analysis, with the one-value test;
   - the step that fired;
   - the declared-scope text;
   - the amendment, as exact Before/After text with a unique anchor, or "none / held until the user decides";
   - a statement that maturity was not relied on.
2. **Constraints on amendments:**
   - never upward on ADR-008's own authority;
   - a `poc-guidelines.md` or command edit only as a user-decided option;
   - never relax a check;
   - never weaken any security rule or Immutable Security Constraint;
   - earlier rulings (P11, P29, P30, P31, P35, P38, P42, O1) are inputs.
3. **Self-placement only at Step D**, per the user's Q1 decision.
4. **For each P5 escalation, a user question:** the subject, the quotes, why the steps did not decide it, and 2–4
   options with their consequences (files, golden impact, tooling, effect on existing PoCs). End with your
   recommendation. Hold the candidate edits verbatim for each option. Design the questions so the user can decide
   them all in one round.
5. **Golden coupling.** The orchestrator pre-computed it, with held-out pruned. Read cases by path under
   `tests/golden/open/<case>/`. **Never open `tests/golden/held-out/`.** **Never write a golden case name unless that
   case has a `tests/golden/open/` directory.**

   | File | Open golden cases that cite it |
   |---|---|
   | `instructions/poc-guidelines.md` | `evaluate-poc-verdict-debt-reconciliation`, `new-poc-plan-hypothesis-format`, `poc-demo-hypothesis-status-evidence-gaps` |
   | `skills/poc-evaluation/SKILL.md`, `commands/evaluate-poc.md` | `evaluate-poc-verdict-debt-reconciliation` |
   | `commands/new-poc.md` | `new-poc-plan-hypothesis-format` |
   | `skills/technical-debt-tracking/SKILL.md`, `agents/technical-debt-narrator.md`, `agents/poc-orchestrator.md`, `skills/rapid-prototyping/SKILL.md` | none (cited) |

   No non-golden test asserts `POC-DEBT-SCORECARD`, "PoC root", `TECHNICAL-DEBT.md` or `debt-ledger`. For every
   candidate edit, state whether it would change a golden quote, fixture or result. Also name any **non-golden test
   that loads a golden case's `expect.py`** whose behaviour the edit could affect.
6. **An amendment list, hit counts (lines and occurrences), and a summary table.**

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/` (never open it), `.env*`, and any credential or
  key file.
- **Write access:** your artifact only, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge.
- Quote verbatim, and mark omissions with "…". Mark anything you did not re-read as **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/poc-guidelines-owner-items-v1.md`, with `Based on:`.
2. There are four D5 records, each naming one step.
3. Every P5 escalation has a user question that meets §2.4, with candidate edits held verbatim.
4. No amendment is upward, relaxing or security-weakening. No tier-1 or command edit appears except as a
   user-decided option.
5. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker.
