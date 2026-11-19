# Artifact: tracked-debt-register-v20.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v19.md` (714 ids; v19 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-169-tracked-debt-register-v20.md` (§ User decision, § Facts since v19, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T845.md` (the user's "v20 go"); `docs/plans/plan-167-batch-i-sec-t832.md` (§ Outcome); `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Outcome, Addenda 1 to 4, second § Outcome); `docs/artifacts/security-review-t835-batch-i-v1.md`, `security-review-t835-batch-i-addendum-v1.md`, `security-review-t837-opencode-permission-v1.md`, `security-review-t840-opencode-read-v1.md`, `security-review-t842-opencode-deny-v1.md`, `security-review-t844-opencode-task-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T845 (plan-169; the user's answer of 2026-11-19, verbatim: "v20 go"). **Date**: 2026-11-19.
- **Tree read**: branch `agent/tech-lead/T845` at `7c2a34e3` (develop `86ef3904` plus the plan-169 commit). The range for "lines added since v19" is `0379dec9..7c2a34e3` (plan-169 § Facts names `0379dec9..86ef3904`; the one extra commit is plan-169's own plan, brief and ledger row): 95 files, 3430 lines added and 1699 removed (read here). `tests/golden/`, `.vscode/` and `.gitlab-ci.yml` have no diff in the range (read here).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `7c2a34e3`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v18 only by grep. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v19.
- **Batch letters**: **J ends** (its one id, SEC-T663-02, is fixed). **AA is new** (Opencode permission, second round; section 5). Every single letter A to Z has been used by an earlier register (read here by grep of the batch tables and "ends" / "is new" lines of v1 to v19), so the new batch takes a two-letter name rather than reusing an ended letter. The batch of each new id is my suggestion.

## 1. Summary

v20 holds **725 ids**: the 714 of v19 and **11 new**. After v20: **547 fixed**, **47 accepted**, **10 obsolete**, **1 open**, **120 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 still have no reviewer's grade (the orchestrator's ids, called LOW). The five new tracked ids are `SECURITY:LOW` (T835 addendum, T837, T842, T844).
- **Two MEDIUMs were minted and fixed in plan-168: SEC-T840-01 and SEC-T842-01.** Each was fixed in the same batch after the user's choice "Fix now, then refresh (Recommended)" (plan-168 Addenda 2 and 3, verbatim). **Neither was ever accepted.** Neither is verified in a live run; that check stays under SEC-T837-01 (T844 § Findings: "live **unverified**") **(unverified)**. SEC-T840-01 existed before T839 and **v11.0.0 shipped with it** (T840; plan-168 Addendum 2). The user's acceptance of SEC-T660-01 for v11.0.0 was made before SEC-T840-01 was found.
- **The three MEDIUMs accepted for v11.0.0 only keep their status and dates** (v17 section 2.3, § 6.2 item 43): SEC-T660-01 and SEC-T665-01 (review **2027-01-28**), SEC-T702-09 (ends **2027-01-30** or at the first Brave release above 2.1.4). TD-T697-07 (MEDIUM, not shipped) ends **2027-01-29**. **SEC-T660-01's scope on Opencode is restated** by T844 (section 6.2, item 49); its status does not change.
- **Fixed since v19 (3 tracked-LOW + 6 new)**: SEC-T832-01 and SEC-T832-02 by T834 (T835 PASS, addendum PASS); SEC-T663-02 by T836 (T837 PASS); new and fixed in the same plan: SEC-T835-01, SEC-T835-02 (T834, plan-167), SEC-T837-03 (T839), SEC-T840-01 (T841 and T843), SEC-T840-02 (T841), SEC-T842-01 (T843).
- **New and tracked-LOW (5)**: SEC-T835-03 (batch I), SEC-T837-01 (batch U), SEC-T837-02, SEC-T842-02, SEC-T844-01 (batch AA).
- **User actions and accepted risks**: unchanged from v19. **Next-release checklist**: one item enters (49). **Dates**: unchanged.

Arithmetic, from the v19 totals:

