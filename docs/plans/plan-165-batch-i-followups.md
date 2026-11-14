# plan-165 — Batch I follow-ups: SEC-T829-01 and SEC-T829-02

**Created:** 2026-11-14
**Based on:** `docs/artifacts/security-review-t829-batch-i-v1.md` (§ 3, SEC-T829-01 and SEC-T829-02); `docs/artifacts/tracked-debt-register-v18.md` (batch I).
**Scopes:** `T831`, `T832`.

## User decision (2026-11-14, verbatim)

The orchestrator offered "Batch I follow-ups: SEC-T829-01 (catch the `git` timeout) and SEC-T829-02 (redaction of a raw `/` in credentials)". The user answered:

> Batch I follow-ups go

## Goal

1. **SEC-T829-01** (LOW). `derive_project_id` in `implementation/runtime/memory/context_retriever.py` does not catch `subprocess.TimeoutExpired`. As a result, a hanging `git` call ends the build and the server with a traceback instead of a refusal. Catch it together with the existing errors (T829's proposal: `except (subprocess.SubprocessError, OSError)`). Add a test that uses a stub `git` which sleeps past the timeout.
2. **SEC-T829-02** (LOW). `_redacted` stops at the first `/`, so userinfo that contains a raw `/` can appear in a shape-error message. T829 proposes two fixes, either or both:
   - (a) the build CLI states a fixed reason instead of repeating the URL;
   - (b) `_redacted` over-redacts everything between the scheme and the last `@` before the path.

   The message must never contain userinfo. Add a test for `https://bob:/tok@host`-style remotes on both the build and the server paths.

## Task Decomposition

1. **T831** (backend-developer): both fixes with tests. Brief: `docs/tasks/task-T831.md`.
2. **T832** (security-engineer, read-only): review T831.
3. **The orchestrator:** gates, the full suite in a clean worktree, the MR, and a pinned, squashed merge on a green pipeline.

## Constraints

No `docker`. Never open `tests/golden/held-out/`. Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-14.**

- **T831** (backend-developer), commit `ec336566`:
  - **SEC-T829-01, fixed.** `derive_project_id` catches `SubprocessError` and `OSError`, so a timeout raises `RemoteResolutionError`. The timeout moved to `_GIT_TIMEOUT_S = 10`.
  - **SEC-T829-02, fixed.** `_redacted` now removes everything up to the last `@`.
  - **A second leak path, found by the developer and fixed:** an `@` in `<org>` or `<repo>` is now refused.
  - The tests failed without the fixes and pass with them.
- **T832** (security-engineer): `docs/artifacts/security-review-t832-batch-i-followups-v1.md`, **PASS**.
  - SEC-T829-01 and -02 are closed.
  - The `@` refusal breaks no configuration that worked before.
  - The pattern runs in linear time.
  - Option (a) is not recommended.
  - **New LOW findings:**
    - SEC-T832-01: the query or fragment of a remote URL is printed verbatim. Tracked.
    - SEC-T832-02: an uncaught `UnicodeDecodeError`. Tracked.
    - SEC-T832-03: comment accuracy. **Fixed** by the orchestrator with T832's wording; not re-reviewed (the orchestrator's ruling, comment only).
- **The orchestrator's own verification:** the gates, the full suite in a clean worktree, and the pipeline. The results are in the merge request.
- **Root drift:** none.
- **Budgets:** T831 about 78k against 70k; T832 about 38k against 50k (its estimate).
