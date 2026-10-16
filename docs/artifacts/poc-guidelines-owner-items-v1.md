# Artifact: poc-guidelines-owner-items-v1.md

> Filename: `poc-guidelines-owner-items-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T598
- **Created**: 2026-10-08
- **Based on**: `docs/tasks/task-T598.md`; `docs/plans/plan-110-poc-guidelines-owner-items.md`;
  `docs/artifacts/poc-contract-resolution-v1.md` §§3a–3c, 5, 7.4, 9 (P11, P29, P30, P31);
  `docs/artifacts/poc-skills-alignment-v1.md` §§4a–4c, 7 (F5), 10 (T570);
  `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted; applied, not amended);
  `docs/decisions/ADR-007-command-contract-authority.md` (Accepted); `implementation/AGENTS.md`.
  Earlier rulings taken as inputs: P11, P29, P30, P31 (T563), P35 (T570), P38 (T574), P42 (T576/T577), O1 (T578/T579),
  and the user's ADR-008 review decision Q1, "Self-placement only".
- **User instruction**: 2026-10-08, "continue"; the recommended item was P33.
- **Supersedes**: none (first version)
- **Decision references**: ADR-008 Steps A–E; ADR-007 branch 1 (cited only through earlier rulings). No ADR is minted.

## 0. What this document is, and what it did not do

This is a decision record for the four P33 subjects, (a) to (d). It changed no knowledge file, command, agent,
instruction, skill or golden case. It writes one file, this one, and sets the brief's `**Status:**` line.

`implementation/knowledge/instructions/poc-guidelines.md` is a **stable instruction** (frontmatter `:4`
`maturity: stable`), so it is tier 1 (ADR-008 D1). ADR-008 § Consequences lists "any change to a tier-1 document's own
text" as "Still not routine". Every candidate edit to `poc-guidelines.md` below is therefore **held** as an option in a
user question (§4), never applied on ADR-008's authority.

**Method and limits.** No shell: no `grep`, no listing, no `git`, no test run. Every claim comes from reading named
files in the worktree `/home/emage/Code/emage/worktrees/agent-solution-architect-T598`, which the orchestrator states is
`develop` `7685de0`. I could not confirm the hash myself **(unverified)**. Every quoted line was re-read in that
worktree; line numbers refer to it. Omissions inside quotes are marked "…". A line joined from a hard-wrapped source
paragraph is marked "(joined)".

**Files read in full (source, not projections):**
- instruction: `poc-guidelines.md`;
- commands: `new-poc.md`, `poc-demo.md`, `evaluate-poc.md`;
- agents: `poc-orchestrator.md`, `technical-debt-narrator.md`, `evaluation-agent.md`, `scaffolding-agent.md`,
  `poc-technical-writer.md`, `poc-devops-engineer.md`, `demo-agent.md`, `integration-agent.md`,
  `data-mockup-agent.md`, `poc-qa-engineer.md`, `poc-security-engineer.md`, `feasibility-agent.md`,
  `technology-scout.md`;
- skills: `technical-debt-tracking`, `poc-evaluation`, `rapid-prototyping`, `technology-scouting`;
- `implementation/AGENTS.md`; `implementation/registry/summary.md`;
- golden (open only, by path): `brief.md` and `expect.py` of `evaluate-poc-verdict-debt-reconciliation`,
  `new-poc-plan-hypothesis-format`, `poc-demo-hypothesis-status-evidence-gaps`; lines 1–12 of
  `new-feature-plan-doc-compliant/expect.py` (existence only);
- `tests/functional/test_golden_harness_scoring.py`;
- the planning and decision inputs above, plus `docs/plans/plan-092-poc-contract-amendments.md`,
  `docs/tasks/task-T597.md` and `docs/tasks/completed-tasks.md:370–402`.

I opened nothing under `tests/golden/held-out/`, no fixture file, and no `.env*`, credential or key file.

## 1. Summary

