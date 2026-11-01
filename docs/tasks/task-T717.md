# T717 — Batch B: release cases in CONTRIBUTING.md

**ID:** T717
**Owner:** technical-writer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-126-batch-b-release-tooling.md` (task T717)
- The user's answer of 2026-11-01, verbatim: "B go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch B rows)

## 1. What and why

(technical-writer): SEC-T685-03, documentation part. `CONTRIBUTING.md` is silent on three release cases: pre-release tags, the retag procedure, and a hotfix during a release. Document them, consistent with the B1 order (CONTRIBUTING steps 5-7) and with `docs/wiki/` where it covers releases. Retagging is a destructive operation and needs the user's approval; say so. *Acceptance:* the three cases are documented. Each statement matches the scripts (`check-release-tag-tree.py`, `verify-main-sync-merge.py`, `publish-release.py`) or is marked **(unverified)**. The orchestrator runs the gates.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test or check that shows it) or not fixed (with the reason).

## 3. Constraints

- You have no shell. The orchestrator gives you a worktree path; edit files only inside it, and only `CONTRIBUTING.md` (plus a `docs/wiki/` page if it needs a pointer). The orchestrator commits, runs the gates and merges. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`. Never read any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

The three cases are documented. Each statement matches the scripts (`check-release-tag-tree.py`, `verify-main-sync-merge.py`, `publish-release.py`) or is marked **(unverified)**. The orchestrator runs the gates.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
