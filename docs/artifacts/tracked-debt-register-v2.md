# Artifact: tracked-debt-register-v2.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v1.md` (204 ids); `docs/plans/plan-123-post-release-follow-ups.md` (all addenda, including those of 2026-10-16, 2026-10-22 and 2026-10-23); `docs/tasks/completed-tasks.md` (rows T661 to T685); `docs/tasks/task-T679.md` (section 3a), `task-T686.md`, `task-T677.md`; the review artifacts `security-review-t655-fetch-removal-v1.md`, `-t657-tool-name-mapping-v1.md`, `-t658-server-denials-v1.md`, `-t660-gitlab-grants-v1.md` (already consolidated in v1; no id added), `-t662-cursor-removal-v1.md`, `-t663-agent-denials-v1.md`, `-t665-token-handling-v1.md`, `-t666-t667-gitlab-sets-v1.md`, `-t672-installer-robustness-v1.md`, `-t674-doc-corrections-v1.md`, `-t675-ci-release-hardening-v1.md`, `-t676-supply-chain-v1.md`, `-t678-cursor-docs-v1.md`, `-t680-pi-placeholders-v1.md`, `-t682-installer-residuals-v1.md`, `-t684-installer-hardening-v1.md`, `-t685-supply-chain-residuals-v1.md`; `brave-audit-acceptance-v1.md`, `-v2.md`; `gitlab-token-handling-design-v1.md`; `gitlab-per-role-token-design-v1.md`. Requirements and architecture artifacts: none apply (a debt register); decision IDs referenced: ADR-010 (through the cited decisions), DEC-T664-1 to -6, DEC-T681-1 to -3.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact; the T687 brief and ledger row are the orchestrator's).
- **Task**: T687 (plan-123, addendum of 2026-10-23). **Date**: 2026-10-23. **Tree read**: develop `f9001692` (worktree `agent/tech-lead/T687`). T677 (function-size refactors) and T686 (release job on `CI_JOB_TOKEN`) are **in flight**; this register treats them as open.
- **Review mode**: read-only. The status of v1 items was re-checked by reading and grep on develop `f9001692` (file and line cited where it matters); where only a review artifact or a completed-task row supports a status, the row says so. Nothing was run, installed or tested for this artifact except the two validators named in section 7. Anything not traced is marked **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's local `.claude/settings*.json` and `.vscode/mcp.json`. No credential or credential-like value is written here.
- **Policy applied** (the user, 2026-10-23, AskUserQuestion, option label verbatim): "Track LOW items as debt, stop chasing (Recommended)". `MEDIUM` and higher are fixed before merge or accepted by the user; `LOW` items are recorded here with an owner and no new task is opened per review round. The older standing decision of 2026-10-09 ("5. C", fix every residual) is therefore applied to LOW findings through this register, not through a task per round (my reading; the plan addendum does not say it supersedes the older decision).
- **Status vocabulary**: `open` (needs a decision, an action or a task, or is above LOW), `tracked-LOW` (a LOW item that stays as debt with an owner), `fixed` (closing evidence given), `accepted` (a documented residual; a user decision is quoted where there is one), `obsolete`. v1 used the first one, `fixed`, `accepted` and `obsolete`; `tracked-LOW` is new and is a sub-class of v1's `open`.

## 1. Summary

v2 holds **323 ids**: the 204 ids of v1, re-walked, and **119 new ids** from the reviews of T662 to T685 and from this reading. After v2: **245 fixed**, 31 accepted, 5 obsolete, **10 open** (decision, action or above LOW), **32 tracked-LOW** (debt with an owner). No open item is `SECURITY:HIGH` or `SECURITY:CRITICAL`; open at `SECURITY:MEDIUM`: SEC-T662-01 (a release-time condition, section 4 theme 7); accepted at `SECURITY:MEDIUM`: SEC-T657-01/SEC-T658-01 (remainder), SEC-T660-01, SEC-T665-01 and SEC-T676-02, each with the user's words (section 6).

### 1.1 v1 ids by their v1 status and their status now

| v1 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 89 | 65 | 2 | 1 | 8 | 13 |
| fixed | 87 | 87 | 0 | 0 | 0 | 0 |
| accepted | 24 | 0 | 24 | 0 | 0 | 0 |
| obsolete | 4 | 0 | 0 | 4 | 0 | 0 |
| **all v1 ids** | **204** | **152** | **26** | **5** | **8** | **13** |

Of the 89 v1 ids that were open, 65 are fixed (T663 to T685, T668 to T670), 2 are accepted as documented behaviour or by the user, 1 is obsolete (the `github` server was removed), and 21 remain (8 open, 13 tracked-LOW). Rows that were `fixed`, `accepted` or `obsolete` in v1 are unchanged (115 ids); the counts above show no regression.

### 1.2 v1 ids by theme (status now)

| Theme (v1 section) | ids | fixed | accepted | obsolete | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| A. Installer, merge scripts and generator | 29 | 23 | 3 | 0 | 0 | 3 |
| B. PoC security scanner | 25 | 22 | 2 | 0 | 0 | 1 |
| C. Release job, CI and release tooling | 34 | 29 | 4 | 0 | 0 | 1 |
| D. MCP server packages and supply chain | 24 | 20 | 3 | 1 | 0 | 0 |
| E. Tool restriction, MCP grants and the GitLab surface | 28 | 19 | 6 | 0 | 2 | 1 |
| F. Documentation, references and counts | 28 | 21 | 4 | 0 | 0 | 3 |
| G. Function size against the 50-line standard | 3 | 0 | 0 | 0 | 2 | 1 |
| H. Knowledge-text notes parked in earlier plans | 20 | 14 | 0 | 1 | 2 | 3 |
| I. Process, governance and carried acceptances | 7 | 2 | 2 | 2 | 1 | 0 |
| J. Golden suite, evaluator and maturity | 3 | 2 | 0 | 0 | 1 | 0 |
| K. Other release-document known issues | 3 | 0 | 2 | 1 | 0 | 0 |

### 1.3 New ids by source (status now)

| Source | new ids | fixed | accepted | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|
| security-review-t662-cursor-removal-v1.md | 7 | 5 | 1 | 1 | 0 |
| security-review-t663-agent-denials-v1.md | 7 | 6 | 0 | 0 | 1 |
| security-review-t666-t667-gitlab-sets-v1.md | 7 | 5 | 2 | 0 | 0 |
| security-review-t665-token-handling-v1.md | 14 | 12 | 1 | 0 | 1 |
| security-review-t672-installer-robustness-v1.md | 20 | 20 | 0 | 0 | 0 |
| security-review-t674-doc-corrections-v1.md | 9 | 8 | 0 | 0 | 1 |
| security-review-t675-ci-release-hardening-v1.md | 10 | 8 | 0 | 0 | 2 |
| security-review-t676-supply-chain-v1.md | 14 | 12 | 1 | 0 | 1 |
| security-review-t678-cursor-docs-v1.md | 3 | 2 | 0 | 0 | 1 |
| security-review-t680-pi-placeholders-v1.md | 9 | 9 | 0 | 0 | 0 |
| security-review-t682-installer-residuals-v1.md | 6 | 6 | 0 | 0 | 0 |
| security-review-t684-installer-hardening-v1.md | 6 | 0 | 0 | 0 | 6 |
| security-review-t685-supply-chain-residuals-v1.md | 3 | 0 | 0 | 0 | 3 |
| this register (reading of the wiki page and of the T664 design) | 1 | 0 | 0 | 1 | 0 |
| `docs/wiki/severity-and-grade-scales.md` § Known gaps | 3 | 0 | 0 | 0 | 3 |
| **All new** | **119** | **93** | **5** | **2** | **19** |

Each new id has its own row in section 3. `SEC-T672-*` and `T672-N-*` are counted as the review wrote them; the `T665-LOW-1` to `-4` ids are the four items of the T665 delta re-review. INFO items without an id are listed in the last subsection of section 3.

## 2. Changes since v1

Every v1 row is accounted for below (152 rows, 204 ids). Rows whose status did not change and that need no remark are collected per theme under "Unchanged". The v1 text of a row that stays open is not repeated: look the id up in `tracked-debt-register-v1.md`; the reason it is still open is given here.

