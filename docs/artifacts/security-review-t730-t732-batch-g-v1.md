# Artifact: security-review-t730-t732-batch-g-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only, with no shell. The orchestrator recorded this artifact from the reviewer's three reports.
- **Gate**: security. **Date**: 2026-11-04 (first report 2026-11-02).
- **Target**: T730, T731 and T732 (LOW batch G, plan-131) on `docs/plan-131-batch-g`.
  - First review at `3a4bfd4c`.
  - Second report at `2c583f5e`, from an exported diff only.
  - Final re-check at `c86c1781be57968df28f1f9f2855264907b1e17e`, against the real files.
- **Based on**:
  - `docs/tasks/task-T730.md` to `task-T732.md`
  - `docs/plans/plan-131-batch-g-release-tooling.md`
  - `docs/artifacts/security-review-t715-t716-batch-b-v1.md` § 4
  - `scripts/check-main-develop-drift.py`, `scripts/publish-release.py`, `scripts/verify-release-docs.py`
  - `ci/requirements-ci.in`, `ci/requirements-ci.txt`, `ci/js/`
  - `tests/functional/test_function_size.py`, `.gitlab-ci.yml`
- **Refused reads.** During the second report, the permission system refused the reviewer's reads of `scripts/publish-release.py`, `scripts/verify-release-docs.py` and `.git/worktrees/plan-131/HEAD`, with an instruction to stop and wait for the user, so that report's verdict was provisional. The orchestrator put this to the user, who answered "Allow its reads (Recommended)". The reads succeeded in the final re-check. The cause of the first refusal was not established.
- **Orchestrator's checks**:
  - `npm view acorn@8.19.0`: the integrity value equals `ci/js/package-lock.json`; published 2026-10-05.
  - `npm audit`: 0 vulnerabilities.
  - `npm audit signatures`: 1 package with a verified registry signature.
  - pip-audit did not run on the CI lock. The reviewer's tool fails on worktree paths. The reviewer compared markdown-it-py and mdurl with PyPI's hashes and vulnerability data instead.

## Verdict: PASS (the final re-check was CONDITIONAL_PASS; its one condition is met by this record)

- 0 CRITICAL, 0 HIGH, 0 MEDIUM.
- No breach of an Immutable Security Constraint.
- No required control removed or weakened.
- The three findings the user chose to fix now (SEC-T731-01, SEC-T731-06, SEC-T730-05) are resolved as reported. SEC-T731-09 is a newly found residual of the first two.
- The only condition is that the eleven remaining LOW findings be tracked as debt. Section 4 is that record; the next register version takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 17 | 6 | 11 (tracked, section 4) |

**Correction to the first report.** It said that no HTML or image can be produced from a commit subject, and that the result is "a link only, never HTML". That was wrong for the code before `8de05af1`: an opening run of more than 80 backticks is literal text in comrak (read from source), so the inside could parse as Markdown (SEC-T730-05). After `8de05af1` the reviewer knows no route to HTML, a link or an image apart from the documented `mailto:` residual, but does not restore the absolute claim. Live GitLab, including its pre-escape filter and its parser version, is **(unverified)**.

## 1. Rulings on the changes

- **Exact refs** (`check-main-develop-drift.py:46, 61-82, 177-183`). Correct: `refs/remotes/<ref>` is resolved with `git show-ref --verify --hash`, and the file is read by object id. Plain ref names are enforced with `fullmatch`. A missing ref fails without a traceback.
- **Reserved Default_Ignorable ranges** (`publish-release.py:81-89`). Correct and complete for Unicode 15.0.
- **Sigil escaping.** Correct for CommonMark. Whether GitLab's reference filters respect the escape is **(unverified)**.
- **`ApiCredential` as a `__slots__` class.** Effective for every form tested. Residual: SEC-T730-03.
- **CI Python lock.** markdown-it-py 4.2.0 and mdurl 0.1.2 have hashes that match PyPI, `--exclude-newer 2026-10-22T12:00:00Z` gives an 11-day cooldown, and CI still installs with `--require-hashes --only-binary=:all:`. Residual: SEC-T730-04.
- **Line separators** (`55e663ee`, `verify-release-docs.py:190, 384-402`). The character set is complete and the error reports only the code point. `install.sh` is outside it: SEC-T731-07.
- **T731's three additions beyond the reviewer's rule** (`15807302`). The reviewer found all three correct, and the last two needed:
  - a type 7 block opens after any line (`:485`);
  - a list run must start at a blank line or heading (`:540-542`);
  - `rstrip(" \t")` and `_filler_lines` (`:260, 490-492, 525`), so that blanking does not create fake blank lines.
