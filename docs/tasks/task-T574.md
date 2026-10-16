# T574 — Adjudicate the PoC skill/command overlaps (P38)

**ID:** T574
**Owner:** Solution Architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-02
**Based on:** `docs/plans/plan-097-poc-skill-command-overlaps.md`; `docs/artifacts/poc-skills-alignment-v1.md` §7 (F1–F8) and
§10.3 (P38); `docs/artifacts/gate-verdict-consistency-v1.md` (the reconciling method used for P37);
`docs/decisions/ADR-007-command-contract-authority.md` (Accepted); `docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md`
(P34b).

## 1. What and why

T570 aligned the three PoC skills with T563's rulings. It left seven overlaps between those skills and the PoC
commands, or `AGENTS.md`, unruled, and they were parked as P38. Decide each one and write the decisions down.
**Decision only.** Do not edit any skill, command, agent, instruction or golden case.

## 2. Facts verified by the orchestrator on `develop` `a0b0659`

Line numbers have moved since T570's §7 because T571 edited these files. The current lines are:

| # | Overlap | Sites (current) |
|---|---|---|
| **F1** | **Two verdict shapes for one PoC evaluation.** The skill emits the one-line `[VERDICT] gate=poc-evaluation \| result=VALIDATED\|INVALIDATED \| evidence_strength=… \| …`. The command produces a `## POC VERDICT` block of eight fields. | `skills/poc-evaluation/SKILL.md:36`; `commands/evaluate-poc.md:25–38` |
| **F2** | **Two "Production Handoff Checklist"s for the same trigger** (`proceed` / `proceed_with_constraints`), with different items. The skill has 13 items in four groups. The command has 8 items. | `poc-evaluation:110–136`; `evaluate-poc:40–51` |
| **F3** | "All POC-DEBT tags cataloged and **promoted** to technical debt backlog", against `technical-debt-tracking`'s `monitor_only` disposition ("Do not create a task", as amended by T571). | `poc-evaluation:118` |
| **F4** | "Refactoring backlog items **created as tasks** in docs/tasks/active-tasks.md" and "Debt remediation tasks created with **severity and target sprint**". `AGENTS.md` § Task Protocol says only orchestrators create tasks, and its ledger row has no severity or sprint field. T571's E13 made `technical-debt-tracking` write *proposals* that the orchestrator turns into tasks. | `poc-evaluation:129–130` |
| **F6** | `rapid-prototyping`'s `[CHECKPOINT] id=poc-{name}-validation \| …` marker, which a prototyping agent "publish[es]". `AGENTS.md` § Checkpoint Protocol says checkpoints are "Written at every phase boundary by the orchestrator" and "Include: completed tasks, key decisions, blockers, token metrics, next steps". | `skills/rapid-prototyping/SKILL.md:98–103` |
| **F7** | None of the three PoC skills has a `## Rails` section. `maturity-promotion-criteria-v2.md` §2.1 (criterion b, "all categories") requires one **for promotion**. All three skills are `experimental`. | the three skills; `maturity-promotion-criteria-v2.md:66,106` |
| **F8** | `rapid-prototyping:54` uses the code-review severity label ("🟡 Should Fix") for untagged shortcuts. | `rapid-prototyping:54` |

**Maturity:** `/evaluate-poc` is **stable** (T562). `poc-evaluation` and `rapid-prototyping` are **experimental**.

**Golden coupling.** `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/expect.py` hard-codes the command's
VERDICT `FIELDS` (`:22`) and its handoff `CHECKLIST` (`:33`). **Any ruling that amends `/evaluate-poc`'s VERDICT block
or its checklist changes that case.** That needs a protected-path grant and a v16 evaluator-hash baseline, which only
the user can authorize. Amending only the experimental skills involves no golden case.

## 3. What to decide

- **Authority, first and explicitly.** ADR-007 is Accepted and governs **command** contracts. It does not rank a skill
  against a command (the P34b gap).
  - Prefer a **reconciling reading**, as `gate-verdict-consistency-v1.md` did. For example: does the skill's marker
    *accompany* the command's block? Are the two checklists *complementary*?
  - Where a ruling truly needs one skill or agent ranked against a command or another skill, **do not invent the
    rank. Stop on that item and report it as a `dependency` blocker naming P34b.**
- **For each of F1–F4 and F6–F8:** say whether it is consistent, needs a specialisation note, or needs an amendment.
  Give exact before/after wording for every amendment.
- **Prefer edits to the experimental skills over edits to the stable command, where the reading allows it.** If you
  rule that the command must change, say so plainly and give the golden coupling. The orchestrator will then raise
  the v16 question with the user. Do not soften a ruling to avoid golden coupling.
- **F7:** say whether `## Rails` sections should be authored now, or only when a promotion is attempted. If now,
  specify them.
- **Blast radius and follow-up table:** list the files each follow-up would edit, and whether each needs a grant.

## 4. Output

`docs/artifacts/poc-skill-command-overlaps-v1.md`, with these sections:
- authority basis;
- one section per item;
- blast radius;
- follow-ups;
- corrections to this brief;
- unverified claims;
- findings outside scope.

## 5. Constraints

- **You have no Bash.** Mark unverified claims as unverified.
- **Write exactly one file:** the artifact. Hand it back uncommitted. Do not edit this brief.
- **Read-only.** You may read `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{brief.md,expect.py}` only.
  Do not open any other golden case, and never open `tests/golden/held-out/`.
- **Do NOT run `glab mr merge` or any merge/approve API, and do not commit or push.**

## 6. Blocker protocol

Types are `technical`, `dependency`, `unclear_requirements` and `external`. Severities are `critical`, `major` and
`minor`. A ranking question under P34b is a `dependency` blocker: report it and do not decide it. If a fact in §2 is
wrong, report it.