### 2.1 A. Installer, merge scripts and generator

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| SEC-004 | open | **fixed** | T672 (merge 84312bb0): swap-based tree replacement (build sibling, restore or discard, HUP/INT/QUIT/TERM traps, `mkdir --` atomic siblings): SEC-T672-02/-03 closed in `security-review-t672-installer-robustness-v1.md`; `SWAP_DONE` state by T682 (SEC-T682-02, `install.sh:1017-1024`). |
| SEC-005 | open | **fixed** | T672: `rsync -a --chmod=go-w` (`install.sh:927,977,1162`) and `chmod go-w` on the cp path (`:1121`); read on develop. Not named in the T672 review table (code comment only). |
| SEC-006 | open | **fixed** | T672: `mkstemp` + `fchmod` + `os.replace` in both merge scripts (SEC-T672-01 MEDIUM, -07 closed); ledger `.bak`; T684 (eb692776): `merge-task-docs.py` plan-then-write with atomic ledgers, backups and seeds (SEC-T682-06 closed in substance; six new LOW in `security-review-t684-installer-hardening-v1.md`). |
| SEC-007 | open | **fixed** | T672: stderr notes name a kept key inside a generator-owned `env`/`environment`/`headers` and a replaced `hooks` value (`merge-mcp-json.py:192-202,225-226,341-352`); T680 (01d023ed) adds the literal-credential WARNING (SEC-T680-01). Traced by code read: the T672 review names the notes only through SEC-T672-05 (help text lists exactly what is noted), SEC-007 appears in the code comment. The register's other option (accept keeping `env`) was not needed: the keep is documented and now noted. |
| SEC-008 | open | **fixed** | T672: (a) a plain install merges instead of overwriting, with the no-sidecar note (SEC-T672-06); (b) `--dry-run` creates nothing (T672 outcome in `completed-tasks.md`); (c) already fixed in v1. |
| SEC-009 | open | **fixed** | T672 + T682 + T684: hints go through `%q` / `shell_quote_ascii` (SEC-T682-03 closed by T684); `find` searches only `memory`, `security`, `handoff` (`install.sh:1623-1636`). Residual display point is SEC-T684-03. |
| SEC-010 | open | **fixed** | T672: no `eval`; `shopt -q` save and restore (`install.sh:709`, grep finds no `eval`). |
| SEC-T658-05 | open | **fixed** | T672: (a) plain install merges; (b) JSON validated before any write (`--validate-only`); (c) one-line stderr notes for replaced values; (d) `tests/functional/test_install_robustness.py:278` `test_projections_only_keeps_the_opencode_and_gemini_denials`. Review: SEC-T672-04/-05/-11 closed. |
| TL-T649-02 | open | **fixed** | T672: destination validated before the tree sync (same fix as SEC-T658-05(b)). |
| SEC-T658-07 | open | **fixed** | (a) wiki fixed in v1 (`44e3cb6`); (b) all manifests validated before the first write: T663 (SEC-T663-06, merge 17fe1792) and T672 (`assertUnderRoot`, overlap checks). |
| TL-T649-03 | open | **fixed** | T663 (SEC-T663-06) and T672: validation of all manifests before the first write. |
| TL-T649-04 | open | **fixed** | T672: `splitInlineArray` refuses YAML-divergent inline arrays (SEC-T672-09 closed; `completed-tasks.md` T672). |
| TL-T649-06 | open | **fixed** | T672: `$1 requires a value` messages (`install.sh:146-156`). The indentation half of the finding was unverified in v1 and is still not checked (unverified). |
| TL-T649-08 | open | **fixed** | T672: header-bounded ledger merge with `.bak` (`completed-tasks.md` T672); T684 plan-then-write. |
| QA-T648-02 | open | **fixed** | T672: the installer prints the Playwright browser step and the `.playwright-mcp/` advice (`install.sh:1573-1589`). |
| SEC-014 | open | **tracked-LOW** | Hash pinning delivered by T676 (b78b8e0a): `implementation/runtime/*/requirements-mcp-server.lock.txt` with `--require-hashes` documented (`PREREQUISITES.md:57`, checklist section 2). Open part: the `git tag -v` documentation needs a decision to sign release tags (`security-review-t674-doc-corrections-v1.md`, Open and unverified); grep finds no `git tag -v` in the live docs. Owner: user decision, then technical-writer. |
| SEC-015 | open | **fixed** | T675 (9a0d91db): `validate_api_target` URL parse, `--end-of-options`, `python3 -I` bootstrap, tag and subject guards; leading-dash `--target` refused by T672 (`install.sh:146-156`); commit subjects sanitised (T675/T676/T685, residual SEC-T685-02). |
| TD-T671-P8 | open | **fixed** | T672: `implementation/platforms/_manifest.schema.json` exists and is validated (SEC-T672-08/-10); the seven manifests' `$schema` now resolves. |
| TD-T671-P5 | open | **tracked-LOW** | No `audience` handling in `install.sh` or `sync.mjs` (grep, develop f9001692). No task; a feature, not robustness. Owner: devops-engineer (when a task touching the commands is opened). |
| TD-T671-K5 | open | **tracked-LOW** | `servers.yaml:188` still hard-codes `em-age-emage.code`. Owner: devops-engineer. |
| *Unchanged (9 ids)* | - | - | SEC-001 (fixed); T636-L1, T636-L2, T636-L3, T636-L4, T636-L5 (fixed); T636-L6 (accepted); T636-L7 (accepted); TD-T671-K7 (accepted) |

### 2.2 B. PoC security scanner

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| SEC-011 | open | **tracked-LOW** | `poc_scan.py` unchanged since T620: `.match` with `$` at lines 581, 638, 688, 784-785, 820 (grep). Owner: backend-developer (S: `fullmatch` + test). |
| SEC-013 | open | **fixed** | T674 (fdc689f8): the submodule limit is stated in `docs/wiki/mcp-servers.md:211` and `implementation/SECURITY.md:68`, labelled as read in code and not run; the launch-directory point was documented earlier. |
| *Unchanged (23 ids)* | - | - | SEC-012 (fixed); T611-1, T611-4, T611-5 (fixed); T611-2 (fixed); T611-3 (fixed); T612-SEC-1 (fixed); T612-SEC-2, T612-SEC-3, T612-SEC-4, T612-SEC-5 (fixed); T620-1, T620-2, T620-3, T620-4 (fixed); R-1 (accepted); K-4 limits (L-4, L-5, L-6, R-6) (accepted); T604-SEV-1, T604-SEV-2, T604-SEV-3, T604-SEV-4, T604-SEV-5, T604-SEV-6 (and three pins) (fixed) |

### 2.3 C. Release job, CI and release tooling

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| SEC-003 | open | **tracked-LOW** | Argv part fixed by T675 (`--token-env WIKI_TOKEN`, `.gitlab-ci.yml:225`). The reuse of the wiki token for the release job remains until T686 (CI_JOB_TOKEN; in flight). LOW grade still rests on D-4 (user statement, not verified). |
| SEC-T619-05 | open | **fixed** | T675 (acd26112): token read by environment (`--token-env`); the `--token` form warns (`security-review-t675-ci-release-hardening-v1.md`). |
| SEC-T635-01 | open | **fixed** | T675: `validate_api_target` as a URL parse with `--expected-host` pinned to `CI_SERVER_HOST`; empty host is an error (SEC-T675-05 closed). |
| SEC-T635-02 | open | **fixed** | T675: redirect-refusing opener on every request (301/302/303/307/308). |
| SEC-T635-03 | open | **fixed** | T675: `getcwd`/`chdir` now inside the `try` (`dry-run-publish-release.py:179-187`); the network guard replaces `OPENER` (SEC-T675-07 closed). |
| SEC-T635-04 | open | **fixed** | T675: the dry-run helper validates the tag (`dry-run-publish-release.py:136`); the review reports all 20 register ids in scope fixed or reduced to documented residuals. |
| SEC-T640-01 | open | **fixed** | T675: symlink guard in `load_release_brief` (`publish-release.py:260`). |
| SEC-T640-02 | open | **fixed** | T675: `UnicodeDecodeError` becomes `ReleasePublishError` (`publish-release.py:264`). |
| SEC-T640-03 | open | **fixed** | T675: tags filtered through `TAG_RE`, subjects stripped of control characters; T676/T685 extend the unsafe class (SEC-T676-05/-12, residual SEC-T685-02). |
| SEC-T640-04 | open | **fixed** | T675: host allowlist, redirect refusal, token not in argv. |
| SEC-T650-03 | accepted | accepted | The user statement D-4 is still unverified by any agent; see section 5, action A-4. |
| SEC-T650-04 | open | **fixed** | T675 (all 8 `image:` lines pinned by digest, `apk add` fuzzy-pinned) and T676 (re-resolved `python:3.12-alpine`/`node:24-alpine` digests, `ci_images_reviewed_on` guard, `tests/functional/test_ci_hash_pins.py:323`). |
| SEC-T650-05 | open | **fixed** | T675: secret-bearing paths denied by resolved path and rg globs (SEC-T675-01 closed), extra roots and worktree roots (`--allow-git-worktrees`, `root_is_too_broad`, SEC-T675-02 closed). The user-side token check stays as TD-T671-ENVTOKEN. |
| TL-T649-05 | open | **fixed** | T675: dry-run default tag read from the README marker (`dry-run-publish-release.py:260`). |
| TL-T649-07 | open | **fixed** | T675: read-time errors become `ReleasePublishError`. |
| TL-T649-12 | open | **fixed** | T675 (after the review follow-up): `verify-release-docs.py` rejects `pending`, `YYYY-MM-DD` and empty values (SEC-T675-06 closed). Stale docstring: SEC-T685-03. |
| TL-T649-13 | open | **fixed** | T675 prints the merge-before-tag NOTE; T685 (f9001692) adds `scripts/check-release-tag-tree.py` to the blocking `main-develop-drift-gate` (`.gitlab-ci.yml:211`). `GRACE_RELEASES = 1` is unchanged. Not run in a real tag pipeline (unverified). |
| TL-T649-14 | open | **fixed** | Same fix as SEC-T650-04. |
| QA-T648-03 | open | **fixed** | Same fix as TL-T649-13 (tree comparison, T685). |
| K-12 | open | **fixed** | T675: the changelog entry is placed below the intro (`publish-release.py:360-361`). The unexercised GitLab API half stays unverified until a real tag pipeline. |
| *Unchanged (14 ids)* | - | - | SEC-T619-01, SEC-T619-02, SEC-T619-03, SEC-T619-04 (fixed); CR619-S1, CR619-S2, CR619-S3 (fixed); CR619-N1, CR619-N2, CR619-N3, CR619-N4 (fixed); CR619-N5 (accepted); K-10 (accepted); GOLDEN_VERSION_LABEL (accepted) |

### 2.4 D. MCP server packages and supply chain

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| T638-L-2 | open | **fixed** | T676 (b78b8e0a): hash-locked Python sets and CI locks; `scripts/audit-mcp-pins.py` audits the npm transitives (it found the brave/SDK pair, SEC-T676-02). npm transitives still float by design (K-13); each bump re-audits. |
| T638-L-3 | open | **obsolete** | The `github` MCP server was removed by T676 on the user's decision of 2026-10-22 ("Remove GitHub MCP server"); the container hardening question no longer applies. SEC-T676-07 closed by removal. |
| T638-L-4 | open | **fixed** | T674: `docs/wiki/mcp-servers.md:184`, `implementation/PREREQUISITES.md:83`; the `--project-ref` flag is labelled unverified against the pinned `@supabase/mcp-server-supabase@0.13.0`. |
| T638-L-8 | open | **fixed** | T676: checklist section 1 item 2 (provenance preference, extra review for single-maintainer packages) and the provenance run of 2026-10-22 (6 of 8 pins have attestations; brave and toolradar do not). |
| SEC-T646-03 | open | **fixed** | T676: provenance preference rule in `docs/wiki/mcp-pin-bump-checklist.md` section 1 item 2. |
| SEC-T646-04 | open | **fixed** | T676: `httpx2>=2.12.0` (`requirements-mcp-server.txt:30`) and hash-locked `*.lock.txt`; `pip-audit` run recorded in checklist section 5. |
| SEC-T646-05 | open | **fixed** | T676: `scripts/audit-mcp-pins.py` (throwaway `package.json` from the pins, `--ignore-scripts`, fail-closed; SEC-T676-03/-04 closed). Brave findings accepted: SEC-T676-02. |
| SEC-T646-06 | open | **fixed** | T676: manual advisory read, checklist section 1 item 4; run recorded 2026-10-22. |
| SEC-T655-06 | open | **fixed** | T676: browser security-version check, checklist section 1 item 6(b). |
| SEC-T655-07 | open | **fixed** | T676: 13 blocked-origins entries added (39 total) with a ported matcher test (SEC-T676-06 closed; Teredo and trailing-dot forms documented as residual). |
| K-17 | open | **fixed** | T676: the audit path works (`audit-mcp-pins.py audit`, run 2026-10-22, checklist section 5). |
| *Unchanged (13 ids)* | - | - | SEC-002 (fixed); T638-M-1 (fixed); T638-M-2, T638-M-3 (fixed); T638-L-1 (accepted); T638-L-5, T638-L-6, T638-L-7 (fixed); SEC-T646-01 (fixed); SEC-T646-02 (fixed); SEC-T650-01 (fixed); K-13 (accepted); K-19 (accepted) |

