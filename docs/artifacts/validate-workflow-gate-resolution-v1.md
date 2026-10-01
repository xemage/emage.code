# Artifact: validate-workflow-gate-resolution-v1.md

> Filename: `validate-workflow-gate-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T566
- **Created**: 2026-10-01
- **Based on**: `docs/tasks/task-T566.md`; `docs/plans/plan-093-validate-workflow-repair.md`;
  `docs/plans/plan-090-golden-wave-3.md` §2 (P28); `docs/plans/plan-084-round-close-and-fired-triggers.md` §4 (P9,
  P10); `docs/decisions/ADR-007-command-contract-authority.md` (the procedure applied);
  `docs/artifacts/poc-contract-resolution-v1.md` §§1, 9 (the model, and the handling of ADR-007's `proposed`
  status); `AGENTS.md`; `docs/artifacts/protected-paths-v1.md` §5.
- **Supersedes**: none (first version)
- **Decision references**: ADR-007 (applied, not amended). No new ADR is minted.

## 0. What this document is, and what it did not do

This document records one decision: how to repair `/validate-workflow` so that step 5's gate list and step 6's
"Gate produces a VERDICT" stop making `Status: PASS` unreachable. It also specifies the follow-ups that implement
the repair. **It changed no command, skill, agent or golden case.**

**Method and limits.** This session had **no shell**: no `grep`, `cmp`, directory listing, git or test run.
Every claim comes from reading named files directly on branch `agent/solution-architect/T566` (`ed3049d`).
Anything that would need a search or a run is marked **(unverified)** and collected in §7.2.

**Files read (source, not projections):** `implementation/knowledge/commands/validate-workflow.md`;
`implementation/knowledge/skills/validation-gates/SKILL.md`; `implementation/knowledge/skills/plan-approve-execute/SKILL.md`;
`implementation/knowledge/skills/testing-strategy/SKILL.md`; `implementation/knowledge/agents/orchestrator.md`;
`AGENTS.md`; and the planning and decision inputs listed above. Under this task's read-only grant extension I
read `brief.md`, `expect.py`, `case.yaml` and the three fixture files of
`tests/golden/open/validate-workflow-gate-verdict-sources/`. I read no other golden case and nothing under
`tests/golden/held-out/`.

**Line numbers in brief §2.** All checked against source on this branch: `validate-workflow.md:24–32`, `:33–37` and
`:76`; `validation-gates` § Gate Types (`:21–29`) and § Verdict Format (`:31–43`); `orchestrator.md` § Validation
Gates (`:197–222`) and Core Workflow Phase 3 step 1 (`:244`); `plan-approve-execute` Phase 2 (`:79–111`). All
match.

## 1. Authority ordering: what the text establishes

**1.1 What defeats a command clause.** ADR-007 § Decision, branch 1:

> "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the same command file?
> If yes, the command is wrong regardless of what the corpus does. […] A command file may also not contradict
> itself — where it does, the clause the rest of the file and the corpus both disagree with is the defective one."

Three things defeat a command clause: `AGENTS.md`, a `stable` *instruction*, and another clause of the same
command file. ADR-007 lists them side by side and does not rank them against each other. (Brief §3 says it
"ranks" them; strictly, it names each as defeating a command clause. See `poc-contract-resolution-v1.md` §1.3.)

**1.2 What ADR-007 does not rank.** None of the four documents step 5 cites qualifies for the second prong:

| Document | Kind | Maturity | Ranked by ADR-007? |
|---|---|---|---|
| `validation-gates` | skill | `stable` (frontmatter line 4) | **No.** Branch 1 names a stable *instruction*, not a stable skill. |
| `testing-strategy` | skill | `stable` | No |
| `plan-approve-execute` | skill | `experimental` | No |
| `orchestrator` | agent | `experimental` | No (`poc-contract-resolution-v1.md` §1.4) |

**What that means for this ruling.** I cannot argue "the stable skill outranks the command, so the command must
match the skill". Nothing below relies on that. The skills and the agent enter the ruling in exactly one way,
which the command's own text supplies: **they are imported by reference.** Step 5 opens:

> "Gate types, executors and the VERDICT format are defined in the `validation-gates` skill (§ Gate Types, §
> Verdict Format); the orchestrator's invocation points are in the `orchestrator` agent's § Validation Gates.
> Each gate below names where it is defined:"

Each bullet then cites a section. Under `poc-contract-resolution-v1.md` §1.4, the mechanism behind its P11 ruling,
"A command imports an agent's text by reference. That makes the imported text a clause of the command, so branch
1's same-file prong can apply." The same holds for imported skill text. A conflict between imported definitions
and step 6 is therefore a conflict *inside* the command.

The non-ranking has three consequences:

- **Exit 3 has no ADR-007 basis.** ADR-007 decides command contracts. It has no branch for amending a skill or an
  agent to fit a command. `poc-contract-resolution-v1.md` §3b reached the same conclusion for a stable
  instruction: "ADR-007 gives no path for bending a stable instruction toward a command."
- **The skill's stable maturity does not decide anything here.** I leave `validation-gates` unchanged because
  nothing in it is defective, not because it outranks the command.
- **The omitted Architecture gate type is a same-file defect, not a rank defect.** See §2, C2.

**1.3 `AGENTS.md` is corroboration, not the prong that fires.** `AGENTS.md` § Validation Gates (`:51–55`) says:

> "VERDICTS: `PASS` | `CONDITIONAL_PASS` | `FAIL` […] `FAIL` blocks progression. Orchestrator creates fix tasks
> and re-routes."

§ Skill Workflow (`:67`) names `validation-gates` as the required skill for "Phase or validation transition". Both
fit treating plan approval (Approve / Revise / Reject) as something other than a validation gate. Neither says
"only things that emit these verdicts are gates", and neither enumerates gates. Consistent with
`poc-contract-resolution-v1.md` §3a ("It does not say 'only ADRs', so I do not treat it as a branch-1
contradiction"), **I do not invoke the `AGENTS.md` prong.**

**1.4 ADR-007 is still `proposed`.** Its header reads "**Status**: proposed". I follow
`poc-contract-resolution-v1.md` §9.1: ADR-007 is used **as a procedure**, and authority is taken directly from the
quoted text. Here that text is the command's own clauses. Formal acceptance is parked as P34. **Not a blocker.**

**1.5 What kind of conflict this is.** It is *contract against contract*, not contract against corpus. No
`/validate-workflow` output exists. The case brief records `grep -rl 'WORKFLOW VALIDATION VERDICT' … -> 0 matches`
(**unverified** by me). Branch 1 still applies, because it fires "regardless of what the corpus does".

## 2. The defect, stated as quotable clauses

`validate-workflow.md` contains two same-file contradictions.

**C1: step 5's first two bullets against everything else.**

| Clause | Text (verbatim) | What it implies |
|---|---|---|
| Step 5, bullets 1–2 (`:25–26`) | "Plan approval gate — `plan-approve-execute` skill § The Three Phases › Phase 2: Approve" / "Architecture briefing gate — `orchestrator` agent § Core Workflow › Phase 3: Development, step 1" | These two are gates |
| Step 5, closing sentence (`:32`) | "The first two are workflow steps, not among the `validation-gates` skill's five gate types." | **They are not gates of the kind the step defines** |
| Step 5, opening (`:24`) | "Gate types, executors and the VERDICT format are defined in the `validation-gates` skill (§ Gate Types, § Verdict Format)" | A VERDICT is the skill's format, whose `**Gate:**` field admits `architecture \| implementation \| integration \| security \| release` only |
| Step 6 (`:33–35`) | "For each gate, verify: […] Gate produces a VERDICT" | Every listed gate must produce one |
| Rails Failure mode (`:76`) | "If any gate […] doesn't produce a VERDICT […] the overall VERDICT is FAIL" | Bullets 1–2 force `FAIL` |
| Step 11 (`:53`) | "**Status**: PASS \| CONDITIONAL_PASS \| FAIL" | `PASS` is a declared outcome |

All the clauses after bullets 1–2 agree with each other: step 5's opening, its closing sentence, step 6, the
Failure mode and step 11. Bullets 1–2 disagree with every one of them. The imported definitions agree too:
`plan-approve-execute` Phase 2 declares "Approve / Revise / Reject", and Phase 3 step 1 declares no output. There
is no output corpus to consult (§1.5). Under ADR-007's tie-break ("the clause the rest of the file […] disagree[s]
with is the defective one"), **the defective clause is step 5's bullets 1–2, not step 6.**

**C2: step 5's "all" against its own list.** Step 5 is headed "**Check all validation gates.**" and defines gate
types by importing `validation-gates` § Gate Types. That table has five rows: Architecture, Implementation,
Integration, Security, Release. The list cites four of them and **omits Architecture**, as brief §2 records. The
defective clause is the list's omission.

The repair fixes the list, and only the list.

## 3. The exits, each with its branch and reasons

Every exit is tested against the same branch. Branch 1 (same-file prong) fires on C1 and C2. The real question is
which clause each exit amends, and whether that is the defective one.

### Exit 1: scope step 6's VERDICT requirement to the real gates; keep the two workflow steps with lighter checks

| | |
|---|---|
| **Branch** | 1, same-file. **It amends the wrong clause.** It edits step 6 and the Failure mode, which agree with the rest of the file, and keeps bullets 1–2, which the rest of the file disagrees with. |
| **For** | Smallest change in spirit. It matches one reading of the author's intent: the closing sentence shows that whoever wrote it knew the two steps were not gates and kept them anyway. |
| **Against** | (1) ADR-007's tie-break picks the clause the rest of the file disagrees with. That is bullets 1–2, not step 6. Authorial intent is not part of the test. (2) **It is a relaxation under ADR-007 §5.** It narrows a universal requirement ("For each gate") to a subset so that the check can pass. The golden case's assertion would have to become "every listed *verdict* gate produces a VERDICT", which is true by construction for the four skill rows. That is the "loosening a regex" pattern. (3) It needs edits to two clauses (step 6 and the Failure mode), and it invents "lighter checks" that no quoted text supports. (4) It leaves C2 in place: the Architecture gate type stays unchecked. (5) Step 11's "Gates validated: <count>/<total>" becomes ambiguous over a mixed list. |
| **Verdict** | **Rejected.** |

### Exit 2: replace the architecture briefing with the VERDICT-producing architecture gate; decide plan approval

| | |
|---|---|
| **Branch** | 1, same-file. **It amends the defective clause.** It corrects step 5's list (C1 and C2) and leaves step 6, the Failure mode and step 11 untouched. |
| **Which architecture citation** | **The skill's § Gate Types row, `**Architecture**`.** The orchestrator's ARCHITECTURE GATE is the *invocation* of that same gate, and step 5's opening already imports "the orchestrator's invocation points". Citing the row makes the new bullet identical in form to the other four. There is also a mechanical reason. The orchestrator's ARCHITECTURE GATE is a bold paragraph, not a heading, table row or numbered step, so `expect.py`'s `_select` has no selector that resolves it. Citing the whole § Validation Gates section (`selector=None`) would match "VERDICT" for any gate cited to it, and the check would no longer discriminate. The skill row resolves exactly and is the stricter citation. "Both" adds nothing the opening does not already say. |
| **Plan approval: options** | **(i) Delete it from the gate list.** **(ii) Keep it as a gate:** the case stays red, so this repairs nothing. **(iii) Move it to a new, separate list of non-gate workflow checks with its own verifications:** see Exit 4. |
| **For** | Edits one clause, the list, and converts the closing sentence's concession into an explicit statement. Keeps step 6's universal requirement at full strength. Fixes C2 at the same time: the list becomes exactly the skill's five gate types. Supplies the Architecture gate, which the orchestrator's Core Workflow already invokes: Phase 1 step 6, "Run **Architecture Gate** before proceeding", which satisfies step 6's reachability verification. The briefing's own concern ("confirm API boundaries and ownership") is still validated by the command, under step 3's "API contract parity" handoff check. |
| **Against** | `/validate-workflow` stops checking plan approval at all. **This is the most contestable part of the ruling** (see the Decision). |
| **Verdict** | **Chosen, with plan-approval option (i).** |

### Exit 3: give the two workflow steps verdicts

| | |
|---|---|
| **Branch** | **None.** Branch 1 decides which *command* clause is defective. It has no path for amending `plan-approve-execute` or `orchestrator` to fit the command (§1.2). This is the "recorded alternative" pattern in `poc-contract-resolution-v1.md` §§3b and 5. |
| **For** | Keeps all six bullets. The case's own discrimination note shows `check()` turns `True` when "Produce VERDICT." is appended to both definitions, so it is the cheapest route to green. |
| **Against** | (1) **That cheapness is the incentive ADR-007 § Context warns about.** It turns the case green by editing the definitions the case reads, not the contract under test. (2) **Rival conventions.** Plan approval already has *two* vocabularies: parked P10 sets `new-project`'s APPROVED / APPROVED_WITH_CHANGES / REJECTED against `plan-approve-execute`'s Approve / Revise / Reject. Adding PASS / CONDITIONAL_PASS / FAIL to the same user decision makes three. ADR-007 Alternative C: "A shipped, user-facing command that declares two acceptable output forms is worse guidance than one that declares one." (3) **Category error.** The `validation-gates` Verdict Format needs an `**Executor:** <agent-name>`, and its Guidelines say "Gate executors should not review their own work". Plan approval's decider is the user, who is not an agent. The briefing's participants include `@solution-architect`, who authored the architecture being briefed. (4) A real verdict in the skill's format would need a sixth `**Gate:**` kind, which means editing the `stable` `validation-gates` skill as well. (5) Blast radius: `plan-approve-execute` and `orchestrator` are consumed by other commands and agents (**unverified**; needs a `grep`). |
| **Verdict** | **Rejected.** |

### Exit 4 (additional): Exit 2, plus a separate "workflow checkpoints" list for plan approval with its own verifications

| | |
|---|---|
| **Branch** | 1 for the list correction (as in Exit 2). The new list is **not** a contract correction: no clause in the file demands it. |
| **For** | Keeps plan-approval coverage. Plan approval would satisfy reachability, blocking ("Never execute without an approved plan") and escalation (Revise / Reject). |
| **Against** | It adds new contract surface and new verification criteria that no quoted authority supplies. It expands the command's Validation Scope (steps 1–4 do not mention plan protocol), which is a scope decision for the command's owner and the Product Owner, not an ADR-007 correction. Done inside this repair, it resembles ADR-007 §5's "admitting a second form for convenience". |
| **Verdict** | **Not taken here. Parked** as a scope question (§6, item S1). If it is wanted, it should be added later as its own step, with quoted authority. |

### Exit 5 (additional): reclassify the case as `capability_gap` (branch 4)

**Rejected.** Branch 4 is for "a hand-authored fixture built to violate a rule". This fixture is real, and the
defect is real: a self-contradicting contract. ADR-007 Alternative D calls this move "the 'relax until it passes'
failure mode wearing a taxonomy disguise".

### Exit 6 (additional): drop `PASS` from step 11's Status

**Rejected.** It would encode the defect as the contract, which the case brief's "Why the case has no
hand-authored report" section already rejects in another form.

## 4. Decision

**Amend `/validate-workflow` step 5's gate list (ADR-007 branch 1, same-file prong). The list becomes exactly the
`validation-gates` skill's five gate types, each citing its § Gate Types row, in the skill's pipeline order. The
architecture briefing is replaced by the Architecture gate. Plan approval is removed from the gate list. The
closing sentence keeps its classification of both as workflow steps and now states the consequence. Step 6, the
Failure mode and step 11 are unchanged.**

**Authority relied on (all quoted in §§1–2):**
- ADR-007 branch 1: "A command file may also not contradict itself — where it does, the clause the rest of the
  file and the corpus both disagree with is the defective one."
- The command's own clauses at `:24`, `:32`, `:33–35`, `:53` and `:76`, against bullets 1–2 (C1).
- Step 5's "Check all validation gates" plus its import of § Gate Types, against the four-of-five list (C2).
- The imported definitions enter only as clauses of the command (§1.2), never as ranked authorities.

**What the ruling does to promotion.** It is promotion-favourable: it removes the only red case on
`/validate-workflow`. I own no part of `/validate-workflow` (`agent: "orchestrator"`). Following ADR-007's own
practice, I state the most contestable part prominently:

- **The contestable part:** plan approval leaves the command's coverage entirely.
- **Alternative reading:** Exit 4 keeps that coverage.
- **Cost of the alternative:** new criteria with no quoted authority, and a scope expansion that is not mine to
  decide.
- **Cost of taking Exit 3 instead:** a third approval vocabulary (P10 worsens) and edits to two documents ADR-007
  does not govern.

**ADR-007 corollary.** No paired sibling is known: the case brief names none, and I may not read other cases
(**unverified**). The nearest corollary row is "1, where the amendment changes only a *name or path*" → the case
survives, with its mirrored list updated. The case also flips green (§5c).

## 5. Implementation specification

### (a) Exact command change: `implementation/knowledge/commands/validate-workflow.md`, lines 25–32

Line 24, step 5's opening, is **unchanged**.

**Before (lines 25–32, verbatim):**

```
   - Plan approval gate — `plan-approve-execute` skill § The Three Phases › Phase 2: Approve
   - Architecture briefing gate — `orchestrator` agent § Core Workflow › Phase 3: Development, step 1
   - Integration checkpoint gate — `validation-gates` skill § Gate Types, **Integration**
   - Code review gate — `validation-gates` skill § Gate Types, **Implementation**
   - Security audit gate — `validation-gates` skill § Gate Types, **Security**
   - Release gate — `validation-gates` skill § Gate Types, **Release**

   The first two are workflow steps, not among the `validation-gates` skill's five gate types.
