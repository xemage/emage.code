# Artifact: tracked-debt-register-v33.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v32.md` (771 ids; v32 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there; its § 5 and § 6 are carried by reference where this register says "as v32"); `docs/artifacts/tracked-debt-register-v26.md`, `-v24.md` and `-v15.md` (the precedents for counting an id minted before merge); `docs/artifacts/tracked-debt-register-v14.md` (the text of TD-T789-01 and the batch Y rows) and `-v12.md` (TL-T753-05, TL-T753-07, TL-T763-01, TL-T763-02); `docs/plans/plan-197-tracked-debt-register-v33.md` (§ User decision, § Facts since v32, § The orchestrator's expected delta, § Task Decomposition) and `docs/tasks/task-T905.md` (the user's "v33 go"); `docs/plans/plan-196-batch-y-shipped-text.md` (Outcome); `docs/artifacts/security-review-t904-batch-y-v1.md` (per-id table, new findings, the orchestrator's addendum); `docs/artifacts/independent-check-t763-v1.md` (TL-T763-01). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T905 (plan-197; the user's answer of 2026-11-21, verbatim: "v33 go"). **Date**: 2026-11-21.
- **Tree read**: branch `agent/tech-lead/T905` (develop `a1af3b58` plus the plan-197 commit `efd04291`). The range for "lines added since v32" is `9493946b..a1af3b58`: 16 files, 700 lines added and 8 removed (read here: `git diff --shortstat`). No diff under `tests/golden/` or `.vscode/`. No code file changes: the range holds `.gitlab-ci.yml` (5 comment lines), `CONTRIBUTING.md`, `implementation/SECURITY.md`, `implementation/runtime/memory/README.md`, two wiki pages, the ledger, task briefs, plans and artifacts. The plan-197 commit is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v32 only by grep (the token scan). No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **Y** drops ten ids (eight fixed, two obsolete; section 2.2) and gains SEC-T904-01 and SEC-T904-03, so Y goes from **11 to 3**. No other batch changes; no new letter, no letter ends.

## 1. Summary

v33 holds **774 ids**: the 771 of v32 and **3 new** (SEC-T904-01 to -03, found by T904 in the review of MR !724). After v33: **621 fixed**, **46 accepted**, **14 obsolete**, **1 open**, **92 tracked-LOW**.