### 2.5 E. Tool restriction, MCP grants and the GitLab surface

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| SEC-T657-01 / SEC-T658-01 | accepted | accepted | Still accepted for the remainder. Opencode per-agent denies delivered by T663 (17fe1792); the Cursor part is gone (T662, ADR-010); the Gemini CLI, Pi (agents without `mcp__` entries) and Opencode built-in agents remain, the latter by the user's decision of 2026-10-16 ("No, document the gap only (Recommended)"). |
| SEC-T660-01 | accepted | accepted | Still accepted. T665 (1d9dd68d) mitigates (token file, `GITLAB_PERMISSION_MODE=modify`, check script); residual carried as SEC-T665-01, re-accepted by the user on 2026-10-16 ("Adopt D and re-accept the residual (Recommended)"). Mitigated, not closed. |
| SEC-T657-04 | open | **accepted** | T663: the override is the documented Opencode behaviour; the sentence with the `gitlab_merge_merge_request` example is in both `AGENTS.md` and pinned by a test (SEC-T663-03 closed); no supported way keeps a prompt (only `OPENCODE_CONFIG_CONTENT`). Accepted as documented behaviour (reviewer, not a user decision). |
| SEC-T657-07 | open | **fixed** | T673 (1c9aa063): new `tests/functional/test_mcp_grant_pins.py` pins memory, sequential-thinking, security-audit, poc-security-audit, context-retriever and the exact set of agents with a write MCP tool. |
| SEC-T658-02 | open | **tracked-LOW** | T676 wrote the check list (`mcp-pin-bump-checklist.md` section 6). Opencode partly observed 2026-10-22 (opencode 1.18.31: resolved rules); the refused call and the whole Gemini CLI check are not run (unverified). Owner: user or an authorised live session (section 5). |
| SEC-T658-03 | open | **fixed** | T674: wiki "Corrections to the cited artifacts" row for `mcp-server-denials-v1.md` §2.2/§6.3 (Gemini ranks the project file above the user file); the immutable artifact is untouched. SEC-T674-02 and -03 closed. |
| SEC-T658-04 | open | **fixed** | T674: "another configuration source" is in `AGENTS.md` and `PREREQUISITES.md:33`; the wiki says the same in other words (`docs/wiki/mcp-servers.md:126,143`). |
| SEC-T658-06 | open | **fixed** | T673: documentation assertions anchored to the paragraph or row they protect, vacuous ones removed with the reason per assertion (`completed-tasks.md` T673). |
| SEC-T660-02 | open | open | No task. `qa-engineer.md:4` still grants `get_pipeline_job_output`. Decision for the user (section 5, decision D-1): drop the tool and add a body line, or accept. |
| SEC-T660-03 | open | **fixed** | T674: operator controls table in `docs/wiki/mcp-servers.md:68,158` and `PREREQUISITES.md` "Server-side limits"; the README-on-main points are labelled unverified (SEC-T674-02). |
| SEC-T660-04 | open | **fixed** | T666 and T667 (5dfd12fa): no agent holds the whole `gitlab` server; seven named holders (24/20/16/8/11/17/6). Closed for the tool surface, not as a credential boundary (SEC-T660-01). |
| SEC-T660-06 | open | **fixed** | T673: forbidden-name classes widened, the 275-name snapshot classified by verb, Gemini agents carry no `tools:` line, documented counts equal the lists. |
| SEC-T660-07 | open | **fixed** | T674: the Pi sentence and the default `core` toolset sentence are in `AGENTS.md` and the wiki (read on develop). |
| K-3 | accepted | accepted | Still a platform-scope limitation; the user has not decided whether Copilot carries the extended servers (section 5, decision D-4). |
| K-15 | open | **accepted** | Split into accepted/fixed ids: Opencode part fixed (T663), Cursor part gone (T662), Gemini CLI/Pi/built-ins remainder accepted (SEC-T657-01/SEC-T658-01); live behaviour stays K-20. |
| K-16 | open | **fixed** | Closed by its split ids: SEC-T660-01 (accepted, mitigated by T665), -03 and -07 (T674), -04 (T666/T667). Existing installs and the root keep the old grants until the next update or the T679 root refresh. |
| K-20 | open | open | Still not observed in a live run for Copilot grants, Gemini denials and Pi list handling; Opencode partly observed 2026-10-22 (checklist section 6). Needs the user or an authorised live session. |
| *Unchanged (11 ids)* | - | - | SEC-T657-02 (fixed); SEC-T657-03 (fixed); SEC-T657-05, SEC-T657-06, SEC-T657-08 (fixed); SEC-T657-09 (fixed); SEC-T660-05 (accepted); SEC-T650-02 (fixed); SEC-T655-01, SEC-T655-02, SEC-T655-03 (fixed) |

### 2.6 F. Documentation, references and counts

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| TL-T649-10 | open | **fixed** | T674: `release-workflow/SKILL.md:134` reads `# Release v<VERSION>`; projections regenerated. |
| SC634-1 (severity-scales page) | open | **fixed** | T674: `docs/wiki/severity-and-grade-scales.md` exists (SEC-T674-01 closed). |
| SC634-2, SC634-3, SC634-4, SC634-5 | open | **fixed** | T674: recorded under "Known gaps" items 1-4 of the page, as the register proposed. The page records them, it does not rule on them; the rulings stay with the owners of the defining documents. Found while writing it: three new rows (TD-T687-02 to -04). |
| STALE-COUNTS | fixed | fixed | Fixed in v1 (T644); T674 refreshed counts again; T678 (403a7dfb) updated platform counts after the Cursor removal. |
| TD-T671-ART | open | **fixed** | T674: three corrections are a wiki section "Corrections to the cited artifacts" (`docs/wiki/mcp-servers.md:160-166`); the immutable artifacts are untouched (SEC-T674-09 handled by merge order). |
| RO621-N-1 | open | **tracked-LOW** | `technical-debt-narrator.md:44` still names `DEBT:` (grep). Owner: solution-architect (ruling), then technical-writer. |
| RO621-N-2 | open | **tracked-LOW** | No document states where `TECHNICAL-DEBT.md` lives (unchanged). Owner: solution-architect (ruling on instruction text). |
| RO621-N-3 | open | **tracked-LOW** | `scrum-master.md:32` still reads `priority::high/medium/low` (grep). Owner: technical-writer (one word + projections). |
| *Unchanged (17 ids)* | - | - | TL-T649-16, TL-T649-17 (fixed); TL-T649-15, TL-T649-18, TL-T649-19, TL-T649-20 (fixed); QA-T648-01, QA-T648-04 (fixed); SEC-T655-09 (fixed); SEC-T655-04, SEC-T655-05, SEC-T655-08, SEC-T655-10 (fixed); RO621-N-4 (accepted); RO621-N-5 (accepted); RO621-O1b, RO621-O5c (accepted) |

### 2.7 G. Function size against the 50-line standard

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| TL-T649-01 | open | open | T677 is in flight (row `pending` in `active-tasks.md`; its dependencies T672, T665 and T675 are done). Lengths were not re-measured after the T665/T672/T676/T680/T684 edits to the same files (unverified); T677 re-measures. |
| TD-T671-FN1 | open | open | Not named in the T677 brief (unchanged). Owner: devops-engineer; extend T677 or accept (orchestrator decision). `render_installed_agents.py` was also edited by T662 (unverified length). |
| TD-T671-FN2 | open | **tracked-LOW** | Proposed accept as pre-existing; unchanged. Owner: tech-lead (re-scan at the next register). |

### 2.8 H. Knowledge-text notes parked in earlier plans

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| P112-P41-O3 | open | **fixed** | T668 (f41b8dca / bc412c88): `prepare-release-real-verdict-missing` now `expected_pass` with a byte-identical copy of the published `docs/releases/v8.0.0.md`; scorecard 34/30/0. |
| P112-P41-O1 | open | open | Never ruled; both delegations still in `orchestrator.md:217,259` (grep). Needs a ruling or the user's acceptance (section 5, decision D-5). |
| TD-T671-P16 | open | **tracked-LOW** | `batch.md:28` unchanged. Owner: technical-writer (with T538, T554 as one small knowledge batch). |
| TD-T671-T538 | open | **tracked-LOW** | `dependency-graphing/SKILL.md:36-38` still blue/yellow (grep). Owner: technical-writer. |
| TD-T671-T554 | open | **tracked-LOW** | `discover-skills.md:34` unchanged. Owner: technical-writer (or accept). |
| TD-T671-legacy | open | open | Not re-read in v1 and not re-read now (unverified). P14/P15 sit in protected goldens and need a grant. Owner: orchestrator (spot-check before the next plan). |
| *Unchanged (14 ids)* | - | - | P112-P32-O1, P112-P32-O2, P112-P32-O5 (fixed); P112-P32-O6 (fixed); P112-P41-O2 (fixed); P112-P41-O4, P112-P33-O1, -O2, -O5, -O6, O-8 (fixed); P112-P33-O4 (obsolete); TD-T671-P13 (fixed); LNA-newfeature-brief (fixed) |

### 2.9 I. Process, governance and carried acceptances

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| TD-T671-ENVTOKEN | open | open | User action; not inspectable by agents (section 5, action A-3). T675 closed the tool-side `.env*` exposure (SEC-T675-01). |
| *Unchanged (6 ids)* | - | - | TL-T649-09 (accepted); TL-T649-11 (fixed); SIGNOFF-CR649 (accepted); CP38-ancestry (fixed); CK625-O1, CK625-O2 (obsolete) |

### 2.10 J. Golden suite, evaluator and maturity

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| K-1 | open | **fixed** | T670 (f41b8dca): `orchestrator` promoted to `stable`; `check-maturity.py` 80 components, 0 failing, independently re-run by the top-level session (`completed-tasks.md` T670). |
| K-2a | open | **fixed** | T668 + T669 (baseline v22, `docs/artifacts/evaluator-hash-known-good-v22.json`): both cases `expected_pass`; scorecard 34/28/0 to 34/30/0. |
| K-2b | open | open | Unchanged: after T668 the scorecard shows 4 `known_failing`, all `capability_gap` (`completed-tasks.md` T668). No task; needs a grant (G-3) and a later baseline; the user decides (section 5, decision D-6). Held-out case not opened. |

### 2.11 K. Other release-document known issues

| v1 id(s) | v1 | now | Closing evidence or reason |
|---|---|---|---|
| *Unchanged (3 ids)* | - | - | K-8 (obsolete); K-14 (accepted); K-21 (accepted) |

### 2.12 v1 statements that are no longer true

