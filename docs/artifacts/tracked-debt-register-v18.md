# Artifact: tracked-debt-register-v18.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v17.md` (708 ids; v17 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-164-tracked-debt-register-v18.md` (§ User decision, § Facts since v17, § Task Decomposition item 1) and `docs/tasks/task-T830.md` (the user's "Continue with the next best step"); `docs/plans/plan-163-batch-i-rsync-and-project-id.md` (§ User decision, § Facts the user reported since register v17, § Outcome); `docs/artifacts/security-review-t829-batch-i-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-014 (Q4, for A-22), ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T830 (plan-164; the user's answer of 2026-11-14, verbatim: "Continue with the next best step"; the orchestrator chose register v18). **Date**: 2026-11-14.
- **Tree read**: branch `agent/tech-lead/T830` at `d5ffed29` (develop `2decb734` plus the plan-164 commit). The range for "lines added since v17" is `8ff89e0d..d5ffed29` (plan-164 § Facts names `8ff89e0d..2decb734`; the one extra commit is plan-164's own plan, brief and ledger row): 13 files, 675 lines added and 7 removed (read here). Outside the plans, briefs, the T829 review and the ledger, the changed files are `scripts/install.sh`, `implementation/runtime/memory/build.py`, `implementation/runtime/memory/README.md` and the tests `tests/functional/test_install_equal_size_copy.py` (new) and `tests/functional/test_memory_indexing_pipeline.py` (read here by diff stat; only the `install.sh` diff was read line by line).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `d5ffed29`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v12 to v16 only by grep. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v17.
- **Batch letters**: no letter ends or starts. The batch of each new id is T829's (section 3).

## 1. Summary

v18 holds **711 ids**: the 708 of v17 and **3 new**. After v18: **535 fixed**, **47 accepted**, **10 obsolete**, **1 open**, **118 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 still have no reviewer's grade (the orchestrator's ids, called LOW). The three new ids are `SECURITY:LOW` (T829).
- **The three MEDIUMs accepted for v11.0.0 only are unchanged** (v17 section 2.3, § 6.2 item 43): SEC-T660-01 and SEC-T665-01 (review **2027-01-28**), SEC-T702-09 (ends **2027-01-30** or at the first Brave release above 2.1.4). TD-T697-07 (MEDIUM, not shipped) ends **2027-01-29**. No source in the range names them.
- **Fixed since v17 (3 + 1 new)**: TD-T774-01 (with QA-T818-01) and QA-T818-03 by T828 (T829 PASS); SEC-T780-06 on the user's report (A-22); SEC-T829-03, minted by T829 and fixed by the orchestrator, **not re-reviewed** (the orchestrator's ruling).
- **New and tracked-LOW (2)**: SEC-T829-01, SEC-T829-02 (batch I).
- **User actions**: **A-21 closed** on the user's report, and SEC-T756-02 stays LOW; **A-22 done** on the user's report (section 7).
- **Next-release checklist** (section 6.2): item 34 (A-21) and item 45 (TD-T774-01's regrade trigger) leave; the next release document may drop K-39 and M-6's check and `touch` workaround (T829 § 1).

Arithmetic, from the v17 totals:

| Status | v17 | leaves | enters | v18 |
|---|---:|---|---|---:|
| fixed | 531 | | + 3 tracked-LOW (TD-T774-01, QA-T818-03, SEC-T780-06) + 1 new (SEC-T829-03) | **535** |
| accepted | 47 | | | **47** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 119 | - 3 fixed | + 2 new (SEC-T829-01, -02) | **118** |
| **all** | **708** | | + 3 new ids | **711** |

Check: 535 + 47 + 10 + 1 + 118 = 711. Open or tracked: 118 + 1 = 119, the size of section 5.

### 1.1 Ids by v17 status and status now

| v17 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 119 | 3 | 0 | 0 | 0 | 116 |
| accepted | 47 | 0 | 47 | 0 | 0 | 0 |
| fixed | 531 | 531 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v17 ids** | **708** | **534** | **47** | **10** | **1** | **116** |
| new in v18 | 3 | 1 | 0 | 0 | 0 | 2 |
| **all v18 ids** | **711** | **535** | **47** | **10** | **1** | **118** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t829-batch-i-v1.md`: SEC-T829-01 to -03 (statuses per plan-163 § Outcome) | 3 | 1 (-03) | 2 (-01, -02) |
| **All new** | **3** | **1** | **2** |

**Ids minted in the range beyond the plan's list: none.** A search of the 675 added lines in `8ff89e0d..d5ffed29`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<digits or T-number>…` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `M-<n>`) finds exactly: A-21, A-22, K-39, M-5, M-6, QA-T818-01, QA-T818-03, SEC-T756-02, SEC-T780-06, SEC-T796-01, SEC-T820-02, SEC-T829-01, SEC-T829-02, SEC-T829-03, TD-T774-01, TL-T819-04 (read here). Set against registers v1 to v17, only SEC-T829-01 to -03 are in no register. Beside them:
- **Labels that are not debt ids**: A-21, A-22 (user actions); K-39, M-5, M-6 (the v11.0.0 release document's Known Issue and migration items).
- **Ids named with no change of status**: SEC-T796-01 (fixed in v15; T829 cites its redaction as the place of SEC-T829-02), SEC-T820-02 (fixed in v17; T829 says its residue is moot, section 2.2), TL-T819-04 (plan-163: "stays tracked"), SEC-T756-02 (stays LOW, section 2.2).
- This register mints no id.

## 2. v17 ids re-checked

Every v17 `open`, `tracked-LOW` and `accepted` id (167) is covered: the changed ones have a row here, the rest are unchanged and carried. The v17 `fixed` and `obsolete` ids stay as v17 records them.

### 2.1 v17 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7).

### 2.2 v17 `tracked-LOW` (119)

**Changed (3).**

| Id | v17 | now | Evidence |
|---|---|---|---|
| TD-T774-01 (QA-T818-01 counted with it, as in v17) | tracked-LOW, `SECURITY:LOW` (A08), batch I; regrade trigger (item 45) | **fixed** | T828 (`c9f282f9`, `f721814a`; squash `996fb2fc`, MR !688): `--checksum` in the rsync calls of `copy_tree_into` and `sync_tree_into` (`scripts/install.sh`, read here); `merge_tree_preserve_existing` (`--ignore-existing`) unchanged. Regression test `tests/functional/test_install_equal_size_copy.py`: 5 rsync subtests failed without the fix (the developer's report, **unverified** by T829 and by me). T829 § 4: "fixed … The regrade trigger (register v17 item 45) is retired … The 'three unidentified files' residue is obsolete." The orchestrator's suite (2753 OK, skipped=25) and pipelines 3068285235, 3068285300 at `fd46d4d8` (plan-164 § Facts; not re-run here) |
| QA-T818-03 | tracked-LOW, `SECURITY:LOW` (A04), batch I | **fixed** | T828: `build.py` `main` refuses, exit 2 and nothing written, a `--project-id` other than `derive_project_id(--own-repo-root)`, or any id without an `origin` remote; 6 new tests; the installer note (`scripts/install.sh`, read here) and the memory README corrected (plan-163 § Outcome). T829 § 2 and § 4: fixed. Library callers keep only the form check, which T829 accepts |
| SEC-T780-06 | tracked-LOW, `SECURITY:LOW`, batch U; user action A-22 (ADR-014 Q4) | **fixed** (on the user's report) | Plan-163 § Facts: the user deleted the `gemini` auto-approve entry in their own `.vscode/settings.json`; `grep -n -i gemini .claude/settings.json` found nothing; both files parse. I did not open either file **(unverified)** |

**Unchanged (116 tracked-LOW; v17 and earlier stay the record of their text)**: v17 § 2.2's 110 that stayed tracked and v17's 9 new tracked ids, less the three above. By batch: I 23, J 1, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 10, Y 10, F 2, U 5 (U's sixth id is K-20, open). 23 + 1 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 5 = 116; with SEC-T829-01 and -02, 118 tracked-LOW in section 5; with the 3 that leave, 119. (The batch sizes are carried from v17 and not recounted id by id here.) Notes:
- **SEC-T756-02 (batch X)** stays tracked-LOW. Its condition, A-21, is now met on the user's report (section 7): the project's only CI variable is `WIKI_TOKEN`; there are no group variables; on `gitlab-runner-16028` a `grep` for `feature_flags`, `FF_GIT_URLS_WITHOUT_TOKENS`, `tls-ca-file`, `helper_image` and `environment` in `config.toml` printed nothing; the `gitlab-runner-16027` config pasted earlier had none either (plan-163 § Facts). **Limit**: instance variables cannot be checked on gitlab.com, so that part stays **(unverified)**. Plan-164 records "SEC-T756-02 stays LOW"; it is not closed, as no source closes it.
- **TL-T761-11 (batch X)**, which "sits next to A-21", is unchanged: no source in the range names it. The user's report that `FF_GIT_URLS_WITHOUT_TOKENS` is absent bears on it; no ruling is made here.
- **TL-T819-04 (batch I)** stays tracked (plan-163 § User decision: the user's "I go" covered TD-T774-01 and QA-T818-03 only).

### 2.3 v17 `accepted` (47)

**Unchanged (47)**, with their v17 qualifiers (v17 section 2.3). No source in the range names an accepted id.

## 3. New ids

Grades are T829's own.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T829-01 | SECURITY:LOW (A04 / A09) | `derive_project_id` (`implementation/runtime/memory/context_retriever.py:128-138`, now also reached from `build.py`) does not catch `subprocess.TimeoutExpired`; fails closed with a traceback (build) or a startup crash (server). Pre-existing | **tracked-LOW** | T829 § 3 and § 4; remediation `except (subprocess.SubprocessError, OSError)` plus a test with a stub `git` that sleeps; owner backend-developer through the orchestrator | I |
| SEC-T829-02 | SECURITY:LOW (A09) | `_redacted` (`context_retriever.py:94-99`) misses userinfo with a raw `/`; the shape error then repeats the URL, now also through `build.py`'s `detail`. Pre-existing and contrived (RFC 3986 requires `/` encoded in userinfo); local stderr only. Traced by reading, not run (T829) | **tracked-LOW** | T829 § 3 and § 4; remediation (a) a fixed reason in `build.py`'s `detail`, or (b) over-redaction in `_redacted`; owner backend-developer through the orchestrator | I |
| SEC-T829-03 | SECURITY:LOW (comment accuracy; no security impact) | The new `install.sh` comment's `--dry-run` claim and cost claim were wrong | **fixed** (minted and fixed in plan-163) | Fixed by the orchestrator with T829's proposed wording; **not re-reviewed: the orchestrator's ruling** (plan-163 § Outcome). Read here: the comment above `copy_tree_into` now says "rsync's sender checksums every regular source file and the receiver its equal-size copies" and "The installer's --dry-run prints the rsync command only; rsync does not run" | — |

## 4. Decisions since v17

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-14 | "I go" | Read by the orchestrator as the word for TD-T774-01 and QA-T818-03 of batch I only, not all 25 | plan-163 § User decision |
| 2026-11-14 | (reports, not quoted) | A-21's CI-variable and runner-config facts; A-22 done | plan-163 § Facts the user reported since register v17 |
| 2026-11-14 | "Continue with the next best step" | The orchestrator chose this register | plan-164 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| Scope of "I go" | TD-T774-01 and QA-T818-03 only | the orchestrator | plan-163 § User decision |
| SEC-T829-03 | Fixed with T829's wording, comment only, not re-reviewed | the orchestrator | plan-163 § Outcome |
| SEC-T780-06, A-21, A-22 | Statuses from the user's reports | the orchestrator's record | plan-163 § Facts, § Outcome |
| Merges, pipelines, suite, ledger | As plan-164 § Facts | the orchestrator's record | section 8 |
| QA-T818-01 counted with TD-T774-01 | Kept from v17 | **mine** (v17) | section 2.2 |
| SEC-T756-02 stays tracked-LOW, not closed | No source closes it; A-21's report keeps it LOW | **mine** (status word) | section 2.2 |
| Batches of the new ids | I, as T829 proposed | T829 | section 3 |

### 4.3 Differences on the record

- **The commit range.** Plan-164 § Facts names `8ff89e0d..2decb734`; this register searched `8ff89e0d..d5ffed29`, which adds plan-164's own commit. The extra commit mints no id.
- **SEC-T829-03 in T829.** T829's tables list it "open, tracked-LOW, batch I" (the status after T828 as reviewed); plan-163 § Outcome and the T829 ledger row record it fixed by the orchestrator afterwards. The later source governs.

## 5. Open items by LOW batch

"Do first" as in v5; the flag's source stays **(unverified)** as v5 § 5 says. Batches not named as changed are carried from v17.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v17 § 5; **new:** SEC-T829-01, SEC-T829-02; **left:** TD-T774-01, QA-T818-03 (fixed) | 25 | as v17; backend-developer for SEC-T829-01, -02 (T829) | as v17; the regrade trigger is retired (item 45 leaves) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v17 | as v17 |
| K | Security runtime | as v17 § 5 | 8 | as v17 | as v17 |
| L | CWSO helper scripts in emage.code | as v17 § 5 | 5 | as v17 | as v17 |
| M | CWSO repository | as v17 § 5 | 12 | as v17 | as v17 |
| N | Release tooling, second round | as v17 § 5 | 10 | as v17 | as v17 (item 46) |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v17 |
| Q | Next release document and its gate rulings | as v17 § 5 | 5 | as v17 | the next release (items 4, 10, 43) |
| R | Release-gate text, second round | as v17 § 5 | 7 | as v17 | as v17 |
| V | Release gate after plans 142, 143 and 146 | as v17 § 5 | 17 | devops-engineer | as v17 |
| X | CI images, the CA control and runner settings | as v17 § 5 | 10 | as v17 | as v17 (item 35); **A-21 closed** |
| Y | Shipped text and records | as v17 § 5 | 10 | as v17 | as v17 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v17 | as v17 |
| U | Live checks and user | as v17 § 5; **left:** SEC-T780-06 (fixed) | 6 | the user or an authorised live session | A-2, A-7, A-11, A-15 (A-22 done) |

Total 25 + 1 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 6 = **119** = 118 tracked-LOW + 1 open. Against v17's 120: I - 2 + 2, U - 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Order, my suggestion only.**
1. Before 2027-01-28: the SEC-T660-01 and SEC-T665-01 review (item 43); decide early whether the next release comes before 2027-01-30 (Brave) or needs a new Brave record.
2. With the next tag-job image bump: `allowed_images` (item 44) and TL-T819-05.
3. QA-T818-04 before the next probe tag (item 46).
4. SEC-T829-01 and -02 with the next change to `context_retriever.py` or `build.py`.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v17 § 6.1 stand and stay the record. Since v17: none accepted, none changed. No agent accepted a risk.

### 6.2 Next release checklist (the release after v11.0.0)

v17 § 6.2 stands, with these changes:
- **Item 34 (A-21) leaves: done.** The user's report (plan-163 § Facts; section 2.2). Instance variables are not checkable on gitlab.com **(unverified)**.
- **Item 45 (TD-T774-01's regrade trigger) leaves: retired.** TD-T774-01 is fixed (T829 § 1 and § 4). **The next release document may drop K-39 and M-6's check and `touch` workaround**: the installer of the next release, which runs from the new clone, already copies with `--checksum`, so the very next `--update` uses the fixed code (T829 § 1). v11.0.0's own document keeps them, as they are correct for v11's installer (T829 § 1).
- Item 8 stays open, as in v17.

Count: 26 rules for every release, 1 open (8), and items 43, 44, 46, 47, 48 (5). With item 34 and item 45 gone, 32 numbers stand.

### 6.3 Dates

v17 § 6.3 stands. The **2027-02-19** row carried from v13 § 6.3 ("A-21 due"; SEC-T756-02's shown deadline) is met by A-21's closure and leaves.

## 7. User actions

Carried from v17 § 7, with these changes:
- **A-21: closed** (plan-163 § Facts, the user's report): the only CI variable is `WIKI_TOKEN` (Protected, Masked, Expanded); no group variables (the project is in the user's namespace); on `gitlab-runner-16028` the `config.toml` grep for `feature_flags`, `FF_GIT_URLS_WITHOUT_TOKENS`, `tls-ca-file`, `helper_image` and `environment` printed nothing; the `gitlab-runner-16027` config pasted earlier had none either. Instance variables cannot be checked on gitlab.com. SEC-T756-02 stays LOW. The report is the user's; nobody in the session read GitLab or the runner **(unverified)**.
- **A-22: done** (plan-163 § Facts, the user's report): the `gemini` auto-approve entry is gone from the user's `.vscode/settings.json`; `grep -n -i gemini .claude/settings.json` found nothing; both files parse. SEC-T780-06 fixed. I did not open the files **(unverified)**.
- **K-20 / A-7: open** (live client checks); K-15's reopen condition depends on it.
- Still open or optional as in v17: the read-deny rules (optional, not a fix; T812 point 2, K-16); SEC-T811-05 runner hardening at the next maintenance.

## 8. Method, limits and validation

- **Carried statuses**: v17's rows and lists, plus the sources in Based on. Plan-164 § Facts is the only source for the merges (!687, !688), the suite (2753 OK, skipped=25) and pipelines (3068285235, 3068285300) at `fd46d4d8`, and the ledger count (0 active, 626 completed before plan-164). `docs/tasks/completed-tasks.md` holds 626 task rows and `active-tasks.md` one (T830) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 675 lines added in `8ff89e0d..d5ffed29` outside `tests/golden/` and `.vscode/`, and set against the text of registers v1 to v17; the result is section 1.2.
- **Counting**: 3 new ids. Section 5 expands to 119 ids; the sizes of unchanged batches are v17's, not recounted id by id here.
- **Still unverified**:
  - Carried from v17 § 8.
  - The user's reports for A-21 and A-22 (GitLab, the runner and the settings files were not read); instance variables on gitlab.com.
  - T828's test runs (the developer's report; T829 ran nothing); the orchestrator's suite and pipelines (plan-164 § Facts; not re-run here).
  - SEC-T829-02's trace (T829 read it, did not run it).
  - The batch membership behind "as v17 § 5".
- **Not run here**: the suite, the pipelines, `install.sh`, `build.py`.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v17.md`; `plan-164-tracked-debt-register-v18.md`; `docs/tasks/task-T830.md`; `plan-163-batch-i-rsync-and-project-id.md`; `security-review-t829-batch-i-v1.md`;
  - by grep: registers v12 to v16 (SEC-T780-06, SEC-T756-02, A-21, A-22, items 34 and 35); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat` and `--stat` of `8ff89e0d..d5ffed29`; `git diff -U0` of `scripts/install.sh`.
- Decision IDs: ADR-011, ADR-014, ADR-015, ADR-016.
