# plan-192 — Batch X, small round: the whole `apk add` pairing and the future publication date

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v30.md` (§ 5 batch X, § 6.2 item 17, § 7);
- `docs/artifacts/security-review-t891-batch-x-v1.md` (SEC-T891-01, SEC-T891-02, SEC-T881-02 and its recommendation);
- `docs/plans/plan-188-batch-x-round.md` (Outcome).

**Scopes:** `T896`, `T897`.

## User decision (2026-11-21, verbatim)

> X go

## Why

The orchestrator had suggested waiting until about 2026-11-26, when Brave 2.2.0 passes the 7-day age rule and a pin bump could exercise the pin-age code. The user chose to start now. No pin can be bumped today, so this round takes the two items of batch X that need no bump: SEC-T891-01 and SEC-T891-02. SEC-T756-02 stays (its remaining action is a rule for later image bumps). SEC-T881-02 waits for the user's choice (see the approval dialog) and, by default, changes nothing.

## Task Decomposition

1. **T896** (devops-engineer): two ids, in this order.
   - **SEC-T891-01:** `ca_job_pairing_problems()` in `tests/functional/test_ci_hash_pins.py` compares the whole ordered `apk add` argument list of `main-develop-drift-gate` and `ca-chain-check-python` (after dropping the `run-allowlisted.py --` wrapper), so the `git~=` constraint and any other package are paired too, not only `openssl`. Mutations: a changed, added, dropped or reordered package in either job is refused.
     - If the two lists are not equal today, stop and report the difference; do not change `.gitlab-ci.yml`.
   - **SEC-T891-02:** in `scripts/audit-mcp-pins.py` `command_age`, a publication time later than `now` is an `AuditError` (exit 2), not "young". Tests offline with the fixed `AGE_NOW`: a time in the future, and a time exactly at `now`. A mutation for each. If the checklist text or its test pins the old behaviour, update both consistently.
   - **Left alone:** SEC-T756-02. SEC-T881-02: no lock and no header change.
2. **T897** (security-engineer, read-only): review T896, with a status per id. The orchestrator supplies the diff and the run evidence.

After T897: the orchestrator verifies (the gates, a clean-worktree full suite, the diff read for weakened assertions), then one merge request, merged on a green pipeline. `.gitlab-ci.yml` and `ci/` are not touched.

## Constraints

- No `docker`.
- No change to a runner, host, project setting, CI variable, image digest, lock or pin. No pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Downloads go only into the scratchpad.
- Budgets: T896 50k, T897 30k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's answers (2026-11-21, verbatim)

The approval line above is left for the user. In the question dialog, the user answered two questions.

> Approve (Recommended)

That option read: "SEC-T891-01 and -02 in one task (T896), then the security review (T897). No pin, lock or CI file changes."

On SEC-T881-02, the CI lock (a fresh rebuild would move six pins), the user answered:

> Keep the lock (Recommended)

That option read: "The security reviewer's advice: no lock change; header lines 3-6 stay the record; the one-cut-off rebuild waits for the next full regeneration with the 14-day review, or an advisory on one of the six pins."

SEC-T881-02 therefore stays a tracked-LOW id with the lock unchanged. The decision is the user's, and register v31 records it as such.

## Outcome

**Done on 2026-11-21.** MR !720.

**T896** (devops-engineer):
- **SEC-T891-01, `44da9174`:** `ca_job_pairing_problems` compares the whole ordered `apk add` argument list of `main-develop-drift-gate` and `ca-chain-check-python` (wrapper dropped, `before_script` and `script`). Both lists are identical today (`apk add --no-cache 'openssl~=3.5' 'git~=2.54'`). Eight mutation cases are added: a changed `git~=` constraint, an added package, a dropped package and a reordered list, once per job.
- **SEC-T891-02, `887b6bcc`:** `command_age` raises `AuditError` (exit 2) for a publication time later than `now`, even when `--allow-young` names the pin. A time exactly at `now` stays age 0, young, as before. The checklist § 1 sentence says so.
- `.gitlab-ci.yml`, `ci/`, the lock and every pin are unchanged.

**T897** (security-engineer): `docs/artifacts/security-review-t897-batch-x-v1.md`, **PASS**. Both ids are fixed. One new LOW:
- **SEC-T897-01:** the pairing check selects only lines whose words start with exactly `apk add`. An extra install written as `apk --no-cache add`, `sh -c '...'`, `env X=1 apk add` or with two spaces, in one job only, is ignored. No current exposure: nothing uses those forms and both lists are equal. The remediation is in the artifact.
- **A wording gap:** the checklist § 1 does not say `--allow-young` cannot override the future-time refusal. The code and the test do. Tracked with SEC-T897-01.

**SEC-T881-02:** the user chose "Keep the lock (Recommended)" (Addendum 1). No lock or header change. It stays a tracked-LOW id, now with the user's decision on record.

**The orchestrator's own verification:**
- The changed test lines were read: the openssl-only comparison became a whole-list comparison, and no assertion was dropped.
- `AuditError` ends in exit 2 (`audit-mcp-pins.py:613-615`), which the reviewer could not confirm.
- `.gitlab-ci.yml` and `ci/` are unchanged, so no CI lint was needed.
- The full suite and the pipeline are recorded in the merge request.

**For register v31:**
- **Fixed:** SEC-T891-01 and SEC-T891-02.
- **New, LOW:** SEC-T897-01 (batch X).
- **Decision on record:** SEC-T881-02, the user's "Keep the lock (Recommended)", stays tracked-LOW. SEC-T756-02 is untouched.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T896 | 73k | 50k |
| T897 | 67k | 30k |
