# T656 — Fix the T655 security review findings (SEC-T655-01, -02, -04, -05, -08, -09, -10)

**ID:** T656
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T655
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Outcome note (orchestrator):** Items 2 to 7 done; item 1 (SEC-T655-01 per-tool grants) stopped because the generator has no per-platform tool-name mapping; the user chose "Build the mapping now (T657)" on 2026-10-15.
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 3: T656)
- `docs/artifacts/security-review-t655-fetch-removal-v1.md` (findings table and conditions), `docs/artifacts/fetch-replacement-evaluation-v1.md` (§5.3 on per-tool grants), `implementation/knowledge/mcp/servers.yaml`
- The user's standing decision of 2026-10-09 ("5. C": fix every residual before the release) and the option "A: Remove fetch, harden Playwright (Recommended)" of 2026-10-15.

## 1. What and why

Fix, in this order, what the T655 review lists as fixable in the repository now:
1. **SEC-T655-01**: in `implementation/knowledge/agents/{qa-engineer,frontend-developer,poc-qa-engineer,demo-agent}.md` replace the whole-server grant `mcp__playwright` by named tools: `mcp__playwright__browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_wait_for`, `browser_take_screenshot`, `browser_network_requests`, `browser_close` and the other non-"unsafe" tools these agents actually use (read each agent's body to see which; list `mcp__playwright__<tool>` names, never `browser_run_code_unsafe`). FIRST find out how each of the seven platform generators renders tool names (read `implementation/scripts/sync.mjs` and the generated agent files for an agent that already lists per-tool MCP names such as `mcp__gitlab__*` entries, if any) and test that a per-tool name survives into each projection in a form that platform honours (use the platform's documentation via `npx ctx7@latest` for Copilot, Cursor, Gemini, Opencode, Pi, Cline and Claude Code where the question is how MCP tool names are written in agent tool lists). If a platform cannot express per-tool names, do not ship a half-measure: report which platforms and stop that item (the other items still proceed). Add a test that pins the grant set: exactly those four agents hold `mcp__playwright__*` named tools, none holds the bare `mcp__playwright`, none holds `browser_run_code_unsafe`, and none of the ten former `fetch` agents holds any Playwright tool.
2. **SEC-T655-02**: document in `docs/wiki/mcp-servers.md`, `AGENTS.md`, `implementation/AGENTS.md` and `implementation/PREREQUISITES.md` that the shipped entry blocks local-app URLs (`localhost`, `127.*`, `*.localhost`, `10.*`, `192.168.*`, `172.16-31`) so E2E testing of a local dev server fails with `ERR_BLOCKED_BY_CLIENT`, and describe a documented user-owned second entry (name `playwright-local`, unrestricted, with a clear warning, preserved by `install.sh --update` because the merge keeps names that are not generator-owned; verify that claim against `scripts/merge-mcp-json.py` before writing it).
3. **SEC-T655-04**: `implementation/scripts/sync.mjs` `splitInlineArray` throws on a backslash inside a quoted item and on an unclosed quote; add tests (including one comparing the reader's result with `yaml.safe_load` for every entry of `servers.yaml`).
4. **SEC-T655-05**: `implementation/PREREQUISITES.md` leads with the pinned command `npx -y @playwright/mcp@0.0.83 install-browser chrome-for-testing` (about 670 MB; mention the `--no-shell` figure only for the plain `playwright install chromium --no-shell` route, about 400 MB), and states what is and is not verified about the download.
5. **SEC-T655-08**: say in `PREREQUISITES.md` and the wiki that installed projects should add `.playwright-mcp/` to their `.gitignore` or set `--output-dir` to an ignored path.
6. **SEC-T655-09**: soften "passed without a shell" to what is verified; document the per-key form of `--force-prune-keys` (and that the combined `docker,postgresql,fetch` form refuses when a name is already gone); fix the core and extended server tables in `AGENTS.md`/`implementation/AGENTS.md` (core: add `hindsight`; extended: add `cwso`, `context-retriever`, `security-audit`, `poc-security-audit`) after verifying against `servers.yaml`; add poc-qa-engineer to the Playwright row.
7. **SEC-T655-10**: replace the tautological `test_blocked_origins_expectation_is_complete` assertion by one that compares against the YAML-parsed value; add the `--force-prune-keys fetch` merge-script test.
Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py --root implementation`; update the root-drift baseline (`tests/_baselines/root-install-drift.json`: sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths, one comment line starting `Declared 2026-10-15 by T656 (`); do NOT refresh the root install.

## 2. Output

The edits above, one local commit, a report per item (done or stopped, with the reason).

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates: sync --check, generate-registry --check, check-maturity.py --root implementation, scorecard.py --check, validate-tasks.py, check_evaluator_hash, held-out isolation test, and the full suite `python3 tests/run.py > file` (summary lines).
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not re-run **(unverified)**.

## 4. Acceptance criteria

1. Each item reported done or stopped with the reason; no half-measure grants.
2. The grant-set test fails when a Playwright grant is added to the ten agents or the whole server is re-granted to the four.
3. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
