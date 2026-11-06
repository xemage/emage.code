# Security review: T749 and T750, the rest of batch S

**Based on:** `docs/plans/plan-143-batch-s-rest.md`, `docs/artifacts/security-review-t745-batch-s-v1.md` § 4, `docs/artifacts/security-review-t748-batch-t-v1.md` § 3 and § 10, `s-gate.diff`, `s-pipe.diff`, `s-tests.diff` (from `a3d42112`), and the tree at `0e7a24ac` by range: `scripts/verify-release-docs.py`, `scripts/check-version-consistency.py`, `.gitlab-ci.yml`, `docs/releases/_template.md`. `scripts/run-allowlisted.py` was read in full in the diff.

- **Reviewer:** security-engineer, read-only, no shell. **Gate:** security. **Date:** 2026-11-06.
- **Method:** hand traces only; I ran no code. "Traced" means I followed the shape through the script. CommonMark tag rules and `markdown_it` internals come from knowledge and earlier reviews; I did not read the 4.2.0 source.
- **Runner evidence:** GitLab Runner v19.5.2 `shells/abstract.go`, `shells/bash.go`, `common/build.go` and `helpers/featureflags/flags.go`, through a summarising fetch.

## Verdict: CONDITIONAL_PASS

- 0 CRITICAL, 0 HIGH, 0 MEDIUM, 9 LOW. Nothing blocks the merge.
- No Immutable Security Constraint is breached, and no required control is removed or weakened.
- **Conditions:**
  - SEC-T751-01 to -09 go into the next register as tracked debt.
  - The first tag pipeline watches the unproved lines (Q3, Q4). A probe needs the user's approval.
- **Why LOW:** as in the earlier reviews, each route needs a commit that survives merge request review, a maintainer's variable, or a shape that fails closed. The GitLab-side rendering is unproved (SEC-T751-08).

### Regressions against `d989ecb7`

**No check got weaker on the gate's route.** Every gate change adds refusals, apart from the narrow `DEPENDENCY_TREES` skip the plan asked for and the output format of `evaluate`. Dropping `unset` is not a real loss (Q4).

Three LOWs come from this plan and are the ones your rule would still fix:

| Id | What this plan introduced | Size |
|---|---|---|
| SEC-T751-02 | New surface: one file that every gate command passes through, with no test under CI-like variables | One test, one contract sentence |
| SEC-T751-03 | New wording: the template overclaims, and the refusal message steers an author to a code span | Wording, plus the test that pins the message |
| SEC-T751-04 | New wording: the reason given in the `rm` comment is wrong, though the conclusion holds | One comment |

## Q1. Are the ids closed?

| Id | Status | What stays |
|---|---|---|
| SEC-T745-01 | **Closed as asked:** cap, pinned timeout, measurement in `--help` | `check_links` is outside the cap and has its own quadratic shape, fail closed: SEC-T751-06. 48 s is one machine and 41 shapes, and `--help` says so |
| SEC-T745-02 | **Closed.** Traced equal to the old pattern, and linear. The test keeps the old pattern as its reference | Nothing |
| SEC-T745-03 | **Closed on the gate's route:** the tag's own document and any named on a Cursor line | Comments stay allowed, by design. A document on a non-Cursor line is not read, as `--help` states. GFM table differential: SEC-T751-08 |
| SEC-T745-04 | **Closed as asked:** `apk` and the scripts are allowlisted, only the fetches keep the token, all pinned | Credential file: SEC-T751-01 |
| SEC-T745-05 | **Closed:** allowlist in place of the denylist, and the credential is removed | Shell and process residual (Q4). No check that the removal hit the right path: SEC-T751-05 |
| SEC-T745-06 | **Closed as asked:** the clause is in contract 6 | It names project level only: SEC-T751-05. "Its only CI/CD variable is WIKI_TOKEN" is **(unverified)** by me. `.gitlab-ci.yml:201` does not carry the caveat |
| SEC-T745-07 | **Closed:** `GIT_STRATEGY: clone` on `release`, pinned, including the mutations | Unproved until a tag runs it |
| SEC-T745-08 | **Closed as asked:** `str` with a codec, one enclosing function, and every other name load refused | A string route such as `importlib`, `__import__` or `sys.modules` is not seen. Crafted only. I did not read the earlier part of `_read_route_problems`, so `codecs.decode` is **(unverified)** |
| SEC-T745-09 | **Closed.** Your narrowing is right: the plan's `pyvenv.cfg` rule would have opened a hole. The tests cover a marker in `docs/wiki` and at the root | Another virtual environment name fails a local run, stated at `check-version-consistency.py:77-79`. A committed file under the exact paths silences only itself |
| SEC-T745-10 | **Closed.** `ascii()` at `:255`, with a test | Output is now `'README.md':3:`. No script under `scripts/` on `develop` reads that text beyond this script itself |
| SEC-T745-11 | **Closed.** The docstring matches `run_checks` | Nothing |
| TD-T739-01 rest | **Closed,** as SEC-T745-01 | As SEC-T745-01 |
| SEC-T741-17 | **Open by design:** runner tag | As before |

