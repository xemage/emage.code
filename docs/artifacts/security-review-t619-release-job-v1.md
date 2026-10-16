# Artifact: security-review-t619-release-job-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review, re-run after a rate-limit interruption). Recorded by the orchestrator from the reviewer's report.
- **Task**: T619 (plan-120). Reviewed commit `474e948`; the developer then fixed SEC-T619-01..04 in one round (`40d0287`), which the orchestrator verified but the reviewer did not re-read.
- **Date**: 2026-10-14.
- **Orchestrator checks on `40d0287`**: `tests.functional.test_publish_release` 16 tests OK; the offline dry run reports `DRY RUN OK`; `--tag ../../x` is refused; the CI diff is the single removed artifact line `- release-notes.md`; `--end-of-options` precedes the revision in all four git calls. Condition C1 (repo-wide sweep) done by the orchestrator: no live document, script or test depends on a root `release-notes.md` or on the old log line "generated artifacts for"; remaining hits are golden fixtures named `fixture/release-notes.md` (a different file) and historical records.

## Verdict: CONDITIONAL_PASS

0 critical, 0 high, 0 medium, 5 low. The release job on a real tag is unchanged apart from the root `release-notes.md`: same git calls, same API calls and payload, same description text, same token handling. No new shell, network or file-write surface. The dry run is isolated (faked git and API, `urlopen` blocked, `ROOT` redirected, placeholder token, `.invalid` host). The CI change only removes an artifact line; `needs`, the tag rule and the `release-docs-gate` and `main-develop-drift-gate` are unaffected.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| SEC-T619-01 | LOW | The new `if not description.strip()` guard is dead code (the description always starts with a heading). | Fixed in `40d0287`: `load_release_brief` fails closed on an empty or blank release document; tests through `load_release_brief` and `main()`. |
| SEC-T619-02 | LOW | `dry-run-publish-release.py --tag` was not validated (path traversal in the temp copy). | Fixed: the CI tag regex with `fullmatch`, the source path must stay under `docs/releases/`; tests. |
| SEC-T619-03 | LOW | `publish-release.py` did no tag validation of its own; `git log <tag>` had no separator (pre-existing). | Fixed: `validate_tag` at the top of `main()` and in `load_release_brief`; `--end-of-options` before the revision in the git calls; tests. |
| SEC-T619-04 | LOW | The dry-run no-write test was weak and coupled to the real v7.0.1 document. | Fixed: CHANGELOG hash before/after; fixture release document for most tests. |
| SEC-T619-05 | LOW | Pre-existing: the token is passed in argv (`--token "${WIKI_TOKEN}"`). | Tracked debt, not in T619's scope (keep the variable masked and protected; a later task can read it from the environment). |

Cosmetic, unchanged: a release document that starts with `# v7.0.1` instead of `# Release vX.Y.Z` yields a duplicated top heading in the GitLab Release description; no gate or parser reads the posted description. The v8.0.0 document follows the template.
