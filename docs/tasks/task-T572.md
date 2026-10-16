# T572 — Adjudicate the validation-gate verdict formats and gate-definition inconsistencies (P37)

**ID:** T572
**Owner:** Solution Architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-096-gate-definition-consistency.md`; `docs/plans/plan-093-validate-workflow-repair.md` §4 (P37);
`docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md` (ADR-007 Accepted; P36 closed; P34b parked);
`docs/artifacts/validate-workflow-gate-resolution-v1.md` §6 (F1–F3); `docs/decisions/ADR-007-command-contract-authority.md`.

## 1. What and why

The repository has one stated rule for gate verdicts. The `validation-gates` skill (**stable**), § Verdict Format,
says: "Every gate MUST produce a verdict in this format". The format is a `## Gate Verdict: <Gate Name>` block whose
`**Gate:**` field admits only `architecture | implementation | integration | security | release`. Several other
documents define a different verdict format or a different gate vocabulary. T566 found three of these divergences
(F1–F3), and the orchestrator's survey found more.

Decide how they reconcile and write the decision down. **Decision only.** Do not edit any skill, command, agent,
instruction or golden case.

## 2. Facts verified by the orchestrator on `develop` `18681b3`

**Verdict formats in use**

| # | Where | Maturity | Format | Gate name |
|---|---|---|---|---|
| V1 | `skills/validation-gates/SKILL.md:31–60` | **stable** | `## Gate Verdict: <Gate Name>` block, "Every gate MUST produce a verdict in this format" | `**Gate:** architecture \| implementation \| integration \| security \| release` |
| V2 | `skills/code-review/SKILL.md:112–118` | **stable** | one-line `[VERDICT] gate=code-review \| result=… \| reviewer=… \| artifact_ref=… \| date=…`; "Code review is a **validation gate** … Every review MUST conclude with a structured verdict" | `code-review` |
| V3 | `skills/testing-strategy/SKILL.md:214–229` | **stable** | one-line `[VERDICT] gate=qa-validation \| …`; "The QA gate uses the same VERDICT protocol as code review". It names the **integration validation gate** (`:207`) | `qa-validation` |
| V4 | `skills/project-planning/SKILL.md:156–159` | experimental | one-line `[VERDICT] gate=plan-review \| …`: "Approval is a validation gate that produces a verdict" | `plan-review` |
| V5 | `skills/poc-evaluation/SKILL.md:36` | experimental | one-line `[VERDICT] gate=poc-evaluation \| …` (PoC track) | `poc-evaluation` |
| V6 | `agents/tech-lead.md:66–75` | experimental | `## VERDICT: [PASS \| CONDITIONAL_PASS \| FAIL]` block, for code reviews | — |
| V7 | `commands/prepare-release.md:38–45` | experimental | `## RELEASE VERDICT` section in `docs/releases/v<version>.md` | release |

Not gate verdicts, and context only: `/validate-workflow`'s `## WORKFLOW VALIDATION VERDICT` (a report on the
workflow) and `/evaluate-poc`'s `## POC VERDICT` (PoC track; P38 already covers its overlap with V5).

**Divergences found by T566** (`validate-workflow-gate-resolution-v1.md` §6)
- **F1:** the integration gate has two formats, V1 and V3, and the orchestrator routes the integration criteria to
  `testing-strategy`.
- **F2:** the orchestrator's Core Workflow never names an "Implementation Gate". § Validation Gates has
  **IMPLEMENTATION GATE** (`orchestrator.md:205`), but Phase 3 step 3 (`:249`) says "delegate to **@tech-lead** for
  code review".
- **F3:** the Architecture gate's executor is **Tech Lead** in the skill (`validation-gates:25`) and **Tech Lead +
  Security Engineer** in the orchestrator (`orchestrator.md:201–203`).

**Settled decisions to respect, not re-decide**
- **P36 (user, 2026-10-01): plan approval is the user's Approve / Revise / Reject decision, not a VERDICT gate.**
  V4 says the opposite. Treat V4's "Approval is a validation gate" as contradicted by a settled user decision.
- **ADR-007 is Accepted.** It governs **command** contracts. It does not rank a skill against another skill, or an
  agent against a skill. That is the **P34b** gap.

**Coupling**
- No tool parses `[VERDICT]` markers: `scripts/`, `implementation/scripts`, `implementation/runtime` and CI have
  no hits.
- No test outside `tests/golden/` asserts any of these formats.
- In `tests/golden/open/` (with `held-out` pruned), the only golden case that reads a verdict definition is
  `validate-workflow-gate-verdict-sources`. It reads a **frozen copy** of `validation-gates`: the `Verdict Format`
  opening sentence and the `**Gate:**` field. If `validation-gates` changes, that case does not fail, but its
  provenance statement goes stale. Say whether your ruling would require re-fixturing it, which would need a grant
  and a baseline bump.

## 3. What to decide

1. **Authority basis, first and explicitly.**
   - Prefer a **reconciling reading** that needs no ranking. For example: are the one-line markers machine-readable
     summary lines that *accompany* the V1 block, with the gate names mapping onto V1's five kinds? Or are they
     rival formats?
   - Where a reconciling reading holds, quote the text that supports it.
   - **Where a ruling truly requires ranking one skill above another, or an agent against a skill, do not
     invent the rank. Stop and report it as a `dependency` blocker naming P34b.** That question is the user's.
2. **For each of V2–V7 and F1–F3:** decide whether it is consistent, needs a specialisation note, or needs an
   amendment. Give exact before/after wording for every amendment. Include the gate-name mapping, if you adopt one.
3. **V4 vs P36:** specify the amendment that makes `project-planning` consistent with the settled decision.
4. **Golden coupling and blast radius:** list every file a follow-up would edit, and say whether any of them
   touches `tests/golden/**`.
5. **Follow-up task table** (owner, files, grant yes/no).

## 4. Output

`docs/artifacts/gate-verdict-consistency-v1.md`, structured as:
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
- **Read-only.** You may read `tests/golden/open/validate-workflow-gate-verdict-sources/{brief.md,expect.py}` only.
  Do not open any other golden case, and never open `tests/golden/held-out/`.
- **Do NOT run `glab mr merge` or any merge/approve API, and do not commit or push.**

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity `critical` |
`major` | `minor`. A ranking question under P34b is a `dependency` blocker: report it and do not decide it. If a fact
in §2 is wrong, report it.
