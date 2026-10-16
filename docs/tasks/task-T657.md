# T657 — Per-platform MCP tool-name mapping and narrowed Playwright grants (SEC-T655-01)

**ID:** T657
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** judgment
**Depends on:** T656
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 4: T657)
- `docs/artifacts/security-review-t655-fetch-removal-v1.md` (SEC-T655-01), `docs/tasks/task-T656.md` and its report (platform findings: Claude Code `mcp__server__tool`, Copilot `server/tool` and `server/*`, Opencode `server_tool` with a glob-capable `tools` map, Gemini `tools: drop`, Cline no agent files, Pi no native MCP, Cursor unverified), `docs/artifacts/fetch-replacement-evaluation-v1.md` §5.3
- The user's decision of 2026-10-15 (AskUserQuestion, verbatim option label): "Build the mapping now (T657)"; the standing decision of 2026-10-09 ("5. C": fix every residual before the release)

## 1. What and why

Close SEC-T655-01. (a) Establish, per platform, from current documentation (`npx ctx7@latest library/docs`, then the vendors' pages with fetch/web if needed; max 3 ctx7 commands per question) how an MCP tool and a whole MCP server are written in an agent's tool list; record each as verified (with source) or unverified in the new artifact `docs/artifacts/mcp-tool-name-mapping-v1.md` (Based on: security-review-t655-fetch-removal-v1.md). (b) Add the mapping to the generator (`implementation/scripts/sync.mjs` and the platform manifests under `implementation/`), source form unchanged (`mcp__<server>__<tool>` and `mcp__<server>`), the rendered form per platform, applied only where the documentation says the current verbatim form is not honoured; an unverified platform keeps its current rendering and is listed in the artifact. Existing shipped lines (`mcp__security-audit__*`, `mcp__poc-security-audit__*`, `mcp__gitlab`, `mcp__playwright`) change only on a platform whose documentation proves the old form was not honoured; list every changed line in the report. (c) Replace the whole-server `mcp__playwright` in `implementation/knowledge/agents/{qa-engineer,frontend-developer,poc-qa-engineer,demo-agent}.md` by named non-"unsafe" tools they use (never `browser_run_code_unsafe`; read each body). (d) Unit tests: the mapping per platform; the grant-set test of T656 (`PlaywrightGrantSetTests`) extended to fail if the bare `mcp__playwright` is re-granted to the four. (e) Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py --root implementation`; update the root-drift baseline (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths, one comment line starting `Declared 2026-10-15 by T657 (`); do NOT refresh the root install. (f) Update the wiki/AGENTS.md statements about the four agents (the Known-issues sentence is dropped only if the narrowing is in force on the platforms where it is verified; state per platform).

## 2. Output

The artifact, the generator change, the narrowed agent files, the tests, one local commit, and a report with the per-platform table.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates: sync --check, generate-registry --check, check-maturity.py --root implementation, scorecard.py --check, validate-tasks.py, check_evaluator_hash, held-out isolation test, and the full suite `python3 tests/run.py > file` (summary lines).
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

1. The artifact lists every platform with verified/unverified status and sources; no guessed mapping.
2. The four agents no longer hold the bare `mcp__playwright` in the sources; the grant-set tests pin that.
3. All gates and the suite pass; every changed shipped line is listed.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
