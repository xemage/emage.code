# Artifact: poc-skill-command-overlaps-v1.md

> Filename: `poc-skill-command-overlaps-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T574
- **Created**: 2026-10-02
- **Based on**: `docs/tasks/task-T574.md`; `docs/plans/plan-097-poc-skill-command-overlaps.md`;
  `docs/artifacts/poc-skills-alignment-v1.md` §1.3, §7 (F1–F8), §10.2 (the approved extension) and §10.3 (P38);
  `docs/artifacts/gate-verdict-consistency-v1.md` §1 (the method), §5 (V5) and §13.2;
  `docs/decisions/ADR-007-command-contract-authority.md` (Accepted); `docs/artifacts/maturity-promotion-criteria-v2.md`
  §1, §2 item 1 and §3.4; `AGENTS.md`.
- **Supersedes**: none (first version)
- **Decision references**: P38 (this task). ADR-007 is **not applied**: no command clause is amended. It is cited only
  for what it does not reach. The approved bases of `poc-skills-alignment-v1.md` §10.2 (T542/FU-C extended to skill
  files; `AGENTS.md` § Task Protocol on its own) and the joint-satisfiability method of
  `gate-verdict-consistency-v1.md` §1.2(i), accepted in its §13.2, are applied. No new ADR is minted.

## 0. What this document is, and what it did not do

This document rules on P38: F1–F4 and F6–F8 of `poc-skills-alignment-v1.md` §7, at the sites in brief §2. It
specifies one follow-up task. **It changed no skill, command, agent, instruction or golden case.**

**Method and limits.** This session had **no shell**: no `grep`, `cmp`, directory listing, git or test run. Every claim
comes from reading named files directly in the worktree on branch `agent/solution-architect/T574` (`develop`
`1208790`). Anything that would need a search or a run is marked **(unverified)** and collected in §14.2.

**Files read (source, not projections):**
- skills `poc-evaluation`, `rapid-prototyping`, `technical-debt-tracking`, `checkpoint-protocol` and `code-review`, in
  full; `testing-strategy` lines 1–30 (Rails model only);
- command `evaluate-poc`, in full;
- instructions `poc-guidelines.md` in full, and `security-guidelines.md` lines 1–12 and 150–174;
- agents `poc-orchestrator` and `evaluation-agent`, in full;
- `AGENTS.md`, in full; `maturity-promotion-criteria-v2.md` lines 1–259;
- the planning and decision inputs listed above.

Under the brief's read-only grant I read `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{brief.md,expect.py}`
and nothing else under `tests/golden/`. I did not open `tests/golden/held-out/`.

**Line numbers in brief §2.** I checked each one at `1208790`. Each points at the text the brief describes. §14.1 lists
the cases where a range is too narrow, where a quote is out of date, or where a citation is ambiguous.

## 1. Authority basis

### 1.1 What does not decide anything here

- **ADR-007** governs command contracts. Branch 1 asks: "Does the clause contradict `AGENTS.md`, a `stable`
  instruction, or another clause of the same command file?" I applied that test to both `/evaluate-poc` clauses in
  P38:
  - The `## POC VERDICT` block (`:25–38`) contradicts none of them. Its `Status` is binary, as `poc-guidelines.md`
    Rule 4 requires.
  - The handoff checklist (`:40–51`) contradicts none of them either.

  **So branch 1 does not fire, and ADR-007 gives no basis to amend or add to the command.** That matches
  `gate-verdict-consistency-v1.md` §6 V7: "A sentence obliging the command to also emit the `validation-gates` block
  would *add* to its contract with no ADR-007 basis." ADR-007 also does not rank a skill against a command. **No
  ruling below amends the command.**
- **Maturity is not rank.** `/evaluate-poc` being `stable` and the two skills being `experimental` does not decide
  anything here. I do not rely on maturity anywhere. The brief's preference for editing experimental files is a
  tie-breaker among readings that are all valid. It is not authority.
- **P34b.** As quoted in `gate-verdict-consistency-v1.md` §1.1, plan-095 §1 parks agent and skill authority as P34b,
  "with the trigger: a ruling that cannot rest on a file's own self-description". I quote that trigger second-hand: I
  did not open plan-095. Every ruling below rests on the bases in §1.2. **No item triggers P34b** (§10).

### 1.2 The bases I rely on

**(i) Joint satisfiability.** Two clauses conflict only if they cannot both be obeyed. This is the method of
`gate-verdict-consistency-v1.md` §1.2(i), accepted in its §13.2. Where both can be obeyed, they are renderings or
parts of one thing, not rivals, and the amendment only says so.

| Clause | Text (verbatim) | Exclusive? |
|---|---|---|
| `poc-evaluation:33` | "Every PoC evaluation MUST conclude with a structured verdict that integrates with the gate protocol" | No. It does not say "only", "instead of" or "no other". |
| `/evaluate-poc:25` | "**Produce a structured VERDICT** at the end of the evaluation" | No |
| `poc-evaluation:112` | "complete the following handoff checklist before transitioning to production implementation" | No |
| `/evaluate-poc:42` | "**If recommending `proceed` or `proceed_with_constraints`**, produce a handoff checklist" | No |

**(ii) One PoC, one outcome.** `poc-guidelines.md:56`, Rule 4: "**Binary outcome** — A PoC either validates or
invalidates the hypothesis." Two renderings of one evaluation therefore carry one value. This plays the role that
`validation-gates:11`'s singular "a structured verdict" played in `gate-verdict-consistency-v1.md` §1.2(i). The
instruction's reach over these skill files is the approved §10.2 extension of `poc-skills-alignment-v1.md`.

**(iii) Self-description.** These are places where one file names another as doing part of its work.
- `poc-evaluation:96`, template § 8: "… to any debt-ledger items the technical-debt-tracking skill created from this
  evaluation". The evaluation leaves debt-item mechanics to `technical-debt-tracking`.
- `technical-debt-tracking:36`: "This skill is responsible for scanning codebases for `POC-DEBT` tags".
- `technical-debt-tracking:54–57`, Step 3, merges in "PoC evaluation refactoring backlog items" and "Code review
  findings (🔴 Must Fix and 🟡 Should Fix items)".
- `technical-debt-tracking:101`: "this skill prepares the proposals, and the orchestrator decides on them and creates
  the tasks."
- `rapid-prototyping:54`'s "🟡 Should Fix" is the label of skill `code-review` § Severity Guide (`:93–98`), and it
  carries that guide's criteria with it.

