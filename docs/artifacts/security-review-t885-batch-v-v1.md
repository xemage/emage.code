# Security Review: T885 — plan-184 batch V (release-document gate and tag jobs)

**Based on:** `docs/plans/plan-184-batch-v-release-gate.md`; `docs/tasks/task-T885.md`; the fix diff `git diff 02f20453 c4b53aba` on `agent/devops-engineer/T883` (T883 a63d4f76, T884 cherry-picked from 74a1a54b; MR !712, draft); the orchestrator's run evidence at c4b53aba (342 tests OK, gates exit 0, root drift `[]`, CI lint valid); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`. Each id's "what was needed" comes from plan-184's wording for it. The original artifacts were not re-read for this review: `security-review-t748-batch-t-v1.md`, `security-review-t751-batch-s-rest-v1.md`, `security-review-t773-pi-removal-v1.md`, `security-review-t811-release-gate-runner-v1.md`, `tech-lead-release-v11-v1.md`, `security-review-t768-ca-control-v1.md`.
**Reviewer:** security-engineer (read-only). **Date:** 2026-11-20.
**User's words (verbatim):** "V go"; plan approval: "Approve (Recommended)".

## Summary
- **Risk Level:** LOW
- **Findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 4 new LOW (plus the LOW residual of SEC-T751-08)
- **Status:** PASS

## Per-id status

| Id | Task | Status | Basis |
|----|------|--------|-------|
| SEC-T748-03 | T883 | fixed | `_heading_problems` reports a section whose end heading's markup is not `##` (a setext heading or `# `). Tests cover `Text\n---`, `Text\n===` and `# Next`; `## Next` stays allowed and `###` does not end the section. |
| SEC-T748-04 (rest) | T883 | fixed | `stray_heading_lines` refuses the exact heading line at column 0 outside a heading, a closed ``` fence or an HTML block (so a `~~~` fence or an unclosed fence is caught). The multi-line reference title gives a real second heading on the locked parser, which is pinned by a test. Indented copies inside a `~~~` fence are not matched; the wrapper case stays documented, as planned. |
| SEC-T748-05 | T883 | fixed | `look_alike_heading_lines`: any heading at any level or depth whose folded text (format characters, fillers, white space, case) equals the name but is not the real form is a problem. Homoglyphs are not folded: see SEC-T885-02. |
| SEC-T748-06 | T883 | fixed | Field markers now include `+`, `1.`, `1)` and `>` blockquote prefixes. The value is read with entities resolved and edge characters stripped, and an empty field takes its sub-items as its value. A blank line or a non-list line under an empty field gives "field has no value", which fails closed. |
| SEC-T748-07 | T883 | fixed | The docstring now says "Tested on the locked version". A closing fence line must end with the opening markup, otherwise the fence is read, which fails closed. |
| SEC-T748-08 | T883 | fixed | The help text and docstring were corrected ("six cases", "fails closed for RELEASE VERDICT only", "table rows included"), and the help test asserts the new phrases and the absence of the old ones. |
| SEC-T748-09 | T883 | fixed | `## Install` and `## Highlights` are found through `section_heading_indexes`; comment, code, `###` and blockquote forms are refused by tests. |
| SEC-T748-12 | T883 | fixed | `is_visible_char` is an allowlist (`isalnum` minus `INVISIBLE_LETTERS`). Headings made only of punctuation, symbols or emoji now count as empty, so the section runs on, which fails closed. |
| SEC-T751-06 | T883 | fixed | A refused document is not link-checked (`check_release_brief` returns False). `LINK_RE` text is `[^\[\]]+`, so a long run of `[` takes linear time. The tail is still quadratic: see SEC-T885-01. |
| SEC-T751-08 | T883 | **partly fixed** | The narrow rule (one code span holding both `\|` and `<` in a paragraph that may be a table) leaves a bypass; see "Ruling on SEC-T751-08" below. The residual is LOW and stays open. |
| SEC-T751-09 | T883 | fixed | `<tech-lead` was added to `PLACEHOLDER_MARKERS`, with a test. The optional part (exact `_template.md` placeholders outside code) was not done; record it as not taken, not as open. |
| SEC-T773-01 | T883 | fixed | The UTF-8 test skips at most one missing pointer, and only the next major, minor or patch release after the newest document. 11 negative cases are tested. |
| SEC-T751-01 | T884 | fixed (runtime unproven) | `rm -rf "${CI_PROJECT_DIR}.tmp"` runs right after the last fetch. Its position and exact form are pinned and mutation-tested. A synthetic runner-layout test shows local git still works. |
| SEC-T751-05 | T884 | fixed (control on the user side) | The precedence clause now names project, group and instance level and `CI_PROJECT_DIR`. The rehearsal item in `CONTRIBUTING.md` asks the user to check the three settings pages. No test can read those settings, and the text says so. |
| SEC-T751-07 | T884 | fixed | Every Python child of the two gates runs `python3 -I` (`python_child_problems`; 4 children, each mutated), and the version check runs as `[sys.executable, "-I", str(script)]`. An AST test shows no gate script imports a sibling module. The token-holding `release` job is outside this id's scope: see SEC-T885-03. |
| SEC-T811-03 | T884 | fixed | `untagged_route_problems` refuses `trigger` and `inherit` on every job, hidden jobs and tag jobs included. Outside the tag jobs, `tags` must be a non-empty list of literal strings. All 8 mutation shapes are refused. See "Bypass shapes" below. |
| TL-T819-05 | T884 | fixed | The comment now reflects a reading of the GitLab Runner v19.5.3 source (shells/abstract.go, shells/bash.go, common/build.go): the credential lives in `$CI_PROJECT_DIR.tmp/.gitlab-runner.ext.conf` (or a credential helper when FF_GIT_URLS_WITHOUT_TOKENS is on). Cleanup uses `rm -f` and a best-effort `git credential reject`. The comment marks this as source reading. |
| SEC-T768-04 | T884 | fixed (runtime unproven) | The drift gate runs the four store checks of `ca-chain-check-python` (shipped and live store, by chain and by SPKI) plus `--ca-release`, all before the fetches. The release-docs gate runs `--ca-release` before pip, and `release` runs it before publishing. No image digest or runner tag changed. |

