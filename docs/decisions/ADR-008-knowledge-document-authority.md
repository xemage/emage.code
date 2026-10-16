# ADR-008 — knowledge-document-authority

> Filename: `ADR-008-knowledge-document-authority.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted. The user approved it on 2026-10-02 ("Accept ADR-008 (Recommended)"), after the three review decisions recorded under § Context. Accepted ADRs are immutable; a change needs a superseding ADR.
  - Drafted for the user's acceptance. Per plan-100 §1 it is "drafted as `proposed`, and the user accepts it before
    it is used".
  - Until it is accepted, no ruling may cite it as authority.
  - Revised to incorporate the user's three review decisions of 2026-10-02 (§ User decisions at review). The final text
    is still subject to the user's acceptance.
- **Date**: 2026-10-02
- **Decider(s)**: solution-architect drafted it. Acceptance is reserved to the user.
- **Tasks**:
  - T581 is this draft.
  - It codifies the bases that T542, T563 (FU-C), T570, T572, T574, T576 and T578 relied on.
  - Once accepted, it makes the parked items P40 and P43 schedulable.
- **Requirements**:
  - `docs/tasks/task-T581.md` §§1–5. §1 quotes the user's decision of 2026-10-02 verbatim.
  - `docs/plans/plan-100-conditional-pass-and-authority-adr.md` §1.
  - `docs/decisions/ADR-007-command-contract-authority.md` (Accepted).
  - `AGENTS.md`.
- **Extends**: ADR-007.
- **Supersedes**: nothing.

## Context

### The gap

ADR-007 settles one kind of conflict: a command's declared contract against the corpus. Its branch 1 also lets
`AGENTS.md`, a `stable` instruction, or another clause of the same command defeat a command clause. ADR-007 does not
rank agent definitions or skills, either against each other or against commands. The rulings that ran into this gap
said so in their own words:

> "Nothing ranks an agent definition against a command, or against an instruction." (`poc-contract-resolution-v1.md`
> §1.4)

> "ADR-007 does not reach skills … I do not rely on "an instruction outranks a skill" anywhere below."
> (`poc-skills-alignment-v1.md` §1.1)

This gap is parked as P34b. Six rulings, spanning seven tasks, worked around it. Each one relied on a basis that had to
be approved, or re-accepted, one ruling at a time:

| Ruling | Basis it relied on | How that basis was made legitimate |
|---|---|---|
| T542: an agent file against `git-workflow` | ADR-007 branch 1, "applied … to an *agent* file, an extension by analogy that branch 1's wording covers but which should be stated rather than glossed" (`completed-tasks.md:343`) | Stated in the ruling itself |
| T563 FU-C: agent outcome vocabulary | The T542 precedent, plus "Each agent also subordinates itself in its own words" (`poc-contract-resolution-v1.md` §9.2) | "Needs explicit orchestrator/user approval" (§6); approved in §9.2 |
| T570: PoC skill files | The T542/FU-C precedent "extended to skills", plus the skills' own descriptions (`poc-skills-alignment-v1.md` §1.2) | "This extension needs the same approval" (§1.2(iii)); approved in §10.2 |
| T572: rival gate-verdict formats | Joint satisfiability, one verdict per gate, and declared scope (`gate-verdict-consistency-v1.md` §1.2) | Accepted per artifact (§13.2) |
| T574: skill against command overlaps | Joint satisfiability; the skill accompanies the command (`poc-skill-command-overlaps-v1.md` §1.2) | Re-accepted per artifact (§16.2) |
| T576/T578: PoC security examples and the PoC reviewer | An instruction states its own precedence and the other concedes; agents subordinate themselves (`poc-security-shortcut-examples-v2.md` §1.2; `poc-security-reviewer-blocking-v3.md` §1.2) | "no ranking is needed", argued afresh each time |

Two items could not be ruled at all, so they were parked behind P34b:
- **P40**: the verdict *criteria* differ across gate documents (`gate-verdict-consistency-v1.md` §13.3: "Resolving this
  needs a ranking, so it **depends on P34b**").
- **P43**: there are two binary PoC verdicts (`poc-skill-command-overlaps-v1.md` §16.3: "Joins **P40** as a
  P34b-dependent item").

### Why this needs an ADR

Three properties make this a decision rather than a tidy-up:

1. **The practice exists, but nothing makes it binding.** Each ruling was legitimate only because of its own approval.
   Nothing guarantees that the next ruling uses the same basis, so there is nothing to audit consistency against.
2. **The tempting shortcuts were refused, one at a time.**
   - Maturity: "**Maturity is not rank.**" (`gate-verdict-consistency-v1.md` §1.1).
   - Category: "I therefore do not rely on "agent outranks command" anywhere below" (`poc-contract-resolution-v1.md`
     §1.4).
   - Convenience: "The brief's preference for editing experimental files is a tie-breaker among readings that are all
     valid. It is not authority." (`poc-skill-command-overlaps-v1.md` §1.1).
   - Popularity: "**popularity is not authority**" (T542, `completed-tasks.md:343`, after ADR-007).

   Each refusal was made locally. None of them binds the next ruling.
3. **The parked items cannot move without a rule.** P40 and P43 each need a choice between documents that the
   self-description basis alone does not settle.

### The user's decision

On 2026-10-02 the user was asked whether to "draft ADR-008 'Knowledge-document authority' (AGENTS.md and stable
instructions first; the command contract governs its output; peers resolved by joint satisfiability, then narrower
scope wins; maturity never ranks; otherwise escalate)?". The user chose **"Draft ADR-008 (Recommended)"**
(`task-T581.md` §1).

This ADR makes those five points precise and grounds each one in what the precedents actually relied on. The user's
answers at review (below) narrowed "narrower scope wins" to the form the precedents support: self-placement.

### User decisions at review (2026-10-02)

The first draft raised three questions. The user answered them on 2026-10-02; the orchestrator relayed the answers
verbatim:

| Question | Answer (verbatim) | Effect on this ADR |
|---|---|---|
| **Q1.** Accept "narrower scope wins by nesting alone", which no decided precedent applied? | **"Self-placement only"** | P3b keeps only the self-placement form. A peer conflict that self-placement cannot decide is escalated (P5). Scope breadth or nesting alone never decides |
| **Q2.** How should `experimental` instructions be placed? | **"Treat as peers (Recommended)"** | An `experimental` instruction outranks nothing until it is promoted. In a conflict it is resolved like a skill or agent: Step A, then Step D, then P5 |
| **Q3.** `AGENTS.md` against a stable instruction? | **"Keep unranked (Recommended)"**. The option's full text was: "Joint satisfiability first. A precedence one declares and the other doesn't contest holds (as security-guidelines vs poc-guidelines did). Otherwise escalate to you. This is conservative and matches every precedent." | They stay unranked. The uncontested-declared-precedence step now applies between `AGENTS.md` and a stable instruction as well as between two stable instructions. The orchestrator made this correction so the ADR follows the option text the user chose (P1 § Within tier 1) |

### Prior ADRs

The orchestrator checked `docs/decisions/` on 2026-10-02. These ADRs exist:
- ADR-001 (cwso-sia-integration);
- ADR-002 (mcp-merge-provenance-tracking);
- ADR-004 (tb-inconclusive-guardrail-demotion);
- ADR-005 (memory-layer-design);
- ADR-006 (gate-g2-routing-target-classes-interpretation);
- ADR-007.

There is no ADR-003 file. None of ADR-001 to ADR-006 addresses document authority. ADR-006 uses "rank" only in an
unrelated routing sense. ADR-007 is the only prior ADR that this one relates to.

## Decision

**When two knowledge documents conflict:**
- **`AGENTS.md` and the `stable` instructions govern within their declared scope.**
- **A command's declared output contract governs that output over any skill or agent applied under it.**
- **Between peers, a conflict exists only if both clauses cannot be obeyed. If they cannot, and one document's own text
  places the subject with the other, that other document governs.**
- **Maturity is never a reason.**
- **Anything these rules do not decide is escalated, not chosen.**

### Scope of this ADR

**Documents covered:**
- `AGENTS.md`. Its root copy is rendered from `implementation/AGENTS.md`, according to the T545 row of
  `completed-tasks.md`.
- The source files under `implementation/knowledge/{instructions,commands,agents,skills}/`.

**Projections.** The installed platform folders are derived, not authored (`AGENTS.md` § Knowledge Base). The source
text is the authority. A projection that differs from its source is a projection defect, not a rival text.

**Not covered:**
- **A document that contradicts itself.** This is resolved by same-file coherence: ADR-007 branch 1's same-file prong
  for commands, and the practice of `poc-skills-alignment-v1.md` §4d and `poc-skill-command-overlaps-v1.md` §1.2(v) for
  other documents.
- **Contract against corpus.** This stays under ADR-007, branches 2–5.
- **A question already settled by an accepted ADR or a recorded user decision.** That decision governs, and documents
  are amended to it. Example: P36 decided `gate-verdict-consistency-v1.md` §4 (V4).
- **Golden cases and protected paths.** `docs/artifacts/protected-paths-v1.md` is unchanged.

### Definitions

**D1 — Stable instruction.**
- **Definition.** A source file under `implementation/knowledge/instructions/` whose frontmatter reads
  `maturity: stable` at the commit the ruling is made on.
- **Source.** This is ADR-007 branch 1's term, read as `poc-contract-resolution-v1.md` §1.1 read it: "Its frontmatter,
  line 4, reads `maturity: stable`, and it is an instruction (`implementation/knowledge/instructions/`)".
- **Today** there are four:
  - `coding-standards`
  - `git-workflow`
  - `poc-guidelines`
  - `security-guidelines`
- **Not stable instructions:** `model-routing-policy` and `mechanical-tier-escalation-policy`, which are both
  `experimental` (`implementation/registry/summary.md`). An `experimental` instruction outranks nothing until it is
  promoted. It is a peer under P3 (user decision Q2).
- **Other categories.** A `stable` command, agent or skill is not a stable instruction. `poc-contract-resolution-v1.md`
  §1.2: "Branch 1 names a stable *instruction*, not a stable *command*."
- **Tier 1** below means `AGENTS.md` together with the stable instructions.

**D2 — Declared scope.** What a document's own text says it governs. It is read from these four sources only:

1. **The frontmatter `description`.** Every category carries one.
2. **The `## Rails` section.**
   - **Inputs** says what brings the document into play.
   - **Out of scope** says what the document excludes.
   - **Failure mode** is not scope.