| Subject | Step that fired | Ruling | ADR-008 amendment | User question | Golden quote / fixture / result |
|---|---|---|---|---|---|
| **(a)** "PoC root" undefined | **E (P5)** | No document defines or places the PoC root. All six sites quote the same undefined phrase, and P29 §3a forbids a lower document from defining it | None. Held until the user decides | **Q-A** (A1 / **A2** / A3) | None, for every option |
| **(b)** No per-item severity in the Debt Inventory | **A (P3a)** | The `## Summary` is **not** computable from the scorecard's own table. Today only `technical-debt-tracking:145` fills the gap, from the debt ledger, and only when that skill writes the scorecard. That is a specialisation (D4), not a conflict | None on ADR-008's authority | **Q-B** (**B1** / B2 / B3), because B1 is a tier-1 edit | None, for every option |
| **(c)** Legacy section | **A (P3a)** | As written, `TECHNICAL-DEBT.md` is **still required**: the note supersedes only "the legacy `DEBT:` comment format" (P29 §3c's literal reading, an input). No cross-document conflict arises under either reading. The "(Legacy)" heading makes the text ambiguous, and only a tier-1 edit can clarify it | None on ADR-008's authority | **Q-C** (**C1** / C2 / C3 / C4) | No quote, fixture or result. C4 alone leaves one descriptive sentence stale (`evaluate-poc-verdict-debt-reconciliation/brief.md:78`) |
| **(d)** Three debt registers (F5) | **A (P3a)** | The three registers coexist and do not conflict. They relate as follows: the ledger is the per-item working register, the scorecard is the summary that gates completion, and `TECHNICAL-DEBT.md` is the narrative explanation. The narrative never acts as a separate source of values | **D1**: a note on `technical-debt-narrator.md:14`. It is ruled and needs no user decision, but it is applied in the form for the user's Q-C answer and **not at all under C4** | None (it depends on Q-C) | None |

**Recommendation for the one-round decision:** **A2, B1, C1**. D1 then follows automatically.

## 2. Hard limits, checked

| Limit | Status |
|---|---|
| No upward amendment on ADR-008's own authority | **Met.** No tier-1 edit is made under ADR-008. A1/A2, B1 and C1–C4 are user-decided instruction changes. Each is argued on `poc-guidelines.md`'s own text, never to match a lower document (ADR-008 P1 Remedy) |
| A `poc-guidelines.md` or command edit appears only as a user-decided option | **Met.** No command edit is proposed in any option. Edits to `poc-guidelines.md` appear only inside Q-A, Q-B and Q-C |
| Never relax a check | **Met.** No option removes or loosens a check. C1, C3 and C4 change or remove a *documentation duty* that no rule, gate or test checks. §4.3 states each change openly so that the user decides it with full information |
| Never weaken a security rule or Immutable Security Constraint | **Met.** No option touches `security-guidelines.md` or § Allowed Shortcuts `:68`. B1 adds a sentence that keeps the debt scale apart from `SECURITY:*` grades. It is a clarification, so a **Security Engineer review is recommended if B1 is chosen** (plan-110 §2 step 2) |
| Earlier rulings are inputs | **Met.** P29 §3a ("quote … rather than define") excludes defining "PoC root" in a lower document. P29 §3b fixes the three tiers. P29 §3c (the literal reading of the Legacy note; `TECHNICAL-DEBT.md` is a separate register) is the basis of (c) and (d). P35/T570 §4c ("feeds the scorecard") is the basis of (d). P42 and O1 bound B1's security sentence. P11, P30, P31 and P38 are untouched |
| Self-placement only at Step D (Q1) | **Met.** Step D fires in no record. Nesting or breadth is relied on nowhere |
| Golden isolation | **Met.** Only cases with a `tests/golden/open/` directory are named. `tests/golden/held-out/` was not opened |

## 3. D5 records

### 3.1 (a) "PoC root" is undefined

**Subject (D3).** A path: the directory in which `POC-DEBT-SCORECARD.md` is created.

**Clauses that use the phrase** (all of them, in the files read):

| # | File:line | Verbatim |
|---|---|---|
| 1 | `instructions/poc-guidelines.md:116` | "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:" |
| 2 | `commands/new-poc.md:37` | "- Write to `POC-DEBT-SCORECARD.md` in the PoC root, per `poc-guidelines.md` § Debt Scorecard" |
| 3 | `commands/poc-demo.md:27` | "- Reference the Technical Debt Scorecard (`POC-DEBT-SCORECARD.md` in the PoC root, per `poc-guidelines.md` § Debt Scorecard)" |
| 4 | `skills/technical-debt-tracking/SKILL.md:33` | "- The Technical Debt Scorecard is `POC-DEBT-SCORECARD.md` in the PoC root, in the structure `poc-guidelines.md` § Debt Scorecard defines. …" |
| 5 | `skills/technical-debt-tracking/SKILL.md:145` | "The Technical Debt Scorecard is `POC-DEBT-SCORECARD.md` in the PoC root. …" |
| 6 | `skills/poc-evaluation/SKILL.md:105` | "[Reference, by inventory `#`, to the related items in `POC-DEBT-SCORECARD.md` in the PoC root (`poc-guidelines.md` § Debt Scorecard), …]" |

**Documents that place PoC files, and what they place:**

| File:line | Verbatim | Places the PoC root? |
|---|---|---|
| `new-poc.md:17` | "- Write to `docs/plans/plan-<ID>.md`" | No. This is the plan |
| `new-poc.md:46` | "- Write checkpoint per `AGENTS.md` § Checkpoint Protocol: store at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, …" | No. This is the checkpoint |
| `poc-orchestrator.md:25` | "3. Write a lightweight plan in `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location):" | No. Its plan contents (`:26–29`) name no directory |
| `rapid-prototyping/SKILL.md:10` | "**Inputs**: A PoC repository to bootstrap or a minimal architecture slice to build (§ When to use), …" | No. This is a hint only |
| `rapid-prototyping/SKILL.md:17` | "- Bootstrapping PoC repositories" | No. This is a hint only |
| `rapid-prototyping/SKILL.md:81–82` | "docs/artifacts/poc-{name}-v1.md" / "docs/artifacts/poc-{name}-v2.md" | No. This is the PoC artifact |
| `technical-debt-tracking/SKILL.md:48` | "grep -rn "POC-DEBT:" … ." | No. It scans the current directory, which is a hint |
| `technical-debt-tracking/SKILL.md:137–138` | "docs/artifacts/debt-ledger-v1.md" / "docs/artifacts/debt-ledger-v2.md" | No. This is the ledger |
| `technology-scouting/SKILL.md:27` | "docs/artifacts/tech-eval-v1.md" | No |
| `poc-guidelines.md:146` | "1. The scorecard must account for **every** `POC-DEBT` tag in the codebase" | No. "the codebase" is also undefined (§8, O5) |
| `scaffolding-agent.md:14` | "- Project skeleton" | No path |
| `implementation/AGENTS.md` | (no PoC path anywhere) | No |

None of the other nine PoC agents I read (`poc-technical-writer`, `poc-devops-engineer`, `demo-agent`,
`integration-agent`, `data-mockup-agent`, `poc-qa-engineer`, `poc-security-engineer`, `feasibility-agent`,
`technology-scout`), and neither `evaluate-poc.md` nor `evaluation-agent.md`, uses "PoC root" or places a PoC directory.
**A repository-wide search was not possible (unverified).** The orchestrator should confirm, with `tests/golden/held-out`
pruned, that "PoC root" occurs nowhere else in `implementation/knowledge/` or `implementation/AGENTS.md`.

**Step A analysis.**
- **MUSTs.** Clause 1 obliges the author to create the file "in the PoC root". Clauses 2–6 point to the same place in
  the same words.
- **Exclusivity.** None of the clauses is exclusive against another, and none offers a second location.
- **One value.** One decision, the scorecard's path, should carry one value. Between documents it does: all six clauses
  name the same term, so no two of them can compute different places from each other. The term itself, though, admits
  more than one value: the repository root, or a PoC subdirectory inside a product repository. No text picks one.
- **Result.** There is no conflict between documents, so there is nothing for Steps B–D to rank. The defect is an
  undefined term in a tier-1 text.

**Why Steps B–D cannot decide it.**
- Step B amends lower documents toward tier 1. It cannot write tier-1 text.
- A lower document cannot fill the slot, even as a D4 "fills a slot the other leaves open" specialisation, because an
  earlier ruling excludes it. P29 §3a (`poc-contract-resolution-v1.md:119`): "The follow-up should **quote the
  instruction's phrase rather than define it**. A command that defines it would be deciding the instruction's meaning on
  the instruction's behalf." T570 E5 followed the same rule ("the edit quotes "in the PoC root" and does not define
  it").

**Step that fired: E (P5).** "Anything these rules do not decide is escalated, not chosen" (ADR-008 § Decision). Brief
§1(a): "If none does, escalate."

**Declared scope relied on.**
- `poc-guidelines.md:2` (description): "… Enforces mandatory debt tracking, hypothesis-first validation, and debt
  scorecards."
- `:10–13` (Rails Inputs, joined): "applies whenever `poc-orchestrator` or a PoC specialist agent begins hypothesis-driven
  exploratory work".

The subject is the instruction's own (§ Debt Scorecard › Scorecard Format).

**Amendment.** None. Held until the user decides **Q-A** (§4.1).

**Maturity.** Not relied on. `maturity: stable` is used only for D1 tier membership.

### 3.2 (b) The Debt Inventory has no per-item severity column

**Subject (D3).** A field: the per-item severity that the scorecard's `## Summary` tier counts are computed from.

**Clauses.**

| File:line | Verbatim |
|---|---|
| `poc-guidelines.md:113` | "Before a PoC can be marked as complete, a **debt scorecard** must be produced. This is a summary document that inventories all shortcuts taken." |
| `poc-guidelines.md:129` | "\| # \| File \| Line \| Category \| Description \| Production Effort \|" |
| `poc-guidelines.md:131–133` | Category values "Security", "Validation", "Reliability"; no severity cell |
| `poc-guidelines.md:136–139` | "- Total debt items: N" / "- Critical (must fix before production): X" / "- Medium (should fix before production): Y" / "- Low (nice to have): Z" |
| `poc-guidelines.md:147` | "2. Each item must have an estimated production effort: `S` (small), `M` (medium), `L` (large)" |
| `technical-debt-tracking/SKILL.md:145` | "… Count the `## Summary` tiers from the debt ledger's per-item severity. …" |
| `technical-debt-tracking/SKILL.md:83` | "- **Severity:** critical \| medium \| low" |
| `technical-debt-tracking/SKILL.md:68` | "… Then write `POC-DEBT-SCORECARD.md` from it … The ledger is this skill's working register and does not substitute for the scorecard." |
| `technical-debt-narrator.md:17` | "- Technical Debt Scorecard with severity, effort, risk, and ownership" |
| `evaluate-poc.md:20` | "7. Technical Debt Scorecard summary (severity, effort, risk, owner)" |
| `evaluate-poc.md:34`, `:57`, `:59` | "- **Debt items**: <count> (CRITICAL: <n>, MEDIUM: <n>, LOW: <n>)"; its own table carries "Severity" with "CRITICAL/MEDIUM/LOW" |

**Is the Summary computable from the scorecard's own table? No.**
- The Debt Inventory carries effort (Rule 2) and Category. It carries no tier.
- The example Category values (Security, Validation, Reliability) are not tiers.
- So `X`, `Y` and `Z` cannot be derived from, or checked against, the Inventory. Only `N`, the row count, can.
- This is the gap that `poc-skills-alignment-v1.md` §4c recorded and left to P33: "the ledger supplies the **per-item
  severity** that the scorecard's `## Summary` counts but its Debt Inventory has no column for."

**Step A analysis.**
- **MUSTs.** The Summary requires the three counts. No rule requires a per-item tier, and no rule forbids recording one
  elsewhere. The instruction can therefore be obeyed: an author assigns the tiers somewhere and counts them. Within
  `poc-guidelines.md` this is a gap, not a self-contradiction.
- **Exclusivity.** Nothing says "only". `technical-debt-tracking:145` says the five sections stay "unchanged and in that
  order". That is about the sections, and it does not touch the counts' source.
- **Specialisation (D4).** `technical-debt-tracking:145` "fills a slot the other leaves open": the counts' source is the
  ledger's per-item severity. Its tiers nest one-to-one in the instruction's tiers (T570 §4b, an input). `/evaluate-poc`'s
  extra Severity column was already ruled a specialisation (P29 §3b: "They add attributes without competing with any").
  The same holds for `technical-debt-narrator:17`'s "severity" attribute.
- **One value.** Per item, the skill's ledger is the single source when the skill writes the scorecard (`:68`, `:145`).
  So the scorecard's Summary carries one value per item.
- **Result.** Jointly satisfiable. No rank is needed.

**Ruling.**
- The Summary is not computable from its own table.
- When `technical-debt-tracking` writes the scorecard, the debt ledger fills the gap (`:145`). That is in force and
  stays.
- When the skill is not applied, nothing fills it. No text requires the skill (`AGENTS.md` § Skill Workflow says agents
  MUST "check applicable skills", not apply this one). The counts are then unverifiable.

**What fills the residual gap.** Whether `poc-guidelines.md`'s own template should carry the tier is a tier-1 merits
question. ADR-008 P1 Remedy: "If the tier-1 text is wrong on the merits, the fix is a separate instruction-change task."
It goes to the user as **Q-B** (§4.2).

**Step that fired: A (P3a).** No conflict, no rank.

**Declared scope relied on.**
- `poc-guidelines.md:2` (debt scorecards).
- `technical-debt-tracking:3`: "Document PoC shortcuts and production remediation plans using a consistent debt ledger."
- `technical-debt-tracking:12` (Rails Out of scope): "Does not define a second scorecard: it adds sections to
  `POC-DEBT-SCORECARD.md`".

**Amendment.** None on ADR-008's authority. The B1 and B2 edits are held in Q-B.

**Maturity.** Not relied on. The skill being `experimental` and the instruction `stable` plays no part in the Step A
result.

### 3.3 (c) The Legacy section is ambiguous

**Subject (D3).** A step: whether, and by whom, `TECHNICAL-DEBT.md` must be written in a PoC.

**Clauses.**

| File:line | Verbatim |
|---|---|
| `poc-guidelines.md:151` | "## Required Debt Marking (Legacy)" |
| `poc-guidelines.md:152` | "When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`." |
| `poc-guidelines.md:154` | "> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work." |
| `poc-orchestrator.md:58` | "12. **Debt Narration** — `@technical-debt-narrator`: TECHNICAL-DEBT.md + scorecard" |
| `poc-orchestrator.md:96–99` (joined) | "… (the legacy `DEBT:` format that instruction documents is superseded and should not be used for new PoC work)" |
| `poc-orchestrator.md:102` | "   - `TECHNICAL-DEBT.md` from `@technical-debt-narrator`" |
| `technical-debt-narrator.md:14` | "- TECHNICAL-DEBT.md with categorized debt" |
| `technical-debt-narrator.md:46` | "**Inputs**: The set of `POC-DEBT`/`DEBT:` tags and shortcuts introduced during PoC execution, …" |

**Reading of the current text.**
- `:152` imposes two duties joined by "and": (i) `DEBT:` comments; (ii) update `TECHNICAL-DEBT.md`.
- The note at `:154`, which is the text's own explanation of the "(Legacy)" label, supersedes only "the legacy `DEBT:`
  comment format". It does not reach duty (ii).
- The heading still begins "Required".
- So **as written, duty (ii) survives: `TECHNICAL-DEBT.md` is still required.** This is P29 §3c's reading, taken as an
  input: "Reading the note literally, the file survives."
- The other reading, that "(Legacy)" retires the whole section, rests on the heading alone. It is contestable, but no
  sentence supports it.

**Step A analysis (cross-document).**
- **Under the literal reading.** The two stable agents produce `TECHNICAL-DEBT.md` (`poc-orchestrator:58`, `:102`;
  `technical-debt-narrator:14`). They satisfy duty (ii) as to the file. Nothing in them forbids a specialist from also
  updating it when it introduces a shortcut: `poc-orchestrator:85` (delegation item 5) is a reminder, not "only".
- **Under the retired reading.** A file that no rule requires may still be produced, so the agents contradict nothing.
- **One value.** The status of `TECHNICAL-DEBT.md` is one decision. The two *readings* give it two values, but that
  disagreement lies inside one tier-1 file, not between documents. ADR-008 § Scope excludes "A document that contradicts
  itself". Clarifying the text is an edit to tier-1 text, which is the user's.
- **Result.** Jointly satisfiable across documents under either reading. No rank is needed.

**Step that fired: A (P3a)** for every cross-document pair. The residual same-file ambiguity in tier 1 is outside
ADR-008 and goes to the user as **Q-C** (§4.3).

**Declared scope relied on.**
- `poc-guidelines.md:2` ("Enforces mandatory debt tracking").
- `:10–13` ("a PoC specialist agent").
- `technical-debt-narrator.md:3`: "Use to document shortcuts and debt introduced during PoC work …". By its own
  description it is a PoC specialist inside the instruction's reach (D2, "reach can be shown from either side").
- `poc-orchestrator.md:91–94` (joined): "the Debt Scorecard format this section summarizes are defined in
  `poc-guidelines.md` — every delegation this agent issues is governed by that instruction".

**Amendment.** None on ADR-008's authority. The C1–C4 edits are held in Q-C.

**Maturity.** Not relied on.

### 3.4 (d) F5: the three debt registers

**Subject (D3).** An actor-and-artifact relationship: how `TECHNICAL-DEBT.md`, `debt-ledger-v{N}.md` and the scorecard's
Debt Inventory relate. It decomposes into one sub-subject per pair.

**Clauses.**

| Register | File:line | Verbatim |
|---|---|---|
| `TECHNICAL-DEBT.md` | `technical-debt-narrator.md:14`, `:15` | "- TECHNICAL-DEBT.md with categorized debt" / "- Severity and remediation effort estimates" |
| | `poc-orchestrator.md:58`, `:102` | quoted in §3.3 |
| Debt ledger | `technical-debt-tracking/SKILL.md:3` | "Document PoC shortcuts and production remediation plans using a consistent debt ledger." |
| | `technical-debt-tracking/SKILL.md:68` | "Output the full debt ledger as a versioned artifact (see below). Then write `POC-DEBT-SCORECARD.md` from it … Every `POC-DEBT` tag found in Step 1 must appear in the scorecard's Debt Inventory (`poc-guidelines.md` Scorecard Rule 1). The ledger is this skill's working register and does not substitute for the scorecard." |
| | `technical-debt-tracking/SKILL.md:141` | "Each version is immutable. Create a new version when items are added, resolved, or promoted." |
| Scorecard Debt Inventory | `poc-guidelines.md:109` | "4. Debt tags must also be registered in the debt scorecard (see below)" |
| | `poc-guidelines.md:113`, `:146`, `:149` | "This is a summary document that inventories all shortcuts taken." / Rule 1 / "4. No PoC task may be marked complete without a finalized scorecard" |
| Consumers | `poc-evaluation/SKILL.md:10` | "… the PoC's `POC-DEBT-SCORECARD.md` and debt ledger (technical-debt-tracking skill). …" |

**What relates what.**
- Ledger ↔ scorecard: related by `technical-debt-tracking:68` and `:145` (T570 §4c: "a distinct working register that
  feeds the scorecard").
- `TECHNICAL-DEBT.md` ↔ scorecard: related by P29 §3c ("a narrative debt register, a different artifact class") and by
  `poc-orchestrator:58`, which names both.
- `TECHNICAL-DEBT.md` ↔ ledger: **no text relates them.** `technical-debt-narrator.md` never names the ledger or the
  skill, and `technical-debt-tracking` never names `TECHNICAL-DEBT.md` or the narrator. This was confirmed in both files
  as read. A wider search is **(unverified)**.

**Step A analysis.**
- **MUSTs.**
  - The scorecard must inventory every tag (Rule 1) and gate completion (Rule 4).
  - The ledger is versioned and immutable (`:141`) and feeds the scorecard (`:68`).
  - `TECHNICAL-DEBT.md` is a narrator deliverable with "categorized debt".
- **Exclusivity.**
  - `technical-debt-tracking:68` ("does not substitute for the scorecard") and `:12` ("Does not define a second
    scorecard") exclude rivalry with the scorecard.
  - Nothing claims to be the *only* debt record, and nothing forbids a narrative register.
- **One value.**
  - The registers render the same items. One item's severity, effort or disposition is one decision, so every register
    that states it must carry one value.
  - Ledger → scorecard already holds one value, because the scorecard is written from the ledger (`:68`, `:145`).
  - `TECHNICAL-DEBT.md` → ledger is not tied. `technical-debt-narrator:15` makes "Severity and remediation effort
    estimates", and nothing says they are the ledger's values. If the narrator restates a value in `TECHNICAL-DEBT.md`,
    two values are possible for one item. That is a gap in what the documents *state*, not a clause that *requires*
    divergence. Both can be satisfied by using the ledger's value, so this is not a contradiction. ADR-008 P3a: "A ruling
    then amends at most to state the relationship where readers will see it."
- **Result.** Jointly satisfiable. The three registers coexist, and none governs another by rank.

**Step that fired: A (P3a).**

**Declared scope relied on.**
- `technical-debt-narrator.md:3` (above) and `:11`: "Document all PoC shortcuts and rebuild requirements."
- `technical-debt-tracking:3`, `:12`.
- `poc-guidelines.md:113`.

**Ruling.** The three registers coexist:

| Register | Role | Source of per-item values |
|---|---|---|
| Debt ledger (`docs/artifacts/debt-ledger-v{N}.md`), when `technical-debt-tracking` is applied | Per-item working register, versioned and immutable, including non-tag sources | Itself |
| Scorecard Debt Inventory (`POC-DEBT-SCORECARD.md`) | Summary and completion record; inventories every `POC-DEBT` tag | The ledger, when one exists (`:68`, `:145`) |
| `TECHNICAL-DEBT.md` (narrator) | Narrative explanation for the inheriting team | The ledger, or else the scorecard. **Never a separate source** |

**Amendment: D1**, a Step A note on `technical-debt-narrator.md:14`, the document whose readers write the narrative
register (§5). It is not a tier-1 or command edit, so it needs no user decision. It does depend on Q-C:
- under **C1, C2 or C3**, D1 is applied as held;
- under **C4**, `TECHNICAL-DEBT.md` is retired, C4's own narrator edit (C4-d) replaces line 14, and **D1 is not
  applied**. The two remaining registers are already related by `technical-debt-tracking:68`.

**Maturity.** Not relied on. `technical-debt-narrator` is `stable` and the skill `experimental`. Neither fact enters the
analysis.

## 4. User questions

They are designed to be decided in **one round**. Q-A, Q-B and Q-C are independent: their anchors do not overlap (§6),
and any combination can be implemented in one task. D1 (§5) follows from the Q-C answer.

**Common consequences for every tier-1 option** (they are not repeated per option):
- **Tooling.** Regenerate mirrors with `node implementation/scripts/sync.mjs --root implementation` and the registry
  checksum with `python3 implementation/scripts/generate-registry.py`. Declare root-projection drift for
  `poc-guidelines.md`, and for every agent or skill touched, in `tests/_baselines/root-install-drift.json`, exactly as
  `--print-drift` reports it (T577 precedent). The path count is **(unverified)**.
- **Evaluator hash.** No option edits `tests/golden/**` or `scripts/scorecard.py`, so no protected-path grant and no v19
  are needed. The one optional exception is under C4 (§4.3).
- **Existing PoCs.** This repository has none. `new-poc-plan-hypothesis-format/brief.md:105–106` records: "No `/new-poc`
  run has ever produced a committed artifact in this repository, at any point in its history." Effects on PoCs in
  downstream install targets are stated per option and are **(unverified)**.

### 4.1 Q-A — what is "the PoC root"?

**Subject.** The directory in which `POC-DEBT-SCORECARD.md` is created (§3.1).

**Quotes.**
- `poc-guidelines.md:116`: "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:"
- Five lower sites quote the same phrase: `new-poc.md:37`, `poc-demo.md:27`, `technical-debt-tracking:33`, `:145`, and
  `poc-evaluation:105`.

**Why the steps did not decide it.**
- Step A finds no conflict: every site uses the same words.
- No document defines or places the PoC root.
- P29 §3a forbids a lower document from defining it.
- ADR-008 cannot write tier-1 text.
- Step E: escalate.

**Options.**

| Option | Meaning | Files | Golden impact | Tooling | Effect on existing PoCs |
|---|---|---|---|---|---|
| **A1. Repository root** | The PoC root is the root of the repository that holds the PoC, the directory that contains its `docs/` tree | `poc-guidelines.md` (one sentence inserted before `:116`) | None: no quote, fixture or result changes. The golden briefs quote the commands' "in the PoC root", which is unchanged | Common | One PoC, and one scorecard, per repository at a time. A repository that holds two PoCs (Rule 2 splits multi-hypothesis work into separate PoCs) cannot hold two scorecards at one path. A PoC kept in a subdirectory of a product repository must keep its scorecard at the repository root |
| **A2. The PoC's top-level directory** (recommended) | The repository root if the PoC has its own repository, otherwise the directory the PoC plan names. Each PoC has its own root and its own scorecard | `poc-guidelines.md` (one sentence inserted before `:116`); `poc-orchestrator.md` (one plan bullet, A2-b) | None, for either edit. `poc-orchestrator` is cited by no golden quote that changes: `new-poc-plan-hypothesis-format/brief.md:58` quotes `:25`, which stays. `:83–84` there says PLAN PHASE contents are "not asserted", which stays true | Common, plus `poc-orchestrator`'s projections | Own-repository PoCs: unchanged. Subdirectory PoCs: their plan must name the directory. A plan written earlier lacks the bullet until it is next revised |
| **A3. Leave undefined** (re-park P33(a)) | No change | None | None | None | None. Scorecard Rule 4's completion gate and Rule 1 keep an artifact whose location cannot be checked. All six sites keep quoting an undefined term |

**Not offered.** Defining the term in a command, agent or skill and leaving tier 1 untouched. P29 §3a (an input)
excludes it: "A command that defines it would be deciding the instruction's meaning on the instruction's behalf."

**Recommendation: A2.**
- It is the only option that works for both PoC shapes the corpus describes: its own repository
  (`rapid-prototyping:17`, "Bootstrapping PoC repositories") and a slice inside a larger repository
  (`rapid-prototyping:10`, "a minimal architecture slice").
- It keeps Rule 2's one-hypothesis-per-PoC compatible with one scorecard per PoC.
- It keeps the sentence the five lower sites quote, "in the PoC root", verbatim, so none of them needs an edit.
- A1 is valid but forbids two PoCs in one repository.
- Golden coupling is zero for all three options, so it played no part in the choice (P4(e)).

**Held candidate edits.**

**A1** — `implementation/knowledge/instructions/poc-guidelines.md`

````
Before:
### Scorecard Format
Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:

After:
### Scorecard Format
The PoC root is the root directory of the repository that holds the PoC: the directory that contains its `docs/` tree. A repository therefore holds one PoC, and one scorecard, at a time.

Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:
````

**A2** — `implementation/knowledge/instructions/poc-guidelines.md`

````
Before:
### Scorecard Format
Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:

After:
### Scorecard Format
The PoC root is the top-level directory of the PoC's code: the repository root when the PoC has its own repository, otherwise the directory that the PoC plan (`docs/plans/plan-<ID>.md`) names as the PoC root. Each PoC has its own PoC root and its own scorecard.

Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:
````

**A2-b** (part of A2) — `implementation/knowledge/agents/poc-orchestrator.md`, § PLAN PHASE item 3. This is a Step A
note: the plan list is not exclusive, so without it nothing contradicts. It exists so that the plan actually names the
root.

````
Before:
   - Key risks and assumptions
   - PoC token budget

After:
   - Key risks and assumptions
   - PoC root, when the PoC does not have its own repository (`poc-guidelines.md` § Debt Scorecard › Scorecard Format)
   - PoC token budget
````

**A3** — no edit.

### 4.2 Q-B — should the scorecard's own table carry each item's severity?

**Subject.** The per-item severity from which the `## Summary` counts are computed (§3.2).

**Quotes.**
- `poc-guidelines.md:129`: "\| # \| File \| Line \| Category \| Description \| Production Effort \|".
- `:137–139`: "- Critical (must fix before production): X" / "- Medium (should fix before production): Y" / "- Low (nice
  to have): Z".
- `technical-debt-tracking:145`: "Count the `## Summary` tiers from the debt ledger's per-item severity."

**Why the steps did not decide it.**
- Step A holds: the skill fills the open slot, so there is no conflict and no ADR-008 amendment.
- The residual is a merits question about tier 1's own template. It covers a PoC whose scorecard is written without the
  skill.
- Only the user changes tier-1 text.

**Options.**

| Option | Meaning | Files | Golden impact | Tooling | Effect on existing PoCs |
|---|---|---|---|---|---|
| **B1. Add a `Severity` column and Scorecard Rule 5** (recommended) | The Inventory carries each item's tier. `Total debt items` is its row count and the three counts are counts of the column, so the Summary becomes checkable against the table. A sentence keeps the debt tier apart from `SECURITY:*` grades | `poc-guidelines.md` (table `:129–133`; rules `:148–149` gain Rule 5); `technical-debt-tracking/SKILL.md:145` (B1-b, the consequential note) | None: no quote, fixture or result changes. `evaluate-poc-verdict-debt-reconciliation/brief.md:77`'s description, "three-tier summary (Critical / Medium / Low)", stays true. That case "has no `POC-DEBT-SCORECARD.md` fixture" (`:89–90`) | Common, plus the skill's projections. **Security Engineer review recommended** (the Rule 5 security sentence; row 1 is Security-category) | A scorecard written before the change lacks the column. It conforms after the next revision. No PoC exists in this repository |
| **B2. No tier-1 change; the skill appends per-item severity** | When `technical-debt-tracking` writes the scorecard, it appends `## Inventory Severity` (`#` → severity). The Summary becomes checkable inside the file in that case only | `technical-debt-tracking/SKILL.md` (`:145` and an inserted section) | None | Mirrors, registry and drift for the skill only | No change when the skill is not applied. The gap stays there |
| **B3. Status quo** | The ledger fills the gap when the skill is applied, and nothing does otherwise | None | None | None | None. A PoC whose scorecard is written without the skill has unverifiable Summary counts |

**Recommendation: B1.**
- The `## Summary` is the instruction's own section. A template whose tier counts cannot be computed from its own
  inventory is incoherent on its own text. That is the merits ground, and it does not depend on what a lower document
  does (ADR-008 P1 Remedy).
- B1 closes the gap for every PoC, not only those where the skill runs.
- The tiers and meanings come from `:137–139`, not from `/evaluate-poc` or the skill. That `technical-debt-narrator:17`
  already promises "severity" in the scorecard is a consequence, not the reason.
- B2 is valid, but it leaves the gap open when the skill is not applied, and it adds a fourth place where severity lives.
- All options have zero golden impact.

**How B1's example values were chosen.**
- Each row's tier comes from the instruction's own text for that row.
- Debt Tag Rule 1 (`:106`) makes each tag state "what the production solution needs", and the rows' tags read:
  - row 1, `:83`: "production must read the URL from configuration …";
  - row 2, `:90`: "production must move these checks into the schema layer …";
  - row 3, `:101`: "production should use async with retry".
- Against `:137–138` ("must fix before production" = Critical; "should fix before production" = Medium), that gives
  **Critical, Critical, Medium**.
- **Disclosed tension, illustrative only.** `technical-debt-tracking:101` lists "hardcoded configuration" under `medium`.
  For row 1, the skill's guide and the instruction's example would then differ. The example is illustrative, not a rule,
  so no clause contradicts another. A reviewer may prefer `Medium` for row 1. I keep `Critical`: it follows the
  instruction's own words, and on a Security-category row the stricter tier is the safe direction.
- **Security sentence.** A `Critical` debt item in the Security category could be misread as a `SECURITY:CRITICAL` finding
  recorded as debt, which the O1 and P39 rulings forbid for findings. Rule 5's second sentence keeps the two scales apart
  and restates § Allowed Shortcuts `:68` ("A `POC-DEBT` tag records a shortcut; it does not make a forbidden shortcut
  permissible"). It neither adds a new security rule nor relaxes one.

**Held candidate edits.**

**B1** — `implementation/knowledge/instructions/poc-guidelines.md`, the Debt Inventory table

````
Before:
| # | File | Line | Category | Description | Production Effort |
|---|------|------|----------|-------------|-------------------|
| 1 | src/db.py | 12 | Security | Hardcoded local database URL (no credentials) | S — read URL from configuration, credentials from vault |
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Reliability | No retry logic | M — add retry with backoff |

After:
| # | File | Line | Category | Description | Severity | Production Effort |
|---|------|------|----------|-------------|----------|-------------------|
| 1 | src/db.py | 12 | Security | Hardcoded local database URL (no credentials) | Critical | S — read URL from configuration, credentials from vault |
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | Critical | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Reliability | No retry logic | Medium | M — add retry with backoff |
````

**B1** (continued) — `implementation/knowledge/instructions/poc-guidelines.md`, § Scorecard Rules

````
Before:
3. The scorecard must be reviewed by the Tech Lead before the PoC is closed
4. No PoC task may be marked complete without a finalized scorecard

After:
3. The scorecard must be reviewed by the Tech Lead before the PoC is closed
4. No PoC task may be marked complete without a finalized scorecard
5. Each item must have a severity: `Critical` (must fix before production), `Medium` (should fix before production) or `Low` (nice to have). In the `## Summary`, `Total debt items` is the number of Debt Inventory rows, and each tier's count is the number of rows with that `Severity`. This severity grades debt items, not security findings: a debt item's `Critical` is not a `SECURITY:CRITICAL` grade, and no tag or severity here makes a shortcut that `security-guidelines.md` forbids permissible (§ Allowed Shortcuts)
````

The rule is appended as Rule 5, not merged into Rule 2, so that the citations "Scorecard Rule 1", "Rules 1 and 4" and
"Rules 3–4" (`technical-debt-tracking:14`, `:68`, `:179`; `poc-evaluation:128`) keep their numbers.

**B1-b** (part of B1) — `implementation/knowledge/skills/technical-debt-tracking/SKILL.md:145`. This is a Step B
consequence once B1 lands. Under B1 the counts come from the column, and the skill's sentence names the ledger. The edit
makes the column carry the ledger's value, so the two sources cannot diverge.

````
Before:
Count the `## Summary` tiers from the debt ledger's per-item severity.

After:
Fill the Debt Inventory's `Severity` column with each item's debt-ledger severity, and count the `## Summary` tiers from that column (`poc-guidelines.md` Scorecard Rule 5).
````

The Before text is a sentence inside line 145, and it occurs once in the file. The rest of line 145 is unchanged.

**B2** — `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`

````
Before:
Count the `## Summary` tiers from the debt ledger's per-item severity.

After:
Count the `## Summary` tiers from the debt ledger's per-item severity, and record each Debt Inventory item's severity, by its `#`, in the appended `## Inventory Severity` section, so that the `## Summary` can be checked against the scorecard itself.
````

````
Before:
## Severity by Disposition

After:
## Inventory Severity

| # | Severity |
|---|----------|
| {inventory #} | {critical, medium or low} |

## Severity by Disposition
````

The second Before text occurs once, at `:152`, inside the appended-sections fence.

**B3** — no edit.

### 4.3 Q-C — is `TECHNICAL-DEBT.md` required, optional or retired?

**Subject.** Whether, and by whom, `TECHNICAL-DEBT.md` is written in a PoC (§3.3).

**Quotes.**
- `poc-guidelines.md:151`: "## Required Debt Marking (Legacy)".
- `:152`: "When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`."
- `:154`: "> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. …"
- `poc-orchestrator.md:58`: "12. **Debt Narration** — `@technical-debt-narrator`: TECHNICAL-DEBT.md + scorecard".
- `technical-debt-narrator.md:14`: "- TECHNICAL-DEBT.md with categorized debt".

**Why the steps did not decide it.**
- Step A finds no cross-document conflict under either reading.
- As written, the file is still required (§3.3). The "Required"/"(Legacy)" heading makes the tier-1 text internally
  ambiguous.
- Same-file ambiguity is outside ADR-008, and clarifying it means editing tier-1 text.

**What each option changes against the current text.**
- The literal duty is **per shortcut**: "When introducing shortcuts … update `TECHNICAL-DEBT.md`".
- The per-shortcut *record* that rules check is the `POC-DEBT` tag: `:72`, `:107` Debt Tag Rule 2, and Scorecard Rule 1
  (`:146`). Nothing checks `TECHNICAL-DEBT.md`: no rule, no gate, no golden `check()`, and (per the brief) no non-golden
  test.
- **C1** moves the duty from every specialist to the narrator.
- **C3** makes the file optional.
- **C4** removes the file.

None of the three relaxes a *check*. Each changes a documentation *duty*, and the user should decide that knowingly.
**C2** keeps the literal duty in full.

**Options.**

| Option | Meaning | Files | Golden impact | Tooling | Effect on existing PoCs |
|---|---|---|---|---|---|
| **C1. Required, written by the narrator** (recommended) | Every PoC produces `TECHNICAL-DEBT.md`. `@technical-debt-narrator` writes it at Debt Narration from the tags and the scorecard. The `DEBT:` comment stays superseded | `poc-guidelines.md` (`:151–154`) | None. Descriptive texts stay true: `evaluate-poc-verdict-debt-reconciliation/brief.md:78` ("`TECHNICAL-DEBT.md` is a separate narrative register") and `new-poc-plan-hypothesis-format/brief.md:70` | Common | None. Both stable agents already work this way (`poc-orchestrator:58`, `:102`; `technical-debt-narrator:14`), so no agent edit is needed |
| **C2. Required per shortcut** (the literal duty, kept and clarified) | Every agent that introduces a shortcut also adds it to `TECHNICAL-DEBT.md`. The narrator completes the file | `poc-guidelines.md` (`:151–154`); `poc-orchestrator.md:85` (C2-b) | None | Common, plus `poc-orchestrator` | Parallel agent worktrees edit one shared file, so merge conflicts are likely. Four PoC agents have no `edit` tool (`feasibility-agent`, `technology-scout`, `poc-security-engineer`, `evaluation-agent`); they rarely introduce code shortcuts, but they cannot comply if they do |
| **C3. Optional** | A PoC may keep `TECHNICAL-DEBT.md`. It is never required | `poc-guidelines.md` (`:151–154`) | None | Common | None in practice: the PoC workflow still produces the file (`poc-orchestrator:58`), so on that track it stays routine while the instruction no longer requires it |
| **C4. Retired** | `DEBT:` comments and `TECHNICAL-DEBT.md` are both retired | `poc-guidelines.md` (`:151–154`); `poc-orchestrator.md:58`, `:102`; `technical-debt-narrator.md:14` (C4-b to C4-d, Step B consequences: after the change, the agents would produce a file the instruction says not to write) | No quote, fixture or result changes. `evaluate-poc-verdict-debt-reconciliation/brief.md:78` (present tense) becomes **descriptively stale**. Refreshing it is optional, and would need a `protected-paths-v1.md` §5 grant and a user-authorized v19, as FU-8 did | Common, plus two agents | The narrative register is lost from the handoff. The narrator's other deliverables (`:15–19`) remain. D1 is not applied |

**Recommendation: C1.**
- It resolves the "Required"/"(Legacy)" ambiguity.
- It keeps the file required, so no deliverable is lost.
- It matches what both stable agents already prescribe, so no agent edit is needed.
- Per-shortcut capture stays with the checked `POC-DEBT` tag.
- C2 is the strictest reading, and the right choice if the user regards the per-shortcut file update as binding today.
  Its cost is shared-file contention across worktrees.
- C3 and C4 reduce the deliverable set. I do not recommend them.
- Golden coupling played no part: it is zero for all options except C4's descriptive staleness.

**Held candidate edits.**

**C1** — `implementation/knowledge/instructions/poc-guidelines.md`

````
Before:
## Required Debt Marking (Legacy)
When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`.

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.

After:
## Narrative Debt Register (`TECHNICAL-DEBT.md`)
Every PoC must also produce `TECHNICAL-DEBT.md`, a narrative register that explains the PoC's debt to the team that inherits it. `@technical-debt-narrator` writes it at the PoC's Debt Narration step (`poc-orchestrator.md` § PoC Workflow), from the `POC-DEBT` tags and the debt scorecard. It is not a scorecard and does not replace one: every shortcut is still recorded by its `POC-DEBT` tag when it is introduced (§ Inline Debt Tags) and inventoried in the debt scorecard (§ Debt Scorecard).

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.
````

**C2** — `implementation/knowledge/instructions/poc-guidelines.md`

````
Before:
## Required Debt Marking (Legacy)
When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`.

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.

After:
## Debt Register (`TECHNICAL-DEBT.md`)
When introducing a shortcut, tag it with a `POC-DEBT` tag (§ Inline Debt Tags) and add it to `TECHNICAL-DEBT.md`, the PoC's narrative debt register. `@technical-debt-narrator` completes the register at the PoC's Debt Narration step (`poc-orchestrator.md` § PoC Workflow). It is not a scorecard and does not replace one: every shortcut is also inventoried in the debt scorecard (§ Debt Scorecard).

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.
````

**C2-b** (part of C2) — `implementation/knowledge/agents/poc-orchestrator.md:85`, a Step A note on the delegation
reminder

````
Before:
5. **Debt tagging**: "Tag all shortcuts with `POC-DEBT` comments per `poc-guidelines.md`. Report known gaps."

After:
5. **Debt tagging**: "Tag all shortcuts with `POC-DEBT` comments per `poc-guidelines.md`, and add each one to `TECHNICAL-DEBT.md`. Report known gaps."
````

**C3** — `implementation/knowledge/instructions/poc-guidelines.md`

````
Before:
## Required Debt Marking (Legacy)
When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`.

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.

After:
## Narrative Debt Register (`TECHNICAL-DEBT.md`, optional)
A PoC may also keep `TECHNICAL-DEBT.md`, a narrative register that explains the PoC's debt to the team that inherits it. It is optional. It is not a scorecard and never replaces one: every shortcut is recorded by its `POC-DEBT` tag when it is introduced (§ Inline Debt Tags) and inventoried in the debt scorecard (§ Debt Scorecard).

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.
````

**C4** — `implementation/knowledge/instructions/poc-guidelines.md`

````
Before:
## Required Debt Marking (Legacy)
When introducing shortcuts, document them with `DEBT:` comments and update `TECHNICAL-DEBT.md`.

> **Note:** The `POC-DEBT` tag format above supersedes the legacy `DEBT:` comment format. Use `POC-DEBT` tags for all new PoC work.

After:
## Legacy Debt Marking (Retired)
The legacy `DEBT:` comments and the `TECHNICAL-DEBT.md` file are retired. Record every shortcut with a `POC-DEBT` tag (§ Inline Debt Tags) and inventory it in the debt scorecard (§ Debt Scorecard). Do not write `DEBT:` comments or `TECHNICAL-DEBT.md` for new PoC work.
````

**C4-b** (part of C4) — `implementation/knowledge/agents/poc-orchestrator.md:58`

````
Before:
12. **Debt Narration** — `@technical-debt-narrator`: TECHNICAL-DEBT.md + scorecard

After:
12. **Debt Narration** — `@technical-debt-narrator`: Technical Debt Scorecard (`POC-DEBT-SCORECARD.md`)
````

**C4-c** (part of C4) — `implementation/knowledge/agents/poc-orchestrator.md:102`. The source line has **three** leading
spaces, unlike its siblings' two (§8, O4). The edit keeps them so that only the text changes.

````
Before:
   - `TECHNICAL-DEBT.md` from `@technical-debt-narrator`

After:
   - `POC-DEBT-SCORECARD.md` (Technical Debt Scorecard) from `@technical-debt-narrator`
````

**C4-d** (part of C4) — `implementation/knowledge/agents/technical-debt-narrator.md:13–15`

````
Before:
## Deliverables
- TECHNICAL-DEBT.md with categorized debt
- Severity and remediation effort estimates

After:
## Deliverables
- Severity and remediation effort estimates
````

`technical-debt-narrator.md:46` ("`POC-DEBT`/`DEBT:` tags") is left unchanged under every option. Legacy `DEBT:` tags may
still exist in older code, and the narrator still reads them.

## 5. Ruled amendment (Step A note, no user decision): D1

**D1** — `implementation/knowledge/agents/technical-debt-narrator.md:14`. Apply it under **C1, C2 or C3**. Under **C4**
do not apply it: C4-d replaces the line.

````
Before:
- TECHNICAL-DEBT.md with categorized debt

After:
- TECHNICAL-DEBT.md with categorized debt: the PoC's narrative debt register (`poc-guidelines.md`). It explains the items that `POC-DEBT-SCORECARD.md` inventories and, where the technical-debt-tracking skill's debt ledger (`docs/artifacts/debt-ledger-v{N}.md`) exists, the items that ledger records. Where it states an item's severity, effort or disposition, it uses the value the ledger records for that item, or the scorecard's value where there is no ledger. It is neither the scorecard nor the ledger, and it substitutes for neither.
````

**Basis.** §3.4, Step A, "state the relationship where readers will see it". The note cites `poc-guidelines.md` without a
section name, so it reads correctly whichever heading C1, C2 or C3 gives the section. It points to the governing
documents rather than copying them (ADR-008 P3b Remedy practice; `poc-skills-alignment-v1.md` §4a: "It names it, so the
two cannot drift apart").

## 6. Amendment list and hit counts

All counts were made **by reading the files, not by `grep`** (no shell). The implementer must re-count each Before text
(one occurrence expected) before editing.

| ID | File | Anchor (Before) | Before lines / occurrences | Applies under |
|---|---|---|---|---|
| A1 | `instructions/poc-guidelines.md` | `:115–116` "### Scorecard Format" + "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:" | 2 / 1 | Q-A = A1 |
| A2 | `instructions/poc-guidelines.md` | same as A1 | 2 / 1 | Q-A = A2 |
| A2-b | `agents/poc-orchestrator.md` | `:28–29` "   - Key risks and assumptions" + "   - PoC token budget" | 2 / 1 | Q-A = A2 |
| B1 (table) | `instructions/poc-guidelines.md` | `:129–133` | 5 / 1 | Q-B = B1 |
| B1 (rule) | `instructions/poc-guidelines.md` | `:148–149` Rules 3–4 | 2 / 1 | Q-B = B1 |
| B1-b | `skills/technical-debt-tracking/SKILL.md` | sentence in `:145`, "Count the `## Summary` tiers from the debt ledger's per-item severity." | 1 / 1 | Q-B = B1 |
| B2 (sentence) | `skills/technical-debt-tracking/SKILL.md` | same sentence as B1-b | 1 / 1 | Q-B = B2 |
| B2 (section) | `skills/technical-debt-tracking/SKILL.md` | `:152` "## Severity by Disposition" | 1 / 1 | Q-B = B2 |
| C1 / C2 / C3 / C4 | `instructions/poc-guidelines.md` | `:151–154` (the heading through the note) | 4 / 1 | Q-C, exactly one of the four |
| C2-b | `agents/poc-orchestrator.md` | `:85` | 1 / 1 | Q-C = C2 |
| C4-b | `agents/poc-orchestrator.md` | `:58` | 1 / 1 | Q-C = C4 |
| C4-c | `agents/poc-orchestrator.md` | `:102` | 1 / 1 | Q-C = C4 |
| C4-d | `agents/technical-debt-narrator.md` | `:13–15` | 3 / 1 | Q-C = C4 |
| D1 | `agents/technical-debt-narrator.md` | `:14` | 1 / 1 | Q-C ∈ {C1, C2, C3} |

**Anchor independence.**
- `poc-guidelines.md`: A (`:115–116`), B1 (`:129–133`, `:148–149`) and C (`:151–154`) are disjoint.
- `poc-orchestrator.md`: A2-b (`:28–29`), C2-b (`:85`), C4-b (`:58`) and C4-c (`:102`) are disjoint.
- `technical-debt-narrator.md`: D1 and C4-d both touch `:14`, but they are mutually exclusive by construction.
- `technical-debt-tracking`: B1-b and B2 share an anchor, but they are mutually exclusive alternatives.

**Term counts in source, before any edit** (the files read; elsewhere **unverified**):

| Term | File: lines | Lines / occurrences |
|---|---|---|
| "PoC root" | `poc-guidelines.md:116`; `new-poc.md:37`; `poc-demo.md:27`; `technical-debt-tracking:33, 145`; `poc-evaluation:105` | 6 / 6, in 5 files. Zero in `poc-orchestrator`, `technical-debt-narrator`, `evaluation-agent`, `rapid-prototyping`, `evaluate-poc`, `implementation/AGENTS.md` and the other PoC agents read |
| `TECHNICAL-DEBT.md` | `poc-guidelines.md:152`; `poc-orchestrator.md:58, 102`; `technical-debt-narrator.md:14` | 4 / 4, in 3 files |
| `debt-ledger` (hyphenated) | `technical-debt-tracking:129, 133, 137, 138, 150`; `poc-evaluation:105` | 6 / 6, in 2 files |
| `POC-DEBT-SCORECARD` | `poc-guidelines.md:116`; `new-poc.md:37`; `poc-demo.md:27`; `technical-debt-tracking:12, 33, 68, 145`; `poc-evaluation:10, 105, 128` | 10 / 10, in 5 files |

**Expected counts after the recommended set (A2 + B1 + C1 + D1):**

| Term | File: lines after the edit | Lines / occurrences |
|---|---|---|
| "PoC root" | `poc-guidelines.md`: the new definition line (3) and the "Create …" line (1) | 2 / 4 |
| | `poc-orchestrator.md`: the A2-b bullet | 1 / 1 |
| | all other files | unchanged |
| `TECHNICAL-DEBT.md` | `poc-guidelines.md`: the C1 heading and body | 2 / 2 |
| | `technical-debt-narrator.md:14` (D1 does not repeat it) | 1 / 1 |
| | `poc-orchestrator.md` | unchanged, 2 / 2 |
| `debt-ledger` | `technical-debt-narrator.md`: D1 adds one | 1 / 1 |
| | `technical-debt-tracking`: B1-b's text adds "debt-ledger severity" to line 145 | 5 / 5 → **6 / 6** |
| `POC-DEBT-SCORECARD` | `technical-debt-narrator.md`: D1 adds one | 1 / 1 |

The B1-b row is easy to miscount. Line 145 does **not** contain "debt-ledger" (hyphenated) before the edit: its old text
reads "debt ledger's", with a space. After B1-b it does. The implementer should confirm every count mechanically, given
the T585 erratum precedent.

## 7. Golden coupling, per candidate edit

Only cases with a `tests/golden/open/` directory are named. The brief's pre-computed table lists them.

**What the three cases quote from `poc-guidelines.md`.** I read each `brief.md` and `expect.py`:
- `evaluate-poc-verdict-debt-reconciliation/brief.md:63–64` quotes Rules 3–4 (`:55–56`).
- `new-poc-plan-hypothesis-format/brief.md:24–31` quotes the Hypothesis Format (`:35–40`) and Rule 2 (`:54`).
- `poc-demo-hypothesis-status-evidence-gaps/brief.md:83` quotes a fragment of Rule 4 (`:56`).

**No case quotes `:113–154`**, which is where every candidate edit falls. No `check()` reads `poc-guidelines.md`, any agent
or any skill. Each `check()` reads only its own `fixture/` (`expect.py:107`, `:73`, `:74` respectively).

| Edit | Golden quote changes? | Fixture changes? | Result changes? | Descriptive text affected | Non-golden test that loads a golden `expect.py` affected? |
|---|---|---|---|---|---|
| A1, A2 | No | No | No | None. The briefs quote the commands' "in the PoC root", which stays | No (see below) |
| A2-b | No | No | No | `new-poc-plan-hypothesis-format/brief.md:83–84` ("PLAN PHASE contents … not asserted") stays true | No |
| B1, B1-b | No | No | No | `evaluate-poc-verdict-debt-reconciliation/brief.md:77` stays true; `:89–90` ("no `POC-DEBT-SCORECARD.md` fixture") stays true | No |
| B2 | No | No | No | None | No |
| C1, C2, C3 | No | No | No | `evaluate-poc-verdict-debt-reconciliation/brief.md:78` and `new-poc-plan-hypothesis-format/brief.md:70` stay true | No |
| C2-b | No | No | No | None | No |
| C4 | No | No | No | **`evaluate-poc-verdict-debt-reconciliation/brief.md:78`** ("`TECHNICAL-DEBT.md` is a separate narrative register") becomes stale (present tense). `new-poc-plan-hypothesis-format/brief.md:70` ("was ruled") and `:113` (a historical `git log` grep) stay true | No |
| C4-b, C4-c, C4-d | No | No | No | None | No |
| D1 | No | No | No | None | No |

**Non-golden tests that load a golden `expect.py`.** `tests/functional/test_golden_harness_scoring.py` loads exactly one
case, `REAL_CASE_ID = "new-feature-plan-doc-compliant"` (`:29`), and feeds it synthetic plan files (`:75–88`). No
candidate edit touches that case, its fixture or `/new-feature`, so the test is unaffected. That file's docstring
(`:4–6`) says `scripts/scorecard.py` imports `expect.py` modules the same way. It is not a test, its results depend only on
fixtures, and no edit touches a fixture. **No other test was enumerated (no shell, unverified).** The brief states that
no non-golden test asserts `POC-DEBT-SCORECARD`, "PoC root", `TECHNICAL-DEBT.md` or `debt-ledger`. The orchestrator
should also check that no test asserts the removed or replaced literals:
- "Required Debt Marking";
- "document them with `DEBT:` comments";
- the old header "\| # \| File \| Line \| Category \| Description \| Production Effort \|";
- "Count the `## Summary` tiers from the debt ledger's per-item severity";
- "TECHNICAL-DEBT.md + scorecard".

**Evaluator hash.** No edit touches `tests/golden/**` or `scripts/scorecard.py`, so the `tests_golden` and
`scripts_scorecard` digests do not move and no v19 is needed. The exception is an optional refresh of the C4 descriptive
staleness, which needs a grant and v19.

## 8. Observations outside the four subjects (not ruled; candidates for parking)

- **O1. Categories.** `poc-guidelines.md:131–133` uses the example Categories "Validation" and "Reliability".
  `technical-debt-tracking:82` fixes a closed set: "Security | Architecture | Testing | Data quality | Operations". The
  instruction's Category is an open column, so the skill's closed set is a specialisation, not a conflict. A scorecard
  written from the ledger, though, can never show the instruction's own example categories.
- **O2. Versioning.** `technical-debt-narrator.md:41` says "Name output artifacts: `<type>-vN.md`", but its deliverables
  `TECHNICAL-DEBT.md` and `POC-DEBT-SCORECARD.md` are unversioned single files. This is a same-file tension in the
  narrator, and the line is boilerplate shared by the PoC agents. `implementation/AGENTS.md:22` governs only "Immutable
  artifacts".
- **O3. Security findings in the ledger (possible O1-shaped gap; route to the Security Engineer).**
  `technical-debt-tracking:61–64` merges "Security scan findings" into the ledger with no qualifier. The blocking classes
  are never debt (`poc-security-engineer.md:22`: "A blocking finding is never recorded for debt handoff"), and
  `rapid-prototyping:74` lets such an item enter the ledger "only as `resolved`". The skill states neither. I did not
  rule this, because it is outside P33. I flag it because a reader applying only that skill could record an open
  `SECURITY:HIGH` finding as debt.
- **O4. Indentation.** `poc-orchestrator.md:102` is indented three spaces; its sibling bullets `:101` and `:103` use two.
  C4-c preserves it. A whitespace fix is a separate, trivial edit.
- **O5. "The codebase."** Scorecard Rule 1 (`:146`, "in the codebase") and `technical-debt-tracking:48` (scan `.`) leave
  the scan scope undefined, much like "PoC root". Under A2 a reader might take it to be the PoC root, but nothing says so.
- **O6. A fourth severity rendering.** `/evaluate-poc`'s Debt Summary table (`:57–59`) gives each item a severity, but no
  text says it is the ledger's or scorecard's value for that item. P29 §3b only says the table scores "the same items".
  This is a possible one-value gap between the command's table and the ledger. Under P2 the command's output contract
  governs its rendering, so any note would fall on `poc-evaluation`, not on the command.

## 9. Lines I could not verify

- The worktree's commit hash, `7685de0`. It is as stated by the orchestrator; I had no `git`.
- That "PoC root", `TECHNICAL-DEBT.md` and `debt-ledger` occur nowhere outside the files listed in §0. A repository-wide
  search needs a shell.
- That no non-golden test asserts any literal that §7 lists as removed or replaced.
- The number of root-projection paths each edit adds to `tests/_baselines/root-install-drift.json`.
- Whether any PoC in a downstream install target is affected (§4 "Effect on existing PoCs").

Every line quoted in §§3–5 and 7 was re-read in the worktree.

## 10. Blockers

None. The P5 escalation of (a), and the tier-1 questions of (b) and (c), are ruling outcomes, not blockers (brief §5).
