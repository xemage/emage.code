# Artifact: tracked-debt-register-v12.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v11.md` (596 ids; v11 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-147-tracked-debt-register-v12.md` and `docs/tasks/task-T783.md` (the user's "v12 go"); `docs/plans/plan-145-release-v10.md` § Outcome; `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md`, with its Addendum and Outcome; `docs/checkpoints/checkpoint-041-release-v10.0.0.md`; `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md`; the review artifacts listed under Metadata; the ledger rows T753 to T782 in `docs/tasks/completed-tasks.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-012 (as v11 cites them), ADR-013 and ADR-014 (as the ledger rows of T770 and T777 and checkpoint-042 record them; not re-read here); no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T783 (plan-147; the user's answer of 2026-11-11, verbatim: "v12 go"). **Date**: 2026-11-11.
- **Tree read**: branch `agent/tech-lead/T783` at `358d292d` (develop `e098b7d9` plus the plan commit). The range for "lines added since v11" is `92eb72c3..e098b7d9`: 566 files, about 9,000 lines added and 50,000 removed, most of them the two removed platform trees. Outside the generated trees, the files that the § 6.2 citations point into and that changed are `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md` (two table rows removed), `tests/functional/test_ci_hash_pins.py` (one test, T765) and `scripts/install.sh`. `scripts/verify-release-docs.py`, `scripts/publish-release.py`, `scripts/run-allowlisted.py` and `implementation/knowledge/agents/release-manager.md` show no diff in the range. The CWSO repository was not read: every CWSO status carries over from v11.
- **Review artifacts read** (by heading, findings table and conclusion; grep beyond that): `security-review-t756-accepted-mediums-v1.md`, `security-review-release-v10-v1.md`, `release-v10-audit-v1.md`, `tech-lead-release-v10-v1.md`, `independent-check-t763-v1.md`, `qa-release-v10-v1.md`, `release-rehearsal-t759-v1.md`, `ca-check-t765-v1.md`, `ca-check-t767-v1.md`, `security-review-t768-ca-control-v1.md`, `pi-removal-inventory-v1.md`, `security-review-t773-pi-removal-v1.md`, `tech-lead-t773-pi-removal-v1.md`, `security-review-t775-gemini-scoping-v1.md`, `gemini-removal-inventory-v1.md`, `security-review-t780-gemini-removal-v1.md`, `tech-lead-t780-gemini-removal-v1.md`, `mcp-pin-audit-v10-v1.md`.
- **Review mode**: read-only. "Unchanged" means no task, review, plan outcome or ledger row since v11 names the id with a change of status, checked by searching the lines added in `92eb72c3..e098b7d9`, outside `tests/golden/`, for every carried id (section 8). A status taken from a review is the latest source's: a later review, plan Outcome or ledger row overrides an earlier one. Code was re-checked only where a line is cited as "read here". Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository. Registers v1 to v10 were not re-read; one keyword grep over all registers looked for carried ids whose text names Pi or Gemini (section 2.4). No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5. New in v12, one status qualifier: **accepted, closes by removal at v11.0.0** (section 2.3). It counts as `accepted`.
- **Batch letters**: I, J, K, L, M, N, P, Q, R, S, V, F and U keep their v11 scope. **W ends.** **X, Y and Z are new** (section 5). T and W are not reused.

## 1. Summary

v12 holds **672 ids**: the 596 of v11 and **76 new**. After v12: **497 fixed**, **49 accepted**, **9 obsolete**, **4 open**, **113 tracked-LOW**.

- **Open above LOW: no `SECURITY:*` grade above LOW is open. Three open ids carry QA's `Medium`.** QA-T760-01, -02 and -03 are graded on QA's own scale (`Critical | High | Medium | Low`), not the `SECURITY:*` scale. Their release-document part was fixed before the tag. QA routes the code behind them (the printed install note, the `--platform-root .claude` default, the exact project-id compare) to this register for the next release, owner backend-developer through the orchestrator (`qa-release-v10-v1.md` § C1). I count them `open`, not tracked-LOW, because of that grade and that binding (batch Z). The fourth open id is K-20 (live checks, user).
- **The accepted MEDIUMs.** SEC-T660-01, SEC-T665-01 and SEC-T702-09 were accepted again by the user for v10.0.0 only. Each needs a fix or a new acceptance before v11.0.0 (section 2.3, section 6.2 item 2). **SEC-T657-01/SEC-T658-01** was accepted for v10.0.0 too, and review T780 closes it by removal at v11.0.0 (section 2.3). TD-T697-07 is unchanged and is not release-shipped.
- **SEC-T756-02**, a new id, was MEDIUM and accepted for v10.0.0, then re-graded **LOW** by review T768. It stays LOW only while A-21 finds none of the listed settings (section 3).
- **Batch W ends:** TD-T746-01 is fixed (T754). It is the only v11 id whose status changed.
- **The Pi and Gemini removals made no v11 id obsolete by name.** They end parts of K-15 and SEC-T657-01/SEC-T658-01 (both now "closes by removal at v11.0.0"), and narrow K-20, A-7, SEC-T658-02 and SEC-T657-04 (section 2.4). SEC-T775-01 to -03 are new and obsolete: closed by removal.
- **Plan-145 settled batch Q's three ids for the v10.0.0 document, and no source closes them.** Checkpoint-041 carries batch Q as tracked, so they stay tracked-LOW and recur at v11.0.0 (section 2.2).
- **An orchestrator's date is wrong.** Checkpoint-041, checkpoint-042 and plan-147 give 2027-02-19 for the CI image review date. By reading, the test now fails after **2027-03-06**, as TL-T761-08 says (section 6.3).
- **Due before v11.0.0** (section 6.2): the three acceptances; the user's two SEC-T762-04 questions; the ADR-013 and ADR-014 migration items; A-21; both CA-chain jobs passing, including after the Node image bump, which has not started (plan-147 § Facts).
- **Open for the user**: A-20 (runner), A-21 (runner settings), A-22 (own settings files); the route of SEC-T735-06 and -07; the SEC-T762-04 questions; any batch before the next tag.

Arithmetic, from the v11 totals:

| Status | v11 | leaves | enters | v12 |
|---|---:|---|---|---:|
| fixed | 469 | | + 1 (TD-T746-01) + 27 new | **497** |
| accepted | 46 | | + 3 new | **49** |
| obsolete | 6 | | + 3 new | **9** |
| open | 1 | | + 3 new | **4** |
| tracked-LOW | 74 | - 1 fixed | + 40 new | **113** |
| **all** | **596** | | + 76 new ids | **672** |

Check: 497 + 49 + 9 + 4 + 113 = 672. Open or tracked: 113 + 4 = 117, the size of section 5.

### 1.1 Ids by v11 status and status now

| v11 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 74 | 1 | 0 | 0 | 0 | 73 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 469 | 469 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v11 ids** | **596** | **470** | **46** | **6** | **1** | **73** |
| new in v12 | 76 | 27 | 3 | 3 | 3 | 40 |
| **all v12 ids** | **672** | **497** | **49** | **9** | **4** | **113** |

### 1.2 New ids by source and final status

