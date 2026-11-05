# Artifact: tracked-debt-register-v7.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v6.md` (517 ids; v6 and v5 stay the record for the text of every id that did not change, and, with v1 to v4, for every id that was `fixed` or `obsolete` there); `docs/plans/plan-134-tracked-debt-register-v7.md` and `docs/tasks/task-T737.md` (the user's "v7 go"); `docs/plans/plan-133-batch-h-release-gate-text.md`; `docs/artifacts/security-review-t734-t736-batch-h-v1.md`; `docs/decisions/ADR-012-medium-acceptance-record.md`; `docs/tasks/completed-tasks.md` (rows T734 to T736). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01, superseded in part), ADR-012 (Accepted 2026-11-04), ADR-007, ADR-008; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T737 (plan-134; the user's answer of 2026-11-05, verbatim: "v7 go"). **Date**: 2026-11-05.
- **Tree read**: branch `agent/tech-lead/T737` at `a4c3c7b3` (develop `b838c67c` plus the plan-134 commit). The commits since v6's merge `22c69513` are `d76a43f7` (batch H, squashed), its merge `b838c67c`, and `a4c3c7b3`. Nothing under `scripts/` or `tests/golden/` changed (`git diff --name-only`), so v6's lines in `verify-release-docs.py`, `publish-release.py` and `install.sh` stand. The CWSO repository was not read: every CWSO status carries over from v6.
- **Review mode**: read-only. A closure cites plan-133, the batch H review, a completed-task row or a grep on `a4c3c7b3`. "Unchanged" means no task, review or plan outcome since v6 names the id with a change of status, checked by searching the lines added in `22c69513..a4c3c7b3` for every carried id (section 8). The code was not re-checked unless a grep is cited. Anything not traced is **(unverified)**.
- **Reviewed tree**: the re-check read `e95f8932`; `git diff --stat e95f8932 d76a43f7` over `implementation/knowledge/`, `docs/releases/`, `docs/decisions/`, `tests/functional/` and `scripts/` is empty, so the reviewed text and pins are the merged ones. The whole diff has 57 files; the rest of it is outside those paths, and I did not itemise it.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository. Registers v1 to v5 were searched by grep for the correction in section 2.4, and not re-read. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5.
- **Batch letters**: H is executed (plan-133) and dropped. I, J, K, L, M, N, P, F and U keep their v6 scope. Q grows to 3 ids. **R** is new (section 5).

## 1. Summary

v7 holds **528 ids**: the 517 of v6 and **11 new**. After v7: **414 fixed**, **46 accepted**, **6 obsolete**, **1 open**, **61 tracked-LOW**.

- **Open above LOW: none.** The one open id is K-20 (live checks, user). Of the 11 new ids, SEC-T735-01 was MEDIUM and is resolved; the other 10 are LOW (review: 0 CRITICAL, 0 HIGH, 0 MEDIUM remaining). The five accepted MEDIUMs (section 6.1) are accepted, not open; under ADR-011 four of them need the user's new acceptance at the next release (section 6.2, item 2).
- **Batch H's 11 ids**: 10 fixed, 1 stays tracked with a new home (SEC-T693-07 in batch R). 10 + 1 = 11.
- **Due before the next release**: SEC-T735-08 and SEC-T735-09 (review § 4). This register's checklist carries what they require (section 6.2, items 2 and 10).

Arithmetic, from the v6 totals:

| Status | v6 | leaves | enters | v7 |
|---|---:|---|---|---:|
| fixed | 398 | | + 10 batch H + 6 new | **414** |
| accepted | 46 | | | **46** |
| obsolete | 6 | | | **6** |
| open | 1 | | | **1** |
| tracked-LOW | 66 | - 10 fixed | + 5 new | **61** |
| **all** | **517** | | + 11 new ids | **528** |

Check: 414 + 46 + 6 + 1 + 61 = 528. Open or tracked: 61 + 1 = 62, the size of section 5.

### 1.1 Ids by v6 status and status now

| v6 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 66 | 10 | 0 | 0 | 0 | 56 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 398 | 398 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v6 ids** | **517** | **408** | **46** | **6** | **1** | **56** |
| new in v7 | 11 | 6 | 0 | 0 | 0 | 5 |
| **all v7 ids** | **528** | **414** | **46** | **6** | **1** | **61** |

