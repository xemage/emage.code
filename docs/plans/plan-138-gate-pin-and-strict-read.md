# plan-138 — Two batch S fixes: the gate job's pin, and strict decoding

**Created:** 2026-11-05
**Based on:** `docs/artifacts/tracked-debt-register-v8.md` § 3 and § 5 (batch S), `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4. The user's answer of 2026-11-05, verbatim: "05 01 go".
**Scopes:** `T741`.

## Goal

Close the two findings the reviewer would take first in batch S:

- **SEC-T739-05.** `allow_failure: true`, `when: manual` or an `exit 0` line can soften `release-docs-gate` without a test failing, and `needs` in `release` does not stop a release after an allowed failure.
- **SEC-T739-01.** `errors="ignore"` drops invalid bytes before parsing, so `<!-- x --\xff>` closes a comment here that a renderer replacing the byte keeps open, and a hidden anchor counts.

The other nine ids of batch S stay tracked. The user's answer named these two only.

## Task Decomposition

1. **T741** (devops-engineer):
   - **SEC-T739-05, in `tests/functional/test_ci_hash_pins.py`, `release_gate_job_problems`.** The job is pinned from an allowlist, not a denylist:
     - the job's keys are exactly `stage`, `image`, `before_script`, `script` and `rules`, which refuses `allow_failure`, `when`, `variables`, `extends`, `after_script` and anything added later;
     - `script` equals `[RELEASE_GATE_COMMAND]`;
     - `rules` equals the one tag rule, exactly;
     - `stage` equals `release`.
     - `.gitlab-ci.yml` does not change, and the check must pass on it as it is.
     - One mutation test for each of: `allow_failure: true` on the job; `allow_failure: true` inside the rule; `when: manual` on the job; `when: manual` inside the rule; a `variables` block; `extends`; an `exit 0` line before the gate command; a second rule; a changed tag pattern.
   - **SEC-T739-01, in `scripts/verify-release-docs.py`.** One helper replaces all seven `errors="ignore"` reads, so none is left in the script.
     - A file that is not valid UTF-8 is refused: the gate exits 1 and names the path and the first bad byte's offset **in the file**, and never the content. Note that `UnicodeDecodeError.start` from `read_text` is relative to a decoding chunk, so decode the whole file's bytes to get the true offset.
     - No traceback, and no check runs on a partly decoded file.
     - Newline handling does not change: CRLF and CR are read as they are today. SEC-T738-02 stays open, and this fix neither closes nor widens it.
     - One sentence in `--help` and the module docstring says so.
     - Fixtures: the `<!-- x --\xff>` shape in a release document; invalid bytes in `scripts/install.sh`, a marker file and a document that `install.sh` points to; an offset beyond the first decoding chunk (over 8192 bytes), asserted exactly; the error holds no byte of the content; a control with CRLF that still passes.
   - **The real tree must still pass:** `python3 scripts/verify-release-docs.py --tag v9.0.0`. Check that every file the gate reads on this tree is valid UTF-8, and report it.
   - *Acceptance:*
     - each mutation fails a test, and each new test that guards a fix fails on the old code; say which do not, and why;
     - `grep -n 'errors="ignore"' scripts/verify-release-docs.py` finds nothing;
     - `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_verify_release_docs.py`, `tests/functional/test_check_release_tag_tree.py`, `tests/functional/test_publish_release.py`, `validate-tasks.py`, `test_link_integrity` and the team-health tests pass. Functions stay under 50 lines and 4 parameters.

## Not changed in this plan

- **The other nine ids of batch S and batch T:** SEC-T738-02, SEC-T738-06, SEC-T739-02, -03, -04, -06, -08, -09, TD-T739-01 and SEC-T739-07. This includes the "(SEC-T738-04)" label in `--help`, which SEC-T739-09 holds.
- **The `release-docs-gate` job itself,** and the `release` job's `needs`, which `test_publish_release.py` and `test_check_release_tag_tree.py` already pin.
- **`errors="ignore"` elsewhere.** `scripts/publish-release.py:688` decodes an HTTP error body, not a checked document.
- **No knowledge edit,** so no root refresh.

## Changes after the first security review

The review of `201f2954` gave CONDITIONAL_PASS with four new MEDIUM findings, all older than T741: routes that soften the gate in `.gitlab-ci.yml` with every test green. The user was asked when to fix them and answered, verbatim: "Fix all four first (Recommended)". The option said: add them to plan-138 with the overclaiming wording SEC-T741-05, then re-review and merge; tests only, no CI file change; the other three LOWs stay tracked.

The orchestrator confirmed the routes before asking.

- **GitLab's CI lint** (read-only, `POST /projects/:id/ci/lint`) resolves a trailing `<<: {script: ["exit 0"]}` to `exit 0`, and a `<<` inside a rule overrides its `if`. A leading `<<` does not override.
- **On a throwaway copy,** each of these edits adds no failure in the seven test modules that read the CI file: a trailing `<<` on `script` and on `rules`; `include:`; a `PYTHONPATH` in top-level `variables:`; `workflow:` with variables; `image: evil:latest # x`; `image: {name: ...}`; `needs: []` on `release`; `when: always` on `release`; `when: manual` on the drift gate. A foreign image with a digest is caught.

