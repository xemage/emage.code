# T619 — Make the release job use the single release document and stop writing a third release-notes.md (P32 O6)

**ID:** T619
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-120-release-v8-readiness.md`
- `scripts/publish-release.py` (around `:195-215`), `.gitlab-ci.yml` (`release` job artifacts, around `:193-206`), `scripts/verify-release-docs.py`
- `docs/artifacts/path-conventions-v3.md` §8 (O6) and the user's decision B-1 "One, at docs/releases/ (Recommended)" (one release document, `docs/releases/v<VERSION>.md`)
- `implementation/knowledge/agents/orchestrator.md` § Release Workflow Preflights
- The user's decisions of 2026-10-09 on the release-readiness question (verbatim): "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B" (point numbers refer to the orchestrator's message listing six open points: 1 breaking changes and migration notes = release-level audit and Migration section; 2 release-level gates and sign-offs = the full sequence; 3 CI release job's third release-notes.md = fix first; 4 maturity = the user authorizes evaluator baseline v21 and asks for a re-evaluation plan and the steps to bring `orchestrator` and `tech-lead` out of `experimental`; 5 known residuals = fix all first; 6 plumbing = API fallback plan for branch and tag steps).

## 1. What and why

The CI `release` job (`publish-release.py`) generates `CHANGELOG.md` and a root `release-notes.md` and publishes the GitLab Release. The user decided one release document, `docs/releases/v<VERSION>.md`. The root `release-notes.md` is a third file and is declared as a job artifact. Make the release job consistent with the decision: the GitLab Release description comes from `docs/releases/v<VERSION>.md` (plus the generated changelog section as today), no root `release-notes.md` is written or kept as an artifact, `CHANGELOG.md` is still regenerated. Keep token handling (`WIKI_TOKEN`), the `release-docs-gate` and `main-develop-drift-gate` dependencies and the tag rule unchanged. The job only runs on a tag, so provide a local dry-run (no network, no tag, no push) that exercises the changed code path against a copy of `docs/releases/v7.0.1.md`, and unit tests. Do not create, push or delete any tag or release. Do not change `docs/releases/_template.md` unless a test requires it (report instead).

## 2. Output

The changed script/CI file(s) and tests, a short report with the dry-run output, the gate results, the suite summary line and every deviation. Describe exactly what a real tag run would now do differently.

## 3. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md`, or any brief's Status line. No `.env*` or credential files.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare any root drift in `tests/_baselines/root-install-drift.json` (sorted paths plus one comment line); do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Quote verbatim, mark omissions with "…", and mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. No code path writes a root `release-notes.md`; the CI job no longer lists it as an artifact; `CHANGELOG.md` generation is unchanged.
2. The dry run and the new tests pass; the full suite and all gates pass.
3. A Security Engineer reviews the diff (the orchestrator dispatches it): token handling and any shell/API use are unchanged or stricter.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