| Source | new | fixed | accepted | obsolete | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| `security-review-t756-accepted-mediums-v1.md`: SEC-T756-01 to -08 | 8 | 3 | 0 | 0 | 0 | 5 |
| `security-review-release-v10-v1.md`: SEC-T762-01 to -05 | 5 | 3 | 0 | 0 | 0 | 2 |
| `release-v10-audit-v1.md`: TL-T753-01 to -07 | 7 | 4 | 0 | 0 | 0 | 3 |
| `tech-lead-release-v10-v1.md`: TL-T761-01 to -13 | 13 | 8 | 0 | 0 | 0 | 5 |
| `independent-check-t763-v1.md`: TL-T763-01, -02 | 2 | 0 | 0 | 0 | 0 | 2 |
| `qa-release-v10-v1.md`: QA-T760-01 to -09 | 9 | 6 | 0 | 0 | 3 | 0 |
| `security-review-t768-ca-control-v1.md`: SEC-T768-01 to -06 | 6 | 0 | 0 | 0 | 0 | 6 |
| `security-review-t773-pi-removal-v1.md`: SEC-T773-01, -02 | 2 | 0 | 0 | 0 | 0 | 2 |
| `tech-lead-t773-pi-removal-v1.md`: TL-T773-01 to -04 | 4 | 0 | 1 | 0 | 0 | 3 |
| `security-review-t775-gemini-scoping-v1.md`: SEC-T775-01 to -03 | 3 | 0 | 0 | 3 | 0 | 0 |
| `security-review-t780-gemini-removal-v1.md`: SEC-T780-01 to -07 | 7 | 2 | 0 | 0 | 0 | 5 |
| `tech-lead-t780-gemini-removal-v1.md`: TL-T780-01 to -09 | 9 | 1 | 2 | 0 | 0 | 6 |
| plan-147 § Facts: TD-T774-01, the orchestrator's id | 1 | 0 | 0 | 0 | 0 | 1 |
| **All new** | **76** | **27** | **3** | **3** | **3** | **40** |

