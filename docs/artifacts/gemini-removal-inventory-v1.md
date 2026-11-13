# Artifact: gemini-removal-inventory-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T776 (plan-146, Part C): inventory of everything that exists because of Gemini CLI platform support, as input to ADR-014 (T777) and the removal steps S1 (T778, code) and S2 (T779, docs). The user's decisions of 2026-11-07 (AskUserQuestion, option labels verbatim): on how to handle the Gemini gap of SEC-T657-01/SEC-T658-01, "Drop Gemini support"; asked to choose between dropping and fixing, "Drop Gemini instead of fixing (Recommended)".
- **Author**: tech-lead, read-only. Method: `git ls-files`, `git grep` (patterns in § 12) with `tests/golden/held-out` never opened, listed or searched; each cited line re-read with `sed -n`; test methods classified with `ast` (bodies naming Gemini only vs. mixed). No `.env*`, credential file, `.claude/settings*.json` or `.vscode/mcp.json` opened (`.claude/settings.json` appears below only as a grep hit count). No generator, installer or test run; behaviour statements come from reading the code, and "verified" means re-read at the cited line.
- **Target**: `develop` at `22bb4c747169153955e50f7041aa0f0f398f8e8b` (MR !659 merged; the S3 root refresh of the Pi removal, MR !660, is **not** in this tree, so the root `AGENTS.md` and root mirrors still carry Pi text and their line numbers can shift when !660 lands).
- **Based on**: `docs/artifacts/pi-removal-inventory-v1.md`, `docs/decisions/ADR-013-drop-pi-platform-support.md`, `docs/decisions/ADR-010-drop-cursor-platform-support.md`, the T775 security review `security-review-t775-gemini-scoping-v1.md` (session scratchpad, recorded by the orchestrator), `docs/artifacts/tech-lead-t773-pi-removal-v1.md`, `docs/artifacts/security-review-t773-pi-removal-v1.md`, `docs/artifacts/tracked-debt-register-v11.md`, `docs/releases/v10.0.0.md`, develop `22bb4c74`.

## Totals

- **Gemini-only tracked files: 184**: 91 under `.gemini/`, 91 under `implementation/.gemini/` (identical file lists; 7 root files differ in content, § 1), `implementation/platforms/gemini.json`, and the vendored schema `tests/fixtures/mcp-schemas/gemini-cli-settings.schema.json` (read only by the Gemini class of `test_mcp_schema_validation.py`; the other hits for its name are history).
- **Tracked files outside the two trees that name Gemini** (case-insensitive `gemini`, held-out never searched): **103 live files, 856 hit lines** (the acceptance-grep set of § 12, including `gemini.json` and the schema fixture), plus 259 history files (§ 9), the drift baseline (§ 9) and 10 golden files (§ 7). The 103 live files:

| Group | Files |
|---|---|
| Generated mirrors of five knowledge files outside `.gemini/` (root 17 + `implementation/` 17) | 34 |
| Code and config (`gemini.json`, manifest schema, `sync.mjs`, `generate-registry.py`, `check.py`, `index.json`, `package.schema.json`, `install.sh`, `render_installed_agents.py`, `merge-mcp-json.py`, `Makefile`) | 11 |
| Knowledge sources (`servers.yaml`, `knowledge/README.md`, 3 commands, 2 skills) | 7 |
| Live docs and templates (README, both `AGENTS.md`, PREREQUISITES, SECURITY, CONTRIBUTING, 6 wiki pages, release template, 2 `.gitlab` templates) | 15 |
| Tests and fixtures outside golden (29 functional, `sample-pack/pack.json`, the Gemini schema fixture) | 31 |
| Root config files the installer does not generate (`.vscode/settings.json`, `.claude/settings.json`) | 2 |
| False positives only: Gemini the **model provider**, not the platform (`implementation/adapters/sia-target/README.md:97`, `harness-entrypoint.py` 18, 19, 61, 73, `registry-entry.go:29`) | 3 |

A fourth false-positive line sits in a counted test file: `tests/functional/test_t223_sia_harness_capture.py:330` (the `AIza...` Gemini **API key** regex).

## Verified facts (G1 to G22)