## Q2. Which routes still let a hidden or unfilled document pass?

### Hidden from a reader

| # | Shape | Status | Id |
|---|---|---|---|
| 1 | `## RELEASE VERDICT\n\n<!-- - Status: PASS -->\n`: renders empty, the raw line makes it non-empty | Traced | SEC-T748-06 |
| 2 | `## RELEASE VERDICT\n\n[x]: u "Status: PASS"\n`: a reference definition renders as nothing. Also a `&#8203;` paragraph and `### &#32;` | Traced | SEC-T748-06 |
| 3 | `- Version: 1\n\n&#x2800;\n---\n\n- Status: pending`: a heading a reader cannot see ends the scan. Also U+3164, U+FFA0, U+115F, U+1160, U+034F | Traced; rendering depends on the font **(unverified)** | SEC-T748-12 |
| 4 | `<!--\n## RELEASE VERDICT\n- Status: pending\n-->` above a filled section | Traced; accepted by ruling 3 | none |
| 5 | `` \| `x \| <div hidden> \| y` \| `` as a row of a real table: a code span here; GFM splits on the pipes first, so a live tag in a cell in GitLab | CommonMark side traced; GitLab side **suspected only** | SEC-T751-08 |
| 6 | A document named on a non-Cursor line, or a pointer newer than the tag: not read for HTML | Traced; stated in `--help` | none |
| 7 | Other GitLab-only syntax | Suspected only **(unverified)** | SEC-T716-03 |

Shape 5 stays inside its cell, because table parsing confines the tag (from knowledge). So it can hide that cell, not a later section.

### Unfilled and visible

| # | Shape | Status | Id |
|---|---|---|---|
| 8 | `- **Independent check**: PASS at abc123, by <tech-lead \| orchestrator \| top-level session>`: `\|` is no attribute name, so it is not HTML, and no marker holds it | Traced; passes on old too | SEC-T751-09 |
| 9 | `` - **Issued at commit**: `<sha>` ``: a code span, no marker. The refusal message suggests exactly this form | Traced | SEC-T751-03, -09 |
| 10 | `<1-3 sentences: ...>`, `<if applicable — ...>`, `<one line per entry: ...>`, `<steps to roll back ...; ...>` from the template: none is HTML, and these sections have no check | Traced; passes on old too | SEC-T751-09 |
| 11 | `~~~\n## RELEASE VERDICT\n- Status: pending\n~~~` above a filled section | Traced | SEC-T748-04 |
| 12 | `Text\n---\n\n- Status: pending`, or `# Next` | Traced; ruling 1 | SEC-T748-03 |
| 13 | `## Release Verdict`, `## RELEASE&nbsp;VERDICT`, `### Gate Verdicts` with a pending field | Traced | SEC-T748-05 |
| 14 | `> - Status: pending`, `1. Status: pending`, `+ Status: pending`, `Status: pending`, a table row, `- Status:\n  - pending`, `- Status: _pending_`, `PASS\|FAIL` | Traced | SEC-T748-06 |
| 15 | `<!-- ## Install ## Highlights -->` and `<!-- Latest release: v1.2.3 -->`: raw substrings | Traced | SEC-T748-09 |

**Your ruling on placeholders.** "The verdict sections are still checked" holds for most of the template's fields, not all of them:

