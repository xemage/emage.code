# plan-176 — Tracked-debt register v23

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v22.md` (729 ids);
- `docs/plans/plan-175-batch-aa-opencode-and-td-t849-01.md` (§ Outcome);
- `docs/artifacts/security-review-t856-batch-aa-v1.md`;
- `docs/artifacts/mcp-agent-denials-evidence-v3.md`.

**Scopes:** `T858`.

## User decision (2026-11-19, verbatim)

> v23 go

## Facts since v22 (the orchestrator's record)

- **Merges:**
  - MR !699 (plan-174, register v22; develop `70a279cf`).
  - MR !700 (plan-175), pinned to `1f0fac5c`; develop `5193e938`.
- **Verification at `1f0fac5c`:** the full suite passed in a clean worktree (2790 OK, skipped=25). Pipelines 3088730937 and 3088730647 succeeded.
- **Root refresh T857:** approved by the user ("Refresh now (Recommended)"). Drift is `[]`.
- **Commit range:** `70a279cf..5193e938`.
- **Ledger:** 0 active, 654 completed.

## The orchestrator's expected delta (for the tech-lead to check, not to copy)

| Change | Ids |
|---|---|
| tracked-LOW → fixed | SEC-T837-02, SEC-T842-02, SEC-T844-01 (batch AA, which ends); TD-T849-01 (batch I) |
| New, tracked-LOW | SEC-T856-01, SEC-T856-02, SEC-T856-03 |

**Expected totals:**
- 732 ids: 555 fixed, 46 accepted, 10 obsolete, 1 open (K-20), 120 tracked-LOW.
- The batch total is 121.

## Task Decomposition

1. **T858** (tech-lead): `docs/artifacts/tracked-debt-register-v23.md`, a delta on v22. It must contain:
   - **A row for each changed or new id**, with its source, and the status counts carried over from v22 that add up.
   - **The § 5 batch table:**
     - Batch AA ends.
     - Propose batches for SEC-T856-01 to -03.
   - **Whether any open item is above LOW.**
   - **The § 1.2 search** of the added lines in the range.
   - **§ 6.2 item 49:** restate it from T856 § 4.
     - The orchestrators can no longer launch built-in agents. They can still reach the token through the shell-holding subagents on their lists.
     - The 13 agents without `execute` have `read` denied for any `gitlab-mcp` directory. `grep` and `glob` are guarded only by `external_directory`. A non-default token path, or a symlink, is not covered.
     - The scope is narrower, not closed.
   - **Carry the dates unchanged:** 2027-01-28, 2027-01-29 and 2027-03-12.

## Constraints

- Only the register file changes.
- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-19.** T858 (tech-lead) wrote `docs/artifacts/tracked-debt-register-v23.md` in commit `bc8c0b45`. It holds **732 ids**:

| Status | Ids |
|---|---:|
| fixed | 555 |
| accepted | 46 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 120 |

The batches total 121. Nothing open is above LOW.

**Changes from v22:**
- **Fixed:** SEC-T837-02, SEC-T842-02, SEC-T844-01 and TD-T849-01.
- **Batches:**
  - AA ends.
  - I goes from 25 to 24.
  - **AB (new)**, "Opencode permission, third round", holds SEC-T856-01, -02 and -03 (the tech-lead's proposal). Its owner is devops-engineer. Its trigger is the next change to the Opencode permission generator or its docs, or the next evidence run.
- **§ 6.2 item 49** is restated from T856 § 4: narrower, not closed. The dates are unchanged.

**The orchestrator's own verification:**
- **The parser** compared the § 5 tables of v22 and v23: SEC-T837-02, SEC-T842-02 and SEC-T844-01 leave.
  - The parser does not read the bold `**AB** (new)` row or the struck-out AA row. I read the table by hand: AB holds SEC-T856-01 to -03, and the stated sum is 121.
- **The status tables add up:** 555 + 46 + 10 + 1 + 120 = 732.
- **The gates exit 0.**
- **The full suite and the pipeline** are recorded in the merge request.

**Budget:** T858 used about 38k tokens against 40k (the agent's estimate).