| # | Fact | Where |
|---|---|---|
| G1 | As for Pi (P1): `syncPlatform` runs `fs.rm(outRoot)` only for a manifest that exists, and `main()` reads every `platforms/*.json` except the schema. Deleting `gemini.json` leaves both `.gemini/` trees in place and invisible to `sync --check`. | `implementation/scripts/sync.mjs` 1228-1236, 1260-1262, 1311 |
| G2 | The orphan guard catches it: `find_orphan_trees` iterates the **working tree** (`base.iterdir()`, 49) and fails for any `.<dir>/.generated-manifest.json` whose platform no manifest owns. So deleting `gemini.json` without `git rm -r` of both trees fails the test. This settles Pi inventory P2's open point **by reading**: untracked directories are not skipped, so a developer's untracked `.gemini/` that still holds a generated manifest with `"platform": "gemini"` fails the test locally. A Gemini CLI user's own `.gemini/` without that marker passes. `REMOVED_PLATFORM_DIRS = (".cursor", ".pi")` (30); the named tests are at 101-105 and the regrown-tree tests at 126-140. | `tests/functional/test_platform_tree_ownership.py` 11-15, 30, 44-59, 79-105, 111-140 |
| G3 | `gemini.json`: `outputDir .gemini`; `fileMap` agents/**commands**/instructions/skills, all `.md` (no TOML); agents `"tools": "drop"` and `keepKeys ["name","description","agents"]`, with **no `mcpToolNames`**; `mcp.tags [core, extended]`, **`outputFile settings.json`**, **`format: "gemini"`**. | `implementation/platforms/gemini.json` 1-32 |
| G4 | `_manifest.schema.json` names Gemini once: the `mcp.format` enum (72). The agents `tools` enum `"drop"` (51) has **one user, gemini.json**. The `mcpToolNames` enum has no Gemini value. | `implementation/platforms/_manifest.schema.json` 51, 72 |
| G5 | **Gemini-only generator code**: `applyAgentFrontmatter`'s `cfg.tools === 'drop'` branch (655-656, only `gemini.json` sets it); `GEMINI_POST_EDIT_HOOKS` (719-734, the `AfterTool` post-edit reminder hook, the only `hooks` block any MCP emitter writes); `emitMcpGemini` (736-756: `${VAR}` placeholders, remote servers as `httpUrl`, `excludeTools` copied from `denyTools` at 753, top level `{hooks, mcpServers}`); the `MCP_EMITTERS` entry `['gemini', emitMcpGemini]` (814). Comments that name Gemini: 186-192 (the `denyTools` rationale), 838 (`mapTemplatedValue` doc). No emitter function is shared with Gemini, unlike `emitMcpVscodePi` for Pi. | `sync.mjs` |
| G6 | **`denyTools` is shared and stays.** Opencode consumes it twice: `emitMcpOpencode` writes the top-level `permission` `playwright_<tool>: deny` (763-767), and `agentMcpDenials` puts the per-agent `false` entries last (594). Its validation (`validateDenyTools` 181, 224-256; `SERVER_KEYS` 198-200) is generic. Only the Gemini consumer (753) and the "Gemini CLI" half of the comments (190-191; `servers.yaml` 36-41, 114-116) go. | `sync.mjs` 141-156, 181, 186-200, 224-256, 594, 763-767; `implementation/knowledge/mcp/servers.yaml` 36-41, 114-118 |
| G7 | `servers.yaml` has no Gemini **data**: no `skipFormats` (deleted by ADR-013) and no `extraPlatforms: [gemini]`. Gemini appears only in comments 5-6, 40 and 115. S1 changes no `servers.yaml` key. | `servers.yaml` |
| G8 | `mapTemplatedValue` with `withDefault` is claude-code only; Gemini calls it with `'${VAR}'` and no default (744-748). The `optional`/`default` keys are unaffected. | `sync.mjs` 744-748, 830-848 |
| G9 | Installer: `SUPPORTED_PLATFORMS=(github gemini opencode claude-code cline)` (20) drives usage, early validation (184-201), `all` and dispatch. Gemini-only items: `platform_managed_paths` `gemini)` (470), `platform_mcp_config` `gemini)` (484), the usage MCP list `.gemini/settings.json` (71) and the "excludeTools denials"/"hooks value" wording (74-75), the `validate_before_update` loop `.gemini` (1333) and its exception text (1337), `install_gemini()` (1612-1616), and the merge comment "permission/excludeTools rules" (1416-1417). The Cursor (186-190) and Pi (191-194) early-validation cases and the two read-only notices `notice_previous_cursor_install` (1278-1304) and `notice_previous_pi_install` (1306-1326, called at 1331-1332 from `validate_before_update` 1328) are the precedent. The Pi notice is a separate function, as ADR-013 D5.4 allowed. | `scripts/install.sh` |
| G10 | Adopter effect today: `install_tree_into "$IMPLEMENTATION/.gemini" "$TARGET/.gemini" settings.json settings.json.provenance.json` runs `rsync -a --delete` on the tree with **only** those two files excluded. Every other file in an adopter's `.gemini/` is deleted on `--update`/`--projections-only`, including files that Gemini CLI itself reads from a project `.gemini/` (G21). `settings.json` is merged by `merge-mcp-json.py`. | `install.sh` 1612-1616, 1333-1342 |
| G11 | **Install markers** for a removal notice: `$TARGET/.gemini/.generated-manifest.json` with `"platform": "gemini"` (3) and `$TARGET/.gemini/settings.json.provenance.json` (a generator-only name; it lists 16 generator-owned keys). Which release first wrote either marker is **(unverified)**. A notice must **not** read `.gemini/.env` (Gemini CLI loads it, and it can hold `GEMINI_API_KEY`; G21). | `implementation/.gemini/.generated-manifest.json` 3; `implementation/.gemini/settings.json.provenance.json` |
| G12 | **`merge-mcp-json.py` Gemini-only paths**: the `excludeTools` union `merge_exclude_tools` (docstring 18-24, function 125-131, call 180-181) and the `hooks` "replaced" note (docstring 36, condition 188). No other generated config holds `excludeTools` or top-level `hooks` (Opencode uses `permission`, merged by `merge_permission`). The comment at 103-104 names Gemini among the `${NAME}` writers. The generic guards (SEC-T680-01/-05/-07/-08/-09), `SERVER_WRAPPERS` (331) and `merge_permission` stay. | `scripts/merge-mcp-json.py` |
| G13 | `render_installed_agents.py`: `PLATFORM_MAP["gemini"]` (19-24) and argparse `choices` (140). As in Pi P15, the **root `AGENTS.md` lines 60, 74, 80, 93, 97 are renderer output** (S1). Lines 88, 102, 116, 118 are authored in `implementation/AGENTS.md` (same line numbers) and change in S2. | `scripts/render_installed_agents.py`; root vs `implementation/AGENTS.md` |
| G14 | `implementation/scripts/check.py:397` requires the word "Gemini" in the **immutable** artifact `docs/artifacts/hook-policy-spec-v1.md` ("missing Gemini compatibility note"). The artifact keeps the word, so the check keeps passing. Keeping or dropping the marker is an ADR-014 choice; dropping it removes one hit. | `implementation/scripts/check.py` 380-404 |
| G15 | Registry: `generate-registry.py:120` fallback list; `registry/index.json` has `gemini` in `platforms` (8) and in two lists of each of the 80 entries (161 hit lines; regenerated); `package.schema.json:23` enum; `tests/fixtures/packs/sample-pack/pack.json:9` declares `gemini`. | as listed |
| G16 | **Fixtures that the Pi removal moved to Gemini** (ADR-013 D8 A: "to `gemini` where a second distinct tree platform is needed"; diff `638a80bb..22bb4c74`): `test_install_projections_only.py` 85 and 92 (`.gemini/commands/...` stale edits; `.pi/prompts/...` before), 291-298 (the single-platform refresh); `test_install_script.py` 1368-1376 (sentinel `.gemini/instructions/coding-standards.md`) and 1449 (the `.claude` symlink into another tree); `test_root_install_parity.py` 232-235 (deleted `.gemini/agents/orchestrator.md`) and 253-256 (stale `.gemini/settings.json` leaf); `test_publish_release.py` 314, 319 (a synthetic `# Gemini CLI` fence, text only). The other Pi-removal edits only dropped `pi` from a list that already held `gemini`. | `git diff -U0 638a80bb 22bb4c74 -- tests/functional` |
| G17 | **Opencode is the only remaining platform with Gemini's tree shape.** Both have `agents/` 28, `commands/` 19, `instructions/` 6, `skills/` 35, an in-tree config plus sidecar excluded from the sweep and merged afterwards (`install_opencode` 1618-1622), and non-MCP top-level keys in the config (`$schema`, `instructions`, `permission`). Claude Code has `rules/` and no in-tree config. GitHub has `prompts/`, and its config `.vscode/mcp.json` lives outside the tree. Cline has only `skills/` plus its config. One caveat: `opencode.json` uses the wrapper `mcp` and `command` as an **array**, so a test that edits `d["mcpServers"]["gitlab"]["command"]` (`test_root_install_parity.py:252`) must adapt its lambda or use `.mcp.json` or `.vscode/mcp.json`. | `git ls-files implementation/.{opencode,claude,github,cline}`; `implementation/.opencode/opencode.json` |
| G18 | Floors and exact lists that **fail** after removal: `test_manifests.py:18` (requires a `gemini` manifest); `test_manifest_schema.py:50` (exact registry list); `test_mcp_platform_conformance.py` 136 and 189 (`5` manifests to `4`); `test_mcp_tool_name_mapping.py:354` `sources * 4` (four platforms project agent files; after removal three: `sources * 3`); `test_install_robustness.py` 101-109 (array = manifests; passes once both change); `test_root_install_parity.py:173` (contract list requires `.gemini`). Loose but passing: `test_mcp_agent_denials.py:333` (per-platform `>= 28`, the `.gemini` tuple goes); `test_mcp_package_pins.py:466` `3 * 20` (claude/github/opencode only, unaffected). | read |
| G19 | **Doc-coupled tests** that pin a Gemini sentence in a live doc and must change in the **same commit** as S2: `test_github_removal_notes.py` 15-17 (SENTENCE_1 "...outside every generated denial on Opencode and Gemini CLI..." required verbatim in `implementation/PREREQUISITES.md`, `docs/wiki/mcp-servers.md` **and the history file `docs/tasks/task-T679.md`**, which stays: the test must accept a new sentence in the two live docs and the old one in the task file, or drop the task file from `DOCS`); `test_mcp_package_pins.py` 868-894 (exact AGENTS.md sentence "...and on Gemini CLI the tool list does not restrict MCP tools..."); `test_gitlab_token_handling.py` 471-501 (posture table must have the five clients incl. "Gemini CLI", 5 rows); `test_mcp_server_denials.py` 798-959 (`CLAIM_DOCS`, the Opencode/Gemini claim detectors, the pre-T658 wording samples 914-927). | read |
| G20 | Count words in live text after removal: `skillify.md:50` "other four platforms" (to three); `context-retriever.md:30` "other 4 platforms" (to 3); `docs/wiki/mcp-servers.md:337` "all 5 platforms" (to 4); `test_root_install_parity.py:3` "six platform trees" (to five); `test_mcp_platform_conformance.py` 9, 15, 31 ("all 5"); `test_mcp_tool_name_mapping.py:351` ("Four platforms project agent files"); `test_install_projections_only.py:335` ("all five MCP configs", to four) and the merge-owned set 337-339. `test_mcp_schema_validation.py:3` "seven platforms" is the dated T384 statement (may stay, as in ADR-013 D1). | read |
| G21 | **Unique to Gemini (no Pi analogue)**: (a) `.gemini/settings.json` is Gemini CLI's **general project settings file** (model, tools, context, hooks, security), not an MCP-only file. The merge keeps user keys, but the generated `hooks.AfterTool` replaces a user value (noted on stderr). (b) The generator writes a **hook** (G5). (c) Commands are emitted as `.md`, while Gemini CLI documents custom commands as `.gemini/commands/*.toml`, so the 19 `.md` commands are probably not loaded **(unverified)**. (d) No `GEMINI.md` context file is written (no tracked `GEMINI.md`; Gemini CLI's default context file name), so whether Gemini CLI ever read `AGENTS.md` or `.gemini/instructions/` depends on the user's `context.fileName` setting **(unverified)**. (e) The 28 agent files probably do not load (non-slug `name:`, `agents:` rejected by the strict schema; SEC-T775-01, source reading). (f) A project `.gemini/` is also Gemini CLI's own folder (`settings.json`, `.env`, `commands/`, `agents/`, policies, extensions, sandbox profiles: vendor list **(unverified)**), so today's `--update` sweep (G10) can delete a user's own Gemini files. (g) A vendored vendor schema backs one test class. (h) Vendor note (T775 V8): Gemini CLI was replaced by Antigravity CLI for unpaid-tier and Google One users on 2026-06-18. | `gemini.json`; `sync.mjs` 719-756; T775 review |
| G22 | No Gemini hit in `.gitignore`, `.gitlab-ci.yml`, `scripts/deploy/*`, `implementation/README.md`, `implementation/runtime/`, `scripts/verify-release-docs.py`, `publish-release.py` or `check-version-consistency.py`. `scripts/scorecard.py` was not opened (protected) and is absent from the grep. | `git grep` |

