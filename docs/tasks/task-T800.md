# T800 — ADR-015: a MEDIUM plan without a harness fix, and a passed deadline

**ID:** T800
**Owner:** solution-architect
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-155-v11-release-decisions.md` (task T800, User decisions 3 and 4)
- `docs/decisions/ADR-011-user-accepted-medium-at-release.md`; `docs/decisions/ADR-012-medium-acceptance-record.md`
- `docs/artifacts/tracked-debt-register-v12.md` (rows SEC-T762-04, TL-T761-10, SEC-T735-08; § 4.1; § 6.2 items 2 and 33); `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (Part 1, Q3)

## 1. What and why

Two rules of the accepted-MEDIUM procedure were unruled (SEC-T762-04, TL-T761-10). The user ruled on both on 2026-11-12; the questions as shown, the answers and the option descriptions are quoted verbatim in the plan's § User decisions 3 and 4. Record them as a decision. Accepted ADRs are immutable, so this is a new ADR that supersedes ADR-011 (and ADR-012, where it applies) in part.

## 2. Output

`docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`, written in the worktree `/home/emage/Code/emage/worktrees/agent-solution-architect-T800` (write there, not in the main checkout). Follow `docs/decisions/_template.md` and the form of ADR-011 and ADR-012. No other file changes; the orchestrator commits.

- **Status: Proposed.** Only the user accepts it. Do not write "Accepted", and do not edit ADR-011 or ADR-012.
- Quote the user's two answers verbatim, with the questions and the option descriptions as the plan records them. Claim nothing the user did not say.
- Rule 1: a plan's fix may be "none possible in the harness" only under the three conditions of the option description (it names who could close it outside the harness; it states plainly that no harness fix exists; it sets a review date). State what the plan's `deadline` then is, staying inside what the user was shown; where the user's words leave something open, list it under "Open points for the user" instead of deciding it.
- Rule 2: a new acceptance by the user, with a new plan and a deadline still ahead, cures a passed deadline; the release document must say that the old deadline passed.
- Name exactly which rows or sentences of ADR-011 and ADR-012 this ADR supersedes or extends, by quoting them, and which knowledge sources would need a follow-up edit (for example `implementation/knowledge/agents/release-manager.md`, `security-engineer.md`, any skill that restates the rule). List those edits as consequences; do not make them.
- Say what the ADR does not change: an acceptance still covers one release only, only the user gives it, no agent carries one over.

## 3. Constraints

- You have no shell: do not try to commit, push or run a test. Never create a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never open `tests/golden/held-out/`.
- Mark anything you did not verify **(unverified)**.
- Token budget: 60k, counting context.

## 4. Acceptance criteria

- The header says Proposed and names the user as the only decider.
- Every quoted user sentence matches the plan character for character.
- Every superseded sentence is quoted with its file and line.
- Relative links resolve from `docs/decisions/`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
