# Artifact: tracked-debt-register-v21.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v20.md` (725 ids; v20 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-171-tracked-debt-register-v21.md` (§ User decision, § Facts since v20, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T848.md` (the user's "v21 go"); `docs/plans/plan-170-sec-t837-01-opencode-live-check.md` (§ Outcome); `docs/artifacts/mcp-agent-denials-evidence-v2.md` (§ 4, § 5); `docs/artifacts/security-review-t847-opencode-live-v1.md` (§ Per-finding statuses, § Rulings on the observations, § Findings, verdict PASS). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T848 (plan-171; the user's answer of 2026-11-19, verbatim: "v21 go"). **Date**: 2026-11-19.
- **Tree read**: branch `agent/tech-lead/T848` at `b26aaf92` (develop `a6732334` plus the plan-171 commit). The range for "lines added since v20" is `c764005a..b26aaf92` (plan-171 § Facts names `c764005a..a6732334`; the one extra commit is plan-171's own plan, brief and ledger row): 15 files, 2415 lines added and 1 removed (read here). `tests/golden/`, `.vscode/` and `.gitlab-ci.yml` have no diff in the range (read here).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `b26aaf92`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. The raw `raw-*.json` files of evidence v2 only through the token scan of the added lines (section 1.2). Registers v1 to v19 only by grep. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v20.
- **Batch letters**: no batch ends and none is new. U shrinks by one (SEC-T837-01 fixed); Y grows by one (SEC-T847-01, my suggestion, section 5).

## 1. Summary

v21 holds **726 ids**: the 725 of v20 and **1 new**. After v21: **548 fixed**, **47 accepted**, **10 obsolete**, **1 open**, **120 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 still have no reviewer's grade (the orchestrator's ids, called LOW). The new id SEC-T847-01 is `SECURITY:LOW` (T847).
- **Fixed since v20 (1 tracked-LOW)**: SEC-T837-01 by T846 (evidence v2; T847 PASS: "**Fixed** by T846 (evidence v2)"). Its refused-call part stays under K-20.
- **New and tracked-LOW (1)**: SEC-T847-01 (batch Y, my suggestion).
- **Live-run notes narrowed, no status change**: SEC-T663-02, SEC-T837-03, SEC-T840-01, SEC-T842-01 (section 2.4). **SEC-T663-03**: T847's note, no status change (section 2.4).
- **The three MEDIUMs accepted for v11.0.0 only keep their status and dates** (v17 section 2.3, § 6.2 item 43): SEC-T660-01 and SEC-T665-01 (review **2027-01-28**), SEC-T702-09 (ends **2027-01-30** or at the first Brave release above 2.1.4). TD-T697-07 (MEDIUM, not shipped) ends **2027-01-29**.
- **User actions and accepted risks**: unchanged from v20. **Next-release checklist**: item 49's live-run wording is updated (section 6.2); no item enters or leaves. **Dates**: unchanged.

Arithmetic, from the v20 totals:

| Status | v20 | leaves | enters | v21 |
|---|---:|---|---|---:|
| fixed | 547 | | + 1 tracked-LOW (SEC-T837-01) | **548** |
| accepted | 47 | | | **47** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 120 | - 1 fixed (SEC-T837-01) | + 1 new (SEC-T847-01) | **120** |
| **all** | **725** | | + 1 new id | **726** |

Check: 548 + 47 + 10 + 1 + 120 = 726. Open or tracked: 120 + 1 = 121, the size of section 5.

### 1.1 Ids by v20 status and status now