## 1. Generated trees

| Path | Files | Content |
|---|---|---|
| `implementation/.gemini/` | 91 | `agents/*.md` 28 (no `tools:`; orchestrators carry `agents:`), `commands/*.md` 19, `instructions/*.md` 6, `skills/` 35, `.generated-manifest.json`, `settings.json` (`hooks` + 16 `mcpServers`; `playwright.excludeTools` = the six tools), `settings.json.provenance.json` (16 `generatorOwnedKeys`) |
| `.gemini/` (root, installer output) | 91 | same file list. **7 files differ in content** from `implementation/.gemini/`: the 6 Pi-removal mirrors in the 27-entry drift baseline (awaiting !660), and `.gemini/settings.json`, which is not in the drift list (root lacks `hindsight`, `cwso` and others and orders a GitLab env key differently; why the parity gate does not count it as drift is **(unverified)**, probably the merge semantics of `compute_drift`) |

Both trees must be removed with `git rm -r` in S1 (G1). The orphan guard enforces this (G2). Deleting the root `.gemini/` changes the root install and needs the user's explicit approval (as ADR-010 Q3 and ADR-013 D6).

## 2. Source of truth

`implementation/platforms/gemini.json` (G3). It is read by: `sync.mjs` `main()` (1260-1262), `generate-registry.py` `_detect_platforms` (117-123), `tests/_helpers` `list_platform_manifests` (used by `test_install_robustness.py`, `test_manifest_schema.py`, `test_manifests.py`, `test_mcp_platform_conformance.py`, `test_platform_tree_ownership.py`), and the manifest schema enum (G4).

