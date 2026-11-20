# Artifact: tech-lead-release-v12-v1.md

> Immutable once produced; a revision is `tech-lead-release-v12-v2.md`.

## Metadata

- **Executor**: tech-lead, read-only review mode. No source or release file was changed; only this file was written. Worktree branch `agent/tech-lead/T876`.
- **Gate**: code review by area (T876, plan-182 § Task Decomposition item 9), the `validation-gates` Implementation gate for the release. I am also the planned independent check of T878's verdict (plan-182 item 11), so I edited no release file. **Date**: 2026-11-19.
- **Target**: `release/v12.0.0` at `90124fb6`; range `v11.0.0..90124fb6` (tag `v11.0.0` on `3118924a`; 240 files, +20100 / -1839; outside `docs/` and the platform mirrors, 42 files).
- **Based on**: `docs/tasks/task-T876.md`; `docs/plans/plan-182-next-release.md` (items 9 and 11, Addenda 1 to 3); `docs/artifacts/release-next-audit-v1.md` (T869: § 1 B-1 to B-18, § 2, § 3 MI-1 to MI-9, § 4 items 4, 15, 18; batch Q TD-T723-01, TL-T780-09); `docs/artifacts/mcp-pin-audit-next-v1.md` (T870); `docs/artifacts/security-confirmation-t871-sec-t660-t665-v1.md` (T871); `docs/artifacts/security-review-t881-ci-lock-v1.md` (T881); `docs/releases/v12.0.0.md` (T873) and `docs/releases/v11.0.0.md`; `docs/artifacts/tech-lead-release-v11-v1.md` (shape); `.claude/rules/coding-standards.md`; `git diff v11.0.0 HEAD`.
- **The user's words** (2026-11-19, verbatim): "release plan go", "Approve (Recommended)", "v12.0.0, MAJOR (Recommended)", "Yes, probe first (Recommended)", "Accept for v12.0.0 (Recommended)" and "Yes, push the probe tag (Recommended)".
- **Decision IDs referenced**: ADR-011, ADR-012, ADR-015, ADR-016.
- **Basis marker**: **(V)** read or run here. **(read)** read, not run. **(unverified)** neither.

## Verdict: CONDITIONAL_PASS

No blocker. Areas 1 to 3 and 5 pass. Area 4 passes on one condition: K-36 and K-32 were written before the probe tag T874 ran (T874 is `in_progress` in `docs/tasks/active-tasks.md:5`), and must report its result before T878 issues the verdict (TL-T876-01). The other findings are Minor or LOW: one function-size rule breach and two tracked items. No finding is a security finding above LOW.

## What was run

- `node implementation/scripts/sync.mjs --root implementation --check`: "OK - no drift across 314 files." **(V)**
- `python3 implementation/scripts/generate-registry.py --check`: "registry is up to date". **(V)**
- `python3 -m unittest` over `test_install_equal_size_copy`, `test_mcp_agent_denials`, `test_audit_mcp_pins_hardening`, `test_ca_chain_check`, `test_sync_wiki_redirects`, `test_context_retriever`, `test_memory_indexing_pipeline`, `test_pin_bump_checklist`, `test_ci_hash_pins` and `test_platform_projections`: 424 tests, OK (skipped=2) **(V)**.
- A function-size scan (Python `ast` for the four changed Python files; a brace scan for `sync.mjs`) of every function new or changed since `v11.0.0` **(V)**.
- Counts in `implementation/.opencode/agents/` (28 files): `bash: deny` in 13, `task: deny` in 26, a `task:` map in 2, with 14 `allow` entries each in `orchestrator.md` and `poc-orchestrator.md` **(V)**.
- No full suite, no golden suite, no install, no pipeline: QA runs them (T875). No job log was read.

## Area 1. Installer and generator: PASS

