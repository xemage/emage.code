# T716 — Batch B: release script, tag-tree check and pin audit

**ID:** T716
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-126-batch-b-release-tooling.md` (task T716)
- The user's answer of 2026-11-01, verbatim: "B go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch B rows)

## 1. What and why

(devops-engineer): the release script, the tag-tree check and the pin audit.
   - SEC-T685-01: `scripts/check-release-tag-tree.py` resolves `origin/main` by git's short-name search, so a tag named `origin/main` shadows it. Resolve `refs/remotes/origin/main`, and add a test with such a tag.
   - SEC-T685-02: the unsafe class for subjects in `scripts/publish-release.py` still misses default-ignorable code points (U+180B-180F, U+206A-206F, U+FFF0-FFF8 and others). Use a Unicode category test (`Cc`, `Cf`, `Zl`, `Zp`, `Co`, `Cn`) plus the explicit `Mn`/`Lo` list.
   - SEC-T675-10: Markdown escaping of commit subjects beyond control characters is not traced. Escape the subjects, or show they are already safe in the release body.
   - SEC-T675-08: several release-tooling controls are pinned only by redundant checks, or are untested. List them and add the missing tests.
   - SEC-T686-07: the child-process allowlist in `publish-release.py` passes `GIT_EXEC_PATH`, `GIT_ASKPASS`, `GIT_CONFIG_*` and the proxy variables without a stated reason. State the reason for each, or drop it.
   - SEC-T686-08: Python and the bootstrap differ on the `LC_` name pattern. Make them the same, and add a test.
   - TL-T708-06: `publish-release.py:433-435,463-466` has functions with 5 and 7 parameters (the limit is 4). Reduce them.
   - SEC-T712-05: add tests for `via` cycles and odd `via` shapes to `tests/functional/test_audit_mcp_pins_hardening.py`.
   - D-T710-2: in the release job's `CHANGELOG.md` artifact, `## [Unreleased]` follows the new entry (T706 O-1, K-10). Place the entry below `## [Unreleased]`, as Keep a Changelog orders it, and add a test.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. All gates and the suite pass. `.gitlab-ci.yml`, if changed, still passes the CI lint (`validate_project_ci_lint`).

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test or check that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with a test, or reported with a reason. All gates and the suite pass. `.gitlab-ci.yml`, if changed, still passes the CI lint (`validate_project_ci_lint`).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
