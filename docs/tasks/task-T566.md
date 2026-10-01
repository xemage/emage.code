# T566 — Adjudicate `/validate-workflow`'s gate list against its VERDICT requirement (P28)

**ID:** T566
**Owner:** Solution Architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-093-validate-workflow-repair.md`; `docs/plans/plan-090-golden-wave-3.md` §2 (P28);
`docs/plans/plan-084-round-close-and-fired-triggers.md` §4 (P9); `docs/decisions/ADR-007-command-contract-authority.md`;
`docs/artifacts/poc-contract-resolution-v1.md` (the most recent application of ADR-007, including how it handled
ADR-007's `proposed` status in §9.1).

## 1. What and why

`/validate-workflow` cannot return `PASS` against this repository. Step 6 requires every gate step 5 lists to
"produce a VERDICT". Its Failure mode makes any gate that does not produce one force the overall VERDICT to `FAIL`.
Two of the six gates step 5 lists produce no VERDICT. Step 5's own closing sentence concedes that they "are workflow
steps, not among the `validation-gates` skill's five gate types". The golden case
`validate-workflow-gate-verdict-sources` (`known_failing` / `tracked_defect`) proves this mechanically. It is the only
thing blocking `/validate-workflow`'s promotion.

Decide the repair under ADR-007 and write it down. **Decision only.** Do not edit any command, skill, agent or golden
case. Implementation is a follow-up whose size your artifact determines.

## 2. Facts verified by the orchestrator on `develop` `42617db`

| Fact | Where |
|---|---|
| Step 5 lists six gates: Plan approval (`plan-approve-execute` § Phase 2: Approve), Architecture briefing (`orchestrator` § Core Workflow › Phase 3, step 1), and the `validation-gates` skill's **Integration**, **Implementation**, **Security** and **Release** rows. | `validate-workflow.md:24–32` |
| Step 6: "For each gate, verify: … Gate produces a VERDICT …". Failure mode: a gate that "doesn't produce a VERDICT" makes the overall VERDICT `FAIL`. | `validate-workflow.md:33–37,76` |
| The `validation-gates` skill (**`stable`**) defines **five** gate types, **Architecture**, Implementation, Integration, Security and Release, and says "Every gate MUST produce a verdict in this format". **Step 5 omits the skill's Architecture gate type.** | `skills/validation-gates/SKILL.md` § Gate Types, § Verdict Format |
| The `orchestrator` agent (`experimental`) § Validation Gates invokes an **ARCHITECTURE GATE** ("after architecture phase"), which delegates to `@tech-lead` and `@security-engineer`, each told to "Produce VERDICT". This is distinct from the Phase 3 step 1 "Architecture Briefing", which declares no output. | `agents/orchestrator.md` § Validation Gates; § Core Workflow › Phase 3 |
| Plan approval (`plan-approve-execute`, **`experimental`**) offers the user **Approve / Revise / Reject**, which is a user decision rather than a VERDICT. | `skills/plan-approve-execute/SKILL.md` § Phase 2: Approve |
| The golden case's `expect.py` **hard-codes step 5's six-gate list** (`GATES`). Its fixture holds byte-identical copies of the three cited files, and they are still identical on `42617db`. | `tests/golden/open/validate-workflow-gate-verdict-sources/` |

## 3. What to decide

Apply ADR-007's ordered branches and **name the branch that fires**. Do not assume which document outranks which:
quote the text. ADR-007 ranks `AGENTS.md`, a `stable` *instruction*, and another clause of the same command file. It
does not rank a stable *skill*, and `poc-contract-resolution-v1.md` §1.4 notes that it does not rank agent
definitions either. Say how that affects the ruling.

The case brief names three candidate exits. Evaluate each, plus any better one you find:

1. Scope step 6's VERDICT requirement to the gates that are gates, and keep the two workflow steps with lighter checks
   (for example reachability only).
2. Replace the architecture briefing with a VERDICT-producing architecture gate. That could be the skill's
   **Architecture** row, the orchestrator's **ARCHITECTURE GATE**, or both, since the skill defines the type and the
   orchestrator invokes it. Then decide what happens to plan approval.
3. Give the two workflow steps verdicts. This edits a skill and an agent that other surfaces use, so weigh the blast
   radius against ADR-007's warning about rival conventions.

For the chosen exit, state:
- **(a)** the exact command clauses to change, with before and after wording;
- **(b)** whether step 6's other three verifications and the Failure mode need consequential edits;
- **(c)** the **golden coupling**:
  - how `GATES` and the brief must change;
  - whether the fixture needs new or re-copied files;
  - whether the case's status flips to `expected_pass`;
  - how ADR-007 §5 and Validation 1 apply, since a realigned check must be no weaker. In particular, removing gates
    from the checked list must be justified as a corrected contract, not a relaxed one;
- **(d)** the follow-up tasks, including whether each needs a protected-path grant.

## 4. Output

`docs/artifacts/validate-workflow-gate-resolution-v1.md`, structured as:
- the authority ordering, quoted;
- each exit, with the branch that fires and the reasons for and against;
- the decision;
- items (a) to (d) above;
- findings outside scope.

## 5. Constraints

- **You have no Bash.** Say where a claim would need one, and mark unverified claims as such.
- **Write exactly one file:** the artifact. Hand it back uncommitted. Do not edit this brief.
- **Read-only grant extension for this task:** you may read `brief.md`, `expect.py`, `case.yaml` and `fixture/**` of
  `tests/golden/open/validate-workflow-gate-verdict-sources/` **only**. Do not open `tests/golden/held-out/`, and do
  not read any other golden case.
- Read-only on everything else.
- **Do NOT run `glab mr merge` or any merge or approve API, and do not commit or push.** Hand everything back.

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If anything in this
brief is wrong, including the facts in §2, report it rather than working around it.
