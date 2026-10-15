# T655 — Remove the fetch server and apply the hardened Playwright entry

**ID:** T655
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Tier:** standard
**Depends on:** T654
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 2: T654, T655)
- `docs/artifacts/fetch-ssrf-test-t653-v1.md`, `docs/artifacts/security-review-t646-dependency-audit-v1.md` (SEC-T646-01), `implementation/knowledge/mcp/servers.yaml`
- The user's decision of 2026-10-15 (AskUserQuestion, free-text answer to the fetch-fix question, quoted): "Remove the fetch server and replace it by an alternative (i.e Playwright MCP Server (microsoft/playwright-mcp)) which you evaluate first. Replace it before Release"

## 1. What and why

Implement the evaluated replacement after the user has seen the evaluation's recommendation (the orchestrator confirms by recording the recommendation as accepted in this brief's Status note before dispatch): remove the `fetch` entry from `implementation/knowledge/mcp/servers.yaml` and set the `playwright` entry's `args` to the evaluated hardened form (pinned version, origin restrictions, isolated/headless as recommended); update the pin-bump policy text and `tests/functional/test_mcp_package_pins.py` if they enumerate the entries; remove `mcp__fetch` from the tool lines of the 11 agents listed in T654 and add the equivalent Playwright tools only where the evaluation says an agent needs them (the Playwright tools are `mcp__playwright`; follow how agents such as qa-engineer list them); update AGENTS.md and wiki/README mentions of the `fetch` server and the core-server counts and tables (7 vs 8 core entries per the T644 report: verify against `servers.yaml`), and `implementation/PREREQUISITES.md` for the browser requirement if the evaluation finds one; regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py --root implementation`; declare the root drift in `tests/_baselines/root-install-drift.json` (do NOT refresh the root). Acceptance: all gates and the full suite pass; `grep -r 'mcp-fetch-server\|mcp__fetch' implementation docs/wiki README.md AGENTS.md` shows only historical records (docs/artifacts, docs/releases, docs/checkpoints, docs/tasks, docs/plans); the T642-era version check still passes; a Security Engineer review of the diff follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before the commit. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.
- Loopback-only tests; the only other network use is the npm registry and the browser download CDN. Mark anything you did not re-run **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
