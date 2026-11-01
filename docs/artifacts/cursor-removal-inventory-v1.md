# Artifact: cursor-removal-inventory-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T661 (plan-123): inventory of everything that exists because of Cursor platform support, as input to ADR-010 (drop Cursor support completely, the user's decision of 2026-10-16: "I want to drop Cursor support completely").
- **Author**: a read-only search agent (method: `git ls-files` and `git grep -i cursor` with `:!tests/golden/held-out` and `:!.git`, binaries skipped); recorded by the orchestrator. Nothing under `tests/golden/held-out/` was opened or listed; no `.env*` or credential file and no `.claude/settings*.json` / `.vscode/mcp.json` was read; no test, installer or generator was run (section 10 is from reading the code only).
- **Target**: `develop` at `6b0f8f2`.
- **Based on**: `docs/plans/plan-123-post-release-follow-ups.md` (T661, T662), `docs/releases/v8.0.0.md`.

## Totals

- Cursor-only tracked files: **182** (91 under `.cursor/`, 91 under `implementation/.cursor/`). Other dedicated files: `implementation/platforms/cursor.json` (1) and `docs/archiv/cursor-chats/*.md` (3; exports of Cursor IDE chats from the project's authoring history, not platform support).
- Other tracked files containing "cursor" (case-insensitive): **339**, of which 15 are false positives (`implementation/runtime/memory/chunker.py` a variable; `tests/eval/memory_retrieval/labeled_dataset.py` pagination; `tests/fixtures/mcp-schemas/gemini-cli-settings.schema.json` an editor enum; one golden fixture plan "real-time cursors"; 11 `ux-designer` agent files whose only hit is CSS `cursor: not-allowed`) and **324** genuine:

| Group | Files |
|---|---|
| Historical records (do not edit) | 207 (docs/tasks 108, docs/releases 32, docs/artifacts 38, docs/plans 21, docs/checkpoints 4, docs/decisions 1, docs/archiv 3) |
| Live docs and templates | 20 |
| Knowledge source | 7 |
| Generated mirrors of knowledge text on the other 6 platforms (root and `implementation/`) | 54 |
| Code and config | 8 |
| Tests outside golden | 20 |
| Golden/open | 8 (in 4 cases) |

No `.mdc` file exists outside `.cursor/` and `implementation/.cursor/`; no `cursor-setup` wiki page exists; `.gitlab-ci.yml` has no cursor mention.

## 1. Source of truth

- `implementation/platforms/cursor.json`: `outputDir .cursor`; `fileMap` agents, commands and instructions use `.mdc` (instructions to `rules/`); instruction frontmatter `renameKeys {applyTo -> globs}`, `keepKeys [description, globs]`; agents `mcpToolNames: "verbatim"` and tools as an array; commands keep `description`, `agent`, `argument-hint`; `mcp` tags core and extended, `outputFile mcp.json`, `format: "cursor"`; its `$schema` points to `./_manifest.schema.json`, which is not tracked (a dangling reference).
- **`implementation/platforms/pi.json:31` also sets `"mcp.format": "cursor"`**: Pi reuses the `cursor` MCP branch of `emitMcp` verbatim (cited by tests and `docs/artifacts/mcp-header-url-templating-design-v1/v2.md`). The format value cannot simply be deleted; it must be renamed or re-homed because Pi depends on it.
- `implementation/scripts/sync.mjs` is manifest-driven (`main()` reads every `platforms/*.json` not starting with `_`), so deleting `cursor.json` stops Cursor generation. Cursor-specific code: `emitMcp` lines 456-474 (`format === 'vscode' || 'cursor'`, the `mcpServers` wrapper, `url` with no `type`, `${env:VAR}`); the comment at 574-575 names cursor. The `mcpToolNames` style `verbatim` is shared with Claude Code; the `applyTo` rename is generic. No `.mdc` or `globs` special-casing besides the manifest.
- `implementation/scripts/generate-registry.py:119` has the fallback `["github","gemini","opencode","cursor"]` when `platforms/` is missing (otherwise it uses the `platforms/*.json` stems). `implementation/registry/package.schema.json:23` has the enum `["github","gemini","opencode","cursor"]` for `supportedPlatforms` (already stale: it lacks pi, claude-code and cline); used by `scripts/package.py`, `check.py:589` and `tests/fixtures/packs/sample-pack/pack.json:9`.
- `implementation/knowledge/schemas/*.json` do not mention platforms or cursor; `sync.sh`, `sync.ps1`, `verify.mjs`, `verify.sh` have no cursor code; knowledge instruction frontmatter uses the neutral `applyTo` (no `globs` or `alwaysApply`).

## 2. Generated trees

- Root `.cursor/` and `implementation/.cursor/`: 91 files each: agents/*.mdc 28, commands/*.mdc 19, rules/*.mdc 6, skills/ 35 (SKILL.md, references, pipeline templates), plus `.generated-manifest.json`, `mcp.json`, `mcp.json.provenance.json`. `.generated-manifest.json` has `platform: "cursor"` and a `files` list of 90 entries.
- `.cursor/mcp.json` (both trees): top-level `mcpServers`, 17 servers; placeholders `${env:VAR}`; remote servers `{url[, headers]}` with no `type`; the root file differs from the `implementation/` file only in key order (merged output). The provenance sidecar is `{schemaVersion:1, generatorOwnedKeys:[17 names]}`.

## 3. Installer

- `scripts/install.sh`: usage line 18 (`--platform cursor | github | ... | all`) and example line 50; line 217 comment (the T559 self-install case `--target implementation/.cursor`); `platform_managed_paths` line 358 (`cursor) .cursor .cursor/mcp.json .cursor/mcp.json.provenance.json`); the `all` expansion in `list_managed_paths` line 405 (`for p in cursor github gemini opencode pi claude-code cline`); `validate_before_update` line 974 loop over `.github .cursor .gemini ...` with the exception text at 978 ("except .cursor/mcp.json, which is merged, not overwritten") and the warning at 986; `install_cursor()` lines 1148-1151 (`install_tree_into implementation/.cursor -> $TARGET/.cursor` with excludes `mcp.json` and `mcp.json.provenance.json`, then `merge_or_copy_mcp_json`); the dispatch `case` line 1189 (`cursor) install_common; install_cursor`); `all` calls `install_cursor` at line 1198 and is the default platform; an unknown platform prints "unknown platform" and exits 1 (line 1207).
- `scripts/render_installed_agents.py`: `PLATFORM_MAP["cursor"]` lines 19-24 (skills `.cursor/skills/`, standards and security `.cursor/rules/*.mdc`, mcp `.cursor/mcp.json`); the `--platform` argparse choices at line 162; the `all` branch iterates `PLATFORM_MAP`, so the root `AGENTS.md` lists cursor paths.
- `scripts/merge-mcp-json.py` and `scripts/merge-task-docs.py` have no cursor branch (generic). Makefile line 12 (comment `PLATFORM=cursor`) and line 13 (usage list).

## 4. Tests outside golden (20 files)

`tests/_baselines/root-install-drift.json` (`drift: []`; prose comment entries mention Cursor on lines 35, 41, 44, 45); `tests/fixtures/packs/sample-pack/pack.json:9` (supportedPlatforms includes `cursor`); `functional/test_manifests.py:18` (required manifests list includes `cursor`); `functional/test_mcp_platform_conformance.py` (line 73 `"cursor"` lambda over `mcpServers`; lines 137 and 190 **hard-coded 7 manifests**; lines 237-251 the cursor manifest is used for a regression injection); `functional/test_platform_projections.py` 406-434 (cursor and pi remote-server shape and `${env:VAR}`; pi's format is literally "cursor"); `functional/test_mcp_tool_name_mapping.py` (line 37 cursor "verbatim"; line 203 `.cursor/agents/fx.mdc`; line 327 the artifact must name "Cursor"); `functional/test_mcp_server_denials.py` (lines 65, 160, 334 cursor in platform tuples; lines 605-648 DocumentationTests require `(?i)cursor` in `docs/wiki/mcp-servers.md`, `implementation/PREREQUISITES.md`, `AGENTS.md`, `implementation/AGENTS.md` and in the artifact `mcp-server-denials-v1.md`); `functional/test_mcp_package_pins.py` (lines 35, 70, 401 `.cursor/mcp.json` list; 368 `.cursor/agents/*.mdc` glob; 509 `.cursor` to `.mdc`, `mcp__gitlab__`); `functional/test_mcp_secret_guard.py` (82, 89, 280); `functional/test_placeholder_flag_text.py:26` (pins `.cursor/agents/poc-security-engineer.mdc`); `functional/test_context_retriever.py:319-323` (`resolve_platform(.cursor)` returns "cursor"); `functional/test_root_install_parity.py` (docstring line 3 "eight platform trees"; line 162 requires `.cursor` in the parsed install.sh trees; lines 243-246 `.cursor/mcp.json(.provenance.json)`); `functional/test_install_script.py` (20 mentions: 357-415 `test_cursor_mcp_json_merge_on_update`; 797-801 sidecar prune for cursor; 1398-1413 symlink scenarios; 1474-1505 sentinel `.cursor/rules/coding-standards.mdc`; 1555, 1595); `functional/test_install_agents_mapping.py` 32-39, 55 (`test_cursor_install_rewrites_agents_paths`); `functional/test_install_projections_only.py` 35, 85, 338; `functional/test_install_target_inside_repo.py` 11-12, 89; `functional/test_install_type_conflicts.py` 39, 105-154; `functional/test_link_integrity.py:35` (skips `.cursor` among the mirror dirs); `functional/test_mcp_schema_validation.py:23` (docstring); `functional/test_publish_release.py` 302-307 (sample release body with an "# Cursor" install line, fixture text); `functional/test_check_version_consistency.py` 399-403 (handles `release-manager.mdc` basenames and the `.mdc` suffix when scanning mirrors).
- Count-sensitive spots that break even if only the manifest is deleted: `test_mcp_platform_conformance.py` (7 manifests), `test_manifests.py`, `test_root_install_parity.py` (the `.cursor` tree). The tests that pin Cursor wording in the artifacts `mcp-server-denials-v1.md` and `mcp-tool-name-mapping-v1.md` mean editing those artifacts needs matching test edits.

## 5. Golden suite (protected paths)

- `tests/golden/` outside held-out holds `README.md`, `_manifest-t411.md`, `_example-scaffold/` (4 files; none mention cursor) and `open/` with 28 case directories.
- Files that mention Cursor, 8 in 4 cases: `discover-skills-registry-grounded-recommendation` (`brief.md` lines 23 and 71 quote the knowledge command text listing `.cursor`; **`expect.py:45` has `PLATFORM_DIRS` including `.cursor`**: behavioural, the evaluator scans the platform directories; `fixture/implementation/registry/index.json` has 159 matching lines); `skillify-skill-file-template-drift` (`brief.md` lines 24 and 89 list the platform folders; **`expect.py` lines 17 and 66 pin the `.cursor/skills` path**); `plan-task-creation-precondition-real` (fixture `plan-030-mcp-remote-transport-alignment.md` lines 35, 36, 108 and `task-T365.md` lines 66, 95, 211, 216, 238); `prepare-release-real-verdict-missing` (`fixture/docs/releases/v7.0.1.md:12`, a fixture copy of the install table). No `.cursor` path or `.mdc` file exists in any golden case. Any edit to these needs a grant (G-3) and a later baseline (v23), as plan-123 states; whether a golden change is actually required is for ADR-010 to decide (the `expect.py` files scan or pin `.cursor` paths but may still pass when `.cursor` is absent; verify before concluding).
- Note: T668 (grant G-2) modifies `skillify-skill-file-template-drift` and `prepare-release-real-verdict-missing` first; their `expect.py` files are unchanged.

## 6. Docs

- `README.md` (11 hit lines: 35, 60 the platform table row `Cursor | .cursor/ | .mdc, applyTo -> globs, mcp.json`, 79, 84 the `--platform` table, 93, 98, 102, 103, 111, 159, 352); `AGENTS.md` (60, 74, 80, 88, 93, 97, 102, 116, 118; the root file is rendered by `render_installed_agents.py` from the `all` branch; lines 116 and 118 pinned by `test_mcp_server_denials.py`); `implementation/AGENTS.md` (88, 102, 116, 118); `implementation/README.md` (13, 14, 20, 36, 51, 81); `implementation/PREREQUISITES.md` (32, 33, 55 "Cursor 0.42+"); `implementation/SECURITY.md:25`; `CONTRIBUTING.md` (20, 68, 116 which says to use `cursor.json` as the template for new platforms, 139 which names `pi.json` reusing the `cursor` branch).
- `docs/wiki` (8 pages): `architecture.md` 39, 45; `cline-setup.md:34`; `contributing-workflow.md:63` (a link to `cursor.json`); `home.md:9`; `implementation-guide.md` 22, 28, 36, 43; `instructions-overview.md` 11, 36; `mcp-servers.md` (21 lines: 15, 64-100 denial and tool-name tables with Cursor "none" rows at 76 and 97, 176, 185, 256-257 Pi "keep the Cursor-format assumption", 283, 335-344 the manual Cursor check); `quick-start.md` 12, 17, 25, 30, 33, 38, 50, 97.
- `docs/releases/_template.md:23` has the install row `| Cursor | cursor |`; no cursor line in `verify-release-docs.py`, `publish-release.py` or `check-version-consistency.py`; the release-workflow, prepare-release and release-manager knowledge text has no cursor mention.
- Historical, do not edit: `docs/releases/` (33 files v3.0.0 to v8.0.0; v8.0.0.md has 12 lines: 21, 80, 81, 84, 153, 154, 157, 161, 238, 239, 262, 301), `docs/artifacts` (38 files; largest `mcp-platform-contract-v2` 16, `mcp-header-url-templating-design-v2` 10, `mcp-platform-contract-v1` 13, `scoped-execution-primitive-v1` 9), `docs/plans` (21), `docs/checkpoints` (4), `docs/decisions` (1: `ADR-002-mcp-merge-provenance-tracking.md`, 6 mentions), `docs/tasks` (108), `docs/archiv/cursor-chats/` (3).

## 7. Registry and metadata

- `implementation/registry/index.json`: the `platforms` array includes `cursor` (line 8); 80 entries each carry `cursor` in `supportedPlatforms` and `projectionStatus` (161 matching lines); produced by `generate-registry.py` from the `platforms/*.json` stems, so regenerating after removing `cursor.json` drops it. `registry/schema.json` holds no platform enum; `registry/summary.md` does not mention cursor.
- Platform counts in live text: `test_mcp_platform_conformance.py:137, 190` ("exactly 7"); `docs/wiki/mcp-servers.md:275` ("all 7 platforms"); `implementation/knowledge/agents/context-retriever.md:30` ("other 6 platforms") and `implementation/knowledge/commands/skillify.md:50` ("other six platforms"), both mirrored across the generated platform trees; `test_root_install_parity.py:3` ("eight platform trees"; `.clinerules` counts as the eighth); golden `discover-skills` `brief.md:71` and skillify `expect.py` ("seven platform"); many historical artifacts say "7 platforms" and "8 platforms"; `AGENTS.md:102` lists `cursor` in the `extended` row.

## 8. CI and scripts

`.gitlab-ci.yml` has no cursor mention (jobs: `verify-knowledge-drift`, `validation-super-gate`, `sync-no-diff`, generic). `check-version-consistency.py`, `verify-release-docs.py`, `publish-release.py` and `implementation/scripts/check.py` do not mention cursor. `.gitlab/issue_templates/Bug.md:16` lists `Cursor` in the platform comment; `.gitlab/merge_request_templates/Default.md:30` lists `.cursor/` among the generated dirs; `.gitignore:96` has `.cursor-tutor/` (generic, unrelated to the projection); `Makefile` lines 12-13.

## 9. Knowledge text

Seven genuine files list `.cursor/` among the platform directories: `implementation/knowledge/README.md:3` (lists only `.github .gemini .opencode .cursor .pi`, already stale), `commands/consolidate-memory.md:35`, `commands/discover-skills.md:18`, `commands/skillify.md:38`, `skills/memory-management/SKILL.md:43`, `skills/skillify/SKILL.md:31`, `mcp/servers.yaml` lines 7 (`.cursor/mcp.json` as an output) and 60 (a comment "Cursor has no such mechanism and stays open"). Each of those (except servers.yaml and README) is mirrored in the 5 platforms' trees that carry commands/skills and in the `.cline` skills, at root and under `implementation/`: 54 mirror files. No instruction file carries cursor-specific frontmatter; no agent or skill depends on Cursor behaviour.

## 10. What a user with an existing Cursor install experiences (from reading `install.sh`)

| Situation | Behaviour today |
|---|---|
| `install.sh --update --platform cursor` or `all` into a project with `.cursor/` | Requires an existing install (`$TARGET/AGENTS.md`, line 918). Prints a warning that it replaces `$TARGET/.cursor` entirely via `rsync --delete`, except `mcp.json`. Runs `rsync -a --delete --exclude=mcp.json --exclude=mcp.json.provenance.json implementation/.cursor/ -> $TARGET/.cursor/` (lines 781-790), or an rm/copy fallback without rsync |
| User-added files in `.cursor/` (own rules, `cli.json`, hooks, commands) | **Deleted** by the sweep, since they have no counterpart in the source |
| `.cursor/mcp.json` | Excluded from the sweep, then `merge_or_copy_mcp_json` (line 1024) calls `merge-mcp-json.py --source implementation/.cursor/mcp.json --dest $TARGET/.cursor/mcp.json --old-sidecar ... --new-sidecar ...`. Generated values win; user-only servers and keys are kept; a server key in the old sidecar's `generatorOwnedKeys` but not the new one is pruned (the ADR-002 rule); with no sidecar nothing is pruned; the sidecar is refreshed |
| Fresh install (no `--update`) | `cp -r` and plain copies of `mcp.json` and its sidecar |
| `--projections-only` | Same tree and MCP handling, never touches `docs/` or `implementation/` |
| Symlink at `.cursor` or `.cursor/mcp.json` | Refused before any write (guard via `platform_managed_paths`) |
| **After Cursor is removed from the installer** | `--platform cursor` hits the "unknown platform" branch, exit 1. `--update` with `all` no longer lists `.cursor`. The existing `.cursor/` is **left untouched and stale** (not removed; `mcp.json` is no longer refreshed or pruned); the warning at line 974 would no longer name it. Whether to delete it with a notice or leave it is the open ADR question |

## 11. Residual risks tied to Cursor (release document)

`docs/releases/v8.0.0.md`: **K-15** (line 238; the Playwright narrowing is not in force on Opencode, Gemini CLI and Cursor; the Cursor CLI `permissions.deny` with `Mcp(server:tool)` is documented but not tested and not shipped; a user-owned `playwright-local` entry is reachable by every agent), **K-16** (line 239; the narrowed GitLab grants are not in force on Cursor), **SEC-T658-01** (lines 262, 301; MEDIUM; the user accepted the unfixable remainder on 2026-10-15, including "Cursor IDE has no documented deny mechanism"; the fixable "Cursor CLI deny list" is superseded by plan-123), **SEC-T657-01**, **SEC-T657-03** and **SEC-T650-02** (LOW). Dropping Cursor makes K-15's Cursor part, the SEC-T658-01 remainder and SEC-T650-02 disappear. An inconsistency in the v8.0.0 text: line 157 says "Cursor and Cline render no agent MCP list", while the generated `.cursor/agents/*.mdc` files do carry `tools: [..., mcp__playwright__..., mcp__gitlab__...]`. Security-review artifacts that mention cursor: `security-review-release-v8-v2.md`, `-t657-tool-name-mapping-v1.md`, `-t658-server-denials-v1.md`, `-t660-gitlab-grants-v1.md`. Related artifacts: `mcp-server-denials-v1.md`, `mcp-tool-name-mapping-v1.md`, `mcp-platform-contract-v1.md` and `-v2.md`, `poc-security-engineer-tool-scoping-v1.md` and `-v2.md`, `security-engineer-audit-server-design-v1.md`, `release-v8-audit-v1.md` and `-v2.md`. Versioning rule: `CONTRIBUTING.md:148` and `implementation/knowledge/skills/release-workflow/SKILL.md:23-35` define semantic versioning with a MAJOR bump for breaking changes and a required migration guide (line 120).

## 12. Not checked

No test, installer or generator was run. Git history was not examined (the last change of `cursor.json` is 3a32c5c, T657). Binary files and untracked or ignored files were not searched. The published GitLab wiki copy of `docs/wiki`, CI variables, release assets and external adopters' repositories are outside the repository and were not checked. Hit counts are `grep -c` line counts; some very long lines were truncated in reading.
