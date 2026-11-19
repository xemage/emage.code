# Artifact: tracked-debt-register-v23.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v22.md` (729 ids; v22 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-176-tracked-debt-register-v23.md` (§ User decision, § Facts since v22, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T858.md` (the user's "v23 go"); `docs/plans/plan-175-batch-aa-opencode-and-td-t849-01.md` (§ Outcome); `docs/artifacts/security-review-t856-batch-aa-v1.md` (PASS); `docs/artifacts/mcp-agent-denials-evidence-v3.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T858 (plan-176; the user's answer of 2026-11-19, verbatim: "v23 go"). **Date**: 2026-11-19.
- **Tree read**: branch `agent/tech-lead/T858` at `b0385efe` (develop `5193e938` plus the plan-176 commit). The range for "lines added since v22" is `70a279cf..b0385efe` (plan-176 § Facts names `70a279cf..5193e938`; the one extra commit is plan-176's own plan, brief and ledger row): 58 files, 3393 lines added and 11 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range, so the search set outside them is the same 58 files and 3393 added lines (read here).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `b0385efe`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v21 only by grep. The seven raw JSON files under `docs/artifacts/mcp-agent-denials-evidence-v3/` were scanned only as added lines (section 1.2), not read. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v22.
- **Batch letters**: **AA ends** (all three ids fixed). **AB is new** (the three T856 ids, my suggestion, section 5). I shrinks by one (TD-T849-01 fixed).

## 1. Summary

v23 holds **732 ids**: the 729 of v22 and **3 new**. After v23: **555 fixed**, **46 accepted**, **10 obsolete**, **1 open**, **120 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 have no reviewer's grade (the orchestrator's ids, called LOW). The only MEDIUMs still accepted for v11.0.0 are SEC-T660-01 and SEC-T665-01 (accepted, not open).
- **Fixed since v22 (4 tracked-LOW)**: SEC-T837-02, SEC-T842-02, SEC-T844-01 (batch AA) and TD-T849-01 (batch I), by T855, confirmed by T856 (section 2.2).
- **New and tracked-LOW (3)**: SEC-T856-01, SEC-T856-02, SEC-T856-03 (T856 § 5; batch AB, my suggestion).
- **Accepted risks**: unchanged. **Next-release checklist**: item 49 restated from T856 § 4 (section 6.2). **Dates**: unchanged. **User actions**: unchanged.

Arithmetic, from the v22 totals:

| Status | v22 | leaves | enters | v23 |
|---|---:|---|---|---:|
| fixed | 551 | | + 4 tracked-LOW (SEC-T837-02, SEC-T842-02, SEC-T844-01, TD-T849-01) | **555** |
| accepted | 46 | | | **46** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 121 | - 4 fixed | + 3 new (SEC-T856-01, -02, -03) | **120** |
| **all** | **729** | | + 3 new ids | **732** |

Check: 555 + 46 + 10 + 1 + 120 = 732. Open or tracked: 120 + 1 = 121, the size of section 5.

### 1.1 Ids by v22 status and status now

| v22 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 121 | 4 | 0 | 0 | 0 | 117 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 551 | 551 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v22 ids** | **729** | **555** | **46** | **10** | **1** | **117** |
| new in v23 | 3 | 0 | 0 | 0 | 0 | 3 |
| **all v23 ids** | **732** | **555** | **46** | **10** | **1** | **120** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t856-batch-aa-v1.md` § 5: SEC-T856-01, SEC-T856-02, SEC-T856-03 | 3 | 0 | 3 |
| **All new** | **3** | **0** | **3** |

**Ids minted in the range beyond the plan's list: none.** A search of the 3393 added lines in `70a279cf..b0385efe`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<digits or T-number>…` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `L-<n>`), and separately for a bare `<PREFIX>-T<nnn>` or a template such as `-NN`, finds exactly: ADR-001, ADR-003, ADR-005, ADR-011, K-20, K-23, SEC-T660-01, SEC-T665-01, SEC-T837-01, SEC-T837-02, SEC-T840-01, SEC-T842-01, SEC-T842-02, SEC-T844-01, SEC-T856-01, SEC-T856-02, SEC-T856-03, TD-T746-01, TD-T849-01, and `UTF-8` (read here). No bare or template form occurs beyond these ids.

