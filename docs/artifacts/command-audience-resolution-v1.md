# Artifact: command-audience-resolution-v1.md

> Filename: `command-audience-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T546
- **Created**: 2026-09-26
- **Based on**: the T546 delegation brief as dispatched (no `docs/tasks/task-T546.md` exists on this
  branch — see §1.1); `docs/decisions/ADR-007-command-contract-authority.md` (the decision whose
  branch 1 this document's per-command verdicts invoke);
  `docs/artifacts/batch-manifest-resolution-v1.md` (the shape this document follows, and §3.2's
  namespace-minting ground, applied in §7); `docs/artifacts/skillify-contract-resolution-v1.md`
  §§0–1 (the sibling adjudication on the same command);
  `docs/tasks/task-T532.md` §3 (the brief that raised this class question and deferred it);
  `docs/tasks/active-tasks.md`; all 19 of `implementation/knowledge/commands/*.md`;
  `implementation/knowledge/schemas/command.schema.json`;
  `implementation/platforms/{claude-code,cline,cursor,gemini,github,opencode,pi}.json`;
  `implementation/scripts/sync.mjs`; `implementation/scripts/generate-registry.py`;
  `implementation/scripts/check-maturity.py`; `implementation/registry/index.json`;
  `implementation/registry/summary.md`; `scripts/install.sh`;
  `scripts/render_installed_agents.py`; `tests/functional/test_schemas.py`;
  `implementation/docs/tasks/validate-tasks.py` (existence only); `AGENTS.md` (read, not edited —
  T545 owns it).
- **Supersedes**: none (first version)

## 0. Method, and the limits on every claim below

**This session had no shell.** No `grep`, no `find`, no directory listing, no test run, no validator
run, no script execution. I hold `read`/`edit`/`web` and no `execute`. **Every finding below was
derived by reading the files named in the Metadata block, by name.** I ran nothing and I claim no
verification that would require running anything.

Three consequences, stated once here and relied on throughout:

1. **I assert no counts of things I could not enumerate.** Where a count appears (19 commands, 6
   command-projecting platforms, 7 platform manifests) it is derived from a file that states it —
   `implementation/registry/summary.md`'s `commands: 19` line and its 19 `| … | command | … |` rows,
   and the seven manifest files I opened individually by name.
2. **I assert no absences** of the form "nothing else references X", with one exception that is
   labelled as such: where I say a string "is not in" a list, I mean *the list I read in full and
   quote*, not the repository.
3. **`tests/golden/**` was not read at all.** Not `case.yaml`, not `expect.py`, not any fixture. I
   hold no authorization for that tree, not even to read it. Wherever a verdict here plausibly
   invalidates a golden checker, that is recorded as a blocker in §10 and **not** estimated.

## 1. Corrections to the brief, stated first

The brief instructs that any defect in it be reported rather than worked around, and predicts §2.2's
table and §4's reading of `check-maturity.py` as the likeliest sites. Both predictions were right,
and there are four further corrections. Ordered by consequence.

### 1.1 The premise is chronologically inverted: **T532 has not run.** *(major)*

The brief's §2 states: *"T532 fixed one instance: `/skillify` told authors to write a new skill to
`.github/skills/<name>/SKILL.md` … ADR-007 branch 1 fired and the contract was amended to a two-row
rule with a precondition."*

**None of that has happened on this branch.** Read by name:

- `docs/tasks/active-tasks.md` line 6: `| T532 | Adjudicate /skillify's declared output path |
  solution-architect | pending | P2 | T531 | 2026-09-25 |` — **`pending`**, not archived.
- `docs/tasks/task-T532.md` line 5: `**Status:** pending`. Its §4 deliverable
  `docs/artifacts/skillify-output-path-resolution-v1.md` **does not exist** (read attempt failed).
- `implementation/knowledge/commands/skillify.md` still says `.github/skills/<name>/SKILL.md` in
  **two** places: the frontmatter `description` (line 2) and the body (line 30). There is no
  two-row rule and no precondition in that file.

What *has* run is **T527**, whose artifact `skillify-contract-resolution-v1.md` amended the
`SKILL.md` **section template** (its §1 quotes the pre-amendment `## Trigger`/`## Steps` form, and
the live file now reads `Round 1 → ## When to Use … Round 3 → ## Procedure`). The **path** was
explicitly left to T532.

This is not a bookkeeping quibble; it changes what this document is for. The brief frames T546 as
generalising a solved instance. In fact **T532 is open and unexecuted, and T532's own brief §3 is
where this class question comes from**, verbatim:

> So the real question is: **does this command's contract address the authoring repo, the target
> project, or both — and does it say so anywhere?** Survey the other commands… If it is undeclared
> across the board, that is a larger finding than this one command and worth saying so.

So the correct ordering is the one that is actually happening: **T546 decides the class, and T532
then applies it to `/skillify`.** The brief's "two-row rule with a precondition" is therefore a
*candidate answer*, not a delivered one, and it is evaluated on the merits in §5.2 — where it turns
out to be **half a fix**, because its target-audience branch writes to a tree that
`install.sh --update` deletes (§7).

**Action for the orchestrator:** `docs/tasks/task-T532.md` should be amended to cite this artifact
before T532 is dispatched, or T532 will re-derive the class question from scratch. I did not amend
it — it is not in my write scope.

### 1.2 §4's reading of `check-maturity.py` is wrong in mechanism, right in conclusion *(minor, but load-bearing for §8)*

The brief says: *"`check-maturity.py:_ledger_defect` filters on `DECLARED_PRIORITIES =
{"P0","P1"}` **before** reading `**Affects:**`. So at P2 the declaration is **recorded but
inert**."*

Read from the file, two distinct mechanisms are conflated:

- `DECLARED_PRIORITIES` (line 413) is used in **exactly one place**: `_collect_ledger_declarations`
  (line 475, `required = row["priority"] in DECLARED_PRIORITIES`). Its only job is to decide whether
  a missing `**Affects:**` field is a **hard error**. It is *not* the filter in `_ledger_defect`.
- `_ledger_defect`'s filter is line 504, `if row["priority"] not in priorities: continue`, where
  `priorities` is the **parameter** passed by `_open_defect` (line 533): `{"P0","P1"}` when
  `include_p1` else `{"P0"}`. This is the line `active-tasks.md`'s own T524 note cites correctly
  ("`check-maturity.py:504` filters the ledger-defect scan by priority").
- **The declaration at P2 is read, parsed and validated — not skipped.** `_collect_ledger_declarations`
  iterates *every* non-`done`/`cancelled` active row at *any* priority, and where the field is
  present it calls `_parse_affects` and stores the result. The docstring at lines 47–51 and 465–467
  is explicit: a malformed entry, **or one naming a component that does not exist, at any
  priority**, raises `LedgerDeclarationError` → `main()` returns **exit 2 with no component report
  at all**.

So "recorded but inert" understates the first half and is right about the second. Precisely: at P2 a
declaration is **recorded, schema-validated against the real component-id set, and inert for
criteria 3 and 7 only.** T546's three declared ids (`command/discover-skills`, `command/handoff`,
`command/prepare-release`) are all real per `implementation/registry/summary.md`, so the declaration
as described is safe — it will not trip the fail-closed path.

### 1.3 §4's consequence claim is wrong about the owning agents *(major — it changes the size of the P1 option)*

The brief says: *"At P1 the maturity gate would go red for `/discover-skills` and `/handoff`, both
currently `stable`, **plus their owning agents under criterion 7**."*

**The owning agents would not go red.** Chain, read from the files:

1. All three commands declare `agent: "orchestrator"` (`discover-skills.md:3`, `handoff.md:3`,
   `prepare-release.md:3`). There is exactly **one** owning agent, not several.
2. `implementation/registry/summary.md:26`: `| orchestrator | agent | experimental | … |`.
3. `check-maturity.py:783`: `if component.maturity in ("deprecated", "experimental"): return
   failures` — an early return **before** `BETA_CRITERIA` and therefore before criterion 3, and long
   before `STABLE_CRITERIA`'s criterion 7.

So `orchestrator` is exempt from both defect criteria at its current maturity. By the same early
return, **`/prepare-release` is also exempt** — it is `experimental`.

**At P1, exactly two components would go red: `command/discover-skills` and `command/handoff`.**
Not two plus agents. This matters because it is the whole of what P1 buys, and §8 weighs it.

### 1.4 "The `keepKeys` list in each of **seven** platform manifests" — it is six, and the edit is not needed at all *(major — it halves the headline blast radius)*

Read individually, all seven: `cline.json` has **no `fileMap.commands`** and **no
`frontmatter.commands`**. Its `fileMap` is `instructions` (rootRelative `.clinerules`) and `skills`
only. `sync.mjs:493` emits commands only `if (manifest.fileMap.commands)`.

**Commands project to six platforms, not seven.** So 19 × 6 = 114 command projections exist, not 133.

And the stronger point, in §5.3: **no manifest needs editing.** `maturity:` is already a source-only
frontmatter key — it appears in **none** of the six `frontmatter.commands.keepKeys` lists I read, and
`applyGenericFrontmatter` (sync.mjs:297-299) drops every key not in `keepKeys`. Confirmed
empirically by reading a projection: `.claude/commands/discover-skills.md`'s frontmatter carries
`description` and `argument-hint` and **neither `agent:` nor `maturity:`**, exactly as
`claude-code.json`'s `"keepKeys": ["description", "argument-hint"]` predicts. `audience:` rides
identical rails for zero manifest edits.

### 1.5 The command schema's real path — and a hard ordering constraint the brief does not mention *(major)*

The brief correctly warns against assuming `implementation/knowledge/_schemas/command.schema.json`.
The real path is **`implementation/knowledge/schemas/command.schema.json`**, derived from
`check-maturity.py:881` (`schemas_dir=source_root / "schemas"`, where `source_root` is
`implementation/knowledge` per `generate-registry.py:_determine_source`) and confirmed by
`tests/functional/test_schemas.py:21` (`knowledge_root() / "schemas" / f"{name}.schema.json"`).

The constraint the brief omits, and the single most important implementation fact in this document:

```json
  "required": ["description", "maturity"],
  "properties": { "description": …, "agent": …, "argument-hint": …, "maturity": … },
  "additionalProperties": false
```

**`additionalProperties: false`.** Two independent consumers enforce it:
`tests/functional/test_schemas.py::test_command_frontmatter` validates **all 19** commands
unconditionally, and `check-maturity.py::_check_schema` is criterion 1 for every non-`experimental`
component. So **the schema edit and the first `audience:` key must land in the same commit**, or the
functional suite goes red for every command carrying the key. §5.3 costs this.

### 1.6 `install_docs`'s "never overwrites" holds only on `--update` *(minor, and it strengthens §7)*

§2.1 says *"`install_docs` uses `rsync -a --ignore-existing` — never overwrites, never deletes."*
That is the `--update` branch (`install.sh:381-390` → `merge_tree_preserve_existing` at 219-233).
The **fresh-install** branch is `copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs"` (line 392),
whose rsync args are `(-a)` with no `--delete` and no `--ignore-existing` (lines 118-129) — so a
fresh run **overwrites same-named files** under `docs/`, though it still deletes nothing.

This does not weaken the durability claim in §7; it sharpens it. A hand-written file under `docs/`
with **no upstream counterpart** is never overwritten (nothing to overwrite it with) and never
deleted (no `--delete` in either branch). `docs/**` is genuinely durable under both modes. The
correction matters only for hand-edits to files the harness *does* ship there.

### 1.7 §2.2's table is otherwise correct, and I confirm each row from the files

| Row | Verified how | Verdict |
|---|---|---|
| `/discover-skills` step 1 names `implementation/registry/index.json`; `stable` | `discover-skills.md:5` (`maturity: stable`), `:12` (step 1 verbatim), `:43` (`## Rails` **Inputs** names it again) | **Confirmed**, and worse than stated: the path appears **twice**, in step 1 and in `## Rails`, so a repair must touch both. |
| `/handoff` step 3 names `implementation/runtime/handoff/schema-v1.json`; `stable` | `handoff.md:5`, `:14` | **Confirmed.** |
| `/prepare-release` steps 6–7 name `implementation/scripts/generate-registry.py` and `scripts/verify-release-docs.py`; `experimental` | `prepare-release.md:5`, `:30-31`, `:40` | **Confirmed**, and it also names `implementation/registry/summary.md` (line 30) — three uninstalled paths, not two. |
| `/skillify` was the only command naming a target-project path as a **write** target | 19 files read | **Contradicted — see §1.8.** |

### 1.8 A fourth broken command the brief does not name: `/consolidate-memory` *(major)*

`/consolidate-memory` is **`stable`** (`consolidate-memory.md:5`) and its step 5 instructs a
**write**:

> - **Promote**: append the content to the appropriate section of `AGENTS.md` or the relevant doc,
>   then remove from memory

In a target project, `$TARGET/AGENTS.md` is **regenerated on every install and every `--update`** by
`install_agents_doc` (install.sh:396-410) → `scripts/render_installed_agents.py`, which
unconditionally `dest.write_text(rendered, …)` (line 174) from `$IMPLEMENTATION/AGENTS.md`. So a
promotion written there **succeeds, and is silently destroyed by the next `install.sh --update`** —
and the memory entry has already been deleted ("then remove from memory"), so the content is gone
from both places.

This is the *same pathology* as `/skillify` — an authoring act aimed at a derived tree — with two
aggravations: it is `stable` rather than `experimental`, and it is **destructive** (the source is
deleted after the copy) rather than merely futile. It is also the case that proves §6's point that
an existence precondition is not the general answer: `AGENTS.md` **exists** in both audiences, so no
existence test detects the divergence. What differs is *authority*, not presence.

`/skillify` is therefore **not** the only command naming a target-project path as a write target. It
is the only one naming a *platform-projection* path as one.

### 1.9 Two adjacent defects found while surveying, reported not acted on

1. **`04-protocols.md` is cited by three commands and I could not find it.** `/new-project` steps 1
   and 17, `/new-feature` step 1, and `/new-poc` step 1 all reference `04-protocols.md §
   Plan-Approve-Execute` / `§ Validation Gates`. `/validate-workflow` step 5 does too. Two of those
   four commands (`/new-project`, `/new-feature`) are **`stable`**. I probed
   `docs/04-protocols.md` and `implementation/docs/04-protocols.md`; **neither exists.** I cannot
   grep, so **whether it exists anywhere else is unevidenced** — it may live under `docs/wiki/` or be
   a legacy v2 filename. Either way it is a *dangling-reference* defect, a different class from
   audience (it is wrong in **both** audiences, like `/skillify`'s path), and it needs its own row.
2. **`/validate-tasks` (a `both` command) routes to `/prepare-release` (an `authoring` command).**
   Its step 2 is "Before `/prepare-release`". Once `/prepare-release` is declared `authoring` (§6),
   that instruction is inert in a target project. Harmless — an instruction naming an absent command
   does nothing — but it is the first instance of a cross-audience routing reference, and §4.3
   records it as a class.

Also noted, not a defect I can act on: every `implementation/platforms/*.json` declares
`"$schema": "./_manifest.schema.json"`, and **that file does not exist** (probed twice). Benign —
`sync.mjs:608` skips `_`-prefixed files, and `generate-registry.py::_detect_platforms` returning
exactly the 7 platforms in `index.json` confirms there is no eighth `*.json` there — but the `$schema`
pointer is dangling in all seven.

## 2. The finding, re-derived: what "audience" is, mechanically

### 2.1 The two audiences, and the exact boundary between them

An audience is not a preference; it is a fact about which files exist. Read from `scripts/install.sh`
(`install_common` at 433-437 plus the seven `install_*` functions at 439-475), what leaves this
repository is exactly:

| Installed | Mechanism | Overwrite/delete behaviour |
|---|---|---|
| `implementation/docs/**` → `$TARGET/docs/**` | `install_docs` (379-394) | fresh: `rsync -a`; `--update`: `rsync -a --ignore-existing`, except `tasks/` → `merge-task-docs.py` |
| `implementation/AGENTS.md` → `$TARGET/AGENTS.md` | `install_agents_doc` → `render_installed_agents.py` | **regenerated every run**, six regex substitutions |
| `implementation/CLAUDE.md` → `$TARGET/CLAUDE.md` | `install_claude_code` (468) | plain `cp` |
| `implementation/runtime/memory`, `implementation/runtime/security` → `$TARGET/implementation/runtime/…` | `install_mcp_server_runtime` (423-431) | `install_tree_into`, excludes `_index`, `__pycache__` |
| `implementation/.<platform>/**` → `$TARGET/.<platform>/**` | seven `install_*` functions | `--update`: `rsync -a --delete` + per-platform excludes |
| MCP config files | `merge_or_copy_mcp_json` (357-377) | merged, not replaced |

**Not installed, confirmed by reading every `install_*` function and finding no reference:**
`implementation/knowledge/`, `implementation/registry/`, `implementation/runtime/handoff/`,
`implementation/platforms/`, `implementation/scripts/`, top-level `scripts/`, `tests/`.

One subtlety that matters for §6: **`$TARGET/implementation/` does exist** in an installed project —
`install_mcp_server_launch` creates it and `__init__.py` (lines 424-427). So a discriminator of the
form "does `implementation/` exist" is **false as a discriminator**; it must name
`implementation/knowledge/` or `implementation/registry/` specifically. §6 relies on this.

### 2.2 The survey: all 19 commands, read individually

`implementation/registry/summary.md` lists exactly 19 `command` rows and I read all 19 source files.
"Worst leak" classifies by the most serious problem, not exhaustively.

| # | Command | Maturity | Recommended `audience` | Worst leak |
|---|---|---|---|---|
| 1 | `batch` | experimental | `both` | **soft**: cites `commands/plan.md`, a source-tree path (§2.3 class C) |
| 2 | `bug-report` | stable | `both` | none — `docs/tasks/**` only |
| 3 | `code-review` | experimental | `both` | none — no repo path at all beyond `docs/artifacts` version names |
| 4 | `consolidate-memory` | **stable** | `both` | **hard write**: promotes into `AGENTS.md`, regenerated in target (§1.8) |
| 5 | `discover-skills` | **stable** | `both` | **hard read**: step 1 + `## Rails` name `implementation/registry/**` |
| 6 | `evaluate-poc` | experimental | `both` | none — `docs/decisions/` only |
| 7 | `handoff` | **stable** | `both` | **hard read**: step 3 names `implementation/runtime/handoff/` |
| 8 | `new-feature` | stable | `both` | none on audience; `04-protocols.md` dangling (§1.9) |
| 9 | `new-poc` | experimental | `both` | none on audience; `04-protocols.md` dangling |
| 10 | `new-project` | stable | `both` | none on audience; `04-protocols.md` dangling ×2 |
| 11 | `plan` | experimental | `both` | none — `docs/plans/`, `docs/tasks/` |
| 12 | `poc-demo` | experimental | `both` | none — `docs/{plans,checkpoints,decisions}/` |
| 13 | `prepare-release` | experimental | **`authoring`** | three uninstalled paths — **correct once declared** (§6.1) |
| 14 | `security-audit` | stable | `both` | none — names no repository path whatsoever |
| 15 | `skillify` | experimental | `both` | **wrong in both audiences**: `.github/skills/` ×2 (T532) |
| 16 | `sprint-status` | stable | `both` | none — `docs/tasks/**` |
| 17 | `team-status` | experimental | `both` | none — `docs/tasks/**` |
| 18 | `validate-tasks` | stable | `both` | **conditional**: portable only via `install_docs` (§2.4) |
| 19 | `validate-workflow` | experimental | `both` | judgment call (§2.5); `04-protocols.md` dangling |

Totals: **1 `authoring`, 18 `both`, 0 `target`.** Four commands carry a hard leak
(`consolidate-memory`, `discover-skills`, `handoff`, `skillify`), one a soft leak (`batch`), one a
conditional (`validate-tasks`). **Thirteen are genuinely clean.**

The brief's "the remaining fifteen are audience-neutral by accident, not design" is right about the
*mechanism* and off by two on the count: it is **thirteen** clean, because `consolidate-memory` is a
fourth defect (§1.8) and `batch` carries a soft leak. The brief's underlying claim — that they are
clean because they touch only `docs/**` or project source, which exist in both — is **confirmed for
all thirteen** by reading each one.

### 2.3 Three classes of leak, because they need three different repairs

- **Class A — unperformable.** The command instructs a read or write at a path that does not exist in
  the declared audience. The step cannot be carried out. `/discover-skills` step 1, `/handoff` step 3.
- **Class B — silently futile or destructive.** The path exists and the operation *succeeds*, but the
  result is not durable. `/consolidate-memory` step 5 (`AGENTS.md` regenerated), and — critically —
  **every candidate repair that writes into `.<platform>/skills/`** (§7). An existence precondition
  cannot detect class B. This is the class the brief's proposed two-row rule for `/skillify` lands in.
- **Class C — a source-tree cross-reference.** The command cites another *component* by its
  authoring-tree path rather than by name: `/batch`'s "`commands/plan.md` step 5",
  `/discover-skills`' bare "`skills/<name>/SKILL.md`" and "`registry/summary.md`". Not wrong so much
  as unresolvable: in a target project the same document lives at `.claude/commands/plan.md`,
  `.github/prompts/plan.prompt.md`, `.pi/prompts/plan.md` and so on. **The repair for class C is to
  cite by component name (`/plan`, the `<name>` skill) and not by path at all** — which is
  audience-free, needs no conditional, and is what `AGENTS.md`'s own Skill Workflow table already
  does (it names skills as `` `systematic-debugging` ``, not as file paths).

### 2.4 `/validate-tasks` — portable, with one unevidenced link in the chain

`/validate-tasks` says *"Run `python3 docs/tasks/validate-tasks.py` from the project root."*
`implementation/docs/tasks/validate-tasks.py` **exists** (I read its first 15 lines), and
`install_docs`'s fresh-install branch `copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs"` copies
it. So the brief's account is right.

**The unevidenced link:** on `--update`, `install_docs` special-cases the `tasks` subdirectory —
`if [[ "$name" == "tasks" ]]; then merge_task_docs` (line 385-386) — which invokes
`scripts/merge-task-docs.py --template-dir … --dest-dir …` rather than `rsync --ignore-existing`.
**I did not read `merge-task-docs.py`.** Whether it carries non-`.md` files such as
`validate-tasks.py` is unknown to me. If it does not, a target project installed before the script
existed would never receive it on `--update`. Flagged, not asserted.

### 2.5 `/validate-workflow` — the one genuine judgment call

Its subject is "the AI development team configuration", and its step 4 enumerates *this
repository's own* commands for regression checks. A reading that makes it `authoring` is respectable.
I classify it **`both`** because a target project receives that same configuration — the same 19
commands, the same agents, the same handoff contract — and validating one's own installed
configuration is a legitimate target-project act. Recorded as contestable; nothing else in this
document turns on it, and `/validate-workflow` is `experimental` either way.

## 3. Q1 — Is a declared `audience:` field the right mechanism?

### 3.1 The answer, in two parts

**Yes — as a *declaration*, not as a *resolution*.**

1. Add `audience` to `implementation/knowledge/schemas/command.schema.json` with
   `"enum": ["authoring", "target", "both"]`, **`required`**, and **source-only** (added to no
   platform manifest's `keepKeys`, so it appears in no projection).
2. The declaration alone fixes nothing. It makes one question *askable, auditable and mechanically
   enforceable*: **"does this command's body name a path that its declared audience does not have?"**
   For the four commands where the honest answer is "yes and it genuinely diverges", the **body**
   carries the resolution (§4). `audience:` says which question to ask; the body answers it.

Three grounds, each from a file read by name:

- **`maturity:` is an exact, working precedent for a source-only, gate-consumed, projection-invisible
  command frontmatter key.** It is required by the schema; it is in **none** of the six
  `frontmatter.commands.keepKeys` lists; `applyGenericFrontmatter` therefore drops it from all 114
  projections (confirmed by reading `.claude/commands/discover-skills.md`, which has no `maturity:`);
  and it is consumed by `generate-registry.py::_maturity` and by `check-maturity.py`. `audience:`
  can be installed on those rails for **one schema edit and zero manifest edits** (§5.3).
- **It is enforceable for free.** Making it `required` in the schema means
  `tests/functional/test_schemas.py::test_command_frontmatter` and `check-maturity.py`'s criterion 1
  (`_check_schema`) both enforce its presence and its enum with **zero new gate code**. No other
  candidate mechanism gets enforcement without writing a new checker.
- **It converts 19 accidents into 19 decisions, which is the actual finding.** The finding is not
  "three commands have bad paths"; it is that audience-neutrality is undesigned. A required
  one-line declaration per command is the cheapest possible instrument that makes the undesigned
  state impossible to re-enter, because a new command cannot be added without answering the question.

**Why `required` rather than optional-with-default-`both`.** An optional key with a default preserves
precisely the defect: silence continues to read as `both`, and nothing can distinguish "considered
and judged `both`" from "never considered". The cost of `required` is that all 19 files must be
edited in **one atomic commit** together with the schema, or the functional suite goes red — which is
a scheduling constraint, not an expense (§5.3 costs it at 20 files in one commit). The value is that
the declaration is an *act*. I recommend `required`.

**Why `target` stays in the enum although no command is `target`-only today.** Without it, `both`
degenerates to "not `authoring`" and the vocabulary stops describing the axis. A future
target-project-only command (a scaffolding or deployment command, say) is entirely plausible.

### 3.2 Rejected alternatives

#### (a) A `## Rails` prose clause only — **rejected as the primary mechanism, retained as a complement**

The natural form is a fourth `## Rails` label, e.g. `**Audience**: both — …`.

**Grounds for rejection.** `check-maturity.py:284` defines `RAILS_LABELS = ("Inputs", "Out of
scope", "Failure mode")` as a closed tuple, and `_rails_check` is wired into **`BETA_CRITERIA`**
(line 569), which is shared by **all four categories** — agents, commands, instructions and skills
alike. Adding a fourth label to that tuple would fail criterion 2 for every non-`experimental`
component in the repository that lacks it: per `implementation/registry/summary.md`'s counts, the
population is 28 agents + 19 commands + 6 instructions + 26 skills = 79 components (the summary's
category counts; how many are non-`experimental` I did not tally). To avoid that, one would have to
make `_rails_check` category-conditional — i.e. **change a shared gate to serve one category**,
which is structurally the move `ADR-007` branch 1 exists to forbid one level down ("a command may
not create a rival convention for the same thing"), applied to a checker.

Two further grounds: `## Rails` is *body* prose, so it projects to all six platforms and ships to
every target project — the audience declaration would become reading material for end users rather
than metadata about two trees. And it is free text: nothing can check a `**Audience**:` clause
against the paths the body actually names, whereas an enum-constrained frontmatter key is checkable
today and is a viable input to a future path-installability gate.

**What is not rejected:** a `## Rails` **Out of scope** clause is the right place to record a
*resolution* once the frontmatter declares the *audience* — e.g. `/prepare-release`'s "Out of scope"
gaining "releasing a downstream project's own product; this command releases this knowledge base."
That is a complement, not the mechanism.

#### (b) Per-step annotation — **rejected**

Marking individual steps `[authoring]` / `[target]`.

**Grounds.** It is the finest granularity and the least enforceable. It puts audience markers into
every line an end user reads; it has no home in any existing gate; and it *labels* a divergence
rather than resolving it — an annotated `[both]` step whose path diverges is no better off than an
unannotated one. The surface is large (19 commands with roughly ten numbered steps each; **I did not
tally steps and assert no count**).

Decisively, **the real distribution does not need it.** Of 19 commands, exactly **one** is
per-step-divergent in a way a file-level declaration cannot express: `/prepare-release`, whose steps
1–5 are portable and steps 6–7 are not. And for that one, §6.1 shows the honest answer is to declare
the *whole command* `authoring`, because what it describes end to end is a release of *this
repository's knowledge base* — its step 6 mandates a checkpoint "Maturity distribution" table
regenerated from `implementation/registry/summary.md`, which is a distribution over emage.code's own
components. One case, whose correct treatment is file-level anyway, does not justify a per-step
vocabulary.

#### (c) Splitting divergent commands into two files — **rejected**

`/skillify-authoring` + `/skillify-target`, and so on.

**Grounds, three.**

1. **It mints a second identity namespace for one component** — `batch-manifest-resolution-v1.md`
   §1.3 and §3.2's ground, one level up. `generate-registry.py:83` derives `id` from the file stem
   (`path.stem`). Two files are therefore **two registry entries**, two `maturity:` claims, two
   `check-maturity.py` component rows, two sets of criterion-4 and criterion-6 obligations (a golden
   case each and a `docs/wiki/**` sentence each, per `COMMAND_STABLE_CRITERIA`), and twelve
   projections instead of six.
2. **It makes the user answer a question the command can answer itself.** Which audience the
   repository is, is a fact determinable by testing one directory's existence (§6). Putting it in the
   slash-command name delegates a mechanical test to a human at the prompt.
3. **It doubles the golden-case obligation for exactly the commands that are hardest to fixture** —
   `active-tasks.md`'s T525/T528 notes record that wave 1 and wave 2 each produced one red case out
   of four/five, and that the PoC commands have no corpus at all. Doubling that population is the
   opposite of what the promotion ladder needs.

#### (d) Doing nothing; fixing paths case by case as T532 does — **rejected as a *class* answer, accepted as the answer for the thirteen clean commands**

This deserves care, because it is what is actually happening and it is not absurd.

**Grounds for rejection.**

1. **It has already escalated to the class once, by itself.** `docs/tasks/task-T532.md` §3 — the
   case-by-case task — is where the class question comes from, in its own words (quoted in §1.1).
   The case-by-case route's own output was "this is a larger finding".
2. **It has no termination condition.** Nothing in this repository can *enumerate* the remaining
   instances. There is no gate that reads a command body and asks whether its paths exist in the
   declared audience; `check-maturity.py`'s seven command criteria are schema validity, `## Rails`
   labels, defect scans, a golden case, `agent:` resolution and a wiki sentence — none of them looks
   at paths. So "fix them as they surface" means "fix the ones a golden case happens to point at".
3. **The existing checks provably cannot surface them.** `/discover-skills` and `/handoff` are both
   `stable`, which means criterion 4 (a golden case with `command: /<id>`) is satisfied for both
   — *inferred* from their `stable` status plus the mechanical enforcement of
   `_command_golden_evidence`; **I did not run the gate and did not read the suite.** Their cases did
   not surface this defect, and structurally could not: a golden case runs against a fixture inside
   `tests/golden/`, i.e. inside the authoring repo. **No golden case can exercise the target-project
   audience at all**, because the suite has no installed-target fixture. The audience axis is
   invisible to criterion 4 by construction. (This is also §8's third argument.)
4. **I found a fourth instance (§1.8) by hand-reading 19 files in one session.** A route that depends
   on someone doing that again, unprompted, is not a route.

**What survives:** for the thirteen clean commands the correct action genuinely *is* nothing — no
conditional, no precondition, one word of frontmatter. The declaration's value for them is that it is
cheap and checkable, not that it changes their text.

#### (e) Install-time path rewriting — **rejected, and the brief did not name it, but it already exists in this repository**

`scripts/render_installed_agents.py` is precisely this mechanism, in production, for `AGENTS.md`: a
`PLATFORM_MAP` of 7 platforms × 4 path fields (`skills`, `standards`, `security`, `mcp`), and six
`_replace_one` regex substitutions applied at install time so the shipped `AGENTS.md` names the
installed platform's real paths. Extending it to the 19 commands is the most *automatic* candidate
answer and must be named before it is dismissed.

**Grounds for rejection.**

1. **It fails closed on prose drift, loudly and globally.** `_replace_one` (lines 57-61) raises
   `ValueError` if its pattern matches zero times. Six hand-written regexes against one file already
   means **every `install.sh` run for every platform aborts** if that file's wording drifts. Applying
   the same scheme to 19 command files with several paths each makes the installer a hostage to
   command prose.
2. **It rewrites only the installed copy.** The authoring repo's own `.claude/commands/*.md` — which
   the running orchestrator actually reads — is never rewritten. Worse, `active-tasks.md`'s T543 row
   records that the repo-root projections are refreshed by **no generator** and checked by **no
   gate** (`sync.mjs:47-49` resolves `ROOT` to `implementation/` absent `--root`, so it writes
   `implementation/.claude/`, never the repo-root tree). So the authoring audience would get *no*
   rewriting at all.
3. **It resolves the wrong axis.** `render_installed_agents.py` resolves *platform*, and it can,
   because `install.sh` passes it `--platform`. Nothing tells `sync.mjs` an *audience*: both
   audiences consume the same projection bytes, generated once.

**Retained as evidence, not as a mechanism.** Its existence proves the repository already accepts
that some shipped prose must name audience-dependent paths, and its fragility is a positive argument
for putting the conditional in the **command's own body**, where an agent evaluates it at run time
against the tree in front of it, rather than in a build step that must guess.

**A bonus diagnosis for T545, since this is the file that explains its two known defects.** The
brief warns that `AGENTS.md` § Knowledge Base bullet 2 omits `.claude/` while bullet 3 includes it,
and that bullet 2 names the wrong `sync.mjs` path. Reading `render_installed_agents.py` explains
exactly why: **bullet 3 is generated** — it is `readme_ref`, built for `--platform all` by iterating
`PLATFORM_MAP` (lines 87-97), which is why it lists all eight roots including `.claude/`. **Bullet 2
is not** — no `_replace_one` pattern matches it, so it is hand-written source text in
`implementation/AGENTS.md` and its `.claude/` omission and wrong script path are source defects.
T545 should fix bullet 2 in `implementation/AGENTS.md` and must **not** hand-edit bullet 3. I did not
touch `AGENTS.md`.

#### (f) Making the installer install whatever the commands name — **deferred to Q4, not rejected wholesale**

"If `/discover-skills` needs the registry, install the registry." This is a **per-command repair**,
not a mechanism for the class, so it is judged per command in §6. Preview: **rejected** for the
registry, **recommended** for the handoff runtime, on a stated rule.

## 4. Q2 — What does `both` oblige a command to do?

### 4.1 The answer

**`both` obliges nothing extra where nothing diverges** — which is thirteen of eighteen. A blanket
"every `both` command carries a precondition" would add thirteen pointless conditionals and is
rejected on the same grounds as per-step annotation: cost without discrimination.

Where something *does* diverge, `both` imposes a three-part obligation:

- **B1 — Every path the body names must exist in both audiences, or the body must resolve it.** A
  path under `docs/**` or under project source satisfies this with no conditional. This is the
  default and the cheap case.
- **B2 — Where a path genuinely diverges, the body carries a *discriminator* and one branch per
  audience.** The discriminator must be (i) evaluable by the agent with the tools it has,
  (ii) a fact about the *repository*, never a question to the user, and (iii) **false in the audience
  it excludes**.
- **B3 — Each branch's target must be *durable* in its own audience.** A branch that writes
  somewhere the next `install.sh --update` deletes has not resolved the divergence; it has hidden it.

### 4.2 Is the precondition-on-directory-existence the general pattern, or specific to `/skillify`?

**The *form* is general. The *test* is not, and B3 is where the proposed `/skillify` rule fails.**

**The form generalises.** A run-time conditional evaluated by the agent against the tree in front of
it is the right shape, because it is the only shape that is correct in both audiences from a single
set of projected bytes (§3.2(e) shows why build-time rewriting is not).

**The specific test does not generalise, on two counts.**

First, **there is no single discriminator.** Three different ones are needed across the four
defective commands, because three different trees are missing:

| Command | What is absent in a target project | Sound discriminator |
|---|---|---|
| `/skillify` | the source knowledge tree | `implementation/knowledge/skills/` exists |
| `/discover-skills` | the generated registry, a **sibling** of `knowledge/`, not part of it | `implementation/registry/index.json` exists |
| `/handoff` | the handoff runtime | `implementation/runtime/handoff/schema-v1.json` exists |
| `/consolidate-memory` | **nothing is absent** | *no existence test works* — see below |

And a trap worth stating explicitly, because it is the obvious shortcut and it is **wrong**: a
discriminator of the form *"does `implementation/` exist"* **fails condition (iii)**.
`install_mcp_server_runtime` (install.sh:423-431) creates `$TARGET/implementation/`,
`$TARGET/implementation/__init__.py` and `$TARGET/implementation/runtime/` on **every** install. The
discriminator must name `implementation/knowledge/` or `implementation/registry/` specifically. The
brief's rendering of the `/skillify` rule ("write `implementation/knowledge/skills/` if it exists")
gets this right; anyone shortening it to `implementation/` would silently invert the test in every
installed project.

Second, and more importantly, **existence is only a proxy for the thing that actually matters, and it
breaks on `/consolidate-memory`.** `AGENTS.md` exists in both audiences. It is writable in both. A
promotion written to `$TARGET/AGENTS.md` **succeeds** — and is destroyed by the next `--update`
(§1.8). No existence test detects that, because nothing is absent. What differs is **authority**: in
the authoring repo the writable source is `implementation/AGENTS.md`; in a target, `AGENTS.md` is
generated output.

So the general obligation is **B2 stated in terms of authority and durability, not presence**:

> A `both` command whose target diverges must name, per audience, the **durable authoritative home**
> for what it produces or reads. An existence precondition is the cheapest correct implementation of
> that *where source-tree presence and authority coincide* — which is three of the four cases, and
> not the fourth.

### 4.3 A fourth obligation that falls out of the survey

**B4 — a `both` command must not name another component by its authoring-tree path.** This is class C
(§2.3): `/batch`'s "`commands/plan.md` step 5", `/discover-skills`' bare "`skills/<name>/SKILL.md`"
and "`registry/summary.md`". The repair needs no conditional at all: **cite by component name, not by
path** — `/plan`, the `<name>` skill — which is audience-free and is what `AGENTS.md`'s own Skill
Workflow table already does (it names `` `systematic-debugging` ``, never a file path). B4 is
cheaper than B2 and covers more instances, so it should be applied first.

The same reasoning covers §1.9's second item: a `both` command referring to an `authoring` command by
name (`/validate-tasks` → `/prepare-release`) is *harmless* — an instruction naming an absent command
does nothing — so B4 needs no cross-audience-routing clause. It is recorded so a future reader does
not mistake the silence for an oversight.

## 5. Q3 — Blast radius, costed against files read by name

### 5.1 The costing

Every row names a file I opened. "0 edits" is a claim about *that file*, derived from its contents,
not a claim about the repository.

| File (read by name) | Edits | Why, from the file |
|---|---|---|
| `implementation/knowledge/schemas/command.schema.json` | **1 — mandatory, and must be in the same commit as the first `audience:` key** | `"additionalProperties": false` (line 12). Add `audience` to `properties` with the three-value enum, and to `required`. |
| `tests/functional/test_schemas.py` | **0** | `_load_schema("command")` + `jsonschema.validate` (lines 20-21, 59-64). It needs no change once the schema allows and requires the key — it enforces both for free. |
| `implementation/scripts/check-maturity.py` | **0** | `_check_schema` (line 367-374) loads `schemas_dir / f"{category}.schema.json"` generically. Criterion 1 enforces the enum for every non-`experimental` command with no new code. |
| `implementation/platforms/claude-code.json` | **0 recommended** | `frontmatter.commands.keepKeys = ["description","argument-hint"]`. `maturity` is already absent, so a source-only key needs no entry. |
| `implementation/platforms/{cursor,gemini,github,opencode}.json` | **0 recommended** | each `["description","agent","argument-hint"]`. Same. |
| `implementation/platforms/pi.json` | **0 recommended** | `["description","argument-hint"]`. Same. |
| `implementation/platforms/cline.json` | **0 — and it has no commands** | no `fileMap.commands`, no `frontmatter.commands`. §1.4. |
| `implementation/scripts/sync.mjs` | **0** | `applyGenericFrontmatter` (288-301) is key-agnostic; it copies `keepKeys` and drops the rest. |
| `implementation/scripts/generate-registry.py` | **0 recommended** (1–3 if `audience` went into the registry) | `_entry_from_file` (79-96) builds a fixed dict with no passthrough: 1 edit there, plus 2 in `_summary_markdown` (header line 147, row 151-153) if it should appear in the table. §5.2 says no. |
| `implementation/registry/index.json` and `summary.md` | **regenerated — not optional, and independent of §5.2** | `_checksum` is `sha256` of the **whole file text including frontmatter** (`_parse_frontmatter` returns `text`, line 52; `_checksum(text)` line 90). Adding `audience:` to any command changes that command's `checksum`, and `--check` (211-223) reports drift until regenerated. **All 19 entries' checksums change.** |
| The 19 files in `implementation/knowledge/commands/` | **19 frontmatter one-liners, of which 6 also need a body edit** | frontmatter: all 19, because `required`. Bodies: `skillify`, `discover-skills`, `handoff`, `prepare-release`, `consolidate-memory` (the four hard leaks plus the reclassification), and `batch` (class C). |
| 114 generated command projections (19 × 6) | **0 hand-edits; `sync.mjs` regenerates** | and — the decisive number — **only 36 change**, not 114, because `audience:` is dropped from frontmatter and only the **6** commands whose *body* changes produce new bytes. Had `audience` gone into `keepKeys`, **all 114** would change. |
| Repo-root `.claude/`, `.github/`, … command projections | **unevidenced; T543's problem** | `sync.mjs:47-49` writes `implementation/.<platform>/`. `active-tasks.md`'s T543 row records the root tree is refreshed by no generator and gated by nothing. I read `.claude/commands/discover-skills.md`; it is consistent with a claude-code projection (no `agent:`, no `maturity:`). Whether the root tree is otherwise in sync: **I did not check and cannot.** |
| `docs/wiki/**` | **unevidenced** | criterion 6 requires a wiki sentence per command. Whether any page needs an audience column is a `technical-writer` question; **I read no file under `docs/wiki/`.** |
| `AGENTS.md` | **0 by this task; 1 new subsection recommended for T545** | see §5.4. |
| `scripts/install.sh` | **0 or 2**, per §6.3 and §7 | one line for `/handoff`'s runtime, one exclude list for `skills/local/`. Both are `devops-engineer`'s file. |
| `tests/golden/**` | **cannot assess** | not read, not authorized. §10. |

### 5.2 Does `audience` belong in the registry? **No.**

Four grounds, each from a file.

1. **The entry shape is deliberately minimal and already omits something more useful.** Read from
   `implementation/registry/index.json` and confirmed against `_entry_from_file`, an entry carries
   `id`, `category`, `name`, `path`, `checksum`, `maturity`, `compatibility` — and **no
   `description`**, which is the single most obviously useful human-facing field a command has. A
   field that loses to `description` on utility does not clear that bar.
2. **Nothing would consume it.** `check-maturity.py` reads component **frontmatter directly** —
   `_build_component` (900-911) → `_read_frontmatter_and_body` — for every criterion except
   `maturity` itself, and uses the registry entry only for `id`/`category`/`path`/`maturity`. The
   decisive precedent is `_collect_command_ownership` (801-814): it needs each command's `agent:`
   key, and it reads it **out of the source file**, not out of the registry. **A command frontmatter
   key that a gate needs is read from the file.** Any future audience gate would do the same.
3. **Why `maturity` *is* there, and `audience` is not analogous.** `maturity` is in the registry
   because `check-maturity.py` consumes `entry["maturity"]` as *the claim under test*, and because
   `_summary_markdown` publishes the per-category distribution that `/prepare-release` step 6
   requires for a release checkpoint's "Maturity distribution" section (read from
   `prepare-release.md:28-32`). `audience` has no such consumer and appears in no report.
4. **It would cost a `schemaVersion` argument nobody needs.** `SEMVER = "3.0.0"` (line 24). Adding a
   field to every entry invites a bump debate that buys nothing.

### 5.3 The headline number

**One mandatory edit outside the commands themselves.** Concretely:

- **One atomic commit:** `command.schema.json` + all 19 command frontmatters = **20 files**. This
  atomicity is forced, not chosen: `test_schemas.py::test_command_frontmatter` validates all 19
  unconditionally, so a partial commit is red.
- **Then, separately per §6:** 6 command **body** edits, each of which can be its own task with its
  own `**Affects:**` row.
- **Regenerated, by running two commands I cannot run:** `implementation/registry/{index.json,
  summary.md}` via `generate-registry.py`, and 36 of 114 command projections via `sync.mjs`.
  `active-tasks.md`'s T522 note records that these are two separate obligations and that
  `sync.mjs --check` gives **no** signal on registry drift.
- **Zero:** manifest edits, generator edits, `sync.mjs` edits, test edits, new gate code.

For comparison, the alternative that looked cheapest — adding a `## Rails` label — costs a change to
a **shared four-category gate** and puts up to 79 components at risk of criterion 2 (§3.2(a)). The
mechanism recommended here is the smallest of the five by a wide margin, and that is its strongest
recommendation.

### 5.4 One `AGENTS.md` subsection, for T545 not for me

`AGENTS.md` is the document `ADR-007` branch 1 measures commands against, so the audience
distinction has to be stated *somewhere* higher than a command file or the per-command verdicts in §6
rest on nothing. The natural home is a short subsection under § Knowledge Base naming the two
audiences, the fact that `implementation/knowledge/`, `implementation/registry/`,
`implementation/runtime/handoff/`, `implementation/platforms/`, `implementation/scripts/` and
top-level `scripts/` are **never installed**, and the `audience:` key.

**T545 owns that file and I did not touch it.** Until such a subsection exists, §6's verdicts rest on
`install.sh`'s behaviour as read — which is a weaker authority than `AGENTS.md` but is not no
authority: it is executable, and `ADR-007` §2.1's own corroboration pattern ("the named file's own
validator rejects it") treats executable behaviour as evidence.

## 6. Q4 — The three commands: repair or reclassify?

The three answers differ, and the rule that makes the difference principled rather than ad hoc is
stated first so it can be checked against each case:

> **Install the artifact when it is self-contained and the target genuinely needs it. Repath the
> command when the artifact is an index of files the target does not have. Reclassify when the
> command is about this repository.**

### 6.1 `/prepare-release` → **reclassify `authoring`**

It is not a portable command that happens to name two uninstalled scripts. It is *about this
repository's own release process from end to end*, and its own text says so three times:

- step 6 regenerates `implementation/registry/summary.md` via `implementation/scripts/
  generate-registry.py --root implementation`;
- step 6 requires a checkpoint `## Maturity distribution` table whose contents are a distribution
  over **emage.code's own components** — a thing no target project has;
- step 7 names `scripts/verify-release-docs.py --tag v<version>` and `docs/releases/_template.md`.

`implementation/scripts/` and top-level `scripts/` appear in no `install_*` function (§2.1). A target
project releasing *its own product* needs a genuinely different command, not this one with paths
patched.

**Declaring it `authoring` makes the uninstalled paths correct rather than defective**, which is the
whole point of the mechanism: the leak was never the path, it was the undeclared audience. Zero
maturity consequence — it is `experimental`, so `check-maturity.py:783` returns before criteria 3
and 7 either way.

Cost: one frontmatter word, plus one recommended `## Rails` **Out of scope** clause so a reader who
reaches the body without the frontmatter is not misled. Optionally a one-clause note on
`/validate-tasks` step 2 (§1.9 item 2); I would leave it, since naming an absent command is inert.

### 6.2 `/discover-skills` → **repair the command, and reject the installer change**

The installer option is real and cheap: one `install_tree_into "$IMPLEMENTATION/registry"
"$TARGET/implementation/registry"` line, on machinery that already exists.

**Reject it, on three grounds from the file itself.**

1. **An installed registry would be an index of files that are not there.** Every entry's `path` is
   relative to `implementation/knowledge` — `sourceRoot: "implementation/knowledge"` in
   `index.json`, and `rel_path = path.relative_to(source_root)` at `generate-registry.py:81`. A
   target project has **no** `implementation/knowledge/`. So `$TARGET` would receive a manifest of 79
   components, **none** of which exists at its stated path. That is worse than absent: a command told
   to "load the registry" would then follow 79 dead paths.
2. **`checksum` would be meaningless there**, being a hash of source files the target does not hold.
3. **Nothing would keep it true.** It would need regenerating per target, and no installed script
   does that.

**The repair.** Step 1's *purpose* is to enumerate the available skills. The thing that exists in
**both** audiences and actually enumerates them is the **skills tree itself**:
`implementation/knowledge/skills/*/SKILL.md` in the authoring repo, and `.<platform>/skills/*/SKILL.md`
in a target — every one of the seven manifests declares `fileMap.skills` as `{"dir": "skills",
"preserveTree": true}` under its `outputDir`, and `render_installed_agents.py`'s `PLATFORM_MAP`
already names that directory per platform, which is why the rendered `AGENTS.md` tells agents to
"check applicable skills in the active platform projection".

So step 1 becomes a B2 two-row rule on the discriminator `implementation/registry/index.json` exists,
with the registry retained as an **optional accelerator** where present rather than as a
precondition. Three further gains in the same edit, at no extra cost:

- it cures the class-C bare references `skills/<name>/SKILL.md` and `registry/summary.md` (B4);
- it fixes `## Rails` **Inputs** too, which names the registry a second time (§1.7);
- `packs/installed/` in step 6 should be examined in the same pass. **I could not find or verify it
  and assert nothing about it** — it appears in no file I read other than `discover-skills.md` itself,
  and I cannot grep.

**The cost that must be stated, not estimated.** `/discover-skills` is `stable`, so criterion 4 means
a golden case for it exists (inferred from `_command_golden_evidence` being mechanically enforced;
**I did not run the gate**). Amending step 1 may put that case's checker out of date exactly as T527
did to `/skillify`'s and T535 did to `/batch`'s — and **I may not read `tests/golden/` to find out.**
§10 carries it as a blocker.

### 6.3 `/handoff` → **repair the installer, and change the command not at all**

This is the case where the installer change is the *better* half, and the asymmetry with §6.2 is
principled:

1. **The artifact is a schema, not an index.** `implementation/runtime/handoff/schema-v1.json` is
   self-contained — a JSON Schema contains no paths into `implementation/knowledge/`. Installing it
   is meaningful in a way installing the registry is not. (**Unevidenced:** I did not read that file
   or anything else under `implementation/runtime/handoff/`. The self-containment claim is an
   inference from what a JSON Schema is, not a reading of this one.)
2. **The precedent and the machinery already exist, for the identical reason.**
   `install_mcp_server_runtime` (install.sh:423-431) already creates `$TARGET/implementation/`,
   `$TARGET/implementation/__init__.py` and `$TARGET/implementation/runtime/`, and copies
   `runtime/memory` and `runtime/security` in, on the stated ground that "Config generation alone
   is not enough… outside the emage.code source repo itself, no such module exists to run until this
   step copies it there" (comment at 412-422). `runtime/handoff/` is the same class: a portable
   command's output is expected to be validated in the target.
3. **A shipped instruction already promises it is there.** This repository's own security guidelines
   state that "Handoff JSON (`docs/checkpoints/handoff-*.json`) must pass
   `runtime/handoff/validator.py`" — and that instruction is projected to every platform and shipped
   to every target project. Installing the tree makes an existing promise true.
4. **Install the whole tree, not just the schema.** `active-tasks.md`'s T529/T536/T537 note records
   that **`validator.py` never loads `schema-v1.json`** — it re-implements the rules. So shipping the
   schema alone would ship a file nothing reads, while the validator the security instruction names
   stayed absent. **I am quoting that ledger note, not verifying it** — I read neither file.

**The result is the cheapest possible resolution of a `both` divergence: the path becomes true in both
audiences and stays byte-identical, so the command needs no conditional and no edit at all.** One
line: `install_tree_into "$IMPLEMENTATION/runtime/handoff" "$TARGET/implementation/runtime/handoff"
"__pycache__"`, added to `install_mcp_server_runtime` beside its two siblings.

That is `scripts/install.sh`, i.e. **`devops-engineer`'s file, not mine and not a command edit.** It
should be its own task, and it should be the *same* task as §7's `skills/local/` exclude, since both
touch the same function region and both would otherwise contend for the same file.

### 6.4 And the fourth: `/consolidate-memory` → **repair the command; no installer change helps**

Out of the brief's scope but it is `stable` and destructive (§1.8), so it needs a verdict.

No installer change can fix it: `AGENTS.md` is *supposed* to be regenerated, and protecting it would
mean never shipping an updated one. The repair is in the command, and it is a B2 two-row rule on
**authority rather than existence**:

- authoring audience → promote into `implementation/AGENTS.md` (the source), never the root copy;
- target audience → promote into a durable project-owned document under `docs/**`, which
  `install_docs` never deletes and never overwrites where the harness ships no counterpart (§1.6) —
  **not** `AGENTS.md`;
- and in both, **do not delete the memory entry until the write target is confirmed durable**, which
  is the clause that turns a destructive defect into a survivable one.

`/consolidate-memory` is `stable`, so the criterion-4 caveat of §6.2 applies to it identically and
for the same unreadable reason.

## 7. Q5 — The durable home, which T532 deferred and I have the mandate to settle

### 7.1 The facts, all read from files

- Installed skills live at `.<platform>/skills/`: every one of the seven manifests declares
  `fileMap.skills` with `"dir": "skills"`, six of them with `"preserveTree": true`.
- **A hand-written skill anywhere under `.<platform>/skills/` is deleted by the next
  `install.sh --update`.** `install_tree_into` → `sync_tree_into` → `rsync -a --delete` with
  per-platform `--exclude`s. `skills` is in **neither** of the two lists I read in full:
  `GITHUB_LOCAL_PATHS` (262-272: `workflows ISSUE_TEMPLATE PULL_REQUEST_TEMPLATE.md
  PULL_REQUEST_TEMPLATE CODEOWNERS dependabot.yml dependabot.yaml FUNDING.yml
  copilot-instructions.md`) and `CLAUDE_LOCAL_PATHS` (255: `settings.json settings.local.json`). The
  other five `install_*` functions pass only their MCP config file and its provenance sidecar.
  `install.sh:324` announces it: *"warning: --update replaces $TARGET/$d entirely (rsync --delete)…
  Other local edits there will be lost."*
- **`docs/**` is durable**, under both modes, for a file with no upstream counterpart: neither branch
  of `install_docs` passes `--delete`, and the `--update` branch passes `--ignore-existing`
  (§1.6 corrects §2.1's over-general claim in the direction that helps here).
- **But no skill loader reads `docs/**`.** Every platform reads its own `skills/` dir — which is why
  `render_installed_agents.py`'s `PLATFORM_MAP` exists and why the rendered `AGENTS.md` Skill
  Workflow row names the platform projection. **I did not verify any vendor client's actual discovery
  rule; that is vendor behaviour and is unevidenced.**

### 7.2 Option A — mint `docs/skills/`. **Rejected, and I decline the mandate.**

Durable but unread. A skill no loader loads is a document, and `docs/**` already holds documents.

The stronger ground is `batch-manifest-resolution-v1.md` §3.2's, applied one level up: it **mints a
third tree to avoid protecting the second**. And it does not even avoid the installer/manifest work —
to be *useful* it would need a new loader rule in every platform, i.e. it **adds** a manifest change
rather than replacing one. T532 declined to mint it for lack of mandate; I have the mandate and
decline it on the merits, which is the stronger refusal.

### 7.3 Option B — a blanket `install.sh` exclude for `skills/`. **Rejected as stated.**

`rsync --exclude=skills` protects the directory from `--delete` **and** from overwrite (the
`rsync_args` loop at 172-176 adds `--exclude`; the no-rsync fallback at 191-213 backs the whole path
up and restores it verbatim). So excluding `skills/` would stop `--update` from ever **delivering**
the 26 canonical skills again — the tree's entire purpose.

The existing carve-outs work because the harness ships **nothing** at those paths
(`sync_tree_into`'s own comment, 156-161: *"Project-local state the harness never ships, so it has no
counterpart in `$IMPLEMENTATION`"*). `skills/` is the opposite case, so the same instrument cannot be
pointed at it whole.

### 7.4 Option C — a **sub-path** carve-out, `.<platform>/skills/local/`. **RECOMMENDED.**

- **It is the existing instrument, pointed at a path that genuinely has no upstream counterpart.**
  `install_tree_into`'s exclude list is already variadic (`"${@:3}"`) and already receives
  *directory*-valued paths — `_index` at line 429 and `workflows` at 445 — and lines 188-190 document
  exactly that (`-r` "so an excluded path may name either a file… or a directory"). Cost: one new
  constant plus one argument added to seven `install_*` calls.
- **It is read by the loader that already exists**, being inside the tree each platform already
  scans. (Subject to §7.1's unevidenced recursion caveat: whether each vendor client walks
  `skills/*/SKILL.md` recursively past one level is **not verified by me**. If some client does not,
  that client's local skills are undiscoverable and the option degrades to Option D *for that
  client only*. This is the single most important thing for the implementing task to check first,
  and it is checkable.)
- **It reuses the mechanism `T518` built for this exact failure** — the ledger records that the
  unexcluded sweep "destroyed `.claude/settings.json` on every `--update`" and deleted target
  projects' entire `.github/workflows/`. This is the same defect, one directory over.
- It keeps canonical and local skills visibly separated, which `docs/skills/` would also do, but
  without the fatal property of being unread.

**Costs, stated rather than glossed:**

1. **Seven paths, not one** — and `sync.mjs` must never emit `skills/local/`, or the exclude would
   shadow real canonical content. It cannot today: `syncPlatform` walks `KNOWLEDGE/skills` (line 530)
   and mirrors the relative tree, so a canonical `local/` dir would have to exist under
   `implementation/knowledge/skills/`. **Whether one does is unevidenced — I could not list that
   directory.** Cheap to check; must be checked.
2. **The `validate_before_update` warning text (install.sh:312-326) must gain the new exception per
   platform**, or the warning becomes a lie. This is `T518`'s own pattern — every carve-out it added
   came with a `case` arm.
3. **It is an `install.sh` change**, i.e. `devops-engineer`'s, and it is the *second* one alongside
   §6.3's. **They should be one task**, since they touch the same file and adjacent regions.
4. **It does not by itself complete `/skillify`.** A skill written to one platform's `skills/local/`
   is invisible to the other six installed platforms. So the target branch of `/skillify`'s two-row
   rule should be *"write to `<platform>/skills/local/<name>/SKILL.md` for **every** installed
   platform folder"* — which is durable **and** complete. This is why the brief's two-row rule as
   stated is **half a fix**: "write every installed platform folder" is the right *shape* and,
   without Option C, writes six or seven copies that the next `--update` deletes. Class B, §2.3.

### 7.5 Option D — declare that a target project has no durable hand-written-skill home

Recorded as the honest minimum if C is judged too expensive: `/skillify` in a target writes the skill
to `docs/` as a *document*, says plainly that no loader will pick it up, and stops. It is worse
guidance, but it is not **false** guidance — which is what the two-row rule without Option C would
be, and false guidance about durability is the worse failure. If C is deferred, D should ship in the
meantime rather than the unqualified two-row rule.

### 7.6 Verdict

**Option C, with Option D as the interim if C's recursion caveat (§7.4 cost 1's sibling) fails or if
the installer task slips.** A carve-out is cheaper than a namespace, reuses an instrument this
repository already built for the identical failure, and is the only option that is both durable and
loaded. `docs/skills/` is refused on the merits.

## 8. Q4 of the brief's §4 — the priority recommendation

**Recommendation: keep T546 at `P2`** — for a better reason than the one given, and with one
condition. **I am not editing the row; the decision is the user's.** (And note §1.1: **there is no
T546 row on this branch at all**, so the question is presently prospective.)

First, the mechanism as corrected (§1.2, §1.3): at `P1`, **exactly two components go red** —
`command/discover-skills` and `command/handoff`, on criterion 7. `/prepare-release` and
`orchestrator` are both `experimental` and exempt by the early return at line 783.

### 8.1 The case for P1, stated at its strongest

- **`/discover-skills` step 1 is unperformable, in a `stable` command that the shipped top-level
  convention document tells every target project to use.** `render_installed_agents.py` writes *"MUST
  check applicable skills in `<platform>/skills/` (or invoke `/discover-skills`)"* into **every**
  installed `AGENTS.md`. So the broken command is the one the installed conventions route to. This is
  a stronger P1 argument than the brief's framing, and it should be on the record.
- **`T536`'s precedent points this way.** `active-tasks.md`'s T536 note records that `stable`
  certifies *"passes the cases that exist"*, not *"has no known contract gaps"*, and names
  `/sprint-status` as "the first concrete instance where those differ". A **second** instance — this
  time where the gap makes a step *unperformable* rather than merely uncolourable — is the point at
  which "the cases that exist" starts to look like too low a bar to keep deferring.

### 8.2 The case for P2, which I find decisive

1. **At P1 the gate goes red before anything is fixed, and stays red until the row archives — that
   is a stall, not a signal.** `T514`, `T522` and `T523` all chose `P2` for exactly this reason, and
   the ledger says so: T514's note records that P2 "keeps this row out of criterion 7's open-defect
   scan — which at P0/P1 would block the very promotions the task exists to perform, the
   self-referential trap this repo has hit repeatedly", and T522's records that promotion inside a
   P1 task "was not merely undesirable, it was arithmetically impossible". A P1 T546 would block
   both commands for the duration of T546 **plus every follow-up that cites it** — on the queue this
   document generates, at least three more rows. The red would be *earned* and *uninformative*.
2. **T546 is an adjudication, not a repair.** Its deliverable is a document. Putting the priority on
   the *thinking* rather than on the *fixing* inverts what priority measures here — and it is the
   error `T535`/`T541` avoided by keeping the `/batch` adjudication `P2` and the `expect.py`
   re-derivation a separate, separately-prioritised task. The repairs in §6 and §7 are the things
   whose urgency is worth expressing, and each will be its own row with its own `**Affects:**`.
3. **No existing check could have caught this, by construction — so a red on it teaches nothing about
   the component.** This sharpens the orchestrator's reasoning rather than merely agreeing with it.
   Criterion 4 is a golden case, and a golden case runs against a fixture inside `tests/golden/`,
   i.e. inside the **authoring** repo. **The suite has no installed-target fixture**, so the
   target-project audience is invisible to criterion 4 *by construction*, not by oversight. The
   `stable` claims for `/discover-skills` and `/handoff` were therefore not merely "granted before
   the criterion existed" — they were granted under a gate that **structurally cannot reach this
   axis**. Turning that gate red on a criterion it cannot evaluate is a worse outcome than leaving it
   green with a tracked defect elsewhere.
4. **P1 buys less than §4 of the brief implies.** Two rows, not "two plus their owning agents"
   (§1.3).

### 8.3 The condition

P2 is right **only if the finding does not evaporate with the row.** At P2 `_ledger_defect` never
sees it, so nothing in the repository would record that two `stable` commands carry an unperformable
step. Two guards, either sufficient; I recommend the first:

1. **Put the priority on the repair, not on the adjudication.** At least the `/discover-skills`
   repair task should be **`P1` with `**Affects:** command/discover-skills`**, so the red appears at
   the moment a task exists that can clear it. That is precisely the `T520`→`T522` and
   `T523`→`T524` sequencing this repository has now run twice, and it is the only arrangement in
   which the red is informative.
2. Failing that, the defect belongs in the two commands' own `case.yaml` as a tracked defect — which
   **I cannot assess, specify or even confirm is possible, because I may not read `tests/golden/`.**

## 9. Summary of verdicts

| Q | Verdict |
|---|---|
| **Q1** | A **`required`, source-only** `audience: authoring \| target \| both` key in `implementation/knowledge/schemas/command.schema.json`. Rejected: `## Rails`-only (breaks a shared four-category gate), per-step annotation (finest granularity, least enforceable, one real case), file splitting (mints a second component identity), do-nothing (no termination condition; already escalated itself), install-time rewriting (fails closed on prose drift; wrong axis; skips the authoring tree). |
| **Q2** | `both` obliges nothing where nothing diverges (13 of 18). Where it diverges: **B1** paths valid in both or resolved; **B2** a discriminator + one branch per audience, sound and audience-false; **B3** each branch durable; **B4** cite components by name, never by authoring-tree path. The precondition's *form* generalises; the *test* does not — three different discriminators are needed, and `/consolidate-memory` admits none, because what differs is authority, not existence. |
| **Q3** | **1 mandatory edit** (the schema) + 19 frontmatter one-liners in **one atomic commit**; 6 body edits as separate tasks; **0** manifest, generator, `sync.mjs` or test edits; registry + 36 of 114 projections regenerated. `audience` does **not** belong in the registry. Commands project to **six** platforms, not seven. |
| **Q4** | `/prepare-release` **reclassify `authoring`**. `/discover-skills` **repair the command** (installer change rejected: an installed registry indexes 79 absent files). `/handoff` **repair the installer** (one line; no command edit). Plus `/consolidate-memory` **repair the command** (a fourth defect, `stable` and destructive). |
| **Q5** | **Option C** — a `.<platform>/skills/local/` sub-path carve-out in `install.sh`, with **Option D** as the interim. `docs/skills/` refused on the merits; a blanket `skills/` exclude refused because it would stop canonical delivery. The brief's two-row rule for `/skillify` is **half a fix** without C. |
| **§4** | **Keep `P2`**, on the argument in §8.2, **conditional on** the `/discover-skills` repair task being `P1` with `**Affects:** command/discover-skills`. Not edited by me. |

