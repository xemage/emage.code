# Artifact: security-review-t715-t716-batch-b-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. The review was read-only: the reviewer had no shell and read the diffs from files the orchestrator exported. The orchestrator wrote this record from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-01.
- **Target**: T715 and T716 (LOW batch B, plan-126) on `docs/plan-126-batch-b`, at `1ccaa513`.
  - T715 commits: `1d658e77`, `f48a63c9`, `dcc892fe`, `15e933ce`, `12ccbe82`.
  - T716 commits: `b0a0973f`, `83dc7503`, `86d0fa32`, `eb363f51`, `9ad48fa2`.
- **Based on**:
  - `docs/tasks/task-T715.md`, `docs/tasks/task-T716.md`, `docs/plans/plan-126-batch-b-release-tooling.md`
  - `docs/artifacts/tracked-debt-register-v4.md` (batch B)
  - `scripts/verify-release-docs.py`, `scripts/publish-release.py`, `scripts/check-release-tag-tree.py`, `scripts/check-main-develop-drift.py`, `scripts/audit-mcp-pins.py`, `.gitlab-ci.yml`

## Verdict: PASS (the review was CONDITIONAL_PASS; its one condition is met by this record)

The reviewer found:
- 0 CRITICAL, 0 HIGH and 0 MEDIUM findings;
- no breach of an Immutable Security Constraint;
- no control removed or weakened: each of the 20 controls assessed is equal to or stricter than before.

The only condition was that the nine LOW findings be tracked as debt. Section 4 is that record: each LOW has an owner and a trigger, and goes into the next register version.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 9 | 0 | 9 (tracked, section 4) |

## 1. Rulings on T715 (`scripts/verify-release-docs.py`)

- **Cursor anchor outside hidden Markdown (SEC-T703-01, lines 139-140, 386-410).** Effective.
  - Code fences and HTML comments are blanked before the section search.
  - An unclosed fence or comment hides the rest of the file. This can only make the check fail, never pass by mistake.
  - Gap: raw HTML blocks are not blanked (SEC-T715-03).
- **Unparsed pointer lines fail (SEC-T703-02, lines 132-134, 357-366, 426-430).** Effective for the keyword forms. The check is case-insensitive, and a keyword hit must lie inside a parsed span. Gaps: SEC-T715-01 and SEC-T715-02.
- **Newer pointers fail (SEC-T703-03, lines 431-438, 457-461).** Fails closed by default.
  - `--allow-newer-pointers` only restores the old behaviour.
  - A test checks that the CI job never passes it, and `.gitlab-ci.yml:195` does not pass it.
- **Whole-token `Latest release:` marker (T717-D2, lines 294-307, 322-323).** Correct.
  - The check rejects `-rc.1`, `.1` and extra digits after the version.
  - It still accepts a sentence-ending `.` or `)`.
  - The tag is passed through `re.escape`.
- **Docstring (SEC-T685-03, code part, lines 20-25).** Matches CI: the tag-tree check runs in the blocking drift-gate job with no grace window.
- **Test pins (SEC-T677-01, SEC-T677-02, TL-T708-04, TL-T708-05).** Adequate. The order in which the installer swap sets its `SWAP_*` variables is checked both by running it and by reading the source.

## 2. Rulings on T716

- **Exact ref names (SEC-T685-01, `check-release-tag-tree.py:71-86, 117-118`).** Effective.
  - `git show-ref --verify --hash` reads the full name literally, with no short-name search.
  - A ref that was not fetched resolves to nothing, so the check fails closed.
  - The sibling drift script still has the old weakness (SEC-T716-01).
- **Unicode categories for commit subjects (SEC-T685-02, `publish-release.py:76-80, 326-332`).** A strict superset of the old explicit class under Python 3.12 (Unicode 15.0).
  - Invisible characters are stripped before escaping, so stripping cannot form a `<!--`.
  - Residual: the result depends on the Python version (SEC-T716-02).
- **Markdown escaping of changelog entries (SEC-T675-10, `publish-release.py:417-446, 463`).** Sound.
  - Code spans are paired the CommonMark way.
  - Escaping `< > [ ] &` removes raw HTML, autolinks, links, images and character references.
  - Block markers at the start of an entry are escaped.
  - The release description holds no commit subject.
  - Gaps: SEC-T716-03 and SEC-T716-05.
