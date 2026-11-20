# plan-184 — Batch V: the release gate after plans 142, 143 and 146

**Created:** 2026-11-20
**Based on:**
- `docs/artifacts/tracked-debt-register-v26.md` (§ 5 batches V and X; § 6.2);
- `docs/artifacts/tracked-debt-register-v14.md` § 5 (V's members) and `-v17.md` § 5 (SEC-T811-03, TL-T819-05 added);
- `docs/artifacts/security-review-t748-batch-t-v1.md` (SEC-T748-03 to -09, -12);
- `docs/artifacts/security-review-t751-batch-s-rest-v1.md` (SEC-T751-01, -05 to -09; residual status of the T748 ids);
- `docs/artifacts/security-review-t773-pi-removal-v1.md` (SEC-T773-01);
- `docs/artifacts/security-review-t811-release-gate-runner-v1.md` (SEC-T811-03);
- `docs/artifacts/tech-lead-release-v11-v1.md` (TL-T819-05);
- `docs/artifacts/security-review-t768-ca-control-v1.md` (SEC-T768-04, batch X, whose trigger is "the next tag-job change").

**Scopes:** `T883`, `T884`, `T885`.

## User decision (2026-11-20, verbatim)

> V go

## Why

Batch V is the largest tracked batch that no trigger pulls in. It hardens the release gate, which every tag depends on. The orchestrator recommended it, and the user chose it.

## Task Decomposition

1. **T883** (devops-engineer): the release-document gate, `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`. 12 ids. For each one, first re-check it against the current code, because T751 already closed parts of several (`security-review-t751-batch-s-rest-v1.md` § rows 186-187).
   - **SEC-T748-03:** a verdict section that ends at a setext or `# ` heading is a problem (fails closed).
   - **SEC-T748-04 (rest):** the `~~~` fence and multi-line reference-title residuals named in T751. The wrapper case stays documented.
   - **SEC-T748-05:** a heading at any level whose folded text equals a section name but is not the real form is a problem.
   - **SEC-T748-06:** widen the field marker and value normalisation (`>`, `1.`, `+`), and treat an empty field's sub-items as its value. Read the golden contract first.
   - **SEC-T748-07:** reword the docstring to what is tested ("tested on the locked version"). Optionally require the closing line to end with the markup.
   - **SEC-T748-08:** fix the four help and docstring overclaims, and update `test_the_help_and_the_docstring_describe_this_check`.
   - **SEC-T748-09:** `## Install` and `## Highlights` through `section_heading_indexes`, not substrings.
   - **SEC-T748-12:** replace the `Cf` filter with an allowlist. A heading counts as visible only if it holds a character that is alphanumeric and not a known filler (U+2800, U+3164, U+FFA0, U+115F, U+1160, U+034F, variation selectors).
   - **SEC-T751-06:** don't run `check_links` on a refused document, and use a non-quadratic `LINK_RE` such as `\[[^\[\]]+\]`. Show that the real documents give the same links, and give the worst-case time before and after.
   - **SEC-T751-08:** without confirming GitLab's rendering (no GitLab call), fail closed: refuse a `<` inside a code span on a line that starts with `|`. Alternatively, read the document with the table rule enabled for the HTML check.
   - **SEC-T751-09:** add `<tech-lead` to the placeholder markers. Optionally, fail on each exact `_template.md` placeholder outside code.
   - **SEC-T773-01:** tighten the UTF-8 test's skip to at most one skipped pointer, and only the next version after the newest release document.
   - **Every** `docs/releases/v*.md` must still pass at its own tag, as the existing tests check. If a fix would newly fail a published document, stop and report it as a blocker. Never edit a published release document.
   - Add a test and a mutation for each fix (the mutation on a copy, with timeout and `ulimit -v`).
   - **Leave alone:** the `sys.executable` version-check line, which T884 owns.
2. **T884** (devops-engineer): the tag jobs and the CI pins, `.gitlab-ci.yml` and `tests/functional/test_ci_hash_pins.py` (with `CONTRIBUTING.md` where a rehearsal item is named). 6 ids. Runs in parallel with T883, in its own worktree.
   - **SEC-T751-01:** in the drift gate, `rm -rf "${CI_PROJECT_DIR}.tmp"` after the second fetch, pinned by a test.
   - **SEC-T751-05:** widen the variable-precedence clause to project, group and instance level and to `CI_PROJECT_DIR`, and add the rehearsal item.
   - **SEC-T751-07:** `python3 -I` on the gate's child scripts, and `[sys.executable, "-I", ...]` for the version check in `verify-release-docs.py`, with the pins updated. Check first that no script imports a sibling module.
   - **SEC-T811-03:** structural pins that refuse `trigger:`, `inherit: default: false` (or an `inherit:default` list without `tags`) and `tags: []`, on any job.
   - **TL-T819-05:** read the GitLab Runner 19.5.3 source (download into the scratchpad only) for where the clone credential lives. Update the `rm -rf .git …` comment, or mark it unverified with the reason.
   - **SEC-T768-04 (batch X; this task changes the tag jobs, which is its trigger):** add `--ca-release` and the SPKI check to the tag jobs' CA handling, the same as the MR CA jobs. Do not change any image digest, because that would need the runner's `allowed_images` changed (checklist § 3, the user).
   - Mutations for each pin.
3. **T885** (security-engineer, read-only): review T883 and T884, with a status per id. The orchestrator supplies the diffs and the run evidence.

After T885: the orchestrator verifies (gates, clean-worktree full suite, diff read for weakened assertions), opens one merge request and merges it on a green pipeline. The **first tag pipeline after this change** is the runtime proof for the tag-job lines (T884). That is recorded in the next-release checklist, not proven here.

## Constraints

- No `docker`.
- No runner, host, project-setting or CI-variable change. No image-digest change.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/` or a published `docs/releases/v*.md`.
- Downloads go only into the scratchpad.
- Budgets: T883 120k, T884 80k, T885 60k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's approval (2026-11-20, verbatim)

The approval line above is left for the user. In the question dialog, the user answered:

> Approve (Recommended)

That option read: "All 17 V ids plus SEC-T768-04, run as T883 and T884 in parallel, then T885."

## Outcome

**Done on 2026-11-20.** MR !712.

- **T883** (devops-engineer, `a63d4f76`): SEC-T748-03, -04 (rest), -05, -06, -07, -08, -09, -12, SEC-T751-06, -09 and SEC-T773-01 fixed. SEC-T751-08 **partly fixed**: the literal rule of item 1 newly failed `v8.0.0.md:104` and 18 older published documents, so T883 refuses only a code span holding both `|` and `<` in a possible table paragraph. T885 shows a bypass (`` | `a|` `<b>` | ``); the residual is LOW and tracked. SEC-T751-09's optional part (exact template placeholders) was not taken. Every published `docs/releases/*.md` gives the same refusal, errors and links as before, on markdown-it-py 3.0.0 and 4.2.0 (T883's run). `LINK_RE` worst case at the cap: 7.62 s before, 0.001 s after.
- **T884** (devops-engineer, `74a1a54b`, cherry-picked as `c4b53aba`): SEC-T751-01, -05, -07, SEC-T811-03, TL-T819-05 (settled from the Runner v19.5.3 source) and SEC-T768-04 fixed. No image digest or runner tag changed.
- **T885** (security-engineer): `docs/artifacts/security-review-t885-batch-v-v1.md`, **PASS**. New LOW: SEC-T885-01 (`LINK_RE` tail still quadratic), SEC-T885-02 (homoglyph look-alike headings), SEC-T885-03 (`publish-release.py` without `-I` in the token-holding `release` job), SEC-T885-04 (no pin that the drift gate's image equals `ca-chain-check-python`'s).

**The orchestrator's own verification:**
- The removed test lines were read: every replaced assertion is the same or stricter.
- At `c4b53aba`: `test_verify_release_docs` and `test_ci_hash_pins` (342 tests) OK; all gates exit 0; root drift `[]`; GitLab CI lint valid with no warnings.
- The reviewer's two assumptions were checked (artifact addendum): the four jobs share one image digest; a top-level `include` is refused.
- The first clean full suite at `c4b53aba` gave 1 error: `test_check_release_tag_tree` still quoted the tree-check line without `-I`, which T884 had not updated. The orchestrator updated that literal (a mutation dropping `-I` from the CI line fails the test) and re-ran the suite at the final head.
- The full suite and the pipeline are recorded in the merge request.

**For register v27:**
- Fixed: the 17 ids above and SEC-T768-04 (batch X).
- Partly fixed, tracked LOW: SEC-T751-08 (follow-up: the HTML check on a parse with the GFM table rule enabled).
- New, LOW: SEC-T885-01 to -04.
- Next-release checklist: the first `v*` tag pipeline must show T885's list of seven points; the user checks that no CI/CD variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists at project, group or instance level.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T883 | 192k | 120k |
| T884 | 134k | 80k |
| T885 | 106k | 60k |