So this section replaces the plan's `Not changed` entry on the `release` job: its `needs` is not pinned in a form a comment cannot satisfy.

T741 therefore also does the following. `.gitlab-ci.yml` still does not change, and every check must pass on it as it is.

- **SEC-T741-01.** Refuse merge keys in the whole CI file, from `yaml.compose`, because PyYAML and GitLab's parser disagree on them. Mutations: a trailing `<<` overriding `script`; one overriding `rules`; one inside the rule; a leading one; a quoted one.
- **SEC-T741-02.** Pin `release` and `main-develop-drift-gate` from the parsed file, as an allowlist of keys. Today's keys are `stage`, `needs`, `image`, `variables`, `before_script`, `script`, `artifacts`, `rules` for `release`, and the same without `needs` and `artifacts` for the drift gate. `needs` is compared as a parsed list, `rules` and `variables` exactly, and the drift gate's `script` exactly, because it is a gate. Mutations: `needs: []` with the old line commented out; `optional: true`; `when` and `allow_failure` on the job and in the rule, for both jobs.
- **SEC-T741-03.** Pin the file level.
  - Refuse `include`, `workflow` and `spec`, and the global forms GitLab still honours: `image`, `services`, `cache`, `before_script`, `after_script`.
  - Compare top-level `variables` and `stages` exactly.
  - `default` holds only `image`, `interruptible` and `tags`.
  - Outside the three pinned jobs, a job with `artifacts` must have `rules`, each with an `if` from an allowlist of today's branch and merge request conditions, so that it cannot run in a tag pipeline.
  - One mutation for each.
- **SEC-T741-04.** In the three pins, `image` is a string that fully matches `python:3\.12-alpine@sha256:[0-9a-f]{64}`. The digest tests in `test_ci_hash_pins.py` and `test_publish_release.py` walk the parsed `image` values of `default` and every job instead of the text regex. A mapping is refused. Mutations: `image: evil:latest # x`; `image: {name: ...}`; the block mapping form.
- **SEC-T741-05, because it corrects claims this change wrote.** Reword the three sentences as the review lists them: the pin says which routes it covers; the sentence on `safe_load` and merge keys goes or states the difference; "every file the gate reads" says "in this process" and names `scripts/check-version-consistency.py`.

