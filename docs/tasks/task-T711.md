# T711 — Publish v9.0.0 (each step needs the user's approval)

**ID:** T711
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T710
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T711)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

Publish (orchestrator; **each step needs the user's explicit approval at that moment**): the B1 order of `CONTRIBUTING.md` (release steps 5 to 7; the user's decision of 2026-10-15 for v8.0.0, "B1: develop, then main, then tag"): MR `release/v9.0.0` to `develop`, then MR `release/v9.0.0` to `main` (both merge commits, PUT-first `squash=false`, `scripts/verify-main-sync-merge.py`), then tag `v9.0.0` on the release-branch tip after checking it is an ancestor of `origin/develop` and `origin/main` with the tree of `origin/main` (corrected 2026-11-01 for TL-T708-01); watch the tag jobs (the first real tag pipeline on `CI_JOB_TOKEN`: user action A-5, SEC-T686-03 and SEC-T686-06 recorded); `docs/checkpoints/checkpoint-040-release-v9.0.0.md`. *Acceptance:* the GitLab Release body equals `docs/releases/v9.0.0.md`; all tag jobs green.

**Conditions from the gates:** observe and record in `checkpoint-040` the items of `docs/artifacts/security-review-release-v9-v1.md` § What T711 must observe (Brave still 2.1.4 and the seven-entry gate command exit 0 before the tag; `release-docs-gate` and `main-develop-drift-gate` pass; SEC-T686-06 runner version and clone method; SEC-T686-03 no job-token value in the `release` log; the Releases API accepts `JOB-TOKEN`; never move, delete or re-create the tag); after the tag re-run `scripts/check-main-develop-drift.py` and expect `releases_behind=0` (QA-T707-03, condition C3 of `qa-gate-release-v9-v1.md`).

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>` (release-manager tasks: on `release/v9.0.0` through the orchestrator); Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