3. **The `applyTo` glob.** Only instructions carry one.
4. **Explicit sentences in the body** that assign a subject to the document itself or to another document. Examples:
   "is responsible for", "this section summarizes", "feed into", "is governed by", "see X for", or a delegation or
   roster entry that names the other document.

Reading rules:

- **Quotable only.** Declared scope is never inferred from a file's name, maturity, category or executing agent, or from
  how often the file is used.
- **An exclusion beats an inclusion.** An Out-of-scope sentence removes a subject even when `applyTo: "**"` or the
  description would otherwise reach it. Example: `poc-guidelines.md`, despite `applyTo: "**"`, "does not reach"
  production-track work (`poc-skills-alignment-v1.md` §1.4, citing `poc-guidelines.md:15`).
- **`applyTo` filters paths; it does not name subjects.** The description and Rails say which subjects an instruction
  governs. `poc-skills-alignment-v1.md` §1.2(i) puts it this way: "defines its own jurisdiction by subject matter, not
  by file type".
- **Reach can be shown from either side.** Document B is within document A's declared scope if A's text reaches B, or
  if B's own text places itself there (`poc-contract-resolution-v1.md` §1.4; `poc-skills-alignment-v1.md` §1.2(ii)).
- **`AGENTS.md` declares no scope narrower than the repository.** Each of its sentences reaches what that sentence names.
  `poc-skills-alignment-v1.md` §1.3: § Task Protocol "is not scoped to a track, an agent or a file type".
