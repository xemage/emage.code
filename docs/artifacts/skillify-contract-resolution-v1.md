# Artifact: skillify-contract-resolution-v1.md

> Filename: `skillify-contract-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T527
- **Created**: 2026-09-25
- **Based on**: `docs/tasks/task-T527.md` §§1–6;
  `docs/decisions/ADR-007-command-contract-authority.md` (the decision this table applies);
  `docs/artifacts/command-contract-resolution-v1.md` (the shape this document follows);
  `docs/plans/plan-073-skillify-adjudication-and-wave2.md` §0–§1;
  `docs/artifacts/maturity-promotion-criteria-v2.md` §§0, 2, 3.4, 3.5 (and v1 §2.1, carried
  forward verbatim into v2); `docs/artifacts/protected-paths-v1.md` §5;
  `tests/golden/open/skillify-skill-file-template-drift/{case.yaml,brief.md,expect.py,fixture/}`;
  `implementation/knowledge/commands/skillify.md`;
  `implementation/knowledge/skills/skillify/SKILL.md`;
  `implementation/knowledge/schemas/skill.schema.json`; `implementation/registry/summary.md`;
  `AGENTS.md`.
- **Supersedes**: none (first version)

## 0. What this document is

`ADR-007` states the principle: *a command's declared contract is authoritative over the corpus
unless the contract contradicts a higher-authority document, or unless the only thing in dispute is
a label for content the corpus already carries.* This document applies that procedure to the one
open conflict it did not cover — `/skillify`'s declared `SKILL.md` template versus the `skillify`
skill's declared `SKILL.md` template versus the real skill corpus.

**The answer is per-section, not per-file.** Two of the five declared sections are relabelled
(branch 3a), three are upheld against a non-conforming corpus (branch 3b), and one contract gap
outside `ADR-007`'s five branches is closed by addition. The skill file is amended in two places to
cure a contradiction with its own procedure. **The golden case stays red under every reading, and
`/skillify` does not become promotable.**

Unlike `command-contract-resolution-v1.md`, this document is **both** the specification and a record
of work done: `T527` §4 asked for the execution as well as the adjudication. §6 states exactly what
was and was not touched, and why one required edit was refused.

## 1. The conflict, enumerated from the files

Two documents declare a structure for the same artifact — `.github/skills/<name>/SKILL.md`.

**Contract A — `implementation/knowledge/commands/skillify.md`, `### Generate the Skill File`**
(quoted verbatim, pre-amendment):

> After the 4-round interview, generate `.github/skills/<name>/SKILL.md` with this structure:
>
> ```markdown
> # <Skill Name>
>
> ## Trigger
> ## Inputs
> ## Steps
> ## Success Criteria
> ## Examples
> ```

**Contract B — `implementation/knowledge/skills/skillify/SKILL.md`, `## SKILL.md Template`**
(quoted verbatim, pre-amendment; `T527`'s brief and `plan-073` §0 both list six sections — the file
actually declares **seven** plus YAML frontmatter and a level-1 title):

> ```markdown
> ---
> name: <skill-name>
> description: "<one-line description>"
> ---
>
> # <Skill Title>
>
> ## Purpose
> ## When to Use
> ## Prerequisites
> ## Procedure
> ## Examples
> ## Edge Cases
> ## Guidelines
> ```

**The structural fact that reframes the whole conflict:** both documents run the *same* four-round
interview, collecting the *same* four things in the *same* order.

| Round | Contract A asks | Contract A emits | Contract B asks | Contract B's Round emits |
|---|---|---|---|---|
| 1 | "When should this skill activate?" | `## Trigger` | "What triggers this workflow?" | frontmatter; template renders `## When to Use` as `- <trigger 1>` |
| 2 | "What inputs does this workflow need?" | `## Inputs` | "What inputs does this skill need?" | `## Prerequisites` + `## Required Context` |
| 3 | "Walk me through the steps." | `## Steps` | "Walk through the workflow step by step." | `## Procedure` |
| 4 | "How do you know it worked?" | `## Success Criteria` | "How do you know the skill executed successfully?" | `## Success Criteria` + `## Edge Cases` |

So the two contracts do **not** disagree about *what* a skill file must contain. They agree on all
four, in order. They disagree about three of the four **names**, and Contract B's final template
then drops one section its own Round 4 declares. That distinction — same content, different labels,
plus one self-inflicted omission — is exactly the distinction `ADR-007` branch 3 is built to make.

