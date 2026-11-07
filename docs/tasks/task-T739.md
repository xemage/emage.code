# T739 — A Markdown parser in the release gate

**ID:** T739
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-05
**Completed:** 2026-11-05
**Based on:**
- `docs/plans/plan-136-release-gate-markdown-parser.md` (task T739)
- The user's answer of 2026-11-05, verbatim: "parser go"
- `docs/artifacts/security-review-t738-batch-n-two-v1.md` § 4; `docs/artifacts/security-review-t730-t732-batch-g-v1.md` § 4 (SEC-T731-08)

## 1. What and why

Replace the hand-written Markdown logic of `has_cursor_migration_item` with `markdown-it-py`, and install it in `release-docs-gate` from a new hash-locked file, as `docs/plans/plan-136-release-gate-markdown-parser.md` § Design and § Task Decomposition specify.

## 2. Output

Committed on `agent/devops-engineer/T739`:
- `scripts/verify-release-docs.py`
- `ci/requirements-release.in`, `ci/requirements-release.txt`, `.gitlab-ci.yml`
- `tests/functional/test_verify_release_docs.py`, `tests/functional/test_ci_hash_pins.py`
- `docs/wiki/mcp-pin-bump-checklist.md`, `CONTRIBUTING.md`

No other file changes, unless a gate requires it; report why.

## 3. Constraints

- Work in your own worktree on branch `agent/devops-engineer/T739`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; pass `--exclude-dir=held-out` to any recursive search over `tests/`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- Max 50-line functions, max 4 parameters. Token budget: 90k.

## 4. Acceptance criteria

As in the plan's task T739, § *Acceptance*.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
