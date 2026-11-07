# Artifact: tech-lead-t773-pi-removal-v1.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/decisions/ADR-013-drop-pi-platform-support.md` (accepted 2026-11-07), `docs/artifacts/pi-removal-inventory-v1.md`, precedent `docs/decisions/ADR-010-drop-cursor-platform-support.md`.

## Metadata

- **Task**: T773, code-review half (plan-146 Part B, ADR-013 step "Reviews"). The security half is a separate review.
- **Reviewer**: tech-lead, read-only. No source file changed; this artifact is the only file written.
- **Reviewed**: branch `agent/technical-writer/T772` at `dc8042bc` (MR !659, draft), which merges develop `04676e5f`. Pi commits: `fcb796ff` (emitter refactor, S1 commit 1), `eab26b7a` (removal, S1 commit 2), `bcc77144` (S2 docs), `bff76906` (S2 regeneration), `2bf74005` (tests, count word, drift declaration). Base for the Pi diff: `638a80bb` (ADR acceptance). The T766 CA-chain files that arrive through the develop merge are not part of this review.
- **Method**: `git diff`, `git show`, `git grep`; scratch regeneration under the session scratchpad; the requested gates in a clean worktree at `dc8042bc`. `tests/golden/held-out/` never opened; no `docker`; no `.env*`, credential or settings file read. The full suite was not run (the orchestrator runs it); I ran three test modules (below).

## Findings

| Id | Severity | Where | Finding |
|---|---|---|---|
| TL-T773-01 | non-blocking | `tests/functional/test_gitlab_token_handling.py:475`, `tests/functional/test_verify_release_docs.py:1929` | The D1 acceptance grep returns two hits that are outside the allowed list (a)-(f) of ADR-013 D1, which says "Anything else is a defect". Both are benign: 475 is the guard `assertNotRegex(posture, r"(?m)^\|\s*Pi\s*\|", ...)`, which must name Pi to test its absence; 1929 is the comment explaining deviation (a). Neither can be reworded away without losing the guard or the explanation. Because ADR-013 is immutable, record both as accepted residue in the S3 checkpoint (or the v11.0.0 plan) so the S3 grep has a complete expected list. |
| TL-T773-02 | nit | `tests/functional/test_merge_mcp_json_guards.py:138` | `test_dropped_literal_and_literal_path_notes` was moved with one body change: the `--drop-env-form` argument is gone (necessarily, the flag no longer exists). Its name still says "dropped", and the `_OLD` key with `${env:OLD}` is now reported as a kept key, not dropped. The test still checks terminal-safe output for the three names and passes; the name is misleading. A rename would break D4's "same names" acceptance, so leave it or rename in a later change with a note. |
| TL-T773-03 | nit | `implementation/scripts/sync.mjs:316-317` | The SEC-T680-02 rationale for "headers may not be optional" was reworded without Pi (as D3 asks) and now states that an optional header "would be sent with an empty or literal placeholder value". True for claude-code (`${VAR:-}` renders empty) by reading `mapTemplatedValue`; for the other clients it is **(unverified)**. Harmless, since the rule only refuses input. |
| TL-T773-04 | nit | `implementation/scripts/sync.mjs` `withEmittedMcpTools` | With `emittedFor` deleted, the helper name and the phrase "emitted" in its comment now mean "selected". Cosmetic. |

No blocking finding.

## 1. ADR conformance