**Non-debt tokens.** The raw evidence JSON added in the range (`docs/artifacts/mcp-agent-denials-evidence-v3/*.json`) stores each agent's resolved rules together with its prompt text. ADR-001 and ADR-003 occur only in the Tech Lead prompt, ADR-005 only in the Context Retriever prompts, and `UTF-8` only in the PoC Orchestrator prompt (read here, by line context of the matches). They are not debt ids, and nothing in those files is read as a status change.

Set against registers v1 to v22, only SEC-T856-01, -02 and -03 are in no register (read here, by grep). Beside them:
- **Ids named with a change of status**: SEC-T837-02, SEC-T842-02, SEC-T844-01, TD-T849-01 (fixed, section 2.2).
- **Ids named with no change of status**: SEC-T660-01, SEC-T665-01 (accepted for v11.0.0; named in T856 § 4 and plan-175); SEC-T837-01, SEC-T840-01, SEC-T842-01 (fixed, as v21 and v20 record; named in the `docs/wiki/mcp-servers.md` context lines that T855 rewrote); TD-T746-01 (fixed earlier; named as the sibling of TD-T849-01); K-23 (Opencode's built-in and the user's own agents, status as v12 to v21 record it; named in T856 § 3 and § 4); K-20 (open); ADR-011 (named, not amended).
- This register mints no id.

## 2. v22 ids re-checked

Every v22 `open`, `tracked-LOW` and `accepted` id (168) is covered: the changed ones have a row here, the rest are unchanged and carried. The v22 `fixed` and `obsolete` ids stay as v22 records them.

### 2.1 v22 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). T855 and T856 observed resolved rule lists only (`opencode debug agent` on 1.19.2, evidence v3); a launched or refused subagent and a refused read were not observed (T856 § 3; `docs/wiki/mcp-servers.md`, read here). K-20 keeps them.

### 2.2 v22 `tracked-LOW` (121)

**Changed (4).**

| Id | v22 | now | Evidence and remainder |
|---|---|---|---|
| SEC-T837-02 | tracked-LOW, `SECURITY:LOW`, batch AA | **fixed** | T855 `fccdaeeb`: the supported range is stated in `implementation/PREREQUISITES.md` ("Per-platform") and `docs/wiki/mcp-servers.md`: 1.0.224 up to the latest 1.x, tested on 1.19.2, 2.x not supported (read here, both added lines). T856 § 3: **Fixed**. **Remainder (T856):** the 1.0.224 floor is source-read, not run; PREREQUISITES states it next to the range ("vendor source read at both tags; not run on 1.0.224", read here), so T856's doc condition is met |
| SEC-T844-01 | tracked-LOW, `SECURITY:LOW`, batch AA | **fixed** (rule lists) | T855 `a0fc4880`: each orchestrator gets `task: {"*": deny, "<Name>": allow, …}`, 14 names each, from its source `agents:` list; the generator refuses built-in names, wildcards and wider allows (plan-175 § Outcome; wiki, read here). T856 § 3: **Fixed** (rule lists). **Remainder (T856):** checked in the resolved rule lists only; a launch was not observed (K-20). Built-in agents and the user's own agents still get no per-agent rule (K-23, as v12 to v21 record it) |
| SEC-T842-02 | tracked-LOW, `SECURITY:LOW`, batch AA | **fixed** for the `read` tool at the default token paths | T855 `a0fc4880`: the 13 agents without `execute` get deny-only `read` patterns for any `gitlab-mcp` directory (`"gitlab-mcp"`, `"gitlab-mcp/*"`, `"*/gitlab-mcp"`, `"*/gitlab-mcp/*"`), covering the relative form of 1.19.2 and the absolute form of 1.0.224; no `read` allow is written (plan-175 § Outcome; wiki and PREREQUISITES, read here). Read here: 13 files in `.opencode/agents/` carry `bash: deny`, and 13 carry the `*/gitlab-mcp/*` pattern. T856 § 3: **Fixed** for the `read` tool. **Remainder (T856):** its residuals are tracked as SEC-T856-02 (`grep`/`glob`) and SEC-T856-03 (non-default path, symlink) (section 3) |
| TD-T849-01 | tracked-LOW (orchestrator id, called LOW), batch I | **fixed** | T855 `22a294ff`: the pid is checked against whole name fields, as in the sibling test; a forced `a<pid>b` name fails the old assertion and passes the new one (plan-175 § Outcome). Read here: `tests/functional/test_merge_task_docs.py:457` now reads `self.assertNotIn(str(os.getpid()), re.split(r"[.-]", seen["name"]), …)`. T856 § 3: **Fixed**, remainder none. The mutation run is T855's and the orchestrator's, not re-run here **(unverified)** |