- **Deliberate false FAILs** (acceptable; each fails closed): `Some text\n**M-3...**`, `Some text\n### M-3...`, `x\n- a\n- **M-3...**`, and `## Migration Guide <!-- x -->`. `docs/releases/v9.0.0.md:71-72` is a blank line followed by the anchor, so that document still passes. The "lacks its Cursor migration item" message does not mention the blank-line rule, though the `--help` text does; the reviewer notes this as worth adding, not as a security issue.
- **acorn supply chain** (T732). Exact pin, lock v3, sha512 integrity equal to the registry, `npm ci --ignore-scripts`, argv without a shell, a parse failure fails closed, a missing parser fails under CI. Residuals: SEC-T732-01, -02.

## 2. Resolved findings

| Id | Finding | Fix | Evidence |
|---|---|---|---|
| SEC-T730-01 | Two URL shapes in commit subjects stayed bare | `c3004758`: tokens wrapped, a space beside a kept span, output re-parsed | `publish-release.py:450-451, 506-531` |
| SEC-T730-02 | `URL_TOKEN_RE` was quadratic | `c3004758`: linear split, closers by bisection | `:451, 457-469, 496` |
| SEC-T730-05 | Over-long backtick runs kept as code spans | `8de05af1`: a run over 32 opens no span and is escaped, in both parsers | `:447, 480, 498` |
| SEC-T731-01 | Type 7 HTML block not blanked after a non-paragraph line | `55974ffe`, `15807302` | `verify-release-docs.py:485` |
| SEC-T731-02 | `str.splitlines()` split at more characters than CommonMark | `55974ffe`, `55e663ee` | `:260, 506, 537`; refusal at `:384-402` |
| SEC-T731-06 | Anchor inside a multi-line inline construct counted | `15807302`: an anchor counts only after a blank line or ATX heading | `:490-492, 525, 536-543` |

## 3. OWASP coverage

| Category | Findings (open) |
|---|---|
| A02 Cryptographic Failures (token handling) | SEC-T730-03 |
| A03 Injection (Markdown/autolink) | SEC-T730-06 |
| A04 Insecure Design (gate false PASS) | SEC-T731-03, -04, -07, -08, -09 |
| A08 Data Integrity (locks, cooldown, CI) | SEC-T730-04, SEC-T732-01, -02 |
| A09 Logging (CI log sanitising) | SEC-T731-05 |
| A01, A05, A06, A07, A10 | 0 |

