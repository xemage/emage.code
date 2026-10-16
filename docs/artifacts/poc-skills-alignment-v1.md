# Artifact: poc-skills-alignment-v1.md

> Filename: `poc-skills-alignment-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T570
- **Created**: 2026-10-01
- **Based on**: `docs/tasks/task-T570.md`; `docs/plans/plan-094-poc-skills-alignment.md`;
  `docs/plans/plan-092-poc-contract-amendments.md` §4 (P35); `docs/artifacts/poc-contract-resolution-v1.md`
  (rulings P29a–c and P31, §1.4, §9.2); `docs/artifacts/validate-workflow-gate-resolution-v1.md` (the model, §1.2);
  `docs/decisions/ADR-007-command-contract-authority.md` (used as a procedure only); `AGENTS.md`.
- **Supersedes**: none (first version)
- **Decision references**: ADR-007 (applied by analogy, not amended); the T542 / FU-C precedent as ruled in
  `poc-contract-resolution-v1.md` §9.2. No new ADR is minted.

## 0. What this document is, and what it did not do

This document decides how three `experimental` PoC skills align with T563's rulings and with `AGENTS.md`:
`poc-evaluation`, `rapid-prototyping` and `technical-debt-tracking`. It also specifies the one follow-up task
that implements those decisions. **It changed no skill, command, agent, instruction or golden case.**

**Method and limits.** This session had **no shell**: no `grep`, directory listing, git or test run. Every claim
comes from reading named files directly on branch `agent/solution-architect/T570` (`4ed6d91`). Anything that would
need a search or a run is marked **(unverified)** and collected in §9.2. I did not open `tests/golden/`.

**Files read (source, not projections):**
- `implementation/knowledge/skills/{poc-evaluation,rapid-prototyping,technical-debt-tracking}/SKILL.md`, in full;
- `implementation/knowledge/skills/gitlab-management/SKILL.md`, lines 1–12 (existence only);
- `implementation/knowledge/instructions/poc-guidelines.md`;
- `implementation/knowledge/commands/{evaluate-poc,new-poc,poc-demo}.md`;
- `implementation/knowledge/agents/{poc-orchestrator,technical-debt-narrator,evaluation-agent}.md`;
- `AGENTS.md`; `docs/tasks/active-tasks.md`; `docs/tasks/validate-tasks.py`;
- `docs/artifacts/skillify-output-path-resolution-v1.md` lines 420–459;
- the planning and decision inputs listed above.

**Line numbers in brief §2.** I checked every one against source on `4ed6d91`. All of them point at the text the
brief describes, with three qualifications that §9.1 records: `:118`, the extent of the promotion procedure, and
the extent of the scorecard template.

## 1. Authority basis

### 1.1 ADR-007 does not reach skills

ADR-007 § Decision, branch 1, reads: "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another
clause of the same command file? If yes, the command is wrong regardless of what the corpus does."

Branch 1 governs **command** clauses. `validate-workflow-gate-resolution-v1.md` §1.2 already recorded that a skill
is not ranked: "Branch 1 names a stable *instruction*, not a stable skill." `poc-contract-resolution-v1.md` §1.4
recorded the same gap for agent definitions. **I do not rely on "an instruction outranks a skill" anywhere
below.** ADR-007 is used only as a procedure, as in `poc-contract-resolution-v1.md` §9.1. It is still `proposed`
(header line 5); its formal acceptance is parked as P34.

### 1.2 The basis I rely on: jurisdiction, self-description, and the T542 / FU-C precedent

There are three legs. Each is quoted rather than assumed.

**(i) `poc-guidelines.md` defines its own jurisdiction by subject matter, not by file type.** It is `maturity:
stable` (frontmatter line 4) and `applyTo: "**"` (line 3). Its description (line 2) reads: "Use for
proof-of-concept workstreams where speed and hypothesis validation are primary goals. Enforces mandatory debt
tracking, hypothesis-first validation, and debt scorecards." Its Rails (lines 10–13) say it "applies whenever
`poc-orchestrator` or a PoC specialist agent begins hypothesis-driven exploratory work". Its only stated exclusion
(line 15) is: "Does not apply to production-track work".

**(ii) Each skill places itself inside that jurisdiction in its own words.**

| Skill | Its own words |
|---|---|
| `poc-evaluation` | frontmatter `description`: "Assess proof-of-concept outcomes against explicit hypotheses and success criteria." |
| `rapid-prototyping` | `description`: "Create pragmatic scaffolding and integration patterns for fast proof-of-concept delivery."; § When to use: "Bootstrapping PoC repositories" (`:10`); `:24`: "All PoC code MUST tag known shortcuts" |
| `technical-debt-tracking` | `description`: "Document PoC shortcuts and production remediation plans using a consistent debt ledger."; `:36`: "This skill is responsible for scanning codebases for `POC-DEBT` tags placed by the rapid-prototyping skill." |

**How a skill reaches an agent.** The brief records that no agent or command names these skills. They reach an
agent through `AGENTS.md` § Skill Workflow: "agents MUST check applicable skills in the active platform
projection". A PoC specialist that applies one of these skills is, by the skill's own description, doing PoC
work. By (i), `poc-guidelines.md` governs that work. Where the skill tells the agent to do something the
instruction forbids, the agent cannot satisfy both. That conflict is what the rulings below remove.

**(iii) Precedent: T542, extended to agent files by FU-C.** T542 applied ADR-007 branch 1 by analogy to an agent
file (`orchestrator.md`) that contradicted the `stable`, `applyTo: "**"` instruction `git-workflow.md`
(`active-tasks.md:423–427`). `poc-contract-resolution-v1.md` §9.2 approved FU-C on that basis: "The basis is the
T542 precedent, where ADR-007 branch 1 was applied by analogy to an agent file that contradicted a `stable`
instruction". `poc-guidelines.md` has exactly the shape of `git-workflow.md`: `stable` and `applyTo: "**"`.

**What this precedent does not cover.** Both T542 and FU-C concerned **agent files**. Applying the same analogy
to **skill files** extends the precedent one step further. FU-C needed "explicit orchestrator/user approval"
(`poc-contract-resolution-v1.md` §6). **This extension needs the same approval** before the follow-up is
dispatched (§8, condition 1). I recommend it, on the grounds of legs (i) and (ii).

### 1.3 `AGENTS.md` carries item (d) on its own

`AGENTS.md` § Task Protocol is not scoped to a track, an agent or a file type:

> "Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`"
> "Task briefs: `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria)"
> "Only orchestrators create/transition tasks. Agents report completion and blockers."
> "Sequential IDs: `T001`, `T002`, … Priorities: `P0` (critical path), `P1`, `P2`."

