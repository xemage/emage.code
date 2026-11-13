# Artifact: tracked-debt-register-v16.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v15.md` (681 ids; v15 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-158-brave-acceptance-v4-and-register-v16.md` (§ User decision, § Facts since v15, § Task Decomposition item 2, § T808 result) and `docs/tasks/task-T809.md` (the user's "2. v16 go"); `docs/plans/plan-155-v11-release-decisions.md`; `docs/plans/plan-156-apply-adr-015.md`; `docs/plans/plan-157-confirmation-as-validity-condition.md`; `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`; `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`; `docs/artifacts/security-review-t802-adr-015-apply-v1.md` (PASS); `docs/artifacts/security-review-t806-adr-016-apply-v1.md` (PASS); `docs/artifacts/brave-replacement-scouting-v1.md`; `docs/artifacts/brave-audit-acceptance-v4.md`; the ledger rows T799 to T808 in `docs/tasks/completed-tasks.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-012, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T809 (plan-158; the user's answer of 2026-11-13, verbatim: "2. v16 go"). **Date**: 2026-11-13.
- **Tree read**: branch `agent/devops-engineer/T808` at `c336ab63` (develop `c4b3f6cf` plus the plan-158 commits `86fa3f37`, `f9e1e5b2`, `68e5f332`, `c336ab63`; read here). The range for "lines added since v15" is `30f409df..c336ab63`: 46 files, 2058 lines added and 57 removed (read here). Outside the new plans, briefs, ADRs, reviews, the scouting record, the Brave record v4 and the ledger, the changed files are `implementation/knowledge/skills/validation-gates/SKILL.md` (lines 70 and 120), `implementation/knowledge/agents/release-manager.md` (line 183), their mirrors under `implementation/.<platform>/` and at the top level, `implementation/registry/index.json`, `tests/_baselines/root-install-drift.json`, `tests/functional/test_release_self_review_text.py`, `docs/decisions/ADR-012-medium-acceptance-record.md` (a header note), and, by T808, `scripts/audit-mcp-pins.py` (line 25), `docs/wiki/mcp-pin-bump-checklist.md` (lines 14 and 40) and `tests/functional/test_pin_bump_checklist.py`. `.gitlab-ci.yml`, `scripts/install.sh`, `implementation/PREREQUISITES.md`, `implementation/runtime/`, `CONTRIBUTING.md` and `docs/releases/` are not in the diff stat (read here), so v15's citations into them stand. The CWSO repository was not read: every CWSO status carries over from v15.
- **Review mode**: read-only. "Unchanged" means no task, review, plan outcome, ADR or ledger row since v15 names the id with a change of status, checked by searching the lines added in the range, outside `tests/golden/`, for every id-like token (section 8). A status taken from a review is the latest source's. "Read here" means a grep, line read or `git` query on `c336ab63`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository. Registers v1 to v10 were not re-read; v11 to v14 only by grep (the rows of SEC-T762-04 and TL-T761-10, § 6.2 items 2 and 33, the § 6.2 citations into the changed files, and the § 6.3 date rows). ADR-015, ADR-016, the two reviews, the scouting record and the Brave record v4 were read in part, by section or by grep, not in full (section 8). No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v15.
- **Batch letters**: no letter ends and no new letter. Q loses two ids and gains one; R gains three; N gains one (section 5). The batch of each new id is my suggestion.

## 1. Summary

