# plan-110 — poc-guidelines owner items and the three debt registers (P33)

**Created:** 2026-10-08
**Based on:** the user's instruction of 2026-10-08, "continue", where the recommended item was P33;
`docs/plans/plan-092-poc-contract-amendments.md` §4 (P33); `docs/artifacts/poc-skills-alignment-v1.md` F5.
**Scopes:** `T598`, `T599`.

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

## 4. Outcome (2026-10-08)

- **The T598 ruling** (`poc-guidelines-owner-items-v1.md` → `-v2.md`):
  - (a) The PoC root is not defined or placed by any document, so it escalated under P5.
  - (b) Step A applies: the `## Summary` cannot be computed from the scorecard's own table. Fixing that requires a
    tier-1 edit, so it went to the user.
  - (c) Step A holds, but the section's own text is ambiguous. Fixing that also requires a tier-1 edit, so it went to
    the user.
  - (d) Step A: the three debt registers can coexist. Note D1 relates them.
  - The orchestrator verified the ruling: the quotes are verbatim (one restored bold), all 17 anchors are unique,
    the six "PoC root" sites are confirmed, and no test is coupled.
- **User decisions** (2026-10-08, verbatim option labels):
  - Q-A: **"PoC's own top dir (Recommended)"**
  - Q-B: **"Add Severity column (Recommended)"**
  - Q-C: **"Required, by narrator (Recommended)"**
- **Security Engineer review: CONDITIONAL_PASS** (`security-review-poc-guidelines-owner-items-v1.md`). Both MEDIUM
  findings were adopted verbatim in v2:
  - SEC-001 (C-1): Rule 5 now keeps a security finding's grade and handling.
  - SEC-002 (O3): a new edit, E-O3, means a blocking finding enters the debt ledger only as `resolved`.
- **v2 check by the orchestrator.** The 8 edits each apply once across 4 files. C-1, E-O3 and I-2 are present
  verbatim, and the counts are confirmed mechanically.
- **Next: T599** (backend-developer, P2) applies v2's 8 edits:
  - 4 in the tier-1 file `poc-guidelines.md`, decided by the user;
  - 1 in `poc-orchestrator`;
  - 2 in `technical-debt-tracking`;
  - 1 in `technical-debt-narrator`.

  No golden quote, fixture or result changes, so no grant or v19 is needed.
- **Parked:** the artifact's observations O1, O2, O4, O5 and O6.

## 5. Completion (2026-10-08)

- **T599 is merged** (MR !523, `develop` `705f280`). All 8 edits were applied verbatim and verified independently.
  SEC-001 and SEC-002 are satisfied, and P33 is closed.
- **Root drift** is 26 declared paths. The next root refresh needs the user's approval.
- **The queue is empty**, and plan-110 is complete.