## 3. Generator: Gemini-only and shared code

| Item | Lines | Kind | S1 change |
|---|---|---|---|
| `cfg.tools === 'drop'` | `sync.mjs` 655-656 | Gemini-only user | delete the branch, or keep it as a generic option (ADR-014). If it goes, drop `"drop"` from the schema enum (`_manifest.schema.json:51`) |
| `GEMINI_POST_EDIT_HOOKS` | 719-734 | Gemini-only | delete |
| `emitMcpGemini` | 736-756 | Gemini-only | delete |
| `MCP_EMITTERS` `['gemini', ...]` | 814 | Gemini-only | delete. `Unknown MCP format: gemini` then fails closed (`emitMcp` 820-828, throw at 826) |
| `denyTools` data, validation, Opencode use | 181, 186-200, 224-256, 594, 763-767 | **shared, stays** (G6) | comment 186-192 loses the Gemini half |
| `mapTemplatedValue` doc | 838 | comment | `(claude-code, gemini)` to `(claude-code)` |
| `_manifest.schema.json` `mcp.format` enum | 72 | schema | drop `"gemini"` |
| `servers.yaml` comments | 5-6, 40, 115 | comment | rewrite without Gemini (YAML comments do not reach any output) |

**Proof that every other platform's generated bytes stay identical** (required for S1). This is simpler than for Pi: no emitter is shared, so no refactor commit is needed.

1. *Tracked-output diff.* After each S1 commit: `node implementation/scripts/sync.mjs --root implementation`, then `git diff --exit-code <base-sha> -- implementation/.github implementation/.vscode implementation/.opencode implementation/.claude implementation/.cline implementation/.clinerules implementation/.mcp.json implementation/.mcp.json.provenance.json` must be empty (base = the develop sha S1 branched from), and `sync --check` must pass. S2 later changes only the mirrors of the five knowledge files of § 8.
2. *Independent hash run.* On scratch copies (`git archive <sha> implementation`), regenerate at base and at the S1 tip, then compare `find .github .vscode .opencode .claude .cline .clinerules .mcp.json .mcp.json.provenance.json -type f -print0 | sort -z | xargs -0 sha256sum` (equal lists). Also run base `sync.mjs` and platforms against the S1 `knowledge/` (proof 2 of the Pi inventory). This proves that the `servers.yaml` comment edits and any `knowledge/` edit made in S1 are byte-neutral.
3. *Opencode denial unchanged.* `jq .permission implementation/.opencode/opencode.json` and the per-agent `false` lines of `implementation/.opencode/agents/*.md` are byte-identical before and after (covered by 1, named here because they are the surviving consumer of `denyTools`).

## 4. Installer and scripts

| File | Lines | Item |
|---|---|---|
| `scripts/install.sh` | 20 | `SUPPORTED_PLATFORMS` (drop `gemini`) |
| | 71, 74-75 | usage: `.gemini/settings.json` in the MCP list; "permission/excludeTools denials" and "permission rule or hooks value" wording (Opencode keeps `permission`) |
| | 184-201 | early validation: add a `gemini` removal case like Cursor/Pi (`[Gg][Ee][Mm][Ii][Nn][Ii]`); ADR-014 sets the text |
| | 470, 484 | `platform_managed_paths` and `platform_mcp_config` `gemini)` cases (a stale case would not fail: only array members are checked) |
| | 1278-1332 | Cursor and Pi notices; a Gemini notice reads the G11 markers only, never `.gemini/.env` |
| | 1333, 1337 | `validate_before_update` loop `.gemini` and its exception text |
| | 1416-1417 | merge comment "permission/excludeTools rules" |
| | 1612-1616 | `install_gemini()` |
| `scripts/render_installed_agents.py` | 19-24, 140 | `PLATFORM_MAP["gemini"]`, `choices` |
| `scripts/merge-mcp-json.py` | 18-24, 36, 103-104, 125-131, 180-181, 188 | the `excludeTools` union and the `hooks` note (G12): delete with their tests, or keep as dead generic rules (ADR-014). Deleting them changes `test_mcp_server_denials.py` `merge_rule_findings` (700-714), which requires the docstring bullet and `merge_exclude_tools` |
| `implementation/scripts/check.py` | 397 | marker on an immutable artifact (G14) |
| `Makefile` | 13 | usage list |
| `scripts/deploy/`, `.gitignore`, `.gitlab-ci.yml` | - | no Gemini code (G22). The `unit-tests` job already fetches tag `v10.0.0` (ADR-013 deviation b), so an end-to-end "old install updated by the new installer" test for Gemini can reuse that fetch |

**Adopter behaviour, from reading the code:**

