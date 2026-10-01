# Artifact: gate-verdict-consistency-v1.md

> Filename: `gate-verdict-consistency-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T572
- **Created**: 2026-10-01
- **Based on**: `docs/tasks/task-T572.md`; `docs/plans/plan-096-gate-definition-consistency.md`;
  `docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md` (§1 ADR-007 accepted and P34b's trigger; §2 P36);
  `docs/plans/plan-093-validate-workflow-repair.md` §4 (P37); `docs/artifacts/validate-workflow-gate-resolution-v1.md`
  §§1, 6, 9 (the model, and F1–F3); `docs/artifacts/poc-skills-alignment-v1.md` §§1, 4a, 10.2 (the model, the
  specialisation precedent and the working basis); `docs/artifacts/command-contract-resolution-v1.md` §3 C and §4
  (golden coupling of `/prepare-release` and `/code-review`); `docs/decisions/ADR-007-command-contract-authority.md`
  (Accepted); `AGENTS.md`.
- **Supersedes**: none (first version)
- **Decision references**: P36 (user decision, applied to V4). ADR-007 is **not applied**: no command clause is amended
  here. It is cited only for what it does not reach. The plan-095 §1 working basis (self-description; the T542/FU-C
  precedent extended to skills) is applied. No new ADR is minted.

## 0. What this document is, and what it did not do

This document rules on how the repository's gate-verdict formats and gate definitions reconcile: V2–V7 and F1–F3 of
brief §2. It specifies one follow-up task. **It changed no skill, command, agent, instruction or golden case.**

**Method and limits.** This session had **no shell**: no `grep`, `cmp`, directory listing, git or test run. Every claim
comes from reading named files directly on branch `agent/solution-architect/T572` (`24518f6`). Anything that would need
a search or a run is marked **(unverified)** and collected in §9.

**Files read (source, not projections):**
- skills `validation-gates`, `code-review`, `testing-strategy`, `project-planning`, `poc-evaluation`,
  `plan-approve-execute` and `release-workflow`, all in full;
- agents `tech-lead`, `orchestrator`, `qa-engineer`, `security-engineer` and `release-manager`, all in full;
- commands `prepare-release`, `code-review`, `security-audit` and `validate-workflow`, all in full;
- `AGENTS.md:1–75`; `implementation/registry/summary.md`;
- the planning and decision inputs listed above.

Under the brief's read-only grant I read `tests/golden/open/validate-workflow-gate-verdict-sources/{brief.md,expect.py}`
and nothing else under `tests/golden/`. I did not open `tests/golden/held-out/`.

**Line numbers in brief §2.** I checked every one against source at `24518f6`. All of them point at the text the brief
describes. §8 records where the cited range is too narrow and where the survey is incomplete.

## 1. Authority basis

### 1.1 What does not decide anything here

- **ADR-007** governs command contracts. Branch 1 says: "Does the clause contradict `AGENTS.md`, a `stable`
  instruction, or another clause of the same command file?" It does not rank a skill against a skill, or an agent
  against a skill (`validate-workflow-gate-resolution-v1.md` §1.2: "Branch 1 names a stable *instruction*, not a stable
  skill"). **None of the rulings below amends a command,** so ADR-007 fires nowhere.
- **Maturity is not rank.** `validation-gates` being `stable` does not make it outrank `code-review` or
  `testing-strategy`, which are also `stable`, or `tech-lead`, which is `experimental`. I do not rely on maturity
  anywhere.
- **P34b.** plan-095 §1 parks agent-definition authority as P34b, "with the trigger: a ruling that cannot rest on a
  file's own self-description". Every ruling below rests on (a) the files' own words, (b) a settled user decision, or
  (c) joint satisfiability. The last needs no rank by construction (§1.2). **No §2 item triggers P34b.** One finding
  outside scope would (§7, G1).

### 1.2 The basis I rely on: joint satisfiability, self-description, and one user decision

**(i) Two MUSTs that can both be obeyed do not conflict.** A ruling needs a rank only when two clauses cannot both be
satisfied. The clauses at issue are:

| Clause | Text (verbatim) | Exclusive? |
|---|---|---|
| `validation-gates:33` | "Every gate MUST produce a verdict in this format" | No. It says nothing like "only", "instead of" or "no other". |
| `code-review:114` | "Every review MUST conclude with a structured verdict that downstream gates (CI/CD, release) can consume" | No |
| `testing-strategy:221` | "The QA gate uses the same VERDICT protocol as code review" | No |
| `tech-lead:68` | "When completing a code review, issue a structured verdict" | No |
| `prepare-release:38` | "Produce a structured release gate VERDICT in the release notes document" | No |

None of them excludes another rendering. A reviewer can write the `## Gate Verdict` block **and** conclude with the
one-line marker. A release can store the gate block **and** publish `## RELEASE VERDICT` in its notes. So the one-line
markers and the extra blocks are **renderings that accompany the canonical block, not rival formats**, provided each
names a gate the canonical block can name. That proviso is (ii).

The precedent for "adds, does not compete" is `poc-skills-alignment-v1.md` §4a, approved in §10.2: "Extra sections are
a specialisation, not a rival … They add attributes without competing with any".

**One verdict per gate.** `validation-gates:11` reads: "Each gate produces a structured verdict (PASS,
CONDITIONAL_PASS, or FAIL)". That is singular, and `code-review:114` ("a structured verdict") is too. So the renderings
of one gate carry **one value**. This is what makes them summaries, not second opinions.