## 10. Blockers

### 10.1 `tests/golden/**` — cannot be assessed, and the Q4 repairs plausibly invalidate two checkers

- **Type:** `dependency` · **Severity:** `major` · **Status:** open, escalated, not worked around.

`/discover-skills` and `/handoff` are both `stable`, so `_command_golden_evidence` (criterion 4)
means a golden case exists for each — *inferred* from the criterion being mechanically enforced;
**I did not run the gate.** §6.2 amends `/discover-skills` step 1 and its `## Rails` **Inputs**.
T527 did the analogous thing to `/skillify` and T535 to `/batch`, and in **both** cases the case's
`expect.py` was left asserting strings no document declared, requiring a separately-authorized
re-derivation (T531, T541).

**I cannot tell whether that happens here, because I hold no authorization for `tests/golden/**` —
not even to read it.** I read no `case.yaml`, no `expect.py`, no fixture, and I make no claim about
any of them. Per the brief: **reported, and stopped.**

Every follow-up implementing §6 must therefore begin by reading the relevant case under an
appropriate grant, and must be prepared for a `protected-paths-v1.md` §5 authorization for a checker
re-derivation. `/consolidate-memory` is also `stable` and carries the identical exposure.

### 10.2 `docs/tasks/task-T546.md` does not exist and `active-tasks.md` has no T546 row