**(iv) `AGENTS.md`, applied to a skill.** The precedent is `poc-skills-alignment-v1.md` §1.3, approved in §10.2: "Item
(d) … rests on `AGENTS.md` § Task Protocol alone". The sentences used here are:
- § Task Protocol: "Only orchestrators create/transition tasks. Agents report completion and blockers." and the
  ledger columns `ID | Title | Owner | Status | Priority | Depends on | Last update`;
- § Checkpoint Protocol: "Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`", "Written at every phase
  boundary by the orchestrator."

**(v) Same-file coherence.** A clause is corrected to agree with its own file, as in `poc-skills-alignment-v1.md`
§4d.

### 1.3 What this costs, and the alternatives not taken

- **The contestable part.** An evaluation run through `/evaluate-poc` now carries the command's block **and** the
  skill's marker (F1), and one checklist of 13 + 7 items (F2). That is verbose. It is the honest result of obeying
  every MUST without ranking any of them.
- **Alternative A: collapse to one format or one checklist.** Choosing whose format survives ranks a skill against a
  command. That is P34b. **Not taken.**
- **Alternative B: amend `/evaluate-poc` to absorb the skill's items or marker.** ADR-007 gives no basis to add to a
  command contract (§1.1). It would also change the golden case (`expect.py:22`, `:33`) and need a grant and a v16
  baseline, with nothing compelling it. **Not taken.** This is the absence of an authority, not softening to avoid
  coupling: no reading I found requires the command to change.
- **Alternative C: copy the command's eight checklist items into the skill unconditionally.** This is not compelled,
  and a copy can drift. The skill names them instead (E7).

## 2. F1: two verdict shapes for one PoC evaluation

| Field | Value |
|---|---|
| **Sites** | `poc-evaluation:33–37` (`[VERDICT] gate=poc-evaluation \| …`); `/evaluate-poc:23–38` (`## POC VERDICT`, eight fields) |
| **Ruling** | **Consistent, with a specialisation note.** The marker is the one-line rendering of the evaluation's single verdict. Under `/evaluate-poc` it **accompanies** the command's block and carries the same values. |
| **Why it is not a rival** | §1.2(i): neither clause is exclusive. A report can hold the `## POC VERDICT` block and end on the marker line. §1.2(ii): one PoC has one outcome, so the two renderings carry one value. The fields map one-to-one where they overlap: `result=` ↔ `Status`; `evidence_strength=` ↔ `Evidence strength` (identical value sets, `poc-evaluation:36` and `/evaluate-poc:33`); `production_recommendation=` ↔ `Production recommendation` (identical sets); `hypothesis=` ↔ `Hypothesis`; `debt_count=` ↔ the `Debt items` total; `date=` ↔ the date of `Timestamp`. The rest is additive: `poc_ref` on the skill's side; `Residual risks`, `Evaluator` and the severity breakdown on the command's side. That is the "adds, does not compete" test of `poc-skills-alignment-v1.md` §4a. |
| **Placement** | "MUST conclude with" (skill) and "at the end of the evaluation" (command) are both met by putting the block in the closing part of the report and the marker on the last line. The command's own steps 10–11 follow step 9, so its "at the end" is not literal either. |
| **V5 note, deferred to here** | `gate-verdict-consistency-v1.md` §5 ruled the marker outside `validation-gates`' reach and deferred any note to P38. E2 includes that note, because the paragraph has to be written anyway. |
| **Also considered: the template's `## 4. Verdict`** | This is the prose verdict inside the skill's full artifact, the counterpart of the command's step 3. The golden case's brief already reads "the structured block is the declared contract for both" (`brief.md:95–96`). No edit. |
| **Golden interaction** | None. E2 edits only the skill. Even an output that follows E2 is safe: `_verdict` keeps only lines matching `FIELD_RE` (`expect.py:43`, `:59`), so a `[VERDICT]` line inside the block's section is ignored. |
| **Amendment** | E2 (§9). |

## 3. F2: two "Production Handoff Checklist"s for one trigger

| Field | Value |
|---|---|
| **Sites** | `poc-evaluation:110–139` (13 items in four groups, inside a fence ending at `:137`, then `:139`); `/evaluate-poc:40–51` (8 items) |
| **Ruling** | **Complementary; one same-file amendment and one specialisation note, plus one wording alignment.** Under `/evaluate-poc` the handoff checklist is the union of the two lists. |
| **Why complementary** | §1.2(i): both say "complete" or "produce" a checklist, and neither says "only these items". The item sets do different jobs. The skill's items are process and knowledge transfer (debt cataloguing, contracts, learnings, task flow, approvals). The command's items are production readiness (performance baselines, test coverage plan, migration strategy, monitoring, infrastructure, security audit). I compared every pair and found no contradiction. One item is the same in substance: skill `:119` "Architecture decisions from PoC documented as decision artifacts" and command `:45` "Architecture decisions documented in `docs/decisions/`". The command's "All CRITICAL debt items have remediation plans with owners" is met by the F4 flow: `critical` ⇒ `must_fix_pre_prod` (`technical-debt-tracking:97`) ⇒ a proposal with an owner and a target sprint (`:107`, `:114–123`). |
| **Same-file defect at `:112`** | "When the **verdict** is `proceed` or `proceed_with_constraints`" uses the verdict for a production-recommendation value. The skill's own Framework separates them: step 3 is "Decide verdict" and step 5 is "Decide production recommendation: proceed \| proceed_with_constraints \| do_not_proceed" (`:12`, `:14`). Its § Verdicts lists only Validated and Invalidated (`:18–20`). Basis §1.2(v). The corrected wording also matches the command's trigger (`:42`, "If recommending …"). |
| **Wording alignment at `:119` (editorial, not compelled)** | Aligning `:119` to the command's exact words lets the union list the architecture item once, with no judgement about whether two wordings are the same item. "Decision artifacts" are `docs/decisions/ADR-<NNN>-<slug>.md` under `AGENTS.md` § Decision Log, so no meaning is lost. **Recorded alternative:** keep both wordings and list both lines. Not taken, because it puts one requirement on the checklist twice. |
| **Golden interaction** | None. The command is unchanged. An output that follows E7 contains the command's eight items verbatim, as `- [ ]` lines. That is what `expect.py:136–139` looks for anywhere in the report. It is a subset check, so the skill's extra items never fail it. |
| **Amendment** | E3 (`:112`), E5 (`:119`), E7 (union note after `:139`). |

## 4. F3: "All POC-DEBT tags cataloged and promoted" against `monitor_only`

