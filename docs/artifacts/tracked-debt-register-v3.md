# Artifact: tracked-debt-register-v3.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v2.md` (323 ids; v2 stays the record for every id that was `fixed` or `obsolete` there); `docs/plans/plan-123-post-release-follow-ups.md` (addenda of 2026-10-23, 2026-10-24 and 2026-10-31); `docs/tasks/completed-tasks.md` (rows T677, T679, T686 to T696); `docs/tasks/task-T689.md` (sections 6 and 7), `task-T693.md`, `task-T694.md`, `task-T695.md`, `task-T696.md`, `task-T697.md`; the review artifacts `security-review-t665-token-handling-v2.md`, `-t677-function-size-refactor-v1.md`, `-t686-release-job-token-v1.md`, `-t688-job-trace-removal-v1.md`, `-t689-token-placement-v1.md`, `-t690-copilot-security-servers-v1.md`, `-t693-release-self-review-v1.md`, `-t694-cwso-secret-source-v1.md`, `-t695-cwso-ci-secret-compose-v1.md` (CWSO repository), `-t696-cwso-deps-toolchain-v1.md` (CWSO repository); the rulings of T691 (`ruling-p112-p41-o1-release-self-review-v1.md`) and T692 (completed-task row; no separate artifact). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-010 (through the cited decisions), DEC-T664-3, DEC-T681-1; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact; the T697 brief and ledger row are the orchestrator's).
- **Task**: T697 (plan-123, addendum of 2026-10-31; the user's approval of 2026-10-31: "1 2 go, refresh yes"). **Date**: 2026-10-31. **Tree read**: branch `chore/T697-T699-debt-checkpoint-refresh` at `d2b77fd7` (develop `e779b9a6` plus the T697 to T699 briefs), worktree `agent/tech-lead/T697`. The CWSO repository was **not** read: every CWSO status below repeats the T695 and T696 reviews and the briefs.
- **Review mode**: read-only. v2 statuses were re-checked by grep and reading on `d2b77fd7` where the change is in this repository (file and line cited); where only a review artifact, a brief or a completed-task row supports a status, the row says so. Anything not traced is marked **(unverified)**.
- **Orchestrator-verified facts cited** (given to me in the T697 delegation, "orchestrator-verified 2026-10-31", not re-checked by me): T689 merged as MR !626 (develop `e779b9a6`) and closed SEC-T665-03 through the in-memory token-file default, not through the disk-encryption assumption; the CWSO JWT secret that was once committed was rotated on 2026-10-31, the committed copies are dead, and no tracked file in either repository holds the dead value; the T689 agent used about 250k tokens against a 150k budget (a process note, not a security id).
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret store in memory or on disk, the user's local `.claude/settings*.json` and `.vscode/mcp.json`. No credential or credential-like value and no internal network address is written here; the CWSO host is called "the CWSO server".
- **Policy applied** (the user, 2026-10-23, option label verbatim): "Track LOW items as debt, stop chasing (Recommended)". `MEDIUM` and higher are closed before merge or accepted by the user; `LOW` items stay here with an owner; no task is opened per review round.
- **Status vocabulary** (as in v2): `open` (needs a decision, an action or a task, or is above LOW), `tracked-LOW` (LOW debt with an owner), `fixed` (closing evidence given), `accepted` (a documented residual; the user's words are quoted where there is a user decision), `obsolete`.
- **Id prefixes**: `SEV-T690-*` is the prefix the T690 reviewer wrote (not `SEC-`); it is kept as written. `TD-T697-*` are ids minted by this register (section 3.10 and 3.11).

## 1. Summary

v3 holds **398 ids**: the 323 of v2 and **75 new**. After v3: **273 fixed**, **39 accepted**, 5 obsolete, **4 open**, **77 tracked-LOW**.

- **Open above LOW**: one, SEC-T662-01 (`SECURITY:MEDIUM`, unchanged since v2): the v9.0.0 release document must carry the Cursor migration item; it must be closed before the v9.0.0 tag (section 5 theme 7). No open item is `SECURITY:HIGH` or `SECURITY:CRITICAL`.
- **Accepted at MEDIUM by the user**: SEC-T657-01/SEC-T658-01 (remainder), SEC-T660-01, SEC-T665-01, SEC-T676-02 (**expires 2026-11-21**, action A-6) and TD-T697-07 (CWSO over plain HTTP on the LAN, decision "C" of 2026-10-31).
- **Every MEDIUM raised by the reviews since v2 is closed**: SEC-T686-01, SEC-T688-01, SEC-T693-01, SEC-T694-01, SEC-T694-02, SEC-T695-01; SEC-T665-03 (withdrawn by the user's "D-3 reject (disk encryption: no)" of 2026-10-24) is closed again by T689.
- **Nearest dates**: the Brave audit acceptance ends 2026-11-21 (A-6); SEC-T686-06 must be settled before the first real tag; the GitLab token and the CWSO bearer token were issued for 90 days on 2026-10-30/31 (A-13; exact expiry not read, (unverified)); the `paste` advisory acceptance in CWSO is due for review on 2027-01-31 (SEC-T696-06).

### 1.1 v2 ids by their v2 status and their status now

| v2 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 10 | 5 | 2 | 0 | 3 | 0 |
| tracked-LOW | 32 | 2 | 3 | 0 | 0 | 27 |
| accepted | 31 | 1 | 30 | 0 | 0 | 0 |
| fixed | 245 | 245 | 0 | 0 | 0 | 0 |
| obsolete | 5 | 0 | 0 | 5 | 0 | 0 |
| **all v2 ids** | **323** | **253** | **35** | **5** | **3** | **27** |

The 73 v2 ids that were open, tracked-LOW or accepted are each accounted for in section 2. Of the 245 v2 `fixed` ids, one is re-recorded because its closure was withdrawn and then re-made: SEC-T665-03 (section 2.4); its status is `fixed` in both versions, so the counts do not move. The other 244 `fixed` and the 5 `obsolete` ids are not repeated: v2 is their record.

### 1.2 New ids by source (status now)

| Source | Repository | new ids | fixed | accepted | open | tracked-LOW |
|---|---|---:|---:|---:|---:|---:|
| security-review-t665-token-handling-v2.md | emage.code | 0 | 0 | 0 | 0 | 0 |
| security-review-t677-function-size-refactor-v1.md | emage.code | 3 | 0 | 0 | 0 | 3 |
| security-review-t686-release-job-token-v1.md | emage.code | 8 | 4 | 1 | 0 | 3 |
| security-review-t688-job-trace-removal-v1.md | emage.code | 5 | 5 | 0 | 0 | 0 |
| security-review-t689-token-placement-v1.md | emage.code | 6 | 0 | 0 | 0 | 6 |
| security-review-t690-copilot-security-servers-v1.md | emage.code | 7 | 0 | 0 | 0 | 7 |
| security-review-t693-release-self-review-v1.md | emage.code | 9 | 1 | 0 | 0 | 8 |
| security-review-t694-cwso-secret-source-v1.md | emage.code | 12 | 3 | 0 | 0 | 9 |
| security-review-t695-cwso-ci-secret-compose-v1.md | **CWSO** | 10 | 4 | 0 | 0 | 6 |
| security-review-t696-cwso-deps-toolchain-v1.md | **CWSO** | 7 | 0 | 0 | 0 | 7 |
| T691 ruling, T692 ruling | emage.code | 0 | 0 | 0 | 0 | 0 |
| `task-T689.md` section 6 (live-check results), minted here | emage.code | 6 | 3 | 2 | 0 | 1 |
| this register (decision "C"; a reading of the T689 review) | both | 2 | 0 | 1 | 1 | 0 |
| **All new** | | **75** | **20** | **4** | **1** | **50** |

The T665 v2 artifact is a record, not a review: it adds no id; its content is in SEC-T665-03 (section 2.4). The T691 ruling adds no id (its residuals became SEC-T693-02 to -09 when T693 applied it); T692 had no Security Engineer review (completed-task row T692).

## 2. v2 ids re-checked

One row per v2 id that was `open`, `tracked-LOW` or `accepted`. "Evidence" gives a file and line read on `d2b77fd7`, a completed-task row, a review artifact or the user's recorded words; "not re-checked" means I relied on v2 and on the absence of any later task that touched the item.

### 2.1 v2 `open` (10 ids)

| Id | v2 | now | Evidence or reason |
|---|---|---|---|
| SEC-T660-02 | open | **fixed** | T688 (the user, 2026-10-23: "Drop the tool from qa-engineer (Recommended)"): `get_pipeline_job_output` removed from `qa-engineer`; T679 refreshed the root (SEC-T688-02 closed). Grep on `d2b77fd7`: no match for the tool name in `implementation/knowledge/agents/`, `.claude/agents/` or the other root projection folders. Residual (shell, `glab ci trace`, Gemini CLI) is documented, `security-review-t688-job-trace-removal-v1.md` § Residuals. |
| K-20 | open | open | Live behaviour still not observed for Copilot grants, Gemini denials and Pi list handling; T690 adds Copilot MCP narrowing and VS Code `cwd` resolution to the unobserved list (`security-review-t690-...` § Unverified). Owner: the user or an authorised live session (A-7). |
| TL-T649-01 | open | **fixed** | T677 (completed-task row T677): every function of the six named files at or under 50 lines, guard test `tests/functional/test_function_size.py` (exists on `d2b77fd7`); review PASS with three LOW (SEC-T677-01 to -03). The guard's blind spots are SEC-T677-01. |
| TD-T671-FN1 | open | **fixed** | T677: `render_installed_agents.py` `render` 91 to 20 lines (`security-review-t677-...` § Metadata). |
| P112-P41-O1 | open | **fixed** | Ruled by T691 (option A+, the user: "O1 have the Solution Architect rule on it.", 2026-10-24) and applied by T693 ("T693 go", 2026-10-31): `implementation/knowledge/agents/release-manager.md:46` (Release Gate Policy item 5, independent check of the self-authored release document) and `orchestrator.md:218` (Release-gate pointer). Residuals are SEC-T693-02 to -09 (section 3.6). |
| TD-T671-legacy | open | open | Not re-read in v1, v2 or v3 **(unverified)**; P14/P15 sit in protected goldens and need a grant. Owner: orchestrator (spot-check before the next plan). |
| TD-T671-ENVTOKEN | open | **fixed** | The CWSO bearer token was replaced on 2026-10-31 and the old token is rejected (plan-123 addendum of 2026-10-31; `task-T696.md` section 6: the pre-rotation token gets HTTP 401, checked by the orchestrator from the devcontainer). The user reported on 2026-10-24 that the token was pasted nowhere (addendum of 2026-10-24). The local `.env` itself was not inspected (by design). |
| K-2b | open | **accepted** | The user, 2026-10-24: "D-6 a" (leave the four `capability_gap` goldens `known_failing`). |
| SEC-T662-01 | open | open | `SECURITY:MEDIUM`. Now carried in `docs/tasks/task-T679.md:40` (section 3a), which closes decision D-9 of v2; `docs/releases/v9.0.0.md` does not exist yet (`docs/releases/` ends at `v8.0.0.md`). Must be closed before the v9.0.0 tag. Owner: release-manager + technical-writer. |
| TD-T687-01 | open | **accepted** | The user, 2026-10-24: "D2 b" (`GITLAB_DENIED_TOOLS_REGEX` stays a documented operator control, not shipped). Grep: no `GITLAB_DENIED_TOOLS_REGEX` in `implementation/knowledge/mcp/servers.yaml`. |

### 2.2 v2 `tracked-LOW` (32 ids)

| Id | v2 | now | Evidence or reason |
|---|---|---|---|
| SEC-014 | tracked-LOW | **accepted** | The user, 2026-10-24: "D-7 b" (no signed tags; `git tag -v` is not documented). Grep: no `git tag -v` in the live docs. |
| TD-T671-P5 | tracked-LOW | tracked-LOW | Grep: no `audience` in `scripts/install.sh` or `implementation/scripts/sync.mjs`. Owner: devops-engineer. |
| TD-T671-K5 | tracked-LOW | tracked-LOW | `implementation/knowledge/mcp/servers.yaml:198` still hard-codes the `em-age-emage.code` index directory. Owner: devops-engineer. |
| SEC-011 | tracked-LOW | tracked-LOW | `implementation/runtime/security/poc_scan.py:581,638,688,784-785,820` still use `.match`. Owner: backend-developer. |
| SEC-003 | tracked-LOW | **fixed** | T686: the release job uses `--token-env CI_JOB_TOKEN --token-header JOB-TOKEN` (`.gitlab-ci.yml:227`); `WIKI_TOKEN` is read only by `wiki-sync` (`.gitlab-ci.yml:178`, comment `:224-225`). Review PASS (`security-review-t686-...`). Not run in a real tag pipeline (A-5, (unverified)). |
| SEC-T658-02 | tracked-LOW | tracked-LOW | The Opencode refused call and the Gemini CLI check are still not run **(unverified)**. Owner: user or an authorised live session (A-7). |
| RO621-N-1 | tracked-LOW | **accepted** | The user, 2026-10-24: "D-5: Accept N-1. ..."; `implementation/knowledge/agents/technical-debt-narrator.md:46` still names `DEBT:` (accepted without change, completed-task row T692). |
| RO621-N-2 | tracked-LOW | **fixed** | T692: `implementation/knowledge/instructions/poc-guidelines.md:155` ("`TECHNICAL-DEBT.md` lives in the PoC root, next to `POC-DEBT-SCORECARD.md`"), anchored by `tests/functional/test_technical_debt_location.py`. The root copy `.claude/rules/poc-guidelines.md` still lacks the sentence: declared root drift, refreshed by T699. |
| RO621-N-3 | tracked-LOW | tracked-LOW | `implementation/knowledge/agents/scrum-master.md:32` still reads `priority::high/medium/low`. Owner: technical-writer. |
| TD-T671-FN2 | tracked-LOW | **accepted** | The user, 2026-10-24: "D-8 accept" (the repository-wide function-length debt of `runtime/**`; plan-123 addendum of 2026-10-24). |
| TD-T671-P16 | tracked-LOW | tracked-LOW | `implementation/knowledge/commands/batch.md:28` unchanged. Owner: technical-writer. |
| TD-T671-T538 | tracked-LOW | tracked-LOW | `implementation/knowledge/skills/dependency-graphing/SKILL.md:36-38` still blue/yellow. Owner: technical-writer. |
| TD-T671-T554 | tracked-LOW | tracked-LOW | `implementation/knowledge/commands/discover-skills.md:34` unchanged. Owner: technical-writer. |
| SEC-T663-02 | tracked-LOW | tracked-LOW | `implementation/.opencode/agents/qa-engineer.md` still has a `tools:` map and no `permission:` block (grep). Owner: devops-engineer. |
| SEC-T665-07 | tracked-LOW | tracked-LOW | Unchanged (DEC-T681-1). Live check 1 adds that the fine-grained token is not usable and that on gitlab.com Free a personal token cannot be limited by role (`task-T689.md` section 6.1). Owner: devops-engineer (if reopened). |
| SEC-T674-06 | tracked-LOW | tracked-LOW | Grep: no `submodule` in `implementation/runtime/security/git_executor.py`. Owner: devops-engineer. |
| SEC-T675-08 | tracked-LOW | tracked-LOW | Not re-checked; no later task names it (completed-task rows T686 to T696). Owner: devops-engineer. |
| SEC-T675-10 | tracked-LOW | tracked-LOW | Not re-checked; same. Owner: devops-engineer. |
| SEC-T676-14 | tracked-LOW | tracked-LOW | Not re-checked; no lock regeneration since. Owner: devops-engineer. |
| SEC-T678-03 | tracked-LOW | tracked-LOW | Carried in `task-T679.md` section 3a; closed when the v9.0.0 release document carries it. Owner: release-manager + technical-writer. |
| SEC-T684-01 | tracked-LOW | tracked-LOW | Not re-checked; T677 touched `install.sh` and `merge-task-docs.py` with no behaviour change (completed-task row T677), so the findings stand. Owner: devops-engineer. |
| SEC-T684-02 | tracked-LOW | tracked-LOW | Same as SEC-T684-01. |
| SEC-T684-03 | tracked-LOW | tracked-LOW | Same as SEC-T684-01. |
| SEC-T684-04 | tracked-LOW | tracked-LOW | Same as SEC-T684-01. |
| SEC-T684-05 | tracked-LOW | tracked-LOW | Same as SEC-T684-01. |
| SEC-T684-06 | tracked-LOW | tracked-LOW | Same as SEC-T684-01. |
| SEC-T685-01 | tracked-LOW | tracked-LOW | Not folded into T686 (the T686 review and row do not name it); not re-checked. Owner: devops-engineer. |
| SEC-T685-02 | tracked-LOW | tracked-LOW | Same as SEC-T685-01. |
| SEC-T685-03 | tracked-LOW | tracked-LOW | Same as SEC-T685-01; T686 added the CONTRIBUTING "Release token and permissions" section, whether it covers the -03 gaps is **(unverified)**. Owner: technical-writer. |
| TD-T687-02 | tracked-LOW | tracked-LOW | Not re-checked; no knowledge batch has run. Owner: solution-architect (ruling), technical-writer. |
| TD-T687-03 | tracked-LOW | tracked-LOW | Same as TD-T687-02. |
| TD-T687-04 | tracked-LOW | tracked-LOW | Same as TD-T687-02. |

### 2.3 v2 `accepted` (31 ids)

| Id | v2 | now | Evidence or reason |
|---|---|---|---|
| K-3 | accepted | **fixed** | T690 (the user, 2026-10-24: "D-4-b"): `implementation/.vscode/mcp.json` carries `security-audit` and `poc-security-audit` (grep); the K-3 sentence is gone from the live docs (`security-review-t690-...`, PASS). Residuals: SEV-T690-01 to -07. Root copy refreshed by T699 (declared drift). |
| SEC-T657-01 / SEC-T658-01 | accepted | accepted | Unchanged (the user, 2026-10-15/16; v2 section 6.1). |
| SEC-T660-01 | accepted | accepted | Unchanged; further mitigated by T689 (in-memory token-file default, at-rest warning in `scripts/check-gitlab-token.py`). Closure still only by an isolated user, container or VM. |
| SEC-T657-04 | accepted | accepted | Documented Opencode behaviour (v2). |
| K-15 | accepted | accepted | Unchanged (v2). |
| SEC-T660-05 | accepted | accepted | Reviewer-accepted (v2). |
| SEC-T650-03 | accepted | accepted | The user reported on 2026-10-24 that `WIKI_TOKEN` is Protected and Masked and that only the `v*` rule for Maintainers remains on protected tags; the orchestrator re-checked the tag protection through the read-only API (plan-123 addendum of 2026-10-24). The `WIKI_TOKEN` flags are the user's statement **(unverified by an agent)**. Since T686 the release job no longer reads `WIKI_TOKEN`. |
| T636-L6 | accepted | accepted | Unchanged (v2 section 6.2). |
| T636-L7 | accepted | accepted | Unchanged. |
| TD-T671-K7 | accepted | accepted | Unchanged. |
| R-1 | accepted | accepted | Unchanged; who accepted it is still **(unverified)**. |
| K-4 limits | accepted | accepted | Unchanged. |
| CR619-N5 | accepted | accepted | Unchanged. |
| K-10 | accepted | accepted | Unchanged. |
| GOLDEN_VERSION_LABEL | accepted | accepted | Unchanged. |
| T638-L-1 | accepted | accepted | Unchanged. |
| K-13 | accepted | accepted | Unchanged. |
| K-19 | accepted | accepted | Unchanged. |
| RO621-N-4 | accepted | accepted | Unchanged (the user, 2026-10-14). |
| RO621-N-5 | accepted | accepted | Unchanged. |
| RO621-O1b | accepted | accepted | Unchanged. |
| RO621-O5c | accepted | accepted | Unchanged. |
| TL-T649-09 | accepted | accepted | Unchanged. |
| SIGNOFF-CR649 | accepted | accepted | Unchanged; SEC-T693-07 records that the concentration can recur. |
| K-14 | accepted | accepted | Unchanged. |
| K-21 | accepted | accepted | Unchanged. |
| SEC-T662-05 | accepted | accepted | Reviewer-accepted (v2). |
| SEC-T667-03 | accepted | accepted | Reviewer-accepted (v2). |
| SEC-T667-06 | accepted | accepted | Reviewer-accepted (v2). |
| SEC-T665-01 | accepted | accepted | The user, 2026-10-16 (v2). The T689 review lists it as residual (1), unchanged. |
| SEC-T676-02 | accepted | accepted | The user, 2026-10-22: "Accept with conditions (Recommended)". **Expires** on the earlier of the first `@brave/brave-search-mcp-server` release above 2.1.4 and **2026-11-21** (A-6). If it lapses unrenewed, the two high findings are open again. |

### 2.4 One v2 `fixed` id re-recorded

| Id | v2 | now | Evidence |
|---|---|---|---|
| SEC-T665-03 | fixed (through the full-disk-encryption assumption) | **fixed** (by T689) | The user, 2026-10-24: "D-3 reject (disk encryption: no)". The v1 closure was withdrawn (`security-review-t665-token-handling-v2.md` § The user's decision): the finding was open from that decision until T689. T689 (MR !626, develop `e779b9a6`, orchestrator-verified 2026-10-31) makes the in-memory file the documented default (`implementation/PREREQUISITES.md:139`) and the checker warns on a persistent file system; `security-review-t689-token-placement-v1.md` § SEC-T665-03 disposition: "Closed by T689". Residuals of that section: (1) and (2) stay with the accepted SEC-T660-01/SEC-T665-01 (section 7.1); (3), environment mode, is the decision row TD-T697-08; (4) is SEC-T689-04; (5), `glab`'s own copy, is TD-T697-04 and action A-10. |

## 3. New ids

One row per id. Columns as in v2: "Status", "Owner" (the role that would do the work, or the user), "Home" (where the work lands under the LOW policy; "-" means closed). Statuses repeat the reviewer's disposition; a row that says "not re-read" was not checked by me.

### 3.1 security-review-t677-function-size-refactor-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T677-01 | LOW | `tests/functional/test_function_size.py` | The size guard misses some function shapes (Bash `function name {`, brace on the next line; JS arrows, methods, nested functions; a column-0 `}` in a heredoc; redefined Python names). | tracked-LOW | devops-engineer | next change to the guard; a real parser or more shapes |
| SEC-T677-02 | LOW | `verify-release-docs.py` `main`; `install.sh` swap helper | No test pins the `check_section_requirements` call or that `SWAP_*` are set before the first rename. | tracked-LOW | devops-engineer | next installer or release-tooling task |
| SEC-T677-03 | LOW | `install.sh` `usage` | Allowlisted as "no logic" but holds one command substitution. | tracked-LOW | devops-engineer | same |

### 3.2 security-review-t686-release-job-token-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T686-01 | MEDIUM | `scripts/publish-release.py` `child_environment()`; release job bootstrap | Child processes were filtered by name only; the job token also reaches them under other names. | fixed | devops-engineer | - (`684099e1`: allowlist plus value filter, mirrored in `.gitlab-ci.yml:222`, read) |
| SEC-T686-02 | LOW | `CONTRIBUTING.md` | Role, tag-protection and job-token-setting caveats. | fixed | devops-engineer | - |
| SEC-T686-03 | LOW | release job logs | Masking of `CI_JOB_TOKEN` in job logs unverified. | fixed | devops-engineer | - (marked (unverified), on the first-tag rehearsal checklist; the check itself is part of A-5) |
| SEC-T686-04 | LOW | tests | Loose test pins and a fake token of a real token's shape. | fixed | devops-engineer | - |
| SEC-T686-05 | LOW | `publish-release.py` argparse | A rejected header name is echoed (repr-escaped). | accepted | security-engineer | - (reviewer: "informational, no action") |
| SEC-T686-06 | LOW (availability, fail-closed) | release job, runner clone method | If the runner uses the credential helper, the value filter removes the token git needs and the two fetches fail before the API call. | tracked-LOW | devops-engineer | **before the first real tag** (A-5): read the runner's clone method; if needed exempt only the two fetches |
| SEC-T686-07 | LOW | child-process allowlist | `GIT_EXEC_PATH`, `GIT_ASKPASS`, `GIT_CONFIG_*` and proxy variables allowlisted without a stated reason. | tracked-LOW | devops-engineer | next release-tooling task |
| SEC-T686-08 | LOW (nit) | `LC_` pattern | Python and bootstrap differ on the `LC_` name pattern. | tracked-LOW | devops-engineer | same |

### 3.3 security-review-t688-job-trace-removal-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T688-01 | MEDIUM | `AGENTS.md`, wiki | "No agent reads raw job output" overclaimed. | fixed | devops-engineer | - (`40746e4c`; the sentence is in `AGENTS.md` § MCP Servers as read) |
| SEC-T688-02 | LOW | repo-root projections | Root copies still granted the tool. | fixed | orchestrator | - (T679; grep on `d2b77fd7` finds no match in the root folders) |
| SEC-T688-03 | LOW | `qa-engineer.md`, `PREREQUISITES.md` | `get_pipeline_test_report` can carry test output text. | fixed | devops-engineer | - (body bullet; residual documented; payload of the pinned server (unverified)) |
| SEC-T688-04 | LOW | `qa-engineer.md` | Self-contradictory body bullet; "Evidence: logs". | fixed | devops-engineer | - |
| SEC-T688-05 | LOW | `GITLAB_FORBIDDEN_NAME` test pattern | Did not match `trace`/`log`/artifact names. | fixed | devops-engineer | - |

### 3.4 security-review-t689-token-placement-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T689-01 | LOW | `implementation/PREREQUISITES.md:147` (review's line) | The creation snippet follows an existing symbolic link at the token path in a pre-existing directory. | tracked-LOW | devops-engineer | first of the T689 batch (reviewer: -01 and -03 first, users copy from these documents) |
| SEC-T689-02 | LOW | `docs/wiki/mcp-servers.md:67`; `security-review-t665-token-handling-v2.md:23` | "Disappears at logout or reboot" lacks the `RemoveIPC`/lingering qualifiers; hibernation images not named. | tracked-LOW | technical-writer | same batch; the T665 record is immutable, so the correction is a later version |
| SEC-T689-03 | LOW | `PREREQUISITES.md:213`; `AGENTS.md:116`, `implementation/AGENTS.md:116` | Migration step 2 omits the at-rest caveat; both AGENTS.md copies still say the setup instructions export the token. | tracked-LOW | devops-engineer + technical-writer | first of the T689 batch |
| SEC-T689-04 | LOW | `scripts/check-gitlab-token.py:233-235,486-490` | With no readable mount table the run ends "ok"; the skipped storage check shows only on an info line (macOS). | tracked-LOW | devops-engineer | next checker change |
| SEC-T689-05 | LOW (informational) | `scripts/check-gitlab-token.py:206-213,222` | Path resolution separate from the open descriptor; the checker's mount namespace can differ from the server's. | tracked-LOW | devops-engineer | same |
| SEC-T689-06 | LOW (informational) | `PREREQUISITES.md:129` | The Git-over-HTTP clause is attributed only to the user's report; it holds for personal tokens; group/project tokens unverified. | tracked-LOW | technical-writer | same batch |

### 3.5 security-review-t690-copilot-security-servers-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEV-T690-01 | LOW | `sync.mjs` `agentMcpDenials` | Selects servers by tags only and ignores `extraPlatforms` (not reachable today). | tracked-LOW | devops-engineer | next generator change |
| SEV-T690-02 | LOW (cross-platform) | security runtime launch | The scanner code lives in the workspace it scans; a hostile branch can substitute it. | tracked-LOW | devops-engineer + technical-writer | a SECURITY.md trust-boundary paragraph; longer term a pinned runtime package |
| SEV-T690-03 | LOW | wiki (VS Code) | Trust-dialog wording, `type` for stdio, `code .` recipe without (unverified) labels; multi-root not addressed. | tracked-LOW | technical-writer | next wiki batch |
| SEV-T690-04 | LOW (pre-existing, now reachable on Copilot) | `implementation/runtime/security/executor.py` | Full inherited environment for child tools; `root_is_too_broad` not applied to `allowed_root`; sensitive-name list misses several credential files. | tracked-LOW | devops-engineer | next change to the security runtime |
| SEV-T690-05 | LOW | T690 tests | Mutation M11 killed only by an input the regex refuses first; superset-only assertions. | tracked-LOW | devops-engineer | next generator change |
| SEV-T690-06 | LOW (informational) | Copilot agents | `context-retriever/retrieve` listed but the server is not generated for Copilot (fail-closed). | tracked-LOW | devops-engineer | a later generator task, or drop the tool from the Copilot render |
| SEV-T690-07 | LOW | `install.sh --update` | Adds the two code-launching servers to an adopter's `.vscode/mcp.json` silently; VS Code auto-start unverified. | tracked-LOW | devops-engineer; release-manager | a stderr note; **the v9.0.0 release notes** (decision D-13) |

### 3.6 security-review-t693-release-self-review-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T693-01 | MEDIUM (A08) | `release-manager.md:46` | The stale-check rule went stale by construction and named no re-run actor. | fixed | devops-engineer | - (re-check at `702f2171`, the user: "fix 01"; "never re-run it yourself" read at `release-manager.md:46`) |
| SEC-T693-02 | LOW | `release-manager.md:46,175`; `validation-gates/SKILL.md:114` | A missing or FAIL independent-check row has no stated effect on the verdict (partly addressed). | tracked-LOW | solution-architect (ruling), technical-writer | next knowledge batch |
| SEC-T693-03 | LOW | `orchestrator.md:218` vs `release-manager.md:46,175` | The checker is named differently; two control layers can merge into one. | tracked-LOW | same | same |
| SEC-T693-04 | LOW | `release-manager.md:163-175`; `prepare-release.md` | The verdict block records no commit; the published document carries no independent-check row (a command change needs the user's decision under ADR-007). | tracked-LOW | same; user for the command part | same |
| SEC-T693-05 | LOW | `release-manager.md:46` | "The document" has an unclear scope. | tracked-LOW | same | same |
| SEC-T693-06 | LOW (pre-existing) | `orchestrator.md:261-262` | Core Workflow Phase 5 puts deployment before the Release Gate. | tracked-LOW | same | same |
| SEC-T693-07 | LOW (residual accepted by ruling section 4 A+) | `release-manager.md:4,46`; `AGENTS.md:116` | The independent check is a role-text duty, not an enforced control. | tracked-LOW | - (reviewer: "Tracked debt; no edit") | none; the top-level session's verification and the user's tag approval stay the final controls |
| SEC-T693-08 | LOW (test coverage) | `tests/functional/test_release_self_review_text.py` | `release-manager.md:229` and `orchestrator.md:129` unpinned; projection list unconfirmed. | tracked-LOW | devops-engineer | same batch |
| SEC-T693-09 | LOW (A08) | `release-manager.md:46` with `docs/releases/_template.md:71-86` | The allowance names the whole `## RELEASE VERDICT` section, so Version and the feature lists may still change after the check. | tracked-LOW | solution-architect, technical-writer | same batch; list the fields |

### 3.7 security-review-t694-cwso-secret-source-v1.md (emage.code)

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T694-01 | MEDIUM (pre-existing) | `deploy/docker-compose-t226.yml` | `set -x`, secret on argv and a fixed fallback in the `sia-executor` entrypoint. | fixed | devops-engineer | - (`dd25a98c`, re-check PASS) |
| SEC-T694-02 | MEDIUM | `deploy/docker-compose-t226.yml` | The compose secret came from an absolute default file. | fixed | devops-engineer | - (`dd25a98c`: `environment: CWSO_JWT_SECRET`) |
| SEC-T694-03 | LOW | `implementation/runtime/cwso/mcp_client.py` | Silent fallback to a secret file. | fixed | devops-engineer | - (`mcp_client.py:75-76` reads the variables named `CWSO_JWT_SECRET` and an explicit `CWSO_JWT_SECRET_FILE`; no default path, as read) |
| SEC-T694-04 | LOW | `implementation/scripts/sia-executor.py` | `--jwt-secret` on argv; `allow_abbrev` echo. | tracked-LOW | devops-engineer | next CWSO-script task in emage.code |
| SEC-T694-05 | LOW | `cwso-deploy-helper.sh`, `mint-cwso-jwt.py` | Error messages can echo values or paths. | tracked-LOW | devops-engineer | same |
| SEC-T694-06 | LOW | `cwso-deploy-helper.sh` `export --secret-file` | Prints the secret to stdout by design. | tracked-LOW | devops-engineer | same |
| SEC-T694-07 | LOW | helper vs minter | Different secret-file parsing rules (fails closed). | tracked-LOW | devops-engineer | same |
| SEC-T694-08 | LOW (reworded at re-check) | `scripts/deploy/cwso-proxmox-setup.sh` | Raw value in the `.env` line compose reads; quoting; value at rest (mode 600) in the container. | tracked-LOW | devops-engineer | same |
| SEC-T694-09 | LOW (reduced) | `tests/functional/test_cwso_jwt_secret_source.py` | Test gaps (`--secret=VALUE`, unknown-argument echo, literal-text checks). | tracked-LOW | devops-engineer | same |
| SEC-T694-10 | LOW (incident) | agent session | The implementing agent printed the dead pre-rotation value once (hash-verified dead by the orchestrator, `task-T694.md` section 6). | tracked-LOW | - | recorded under SEC-T695-06 |
| SEC-T694-11 | LOW (pre-existing) | `cwso-proxmox-setup.sh`, `cwso-deploy-helper.sh` | Unpinned `get.docker.com` and `releases/latest` downloads without checksum; fixed `/tmp` paths. | tracked-LOW | devops-engineer | same |
| SEC-T694-12 | LOW (operational) | old `cwso-sia-executor` containers | A container from the old compose keeps xtrace output in its log. | tracked-LOW | user | A-11; on the CWSO server no such container exists (`task-T696.md` section 6, orchestrator check); other hosts (unverified) |

Count note: the re-check line says "LOW 11 in total over both rounds, 1 resolved, 10 open". By enumeration the LOW ids are SEC-T694-03 to -12 (ten), one resolved (-03), nine open (-04 to -12, -10 recorded under SEC-T695-06). This register counts by enumeration; the completed-task row T694 says "10 LOW tracked".

### 3.8 security-review-t695-cwso-ci-secret-compose-v1.md (repository **CWSO**)

| Id | Grade | Location (CWSO) | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T695-01 | MEDIUM | `docs/user/README.md`; `deploy/docker-compose.yml` | Cross-host access was documented over plain HTTP (bearer token in cleartext). | fixed | devops-engineer | - (`72b0d5a`: SSH tunnel or TLS proxy required; the user's own deployment is the accepted risk TD-T697-07) |
| SEC-T695-02 | LOW | README | The Origin list read as a network control. | fixed | devops-engineer | - |
| SEC-T695-03 | LOW | `orchestrator/internal/config/config.go`, `transport/http.go` | `CWSO_ALLOWED_ORIGINS` entries not validated (`null`, empty host). | tracked-LOW | devops-engineer | the next CWSO hardening batch (the reviewer's deadline; owner orchestrator for scheduling) |
| SEC-T695-04 | LOW | `deploy/docker-compose.ci.yml` | `restart: unless-stopped` also in CI. | fixed | devops-engineer | - |
| SEC-T695-05 | LOW (residual, wider at `519d2a2`) | `.gitlab-ci.yml` e2e jobs | Fixed project/container names; `down -v` on project `cwso` would remove a non-CI stack on the shared `dind` daemon. | tracked-LOW | devops-engineer | same batch |
| SEC-T695-06 | LOW (process) | agent sessions | Agents printed the dead value in tool output (T695; T694 via SEC-T694-10); local session transcripts may keep it. | tracked-LOW | orchestrator (process); user (A-15) | process rule: presence checks only (`git grep -l`, counts) |
| SEC-T695-07 | LOW (pre-existing) | `config.go:242-245` | Short HS256 secrets accepted. | tracked-LOW | devops-engineer | same batch |
| SEC-T695-08 | LOW | public docs | An internal network address was named. | fixed | devops-engineer | - (reserved example name; orchestrator check) |
| SEC-T695-09 | LOW (narrower at `519d2a2`) | `scripts/release-assets.sh:36` | Rust release builds use 1.86 against CI's 1.87 (Go part resolved). | tracked-LOW | devops-engineer | same batch (overlaps SEC-T696-01) |
| SEC-T695-10 | LOW (pre-existing) | `transport/http.go`; `docker-compose.yml` | Plain HTTP listener published on all interfaces by default. | tracked-LOW | devops-engineer | same batch; default bind `127.0.0.1` or native TLS |

### 3.9 security-review-t696-cwso-deps-toolchain-v1.md (repository **CWSO**)

| Id | Grade | Location (CWSO) | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| SEC-T696-01 | LOW | `scripts/release-assets.sh:36-37` | Rust 1.86 for release binaries, `cargo build` without `--locked`. | tracked-LOW | devops-engineer | next CWSO hardening batch (with SEC-T695-09) |
| SEC-T696-02 | LOW (pre-existing) | CI and Rust Dockerfiles | Rust pinned at 1.87, behind current stable. | tracked-LOW | devops-engineer | same |
| SEC-T696-03 | LOW (pre-existing) | runtime base images | Old `alpine:3.20` and `debian:bookworm-slim` bases; no OS-package scan. | tracked-LOW | devops-engineer | same |
| SEC-T696-04 | LOW (pre-existing) | CI and Dockerfiles | Base images pinned by tag, not digest. | tracked-LOW | devops-engineer | same |
| SEC-T696-05 | LOW (pre-existing) | `deploy/Dockerfile.orchestrator:8-9` | `go mod download \|\| true`; `go.sum*` glob. | tracked-LOW | devops-engineer | same |
| SEC-T696-06 | LOW | `services/.cargo/audit.toml:15-16` | The `paste` (RUSTSEC-2024-0436, unmaintained) acceptance review date **2027-01-31** is a comment only. | tracked-LOW | devops-engineer | **this row is the register entry the reviewer asked for**: review on or before 2027-01-31 |
| SEC-T696-07 | LOW (informational) | `services/cwso-sparse/Cargo.toml:38`; `agent.rs` | (a) explicit wasmtime feature list must be re-diffed on every bump; (b) no fuel or epoch interruption. | tracked-LOW | devops-engineer | (a) every wasmtime bump; (b) before untrusted modules are accepted |

### 3.10 `task-T689.md` section 6: live-check results (minted here, emage.code)

The brief's section 6 holds observations, not graded findings; each gets an id here so that its state is traceable. Line numbers are `implementation/PREREQUISITES.md` on `d2b77fd7`.

| Id | Grade | Observation (date) | Status | Evidence | Owner | Home |
|---|---|---|---|---|---|---|
| TD-T697-01 | info | Fine-grained personal access tokens are not usable for `qa-engineer` and `scrum-master` (no Create permission for Issue, Milestone, Issue link) (2026-10-24). | accepted | Platform limitation; the legacy `api` token stays the default (`PREREQUISITES.md:129`, `:221`). Bears on SEC-T665-07. | - | - |
| TD-T697-02 | info | `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` stops the `gitlab` MCP server from connecting; cause **(unverified)**; Bash-side parts not established. | accepted | Documented as not compatible (`PREREQUISITES.md:172`, `:222`). | - | - |
| TD-T697-03 | info | Token-file mode works with the variable unset; the empty-variable case and the reverse direction were not reported **(unverified)**. | tracked-LOW | `PREREQUISITES.md:223`; `security-review-t665-token-handling-v2.md` § Live-check results. | user | A-2 remainder |
| TD-T697-04 | info | `glab` reads `GITLAB_TOKEN` ahead of its config file; its own stored login is a second plaintext credential at rest. | fixed | Documented (`PREREQUISITES.md:187`); the user's devcontainer copy was emptied and the OAuth authorization revoked on 2026-10-30 (orchestrator note in the T689 review). Other installs: A-10. | user | A-10 |
| TD-T697-05 | info | The Claude Code sandbox left 0-byte placeholder dotfiles in the home directory, which broke login shells (2026-10-26); cause inferred **(unverified)**. | fixed | Warning documented (`PREREQUISITES.md:179`). | - | - |
| TD-T697-06 | info | The VS Code server reads its environment once at start; a changed token or file needs a server restart. | fixed | Documented (`PREREQUISITES.md:164`). | - | - |

### 3.11 This register

| Id | Grade | Location | Description | Status | Owner | Home |
|---|---|---|---|---|---|---|
| TD-T697-07 | MEDIUM (the grade of SEC-T695-01, which describes the same exposure; my mapping, not a Security Engineer's grading) | the user's deployment: the devcontainer to the CWSO server | CWSO is reached over plain HTTP on the LAN; the bearer token (90 days, role orchestrator) travels in cleartext (`task-T695.md` section 6). The repository now requires a tunnel or TLS (SEC-T695-01 fixed); the user's own deployment does not use either. The server keeps its local compose override for the Origin list. | accepted | user | decision "C" (2026-10-31; section 4); re-decide if the LAN changes or the token's role widens |
| TD-T697-08 | decision | `implementation/PREREQUISITES.md:139-160` (environment mode); `security-review-t689-token-placement-v1.md` § SEC-T665-03 disposition, residual (3) | Environment mode stays supported, and the documents now say that an exported token in a shell profile is a plaintext secret at rest. The T689 reviewer calls this, on an unencrypted disk, "the user's own accepted Constraint-6 exposure", but no recorded user decision accepts it (the T689 brief and the plan addenda do not; T665 v2 says only "Stays supported"). Immutable Security Constraint 6 admits no acceptance by its own text. The question is whether supporting (documenting) a mode that puts the user's own credential at rest is consistent with Constraint 6, or whether the documents should mark environment mode as acceptable only on an encrypted disk, as they already do for a persistent token file. | open | security-engineer (ruling), then user | decision D-11 |

## 4. The user's decisions since 2026-10-23

Words are quoted only where the plan addenda, the briefs or the completed-task rows record them verbatim; everything else is a description.

| Date | Decision (recorded words) | Effect in this register | Source |
|---|---|---|---|
| 2026-10-23 | Root refresh T679: "Yes, refresh the root now (Recommended)" | A-8 done; SEC-T688-02 closed | plan-123 addendum of 2026-10-23 (T688) |
| 2026-10-23 | D-1: "Drop the tool from qa-engineer (Recommended)" | SEC-T660-02 fixed (T688) | same |
| 2026-10-24 | "D2 b" | TD-T687-01 accepted | addendum of 2026-10-24 |
| 2026-10-24 | "D-3 reject (disk encryption: no)" | SEC-T665-03 withdrawn, then fixed by T689 | same; `security-review-t665-token-handling-v2.md` |
| 2026-10-24 | "D-4-b" | K-3 fixed (T690) | same |
| 2026-10-24 | "D-5: Accept N-1. Rule N-2 in one sentence (choose best location). O1 have the Solution Architect rule on it." | RO621-N-1 accepted; RO621-N-2 fixed (T692); P112-P41-O1 ruled (T691) and applied (T693) | same |
| 2026-10-24 | "D-6 a" | K-2b accepted | same |
| 2026-10-24 | "D-7 b" | SEC-014 accepted | same |
| 2026-10-24 | "D-8 accept" | TD-T671-FN2 accepted | same |
| 2026-10-24 | "D-10 yes" (confirms T667's merge exclusion for `devops-engineer` and `release-manager`) | v2 decision D-10 settled | same |
| 2026-10-31 | "T689 go" | T689 started and merged | completed-task row T689 |
| 2026-10-31 | "T693 go"; then "fix 01" for SEC-T693-01 | T693 applied; SEC-T693-01 fixed | completed-task row T693; `task-T693.md` section 6 |
| 2026-10-31 | "T694 go" | T694 and (per its brief's Based-on line) T695 | addendum of 2026-10-31; `task-T695.md` header |
| 2026-10-31 | "T696 go" | T696 | addendum of 2026-10-31 (T696) |
| 2026-10-31 | "C" (decision "C"): CWSO over plain HTTP on the LAN stays an accepted risk; the SSH tunnel (A) and the TLS proxy (B) were not chosen | TD-T697-07 accepted | `task-T695.md` section 6; addendum of 2026-10-31 (T696) |
| 2026-10-31 | "1 2 go, refresh yes" | T697 (this register), T698 (checkpoint 039), T699 (root refresh) | addendum of 2026-10-31 (T697 to T699) |

Also recorded on 2026-10-24 (the user's reports, described, not quoted): the results of actions A-1 to A-4 (section 6.1). On 2026-10-30/31 the user moved every devcontainer secret into a gpg-encrypted store with a copy in RAM, issued one new legacy GitLab token (scope `api`, 90 days), revoked the older GitLab tokens and the `glab` OAuth login, rotated the CWSO JWT secret and issued a new 90-day bearer token (addendum of 2026-10-31). D-9 of v2 was the orchestrator's and is done (`task-T679.md:40`).

## 5. Open items by theme

Rule applied: `MEDIUM` and higher must be closed or accepted by the user (the one open MEDIUM is theme 7); `LOW` items stay as debt with an owner; no task per round. "Home" names where the work would land if the user wants it done, never a new task. No task is in flight.

### 1. Installer, generator and merge scripts (tracked-LOW)

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| SEC-T684-01 to -06 | LOW | Six installer and `merge-task-docs.py` hardening items (v2 section 3.12). | devops-engineer | next task touching `install.sh`, `sync.mjs` or `merge-task-docs.py`; batch all six |
| SEC-T677-01 to -03 | LOW | Function-size guard blind spots, two missing pins, `usage` allowlist reason. | devops-engineer | same batch |
| SEV-T690-01, -05, -06, -07 | LOW | `extraPlatforms` vs denials, T690 test gaps, `context-retriever` on Copilot, silent addition of the two servers on `--update`. | devops-engineer | next generator change; -07 also the v9.0.0 notes |
| SEC-T663-02 | LOW | Opencode `tools:` map to `permission:`. | devops-engineer | next Opencode generator change |
| TD-T671-P5, TD-T671-K5 | LOW | `audience:` unimplemented; hard-coded index directory. | devops-engineer | as in v2 |

### 2. CI, release and supply chain (tracked-LOW; emage.code)

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| SEC-T686-06 | LOW (availability) | Clone method vs the value filter. **Settle before the first real tag.** | devops-engineer | v9.0.0 tag rehearsal (A-5) |
| SEC-T686-07, -08 | LOW | Allowlist reasons; `LC_` pattern. | devops-engineer | next release-tooling task |
| SEC-T685-01 to -03, SEC-T675-08, SEC-T675-10 | LOW | As in v2. | devops-engineer; technical-writer for SEC-T685-03 | next release-tooling task |
| SEC-T676-14 | INFO | Lock `--exclude-newer`. | devops-engineer | next lock regeneration |
| SEC-T674-06, SEC-011 | LOW | Scanner hardening; `fullmatch`. | devops-engineer; backend-developer | next PoC-scanner change |

### 3. Tool restriction, the GitLab token and the security runtime

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| TD-T697-08 | decision | Environment mode and Constraint 6. | security-engineer, user | decision D-11 |
| SEC-T689-01 to -06 | LOW | Snippet symlink, wiki qualifiers, migration caveat and AGENTS sentence, checker "not determined" result, namespace note, scope attribution. -01 and -03 first. | devops-engineer, technical-writer | one small token-docs batch |
| SEV-T690-02, -04 | LOW | Scanner trust boundary; environment and root checks in `executor.py`. | devops-engineer, technical-writer | next security-runtime change |
| SEC-T665-07 | LOW | One shared Developer-level token (DEC-T681-1). | devops-engineer (if reopened) | reopening conditions in `gitlab-per-role-token-design-v1.md` 5.3 |
| SEC-T658-02, K-20 | LOW / info | Live checks not run (Gemini CLI, Opencode refused call, Copilot, Pi). | user | A-7 |
| TD-T697-03 | info | Live check 3 remainder. | user | A-2 remainder |

### 4. Documentation, knowledge text and rulings (tracked-LOW)

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| SEC-T693-02 to -06, -08, -09 | LOW | Release-gate wording residuals of T693. | solution-architect (ruling), technical-writer | one small knowledge batch (the T691 ruling's preferred carrier) |
| SEC-T693-07 | LOW | Role-text duty, not enforcement (accepted by ruling A+, no edit). | - | none |
| RO621-N-3, TD-T671-P16, TD-T671-T538, TD-T671-T554, TD-T687-02 to -04 | LOW | As in v2. | technical-writer; solution-architect for TD-T687-* | same batch |

### 5. Function size

Closed: TL-T649-01 and TD-T671-FN1 are fixed (T677); TD-T671-FN2 is accepted ("D-8 accept"). Residuals are SEC-T677-01 to -03 (theme 1).

### 6. Golden suite and parked notes

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| TD-T671-legacy | LOW (unverified) | Older parked remarks never re-read. | orchestrator | spot-check before the next plan |

K-2b is accepted ("D-6 a").

### 7. v9.0.0 release items

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| SEC-T662-01 | SECURITY:MEDIUM | The v9.0.0 release document must carry the Cursor migration item and the gate must check the pointer target. Carried in `task-T679.md:40`. **Must be closed before the tag.** | release-manager + technical-writer | v9.0.0 release preparation |
| SEC-T678-03 | LOW | Leftover `.cursor/`. | release-manager + technical-writer | v9.0.0 release document (`task-T679.md` 3a) |
| SEC-T686-06 | LOW | See theme 2. | devops-engineer | before the first real tag |
| SEV-T690-07 | LOW | Release notes for the two new Copilot servers. | release-manager | v9.0.0 release document (D-13) |

### 8. CWSO repository (tracked-LOW)

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| SEC-T695-03, -05, -07, -09, -10 | LOW | Origin validation, shared-daemon names, short secrets, release Rust toolchain, plain-HTTP default bind. | devops-engineer (scheduling: orchestrator) | the next CWSO hardening batch (T695 reviewer's deadline) |
| SEC-T696-01 to -05, -07 | LOW | Release build toolchain and `--locked`, Rust version, old bases and no OS scan, tag pins, `go mod download \|\| true`, wasmtime feature list and interruption. | devops-engineer | same batch |
| SEC-T696-06 | LOW | `paste` acceptance review on or before **2027-01-31**. | devops-engineer | this register row |
| SEC-T695-06 (with SEC-T694-10) | LOW (process) | Agents printing secret matches. | orchestrator | process rule in briefs; A-15 |

### 9. CWSO scripts in emage.code (tracked-LOW)

| Id | Grade | What is open | Owner | Home |
|---|---|---|---|---|
| SEC-T694-04 to -09, -11 | LOW | argv secret flag, echoing errors, `export` prints the secret, parsing rules, raw `.env` value, test gaps, unpinned downloads. | devops-engineer | next CWSO-script task in emage.code |
| SEC-T694-12 | LOW | Old `cwso-sia-executor` containers on other hosts. | user | A-11 |

## 6. User actions and decisions with no task

### 6.1 User actions (agents cannot do them)

| # | Action | State now | Source |
|---|---|---|---|
| A-1 | Rotate the credential the T676 session exposed | **done** (user report, 2026-10-24: the Context7 key rotated and revoked; not verified by an agent) | addendum of 2026-10-24 |
| A-2 | Live checks of the T665 design | **mostly done**: checks 1 to 3 run 2026-10-24 to 2026-10-31 (`PREREQUISITES.md:221-223`); open: the empty-variable and reverse cases of check 3 (TD-T697-03) and the design's checks 4 and 5 (`PREREQUISITES.md:225`: protected-branch merge with a Developer token, VS Code/Cline unset-variable behaviour) **(unverified)** | `task-T689.md` section 6 |
| A-3 | Check or rotate the CWSO bearer token | **done** (rotated 2026-10-31; the old token gets HTTP 401, orchestrator check) | `task-T696.md` section 6 |
| A-4 | `WIKI_TOKEN` protected and masked; `v*` tags for Maintainers only | **done** (user report 2026-10-24; tag protection re-checked by the orchestrator through the read-only API; `WIKI_TOKEN` flags (unverified by an agent)) | addendum of 2026-10-24 |
| A-5 | Run and record the first real tag pipeline | **open**; adds SEC-T686-06 (clone method), SEC-T686-03 (job-token masking) and whether job tokens work in tag pipelines on protected tags (T686) | `security-review-t686-...` § Open and unverified |
| A-6 | Brave audit acceptance expiry | **open, due 2026-11-21** (or the first brave release above 2.1.4): `audit-mcp-pins.py audit --audit-level high` must pass without `--accept`, or the user renews in a new acceptance version | SEC-T676-02 |
| A-7 | Live checks of the Gemini CLI and Opencode denials (plus the T690 VS Code behaviour) | **open** | SEC-T658-02, K-20, `security-review-t690-...` § Unverified |
| A-8 | Approve the T679 root refresh | **done** ("Yes, refresh the root now (Recommended)", 2026-10-23; T679 merged) | completed-task row T679 |
| A-9 | v9.0.0 migration items (reference) | `task-T679.md` section 3a lists T672, T676, T680, SEC-T678-03 and SEC-T662-01; **not listed**: T688 (qa-engineer 20 to 19 GitLab tools), T689 (token-file default in memory), T690 (two code-launching servers added to `.vscode/mcp.json` on `--update`, SEV-T690-07), T693 (Release-gate input) (decision D-13) | grep of `task-T679.md` |
| A-10 | On every other install: empty `glab`'s own stored login and revoke its OAuth authorization if `GITLAB_TOKEN` is used | **open** (done on the user's devcontainer on 2026-10-30) | T689 review, recommendation; TD-T697-04 |
| A-11 | Remove or recreate any `cwso-sia-executor` container created from the old compose definition | **open** for other hosts; none exists on the CWSO server | SEC-T694-12; `task-T696.md` section 6 |
| A-12 | Optional: replace the CWSO server's local compose override with `CWSO_ALLOWED_ORIGINS` | **open, optional** (the T695 brief expected the replacement; the outcome says the override stays) | `task-T695.md` sections 1 and 6 |
| A-13 | Renew the GitLab token (legacy, scope `api`) and the CWSO bearer token before they expire | **open**; both issued for 90 days on 2026-10-30/31; exact expiry dates not read **(unverified)** | addendum of 2026-10-31 |
| A-14 | Recheck that the CWSO server runs the merged images after the next CWSO change | reference only; the user rebuilt at CWSO develop `5869cc5` on 2026-10-31 | `task-T696.md` section 6 |
| A-15 | Optional: purge local session transcripts that hold the dead (rotated, already public in history) CWSO secret | **open, optional**; retention unverified | SEC-T695-06, SEC-T694-10 |

### 6.2 Decisions

| # | Decision | Options | Recommendation (mine; the user decides) |
|---|---|---|---|
| D-1 to D-10 | v2 decisions | All settled: D-1 2026-10-23, D-2 to D-8 and D-10 2026-10-24 (section 4), D-9 by the orchestrator (`task-T679.md:40`). | - |
| D-11 | TD-T697-08: environment mode and Immutable Security Constraint 6 | (a) Mark environment mode in the documents as acceptable only on an encrypted disk, like a persistent token file. (b) A Security Engineer ruling that a user's own shell profile is outside Constraint 6 (then record it). (c) Remove environment mode (breaking). | (a): one sentence in `PREREQUISITES.md` and the wiki, with SEC-T689-03 in the same batch. |
| D-12 | When to run the LOW batches | The token-docs batch (SEC-T689-*), the knowledge batch (SEC-T693-*, RO621-N-3, TD-T687-*), the CWSO hardening batch (SEC-T695-*, SEC-T696-*). Under the LOW policy none is opened by default. | Fold SEC-T689-01/-03 and D-11 (a) into the v9.0.0 preparation, because users copy from those documents. |
| D-13 | Add T688, T689, T690 and T693 to the v9.0.0 migration list (`task-T679.md` 3a or the release-manager brief) | Orchestrator edit when the release is prepared. | Do it with SEC-T662-01; no new task. |

## 7. Accepted risks

### 7.1 Accepted by the user (words and dates)

| Item | Date | The user's words (verbatim as recorded) | What stays |
|---|---|---|---|
| SEC-T658-01 / SEC-T657-01 | 2026-10-15; 2026-10-16 | as in v2 section 6.1 | unchanged |
| SEC-T660-01 / SEC-T665-01 | 2026-10-15; 2026-10-16 | as in v2 | same-user read access to the token (file in memory or on disk); tmpfs swap unless swap is encrypted (T689 residuals 1 and 2) |
| SEC-T665-07 / DEC-T681-1 | 2026-10-22 | as in v2 | unchanged |
| SEC-T676-02 | 2026-10-22 | "Accept with conditions (Recommended)" | **expires 2026-11-21** (A-6) |
| SEC-T650-03 / SEC-003 grade | 2026-10-15; reported again 2026-10-24 | as in v2 | the release job no longer uses `WIKI_TOKEN` (T686); the flags are the user's statement |
| SIGNOFF-CR649; RO621 N-4, N-5, O1-b, O5-c | 2026-10-15; 2026-10-14 | as in v2 | unchanged |
| TD-T687-01 | 2026-10-24 | "D2 b" | `GITLAB_DENIED_TOOLS_REGEX` remains an operator control the user may set |
| SEC-014 | 2026-10-24 | "D-7 b" | release tags are not signed; `git tag -v` is not documented |
| RO621-N-1 | 2026-10-24 | "D-5: Accept N-1. ..." | `technical-debt-narrator.md:46` names `DEBT:` |
| K-2b | 2026-10-24 | "D-6 a" | four `capability_gap` goldens stay `known_failing` |
| TD-T671-FN2 | 2026-10-24 | "D-8 accept" | `implementation/runtime/**` functions over 50 lines |
| TD-T697-07 | 2026-10-31 | "C" | CWSO over plain HTTP on the LAN; the bearer token in cleartext there; tunnel (A) and TLS proxy (B) not chosen |

### 7.2 Accepted by a reviewer or documented as a residual (not a decision of the user)

As in v2 section 6.2 (T636-L6/L7, K-14, SEC-T660-05, SEC-T657-04, SEC-T667-03/-06, SEC-T662-05, R-1, K-4 limits, K-10, K-13, K-19, K-21, GOLDEN_VERSION_LABEL, TD-T671-K7, TL-T649-09, CR619-N5, T638-L-1, K-15), plus:

| Item | Basis |
|---|---|
| SEC-T686-05 | Reviewer: "informational, no action". |
| TD-T697-01, TD-T697-02 | Platform limitations observed in live checks and documented in `PREREQUISITES.md`. |
| SEC-T693-07 | Ruling section 4 A+ accepts the residual; tracked with no edit. |
| SEC-T665-03 residuals (4) and (5) | Skipped storage check without a mount table (SEC-T689-04); `glab`'s own copy (TD-T697-04, A-10). Residual (3), environment mode, is **not** accepted by any recorded decision (TD-T697-08). |

## 8. Method, limits and validation

1. Read v2 by section (sections 1, 2, 3 filtered to non-`fixed` rows, and 4 to 8), the plan-123 addenda of 2026-10-23 to 2026-10-31, `completed-tasks.md` rows T677, T679 and T686 to T696, the ten review artifacts listed under "Based on", the T691 ruling's headings and residuals, `task-T689.md` sections 1, 6 and 7, and the outcome sections of `task-T693.md` to `task-T696.md` (with section 1 of T694 and T695).
2. Re-checked on `d2b77fd7` by grep or read (file and line in the rows): `.gitlab-ci.yml:178,222-227`; `servers.yaml:198` and the absence of `GITLAB_DENIED_TOOLS_REGEX`; `poc_scan.py` `.match` lines; the absence of `audience` handling; the absence of `get_pipeline_job_output` in the knowledge agents and root projections; `technical-debt-narrator.md:46`; `poc-guidelines.md:155`; `scrum-master.md:32`; `batch.md:28`; `dependency-graphing/SKILL.md:36-38`; `discover-skills.md:34`; the Opencode `tools:` map; `git_executor.py`; `task-T679.md:40`; `implementation/.vscode/mcp.json`; `release-manager.md:46`; `orchestrator.md:218`; `mcp_client.py:75-76`; `PREREQUISITES.md:129-229` (selected lines); the existence of `test_function_size.py`, `test_release_self_review_text.py`, `test_technical_debt_location.py`, `test_cwso_jwt_secret_source.py`.
3. **Not traced or not verified**: the CWSO repository (every SEC-T695-* and SEC-T696-* status repeats the review); SEC-T675-08/-10, SEC-T676-14, SEC-T684-*, SEC-T685-*, TD-T687-02 to -04 (not re-checked; no later task names them); TD-T671-legacy; who accepted R-1; whether SEC-T685-03 is covered by the T686 CONTRIBUTING section; the `WIKI_TOKEN` flags; the expiry dates of the two 90-day tokens; everything that depends on a real tag pipeline (A-5); the reviewers' own unverified lists, which stand as written in their artifacts; the full test suite was not run for this artifact.
4. **Process note** (orchestrator-verified 2026-10-31; not a security id): the T689 implementing agent used about 250k tokens against a 150k budget. This register itself was produced within the T697 budget of about 100k (estimate).
5. Count note: the T694 re-check's "10 open" LOW and this register's 9 differ by enumeration (section 3.7).
6. This register changes no task row, brief, ledger, release document or source file. Dispositions for items the user has not decided are proposals.
7. Validation run by the producer (results in the task report): `python3 docs/tasks/validate-tasks.py`; `python3 -m unittest tests.functional.test_link_integrity`; `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Reviewed by: Tech Lead, read-only mode (no source modified; the only file written is this artifact).
- Artifact versions referenced: `tracked-debt-register-v2.md`, `plan-123-post-release-follow-ups.md`, the review artifacts and briefs named under "Based on", `ruling-p112-p41-o1-release-self-review-v1.md`, `gitlab-per-role-token-design-v1.md` (section 5.3, by reference). Decision IDs: ADR-010, DEC-T664-3, DEC-T681-1; ADR-007 by reference in SEC-T693-04; no ADR is amended.
- Next step: the orchestrator archives T697, carries A-6 (2026-11-21) and SEC-T686-06 into checkpoint 039 (T698), asks the user about D-11 to D-13, and keeps SEC-T662-01 on the v9.0.0 gate.
