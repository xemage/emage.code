# T621 — Rule the remaining task-protocol and PoC-track observations (P41 O4, P33 O1/O2/O5/O6, O-8 priority mapping)

**ID:** T621
**Owner:** solution-architect
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-120-release-v8-readiness.md`
- `docs/plans/plan-112-parked-note-cleanup.md` §2
- `docs/artifacts/remaining-verdict-renderings-v1.md` §8 (O4) and `docs/artifacts/poc-guidelines-owner-items-v2.md` §7 (O1, O2, O5, O6)
- `docs/artifacts/task-protocol-observations-ruling-v1.md` (O-8) and `docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md`, `ADR-007-command-contract-authority.md`, `AGENTS.md`
- The user's decisions of 2026-10-09 on the release-readiness question (verbatim): "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B" (point numbers refer to the orchestrator's message listing six open points: 1 breaking changes and migration notes = release-level audit and Migration section; 2 release-level gates and sign-offs = the full sequence; 3 CI release job's third release-notes.md = fix first; 4 maturity = the user authorizes evaluator baseline v21 and asks for a re-evaluation plan and the steps to bring `orchestrator` and `tech-lead` out of `experimental`; 5 known residuals = fix all first; 6 plumbing = API fallback plan for branch and tag steps).

## 1. What and why

The user decided to fix every residual before the release. Give each of these a disposition with the exact held amendment where a real conflict exists, re-reading the live lines first (many files changed since those artifacts were written): **P41 O4** (`orchestrator.md` pointer to `validation-gates` `(after core implementation)`), **P33 O1** (debt category sets: the example Categories `Validation`/`Reliability` in `poc-guidelines.md` against the skill's closed set in `technical-debt-tracking`), **P33 O2** (`technical-debt-narrator` `Name output artifacts: <type>-vN.md` against the unversioned `TECHNICAL-DEBT.md` and `POC-DEBT-SCORECARD.md`), **P33 O5** (the scan scope for `POC-DEBT` tags is undefined: Scorecard Rule 1 "in the codebase" and `technical-debt-tracking` scanning `.`), **P33 O6** (`/evaluate-poc` Debt Summary severities not stated to equal the ledger's or the scorecard's values), and **O-8** (no documented mapping from the GitLab `priority::critical/high/medium/low` labels to the ledger priorities `P0`/`P1`/`P2`; the only statement is `commands/bug-report.md:54`: critical to P0, high to P0, medium to P1, low to P2 — decide where a mapping belongs, draft it from that statement, and say whether it needs the user's confirmation). Precedent (do not re-litigate): amend the agent, skill or command toward `AGENTS.md`; Step A readings need no edit. `poc-guidelines.md` is tier-1-adjacent instruction text: if an item is a conflict inside tier 1, escalate under P5 as a question. Decision only. Report hit counts, projected paths and root-drift paths, golden and test coupling (open cases only; held-out coupling is unknown and not checked), and whether a grant or baseline would be needed (a golden file edit would need the file-scoped grant and baseline v21).

## 2. Output

`docs/artifacts/remaining-observations-ruling-v1.md`: a disposition table, D5 records for the real conflicts with held Before/After fences, hit counts, effects, ONE consolidated user question (grouped, at most 4 options per group, a recommendation each), a handoff package and a summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge. Do not edit `.claude/`, `.github/` or the other derived platform folders.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`; every listed item has a disposition.
2. No amendment is applied; the user question is answerable in one round.
3. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
