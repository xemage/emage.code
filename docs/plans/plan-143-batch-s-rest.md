# plan-143 — What is left of batch S

**Created:** 2026-11-06
**Based on:** `docs/artifacts/tracked-debt-register-v10.md` § 5 (batch S), `docs/artifacts/security-review-t745-batch-s-v1.md` § 4, `docs/artifacts/security-review-t748-batch-t-v1.md` § 3, § 10, `docs/plans/plan-142-verdict-check-tokens.md` § Outcome. The user's answer of 2026-11-06, verbatim: "Sgo".
**Scopes:** `T749`, `T750`, `T751`.

## Goal

Close the 12 of batch S's 13 ids that need nothing from outside the repository. SEC-T741-17's dedicated runner tag stays open: it needs a runner, which is the user's to provide.

## What the orchestrator measured on `d989ecb7`

- **Size.** The largest release document is `v8.0.0.md`, 66,745 characters; then `v9.0.0.md`, 61,186.
- **HTML.** The parser finds live HTML, meaning anything other than comments, in no document under `docs/releases/` but `_template.md`, whose `<placeholder>` text reads as HTML. `README.md` holds none either.
- **Git.** `scripts/verify-release-docs.py` and `scripts/check-version-consistency.py` start no `git`. The gate's only child process is the version check.

## Design

**The gate script (T749).**

- **No HTML other than comments, anywhere in a release document** (SEC-T745-03). `document_refusal` refuses it, by the parser's tokens, after the size and line limits. This replaces the reviewer's narrower options, because no real document needs HTML. `has_cursor_migration_item` applies the same rule to a pointed document, in place of "the first HTML ends the search". The message names the path and a line, never the content.
  - It also closes SEC-T748-13 and the `<div hidden>` wrappers under SEC-T748-04 and SEC-T748-12, and SEC-T748-02's `<span hidden>` heading on the gate's route. Those ids are batch T's, for the next register; T749 reports what each one still leaves.
  - `heading_is_visible` and `html_block_holds_line` stay. They still guard a direct call. Do not remove them in this plan.