- **Child-process environment (SEC-T686-07, `publish-release.py:96-131, 242-254`).** Stricter than before.
  - `GIT_EXEC_PATH`, `GIT_ASKPASS`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` and `GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n` are dropped.
  - Every remaining name has a stated reason.
  - Whether the runner sets a dropped variable is **(unverified)**.
- **`LC_` rule (SEC-T686-08, `publish-release.py:131, 252`; `.gitlab-ci.yml:222`).** The script and the CI bootstrap use the same pattern and `fullmatch`, and a test pins them together.
- **`ApiCredential` and `ApiTarget` (TL-T708-06, `publish-release.py:532-605`).** No token appears in a repr, str, log line or error message. Residual: SEC-T716-04.
- **CHANGELOG order (D-T710-2, lines 503-506)** and **semantic previous-tag sort (T717-D3, lines 279-298)**: correct, with no finding.
- **`via_list` and cycles (SEC-T712-05, `audit-mcp-pins.py:278-319, 343`).** Fails closed.
  - A `via` that is not a list is never accepted.
  - The `seen` sets end every cycle.
  - A vulnerability entry that is not a dict still raises `AttributeError` (line 339), so the audit exits non-zero. That is a closed failure, not a finding.

## 3. OWASP notes

- **A03 Injection:** subjects are neutralised. Tags and refs are filtered by pattern, go to git after `--end-of-options` or as full `refs/` names, and run with `shell=False`. The bootstrap runs `python3 -I`. Residual: SEC-T716-03.
- **A05 Misconfiguration:** the child-process allowlist is stricter. Residual: SEC-T716-02.
- **A08 Data integrity:** tags that pose as refs are ignored, and newer or unparsed pointers fail the gate. Residuals: SEC-T716-01 and SEC-T716-05.
  - Info, **(unverified)**: a tag pipeline runs the tagged commit's own `.gitlab-ci.yml`. Keep `v*` tags protected, restrict tag creation, and limit pipeline-variable overrides to Maintainer.
- **A09 Logging:** no token is logged. Residual: SEC-T715-04.
- **A01, A02, A04, A06, A07, A10:** not affected. The host pin and the refusal to follow redirects are unchanged and still tested.

## 4. Findings (all LOW, tracked as debt; owner devops-engineer)

| Id | Location | Finding | Fix | Trigger |
|---|---|---|---|---|
| SEC-T715-01 | `verify-release-docs.py:134, 357-366` | Pointer forms without the keywords still pass unchecked: `v9.0.0.md`, `release-notes`, `doc/releases`, `"$REL_DOC"`, a wiki URL. | Widen `POINTER_LIKE_RE`, or name release documents in `install.sh` only through one checked constant. Add a fixture for each form. | Before the next release that changes the `install.sh` pointers |
| SEC-T715-02 | `verify-release-docs.py:352-353`; `install.sh:1300` | A prose pointer on a line that mentions Cursor is checked only for existence, not for the Cursor item. | Check the Cursor item for it, or report it as unparsed. Reword `install.sh:1300`. | Same |
| SEC-T715-03 | `verify-release-docs.py:386-414` | An anchor inside a raw HTML block still counts. | Also blank CommonMark HTML blocks, with a fixture. | Next LOW batch |
| SEC-T715-04 | `verify-release-docs.py:427-430` (also line 221) | An `install.sh` line is printed into the CI log without stripping control or bidi characters. | Replace them with the `UNSAFE_RE` used in `check-release-tag-tree.py:48`, with a test. | Next LOW batch |
| SEC-T716-01 | `check-main-develop-drift.py:50-51, 146-147`; `.gitlab-ci.yml:208-209` | `origin/main` and `origin/develop` are resolved by short-name search, so a tag of that name shadows the branch. A false PASS is caught by the tag-tree check in the same job. A false FAIL blocks the release until the stray tag is deleted. | Resolve the refs as `check-release-tag-tree.py:71-86` does, with a shadow-tag test. | Before the next release that changes the drift job; recommended first |
| SEC-T716-02 | `publish-release.py:76-80, 326-328` | The category test depends on the Unicode version of the Python that runs it. On a newer Python, a code point newly assigned in a reserved Default_Ignorable range would be kept. | Add the reserved Default_Ignorable ranges explicitly, and assert `unicodedata.unidata_version` for the release image. | Next LOW batch; at the latest when the release image changes |
| SEC-T716-03 | `publish-release.py:417-446` | Bare URLs and GitLab references (`@user`, `#123`, `!12`, `~label`, `%milestone`) in a commit subject still render as links in `CHANGELOG.md`. Commit authors need push or merge access. | Document this as residual risk at lines 411-416, or neutralise these forms outside code spans, with tests. | Next LOW batch |
| SEC-T716-04 | `publish-release.py:532-539` | `ApiCredential` is a NamedTuple: `tuple()`, `_asdict()`, `%`-formatting, unpacking and pickling still expose the token. No code path uses these today. | Use a non-iterable type (a frozen dataclass with `field(repr=False)`), with a test; or narrow the docstring. | Next LOW batch |
| SEC-T716-05 | `tests/functional/test_publish_release_t716.py` | The one CommonMark rendering test skips silently when markdown-it-py is missing. Whether CI installs it is **(unverified)**. | Pin markdown-it-py for the tests, or fail instead of skipping when `CI` is set. | Next LOW batch |

## 5. Not verified by the reviewer

The reviewer had no shell, so it did not run the test suite, the gates or the CI lint. The orchestrator runs these independently before the merge. It also did not check runner or GitLab behaviour, which stays **(unverified)** until the next tag pipeline.