| Placeholder | Parser reads it as | Gate result |
|---|---|---|
| `<count>`, `<ISO-8601>`, `<sha ...>`, `<any known issues ...>` | HTML | Refused |
| `<PASS/CONDITIONAL_PASS>`, `<PASS \| CONDITIONAL_PASS \| FAIL>` | Text | Caught by a marker |
| `<tech-lead \| orchestrator \| top-level session>` at `_template.md:88` | Text | **Passes** (shape 8) |

**No route round the rules found.**
- `document_refusal` runs before every other read of the tokens on both routes.
- A document within the limits always has tokens, so `nesting_limit_line(None)` cannot happen.
- The block limit is exact: the skip needs `state.level >= 20`, and only an opener at level 19 reaches it. `test_below_the_limit_nothing_is_skipped` holds this.
- The inline parser has its own limit, but links disable nesting and images parse separately, so inline depth stays near 2 (from knowledge; run shape 4 below).

## Q3. Is `rm -rf .git "${CI_PROJECT_DIR}.tmp"` safe?

**Safe for this job, and it removes what it claims on 19.5.2 by source reading.** Only a tag pipeline proves it.

- **What it removes.**
  - `Build.TmpProjectDir()` is `BuildDir + ".tmp"`, and `CI_PROJECT_DIR` is `FullProjectDir()`, the same directory by default.
  - `setupTemplateDir` writes `include.path` to the external config in every mode, so `.git/config` reaches it.
  - With `FF_GIT_URLS_WITHOUT_TOKENS` off, its default in `flags.go`, the insteadOf rewrite in that file carries the token. With the flag on, the file holds a helper and no token.
  - The removal also takes file-type variables and the seed file.
  - The implementer's reading holds, including the part it could not read: `credHelperCommand` reads `${CI_JOB_TOKEN}`.
- **Later stages.**
  - The job has no `after_script`, cache or artifacts.
  - `writeCleanupScript` uses `rm -f` and `rm -r -f`, and guards `chmod` with `IfDirectory`.
  - A cleanup failure only logs a warning: `removeFileBasedVariables` returns nothing.
  - So this can neither fail the job nor pass it wrongly.
- **Other jobs.**
  - The next `clone` removes and recreates everything.
  - A `fetch` job on the same volume finds no `.git` and starts fresh (from knowledge).
  - A parallel job uses another concurrency directory (from knowledge; runner configuration **(unverified)**).
- **Empty or odd `CI_PROJECT_DIR`.** The path always ends in `.tmp` and is quoted, so it can never be `/` or a parent.

| Value | Effect |
|---|---|
| Empty | `.tmp` in the working directory: harmless |
| `/` | `/.tmp` |
| Trailing slash | `.tmp` inside the project |
| Leading `-` | Busybox rejects the option and the job fails closed |

- **The real weakness.** A variable set at project level would point the removal at the wrong path, and the credential would stay with the job green: SEC-T751-05.
- **Is `.git` needed?** No. `test_nothing_in_the_docs_gate_starts_git` holds it, and I found no git call in either script.
- **Unverified:** that the deployed runner is 19.5.2, and the flag's value on it.

## Q4. Does the allowlist leak?

**Not through the filter. It is an environment filter, as its docstring says.**

- **`--keep`:** exact names by regex, usage errors tested, pinned to `CI_JOB_TOKEN` on the two fetches, and mutations cover a second name. No leak.
- **Value filter:** matches whole values of `CI_JOB_TOKEN` and `WIKI_TOKEN`, and the empty case is guarded. An encoded form, or another secret in a proxy URL, passes. `release` behaves the same way, and a proxy password has to pass. No finding.
- **`-I`:** ignores `PYTHON*`, the current directory, the script's directory and the user's site directory. It applies **only to the wrapper**. The children have no `-I`: SEC-T751-07.
- **`os.execvpe`:** searches the `PATH` of the filtered environment.
  - A `PATH` holding the token is dropped, the search falls to `/bin:/usr/bin`, `python3` in `/usr/local/bin` is not found, and the result is 127, which fails closed.
  - Error text carries the command name only.
  - Nothing is buffered before the exec, and the exit code carries through.
- **What the job's shell still holds:** every variable, stated in the comment and docstring.
  - `/proc/$PPID/environ` holds only the shell's starting environment.
  - `/proc/$PPID/mem` needs attach rights, which depend on Yama and capabilities **(unverified)**.
  - Whether the executor passes variables into the container's own environment, so `/proc/1/environ` would hold them, is **(unverified)**. See run shape 6.