```

**After (replaces lines 25–32 exactly):**

```
   - Architecture review gate — `validation-gates` skill § Gate Types, **Architecture**
   - Code review gate — `validation-gates` skill § Gate Types, **Implementation**
   - Integration checkpoint gate — `validation-gates` skill § Gate Types, **Integration**
   - Security audit gate — `validation-gates` skill § Gate Types, **Security**
   - Release gate — `validation-gates` skill § Gate Types, **Release**

   These are the skill's five gate types, in the order of its § Procedures › 4. Gate Pipeline for a Release. Plan approval (`plan-approve-execute` skill § The Three Phases › Phase 2: Approve, a user decision: Approve / Revise / Reject) and the architecture briefing (`orchestrator` agent § Core Workflow › Phase 3: Development, step 1) are workflow steps, not validation gates, and are not checked here.
```

**Notes for the implementer (nothing below is left to choose):**
- The separator in each bullet is ` — ` (space, U+2014 EM DASH, space), as in the existing bullets. The golden
  parser in (c) depends on it.
- **The new bullet's name is exactly `Architecture review gate`.** It follows the pattern of "Code review gate"
  and the orchestrator's "Review architecture-v1.md…".
- **Order:** Architecture → Implementation → Integration → Security → Release, matching `validation-gates`
  § Procedures › 4 ("Architecture Gate → Implementation Gate → Integration Gate → Security Gate → Release Gate").
  This also reverses today's Integration-before-Code-review order.
- The three unchanged bullets keep their names and citations byte-for-byte. Only the "Code review gate" line moves.
- No other line of the file changes. The file shrinks by one line, so step 6 moves from `:33–37` to `:32–36` and
  the Failure mode from `:76` to `:75`.
- **Regenerate** with `node implementation/scripts/sync.mjs --root implementation` and
  `python3 implementation/scripts/generate-registry.py`. Confirm with both `--check` modes. Top-level platform
  folders are refreshed only by `scripts/install.sh`, and running that is a separate user-approved step (the
  parked root-drift item). Never hand-edit them.

### (b) Consequential edits to step 6's other verifications and the Failure mode

**None.** Step 6's four verifications, the Rails Failure mode and step 11's template stay as they are. Here is why
each still holds over the five gates:

| Verification | Satisfiable for all five? | Source (corroboration, not rank) |
|---|---|---|
| Reachable in workflow | Yes. Architecture: `orchestrator` Phase 1 step 6. Integration: Phase 3 step 4. Security: Phase 4 step 3. Release: Phase 5 step 4. Implementation: § Validation Gates "IMPLEMENTATION GATE (after core implementation)" and Phase 3 step 3, "delegate to **@tech-lead** for code review". See §6 F2 for a weakness. | `orchestrator.md:201–217, 234, 249–250, 255, 261` |
| Produces a VERDICT | Yes, all five are skill rows admitted by the Verdict Format | `validation-gates` `:21–43` |
| Blocks on FAIL | Yes | `AGENTS.md:54`; `validation-gates` § Procedures 2 and 4 |
| Escalation path defined | Yes | `orchestrator.md:219–222` ("FAIL → Create fix tasks…"), § Blocker Handling |

`Gates validated: <count>/<total>` now has `<total> = 5`. That needs no wording change. **`Status: PASS` becomes
reachable in principle**, which is the point of the repair.

### (c) Golden coupling: `tests/golden/open/validate-workflow-gate-verdict-sources/`

**`expect.py`: required changes.**

1. **`GATES`**: replace it with exactly these five entries, in this order:
   ```python
   GATES = {
       "Architecture review gate": (VG, ("## Gate Types",), "row:Architecture"),
       "Code review gate": (VG, ("## Gate Types",), "row:Implementation"),
       "Integration checkpoint gate": (VG, ("## Gate Types",), "row:Integration"),
       "Security audit gate": (VG, ("## Gate Types",), "row:Security"),
       "Release gate": (VG, ("## Gate Types",), "row:Release"),
   }
   ```
   Remove the then-unused `PAE` and `ORCH` constants. Add `CMD = KNOWLEDGE / "commands/validate-workflow.md"`.

2. **Per-gate predicate**: **unchanged.** `_unfenced_lines`, `_section`, `_select`, `_verdict_gate_kinds`,
   `gate_produces_verdict`, `VERDICT_WORD_RE` and `GATE_FIELD_RE` stay byte-for-byte, including the lenient (b)
   path, so the value constraints are identical.

3. **New completeness predicate** (required). The set of `row:` keys in `GATES` (lower-cased) must **equal**
   `_verdict_gate_kinds(vg_text)` read from the fixture, and that set must be non-empty. This makes "Check all
   validation gates" mechanical: a list that omits any gate kind the Verdict Format admits fails. Today's check
   cannot detect that omission, which is the Architecture omission brief §2 found.

4. **New list-fidelity predicate** (required).
   - Read the fixture copy of `CMD`.
   - Find the first unfenced line starting with `5. **Check all validation gates.**`.
   - Collect each subsequent line matching `^   - (.+?) — ` (three spaces, hyphen, space; the separator is
     U+2014). Stop at the first line matching `^\d+\. `.
   - The ordered list of captured names must **equal** `list(GATES)`.

   This ties the check's list to the command's list, so the mirror cannot drift silently. A command that re-adds a
   non-verdict step as a gate fails: either the list is no longer equal, or, if `GATES` follows, the per-gate
   predicate fails.

5. `check()` returns `all(per-gate) and completeness and fidelity`. `main()` prints each per-gate line plus one
   line each for completeness and fidelity. Update the module docstring: five gates, the two new predicates, and
   "Expected today: True (expected_pass), resolved by `validate-workflow-gate-resolution-v1.md`".

**Fixture.**
- **Add** `fixture/implementation/knowledge/commands/validate-workflow.md`, a byte-identical copy of the
  **amended** source from (a). Confirm with `cmp`.
- **Keep** `fixture/implementation/knowledge/skills/validation-gates/SKILL.md` unchanged. Re-confirm it is
  byte-identical to source with `cmp`. It looks identical on reading (**unverified**: no `cmp`).
- **Delete** `fixture/…/skills/plan-approve-execute/SKILL.md` and `fixture/…/agents/orchestrator.md`. After (a),
  no bullet cites them and `check()` reads neither. Keeping them would leave the provenance statement ("copies of
  the files step 5 cites") false. Before deleting, check that no suite-format test requires a fixed fixture file
  set (**unverified**).

**`brief.md`: rewrite to the corrected contract.**
- Change the header to `(expected_pass)`.
- Quote the **amended** step 5 and the unchanged step 6 and Failure mode verbatim.
- Replace the Result table with five rows, all "Yes, by (a)", plus the two new predicates.
- Replace "Why `tracked_defect`, and why this case does not resolve it" with a short "Resolution" section. It
  should cite this artifact, ADR-007 branch 1 (same-file prong, C1 and C2), and the reasoning in "Validation 1"
  below.
- Keep "Why the case has no hand-authored report" and "Readings deliberately not asserted" as they are. Add a
  note that the (b) path is unused by the current five rows but kept so that the predicate is unchanged.
- Update the Provenance section: two fixture files, the `develop` SHA they were copied at, and why two copies were
  removed.
- Re-derive the Discrimination section on temp copies. **It must show `True` on the fixture and `False` for each
  of the following:**
  1. the old Plan approval bullet re-inserted into the fixture command's step 5 (fidelity);
  2. the Code review and Integration bullets swapped in the fixture command (ordered fidelity);
  3. the `Architecture review gate` entry removed from `GATES` in a temp `expect.py`, with the matching bullet
     removed from the fixture command (completeness);
  4. `architecture` removed from the skill's `**Gate:**` field (per-gate and completeness);
  5. the Architecture row deleted from § Gate Types (per-gate);
  6. "Every gate MUST produce a verdict" removed (per-gate);
  7. the Release row deleted (carried over from the current brief).

**`case.yaml`.**
- Set `status: expected_pass`.
- Delete `known_failing_category` and `known_failing_reason`.
- Remove the tag `contract-self-contradiction`, which would no longer be true. Keep the other tags.
- Match the field shape of an existing `expected_pass` `case.yaml`. The orchestrator should name one in the FU-2
  brief, because the grant does not cover reading other cases.

**Does the case flip to `expected_pass`?** **Yes.** By reading the code (not by running it, **unverified**):
- `_select` matches `| **Architecture** | …` at `validation-gates:25`, and `architecture` is in the
  `**Gate:**` kinds, so all five per-gate checks return `True` by (a).
- The `row:` keys equal the five Verdict Format kinds, so completeness holds.
- The amended step 5 bullets equal `list(GATES)` in order, so fidelity holds.

**ADR-007 §5 and Validation 1: why this is a corrected contract, not a relaxed one.** Validation 1 requires that
"the replacement `expect.py` requires the same number of structural elements with the same ordering and value
constraints […] A follow-up that produces a shorter required-field list has violated §5".

| | Today | After |
|---|---|---|
| Per-gate VERDICT predicates | 6, two of them structurally unsatisfiable against the shipped definitions | 5, with the identical predicate |
| Completeness (all skill gate kinds listed) | none | 1 |
| List fidelity (the check's list is the command's list, in order) | none | 1 |
| Value constraints on a per-gate pass | (a) or (b) | (a) or (b), unchanged |
| Ordering | not enforced | enforced |

- **The removal follows from the contract, not from the check's convenience.** `GATES` is a mirror of step 5,
  not a list of fields the check imposes. Step 5 changed under branch 1 for quoted reasons (§2). The mirror
  follows, as ADR-007's corollary prescribes for amended contracts ("fixture/glob updated to the amended form").
  §5 itself permits re-authoring "to a corrected contract".
- **No real defect goes undetected.** Against the shipped definitions, the old check's two dropped entries could
  fail in one way only, and the case brief says so itself: they fail "regardless of the workflow's actual
  health". They carried no information about the workflow. The only thing they detected was the command's
  self-contradiction, which is now removed at its source.
- **The new check detects defects the old one could not.** It catches a step 5 that omits any gate kind (today's
  Architecture omission was invisible to the old check), a step 5 whose list drifts from `GATES`, and a
  non-verdict step re-added as a gate. The set of *verdict-producing* gates checked grows from four to five.
- **Honest weakness.** A literal reader who counts per-gate entries will see six become five. Validation 1's own
  heading is "No check is weaker", and on the substance the check is stronger: seven predicates instead of six,
  plus enforced ordering. **The reviewer should rule on this explicitly**, as `poc-contract-resolution-v1.md`
  §9.2 did for its own count change.

**Suite consequences (orchestrator to verify).**
- `expect.py` changes, so the evaluator hash moves and a **user-authorized baseline** is required. plan-093 §2
  says this is v15 (**unverified**).
- ADR-007 Validation 2: `scripts/scorecard.py` must report **exactly one** transition, this case going from
  `known_failing` to `expected_pass`, and nothing else.
- The `known_failing` population drops by one. Check it against the `tests/golden/README.md` floor of
  "≥5 `known_failing`" (current count **unverified**).

### (d) Follow-up tasks

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Depends on / notes |
|---|---|---|---|---|---|
| **FU-1**: amend `/validate-workflow` step 5 | (a) | `implementation/knowledge/commands/validate-workflow.md` (lines 25–32 only); regenerated mirrors under `implementation/.<platform>/`; `implementation/registry/index.json` via the generator | **No** | Backend Developer | None. On its own it leaves the case red and its brief stale, because the case reads frozen copies. No verbatim-quote test exists (`poc-contract-resolution-v1.md` §9.1), so it is safe to land alone. |
| **FU-2**: realign the golden case | (c) | `tests/golden/open/validate-workflow-gate-verdict-sources/{expect.py,brief.md,case.yaml}`; `fixture/implementation/knowledge/commands/validate-workflow.md` (add); `fixture/…/skills/plan-approve-execute/SKILL.md` and `fixture/…/agents/orchestrator.md` (delete); `fixture/…/skills/validation-gates/SKILL.md` (re-confirm only) | **Yes.** `protected-paths-v1.md` §5, scoped to this one case directory. No other case and no `held-out/` access, except reading one named `expected_pass` `case.yaml` as a shape template if the orchestrator grants it. | QA Engineer | Depends on FU-1, because the fixture copy must be the amended bytes. Can share FU-1's MR if copied from the same tree and confirmed with `cmp`. Needs the user-authorized baseline (v15 per plan-093). Afterwards, re-run `scripts/scorecard.py` and confirm exactly one transition. |
| **FU-3**: promotion pass for `/validate-workflow` | plan-093 §2, third bullet | the command's frontmatter `maturity:`, per `maturity-promotion-criteria-v1.md` (not read here) | **No** | as plan-093 assigns | Depends on FU-2 and the baseline. Whether a green case is the only remaining criterion is **unverified** (brief §1 and plan-093 assert it). The `orchestrator` agent stays blocked regardless (plan-093 §1). |

**No skill or agent edits** are part of this repair. **One protected-path authorization** in total (FU-2).

## 6. Findings outside scope

These are not decided here. They are candidates for parking.

- **S1: plan-approval coverage (scope question).** If `/validate-workflow` should validate plan approval as a
  *non-gate* workflow control (Exit 4), the command's owner and the Product Owner should add it as its own step,
  with quoted authority and its own criteria. It interacts with P10, because the approval vocabulary is not yet
  unified.
- **F1: two VERDICT formats for the integration gate (both `stable` skills).**
  - `validation-gates` § Verdict Format: `## Gate Verdict` with `**Gate:** integration`.
  - `testing-strategy` § Protocol-Aware Enhancements: `[VERDICT] gate=qa-validation | result=…`.
  - `orchestrator.md:210–211` routes the INTEGRATION GATE's criteria to `testing-strategy`.

  The same shape of rival convention, but between two skills, which ADR-007 does not reach.