**(ii) The gate names map onto `validation-gates`' five kinds, in the files' own words.** `validation-gates` defines its
own reach by gate type. Its Rails, `:185`, read: "**Inputs**: A gate type
(architecture/implementation/integration/security/release), its designated executor agent, and that gate type's
required inputs". Its frontmatter `description` (`:3`) names the colloquial gates it covers: "Use when performing code
review gates, QA gates, security audits, or release readiness checks."

A name that maps onto one of the five is under the canonical format. A name that maps onto none is outside it. That is
the skill's own scope statement, not a rank. The mapping is in §2.

**(iii) Self-description where one file declares itself a summary of, or an input to, another.**
- `tech-lead:29–30`: "See skill `code-review` for the full structured checklist, feedback format, and VERDICT
  conventions this section summarizes."
- `project-planning:153`: "All plans produced by this skill feed into the **plan-approve-execute** protocol."
- `testing-strategy:14–18`, Rails: "Does not execute tests or produce the QA gate verdict itself — the agent executing
  the QA gate runs the strategy this skill defines and emits the actual `PASS`/`CONDITIONAL_PASS`/`FAIL` verdict against
  it. This skill defines the plan and thresholds a gate is judged against, not the judgment."
- `validation-gates:186`, Rails: "this skill defines the verdict process and format, not the review content itself."

**(iv) P36, a settled user decision.** plan-095 §2: "Plan approval is the user's Approve / Revise / Reject decision, not
a VERDICT-producing gate." Brief §2 directs me to treat it as settled.

**Corroboration, not the basis.** `AGENTS.md:67` (§ Skill Workflow) makes `validation-gates` the mandatory skill at
every "Phase or validation transition". The canonical block therefore cannot be dropped in favour of a marker, and
"accompanies, does not replace" is the only joint reading open. `AGENTS.md:52` fixes the verdict vocabulary that V1,
V2, V3, V6 and V7 all share.

### 1.3 What the reconciling reading costs, and its alternatives

- **The contestable part.** A code review now emits up to three renderings of one verdict: the `## Gate Verdict`
  block, the `tech-lead` block, and the one-line marker. The `/code-review` command adds a fourth (§7, G3). That is
  verbose. It is the honest result of obeying every MUST without ranking any of them.
- **Alternative A: collapse to one format.** Delete the markers, or replace the canonical block with them. This
  requires choosing which skill's format survives, which is a skill-against-skill (or agent-against-skill) rank and
  therefore P34b. **Not taken.**
- **Alternative B: relabel the markers to the five kinds** (`gate=code-review` → `gate=implementation`). Not compelled.
  `/validate-workflow` (`stable`), step 5 at `:24–29`, already treats "Code review gate" as a legitimate *name* for the
  **Implementation** *kind*, so the name and the kind coexist in a stable file today. A relabel would also change a
  marker grammar in two stable skills with no quoted authority behind it. **Not taken**, on the same minimal-change
  ground as `poc-skills-alignment-v1.md` §3 ("an edit with no authority behind it").

## 2. Gate-name mapping (adopted)

| Name used | Where | `validation-gates` kind | Basis (quoted) |
|---|---|---|---|
| `code-review`, "code review", "Code review gate" | V2 marker; V6; `/validate-workflow:26`; V7's "Quality gates passed" list | **implementation** | `validation-gates:26`: "**Implementation** \| Tech Lead \| After code complete, before merge"; `:3` "code review gates"; `/validate-workflow:26`: "Code review gate — `validation-gates` skill § Gate Types, **Implementation**"; `orchestrator.md:205–206`: "IMPLEMENTATION GATE … Delegate to `@tech-lead`: "Review implementation …"; `code-review:148`: "A `FAIL` verdict blocks the merge request"; `release-workflow:200`: "Implementation gate: **REQUIRED** (focused review of the fix)" |
| `qa-validation`, "QA gate", "QA validation gate" | V3 | **integration** | `testing-strategy:207`: "Test results are a critical input to the **integration validation gate**", the gate that `:214`'s "QA validation gate" then produces a verdict for; `validation-gates:27`: "**Integration** \| QA Agent \| After feature merge, before release"; `orchestrator.md:208–211`: INTEGRATION GATE → `@qa-engineer`, criteria "defined by skill `testing-strategy`"; `:3` "QA gates" |
| "release gate" (`## RELEASE VERDICT`) | V7 | **release** | `prepare-release:38`: "a structured release gate VERDICT"; `validation-gates:29` |
| `security-audit`, "Security audit gate" | V7's list; `/validate-workflow:28` | **security** | `/validate-workflow:28`; `:3` "security audits" |
| `test-coverage` | V7's list | **integration** (weaker) | Only via `testing-strategy:229–241`, where coverage thresholds "determine the QA gate verdict". No file states it outright. Informational; nothing is amended on it. |
| "Architecture review gate" | `/validate-workflow:25`; F3 | **architecture** | `/validate-workflow:25` |
| `plan-review` | V4 | **none: not a validation gate** | P36 (§4) |
| `poc-evaluation` | V5 | **none: PoC-track hypothesis verdict** | §5 |

The mapping lives here. The follow-up carries only the rows each file needs into that file (E1, E2, E6, E7).

## 3. V2, V3 and F1: the one-line markers in `code-review` and `testing-strategy`

### V2: `code-review:112–126`

