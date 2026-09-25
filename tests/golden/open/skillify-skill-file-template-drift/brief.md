# Case: skillify-skill-file-template-drift (known_failing / tracked_defect)

## Command under test
`/skillify`

## Brief (illustrative — not executed live)
"Capture the pre-completion verification gate we keep re-deriving as a reusable skill." The
4-round interview runs and a skill file is generated at the declared location.

## What this checks
`implementation/knowledge/commands/skillify.md` `## Instructions` → `### Generate the Skill File`
(the step immediately after Round 4 and immediately before `### Present for Approval`), verbatim:

> ### Generate the Skill File
>
> After the 4-round interview, generate `.github/skills/<name>/SKILL.md` with this structure:
>
> ```markdown
> # <Skill Name>
>
> ## Trigger
> <when this skill activates>
>
> ## Inputs
> <required and optional inputs>
>
> ## Steps
> <numbered procedure with decision points>
>
> ## Success Criteria
> <how to verify successful completion>
>
> ## Examples
> <one or two concrete usage examples>
> ```

This is the command's only structurally checkable clause — Rounds 1–4 are an interactive
interview whose outputs are prose, and `### Present for Approval` is a human interaction. The
generated file's declared path and declared section list are the whole of what `/skillify` commits
to producing, so they are what this case asserts.

## Pass condition
Exactly one `SKILL.md` exists under `fixture/.github/skills/<name>/` (the declared path), and it
contains a level-1 title plus all five declared `##` sections: `## Trigger`, `## Inputs`,
`## Steps`, `## Success Criteria`, `## Examples`.

## Why this is known_failing today
The fixture is a real, representative skill file — `.github/skills/verification-before-completion/
SKILL.md`, copied byte-identically — and it satisfies **none** of `## Trigger`, `## Inputs` or
`## Steps`. Its actual sections are `## Rails`, `## Purpose`, `## When to Use`, `## Iron Rule`,
`## Gate Procedure`, `## Claim → Evidence Map`, `## Red Flags — Stop`, `## emage.code Standard
Commands`, `## Orchestrator Enforcement`.

This is not one stray file. A corpus survey across **every** real skill file in this repository —
the 26 sources under `implementation/knowledge/skills/*/SKILL.md` and the same 26 as projected to
`.github/skills/*/SKILL.md`, which is the exact directory `/skillify` declares it writes to —
returns, identically for both trees:

| Declared section | Files containing it |
|---|---|
| `## Trigger` | 0 / 26 |
| `## Inputs` | 0 / 26 |
| `## Steps` | 0 / 26 |
| `## Success Criteria` | 3 / 26 |
| `## Examples` | 9 / 26 |
| **all five together** | **0 / 26** |

The corpus is not unstructured; it is uniformly structured to a *different* template — `## Purpose`,
`## When to Use`, `## Prerequisites`, `## Procedure`, `## Examples`, `## Edge Cases`. That template
is itself declared, in `implementation/knowledge/skills/skillify/SKILL.md`'s `## SKILL.md Template`
section. **The `/skillify` command and the `skillify` skill declare two different output shapes for
the same artifact, and every skill file in the repository follows the skill's, not the command's.**

No fixture was selected to manufacture this result: the survey shows every available real file
fails this check, so no choice of real fixture could have made the case green. Choosing a
hand-authored fixture in the command's declared shape instead *would* have made it green — and
would have asserted a structure with zero instances in the corpus it claims to describe. Per
`ADR-007` §5, the check is not relaxed to reach a pass.

## Category
`tracked_defect`, not `capability_gap`. Nothing prevents a conforming file from being written; two
declared contracts simply disagree, and the disagreement is mechanically resolvable in either
direction — amend `skillify.md` to the corpus/skill template, or migrate the corpus to the
command's. It needs an `ADR-007` adjudication of which document holds authority, which is exactly
what a tracked defect is for. Resolving this case by editing either
`implementation/knowledge/commands/skillify.md` or the fixture is explicitly **out of scope** for
the task that authored it (`T525` §1).

## Provenance
**Fully real.** `fixture/.github/skills/verification-before-completion/SKILL.md` is a byte-identical
copy of `.github/skills/verification-before-completion/SKILL.md` from this repository's working
tree, placed at the same repo-relative path the command declares as its output location. The survey
table above is reproducible with:

```
python3 - <<'PY'
from pathlib import Path
req = ["## Trigger", "## Inputs", "## Steps", "## Success Criteria", "## Examples"]
for root in ["implementation/knowledge/skills", ".github/skills"]:
    files = sorted(Path(root).glob("*/SKILL.md"))
    for h in req:
        print(root, h, sum(1 for f in files if h in f.read_text()), "/", len(files))
    print(root, "ALL FIVE",
          sum(1 for f in files if all(h in f.read_text() for h in req)), "/", len(files))
PY
```