| Field | Value |
|---|---|
| **Site** | `poc-evaluation:118`: "All POC-DEBT tags cataloged and promoted to technical debt backlog" |
| **Clauses against it** | `technical-debt-tracking:109`: "`monitor_only` \| Do not propose a task; add to risk register with monitoring criteria". Its § Promotion Procedure uses "promotion" for one specific act, "from the debt ledger to the production task backlog" (`:101`), filtered by disposition (`:113`). |
| **Ruling** | **Amend `poc-evaluation:118`.** "All … promoted" admits three readings, because "technical debt backlog" is a term neither skill defines. If it means the debt ledger, the line is consistent. If it means the evaluation's own § 6 Refactoring Backlog, it is redundant. If it means the production task backlog, which is the only object `technical-debt-tracking` "promotes" to, it collides with `monitor_only`. A checklist line that one reading turns into a contradiction is defective as written. |
| **Why this is not a rank** | The replacement asks for what both sides already require, so it chooses no winner. (a) **Every tag in the scorecard**: `poc-guidelines.md:133`, Scorecard Rule 1, "The scorecard must account for **every** `POC-DEBT` tag in the codebase", reaching this skill through the approved §10.2 extension. (b) **Every tag in the ledger with a disposition**: `technical-debt-tracking` Step 2 parses "each discovered tag" into a debt item (`:44–50`), and the Debt Item Format carries `Disposition` (`:84`). (c) **Self-description**: `poc-evaluation:96` already places the ledger items in `technical-debt-tracking`'s hands. Promotion itself moves to the Task Creation group (F4), where it is filtered by disposition. |
| **Amendment** | E4 (§9). |

## 5. F4: "created as tasks … with severity and target sprint"

| Field | Value |
|---|---|
| **Sites** | `poc-evaluation:128–131`, the whole `### Task Creation` group (the brief cites `:129–130`) |
| **Ruling** | **Consistent on a joint-satisfiability reading. A clarifying amendment makes that reading explicit and closes an F3-shaped gap.** |
| **The reading** | The checklist lines are passive ("created"). They state that tasks exist and do not say who creates them, so an orchestrator creating them satisfies both the line and `AGENTS.md` § Task Protocol. Under `/evaluate-poc` the executor is `poc-orchestrator` (`agent:` frontmatter), and `AGENTS.md` § Team Model names it an orchestrator. `AGENTS.md` lists what a brief contains ("objective, inputs, outputs, acceptance criteria") without excluding anything else, so severity and target sprint can sit in the brief's prose. That is where `poc-skills-alignment-v1.md` §4d put "Sprint" ("Sprint becomes brief context, since the ledger has no sprint column"). |
| **Why amend anyway** | (1) "Tasks created **with** severity and target sprint" reads as task fields, and an `AGENTS.md` row has neither. T571's E13 already defines the carrier: a proposal with "Proposed priority" and "Target sprint" (`technical-debt-tracking:114–123`). (2) "Refactoring backlog items created as tasks" (`:129`) has F3's shape. The § 6 backlog is built "from POC-DEBT tags and review findings" (`:83`), so it can hold `monitor_only` items, which must not become tasks (`:109`). `technical-debt-tracking` Step 3 already merges the backlog into the ledger (`:56`), which is where dispositions are assigned. (3) The amendment names an actor, so the passive voice cannot be read as "the evaluator creates them". |
| **Authority** | `AGENTS.md` § Task Protocol, the approved §10.2 basis (§1.2(iv)); `technical-debt-tracking:56`, `:101`, `:113–124` (self-description, §1.2(iii)). **No rank:** the amended lines route through procedures both skills already state. |
| **Severity** | It is dropped from the task line on purpose. A proposal has no severity field. Severity lives on the ledger item (`:76`), which the proposal references by `DEBT-{ID}`, and it reaches the task as the proposed priority through disposition (`:97`, `:107–108`). |
| **Amendment** | E6 (§9). |

## 6. F6: `rapid-prototyping`'s `[CHECKPOINT]` marker against `AGENTS.md` § Checkpoint Protocol

| Field | Value |
|---|---|
| **Sites** | `rapid-prototyping:97–105` (heading `:97`, "publish" `:99`, marker `:102`) |
| **Clauses against it** | `AGENTS.md` § Checkpoint Protocol: checkpoints are files at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, "Written at every phase boundary by the orchestrator", and they "Include: completed tasks, key decisions, blockers, token metrics, next steps". |
| **Ruling** | **Consistent on a reconciling reading, with a specialisation note and one verb change.** The marker is a **status line that a prototyping agent reports to the orchestrator**, not a checkpoint in `AGENTS.md`'s sense. The orchestrator carries its content into the checkpoint it writes for that phase. |
| **Why it is not a rival** | §1.2(i): the skill names no file, no path and no checkpoint sections. It defines one line. A line in a completion report is "Agents report completion and blockers" (`AGENTS.md` § Task Protocol), and writing it creates no checkpoint. The PoC track's own orchestrator already owns the checkpoint for the phase this skill serves: `poc-orchestrator.md:35` ("Write checkpoints after each PoC phase (scout → feasibility → scaffold → integrate → demo → evaluate)") and `:92` ("After scaffolding + integration complete"). Its specialists are the ones who prototype (`:48–49`, `@scaffolding-agent`, `@integration-agent`). |
| **Why amend anyway** | "**publish** a hypothesis validation **checkpoint**" (`:99`), tagged `[CHECKPOINT]`, invites an agent to write a checkpoint, which only the orchestrator does. The note states the reading where the agent will see it. |
| **Not changed: the tag `[CHECKPOINT]`** | Renaming it (for example to `[POC-STATUS]`) would change a marker grammar with no quoted authority. That is the reasoning `gate-verdict-consistency-v1.md` §1.3 Alternative B used. **Recorded alternative; not taken.** "milestone checkpoint" at `:105` and "Checkpoint triggers" at `:112` stay for the same reason, and the note covers them. |
| **Unchanged elsewhere** | `poc-evaluation:139` ("referenced in the next checkpoint summary") is passive. The orchestrator's checkpoint references the checklist. Consistent; no edit. |
| **Amendment** | E10 (`:99`), E11 (note after `:103`). |

## 7. F7: `## Rails` sections for the three PoC skills