**Unchanged (117 tracked-LOW; v22 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 10, Y 11, F 2, U 5 (U's sixth id is K-20, open). 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 11 + 2 + 5 = 117; with the 3 new, 120 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v22 and not recounted id by id here.)

### 2.3 v22 `accepted` (46)

**Unchanged (46)**, with their v17 qualifiers (v17 section 2.3) and v22's removal of SEC-T702-09. SEC-T660-01 is named in the range: T856 § 4 restates its Opencode scope with no change of status (section 6.2, item 49). SEC-T665-01 and K-23 are named with no change.

## 3. New ids

The grade is the reviewer's own (T856 § 5).

| Id | Grade | Short description | Status | Evidence and remediation (T856) | Batch |
|---|---|---|---|---|---|
| SEC-T856-01 | SECURITY:LOW (A05) | Scratch paths that include the local username sit in the raw JSON of evidence v2 and v3 (`external_directory` patterns), in a public repository. The username is already public as repository owner and git user, so the extra exposure is small. T856 took the exact content from its brief **(unverified)**; not re-read here | **tracked-LOW** | Do not rewrite the immutable v2/v3 files (their hashes are recorded). In future evidence runs use a neutral scratch root or redact the path to `<path>` before storing, and record the redaction | AB |
| SEC-T856-02 | SECURITY:LOW (A01) | For the 13 agents without `execute`, the `read` deny can be bypassed with `grep`, which returns content, wherever `external_directory` resolves to allow; without a broad user rule it resolves to `ask` (T856 traced vendor `grep.ts`). T856's residual (iv), no `external_directory` rules added, is part of this id | **tracked-LOW** | Docs say the `read` denies are defense in depth, not a boundary: done by the orchestrator in `docs/wiki/mcp-servers.md` (plan-175 § Outcome; read here, "these denies are defense in depth, not a boundary … (SEC-T856-02, tracked LOW)"). What remains: optionally test a deny-only `external_directory` map for `*/gitlab-mcp*` against the tool-output allow (T856 § 2.3) | AB |
| SEC-T856-03 | SECURITY:LOW (A01) | A token at a non-default path, or a symlink to it inside the project (read under the link's own path), is not denied by the `read` patterns | **tracked-LOW** | Document that only the default directory name is covered and that a token must not be linked into a project. Read here: PREREQUISITES and the wiki already say a token "kept under another path" and "a link to the token inside the project" are not covered; neither says a token must not be linked into a project, so that sentence remains | AB |

## 4. Decisions since v22

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-19 | "AA + TD-T849-01 go" | T855, T856 | T856 § Metadata |
| 2026-11-19 | "Refresh now (Recommended)" | T857 root refresh | plan-175 § Outcome; plan-176 § Facts |
| 2026-11-19 | "v23 go" | This register | plan-176 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T837-02, SEC-T842-02, SEC-T844-01, TD-T849-01 | Fixed, with T856's remainders | T856 (PASS); the orchestrator | T856 § 3; plan-175 § Outcome |
| SEC-T856-01, -02, -03 | Minted LOW, tracked under the LOW policy | T856; the orchestrator | T856 § 5; plan-175 § Outcome |
| SEC-T856-02 wiki sentence | Added before merge | the orchestrator | plan-175 § Outcome |
| Batch AA | Ends | the orchestrator; me | plan-176; section 5 |
| Batch of SEC-T856-01 to -03 | AB (new) | me (suggestion) | section 5 |
| Merges, pipelines, suite, ledger | As plan-176 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** My reading gives the same 4 ids that leave `tracked-LOW` for `fixed`, the same 3 new tracked-LOW ids, 732 ids (555 / 46 / 10 / 1 / 120) and a batch total of 121. What I add: the batch for the three new ids (AB), the non-debt tokens of section 1.2 (ADR-001, ADR-003, ADR-005, `UTF-8` in the raw evidence prompt text), and the remaining text of SEC-T856-03 (section 3).
- **The commit range.** Plan-176 § Facts names `70a279cf..5193e938`; this register searched `70a279cf..b0385efe`, which adds plan-176's own commit. The extra commit mints no id.
- **T856 § 3's "Before" column.** It gives SEC-T844-01 and SEC-T842-02 as "open"; v22 records both as tracked-LOW in batch AA (v22 section 5). The status they leave here is v22's, tracked-LOW; the end status, fixed, is the same either way.
- **Ledger.** Plan-176 § Facts: "0 active, 654 completed". Read here: `completed-tasks.md` holds 654 task rows and `active-tasks.md` one (T858, added by the plan-176 commit). No difference.
- **Agent counts.** T856 § 4 and the brief: 15 generated agents with `execute`, 13 without. Read here: 13 of the generated `.opencode/agents/*.md` files carry `bash: deny`; the 15 files T857 refreshed are those 13 plus the two orchestrators. The total of 28 is carried from v20 (not recounted here).

## 5. Open items by LOW batch

Carried from v22 § 5; I shrinks, AA ends, AB is new.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v22 § 5 **less** TD-T849-01 (fixed) | 24 | as v22 | as v22 |
| K | Security runtime | as v22 § 5 | 8 | as v22 | as v22 |
| L | CWSO helper scripts in emage.code | as v22 § 5 | 5 | as v22 | as v22 |
| M | CWSO repository | as v22 § 5 | 12 | as v22 | as v22 |
| N | Release tooling, second round | as v22 § 5 | 10 | as v22 | as v22 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v22 | as v22 |
| Q | Next release document and its gate rulings | as v22 § 5 | 5 | as v22 | as v22 |
| R | Release-gate text, second round | as v22 § 5 | 7 | as v22 | as v22 |
| V | Release gate after plans 142, 143 and 146 | as v22 § 5 | 17 | as v22 | as v22 |
| X | CI images, the CA control and runner settings | as v22 § 5 | 10 | as v22 | as v22 |
| Y | Shipped text and records | as v22 § 5 | 11 | as v22 | as v22 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v22 | as v22 |
| U | Live checks and user | as v22 § 5 | 6 | as v22 | as v22 (K-20 keeps the refused-call, launch and refused-read checks) |
| ~~AA~~ | ~~Opencode permission, second round~~ | **ended**: SEC-T837-02, SEC-T842-02, SEC-T844-01 fixed (section 2.2) | 0 | - | - |
| **AB** (new) | Opencode permission, third round: the T855 residuals and their evidence runs | SEC-T856-01, SEC-T856-02, SEC-T856-03 | 3 | devops-engineer (generator and docs; the orchestrator assigns) | the next change to the Opencode permission generator or its docs, or the next `mcp-agent-denials-evidence` run, whichever comes first; check at next-release preparation with item 49 |

Total 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 11 + 2 + 6 + 3 = **121** = 120 tracked-LOW + 1 open (K-20). Against v22's 122: I - 1, AA - 3, AB + 3. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Why AB, not Y or U.** All three ids come from one review (T856) of one change (T855) and sit on the same surface: the Opencode `read`/`grep`/`glob`/`external_directory` rules and the evidence runs that observe them. SEC-T856-02's open part is an optional generator test, which is generator work, not shipped text, so Y does not fit; SEC-T856-01 is a rule for the next evidence run, which is the same task as any re-observation of the Opencode maps. U holds live checks by the user, and none of the three needs a live call. AA ended with its last id fixed, so a new letter keeps v23's record of AA's end clean; letters are not reused (v12 Metadata).

**Order, my suggestion only.** v22 § 5 stands, with these changes: TD-T849-01 is done; in AB, SEC-T856-03's one sentence first (cheap), then SEC-T856-02's optional test, and SEC-T856-01 applies at the next evidence run.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v22 § 6.1 stand and stay the record, unchanged. **The MEDIUMs accepted for v11.0.0 only are SEC-T660-01 and SEC-T665-01**, review **2027-01-28** (token renewal). None accepted since v22. No agent accepted a risk.

### 6.2 Next release checklist (the release after v11.0.0)

v22 § 6.2 (through it v21, v20, v19, v18 and v17 § 6.2) stands, with one change in item 49:

- **Item 49 (restated from T856 § 4; narrower, not closed): SEC-T660-01's scope on Opencode for the acceptance at the next release.** It stays the user-accepted MEDIUM under ADR-011, with its review on **2027-01-28**. On Opencode, these can still read the GitLab token:
  - (a) every generated agent that holds `execute` (15), through its shell;
  - (b) Opencode's built-in agents (`build` has a shell) and agent files of the user's own (K-23);
  - (c) the two orchestrators, indirectly: since T855 they can no longer launch the built-in agents and can launch only their 14 named subagents each, but those include shell holders such as Backend Developer and DevOps Engineer;
  - (d) the 13 generated agents without `execute`: their `read` is denied for any `gitlab-mcp` directory; `grep` and `glob` on the token directory are guarded only by `external_directory` (default `ask`; `allow` under a broad user rule) (SEC-T856-02); a token at a non-default path, or a symlink to it inside the project, is not covered (SEC-T856-03).

  No fix is possible in the harness for (a) and (b). The counts stay as v20 checked them: 15 with `execute`, 13 without. v20/v21's sentence that nothing here is observed in a live call stands as v21 worded it: the rule lists are observed (evidence v3), a refused call is not (K-20). The acceptance question at item 43 uses this scope.

Count: the numbers of v22 stand; item 49 keeps its number with a narrower scope.

### 6.3 Dates

v22 § 6.3 stands unchanged; no source in the range changes a date:
- **2027-01-28**: SEC-T660-01 and SEC-T665-01 review (token renewal). Unchanged.
- **2027-01-29**: TD-T697-07 ends. Unchanged.
- **2027-03-12**: the CI image review date fails (`ci_images_reviewed_on: 2026-11-11` plus 120 days); `.gitlab-ci.yml` has no diff in the range (read here). Unchanged.

## 7. User actions

v22 § 7 stands unchanged. K-20 / A-7 stays open; the launch and refused-read checks of SEC-T844-01 and SEC-T842-02 belong to it. No new user action.

## 8. Method, limits and validation

- **Carried statuses**: v22's rows and lists, plus the sources in Based on. Plan-176 § Facts is the only source for the merges (!699, !700), the suite (2790 OK, skipped=25, at `1f0fac5c`), the pipelines (3088730937, 3088730647), the root refresh T857 (drift `[]`) and the ledger count. `docs/tasks/completed-tasks.md` holds 654 task rows and `active-tasks.md` one (T858) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 3393 lines added in `70a279cf..b0385efe` outside `tests/golden/` and `.vscode/` (there is no diff in either), and set against the text of registers v1 to v22; the result is section 1.2. Tokens inside the raw evidence prompt text were classified by line context, not by reading the files.
- **Counting**: 3 new ids, 4 status changes. Section 5 expands to 121 ids; the sizes of unchanged batches are v22's, not recounted id by id here.
- **Still unverified**:
  - Carried from v22 § 8.
  - T855's mutation runs (14 of 14 killed) and the byte-identity of the Claude Code, Cline and GitHub outputs (plan-175 § Outcome; not re-run here).
  - The orchestrator's parser comparison of the v3 raw files with the generated maps (plan-175 § Outcome).
  - SEC-T856-01's exact content (T856 took it from its brief; the raw files were not read here).
  - The orchestrator's suite and pipelines (plan-176 § Facts; not re-run here).
  - The batch membership behind "as v22 § 5".
- **Not run here**: the suite, the pipelines, the generator, Opencode.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v22.md`; `plan-176-tracked-debt-register-v23.md`; `docs/tasks/task-T858.md`; `plan-175-batch-aa-opencode-and-td-t849-01.md` (§ Outcome); `security-review-t856-batch-aa-v1.md` (§ 3, § 4, § 5, Metadata);
  - by grep or line read: `docs/wiki/mcp-servers.md` and `implementation/PREREQUISITES.md` (added lines); `tests/functional/test_merge_task_docs.py`; `.opencode/agents/*.md` (counts only); registers v1 to v22 (the token scan, item 49 of v20 and v21); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat`, `--stat` and `--name-only` of `70a279cf..b0385efe`; `git diff -U0` of the range outside `tests/golden/` and `.vscode/` (added lines only, for the token scan). `mcp-agent-denials-evidence-v3.md` was taken through plan-175 § Outcome and T856, not re-read in full.
- Decision IDs: ADR-011, ADR-015, ADR-016.
