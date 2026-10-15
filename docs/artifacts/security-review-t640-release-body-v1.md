# Artifact: security-review-t640-release-body-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review of the three files at the branch tip). Recorded by the orchestrator from the reviewer's report.
- **Task**: T640 (plan-121 addendum 3): T632 group C3, code part. Reviewed commit `4aeb65f`.
- **Date**: 2026-10-15.
- **Orchestrator checks**: the developer reports 37 tests in `test_publish_release` (all pass), all gates, and the full suite (1163 tests OK, 23 skipped); the orchestrator re-ran the 37 tests and the `--template-shaped` dry run on the branch (OK) and read the diff of `scripts/publish-release.py`.

## Verdict: PASS

0 critical, 0 high, 0 medium, 4 low. The description is the release document byte-for-byte and travels only as a JSON body; it is never interpolated into a URL or shell. Tag validation (`fullmatch`), `--end-of-options` in every git call, `validate_api_target`, fail-closed document loading and token handling are intact. Document content no longer reaches `CHANGELOG.md`. The dry run and the mutation tests write only to temp directories.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| SEC-T640-01 | LOW (A03/A05; pre-existing path) | `load_release_brief` follows a symlinked `docs/releases/<tag>.md` (the dry run's `resolve_release_source` refuses one that leaves the directory). The `verify-release-docs.py` gate (Install, Highlights, RELEASE VERDICT, `Latest release:`) masks most of it. | Tracked debt: add `is_symlink()` or `resolve().is_relative_to(docs/releases)`. |
| SEC-T640-02 | LOW (A05) | Strict `decode("utf-8")` raises `UnicodeDecodeError`, which `main` does not catch: fails closed with a traceback, no token. | Tracked debt: wrap and raise `ReleasePublishError`. |
| SEC-T640-03 | LOW (A03) | Commit subjects and `previous_tag` enter `CHANGELOG.md` verbatim as markdown (links, HTML, unterminated fence); no heading injection found. `previous_tag` is not checked against `TAG_RE`. The file is a job artifact. | Tracked debt: filter `get_tag_list` through `TAG_RE`; optionally escape subjects. |
| SEC-T640-04 | LOW (A10/A02; pre-existing, unchanged) | Host not allowlisted, redirects keep `PRIVATE-TOKEN`, token in argv. Same item as SEC-T635-01/02 and SEC-T619-05. | Tracked debt, merged with those items. |

Informational: no size cap on the document (GitLab rejects an oversized body and the request fails closed); a range with only merge commits now fails with "no commits found"; legacy documents that start `# v6.0.10` are published as stored (no `# Release <tag>` title added), by C3.

Limits: the reviewer had no shell (tests and dry run not run by the reviewer) and `grep_content` failed on every call; held-out and `.env*` files not opened.
