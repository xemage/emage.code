# plan-205 — Batch X: exact pins for the python CA job (SEC-T915-01 to -04)

**Created:** 2026-11-28
**Based on:**
- `docs/artifacts/tracked-debt-register-v36.md` (§ 5 batch X);
- `docs/artifacts/security-review-t914-batch-x-v1.md` (SEC-T915-01 to -04, with the orchestrator's addendum);
- `docs/plans/plan-203-batch-x-apk-allowlist.md` (Outcome).

**Scopes:** `T917`, `T918`.

## User decision (2026-11-28, verbatim)

> X go

The user's answer was to the recommendation of batch X, which offered to add the Brave 2.2.0 bump. This plan does not include it: the bump is a pin change with its own audit and age rules and is not named in the user's words. It waits for a separate word.

## Why

The apk check (plan-203) judges only lines that hold `apk`, `$`, a backtick or `eval`. The python CA job (`ca-chain-check-python`) is the reference that the drift gate's CA lines are paired with, but no pin fixes its lines or keys (SEC-T915-01, -02). Its one permitted apk line may also move or repeat (SEC-T915-03). The drift gate's own pin is exact, so the mutation case for it has to test a verbatim move and a repeat (SEC-T915-04).

## Task Decomposition

1. **T917** (devops-engineer): add an exact pin for `ca-chain-check-python` in `tests/functional/test_ci_hash_pins.py`, as a separate constant set (not in `PINNED_JOBS`: that loop also sets the tag-job rules, and the python job has no tag):
   - **Key set:** exactly `stage`, `image`, `needs`, `before_script`, `script`, `rules`. A job-level `hooks`, `run`, `variables` or `after_script` is refused (SEC-T915-02).
   - **`before_script` and `script`:** compared exactly, in order, with the lines the file has now. The apk line is one of them, so its position is fixed: after the store copy and the `--ca-release` check, before the live-store checks (SEC-T915-01, -03).
   - **Image:** the existing `PINNED_IMAGE` check stays.
   - **Mutations** (on a copy, with `timeout` and `ulimit -v`): a `hooks` key on the python job; a moved apk line in `after_script`-equivalent positions (before the copy, and after the last check); a repeated apk line; a changed script line; an added `after_script`. Each must be refused.
   - **SEC-T915-04:** for `main-develop-drift-gate`, add two mutation cases with a verbatim move of `DRIFT_GATE_REMOVE` into `after_script` and a verbatim duplicate of `DRIFT_GATE_APK`, each asserting the refusal comes from the exact pin (`pinned_job_problems`), and fix the existing "moved to after_script" case so it moves the line verbatim.
   - No job, digest, pin or image change. `.gitlab-ci.yml` is not edited, so if a test fails on the real file, stop and report: the real file is the truth.
2. **T918** (security-engineer, read-only): review T917 with a status per id (SEC-T915-01 to -04). The orchestrator supplies the diff and the run evidence.

After T918: the orchestrator verifies (gates, clean-worktree full suite, diff read for weakened assertions), opens one merge request and merges it on a green pipeline.

## Constraints

- No `docker`. No runner, host, project-setting or CI-variable change. No image-digest change.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Budgets: T917 80k, T918 50k.

## Approval

- [ ] Approved by the user

## Outcome (2026-11-28)

**T917** (devops-engineer, `0e966bbd`): exact pins for `ca-chain-check-python` in `tests/functional/test_ci_hash_pins.py` (key set, ordered `before_script` and `script`, plus `stage`, `needs` and `rules`, which the agent added so no tag pipeline can start the job); verbatim drift-gate mutations in a new class; the trailing-space row removed. 134 tests OK. Co-Authored-By trailer is the Haiku line (the agent's session).
**T918** (security-engineer): PASS; 0 CRITICAL, HIGH or MEDIUM. SEC-T915-01 to -04 closed. New LOW: SEC-T918-01 (script contents not pinned), -02 (fixture checksum file self-referential), -03 (python image only shape-checked), -04 (duplicate YAML keys), -05 (dead-code check, `in_after_script` is still used so it is not dead).
**Not verified here:** the suite and pipeline (run at the closeout head).