These sentences constrain the file and the act of creating a task, whoever performs it. ADR-007 calls `AGENTS.md`
"this repository's top-level convention document", which "a command may specialise … but may not create a rival
convention for the same thing". I apply that sentence to a skill by the same analogy as §1.2(iii).

**Mechanical corroboration, not authority.** `docs/tasks/validate-tasks.py`, which "ships standalone into target
repos" (`:30–31`), enforces the same contract:
- `PRIORITY_SET = {"P0", "P1", "P2"}` (`:14`), and rejects any other value (`:313–314`);
- an active row must have exactly 7 cells (`:287–293`);
- every ledger ID must have a `task-<ID>.md` brief (C7, `:376–380`).

`parse_table_rows` reads only lines that start with `|` (`:108–110`). A `### T{ID}` block is therefore invisible
to the validator. A task created in the skill's format would exist in no checked form.

### 1.4 Where the basis fails or is weaker, item by item

| Item | Basis | Holds? |
|---|---|---|
| P31 in `poc-evaluation` and `rapid-prototyping` | §1.2: `poc-guidelines.md` Rules 3–4 and `## Result` | **Yes**, subject to the §1.2(iii) approval |
| Case of `rapid-prototyping`'s values | Nothing. Rule 4 is prose ("validates or invalidates"), not a token list | **No authority either way.** Ruled on minimal change (§3) |
| `poc-evaluation`'s new `Evidence strength` field | Not `poc-guidelines.md`, which has no such concept. The basis is the brief's direction (§3: "with `Evidence strength: weak`") plus same-file coherence: the replacement rule at `:103` would otherwise name a field the template lacks | **Weaker**: an additive edit, stated as such |
| (a) and (b) for PoC-phase use of `technical-debt-tracking` | §1.2 | **Yes**, subject to the §1.2(iii) approval |
| (b) when `technical-debt-tracking` runs on **production-track** work | **`poc-guidelines.md` does not reach it** (line 15). Plan-092 P35 raised this ("That skill may also serve the production track"). Two of its triggers may be production-track: "Before any production handoff" and "As part of the QA validation gate" (`:65–66`). | **The instruction does not compel this.** The scale follows anyway, because the skill has **one** Debt Item Format (`:68–87`) for every trigger and cannot carry two scales for one field. I know of no production-track document that defines a competing debt scale **(unverified)** |
| (c), the debt ledger | Nothing contradicts it (§4c) | **No branch fires**, so there is no removal |
| (d), the promotion procedure | §1.3, `AGENTS.md`, which is track-neutral | **Yes.** This is the strongest of the four, and it holds even on the production track |
| The disposition axis (`must_fix_pre_prod` etc.) | Only the coupling to `critical` is compelled (§4b) | **Partial.** The axis itself stays |

## 2. `poc-evaluation`: apply P31

**How to apply these edits.** The implementer matches each edit by its exact **before** text. Every before text
below is unique in its file. Line numbers refer to source at `4ed6d91`, before any edit.

### E1: `:19–21`, the verdict list

````
Before:
- Validated
- Invalidated
- Inconclusive

After:
- Validated
- Invalidated
````

**Authority:** `poc-guidelines.md:56`, Rule 4: "**Binary outcome** — A PoC either validates or invalidates the
hypothesis." `/evaluate-poc:16` already reads "Verdict (Validated, Invalidated)".

### E2: `:37`, the `[VERDICT]` marker

````
Before:
[VERDICT] gate=poc-evaluation | result=VALIDATED|INVALIDATED|INCONCLUSIVE | poc_ref=poc-{name}-v{N} | hypothesis="{short hypothesis}" | production_recommendation=proceed|proceed_with_constraints|do_not_proceed | debt_count={N} | date={YYYY-MM-DD}

After:
[VERDICT] gate=poc-evaluation | result=VALIDATED|INVALIDATED | evidence_strength=strong|moderate|weak | poc_ref=poc-{name}-v{N} | hypothesis="{short hypothesis}" | production_recommendation=proceed|proceed_with_constraints|do_not_proceed | debt_count={N} | date={YYYY-MM-DD}
````

**Authority:** Rule 4, as for E1. The `evidence_strength` field is **additive** (§1.4). It carries the
distinction that `poc-contract-resolution-v1.md` §5 calls the semantic cost of a binary outcome: "`INVALIDATED`
will now cover both 'disproven' and 'not proven in time'. The `Evidence strength` field is what tells them
apart." Its values copy `/evaluate-poc:33` exactly.

### E3: `:63–66`, template § 4. Verdict

````
Before:
## 4. Verdict
**{VALIDATED | INVALIDATED | INCONCLUSIVE}**

Rationale: [Why this verdict]

After:
## 4. Verdict
**{VALIDATED | INVALIDATED}**

Evidence strength: {strong | moderate | weak}

Rationale: [Why this verdict]

Recommended next step: [The next step; for an `INVALIDATED` verdict with weak evidence, name a follow-up PoC with refined criteria]
````

**Authority:** Rule 4, as for E1. The two added lines are needed by E4, which requires `Evidence strength: weak`
and a named follow-up PoC. The template has no other section that could hold either. The "Recommended next step"
line implements the skill's own Framework step 4, "Recommend next step" (`:13`), which the template omitted. That
is a same-file basis.

### E4: `:103`, the ">50% untested" rule

````
Before:
- A PoC with >50% untested criteria should receive an `INCONCLUSIVE` verdict, not `VALIDATED`.

After:
- The verdict is `VALIDATED` only if every success criterion defined in the PoC artifact was tested and met by the PoC's deadline. Post-hoc criteria cannot stand in for an untested one.
- If any such criterion was tested and not met, the verdict is `INVALIDATED`, with the evidence strength the tests support.
- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).
````

**Authority:**
- `poc-guidelines.md:55`, Rule 3: "If the hypothesis isn't validated by the deadline, it fails".
- `:56`, Rule 4: "'Partially validated' requires a follow-up PoC with refined criteria".
- The model is `/evaluate-poc:65`: "If evidence strength is weak, or the hypothesis wasn't actually tested by its
  deadline, returns `INVALIDATED` with `Evidence strength: weak` and names a follow-up PoC with refined criteria as
  the recommended next step, rather than forcing a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First
  Validation, Rules 3–4)."

**Why there is no 50% threshold.** A one-for-one swap ("> 50% untested → `INVALIDATED`") would leave a window of
1–50% untested criteria where the skill would still permit `VALIDATED`. A PoC with untested criteria is at best
"partially validated", and Rule 4 sends that to a follow-up PoC, not to `VALIDATED`. The old line did not say
that ≤ 50% may be `VALIDATED`. Re-stating a threshold in a binary rule would imply exactly that.