- **`install.sh` `rsync --checksum` (B-11)** **(V)**. `--checksum` is added to both rsync paths, `copy_tree_into` (`:938`) and `sync_tree_into` (`:988`), with the reasoning at `:907-918`. `merge_tree_preserve_existing` (`--ignore-existing`) and the `cp` fallbacks need no change, as the comment says. Covered by `tests/functional/test_install_equal_size_copy.py` (new, 97 lines). No other installer logic changed; the memory notice (`:1759-1760`) states B-12 correctly.
- **`build.py` `--project-id` check (B-12)** **(V)**. `remote_project_id_problem` (22 lines, 2 parameters) uses `context_retriever.derive_project_id`, the server's own normalisation, so the build and the server cannot disagree on the id. It refuses a mismatch and any id without a usable `origin`; it runs in `main` before both `--check-against` and the build. Its message names only the derived id and the path (truncated to 200 characters); a `RemoteResolutionError` text is already redacted at its source (T797). Covered by `test_memory_indexing_pipeline.py` (+173).
- **`context_retriever.py` (B-13)** **(V)**: `_GIT_TIMEOUT_S = 10` (`:103`) on the `git remote get-url` call (`:156`); `_redacted` on every remote shown in an error (`:133`, `:137`, `:140`); the `@`-in-slug refusal (`:142`). Changed functions are at most 23 lines. Covered by `test_context_retriever.py` (+145).
- **`sync.mjs` permission maps (B-1 to B-4, B-6)** **(V)**:
  - `permissionLines` keeps the T663 order (server-wildcard denies first, allows, per-agent denies last) and adds the pattern maps after every flat entry, so the last-rule-wins order holds. Pattern keys are written with `JSON.stringify`, which is valid YAML.
  - `builtinDenials` refuses a key that the same agent both grants and denies. `validateDenyUnlessGranted` returns the deny-only set, and `validatePermissionKeys` refuses any of them, `read` and `external_directory` as an allow key, so `bash`, `webfetch`, `websearch` and `task` can never be written as an allow.
  - `taskMap` and `assertTaskMap` fail closed: a holder without `agents:` gets `"*": deny` alone; built-in names (case-insensitive), wildcards, the agent's own name, duplicates and a first rule other than `"*": deny` are refused. An agent without `agent` gets a flat `task: deny` and no map, so the two forms never meet.
  - `pathDenials` and `validatePathDenyUnlessGranted` are deny-only by construction; `patternMaps` re-asserts it.
  - The `mcpAgentDenies` check and the schema enum (`array`, `permission`, `string`) move together; `opencode.json` carries `tools: "permission"` and the five new keys.
  - Every changed or new function is at most 50 lines. **One exceeds the parameter limit:** `taskMap(slug, data, sourceTools, cfg, agentNames)` has five (TL-T876-02).
  - Covered by `test_mcp_agent_denials.py` (+797), `test_platform_projections.py`, `test_mcp_server_denials.py` and `test_mcp_tool_name_mapping.py`; both drift gates pass.

**Findings in this area**: TL-T876-02.

## Area 2. Knowledge text and rulings: PASS

- **`implementation/PREREQUISITES.md`** **(V)**: `:4` and `:227` keep Node 22, 24 and 26 with their minimums, and `:227` names "v24 or v26 for the filesystem server"; the TL-T869-01 exception paragraph says the Node 22 behaviour is **unverified**; `:66` states the Opencode range (1.0.224 to the latest 1.x, tested on 1.19.2, 2.x not supported). The `true`/`false` to `allow`/`deny` wording follows the generator.
- **`AGENTS.md`** (root and `implementation/`) **(V)**: the GitLab-grants paragraph adds the Opencode `bash: deny` (T841) and `task: deny` (T843) sentences, consistent with the counts above (13 and 26 of 28, so only the two orchestrators can launch a subagent). The two files differ only in the lines that already differed at `v11.0.0` (skill and instruction pointers).
- **`docs/wiki/mcp-servers.md`** **(read)**: the T836 `permission:` map, T839 generic names, T841 built-in denies, T855 `task` and `read` maps, T861 `external_directory`, the default-directory-only limit (SEC-T856-03) and the supported range. Each is marked as documented and observed in resolved rule lists only, with refused calls not observed; that matches K-20.
- **`docs/wiki/mcp-pin-bump-checklist.md`** **(V)**: § 1 holds the 7-day rule and the two `--allow-young` exceptions (filesystem 2.4.0, Brave 2.1.5) with dates and reasons; § 2 runs `pip-audit` on every lock (T880); § 4 has no `--accept`; § 5 records the T866 run. `test_pin_bump_checklist.py` passes.
- No file under `implementation/knowledge/agents/`, `skills/`, `commands/` or `rules/` changed (diff stat) **(V)**, so no ruling text is in scope; ADR-011, ADR-015 and ADR-016 apply as written for v11.0.0.

**Findings in this area**: none.

## Area 3. CI and the release job: PASS

