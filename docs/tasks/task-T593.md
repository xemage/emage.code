# T593 — Rule P41 (remaining verdict renderings and editorial items G3–G9) under ADR-008 and ADR-007

**ID:** T593
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-107-remaining-verdict-renderings.md`
- `docs/artifacts/gate-verdict-consistency-v1.md`: §7 G3–G9, §13.1 (the six renderings, confirmed) and §13.3 (P41)
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
  `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- These artifacts are inputs, and none of them is reopened:
  - `conditional-pass-semantics-v4.md` (P39)
  - `adr-008-rulings-p40-p43-v3.md` (P40/P43)
  - `security-gate-alignment-v2.md`
  - `security-finding-grading-and-owasp-run-v2.md`
  - `security-grade-definitions-v2.md`
- The user's instruction of 2026-10-08, "Continue with the next best step"; the recommended step was P41.

## 1. What and why

`gate-verdict-consistency-v1.md` (T572) ruled the core verdict format and parked the rest as P41. Rule each item
below under ADR-008, with ADR-007 governing any command clause. Re-read every cited line on your commit: many files
have changed since T572.

- **G3: six further verdict renderings.**
  - The renderings: `qa-engineer`, `security-engineer`, `release-manager`, `/code-review`, `/security-audit` and
    `release-workflow`.
  - T572 §1.2 said each one "maps onto a single kind and none excludes the canonical block".
  - Rule whether each one is jointly satisfiable with `validation-gates` § Verdict Format, as T572 did for the first
    seven. If one is, an accompanying note may be enough, or nothing at all.
- **G4: the release gate executor.** Three documents disagree:
  - `/prepare-release` (`agent: "orchestrator"`, "**Release manager**: orchestrator");
  - `validation-gates` § Gate Types (Release → Release Manager);
  - `orchestrator.md`, which delegates the RELEASE GATE to `@release-manager`.

  `validation-gates` also says "Gate executors should not review their own work". This is a command clause against
  a skill and an agent, so ADR-008 P2 and ADR-007 apply. **A command change is only possible as a user decision.**
  Expect a P5 escalation.
- **G5: two release-notes paths.**
  - `release-workflow` uses `docs/artifacts/release-notes-v<VERSION>.md`.
  - `/prepare-release` uses `docs/releases/v<version>.md`.

  This belongs to the P32 path family. Rule it, or state why it should join P32.
- **G6: second verdict vocabularies in the same file.**
  - `code-review` has `### Verdict: [Approved | Changes Requested | Needs Discussion]`.
  - `tech-lead` has `### Status: [Approved | …]`.

  Both sit next to the `PASS`/`CONDITIONAL_PASS`/`FAIL` verdict. Rule whether they can coexist, how they map, and
  what "Needs Discussion" maps to.
- **G7: `project-planning` defects.**
  - The `### T{ID}` task block with `Priority: must | should | could`, against `AGENTS.md` § Task Protocol
    (`P0`/`P1`/`P2`).
  - The lifecycle `pending → in-progress → review → done`, against `AGENTS.md` (`pending → in_progress → blocked →
    in_review → done | cancelled`).
  - The plan path `docs/plans/project-plan-v{N}.md`. This joins P32: note it, but do not rule it.
- **G8** (lowercase tokens) and **G9** (`orchestrator` timing wording) were "noted only" at T572. Confirm or revise
  that disposition briefly.

**Decision only.** Write exactly one file, your artifact. Every proposed amendment then gets an orchestrator check
(and a Security Engineer review if it touches security criteria). The user decides every P5 escalation and any
command change.

## 2. Output

`docs/artifacts/remaining-verdict-renderings-v1.md`, containing:

1. **A D5 record per item** (G3 may group the six renderings, but each still gets its own one-value test). Each
   record has:
   - every clause quoted verbatim with file and line, **on the `develop` commit your worktree is on**;
   - the Step A analysis, with the one-value test;
   - the step that fired;
   - the declared-scope text;
   - the amendment (exact Before/After and a unique anchor) or "none";
   - a statement that maturity was not relied on.
2. **Constraints on amendments:**
   - No upward amendment: never `AGENTS.md` or a stable instruction.
   - No command amendment without a user decision (ADR-007).
   - Never relax a check.
   - No inputs listed above may be reopened.
3. **Self-placement only at Step D**, per the user's Q1 decision. For each P5 escalation, write a user question:
   the subject, the quotes, why the steps did not decide it, 2–4 options with their consequences, and your
   recommendation.
4. **Golden coupling.** The orchestrator pre-computed it, with held-out pruned. Read the cases by path under
   `tests/golden/open/<case>/`, and **never open `tests/golden/held-out/`**. Some open briefs written before T411 name
   held-out sibling cases. **Never copy any golden case name into your artifact unless the case has a directory under
   `tests/golden/open/`.**

   | File | Open golden cases |
   |---|---|
   | `commands/prepare-release.md` | `prepare-release-changelog-grouping-compliant`, `prepare-release-conditional-pass-conditions-gap`, `prepare-release-real-verdict-missing` |
   | `commands/code-review.md`, `skills/code-review/SKILL.md` | `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` |
   | `commands/security-audit.md` | `security-audit-coverage-consistency`, `security-audit-critical-not-fail`, `security-audit-verdict-fields-compliant` |
   | `agents/orchestrator.md` | `validate-workflow-gate-verdict-sources` (cited) |
   | `agents/{qa-engineer,security-engineer,release-manager,tech-lead}.md`, `skills/{release-workflow,project-planning}/SKILL.md` | none |

   For each amendment, state whether a quote, a fixture or a result would change. A change to a golden quote or
   fixture needs a protected-path grant and a user-authorized evaluator-hash baseline.
5. **An amendment list, hit counts (line count and occurrence count) and a summary table.**

## 3. Constraints

- **Read access:** the whole repo except `tests/golden/held-out/` (never open it), `.env*`, and credential or key
  files.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge.
- Quote verbatim, and mark omissions with "…". Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/remaining-verdict-renderings-v1.md`, with `Based on:`.
2. Every item G3–G9 is accounted for: ruled, escalated, or explicitly deferred to P32 with a reason.
3. No ruling relies on maturity, corpus counts, majority practice or golden-coupling convenience.
4. Every amendment has exact Before/After text, is neither upward nor relaxing, and states its golden coupling.
5. Every P5 escalation has a user question that meets §2.3.
6. No golden case name appears except those with a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker.