**Recorded alternative:** keep the threshold ("> 50% … `INVALIDATED` with `Evidence strength: weak`"). **Not
taken**, because it re-opens the window that Rule 4 closes.

**Untouched:** `:101` ("mark as 'Not Tested' with reason") and `:102` (post-hoc flag) are unchanged. E4 relies on
both.

### E5: `:92–93`, template § 8. Linkage (consequential on §4a; not in brief §2)

````
Before:
## 8. Technical Debt Scorecard Linkage
[Reference to technical-debt-tracking scorecard items created from this evaluation]

After:
## 8. Technical Debt Scorecard Linkage
[Reference, by inventory `#`, to the related items in `POC-DEBT-SCORECARD.md` in the PoC root (`poc-guidelines.md` § Debt Scorecard), and, by `DEBT-{ID}`, to any debt-ledger items the technical-debt-tracking skill created from this evaluation]
````

**Authority:** §4a. Once the "technical-debt-tracking scorecard" is ruled to be `POC-DEBT-SCORECARD.md`, this
pointer must name it. Following `poc-contract-resolution-v1.md` §3a, the edit quotes "in the PoC root" and does
not define it.

**Unchanged in `poc-evaluation`:**
- `:26` "Linkage to Technical Debt Scorecard items": after §4a, the name designates the right artifact.
- `:113` and `:123–126` (§7, F3 and F4).

## 3. `rapid-prototyping`: apply P31; does case matter?

### E6: `:102`, the checkpoint marker

````
Before:
[CHECKPOINT] id=poc-{name}-validation | hypothesis="{hypothesis text}" | evidence=[{evidence items}] | debt_tags={count} | verdict=validated|invalidated|inconclusive | artifact_refs=[poc-{name}-v{N}] | next=[{next steps}]

After:
[CHECKPOINT] id=poc-{name}-validation | hypothesis="{hypothesis text}" | evidence=[{evidence items}] | debt_tags={count} | verdict=validated|invalidated|in_progress | artifact_refs=[poc-{name}-v{N}] | next=[{next steps}]
````

### E7: new paragraph, inserted immediately after the closing fence on `:103` and before `**Evidence items**` on `:105`, separated by one blank line on each side

````
After (inserted text):
**Verdict values:** `in_progress` is allowed only at a milestone checkpoint, before any of the checkpoint triggers below has fired. At a trigger, the verdict is binary: `validated` or `invalidated` (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). A hypothesis not validated when the time-box expires is `invalidated` (Rule 3). A partial result is `invalidated`, and `next=` names a follow-up PoC with refined criteria.
````

**Authority for E6 and E7:**
- `poc-guidelines.md:55–56`, Rules 3–4.
- The precedent `poc-contract-resolution-v1.md` §5: `/poc-demo` "keeps `IN_PROGRESS`", because "'not yet decided'
  is a legitimate state that Rule 4 does not touch".

**Why `in_progress` replaces `inconclusive` instead of just deleting it.** The skill publishes this marker "At the
conclusion of prototyping (or at significant milestones)" (`:99`). At a milestone the PoC has not concluded. Plain
deletion would force a binary claim mid-PoC, a premature call that no rule requires. E7 confines `in_progress` to
milestones, so no terminal checkpoint can carry a third outcome. The spelling is `in_progress` (underscore), which
matches `AGENTS.md` § Lifecycle States and `/poc-demo:37`'s `IN_PROGRESS`. It does **not** follow the same file's
`in-progress` at `:71`, which is an artifact status, not a verdict.

**Does case matter? No.**
- No quoted authority makes case normative. Rule 4 is prose. `## Result` (`poc-guidelines.md:112`) shows
  `VALIDATED / INVALIDATED` as template text, not as a token grammar that a checkpoint marker must follow.
- What conflicts with Rule 4 is the **value set** (a third terminal outcome), not the case.
- The marker is a `[CHECKPOINT]`, not a `[VERDICT]`. It already uses lowercase values throughout.
- **Decision:** keep lowercase, and change the value set only.
- **Recorded alternative:** uppercase, to match `poc-evaluation`'s `[VERDICT]` marker and the scorecard's `##
  Result`. Not taken. It would be an edit with no authority behind it. If one token case across the PoC track is
  wanted, that is a separate editorial decision. The same reasoning keeps `technical-debt-tracking`'s lowercase
  severities (§4b).

**Unchanged:** `:113` ("The PoC time-box expires (document whatever evidence exists)"); E7 states the consequence.
`:53` (the consumer reference to technical-debt-tracking) stays as it is.

## 4. `technical-debt-tracking`: decisions (a)–(d)

### 4a. Scorecard identity: **the same artifact as `POC-DEBT-SCORECARD.md`**

| Field | Value |
|---|---|
| **Clauses** | Skill `:26`: "Produce a Technical Debt Scorecard summary by severity band." `:136–174`: a "Technical Debt Scorecard v{N}" template, ending "The scorecard is included as part of the PoC evaluation output and referenced in production handoff checkpoints." Against them, `poc-guidelines.md:100`: "Before a PoC can be marked as complete, a **debt scorecard** must be produced. This is a summary document that inventories all shortcuts taken." `:103`: "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure". |
| **Decision** | **Same artifact.** The skill's "Technical Debt Scorecard" **is** `POC-DEBT-SCORECARD.md` in the PoC root, in `poc-guidelines.md`'s five-section structure, unchanged and in order. The skill's own aggregates stay as **additional sections appended after `## Recommendation`**. The `v{N}` versioning of the scorecard is dropped: there is one file. |
| **Why it is the same artifact, and why `TECHNICAL-DEBT.md` was different** | T563 §3c ruled `TECHNICAL-DEBT.md` distinct because "every document that names `TECHNICAL-DEBT.md` names it **next to** the scorecard, never **as** it". The test here gives the opposite answer on all three counts. **Name:** the PoC track's `stable` commands use "Technical Debt Scorecard" to mean `POC-DEBT-SCORECARD.md`: `/new-poc:36–37` ("Maintain a Technical Debt Scorecard … Write to `POC-DEBT-SCORECARD.md` in the PoC root") and `/poc-demo:27` ("Reference the Technical Debt Scorecard (`POC-DEBT-SCORECARD.md` in the PoC root …)"). **Input:** both inventory `POC-DEBT` tags (skill `:36`; `poc-guidelines.md:133`, Rule 1). **Role:** both are the evaluation-time debt summary (skill `:174`; `poc-guidelines.md:100`). No document names the skill's scorecard next to `POC-DEBT-SCORECARD.md` as a separate deliverable. |
| **Branch** | Branch 1 by analogy, stable-instruction prong (§1.2), as in P29a. |
| **Authority relied on** | `poc-guidelines.md:103` and Rule 4 (`:136`): "No PoC task may be marked complete without a finalized scorecard". The commands are corroboration of the track's naming, **not** rank (§1.1). |
| **Extra sections are a specialisation, not a rival** | Precedent: `poc-contract-resolution-v1.md` §3b kept `/evaluate-poc`'s extra columns, because "They add attributes without competing with any". The appended sections (severity by disposition, by category, remediation sequence, risk register) add views and do not restate any of the instruction's five sections under another form. |
| **Rejected alternatives** | (1) **Rule it distinct and rename it** (for example, "debt ledger summary"). It shares the name, input and role, so a rename would only relabel a rival to avoid the conflict. It would also add a fourth debt document next to the scorecard, `TECHNICAL-DEBT.md` and the ledger. (2) **Delete the skill's scorecard.** This would lose the disposition, category and sequencing content, which is a legitimate specialisation. |
| **What changes** | E8 (`:25–28`), E9 (`:59–61`), E14 (`:136–174`); `poc-evaluation` E5. |

