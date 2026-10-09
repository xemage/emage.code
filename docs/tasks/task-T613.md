# T613 — Rule the Scrum Master/Task Protocol conflict (P41 O2) and the third checkpoint name (T607 O7)

**ID:** T613
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-117-scrum-master-and-checkpoint-name-rulings.md`
- `docs/plans/plan-112-parked-note-cleanup.md` §2
- `docs/artifacts/remaining-verdict-renderings-v1.md` §8 (O2) and `docs/artifacts/naming-conflicts-ruling-v1.md` §2.3, §8 (O5 model, O7)
- `docs/decisions/ADR-008-knowledge-document-authority.md` (authority ranking) and `ADR-007-command-contract-authority.md`
- `AGENTS.md` § Task Protocol, § Checkpoint Protocol
- The user's instruction of 2026-10-09: "go".

## 1. What and why

Two parked notes conflict with tier-1 text (`AGENTS.md`):

- **P41 O2.** `scrum-master.md:25` "Update task status in `active-tasks.md`" and `:27` "Ensure every task entry includes: ID, title,
  assignee, status, story points, sprint, and dependencies" are in tension with `AGENTS.md:14, :18` (only orchestrators
  create/transition tasks; the ledger columns are `ID | Title | Owner | Status | Priority | Depends on | Last update`). Same shape
  as the `/new-feature:25` conflict the user resolved in T607 (O5: the Scrum Master proposes, the orchestrator creates). Re-read
  the live lines first; the line numbers may have moved.
- **T607 O7.** `checkpoint-protocol/SKILL.md` uses a third checkpoint name, `checkpoint-<N>.md` (around `:104`, `:173`, `:179`),
  against its own `:44` and `AGENTS.md` § Checkpoint Protocol (`checkpoint-<SEQ>-<phase>.md`). Re-read the live lines.

Rule each under ADR-008: which text wins, which side is amended, and the exact amendment. Where the ADR ranking does not decide
(a conflict inside tier 1), escalate to the user under P5 as a question.

**Decision only.** Write exactly one file. Every edit is held for the user. Do not edit any knowledge file. Check how widely each
conflicting clause is repeated (mirrors, other agents or skills, commands, tests, golden cases that quote them) and report hit
counts, projected paths and root-drift paths, golden and test coupling, and whether a grant or baseline would be needed. Check for
other agents or skills with the same Task Protocol conflict (for example `product-owner`, `release-manager`, `project-planning`
skill) and list them as observations, not rulings. Maturity is not relied on (ADR-008 P4).

## 2. Output

`docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md`, containing:

1. A D5 record per item (verbatim clauses with file and line on the commit your worktree is on, the Step A analysis, the step that fired, the amendment or "held for the user"), and a statement that maturity was not relied on.
2. Hit counts of every site that repeats each conflicting clause.
3. The effects (projected paths, root drift, golden and test coupling, grant or baseline).
4. **One user question** (consolidated, at most 4 options per item), with a recommendation.
5. A handoff package for the implementing task, and a summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge. Do not edit `.claude/`, `.github/` or the other derived platform folders.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. Two D5 records exist, and no amendment is applied.
3. The user question is answerable in one round and carries a recommendation.
4. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
