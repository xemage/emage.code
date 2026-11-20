# plan-183 — Tracked-debt register v26

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v25.md` (740 ids);
- `docs/plans/plan-182-next-release.md` (Addenda 1 to 4, Outcome);
- `docs/checkpoints/checkpoint-044-release-v12.0.0.md`;
- `docs/releases/v12.0.0.md`;
- the plan-182 gate artifacts: T869, T870, T871, T875, T876, T877, T878 (the independent check) and T881.

**Scopes:** `T882`.

## User decision (2026-11-20, verbatim)

> v26 go

## Facts since v25 (the orchestrator's record)

- **Merges:**
  - MR !706 (plan-181, register v25; develop `9b9a31f0`).
  - MR !707 (plan-182 wave 1; develop `6afb6143`).
  - MR !708 (release into develop; `fb116f1f`).
  - MR !709 (release into main; `ba17bda6`).
  - MR !710 (the closeout; develop `43b6d3f2`).
- **v12.0.0 published 2026-11-20:**
  - the tag on `514503b0`;
  - tag pipeline 3092574856, with all three jobs on runner #59129270;
  - the Release body equals the document;
  - drift `releases_behind=0`.
- **Release verdict:** CONDITIONAL_PASS, issued at `e0e3b355`, independent check PASS.
- **SEC-T660-01 and SEC-T665-01:** accepted by the user for v12.0.0 only ("Accept for v12.0.0 (Recommended)", after T871). The v11.0.0 acceptance ended with the release. Review on 2027-01-28.
- **SEC-T811-05** (the runner hardening user action): the user applied the steps.
  - `gitlab-runner` 19.5.3;
  - `services_limit = 0`;
  - `lint`: "Configuration file is valid.";
  - no log line on services, unknown, deprecated or invalid.

  Recorded in checklist § 5. The tag pipeline ran on the hardened runner.
- **Commit range:** `9b9a31f0..43b6d3f2`.
- **Ledger:** 0 active, 678 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T811-05 (the user applied the runner steps; § 5 record) |
| New, minted and fixed | TL-T869-01 (T880), SEC-T881-01 (T880), QA-T875-01 and SEC-T877-01 (`e0e3b355`), QA-T875-02 (`e0e3b355`), TL-T876-01 (`e0e3b355`), TL-T876-05 (`e0e3b355`) |
| New, tracked-LOW | SEC-T881-02, TL-T876-02 |
| New, decide the status | TL-T869-02 (info: the stale SEC-T762-04 premise; no defect); TL-T876-03 (dismissed by the orchestrator, withdrawn by the tech-lead); TL-T876-04 (the same defect as SEC-T867-01, already tracked: a duplicate) |
| Accepted, renewed | SEC-T660-01 and SEC-T665-01: the acceptance for v11.0.0 ended; new acceptance for v12.0.0 only |

The tech-lead derives the totals and the § 5 batch table from v25 and this delta, and reports any difference.

## Task Decomposition

1. **T882** (tech-lead): write `docs/artifacts/tracked-debt-register-v26.md`, a delta on v25. It must contain:
   - **A row for each changed or new id**, with its source and status. Follow the precedent of earlier registers for info-only, dismissed and duplicate ids.
   - **Counts against v25 that add up**, and the § 5 batch table:
     - SEC-T811-05 leaves batch X;
     - place the new LOW ids in batches.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range.
   - **§ 6:**
     - § 6.1: the v12.0.0 acceptance of SEC-T660-01 and SEC-T665-01, with their Conditions lines in `docs/releases/v12.0.0.md` (K-16).
     - § 6.2: the next-release checklist after v12.0.0. Carry the items that remain, item 43 (an acceptance ends at each release) and item 49 (the Opencode scope).
     - § 6.3, the dates:
       - 2027-01-28;
       - 2027-01-29;
       - 2027-03-20;
       - the young-pin exceptions lapsing about 2026-11-24/25;
       - Brave 2.2.0 (published 2026-11-19), not pinned.
   - **§ 7, user actions:** SEC-T811-05 is done; K-20 stays; `/tmp/evidence-run` removal is optional.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-20.** T882 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v26.md` in commit `c68b6333`. It holds **750 ids**:

| Status | Ids |
|---|---:|
| fixed | 575 |
| accepted | 46 |
| obsolete | 12 |
| open (K-20) | 1 |
| tracked-LOW | 116 |

The batches total 117. Nothing open is above LOW.

**Changes from v25:**
- **Fixed:**
  - SEC-T811-05. The container-escape patching rule moves into § 6.2 item 44.
  - Six new ids: TL-T869-01, SEC-T881-01, QA-T875-01 (with SEC-T877-01, counted once), QA-T875-02, TL-T876-01 and TL-T876-05.
- **Obsolete:** TL-T869-02 (info) and TL-T876-03 (dismissed and withdrawn), following v12's and v17's precedent.
- **Duplicate, counted once:** TL-T876-04, counted with SEC-T867-01. Its date-print half joins SEC-T867-02's remainder.
- **New, tracked-LOW:** SEC-T881-02 (batch X) and TL-T876-02 (batch AB).
- **Accepted, renewed:** SEC-T660-01 and SEC-T665-01 are accepted for v12.0.0 only.
- **§ 6.2 is reset for the release after v12.0.0.** New items: 50 (pin age, Brave 2.2.0) and 51 (K-43, the Node floor residual).

**The orchestrator's rulings:**
- TL-T869-01 is fixed, as the tech-lead ruled. T869's route allowed the PREREQUISITES note as the fix. The residual is K-43 and item 51.
- The checklist § 5 runner row still says the tag pipeline on the hardened runner was "not yet observed". Checkpoint-044 records that it ran (pipeline 3092574856), so this is a gap in the record. It can be closed with the next checklist edit.

**The orchestrator's own verification:**
- The X, AB and Q rows read by hand; the stated total is 117.
- The status tables add up: 575 + 46 + 12 + 1 + 116 = 750.
- The gates exit 0.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T882 used about 48k tokens against 50k (the agent's estimate).