| Decision | Result |
|---|---|
| D1 scope | Met. `pi.json`, both trees, generator items, installer array/usage/maps/loop/`install_pi`/third argument, renderer map and `choices`, `merge-mcp-json.py --drop-env-form` and `drop_dead_env_form`, `Makefile` 12-13, schemas, registry, sample pack, tests and live docs all changed. History paths unchanged. Residue: see § 3 and TL-T773-01. |
| D2 emitter | Met. `fcb796ff` is the refactor alone (`sync.mjs` only); `emitMcpVscode` is vscode-only, `MCP_EMITTERS` has no `pi` entry; `mcpToolNames` style `pi` deleted; negative test `Unknown MCP format: pi` present (`test_mcp_platform_conformance.py:274-279`). Byte proofs in § 2. |
| D3 | Met. `skipFormats` key, validation, `emittedFor` deleted; a leftover key now fails as an unknown `SERVER_KEYS` key, pinned by `test_mcp_platform_conformance.py:282-297` (closes the ADR's **(unverified)** point). `optional` kept with the claude-code fallback; `mapEnvOmitOptional` deleted; comment 874 reads `vscode/cline`. |
| D4 split | Met; counts in § 4. |
| D5 adopter | Met. Removal case `[Pp][Ii]` in early validation with the exact D5.1 message (case-insensitive like the Cursor case, a harmless widening); `notice_previous_pi_install` reads only (`-d`, `-L`, `-f`, `grep -q`, `-e`), skips a symlinked `.pi` or marker, runs for `--update` and `--projections-only` (`--projections-only` sets `UPDATE=1`, `install.sh:364`); no write or delete path names `.pi`. Usage list and `--platform all` lose Pi. |
| D6 trees | Met. `git ls-files` shows no `.pi/` path at either level; `REMOVED_PLATFORM_DIRS = (".cursor", ".pi")` with a named case and the scratch fixture regaining `.pi` (`test_platform_tree_ownership.py:30, 105, 137-140`). |
| D7 schemas | Met. Both manifest-schema enums, `package.schema.json`, `generate-registry.py` fallback, sample pack and registry drop `pi`; negative schema tests at `test_manifest_schema.py:123-141`. |
| D8 fixtures | Met. Re-pointed to `cline`, which has the property the tests rely on: `install_cline` installs `.cline` with `mcp.json` and its sidecar excluded and merges `mcp.json` (`install.sh:1637-1641`), the same shape `install_pi` had. Floors: `sources * 4`, `3 * 20`, `== 5` manifests; `"Pi ("` artifact assertion deleted. |
| D9 version | Not in scope of this change (release plan); the messages name v11.0.0 consistently. |
| D10 golden | Met. No diff under `tests/golden/` or `scripts/scorecard.py` (`git diff --stat 04676e5f..dc8042bc` empty); `scorecard.py --check` OK. |
| D11 | Docs side checked only for the `PREREQUISITES.md` Pi lines (gone); the security consequences are the security reviewer's. |

Deviations provisionally accepted by the orchestrator:

- **(a) narrowed skip in `test_verify_release_docs.py`** — accept. It skips a missing `docs/releases/v*.md` pointer only when it is newer than the newest release document present (`pointer_applies`), so the test still fails for any missing older or current document, and at the v11.0.0 tag the gate reads the file. Narrower than a blanket skip and self-expiring.
- **(b) `unit-tests` fetches tag `v10.0.0`** — accept. Same pattern as the existing `v8.0.0` fetch for the Cursor test; `--depth=1` suffices for `git archive`; the class fails rather than skips under CI, so a missing tag cannot pass silently. It is a fetch in a branch job, not a job on a tag.
- **(c) two generic `skipFormats` tests deleted/trimmed** (`test_github_security_servers.py` `test_skip_formats_still_wins_over_the_platform_list`; the `skipFormats` subtest of `test_mcp_agent_denials.py:675-689`) — accept. Both tested the deleted key. The SEV-T690-06 behaviour they also touched (a grant of a server the platform config does not carry is left out) keeps coverage through the tag-based case in `test_mcp_tool_name_mapping.py:283-340`.
- **(d) `MCP_FORMATS` deleted rather than reduced** — accept. Its only reader was the `skipFormats` validation that D3 A deletes; keeping a list with no reader would be dead code (driver 4).

## 2. Byte equality (reproduced)

On scratch copies (`git archive <sha> implementation`), each regenerated with `node implementation/scripts/sync.mjs --root implementation`, then `find .github .vscode .gemini .opencode .claude .cline .mcp.json .mcp.json.provenance.json -type f -print0 | sort -z | xargs -0 sha256sum` (403 files each):

| Comparison | Result |
|---|---|
| `638a80bb` vs `fcb796ff` (non-Pi) | identical |
| `638a80bb` vs `fcb796ff` (`.pi/`, 91 files) | identical (commit 1 left Pi output unchanged) |
| `638a80bb` vs `eab26b7a` (non-Pi) | identical |
| base `sync.mjs` and platforms of `638a80bb` against the `knowledge/` of `eab26b7a` vs `638a80bb` (proof 2) | identical |
| `git diff --quiet 638a80bb eab26b7a -- implementation/.github implementation/.vscode implementation/.gemini implementation/.opencode implementation/.claude implementation/.cline implementation/.mcp.json implementation/.mcp.json.provenance.json` (proof 1) | empty |
| Proof 3: three synthetic servers prepended to `servers.yaml` (remote with a wrapped secret header; stdio with `cwd: workspace`, an `optional` and a literal env value; stdio with `env: {}`), regenerated at `638a80bb` and `eab26b7a` | `.vscode/mcp.json` identical, and all 403 non-Pi files identical. Output: `{"type": "http", "url": "${env:ZZ_URL}", "headers": {"Authorization": "Bearer ${env:ZZ_TOKEN}"}}`, `cwd: "${workspaceFolder}"`, `env: {}` written for the empty map. |

Proof 3 is not committed as a test; that matches the ADR (a proof, not a test requirement).

## 3. Completeness

Inventory § 12 content grep at `dc8042bc`, every hit classified:

| Class | Hits |
|---|---|
| Root projections awaiting S3 (all in the 27-entry drift declaration) | 22 mirror files under `.claude/`, `.cline/`, `.gemini/`, `.github/`, `.opencode/` (consolidate-memory, discover-skills, skillify commands; memory-management and skillify skills); root `AGENTS.md` 60, 74, 80, 93, 97 (renderer) and 88, 102, 116, 118 (copied) |
| (a) false positives | `scripts/deploy/cwso-docker-desktop.sh:80`, `tests/functional/test_publish_release.py:555` |
| (b) removal message, notice and their tests | `scripts/install.sh` 192, 1306-1325; `tests/functional/test_install_removed_platform_v11.py` |
| (c) orphan guard | `tests/functional/test_platform_tree_ownership.py` 11, 15, 30, 105, 109, 137-140 |
| (d) negative tests | `test_mcp_platform_conformance.py` 274-279; `test_manifest_schema.py` 123-141 |
| (e) README migration paragraph | `README.md` 65-67 |
| (f) "recorded before Pi was removed" | `docs/wiki/mcp-servers.md` 108, 133, 143; `implementation/AGENTS.md` 116, 118; `implementation/PREREQUISITES.md` 44, 45 (each hit is only that clause) |
| Outside the list | `test_gitlab_token_handling.py:475`, `test_verify_release_docs.py:1929` (TL-T773-01) |

File-name check: empty. `--print-drift` prints 27 paths, equal to the baseline's 27 (1 from T771 + 26 from T772); the baseline's `_comment` was only appended to (the previous last entry gained a comma).

Count words: no wrong count in live text. `skillify.md:50` "other four platforms", `context-retriever.md:30` "other 4 platforms", `docs/wiki/mcp-servers.md:337` "all 5 platforms", `test_root_install_parity.py:3` "six platform trees" (five platform dirs plus `.clinerules`). `test_mcp_schema_validation.py:3` "seven platforms" is the dated T384 statement D1 allows. Floors: `sources * 4`, `3 * 20`, `== 5` (two places).

## 4. Tests

- **D4 split**, counted with `ast` on `638a80bb:tests/functional/test_pi_optional_variables.py`: 52 test methods. Moved 22 (`LiteralCredentialClassificationTests` 5, `LiteralPathTests` 2, `TerminalSafeNamesTests` 5, `PrunedEntryTests` 5 to `test_merge_mcp_json_guards.py`; `OptionalRenderingTests` 3, `OptionalValidationTests` 2 to `test_mcp_optional_env.py`); deleted 30 (`OptionalRenderingTests` 2 Pi methods, `ShippedPiOutputTests` 5, `SkipFormatsTests` 4, `PiMigrationTests` 10, `PiDocumentationTests` 9). 22 + 30 = 52; no new method. 18 bodies identical; 4 differ only by a removed Pi line or folder (3) and the removed `--drop-env-form` argument (1, TL-T773-02).
- **Re-pointed fixtures** preserve intent: `cline` has the in-tree `mcp.json` excluded from the tree copy and merged afterwards, which is the property the stale-edit, sentinel, `SHIPPED_FILE` and secret-guard tests rely on (§ 1, D8).
- **D5 tests**: 16 methods, all driving the real `scripts/install.sh` through `run_installer` (rsync and the cp fallback via `path_without_rsync`): four modes of `--platform pi`, case variants, help text, `--platform all` creates no `.pi`, notice and byte-unchanged `.pi/` with a user file and an edited `mcp.json`, each marker alone, another platform's manifest, no `.pi`, a user's own `.pi` without markers, plain install, symlinked `.pi`, symlinked marker, a source scan for write/delete paths, and the end-to-end `git archive v10.0.0` install updated by the new installer. `python3 -m unittest tests.functional.test_merge_mcp_json_guards tests.functional.test_mcp_optional_env tests.functional.test_install_removed_platform_v11`: 38 tests OK (tag `v10.0.0` present locally, so the end-to-end class ran).
- **Posture table**: the test requires the five clients, no `Pi` row, 5 rows, and "observed" only in the Claude Code status cell; `implementation/PREREQUISITES.md` § Per-client posture has exactly those five rows (Claude Code, GitHub Copilot / VS Code, Opencode, Gemini CLI, Cline) and the Claude Code-only legend.

## 5. Code quality

- New and changed functions are short: `notice_previous_pi_install` 16 lines, `emitMcpVscode` 14, no new parameter lists over 4; early returns used. `usage()` (69 lines, a heredoc) is pre-existing and unchanged in shape.
- Dead code: none left. `KEPT_KEY_PARENTS` and `SERVER_WRAPPERS` in `merge-mcp-json.py` still have readers (the generic guards; `servers` is the vscode wrapper); `selectedFor` replaced every `emittedFor` call; the `"dropped"` note kind and its hint were removed with the function.
- Comments: no comment in code still describes Pi behaviour (acceptance grep). TL-T773-03 and TL-T773-04 are wording nits.
- The Pi notice is a second function beside the Cursor notice rather than one table-driven function; D5.4 allowed either, and the Cursor behaviour is unchanged.

## 6. Gates (worktree at `dc8042bc`)

| Command | Result |
|---|---|
| `node implementation/scripts/sync.mjs --root implementation --check` | OK, no drift across 404 files |
| `python3 implementation/scripts/generate-registry.py --check` | registry is up to date |
| `python3 implementation/scripts/check-maturity.py --root implementation` | all pass, 0 fail |
| `python3 scripts/check-version-consistency.py` | PASS (canonical v10.0.0) |
| `python3 docs/tasks/validate-tasks.py` | PASS (10 active, 565 completed) |
| `python3 scripts/scorecard.py --check` | OK, 34 cases, 30 pass, 0 regressions |
| `python3 -m unittest tests.functional.test_golden_held_out_isolation` | 8 tests OK |
| `python3 -m tests.functional.test_root_install_parity --print-drift` | 27 paths, equal to the baseline `drift` list |

## Not verified

The full test suite (the orchestrator runs it); the security assessment of the notice code (security half of T773); TL-T773-03's claim for clients other than claude-code; behaviour in CI of the new `v10.0.0` fetch (read, not run).

## VERDICT: CONDITIONAL_PASS

### Reviewed Artifacts
- Implementation: `agent/technical-writer/T772` at `dc8042bc` (MR !659); Pi commits `fcb796ff`, `eab26b7a`, `bcc77144`, `bff76906`, `2bf74005`
- Against requirements: the user's request of 2026-11-07, "Remove PI support completely" (as recorded in `pi-removal-inventory-v1.md`), and plan-146 Part B
- Against architecture: `docs/decisions/ADR-013-drop-pi-platform-support.md`, `docs/artifacts/pi-removal-inventory-v1.md`

### Decision IDs Referenced
- ADR-013 (D1-D11), ADR-010 (precedent)

### Conditions (for CONDITIONAL_PASS)
- [ ] TL-T773-01: record `tests/functional/test_gitlab_token_handling.py:475` and `tests/functional/test_verify_release_docs.py:1929` as accepted residue of the D1 acceptance grep (ADR-013 is immutable, so in the S3 checkpoint or the v11.0.0 plan) — owner: orchestrator; due: before S3 (T774). No code change required.

TL-T773-02 to -04 are nits, optional, not conditions.

### Blocking Issues (for FAIL)
- None.

### Merge Authorization
- Merge permitted: Yes, with conditions tracked (subject also to the security half of T773 and the full suite)
- Reviewed by: Tech Lead
- Review mode: read-only (no modifications made to source)

## Gate Verdict

**Gate:** implementation
**Verdict:** CONDITIONAL_PASS

[VERDICT] gate=code-review verdict=CONDITIONAL_PASS task=T773 target=dc8042bc
