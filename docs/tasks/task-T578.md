# T578 — Adjudicate the PoC security reviewer's non-blocking rule for critical findings (O1, SECURITY:HIGH)

**ID:** T578
**Owner:** Solution Architect
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Affects:** agent/poc-security-engineer
**Depends on:** —
**Created:** 2026-10-02
**Based on:**
- `docs/plans/plan-099-poc-security-reviewer-blocking.md`
- `docs/artifacts/security-review-poc-security-shortcuts-v1.md` § O1 (Security Engineer rating: SECURITY:HIGH, plus a fix direction)
- `docs/artifacts/poc-security-shortcut-examples-v2.md` §9 and §13.2
- `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)

**Priority note:** the user decided on 2026-10-02 that this runs at **P1**. This row declares `agent/poc-security-engineer`.
While it stays open, `check-maturity` counts the agent as having an open P1 defect, so the agent is held at `beta`
in the same MR that scoped this task. It returns to `stable` only after the fix lands and passes its gates.

## 1. What and why

The **stable** `poc-security-engineer` agent tells PoC security reviews **not to block**, including on critical
findings. A committed secret or an obvious injection or authorization gap is "recorded for debt handoff" instead.
This contradicts:
- `security-guidelines` Immutable Constraint 1: "No secrets in source control … not negotiable regardless of PoC
  status".
- The Security Review Workflow: "CRITICAL and HIGH findings block merge".

A secret recorded as "debt" stays in git history and is never rotated. The Security Engineer rated this
**SECURITY:HIGH** and asked for a dedicated task.

Decide the repair and write it down. **Decision only.** Do not edit any agent, skill, command, instruction or golden
case. A follow-up implements it, and a Security Engineer reviews the ruling first.

## 2. Facts verified by the orchestrator on `develop` `81921f7`

| Site | Maturity | Text |
|---|---|---|
| `agents/poc-security-engineer.md:3` (description) | stable | "…flags critical risks **without blocking** rapid validation." |
| `agents/poc-security-engineer.md:18–20` (§ Behavior) | stable | "- Do not block progress by default" / "- Record findings for debt handoff" |
| `agents/poc-security-engineer.md:35` (§ Blocker Reporting) | stable | "Suggest a workaround — PoC speed matters, prefer unblocking over perfection" |
| `agents/poc-security-engineer.md:46` (Rails, Out of scope) | stable | "Blocking PoC progress on non-critical findings; performing a full OWASP-style audit." |
| `agents/poc-security-engineer.md:47` (Rails, Failure mode) | stable | "If a critical risk (exposed secret, obvious injection/auth gap) is found, **records it explicitly for debt handoff** rather than silently omitting it" |
| `agents/poc-orchestrator.md:53` | stable | "9. **Security Scan** — `@poc-security-engineer`: critical risks only" |
| `agents/poc-orchestrator.md:66` | stable | "4. **Speed directive**: 'Optimize for demo speed, not production quality'" |
| `agents/poc-orchestrator.md:114` | stable | "**DO NOT** block on non-critical security findings — record for debt handoff". Nothing anywhere says that a *critical* finding blocks. |
| `skills/rapid-prototyping/SKILL.md:61` ("Enforcement") | experimental | As amended by T575 (E9): "The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review …" scale. The reviewer says an untagged *removal of a security control* should block outright. Batch it here, and note that T577 is editing other parts of this file in parallel. |
| `instructions/security-guidelines.md:151–160` and § Security Review Workflow | stable | Immutable Constraints 1–6. "CRITICAL and HIGH findings block merge"; "MEDIUM findings must have a remediation plan before merge". |

**Authority.** The precedence is stated in the documents themselves:
- `security-guidelines`' Rails forbid disabling a security control "even in PoC or development mode".
- `poc-guidelines` (stable), Rails: "Does not waive the Immutable Security Constraints".
- `poc-orchestrator` subordinates itself to `poc-guidelines` (`:73–76`, "every delegation this agent issues is
  governed by that instruction").

Agents are not ranked by ADR-007. That is the P34b gap. The repair should still rest on these quoted texts and on
the precedent for agent files (T542/FU-C). **If any part truly needs a ranking, report it as a `dependency` blocker
naming P34b rather than inventing one.**

**Mechanical constraint.** `tests/functional/test_agent_escalation_consistency.py` requires every PoC-track agent,
`poc-security-engineer` included, to keep the literal sentence **"The PoC orchestrator will handle escalation"** in
its Blocker Reporting section. Your amendment must preserve it.

## 3. What to decide

Rule on each site, giving exact before/after wording in four-backtick fences, one fence per edit, each starting with
`Before:`. The Security Engineer's fix direction is the starting point:
1. Keep "do not block by default" for **non-critical** findings only.
2. Add an explicit carve-out: any breach of an Immutable Security Constraint, or any SECURITY:CRITICAL or HIGH
   finding, **blocks** the PoC and escalates to `@poc-orchestrator`. It is never handed off as debt.
3. For an exposed secret, require **revocation or rotation and removal from history**, not only deletion from the
   code. Say who does what. Note that rewriting git history is a destructive operation, and `security-guidelines` §
   Agent Safety Guards requires explicit user approval for it.
4. Make `poc-orchestrator` consistent:
   - critical findings block;
   - the speed directive gets a security exception;
   - consider whether the secrets scan should run earlier than step 9, because by then a secret is already committed.
5. Decide whether MEDIUM findings need the "remediation plan" that the Security Review Workflow requires.
6. Cover the `rapid-prototyping` "🟡 Should Fix" enforcement item.

Also specify the follow-up tasks and the review step, and state the verification each follow-up must pass.

## 4. Output

`docs/artifacts/poc-security-reviewer-blocking-v1.md`, with these sections:
- authority basis;
- one section per site;
- the secret-exposure procedure;
- blast radius and golden coupling;
- follow-ups;
- corrections to this brief;
- unverified claims;
- findings outside scope.

## 5. Constraints

- **You have no Bash.** Mark unverified claims as such.
- **Write exactly one file:** the artifact. Hand it back uncommitted. Do not edit this brief.
- **Read-only.** Do not open `tests/golden/` at all.
- **Do NOT run `glab mr merge` or any merge or approve API, and do not commit or push.**

## 6. Blocker protocol

Types: `technical` | `dependency` | `unclear_requirements` | `external`. Severities: `critical` | `major` | `minor`.
A ranking question under P34b is a `dependency` blocker. If a fact in §2 is wrong, report it.
