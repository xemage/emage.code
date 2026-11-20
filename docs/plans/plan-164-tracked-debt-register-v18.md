# plan-164 — Tracked-debt register v18

**Created:** 2026-11-14
**Based on:** `docs/artifacts/tracked-debt-register-v17.md` (708 ids); `docs/plans/plan-163-batch-i-rsync-and-project-id.md` (§ Facts the user reported since register v17, § Outcome); `docs/artifacts/security-review-t829-batch-i-v1.md`.
**Scopes:** `T830`.

## User decision (2026-11-14, verbatim)

After plan-163 merged, the user said:

> Continue with the next best step

The orchestrator chose register v18, so that the user's A-21 and A-22 reports and plan-163's statuses are in the register before any further work. Nothing else is due before 2027-01-28.

## Facts since v17 (the orchestrator's record)

- **Merges:**
  - MR !687 (register v17): develop `8ff89e0d`.
  - MR !688 (plan-163): squash `996fb2fc`, develop `2decb734`. Verified at `fd46d4d8`: the full suite passed (2753 OK, skipped=25), and pipelines 3068285235 and 3068285300 succeeded.
- **Commit range:** `8ff89e0d..2decb734`.
- **Ledger:** 0 active, 626 completed.

## Task Decomposition

1. **T830** (tech-lead): `docs/artifacts/tracked-debt-register-v18.md`, a delta on v17. It records:
   - **From the user's reports in plan-163 § Facts:** A-21 is closed, and SEC-T756-02 stays LOW. A-22 is done, and SEC-T780-06 is fixed.
   - **From T829:** TD-T774-01, QA-T818-03 and SEC-T829-03 are fixed. SEC-T829-01 and SEC-T829-02 are new LOW items in batch I. The regrade trigger in § 6.2 item 45 is retired. The next release document may drop K-39 and the M-6 workaround.
   - **Counts** that add up from v17, the batch table, and whether any open item is above LOW.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-14.** T830 (tech-lead), commit `35cac314`: `docs/artifacts/tracked-debt-register-v18.md`.

**Status counts:** 711 ids.

| Status | Ids |
|---|---:|
| fixed | 535 |
| accepted | 47 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 118 |

The batches total 119. Nothing open is above LOW.

**Changes:**
- **Fixed:** TD-T774-01 (with QA-T818-01), QA-T818-03, and SEC-T780-06 (on the user's report).
- **New LOW:** SEC-T829-01 and SEC-T829-02, both in batch I.
- **Minted and fixed:** SEC-T829-03, the orchestrator's fix, not re-reviewed.
- **§ 6.2:** items 34 and 45 leave.
- **§ 7:** A-21 is closed and A-22 is done, both on the user's reports.

**The orchestrator's ruling on T830's question:** SEC-T756-02 stays tracked-LOW. A-21 confirms the condition for its grade, but no source fixes the finding itself.

**The orchestrator's own verification:**
- The parser compared the § 5 tables. TD-T774-01, QA-T818-03 and SEC-T780-06 leave; SEC-T829-01 and -02 enter; the sizes add up to 119.
- The status counts add up.
- The gates exit 0.
- The full suite and the pipeline are recorded in the merge request.

**Budget:** T830 used about 45k against 50k (the agent's estimate).
