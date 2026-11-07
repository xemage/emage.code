# T747 — Batch T: the verdict check reads the parser's tokens

**ID:** T747
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-06
**Completed:** 2026-11-06
**Based on:**
- `docs/plans/plan-142-verdict-check-tokens.md` (task T747)
- The user's answer of 2026-11-06, verbatim: "T go"
- `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4 (SEC-T739-07)

## 1. What and why

Move the release gate's verdict section finding to `markdown-it-py` tokens, as `docs/plans/plan-142-verdict-check-tokens.md` § Design specifies, so that a visible unfilled verdict cannot pass through a comment, a second heading, a quoted heading or a paired ` ``` `.

## 2. Output

Changes to `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`, committed on `agent/devops-engineer/T747`. No other file changes, unless a test elsewhere must follow; report it if so.

## 3. Constraints

- Work in your own worktree on branch `agent/devops-engineer/T747`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- Mutation runs only as the plan says: a throwaway copy under the scratchpad, a timeout and a memory cap on every run, one at a time, never in a worktree. An uncapped run has already crashed this machine once. No full suite. Put a `timeout` on any test run.
- Token budget: 120k, counting context.

## 4. Acceptance criteria

As in the plan, § Task Decomposition, T747.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
