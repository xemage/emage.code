# Artifact: security-review-t739-gate-parser-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only, with no shell. The orchestrator recorded this artifact from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-05.
- **Target**: T739 (plan-136) on `agent/devops-engineer/T739` at `ce5464091e49b14a4e47b4c302a89743961a96f1`, from an exported diff and the worktree files.
- **Based on**:
  - `docs/plans/plan-136-release-gate-markdown-parser.md`
  - `docs/artifacts/security-review-t738-batch-n-two-v1.md` § 4
  - `docs/artifacts/security-review-t730-t732-batch-g-v1.md` § 4
  - `scripts/verify-release-docs.py`, `.gitlab-ci.yml`, `ci/requirements-release.txt`, `tests/functional/test_verify_release_docs.py`, `tests/functional/test_ci_hash_pins.py`
- **Tools**: `pip-audit` did not run: the tool reported `executable not found: 'pip-audit'`. The reviewer used PyPI's data instead. `grep_content` reflects `develop`. No read was refused.
- **Orchestrator's checks**, with `markdown-it-py` 3.0.0 and the locked 4.2.0:
  - About 45 shapes compared with the rendered HTML gave identical results on both versions. The gate counted no anchor that the renderer hides, apart from the stated raw HTML residual. The three pathological inputs the reviewer was told about (200000 `*`, 50000 `[`, 5000 `> `) took under a second, but that statement was too broad: after the review, the orchestrator measured a line of many attributes scaling worse than linearly (TD-T739-01, plan-136 § Outcome). The reviewer did not see this.
  - The real tree passes with a clean install from the new lock.
  - The reviewer's hand traces, run on the commit:

    | Id | Shape | Result |
    |---|---|---|
    | SEC-T739-01 | The invalid-UTF-8 comment shape | With `errors="ignore"`, the gate's read: gate True, anchor rendered. With `errors="replace"`: gate False, anchor hidden. Confirmed on the parser side |
    | SEC-T739-02 | `**<span hidden>Cursor</span>**`, and a heading with `display:none` | Gate True. Confirmed |
    | SEC-T739-07 | Shapes (a), (b), (c) | 0 problems each, while the control has 1. Confirmed |
    | Question 2 | 25 nested list markers, then the section | Gate False. Confirmed: a false FAIL |

## Verdict: CONDITIONAL_PASS; its one condition is met by this record

- 0 CRITICAL, 0 HIGH, 0 MEDIUM.
- No breach of an Immutable Security Constraint, and no control that `security-guidelines.md` requires is removed or weakened.
- Nothing blocks the merge. The only condition is that the LOW findings be tracked as debt. Section 4 is that record; the next register version takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 16 | 5 | 11 (tracked, section 4) |

**Why LOW.** As in T738, each route needs a crafted file committed with write access that survives merge request review, and that person could equally remove the pointer. The consequence is a release document without a visible migration item.

## 1. Rulings

- **Design against code.** It conforms: the section's opening and end, the container rule, what counts as text, and the depth count. A missing inline token is not reachable, and would be a traceback and exit 1.
- **False PASS.** Reference links, a heading in a reference definition, tabs, lazy continuation and entities give the right result. `maxNesting` can only lose later content, so a True always rests on a visible anchor. The routes left are SEC-T739-01 to -04.
- **Fail closed.** Acceptable. `--help` and a bad argument are not gate runs; a bad argument exits 2, and a job always passes `--tag`. `main()` has no broad `except`, and its only `return 0` comes after the check.
- **Supply chain.**
  - Against PyPI's JSON: the hashes of both wheels and both sdists match the lock; both wheels are `py3-none-any`; both uploads are older than the 2026-10-22 cut-off; neither is yanked; `vulnerabilities: []`.
  - A wheel with `--only-binary=:all:` runs no build backend, so third-party code first runs at `import markdown_it`.
  - A PyPI outage fails closed. The job must stay without `allow_failure`, because an outage is when someone will be tempted to add it.
  - The same wheels already run in `unit-tests`, so T739 adds a new token context and no new code to trust (SEC-T739-06).
- **What was removed.** Nothing weakens a control. All listed flips are correct against CommonMark. Under GFM the same lines are at most a table row, and the following list or heading still renders. Further changes, all visible and correct: `+` and `1)` markers, indented headings, and a lead in an item's second paragraph now count.
- **Claims.** `--help` is accurate on the section, the anchor and the residuals, with two loose points (SEC-T739-02, -09).
- **Test quality (read, not run).** Each named mutation should fail a test. The 1.0 s timing test could flake on a loaded runner, which is a stability concern, not a security one.

## 2. Resolved findings

| Id | Finding | Ruling |
|---|---|---|
| SEC-T731-09(b) | The gate paired fences or closed comments where CommonMark does not | Closed. Both forms are False |
| SEC-T738-01 | A wrongly opened type 7 block hid a fence or `<?` line | Closed. The construct now hides the anchor, as it does for a reader |
| SEC-T738-03 | `HTML_COMMENT_RE` hid too much | Closed. It is gone from this path, and both shapes are tested |
| SEC-T738-04 | Older claims contradicted the docstrings | Closed. One label stays misleading (SEC-T739-09) |
| SEC-T731-08 | The section ended only at a `## ` line, so an anchor in the next section counted | Closed as written. `section_text` remains for the verdict check; see SEC-T739-07 |