| Situation | Today | After a plain removal |
|---|---|---|
| `--update`/`--projections-only` with `gemini`/`all` into a project with `.gemini/` | warning (1333-1342), then `rsync -a --delete` of `implementation/.gemini/` into `$TARGET/.gemini/`, excluding only `settings.json` and its sidecar: **user files inside `.gemini/` are deleted**, including Gemini CLI's own (G21 f) | `.gemini/` is never written, deleted, pruned, warned about or symlink-guarded |
| `.gemini/settings.json` | merged: generator-owned servers refreshed, `excludeTools` unioned, generated `hooks.AfterTool` replaces the user's | frozen. The six Playwright `excludeTools` stay (fail safe for those six), but pins, `--blocked-origins`, GitLab entry and placeholders stop receiving updates. The user's other Gemini settings are untouched |
| `.gemini/agents/*.md`, `commands/*.md` | refreshed | frozen (and probably never loaded, G21 c/e) |
| `--platform gemini` | installs | `error: unknown platform 'gemini'`, exit 1, nothing written (184-201 run before any write), unless ADR-014 adds a removal case |

Recommendation for ADR-014, as ADR-013 D5: a removal message for `--platform gemini` (all letter cases), and a read-only notice when `$TARGET/.gemini/.generated-manifest.json` says `"platform": "gemini"` or `$TARGET/.gemini/settings.json.provenance.json` exists. Never delete. The notice must not read `settings.json` or `.env`. It must say that `.gemini/settings.json` may also hold the user's own Gemini settings, so cleanup means removing the generated `mcpServers` and `hooks` entries, not the file.

## 5. Registry and metadata

`generate-registry.py:120` fallback list; `registry/index.json` (G15; regenerate); `registry/package.schema.json:23` enum (drop `gemini`; a pack that declares it is then rejected, a small compatibility change for ADR-014, as ADR-013 D7); `tests/fixtures/packs/sample-pack/pack.json:9` (drop `gemini`; it then declares `github`, `opencode`). Add the negative schema case beside `test_manifest_schema.py` 122-141 (it hosts on `claude-code.json`, not Gemini).

## 6. Tests outside golden

### 6.1 Re-point (fixtures that use Gemini as a host; G16 and older)

Host: **`opencode`** unless noted (G17).

| File | Lines | Change |
|---|---|---|
| `test_install_projections_only.py` | 85, 92 | stale edit and removed-upstream file to `.opencode/commands/...` |
| | 291-298 | single-platform refresh: `--platform opencode`, prefix `.opencode/`, AGENTS.md assertion `` `.opencode/skills/` ``. Check that `DELETED_SHIPPED` (`.opencode/agents/orchestrator.md`, 93) does not interfere |
| `test_install_script.py` | 1368-1376 | sentinel to `.opencode/instructions/coding-standards.md` |
| | 1449 | `.claude` symlink into `.opencode` |
| `test_root_install_parity.py` | 232-235 | `.opencode/agents/orchestrator.md` |
| | 250-256 | stale leaf: `.vscode/mcp.json` (`servers`) or `.mcp.json`, or adapt the lambda to `d["mcp"]["gitlab"]["command"] = ["stale"]` for `opencode.json` (G17 caveat) |
| `test_install_robustness.py` | 354-361 | `test_under_both_copiers` (corrupt config) to `opencode` |
| | 1207-1210 | the unselected sibling to `.opencode.emage-old.4242` |
| `test_publish_release.py` | 314, 319 | synthetic `# Gemini CLI` fence: tidy only (any heading text works) |

### 6.2 Delete (they test Gemini itself)

| File | Lines | Test |
|---|---|---|
| `test_install_script.py` | 357-422 | `test_gemini_settings_json_merge_on_update`. Its one generic assertion (a non-MCP sibling key survives the merge, 417-421) can move to `test_opencode_opencode_json_merge_on_update` (`instructions`/`$schema`) |
| | 691-693 | `..._sidecar_history_gemini` (siblings stay) |
| `test_install_robustness.py` | 263-275 | `test_plain_install_unions_the_gemini_exclude_tools_and_reports_a_replaced_hook` |
| `test_mcp_server_denials.py` | 147-158, 414-458, 534-538, 576-595 | the Gemini emit, union and install tests. 534-538 (only `permission` and `excludeTools` are special) keeps its `permission` half if the union goes |
| `test_mcp_schema_validation.py` | 44-59 + `tests/fixtures/mcp-schemas/gemini-cli-settings.schema.json` | the Gemini class and its vendored schema; the Opencode class and fixture stay; docstring 9-12 edited |
| `test_mcp_package_pins.py` | 813-824 | `test_gemini_agents_carry_no_tools_line` (SEC-T660-06; its premise is outdated per T775 V3) |
| `test_mcp_tool_name_mapping.py` | 200-202, 242-246 | the drop-line test and "unknown style fails even when the platform drops the tools line" (re-host on a synthetic `tools: drop` mutation of another manifest if `drop` is kept, § 3) |
| `test_platform_projections.py` | 210-215 | `test_gemini_agents_drop_tools_field` |
| `test_gitlab_token_handling.py` | 130-139 | `test_gemini_renders_the_documented_form...`. Its "others keep theirs" half is covered by 184-202 |

### 6.3 Edit (lists, maps, counts, mixed tests)

