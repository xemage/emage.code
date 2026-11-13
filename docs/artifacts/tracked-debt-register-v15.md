# Artifact: tracked-debt-register-v15.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v14.md` (680 ids; v14 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-154-tracked-debt-register-v15.md` (§ Facts since v14, § Task Decomposition) and `docs/tasks/task-T798.md` (the user's "v15 go"); `docs/plans/plan-153-context-retriever-low-residue.md` (§ Task Decomposition, § Addendum, § Outcome); `docs/artifacts/security-review-t796-context-retriever-v1.md` (FAIL); `docs/artifacts/security-review-t796-context-retriever-v2.md` (PASS); the ledger rows T795 to T797 in `docs/tasks/completed-tasks.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (only the user accepts a MEDIUM, for one release), as v14 cites it; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T798 (plan-154; the user's answer of 2026-11-12, verbatim: "v15 go"). **Date**: 2026-11-12.
- **Tree read**: branch `agent/tech-lead/T798` at `878e9df6` (develop `c7016af9` plus the plan commit, which changes only the plan, the brief and `active-tasks.md`; read here). The range for "lines added since v14" is `34f8ea7f..c7016af9`: 2 commits (the squash `2addaef4` and its merge), 14 files, 647 lines added and 14 removed. Outside the new review, plan and brief files and the ledger, the changed files are `implementation/runtime/memory/{build.py,context_retriever.py,README.md}`, `scripts/install.sh` and three test files (`test_context_retriever.py`, `test_install_robustness.py`, `test_memory_indexing_pipeline.py`). `tests/golden/`, the top-level platform folders and `.mcp.json`, `.gitlab-ci.yml`, `implementation/PREREQUISITES.md`, `implementation/knowledge/`, `CONTRIBUTING.md`, `docs/releases/` and `docs/wiki/` show no diff in the range (read here), so v14's citations into them stand. The CWSO repository was not read: every CWSO status carries over from v14.
- **Review mode**: read-only. "Unchanged" means no task, review, plan outcome or ledger row since v14 names the id with a change of status, checked by searching the lines added in `34f8ea7f..c7016af9`, outside `tests/golden/`, for every id-like token (section 8). A status taken from a review is the latest source's. "Read here" means a grep, line read or `git` query on `878e9df6`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository. Registers v1 to v10 were not re-read; v11 to v13 only by grep (the § 6.2 citations into the changed files, and the timing-test search of section 4.2). No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v14.
- **Batch letters**: **O ends** (its three ids are fixed). Z stays ended (v14). No new letter. All other v14 letters keep their scope.

## 1. Summary