| Status | v19 | leaves | enters | v20 |
|---|---:|---|---|---:|
| fixed | 538 | | + 3 tracked-LOW (SEC-T832-01, -02, SEC-T663-02) + 6 new (SEC-T835-01, -02, SEC-T837-03, SEC-T840-01, -02, SEC-T842-01) | **547** |
| accepted | 47 | | | **47** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 118 | - 3 fixed | + 5 new (SEC-T835-03, SEC-T837-01, -02, SEC-T842-02, SEC-T844-01) | **120** |
| **all** | **714** | | + 11 new ids | **725** |

Check: 547 + 47 + 10 + 1 + 120 = 725. Open or tracked: 120 + 1 = 121, the size of section 5.

### 1.1 Ids by v19 status and status now

| v19 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 118 | 3 | 0 | 0 | 0 | 115 |
| accepted | 47 | 0 | 47 | 0 | 0 | 0 |
| fixed | 538 | 538 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v19 ids** | **714** | **541** | **47** | **10** | **1** | **115** |
| new in v20 | 11 | 6 | 0 | 0 | 0 | 5 |
| **all v20 ids** | **725** | **547** | **47** | **10** | **1** | **120** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t835-batch-i-v1.md`: SEC-T835-01, -02 (fixed per the addendum and plan-167 § Outcome) | 2 | 2 | 0 |
| `security-review-t835-batch-i-addendum-v1.md`: SEC-T835-03 | 1 | 0 | 1 |
| `security-review-t837-opencode-permission-v1.md`: SEC-T837-01 to -03 (-03 fixed per T840) | 3 | 1 (-03) | 2 (-01, -02) |
| `security-review-t840-opencode-read-v1.md`: SEC-T840-01 (MEDIUM), -02 (fixed per T842 and T844) | 2 | 2 | 0 |
| `security-review-t842-opencode-deny-v1.md`: SEC-T842-01 (MEDIUM), -02 (-01 fixed per T844) | 2 | 1 (-01) | 1 (-02) |
| `security-review-t844-opencode-task-v1.md`: SEC-T844-01 | 1 | 0 | 1 |
| **All new** | **11** | **6** | **5** |

**Ids minted in the range beyond the plan's list: none.** A search of the 3430 added lines in `0379dec9..7c2a34e3`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<digits or T-number>…` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `M-<n>`) finds exactly: A-7, ADR-011, K-20, K-23, SEC-T646-01, SEC-T657-02, SEC-T657-04, SEC-T660-01, SEC-T660-02, SEC-T660-04, SEC-T663-02, SEC-T663-03, SEC-T832-01 to -03, SEC-T835-01 to -03, SEC-T837-01 to -03, SEC-T840-01, -02, SEC-T842-01, -02, SEC-T844-01, and `ISO-8859`, `UTF-8` (not ids) (read here). Set against registers v1 to v19, only the 11 ids of the table above are in no register. Beside them:
- **Ids named with no change of status**: SEC-T646-01, SEC-T657-02, SEC-T657-04, SEC-T660-02, SEC-T660-04, SEC-T663-03 (all in the refreshed `AGENTS.md` text, T838; statuses as their registers record them); SEC-T660-01 (accepted; scope restated, section 6.2); SEC-T832-03 (fixed in v19); K-20 and A-7 (open; SEC-T837-01's refused-call part stays under K-20, T837); K-23 (Opencode's built-in agents, the user's decision of 2026-10-16; v12's K-15 rows record it "outside this register", and T844 (SEC-T844-01) names it as the place to document the gap).
- This register mints no id.

## 2. v19 ids re-checked

Every v19 `open`, `tracked-LOW` and `accepted` id (166) is covered: the changed ones have a row here, the rest are unchanged and carried. The v19 `fixed` and `obsolete` ids stay as v19 records them.

### 2.1 v19 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7).

### 2.2 v19 `tracked-LOW` (118)

**Changed (3).**