## Ruling on SEC-T751-08 (question 1)

The narrow rule does **not** close the hazard. GFM splits a table cell at every unescaped `|`, inside code spans too (GFM spec § tables: a pipe in a cell, code spans included, must be escaped). The rule tests code spans as the CommonMark preset sees them, and a bypass needs no single span to hold both characters:

```
| `a|` `<b>` |
|---|
```

The CommonMark parse sees two spans, `a|` and `<b>`, so the rule passes the line. GitLab splits the cell after `` `a ``. The second cell, `` ` `<b>` ``, then pairs its first two backticks into the span `" "`, which leaves `<b>` as live inline HTML and a stray backtick. The SEC-T745-03 HTML rule never sees that `<b>`.

**What closes it without failing a published document:** take the plan's alternative and run the existing HTML refusal (`live_html_line`) a second time on a token stream parsed with the GFM table rule enabled (`MarkdownIt("commonmark", ...).enable("table")`). markdown-it-py's table rule splits cells at unescaped pipes, including inside backticks, and parses each cell inline on its own, so it shows the `<b>` that GitLab would produce. Refuse the document if that second parse yields any `html_inline`/`html_block` other than comments.
- `v8.0.0.md:104` (`<dir>` in a code span with no `|`) stays a code span after the split, so it is not refused.
- A span written with an escaped `\|` is not split by either parser.
- T883 must show that all 19 documents named in its report give the same result. If any of them splits a span that holds `<`, that document holds live HTML under GitLab's own rendering, which is a real finding, not a false positive.

Until then the residual is LOW: only a committer can write the shape, the document is reviewed in a merge request, and GitLab's sanitiser limits the effect to hidden or styled text.

## Answers to the other questions

**Question 2 (tag jobs).**
- **Token exposure:** every new line except the drift gate's removal runs under `scripts/run-allowlisted.py` without `--keep`, so `CI_JOB_TOKEN` is not in its environment. A test asserts that none of these lines holds a `$` and that no `set -x` or xtrace appears in the pinned jobs. The removal line runs in the job shell, but `rm -rf` prints nothing, and the runner echoes the unexpanded text. I saw nothing that can print the token.
- **Removal after the fetches:** git ignores an `include.path` whose file is missing (git-config documentation; also shown by the new synthetic test). The two scripts after it read only the local repository. The runner's cleanup removes files with `rm -f`, and its credential reject is best-effort, so a missing directory does not fail cleanup. The same removal has already run in `release-docs-gate` since T750.
- **Other files in `.tmp`:** the directory also holds file-type variables and the runner's TLS CA file. Nothing after the removal uses the network or a file variable, so this is safe as written. Any future network line after the removal would break, and the pinned order makes such a change visible in review.
- **Break risk on the dedicated runner:** `cp -L /etc/ssl/cert.pem`, `cp -RL /etc/ssl/certs` and `apk add 'openssl~=3.5'` work only if the drift gate's image is the same image (same Alpine branch) as `ca-chain-check-python`. I did not verify this (assumption). `--ca-release` is awk-only per the comment, so `release-docs-gate` and `release` need no openssl. `mkdir /tmp/ca-shipped` fails if the directory exists, which cannot happen in a fresh job container. `allowed_images` is untouched.

