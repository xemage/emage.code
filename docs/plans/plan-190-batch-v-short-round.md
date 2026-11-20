# plan-190 — Batch V, short round: the look-alike heading hole and the help text

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v29.md` (§ 5 batch V);
- `docs/artifacts/security-review-t888-batch-v-v1.md` (SEC-T888-02 with the orchestrator's addendum, SEC-T888-04);
- `docs/plans/plan-186-batch-v-third-round.md` (Outcome).

**Scopes:** `T893`, `T894`.

## User decision (2026-11-20, verbatim)

> V go

## Why

SEC-T888-02(a) is a hole in the release gate that the orchestrator confirmed by running it: `## RELEASE VERDİCT` (dotted İ, U+0130) is not caught as a look-alike of `## RELEASE VERDICT`, so it ends the real verdict section early and the rest of the section goes unchecked. SEC-T888-04 is the gate's stale help text in the same file. The orchestrator recommended exactly these two as a short round, and the user chose it. SEC-T888-01, -02(b) and -03 stay in batch V.

## Task Decomposition

1. **T893** (devops-engineer): two ids, in this order. Files: `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py` only.
   - **SEC-T888-02(a):** in `folded`, casefold first, then NFKD, then drop the Mn, Me and Cf characters, then NFKC (T888's remediation), so that `İ` no longer expands to two characters before the length check.
     - Add tests for `## RELEASE VERDİCT`, and also for the other characters that casefold or NFKD expand (`ß`, `ﬁ` ligature, `ǆ`), against `RELEASE VERDICT` and `Gate Verdicts`.
     - Everything the earlier tests catch (Cyrillic, Greek, full-width, Roman numerals, combining marks) must still be caught.
     - `RELEASE VERDICTS`, `RELEASE VERDICT notes` and `Gate Verdict` must still be allowed.
     - The wildcard rule for non-ASCII letters stays as it is. SEC-T888-02(b), the non-letter look-alikes `∨` and `∣`, is **not** in this round.
     - Every published `docs/releases/*.md` and `REQUIRED_FILES` must give the same refusal, errors and links as before, on markdown-it-py 3.0.0 and 4.2.0. The previous tasks' baseline and compare scripts are in `scratchpad/t887/` and may be reused. If one newly fails, stop and report a blocker; never edit a published document.
   - **SEC-T888-04:** update the help text (and the module docstring where it says the same) to the widened narrow rule, the second parse with the GFM table rule ("a text holding a `|` is parsed twice, at most doubling the parse time, not measured"), and the six `release` job facts that apply to the gate. Extend `test_the_help_and_the_docstring_describe_this_check` to assert the new phrases and the absence of the old one-span wording.
   - A test and a mutation for each fix (the mutation on a copy, with `timeout` and `ulimit -v`).
2. **T894** (security-engineer, read-only): review T893, with a status per id. The orchestrator supplies the diff and the run evidence.

After T894: the orchestrator verifies (the gates, a clean-worktree full suite, the diff read for weakened assertions), then one merge request, merged on a green pipeline. `.gitlab-ci.yml` is not touched.

## Constraints

- No `docker`.
- No change to a runner, host, project setting, CI variable or image digest. No pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Downloads go only into the scratchpad.
- Budgets: T893 70k, T894 40k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's approval (2026-11-20, verbatim)

The approval line above is left for the user. In the question dialog, the user answered:

> Approve (Recommended)

That option read: "The two ids in one task (T893), then the security review (T894)."

## Outcome

**Done on 2026-11-20.** MR !718.

**T893** (devops-engineer):
- **SEC-T888-02(a), `4d71af64`:** `folded` casefolds first, then NFKD, drops Mn, Me and Cf, then NFKC. `## RELEASE VERDİCT` is caught as a look-alike.
- **SEC-T888-04, `3c97074a`:** the help text matches the widened narrow rule and the second parse with the GFM table rule.
- **`e570a268`:** fixes for three findings of T894's review (below).
- The published documents give 0 differences on markdown-it-py 3.0.0 and 4.2.0 (T893's run).

**T894** (security-engineer): `docs/artifacts/security-review-t894-batch-v-v1.md`, **CONDITIONAL_PASS** at `3c97074a`.
- **SEC-T894-01 (regression, LOW):** the case-fold reorder let characters such as a mathematical `𝐕` or a letterlike `ℛ` keep their capital, so a heading spelled with them was no longer caught, though `88bf0fcc` caught it. The orchestrator confirmed it by running it. Fixed in `e570a268` by a second casefold after the final NFKC.
- **SEC-T894-02 (LOW):** "at most doubles the parse time" was not backed by the code. Reworded, with its test.
- **SEC-T894-03 (LOW):** a test loop was a no-op for `Gate Verdicts`. Rebuilt per name.
- The condition named the orchestrator's run as the confirmation, so **no second security review was held**. The orchestrator's sweep of every code point against both names is in the artifact addendum: 11,884 shapes the old gate caught but the new one does not, all of them characters whose accent-stripped base is a different ASCII letter than the name's letter (no look-alike, **(unverified)** visually), and 497 shapes the new one catches and the old one missed.

**The orchestrator's own verification:**
- The removed test lines were read: a phrase list that was extended, the reworded parse-cost phrase, and the per-name loop.
- `.gitlab-ci.yml` is unchanged, so no CI lint was needed.
- The full suite and the pipeline are recorded in the merge request.

**For register v30:**
- **Fixed:** SEC-T888-02(a) (SEC-T888-02(b) stays open) and SEC-T888-04.
- **Minted and fixed in this MR:** SEC-T894-01, -02, -03.
- **Still open, tracked-LOW:** SEC-T888-01, SEC-T888-02(b), SEC-T888-03.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T893 | 159k (two rounds) | 70k |
| T894 | 79k | 40k |