### 4b. Scales

| Field | Value |
|---|---|
| **Clauses** | Severity: `critical \| high \| medium \| low` (`:76`), guide `:91–96`, summary rows `:150–153`, "Critical/High" `:157`. Effort: `XS (< 1h) \| S (1-4h) \| M (4-16h) \| L (16-40h) \| XL (40h+)` (`:78`). Points: `XS=1, S=2, M=5, L=8, XL=13` (`:119`). Against them, `poc-guidelines.md:123–126`: "Critical (must fix before production) / Medium (should fix before production) / Low (nice to have)"; `:134`, Rule 2: "Each item must have an estimated production effort: `S` (small), `M` (medium), `L` (large)". |
| **Decision: severity** | Three tiers, `critical \| medium \| low` (lowercase kept, §3), carrying the instruction's meanings one-to-one. `high`'s criteria are redistributed by production consequence. Blocking items go to `critical`: "missing error handling on critical paths" and "architectural violation that blocks scaling". Degrading items go to `medium`: "performance degradation under load". This mirrors `/evaluate-poc:59`'s Production Impact scale "blocks/degrades/cosmetic", which is corroboration, not authority. **Coupling, compelled:** a `critical` item always takes disposition `must_fix_pre_prod`. The instruction defines Critical as "must fix before production", so `critical` + `can_defer_post_ga` or `critical` + `monitor_only` would contradict it. The converse is not compelled: a `medium` or `low` item may still be `must_fix_pre_prod`, because the team may choose to fix a "should fix". |
| **Decision: effort** | `S \| M \| L`, using the instruction's labels and keeping the skill's hour calibration as **indicative** bands nested inside them: S < 4h (old XS+S), M 4–16h, L 16h+ (old L+XL). Nesting inside the parent tiers is what `poc-contract-resolution-v1.md` §3b calls a specialisation. The bands are guidance, not a definition. A **recorded alternative** is to drop the hours, following §3a's "quote, don't define" for "PoC root". Not taken: effort bands are calibration of a closed label set, not the meaning of a location the instruction leaves undefined. |
| **Decision: points mapping** | **Removed.** Its only consumer is the `**Points:**` field of the task block, which (d) removes. Neither an `AGENTS.md` ledger row nor a brief ("objective, inputs, outputs, acceptance criteria") has a points field. The promotion proposal carries `Effort` instead. |
| **Branch** | Branch 1 by analogy, stable-instruction prong (§1.2), as in P29b. For production-track use, see §1.4: the single Debt Item Format carries the scale there. |
| **Authority relied on** | `poc-guidelines.md:123–126, :134`. Rule 2 is a closed set, and the ledger items are the same items the scorecard inventories (Rule 1), so an `XS`/`XL` or `high` item has no legal value in the scorecard. P29b's reasoning applies unchanged: "`HIGH` does not" nest inside the parent tiers. |
| **What changes** | E8 (coupling sentence), E10 (`:76`), E11 (`:78`), E12 (`:89–96`), E13 (`:119`, removed with the task block), E14 (summary rows). |

### 4c. The debt ledger at `docs/artifacts/debt-ledger-v{N}.md`: **kept, distinct, path unchanged**

| Field | Value |
|---|---|
| **Clauses** | `:59–61` ("Produce consolidated debt ledger … as a versioned artifact"); `:128–134` (the path, and "Each version is immutable"). |
| **Decision** | **Keep it as a distinct working register that feeds the scorecard.** State explicitly that it does not substitute for the scorecard. Its items use §4b's scales automatically, through the Debt Item Format. Fix one same-file contradiction in the promotion step that touches it (E13, step 5). |
| **Branch** | **None fires.** No quoted text contradicts it, so there is no basis to remove it. This mirrors T563 §3c. |
| **Why it is not a rival** | The ledger is a per-item register: `DEBT-{ID}` blocks with 13 fields, including sources beyond `POC-DEBT` tags (code review, security scan, evaluation). The scorecard is "a summary document" (`poc-guidelines.md:100`) and the completion gate. They do not carry the same thing in two forms. Separately, the ledger supplies the **per-item severity** that the scorecard's `## Summary` counts but its Debt Inventory has no column for. That gap is the parked P33 item, and it is not decided here. |
| **Conformance** | The name `debt-ledger-v{N}.md` follows `AGENTS.md` § Artifact Versioning ("`<type>-v<N>.md`"). Immutability is already declared at `:134`. |
| **Same-file defect fixed in (d)** | Promotion step 4 (`:126`): "Update the debt ledger to mark promoted items with `promoted_to=T{ID}`". This contradicts `:134`: "Each version is immutable. Create a new version when items are added, resolved, or promoted." The edit records the mark in the **next** version. |
| **Not decided** | How the ledger relates to `TECHNICAL-DEBT.md`, the narrator's register (`technical-debt-narrator.md:14`). No text links the two, so I do not identify them (§7, F5). |
| **What changes** | E9 (relationship sentence); E13 step 5. `:128–134` itself is unchanged. |

### 4d. The promotion procedure against `AGENTS.md` § Task Protocol

