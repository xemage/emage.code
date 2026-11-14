# plan-167 — Batch I: SEC-T832-01 and SEC-T832-02

**Created:** 2026-11-14
**Based on:** `docs/artifacts/security-review-t832-batch-i-followups-v1.md` § 6; `docs/artifacts/tracked-debt-register-v19.md` (batch I).
**Scopes:** `T834`, `T835`.

## User decision (2026-11-14, verbatim)

> Continue with one of the LOW batches

The orchestrator chose batch I's SEC-T832-01 and SEC-T832-02. Both are small, T832 proposed the code for each, and they finish the remote-URL handling of plans 163 and 165. The other ids in batch I stay tracked.

## Goal

1. **SEC-T832-01** (LOW). `_redacted` in `implementation/runtime/memory/context_retriever.py` removes only the userinfo of a remote URL, so its query string and fragment are printed verbatim. `default_index_dir` also prints the slug, which can carry a query. The fix:
   - after the userinfo substitution, cut the URL at the first `?` or `#`;
   - drop the slug from the `default_index_dir` message.
2. **SEC-T832-02** (LOW). `derive_project_id` runs `subprocess.run(..., text=True)`. A remote that is not valid UTF-8 raises an uncaught `UnicodeDecodeError`. The fix: refuse it cleanly, either by passing `errors="replace"` and refusing the result, or by catching `UnicodeDecodeError`. Either way it gives the usual `RemoteResolutionError` on both the server and build paths.

Each fix gets a test that fails without it.

## Task Decomposition

1. **T834** (backend-developer): both fixes, with tests.
2. **T835** (security-engineer, read-only): review T834.
3. **The orchestrator:** the gates, the full suite in a clean worktree, the MR, and the merge, pinned and squashed, on a green pipeline.

## Constraints

- No `docker`.
- Never open `tests/golden/held-out/`.
- Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-14.**

**T834** (backend-developer), commits `a4143f81` and `0487febd`:
- **SEC-T832-01 (fixed):** `_redacted` removes the userinfo, then cuts at the first `?` or `#`, then truncates. When a `?` or `#` comes before the last `@`, it shows only the scheme and `***` (SEC-T835-01). `default_index_dir` no longer shows the slug.
- **SEC-T832-02 (fixed):** `derive_project_id` refuses an undecodable remote with `RemoteResolutionError`, and decodes strictly as UTF-8 (SEC-T835-02). The locale-gated test skips are removed.
- **Tests:** every new test failed without its fix and passes with it.

**T835** (security-engineer):
- `docs/artifacts/security-review-t835-batch-i-v1.md`: **PASS**. It found SEC-T835-01 (an `@` in the query or fragment defeated the query cut) and SEC-T835-02 (decoding depended on the locale). Both were fixed in this batch.
- `docs/artifacts/security-review-t835-batch-i-addendum-v1.md`: **PASS**. SEC-T832-01 is now fully fixed.
- **New:** SEC-T835-03 (`SECURITY:LOW`, message accuracy, no security impact). Strict decoding also applies to git's `stderr`, so the message can blame the remote when git failed. It is tracked under the user's LOW policy and not chased further.

**The orchestrator's own verification:** the gates, the full suite in a clean worktree, and the pipeline. The results are in the merge request. No root drift.

**Budgets:**

| Task | Tokens used (about) | Budget |
|---|---:|---:|
| T834 | 159k (two rounds) | 60k + 30k |
| T835 | 79k plus the addendum | 40k + 25k |
