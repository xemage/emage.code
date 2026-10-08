# T595 — Rule P32 (production plan path and release-notes path conventions) under ADR-008 and ADR-007

**ID:** T595
**Owner:** solution-architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-108-path-conventions.md`
- `docs/plans/plan-092-poc-contract-amendments.md` §4 (P32), and `docs/artifacts/poc-contract-resolution-v1.md` §7.2
  (origin) and the P11 decision (`plan-<ID>.md` on the PoC track)
- `docs/artifacts/remaining-verdict-renderings-v1.md` §5 (G5 → P32) and §6.3 (the G7 plan path → P32)
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
  `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- The user's decision of 2026-10-08: "Next item: continue as recommended". The recommended item was P32.

## 1. What and why

### (a) The production-track plan path

Several documents name the plan file differently:

| Document | Name it uses |
|---|---|
| `/new-feature` (stable) | `docs/plans/feature-<slug>.md` |
| `plan-approve-execute` (experimental) | `plan-<feature-or-phase>.md` / `plan-<name>.md` |
| `project-planning` (experimental, after T594) | `docs/plans/project-plan-v{N}.md` |
| `orchestrator.md` and `/plan` | `docs/plans/plan-<ID>.md` |

Real plans in this repo are named `plan-<ID>-<slug>.md`. `tests/performance/test_team_health.py` globs
`docs/plans/plan-*.md` and requires every active task to be referenced by some plan. P11 already decided `plan-<ID>.md`
for the PoC track.

Rule:
- whether these clauses contradict;
- whether `<ID>` admits a `-<slug>` suffix;
- which convention governs the production track.

### (b) The release-notes duplication (G5 residual)

| Document | Path |
|---|---|
| `release-workflow` | `docs/artifacts/release-notes-v<VERSION>.md` |
| `/prepare-release` | `docs/releases/v<version>.md` |

T593 found these jointly satisfiable at Step A. The residual is a choice between two things: one document or two,
and which path. Rule whether ADR-008 decides any part of it. If it does not, escalate.

### Expected outcome

Choosing a convention is likely **a user decision (P5)**. A command change is a user decision under ADR-007. Write
the user questions so the user can decide both (a) and (b) in one round.

**Decision only.** Write exactly one file: your artifact.

## 2. Output

`docs/artifacts/path-conventions-v1.md`, containing:

1. **A D5 record for (a) and for (b).** Each record includes:
   - every clause quoted verbatim with file and line, **on the `develop` commit your worktree is on**;
   - the Step A analysis, with the one-value test;
   - the step that fired;
   - the declared-scope text;
   - the amendment (exact Before/After and a unique anchor) or "none / held until the user decides";
   - a statement that maturity was not relied on.
2. **Constraints:**
   - No upward amendment: never `AGENTS.md` or a stable instruction.
   - No command amendment without a user decision.
   - Never relax a check.
   - Earlier rulings, including P11, are inputs.
3. **Self-placement only at Step D**, per the user's Q1 decision.
4. **For each P5 escalation, a user question** containing:
   - the subject and the quotes;
   - why the steps did not decide it;
   - 2–4 options, each with its consequences: the files that change, any test or tooling impact (for example the
     `plan-*.md` glob in `test_team_health.py`), golden impact, and whether existing real plans or releases would
     need renaming;
   - your recommendation.

   For each option, hold the candidate edits with exact Before/After text so they can be applied verbatim once the
   user decides.
5. **Golden coupling.** The orchestrator pre-computed it, with held-out pruned. Read the cases by path under
   `tests/golden/open/<case>/`, and **never open `tests/golden/held-out/`**. Some open briefs written before T411
   name held-out sibling cases. **Never write a golden case name unless that case has a directory under
   `tests/golden/open/`.**

   | File | Open golden cases that cite it |
   |---|---|
   | `commands/new-feature.md` | `new-feature-checkpoint-line-compliant`, `new-feature-plan-doc-compliant`, `new-feature-real-checkpoint-format-drift` |
   | `commands/plan.md` | `plan-real-doc-header-drift`, `plan-required-sections-compliant`, `plan-task-creation-precondition-real` |
   | `commands/prepare-release.md` | `prepare-release-changelog-grouping-compliant`, `prepare-release-conditional-pass-conditions-gap`, `prepare-release-real-verdict-missing` |
   | `commands/new-poc.md` | `new-poc-plan-hypothesis-format` |
   | `skills/plan-approve-execute/SKILL.md`, `agents/orchestrator.md` | `validate-workflow-gate-verdict-sources` (cited only) |
   | `skills/{project-planning,release-workflow}/SKILL.md`, `agents/poc-orchestrator.md` | none |

   For every candidate edit, state whether it would change a quote, a fixture or a result. A change to a golden
   quote or fixture needs a protected-path grant and a user-authorized evaluator-hash baseline (v18).
6. **An amendment list, hit counts (lines and occurrences) and a summary table.**

## 3. Constraints

- **Read access:** the whole repo, except: never open `tests/golden/held-out/`, and never read `.env*`, credential
  or key files.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- **No shell:** you have none. Do not commit, push or merge.
- **Quoting:** quote verbatim and mark omissions with "…". Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/path-conventions-v1.md`, with `Based on:`.
2. There are D5 records for (a) and (b), each naming one step.
3. Every P5 escalation has a user question that meets §2.4, with its candidate edits held verbatim.
4. No amendment is upward or relaxing, and none changes a command without a user decision.
5. No golden case name appears unless its case has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). A P5 escalation is a ruling outcome, not a blocker.