- **Type:** `dependency` · **Severity:** `minor` · **Status:** reported per the brief's §5.

The brief states the file is arriving via an unmerged MR and instructs me not to create it. I did
not. There is also **no T546 row** in `docs/tasks/active-tasks.md` on this branch (six rows: T530,
T532, T538, T539, T543, T544). So §8's priority analysis is prospective, and §1.1's finding — that
T532 is `pending` — means the two rows should be reconciled in one edit when the MR lands.

### 10.3 Three unevidenced links this document relies on

Not blockers, but each should be checked by the implementing task before it is trusted:

1. **Vendor skill-discovery recursion** — whether each platform client walks
   `skills/local/*/SKILL.md`. §7.4 degrades to Option D for any client that does not. Cheap to check;
   I could not.
2. **`scripts/merge-task-docs.py`** — whether `--update` carries `docs/tasks/validate-tasks.py`
   into a target. §2.4. I did not read that script.
3. **`implementation/runtime/handoff/`** — I read nothing in it. §6.3's self-containment argument is
   an inference about JSON Schema in general, and the claim that `validator.py` re-implements rather
   than loads `schema-v1.json` is quoted from `active-tasks.md`'s T529/T536/T537 note.

## 11. Consumed by

- **`T532`**, which should be amended to cite this artifact before dispatch. Its `/skillify` verdict
  is §4's B2 plus §7's Option C; without Option C it should ship §7.5's Option D rather than the
  unqualified two-row rule.