- **Missing Rails.** A file with no `## Rails` is read from sources 1, 3 and 4.
- **Internal disagreement.** If one file's sources disagree with each other, that is a same-file defect and outside this
  ADR.

**D3 — Subject.** The single thing both clauses govern, stated in one phrase. It is one of: a path, a field, a value
set, a format, a criterion, an actor or a step. A conflict about two subjects is two conflicts.

**D4 — Contradiction and specialisation.**
- **Contradiction.** Two clauses contradict when no single output or action can satisfy both, that is, when Step A
  fails.
- **Specialisation.** A clause specialises another, and does not contradict it, when it does one of the following:
  - adds fields, sections, items or renderings that compete with none;
  - fills a slot the other leaves open;
  - uses values that nest inside the other's.
- **Sources** for specialisation (`poc-contract-resolution-v1.md`):
  - §3b: "They add attributes without competing with any, which is a specialisation", and "a specialisation would nest
    inside the parent tiers".
  - §4: a value for `<phase>` "is a specialisation inside `AGENTS.md`'s own slot".

**D5 — Ruling record.** Every ruling made under this ADR records the following:
- the subject (D3);
- both clauses, quoted with file and line;
- the Step A analysis: which MUSTs are involved, whether either is exclusive, and whether one decision could carry two
  values;
- the step that fired;
- for P1–P3, the declared-scope text relied on;
- the amendment, and which file it falls on;
- an explicit statement that maturity was not relied on.

Every precedent already carries these items, as "Authority relied on (quoted)" and "Branch" fields. Making them
mandatory is what makes each principle checkable after the fact.

### P1 — `AGENTS.md` and stable instructions govern within their declared scope

**Rule.** A clause of an agent, skill or command is defective if it contradicts either of these:
- `AGENTS.md`;
- a stable instruction, on a subject within that instruction's declared scope.

The defective clause is amended toward the tier-1 text. Its own maturity does not matter, and neither does what the
corpus does.

**Test.** A ruling under P1 must show all four of the following:
- **(a)** The tier-1 sentence is quoted, and the contradiction is visible in its own text. This repeats ADR-007 § Risks:
  "the contradiction must be quotable".
- **(b)** The subject is within the tier-1 document's declared scope (D2). Reach may be shown from either side.
- **(c)** Step A fails.
- **(d)** The other document is an agent, skill or command. For a command, P1 *is* ADR-007 branch 1, unchanged.

**Remedy.**
- Amend the lower document. Prefer citing the tier-1 text to restating it, so that authority stays in one place. T542:
  "the new prose only restates … what `git-workflow.md` already mandates, and **cites** it, so authority stays in one
  place".
- **This ADR never amends a tier-1 document to match a lower one.** If the tier-1 text is wrong on the merits, the fix
  is a separate instruction-change task, and the lower document is re-checked afterwards.
  `poc-contract-resolution-v1.md` §3b: "ADR-007 decides command contracts and has no branch for amending a stable
  instruction to match a command."

**Within tier 1.** `AGENTS.md` and the stable instructions are **not ranked** against each other. The user decided this
at review (Q3, "Keep unranked (Recommended)"). ADR-007 had left the question open. `poc-contract-resolution-v1.md` §1.3:
"Nothing ranks `AGENTS.md` against a `stable` instruction. ADR-007 lists them side by side, and `AGENTS.md` is silent."
No precedent has ranked them since. Therefore:

- **Stable instruction against stable instruction.**
  1. Apply Step A.
  2. If one instruction declares precedence over the other by name, and the other does not contest it, the declared
     precedence holds. `poc-security-shortcut-examples-v2.md` §1.2: "`security-guidelines` asserts precedence over
     `poc-guidelines` by name. `poc-guidelines` concedes it in its own Rails." … "One side asserts and the other does
     not contest, so again no ranking is needed."
  3. Otherwise, go to P5.
- **`AGENTS.md` against a stable instruction.**
  1. Apply Step A.
  2. If one of them declares precedence over the other by name, and the other does not contest it, the declared
     precedence holds. This is the same rule as for two stable instructions. The user's chosen option for Q3 stated
     it: "Joint satisfiability first. A precedence one declares and the other doesn't contest holds … Otherwise
     escalate."
  3. Otherwise, go to P5.

  `AGENTS.md` names `coding-standards` and `security-guidelines` (§ Code Standards, § Security) but declares no
  precedence either way. None of the four stable instructions declares precedence over `AGENTS.md` in its Rails, read
  at `dd7703b`. Their bodies were not searched, so this is **(unverified)** beyond the Rails.

**Grounded in:**
- **T542** (`completed-tasks.md:343`): "**`ADR-007` branch 1 fires: an agent file contradicted `git-workflow.md`**, which
  is `maturity: stable` with `applyTo: "**"` and whose Rails block states it *"Does not grant any agent, including the
  orchestrator, authority to bypass branch protection for any reason…"*"
- **FU-C** (`poc-contract-resolution-v1.md` §9.2): "The basis is the T542 precedent, where ADR-007 branch 1 was applied
  by analogy to an agent file that contradicted a `stable` instruction." The agents edited, `poc-orchestrator` and
  `evaluation-agent`, are `stable`.
