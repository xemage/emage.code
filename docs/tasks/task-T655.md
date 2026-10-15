# T655 — Remove the fetch server and apply the hardened Playwright entry

**ID:** T655
**Owner:** devops-engineer
**Status:** done
**Status note (orchestrator, 2026-10-15):** The T654 evaluation (`docs/artifacts/fetch-replacement-evaluation-v1.md`) found that Playwright MCP with its own origin flags is not an SSRF-safe replacement for `fetch` (redirects, WebSockets, the unsafe tool are not covered). The user chose, by AskUserQuestion on 2026-10-15, the option "A: Remove fetch, harden Playwright (Recommended)": remove `mcp-fetch-server`; the agents keep using the platform `web` tool and do NOT get Playwright; harden the existing `playwright` entry with the evaluated args; add the browser step to PREREQUISITES and `.playwright-mcp/` to `.gitignore`. Only 10 agents list `mcp__fetch` (not 11): solution-architect, devops-engineer, tech-lead, frontend-developer, security-engineer, feasibility-agent, technology-scout, poc-orchestrator, integration-agent, backend-developer.
**Priority:** P0
**Tier:** standard
**Depends on:** T654
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 2: T654, T655)
- `docs/artifacts/fetch-ssrf-test-t653-v1.md`, `docs/artifacts/security-review-t646-dependency-audit-v1.md` (SEC-T646-01), `implementation/knowledge/mcp/servers.yaml`
- The user's decision of 2026-10-15 (AskUserQuestion, free-text answer to the fetch-fix question, quoted): "Remove the fetch server and replace it by an alternative (i.e Playwright MCP Server (microsoft/playwright-mcp)) which you evaluate first. Replace it before Release"

## 1. What and why

Implement the evaluated replacement after the user has seen the evaluation's recommendation (the orchestrator confirms by recording the recommendation as accepted in this brief's Status note before dispatch): remove the `fetch` entry from `implementation/knowledge/mcp/servers.yaml` and set the `playwright` entry's `args` to the hardened form of the evaluation's recommendation, copied exactly from `docs/artifacts/fetch-replacement-evaluation-v1.md` (`-y @playwright/mcp@0.0.83 --headless --isolated --browser chromium --sandbox --block-service-workers --no-webmcp --blocked-origins <the full list with the brace lists expanded as the artifact gives them>`); check how the installer and the platform MCP-config generators handle a `;`-containing argument and square brackets (quoting/escaping per platform, including the Gemini, Opencode, Pi and Cline formats) and test the generated configs; if `--sandbox` is likely to fail in containers, say so in PREREQUISITES; update the pin-bump policy text and `tests/functional/test_mcp_package_pins.py` if they enumerate the entries; remove `mcp__fetch` from the tool lines of the 10 agents named in the Status note and add NO Playwright tools to them (they keep `web`); update AGENTS.md and wiki/README mentions of the `fetch` server and the core-server counts and tables (7 vs 8 core entries per the T644 report: verify against `servers.yaml`), and `implementation/PREREQUISITES.md` for the browser requirement (Chromium, how to install it with `npx playwright install chromium`, the size, that the first tool call fails without it), `.gitignore` (`.playwright-mcp/`), and the docs that describe the Playwright server (state its limits: origin flags do not cover redirects, WebSockets or `browser_run_code_unsafe`); regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py --root implementation`; declare the root drift in `tests/_baselines/root-install-drift.json` (do NOT refresh the root). Acceptance: all gates and the full suite pass; `grep -r 'mcp-fetch-server\|mcp__fetch' implementation docs/wiki README.md AGENTS.md` shows only historical records (docs/artifacts, docs/releases, docs/checkpoints, docs/tasks, docs/plans); the T642-era version check still passes; a Security Engineer review of the diff follows.

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
