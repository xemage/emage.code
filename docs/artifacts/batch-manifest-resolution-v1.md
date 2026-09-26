# Artifact: batch-manifest-resolution-v1.md

> Filename: `batch-manifest-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T535
- **Created**: 2026-09-26
- **Based on**: `docs/tasks/task-T535.md` §§1–6;
  `docs/decisions/ADR-007-command-contract-authority.md` (the decision this document applies);
  `docs/artifacts/command-contract-resolution-v1.md` and
  `docs/artifacts/skillify-contract-resolution-v1.md` (the shape this document follows);
  `docs/plans/plan-076-wave2-findings.md` §1; `AGENTS.md` (Task Protocol, Lifecycle States);
  `implementation/knowledge/commands/batch.md`; `implementation/knowledge/commands/plan.md`;
  `implementation/knowledge/commands/bug-report.md`;
  `implementation/knowledge/instructions/git-workflow.md`;
  `implementation/knowledge/skills/worktree-isolation/SKILL.md`;
  `implementation/knowledge/skills/task-management/SKILL.md`;
  `implementation/knowledge/agents/orchestrator.md`; `docs/tasks/validate-tasks.py`;
  `docs/tasks/_template.md`; `docs/artifacts/maturity-promotion-criteria-v2.md` §§3.2, 3.5;
  `docs/artifacts/protected-paths-v1.md` §5;
  `tests/golden/open/batch-manifest-ledger-schema-conflict/{case.yaml,brief.md,expect.py,fixture/}`;
  `implementation/registry/summary.md`; `docs/wiki/commands-and-skills-overview.md`.
- **Supersedes**: none (first version)

## 0. What this document is, and the answer in one paragraph

`ADR-007` states the principle: *a command's declared contract is authoritative over the corpus
unless the contract contradicts a higher-authority document, or unless the only thing in dispute is
a label for content the corpus already carries.* This document applies that procedure to one
conflict: `/batch` step 5's five-field manifest versus the schema `AGENTS.md` pins on
`docs/tasks/active-tasks.md`.

**Verdict: branch 1 fires twice, on two clauses, against two different higher authorities, and the
amendment deletes nothing.** Step 5 contradicts `AGENTS.md` § Task Protocol; step 3 independently
contradicts `git-workflow.md` (a `stable` instruction) and the very skill step 3 tells the reader to
use. Curing step 3 is what makes the step 5 repair honest rather than convenient: once a unit's
branch is `agent/<agent-name>/<task-id>`, the branch is *determined by two cells the ledger row
already has*, so it does not need a column — and it is still written down, in the plan document
step 2 now declares. All five of step 5's declared fields survive; each gets exactly one home.
**`/batch` does not end promotable**, and the golden case is **not** flipped: three of its
assertions now test strings that no document declares, so `expect.py` must be re-derived under an
authorization this task does not hold (§7).

Like `skillify-contract-resolution-v1.md` and unlike `command-contract-resolution-v1.md`, this
document is **both** specification and record of work done: `T535` §4 asked for the execution too.
§6 states exactly what was and was not touched.

## 1. The conflict, enumerated from the files

### 1.1 The clause `T535` convened over — step 5

`implementation/knowledge/commands/batch.md` `## Instructions` step 5, verbatim, pre-amendment:

> 5. **Track progress** — update `docs/tasks/active-tasks.md` with the full batch manifest:
>    - Unit ID, description, assigned agent, branch, status

`AGENTS.md` § Task Protocol, verbatim:

> - Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`
> - Sequential IDs: `T001`, `T002`, … Priorities: `P0` (critical path), `P1`, `P2`.

`docs/tasks/validate-tasks.py` enforces both halves (line numbers as of this task, post-`T537`/`T540`):

```python
if len(row.cells) != 7:                 # line 288 -- C2
    add_fail(fails, "C2", f"active-tasks.md:{row.line_no} has {len(row.cells)} cells (expected 7)")
