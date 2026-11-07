# T720 — Batch D: apply the T718 rulings and ADR-011

**ID:** T720
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T718
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-127-batch-d-knowledge-and-rulings.md` (task T720)
- The user's answer of 2026-11-01, verbatim: "D go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch D rows; descriptions in v1 to v3)

## 1. What and why

(technical-writer): apply the T718 rulings, and ADR-011 once the user has decided. Also update § Known gaps of `docs/wiki/severity-and-grade-scales.md`. Depends on T718 and on the user's decisions on TD-T713-01 and the SEC-T693-04 command part. *Acceptance:* the text matches each ruling exactly, and every place ADR-011 names is changed or left as ruled.

## 2. Output

The changes or artifacts stated in section 1, and a closing report: per id, done (file:line) or not done (with the reason).

## 3. Constraints

- You have no shell. The orchestrator gives you a worktree path; edit files only inside it. Knowledge edits go under `implementation/knowledge/` only, never in a projection (`.claude/`, `.github/`, `implementation/.<platform>/` and so on). The orchestrator commits, runs `sync.mjs`, `generate-registry.py` and the gates, and merges. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

The text matches each ruling exactly, and every place ADR-011 names is changed or left as ruled.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
