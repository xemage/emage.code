# Artifact: code-review-t619-v1.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/tasks/task-T619.md`, `docs/plans/plan-120-release-v8-readiness.md`, `docs/plans/plan-121-release-v8-wave-2.md` (T625 item), `docs/tasks/task-T625.md`, `implementation/knowledge/commands/code-review.md`, skill `code-review`, and the T619 change `git diff 5e07a6b..3771781` (merge `3771781`, single code commit `ce0ad52`).

## Review: T619 - release job uses the single release document and stops writing a root `release-notes.md`

### Verdict: CONDITIONAL_PASS

### Summary

The change does what T619 asks: no code path writes a root `release-notes.md`, the CI `release` job lists only `CHANGELOG.md`, the GitLab description is built in memory from `docs/releases/<tag>.md` plus the changelog section, and the tag is now validated fail-closed before it reaches a path, a git argument or an API URL. The 16 tests and the offline dry run pass. There are no Must Fix findings and no security finding above LOW; three Should Fix items concern coverage of the real (template-shaped) release document path, a coding-standard breach in the new dry-run helper, and tests that accept any `RuntimeError`.

### Context and artifact versions reviewed

| Artifact | Version / ref | Use in this review |
|---|---|---|
| `scripts/publish-release.py` | after `3771781` (diff vs `5e07a6b`) | reviewed in full, cited by line |
| `scripts/dry-run-publish-release.py` | new in `3771781` | reviewed in full |
| `tests/functional/test_publish_release.py` | after `3771781` | reviewed in full |
| `.gitlab-ci.yml` (`release` job, lines 193-206 at this ref) | after `3771781` | reviewed (diff and surrounding job) |
| `docs/tasks/task-T619.md` | as merged (Status `done`) | acceptance criteria 1-3 |
| `docs/plans/plan-120-release-v8-readiness.md` | v1 (as committed) | plan row B (T619) the change must match |
| `docs/artifacts/security-review-t619-release-job-v1.md` | v1 | read for context only; its conclusions are not relied on |
| `docs/releases/_template.md`, `docs/releases/v7.0.1.md`, `scripts/verify-release-docs.py` | at `4c5b43e` | consumers/inputs of the changed path |
| Checkpoint | none cited by the brief | not reviewed against a checkpoint |

Decision IDs: none cited in the brief; the plan input is the user's decision B-1 ("One, at docs/releases/ (Recommended)") as quoted in `task-T619.md`. No ADR applies.

### Plan conformance (task-T619.md section 1 and section 4)