`Contract B`'s extra sections (`## Purpose`, `## Edge Cases`, `## Guidelines`) are **not** in
conflict with Contract A: a file that carries them *in addition to* Contract A's five still
satisfies Contract A. A superset is compatible. Only the three renamed labels and the one dropped
section are genuinely in dispute.

## 2. The verdict vocabulary

Per `ADR-007` §2, applied in order; the first branch that fires decides.

- **Branch 1 — amend the contract.** The clause contradicts `AGENTS.md`, a `stable` instruction, or
  another clause of the same command file.
- **Branch 2 — reclassify (wrong artifact class).** The fixture is not an instance of the class the
  clause governs.
- **Branch 3a — amend the contract (relabelling).** The corpus carries the same content under a
  different name *and* offers **a single coherent alternative**.
- **Branch 3b — fix the corpus (omission).** The corpus lacks the declared content. Contract stands,
  case stays failing.
- **Branch 4 — reclassify (no corpus).** A hand-authored counter-example.

One verdict below falls **outside** all five; it is labelled as such rather than forced into branch
1. `ADR-007` names branch 1 as "the loophole to watch," so a finding that does not fit its
enumeration is recorded as not fitting.

### 2.1 Branches 1, 2 and 4, checked first and rejected — with the evidence

**Branch 1 does not fire on Contract A's section names.** Three independent checks:

1. **`AGENTS.md` is silent on `SKILL.md` internal structure.** Its sections are Team Model,
   Lifecycle States, Task Protocol, Artifact Versioning, Checkpoint Protocol, Decision Log,
   Delegation Brief, Blocker Protocol, Validation Gates, Skill Workflow, Code Standards, Security,
   Knowledge Base, MCP Servers, Token Governance. Skills appear only as *things to consult*
   ("check applicable skills in the active platform projection", the mandatory-skill table) and as
   generated projections. No section prescribes headings inside a `SKILL.md`. Verified by reading
   `AGENTS.md`, not taken from the brief.
2. **No `stable` instruction governs it.** The registry lists six instructions —
   `coding-standards`, `git-workflow`, `mechanical-tier-escalation-policy`, `model-routing-policy`,
   `poc-guidelines`, `security-guidelines`. None addresses skill-file structure.
3. **`skillify.md` does not contradict itself.** Its Rounds 1–4 (`Trigger`, `Inputs`, `Steps`,
   `Success Criteria`) map one-to-one onto its template's first four sections, in order. It is the
   internally *consistent* one of the two documents.

**Correction to `plan-073` §1's supporting evidence, which does not change its conclusion.**
`plan-073` §1 says "no skills-format artifact exists (`docs/artifacts/` holds only
`research-agents-skills-ecosystem-v1.md`, which is research, not a contract)." That is not quite
right: `maturity-promotion-criteria-v1.md` §2.1 (carried verbatim into `v2`) **does** mandate one
section of `SKILL.md` structure — a `## Rails` heading with `**Inputs**:`, `**Out of scope**:` and
`**Failure mode**:` sub-items — and `implementation/scripts/check-maturity.py` enforces it. It is a
contract artifact governing skill structure, and it is machine-checked. It still does not make
branch 1 fire, for the reason in §3.6: it is a *promotion gate* (`experimental → beta`, §3.4.2), not
a universal requirement, so a freshly-skillified `experimental` file that lacks `## Rails`
contradicts nothing. The conclusion holds; the stated reason for it was wrong.

**Branch 2 does not fire.** The clause governs `.github/skills/<name>/SKILL.md`. The fixture is
`fixture/.github/skills/verification-before-completion/SKILL.md`, a byte-identical copy of a real
file at literally that path in this repository's tree. In-class, same path, no class disagreement —
and notably this is the one case in the suite that does **not** exhibit the artifact-class
disagreement `command-contract-resolution-v1.md` §5 found in all three open pairs. One caveat,
recorded because it is real and does not change the verdict: `.github/skills/**` in *this* repo is
**generated** by `sync.mjs`, so those files evidence what the generator emits, not what `/skillify`
emits. The case's own survey ran against both trees (`implementation/knowledge/skills/` and
`.github/skills/`) and returned identical results, so the distinction is inert here. See §5.1 for
the separate defect this surfaced.

**Branch 4 does not fire.** There is a large real corpus — 26 skill files, per
`implementation/registry/summary.md` — and the fixture is a real artifact, tagged `real-artifact`
in `case.yaml`. Nothing here is a hand-authored counter-example.

## 3. Resolution table — one row per declared section

