# Artifact: tracked-debt-register-v26.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v25.md` (740 ids; v25 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/artifacts/tracked-debt-register-v17.md` (the post-release form of section 6); `docs/plans/plan-183-tracked-debt-register-v26.md` (§ User decision, § Facts since v25, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T882.md` (the user's "v26 go"); `docs/plans/plan-182-next-release.md` (Addenda 1 to 4, Outcome); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`; `docs/releases/v12.0.0.md` (Known Issues, Conditions); the gate artifacts `release-next-audit-v1.md`, `mcp-pin-audit-next-v1.md`, `security-confirmation-t871-sec-t660-t665-v1.md`, `security-review-t881-ci-lock-v1.md`, `qa-gate-release-v12-v1.md`, `tech-lead-release-v12-v1.md`, `security-review-t877-release-v12-v1.md`, `independent-check-t878-v1.md`; `docs/wiki/mcp-pin-bump-checklist.md` (§ 2, § 5). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T882 (plan-183; the user's answer of 2026-11-20, verbatim: "v26 go"). **Date**: 2026-11-20.
- **Tree read**: branch `agent/tech-lead/T882` at `458c17ec` (develop `43b6d3f2` plus the plan-183 commit). The range for "lines added since v25" is `9b9a31f0..458c17ec` (plan-183 § Facts names `9b9a31f0..43b6d3f2`; the one extra commit is plan-183's own plan, brief and ledger row). It includes the release merges (!708, !709) and the closeout (!710): 39 files, 2638 lines added and 22 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range, so the search set outside them is the same 39 files and 2638 added lines (read here).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `458c17ec`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v24 only by grep (and v17 § 2.3, § 6 by line read). Code files were read only as added lines, except `implementation/scripts/sync.mjs` lines 693-699 (`taskMap`). `/tmp/evidence-run` was checked only for existence. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v25.
- **Post-release register.** This register follows v12.0.0 (tag on `514503b0`, an ancestor of `458c17ec`, read here). As v17 did after v11.0.0, section 6 restates the accepted risks for the release that shipped and resets the next-release checklist to "the release after v12.0.0".
- **Batch letters**: **X** loses SEC-T811-05 (fixed) and takes **SEC-T881-02** (my suggestion), so stays 6. **AB** takes **TL-T876-02** (my suggestion), so grows to 3. No new letter.

## 1. Summary

v26 holds **750 ids**: the 740 of v25 and **10 new** (12 ids named; two are counted with another id, section 1.2). After v26: **575 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **116 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 have no reviewer's grade (the orchestrator's ids, called LOW). The MEDIUMs that shipped in v12.0.0 are SEC-T660-01 and SEC-T665-01, **accepted by the user for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v25, from tracked-LOW (1)**: SEC-T811-05 (batch X), the user's runner hardening (section 2.2).
- **New and fixed (6)**: TL-T869-01, SEC-T881-01, QA-T875-01 / SEC-T877-01 (counted as one), QA-T875-02, TL-T876-01, TL-T876-05 (section 3).
- **New and obsolete (2)**: TL-T869-02 (information, no defect), TL-T876-03 (dismissed by the orchestrator, withdrawn by its author) (section 3).
- **New and tracked-LOW (2)**: SEC-T881-02 (batch X), TL-T876-02 (batch AB) (section 3; batches my suggestion).
- **New, counted with an existing id (1)**: TL-T876-04 is SEC-T867-01 (section 1.2, section 2.2).
- **Accepted, qualifier changed (2)**: SEC-T660-01, SEC-T665-01: the v11.0.0 acceptance ended with that release; the user accepted both for v12.0.0 only (section 2.3, section 6.1).
- **Next-release checklist**: reset to "the release after v12.0.0", 33 numbers carried, 2 new (section 6.2). **Dates**: section 6.3. **User actions**: SEC-T811-05 done; K-20 stays; `/tmp/evidence-run` removal optional (section 7).

Arithmetic, from the v25 totals:

| Status | v25 | leaves | enters | v26 |
|---|---:|---|---|---:|
| fixed | 568 | | + 1 tracked-LOW (SEC-T811-05); + 6 new | **575** |
| accepted | 46 | | (SEC-T660-01, SEC-T665-01 stay accepted, now for v12.0.0 only) | **46** |
| obsolete | 10 | | + 2 new (TL-T869-02, TL-T876-03) | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 115 | - 1 fixed | + 2 new (SEC-T881-02, TL-T876-02) | **116** |
| **all** | **740** | | + 10 new ids | **750** |

