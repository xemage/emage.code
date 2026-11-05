# T738 — Batch N, two gate fixes (SEC-T731-07, SEC-T731-09(a))

**ID:** T738
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-05
**Completed:** 2026-11-05
**Based on:**
- `docs/plans/plan-135-batch-n-two-gate-fixes.md` (task T738)
- The user's answer of 2026-11-05, verbatim: "N two go"
- `docs/artifacts/security-review-t730-t732-batch-g-v1.md` § 4; `docs/artifacts/tracked-debt-register-v7.md` § 5

## 1. What and why

Fix SEC-T731-07 and SEC-T731-09(a) and correct the two claims, as `docs/plans/plan-135-batch-n-two-gate-fixes.md` § Task Decomposition specifies.

## 2. Output

Changes to `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`, committed on `agent/devops-engineer/T738`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/devops-engineer/T738`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; pass `--exclude-dir=held-out` to any recursive search over `tests/`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- Max 50-line functions, max 4 parameters. Token budget: 50k.

## 4. Acceptance criteria

As in the plan: each new test fails on the old code and passes on the new; reverting either fix makes a test fail; `python3 scripts/verify-release-docs.py --tag v9.0.0` passes on the real tree; all gates and the full suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