| Field | Value |
|---|---|
| **Ruling** | **Consistent, with a specialisation note.** The marker accompanies the canonical block for the **implementation** gate. |
| **Why it is not a rival** | §1.2(i): both MUSTs are non-exclusive. §1.2(ii): `gate=code-review` names the Implementation kind (§2). The marker's stated role is downstream consumption ("that downstream gates (CI/CD, release) can consume", `:114`; "consumed by the CI/CD pipeline at the `approve` stage", `:146`; recorded "in the next checkpoint summary under `decisions=[...]`", `:151`). That is the role of a one-line summary, not of a replacement verdict document. |
| **Why a note at all** | The heading "VERDICT Format for Validation Gates" (`:112`) reads, standing alone, as *the* format of the gate. The note states the relationship where an agent applying this skill will see it. |
| **Amendment** | E1 (§10). |

### V3: `testing-strategy:205–229`

| Field | Value |
|---|---|
| **Ruling** | **Consistent, with a specialisation note.** The marker accompanies the canonical block for the **integration** gate. This skill supplies the thresholds; it does not supply a rival verdict document. |
| **Why** | §1.2(i) and (ii) as for V2. `testing-strategy:221`, "The QA gate uses the same VERDICT protocol as code review", carries V2's ruling across in this skill's own words. Its Rails (`:14–18`) say it "defines the plan and thresholds a gate is judged against, not the judgment". |
| **Amendment** | E2 (§10). |

### F1: "the integration gate has two formats, V1 and V3, and the orchestrator routes the integration criteria to `testing-strategy`"

| Field | Value |
|---|---|
| **Ruling** | **Resolved by V3; no further amendment.** There is one verdict, in the canonical block, with the marker as its one-line rendering. |
| **The routing is consistent** | `orchestrator.md:210–211` routes "The coverage thresholds and `PASS`/`CONDITIONAL_PASS`/`FAIL` *criteria*" to `testing-strategy`, not the *format*. That matches both skills' self-descriptions: `testing-strategy` Rails ("thresholds a gate is judged against") and `validation-gates:186` ("defines the verdict process and format, not the review content itself"). `orchestrator.md` needs no edit for F1. |
| **Left open** | Whether `validation-gates`' generic Verdict Rules (`:62–68`, severity-based) always yield the same value as `testing-strategy`'s coverage thresholds (`:229–241`). This is a *criteria* question, not a format question. It is G1 (§7). |

## 4. V4: `project-planning` against P36

| Field | Value |
|---|---|
| **Ruling** | **Amend.** "Approval is a validation gate that produces a verdict" (`:156`) and everything that depends on it are contradicted by P36. |
| **Authority (quoted)** | (1) **P36**, plan-095 §2: "Plan approval is the user's Approve / Revise / Reject decision, not a VERDICT-producing gate." (2) **Self-description**: `project-planning:153`, "All plans produced by this skill feed into the **plan-approve-execute** protocol." That protocol's Phase 2 is "Approve / Revise / Reject" (`plan-approve-execute:99–111`), with no verdict. The skill's own summary of the protocol it names is the defective part. (3) Corroboration: `/validate-workflow:31` (stable): "Plan approval (… a user decision: Approve / Revise / Reject) … are workflow steps, not validation gates"; `orchestrator.md:30`: "You can approve, modify, or reject." Also §2: `plan-review` maps to none of `validation-gates`' five kinds (`:185`). |
| **Not re-decided** | P36 itself. The vocabulary is the one P36's own sentence uses (Approve / Revise / Reject). P10, `/new-project`'s rival approval vocabulary, is **not** touched and stays parked. |
| **Reach of the contradiction** | Wider than brief §2's `:156–159`: `:160` ("Only after a `PASS` or `CONDITIONAL_PASS` verdict"), `:162` ("rejected (`FAIL`)"), the plan template's `## Status` (`:179`, no `rejected` value) and `## Approval` (`:199–202`, Reviewer / Verdict / Conditions). |
| **Amendment** | E3, E4 and E5 (§10). |

## 5. V5: `poc-evaluation:31–37`

| Field | Value |
|---|---|
| **Ruling** | **Consistent; no amendment.** The marker is outside `validation-gates`' reach. |
| **Why** | (1) `validation-gates:185` scopes the skill to five gate types. PoC evaluation is none of them (§2). (2) The skill's own words claim a shape, not membership: "a structured verdict that **integrates with** the gate protocol" (`:33`). It does not say it *is* a validation gate, unlike `code-review:114`. (3) Its values (`VALIDATED\|INVALIDATED`) are the PoC track's binary outcome under `poc-guidelines.md` Rule 4, through the working basis approved in `poc-skills-alignment-v1.md` §10.2 and kept by plan-095 §1. They are not `AGENTS.md:52`'s gate vocabulary, and could not be. |
| **Why no clarifying note** | A note ("not one of the five gate types") would be harmless. But any edit to `poc-evaluation` fires P38's trigger ("the next task touching `poc-evaluation` …", `poc-skills-alignment-v1.md` §10.3). The overlap with `/evaluate-poc`'s `## POC VERDICT` already belongs to P38 (brief §2). **Defer any note to P38.** |

## 6. V6, V7, F2 and F3

### V6: `tech-lead:66–100`, the `## VERDICT:` block

