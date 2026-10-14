# T640 — Release body = the release document only; commit list to CHANGELOG.md only, merge commits excluded (T632 group C3, code part)

**ID:** T640
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T635
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Addendum 3: T640)
- `docs/artifacts/release-documents-ruling-v1.md` §6.2 and §7.3 (the C3 code specification and filter F1), `docs/artifacts/code-review-t619-v2.md` (conditions C1-C3, N1-N4), `scripts/publish-release.py`, `scripts/dry-run-publish-release.py`, `tests/functional/test_publish_release.py`, `.gitlab-ci.yml`
- The user's answers of 2026-10-15 (AskUserQuestion, verbatim option labels): T632 group A "A1: union contract + fixes (Recommended)", group B "B1: develop, then main, then tag (Recommended)", group C "C3: the document only (Recommended)"; T637: SEC-002 grade "Yes, HIGH for that entry (Recommended)", replacements "Approve all four (Recommended)", pins "Approve the proposed pins (Recommended)", docker and postgresql "Remove both"; ADR-009 "Accept ADR-009 as written (Recommended)".

## 1. What and why

Implement C3 as specified: the GitLab Release description is the release document, whole (starting `# Release vX.Y.Z`, so the title-strip branch is gone or kept consistent with T635's tests); the generated commit list is built with `git log --no-merges --pretty=%s --end-of-options <range>` (filter F1) and goes into `CHANGELOG.md` only; `render_release_description`, `main`, `update_changelog`'s input, the dry run and the tests change accordingly (the PUT path and the template-shaped document are covered by T635's tests: build on them, do not duplicate). Keep: tag validation, `--end-of-options` in every git call, fail-closed on a missing or blank release document, the token handling and API calls unchanged, no new network/shell/write surface, the offline dry run. Never create, push or delete a tag or release; never use or print `WIKI_TOKEN`. Also record the effect on `CHANGELOG.md` group headings (observation O-1 of the ruling) without changing it unless the spec says so.

## 2. Output

The changed script and tests, a short report with the dry-run output (the body is exactly the document; the changelog section lists no merge commits), gate results and the suite summary line.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line; do not edit generated platform folders by hand; no root refresh.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare ALL root drift in `tests/_baselines/root-install-drift.json` (it currently lists the 33 paths of T624 and may list more by the time you start: add, never remove; sorted paths plus one comment line starting "Declared 2026-10-15 by <task> (").
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `docs/tasks/validate-tasks.py`, the evaluator hash (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.

## 4. Acceptance criteria

1. The description equals the release document byte-for-byte; `CHANGELOG.md` gets the filtered commit list; mutation tests fail if either is reverted.
2. All gates and the full suite pass. A Security Engineer reviews the diff (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