- **T570** (`poc-skills-alignment-v1.md` §10.2): "**Approved: §1.2(iii), extending the T542/FU-C precedent from agent
  files to skill files.** All three skills place themselves inside `poc-guidelines.md`'s reach in their own
  descriptions." Its item (d) "rests on `AGENTS.md` § Task Protocol alone".
- **T578** (`poc-security-reviewer-blocking-v3.md` §1.2): "Each agent is also within the instruction's reach in its own
  terms."
- **Scope limit** (`poc-skills-alignment-v1.md` §1.4): for production-track use of `technical-debt-tracking`,
  "**`poc-guidelines.md` does not reach it** (line 15)".

### P2 — A command's declared output contract governs that output

**Rule.** When a skill or agent is applied under a command, the command's declared output contract governs the output
the command produces. The skill or agent supplies the method. It may specialise that output (D4), but it may not
override it.

**Test.** P2 applies when all three of the following hold:
- **(a) Applied under.** The command names the skill or agent, invokes it, imports its text, or is executed by it through
  its `agent:` frontmatter.
- **(b) Output contract.** The subject is something the command declares it produces: an artifact, path, section,
  field, value set or required item.
- **(c)** Step A fails.

If (b) fails because the subject is a non-output clause of the command, such as a process step or an executor, P2 does
not apply. See P5.

**Remedy.**
- **Amend the skill or agent, not the command.** Scope the amendment to "when run through `/<command>`". Under the
  command, the skill or agent then accompanies or defers to the contract, and its standalone prescription is untouched.
  `poc-skill-command-overlaps-v1.md` E2 and E7 are the models.
- **The command is never amended on the strength of a skill or agent.** ADR-007 branch 1 lists everything that can
  defeat a command clause, and neither a skill nor an agent is on that list.
- **Imported text is a command clause.** Text that a command imports by reference is governed by ADR-007's same-file
  prong, not by P2. `poc-contract-resolution-v1.md` §1.4: "A command imports an agent's text by reference. That makes
  the imported text a clause of the command".

**Grounded in:**
- **ADR-007** § Decision: "A command's declared contract is authoritative over the corpus unless the contract
  contradicts a higher-authority document, or unless the only thing in dispute is a label". When a skill is applied
  under the command, the output it prescribes *is* that corpus.
- **T574** (`poc-skill-command-overlaps-v1.md`):
  - §1.1: "**So branch 1 does not fire, and ADR-007 gives no basis to amend or add to the command.** … ADR-007 also does
    not rank a skill against a command. **No ruling below amends the command.**"
  - F1: the skill's marker "**accompanies** the command's block and carries the same values".
  - E7: the command's checklist items are carried "each worded exactly as the command words it".
- **T572** (`gate-verdict-consistency-v1.md` §6, V7): "A sentence obliging the command to also emit the
  `validation-gates` block would *add* to its contract with no ADR-007 basis."
- **Corroboration, outside the six precedents.** T551 (`completed-tasks.md:354`) gave the `memory-management` skill an
  Authority section that "names the command as authoritative so the two cannot drift again (the T532/skillify
  precedent)".

### P3 — Peers: joint satisfiability, then self-placement

**Peers** are skills, agents and `experimental` instructions, in any pairing: skill and skill, agent and skill, agent and
agent, or any of these against an `experimental` instruction (user decision Q2).

#### P3a — Joint satisfiability (Step A)

Two clauses conflict only if no single output or action can satisfy both. T572 and T574 applied this test in four steps:

1. Quote each MUST.
2. Ask whether either clause is exclusive. A clause is exclusive if it says "only", "instead of", "no other" or
   "replaces", or if it fixes a closed value set for the same field. `poc-contract-resolution-v1.md` §3b: "Rule 2 is a
   closed set".
3. Ask whether one decision would carry two values. All renderings of one decision, such as one gate verdict or one PoC
   outcome, carry one value. If the two clauses can compute different values for the same input, they contradict, even
   when both formats can be emitted.
4. Treat added fields, sections, items and renderings as specialisation (D4).

If both clauses can be satisfied, there is no conflict and nothing is ranked. A ruling then amends at most to state the
relationship where readers will see it. The models are `gate-verdict-consistency-v1.md` E1, E2 and E6, and
`poc-skill-command-overlaps-v1.md` E2 and E7.

Step A needs no rank, so it runs **before every other step, not only between peers**. T576 applied it between a skill
and two instructions, and T572 V7 applied it between a command and a skill.

#### P3b — Self-placement (Step D)

If a real contradiction remains between peers, read both declared scopes (D2) on the subject (D3):

- **Self-placement decides.** P3b fires when one document's own text does either of these on that subject:
  - assigns the subject to the other document;
  - declares itself a summary of, an input to, or a consumer of the other document.

  The other document then governs.
- **Nothing else decides.** If neither document's text places the subject with the other, P3b does not decide. Go to
  P5. This holds even when one scope looks narrower, more specific, or nested inside the other. Scope breadth or nesting
  alone is never a basis (user decision Q1, "Self-placement only").

**Remedy.** Amend the other document to point to the governing one, by name and section. Do not copy the governing
text.
- `poc-skills-alignment-v1.md` §4a: "It names it, so the two cannot drift apart".
- `poc-skill-command-overlaps-v1.md` §1.3: "a copy can drift".

**P3a is grounded in:**
- `gate-verdict-consistency-v1.md` §1.2(i): "**(i) Two MUSTs that can both be obeyed do not conflict.** A ruling needs a
  rank only when two clauses cannot both be satisfied." It also gives the exclusivity test ("It says nothing like
  "only", "instead of" or "no other"") and the one-value test ("the renderings of one gate carry **one value**").
- `poc-skill-command-overlaps-v1.md` §1.2(i): "Two clauses conflict only if they cannot both be obeyed." §1.2(ii):
  "One PoC, one outcome."
