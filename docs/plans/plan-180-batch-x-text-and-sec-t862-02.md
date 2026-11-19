# plan-180 — Batch X text items (SEC-T860-01, SEC-T860-02) and SEC-T862-02

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v24.md` (§ 5 batches X and AB; § 7 user actions);
- `docs/artifacts/security-review-t860-batch-x-v1.md` (SEC-T860-01, SEC-T860-02);
- `docs/artifacts/security-review-t862-batch-ab-v1.md` (SEC-T862-02);
- `docs/wiki/mcp-pin-bump-checklist.md`.

**Scopes:** `T866`, `T867`.

## User decision (2026-11-19, verbatim)

> X + SEC-T862-02 go

## Why

The user's pending runner hardening (SEC-T811-05) relies on written steps that are not yet complete (SEC-T860-02). Writing them first lets the user apply the steps once.

## Task Decomposition

1. **T866** (devops-engineer):
   - **(a) SEC-T860-01:** a minimum release age for `npx` pin bumps in checklist § 1, for example 7 days after publication.
     - A younger pin needs a recorded exception in the merge request that names its provenance, its audit result and its diff review.
     - If it is cheap and safe, add an `age` check to `scripts/audit-mcp-pins.py` that reports pins younger than the rule. Test it with a fixed date, offline, and with a mutation.
     - Record the 2.4.0 `server-filesystem` pin (published 2026-11-18, pinned 2026-11-19) as the first exception, with T860's reasons.
   - **(b) SEC-T860-02:** checklist § 3, runner hardening.
     - Add a step to verify that `services_limit` takes effect: after the restart, check the runner log for an unknown-key or deprecation warning, and record `gitlab-runner --version` in § 5.
     - Add an out-of-cycle trigger: patch at once for a critical runc, Docker Engine or kernel container-escape advisory. The 120-day image review is the ceiling, not the cadence.
   - **(c) SEC-T862-02:** the redaction test, `T861EvidenceRedactionTests`.
     - Also scan the evidence `.md` of every directory after v3.
     - Add the `/var/folders/`, `/private/var/` and `C:\\Users\\` (backslash form) prefixes.
     - State in the wiki rule that the local clean-suite run is the user-name check of record, because CI runs as another user.
     - Mutations for each.
2. **T867** (security-engineer, read-only): review T866, with a status per id.

## Constraints

- No `docker`.
- No runner, host or project-setting change. The user applies the runner steps.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`.
- Downloads go only into the scratchpad.

## Outcome

**Done on 2026-11-19.**

**T866** (devops-engineer):
- **(a) SEC-T860-01, `611c55b6`.**
  - Checklist § 1 gains a 7-day minimum release age. A younger pin needs an exception recorded in the merge request, naming its provenance, its audit and its diff review.
  - `scripts/audit-mcp-pins.py age`:
    - runs `npm view … time` through the hardened `run_npm`;
    - takes `--min-age-days` and `--allow-young PKG@VER:REASON` (a reason is required; an exception for a version that is not pinned is an error);
    - fails closed on any doubt.
  - **Recorded exceptions:**
    - `server-filesystem@2.4.0` (T860's reasons);
    - `@brave/brave-search-mcp-server@2.1.5`, which T866 found was also 2 days old when pinned. T867 confirmed it.
- **(b) SEC-T860-02, `84e14c21`.** The runner hardening steps in checklist § 3:
  - **Recording and checking:** record `gitlab-runner --version`, then run `gitlab-runner lint --config /etc/gitlab-runner/config.toml` where it exists, because the TOML decoder ignores unknown keys silently. Without `lint`, check the docs at the exact version tag.
  - **Restart and log:** restart, then read the log with `journalctl -u gitlab-runner`. Stop and report on any problem, and record the result in § 5.
  - **Out-of-cycle trigger:** patch at once for a critical runc, containerd, Docker Engine, GitLab Runner or kernel escape advisory, and push no release tag until patched.
- **(c) SEC-T862-02, `6f445234`.** The redaction test now also scans each evidence `.md` after v3, and adds the `/var/folders/`, `/private/var/` and Windows `X:\Users\` prefixes. In the `.md` only, a prefix counts when a path-segment character follows it. The wiki names the local clean-suite run as the user-name check of record.

**T867** (security-engineer): `docs/artifacts/security-review-t867-batch-x-text-v1.md`, **PASS**.
- **SEC-T860-01, SEC-T860-02 and SEC-T862-02: fixed.** For SEC-T860-02, the user still applies the steps; SEC-T811-05 stays a user action.
- **The brave exception:** confirmed.
- **New, LOW, tracked:**
  - **SEC-T867-01:** `--min-age-days 0` turns the check off with no recorded reason.
  - **SEC-T867-02:** the age is counted in whole UTC days, and a duplicate `--allow-young` silently replaces the first.
  - **SEC-T867-03:** the `.md` redaction rule could miss a name split from its prefix on a prose line. Better: exclude only the exact Redaction line.

**The orchestrator's own verification:**
- **The `age` check, run live:**
  - without exceptions: exit 1, with the two young pins flagged;
  - with both exceptions: exit 0;
  - with `left-pad@1.3.0`: exit 2.
- **The test diffs** were read for weakened assertions, because T867 could not read them. Nothing was dropped:
  - the raw-file scan keeps the strict form;
  - the two lines removed from `test_pin_bump_checklist.py` are tuples, each replaced by a longer one.
- **The gates** exit 0, and the drift is `[]`.
- **The main checkout** holds only the user's edits.
- **The full suite and the pipeline** are recorded in the merge request.

**For register v25:**
- **Fixed:** SEC-T860-01, SEC-T860-02 (text) and SEC-T862-02.
- **New, LOW:** SEC-T867-01, -02 and -03.
- **SEC-T811-05:** the user's runner steps are now complete in checklist § 3.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T866 | 60k | 70k |
| T867 | 30k | 35k |