- v1 section 2.3 listed SEC-007 as needing a decision of the Tech Lead and Security Engineer: it was handled by T672 (notes) and T680 (credential WARNING); no decision is left. Verified in the code (`merge-mcp-json.py:192-202`); the T672 review table does not name SEC-007, so the trace is by the code comment and the module docstring.
- v1 section 2.3 and section 5 said K-18 lists SEC-T657-09 and SEC-T658-03/-04, SEC-T660-07 as open: the release document is immutable and still says so; the closed state is in section 2.5 above.
- v1 listed five items under "User actions or decisions with no task" (SEC-T650-03/D-4, TD-T671-ENVTOKEN, K-3, SEC-T660-02, SEC-007). SEC-007 no longer needs a decision; the other four do (section 5).
- v1 section 2.2 counted `new task needed` for 12 ids and proposed to extend T672 to T677 for 32 ids. Under the LOW policy of 2026-10-23 no such task or extension is opened; the ids are in section 4 with an owner.
- v1 proposed T663 for SEC-T657-04; T663 documented the override instead of removing it (the behaviour cannot be removed), so SEC-T657-04 is `accepted`, not `fixed`.

## 3. New ids

One row per id. "Status" is `fixed` (the closing task or commit is in the note), `accepted` (the user's words or the reviewer's acceptance are in the note), `open`, or `tracked-LOW`. "Owner" is the role that would do the work, or the user. "Home" is where the work lands under the LOW policy; "-" means closed.

### 3.1 security-review-t662-cursor-removal-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T662-01 | SECURITY:MEDIUM | `install.sh` Cursor notice; `docs/releases/v9.0.0.md` (not yet written) | A frozen Cursor install is never pruned again; the stderr notice was made self-sufficient (8191c3c9), but the v9.0.0 release document must carry the Cursor migration item (M-9 steps, the v5.0.0-v6.9.0 keys, `--force-prune-keys` only from the v8.0.0 tag, the Known Issue) and the release gate must check that the pointer target exists | open | open until the v9.0.0 release document exists; not listed in `task-T679.md` section 3a (gap, section 5 of this register) | release-manager + technical-writer | v9.0.0 release document |
| SEC-T662-02 | SECURITY:MEDIUM | `tests/functional/test_install_cursor_removal.py`; `.gitlab-ci.yml` `unit-tests` | The real-v8.0.0 upgrade test skipped silently when the tag was missing | fixed | T662 (8e73c6e3), 8191c3c9: fails under `CI`, the job fetches the tag; the shallow tag fetch on a runner is unverified until the first pipeline | devops-engineer | - |
| SEC-T662-03 | LOW | `install.sh:20` | Supported-platform list written in four places | fixed | T672: one `SUPPORTED_PLATFORMS` array (`install.sh:20`, used at `:51,:184`), pinned by `tests/functional/test_install_robustness.py` (SEC-T662-03 in its docstring, lines 9, 99, 130, 141) | devops-engineer | - |
| SEC-T662-04 | LOW | `install.sh` removal message | Echoed platform value sanitised with a locale-dependent class | fixed | 8191c3c9 (`LC_ALL=C`, three-locale test) | devops-engineer | - |
| SEC-T662-05 | LOW | Cursor notice detection | Known false negatives (installs older than the manifest or sidecar; a plain install prints no notice) | accepted | accepted by the reviewer; documented in the test docstring | security-engineer | - |
| SEC-T662-06 | LOW | absence test | By-name test checked the filesystem, not tracked files | fixed | 8191c3c9 (`git ls-files`; fails under CI) | devops-engineer | - |
| SEC-T662-07 | LOW | `install.sh` `mkdir -p "$TARGET"` | `--dry-run` created the target | fixed | T672 (`--dry-run` creates nothing) | devops-engineer | - |

### 3.2 security-review-t663-agent-denials-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T663-01 | SECURITY:MEDIUM | Opencode agent files; `servers.yaml` `denyUnlessGranted` | Only `gitlab` carried the per-agent deny; other servers stayed callable by non-holders | fixed | 793cd60 and 6c271ed (T663, merge 17fe1792); user decisions 2026-10-16: "Exempt the read/search servers (Recommended)" and "No, document the gap only (Recommended)" for built-in agents | devops-engineer | - |
| SEC-T663-02 | LOW | `implementation/.opencode/agents/*.md` (`tools:` map) | The mechanism rests on the legacy `tools:` map, which Opencode documents as deprecated; migrate to a `permission:` block; add a release-checklist item and a refused-call check | tracked-LOW | checklist section 6 has the `opencode agent list` step (T676); the refused call is unverified; migration not started | devops-engineer | next task that touches the Opencode generator |
| SEC-T663-03 | LOW | `AGENTS.md`, wiki, `PREREQUISITES.md` | SEC-T657-04 override not documented or pinned | fixed | 793cd60 (sentence + test) | technical-writer | - |
| SEC-T663-04 | LOW | user-facing docs | `gitlab_*` over-match, saved approvals, built-in agents omitted | fixed | 793cd60 | technical-writer | - |
| SEC-T663-05 | LOW | `tests/functional` denial tests (anchoring) | Weak documentation assertions; model defaults | fixed | 793cd60 | qa-engineer | - |
| SEC-T663-06 | LOW | `sync.mjs` | Misspelled flag key ignored; manifests validated in the write loop | fixed | 793cd60 (closes SEC-T658-07(b)) | devops-engineer | - |
| SEC-T663-07 | LOW | `docs/artifacts/mcp-agent-denials-evidence-v1.md` | Resolver evidence was prose | fixed | 793cd60, 6c271ed (six raw files with sha256) | devops-engineer | - |

### 3.3 security-review-t666-t667-gitlab-sets-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T667-01 | SECURITY:MEDIUM | `release-manager.md`, `release-workflow` skill | Role text told the release manager to merge, tag and publish while the docs and the tool list say it does not | fixed | fff383b8 (T667, merge 5dfd12fa); whether the user confirmed the plan's open question on the merge exclusion is not recorded (unverified) | devops-engineer | - |
| SEC-T666-01 | LOW | `orchestrator.md` | Body instructed `glab release create` and release tagging | fixed | fff383b8 | devops-engineer | - |
| SEC-T667-02 | LOW | docs "Used by" rows, wiki, `mcp-agent-denials-v1.md` | Stale "whole server" statements | fixed | fff383b8; addendum `mcp-agent-denials-v1-addendum-t667.md` | technical-writer | - |
| SEC-T667-03 | LOW | `create_merge_request` grant | Can target any project, branch and reviewer the token reaches and start MR pipelines | accepted | accepted residual by the reviewer; one sentence added to the docs | security-engineer | - |
| SEC-T667-04 | LOW | tests | Docs and counts not pinned; tool names not checked against the registry | fixed | fff383b8 (snapshot `tests/_baselines/gitlab-mcp-tool-names.json`) | qa-engineer | - |
| SEC-T667-05 | LOW | docs | Over-claim; PAT scope guidance inconsistent | fixed | wording in fff383b8; scope reconciliation by T665 | devops-engineer | - |
| SEC-T667-06 | LOW | CI lint tools; `get_merge_request(include_summaries)` | `dry_run` lint resolves `include:` server-side; summaries returned | accepted | accepted residual by the reviewer; one sentence added | security-engineer | - |

### 3.4 security-review-t665-token-handling-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T665-01 | SECURITY:MEDIUM | six of seven GitLab roles hold `execute` | Residual of SEC-T660-01 after option D: a shell reads the token file or calls the API | accepted | user, 2026-10-16: "Adopt D and re-accept the residual (Recommended)"; closure only by an isolated user, container or VM | user | - |
| SEC-T665-02 | SECURITY:MEDIUM | `scripts/check-gitlab-token.py` | Checker printed `result: ok` though the role was not verified | fixed | T665 (1d9dd68d); closed by the delta review | devops-engineer | - |
| SEC-T665-03 | SECURITY:MEDIUM | `PREREQUISITES.md` token file | Plaintext token file at rest (Immutable Constraint 6 judgement) | fixed | docs state the full-disk-encryption assumption and placements; the orchestrator's position that Constraint 6 is not breached was "for the user to confirm"; no confirmation found (unverified, section 5, decision D-3) | user (confirm) | - |
| SEC-T665-04 | LOW | `check-gitlab-token.py` | Token-file read: symlink, TOCTOU, owner | fixed | `O_NOFOLLOW`, `fstat` owner check; closed | devops-engineer | - |
| SEC-T665-05 | LOW | `check-gitlab-token.py` | Exit-code collision, one-character leak, argument echo | fixed | closed | devops-engineer | - |
| SEC-T665-06 | LOW | file-creation snippet | `umask` left set; old mode kept | fixed | closed | technical-writer | - |
| SEC-T665-07 | LOW | `PREREQUISITES.md` scope table | One shared token needs Developer for three roles; the table may understate Developer's reach | tracked-LOW | user, 2026-10-22: "A: status quo + exposure sentence (Recommended)" and "Yes, document it (Recommended)" (Reporter profile); T674 wrote it, T683 pins it; stays open as LOW (`gitlab-per-role-token-design-v1.md`) | devops-engineer (if reopened) | reopening conditions in the design section 5.3 |
| SEC-T665-08 | LOW | `sync.mjs` `validateSpec` | `secret` advisory, `wrap` unrestricted | fixed | closed | devops-engineer | - |
| SEC-T665-09 | LOW | Pi documentation / generator | Pi diagnosis unverified; optional variables unsupported | fixed | wording fixed by T665; generator by T680 (01d023ed) | devops-engineer | - |
| SEC-T665-10 | LOW | tests | Test weaknesses and gaps | fixed | closed | qa-engineer | - |
| T665-LOW-1 | LOW | `check-gitlab-token.py`/docs | `Reporter.clean` stripped only C0 controls | fixed | fixed in 8fcfb72c with tests and mutation proofs (not re-read by the reviewer) | devops-engineer | - |
| T665-LOW-2 | LOW | `check-gitlab-token.py`/docs | output section outside the `try` (exit 1) | fixed | fixed in 8fcfb72c with tests and mutation proofs (not re-read by the reviewer) | devops-engineer | - |
| T665-LOW-3 | LOW | `check-gitlab-token.py`/docs | "nothing is written to disk" overstated for tmpfs | fixed | fixed in 8fcfb72c with tests and mutation proofs (not re-read by the reviewer) | devops-engineer | - |
| T665-LOW-4 | LOW | `check-gitlab-token.py`/docs | scope guidance contradicted the checker (`read_user`) | fixed | fixed in 8fcfb72c with tests and mutation proofs (not re-read by the reviewer) | devops-engineer | - |