| Id | v19 | now | Evidence |
|---|---|---|---|
| SEC-T832-01 | tracked-LOW, `SECURITY:LOW` (A09), batch I | **fixed** | T834 (commits `a4143f81`, `0487febd`; squash `48b95fac`, merge `2ad398a2`): `_redacted` removes the userinfo, then cuts at the first `?` or `#`, then truncates; with a `?` or `#` before the last `@` it shows only the scheme and `***` (SEC-T835-01); `default_index_dir` no longer shows the slug (plan-167 § Outcome). T835 addendum: "SEC-T832-01 is now fully fixed". Tests failing without the fix and passing with it: the developer's report **(unverified)** |
| SEC-T832-02 | tracked-LOW, `SECURITY:LOW` (A04), batch I | **fixed** | T834: `derive_project_id` refuses an undecodable remote with `RemoteResolutionError` and decodes strictly as UTF-8 (SEC-T835-02); the locale-gated test skips are removed (plan-167 § Outcome). T835 PASS; T835 ledger row: "SEC-T832-01, -02, SEC-T835-01, -02 fixed" |
| SEC-T663-02 | tracked-LOW, batch J | **fixed** | T836 (commits `956c9d1c`, `00538942`; squash `7d3d8b5a`, merge `86ef3904`): the generator writes each Opencode agent's grants and denials as a frontmatter `permission:` map, same names, same order, and no longer writes `tools:` (plan-168 § Outcome). T837 PASS: "SEC-T663-02: fixed. Its live-check part moves to SEC-T837-01". Read here: no file in `implementation/.opencode/agents/` writes a `read:` key; root and `implementation/` agent trees are identical. Not verified in a live run **(unverified)** |

**Unchanged (115 tracked-LOW; v19 and earlier stay the record of their text)**: by batch: I 23, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 10, Y 10, F 2, U 5 (U's sixth id is K-20, open). 23 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 5 = 115; with the 5 new, 120 tracked-LOW in section 5; with the 3 that leave, 118 before. (The batch sizes are carried from v19 and not recounted id by id here.)

### 2.3 v19 `accepted` (47)

**Unchanged (47)**, with their v17 qualifiers (v17 section 2.3). SEC-T660-01 is named in the range: T844 § 6 restates its Opencode scope with no change of status (section 6.2, item 49). No other accepted id is named.

## 3. New ids

Grades are the reviewers' own.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T835-01 | SECURITY:LOW (A09) | An `@` in the query or fragment made the userinfo step remove the `?` or `#`, so the rest of the query was printed | **fixed** (minted and fixed in plan-167) | T835 § Findings; fixed by `0487febd` (T835 addendum) | — |
| SEC-T835-02 | SECURITY:LOW (robustness, A04) | `text=True` decoded in the locale's encoding, so behaviour and tests depended on the locale | **fixed** (minted and fixed in plan-167) | T835 § Findings; fixed by `0487febd` (T835 addendum) | — |
| SEC-T835-03 | SECURITY:LOW (message accuracy; no security impact; A09) | Strict UTF-8 decoding also applies to git's `stderr`, so the "not valid UTF-8 text" message can blame the remote when git failed (`context_retriever.py:155-168`, T835's line numbers) | **tracked-LOW** | T835 addendum; owner backend-developer through the orchestrator; "tracked under the user's LOW policy and not chased further" (plan-167 § Outcome) | I |
| SEC-T837-01 | SECURITY:LOW (A05) | Nobody has observed `opencode debug agent` resolving the new `permission:` form to the same ordered rule list as the stored `tools:` lists | **tracked-LOW** | T837 § Findings; remediation: re-run `opencode debug agent` for Tech Lead, QA Engineer, Demo Agent and Orchestrator on opencode-ai 1.19.2, diff with the stored lists, store as evidence v2; the refused-call check stays under K-20; owner devops-engineer. It is also the live check for SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01 (plan-168 § Outcome) | U |
| SEC-T837-02 | SECURITY:LOW (A05 / A06) | No supported Opencode version range is declared; before about 1.1.1 **(unverified)** the map with MCP keys may be ignored, and the 2.x translation of the V1 map is undocumented, so per-agent denials could fail open | **tracked-LOW** | T837 § Findings; remediation: state the tested range in PREREQUISITES; before claiming 2.x, add a V2 generator variant and observe it live; owner devops-engineer | AA |
| SEC-T837-03 | SECURITY:LOW (pre-existing; A01 / A05) | `search`, `execute`, `web` were inert permission names; `read: allow` after Opencode's default `read: ask` for `*.env` re-allowed reading `.env` without a prompt | **fixed** (minted in T837, fixed by T839) | T840 § Findings: fixed (by reading; live **unverified**). The user: "SEC-T837-03: fix before root refresh." (plan-168 Addendum 1). The orchestrator's ruling: LOW, not a required control (plan-168 § Outcome) | — |
| SEC-T840-01 | **SECURITY:MEDIUM** (A01 / A04; existed before T839, shipped in v11.0.0) | Opencode's default `* allow *` gave every generated agent `bash`, `edit`/`write` and web access, read-only roles included, and through the shell the `gitlab` token | **fixed** (minted in T840; reduced by T841, closed with T843); **never accepted** | T840 (CONDITIONAL_PASS); the user: "Fix now, then refresh (Recommended)" (plan-168 Addendum 2); T842: reduced, direct path closed; T844: fixed, "live **unverified**; live check under SEC-T837-01" **(unverified)** | — |
| SEC-T840-02 | SECURITY:LOW (A05) | The wiki did not say which default read rules apply | **fixed** (minted in T840, fixed by T841) | T842 § Findings: fixed | — |
| SEC-T842-01 | **SECURITY:MEDIUM** (A01 / A04) | Opencode allows `task` by default and a subagent uses its own permissions, so an agent without a shell could launch one that has a shell | **fixed** (minted in T842, fixed by T843); **never accepted** | T842 (CONDITIONAL_PASS); the user: "Fix now, then refresh (Recommended)" (plan-168 Addendum 3); T844: fixed, "live **unverified**". Read here: 26 of 28 agent files carry `task: deny`; only `orchestrator.md` and `poc-orchestrator.md` do not | — |
| SEC-T842-02 | SECURITY:LOW (A01) | For an agent with `bash: deny`, the only guard between the `read` tool and the out-of-project token file is the `external_directory` prompt (ask on 1.19.2; the V2 docs say allow) | **tracked-LOW** (mitigated by documentation) | T842 § Findings; T844: "The note has been added" (PREREQUISITES § GitLab token); optional deny-only `read` rule for the token directory, pattern syntax **(unverified)**, never re-allowing `.env`; owner devops-engineer | AA |
| SEC-T844-01 | SECURITY:LOW (A01) | With the default `task` permission an orchestrator can launch the built-in `general` and `build` agents, which carry no per-agent MCP denials, so GitLab tools its own map denies are reachable in one tool call; no new capability (the orchestrators already hold a shell and the token, SEC-T660-01) | **tracked-LOW** | T844 § Findings; remediation: a deny-plus-named-allows `task` map for the two delegators (1.x syntax **(unverified)**), tests and a mutation; or document the gap next to K-23; owner devops-engineer | AA |