Check: 575 + 46 + 12 + 1 + 116 = 750. Open or tracked: 116 + 1 = 117, the size of section 5.

### 1.1 Ids by v25 status and status now

| v25 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 115 | 1 | 0 | 0 | 0 | 114 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 568 | 568 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v25 ids** | **740** | **569** | **46** | **10** | **1** | **114** |
| new in v26 | 10 | 6 | 0 | 2 | 0 | 2 |
| **all v26 ids** | **750** | **575** | **46** | **12** | **1** | **116** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `release-next-audit-v1.md` § 6: TL-T869-01, TL-T869-02 | 2 | 1 (-01) | 1 (-02) | 0 |
| `security-review-t881-ci-lock-v1.md`: SEC-T881-01, SEC-T881-02 | 2 | 1 (-01) | 0 | 1 (-02) |
| `qa-gate-release-v12-v1.md` and `security-review-t877-release-v12-v1.md`: QA-T875-01 / SEC-T877-01 (one finding, counted once), QA-T875-02 | 2 | 2 | 0 | 0 |
| `tech-lead-release-v12-v1.md`: TL-T876-01, -02, -03, -05 (TL-T876-04 is SEC-T867-01, not counted again) | 4 | 2 (-01, -05) | 1 (-03) | 1 (-02) |
| **All new** | **10** | **6** | **2** | **2** |