| Field | Value |
|---|---|
| **Facts** | `maturity-promotion-criteria-v2.md` §1 criterion (b), "Explicit rails", "Applies as-is" to `skill` (`:66`). §2 item 1 defines the section (`:106–112`): heading `## Rails` with non-empty `**Inputs**:`, `**Out of scope**:` and `**Failure mode**:`. §3.4 makes it criterion 2 of a skill's **`experimental → beta`** step (`:221–225`), with skill-specific meanings: "'inputs' as the situation/trigger for using the skill, 'out of scope' as what the skill deliberately excludes, 'failure mode' as what the skill instructs when its own procedure cannot complete." Nothing requires Rails while a skill stays `experimental`. |
| **Decision** | **Author them now, in the same follow-up, for all three skills.** This is not compelled. It is a judgement, and the reasons are below. |
| **Why now** | (1) The Out-of-scope line is the most durable place to record F1, F4 and F6. These rulings are all scope boundaries: the skill does not create tasks, does not write checkpoints, and its `gate=` is not a validation gate. A promotion-time author would have to rediscover them. (2) FU-1 already edits `poc-evaluation` and `rapid-prototyping`, and declares their root drift, so their Rails cost nothing extra in process. (3) P38's own trigger includes "any promotion of these skills" (`poc-skills-alignment-v1.md` §10.3). Writing Rails now removes one of the gaps a promotion would hit. (4) Every Rails sentence below restates text already in the file, in `AGENTS.md` or in `poc-guidelines.md`. None adds behaviour. |
| **What it does not do** | It changes no `maturity:` value and is not a promotion claim. Beta still needs `maturity: beta` set and no open P0 defect (§3.4 items 1 and 3). |
| **`technical-debt-tracking`** | It is not otherwise touched by P38. Its Rails (E12) is included for the trio's consistency, at the cost of 7 more root-drift paths. The orchestrator may split E12 out without affecting E1–E11. |
| **Placement** | Directly after the H1 title, as in `testing-strategy:9`, `checkpoint-protocol:9` and `poc-guidelines.md:9`. |
| **Amendment** | E1, E8, E12 (§9). |

## 8. F8: `rapid-prototyping:54`, "🟡 Should Fix" for untagged shortcuts

| Field | Value |
|---|---|
| **Site** | `rapid-prototyping:54`: "Untagged shortcuts discovered during review are flagged as review findings (severity: 🟡 Should Fix)." |
| **Ruling** | **Consistent on one reading; a clarifying amendment makes that reading explicit.** The label is the `code-review` skill's review-finding scale, used for a review finding. That is its own domain, and it is not a debt-severity scale (`poc-skills-alignment-v1.md` §7 F8). The defect is the line's subject. As written, it grades **the shortcut** at 🟡 whatever the shortcut is. |
| **Why that matters** | The line borrows `code-review`'s labels, and so their criteria (§1.2(iii)): "🔴 Must Fix \| Bug, security issue, data loss risk \| Block merge" and "🟡 Should Fix \| Performance, maintainability concern \| Request changes" (`code-review:96–97`). A fixed 🟡 for an untagged shortcut that is a security issue would apply that scale against its own criteria. The coherent reading: the **missing tag** is the 🟡 finding (untracked debt is a maintainability concern), and the shortcut is graded like any other finding. `technical-debt-tracking:55` already expects both 🔴 and 🟡 review findings to reach the ledger, where debt severity is assigned separately. |
| **Authority** | Same-scale coherence with the scale the line itself names; `technical-debt-tracking` Step 3 (self-description). No rank. |
| **Amendment** | E9 (§9). |

## 9. Exact amendments (follow-up FU-1)

Each edit is matched by its exact **before** text, and each before text is unique in its file. Line numbers refer to
source at `1208790`, before any edit. `—` is U+2014 wherever it appears. A three-backtick line inside a block is a
literal three-backtick fence. All edits are to `experimental` skills, and **none touches `/evaluate-poc`.**

### `implementation/knowledge/skills/poc-evaluation/SKILL.md`

#### E1: `:7–9` (F7): insert `## Rails`

````
Before:
# PoC Evaluation

## Framework

After:
# PoC Evaluation

## Rails
**Inputs**: A PoC whose outcome is to be assessed: its PoC artifact (`poc-{name}-v{N}`) with the hypothesis and success criteria defined before the PoC started, the evidence gathered against them, and the PoC's `POC-DEBT-SCORECARD.md` and debt ledger (technical-debt-tracking skill). This includes an evaluation run through the `/evaluate-poc` command.

**Out of scope**: Does not scan for `POC-DEBT` tags or write the scorecard; the technical-debt-tracking skill does, and § 8 of the evaluation links to its items. Does not create tasks or write checkpoints: debt items reach the task backlog as promotion proposals, and an orchestrator creates the tasks and writes the checkpoints (`AGENTS.md` § Task Protocol, § Checkpoint Protocol). The `[VERDICT]` line is the PoC track's hypothesis verdict, not a `validation-gates` gate verdict.

**Failure mode**: If any success criterion defined in the PoC artifact was not tested by the PoC's deadline, or rests only on weak evidence, the verdict is `INVALIDATED` with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria (§ Hypothesis Success Criteria Reference). Never force a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).

## Framework
````

**Authority:** criteria-v2 §3.4 item 2 (shape). Content: `:36`, `:96`, `:104–108`; F1, F4 and F6 rulings;
`technical-debt-tracking:36`, `:59–61`.

#### E2: `:36–39` (F1): insert one paragraph after the marker fence

````
Before:
[VERDICT] gate=poc-evaluation | result=VALIDATED|INVALIDATED | evidence_strength=strong|moderate|weak | poc_ref=poc-{name}-v{N} | hypothesis="{short hypothesis}" | production_recommendation=proceed|proceed_with_constraints|do_not_proceed | debt_count={N} | date={YYYY-MM-DD}
```

**Full evaluation artifact structure:**

After:
[VERDICT] gate=poc-evaluation | result=VALIDATED|INVALIDATED | evidence_strength=strong|moderate|weak | poc_ref=poc-{name}-v{N} | hypothesis="{short hypothesis}" | production_recommendation=proceed|proceed_with_constraints|do_not_proceed | debt_count={N} | date={YYYY-MM-DD}
```

This line is the one-line rendering of the evaluation's single verdict: a PoC either validates or invalidates its hypothesis (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). When the evaluation is run through the `/evaluate-poc` command, the line accompanies, and does not replace, that command's `## POC VERDICT` block. Both record the same evaluation, so their values agree: `result=` is the block's `Status`, `evidence_strength=` its `Evidence strength`, `production_recommendation=` its `Production recommendation`, and `hypothesis=` a short form of its `Hypothesis`; `debt_count=` is the total in its `Debt items` line, and `date=` is the date of its `Timestamp`. `gate=poc-evaluation` names this PoC-track verdict. It is not one of the `validation-gates` skill's gate types, and its values are not that skill's `PASS` / `CONDITIONAL_PASS` / `FAIL`.

**Full evaluation artifact structure:**
````

**Authority:** §1.2(i), (ii); `gate-verdict-consistency-v1.md` §5 (V5) and its §2 mapping row "`poc-evaluation` |
**none: PoC-track hypothesis verdict**".