| v20 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 120 | 1 | 0 | 0 | 0 | 119 |
| accepted | 47 | 0 | 47 | 0 | 0 | 0 |
| fixed | 547 | 547 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v20 ids** | **725** | **548** | **47** | **10** | **1** | **119** |
| new in v21 | 1 | 0 | 0 | 0 | 0 | 1 |
| **all v21 ids** | **726** | **548** | **47** | **10** | **1** | **120** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t847-opencode-live-v1.md`: SEC-T847-01 | 1 | 0 | 1 |
| **All new** | **1** | **0** | **1** |

**Ids minted in the range beyond the plan's list: none.** A search of the 2415 added lines in `c764005a..b26aaf92`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<digits or T-number>…` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `M-<n>`) finds exactly: AC-1, ADR-001, ADR-003, ADR-005, K-20, SEC-T660-02, SEC-T663-02, SEC-T663-03, SEC-T837-01, SEC-T837-02, SEC-T837-03, SEC-T840-01, SEC-T842-01, SEC-T847-01, TC-001, TC-002 (read here). AC-1, ADR-001, ADR-003, ADR-005, TC-001 and TC-002 occur only in agent prompt text copied into the raw `opencode debug agent` output of evidence v2 (`raw-*.json`; template examples, not debt ids) (read here). Set against registers v1 to v20, only SEC-T847-01 is in no register. Beside it:
- **Ids named with a change of status**: SEC-T837-01 (fixed, section 2.2).
- **Ids named with no change of status**: SEC-T663-02, SEC-T837-03, SEC-T840-01, SEC-T842-01 (fixed; live-run notes narrowed, section 2.4); SEC-T663-03 (as its register records it; T847's note, section 2.4); SEC-T837-02 (tracked-LOW, batch AA; named by T847 as out of scope, Opencode 2.x); SEC-T660-02 (named in evidence v2 § 3 as the reason for T688's removal of `gitlab_get_pipeline_job_output`; status as its register records it); K-20 (open; the refused-call check).
- This register mints no id.

## 2. v20 ids re-checked

Every v20 `open`, `tracked-LOW` and `accepted` id (168) is covered: the changed ones have a row here, the rest are unchanged and carried. The v20 `fixed` and `obsolete` ids stay as v20 records them, with the notes of section 2.4.

### 2.1 v20 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). A refused tool call on Opencode is still not observed (T847; evidence v2 § 5).

### 2.2 v20 `tracked-LOW` (120)

**Changed (1).**

| Id | v20 | now | Evidence |
|---|---|---|---|
| SEC-T837-01 | tracked-LOW, `SECURITY:LOW` (A05), batch U | **fixed** | T846 (commit `eb77fa28`; MR !695, develop `a6732334`, per plan-171 § Facts): `docs/artifacts/mcp-agent-denials-evidence-v2.md`, `opencode debug agent` on opencode-ai 1.19.2 for Tech Lead, QA Engineer, Demo Agent, Orchestrator and Context Retriever; each resolved agent segment equals the generated `permission:` map in names, actions and order; every difference from v1 attributed, none widens access (plan-170 § Outcome). T847 PASS: "**Fixed** by T846 (evidence v2)… The refused-call part stays under K-20." The equality of the indexed lists with the raw files rests on T846's and the orchestrator's scripts; T847 did not re-check it, nor did I **(unverified)** |

