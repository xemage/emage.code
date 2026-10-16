# Artifact: adr-008-status-and-severity-scales-v1.md

> Immutable once produced; revisions bump `<N>`. Decision only; held for the user. Nothing in this file is applied until the orchestrator relays the user's answer to the question in § 1.4.

**Based on:** `docs/tasks/task-T634.md`; `docs/decisions/ADR-008-knowledge-document-authority.md` (all of it read, at develop `4c5b43e`); `docs/decisions/_template.md`, `ADR-001`, `ADR-002`, `ADR-004`, `ADR-005`, `ADR-006`, `ADR-007` (headers only); `AGENTS.md` (worktree root copy, whole file); `docs/artifacts/release-v8-audit-v1.md` (whole file; C-8 at `:227-232`, Migration table M-6 at `:159-172`); `docs/tasks/completed-tasks.md` (T581 row at `:385`, T580-T584 rows at `:386-389`); the scale sources listed in § 2 (all read in the worktree). Requirements/architecture versions: not applicable (documentation decision). Decision IDs referenced: ADR-007, ADR-008; proposed ADR-009 (§ 1.3).

**Author / mode:** Solution Architect, no shell, no commit. Edited: this file and the `**Status:**` line of the T634 brief. No ADR, knowledge file, golden path or `.claude/` file was touched. `plan-121` (the brief's first input) was **not** read **(unverified)**; the brief's own text was used for it.

**Basis marker:** every `file:line` below was read in this worktree. Citations are to the **source** files under `implementation/knowledge/` (the authority per ADR-008 "Projections"); the installed `.claude/rules/*` projections have a different line offset because the frontmatter is dropped **(projection line numbers unverified)**. Anything not re-read is marked **(unverified)**.

---

## 1. The ADR-008 Status block

### 1.1 The two clauses

`docs/decisions/ADR-008-knowledge-document-authority.md`, header (lines 5-10):

| Line | Text (verbatim) |
|---|---|
| 5 | `- **Status**: Accepted. The user approved it on 2026-10-02 ("Accept ADR-008 (Recommended)"), after the three review decisions recorded under § Context. Accepted ADRs are immutable; a change needs a superseding ADR.` |
| 6 | `  - Drafted for the user's acceptance. Per plan-100 §1 it is "drafted as `proposed`, and the user accepts it before` |
| 7 | `    it is used".` |
| 8 | `  - Until it is accepted, no ruling may cite it as authority.` |
| 9-10 | `  - Revised to incorporate the user's three review decisions of 2026-10-02 (§ User decisions at review). The final text` / `    is still subject to the user's acceptance.` |

So `:5` says accepted and `:8` says no ruling may cite it. Read literally, `:8` would void every ruling that cited ADR-008 after 2026-10-02 (for example the T584 rulings, `completed-tasks.md:389`).

### 1.2 Diagnosis

- Acceptance is independently recorded: `completed-tasks.md:385` (T581 row, artifact column "ADR-008 ... (Accepted)"; text "The user accepted ADR-008."); `release-v8-audit-v1.md:72` (B-08, "accepted"); audit `:228` (C-8) names the contradiction. The verbatim option label "Accept ADR-008 (Recommended)" appears only at `ADR-008:5`; I did not see the underlying AskUserQuestion record, so the label is **(unverified)** beyond that line. The orchestrator should confirm it before the held text is published.
- ADR-008 itself prescribes the header edit that created the defect: `ADR-008:603` ("On acceptance: the user's acceptance is recorded in this header through a normal MR"). Line 5 is that edit. Lines 6-10 are the draft-era bullets that were not removed when it was made. The defect is residue, not a disagreement about the decision.
- Other draft-era sentences remain in ADR-008, all historical rather than contradictory, and none needs fixing: `:12` ("Acceptance is reserved to the user"), `:14` ("T581 is this draft"), `:16` ("Once accepted, it makes the parked items P40 and P43 schedulable"), `:605-606` ("The final text still needs the user's acceptance"). The held text covers them by one reading rule.
- Supersession convention (`AGENTS.md:35`, "Immutable once accepted; superseded decisions link to replacement"; `_template.md:5`, status `superseded by ADR-<MMM>`; `ADR-007:6` and `ADR-008:5`, "a change needs a superseding ADR"). No ADR in `docs/decisions/` has been superseded yet (ADR-001, 002, 004, 005, 006, 007 headers read: all `Accepted`), so there is no worked precedent. `ADR-002:14-24` is the only correction precedent and it explicitly was pre-merge and issued no number, so it does not apply to a merged ADR.
- Partial supersession (a Status block only) has no precedent either. Marking ADR-008 `superseded by ADR-009` would be wrong, because it would suggest the rules P1-P5 are dead. The held text therefore supersedes only the named bullets and leaves ADR-008 `Accepted`.

### 1.3 Held text (recommended option): successor ADR

**File:** `docs/decisions/ADR-009-adr-008-acceptance-record.md`. ADR-009 is the next number if nothing newer exists; I could not list `docs/decisions/` and the orchestrator must confirm no ADR-009 exists at the commit it uses **(unverified)**. ADR-003 has no file (`ADR-008:107`), which is a separate gap.

**Exact text:**

````markdown
# ADR-009 — adr-008-acceptance-record

> Filename: `ADR-009-adr-008-acceptance-record.md` (zero-padded sequential, kebab-case slug).

- **Status**: Proposed. It becomes Accepted when the user approves it. The acceptance is then recorded in this line through a normal MR (`git-workflow.md`).
- **Date**: 2026-10-14
- **Decider(s)**: solution-architect drafted it. Acceptance is reserved to the user.
- **Tasks**: T634 (this draft). T581 (ADR-008 and its acceptance). T623 (release audit finding C-8).
- **Requirements**: `docs/decisions/ADR-008-knowledge-document-authority.md` header lines 5-10 at develop `4c5b43e`; `docs/artifacts/release-v8-audit-v1.md` C-8; `AGENTS.md` § Decision Log; `docs/tasks/completed-tasks.md` T581 row.
- **Extends**: ADR-008, its Status block only.
- **Supersedes**: only the draft-era Status bullets of ADR-008, at lines 6-10 of the file as of develop `4c5b43e`: "Drafted for the user's acceptance ...", "Until it is accepted, no ruling may cite it as authority.", and "Revised to incorporate ... The final text is still subject to the user's acceptance." Nothing else.

## Context

ADR-008's Status block says at line 5, "Accepted. The user approved it on 2026-10-02 ("Accept ADR-008 (Recommended)") ...", and at lines 6-10 that it was "Drafted for the user's acceptance", that "Until it is accepted, no ruling may cite it as authority", and that "The final text is still subject to the user's acceptance". The first is the state after acceptance, and the others are the state before it. ADR-008 § Follow-ups said to record the acceptance in the header through a normal MR. Line 5 is that record, and the draft-era bullets were left beside it. The release audit named the result (`release-v8-audit-v1.md` C-8). An accepted ADR is immutable and a change needs a superseding ADR (`AGENTS.md` § Decision Log; ADR-008 line 5).

## Decision

1. **ADR-008 is Accepted.** The user accepted it on 2026-10-02 (ADR-008 line 5; `completed-tasks.md` T581 row: "The user accepted ADR-008.").
2. **The draft-era bullets at ADR-008 lines 6-10 have no force.** They describe the draft before acceptance and stay in the file as history. Where they differ from line 5, line 5 governs.
3. **Other draft-era sentences are read the same way.** These are ADR-008 § Decider(s) "Acceptance is reserved to the user", § Tasks "T581 is this draft" and "Once accepted, it makes the parked items P40 and P43 schedulable", and § Follow-ups "The final text still needs the user's acceptance". They describe the draft process and are history. They do not make ADR-008 provisional.
4. **Every ruling that cited ADR-008 as authority on or after 2026-10-02 stands.** None is reopened or re-derived by this ADR.
5. **Unchanged.** The text of ADR-008 is not edited by this ADR. ADR-008 stays `Accepted`, dated 2026-10-02, and it still extends ADR-007 and supersedes nothing in it. Its Decision, D1-D5, P1-P5, Order of application, user decisions Q1-Q3, Alternatives, Consequences and Validation are unchanged. No file under `implementation/knowledge/` changes.
6. **Reading rule.** For the status of ADR-008, read its line 5 together with this ADR. A reader who finds lines 6-10 first should treat them as superseded by ADR-009.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| A. Append a status note inside ADR-008 | A reader of ADR-008 sees the correction | Edits an accepted ADR; ADR-008 line 5 says a change needs a superseding ADR; no precedent | Not chosen |
| B. Mark ADR-008 `superseded by ADR-009` | Uses the template's status vocabulary | Reads as if P1-P5 were replaced | Not chosen |
| C. Leave it and note it in the v8.0.0 release document | No new record | The next reader of ADR-008 still finds a contradiction, and `:8` can be quoted against a later ruling | Not chosen |

## Consequences

- **Positive**: one authoritative statement that ADR-008 is accepted; no ruling is exposed to the `:8` sentence; ADR-008 stays byte-for-byte as accepted.
- **Negative**: a number is spent on a clerical correction. ADR-008 read alone still shows the contradictory bullets.
- **Risks introduced**: a reader who never opens ADR-009 still sees the contradiction. *Mitigation:* the audit and the v8.0.0 release document point to ADR-009; the user may additionally approve an append-only pointer in ADR-008 if wanted (not part of this ADR).
- **Follow-ups**: none to knowledge files. T634 is the only task.

## Validation

1. `git diff` of the implementing MR shows only the new ADR-009 file (plus ledger/checkpoint bookkeeping); `ADR-008-knowledge-document-authority.md` is unchanged.
2. ADR-009's quoted lines match ADR-008 at the commit named in Supersedes.
3. No ruling or ledger row changes.
````

### 1.4 The user question (one)

**Question:** "How should the contradictory ADR-008 Status block (accepted at line 5, 'draft, do not cite' at lines 6-10) be corrected?"

| Option | What happens | What stays unchanged | Cost and risk |
|---|---|---|---|
| **1. Successor ADR-009, ADR-008 untouched (Recommended)** | `docs/decisions/ADR-009-adr-008-acceptance-record.md` is added with the § 1.3 text. It supersedes only ADR-008 lines 6-10 | ADR-008 byte-for-byte, its `Accepted` status and every ruling that cited it | Uses one ADR number. ADR-008 read alone still shows the contradiction, which is why Decision 6 exists. Needs your acceptance of ADR-009 |
| **2. Append-only note inside ADR-008** | One bullet is appended under ADR-008 line 10 (text below). No existing character is changed | All other ADR-008 text | Edits a file whose own line 5 says a change needs a superseding ADR, with no precedent. A test or check on accepted-ADR bytes would object **(unverified, I could not search `tests/`)** |
| **3. Leave it; record it only in the v8.0.0 release document** | Nothing in `docs/decisions/` changes | Everything | The contradiction stays quotable against a later ruling (`:8`). It repeats audit C-8 into the release instead of closing it |

**Recommendation: option 1.** It is the one mechanism that `AGENTS.md:35`, `ADR-007:6` and `ADR-008:5` all name, it keeps the accepted file immutable, and it leaves a discoverable numbered record. If you want ADR-008 readers to find it without opening `docs/decisions/`, option 2 is the alternative; I would not combine them.

Option 2 held text, if chosen (append after `ADR-008:10`, two-space-indented under the Status bullet, nothing else edited):

```markdown
  - Status note (2026-10-14, T634): ADR-008 has been Accepted since 2026-10-02 (line 5 above; `docs/tasks/completed-tasks.md`, T581 row). The three bullets above ("Drafted for the user's acceptance", "Until it is accepted, no ruling may cite it as authority", "Revised ... still subject to the user's acceptance") describe the draft before acceptance. They are kept as history and have no force. Nothing else in this ADR changes.
```

---

## 2. Reference table of coexisting severity and grade scales (draft)

### 2.1 Proposed home

**Recommended:** a new, non-authoritative reference page **`docs/wiki/severity-and-grade-scales.md`**, linked from `docs/wiki/home.md` and from the v8.0.0 Migration section M-6 (`release-v8-audit-v1.md:159`). The `docs/wiki/` pages `README.md`, `home.md` and `implementation-guide.md` exist (audit `:207`). Whether other wiki pages are indexed anywhere, and whether the page reaches adopters, are **(unverified)**.

Rules for the home:
- **Descriptive, never ranking.** Every row points to the document that defines its scale, and that document governs (ADR-008 P4: nothing here orders documents). If a row differs from its source, the source wins and the page is the defect.
- **No version marker** (`scripts/check-version-consistency.py` scans wiki pages for `Latest release`/version claims, audit C-1 `:207`); the page needs none. Whether the script flags a new page without one is **(unverified)**.
- Needs a source-line refresh whenever a defining document changes; line numbers below are as of develop `4c5b43e`. The page should cite sections, with lines only as a hint.

Homes considered and not recommended:

| Home | Why not |
|---|---|
| `AGENTS.md` (and `implementation/AGENTS.md`) | It is tier 1 (ADR-008 D1/P1): a table there would become authority over all skills and agents, and it is loaded in every session (token governance). Edits need the rendering workflow. |
| A new file under `implementation/knowledge/instructions/` | `stable` makes it tier 1 (D1). It also needs `sync.mjs`, registry, seven projections and maturity checks. Out of proportion. |
| A new `docs/artifacts/...-vN.md` | Immutable by convention, so a living table needs a new version for every change. Fine for the one-off M-6, wrong for a standing reference. |
| `docs/releases/v8.0.0.md` M-6 only | Time-bound release text; M-6 already exists and states "there is no single reference" (audit `:230`). Keep M-6 and link to the page. |

### 2.2 Draft text for the page: Table 1, the scales

Same word, different object: `critical`, `high`, `medium` and `low` appear on five different scales below. Always name the scale.

| # | Scale | Values | What it grades | Defined at | Notes |
|---|---|---|---|---|---|
| S1 | **Blocker severity** | `critical`, `major`, `minor` | Impact of a **blocker** on tasks and the timeline | Set: `AGENTS.md:48` (§ Blocker Protocol, `:46-49`). Criteria: `implementation/knowledge/skills/blocker-escalation/SKILL.md:50-58`; report field `:38` | Lower case. Not a finding grade. `critical` also shortens the retry rule (`blocker-escalation:139`). The `/team-status` table uses `CRITICAL/MAJOR/MINOR` (audit A-15 `:53`, **unverified** by me) |
| S2 | **Bug severity** | `Critical`, `High`, `Medium`, `Low` | Impact of a **reported bug** | `implementation/knowledge/commands/bug-report.md:20` (report field), `:54` (priority mapping), `:59-63` (blocker flags `[RELEASE_BLOCKER]`, `[TEAM_BLOCKER]`, "escalate severity") | Four levels, no definitions in the command beyond "with justification". The blocker flags are not severities |
| S3 | **Task priority** | `P0`, `P1`, `P2` | **Scheduling** priority of a task (not a severity) | `AGENTS.md:19`; ledger column `AGENTS.md:14` | Target of two mappings (S2 and S4). Listed so the mappings can be read |
| S4 | **PoC debt severity** | `Critical`, `Medium`, `Low` (scorecard); `critical`, `medium`, `low` (debt ledger) | Impact of a **`POC-DEBT` item** | `implementation/knowledge/instructions/poc-guidelines.md:131-135` (inventory column), `:137-141` (summary), `:152` (Scorecard Rule 5); `implementation/knowledge/skills/technical-debt-tracking/SKILL.md:85` (ledger field), `:98-104` (assignment guide), `:147` (capitalisation) | Three tiers since v8 (`high` removed, audit A-08 `:46`). `Critical` = must fix before production; `critical` always has disposition `must_fix_pre_prod` (`technical-debt-tracking:34`, `:106`) |
| S5 | **Security grade** | `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, `SECURITY:LOW` | Severity of a **security finding** | Set and consequences: `implementation/knowledge/instructions/security-guidelines.md:181-184` (§ Security Review Workflow, steps 2-5); `:22-24` (Rails). Definitions: `implementation/knowledge/agents/security-engineer.md:79-84` (§ Findings Classification), also `implementation/knowledge/commands/security-audit.md:42-48` (command's own definitions; the higher grade of the two applies, `:48`) | Written `CRITICAL/HIGH/MEDIUM/LOW` without the prefix in `security-engineer.md:103`, `:172-175` and `security-audit.md:57-61`; same scale. `security-engineer.md:79-84` also carries a time SLA (a due-date overlay, not a scale); it never permits what the workflow blocks (`:86`) |
| S6 | **Code-review level** | `Must Fix`, `Should Fix`, `Nice to Have` (`🔴`, `🟡`, `🔵`) | Required **action on a review finding** | `implementation/knowledge/skills/code-review/SKILL.md:81-90` (format), `:97-102` (Severity Guide); `implementation/knowledge/commands/code-review.md:24`, `:43-45` (counts in the VERDICT) | Defined by action (block merge / request changes / comment), not by impact. `✅ Well Done` is praise, not a level |
| S7 | **Gate finding severity** | `critical`, `high`, `medium`, `low` | Severity of a **finding in a gate verdict** (any gate) | `implementation/knowledge/skills/validation-gates/SKILL.md:47-52` (Findings table), `:76-81` (Severity Definitions), `:64-68` (Verdict Rules) | Lower case. Security findings use S5's grade, mapped 1:1 (`:83`) |
| V1 | **Gate verdict** (an outcome, not a severity) | `PASS`, `CONDITIONAL_PASS`, `FAIL` | The **result of one gate** | `AGENTS.md:52`; `validation-gates/SKILL.md:43`, `:64-68` | Lower-case and capitalised forms (`pass`, `Conditional Pass`) carry the same values: `security-engineer.md:96-98`, `:155-157`, `code-review.md:22`; one verdict per gate (`security-engineer.md:164`) |

### 2.3 Draft text for the page: Table 2, how the scales relate

"Maps" means a rule in a defining document says value X of one scale is value Y of another. Everything else is explicitly **not** a mapping.

| Pair | Relation | Source |
|---|---|---|
| S5 and S7 | **Maps 1:1.** `SECURITY:CRITICAL` is `critical`, `HIGH` is `high`, `MEDIUM` is `medium`, `LOW` is `low`. What each grade requires comes from `validation-gates` § Verdict Rules and S5, and the tier never lowers it | `validation-gates/SKILL.md:83`; grading by the S5 definitions `:85` |
| S5 and S4 | **One-way handling rules, not a value map.** `SECURITY:CRITICAL`/`HIGH`, an Immutable Constraint breach and an omitted/weakened required control are **never** debt. `SECURITY:MEDIUM` is `Critical` debt. `SECURITY:LOW` is tracked as technical debt, with its debt tier assigned by the S4 guide. S4 `Critical` is **not** a `SECURITY:CRITICAL` grade | `poc-guidelines.md:152`; `technical-debt-tracking/SKILL.md:66`; `security-guidelines.md:184` |
| S6 and S7 | **Does not map.** Both apply to the same verdict: "Grade each finding on both scales ... and give the most restrictive verdict either requires." Must Fix means `FAIL`, only Should Fix means `CONDITIONAL_PASS`. A `high` finding without mitigation is `FAIL` even when graded Should Fix | `code-review/SKILL.md:129-131`, `:133`; `validation-gates/SKILL.md:72` |
| S6 and S5 | **Does not map.** A security finding is graded on S5 and, as a review finding, on S6. S6 Must Fix describes "Bug, security issue, data loss risk" (`code-review/SKILL.md:99`); a `SECURITY:MEDIUM` is not automatically Must Fix | `code-review/SKILL.md:40`, `:99`, `:133` |
| S7 and S4 | **Does not map.** S4 has no `high` tier. A `CONDITIONAL_PASS` condition on the PoC track becomes a debt item whose S4 tier is assigned by the S4 guide, not by the finding's S7 value | `validation-gates/SKILL.md:67`, `:140`; `technical-debt-tracking/SKILL.md:98-104`; audit A-08 `:46` |
| S6 and S4 | **Does not map.** Must Fix and Should Fix findings are merged into the debt ledger, and each item is then given an S4 tier by the guide | `technical-debt-tracking/SKILL.md:57`, `:62` |
| S2 and S3 | **Maps, many to one.** `critical` and `high` become `P0`, `medium` becomes `P1`, `low` becomes `P2`. This is the only severity-to-priority rule for bugs | `bug-report.md:54` |
| S4 and S3 | **Maps through the disposition, not directly.** `critical` implies `must_fix_pre_prod`, which is proposed at `P0`; `can_defer_post_ga` is proposed at `P1`; `monitor_only` gets no task | `technical-debt-tracking/SKILL.md:34`, `:106`, `:114-118` |
| S1 and every other scale | **Does not map.** A blocker's severity is about delay, not defect. A bug or finding that blocks work is reported as a blocker on S1 separately | `AGENTS.md:46-49`; `blocker-escalation/SKILL.md:50-58`; `bug-report.md:59-63` |
| S2 and S5 / S7 / S4 | **Does not map.** The words overlap (`High`, `Critical`) but no document equates them. A bug that is a security finding is graded on S5 as well | (absence; no source states a mapping) |
| V1 and the severity scales | The verdict is derived from the findings by each gate's verdict rules (S7 in `validation-gates:64-68`, S6 in `code-review/SKILL.md:129-131`, S5 in `security-guidelines.md:182-184`), most restrictive wins | `validation-gates/SKILL.md:72`; `code-review/SKILL.md:133` |

### 2.4 Open points found (not decided here; for the page's "Known gaps" or a later ruling)

1. **Unnamed scale in blocker lines.** `implementation/knowledge/agents/security-engineer.md:159` and `:184` write `severity=[sev]` for a blocked remediation path. S1 (`critical|major|minor`) and S5 (`CRITICAL..LOW`) both fit, and nothing I read says which. Other agents' blocker lines were not searched **(unverified)**. This is a candidate for a ruling, not for the reference table.
2. **S4 tier for `SECURITY:LOW`** is left to the S4 guide; no document fixes it.
3. **Casing** differs across documents for the same values (S4, S5, V1). No document is wrong; the page should say values are compared case-insensitively only if a source says so (none does, **unverified**).
4. **Out of the table's reach:** PoC outcome (`VALIDATED|INVALIDATED`, `evidence_strength`), lifecycle states, golden-case categories, GitLab `priority::*` labels (parked under O-8, T621; audit `:229`), the time SLA in `security-engineer.md:79-84`.

---

## 3. Acceptance check against the brief

| Criterion | Status |
|---|---|
| Exactly one file with `Based on:`; the exact held text is given | Met: this file; held text in § 1.3 (ADR-009) and § 1.4 (option 2 note) |
| No accepted text is edited | Met: no ADR or knowledge file touched |
| Both clauses quoted with file:line; what stays unchanged stated | Met: § 1.1, § 1.3 Decision 5 |
| ONE user question with options and a recommendation | Met: § 1.4, recommendation option 1 |
| Scale table with name, values, grades, where defined (file:line), mapping or non-mapping, proposed home | Met: § 2.1-2.3 |
| Not run: `python3 -m unittest tests.functional.test_golden_held_out_isolation` (no shell) | The orchestrator must run it before commit. This file names no golden case and no held-out case |