- `poc-security-shortcut-examples-v2.md` §1.2: "Replacing the examples makes the skill and both instructions jointly
  satisfiable."

**P3b is grounded in:**
- **T572 V6:** `tech-lead` "this section summarizes" `code-review`.
- **T572 F1:** criteria go to `testing-strategy` and format to `validation-gates`, matching "both skills'
  self-descriptions".
- **T572 V5:** "A name that maps onto none is outside it. That is the skill's own scope statement, not a rank".
- **T574 F3:** "`poc-evaluation:96` already places the ledger items in `technical-debt-tracking`'s hands".
- **T574 F8:** "The label is the `code-review` skill's review-finding scale, used for a review finding. That is its own
  domain".

**Why nesting alone is excluded.** In every decided case, the governed document's own words pointed to the governing
one. Where only nesting was available, the rulings declined to rank and parked the item:
- `gate-verdict-consistency-v1.md` §1.3, Alternative A: "a skill-against-skill (or agent-against-skill) rank and
  therefore P34b. **Not taken.**"
- G1 became P40.
- T574 O2 became P43: "ruling it would decide between two skills on more than a reading. Not ruled."

The first draft offered a nesting form for those cases. The user declined it at review (Q1, "Self-placement only"), so
such cases escalate under P5.

### P4 — Maturity never ranks

**Rule.**
- **(a)** No ruling cites a `maturity:` value as a reason for a clause to govern or to yield.
- **(b)** Promoting or demoting an agent, skill or command changes no ruling.
- **(c)** Maturity appears in exactly one place: D1, which decides whether an instruction is in tier 1. That condition
  is ADR-007's own term, and the user's P1 wording ("stable instructions") repeats it. It decides membership of tier 1.
  It never orders documents within tier 1 or below it.
- **(d)** Several different edits may each be valid on the texts. Maturity, or blast radius, may then choose among them.
  The ruling must show that every alternative is valid without reference to maturity.
- **(e)** ADR-007's companion exclusions also apply unchanged:
  - Counting artifacts is not authority: "Popularity is not authority".
  - Neither is avoiding a golden-coupled or protected file. `poc-contract-resolution-v1.md` §3b: "Taking that route
    *because* it avoids golden edits is exactly the incentive ADR-007 § Context warns about."

**Grounded in:**
- `poc-contract-resolution-v1.md` §1.2: "**Promoting a command to `stable` does not change its rank.**"
- `gate-verdict-consistency-v1.md` §1.1: "**Maturity is not rank.** `validation-gates` being `stable` does not make it
  outrank `code-review` or `testing-strategy`, which are also `stable`, or `tech-lead`, which is `experimental`. I do not
  rely on maturity anywhere."
- `poc-skill-command-overlaps-v1.md` §1.1: "**Maturity is not rank.** … The brief's preference for editing experimental
  files is a tie-breaker among readings that are all valid. It is not authority." This is the source of rule (d).

### P5 — Otherwise escalate

**Rule.** A conflict that Steps A–D do not decide is escalated. It is never resolved by choosing. Escalation includes
these cases:
- a contradiction within tier 1 that neither Step A nor an uncontested declared precedence settles (P1);
- a non-output clause of a command against a skill or agent, which fails P2(b). Example:
  `gate-verdict-consistency-v1.md` G4, the release-gate executor: "This is command against skill and agent, so ADR-007
  is silent on it";
- a command against another command, unless P1 or ADR-007 decides it;
- peers, including `experimental` instructions, whose conflict self-placement (P3b) does not decide. This includes
  cases where one scope merely nests inside the other (Q1).

**Form.**
1. **Report a blocker** under `AGENTS.md` § Blocker Protocol, which says "Agents MUST NOT silently fail".
   - Type: `unclear_requirements`, or `dependency` where another pending decision would settle the conflict.
   - Content: the subject, both quotes, and the step that failed to decide.
2. **Route it.** The orchestrator parks the conflict with a trigger, or puts it to the user.
   - A question that needs a general rule goes to an ADR, as P34b did.
   - A one-off question goes to the user, as P36 did.
3. **Hold the subject.** Until the conflict is decided, neither document is amended on the disputed subject.

**Grounded in:**
- P34b itself.
- P40: "Resolving this needs a ranking, so it **depends on P34b**".
- P43: "Joins **P40** as a P34b-dependent item".
- G4, quoted above.
- The per-case approvals that FU-C and T570 required before dispatch (`poc-contract-resolution-v1.md` §6;
  `poc-skills-alignment-v1.md` §1.2(iii)).

### Order of application

Apply the steps in order. The first step that fires decides the case. P4 constrains every step.

| Step | Principle | Fires when | Outcome |
|---|---|---|---|
| **A** | P3a | Every pair, every time | Jointly satisfiable: no conflict, no rank. At most a note stating the relationship |
| **B** | P1 | A tier-1 text, within its declared scope, against an agent, skill or command; or two tier-1 texts (§ Within tier 1) | Amend the lower document. Within tier 1: an uncontested declared precedence holds, otherwise go to E |
| **C** | P2 | A skill or agent applied under a command, on the command's declared output | Amend the skill or agent, scoped to the command |
| **D** | P3b | Peers (skills, agents, `experimental` instructions) | Self-placement: the document the other's own text points to governs, and the other is amended to point to it. Without self-placement, go to E |
| **E** | P5 | Anything not decided above | Report a blocker and route it to an ADR or the user |

**Why tier 1 comes first.** A command clause that contradicts tier 1 is amended by ADR-007 branch 1 before P2 lets it
govern anything. This is the same order ADR-007 itself uses.

### Relationship to ADR-007

ADR-008 **extends** ADR-007 and supersedes nothing in it. ADR-007 stays Accepted and immutable (`AGENTS.md` § Decision
Log: "Immutable once accepted").

