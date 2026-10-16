# Artifact: security-review-t658-server-denials-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell; the `security-audit` grep tool failed again, so full reads and vendor fetches were used; the reviewer read the final tree, not the commit diff; Opencode vendor source spot-checked at v1.19.0 and v2.0.29, Gemini documentation pages read, Gemini source files not re-read). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-15.
- **Target**: T658, commit `79a84b7` on `agent/devops-engineer/T658`: server-level denial of the six excluded Playwright tools (Opencode top-level `permission`, Gemini CLI `excludeTools`), driven from `denyTools` in `servers.yaml`; the new merge rules in `scripts/merge-mcp-json.py`; manifest-load validation of `mcpToolNames`.
- **Based on**: `docs/tasks/task-T658.md`, `docs/artifacts/mcp-server-denials-v1.md`, `docs/artifacts/security-review-t657-tool-name-mapping-v1.md`.
- **Orchestrator checks**: the developer reports 1267 tests OK (skipped 23) and all gates; the orchestrator re-ran the 71 tests of the denial and mapping modules after the documentation edits listed under SEC-T658-03, -04 and -07 (OK).

## Verdict: CONDITIONAL_PASS

0 critical, 0 high, 1 medium (SEC-T658-01, SEC-T657-01 carried and re-scoped), 6 low. No Immutable Security Constraint is breached; no required control is omitted or weakened; no secret or PII. The change only adds a denial. The six denied names equal the six excluded tools exactly (`browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop`, singular `browser_network_request`), spelled as the `@playwright/mcp` v0.0.83 README reports them; the plural `browser_network_requests` is a separate granted tool and is not denied; the intersection of every agent's grant set with the denial list is empty (pinned by a test).

## Do the denials do what is claimed?

According to documentation and source, yes; nothing was observed live.
- **Opencode**: rule order is defaults, then global `permission`, then the agent's own rules, `evaluate` is `findLast`, patterns are anchored, so the global deny holds for every shipped agent (none writes a later conflicting allow). Residual: a user's own agent file, or another config source, that allows one of the names, `playwright_*` or `*` overrides the denial.
- **Gemini CLI**: `excludeTools` on `mcpServers.<name>` takes precedence over `includeTools`; the subagent claim rests on the artifact's source reading alone.
- **Residual**: Cursor has no mechanism; Pi is open for agents with no `mcp__` entry; on Opencode, Gemini and Cursor all other tools of every server (GitLab write tools included) stay open to every agent; `playwright-local` is not covered. SEC-T657-01 therefore keeps MEDIUM.

## Findings

| ID | Grade | OWASP | Location | Finding | Disposition |
|---|---|---|---|---|---|
| SEC-T658-01 | SECURITY:MEDIUM (SEC-T657-01 carried, re-scoped) | A01, A04 | `implementation/.opencode/opencode.json:175-182`; `implementation/.gemini/settings.json:43-50`; Known-issues text | The six-tool denial narrows the exposure only on Opencode and Gemini and only by documentation; Cursor open, Pi partly open, other tools open, `playwright-local` uncovered | C-1: the Known-issues text below replaces the T657 text (owner release-manager, T645, before the release). C-2 (remediation plan): the per-agent `false` form that Opencode documents (the generator owns the agent files and can emit `playwright_*: false` and the GitLab write tools as `false` for roles that do not hold them); research a Cursor mechanism; owner devops-engineer, review tech-lead, after the release unless the user accepts the disclosure |
| SEC-T658-02 | SECURITY:LOW | A04, A05 | artifact `mcp-server-denials-v1.md` §2 ("verified" label); `servers.yaml:58-62` | Both mechanisms never ran live; a Gemini name-format mismatch (for example the fully qualified `mcp_playwright_…` form) would deny nothing silently (fails open without a signal) | Tracked debt; add a one-time manual check to the release checklist (Gemini `/mcp` listing; an Opencode call that is refused); read "verified" as "verified by source, not live" |
| SEC-T658-03 | SECURITY:LOW | A05 | artifact §2.2 and §6.3; wiki | The artifact says a user-level `playwright` entry "wins over the project file"; Gemini ranks the project file above the user file, only the system settings are higher; project settings load only in a trusted workspace (unverified) | Wiki corrected in this MR; the artifact is immutable and is corrected at its next version |
| SEC-T658-04 | SECURITY:LOW | A01 | wiki; `AGENTS.md:116`; `PREREQUISITES.md:33`; merge docstring | "Denial goes last" holds inside one file; Opencode merges several sources, so a `playwright_*: allow` in another source can still follow it (artifact §6.6 lists it; the user-facing docs named only agent files) | Wiki sentence added in this MR; add the same sentence to `AGENTS.md` and `PREREQUISITES.md` at the next edit |
| SEC-T658-05 | SECURITY:LOW | A05, A09 | `scripts/install.sh:1031-1041`; `scripts/merge-mcp-json.py:168-170,192-197` | (a) a plain install without `--update` overwrites an existing `.opencode/opencode.json` or `.gemini/settings.json` wholesale incl. the user's `permission`/`excludeTools` (pre-existing); (b) a config with comments or trailing commas makes `json.load` fail with a traceback after the platform tree was replaced (pre-existing); (c) the override of a user's allow on a generator-owned key is silent; (d) `--projections-only` has no end-to-end test | Tracked debt: one-line stderr note when a user value is replaced, catch `JSONDecodeError` with a clear message, a `--projections-only` end-to-end case, document (a) |
| SEC-T658-06 | SECURITY:LOW | A08 | `tests/functional/test_mcp_server_denials.py:624-648`; `test_mcp_tool_name_mapping.py:332-346` | Doc assertions that cannot fail (a forbidden sentence the old text never contained; whole-file matches that another paragraph satisfies; an unanchored artifact line check; a docstring grep; a loose `>= 12` floor) | Tracked debt: anchor each assertion to the T658 paragraph |
| SEC-T658-07 | SECURITY:LOW | A04 | artifact §2.1; wiki line 80; `sync.mjs:369-370` | (a) "18 distinct granted names" should read 19 (25 default tools minus 6 denied); (b) the comment "stops the run before any file is written" is wrong for `mcpToolNames`, which is validated per manifest inside the write loop | (a) wiki corrected in this MR; (b) tracked debt: validate all manifests before the first write |

