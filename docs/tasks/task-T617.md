# T617 — Rule the twelve observations of the T615 ruling (O-1..O-12)

**ID:** T617
**Owner:** solution-architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-119-task-protocol-observations-o1-o12.md`
- `docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md` §7 (the twelve observations with quotes and readings), §4.6, §5.2 and §5.4
- `docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` (the S1/S2/K model) and `docs/artifacts/naming-conflicts-ruling-v1.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md` and `ADR-007-command-contract-authority.md`
- `AGENTS.md` § Lifecycle States, § Task Protocol, § Blocker Protocol, § Checkpoint Protocol
- The user's instruction of 2026-10-09: "Continue with the twelve observations".

## 1. What and why

Give every observation O-1..O-12 a disposition, re-reading the live lines first (T608 to T616 changed several files; line numbers
in the T615 artifact may be stale). Dispositions: **rule** (a real conflict: D5 record, which text wins under ADR-008, the exact
held amendment), **Step A holds / no edit** (with the reason), **typo or same-file defect** (the exact held fix), **lookalike**
(record), or **not a knowledge file** (O-11: report only; the orchestrator tidies the ledger note). The ones the T615 reviewer called most
likely to need a ruling: O-1 (blocker severity scale `critical|high|medium|low` against `AGENTS.md:48` `critical|major|minor`; also
`team-status` and `validate-workflow` use the longer scale), O-2 (`commands/prepare-release.md:29` names `checkpoint-release-v<version>.md`
without `<SEQ>`), O-3 (`release-workflow` and `orchestrator.md:146` assume `done` rows in `active-tasks.md`), O-4 (passive follow-up logging
to the active ledger in code-review, testing-strategy and ci-cd-pipeline, plus a "target sprint" field the ledger lacks). Also decide
O-7 (the `NEVER T001` typo in `task-management`), O-8 and O-9 (priority and column mappings between GitLab/plan tables and the ledger:
is a documented mapping needed, and where), and O-10 (`Assignee` against `Owner` in the checkpoint skill and template).

The user's earlier decisions are precedent (do not re-litigate): amend the agent, skill or command toward `AGENTS.md`; the orchestrator
writes the ledger; the ledger has seven columns. A conflict inside tier 1 (for example, whether the blocker severity set should change in
`AGENTS.md`) escalates to the user under P5 as a question.

**O-2 is a command in the golden suite's scope.** Report, for every edit that touches a command: the open golden cases that quote the old text
(read `tests/golden/open/` only), whether a protected-path grant or a new evaluator baseline (v21) would be needed, and say explicitly that
held-out coupling is unknown and was not checked. Do not design around the held-out folder.

**Decision only.** Write exactly one file. Every edit is held for the user. Do not edit any knowledge file. Report hit counts of every site
repeating each conflicting clause, projected paths and root-drift paths, golden and test coupling, and whether a grant or baseline would be
needed. Maturity is not relied on (ADR-008 P4). Keep the user question consolidated and answerable in one round (group related items; give
a recommendation for each group).

## 2. Output

`docs/artifacts/task-protocol-observations-ruling-v1.md`, containing:

1. A disposition table for O-1..O-12, then a D5 record for every item with disposition "rule" (verbatim clauses with file and line on the commit your worktree is on, the Step A analysis, the step that fired, the amendment or "held for the user"), and a statement that maturity was not relied on.
2. Hit counts of every site that repeats each conflicting clause.
3. The effects (projected paths, root drift, golden and test coupling, grant or baseline).
4. **A consolidated user question** (grouped items, at most 4 options per group), with a recommendation per group.
5. A handoff package for the implementing task(s), any further observations, and a summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge. Do not edit `.claude/`, `.github/` or the other derived platform folders.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. Every observation O-1..O-12 has a disposition; every "rule" item has a D5 record; no amendment is applied.
3. The user question is answerable in one round and carries a recommendation per group.
4. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