| Field | Value |
|---|---|
| **Ruling (format)** | **Consistent, with a specialisation note.** The block is the Tech Lead's merge-authorization record for the **implementation** gate. It accompanies the canonical block and the `code-review` marker. |
| **Authority** | Self-description, `tech-lead:29–30`: "See skill `code-review` for the full structured checklist, feedback format, and VERDICT conventions this section summarizes." Under V2, those conventions are "the canonical block, concluded by the marker". The block's extra fields are ones this role requires in its own text: `:17` ("Ensure code review outcomes reference decision IDs"), `:112` ("Ensure every merge approval cites artifact versions and decision IDs"). That makes them additions, not rivals (§1.2(i)). |
| **Honest weakness** | "this section" literally heads `### Code Review` (`:28–41`), and the verdict format is the sibling `### Review Verdict Format` (`:66`). But lines 28–41 contain no feedback format and no VERDICT, so the feedback format and VERDICT conventions that "this section summarizes" can only be the material at `:43–100`. I read the sentence that way. If the reviewer rejects that reading, the ruling falls back on §1.2(i) alone (joint satisfiability), which reaches the same result. |
| **Not ruled: CONDITIONAL_PASS semantics** | `tech-lead:97` says CONDITIONAL_PASS means "Merge is blocked until conditions are resolved". `code-review:149`, `validation-gates:67, 131–132`, `AGENTS.md:55` and `orchestrator.md:221` all say CONDITIONAL_PASS proceeds with conditions tracked. The `/code-review` command (`:51`, "conditions that must be met before merge") sides with `tech-lead`. That is a real contradiction. It concerns verdict *meaning*, not format, and it involves a golden-covered command (`command-contract-resolution-v1.md` §4 lists `/code-review` among the covered commands with an open defect). This task's grant cannot see that coupling. **Reported as G2 (§7), not ruled.** The E6 note says nothing about it either way. |
| **Amendment** | E6 (§10). |

### V7: `prepare-release:36–58`, `## RELEASE VERDICT`

| Field | Value |
|---|---|
| **Ruling** | **Consistent; no amendment.** The release-notes section is the release gate's published rendering. `validation-gates:120` ("Store the verdict in `docs/artifacts/gate-<type>-<target>-<date>.md`") still requires the canonical block, independently. Both can be produced (§1.2(i)). |
| **Why no note, unlike V2/V3** | (1) ADR-007 governs this command, and no branch fires: the clause contradicts neither `AGENTS.md`, nor a stable *instruction*, nor itself. A sentence obliging the command to also emit the `validation-gates` block would *add* to its contract with no ADR-007 basis. (2) The block is golden-coupled. `command-contract-resolution-v1.md` §3 C keeps its 11 fields as a branch-3b standing red, whose exit is ADR-007 Validation 5: "The next real release emits a conforming release verdict". Editing the clause during that exit is avoidable risk. |
| **Not ruled** | The executor. `prepare-release:56` fixes "**Release manager**: orchestrator", while `validation-gates:29` names Release Manager and `orchestrator.md:216–217` delegates the RELEASE GATE to `@release-manager`. That is G4 (§7). |

### F2: the orchestrator's Core Workflow never names the Implementation Gate

| Field | Value |
|---|---|
| **Ruling** | **Consistent in substance; one naming amendment for same-file coherence.** |
| **Why consistent** | `/validate-workflow:24` places "the orchestrator's invocation points" in "§ Validation Gates". There the gate is defined and invoked: "**IMPLEMENTATION GATE** … Delegate to `@tech-lead`: "Review implementation against architecture-v1.md. Produce VERDICT."" (`orchestrator.md:205–206`). Under §2, Phase 3 step 3 (`:249`, "delegate to **@tech-lead** for code review") *is* that invocation. Its timing, "After each completion", also matches `validation-gates:26`'s trigger, "After code complete, before merge". |
| **Why amend anyway** | The Core Workflow names the other four gates as "Run **… Gate**" (`:234`, `:250`, `:255`, `:261`). Leaving the fifth unnamed is what made T566 §6 F2 fear a strict reachability reading. The edit names the gate and changes no behaviour. The basis is the file's own pattern. No rank is involved. |
| **Not amended** | `:205`'s "(after core implementation)" is looser than "after each completion", but not contradictory: the gate has run for every item once core implementation is complete. Noted only (G9). |
| **Amendment** | E7 (§10). |

### F3: Architecture gate executor: Tech Lead (`validation-gates:25`) vs Tech Lead + Security Engineer (`orchestrator.md:201–203`)

| Field | Value |
|---|---|
| **Ruling** | **Consistent (specialisation); no amendment.** |
| **Why** | The orchestrator keeps the skill's executor (`@tech-lead`, "Review architecture-v1.md against requirements-v1.md. Produce VERDICT.") and adds a second reviewer. Nothing in `validation-gates` makes the executor exclusive, and `:180` requires cross-agent review ("Cross-agent review is mandatory"). The canonical `**Executor:**` field is single-valued (`:39`), so the Security Engineer's review is a second canonical block with `**Gate:** architecture` and `**Executor:** security-engineer`. The orchestrator's "Process verdicts" rules (`:219–222`) apply to each block, so a `FAIL` from either blocks progression. That follows from the text as written and needs no edit. |
| **Rejected alternative** | Add Security Engineer to `validation-gates:25`. That edits the stable skill and the golden case's frozen source, for a combination the orchestrator already expresses. Not compelled. |

### V1: `validation-gates`

**Unchanged.** Nothing in it is defective, and every ruling above reconciles *to* it without ranking it. This is the
reason no golden re-fixturing follows (§8).

## 7. Findings outside scope (not decided; candidates for parking)

