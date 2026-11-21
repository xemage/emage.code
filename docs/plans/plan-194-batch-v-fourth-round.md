# plan-194 — Batch V, fourth round: the last three ids

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v31.md` (§ 5 batch V, § 6.2 item 52);
- `docs/artifacts/security-review-t888-batch-v-v1.md` (SEC-T888-01, SEC-T888-02(b), SEC-T888-03, with their remediation);
- `docs/artifacts/security-review-t894-batch-v-v1.md` (the sweep of the fold order);
- `docs/plans/plan-190-batch-v-short-round.md` (Outcome).

**Scopes:** `T899`, `T900`.

## User decision (2026-11-21, verbatim)

> V go

## Why

Batch V has three ids left and nothing else in it. This round closes the batch. It is the release gate that must be right before the next tag.

## Task Decomposition

1. **T899** (devops-engineer): `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`. Three ids, in this order (re-check each against the current code first).
   - **SEC-T888-03:** keep the linear `LINK_RE`, and make a missed link fail closed: any `](` whose target the regex does not match is refused, or reported as "cannot check". Tests for `[a](b_(c).md)` and `[a](\nb.md)`. Show that every real `docs/releases/v*.md` still passes, and that the worst-case time stays linear (before and after).
   - **SEC-T888-02(b):** non-letter look-alikes (`∨` U+2228, `∣` U+2223) in a heading must not end the verdict section unseen. Let a non-ASCII character that is not a space or mark stand for any character in `reads_as`, as the review suggested, **but first sweep it**: report how many real headings in `docs/**/*.md` and the release documents it newly flags, and show that no published release document newly fails. If one does, stop and report it as a blocker. Tests for `∨` and `∣`.
   - **SEC-T888-01:** widen the narrow table rule to "a paragraph that may be a table holds a `|` and a `<` anywhere outside a code span or comment, beyond what the table parse shows". Tests for `| [x](y "|<b>") |` in a body row. Do not call GitLab. Same published-document check.
   - Each fix gets a test and a mutation (on a copy, with timeout and `ulimit -v`).
   - If a fix would newly fail a published document, stop and report it. Never edit a published release document or `tests/golden/`.
2. **T900** (security-engineer, read-only): review T899, with a status per id. The orchestrator supplies the diff and the run evidence.

After T900: the orchestrator verifies (the gates, a clean-worktree full suite, the diff read for weakened assertions), then one merge request, merged on a green pipeline. `.gitlab-ci.yml` is not touched.

## Constraints

- No `docker`.
- No runner, host, project-setting or CI-variable change. No image-digest change. No pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Downloads go only into the scratchpad.
- Budgets: T899 80k, T900 40k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's approval (2026-11-21, verbatim)

The approval line above is left for the user. In the question dialog, the user answered:

> Approve (Recommended)

That option read: "All three ids in one task (T899), then the security review (T900)."

## Outcome

**Done on 2026-11-21.**

**T899** (devops-engineer, `f6ca9470` and `2584bb45`): `scripts/verify-release-docs.py` and its tests.
- **SEC-T888-03:** a `](` that no link pattern matches is reported as "cannot check". A linear `IMAGE_LINK_RE` and a read of inline code as `x` keep 47 real files from being refused. Sweep of 2,149 markdown files: 0 "cannot check", 0 new broken link. Worst case at the cap: 641 ms before, 665 ms after.
- **SEC-T888-02(b):** any non-ASCII character that is no space and no mark is a wildcard in `reads_as`. Sweep of 14,675 headings: 0 newly flagged.
- **SEC-T888-01:** a paragraph that may be a table and holds a `|` and a `<` outside code spans and comments is refused. 29 paragraphs are newly flagged, none in a gated document or a `docs/releases/v*.md`. The exclusion is textual (SEC-T900-02).
- Each fix has tests and a mutation.

**T900** (security-engineer): `docs/artifacts/security-review-t900-batch-v-v1.md`, **CONDITIONAL_PASS** at `f6ca9470`. One MEDIUM, SEC-T900-01: `CODE_SPAN_RE` was exponential and `COMMENT_RE` quadratic, on every paragraph. The orchestrator confirmed it by running it (0.49 s at 22 newlines, 18.6 s on 32,000 `<!--`). T899 fixed it in `2584bb45` with linear scans and timing tests at the cap (0.001 to 0.037 s). The orchestrator re-ran the shapes and fuzzed 2,587 paragraphs against markdown-it (0 differences). The old-pattern mutation does not fail an assertion; it hangs until killed (exit 124). No second security review was held, because the condition named the orchestrator's confirmation.

**Batch V ends:** SEC-T888-03 and SEC-T888-02(b) are fixed. SEC-T888-01 is fixed in the form the review asked for, with the residual SEC-T900-02.

**For register v32:**
- **Fixed:** SEC-T888-01, SEC-T888-02, SEC-T888-03; SEC-T900-01 (MEDIUM, minted and fixed in the same MR), -03 and -05.
- **New, tracked LOW:** SEC-T900-02 (textual exclusion), -04 (plain `<` refused in a table), -06 (`strip_code` ignores escapes; reference links and autolinks unchecked).
- **Batch V is empty.** Check where SEC-T900-02, -04 and -06 belong (a new V round).

**The orchestrator's own verification:** the diff was read; the gates and the release-docs tests pass; the full suite is recorded in the merge request.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T899 | 131k | 80k |
| T900 | 103k | 40k |