## 4. Decisions since v19

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-14 | "Continue with one of the LOW batches" | The orchestrator then chose SEC-T832-01, -02 (T834, T835) | plan-167 § User decision |
| 2026-11-14 | "J go" | Batch J (T836, T837) | plan-168 § User decision |
| 2026-11-14 | "SEC-T837-03: fix before root refresh." / "Once done do the root refresh" | T839, T840; the second line approves T838 | plan-168 Addendum 1 |
| 2026-11-14 | "Fix now, then refresh (Recommended)" | SEC-T840-01: T841, T842 (option label; question dialog) | plan-168 Addendum 2 |
| 2026-11-14 | "Fix now, then refresh (Recommended)" | SEC-T842-01: T843, T844 (option label; question dialog) | plan-168 Addendum 3 |
| 2026-11-19 | "v20 go" | This register | plan-169 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T837-03 | LOW; the "Envsitter" rule is a behaviour rule, not a configuration control the generator must emit, so the required-control rule does not trigger; fix offered anyway | the orchestrator | plan-168 § Outcome (first) |
| SEC-T835-03 | Tracked-LOW, not chased | T835 addendum; the orchestrator | plan-167 § Outcome |
| Batch of each new tracked id; J ends; AA new | As section 5 | me (suggestion) | this register |
| Merges, pipelines, suite, root refresh, ledger | As plan-169 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** My reading gives the same 11 new ids, the same 3 that leave tracked-LOW, 725 ids (547 / 47 / 10 / 1 / 120) and a batch total of 121, and J ends. What I add: the new batch letter (AA, because no single letter is free), and K-23 among the named ids (outside this register, as v12 recorded).
- **The commit range.** Plan-169 § Facts names `0379dec9..86ef3904`; this register searched `0379dec9..7c2a34e3`, which adds plan-169's own commit. The extra commit mints no id.
- **SEC-T835-01 and -02 in T835.** T835's main table lists them "new, tracked-LOW" (the status as reviewed); the T835 addendum and plan-167 § Outcome record them fixed by `0487febd`. The later source governs.
- **SEC-T840-01 in T842.** T842 records it "reduced"; T844 and plan-168 § Outcome record it fixed. The later source governs.
- **Reviewers' line numbers** (T835, T837, T840, T842, T844) are theirs at the reviewed commits **(unverified)** at `7c2a34e3`.
- **An observation, not a new id.** The 15 agents that keep a shell include `tech-lead.md`, a role that `security-guidelines.md` § Agent Permission Classification calls read-only during review (read here: `tech-lead.md` has no `bash: deny`). This follows its source line's `execute` grant and is inside SEC-T660-01's restated scope (item 49); T842 and T844 did not grade it separately. I mint nothing for it.

