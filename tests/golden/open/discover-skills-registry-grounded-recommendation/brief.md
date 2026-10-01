# Case: discover-skills-registry-grounded-recommendation

## Command under test
`/discover-skills`

## Brief (illustrative — not executed live)
"Which skills apply to implementing T525's golden cases and marking the task done?" — an
implementation-phase intent that ends in a done claim.

## What this checks
`implementation/knowledge/commands/discover-skills.md` `## Instructions` steps 1, 3 and 4, and the
`## Output format` block.

Step 1, verbatim (as amended by T554, which repaired it per
`docs/artifacts/command-audience-resolution-v1.md` §6.2 — before T554 it read "load
`implementation/registry/index.json`", a file `install.sh` never ships to a target):

> 1. **Enumerate skills** — a skill is a directory holding a `SKILL.md`. Where they live depends on whether `implementation/registry/index.json` exists:
>
>    | `implementation/registry/index.json` | You are in | Enumerate skills from |
>    |--------------------------------------|------------|-----------------------|
>    | exists | the emage.code authoring repository | `implementation/knowledge/skills/*/SKILL.md`. The registry's `category: skill` entries index this same tree and may be read instead, as an accelerator (`implementation/registry/summary.md` for an overview); where the two disagree, the tree wins. |
>    | does not exist | an installed target project | `.<platform>/skills/*/SKILL.md` — the active platform projection (`.claude`, `.cline`, `.cursor`, `.gemini`, `.github`, `.opencode` or `.pi`). Targets have no registry; do not look for one. |
>
>    Test for the registry file itself, never for `implementation/` — the installer creates `implementation/runtime/` in target projects too. Recommend only skills this step enumerated.

Step 3, verbatim:

> 3. **Recommend skills** — return a ranked table:
>
> | Skill | Why | Mandatory? |
> |-------|-----|------------|

Step 4, verbatim (first rule only — it is the one this case's intent triggers):

> 4. **Apply mandatory rules** from `AGENTS.md` Skill Workflow:
>    - Implementation → `verification-before-completion` before done claims

`## Output format`, verbatim:

> ```markdown
> ## Recommended skills for: <intent>
>
> ### Mandatory
> - ...
>
> ### Suggested
> - ...
>
> ### Next command
> `/...` or load the `<name>` skill
> ```

**The load-bearing assertion is step 1's, and it is the reason this case is worth having.** Step 1
says the recommendation is produced by *enumerating the skills tree* — so every skill the output
names must be a skill that enumeration actually contains. That is the difference between a
recommendation and a plausible-sounding list, and it is the one failure mode of this command that a
reader cannot catch by eye: a confidently-formatted table naming `context-budget-management` or
`release-checklist` looks exactly as correct as one naming `context-window-management` or
`release-workflow`. The check fails on any name that does not resolve — and naming a real *agent*
or *command* id in a skills table fails too, because neither is a `category: skill` entry nor a
`<name>/SKILL.md` directory.

**Step 1 has two rows, and the fixture exercises both.** The discriminator is whether
`implementation/registry/index.json` exists, and the fixture carries one recommendation and two
repository roots against which it must ground:

| Root | Discriminator | Row | Enumeration the check resolves against |
|---|---|---|---|
| `fixture/` | registry present | authoring | the registry's `category: skill` entries — the accelerator step 1 permits reading instead of the tree. This root carries no `implementation/knowledge/skills/`; where a root does, the check resolves against that tree instead ("where the two disagree, the tree wins"). |
| `fixture/installed-target/` | registry absent | target | every `<name>/SKILL.md` under the seven platform projections' `skills/` directories (`.claude`, `.cline`, `.cursor`, `.gemini`, `.github`, `.opencode`, `.pi` — the `outputDir` of each `implementation/platforms/*.json` manifest); this root carries `.github/skills/`. |

Every cited name must resolve in **both** roots, and each root must land in the row it exists to
exercise — a fixture that loses its target root, or whose target root gains a registry, fails rather
than silently testing one row. The platform list is fixed, not a `.*` glob: a dot-directory that is
not a platform projection is not a skills tree, and a directory without a `SKILL.md` is not a skill.

**Not relaxed (ADR-007 §5).** The pre-T554 check resolved names against the registry alone. The
re-derived check runs that same resolution for the authoring root of this fixture and adds the target
root on top, so for the committed fixture it is strictly stronger: in a temp-fixture matrix, an
invented skill was rejected under each row independently (present only in the target tree → the
authoring row rejects it; present only in the registry → the target row rejects it; present in
neither → both reject it), and across 2,000 randomised fixture mutations without a knowledge tree
the new check accepted nothing the old one rejected. The one place it can accept what the old check
rejected is a root that carries `implementation/knowledge/skills/` with a real `<name>/SKILL.md` the
registry lacks — a stale accelerator hiding a real skill, which step 1 says the tree overrules.

Step 4's rule is checked as a second, independent assertion: for an implementation intent ending in
a done claim, `verification-before-completion` must appear under `### Mandatory` specifically, not
merely somewhere in the document.

## Pass condition
`fixture/recommendation.md` contains all four declared output-format headings
(`## Recommended skills for:`, `### Mandatory`, `### Suggested`, `### Next command`); contains at
least one table with the declared `| Skill | Why | Mandatory? |` header row; names at least one
skill; `fixture/` lands in step 1's authoring row and `fixture/installed-target/` in its target row,
each enumerating at least one skill; every name in a `| Skill |` column resolves to a skill that row
enumerates in **each** root; and `verification-before-completion` appears in the `### Mandatory`
section.

## Provenance
**Registry: real, and a snapshot.** `fixture/implementation/registry/index.json` is a copy of this
repository's own `implementation/registry/index.json` taken at authoring time (`generatedAt`
2026-09-25; 79 entries: 28 `agent`, 19 `command`, 6 `instruction`, 26 `skill`). It is no longer
byte-identical to the live file: by T554's base (`19ab1e7`) later edits had moved its `generatedAt`,
17 `checksum`s and 7 `maturity` values. Its 26 `category: skill` ids are unchanged, and at that base
they equal both `implementation/knowledge/skills/*/` and every platform projection's `skills/*/`.
The check reads only `id` and `category`.

**Target skills tree: real frontmatter, bodies omitted.** `fixture/installed-target/.github/skills/
<name>/SKILL.md` holds, for each of the 26 skills, lines 1–4 of
`implementation/.github/skills/<name>/SKILL.md` at `19ab1e7` verbatim — the `name`/`description`
frontmatter every platform manifest keeps (`frontmatter.skills.keepKeys`) — and nothing else. All
seven projections' `skills/` trees were byte-identical at that commit, so `.github` stands for any of
them; it is also the platform the `skillify` case's fixture already uses. The bodies are omitted
because the check reads only the existence of `<name>/SKILL.md`, and because several bodies carry
relative links (`../../../../docs/…`) that would dangle at this depth and fail
`tests/functional/test_link_integrity.py`. `.claude` was avoided deliberately: Claude Code loads a
nested `.claude/skills/` the first time it reads or edits a file below it, and a fixture must not
inject 26 duplicate skills into an agent session.

**`recommendation.md` is hand-authored**, as the agent-side output under test. A corpus survey
(`grep -rl "## Recommended skills for:" . --include=*.md`) returned 11 matches, and every one of
them is either `implementation/knowledge/commands/discover-skills.md` itself or one of its 10
platform projections under `implementation/.{claude,gemini,github,opencode,pi}/` and the installed
`.{claude,gemini,github,opencode,pi}/` — i.e. every hit is the command's own declared *template*,
and **zero are produced output**. Excluding those paths leaves an empty result set: no real
`/discover-skills` output has ever been committed to this repository, so there was nothing real to
source this file from. That absence is documented rather than worked around, following
`new-feature-plan-doc-compliant/brief.md`'s precedent. The five skill names it cites were checked
against the registry at authoring time; the check re-derives that resolution from both roots'
enumerations rather than trusting the authoring-time survey. T554 changed one line of it, the
`### Next command` line, from "read `skills/verification-before-completion/SKILL.md`" to "load the
`verification-before-completion` skill", tracking the amended output format (ADR-007 §5: re-authoring
a hand-authored fixture to a corrected contract is not relaxation; the check does not read that
line).