- **Dropping `unset` is not a real regression.** As I recall the runner's bash form, the script reaches the shell as one `eval` string holding the exports **(from knowledge, unverified)**. If so, the values stayed in the shell's memory under `unset` too. On that basis, the allowlist plus the removal is stronger.
- **Fetches under the allowlist:** `GIT_CONFIG_GLOBAL` is dropped, and that is fine. The `.git/config` include exists in both modes and the token comes from the kept variable. The helper test covers this form. Only a tag pipeline proves the real fetch.
- **The drift gate's credential file:** **SEC-T751-01, LOW, not a regression.**
  - It was readable by everything at `d989ecb7`, with a full environment too.
  - `apk`'s packages are signed upstream, and the scripts are the same tree as the tag.
  - A grep of the two scripts on `develop` finds no fetch, so they appear not to need it. `git` ignores a missing include.
  - One pinned line after the fetches would remove it from the scripts' reach. `apk` runs first and keeps it.

## Q5. Does the pin still guard all of this?

**The commands, yes. The code behind them, no.**

- **Guarded exactly:**
  - each gate command, the removal line, `timeout` and `GIT_STRATEGY` on all three jobs;
  - the key sets, so `hooks`, `after_script` and `extends` are refused on these jobs;
  - `default` and top-level keys, and `CI_` variables in job `variables`.
- **Changes that stay green (traced; mutation A in run shape 1 confirms the first):**

| # | Change | Why every test stays green | Id |
|---|---|---|---|
| a | `if "CI_COMMIT_TAG" in os.environ: sys.exit(0)` in `scripts/run-allowlisted.py`, or `if command[-3:-2] == ["--tag"]: return 0` | `test_run_allowlisted` runs with a small fixed environment and never runs a gate command through it. **Skips both gates with a one-file edit** | SEC-T751-02 |
| b | The same condition inside `verify-release-docs.py` or a drift script | Same class, existed before this plan | Stays with review |
| c | A committed `scripts/markdown_it/__init__.py` | `python3 scripts/...` has `scripts/` on its path | SEC-T751-07 |
| d | A committed root `pip/__main__.py` | `python3 -m pip` has the current directory on its path | SEC-T751-07 |
| e | A project or group variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` | No test reads CI/CD variables | SEC-T751-05 |

A hash pin of the wrapper would add no real control, because the diff is already visible in the merge request, so I do not propose one. What helps is a behavioural test under CI-like variables, which catches a careless edit, and the contract naming this file as review-only.

## Q6. Can the rules fail a real release wrongly, or weaken a check?

**No weakening found, compared with `d989ecb7`.** Wrong failures are possible but are caught before the tag.

- **HTML rule.** Prose such as `Array<string>`, `<your-project>`, `<br>` or `<kbd>` is now refused, and `<details>` can no longer be used.
  - That is the plan's decision.
  - The message names the line.
  - `test_no_release_document_is_refused_and_the_template_is` runs in `unit-tests` on every merge request, so a new `v*.md` fails there rather than at the tag.
  - The same test catches a parser lock bump that would newly refuse an old document.
- **Cap.** 131072 against 66,745 at the largest. The refusal is clear, and changing it is a two-file edit.
- **Nesting.** The deepest real document reaches 5 of 20. Being one level strict costs nothing real.
- **Timeout.** 10 minutes against 6 s measured for v9.0.0.
- **Direct-call behaviour.** `MarkdownIt("commonmark", {"maxNesting": 20})` equals the preset, and a test holds it. `has_cursor_migration_item` is a strict superset of the old refusals.
- **Skipped paths.** A stale claim in a tracked `venv/` or `.venv/` file is no longer read. This is negligible, and the plan asked for it.

## Q7. What do the batch T ids still leave on the gate's route?

| Id | On the gate's route | Stays |
|---|---|---|
| SEC-T748-02 | **Closed.** `<span hidden>` is refused; format characters were closed earlier | Non-`Cf` characters move to -12. The direct-call guard stays, as the plan says |
| SEC-T748-04 | `<div>` and `<div hidden>` wrappers are refused | `~~~` fence above the section (displayed as code), a multi-line reference title (hidden), and comments under ruling 3 |
| SEC-T748-12 | The wrapper part is closed | **U+2800, U+3164, U+FFA0, U+115F, U+1160, U+034F and variation selectors stay**: shape 3 of Q2. Old caught them |
| SEC-T748-13 | **Closed.** `## <span hidden>RELEASE VERDICT</span>` is refused first | `section_heading_indexes` alone still counts it, on a direct call only. Its pairing with -05 stays under -05 |