- AC1 (no root `release-notes.md`, artifact removed, CHANGELOG generation unchanged): met. `write_artifacts` writes only `CHANGELOG.md` (`scripts/publish-release.py:231-233`); the artifact line is removed (`.gitlab-ci.yml` diff, one `-` line); `update_changelog` (`:204-228`) is untouched and now receives the same text as before (`:303-304`). A repo-wide `grep` finds no live consumer of a root `release-notes.md` (hits are golden fixtures with a different file, historical records, and the change's own negative assertions).
- "Keep token handling, `release-docs-gate`/`main-develop-drift-gate` `needs`, and the tag rule unchanged": met, and pinned by `tests/functional/test_publish_release.py:238-240`. `--token "${WIKI_TOKEN}"` is untouched.
- "Provide a local dry-run (no network, no tag, no push) against a copy of `docs/releases/v7.0.1.md`, and unit tests": met (`scripts/dry-run-publish-release.py`, 13 new tests).
- AC2 (dry run and new tests pass): verified by me (below). The full suite `tests/run.py` and the gate list (sync, registry, maturity, scorecard, validate-tasks, evaluator hash, held-out isolation) **(unverified, not re-run in this review)**.
- AC3 (Security Engineer reviewed): a security review artifact exists in the diff (`docs/artifacts/security-review-t619-release-job-v1.md`); I did not rely on it.
- Task-brief "short report with the dry-run output ... and every deviation" **(unverified; it is not part of the diff)**.

### Read-only checks run

- `python3 -m unittest tests.functional.test_publish_release`: `Ran 16 tests ... OK`.
- `python3 scripts/dry-run-publish-release.py`: exit 0, `root release-notes.md written: False`, files in the temp root `CHANGELOG.md` and `docs/releases/v7.0.1.md`, fake calls `GET` (404) then `POST .../projects/0/releases`, `DRY RUN OK`. `git status` before and after: clean (the repository is not written).
- `git merge-base`, `git rev-list --count` and `git log --pretty=%s` accept `--end-of-options` on the local git 2.43.0 (the CI image `python:3.12-alpine` ships a newer git; version in that image **(unverified)**; `--end-of-options` needs git 2.24 or later).

### Review checklist

**1. Correctness and acceptance criteria.** Met (above). `validate_tag` uses `fullmatch` (`:48-52`), so a trailing newline is rejected, and it runs first in `main()` (`:293`) before any `git fetch`, which `test_main_rejects_invalid_tag_before_any_git_call` (`tests/functional/test_publish_release.py:176-188`) proves with an empty call list. The empty-document guard (`scripts/publish-release.py:124-127`) closes a real gap: previously a blank document produced a description that was only the title and changelog. One uncovered correctness path is the heading strip (Finding S1).

**2. Security (OWASP Top 10).** The change touches security-sensitive code (input validation of an externally supplied tag, `subprocess` argv, a bearer token sent to an API, release publishing), so all ten categories were run against the diff:

| # | Result |
|---|---|
| A01 Broken Access Control | None. Token scope (`WIKI_TOKEN`) and the `needs` gates are unchanged and pinned by test. |
| A02 Cryptographic Failures | None. Token is not logged; `:316-320` prints only the tag; the dry run uses a labelled placeholder and a `.invalid` host (`scripts/dry-run-publish-release.py:29,117`) and a test asserts the placeholder is not in stdout (`tests/functional/test_publish_release.py:115`). |
| A03 Injection | None; improved. All git calls use an argv list (no shell). `--end-of-options` now precedes every revision argument (`scripts/publish-release.py:95-98,109`), and the tag is allowlisted before use in a file path (`:117-118`), git args and the release URL (`:254`). Before this change a tag containing `/`, `?` or `..` could shape the URL and path. |
| A04 Insecure Design | None. Fail-closed on invalid tag, missing or blank document. |
| A05 Security Misconfiguration | None. CI diff only removes an artifact line. |
| A06 Vulnerable Components | None. Standard library only; no dependency or image change. |
| A07 Authentication Failures | Not applicable beyond the token (see A02). |
| A08 Data Integrity Failures | None. Release job still `needs` both gates; tag rule unchanged. The dry run copies the document into a temp root, so it cannot alter the tree. |
| A09 Logging and Monitoring | None new. `gitlab_request` still includes the response body in its error (`:248`); pre-existing. |
| A10 SSRF | `--api-v4-url` is not scheme-checked (`:253-254`, `:283-286`) and `urllib` accepts non-HTTP schemes; the value comes from the CI predefined variable, unchanged by this MR. Recorded as N3 (SECURITY:LOW, pre-existing). |

No finding is graded SECURITY:CRITICAL, SECURITY:HIGH or SECURITY:MEDIUM. No Immutable Security Constraint is breached and no required control is removed or weakened; input validation was added, not removed.

**3. Performance.** No concern: one extra regex match and two string operations; the git calls are the same count as before.

**4. Code quality and maintainability.** Clear naming (`render_release_description`, `write_artifacts` docstring states its sole output). The three-line `_revision_range` git block is slightly repetitive but readable. One standard breach (S2).

**5. Test coverage.** Good breadth: happy path via dry run with a fixture document, real v7.0.1 document, no-write guard, missing and blank document (direct and through `main()`), tag allowlist (good and bad), argument order of the four git calls, traversal and symlink escape of the dry-run source, and the CI artifact and gate pins. Gaps: S1 and S3, N1 and N5.

**6. Documentation.** The module docstring (`scripts/publish-release.py:2-9`) and dry-run docstring (`scripts/dry-run-publish-release.py:2-13`) state the behaviour and the offline rehearsal. `docs/releases/_template.md` lines 4-6 still say the job embeds "highlights + install" while the job embeds the whole document; this is pre-existing, outside this diff, and recorded in `docs/artifacts/release-v8-audit-v1.md` (C-3).

**7. Gate status recommendation:** `conditional_pass`.

### Findings

#### Must Fix

None.

#### Should Fix

1. **`scripts/publish-release.py:197-198` and `tests/functional/test_publish_release.py:90`** - The branch that strips the document's own title when it starts with `# Release <tag>` is never exercised. The fixture uses `# v1.2.3`, and the only real document used, `docs/releases/v7.0.1.md`, also starts with `# v7.0.1`; the dry-run output shows the consequence (`# Release v7.0.1` followed by `# v7.0.1`). The v8.0.0 document is expected to follow `docs/releases/_template.md`, whose title is `# Release vX.Y.Z`, so the path that the real tag run will take is the one with no test and no rehearsal.
   > Suggestion: add a test (and ideally a second dry-run default or `--source` fixture) that uses a template-shaped document starting `# Release v1.2.3` and asserts the description has exactly one top-level title line. Decide separately, with the Product Owner or orchestrator, whether `render_release_description` should also strip a bare `# <tag>` title (that is a behaviour change, so not requested here).
2. **`scripts/dry-run-publish-release.py:80-86`** - `run_dry_run` takes five parameters (`tag, work, repo, source_dir, copy_changelog`); `AGENTS.md` § Code Standards allows at most four. The function is 48 lines, within the 50-line limit.
   > Suggestion: bundle `repo`, `source_dir` and `copy_changelog` into a small frozen dataclass (for example `DryRunSource`) or drop `repo`, which only the module loader needs and which tests never vary.
3. **`tests/functional/test_publish_release.py:165,216,226`** - Three tests assert `RuntimeError`, the base class. They pass for any unrelated `RuntimeError`, including the loader's `unable to load publish-release module` (`scripts/dry-run-publish-release.py:40-41`), so they can pass for the wrong reason. The base class is used because the dry-run module loads its own copy of `ReleasePublishError`, so `self.publish_release.ReleasePublishError` does not match.
   > Suggestion: keep `RuntimeError` but use `assertRaisesRegex` with the specific message (`release brief is empty`, `invalid release tag`, `escapes`), or expose the loaded module on the `run_dry_run` result so the test can assert the precise class.

#### Nice to Have

1. **`scripts/publish-release.py:40` and `tests/functional/test_publish_release.py:240`** - `TAG_RE` is a hand-copied duplicate of the CI rule, which appears four times in `.gitlab-ci.yml`; the test pins the CI string but does not compare it with `TAG_RE`, so the two can drift apart silently (a CI rule that is wider than `TAG_RE` fails closed at run time; a narrower one would accept less than the script).
   > Suggestion: extract the regex from the `release` job in the test and assert `TAG_RE.pattern` equals it.
2. **`scripts/dry-run-publish-release.py:108-112,154`** - The isolation relies on every write going through `module.ROOT`; a future relative-path write would hit the caller's current directory. `desc.split("---")[-1]` also truncates the displayed changelog if a commit subject contains `---`.
   > Suggestion: `os.chdir(work)` for the duration of the run (restore in the `finally`) and split on the `"\n\n---\n\n"` separator used by `render_release_description` (`scripts/publish-release.py:201`).
3. **`scripts/publish-release.py:109,253-254,283-286`** - (SECURITY:LOW, hardening, pre-existing) `git log` has no trailing `--`, so a file named like the revision makes it ambiguous (fails closed today); `--project-id` and `--api-v4-url` are used without a digit or `https://` check (CI-provided; A10). The token also remains in argv (`.gitlab-ci.yml` release job; already tracked as SEC-T619-05).
   > Suggestion: add `--` after the revision; validate `project_id.isdigit()` and `api_v4_url.startswith("https://")`; read the token from `os.environ` in a later task. Track as technical debt per `security-guidelines.md` § Security Review Workflow (LOW).
4. **`tests/functional/test_publish_release.py:100-115`, `scripts/dry-run-publish-release.py:102-106`** - The fake GitLab returns 404 on `GET`, so only the `POST` path of `create_or_update_release` (`scripts/publish-release.py:262-275`) is exercised; the `PUT` branch (existing release) has no coverage.
   > Suggestion: parametrise the fake so a second run answers the `GET` with `{"tag_name": tag}` and assert one `PUT`.
5. **`docs/tasks/task-T619.md:5,11` and `ce0ad52`** - The single code commit also carries ledger and Status-line edits (`docs/tasks/active-tasks.md`, `completed-tasks.md`, `task-T619.md` Status `done`), which the brief reserved to the orchestrator, and `Completed:` still reads `—`. Review-wise harmless, but it blurs the code diff.
   > Suggestion: keep ledger transitions in their own commit; set `Completed:` to the date when the brief is closed.

#### Well Done

- Validation is allowlist-based, anchored with `fullmatch`, placed at both entry points (`main` and `load_release_brief`) and before any side effect, and covered by negative cases including a newline suffix and a leading dash (`tests/functional/test_publish_release.py:172`).
- `--end-of-options` is applied to all four git calls and a test asserts its position relative to the tag (`:190-210`).
- The dry run is genuinely isolated: faked `run_git` and `gitlab_request`, `urlopen` made to raise, `ROOT` redirected to a temp directory, placeholder token, `.invalid` host, path-escape and symlink checks on the source (`scripts/dry-run-publish-release.py:68-77,108-125`), and it drives the real `main()` rather than reimplementing it.
- The CI change is the minimal single-line removal, and its invariants (`needs`, token argument, tag rule) are pinned by a test.
- Fail-closed behaviour for blank release documents is tested both directly and through `main()` with an assertion that no `CHANGELOG.md` is written.

### Conditions (CONDITIONAL_PASS)

The production track applies: each condition is resolved before the next gate (the Release gate for the v8.0.0 tag, the first real run of this job). Orchestrator adds each to `docs/tasks/active-tasks.md` (`AGENTS.md` § Task Protocol).

- [ ] **C1** (Should Fix 1) - Add the template-shaped-document test and rehearsal; confirm with a dry run on a copy of the v8.0.0 document once it exists. Owner: devops-engineer. Due: before the Release gate for v8.0.0, and in any case before the v8.0.0 tag is pushed.
- [ ] **C2** (Should Fix 2) - Reduce `run_dry_run` to four parameters. Owner: devops-engineer. Due: before the Release gate for v8.0.0.
- [ ] **C3** (Should Fix 3) - Tighten the three `assertRaises(RuntimeError)` assertions. Owner: devops-engineer. Due: before the Release gate for v8.0.0.
- Nice to Have items N1-N5 are optional; the LOW hardening in N3 is recorded as technical debt (owner: devops-engineer, no fixed deadline), not as a gating condition.

No security finding is listed as a condition, so no security remediation plan is required.

### Merge authorization (the change is already merged as `3771781`)

- Merge permitted: Yes, with conditions tracked (retroactive; the merge preceded this review, so the conditions apply to follow-up work).
- Reviewed by: Tech Lead, read-only mode (no source modified; the only files written are this artifact and the T625 brief's Status line).
- Not verified: the full test suite and the gate list in `task-T619.md` section 3; the CI image's git version; the actual tag run (cannot be run before a tag).

[VERDICT] gate=code-review | result=CONDITIONAL_PASS | reviewer=tech-lead | artifact_ref=code-review-t619-v1 (reviewed: merge 3771781, ce0ad52) | date=2026-10-14

## Gate Verdict

**Gate:** implementation
### Verdict: CONDITIONAL_PASS

## VERDICT

- **Status**: CONDITIONAL_PASS
- **Reviewed artifacts**: `scripts/publish-release.py` (after 3771781), `scripts/dry-run-publish-release.py` (new in 3771781), `tests/functional/test_publish_release.py` (after 3771781), `.gitlab-ci.yml` (release job, after 3771781), `docs/tasks/task-T619.md` (as merged), `docs/plans/plan-120-release-v8-readiness.md` (v1, plan row B / T619), `docs/artifacts/security-review-t619-release-job-v1.md` (v1, context only), `docs/plans/plan-121-release-v8-wave-2.md`, `docs/tasks/task-T625.md`
- **Must Fix count**: 0
- **Should Fix count**: 3
- **Nice to Have count**: 5
- **Blocker IDs**: none (not FAIL)
- **Reviewer**: tech-lead
- **Timestamp**: 2026-10-14T19:34:25Z