| ADR-007 | ADR-008 |
|---|---|
| Decision sentence: a command's contract is authoritative unless it contradicts a higher authority or disputes only a label | P2 restates it from the side of the skills and agents applied under the command. P2 adds no new way to defeat a command clause |
| Branch 1: `AGENTS.md`, a `stable` instruction, or the same file | P1 is branch 1 extended from command clauses to agent and skill clauses. That extension used to happen by analogy and per-case approval; P1 makes it explicit. The term "stable instruction" (D1) and the quotability mitigation are the same |
| Branch 1 leaves `AGENTS.md` against a stable instruction open (`poc-contract-resolution-v1.md` §1.3) | They stay unranked. Step A, or for two instructions an uncontested declared precedence, settles what it can; the rest goes to P5. This adds a method, not a rank |
| Branches 2–5 and the sibling corollary | Untouched. They still govern contract against corpus |
| §5, "Never resolve by relaxing a check" | Applies unchanged wherever an ADR-008 amendment touches a check |
| "Popularity is not authority" | Carried into P4(e) |

**Non-contradiction check:**
1. ADR-008 adds nothing to branch 1's list of defeaters.
2. P2 and P3 never amend a command.
3. Every command clause that ADR-007 would amend, ADR-008 also amends, because for commands P1 *is* branch 1.
4. No ADR-007 verdict changes as a result.

### Worked examples (illustrative only; they decide nothing)

These examples show where each item would enter the procedure and which question its ruling would have to answer. The
answers belong to the P40 and P43 rulings, once the user has accepted this ADR. Line numbers are at `dd7703b`. The
exception is the `tech-lead.md` and `orchestrator.md` citations, which are taken from `gate-verdict-consistency-v1.md`
and were not re-read at `dd7703b` **(unverified)**.

#### P40 — verdict *criteria* across the gate documents

**Boundary.**
- Whether `CONDITIONAL_PASS` permits a merge is P39, which T580 is deciding in parallel. P40 takes T580's outcome as an
  input and does not re-decide it.
- The verdict *format* was settled by T572 and is not reopened.

