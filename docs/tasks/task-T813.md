# T813 — Release-level audit of v10.0.0..develop

**ID:** T813
**Owner:** tech-lead
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-161-release-v11.md` (plan-161 § Task Decomposition item 1; § State at writing)
- The user's answers of 2026-11-13 (question dialog, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)"; probe tag "Yes, probe first (Recommended)".

## 1. What and why

As specified in plan-161 § Task Decomposition item 1: wave 1 of the v11.0.0 release, on `develop` before the release branch.

## 2. Output

`docs/artifacts/release-v11-audit-v1.md`.

## 3. Constraints

- Read-only on source: the only file you create is the audit artifact.
- Conventional Commits ending with `Co-Authored-By: Claude <noreply@anthropic.com>`. Do not push, merge, tag or release.
- Do not edit the ledger, any brief's Status line or the plan. No `docker` command.
- Never open `tests/golden/held-out/`; recursive searches over `tests/` need `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, `.env*`, credential files, or the user's `.claude/settings*.json` and `.vscode/*.json`.
- Mark anything not verified **(unverified)**. `timeout` on every command that may hang.

## 4. Acceptance criteria

As in plan-161 § Task Decomposition item 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`). A blocker for the release goes to the orchestrator at once.