### 3.5 security-review-t672-installer-robustness-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T672-01 | SECURITY:MEDIUM | `merge-mcp-json.py`, `merge-task-docs.py` temp file | Replacement temp file held merged config at 0666 minus umask with a predictable name | fixed | `mkstemp` + `fchmod`; closed by the delta review (84312bb0) | devops-engineer | - |
| SEC-T672-02 | LOW | `install.sh`, merge scripts, `sync.mjs` | `swap_cleanup` left the old tree after an interrupt; HUP/QUIT not trapped | fixed | closed by the delta review | devops-engineer | - |
| SEC-T672-03 | LOW | `install.sh`, merge scripts, `sync.mjs` | predictable swap sibling names, check-then-create window | fixed | closed by the delta review | devops-engineer | - |
| SEC-T672-04 | LOW | `install.sh`, merge scripts, `sync.mjs` | fail-closed claim held for one of three platform maps | fixed | closed by the delta review | devops-engineer | - |
| SEC-T672-05 | LOW | `install.sh`, merge scripts, `sync.mjs` | help text overclaimed the replaced-value notes | fixed | closed by the delta review; matched to its fix by theme only (reviewer's own caveat) | devops-engineer | - |
| SEC-T672-06 | LOW | `install.sh`, merge scripts, `sync.mjs` | plain install now merges: retired entries survive without a sidecar | fixed | closed (stderr note); migration line goes into the v9.0.0 notes (`task-T679.md` section 3a); matched to its fix by theme only (reviewer's own caveat) | devops-engineer | - |
| SEC-T672-07 | LOW | `install.sh`, merge scripts, `sync.mjs` | atomic-write robustness gaps | fixed | closed by the delta review | devops-engineer | - |
| SEC-T672-08 | LOW | `install.sh`, merge scripts, `sync.mjs` | `sync.mjs` did not validate manifest paths | fixed | closed by the delta review | devops-engineer | - |
| SEC-T672-09 | LOW | `install.sh`, merge scripts, `sync.mjs` | `splitInlineArray` read some YAML forms differently | fixed | closed by the delta review; matched to its fix by theme only (reviewer's own caveat) | devops-engineer | - |
| SEC-T672-10 | LOW | `install.sh`, merge scripts, `sync.mjs` | any `_*.json` in `platforms/` skipped silently | fixed | closed by the delta review; matched to its fix by theme only (reviewer's own caveat) | devops-engineer | - |
| SEC-T672-11 | LOW | `install.sh`, merge scripts, `sync.mjs` | test gaps | fixed | closed by the delta review; matched to its fix by theme only (reviewer's own caveat) | devops-engineer | - |
| SEC-T672-12 | LOW | `install.sh`, merge scripts, `sync.mjs` | the swap reset the tree root mode | fixed | closed by the delta review | devops-engineer | - |
| T672-N-1 | LOW | installer / generator | `merge-mcp-json.py` printed user-file names unsanitised | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-2 | LOW | installer / generator | old directory mode applied before the copy (availability) | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-3 | LOW | installer / generator | second signal during `swap_cleanup`; `mv -T` | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-4 | LOW | installer / generator | `sync.mjs` did not normalise an absolute `--root` | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-5 | LOW | installer / generator | `assertUnderRoot` only prevents leaving ROOT; overlapping trees unchecked | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-6 | LOW | installer / generator | schema `relPath` pattern did not cross a newline | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-7 | LOW | installer / generator | stale `emage-old/new` sibling after SIGKILL undetected | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |
| T672-N-8 | LOW | installer / generator | `merge-task-docs.py` `main()` caught only `SymlinkRefused` | fixed | T682 (33f6375b): N-1..N-8 closed (`security-review-t682-installer-residuals-v1.md`, PASS) | devops-engineer | - |

### 3.6 security-review-t674-doc-corrections-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T674-01 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | severity page rows S7/S4, S6/S7 readable without the security carve-out | fixed | closed; T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-02 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | GitLab README version basis not pinned to 2.2.5 | fixed | closed (unverified points labelled); T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-03 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | "a plugin" named as an Opencode override source without a source | fixed | closed; T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-04 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | dangling references; awkward branch-protection pairing | fixed | closed; T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-05 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | "all six do today" for the Playwright notice | fixed | closed; T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-06 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | repo-local git config could change the submodule statement | tracked-LOW | text closed ("with default git configuration"); the optional code hardening `-c submodule.recurse=false` in `git_executor.HARDENING` is a separate code task, not opened; T674 merge fdc689f8 | devops-engineer | next task that touches `git_executor` |
| SEC-T674-07 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | Reporter-profile failure stated as fact without the label | fixed | closed by the orchestrator; T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-08 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | two minor inconsistencies in the role statements | fixed | closed by the orchestrator; T674 merge fdc689f8 | technical-writer | - |
| SEC-T674-09 | LOW | wiki / `PREREQUISITES.md` / `AGENTS.md` | merge-order dependency on the T681 artifact | fixed | handled: !605 merged first; T674 merge fdc689f8 | technical-writer | - |

### 3.7 security-review-t675-ci-release-hardening-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T675-01 | LOW | CI / release tooling / `audit_server.py` | `.env*` deny narrower than the intent (`.envs/`, `*.pem`, `.git/config`...) | fixed | aa0371e; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-02 | LOW | CI / release tooling / `audit_server.py` | roots from `--allow-git-worktrees` not filtered like explicit roots | fixed | aa0371e (`root_is_too_broad`); T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-03 | LOW | CI / release tooling / `audit_server.py` | digests froze two end-of-life bases (`alpine:3.20`, `node:20-alpine`) | fixed | T676: `node:24-alpine`, `python:3.12-alpine` by digest with a review-date guard; T685 replaced EOL examples in two knowledge files; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-04 | LOW | CI / release tooling / `audit_server.py` | CI skipped the tests that prove the new controls | fixed | aa0371e; install on musl/Alpine unverified until the first pipeline; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-05 | LOW | CI / release tooling / `audit_server.py` | empty `--expected-host` turned the host pin off | fixed | aa0371e; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-06 | LOW | CI / release tooling / `audit_server.py` | placeholder gate skippable; `FIELD_RE` backtracked | fixed | aa0371e; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-07 | LOW | CI / release tooling / `audit_server.py` | dry-run network guard no longer covered `OPENER.open` | fixed | aa0371e; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-08 | LOW | CI / release tooling / `audit_server.py` | several controls pinned only by redundant checks or untested | tracked-LOW | partly fixed in aa0371e; the remainder was routed to T673 and is not named in the T673 outcome (not traced); T675 merge 9a0d91db | devops-engineer | next task that touches `publish-release.py`/tests |
| SEC-T675-09 | LOW | CI / release tooling / `audit_server.py` | floating PyPI packages in the job that binds the Docker socket | fixed | T676: `ci/requirements-*.txt` with `--require-hashes --only-binary=:all:`; T675 merge 9a0d91db | devops-engineer | - |
| SEC-T675-10 | LOW | CI / release tooling / `audit_server.py` | residual nits in the release script | tracked-LOW | mostly fixed in aa0371e; Markdown escaping of subjects beyond control characters not traced; bidi and invisible characters handled by T676/T685 (residual SEC-T685-02); T675 merge 9a0d91db | devops-engineer | next task that touches `publish-release.py`/tests |

### 3.8 security-review-t676-supply-chain-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T676-01 | SECURITY:MEDIUM | `docs/wiki/mcp-pin-bump-checklist.md` isolated command | The "isolated" command expanded `$HOME` and printed the real global config; a bearer value reached a session transcript | fixed | command fixed and pinned by a test (T676, merge b78b8e0a); the credential printed in that session must be treated as exposed, rotation is the user's (section 5, action 1) | devops-engineer | - |
| SEC-T676-02 | SECURITY:MEDIUM | `servers.yaml` `brave` pin | `npm audit`: 2 high findings from `@brave/brave-search-mcp-server@2.1.4` via `@modelcontextprotocol/sdk@1.30.0` (five GHSA) | accepted | user, 2026-10-22: "Accept with conditions (Recommended)"; `brave-audit-acceptance-v1.md`, v2 (T685) changes only the command syntax; expiry the first brave release above 2.1.4 or 2026-11-21 | user | - |
| SEC-T676-03 | LOW | supply chain / CI / checklist | `audit` could print "no known vulnerabilities" for an unexpected JSON object | fixed | fixed | devops-engineer | - |
| SEC-T676-04 | LOW | supply chain / CI / checklist | npm subprocess read `~/.npmrc`; redirects followed; titles unfiltered | fixed | fixed | devops-engineer | - |
| SEC-T676-05 | LOW | supply chain / CI / checklist | a lone CR forged a changelog entry; invisible tag characters survived | fixed | fixed (NUL framing, extended class); residual SEC-T676-12 then SEC-T685-02 | devops-engineer | - |
| SEC-T676-06 | LOW | supply chain / CI / checklist | blocked-origins list: no matcher test; apex names not blocked | fixed | fixed (39 entries, ported matcher test); Teredo and trailing-dot forms documented as residual | devops-engineer | - |
| SEC-T676-07 | LOW | supply chain / CI / checklist | GitHub server read-only default: restore advice incomplete | fixed | closed by removal (user decision 2026-10-22) | devops-engineer | - |
| SEC-T676-08 | LOW | supply chain / CI / checklist | hash-locked installs could still build from source | fixed | fixed (`--only-binary=:all:`) | devops-engineer | - |
| SEC-T676-09 | LOW | supply chain / CI / checklist | `python:3.12-alpine` digest stale; EOL table static | fixed | fixed (re-resolved digest, 120-day review guard) | devops-engineer | - |
| SEC-T676-10 | LOW | supply chain / CI / checklist | checklist test gaps; secret regex | fixed | fixed | devops-engineer | - |
| SEC-T676-11 | LOW | supply chain / CI / checklist | `--accept` global by advisory id; date unbounded | fixed | T685 (f9001692): `GHSA:date:package@version`, a pin bump voids it, 90-day bound (`brave-audit-acceptance-v2.md`) | devops-engineer | - |
| SEC-T676-12 | LOW | supply chain / CI / checklist | NUL framing untested across several commits; U+034F and Khmer vowels not in the unsafe class | fixed | T685: class extended, 3-commit real-git test; residual SEC-T685-02 | devops-engineer | - |
| SEC-T676-13 | LOW | supply chain / CI / checklist | user-owned GitHub server has no generated denial; notes do not mention revoking the PAT | fixed | T685: two sentences in the upgrade note (to be carried into the v9.0.0 migration item, `task-T679.md` section 3a) | devops-engineer | - |
| SEC-T676-14 | INFO | CI lock `--exclude-newer` | The lock cutoff equals the generation day: reproducibility, not a cooldown | tracked-LOW | optional at the next lock regeneration; T685 added the seven-day cooldown note | devops-engineer | next lock regeneration |

### 3.9 security-review-t678-cursor-docs-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T678-01 | LOW | `tests/functional/test_mcp_server_denials.py:654` | Guard regex still names Cursor | fixed | T673 (1c9aa063): sentence-level open-claim check, no Cursor wording | qa-engineer | - |
| SEC-T678-02 | LOW | `docs/wiki/mcp-servers.md:78`; `PREREQUISITES.md:33` | Citations of `mcp-server-denials-v1.md` lacked the "recorded before Cursor was removed" clause | fixed | fixed in the T678 branch (403a7dfb) | technical-writer | - |
| SEC-T678-03 | LOW | v9.0.0 migration item | No live doc says a leftover `.cursor/` is no longer updated and its agents are not tool-restricted | tracked-LOW | carried in `task-T679.md` section 3a; closed when the v9.0.0 release document carries it | release-manager + technical-writer | v9.0.0 release document |

### 3.10 security-review-t680-pi-placeholders-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T680-01 | SECURITY:MEDIUM | `.pi/mcp.json` generator and merge | a literal token typed into an omitted Pi key was kept by the merge | fixed | WARNING for a kept credential-like literal (names only); T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-02 | LOW | `.pi/mcp.json` generator and merge | `optional` on a header would silently drop it on Pi | fixed | `optional` refused on `headers`; T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-03 | LOW | `.pi/mcp.json` generator and merge | `hindsight`, `cwso` generated for Pi though Pi 1.x rejects a templated url | fixed | `skipFormats: [pi]` and prune; T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-04 | LOW | `.pi/mcp.json` generator and merge | verification claims broader than the evidence | fixed | four named releases, scoped claims; T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-05 | LOW | `.pi/mcp.json` generator and merge | drop is lossy and printed names are not escaped | fixed | `format_names()` helper (last round, not re-read by the reviewer); T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-06 | LOW | `.pi/mcp.json` generator and merge | test and mutation gaps | fixed | fixed; T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-07 | LOW | `.pi/mcp.json` generator and merge | literal-credential classifier treated `${VAR:-glpat-...}` as a placeholder | fixed | full-match rule (last round, not re-read); T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-08 | LOW | `.pi/mcp.json` generator and merge | quadratic regex on a hostile value | fixed | 4096-character cap (last round, not re-read); T680 merge 01d023ed | devops-engineer | - |
| SEC-T680-09 | LOW | `.pi/mcp.json` generator and merge | pruning a hand-fixed `hindsight`/`cwso` loses it with no backup | fixed | migration text and a note (last round, not re-read); T680 merge 01d023ed | devops-engineer | - |

### 3.11 security-review-t682-installer-residuals-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T682-01 | LOW | `swap_cleanup` | Cleanup could not remove a read-only build tree | fixed | 535b40fe (not re-read by the reviewer) | devops-engineer | - |
| SEC-T682-02 | LOW | `swap_cleanup` | "Swap complete" inferred from `dest` existing: could delete the user's only old tree | fixed | 535b40fe (`SWAP_DONE`); equivalent mutation survivor S02f documented | devops-engineer | - |
| SEC-T682-03 | LOW | N-7 display and hint | Locale-dependent `printable`; nesting hint; no hostile-name paste test | fixed | closed in substance by T684 (eb692776); display point remains as SEC-T684-03 | devops-engineer | - |
| SEC-T682-04 | LOW | `sync.mjs` overlap check | `mcp.outputFile` and its sidecar only constrained to ROOT; lexical comparison | fixed | closed in substance by T684 (`physicalFolded`, `mcpFiles`); residuals SEC-T684-01, -02 | devops-engineer | - |
| SEC-T682-05 | LOW | `discard_old_tree` | `chmod -R` on a symlink argument | fixed | 535b40fe | devops-engineer | - |
| SEC-T682-06 | LOW | `merge-task-docs.py` | N-8 message overclaims; preflight does not run the merge; copies not atomic | fixed | closed in substance by T684 (plan-then-write); residuals SEC-T684-04, -05 | devops-engineer | - |

### 3.12 security-review-t684-installer-hardening-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T684-01 | LOW | `sync.mjs:944` | `physicalFolded` follows a dangling link with a lexical `dirname` (a dangling `../` behind a symlinked parent lands in the wrong place). Fix: `path.resolve(await fs.realpath(path.dirname(current)), link)` | tracked-LOW | reviewer's proposal; T684 merge eb692776 | devops-engineer | next task that touches the installer / `merge-task-docs.py` |
| SEC-T684-02 | LOW | `sync.mjs` `mcp.outputFile` | `outputFile` guarded by a deny-list of inputs only; not compared with other manifests' removal trees. Fix: allowlist under the manifest's own `outputDir` plus the two exact exceptions | tracked-LOW | reviewer's proposal; T684 merge eb692776 | devops-engineer | next task that touches the installer / `merge-task-docs.py` |
| SEC-T684-03 | LOW | `install.sh:279-281` | locale-dependent `printable` still shows target-controlled names; U+202E passes `[:print:]`. Fix: `printable() { ascii_printable "$1"; }` | tracked-LOW | reviewer's proposal; T684 merge eb692776 | devops-engineer | next task that touches the installer / `merge-task-docs.py` |
| SEC-T684-04 | LOW | `merge-task-docs.py` `_atomic_write_bytes` | no `fsync` of the temp file or the directory (kill-safe, not power-loss-safe). Fix: fsync both | tracked-LOW | reviewer's proposal; T684 merge eb692776 | devops-engineer | next task that touches the installer / `merge-task-docs.py` |
| SEC-T684-05 | LOW | `merge-task-docs.py` seeds | seeds published with `os.replace` can clobber a file created between planning and writing; `dest_dir.mkdir` before the dry-run guard (pre-existing). Fix: `os.link`/exclusive create; move `mkdir` after the guard | tracked-LOW | reviewer's proposal; T684 merge eb692776 | devops-engineer | next task that touches the installer / `merge-task-docs.py` |
| SEC-T684-06 | LOW | tests | T04j not strictly equivalent; no non-UTF-8 name test; bash 3.2 `%q` unverified; a mode assertion that cannot fail. Fix: add the 41-link test; use a ledger mode other than 0600 | tracked-LOW | reviewer's proposal; T684 merge eb692776 | devops-engineer | next task that touches the installer / `merge-task-docs.py` |

### 3.13 security-review-t685-supply-chain-residuals-v1.md

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| SEC-T685-01 | LOW | `scripts/check-release-tag-tree.py` | `origin/main` resolved by git's short-name search: a tag named `origin/main` shadows it. Fix: resolve `refs/remotes/origin/main` and test a fixture with such a tag | tracked-LOW | reviewer's proposal; T685 merge f9001692 | devops-engineer | next task that touches the release gate (T686 touches `.gitlab-ci.yml`) |
| SEC-T685-02 | LOW | `publish-release.py` subject unsafe class | Default-ignorable code points still missing (U+180B-180F, U+206A-206F, U+FFF0-FFF8 and others). Fix: category test (`Cc`, `Cf`, `Zl`, `Zp`, `Co`, `Cn`) plus the explicit `Mn`/`Lo` list | tracked-LOW | reviewer's proposal | devops-engineer | next task that touches `publish-release.py` (T686) |
| SEC-T685-03 | LOW | `scripts/verify-release-docs.py:15-17`; `CONTRIBUTING.md` | Docstring still says the main duty is enforced "within its grace window"; CONTRIBUTING silent on pre-release tags, the retag procedure and the hotfix-during-release case | tracked-LOW | reviewer's proposal; T686 also edits `CONTRIBUTING.md` | technical-writer | T686 documentation part or the v9.0.0 release preparation |

### 3.14 this register (reading of the wiki page and of the T664 design)

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| TD-T687-01 | decision | `implementation/knowledge/mcp/servers.yaml` `gitlab` entry; `gitlab-token-handling-design-v1.md` DEC-T664-3 | DEC-T664-3(c): a `GITLAB_DENIED_TOOLS_REGEX` for merge, push and release tools "after T667" was recommended; the entry does not set it and no task names it. Whether the user's "Accept the defaults (Recommended)" included (c) is not recorded (unverified) | open | no task; decision needed (section 5, decision D-2) | orchestrator -> user | - |

### 3.15 `docs/wiki/severity-and-grade-scales.md` § Known gaps

| Id | Grade | Location | Description | Status | Note | Owner | Home |
|---|---|---|---|---|---|---|---|
| TD-T687-02 | LOW | `docs/wiki/severity-and-grade-scales.md` § Known gaps item 5 | `qa-engineer` § Bug Report Format lists `P0`-`P3` while `AGENTS.md` defines `P0`-`P2` | tracked-LOW | found by T674 while writing the page; rulings belong to the owner of the defining document | solution-architect (ruling), technical-writer | next knowledge batch |
| TD-T687-03 | LOW | `docs/wiki/severity-and-grade-scales.md` § Known gaps item 5 | `release-workflow` § Hotfix Workflow says "severity (must be critical or high)" without naming the scale (S2 vs S7 casing) | tracked-LOW | found by T674 while writing the page; rulings belong to the owner of the defining document | solution-architect (ruling), technical-writer | next knowledge batch |
| TD-T687-04 | LOW | `docs/wiki/severity-and-grade-scales.md` § Known gaps item 5 | `security-engineer` § Security Review Report Format uses a third casing of S5 and V1 | tracked-LOW | found by T674 while writing the page; rulings belong to the owner of the defining document | solution-architect (ruling), technical-writer | next knowledge batch |

### 3.16 INFO items without an id

Recorded so they are not lost; none is graded.

- T672 review: a leftover `.<name>.<random>.tmp` after SIGKILL could be committed by mistake; `--validate-only` requires W_OK on the file itself; replacing a file drops owner, ACL and hard links.
- T665 review: `O_NOFOLLOW` covers only the last path component; Python `strip()` differs from the server's `trim()` at a few edge characters; no `O_NOCTTY`.
- T685 review: the 90-day bound is relative to the run day; an acceptance whose advisory no longer appears prints as accepted and does not fail; the tag gate and the release job come from the tagged commit, so they guard process errors, not a malicious tagger (the real controls are protected tags and a protected token); the docs say an acceptance counts "only when that package is the only pinned package" while the code accepts when every at-risk pin has its own acceptance; "revoke or unset" suggests unsetting removes the credential; the unsafe class strips U+200C/U+200D used in Persian and Indic subjects; a non-UTF-8 path in a failing diff raises a traceback in `check-release-tag-tree.py` (fail-closed); `node:24-alpine` enters maintenance on 2026-10-20 and Node 26 becomes LTS on 2026-10-28.
- T680 review: Pi has no per-server environment scoping (documented); the trust prompt for a project-level `.pi/mcp.json` is unverified; a stale exported `GITLAB_PERSONAL_ACCESS_TOKEN` still wins over `_FILE` (documented).

## 4. Open items by theme

Rule applied: `MEDIUM` and higher must be closed or accepted by the user (the one open MEDIUM is theme 7); `LOW` items stay open as debt with an owner; no task is created per round. "Home" names where the work would land if the user wants it done, never a new task. Tasks that already exist: T677 and T686 (both in flight).

### 1. Installer, merge scripts and generator (tracked-LOW)

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| SEC-T684-01, -02, -03, -04, -05, -06 | LOW | Dangling-link resolution, `mcp.outputFile` allowlist, ASCII-only `printable`, `fsync`, seed clobber race, test accuracy (section 3.12). | devops-engineer | the next task that touches `install.sh`, `sync.mjs` or `merge-task-docs.py`; batch all six |
| SEC-T663-02 | LOW | Migrate the Opencode `tools:` map to a `permission:` block; refused-call check. | devops-engineer | next Opencode generator change |
| TD-T671-P5 | LOW | `audience:` declared on commands but implemented nowhere. | devops-engineer | a task that touches commands and the installer |
| TD-T671-K5 | LOW | Hard-coded `context-retriever` index directory. | devops-engineer | next `servers.yaml` change |

### 2. CI, release and supply chain (tracked-LOW)

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| SEC-003 | LOW (user statement D-4) | Release job still uses the wiki token; argv part fixed. | devops-engineer | T686 (in flight) |
| SEC-T685-01, -02, -03 | LOW | `origin/main` shadowing by a tag, default-ignorable code points, stale gate docstring and CONTRIBUTING gaps (section 3.13). | devops-engineer; technical-writer for -03 | T686 touches `.gitlab-ci.yml`, `publish-release.py` and `CONTRIBUTING.md`: the natural carrier, if the user wants them folded in; otherwise the next release-tooling task |
| SEC-T675-08, SEC-T675-10 | LOW | Remainder of weakly pinned controls; Markdown escaping of commit subjects (not traced). | devops-engineer | next release-tooling task |
| SEC-T676-14 | INFO | Lock `--exclude-newer` is the generation day. | devops-engineer | next lock regeneration |
| SEC-T674-06 | LOW | Optional `-c submodule.recurse=false` in `git_executor.HARDENING`. | devops-engineer | next change to the PoC scanner |
| SEC-011 | LOW | `.match` with `$` accepts a trailing newline in five validators (fails closed in git). | backend-developer | next change to `poc_scan.py` (S: `fullmatch` + test) |
| SEC-014 | LOW | Hash pinning delivered; `git tag -v` documentation needs the signing decision D-7. | user, then technical-writer | decision D-7 |

### 3. Tool restriction and the GitLab surface

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| SEC-T660-02 | LOW (decision) | Raw job traces in `qa-engineer`. | user | decision D-1 |
| TD-T687-01 | decision | DEC-T664-3(c): denied-tools regex not shipped, no task. | user | decision D-2 |
| SEC-T665-07 | LOW | One shared Developer-level token for three roles; stays open with the exposure sentence and the Reporter profile (user decision 2026-10-22). | devops-engineer (if reopened) | reopening conditions in `gitlab-per-role-token-design-v1.md` section 5.3 |
| SEC-T658-02, K-20 | LOW / info | Gemini CLI denial and the Opencode refused call never run; Copilot grants and Pi list handling unobserved. | user or an authorised live session | section 5, action A-7 |

### 4. Documentation, knowledge text and rulings (tracked-LOW)

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| RO621-N-1, RO621-N-2 | observation | Legacy `DEBT:` input wording; no stated home for `TECHNICAL-DEBT.md`. | solution-architect (ruling), technical-writer | decision D-5; then one small knowledge edit |
| RO621-N-3, TD-T671-P16, TD-T671-T538, TD-T671-T554 | LOW | `priority::critical` missing from the Scrum Master labels; `batch.md` slug charset; colour swap; no-op pack merge step. | technical-writer | one small knowledge batch (projections change) |
| TD-T687-02, -03, -04 | LOW | Three scale inconsistencies found while writing the severity page. | solution-architect (ruling), technical-writer | same batch |
| P112-P41-O1 | observation | Release self-review: the orchestrator delegates preparation and the Release gate to `@release-manager`. | solution-architect / user | decision D-5 |
| TD-T671-legacy | LOW (unverified) | Older parked remarks, not re-read in v1 or v2. | orchestrator | spot-check before the next plan |

### 5. Function size (T677 in flight)

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| TL-T649-01 | Should Fix | Six functions over 50 lines. | devops-engineer | T677 (in flight); lengths not re-measured here |
| TD-T671-FN1 | Should Fix | `render_installed_agents.py` `render` (91 lines), not in the T677 brief. | devops-engineer | decision D-8: extend T677 or accept |
| TD-T671-FN2 | Nice to Have | About 45 Python functions over 50 lines elsewhere. | tech-lead | accept (decision D-8); re-scan at the next register |

### 6. Golden suite

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| K-2b | info | Four `capability_gap` goldens stay `known_failing`. | user | decision D-6 (grant G-3 and a later baseline) |

### 7. v9.0.0 release items

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| SEC-T662-01 | SECURITY:MEDIUM | The v9.0.0 release document must carry the Cursor migration item (M-9 steps, the v5.0.0-v6.9.0 keys, `--force-prune-keys` only from the v8.0.0 tag, the "frozen Cursor install" Known Issue) and the release gate must check that the pointer target exists. | release-manager + technical-writer | v9.0.0 release preparation. `task-T679.md` section 3a does not list it (decision D-9). MEDIUM: must be closed before the release is tagged |
| SEC-T678-03 | LOW | A leftover `.cursor/` is no longer updated and its agents are not tool-restricted. | release-manager + technical-writer | v9.0.0 release document (listed in 3a) |

### 8. User actions with an id

| Id | Grade | What is open | Owner | Home or next step |
|---|---|---|---|---|
| TD-T671-ENVTOKEN | process (user) | Check or rotate the CWSO bearer token in the local `.env`. | user | section 5, action A-3 |

## 5. User actions and decisions with no task

### 5.1 User actions (agents cannot do them)

| # | Action | Source | Detail |
|---|---|---|---|
| A-1 | Rotate the bearer credential that the T676 session exposed | SEC-T676-01 | The checklist's "isolated" command expanded `$HOME`, printed the real global config and a bearer value reached a session transcript. The review says to treat that credential as exposed and that rotation is "a user action, to be confirmed". Which credential it was is not named in any artifact I read; whether it is the one of A-3 is unverified. The command is fixed and pinned by a test. |
| A-2 | Live checks 1 to 3 of the T665 design (throwaway token, scratch project) | SEC-T665-01; `gitlab-token-handling-design-v1.md` section 8.4; T665 outcome ("the three live checks ... are the user's and unrun") | (1) a fine-grained PAT against the 20 `qa-engineer` and 24 `scrum-master` tools; (2) Claude Code with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`; (3) the empty `${VAR:-}` default with a set `_FILE`. Checks 4 (placeholder expansion on Gemini CLI, Pi, Cline, VS Code) and 5 (a Developer token merging into a protected branch) of the design are also unrun; the documents label every dependent claim "unverified". |
| A-3 | Check or rotate the CWSO bearer token in the local `.env` | TD-T671-ENVTOKEN (SEC-T650-05, checkpoint-038 section 9) | Its `exp` claim appeared past in a search result; not verified; not inspectable by agents. T675 closed the tool-side exposure (secret-bearing paths are denied). |
| A-4 | Set `WIKI_TOKEN` as a protected, masked variable with the minimum role; restrict protected `v*` tags to Maintainers | SEC-T650-03 (D-4), SEC-003; T685 report; T686 docs | D-4 is the user's statement ("Yes, both are set"), not verified by any agent. T686 documents it and moves the release job to the job token; `WIKI_TOKEN` then serves only `wiki-sync`. Anyone who can push a release tag runs the tagged commit's script with the job's variables until then. |
| A-5 | Run and record the first real tag pipeline | T675, T676, T685, T662, T686 | To confirm: the `main-develop-drift-gate` output carries `release-tree: PASS`; the tag ref exists after the tags fetch; `needs` still gates `release`; the pinned images and `apk ~=` pins resolve; the `unit-tests` job fetches `v8.0.0` under `GIT_DEPTH 20` (SEC-T662-02) and installs ripgrep and `mcp` on musl (SEC-T675-04); whether job tokens work in tag pipelines on protected tags in this instance (T686); the first run of the changed `.gitlab-ci.yml`. Keep the manual `glab release create` fallback until then (T686). |
| A-6 | Brave audit acceptance expiry | SEC-T676-02; `brave-audit-acceptance-v2.md` | Expires on the earlier of the first `@brave/brave-search-mcp-server` release above 2.1.4 and **2026-11-21**. After that `python3 scripts/audit-mcp-pins.py audit --audit-level high` must pass without `--accept` for these ids, or the user renews the decision in a new artifact version. Do not set `BRAVE_MCP_TRANSPORT=http` meanwhile (reopens GHSA-46jr-4wx8-v453). |
| A-7 | Live checks of the Gemini CLI and Opencode denials | SEC-T658-02, K-20; checklist section 6 | Opencode resolved rules observed 2026-10-22 (opencode 1.18.31); the refused call and the whole Gemini CLI check are not run (the CLI was not installed on the T676 host). |
| A-8 | Approve the T679 root refresh (ADR-010 step S3) | `task-T679.md`; D-1 of the T666/T667 review | Needs the user's approval at that step. Until it runs, this repository's own installed agents keep the pre-T666 grants (`.claude/agents` and the other root trees). |
| A-9 | The v9.0.0 migration items (reference only; no action now) | `docs/tasks/task-T679.md` section 3a | Listed there: SEC-T678-03 (leftover `.cursor/`); T672 (plain install merges, the no-sidecar note, new on-disk names); T676 (BREAKING: the `github` server is removed; copy the entry under your own name before `--update`; `docker` is no longer a launcher; SEC-T676-13 sentences); T680 (Pi placeholders, `hindsight`/`cwso` not generated for Pi). **Not listed there: SEC-T662-01** (decision D-9). |

### 5.2 Decisions

| # | Decision | Options | Recommendation (mine; the user decides) |
|---|---|---|---|
| D-1 | SEC-T660-02: raw job traces (last 1000 lines) in `qa-engineer`, which can hold unmasked secrets and attacker-influenced text that the model may copy into a bug issue. **No task exists.** | (a) Fix: drop `get_pipeline_job_output` from `qa-engineer` (20 to 19 tools), add a body line "never paste raw job output into issues", regenerate the projections, update the pinned counts (a one-line knowledge edit plus tests). (b) Document: keep the tool, add the body line and a sentence in the wiki. (c) Accept as is: defensible for the QA gate; `devops-engineer` already lost the tool in T667. | (a) if the QA role can work from `get_pipeline_job` and the test report; otherwise (b). Under the LOW policy (c) is allowed, with this register as the record. |
| D-2 | TD-T687-01: ship a `GITLAB_DENIED_TOOLS_REGEX` for merge, push and release tools (DEC-T664-3(c), "after T667") | (a) Ship it in the generated `gitlab` entry. (b) Keep it a documented operator control only (today). The recommendation of the design was conditional on the user not using MCP delete/cancel tools in the own session. | (b) unless you want the server to refuse those tools for every client; then (a) as a small task with a Security Engineer read. |
| D-3 | SEC-T665-03: confirm that a plaintext token file at rest does not breach Immutable Security Constraint 6 | The orchestrator's position ("not breached": the harness stores nothing, the file is the user's own credential outside the repository, the previous `export` in a profile file was worse, and the position holds only through the stated full-disk-encryption assumption) was "for the user to confirm". No confirmation was found in the plan, the ledger or the reviews. | Confirm or reject in one line; the documents already state the assumption. |
| D-4 | K-3: should GitHub Copilot carry the extended servers (`security-audit`, `poc-security-audit`)? Today the PoC security scan cannot complete there and the agent rule makes that a FAIL. | (a) Accept the platform limitation (v1 proposal). (b) Generate the two servers for Copilot (a generator task). | (a). |
| D-5 | Rulings on P112-P41-O1 (release self-review), RO621-N-1 (legacy `DEBT:` wording), RO621-N-2 (where `TECHNICAL-DEBT.md` lives) | Rule by ADR/instruction edit, or accept as is. | Accept RO621-N-1 (harmless); rule N-2 in one sentence; P112-P41-O1 needs the solution-architect (ADR-008 step A) or your acceptance. |
| D-6 | K-2b: the four `capability_gap` goldens stay `known_failing` | (a) Leave them (they are honest). (b) Check whether the T580/T582 amendments close the gaps, then a grant G-3 and a later baseline. | (a) for now. |
| D-7 | SEC-014: sign release tags so that `git tag -v` can be documented? | (a) Yes: sign, then document `git tag -v` and add key distribution. (b) No: record the decision and close SEC-014 as accepted. (The contribution guide uses `git tag -a`.) | (b) unless a signing key already exists. |
| D-8 | TD-T671-FN1 and TD-T671-FN2 | FN1: extend T677 with `render_installed_agents.py` `render`, or accept. FN2: accept as pre-existing (the standard applies to new and changed code) or order a sweep. | Extend T677 by one function; accept FN2. |
| D-9 | SEC-T662-01 is not in `task-T679.md` section 3a, and no v9.0.0 release task exists | The orchestrator adds the M-9 steps list, the v5.0.0-v6.9.0 keys, the `--force-prune-keys` only-from-v8.0.0 sentence and the "frozen Cursor install" Known Issue to the T679 brief 3a (or to the release-manager brief), and a gate check that the pointer target exists. This is a MEDIUM finding: it must be closed before the tag. | Do it when the release is prepared; no new task is needed. |
| D-10 | Whether the user confirmed T667's merge exclusion for `devops-engineer` and `release-manager` (plan-123 Open Question 3) | Not recorded in the plan, the T667 outcome or the review (unverified). The project rule is that subagents never merge, and the role texts now say so. | Record the confirmation in the next checkpoint if it was given. |

## 6. Accepted risks

### 6.1 Accepted by the user (words and dates)

| Item | Date | The user's words (AskUserQuestion option labels, verbatim) | What stays |
|---|---|---|---|
| SEC-T658-01 / SEC-T657-01 (Playwright narrowing) | 2026-10-15; 2026-10-16 | "Accept the unfixable remainder; fix the rest after v8.0.0 (Recommended)"; for the Cursor part: "I want to drop Cursor support completely"; for built-in Opencode agents: "No, document the gap only (Recommended)"; read/search servers: "Exempt the read/search servers (Recommended)" | Gemini CLI (every agent can call every tool), Pi agents without `mcp__` entries, Opencode built-in agents, a later config source or user agent file on Opencode; the Cursor part disappeared with T662. |
| SEC-T660-01 / SEC-T665-01 (GitLab token reachable from the environment) | 2026-10-15; 2026-10-16 | "Accept the risk, plan after the release (Recommended)"; then "Adopt D and re-accept the residual (Recommended)" and "Accept the defaults (Recommended)" | Mitigated, not closed: six of seven GitLab roles hold `execute` and run as the user; closure only by an isolated user, container or VM. |
| SEC-T665-07 / DEC-T681-1 (one shared Developer-level token) | 2026-10-22 | "A: status quo + exposure sentence (Recommended)"; "Yes, document it (Recommended)" (Reporter profile) | Stays open as LOW with an accurate description; options B, C, D not pursued. |
| SEC-T676-02 (Brave audit, two high findings via the MCP SDK 1.30.0) | 2026-10-22 | "Accept with conditions (Recommended)" | Stdio launch only; expiry the first brave release above 2.1.4 or 2026-11-21 (`brave-audit-acceptance-v1.md`, `-v2.md`). |
| SEC-T650-03 / SEC-003 grade (the wiki token is protected and masked, `v*` tags are protected) | 2026-10-15 | "I'll check; both are set (grade drops to LOW)"; "Yes, both are set" | Not verified by any agent; if false, SEC-003 returns to MEDIUM or higher (action A-4). |
| SIGNOFF-CR649 (tech-lead promoted and also reviewed the release) | 2026-10-15 | "Acknowledge the disclosure (Recommended)" | Disclosure only. |
| RO621 observations N-4, N-5, O1-b, O5-c | 2026-10-14 | "A1, B1, C1" (all recommended) | Held edits not applied by decision. |

Decisions of the user that are not risk acceptances but shape this register: ADR-010 (2026-10-16): "v9.0.0 (MAJOR), no deprecation release (Recommended)", "B: error plus read-only notice, never delete (Recommended)", "Yes, delete both trees (Recommended)", "Accept all four defaults (Recommended)"; the GitHub MCP server (2026-10-22): "Remove GitHub MCP server" (free-text answer; breaking for v9.0.0); the release job on the job token (2026-10-23): "Yes, create a task to switch (Recommended)"; the LOW policy (2026-10-23): "Track LOW items as debt, stop chasing (Recommended)".

### 6.2 Accepted by a reviewer or documented as a residual (not a decision of the user)

| Item | Basis |
|---|---|
| T636-L6, T636-L7, K-14 | Symlink guard checks the final component only in the Python writers; TOCTOU only under `sudo` into a shared tree. Reviewer-accepted, documented in `usage()`. |
| SEC-T660-05 | Residual powers of four scrum-master tools cannot be restricted by argument. Reviewer-accepted (S660). |
| SEC-T657-04 | The generated `x: true` entries override a user's own `ask`/`deny` on Opencode for held tools; documented and pinned by a test (SEC-T663-03). Accepted as documented behaviour. |
| SEC-T667-03, SEC-T667-06 | `create_merge_request` reaches any project and branch the token reaches; CI lint resolves `include:` server-side. Reviewer-accepted; one sentence each in the docs. |
| SEC-T662-05 | Known false negatives of the Cursor notice. Reviewer-accepted. |
| R-1, K-4 limits | JWT rule cost model and scanner limits: documented fail-closed residuals. R-1's deciding party is recorded only as "measured and accepted" (unverified who). |
| K-10, K-13, K-19, K-21, GOLDEN_VERSION_LABEL, TD-T671-K7, TL-T649-09, CR619-N5, T638-L-1 | Documented behaviour or time-bound items; v1 proposed "accept". No verbatim user decision found. |
| Opencode `tools:` map deprecation, plugin hooks, a later config source | Disclosed residuals of the Opencode denials (SEC-T663-02 and the T663 residuals); the plugin hook is unverified. |

## 7. Method, limits and validation

1. Read v1 in full, the plan with all addenda, `completed-tasks.md` rows T661 to T685 and the 13 review artifacts of T662 to T685, the two brave acceptance versions, the briefs of T671 to T677, T679 and T686, and the two GitLab design artifacts (headings, decisions and the unverified lists). The reviews of T655, T657, T658 and T660 are the sources of v1 and were not re-read for new ids; their ids are all in v1.
2. For each v1 id the repository on develop `f9001692` was read or searched where the change is in code or docs (greps listed in the evidence column: `install.sh`, `merge-mcp-json.py`, `poc_scan.py`, `.gitlab-ci.yml`, `publish-release.py`, `dry-run-publish-release.py`, the knowledge files, the wiki). Closure by T668 to T670, T673, T676 and others also rests on the completed-task outcome and the review text.
3. Ids marked closed on a review or a developer claim without my own read are marked "not re-read by the reviewer" in the note. Every `fixed` of a new id repeats the reviewer's disposition.
4. **Not traced or not verified**: the indentation half of TL-T649-06; the lengths of the functions of TL-T649-01 and TD-T671-FN1 after the T665 to T684 edits; TD-T671-legacy and the T604/T608/T609 individual LOWs (not re-read in v1 either); who accepted R-1; the T673 follow-up on the SEC-T675-08 remainder and on "SEC-T655-10 leftovers"; the Markdown escaping part of SEC-T675-10; whether a test ties `SUPPORTED_PLATFORMS` to the manifests (SEC-T662-03); whether the user confirmed D-10 and D-3; whether D-2 was meant by "Accept the defaults"; the T680 last round, the T682 follow-up commit, T665's `8fcfb72c` and T675's `aa0371e` were not re-read by their reviewers; everything that depends on a real tag pipeline (A-5). The full test suite was not run for this artifact.
5. This register changes no task row, brief, ledger or release document. Dispositions marked "accept" for items the user has not decided are proposals.
6. Validation run by the producer (results in the task report): `python3 docs/tasks/validate-tasks.py`; `python3 -m unittest tests.functional.test_link_integrity tests.performance.test_team_health`.

## 8. Review mode and references

- Reviewed by: Tech Lead, read-only mode (no source modified; the only file written is this artifact).
- Artifact versions referenced: `tracked-debt-register-v1.md`, `plan-123-post-release-follow-ups.md`, and the review artifacts named under "Based on". Decision IDs: ADR-010, DEC-T664-1 to -6, DEC-T681-1 to -3; no ADR is amended.
- Next step: the orchestrator archives T687, decides D-1 to D-10 with the user, and carries section 4 forward; the next register version is due when the LOW policy next needs it (for example after T677 and T686 merge).