**Unchanged (119 tracked-LOW; v20 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 10, Y 10, F 2, U 5 (U's sixth id is K-20, open), AA 3. 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 5 + 3 = 119; with the 1 new, 120 tracked-LOW in section 5; with the 1 that leaves, 120 before. (The batch sizes are carried from v20 and not recounted id by id here.)

### 2.3 v20 `accepted` (47)

**Unchanged (47)**, with their v17 qualifiers (v17 section 2.3). No accepted id is named in the range.

### 2.4 Notes on fixed and registered ids (no status change)

**Narrowed live-run notes (T847 § Per-finding statuses).** For SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01, "live **unverified**" in v20 (sections 2.2 and 3) now reads, in T847's words: "resolved rule list observed on opencode-ai 1.19.2 (evidence v2); a refused tool call is not observed (K-20)". Still **unverified**: how 1.19.2 maps `bash`, `edit`, `webfetch`, `websearch` and `task` onto its tools at call time; and the 23 agents that were not run, which rest on the generator.

| Id | Status (unchanged) | T847's narrowed note, per row |
|---|---|---|
| SEC-T663-02 | fixed (T836) | Observed: 1.19.2 resolves the frontmatter `permission:` map into the same ordered rules, for five agents. A refused call: not observed (K-20) |
| SEC-T837-03 | fixed (T839) | Observed for the five agents: no agent segment holds a `read` rule, so the last generated `read` rules are the built-in `*.env` / `*.env.*` ask rules and `*.env.example` allow. T847's caveats: **it did not re-review T839's fix itself**; in the test the hostile user rule `*: allow` (#12) re-allows `.env` reads, from the user's own configuration, not the generated files; its reading of how `*` matches a path is **(unverified)**; the other 23 agents rest on the generator (not observed) |
| SEC-T840-01 | fixed (T841, T843); never accepted | Observed for rule resolution: `bash: deny` (Demo Agent, Context Retriever) and `edit`, `webfetch`, `websearch` deny (Context Retriever), each the last match. Not lifted: the call-time mapping of those names (for example whether `edit` also governs write and patch) **(unverified)**; a refused call (K-20). The read-only roles that motivated the finding (security-engineer, product-owner, scrum-master) were not run (not observed) |
| SEC-T842-01 | fixed (T843); never accepted | Observed for rule resolution: `task: deny` is the last match for Tech Lead, QA Engineer, Demo Agent and Context Retriever; the Orchestrator has no `task` entry, as intended. Not lifted: that `task` governs the subagent-launch tool at call time **(unverified)**; a refused `task` call (K-20) |

**SEC-T663-03 (T847 § Rulings, observation 1; no change of status, no new finding).** T847's note, recorded here: "v2 (T846): the global-configuration placement is observed unchanged for the `permission:` form; the v1 merge-tool example now resolves to deny (fails closed, by reading); held named tools are still overridden; the agent-block and `OPENCODE_CONFIG_CONTENT` runs were not repeated." The deny for `gitlab_merge_merge_request` is computed by last-match reading, not run **(unverified)**.

## 3. New ids

The grade is the reviewer's own.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T847-01 | SECURITY:LOW (A05) | Evidence v1 (`mcp-agent-denials-evidence-v1.md`, lines 94, 188, 255, T847's line numbers) says an unmatched name "would match no rule and depend on the default behaviour, ask in the current core". On opencode-ai 1.19.2 built-in rule 0 is `*: allow` (in v1's and v2's resolved lists alike), so such a name resolves to allow. The affected names are the exempt servers, allowed by the user's decision (`denyUnlessGranted: false`, 2026-10-16); no generated control depends on the claim | **tracked-LOW** | T847 § Findings; remediation: v1 is immutable, so record in register v21, and next to the wiki's evidence links, that evidence v2 § 4 supersedes v1 on this point: "rule 0 is a built-in `*: allow`; a name with no later rule resolves to allow on 1.19.2". Owner: technical-writer or devops-engineer (T847). **The register part is done here (this row).** The wiki pointer is still to do: `docs/wiki/mcp-servers.md` names neither SEC-T847 nor rule 0 at `b26aaf92` (read here), so the id stays tracked-LOW. Evidence v2 § 4 itself notes that how Opencode treats a name with no rule beyond the list is not observed **(unverified)** | Y |

**The supersession, as this register records it**: on Opencode's default for a name no later rule matches, `mcp-agent-denials-evidence-v2.md` § 4 supersedes `mcp-agent-denials-evidence-v1.md` (lines 94, 188, 255). Rule 0 is a built-in `*: allow`; such a name resolves to allow on 1.19.2, not to ask. Any later text about Opencode's default should cite rule 0 of the stored lists (T847).

## 4. Decisions since v20

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-19 | "SEC-T837-01 go" | T846, T847 | T847 § Metadata (plan-170) |
| 2026-11-19 | "v21 go" | This register | plan-171 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T837-01 | Fixed | T847 (PASS); the orchestrator | T847 § Per-finding statuses; plan-170 § Outcome |
| SEC-T847-01 | Tracked-LOW, under the LOW policy | T847; the orchestrator | T847 § Conditions; plan-170 § Outcome |
| Batch of SEC-T847-01 | Y | me (suggestion) | section 5 |
| Merges, pipelines, suite, ledger | As plan-171 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** My reading gives the same 1 new id, the same 1 that leaves tracked-LOW, 726 ids (548 / 47 / 10 / 1 / 120) and a batch total of 121. What I add: the batch for SEC-T847-01 (Y), and the six non-debt tokens of section 1.2.
- **The commit range.** Plan-171 § Facts names `c764005a..a6732334`; this register searched `c764005a..b26aaf92`, which adds plan-171's own commit. The extra commit mints no id.
- **SEC-T837-03's prior status in T847.** T847's per-finding table gives its prior status as "Open, tracked LOW". v20 records it **fixed** (by T839, per T840; v20 section 3), and T847's own findings table records it "**Fixed** (fix not re-reviewed here)". v20 governs; the status stays fixed. T847's prior-status cell is a slip in that table, not a change of status.
- **SEC-T840-01 and SEC-T842-01 in T847's findings table** carry "SECURITY:MEDIUM (historical)"; both stay fixed and never accepted, as v20 records.
- **Reviewers' line and index numbers** (T847's evidence v1 lines, evidence v2 rule indices) are theirs at the reviewed commit **(unverified)** at `b26aaf92`.

## 5. Open items by LOW batch

Carried from v20 § 5; U and Y change.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v20 § 5 | 24 | as v20 | as v20 |
| K | Security runtime | as v20 § 5 | 8 | as v20 | as v20 |
| L | CWSO helper scripts in emage.code | as v20 § 5 | 5 | as v20 | as v20 |
| M | CWSO repository | as v20 § 5 | 12 | as v20 | as v20 |
| N | Release tooling, second round | as v20 § 5 | 10 | as v20 | as v20 |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | as v20 | as v20 |
| Q | Next release document and its gate rulings | as v20 § 5 | 5 | as v20 | as v20 |
| R | Release-gate text, second round | as v20 § 5 | 7 | as v20 | as v20 |
| V | Release gate after plans 142, 143 and 146 | as v20 § 5 | 17 | as v20 | as v20 |
| X | CI images, the CA control and runner settings | as v20 § 5 | 10 | as v20 | as v20 |
| Y | Shipped text and records | as v20 § 5; **new:** SEC-T847-01 | 11 | as v20; technical-writer or devops-engineer for SEC-T847-01 (T847) | as v20; SEC-T847-01 with the next edit of `docs/wiki/mcp-servers.md` |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v20 | as v20 |
| U | Live checks and user | as v20 § 5; **left:** SEC-T837-01 (fixed) | 6 | as v20 | as v20 (K-20 keeps the refused-call check) |
| AA | Opencode permission, second round | SEC-T837-02, SEC-T842-02, SEC-T844-01 | 3 | devops-engineer (T837, T842, T844) | as v20 |

Total 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 11 + 2 + 6 + 3 = **121** = 120 tracked-LOW + 1 open (K-20). Against v20's 121: U - 1, Y + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Why Y for SEC-T847-01, not AA.** What remains is a one-line documentation pointer in shipped text (`docs/wiki/mcp-servers.md`), the kind of item Y holds. It needs no generator change and no Opencode run, and its trigger does not turn on Opencode 2.x, which is AA's latest trigger. AA would also fit by subject; if SEC-T844-01 is closed by documenting the gap next to K-23 in the same wiki page, the two can share one edit whichever batch holds the id.

**Order, my suggestion only.** v20 § 5 stands, with these changes: SEC-T837-01 is done, so the next Opencode item is AA (SEC-T837-02 first, then SEC-T844-01, then SEC-T842-02's optional deny rule); SEC-T847-01 with the next wiki edit, cheapest alongside AA's documentation work.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v20 § 6.1 stand and stay the record. Since v20: none accepted, none changed. No agent accepted a risk.

### 6.2 Next release checklist (the release after v11.0.0)

v20 § 6.2 (through it v19, v18 and v17 § 6.2) stands, with one wording change in item 49:

- **Item 49 (updated wording; scope and counts unchanged): SEC-T660-01's scope on Opencode for the acceptance at the next release.** v20 § 6.2 item 49 stands in full (the 15 agents with a direct shell, the 2 delegators, the 13 others behind the `external_directory` prompt, and the counts checked there), except its sentence "Nothing here is observed in a live run (SEC-T837-01) **(unverified)**", which now reads: **The resolved rule lists are observed on opencode-ai 1.19.2 for five agents (Tech Lead, QA Engineer, Demo Agent, Orchestrator, Context Retriever; evidence v2, T847). A refused tool call is not observed (K-20). Still unverified: how 1.19.2 maps `bash`, `edit`, `webfetch`, `websearch` and `task` onto its tools at call time, and the 23 agents that were not run, which rest on the generator.** The counts were not re-checked here; no file under `implementation/.opencode/` or `.opencode/` changed in the range (read here).

Count: unchanged from v20; 33 numbers stand.

### 6.3 Dates

v20 § 6.3 stands; no source in the range changes a date:
- **2027-01-28**: SEC-T660-01 and SEC-T665-01 review (token renewal).
- **2027-01-29**: TD-T697-07 ends.
- **2027-01-30**: SEC-T702-09 ends, or at the first Brave release above 2.1.4.
- **2027-03-12**: the CI image review date fails (`ci_images_reviewed_on: 2026-11-11` plus 120 days); `.gitlab-ci.yml` has no diff in the range (read here).

## 7. User actions

v20 § 7 stands unchanged. K-20 / A-7 stays open.

## 8. Method, limits and validation

- **Carried statuses**: v20's rows and lists, plus the sources in Based on. Plan-171 § Facts is the only source for the merges (!694, !695), the suite (2775 OK, skipped=25) and pipelines (3087443885, 3087443847) at `84d43610`, and the ledger count (0 active, 644 completed; no root drift). `docs/tasks/completed-tasks.md` holds 644 task rows and `active-tasks.md` one (T848) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 2415 lines added in `c764005a..b26aaf92` outside `tests/golden/` and `.vscode/`, and set against the text of registers v1 to v20; the result is section 1.2.
- **Counting**: 1 new id. Section 5 expands to 121 ids; the sizes of unchanged batches are v20's, not recounted id by id here.
- **Still unverified**:
  - Carried from v20 § 8, except "every Opencode fix in a live run (SEC-T837-01)", now narrowed as in section 2.4.
  - The equality of evidence v2's indexed lists with its raw files and with the generated maps (T846's and the orchestrator's scripts; not re-run here, nor by T847).
  - On Opencode: a refused tool call (K-20); the call-time mapping of `bash`, `edit`, `webfetch`, `websearch` and `task`; the 23 agents not run; Opencode 2.x (SEC-T837-02); the SEC-T663-03 agent-block and `OPENCODE_CONFIG_CONTENT` runs on the `permission:` form.
  - The orchestrator's suite and pipelines (plan-171 § Facts; not re-run here).
  - The batch membership behind "as v20 § 5".
- **Not run here**: the suite, the pipelines, the generator, Opencode.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v20.md`; `plan-171-tracked-debt-register-v21.md`; `docs/tasks/task-T848.md`; `plan-170-sec-t837-01-opencode-live-check.md` (§ Outcome); `mcp-agent-denials-evidence-v2.md` (§ 4, § 5, headings); `security-review-t847-opencode-live-v1.md` (in full);
  - by grep: registers v1 to v20 (the token scan); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`; `docs/wiki/mcp-servers.md` (evidence links, SEC-T847, rule 0);
  - `git diff --shortstat` and `--stat` of `c764005a..b26aaf92`; `git diff -U0` of the range outside `tests/golden/` and `.vscode/` (added lines only, for the token scan).
- Decision IDs: ADR-011, ADR-015, ADR-016.
