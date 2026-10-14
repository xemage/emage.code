# T638 — Apply the approved MCP server package fixes: corrected and pinned entries, docker and postgresql removed (audit SEC-002)

**ID:** T638
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Addendum 3: T638)
- `docs/artifacts/mcp-server-packages-v1.md` (the single spec: §9 decisions, the exact YAML, the soaked fallbacks, the per-projection impact) and `docs/artifacts/security-review-release-v8-v1.md` (SEC-002)
- `implementation/knowledge/mcp/servers.yaml` (source of truth), `implementation/scripts/sync.mjs` (generator), `tests/functional/test_audit_server.py` (`test_other_entries_untouched_sample`), `implementation/PREREQUISITES.md`, `scripts/merge-mcp-json.py`
- The user's answers of 2026-10-15 (AskUserQuestion, verbatim option labels): T632 group A "A1: union contract + fixes (Recommended)", group B "B1: develop, then main, then tag (Recommended)", group C "C3: the document only (Recommended)"; T637: SEC-002 grade "Yes, HIGH for that entry (Recommended)", replacements "Approve all four (Recommended)", pins "Approve the proposed pins (Recommended)", docker and postgresql "Remove both"; ADR-009 "Accept ADR-009 as written (Recommended)".

## 1. What and why

Apply, exactly as the research artifact proposes and the user approved: (1) replace the four nonexistent entries by stdio entries: `filesystem` -> `npx -y @modelcontextprotocol/server-filesystem@1.0.0 .`; `git` -> `uvx mcp-server-git@2026.10.10 --repository .`; `supabase` -> `npx -y @supabase/mcp-server-supabase@0.13.0 --read-only` with `SUPABASE_ACCESS_TOKEN` in env (secret, fromEnv); `github` -> `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server@sha256:<the digest in the artifact>` with the token in env; (2) pin every remaining npx entry to the approved exact versions (`@zereight/mcp-gitlab@2.2.5`, `@playwright/mcp@0.0.83`, `mcp-fetch-server@1.1.2`, `@modelcontextprotocol/server-memory@1.0.0`, `@modelcontextprotocol/server-sequential-thinking@1.0.0`, `@brave/brave-search-mcp-server@2.1.4`, `toolradar-mcp@2.1.0`) and keep `-y`; (3) REMOVE the `docker` and `postgresql` entries (user decision). Edit `servers.yaml` only, then run the generator so every platform projection follows; update `test_other_entries_untouched_sample` and any other test that asserts the old names, update `implementation/PREREQUISITES.md` (uv for `git`, Docker for `github`; remove what no longer applies), and re-verify each pinned version still exists at execution time (`npm view <pkg>@<ver> version`, `uvx`/PyPI JSON) and that the container digest resolves (anonymous manifest request); if a pinned version no longer resolves, use the artifact's fallback and report it. Do not install or run any package. Because `merge-mcp-json.py` keeps dest-only keys inside a surviving server object and never prunes removed servers on its own, write in your report the exact adopter-facing migration note (what existing v7.x installs must do after `--update`: for example remove the stale `docker`, `postgresql`, `filesystem`, `git`, `supabase`, `github` server objects from their MCP config, or run the prune option the script offers; verify what the script really does before you write it). Drift: all projected MCP configs under every platform change (the artifact counts up to 14 JSON files plus the provenance sidecars); declare them.

## 2. Output

The changed `servers.yaml`, regenerated projections, updated tests and `PREREQUISITES.md`, the drift baseline, and a report with the version-resolution evidence, the adopter migration note, gate results and the suite summary line.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line; do not edit generated platform folders by hand; no root refresh.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare ALL root drift in `tests/_baselines/root-install-drift.json` (it currently lists the 33 paths of T624 and may list more by the time you start: add, never remove; sorted paths plus one comment line starting "Declared 2026-10-15 by <task> (").
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `docs/tasks/validate-tasks.py`, the evaluator hash (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.

## 4. Acceptance criteria

1. The generated configs contain exactly the approved entries and pins; no `@anthropic/mcp-filesystem`, `@github/mcp-github`, `@modelcontextprotocol/mcp-git`, `@supabase/mcp`, `docker-mcp` or `postgres-mcp` remains in any projection.
2. All gates and the full suite pass; root drift declared; no root refresh.
3. A Security Engineer reviews the diff (the orchestrator dispatches it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
