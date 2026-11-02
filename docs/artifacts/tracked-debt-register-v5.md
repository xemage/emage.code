# Artifact: tracked-debt-register-v5.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v4.md` (443 ids; v4 stays the record for every id that was `fixed` or `obsolete` there, and, with v1 to v3, for the text of every carried id); `docs/plans/plan-130-tracked-debt-register-v5.md` and `docs/tasks/task-T729.md` (the user's "v5 go"); `docs/plans/plan-125-post-v9-follow-ups.md` (batch C, T714); the `## Outcome` sections of `docs/plans/plan-126-batch-b-release-tooling.md`, `plan-127-batch-d-knowledge-and-rulings.md`, `plan-128-batch-a-installer-generator.md` and `plan-129-batch-e-cwso-hardening.md` (plan-129 also § Items without code change); `docs/tasks/completed-tasks.md` (rows T714 to T728); the review artifacts `security-review-t714-batch-c-v1.md`, `security-review-t665-token-handling-v3.md`, `security-review-t715-t716-batch-b-v1.md`, `security-review-t718-t720-batch-d-v1.md`, `security-review-t722-t725-batch-a-v1.md`, `security-review-t726-t728-batch-e-v1.md`; `docs/artifacts/rulings-batch-d-v1.md`; `docs/decisions/ADR-011-user-accepted-medium-at-release.md`; `tests/_baselines/root-install-drift.json` (the `_comment` lines of root refreshes 23 and 24). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01), ADR-007, ADR-008, DEC-T681-1, D-T700-1; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T729 (plan-130; the user's answer of 2026-11-02, verbatim: "v5 go"). **Date**: 2026-11-02.
- **Tree read**: branch `agent/tech-lead/T729` at `0ae07c0f` (from `docs/plan-130-register-v5`; develop `a787117b` plus the plan-130 commit). The CWSO repository was not read: every CWSO status comes from plan-129 § Outcome, the T727/T728 rows (CWSO MR !218, CWSO develop `6630ecb`, pipeline 3016294206) and the batch-E review.
- **Review mode**: read-only. A closure cites a completed-task row, a plan outcome, a review artifact or a grep on `0ae07c0f`. "Unchanged" means no task, review or plan outcome since v4 names the id, and I did not re-check the code unless a grep is cited. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary (`fixed`, `accepted`, `obsolete`, `open`, `tracked-LOW`) and id prefixes as in v3 and v4. Decision ids (`D-*` that decide, `R1`-`R10`, `A1`-`A13`, `O1`) and user actions (`A-*`, `UA-*`) are not counted as debt ids, as in v4. The gaps `T717-D1` to `-D3` are debt (found and fixed in plan-126) and are counted.
- **Batch letters**: v4's A to E are all executed (A: plan-128, B: plan-126, C: T714, D: plan-127, E: plan-129). Their remainders and the new ids are regrouped in section 5 into new batches from **G**; F (PoC scanner) and U (live checks and user) keep their letters.

## 1. Summary

v5 holds **500 ids**: the 443 of v4 and **57 new**. After v5: **381 fixed**, **45 accepted**, **6 obsolete**, **1 open**, **67 tracked-LOW**.

- **Open above LOW: none.** The one open id is K-20 (live checks, user). Every new finding is LOW except SEC-T720-01 (MEDIUM), which is fixed (`06a48087`, re-check PASS).
- **Batches B, D, A, E and C closed 70 of v4's 134 carried ids** (69 tracked-LOW plus TD-T713-01, decided by ADR-011). TD-T671-legacy moves from `open` to `tracked-LOW` after the orchestrator's re-read (plan-127).
- **Accepted at MEDIUM by the user**: SEC-T657-01/SEC-T658-01 (remainder), SEC-T660-01, SEC-T665-01, SEC-T702-09 (Brave 2.1.4, acceptance v3), TD-T697-07 (now tied to the CWSO bearer token, SEC-T699-04). **Under ADR-011 every accepted MEDIUM that the next release ships needs the user's new acceptance for that release** (section 6.2).
- **Nearest dates** (section 6.3): Trivy 0.76.1 adoptable from 2026-11-04; GitLab token renewal 2027-01-28; CWSO bearer renewal and the end of TD-T697-07 2027-01-29; Brave acceptance v3 end 2027-01-30. The CWSO `paste` review (2027-01-31) is closed.

### 1.1 v4 ids by v4 status and status now

| v4 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 3 | 1 | 0 | 0 | 1 | 1 |
| tracked-LOW | 86 | 69 | 0 | 0 | 0 | 17 |
| accepted | 45 | 0 | 45 | 0 | 0 | 0 |
| fixed | 303 | 303 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v4 ids** | **443** | **373** | **45** | **6** | **1** | **18** |

The 134 v4 ids that were open, tracked-LOW or accepted are each in section 2. One v4 `fixed` id, SEC-T689-02 (fixed in part), is re-recorded in section 2.4 because T714 closed its rest; it stays `fixed`.