#### E3: `:112` (F2, same-file)

````
Before:
When the verdict is `proceed` or `proceed_with_constraints`, complete the following handoff checklist before transitioning to production implementation:

After:
When the production recommendation is `proceed` or `proceed_with_constraints`, complete the following handoff checklist before transitioning to production implementation:
````

**Authority:** same-file, `:12`, `:14`, `:18–20` (§1.2(v)).

#### E4: `:118` (F3)

````
Before:
- [ ] All POC-DEBT tags cataloged and promoted to technical debt backlog

After:
- [ ] All POC-DEBT tags inventoried in `POC-DEBT-SCORECARD.md` (`poc-guidelines.md` Scorecard Rule 1) and recorded in the debt ledger with a disposition (technical-debt-tracking skill)
````

**Authority:** `poc-guidelines.md:133`; `technical-debt-tracking:44–50`, `:84`; `poc-evaluation:96`.

#### E5: `:119` (F2, editorial alignment)

````
Before:
- [ ] Architecture decisions from PoC documented as decision artifacts

After:
- [ ] Architecture decisions documented in `docs/decisions/`
````

**Authority:** none compels it (§3). It copies `/evaluate-poc:45` exactly, including the backticks, so that E7's union
lists the item once. It is consistent with `AGENTS.md` § Decision Log.

#### E6: `:128–131` (F4): replace the Task Creation group

````
Before:
### Task Creation
- [ ] Refactoring backlog items created as tasks in docs/tasks/active-tasks.md
- [ ] Debt remediation tasks created with severity and target sprint
- [ ] Production implementation tasks created referencing PoC artifacts

After:
### Task Creation
- [ ] Refactoring backlog items merged into the debt ledger (technical-debt-tracking skill, § POC-DEBT Tag Scanning Procedure, Step 3)
- [ ] Promotion proposals for every `must_fix_pre_prod` and `can_defer_post_ga` debt item reported to the orchestrator, each with its proposed priority and target sprint (technical-debt-tracking skill, § Promotion Procedure for Debt Items to Production Backlog)
- [ ] Production implementation tasks, and tasks for the accepted proposals, created by an orchestrator as rows in `docs/tasks/active-tasks.md` with `docs/tasks/task-<ID>.md` briefs, referencing PoC artifacts (`AGENTS.md` § Task Protocol)
````

**Authority:** `AGENTS.md` § Task Protocol; `technical-debt-tracking:56`, `:101`, `:113–124`. The group keeps three
items and its heading.

#### E7: `:139` (F2): append the union note

````
Before:
The completed checklist is included in the evaluation artifact and referenced in the next checkpoint summary.

After:
The completed checklist is included in the evaluation artifact and referenced in the next checkpoint summary.

When the evaluation is run through the `/evaluate-poc` command, that command's step 10 handoff checklist is required for the same recommendations. Its items complement this list and do not replace it. Produce one `## Production Handoff Checklist` holding this list's four groups and a fifth group, `### Production Readiness (/evaluate-poc step 10)`, with the command's other seven items, each worded exactly as the command words it. The command's eighth item, its architecture-decisions item, is already in the Code & Architecture group in the same words, so list it there only.
````

**Authority:** §1.2(i); `/evaluate-poc:42–51`. **Depends on E5.** If E5 is not applied, replace the last two sentences
with: "… a fifth group, `### Production Readiness (/evaluate-poc step 10)`, with all eight of the command's items, each
worded exactly as the command words it."

### `implementation/knowledge/skills/rapid-prototyping/SKILL.md`

#### E8: `:7–9` (F7): insert `## Rails`

````
Before:
# Rapid Prototyping

## When to use

After:
# Rapid Prototyping

## Rails
**Inputs**: A PoC repository to bootstrap or a minimal architecture slice to build (§ When to use), for a hypothesis documented before any code is written (`poc-guidelines.md` § Hypothesis-First Validation, Rule 1).

**Out of scope**: Does not scan for `POC-DEBT` tags or write the debt scorecard (the technical-debt-tracking skill scans for them, § Mandatory Debt Tagging), and does not run the PoC evaluation (the poc-evaluation skill). Does not write checkpoint files: its `[CHECKPOINT]` line is reported to the orchestrator, which writes the checkpoints (`AGENTS.md` § Checkpoint Protocol).

**Failure mode**: When the PoC time-box expires, report the `[CHECKPOINT]` line with whatever evidence exists. A hypothesis not validated by then is `invalidated`, and a partial result is `invalidated` with `next=` naming a follow-up PoC with refined criteria (§ Hypothesis Validation Checkpoint Format; `poc-guidelines.md` Rules 3–4). A shortcut found without a `POC-DEBT` tag is flagged as a review finding (§ Mandatory Debt Tagging, Enforcement).

## When to use
````

**Authority:** criteria-v2 §3.4 item 2 (shape). Content: `:10–11`, `:53–54`, `:105`, `:115`; F6 ruling;
`poc-guidelines.md:53`.

#### E9: `:54` (F8)

````
Before:
- Untagged shortcuts discovered during review are flagged as review findings (severity: 🟡 Should Fix).

After:
- An untagged shortcut discovered during review is flagged as a review finding. The missing tag is a 🟡 Should Fix finding. The shortcut itself is graded like any other finding on the code-review skill's § Severity Guide, so a shortcut that is a bug, security issue or data loss risk is a 🔴 Must Fix finding. These labels grade review findings, not debt: the technical-debt-tracking skill assigns the debt severity when it merges the finding into the debt ledger (§ POC-DEBT Tag Scanning Procedure, Step 3).
````

**Authority:** `code-review:93–98`; `technical-debt-tracking:54–57`, `:89–95`.

#### E10: `:99` (F6)

````
Before:
At the conclusion of prototyping (or at significant milestones), publish a hypothesis validation checkpoint:

After:
At the conclusion of prototyping (or at significant milestones), report a hypothesis validation checkpoint line to the orchestrator:
````

#### E11: `:102–105` (F6): insert one paragraph after the marker fence

````
Before:
[CHECKPOINT] id=poc-{name}-validation | hypothesis="{hypothesis text}" | evidence=[{evidence items}] | debt_tags={count} | verdict=validated|invalidated|in_progress | artifact_refs=[poc-{name}-v{N}] | next=[{next steps}]
```

**Verdict values:** `in_progress` is allowed only at a milestone checkpoint, before any of the checkpoint triggers below has fired. At a trigger, the verdict is binary: `validated` or `invalidated` (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). A hypothesis not validated when the time-box expires is `invalidated` (Rule 3). A partial result is `invalidated`, and `next=` names a follow-up PoC with refined criteria.

After:
[CHECKPOINT] id=poc-{name}-validation | hypothesis="{hypothesis text}" | evidence=[{evidence items}] | debt_tags={count} | verdict=validated|invalidated|in_progress | artifact_refs=[poc-{name}-v{N}] | next=[{next steps}]
```

