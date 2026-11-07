# T735 — Batch H, knowledge edits

**ID:** T735
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T734
**Affects:** —
**Created:** 2026-11-04
**Completed:** 2026-11-04
**Based on:**
- `docs/plans/plan-133-batch-h-release-gate-text.md` (task T735)
- The user's answer of 2026-11-04, verbatim: "H go"
- `docs/artifacts/security-review-t718-t720-batch-d-v1.md` § 3; `docs/decisions/ADR-012-medium-acceptance-record.md`

## 1. What and why

Make the edits in plan-133 § Task Decomposition item 2, and B1 to B3 of ADR-012, under `implementation/knowledge/` only. You have no shell: the orchestrator commits your work and runs the gates.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree on branch `agent/technical-writer/T735`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never edit `tests/golden/**` or `scripts/scorecard.py`: the user's grant for this batch covers four remarks that are already fixed, and no others (`docs/artifacts/protected-paths-v1.md`). Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each edit is made as written, or reported with the reason. No file outside `implementation/knowledge/` changes.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