- **G1: verdict *criteria* diverge across gate documents.** This is a P34b candidate if it ever has to be ruled.
  - `validation-gates` (`:62–77`): four severity tiers; `PASS` = no critical or high findings.
  - `code-review` (`:93–99`, `:122–126`): Must / Should / Nice; `PASS` = no must-fix findings, and any should-fix
    finding gives `CONDITIONAL_PASS`.
  - `testing-strategy` (`:229–241`): coverage thresholds.
  - `qa-engineer` (`:116–120`): `conditional_pass` = "Only medium/low issues".
  - `security-engineer` (`:152`): `fail` on any unresolved high finding. This one is backed by `security-guidelines.md`
    (stable instruction): "`CRITICAL` and `HIGH` findings block merge".

  These can give different values for the same findings. Two examples: a lone maintainability concern is
  `validation-gates` PASS (a medium finding) but `code-review` CONDITIONAL_PASS (should-fix). A mitigated high finding
  is `validation-gates` CONDITIONAL_PASS but `security-engineer` FAIL. The rulings above fix the *format* and say the
  renderings carry one value. They do not say whose criteria compute that value. Ruling that would rank stable skills
  against each other and against stable agents. The security case alone may rest on the stable instruction.
- **G2: CONDITIONAL_PASS at the implementation gate: merge allowed or blocked?**
  - **Blocked:** `tech-lead:82, :90, :97`; `/code-review:51`.
  - **Proceeds:** `code-review:125, :149`; `validation-gates:67, :131–132`; `AGENTS.md:55`; `orchestrator.md:44, :221`.

  The agent side looks rulable on its own self-description (`tech-lead:29–30`) plus `AGENTS.md:55`. But `/code-review`
  must move with it, or the agent will contradict the command it executes. That command's golden coverage (open and
  possibly held-out) is outside this task's grant. **Recommend a separate ADR-007 adjudication, with a held-out read
  grant.**
- **G3: brief §2's survey is incomplete.** Further verdict renderings I read:
  - `qa-engineer` (stable): `## VERDICT:` in the Structured Test Report (`:163–172`), plus lowercase `pass` /
    `conditional_pass` / `fail` (`:114–115`).
  - `security-engineer` (stable): `## VERDICT:` (`:158–195`), plus lowercase tokens (`:151`).
  - `release-manager` (stable): `## RELEASE VERDICT: [..]` (`:159–189`). This is the same heading text as V7 with a
    different shape.
  - `/code-review` (experimental, `agent: tech-lead`): `## VERDICT` with `- **Status**:` (`:36–49`).
  - `/security-audit` (stable): `## VERDICT` with `- **Status**:` (`:50–64`).
  - `release-workflow` (experimental): `## Gate Verdicts` in release notes (`:149–154`).

  §1.2's reading extends to all of them: each maps onto a single kind and none excludes the canonical block. They are
  **not ruled here**, because they are not in §2. Two of them are golden-covered commands, so a follow-up would have to
  check coupling first.
- **G4: release gate executor.** `/prepare-release` (`agent: "orchestrator"`, `:56` "Release manager: orchestrator")
  conflicts with `validation-gates:29` (Release Manager) and with `orchestrator.md:216–217` (delegates to
  `@release-manager`). `validation-gates:180` adds "Gate executors should not review their own work", and the
  orchestrator both prepares the release and issues its verdict. This is command against skill and agent, so ADR-007
  is silent on it. The field is one of the 11 the release golden cases check.
- **G5: two release-notes paths.** `release-workflow:56, :160` use `docs/artifacts/release-notes-v<VERSION>.md`;
  `prepare-release:39` uses `docs/releases/v<version>.md`. This is the same shape as the P32 path family.
- **G6: a second "verdict" vocabulary inside the same files.** `code-review:71` has "`### Verdict: [Approved | Changes
  Requested | Needs Discussion]`" and `tech-lead:47` has "`### Status: [Approved | …]`", each next to the
  `PASS`/`CONDITIONAL_PASS`/`FAIL` verdict. "Needs Discussion" has no counterpart in that vocabulary. This is a
  same-file issue that is rulable without rank, but it is not in §2.
- **G7: other `project-planning` defects, untouched by E3–E5.** They have the same shape as
  `poc-skills-alignment-v1.md` §4d:
  - the `### T{ID}` task block and `Priority: must | should | could` (`:211–222`), against `AGENTS.md` § Task Protocol;
  - the lifecycle `pending → in-progress → review → done` (`:229`), against `AGENTS.md:10`;
  - the plan path `docs/plans/project-plan-v{N}.md` (`:169–170`), part of the P32 family.
- **G8: token case.** Lowercase `pass` / `conditional_pass` / `fail` appears in `qa-engineer`, `security-engineer`,
  `/code-review:22` and `/validate-workflow:41`. Following `poc-skills-alignment-v1.md` §3, no quoted authority makes
  case normative. Noted only.
- **G9: timing wording.** `orchestrator.md:205`'s "(after core implementation)" against `:249` and
  `validation-gates:26`. I read these as compatible (§6, F2). Noted only.

## 8. Golden coupling and blast radius

**The `/validate-workflow` case.** `expect.py` reads its fixture copy of `validation-gates`: the § Gate Types rows
(`_select`, `row:<Kind>`), the § Verdict Format sentence "every gate must produce a verdict" and the `**Gate:**` field
(`_verdict_gate_kinds`). It also reads the fixture copy of `commands/validate-workflow.md` step 5. **No follow-up
below edits either file.** The fixture copies stay byte-identical to source, and the case brief's Provenance statement
stays true. **No re-fixturing, no protected-path grant and no baseline bump are needed.** That the fixture is still
byte-identical at `24518f6` is **(unverified)**: T568 confirmed it at `a6be6b0`.

**Files the follow-up edits.** None is under `tests/golden/**`.