| File | Lines | Change |
|---|---|---|
| `test_install_robustness.py` | 8, 44, 49, 277-294 | maps lose `gemini`; `test_projections_only_keeps_the_opencode_and_gemini_denials` keeps its Opencode half (SEC-T658-05 d) |
| `test_install_script.py` | 1399 | guarded-tree list |
| `test_install_projections_only.py` | 35, 335-339 | `HARNESS_TREES`; merge-owned set five configs to four |
| `test_install_agents_mapping.py` | 46, 50 | drop `.gemini/` assertions |
| `test_install_command_audience.py` | 40 | `SINGLE_PLATFORMS` |
| `test_install_cursor_removal.py` | 153, 182, 187, 392 | supported list, help text, trees |
| `test_install_removed_platform_v11.py` | 103, 107, 295 | help text, supported list, trees; add the Gemini cases here or in a sibling file (§ 6.4) |
| `test_root_install_parity.py` | 3, 173 | count word; contract list loses `.gemini` |
| `test_platform_tree_ownership.py` | 11-15, 30, 101-105, 126-140 | add `.gemini` to `REMOVED_PLATFORM_DIRS`, a named Gemini case and a regrown-tree case (scratch fixture already hosts on `cline`) |
| `test_manifest_schema.py` | 50 | exact registry list |
| `test_manifests.py` | 18 | required list (G18) |
| `test_mcp_platform_conformance.py` | 9, 15, 31, 73, 136, 189 | count 5 to 4; `_SERVER_MAP_BY_FORMAT["gemini"]`. The `cursor`/`pi` fail-closed tests host on `cline.json` (unaffected); add `Unknown MCP format: gemini` |
| `test_mcp_tool_name_mapping.py` | 33-40, 89-98, 351-354, 376 | `NO_AGENT_TOOL_RENDERING` loses `gemini`; floor to `sources * 3`; 376 `"Gemini CLI ("` asserts a row of the **immutable** `mcp-tool-name-mapping-v1.md`: delete as ADR-013 D8 did for `"Pi ("` |
| `test_mcp_server_denials.py` | 1-9, 68, 177-181, 315-329, 345-350, 374-380, 526-532, 691-695, 700-714, 723, 769-771, 798-959 | `GENERATED_MCP` loses `gemini`; mixed tests keep their Opencode half. 723 and 769-771 assert Gemini rows of the **immutable** `mcp-server-denials-v1.md`: delete as ADR-013 did, or keep like the Cursor row still asserted at 772 (ADR-014 choice; if kept they are grep residue). Doc detectors per G19 |
| `test_mcp_package_pins.py` | 34, 78, 285, 480-504, 717-738, 868-894 | lists; `test_generated_denial_equals_the_list_on_opencode_and_gemini_only` becomes Opencode only (and asserts no other config carries a denial); doc sentence per G19 |
| `test_mcp_agent_denials.py` | 333, 786 | platform tuples |
| `test_mcp_secret_guard.py` | 22, 93, 98 | comment and file lists |
| `test_mcp_optional_env.py` | 30, 34, 126 | maps |
| `test_gitlab_token_handling.py` | 12, 51, 196, 219-220, 244, 473 | maps; the posture-table test (471-501) changes with S2 (G19) |
| `test_github_security_servers.py` | 61, 246, 350 | lists; 350 is a sample "old sentence" for a detector (may stay as a literal sample, then it is grep residue) |
| `test_github_removal_notes.py` | 3, 15-17 | G19: the T679 history file keeps the old sentence |
| `test_context_retriever_mcp_server.py` | 247 | list |
| `test_link_integrity.py` | 35 | skip set |
| `test_release_self_review_text.py` | 58, 65, 71 | mirror lists |
| `test_technical_debt_location.py` | 36, 43 | mirror lists |
| `test_placeholder_flag_text.py` | 26 | mirror list |
| `test_platform_projections.py` | 3, 27, 101, 355-368 | `_TARGET_PLATFORMS`; T360 remote-shape assertions on `httpUrl` go |
| `tests/fixtures/packs/sample-pack/pack.json` | 9 | § 5 |

### 6.4 Add

ADR-014 installer tests mirroring ADR-013 D5.5: refusal of `--platform gemini` in every mode and letter case, nothing written; help text; `--platform all` creates no `.gemini`; notice with each marker alone and byte-unchanged `.gemini/` (with a user file and an edited `settings.json`); no notice for a user's own `.gemini/` without markers, for a symlinked `.gemini` or marker; a source scan that no write/delete path names `.gemini`; a check that the notice never opens `.gemini/.env`; and the `git archive v10.0.0` end-to-end case. Also add an `Unknown MCP format: gemini` negative test and `.gemini` to the orphan guard's named list.

### 6.5 What must survive for Opencode

The six-tool server denial and its tests: `DENIED`/`PLAYWRIGHT_EXCLUDED` constants, `validateDenyTools` tests, the Opencode `permission` emit and merge (`merge_permission`, last-match ordering), the per-agent deny tests (`test_mcp_agent_denials.py`), `test_projections_only_keeps_the_opencode_..._denials` (Opencode half), and the denial-pin test (`test_mcp_package_pins.py` 479-492). Count them before and after S1, as T773 did for the Pi split. No generic guard lives only in a Gemini-named test, with one exception: the non-MCP-sibling-key assertion (§ 6.2).

## 7. Golden (`tests/golden/open/`, protected; nothing edited)

| Case | Gemini mention | What `check()` reads | Result after removal |
|---|---|---|---|
| `skillify-skill-file-template-drift` | `brief.md` 24, 89; `expect.py` 17 (docstring), 67 (`(".gemini", "skills")` in `DECLARED_SKILL_ROOTS`) | `case_dir/fixture` only (80-); missing roots skipped (`is_dir()`) | unchanged |
| `discover-skills-registry-grounded-recommendation` | `brief.md` 23, 71, 125-126; `expect.py:45` `PLATFORM_DIRS`; frozen `fixture/implementation/registry/index.json` | `fixture/` and `fixture/installed-target/` (137-152); missing dirs skipped (66, 78) | unchanged |
| `consolidate-memory-recommendation-table-grounded` | `brief.md` 119-120 | its fixture | unchanged |
| `plan-task-creation-precondition-real` | fixture plan-030, `task-T365.md` | its fixture | unchanged (historical text) |
| `prepare-release-real-verdict-missing` | `fixture/docs/releases/v8.0.0.md` | its fixture | unchanged |
| `sprint-status-dag-ledger-grounded` | `fixture/docs/tasks/active-tasks.md:54` | `fixture/` only (105-112) | unchanged |

All six are `status: expected_pass`. None of their `expect.py` files reads a repository path outside its own `fixture/` (grep for `repo_root`, `parents[`, `../`: 0 hits each), and no fixture has a `.gemini` directory. **No golden edit, no grant and no baseline bump is needed.** The constants keep `.gemini` as a frozen superset (harmless, as ADR-010 D5).

## 8. Live docs and knowledge