**How the info, dismissed and duplicate ids are treated (precedents).**
- **Duplicates, counted once** (v17 § 1.2 and § 4.2: "QA-T818-01 is TD-T774-01, not counted again"; "TL-T819-01 / SEC-T820-01 (one finding, counted once)"): **TL-T876-04** is SEC-T867-01 (plan-182 § Addendum 4: "the same as SEC-T867-01"; release document Conditions; T876's own text, `--min-age-days 0`), so it adds no id. **SEC-T877-01** is QA-T875-01 (plan-182 § Addendum 4: "SEC-T877-01 (`edit: allow`; the same as QA-T875-01)"; both fixed by one wording change in `e0e3b355`), so the pair is one id in the counts.
- **Info and dismissed, `obsolete`** (v12 § 3: SEC-T775-03, "SECURITY:LOW (info)", **obsolete**; v17 § 2.2: TD-T808-02, **obsolete** "my ruling" when its condition no longer applied). Both ids are minted in a gate artifact, so they are counted, but neither names a defect that remains: **TL-T869-02** records a stale premise in the plan (SEC-T762-04 and TL-T761-10 were already fixed in v16), and **TL-T876-03** was dismissed by the orchestrator and withdrawn by its author (T878 point 1: "My T876 finding missed those two lines"). Neither is `fixed`, because nothing was changed to close it.

**Ids minted in the range beyond the plan's list: none.** A search of the 2638 added lines in `9b9a31f0..458c17ec`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (192 distinct tokens), set against the text of registers v1 to v25, finds as in no register exactly:
- **The plan's list**: TL-T869-01, TL-T869-02, SEC-T881-01, SEC-T881-02, QA-T875-01, QA-T875-02, TL-T876-01 to -05, SEC-T877-01.
- **Labels that are not debt ids**: K-27, K-30, K-31, K-40 to K-43 (the v12.0.0 release document's Known Issues; earlier K numbers are in registers); A-04, A-05, A-07, A-08 (breaking-change labels); B-2 to B-18 except B-1 and B-13 (T869 changelog labels); X-01 to X-12 except X-04, F-01 to F-03 (release-document changelog labels); M-7, M-10 and MI-2, MI-3, MI-5 to MI-7, MI-9 (migration items); C-2, C-5 (gate conditions); GHSA-5648 (a fragment of an advisory id, `mcp-pin-audit-next-v1.md`). Read here: each occurs only in release documents, gate artifacts, the plan or the checkpoint.
- The bare form `QA-T875` (no suffix) occurs only as "QA-T875 C3", a condition of T875, not an id.

**Ids named with no change of status** (in the range; statuses carried and not re-traced id by id **(unverified beyond the grep)**): among others SEC-T702-08, SEC-T702-09 (fixed by the Brave 2.1.5 pin; the release document: "SEC-T702-09 is fixed"), SEC-T735-06, SEC-T735-08, SEC-T735-09, SEC-T741-17, SEC-T756-07, SEC-T762-04, SEC-T768-03, SEC-T786-01, SEC-T786-02, SEC-T840-01, SEC-T842-02, SEC-T856-02, SEC-T856-03, SEC-T860-01, SEC-T860-02, SEC-T867-02, SEC-T658-02, TD-T697-07, TD-T723-01, TD-T774-01, TD-T849-01, TL-T761-10, TL-T780-09, TL-T819-03, TL-T821-01, QA-T818-01, -03, -04, K-20. **Ids named with a change** are those of sections 2 and 3. This register mints no id.

## 2. v25 ids re-checked

Every v25 `open`, `tracked-LOW` and `accepted` id (162) is covered: the changed ones have a row here, the rest are unchanged and carried. The v25 `fixed` and `obsolete` ids stay as v25 records them.

### 2.1 v25 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check; the release document carries it as K-20 ("A one-time manual check after updating is advised (user action A-7)").

### 2.2 v25 `tracked-LOW` (115)

**Changed to fixed (1).**

| Id | v25 | now | Evidence and remainder |
|---|---|---|---|
| SEC-T811-05 | tracked-LOW, batch X; `SECURITY:LOW` (A05): `allowed_services` unset; container-escape surface (v17 § 3) | **fixed** | Checklist § 5, row of 2026-11-19 (read here): the user, on the release-gate runner, `gitlab-runner --version` 19.5.3; `services_limit = 0` added to `[runners.docker]`; `gitlab-runner lint --config /etc/gitlab-runner/config.toml`: "Configuration file is valid." (exit 0) before the restart; restart; the `journalctl` grep for services, unknown, unsupported, deprecated or invalid: "no line". The probe (pipeline 3090926673) and then tag pipeline 3092574856 ran on the hardened runner, all three tag jobs, `release` included, on runner #59129270 (checkpoint-044 step 4; plan-182 § Outcome; not re-observed here). That closes the finding's services half and records steps (a) to (e) of checklist § 3. **Remainder, not a new id**: the container-escape half is the recurring patching rule of checklist § 3 (record Docker Engine, GitLab Runner and kernel versions at each CI image review; out-of-cycle patching), which no one-time action can close; the 2026-11-19 row records only the runner version, so it moves to section 6.2 as a rule (item 44). "Nothing else in that LXC" is not recorded **(unverified)**. The § 5 row still ends "Not yet observed: a tag pipeline on the hardened runner", written before T874 and the tag; checkpoint-044 now records it, the checklist row was not updated (read here; a record gap, not a finding) |

**Tracked-LOW with a changed note (2).**

| Id | Batch | Changed note | Source |
|---|---|---|---|
| SEC-T867-01 | X | **TL-T876-04 is the same finding** and is counted with it (section 1.2). T876 adds: "only the checklist's fixed command guards it"; fix as T867 (a floor of 7, or `--allow-young` below it) | `tech-lead-release-v12-v1.md` row TL-T876-04; plan-182 § Addendum 4 |
| SEC-T867-02 | X | **TL-T876-04's second half joins this remainder**: `age` prints the publication date in the stamp's own offset while it computes the age from the UTC date; print the UTC date with the fix of the calendar-day count. The surface and owner are SEC-T867-02's, so no separate id | `tech-lead-release-v12-v1.md` row TL-T876-04 ("print the UTC date"); my ruling |

**Unchanged (112 tracked-LOW; v25 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 3 (SEC-T756-02, SEC-T768-04, TL-T761-11), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 2 (SEC-T856-02, SEC-T867-03). 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 3 + 11 + 2 + 5 + 2 = 112; with the 2 changed-note ids, 114 carried; with the 2 new, 116 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v25 and not recounted id by id here; X and AB were traced from v25 § 5.)

**Batch Q in v12.0.0, unchanged.** T869 § 5 routed all five members (TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01) for this release, and the gates record the routes applied (T876 re-read the `install.sh` lines and checked the migration items by hand; the Conditions lines attribute the swap and hibernation clause to T871). Each is a per-release duty that recurs (T869 § 5: TD-T723-01 "Stays tracked (recurs)", SEC-T735-08 "Stays tracked"; items 4, 10, 43), and no source in the range changes a status, so all five stay tracked-LOW in Q, as v17 left them after v11.0.0.

### 2.3 v25 `accepted` (46)

**Qualifier changed (2), unchanged (44).**

| Id | v25 | now | What the sources record |
|---|---|---|---|
| SEC-T660-01 | accepted MEDIUM, for v11.0.0 only; review 2027-01-28 | **accepted MEDIUM, for v12.0.0 only (shipped)** | The v11.0.0 acceptance ended with that release (v17 § 6.1; item 43). T871 (`security-confirmation-t871-sec-t660-t665-v1.md`), the Security Engineer's new review for v12.0.0, came before the question (ADR-016). The user, 2026-11-19, question dialog: **"Accept for v12.0.0 (Recommended)"** (`docs/releases/v12.0.0.md:285`, Conditions; K-16 at `:184`; plan-182 § Addendum 2). Plan as shown: owner the user (isolation) and devops-engineer (documentation); fix: none possible in the harness; the question stated item 49's Opencode scope. The deadline 2027-01-28 was ahead at the tag (UTC date 2026-11-20, checkpoint-044). **Left**: the review on **2027-01-28** (ADR-015 O3, W1), and a fix or a new acceptance before the next release that ships it (item 43) |
| SEC-T665-01 | as SEC-T660-01 | **accepted MEDIUM, for v12.0.0 only (shipped)** | As SEC-T660-01, the same question and answer (`docs/releases/v12.0.0.md:286`); the Conditions line attributes the swap and hibernation clause to T871 (TL-T821-01's route) |

**Unchanged (44)**, with their v25 qualifiers: TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29; the release document does not list it as accepted, T869 § 7); the 40 LOW or INFO ids listed in v13 § 2.3; the orchestrator-accepted residues TL-T773-01, TL-T780-01, TL-T780-07. 1 + 40 + 3 = 44; with the 2 rows of changed qualifier, 46.

## 3. New ids

Grades are the reviewers' own.

| Id | Grade | Short description | Status | Evidence and remediation | Batch |
|---|---|---|---|---|---|
| TL-T869-01 | LOW (T869) | `server-filesystem@2.4.0` declares `engines.node >=24`; `PREREQUISITES.md` supported Node 22 | **fixed** (T880) | T869's route: the orchestrator decides between a PREREQUISITES/document note and nothing. T880 wrote the note: `implementation/PREREQUISITES.md:4`, "**Exception (TL-T869-01):** … use Node 24 or 26 if you enable it" (read here); release document X-12, M-4. **Remainder**: whether 2.4.0 runs on Node 22 is unverified and no installer check enforces a Node minimum; the release document keeps this as K-43 (item 51). The release document's K-43 calls TL-T869-01 "LOW, tracked" (section 4.3) | - |
| TL-T869-02 | info (T869) | Plan-182 treated SEC-T762-04 and TL-T761-10 as open for the user; both were fixed in v16 | **obsolete** (no defect; the orchestrator dropped the user action, plan-182 § Addendum 2) | `release-next-audit-v1.md` § 5, § 6 | - |
| SEC-T881-01 | SECURITY:LOW (A06) | `opentelemetry-api` 1.45.1 (CVE-2026-126360, availability only) in `ci/requirements-ci.txt`; CI locks were outside the routine audit | **fixed** (T880) | Lock 1.45.2 with hashes (`ci/requirements-ci.txt`; release document X-11); checklist § 2 "Audit scope (T880)" now audits every `ci/requirements-*.txt` and the § 5 row of 2026-11-19 records no known vulnerabilities after (read here). T881: "Fixed by T880 and closes on merge" | - |
| SEC-T881-02 | SECURITY:LOW (A08) | `ci/requirements-ci.txt` header line 2 does not reproduce the lock on its own (the `--upgrade-package` step from the previous lock is in lines 3-6) | **tracked-LOW** | At the next full regeneration of the lock, write the exact reproducing command (T881 § Findings). Owner devops-engineer | X |
| QA-T875-01 / SEC-T877-01 (counted as one) | Low (T875); SECURITY:LOW (A05) (T877) | Release document M-1 and `docs/wiki/mcp-servers.md:121` said the deny-unless-granted keys are never written as an allow; `edit` is written `edit: allow` (20 agents) | **fixed** (`e0e3b355`) | `docs/releases/v12.0.0.md:85` ("`edit` is different: an agent whose source holds `edit` gets `edit: allow` (20 agents)") and `docs/wiki/mcp-servers.md:121` ("For `edit` the generator writes `edit: allow` (20 agents) … (SEC-T877-01)") (read here); Conditions: C1 of T875, C-4 of T877, "met" | - |
| QA-T875-02 | Low (T875) | "What a target does not receive" said the install writes no `docs/wiki/`; it writes the two project-wiki templates | **fixed** (`e0e3b355`) | `docs/releases/v12.0.0.md:77` ("of `docs/wiki/` only the two project-wiki templates") (read here); Conditions: C2 of T875, "met" | - |
| TL-T876-01 | Important (T876) | K-36 and K-32 written before the probe tag ran | **fixed** (`e0e3b355`) | K-36 and K-32 report the probe (`docs/releases/v12.0.0.md:207-208`, read here); Conditions: C-1 of T876, "met"; T878 confirmed | - |
| TL-T876-02 | Minor (T876) | `taskMap(slug, data, sourceTools, cfg, agentNames)` in `implementation/scripts/sync.mjs:693` has 5 parameters (standard: 4) | **tracked-LOW** | Derive `sourceTools` inside, or pass one context object. Owner devops-engineer, at the next generator change (T876) | AB |
| TL-T876-03 | LOW (T876) | The python CA job lacks the node job's guarded `--capath` step | **obsolete** (dismissed by the orchestrator, plan-182 § Addendum 4; withdrawn by its author, T878 point 1) | `.gitlab-ci.yml:180`, `:182` already run `--capath` unconditionally (per T878; not re-read here **(unverified)**) | - |
| TL-T876-05 | Minor (T876) | A-02 cited "register v20's counts, not re-counted" | **fixed** (`e0e3b355`) | A-02 now cites T876's re-count at `90124fb6` (`docs/releases/v12.0.0.md:52`, read here) | - |

TL-T876-04 has no row here: it is SEC-T867-01 (section 2.2). `e0e3b355` is an ancestor of `458c17ec` (read here).

## 4. Decisions since v25

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-19 | "Accept for v12.0.0 (Recommended)" | SEC-T660-01 and SEC-T665-01 accepted for v12.0.0 only, after T871 | `docs/releases/v12.0.0.md:285-286`; plan-182 § Addendum 2 |
| 2026-11-19 | (the user's report of the runner steps) | SEC-T811-05 applied; recorded by the orchestrator in checklist § 5 | checklist § 5 row 2026-11-19 |
| 2026-11-20 | "v26 go" | This register | plan-183 § User decision; T882 brief |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| TL-T869-01 route | PREREQUISITES note (applied by T880) | the orchestrator | plan-182 § Addendum 2; X-12 |
| TL-T876-03 | Dismissed | the orchestrator; withdrawn by T878 | plan-182 § Addendum 4; T878 |
| TL-T876-02, SEC-T881-02 | LOW, tracked under the LOW policy | T876, T881; the orchestrator | release document Conditions |
| SEC-T811-05 fixed; patching rule to item 44 | as section 2.2 | **mine** | section 2.2 |
| TL-T869-01 fixed (not tracked) | as section 3 | **mine** | section 3, section 4.3 |
| TL-T869-02, TL-T876-03 obsolete; TL-T876-04 with SEC-T867-01; QA-T875-01 with SEC-T877-01 | precedents of section 1.2 | **mine** | section 1.2 |
| TL-T876-04's date-printing half joins SEC-T867-02 | one surface, one owner | **mine** | section 2.2 |
| Batches of the two new tracked ids | X (SEC-T881-02), AB (TL-T876-02) | **mine** (suggestion) | section 5 |
| Merges, pipelines, ledger | As plan-183 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids or statuses; the totals are mine.** My reading gives SEC-T811-05 fixed; 6 new fixed (counting QA-T875-01 and SEC-T877-01 as one, as the expected delta's single cell does); SEC-T881-02 and TL-T876-02 tracked-LOW; SEC-T660-01 and SEC-T665-01 renewed for v12.0.0. For the "decide the status" row: TL-T869-02 and TL-T876-03 **obsolete**, TL-T876-04 **counted with SEC-T867-01**. Totals 750 (575 / 46 / 12 / 1 / 116), batch total 117.
- **TL-T869-01: the release document says "tracked", the plan and checkpoint say "fixed".** `docs/releases/v12.0.0.md` K-43 reads "(M-4; TL-T869-01, LOW, tracked)" and K-18 lists it among the new ids without a status; plan-183 and checkpoint-044 say "fixed by T880". I rule **fixed**: the finding's own route (T869 § 6) offered a note as the resolution, and the note is in place. What K-43 keeps (Node 22 unverified, no Node minimum enforced) is a Known Issue, carried as item 51, not a debt id. If the orchestrator prefers the release document's word, TL-T869-01 moves to tracked-LOW (batch I or X) and the totals become 574 fixed and 117 tracked-LOW, batch total 118.
- **TL-T876-04 is not wholly SEC-T867-01.** Its second half (the printed date's offset) is not in SEC-T867-01's text; I attach it to SEC-T867-02's remainder (section 2.2) rather than mint an id.
- **SEC-T811-05's § 5 row** still says the tag pipeline on the hardened runner is "not yet observed"; checkpoint-044 records it. A record gap only (section 2.2).
- **The commit range.** Plan-183 § Facts names `9b9a31f0..43b6d3f2`; this register searched `9b9a31f0..458c17ec`, adding plan-183's own commit, which mints no id.
- **Ledger.** Plan-183 § Facts: "0 active, 678 completed". Read here: `completed-tasks.md` holds 678 task rows and `active-tasks.md` one (T882, added by the plan-183 commit). No difference.

## 5. Open items by LOW batch

Carried from v25 § 5; X changes members, not size; AB grows by one.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v25 § 5 | 24 | as v25 | as v25 |
| K | Security runtime | as v25 § 5 | 8 | as v25 | as v25 |
| L | CWSO helper scripts in emage.code | as v25 § 5 | 5 | as v25 | as v25 |
| M | CWSO repository | as v25 § 5 | 12 | as v25 | as v25 |
| N | Release tooling, second round | as v25 § 5 | 10 | as v25 | as v25 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v25 | as v25 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v25 | each release's preparation (section 2.2) |
| R | Release-gate text, second round | as v25 § 5 | 7 | as v25 | as v25 |
| V | Release gate after plans 142, 143 and 146 | as v25 § 5 | 17 | as v25 | as v25 |
| **X** | CI images, the CA control, the CI locks and the pin-age check | SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T867-01 (with TL-T876-04), SEC-T867-02 (with TL-T876-04's date print); **new:** SEC-T881-02. **Left:** SEC-T811-05 (fixed) | 6 | devops-engineer | SEC-T768-04 at the next tag-job change; SEC-T867-01 and -02 with the next change to `audit-mcp-pins.py age` or at the next `npx` pin bump, whichever comes first; SEC-T881-02 at the next full regeneration of `ci/requirements-ci.txt` (item 17); SEC-T756-02 and TL-T761-11 as v25 (item 35) |
| Y | Shipped text and records | as v25 § 5 | 11 | as v25 | as v25 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v25 | as v25 |
| U | Live checks and user | as v25 § 5 | 6 | as v25 | as v25 (K-20 keeps the refused-call, launch and refused-read checks) |
| **AB** | Opencode permission, third round: the generator's permission maps and their evidence runs | SEC-T856-02, SEC-T867-03; **new:** TL-T876-02 | 3 | devops-engineer (generator, tests and docs; the orchestrator assigns) | the next change to the Opencode permission generator or its docs, or the next `mcp-agent-denials-evidence` run, whichever comes first; check at next-release preparation with item 49 |

Total 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 6 + 11 + 2 + 6 + 3 = **117** = 116 tracked-LOW + 1 open (K-20). Against v25's 116: X - 1 + 1, AB + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Rows changed against v25: X and AB** (and Q's ids written out, unchanged).

**Why X for SEC-T881-02.** It is a CI supply-chain record in `ci/requirements-ci.txt`, the same owner and the same checklist (§ 2) as X's pin and image items; its trigger, the next full lock regeneration, is a CI maintenance step. X's scope line now names the CI locks. A new letter for one id would split the CI surface (v12 Metadata).

**Why AB for TL-T876-02.** `taskMap` builds the Opencode `task` permission map (`sync.mjs:693-699`, read here), AB's surface, and its trigger, "the next generator change", is AB's.

**Order, my suggestion only.** v25 § 5 stands, with: in X, SEC-T881-02 with the next lock regeneration; in AB, TL-T876-02 with the next permission-generator change.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v25 § 6.1 stand and stay the record. Since v25: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871, the Security Engineer's confirming review for v12.0.0 (ADR-016). They are carried unchanged from K-16 (`docs/releases/v12.0.0.md:184`) into the Conditions (`:285`, `:286`; T877 C-1): `risk_accepted_by=@user`, grade `SECURITY:MEDIUM`, `release=v12.0.0`, plan as shown (owner the user for isolation, devops-engineer for documentation), "Fix: none possible in the harness", the outside closers named per T871, review **2027-01-28**. Their v11.0.0 acceptance ended with that release. No agent accepted a risk. **Each acceptance covers v12.0.0 only**: each id returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. The young-pin exceptions (section 6.3) are recorded exceptions under checklist § 1, not risk acceptances.

### 6.2 Next release checklist (the release after v12.0.0)

Reset from v25 § 6.2 (through it v24 to v17 § 6.2), with its numbers. Where an item keeps its text, the text is in the register that last changed it. Status at v12.0.0 from `release-next-audit-v1.md` § 4 and the gates. No item is dropped: every carried number is either a rule for every release or still open.

**Stand as rules for every release (26), text carried**: 3, 4 (TD-T723-01: re-cite current `install.sh` lines), 6, 7, 9, 10 (SEC-T735-09), 11, 12, 14, 15, 16, 17 (now also: at the next full regeneration of `ci/requirements-ci.txt`, fix SEC-T881-02's header line), 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 35. Line citations into `.gitlab-ci.yml` and `install.sh` moved again in this release; re-read them.

**Stays open (1)**:
- 8: the npm step in a tag pipeline and the musl lock stay **(unverified)**; tag pipeline 3092574856 ran the `release` job, but no source here says what it showed for the npm step.

**Carried, restated after v12.0.0 (6)**:

43. **The acceptances end at each release: SEC-T660-01 and SEC-T665-01, accepted for v12.0.0 only.** Each needs a fix or a new acceptance before the next release that ships it; no agent grants or carries one over. On **2027-01-28** the owner records in the register whether a harness fix now exists and whether the outside closer is still right (ADR-015 O3, W1). A new acceptance needs, before the user is asked, the Security Engineer's new review or dated statement for that release (ADR-016 D1, D2, O-B, O-C; T871 served v12.0.0 and does not serve the next). If 2027-01-28 has passed when the next release ships, the release document says so, with its date and the release it was given for (ADR-015). Ask the way SEC-T735-08 says: name the release, show the plan and a deadline still ahead.
44. **The release-gate runner.** At any bump of the tag jobs' image digest, the runner's `allowed_images` changes with it; in every `v*` tag pipeline all three jobs must show runner #59129270, or SEC-T741-17 reopens (met at v12.0.0, C-3). **Now also (from SEC-T811-05's remainder):** at each CI image review the user patches and records Docker Engine, GitLab Runner and the host kernel in checklist § 5, and patches out of cycle for a critical container-escape advisory, with no release tag until patched (checklist § 3).
46. **Probe tags** (QA-T818-04, tracked): until `resolve_previous_tag` skips pre-releases of the same core version, a probe tag is deleted on the remote and locally (or only `refs/tags/<tag>` is pushed), and `git ls-remote --tags origin` shows no `gate` ref before and after the tag push.
47. **Dates**: section 6.3; each acceptance shown to the user must have its deadline still ahead at the tag.
48. **K-15's reopen condition**: if the Opencode live check (K-20, A-7, SEC-T658-02) shows the per-agent denies are not honoured, SEC-T657-01 / SEC-T658-01 reopen.
49. **SEC-T660-01's Opencode scope** for the acceptance question at the next release (item 43): v24 § 6.2 item 49 stands unchanged ((a) the 15 agents with `execute`; (b) built-in agents and own agent files, K-23; (c) the orchestrators, through their named shell-holding subagents; (d) the 13 others covered for `read`/`grep`/`glob` on the default token directory, not for a parent-directory `grep`, a non-default path, or a token linked into a project; release document K-42). No harness fix for (a) and (b). Re-check the counts if the generator's permission maps change (batch AB).

**New (2), my suggestion**:

50. **MCP pin age at the next release.** The two young-pin exceptions of checklist § 1 lapse by themselves (section 6.3); the release-time `age` run after about 2026-11-25 needs none, and any pin bump voids its exception (T877 C-5). Brave 2.2.0 and other newer upstream releases (`mcp-pin-audit-next-v1.md` § 5) are bump candidates only through the full checklist, including the 7-day rule.
51. **K-43 (from TL-T869-01's remainder).** While the `filesystem` pin declares `engines.node >=24`, the release document must not claim it runs on Node 22, and keeps K-43 until a run on Node 22 or an installer check settles it.

Count: 26 rules + 1 open + 6 carried = 33 numbers, as v25; plus 2 new = 35.

### 6.3 Dates

| Date | What | Ids |
|---|---|---|
| **about 2026-11-24 / 2026-11-25** | The young-pin exceptions lapse: `@brave/brave-search-mcp-server@2.1.5` (published 2026-11-17) about 2026-11-24; `@modelcontextprotocol/server-filesystem@2.4.0` (published 2026-11-18) about 2026-11-25. From then `age` passes without `--allow-young`; caveat SEC-T867-02 (UTC calendar days: may pass up to just under a day early) | item 50; K-40 |
| 2026-11-19 (published) | **Brave 2.2.0**, not pinned (under the age rule; 2.1.5 has no advisory; `mcp-pin-audit-next-v1.md` § 5, plan-182). 7 days old about 2026-11-26 **(derived, unverified)** | item 50 |
| **2027-01-28** | GitLab token renewal; the review of SEC-T660-01 and SEC-T665-01's plan, its deadline under ADR-015 | A-13; SEC-T660-01, SEC-T665-01; item 43 |
| **2027-01-29** | End of TD-T697-07 (CWSO over plain HTTP on a LAN; not shipped, not renewed by v12.0.0) | TD-T697-07 |
| **2027-03-20** | `ci_images_reviewed_on: 2026-11-19` (`.gitlab-ci.yml:25`, read here; no diff in the range) plus 120 days: `test_ci_hash_pins.py` fails from this day; 2027-03-19 is the last passing day | X; item 19 |

The 2027-01-30 Brave date of v17 § 6.3 is gone: SEC-T702-09 is fixed (v22; release document M-4).

## 7. User actions

v25 § 7 stands, with these changes:

- **SEC-T811-05: done.** The user applied the runner steps on 2026-11-19 (checklist § 5; section 2.2). What recurs is the patching rule of checklist § 3 (item 44), at each CI image review and out of cycle.
- **K-20 / A-7 stays open**: the one-time live client checks (refused call, launch and refused read on Opencode; Copilot grants; the rest of release document K-20).
- **Optional: remove `/tmp/evidence-run`**, the neutral evidence root T861 created. It still exists (read here, existence only).

## 8. Method, limits and validation

- **Carried statuses**: v25's rows and lists, plus the sources in Based on. Plan-183 § Facts, plan-182 § Outcome and checkpoint-044 are the only sources for the merges (!706 to !710), the tag, the pipelines (3090926673, 3092574856), the runner, the Release body and the drift (`releases_behind=0`). `docs/tasks/completed-tasks.md` holds 678 task rows and `active-tasks.md` one (T882) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 2638 lines added in `9b9a31f0..458c17ec` outside `tests/golden/` and `.vscode/` (there is no diff in either) and set against the text of registers v1 to v25; the result is section 1.2. Labels were classified by the files they occur in.
- **Counting**: 12 ids named new, 10 counted (TL-T876-04 with SEC-T867-01; SEC-T877-01 with QA-T875-01); 1 status change into `fixed` from tracked-LOW; 2 qualifier changes in `accepted`. Section 5 expands to 117 ids; the sizes of unchanged batches are v25's, not recounted id by id here; X and AB were traced from v25 § 5.
- **Still unverified**:
  - Carried from v25 § 8.
  - The tag pipeline's and probe's runner records, and the user's runner steps beyond the § 5 row (not re-observed; no job log read).
  - `.gitlab-ci.yml:180`, `:182` (TL-T876-03's dismissal; T878's reading).
  - Whether `server-filesystem@2.4.0` runs on Node 22.
  - Brave 2.2.0's 7-day date (derived from the publication date).
  - The batch membership behind "as v25 § 5", and the statuses of the ids named with no change in section 1.2.
- **Not run here**: the suite, the pipelines, `audit-mcp-pins.py`, the generator, Opencode, `pip-audit`.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v25.md`; `tracked-debt-register-v17.md` (§ 1.2, § 2.3, § 6); `plan-183-tracked-debt-register-v26.md`; `docs/tasks/task-T882.md`; `plan-182-next-release.md` (Addenda, Outcome); `checkpoint-044-release-v12.0.0.md`; `docs/releases/v12.0.0.md` (A-02, M-1, M-4, K-16, K-18, K-32, K-36, K-40 to K-43, Conditions);
  - the gate artifacts: `release-next-audit-v1.md` (§ 3 to § 7), `mcp-pin-audit-next-v1.md`, `security-confirmation-t871-sec-t660-t665-v1.md` (by reference), `security-review-t881-ci-lock-v1.md`, `qa-gate-release-v12-v1.md`, `tech-lead-release-v12-v1.md`, `security-review-t877-release-v12-v1.md`, `independent-check-t878-v1.md`;
  - by grep or line read: `docs/wiki/mcp-pin-bump-checklist.md` (§ 2, § 5 rows of 2026-11-19), `docs/wiki/mcp-servers.md:121`, `implementation/PREREQUISITES.md:4`, `implementation/scripts/sync.mjs:693-699`, `.gitlab-ci.yml:25`; registers v1 to v24 (the token scan and the precedents); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat`, `--stat` and `-U0` of `9b9a31f0..458c17ec`; `git merge-base --is-ancestor` for `e0e3b355` and `514503b0`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