## 5. Open items by LOW batch

Carried from v19 § 5; I, U and J change, AA is new.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v19 § 5; **new:** SEC-T835-03; **left:** SEC-T832-01, SEC-T832-02 (fixed) | 24 | as v19; backend-developer for SEC-T835-03 (T835 addendum) | as v19 |
| J | Opencode `tools` to `permission` | **ends**: SEC-T663-02 fixed (T836, T837) | 0 | — | — |
| K | Security runtime | as v19 § 5 | 8 | as v19 | as v19 |
| L | CWSO helper scripts in emage.code | as v19 § 5 | 5 | as v19 | as v19 |
| M | CWSO repository | as v19 § 5 | 12 | as v19 | as v19 |
| N | Release tooling, second round | as v19 § 5 | 10 | as v19 | as v19 |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | as v19 | as v19 |
| Q | Next release document and its gate rulings | as v19 § 5 | 5 | as v19 | as v19 |
| R | Release-gate text, second round | as v19 § 5 | 7 | as v19 | as v19 |
| V | Release gate after plans 142, 143 and 146 | as v19 § 5 | 17 | as v19 | as v19 |
| X | CI images, the CA control and runner settings | as v19 § 5 | 10 | as v19 | as v19 |
| Y | Shipped text and records | as v19 § 5 | 10 | as v19 | as v19 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v19 | as v19 |
| U | Live checks and user | as v19 § 5; **new:** SEC-T837-01 | 7 | the user or an authorised live session; devops-engineer for SEC-T837-01 (T837) | as v19; SEC-T837-01 with the next authorised Opencode 1.19.2 live session, together with K-20's refused-call check |
| AA | **New.** Opencode permission, second round | SEC-T837-02, SEC-T842-02, SEC-T844-01 | 3 | devops-engineer (T837, T842, T844) | its own task; at the latest before any claim of Opencode 2.x support (SEC-T837-02 and SEC-T842-02 both turn on 2.x) |

Total 24 + 0 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 7 + 3 = **121** = 120 tracked-LOW + 1 open (K-20). Against v19's 119: I - 2 + 1, J - 1, U + 1, AA + 3. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Order, my suggestion only.** v19 § 5 stands, with these changes: item 4 now reads SEC-T835-03 with the next change to `context_retriever.py`; SEC-T837-01 first among the new ids, because it is the live check that would confirm the fixes of SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01, and is best run before the next release's SEC-T660-01 acceptance question (item 49); then AA, SEC-T837-02 first (a stated version range bounds the other two), then SEC-T844-01 (verify the 1.x map-valued `task` syntax first, or document next to K-23), then SEC-T842-02's optional deny rule.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v19 § 6.1 stand and stay the record. Since v19: none accepted, none changed. No agent accepted a risk. SEC-T840-01 and SEC-T842-01 were never accepted (section 3).

### 6.2 Next release checklist (the release after v11.0.0)

v19 § 6.2 (through it v18 and v17 § 6.2) stands, with one item entering:

