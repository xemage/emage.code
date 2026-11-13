# T804 — ADR-016: the Security Engineer's confirmation as a fourth validity condition

**ID:** T804
**Owner:** solution-architect
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-157-confirmation-as-validity-condition.md` (§ User decision, § Scope choice)
- `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`
- `docs/artifacts/security-review-t802-adr-015-apply-v1.md` (SEC-T802-01 to -04)

## 1. What and why

The user decided SEC-T802-03 on 2026-11-12; the words are quoted verbatim in the plan's § User decision. Under ADR-015 Rule 1 the Security Engineer's confirmation (O4) is required but stands outside the "only when" conditions, and no text says the acceptance fails without it. The user ruled that it becomes a fourth validity condition. ADR-015 is accepted and immutable, so this is a new ADR that supersedes it in part.

## 2. Output

`docs/decisions/ADR-016-<slug>.md`, written in the worktree `/home/emage/Code/emage/worktrees/agent-solution-architect-T804` (write there, not in the main checkout). Follow `docs/decisions/_template.md` and the form of ADR-015. No other file changes; the orchestrator commits.

- **Status: Proposed.** Only the user accepts it. Do not write "Accepted", and do not edit ADR-015 or any other ADR.
- Quote the user's answer and the orchestrator's two sentences verbatim, as the plan records them. Claim nothing the user did not say.
- Decision: a plan whose fix is "none possible in the harness" is valid only when all four hold: the three conditions of ADR-015 Rule 1, and the Security Engineer's review of the finding confirms that no harness fix exists. State the consequence in so many words: a plan that lacks any one of the four is not a valid plan, and the acceptance does not hold. Keep ADR-015's "the question to the user cites it"; say whether that citing is part of the fourth condition or a separate duty, staying inside the user's words; if the words leave it open, list it under "Open points for the user" with a recommendation instead of deciding it.
- Name exactly which sentences of ADR-015 this ADR supersedes, by quoting them with file and line (§ Decision, O4, row C1; row C2 if its text must change; say explicitly if C2 needs no change and why).
- A "Files and lines" table like ADR-015's, with the exact replacement text for `implementation/knowledge/skills/validation-gates/SKILL.md:70`. Read the live line first; the replacement must be a minimal change of the current C1 text.
- In a separate table headed "Wording only, not part of the decision", give exact text for SEC-T802-01 (what the outcome recorded on the review date covers; a fix that now exists is a changed fix), SEC-T802-02 ("It covers only the release" to "An acceptance covers only the release") and SEC-T802-04 (the gate-input line near `validation-gates/SKILL.md:120` gains the plan's deadline). Read each live line and quote it. Say that ADR-015 allows wording changes that keep the rule, that the user may strike any of the three, and that the orchestrator proposed including them (plan § Scope choice).
- Say what the ADR does not change: an acceptance still covers one release only, only the user gives it, no agent grants, extends, infers or carries one over; never for critical, high, an Immutable Security Constraint breach, or an omitted or weakened control.
- List the follow-ups as consequences without making them: the source edits, the test pins in `tests/functional/test_release_self_review_text.py`, a header note on ADR-015 ("Superseded in part by ADR-016"), root drift.

## 3. Constraints

- You have no shell: do not try to commit, push or run a test. Never create a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md`, any brief's Status line, any plan, or any knowledge source.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never open `tests/golden/held-out/`.
- Mark anything you did not verify **(unverified)**.
- Token budget: 80k, counting context.

## 4. Acceptance criteria

- The header says Proposed and names the user as the only decider.
- Every quoted user sentence matches the plan character for character.
- Every superseded sentence is quoted with its file and line.
- Relative links resolve from `docs/decisions/`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