...
if not ID_RE.fullmatch(task_id):        # line 307 -- C3, ID_RE = ^T\d{3,}$
```

Field-by-field, four of five map and one does not:

| step 5 field | `active-tasks.md` column | Maps? |
|---|---|---|
| Unit ID | `ID` | only if the ID is `T\d{3,}` — `U<n>` fails `C3` |
| description | `Title` | yes |
| assigned agent | `Owner` | yes |
| status | `Status` | yes |
| **branch** | **— nothing** | **no** |
| — | `Priority` | unmapped by step 5 |
| — | `Depends on` | unmapped by step 5 |
| — | `Last update` | unmapped by step 5 |

### 1.2 The clause behind it, which `T535`'s brief did not name — step 3

Step 3, verbatim, pre-amendment:

> 3. **Create worktree isolation** — for each unit:
>    - Create a dedicated worktree and branch **using the worktree-isolation skill**
>    - Branch naming: `batch/<slug>/<unit-number>-<short-description>`

`implementation/knowledge/instructions/git-workflow.md` — `maturity: stable`, `applyTo: "**"`,
whose own Rails declares its trigger as "every Git operation — branching, committing, merging,
opening merge requests, **or managing agent worktrees**":

> ## Agent Worktree Branch Naming
>
> Agents operate in isolated worktrees. Agent branches follow a dedicated naming convention:
>
> ```
> agent/<agent-name>/<task-id>
> ```
>
> ### Rules
> - `<agent-name>` is the kebab-case agent role name
> - `<task-id>` matches the task identifier from the task management system

And the skill step 3 itself names, `skills/worktree-isolation/SKILL.md` § "Branch Naming
Convention": `agent/<agent-name>/<task-id>`.

**Step 3 directs the reader to a procedure and then overrides that procedure's output name with a
different one.** That is the more consequential of the two defects, and it is the one the brief,
`plan-076` §1 and the case's own `known_failing_reason` all treat as settled background rather than
as part of the conflict.

### 1.3 Why the two are one defect

`/batch` mints a **parallel identity namespace** for objects this repository already has a governed
namespace for:

| Object | Governed identity | `/batch`'s rival |
|---|---|---|
| a unit of work | task, `T\d{3,}`, with a `docs/tasks/task-<ID>.md` brief and a ledger row | "unit", `U<n>`, with no brief and no declared home |
| an agent's isolated branch | `agent/<agent-name>/<task-id>` | `batch/<slug>/<unit-number>-<short-description>` |

Everything the brief describes follows from that one root cause. `branch` has nowhere to go
*because* the branch name deliberately contains neither the owner nor the task ID that the ledger
row already carries. `U<n>` trips `C3` *because* it is a second ID scheme for a task. The repair is
therefore not "find somewhere to put a branch"; it is "stop minting the namespace", after which the
branch stops needing a column at all.

## 2. The decision procedure, applied in `ADR-007`'s order

`ADR-007` §2: the first branch that fires decides. Branch 1 is first, and `ADR-007` names it "the
loophole to watch" — the contradiction must be quotable from the higher-authority document's own
text. Both are quoted verbatim in §1. What follows is the scrutiny that entitles the claim, plus
what the later branches would have said, because a verdict that never looks at them cannot claim to
be robust.

### 2.1 Branch 1 on step 5 — fires

`AGENTS.md` is, in `ADR-007`'s own words, "this repository's top-level convention document; a
command may specialise it but may not create a rival convention for the same thing." Step 5 names
that exact file and declares a different column set for it. This is not a specialisation: a
five-field row is not a refinement of a seven-column row, it is a different row, and the repository's
own validator rejects it on sight (`C2`). Three independent corroborations, none of which is a
popularity count:

1. **The named file's own validator rejects it.** Not a survey — an executable check in the
   repository, at `docs/tasks/validate-tasks.py:288`, whose failure text the case's `brief.md`
   already reproduces.
2. **A second, `stable` command declares the conforming form for exactly this situation.**
   `commands/bug-report.md` (`maturity: stable`) has the same need — a command that must create a
   ledger row — and declares: *"Use the NEXT sequential `T<NNN>` ID. NEVER invent a `BUG-` prefix —
   non-`T` rows are silently deleted by `install.sh --update`. Format (7 columns, exact order): `|
   T<NNN> | BUG: <title> | <owner-slug> | pending | P0|P1|P2 | <dep-ids or —> | YYYY-MM-DD |`"*.
   The pattern `/batch` needed already existed, in a `stable` sibling, including the
   `<PREFIX>: <title>` device for making a command's rows findable.
3. **The skill `AGENTS.md` delegates the mechanics to agrees.** `skills/task-management/SKILL.md`
   § "Task Table Format": "active-tasks.md — 7 columns, in this exact order", and its field rules
   read "ID | `T` + 3 or more digits… NEVER `BUG-7`."

The corpus is irrelevant to this branch and was not counted. `ADR-007` §2.1: "If the corpus
happened to follow the command and disagree with `AGENTS.md`, this branch would still amend the
command." It happens that there is no corpus at all (§5), which is precisely why an argument from
practice was unavailable and an argument from authority was required.

### 2.2 Branch 1 on step 3 — fires independently

`git-workflow.md` is `maturity: stable` per `implementation/registry/summary.md`, so it is inside
branch 1's enumeration ("`AGENTS.md`, a `stable` instruction, or another clause of the same command
file") on the `stable`-instruction limb. It governs the same object — an agent's isolated worktree
branch — under `applyTo: "**"`, and declares a different name.

The specialisation defence fails on the text. A specialisation of `agent/<agent-name>/<task-id>`
would keep the agent name and the task ID and refine something; `batch/<slug>/<unit-number>-<short-
description>` contains **neither** of the two elements `git-workflow.md`'s own Rules make mandatory.
It is a rival root namespace, and an **ungoverned** one: `git-workflow.md`'s "Worktree Lifecycle"
(create from `develop`, review, merge by MR, `git branch -d agent/<agent-name>/<task-id>`, "Never
leave stale worktrees — cleanup is mandatory") and its "Merge Request Rules" attach to `agent/*` and
to GitFlow's five prefixes. A `batch/*` branch has no declared creation base, no declared merge
path and no declared cleanup — while `/batch` step 7 asks the user to open a PR from each of them.

Two further reasons this clause is the defective one, in `ADR-007`'s sense of "the clause the rest of
the file and the corpus both disagree with":

- **It is self-defeating within its own step.** Step 3 says to use the worktree-isolation skill and
  then contradicts that skill's single declared convention.
- **It works against step 5.** Step 5 exists to make a unit traceable on the ledger; step 3's name
  omits the one token — the task ID — that would tie a branch to a ledger row.

### 2.3 Branch 2 — does not fire

The clause governs `docs/tasks/active-tasks.md`. The fixture's ledger is that class: its title,
header and separator lines are byte-identical copies of this repository's real `active-tasks.md`
(stated in the case's `brief.md` § Provenance and confirmed by reading both). Same path, same class,
no class disagreement — so this case is the second in the suite, after
`skillify-skill-file-template-drift`, that does **not** exhibit the artifact-class disagreement
`command-contract-resolution-v1.md` §5 found in all three of the original open pairs.

### 2.4 Branch 3 — unreachable, and there is nothing there anyway

3a needs a corpus carrying the same content under one coherent alternative name; 3b needs a corpus
that omits it. **There is no corpus.** Re-checked and carried from the case's own survey: zero
`batch/*` branches exist and zero rows in either ledger mention `batch/` — `/batch` has never been
run to completion in this repository (§5 states the limits of my ability to re-verify that).

### 2.5 Branch 4 — the convenient answer, available on a squint, and refused

This is the one place where the incentive `ADR-007` §Context warns about actually points somewhere,
so it is recorded prominently rather than buried.

With no corpus and a hand-authored `decomposition.md`, a motivated reader could argue branch 4 —
"no contract-vs-corpus conflict at all; reclassify `tracked_defect` → `capability_gap`" — exactly as
`command-contract-resolution-v1.md` row D did for `/security-audit`. **That is the answer that
unblocks a promotion immediately**: `capability_gap` does not count under
`maturity-promotion-criteria-v2.md` §3.5, so `/batch` would clear the defect criterion today,
with no command edit at all. The verdict taken here clears nothing and makes the command's contract
*harder* to satisfy.

It is refused because branch 4's own stated condition is not met. `ADR-007` §2.4: "There is no
corpus to fix **and, if the rule is independently backed**, no contract to amend." Here the rule is
not independently backed — it is contradicted by `AGENTS.md` and by a `stable` instruction, so there
*is* a contract to amend, and §2's ordering means branch 1 decides before branch 4 is ever reached.
The case's own `Category` section reached the same conclusion from the other direction ("Nothing
prevents a conforming manifest from being written"), and agreeing with it costs this task the
cheapest available green.

## 3. The four repair options, and the three that were rejected

Branch 1 firing settles that the command changes. It does not say how. These are the options
`T535` §3 and `plan-076` §1 name, plus the one they do not, each judged on the merits.

### 3.1 Rejected — amend the ledger schema to carry a branch

**Grounds for rejection: wrong document, and the blast radius is not this task's to spend.**
`active-tasks.md`'s columns are declared in `AGENTS.md`, so this is an `AGENTS.md` amendment.
Downstream of it: `docs/tasks/validate-tasks.py`'s destructuring and **fourteen** checks (`C1`–`C14`
— `C12`, `C13` and `C14` were added after this conflict was first recorded, by `T537` and `T540`, so
the schema is *more* load-bearing now, not less); `skills/task-management/SKILL.md`'s two schema
tables and its archival field-mapping; `commands/bug-report.md`'s declared row format;
`docs/tasks/_template.md`; every platform projection of all of those; the active ledger; and
`completed-tasks.md`'s several hundred archived rows, whose 5-column schema is derived from the
7-column one by the declared mapping in `skills/task-management/SKILL.md` § "Field mapping when
archiving". (`T535` §3 puts the archived count at 330 and this task's dispatch at 334; I did not
count, and nothing here turns on the figure.)

And it would be the wrong shape even if it were free: a `Branch` column would be **null for every
row that is not a batch unit**, which is almost every row. `ADR-007` branch 1's reasoning — a
command may not make the top-level convention serve its local need — cuts against widening the
convention for one command just as much as against the command inventing a rival.

### 3.2 Rejected — a new, dedicated batch-manifest file

**Grounds for rejection: it mints a third namespace to avoid minting a second.** A
`docs/tasks/batch-<slug>.md` or similar would be a new file class inside a directory whose contents
`AGENTS.md` enumerates (`active-tasks.md`, `completed-tasks.md`, `task-<ID>.md`). It is also
unnecessary, because a governed home for exactly this document already exists (§4.1) and two
documents already *require* `/batch` to produce one:

- `commands/plan.md` § "Task Creation Precondition": *"no task row may be added to
  `docs/tasks/active-tasks.md` until (a) the plan document it derives from exists under
  `docs/plans/plan-<ID>.md` and (b) that plan has been presented for review… Every task ID created
  from this plan must appear in the plan document's text."*
- `agents/orchestrator.md` § "Creating Tasks", which restates it and adds: *"Task creation without a
  backing plan is not permitted."* `/batch`'s `agent:` frontmatter is `orchestrator`.

A `/batch` run that creates ledger rows therefore owes a plan document under `docs/plans/` **whether
or not** the manifest question is ever asked. Inventing a second document beside it would leave the
unit briefs' mandatory `**Based on:** docs/plans/plan-<NNN>-<slug>.md` field (per
`docs/tasks/_template.md`) pointing at a document class that is not a plan.

### 3.3 Rejected — keep `batch/*`, and store the branch somewhere

**Grounds for rejection: it treats the symptom and leaves the branch-1 contradiction of §2.2
standing.** Every variant was considered, including the attractive middle option
`batch/<slug>/<task-id>-<short-description>`, which would preserve the `git branch --list
'batch/<slug>/*'` grouping affordance *and* make the branch derivable. It still creates a branch
namespace no `stable` instruction declares, with no lifecycle and no merge path, so the
contradiction is narrowed cosmetically rather than cured.

**The lost affordance is real and is not dismissed.** Two mitigations, neither of which needs a new
namespace: the ledger `Title` carries a `BATCH <slug>:` prefix (§4.3), modelled on `bug-report.md`'s
`BUG: <title>`, which makes a batch's rows greppable in the file that actually tracks them; and the
step 2 plan document lists the batch's branches in one table. **If prefix grouping is judged worth
having in git itself, the document to amend is `git-workflow.md`** — a `stable` instruction, in its
own task, with its own adjudication. A command may not mint it. That door is named here rather than
walked through.

### 3.4 Rejected as *stated* — "drop `branch`, it is derivable"

This is the option `T535` §3 flags as the one that must be reached on the merits or not at all. As
stated in the brief it is **not** sound, and it is rejected in that form:

> `branch` may be **derivable** rather than stored: step 3 of `batch.md` already declares
> `batch/<slug>/<unit-number>-<short-description>`, and `git-workflow.md` declares
> `agent/<name>/<task-id>`.

Under step 3 **as it stood**, the branch was *not* derivable from a ledger row. `batch/<slug>/<unit-
number>-<short-description>` is a function of the batch slug, an ordinal and a free-text
description — none of which appears in any ledger column. Deleting `branch` from step 5 while
leaving step 3 intact would have destroyed the only record of a value the command's own step 7 needs
("Help the user create a PR for each branch"), and it would have been `ADR-007` §5's prohibited
move exactly: "deleting required fields… for convenience." It is also the *smallest* available edit,
which `T535` §3 and `plan-076` §1 both name as the wrong reason to choose anything.

**What makes the derivation true is the §2.2 amendment, not the deletion.** The two edits are a
package, and the ordering matters: step 3 is corrected because a `stable` instruction says so, and
*then* `agent/<Owner>/<ID>` is a function of two cells the row already carries. If a reviewer
overturns §2.2 and restores `batch/*`, the step 5 amendment must be revisited with it, because its
premise is gone. That dependency is the single most important thing to carry forward from this
document.

## 4. The verdict, and what makes it §5-safe

### 4.1 The decomposition gets a declared home

**Amend by addition** — `/batch` declared no path for its decomposition at all, while `##
Important` required it to be produced and presented ("Present the decomposition plan for user
approval before creating worktrees"). Like `skillify-contract-resolution-v1.md` §3.6, this is a
**gap, not a contradiction**, and is labelled as sitting outside `ADR-007`'s five branches rather
than folded into branch 1: silence is not contradiction, and branch 1 is the branch not to stretch.

The declared home is `docs/plans/plan-<ID>.md`, quoted in the form `commands/plan.md` step 5 and
`agents/orchestrator.md` both use. (The corpus and `docs/tasks/_template.md` render `<ID>` as
`<NNN>-<slug>`; that pre-existing looseness between four documents is recorded in §5.3 and
deliberately not resolved here.) The document is declared to be a plan document, and therefore to
follow `plan.md` step 5's six declared sections, **plus** one additional required section, the
Batch Manifest.

Reusing `/plan`'s structure rather than declaring a lighter batch-specific one is a deliberate
choice, and it is the *stricter* of the two:

- All six sections are meaningful for a batch. `Dependency Graph` is the strongest case: an
  independent batch renders as a graph with no edges, which is the visual proof of step 2's
  constraint rather than a formality. `Risk Assessment` is what step 7's merge-order advice should
  be reasoned from.
- It keeps two commands from declaring rival structures for one directory — the same failure mode
  branch 1 exists to prevent, one level down.
- It costs something: `/plan`'s six-header contract is a standing red
  (`command-contract-resolution-v1.md` row A, branch 3b — contract upheld, corpus non-conforming,
  8 of 8 sampled plan documents fail it). A conforming `/batch` run must now produce a plan document
  that no document in this repository has yet produced. That is `ADR-007` 3b's "earn it by doing the
  work", inherited on purpose, not an oversight.

**Counter-reading, recorded because it is respectable:** a reviewer may prefer that `/batch` declare
only the content it needs (unit table, independence, merge order) and not inherit `/plan`'s header
list. Under that reading the executed edit is smaller but the path, the manifest section and every
other verdict here are unchanged — **and no case outcome or promotion outcome moves** (§5.2, §8),
because the golden case does not check the plan document's headers and
`maturity-promotion-criteria-v2.md` §3.5's defect scan is per-`command:`, so `/plan`'s red case
never attaches to `/batch`. This verdict is robust to being overruled here.

### 4.2 Step 3 — `batch/<slug>/<unit-number>-<short-description>` → `agent/<agent-name>/<task-id>`

Branch 1 (§2.2), on the `stable`-instruction limb. The amended clause cites `git-workflow.md` § and
the skill, so the three documents now say one thing.

### 4.3 Step 5 — the ledger row, in the ledger's own schema

Branch 1 (§2.1). Step 5 now declares the 7-column row explicitly, in `bug-report.md`'s form, with
four additions that are all constraints rather than permissions:

| Addition | Why |
|---|---|
| `T<NNN>`, never `U<n>` — cites `C3` and the `install.sh --update` deletion | Kills the second collision at its root: the unit *is* a task, so there is one ID scheme. |
| a `docs/tasks/task-T<NNN>.md` brief per unit, citing the step 2 plan in `**Based on:**` | `AGENTS.md` § Task Protocol requires a brief per task; `validate-tasks.py` `C6`/`C7` enforce the correspondence in both directions. |
| `Depends on` must not name another unit of the same batch; outside-the-batch dependencies are permitted | **This is a gain, not bookkeeping.** Step 2's independence constraint — which `## Rails` names as the command's declared failure mode — had no enforcement home anywhere. The ledger's sixth column is that home, and `C12`/`C13`/`C14` already resolve, self-check and cycle-check those edges. |
| the ledger is authoritative for `Status`; the manifest is not a second status record | Prevents the drift that any two-homes-for-one-fact design generates. |

### 4.4 Nothing is deleted — every declared field has exactly one home

This is the §5 argument, and it is the reason this verdict is not the rejected option of §3.4:

| step 5's declared field | Home after the amendment |
|---|---|
| Unit ID | `active-tasks.md` `ID`, as a real `T<NNN>` |
| description | `active-tasks.md` `Title`, as `BATCH <slug>: <description>`; in full in the manifest's `Description` |
| assigned agent | `active-tasks.md` `Owner` |
| status | `active-tasks.md` `Status` — authoritative, and the only place it is recorded |
| **branch** | the step 2 plan document's **Batch Manifest**, constrained to equal `agent/<Assigned agent>/<Task ID>` |

`ADR-007` §5 prohibits "deleting required fields, loosening a regex, or admitting a second form for
convenience." **No field is deleted; none is loosened; no second form is admitted.** The manifest is
partitioned by ownership rather than shrunk, and the amended contract adds requirements the old one
did not have (a `T` ID, a per-unit brief, a `Priority`, a dated `Last update`, a constrained
`Depends on`, a six-section plan document, and conformance to all fourteen ledger checks). A
follow-up that produces a *shorter* required list than this has misread the verdict.

The branch is stored **and** derivable, deliberately: the manifest records it for step 7's benefit,
and the constraint that it equal `agent/<Owner>/<ID>` means the stored copy can be checked against
the ledger rather than believed. A derived value with a declared derivation rule cannot silently
drift; a stored value with no rule can.

## 5. Re-verification, method limits, and what the inputs got wrong

**Method, stated plainly and up front: this session had no shell, no `grep`, no directory listing,
and no ability to execute anything.** I hold `read`/`edit`/`web` and no `execute` (per
`implementation/knowledge/agents/solution-architect.md` and `T535` §1). Every finding below was
derived by reading named files. **I ran no test, no validator, no checker and no script, and I claim
no verification that requires one.**

### 5.1 Findings that correct or qualify the inputs

| Claim | Finding | Verdict on the claim |
|---|---|---|
| `T535` §3 / `plan-076` §1: "`branch` may be derivable… `git-workflow.md` declares `agent/<name>/<task-id>`" | **True only after step 3 is amended, which neither document proposes.** Under step 3 as it stood the branch was a function of slug + ordinal + free text, none of it on the ledger. Taken as stated this option is `ADR-007` §5's prohibited deletion. See §3.4 — this is the most consequential correction here, because it is the difference between the right verdict and the same verdict reached for a wrong reason. | **Right instinct, unsound as stated.** |
| `T535` §2 / `plan-076` §1 / `case.yaml`: the conflict is step 5 versus the ledger schema | **Incomplete. Step 3 carries an independent branch-1 defect against a `stable` instruction** (§2.2) and against the skill step 3 itself invokes. All three inputs treat step 3's branch pattern as settled background — the case's `expect.py` assertion B *asserts* it as the contract. | **Understated by one clause.** |
| `T535` §2 / `plan-076` §1: "the two spare columns are taken" | **Framing is backwards for one of them.** `Priority` and `Depends on` are described as obstacles crowding out `branch`. `Depends on` is in fact the column `/batch` most needs: it is the only enforcement home for step 2's independence constraint, and `C12`/`C13`/`C14` now check it (§4.3). The ledger does not merely accommodate a batch; it validates the batch's own declared invariant. | **Materially misframed; does not change the branch assignment.** |
| `T535` brief: `validate-tasks.py` has gained `C12`, `C13`, `C14` since the conflict was recorded | **Confirmed by reading the file** (`C12`/`C13` at lines 457–483, `C14` at 485–493, `dependency_cycles()` at 214). The steer that this makes the schema *more* load-bearing is correct, and it is one of the grounds for rejecting §3.1. | **Accurate and load-bearing.** |
| case `brief.md`: "**Five** of step 5's fields map onto that schema (`Unit ID`→`ID`, `description`→`Title`, `assigned agent`→`Owner`, `status`→`Status`)" | **Off by one in the prose:** it says five and lists four. `T535` §2 and `plan-076` §1 both say four, correctly. Cosmetic, but it is in a protected file and should be corrected by the same follow-up as the rest (§7). | **Typo in a protected file.** |
| `case.yaml` and `brief.md`: the cell-count check is at `validate-tasks.py:195` | **Stale line number.** It is at line 288 now; `C3`'s ID check is at 307. The quoted code is still accurate. | **Stale, harmless, worth folding into the follow-up.** |
| `case.yaml` / `brief.md`: zero `batch/*` branches; zero `batch/` rows in either ledger; `/batch` never run to completion here | **Consistent with everything read, and not independently re-verified.** Both original surveys were shell commands (`git branch -a --list 'batch/*'`, `grep -c 'batch/'`) that I cannot run. No `batch/` branch or row was encountered in any file read this session, including both ledgers' schemas and the registry. **Flagged as unverified rather than confirmed.** Nothing in §2 depends on it: branch 1 fires on authority, and a corpus, if one existed, would not change that. | **Unverified, not contradicted, and inert to the verdict.** |
| `docs/wiki/commands-and-skills-overview.md`'s `/batch` row: "tracking the full batch manifest in the task ledger" | **Still true after the amendment, and slightly loose either way** — the ledger tracks the units; the manifest's branch column lives in the plan document. `maturity-promotion-criteria-v2.md` §3.2 criterion 6 (a full sentence under `docs/wiki/**`) is satisfied by this row, verified by reading it. Not edited: a one-clause wording refresh belongs to `technical-writer`, and criterion 6 does not turn on it. | **Satisfied; a cosmetic refresh is optional.** |

### 5.2 Does the golden case pass? **No — and it cannot, under the checker that exists**

Traced by reading `expect.py` against `fixture/` line by line. **Not executed** — see §5 preamble.

| Assertion | Element | Fixture | Under the amended contract |
|---|---|---|---|
| parse | 5-col unit table, headers matching unit/description/agent/branch/status | present, 3 rows | the manifest's columns are `Task ID \| Description \| Assigned agent \| Branch`, so a conforming artifact has **four** columns and `_table_matching` returns `None` → `check()` returns `False` |
| parse | `UNIT_ID_RE = ^U\d+$` | `U1`, `U2`, `U3` → passes | a conforming unit ID is `T534`, which **fails** `^U\d+$` |
| **B** | `BRANCH_RE = ^batch/[a-z0-9][a-z0-9-]*/\d+-[a-z0-9][a-z0-9-]*$` | `batch/structured-logging/1-runtime-memory` → passes | a conforming branch is `agent/backend-developer/T534`, which **fails** `BRANCH_RE` |
| **A** | per-unit dependency table, no intra-batch edge | present, all `—` → passes | relocates to the ledger row's `Depends on` (§4.3) |
| **C** | some ledger row carries the unit's ID **and agent and status and branch** | no row carries `U1` or any branch → **fails** | `branch` is no longer a ledger field, so assertion C as written can never be satisfied by a conforming artifact |

`check()` returns `False` today, returned `False` before this task, and would return `False` against
a fully conforming artifact. **Three of its five checks now test strings that no document declares.**
The checker has stopped being a check of the live contract — which is a defect with a deadline, not
a cosmetic one, and is why §7 is a blocker rather than a note.

**`case.yaml` was not touched, and must not be flipped on this document's word.** `T535` §5's grant
is conditional on the verdict genuinely making `check()` return `True`; it does not.

**Whether the case can *ever* pass — stated carefully, because this is the one place a reader should
be suspicious of me.** After an authorized re-derivation (§7) the case is *expected* to pass, and
the reason is favourable to me, so here is the full chain with its weakest link named:

- The fixture's **ledger half already conforms** to the amended step 5 with no edit at all: its
  three rows are 7-column, their IDs are `T534`/`T535`/`T536` (matching `C3`), their Titles carry a
  `BATCH structured-logging …` prefix, their Owners are real agent slugs, Status is `pending`,
  Priority `P2`, `Depends on` `—`, dates well-formed. That the real-schema half of a
  hand-authored-to-fail case happens to satisfy the amended contract exactly is corroboration that
  the amended shape is the natural one — the case's author reached for it instinctively while
  arguing it was impossible.
- The fixture's **`decomposition.md` does not conform** (`U<n>` IDs, `batch/*` branches, five
  columns, no plan-document sections) and would need re-authoring. `ADR-007` §5 permits exactly
  this — "Re-authoring a *hand-authored fixture* to a corrected contract is permitted and is not
  relaxation" — and the case's own `brief.md` § Provenance states "`decomposition.md` is
  hand-authored." `ADR-007`'s sibling-fate corollary, branch 1 "where the amendment changes only a
  *name or path*", predicts survival with the fixture updated to the amended form.
- **The weakest link:** a reader may fairly say the amendment changes more than a name or a path —
  it changes the manifest's *class* (a ledger row plus a plan-document section, where there was one
  ledger row) — which is the corollary's other row, "**invalidated — must be re-purposed**". Under
  that reading the case needs a new fixture and a new `check()`, not an updated one. **The
  difference matters for who does the work, not for the verdict or for whether the case is red
  today**, and either way the outcome is earned by producing conforming artifacts rather than by
  weakening a check. I did not resolve it, because resolving it *is* the re-derivation I am not
  authorized to perform.

### 5.3 Observations outside this task's scope, recorded not acted on

1. **`agents/orchestrator.md` § "Git Workflow Enforcement" contradicts `git-workflow.md`.** It
   routes `docs` and `chore` work to "commit directly to develop (docs-only changes exempt)", while
   `git-workflow.md` § "Protected Branches — No Direct Commits, Ever" states "There is no 'it's just
   a doc update' exception" and records two rejected pushes as precedent. That is a branch-1 defect
   in an `experimental` agent file against a `stable` instruction, structurally identical to §2.2
   and entirely unrelated to `/batch`. It deserves its own task.
2. **`plan-<ID>.md` versus `plan-<NNN>-<slug>.md`.** `commands/plan.md`, `agents/orchestrator.md`
   and now `commands/batch.md` write `docs/plans/plan-<ID>.md`; `docs/tasks/_template.md` and the
   real corpus use `plan-<NNN>-<slug>.md`. Harmless in practice and pre-existing; I quoted the
   former so as not to mint a fourth form, rather than because it is the better one.
3. **`task-T535.md` declares `**Affects:** —`.** The honest value is `command/batch`, since this
   task does indict that command. It is `P2`, so `C11` does not require the field and
   `maturity-promotion-criteria-v2.md` §3.5 does not read `P2` rows, so nothing turns on it — and
   `T535` §4 authorized only the `**Status:**` edit on that file. Flagged rather than changed.
4. **`maturity-promotion-criteria-v2.md` §3.5's two limbs are priority-asymmetric.** Limb (a) is
   explicitly `P0`/`P1`-scoped; limb (b) (a `tracked_defect` golden case) carries no priority, yet
   the definition it feeds is named "open `P0`/`P1` defect". So it is genuinely unclear whether a
   `tracked_defect` case blocks the `experimental → beta` gate (criterion 3, `P0` only) or only
   `beta → stable` (criterion 7). It does not change §8's answer — `/batch` is blocked at criterion 7
   under either reading — but a future promotion wave will have to decide, and should not have to
   decide it under time pressure.

## 6. What was executed, and what was deliberately not

### 6.1 Executed

| File | Change |
|---|---|
| `implementation/knowledge/commands/batch.md` | Step 2 gains the declared plan-document path and the Batch Manifest section (§4.1). Step 3's branch pattern → `agent/<agent-name>/<task-id>`, with the ID-allocation ordering made explicit (§4.2). Step 5 rewritten to the 7-column schema with the four constraints in §4.3. `## Important` gains the artifact-ordering bullet. `## Rails` § "Out of scope" gains the manifest clause. **Step numbering is unchanged**, deliberately: `expect.py`'s docstring and the case's `brief.md` both cite these clauses by step number. |
| `docs/artifacts/batch-manifest-resolution-v1.md` | This document. |
| `docs/tasks/task-T535.md` | `**Status:** pending` → `in_review`. No ledger row touched — archival is orchestrator-only per `AGENTS.md`. |

### 6.2 Not executed

| Not done | Reason |
|---|---|
| `tests/golden/open/batch-manifest-ledger-schema-conflict/expect.py` | **Required, and refused.** `T535` §5 excludes it and instructs a blocker instead; `protected-paths-v1.md` §5 item 1 forbids a silent edit and item 2 requires a named authorization no wider than the one I hold. §5.1 of `protected-paths-v1.md` also forbids extending my own grant, so `T535` §5's table was not edited either. See §7. |
| `case.yaml` status flip | The verdict does **not** make `check()` return `True` (§5.2), and I cannot run `check()` to find out otherwise. `T535` §5's grant is conditional on a genuine pass; flipping would be a guess dressed as a result. |
| `case.yaml` `known_failing_reason` / `tags` | Now stale (it cites `validate-tasks.py:195`, and frames the exit as "either… or the ledger schema gains the fields", which §3.1 rejects). The grant covers only a status flip and removal of the `known_failing_*` keys on a genuine pass, neither of which applies. |
| `brief.md` restatement | The grant reads "restate the expected outcome **to match**" — i.e. to match a flip that is not happening. Following `skillify-contract-resolution-v1.md` §4.4's identical refusal. Its staleness is real and specified in §7. |
| `docs/tasks/active-tasks.md` and `completed-tasks.md` | Out of scope by `T535` §4 and `AGENTS.md` (orchestrator-only). |
| `AGENTS.md`, `docs/tasks/validate-tasks.py`, `skills/task-management/SKILL.md` | §3.1 — the schema is not amended, so none of them needs to change. This is the load-bearing consequence of the verdict: the largest option was available and was not taken. |
| `implementation/knowledge/instructions/git-workflow.md` | §3.3 — if `batch/*` grouping is wanted in git, that is where it would be declared, by its own task with its own adjudication. Amending a `stable` instruction to accommodate a command I was sent to fix would invert the authority `ADR-007` just applied. |
| `docs/wiki/commands-and-skills-overview.md` | §5.1 — the `/batch` row remains true and satisfies criterion 6. A wording refresh is `technical-writer`'s, and not required. |
| `commands/batch.md`'s `maturity:` field | Still `experimental`. A maturity flip is a component-state decision (the `T526`/`T534` precedent), not an adjudication outcome, and §8 says it would not be earned yet anyway. |
| Platform projections (`.claude/`, `.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.cursor/`, `.cline/`) and `implementation/registry/` | Generated. `AGENTS.md` forbids hand-editing them. They will show drift until `node implementation/scripts/sync.mjs` **and** `python3 implementation/scripts/generate-registry.py` are both re-run — per `T535` §6, `sync.mjs --check` alone does not catch registry drift. |

## 7. Blocker — `expect.py` must be re-derived, and this task refused to do it

- **Type:** `technical` · **Severity:** `major` · **Status:** open, escalated, not worked around.

Three of the checker's five elements now test a superseded contract (§5.2): `UNIT_ID_RE = ^U\d+$`
and `BRANCH_RE = ^batch/…$` assert forms no document declares any more, and assertion C requires a
`branch` in a ledger row that the amended contract says is not there. `check()` returns `False`
either way, so nothing is currently *mis*-reported — but the case has stopped measuring the live
contract.

`T535` §5 excludes `expect.py` and instructs a blocker; `protected-paths-v1.md` §5 item 2 requires
a named, orchestrator-authored authorization. **The §5 table was not widened and `expect.py` was not
touched**, matching `T520`, `T523`, `T525`, `T527` and `T531`.

**Specification for the authorized follow-up.** `ADR-007` Validation criterion 1 requires the
replacement to assert the same number of structural elements with the same ordering and value
constraints. Element-for-element:

| Existing element | Replacement | Strength |
|---|---|---|
| `UNIT_ID_RE = ^U\d+$` | `^T\d{3,}$` — the same regex `validate-tasks.py` `C3` uses | unchanged (one ID regex, stricter digit floor) |
| `BRANCH_RE = ^batch/[a-z0-9][a-z0-9-]*/\d+-[a-z0-9][a-z0-9-]*$` | `^agent/[a-z0-9][a-z0-9-]*/T\d{3,}$` | unchanged in count; **stronger**, because it must also equal `agent/<row's Owner>/<row's ID>`, which is checkable against the ledger rather than merely well-formed |
| `MANIFEST_CONCEPTS` — 5 header concepts on the unit table | 4 (`task id`, `description\|title`, `agent\|owner\|assign`, `branch`) on the plan document's Batch Manifest, **plus** the 5th (`status\|state`) asserted on the ledger row | 5 concepts before, 5 after — relocated, not dropped |
| `DEPENDS_CONCEPTS` — independence read from the decomposition's dependency table | independence read from the ledger row's `Depends on` cell: no unit's cell may name another unit of the same batch | unchanged in count; **stronger**, because it now reads the column `validate-tasks.py` `C12`/`C13`/`C14` also validate |
| assertion C — a ledger row carries ID + agent + status + branch | a ledger row carries ID + agent + status, is 7 cells, its ID matches `^T\d{3,}$`, and its `Title` begins `BATCH <slug>:` | 4 conjuncts before, 5 after |
| *(none)* | the plan document exists at the declared path and carries `plan.md` step 5's six sections plus `## Batch Manifest` | net addition; **omit this if §4.1's counter-reading is taken**, and say so in the docstring |