v15 holds **681 ids**: the 680 of v14 and **1 new**. After v15: **508 fixed**, **49 accepted**, **9 obsolete**, **1 open**, **114 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, user; no grade). TD-T774-01 and TD-T789-01 have no reviewer's grade. The accepted MEDIUMs (SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07) are accepted, not open, and unchanged; the first three still need a fix or a new acceptance before v11.0.0 (section 6.2 item 2).
- **Plan-153 fixed batch O**: SEC-T791-02, SEC-T791-03 (T795, confirmed by T796 v1 and v2) and QA-T792-1 (T795; T796 on review; the orchestrator's re-run). **Batch O ends.**
- **Plan-153 minted SEC-T796-01** (SECURITY:LOW, blocking in T796 v1 under the gate rule) and **fixed it** (T797, confirmed by T796 v2 PASS).
- **Due before v11.0.0** (section 6.2): as v14. Item 36 gets the moved `install.sh` lines and, my suggestion, the batch O lines for the release document.
- **Not checked since v14**: SEC-T786-01's trigger (Alpine `nodejs` 24.22.3 in a `unit-tests` log) **(unverified)**; plan-154 § Facts.
- **Open for the user**: as v14. A-20, A-21 and A-22; the route of SEC-T735-06 and -07; the SEC-T762-04 questions; any batch before the next tag.

Arithmetic, from the v14 totals:

| Status | v14 | leaves | enters | v15 |
|---|---:|---|---|---:|
| fixed | 504 | | + 3 (SEC-T791-02, SEC-T791-03, QA-T792-1) + 1 new (SEC-T796-01) | **508** |
| accepted | 49 | | | **49** |
| obsolete | 9 | | | **9** |
| open | 1 | | | **1** |
| tracked-LOW | 117 | - 3 fixed | | **114** |
| **all** | **680** | | + 1 new id | **681** |

Check: 508 + 49 + 9 + 1 + 114 = 681. Open or tracked: 114 + 1 = 115, the size of section 5.

### 1.1 Ids by v14 status and status now

| v14 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 117 | 3 | 0 | 0 | 0 | 114 |
| accepted | 49 | 0 | 49 | 0 | 0 | 0 |
| fixed | 504 | 504 | 0 | 0 | 0 | 0 |
| obsolete | 9 | 0 | 0 | 9 | 0 | 0 |
| **all v14 ids** | **680** | **507** | **49** | **9** | **1** | **114** |
| new in v15 | 1 | 1 | 0 | 0 | 0 | 0 |
| **all v15 ids** | **681** | **508** | **49** | **9** | **1** | **114** |

### 1.2 New ids by source and final status

| Source | new | fixed | accepted | obsolete | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| `security-review-t796-context-retriever-v1.md` § Findings: SEC-T796-01 (fixed per `-v2.md`) | 1 | 1 | 0 | 0 | 0 | 0 |
| **All new** | **1** | **1** | **0** | **0** | **0** | **0** |

**Other ids in the added lines.** A search of the 647 lines added in `34f8ea7f..c7016af9`, outside `tests/golden/`, for `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `M-<n>`, `A-<n>`, `UA-<n>`, `O-<n>` and `BLK-` tokens, and for any `<CAPS>-<digits>` token, finds only: SEC-T791-02, SEC-T791-03, QA-T792-1 (v14 ids; section 2); SEC-T796-01 (new; section 3); **SEC-009** (cited in T796 v1 point 4 and plan-153 as the reason for the existing `%q` quoting; no change of status, as in v14); and **O-1, O-2** (T796 v2's observations; section 3.1). No blocker record id and nothing else is minted. This register mints no id.

## 2. v14 ids re-checked

Every v14 `open`, `tracked-LOW` and `accepted` id (167) has a row or a list entry here: 1 + 117 + 49. The v14 `fixed` and `obsolete` ids stay as v14 records them.

### 2.1 v14 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range names it.

### 2.2 v14 `tracked-LOW` (117)

**Changed (3).**

| Id | v14 | now | Evidence |
|---|---|---|---|
| SEC-T791-02 | tracked-LOW, SECURITY:LOW (A09), batch O | **fixed** | T795 (commits `d480c31d`, `344691b8`, `15e427ba`; plan-153 § Outcome): `foreign_project_paths` and `_warn_project_id_mismatches` warn on stderr, by path only, for every own-repo project-scope entry whose `project_id` is not `--project-id`; the case-only wording is kept; entries stay indexed; `scope_filter.py` unchanged. T796 v1 § Status: "fixed" (the two lists cover every inequality exactly once; both the write and the check path warn). T796 v2: unchanged. Now `build.py:113` `case_mismatched_paths`, `:125` `foreign_project_paths`, `:282` `_warn_project_id_mismatches`, called at `:276` and `:308`; `scope_filter.py` has no diff in the range (read here). Ledger T795, T796 |
| SEC-T791-03 | tracked-LOW, SECURITY:LOW (A03), batch O | **fixed** | T795: `is_derived_project_id` returns False for a non-string and for `.`/`..` segments; `normalize_remote_to_project_id` refuses a `.`/`..` org or repo with `RemoteResolutionError`, so the server does not start (default) or every `retrieve` fails (with `--index-dir`); both fail closed (plan-153 § Outcome; T796 v1 point 3). T796 v1 § Status: "fixed"; v2: unchanged. Now `context_retriever.py:149` `is_derived_project_id`, the refusal message at `:119` (read here; T796 v1 cites `:144-147` and `:108-109` at `15e427ba`, before T797 added the helper). Ledger T795, T796 |
| QA-T792-1 | tracked-LOW, QA Low, batch O | **fixed** | T795: the printed build command starts with `source .venv-mcp/bin/activate &&`. T796 v1 § Status: "fixed on review", with the test of the negative case (no venv, no fallback to the system `python3`). The orchestrator re-ran the printed lines, each in its own shell, in a temporary target: the build line ran `.venv-mcp/bin/python3`, the old one `/usr/bin/python3`; the `pip install` of fastembed was not run, so the build stopped at the missing `yaml` (plan-153 § Outcome; plan-153 § Task Decomposition item 3 gave the re-run to the orchestrator, no QA task). The build line is now `scripts/install.sh:1739`, after the venv line at `:1735` and the comment at `:1737-1738` (read here). Ledger T795 |

**Unchanged (114 tracked-LOW; v14 and earlier stay the record of their text)**: the 112 ids of v14 § 2.2's "Unchanged" table, by batch (I 23, J 1, K 7, L 5, M 12, N 8, P 1, Q 9, R 4, S 1, V 15, X 10, Y 8, F 2, U 6), and the two v14 new ids that did not change, **TD-T789-01** (Y) and **SEC-T791-01** (Q). No other v14 tracked-LOW id occurs in the added lines (section 8). 112 + 2 = 114; with the 3 changed, 117. **SEC-T786-01's closing trigger was not checked** in the range (plan-154 § Facts; **(unverified)**); it stays tracked-LOW and its check stays at v11.0.0 preparation (item 37).

### 2.3 v14 `accepted` (49)

**Unchanged (49)**; no source in the range names any of them, and none has a new acceptance. As v14 § 2.3 (and through it v13 § 2.3): the five rows with their qualifiers (SEC-T660-01, SEC-T665-01 and SEC-T702-09 accepted MEDIUM for v10.0.0 only; SEC-T657-01 / SEC-T658-01, counted as one, and K-15 close by removal at v11.0.0 unless the Opencode live check fails); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; the orchestrator-accepted residues TL-T773-01, TL-T780-01, TL-T780-07. 5 + 1 + 40 + 3 = 49.

## 3. New ids

Grades are the reviewers' own. "Read here" means a line read on `878e9df6`.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T796-01 | SECURITY:LOW (A09) on its own; **blocking** in T796 v1 under § Security Gate Protocol item 2, as a required § Logging control ("DO NOT log: passwords, tokens") left out of code under review | The `RemoteResolutionError` messages of `normalize_remote_to_project_id`, T795's new one included, repeated the remote URL with any `user:token@` part (an HTTPS remote with a personal access token, a CI checkout remote) | **fixed** | T796 v1 § Findings and § Blockers. T797 (commit `47e56c56`, which changes only `context_retriever.py` and `test_context_retriever.py`; read here): `_redacted()` replaces the userinfo with `***@` before the 200-character cut, in all three messages (plan-153 § Outcome). T796 v2 § Status: "fixed"; § Answers 1 to 3: userinfo the parser accepts reaches no message; the greedy regex covers it; limits (a) and (b) acceptable with no grade. Now `context_retriever.py:94` `_USERINFO_RE`, `:97-99` `_redacted`, used at `:112`, `:116`, `:119` (read here). Ledger T796, T797 | — (minted and fixed in plan-153) |

### 3.1 T796 v2's observations O-1 and O-2

**Recorded here as observations, with no id and no batch.** T796 v2 gives them "no grade, no action required": **O-1** (a malformed URL with a raw `/` in the password can put part of it into the slug message at `context_retriever.py:172`, cut to 80 characters) and **O-2** (a query string in the remote reaches the same message). The reviewer states that git and curl cannot authenticate with either URL, so no working credential is at stake, and that O-1 is not a regression (the same text could appear before T795 and T797). A debt id needs a finding or an owner's decision to track work; neither exists, and this register mints no id. The one hardening the reviewer names (show only the refusal reason at `:172`, without the slug) is recorded so that a later change of that message can take it up; whether to do it is the orchestrator's call, not a tracked item. They are not T789's O-1 and O-2, which are parts of TD-T789-01 in batch Y; cite them as "T796 v2 O-1/O-2".

## 4. Decisions since v14

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-12 | "O go" | Plan-153 (batch O, T795 to T797). The reading as batch O is the orchestrator's (section 4.2) | plan-153 Based on; plan-154 § Facts; ledger T795 |
| 2026-11-12 | "v15 go" | Plan-154, T798, this register | plan-154 Based on; task-T798 |

**Still unruled, for the user (SEC-T762-04, with TL-T761-10):** as v12 § 4.1 (section 6.2, item 33). **No ruling was asked of the user on SEC-T796-01** (section 4.2).

### 4.2 The orchestrator's rulings (not the user's)

| Item | Decision | Source | Effect |
|---|---|---|---|
| SEC-T796-01's route | Routed to a fix (T797) instead of asking the user or the orchestrator to rule whether an exception message is "logging" under § Logging. T796 v1 had left that ruling open: under it the verdict would have been PASS with SEC-T796-01 as tracked-LOW debt | plan-153 § Addendum | The question stays unruled; it no longer matters for this code, as v2 finds no credential in any message. SEC-T796-01 is fixed, not debt |
| QA-T792-1's check | No separate QA task; the orchestrator re-ran the printed lines itself | plan-153 § Task Decomposition item 3, § Outcome | The fix rests on T796's review plus that re-run (section 2.2). The build itself was not run to completion in the re-run (fastembed not installed) |
| The reading of "O go" | The word for batch O as v14 defines it; not approval of a release, a tag or a root refresh | plan-153 Based on; plan-154 § Facts | Plan-153. No root refresh was needed: `--print-drift` gave `[]` (plan-154 § Facts) |
| The timing-test failure | An observation, not an id: one clean-suite run at the superseded `15e427ba` failed `test_scaling_and_throughput` (`verify-throughput` cv 0.416 > 0.350) while another full suite ran on the same host; run alone it passed 3 of 3 (cv 0.03 to 0.07); the final run at `6bcccd68` had no failure | plan-154 § Facts | **My answer: no existing id holds it.** The registers' only flaky-test id, TD-T746-01 (batch W), is a different test (`test_merge_mcp_json_robustness.py`, a temp-file name) and was fixed by T754 (v12). A grep of v10 to v14 for `throughput`, `scaling`, `cv` and `flaky` finds nothing else about this test (read here). The threshold is `max_coefficient_of_variation: 0.35` in `tests/_baselines/benchmark-thresholds-v1.json:19`, and the method is `test_scaling_and_throughput_envelope` in `tests/performance/test_scaling_and_throughput.py:97` (read here; the plan names the module). I agree it stays an observation: a coefficient-of-variation gate fails under a concurrent full suite by design, and no failure is recorded on a quiet host or in a pipeline. My suggestion: mint an id if it fails once with no other load on the host, or in a pipeline job |
| SEC-T796-01 without a batch | **Mine**: minted and fixed inside plan-153, so it enters as `fixed` and never sat in a batch | this register | sections 1.2, 3 |

### 4.3 Differences on the record

These stay as the sources state them.
- **Line numbers in T796 v1.** T796 v1 read `15e427ba`; T797 then added `_USERINFO_RE` and `_redacted` above the cited lines, so `is_derived_project_id` moved from `:144` to `:149` and the refusal from `:109` to `:119`. A shift, not a conflict; section 2.2 gives both.
- **T796 v2's unverified point "that `a5da3106` adds only docs"** is settled here: `git diff 47e56c56 a5da3106` and `a5da3106 6bcccd68` touch only the T796 review artifacts, plan-153, the ledger and the briefs T795 to T797; `47e56c56` is an ancestor of `a5da3106`, which is an ancestor of `6bcccd68`, and the tree of `6bcccd68` equals the squash `2addaef4` (read here).
- **Plan-153 § Outcome** says "The orchestrator's checks: see the merge request"; plan-154 § Facts gives their results (section 8).

## 5. Open items by LOW batch

"Do first" as in v5; the flag's source stays **(unverified)** as v5 § 5 says. All batches except O are carried from v14 without change. **O ends.** Z stays ended and is dropped from the table.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v14 § 5 | 23 | as v14 | as v14. **TD-T774-01 needs a grade first** (my suggestion) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v14 | as v14 |
| K | Security runtime | as v14 § 5 | 7 | as v14 | as v14 |
| L | CWSO helper scripts in emage.code | as v14 § 5 | 5 | as v14 | as v14 |
| M | CWSO repository | as v14 § 5 | 12 | as v14 | as v14 |
| N | Release tooling, second round | as v14 § 5 | 8 | as v14 | as v14; the release scripts have no diff since v14 |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v14 |
| Q | Next release document and its gate rulings | as v14 § 5 (with SEC-T791-01) | 10 | as v14 | **the v11.0.0 release** (items 2, 4, 10, 31, 33, 36, 38, 39) |
| R | Release-gate text, second round | as v14 § 5 | 4 | orchestrator routes each | **the route of SEC-T735-06 and -07 is still to be settled before batch R** |
| S | Release gate: the runner tag | SEC-T741-17 (the rest) | 1 | the user (A-20) | waits on the user's runner |
| V | Release gate after plans 142, 143 and 146 | as v14 § 5 | 15 | devops-engineer | **open, for the user**: no source binds V to a release; SEC-T751-06 first (v11's suggestion) |
| X | CI images, the CA control and runner settings | as v14 § 5 | 10 | as v14 | as v14 (item 37 for SEC-T786-01, whose trigger is unchecked since T786; A-21; item 35) |
| Y | Shipped text and records | as v14 § 5 (with TD-T789-01) | 9 | as v14 | as v14 |
| O | `context-retriever` after T790: LOW residue | **Ended.** SEC-T791-02, SEC-T791-03, QA-T792-1 fixed (T795; T796 v1, v2; the orchestrator's re-run) | 0 | — | — |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v14 | as v14 |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06, SEC-T780-06 | 7 | the user or an authorised live session | A-2, A-7, A-11, A-15, A-22 |

Total 23 + 1 + 7 + 5 + 12 + 8 + 1 + 10 + 4 + 1 + 15 + 10 + 9 + 0 + 2 + 7 = 115 = 114 tracked-LOW + 1 open. **No open item carries a grade above LOW** on any scale; K-20, TD-T774-01 and TD-T789-01 have no grade.

**Order, my suggestion only.** v14's item 2 (batch O) is done.
1. At v11.0.0 preparation: Q, with SEC-T784-01 and SEC-T791-01, in the release document; item 2's ADR-011 re-acceptances; X's SEC-T786-01 check (item 37).
2. Y's TD-T789-01, at the next edit of the checklist page (at the latest the next image bump).
3. V's SEC-T751-06, as v11 suggests.
4. I's TD-T774-01, once graded.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v14 § 6.1 stand and stay the record. Nothing new since v14: plan-153 accepted no risk (SEC-T796-01 was fixed, not accepted). The MEDIUM end dates are as v12 § 6.1.

### 6.2 Next release checklist (v11.0.0, MAJOR)

Carried from v14 § 6.2, with its numbers. **Only item 36 changes.** Items not named here keep v14's text (and, through v14, v13's and v12's).

**Citations re-read.** In the range, `scripts/install.sh` changed in one hunk at `:1734` (two lines added in `print_memory_index_notice`), and `implementation/runtime/memory/` changed in `build.py` (first hunk at `:88`), `context_retriever.py` and `README.md` (read here). The § 6.2 citations into these files:
- `install.sh` in items 4, 13 and 31 (through v12/v13): `:187` the Cursor error, `:1300` the gate comment, `:1301` the `.cursor/mcp.json` advice, `:1305` the pointer, the Pi notice ending `:1327`, the Gemini notice ending `:1351`. All lie before `:1734` and **stand** (read here). v11 § 6.2's `install.sh` citations sit in items 4 and 13, which v12 replaced (one grep each of v11 to v13 § 6.2, read here).
- `install.sh` in item 36: `:1737-1739` for the build lines. **Moved** to `:1739-1741` (the comment now at `:1737-1738`); see item 36.
- `build.py:12` in v12 item 19 (the audit's remark, which v12 calls wrong): before the first hunk, the CLI docstring is unchanged; **stands**.
- No item cites `context_retriever.py` or the memory `README.md`.
`.gitlab-ci.yml`, `implementation/PREREQUISITES.md` and `docs/wiki/` did not change, so items 14, 19, 21, 23, 35 and 38 stand.

36. **Changed (citation; and, my suggestion, the batch O lines).** As v14, with two changes:
    - The cited `install.sh:1745-1747` in v10.0.0 M-2, which v14 mapped to `:1737-1739`, is now `:1739-1741`; the new document cites the current lines (read here).
    - **Where the release document reports batch O and T795's behaviour changes: here**, under the same "what the release document reports as fixed" heading as K-35 and M-2, because no open id is left for them and batch Q holds only open ids. No source requires these lines; they are my suggestion for release-manager. (a) The printed build line now activates `.venv-mcp` first, so the printed lines also work run one by one (QA-T792-1). (b) The build now names on stderr, by path only, every own-repo project-scope entry whose `project_id` is not `--project-id`, not only a case-only difference (SEC-T791-02). (c) A workspace whose `origin` remote has `.` or `..` as its `<org>` or `<repo>` gets no project id: the server does not start (default) or every `retrieve` fails (with `--index-dir`), and `--project-id` refuses such an id (SEC-T791-03). Whether any real host allows such a project path is **(unverified)**; (c) is a behaviour change, so it may also need a migration line if one is found. (d) Refusal messages no longer repeat a remote's userinfo (SEC-T796-01). The memory `README.md` already states (a) to (c), (c) for the default path only (`implementation/runtime/memory/README.md:61-70`, read here).

### 6.3 Dates

Carried from v14 § 6.3 unchanged. No source in the range changes a row; `.gitlab-ci.yml` has no diff, so `ci_images_reviewed_on: 2026-11-11` and its failing day **2027-03-12** stand (last passing day 2027-03-11).

## 7. User actions

Carried from v14 § 7 unchanged. No source in the range names a user action. **A-21 is still open** (as v14). A-22's state is still **(unverified)**: the two settings files were not opened.

## 8. Method, limits and validation

- **Carried statuses**: v14's rows and lists, plus the sources in Based on. Plan-154 § Facts is the only source for the merges (!672, !673), their pipelines and suite runs, the user's words, the timing-test observation and the ledger count (0 active, 594 completed after !673). `docs/tasks/completed-tasks.md` holds 594 task rows, and `active-tasks.md` holds only T798 (read here). No network call was made.
- **The search for changes**: a script extracted every id-like token from the 647 lines added in `34f8ea7f..c7016af9` outside `tests/golden/` (patterns as in section 1.2, plus any `<CAPS>-<digits>` token). The only tokens are SEC-T791-02, SEC-T791-03, QA-T792-1, SEC-T796-01, SEC-009, O-1 and O-2 (and `UTF-8`). Each hit was read in context. As every other v14 id is absent from the added lines, no other status can have changed through a source in the range.
- **Counting**: 1 new id, from T796 v1 § Findings. Section 5 expands to 115 distinct ids: the 114 tracked-LOW ids that remain and the 1 open id.
- **What real jobs and runs proved.** Source: plan-154 § Facts and plan-153 § Outcome. I read no job log and ran no pipeline.
  - MR !672 at `0d78e1da`: pipeline 3058912821 green; full suite in a clean worktree 2719 OK (skipped=25).
  - MR !673 at `6bcccd68`: pipeline 3060303820 green; full suite in a clean worktree 2731 OK (skipped=25); `--print-drift` `[]`.
  - The clean-suite run at the superseded `15e427ba` with one timing failure, and the three solo runs of that test (section 4.2).
  - The orchestrator's re-run of QA-T792-1's printed lines in a temporary target (section 2.2).
- **What GitLab's APIs proved.** Nothing new in the range; none is cited by plan-153 or plan-154 beyond the pipeline results above, and how those were read is not recorded **(unverified)**.
- **What is reading only**:
  - T796 v1 and v2 in full ("no file modified, no command run"; each § Method and limits; the tests were read, not run);
  - my line reads, greps and `git` queries (sections 2, 3, 4.3, 6.2).
- **Dropped from the unverified list**:
  - T796 v2: "that `a5da3106` adds only docs" (section 4.3) and "the full diff of `47e56c56`" (its stat: `context_retriever.py` and its test only; read here, the diff body not reviewed by me).
  - T796 v1: "whether a top-level folder or `tests/golden/` changed": neither has a diff in the range (read here).
  - T796 v1 and v2: "that the suite, the drift gates and the pipeline pass": plan-154 § Facts (the orchestrator's runs; not run here).
  - T796 v1 and v2: QA-T792-1's re-run: done by the orchestrator (plan-153 § Outcome).
- **Still unverified**:
  - Carried from v14 § 8.
  - SEC-T786-01's trigger, unchecked since T786 (plan-154 § Facts).
  - New, from T796 v1 § Method and limits: whether `implementation/PREREQUISITES.md` or `docs/wiki/mcp-servers.md` needed a correction (neither changed in the range; a grep of both for `memory.build`, `letter case`, `case-only` and `.venv-mcp` finds only the security runtime's own venv line at `docs/wiki/mcp-servers.md:206`, read here, so I found no false wording, but did not read either file in full); how the `mcp` SDK shows a tool exception to the client (v2: no longer matters for credentials).
  - New, from this register: whether any real git host allows `.` or `..` as a project path (section 6.2 item 36 (c)); the full build in QA-T792-1's re-run (stopped at the missing `yaml`, plan-153 § Outcome).
- **Not run here**: the suite and the pipelines, which the orchestrator ran before each merge. No mutation and no full suite ran for this register.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v14.md`; `plan-154-tracked-debt-register-v15.md`; `docs/tasks/task-T798.md`; `plan-153-context-retriever-low-residue.md`; `security-review-t796-context-retriever-v1.md`; `security-review-t796-context-retriever-v2.md`; `docs/tasks/completed-tasks.md` rows T795 to T797;
  - by grep or line range: `scripts/install.sh`, `implementation/runtime/memory/build.py`, `implementation/runtime/memory/context_retriever.py`, `implementation/runtime/memory/README.md`, `implementation/PREREQUISITES.md` and `docs/wiki/mcp-servers.md` (one grep), `tests/_baselines/benchmark-thresholds-v1.json`, `tests/performance/test_scaling_and_throughput.py`, v11 to v13 § 6.2 (one grep each), v10 to v14 (one grep for the timing test);
  - `git diff 34f8ea7f c7016af9`; `git diff --stat` and `git merge-base --is-ancestor` for `47e56c56`, `a5da3106`, `6bcccd68`, `2addaef4`.
- Decision IDs: ADR-011.
