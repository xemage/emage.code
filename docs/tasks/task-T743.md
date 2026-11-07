# T743 — Batch S: the gate script

**ID:** T743
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-06
**Completed:** 2026-11-06
**Based on:**
- `docs/plans/plan-140-batch-s-release-gate.md` (task T743)
- The user's answer of 2026-11-06, verbatim: "S go"
- `docs/artifacts/tracked-debt-register-v9.md` § 3, § 5; `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4; `docs/artifacts/security-review-t738-batch-n-two-v1.md` § 4; `docs/artifacts/security-review-t741-gate-pin-v1.md` § 4

## 1. What and why

Do T743, as `docs/plans/plan-140-batch-s-release-gate.md` § Task Decomposition specifies.

## 2. Output

Changes to `scripts/verify-release-docs.py`, `tests/functional/test_verify_release_docs.py`, `docs/releases/_template.md` and `CONTRIBUTING.md`, committed on `agent/devops-engineer/T743`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/devops-engineer/T743`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Do not read the CWSO repository.
- Follow the plan's mutation rules. Do not run the full suite: the orchestrator does. Do not start Docker or change any running container.
- Fix these ids only. If you find another problem, report it and do not fold it in. Mark anything you did not verify **(unverified)**.
- Token budget: 120k, counting context.

## 4. Acceptance criteria

As in the plan.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