- **F2: the Implementation gate is not named in the orchestrator's Core Workflow.** Phase 3 step 3 says "delegate
  to **@tech-lead** for code review". It never says "Run **Implementation Gate**", unlike the other four. A strict
  `/validate-workflow` run could flag step 6 "reachable in workflow" on it, so in practice `PASS` could still
  depend on how a validator reads that step. The golden case does not assert reachability.
- **F3: executor mismatch for the Architecture gate.** `validation-gates` names Tech Lead. `orchestrator`
  § Validation Gates delegates to `@tech-lead` **and** `@security-engineer`. This reads as a specialisation, not a
  contradiction. Noted only.
- **F4: another plan-path variant.** `validation-gates` § Gate Input Requirements › Architecture Gate cites
  `docs/plans/plan-<feature>.md`. This belongs to the parked P32 family.

## 7. Hand-back lists

### 7.1 Corrections to the brief (all `unclear_requirements`, severity `minor`)

1. §3: "ADR-007 ranks `AGENTS.md`, a `stable` instruction, and another clause of the same command file". ADR-007
   names each of these as defeating a command clause. It does not rank them against each other (§1.1).
2. §2, row 4, omits that the orchestrator's Core Workflow invokes the Architecture Gate at **Phase 1 step 6**
   ("Run **Architecture Gate** before proceeding"). That invocation is what satisfies reachability for the chosen
   exit.
