# Case: skillify-skill-file-template-drift (known_failing / tracked_defect)

## Command under test
`/skillify`

## Brief (illustrative — not executed live)
"Capture the pre-completion verification gate we keep re-deriving as a reusable skill." The
4-round interview runs and a skill file is generated at the declared location.

## What this checks
`implementation/knowledge/commands/skillify.md` `## Instructions` → `### Generate the Skill File`
(immediately before `### Present for Approval`) and the `### Choose the Output Path` step it points
back to, verbatim as they read today, after `T527` amended the first and `T532` added the second:

> ### Choose the Output Path
>
> **Check, do not assume.** This command ships both into the emage.code authoring repository and into
> every project that installed emage.code, and the source of truth for a skill is not the same place
> in the two. Test for the source tree first, then apply the one row that matches:
>
> | If the project has… | Write the skill to | Then |
> |---|---|---|
> | `implementation/knowledge/skills/` — an emage.code **authoring** checkout | `implementation/knowledge/skills/<name>/SKILL.md` | Regenerate the derived trees … |
> | no `implementation/knowledge/` — an **installed target** project | `<platform>/skills/<name>/SKILL.md` in **every** installed platform folder that exists: `.github/`, `.claude/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/` | Tell the user, in the approval step below, that `scripts/install.sh --update` replaces each of those trees wholesale … |
>
> This is **one rule with a precondition, not two acceptable output forms**: exactly one row applies to
> any given project, decided by whether `implementation/knowledge/skills/` exists.
>
> …
>
> ### Generate the Skill File
>
> After the 4-round interview, generate the `SKILL.md` at the path chosen above, with this structure.
> Each interview round maps to one section: Round 1 → `## When to Use`, Round 2 → `## Inputs`,
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
section names and the level-1 title are unchanged. The amended template additionally declares YAML
frontmatter (`name`, `description`); `expect.py` does not assert the frontmatter, so the checked
surface is the declared output location, the level-1 title and the five `##` sections.

`T532` then changed the output location and nothing else. Until then the step read "generate
`.github/skills/<name>/SKILL.md` with this structure" — one hardcoded path. It now points to
`### Choose the Output Path`, whose two rows are mutually exclusive by a checkable predicate
(`docs/artifacts/skillify-output-path-resolution-v1.md` §4.4). No section name moved, so the case's
failure cause did not move either (§5.2 there). This is `ADR-007`'s sibling-fate corollary, row 1,
applied literally: the amendment changes only a path, so the case survives and its glob is widened
(`T548`).

**The fixture exercises the installed-target row.** It has no `implementation/knowledge/`, so the
precondition selects the second row, and `.github/` is the only platform folder in it, so "every
installed platform folder that exists" is that one folder — the single-platform degenerate case
§4.4 property 3 describes.

These are the command's only structurally checkable clauses — Rounds 1–4 are an interactive
interview whose outputs are prose, and `### Present for Approval` is a human interaction. The
generated file's declared location and declared section list are what `/skillify` commits to
producing as a file, so they are what this case asserts. The follow-through each row declares
(regenerating the derived trees; warning the user about `install.sh --update`) is an action or a
message, not a file shape, and is not asserted.

## Pass condition
Over the eight declared skill directories under `fixture/` — `implementation/knowledge/skills/`,
and `<platform>/skills/` for `.github`, `.claude`, `.cursor`, `.gemini`, `.opencode`, `.pi`,
`.cline` — all of the following hold:

- at least one of them exists;
- **no single directory** holds more than one `<name>/SKILL.md` (two skills in one directory leave
  it ambiguous which the run generated);
- **at least one** `SKILL.md` resolves across the whole set; and
- **every** `SKILL.md` that resolves contains a level-1 title plus all five declared `##` sections:
  `## When to Use`, `## Inputs`, `## Procedure`, `## Success Criteria`, `## Examples`.

`expect.py` was re-derived against the amended template at `T531`; its discovery was widened from
`fixture/.github/skills/` alone to the declared set at `T548`, taking option (i) of
`skillify-output-path-resolution-v1.md` §7. Option (ii) — relocate the fixture to the authoring
row — would have moved a file under `fixture/`, which `T548` was not authorized to do.

**Uniqueness is per directory, not across the set — a revision made in `T548`'s own review.** The
first version applied §7's "exactly one candidate across the whole set" literally. That rejected a
*correct* installed-target output for any project with two or more platform folders, because the
second row requires the skill in **every** installed platform folder that exists: the checker would
have contradicted the contract it checks. The orchestrator overruled it. Uniqueness now applies
within each directory, where a second skill really is ambiguous, and every copy found must conform,
so a correct copy in one platform folder cannot mask a non-conforming one in another. Two things are
deliberately **not** asserted across directories: that the copies are byte-identical, and that they
share one `<name>`. The command says to write "the skill" to each folder but declares neither
property, and asserting either would add an element §7 does not specify.

**Why the widening is not a relaxation, stated precisely.** It is not true that the wider search
admits only fewer fixtures than before: a conforming `SKILL.md` placed only under
`.claude/skills/` or only under `implementation/knowledge/skills/` now resolves, where it did not.
What makes that legitimate under `ADR-007` §5 is that every newly admitted location is one the
amended contract declares — nothing undeclared resolves (`docs/skills/`, or `sync.mjs`'s
`implementation/.<platform>/skills/` output, still do not) — and the five section assertions, which
are this case's failure cause, are byte-identical and now apply to **every** copy rather than to
the single file the old guard admitted. Compared with the pre-`T548` checker, the result is:

- **Accepted that was rejected before:** only locations the amended contract declares — a
  conforming skill only under `.claude/skills/` or only under `implementation/knowledge/skills/`.
- **Rejected that was accepted before:** a conforming `.github/skills/` copy next to a
  non-conforming copy in another declared directory.
- **Unchanged:** the same skill in several platform folders is still accepted, two skills in one
  directory are still rejected, and undeclared locations (`docs/skills/`, or `sync.mjs`'s
  `implementation/.<platform>/skills/` output) still resolve nothing.

§7's out-of-scope row forbids asserting that the skill exists in all seven folders, and that is not
asserted.

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
`.github/skills/*/SKILL.md`, which was then the exact directory `/skillify` declared it writes to
(since `T532`, one directory of its declared set) — returning identically for both trees:

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
tree, placed at the same repo-relative path. When the case was authored that path was the command's
single declared output location; since `T532` it is the installed-target row's path for a project
whose only platform folder is `.github/`, and the fixture was not moved.

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
