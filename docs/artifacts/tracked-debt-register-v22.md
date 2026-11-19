# Artifact: tracked-debt-register-v22.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v21.md` (726 ids; v21 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-174-tracked-debt-register-v22.md` (§ User decision, § Facts since v21, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T854.md` (the user's "v22 go"); `docs/plans/plan-172-batch-p-brave-upstream-report.md` (§ Outcome); `docs/plans/plan-173-brave-2-1-5-pin-bump.md` (§ Outcome, "For register v22"); `docs/artifacts/brave-upstream-report-draft-v1.md` and `-v2.md`; `docs/artifacts/security-review-t850-brave-report-v1.md` (CONDITIONAL_PASS); `docs/artifacts/security-review-t852-brave-2-1-5-v1.md` (PASS); `docs/artifacts/brave-audit-acceptance-v4.md`; `docs/wiki/mcp-pin-bump-checklist.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T854 (plan-174; the user's answer of 2026-11-19, verbatim: "v22 go"). **Date**: 2026-11-19.
- **Tree read**: branch `agent/tech-lead/T854` at `cd5130a7` (develop `0657ec2d` plus the plan-174 commit). The range for "lines added since v21" is `2be43862..cd5130a7` (plan-174 § Facts names `2be43862..0657ec2d`; the one extra commit is plan-174's own plan, brief and ledger row): 29 files, 1245 lines added and 60 removed; outside `tests/golden/` and `.vscode/`, 28 files, 1244 added and 59 removed (read here). `tests/golden/` has no diff in the range. Unlike v21's range, `.vscode/mcp.json` has a two-line diff (the Brave pin, per T853 in plan-173 § Outcome); it is excluded from the search as in v21 and was not opened (read here: `git diff --stat` only).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `cd5130a7`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v20 only by grep. No network call was made, so the upstream issue is not checked here **(unverified)**. No credential, token value or network address is written here; the one URL is the public GitHub issue.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v21.
- **Batch letters**: no batch ends and none is new. I grows by one (TD-T849-01, my suggestion, section 5); P keeps its one id with a new owner and trigger.

## 1. Summary

v22 holds **729 ids**: the 726 of v21 and **3 new**. After v22: **551 fixed**, **46 accepted**, **10 obsolete**, **1 open**, **121 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01, TD-T808-01 and the new TD-T849-01 have no reviewer's grade (the orchestrator's ids, called LOW). The only MEDIUMs still accepted for v11.0.0 are SEC-T660-01 and SEC-T665-01 (accepted, not open).
- **Fixed since v21 (1 accepted)**: SEC-T702-09 (MEDIUM, A06) by T851, the Brave pin bump to 2.1.5 (T852 PASS; section 2.3).
- **New, minted and fixed (2)**: SEC-T850-01, SEC-T850-02 (T850; fixed by draft v2, plan-172 § Outcome).
- **New and tracked-LOW (1)**: TD-T849-01 (orchestrator id; batch I, my suggestion).
- **Note, no status change**: SEC-T702-08 (tracked-LOW, batch P) was filed upstream by the user on 2026-11-19 as https://github.com/brave/brave-search-mcp-server/issues/377 (plan-174 § Facts; plan-173 § Outcome). It closes when a release with the fix is pinned.
- **Accepted risks**: SEC-T702-09's acceptance ended (section 6.1). **Next-release checklist**: item 43 loses its SEC-T702-09 part; item 49 unchanged (section 6.2). **Dates**: 2027-01-30 leaves (section 6.3). **User actions**: unchanged.

Arithmetic, from the v21 totals:

| Status | v21 | leaves | enters | v22 |
|---|---:|---|---|---:|
| fixed | 548 | | + 1 accepted (SEC-T702-09); + 2 new (SEC-T850-01, -02) | **551** |
| accepted | 47 | - 1 fixed (SEC-T702-09) | | **46** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 120 | | + 1 new (TD-T849-01) | **121** |
| **all** | **726** | | + 3 new ids | **729** |

Check: 551 + 46 + 10 + 1 + 121 = 729. Open or tracked: 121 + 1 = 122, the size of section 5.

### 1.1 Ids by v21 status and status now

