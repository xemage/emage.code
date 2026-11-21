# plan-199 — Batch X: SEC-T897-01 (the apk-pairing check)

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v33.md` (§ 5 batch X, § 6.3);
- `docs/artifacts/security-review-t897-batch-x-v1.md` (the SEC-T897-01 row and its code sketch);
- `docs/artifacts/security-review-t881-ci-lock-v1.md` (SEC-T881-02) and `docs/artifacts/security-review-t768-ca-control-v1.md` (SEC-T756-02).

**Scopes:** `T908`, `T909`.

## User decision (2026-11-21, verbatim)

> X go

## What batch X holds today

- **SEC-T897-01 (LOW):** fixable now. This plan.
- **SEC-T881-02 (LOW):** decided by the user ("Keep the lock (Recommended)", 2026-11-21). Its fix is the next full regeneration of the lock; nothing to do here.
- **SEC-T756-02 (LOW):** the runner and CI-variable side (A-21) is the user's; it stays tracked, untouched.
- Not in this plan: the young-pin lapse (about 2026-11-24/25) and the Brave 2.2.0 pin bump (about 2026-11-26), which are not due yet.

## Task Decomposition

1. **T908** (devops-engineer): fix SEC-T897-01 in `tests/functional/test_ci_hash_pins.py` (`ca_job_pairing_problems` and `apk_adds`, about lines 1477-1480 and the docstring). Today the selector keeps only lines whose words start with exactly `apk add`; an extra install written as `apk --no-cache add x`, `apk  add x`, `env X=1 apk add x`, `sh -c 'apk add x'`, `command apk add x` or after `;` or `&&` in one job only is ignored. Fail closed: any line, after the wrapper is dropped (`unwrapped()`), whose words or `sh -c` payload (re-split with shlex) contain the token `apk` and that is not exactly an `apk add ...` line is a problem. Keep every existing assertion and case. Add one mutation case each for `apk --no-cache add x` and `sh -c 'apk add x'` in one job, and show each fails the test on the old code and passes on the new. Show that today's real `.gitlab-ci.yml` (both jobs hold `apk add --no-cache 'openssl~=3.5' 'git~=2.54'`) still passes. Also add the wording gap from the register to the checklist, `docs/wiki/mcp-pin-bump-checklist.md`: `--allow-young` cannot override the refusal of a future time. Run `tests/functional/test_ci_hash_pins.py` and `tests/functional/test_pin_bump_checklist.py`. Change no job, no image digest and no pin.
2. **T909** (security-engineer, read-only): review T908, with a status per id. The orchestrator supplies the diffs and the run evidence.

After T909: the orchestrator verifies (gates, clean-worktree full suite, diff read for weakened assertions), opens one merge request and merges it on a green pipeline.

## Constraints

- No `docker`. No runner, host, project-setting or CI-variable change. No image-digest change, no pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files. Never open `tests/golden/held-out/`; never edit `tests/golden/`, a published release document, an immutable `-vN` artifact or a derived platform folder.
- Mutation runs on a copy, with `timeout` and `ulimit -v`.
- Do not write a link-like text with a parenthesis in the target in prose.
- Budgets: T908 50k, T909 40k.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-21)

- T908 done (commit 069c8f14): SEC-T897-01 fixed; the checklist wording gap closed.
- T909 security review PASS (`docs/artifacts/security-review-t908-batch-x-v1.md`): two new LOW ids, SEC-T909-01 (quote-split or variable forms of `apk`, `after_script` not scanned) and SEC-T909-02 (`<` and `>` refuse a legitimate constraint such as `git>=2.54`), tracked as debt for register v34, batch X.
- SEC-T881-02 (the user chose "Keep the lock") and SEC-T756-02 (the user's runner and variable side, A-21) are unchanged. The young-pin lapse and the Brave 2.2.0 bump are not due before about 2026-11-24 to 26 and are not part of this plan.
- No job, image digest or pin changed; no root refresh needed (a test file and a wiki page only).
