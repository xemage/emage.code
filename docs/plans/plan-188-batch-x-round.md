# plan-188 — Batch X: the pin-age check, the CI-image pin, the lock header and a note

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v28.md` (§ 5 batch X);
- `docs/artifacts/security-review-t867-batch-x-text-v1.md` (SEC-T867-01, -02);
- `docs/artifacts/tech-lead-release-v12-v1.md` (TL-T876-04);
- `docs/artifacts/security-review-t881-ci-lock-v1.md` (SEC-T881-02);
- `docs/artifacts/security-review-t885-batch-v-v1.md` (SEC-T885-04);
- `docs/artifacts/tech-lead-release-v10-v1.md` and `docs/artifacts/security-review-t860-batch-x-v1.md` (TL-T761-11);
- `docs/wiki/mcp-pin-bump-checklist.md`.

**Scopes:** `T890`, `T891`.

## User decision (2026-11-20, verbatim)

> X go

## Why

Batch X's items are CI supply-chain and pin hygiene. SEC-T885-04 guards the next tag pipeline: nothing yet keeps the drift gate on the same image as the CA job, and the new certificate lines in the drift gate depend on that. The orchestrator had suggested waiting until about 2026-11-26 (Brave 2.2.0 passes the 7-day rule), so that a pin bump would exercise the pin-age fixes. The user chose to start now; the pin-age fixes are tested with a fixed date instead, and no pin is bumped here.

## Task Decomposition

1. **T890** (devops-engineer): five ids, in this order.
   - **SEC-T885-04:** a structural pin in `tests/functional/test_ci_hash_pins.py` that the `main-develop-drift-gate` job's `image` equals `ca-chain-check-python`'s image, and that both install the same `openssl` constraint in their `apk add` lines. A mutation for each.
   - **SEC-T867-01 with TL-T876-04:** `scripts/audit-mcp-pins.py age`: refuse `--min-age-days` below the 7-day rule (exit 2), or print `floor lowered below 7 days` and count it as a finding. Choose one and say why. Say in checklist § 1 that the default is the rule.
   - **SEC-T867-02 with TL-T876-04's date print:** compute `(now_utc - published) >= timedelta(days=min_age)` from a fixed `now` in tests; refuse a duplicate `--allow-young`; print the publication time in UTC. Tests offline, with a fixed date, and a mutation for each.
   - **SEC-T881-02:** the header of `ci/requirements-ci.txt`.
     - In the scratchpad only, try one `uv pip compile` run with a single cut-off for all packages, so line 2 reproduces the lock alone.
     - If the resulting lock is identical to the committed one (same pins and hashes), write the reproducing command in the header.
     - If it is not identical, **stop, change no lock, and report** the difference. A lock change is a supply-chain change for the user.
   - **TL-T761-11:** the note beside the `FF_GIT_URLS_WITHOUT_TOKENS` open point (where register v28 and the T761 source say), that on a runner with the flag on the `release` fetch has no credential: it works while the project is public and fails closed if not, and `CONTRIBUTING.md`'s rule (do not widen the allowlist) is right.
   - **Left alone:** SEC-T756-02 (its remaining action is "every image bump passes both CA jobs", a rule for later bumps, not work now).
2. **T891** (security-engineer, read-only): review T890, with a status per id. The orchestrator supplies the diff and the run evidence.

After T891: the orchestrator verifies (the gates, the CI lint, a clean-worktree full suite, the diff read for weakened assertions), then one merge request, merged on a green pipeline. No pin is bumped, no image digest changes, and no runner setting changes.

## Constraints

- No `docker`.
- No change to a runner, host, project setting, CI variable or image digest. No pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Downloads and `uv` runs go only into the scratchpad.
- Budgets: T890 100k, T891 50k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's approval (2026-11-20, verbatim)

The approval line above is left for the user. In the question dialog, the user answered:

> Approve (Recommended)

That option read: "Five of the six X items in one task (T890), then the security review (T891). SEC-T756-02 stays."

## Outcome

**Done on 2026-11-20.** MR !716.

**T890** (devops-engineer):
- **SEC-T885-04, `38646d9b`:** `ca_job_pairing_problems()` pins that the drift gate's image equals `ca-chain-check-python`'s and that both `apk add` lines carry the same `openssl` constraint.
- **SEC-T867-01 and -02 with TL-T876-04, `f581e819`:** `--min-age-days` below 7 is refused (exit 2), and the age is an exact UTC time difference. A duplicate `--allow-young` is refused. The publication time prints in UTC. Checklist § 1 says the option may only raise the default.
- **TL-T761-11, `be9659dc`:** the note in `CONTRIBUTING.md` and a comment above the fetch in `scripts/publish-release.py`. No `.gitlab-ci.yml` change.
- **SEC-T881-02: not fixed, by design.** A fresh single-cut-off compile of `ci/requirements-ci.txt` (uv 0.11.9, scratchpad only) differs from the committed lock in **6** pins: certifi, pycparser, pydantic, pydantic-core, sse-starlette and starlette. T890 reported 7; its own pin lists and T891 show 6. No lock or header change. **The decision is the user's.**
- **SEC-T756-02:** left alone, as planned.

**T891** (security-engineer): `docs/artifacts/security-review-t891-batch-x-v1.md`, **PASS**. New LOW:
- **SEC-T891-01:** the pairing check covers only the image and `openssl`, not the whole `apk add` list (`git~=` included).
- **SEC-T891-02:** a publication time in the future counts as young but is not an error.
- **SEC-T891-03:** restates SEC-T881-02 with the count of 6 pins.

T891 recommends keeping the lock and using header lines 3-6 as the record. The one-cut-off regeneration then waits for the next full regeneration, with the 14-day review.

**The orchestrator's own verification:**
- The removed test lines were read: each is replaced by a stricter or equivalent check.
- `.gitlab-ci.yml` and `ci/` are unchanged, so no CI lint was needed.
- The pin count was re-derived with `diff` on the agent's pin lists.
- The full suite and the pipeline are recorded in the merge request.

**For register v29:**
- **Fixed:** SEC-T885-04, SEC-T867-01, SEC-T867-02, TL-T761-11 (TL-T876-04 with the first two).
- **Open, tracked-LOW:** SEC-T881-02 (with SEC-T891-03), SEC-T756-02, and the new SEC-T891-01 and -02.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T890 | 106k | 100k |
| T891 | about 70k | 50k |