| File | Edits | Maturity | Golden reads it? |
|---|---|---|---|
| `implementation/knowledge/skills/code-review/SKILL.md` | E1 | stable | not as a verdict definition (brief §2); any other read **(unverified)** |
| `implementation/knowledge/skills/testing-strategy/SKILL.md` | E2 | stable | same |
| `implementation/knowledge/skills/project-planning/SKILL.md` | E3–E5 | experimental | same |
| `implementation/knowledge/agents/tech-lead.md` | E6 | experimental | same |
| `implementation/knowledge/agents/orchestrator.md` | E7 | experimental | no longer in the `/validate-workflow` fixture (T568 removed it); other cases **(unverified)** |

**Generated outputs (mechanical, not content):**
- the `implementation/.<platform>/` mirrors, via `node implementation/scripts/sync.mjs --root implementation`;
- `implementation/registry/index.json` checksums, via `python3 implementation/scripts/generate-registry.py`. Confirm
  both with `--check`.
- repo-root projections of all five files. Per plan-095 §3, "every knowledge change again declares its root paths, or
  refreshes the root, in the same MR". Declare exactly what `--print-drift` reports in
  `tests/_baselines/root-install-drift.json`. The count is **(unverified)**: up to 5 × 7. Do not hand-edit the root
  folders.

**Parked triggers.**
- **Fires:** P37 itself (this task).
- **Does not fire:**
  - P32 (`/new-feature`, `/plan`);
  - P33 (`poc-guidelines.md`);
  - P38 (`poc-evaluation`, `rapid-prototyping`, `/evaluate-poc`). V5 is deliberately left unedited for this reason.

**Commands.** None is edited, so ADR-007 Validation 2 and 4 are unaffected.

## 9. Hand-back lists

### 9.1 Corrections to the brief (`unclear_requirements`)

1. **(major) §2's table, and plan-096 §1's "seven places", undercount.** At least six more verdict renderings exist
   (§7, G3), three of them in `stable` agents. The rulings here cover §2's items. P37 is not exhausted until G3 is
   scoped.
2. **(minor) V4's range `:156–159` is too narrow.** The contradiction reaches `:160`, `:162`, `:179` and `:199–202`
   (§4).
3. **(minor) V6's "Gate name —".** It is derivable: `tech-lead:29–30` ties the block to `code-review`, which is the
   implementation gate. The row also omits the CONDITIONAL_PASS contradiction (G2).
4. **(minor) V7 omits the executor conflict** (`:56`, "Release manager: orchestrator"; G4).
5. **(minor) "Settled decisions" omits plan-095 §1's working basis and P34b's trigger**: "a ruling that cannot rest on
   a file's own self-description". That trigger is what lets every §2 item be ruled here without escalation.
6. **(minor) The §2 facts were verified on `18681b3`; this worktree is at `24518f6`.** Every line I cite matches at
   `24518f6`. That the intervening commits (`bf912f5` and its merge) touched only `docs/` is **(unverified)**.

### 9.2 Unverified claims (need a shell)

1. No golden case in `open/` reads any of the five files FU-1 edits. The brief's claim covers only reads "as a verdict
   definition". Needs a `grep` with `held-out` pruned before traversal (plan-093 §5).
2. The `/validate-workflow` fixture copy of `validation-gates` is still byte-identical to source at `24518f6`.
3. No tool or CI step parses `[VERDICT]` markers. This is the brief's claim; I did not search.
4. Nothing outside `implementation/knowledge/` (docs, wiki, README) quotes `gate=plan-review` or "Approval is a
   validation gate".
5. The root-projection path count for FU-1.
6. G3 is complete. I did not read `poc-qa-engineer`, `poc-security-engineer`, `evaluation-agent`, `ci-cd-pipeline`,
   `checkpoint-protocol`, `/new-project`, `/new-feature` or `/batch`.
7. A P2 task that edits two `stable` skills has no maturity consequence under `check-maturity.py`. plan-092 §3 suggests
   so; I have not checked it for skills.
8. `18681b3..24518f6` touches only `docs/`.

### 9.3 Blockers

**None.** No §2 item requires a rank, so there is no P34b blocker. G1 is a P34b *candidate* outside scope.

## 10. Exact amendments (follow-up FU-1)

Each edit is matched by its exact **before** text, and each before text is unique in its file. Line numbers refer to
source at `24518f6`, before any edit. `—` is U+2014 wherever it appears. Fences inside before/after blocks are literal
three-backtick fences.

### E1: `code-review/SKILL.md:117–120` (V2): insert one paragraph

````
Before:
[VERDICT] gate=code-review | result=PASS|CONDITIONAL_PASS|FAIL | reviewer={role} | artifact_ref={artifact-version} | date={YYYY-MM-DD}
```

**Verdict definitions:**

After:
[VERDICT] gate=code-review | result=PASS|CONDITIONAL_PASS|FAIL | reviewer={role} | artifact_ref={artifact-version} | date={YYYY-MM-DD}
```

Code review is the `validation-gates` skill's **Implementation** gate (§ Gate Types: Tech Lead, after code complete, before merge). This line accompanies, and does not replace, the `## Gate Verdict` block that skill's § Verdict Format requires of every gate, with `**Gate:** implementation`. Both record the gate's one verdict, so `result=` carries the same value as the block's `### Verdict:`.

**Verdict definitions:**
````

### E2: `testing-strategy/SKILL.md:216–219` (V3, F1): insert one paragraph

````
Before:
[VERDICT] gate=qa-validation | result=PASS|CONDITIONAL_PASS|FAIL | coverage={N}% | failed_tests={count} | critical_failures={count} | artifact_ref=test-plan-v{N} | date={YYYY-MM-DD}
```

### VERDICT Format for QA Gate

After:
[VERDICT] gate=qa-validation | result=PASS|CONDITIONAL_PASS|FAIL | coverage={N}% | failed_tests={count} | critical_failures={count} | artifact_ref=test-plan-v{N} | date={YYYY-MM-DD}
```