This line is a status report, not a checkpoint file. Checkpoints (`docs/checkpoints/checkpoint-<SEQ>-<phase>.md`) are written by the orchestrator at every phase boundary (`AGENTS.md` § Checkpoint Protocol). Include the line in your report to the orchestrator (`AGENTS.md` § Task Protocol: "Agents report completion and blockers"). The orchestrator carries what it needs from the line into the checkpoint for that phase.

**Verdict values:** `in_progress` is allowed only at a milestone checkpoint, before any of the checkpoint triggers below has fired. At a trigger, the verdict is binary: `validated` or `invalidated` (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). A hypothesis not validated when the time-box expires is `invalidated` (Rule 3). A partial result is `invalidated`, and `next=` names a follow-up PoC with refined criteria.
````

**Authority for E10–E11:** `AGENTS.md` § Checkpoint Protocol and § Task Protocol; corroborated by
`poc-orchestrator.md:35`, `:92`. The `:105` paragraph is unchanged and is carried in Before/After only as an anchor.

### `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`

#### E12: `:7–9` (F7): insert `## Rails`

````
Before:
# Technical Debt Tracking

## Categories

After:
# Technical Debt Tracking

## Rails
**Inputs**: A PoC codebase to scan for `POC-DEBT` tags, plus the code-review findings, PoC-evaluation refactoring backlog items and security-scan findings to merge with them (§ POC-DEBT Tag Scanning Procedure). The scan runs at the conclusion of every PoC (before evaluation), before any production handoff, and as part of the QA validation gate (Automation note).

**Out of scope**: Does not create or transition tasks: it writes promotion proposals, and the orchestrator decides on them and creates the tasks (`AGENTS.md` § Task Protocol; § Promotion Procedure for Debt Items to Production Backlog). Does not define a second scorecard: it adds sections to `POC-DEBT-SCORECARD.md` (§ Scorecard Requirements).

**Failure mode**: If the scorecard does not account for every `POC-DEBT` tag found in Step 1, it is not finalized, and no PoC task may be marked complete without a finalized scorecard (`poc-guidelines.md` Scorecard Rules 1 and 4). A `critical` item cannot be deferred or only monitored: it is always `must_fix_pre_prod`.

## Categories
````

**Authority:** criteria-v2 §3.4 item 2 (shape). Content: `:26`, `:36`, `:54–66`, `:97`, `:101`; `poc-guidelines.md:133`,
`:136`.

**Unchanged in all three skills:** frontmatter (so the registry's descriptive fields do not change; only checksums
move) and every line not named above.

## 10. P34b blockers

**None.** I found no item that needs a skill or agent ranked against a command or another skill:
- F1 and F2 rest on joint satisfiability (§1.2(i)), plus Rule 4 (one outcome) and same-file coherence.
- F3 and F4 rest on readings both skills share, plus the approved §10.2 bases.
- F6 rests on a reading that leaves `AGENTS.md` fully obeyed.
- F7 rests on the criteria document.
- F8 rests on the scale the line itself names.

O2 (§13) is the only P34b *candidate*, and it is outside scope.

## 11. Blast radius and golden coupling

**`/evaluate-poc` and its golden case.** No edit touches `implementation/knowledge/commands/evaluate-poc.md`. The case
`tests/golden/open/evaluate-poc-verdict-debt-reconciliation` checks that command verbatim (`brief.md:11`). Its
`FIELDS` (`expect.py:22`) and `CHECKLIST` (`:33`) stay correct. **No protected-path grant, no re-fixturing and no v16
evaluator-hash baseline are needed.** For the record, nothing here weakens the case: every assertion stays as it is.

**Files the follow-up edits.** None is under `tests/golden/**`.

| File | Edits | Maturity | Golden reads it? |
|---|---|---|---|
| `implementation/knowledge/skills/poc-evaluation/SKILL.md` | E1–E7 | experimental | No live read, per `poc-skills-alignment-v1.md` §10.1 #2 (checked at `4ed6d91`) **(unverified at `1208790`)** |
| `implementation/knowledge/skills/rapid-prototyping/SKILL.md` | E8–E11 | experimental | Only a frozen installed copy in the `/discover-skills` case fixture, where `expect.py` checks that the directory exists (§10.1 #2) **(unverified at `1208790`)** |
| `implementation/knowledge/skills/technical-debt-tracking/SKILL.md` | E12 | experimental | Same as `rapid-prototyping` |

**Generated outputs (mechanical, not content):**
- the `implementation/.<platform>/skills/<name>/SKILL.md` mirrors, via
  `node implementation/scripts/sync.mjs --root implementation`;
- `implementation/registry/index.json` checksums, via `python3 implementation/scripts/generate-registry.py`. Confirm
  both with `--check`;
- the repo-root projections. `poc-skills-alignment-v1.md` §10.1 #4 counted **21** paths for these three skills (7
  platforms). Declare exactly what `--print-drift` reports in `tests/_baselines/root-install-drift.json`. Do not
  hand-edit the root folders (`AGENTS.md` § Knowledge Base). The count is **(unverified)** at `1208790`, and it drops
  to 14 if E12 is split out.