**Question 3 (SEC-T811-03 bypass shapes).**
- YAML merge keys and anchors are resolved by `safe_load`, so a `trigger` or `inherit` they bring in is still seen.
- `!reference` tags and multi-document files (`spec:` headers) make `safe_load` raise, which fails closed.
- `extends` from a hidden job: the hidden job is walked, so `tags: []` or `inherit` there is refused.
- Variable tags: a `$` is refused. `parallel:matrix` cannot inject a tag without one.
- `inherit` is refused in every form (`inherit: variables: false` too). That is broader than the plan and fails closed.
- Remaining route: a file-level `include:` (local, project, remote, template or component) brings in jobs that no pin reads. I assume `file_level_problems` refuses `include`, but I did not check it in this review. The first item of the tag-pipeline list below covers it.

**Question 4 (regexes).**
- `LIST_ITEM_PREFIX`: each `>` group starts with `>`, so the prefix matches only one way. In `FIELD_RE` the label starts and ends with a non-blank, so the colon search backtracks across each run of spaces once: linear, as the tests at 30k-60k characters show.
- `QUOTE_PREFIX_RE` and `DELIMITER_CELL_RE` are linear. `folded` and `look_alike_heading_lines` are linear in the number of tokens.
- `table_code_html_line` scans each matching paragraph's lines once.
- `LINK_RE`'s **tail** is still quadratic: see SEC-T885-01.
- **Fail-open:** an alphanumeric character that renders as nothing and is not in `INVISIBLE_LETTERS` would end a section early (fail-open). I know of no such character beyond the listed fillers, so this is not raised. Homoglyph look-alikes are SEC-T885-02.

**Question 5 (tests).** No assertion was weakened. In detail:
- The blockquote heading moved from "allowed repeat" to look-alike error (stricter).
- `# Next` and setext ends moved from "no problem" to `weak_end`; the section still ends there (stricter).
- The misspelt `## Gate verdicts` moved from pass to look-alike error. This replaces plan-142's ruling 5, which SEC-T748-05 covers; record that in the T885 ledger row.
- The docs-gate no-kept-variable check grew from line `[1]` to all of `before_script[1:]` (stricter).
- The UTF-8 skip changed from `pointer_applies` to at most one next-release pointer, plus an explicit assertion (stricter).
- Removed docstring phrases are asserted absent because they overclaimed (SEC-T748-08).

## New findings

