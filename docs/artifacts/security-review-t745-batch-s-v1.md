# Artifact: security-review-t745-batch-s-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only, with no shell. The orchestrator recorded this artifact from the reviewer's report. The ids `SEC-T745-NN` take their number from the review, not from a task.
- **Gate**: security. **Date**: 2026-11-06.
- **Target**: batch S (plan-140, T743 and T744) on `docs/plan-140-batch-s-release-gate` at `8a1334a759f281d6372b39796e286a08d092f719`, from the exported diff, all 1654 lines of it, and the worktree files.
- **An edit after the review, by the orchestrator:** `8ee1e2d3` adds `ANTHROPIC_API_KEY` to the `unset` line and to `GATE_CREDENTIALS`. It was not re-reviewed (TD-T745-01, section 4).
- **Based on**:
  - `docs/plans/plan-140-batch-s-release-gate.md`
  - `docs/artifacts/tracked-debt-register-v9.md` § 3, § 5
  - `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4, `docs/artifacts/security-review-t738-batch-n-two-v1.md` § 4, `docs/artifacts/security-review-t741-gate-pin-v1.md` § 4
- **Tools**: `grep_content` rejects a worktree path and reflects `develop`, so the reviewer used it as a pointer and read the worktree. No dependency changed, and no audit ran.
- **Orchestrator's checks**, run live, each with a timeout and a memory cap, because the reviewer traced by hand:
  - **The reviewer's inputs on the locked `markdown-it-py` 4.2.0**, with the full suite running on the same machine:

    | Input | Size | Time |
    |---|---:|---:|
    | Unclosed `<!-- ` repeated, one line | 16 KB | 0.77 s |
    | same | 32 KB | 2.68 s |
    | same | 65 KB | 9.78 s |
    | `<? ` repeated, one line | 65 KB | 7.99 s |
    | `<![CDATA[ ` repeated, one line | 65 KB | 5.69 s |
    | `<!a ` repeated, one line | 65 KB | 0.75 s |
    | 200 lines of 1 KB of unclosed `<!-- `, one paragraph | 200 KB | over 90 s (stopped) |
    | `FRONT_MATTER_OPENING_RE` on `coding:` repeated and 100000 blank lines | 165 KB | 12.75 s |

    So SEC-T745-01's shape is real and its estimate was high: "tens of seconds" for 64 KB was about 10 s. The hours for 1 MB were not run. The project's `build_timeout` is 3600 s, so the worst case is a job that stalls for an hour and fails closed.
  - **`<style>h3{display:none}</style>` after the anchor** gives True: SEC-T745-03 confirmed.
  - **The correction to T744's report:** `exit 0` added to `release.before_script`, on a throwaway copy, fails `test_the_bootstrap_is_the_exact_text_that_yaml_parses_to`. `ci_pin_problems` itself does not catch it.
  - **The real `.gitlab-ci.yml`** through GitLab's read-only lint at `8a1334a7`: valid, no warnings. A dry run on `v9.0.0` runs exactly the three pinned jobs, and on `develop` the other seven. The merged YAML shows `GIT_STRATEGY: clone` on both gates and the `unset` line first.
  - **Edits caught by the pin:** `exit 0` on the drift gate, `GIT_STRATEGY: fetch`, the strategy dropped, the `unset` line dropped or one name shorter, `release`'s script softened, `release`'s artifacts changed.
  - **Shapes on 4.2.0,** on T743's final code: inline or raw HTML before the anchor anywhere in the document gives False, in a lead, a heading, a link, a paragraph above, a list, a blockquote and the section title. A plain lead, a heading, a list lead, a comment, a code span, a fence holding a tag, an autolink, a comment title, and HTML after the anchor or the section give True.

## Verdict: CONDITIONAL_PASS

- 0 CRITICAL, 0 HIGH, 0 MEDIUM.
- No breach of an Immutable Security Constraint, and no required control removed or weakened.
- Nothing blocks the merge. The only condition is that the LOW findings be tracked as debt. Section 4 is that record; the next register takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 26 | 13 | 13 (tracked, section 4) |

The 26 are the 15 ids of batch S and 11 new ones. TD-T745-01 is the orchestrator's id, and it is not counted or graded here.

**Why LOW.** Each route needs a crafted commit that survives merge request review, and the timing effects fail closed.

## 1. The 15 ids

| Id | Ruling | Note |
|---|---|---|
| SEC-T739-02 | Closed | Both sides of the word and a tag in a link, through the flat token list |
| SEC-T739-03 | Closed by refusal | The widening to the whole document before the anchor is sound. After the anchor: SEC-T745-03 |
| SEC-T739-04 | Closed | A superset of GitLab's opening. Whether the Release description uses front matter stays **(unverified)** |
| SEC-T739-06 | Closed as asked | Residuals are stated: SEC-T745-04, -05 |
| SEC-T739-08 | Closed | Template, error text and both `CONTRIBUTING.md` lines |
| SEC-T739-09 | Closed | Sentence, label and fixtures |
| SEC-T738-02 | Closed | Refused on decoded text, the same as raw bytes for U+000D under strict UTF-8 |
| SEC-T738-06 | Closed | Escapes, and a byte-level guard test |
| TD-T739-01 | **Open in part** | The 65536 refusal is correct, but a line limit does not bound parse time: SEC-T745-01 |
| SEC-T741-06 | Closed | `.gitlab-ci.yml:67` stays, as the plan says |
| SEC-T741-07 | Closed | Clause and test |
| SEC-T741-08 | Closed | The AST walk meets the plan's list. Limits: SEC-T745-08 |
| SEC-T741-12 | Closed | Exact values |
| SEC-T741-16 | Closed on this project | It rests on a setting no test reads, as contract 6 says |
| SEC-T741-17 | **Open in part** | `GIT_STRATEGY: clone` is done and pinned. The runner tag is not, because it needs a runner, so the Docker socket route stays. See SEC-T745-07 |

## 2. Rulings

- **A crafted document that passes while a reader cannot see the anchor.** On a CommonMark render, the only route found is SEC-T745-03. Raw output comes only from `html_block` and `html_inline`, and both are walked. Reference definitions, images, entities, setext headings, paragraph continuation, breaks and HTML in link text all fail as routes (hand traces). GitLab-only syntax stays open under SEC-T716-03.
- **`COMMENTS_ONLY_RE`** is right, and has one parse for each part of the text, so no catastrophic backtracking. A very long comment costs Python's stack, and that fails closed. It refuses a comment that a browser ends earlier than the parser does, which matters on the 4.x regex (read at v4.0.0; 4.2.0 not read).
- **`FRONT_MATTER_OPENING_RE`** is sound and broad enough, and polynomial rather than exponential: SEC-T745-02.
- **The refusals** reach every parse. `long_line_number` is enough, because the parser splits lines on `\n` only.
- **`keep_cr`** has one caller, which returns on any CR. No bypass found.
- **The `unset` line** holds through `before_script` and `script`, and the job has no `after_script`. It does not stop code reading the clone credential, and the comment says so. The drift gate correctly keeps `CI_JOB_TOKEN`, because the runner's credential helper may read it from the environment.
- **`GIT_STRATEGY: clone`** should work with the drift gate's fetches (runner source, master). If not, the gate fails closed. The first real run is a tag pipeline, so a release candidate stays the right proof.
- **The pins.** `is not True` is right. An exact `release.script` costs a visible two-file edit, which is acceptable. Edits inside `release.before_script`'s Python string are not seen, and they do not skip a gate.
- **SEC-T741-06.** The offset claim is right. A committed non-UTF-8 `.md` outside the exclusions now blocks the release, which is what the id asks.
- **Test quality.** No weakening found in the flipped tests. `test_publish_release_job_token` now imports `test_ci_hash_pins`, so its PyYAML `skipTest` is dead code; without PyYAML the module errors, which fails closed.

## 3. OWASP coverage

| Category | Findings (open) |
|---|---|
| A04 Insecure Design | SEC-T745-01, -02 |
| A05 Security Misconfiguration | SEC-T745-04, -05, -06, -09 |
| A08 Data Integrity | SEC-T745-03, -07, -08 |
| A09 Logging & Monitoring | SEC-T745-10, -11 |
| A01, A02, A03, A06, A07, A10 | 0. A06: no dependency changed, no audit ran |

## 4. Findings tracked as LOW debt (owner devops-engineer, proposed; next sprint)

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T745-01 | `MAX_LINE_CHARS`, `document_refusal` | `html_inline` searches the rest of the paragraph with no memo, so unclosed `<!-- `, `<? ` and `<![CDATA[ ` are quadratic in the **paragraph**. Lines join, so the line limit does not bound it. Measured in the Metadata. | Pin a job `timeout` on the gate, add a total size cap, and state the bound in `--help`. A cap alone is not enough. |
| SEC-T745-02 | `FRONT_MATTER_OPENING_RE` | Polynomial: a first line of `coding:` repeats plus a long blank run retries for each occurrence. 12.75 s measured. | Replace the optional group with a `partition("\n")` check of the first line, then one test of the body. |
| SEC-T745-03 | `has_cursor_migration_item`; `--help` | `<style>h3{display:none}</style>` after the anchor gives True and hides it in a browser. GitLab's sanitizer should strip it **(unverified, from memory)**. | Any live HTML anywhere in the document fails, after checking the 33 documents; or refuse `style` and `script`; or reword the `--help` claim. |
| SEC-T745-04 | `main-develop-drift-gate` | `apk add` and the scripts see every credential, while `release` filters `apk`'s environment. | Unset all names except `CI_JOB_TOKEN`, filter `apk` as `release` does, and pin it. |
| SEC-T745-05 | `release-docs-gate`, the `unset` line | A denylist: a later project variable stays visible, as `ANTHROPIC_API_KEY` was (TD-T745-01). The credential's location varies by runner mode. | Run pip and the gate under an allowlisted environment, or also remove the credential if `.git` is unused by this job **(unverified)**. Reword the comment to "the clone credential". |
| SEC-T745-06 | Contract 6; `GIT_STRATEGY` | Project variables outrank job `variables` **(from memory)**, so a project-level `GIT_STRATEGY` beats the pin with every test green. The project has none today (orchestrator, by API). | One clause in contract 6, and no project variable of that name. |
| SEC-T745-07 | `release` | The job that publishes with the token stays on `fetch`. The runner cleans `.git/config` and hooks there on non-shell executors, so the risk is small. | Add `GIT_STRATEGY: clone` and pin it. |
| SEC-T745-08 | `_read_route_problems`; `test_the_parser_has_one_call_site` | `str(raw, "utf-8", "ignore")` inside `read_strict` passes the walk. A module-level `PARSER = MarkdownIt(...)` or an alias passes the second test. | Refuse `str` with more than one argument in `read_strict`, require exactly one enclosing function, and refuse any other `MarkdownIt` name load. |
| SEC-T745-09 | `find_markdown_files` | A non-UTF-8 `.md` in `ci/js/node_modules` or an in-tree virtual environment now fails a local run. No effect in CI. | Skip those directories, or list tracked files only. |
| SEC-T745-10 | `evaluate`, `check-version-consistency.py` | Drift lines print the path unescaped in a standalone run. | Use `ascii()` as `refusal_line` does. |
| SEC-T745-11 | `document_refusal` docstring | "before reading it for anything else" is loose: `check_line_breaks` runs before it and `check_links` after it on the tag's own document. | Reword it to "before parsing it". |
| TD-T739-01 (rest) | as SEC-T745-01 | The line limit is in, and a total bound is not. | As SEC-T745-01. |
| SEC-T741-17 (rest) | The gates' runner | A dedicated runner tag needs a runner, so a branch job on the same runner may leave state on the host, and `unit-tests` binds the Docker socket **(unverified, runner-dependent)**. | A dedicated runner tag on the gates, and pin it. |

**Not graded by a reviewer:**

| Id | Location | Finding | Fix |
|---|---|---|---|
| TD-T745-01 | The project's CI/CD variables | `ANTHROPIC_API_KEY` is a project variable, masked and not protected, so it reaches every job, on every branch. No job in `.gitlab-ci.yml` names it, and it was never named there (`git log -S`). The orchestrator found it by listing names through the API and printed no value. `8ee1e2d3` removes it from the docs gate's environment; every other job still has it. | **The user's decision:** delete it if unused, or protect it. Rotate it if there is any doubt. |

## 5. Not verified

- **By the reviewer:** no code was run, so its results are hand traces. `markdown-it-py` 4.2.0's source was not read. GitLab's `front_matter.rb` and the runner's `shells/abstract.go` are master, read through a summarising fetch, not the deployed versions. Real rendering, the sanitizer and the Release description were not seen. Docker executor details and variable precedence are from memory.
- **Partly read:** `test_ci_hash_pins.py` and `test_publish_release_job_token.py` outside the diff, and `.gitlab-ci.yml` between lines 70 and 185.
- **`8ee1e2d3`** was not reviewed.
- **The `unset` line and `GIT_STRATEGY: clone`** have never run in a real job. They run first in a tag pipeline, with the parser install.
- **The value of `ANTHROPIC_API_KEY`:** not read, so whether it is live is unknown.