- **`.gitlab-ci.yml`** **(V)**. The diff has three hunks only: the header (the T859 re-read and `ci_images_reviewed_on: 2026-11-19`, `:20-25`), and the two CA jobs (`sha256sum -c SHA256SUMS` before use in both; the node job's conditional `--capath /etc/ssl/certs` run). No hunk touches `release-docs-gate` (`:267`), `main-develop-drift-gate` (`:294`) or `release` (`:317`).
  - **§ 6.2 item 15**: the only `allow_failure: true` lines are `:59` (`markdown-links`), `:225` (`main-develop-drift-check`) and `:265` (`wiki-sync`), none a tag job; the three tag jobs carry `tags: ["release-gate"]` (`:270`, `:297`, `:321`) and no `allow_failure`.
  - **§ 6.2 item 18**: the job list is the same as at `v11.0.0` (no new job), so no new job needs a `NOT_TAG_CONDITIONS` `if` (`tests/functional/test_ci_hash_pins.py:134`); `test_ci_hash_pins` passes.
  - The review date: the test passes at the reviewed date + 120 days (`test_ci_hash_pins.py:1390`), so 2027-03-19 is the last passing day and 2027-03-20 fails, as K-41 states.
- **`scripts/check-ca-chains.sh`** **(V)**. `EXPECTED_KEYS=14`, `EXPECTED_ROOTS=4`; `split_pems` reads the three certificate PEM forms and counts other `BEGIN` blocks; `spki_of` writes the key to a file before hashing, so an unreadable certificate gives no hash instead of the empty-input hash; `check_fixtures` counts keys, distinct keys, chains, extras and roots and requires every non-leaf fixture certificate to carry a listed key; `check_keys` fails on a non-certificate block and on a certificate whose key cannot be read. Every function is under 50 lines. Covered by `test_ca_chain_check.py` (+130). The python job has no `--capath` step; whether `python:3.12-alpine` ships hashed `/etc/ssl/certs` entries is **(unverified)** here (TL-T876-03).
- **`scripts/sync-wiki.py`** **(V)**. `_RefuseRedirects.redirect_request` returns `None`, so a 3xx surfaces as `HTTPError` and the page fails; all requests go through `OPENER`. `test_sync_wiki_redirects.py` passes (its 302 case prints the expected `[FAIL] page: HTTP 302`). `redirect_request` has five parameters besides `self`; that is the `urllib` override signature, not a design choice, so it is not a finding.
- **`audit-mcp-pins.py age`** **(V)**. Fail-closed: a non-zero `npm view`, a missing, non-string or unparseable time is an `AuditError` (exit 2); `--allow-young` needs `PACKAGE@VERSION:REASON` with a printable reason and must name a current npm pin; the age is in UTC calendar days (SEC-T867-02, known). New functions are 4 to 19 lines with at most 3 parameters. Covered by `test_audit_mcp_pins_hardening.py` (+110). `--min-age-days` accepts 0 (TL-T876-04).
- **CI lock (T880, T881)** **(V)**. `ci/requirements-ci.txt` changes only the header and `opentelemetry-api` 1.45.1 to 1.45.2 with two new hashes; `ci/requirements-release.txt` changes only a comment. That matches Addendum 3 and T881 (PASS; SEC-T881-01 fixed, SEC-T881-02 tracked LOW). The CVE and GHSA ids in X-11 and the lock header agree with T881.
- **The release scripts**: `verify-release-docs.py`, `publish-release.py`, `check-release-tag-tree.py` and `run-allowlisted.py` have no diff since `v11.0.0` **(V)**.

**Findings in this area**: TL-T876-03, TL-T876-04.

## Area 4. The release document, read against the sources: CONDITIONAL_PASS

**`install.sh` line references (TD-T723-01, § 6.2 item 4)** **(V)**. Every cited line holds at `90124fb6`: `:187` and `:1317` (Cursor, `docs/releases/v9.0.0.md`), `:1313` (M-9 of v8.0.0), `:192` and `:1339` (Pi), `:196` and `:1363` (Gemini CLI), `:907` (comment), `:938`, `:988`, `:1759`, `:1760`. `grep docs/releases scripts/install.sh` gives exactly these seven pointer lines and none to `v12.0.0.md`, so "No installer line points to this document" is true. TD-T723-01 is met for this release; it stays tracked because it recurs.

**Other citations** **(V)**: `implementation/PREREQUISITES.md:4`, `:66`, `:227`; `servers.yaml:143` (Brave 2.1.5, `--transport stdio`) and `:241` (filesystem 2.4.0); `.gitlab-ci.yml:25`; `_GIT_TIMEOUT_S` 10 s; the five manifest keys of M-8 in `implementation/platforms/opencode.json` and the schema enum.

**Against T869 § 1 and § 3 (TL-T780-09, by hand)** **(V)**. Every B item is carried: B-1 to B-5 as A-01 to A-05, B-6 as A-08, B-8 as A-07 and X-05, B-12 as A-06; B-7 X-04, B-9 X-09, B-10 X-10, B-11 X-06 and M-5, B-13 X-08 and M-7, B-14 F-02, B-15 F-03, B-16 M-9 and K-34, B-17 M-9 and K-36, B-18 M-10. The Breaking-changes count rule (B-1 to B-6, B-8, B-12; 8 entries) matches the eight entries listed. Every MI item is carried: MI-1 M-1, MI-2 M-2, MI-3 M-3, MI-4 M-8, MI-5 M-4, MI-6 M-5, MI-7 M-6, MI-8 M-7, MI-9 M-9. MI-5's rule holds: the document claims nowhere that `filesystem` 2.4.0 runs on Node 22 (A-07, M-4 and K-43 mark it **unverified**). Each M item names an action or says none is needed. The counts in A-02 and M-1 (13, 26, 14) match my re-count above, although A-02 says they were not re-counted (TL-T876-05).

**Claims checked**:
- "modified 36 files": 28 agents + 4 MCP configs + `AGENTS.md` + 3 files of `implementation/runtime/memory/` = 36, and exactly three files changed under `implementation/runtime/memory/` in the range **(V)**; the throwaway-target run itself is the release manager's observation **(unverified)** here.
- M-9: "`verify-release-docs.py` and `publish-release.py` have no change since v11.0.0" **(V)**.
- K-40: 2026-11-17 + 7 = 2026-11-24 and 2026-11-18 + 7 = 2026-11-25 **(V)**.
- K-41: 2027-03-19 is the last passing day of the image review **(V)**.
- K-16: the Conditions lines carry the verbatim answer "Accept for v12.0.0 (Recommended)", the T871 confirmation before the question, "Fix: none possible in the harness" and the outside closer, as ADR-016's conditions need (read against T871 and Addendum 2) **(read)**. SEC-T702-09 and TD-T697-07 are correctly not accepted.
- Nothing I traced claims what the audits mark unverified: the Node 22 behaviour, a refused live call or launch (K-20), the older-client behaviour (M-3), the runner log (K-36) and the `unit-tests` Node version (K-38) are each marked.

**Rollback Plan** **(V for the text, unverified for the run)**. It states what returns (SEC-T840-01, SEC-T702-09 with its lapsed acceptance, SEC-T756-07, the v11 memory files) and what does not (the deleted own agent file; the v11 installer's quick-check skip, with the v11.0.0 M-6 `touch` step as the remedy). The steps are correct against the installer: `--update` replaces the trees, client-owned files are spared. The maintainer paths (retag, hotfix) are stated as not rehearsed.

**The probe tag (K-36, K-32)**. Both say the probe `v12.0.0-gate.1` result and its deletion are **(unverified at writing)**. That is honest now, but T874 is still `in_progress`, and the document that ships must say what the probe showed and whether the gate ref is gone (TL-T876-01, the condition; the same pattern as TL-T819-01 for v11.0.0).

**Findings in this area**: TL-T876-01 (the condition), TL-T876-05.

## Area 5. The version: PASS

**MAJOR is still right** **(V)**. Nothing in `90124fb6` beyond T869's tree (`2fec9af8`) changes the analysis: outside `docs/`, `2fec9af8..90124fb6` changes only `ci/requirements-ci.txt`, `ci/requirements-release.txt` and `implementation/PREREQUISITES.md` (T880, reviewed in Areas 2 and 3) and `implementation/README.md` (T872's version markers). B-2 and B-3 remove a capability the generated Opencode agents had, B-5 drops older clients, B-6 makes a valid v11.0.0 fork manifest (`tools: "object"`) fail the schema, and B-12 refuses a `build.py` call that v11.0.0 accepted; each alone is a breaking change by the `release-workflow` flowchart. The version markers read v12.0.0 (`README.md:14`, `:233`; `implementation/README.md:4`, `:6`, `:61`). It agrees with the user's choice "v12.0.0, MAJOR (Recommended)".

**Findings in this area**: none.

## Findings

| ID | Severity | Location | Finding | Fix | Route |
|---|---|---|---|---|---|
| TL-T876-01 | Important | `docs/releases/v12.0.0.md` K-36, K-32 (Known Issues, Release pipeline) | Written before T874 ran; both say the probe result and the probe tag's deletion are unverified at writing. The shipped document must report what `v12.0.0-gate.1` showed (runner per tag job, which gates ran, that `release` does not run on a probe) and its limits, and K-32 must still require no `gate` ref before and after the tag push. | Update K-36 and K-32 from T874's record. | release-manager, before T878 issues the verdict; condition C-1. I confirm it in the independent check. |
| TL-T876-02 | Minor | `implementation/scripts/sync.mjs`, `taskMap(slug, data, sourceTools, cfg, agentNames)` | Five parameters; the coding standard allows four. `sourceTools` is `sourceToolList(data)`, which `taskMap` can derive itself. Not a behaviour defect. | Derive `sourceTools` inside, or pass one context object. | Track as LOW debt (register v26); devops-engineer at the next generator change. |
| TL-T876-03 | LOW | `.gitlab-ci.yml` `ca-chain-check-python`; `scripts/check-ca-chains.sh` | The node job runs `--capath /etc/ssl/certs` when hashed entries exist (SEC-T768-03); the python job has no such step. Whether `python:3.12-alpine` (with the `apk add` of openssl and git) has hashed entries that libcurl would read is **(unverified)**. | Confirm or add the same conditional step to the python job. | security-engineer T877 to confirm or dismiss; else register v26. |
| TL-T876-04 | LOW | `scripts/audit-mcp-pins.py` `age`, `non_negative_int`; `command_age` print | `--min-age-days 0` is accepted and turns the 7-day rule off with no recorded exception; only the checklist's fixed command guards it. The printed publication date is in the stamp's own offset, while the age uses the UTC date. | Set a floor of 7 (or require `--allow-young` below it); print the UTC date. | Track as LOW debt (register v26). |
| TL-T876-05 | Minor | `docs/releases/v12.0.0.md` A-02 | "register v20's counts, not re-counted for this document": this review re-counted them at `90124fb6` (13 `bash: deny`, 26 `task: deny`, 14 named allows per orchestrator). | Optionally cite this review instead of "not re-counted". Not a condition. | release-manager, optional with C-1. |

## Before the tag

1. C-1 (TL-T876-01) is applied by the release manager before T878's verdict; I confirm it as the independent checker.
2. T875 (QA) runs the suite, the golden suite, the installs and the CA jobs on the release commit; T877 (security) re-checks the release-level delta and TL-T876-03.
3. TL-T876-02 to -04 go to register v26 as tracked LOW, under the user's LOW policy. TL-T876-05 is optional wording.

## Gate Verdict: Implementation Review

**Gate:** implementation
**Executor:** tech-lead
**Date:** 2026-11-19
**Target:** v12.0.0 release (`release/v12.0.0` at `90124fb6`)

### Verdict: CONDITIONAL_PASS

Findings: TL-T876-01 to -05 (one Important, two Minor, two LOW; no blocker, and no security finding graded above LOW). Condition: C-1.

## VERDICT: CONDITIONAL_PASS

### Reviewed Artifacts

- Implementation: `release/v12.0.0` at `90124fb6`, range `v11.0.0..90124fb6`
- Against requirements: none applies; `docs/plans/plan-182-next-release.md`, `docs/artifacts/release-next-audit-v1.md`
- Against architecture: none applies; ADR-011, ADR-012, ADR-015, ADR-016

### Decision IDs Referenced

- ADR-011, ADR-012, ADR-015, ADR-016

### Conditions (for CONDITIONAL_PASS)

- [ ] **C-1** TL-T876-01: update K-36 and K-32 in `docs/releases/v12.0.0.md` with T874's probe result, its limits and the state of the probe tag. Owner release-manager; due before T878 issues the verdict and before my independent check (production track: before the next gate).

### Blocking Issues (for FAIL)

- None.

### Merge Authorization

- Merge permitted: Yes, with conditions tracked. This review merges nothing; the merges, the tag and the Release each keep the user's approval.
- Reviewed by: Tech Lead
- Review mode: read-only (no modifications made to source)

## Not checked (unverified)

- Any live client behaviour: Opencode refused calls and launches, older Opencode clients (K-20, M-3).
- Whether `server-filesystem@2.4.0` runs on Node 22 (K-43).
- The probe tag pipeline and any job log (T874; K-36, K-38).
- The release manager's throwaway-target install and rollback run.
- The runner settings and the user's hardening steps (B-17).
- The mirrors file by file (covered only by the drift gates).
- `tests/golden/`, which was not opened.

[VERDICT] gate=code-review status=CONDITIONAL_PASS target=release/v12.0.0@90124fb6 findings=TL-T876-01..05 conditions=C-1