### 1.2 New ids by source

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t734-t736-batch-h-v1.md`, SEC-T735 | 9 | 5 | 4 |
| same, SEC-T736 | 2 | 1 | 1 |
| **All new** | **11** | **6** | **5** |

A search of the lines added in `22c69513..a4c3c7b3` finds no other new id: plan-133, ADR-012, briefs T734 to T736, the changed knowledge and the pins mint none. B1 to B3 and the `E1`, `E3` and `RULED_*` names are rows and test constants, not debt ids. This register mints none.

## 2. v6 ids re-checked

Every v6 `open`, `tracked-LOW` and `accepted` id (113) has a row or a list entry here: 1 + 66 + 46. The v6 `fixed` and `obsolete` ids stay as v6 records them.

### 2.1 v6 `open` (1)

K-20: **Unchanged**, open, batch U (A-7).

### 2.2 v6 `tracked-LOW` (66)

**Changed or re-homed (11, batch H; plan-133 § Outcome; rows T734 to T736; "review" is `security-review-t734-t736-batch-h-v1.md`; lines by grep on `a4c3c7b3`, under `implementation/knowledge/`)**

| Id | v6 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-T720-02 | tracked-LOW | **fixed** | - | ADR-012 B1, B3 (the user: "Add it as ADR-012 (Recommended)"); `skills/validation-gates/SKILL.md:70`, `agents/release-manager.md:183`, `agents/security-engineer.md:86`; review § 1 "They close SEC-T720-02 and -03". Nothing enforces them: SEC-T693-07. |
| SEC-T720-03 | tracked-LOW | **fixed** | - | ADR-012 B3, `release-manager.md:183`; published template points to the format, `docs/releases/_template.md:90` (SEC-T735-05); review § 1. |
| SEC-T720-04 | tracked-LOW | **fixed** | - | `release-manager.md:46`: the closed list and "No other text may be added after the check."; plan-133 § Outcome. |
| SEC-T720-05 | tracked-LOW | **fixed** | - | `agents/orchestrator.md:262`; review § 1 "Closed". No pin yet: SEC-T736-01 (rest). |
| SEC-T720-06 | tracked-LOW | **fixed** | - | `skills/release-workflow/SKILL.md:171, 233` (hotfix eligibility), as SEC-T735-04 changed it; review § 1. No pin yet for `:233`: SEC-T736-01 (rest). |
| SEC-T720-07 | tracked-LOW | **fixed** | - | `validation-gates/SKILL.md:70`, opening sentence; review § 1 "Closed", and `agents/tech-lead.md:100` does not contradict it. |
| SEC-T720-08 | tracked-LOW | **fixed** | - | `release-manager.md:46`, `orchestrator.md:218`, as SEC-T735-03 changed them; review § 1 "Closed". Narrows SEC-T693-07. |
| TD-T720-01 | tracked-LOW | **fixed** | - | `release-workflow/SKILL.md:117, 171, 233`, with SEC-T720-06 (plan-133 T735; § Outcome). |
| TD-T725-01 | tracked-LOW | **fixed** | - | `commands/validate-tasks.md:16`, `commands/validate-workflow.md:20`, `skills/testing-strategy/SKILL.md:168`, `release-workflow/SKILL.md:132`; review § 1 "Closed. Two remaining uses are conditional". No pin yet: SEC-T736-01 (rest). |
| TD-T671-legacy | tracked-LOW | **fixed** | - | P10: `skills/plan-approve-execute/SKILL.md:115` (T735); review § 1 "Consistent, and it fails closed". The four parked remarks had been fixed earlier: section 2.4. Resolves v5's and v6's **(unverified)** on the T547 remark: it is P9 to P12 (`docs/plans/plan-084-round-close-and-fired-triggers.md:53-56`; plan-133). |
| SEC-T693-07 | tracked-LOW | tracked-LOW | **R** | SEC-T720-08 and SEC-T735-03 narrow it and do not close it (plan-133 § Outcome). Batch H is finished, so it moves. The residual stays accepted by ruling with no edit (v3 § 7.2; plan-127): see section 5. |

**Unchanged (55 tracked-LOW; v6 and v5 stay the record of their text)**

| Batch | Ids | n |
|---|---|---:|
| I | SEC-T722-01, SEC-T722-02, SEC-T722-03, SEC-T722-04, SEC-T722-05, SEC-T725-01, SEC-T725-02, SEC-T725-03, SEC-T724-01, TD-T724-01 | 10 |
| J | SEC-T663-02 | 1 |
| K | SEC-T714-02, SEC-T714-04, SEC-T714-06, SEC-T714-08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 |
| L | SEC-T726-01, SEC-T726-02, SEC-T726-03, TD-T726-01, TD-T726-02 | 5 |
| M | SEC-T727-01, SEC-T727-02, SEC-T727-03, SEC-T727-04, SEC-T727-05, SEC-T728-01, SEC-T728-02, SEC-T728-03, TD-T728-01, TD-T728-02, TD-T728-03, SEC-T696-07 | 12 |
| N | SEC-T730-03, SEC-T730-04, SEC-T730-06, SEC-T731-03, SEC-T731-04, SEC-T731-05, SEC-T731-07, SEC-T731-08, SEC-T731-09, SEC-T732-01, SEC-T732-02 | 11 |
| P | SEC-T702-08 | 1 |
| Q | TD-T723-01 | 1 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 5 |

Total 55; with the 11 above, 66. SEC-T731-07 and SEC-T731-09 are named since v6 only in plan-133 § Not changed: the two fixes stay undone, because the user's answer was "H go".

### 2.3 v6 `accepted` (46)

**All unchanged**; basis as in v5 § 2.3 and v6 § 6.1. The four MEDIUMs named in ADR-012's Context are named there as the acceptances the next release must write; none has a new acceptance.

- **MEDIUM (5)**: SEC-T657-01 / SEC-T658-01 (one id), SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07.
- **LOW or INFO (41)**: K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, K-15, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07.

### 2.4 A correction to earlier records

Registers v1 to v6 and plan-127 carried older golden remarks as parked after they had been fixed: P13, P14 and P15 by T560 (`a6be07c6`), with P15 finished by T668, and T565 by T583 (`8dec82f3`). Nobody re-read them until the orchestrator did before batch H (plan-133 § The golden grant was not needed). The earlier registers are immutable and stay as written; this section is the correction.

How each record carried them, by grep:

- v1 to v3 name P14 and P15 under TD-T671-legacy, not re-read. v4 carries TD-T671-legacy without naming them.
- plan-127 (§ Outcome), v5 and v6 name P14, P15 and the remarks of CT rows T539 and T565 as parked. Plan-133 equates the T539 remark with P13.
- v1 also has a separate row, TD-T671-P13, recorded `fixed`. That row was right, so P13 stood as fixed under one id while the same fact stood as parked under TD-T671-legacy from plan-127 on.

No status count changes beyond TD-T671-legacy itself.

## 3. New ids

Source: `security-review-t734-t736-batch-h-v1.md` (§ 2 resolved, § 4 tracked; the reviewer's fix for each is in § 4). Fixed ids landed in squash `d76a43f7`. Owner per review § 4: "orchestrator, who routes each".

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T735-01 | MEDIUM | ADR-012 § Status, § Decision | The first draft recorded agent-drafted sentences as the user's decision. | fixed (the user: "Record it, no new question (Recommended)"; ADR-012 records the answer and how it arose) | - | - |
| SEC-T735-02 | LOW | ADR-012 § Decision, B1, B3 | A deadline that passes without moving was not covered. | fixed (the user: "Add the sentence (Recommended)"). Residual SEC-T735-08 | - | - |
| SEC-T735-03 | LOW | `release-manager.md:46`, `orchestrator.md:218` | The independence clause had no effect, an ambiguous scope, and no route when the checker edits. | fixed | - | - |
| SEC-T735-04 | LOW | `release-workflow/SKILL.md:171, 202, 205` | Hotfix eligibility: no check that the issue is in the released version, no one to confirm it, "no design impact" stated as fact. | fixed | - | - |
| SEC-T735-05 | LOW | `docs/releases/_template.md:90` | The Conditions slots were missing from the published template. | fixed. Residual SEC-T735-09 | - | - |
| SEC-T735-06 | LOW | `validation-gates/SKILL.md:70`; `release-manager.md:46, 183` | "As shown to the user" has no source: an agent writes the plan into Conditions, and nothing requires comparing it with what was shown. | tracked-LOW | orchestrator routes | R |
| SEC-T735-07 | LOW | `validation-gates/SKILL.md:70` | B1 puts the owner sentence before "It covers only the release it was given for", so "It" no longer points clearly to the acceptance. | tracked-LOW | orchestrator routes | R |
| SEC-T735-08 | LOW | `validation-gates/SKILL.md:70`; `tracked-debt-register-v6.md:203` | If a carried plan's deadline has already passed when the user is asked, the text does not say whether the new acceptance cures it. v6's checklist omitted the release version and "as shown to the user". | tracked-LOW | orchestrator routes (release-manager suggested) | Q |
| SEC-T735-09 | LOW | `docs/releases/_template.md:90`; `release-manager.md:46` | Deleting the pointer sentence after the check makes the check stale. It fails closed. | tracked-LOW | orchestrator routes (release-manager suggested) | Q |
| SEC-T736-01 | LOW | `tests/functional/test_release_self_review_text.py` | The rest: no pin for B2 (`security-engineer.md:86`), SEC-T720-05 (`orchestrator.md:262`), `release-workflow:233`, or TD-T725-01. B1, B3, the hotfix eligibility and the pointer sentence are pinned (the test's docstring, `:16-21`). | tracked-LOW (the rest) | orchestrator routes | R |
| SEC-T736-02 | LOW | plan-133 § Changes after the first security review | The Changelog Preview wording had no recorded source. | fixed (recorded and anchored there) | - | - |

## 4. Decisions since v6

### 4.1 The user's (words verbatim as recorded)

These are the option labels plan-133 and ADR-012 record. The reviewer did not verify the question shown to the user beyond the orchestrator's message and ADR-012 (review § 5), and neither did I **(unverified)**. Each row claims only what its question asked.

| Date | Words | What the question asked, and the effect | Source |
|---|---|---|---|
| 2026-11-04 | "H go" | Run batch H: plan-133, T734 to T736. It did not cover the two batch N fixes | plan-133 Based on, § Not changed |
| 2026-11-04 | "Add it as ADR-012 (Recommended)" | SEC-T720-02 and -03: the wording quoted in ADR-012's Status. ADR-012 Accepted | plan-133 Based on; ADR-012 Status |
| 2026-11-04 | "Grant it for batch H" | A protected-path edit for the parked golden remarks. **Given, not used**: all four were already fixed, nothing under `tests/golden/` changed, baseline v22 stands | plan-133 § The golden grant, § Outcome |
| 2026-11-04 | "Yes, refresh in this MR (Recommended)" | The root refresh in this merge request. Done, drift list empty | plan-133 Based on, § Outcome |
| 2026-11-04 | "Record it, no new question (Recommended)" | A change of the plan's owner; the option's description also said that moving a deadline earlier or finishing sooner needs no new acceptance. Resolves SEC-T735-01 | ADR-012 Status; plan-133 § Changes after the first security review |
| 2026-11-04 | "Add the sentence (Recommended)" | The sentence "A deadline that passes before the release ships counts as moved later". Resolves SEC-T735-02 | same |
| 2026-11-04 | "Fix the three now (Recommended)" | SEC-T735-03 to -05 (row T735). The same label in v6 § 4.1 is another answer, on batch G | row T735; plan-133 § Changes |
| 2026-11-05 | "v7 go" | plan-134, T737 (this register) | plan-134 Based on |

### 4.2 Other decisions (not the user's)

| Id or item | Decision | By | Effect |
|---|---|---|---|
| TD-T671-legacy, P10 | `APPROVED_WITH_CHANGES` = Revise; "No answer other than Approve or `APPROVED` starts execution"; `commands/new-project.md` does not change (ADR-007) | the orchestrator's ruling (plan-133, T735) | `plan-approve-execute/SKILL.md:115` |
| SEC-T736-02 | "Changelog Preview" added to the closed list; hotfix lines `:167, 172` aligned | orchestrator (plan-133 § Changes) | `release-manager.md:46` |
| SEC-T693-07 | No edit | ruling of v3 § 7.2 and plan-127, carried by plan-133; not re-put to the user | batch R |
| Batches Q and R | SEC-T735-08 and -09 join Q; R is new; H is dropped | plan-134 | section 5 |
| SEC-T731-07, SEC-T731-09(a) | Fix before the next tag | **the tech lead's recommendation only**; the user has not ruled on it | section 5 |

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. I, J, K, L, M, N, P, F and U are carried from v6 without change.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | **SEC-T722-03 (do first)**, **SEC-T725-02 (do first)**, SEC-T722-01, -02, -04, -05, SEC-T725-01, -03, SEC-T724-01, TD-T724-01 | 10 | devops-engineer; backend-developer (SEC-T724-01, TD-T724-01) | next installer or generator change; SEC-T725-02 before the release that ships T725 (recommendation) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | devops-engineer | its own task (five test files, documents and live evidence change; plan-128) |
| K | Security runtime (`security-audit` servers) | SEC-T714-02, -04, -06, -08, SEV-T690-02 (pinned runtime package), SEV-T690-04 ((d) Copilot), SEC-T665-07 (if reopened) | 7 | devops-engineer; technical-writer (wiki residual of SEC-T714-06) | next change to `implementation/runtime/security/`; SEC-T665-07 on its reopening conditions |
| L | CWSO helper scripts in emage.code | SEC-T726-01 to -03, TD-T726-01, TD-T726-02 | 5 | devops-engineer | next change to the CWSO helper scripts; TD-T726-02 before the next Proxmox setup |
| M | CWSO repository | **SEC-T728-01 (do first)**, **SEC-T727-01, -02 (do first)**, SEC-T727-03 to -05, SEC-T728-02, -03, TD-T728-01 to -03, SEC-T696-07 ((b) fuel/epoch) | 12 | devops-engineer (CWSO; agent branch from CWSO `origin/develop`, MR into CWSO `develop`) | next CWSO change; TD-T728-02 adoptable since **2026-11-04**; TD-T728-01 in the next CWSO release notes; SEC-T696-07(b) before untrusted modules are accepted |
| N | Release tooling, second round (`publish-release.py`, `verify-release-docs.py`, CI locks and the npm step) | **SEC-T731-09**, SEC-T730-03, -04, -06, SEC-T731-03, -04, -05, -07, -08, SEC-T732-01, -02 | 11 | devops-engineer (batch G review § 4) | next fixing round; no source binds it to a release; see below |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines; the orchestrator offers the draft (plan-126) | when the user reopens it: "Keep it tracked" sets no date. The natural next look is the Brave review of section 6.3 (tech-lead's suggestion; no source sets it) |
| Q | Next release document | TD-T723-01, **SEC-T735-08**, **SEC-T735-09** | 3 | release-manager (TD-T723-01, v6); orchestrator routes the two SEC ids (review § 4). Suggested, no source sets it: release-manager, because they shape the release document | the next release document. **SEC-T735-08 and -09 before the next release starts** (review § 4; section 6.2, items 2 and 10); TD-T723-01: item 4 |
| **R** (new) | Release-gate text, second round | SEC-T735-06, SEC-T735-07, SEC-T736-01 (the rest), SEC-T693-07 | 4 | orchestrator routes each (review § 4). Suggested, as in T735 and T736, no source sets it: technical-writer for text, devops-engineer for pins | none set: review § 4 dates only SEC-T735-08 and -09. Read here as the next change to the release-gate text; see below |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 10 + 1 + 7 + 5 + 12 + 11 + 1 + 3 + 4 + 2 + 6 = 62 = 61 tracked-LOW + 1 open. No open item is above LOW.

**Batch N, in short.** Carried from v6; `scripts/` did not change, and `:522` was read again on `a4c3c7b3`.

- **SEC-T731-09(a) is the one-line fix the reviewer gave**: at `verify-release-docs.py:522` change `block[0].search(line, block[1])` to `block[0].search(line)` (the fix is not run here). Its false PASS needs a **crafted release document**, one that holds such a comment together with an anchor. Part (b) needs `markdown-it-py` in the gate or a documented residual, and the two claims at `:479, 534` need correcting either way.
- **SEC-T731-07**: the reviewer's fix is one more entry in the `check_line_breaks` list. It too needs a crafted file, here a crafted `install.sh`.
- **Recommendation (tech-lead, advice only, no source sets this, and the user has not ruled on it)**: do SEC-T731-07 and SEC-T731-09(a) before the next tag, because both are small and the next release runs this gate. It is not a condition; the review passed with them tracked. Plan-133 § Not changed left them out because the user's answer was "H go".

**Batch R, in short.**

- **SEC-T735-07: confirm the route first.** The reviewer's fix, "An acceptance covers", changes ADR-011's A1 text, and accepted ADRs are immutable (ADR-012 Status). The route is not settled; the review says only to confirm it.
- **SEC-T735-06** has the same question (tech-lead's reading, no source says so): its fix, that `mitigation` cites where the plan was shown, changes the Conditions line, which is ADR-012's row B3. The top-level session's comparison would be a new duty too.
- **SEC-T736-01 (the rest)** needs pins and mutations only, in the style of T736, and no knowledge text.
- **SEC-T693-07 has no text fix**: "the independent check is a duty in the role text, not an enforced control" (plan-133), and the residual is accepted by ruling with no edit. Batch R must not edit for it. It closes only if an enforced control is built, and nothing here proposes one.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 § 6.1 and v6 § 6.1 stand unchanged and stay the record. No acceptance was added or renewed by batch H. What changed is the record a new acceptance must hold: ADR-012 replaces rows A1, A8 and A12 of ADR-011 in part. The rest of ADR-011 stands: only the user accepts, one release only.

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 pin audit **2027-01-30 or the first Brave release above 2.1.4**; SEC-T702-09, SEC-T660-01, SEC-T665-01 and the SEC-T657-01/SEC-T658-01 remainder: **the next release needs the user's new acceptance** (ADR-011, ADR-012).

### 6.2 Next release checklist

Carried from v6 § 6.2, renumbered: items 1 to 4 keep their numbers, v6 item 5 is dropped (batch H did it), and v6 items 6 to 9 are now 5 to 8. Item 1 loses TD-T725-01 (fixed), item 2 gains SEC-T735-08. Items 9 to 13 are new. Lines read on `a4c3c7b3`, under `implementation/knowledge/` unless the path starts at `docs/`.

1. **Migration item T725 (TD-T671-P5)** in the release document: authoring-only commands are no longer installed into target projects; commands declare `audience: authoring | target | both`; today only `/prepare-release` (five platform paths listed in plan-128 § Outcome); `--update`/`--projections-only` deletes an existing copy (a dry run prints the `rm`); an authoring checkout (`implementation/registry/index.json`) keeps them; a target that used `/prepare-release` keeps its own copy under another file name; `.generated-manifest.json` gains `authoringOnly`; the generator refuses a command without a valid `audience:`.
2. **ADR-011 re-acceptances**: the Release Gate input lists every MEDIUM an earlier release shipped under the user's acceptance and not yet fixed (SEC-T720-01 fix, `validation-gates/SKILL.md`): **SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09**. Each one is fixed, or the user accepts it again for this release, verbatim and dated, with its remediation plan (owner, fix, deadline). No agent grants or carries one over.
   - **When asking the user to re-accept any of these four (SEC-T735-08; ADR-012): name the release, record the plan as shown, and show a deadline still ahead.** The rule text does not say whether a new acceptance cures a deadline that has already passed, so do not put that case to the user as if it were settled.
   - Each carried plan's actual deadline was not verified by the reviewer (review § 5) or here **(unverified)**: read it before asking.
3. **New verdict fields** (R4, R10): `Issued at commit` and `Independent check` (`docs/releases/_template.md:87-88`; `commands/prepare-release.md:59-60`). The independent check row must be present, current and not FAIL (SEC-T693-02).
4. **TD-T723-01 (batch Q)**: the release document cites current `install.sh` lines. `docs/releases/v9.0.0.md:86` cites `install.sh:1300`, and `:75` cites `install.sh:1285-1302`, which v5 did not mention. On `a4c3c7b3` the advice is `scripts/install.sh:1297-1300` and the pointer is `:1301`; re-read them when the document is written.
5. **Brave**: if the release falls after 2027-01-30 or after a Brave release above 2.1.4, the pin audit needs a new acceptance version or the bump first.
6. **D-T710-2**: confirm in the release job that the `CHANGELOG.md` entry lands below `[Unreleased]` (fixed in code by T716; not yet observed in a tag pipeline).
7. **Visible changes of batch G** (plan-131 § Outcome), for the release document and its author:
   - `CHANGELOG.md` entries now show `\#42`, `\@user` and URLs in backticks in their source, and `(#42)` no longer links to the issue.
   - Release documents need a blank line or an ATX heading before the Cursor item, and no trailing comment on `## Migration Guide`. Those shapes are deliberate false FAILs. The "lacks its Cursor migration item" message does not mention the blank-line rule; `--help` does.
   - Checked documents may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`. They are the tag's release document and the three marker files (`verify-release-docs.py:41-45, 622`).
8. **Not verified live in plan-131; watch these in the release**:
   - how GitLab renders the escaped references and code spans;
   - the npm step (`npm ci --ignore-scripts --prefix ci/js`) in a tag pipeline;
   - the lock on the musl image beyond the MR pipeline.
9. **The Conditions block** (`agents/release-manager.md:183`, ADR-012 B3): an accepted `SECURITY:MEDIUM` fills `risk_accepted_by=` with the user's words verbatim and the date, `grade=`, `release=` (the version the user was asked about), and `mitigation=` with the plan as shown to the user, its owner and fix, and the current owner if it has changed; `deadline=` holds the plan's deadline.
10. **The template's pointer sentence** (`docs/releases/_template.md:90`; SEC-T735-09): remove it before the independent check, or leave it. Deleting it after the check makes the check stale. That the gate tolerates the leftover sentence is T736's report; the reviewer did not verify it (review § 5).
11. **The independent checker** (`agents/release-manager.md:46`): "The checker has not authored or edited the release files for this release; if the checker has, the row counts as missing." The orchestrator or the top-level session will often be ineligible, so `@tech-lead` is the practical default (review § 1; plan-133 § Outcome). If the checker edited the files, another eligible checker re-runs it.
12. **Batch H changes a release author sees**:
    - after the check, only the closed list in `agents/release-manager.md:46` may change ("No other text may be added after the check"); it includes "Changelog Preview (a summary of the checked changelog, nothing new)";
    - hotfix eligibility (`skills/release-workflow/SKILL.md:171`): the issue is present in the released version, and is graded critical or high on its own scale, or, whatever its grade, is a breach of an Immutable Security Constraint or a required control omitted, removed, disabled or weakened, which `@security-engineer` confirms. A fix with design impact does not take the fast track (`:202`).
13. **Not verified in batch H**: whether targets receive `scripts/verify-release-docs.py` and `docs/releases/_template.md` (review § 1). The migration note must not assume that they do. A grep of `scripts/install.sh` finds no `rsync` or `cp` line naming `scripts` or `docs`, and its one mention of the gate script is a comment (`:1296`). That is a grep and not an install, so the question stays **(unverified)**.

### 6.3 Dates

Carried from v6 § 6.3. Plan-133 adds none.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced; CWSO not read **(unverified)** | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v6, which did not re-read them; nor did I **(unverified)**.

## 7. User actions

Carried from v6 § 7. Plan-133 adds none and closes none; I did not re-check any state.

| # | Action | State now | Due |
|---|---|---|---|
| A-2 | Remaining T665 live checks (TD-T697-03; design checks 4, 5) | open | - |
| A-7 | Live checks Gemini CLI, Opencode denials, VS Code T690 servers, Pi lists (K-20, SEC-T658-02) | open | - |
| A-10 | On every other install: empty `glab`'s stored login and revoke its OAuth authorization if `GITLAB_TOKEN` is used | open (done on the user's devcontainer, v3) | - |
| A-11 | Remove or recreate any `cwso-sia-executor` container from the old compose definition (SEC-T694-12) | open for other hosts; none on the CWSO server | - |
| A-12 | Optional: replace the CWSO server's local compose override with `CWSO_ALLOWED_ORIGINS` | open, optional; now also subject to the T727 origin checks (A-16) | - |
| A-13 | Renew the GitLab token and the CWSO bearer token; renew the TD-T697-07 acceptance with the new bearer | open | GitLab **2027-01-28**; CWSO bearer **2027-01-29** |
| A-14 | Recheck that the CWSO server runs the merged images after the next CWSO change | due again (v5): CWSO develop moved to `6630ecb` (MR !218); do it with A-16 | at the next redeploy |
| A-15 | Optional: purge local session transcripts that hold the dead CWSO secret (SEC-T694-10, SEC-T695-06) | open, optional | - |
| A-16 | **Before the next CWSO redeploy** (`git pull` plus `docker compose up -d`), or the server loses LAN access: set `CWSO_HTTP_PUBLISH_ADDR` to the all-interfaces address in `deploy/.env`, or add a `ports: !override` entry to the local override (exact text in plan-129 § Outcome); make sure the JWT secret is at least 32 bytes; make sure the `CWSO_ALLOWED_ORIGINS` entries pass the new checks. The loopback guarantee needs Docker Engine 28 or later (SEC-T727-04; the user's version **(unverified)**) | open | before the next CWSO redeploy |
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open (unchanged since v4; not re-checked) | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open (same) | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open (same) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- **Carried statuses**: v6 rows and lists, plus plan-133, rows T734 to T736 and the batch H review. Greps on `a4c3c7b3` where cited.
- **Counting**: a script takes the 113 carried ids from v6 §§ 2.1 to 2.3 and 3, checks that each occurs in sections 2.1 to 2.3 of this register, counts the rows of sections 2.2 and 3 by status, and expands section 5 to 62 distinct ids, equal to the carried ids still open or tracked plus the 5 new. The expected counts of plan-134 were derived this way and match.
- **Where the sources differ or leave a gap** (none changes a status):
  - **SEC-T735-08 and -09.** The reviewer's fix for each is that the next register's checklist says it, and section 6.2 now does. They stay tracked-LOW all the same, as plan-133 and plan-134 expect, until a release has applied them. For SEC-T735-08 the gate text also still does not say whether a new acceptance cures a passed deadline, which no fix proposes to change.
  - **The correction.** Plan-134 says "Registers v1 to v6" carried all four remarks, and names T560 and T583. The records are narrower, and P15 also needed T668 (plan-133): section 2.4.
  - **SEC-T693-07.** Plan-127 says "stays accepted by ruling"; v3 to v6 and plan-133 keep the id `tracked-LOW` with the residual accepted by ruling. This register keeps `tracked-LOW`. It belongs to R by plan-134, though no R text edit applies to it (section 5).
  - **Review § 4 gives the owner only as "orchestrator, who routes each".** The worker names in Q and R are v6's for TD-T723-01 and my suggestion for the rest, marked so.
  - **Target receipt.** Plan-134 attributes the open question to plan-133; the sentence that marks it **(unverified)** is in review § 1.
- **Unverified**, carried from v6: the source of the "do first" flags other than the fixed SEC-T716-01; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates; which three gaps "Fix now in this batch (Recommended)" covered (v6 § 8); live GitLab rendering (SEC-T716-03); the npm step in a tag pipeline; the lock on the musl image beyond the MR pipeline; whether the orchestrator's draft of the upstream report was ever shown to the user; adoption of Trivy 0.76.1.
- **Unverified**, new: the questions shown to the user beyond ADR-012 and plan-133 (section 4.1); each carried plan's actual deadline (review § 5); whether the gate tolerates the leftover pointer sentence (T736's report, review § 5); whether targets receive the gate script and the template. The pins' mutation proof, the suite and `scorecard.py --check` were run by the orchestrator before the merge (review § 5; plan-133 § Outcome) and not re-run here. The reviewers' own unverified lists stand as written in their artifacts.
- **Resolved since v6**: the T547 remark of TD-T671-legacy (plan-133; `docs/plans/plan-084-round-close-and-fired-triggers.md:53-56`).
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v6.md`; `plan-133-batch-h-release-gate-text.md`; `plan-134-tracked-debt-register-v7.md`; `docs/tasks/task-T737.md`; `completed-tasks.md` rows T734 to T736; `security-review-t734-t736-batch-h-v1.md`; `ADR-012-medium-acceptance-record.md`; the header line of ADR-011; by grep only, the SEC-T693-07 lines and the TD-T671-legacy and P13 to P15 lines of v1 to v5 and plan-127, and the P9 to P12 lines of plan-084. Decision IDs: ADR-011, ADR-012; ADR-007 and ADR-008 as plan-133 cites them, not read here.