- **A total size cap** (SEC-T745-01, TD-T739-01's rest): `MAX_DOCUMENT_CHARS = 131072` (128 KiB), about twice the largest document. `markdown_tokens` returns None above it, as it does for a long line, so no route reaches the parser, and `document_refusal` names it. Measure the worst shapes at the cap on the locked 4.2.0, with a time limit on each run, and state the result in `--help`. Do not claim a bound you did not measure.
- **`FRONT_MATTER_OPENING_RE`** (SEC-T745-02): replace the optional group with a `partition("\n")` check of the first line, then one test of the body. Same accepted and refused documents, in linear time. Compare old and new on crafted and real documents.
- **`_read_route_problems` and `test_the_parser_has_one_call_site`** (SEC-T745-08): as the review's fix.
- **`find_markdown_files`** (SEC-T745-09): skip `node_modules` and any directory holding `pyvenv.cfg`. List what else it skips.
- **`evaluate`** (SEC-T745-10): `ascii()` on the path, as `refusal_line` does.
- **`document_refusal`'s docstring** (SEC-T745-11): "before parsing it". The refusal now parses for HTML, so word it to match what the code does.
- `--help`, the module docstring, `docs/releases/_template.md` (a sentence that release authors must replace every `<placeholder>`, if it does not already say so) and `CONTRIBUTING.md`, wherever they state these rules.

**The pipeline (T750).**

- **`scripts/run-allowlisted.py`,** new and small: `run-allowlisted.py [--keep NAME]... -- COMMAND...` replaces itself with `COMMAND`, through `os.execvpe`, under an allowlisted environment. The allowlist is the one in `release`'s `before_script` (`PATH`, `HOME`, `LANG`, `LANGUAGE`, `TMPDIR`, `TZ`, `SSL_CERT_FILE`, `SSL_CERT_DIR`, `CURL_CA_BUNDLE`, the proxy names and `LC_*`). Run it with `python3 -I`. No dependency, and a test.
- **`release-docs-gate`** (SEC-T745-05): pip and the gate run through it, in place of the `unset` line, and a first line `rm -rf .git` removes the clone credential, because nothing in this job uses git. That retires `GATE_CREDENTIALS`, `RELEASE_GATE_UNSET` and the name `ANTHROPIC_API_KEY`.
- **`main-develop-drift-gate`** (SEC-T745-04): `apk add` and the two scripts run through it with no `--keep`. The two `git fetch` lines run through it with `--keep CI_JOB_TOKEN`, because git may need the token. Check how GitLab documents the clone credential; if that is not certain, say **(unverified)**, because only a tag pipeline proves it.
- **`timeout`** (SEC-T745-01): `timeout: 10 minutes` on `release-docs-gate`, so a crafted document at the cap stops well before the project's 3600 s. Adjust it only if the measurement above says so, and say why.
- **`release`** (SEC-T745-07): `GIT_STRATEGY: clone`.
- **Pins:** each of these in `PINNED_JOBS` and the file's constants, exactly. The job's `keys` gain `timeout`. **Contract 6** gains a clause for SEC-T745-06: a project-level `GIT_STRATEGY` may beat the pin (the reviewer's memory, mark it so), and the project must hold no variable of that name. The comment in `.gitlab-ci.yml` must match.
- **GitLab's read-only CI lint is the ground truth for the routes:** `POST projects/em-age%2Femage.code/ci/lint` with `include_merged_yaml`, and with `dry_run: true, ref: v9.0.0, include_jobs: true`. It creates no pipeline. PyYAML and GitLab's parser can differ.
- `release`'s `before_script` stays as it is. Moving it onto the new script is a later change.

## Task Decomposition

1. **T749** (devops-engineer): the gate script, `tests/functional/test_verify_release_docs.py`, `tests/functional/test_check_version_consistency.py`, and the docs named above.
   - *Acceptance:*
     - each id has a test that fails on the old code and passes on the new, shown on a throwaway copy;
     - the 35 files under `docs/releases/`: every `v*.md` is refused by no new rule, and `--tag v9.0.0` passes on 3.0.0 and the locked 4.2.0;
     - tests that reach HTML through `check_release_brief` now expect the refusal, and each shape they covered stays tested on `verdict_placeholder_problems` directly;
     - the front matter check gives the same answer as the old one on every document and crafted shape you try, listed in the report, and the 12.75 s shape takes under a second;
     - a mutation of each new rule is caught.
2. **T750** (devops-engineer), after T749: the new script, `.gitlab-ci.yml`, `tests/functional/test_ci_hash_pins.py`, and tests that read the pinned commands (`test_publish_release*.py`, if they do).
   - *Acceptance:*
     - the script's own test proves that a secret variable does not reach the child, an allowlisted one does, `--keep` works, and a missing command fails;
     - a local dry run of the gate through the script from a `git archive` export with no `.git` passes, and so do the drift scripts under the allowlist;
     - GitLab's lint is valid, and its tag route still runs only the 3 tag jobs. Paste what it says about each job's keys;
     - each pinned value has a mutation that fails `test_ci_hash_pins`.
3. **T751** (security-engineer): review both, read-only. Questions: are the 12 ids closed; which route lets a hidden or unfilled release document pass now; is `rm -rf .git` safe for this job; does the allowlist leak; does the pin still guard all of it; what do the batch T ids still leave.

**Every mutation run:** a full throwaway copy under the session's scratchpad, excluding `tests/golden` and `node_modules`; the script aborts unless the unmutated baseline passes; `subprocess.run(..., timeout=120, preexec_fn=...)` with `RLIMIT_AS` of 3 GiB; one at a time; stop below 3 GB available; a timeout counts as caught; never in a worktree. The same limits on any timing run.

## Not changed

- SEC-T741-17's runner tag; SEC-T748-05, -06, -07, -08, -09 and -03; TD-T746-01. They stay tracked.
- `tests/golden/**` and `scripts/scorecard.py`. `implementation/knowledge/`, so no root refresh is expected.

## Not verifiable before a tag

The real jobs do not run on a merge request, so `run-allowlisted.py`, `rm -rf .git`, `timeout` and the fetch under `--keep` are unproved until a tag pipeline runs them. If one breaks, the release stops and fails closed. A second gate probe would prove all but the `release` job. **It needs the user's approval**, and the tag can be deleted only in the web interface.

## Constraints

- Functions of at most 50 lines and 4 parameters. Conventional Commits. Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file.
- Subagents never merge, push, tag or release. The orchestrator verifies and merges on a green pipeline.
- The user's policy: LOW items are tracked, not chased. No fix round after T751 for a LOW that this plan did not introduce.

## Outcome (2026-11-06)

- **Done: T749, T750, T751.** Closed: SEC-T745-01 to -11 and the rest of TD-T739-01. On the gate's route also SEC-T748-02 and -13. SEC-T748-04 and -12 narrow. SEC-T741-17's dedicated runner tag stays open: it needs a runner, which is the user's to provide.
- **The gate refuses,** in this order: a document over 131072 characters; a line over 65536; a front matter opening; the parser's nesting limit; HTML other than comments, anywhere. The largest real document is 66,745 characters, and the deepest reaches level 5 of 20.
- **The pipeline.** `release-docs-gate` opens with `rm -rf .git "${CI_PROJECT_DIR}.tmp"`, has `timeout: 10 minutes`, and runs pip and the gate through `scripts/run-allowlisted.py`. `main-develop-drift-gate` runs every command through it, and the two fetches keep `CI_JOB_TOKEN`. `release` has `GIT_STRATEGY: clone`. All are pinned. The `unset` line, `GATE_CREDENTIALS` and the name `ANTHROPIC_API_KEY` are gone.
- **The orchestrator's design was wrong in two places, and the implementers caught both.**
  - The plan said `rm -rf .git` removes the clone credential. On runner 19.5.2 `.git/config` only includes a file in `$CI_PROJECT_DIR.tmp` (T750, source reading), so that directory goes too.
  - The plan's `pyvenv.cfg` skip let a committed file silence the version check for `docs/wiki` (T749). The orchestrator narrowed it to the exact paths `ci/js/node_modules/`, `.venv/` and `venv/`.
- **A rule added on T749's finding:** past the parser's nesting limit the rest of a list's document is not read, so "no HTML anywhere" did not hold. The document is now refused there.
- **A deviation, to report to the user.** T750 ran the pinned image through `docker`, beyond its brief. `DOCKER_HOST` points at `ssh://root@10.10.160.11`, so the containers ran on that host, as T728's did, which also runs the user's `portainer` and `hindsight`. The orchestrator's brief did not forbid it. The orchestrator checked afterwards: only those two containers exist, no other image is left, and nothing of the agent was still running. Future briefs forbid `docker` unless the user approved it.
- **Review:** CONDITIONAL_PASS, `docs/artifacts/security-review-t751-batch-s-rest-v1.md`; 0 CRITICAL, 0 HIGH, 0 MEDIUM; 9 LOW. The reviewer found no check weaker on the gate's route. Fixed in `6c58244b`, as this plan's own: SEC-T751-02, -03, -04. These edits add a test and change wording and a message, not gate logic, and were not re-read. Tracked until the next register: SEC-T751-01, -05, -06, -07, -08, -09. Its conditions are that they are tracked, and that the first tag pipeline confirms the removal, the wrapper and the fetches.
- **Observed for the first time:** GitLab's Markdown API strips `hidden` and removes `<style>` (the review's closing section). A Release description is **(unverified)**.
- **Verified.**
  - 43 + 21 mutations on T749, 36 on T750, and 3 by the orchestrator were caught, on full copies with passing baselines and caps. The first 43 and the first 20 of the 21 ran before later edits and were not repeated.
  - All 33 `v*.md` pass on parser 3.0.0 and the locked 4.2.0.
  - T750 reports that the jobs' commands ran in the pinned image, against a `file://` origin, so no credential path ran.
- **Not verified.** No real job has run any of this: `run-allowlisted.py`, the removal, the fetches under `--keep`, the `timeout`, and clone on `release`. If one breaks, the release stops and fails closed. The deployed runner's flag `FF_GIT_URLS_WITHOUT_TOKENS` is unknown.
- **For the next register:** the closures above; SEC-T751-01 to -09 with the three fixed; TD-T746-01; SEC-T748-03, -04, -05, -06, -07, -08, -09, -12; A-19 if the tag is gone. Checklist: the old item that a new CI/CD variable needs the `unset` line retires, and the first tag pipeline watches the new lines (`CONTRIBUTING.md` lists them).
- **Open for the user.** A second gate probe, the route of SEC-T735-06 and -07, A-19, a dedicated runner.
- **Token use (the harness's count, which includes context).** T749 about 205k against 120k + 40k; T750 about 178k against 120k; T751 about 232k against 120k.