## Q8. Do the words state this exactly?

**Mostly yes.** `--help`'s five cases and their order, the nesting paragraph, the "measurement, not a bound" sentence, the `run-allowlisted.py` docstring and the `.gitlab-ci.yml` allowlist comments all match the code.

Overclaims:
1. **`_template.md:3`:** "it reads a placeholder left outside code as HTML" is false for at least 6 of the template's own placeholders (Q2). The docstring of `test_no_release_document_is_refused_and_the_template_is` says the same. SEC-T751-03.
2. **The refusal message and `CONTRIBUTING.md`:** "put text such as a placeholder in a code span" tells an author in a hurry how to pass with an unfilled `<sha>`. SEC-T751-03.
3. **`.gitlab-ci.yml:210`:** "Later runner stages recreate that directory, so removing it is safe". The directory is recreated only by `SourceEnv` and by a file variable under `writeExports`. The real reason is that the later stages need nothing in it. SEC-T751-04.
4. **`tests/functional/test_ci_hash_pins.py:30-33`:** names project level only. SEC-T751-05.
5. **`CONTRIBUTING.md` rehearsal:** it checks that the runner's later stages survived the removal, not that the credential is gone, and a job log cannot show the second. SEC-T751-05.
6. **Older and still open, under SEC-T748-08:** "a hidden 'pending' still fails" at `verify-release-docs.py:299-300`, and "Pinned on 3.0.0 and 4.2.0" under SEC-T748-07.

## Findings (owner devops-engineer, proposed; next sprint; tracked as LOW debt)

Lines are at `0e7a24ac`.

