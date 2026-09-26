---
description: "Capture the current workflow or a recurring pattern as a reusable skill file. Use when you discover a useful workflow that should be documented for reuse."
agent: "orchestrator"
argument-hint: "Describe the workflow to capture as a skill..."
---

You are in **Skillify mode**. Capture a workflow or recurring pattern as a reusable skill file.

## Instructions

### Round 1 — Trigger
Ask the user: *"When should this skill activate? What keywords, file patterns, or situations should trigger it?"*
Document the trigger conditions.

### Round 2 — Inputs
Ask the user: *"What inputs does this workflow need? (files, config values, user choices, context from other tools)"*
Document required and optional inputs.

### Round 3 — Steps
Ask the user: *"Walk me through the steps. What happens first, what decisions branch the flow, and what tools or commands are used?"*
Document the step-by-step procedure, including decision points and tool usage.

### Round 4 — Success Criteria
Ask the user: *"How do you know it worked? What does a successful outcome look like?"*
Document measurable success criteria and expected outputs.

### Choose the Output Path

**Check, do not assume.** This command ships both into the emage.code authoring repository and into
every project that installed emage.code, and the source of truth for a skill is not the same place
in the two. Test for the source tree first, then apply the one row that matches:

| If the project has… | Write the skill to | Then |
|---|---|---|
| `implementation/knowledge/skills/` — an emage.code **authoring** checkout | `implementation/knowledge/skills/<name>/SKILL.md` | Regenerate the derived trees: `node implementation/scripts/sync.mjs` **and** `python3 implementation/scripts/generate-registry.py --root implementation`. Do not hand-write any platform folder. |
| no `implementation/knowledge/` — an **installed target** project | `<platform>/skills/<name>/SKILL.md` in **every** installed platform folder that exists: `.github/`, `.claude/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/` | Tell the user, in the approval step below, that `scripts/install.sh --update` replaces each of those trees wholesale (`rsync -a --delete`, and the installer prints that warning itself), so the skill must be re-applied after an update or contributed upstream to survive one. |

This is **one rule with a precondition, not two acceptable output forms**: exactly one row applies to
any given project, decided by whether `implementation/knowledge/skills/` exists.

Two reasons the path is not a free choice:

- **In an authoring checkout the platform folders are derived, not authored.** `AGENTS.md`
  § Knowledge Base declares that "Source knowledge lives … under `implementation/knowledge/`" and
  that the per-platform folders are projections that must not be edited by hand.
  `implementation/scripts/sync.mjs` deletes each platform output directory before regenerating it,
  so a hand-written skill there is destroyed, never reaches the source tree or
  `implementation/registry/`, and never appears in the other six platforms.
- **In an installed target, one platform folder is not enough.** `AGENTS.md` § Skill Workflow
  requires agents to "check applicable skills in the active platform projection" and lists all seven
  folders. A skill written to only one of them is invisible to any agent running on the other six.
  Where a project installed a single platform, "every folder that exists" is that one folder.

### Generate the Skill File

After the 4-round interview, generate the `SKILL.md` at the path chosen above, with this structure.
Each interview round maps to one section: Round 1 → `## When to Use`, Round 2 → `## Inputs`,
Round 3 → `## Procedure`, Round 4 → `## Success Criteria`.

```markdown
---
name: <skill-name>
description: "<one-line description>"
---

# <Skill Name>

## When to Use
<when this skill activates>

## Inputs
<required and optional inputs>

## Procedure
<numbered procedure with decision points>

## Success Criteria
<how to verify successful completion>

## Examples
<one or two concrete usage examples>
```

### Present for Approval

Show the generated skill file to the user, **naming the exact path or paths chosen above and which
row of the table applied**. In an installed target project, state that row's durability warning too.
Apply changes only after explicit approval.

## Rails

**Inputs**: A description of the workflow or recurring pattern to capture (`{{input}}`), refined through the 4-round interview.
**Out of scope**: Applying the generated skill file without explicit user approval of the draft; hand-writing a skill into a platform projection folder (`.github/skills/`, `.claude/skills/`, …) of an emage.code authoring checkout, where `implementation/knowledge/skills/` is the source of truth.
**Failure mode**: If the user's answers in any interview round are too vague to produce a concrete trigger/steps/success-criteria, asks a follow-up rather than fabricating plausible-sounding but ungrounded content.

## Workflow to Capture

{{input}}