**Other ids in the added lines.** A search of the lines added in `92eb72c3..e098b7d9`, outside `tests/golden/`, for any `<PREFIX>-T<nnn>-<n>` id that no register holds finds, beyond the table above, only `BLK-T756-01` to `-04`, `BLK-T762-01`, `-02` and `BLK-T768-01`, which are blocker records and not debt ids, and the placeholders `SEC-T756-xx`, `TL-T761-xx` and `QA-T760-xx` in checkpoint-041. `K-22` to `K-35`, `M-1` to `M-9`, `F-`, `X-` and `A-0n` entries are item numbers inside `docs/releases/v10.0.0.md`; K-23 is not a register id. A-21 and A-22 are user-action numbers. Ids that the removals call moot and that v11 does not carry (SEC-T680-01's Pi half, SEC-T680-02 to -04 per review T773 § 7; SEC-T660-06 per review T780 § 6) keep the status that v10 and earlier record; I did not re-read it. This register mints no debt id; TD-T774-01 is the orchestrator's (plan-147).

## 2. v11 ids re-checked

Every v11 `open`, `tracked-LOW` and `accepted` id (121) has a row or a list entry here: 1 + 74 + 46. The v11 `fixed` and `obsolete` ids stay as v11 records them.

### 2.1 v11 `open` (1)

K-20: **open, narrowed** (section 2.4), batch U (A-7).

### 2.2 v11 `tracked-LOW` (74)

**Changed (1).**

| Id | v11 | now | Evidence |
|---|---|---|---|
| TD-T746-01 | tracked-LOW, batch W | **fixed** | T754, batch W (plan-145 § Task Decomposition item 2; ledger row T754: "TD-T746-01 closed"). Not re-run here |

**Named since v11 with no change of status (6 rows).**

| Id | What the sources say | Status |
|---|---|---|
| SEC-T725-02 | Its recommended timing, "before the release that ships T725", was not taken: v10.0.0 shipped T725 with it unfixed (SEC-T762-05). It stays first in batch I. Whether the user was told is **(unverified)** | tracked-LOW, batch I; **its trigger has passed** |
| SEC-T722-04 | The v10.0.0 document now warns of it in M-2 (SEC-T762-01). A note, not a fix | tracked-LOW, batch I |
| TD-T723-01 | The v10.0.0 document cites current `install.sh` lines (T761 § Citations, QA § Citations). No source closes the id, and checkpoint-041 carries batch Q | tracked-LOW, batch Q; recurs at v11.0.0 (item 4) |
| SEC-T735-08 | Plan-145 "settled" it by how the orchestrator asked: T756 § Passed deadlines; T762 § Orchestrator's record compares the questions with the Conditions text. The rule gap continues as SEC-T762-04. No source closes it | tracked-LOW, batch Q; recurs (item 2) |
| SEC-T735-09 | The pointer sentence is gone from `docs/releases/v10.0.0.md`, "so § 6.2 item 10 is settled" (T761). The template keeps it (`docs/releases/_template.md:88`, read here). No source closes it | tracked-LOW, batch Q; recurs (item 10) |
| SEC-T658-02 | Narrowed by both removals (section 2.4) | tracked-LOW, batch U |

**My judgment on batch Q:** I keep all three ids tracked because no source closes them. If the orchestrator reads plan-145's "settled here" as a closure, they become `fixed` and the totals become 500 fixed and 110 tracked-LOW.

**Unchanged (67 tracked-LOW; v11 and earlier stay the record of their text)**

| Batch | Ids | n |
|---|---|---:|
| I | SEC-T722-01, SEC-T722-02, SEC-T722-03, SEC-T722-05, SEC-T725-01, SEC-T725-03, SEC-T724-01, TD-T724-01 | 8 |
| J | SEC-T663-02 | 1 |
| K | SEC-T714-02, SEC-T714-04, SEC-T714-06, SEC-T714-08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 |
| L | SEC-T726-01, SEC-T726-02, SEC-T726-03, TD-T726-01, TD-T726-02 | 5 |
| M | SEC-T727-01, SEC-T727-02, SEC-T727-03, SEC-T727-04, SEC-T727-05, SEC-T728-01, SEC-T728-02, SEC-T728-03, TD-T728-01, TD-T728-02, TD-T728-03, SEC-T696-07 | 12 |
| N | SEC-T730-03, SEC-T730-04, SEC-T730-06, SEC-T731-03, SEC-T731-04, SEC-T731-05, SEC-T732-01, SEC-T732-02 | 8 |
| P | SEC-T702-08 | 1 |
| R | SEC-T735-06, SEC-T735-07, SEC-T736-01, SEC-T693-07 | 4 |
| S | SEC-T741-17 (the rest; A-20) | 1 |
| V | SEC-T748-03, SEC-T748-04, SEC-T748-05, SEC-T748-06, SEC-T748-07, SEC-T748-08, SEC-T748-09, SEC-T748-12, SEC-T751-01, SEC-T751-05, SEC-T751-06, SEC-T751-07, SEC-T751-08, SEC-T751-09 | 14 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 4 |

Total 67; with the 1 changed and the 6 named, 74. The release-level reviews mention SEC-T714-02, -04, SEV-T690-02, -04, SEC-T665-07, SEC-T663-02, TD-T726-01, SEC-T702-08, SEC-T741-17, SEC-T735-06, SEC-T751-05 and SEC-T751-09 as tracked, in Known Issues or in the gate records, with no change of status. Checkpoint-041 records for SEC-T751-05: "the log shows that the removal ran, not that the credential file was there to remove (SEC-T751-05 stays as recorded)".

### 2.3 v11 `accepted` (46)

**Changed or accepted again (5 rows).** Source for the acceptances: checkpoint-041 § Key decisions; the Conditions text in `security-review-release-v10-v1.md` § "Text for T763's Conditions block", which T763 carried exactly (`independent-check-t763-v1.md` point 4). The user's words, each time: "Accept for v10.0.0 (Recommended)", 2026-11-07.

| Id | v11 | now | Evidence | Before v11.0.0 |
|---|---|---|---|---|
| SEC-T660-01 | accepted MEDIUM | **accepted MEDIUM, for v10.0.0 only** | T756 Part 1: the carried plan's deadline ("the sprint after v8.0.0") **had passed**. The plan shown was "Fix: none possible in the harness", with a review on 2027-01-28 that "is **not a fix date**" (T762 Q4) | **A fix or a new acceptance by the user.** No agent carries it over (ADR-011). The SEC-T762-04 questions apply to it |
| SEC-T665-01 | accepted MEDIUM | **accepted MEDIUM, for v10.0.0 only** | T756 Part 1: no deadline was ever set; "Nothing more can be fixed in the harness". Same review date | **A fix or a new acceptance by the user**, as above |
| SEC-T702-09 | accepted MEDIUM | **accepted MEDIUM, for v10.0.0 only** | T755: same seven Brave ids, newest release still 2.1.4; T756: deadline not passed | **A fix or a new acceptance by the user**; and its own deadline, 2027-01-30 or the first Brave release above 2.1.4 (item 5) |
| SEC-T657-01 / SEC-T658-01 (rest) | accepted MEDIUM | **accepted, closes by removal at v11.0.0** | Accepted for v10.0.0 (deadline 2027-01-31, T762 Q4). Then review T775 found the remainder was Gemini CLI only, and review T780 § 6: "close by removal at v11.0.0; no ADR-011 acceptance needed" | No acceptance needed. **v10.0.0 still ships it**, and v10.x installs stay under the v10.0.0 acceptance. **It reopens if the open Opencode live check (K-20, A-7, SEC-T658-02) shows the per-agent denies are not honoured** (T780 § 6) |
| K-15 | accepted LOW | **accepted, closes by removal at v11.0.0** | Its Pi part ended with ADR-013 (T773 § 7), its Gemini part with ADR-014; "K-15 ends" (T780 § 6). What remains of the subject is K-23, Opencode's built-in agents, a user decision of 2026-10-16 (gemini inventory, row K-15) | As for SEC-T657-01: v10.0.0 ships it |

**Why this status.** "Accepted" is still true of the released v10.0.0, and the closure takes effect only with the release that ships the removal. "Obsolete" now would claim more than review T780 does, and "fixed" would hide the reopening condition. At v11.0.0 both ids become `obsolete` (by removal), unless the Opencode check fails first.

**Unchanged (41)**: TD-T697-07 (MEDIUM; not release-shipped, T756 Part 1; ends 2027-01-29), and the LOW or INFO ids K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04 (narrowed, section 2.4), SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07. That is TD-T697-07 plus 40 LOW or INFO; with the 5 above, 46. None has a new acceptance.

### 2.4 Ids the Pi and Gemini removals touch

Method: the two inventories' own reading of v11 (`pi-removal-inventory-v1.md` § register ids; `gemini-removal-inventory-v1.md` § register ids), reviews T773 § 7 and T780 § 6, and one grep of all registers for lines that name `pi.json`, `gemini`, `.pi/`, `emitMcpGemini`, `skipFormats`, `excludeTools` or `Pi`, intersected with the 121 carried ids. That grep finds K-20, SEC-T658-02, SEC-T657-01, SEC-T658-01, SEC-T660-01, SEC-T665-01, SEC-T657-04 and K-15, and nothing else. **No carried id is fully obsolete.**

| Id | Status | What the removals end | What stays |
|---|---|---|---|
| SEC-T657-01 / SEC-T658-01 | accepted, closes by removal at v11.0.0 | Both remaining platform parts | The reopening condition (section 2.3) |
| K-15 | accepted, closes by removal at v11.0.0 | Its Pi and Gemini parts | K-23, Opencode, outside this register |
| K-20 | open, **text stale** | "Pi lists" and "the Gemini CLI denials" among the live checks | The Opencode refused call, Copilot and the VS Code T690 servers (A-7) |
| SEC-T658-02 | tracked-LOW, **text stale** | The Gemini CLI check and the Pi list handling | The Opencode refused call and the Copilot checks; `mcp-pin-bump-checklist.md` § 6 |
| SEC-T657-04 | accepted LOW, **text stale in part** | An older row names Gemini CLI and Pi among the platforms where narrowing was not in force | Its current subject, by my reading: no generated or configured route keeps a prompt on Opencode except `OPENCODE_CONFIG_CONTENT` and the managed configuration (`AGENTS.md` § MCP Servers) |
| SEC-T660-01, SEC-T665-01 | unchanged by the removals | The grep hit is a historical split row ("Pi and Opencode wording") | All of it |

The new SEC-T756-07 also names Gemini CLI ("On Gemini CLI any agent can reach it"). That part ends with the removal on `develop` (section 3).

## 3. New ids

Sources as in section 1.2. Grades are the reviewers' own: `SECURITY:*` for security reviews; Critical, Important, Minor, LOW or nit for the Tech Lead; QA's `Critical | High | Medium | Low`. "Read here" means a grep or line read on `358d292d`.

**Plan-145, the v10.0.0 release**

| Id | Grade | Short description | Status | Evidence, what stays | Batch |
|---|---|---|---|---|---|
| SEC-T756-01 | SECURITY:HIGH | CVE-2026-115557: Python 3.12.15 in the CI image lacked the eMudhra distrust, and `release` sends its token through it | **fixed** | T765 bumped to 3.12.16; T759's `_ssl` check found the block; T762 Q1 closes it | - |
| SEC-T756-02 | MEDIUM, then **SECURITY:LOW** | `git` in CI depends only on the CA bundle | **tracked-LOW** | Accepted by the user for v10.0.0 at MEDIUM. Re-graded LOW by T768, effective when MR !658 merged with both CA jobs passing, which pipeline 3040148068 shows (ledger T766, T768). Ledger T768 and checkpoint-042 record the user's "No pin (Recommended)". **Condition:** A-21. A listed CA variable set, or an unchecked `helper_image`, returns it to MEDIUM. `GIT_SSL_NO_VERIFY` set is HIGH, as a separate finding (T768). Residual LOW: unlogged cross-signs, no live connection test, non-amd64 not read, helper image pinned by tag only | X |
| SEC-T756-03 | SECURITY:LOW | Expat CVEs in the Python image | **fixed** | By the same bump (T762 Q1) | - |
| SEC-T756-04 | SECURITY:LOW | `tarfile` CVE-2026-114583 | **fixed** | As -03 | - |
| SEC-T756-05 | SECURITY:LOW, provisional | Node security release, content unpublished. No tag job uses Node | **tracked-LOW** | T762 Q2: stands, to be re-graded when the content is published. The advisory was due on 2026-11-11 and **the bump has not started** (plan-147 § Facts). I did not read the advisory **(unverified)** | X |
| SEC-T756-06 | SECURITY:LOW, provisional | Alpine 3.24.4 notes unread | **tracked-LOW** | The Python image is on 3.24.4, the Node image still on 3.24.3 (T756 re-grade table; `.gitlab-ci.yml:16-17`, read here) | X |
| SEC-T756-07 | SECURITY:LOW | Two moderates through `server-filesystem` (`servers.yaml:241-246`) | **tracked-LOW** | No agent lists the server, `denyUnlessGranted: true`. Its "on Gemini CLI any agent can reach it" ends on `develop` with the removal. v10.0.0 still ships the Gemini path | X |
| SEC-T756-08 | SECURITY:LOW | `scripts/sync-wiki.py` uses plain `urlopen`, which follows redirects with `PRIVATE-TOKEN` | **tracked-LOW** | T756: "may already be tracked". A grep of all registers for `sync-wiki` lines that mention redirects finds none, so it is new. `scripts/sync-wiki.py:71` still calls `urllib.request.urlopen` (read here) | X |
| SEC-T762-01 | SECURITY:LOW | Release document omitted tracked residuals (K-25, M-2) | **fixed** | Applied in T763 (`independent-check-t763-v1.md` point 2) | - |
| SEC-T762-02 | SECURITY:LOW | "Nothing open in it is above LOW" next to five shipped MEDIUMs | **fixed** | As -01 (with TL-T761-07) | - |
| SEC-T762-03 | SECURITY:LOW | K-29 called the executor unverified | **fixed** | As -01 | - |
| SEC-T762-04 | SECURITY:LOW | Two rules are unruled: can a plan's fix be "none possible", and does a new acceptance cure a passed deadline | **tracked-LOW** | Owner orchestrator, **ruling the user**, by the next release's gate (T762 Conditions). Unruled (section 4.1) | Q |
| SEC-T762-05 | SECURITY:LOW | SEC-T725-02's timing was not taken | **tracked-LOW** | Keep it first in batch I and tell the user (T762) | I |
| TL-T753-01 | Important | "Keep a copy under another file name" fails inside a platform tree | **fixed** | T758 used M-1's wording (audit table; plan-145 § Wave 1 note) | - |
| TL-T753-02 | Important | `--projections-only` from v9 leaves `context-retriever` unable to start | **fixed** (as a document item) | T758 states M-2. No code fix was proposed | - |
| TL-T753-03 | Important | T714 and T722 breaks were missing from § 6.2 and plan-145 | **fixed** | T758 took M-2 to M-6 | - |
| TL-T753-04 | Minor | Stale install note on `--index-dir` | **fixed** | T765, "the installer note" (ledger T765). `grep -c 'already set in the generated' scripts/install.sh` is 0 (read here). The audit's remark on `build.py:12` was wrong (plan-145 § Wave 1, T765) | - |
| TL-T753-05 | Minor | Shipped text names scripts a target lacks | **tracked-LOW** | K-33 in the v10.0.0 document | Y |
| TL-T753-06 | Minor | `files` in a target's manifest names the withheld command | **tracked-LOW** | No reader of `files` found (audit) | I |
| TL-T753-07 | Minor | T745 has a review and no ledger row | **tracked-LOW** | A record gap. This register records it, and only the orchestrator can add a row | Y |
| TL-T761-01 | Important | Upgrade steps never said to back up first | **fixed** | Applied in step 1 (T763 point 1) | - |
| TL-T761-02 | Important | Mixed-case `--project-id` | **fixed**, with a correction | Applied in M-2 (T763 point 1). **TL-T763-01 corrects it:** the value that causes the empty result is the entry's `project_id`, not `--project-id` | - |
| TL-T761-03 | Important | README and wiki offered `--projections-only` with no upgrade warning | **fixed** | Applied at `README.md` and `docs/wiki/implementation-guide.md` (T763 point 1). **The orchestrator decided it, not the user** (checkpoint-041; section 4.2) | - |
| TL-T761-04 | Important | Ordering trap at T763's independent check | **fixed** | "-04's order holds" (T763 point 1) | - |
| TL-T761-05 | Minor | Highlight overstated what a plain install deletes | **fixed** | Line 36 (T763 point 1) | - |
| TL-T761-06 | Minor | Nested group under `<org>` | **fixed** | M-2's nested-group sentence (T763 point 1) | - |
| TL-T761-07 | Minor | K-18's "nothing open above LOW" | **fixed** | In K-18 (T763 point 1) | - |
| TL-T761-08 | LOW | Stale notes in register v11 § 6.2 item 1 and § 6.3 and in plan-145; the CI header's bump recipe omits the test constants | **tracked-LOW** | The register notes are corrected here (section 6.2 items 1 and 19, section 6.3). **The header recipe still omits them** (`.gitlab-ci.yml:25-29`, read here) | Y |
| TL-T761-09 | Minor | "Copy it back after each `--update`" | **fixed** | Line 81 (T763 point 1) | - |
| TL-T761-10 | LOW | Does a "Fix: none possible" plan satisfy the rule? | **tracked-LOW** | The same question as SEC-T762-04's first. For the user | Q |
| TL-T761-11 | LOW | With `FF_GIT_URLS_WITHOUT_TOKENS` on, `release`'s fetch would have no credential | **tracked-LOW** | Works while the project is public; fails closed otherwise. Sits next to A-21 | X |
| TL-T761-12 | Minor | The first-tag list does not say that `main` must not move before the tree check ends | **tracked-LOW** | Held by practice at T764: `main` stayed `623eea7c` (checkpoint-041). The text is still missing (`CONTRIBUTING.md:280-293`, read here) | Y |
| TL-T761-13 | LOW | `implementation/runtime/memory/README.md:52, 74` use this repository's own index path as the example | **tracked-LOW** | Still so (read here) | Y |
| TL-T763-01 | LOW | Corrects TL-T761-02: which value causes the empty result | **tracked-LOW** | "Next register: correct the record", done above. The document's wording stays | Y |
| TL-T763-02 | LOW | M-2 has no pointer to K-35 | **tracked-LOW** | For the next edit | Y |
| QA-T760-01 | Medium (QA) | M-2's rebuild fails with the dependencies the installer prints | **open** | Document fixed (C1, T763 point 2). **Code residue:** the printed note still names only `requirements-mcp-server.txt` (`scripts/install.sh:1753`, read here). For this register, next release (QA C1) | Z |
| QA-T760-02 | Medium (QA) | A mixed-case project id silently returns nothing | **open** | Document fixed. Code residue: the exact compare in `scope_filter.py:52` (QA's line; not re-read) | Z |
| QA-T760-03 | Medium (QA) | Without `.claude/`, `retrieve` fails on non-Claude installs | **open** | Document fixed (K-35). Code residue: `--platform-root .claude` in `servers.yaml:194` (read here) | Z |
| QA-T760-04 | Low (QA) | K-32 said the probe tags were still on the remote | **fixed** | C2 applied (T763 point 2) | - |
| QA-T760-05 | Low (QA) | Nested groups not described | **fixed** | C2 | - |
| QA-T760-06 | Low (QA) | The M-6 `/tmp/cwso-credcheck*` wording | **fixed** | C2 | - |
| QA-T760-07 | Low (QA) | `?` for non-ASCII holds only where `printable` is used | **fixed** | C2 | - |
| QA-T760-08 | Low (QA) | The "not received" list omitted PREREQUISITES and SECURITY | **fixed** | C2 | - |
| QA-T760-09 | Low (QA), a carry-over of QA-T707-03 | The one-release grace makes the drift check vacuous for v10 | **fixed, as C3 asked** | Merged into develop and main before the tag. After the tag, `releases_behind=0` (checkpoint-041). The grace itself is QA-T707-03's, as earlier registers record | - |

**Plan-146: the CA control and the Pi and Gemini removals**

| Id | Grade | Short description | Status | Evidence, what stays | Batch |
|---|---|---|---|---|---|
| SEC-T768-01 | SECURITY:LOW | The SPKI scan reads only `BEGIN CERTIFICATE` blocks | **tracked-LOW** | `scripts/check-ca-chains.sh:123` still matches only that form (read here). Owner devops-engineer, next sprint (T768) | X |
| SEC-T768-02 | SECURITY:LOW | Fixtures not cross-checked; CI does not run `sha256sum -c` | **tracked-LOW** | As -01 | X |
| SEC-T768-03 | SECURITY:LOW | The node job checks only `--cafile` | **tracked-LOW** | As -01 | X |
| SEC-T768-04 | SECURITY:LOW | No CA check in tag pipelines | **tracked-LOW** | At the next tag-job change (T768) | X |
| SEC-T768-05 | SECURITY:LOW | T767 says 4 extra certificates; the script has 3 | **tracked-LOW** | Which is right is **(unverified)** (T768) | X |
| SEC-T768-06 | SECURITY:LOW | `mcp-pin-bump-checklist.md:30` names the old Python digest | **tracked-LOW** | Still `92abd2ba` (read here) | X |
| SEC-T773-01 | SECURITY:LOW | The UTF-8 test skips a missing release document newer than the newest one | **tracked-LOW** | The gate still rejects it at the tag (T773). It is T771's narrowed skip, which the orchestrator accepted (section 4.2) | V |
| SEC-T773-02 | SECURITY:LOW | An adopter's `.pi/` stays frozen; no notice without a marker | **tracked-LOW** | Accepted in ADR-013 D11. The v11.0.0 document must carry the Appendix A item and the frozen-state warning (item 31) | Q |
| TL-T773-01 | non-blocking | Two hits of the D1 grep outside ADR-013's allowed list | **accepted (the orchestrator's)** | Recorded as accepted residue in ledger row T773. Not the user's | - |
| TL-T773-02 | nit | Moved test's name still says "dropped" | **tracked-LOW** | Optional (T773) | I |
| TL-T773-03 | nit | The reworded rationale is true for claude-code; other clients **(unverified)** | **tracked-LOW** | As -02 | I |
| TL-T773-04 | nit | "emitted" now means "selected" | **tracked-LOW** | As -02 | I |
| SEC-T775-01 | SECURITY:LOW | Gemini agent files fail the strict loader | **obsolete** (closed by removal) | Review T780 § 6; `gemini-removal-inventory-v1.md`: "closed-by-removal, not open LOW debt". v10.0.0 still ships the files | - |
| SEC-T775-02 | SECURITY:LOW | Docs said Gemini does not enforce tool lists | **obsolete** (closed by removal) | As -01 | - |
| SEC-T775-03 | SECURITY:LOW (info) | Gemini subagents cannot call agents | **obsolete** (closed by removal) | As -01 | - |
| SEC-T780-01 | SECURITY:LOW | The Opencode posture cell read "No (K-15)" | **fixed** | T779 (ledger T779, T780). `No (K-15)` is absent from `implementation/PREREQUISITES.md` (read here) | - |
| SEC-T780-02 | SECURITY:LOW | Unconditional `agents-root` exemption in `test_mcp_package_pins.py` | **fixed** | T781 (ledger T781). `RAW_JOB_OUTPUT_PRE_T779` and the exemption are absent (read here) | - |
| SEC-T780-03 | SECURITY:LOW | Source scans would miss a write through `$dir` in the notice | **tracked-LOW** | Snapshot tests catch it at run time (T780) | I |
| SEC-T780-04 | SECURITY:LOW | A FIFO swapped in after the check makes `grep -Eq` hang (all three notices) | **tracked-LOW** | As -03 | I |
| SEC-T780-05 | SECURITY:LOW | Adopters keeping Gemini CLI keep a frozen `.gemini/settings.json` | **tracked-LOW** | The v11.0.0 document must carry the Appendix A item (item 31) | Q |
| SEC-T780-06 | SECURITY:LOW | The user's `.vscode/settings.json:13` auto-approves `gemini`; one hit in `.claude/settings.json` | **tracked-LOW** | User action A-22 (ADR-014 Q4). Not opened here **(unverified)** | U |
| SEC-T780-07 | SECURITY:LOW | `install.sh:169`, `:242` echo raw argv | **tracked-LOW** | Line 169 still prints `$1` raw (read here) | I |
| TL-T780-01 | non-blocking | Permanent absence guards in `test_mcp_package_pins.py` match the D1 grep | **accepted (the orchestrator's)** | Recorded as accepted residue in ledger row T780. Not the user's | - |
| TL-T780-02 | condition for T781 | = SEC-T780-02 | **fixed** | As SEC-T780-02 | - |
| TL-T780-03 | LOW | Three near-identical `notice_previous_<platform>_install` functions | **tracked-LOW** | Conforms to ADR-014 D4.4 (T780) | I |
| TL-T780-04 | nit | A 146-character comment line in `sync.mjs` | **tracked-LOW** | Optional | I |
| TL-T780-05 | nit | Ragged docstring | **tracked-LOW** | Optional | I |
| TL-T780-06 | nit | An orphaned process after the FIFO test's timeout | **tracked-LOW** | Optional | I |
| TL-T780-07 | nit (accepted deviation) | Looser `ARTIFACT_UNSAFE_CONTEXTS` anchor | **accepted (the orchestrator's)** | One of T778's deviations that the orchestrator accepted (checkpoint-042) | - |
| TL-T780-08 | observation | `implementation/SECURITY.md:9`: "v2 keeps the same defaults" is out of date | **tracked-LOW** | A doc item, not Gemini residue (T780) | Y |
| TL-T780-09 | observation | The release-doc gate requires a migration item only on `install.sh` lines with "Cursor" | **tracked-LOW** | The v11.0.0 plan carries the Pi and Gemini items by review, or adds a check (T780) | Q |

**The orchestrator's id**

| Id | Grade | Short description | Status | Evidence, what stays | Batch |
|---|---|---|---|---|---|
| TD-T774-01 | **none: no reviewer has graded it** | The installer's `rsync -a` compares size and modification time only. After a fresh checkout, a changed file of the same length and checkout time is not copied. Seen in both root refreshes (T774: four `context-retriever` agent files; T781). The same skip can hit a user's `install.sh --update` | **tracked-LOW, ungraded** | Plan-147 § Facts, the only source; ledger rows T774 and T781. Worked around by touching the sources. Suggested fix (orchestrator's): `rsync --checksum` or a post-copy compare. Not reproduced here. A skipped update could leave a target with an old projection, possibly an old security setting, so a reviewer should grade it **(my reading)** | I |

**My batch choice for TD-T774-01:** batch I, because it is `scripts/install.sh` behaviour.

## 4. Decisions since v11

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. The questions as shown were not verified beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-06 | "release go" | Plan-145, the v10.0.0 release | plan-145 Based on |
| 2026-11-06 | "v10.0.0, MAJOR (Recommended)"; "Add batch W only (Recommended)"; "Docker, this rehearsal only (Recommended)" | Version, scope, rehearsal (AskUserQuestion) | plan-145 Based on |
| 2026-11-06 | "Approve (Recommended)" | Plan-145 | plan-145 Based on |
| not dated in the source | "Approve both (Recommended)" | The new `python:3.12-alpine` digest and the `_ssl` check in the rehearsal | checkpoint-041 § Key decisions |
| 2026-11-07 | "Accept for v10.0.0 (Recommended)", once each | SEC-T660-01, SEC-T665-01, the SEC-T657-01/SEC-T658-01 remainder, SEC-T702-09, SEC-T756-02 | checkpoint-041; T762 Conditions text |
| 2026-11-07 | "develop go", "main go", "tag go" | The three publishing steps, each at its moment | plan-145 § Outcome |
| 2026-11-07 | "Plan for: Fix of SEC-T756-02, Remove PI support completely, then review and work on SEC-T657-01/SEC-T658-01" | The request for plan-146 | plan-146 Based on |
| 2026-11-07 | "Approve (Recommended)" | Plan-146 | checkpoint-042 |
| 2026-11-07 | "No pin (Recommended)" | No CA pin on the job's own `git` | checkpoint-042; plan-146 § Outcome |
| 2026-11-07 | Q1 "v11.0.0, no deprecation (Recommended)"; Q2 "Error + notice, never delete (Recommended)"; Q3 "Delete both in S1 (Recommended)"; Q4/Q5 "Accept all (Recommended)" | ADR-013 | ledger T770; checkpoint-042 |
| 2026-11-07 | "Agent lists + GitLab allowlist (Recommended)", "Yes, I use glab/web/other (Recommended)", "Drop Gemini support"; then "Drop Gemini instead of fixing (Recommended)" | The Gemini fix options, the conflict, and its resolution | plan-146 Addendum |
| 2026-11-07 | Q1 "Error + notice, never delete (Recommended)"; Q2 "Delete both in T778 (Recommended)"; Q3/Q5 "Accept all (Recommended)"; Q4 "I'll remove it myself (Recommended)" | ADR-014 | ledger T777; checkpoint-042 |
| 2026-11-07, 2026-11-11 | "Yes, refresh now (Recommended)", each at its moment | The root refreshes T774 and T781 | ledger T774, T781 |
| 2026-11-11 | "v12 go" | Plan-147, T783, this register | plan-147 Based on |

**Still unruled, for the user (SEC-T762-04, with TL-T761-10):** (1) can a plan's fix be "none possible"; (2) does a new acceptance cure a deadline that has already passed. No agent rules on either (section 6.2, item 33).

### 4.2 The orchestrator's rulings (not the user's)

| Item | Decision | Source | Effect |
|---|---|---|---|
| TL-T761-03 | Added the `--projections-only` warning to the README and the wiki. **The user may overrule it** | checkpoint-041 | TL-T761-03 fixed |
| TL-T753-04 | Fixed the install note in wave 1 (T765), as the audit recommended | ledger T765 | TL-T753-04 fixed |
| SEC-T756-01 as task T765 | Added to wave 1 before the user's decisions, because a HIGH cannot be accepted | plan-145 § T765 | SEC-T756-01 fixed |
| The T767 owner change | | checkpoint-042 | none on an id |
| T771's narrowed release-gate test skip, and the `v10.0.0` tag fetch in `unit-tests` | Accepted as deviations | checkpoint-042; ledger T771 | SEC-T773-01 |
| T778's deviations | Accepted | checkpoint-042 | TL-T780-07 |
| TL-T773-01 and TL-T780-01 | Recorded as accepted residue in the ledger rows of T773 and T780 | checkpoint-042 | both accepted |
| TD-T774-01 | Minted and described; the fix is suggested, not scheduled | plan-147 § Facts | section 3 |
| Batch letters X, Y, Z and the Q, V, I additions | **Mine**, as plan-147 leaves to me | this register | section 5 |

### 4.3 Errors on the record

These stay as the sources state them.

- **The CI image review date (the orchestrator's).** Checkpoint-041 ("goes stale on 2027-02-19"), checkpoint-042 and plan-147 give 2027-02-19. `.gitlab-ci.yml:20` reads `ci_images_reviewed_on: 2026-11-06`, and the test allows 120 days, so by reading it fails from **2027-03-07** (after 2027-03-06). TL-T761-08 said so before the tag. 2027-02-19 is SEC-T756-02's deadline as shown to the user and A-21's due date, not the test's.
- **TL-T761-02 was wrong in part (the Tech Lead's own).** It named `--project-id` as the value that matters; it is the entry's `project_id` (TL-T763-01). My artifact is immutable, so the correction is here.
- **The audit's remark on `build.py:12` was wrong (the Tech Lead's own, T753)** (plan-145, T765).
- **T756's runner-pin reason for SEC-T756-02's lower grade was wrong for the job's own `git`.** The reviewer withdrew it after T765 (`security-review-t756-accepted-mediums-v1.md` § Re-grade).
- **`.gitlab-ci.yml:17` misquoted review T756** ("no security release to wait for"). The reviewer asked for a rewording, and the line now gives the reviewer's reason (read here).
- **T767's "4 certificates"** against 3 in its table and script (SEC-T768-05; which is right is unverified).
- **Over budget**, by the harness's count including context: T753 about 171k against 130k, T755 124k/80k, T756 246k/100k, T765 173k/110k (plan-145); the gate agents 160k to 230k against 60k to 120k (checkpoint-041); T771 323k/150k, T778 293k/150k, T772 200k/120k, T779 251k/120k, T766 197k/110k, T776 209k/120k (checkpoint-042).

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. J, K, L, M, N, P, R, S and F are carried from v11 without change. I, Q, U and V grow. W ends. X, Y and Z are new.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | **SEC-T722-03 (do first)**, **SEC-T725-02 (do first; its trigger passed, SEC-T762-05)**, SEC-T722-01, -02, -04, -05, SEC-T725-01, -03, SEC-T724-01, TD-T724-01; **new:** TD-T774-01, SEC-T762-05, TL-T753-06, SEC-T780-03, -04, -07, TL-T780-03, TL-T780-04, -05, -06, TL-T773-02, -03, -04 | 23 | devops-engineer; backend-developer (SEC-T724-01, TD-T724-01) | next installer or generator change. **TD-T774-01 needs a grade first** (my suggestion) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | devops-engineer | its own task (plan-128) |
| K | Security runtime (`security-audit` servers) | SEC-T714-02, -04, -06, -08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 | devops-engineer; technical-writer | next change to `implementation/runtime/security/` |
| L | CWSO helper scripts in emage.code | SEC-T726-01 to -03, TD-T726-01, TD-T726-02 | 5 | devops-engineer | next change to the CWSO helper scripts; TD-T726-02 before the next Proxmox setup |
| M | CWSO repository | **SEC-T728-01**, **SEC-T727-01, -02 (do first)**, SEC-T727-03 to -05, SEC-T728-02, -03, TD-T728-01 to -03, SEC-T696-07 | 12 | devops-engineer (CWSO) | as v11 |
| N | Release tooling, second round | SEC-T730-03, -04, -06, SEC-T731-03, -04, -05, SEC-T732-01, -02 | 8 | devops-engineer | next fixing round; `verify-release-docs.py` and `publish-release.py` are unchanged since v11, so v11's lines stand |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v11 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09; **new:** SEC-T773-02, SEC-T780-05, TL-T780-09, SEC-T762-04, TL-T761-10 | 8 | release-manager; the orchestrator routes; **the user rules on SEC-T762-04 and TL-T761-10** | **the v11.0.0 release** (items 2, 4, 10, 31, 33) |
| R | Release-gate text, second round | SEC-T735-06, SEC-T735-07, SEC-T736-01 (the rest), SEC-T693-07 | 4 | orchestrator routes each | **the route of SEC-T735-06 and -07 is still to be settled before batch R** (v11 § 5) |
| S | Release gate: the runner tag | SEC-T741-17 (the rest) | 1 | the user provides the runner (A-20) | waits on the user's runner |
| V | Release gate after plans 142, 143 and 146 | SEC-T748-03, -04, -05, -06, -07, -08, -09, -12, SEC-T751-01, -05, -06, -07, -08, -09; **new:** SEC-T773-01 | 15 | devops-engineer | **open, for the user**: no source binds V to a release. v11's suggested order stands, with SEC-T751-06 first |
| X (new) | CI images, the CA control and runner settings | SEC-T756-02, SEC-T756-05, SEC-T756-06, SEC-T756-07, SEC-T756-08, SEC-T768-01 to -06, TL-T761-11 | 12 | devops-engineer (T768: "next sprint"; -04 at the next tag-job change) | **the Node image bump** (SEC-T756-05, -06; both CA jobs must pass); A-21 (SEC-T756-02, TL-T761-11) |
| Y (new) | Shipped text and records | TL-T753-05, TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T763-01, TL-T763-02, TL-T780-08 | 8 | technical-writer; orchestrator for TL-T753-07 and TL-T761-12 (suggested; no source sets it) | the next docs change; TL-T761-12 before the next first-tag use of `CONTRIBUTING.md` |
| Z (new) | `context-retriever` after M-2: code residue | QA-T760-01, QA-T760-02, QA-T760-03 (**open, QA Medium**) | 3 | backend-developer through the orchestrator (QA C1) | **"next release"** (QA C1). Section 6.2 item 36 |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06; **new:** SEC-T780-06 | 7 | the user or an authorised live session | A-2, A-7, A-11, A-15, A-22 |

Total 23 + 1 + 7 + 5 + 12 + 8 + 1 + 8 + 4 + 1 + 15 + 12 + 8 + 3 + 2 + 7 = 117 = 113 tracked-LOW + 4 open. **No open item carries a `SECURITY:*` grade above LOW.** Batch Z carries QA's Medium, and TD-T774-01 has no grade.

**Batch W ends.** TD-T746-01 is fixed.

**Order, my suggestion only.** X first, because the Node bump is due and both CA jobs must pass on it. Then Z, because QA binds it to the next release. Then V's SEC-T751-06, as v11 suggests. Then I's TD-T774-01, once graded, because it can silently skip an update in a target.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v11 § 6.1 stand and stay the record. New since v11: the user's five acceptances for v10.0.0 only (section 2.3), and three orchestrator-accepted LOW residues (TL-T773-01, TL-T780-01, TL-T780-07), which are not the user's acceptances. ADR-011 holds: only the user accepts a MEDIUM, for one release only.

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 **2027-01-30 or the first Brave release above 2.1.4**; SEC-T660-01, SEC-T665-01 and SEC-T702-09 **at v11.0.0** (a fix or a new acceptance); SEC-T657-01/SEC-T658-01, shown deadline **2027-01-31** (T762 Q4), **closes by removal at v11.0.0**.

### 6.2 Next release checklist (v11.0.0, MAJOR)

Carried from v11 § 6.2, with its numbers. Items 1, 2, 3, 4, 6, 8, 10, 13, 14, 19, 21, 23, 27 and 28 change, and items 31 to 36 are new. I re-read every line that points into `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `tests/functional/test_ci_hash_pins.py` and `scripts/install.sh`, the files changed since v11. Lines in `scripts/verify-release-docs.py`, `scripts/publish-release.py`, `scripts/run-allowlisted.py` and `release-manager.md` stand, because those files have no diff. Items not named here keep v11's text.

1. **Done at v10.0.0.** The T725 migration item shipped with M-1's wording (TL-T753-01), not v11's "another file name". Not a v11.0.0 item.
2. **ADR-011 re-acceptances: SEC-T660-01, SEC-T665-01, SEC-T702-09.** Each is fixed, or the user accepts it again for v11.0.0, verbatim and dated, with its plan (owner, fix, deadline). No agent grants or carries one over. SEC-T756-02 is LOW and leaves this list while A-21 holds (item 34). SEC-T657-01/SEC-T658-01 needs no acceptance and closes by removal; the document says so (item 32). Ask the way SEC-T735-08 says: name the release, record the plan as shown, show a deadline still ahead. **Do not present the SEC-T762-04 questions as settled** (item 33).
3. Verdict fields: `docs/releases/_template.md:85-86` (two lines earlier than v11's, because the Pi and Gemini rows left the platform table).
4. **TD-T723-01:** the current lines are `scripts/install.sh:187` (the Cursor error naming v9.0.0), `:1301-1304` (the `.cursor/mcp.json` advice) and `:1305` (the pointer), read here. The new Pi and Gemini notices are at about `:1306-1352`, so **re-read the lines when the document is written**.
5. Brave: as v11.
6. **D-T710-2: observed at the v10.0.0 tag.** The `CHANGELOG.md` artifact has the entry below `[Unreleased]` (checkpoint-041). **What it leaves:** nothing for v11.0.0 unless `scripts/publish-release.py` changes (my reading).
7. Visible changes of batches G, S and T: as v11. The gate's rules hold, because `scripts/verify-release-docs.py` has no diff.
8. **Observed at the v10.0.0 tag:** GitLab rendered 0 reference links in the Release, and the escaped references stayed literal (checkpoint-041). **What it leaves:** the npm step does not run in a tag pipeline, since no npm job matches the tag rule, so only merge request pipelines cover it. The musl lock beyond the MR pipeline stays **(unverified)**.
9. to 12. As v11.
13. **Settled by an install (T753):** targets receive neither `scripts/verify-release-docs.py` nor `docs/releases/_template.md` (plan-145 § Wave 1). The gate script's one mention in `install.sh` is now the comment at `:1300`.
14. **Observed at the v10.0.0 tag (checkpoint-041).** `release-docs-gate` (`.gitlab-ci.yml:249-271`) ran the removal (`:265`), pip and the gate through the script. The `release` job ran: "Created fresh repository" (`GIT_STRATEGY: clone`, `:302`), the script's `git` under the allowlist, and `JOB-TOKEN` accepted on the protected tag. The job token did not appear in any log. **What it leaves:** the 10-minute `timeout` (`:257`) was not reached. That the removal hit the right path is unproved (SEC-T751-05).
15. to 18. As v11; the lines in `test_ci_hash_pins.py` (`:335`, `:381`, `:661`, `:125`) are unchanged.
19. **Corrected.** Changing the review date **no longer needs a test edit**: the mutation test reads the date from the file (T765; `test_ci_hash_pins.py:1287-1288`, read here). A digest bump passes. An `apk` pin needs an edit of `DRIFT_GATE_APK` (`:82`), and a Python minor bump an edit of `PINNED_IMAGE` (`:93`). **The CI header's recipe still does not say so** (`.gitlab-ci.yml:25-29`; TL-T761-08). The audit's remark on `build.py:12` was wrong (T765).
20. As v11.
21. As v11; the job shell's comment is now `.gitlab-ci.yml:266`.
22. As v11.
23. As v11; the `release` job's `script` line is now `.gitlab-ci.yml:309`.
24. to 26. As v11.
27. As v11; `CONTRIBUTING.md:224-226`.
28. **The first-tag list is `CONTRIBUTING.md:280-293`. Observed at the v10.0.0 tag:** both fetches worked with `--keep CI_JOB_TOKEN`, and the tree check passed. **Its limit holds:** the project is public, so the fetches do not prove that the job token was used. Also not in the text: `main` must not move between the tag and the tree check (TL-T761-12).
29. As v11. T759 used Docker with the user's approval, for that rehearsal only.
30. As v11.
31. **New. The release document carries the ADR-013 and ADR-014 Appendix A migration items and the frozen-state warnings** (SEC-T773-02, SEC-T780-05). **The release-doc gate checks a migration item only on `install.sh` lines that mention Cursor** (TL-T780-09), so these two items are checked by review. The `install.sh` pointer to `docs/releases/v11.0.0.md` must resolve before the tag: the gate refuses a missing document at its own tag (SEC-T773-01).
32. **New. The v10.0.0-only acceptances:** SEC-T660-01, SEC-T665-01 and SEC-T702-09 (item 2). The document records SEC-T657-01/SEC-T658-01 and K-15 as closed by removal, with the reopening condition: the Opencode live check (K-20, A-7, SEC-T658-02).
33. **New. The user's two SEC-T762-04 questions** (with TL-T761-10), ruled by the user before the gate, or stated as unruled.
34. **New. A-21 before the tag** (or by 2027-02-19, whichever is first). SEC-T756-02 stays LOW only if none of the listed settings is set.
35. **New. Both CA-chain jobs** (`ca-chain-check-python`, `ca-chain-check-node`, `.gitlab-ci.yml:158`, `:179`) must pass on the release commit, **including after the Node image bump**, which has not started (plan-147 § Facts). `ca-chain-check-node` runs in the default image, so it follows the bump.
36. **New. Run `python3 -m tests.functional.test_root_install_parity --print-drift` after any root refresh** (TD-T774-01); if it lists paths, touch the sources and refresh again. Batch Z's code residue is QA's "next release" (QA C1): fix it, or record why it waits.

### 6.3 Dates

Carried from v11 § 6.3, with additions and one correction.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced **(unverified)** | TD-T728-02 (batch M) |
| **2026-11-11** | The Node security advisory was due. **The bump has not started** (plan-147 § Facts). Both CA jobs must pass on the new digest | SEC-T756-05, -06; item 35 |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; end of TD-T697-07 | A-13, TD-T697-07 |
| **2027-01-30** | End of the Brave acceptance (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| **2027-01-31** | SEC-T657-01/SEC-T658-01's shown deadline (T762 Q4); moot if v11.0.0 ships first | section 2.3 |
| **2027-02-19** | SEC-T756-02's deadline as shown to the user ("and before any earlier image bump"); A-21 due | SEC-T756-02, A-21 |
| **2027-03-06** | **Correction:** the last day `test_the_review_date_is_present_and_fresh` passes. `ci_images_reviewed_on: 2026-11-06` (`.gitlab-ci.yml:20`) plus `MAX_REVIEW_AGE_DAYS = 120` (`test_ci_hash_pins.py:1255`), by reading; it fails from 2027-03-07. v11's 2027-02-19 and the orchestrator's 2027-02-19 (checkpoints 041, 042, plan-147) are stale (TL-T761-08) | the next image review |

The token dates repeat v6 to v11, which did not re-read them; nor did I **(unverified)**.

## 7. User actions

Carried from v11 § 7. A-7 narrows, A-19 is closed, and A-21 and A-22 are new. I did not re-check any other state.

| # | Action | State now | Due |
|---|---|---|---|
| A-2 | Remaining T665 live checks (TD-T697-03) | open | - |
| A-7 | Live checks: **Opencode denials, VS Code T690 servers, Copilot** (K-20, SEC-T658-02). The Gemini CLI and Pi items drop (section 2.4) | open. **It now also decides whether SEC-T657-01/SEC-T658-01 reopens** | before v11.0.0 is advisable (my suggestion; no source sets it) |
| A-10 | Empty `glab`'s stored login on other installs | as v11 | - |
| A-11 | Old `cwso-sia-executor` containers (SEC-T694-12) | as v11 | - |
| A-12 | Optional: `CWSO_ALLOWED_ORIGINS` | as v11 | - |
| A-13 | Renew the GitLab token and the CWSO bearer; renew TD-T697-07 | open | **2027-01-28**; **2027-01-29** |
| A-14 | Recheck the CWSO server's images after the next CWSO change | as v11 | at the next redeploy |
| A-15 | Optional: purge transcripts holding the dead CWSO secret | as v11 | - |
| A-16 | Before the next CWSO redeploy: `CWSO_HTTP_PUBLISH_ADDR` and the rest of v11's text | open | before the next CWSO redeploy |
| A-17 | | closed (v11) | - |
| A-18 | | closed (v11); its limit stands | - |
| A-19 | Delete both probe tags | **closed.** Checkpoint-041 records that the user deleted both. `git ls-remote --tags origin 'v9.0.0-gate*'` returned nothing on 2026-11-11 (plan-147 § Facts; re-run here with the same result). QA-T760-04 found 0 `gate` refs on 2026-11-07 | - |
| A-20 | A dedicated runner, for SEC-T741-17 | open | - |
| A-21 | **New.** The runner owner reports, **presence only**, whether `FF_GIT_URLS_WITHOUT_TOKENS` is on; whether any of `SSL_CERT_FILE`, `SSL_CERT_DIR`, `CURL_CA_BUNDLE`, `GIT_SSL_CAINFO`, `GIT_SSL_CAPATH` or `GIT_SSL_NO_VERIFY` is set as a CI variable; and whether the runner's `tls-ca-file` or `helper_image` is set (T767, T768; checkpoint-042) | open | **before the next tag or by 2027-02-19, whichever is first** |
| A-22 | **New.** Remove the `gemini` terminal auto-approval in your own `.vscode/settings.json:13`, and review the one Gemini mention in your `.claude/settings.json` (ADR-014 Q4, "I'll remove it myself (Recommended)"; SEC-T780-06). Git showed both files as modified locally at the start of this task. Neither file was opened, so whether the action is done is **(unverified)** | open | - |
| UA-T699-1 to -3 | As v11 | open (not re-checked) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- **Carried statuses**: v11's rows and lists, plus the sources in Based on. Greps and line reads on `358d292d` where cited "read here". Plan-147 § Facts is the only source for TD-T774-01, A-19's closure and the Node image bump. The only network call was `git ls-remote --tags` (A-19).
- **The search for changes**: a script extracted the 121 carried ids (1 open, 74 tracked-LOW, 46 accepted, with SEC-T657-01 and SEC-T658-01 as one) from v11's sections 2 and 3. It searched every line added in `92eb72c3..e098b7d9` outside `tests/golden/` and found 35 of them named. Each hit was read in context, and only those in sections 2.2 to 2.4 change a status or a text. The same lines were searched for new `<PREFIX>-T<nnn>-<n>` ids against all registers (section 1.2).
- **Counting**: 76 new ids from the reviews' findings tables and plan-147; their statuses as in section 3. Section 5 expands to 117 distinct ids: 73 carried tracked-LOW (74 less TD-T746-01), K-20, the 40 new tracked-LOW and the 3 new open. A script checked that every carried id and every new id occurs in this artifact, and that section 5's ids are exactly the open and tracked ones. Plan-147 gave no expected totals, so there is nothing to match them against.
- **Where the sources differ or leave a gap** (none changes a status beyond what section 1 states):
  - **Batch Q's closure.** Plan-145 says "settled here", and checkpoint-041 carries Q as tracked (section 2.2).
  - **The CI review date.** The checkpoints and plan-147 say 2027-02-19; the file and the test say 2027-03-06 (section 4.3).
  - **QA's Medium.** QA's scale is not the `SECURITY:*` scale. I count the three ids as open, and do not call them LOW (section 1).
  - **SEC-T762-05's "tell the user"** is not traced to a record of the telling **(unverified)**.
  - **"Approve both (Recommended)"** has no date in checkpoint-041.
  - **TD-T774-01** has no reviewer's grade.
- **What real jobs proved** (checkpoint-041; jobs not re-read here). Tag pipeline 3039977704, runner 19.5.3, Docker executor, pinned Python image. All three tag jobs passed. The `release` job ran this code for the first time: a fresh clone, the `CHANGELOG.md` entry below `[Unreleased]` (D-T710-2), `JOB-TOKEN` accepted. The Release body equals the document (56,774 characters). 0 job-token prefixes in the logs. Pipeline 3040148068: both CA jobs passed (ledger T766). T759's rehearsal ran the release job in the real image against a double, with `_ssl` holding the block (ledger T759).
- **What GitLab's APIs proved** (the orchestrator, read-only, not re-run here): the rendered Release holds 0 reference links (checkpoint-041). The tags (A-19) were read with `git ls-remote`, here too.
- **What is a hand trace**: review T768's OpenSSL loader point (SEC-T768-01, unverified on 3.5); T767's runner and helper-image source reading; review T780's notice and FIFO analysis (SEC-T780-03, -04); TL-T761-02 and TL-T763-01's reading of `scope_filter.py`, though QA and T763 ran it; the removal reviews' byte-equality and grep classifications, as their artifacts state.
- **Dropped from v11's unverified list, each with what settled it**: D-T710-2 in a real release job (observed); the `release` job's clone setting (observed); the npm step in a tag pipeline (no npm job runs on a tag; settled as "not applicable", the MR pipelines only); whether targets receive the gate script and the template (settled by T753's install: they do not); the runner version and executor (19.5.3, Docker, from the job logs; T767 § 4).
- **Still unverified**, carried from v11 (unless dropped above): the "do first" sources; Docker 29.9.2 on Ubuntu 20.04; the Go CA backport; the user's Docker Engine; the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates; GitLab's rendering of hidden HTML in a Release description (SEC-T716-03; only the reference links were observed); the musl lock beyond the MR pipeline; the Brave draft; Trivy adoption; the questions as shown to the user; whether the gate tolerates the template's pointer sentence; `markdown-it-py` 4.2.0's source; the deployed GitLab version; the `timeout` in a real job; that the removal hit the right path (SEC-T751-05); variable precedence at group and instance level; SEC-T730-06's location; and the rest of v11 § 8 as written there.
- **Unverified, new, from the plan-145 and plan-146 reviews**: `FF_GIT_URLS_WITHOUT_TOKENS`, the CA variables, `tls-ca-file` and `helper_image` on the runner (A-21); the helper image's digest and which image the runner used (T767 § 5); a live TLS connection to a disclosed host (T765 § Could not establish 1); non-amd64 images; OpenSSL 3.5's loading of `TRUSTED CERTIFICATE` blocks; T767's 4 against 3; the Node advisory's content (SEC-T756-05); Alpine 3.24.4's notes (SEC-T756-06); the operators' Brave environment (T756); K-35 on Opencode, Pi and Cline, which QA read and did not run (T763); TL-T773-03 for clients other than claude-code; review T780's own list (the 101/101 count, the deleted and renamed list, `merge_rule_findings`, `REMOVED_PLATFORM_DIRS`, the FIFO variant of `--update --dry-run`, `grep -D skip` portability, older hooks, SEC-T660-06's content, the settings-file hits, the full D1 grep); the Opencode per-agent denies in a live tool call (A-7); and every removal review's statement that no generator, installer or test run was its own.
- **Not run here**: the suite and the gates, which the orchestrator ran before each merge (checkpoint-042: green MR pipeline, the full suite in a clean worktree). No mutation and no full suite ran for this register.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `timeout 300 python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v11.md`; `plan-147-tracked-debt-register-v12.md`; `docs/tasks/task-T783.md`; `plan-145-release-v10.md`; `plan-146-ca-check-pi-removal-gemini-scoping.md`; `checkpoint-041-release-v10.0.0.md`; `checkpoint-042-plan-146-ca-pi-gemini.md`; the eighteen review artifacts under Metadata; `docs/tasks/completed-tasks.md` rows T753 to T782; by grep or line range, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/install.sh`, `scripts/check-ca-chains.sh`, `scripts/sync-wiki.py`, `implementation/PREREQUISITES.md`, `implementation/knowledge/mcp/servers.yaml`, `implementation/runtime/memory/README.md`, `docs/wiki/mcp-pin-bump-checklist.md`, `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_mcp_package_pins.py`. Decision IDs: ADR-011, ADR-012, ADR-013, ADR-014.