## 4. Findings tracked as LOW debt (owner devops-engineer; next sprint)

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T730-03 | `publish-release.py:562-586, 683` (lines at `3a4bfd4c`) | `object.__getstate__()` (Python 3.11 and later) and `copyreg` or `dispatch_table` registrations still expose the token. `main()` keeps the token in a plain local, which a traceback that captures locals would show. All need deliberate in-process calls. | Make `__getstate__`, `__copy__` and `__deepcopy__` raise, and test them. Document the residual. Optionally `del token`. |
| SEC-T730-04 | `ci/requirements-ci.in`, `ci/requirements-ci.txt:2-4` | The 7-day cooldown and the 14-day minimum age are not enforced by any test. | Add a `# generated-on:` header, and assert a gap of at least 7 days in `test_ci_hash_pins.py`. |
| SEC-T730-06 | `publish-release.py`, the fallback after the re-parse | The fallback leaves a bare URL rather than failing closed, and a test expects that. No input that reaches it is known. | Raise `ReleasePublishError` there, or correct the comment and the claim. |
| SEC-T731-03 | `verify-release-docs.py:142, 146` (lines at `3a4bfd4c`) | Two `POINTER_LIKE_RE` alternatives take quadratic time on long lines. The input is the reviewed `install.sh`. | Bound the quantifiers, and add a long-line timing test. |
| SEC-T731-04 | `verify-release-docs.py:141-148` (lines at `3a4bfd4c`) | False negatives: variable-built names, `9.0.0.md` without a `v`, `rel-notes`, `/-/tags/` URLs, `CHANGELOG`/`NEWS`, homoglyphs. | Add the listed alternatives with fixtures, and name the residuals in `MIGRATION_POINTER_HELP`. |
| SEC-T731-05 | `verify-release-docs.py:183` (line at `3a4bfd4c`), as in `check-release-tag-tree.py:48` | `UNSAFE_RE` misses U+00AD, U+180E, U+FFF9-FFFB, the tag characters U+E0001 and U+E0020-E007F, and unassigned code points. | Share one category-based filter between both scripts, and keep the equality test. |
| SEC-T731-07 | `verify-release-docs.py:435` | `install.sh` is outside the line-separator refusal, so `docs/releases/v9.0.0.md<U+2028>Cursor` on one shell line drops the Cursor requirement. | Add `INSTALL_SH` to the `check_line_breaks` list. |
| SEC-T731-08 | `verify-release-docs.py:265` | The section ends only at a line starting `## `. A setext `Next\n---`, ` ## Next` or `##\tNext` does not end it, so an anchor in the next section counts. The anchor is visible but in the wrong section. Older than this batch. | Also end the section at a level 1 or 2 ATX heading indented up to 3 spaces or followed by a tab, and at a setext underline. Add fixtures. |
| SEC-T731-09 | `verify-release-docs.py:522, 156-157`, and the claims at `:479, 534` | A false PASS is still possible when the gate hides too much, because a blanked line counts as a block start. (a) `<!-->\n<a title="\n-->\n**M-3. Cursor removed.**\n">`: CommonMark closes the comment on line 1, but the gate stays open until `-->`. `<?>` behaves the same way. (b) `- a\n  ```\nx\n  ```\n**M-3. Cursor removed.**`: the gate pairs two fences that CommonMark does not. The "never a false PASS" claims are not strictly true. | (a) Change `:522` to `block[0].search(line)`. (b) Use `markdown-it-py` in the gate, or document the residual. Correct the two claims either way. |
| SEC-T732-01 | `.gitlab-ci.yml:93-104` (lines at `3a4bfd4c`) | npm and the acorn parser run in `unit-tests`, the job that binds the host Docker socket. The package is bound by sha512, but npm is pinned to a major version only and acorn has no provenance attestation. | Run the JS size tests in a job without the socket, or check the tarball's sha512 in Python and extract it with `tarfile` `filter="data"`. |
| SEC-T732-02 | `ci/js/README.md:39-43` | The 14-day minimum age for acorn is only a manual rule. | Record the publish date in a machine-readable form, and assert the gap in `TestJsParserSupplyChain`. |

## 5. Not verified by the reviewer

- The test suite and the CI lint. The orchestrator ran the suite before the merge.
- The shapes above: they come from the code and CommonMark rules, not from a run. The comrak and cmark limits are read from their source.
- `main()` of `verify-release-docs.py` at HEAD, so its `check_line_breaks` call rests on the exported diff.
- Tree match: by reading the files against the diffs, not with `git diff`. The reviewer confirmed the sha from the worktree's HEAD and its ref.
- Live GitLab rendering of escaped references and of URLs in code spans.