| File | Lines | Kind |
|---|---|---|
| `README.md` | 58 (platform table), 89 (`--platform` table), 105, 117, 170, 369 | authored; add a migration paragraph like the Pi one (65-67) |
| `AGENTS.md` (root) | 60, 74, 80, 93, 97 rendered (G13); 88, 102, 116, 118 copied from `implementation/AGENTS.md` | rendered by `--projections-only` (S3) |
| `implementation/AGENTS.md` | 88, 102 (`extended` row), 116 (GitLab grants: "on Gemini CLI the tool list does not restrict MCP tools" twice), 118 (Playwright: the Gemini `excludeTools` half and "On Gemini CLI every agent can still call ...") | authored; extend the existing "recorded before Cursor was removed and before Pi was removed" clauses |
| `implementation/PREREQUISITES.md` | 44, 45, 57, 60 (G19 sentence), 66 (install line), 161, 174 (posture row), 186 ("not enforced on Opencode and Gemini CLI (K-15)"), 209 | authored. Line 186 also mis-states Opencode (K-23 since T663; T773 security answer 6): align in the same edit |
| `implementation/SECURITY.md` | 9, 39 (v1 history: may stay), 25 (placeholder forms) | authored |
| `CONTRIBUTING.md` | 20, 68 (folder lists), 133 (T360 lesson about `httpUrl`: history, may stay or be reworded) | authored |
| `docs/wiki/mcp-servers.md` | 15, 56, 83, 94, 96, 100, 105, 110, 111, 113, 140, 143, 152, 234, 245, 294, 299, 320, 337 (count), 345, 352-360 (the "Gemini CLI" schema paragraph) | authored |
| `docs/wiki/mcp-pin-bump-checklist.md` | 56-58 (§ 6 intro), 65-68 (Gemini live-check steps), 75 (record row "not run") | authored; § 6 becomes Opencode-only |
| `docs/wiki/quick-start.md` 18, 32, 78, 128; `architecture.md` 37, 46; `home.md` 9; `implementation-guide.md` 45 | | authored |
| `docs/releases/_template.md` | 24 | template |
| `.gitlab/issue_templates/Bug.md` 16; `.gitlab/merge_request_templates/Default.md` 30 | | templates (Default.md 30 also carries a stale `v2/implementation/knowledge/` path) |
| `implementation/knowledge/mcp/servers.yaml` | 5-6, 40, 115 | source comments (S1, § 3) |
| `implementation/knowledge/README.md` | 3 | source, not mirrored |
| `knowledge/commands/consolidate-memory.md:35`, `discover-skills.md:18`, `skillify.md:38` (+ count 50), `skills/memory-management/SKILL.md:43`, `skills/skillify/SKILL.md:31`, `agents/context-retriever.md:30` (count) | | sources; the five path-list files have **34 mirrors** outside `.gemini/` (3 commands x 3 platforms + 2 skills x 4 platforms, at root and under `implementation/`) |
| `.vscode/settings.json` | 13 | authored root config, not generated: `"gemini": true` in the terminal auto-approve list (lets an agent run the `gemini` CLI without a prompt; see `implementation/SECURITY.md:9`). Recommend dropping it (a tightening); user-owned, so ask |
| `.claude/settings.json` | 1 hit (not opened by rule) | user-owned, client-owned by the installer, modified in the user's checkout; content and whether to change it are for the user **(unverified)** |

What the root refresh (S3) renders: the root trees from `implementation/`, root `AGENTS.md` (rendered lines via `render_installed_agents.py`, the rest copied), `CLAUDE.md`. The root `.gemini/` must be deleted by hand in S3 (`git rm -r`); `--projections-only` no longer names it.

## 9. Stays untouched (history), counts only

`docs/releases/` 34 files (all but `_template.md`), `docs/artifacts/` 77, `docs/plans/` 23, `docs/checkpoints/` 7, `docs/tasks/` 112, `docs/decisions/` 4 (ADR-002, ADR-005, ADR-010, ADR-013), `docs/archiv/` 2, `tests/golden/open/` 10 files in 6 cases (§ 7), and the append-only `_comment` of `tests/_baselines/root-install-drift.json` (24 hit lines; its `drift` list holds 6 `.gemini/` paths from the Pi removal, which disappear with the tree and must be re-declared or cleared in S3).

## 10. Security-relevant Gemini facts

| Item | Today | After removal |
|---|---|---|
| SEC-T657-01/SEC-T658-01 remainder (MEDIUM; `v10.0.0.md:200` K-15 and the acceptance record 298, deadline 2027-01-31) | after ADR-013 D9, Gemini CLI only: every Gemini agent and the main session can call every configured MCP tool except the six Playwright tools (T775) | **No platform part remains under the records' definition.** Claude Code and Copilot enforce named tools; Opencode's generated agents carry per-agent denies, and its built-in and user-owned agents are K-23 (user decision 2026-10-16, "document the gap only"), tracked separately; Cline has no agent files ("n/a" in the posture table). Whether the id closes, and so needs no ADR-011 re-acceptance at v11.0.0, is for the security engineer and ADR-014 to confirm |
| K-15 (accepted LOW in register v11 131; text `v10.0.0.md:200`) | names Gemini (and Pi, already ended) | the Gemini part ends. What remains is K-23 (Opencode) |
| SEC-T775-01 (agents do not load), -02 (docs say Gemini does not enforce tool lists), -03 (Gemini subagents cannot call agents) | LOW, proposed by T775 | **moot**: they describe generated Gemini files and Gemini docs, both removed. -02's adjacent Opencode mis-statement at `PREREQUISITES.md:186` is not Gemini and stays to fix (K-23 alignment) |
| K-20 (`v10.0.0.md:244`), register v11 A-7 (357), SEC-T658-02 (live checks not run, batch U) | "the Gemini CLI denials" among the live checks; `mcp-pin-bump-checklist.md` § 6 Gemini steps 65-68, record row 75 "not run" | the Gemini item drops; K-20, A-7 and SEC-T658-02 stay open for Opencode step 3, Copilot and the others |
| SEC-T660-06 (the generator drops Gemini tool lines) | pinned by `test_mcp_package_pins.py` 813-824 | moot; its premise is outdated per T775 V3 anyway |
| K-35 (`v10.0.0.md:229`) | the run evidence is a `--platform gemini` target | the defect is generic (`--platform-root .claude`) and stays; its evidence platform disappears, so a re-run on Opencode or Cline is advisable **(unverified that it reproduces there; read-only claim in the release text)** |
| Frozen adopter state | `.gemini/settings.json` merged on `--update` | stops; same exposure class as ADR-013 D11 / SEC-T773-02 (frozen pins, `--blocked-origins`, GitLab entry). The six `excludeTools` entries persist (fail safe), and nothing removes the hook |
| The `excludeTools` union in `merge-mcp-json.py` | live for Gemini | dead if kept; if deleted, a user who still runs the merge script by hand on a Gemini file gets source-wins semantics for that key **(only reachable by hand-run)** |
| `.vscode/settings.json:13` auto-approve `gemini` | lets an agent start the `gemini` CLI without prompting | recommend removal (§ 8) |

