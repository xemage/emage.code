---
description: "Review MCP Memory entries, prune stale items, and promote valuable items into durable project documents under docs/. Use periodically to keep memory clean and relevant."
agent: "orchestrator"
argument-hint: "Optional: focus area or category to consolidate..."
maturity: stable
audience: both
---

You are in **Memory Consolidation mode**. Review, organize, and clean up MCP Memory entries to keep the project knowledge base accurate and lean.

## Instructions

1. **Read all MCP Memory entries** — use `mcp__memory` to retrieve the full set of stored memories. If a focus area is provided, filter to that category.
2. **Categorize each entry** — assign one of:
   - **Keep** — still relevant, correctly scoped, leave in memory
   - **Promote** — frequently referenced or broadly useful; should be written into a durable project document (see **Promotion Targets** below)
   - **Prune** — stale, obsolete, superseded, or duplicated; safe to remove
3. **Present recommendations** — show a table with:
   - Memory key/identifier
   - Current content summary (one line)
   - Recommended action (Keep / Promote / Prune)
   - Rationale (why this action)
4. **Wait for user approval** — do NOT execute changes until the user confirms which recommendations to apply. For each Promote, name the proposed target file and section (see **Promotion Targets**) below the table, not as a table column, so the user approves the destination together with the action.
5. **Execute approved changes**:
   - **Promote**: write the content into the approved target file, then re-read that file to confirm the content is present. Remove the entry from memory only if the target is a durable promotion target (see **Promotion Targets**) **and** the re-read confirms the write. Otherwise leave the entry in memory and report it as *promoted, retained*.
   - **Prune**: delete the memory entry
   - **Keep**: no action needed
6. **Report results** — summarize what was promoted (with each target file), promoted but retained (with the reason), pruned, and kept. Note the new memory entry count.

## Promotion Targets

A promotion target must be a file that no generator or installer rewrites, so the promoted content outlives the memory entry it replaces.

- **Use** a document under `docs/` that the project owns — an existing project document whose subject fits, or a new file. `install.sh` never deletes files under `docs/`, and never overwrites one it does not ship itself. Prefer a file the project created: a file the installer ships under `docs/` keeps local edits across `--update`, but a fresh `install.sh` run without `--update` overwrites it.
- **Never use** the root `AGENTS.md` or `CLAUDE.md`, or anything under `.claude/`, `.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/`, `.cline/` or `.clinerules/`, including the skill files there. They are generated: every install and every `install.sh --update` re-renders `AGENTS.md`, a Claude Code install copies `CLAUDE.md` over the existing one, and `--update` replaces the platform folders wholesale. A promotion written there is lost at the next update.
- **In the emage.code repository itself**, the root `AGENTS.md` and the platform folders are generated as well. Promote into the root `docs/`, not `implementation/docs/`, which ships to every installed project. If an entry belongs in the shipped conventions (`implementation/AGENTS.md`) or in a shipped skill under `implementation/knowledge/`, do not edit those from this command. Promote it to `docs/` as above, and propose a separate task for the knowledge-base change.
- A document under `docs/` is not loaded into agent context automatically. Name each target file in the step 6 report so it can be referenced where it is needed.

## Important

- Never delete a memory entry without explicit user approval.
- Never remove a promoted entry from memory until its content is confirmed in a durable promotion target. If the user approves a target listed under **Never use**, explain why it is not durable and keep the memory entry.
- When promoting, place the content in the most relevant section of the target document and format it consistently with the existing entries there.
- If you find contradictory memories, flag them for user resolution rather than choosing one silently.

## Rails

**Inputs**: The current MCP Memory entries and an optional focus area/category (`{{input}}`).
**Out of scope**: Deleting or promoting any memory entry without explicit user approval of the presented recommendation table; writing promotions into generated files (the root `AGENTS.md`, `CLAUDE.md`, or the platform folders) or into shipped knowledge-base source.
**Failure mode**: If two memories contradict each other, flags them for user resolution rather than silently choosing one. If a promotion cannot be confirmed in a durable target, the memory entry is retained and reported as *promoted, retained*, never deleted.

## Focus Area

{{input}}