| Slice | Clauses (quoted or cited) | Where ADR-008 would start | Question the P40 ruling must answer |
|---|---|---|---|
| **S1. Security findings at any gate** | `security-guidelines.md` Rails `:22–23`: "`SECURITY:CRITICAL`/`SECURITY:HIGH` findings block merge … until resolved", and § Security Review Workflow, which says the same. Against: `validation-gates:67`, CONDITIONAL_PASS "High findings have documented mitigations"; `testing-strategy:240`, security scan CONDITIONAL_PASS "No critical; high findings have mitigations". In line with tier 1: `security-engineer:152`, "`fail` when any unresolved critical or high severity vulnerability remains" | **Step B (P1).** The instruction's description covers "security-sensitive code", and its Review Workflow covers merge requests that touch it. T572 G1 already noted that "The security case alone may rest on the stable instruction" | (1) Is a "documented mitigation" a resolution? (2) Is a `validation-gates` `high` that is a security finding the same as a `SECURITY:HIGH`? If the answers are "no" and "yes", the two skills' CONDITIONAL_PASS rows, as they apply to security findings at merge, contradict tier 1, and P1 amends the skills. Otherwise Step A holds. Either way, the merge effect waits for T580 |
| **S2. Implementation gate, other findings** | `validation-gates:66`: PASS = "No critical or high findings. Medium/low findings noted but non-blocking". `code-review:126–127`: PASS = "No must-fix findings", CONDITIONAL_PASS = "Only should-fix findings". The scales differ: four tiers (`validation-gates:72–77`) against Must/Should/Nice (`code-review:94–98`). G1's example: a lone maintainability concern is PASS under the first and CONDITIONAL_PASS under the second | **Step A.** Are the verdict tables exclusive definitions, so that one finding gets two values? Or are they necessary conditions, so that the most restrictive verdict any applicable table requires satisfies them all? Does "noted but non-blocking" exclude CONDITIONAL_PASS? | If Step A fails, go to **Step D**. `validation-gates:186` (Rails): "defines the verdict process and format, not the review content itself". `code-review:120`: "Code review is the `validation-gates` skill's **Implementation** gate". The ruling must decide whether a verdict-rules table is "process" or "review content". If it is review content, `validation-gates` has conceded it and self-placement (P3b) applies. If not, the slice escalates (P5). That `code-review` names the Implementation gate more specifically than `validation-gates`' five gate kinds does not decide it (Q1). `tech-lead` summarises `code-review` (`tech-lead:29–30`). Its `experimental` maturity is irrelevant (P4) |
| **S3. Integration gate** | `validation-gates:66–68` (generic) and `testing-strategy:221–243` (thresholds; Rails `:14–18`: "defines the plan and thresholds a gate is judged against, not the judgment"), against `qa-engineer:116–120`: `fail` on "Any unresolved critical defect" or "Missing coverage for critical acceptance criteria", and `conditional_pass` for "Only medium/low issues with explicit mitigation and owner" | **Step A.** Coverage thresholds and severity criteria test different inputs and may be jointly satisfiable | If not, go to **Step D**. `qa-engineer` does not name `testing-strategy`, so on the two parties' own texts there is no self-placement between them. `orchestrator.md:210–211` routes the criteria to `testing-strategy` (T572 F1), but that is a third document's assignment. The ruling must decide whether that routing counts as self-placement for the parties (D2 source 4 reads a document's *own* text). If it does not, the slice escalates (P5) |
| **S4. Security gate, medium and low findings** | `security-engineer:153`: `conditional_pass` "only when medium/low findings have owners and remediation windows". `validation-gates:67`: "Medium/low with clear remediation plan" | **Step A.** These are probably two wordings of one condition | Whether "owners and remediation windows" specialises "clear remediation plan" (D4) or contradicts it |

#### P43 — two binary PoC verdicts

**Subject.** Which verdict is the PoC's outcome. Tier 1 already fixes that there is exactly one:
`poc-guidelines.md` Rule 4, "A PoC either validates or invalidates the hypothesis", and the scorecard's single
`## Result`. `poc-skill-command-overlaps-v1.md` §1.2(ii): "One PoC, one outcome."

**Clauses.**
- `rapid-prototyping:122` (`[CHECKPOINT] … verdict=validated|invalidated|in_progress`) and `:127`: "At a trigger, the
  verdict is binary". Its triggers (`:134–137`) include "All success criteria have been tested (regardless of
  outcome)".
- `poc-evaluation:43` (`[VERDICT] … result=VALIDATED|INVALIDATED`) and `:115–117`: "`VALIDATED` only if every success
  criterion … was tested and met"; weak evidence means `INVALIDATED`.
- `/evaluate-poc:31`: "**Status**: VALIDATED | INVALIDATED".
- `evaluation-agent:16`: "Verdict: Validated | Invalidated".
- `poc-orchestrator:38`: "Delegate to `@evaluation-agent` for hypothesis verdict", and `:65`: on timebox expiry,
  "record the verdict `poc-guidelines.md` Rule 3 requires".

How each step would apply:

- **Step B (P1).** Rules 3–4 constrain the *value*: binary, and failed at the deadline. They do not say *which document*
  issues the outcome. P1 probably fixes the constraints but not the issuer. The ruling must confirm this.
- **Step A (P3a).**
  - Both lines can be emitted. The question is whether they can differ for one PoC. They can. A checkpoint at "All
    success criteria have been tested" may carry `validated`, while the evaluation applies `poc-evaluation:115–117`
    (post-hoc criteria, weak evidence) and returns `INVALIDATED`.
  - So Step A holds only if the checkpoint's verdict is a report that the evaluation supersedes. The candidate texts
    are `rapid-prototyping:125` ("This line is a status report, not a checkpoint file") and its Rails `:12` ("does not
    run the PoC evaluation (the poc-evaluation skill)").
  - **The ruling must decide whether that Rails sentence disclaims the *outcome*, which would make self-placement (P3b)
    fire, or only the *activity* of evaluating.** T574 drafted that sentence (E8) and still recorded O2 as open, which is evidence
    that its author did not read it as settling the outcome.
- **Step C (P2).** Under `/evaluate-poc`, the command's `Status` governs the evaluation's rendering. The prototyping
  line is not the command's output, so P2 alone does not decide which verdict is the outcome.
- **Step D (P3b).** The parties are `rapid-prototyping` against `poc-evaluation` (skill against skill), with
  `evaluation-agent` and `poc-orchestrator` also bearing on the subject.
  - **Self-placement candidates.** The first is the `rapid-prototyping:12` Rails sentence, read as disclaiming the
    outcome (see Step A above). The second is `poc-orchestrator:38`, which assigns the "hypothesis verdict" to
    `@evaluation-agent`. That counts only if `poc-orchestrator` is a party, which its `:65` timebox verdict may make it.
  - **Not a basis.** On the descriptions, "Assess proof-of-concept outcomes" (`poc-evaluation`) reads as more specific
    than "scaffolding and integration patterns" (`rapid-prototyping`). That comparison of scopes alone does not decide
    (Q1). If no self-placement text is found, go to P5.

**Possible results, not chosen here:**
1. Jointly satisfiable, with a note.
2. Self-placement names the evaluation documents, and `rapid-prototyping` is amended to point to them.
3. Escalation.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **A. Fixed order by category** (e.g. `AGENTS.md` > instructions > commands > agents > skills) | Mechanical. One lookup | Decides by file type, not by subject. The precedents refused it: "I therefore do not rely on "agent outranks command" anywhere below" (`poc-contract-resolution-v1.md` §1.4). It would let `tech-lead` (an agent) override `code-review` (a skill) on `code-review`'s own subject, against `tech-lead:29–30` | Rejected |
| **B. Maturity ranks** (`stable` beats `experimental`) | Already recorded on every file. Cheap | Refused three times (P4). A promotion would silently rewrite past rulings. It also creates the incentive ADR-007 § Context warns about: a favourable ruling promotes the owner | Rejected by P4 |
| **C. Majority practice** | Easy to measure | "Popularity is not authority" (ADR-007) | Rejected by ADR-007 |
| **D. Status quo**: case-by-case with one-off approvals | Maximally cautious | Every agent or skill ruling waits for an approval. The approvals state no rule, so consistency between them cannot be audited. P40 and P43 stay parked indefinitely | Rejected by the user's decision of 2026-10-02 |
| **E. Broader scope governs** (the general document over the specific one) | One canonical source per area | Inverts every self-placement precedent: T572 F1 routes thresholds to `testing-strategy`, and T574 F8 defers to `code-review`'s scale. Generic documents would have to carry every specific | Rejected |
| **G. Narrower scope governs by nesting alone** (the specific document wins even without self-placement) | Would decide more P40/P43 slices without escalating | No decided precedent applied it, and the rulings that could have applied it declined (§ P3b). It creates a rank that no ruling had used | Rejected by the user at review (Q1, "Self-placement only") |
| **F. Always reconcile, never rank** | No rank ever | Cannot decide a real contradiction, where one decision would carry two values. It becomes the "rubber stamp" ADR-007 §3a warns about | Kept only as Step A |

## Consequences

- **Positive**
  - **One-off approvals become routine.** Once this ADR is accepted, none of the following needs a per-case approval:
    - Applying ADR-007 branch 1 to an **agent** file. T542 did this "by analogy … which should be stated rather than
      glossed". It is now P1.
    - Amending **stable agents** against a stable instruction. FU-C: "Needs explicit orchestrator/user approval". It is
      now P1.
    - Amending **skill files** against a stable instruction or `AGENTS.md`. T570 §1.2(iii): "This extension needs the
      same approval". It is now P1.
    - **Joint satisfiability.** It was accepted per artifact (T572 §13.2, T574 §16.2) and is now standing Step A.
    - The **instruction-against-instruction precedence** argument. T576 and T578 each re-argued that "no ranking is
      needed". It is now the tier-1 rule in P1.
    - **Self-placement between peers** (T572 V6/F1, T574 F3/F8). It is now P3b.
  - **Rulings become auditable.** The D5 record lets a reviewer check which step fired against the quoted text.
  - **P40 and P43 become schedulable.** Each worked example names the step where it enters.
  - **Still not routine:**
    - anything under P5;
    - protected-path grants and evaluator-hash baselines;
    - any change to a tier-1 document's own text;
    - acceptance of this ADR.

- **Negative**
  - **Verbosity stays.** Step A keeps accompanying renderings rather than collapsing them. T572 §1.3 and T574 §1.3 both
    called this "the honest result of obeying every MUST without ranking any of them".
  - **Stable agents and skills can be edited without a per-case approval.** Expect more edits to `stable` files, each
    resting on its D5 record rather than on an approval.
  - **More peer conflicts escalate.** Because self-placement is the only peer tie-break (Q1), some P40 and P43 slices
    will still need an ADR or a user decision. That is intended. It keeps every peer ruling resting on the documents'
    own words.

- **Risks introduced**
  - **Scope gaming (P3b).** A document's description, Rails or body could be rewritten to add or remove a
    self-placement sentence, so as to "win" a pending conflict.
    *Mitigation:* declared scope is read as of the commit on which the conflict was first recorded. A scope edit made
    in the same change as the ruling it would decide cannot be relied on.
  - **The tier-1 loophole (P1).** "It contradicts `AGENTS.md`" stays the branch a motivated reader would reach for, as
    ADR-007 § Risks warned. *Mitigation:* the same quotability test, plus P1(b), the declared-scope test.
  - **Step A as a rubber stamp.** "Both can be emitted" can hide a real criteria conflict. *Mitigation:* the one-value
    test (P3a step 3) is mandatory. P40 S2 is the first case where it bites.
  - **The maturity tie-breaker (P4(d)) as a back door.** *Mitigation:* the ruling must show every alternative valid
    without reference to maturity.

- **Follow-ups**
  - **On acceptance:** the user's acceptance is recorded in this header through a normal MR (`git-workflow.md`).
    Plan-100 §2 then makes P40 and P43 schedulable. P40 slice S1 also depends on T580.
  - **Review questions Q1–Q3** were answered by the user on 2026-10-02 (§ User decisions at review) and are folded
    into this text. The final text still needs the user's acceptance.
  - **No knowledge-file edit follows from this ADR itself.**

## Validation

The decision is correct if all of the following hold. Each is checkable. A failure is grounds to revisit this ADR, not
to work around it.

1. **It reproduces the precedents without approvals.** Re-derived under ADR-008, each precedent reaches its recorded
   outcome at the step shown, and no step needs a one-off approval:

   | Precedent | Step that fires | Outcome (unchanged) |
   |---|---|---|
   | T542: `orchestrator.md` against `git-workflow` | B (P1). The Rails names "the orchestrator" | Amend the agent and cite the instruction |
   | T563 FU-C: `poc-orchestrator`, `evaluation-agent` against Rule 4 | B (P1). Self-subordination (`poc-orchestrator:91–94` at `dd7703b`; the precedents cite it as `:73–76`, its position before the § Security Findings section was inserted) and "a PoC specialist agent" | Amend both stable agents |
   | T570: three PoC skills | B (P1). The skills' own PoC descriptions; item (d) via `AGENTS.md` § Task Protocol | Amend the skills. Production-track reach is denied by D2's exclusion rule, as in §1.4 |
   | T572: verdict formats; V4; V5 | A for V2/V3/V6/V7. V4 is outside this ADR (user decision P36). V5 is outside `validation-gates`' declared scope (D2) | Notes only. V4 amended. V5 unchanged |
   | T574: skill against `/evaluate-poc`; F3; F8 | A and C for F1/F2; D (self-placement) for F3/F8 | Command unchanged. The skill accompanies it and points to the governing documents |
   | T576/T578: PoC security | B within tier 1 (uncontested declared precedence); B (P1) for the skill and the agents | Amend `poc-guidelines`' examples, `rapid-prototyping` and the two agents |

   If any row comes out differently, the ADR has not codified the precedent, and must be revised before acceptance.
2. **ADR-007 is unaffected.** No verdict recorded in `docs/artifacts/command-contract-resolution-v1.md` or in later
   ADR-007 applications changes. This holds by construction, because ADR-008 adds no defeater of a command clause. It
   is to be confirmed on first use.
3. **Rulings carry the D5 record.** The P40 and P43 rulings name a step for every slice, and none cites maturity, corpus
   counts or golden-coupling convenience as a reason. A reviewer can check this from the record alone.
4. **No upward amendments.** No diff made under this ADR changes a tier-1 file to match a lower document, or changes a
   command on the strength of a skill or agent. The exception is a tier-1 file amended under the within-tier rule.
   This can be checked from the file list of each implementing MR.
5. **Step D decides only by self-placement.** Every Step D ruling quotes the governed document's own sentence that
   places the subject with the governing document. A Step D ruling that relies on scope breadth, specificity or nesting
   alone has misapplied this ADR (Q1). Escalation of a P40 or P43 slice that lacks such a sentence is the designed
   outcome, not a failure.
6. **Escalations are visible.** Every P5 outcome appears as a parked item with a trigger, or as a question put to the
   user. None is resolved silently.
