# Artifact: skillify-output-path-resolution-v1.md

> Filename: `skillify-output-path-resolution-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T532
- **Created**: 2026-09-26
- **Based on**: `docs/tasks/task-T532.md` §§1–6;
  `docs/decisions/ADR-007-command-contract-authority.md` (the decision this document applies, whose
  own **status is `proposed`, not accepted** — a `T542` finding; it is used here as a procedure, and
  every verdict's authority is the higher-authority document quoted, not the ADR);
  `docs/artifacts/command-contract-resolution-v1.md`,
  `docs/artifacts/skillify-contract-resolution-v1.md` (`T527`, on this same command) and
  `docs/artifacts/batch-manifest-resolution-v1.md` (`T535`) — the shape this document follows;
  `docs/artifacts/skillify-contract-resolution-v1.md` §5.5 (the defect referred here);
  `AGENTS.md` (§ Knowledge Base, § Skill Workflow);
  `implementation/knowledge/commands/skillify.md`;
  `implementation/knowledge/skills/skillify/SKILL.md`;
  `implementation/scripts/sync.mjs`; `scripts/install.sh`;
  `implementation/platforms/github.json`, `implementation/platforms/claude-code.json`;
  `implementation/registry/summary.md`, `implementation/registry/index.json`;
  `implementation/knowledge/instructions/coding-standards.md`,
  `implementation/knowledge/instructions/git-workflow.md`,
  `implementation/knowledge/instructions/security-guidelines.md`,
  `implementation/knowledge/instructions/poc-guidelines.md`;
  the other 18 `implementation/knowledge/commands/*.md` read for the audience survey (§3);
  `docs/artifacts/protected-paths-v1.md` §§1, 3, 5.
- **Supersedes**: none (first version)

## 0. What this document is, and the answer in one paragraph

`ADR-007` states the principle: *a command's declared contract is authoritative over the corpus
unless the contract contradicts a higher-authority document, or unless the only thing in dispute is a
label for content the corpus already carries.* This document applies that procedure to the defect
`skillify-contract-resolution-v1.md` §5.5 referred forward: `/skillify` declares its output at
`.github/skills/<name>/SKILL.md`, in its `description` frontmatter and in its "Generate the Skill
File" step.

**Verdict: branch 1 fires, on `AGENTS.md` § Knowledge Base, and the amendment deletes nothing.** The
clause directs a hand-write into a **derived** tree in a repository whose top-level convention
document declares `implementation/knowledge/` the source and the platform folders projections. The
amended contract declares **one rule with a checkable precondition** — source tree if
`implementation/knowledge/skills/` exists, every installed platform's skills directory otherwise —
not two acceptable forms.

**The brief's central premise is wrong, and correcting it strengthens the verdict.** `T532` §3 and
the `T527` §5.5 finding it inherits both hold that the declared path "is **correct** for an installed
target project." It is not. `scripts/install.sh --update` replaces `$TARGET/.github` with
`rsync -a --delete` and `skills` is **not** in its protected-paths list, so a `/skillify` output
written there is deleted in a target project too — by a different program, on a different trigger,
with the installer printing the warning itself. The clause is not "right for one audience and wrong
for the other"; it is wrong for both, for two distinct mechanisms.

**On the audience question `T532` §3 actually convened over: nothing is declared, anywhere, in any of
the nineteen commands** — and the ambiguity runs in both directions, with three `stable` commands
naming authoring-repo-only paths that `install.sh` never ships. That is the larger finding (§3), and
it is larger than this one command.

**`/skillify` does not become promotable**, and the golden case is **not** flipped: it fails for the
template reasons `T527` settled, independent of path. A checker change is required and refused (§7).

Like `skillify-contract-resolution-v1.md` and `batch-manifest-resolution-v1.md`, this document is
**both** specification and record of work done: `T532` §4 asked for the execution too. §6 states
exactly what was and was not touched.

## 1. The conflict, enumerated from the files

### 1.1 The clause, verbatim (pre-amendment)

`implementation/knowledge/commands/skillify.md`, frontmatter:

> ```yaml
> description: "Capture the current workflow or a recurring pattern as a reusable skill file (.github/skills/). Use when you discover a useful workflow that should be documented for reuse."
> ```

and `### Generate the Skill File`:

> After the 4-round interview, generate `.github/skills/<name>/SKILL.md` with this structure.

`implementation/knowledge/skills/skillify/SKILL.md` declares the same path twice — `## File
Location` (a fenced one-liner) and the user-facing draft message in `## Review and Approval` step 1
(`**Location:** \`.github/skills/<skill-name>/SKILL.md\``). So this is again a two-documents-one-
artifact situation, and again the skill yields (§4.4), per `T527` §3.2's ruling that the skill is not
a higher-authority document.

### 1.2 The higher-authority text, verbatim

`AGENTS.md` § Knowledge Base, all four bullets, because which bullet is load-bearing turns out to
matter:

> - Source knowledge lives in the emage.code repository under `implementation/knowledge/`; this target uses installed platform projections.
> - Per-platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`, `.clinerules/`, `.cline/`) are **generated** by `scripts/sync.mjs`. **Do not edit them by hand.**
> - Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/`, `.clinerules/`) as runtime references in this target project.
> - Cline auto-detects the root `AGENTS.md` natively …

`AGENTS.md` § Skill Workflow:

> Before implementation, debugging, review response, or completion claims, agents MUST check
> applicable skills in the active platform projection (`.github/skills/`, `.cursor/skills/`,
> `.gemini/skills/`, `.opencode/skills/`, `.pi/skills/`, `.claude/skills/`, `.cline/skills/`) (or
> invoke `/discover-skills`).

### 1.3 What the two programs actually do — read from the code, not assumed

This is the part `T532`'s brief, `T527` §5.5 and `T543`'s scoping each got partly right and partly
wrong, so it is set out from the source.

**`implementation/scripts/sync.mjs`** resolves its root as
`const ROOT = rootArg ? … : path.resolve(__dirname, '..')` (line 47–49) and each platform's output as
`const outRoot = path.resolve(ROOT, manifest.outputDir)` (line 468). With no `--root`, `ROOT` is
`implementation/`, and `implementation/platforms/github.json` sets `"outputDir": ".github"`. **So
`sync.mjs` writes `implementation/.github/`, not the repository root's `.github/`.** Line 472 is the
destructive part:

```js
if (!CHECK_ONLY) {
  await fs.rm(outRoot, { recursive: true, force: true });
}
```

The whole output directory is removed before regeneration. Anything hand-written under
`implementation/.github/skills/` is destroyed on the next `make sync`.

**`scripts/install.sh`** is what writes the repository root's platform folders, and a target
project's. `install_github()` (line 444–448):

```bash
install_tree_into "$IMPLEMENTATION/.github" "$TARGET/.github" "${GITHUB_LOCAL_PATHS[@]}"
```

`install_tree_into` dispatches to `sync_tree_into` when `--update` is set, which runs
`rsync -a --delete` (line 171) with one `--exclude` per protected path. `GITHUB_LOCAL_PATHS`
(lines 262–272) is `workflows ISSUE_TEMPLATE PULL_REQUEST_TEMPLATE.md PULL_REQUEST_TEMPLATE
CODEOWNERS dependabot.yml dependabot.yaml FUNDING.yml copilot-instructions.md`. **`skills` is not in
it.** `validate_before_update()` (line 309–329) prints the consequence in the installer's own words:

> `warning: --update replaces $TARGET/.github entirely (rsync --delete) (except workflows/, ISSUE_TEMPLATE/, PULL_REQUEST_TEMPLATE*, CODEOWNERS, dependabot.y*ml, FUNDING.yml and copilot-instructions.md, which are project-local and left untouched). Other local edits there will be lost.`

The same holds for all seven platforms: `.claude/`'s carve-outs are `settings.json` and
`settings.local.json` only (`CLAUDE_LOCAL_PATHS`, line 255); the other five protect only their MCP
config and its provenance sidecar. **No platform tree has a durable place for a hand-written skill,
in any audience.**

And `install.sh` lines 76–88 refuse to run at the repository root at all unless `--update` is passed,
in which case it warns *"updating in-place at repository root."* That refusal is why the root trees
lag: the only sanctioned way to refresh them is a command whose own warning says it will destroy
local edits there.

## 2. The decision procedure, applied in `ADR-007`'s order

`ADR-007` §2: the first branch that fires decides, and branch 1 is "the loophole to watch" — the
contradiction must be quotable from the higher-authority document's own text. §1.2 quotes it. What
follows is the scrutiny that entitles the claim, including the one place where `AGENTS.md`'s text is
weaker than it looks.

### 2.1 Branch 1 — fires, on `AGENTS.md` § Knowledge Base bullet 1

The load-bearing quotation is bullet **1**, not bullet 2:

> Source knowledge lives in the emage.code repository under `implementation/knowledge/`; this target
> uses installed platform projections.

`AGENTS.md` partitions the world into a source tree and projections of it. Authoring a **new** skill
is a source-knowledge act. A command that directs that act at a projection contradicts the partition
directly, and it does so platform-independently — the sentence names no platform. `ADR-007` §2.1: a
command "may specialise [`AGENTS.md`] but may not create a rival convention for the same thing." A
command that makes a projection the authoring surface is not specialising the partition; it inverts
it.

Bullet 2 ("Per-platform folders … are **generated** by `scripts/sync.mjs`. **Do not edit them by
hand.**") supports the same conclusion but is the weaker citation, for two reasons that a reader
should have in front of them:

1. **Its stated mechanism is factually wrong for the tree `/skillify` names.** §1.3 shows
   `sync.mjs` writes `implementation/.github/`, not the root `.github/`. The root tree is written by
   `install.sh`. `T543`'s discovery is correct on this point and is confirmed here by reading the
   code.
2. **Its list omits `.claude/`.** Bullet 2's parenthesis is `.github/`, `.gemini/`, `.opencode/`,
   `.cursor/`, `.pi/`, `.clinerules/`, `.cline/` — seven entries, but **not** `.claude/`, which
   bullet 3's list *does* include. By `AGENTS.md`'s own text, `.claude/` is therefore not covered by
   the hand-edit prohibition. **Had `/skillify` hardcoded `.claude/skills/` instead of
   `.github/skills/`, bullet 2 would not have been available at all.** A branch-1 verdict that
   depended on which platform a command happened to name would be an accident, not a ruling — which
   is exactly why this verdict rests on bullet 1, which is complete and platform-neutral. Bullet 2's
   omission is a real defect in `AGENTS.md` and is recorded in §5.3 rather than fixed here.

### 2.2 Is an `install.sh`-written file "generated" for the purposes of the prohibition? **Yes.**

`T532`'s dispatch asks this directly and it deserves a direct answer rather than a route around it.

**Yes — and the reason is that the prohibition's operative content is ownership, not authorship.**
"Do not edit them by hand" is a rule about a tree that a program owns and will overwrite. Three
grounds:

1. **The imperative does not depend on the justification.** `AGENTS.md`'s bullet 2 is two
   statements: a claim about provenance and an imperative. Branch 1 asks whether the command's clause
   contradicts `AGENTS.md`; the imperative is what it contradicts. An inaccurate rationale attached to
   a correct rule does not suspend the rule. Holding otherwise is the self-ratifying move `ADR-007`
   §Context exists to refuse — it would let any convention be retired by finding a flaw in its stated
   reason rather than in its substance.
2. **The imperative is *true*, by a different program.** §1.3: `install.sh --update` runs
   `rsync -a --delete` over each platform tree with `skills` unprotected, and says so in its own
   warning text. The predicted harm — "your hand-edit here will be destroyed" — is exactly what
   happens. `AGENTS.md` misnames *which* program owns the tree; it does not misidentify *that* the
   tree is program-owned.
3. **Both candidate readings of "the `.github/` tree" are hostile to hand-edits.**
   `implementation/.github/` is `rm -rf`'d by `sync.mjs` line 472; the root `.github/` is
   `rsync --delete`d by `install.sh --update`. Only the process and the trigger differ.

**The honest qualification, stated because it cuts against me.** The root platform folders are
checked by no gate — `sync.mjs --check` compares only under `implementation/`, so it reports "no
drift" regardless of the root's state, and `T543` records that the root trees currently lag. So a
hand-written skill at the repository root's `.github/skills/` may in practice **survive
indefinitely**, until somebody runs `install.sh --target . --update`. The prohibition is therefore
*under-enforced*, not false. **Under-enforcement is not permission**, and a contract that tells
users to write somewhere that survives only by neglect is worse guidance than one that names the
source of truth. The correct generalisation for a future `AGENTS.md` revision is
**source-versus-derived**, not sync-versus-install: both programs produce derived trees from
`implementation/knowledge/`, and both destroy what they do not generate.

### 2.3 A second branch-1 limb, weaker, and the verdict does not rest on it

`AGENTS.md` § Skill Workflow (§1.2) makes checking skills **mandatory** and enumerates seven equal
platform projections. A command that writes to exactly one of them produces a skill that agents on
the other six are required to look for and will not find. That is a contradiction *in effect* rather
than in letter — § Skill Workflow does not say "a skill must exist in all seven" — so it is recorded
as a corroboration, not as the deciding ground. §2.1 decides the case on its own. This limb does,
however, carry the hardcoding half of the defect (`T532` §2 item 2), and it is why the amendment
generalises the target-project row to every installed platform folder rather than merely swapping one
platform's name for another's (§4.2).

### 2.4 Branch 2 — does not fire, but it is closer than in `T527`

The clause governs a `SKILL.md` at a declared path. The golden case's fixture is
`fixture/.github/skills/verification-before-completion/SKILL.md`. In-class: it is a `SKILL.md`. On
path, `.github/skills/` **remains a declared path** after the amendment — for the installed-target
row — so the fixture is not thrown out of class. `T527` §2.1 already recorded the caveat that
`.github/skills/**` in this repo evidences what the generator emits rather than what `/skillify`
emits; this document makes that caveat's cause precise (§1.3) but reaches the same place: no class
disagreement, branch 2 does not fire.

### 2.5 Branch 3 — unreachable, and there is no corpus for it anyway

3a needs a corpus carrying the same thing under one coherent alternative name; 3b needs a corpus that
omits it. **There is no corpus of `/skillify` outputs at all.** Every one of the 26 skills in
`implementation/registry/summary.md` predates the command or was hand-authored; nothing in this
repository records a skill having been produced *by* `/skillify` at either path. Branch 1 fires
first regardless, and a corpus would not change that — `ADR-007` §2.1: "If the corpus happened to
follow the command and disagree with `AGENTS.md`, this branch would still amend the command." I could
not enumerate directories to prove the absence (§5 states the limits), so this is stated as
"unevidenced," not "verified empty." Nothing in §2.1 depends on it.

### 2.6 Branch 4 — the convenient answer, and why it is not available

A motivated reader could argue: no corpus, a fixture that is a copy of a *generated* file rather than
a `/skillify` output, therefore no contract-vs-corpus conflict, therefore reclassify. **That is the
answer that costs nothing and clears a promotion criterion.** It fails branch 4's own stated
condition — `ADR-007` §2.4: "There is no corpus to fix **and, if the rule is independently backed**,
no contract to amend." The rule here is not independently backed; it is contradicted by `AGENTS.md`
(§2.1). There is a contract to amend, and §2's ordering means branch 1 decides before branch 4 is
reached. The verdict taken instead makes `/skillify`'s contract **harder** to satisfy and leaves the
case red.

## 3. The audience question — the finding that is larger than this command

`T532` §3 asks: does this command's contract address the authoring repo, the target project, or both,
and **does it say so anywhere?** The answer, and the survey behind it.

**Nothing is declared. In any of the nineteen commands. Not in a frontmatter field, not in prose, not
in `## Rails`.** There is no `audience:` key in the command frontmatter (`github.json` keeps
`description`, `agent`, `argument-hint`; `claude-code.json` keeps `description`,
`argument-hint`), no schema slot for one, and no convention section in `AGENTS.md` that names the
distinction. Every command's audience is inferred by the reader from the paths it happens to mention.

**And the ambiguity runs in both directions.** `/skillify` is the only command found that names a
target-project path as a *write* target. Three others name **authoring-repo-only** paths, and two of
the three are `maturity: stable`:

| Command | Maturity | Path it names | Shipped to a target project? |
|---|---|---|---|
| `/discover-skills` step 1 | **stable** | "load `implementation/registry/index.json` (or `registry/summary.md`)" | **No.** `install.sh`'s `install_common()` copies `implementation/docs`, `implementation/runtime/memory` and `implementation/runtime/security` and nothing else from `implementation/`. `implementation/registry/` is never installed. The command's step 1 cannot be performed in a target project. |
| `/handoff` step 3 | **stable** | "conforming to `implementation/runtime/handoff/schema-v1.json`" | **No.** Same reason — only `runtime/memory` and `runtime/security` are installed. Confirmed the file exists in this repo by reading it. |
| `/prepare-release` steps 6–7 | experimental | "regenerate `implementation/registry/summary.md` via `implementation/scripts/generate-registry.py --root implementation`"; "`scripts/verify-release-docs.py --tag v<version>`" | **No.** Neither `implementation/scripts/` nor the repo-root `scripts/` is installed. This command is unambiguously about the emage.code repository's own release process and says so nowhere. |

The remaining fifteen are audience-neutral by accident rather than by design: they name only
`docs/plans/`, `docs/tasks/`, `docs/checkpoints/`, `docs/artifacts/`, `docs/releases/` or the
project's own source, all of which exist in both. `/validate-tasks` ("Run
`python3 docs/tasks/validate-tasks.py` from the project root") is neutral only because
`install_docs()` copies `implementation/docs/` into `$TARGET/docs/`; that is the one mechanism
keeping most of the registry portable, and it is undocumented in any command.

**So: the distinction is real, load-bearing, undeclared across the board, and already broken in both
directions in `stable` components.** `/skillify` is the instance that happened to be adjudicated;
`/discover-skills` and `/handoff` are the same defect class in components that have already been
promoted. **This is a larger finding than `T532` and should be its own task** — the shape of the fix
is a declared audience field (`audience: authoring | target | both`) plus one pass over all nineteen
commands, not nineteen ad-hoc amendments. It is recorded in §5.3 and §9, not executed here: minting a
frontmatter key touches `implementation/knowledge/schemas/command.schema.json`, all seven platform
manifests' `keepKeys`, `generate-registry.py` and every projection, which is far outside a
single-clause adjudication and is exactly the blast-radius argument `batch-manifest-resolution-v1.md`
§3.1 used to decline a comparable widening.

## 4. The four repair options, and the three that were rejected

Branch 1 firing settles that the command changes. It does not say to what.

### 4.1 Rejected — `.github/skills/` → `implementation/knowledge/skills/`, and nothing else

**Grounds: it is the smallest edit, it cures the letter of branch 1, and it relocates the audience bug
rather than fixing it.** A target project has no `implementation/knowledge/` — that is the first thing
`AGENTS.md` bullet 1 says about a target ("this target uses installed platform projections"). This
command is projected into all seven platform folders and installed into every target project, so
target projects are its **larger** audience. An amendment that leaves them with a path that does not
exist there has moved the defect, not removed it, and `T535` §3.4 and `plan-076` both name "it is the
smallest available edit" as the wrong reason to choose anything.

### 4.2 Rejected as stated — list all seven platform paths, unconditionally

**Grounds: it cures the hardcoding and leaves the authority conflict standing.** All seven platform
folders are derived trees in an authoring checkout, so seven wrong paths contradict `AGENTS.md`
bullet 1 exactly as one did. `ADR-007` Alternative C also applies: "a shipped, user-facing command
that declares two acceptable output forms is worse guidance than one that declares one" — seven is
worse still. The *generalisation to all installed platforms* survives as the target-project half of
the accepted verdict (§4.3), where it is a set, not a menu; what is rejected is doing it
unconditionally, for both audiences.

### 4.3 Rejected — mint a durable project-local skill home (e.g. `docs/skills/`)

This option is genuinely attractive and is rejected on the `batch-manifest-resolution-v1.md` §3.2
ground: **it mints a namespace to solve a problem, inside an adjudication that has no mandate to mint
one.**

The problem is real. §1.3 establishes that **no** platform tree in an installed target project
survives `install.sh --update`, and `install_docs()` under `--update` uses
`merge_tree_preserve_existing` → `rsync -a --ignore-existing`, which never overwrites and never
deletes — so `docs/**` is in fact the one installed tree the installer treats as the project's own,
and would be a durable home. But declaring `docs/skills/` would create a new file class in a
directory whose contents no document enumerates for that purpose, it would be invisible to every
platform's skill loader (so it would need a second, derived copy anyway), and `/discover-skills` — the
command that finds skills — reads a registry that a target project does not have (§3). The right fix
is a durable, *loadable* project-local skill home plus an installer carve-out, which is a harness
design change with an `install.sh` edit in it. **The door is named here rather than walked through**
(§5.3, §9), and the accepted verdict instead makes the loss *visible* at the approval step rather
than silent (§4.4).

### 4.4 Accepted — one rule, one checkable precondition

**Amend the contract** (branch 1). The declared path becomes a function of a test the agent performs:

| Precondition | Declared output | Declared follow-through |
|---|---|---|
| `implementation/knowledge/skills/` exists — an authoring checkout | `implementation/knowledge/skills/<name>/SKILL.md` | re-run `node implementation/scripts/sync.mjs` **and** `python3 implementation/scripts/generate-registry.py --root implementation`; never hand-write a platform folder |
| it does not — an installed target | `<platform>/skills/<name>/SKILL.md` in **every** installed platform folder that exists | tell the user at the approval step that `install.sh --update` replaces those trees wholesale |

Four properties make this the right shape and make it `ADR-007` §5-safe:

1. **It is one rule, not two admitted forms.** §5 prohibits "admitting a second form for
   convenience." The two rows are **mutually exclusive by a checkable predicate** — a directory either
   exists or does not — so no author ever chooses between them, and no reader is left with a menu.
   This is the distinction a suspicious reader should press on, and it is the reason the amended text
   states it in the file itself: *"This is one rule with a precondition, not two acceptable output
   forms."* A second form for convenience would be "write to either place"; this is "the source of
   truth is here, and which place that is follows from what the project is."
2. **Nothing is deleted and nothing is loosened.** The old contract required one path. The new one
   requires a path *plus* a precondition check, *plus* two generator invocations in the authoring
   case, *plus* a copy into every installed platform folder in the target case, *plus* a named
   disclosure at the approval step. The amended contract is strictly harder to satisfy. Per
   `ADR-007` Validation criterion 1, a follow-up that produces a *shorter* requirement list than this
   has misread the verdict.
3. **The target-project row degrades correctly.** `install.sh --platform cursor` produces a project
   with one platform folder, and "every folder that exists" is then that one folder. The rule needs no
   special case for single-platform installs.
4. **The loss becomes visible instead of silent.** `/skillify` already had a "Present for Approval"
   step; it is the natural place to say "and this will be deleted by the next harness update." A
   contract that requires the user to be told is better than one that quietly writes into a tree the
   installer owns.

**Counter-reading, recorded because it is respectable.** A reviewer may prefer that the
target-project row name only the *active* platform's folder rather than all that exist: seven
hand-maintained copies of one file, with no generator keeping them in step, is a drift factory, and
in an authoring checkout the seven copies are consistent *precisely because* a generator makes them.
That objection is real. It is outweighed by the failure it trades for — a skill invisible to six of
seven platforms, when `AGENTS.md` § Skill Workflow makes checking skills mandatory and lists all
seven — and by the fact that a skill file is edited rarely. **The verdict is robust to being
overruled here:** `.github/skills/` remains in the declared set under either reading, so no golden-case
outcome (§5.2) and no promotion outcome (§8) moves.

### 4.5 The `description` frontmatter — changed, and a correction to the brief

The parenthetical `(.github/skills/)` is removed; the rest of the sentence is unchanged. Two reasons:
a one-line command description is not a place for a two-branch conditional, and naming one platform's
path in it is the hardcoding being cured. `description` is in `keepKeys` for every platform manifest
read (`github.json`, `claude-code.json`), so it is user-visible in all seven projections' command
pickers.

**Correction:** `T532`'s dispatch says "that field is what `/discover-skills` surfaces." It is not.
`/discover-skills` step 1 loads `implementation/registry/index.json`, whose entries carry `id`,
`category`, `name`, `path`, `checksum`, `maturity` and `compatibility` — and **no `description`**
(verified by reading the file). The field is surfaced by each platform's own slash-command UI. This
does not change the decision to amend it; it changes who sees it.

### 4.6 The skill file yields, as in `T527` §4.2

`skills/skillify/SKILL.md` declared the same superseded path in two places (§1.1). Leaving them would
recreate exactly the two-contracts-for-one-artifact condition `T527` §4.3 had just eliminated. Per
`T527` §3.2's ruling — the skill is `experimental`, is not `AGENTS.md`, not a `stable` instruction and
not another clause of the command, so under `ADR-007`'s core rule the command's contract is
authoritative against it — the skill is amended to match. **It restates the rule by reference and
names the command as authoritative**, deliberately, so the two documents cannot drift again the way
they just did.

## 5. Re-verification, method limits, and what the inputs got wrong

**Method, stated plainly and up front: this session had no shell, no `grep`, no directory listing, and
no ability to execute anything.** `implementation/knowledge/agents/solution-architect.md` declares
`tools` without `execute`; `claude-code.json`'s `toolMap` maps my grant to `Read`, `Edit`, `Write`,
`WebFetch`, `WebSearch`, `TodoWrite` and no `Bash`. Every finding here was derived by reading named
files. **I ran no test, no validator, no checker, no generator and no script, and I claim no
verification that requires one.** Specifically I did not and could not run
`node implementation/scripts/sync.mjs`, `python3 implementation/scripts/generate-registry.py`,
`scripts/scorecard.py`, `implementation/scripts/check-maturity.py`, or the golden case's `check()`.

I also **did not read anything under `tests/golden/`**, by instruction, so §7's specification is
derived from `skillify-contract-resolution-v1.md` §6's element inventory of that file plus what
follows logically from the amendment — **not** from the file's current bytes. `T531` re-derived it
after `T527`, so its present content is known to me only at second hand. §7 says so where it matters.

### 5.1 Findings that correct or qualify the inputs

| Claim | Finding | Verdict on the claim |
|---|---|---|
| `T532` §3 and `T527` §5.5: "The path is **correct** for an installed target project" | **Wrong, and this is the most consequential correction here.** `install.sh`'s `install_github()` → `install_tree_into` → `sync_tree_into` runs `rsync -a --delete` on `$TARGET/.github` with only `GITHUB_LOCAL_PATHS` excluded, and `skills` is not among them; `validate_before_update()` prints "replaces $TARGET/.github entirely (rsync --delete) … Other local edits there will be lost." A `/skillify` output is destroyed in a target project too. The clause is wrong for **both** audiences, by two different programs. | **Wrong premise; it strengthens the verdict rather than weakening it.** |
| `T532` §2 item 1: "`AGENTS.md` states `.github/` is generated by `scripts/sync.mjs` and must not be edited by hand. A `/skillify` output written there **in this repo** is destroyed by the next sync." | **Half right.** The prohibition is real and quotable, but the named mechanism is wrong for the tree in question: `sync.mjs` has `ROOT = path.resolve(__dirname, '..')` = `implementation/`, so it writes `implementation/.github/`. A file at the repository root's `.github/skills/` is **not** touched by `make sync`; it is destroyed by `install.sh --target . --update`. | **Right conclusion, wrong mechanism — same shape as `T527` §2.1's "wrong premise, right conclusion" row.** |
| `T543`: the root platform folders are refreshed by no generator, checked by no gate, and are *installed* by `install.sh --update` rather than generated | **Confirmed by reading both programs, with one refinement.** "Refreshed by no generator" is better stated as "refreshed only by an explicitly-invoked installer that `install.sh` lines 76–88 *refuse* to run at the repository root unless `--update` is passed" — which is why they lag. And the installer is *more* destructive than `sync.mjs` in one respect (`rsync --delete` over the whole tree in a target project) while running far less often. | **Accurate and load-bearing; see §2.2 for the answer it was raised to prompt.** |
| `T532` dispatch: `skillify.md`'s `description` "is what `/discover-skills` surfaces" | **Not accurate.** `/discover-skills` reads `implementation/registry/index.json`, whose entries carry no `description` (read directly). The field is surfaced by each platform's command picker instead. Does not change the amendment (§4.5). | **Wrong consumer named; the field still needed changing.** |
| `ADR-007`'s status is `proposed`, not `accepted` (a `T542` finding, restated in the dispatch) | **Confirmed by reading the ADR's own `- **Status**: proposed` line.** Handled as the dispatch directs: `ADR-007` is used as a *procedure*, and this verdict's authority is `AGENTS.md` § Knowledge Base bullet 1, quoted verbatim in §1.2 and checkable without taking either document's word for it. | **Accurate; noted and worked around correctly.** |
| `T532` §2 item 2: the clause "hardcodes one platform of seven" | **Confirmed**, and it is a live functional defect, not cosmetic: `AGENTS.md` § Skill Workflow makes skill-checking mandatory and lists all seven projections, so a skill in one is invisible to the other six (§2.3). | **Accurate and understated.** |
| `T527` §5.5: the other six platform skills directories "are equally valid targets per `AGENTS.md`'s own Skill Workflow list" | **Confirmed**, and `AGENTS.md` § Knowledge Base bullet 2's own list is **inconsistent with itself** on this: it omits `.claude/` while bullet 3 includes it (§2.1 item 2). | **Accurate, and it surfaced a defect in `AGENTS.md`.** |

### 5.2 Does the golden case pass? **No — and the path amendment is not why**

`skillify-skill-file-template-drift` scored **1 of 5** sections after `T527`'s amendment
(`skillify-contract-resolution-v1.md` §5.3: `## When to Use` passes; `## Inputs`, `## Procedure`,
`## Success Criteria`, `## Examples` fail against the fixture
`.github/skills/verification-before-completion/SKILL.md`). **Nothing in this verdict touches a
section name, so the score is unchanged and `check()` still returns `False`.** I could not run it and
did not read the file; this follows from `T527` §5.3's traced table plus the fact that §4.4 changes
only a path.

`case.yaml` was **not** touched and **must not** be flipped on this document's word.

`ADR-007`'s sibling-fate corollary applies here more cleanly than in any prior case in this series.
Its table's first row reads: *"1, where the amendment changes only a **name or path** → survives;
fixture/glob updated to the amended form."* **This is the first verdict in the series where that row
applies literally** — `T527` changed section labels, `T535` arguably changed an artifact class, and
this one changes a path and nothing else. The prediction is therefore unambiguous: the case survives,
the glob is updated, the fixture stays in class (§2.4), and the case stays red for template reasons.

### 5.3 Observations outside this task's scope, recorded not acted on

1. **`AGENTS.md` § Knowledge Base bullet 2 is wrong in two ways** (§2.1): it names `scripts/sync.mjs`
   as the generator of the root platform folders, which the code contradicts, and its "do not edit"
   list omits `.claude/` while bullet 3's list includes it. Both should be fixed, and the fix should
   generalise the rule to **source-versus-derived** so it covers `install.sh` too. **Not touched
   here:** `AGENTS.md` is the top-level convention document this verdict *cites as authority*, and
   amending the authority in the same breath as applying it would invert the ordering `ADR-007` just
   used. It needs its own task. `docs/artifacts/protected-paths-v1.md` §6 carries the same
   imprecision ("`implementation/scripts/sync.mjs` regenerates every platform's agent projection …
   the pointer therefore appears in every platform projection folder (`.claude/agents/`, `.cursor/`,
   …)"), which is true of `implementation/.claude/agents/` and not of the root's.
2. **The undeclared-audience defect is repository-wide** (§3), and it is already broken in two
   `stable` commands: `/discover-skills` step 1 and `/handoff` step 3 both name
   `implementation/`-only paths that `install.sh` never copies, and `/prepare-release` steps 6–7 are
   wholly about this repository's own release process. **This deserves its own task**, with a declared
   `audience:` field and one pass over all nineteen commands. Not executed: it touches
   `command.schema.json`, seven platform manifests' `keepKeys`, `generate-registry.py` and every
   projection.
3. **An installed target project has no durable, loadable home for a locally-authored skill**
   (§4.3). Every platform tree is swept by `install.sh --update`; `docs/**` survives
   (`rsync --ignore-existing`) but no skill loader reads it, and `/discover-skills`'s registry is not
   installed. This is a harness design gap needing an `install.sh` carve-out or a declared
   project-local skills path, and it is the thing that would let §4.4's target-project row stop
   carrying a warning.
4. **`/new-project` step 1, `/new-feature` step 1 and `/validate-workflow` step 5 all cite
   `04-protocols.md`**, a document I found no trace of in anything I read. If it does not exist, three
   commands (two of them `stable`) reference a dangling protocol document. **Flagged, not verified** —
   I cannot list directories, so I cannot prove absence. Unrelated to `/skillify`.
5. **`task-T532.md` declares `**Affects:** —`.** The honest value is `command/skillify` plus
   `skill/skillify`. It is `P2`, so nothing turns on it, and `T532` §4 authorized only the
   `**Status:**` edit on that file. Flagged rather than changed — the same call
   `batch-manifest-resolution-v1.md` §5.3.3 made.

## 6. What was executed, and what was deliberately not

### 6.1 Executed

| File | Change |
|---|---|
| `implementation/knowledge/commands/skillify.md` | `description` frontmatter loses the `(.github/skills/)` parenthetical (§4.5). A new `### Choose the Output Path` section is inserted before `### Generate the Skill File`, carrying §4.4's two-row rule, the explicit "one rule with a precondition, not two acceptable output forms" statement, and the two `AGENTS.md` citations. `### Generate the Skill File` now says "at the path chosen above"; its section list, ordering and round-mapping sentence are **byte-identical otherwise** — `T531` re-derived `expect.py` against exactly those five strings and none of them moves. `### Present for Approval` requires the chosen path and the durability warning to be named. `## Rails` § "Out of scope" gains the authoring-checkout clause; all three Rails labels remain present, so `maturity-promotion-criteria-v2.md` §3.4.2 criterion 2 is unaffected. |
| `implementation/knowledge/skills/skillify/SKILL.md` | `## File Location`'s fenced `.github/skills/<skill-name>/SKILL.md` is replaced by the same two-branch rule stated by reference, naming `commands/skillify.md` as authoritative (§4.6). The `## Review and Approval` draft message's hardcoded `**Location:**` line becomes `<the exact path(s) chosen per § File Location>`. The `## SKILL.md Template` block, the four interview rounds and everything `T527` §4.2 touched are **unchanged**. |
| `docs/artifacts/skillify-output-path-resolution-v1.md` | This document. |
| `docs/tasks/task-T532.md` | `**Status:** pending` → `in_review`. **No ledger row touched** — archival is orchestrator-only per `AGENTS.md` § Task Protocol. |

**The skill-file edit is beyond `T532` §4's named deliverable**, which lists only
`commands/skillify.md`. It is inside this round's stated grant over `implementation/knowledge/`, it
follows the direct precedent of `T527` §4.2 amending this exact file for this exact reason, and
leaving it would have re-created the two-contracts defect `T527` §4.3 closed. **Flagged prominently
so the orchestrator can revert it if the grant is read narrower than I have read it** — the command
amendment stands on its own without it.

### 6.2 Not executed

| Not done | Reason |
|---|---|
| `tests/golden/open/skillify-skill-file-template-drift/expect.py` | **Required, and refused.** `T532` §5 excludes it and instructs a blocker; `protected-paths-v1.md` §5 item 1 forbids a silent edit and item 2 requires a named, orchestrator-authored authorization. §5 of that document also forbids widening my own grant, so `T532` §5's table was not edited either. See §7. Matching `T520`, `T523`, `T525`, `T527`, `T531` and `T535`. |
| **Reading** anything under `tests/golden/` | Not required by `protected-paths-v1.md` (§3 freezes write scope, not read scope), but the dispatch said "stay out of `tests/golden/` entirely," and reinterpreting an explicit boundary as a write-only boundary to improve my own deliverable is the wrong trade. The cost is real and is disclosed in §5's preamble and §7. |
| `case.yaml` status flip or `known_failing_reason` rewrite | The verdict does not make `check()` return `True` (§5.2), and I cannot run it. Any grant is conditional on a genuine pass. |
| `brief.md` restatement | Another agent is editing that file this round. Its path-related staleness is specified in §7 for whoever owns it. |
| `AGENTS.md` | §5.3.1 — it is the authority this verdict cites; amending it while applying it inverts the ordering. Its two defects need their own task. |
| A declared `audience:` frontmatter field on all nineteen commands | §3 and §5.3.2 — the right fix for the larger finding, and far outside a single-clause adjudication. |
| A durable project-local skills path, or an `install.sh` carve-out for `<platform>/skills/` | §4.3 and §5.3.3 — a harness design change with a shell-script edit in it. The verdict makes the loss visible instead; it does not pretend to prevent it. |
| `## Rails` in either template (`T527` §3.7) and `## Required Context` in the skill (`T527` §4.4) | Still open, still outside this task's clause. Unchanged by this verdict. |
| `commands/skillify.md`'s `maturity:` field | Still `experimental`. A maturity flip is a component-state decision (`T526`/`T534` precedent), not an adjudication outcome, and §8 says it would not be earned anyway. |
| Platform projections (`.claude/`, `.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.cursor/`, `.cline/`) and `implementation/registry/` | Generated. `AGENTS.md` forbids hand-editing them — and this verdict's whole point is that authoring into a derived tree is the defect. They will show drift until **both** `node implementation/scripts/sync.mjs` and `python3 implementation/scripts/generate-registry.py` are re-run: `sync.mjs --check` alone does not catch registry drift, and `index.json` carries a per-entry `checksum` that any edit to a source file invalidates. |

## 7. Blocker — `expect.py` must be re-derived, and this task refused to do it

- **Type:** `technical` · **Severity:** `minor` · **Status:** open, escalated, not worked around.

**Severity is `minor`, not `major`, and the downgrade from `T527` §6 and `T535` §7 is deliberate.**
In both of those, the checker asserted strings **no document declared any more**. Here the amendment
*adds* declared paths without retiring `.github/skills/`: the installed-target row still names it. So
the existing checker remains a valid, merely **narrow**, check of the live contract — it tests one
declared path out of a declared set — rather than a check of a superseded one. Nothing is
mis-reported and nothing is measuring a dead contract. It should still be widened, and the docstring
is now stale either way.

**Specification for the authorized follow-up.** `ADR-007` Validation criterion 1 requires the
replacement to assert the same number of structural elements with the same ordering and value
constraints.

**Caveat on this specification, stated first because it limits it:** I did not read `expect.py` (§6.2),
so the element names below come from `skillify-contract-resolution-v1.md` §6's inventory of that file
(module docstring; `TITLE_RE`; the `is_dir()` guard; the `len(candidates) != 1` guard;
`REQUIRED_SECTIONS`; the `all(section in text …)` substring operator; `main()`) and `T531` re-derived
it after that was written. **The authorized task must reconcile these element names against the live
bytes before applying anything here**, and must treat a mismatch as a signal to re-derive from the
amended contract rather than to force-fit this table.

| Element (per `T527` §6's inventory) | Required change | Strength |
|---|---|---|
| Module docstring's quoted clause | Update to the amended `### Choose the Output Path` rule. Quote **both** rows, and state that the fixture exercises the installed-target row. | unchanged — documentation |
| The fixture-discovery path expression (whatever now resolves `.github/skills/`) | Widen from one hardcoded segment to the declared set. Two acceptable derivations, and the authorized task should pick one and say which in the docstring: **(i)** search `implementation/knowledge/skills/` **and** each of the seven `<platform>/skills/` directories, keeping the existing `is_dir()` and `len(candidates) != 1` guards so exactly one candidate must still resolve across the whole set; or **(ii)** relocate the fixture to `fixture/implementation/knowledge/skills/<name>/SKILL.md` and point the expression at the authoring-checkout row, which is the row `AGENTS.md` makes authoritative for this repository. | **unchanged in count; stronger under (i)** — a wider search with the same "exactly one candidate" guard is a stricter uniqueness assertion, not a looser one. Under (ii) it is unchanged in count and narrower in scope. |
| `TITLE_RE`, `REQUIRED_SECTIONS`, the `all(section in text …)` substring operator, `main()` | **Byte-identical.** This verdict changes no section name and no operator. `T531`'s five `REQUIRED_SECTIONS` strings all stand. | unchanged |
| *(none)* | Do **not** add an assertion that the skill exists in all seven platform folders. That is §4.4's counter-reading territory, the fixture carries one folder, and adding it would strengthen the check beyond what this verdict decided. | deliberately omitted |

`ADR-007` §5 is satisfied by construction: nothing is deleted, no regex is loosened, and no second
form is admitted — the widened path set mirrors a contract that now declares a set, and the "exactly
one candidate" guard is retained so the set does not become a disjunction the fixture can satisfy
cheaply.

The same authorization should carry:

- **`brief.md`** — its `## What this checks` and `## Pass condition` sections quote the command's
  clause, which now names a different path. **Note: another agent is editing this same file this
  round** for `T527`'s template staleness (`skillify-contract-resolution-v1.md` §5.4). These two sets
  of corrections should land in **one** authorization, not two, or the second will conflict with the
  first.
- **`case.yaml`** — its `known_failing_reason` should not be rewritten to mention the path at all:
  after `T527` §4.3 and this verdict, the case is a plain branch-3b standing red (the corpus does not
  carry the declared sections), and the path was never its failure cause.
- The follow-up must **run** `check()` and report the observed result. **It will still return
  `False`** (§5.2). I could not, and did not.

## 8. Is `/skillify` promotable? **No — and this task does not move it.**

Stated plainly, against `docs/artifacts/maturity-promotion-criteria-v2.md` §3.5, and unchanged from
`skillify-contract-resolution-v1.md` §7's answer: the golden case remains `known_failing` with
`known_failing_category: tracked_defect` and `command: /skillify`, so §3.5's second limb fires and
command criterion 7 stays red. `/skillify` is also still `maturity: experimental` per
`implementation/registry/summary.md` and has not met the `experimental → beta` bar, which is a
component-state decision and not an adjudication outcome.

The cheapest green was available here (§2.6 — reclassify to `capability_gap`, no command edit,
criterion cleared today) and was refused on branch 4's own stated condition. The verdict taken
instead makes the contract strictly harder to satisfy (§4.4 item 2) and leaves the case red. **No
promotion should be granted on this document; `implementation/scripts/check-maturity.py` must be
re-run for real, and I ran nothing.**

`ADR-007` §Consequences predicted an uneven result and warned that a clean sweep would be the
suspicious one. This is the uneven shape: a contract amended, a case still red, two follow-up tasks
opened, and one defect found in the document that supplied the verdict's own authority.

## 9. Consumed by

- The authorized follow-up implementing §7 — `expect.py`'s path expression and docstring, folded
  into the **same** authorization as `T527` §5.4's `brief.md`/`case.yaml` corrections, under a
  `protected-paths-v1.md` §5 grant authored by the orchestrator and not by this document.
- **A new task for §3 / §5.3.2** — the undeclared-audience defect across all nineteen commands, with
  `/discover-skills` and `/handoff` (both `stable`) and `/prepare-release` as its confirmed
  instances. This is the finding `T532` §3 asked for and it is larger than `T532`.
- **A new task for §5.3.1** — `AGENTS.md` § Knowledge Base bullet 2's wrong generator, its missing
  `.claude/`, and the source-versus-derived generalisation; plus the same imprecision in
  `protected-paths-v1.md` §6.
- **A new task for §5.3.3** — a durable, loadable project-local skills home in an installed target,
  which is what would let §4.4's target-project row drop its durability warning.
- Optionally, a check of §5.3.4's `04-protocols.md` references in `/new-project`, `/new-feature` and
  `/validate-workflow`.
- Any re-run of `node implementation/scripts/sync.mjs`,
  `python3 implementation/scripts/generate-registry.py --root implementation`,
  `scripts/scorecard.py`, `implementation/scripts/check-maturity.py` or
  `docs/tasks/validate-tasks.py` — all of which this task's changes require or invite, and **none of
  which this task could run.**
