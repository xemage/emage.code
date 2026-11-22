# plan-201 — Batch X: SEC-T909-01 and SEC-T909-02 (the apk-pairing check, second round)

**Created:** 2026-11-22
**Based on:**
- `docs/artifacts/tracked-debt-register-v34.md` (§ 5 batch X, § 6.3);
- `docs/artifacts/security-review-t908-batch-x-v1.md` (the SEC-T909-01 and SEC-T909-02 rows and their remediation text);
- `docs/plans/plan-199-batch-x-sec-t897-01.md` (Outcome).

**Scopes:** `T911`, `T912`.

## User decision (2026-11-22, verbatim)

> X go

(The user said this after the orchestrator recommended batch X as one round: the two new ids now, the Brave 2.2.0 pin bump on or after about 2026-11-26.)

## What this plan holds

- **SEC-T909-01 (LOW):** in `ca_job_pairing_problems` / `apk_adds` the raw-text gate `\bapk\b` runs before shlex, so a quote- or escape-split token (`ap""k add x`, `a\pk add x`) is skipped, a command held in a variable (`$PM add x`) is not seen, and `after_script` is not scanned.
- **SEC-T909-02 (LOW):** the refused character set includes `<` and `>`, so a legitimate constraint such as `'git>=2.54'` is refused as a stray with a message that does not say why.
- Not in this plan: SEC-T881-02 (the user chose "Keep the lock"), SEC-T756-02 (the user's A-21), and the Brave 2.2.0 pin bump (not due before about 2026-11-26).

## Task Decomposition

1. **T911** (devops-engineer): `tests/functional/test_ci_hash_pins.py`, `ca_job_pairing_problems` and its tests. Keep every existing assertion and case.
   - **SEC-T909-01:** fail closed on a quote- or escape-split program name and on any line that runs a command through a variable. For the two jobs, refuse (as a stray) any line in `before_script`, `script` or `after_script` that is not exactly a plain `apk add` line and that either (a) contains a quote, backslash or `$` outside the standard add line's arguments, or (b) after shlex has a word that equals `apk` or ends with `/apk` or contains `apk`. Scan `after_script` too (or add a case that the two jobs have none and the check refuses one if added). Add one mutation case each for `ap""k add x`, `a\pk add x`, a variable form (`PM=apk; $PM add x` or `$PM add x`), and an `after_script` install; show on a copy (with `timeout` and `ulimit -v`) that each fails on the code at the start of this task and passes on the new.
   - **SEC-T909-02:** drop `<` and `>` from the refused set (they are inert inside a quoted word) but keep refusing them unquoted; or say in the message and the docstring which characters are refused and why. Add a case that `'git>=2.54'` in both jobs is accepted, and a case that an unquoted redirect (`apk add x > /tmp/y`) is still refused.
   - The two real jobs must still pass. Run `tests/functional/test_ci_hash_pins.py` and `tests/functional/test_pin_bump_checklist.py`. If the checklist names the pairing check, keep it true.
   - Change no job, no image digest, no pin.
2. **T912** (security-engineer, read-only): review T911, with a status per id. The orchestrator supplies the diff and the run evidence.

After T912: the orchestrator verifies (gates, clean-worktree full suite, diff read for weakened assertions), opens one merge request and merges it on a green pipeline.

## Constraints

- No `docker`. No runner, host, project-setting or CI-variable change. No image-digest change, no pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files. Never open `tests/golden/held-out/`; never edit `tests/golden/`, a published release document, an immutable `-vN` artifact or a derived platform folder.
- Mutation runs on a copy, with `timeout` and `ulimit -v`.
- Do not write a link-like text with a parenthesis in the target in prose.
- Budgets: T911 50k, T912 40k.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-22)

- T911 done (commit 6591811d): SEC-T909-02 fixed; SEC-T909-01 partly fixed (the named forms are closed).
- T912 security review PASS (`docs/artifacts/security-review-t911-batch-x-v1.md`): four new LOW ids for register v35, batch X: SEC-T912-01 (`script` as a string or a nested list is not scanned), SEC-T912-02 (the quote stripping hides a redirect after a stray apostrophe), SEC-T912-03 (the variable-program test is a command-position denylist; `extends:` and `default:` not resolved), SEC-T912-04 (over-refusal of any line that contains `apk` or starts with a variable). SEC-T909-01's residue is -01 and -03.
- The engineer's claim that `apk  add` is now refused was wrong (the reviewer read the code); no behaviour change.
- Not in this plan and unchanged: SEC-T881-02 (the user chose "Keep the lock"), SEC-T756-02 (the user's A-21), the Brave 2.2.0 pin bump (not due before about 2026-11-26).
- No job, image digest or pin changed; no root refresh needed.
