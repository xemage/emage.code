# Artifact: security-review-t635-release-job-conditions-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review, including a reading of git's `revision.c` for v2.43.0). Recorded by the orchestrator from the reviewer's report.
- **Task**: T635 (plan-121 addendum): resolution of the Tech Lead's conditions C1-C3 and the cheap Nice-to-Have items N1-N4 of `code-review-t619-v2.md`. Reviewed commit `48a823b`.
- **Date**: 2026-10-15.
- **Orchestrator checks**: the developer reports 29 tests in `test_publish_release` (was 16), three hand mutations that fail the tests (strip guard, trailing `--`, `chdir`), the default and template-shaped dry runs, all gates and the full suite (1122 tests OK, 23 skipped); the changed-file set is the three files named below (the reviewer could not list it).

## Verdict: PASS

0 critical, 0 high, 0 medium, 4 low. Behaviour for a valid tag is unchanged apart from the trailing `--` on `git log`: same git calls, same API calls, endpoints, payload and description, token only in the `PRIVATE-TOKEN` header and never printed. The new validators fail closed for CI inputs; the dry run stays offline and writes only to a temp directory; the in-memory mutation test cannot reach network or git.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| SEC-T635-01 | LOW (A10/A05) | `validate_api_target` is a prefix check (userinfo, any https host, a port, a query or fragment, trailing control characters pass; control characters later raise `InvalidURL` as an uncaught traceback, with no token in it). | Tracked debt: parse with `urlsplit` and require https, a hostname, no userinfo, no query or fragment, a path ending in `/api/v4`; optionally pin the host to `CI_SERVER_HOST`. |
| SEC-T635-02 | LOW (A10/A02; pre-existing, outside the diff) | `urllib` follows redirects and re-sends `PRIVATE-TOKEN` to the redirect target, including another host or `http://`. | Tracked debt, linked to SEC-T619-05 (token handling): use an opener whose redirect handler refuses. |
| SEC-T635-03 | LOW | In `run_dry_run`, `os.getcwd()` and `os.chdir(work)` run before the `try`; a failure there leaves `sys.argv` and `urlopen` patched (fails safe). | Tracked debt. |
| SEC-T635-04 | LOW (test hygiene) | `write_template_shaped_document` builds a path from a tag without `validate_tag` (only a constant is passed); one `assertIs` is vacuous. | Tracked debt. |

Recommended before the v8.0.0 tag: run the release job's git commands once on the real CI image (a floating `python:3.12-alpine` with an unpinned `apk add git`) or on a `-rc` tag, to confirm `--end-of-options <rev> --`. The default dry run on a copy of the real v8.0.0 document is repeated when that document exists. Note for T640: the real `docs/releases/v7.0.1.md` starts with `# v7.0.1`, so its description carries two titles; the v8.0.0 document follows the template (`# Release v8.0.0`) and is unaffected.