### 3.1 `## Trigger` → **`## When to Use`**

| Field | Value |
|---|---|
| **Verdict** | **Amend the contract — relabel** (branch 3a). |
| **Content in dispute?** | **No.** Both contracts collect "when does this activate" in Round 1. Contract B's template renders `## When to Use` as `- <trigger 1>`, `- <trigger 2>` — it *is* the trigger section, under another name. |
| **Single coherent alternative?** | **Yes, and this is the strongest evidence in the whole adjudication.** `## When to Use` is the corpus's name for it: **20/26** repo-wide (`plan-073` §0), and **6 of 6** files read directly in this session (`api-design`, `blocker-escalation`, `checkpoint-protocol`, `plan-approve-execute`, `verification-before-completion`, `worktree-isolation`). One exact heading, no variants observed. `## Trigger` appears **0/26**. |
| **Why not 3b** | Claiming the corpus "omits" activation conditions would be false — every file read carries them, under one shared name. |
| **Effect on the case** | The fixture **gains** this section (it has `## When to Use`). Per-section score moves 0/5 → 1/5. The case still fails. |

### 3.2 `## Inputs` → **unchanged**

| Field | Value |
|---|---|
| **Verdict** | **Fix the corpus — omission** (branch 3b). Contract A stands. |
| **Content in dispute?** | Contract B proposes `## Prerequisites` for the same Round 2 content, so *as between the two contracts* this is a label dispute. |
| **Single coherent alternative in the corpus?** | **No.** `## Prerequisites` is **2/26** repo-wide and **0 of 6** in the files read directly. `## Inputs` is 0/26. The corpus does not carry declared inputs as a section **at all** in 24 of 26 files. |
| **Why 3b, not 3a** | `ADR-007` 3a's second condition is load-bearing and is not met. Renaming `## Inputs` to `## Prerequisites` would be deferring not to the corpus but to **the skill file** — and the skill is not a higher-authority document. It is `experimental` (per `registry/summary.md`), it is not `AGENTS.md`, not a `stable` instruction, and not another clause of the command. Under `ADR-007`'s core rule the command's declared contract is authoritative against everything that is not one of those three. **A 2/26 heading is popularity evidence, and popularity is not authority — least of all a popularity of two.** |
| **Where the corpus *does* carry inputs** | In `## Rails` → `**Inputs**:`, mandated by `maturity-promotion-criteria-v2.md` §2.1/§3.4.2. Observed in `checkpoint-protocol` and `verification-before-completion` (both `stable`) and absent from the four `experimental` files read — consistent with `## Rails` being added at promotion time. This is the repository's own higher-authority vocabulary for input declarations, and it uses the word **Inputs**. That is a tiebreaker *for* Contract A's label, not against it. |
| **Consequence for Contract B** | Because Contract A holds and Contract B has no authority to override it, **the skill file is amended** to `## Inputs` (§4.2). This is where the command-vs-skill disagreement is actually resolved. |
| **Effect on the case** | The fixture has no `## Inputs` section (it has `**Inputs**:` inside `## Rails`, which is not a `##` heading). Still fails. |

### 3.3 `## Steps` → **`## Procedure`** *(the weakest verdict here — read the counter-reading)*

| Field | Value |
|---|---|
| **Verdict** | **Amend the contract — relabel** (branch 3a), held with lower confidence than §3.1. |
| **Content in dispute?** | **No.** All 6 files read carry a stepwise procedure. `## Steps` appears 0/26. Calling this omission would be plainly false. |
| **Single coherent alternative?** | **The word, yes; the exact heading, no.** In 6 files read: `## Procedure` (`api-design`), `## Procedures` (`blocker-escalation`, `checkpoint-protocol`, `worktree-isolation`), `## Gate Procedure` (`verification-before-completion`), `## Procedure Summary` (`plan-approve-execute`). Four heading variants. "Procedure" is unambiguously the corpus's word for stepwise content; the variation is singular/plural and qualifiers. |
| **Why 3a is still the right call** | The dispute is *nothing but a label*: there is no substantive difference between a section named "Steps" and one named "Procedure" holding a numbered procedure. `ADR-007`'s stated purpose for the relabel clause is precisely "shown to dispute nothing but a label." The chosen replacement is not arbitrary: `## Procedure` is what Contract B declares, what the plurality of the corpus uses, and the singular root of every variant observed. |
| **The counter-reading, stated because it is respectable** | Under a strict reading of 3a's second condition — "if the corpus is merely *heterogeneous*, there is nothing to defer to" — four heading variants in six files is heterogeneity, 3a fails, and the verdict falls through to **3b with `## Steps` unchanged**. `command-contract-resolution-v1.md` row A took exactly that strict reading for `/plan`'s headers. **The outcome is identical either way:** the fixture carries neither `## Steps` nor `## Procedure` (its heading is `## Gate Procedure`, which does not contain the substring `## Procedure`), so the case fails on this section under both readings, and neither reading promotes `/skillify`. The verdict is robust to being overruled here. |
| **Constraint on the re-derived checker** | The existing `expect.py` tests membership by substring (`section in text`). That operator must be **kept** — it admits `## Procedures` and `## Procedure Summary`. Switching to an exact-heading regex would be a *strengthening* beyond what this verdict decided, and switching to something looser would be relaxation. Keep the operator; change only the string. |
| **Effect on the case** | Still fails. |