- **The one atomic schema-plus-19-frontmatters commit** of §5.3, which needs no protected-path grant.
- **Three or four command-body repair tasks** (§6.1 `/prepare-release`, §6.2 `/discover-skills`,
  §6.4 `/consolidate-memory`, and §4.3's B4 pass over `/batch`), each needing §10.1's golden-case
  check first, and at least the `/discover-skills` one at `P1` per §8.3.
- **One `devops-engineer` task** carrying both `scripts/install.sh` changes together: §6.3's
  `runtime/handoff` line and §7.4's `skills/local/` exclude plus its `validate_before_update`
  warning arms.
- **`T545`**, for §5.4's `AGENTS.md` audience subsection, and for §3.2(e)'s bonus diagnosis of why
  § Knowledge Base bullet 2 omits `.claude/` while bullet 3 includes it (bullet 3 is generated by
  `render_installed_agents.py`; bullet 2 is hand-written source).
- **A new row** for §1.9's `04-protocols.md` dangling reference, cited by four commands, two of them
  `stable`, and found at neither path I probed.
- **Any re-run of** `python3 implementation/scripts/generate-registry.py`,
  `node implementation/scripts/sync.mjs`, `python3 implementation/scripts/check-maturity.py`,
  `python3 docs/tasks/validate-tasks.py` or the functional suite — **all of which this document's
  recommendations require and none of which this session could run.**