## 3. OWASP coverage

| Category | Findings (open) |
|---|---|
| A05 Security Misconfiguration | SEC-T739-08 |
| A08 Data Integrity | SEC-T739-01 to -07, -09; SEC-T738-02, -06 |
| A01, A02, A03, A04, A06, A07, A09, A10 | 0. Hash lock checked, printed text passes `printable`, parser output is never rendered, no URL from input |

## 4. Findings tracked as LOW debt (owner devops-engineer; next sprint)

Ordered by the fix the reviewer would take first. SEC-T738-02 and SEC-T738-06 stay open as `security-review-t738-batch-n-two-v1.md` § 4 records them. The plain-newline part of SEC-T738-02 is now documented in `--help`.

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T739-05 | `tests/functional/test_ci_hash_pins.py`, `release_gate_job_problems` | The pins do not catch `allow_failure: true`, `when: manual`, or an `exit 0` line before the gate, because the script check is only membership. `needs` in `release` does not stop a release after an allowed failure. | Require `script` to equal the gate command, refuse `allow_failure`, `when` and `variables` on the job, and assert `rules` exactly, each with a mutation. |
| SEC-T739-01 | `scripts/verify-release-docs.py:566`; the claim at `:20` | `errors="ignore"` drops invalid bytes before parsing, so `<!-- x --\xff>` closes a comment here that a renderer replacing the byte keeps open, and a hidden anchor counts. Older than T739. How GitLab treats such a file is **(unverified)**. | Decode strictly and refuse the document, naming the byte offset and never the content, with a fixture. The other `errors="ignore"` reads are worth the same. |
| SEC-T739-02 | `inline_text`, `:470-482`; `--help` `:206-207` | Text between inline HTML tags counts, as in `**<span hidden>Cursor</span>**`. "Inline HTML never count" reads wider than that. Whether GitLab's sanitizer keeps these attributes is **(unverified)**. | Refuse an anchor holding an inline tag, allowing comments, and update `--help`. |
| SEC-T739-04 | `:210-211` | Stated residual. A document that opens and closes with `---` around the section reads as live here and may be front matter on GitLab **(unverified)**, including as the Release description. | Refuse a release document whose first line is `---`, `+++` or `;;;`. |
| SEC-T739-06 | `.gitlab-ci.yml:196-206` | pip and `markdown_it` see `CI_JOB_TOKEN` and probably `WIKI_TOKEN` **(unverified: project settings)**. The `release` job filters its environment for `git` and `apk`; this job does not. | Add `unset WIKI_TOKEN CI_JOB_TOKEN CI_REGISTRY_PASSWORD CI_REPOSITORY_URL` as the first `before_script` line, and update the pin. Residual: the clone credential in `.git/config`. Check the list against GitLab's documentation. |
| SEC-T739-08 | `docs/releases/_template.md:3`; `verify-release-docs.py:569`; `CONTRIBUTING.md` lines 405 and 436 on `develop` | "A line that starts with a bold lead" is looser than the parser. The direction is a false FAIL with a clear error. | "A paragraph that opens with a `**` span holding the word, optionally in a list". Point the two `CONTRIBUTING.md` lines to step 4's install. |
| SEC-T739-09 | `MIGRATION_POINTER_HELP` `:210`; docstring `:20` | The nesting limit is neither stated nor tested. "What stays open (SEC-T738-04)" cites a closed id. Some shapes have no fixture: nesting past the limit, an anchor in a reference definition's title, lazy continuation. | One sentence, the fixtures, and the new ids. |
| SEC-T739-07 | `section_text`, `:251-263`; `verdict_placeholder_problems`, `:266-277` | The verdict's placeholder check stays on line rules, and three crafted shapes pass with `- Status: pending` in place: (a) the heading quoted first in a comment, (b) a hidden heading line that ends the section early, (c) `FENCED_CODE_RE` pairing two ``` in a paragraph. Older than T739; plan-136 kept it on purpose. | Read these sections from the token stream, or at least refuse a second occurrence of the heading. Needs its own plan, because the field logic is line-based. |
| SEC-T739-03 | `:211-213` | Stated residual. `<div hidden>`, a blank line, then an anchor gives True. `<details>` only collapses content. | Optional: do not count an anchor after an unclosed non-comment `html_block`, which needs tag balancing. Otherwise keep it documented. |

## 5. Not verified by the reviewer

- No code was run. The orchestrator confirmed the shapes above. The mutation runs are the implementer's report.
- The source of 4.2.0 was not read, and of 3.0.0 only `parser_block.py` and `presets/commonmark.py`. Statements about the other rules come from knowledge.
- GitLab: real rendering, including front matter, invalid bytes and the sanitizer; the flags on `WIKI_TOKEN`; tag protection; which runner holds the Docker socket; the install in a tag pipeline.
- The test files were read in part.