| Id | Grade | OWASP | Location | Description | Proposed fix | Regression from this plan? |
|---|---|---|---|---|---|---|
| SEC-T751-01 | SECURITY:LOW | A05 | `.gitlab-ci.yml:231-237` | The drift gate's credential file stays readable by `apk`, by `git` and by both scripts, though the scripts appear not to need it | After the second fetch, add `- rm -rf "${CI_PROJECT_DIR}.tmp"` and pin it. Prove with run shape 5. `apk` keeps access, because it runs first | No; better than `d989ecb7` |
| SEC-T751-02 | SECURITY:LOW | A08 | `scripts/run-allowlisted.py:72-81`; `tests/functional/test_run_allowlisted.py`; contract 6 | Every gate command runs through a file whose tests never use CI-like variables or a gate command, so a conditional exit stays green | Run `sh -c 'exit 7'` and `false` through it with `CI=true`, `GITLAB_CI=true`, `CI_COMMIT_TAG=v1.2.3` and a token set. Assert the code passes through. Name the file in contract 6 as review-only. This catches a careless edit, not a crafted one | **Yes: new surface.** Not a weaker check, because scripts could already hold such a condition |
| SEC-T751-03 | SECURITY:LOW | A08 | `docs/releases/_template.md:3`; `verify-release-docs.py:706-708`; `CONTRIBUTING.md:223-224` | Overclaim on placeholders, and a message that steers an unfilled placeholder into a code span, where it passes | Template: "the gate refuses what the parser reads as HTML, which is many placeholders but not all, and it does not read the others". Message: "replace a placeholder with its value; put literal text in a code span" | **Yes: wording.** Net behaviour improved, since a bare `<sha>` is now refused |
| SEC-T751-04 | SECURITY:LOW | A05 | `.gitlab-ci.yml:210` | The stated reason for safety is wrong | "The later stages need nothing in it: cleanup uses `rm -f`, and a cleanup failure only warns" | **Yes: wording** |
| SEC-T751-05 | SECURITY:LOW | A05 | `.gitlab-ci.yml:211`; `tests/functional/test_ci_hash_pins.py:30-33`; `CONTRIBUTING.md` rehearsal | Group and instance variables also outrank job variables (from memory of the docs' precedence table), and predefined variables rank lowest, so `CI_PROJECT_DIR` set at project level silently misses the directory. Nothing shows the credential is gone | Widen the clause to project, group and instance level, and to `CI_PROJECT_DIR`. Add a rehearsal item through run shape 6 | No |
| SEC-T751-06 | SECURITY:LOW | A04 | `verify-release-docs.py:308`, `:1002-1003` | `LINK_RE` is quadratic on `[` repeated, is outside the cap, and runs even on a refused document, so a large one holds the job until its timeout. Fails closed. Residual of SEC-T745-01 | Do not run `check_links` on a refused document, and use `\[[^\[\]]+\]` after checking that real documents give the same links. Run shape 2 tells whether 48 s is still the worst | No |
| SEC-T751-07 | SECURITY:LOW | A08 | `.gitlab-ci.yml:213`, `:215`, `:235`, `:237`; `verify-release-docs.py:563` | The children run without `-I`, so a committed `scripts/markdown_it/` or root `pip/` shadows the real module with all tests green | `python3 -I` on the children and `[sys.executable, "-I", ...]` for the version check, updating the pins. Check first that no script imports a sibling | No |
| SEC-T751-08 | SECURITY:LOW | A08 | `verify-release-docs.py:371`, `:852-862` | The commonmark preset has no tables: pipes inside a code span can yield a live tag in a GFM table. GitLab side **suspected only**. Register with SEC-T716-03 | First run shape 7. If confirmed, also read the document with the table rule enabled for the HTML check, or refuse a `<` in a code span on a line that starts with `\|` | No |
| SEC-T751-09 | SECURITY:LOW | A08 | `verify-release-docs.py:141-147`; `_template.md:7`, `:47`, `:51`, `:88`, `:94` | Template placeholders that are not HTML and hold no marker pass, one of them inside a verdict section | Add `<tech-lead` to the markers. Optionally, fail on each exact template placeholder anywhere outside code | No |

## Recommendations, in order

1. Fix SEC-T751-02, -03 and -04 before the merge, or accept them explicitly. All three are small.
2. Run the shapes below, especially 1, 2 and 7.
3. Track the rest. SEC-T751-01 is one line if you want it at the same time.

## Shapes to run

Use the plan's limits: a throwaway copy, a timeout and `RLIMIT_AS`.

1. **Mutation A on a copy:** add `if "CI_COMMIT_TAG" in os.environ: sys.exit(0)` at the top of `main` in the wrapper, then run `test_run_allowlisted` and `test_ci_hash_pins`. I expect both green, which confirms SEC-T751-02.
2. **Time, whole gate:**
   - `"[" * 131072` as the tag's document;
   - `"[a](" * 32768`;
   - 1 MiB of `[`, which should be refused and then held by `check_links`.

   Stop at 120 s, and state whether any of the first two exceeds 48 s.
3. **Expected 0 errors on `verdict_placeholder_problems`, and `document_refusal` None:**
   - `## RELEASE VERDICT\n\n<!-- - Status: PASS -->\n`
   - `## RELEASE VERDICT\n\n[x]: u "Status: PASS"\n`
   - `## RELEASE VERDICT\n\n- Version: 1\n\n&#x2800;\n---\n\n- Status: pending\n`
   - `## RELEASE VERDICT\n\n- **Independent check**: PASS at abc123, by <tech-lead | orchestrator | top-level session>\n`
   - `` ## RELEASE VERDICT\n\n- **Issued at commit**: `<sha>`\n ``
   - `~~~\n## RELEASE VERDICT\n- Status: pending\n~~~\n\n## RELEASE VERDICT\n\n- Status: PASS\n`
   - Each placeholder on its own line, expected **not** HTML:
     - `<1-3 sentences: what this release contains>`
     - `<if applicable — steps to upgrade from the previous version>`
     - `<one line per entry: description, task ID, artifact version references>`
     - `<steps to roll back if critical issues are discovered after the release; state whether they were tested>`
     - `<PASS/CONDITIONAL_PASS>`
     - `<PASS | CONDITIONAL_PASS | FAIL>`
   - Expected HTML: `<count>`, `<ISO-8601>`, `<any known issues shipping with this release>`, `<sha the release files were at when the verdict was issued>`.
4. **Inline depth on 4.2.0:** `"[" * 25 + "a" + "](u)" * 25 + " <b>x</b>"` and `"**" * 30 + "<b>x</b>" + "**" * 30`. Expected: both refused for HTML, with the largest child `level` under 20.
5. **Drift fix proof:** in a local clone whose `.git/config` has `include.path` to a sibling `.tmp` file, delete that directory, then run `git rev-parse origin/main` and both drift scripts under the wrapper. Expected: both pass.
6. **Probe only, needs the user's approval.** In a real job, print booleans and never values:
   - whether `CI_JOB_TOKEN=` is in `/proc/1/environ` and in `/proc/$PPID/environ`;
   - whether `/proc/$PPID/mem` opens;
   - whether `${CI_PROJECT_DIR}.tmp` exists after the removal.
7. **GitLab's read-only render API:** `POST /api/v4/markdown` with `{"text": ..., "gfm": true, "project": "em-age/emage.code"}`. It creates nothing. This answers several open **(unverified)** items, though the Release description may differ. Text to send:
   - `` | a | b | c |\n|---|---|---|\n| `x | <div hidden> | y` | ``, and the same with `<style>h3{display:none}</style>`;
   - `<div hidden>x</div>`;
   - `## <span hidden>x</span>`;
   - `&#x2800;\n---`.

## Not verified

- No code run. These are the implementer's report: the 43 + 21 + 36 mutations, all 33 documents on both parser versions, and the 48.43 s measurement. GitLab's lint and the 3 jobs on the tag route are your report.
- `markdown-it-py` 4.2.0 source, the deployed runner's version and flag, and the Docker executor's container environment.
- GitLab's rendering and sanitizer, the Release description path, and variable precedence for these names.
- `.git/config` and the external config as a real job leaves them. All pipeline lines are unproved until a tag pipeline runs them, and a failure there stops the release, which fails closed.
- `check-*.py` was grepped on `develop`, not at `0e7a24ac`. The plan's diffs do not change those two scripts.
- I read `test_ci_hash_pins.py` only through the diff, so `ci_pin_problems` itself rests on the T745 review and your lint.
- `tests/golden/` was not opened, and no `.env*` or credential file was read. No dependency changed, so no audit ran.

## Gate Verdict: Security

**Gate:** security
**Executor:** security-engineer
**Date:** 2026-11-06
**Target:** T749 and T750 (plan-143) at `0e7a24ac`

### Verdict: CONDITIONAL_PASS

### Findings

SEC-T751-01 to -09, as above, each severity `low`, category `security`.

### Conditions

- [ ] SEC-T751-01 to -09 recorded in the next register. Owner: devops-engineer (proposed). Due: next sprint.
- [ ] The first tag pipeline confirms the removal, the wrapper and the fetches, using `CONTRIBUTING.md`'s rehearsal list.

### Summary

The 12 ids are closed as asked, with the residuals named in Q1. No check got weaker. The plan adds one new surface and two wording errors, all LOW.

## VERDICT: CONDITIONAL_PASS

### Findings Summary

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 9 | 0 | 9 |

The 12 earlier ids in Q1 are resolved and are not counted in these 9.

### Justification

The gate's rules and the job's pins hold by trace. The remaining routes need a commit that survives review, a maintainer's variable, or a shape that fails closed. SEC-T751-08 is suspected only.

### Conditions

- SEC-T751-01 to -09: owner=@devops-engineer (proposed), remediation=as in the findings table, deadline=next sprint. By the user's policy, LOW is tracked. -02, -03 and -04 are the ones this plan introduced.

### Blockers

None for the verdict.

- `technical`, `minor`: `grep_content` errors on the worktree and scratchpad paths. I read those by range and used the tool only on `develop`.

### OWASP Coverage

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (nothing in the diff) | 0 |
| A02: Cryptographic Failures | Yes (credential handling is under A05) | 0 |
| A03: Injection | Yes (argv is passed through, the path is quoted, tokens are never rendered) | 0 |
| A04: Insecure Design | Yes | 1 |
| A05: Security Misconfiguration | Yes | 3 |
| A06: Vulnerable Components | No (no dependency changed; no audit ran) | 0 |
| A07: Auth Failures | Yes (nothing in the diff) | 0 |
| A08: Data Integrity Failures | Yes | 5 |
| A09: Logging & Monitoring | Yes (messages hold paths and line numbers only; `ascii()` added) | 0 |
| A10: SSRF | Yes (no URL handling in the diff) | 0 |

## Task completion

- **Artifact:** this report, as text, for you to commit as `docs/artifacts/security-review-t751-batch-s-rest-v1.md`. Nothing was written or modified.
- **Acceptance:** all eight questions are answered with evidence, each finding has id, grade, location, description, fix and regression status, and each route is marked traced or suspected.
- **Follow-up for the next register:**
  - Close the 12 ids in Q1.
  - Mark SEC-T748-02 and -13 closed on the gate's route.
  - Narrow SEC-T748-04 and -12 as in Q7.
  - Add SEC-T751-01 to -09.

Key paths:
- `/home/emage/Code/emage/worktrees/plan-143/scripts/run-allowlisted.py`
- `/home/emage/Code/emage/worktrees/plan-143/scripts/verify-release-docs.py`
- `/home/emage/Code/emage/worktrees/plan-143/.gitlab-ci.yml`
- `/home/emage/Code/emage/worktrees/plan-143/docs/releases/_template.md`
- `/home/emage/Code/emage/worktrees/plan-143/tests/functional/test_run_allowlisted.py`
- `/home/emage/Code/emage/worktrees/plan-143/tests/functional/test_ci_hash_pins.py`

## Orchestrator's record after this report

Everything above is the reviewer's report on `0e7a24ac`. The reviewer ran no code. The orchestrator then ran its list.

**Shapes** (parser 4.2.0 unless stated).

| Reviewer's item | Result |
|---|---|
| 1, Mutation A | Survived on `0e7a24ac`, which confirms SEC-T751-02. After `6c58244b` it is caught, and so are two variants (an exit on `--tag`, an exit on `CI=true`), each on a full copy with a passing baseline |
| 2, Time | `"[" * 131072`, `"[a](" * 32768` and 1 MiB of `[`: each exit 1 in about 0.1 s. None exceeds 48 s. **SEC-T751-06's hold did not reproduce on these shapes;** the orchestrator did not trace why, so it stays tracked. T749's own `[` shapes took 2.63 s |
| 3, Routes | All six listed shapes: no refusal, 0 problems, as the reviewer traced. The placeholders read as the reviewer's table says |
| 4, Inline depth | Both refused for HTML. Largest child level: 1 for the links, **30 for the emphasis**, where the reviewer expected under 20. The HTML was still seen, so no route follows |
| 5, Drift fix | Not run: SEC-T751-01 stays tracked |
| 6, Probe | Not run: it needs the user's approval |

**Item 7, GitLab's read-only render API,** `POST /api/v4/markdown` with `gfm: true` and this project, 2026-11-06. This is the Markdown API, and whether a Release description renders the same way stays **(unverified)**.

| Text | Rendered |
|---|---|
| `<div hidden>x</div>` | `<div>x</div>`: `hidden` stripped |
| `## <span hidden>x</span>` | `<span>x</span>` in the heading: `hidden` stripped |
| `<style>h3{display:none}</style>` above `### h` | The tag is removed and its text is displayed; the heading stays |
| `` | `x | <div hidden> | y` | `` in a table | Cells `` `x ``, `<div></div>` and `` y` ``: GFM splits first, as the reviewer suspected, and `hidden` is stripped |
| `` | `x | <style>...</style> | y` | `` in a table | The middle cell holds the text, no tag |
| `&#x2800;\n---` | An `h2` holding U+2800: a heading with no visible text |

So on this API the sanitizer strips what the hidden-HTML findings were about (SEC-T745-03, SEC-T748-04, SEC-T748-13, SEC-T751-08's effect), and SEC-T748-12's character does render as a blank heading.

**Fixes after this report, in `6c58244b`, not re-read by the reviewer:** SEC-T751-02 (a test and one contract sentence), SEC-T751-03 (the refusal message, `_template.md`, `CONTRIBUTING.md`), SEC-T751-04 (one comment). No gate logic changed: only the message text. The reviewer's other six stay tracked.
