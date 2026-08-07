# Task T329 — GATE: role-mapping fidelity check

**ID:** T329
**Owner:** solution-architect
**Status:** done
**Completed:** 2026-08-06
**Priority:** P1
**Depends on:** T327
**Created:** 2026-08-06
**Based on:** `docs/plans/plan-018-cwso-agent-knowledge-awareness.md`; `docs/artifacts/role-mapping-cwso-v1.md`

## Objective

Read-only review. Confirm that the CWSO-to-agent role-mapping table embedded in
`implementation/knowledge/skills/cwso-awareness/SKILL.md` (produced by T327) is faithful to the already-approved
`docs/artifacts/role-mapping-cwso-v1.md` — not a reinvented or drifted mapping. This is a validation gate per
`AGENTS.md` § Validation Gates; you MUST NOT modify any file during this review.

## Inputs

- `implementation/knowledge/skills/cwso-awareness/SKILL.md` (T327 output)
- `implementation/knowledge/agents/orchestrator.md`, `backend-developer.md`, `devops-engineer.md` (T327 output)
- `docs/artifacts/role-mapping-cwso-v1.md` (source of truth, task T211, already approved — do not alter)

## Constraints

- Read-only. No file writes, no edits, no annotations committed to the reviewed files.
- Produce a VERDICT: `PASS` | `CONDITIONAL_PASS` | `FAIL`.

## Expected outputs

A verdict report (returned to the orchestrator, not written to a new file) covering:
1. Does the embedded tier table match `role-mapping-cwso-v1.md` for `orchestrator`, `backend-developer`,
   `devops-engineer` (tier assignment + rationale substance, not necessarily identical prose)?
2. Does the skill correctly represent the worker/orchestrator CWSO-server role split (distinct from, but
   consistent with, the emage.code-agent tier concept) as described in `implementation/runtime/cwso/README.md`?
3. Any factual drift, invented tiers, or unsupported claims?
4. VERDICT with justification.

## Acceptance criteria

- `PASS`: table is verbatim-equivalent to the source artifact for the three agents; no invented facts.
- `CONDITIONAL_PASS`: minor wording drift only, no factual/tier errors; note conditions for the orchestrator
  to track.
- `FAIL`: tier assignment or rationale contradicts `role-mapping-cwso-v1.md`, or the worker/orchestrator
  server-role split is misrepresented. Blocks T328 until fixed.

## Blocker protocol

Report blockers as: type + severity + proposed mitigation. Max 2 retries before escalating to the orchestrator.

## Execution notes

Read-only review of `implementation/knowledge/skills/cwso-awareness/SKILL.md` and the three edited agent
files against `docs/artifacts/role-mapping-cwso-v1.md` and `implementation/runtime/cwso/README.md`. All 15
rows of the embedded tier table matched the source artifact byte-for-byte (tier + rationale); the
worker/orchestrator server-role-split table matched the runtime README; the three agent-file tier statements
matched their artifact rows; no invented tiers, no conflation of the "emage.code agent role" concept with the
"CWSO client role" concept. No file writes performed.

**VERDICT: PASS**

Outcome: PASS.