3. §3, Exit 2, offers "the orchestrator's **ARCHITECTURE GATE**" as a possible *citation*. As a citation it is not
   resolvable by `expect.py`'s selectors: it is a bold paragraph, not a heading, row or step. Citing its whole
   section would make the check non-discriminating (§3, Exit 2). It is the gate's invocation, not its definition.
4. §2's facts were verified on `42617db`. This worktree is at `ed3049d`. I assume the intervening commits are
   docs-only, which is **unverified**.

### 7.2 Unverified claims (need a shell)

1. The three fixture files are byte-identical to source (I compared by reading: `validation-gates` in full,
   `orchestrator.md:190–269`, `plan-approve-execute:75–114`). Needs `cmp`.
2. `42617db..ed3049d` touches none of the cited files.
3. No other golden case targets `/validate-workflow` or quotes step 5. I was not permitted to look.
4. The case brief's `grep … 'WORKFLOW VALIDATION VERDICT'` → 0 still holds.
5. The current `known_failing` count against the README floor of ≥5.
6. The baseline number (v15) and the evaluator-hash mechanics.
7. The field shape an `expected_pass` `case.yaml` needs.
8. No test outside `tests/golden/` depends on this case's fixture file set.
9. FU-2's `check()` returns `True`. Predicted from reading the code, not from a run.
10. The consumers of `plan-approve-execute` and `orchestrator` (the blast-radius argument against Exit 3).
11. Nothing else in the repository (docs, README, other commands) quotes step 5's six-gate list. Needs `grep -rn
    "Architecture briefing gate\|Plan approval gate"` outside `tests/golden/`.
12. A green golden case is the only remaining promotion blocker for `/validate-workflow`.

### 7.3 Blockers

None.

## 8. Summary

| Item | Value |
|---|---|
| Branch that fires | ADR-007 branch 1, **same-file prong** (C1: bullets 1–2 against step 5's opening and closing sentences, step 6, the Failure mode and step 11; C2: "all validation gates" against a four-of-five list) |
| Decision | Exit 2: step 5 lists exactly the skill's five gate types in pipeline order; the briefing is replaced by `Architecture review gate`; plan approval leaves the gate list; step 6, the Failure mode and step 11 are unchanged |
| Rejected | Exit 1 (amends the wrong clause, and is a §5 relaxation); Exit 3 (no ADR-007 basis, a third approval vocabulary, a category error); Exit 5 (taxonomy disguise); Exit 6 (encodes the defect) |
| Parked | Exit 4 / S1 (plan-approval coverage as a scope question); F1–F4 |
| Golden | `GATES` 6 → 5, plus completeness and ordered list-fidelity predicates; fixture: add the amended command copy, delete two now-uncited copies; flips to `expected_pass`; needs one grant and one baseline |
| Follow-ups | FU-1 (command, no grant), then FU-2 (golden, grant), then FU-3 (promotion pass) |

## 9. Orchestrator verification and rulings (added before commit, 2026-10-01)

*Added by the orchestrator, not the producing agent, on `develop` `ed3049d`. It settles the items marked
(unverified) above and rules on the question §5(c) leaves to the reviewer. §§0–8 are unchanged.*

**9.1 Unverified claims, checked**

| Claim | Result |
|---|---|
| The fixture copies are byte-identical to source | `cmp`: all three are identical. **Confirmed.** |
| `42617db..ed3049d` touches none of the cited files | Only `plan-093`, `active-tasks.md` and `task-T566.md` changed. **Confirmed.** |
| No other golden case targets or quotes `/validate-workflow` | No hit in `tests/golden/open/` outside this case. **Confirmed.** |
| The "WORKFLOW VALIDATION VERDICT" grep returns 0 | **Corrected: it returns 2,** and both are documents that *mention* the block: this artifact and the case's own `brief.md`, which matches its own text. Neither is a real `/validate-workflow` report, so the substance stands, but the brief's literal "0 matches" was never accurate. FU-2 must restate the grep honestly, for example by excluding `tests/golden/` and `docs/artifacts/` and saying so. |
| The `known_failing` count is at least the README floor of 5 | 7 in `open/` today, so 6 after the flip. **Confirmed.** No test asserts the count. |
| No test depends on this case's fixture file set | `test_golden_suite_format.py:40` requires only that a `fixture` directory exists. **Confirmed.** Deleting the two copies is safe. |
| The orchestrator invokes the Architecture gate | `orchestrator.md` § Core Workflow › Phase 1, step 6: "Run **Architecture Gate** before proceeding". **Confirmed.** |
| The pipeline order | `validation-gates` § Procedures › 4: "Architecture Gate → Implementation Gate → Integration Gate → Security Gate → Release Gate". **Confirmed.** |
| Nothing else quotes step 5's six-gate list | Only the command's source, its 6 `implementation/.<platform>/` mirrors, and **6 repo-root projections** (`.claude`, `.cursor`, `.gemini`, `.github`, `.opencode`, `.pi`). **FU-1 must declare those 6 root paths** in `tests/_baselines/root-install-drift.json`, as T564 did. |
| The shape of an `expected_pass` `case.yaml` | `id`, `command`, `status: expected_pass`, `tags`, with no `known_failing_*` keys (e.g. `team-status-dag-colour-code/case.yaml`). The FU-2 brief states this shape, so no read grant on another case is needed. |
| The baseline number | v14 is current, so this is **v15**. It needs the user's explicit authorization. |

**9.2 Rulings**

- **ADR-007 Validation 1 (six per-gate entries become five): not a weakening. Accepted.** The two removed entries
  were structurally unsatisfiable against the shipped definitions. They could only ever fail, "regardless of the
  workflow's actual health", so they measured nothing about the workflow. In their place the check gains two
  predicates the old one lacked. Completeness catches the omission of any gate kind, which is the omission the
  old check could not see. Ordered list fidelity catches a non-verdict step being re-added. The number of
  verdict-producing gates checked also rises from four to five. The per-gate value constraints are byte-identical.
  FU-2's discrimination section must demonstrate all seven listed perturbations.
- **Coverage of plan approval (the contestable part): accepted as decided.** Step 5's own closing sentence already
  classified plan approval as a workflow step, not a gate. Removing it from a list headed "Check all validation
  gates" corrects the list rather than narrowing the command's intent. Whether `/validate-workflow` should check
  plan approval as a non-gate is a scope question (S1). It is **parked as P36**, not decided here.
- **FU sequencing:** FU-1 (`T567`) → FU-2 (`T568`) → FU-3 (`T569`), each in its own MR, as in plan-092. FU-1 on
  its own leaves the case red, which is already its state, so there is no stale-green window this time.

**9.3 Parked**

- **P36:** S1, whether `/validate-workflow` should check plan approval as a non-gate (interacts with P10).
- **P37:** F1–F3. The integration gate has two VERDICT formats, one in `validation-gates` and one in
  `testing-strategy`. The orchestrator's Core Workflow never names "Implementation Gate". The Architecture gate's
  executor differs between the skill and the agent.
- F4 joins **P32** (plan-path family).
