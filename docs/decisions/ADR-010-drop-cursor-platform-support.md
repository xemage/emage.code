# ADR-010 — drop-cursor-platform-support

> Filename: `ADR-010-drop-cursor-platform-support.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted on 2026-10-16 by the user (AskUserQuestion, option labels verbatim): Q1 "v9.0.0 (MAJOR), no deprecation release (Recommended)"; Q2 "B: error plus read-only notice, never delete (Recommended)"; Q3 "Yes, delete both trees (Recommended)"; Q4 to Q7 "Accept all four defaults (Recommended)". The decision to drop Cursor is the user's, 2026-10-16, verbatim: "I want to drop Cursor support completely".
- **Date**: 2026-10-16
- **Decider(s)**: solution-architect drafted it. Acceptance is reserved to the user.
- **Tasks**: T661 (this ADR and `docs/artifacts/cursor-removal-inventory-v1.md`). T662 (implementation; § Task breakdown proposes a split). Plan-123 tasks that touch the same files and must be sequenced against it: T663, T666, T667, T668, T671, T672, T673, T674, T675, T677.
- **Requirements**: there is no `requirements-vN.md` for this work; the requirement is the user's sentence above, recorded in `docs/plans/plan-123-post-release-follow-ups.md` (Goal, Task Decomposition item T661, Open Questions) and `docs/tasks/task-T661.md`.
- **Based on**: `docs/plans/plan-123-post-release-follow-ups.md`; `docs/artifacts/cursor-removal-inventory-v1.md` (the factual base; every claim below that I re-read in the code is marked "verified", the rest is quoted from it); `docs/releases/v8.0.0.md` (K-15, K-16, Install table, Migration Guide format M-1 to M-9, Gate Verdicts); `CONTRIBUTING.md` § Releasing (SemVer, line 148) and § Adding a new platform; `implementation/knowledge/skills/release-workflow/SKILL.md` § Semantic Versioning (lines 21-40) and the Release Gate Checklist (line 120, migration guide for a MAJOR version or breaking changes); `docs/artifacts/protected-paths-v1.md`; `docs/artifacts/security-review-release-v8-v2.md` (SEC-T650-02); ADR-002 (provenance sidecars), ADR-008, ADR-009 (ADR format and immutability).
- **Extends**: nothing.
- **Supersedes**: nothing. It amends in scope only, without editing them: the Cursor rows and the "7 platforms" counts of ADR-002 and of the immutable artifacts `mcp-server-denials-v1.md`, `mcp-tool-name-mapping-v1.md`, `mcp-platform-contract-v1.md` and `-v2.md` describe the platform set of v8.0.0 and stay as historical records. Read them together with this ADR once it is accepted.

## Context

### What is taken and what is open

The user decided on 2026-10-16 to stop supporting Cursor altogether. The earlier plan was to fix the Cursor part of SEC-T658-01 with a Cursor CLI deny list; the decision replaces that with removal (plan-123, Goal). What the decision does not say, and this ADR settles, is: how far the removal reaches, what happens to `scripts/install.sh` runs against projects that already have a `.cursor/` install, which version number the change carries, whether the protected golden suite must change, and in what order T662 does the work.

### Verified facts (re-read in this worktree at develop `6b0f8f2` plus the inventory commits)

| # | Fact | Where (verified by reading) |
|---|---|---|
| V1 | The generator is manifest-driven. `main()` reads every `platforms/*.json` whose name does not start with `_`; deleting `cursor.json` stops Cursor generation. | `implementation/scripts/sync.mjs` 756-780 |
| V2 | `syncPlatform` removes the output directory (`fs.rm(outRoot)`) **only for a manifest that exists**, and `--check` compares only files it would generate. After `cursor.json` is deleted, an orphan `implementation/.cursor/` is neither deleted by `sync` nor reported by `sync --check` or `verify.mjs` (a thin wrapper of `--check`). The removal commit must `git rm -r` it. | `sync.mjs` 625-631, 606-623; `verify.mjs` 1-41 |
| V3 | `emitMcp` has one shared branch `format === 'vscode' \|\| 'cursor'` (456-475). The `cursor` side emits `{ mcpServers: { <name>: { url[, headers] } } }` for remote servers (no `type`) and `{ command, args[, env] }` for stdio, with `${env:VAR}` placeholders. Any other value falls through to `throw new Error('Unknown MCP format: ...')` (566). `syncPlatform` branches on a format only for `opencode` (707). The comment at 574-575 names cursor. | `sync.mjs` |
| V4 | **`implementation/platforms/pi.json` sets `"mcp": { "format": "cursor" }`** (line 31). Pi therefore depends on the Cursor emit branch; deleting the branch or the value breaks Pi's `.pi/mcp.json`. | `pi.json` 28-32 |
| V5 | Other consumers of the format string: `tests/functional/test_mcp_platform_conformance.py` keys `_SERVER_MAP_BY_FORMAT[manifest["mcp"]["format"]]` (lines 70-77, 153, 183, 200), so Pi is looked up under `"cursor"`; `tests/functional/test_platform_projections.py` 413-439 (`shape_by_format`, `template_by_format`, `format_by_platform = {..., "pi": "cursor", ...}` and a comment saying so); prose in `CONTRIBUTING.md` 138-139 ("as `pi.json` currently does with `cursor`'s"), `docs/wiki/mcp-servers.md` 256-257 (inventory), and the historical `docs/artifacts/mcp-header-url-templating-design-v1.md` and `-v2.md`. No other code reads the value: `generate-registry.py`, `check.py`, `verify.mjs`, `sync.sh` and `merge-mcp-json.py` are generic (read: `verify.mjs`, `sync.sh`, `generate-registry.py` 95-175). `implementation/platforms/_manifest.schema.json`, to which every manifest's `$schema` points, is not tracked, so whether it enumerates format values could not be checked **(unverified)**. | as listed |
| V6 | Installer: `platform_managed_paths` has the `cursor)` case (358); `list_managed_paths` expands `all` over `cursor github gemini opencode pi claude-code cline` (405); `validate_before_update` loops over `.github .cursor .gemini ...` with a `.cursor` exception text (974-986); `install_cursor()` (1148-1151); the dispatch has `cursor)` (1189) and `all` calls `install_cursor` (1198); an unknown platform prints `error: unknown platform '<x>'` and exits 1 (1206-1208). `--platform` is **not validated at parse time** (84): for an unknown value the script already ran `mkdir -p "$TARGET"` (996) and, on `--update`, `require_existing_install` and `validate_before_update` before it fails at 1207. | `scripts/install.sh` |
| V7 | Today `--update` and `--projections-only` run `sync_tree_into` for `.cursor` with excludes `mcp.json` and `mcp.json.provenance.json`: `rsync -a --delete` (or the `rm -rf` and copy fallback). Files a user added inside `.cursor/` are deleted, and the installer says so on stderr (986: "replaces ... entirely (rsync --delete)... Other local edits there will be lost."). `.cursor/mcp.json` is merged by `merge-mcp-json.py` with the ADR-002 sidecar rules. | `install.sh` 771-846, 880-889, 971-991, 1148-1151 |
| V8 | `--projections-only` and `--update` can only touch trees the installer still knows. After removal the loop in `list_managed_paths` and the dispatch no longer name `.cursor`, so **a leftover root `.cursor/` is never refreshed, deleted or guarded**. | `install.sh` 395-409, 1188-1210 |
| V9 | The root parity gate is blind to an orphan root tree: `compute_drift` compares only files that a fresh `--platform all` install ships, and `_root_only_drift` looks only at trees parsed from `install.sh` (`parse_replaced_trees`). A root `.cursor/` that no `install_tree_into` line names is not examined. `test_install_contract_is_parsed` currently **requires** `.cursor` among the parsed trees (162-164), and the detector test deletes `.cursor/mcp.json.provenance.json` as its MCP example (243-246). | `tests/functional/test_root_install_parity.py` |
| V10 | `render_installed_agents.py`: `PLATFORM_MAP["cursor"]` (19-24), the argparse `choices` (162) and the `all` branch iterating `PLATFORM_MAP` (65-105), so the root and installed `AGENTS.md` list the `.cursor` paths today. The `render` regexes match phrases, not counts, so shrinking the map keeps them valid. | `scripts/render_installed_agents.py` |
| V11 | All four golden cases that mention Cursor read **only their own `fixture/` directory** and never the repository's `.cursor`. See D5. | the four `expect.py` files |
| V12 | `package.schema.json` allows `supportedPlatforms` items `github`, `gemini`, `opencode`, `cursor` only (already stale: no `pi`, `claude-code`, `cline`), `generate-registry.py:119` has the same list as a fallback when `platforms/` is missing, and `tests/fixtures/packs/sample-pack/pack.json:9` declares `cursor`. | `implementation/registry/package.schema.json` 20-24; `generate-registry.py` 116-120 |
| V13 | `docs/releases/_template.md` line 23 carries the install row `\| Cursor \| cursor \|`; `scripts/verify-release-docs.py` has no platform logic (required files and sections only), so removing the row cannot fail the release gate. | read |
| V14 | `servers.yaml` mentions `.cursor/mcp.json` as an output (line 7) and says "Cursor has no such mechanism and stays open" (line 60). Both are comments; the generated MCP files are unaffected. | read |
| V15 | `test_mcp_tool_name_mapping.py` 313-320 asserts `len(files) >= sources * 6` over `implementation/.*/agents/*`, with the comment "Six platforms project agent files". Removing Cursor leaves five, so this test **fails on the floor** unless edited. `test_mcp_package_pins.py` 369 has `>= 5 * 20` over five platforms (still passes at four, but the floor is then loose). The inventory did not list these two. | read |
| V16 | Live text with counts that change: `context-retriever.md:30` ("the other 6 platforms"), `skillify.md:50` ("the other six platforms") **and `skillify.md:52-53` ("lists all seven folders", "the other six")**, `docs/wiki/mcp-servers.md:275` ("all 7 platforms"), `test_root_install_parity.py:3` ("eight platform trees"), `test_mcp_platform_conformance.py` 9, 31, 137, 170, 178, 190 ("7"). | read |

### Corrections to the inventory

1. The inventory does not say that `sync --check` and the parity gate cannot see an orphan tree (V2, V9). That is the most important constraint on the removal commit.
2. V15 and the `skillify.md:52-53` counts are additions.
3. SEC-T650-02 (inventory § 11) was already **fixed** in the T645 amendment (`security-review-release-v8-v2.md` row SEC-T650-02, and `docs/releases/v8.0.0.md` line 277). What disappears with Cursor is the optional tail of that row, "optional research and emission as part of the SEC-T658-01 plan", and the plan-123 intent to emit a Cursor CLI deny list.
4. The inventory counts the root `AGENTS.md` among files that a `--projections-only` refresh re-renders. Verified (V10); it also means S1 changes the render output and therefore declares `AGENTS.md` as drift (D7).

## Decision drivers

1. Completeness: "completely" means no tree, no flag, no manifest, no test pinning, no live doc claim, with a short, explicit list of what stays as history.
2. Do not break Pi (V4) and do not change any other platform's generated bytes.
3. No data loss for adopters: the removal must not delete a project's files, and must be strictly safer than today's sweep (V7).
4. No silent stale security state: a leftover Cursor install keeps frozen MCP pins and, for installs from v7.x or older, the launchers that M-9 of the v8.0.0 notes warns about. The user must be told.
5. The project's own rules: SemVer with a migration guide (CONTRIBUTING 148; release-workflow SKILL 27, 120), immutability of historical records and accepted ADRs, no edit to `tests/golden/**` without a named grant, and the root install changed only through user-approved steps.
6. A gate that cannot see the removal is not a gate (V2, V9): add a guard instead of relying on review.

## Decisions

Each sub-decision lists the options, then my recommendation. The recommendation is the architect's; the user decides where marked in § User decisions needed.

### D1. Scope of removal

**Remove** (the "Cursor classes" of the inventory):

| Class | What | Notes |
|---|---|---|
| Source of truth | `implementation/platforms/cursor.json` | one file |
| Generated trees | `implementation/.cursor/` and the root `.cursor/` (91 files each, inventory § 2) | `git rm -r`; V2 and V8 say nothing else will |
| Generator | the `cursor` format value and the comment at `sync.mjs` 574-575 (after D2); `servers.yaml` comments at lines 7 and 60 | `servers.yaml` header already omits pi, claude-code and cline: correct it to name the outputs generically instead of listing platforms |
| Installer | usage lines 18 and 50, comment 217, `platform_managed_paths`, `list_managed_paths`, `validate_before_update` loop and `.cursor` exception, `install_cursor`, dispatch and `all`, plus the new D3 behaviour; `render_installed_agents.py` `PLATFORM_MAP` and `choices`; `Makefile` lines 12-13 | |
| Registry and metadata | `generate-registry.py:119` fallback; `registry/index.json` regenerated (platforms array, 80 entries' `supportedPlatforms` and `projectionStatus`); `package.schema.json` enum; `tests/fixtures/packs/sample-pack/pack.json:9` (D9) | |
| Tests (outside golden) | edited or deleted per D6 | |
| Live docs | `README.md`, `AGENTS.md`, `implementation/AGENTS.md`, `implementation/README.md`, `implementation/PREREQUISITES.md`, `implementation/SECURITY.md:25`, `CONTRIBUTING.md` (including the "use `cursor.json` as a template" step, which must name another manifest, and the `pi.json`-reuses-`cursor` lesson, which becomes a historical remark or is rewritten for the renamed format), the eight `docs/wiki` pages, `docs/releases/_template.md:23` | inventory § 6 |
| Knowledge text | the seven source files of inventory § 9 and the count words of V16; the 54 generated mirrors follow by regeneration | |
| CI and templates | `.gitlab/issue_templates/Bug.md:16`, `.gitlab/merge_request_templates/Default.md:30` | `.gitlab-ci.yml` needs no change (read in the inventory) |

**Stays untouched** (historical records, edited never): everything under `docs/releases/` (33 files), `docs/artifacts/` (38 files), `docs/plans/`, `docs/checkpoints/`, `docs/tasks/`, `docs/decisions/` (ADR-002 and this ADR) and `docs/archiv/` including the three Cursor-chat exports, which are authoring history and not platform support; `tests/golden/**` (D5); the append-only `_comment` ledger inside `tests/_baselines/root-install-drift.json` (its new "Declared" lines may name the removal). Also kept: `.gitignore:96` `.cursor-tutor/` (a generic ignore of an unrelated editor-side folder; harmless; I did not establish what writes it **(unverified)**) and the false positives of inventory (`cursor:` in CSS of the `ux-designer` agent, a pagination cursor in two Python files, an editor enum in a vendored schema, "real-time cursors" in a golden fixture).

**Acceptance wording for T662** (replaces "no Cursor references remain outside historical records and the migration note"): `git grep -il cursor` over tracked files, excluding the paths above, returns only (a) the false positives, (b) `.gitignore`, (c) the installer's removal message and notice code with their tests, and (d) the migration paragraph in `README.md`. Anything else is a defect.

### D2. Pi and the shared emit branch

Options:

| Option | Description | Verdict |
|---|---|---|
| A. Rename the value to `pi` | `pi.json`: `"format": "pi"`; `emitMcp`: the branch condition becomes `'vscode' \|\| 'pi'` and the wrapper selection tests `'pi'`; tests and prose follow. Every other format value names its platform (`claude-code`, `cline`, `gemini`, `opencode`; `vscode` is the exception for Copilot), so `pi` is consistent. A format that is named after its only user cannot be copied silently by the next platform, which is exactly the T360 lesson in CONTRIBUTING 129-144. | **Recommended** |
| B. Neutral name (`mcpServers-url`) | Same change with a descriptive value. Reads as reusable, which invites the copy-a-sibling mistake that T360 documents. | Acceptable alternative, same cost |
| C. Keep `"cursor"` as an internal alias | No change to Pi. Leaves the string in the manifest, the generator and two tests, contradicts "completely", and keeps a branch named after a platform that no longer exists. | Rejected |

Requirements for the change, whichever name is chosen:

1. Rename and removal land together in the same MR, as **separate commits in this order**: (1) rename (manifest, `emitMcp` condition, the two tests that key on the string, prose), (2) delete Cursor. After commit (1) `node implementation/scripts/sync.mjs --root implementation` must leave `implementation/.pi/mcp.json`, `.pi/mcp.json` and both provenance sidecars **byte-identical** (`git diff --exit-code` over `implementation/.pi .pi` is the acceptance check). The branch must not change output for Pi or for `vscode`.
2. `test_mcp_platform_conformance.py`: `_SERVER_MAP_BY_FORMAT` gets the new key and loses `"cursor"`. `test_platform_projections.py`: `shape_by_format`, `template_by_format`, `format_by_platform` and the comment (413-439) use the new name, with the Cursor entries removed.
3. A negative test: a manifest with `mcp.format: "cursor"` makes `sync.mjs` exit non-zero with `Unknown MCP format: cursor` (the existing throw, V3). This is the intended fail-closed behaviour for a fork that still carries the old value; mention it in the migration text for maintainers.
4. T677 (refactor of `emitMcp`, 117 lines) comes later and may split the shared branch; T662 does the minimum so the two do not collide.

### D3. Existing adopter installs

State after removal (verified from V6-V8): `install.sh --platform cursor` reaches the "unknown platform" branch; `--update` and `--projections-only` with `all` no longer list `.cursor`; an existing `.cursor/` is **left untouched and stale**, `mcp.json` is no longer refreshed or pruned, and the leftover would also no longer be guarded against symlinks (it is no longer written, so nothing needs the guard).

Options for what the installer does:

| Option | Behaviour | Data loss | Security | Cost |
|---|---|---|---|---|
| A. Unknown-platform error only | `--platform cursor` fails as any typo; `--update` silently ignores `.cursor/`. | None | Worst: a user sees no sign that the Cursor config is frozen (stale pins; v7.x launchers, see D8) | Nil |
| **B. Early validation with a removal message, plus a notice when a Cursor install is detected; never deletes** | See below. | **None; strictly safer than today** (the sweep of V7 is gone) | The user is told on every `--update` and `--projections-only` until they act | Small: about 25 lines of shell and four tests |
| C. Detect and remove generator-owned files on `--update`, with a notice | Remove exactly the paths listed in `.cursor/.generated-manifest.json`, then empty directories; keep everything else; handle `mcp.json` by pruning the sidecar's `generatorOwnedKeys`. | Low but real: a user who deliberately keeps using Cursor with the harness loses it during an update that they expected to refresh their tools; edits they made to generated files are deleted (as they would have been overwritten before) | Best: closes the stale-pin exposure automatically | Large: new delete path to guard (symlinks via `refuse_unsafe_path`, `--dry-run`, rsync and no-rsync parity), a prune mode for `mcp.json` that does not exist today (`--force-prune-keys` refuses names that are absent and needs a generated `--source` file, which will not exist after removal), tests, and a new security review. Also `.cursor/` is Cursor's own folder, so deleting inside it is an act on a tool the harness no longer owns |
| D. Notice printed once, with state | Needs a marker file in the user's project. | None | As B, minus nagging | Adds persistent state to a project for a one-off message; rejected |

**Recommendation: B.** Specification for T662 (behaviour, not code):

1. **Early platform validation.** Immediately after argument parsing (before `resolve_abs_path`, `mkdir -p`, any guard or write) the value of `--platform` is checked against `github gemini opencode pi claude-code cline all`. An unknown value exits 1 with `error: unknown platform '<x>'` and the supported list; the usage text changes accordingly. The value `cursor` gets its own text, for example: `error: platform 'cursor' was removed in v9.0.0 (see docs/releases/v9.0.0.md). Existing .cursor/ files in your project are not touched. Nothing was written.` Rationale: today a typo creates the target directory first (V6); the new check also covers the removed value with one message. Exit code stays 1.
2. **Detection and notice.** In `validate_before_update` (it runs for `--update` and, because `--projections-only` sets `UPDATE=1`, for both), if `$TARGET/.cursor` is a directory and either `$TARGET/.cursor/.generated-manifest.json` contains `"platform": "cursor"` or `$TARGET/.cursor/mcp.json.provenance.json` exists, print one warning block to stderr, then continue normally with exit 0. Content: Cursor is no longer supported and `.cursor/` is no longer updated, pruned or checked; the MCP server versions and the Playwright hardening in `.cursor/mcp.json` are frozen at the version that wrote them; if the install came from v7.x or older it can still contain unpinned or non-existent launchers (name `@anthropic/mcp-filesystem`, see M-9 of the v8.0.0 release notes); the file is not deleted by the installer; remove it or edit it by hand (point to the migration note). The check **reads**, never writes, and must use `-d` and `grep -q` only. Installs older than the manifest and the sidecar are not detected **(unverified: which release first wrote `.generated-manifest.json`)**; the fallback `.cursor/rules/coding-standards.mdc` may be added if the implementer finds an older release that wrote neither.
3. **No deletion anywhere**, in any mode. `--platform all` simply no longer includes Cursor.
4. **Tests** (replace the deleted Cursor install tests; use `git archive v8.0.0` to build a real pre-removal install, as the v8.0.0 rollback test did, and also a synthetic one): (a) `--platform cursor`, plain, `--update`, `--projections-only`, `--dry-run`: exit 1, the removal message, target directory not created, no existing file changed; (b) a v8.0.0-style target with `.cursor/` plus a user-added `.cursor/rules/own.mdc` and an edited `mcp.json`: `--update` and `--projections-only` exit 0, print the notice, leave every byte under `.cursor/` unchanged (the data-loss regression test; today the same scenario deletes `own.mdc`); (c) a target without `.cursor/`: no notice; (d) a target whose `.cursor` is a symlink: no notice is required, no write through it, exit 0 (it is not a managed path any more); (e) both copiers (rsync and the cp fallback) for (b).

**What the user-facing migration text must say** is drafted in Appendix A.

### D4. Version impact

Removing a supported platform removes a documented value of a public CLI option (`--platform cursor`, README table row, the install table of every release document) and deletes a generated tree that adopters have installed. Under the project's own rule (CONTRIBUTING 148; release-workflow SKILL 25-29, flowchart 33-40: "Has any public API or contract changed in a breaking way? Yes: MAJOR") this is a breaking change and needs a migration guide (SKILL 120).

| Option | What ships | For | Against |
|---|---|---|---|
| **A. v9.0.0, no deprecation release** | The Cursor removal ships with the other plan-123 work in the next MAJOR. The release notes carry a Breaking-changes entry and Migration Guide item (Appendix A). The installer message of D3 serves as the in-product notice. | Matches the user's "completely" without a transition period of work on a platform that is being dropped. Precedent: v8.0.0 itself removed the `fetch`, `docker` and `postgresql` servers and narrowed agent tool grants as breaking entries (A-22, A-25, A-26) with no earlier deprecation release (`docs/releases/v8.0.0.md` 46-70). Several other plan-123 items are probably breaking under the v8.0.0 counting rule as well (T666 and T667 narrow the GitLab grants of the orchestrators, T665 may change token handling), so a MAJOR is likely anyway **(unverified: not yet designed)**. | A MAJOR for a change that some adopters (those not using Cursor) never notice. |
| B. Deprecation cycle: v8.1.0 announces, v9.0.0 removes | v8.1.0 keeps generating `.cursor/`, adds an installer warning on `--platform cursor` and `all`, documents the removal date; v9.0.0 removes. | Gives Cursor users one release of notice. | An extra full release (release branch, five gates, security re-check; the v8.0.0 preparation ran about twenty tasks, T641 to T660) for a warning. Cursor keeps being maintained and regenerated through T663, T666 and T667. The Cursor part of SEC-T658-01 (K-15) stays open for another cycle, against the standing decision "5. C" of 2026-10-09 (fix every residual). The deprecation code is thrown away one release later. The user has already decided to drop it. |
| C. Remove in a MINOR (v8.1.0) | | Fast | Violates the project's own versioning rule; adopters on `^8` get a breaking change; the Migration Guide requirement (MAJOR or breaking) still applies. Rejected. |

**Recommendation: A, v9.0.0**, with the whole plan-123 set shipping in it (the plan's phrase "a v8.x release" is then superseded by this ADR's version decision). The version markers and the release document are the release-manager's work at release time, not T662's. If the user prefers B, T662 changes shape (it must add the deprecation warning and keep generating Cursor until v9.0.0) and this ADR needs a revision before T662 starts; that is why Q1 is first.

### D5. Does the removal require any `tests/golden/**` edit?

**No. No golden edit is required, no grant G-3 is needed, and no baseline v23 is needed for the removal.** Evidence, from reading each case's `expect.py` and, where cited, its fixture:

| Case | Cursor mention | What `check()` reads | Does it still pass with no `.cursor` in the fixture? |
|---|---|---|---|
| `discover-skills-registry-grounded-recommendation` | `brief.md` 23 and 71 (quoted command text and "seven platform projections"); `fixture/implementation/registry/index.json` (159 matching lines, a frozen copy); `expect.py:45` `PLATFORM_DIRS` includes `.cursor` | `fixture/recommendation.md`, and the skills of two fixture roots: `fixture/` (registry present, authoring row) and `fixture/installed-target/` (registry absent, target row). `_target_skills` loops over `PLATFORM_DIRS` and calls `_tree_skill_names(root/<dir>/skills)`, which returns `set()` when the directory does not exist (lines 64-68, 83-87). | Yes. Neither fixture root has a `.cursor` directory (read attempts of `fixture/.cursor` and `fixture/installed-target/.cursor/skills` both returned "does not exist"; the installed-target root carries `.github/skills/` per `brief.md` 71). The constant is a superset of the live platform list afterwards, which is harmless. |
| `skillify-skill-file-template-drift` (`known_failing` until T668) | `brief.md` 24 and 89; `expect.py` docstring line 17 and `DECLARED_SKILL_ROOTS` line 66 pin `.cursor/skills` | the fixture's declared skill roots: `existing_roots = [root for root in skills_roots if root.is_dir()]` (line 83); a missing directory is skipped | Yes. `fixture/.cursor/skills` does not exist (read attempt). T668 replaces the fixture by a copy of `gitlab-api-push-fallback/SKILL.md` under `implementation/knowledge/skills/`, which T662 does not touch. |
| `plan-task-creation-precondition-real` | fixture `plan-030-mcp-remote-transport-alignment.md` and `task-T365.md` quote Cursor text | `fixture/docs/tasks/task-T365.md` and the plan it cites; checks `T365` appears in the plan text | Yes: it never inspects platform directories. Cursor words in the fixture are historical content. |
| `prepare-release-real-verdict-missing` | the former v7 release-document fixture under `fixture/docs/releases/` (line 12, the install row, read) | the `## RELEASE VERDICT` fields of the single document in `fixture/docs/releases/` | Yes: the Install table is irrelevant to the check. T668 replaces the fixture by a copy of `docs/releases/v8.0.0.md`, which also names Cursor and is a frozen historical record. |

Consequences and conditions:

1. The `brief.md` quotes of the live command text, the "seven platform" wording and the extra `.cursor` entries in two constants become frozen evidence that no longer equals the live command. That is by design (a golden case is a snapshot of a contract at a date) and is not a defect.
2. T668 (G-2) and T669 (baseline v22) are independent of T662. T662 must not edit any file under `tests/golden/**` and must not touch `scripts/scorecard.py`; its acceptance includes `python3 scripts/scorecard.py --check` unchanged and the evaluator-hash check passing with no drift.
3. An optional later alignment of the two constants and the "seven" wording could ride along with a future golden task; it is not needed for this removal and I do not recommend scheduling it. Whether any test compares a golden `expect.py` constant with the manifests **could not be established by reading** (I did not find one; the full suite will show) **(unverified)**.
4. If, against this finding, T662 meets a failing golden case, it stops and reports to the orchestrator (plan-123 T662: "stops at that point and the orchestrator brings a grant (G-3)"). Do not "fix" it by editing the case.

### D6. Tests

**Delete outright** (they test Cursor itself): `test_install_script.py::test_cursor_mcp_json_merge_on_update` (357-411); `test_install_script.py::test_update_prunes_retired_generator_owned_key_via_sidecar_history_cursor` (797-801; its gemini, opencode, pi and cline siblings stay, so the five per-tree-platform sidecar-survival assertions of ADR-002 become four); `test_install_agents_mapping.py::test_cursor_install_rewrites_agents_paths`; the Cursor entries of the lookup tables listed below; `tests/functional/test_context_retriever.py` 319-323 is a synthetic platform name in a generic test and is **edited** to a remaining platform, not deleted.

**Edit (count-sensitive, will fail if left)**:

| File | Change |
|---|---|
| `test_manifests.py:18` | required list drops `cursor` (the test name says "at least four platforms"; leave) |
| `test_mcp_platform_conformance.py` | "7 platforms/manifests" becomes 6 in the assertions at lines 137, 178, 190 and in the docstring and comments (the "7 core + 10 extended" at 52-53 is a server count and stays); the test names that say "seven"; `_SERVER_MAP_BY_FORMAT` loses `"cursor"` and gains the D2 name; the regression-injection test (237-251) uses another `mcpServers`-wrapper platform (for example `cline`) and its final `assertIn("cursor", ...)` becomes that platform's name |
| `test_platform_projections.py` 405-439 | D2 |
| `test_mcp_tool_name_mapping.py` | `EXPECTED_STYLE` and its comment drop `cursor`; `GeneratorRunTests.test_rendering_per_platform` drops the `.cursor/agents/fx.mdc` case (203); **line 318: `sources * 6` becomes `sources * 5` and the comment "Six platforms" becomes "Five"** (V15); `ArtifactTests` line 327: remove `"Cursor"` from the required platform tuple (the artifact stays; D6 note below) |
| `test_mcp_server_denials.py` | `GENERATED_MCP` loses `cursor` (65); the two platform tuples at 160 and 334 lose it; `DocumentationTests`: remove `"Cursor"` from the artifact needle list (605), and **remove the `assertRegex(text, r"(?i)cursor")` at 631**; keep every other assertion. The `assertNotRegex` of 642-648 stays (it forbids a sentence that no longer exists; harmless) |
| `test_mcp_package_pins.py` | `PROJECTIONS` (35), `PLAYWRIGHT_ENTRY_PATHS` (70), the 401 list, the `.cursor/agents/*.mdc` glob (368) and the `assertGreaterEqual(len(files), 5 * 20)` floor becomes `4 * 20`, the `platforms` dict entry (509) and its docstring (503) |
| `test_mcp_secret_guard.py` | `GENERATED_MCP_FILES` loses two entries (82, 89); line 280 uses `.cursor/mcp.json` only as a *fake relative path* in a negative test of the allowlist: change it to `.pi/mcp.json` |
| `test_placeholder_flag_text.py:26` | drop the `.cursor/agents/*.mdc` mirror from `SE_MIRRORS` (the other tuple is derived) |
| `test_root_install_parity.py` | docstring "eight" becomes "seven"; `test_install_contract_is_parsed` loses `.cursor` (162); the detector test (243-246) uses `.cline/mcp.json.provenance.json` and expects `{".pi/mcp.json", ".cline/mcp.json", ".cline/mcp.json.provenance.json"}` |
| `test_install_script.py` | symlink matrix case `cursor-mcp-file` (1398) becomes a pi or cline case; `single-other` (1409-1416) uses `.pi` as "not claude-code's path"; the sentinel in `_sentinel_target` (1482) and the `.cursor` link/lock tests (1505, 1555, 1595) use `.pi/instructions/coding-standards.md` and `.pi`; the managed-path list assertion (1505) loses `.cursor` |
| `test_install_agents_mapping.py` 55 | drop the `.cursor/skills/` assertion of the `all` test |
| `test_install_projections_only.py` | `HARNESS_TREES` (35) and `STALE_EDITS` (85, use `.pi/prompts/plan.md`) lose `.cursor`; the merge-owned set at 338 loses `.cursor/mcp.json` (seven configs become six) |
| `test_install_target_inside_repo.py` 11-12, 89 | re-point the `--target implementation/.cursor` example to a remaining tree (the T559 case is generic) |
| `test_install_type_conflicts.py` | `SHIPPED_FILE` (39) becomes a Pi file, for example `.pi/instructions/coding-standards.md`; the `.cursor/commands/plan.mdc` stale file (106) becomes `.pi/prompts/plan.md` and the `.cursor` tree snapshots (107, 116, 145-155) become `.pi` (Pi also excludes `mcp.json`, so the "kept path" case of 135-155 carries over) |
| `test_link_integrity.py:35` | drop `.cursor` from the skipped mirror directories (a root `.cursor/` no longer exists) |
| `fixtures/packs/sample-pack/pack.json:9` | D9 |
| Tidy only (no behaviour): `test_publish_release.py` 302-307 (`# Cursor` becomes another platform in a synthetic fence); `test_check_version_consistency.py` 399-403 (drop the `.mdc` suffix and `release-manager.mdc`); `test_mcp_schema_validation.py:23` docstring | |

**Add**: (1) the D3 tests; (2) the D2 negative test; (3) an **orphan-tree guard**, because V2 and V9 show that neither `sync --check` nor the parity gate would notice a regrown or leftover tree: for every `implementation/.<dir>/.generated-manifest.json` (and every root `.<dir>/.generated-manifest.json`), the directory must equal the `outputDir` of some `platforms/*.json` whose `platform` equals the manifest's `platform` field; the test asserts that `.cursor` is absent at both levels as a named case so a revert is loud.

**Documentation assertions and the immutable artifacts.** `test_mcp_server_denials.py::DocumentationTests` and `test_mcp_tool_name_mapping.py::ArtifactTests` currently require the word "Cursor" in the live docs and in `mcp-server-denials-v1.md` and `mcp-tool-name-mapping-v1.md`. The artifacts are immutable and keep their Cursor rows as the evidence of what v8.0.0 shipped. The tests change, the artifacts do not: the required-word assertions are deleted as listed above, and no replacement "must not contain Cursor" assertion is added for the artifacts. Live docs that cite those artifacts as evidence should add the clause "recorded before Cursor was removed" once, where they cite them (S2). This ADR is the pointer for readers of the artifacts. A `-v2` of either artifact is not needed.

T673 (test quality, SEC-T658-06) will later rework the same documentation tests; it should start after S1 merges.

### D7. Root install and drift

Verified behaviour (V8, V9): after the installer forgets `.cursor`, `--projections-only` leaves a root `.cursor/` untouched, the parity gate does not flag it, and `sync --check` does not flag `implementation/.cursor/` (V2). So deletion must be explicit.

Options: (a) delete the root `.cursor/` in the implementation MR (S1) together with `implementation/.cursor/`; (b) delete it in the root-refresh MR (S3).

**Recommendation: (a).** Reasons: the leftover tree has no owner after S1 and nothing in the toolchain can reach it; a leftover tree plus an orphan guard test that must then exempt it is worse than one deletion; `git rm -r` of tracked files is reviewed in the same MR as the code that makes it unreachable; it needs no installer run. This is a deletion of the repository's own tracked files, not a refresh of the harness, but because the standing rule is that a root refresh needs the user's approval (plan-123 Constraints), Q3 asks the user to confirm that approving this ADR also approves the deletion of the root `.cursor/`.

Drift baseline (`tests/_baselines/root-install-drift.json`, format per the task constraints: sorted `--print-drift` paths plus one comment line starting `Declared <date> by <task> (`):

- After S1: the only expected drift is `AGENTS.md` (the rendered `all` branch no longer lists `.cursor`, V10), plus the root `.cursor/` is simply gone. Declare it.
- After S2: add the root mirrors of the edited knowledge files on the remaining platforms (inventory § 9 counts 54 mirror files at root and under `implementation/` together; the `implementation/` side is regenerated in S2, the root side is the drift) and the further `AGENTS.md` change. Declare exactly what `--print-drift` prints.
- S3 (the `--projections-only` refresh, user-approved, run by the orchestrator): drift returns to `[]`. In a fresh worktree, touch the source mtimes first (the note in the baseline's comment of the nineteenth refresh).
- The existing `_comment` ledger is not edited, only appended to.

### D8. Security effects

Disappear with Cursor:

| Item | Effect |
|---|---|
| K-15, the Cursor part | "not in force on Opencode, Gemini CLI and Cursor", "In the Cursor IDE no such mechanism is documented", the CLI `permissions.deny` remark and "reachable by every agent on ... Cursor" go; K-15 keeps Opencode, Gemini CLI and Pi |
| K-16, the Cursor part | "not in force on Opencode, Gemini CLI and Cursor (K-15)" |
| SEC-T658-01 | one of its three accepted unfixable parts (Cursor IDE) disappears. The user's acceptance of 2026-10-15 stands for the other two (Gemini CLI per-agent scoping, Pi agents with no `mcp__` entry) and needs no new decision. The "Cursor CLI deny list" half of the fixable parts is cancelled, not fixed. T663 (Opencode per-agent denies) is unaffected |
| SEC-T650-02 | already fixed in text (correction 3); its optional research/emission tail is cancelled |
| SEC-T657-01 (re-scoped into SEC-T658-01) | the Cursor row of the analysis ends |
| Documents | the Cursor rows of the tool-name and denial tables in `docs/wiki/mcp-servers.md` (76, 97, 335-344 manual check) and the AGENTS.md sentences "Cursor documents no such mechanism and stays open" |
| Surface | 28 generated agent files (per tree) whose `tools` lists carry `mcp__` names that Cursor does not enforce (K-15), a 17-server MCP config that no gate checked for enforcement, and Cursor entries in the pin and secret-guard tests that must be kept in step at every pin bump (`test_mcp_package_pins.py`, `test_mcp_secret_guard.py`) |

New risks and mitigations:

1. **Stale `.cursor/` in adopters' projects keeps frozen MCP entries.** Exact pins stop receiving bumps (the pin policy of `servers.yaml` assumes `--update` delivers them), the hardened Playwright arguments stop receiving fixes, and a `.cursor/mcp.json` from v7.x or older still contains `npx -y @anthropic/mcp-filesystem` (E404 on npm, scope not controlled by the vendor, `docs/releases/v8.0.0.md` M-9) and, if the install is older, `e2b-mcp` (unscoped, claimable). **Before this change, `--update` from v8.0.0 would have pruned `docker`, `postgresql`, `fetch` and the others through the sidecar; after it, nothing prunes anything in `.cursor/mcp.json`.** An adopter who goes from v7.x straight to v9.0.0 never gets the v8.0.0 clean-up for that file. Mitigation: the D3 notice (names the risk and M-9), the migration text (Appendix A) that tells them to follow M-9 from the `v8.0.0` tag or delete the file, and the Known Issues entry of the release.
2. **A user who stays on an old release** keeps the sweep behaviour of V7 and the old Cursor residuals; this is no worse than today. A rollback from v9 to v8.x with `--update` regenerates `.cursor/`, and D3 option B means v9 has not deleted anything in the meantime.
3. **`--platform all` changes meaning** for CI that expected `.cursor/` to appear: it now silently installs six platforms. The explicit `--platform cursor` fails loudly (exit 1). A script that uses `all` and then reads `.cursor/` fails in its own step; the release Breaking-changes entry names it.
4. **Drift of the orphan kind** (a leftover or regrown tree) is not detected by existing gates: closed by the D6 orphan guard.
5. **Fork manifests** with `mcp.format: "cursor"` fail with `Unknown MCP format` (fail-closed).
6. A mistake in the new detection code could read from a target path that is a symlink: the check only reads (`-d`, `grep -q`), writes nothing, and a symlinked `.cursor` is no longer a managed path. The Security Engineer review of S1 covers this.

### D9. Registry, pack schema and metadata

`generate-registry.py` takes its platform list from `platforms/*.json`, so regeneration drops `cursor` from `registry/index.json` and updates the per-entry `checksum` values for the seven edited knowledge files. The two hard-coded lists need a decision: (a) remove `cursor` only (leaves the list stale and `pi`, `claude-code`, `cline` still rejected by the schema), or (b) replace them with the six current platforms. **Recommendation: (b)**: it is the same line, it removes an already-wrong schema, and it is what the fallback should say. It changes what a pack may declare, so it is a small additional compatibility change; a pack that declares `cursor` is rejected by the schema afterwards. The sample pack's `supportedPlatforms` is edited to platforms in the list. Low impact (the packaging workflow is an authoring-side feature **(unverified: `scripts/package.py` was not read)**); Q5 lets the user veto (b).

## Decision record (2026-10-16)

The user accepted this ADR with the recommended option for every question: version v9.0.0 with no deprecation release (Q1 A); adopter behaviour B, a removal message and a read-only notice, never deleting (Q2); approval to delete the tracked root `.cursor/` and `implementation/.cursor/` in S1 (Q3); the Pi format value `pi` (Q4), the pack schema and registry fallback listing the six current platforms (Q5), the T662 split into three steps (Q6), and no golden edit, no grant G-3 and no baseline v23 (Q7). The orchestrator split T662 into **T662 (S1)**, **T678 (S2, documentation)** and **T679 (S3, root refresh, needing the user's approval at that step)**; plan-123 carries an addendum for T678 and T679.

## Task breakdown for T662

T662 as written (L, devops-engineer with technical-writer) edits about 110 tracked non-historical files (inventory: 20 live docs and templates, 7 knowledge sources, 54 generated mirrors, 8 code and config files, 20 tests) and deletes about 183 (two 91-file trees and the manifest). I recommend the orchestrator split it into three rows (IDs assigned by the orchestrator; I call them S1-S3), because the tests that currently require the word "Cursor" in live docs must change before the docs do, and because the root refresh is a separate user-approved step.

Order and dependencies: S1, then S2, then S3. S2 depends on S1 (otherwise `DocumentationTests` fail); S3 depends on S2 (so one refresh carries the final text).

| Step | Owner | Content | Acceptance criteria |
|---|---|---|---|
| **S1: generator, installer, registry, tests, trees** | devops-engineer (shell, tests); Security Engineer review of the diff afterwards; Tech Lead review; QA run of the scenario test | Commit 1: D2 rename (manifest, `emitMcp`, the two keyed tests, prose in the changed files). Commit 2: delete `platforms/cursor.json`; `git rm -r implementation/.cursor .cursor`; `render_installed_agents.py`; `install.sh` per D3 and D1; `generate-registry.py` fallback and `package.schema.json`/sample pack (D9); `Makefile` 12-13; `servers.yaml` comments (7, 60); regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`; every test change of D6 including the new tests; declare drift (`AGENTS.md`) | (1) After commit 1, `implementation/.pi`, `.pi` and all other trees are byte-identical (`git diff --exit-code`). (2) After commit 2, `git ls-files` lists no `.cursor/` path at root or under `implementation/`, no `cursor.json`; `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py`, `scorecard.py --check`, `validate-tasks.py`, the evaluator-hash check (no drift), `test_golden_held_out_isolation` and the full suite pass. (3) D3 tests pass under rsync and cp. (4) Scenario: build a real v8.0.0 install with `git archive v8.0.0`, run the new installer with `--update` and `--projections-only`: exit 0, notice printed, every file under `.cursor/` byte-identical, user file kept. (5) `--platform cursor`: exit 1, message, no directory created. (6) No change under `tests/golden/**` or `scripts/scorecard.py` (`git diff --stat`). (7) `git grep -il cursor` limited to the D1 allowed list plus the S2 files not yet edited. (8) Orphan guard test present and failing when a `.cursor/.generated-manifest.json` is added to a scratch copy. |
| **S2: live docs, knowledge text, templates** | technical-writer (no shell: the orchestrator commits and runs the two generators); Security Engineer reads the changed security statements | The doc list of D1; the seven knowledge files and the count words of V16 (`skillify.md:50-53` included); `docs/releases/_template.md` (row 23 removed; nothing else changes in the template); `.gitlab` templates; `CONTRIBUTING.md` "Adding a new platform" step 1 names another manifest (for example `claude-code.json`) and the T360 lesson is rewritten without `cursor`; README gets one short paragraph "Cursor support was removed in v9.0.0 (see the release notes)" in the supported-platforms section; the one clause "recorded before Cursor was removed" where live docs cite the two immutable artifacts; regenerate mirrors and registry; extend the drift declaration | (1) The D1 acceptance grep. (2) `test_link_integrity` passes (the `cursor.json` links of `CONTRIBUTING.md` and `docs/wiki/contributing-workflow.md:63` are gone or re-pointed; the wiki directory itself is skipped by that test, so check its links by hand). (3) No sentence says a platform count that is now wrong (sweep for `\b(6\|six\|7\|seven\|8\|eight)\b` near "platform" and "folder"). (4) All gates of S1 pass; drift baseline lists exactly the paths `--print-drift` prints. |
| **S3: root refresh** | orchestrator, with the user's approval for this step (plan-123 Constraints) | `scripts/install.sh --target . --platform all --projections-only` on the S2 tip; empty the drift list and add the "Emptied" line | `--print-drift` prints `[]`; the suite passes; `git status` shows no `.cursor` path; no file under `docs/` or `implementation/` changed by the refresh. |

Sequencing against other plan-123 tasks (same files; coordinate by merge order, not by design):

| Task | Shared files | Rule |
|---|---|---|
| T663 (Opencode per-agent denies) | `sync.mjs emitMcp`, `test_mcp_server_denials.py`, `test_mcp_tool_name_mapping.py`, docs | whichever merges second rebases; T662 S1 touches only the format string and the Cursor test entries |
| T666, T667 (GitLab sets) | `test_mcp_package_pins.py` (`platforms` dict), agents | same; T666 must not add a Cursor entry to the dict |
| T672, T673, T674, T675, T677 | `install.sh`, `sync.mjs`, the same tests, the docs, `emitMcp` | start after S1 (T672, T673, T677) or after S2 (T674) |
| T668/T669/T670 | `tests/golden/**` | independent of T662 (D5); no ordering needed |
| T671 | register | mark the Cursor items "closed as obsolete (Cursor removed)" |

**Gates for S1 and S2** (from the task constraints): `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash with no drift, `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file`. The brief for S1 must say that the agent never opens `tests/golden/held-out/`.

## User decisions needed

Gating (T662 cannot start without these):

- **Q1. Version.** A: v9.0.0 with no deprecation release (recommended). B: v8.1.0 deprecation notice, then v9.0.0 removal. (C, remove in a MINOR, is not offered.) The installer message of D3 names the version.
- **Q2. Adopter behaviour.** B: removal message, notice, never delete (recommended). Alternatives: A (nothing) or C (remove generator-owned files with a notice).
- **Q3. Root `.cursor/`.** Confirm that approving this ADR also approves deleting the tracked root `.cursor/` (and `implementation/.cursor/`) in S1, so that S3 needs no deletion (recommended). The alternative is to delete it in S3 under its own approval.

Defaults the user may veto:

- **Q4.** The Pi format value is `pi` (D2 A) rather than `mcpServers-url` (D2 B).
- **Q5.** The pack schema enum and the registry fallback list the six current platforms (D9 b) rather than only dropping `cursor`.
- **Q6.** Split T662 into S1, S2 and S3 (recommended) or keep one task.
- **Q7.** Confirm that no `tests/golden/**` edit, no grant G-3 and no baseline v23 are planned (D5); plan-123's Open Question on golden files that mention Cursor is closed by this finding.

Already decided and not asked: the three Cursor-chat exports under `docs/archiv/cursor-chats/` stay; historical records stay; the unfixable remainder of SEC-T658-01 for Gemini CLI and Pi stays accepted (2026-10-15).

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Keep Cursor, fix it (Cursor CLI deny list, plan-123 original) | Superseded by the user's decision |
| Delete `cursor.json` only and leave trees and installer | Breaks Pi (V4), leaves 182 orphan files, an installer that still writes `.cursor/`, and gates that cannot see it (V2, V9) |
| Keep `format: "cursor"` as an alias for Pi | D2 C |
| Edit the Cursor rows out of the immutable artifacts | Violates immutability; changes tests instead (D6) |
| Edit the four golden cases to remove Cursor | Not needed (D5); would cost a grant and a baseline for a cosmetic change |
| Remove generator-owned files from adopter projects | D3 C: destructive in someone else's folder for a tool they may still use |

## Consequences

- **Positive**: one Cursor-related residual family ends (K-15 and K-16 Cursor parts, SEC-T658-01 Cursor part, SEC-T650-02 tail); one manifest, one emit branch, 182 generated files, about 20 test files and 54 mirror files fewer to maintain; `--update` stops sweeping a folder the harness never fully owned; the orphan guard closes a gap that existed for any future platform removal.
- **Negative**: a MAJOR release; Cursor users lose agents, commands, rules and skills updates and must clean up by hand; a documentation sweep of about 20 files; the immutable artifacts and ADR-002 keep Cursor rows that readers must interpret with this ADR.
- **Risks introduced**: D8 items 1-6. The largest is the frozen `.cursor/mcp.json` of v7.x installs.
- **Follow-ups**: release-manager writes the Breaking-changes entry, Migration Guide item and Known Issues from Appendix A; T671 closes the Cursor items; T663 and T666/T667 must not reintroduce Cursor; if the user later wants an opt-in cleanup command (`--remove-platform cursor`), it is a separate ADR (D3 C's design questions).

## Validation

1. After S1: `git ls-files | grep -i cursor` shows only allowed paths (D1); `git diff 6b0f8f2 -- tests/golden scripts/scorecard.py` is empty.
2. `.pi/mcp.json`, `implementation/.pi/mcp.json` and the other trees are byte-identical across commit 1 of S1.
3. The scenario test of D3 passes against a real v8.0.0 install and a synthetic one.
4. The orphan guard fails on a scratch copy that regains `implementation/.cursor/.generated-manifest.json`.
5. The full suite, scorecard (34 cases, counts as at v8.0.0: 28 pass, 6 `known_failing`, 0 regressions, or the T668 counts if it merged first) and the evaluator hash pass.
6. After S3: `--print-drift` prints `[]`.

## Not verified

- The tracked-file counts (182, 324, 54) are from the inventory; I re-read the files I cite but did not recount.
- I did not read `scripts/package.py`, `Makefile`, the `docs/wiki` pages, `README.md` or `implementation/PREREQUISITES.md` line by line; their Cursor lines are from the inventory. I read `install.sh` fully for the paths cited and about twelve test files for the cited ranges; I did not read `test_install_script.py`, `test_install_target_inside_repo.py` or `test_install_update_root.py` in full, so the D6 list must be completed with `git grep -il cursor tests/` after the edit.
- Whether `_manifest.schema.json` (untracked) enumerates MCP formats; whether any test compares a golden `expect.py` constant with the manifests; what the evaluator hash covers beyond the golden files (irrelevant while no golden file changes; `scorecard.py --check` and the hash check will confirm).
- Which release first wrote `.generated-manifest.json` and the provenance sidecar into adopter installs (detection fallback in D3).
- Cursor's documentation: the page `https://cursor.com/docs/context/rules`, fetched 2026-10-16, says Cursor supports `AGENTS.md` in the project root and subdirectories as an alternative to `.cursor/rules`; the page states no version and says nothing on `.claude/` or skills directories.
- Whether T665 to T667 will be breaking under the v8.0.0 counting rule (D4); the number of adopters with a Cursor install; the published GitLab wiki copy; external repositories; the effect on `scripts/package.py` users.
- No installer, generator or test was run. The migration commands in Appendix A are drafted from the code and the release document and are **not re-run**; S1's scenario test must run them before the release document ships.

## Appendix A. Draft user-facing migration text (for `docs/releases/v9.0.0.md`)

Written by the release-manager and technical-writer at release time; the numbering and version are placeholders.

**Install table.** Remove the `| Cursor | cursor |` row of the template. Under the table: "Cursor support was removed in v9.0.0; see Migration Guide item M-n."

**Breaking changes entry.** "**A-nn** Cursor is no longer a supported platform. `scripts/install.sh --platform cursor` exits 1 before writing anything; `--platform all` no longer installs `.cursor/`. The `cursor` platform manifest, the generated `.cursor/` tree (agents, commands and rules as `.mdc`, skills, `mcp.json`) and the `cursor` MCP format value are removed. Maintainers with a platform manifest that sets `mcp.format` to `cursor` must change it (Pi now uses `pi`)."

**Migration Guide item M-n. Cursor is no longer supported.**

- What changed: the items above. `--update` and `--projections-only` no longer touch `.cursor/` at all: files you added there are no longer deleted (before, they were). The installer prints a note while it finds a harness-generated `.cursor/` in your project.
- If you do not use Cursor with this harness, or want a clean tree: if you added nothing of your own to `.cursor/`, delete the folder (`rm -r .cursor`). If you did, delete the paths listed in `.cursor/.generated-manifest.json` under `files`, except `mcp.json`, then delete the manifest and any empty folders. For `.cursor/mcp.json`, remove the server entries the harness added (the names listed in `.cursor/mcp.json.provenance.json` under `generatorOwnedKeys`) and keep your own, or delete the file if it holds nothing of yours. Then delete the sidecar.
- If you keep the folder: it is frozen at the version that wrote it. Its MCP server versions are not bumped, its Playwright hardening is not updated, its agents and rules are not refreshed, and nothing prunes it. **If it came from v7.0.1 or older it can still start `npx -y @anthropic/mcp-filesystem`, a package that does not exist on npm under a scope the vendor does not control (M-9 of the v8.0.0 release notes; also the keys `e2b`, `redis`, `figma`, `notion` of v5.0.0 to v6.9.0 installs). Remove those entries now.** The generated file that the v8.0.0 instructions name (`implementation/.cursor/mcp.json`) does not exist in v9.0.0; use the `v8.0.0` tag of your clone for `--force-prune-keys`, or edit the file by hand.
- Cursor itself reads an `AGENTS.md` in the project root (Cursor documentation, checked 2026-10-16). The installer still writes `AGENTS.md` for every platform; its skill and rule paths name the platforms you install. The harness no longer provides Cursor-specific agents, commands, rules or skills.
- Automation: a script that runs `install.sh --platform cursor` now fails with exit 1 and a message. A script that runs `--platform all` and then reads `.cursor/` must be changed.
- Rollback: running the v8.x installer with `--update` recreates `.cursor/` and, as before, replaces it wholesale (your own files in it are deleted by that older installer; commit or back them up first).
- Pack authors: `supportedPlatforms` in `pack.json` no longer accepts `cursor` (the schema now lists the six supported platforms).

**Known Issues.** The residuals K-15 and K-16 are restated without Cursor. Add: "A Cursor install left in a project is frozen and is not pruned (item M-n)."
