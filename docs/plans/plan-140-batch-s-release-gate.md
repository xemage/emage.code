# plan-140 — Batch S: the release gate after the parser

**Created:** 2026-11-06
**Based on:** `docs/artifacts/tracked-debt-register-v9.md` § 3 and § 5 (batch S, 15 ids), `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4, `docs/artifacts/security-review-t738-batch-n-two-v1.md` § 4, `docs/artifacts/security-review-t741-gate-pin-v1.md` § 4. The user's answer of 2026-11-06, verbatim: "S go".
**Scopes:** `T743`, `T744`.

## Goal

Close batch S before the next tag: the routes left in the Cursor check, the job's exposure to tokens, what the pin leaves unpinned, and the child's lenient reads.

## Facts read before this plan (orchestrator, 2026-11-06)

- **Project settings, by read-only API.** `ci_pipeline_variables_minimum_override_role` is `no_one_allowed` and `restrict_user_defined_variables` is true, so nobody can set a pipeline variable. That is stricter than A-17 asked, and SEC-T741-16's route is closed on this project while the setting stands. `v*` tags are protected, and Maintainers may create them, which answers A-18. `main` and `develop` allow no direct push. `shared_runners_enabled` is false.
- **The 33 release documents, parsed with the locked `markdown-it-py` 4.2.0.** None opens with `---`, `+++` or `;;;`. None has raw HTML or inline HTML in its Migration Guide. The longest line is 3597 characters. `scripts/install.sh`, `README.md` and `CHANGELOG.md` hold no CR.
- **TD-T739-01 on 4.2.0.** `<a` followed by ` x="y"` repeated: 0.07 s, 0.17 s, 0.51 s, 1.60 s and 5.45 s at 60 KB, 120 KB, 240 KB, 480 KB and 960 KB. That is worse than linear, as on 3.0.0.

## Task Decomposition

1. **T743** (devops-engineer): the gate script and its tests, 10 ids.
   - **SEC-T739-02.** An anchor holding non-comment inline HTML does not count: `**<span hidden>Cursor</span>**` and a heading with such a tag give False. Comments stay allowed. Update `--help`.
   - **SEC-T739-03.** Fail closed instead of balancing tags: in the section, an anchor after a raw `html_block` that is not a comment does not count. Update `--help`, which now lists this as open.
   - **SEC-T739-04.** Refuse a release document whose first line is `---`, `+++` or `;;;`, naming the path, because GitLab may read what follows as front matter.
   - **SEC-T739-08.** Reword `docs/releases/_template.md:3` and the error at `verify-release-docs.py` ("lead line"), to "a paragraph that opens with a `**` span holding the word, optionally in a list". Point the two `CONTRIBUTING.md` lines at the gate to step 4's install. If any line under `implementation/knowledge/` would need the same change, stop and report it: this plan makes no knowledge edit.
   - **SEC-T739-09.** One sentence in `--help` on the nesting limit, which fails closed. Replace the label "(SEC-T738-04)". Add fixtures: nesting past the limit, an anchor in a reference definition's title, lazy continuation.
   - **SEC-T738-02.** Refuse a CR in `scripts/install.sh` from the raw bytes, naming the line. CRLF Markdown stays allowed. One sentence in `MIGRATION_POINTER_HELP`: the rule catches an omission on one line and does not defend against a crafted script.
   - **SEC-T738-06.** Escapes instead of raw U+2028 and U+2029 in `tests/functional/test_verify_release_docs.py`: `CHARS`, `UNSAFE_SAMPLES` and the other lines the register names.
   - **TD-T739-01.** Refuse a document with a line longer than 65536 characters before parsing it, naming the path and line and no content. Measure that a document at the limit stays well under a second. If many long lines together still scale badly, report it.
   - **SEC-T741-07.** A clause in `--help`: a document on an `install.sh` line without "Cursor" is checked for existence only.
   - **SEC-T741-08.** Replace the text match in `test_the_script_has_one_way_to_read_a_file` with an AST walk: no `open`, no `.read_text`, and `read_bytes` and `.decode` in `read_strict` only.
   - *Acceptance:*
     - each fix has a test that fails on the old code, or a stated reason; each new check survives a mutation;
     - `python3 scripts/verify-release-docs.py --tag v9.0.0` passes, on 3.0.0 and on the locked 4.2.0;
     - all 33 release documents give the same Cursor result as before; report any that changes;
     - the module's tests, `validate-tasks.py`, `test_link_integrity` and team health pass. Functions stay under 50 lines and 4 parameters.
2. **T744** (devops-engineer, after T743): the pipeline, the pins and the child, 5 ids.
   - **SEC-T739-06.** First `before_script` line of `release-docs-gate`: `unset WIKI_TOKEN CI_JOB_TOKEN CI_REGISTRY_PASSWORD CI_REPOSITORY_URL`. Check the list against GitLab's documentation of predefined variables, and report any credential variable it misses. Update the pin. The clone credential in `.git/config` stays, and contract 6 or the job's comment says so.
   - **SEC-T741-17.** `GIT_STRATEGY: clone` on `release-docs-gate` and `main-develop-drift-gate`, pinned. The dedicated runner tag needs a runner, so it stays open for the user: do not add a tag no runner holds.
   - **SEC-T741-12.** Exact values for `release.script` and `release.artifacts`, and for `default.tags` and `default.interruptible`.
   - **SEC-T741-16.** A clause in contract 6: the rule on tag jobs assumes nobody can set a pipeline variable, which is this project's setting and not something a test reads. Add it to the plan's Outcome.
   - **SEC-T741-06.** `scripts/check-version-consistency.py:148, 177` and `scripts/dry-run-publish-release.py:255` read strictly and exit non-zero, naming the path and offset. First run the script itself on the tree and confirm that nothing it scans is invalid. Do not write your own scan that walks `tests/golden/`. `.gitlab-ci.yml:67`, the informational `markdown-links` job, stays: it decides nothing.
   - **`.gitlab-ci.yml` changes in this task, so check it live.** With the read-only lint, confirm the file is valid, and that a dry run with `ref: v9.0.0` runs the same three jobs.
   - *Acceptance:*
     - each mutation of a pin fails a test;
     - `ci_pin_problems` passes on the new file;
     - the tests of every module that reads the CI file pass: `test_ci_hash_pins`, `test_publish_release`, `test_publish_release_t730`, `test_publish_release_job_token`, `test_check_release_tag_tree`, `test_gitlab_exposure_docs`, plus the consistency script's own tests;
     - `validate-tasks.py`, `test_link_integrity` and team health pass.

## Not changed in this plan

- **Batch T,** SEC-T739-07: it needs its own plan.
- **Other batches,** including batch N's `scripts/verify-release-docs.py` regexes.
- **No knowledge edit,** so no root refresh.
- **The runner tag of SEC-T741-17,** which needs a runner.

## Not verifiable before the next tag

No merge request pipeline runs `release-docs-gate` or the drift gate, so the `unset` line and `GIT_STRATEGY: clone` run for the first time in a tag pipeline, as the parser install does. A release candidate would prove them first. The lint's dry run proves the configuration only.

## Constraints

- **Mutation runs, not optional.** Never mutate a worktree. Mutate a throwaway copy under the scratchpad, excluding `tests/golden`. Each test run has a timeout and a memory cap. Count a timeout as caught. Run nothing else in parallel. Stop if available memory falls under 3 GB. An unbounded mutation run took the devcontainer down during T741.
- `tests/golden/**` and `scripts/scorecard.py` stay untouched. Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`.
- Subagents never merge, tag or release, and do not run the full suite. The orchestrator verifies, a Security Engineer reviews, and the orchestrator merges on a green pipeline. A new finding at MEDIUM or above goes to the user.

## Outcome (2026-11-06)

- **T743 and T744 are done.** 13 of the 15 ids are closed; TD-T739-01 and SEC-T741-17 are open in part (below).
  - **Cursor check.** Any raw or inline HTML other than comments before the anchor, anywhere in the document, means no anchor counts. A document that opens like front matter is refused, and so is a line over 65536 characters. `scripts/install.sh` may hold no CR.
  - **Pipeline.** `release-docs-gate` unsets the credentials first, and both gates use `GIT_STRATEGY: clone`. `release`'s script and artifacts and `default`'s values are pinned exactly. The version check and the dry run read strictly.
- **Security review.** `docs/artifacts/security-review-t745-batch-s-v1.md` gives CONDITIONAL_PASS, and that record meets its one condition. 0 CRITICAL, 0 HIGH, 0 MEDIUM. 13 LOW tracked until the next register: SEC-T745-01 to -11 and the rest of TD-T739-01 and SEC-T741-17. TD-T745-01 is ungraded.
- **The orchestrator's check** is in the review's Metadata.
- **A ruling that widened the plan.** T743's first report left three routes open: inline HTML in an earlier paragraph, raw HTML above the section, and a hidden section title. The orchestrator confirmed them on 4.2.0, and ruled them into SEC-T739-02 and -03 as one rule, because listing places was the mistake T741 made three times. None of the 33 documents holds HTML other than comments. The reviewer finds the widening sound.
- **Where this plan's figure was wrong.** The plan asked that a document at the limit stay "well under a second". T743 measured 1.52 s for `![`, and the reviewer's inputs measure about 10 s for one line at the limit and over 90 s for 200 KB of short lines. A line limit does not bound parse time. Worst case, the job stalls until the project's 3600 s timeout and fails closed. SEC-T745-01 tracks it.
- **Found while checking: `ANTHROPIC_API_KEY` (TD-T745-01).** T744 had no tool to read project variables. The orchestrator listed their names through the API, printing no value: `WIKI_TOKEN`, protected, and `ANTHROPIC_API_KEY`, masked and not protected. Nothing in `.gitlab-ci.yml` names the second, so it looks unused, yet it reaches every job on every branch.
  - `8ee1e2d3` adds it to the docs gate's `unset` line and pin. This is an orchestrator edit after the review, and it was not re-reviewed.
  - **Deleting or protecting it is the user's decision.** No project setting was changed.
- **Facts for the user actions.** A-17 and A-18 are answered by the settings in § Facts read before this plan, with no change made: `ci_pipeline_variables_minimum_override_role` is `no_one_allowed`, and `v*` tags are protected for Maintainers. A Maintainer can still tag a commit that never went through a merge request, so the merge guard's limit stands.
- **SEC-T741-16's clause,** which this plan said to record here: the rule on tag jobs assumes nobody can set a pipeline variable, which is this project's setting and not something a test reads. It is in contract 6.
- **Rulings.**
  - **T744's report said an `exit 0` in `release.before_script` passes.** The reviewer corrected that, and the orchestrator confirmed it on a copy: `test_the_bootstrap_is_the_exact_text_that_yaml_parses_to` catches it.
  - **The `--help` label** "What stays open" stands, as T743 chose.
  - **The list of `SEC-T745` Lows stays tracked** under the user's policy ("Track LOW items as debt, stop chasing (Recommended)"), and none is folded in.
- **Mutation runs** followed the new rules: throwaway copies, a timeout and a memory cap on each run. T743 reports 83 of 83 caught, after one real gap was closed. T744 reports all caught, after one real gap was closed and an equivalent mutant led to a simpler read. The orchestrator re-ran about 30 shapes and 8 pin edits, not the harnesses.
- **For the next register's checklist.**
  - **Watch these in the first tag pipeline,** with the parser install: the `unset` line and `GIT_STRATEGY: clone`. No merge request pipeline runs them. A release candidate would prove them first.
  - **A new CI/CD variable** needs adding to `GATE_CREDENTIALS` and the `unset` line. No test reads the project's variables.
  - **A release document** may hold no HTML other than comments before its Cursor item.
  - **A release script change** now needs the same edit in `RELEASE_COMMAND`.
  - A-17 and A-18 can close, with the facts above. TD-T745-01 is new for the user.
- **Not verified.** The review's section 5.
- **Token use against budget** (the harness's counts, which include context):

  | Task | Used | Budget |
  |---|---|---|
  | T743, both rounds | about 194k | 120k + 25k |
  | T744 | about 172k | 100k |
  | Security review | about 207k | 120k |

