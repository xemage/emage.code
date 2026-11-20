# plan-186 — Batch V, third round: the release job and the gate script

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v27.md` (§ 5 batch V);
- `docs/artifacts/security-review-t885-batch-v-v1.md` (SEC-T885-01, -02, -03; the ruling on SEC-T751-08);
- `docs/plans/plan-184-batch-v-release-gate.md` (Outcome).

**Scopes:** `T887`, `T888`.

## User decision (2026-11-20, verbatim)

> V go

## Why

Batch V's four remaining items are all in the files plan-184 just changed and reviewed. SEC-T885-03 is in the one tag job that holds the job token. The orchestrator recommended V with SEC-T885-03 first, and the user chose it.

## Task Decomposition

1. **T887** (devops-engineer): four ids, in this order.
   - **SEC-T885-03:** `python3 -I scripts/publish-release.py …` in the `release` job.
     - First, an AST check that `publish-release.py` imports no sibling module.
     - Update `RELEASE_COMMAND` in `tests/functional/test_ci_hash_pins.py`, and extend `python_child_problems` to the `release` job, with a mutation.
     - Grep every test (`--exclude-dir=held-out`) for the old literal and update each one. In plan-184, one test was missed.
   - **SEC-T751-08 (residual):** run the existing HTML refusal a second time, on a token stream parsed with the GFM `table` rule enabled. Refuse any non-comment `html_inline` or `html_block` that this parse yields.
     - The bypass `` | `a|` `<b>` | `` must be refused.
     - `v8.0.0.md:104` and every other published `docs/releases/*.md` must give the same result as before, on markdown-it-py 3.0.0 and 4.2.0.
     - If a published document newly fails, stop and report it as a blocker. Never edit a published document.
     - Whether to keep or drop the narrow rule from plan-184: say which, and why.
   - **SEC-T885-01:** change the `LINK_RE` tail so that each attempt stops at the next `(` (for example `\(([^()\s]+)\)`, or `[^()\n]+`).
     - Show that the real documents and `REQUIRED_FILES` give the same links.
     - Add a timing test for the repeated `[a](` shape, with times before and after at the cap.
   - **SEC-T885-02:** look-alike headings in other scripts.
     - In `folded`, apply NFKC, and catch confusable letters: a non-ASCII letter matches any letter at its position, or use a skeleton mapping.
     - Add tests for Cyrillic and Greek forms of `RELEASE VERDICT` and `Gate Verdicts`.
     - No published document may newly fail.
   - A test and a mutation for each fix (the mutation on a copy, with `timeout` and `ulimit -v`).
2. **T888** (security-engineer, read-only): review T887, with a status per id. The orchestrator supplies the diff and the run evidence.

After T888: the orchestrator verifies (the gates, the CI lint, a clean-worktree full suite, and the diff read for weakened assertions). Then one merge request, merged on a green pipeline. The `release` job's new line is proven at run time only by the next `v*` tag pipeline, recorded with checklist item 52.

## Constraints

- No `docker`.
- No change to a runner, host, project setting, CI variable or image digest.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Downloads go only into the scratchpad.
- Budgets: T887 120k, T888 60k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's approval (2026-11-20, verbatim)

The approval line above is left for the user. In the question dialog, the user answered:

> Approve (Recommended)

That option read: "All 4 items in one task (T887), then the security review (T888)."

## Outcome

**Done on 2026-11-20.** MR !714.

**T887** (devops-engineer):
- **SEC-T885-03, `56f82e41`:** the `release` job runs `python3 -I scripts/publish-release.py`. `python_child_problems` now covers the `release` job, and `publish-release.py` is in the AST no-sibling-import test.
- **`88bf0fcc`:**
  - **SEC-T751-08 (residual):** a second parse with the GFM table rule, only for a text holding `|`. The narrow rule is kept and widened to "a code span with `|` and a code span with `<` in one paragraph that may be a table".
  - **SEC-T885-01:** `LINK_RE` tail `[^()\n]+`. At the cap, 17.35 s before and 0.003 s after.
  - **SEC-T885-02:** NFKC, combining marks dropped, and the `reads_as` wildcard for non-ASCII letters.
- **The published documents:** all 38 `docs/releases/*.md` and `REQUIRED_FILES` give the same result as before, on markdown-it-py 3.0.0 and 4.2.0 (T887's run).

**T888** (security-engineer): `docs/artifacts/security-review-t888-batch-v-v1.md`, **PASS**. All four ids are fixed. T888 corrects T885: the header-row bypass shape is no table under the GFM spec either, and the real hazard, the same shape as a body row, is refused.

New, LOW:
- **SEC-T888-01:** a `|` in a link title or destination inside a table is caught only by the table parse.
- **SEC-T888-02:** `İ` and non-letter look-alikes such as `∨` get through.
- **SEC-T888-03:** links whose target holds parentheses or follows a line break are not checked.
- **SEC-T888-04:** the help text is stale.

**The orchestrator's own verification:**
- The removed test lines were read: each is the same or stricter.
- GitLab CI lint at `88bf0fcc`: valid, with no warnings.
- SEC-T888-02 (a) and (b) were confirmed by a run of `verdict_placeholder_problems` (artifact addendum).
- The full suite and the pipeline are recorded in the merge request.

**For register v28:**
- **Fixed:** SEC-T885-01, -02, -03, SEC-T751-08. Batch V is then empty of its old ids.
- **New, LOW:** SEC-T888-01 to -04.
- **Checklist item 52 gains** T888's six release-job points.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T887 | 148k | 120k |
| T888 | 106k | 60k |