The `_cells`/`_tables`/`_table_matching` helpers, the `main()` wrapper and the
"at least two units" guard should stay byte-identical. The module docstring's quoted clauses must be
updated to the amended steps in the same edit. The same authorization should carry:

- `case.yaml` — `known_failing_reason` (stale line number; its stated exit now contradicts §3.1),
  and the `status` / `known_failing_*` keys **only if** `check()` is observed to return `True`.
- `brief.md` — its `## What this checks` quotes all three steps pre-amendment; its `## Pass
  condition`, `## Why this is known_failing today` and `## Category` sections are all superseded;
  and §5.1's "Five… (four listed)" typo is in it. Same defect shape as `T530`
  (`new-feature-real-checkpoint-format-drift`) and `skillify-contract-resolution-v1.md` §5.4, and it
  should be folded into the same authorization.
- **A re-authored `fixture/decomposition.md`**, if §5.2's "name or path" reading is taken — or a
  re-purposed fixture and check, if the "artifact class" reading is. That choice belongs to the
  authorized task, with the trade-off in §5.2 in front of it.

The follow-up must **run** `check()` and report the observed result. I could not, and did not.

## 8. Is `/batch` promotable? **No.**

Stated plainly, as `T535` §3 requires, and against
`docs/artifacts/maturity-promotion-criteria-v2.md` §3.2. `/batch` is `maturity: experimental` per
`implementation/registry/summary.md`, so it must clear `experimental → beta` before `beta → stable`
is even in question.