### 3.4 `## Success Criteria` → **unchanged** (and the apparent conflict dissolves)

| Field | Value |
|---|---|
| **Verdict** | **Fix the corpus — omission** (branch 3b). Contract A stands, unamended. |
| **Is this actually a command-vs-skill conflict?** | **No — and this is the finding that most changes the shape of the adjudication.** `T527`'s brief and `plan-073` §1 both treat `## Success Criteria` as a section Contract A declares and Contract B does not. But Contract B's **Round 4** declares it verbatim: *"Output: `## Success Criteria` — `<criterion 1>` `<criterion 2>`"*. Contract B's own final template then omits it. **The two contracts agree that a skill file must carry success criteria. The only document that drops it is Contract B, contradicting Contract B.** |
| **Why the contract is not relaxed** | `ADR-007` §5 forbids resolving by deleting a required field. The merits argument for deletion was considered and **fails**: the section is not a unilateral invention of one document — two independently-authored contracts both interview for it, so it is the one section with *double* declared backing. Deleting it would also propagate Contract B's internal defect into Contract A. **The section should have been declared, was declared twice, and stays.** |
| **Corpus** | **3/26** repo-wide, and that figure is an **upper bound** — see §5.2. In 6 files read directly, the exact heading appears as a real section **0 times**; its one appearance (`plan-approve-execute`) is inside a fenced ```` ```markdown ```` block illustrating a *plan document* template, which the substring survey cannot distinguish from a real heading. The true count is plausibly 1–2 of 26. This is omission by a wide margin. |
| **Consequence for Contract B** | **The skill file is amended** to restore `## Success Criteria` to its template (§4.2). This is a *strengthening* of Contract B and cures a self-contradiction; it is not relaxation of anything. |
| **Effect on the case** | Still fails. This is the section that guarantees the case cannot go green on any reading. |

### 3.5 `## Examples` and `# <Skill Name>` → **unchanged, no conflict**

| Field | Value |
|---|---|
| **Verdict** | **No conflict between the contracts.** Against the corpus, `## Examples` is **fix the corpus** (branch 3b). |
| **Why** | Both contracts declare `## Examples` and a level-1 title, identically. There is nothing to adjudicate. Corpus: `## Examples` **9/26** (3 of 6 read directly: `blocker-escalation`, `checkpoint-protocol`, `plan-approve-execute`). The near-miss `## Example: Batch Parallel Execution Workflow` (`worktree-isolation`) is one file, not a rival convention, and `ADR-007` 3a's second condition is not met by a sample of one. Level-1 title: present in 6/6 read and required by every projection. |
| **Effect on the case** | The fixture has a level-1 title (passes) and no `## Examples` (fails). |

### 3.6 YAML frontmatter → **added to Contract A** *(outside ADR-007's five branches)*