### 1.2 New ids by source (status now)

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t714-batch-c-v1.md` (T714) | 8 | 4 | 4 |
| `security-review-t715-t716-batch-b-v1.md` (T715, T716) | 9 | 0 | 9 |
| plan-126 § Outcome, Added scope (T717-D1 to -D3) | 3 | 3 | 0 |
| `security-review-t718-t720-batch-d-v1.md` (T718 to T720) | 8 | 1 | 7 |
| plan-127 § Outcome (TD-T720-01) | 1 | 0 | 1 |
| `security-review-t722-t725-batch-a-v1.md` (T722 to T725) | 9 | 0 | 9 |
| plan-128 § Outcome (TD-T723-01, TD-T724-01, TD-T725-01) | 3 | 0 | 3 |
| `security-review-t726-t728-batch-e-v1.md` (T726 to T728) | 11 | 0 | 11 |
| plan-129 § Outcome (TD-T726-01, -02, TD-T728-01 to -03) | 5 | 0 | 5 |
| **All new** | **57** | **8** | **49** |

No new id is accepted, obsolete or open. `rulings-batch-d-v1.md`, ADR-011 and `security-review-t665-token-handling-v3.md` (an erratum) mint no finding id. This register mints none.

## 2. v4 ids re-checked

Columns: Id | v4 | now | Batch (section 5) | Evidence or reason. "-" = closed, no batch.

### 2.1 v4 `open` (3)

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| K-20 | open | open | U | Unchanged: no task since v4 ran the live checks (Copilot grants, Gemini denials, Pi lists, Opencode per-agent denies, VS Code behaviour of the two T690 servers). A-7. |
| TD-T671-legacy | open | **tracked-LOW** | H | Re-read by the orchestrator (plan-127 § Outcome): P4 and P7 obsolete, P9 (T566), P11 (T563, T595) and P12 (T563, P29) fixed, the T544 remark is TD-T671-P16 (closed by T719). Left: **P10** (`/new-project` uses `APPROVED`/`APPROVED_WITH_CHANGES`/`REJECTED`, `plan-approve-execute` uses Approve/Revise/Reject), and, parked in protected goldens and needing a grant, **P14, P15 and the remarks of CT rows T539 and T565**. The T547 remark, listed in plan-127 § Task Decomposition, is not named in the outcome **(unverified)**. |
| TD-T713-01 | open (ruling) | **fixed** | - | Decided by the user through ADR-011 (Accepted 2026-11-01: "(a) Time-bound acceptance (Recommended)", end date "Until the next release"); `rulings-batch-d-v1.md` § 3; rows A1 to A13 applied by T720, pinned by T721. |

### 2.2 v4 `tracked-LOW` (86), by v4 batch

**v4 batch A, installer and generator (15; plan-128, rows T722 to T725, `security-review-t722-t725-batch-a-v1.md`)**

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| TD-T671-P5 | tracked-LOW | **fixed** | - | T725: `audience:` implemented and required by the generator; authoring-only commands withheld from targets (`implementation/knowledge/commands/prepare-release.md:6` `audience: authoring`, grep). Residuals SEC-T725-01 to -03, TD-T725-01. |
| TD-T671-K5 | tracked-LOW | **fixed** | - | T722: `context-retriever` index directory derived from the git remote; review § 1 "K5". Residual SEC-T722-04. |
| SEC-T663-02 | tracked-LOW | tracked-LOW | J | Not done (plan-128 § Outcome): Opencode now calls the agent `tools` map deprecated; moving to `permission` changes five test files, documents and recorded live evidence, so it needs its own task. `implementation/.opencode/agents/qa-engineer.md:4` still `tools:` (grep). |
| SEC-T684-01 | tracked-LOW | **fixed** | - | T722: dangling links resolved from the physical parent; review § 1. Residual SEC-T722-01. |
| SEC-T684-02 | tracked-LOW | **fixed** | - | T722: `mcp.outputFile` allowlisted; review § 1. Residual SEC-T722-05. |
| SEC-T684-03 | tracked-LOW | **fixed** | - | T723: byte-wise `printable`; review § 1 T723 "No finding". |
| SEC-T684-04 | tracked-LOW | **fixed** | - | T723: fsync of file and directory; same. |
| SEC-T684-05 | tracked-LOW | **fixed** | - | T723: no-clobber publish, no `mkdir` in a dry run; same. |
| SEC-T684-06 | tracked-LOW | **fixed** | - | T723: 41-link, non-UTF-8 and 0640 tests (`test_sync_symlink_hop_limit.py`); boundary residual SEC-T722-02. |
| SEC-T677-03 | tracked-LOW | **fixed** | - | T723: `usage` without logic (row T723). |
| SEV-T690-01 | tracked-LOW | **fixed** | - | T722: per-agent denials honour `extraPlatforms`; review § 1. |
| SEV-T690-05 | tracked-LOW | **fixed** | - | T722: direct M11 kill and exact sets (row T722). |
| SEV-T690-06 | tracked-LOW | **fixed** | - | T722: grants for servers a platform does not carry dropped; review § 1. Residual SEC-T722-03. |
| QA-T707-01 | tracked-LOW | **fixed** | - | T724: `merge-mcp-json.py` accepts the Opencode `{env:NAME}` form. Residuals SEC-T724-01, TD-T724-01. |
| TL-T708-03 | tracked-LOW | **fixed** | - | T723: Cursor notice one case per line. The published v9.0.0 line reference is TD-T723-01. |

**v4 batch B, release tooling and CI (20; plan-126, rows T715 to T717, `security-review-t715-t716-batch-b-v1.md`)**

plan-126 § Outcome counts "17 closed" and names SEC-T677-01 "partly closed"; the rows give 16 fully closed ids plus SEC-T677-01, so the 17 include it. This register keeps SEC-T677-01 `tracked-LOW` for its residual shapes.

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-T677-01 | tracked-LOW | tracked-LOW (narrowed) | G | T715 closed what a line-based guard can close; the residual shapes are listed in the docstring of `tests/functional/test_function_size.py` (row T715; plan-126 § Outcome). |
| SEC-T677-02 | tracked-LOW | **fixed** | - | T715: tests pin `check_section_requirements` and the `SWAP_*` order; review § 1 "Adequate". Resolves v4's **(unverified)**. |
| SEC-T685-01 | tracked-LOW | **fixed** | - | T716: exact ref names in `check-release-tag-tree.py`; review § 2. The sibling drift script is SEC-T716-01. |
| SEC-T685-02 | tracked-LOW | **fixed** | - | T716: Unicode-category unsafe class; review § 2. Residual SEC-T716-02. |
| SEC-T685-03 | tracked-LOW | **fixed** | - | Code part T715 (docstring matches CI; review § 1); documentation part T717 (`CONTRIBUTING.md`, two cases recorded as not ruled). Resolves v4's **(unverified)**. |
| SEC-T675-08 | tracked-LOW | **fixed** | - | T716: controls traced and mutation-swept (row T716). |
| SEC-T675-10 | tracked-LOW | **fixed** | - | T716: Markdown escaping of changelog entries; review § 2 "Sound". Residuals SEC-T716-03, -05. |
| SEC-T676-14 | tracked-LOW | tracked-LOW | G | Not in plan-126 ("Not in this plan"): due at the next lock regeneration; none planned. |
| SEC-T686-07 | tracked-LOW | **fixed** | - | T716: child environment with stated reasons; review § 2 "Stricter than before". Whether the runner sets a dropped variable **(unverified)** (review). |
| SEC-T686-08 | tracked-LOW | **fixed** | - | T716: one `LC_` rule, pinned by a test; review § 2. |
| SEC-T703-01 | tracked-LOW | **fixed** | - | T715: fenced and commented anchors ignored; review § 1. Residual SEC-T715-03. |
| SEC-T703-02 | tracked-LOW | **fixed** | - | T715: unparsed pointer forms fail; review § 1. Residuals SEC-T715-01, -02. |
| SEC-T703-03 | tracked-LOW | **fixed** | - | T715: newer pointers fail unless `--allow-newer-pointers`; the CI job does not pass it (review § 1). |
| SEC-T712-05 | tracked-LOW | **fixed** | - | T716: `via` shape and cycle tests, two audit defects fixed; review § 2 "Fails closed". |
| SEC-T702-08 | tracked-LOW | tracked-LOW | G | Upstream code (plan-126 "Not in this plan"): the orchestrator offers the user a draft report to the Brave project; the user files it or declines. No user answer found in the read sources **(unverified)**. |
| TL-T708-04 | tracked-LOW | **fixed** | - | T715: version-independent tests; review § 1. |
| TL-T708-05 | tracked-LOW | **fixed** | - | T715: same. |
| TL-T708-06 | tracked-LOW | **fixed** | - | T716: `ApiCredential`/`ApiTarget`; review § 2. Residual SEC-T716-04. |
| TL-T708-07 | tracked-LOW | tracked-LOW | G | Not changed, by the user's T704 decision D-T700-1 "Exclude docs/decisions/ (Recommended)" (row T715). The reviewer found it "acceptable as is" (v4); closing it as `accepted` needs the orchestrator to record that basis. |
| D-T710-2 | tracked-LOW | **fixed** | - | T716: CHANGELOG entry below `[Unreleased]`; review § 2 "correct, with no finding". Verdict condition C-3 of v9.0.0 met in code; first observed only in the next release job **(unverified)**. |

**v4 batch C, token docs and security runtime (8; T714, plan-125, `security-review-t714-batch-c-v1.md` § Disposition of earlier ids)**

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-T701-01 | tracked-LOW | **fixed** | - | T714: hibernation note at `PREREQUISITES.md:155-156`; the immutable T665 record corrected by the erratum `security-review-t665-token-handling-v3.md`. |
| SEC-T701-02 | tracked-LOW | **fixed** | - | T714; § Disposition "closed". |
| SEC-T701-03 | tracked-LOW | **fixed** | - | T714; same. |
| SEC-T689-04 | tracked-LOW | **fixed** | - | T714: `check-gitlab-token.py` names an undetermined storage (`--strict-storage`); wording residual SEC-T714-05 fixed. |
| SEC-T689-05 | tracked-LOW | **fixed** | - | T714: the opened descriptor is checked; mount-namespace limit documented. |
| SEV-T690-02 | tracked-LOW | tracked-LOW (narrowed) | K | Partly closed: the trust-boundary paragraph and CODEOWNERS guidance are in `implementation/SECURITY.md` § 4.2; **the pinned runtime package stays tracked**. |
| SEV-T690-04 | tracked-LOW | tracked-LOW (narrowed) | K | Partly closed: (a) environment, (b) `allowed_root`, (c) names done, with residuals SEC-T714-02, -04, -06, -08; **(d) still open**: the Copilot security agents hold `read`/`search`, so the server's denials are not a boundary there. |
| SEC-T665-07 | tracked-LOW | tracked-LOW | K | Not in T714; unchanged (DEC-T681-1; reopening conditions in `gitlab-per-role-token-design-v1.md` 5.3). |

**v4 batch D, knowledge text and rulings (16 tracked-LOW; plan-127, rows T718 to T721, `rulings-batch-d-v1.md`, `security-review-t718-t720-batch-d-v1.md`)**. The two `open` batch-D ids are in 2.1.

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| RO621-N-3 | tracked-LOW | **fixed** | - | T719: `priority::critical` in scrum-master. |
| TD-T671-P16 | tracked-LOW | **fixed** | - | T719: `/batch` slug character set; review § 1 T719. |
| TD-T671-T538 | tracked-LOW | **fixed** | - | T719: dependency-graphing colours aligned. |
| TD-T671-T554 | tracked-LOW | **fixed** | - | T719: `/discover-skills` step 6 removed under ADR-007 branch 1. |
| TD-T687-02 | tracked-LOW | **fixed** | - | R7 (T718), applied in T720. |
| TD-T687-03 | tracked-LOW | **fixed** | - | R8, applied in T720. Residual TD-T720-01 (two lines R8 did not cover). |
| TD-T687-04 | tracked-LOW | **fixed** | - | R9, applied in T720. |
| SEC-T693-02 | tracked-LOW | **fixed** | - | R1/R5, applied in T720; review § 1 "fails closed". |
| SEC-T693-03 | tracked-LOW | **fixed** | - | R1 to R3; review § 1 "sound". |
| SEC-T693-04 | tracked-LOW | **fixed** | - | R4 (knowledge part) and R10 (command part, the user's "O1: both fields (Recommended)"). `docs/releases/_template.md:87-88` and `implementation/knowledge/commands/prepare-release.md:59-60` carry `Issued at commit` and `Independent check` (grep). Resolves v4's **(unverified)**. |
| SEC-T693-05 | tracked-LOW | **fixed** | - | R1 to R3; review § 1. |
| SEC-T693-06 | tracked-LOW | **fixed** | - | R6: Release Gate before deployment; review § 1. |
| SEC-T693-07 | tracked-LOW | tracked-LOW | H | Unchanged: accepted by ruling with no edit (plan-127 § Outcome; v3 § 7.2). |
| SEC-T693-08 | tracked-LOW | **fixed** | - | T721: E1-E3 re-pinned with clause pins, 13-mutation proof. |
| SEC-T693-09 | tracked-LOW | **fixed** | - | R1: closed list of fields that may change after the check; residual SEC-T720-04. |
| SEV-T690-03 | tracked-LOW | **fixed** | - | T719 (VS Code wiki labels, completed by the orchestrator). |

**v4 batch E, CWSO hardening (23; plan-129, rows T726 to T728, `security-review-t726-t728-batch-e-v1.md`; CWSO not read)**

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-T694-04 | tracked-LOW | **fixed** | - | T726: `sia-executor.py` takes the secret from a file or the environment only. |
| SEC-T694-05 | tracked-LOW | **fixed** | - | T726: errors name options, never values or paths. Residual SEC-T726-01, -02. |
| SEC-T694-06 | tracked-LOW | **fixed** | - | T726: `export --secret-file` needs `--print-secret`, refuses a terminal. |
| SEC-T694-07 | tracked-LOW | **fixed** | - | T726: one secret-file rule in four readers. Residual SEC-T726-03. |
| SEC-T694-08 | tracked-LOW | **fixed** | - | T726: single-quoted `.env` line, backslash refused, mode 600. |
| SEC-T694-09 | tracked-LOW | **fixed** | - | T726: tests (`test_cwso_jwt_secret_source.py`). |
| SEC-T694-10 | tracked-LOW | tracked-LOW | U | Process incident; rule in force (presence checks only); transcripts remain A-15 (plan-129 § Items without code change). |
| SEC-T694-11 | tracked-LOW | **fixed** | - | T726: Docker Engine 29.9.2 and compose v5.6.1 pinned and sha256-checked. Residual TD-T726-02. |
| SEC-T694-12 | tracked-LOW | tracked-LOW | U | User action A-11; none on the CWSO server, other hosts **(unverified)** (plan-129). |
| SEC-T695-03 | tracked-LOW | **fixed** | - | T727 (CWSO MR !218): origin entries validated at load. Residuals SEC-T727-01, -02. |
| SEC-T695-05 | tracked-LOW | **fixed** | - | T728: per-job e2e compose projects. |
| SEC-T695-06 | tracked-LOW | tracked-LOW | U | Process; A-15 (plan-129). |
| SEC-T695-07 | tracked-LOW | **fixed** | - | T727: 32-byte HS256 minimum, also for `-transport http`. |
| SEC-T695-09 | tracked-LOW | **fixed** | - | T728: one Rust toolchain 1.99.1 with `--locked`. |
| SEC-T695-10 | tracked-LOW | **fixed** | - | T727: loopback by default, opt-in `CWSO_HTTP_PUBLISH_ADDR`. Residuals SEC-T727-03 to -05; user action A-16. |
| SEC-T696-01 | tracked-LOW | **fixed** | - | T728 (row T728). |
| SEC-T696-02 | tracked-LOW | **fixed** | - | T728. |
| SEC-T696-03 | tracked-LOW | **fixed** | - | T728: Debian trixie and Alpine 3.24, blocking Trivy 0.76.0 scan. Residual SEC-T728-01, TD-T728-02. |
| SEC-T696-04 | tracked-LOW | **fixed** | - | T728: 33 references pinned by digest, `check:image-pins`. Residual SEC-T728-02. Digest-to-tag match **(unverified)** (review § 4). |
| SEC-T696-05 | tracked-LOW | **fixed** | - | T728: `go.sum` required. |
| SEC-T696-06 | tracked-LOW | **fixed** | - | T728: arrow/parquet 60.0.0 remove `paste`; the review due 2027-01-31 is closed. |
| SEC-T696-07 | tracked-LOW | tracked-LOW (narrowed) | M | (a) fixed by T728 (wasmtime feature pin test; residual SEC-T728-03); **(b) no fuel or epoch interruption stays**, trigger "before untrusted modules are accepted" (v3). |
| SEC-T699-04 | tracked-LOW | **fixed** | - | Decided by the user, 2026-11-02: "Tie to the bearer (Recommended)"; conditions in plan-129 § Items without code change (section 6.1, TD-T697-07). |

**v4 batch F and U (4)**

| Id | v4 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-011 | tracked-LOW | tracked-LOW | F | Unchanged; `implementation/runtime/security/poc_scan.py` still holds 6 `.match(` calls (grep count). |
| SEC-T674-06 | tracked-LOW | tracked-LOW | F | Unchanged; no `submodule` in `implementation/runtime/security/git_executor.py` (grep). |
| SEC-T658-02 | tracked-LOW | tracked-LOW | U | Live checks not run (A-7). |
| TD-T697-03 | tracked-LOW | tracked-LOW | U | Live-check cases still open (A-2). |

### 2.3 v4 `accepted` (45)

All unchanged; basis as in v3 § 7 and v4 § 2.3 / § 3.4. The MEDIUM ones are marked; ADR-011 applies to them at the next release (section 6.2).

| Id | v4 | now | Evidence or reason |
|---|---|---|---|
| K-2b | accepted | accepted | Unchanged ("D-6 a"). |
| TD-T687-01 | accepted | accepted | Unchanged ("D2 b"). |
| SEC-014 | accepted | accepted | Unchanged ("D-7 b"). |
| RO621-N-1 | accepted | accepted | Unchanged ("D-5"). |
| TD-T671-FN2 | accepted | accepted | Unchanged ("D-8 accept"). |
| SEC-T657-01 / SEC-T658-01 | accepted (MEDIUM) | accepted | Unchanged (one id, as in v2 to v4). ADR-011: needs the user's new acceptance at the next release that ships it. |
| SEC-T660-01 | accepted (MEDIUM) | accepted | Unchanged ("mitigated, not closed"). ADR-011: same. |
| SEC-T657-04 | accepted | accepted | Unchanged. |
| K-15 | accepted | accepted | Unchanged. |
| SEC-T660-05 | accepted | accepted | Unchanged. |
| SEC-T650-03 | accepted | accepted | Unchanged. |
| T636-L6 | accepted | accepted | Unchanged. |
| T636-L7 | accepted | accepted | Unchanged. |
| TD-T671-K7 | accepted | accepted | Unchanged. |
| R-1 | accepted | accepted | Unchanged; who accepted it still **(unverified)**. |
| K-4 limits | accepted | accepted | Unchanged. |
| CR619-N5 | accepted | accepted | Unchanged. |
| K-10 | accepted | accepted | Unchanged; its D-T710-2 part is fixed by T716. |
| GOLDEN_VERSION_LABEL | accepted | accepted | Unchanged. |
| T638-L-1 | accepted | accepted | Unchanged. |
| K-13 | accepted | accepted | Unchanged. |
| K-19 | accepted | accepted | Unchanged. |
| RO621-N-4 | accepted | accepted | Unchanged. |
| RO621-N-5 | accepted | accepted | Unchanged. |
| RO621-O1b | accepted | accepted | Unchanged. |
| RO621-O5c | accepted | accepted | Unchanged. |
| TL-T649-09 | accepted | accepted | Unchanged. |
| SIGNOFF-CR649 | accepted | accepted | Unchanged. |
| K-14 | accepted | accepted | Unchanged. |
| K-21 | accepted | accepted | Unchanged. |
| SEC-T662-05 | accepted | accepted | Unchanged. |
| SEC-T667-03 | accepted | accepted | Unchanged. |
| SEC-T667-06 | accepted | accepted | Unchanged. |
| SEC-T665-01 | accepted (MEDIUM) | accepted | Unchanged. ADR-011: needs the user's new acceptance at the next release that ships it. |
| SEC-T686-05 | accepted | accepted | Unchanged. |
| TD-T697-01 | accepted | accepted | Unchanged. |
| TD-T697-02 | accepted | accepted | Unchanged. |
| TD-T697-07 | accepted (MEDIUM) | accepted | **Re-based** by the user's "Tie to the bearer (Recommended)" (2026-11-02, SEC-T699-04): stays MEDIUM; ends when the current CWSO bearer token expires (**2027-01-29**); renewed by the user with each new token; ends at once if CWSO becomes reachable from outside the LAN, if the token's role widens beyond orchestrator, or if a token leak is suspected (plan-129 § Items without code change). |
| SEC-T702-01 | accepted | accepted | Unchanged; acceptance v3, to 2027-01-30. |
| SEC-T702-02 | accepted | accepted | Same. |
| SEC-T702-03 | accepted | accepted | Same. |
| SEC-T702-04 | accepted | accepted | Same. |
| SEC-T702-05 | accepted | accepted | Same. |
| SEC-T702-06 | accepted | accepted | Same. |
| SEC-T702-09 | accepted (MEDIUM) | accepted | Unchanged; acceptance v3 until 2027-01-30 or the first Brave release above 2.1.4. ADR-011: the release-level acceptance ("Ship with it accepted (Recommended)") covered v9.0.0 only; the next release that ships it needs a new one. |

### 2.4 One v4 `fixed` id re-recorded

| Id | v4 | now | Evidence |
|---|---|---|---|
| SEC-T689-02 | fixed (in part; rest carried by SEC-T701-01) | fixed | T714 § Disposition: "SEC-T689-02 (rest) closed". |

## 3. New ids

Columns: Id | Grade | Location | Short description | Status | Owner | Batch. Line numbers are the reviewers'; they were not re-read unless stated.

### 3.1 `security-review-t714-batch-c-v1.md` (T714, batch C)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T714-01 | MEDIUM | `executor.py` `CHILD_ENV_NAMES` | The allowlist silently dropped package-index settings (fallback to the public index) and the dotnet telemetry opt-out. | fixed (`5fa9629c`; `PackageIndexSettingsTests`, mutation proof) | - | - |
| SEC-T714-02 | LOW | `validation.py:106-126` | `validate_allowed_root` trusts `$HOME`; empty or overridden `HOME`, broad non-ancestors accepted. | tracked-LOW | devops-engineer | K |
| SEC-T714-03 | LOW | `poc_audit_server.py:92` | PoC server's `--allowed-root` lacked the broad-root check. | fixed (`7a7c6b8b`; `BroadAllowedRootTests`) | - | - |
| SEC-T714-04 | LOW | `validation.py:33-37` | Sensitive-name list misses further credential files and MCP configs. | tracked-LOW | devops-engineer | K |
| SEC-T714-05 | LOW | `check-gitlab-token.py:13`; `PREREQUISITES.md` step 6 | Docstring said every warning means exit 1. | fixed (`b26f6ebe`) | - | - |
| SEC-T714-06 | LOW (info) | `executor.py` | Proxy URLs may carry credentials; tool output reaches the agent verbatim. | tracked-LOW | devops-engineer | K |
| SEC-T714-07 | LOW | `PREREQUISITES.md:213` | Two different "step 3" references. | fixed (`b26f6ebe`) | - | - |
| SEC-T714-08 | LOW | `executor.py` `_PIP_INDEX_RE`, `CHILD_ENV_NAMES` | pip hardening settings made in the environment are dropped without the guard noticing. | tracked-LOW | devops-engineer | K |

### 3.2 `security-review-t715-t716-batch-b-v1.md` (T715, T716, batch B; all LOW, owner devops-engineer)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T715-01 | LOW | `verify-release-docs.py:134, 357-366` | Pointer forms without the keywords pass unchecked. | tracked-LOW (trigger: before the next release that changes the `install.sh` pointers) | devops-engineer | G |
| SEC-T715-02 | LOW | `verify-release-docs.py:352-353`; `install.sh` Cursor advice | A prose pointer on a Cursor line is checked only for existence. | tracked-LOW (same trigger) | devops-engineer | G |
| SEC-T715-03 | LOW | `verify-release-docs.py:386-414` | An anchor inside a raw HTML block still counts. | tracked-LOW | devops-engineer | G |
| SEC-T715-04 | LOW | `verify-release-docs.py:427-430, 221` | An `install.sh` line is printed into the CI log without stripping control or bidi characters. | tracked-LOW | devops-engineer | G |
| SEC-T716-01 | LOW | `check-main-develop-drift.py:50-51, 146-147`; `.gitlab-ci.yml:208-209` | `origin/main`/`origin/develop` resolved by short name; a same-named tag shadows the branch (false FAIL blocks a release). | tracked-LOW; **do first** (review: "recommended first"; trigger: before the next release that changes the drift job) | devops-engineer | G |
| SEC-T716-02 | LOW | `publish-release.py:76-80, 326-328` | Category test depends on the Python's Unicode version. | tracked-LOW (at the latest when the release image changes) | devops-engineer | G |
| SEC-T716-03 | LOW | `publish-release.py:417-446` | Bare URLs and GitLab references in a subject still render as links in `CHANGELOG.md`. | tracked-LOW | devops-engineer | G |
| SEC-T716-04 | LOW | `publish-release.py:532-539` | `ApiCredential` is a NamedTuple; tuple, `_asdict`, pickling expose the token (no code path uses them). | tracked-LOW | devops-engineer | G |
| SEC-T716-05 | LOW | `tests/functional/test_publish_release_t716.py` | The CommonMark test skips silently without markdown-it-py; CI install **(unverified)**. | tracked-LOW | devops-engineer | G |

### 3.3 plan-126 § Outcome, Added scope (T717 gaps)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| T717-D1 | gap (ungraded) | `check-release-tag-tree.py` docstring | Gap found by T717. | fixed (T716, "tag-tree docstring") | - | - |
| T717-D2 | gap (ungraded) | `verify-release-docs.py` `Latest release:` marker | Marker not matched as a whole token. | fixed (T715; review § 1 "Correct") | - | - |
| T717-D3 | gap (ungraded) | `publish-release.py` previous-tag sort | Previous tag not sorted semantically. | fixed (T716; review § 2 "correct, with no finding") | - | - |

### 3.4 `security-review-t718-t720-batch-d-v1.md` (T718 to T720, batch D; owner orchestrator, who routes each)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T720-01 | MEDIUM | `validation-gates/SKILL.md`, `release-workflow/SKILL.md` | Carried user acceptances were not a Release Gate input. | fixed (`06a48087`, the reviewer's four texts; re-check PASS) | - | - |
| SEC-T720-02 | LOW | `validation-gates/SKILL.md:70` (A1); `security-engineer.md:86` (A12) | Acceptance record names neither the release asked about nor ties the remediation plan to the one shown to the user. | tracked-LOW (changes ADR-011 row text: superseding ADR or the user) | orchestrator; solution-architect | H |
| SEC-T720-03 | LOW | `release-manager.md:183` (A8) | Conditions template lacks slots for date, grade, release, plan owner and fix. Fails closed. | tracked-LOW (same route as -02) | orchestrator; solution-architect | H |
| SEC-T720-04 | LOW | `release-manager.md:46` (R1) | "What you add below the field list" can be read as open-ended. | tracked-LOW (knowledge edit plus re-pin) | technical-writer; devops-engineer (pin) | H |
| SEC-T720-05 | LOW | `orchestrator.md:262` (R6) | Deployment after a CONDITIONAL_PASS does not repeat the item 2 acceptance record. | tracked-LOW (knowledge edit plus re-pin) | technical-writer; devops-engineer (pin) | H |
| SEC-T720-06 | LOW | `release-workflow/SKILL.md:171, 232` (R8) | Hotfix eligibility names only CRITICAL and HIGH. | tracked-LOW | technical-writer | H |
| SEC-T720-07 | LOW | `validation-gates/SKILL.md:70` (heading) | Heading "never qualify for CONDITIONAL_PASS" contradicts the medium rule in the body. Fails closed. | tracked-LOW | technical-writer | H |
| SEC-T720-08 | LOW | `release-manager.md:46` (R1); `orchestrator.md:218` (R3) | The independent checker need not differ from the author of the release files. | tracked-LOW (knowledge edit plus re-pin) | technical-writer; devops-engineer (pin) | H |

### 3.5 plan-127 § Outcome

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| TD-T720-01 | LOW | `release-workflow/SKILL.md` "No critical or high bugs", "Confirm the issue is critical" (now lines 117 and 171, grep; the plan cites 116 and 170) | Two lines name no severity scale (R8 closed the same gap elsewhere). | tracked-LOW | technical-writer | H |

### 3.6 `security-review-t722-t725-batch-a-v1.md` (T722 to T725, batch A)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T722-01 | LOW | `sync.mjs:1071, 918-921` | A dangling link's text is still resolved lexically (`sym/../y`). Needs a crafted authoring tree. | tracked-LOW | devops-engineer | I |
| SEC-T722-02 | LOW | `sync.mjs:1043, 1053, 1079`; `test_sync_symlink_hop_limit.py:44` | Off by one: 39 hops resolve, comment says 40; boundary not pinned. Fails closed. | tracked-LOW | devops-engineer | I |
| SEC-T722-03 | LOW | `sync.mjs:654-662` | Drop step compares the exact key: an unknown or case-variant token survives and becomes a Copilot grant; object-form `tools` maps not filtered. | tracked-LOW; **do first** (plan-130) | devops-engineer | I |
| SEC-T722-04 | LOW | `context_retriever.py:99, 103`; `server.py:133` | Error for an unrecognised remote contains the raw remote URL (may hold userinfo); traceback at startup. | tracked-LOW | devops-engineer | I |
| SEC-T722-05 | LOW | `sync.mjs:979-984, 1089-1105` | The MCP output allowlist is lexical; a symlinked `.vscode` writes outside ROOT. | tracked-LOW | devops-engineer | I |
| SEC-T724-01 | LOW | `merge-mcp-json.py:114, 131, 457` | `GENERATED_REF` is the same for every platform; some edited entries get no "differs" note. | tracked-LOW | backend-developer | I |
| SEC-T725-01 | LOW | `install.sh:1526-1536` | Through a bind mount, `withhold_authoring_only` can delete `prepare-release` from the source mirror. Contrived. | tracked-LOW | devops-engineer | I |
| SEC-T725-02 | LOW | `install.sh:1492-1509` | Any safe relative path is accepted in `authoringOnly`; a missing key or manifest reads as empty, so the filter fails open. | tracked-LOW; **do first** (plan-130) | devops-engineer | I |
| SEC-T725-03 | LOW | `install.sh:1483-1485` | `-f` follows symlinks; a link under `implementation/` can switch the filter off (commands are kept). | tracked-LOW | devops-engineer | I |

### 3.7 plan-128 § Outcome

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| TD-T723-01 | LOW | `docs/releases/v9.0.0.md` | Cites `install.sh:1300`; the advice now starts near line 1297 and spans four lines. The published document stays unchanged. | tracked-LOW (the next release document cites the current lines) | release-manager | G |
| TD-T724-01 | LOW | `merge-mcp-json.py` | Any literal value in a generated `env` block (for example the `gitlab` permission mode) reads as hand-edited; matters only if `gitlab` is retired. | tracked-LOW | backend-developer | I |
| TD-T725-01 | LOW | `commands/validate-tasks.md`, `commands/validate-workflow.md`, `skills/testing-strategy/SKILL.md`, `skills/release-workflow/SKILL.md` | Knowledge that ships to targets still names `/prepare-release`, which targets no longer receive (grep: all four still name it). | tracked-LOW; due with the next release (T725 migration item) | technical-writer | H |

### 3.8 `security-review-t726-t728-batch-e-v1.md` (T726 to T728, batch E; all LOW, owner devops-engineer)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T726-01 | LOW | `scripts/cwso-deploy-helper.sh:218-222` | `reject_argument` prints a bare `-`-prefixed token in full; a secret passed bare would be printed. | tracked-LOW | devops-engineer | L |
| SEC-T726-02 | LOW | `sia-executor.py:835`; `mint-cwso-jwt.py` | `Path.is_file()` outside the `try`; a `PermissionError` traceback may print the path. | tracked-LOW | devops-engineer | L |
| SEC-T726-03 | LOW | the four readers; `docker-compose-t226.yml:177`; CWSO `config.go:127-128` | One-rule guarantee holds only for tested layouts; Unicode whitespace differs. Effect: auth failure, not disclosure. | tracked-LOW | devops-engineer | L |
| SEC-T727-01 | LOW | CWSO `transport/http.go:667, 683-697` | Without `Origin`, the Host check splits at the first `:`; any IPv6 Host passes. The JWT still applies. | tracked-LOW; **do first** (plan-130) | devops-engineer (CWSO) | M |
| SEC-T727-02 | LOW | CWSO `config/http_security.go:69` | The origin rejection message quotes an entry with userinfo, so its password reaches the logs. | tracked-LOW; **do first** (plan-130) | devops-engineer (CWSO) | M |
| SEC-T727-03 | LOW | CWSO `scripts/phase2-integration.py:35-39` | The CI override is chosen by the generic `CI` variable; a developer machine with it set publishes on all interfaces. | tracked-LOW | devops-engineer (CWSO) | M |
| SEC-T727-04 | LOW | CWSO `deploy/docker-compose.yml:272`; `docs/user/README.md` | Before Docker Engine 28, same-L2 hosts could reach loopback-published ports; the user's Engine version **(unverified)**. | tracked-LOW | devops-engineer (CWSO) | M |
| SEC-T727-05 | LOW | CWSO `deploy/docker-compose.yml:472-473` | Pre-existing: the opt-in `rollout` service publishes on all interfaces. | tracked-LOW | devops-engineer (CWSO) | M |
| SEC-T728-01 | LOW | CWSO `.gitlab-ci.yml:269-296, 504-536` | The image scan does not gate `deploy:registry`, which rebuilds instead of pushing the scanned images; tag pipelines not scanned. | tracked-LOW; **do first** (plan-130) | devops-engineer (CWSO) | M |
| SEC-T728-02 | LOW | CWSO `config/config.go:154`; `scripts/check-image-pins.sh:24-39` | Sandbox default image unpinned and end-of-life; the pin guard misses several reference forms. | tracked-LOW | devops-engineer (CWSO) | M |
| SEC-T728-03 | LOW | CWSO `services/cwso-sparse/tests/wasmtime_features.rs:96-120` | The test checks declared, not resolved, wasmtime features. | tracked-LOW | devops-engineer (CWSO) | M |

### 3.9 plan-129 § Outcome

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| TD-T726-01 | LOW | `implementation/scripts/dispatch-test-sia.py` | Still accepts `--jwt-secret` on argv (grep: lines 18, 571). | tracked-LOW | devops-engineer | L |
| TD-T726-02 | LOW | `scripts/deploy/cwso-proxmox-setup.sh` | The default Proxmox template is Ubuntu 20.04; whether Docker Engine 29.9.2 is packaged for it **(unverified)**. | tracked-LOW | devops-engineer | L |
| TD-T728-01 | LOW | CWSO release binaries | Rust release binaries now need glibc 2.41; belongs in the next CWSO release notes. | tracked-LOW | devops-engineer (CWSO) | M |
| TD-T728-02 | LOW | CWSO `security:image-scan` | Trivy 0.76.1 (eMudhra CA mitigation) adoptable from **2026-11-04**; a Go 1.26 backport of the CA fix **(unverified)**. | tracked-LOW | devops-engineer (CWSO) | M |
| TD-T728-03 | LOW | CWSO CI `docker:27.5.1` | Out of support; an upgrade needs the runner daemon's version first. | tracked-LOW | devops-engineer (CWSO) | M |

## 4. Decisions since v4

### 4.1 The user's (words verbatim as recorded)

| Date | Words | Effect | Source |
|---|---|---|---|
| 2026-11-01 | "B go" | plan-126 (T715 to T717) | `plan-126-batch-b-release-tooling.md` Based on |
| 2026-11-01 | "D go" | plan-127 (T718 to T721) | `plan-127-batch-d-knowledge-and-rulings.md` Based on |
| 2026-11-01 | TD-T713-01: "(a) Time-bound acceptance (Recommended)"; end date: "Until the next release" | **ADR-011 Accepted**: a `SECURITY:MEDIUM` ships only under the user's verbatim, dated acceptance for that one release, with a remediation plan; no time-based maximum; renewed at each release that ships the finding. TD-T713-01 fixed | ADR-011 Status; plan-127 § Outcome; `rulings-batch-d-v1.md` § 5 |
| 2026-11-01 | SEC-T693-04 command part: "O1: both fields (Recommended)" | R10: the published verdict records `Issued at commit` and `Independent check`. SEC-T693-04 fixed | same; `rulings-batch-d-v1.md` § 1.5 |
| 2026-11-01 | "Yes, refresh now (Recommended)" | **Root refresh 23**: the 58 paths declared by T719, T720 and the SEC-T720-01 fix; drift emptied | `tests/_baselines/root-install-drift.json` `_comment` |
| 2026-11-02 | "A go" | plan-128 (T722 to T725) | `plan-128-batch-a-installer-generator.md` Based on |
| 2026-11-02 | "Yes, refresh now (Recommended)" | **Root refresh 24**: the 12 paths declared by T722 and T725; the root stays an authoring checkout and keeps `/prepare-release`; drift emptied (`drift` list empty on `0ae07c0f`) | same |
| 2026-11-02 | "E go" | plan-129 (T726 to T728) | `plan-129-batch-e-cwso-hardening.md` Based on |
| 2026-11-02 | SEC-T699-04: "Tie to the bearer (Recommended)" | TD-T697-07 re-based (section 2.3); SEC-T699-04 fixed | plan-129 Based on and § Items without code change |
| 2026-11-02 | "v5 go" | plan-130, T729 (this register) | `plan-130-tracked-debt-register-v5.md` Based on |

The user's earlier decision D-T700-1 "Exclude docs/decisions/ (Recommended)" (v4 § 4.1) is the reason TL-T708-07 was left unchanged (row T715).

### 4.2 Other decisions (not the user's)

| Id | Decision | By | Effect |
|---|---|---|---|
| R1 to R9 | Release-gate wording and severity-scale rulings | solution-architect (T718) | SEC-T693-02, -03, -05, -06, -09, TD-T687-02 to -04 fixed (applied in T720) |
| A1 to A13 | ADR-011 rows applied | technical-writer (T720) | TD-T713-01 fixed in the knowledge |
| SEC-T693-07 | Residual accepted by ruling, no edit | plan-127 | stays tracked-LOW |
| TD-T671-legacy re-read | P4, P7 obsolete; P9, P11, P12 fixed; P10 open; P14, P15, T539, T565 parked | orchestrator (plan-127) | narrowed (2.1) |
| SEC-T663-02 | Not done in batch A; needs its own task | devops-engineer, orchestrator (plan-128) | own item J |
| SEC-T694-10, SEC-T695-06, SEC-T694-12 | Process rule and user actions, no code change | orchestrator (plan-129) | stay tracked (U) |

## 5. Open items by LOW batch

v4's batches A to E are executed. The open items are regrouped here. "Do first" marks the items named in plan-130 and `task-T729.md`; of these only SEC-T716-01 carries the words "recommended first" in its review artifact; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag is not in the review artifacts I read **(unverified source: the reviewers' reports as relayed by the orchestrator)**.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| G | Release tooling and CI (emage.code) | **SEC-T716-01 (do first)**, SEC-T716-02 to -05, SEC-T715-01 to -04, SEC-T677-01, SEC-T676-14, SEC-T702-08, TL-T708-07, TD-T723-01 | 14 | devops-engineer; release-manager (TD-T723-01); the user files or declines the upstream report (SEC-T702-08) | **before the next release** (SEC-T716-01; SEC-T715-01/-02 if the `install.sh` pointers change; TD-T723-01 in the next release document); SEC-T676-14 at the next lock regeneration |
| H | Release-gate knowledge text and ADR-011 follow-ups | SEC-T720-02 to -08, TD-T720-01, TD-T725-01, TD-T671-legacy (P10; parked P14, P15, T539, T565), SEC-T693-07 | 11 | orchestrator routes; solution-architect or the user (SEC-T720-02, -03: superseding ADR); technical-writer; devops-engineer (re-pins of `test_release_self_review_text.py`) | before the next release for SEC-T720-02 to -05, -08 and TD-T725-01 (they shape that release's gate and migration note); the parked TD-T671-legacy items need a protected-path grant |
| I | Installer and generator | **SEC-T722-03 (do first)**, **SEC-T725-02 (do first)**, SEC-T722-01, -02, -04, -05, SEC-T725-01, -03, SEC-T724-01, TD-T724-01 | 10 | devops-engineer; backend-developer (SEC-T724-01, TD-T724-01) | next installer or generator change; SEC-T725-02 before the release that ships T725 (recommendation) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | devops-engineer | its own task (five test files, documents and live evidence change; plan-128) |
| K | Security runtime (`security-audit` servers) | SEC-T714-02, -04, -06, -08, SEV-T690-02 (pinned runtime package), SEV-T690-04 ((d) Copilot), SEC-T665-07 (if reopened) | 7 | devops-engineer; technical-writer (wiki residual of SEC-T714-06) | next change to `implementation/runtime/security/`; SEC-T665-07 on its reopening conditions |
| L | CWSO helper scripts in emage.code | SEC-T726-01 to -03, TD-T726-01, TD-T726-02 | 5 | devops-engineer | next change to the CWSO helper scripts; TD-T726-02 before the next Proxmox setup |
| M | CWSO repository | **SEC-T728-01 (do first)**, **SEC-T727-01, -02 (do first)**, SEC-T727-03 to -05, SEC-T728-02, -03, TD-T728-01 to -03, SEC-T696-07 ((b) fuel/epoch) | 12 | devops-engineer (CWSO; agent branch from CWSO `origin/develop`, MR into CWSO `develop`) | next CWSO change; TD-T728-02 from **2026-11-04**; TD-T728-01 in the next CWSO release notes; SEC-T696-07(b) before untrusted modules are accepted |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 68 = 67 tracked-LOW + 1 open. No open item is above LOW.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

ADR-011 applies: "An acceptance covers only the release it was given for", and "at the next release that ships the finding, the finding blocks again until it is fixed or the user accepts it again for that release". The pin-audit acceptance v3 and the per-advisory audit acceptances are separate time-bound mechanisms that ADR-011 leaves unchanged (ADR-011 § Decision).

| Item | Grade | Words, date | Until |
|---|---|---|---|
| SEC-T702-09 (with SEC-T702-01 to -06) | MEDIUM | "Renew + force stdio (Recommended)" (acceptance v3); "Ship with it accepted (Recommended)", 2026-11-01 (v9.0.0 only) | pin audit: **2027-01-30 or the first Brave release above 2.1.4**; release: **the next release needs the user's new acceptance** (ADR-011) |
| SEC-T660-01 | MEDIUM | as in v3 § 7.1; shipped in v8.0.0 and v9.0.0 | **the next release needs the user's new acceptance** (ADR-011) |
| SEC-T665-01 | MEDIUM | as in v3 § 7.1 | same |
| SEC-T657-01/SEC-T658-01 (remainder) | MEDIUM | as in v3 § 7.1 | same |
| TD-T697-07 | MEDIUM | "C", 2026-10-31; re-based by "Tie to the bearer (Recommended)", 2026-11-02 | **2027-01-29** (expiry of the current CWSO bearer token); renewed by the user with each new token; ends at once on external reachability, a wider token role or a suspected leak. A deployment acceptance, not a release-shipped finding |
| Every other accepted id of section 2.3 | LOW/INFO | as in v3 §§ 7.1, 7.2 | unchanged |

The v9.0.0 `## RELEASE VERDICT` records a user acceptance for SEC-T702-09 only and cites SEC-T660-01 as the v8.0.0 precedent; SEC-T665-01 and SEC-T657-01/SEC-T658-01 are not named in it (grep on `docs/releases/v9.0.0.md`). ADR-011 § Alternatives lists all four as needing "a new acceptance at the next release that ships it", so the next verdict names each of them explicitly.

### 6.2 Next release checklist

1. **Migration item T725 (TD-T671-P5)** in the release document: authoring-only commands are no longer installed into target projects; commands declare `audience: authoring | target | both`; today only `/prepare-release` (five platform paths listed in plan-128 § Outcome); `--update`/`--projections-only` deletes an existing copy (a dry run prints the `rm`); an authoring checkout (`implementation/registry/index.json`) keeps them; a target that used `/prepare-release` keeps its own copy under another file name; `.generated-manifest.json` gains `authoringOnly`; the generator refuses a command without a valid `audience:`. Fix TD-T725-01 with it.
2. **ADR-011 re-acceptances**: the Release Gate input lists every MEDIUM an earlier release shipped under the user's acceptance and not yet fixed (SEC-T720-01 fix, `validation-gates/SKILL.md`): **SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09**. Each one is fixed, or the user accepts it again for this release, verbatim and dated, with its remediation plan (owner, fix, deadline). No agent grants or carries one over.
3. **New verdict fields** (R4, R10): `Issued at commit` and `Independent check` (`docs/releases/_template.md:87-88`; `prepare-release.md:59-60`). The independent check row must be present, current and not FAIL (SEC-T693-02).
4. **Release tooling before the tag**: SEC-T716-01 (batch G, do first); SEC-T715-01/-02 if the `install.sh` pointers change; the release document cites current `install.sh` lines (TD-T723-01).
5. **Batch H items that shape the gate**: SEC-T720-02, -03 (need the user or a superseding ADR), -04, -05, -08, if they are to apply to this release.
6. **Brave**: if the release falls after 2027-01-30 or after a Brave release above 2.1.4, the pin audit needs a new acceptance version or the bump first.
7. **D-T710-2**: confirm in the release job that the `CHANGELOG.md` entry lands below `[Unreleased]` (fixed in code by T716; not yet observed in a tag pipeline).

### 6.3 Dates

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v4 (from checkpoint-039/-040 and the T697-T699 review); I did not re-read them **(unverified)**.

## 7. User actions

| # | Action | State now | Due |
|---|---|---|---|
| A-2 | Remaining T665 live checks (TD-T697-03; design checks 4, 5) | open | - |
| A-7 | Live checks Gemini CLI, Opencode denials, VS Code T690 servers, Pi lists (K-20, SEC-T658-02) | open | - |
| A-10 | On every other install: empty `glab`'s stored login and revoke its OAuth authorization if `GITLAB_TOKEN` is used | open (done on the user's devcontainer, v3) | - |
| A-11 | Remove or recreate any `cwso-sia-executor` container from the old compose definition (SEC-T694-12) | open for other hosts; none on the CWSO server | - |
| A-12 | Optional: replace the CWSO server's local compose override with `CWSO_ALLOWED_ORIGINS` | open, optional; now also subject to the T727 origin checks (A-16) | - |
| A-13 | Renew the GitLab token and the CWSO bearer token; renew the TD-T697-07 acceptance with the new bearer | open | GitLab **2027-01-28**; CWSO bearer **2027-01-29** |
| A-14 | Recheck that the CWSO server runs the merged images after the next CWSO change | **due again**: CWSO develop moved to `6630ecb` (MR !218); do it with A-16 | at the next redeploy |
| A-15 | Optional: purge local session transcripts that hold the dead CWSO secret (SEC-T694-10, SEC-T695-06) | open, optional | - |
| **A-16** (new, plan-129) | **Before the next CWSO redeploy** (`git pull` plus `docker compose up -d`), or the server loses LAN access: set `CWSO_HTTP_PUBLISH_ADDR` to the all-interfaces address in `deploy/.env`, or add a `ports: !override` entry to the local override (exact text in plan-129 § Outcome); make sure the JWT secret is at least 32 bytes; make sure the `CWSO_ALLOWED_ORIGINS` entries pass the new checks. The loopback guarantee needs Docker Engine 28 or later (SEC-T727-04; the user's version **(unverified)**) | open | before the next CWSO redeploy |
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open (unchanged since v4; not re-checked) | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open (same) | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open (same) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- Carried statuses: v4 rows plus plans 125 to 129 (outcome sections), rows T714 to T728, the five batch reviews, the rulings and ADR-011. Greps on `0ae07c0f` where cited (`audience:` in `prepare-release.md`, the Opencode `tools:` map, `poc_scan.py` `.match(` count, `git_executor.py` `submodule`, `dispatch-test-sia.py` `--jwt-secret`, the four TD-T725-01 files, the two TD-T720-01 lines, the verdict template fields, the empty root drift list).
- CWSO statuses come from plan-129, rows T727/T728 and the batch-E review; the CWSO repository was not read.
- **Unverified**: the T547 remark of TD-T671-legacy; the source of the "do first" flags other than SEC-T716-01; whether the user answered the SEC-T702-08 upstream-report offer; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; markdown-it-py in CI (SEC-T716-05); Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates. The reviewers' own unverified lists stand as written in their artifacts.
- Counting: a script reads every table row of sections 2 and 3 and counts ids per status; it gives 500 ids, 381 fixed (373 carried plus 8 new), 45 accepted, 6 obsolete (v4 record), 1 open, 67 tracked-LOW, and 68 ids in section 5.
- Validators run before commit: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v4.md` (and v1 to v3 for descriptions); plans 125 to 130; `docs/tasks/task-T729.md`; `completed-tasks.md` rows T714 to T728; the artifacts listed under "Based on". Decision IDs: ADR-011, ADR-007, ADR-008, DEC-T681-1, D-T700-1.