The QA validation gate is the integration validation gate named above: the `validation-gates` skill's **Integration** gate (§ Gate Types: QA Agent, after feature merge, before release). As with code review, this line accompanies, and does not replace, the `## Gate Verdict` block that skill's § Verdict Format requires of every gate, with `**Gate:** integration`, and `result=` carries the same value as the block's `### Verdict:`. This skill supplies the thresholds that verdict is judged against (§ Coverage Thresholds That Determine Gate Outcome).

### VERDICT Format for QA Gate
````

### E3: `project-planning/SKILL.md:156–162` (V4)

````
Before:
2. **Approve** — The plan is submitted for review. Approval is a validation gate that produces a verdict:
   ```
   [VERDICT] gate=plan-review | result=PASS|CONDITIONAL_PASS|FAIL | reviewer={role} | artifact_ref=plan-v{N} | date={YYYY-MM-DD}
   ```
3. **Execute** — Only after a `PASS` or `CONDITIONAL_PASS` verdict does execution begin. `CONDITIONAL_PASS` items become tracked tasks.

**No work begins without an approved plan.** If a plan is rejected (`FAIL`), it must be revised and resubmitted.

After:
2. **Approve** — The plan is presented to the user, who decides **Approve**, **Revise** or **Reject** (`plan-approve-execute` skill § The Three Phases › Phase 2: Approve). Plan approval is the user's decision, not a validation gate: it produces no `PASS` / `CONDITIONAL_PASS` / `FAIL` verdict.
3. **Execute** — Only after the user approves does execution begin.

**No work begins without an approved plan.** If the user chooses Revise, update the plan per the feedback and re-present it for approval. If the user chooses Reject, set the plan's status to `rejected` and discuss alternative approaches.
````