| Field | Value |
|---|---|
| **Verdict** | **Amend the contract by addition.** This does not fit any of `ADR-007`'s five branches and is labelled as such rather than forced into branch 1. |
| **The gap** | Contract A says "generate `.github/skills/<name>/SKILL.md` **with this structure**" and the block begins at `# <Skill Name>`. A file produced exactly to that structure has **no YAML frontmatter**. |
| **What that breaks** | `name` and `description` frontmatter is universal and load-bearing: **26/26** corpus files carry it in both trees (6/6 confirmed by direct read, including the golden fixture); Contract B declares it in its template *and* states it as a rule — *"Every skill must have the YAML frontmatter with `name` and `description`"*; `implementation/knowledge/schemas/skill.schema.json` makes `name` and `description` required with `additionalProperties: false`; `implementation/registry/summary.md` is generated from it; and `/discover-skills` reads the registry it produces. A frontmatter-less skill file is not discoverable by the very command that exists to find it. |
| **Why not branch 1** | Branch 1's enumeration is `AGENTS.md`, a `stable` instruction, or another clause of the same command file. A JSON schema plus a projection convention is **none of those**, however strongly enforced. Calling it branch 1 would stretch the branch `ADR-007` itself flags as the one to watch. The honest description is: the contract is *silent* where every other authority is emphatic, and silence is a gap, not a contradiction. |
| **Why amending anyway is safe under `ADR-007` §5** | §5 prohibits *relaxing* a check — "deleting required fields, loosening a regex, or admitting a second form." This adds a required element and removes none. The amended contract is strictly stronger than the one it replaces. |
| **What is added, precisely** | `name` and `description` only — **not** `maturity`. Verified from the fixture: `.github/skills/verification-before-completion/SKILL.md` carries `name` + `description` and **no** `maturity`, while its source `implementation/knowledge/skills/*/SKILL.md` does carry `maturity`. `sync.mjs` strips it during projection. Contract A writes to the **projection** path, so requiring `maturity:` there would have been wrong. Contract B's template is already correct on this point and is **not** changed. |

### 3.7 `## Rails` → **recommended, deliberately NOT executed**

| Field | Value |
|---|---|
| **Verdict** | **No amendment made.** Recorded as a recommendation with its counter-argument, for a future version to decide. |
| **The finding** | `maturity-promotion-criteria-v2.md` §2.1 requires a `## Rails` heading with `**Inputs**:`, `**Out of scope**:` and `**Failure mode**:`, machine-checked by `implementation/scripts/check-maturity.py`. **Neither contract declares it.** A skill produced by either contract can therefore never leave `experimental` without a later hand-edit — which is a real ergonomic defect in both. |
| **Why it was not executed** | §3.4.2 places `## Rails` at the **`experimental → beta`** gate, not at creation. A newly skillified file is legitimately `experimental`, so omitting `## Rails` contradicts nothing — it just defers work. That reading is at least as strong as the opposite one, and `ADR-007` warns that branch 1 is "the branch a motivated reader would reach for." **Executing a contested amendment on a section I would benefit from declaring is precisely the incentive `ADR-007` §Context names.** Under-reaching here is the correct error to make. |
| **Recommendation** | A follow-up should add `## Rails` to **both** templates, with a one-line note that it is what a skill needs to reach `beta`. If taken, it is additive and §5-safe, and it would also give §3.2's `## Inputs` a second, tier-appropriate home. |

## 4. What was executed

### 4.1 `implementation/knowledge/commands/skillify.md` — amended

One block changed: `### Generate the Skill File`. Section **count is unchanged at five**; ordering is
unchanged; two labels change; frontmatter is added. A mapping sentence is added so the interview
round headings (`Round 1 — Trigger`, `Round 3 — Steps`) do not silently mismatch the renamed output
sections. The round headings themselves are **not** renamed: they name interview topics, not output
sections, and renaming them would blur which document the verdict acted on.

| Before | After | Branch |
|---|---|---|
| *(no frontmatter)* | `name` + `description` frontmatter | §3.6 — addition |
| `# <Skill Name>` | `# <Skill Name>` | no conflict |
| `## Trigger` | `## When to Use` | 3a |
| `## Inputs` | `## Inputs` | 3b |
| `## Steps` | `## Procedure` | 3a |
| `## Success Criteria` | `## Success Criteria` | 3b |
| `## Examples` | `## Examples` | no conflict |

### 4.2 `implementation/knowledge/skills/skillify/SKILL.md` — amended

Two changes, both **strengthening**, both curing a contradiction between the file's own `## Procedure:
The 4-Round Interview` section and its `## SKILL.md Template` section:

1. **`## Prerequisites` → `## Inputs`**, in *both* the Round 2 output block and the template — per
   §3.2, Contract A holds the label and Contract B yields.
2. **`## Success Criteria` restored to the template**, between `## Procedure` and `## Examples` —
   per §3.4, the file's own Round 4 declares it and its template dropped it.

### 4.3 The result: the two contracts are reconciled

After §4.1 and §4.2, Contract B's template is a **strict superset of Contract A's, in the same
relative order**:

