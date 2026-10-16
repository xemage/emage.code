# T607 — Rule the three AGENTS.md naming conflicts (P32 O1, O2, O5)

**ID:** T607
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-114-placeholder-flag-and-naming-rulings.md`
- `docs/plans/plan-112-parked-note-cleanup.md` §2
- `docs/artifacts/path-conventions-v3.md` §8 (O1, O2, O5)
- `docs/decisions/ADR-008-knowledge-document-authority.md` (authority ranking) and `ADR-007-command-contract-authority.md`
- The user's decision of 2026-10-09: "C - but do not forget / note the cosmetics".

## 1. What and why

Three parked notes conflict with tier-1 text (`AGENTS.md`):

- **O1.** The `coding-standards` naming table (`:66–83`) puts version suffixes (`-vN`) on plan file names, and conflicts
  with `AGENTS.md:27` (checkpoint naming) and `AGENTS.md:33` (decision naming). The templates' `:61` revision rule
  conflicts with `plan-approve-execute:182`.
- **O2.** `/new-project:43` and `:51` conflict with `AGENTS.md:27` and `:22`.
- **O5.** `/new-feature:25`, "Have the Scrum Master create tasks", conflicts with `AGENTS.md:18` (only orchestrators create tasks).

Rule each under ADR-008: which text wins, which side is amended, and the exact amendment. Where the ADR ranking does not decide
(a conflict inside tier 1), escalate under P5 to the user as a question.

**Decision only.** Write exactly one file. Every edit is held for the user. Do not edit any knowledge file.

## 2. Output

`docs/artifacts/naming-conflicts-ruling-v1.md`, containing:

1. A D5 record per item (verbatim clauses with file:line on the commit your worktree is on, the Step A analysis, the step that
   fired, the amendment or "held for the user"), and a statement that maturity was not relied on.
2. Hit counts of every site that repeats each conflicting clause, so the implementation task knows its scope.
3. The effects: projected paths and root-drift paths, golden and test coupling (tests that assert these clauses), and whether a
   baseline or grant would be needed.
4. **One user question** (at most 4 options per item, consolidated so the user answers in one round), with a recommendation.
5. A note that the `poc-orchestrator:102` indentation (P33 O4) is cosmetic and rides along with the implementation of the decision.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file.
  Never open `tests/golden/held-out/`. Never write a golden case name unless that case has a `tests/golden/open/` directory.
- **Write access:** your artifact, plus this brief's `**Status:**` line (set it to `in_review`).
- You have no shell. Do not commit, push or merge. Do not edit `.claude/`, `.github/` or the other derived platform folders.

## 4. Acceptance criteria

1. Exactly one file is written, with `Based on:`.
2. Three D5 records exist, and no amendment is applied.
3. The user question is answerable in one round and carries a recommendation.
4. No golden case name appears unless it has a `tests/golden/open/` directory.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`).
