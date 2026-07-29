# Task T270 — W6-02 Audit the remaining ID gaps T037 / T227 / T229 (D6) — **STOP FIRST**

**ID:** T270
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Depends on:** T269
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 6 / W6-02

## ⛔ STOP FIRST — mandatory user confirmation
This task is **investigation first, editing second**. Present findings to the user and
**wait** before editing any file.

## STOP-RULES (read before touching anything)
- Phase 1 (investigate) modifies **NO files**.
- Phase 2 (remediate) may only run after explicit user approval, and then follows the
  T268 + T269 pattern — **one file per commit**.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T270 resolve ledger id gaps <ids>`

## Phase 1 — investigate (no writes)
Run:
```bash
for id in T037 T227 T229; do
  echo "== $id"
  grep -l "$id" docs/tasks/*.md 2>/dev/null
done
```

Then, for each of `T037`, `T227`, `T229`, classify it into exactly one bucket:

| Bucket | Condition | Action |
|--------|-----------|--------|
| **A — never used** | no brief file `docs/tasks/task-<ID>.md` AND no row in either ledger | no action |
| **B — orphan brief** | brief file exists BUT no row in either ledger | apply the T268 + T269 pattern |
| **C — orphan row** | row exists in a ledger BUT no brief file | create the brief from `implementation/docs/tasks/_template.md` |
| **D — already consistent** | brief + exactly one ledger row | no action |

## Phase 2 — report and wait
Present a table to the user:

| ID | Brief exists? | In active? | In completed? | Bucket | Proposed action |
|----|---------------|-----------|---------------|--------|-----------------|

Then ask:
> "Confirm the proposed action for each ID above before I edit anything."

**WAIT for the answer.** Do not edit on silence.

## Phase 3 — remediate (only after approval)
Apply only the approved actions, one file per commit.

## Expected outputs
- The classification table, recorded in `## Execution notes`.
- Zero or more one-file commits, each approved by the user.

## Acceptance criteria
1. All three IDs are classified into exactly one bucket each.
2. The user's approval (or "no action") is recorded verbatim.
3. After remediation, the ledger validator reports no `FAIL C6` or `FAIL C7` line
   mentioning `T037`, `T227`, or `T229`.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Phase 1 investigation completed:
- T037: Brief exists (`docs/tasks/task-T037.md`), missing from both ledgers (Bucket B — orphan brief). Remediated by archiving into `completed-tasks.md` with Done on 2026-05-23.
- T227: No brief, no ledger row (Bucket A — never used). No action needed.
- T229: No brief, no ledger row (Bucket A — never used). No action needed.

User approved proposed actions via prompt.