Register v11 names Gemini on one line only (357, A-7). No v11 id becomes fully obsolete by name. Their Gemini parts end: SEC-T657-01/SEC-T658-01 (the whole remainder, subject to confirmation), K-15, K-20/A-7/SEC-T658-02. The T775 proposals SEC-T775-01..-03 should be recorded in register v12 as closed-by-removal, not as open LOW debt.

## 11. Corrections to earlier records (for ADR-014, not edits to them)

1. ADR-013 D9: "After the removal, the SEC-T657-01/SEC-T658-01 remainder is Gemini CLI only". Now Gemini goes too (§ 10).
2. ADR-013 D8 A re-pointed fixtures "to `gemini` where a second distinct tree platform is needed". They move again, to `opencode` (G16, G17; § 6.1).
3. `implementation/AGENTS.md` 116/118, `PREREQUISITES.md:186` and `servers.yaml:115-116` say Gemini CLI does not restrict MCP tools per agent. T775 (V2-V3) found that Gemini CLI v0.67.0 does enforce a subagent `tools:` list and that our generator drops it. With the removal the statement disappears rather than being corrected.
4. The immutable artifacts `mcp-server-denials-v1.md`, `mcp-tool-name-mapping-v1.md`, `mcp-agent-denials-v1.md` and `hook-policy-spec-v1.md` carry Gemini rows or notes. Cite them with "recorded before Gemini CLI was removed" (extending the existing Cursor/Pi clauses), not with a `-v2`.
5. `docs/wiki/mcp-servers.md:152`, a correction row about `mcp-server-denials-v1.md` § 2.2 (Gemini scope merge), goes with the Gemini section.
6. `CONTRIBUTING.md:133` uses Gemini's `httpUrl` as its T360 example. Keep it as dated history or reword it.
7. The Pi inventory's P2 **(unverified)** point is now settled by reading (G2).
8. `v10.0.0.md:200` and the ADR-011 acceptance record (298) name a remainder whose last platform is removed. The release record stays; register v12 and the v11.0.0 release document state the outcome.

## 12. Acceptance grep for S1+S2

Content (run from the repository root):

```bash
git grep -I -n -i 'gemini' -- . \
  ':!.gemini' ':!implementation/.gemini' ':!docs/releases/v*' ':!docs/artifacts' ':!docs/plans' \
  ':!docs/checkpoints' ':!docs/tasks' ':!docs/decisions' ':!docs/archiv' ':!tests/golden' \
  ':!tests/_baselines/root-install-drift.json'
```

File names: `git ls-files | grep -i gemini | grep -v -E '^(docs/(releases/v|artifacts|plans|checkpoints|tasks|decisions|archiv)|tests/golden/)'`.

Run on today's tree (`22bb4c74`): **856 lines in 103 files**. The file-name check returns **184 paths** (both trees, `gemini.json`, `tests/fixtures/mcp-schemas/gemini-cli-settings.schema.json`). "gemini" has no lookalike word. The false positives are **semantic**: Gemini the model provider and its API-key format (`implementation/adapters/sia-target/*` 3 files, `tests/functional/test_t223_sia_harness_capture.py:330`); URLs `google-gemini/gemini-cli` and `geminicli.com` appear only in Gemini-specific lines that go anyway. Watch for the `GEMINI_API_KEY`/`GOOGLE_API_KEY` names in the adapter: they stay.

After S1+S2 (+S3 for the root) the content grep must return only: (a) the false positives above; (b) the installer's Gemini removal message and notice and their tests; (c) the `.gemini` entry of `REMOVED_PLATFORM_DIRS` and its named tests; (d) the `Unknown MCP format: gemini` and schema negative tests; (e) the README migration paragraph; (f) the "recorded before Gemini CLI was removed" clauses; (g) the ADR-013 TL-T773-01 residue lines if they still name Gemini (`test_gitlab_token_handling.py` posture guard: an `assertNotRegex` for a `Gemini CLI` row would join it); (h) whatever ADR-014 keeps on purpose: `check.py:397` (G14), the artifact-row assertions of `test_mcp_server_denials.py` 723/769-771 (§ 6.3), the detector sample `test_github_security_servers.py:350`, the old-sentence handling for `docs/tasks/task-T679.md` in `test_github_removal_notes.py`, `implementation/SECURITY.md` 9/39 (v1 history), `CONTRIBUTING.md:133`, `test_mcp_schema_validation.py:3`'s dated sentence, and the `.claude/settings.json` hit if the user keeps it. ADR-014 must enumerate (h) explicitly, so that the S3 grep has a complete expected list (the lesson of TL-T773-01). The file-name check must return nothing. Also sweep the count words of G20.

## 13. Not checked

No test, generator or installer run. Git history examined only for the Pi-removal test diff (`638a80bb..22bb4c74`). Untracked and ignored files were not searched, and held-out was never touched. **(Unverified)**: what Gemini CLI stores in a project `.gemini/` (vendor list); whether it loads `.md` commands; whether it reads `AGENTS.md` without a `context.fileName` setting; which release first wrote `.gemini/.generated-manifest.json` or `settings.json.provenance.json`; why root `.gemini/settings.json` differs from the generated file without being declared drift; whether K-35 reproduces on Opencode or Cline; the content of `.claude/settings.json`. Adopter repositories, the published wiki and CI variables are outside the repository.