| Id | Severity | OWASP | Location | Description | Remediation |
|----|----------|-------|----------|-------------|-------------|
| SEC-T885-01 | SECURITY:LOW | A04 (resource use) | `scripts/verify-release-docs.py`, `LINK_RE` | The tail `\(([^)]+)\)` is unchanged and still quadratic. In a text of repeated `[a](` with no `)`, every start scans to the end of the text (`[^)]` crosses `[`, `(` and newlines): about 32k starts times about 65k characters at the 131072-character cap, so seconds per document (not measured). Only a committer can write it, and the job timeout bounds it. | Use `\[[^\[\]]+\]\(([^()\s]+)\)` (or `[^()\n]+`), so each attempt stops at the next `(`. Show that the real documents give the same links, as T883 did for the text part, and add a timing test for the `[a](` shape. |
| SEC-T885-02 | SECURITY:LOW | A04 | `folded`, `look_alike_heading_lines` | The look-alike check folds case, white space, format characters and fillers, but not confusables. `## RELEASE VЕRDICT` (Cyrillic Е) after the real section ends that section, and its body is not checked, while a reader sees a second "RELEASE VERDICT". This is the SEC-T748-05 hazard through homoglyphs. | In `folded`, also apply NFKC and map each non-ASCII letter to a wildcard, then compare against the name with any letter allowed at those positions (or use a UTS #39 skeleton). Add a Cyrillic or Greek test. |
| SEC-T885-03 | SECURITY:LOW | A08 | `.gitlab-ci.yml`, `release` job, `RELEASE_COMMAND` | `python3 scripts/publish-release.py` still runs without `-I` in the one job whose environment holds `CI_JOB_TOKEN`. A committed shadow module next to it (for example `scripts/json.py`) would run with the token. This is the SEC-T751-07 hazard, outside that id's gate-only scope. | Use `python3 -I scripts/publish-release.py ...`, after an AST check that the script imports no sibling module. Update `RELEASE_COMMAND`, extend `python_child_problems` to the `release` job, and add a mutation. |
| SEC-T885-04 | SECURITY:LOW | A05 | `.gitlab-ci.yml`, `main-develop-drift-gate` `before_script` | The new CA lines (`cp -L /etc/ssl/cert.pem`, `apk add 'openssl~=3.5'`) assume the drift gate's image matches `ca-chain-check-python`'s. No pin compares the two jobs' `image` or `apk` lines; the test compares only the `check-ca-chains.sh` lines. A later image change in one job could break the tag pipeline, or make the check prove a different store. | Add a pin that the drift gate's `image` equals `ca-chain-check-python`'s image, and that both install the same `openssl` constraint. |

## Recommendations (priority order)
1. Follow up SEC-T751-08 with the table-rule HTML check, and show that all 19 published documents keep their result. Until then, track the residual as LOW.
2. SEC-T885-03: `-I` for `publish-release.py`.
3. SEC-T885-01, -02, -04 as tracked LOW debt in register v27.

## What the first `v*` tag pipeline after this change must show
1. All three tag jobs ran on the dedicated runner (tag `release-gate`), and no other job ran on the tag. No child pipeline started, and no included file added jobs.
2. `release-docs-gate`: `--ca-release` passed before pip. pip ran as `python3 -I -m pip`. `verify-release-docs.py` ran as `python3 -I` and its version check reported no import error. The checkout lines name `CI_PROJECT_DIR` as GitLab sets it, with `GIT_STRATEGY` `clone`.
3. `main-develop-drift-gate`: the copy of the shipped store worked. `--ca-release` passed before and after `apk add`. `apk add 'openssl~=3.5' 'git~=2.54'` succeeded. `sha256sum -c` passed. The four store runs each ended in `RESULT: PASS`. Both fetches worked with `--keep CI_JOB_TOKEN`. `rm -rf "${CI_PROJECT_DIR}.tmp"` ran after the second fetch. Both scripts after it passed as `python3 -I`.
4. `release`: `--ca-release` passed before `publish-release.py`, and the Release was created.
5. No job log shows the job token (GitLab masks it as `[MASKED]`), and no line of these jobs echoes an expanded variable.
6. The runner's cleanup stage finished without a failure caused by the missing `.tmp` directory (a warning is acceptable; record it).
7. The user's check, recorded: no CI/CD variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` at project, group or instance level.

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 18 reviewed ids + 4 new | 17 | 5 (SEC-T751-08 residual, SEC-T885-01..04) |

### Justification
No CRITICAL, HIGH or MEDIUM finding, no breach of an Immutable Security Constraint, and no required control removed or weakened; every control in scope was tightened. 17 ids are fixed. SEC-T751-08 is partly fixed: its residual bypass is LOW (committer-only, reviewed document, GitLab's sanitiser still applies). The four new findings are LOW. PASS holds on the condition that the orchestrator tracks the five remaining LOWs as technical debt in register v27, as § Verdict Rules requires.

### Conditions
None (PASS). The five remaining LOWs go to register v27 as tracked debt.

### Blockers
None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 0 |
| A02: Cryptographic Failures | Yes (CA store, SEC-T768-04) | 0 |
| A03: Injection | Yes (HTML in the release document, SEC-T751-08) | 0 new (residual of SEC-T751-08) |
| A04: Insecure Design | Yes | 2 (SEC-T885-01, -02) |
| A05: Security Misconfiguration | Yes | 1 (SEC-T885-04) |
| A06: Vulnerable Components | Yes (no dependency changed; audit not re-run) | 0 |
| A07: Auth Failures | Yes (clone credential, job token) | 0 |
| A08: Data Integrity Failures | Yes | 1 (SEC-T885-03) |
| A09: Logging & Monitoring | Yes (no token in logs) | 0 |
| A10: SSRF | Yes (fetch targets fixed) | 0 |

## Addendum — orchestrator checks of the two assumptions (2026-11-20)

- **Question 2 / SEC-T885-04:** at `c4b53aba`, `main-develop-drift-gate`, `release-docs-gate`, `release` and `ca-chain-check-python` all name `python:3.12-alpine@sha256:e064671c…` (read from the parsed `.gitlab-ci.yml`). The CA lines therefore run on the same image today; SEC-T885-04 stays as the missing pin that keeps it so.
- **Question 3:** a top-level `include` is refused by `REFUSED_TOP_LEVEL` in `tests/functional/test_ci_hash_pins.py:154`, with tests at `:951` and `:1324`; the file has no `include` key.