v16 holds **690 ids**: the 681 of v15 and **9 new**. After v16: **514 fixed**, **49 accepted**, **9 obsolete**, **1 open**, **117 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, user; no grade). TD-T774-01, TD-T789-01, TD-T808-01 and TD-T808-02 have no reviewer's grade (the last two are the orchestrator's ids, which plan-158 calls LOW).
- **The accepted MEDIUMs are not open, but two of them are not settled for v11.0.0.** SEC-T702-09 is accepted by the user for v11.0.0 only, on record in `brave-audit-acceptance-v4.md`. For SEC-T660-01 and SEC-T665-01 the user's "Accept for v11.0.0" of 2026-11-12 is on record, but ADR-016 (accepted after it) makes the Security Engineer's confirmation, before the user is asked, a fourth validity condition, and no dated statement for v11.0.0 exists. This register does not rule whether that acceptance holds; section 2.3 states what must happen before the v11.0.0 gate. TD-T697-07 is unchanged.
- **Plans 155 to 157 fixed SEC-T762-04 and TL-T761-10** (the user's rulings, ADR-015, T801, T802) and **minted and fixed SEC-T802-01 to -04** (T802; fixed by T805 under ADR-016; confirmed by T806).
- **New and tracked-LOW**: SEC-T806-01, -02, -03 (T806) and TD-T808-01, -02 (the orchestrator, from T808).
- **Due before v11.0.0** (section 6.2): items 2 and 33 change; items 40 to 42 are new.
- **Not checked since v15**: SEC-T786-01's trigger (Alpine `nodejs` 24.22.3 in a `unit-tests` log) **(unverified)**; plan-158 § Facts.
- **Open for the user**: A-20, A-21 and A-22; the route of SEC-T735-06 and -07; any batch before the next tag; the v11.0.0 release plan (step 3 of plan-158 § User decision, not answered); after the Security Engineer's statement, the question on SEC-T660-01 and SEC-T665-01 again; and, in my view, the route of SEC-T806-01 and -02 if their text is to change (section 3.1). The SEC-T762-04 questions leave this list.

Arithmetic, from the v15 totals:

| Status | v15 | leaves | enters | v16 |
|---|---:|---|---|---:|
| fixed | 508 | | + 2 (SEC-T762-04, TL-T761-10) + 4 new (SEC-T802-01 to -04) | **514** |
| accepted | 49 | | | **49** |
| obsolete | 9 | | | **9** |
| open | 1 | | | **1** |
| tracked-LOW | 114 | - 2 fixed | + 5 new (SEC-T806-01 to -03, TD-T808-01, TD-T808-02) | **117** |
| **all** | **681** | | + 9 new ids | **690** |

Check: 514 + 49 + 9 + 1 + 117 = 690. Open or tracked: 117 + 1 = 118, the size of section 5.

### 1.1 Ids by v15 status and status now

| v15 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 114 | 2 | 0 | 0 | 0 | 112 |
| accepted | 49 | 0 | 49 | 0 | 0 | 0 |
| fixed | 508 | 508 | 0 | 0 | 0 | 0 |
| obsolete | 9 | 0 | 0 | 9 | 0 | 0 |
| **all v15 ids** | **681** | **510** | **49** | **9** | **1** | **112** |
| new in v16 | 9 | 4 | 0 | 0 | 0 | 5 |
| **all v16 ids** | **690** | **514** | **49** | **9** | **1** | **117** |

### 1.2 New ids by source and final status

| Source | new | fixed | accepted | obsolete | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| `security-review-t802-adr-015-apply-v1.md` § Findings: SEC-T802-01 to -04 (fixed per `security-review-t806-adr-016-apply-v1.md` § Status of SEC-T802-01 to -04) | 4 | 4 | 0 | 0 | 0 | 0 |
| `security-review-t806-adr-016-apply-v1.md` § Findings: SEC-T806-01 to -03 | 3 | 0 | 0 | 0 | 0 | 3 |
| `plan-158-brave-acceptance-v4-and-register-v16.md` § T808 result: TD-T808-01, TD-T808-02 (the orchestrator's ids) | 2 | 0 | 0 | 0 | 0 | 2 |
| **All new** | **9** | **4** | **0** | **0** | **0** | **5** |

**Other ids in the added lines.** A search of the 2058 added lines, outside `tests/golden/`, for `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `L-<n>` and `ADR-<nnn>` tokens, and for the short point labels, finds, beside the ids of sections 2 and 3:
- **v15 ids named with no change of status**: SEC-T702-08 (the Brave record v4: "not accepted here and not changed"); SEC-T735-08 (an input row of `task-T800.md`); SEC-T786-01, A-21 and A-22 (plan-158: not checked, or still open); SEC-T646-05, SEC-T646-06, K-17, SEC-T676-11 and SEC-T676-14 (labels on the two rewritten lines of `docs/wiki/mcp-pin-bump-checklist.md`, in the Brave record v4 and in `test_pin_bump_checklist.py`).
- **Labels that are not debt ids**: O1 to O7 (ADR-015's open points, ruled by the user's acceptance); O-A to O-D (ADR-016's, likewise); C1 to C4 (ADR-015's rows), D1 to D4 and W1 to W3 (ADR-016's rows); L-1 to L-6 (limits of the Brave records and of the scouting record).
- **No other id is minted**: none in the scouting record, ADR-015 or ADR-016, and no blocker record id. This register mints no id.

## 2. v15 ids re-checked

Every v15 `open`, `tracked-LOW` and `accepted` id (164) has a row or a list entry here: 1 + 114 + 49. The v15 `fixed` and `obsolete` ids stay as v15 records them.

### 2.1 v15 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range names it.

### 2.2 v15 `tracked-LOW` (114)

**Changed (2).**

| Id | v15 | now | Evidence |
|---|---|---|---|
| SEC-T762-04 | tracked-LOW, SECURITY:LOW, batch Q; two rules unruled, for the user (v12 § 3) | **fixed** | The user ruled both questions on 2026-11-12 (plan-155 § User decisions 3 and 4; section 4.1). ADR-015 records the rulings and was accepted by the user (plan-155 § Addendum 6). T801 applied rows C1 and C2 (commits `23de85b9`, `9b9ab6d1`; plan-156 § Outcome: C1 in `validation-gates/SKILL.md:70`, C2 in `release-manager.md:183`, verbatim by the orchestrator's word diff, pinned in `test_release_self_review_text.py`). T802: PASS. Plan-156 § Outcome: "SEC-T762-04, TL-T761-10: fixed by this plan". ADR-016 then changed the first rule's sentence at `SKILL.md:70` (rows D1, D2; T805; T806 PASS); both rules are in the text now (read here, section 6.2). Ledger T800 to T802 |
| TL-T761-10 | tracked-LOW, LOW, batch Q; the same question as SEC-T762-04's first (v12 § 3) | **fixed** | As SEC-T762-04, question 1: plan-155 § User decisions 3; ADR-015; plan-156 § Outcome |

**Unchanged (112 tracked-LOW; v15 and earlier stay the record of their text)**: the ids of v15 § 2.2's "Unchanged" list other than the two above, by batch: I 23, J 1, K 7, L 5, M 12, N 8, P 1, Q 8, R 4, S 1, V 15, X 10, Y 9, F 2, U 6. 23 + 1 + 7 + 5 + 12 + 8 + 1 + 8 + 4 + 1 + 15 + 10 + 9 + 2 + 6 = 112; with the 2 changed, 114. Those of them that occur in the added lines (SEC-T702-08, SEC-T735-08, SEC-T786-01; section 1.2) occur with no change. **SEC-T786-01's closing trigger was not checked** in the range (plan-158 § Facts; **(unverified)**); its check stays at v11.0.0 preparation (item 37). SEC-T735-08 (how the acceptance question is asked) stays tracked: ADR-015 and ADR-016 add to what the question must show and cite, and no source closes the id.

### 2.3 v15 `accepted` (49)

**Status unchanged for all 49; the qualifier changes for three.** The count stays 49: no source in the range moves any of them to `fixed` or `open`.

| Id | v15 | now | What the sources record |
|---|---|---|---|
| SEC-T702-09 | accepted MEDIUM, for v10.0.0 only | **accepted MEDIUM, for v11.0.0 only** | The user, 2026-11-12: "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0" (plan-155 § User decisions 2); T799 found no easy and good replacement (`brave-replacement-scouting-v1.md`); the user, 2026-11-12: "Keep the acceptance (Recommended)" (plan-155 § Addendum 5); the user, 2026-11-13: "1. Keep the acceptance" (plan-158 § User decision). Plan as shown: owner devops-engineer; fix: bump to the first Brave release above 2.1.4; deadline 2027-01-30 or that release, whichever comes first. The record is `docs/artifacts/brave-audit-acceptance-v4.md` (T808; no pin, launch argument, gate logic, advisory or expiry changed). npm's newest release was 2.1.4 on 2026-11-13 (T808 and the orchestrator; plan-158 § T808 result; not run here). The plan has a fix, so ADR-016's four conditions do not apply (T806 § Note, item 7). **Left for the release**: the acceptance in the release document's own form (item 2); TD-T808-02 |
| SEC-T660-01 | accepted MEDIUM, for v10.0.0 only | **accepted MEDIUM, for v10.0.0 only; for v11.0.0 the user's words are on record, and whether that acceptance holds under ADR-016 is not ruled here** | See below |
| SEC-T665-01 | accepted MEDIUM, for v10.0.0 only | as SEC-T660-01 | See below |

**SEC-T660-01 and SEC-T665-01: what the sources say.**
1. On 2026-11-12 the user answered **"Accept for v11.0.0"** to a question that showed the plan: owner the user (isolation) and devops-engineer (documentation); fix: none possible in the harness; deadline: review at token renewal on 2027-01-28, and a new acceptance at the release after v11.0.0 (plan-155 § User decisions 1).
2. ADR-015 (accepted the same day) allows such a plan under three conditions. Plan-155 § Outcome: the release document records, for each id, who could close it outside the harness, that no harness fix exists and which Security Engineer review confirms it, and the review date 2027-01-28 as the plan's deadline; for SEC-T660-01 also that the old deadline passed.
3. ADR-016 (accepted later on 2026-11-12) makes the Security Engineer's confirmation a fourth validity condition. **O-B**: the review must exist before the user is asked. **O-C**: at a later release an earlier review does not serve unseen; the Security Engineer confirms for the release asked about, by a new review or a dated statement that the earlier review still holds. **O-D**: the condition applies to every release verdict issued after ADR-016 was accepted, so for v11.0.0 a confirming review must be on record before that gate (`ADR-016…md:162-164`, read here).
4. The only Security Engineer review the orchestrator found that says no harness fix exists is `docs/artifacts/security-review-t756-accepted-mediums-v1.md`, written for v10.0.0 (a grep, not a full reading). **No dated Security Engineer statement for v11.0.0 exists** (plan-158 § Facts). I did not search for one myself **(unverified)**.
5. The orchestrator told the user on 2026-11-12 and 2026-11-13 that the v11.0.0 release plan will commission that statement first and then ask again, and that **the earlier answer is not treated as carried over**. The user has not yet answered on the release plan (plan-158 § Facts, § User decision). T806 § Note, item 3: "No agent may treat the earlier answer as carried over."

**What must happen before the v11.0.0 gate** (from ADR-016 O-D, plan-157 § Outcome and T806 § Note, items 1 to 6; not a ruling of mine):
- the release plan states whether a confirming Security Engineer review was on record before the question of 2026-11-12, naming artifact and date for each id;
- the Security Engineer gives, for v11.0.0, a new review or a dated statement that the earlier review still holds (both ids shipped in v10.0.0, so D2 applies; T806 is not that review);
- after that, the question is put to the user again, showing the same plan and citing the review, and the verdict records the user's new words verbatim with the date;
- the Conditions line names the review with its date, the dated statement if one is used, and the date the question was put (SEC-T806-02), and for SEC-T660-01 that the old deadline passed;
- 2027-01-28 is still ahead when v11.0.0 ships; if not, ADR-015 Rule 2 applies.

**Unchanged (46)**, with their v15 qualifiers: SEC-T657-01 / SEC-T658-01 (counted as one) and K-15 (close by removal at v11.0.0 unless the Opencode live check fails); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; the orchestrator-accepted residues TL-T773-01, TL-T780-01, TL-T780-07. 2 + 1 + 40 + 3 = 46; with the three rows above, 49. No source in the range names any of the 46.

## 3. New ids

Grades are the reviewers' own, except where the row says otherwise. "Read here" means a line read on `c336ab63`.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T802-01 | SECURITY:LOW | ADR-015's O3 (what the owner records on the review date) stood in the skill in a short form | **fixed** | T802 § Findings; plan-156 § Outcome. The user included W1 (section 4.1). T805 (`97e1c0b4`, `946a2a9a`): W1 at `validation-gates/SKILL.md:70`, pinned. T806 § Status: "fixed by W1". Ledger T805, T806 | — (minted in plan-156, fixed in plan-157) |
| SEC-T802-02 | SECURITY:LOW | "It covers" followed the passed-deadline sentence, so its subject was unclear; the sentence was unpinned | **fixed** | As above: W2 at `SKILL.md:70` ("An acceptance covers only the release"), pinned. T806 § Status: "fixed by W2" | — |
| SEC-T802-03 | SECURITY:LOW | The Security Engineer's confirmation stood outside "only when"; no text said an acceptance fails without it | **fixed** | The user: "confirmation should become a fourth validity condition" (plan-157 § User decision); ADR-016, accepted by the user; T805: rows D1 and D2 at `SKILL.md:70`. T806 § Status: "decided by the user (ADR-016) and fixed by D1 and D2"; SEC-T806-01 is its residue | — |
| SEC-T802-04 | SECURITY:LOW | The gate-input line at `SKILL.md:120` lacked the old plan's deadline | **fixed** | The user included W3; T805: W3 at `SKILL.md:120` ("and its plan's deadline", read here), pinned. T806 § Status: "fixed by W3" | — |
| SEC-T806-01 | SECURITY:LOW | (a) Row D2 does not itself say the dated statement comes before the user is asked; that follows only from D1. (b) "an earlier review" and "a later release" have no stated reference point | **tracked-LOW** | T806 § Findings: "Track"; a wording candidate with the same rule; "decide the route at the next edit of § Verdict Rules. Until then the release plan applies § Decision's reading". Plan-157 § Outcome | R |
| SEC-T806-02 | SECURITY:LOW | The `mitigation` slot at `release-manager.md:183` names the confirming review but not its date or the dated statement; the Release gate inputs do not list the review. O-B and O-C cannot be checked from the release document alone | **tracked-LOW** | T806 § Findings: "Track. Until a text change is decided, the release document names the review artifact with its date, the dated statement if D2 applies, and the date the question was put. A slot change touches ADR-015 row C2 and needs its own decision" (item 40) | R |
| SEC-T806-03 | SECURITY:LOW | The sentence "An acceptance never covers a security finding graded critical or high, …" at `SKILL.md:70` has no pin in `test_release_self_review_text.py`; it predates T805. Whether another test file pins it is **(unverified)** (the reviewer's mark; not checked here) | **tracked-LOW** | T806 § Findings: "Track. Add the sentence to the clause pins with one mutation … at the next edit of this test" | R |
| TD-T808-01 | no reviewer's grade; the orchestrator's id, "LOW, tracked" | `scripts/audit-mcp-pins.py` names the acceptance record by version in its usage text (`:25`, read here), so each new record version needs a script edit; T808's new test catches a stale name | **tracked-LOW** | plan-158 § T808 result | N |
| TD-T808-02 | no reviewer's grade; the orchestrator's id, "LOW, tracked" | The Brave record v4 does not extend the acceptance in time. If v11.0.0 is tagged after 2027-01-30, or after a Brave release above 2.1.4, the gate fails and the user must decide again | **tracked-LOW** | plan-158 § T808 result; `brave-audit-acceptance-v4.md:32` (read here). A date, in section 6.3 | Q |

### 3.1 Do SEC-T806-01 and -02 need the user's word?

My view; the orchestrator decides the route.
- **To track them: no.** The 2026-10-23 policy covers a LOW finding.
- **For v11.0.0: no.** Both are met by what the release plan and the release document do (items 2 and 40), which T806 itself prescribes "until a text change is decided".
- **To change the text: yes, for both.** SEC-T806-01's candidate keeps the rule, but the sentence is row D2 of ADR-016, quoted word for word in the skill and pinned against the ADR. SEC-T806-02's slot change touches ADR-015 row C2 in the same way. An accepted ADR is immutable, so either edit needs a new ADR that supersedes the row, and only the user accepts an ADR. Plan-157 gave the wording-only fixes W1 to W3 the same treatment (the user chose them and ADR-016 carries them).
- **SEC-T806-03: no.** It adds a pin for text that already stands; no rule and no ADR row changes.

## 4. Decisions since v15

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-12 | "Accept for v11.0.0" | SEC-T660-01 and SEC-T665-01, with the plan as shown (section 2.3). Given before ADR-016 | plan-155 § User decisions 1 |
| 2026-11-12 | "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0" | SEC-T702-09; typed by the user; conditional | plan-155 § User decisions 2 |
| 2026-11-12 | "Yes, with conditions (Recommended)" | SEC-T762-04 question 1 (also TL-T761-10): a plan's fix may be "none possible in the harness" only when the plan names who could close it outside the harness, states plainly that no harness fix exists, and sets a review date | plan-155 § User decisions 3 |
| 2026-11-12 | "Yes, a new acceptance cures it (Recommended)" | SEC-T762-04 question 2: a new, dated acceptance with a new plan replaces the old one; the release document must say that the old deadline passed | plan-155 § User decisions 4 |
| 2026-11-12 | "Keep the acceptance (Recommended)" | SEC-T702-09 after the scouting: accepted for v11.0.0 only, plan as shown. The other options were "Remove Brave entirely" and "Audit Tavily and Exa first" | plan-155 § Addendum 5 |
| 2026-11-12 | "Accept with all recommendations" | ADR-015, with the architect's answers to O1 to O7 | plan-155 § Addendum 6 |
| 2026-11-12 | "Continue" | In answer to "Say "continue" and I'll start with item 1" (apply ADR-015, with a security review). The reading is the orchestrator's (section 4.2) | plan-156 Based on |
| 2026-11-12 | "Root refresh approved" | The root refresh for the 7 declared paths (T803) | plan-156 § Addendum |
| 2026-11-12 | "confirmation should become a fourth validity condition" | SEC-T802-03. The user said nothing then about SEC-T802-01, -02 or -04 | plan-157 § User decision |
| 2026-11-12 | "Accept with all recommendations (Recommended)" | ADR-016, with the answers to O-A to O-D as the option showed them | plan-157 § User decisions on ADR-016, question 1 |
| 2026-11-12 | "W1 (SEC-T802-01),W2 (SEC-T802-02),W3 (SEC-T802-04)" | Which wording-only fixes go into the same change (multiple choice; the other option was "None") | plan-157 § User decisions on ADR-016, question 2 |
| 2026-11-13 | "Approving root refresh" | The root refresh for the 4 declared paths (T807) | plan-157 § Addendum |
| 2026-11-13 | "1. Keep the acceptance" and "2. v16 go" | Steps 1 and 2 of the orchestrator's list: the Brave record v4 (T808) and this register (T809). Step 3, the v11.0.0 release plan, was not answered | plan-158 § User decision |

**No longer unruled**: the SEC-T762-04 questions (with TL-T761-10). **Still for the user**: section 1, "Open for the user".

### 4.2 The orchestrator's rulings (not the user's)

| Item | Decision | Source | Effect |
|---|---|---|---|
| The reading of "Continue" | The word for plan-156 (apply ADR-015 with a security review); not approval of a root refresh, which was asked separately | plan-156 Based on, § Addendum | Plan-156, T801 and T802 |
| Answer 2 on SEC-T702-09 is conditional | "Easy and good" is not decided by an agent: the scout reports, and the orchestrator puts the result to the user | plan-155, "The orchestrator's reading" | T799; the user's "Keep the acceptance (Recommended)" |
| "An ADR-011 amendment" | Accepted ADRs are immutable, so a new ADR supersedes ADR-011 in part; only the user accepts it | plan-155, "The orchestrator's reading" | ADR-015; likewise ADR-016 for ADR-015 |
| W1 to W3 folded into T805 | After the user included them, the three wording fixes went into the same task and merge as D1 and D2 | plan-157 § Outcome | SEC-T802-01, -02, -04 fixed with -03 |
| T802's "44 to 73" note | A misreading: 73 is the new total and the 29 entries for T801 are the difference | plan-156 § Outcome | No finding |
| SEC-T660-01 and SEC-T665-01 | The earlier answer is not treated as carried over; the release plan commissions the Security Engineer's statement first and asks again | plan-158 § Facts; plan-157 § Outcome | Section 2.3; item 2 |
| No Security Engineer review of the Brave record v4 or of this register | The release security review reads both | plan-158 § Task Decomposition item 2 | Section 8 |
| The reading of "1. Keep the acceptance / 2. v16 go" | The word for steps 1 and 2 only; nothing here is a release, a tag or a root refresh | plan-158 § User decision | T808, T809 |
| TD-T808-01 and TD-T808-02 | Minted by the orchestrator from T808's suggestions, "both LOW, tracked" | plan-158 § T808 result | Section 3 |
| The batches of the five new tracked ids, and section 3.1 | **Mine** | this register | Section 5 |

### 4.3 Differences on the record

These stay as the sources state them.
- **Plan-156 against plan-157 on SEC-T802-01 to -04.** Plan-156 § Outcome records all four as "LOW, tracked"; plan-157 § Outcome records them as fixed. The later source governs; they never sat in a register as tracked.
- **ADR-015 row C1 against the live text.** ADR-015's C1 sentence about the Security Engineer's review is superseded by ADR-016 row D1; ADR-015 carries a header note and stays the record for the rest (plan-157 § Outcome).
- **Plan-155 § Outcome on SEC-T660-01 and SEC-T665-01** says "accepted MEDIUM for v11.0.0 only (decision 1)". It was written before ADR-016. Plan-157 § Outcome and plan-158 § Facts say the earlier answer is not treated as carried over. Section 2.3 records both and rules neither.
- **T806 § Note, item 2** takes "shipped in v10.0.0 under the user's acceptance" from the session record, unverified by the reviewer. v12 § 2.3 records both ids as accepted for v10.0.0 only (read here by grep), which agrees.

## 5. Open items by LOW batch

"Do first" as in v5; the flag's source stays **(unverified)** as v5 § 5 says. Batches not named as changed are carried from v15 without change. O and Z stay ended and are dropped from the table.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v15 § 5 | 23 | as v15 | as v15. **TD-T774-01 needs a grade first** (my suggestion) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v15 | as v15 |
| K | Security runtime | as v15 § 5 | 7 | as v15 | as v15 |
| L | CWSO helper scripts in emage.code | as v15 § 5 | 5 | as v15 | as v15 |
| M | CWSO repository | as v15 § 5 | 12 | as v15 | as v15 |
| N | Release tooling, second round | as v15 § 5; **new:** TD-T808-01 | 9 | as v15; devops-engineer for TD-T808-01 (my suggestion) | as v15; TD-T808-01 at the next version of the Brave record at the latest |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v15 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, SEC-T773-02, SEC-T780-05, TL-T780-09, SEC-T784-01, SEC-T791-01; **new:** TD-T808-02; **left:** SEC-T762-04, TL-T761-10 (fixed) | 9 | as v15; the orchestrator watches TD-T808-02's dates | **the v11.0.0 release** (items 2, 4, 10, 31, 36, 38, 39, 40 to 42) |
| R | Release-gate text, second round | as v15 § 5; **new:** SEC-T806-01, SEC-T806-02, SEC-T806-03 | 7 | orchestrator routes each; an ADR by solution-architect for -01 and -02 if the text is to change; devops-engineer or backend-developer for -03 (my suggestions) | the route of SEC-T735-06 and -07 is still to be settled before batch R; SEC-T806-01 at the next edit of § Verdict Rules, SEC-T806-03 at the next edit of the test (T806) |
| S | Release gate: the runner tag | SEC-T741-17 (the rest) | 1 | the user (A-20) | waits on the user's runner |
| V | Release gate after plans 142, 143 and 146 | as v15 § 5 | 15 | devops-engineer | as v15 |
| X | CI images, the CA control and runner settings | as v15 § 5 | 10 | as v15 | as v15 (item 37 for SEC-T786-01; A-21; item 35) |
| Y | Shipped text and records | as v15 § 5 | 9 | as v15 | as v15 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v15 | as v15 |
| U | Live checks and user | as v15 § 5 | 7 | the user or an authorised live session | A-2, A-7, A-11, A-15, A-22 |

Total 23 + 1 + 7 + 5 + 12 + 9 + 1 + 9 + 7 + 1 + 15 + 10 + 9 + 2 + 7 = 118 = 117 tracked-LOW + 1 open. Against v15's 115: Q - 2 + 1, R + 3, N + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T774-01, TD-T789-01, TD-T808-01 and TD-T808-02 have no reviewer's grade.

**Order, my suggestion only.**
1. In the v11.0.0 release plan, first: the Security Engineer's dated statement or new review for SEC-T660-01 and SEC-T665-01, then the question to the user again (item 2).
2. At v11.0.0 preparation: Q, with SEC-T784-01, SEC-T791-01 and TD-T808-02, in the release document; items 40 to 42; X's SEC-T786-01 check (item 37).
3. R's SEC-T806-03 with the next edit of the pin test; SEC-T806-01 and -02 together in one ADR, if the user wants the text changed.
4. Y's TD-T789-01, V's SEC-T751-06 and I's TD-T774-01, as v15.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v15 § 6.1 stand and stay the record. Since v15: SEC-T702-09 is accepted by the user for v11.0.0 only (`brave-audit-acceptance-v4.md`); the user's words on SEC-T660-01 and SEC-T665-01 for v11.0.0 are recorded in section 2.3, with what is still needed. No agent accepted a risk. The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 **2027-01-30 or the first Brave release above 2.1.4**; for SEC-T660-01 and SEC-T665-01 the plan shown names the review date **2027-01-28**, which under ADR-015 is the plan's deadline.

### 6.2 Next release checklist (v11.0.0, MAJOR)

Carried from v15 § 6.2, with its numbers. **Items 2 and 33 change; items 40, 41 and 42 are new.** Items not named here keep v15's text (and, through it, v14's to v11's).

**Citations re-read.** In the range, `implementation/knowledge/skills/validation-gates/SKILL.md` changed at `:70` and `:120`, and `implementation/knowledge/agents/release-manager.md` at `:183`; each hunk replaces one line by one line, so no line number in either file moves (read here: `git diff -U0`). The § 6.2 citations into them (one grep of v11 to v15 for line citations; only v11 § 6.2 has any, read here):
- `agents/release-manager.md:183` in v11 item 9 (the Conditions block, ADR-012 B3): **stands, with additions**. The slots `risk_accepted_by=`, `grade=`, `release=`, `mitigation=` and `deadline=` are as item 9 describes; `mitigation=` now also carries, for a "none possible in the harness" fix, who could close it outside the harness, the plain statement with the confirming Security Engineer review, and the review date; `deadline=` now also carries, where an earlier plan's deadline passed, the statement that it passed, its date and the release the old acceptance was given for (ADR-015 row C2; read here). Item 40 uses them.
- `agents/release-manager.md:46` in v11 items 11 and 12 (the independent checker; the closed list of what may change after the check): unchanged line, **stands** (read here).
- `skills/release-workflow/SKILL.md:171` in v11 item 12 is another file, with no diff in the range; **stands**.
- No item cites `validation-gates/SKILL.md` by line. Items that restate its § Verdict Rules (item 2) are rewritten below from the text now at `:70` and `:120`.
`docs/wiki/mcp-pin-bump-checklist.md` changed at `:14` and `:40`, one line for one line; the registers' only line citation into it, `:30` (v12 and v13), does not move and **stands**. `.gitlab-ci.yml`, `scripts/install.sh` and `implementation/PREREQUISITES.md` did not change, so items 14, 19, 21, 23, 35, 36 and 38 stand.

2. **Changed. The MEDIUMs shipped under an acceptance: SEC-T660-01, SEC-T665-01, SEC-T702-09.** No agent grants or carries one over.
    - **SEC-T702-09: answered.** Accepted by the user for v11.0.0 only (section 2.3). Left: the release document records the acceptance in its own form (the Conditions line, with the user's words verbatim and dated, the plan as shown, and the deadline), beside the pin-audit record v4 (ADR-011; plan-158 § T808 result); the gate command of v4 runs at the release; TD-T808-02's dates hold at the tag (item 42).
    - **SEC-T660-01 and SEC-T665-01: answered on 2026-11-12, and to be asked again.** Left, in this order (section 2.3): the fact whether a confirming review preceded that question; the Security Engineer's new review or dated statement for v11.0.0; the question to the user again, showing the same plan and citing the review; the user's new words in the verdict. Until then no agent treats the earlier answer as an acceptance that holds for v11.0.0.
    - SEC-T756-02 and SEC-T657-01/SEC-T658-01: as v12 item 2 (items 32 and 34).
    - Ask the way SEC-T735-08 says: name the release, record the plan as shown, show a deadline still ahead.
33. **Changed: answered.** The user ruled both SEC-T762-04 questions (with TL-T761-10); ADR-015 and ADR-016 are accepted and applied. Nothing is left to ask. Left: the release document follows the rules (item 40) and no longer states the questions as unruled.
40. **New. The ADR-015 and ADR-016 record duties, for SEC-T660-01 and SEC-T665-01** (plan-155 § Outcome; `release-manager.md:183`; T806 § Note). The Conditions line of each records:
    - who could close the finding outside the harness (the plan shown names the user, by isolation);
    - the plain statement that no harness fix exists, with the Security Engineer review that confirms it, **named with its date**, and, as v10.0.0 shipped both, the Security Engineer's **dated statement for v11.0.0** that the earlier review still holds, or the new review (ADR-016 rows D1 and D2; SEC-T806-02 asks for the dates);
    - that the confirmation came **before the user was asked**, with the date the question was put (O-B; SEC-T806-01, -02);
    - the review date **2027-01-28** as the plan's deadline, which must still be ahead when v11.0.0 ships; if it is not, ADR-015 Rule 2 applies (a new acceptance with a new plan);
    - for **SEC-T660-01**, that the earlier plan's deadline passed, its date, and the release the old acceptance was given for (ADR-015 O5; v12 § 2.3: the carried deadline "the sprint after v8.0.0" had passed before v10.0.0);
    - the user's words verbatim with the date, the grade, the release asked about, and the plan as shown with its owner (v11 item 9).
41. **New. The note of the T806 review, items 1 to 7**, is an input of the v11.0.0 release plan: items 1 to 3 are the steps of item 2 above; item 4, T806 is not the confirming review; items 5 and 6 are in item 40; item 7, the four conditions do not apply to SEC-T702-09, whose plan has a fix.
42. **New. The Brave record is v4** (`docs/artifacts/brave-audit-acceptance-v4.md`): the release gate reads it, and its seven `--accept` entries carry the expiry 2027-01-30. If v11.0.0 is tagged after 2027-01-30, or after a Brave release above 2.1.4, the gate fails and the user decides again (TD-T808-02). Check npm's newest Brave release again at release preparation.

### 6.3 Dates

Carried from v15 § 6.3 (through it, v13 § 6.3). `.gitlab-ci.yml` has no diff, so `ci_images_reviewed_on: 2026-11-11` and its failing day **2027-03-12** stand. Changed or added rows:

| Date | What | Ids |
|---|---|---|
| **2027-01-28** | GitLab token renewal (as before). **Added:** the review date of the plan shown for SEC-T660-01 and SEC-T665-01, which is that plan's deadline under ADR-015. It must still be ahead when v11.0.0 ships; on that date the owner records in the register whether a harness fix now exists and whether the outside closer is still right (ADR-015 O3, W1) | A-13; SEC-T660-01, SEC-T665-01 |
| **2027-01-30** | End of the Brave acceptance, or the first Brave release above 2.1.4 if earlier (as before; v4 does not move it). **Added:** a v11.0.0 tag after either needs the user's new decision | SEC-T702-09, SEC-T702-01 to -06; TD-T808-02 |

## 7. User actions

Carried from v15 § 7 unchanged. No source in the range changes a user action. **A-21 is still open** and A-22's state is still **(unverified)** (plan-158 § Task Decomposition: both stay open as far as the orchestrator knows; the two settings files were not opened). Not a lettered action, but waiting on the user: the word for the v11.0.0 release plan, and afterwards the question on SEC-T660-01 and SEC-T665-01 again.

## 8. Method, limits and validation

- **Carried statuses**: v15's rows and lists, plus the sources in Based on. Plan-158 § Facts and § T808 result are the only source for the merges (!674 to !679), their pipelines and suite runs, the ledger count (0 active, 604 completed after !679), the facts about SEC-T660-01 and SEC-T665-01 under ADR-016, and the ids TD-T808-01 and -02. `docs/tasks/completed-tasks.md` holds 605 task rows (604 and T808) and `active-tasks.md` holds only T809 (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 2058 lines added in `30f409df..c336ab63` outside `tests/golden/`; the result is section 1.2. Each v15 id found was read in its context, by line or by its source's section. As every other v15 id is absent from the added lines, no other status can have changed through a source in the range.
- **Counting**: 9 new ids (4 from T802, 3 from T806, 2 from plan-158). Section 5 expands to 118 ids: 117 tracked-LOW and 1 open. The batch sizes of unchanged batches are v15's, not recounted id by id here.
- **What real jobs and runs proved.** Source: plan-158 § Facts and § T808 result. I read no job log and ran no pipeline.
  - MRs !675 to !679, each at its verified commit: both pipelines green and the full suite in a clean worktree (2731, 2732, 2732, 2736, 2736 OK; skipped=25); `--print-drift` `[]` after !677 and !679.
  - T808 and the orchestrator, 2026-11-13: npm's newest Brave release is 2.1.4; by T808, the audit without `--accept` exits 1 with v3's seven advisories and with the seven entries exits 0.
- **What GitLab's APIs proved.** Nothing is cited beyond the pipeline results above; how those were read is not recorded **(unverified)**.
- **What is reading only**:
  - T802 and T806 in full: each ran nothing; the tests, gates, word diff, mirrors, registry and drift results are the orchestrator's evidence (each § What I did not verify);
  - the scouting record: nothing was run, pages were read through a summarising fetch, and several rows are from general knowledge (its L-1 to L-5); the orchestrator's three `npm view` checks are in plan-155 § Outcome;
  - my line reads, greps and `git` queries.
- **Still unverified**:
  - Carried from v15 § 8.
  - SEC-T786-01's trigger, unchecked since T786 (plan-158 § Facts).
  - From T802: ADR-011 not opened; wiki restatements other than `severity-and-grade-scales.md:34`; `skills/release-workflow/SKILL.md:113` not read; other test files pinning the unpinned sentences of `SKILL.md:70`; which commit added ADR-012's header note.
  - From T806: whether a confirming review was on record before the question of 2026-11-12; that both ids shipped in v10.0.0 under the user's acceptance (v12 § 2.3 agrees, section 4.3); whether another test file pins SEC-T806-03's sentence; other restatements of the superseded sentence outside the files it read.
  - From T808's record: the six-entry negative control, `--signatures`, `provenance` and the manual advisory read were not run for v4 (`brave-audit-acceptance-v4.md:89`).
  - From this register: the user's words beyond the plans' records; that no dated Security Engineer statement for v11.0.0 exists (plan-158's fact, not searched here); the full text of ADR-015, ADR-016, the two reviews, the scouting record and the Brave record v4 (read by section or grep); the full wording of the option description of plan-155 § Addendum 6 (read in part); the v15 batch membership behind "as v15 § 5"; any line citation that an item of v11 to v14 § 6.2 makes in a form my grep did not match.
- **Not run here**: the suite, the pipelines, `npm`, the audit script. No mutation and no full suite ran for this register.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v15.md`; `plan-158-brave-acceptance-v4-and-register-v16.md`; `docs/tasks/task-T809.md`;
  - by section or grep: `plan-155-v11-release-decisions.md`, `plan-156-apply-adr-015.md`, `plan-157-confirmation-as-validity-condition.md`, `ADR-015-medium-plan-without-fix-and-passed-deadline.md`, `ADR-016-security-engineer-confirmation-as-validity-condition.md`, `security-review-t802-adr-015-apply-v1.md`, `security-review-t806-adr-016-apply-v1.md`, `brave-replacement-scouting-v1.md`, `brave-audit-acceptance-v4.md`, registers v11 to v14, `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - by line: `implementation/knowledge/skills/validation-gates/SKILL.md:70` and `:120`, `implementation/knowledge/agents/release-manager.md:46` and `:183`;
  - `git diff --stat 30f409df..c336ab63`; `git diff -U0` of the two knowledge files, `docs/wiki/mcp-pin-bump-checklist.md` and `scripts/audit-mcp-pins.py`.
- Decision IDs: ADR-011, ADR-012, ADR-015, ADR-016.