**Maturity.** No `maturity:` value changes, and no `stable` file is edited. Adding Rails to `experimental` skills
should leave `check-maturity` at its baseline (79 components, 0 failing; skills 7 stable / 19 experimental, per
`gate-verdict-consistency-v1.md` §13.1 #7) **(unverified)**.

**Parked triggers.**
- **Fires:** P38 (this task).
- **Does not fire:** P33 (`poc-guidelines.md` is not edited); P39, P40 and P41 (no file in their scope is edited).

## 12. Follow-up tasks

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / notes |
|---|---|---|---|---|---|---|
| **FU-1**: apply the P38 skill edits | E1–E12 | `implementation/knowledge/skills/{poc-evaluation,rapid-prototyping,technical-debt-tracking}/SKILL.md`; the regenerated `implementation/.<platform>/` mirrors; `implementation/registry/index.json` via the generator; root-drift declarations in `tests/_baselines/root-install-drift.json` | **No** | Backend Developer (the owner class of T571 and T573) | P2 (plan-097 §2) | **Before dispatch:** the orchestrator settles §14.2 items 1 and 4, and decides whether to keep E12 in. **Verify:** (1) each before text matched exactly once; (2) `sync.mjs --check` and `generate-registry.py --check` are clean; (3) the root parity gate is green; (4) `## Rails` occurs exactly once in each edited skill; (5) these phrases have 0 hits under `implementation/knowledge/`: "promoted to technical debt backlog", "publish a hypothesis validation checkpoint", "When the verdict is `proceed`", and "created with severity and target sprint"; (6) `commands/evaluate-poc.md` and everything under `tests/golden/` are byte-unchanged (`git diff --stat`); (7) the `check-maturity` baseline is unchanged; (8) the golden scorecard is unchanged. |

**There is no command follow-up and no golden follow-up.** The orchestrator does not need to raise a v16 question with
the user for P38.

## 13. Findings outside scope (not decided; candidates for parking)

- **O1 (major, security): PoC "shortcut" examples that the Immutable Security Constraints forbid.**
  `security-guidelines.md:157`, Constraint 3, reads: "Security middleware, input validation, and authentication checks
  must never be bypassed, even in development or PoC mode." `:158`, Constraint 4, reads: "Every input from outside the
  system boundary … must be validated before use." Against them:
  - `rapid-prototyping:33` lists "disabled security" as a taggable configuration shortcut.
  - `rapid-prototyping:37` gives "No input validation — add comprehensive validation before production" as a model
    tag.
  - The stable instruction `poc-guidelines.md:84` has the same example.

  `poc-guidelines.md:17–19` (Rails) says it "Does not waive the Immutable Security Constraints", so its own example
  contradicts its own Rails. Tagging does not make a forbidden pattern legal. This touches a stable instruction (P33's
  file) and a `security-guidelines` constraint. FU-1 deliberately leaves `rapid-prototyping:30–49` untouched. I
  recommend a separate ruling with Security Engineer input. Whether this is already parked is **(unverified)**.
- **O2 (P34b candidate): two binary outcome claims for one PoC.** The prototyping agent's `[CHECKPOINT]` carries
  `verdict=validated|invalidated` at a trigger (`rapid-prototyping:105`). The evaluation later decides the verdict
  (`poc-evaluation:12`, `:106–108`). No text says which one is the PoC's outcome, or that the checkpoint's verdict is
  provisional. Self-description points toward the evaluation: the skill descriptions say "Assess proof-of-concept
  outcomes" versus "scaffolding … for fast proof-of-concept delivery". But ruling it would decide between two skills
  on more than a reading. Not ruled.
- **O3 (minor, protected path, report only): the golden case brief overstates and under-specifies.**
  - `brief.md:54–55` says the eight checklist items are present "**when and only when**" the recommendation is
    `proceed`/`proceed_with_constraints`. `expect.py:136–139` checks only "when", and `brief.md:117` confirms that
    `do_not_proceed` with no checklist passes. Nothing fails a checklist present under `do_not_proceed`.
  - `expect.py:98–103` reads step 6's "top 5 minimum" as ≥ 5 *numbered* lines under exactly one heading containing
    "backlog". `poc-evaluation`'s template renders its backlog as a table under `## 6. Refactoring Backlog`
    (`:82–88`). A real `/evaluate-poc` output that follows the skill's template would therefore fail the case, though
    it meets the command's prose.

  Neither is mine to change (`protected-paths-v1.md`). Neither weakens anything here.
- **O4 (minor): F4's shape in the stable `code-review` skill.** `code-review:151` says should-fix items are "logged as
  a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint". The actor is unstated, and the
  ledger has no sprint column. `:153` adds "recorded in the next checkpoint summary under `decisions=[...]`", a
  checkpoint grammar that neither `AGENTS.md` nor `checkpoint-protocol` defines. Candidate for P41.
- **O5 (minor): `checkpoint-protocol` against `AGENTS.md` and itself.**
  - `:59` has "**Author:** <agent-name or orchestrator>", against "by the orchestrator".
  - `:104` writes to `docs/checkpoints/checkpoint-<N>.md`, against its own `:44` and `AGENTS.md`'s
    `checkpoint-<SEQ>-<phase>.md`.
  - `:173`'s example has the same problem.
- **O6 (minor): a vacuous `VALIDATED`.** `poc-evaluation:106` reads "`VALIDATED` only if every success criterion
  defined in the PoC artifact was tested and met". If the artifact defines none, that is vacuously true. `poc-guidelines`
  Rule 1 and the Hypothesis Format require success criteria, so the case should not arise, but the skill does not say
  what to do if it does.
- **O7 (minor; P33-adjacent): the scorecard's `## Result` before there is a verdict.** `technical-debt-tracking:64`
  runs the scan, and so writes `POC-DEBT-SCORECARD.md` (Step 4), "At the conclusion of every PoC (before
  evaluation)". The scorecard's `## Result` (`poc-guidelines.md:111–112`) then has no verdict to copy yet.

## 14. Hand-back lists

### 14.1 Corrections to the brief (`unclear_requirements`, all `minor`)

1. **F3's quote is pre-T571.** The current text at `technical-debt-tracking:109` is "Do not **propose** a task; add to
   risk register with monitoring criteria", not "Do not create a task". The conflict survives in substance (§4).
2. **F2's range `:110–136` is too narrow.** The fence closes at `:137`, and `:139` ("… referenced in the next
   checkpoint summary") belongs to the same block. `:112` also carries a same-file defect ("When the verdict is
   `proceed`") that the brief does not list (§3, E3).
3. **F4's range `:129–130` is too narrow.** The group is `:128–131`. `:131` raises the same actor question, and `:129`
   also has F3's shape: the backlog can hold `monitor_only` items (§5).
4. **F6's range starts at the heading `:97`, not `:98`** (`:98` is blank). The brief also omits the most relevant
   corroboration: `poc-orchestrator.md:35` and `:92` already put the scaffold and integrate checkpoint with the
   orchestrator.
5. **F7's "§2.1".** The document has no §2.1 heading. The Rails convention is §2 item 1 (`:106`), which §3.1 itself
   cites as "§2.1". For skills, the operative clause is §3.4 item 2 (`:223–225`). That makes Rails an
   **`experimental → beta`** criterion, not only a `stable` one, and it defines skill-specific meanings for the
   three labels.
6. **The golden coupling is a subset check.** `expect.py:136–139` requires each of the eight `CHECKLIST` items to be
   present and allows extras. Extra checklist items in an output never fail the case. Items added to the command would
   go unchecked rather than fail. The brief's statement ("Any ruling that amends … its checklist changes that case")
   remains true, because the case's brief quotes the command verbatim.
7. **The facts were verified on `a0b0659`; this worktree is at `1208790`.** Every line I cite matches at `1208790`.
   That `a0b0659..1208790` touches only `docs/` is **(unverified)**.