**Stays tracked as LOW,** for the next register: SEC-T741-06 (the child's lenient reads), SEC-T741-07 (a pointed document that is not read), SEC-T741-08 (the narrow source test).

**A correction to this plan.** Its sentence that `UnicodeDecodeError.start` from `read_text` is chunk-relative was the orchestrator's, and it is wrong for a whole-file read: T741 did not reproduce it, and the orchestrator measured the true offset at 20000 on ASCII and multibyte prefixes. Decoding the bytes remains right, and the exact-offset test stays.

## Constraints

- `tests/golden/**` and `scripts/scorecard.py` stay untouched. Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`.
- Subagents never merge, tag or release. The orchestrator verifies, a Security Engineer reviews, and the orchestrator merges on a green pipeline.

## Changes after the second security review

The second review, of `ec2ea70b`, closed SEC-T741-01 to -05 and found two more MEDIUM routes, SEC-T741-09 and -10, both older than T741. The orchestrator confirmed both on GitLab's lint. The user answered, verbatim: "Fix, narrow re-review (Recommended)". The option said: fix -09 and -10, plus -13 and -14; the same reviewer checks only that new diff; merge after; -11 and -12 stay tracked as LOW.

The narrow re-review of `036b4e47` closed those and found SEC-T741-15, a third route of the same kind, again older than T741: a `pages` job makes artifacts without an `artifacts` key. The orchestrator put to the user that the pin listed dangerous job shapes, and offered to invert it. The user answered, verbatim: "Invert the rule, then stop (Recommended)". The option said: any other job that could run on a tag is refused, whatever it does; the same reviewer checks that one diff; if it finds yet another route, the orchestrator records a remediation plan and merges unless it is HIGH or worse. It found none above LOW, so that clause was not used.

## Outcome (2026-11-06)

- **T741 is done.** Ids resolved: SEC-T739-05, SEC-T739-01, and from this plan's reviews SEC-T741-01 to -05, -09, -10, -11, -13, -14 and -15.
  - **The gate** refuses a checked file that is not valid UTF-8, naming the path and the offset. No `errors="ignore"` is left in `scripts/verify-release-docs.py`.
  - **`ci_pin_problems`** now pins the three tag jobs and the file level from parsed values, as allowlists, and refuses spellings GitLab folds. Outside the three tag jobs, no job may be able to run in a tag pipeline, whatever it does.
  - `.gitlab-ci.yml` did not change. `tests/functional/test_knowledge_template_images.py` changed too, beyond the brief's first list (see below).
- **Security review.** `docs/artifacts/security-review-t741-gate-pin-v1.md`: PASS on the last round. 0 CRITICAL, 0 HIGH, 0 MEDIUM remaining; 6 LOW tracked until the next register: SEC-T741-06, -07, -08, -12, -16, -17.
- **The orchestrator's check** is in the review's Metadata. The strongest evidence: on GitLab's dry run with the tag `v9.0.0`, the real file runs exactly the three pinned jobs, and every edit that softened the gate in GitLab's lint has at least one pin problem. Final verification at the merged commit: all gates pass, drift empty, 2543 tests OK with 24 skipped.
- **Skips.** All 24 are live or optional tests: the CWSO live contract and integration tests, the real-embedding pipeline, retrieval performance, `pip-audit` end to end, and the Playwright matcher. None is a gate. Runs on this plan's trees reported 13, 24 and 25. The count moves with what the environment offers, and the difference between runs was not traced further.
- **Three reviews, three new routes.** Each round of MEDIUMs was older than T741. They come from one cause: this is a check with PyYAML of a file GitLab reads with another parser, and the first design listed dangerous shapes. So no pin can be proved complete. Contract 6 states its routes and limits.
- **A crash, and what it taught.** On 2026-11-05 the implementer's mutation script ran in the worktree with no timeout. Its "no seen-set" mutation made the YAML walker loop forever on `test_a_recursive_alias_ends`, with the stack growing at about 17 MB/s (measured), and the devcontainer became unresponsive and was rebooted. That this caused the crash is an inference, because no system logs were read; the endless loop and the growth rate were measured.
  - The killed script left that mutation in the worktree. The orchestrator found it by checking every mutation's original text, and restored one line.
  - The test now runs in a child with a time limit and a memory cap, and later mutation runs used a throwaway copy, with both limits.
  - The orchestrator's brief had not asked for limits.
- **Who wrote what.** The implementer's report never arrived, and its agent could not be resumed. On the user's "Finish T741 yourself", the orchestrator finished and verified the rest, so the second reviewer was told it was the only independent check on those commits.
- **A regression the full suite caught, after the narrower runs missed it.** `b23c756f` made `eol_image_problems` parse its input, and `test_knowledge_template_images` feeds it joined `image:` lines. That raised 96 errors on empty input, and with several images the repeated key would have collapsed to the last one, so an end-of-life image before it would have passed. `ec2ea70b` separates the check from the walk and adds a regression test, proved on a copy.
- **Rulings.**
  - **SEC-T741-05** was folded in as claims this change wrote. **SEC-T741-13 and -14** were folded in by the user's option.
  - **Mutation "image without str check"** stays uncaught: `fullmatch(str(image))` cannot change a result, and the reviewer traced the same.
- **For the next register's checklist.**
  - Register v8 § 6.2 item 15, "no test catches this yet", is out of date: `allow_failure` on any tag job now fails a test. The job must still stay without it.
  - A new job in `.gitlab-ci.yml` needs an `if` from `NOT_TAG_CONDITIONS`. Adding a condition means checking that it is false on a tag.
  - A digest bump across all jobs passes. An `apk` pin or a Python minor bump needs a test constant edit; the CI header's bump recipe does not say so yet.
  - SEC-T741-16 has a user side: the project's minimum role for pipeline variables is a project setting, not checked here.
- **Not verified.** The list is in the review's section 5, including that artifacts from a `pages` job reach the gates, and project settings such as protected tags.
- **Disclosed.** While checking routes, the orchestrator sent the real `.gitlab-ci.yml` and small test files to this project's GitLab CI lint, which is read-only. Its `dry_run` creates no pipeline. The `ci` tool category was activated in the GitLab MCP session. Two reboots wiped `/tmp`, including the leftover `/tmp/emage-symlink-guard-q8kvpw64` that plan-136 named.
- **Token use against budget** (the harness's counts, which include context):

  | Task | Used | Budget |
  |---|---|---|
  | T741, first and stopped second round | about 188k | 90k + 60k |
  | First security review | about 164k | 60k |
  | Second security review, all three rounds | about 193k | 60k + 30k + 25k |
