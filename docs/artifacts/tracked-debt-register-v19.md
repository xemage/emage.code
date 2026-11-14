# Artifact: tracked-debt-register-v19.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v18.md` (711 ids; v18 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-166-tracked-debt-register-v19.md` (§ User decision, § Facts since v18, § Task Decomposition item 1) and `docs/tasks/task-T833.md` (the user's "v19 go"); `docs/plans/plan-165-batch-i-followups.md` (§ Outcome); `docs/artifacts/security-review-t832-batch-i-followups-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T833 (plan-166; the user's answer of 2026-11-14, verbatim: "v19 go"). **Date**: 2026-11-14.
- **Tree read**: branch `agent/tech-lead/T833` at `917e522c` (develop `ec06c266` plus the plan-166 commit). The range for "lines added since v18" is `198d35b1..917e522c` (plan-166 § Facts names `198d35b1..ec06c266`; the one extra commit is plan-166's own plan, brief and ledger row): 11 files, 509 lines added and 6 removed (read here). Outside the plans, briefs, the T832 review and the ledger, the changed files are `implementation/runtime/memory/context_retriever.py` (diff read line by line) and the tests `tests/functional/test_context_retriever.py` and `tests/functional/test_memory_indexing_pipeline.py` (read by diff stat only).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `917e522c`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v17 only by grep. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v18.
- **Batch letters**: no letter ends or starts. The new tracked ids go to batch I (plan-166 § Task Decomposition).

## 1. Summary

v19 holds **714 ids**: the 711 of v18 and **3 new**. After v19: **538 fixed**, **47 accepted**, **10 obsolete**, **1 open**, **118 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 still have no reviewer's grade (the orchestrator's ids, called LOW). The three new ids are `SECURITY:LOW` (T832).
- **The three MEDIUMs accepted for v11.0.0 only are unchanged** (v17 section 2.3, § 6.2 item 43): SEC-T660-01 and SEC-T665-01 (review **2027-01-28**), SEC-T702-09 (ends **2027-01-30** or at the first Brave release above 2.1.4). TD-T697-07 (MEDIUM, not shipped) ends **2027-01-29**. No source in the range names them.
- **Fixed since v18 (2 + 1 new)**: SEC-T829-01 and SEC-T829-02 by T831 (T832 PASS); SEC-T832-03, minted by T832 and fixed by the orchestrator, **not re-reviewed** (the orchestrator's ruling).
- **New and tracked-LOW (2)**: SEC-T832-01, SEC-T832-02 (batch I).
- **User actions, next-release checklist, accepted risks, dates**: unchanged from v18.

Arithmetic, from the v18 totals:

| Status | v18 | leaves | enters | v19 |
|---|---:|---|---|---:|
| fixed | 535 | | + 2 tracked-LOW (SEC-T829-01, -02) + 1 new (SEC-T832-03) | **538** |
| accepted | 47 | | | **47** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 118 | - 2 fixed | + 2 new (SEC-T832-01, -02) | **118** |
| **all** | **711** | | + 3 new ids | **714** |

Check: 538 + 47 + 10 + 1 + 118 = 714. Open or tracked: 118 + 1 = 119, the size of section 5.

### 1.1 Ids by v18 status and status now

| v18 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 118 | 2 | 0 | 0 | 0 | 116 |
| accepted | 47 | 0 | 47 | 0 | 0 | 0 |
| fixed | 535 | 535 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v18 ids** | **711** | **537** | **47** | **10** | **1** | **116** |
| new in v19 | 3 | 1 | 0 | 0 | 0 | 2 |
| **all v19 ids** | **714** | **538** | **47** | **10** | **1** | **118** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t832-batch-i-followups-v1.md`: SEC-T832-01 to -03 (statuses per plan-165 § Outcome) | 3 | 1 (-03) | 2 (-01, -02) |
| **All new** | **3** | **1** | **2** |

**Ids minted in the range beyond the plan's list: none.** A search of the 509 added lines in `198d35b1..917e522c`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<digits or T-number>…` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `M-<n>`) finds exactly: SEC-T796-01, SEC-T829-01, SEC-T829-02, SEC-T829-03, SEC-T832-01, SEC-T832-02, SEC-T832-03, and `UTF-8` (not an id) (read here). Set against registers v1 to v18, only SEC-T832-01 to -03 are in no register. Beside them:
- **Ids named with no change of status**: SEC-T796-01 (fixed in v15; T831's code comment cites its redaction), SEC-T829-03 (fixed in v18; T832 § 7: "not reviewed here; outside T831's diff").
- This register mints no id.

## 2. v18 ids re-checked

Every v18 `open`, `tracked-LOW` and `accepted` id (166) is covered: the changed ones have a row here, the rest are unchanged and carried. The v18 `fixed` and `obsolete` ids stay as v18 records them.

### 2.1 v18 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7).

### 2.2 v18 `tracked-LOW` (118)

**Changed (2).**

| Id | v18 | now | Evidence |
|---|---|---|---|
| SEC-T829-01 | tracked-LOW, `SECURITY:LOW` (A04 / A09), batch I | **fixed** | T831 (commit `ec336566` per plan-165 § Outcome; squash `8473bb26`, merge `ec06c266`): `derive_project_id` now catches `(subprocess.SubprocessError, OSError)`, so `TimeoutExpired` raises `RemoteResolutionError`; the timeout is the module constant `_GIT_TIMEOUT_S = 10` (read here in the diff of `context_retriever.py`). T832 § 1 and § 7: closed. "The tests failed without the fixes and pass with them" (plan-165 § Outcome; the developer's report, **unverified** here) |
| SEC-T829-02 | tracked-LOW, `SECURITY:LOW` (A09), batch I | **fixed** | T831: `_USERINFO_RE` now removes everything between the scheme and the **last** `@` of the URL (`^((?:[a-zA-Z][\w+.-]*://)?).*@`, `re.DOTALL`), so userinfo holding a raw `/` or `@` goes whole; it over-redacts a path holding `@` (read here). **A second leak path**, found by the developer: userinfo the parser could not separate from the path reached the id and its messages through `default_index_dir` / `RequestingContext`; it is **closed by the new refusal** of an `@` in `<org>` or `<repo>` in `normalize_remote_to_project_id` (read here). T832 § 2, § 3 and § 7: fixed "including the second `default_index_dir` / `RequestingContext` path"; the `@` refusal breaks no configuration that worked before and the pattern runs in linear time; option (a) (a fixed `detail` in `build.py`) is not required (T832 § 5) |

**Unchanged (116 tracked-LOW; v18 and earlier stay the record of their text)**: v18 § 2.2's 116 that stayed tracked and v18's 2 new tracked ids, less the two above. By batch: I 23, J 1, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 10, Y 10, F 2, U 5 (U's sixth id is K-20, open). 23 + 1 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 5 = 116; with SEC-T832-01 and -02, 118 tracked-LOW in section 5; with the 2 that leave, 118 before. (The batch sizes are carried from v18 and not recounted id by id here.) TL-T819-04 (batch I) stays tracked; no source in the range names it.

### 2.3 v18 `accepted` (47)

**Unchanged (47)**, with their v17 qualifiers (v17 section 2.3). No source in the range names an accepted id.

## 3. New ids

Grades are T832's own (T832 § 6).

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T832-01 | SECURITY:LOW (A09) | `_redacted` (`context_retriever.py:109`) removes only userinfo: the query string and fragment of a remote are printed verbatim, in the shape error and through the slug in `default_index_dir` (`:185`, `slug[:80]`). Local stderr only; that a token in a query string authenticates a git remote is doubted by T832 **(unverified)** | **tracked-LOW** | T832 § 4 and § 6; remediation: after the substitution cut the string at the first `?` or `#`, and drop the slug from the `default_index_dir` message; owner backend-developer through the orchestrator | I |
| SEC-T832-02 | SECURITY:LOW (A04) | `derive_project_id` (`context_retriever.py:142-152`) runs `git` with `text=True`; a remote that is not valid UTF-8 raises an uncaught `UnicodeDecodeError`. Contrived; fails closed | **tracked-LOW** | T832 § 6; remediation: `errors="replace"` to `subprocess.run`, or `UnicodeDecodeError` in the `except`; owner backend-developer through the orchestrator | I |
| SEC-T832-03 | SECURITY:LOW (comment accuracy; no security impact, no OWASP category) | The comment on the new `@` refusal said "git hosts allow no `@`"; plain SSH or self-hosted path remotes can hold one | **fixed** (minted and fixed in plan-165) | Fixed by the orchestrator with T832's proposed wording; **not re-reviewed: the orchestrator's ruling, comment only** (plan-165 § Outcome). Read here: the comment above `_USERINFO_LEFT_IN_PATH` now says "an id with `@` is never a valid index slug (`_INDEX_SLUG_RE`); refusing it here keeps userinfo the parser could not separate from the path (a raw `/` in it) out of the id and its messages" | — |

## 4. Decisions since v18

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-14 | "Batch I follow-ups go" | The word for T831 (SEC-T829-01, -02) and its review | `docs/tasks/completed-tasks.md`, T831 row (plan-165 itself read only at § Outcome) |
| 2026-11-14 | "v19 go" | This register | plan-166 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T832-03 | Fixed with T832's wording, comment only, not re-reviewed | the orchestrator | plan-165 § Outcome |
| SEC-T832-01, -02 | Tracked-LOW, batch I | T832 (tracked), plan-166 (batch I) | T832 § 7; plan-166 § Task Decomposition |
| Merges, pipelines, suite, ledger | As plan-166 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **The commit range.** Plan-166 § Facts names `198d35b1..ec06c266`; this register searched `198d35b1..917e522c`, which adds plan-166's own commit. The extra commit mints no id.
- **SEC-T832-03 in T832.** T832's tables list it "new, tracked-LOW" (the status as reviewed); plan-165 § Outcome and the T832 ledger row record it fixed by the orchestrator afterwards. The later source governs.
- **T832's line numbers** (`:98-99`, `:109`, `:142-152`, `:185`) are T832's, at the reviewed commit; after the orchestrator's comment fix they may have shifted **(unverified)**.

## 5. Open items by LOW batch

Carried from v18 § 5; only batch I changes.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v18 § 5; **new:** SEC-T832-01, SEC-T832-02; **left:** SEC-T829-01, SEC-T829-02 (fixed) | 25 | as v18; backend-developer for SEC-T832-01, -02 (T832) | as v18 |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v18 | as v18 |
| K | Security runtime | as v18 § 5 | 8 | as v18 | as v18 |
| L | CWSO helper scripts in emage.code | as v18 § 5 | 5 | as v18 | as v18 |
| M | CWSO repository | as v18 § 5 | 12 | as v18 | as v18 |
| N | Release tooling, second round | as v18 § 5 | 10 | as v18 | as v18 |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | as v18 | as v18 |
| Q | Next release document and its gate rulings | as v18 § 5 | 5 | as v18 | as v18 |
| R | Release-gate text, second round | as v18 § 5 | 7 | as v18 | as v18 |
| V | Release gate after plans 142, 143 and 146 | as v18 § 5 | 17 | as v18 | as v18 |
| X | CI images, the CA control and runner settings | as v18 § 5 | 10 | as v18 | as v18 |
| Y | Shipped text and records | as v18 § 5 | 10 | as v18 | as v18 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v18 | as v18 |
| U | Live checks and user | as v18 § 5 | 6 | as v18 | as v18 |

Total 25 + 1 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 6 = **119** = 118 tracked-LOW + 1 open. Against v18's 119: I - 2 + 2. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Order, my suggestion only.** v18 § 5 stands, with item 4 now reading: SEC-T832-01 and -02 with the next change to `context_retriever.py` (both are small and in the same file).

## 6. Accepted risks, next release and dates

v18 § 6 stands unchanged: since v18 no risk was accepted or changed, no checklist item enters or leaves, and no date changes.

## 7. User actions

v18 § 7 stands unchanged. K-20 / A-7 stays open.

## 8. Method, limits and validation

- **Carried statuses**: v18's rows and lists, plus the sources in Based on. Plan-166 § Facts is the only source for the merges (!689, !690), the suite (2759 OK, skipped=25) and pipelines (3068677008, 3068676985) at `0ec9a571`, and the ledger count (0 active, 629 completed before plan-166). `docs/tasks/completed-tasks.md` holds 629 task rows and `active-tasks.md` one (T833) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 509 lines added in `198d35b1..917e522c` outside `tests/golden/` and `.vscode/`, and set against the text of registers v1 to v18; the result is section 1.2.
- **Counting**: 3 new ids. Section 5 expands to 119 ids; the sizes of unchanged batches are v18's, not recounted id by id here.
- **Still unverified**:
  - Carried from v18 § 8.
  - T831's test runs (the developer's report); the orchestrator's suite and pipelines (plan-166 § Facts; not re-run here).
  - SEC-T832-01's premise that a query-string token does not authenticate a git remote (T832's own **unverified**).
  - The batch membership behind "as v18 § 5".
- **Not run here**: the suite, the pipelines, `build.py`, the context retriever.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v18.md`; `plan-166-tracked-debt-register-v19.md`; `docs/tasks/task-T833.md`; `plan-165-batch-i-followups.md` (§ Outcome); `security-review-t832-batch-i-followups-v1.md`;
  - by grep: registers v1 to v17 (the token scan); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat` and `--stat` of `198d35b1..917e522c`; `git diff -U0` of `implementation/runtime/memory/context_retriever.py`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
