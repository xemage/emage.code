# plan-203 — Batch X: the apk check as an exact-line allowlist

**Created:** 2026-11-23
**Based on:**
- `docs/artifacts/tracked-debt-register-v35.md` (§ 5 batch X, § 7 the allowlist question);
- `docs/artifacts/security-review-t911-batch-x-v1.md` (SEC-T912-01 to -04, with the orchestrator's addendum);
- `docs/plans/plan-201-batch-x-sec-t909.md` (Outcome).

**Scopes:** `T914`, `T915`.

## User decision (2026-11-23, verbatim)

> X with apk-allowlist

The user's earlier word of 2026-11-22 on the open question was none; this answer rules on it.

## Why

Each review round closed the forms the last one named and the next review named more, because `apk_adds` in `tests/functional/test_ci_hash_pins.py` is a denylist (SEC-T912-03). An exact-line allowlist ends that cycle and closes SEC-T912-01 to -04 together.

## Task Decomposition

1. **T914** (devops-engineer): replace the denylist logic of `apk_adds` / `ca_job_pairing_problems` in `tests/functional/test_ci_hash_pins.py` with an exact-line allowlist, for the two jobs it covers (`ca-chain-check-python` and the drift gate). Only that test file changes (and the wiki checklist text only if it names the old rules).
   - **Rule:** in the three fields `before_script`, `script` and `after_script` of the two jobs, every line that holds the token `apk`, a `$`, a backtick or `eval` (anywhere in the raw text, also after quote or backslash removal) must equal exactly one pinned permitted line, character for character. The permitted lines are the standard `apk add` line of each job as the file has it now (the drift gate's is `DRIFT_GATE_APK`; read the other from `.gitlab-ci.yml`). Any other such line is refused. Lines that hold none of those are not judged by this check (the other pins judge them).
   - **SEC-T912-01:** a field that is not a list of strings (a plain string, a nested list, a non-string item) is itself a problem for those two jobs; no silent skip.
   - **SEC-T912-02:** no quote stripping hides anything, since the decision is an equality test, not a scan. Show that a stray apostrophe or a redirect after it is refused.
   - **SEC-T912-03:** show that `extends:` or `default:` on either job that could add lines is refused or resolved (decide, say which, and test it), and that variable-program forms at any position are refused.
   - **SEC-T912-04:** the over-refusal is the price of an allowlist; keep it narrow (only lines with `apk`, `$`, a backtick or `eval`) and check the real `.gitlab-ci.yml` has no other such line in those jobs, or list which and pin them as permitted lines if they are legitimate (say so in the report).
   - Keep every existing behaviour the old tests assert that is still right (equal ordered argument lists, same image, the 8 plus 15 mutation cases): port them, never delete an assertion without saying why. Add a test and a mutation for each new refusal (mutations on a copy, with `timeout` and `ulimit -v`).
   - No job, digest, pin or image change.
2. **T915** (security-engineer, read-only): review T914 with a status per id (SEC-T912-01 to -04) and name any form of `apk` use the allowlist still lets through. The orchestrator supplies the diff and the run evidence.

After T915: the orchestrator verifies (gates, clean-worktree full suite, diff read for weakened assertions), opens one merge request and merges it on a green pipeline.

**Out of scope:** the Brave 2.2.0 pin bump (not pinnable before about 2026-11-26) and the young-pin lapse; SEC-T756-02 and SEC-T881-02 stay as decided.

## Constraints

- No `docker`. No runner, host, project-setting or CI-variable change. No image-digest change.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Budgets: T914 80k, T915 50k.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-23)

**T914** (devops-engineer, `77ed3468`): the apk check in `tests/functional/test_ci_hash_pins.py` is an exact-line allowlist for `ca-chain-check-python` (one permitted line) and the drift gate (three). Non-list fields, `extends` and `default:` script fields are refused; 120 tests OK (118 before), 11 implementation weakenings each caught. One test was replaced, deliberately stricter: `'git>=2.54'` is now refused unless it is in the pinned line.
**T915** (security-engineer): `docs/artifacts/security-review-t914-batch-x-v1.md`, PASS; 0 CRITICAL, HIGH or MEDIUM. SEC-T912-01, -02, -04 closed; SEC-T912-03 partly closed. New LOW: SEC-T915-01 (python job's lines not exactly pinned), -02 (its key set not pinned), -03 (apk line not placed), -04 (one mutation weaker than its name) — for register v36, batch X; -01 and -02 are one fix.
**No job, digest or pin changed. No root refresh needed.** Not yet done: the Brave 2.2.0 bump (not pinnable before about 2026-11-26).