## Merge script (`scripts/merge-mcp-json.py:45-82`)

No data-loss or abuse path. `excludeTools` is a union with the user's elements first; top-level `permission` keeps the user's keys, expands a string shorthand to `{"*": s}` and sets the six generated keys last as `deny`; a nested `permission` key is untouched; non-dict/non-list values are replaced; idempotence is tested (every merge twice, shipped files as fixed points, with and without sidecar); the install end-to-end test covers fresh install, a user edit, then `--update` for Opencode and Gemini. A user's allow on one of the six names is overridden by design and documented. The `sync.mjs` validation (`^[A-Za-z0-9_]+$`, non-empty, no duplicates, no wildcard) is linear and runs inside `readServersYaml`; the six names appear only in `servers.yaml`.

## Required Known-issues change (replaces the T657 text from "It is **not in force on Opencode, Gemini CLI and Cursor**…" to the `playwright-local` sentence; the rest is unchanged)

> It is **not in force on Opencode, Gemini CLI and Cursor**, where an agent's tool list does not restrict MCP tools. On Opencode and Gemini CLI the generated configuration denies six tools of the shipped `playwright` server for every agent (`browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop`, `browser_network_request`): on Opencode through top-level `permission` entries, on Gemini CLI through `excludeTools`. This follows the vendor documentation and source and has not been observed in a live run. On Opencode an agent file of the user's own, or another configuration source, that allows one of these names, `playwright_*` or `*` overrides the denial. On Cursor there is no such mechanism: every agent can call every tool of every configured server, including `browser_run_code_unsafe`, `browser_evaluate` and `browser_file_upload`; the same holds on Pi for an agent that lists no `mcp__` tool. On Opencode, Gemini CLI and Cursor every agent can still call all other tools of every configured MCP server, including the GitLab write tools. A user-owned `playwright-local` entry has no origin restriction, is not covered by the denial, and is reachable by every agent on Opencode, Gemini CLI and Cursor.

## Conditions

- C-1: the Known-issues change above (owner release-manager, T645, before the release).
- C-2: the remediation plan under SEC-T658-01 (owner devops-engineer, review tech-lead; after the release unless the user accepts the disclosure).
- Tracked debt: SEC-T658-02 to -07 (next sprint). None blocks the release.

## Limits

L-1 no shell (no test, `sync.mjs --check` or registry check run by the reviewer); L-2 the final tree was read, not the commit diff, HEAD could not be confirmed, `implementation/AGENTS.md` was not read; L-3 Opencode source spot-checked at v1.19.0 and v2.0.29, Gemini source not re-read; L-4 no platform run live by anyone; L-5 held-out files, `.env*` and credential files were not opened.