| v21 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 120 | 0 | 0 | 0 | 0 | 120 |
| accepted | 47 | 1 | 46 | 0 | 0 | 0 |
| fixed | 548 | 548 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v21 ids** | **726** | **549** | **46** | **10** | **1** | **120** |
| new in v22 | 3 | 2 | 0 | 0 | 0 | 1 |
| **all v22 ids** | **729** | **551** | **46** | **10** | **1** | **121** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t850-brave-report-v1.md`: SEC-T850-01, SEC-T850-02 | 2 | 2 | 0 |
| plan-173 § Outcome (orchestrator id): TD-T849-01 | 1 | 0 | 1 |
| **All new** | **3** | **2** | **1** |

**Ids minted in the range beyond the plan's list: none.** A search of the 1244 added lines in `2be43862..cd5130a7`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<digits or T-number>…` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `L-<n>`) finds exactly: ADR-011, K-17, K-20, L-8, SEC-T646-03, SEC-T646-05, SEC-T660-01, SEC-T665-01, SEC-T676-11, SEC-T702-07, SEC-T702-08, SEC-T702-09, SEC-T756-07, SEC-T850-01, SEC-T850-02, SEC-T852, TD-T849-01 (read here). `SEC-T852` occurs only as the template `SEC-T852-NN` in T852's line "This review mints no new `SEC-T852-NN` id" (not a debt id); `L-8` occurs only inside `T638-L-8`, a reference already in the registers (read here). Set against registers v1 to v21, only SEC-T850-01, SEC-T850-02 and TD-T849-01 are in no register. Beside them:
- **Ids named with a change of status**: SEC-T702-09 (fixed, section 2.3).
- **Ids named with no change of status**: SEC-T702-08 (tracked-LOW, batch P; filed upstream, section 2.2); SEC-T702-07 (fixed by T712; T852: "the forced stdio still holds"); SEC-T756-07 (tracked-LOW, batch X; T851/T852: the 3 known moderates, unchanged); SEC-T660-01, SEC-T665-01 (accepted for v11.0.0; named in T852's and the acceptance context); SEC-T646-03, SEC-T646-05, K-17, SEC-T676-11 (fixed, as their registers record; named in the checklist § 1 steps and the pin test docstring that T851 touched); ADR-011 (named, not amended); K-20 (open).
- This register mints no id.

## 2. v21 ids re-checked

Every v21 `open`, `tracked-LOW` and `accepted` id (168) is covered: the changed ones have a row here, the rest are unchanged and carried. The v21 `fixed` and `obsolete` ids stay as v21 records them.

### 2.1 v21 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No Opencode file changed in the range beyond the one-line Brave pin in `.opencode/opencode.json` and its mirror (read here: `git diff --stat`).

### 2.2 v21 `tracked-LOW` (120)

**Changed: none in status. One note.**

| Id | v21 | now | Evidence |
|---|---|---|---|
| SEC-T702-08 | tracked-LOW, `SECURITY:LOW`, batch P | **tracked-LOW**, batch P (owner and trigger updated, section 5) | Filed upstream by the user on 2026-11-19 as https://github.com/brave/brave-search-mcp-server/issues/377; "The issue is open, and its text is draft v2 § 4" (plan-174 § Facts; plan-173 § Outcome, "For register v22"). Draft v2 § 5's rule for the answer "filed: <URL>": "recorded as reported upstream; it closes when a release with the fix is pinned" (plan-172 § Outcome). T849 found the unbounded `fetch` and whole-body reads still present in 2.1.5 (`dist/BraveAPI/` byte-identical to 2.1.4) and on `main` at `e08f5af0`; T852 records it "unchanged (issue #377, batch P)". The issue's existence and state were not checked here **(unverified)** |

**Unchanged (119 tracked-LOW besides SEC-T702-08; v21 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, Q 5, R 7, V 17, X 10, Y 11, F 2, U 5 (U's sixth id is K-20, open), AA 3. 24 + 8 + 5 + 12 + 10 + 5 + 7 + 17 + 10 + 11 + 2 + 5 + 3 = 119; with SEC-T702-08 (P), 120; with the 1 new, 121 tracked-LOW in section 5. (The batch sizes are carried from v21 and not recounted id by id here.)

### 2.3 v21 `accepted` (47)

**Changed (1).**

| Id | v21 | now | Evidence |
|---|---|---|---|
| SEC-T702-09 | accepted for v11.0.0 only, `SECURITY:MEDIUM` (A06); end 2027-01-30 or the first Brave release above 2.1.4 (v17 section 2.3; `brave-audit-acceptance-v4.md`) | **fixed** | T851 (commit `bb9ccb37`; MR !698, develop `0657ec2d`, per plan-174 § Facts): the `brave` pin is `@brave/brave-search-mcp-server@2.1.5`, still with `--transport stdio`. T852 PASS: "**Its acceptance has ENDED.** Its own end condition, 'the first Brave release above 2.1.4', was met when 2.1.5 was published on 2026-11-17. The bump also voids it mechanically: the script refuses all seven acceptances as 'not a current npm pin'. No new acceptance and no ADR-011 renewal is needed at the next release." 2.1.5 carries `@modelcontextprotocol/sdk` 1.32.2 and `zod` 4.6.7 (plan-172 § Outcome, the orchestrator's `npm view`). Read here: the refusal of a 2.1.4 acceptance is asserted at `tests/functional/test_pin_bump_checklist.py:212` (`assertRaisesRegex(mod.AuditError, "is not a current npm pin")`). T852's residual (the root self-install still on 2.1.4 until T853) is closed by T853 (drift `[]`, plan-173 § Outcome); v11.0.0 shipped 2.1.4 under the valid acceptance and its record stays. That the 2.1.5 audit is clean rests on T851's and the orchestrator's runs, not re-run here **(unverified)** |

**Unchanged (46)**, with their v17 qualifiers (v17 section 2.3). SEC-T660-01 and SEC-T665-01 are named in the range with no change.

## 3. New ids

The grade is the reviewer's own.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T850-01 | SECURITY:LOW (wording) | Draft v1 § 4 "What happens" called both undici timers "inactivity timeouts"; `headersTimeout` is a total wait and only `bodyTimeout` is an inactivity timer, so the draft overstated the headers case | **fixed** | T850 § findings (CONDITIONAL_PASS); fixed by `brave-upstream-report-draft-v2.md`, v1 with T850's exact replacement text for that paragraph (draft v2 revision note; plan-172 § Outcome) | - |
| SEC-T850-02 | SECURITY:LOW (wording) | Draft v1 § 4 "Side note, same lines" quoted an error string that was not verified | **fixed** | T850 § findings; fixed by draft v2 (T850's replacement text for "Side note, same lines") (plan-172 § Outcome) | - |
| TD-T849-01 | none (orchestrator id, called LOW) | `tests/functional/test_merge_task_docs.py` `test_temp_file_has_the_old_mode_before_content_and_a_random_name` asserts `assertNotIn(str(os.getpid()), seen["name"])` (line 454, read here), a substring check, so it fails when the CI pid's digits occur by chance in mkstemp's random name. Seen in pipeline 3087701714 (on `900deb79`, MR !697), passed on a retry of the same sha (plan-173 § Outcome; plan-174 § Facts; the job log was not opened). The same flaw was TD-T746-01; its fix, a whole-field check (`re.split(r"[.-]", first)`), is in `test_merge_mcp_json_robustness.py` only (line 177, with the TD-T746-01 comment, read here). That T754 made that fix is plan-173's statement; `git log --grep=T754` finds no commit subject naming it **(unverified)** | **tracked-LOW** | plan-173 § Outcome, "For register v22". Remediation, my suggestion: apply the same whole-field check in `test_merge_task_docs.py`. Owner: devops-engineer or backend-developer (the orchestrator assigns) | I |

## 4. Decisions since v21

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-19 | the go for plan-172 (words not re-read here) | T849, T850 | plan-172 **(unverified)** |
| 2026-11-19 | "Brave 2.1.5 go" | T851, T852 | T852 § Metadata |
| 2026-11-19 | "Refresh now (Recommended)" | T853 root refresh | plan-173 § Outcome; plan-174 § Facts |
| 2026-11-19 | filing SEC-T702-08 upstream (issue #377) | SEC-T702-08 reported upstream | plan-174 § Facts |
| 2026-11-19 | "v22 go" | This register | plan-174 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T702-09 | Fixed; acceptance ended by its own terms | T852 (PASS); the orchestrator | T852; plan-173 § Outcome |
| SEC-T850-01, -02 | Minted and fixed (draft v2) | T850; the orchestrator | plan-172 § Outcome |
| TD-T849-01 | Tracked-LOW, under the LOW policy | the orchestrator | plan-173 § Outcome |
| Batch of TD-T849-01 | I | me (suggestion) | section 5 |
| SEC-T702-08 | Tracked-LOW, reported upstream | the orchestrator; T852 | plan-173 § Outcome; plan-172 § Outcome (draft v2 § 5) |
| Merges, pipelines, suite, ledger | As plan-174 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** My reading gives the same 3 new ids, the same 1 that leaves `accepted`, 729 ids (551 / 46 / 10 / 1 / 121) and a batch total of 122. What I add: the batch for TD-T849-01 (I), the non-debt tokens of section 1.2 (`SEC-T852-NN`, `T638-L-8`), and the `.vscode/mcp.json` diff noted in Metadata.
- **The commit range.** Plan-174 § Facts names `2be43862..0657ec2d`; this register searched `2be43862..cd5130a7`, which adds plan-174's own commit. The extra commit mints no id.
- **Ledger.** Plan-174 § Facts: "0 active, 650 completed". Read here: `completed-tasks.md` holds 650 task rows and `active-tasks.md` one (T854, added by the plan-174 commit). No difference.
- **Reviewers' line numbers** (T849's `dist/` and `src/` lines, T852's) are theirs at the reviewed commit **(unverified)** at `cd5130a7`.

## 5. Open items by LOW batch

Carried from v21 § 5; I and P change.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v21 § 5; **new:** TD-T849-01 | 25 | as v21; for TD-T849-01 the orchestrator assigns (devops-engineer or backend-developer) | as v21; TD-T849-01 with the next edit of `tests/functional/test_merge_task_docs.py`, or at its next CI failure |
| K | Security runtime | as v21 § 5 | 8 | as v21 | as v21 |
| L | CWSO helper scripts in emage.code | as v21 § 5 | 5 | as v21 | as v21 |
| M | CWSO repository | as v21 § 5 | 12 | as v21 | as v21 |
| N | Release tooling, second round | as v21 § 5 | 10 | as v21 | as v21 |
| P | Upstream report to the Brave project | SEC-T702-08 (reported upstream: issue #377, filed by the user 2026-11-19) | 1 | **updated:** upstream (the Brave project) for the fix; devops-engineer for the pin bump that carries it, per `docs/wiki/mcp-pin-bump-checklist.md` | **updated:** the report is filed; the id closes when a Brave release with the fix (bounded `fetch` and body reads, issue #377) is published and pinned. Check at each Brave pin bump and at next-release preparation |
| Q | Next release document and its gate rulings | as v21 § 5 | 5 | as v21 | as v21 |
| R | Release-gate text, second round | as v21 § 5 | 7 | as v21 | as v21 |
| V | Release gate after plans 142, 143 and 146 | as v21 § 5 | 17 | as v21 | as v21 |
| X | CI images, the CA control and runner settings | as v21 § 5 | 10 | as v21 | as v21 |
| Y | Shipped text and records | as v21 § 5 | 11 | as v21 | as v21 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v21 | as v21 |
| U | Live checks and user | as v21 § 5 | 6 | as v21 | as v21 (K-20 keeps the refused-call check) |
| AA | Opencode permission, second round | SEC-T837-02, SEC-T842-02, SEC-T844-01 | 3 | devops-engineer (T837, T842, T844) | as v21 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 11 + 2 + 6 + 3 = **122** = 121 tracked-LOW + 1 open (K-20). Against v21's 121: I + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01, TD-T808-01 and TD-T849-01 have no reviewer's grade.

**Why I for TD-T849-01.** The test covers `merge-task-docs.py`'s `sync_task_docs`, the installer's task-ledger merge (read here: the test loads `merge-task-docs.py`), so the code under test is in I's scope. Its sibling TD-T746-01 had batch W, which ended in v12 and is not reused (v12 Metadata). The fix is one assertion and needs no new letter. Y (shipped text) does not fit: no text changes.

**Order, my suggestion only.** v21 § 5 stands, with these changes: TD-T849-01 is cheap and removes a known CI flake, so it can go first in I; P waits on upstream.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v21 § 6.1 stand and stay the record, with one change: **SEC-T702-09's acceptance for v11.0.0 has ended** by its own end condition (the first Brave release above 2.1.4, 2.1.5 of 2026-11-17), and the id is fixed (section 2.3). `brave-audit-acceptance-v4.md` stays the record of that acceptance; its seven `--accept` entries are void and refused by the script (T852). **The MEDIUMs accepted for v11.0.0 only are now SEC-T660-01 and SEC-T665-01**, review **2027-01-28** (token renewal). None accepted since v21. No agent accepted a risk.

### 6.2 Next release checklist (the release after v11.0.0)

v21 § 6.2 (through it v20, v19, v18 and v17 § 6.2) stands, with one change in item 43:

- **Item 43 (narrowed): the two MEDIUMs accepted for v11.0.0 only: SEC-T660-01, SEC-T665-01.** v17 § 6.2 item 43 stands for those two (its sub-bullet on the 2027-01-28 review, ADR-015 O3/W1, ADR-016 D1/D2/O-B/O-C, and the ask the way SEC-T735-08 says). Its heading's SEC-T702-09 and its sub-bullet "SEC-T702-09: the fix (the first Brave release above 2.1.4) or a new acceptance with a new Brave record (v5) and gate command before the tag; check npm's newest Brave release at preparation" are dropped: the fix is in (section 2.3). **Nothing else in § 6.2 names SEC-T702-09**: in the § 6.2 sections of v17 to v21 it occurs only in item 43's heading and that sub-bullet (read here, by grep; v16 and earlier § 6.2 are superseded through v17's item 43, which replaced item 2, and were not re-read).
- **Item 49: unchanged** (v20 wording as updated in v21). No file under `implementation/.opencode/` or `.opencode/` changed in the range except the one-line Brave pin (read here).

**Checklist facts changed by T851** (`docs/wiki/mcp-pin-bump-checklist.md`, read here):
- **Provenance**: `@brave/brave-search-mcp-server@2.1.5` has npm provenance (SLSA v1); 2.1.4 had none (plan-173 § Outcome; run record of 2026-11-19 at line 57). The 2026-10-22 run record ("never published with provenance") stays as history.
- **§ 4 release gate** (line 42): `audit --audit-level high --signatures` and `provenance` with **no `--accept`**; any new acceptance needs the user's decision, a new artifact, scoping to a current pin and the test listing it (T852).
- **`tests/functional/test_pin_bump_checklist.py`** now requires every `--accept` to name a current npm pin (line 78: "... which is not a current npm pin"; lines 212, 225, 230), and checks the v3 and v4 records as history.

Count: the 33 numbers of v21 stand; item 43 keeps its number with a narrower scope.

### 6.3 Dates

v21 § 6.3 stands except one date:
- **2027-01-28**: SEC-T660-01 and SEC-T665-01 review (token renewal). Unchanged.
- **2027-01-29**: TD-T697-07 ends. Unchanged.
- ~~2027-01-30~~: **removed**. SEC-T702-09's end date no longer applies: the acceptance ended with Brave 2.1.5 (section 6.1).
- **2027-03-12**: the CI image review date fails (`ci_images_reviewed_on: 2026-11-11` plus 120 days); `.gitlab-ci.yml` has no diff in the range (read here). Unchanged.

## 7. User actions

v21 § 7 stands unchanged. K-20 / A-7 stays open. The upstream filing of SEC-T702-08 is done by the user (section 2.2); no new user action.

## 8. Method, limits and validation

- **Carried statuses**: v21's rows and lists, plus the sources in Based on. Plan-174 § Facts is the only source for the merges (!696, !697, !698), the suites (2775 OK at `900deb79`; 2778 OK, skipped=25, at `1e01a5d5`), the pipelines (the TD-T849-01 failure and its retry; three green at `1e01a5d5`), the root refresh (drift `[]`) and the ledger count. `docs/tasks/completed-tasks.md` holds 650 task rows and `active-tasks.md` one (T854) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 1244 lines added in `2be43862..cd5130a7` outside `tests/golden/` and `.vscode/`, and set against the text of registers v1 to v21; the result is section 1.2.
- **Counting**: 3 new ids, 1 status change. Section 5 expands to 122 ids; the sizes of unchanged batches are v21's, not recounted id by id here.
- **Still unverified**:
  - Carried from v21 § 8.
  - The upstream issue #377's existence and state (no network call).
  - T851's and the orchestrator's audit and provenance runs on 2.1.5 (not re-run here).
  - That T754 made the whole-field fix in `test_merge_mcp_json_robustness.py` (plan-173's statement).
  - The orchestrator's suites and pipelines (plan-174 § Facts; not re-run here).
  - The batch membership behind "as v21 § 5".
- **Not run here**: the suite, the pipelines, the generator, the audit script, npm.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v21.md`; `plan-174-tracked-debt-register-v22.md`; `docs/tasks/task-T854.md`; `plan-172-batch-p-brave-upstream-report.md` (§ Outcome); `plan-173-brave-2-1-5-pin-bump.md` (§ Outcome);
  - by grep or line read: `security-review-t852-brave-2-1-5-v1.md`; `brave-audit-acceptance-v4.md`; `security-review-t850-brave-report-v1.md` and `brave-upstream-report-draft-v2.md` (through the added lines); `docs/wiki/mcp-pin-bump-checklist.md`; `tests/functional/test_pin_bump_checklist.py`; `tests/functional/test_merge_task_docs.py`; `tests/functional/test_merge_mcp_json_robustness.py`; registers v1 to v21 (the token scan, § 6.2 of v17 to v21); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat` and `--stat` of `2be43862..cd5130a7`; `git diff -U0` of the range outside `tests/golden/` and `.vscode/` (added lines only, for the token scan).
- Decision IDs: ADR-011, ADR-015, ADR-016.