- **Open above LOW: nothing.** T904 found 0 CRITICAL, HIGH or MEDIUM. The one open id is K-20 (live checks, the user; no grade). TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v32, from tracked-LOW (8)**: TL-T761-12, TL-T819-03, TL-T761-13, TL-T780-08, SEC-T847-01, TL-T761-08, TL-T753-07 (the seven of the expected delta) and **TD-T789-01** (my ruling, below). Section 2.2.
- **Obsolete since v32, from tracked-LOW (2)**: TL-T763-01, TL-T763-02 (cannot be fixed at the source; section 2.2).
- **New, minted and closed in the same MR (1)**: SEC-T904-02 (section 3.1). Precedent v26, v24, v15: counted once, as new and fixed.
- **New, tracked-LOW (2)**: SEC-T904-01, SEC-T904-03 (batch Y; section 3.2).
- **How TD-T789-01 and SEC-T904-01 are counted (my ruling).** TD-T789-01 had three parts: O-1, O-2 and flag 3. O-2 and flag 3 are fixed (T904 confirms both; read here in the diff). O-1 is partly fixed: the page now says to check `docker context show` and `DOCKER_HOST`, or to name a context, but the printed command is still a plain `docker run`. T904 named that remainder as **SEC-T904-01**. SEC-T904-01 is the O-1 point itself, graded and with its own remediation. Keeping both tracked would count one point twice (the v26 precedent counts a restatement once), and a "partly fixed" parent with no part of its own left is not a state the register has. I follow the v32 precedent (SEC-T888-01 counted fixed "in the form the review asked for", its residue SEC-T900-02 counted once as new): **TD-T789-01 is fixed, and SEC-T904-01 carries the residue** as one tracked-LOW id. The orchestrator's expected delta keeps TD-T789-01 tracked; that gives 620 fixed, 93 tracked-LOW and a batch Y of 4, one more in each of the last two and one fewer in the first (section 4.3). The user loses nothing either way: the O-1 remainder is tracked in batch Y once.
- **How TL-T763-01 is counted (my ruling).** **Obsolete**, as the expected delta says. The source (`independent-check-t763-v1.md`) said: "Next register: correct the record. Next edit: [reword] in your entries' `project_id`". The register half was done in v12 and the record is in the independent check. The second half would edit the published `docs/releases/v10.0.0.md`, which plan-196 and the release-document rules forbid. The published wording stays and is "still safe and complete" (the check's own words). Nothing remains to do at the source and no later release changes the document. It is not "accepted": no one accepted a risk, the item simply cannot be actioned.
- **How TL-T763-02 is counted.** **Obsolete.** The pointer from M-2 to K-35 belongs in the document that holds M-2. That is the published `docs/releases/v10.0.0.md`; the later release documents that mention K-35 are published too (the orchestrator's addendum to T904, SEC-T904-02). K-35 (QA-T760-03) was fixed by T790 (v14), so the pointer has no work left to point at. The only current `M-2` outside `docs/artifacts/` is the migration item of the v11.0.0 notes, which is unrelated (same source).
- **TL-T753-05 stays tracked-LOW.** Its fix is in knowledge sources (`implementation/knowledge/`), and a change there needs mirror regeneration and a root refresh, which needs the user's approval (section 7). Not recorded as fixed.
- **Next-release checklist**: 36 numbers carried, none new; item 52 gains one point (section 6.2). **Dates**: as v32 (section 6.3). **User actions**: v32's, and one conditional (section 7).

Arithmetic, from the v32 totals:

| Status | v32 | leaves | enters | v33 |
|---|---:|---|---|---:|
| fixed | 612 | | + 8 tracked-LOW (the seven and TD-T789-01); + 1 new fixed (SEC-T904-02) | **621** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | + 2 tracked-LOW (TL-T763-01, -02) | **14** |
| open | 1 | | | **1** |
| tracked-LOW | 100 | - 8 fixed; - 2 obsolete | + 2 new (SEC-T904-01, -03) | **92** |
| **all** | **771** | | + 3 new ids | **774** |

Check: 621 + 46 + 14 + 1 + 92 = 774. Open or tracked: 92 + 1 = 93, the size of section 5.

### 1.1 Ids by v32 status and status now

| v32 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 100 | 8 | 0 | 2 | 0 | 90 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 612 | 612 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v32 ids** | **771** | **620** | **46** | **14** | **1** | **90** |
| new in v33 | 3 | 1 | 0 | 0 | 0 | 2 |
| **all v33 ids** | **774** | **621** | **46** | **14** | **1** | **92** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t904-batch-y-v1.md` § New findings: SEC-T904-01 to -03 | 3 | 1 | 0 | 2 |
| **All new** | **3** | **1** | **0** | **2** |

**Ids minted in the range beyond T904's list: none.** A search of the 700 lines added in `9493946b..a1af3b58` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>`, `<LETTERS>-<digits>` or `ADR-<digits>` (61 distinct tokens; register v32 itself is among the added files), set against the text of registers v1 to v32, finds as in no register exactly the three ids **SEC-T904-01, -02, -03**. The other 58 tokens are in earlier registers (among them the eleven batch Y ids, TL-T753-07's source T745 ids, K-35, ADR-011, ADR-015, ADR-016).

**Duplicates: none after my ruling.** SEC-T904-01 is the residue of TD-T789-01 (O-1), and is counted once, as the one open id for that point (section 1). SEC-T904-03 concerns a function name in the `.gitlab-ci.yml` header, which TL-T761-08 (fixed) put there: a defect in the fix, new and its own. SEC-T904-02 is a check, not a defect in the code or text (section 3.1).

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): the rest of the 58, among them SEC-T745-01 to -11 (named in the T745 ledger row), which are in v5 to v13.

## 2. v32 ids re-checked

Every v32 `open`, `tracked-LOW` and `accepted` id (147) is covered: the changed ones have a row here, the rest are unchanged and carried. The v32 `fixed` and `obsolete` ids stay as v32 records them.

### 2.1 v32 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v32 `tracked-LOW` (100)

Basis: plan-196 Outcome, T904's per-id table (reasoned; T904 had no shell) and the orchestrator's addendum. Fix commits `4fb213db` (T902) and `b209e4f0` (T903); MR !724, develop `a1af3b58`, pinned `204ee14a`; pipelines 3097772273 and 3097772199; clean suite 2883 OK, skipped=25 (plan-197 § Facts). **Verified here in `git diff 9493946b..a1af3b58`:** each text fix below is in the diff; no derived platform folder, published `docs/releases/v*.md`, immutable `-vN` artifact or `tests/golden/` file is touched; `.gitlab-ci.yml` changes by five comment lines only.

**Changed to fixed (8).**

| Id | v32 batch | now | Evidence and remainder |
|---|---|---|---|
| TL-T761-12 | Y | **fixed** (T902) | `CONTRIBUTING.md` now says not to move `main` between the tag and the end of `main-develop-drift-gate`, whose last line compares the tag's tree with `origin/main`, and that `develop` may move. T904 matched this to `.gitlab-ci.yml` line 336; the README-marker half ("the drift check beside it compares only the markers") is **(unverified)** by T904 and by me |
| TL-T819-03 | Y | **fixed** (T902) | Same text: the three tag jobs run only on the runner tagged `release-gate`; its `allowed_images` must equal the digest of `python:3.12-alpine`; otherwise the jobs fail closed; the step is in the pin-bump checklist section 3 and is pointed to, not repeated; "an agent does not change the runner". T904: matches the checklist |
| TL-T761-13 | Y | **fixed** (T902) | `implementation/runtime/memory/README.md` uses `<org>/<repo>` and `<org>-<repo>` with the substitution rule (lower case) in place of this repository's own path. T904: the rule matches the old example |
| TL-T780-08 | Y | **fixed** (T902) | `implementation/SECURITY.md` says v1's statement "v2 keeps the same defaults" is dated and the harness ships no `.vscode/settings.json` (only `.vscode/mcp.json`; the orchestrator checked `implementation/.vscode`). The hardening advice stays, framed for a v1-style list; no control weakened. This checkout's own user-owned `.vscode/settings.json` was not read. The file is under `implementation/`; the orchestrator's `--print-drift` printed `[]` for it (taken as given), so no derived copy differs |
| SEC-T847-01 | Y | **fixed** (T902) | `docs/wiki/mcp-servers.md` says `mcp-agent-denials-evidence-v2.md` section 4 supersedes v1 on a name that no rule after the built-in ones matches (rule 0 is `*: allow` on `opencode-ai@1.19.2`; computed, not observed). Evidence v1 untouched (immutable). T904 checked it against evidence v2 |
| TL-T761-08 | Y | **fixed** (T903) | Five comment lines in the `.gitlab-ci.yml` header name `EOL_TABLE_DATE`, `PINNED_IMAGE` and `DRIFT_GATE_APK` (all three exist in `tests/functional/test_ci_hash_pins.py`: read here, T904 line numbers 1401, 123, 97). No job, key, value or digest changed; the CI lint at the head sha is valid (the orchestrator). **Remainder**: SEC-T904-03 (the function name; tracked) |
| TL-T753-07 | Y | **fixed** (orchestrator) | The T745 row is in `docs/tasks/completed-tasks.md` and `docs/tasks/task-T745.md` is a new record-only brief (both in the range, read here). The v12 note said only the orchestrator can add the row; it did, at plan-196 |
| TD-T789-01 | Y | **fixed** (T902); counted fixed by my ruling (section 1) | The checklist (`docs/wiki/mcp-pin-bump-checklist.md`, section 2 and section 3 step c): **O-2** names the per-platform manifest media types (the registry may answer with an error without them; the hash check still guards the result); **flag 3** now reads "after a change of this lock, watch it at the next release or release candidate" (T904: honest, tag pipeline 3039977704 observed, no log re-read); **O-1** adds the `docker context show` and `DOCKER_HOST` check and a `docker --context <non-production context> run` option. **Residue**: SEC-T904-01 (tracked). No `SECURITY:*` grade for TD-T789-01 itself |

**Changed to obsolete (2).**

| Id | v32 batch | now | Evidence and reason |
|---|---|---|---|
| TL-T763-01 | Y | **obsolete** (cannot be fixed at the source) | Source: `independent-check-t763-v1.md` TL-T763-01 (LOW, track): the value that causes the empty result is the entry's `project_id`, not `--project-id`; TL-T761-02 (immutable) got it wrong. "Next register: correct the record" is done in that check (and v12); "next edit" would reword the published `docs/releases/v10.0.0.md` M-2, which stays untouched. The published advice is safe and complete (lower case in all three). Nothing is left to track |
| TL-T763-02 | Y | **obsolete** (cannot be fixed at the source) | M-2 has no pointer to K-35. M-2 and K-35 are items of the published `docs/releases/v10.0.0.md` (and the later published release notes that cite K-35). K-35 (QA-T760-03) was fixed by T790, so the pointer is moot. The orchestrator's search for a current editable document that holds that M-2 found none (T904 addendum; SEC-T904-02) |

**Unchanged (90 tracked-LOW)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 3, X 3, Y 1 (TL-T753-05), F 2, U 5 (U's sixth id is K-20, open), AB 3. 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 1 + 2 + 5 + 3 = 90 = the 100 of v32 less 8 fixed and 2 obsolete (all ten leave batch Y: 11 - 10 = 1). The sizes of unchanged batches are carried from v32 and not recounted id by id.

### 2.3 v32 `accepted` (46)

**Unchanged (46)**, with their v32 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01 other than as carried text.

## 3. New ids

The grade is the reviewer's own (T904 § New findings). Owner: technical-writer or devops-engineer (my suggestion; no source names one).

### 3.1 Minted and closed in the same MR (1)

| Id | Grade | Short description | Status | Basis |
|---|---|---|---|---|
| SEC-T904-02 | SECURITY:LOW (A09, record accuracy) | If this register records TL-T763-02 as "cannot fix there" with no search for a current document that holds M-2, the id is closed on an unchecked premise. | **fixed** (checked in the same MR, by the orchestrator's addendum) | The orchestrator searched the current documents: no current editable document holds that M-2 (section 2.2). It is a check of this register's own record, not a defect in shipped text; counted once as new and fixed (v26, v24, v15) |

### 3.2 New, tracked-LOW (2)

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T904-01 | SECURITY:LOW (A05) | `docs/wiki/mcp-pin-bump-checklist.md` section 2, CI lock files bullet (the residue of TD-T789-01 O-1): the printed command is still a plain `docker run`. The safe step is offered as a check of `docker context show` and `DOCKER_HOST`, or an optional `--context`. A copy-paste still reaches the production host if `DOCKER_HOST` points at it. `docker context show` prints a name, not a host. Whether `--context` beats an exported `DOCKER_HOST` in the CLI in use was not verified. No agent runs `docker` (the policy stands) | **tracked-LOW** (new) | Put `docker --context <non-production context> run ...` in the printed command, so the placeholder must be filled in; say `docker context inspect <name>` shows the host; keep the `DOCKER_HOST` check | Y |
| SEC-T904-03 | SECURITY:LOW (A05, documentation drift) | The `.gitlab-ci.yml` header names `eol_problems_of`; the comment at `EOL_TABLE_DATE` in `tests/functional/test_ci_hash_pins.py` says `eol_image_problems`. Read here: **both exist** (`eol_image_problems` at line 554 delegates to `eol_problems_of` at line 560), so the text is not wrong, but two names for one table make a search miss | **tracked-LOW** (new) | Name the function that holds the table once in both places, or say `eol_problems_of` is called by `eol_image_problems`. Comment-only; the lint and `test_ci_hash_pins.py` rerun | Y |

**Why batch Y.** Both are shipped text or its records (a wiki page; a CI header comment), the same surface as the rest of Y. Trigger: the next edit of the checklist page (SEC-T904-01) or of the `.gitlab-ci.yml` header (SEC-T904-03); the first is useful before the next image bump (the checklist's own use).

## 4. Decisions since v32

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-21 | "Y go" | Batch Y (plan-196): the 11 ids, T902 to T904 | plan-196 § User decision |
| 2026-11-21 | "Approve (Recommended)" | The plan-196 approval, "All 11 ids: T902 docs, T903 CI header comment, T904 security review" | plan-196 § Addendum 1 |
| 2026-11-21 | "v33 go" | This register | plan-197 § User decision; T905 brief |

I did not verify the words beyond those records **(unverified)**. No risk was accepted by the user in the range.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| TL-T753-07 closed by a ledger row and a record-only brief | The orchestrator's own item | the orchestrator | plan-196 Outcome |
| SEC-T904-02 checked and closed in the artifact's addendum | No current document holds that M-2 | the orchestrator | T904 addendum |
| SEC-T904-01 and -03 not fixed in the MR | A text change would need new suite and pipeline runs | the orchestrator | T904 addendum |
| TL-T763-01, -02 obsolete | Cannot be fixed at the source | the orchestrator; confirmed by me | section 2.2 |
| TD-T789-01 fixed, SEC-T904-01 carries the residue | A restatement is counted once; v32's precedent | **mine** | section 1 |
| TL-T753-05 stays tracked-LOW | Needs a root refresh and the user | the orchestrator; confirmed by me | section 7 |
| SEC-T904-01, -03 in batch Y | The same surface | **mine** | section 5 |
| Merges, pipelines, ledger | As plan-197 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: one ruling, four figures.** Ids 774, accepted 46, obsolete 14 (12 + 2), open 1 and the changed set otherwise agree. The delta keeps TD-T789-01 tracked (fixed 612 + 7 + 1 = 620, tracked-LOW 100 - 7 - 2 + 2 = 93, section 5 of 94, batch Y of 4: TL-T753-05, TD-T789-01, SEC-T904-01, SEC-T904-03). **My ruling** counts TD-T789-01 as fixed (section 1), so: **fixed 621**, **tracked-LOW 92**, **section 5 of 93**, **batch Y of 3** (TL-T753-05, SEC-T904-01, SEC-T904-03). Both sets add up to 774 (621 + 46 + 14 + 1 + 92; 620 + 46 + 14 + 1 + 93). If the orchestrator prefers the delta, TD-T789-01 moves back to tracked-LOW in batch Y and the figures are the delta's.
- **Ledger.** Plan-197 § Facts: "0 active, 702 completed". Not re-counted row by row beyond the plan's figure and the five rows added in the range; the T905 row is the one active row (the plan-197 commit adds it). See section 8.
- **Plan-196 wording.** Its Outcome says TD-T789-01 is "partly" fixed with SEC-T904-01 as the residue and lists it in batch Y; the register rules the point once (section 1).

## 5. Open items by LOW batch

Carried from v32 § 5; **Y changes members** (ten ids leave, two join, one stays; size 11 to 3); all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---|---|---|
| I | Installer and generator | as v32 § 5 (includes TD-T888-01) | 25 | as v32 | as v32 |
| K | Security runtime | as v32 § 5 | 8 | as v32 | as v32 |
| L | CWSO helper scripts in emage.code | as v32 § 5 | 5 | as v32 | as v32 |
| M | CWSO repository | as v32 § 5 | 12 | as v32 | as v32 |
| N | Release tooling, second round | as v32 § 5 | 10 | as v32 | as v32 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v32 | as v32 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v32 | each release's preparation |
| R | Release-gate text, second round | as v32 § 5 | 7 | as v32 | as v32 |
| V | Release gate, fourth round | SEC-T900-02, SEC-T900-04, SEC-T900-06 | 3 | devops-engineer | the next change to `scripts/verify-release-docs.py`; at the latest before the tag's release document is gated (item 52) |
| X | CI images, the CA control, the CI locks and the pin-age check | SEC-T756-02, SEC-T881-02, SEC-T897-01 | 3 | devops-engineer | as v32 |
| **Y** | Shipped text and records | **stay:** TL-T753-05. **new:** SEC-T904-01, SEC-T904-03. **Left (fixed):** TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T780-08, TD-T789-01, TL-T819-03, SEC-T847-01. **Left (obsolete):** TL-T763-01, TL-T763-02 | 3 | technical-writer (SEC-T904-01, TL-T753-05); devops-engineer (SEC-T904-03) (my suggestion; no source names one) | TL-T753-05: the next root refresh the user approves; SEC-T904-01: the next edit of the checklist page, and at the latest before the next image bump; SEC-T904-03: the next edit of the `.gitlab-ci.yml` header |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v32 | as v32 |
| U | Live checks and user | as v32 § 5 | 6 | as v32 | as v32 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v32 | as v32 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 3 + 2 + 6 + 3 = **93** = 92 tracked-LOW + 1 open (K-20). Against v32's 101: minus 8 (batch Y from 11 to 3). **No open item carries a grade above LOW** on any scale; K-20, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v32: Y only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v32 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range.

### 6.2 Next release checklist (the release after v12.0.0)

v32 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29 and v31; item 52 with 15 points). Change:

- **Item 52, point 16 (added).** `CONTRIBUTING.md` section "Cutting a release" now carries two rules for the tag itself (TL-T761-12, TL-T819-03), which the first tag of the next release must follow and which the preparer should read: **do not move `main` between the tag and the end of `main-develop-drift-gate`** (its last line compares the tag's tree with `origin/main`; `develop` may move), and **the three tag jobs run only on the `release-gate` runner**, whose `allowed_images` must equal the digest of `python:3.12-alpine` in `.gitlab-ci.yml`, set by the user before the tag if the release changes the digest (checklist section 3). Neither is a new check; both state what the jobs already do.
- **Item 8** stays open: no tag pipeline ran in the range. Items 43, 44, 46 to 51 and points 1 to 15 of item 52: as v32.

Count: 36 numbers carried, 0 new; item 52 has 16 points.

### 6.3 Dates

Unchanged from v32 § 6.3 (the first two are at hand on 2026-11-21): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`; the range changes only comments in the `.gitlab-ci.yml` header, not that key), 2027-03-19 the last passing day.

## 7. User actions

v32 § 7 stands, unchanged:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).
- The SEC-T881-02 choice stays decided ("Keep the lock (Recommended)", 2026-11-21); nothing remains for the user on it.
- **New, a decision when the user wants it: a root refresh for TL-T753-05.** The fix is in knowledge sources, so it needs the mirrors regenerated and a root refresh, which needs the user's approval at that moment. Until then TL-T753-05 stays tracked-LOW in batch Y. Not a blocker for any release: the text is shipped text that names scripts a target lacks (K-33 in the v10.0.0 notes).

## 8. Method, limits and validation

- **Carried statuses**: v32's rows and lists, plus the sources in Based on. Plan-197 § Facts and plan-196 Outcome are the only sources for the merges (!723, !724), the pinned sha `204ee14a`, the pipelines (3097772273, 3097772199) and the clean suite (2883 OK, skipped=25). The ledger figure "0 active, 702 completed" is the plan's. No network call was made.
- **The search for changes**: every id-like token was extracted from the lines added in `9493946b..a1af3b58` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v32; the result is section 1.2 (61 distinct tokens, 3 in no register).
- **Counting**: 3 ids named new by T904; 3 counted (no duplicate), 1 closed in the MR and 2 tracked-LOW; 8 status changes into `fixed` and 2 into `obsolete` from tracked-LOW. Section 5 expands to 93 ids; the sizes of unchanged batches are v32's, not recounted id by id.
- **Still unverified**:
  - Carried from v32 § 8.
  - T904's reading (no shell; the orchestrator ran the lint, `validate-tasks`, `test_pin_bump_checklist`, `test_link_integrity`, `test_team_health*`, `scorecard --check` and `--print-drift`, taken as given).
  - The README-marker half of the TL-T761-12 text; the `ca-chain-check-python` job's `apk add` list; whether `--context` beats `DOCKER_HOST`.
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v32 § 5".
- **Not run here**: the suite, the pipelines, the mutations.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v32.md`; registers v1 to v32 (the token scan, by grep); `-v26.md`, `-v24.md`, `-v15.md` (precedents); `-v14.md`, `-v12.md` (the Y rows); `plan-197-tracked-debt-register-v33.md`; `plan-196-batch-y-shipped-text.md` (Outcome); `security-review-t904-batch-y-v1.md` (all sections, addendum); `independent-check-t763-v1.md` (TL-T763-01);
  - `git diff --shortstat`, `--stat` and `-U0` of `9493946b..a1af3b58`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