**Authority:** P36; `:153` (self-description); `plan-approve-execute:99–111`, whose Handling Responses wording E3
mirrors ("Update plan per feedback, re-present for approval"; "Update plan status to `rejected`, discuss alternative
approaches"). Lines `:151–155` are unchanged.

### E4: `project-planning/SKILL.md:179` (consequential on E3)

````
Before:
## Status: draft | approved | superseded

After:
## Status: draft | approved | rejected | superseded
````

**Authority:** same-file coherence with E3's `rejected`. The value set copies `plan-approve-execute:39`.

### E5: `project-planning/SKILL.md:199–202` (consequential on E3)

````
Before:
## Approval
- Reviewer: {role}
- Verdict: PASS | CONDITIONAL_PASS | FAIL
- Conditions (if CONDITIONAL_PASS): [list]

After:
## Approval
- Decided by: user
- Decision: Approve | Revise | Reject
- Changes requested (if Revise): [list]
````

**Authority:** P36. The third line carries `plan-approve-execute:101` ("**Revise** — specify changes needed") into the
slot the removed Conditions line held. The field count is unchanged.

### E6: `tech-lead.md:66–68` (V6)

````
Before:
### Review Verdict Format

When completing a code review, issue a structured verdict:

After:
### Review Verdict Format

When completing a code review, issue a structured verdict. A code review is the `validation-gates` skill's **Implementation** gate, so this block accompanies, and does not replace, that skill's `## Gate Verdict` block (`**Gate:** implementation`) and the concluding `[VERDICT] gate=code-review` line of skill `code-review` (§ VERDICT Format for Validation Gates). All three record the same verdict. This block adds the artifact, decision-ID and merge-authorization fields this role requires (§ State and Handoff Protocol, § Merge and Architecture Authority):
````

**Unchanged:** `:70–100`, including the CONDITIONAL_PASS definition at `:97` (G2 is not ruled).

### E7: `orchestrator.md:249` (F2)

````
Before:
3. After each completion, delegate to **@tech-lead** for code review

After:
3. After each completion, run the **Implementation Gate**: delegate to **@tech-lead** for code review (see § Validation Gates)
````

**Unchanged:** `:197–222` (§ Validation Gates, including F3's two Architecture delegations) and every other line.

## 11. Follow-up tasks

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / notes |
|---|---|---|---|---|---|---|
| **FU-1**: apply the gate-verdict consistency edits | E1–E7 | `implementation/knowledge/skills/{code-review,testing-strategy,project-planning}/SKILL.md`; `implementation/knowledge/agents/{tech-lead,orchestrator}.md`; regenerated `implementation/.<platform>/` mirrors; `implementation/registry/index.json` via the generator; root-drift declarations in `tests/_baselines/root-install-drift.json` | **No** | Backend Developer (the owner class of T564/T567/T571) | P2 (plan-096 §2) | **Before dispatch:** the orchestrator settles §9.2 items 1 and 7. **Verify:** each before text matched exactly once; `sync.mjs --check` and `generate-registry.py --check` clean; the root parity gate is green; `gate=plan-review` and "Approval is a validation gate" have 0 hits under `implementation/knowledge/`; `validation-gates/SKILL.md` and `commands/validate-workflow.md` are byte-unchanged (`git diff --stat`). |

**There is no golden follow-up.** Re-fixturing the `/validate-workflow` case is not needed, because `validation-gates`
does not change.

**Candidates for parking** (the orchestrator decides):
- G1 as a P34b dependency;
- G2 as an ADR-007 adjudication needing a held-out read grant;
- G3 as "P37b: remaining verdict renderings";
- G4 and G5 together with the release-verdict exit (ADR-007 Validation 5);
- G6, G7, G8 and G9 as editorial items.

## 12. Summary

| Item | Ruling | Amendment | Basis |
|---|---|---|---|
| V1 `validation-gates` | Canonical; unchanged | — | Nothing defective |
| V2 `code-review` marker | Consistent: accompanies the block; `code-review` → implementation | E1 (note) | §1.2(i), (ii); `/validate-workflow:26` |
| V3 `testing-strategy` marker | Consistent: accompanies the block; `qa-validation` → integration | E2 (note) | §1.2(i), (ii); `:207`, `:221`; Rails |
| V4 `project-planning` | Contradicts P36 | E3–E5 | P36; `:153` self-description |
| V5 `poc-evaluation` | Consistent: outside `validation-gates`' reach | none (defer to P38) | `validation-gates:185`; "integrates with" |
| V6 `tech-lead` block | Consistent: merge-authorization rendering for implementation | E6 (note) | `tech-lead:29–30` self-description; §1.2(i) |
| V7 `/prepare-release` | Consistent: published rendering for release | none | §1.2(i); ADR-007 gives no basis to add; golden-coupled |
| F1 | Resolved by V3; the routing is criteria, not format | none beyond E2 | Rails of both skills; `orchestrator.md:210–211` |
| F2 | Consistent in substance | E7 (naming) | Same-file pattern `:234/250/255/261` |
| F3 | Specialisation (an added reviewer) | none | `validation-gates:180`; non-exclusive executor |
| P34b blockers | None | — | — |
| Golden | No re-fixture, no grant, no baseline | — | `validation-gates` and `validate-workflow` untouched |

## 13. Orchestrator verification and rulings (added before commit, 2026-10-01)

*The orchestrator added this section, not the producing agent. It was written on `develop` `24518f6`. It settles
the §9.2 items that FU-1's dispatch depends on and decides how the §7 and §11 candidates are parked. §§0–12 are
unchanged.*

**13.1 §9.2 claims, checked**

| # | Claim | Result |
|---|---|---|
| 1 | No golden case reads the five FU-1 files | A search of `tests/golden/` (with `held-out` pruned before traversal) found 2 cases that mention them. In `validate-workflow-gate-verdict-sources` the mention is `brief.md` prose (its `expect.py` reads only the fixture copies of the command and `validation-gates`). In `discover-skills-registry-grounded-recommendation` it is a frozen registry copy inside its fixture. **Neither reads the live files. Confirmed.** |
| 2 | The fixture copy of `validation-gates` is identical to source | `cmp`: identical at `24518f6`. **Confirmed.** FU-1 leaves `validation-gates` alone, so it stays identical. |
| 3 | No tool parses `[VERDICT]` markers | Confirmed when the task was scoped: no hits in `scripts/`, `implementation/scripts`, `implementation/runtime`, CI, or tests outside `tests/golden/`. |
| 4 | Nothing outside `implementation/knowledge/` quotes `gate=plan-review` | The only hits are `project-planning` and its generated projections (under `implementation/.<platform>/` and the repo root). **Confirmed.** FU-1 must declare the root projections as drift. |
| 7 | Editing two stable skills in a P2 task does not affect maturity | `check-maturity` counts only P0/P1 active rows (`DECLARED_PRIORITIES`), and E1/E2 are additive notes that remove no evidence tag or reference. Today's baseline: 79 components, 0 failing, skills 7 stable / 19 experimental. FU-1 must show the same. |
| 8 | `18681b3..24518f6` touches only `docs/` | Only plan-096, `active-tasks.md` and `task-T572.md` changed. **Confirmed.** |
| §9.1 #1 | Six more verdict formats exist | **Confirmed:** `commands/code-review.md:39`, `commands/security-audit.md:53`, `agents/qa-engineer.md:163`, `agents/security-engineer.md:163`, `agents/release-manager.md:164` and `skills/release-workflow/SKILL.md:149`. Plan-096's "seven places" undercounted. These are parked as part of P41. |

**13.2 Rulings**

- **Accepted: E1–E7 as specified**, together with the gate-name mapping in §2. They add notes and amend V4 toward the
  user's P36 decision. They neither rank documents nor touch `validation-gates` or `/validate-workflow`. FU-1
  (`T573`) may be dispatched.
- **Accepted: V5 and V7 left unchanged.** V5 is deferred to P38. V7 is unchanged because ADR-007 gives no basis for
  adding to its contract, and its golden case is still waiting for a real release.

**13.3 Parked**

- **P39 (G2):** do the documents agree on whether CONDITIONAL_PASS allows a merge? `tech-lead:97` and
  `/code-review:51` say merging is blocked. `code-review:149`, `validation-gates:67`, `AGENTS.md:55` and the
  orchestrator say work proceeds. This is a **behavioural** conflict, so it is the most consequential item here.
  `/code-review` is a command, so ADR-007 applies, but it has golden coverage that a grant would have to make
  visible. **Any task that needs to read `tests/golden/held-out/` needs explicit user approval** (see the T568
  incident). **Trigger:** the next round; flagged to the user.
- **P40 (G1):** the verdict *criteria* differ (severity rules across stable skills and agents). Resolving this needs
  a ranking, so it **depends on P34b**. **Trigger:** a P34b decision.
- **P41 (G3–G9):** the remaining verdict renderings (§13.1), the `/prepare-release` executor and the release-notes
  path (G4, G5), second verdict vocabularies (G6), `project-planning`'s task block (G7; its plan path joins P32),
  lowercase verdict tokens (G8), and the wording of `orchestrator:205` (G9). These are editorial. **Trigger:** the
  next task touching any of these files.
