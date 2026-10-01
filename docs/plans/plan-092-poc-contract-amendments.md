# plan-092 — Amend the PoC-track contracts per T563, then realign their golden cases

**Created:** 2026-10-01
**Based on:** `docs/artifacts/poc-contract-resolution-v1.md` (T563), §§6 and 9; `docs/plans/plan-091-wave-3-promotion-and-poc-conflicts.md`;
MR !445 (T562).
**Scopes:** `T564`, `T565`.

## 1. What T563 decided

ADR-007 branch 1 fires in all four conflicts: each PoC command is amended toward a higher-authority text it
contradicts.

- **P11:** the plan is written to `docs/plans/plan-<ID>.md`.
- **P29:** the scorecard is `POC-DEBT-SCORECARD.md` in the PoC root, and `/evaluate-poc`'s scales become
  `S/M/L` and `CRITICAL/MEDIUM/LOW`.
- **P30:** checkpoints are written to `checkpoint-<SEQ>-<phase>.md`.
- **P31:** the outcome is binary; `INCONCLUSIVE` is removed and weak evidence returns `INVALIDATED`.

The orchestrator settled the artifact's unverified claims in §9:
- No test compares golden brief quotes against command bodies.
- The `evaluate-poc` fixture uses `HIGH`, so it must be re-authored.
- ADR-007 is still `proposed` and is used as a procedure, following the T542 precedent.

## 2. Two tasks, in sequence

| Task | Covers | Protected paths? | Owner |
|---|---|---|---|
| `T564` | FU-A (the three command contracts) + FU-C (the agent-side P31 vocabulary in `poc-orchestrator` and `evaluation-agent`, approved in §9.2) | No | Backend Developer |
| `T565` | FU-B: realign the three PoC golden cases to the amended wording | **Yes**: `protected-paths-v1.md` §5, three named `open/` case directories | QA Engineer |

`T565` depends on `T564`, because its briefs must quote the merged wording verbatim. Between the two merges, the
three cases quote superseded text but stay green. Every affected `check()` accepts a superset of the amended
values, and no gate compares the quotes, so dispatch `T565` as soon as `T564` merges.

**`T565` needs a user decision.** Any `expect.py` or fixture edit moves the `tests_golden` digest past v13. Two
evaluator-hash tests go red until the user explicitly authorizes a v14 baseline, as with v9–v13. The orchestrator
cannot grant that.

## 3. Why P2, and how the defects are declared

`check-maturity.py` counts only **P0/P1** active rows against a component's level (§3.5, criteria 3 and 7). A P1
row declaring `command/new-poc` would fail the three commands T562 just promoted. Both tasks are **P2**, the same
priority as T563 and as P29–P31 while they were parked:

- The defects are contract wording on a track that has no corpus in this repository.
- T562 recorded the caveat up front: the greens certify content, not paths.
- The ladder allows open P2 defects at `stable` by design.

The briefs still declare `**Affects:**` with the real components, so the defects are on the record. The user may
re-rank either task P1, which would hold the three commands below `stable` until it closes.

**After `T565`,** `check-maturity.py` and `scripts/scorecard.py` must show the three PoC greens **re-earned** on
the amended contract, not inherited.

## 4. Parked items added (from T563 §9.3)

- **P32:** the production-track plan path. `new-feature.md:14` writes `feature-<slug>.md`, the
  `plan-approve-execute` skill uses `plan-<feature-or-phase>.md`, and real plans are `plan-<ID>-<slug>.md`.
  **Trigger:** the next task touching `/new-feature` or `/plan`.
- **P33:** items for `poc-guidelines.md`'s owner. "PoC root" is undefined, the Debt Inventory has no
  per-item severity column although the summary counts tiers, and the Legacy section is ambiguous about
  `TECHNICAL-DEBT.md`. **Trigger:** the next task touching `poc-guidelines.md`.
- **P34:** formal acceptance of ADR-007 (still `proposed`), and whether an ADR on agent-definition authority
  (FU-D) is wanted. **Trigger:** a user decision; flagged to the user 2026-10-01.

Still parked from earlier plans: **P28** (`/validate-workflow` step 6 against its non-verdict gates). Its trigger,
"after T563", has now fired. It is the next single-command repair after `T565`.
