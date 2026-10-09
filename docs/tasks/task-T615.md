# T615 — Rule the task-protocol conflicts in four skills (blocker-escalation, task-management, gitlab-management, dependency-graphing)

**ID:** T615
**Owner:** solution-architect
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-118-task-protocol-skill-conflicts.md`
- `docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` §2 (the S1/S2 model), §4.3 and §7 (the observations)
- `docs/decisions/ADR-008-knowledge-document-authority.md` and `ADR-007-command-contract-authority.md`
- `AGENTS.md` § Lifecycle States, § Task Protocol
- The user's instruction of 2026-10-09: "Continue with the four-skill ruling".

## 1. What and why

The T613 ruling listed these observations (not ruled). Re-read the live lines first; line numbers may have moved:

- **`skills/blocker-escalation/SKILL.md:78`** — "Transition the impacted task(s) to `blocked` status in `active-tasks.md`" in the agent procedure; against `AGENTS.md` ("Only orchestrators create/transition tasks. Agents report completion and blockers."). Strongest match; same shape as S1.
- **`skills/task-management/SKILL.md:112–124`** — no actor named for ledger writes; the same file uses `BlockedBy`/`Blocks` fields its own 7-column table lacks.
- **`skills/gitlab-management/SKILL.md:137`** — the sync back to the ledger names no actor; **`:171–172`** — ledger values `in-progress` and `review` against the lifecycle's `in_progress` and `in_review`.
- **`skills/dependency-graphing/SKILL.md:26`** — reads `Blocks` and `BlockedBy` columns the ledger does not have.
- Also in the same observation list, because they are the same class: **`skills/checkpoint-protocol/SKILL.md:101`** queries `active-tasks.md` for `done` rows, which the INVARIANT at `AGENTS.md:15` forbids (done rows live in `completed-tasks.md`); and **`:59`** "Author: <agent-name or orchestrator>" against `AGENTS.md:28` (the observation says the two are probably jointly satisfiable: confirm or rule).

Rule each under ADR-008: which text wins, which side is amended, and the exact amendment. Where the ADR ranking does not decide (a
conflict inside tier 1, for example the `BlockedBy`/`Blocks` columns if the intent is to extend the ledger schema), escalate to the user
under P5 as a question. The user's earlier decisions are precedent (do not re-litigate): the orchestrator writes the ledger; the ledger has
seven columns; `AGENTS.md` names win over skills and agents.

Also scan, read-only and by reading, the remaining skills, agents and commands for the same two shapes (an agent other than the orchestrator
writing or transitioning the ledger; ledger fields or status values not in `AGENTS.md`) and list further hits as observations, not rulings.

**Decision only.** Write exactly one file. Every edit is held for the user. Do not edit any knowledge file. Report hit counts of every site
that repeats each conflicting clause, projected paths and root-drift paths, golden and test coupling (including any golden case briefs that
quote these clauses), and whether a grant or baseline would be needed. Maturity is not relied on (ADR-008 P4).

## 2. Output

`docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md`, containing:

1. A D5 record per item (verbatim clauses with file and line on the commit your worktree is on, the Step A analysis, the step that fired, the amendment or "held for the user"), and a statement that maturity was not relied on.
2. Hit counts of every site that repeats each conflicting clause.
3. The effects (projected paths, root drift, golden and test coupling, grant or baseline).
4. **One user question** (consolidated, at most 4 options per item), with a recommendation.
5. A handoff package for the implementing task, a list of further observations, and a summary table.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge. Do not edit `.claude/`, `.github/` or the other derived platform folders.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. A D5 record exists for every item above, and no amendment is applied.
3. The user question is answerable in one round and carries a recommendation.
4. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
