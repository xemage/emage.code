# Task T328 — Sync + propagate CWSO knowledge to platform projections

**ID:** T328
**Owner:** backend-developer
**Status:** done
**Completed:** 2026-08-06
**Priority:** P1
**Depends on:** T329 (must be PASS or CONDITIONAL_PASS)
**Created:** 2026-08-06
**Based on:** `docs/plans/plan-018-cwso-agent-knowledge-awareness.md`; `Makefile`; `implementation/scripts/sync.mjs`;
`scripts/install.sh`; precedent commit `6d1fca3` ("chore: sync root .claude/ install with T301 tool-projection
fix (v6.4.2)")

## Objective

`implementation/knowledge/` is the single source of truth; per-platform folders (`implementation/.claude/`,
`.github/`, etc.) and this repo's own root-level `.claude/`, `.github/`, `.cursor/`, `.gemini/`, `.opencode/`,
`.pi/` (a self-installed copy of the tool, per the repo's own dogfooding convention — see commit `6d1fca3`)
are GENERATED. Never hand-edit them. Regenerate the `implementation/` mirrors from T327's knowledge-base
changes, then propagate that regeneration into the root-level installed copy so this session's own Claude Code
instance (and other platform tools) actually pick up CWSO awareness.

## Inputs

- T327's committed changes to `implementation/knowledge/skills/cwso-awareness/SKILL.md` and the three agent
  files.
- T329's gate verdict (must not be `FAIL`).

## Constraints

- Do not hand-edit any file under `implementation/.claude/`, `.claude/`, `.github/`, `.cursor/`, `.gemini/`,
  `.opencode/`, `.pi/` — only the two commands below may touch them.
- Do not touch `.vscode/mcp.json`, `deploy/local-dev/`, `docs/deployment/cwso-emage-orchestrator-connection-guide.md`,
  `scripts/mint-cwso-jwt.py` (unrelated uncommitted work already in the working tree — leave untouched,
  do not stage or commit them).
- Run commands from the repo root (`/home/emage/Code/emage/emage.code`).

## Procedure

1. `make sync` — regenerates `implementation/.claude/`, `implementation/.github/`, etc. from
   `implementation/knowledge/`.
2. `make verify` — must exit 0 (no drift between knowledge and generated mirrors).
3. `bash scripts/install.sh --target . --platform all --update` — propagates the regenerated
   `implementation/<platform>/` trees into this repo's own root-level `.claude/`, `.github/`, `.cursor/`,
   `.gemini/`, `.opencode/`, `.pi/` (this repo installs itself onto itself; `--update` is required to write to
   the repo root, and only rewrites the platform-generated directories plus `AGENTS.md`/`CLAUDE.md`/`.mcp.json`
   /docs merges — it does not touch the out-of-scope files listed above).
4. Capture literal evidence:
   - `grep -rl -i cwso .claude/skills .claude/agents` — expect nonzero file list (was zero before T327).
   - `grep -c -i cwso .claude/agents/orchestrator.md .claude/agents/backend-developer.md .claude/agents/devops-engineer.md`
   - `git status --porcelain` — confirm only expected platform dirs + knowledge files changed, and the four
     out-of-scope files remain in their pre-existing state (unstaged, untouched).

## Expected outputs

- Regenerated `implementation/.claude/**` (and sibling implementation platform dirs) reflecting T327's changes.
- Regenerated root `.claude/**` (and sibling root platform dirs) reflecting the same.
- Literal command output captured in this task's Execution notes as the completion evidence.

## Acceptance criteria

1. `make verify` exits 0.
2. `grep -rl -i cwso .claude/skills .claude/agents` returns at least one file path.
3. The out-of-scope uncommitted files (`.vscode/mcp.json`, `deploy/local-dev/`,
   `docs/deployment/cwso-emage-orchestrator-connection-guide.md`, `scripts/mint-cwso-jwt.py`) show no new
   modification caused by this task (their pre-existing uncommitted state, if any, is untouched).

## Blocker protocol

Report blockers as: type + severity + proposed mitigation. Max 2 retries before escalating to the orchestrator.

## Execution notes

Ran `make sync` (511 files written across 6 implementation platform dirs), `make verify` (exit 0, "no drift
across 511 files"), then `bash scripts/install.sh --target . --platform all --update` to propagate the
regenerated `implementation/<platform>/` trees into this repo's self-installed root-level `.claude/`,
`.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/`. Verified `grep -rl -i cwso .claude/skills
.claude/agents` returns `.claude/agents/orchestrator.md`, `.claude/agents/devops-engineer.md`,
`.claude/agents/backend-developer.md`, `.claude/skills/cwso-awareness/SKILL.md` (was zero hits before this
task). `install.sh --update`'s `rsync --delete` on `.claude/` collaterally deleted the locally-maintained,
non-generated `.claude/settings.json` (a Claude Code permissions file, not part of `implementation/.claude/`
source) — restored via `git checkout -- .claude/settings.json` before commit; confirmed content unchanged
from its pre-existing tracked state. The four unrelated uncommitted working-tree files
(`.vscode/mcp.json`, `deploy/local-dev/`, `docs/deployment/cwso-emage-orchestrator-connection-guide.md`,
`scripts/mint-cwso-jwt.py`) were confirmed unmodified by this task via `git status --porcelain` before and
after. Committed as `chore(T328): sync + propagate cwso-awareness to platform projections`.

Outcome: PASS.
