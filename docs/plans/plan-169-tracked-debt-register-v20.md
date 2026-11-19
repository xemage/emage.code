# plan-169 — Tracked-debt register v20

**Created:** 2026-11-19
**Based on:** `docs/artifacts/tracked-debt-register-v19.md` (714 ids); `docs/plans/plan-167-batch-i-sec-t832.md` (§ Outcome); `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Outcome, Addenda 1 to 4); the security reviews of T835 (with its addendum), T837, T840, T842 and T844.
**Scopes:** `T845`.

## User decision (2026-11-19, verbatim)

> v20 go

## Facts since v19 (the orchestrator's record)

- **Merges:**
  - MR !691 (plan-166, register v19).
  - MR !692 (plan-167), squash `48b95fac`; develop `2ad398a2`.
  - MR !693 (plan-168), pinned to `f075134a`, squash `7d3d8b5a`; develop `86ef3904`.
- **Verification at `f075134a`:** the full suite passed in a clean worktree (2775 OK, skipped=25). Pipelines 3069161042 and 3069161013 succeeded.
- **Root refresh T838**, approved by the user: 29 paths. Drift is `[]`.
- **Commit range:** `0379dec9..86ef3904`.
- **Ledger:** 0 active, 641 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| Leave tracked-LOW as fixed | SEC-T832-01, SEC-T832-02 (batch I); SEC-T663-02 (batch J) |
| New ids, minted and fixed in the same batch | SEC-T835-01, SEC-T835-02, SEC-T837-03, SEC-T840-01 (MEDIUM), SEC-T840-02, SEC-T842-01 (MEDIUM) |
| New ids, tracked-LOW | SEC-T835-03, SEC-T837-01, SEC-T837-02, SEC-T842-02, SEC-T844-01 |

**Expected totals:**
- 725 ids: 547 fixed, 47 accepted, 10 obsolete, 1 open (K-20), 120 tracked-LOW.
- The batch total is 121.
- Batch J ends with SEC-T663-02.

## Task Decomposition

1. **T845** (tech-lead): write `docs/artifacts/tracked-debt-register-v20.md`, a delta on v19. It must contain:
   - A row for every id that changed status or is new, with its source.
   - Status counts carried over from v19 that add up.
   - The § 5 batch table:
     - Place the five new tracked-LOW ids in batches. The tech-lead proposes the batch letters.
     - Say whether batch J ends.
   - Whether any open item is above LOW.
   - A search of the added lines in the range for ids beyond this list, as in v19 § 1.2.
   - **SEC-T660-01's restated scope on Opencode**, from T844 and plan-168 § Outcome:
     - A direct shell, and with it the token, for the 15 agents that hold `execute`, the built-in agents and the user's own agents.
     - Delegation only for the two orchestrators.
     - For the other 13 agents, `read` only, behind the `external_directory` prompt.

     The acceptance of SEC-T660-01 at the next release must use this scope. Record it as a § 6 item. It does not change any status.
   - The two MEDIUMs, SEC-T840-01 and SEC-T842-01: minted and fixed in plan-168. They were never accepted. **Not verified in a live run** (SEC-T837-01).

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-19.** T845 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v20.md` in commit `ae33131c`. It holds **725 ids**:

| Status | Ids |
|---|---:|
| fixed | 547 |
| accepted | 47 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 120 |

The batches total 121. Nothing open is above LOW.

**Changes from v19:**
- **Fixed:** SEC-T832-01, SEC-T832-02 and SEC-T663-02.
- **Minted and fixed in plans 167 and 168:** SEC-T835-01, SEC-T835-02, SEC-T837-03, SEC-T840-01 (MEDIUM), SEC-T840-02 and SEC-T842-01 (MEDIUM). The two MEDIUMs were never accepted. They are **not verified in a live run** (SEC-T837-01).
- **New tracked-LOW:**
  - SEC-T835-03 (batch I);
  - SEC-T837-01 (batch U);
  - SEC-T837-02, SEC-T842-02 and SEC-T844-01 (new batch AA, "Opencode permission, second round"; the tech-lead's proposal).
- **Batch J ends.**
- **§ 6.2 item 49:** SEC-T660-01's restated scope on Opencode, for the acceptance at the next release.

**The orchestrator's own verification:**
- **The parser** compared the § 5 tables of v19 and v20, widened to two-letter batches:
  - SEC-T832-01 and -02 leave batch I.
  - The five new LOW ids enter.
  - The stated total is 121.
  - Batch J is stated as ending with size 0. The parser only recognises "Ended", so it still lists SEC-T663-02 there.
- **The status tables add up:** 547 + 47 + 10 + 1 + 120 = 725.
- **Opencode agent files:** 13 of 28 carry `bash: deny`, and 26 carry `task: deny`. The two without `task: deny` are `orchestrator.md` and `poc-orchestrator.md`. The root tree is identical.
- **The gates exit 0.**
- **The full suite and the pipeline** are recorded in the merge request.

**Budget:** T845 used about 48k tokens against 50k (the agent's estimate).