| | Contract A (amended) | Contract B (amended) |
|---|---|---|
| frontmatter | `name`, `description` | `name`, `description` |
| title | `# <Skill Name>` | `# <Skill Title>` |
| | — | `## Purpose` |
| 1 | `## When to Use` | `## When to Use` |
| 2 | `## Inputs` | `## Inputs` |
| 3 | `## Procedure` | `## Procedure` |
| 4 | `## Success Criteria` | `## Success Criteria` |
| 5 | `## Examples` | `## Examples` |
| | — | `## Edge Cases` |
| | — | `## Guidelines` |

**Any file generated by following the skill now satisfies the command.** The two-contracts-for-one-
artifact condition that `case.yaml`'s `known_failing_reason` describes no longer exists. What
remains is a single agreed contract and a corpus that does not follow it — an ordinary branch 3b
standing red.

### 4.4 What was NOT executed, and why

| Not done | Reason |
|---|---|
| `tests/golden/open/skillify-skill-file-template-drift/expect.py` | **Required, and refused.** `T527` §5 states `expect.py` is not authorized and instructs a blocker instead. `protected-paths-v1.md` §5 item 1 forbids a silent edit and item 2 requires a named authorization. See §6. |
| `case.yaml` status flip | The verdict does **not** make `check()` return `True` (§5.3). §5's grant is conditional on a genuine pass. Flipping it would be false. |
| `case.yaml` `known_failing_reason` rewrite | Its text is now stale (§5.4) but the grant covers only the status flip and removal of `known_failing_*` keys on a genuine pass. Rewriting the reason on a still-failing case is outside it. |
| `brief.md` restatement | The grant reads "restate the expected outcome **to match**" — i.e. to match a flip that is not happening. Its §"Why this is known_failing today" is now factually wrong (§5.4) and needs a follow-up with its own authorization. |
| `## Rails` in either template | §3.7 — contested reading, deliberately under-reached. |
| `## Required Context` in Contract B | Contract B's Round 2 declares `## Required Context` and its template omits it — the *same* defect shape as §3.4. Left alone on purpose: unlike `## Success Criteria`, it is not one of the five disputed sections, so fixing it is outside this adjudication. Recorded for a follow-up. |
| The `.github/` output-path question | §5.1 — a real defect, but resolving it changes the declared path and therefore `expect.py`. Out of grant. |
| Platform projections (`.claude/`, `.github/`, `.gemini/`, …) | Generated by `sync.mjs`; `AGENTS.md` forbids hand-editing. They will show drift until the generator is re-run. |

## 5. Corpus re-verification, method limits, and what had drifted