| Field | Value |
|---|---|
| **Clauses** | `:100`: "debt items must be promoted from the debt ledger to the production task backlog". `:106`: priority `P0`. `:107`: priority `should`. `:113–124`: a `### T{ID}` block with **Assignee**, **Priority** `{must \| should}`, **Points** and **Sprint**. `:125`: GitLab sync. `:126`: in-place ledger update. |
| **Defects** | (1) `should` (`:107`) and `must` / `should` (`:118`) are not `AGENTS.md` priorities. `:118` also contradicts the skill's own `:106` (`P0`). (2) The block format is not the 7-column ledger row, and there is no `task-<ID>.md` brief. (3) The procedure has whoever applies the skill create tasks, against "Only orchestrators create/transition tasks". (4) Step 4 contradicts `:134` (§4c). |
| **Decision: priorities** | `must_fix_pre_prod` → `P0` (unchanged; `:106` is already legal). `can_defer_post_ga` → **`P1`**. This is an ordinal relabel of the skill's own two-level `must` / `should` (`:118`) onto `AGENTS.md`'s scale, anchored at the skill's own `must` = `P0` (`:106`). It is not a new judgment. The ledger legend at `active-tasks.md:460`, "`P1` (important) · `P2` (nice-to-have)", fits MoSCoW `should` (important, not vital). That is corroboration only, since the legend is not `AGENTS.md`. **Recorded alternative:** `P2`, reasoning that post-GA deferral is the lowest urgency. Not taken, because it would collapse the skill's ordinal instead of carrying it over. Either way, the orchestrator may change the proposed value. |
| **Decision: who creates, and in what format** | The skill **proposes**; the orchestrator **creates**. A proposal carries everything the orchestrator needs for a row and a brief. The orchestrator assigns the sequential ID, writes the 7-column row and writes `task-<ID>.md`. `Assignee` becomes **Proposed owner**, which the orchestrator maps to an agent name (`active-tasks.md:461`: "Owners are agent names from `knowledge/agents/`"). `Points` becomes `Effort`. `Sprint` becomes brief context, since the ledger has no sprint column. `Status` and `Created` are dropped, because the orchestrator sets them. |
| **Decision: GitLab sync** | Kept, moved after creation, and worded "created" instead of "promoted". `AGENTS.md` does not say who syncs issues, so I assign no actor. |
| **Branch** | Branch 1 by analogy, `AGENTS.md` prong (§1.3), plus a same-file prong for `:118` vs `:106` and step 4 vs `:134`. |
| **Authority relied on** | `AGENTS.md` § Task Protocol, the four sentences quoted in §1.3. Mechanical corroboration: `validate-tasks.py:14`, `:287–293`, `:313–314`, C7. This leg does not depend on `poc-guidelines.md`'s jurisdiction, so it holds on the production track too. |
| **What changes** | E13 (`:98–126`, replaced as one block). |

### Exact wording for `technical-debt-tracking`

#### E8: `:25–28`, § Scorecard Requirements

````
Before:
## Scorecard Requirements
- Produce a Technical Debt Scorecard summary by severity band.
- Mark each item as: `must_fix_pre_prod`, `can_defer_post_ga`, or `monitor_only`.
- Include top remediation sequence for the first production sprint.

After:
## Scorecard Requirements
- The Technical Debt Scorecard is `POC-DEBT-SCORECARD.md` in the PoC root, in the structure `poc-guidelines.md` § Debt Scorecard defines. This skill adds sections to it; it does not define a second scorecard.
- Mark each item as: `must_fix_pre_prod`, `can_defer_post_ga`, or `monitor_only`. A `critical` item is always `must_fix_pre_prod`.
- Include top remediation sequence for the first production sprint.
````

#### E9: `:59–61`, Step 4

````
Before:
**Step 4: Produce consolidated debt ledger**

Output the full debt ledger as a versioned artifact (see below).

After:
**Step 4: Produce consolidated debt ledger, then the scorecard**

Output the full debt ledger as a versioned artifact (see below). Then write `POC-DEBT-SCORECARD.md` from it (see Technical Debt Scorecard below). Every `POC-DEBT` tag found in Step 1 must appear in the scorecard's Debt Inventory (`poc-guidelines.md` Scorecard Rule 1). The ledger is this skill's working register and does not substitute for the scorecard.
````

#### E10: `:76`

````
Before:
- **Severity:** critical | high | medium | low

After:
- **Severity:** critical | medium | low
````

#### E11: `:78`

````
Before:
- **Effort:** XS (< 1h) | S (1-4h) | M (4-16h) | L (16-40h) | XL (40h+)

After:
- **Effort:** S (small, indicatively < 4h) | M (medium, indicatively 4-16h) | L (large, indicatively 16h+)
````

#### E12: `:89–96`, the severity assignment guide

````
Before:
**Severity assignment guide:**

| Severity | Criteria |
|----------|----------|
| **critical** | Security vulnerability, data loss risk, or compliance violation |
| **high** | Performance degradation under load, missing error handling on critical paths, architectural violation that blocks scaling |
| **medium** | Missing tests for important paths, hardcoded configuration, suboptimal patterns |
| **low** | Code style issues, minor optimization opportunities, documentation gaps |

After:
**Severity assignment guide** (tiers and meanings from `poc-guidelines.md` § Debt Scorecard):

| Severity | Meaning | Criteria |
|----------|---------|----------|
| **critical** | Must fix before production | Security vulnerability, data loss risk, compliance violation, missing error handling on critical paths, architectural violation that blocks scaling |
| **medium** | Should fix before production | Performance degradation under load, missing tests for important paths, hardcoded configuration, suboptimal patterns |
| **low** | Nice to have | Code style issues, minor optimization opportunities, documentation gaps |

A `critical` item always takes disposition `must_fix_pre_prod`: `poc-guidelines.md` defines Critical as "must fix before production", so it cannot be deferred or only monitored.
````

#### E13: `:98–126`, the promotion procedure (replace the whole block)

````
Before:
### Promotion Procedure for Debt Items to Production Backlog

When a PoC transitions to production implementation, debt items must be promoted from the debt ledger to the production task backlog:

**Promotion rules:**

| Disposition | Promotion Action |
|-------------|-----------------|
| `must_fix_pre_prod` | Create task in `docs/tasks/active-tasks.md` with priority `P0` and target sprint = current or next |
| `can_defer_post_ga` | Create task in `docs/tasks/active-tasks.md` with priority `should` and target sprint = post-GA sprint |
| `monitor_only` | Do not create a task; add to risk register with monitoring criteria |

**Promotion procedure:**

1. Filter the debt ledger for items with disposition `must_fix_pre_prod` and `can_defer_post_ga`.
2. For each item, create a task entry:
   ```markdown
   ### T{ID}: Resolve DEBT-{debt-id} — {title}
   - **Status:** pending
   - **Assignee:** {recommended owner from debt item}
   - **Priority:** {must | should — based on disposition}
   - **Points:** {mapped from effort: XS=1, S=2, M=5, L=8, XL=13}
   - **Sprint:** {target sprint from debt item}
   - **Depends on:** [any prerequisites]
   - **Artifact refs:** [debt-ledger-v{N}, poc-{name}-v{N}]
   - **Created:** {YYYY-MM-DD}
   ```
3. Sync promoted tasks to GitLab issues (see gitlab-management skill).
4. Update the debt ledger to mark promoted items with `promoted_to=T{ID}`.

After:
### Promotion Procedure for Debt Items to Production Backlog

