# plan-110 — poc-guidelines owner items and the three debt registers (P33)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "continue", where the recommended item was P33;
`docs/plans/plan-092-poc-contract-amendments.md` §4 (P33); `docs/artifacts/poc-skills-alignment-v1.md` F5.
**Scopes:** `T598`.

## 1. Why now

P33 is the last substantive parked item. It concerns `poc-guidelines.md`, a stable tier-1 instruction, so any change
to its own text is a user decision under ADR-008. F5 (the three debt registers) joined P33 at T570.

## 2. Sequence

1. **T598** (solution-architect, P2, decision only): one D5 record each for (a) the PoC root, (b) the Debt Inventory
   severity, (c) the Legacy section and (d) the three debt registers. Every P5 escalation, and every tier-1 or
   command edit, is written as a user question with its candidate edits held verbatim.
2. **Orchestrator verification**, then a Security Engineer review if any edit touches security criteria.
3. **The user decides** every escalation.
4. **Implementation** is a separate task. If it changes a golden quote or fixture, it also needs a protected-path
   grant and a user-authorized v19.

## 3. Not in scope

P44, L4/X5 and the small parked observations stay parked.
