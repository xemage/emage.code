# Artifact: pi-removal-inventory-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T769 (plan-146, Part B, item 5): inventory of everything that exists because of Pi platform support, as input to ADR-013 (T770) and the removal steps S1 (T771, code) and S2 (T772, docs). The user's request of 2026-11-07, verbatim: "Remove PI support completely".
- **Author**: tech-lead, read-only. Method: `git ls-files`, `git grep` (patterns in § 12) with `tests/golden/held-out` never opened, listed or searched; each cited line re-read with `sed -n`. No `.env*`, credential file, `.claude/settings*.json` or `.vscode/mcp.json` read. No generator, installer or test run (behaviour statements are from reading the code; "verified" below means re-read at the cited line).
- **Target**: `develop` at `f032d7f692420692ac7949a68360eaf8f330163d`.
- **Based on**: `docs/decisions/ADR-010-drop-cursor-platform-support.md`, `docs/artifacts/cursor-removal-inventory-v1.md`, `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (branch `docs/plan-146-start`), `docs/artifacts/tracked-debt-register-v11.md`, `docs/releases/v10.0.0.md`.

## Totals

- **Pi-only tracked files: 184**: 91 under `.pi/`, 91 under `implementation/.pi/` (identical file lists), `implementation/platforms/pi.json`, `tests/functional/test_pi_optional_variables.py` (which is **not** all Pi, see § 6.2).
- **Tracked files outside the two trees that name Pi** (held-out never searched): 335 = **106 live** (the acceptance-grep set of § 12, 624 hit lines today, including `pi.json` and `test_pi_optional_variables.py`) + 219 history + 1 drift baseline (§ 9) + 9 golden (§ 7). The 106 live files:

| Group | Files |
|---|---|
| Generated mirrors of five knowledge files (root 22 + `implementation/` 22) | 44 |
| Code and config (`pi.json`, manifest schema, `sync.mjs`, `generate-registry.py`, `index.json`, `package.schema.json`, `install.sh`, `render_installed_agents.py`, `merge-mcp-json.py`, `Makefile`) | 10 |
| Knowledge sources (`servers.yaml`, `README.md`, 3 commands, 2 skills) | 7 |
| Live docs and templates | 14 |
| Tests outside golden (29 functional including `test_publish_release.py`, 1 pack fixture) | 30 |
| False positive only | 1 (`scripts/deploy/cwso-docker-desktop.sh:80` `lsof -Pi`); a second false-positive line, `tests/functional/test_publish_release.py:555` `"a pi/v4"`, sits in a file counted under tests |

(`tests/_baselines/root-install-drift.json`, 19 hit lines in its append-only `_comment`, is counted in § 9, not here.)

## Verified facts (P1 to P20)

| # | Fact | Where |
|---|---|---|
| P1 | The generator is manifest-driven; `syncPlatform` runs `fs.rm(outRoot)` only for a manifest that exists, and `--check` compares only files it would generate. Deleting `pi.json` leaves both `.pi/` trees in place, invisible to `sync --check` and `verify.mjs` (as ADR-010 V2). | `implementation/scripts/sync.mjs` 1278-1285, 1312, 1360 |
| P2 | **New since ADR-010:** the orphan-tree guard `tests/functional/test_platform_tree_ownership.py` (T662) fails if a `.<dir>/.generated-manifest.json` exists at either level without a manifest owning it. Deleting `pi.json` without `git rm -r` of both trees therefore **fails this test** (good). `REMOVED_PLATFORM_DIRS = (".cursor",)` (29) and the named test (78-98) cover only Cursor. The root check scans the working tree, so a developer's own **untracked** `.pi/` with a `"platform": "pi"` generated manifest would also fail it locally **(unverified: whether `find_orphan_trees` skips untracked dirs; read 43-70 only partly)**. | 29, 43, 60-98, 100-138 |
| P3 | The root parity gate (`compute_drift`, `_root_only_drift` over trees from `parse_replaced_trees`) still cannot see a root tree the installer no longer names; `test_install_contract_is_parsed` **requires** `.pi` (174). | `tests/functional/test_root_install_parity.py` 74, 134, 146, 172-176 |
| P4 | `pi.json`: `outputDir .pi`; `fileMap` agents/`prompts`/instructions/skills `.md`; agents `tools: array`, **`mcpToolNames: "pi"`**; `mcp.tags [core, extended]`, `outputFile mcp.json`, **`format: "pi"`** (renamed from `cursor` by ADR-010 D2). | `implementation/platforms/pi.json` 1-33 |
| P5 | `_manifest.schema.json` is now tracked (ADR-010 V5 said untracked) and enumerates `"pi"` twice: `mcpToolNames` enum (52) and `mcp.format` enum (72). | `implementation/platforms/_manifest.schema.json` 52, 72 |
| P6 | **Shared emit branch:** `emitMcpVscodePi(filtered, format)` serves `vscode` and `pi` (`MCP_EMITTERS` 849-850). Pi-specific inside it: template `${VAR}` vs `${env:VAR}` (736), `mapEnvOmitOptional` for Pi only (737), wrapper `mcpServers` vs `servers` (738-739, 752), remote `{url}` vs `{type:'http', url}` (743), `cwd` for vscode only (747), `env` written when empty for vscode only (749). An unknown format throws `Unknown MCP format: <x>` (863). | `sync.mjs` 717-752, 848-864 |
| P7 | `MCP_FORMATS` (207) includes `pi`; it validates `skipFormats` (251-256). After `pi` leaves the list, the two `skipFormats: [pi]` lines in `servers.yaml` **stop the run**; they must go in the same commit. `skipFormats` then has no user (generic code 203-220, 251-256 stays or goes: ADR-013 decision). | `sync.mjs` 199, 203-207, 219-220, 251-256; `servers.yaml` 165, 173 |
| P8 | `optional` (T680) is **not** Pi-only: claude-code reads it in `mapTemplatedValue` (881: `default` string first, else `''` when `optional`). Both GitLab entries carry `default: ""` **and** `optional: true` (`servers.yaml` 98-99), so for claude-code the output is `${VAR:-}` with or without `optional`; vscode/gemini/opencode/cline use `mapEnv` and ignore it. Removing `optional: true` from 98-99 is byte-neutral for every non-Pi format (by reading 873-892). Pi-only pieces: `mapEnvOmitOptional` (895-904), the Pi rationale of the `headers`-may-not-be-optional rule (SEC-T680-02, 332-336), comments 278-280. | `sync.mjs` 278-312, 326-336, 873-904; `servers.yaml` 24-34, 92-99 |
| P9 | `mcpToolNames` style `pi` (`mcp__<server>__<tool>`, chars outside `[A-Za-z0-9_]` to `_`) is Pi-only (528, 560-563); claude-code uses `verbatim`. | `sync.mjs` 521-563, 568-582 |
| P10 | `generate-registry.py` fallback list (120) and `package.schema.json` enum (23) both list `pi`; `implementation/registry/index.json` has `pi` in the `platforms` array (11) and in `compatibility.supportedPlatforms` and `compatibility.projectionStatus` of all 80 entries (161 lines); regenerating after `pi.json` is deleted drops them. `tests/fixtures/packs/sample-pack/pack.json:9` declares `pi`. Schema consumers: `implementation/scripts/package.py`, `check.py`, `implementation/commands/package-install.md`, `tests/functional/test_package_workflow.py` (none names Pi). | as listed |
| P11 | Installer: one array `SUPPORTED_PLATFORMS=(github gemini opencode pi claude-code cline)` (20) drives usage, early validation (183-197, before any write), `all`, dispatch (`install_platform`, 1647-1655); per-platform maps `platform_managed_paths` `pi)` (468) and `platform_mcp_config` `pi)` (483); a platform in the array without a map entry or `install_<name>` fails closed (exit 70, `internal_unknown_platform` 492-495). Pi-only: usage text 72 and example 92; `validate_before_update` tree loop `.pi` (1308) and its exception text (1314); `install_pi()` 1604-1608, the only caller of `merge_or_copy_mcp_json`'s third argument `--drop-env-form` (1388, 1401-1403). | `scripts/install.sh` |
| P12 | `test_install_robustness.py` asserts the array **equals** the outputDir-bearing manifests (102-109) and that each platform has every per-platform piece (111-) and mutates `install_pi`/the `pi)` lines (1260-1284). So array and manifest must change together. | `tests/functional/test_install_robustness.py` 95-145, 1255-1285 |
| P13 | Cursor precedent in code: the early-validation `cursor` case with its own message (186-190) and the read-only `notice_previous_cursor_install` (1276-1302, called at 1307). A Pi analogue does not exist yet. | `install.sh` |
| P14 | `merge-mcp-json.py --drop-env-form` and `drop_dead_env_form()` are Pi-only (docstring 41-54, function 134, argparse 423-425, call 516-517); comment 112-113 names Pi. The SEC-T680-01 credential-literal WARNING and SEC-T680-05/-07/-08 helpers in the same script are **generic** (every format). | `scripts/merge-mcp-json.py` |
| P15 | `render_installed_agents.py`: `PLATFORM_MAP["pi"]` (31-35), argparse `choices` (146); the `all` branch iterates `PLATFORM_MAP`, so the **root `AGENTS.md` lines 60, 74, 80, 93, 97 are renderer output** and change in S1. Root lines 88, 102, 116, 118 are authored in `implementation/AGENTS.md` (same line numbers) and change in S2. | `scripts/render_installed_agents.py`; `diff implementation/AGENTS.md AGENTS.md` |
| P16 | `.pi/.generated-manifest.json` carries `"platform": "pi"` (3); `.pi/mcp.json` has 14 servers (no `hindsight`, `cwso`: `skipFormats`), its sidecar `generatorOwnedKeys` the same 14. Both are usable install markers for a detection notice. | `implementation/.pi/` |
| P17 | Platform-count floors that **fail** after removal: `test_mcp_tool_name_mapping.py:371` `>= sources * 5` (five agent-projecting platforms; 4 × 28 = 112 < 140); `test_mcp_platform_conformance.py` 137 and 190 (`== 6` manifests); `test_manifest_schema.py:50` (exact registry list); `test_install_robustness.py` 102-109 (array = manifests). Loose but passing: `test_mcp_package_pins.py:468` `>= 4 * 20` over claude/github/opencode/pi globs (3 × 28 = 84 ≥ 80; should become `3 * 20`). | read |
| P18 | Count words in live text: `implementation/knowledge/commands/skillify.md` 50 ("other five platforms"), 52-53 ("all six folders", "other five"); `implementation/knowledge/agents/context-retriever.md:30` ("other 5 platforms"); `docs/wiki/mcp-servers.md:358` ("all 6 platforms"); `tests/functional/test_root_install_parity.py:3` ("seven platform trees"); `test_mcp_platform_conformance.py` 9, 15, 143, 145 ("6"); `test_mcp_tool_name_mapping.py:368` ("Five platforms"). `test_mcp_schema_validation.py:3` ("seven platforms", T384 research date: historical statement, may stay). | read |
| P19 | All five golden cases that name Pi read **only their own `fixture/`**; no fixture has a `.pi` directory; none needs an edit (§ 7). | the five `expect.py` |
| P20 | `.gitignore`, `.gitlab-ci.yml`, `implementation/README.md`, `implementation/runtime/`, `scripts/scorecard.py` (not opened; absent from the grep), `scripts/verify-release-docs.py`, `publish-release.py` have no Pi hit. `.gitlab/merge_request_templates/*` have none. | `git grep` |

## 1. Generated trees

| Path | Files | Content |
|---|---|---|
| `implementation/.pi/` | 91 | `agents/*.md` 28, `prompts/*.md` 19, `instructions/*.md` 6, `skills/` 35, `.generated-manifest.json`, `mcp.json`, `mcp.json.provenance.json` |
| `.pi/` (root, installer output) | 91 | same file list (verified by `diff` of the two `git ls-files` lists) |

Both must be `git rm -r` in S1 (P1); the orphan guard now enforces it for files carrying a generated manifest (P2). Deleting the root `.pi/` is a change to the root install and needs the user's explicit approval (as ADR-010 Q3).

## 2. Source of truth

`implementation/platforms/pi.json` (P4). Readers: `sync.mjs` `main()` (all `platforms/*.json` except the schema, 1312), `generate-registry.py` `_detect_platforms` (117-123), `tests/_helpers` `list_platform_manifests` (used by `test_install_robustness.py`, `test_manifest_schema.py`, `test_mcp_platform_conformance.py`), and the manifest schema enums (P5).

## 3. Generator: Pi-only and shared code

| Item | Lines | Kind | S1 change |
|---|---|---|---|
| `MCP_FORMATS` | `sync.mjs` 207 | shared list | drop `'pi'` |
| `skipFormats` comment / validation / `emittedFor` | 203-206, 219-220, 251-256 | generic, Pi is the only user | comment loses the Pi example; keep or delete the feature (ADR-013) |
| `servers.yaml` `skipFormats: [pi]` | 165 (`hindsight`), 173 (`cwso`) | data | delete both lines (else P7: run stops) |
| `servers.yaml` header comments | 30-40 | comment | rewrite without Pi |
| `optional` on GitLab env | `servers.yaml` 92-93 (comment), 98-99 | data | remove `optional: true` and the Pi comment; byte-neutral (P8) |
| `SPEC_KEYS` `optional`, validation | `sync.mjs` 278-281, 306-312, 326-336 | generic | keep (claude-code reads it) or remove with 98-99 (ADR-013); the headers rule's rationale (SEC-T680-02, 332-333) becomes moot |
| `mapTemplatedValue` `optional` fallback | 873, 881 | shared | unchanged if `optional` kept |
| `mapEnvOmitOptional` | 895-904 | Pi-only | delete |
| `emitMcpVscodePi` | 717-752 | **shared with vscode** | becomes `emitMcpVscode`: fixed `${env:VAR}`, `mapEnv`, `servers` wrapper, `{type:'http', url}`, `cwd` rule, `env` written even when empty; comments 724-735 lose Pi |
| `MCP_EMITTERS` `['pi', ...]` | 850 | Pi-only | delete; 849 points at the renamed function |
| `mcpToolNames` style `pi` | 528, 560-563 | Pi-only | delete |
| `_manifest.schema.json` enums | 52, 72 | schema | drop `"pi"` |
| `mapTemplatedValue` doc comment | 874 | comment | `vscode/pi/cline` to `vscode/cline` |

**Proof that every other platform's generated bytes stay identical** (required for S1):

1. *Tracked-output diff.* All generated non-Pi outputs are tracked. After each S1 commit: `node implementation/scripts/sync.mjs --root implementation` then `git diff --exit-code <base-sha> -- implementation/.github implementation/.vscode implementation/.gemini implementation/.opencode implementation/.claude implementation/.cline implementation/.mcp.json implementation/.mcp.json.provenance.json` must be empty (base = the develop sha S1 branched from), and `sync --check` must pass. S2 later changes only the mirrors of the five knowledge files of § 8.
2. *Independent hash run.* On a scratch copy of `implementation/`, run the base `sync.mjs` and the S1 `sync.mjs` against the **same** `knowledge/` (with the S1 `servers.yaml`), then compare `find .github .vscode .gemini .opencode .claude .cline .mcp.json* -type f -print0 | sort -z | xargs -0 sha256sum` of both runs. Equal hash lists prove the refactor of P6 and the `servers.yaml` edits of P7/P8 are byte-neutral.
3. *Unit check of the vscode branch.* A synthetic `servers.yaml` with a remote server with headers, a stdio server with `cwd: workspace`, an `optional` env value and an empty `env` must render identically before and after (P6 lists the six behaviours).
4. *Order of commits* (as ADR-010 D2): (1) the vscode-only refactor of the emitter with Pi still present, proven by 1-3 (Pi output also unchanged); (2) the Pi deletion.

## 4. Installer and scripts

| File | Lines | Item |
|---|---|---|
| `scripts/install.sh` | 20 | `SUPPORTED_PLATFORMS` (drop `pi`) |
| | 72, 92 | usage text (`.pi/mcp.json` in the MCP list; `--platform pi --update` example) |
| | 183-197 | early validation: add a `pi` removal case like `cursor` (186-190), ADR-013 decides the text |
| | 468, 483 | `platform_managed_paths` and `platform_mcp_config` `pi)` cases (a stale case would not fail: only array members are checked) |
| | 1276-1307 | Cursor notice; a Pi notice is the ADR-013 question (P13) |
| | 1308, 1314 | `validate_before_update` loop `.pi` and its exception text |
| | 1388, 1401-1403 | `merge_or_copy_mcp_json` third argument, only used by Pi: delete with the flag |
| | 1604-1608 | `install_pi()` |
| `scripts/render_installed_agents.py` | 31-35, 146 | `PLATFORM_MAP["pi"]`, `choices` |
| `scripts/merge-mcp-json.py` | 41-54, 112-113, 134-, 423-425, 516-517 | `--drop-env-form`, `drop_dead_env_form` (P14); keep the generic warnings |
| `Makefile` | 12, 13 | `PLATFORM=pi` example and usage list |
| `scripts/deploy/` | - | no Pi code (`cwso-docker-desktop.sh:80` is `lsof -Pi`, a false positive) |
| `.gitignore` | - | no Pi entry |

**Adopter behaviour, from reading the code:**

| Situation | Today | After a plain removal |
|---|---|---|
| `--update` or `--projections-only` with `pi`/`all` into a project with `.pi/` | warning (1308-1318), then `rsync -a --delete` of `implementation/.pi/` into `$TARGET/.pi/`, excluding `mcp.json` and its sidecar (`sync_tree_into` 962-; `install_tree_into` 1185-1194): **user files inside `.pi/` are deleted** | `.pi/` is never written, deleted, pruned, warned about or symlink-guarded (the guard is derived from the selected platforms, 542) |
| `.pi/mcp.json` | merged by `merge-mcp-json.py` with sidecar pruning and `--drop-env-form` | frozen: pins, Playwright hardening and GitLab grants stop receiving updates |
| `.pi/agents/*.md` | refreshed | frozen tool lists |
| `--platform pi` | installs | `error: unknown platform 'pi'`, exit 1, nothing written (183-197 run before any write), unless ADR-013 adds a removal case |
| `.pi/` as Pi's own project folder | the sweep can delete Pi's own project files there **(unverified: what Pi itself stores in a project `.pi/`)** | untouched |

Recommendation for ADR-013 as in ADR-010 D3 B: removal message for `--platform pi` and a read-only notice when `$TARGET/.pi/.generated-manifest.json` says `"platform": "pi"` or `$TARGET/.pi/mcp.json.provenance.json` exists; never delete. Which release first wrote `.generated-manifest.json` for Pi is **(unverified)**.

## 5. Registry and metadata

`generate-registry.py:120` fallback list; `registry/index.json` (P10; regenerate); `registry/package.schema.json:23` enum (drop `pi`; a pack that declares `pi` is then rejected: small compatibility change for ADR-013); `tests/fixtures/packs/sample-pack/pack.json:9` (drop `pi`).

## 6. Tests outside golden

### 6.1 Edit (would fail or would keep naming Pi)

| File | Lines | Change |
|---|---|---|
| `test_install_robustness.py` | 46, 50, 158, 183, 196, 252, 512-586, 1260-1284 | MCP/tree maps lose `pi`; examples and the fail-closed mutation re-pointed to another platform (for example `cline`) |
| `test_install_script.py` | 24, 44-148, 358, 481-529, 1135, 1349, 1361-1364, 1418-1420, 1425-1456, 1506-1546 | default platform and fixtures `pi` to a remaining tree-plus-`mcp.json` platform (`cline` or `gemini`); delete `..._sidecar_history_pi` (752-754; the siblings stay) |
| `test_install_projections_only.py` | 35, 85, 92, 157-159, 291-298, 339, 408 | `HARNESS_TREES`, stale edits, merge-owned set (six configs to five), pi-only refresh test re-pointed |
| `test_install_target_inside_repo.py` | 11-12, 88-113 | `implementation/.pi` example and `--platform pi` to a remaining platform |
| `test_install_type_conflicts.py` | 39, 105-154 | `SHIPPED_FILE` and `.pi` snapshots to a remaining platform |
| `test_install_update_root.py` | 139-143 | alias case `--platform pi` |
| `test_install_agents_mapping.py` | 48 | drop the `.pi/skills/` assertion |
| `test_install_command_audience.py` | 40 | `SINGLE_PLATFORMS` |
| `test_install_cursor_removal.py` | 153, 182, 187, 240, 392 | supported list and trees lose `pi`; 240 uses `{"platform": "pi"}` as "another platform": pick a supported one |
| `test_root_install_parity.py` | 3, 174, 232-256 | "seven" to "six"; contract list loses `.pi`; detector examples re-pointed |
| `test_platform_tree_ownership.py` | 11-13, 29, 78-98, 100-138 | add `.pi` to `REMOVED_PLATFORM_DIRS` and a named Pi case; the scratch fixture (107-111, 130-138) uses `pi` as the valid platform: re-point |
| `test_manifest_schema.py` | 50, 68-72 | exact registry list; synthetic `pi.json` example |
| `test_mcp_platform_conformance.py` | 9, 15, 73, 137, 143-145, 190, 253-270 | count 6 to 5; `_SERVER_MAP_BY_FORMAT["pi"]`; the `cursor` fail-closed test hosts on `pi.json` (259): move to another manifest, add the same for `pi` |
| `test_platform_projections.py` | 4, 101, 412-452 | T360 remote-shape table loses Pi |
| `test_mcp_tool_name_mapping.py` | 39, 58, 78-79, 131, 206, 283-309, 363-364, 368-371, 395 | style map, rendering cases, floor `sources * 5` to `* 4` (P17), artifact required-word `"Pi ("` (395: assertion on an immutable artifact, delete as ADR-010 D6) |
| `test_mcp_package_pins.py` | 37, 81, 464-468, 503, 719-783 | lists lose `.pi`; floor `4 * 20` to `3 * 20` |
| `test_mcp_secret_guard.py` | 20, 95, 101, 322 | file lists; 322 uses `.pi/mcp.json` as a fake path: re-point |
| `test_mcp_server_denials.py` | 67, 162, 342 | platform tuples |
| `test_mcp_agent_denials.py` | 332, 707, 793 | platform globs |
| `test_github_security_servers.py` | 61, 149-150, 246 | Pi `skipFormats` exception |
| `test_gitlab_token_handling.py` | 14, 53, 74, 109-119, 146-149, 206, 254, 344-389, 476-503 | Pi rows; `merge_pi` tests go with `--drop-env-form`; the posture table test (476-503) requires a `Pi` row in the docs: edit with S2 |
| `test_context_retriever.py` | 319-323 | synthetic platform name: re-point |
| `test_context_retriever_mcp_server.py` | 247 | list |
| `test_release_self_review_text.py` | 61, 69, 73 | mirror lists |
| `test_technical_debt_location.py` | 39, 47 | mirror lists |
| `test_placeholder_flag_text.py` | 29 | mirror list |
| `test_mcp_schema_validation.py` | 23 | docstring |
| `test_publish_release.py` | 314, 319 | synthetic `# Pi` fence: tidy only (555 is a false positive) |
| `tests/fixtures/packs/sample-pack/pack.json` | 9 | § 5 |

### 6.2 `test_pi_optional_variables.py` (65 hits): split, do not delete whole

Pi-only, delete: `test_pi_*` of `OptionalRenderingTests` (118-137), `ShippedPiOutputTests` (175-216), `PiMigrationTests` (268-449, `--drop-env-form`), `PiDocumentationTests` (674-748), and `SkipFormatsTests` (218-266) if the feature goes. **Generic, keep (move to a merge-script or generator test file):** `OptionalValidationTests` (146-173) and the claude-code part of 101-116 if `optional` stays; `LiteralCredentialClassificationTests` (451-496), `LiteralPathTests` (498-525), `TerminalSafeNamesTests` (527-599), `PrunedEntryTests` (601-672, includes Opencode cases). These guard SEC-T680-01/-05/-07/-08/-09 fixes in `merge-mcp-json.py`, which serve every format; deleting the file whole would silently drop them.

### 6.3 Add

The ADR-013 installer tests (removal message, read-only notice, no write under `.pi/`, both copiers, as ADR-010 D3.4); a `Unknown MCP format: pi` fail-closed test; `.pi` in the orphan guard's named list.

## 7. Golden (`tests/golden/open/`, protected; nothing edited)

| Case | Pi mention | What `check()` reads | Result after removal |
|---|---|---|---|
| `skillify-skill-file-template-drift` | `brief.md` 24, 89; `expect.py` 17 (docstring), 69 (`(".pi", "skills")` in `DECLARED_SKILL_ROOTS`) | `case_dir/fixture` only (80-95); missing roots skipped (`is_dir()`, 83) | unchanged: the fixture has only `implementation/knowledge/skills/gitlab-api-push-fallback/SKILL.md` |
| `discover-skills-registry-grounded-recommendation` | `brief.md` 23, 71, 125-126; `expect.py:45` `PLATFORM_DIRS` has `.pi`; frozen `fixture/implementation/registry/index.json` | `fixture/` and `fixture/installed-target/` (125-152); `_target_skills` skips missing dirs (83-87) | unchanged: the installed target has only `.github/skills/` |
| `consolidate-memory-recommendation-table-grounded` | `brief.md` 119-120 | `fixture/recommendations.md`, `fixture/memory-entries.json` (95-101) | unchanged |
| `plan-task-creation-precondition-real` | fixture plan 36-37; `task-T365.md` 70, 99, 216, 238 | `fixture/docs/tasks/task-T365.md` and the plan it cites (15-29) | unchanged: historical text |
| `prepare-release-real-verdict-missing` | `fixture/docs/releases/v8.0.0.md` 25, 68, 80-84, 153-157 | the verdict block of that fixture (55-) | unchanged |

All five are `status: expected_pass`. No test or script reads `PLATFORM_DIRS` or `DECLARED_SKILL_ROOTS` outside the cases (grep of `tests/functional`, `scripts`, `implementation/scripts`). **No golden edit, no grant, no baseline bump is needed.** The constants keep `.pi` (and `.cursor`) as frozen supersets, harmless as in ADR-010 D5.

## 8. Live docs and knowledge

| File | Lines | Kind |
|---|---|---|
| `README.md` | 35, 60 (platform table), 88 (`--platform` table), 104, 116, 168, 367 | authored |
| `AGENTS.md` (root) | 60, 74, 80, 93, 97 rendered by `render_installed_agents.py` (P15); 88, 102, 116, 118 copied from `implementation/AGENTS.md` | rendered by `--projections-only` |
| `implementation/AGENTS.md` | 88, 102 (`extended` row), 116 (GitLab grants: "on Pi for an agent whose file is passed to `pi --tools`..."), 118 (Playwright narrowing "on Pi for an agent that lists an `mcp__` tool") | authored |
| `implementation/PREREQUISITES.md` | 44, 68 (client table, pi.dev), 162, 168, 176 (Pi placeholder row), 189 ("Pi has no per-server environment scoping"), 212 | authored |
| `implementation/SECURITY.md` | 25 | authored |
| `CONTRIBUTING.md` | 20, 68, 141 (T360 lesson cites `pi.json` with `"pi"`) | authored |
| `docs/wiki/mcp-servers.md` | 15, 56, 86, 89-104 (section "Pi: verified forms"), 112, 114, 124, 157, 162, 253, 266, 314, 340 (T385 closed decision), 358 (count), 368, 417-425 (manual Pi check) | authored |
| `docs/wiki/quick-start.md` 20, 33, 81, 130; `architecture.md` 39, 47; `home.md` 9; `implementation-guide.md` 45; `mcp-pin-bump-checklist.md` 68 | | authored |
| `docs/releases/_template.md` | 26 (`\| Pi \| pi \|`) | template |
| `.gitlab/issue_templates/Bug.md` | 16 | template |
| `implementation/knowledge/mcp/servers.yaml` | 30-40, 92-93, 98-99, 165, 173 | source (S1, § 3) |
| `implementation/knowledge/README.md` | 3 | source, not mirrored |
| `knowledge/commands/consolidate-memory.md:35`, `discover-skills.md:18`, `skillify.md:38` (+ counts 50-53), `skills/memory-management/SKILL.md:43`, `skills/skillify/SKILL.md:31`, `agents/context-retriever.md:30` (count) | | sources; the five path-list files have **44 mirrors** (3 commands x 4 platforms + 2 skills x 5 platforms, at root and under `implementation/`) |

## 9. Stays untouched (history), counts only

`docs/releases/` 34 files (all but `_template.md`), `docs/artifacts/` 66, `docs/plans/` 21, `docs/checkpoints/` 5, `docs/tasks/` 90, `docs/decisions/` 2 (ADR-002, ADR-010), `docs/archiv/` 1, `tests/golden/` 9 (§ 7), and the `_comment` ledger of `tests/_baselines/root-install-drift.json` (19 hit lines; append-only; `drift` is `[]` today).

## 10. Security-relevant Pi facts

| Item | Today | After removal |
|---|---|---|
| K-15 / SEC-T657-01 / SEC-T658-01 remainder (MEDIUM, `docs/releases/v10.0.0.md:200`) | "On Pi an agent file with no `mcp__` entry is not restricted"; Pi named among enforcing platforms when passed to `pi --tools` | the Pi part ends; the remainder is Gemini CLI only (Opencode's limit is K-23). The user's acceptance for v10.0.0 needs no new decision for Pi |
| K-20 (open, `v10.0.0.md:244`) and register v11 A-7 (357) | "the Pi list handling", "Pi lists" among the live checks | the Pi item drops; K-20 and A-7 stay open for the rest |
| SEC-T680-01 to -09 (all **fixed**, `tracked-debt-register-v2.md` 382-390) | Pi placeholder and merge findings | -02, -03, -04 and the Pi half of -01 become moot; the generic merge fixes (-01 warning, -05, -07, -08, -09) stay and keep their tests (§ 6.2) |
| `PREREQUISITES.md:189` | Pi passes every exported variable to every stdio server | gone |
| Frozen adopter state | `.pi/mcp.json` merged and pruned on `--update` | stops; same exposure as ADR-010 D8.1 (frozen pins, Playwright args, GitLab grants in `.pi/agents/*.md`) |

Register v11 has no other id that names Pi (one hit line, 357). No open id becomes fully obsolete; the Pi parts of K-15, K-20/A-7 and SEC-T658-01 do.

## 11. Corrections to earlier records (for ADR-013, not edits to them)

1. ADR-010 V5 says `_manifest.schema.json` is untracked: it is tracked now and enumerates `pi` (P5).
2. ADR-010 D2 named the format after "its only user" (Pi); after this removal the `emitMcpVscodePi` branch serves only `vscode`.
3. ADR-010 D6 re-pointed many Cursor test fixtures **to Pi** (`.pi/instructions/coding-standards.md`, `.pi/prompts/...`, symlink `single-other` `.pi`, secret-guard fake path `.pi/mcp.json`); they move again (§ 6.1).
4. ADR-010 D8 and `v10.0.0.md:200`: "K-15 keeps Opencode, Gemini CLI and Pi" and "the user's acceptance stands for ... Pi agents with no `mcp__` entry": the Pi part ends.
5. ADR-010 V2 and V9 (orphan tree invisible) are now half-closed by the T662 orphan guard (P2); the root parity gate is still blind (P3).
6. `CONTRIBUTING.md:141` uses `pi.json` as its example of a self-named format; it needs another example.
7. `AGENTS.md` / `docs/wiki/mcp-servers.md` cite immutable artifacts (`mcp-tool-name-mapping-v1.md`, `mcp-server-denials-v1.md`, `mcp-agent-denials-v1.md`) that carry Pi rows; as ADR-010 D6, cite them with "recorded before Pi was removed" instead of a `-v2`.

## 12. Acceptance grep for S1+S2

Content (run from the repository root):

```bash
git grep -I -n -i -E '\.pi\b|\bpi\b|\bpi_|_pi\b|vscodepi|pi-coding-agent|drop.env.form' -- . \
  ':!.pi' ':!implementation/.pi' ':!docs/releases/v*' ':!docs/artifacts' ':!docs/plans' \
  ':!docs/checkpoints' ':!docs/tasks' ':!docs/decisions' ':!docs/archiv' ':!tests/golden' \
  ':!tests/_baselines/root-install-drift.json'
```

File names: `git ls-files | grep -i -E '(^|/)\.pi/|(^|[/_-])pi([._-]|$)' | grep -v -E '^(docs/(releases/v|artifacts|plans|checkpoints|tasks|decisions|archiv)|tests/golden/)'`.

Run on today's tree (`f032d7f6`): **624 lines in 106 files**; the file-name check returns 184 paths (both trees, `pi.json`, `test_pi_optional_variables.py`). `-i` adds no hit to the case-sensitive form; the pattern does not match `api`, `pip`, `pipeline`, `.pip`, `PII` (word boundaries), and catches `pi_root`, `merge_pi`, `emitMcpVscodePi`. After S1+S2 the content grep must return only: (a) the two false positives (`scripts/deploy/cwso-docker-desktop.sh:80`, `tests/functional/test_publish_release.py:555`); (b) the installer's Pi removal message and notice code and their tests; (c) the `.pi` entry of `REMOVED_PLATFORM_DIRS` and its named test; (d) the `Unknown MCP format: pi` negative test; (e) the README migration paragraph; (f) the "recorded before Pi was removed" clauses; and the file-name check must return nothing. Anything else is a defect. Also sweep the count words of P18.

## 13. Not checked

No test, generator or installer run. Git history not examined. Untracked and ignored files not searched; held-out never touched. What Pi stores in a project `.pi/`, which release first wrote `.pi/.generated-manifest.json`, and whether `find_orphan_trees` skips untracked directories are **(unverified)**. Adopter repositories, the published wiki and CI variables are outside the repository.