When a PoC transitions to production implementation, debt items must be proposed for promotion from the debt ledger to the production task backlog. Per `AGENTS.md` § Task Protocol, "Only orchestrators create/transition tasks": this skill prepares the proposals, and the orchestrator decides on them and creates the tasks.

**Promotion rules:**

| Disposition | Promotion Action |
|-------------|-----------------|
| `must_fix_pre_prod` | Propose a task with priority `P0` and target sprint = current or next |
| `can_defer_post_ga` | Propose a task with priority `P1` and target sprint = post-GA sprint |
| `monitor_only` | Do not propose a task; add to risk register with monitoring criteria |

**Promotion procedure:**

1. Filter the debt ledger for items with disposition `must_fix_pre_prod` and `can_defer_post_ga`.
2. For each item, write a promotion proposal, and report the proposals to the orchestrator:
   ```markdown
   #### Proposal: Resolve DEBT-{debt-id} — {title}
   - **Proposed priority:** {P0 | P1 — per the promotion rules above}
   - **Proposed owner:** {recommended owner from debt item}
   - **Effort:** {S | M | L — from debt item}
   - **Target sprint:** {target sprint from debt item}
   - **Depends on:** [any prerequisites]
   - **Artifact refs:** [debt-ledger-v{N}, poc-{name}-v{N}]
   ```
3. The orchestrator creates each accepted proposal as a task, per `AGENTS.md` § Task Protocol: a row in `docs/tasks/active-tasks.md` with the columns `ID | Title | Owner | Status | Priority | Depends on | Last update`, and a brief at `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria). The orchestrator assigns the sequential ID and may change the proposed priority or owner.
4. Sync created tasks to GitLab issues (see gitlab-management skill).
5. Record `promoted_to=T{ID}` for each created task in the next debt-ledger version (versions are immutable; see below).
````

**Notes for the implementer:** the inner fence stays three backticks, as in the source. The `—` in the headings and
in the proposal fields is U+2014, as in the source. Nothing else in `:98–126` survives. `:127` (blank) and
`:128–134` (Debt ledger versioning) are unchanged.

#### E14: `:136–174`, the scorecard section (replace the whole block, from the `### Technical Debt Scorecard (Enhanced)` heading through the final sentence on `:174`)

````
Before:
(lines 136–174 verbatim, from "### Technical Debt Scorecard (Enhanced)" through "The scorecard is included as part of the PoC evaluation output and referenced in production handoff checkpoints.")

After:
### Technical Debt Scorecard (Enhanced)

The Technical Debt Scorecard is `POC-DEBT-SCORECARD.md` in the PoC root. Write it in the structure `poc-guidelines.md` § Debt Scorecard › Scorecard Format defines — `## Hypothesis`, `## Result`, `## Debt Inventory`, `## Summary`, `## Recommendation` — unchanged and in that order. Count the `## Summary` tiers from the debt ledger's per-item severity. Then append the following sections after `## Recommendation`:

```markdown
## Scorecard Source
- Date: {YYYY-MM-DD}
- Debt ledger: debt-ledger-v{N}

## Severity by Disposition

| Severity | Total | must_fix_pre_prod | can_defer_post_ga | monitor_only |
|----------|-------|-------------------|-------------------|--------------|
| Critical | {N} | {N} | 0 | 0 |
| Medium | {N} | {N} | {N} | {N} |
| Low | {N} | {N} | {N} | {N} |

## Summary by Category

| Category | Total | Critical | Estimated Total Effort |
|----------|-------|----------|----------------------|
| Security | {N} | {N} | {effort} |
| Architecture | {N} | {N} | {effort} |
| Testing | {N} | {N} | {effort} |
| Data quality | {N} | {N} | {effort} |
| Operations | {N} | {N} | {effort} |

## Top Remediation Sequence (First Production Sprint)
1. DEBT-{ID}: {title} — {effort} — {owner}
2. DEBT-{ID}: {title} — {effort} — {owner}
3. DEBT-{ID}: {title} — {effort} — {owner}

## Risk Acceptance Register
[Items with disposition=monitor_only and their monitoring criteria]
```

The scorecard is included as part of the PoC evaluation output and referenced in production handoff checkpoints. The Tech Lead reviews it before the PoC is closed, and no PoC task may be marked complete without it (`poc-guidelines.md` Scorecard Rules 3–4).
````

**Notes for the implementer:**
- The `Critical` row's `0 | 0` cells are literal zeros. They encode the §4b coupling.
- The section deliberately does **not** copy the instruction's template. It names it, so the two cannot drift
  apart, following the pattern of `/new-poc:37` and `/poc-demo:27`.
- `## Severity by Disposition` replaces the old `## Summary by Severity`. That avoids a second section titled
  "Summary" next to the instruction's `## Summary`.

**Unchanged in `technical-debt-tracking`:**
- `:1–23`, the frontmatter, Categories and Required fields;
- `:34–58`, including the grep command and Steps 1–3;
- `:63–87`, except `:76` and `:78`;
- `:128–134`.

The frontmatter `description` does not change, so the registry's descriptive fields do not change either. Only
its checksums move.

## 5. Blast radius

**Nothing outside the three skills needs a content change.** Here is the check against each neighbour:

| Neighbour | Status after these rulings |
|---|---|
| `poc-guidelines.md` | Unchanged. Nothing here amends an instruction. P33 stays parked. |
| `AGENTS.md` | Unchanged. |
| `/evaluate-poc`, `/new-poc`, `/poc-demo` | Already aligned by T564. `/evaluate-poc:20` ("Technical Debt Scorecard summary (severity, effort, risk, owner)") and `/poc-demo:19` read correctly under §4a. |
| `poc-orchestrator`, `evaluation-agent`, `technical-debt-narrator` | Already aligned, or state no scales. `poc-orchestrator.md:39` and `technical-debt-narrator.md:17` say "Technical Debt Scorecard" and now resolve to the one artifact. |
| `tests/golden/**` | Not opened. Brief §2 says no case quotes the skills, and the only hit is a frozen registry copy that is not compared to the live registry. **No protected path is involved.** |
| Generated outputs (mechanical, not content) | (1) The `implementation/.<platform>/skills/<name>/SKILL.md` mirrors: regenerate with `node implementation/scripts/sync.mjs --root implementation`. (2) `implementation/registry/index.json` checksums: regenerate with `python3 implementation/scripts/generate-registry.py`. Confirm both with `--check`. (3) The repo-root projections of the three skills will drift. Declare them in `tests/_baselines/root-install-drift.json`, as T564 and T567 did; the exact path count is **(unverified)**, probably 3 × 6 or 3 × 7. Do not hand-edit the root folders (`AGENTS.md` § Knowledge Base). |
| Maturity | None. All three skills are `experimental` (plan-094 §1). |