**Method, stated plainly and up front: this session had no shell, no `grep`, and no directory
listing.** Every figure below is either (a) carried from `plan-073` §0 and labelled as carried, or
(b) derived by reading named files directly with a file reader. Nothing here was re-counted across
all 26 files. **Six files were read in full**, chosen for spread across maturity and age:
`api-design` (experimental), `blocker-escalation` (experimental), `checkpoint-protocol` (stable),
`plan-approve-execute` (experimental), `verification-before-completion` (stable, via the golden
fixture's byte-identical copy), `worktree-isolation` (experimental). The skill inventory came from
`implementation/registry/summary.md`, which lists exactly 26 skills.

### 5.1 Findings that change or qualify the inputs

| Claim | Finding | Verdict on the claim |
|---|---|---|
| `T525` closure / `active-tasks.md`: the corpus "uniformly follows" the skill's template, "26 of 26 follow" | **Wrong, as `plan-073` §0 already established.** Directly confirmed: of 6 files read, **zero** satisfy Contract B completely. `api-design` has no `## Purpose`, no `## Examples`, no `## Prerequisites`, no `## Edge Cases`, no `## Guidelines`. `verification-before-completion` has none of `## Prerequisites`, `## Procedure`, `## Examples`, `## Edge Cases`, `## Guidelines`. | **Materially overstated; already corrected by `plan-073` §0. Confirmed here.** |
| `plan-073` §0 / `T527` §2: 0/26 satisfy Contract A; 1/26 satisfies Contract B; per-section 20/16/16/9/2/1 | **Consistent with everything read.** 6/6 have `## When to Use`; 5/6 have `## Purpose`; 3/6 have `## Examples`; 0/6 have `## Prerequisites`; 0/6 have `## Edge Cases`. Direction and rough magnitude all hold. | **Sound, within sampling error.** |
| `T527` §1 and `plan-073` §0: the skill declares a **six**-section template | **Incomplete.** The template declares **seven** `##` sections — `## Guidelines` was omitted from both restatements — plus YAML frontmatter and a level-1 title. Does not change any verdict (`## Guidelines` is a superset extra, §1), but the "1 of 26 satisfies it completely" figure is measured against whichever list was used, and the two lists differ. | **Understated by one section.** |
| `plan-073` §1: "no skills-format artifact exists" | **Not correct.** `maturity-promotion-criteria-v1.md` §2.1 / v2 §3.4.2 mandates `## Rails` and `check-maturity.py` enforces it. The branch-1 conclusion still holds, for the different reason given in §2.1/§3.7. | **Wrong premise, right conclusion.** |
| The survey method itself (`case.yaml`, `brief.md`, and the reproduction script in `brief.md` §Provenance) | **Systematically inflates every count.** The script tests `h in f.read_text()` — plain substring containment over the whole file, including fenced code blocks. `plan-approve-execute` contains `## Success Criteria`, `## Dependency Graph` and `## Open Questions` **only inside a ```` ```markdown ```` fence illustrating a plan document**, and contains `## Procedure` only as a prefix of `## Procedure Summary`; `blocker-escalation`, `checkpoint-protocol` and `worktree-isolation` match `## Procedure` only via `## Procedures`. **All published per-section counts are upper bounds.** | **A real methodological defect. It biases every count *toward* conformance, i.e. toward a green — so correcting it can only make the case more firmly red, never less.** |

### 5.2 The consequence for `## Success Criteria`

The 3/26 figure is the one most affected. Of the 6 files read, the heading appears zero times as a
real section and once inside a fence. If that ratio is representative, the true count is 1–2 of 26,
not 3. This *strengthens* §3.4's branch-3b verdict; it does not weaken it. No verdict here depends
on the exact number.

### 5.3 Does the case pass? **No — under both readings of §3.3.**

The fixture is `.github/skills/verification-before-completion/SKILL.md`. Its real sections are
`## Rails`, `## Purpose`, `## When to Use`, `## Iron Rule`, `## Gate Procedure`,
`## Claim → Evidence Map`, `## Red Flags — Stop`, `## emage.code Standard Commands`,
`## Orchestrator Enforcement`.

| Required (amended) | Fixture | Result |
|---|---|---|
| level-1 title | `# Verification Before Completion` | pass |
| `## When to Use` | present | **pass** (was fail) |
| `## Inputs` | only `**Inputs**:` inside `## Rails` | fail |
| `## Procedure` | `## Gate Procedure` — does not contain the substring `## Procedure` | fail |
| `## Success Criteria` | absent | fail |
| `## Examples` | absent | fail |

**1 of 5.** Under the §3.3 counter-reading (`## Steps` retained) it is also 1 of 5. Under the
*current, unamended* `expect.py` it is 0 of 5. `check()` returns `False` in all three cases.
**`case.yaml` is not flipped, and nothing under `tests/golden/**` was touched.**

### 5.4 What is now stale in the case's own files

Both will be wrong once this lands, and **neither is fixed here** (§4.4):

- `case.yaml` `known_failing_reason` — asserts "The real corpus uniformly follows a different
  template" (false, per §5.1) and frames the defect as "two declared contracts disagree" (no longer
  true after §4.3). Its accurate replacement is a plain branch-3b statement: *the corpus does not
  carry the declared sections; exit is to author a conforming skill file and re-fixture.*
- `brief.md` — its `## What this checks` quotes the pre-amendment template verbatim, its
  `## Pass condition` lists the pre-amendment section names, and its `## Why this is known_failing
  today` contains the same "uniformly structured to a different template" claim.

This is the same defect shape as `T530` (stale `new-feature-real-checkpoint-format-drift` brief) and
should be folded into the same authorization.

### 5.5 A separate defect the branch-2 check surfaced (not adjudicated here)

