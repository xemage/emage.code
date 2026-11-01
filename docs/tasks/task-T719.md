# T719 — Batch D: knowledge edits without a ruling

**ID:** T719
**Owner:** technical-writer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-127-batch-d-knowledge-and-rulings.md` (task T719)
- The user's answer of 2026-11-01, verbatim: "D go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch D rows; descriptions in v1 to v3)

## 1. What and why

(technical-writer): the knowledge edits that need no ruling. Runs in parallel with T718.
   - RO621-N-3: `implementation/knowledge/agents/scrum-master.md:32,85` omits `priority::critical`, which `gitlab-management` defines.
   - TD-T671-P16: `implementation/knowledge/commands/batch.md:28` declares no character set for `<slug>`. Use the slug rule the repo already uses elsewhere, and cite it.
   - TD-T671-T538: `implementation/knowledge/skills/dependency-graphing/SKILL.md:36-38` colours `in_progress` blue and `in_review` yellow, the reverse of `commands/team-status.md:34-38`. Align the skill to the commands.
   - TD-T671-T554: `implementation/knowledge/commands/discover-skills.md:34`, step 6, merges `packs/installed/` registry entries that no pack format contains. Under ADR-007 this is a command text, so ask whether the edit needs the user, or propose to leave it and say why.
   - SEV-T690-03: the VS Code part of `docs/wiki/mcp-servers.md`. It lacks (unverified) labels for the trust-dialog wording, `type` for stdio and the `code .` recipe, and it does not address multi-root workspaces.
   - *Acceptance:* each item edited, or reported with a reason. The orchestrator runs `sync.mjs`, `generate-registry.py` and all gates.

## 2. Output

The changes or artifacts stated in section 1, and a closing report: per id, done (file:line) or not done (with the reason).

## 3. Constraints

- You have no shell. The orchestrator gives you a worktree path; edit files only inside it. Knowledge edits go under `implementation/knowledge/` only, never in a projection (`.claude/`, `.github/`, `implementation/.<platform>/` and so on). The orchestrator commits, runs `sync.mjs`, `generate-registry.py` and the gates, and merges. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item edited, or reported with a reason. The orchestrator runs `sync.mjs`, `generate-registry.py` and all gates.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
