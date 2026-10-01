---
description: "List and recommend skills from the repository's skills tree for the current task or intent."
agent: "orchestrator"
argument-hint: "Task intent, e.g. 'debug CI failure' or 'prepare release'..."
maturity: stable
---

You are in **Skill Discovery** mode. Match the user's intent to canonical skills.

## Instructions

1. **Enumerate skills** — a skill is a directory holding a `SKILL.md`. Where they live depends on whether `implementation/registry/index.json` exists:

   | `implementation/registry/index.json` | You are in | Enumerate skills from |
   |--------------------------------------|------------|-----------------------|
   | exists | the emage.code authoring repository | `implementation/knowledge/skills/*/SKILL.md`. The registry's `category: skill` entries index this same tree and may be read instead, as an accelerator (`implementation/registry/summary.md` for an overview); where the two disagree, the tree wins. |
   | does not exist | an installed target project | `.<platform>/skills/*/SKILL.md` — the active platform projection (`.claude`, `.cline`, `.cursor`, `.gemini`, `.github`, `.opencode` or `.pi`). Targets have no registry; do not look for one. |

   Test for the registry file itself, never for `implementation/` — the installer creates `implementation/runtime/` in target projects too. Recommend only skills this step enumerated.
2. **Parse intent** — from `{{input}}` or active task brief; identify phase (plan, implement, debug, review, release).
3. **Recommend skills** — return a ranked table:

| Skill | Why | Mandatory? |
|-------|-----|------------|
| ... | one-line rationale | yes/no |

4. **Apply mandatory rules** from `AGENTS.md` Skill Workflow:
   - Implementation → `verification-before-completion` before done claims
   - Bugs/tests → `systematic-debugging` before fixes
   - Review feedback → `receiving-code-review` before edits
   - Phase transitions → relevant gate skill (`validation-gates`, `checkpoint-protocol`)
5. **Offer invocation** — tell the user which skill file to load or which slash command to run next.
6. **Optional packaging** — if a skill pack is installed (`packs/installed/`), merge pack registry entries into recommendations.

## Output format

```markdown
## Recommended skills for: <intent>

### Mandatory
- ...

### Suggested
- ...

### Next command
`/...` or load the `<name>` skill
```

## Rails

**Inputs**: The skills tree step 1 selects — `implementation/knowledge/skills/*/SKILL.md` where `implementation/registry/index.json` exists (that registry and `implementation/registry/summary.md` as optional accelerators), otherwise `.<platform>/skills/*/SKILL.md` — and the user's task intent (`{{input}}` or the active task brief).
**Out of scope**: Modifying any skill or registry file — this command only recommends and points to existing skill files/commands.
**Failure mode**: If no skill matches the stated intent well, says so explicitly rather than recommending a poorly-fitting skill just to return a non-empty table.