Contract A declares its output path as `.github/skills/<name>/SKILL.md`. In **this** repository that
directory is generated by `sync.mjs`, and `AGENTS.md` states per-platform folders "are **generated**
… **Do not edit them by hand**" — so a `/skillify` output written there is destroyed by the next
sync, and the source under `implementation/knowledge/skills/` never receives it. In an installed
**target** project the same path is correct, because a target has only projections. The clause is
therefore right for one audience and wrong for the other, and it also hardcodes one platform out of
seven (`.claude/skills/`, `.cursor/skills/`, `.gemini/skills/`, `.opencode/skills/`, `.pi/skills/`,
`.cline/skills/` are equally valid targets per `AGENTS.md`'s own Skill Workflow list).

**Not adjudicated here** because it is a path question, not the template conflict `T527` convened
over, and because any resolution changes the glob in `expect.py` — the same authorization boundary
as §6. Recommended as its own task with an `ADR-007` adjudication of its own.

## 6. Blocker — `expect.py` must be re-derived, and this task refused to do it

- **Type:** `technical` · **Severity:** `major` · **Status:** open, escalated, not worked around.

§4.1 changes two of the five strings in `expect.py`'s `REQUIRED_SECTIONS`. Until it is re-derived,
the checker tests a **superseded** contract: it would assert `## Trigger` and `## Steps`, which no
document declares any more. The case returns `False` either way, so nothing is currently *mis*-
reported — but the check has stopped being a check of the live contract, and that is a real defect
with a deadline, not a cosmetic one.

`T527` §5 excludes `expect.py` from this task's grant and instructs a blocker instead;
`protected-paths-v1.md` §5 item 2 requires a named, orchestrator-authored authorization. **The §5
table was not widened and `expect.py` was not touched**, matching `T520` and `T523`.

**Exact specification for the authorized follow-up** — same element count, same operator, same
ordering guarantees, no loss of strength:

```python
REQUIRED_SECTIONS = (
    "## When to Use",     # was "## Trigger"
    "## Inputs",          # unchanged
    "## Procedure",       # was "## Steps"
    "## Success Criteria",# unchanged
    "## Examples",        # unchanged
)
```

Everything else in the file — the `TITLE_RE` check, the `is_dir()` guard, the
`len(candidates) != 1` guard, the `all(section in text …)` substring operator, `main()` — stays
**byte-identical**. Five elements before, five after. `ADR-007` Validation criterion 1 ("no check is
weaker") is satisfied by construction. The module docstring's quoted clause must be updated to the
amended template in the same edit. The follow-up should also carry §5.4's `case.yaml` and `brief.md`
corrections, and must re-confirm that `check()` still returns `False` — it will.

## 7. Summary

| Element | Verdict | Branch | Contract changed? | Effect on the case |
|---|---|---|---|---|
| `## Trigger` | relabel → `## When to Use` | 3a | Contract A | fail → **pass** |
| `## Inputs` | fix the corpus | 3b | no (Contract B yields) | fail |
| `## Steps` | relabel → `## Procedure` | 3a *(weak; 3b counter-reading changes nothing)* | Contract A | fail |
| `## Success Criteria` | fix the corpus | 3b | no (Contract B's omission cured) | fail |
| `## Examples` | fix the corpus | 3b | no | fail |
| level-1 title | no conflict | — | no | pass |
| YAML frontmatter | add to the contract | *outside the five branches* | Contract A | not checked |
| `## Rails` | recommend only | — | **no — deliberately** | not checked |

**Net: 2 relabelled, 3 upheld against the corpus, 1 gap closed by addition, 1 contested amendment
declined. The two contracts are reconciled into one (§4.3). The golden case scores 1 of 5 and stays
`known_failing` / `tracked_defect`.**

**Promotion outcome, stated plainly: `/skillify` does NOT become promotable.**
`maturity-promotion-criteria-v2.md` §3.5's golden-case half still fires — an unresolved
`known_failing` + `tracked_defect` case names `command: /skillify` — so `/skillify` fails command
criterion 7, and criterion 4's evidence is a case it does not pass. It is also still
`maturity: experimental` and has not met the `experimental → beta` bar. This was the expected and,
on the evidence, the correct outcome; no attempt was made to engineer a green, and §5.1's discovery
that the survey method biases *toward* conformance means the honest numbers are worse than the
published ones, not better.

**Recommended exit, per `ADR-007` 3b:** author one skill file that genuinely conforms to the
now-single contract and re-fixture the case against it. Promotion earned by producing the output the
command promises — not by editing the test.

## 8. Consumed by

- The authorized follow-up implementing §6 (`expect.py` re-derivation) and §5.4 (`case.yaml`
  `known_failing_reason`, `brief.md`) under a `protected-paths-v1.md` §5 grant naming those files.
- A follow-up for §3.7 (`## Rails` in both templates) and §4.4's `## Required Context` — neither
  requires a protected-path grant.
- A separate task for §5.5 (the `.github/` output-path question), which does.
- `plan-073` §2's `T527` row, and any re-run of `implementation/scripts/check-maturity.py` — which
  must be re-run for real before any promotion claim. **No promotion should be granted on this
  document alone.**