### 14.2 Unverified claims (need a shell)

1. No golden case under `open/` reads the live source of the three skills. I relied on `poc-skills-alignment-v1.md`
   §10.1 #2, checked at `4ed6d91`. It needs a `grep` with `held-out` pruned before traversal.
2. `a0b0659..1208790` touches only `docs/`.
3. The number of root-projection paths (21, or 14 without E12).
4. Rails on `experimental` skills leaves the `check-maturity` baseline unchanged, and the script does not flag a
   component that meets the beta criteria while declared `experimental`.
5. No tool, CI step or test parses `[CHECKPOINT]` lines or `gate=poc-evaluation` markers. T572 §13.1 #3 covered
   `[VERDICT]` markers only.
6. Nothing outside `implementation/knowledge/` (wiki, README, docs) quotes the replaced lines of E3, E4, E5, E6, E9 or
   E10.
7. Whether O1 is already parked, for example under P33.
8. plan-095 §1's P34b trigger wording. I quoted it from `gate-verdict-consistency-v1.md` §1.1, not from plan-095.

### 14.3 Blockers

**None.** No P34b blocker exists (§10).

## 15. Summary

| Item | Ruling | Amendment | Basis |
|---|---|---|---|
| Authority | Joint satisfiability; one PoC, one outcome; self-description; `AGENTS.md` via the approved §10.2 basis; same-file coherence. ADR-007 fires nowhere; no rank. | — | §1 |
| F1 verdict shapes | Consistent: the marker accompanies the command's block, with the same values; V5's note is added | E2 | §1.2(i), (ii) |
| F2 checklists | Complementary: under `/evaluate-poc` the checklist is the union; `:112` trigger fixed | E3, E5, E7 | §1.2(i), (v) |
| F3 "promoted" vs `monitor_only` | Amend: inventory in the scorecard plus the ledger with a disposition; promotion moves to F4's flow | E4 | Scorecard Rule 1; `technical-debt-tracking` Steps 2 and 4; `:96` |
| F4 task creation | Consistent on the passive reading; clarifying amendment through the proposal → orchestrator flow | E6 | `AGENTS.md` § Task Protocol; `technical-debt-tracking:56, :101, :113–124` |
| F6 `[CHECKPOINT]` | Consistent: a status line reported to the orchestrator, not a checkpoint file; "publish" → "report" | E10, E11 | `AGENTS.md` § Checkpoint / § Task Protocol; `poc-orchestrator:35, :92` |
| F7 `## Rails` | Author now, for all three skills (judgement; E12 can be split out) | E1, E8, E12 | criteria-v2 §3.4 item 2 |
| F8 "🟡 Should Fix" | Consistent if the label grades the missing tag; clarified | E9 | `code-review:93–98`; `technical-debt-tracking` Step 3 |
| `/evaluate-poc` | Unchanged | — | ADR-007 branch 1 does not fire |
| Golden | No grant, no re-fixture, no v16 | — | the command is untouched |
| P34b blockers | None (O2 is a candidate outside scope) | — | §10 |

## 16. Orchestrator verification and rulings (added before commit, 2026-10-02)

*Added by the orchestrator, not the producing agent, on `develop` `1208790`. It settles the §14 unverified items
and decides FU-1's scope and the parking of §13. §§0–15 are unchanged.*

**16.1 Unverified claims, checked**

| # | Claim | Result |
|---|---|---|
| 1 | No golden case reads the live skill sources | Searched `tests/golden/` with `held-out` pruned before traversal. The only hit is the `/discover-skills` fixture, which checks the installed copies for **presence only** (verified in `poc-skills-alignment-v1.md` §10.1). **Confirmed.** No grant is needed. |
| 2 | `a0b0659..1208790` touches only `docs/` | The range touches only plan-097, `active-tasks.md` and `task-T574.md`. **Confirmed.** |
| 3 | Root-drift path count | 3 skills × 7 platforms = **21** (14 without E12). FU-1 must declare exactly what `--print-drift` reports, added to the 33 already declared. |
| 4 | `check-maturity` is unchanged by adding `## Rails` to experimental skills | Adding Rails raises no skill's claimed level, and `check-maturity` only checks claimed levels, so the baseline (79/0, skills 7/19) must hold. FU-1 must show that it does. |
| 5 | Nothing parses `[CHECKPOINT]` or `gate=poc-evaluation` | No hits in `scripts/`, `implementation/scripts`, `implementation/runtime`, or in tests outside `tests/golden/`. **Confirmed.** |
| 6 | Nothing outside `implementation/knowledge/` quotes the replaced lines | Only the skill, its generated projections (`implementation/.<platform>/` and the repo root), and two `docs/artifacts/` records that *quote* it as evidence. The records stay as written. **Confirmed.** |

**16.2 Rulings**

- **Accepted: E1–E12, including E12 and the editorial E5.** Every edit falls on an experimental skill. `/evaluate-poc`
  is untouched, so its golden case stays valid. **No v16 baseline is needed.** FU-1 is `T575`.
- **Accepted: F7, author `## Rails` now.** This is cheap, it is a beta criterion under §3.4 item 2, and it removes a
  known blocker before any promotion is attempted. No `maturity:` value changes.

**16.3 Parked**

- **P42 (O1, security — scheduled next, not merely parked):**
  - `poc-guidelines.md:82–85` (**stable**) and `rapid-prototyping:33–37` present "No input validation" and "disabled
    security" as model PoC shortcuts to tag. `security-guidelines.md` Immutable Constraints 3 and 4 forbid exactly
    that "even in development or PoC mode".
  - No P34b ranking is needed. `security-guidelines`' own Rails (`:19`) says it supersedes "any
    speed-over-completeness pressure from `poc-guidelines.md`", and `poc-guidelines`' Rails says it "Does not waive
    the Immutable Security Constraints".
  - The repo-root `.claude/rules/poc-guidelines.md` that this session loads carries the same example.
  - The next round scopes the fix. Whether it is P1, which would hold `poc-guidelines` below stable while open, is
    flagged to the user.
- **P43 (O2):** two binary verdicts for one PoC, from the prototyping `[CHECKPOINT]` and from the evaluation, with no
  text saying which counts. Joins **P40** as a P34b-dependent item.
- **P44 (O3, golden — protected path):** the `evaluate-poc` case's `expect.py:98–103` counts numbered backlog lines,
  while the skill's template renders the backlog as a table. Its `brief.md:54–55` says "when and only when" but
  checks only "when". Fixing either needs a grant and a user-authorized baseline. Batch this with the `new-poc`
  docstring fix.
- O4 and O5 join **P41**. O6 and O7 join **P33**.
