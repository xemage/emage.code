# Case: skillify-skill-file-template-drift (known_failing / tracked_defect)

## Command under test
`/skillify`

## Brief (illustrative — not executed live)
"Capture the pre-completion verification gate we keep re-deriving as a reusable skill." The
4-round interview runs and a skill file is generated at the declared location.

## What this checks
`implementation/knowledge/commands/skillify.md` `## Instructions` → `### Generate the Skill File`
(the step immediately after Round 4 and immediately before `### Present for Approval`), verbatim as
that step reads today, after `T527` amended it:

> ### Generate the Skill File
>
> After the 4-round interview, generate `.github/skills/<name>/SKILL.md` with this structure. Each
> interview round maps to one section: Round 1 → `## When to Use`, Round 2 → `## Inputs`,
> Round 3 → `## Procedure`, Round 4 → `## Success Criteria`.
>
> ```markdown
> ---
> name: <skill-name>
> description: "<one-line description>"
> ---
>
> # <Skill Name>
>
> ## When to Use
> <when this skill activates>
>
> ## Inputs
> <required and optional inputs>
>
> ## Procedure
> <numbered procedure with decision points>
>
> ## Success Criteria
> <how to verify successful completion>
>
> ## Examples
> <one or two concrete usage examples>
> ```

`T527` renamed two of these sections: the step previously declared `## Trigger` where it now
declares `## When to Use`, and `## Steps` where it now declares `## Procedure`. The other three
section names, the declared output path, and the level-1 title are unchanged. The amended template
additionally declares YAML frontmatter (`name`, `description`); `expect.py` does not assert the
frontmatter, so the checked surface is the declared path, the level-1 title and the five `##`
sections.

This is the command's only structurally checkable clause — Rounds 1–4 are an interactive
interview whose outputs are prose, and `### Present for Approval` is a human interaction. The
generated file's declared path and declared section list are the whole of what `/skillify` commits
to producing, so they are what this case asserts.

## Pass condition
Exactly one `SKILL.md` exists under `fixture/.github/skills/<name>/` (the declared path), and it
contains a level-1 title plus all five declared `##` sections: `## When to Use`, `## Inputs`,
`## Procedure`, `## Success Criteria`, `## Examples`. `expect.py` was re-derived against the
amended template at `T531`.

## Why this is known_failing today
The fixture is a real, representative skill file — `.github/skills/verification-before-completion/
SKILL.md`, copied byte-identically — and it satisfies **1 of the 5** declared sections. It has
`## When to Use`. It has no `## Inputs`, no `## Procedure`, no `## Success Criteria` and no
`## Examples` section — `## Gate Procedure` is a different heading, and the `**Inputs**:` label
inside `## Rails` is bold body text, not a heading. Its actual sections are `## Rails`,
`## Purpose`, `## When to Use`, `## Iron Rule`, `## Gate Procedure`, `## Claim → Evidence Map`,
`## Red Flags — Stop`, `## emage.code Standard Commands`, `## Orchestrator Enforcement`.

This is not one stray file.

### Corpus measurement after T527
Per `T527`'s fence-aware measurement (headings appearing inside fenced code blocks are not counted
as declared sections) across the 26 real skill files under
`implementation/knowledge/skills/*/SKILL.md`: **0 of 26** satisfy the command's amended template,
and **0 of 26** satisfy the template declared by the `skillify` *skill*
(`implementation/knowledge/skills/skillify/SKILL.md`, `## SKILL.md Template`). The corpus follows
**neither** declared template.

### Historical record — the survey taken when this case was authored (T525)
Retained as real evidence of the corpus's shape. Two caveats apply to reading it against the
current contract: it was measured with a naive substring test rather than the fence-aware method
above, and it was measured against the section names the command declared **before** `T527`.

Surveyed across **every** real skill file in this repository — the 26 sources under
`implementation/knowledge/skills/*/SKILL.md` and the same 26 as projected to
`.github/skills/*/SKILL.md`, which is the exact directory `/skillify` declares it writes to —
returning identically for both trees:

| Section as declared pre-`T527` | Files containing it |
|---|---|
| `## Trigger` — renamed to `## When to Use` by `T527` | 0 / 26 |
| `## Inputs` — name unchanged by `T527` | 0 / 26 |
| `## Steps` — renamed to `## Procedure` by `T527` | 0 / 26 |
| `## Success Criteria` — name unchanged by `T527` | 3 / 26 |
| `## Examples` — name unchanged by `T527` | 9 / 26 |
| **all five together** | **0 / 26** |

The first and third rows measure names the command no longer declares; they are kept as the record
of the pre-`T527` state, not as a measurement of the current template. The three unchanged rows
still name currently-declared sections, subject to the substring-vs-fence-aware caveat above.

No fixture was selected to manufacture this result. Every available real file fails this check —
0 of 26 under either declared template — so no choice of real fixture could have made the case
green. Choosing a hand-authored fixture in the declared shape instead *would* have made it green,
and would have asserted a structure with zero instances in the corpus it claims to describe. Per
`ADR-007` §5, the check is not relaxed to reach a pass.

## Category
`tracked_defect`, not `capability_gap`. Nothing prevents a conforming file from being written.

This case was originally framed as two *declared contracts* disagreeing — the command and the
`skillify` skill naming different output shapes for the same artifact. **After `T527` that framing
no longer holds:** the command's five sections are now a subset of the skill's
`## SKILL.md Template`, in the same relative order (the skill declares `## Purpose`,
`## When to Use`, `## Inputs`, `## Required Context`, `## Procedure`, `## Success Criteria`,
`## Examples`, `## Edge Cases`, `## Guidelines`; the command's five appear within that sequence, in
order). A file conforming to the skill's template satisfies the command's template as well.

What remains is drift between the declared template and the corpus, not between two declarations:
0 of 26 real skill files satisfy either. It is mechanically resolvable in either direction —
migrate the corpus to the declared template, or amend the declared template to the corpus's actual
shape — and needs an adjudication of which side holds authority, which is exactly what a tracked
defect is for. Resolving this case by editing
`implementation/knowledge/commands/skillify.md` or the fixture was explicitly **out of scope** for
the task that authored it (`T525` §1) and remains out of scope for the prose corrections at `T530`.

## Provenance
**Fully real.** `fixture/.github/skills/verification-before-completion/SKILL.md` is a byte-identical
copy of `.github/skills/verification-before-completion/SKILL.md` from this repository's working
tree, placed at the same repo-relative path the command declares as its output location.

The historical survey table above is reproducible with the naive substring method that produced it.
`PRE_T527` reproduces the table as recorded; `CURRENT` applies the same method to the section names
the command declares today:

```
python3 - <<'PY'
from pathlib import Path
PRE_T527 = ["## Trigger", "## Inputs", "## Steps", "## Success Criteria", "## Examples"]
CURRENT  = ["## When to Use", "## Inputs", "## Procedure", "## Success Criteria", "## Examples"]
for label, req in [("PRE_T527", PRE_T527), ("CURRENT", CURRENT)]:
    for root in ["implementation/knowledge/skills", ".github/skills"]:
        files = sorted(Path(root).glob("*/SKILL.md"))
        for h in req:
            print(label, root, h, sum(1 for f in files if h in f.read_text()), "/", len(files))
        print(label, root, "ALL FIVE",
              sum(1 for f in files if all(h in f.read_text() for h in req)), "/", len(files))
PY
```

Note that this snippet counts headings that occur inside fenced code blocks — including the template
blocks inside `skillify`'s own skill file — so its per-section counts are upper bounds relative to
the fence-aware measurement reported under "Corpus measurement after T527".