## 6. Follow-up task

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / notes |
|---|---|---|---|---|---|---|
| **FU-1**: align the three PoC skills | E1–E14 | `implementation/knowledge/skills/poc-evaluation/SKILL.md` (E1–E5); `…/rapid-prototyping/SKILL.md` (E6–E7); `…/technical-debt-tracking/SKILL.md` (E8–E14); the regenerated `implementation/.<platform>/` mirrors; `implementation/registry/index.json` via the generator; root-drift declarations in `tests/_baselines/root-install-drift.json` | **No** | Backend Developer (the same owner class as T564) | P2 (plan-094 §2) | **Dispatch only after the §1.2(iii) approval.** Apply each edit by its exact before text. Verify: (1) `sync.mjs --check` and `generate-registry.py --check` are clean; (2) the case-insensitive string `inconclusive` no longer occurs in any of the three source files; (3) neither `XS` nor `XL` as an effort value, nor `high` as a severity value, nor the priorities `should` or `must`, remain in `technical-debt-tracking`; (4) `python3 docs/tasks/validate-tasks.py` still passes (it should be unaffected). |

No other task is needed. There is **no** golden follow-up and **no** baseline or evaluator-hash change.

## 7. Findings outside scope (not decided; candidates for parking)

- **F1: two verdict formats for one PoC evaluation.** `poc-evaluation:37`'s `[VERDICT] gate=poc-evaluation | …`
  and `/evaluate-poc:27–38`'s `## POC VERDICT` block carry overlapping fields in different shapes. This is the
  same rival-format shape as P37/F1 (`validate-workflow-gate-resolution-v1.md` §6), between a skill and a command.
  ADR-007 does not rank them.
- **F2: two Production Handoff Checklists.** `poc-evaluation:105–134` and `/evaluate-poc:40–51` list different
  items under the same heading.
- **F3: `poc-evaluation:113`**, "All POC-DEBT tags cataloged and promoted to technical debt backlog". "All …
  promoted" conflicts with `technical-debt-tracking`'s `monitor_only` ("Do not create a task"). This is a
  skill-to-skill inconsistency with no higher authority behind it, so I left it unruled.
- **F4: `poc-evaluation:123–126`** (§ Task Creation in the checklist). The passive "created as tasks" does not
  contradict "Only orchestrators create/transition tasks", but "Debt remediation tasks created with severity and
  target sprint" names fields that an `AGENTS.md` row lacks. A natural cleanup is to point it at E13's
  proposal → orchestrator flow. That is not compelled.
- **F5: three debt registers.** `TECHNICAL-DEBT.md` (narrator), `debt-ledger-v{N}.md` (this skill) and the
  scorecard's Debt Inventory. No text relates the first two. This belongs with the parked P33 Legacy-section
  question.
- **F6: `rapid-prototyping`'s `[CHECKPOINT]` marker against `AGENTS.md` § Checkpoint Protocol.** That protocol says
  checkpoints are "Written at every phase boundary by the orchestrator" and include "completed tasks, key decisions,
  blockers, token metrics, next steps". The skill has a prototyping agent "publish" a checkpoint marker without
  those fields. This is possibly P30's shape. It is unruled, because brief §2 cites only the marker's `verdict=`
  values.
- **F7: no `## Rails` section in any of the three skills.** `maturity-promotion-criteria-v2.md` §2.1 reportedly
  mandates `## Rails` (`active-tasks.md:252`). Whether that applies to skills is **(unverified)**. It would matter
  only at promotion.
- **F8: `rapid-prototyping:54`** uses code-review severity ("🟡 Should Fix") for untagged shortcuts. That is a
  different scale for a different thing, review findings, so it is not P29b. Noted only.

## 8. Summary

| Item | Decision | Basis (quoted in §§1–4) |
|---|---|---|
| Authority | `poc-guidelines.md`'s own jurisdiction (description, `applyTo: "**"`, Rails) plus each skill's PoC self-description, by the T542 / FU-C analogy **extended to skills**. `AGENTS.md` § Task Protocol on its own for (d). | §1.2–1.3; it fails for production-track use of (b) (§1.4) |
| `poc-evaluation` | Drop `INCONCLUSIVE` (E1–E3); a binary `:103` rule with no threshold (E4); add `Evidence strength` and `Recommended next step` (E2–E3, additive); linkage points at `POC-DEBT-SCORECARD.md` (E5) | Rules 3–4; `/evaluate-poc:65` as the model |
| `rapid-prototyping` | `inconclusive` → `in_progress`, confined to milestones (E6–E7); **case does not matter**, so lowercase stays | Rules 3–4; `/poc-demo` `IN_PROGRESS` precedent |
| (a) Scorecard identity | **Same artifact** as `POC-DEBT-SCORECARD.md`; the skill's aggregates are appended sections | `poc-guidelines.md:100, :103`, Rules 1 and 4 |
| (b) Scales | `critical \| medium \| low`, with `critical` ⇒ `must_fix_pre_prod`; `S \| M \| L` with indicative hours; points removed | `poc-guidelines.md:123–126, :134` |
| (c) Ledger | Kept, distinct and unchanged in path; states that it feeds the scorecard and does not replace it | No branch fires |
| (d) Promotion | The skill proposes and the orchestrator creates; `should` → `P1`; 7-column row plus brief; ledger mark goes in the next version | `AGENTS.md` § Task Protocol; same-file `:118` / `:106` and `:126` / `:134` |
| Blast radius | Three source skills plus generated mirrors, registry and root-drift declarations | §5 |

**Conditions before FU-1 is dispatched:**
1. Explicit orchestrator/user approval of extending the T542 / FU-C analogy from agent files to skill files
   (§1.2(iii)).
2. Settle the (unverified) items in §9.2.

## 9. Hand-back lists

### 9.1 Corrections to the brief (all `unclear_requirements`, severity `minor`)

1. **`:118` is not only `should`.** It reads "`{must | should — based on disposition}`". `must` is also not an
   `AGENTS.md` priority, and `:118` contradicts the same file's `:106`, which uses `P0`. The skill is internally
   inconsistent, not merely out of line with `AGENTS.md`.
2. **The promotion procedure spans `:98–126`, not `:100–124`.** Steps 3–4 (`:125–126`) are outside the cited range,
   and step 4 carries its own same-file defect against `:134` (immutability).
3. **The scorecard section spans `:136–174`.** The template fence closes at `:172`, and `:174` declares the
   scorecard's role, which is evidence for §4a.
4. **Brief §2's "`:36`".** The "must account for" wording is `poc-guidelines.md:133` (Rule 1). `:36` is the
   skill's scanning sentence. The fact is right; the citation is ambiguous.
