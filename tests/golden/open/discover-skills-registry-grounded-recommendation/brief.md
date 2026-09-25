# Case: discover-skills-registry-grounded-recommendation

## Command under test
`/discover-skills`

## Brief (illustrative — not executed live)
"Which skills apply to implementing T525's golden cases and marking the task done?" — an
implementation-phase intent that ends in a done claim.

## What this checks
`implementation/knowledge/commands/discover-skills.md` `## Instructions` steps 1, 3 and 4, and the
`## Output format` block.

Step 1, verbatim:

> 1. **Read registry** — load `implementation/registry/index.json` (or `registry/summary.md` for overview).

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
> `/...` or read `skills/<name>/SKILL.md`
> ```

**The load-bearing assertion is step 1's, and it is the reason this case is worth having.** Step 1
says the recommendation is produced by *loading the registry* — so every skill the output names
must be a skill the registry actually contains. That is the difference between a recommendation and
a plausible-sounding list, and it is the one failure mode of this command that a reader cannot
catch by eye: `implementation/registry/index.json` holds 79 entries across four categories, of
which 26 are `category: skill`, and a confidently-formatted table naming
`context-budget-management` or `release-checklist` looks exactly as correct as one naming
`context-window-management` or `release-workflow`. This case resolves every name in the
`| Skill |` column against the real registry and fails on any that does not resolve **to an entry
whose `category` is `skill`** — naming a real *agent* or *command* id in a skills table fails too.

Step 4's rule is checked as a second, independent assertion: for an implementation intent ending in
a done claim, `verification-before-completion` must appear under `### Mandatory` specifically, not
merely somewhere in the document.

## Pass condition
`fixture/recommendation.md` contains all four declared output-format headings
(`## Recommended skills for:`, `### Mandatory`, `### Suggested`, `### Next command`); contains at
least one table with the declared `| Skill | Why | Mandatory? |` header row; names at least one
skill; every name in a `| Skill |` column resolves to an entry in
`fixture/implementation/registry/index.json` whose `category` is `skill`; and
`verification-before-completion` appears in the `### Mandatory` section.

## Provenance
**Registry: real.** `fixture/implementation/registry/index.json` is a byte-identical copy of this
repository's own `implementation/registry/index.json` (79 entries: 28 `agent`, 19 `command`,
6 `instruction`, 26 `skill`), which is the exact file step 1 names.

**`recommendation.md` is hand-authored**, as the agent-side output under test. A corpus survey
(`grep -rl "## Recommended skills for:" . --include=*.md`) returned 11 matches, and every one of
them is either `implementation/knowledge/commands/discover-skills.md` itself or one of its 10
platform projections under `implementation/.{claude,gemini,github,opencode,pi}/` and the installed
`.{claude,gemini,github,opencode,pi}/` — i.e. every hit is the command's own declared *template*,
and **zero are produced output**. Excluding those paths leaves an empty result set: no real
`/discover-skills` output has ever been committed to this repository, so there was nothing real to
source this file from. That absence is documented rather than worked around, following
`new-feature-plan-doc-compliant/brief.md`'s precedent. The five skill names it cites were checked
against the registry at authoring time; the check re-derives that resolution from the registry file
itself rather than trusting the authoring-time survey.