- **Item 49 (new): SEC-T660-01's scope on Opencode for the acceptance at the next release.** The acceptance question for SEC-T660-01 at the next release (item 43) uses this scope, from T844 § 6 and plan-168 § Outcome. It changes no status.
  - **Direct shell, and with it the token:** the 15 generated agents whose source line holds `execute`, Opencode's built-in agents, and the user's own agent files.
  - **Delegation:** only `orchestrator` and `poc-orchestrator`, which hold a shell themselves.
  - **The other 13 generated agents:** no shell and no delegation; their only path to the token file is `read`, behind the `external_directory` prompt (SEC-T842-02).
  - **Counts checked here** against `implementation/.opencode/agents/*.md`: 28 files; 13 carry `bash: deny`, and all 13 also carry `task: deny`; 26 carry `task: deny`; the 2 without it are `orchestrator.md` and `poc-orchestrator.md`, which also have no `bash: deny`; so 15 files have no `bash: deny` (`backend-developer`, `data-mockup-agent`, `database-engineer`, `devops-engineer`, `feasibility-agent`, `frontend-developer`, `integration-agent`, `orchestrator`, `poc-devops-engineer`, `poc-orchestrator`, `poc-qa-engineer`, `qa-engineer`, `release-manager`, `scaffolding-agent`, `tech-lead`). The root `.opencode/agents/` is identical (read here). That "no `bash: deny`" means "the source line holds `execute`" is the generator rule of T841 as plan-168 Addendum 2 records it; I did not read the source lines **(unverified)**. Nothing here is observed in a live run (SEC-T837-01) **(unverified)**.
  - The acceptance text should also say that the user's v11.0.0 acceptance predates SEC-T840-01, which v11.0.0 shipped and which was never accepted (section 3). Whether the next release document must name SEC-T840-01 as shipped-and-fixed is for the orchestrator and the release rules **(unverified)**; I suggest it does.

Count: 26 rules for every release, 1 open (8), and items 43, 44, 46, 47, 48, 49 (6). 33 numbers stand.

### 6.3 Dates

v19 § 6.3 (through it v17 § 6.3) stands; no source in the range changes a date:
- **2027-01-28**: SEC-T660-01 and SEC-T665-01 review (token renewal).
- **2027-01-29**: TD-T697-07 ends.
- **2027-01-30**: SEC-T702-09 ends, or at the first Brave release above 2.1.4.
- **2027-03-12**: the CI image review date fails (`ci_images_reviewed_on: 2026-11-11` plus 120 days); `.gitlab-ci.yml` has no diff in the range (read here).

## 7. User actions

v19 § 7 stands unchanged. K-20 / A-7 stays open.

## 8. Method, limits and validation

- **Carried statuses**: v19's rows and lists, plus the sources in Based on. Plan-169 § Facts is the only source for the merges (!691, !692, !693), the suite (2775 OK, skipped=25) and pipelines (3069161042, 3069161013) at `f075134a`, the root refresh T838 (29 paths, drift `[]`) and the ledger count (0 active, 641 completed). `docs/tasks/completed-tasks.md` holds 641 task rows and `active-tasks.md` one (T845) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 3430 lines added in `0379dec9..7c2a34e3` outside `tests/golden/` and `.vscode/`, and set against the text of registers v1 to v19; the result is section 1.2.
- **Counting**: 11 new ids. Section 5 expands to 121 ids; the sizes of unchanged batches are v19's, not recounted id by id here. The Opencode agent counts in item 49 are counted here.
- **Still unverified**:
  - Carried from v19 § 8.
  - T834's, T836's, T839's, T841's and T843's test and mutation runs (the developers' reports); the orchestrator's suite and pipelines (plan-169 § Facts; not re-run here).
  - Every Opencode fix in a live run (SEC-T837-01).
  - The batch membership behind "as v19 § 5".
- **Not run here**: the suite, the pipelines, the generator, Opencode, the context retriever.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v19.md`; `plan-169-tracked-debt-register-v20.md`; `docs/tasks/task-T845.md`; `plan-167-batch-i-sec-t832.md` (§ User decision, § Outcome); `plan-168-batch-j-opencode-permission.md` (§ User decision, both § Outcome sections, Addenda 1 to 4); the six security reviews in Based on (finding tables and verdicts; T844 § 6 and § Findings);
  - by grep: registers v1 to v18 (the token scan, the batch letters, K-23, the dates); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`; `implementation/.opencode/agents/*.md` and `.opencode/agents/*.md` (`bash: deny`, `task: deny`, `read:`);
  - `git diff --shortstat` and `--stat` of `0379dec9..7c2a34e3`; `git diff -U0` of the range outside `tests/golden/` and `.vscode/` (added lines only, for the token scan).
- Decision IDs: ADR-011, ADR-015, ADR-016.