5. **Sites not in §2 that the same rulings reach:** `poc-evaluation:63–66` (template fields that E4 needs) and
   `:92–93` (scorecard linkage); `rapid-prototyping:99` (the milestone trigger that makes plain deletion wrong);
   `technical-debt-tracking:25–28` and `:59–61`. Further related sites I left unruled are recorded as F3 and F4.
6. **(b) is not only P29b's shape.** In this skill, severity interacts with a disposition axis (`:84`,
   `:104–108`) that `/evaluate-poc` never had. A coupling (`critical` ⇒ `must_fix_pre_prod`) is required to avoid
   contradicting the instruction's definition of Critical.
7. **Plan-092 P35's prior question** ("That skill may also serve the production track, so first decide whether
   `poc-guidelines.md` governs it") is not carried into brief §3. §1.4 answers it: the instruction governs
   PoC-phase use, not production-track use, and (d) rests on `AGENTS.md` instead.
8. **The facts were verified on `2d7d005`; this worktree is at `4ed6d91`.** Every line I cite matches on
   `4ed6d91`, so the gap is moot for line numbers. That the intervening commit touched only `docs/` is
   **(unverified)**.

### 9.2 Unverified claims (need a shell)

1. No agent or command names any of the three skills, and the skills reference only each other. This is brief §2;
   I confirmed it only for the three PoC commands and three PoC agents I read.
2. No golden case quotes the three skills. This is brief §2; I did not open `tests/golden/`.
3. No test outside `tests/golden/` asserts the content of these three skill files. Needs a `grep` under `tests/`
   for each skill name.
4. The number of repo-root projection paths FU-1 must declare in `tests/_baselines/root-install-drift.json`, and
   that this file is still the mechanism T564 and T567 used.
5. No production-track document defines a competing debt severity or effort scale (§1.4). Needs a `grep` for
   `XS`/`XL` and four-tier severity outside the PoC files.
6. Whether `technical-debt-tracking` is actually invoked on production-track work, through the "QA validation gate"
   trigger.
7. Whether `maturity-promotion-criteria-v2.md` §2.1's `## Rails` requirement applies to skills (F7).
8. The T542 precedent's details. I relied on `poc-contract-resolution-v1.md` §9.2 and `active-tasks.md:423–427`,
   not on T542's own brief or its `completed-tasks.md` row.
9. `4ed6d91` differs from `2d7d005` only under `docs/`.

### 9.3 Blockers

None. One **approval** is required before FU-1: the §1.2(iii) extension to skill files. It is a condition, not a
blocker on this decision.

## 10. Orchestrator verification and rulings (added before commit, 2026-10-01)

*The orchestrator added this section; the producing agent did not write it. It was written on `develop` `4ed6d91`.
It settles the claims marked (unverified) in §9.2 and decides the approval that §1.2(iii) and §6 require. §§0–9
are unchanged.*

**10.1 Unverified claims, checked**

| # | Claim | Result |
|---|---|---|
| 1 | No agent or command names the three skills | `grep` over all of `implementation/knowledge/` and `AGENTS.md`, excluding the three skills themselves: **no hits. Confirmed** (wider than the PoC files the producer checked). |
| 2 | No golden case quotes the skills | Searched `tests/golden/` with `held-out` pruned before traversal. The only hits are the installed copies of `technical-debt-tracking` and `rapid-prototyping` in the `/discover-skills` case's `fixture/installed-target/.github/skills/`. That case's `expect.py` resolves every path inside its own fixture (`ROOTS` are fixture-relative) and checks that **skill directories exist**, not what they contain. **No coupling. Confirmed:** no grant and no baseline are needed. |
| 3 | No test outside `tests/golden/` asserts the skills' content | No hits. **Confirmed.** |
| 4 | Root-projection paths to declare | The three skills are projected to **21** repo-root paths (7 platforms, including `.cline`). FU-1 must declare exactly what `--print-drift` reports, using `tests/_baselines/root-install-drift.json` as T564 and T567 did. |
| 5 | No production-track document defines a competing debt scale | No `XS`/`XL` effort scale exists anywhere else in `implementation/knowledge/` (the only `xl` hit is a CSS token in `ux-designer.md`). **Confirmed.** Separately, the four-tier `CRITICAL/HIGH/MEDIUM/LOW` scales in the security artifacts and the `/validate-workflow` remediation backlog grade different artifacts and are not touched. |
| 6 | `technical-debt-tracking` runs on production-track work | Only through its own "Automation note" (the QA validation gate trigger). No agent or command invokes it by name (#1). §1.4's reasoning stands: one Debt Item Format serves every trigger. |
| 7 | The `## Rails` requirement (`maturity-promotion-criteria-v2` §2.1) applies to skills | It applies to **all categories** (criterion b) as a *promotion* criterion. It does not block these `experimental` skills. F7 is parked as P38. |
| 9 | `2d7d005..4ed6d91` touches only `docs/` | It touches only `plan-094`, `active-tasks.md` and `task-T570.md`. **Confirmed.** |

**10.2 Rulings**

- **Approved: §1.2(iii), extending the T542/FU-C precedent from agent files to skill files.** All three skills place
  themselves inside `poc-guidelines.md`'s reach in their own descriptions. All three are `experimental`, so maturity
  is unaffected. Item (d) does not depend on this extension at all, because it rests on `AGENTS.md` § Task Protocol
  alone, which `validate-tasks.py` enforces mechanically. FU-1 (`T571`) may be dispatched.
- **Accepted: `should` → `P1`** (the skill's own must/should order, with must = `P0`). The recorded alternative,
  `P2`, is not taken. A "should" item is important but not critical, which is what `P1` already means here.
- **Accepted: E4 drops the >50% threshold.** Keeping any threshold would allow `VALIDATED` with untested criteria,
  which Rule 4 rules out.
- **Accepted: `critical` ⇒ `must_fix_pre_prod`.** This is compelled by the instruction's own meaning of Critical:
  "must fix before production".
- **Accepted: (a) the scorecard is the same artifact as `POC-DEBT-SCORECARD.md`** (same name, input and role). The
  skill points at the instruction's structure and appends its own aggregates, rather than keeping a rival format.

**10.3 Parked**

- **P38:** the PoC skill/command duplication and checkpoint items F1–F4 and F6–F8: two VERDICT formats, two handoff
  checklists, "promoted" vs `monitor_only`, task fields, the `[CHECKPOINT]` marker vs `AGENTS.md`, no `## Rails`
  sections, and the code-review severity scale in `rapid-prototyping`. **Trigger:** the next task touching
  `poc-evaluation`, `rapid-prototyping` or `/evaluate-poc`, or any promotion of these skills.
- **F5** (three debt registers) joins **P33**.