| Gate | Criterion | State |
|---|---|---|
| → beta | 1. `maturity: beta` set; passes `command.schema.json` | **not met.** Still `experimental`, and a maturity flip is a component-state decision, not this task's (§6.2). |
| → beta | 2. `## Rails` present with all three labels | met (verified by reading the file; still intact after the amendment, with one clause added to "Out of scope"). |
| → beta | 3. no open `P0` defect | **unresolved.** §3.5's golden-case limb carries no priority, so whether a `tracked_defect` case fires here is genuinely ambiguous (§5.3.4). |
| → stable | 4. ≥1 golden case with `command: /batch` | met — `batch-manifest-ledger-schema-conflict` exists. |
| → stable | 5. `agent:` resolves to a real registry agent | met — `agent: "orchestrator"`, which is in the registry. |
| → stable | 6. a full sentence under `docs/wiki/**` | met — `docs/wiki/commands-and-skills-overview.md`'s `/batch` row (§5.1). |
| → stable | 7. no open `P0`/`P1` defect | **not met, and this is decisive.** The case remains `known_failing` + `tracked_defect` with `command: /batch`, so §3.5's second limb fires. |

So: **`/batch` does not end promotable, and this task does not unblock it.** Criterion 7 stays red
until the §7 follow-up lands, re-derives the checker, resolves the fixture question and is *observed*
to make `check()` return `True`; and even then `/batch` must be promoted through `beta` first, on a
separate component-state decision. **Nothing here should be taken as a promotion recommendation, and
no promotion should be granted without re-running `implementation/scripts/check-maturity.py` for
real** — I ran nothing.

This was the expected shape and, on the evidence, the correct one. `ADR-007` §Consequences predicted
"2 cases end green, 1 stops blocking without going green, 3 stay red" and warned that a clean sweep
would be the suspicious result. The cheapest green was available here (§2.5 — reclassify to
`capability_gap`, no command edit, promotion criterion cleared today) and was refused on its own
stated condition. The verdict taken instead makes `/batch`'s contract strictly harder to satisfy,
inherits a standing red from `/plan` (§4.1), and leaves the case red.

## 9. Consumed by

- The authorized follow-up implementing §7: `expect.py` re-derivation, the `case.yaml` /`brief.md`
  corrections, and the fixture decision — under a `protected-paths-v1.md` §5 grant naming those
  files, authored by the orchestrator and not by this document.
- A separate task for §3.3, **if** `batch/*`-style prefix grouping is judged worth having: it is an
  amendment to `git-workflow.md`, a `stable` instruction, and needs its own `ADR-007` adjudication.
- A separate task for §5.3.1 (`orchestrator.md`'s direct-to-`develop` carve-out versus
  `git-workflow.md`) — unrelated to `/batch`, and a live branch-1 defect.
- Optionally, `technical-writer` for §5.1's one-clause `docs/wiki` refresh, and a future revision of
  `maturity-promotion-criteria-v<N>.md` for §5.3.4's priority asymmetry.
- Any re-run of `implementation/scripts/check-maturity.py`, `docs/tasks/validate-tasks.py`,
  `node implementation/scripts/sync.mjs` or
  `python3 implementation/scripts/generate-registry.py` — all of which this task's changes require
  and none of which this task could run.
