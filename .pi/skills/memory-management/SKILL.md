---
name: "memory-management"
description: "Manage the memory hierarchy: MCP Memory for runtime facts, project-owned documents under docs/ for promoted conventions and decisions, checkpoints for progress. Use when persisting important decisions, consolidating memory, or pruning stale entries."
---

# Memory Management

## Purpose

Manage the three-tier memory hierarchy to ensure important context is persisted at the right level, stale information is pruned, and agents can efficiently retrieve what they need.

## Who This Skill Addresses

This skill ships into every emage-installed project and also applies to the emage.code repository itself. In both, the root `AGENTS.md`, `CLAUDE.md` and the platform folders are **generated**, not authored: every install and every `install.sh --update` re-renders `AGENTS.md`, a Claude Code install copies `CLAUDE.md` over the existing one, and `--update` replaces the platform folders wholesale. None of them is a place to persist memory.

A project that does not use this harness and maintains its own `AGENTS.md` by hand is not the reader this skill addresses.

## Authority

`commands/consolidate-memory.md` — its § "Promotion Targets", step 5 and § "Important" — is authoritative for where promoted content goes and when a memory entry may be removed. This skill restates those rules for readers who reach it directly and must not diverge from them. If the two ever disagree, follow the command and report the disagreement.

## When to Use

- Persisting a key decision or architectural choice
- Consolidating scattered runtime notes into structured storage
- Promoting frequently referenced facts to higher-tier storage
- Pruning outdated or obsolete entries
- Setting up memory for a new project or phase

## Memory Tiers

| Tier | Storage | Scope | Lifetime | Content Type |
|------|---------|-------|----------|-------------|
| **Tier 1: MCP Memory** | MCP Memory tool (`/memories/`) | Runtime | Session or persistent | Runtime facts, quick notes, working state, temporary context |
| **Tier 2: Project documents** | Project-owned documents under `docs/` | Project | Permanent (version controlled; `install.sh` never deletes files under `docs/`) | Promoted project conventions, architectural decisions, recurring patterns |
| **Tier 3: Checkpoints** | `docs/checkpoints/` | Phase/session | Semi-permanent (compressed over time) | Progress state, completed work, active blockers, decision history |

### What Tier 2 Is — and Is Not

Tier 2 is content the project **authors**: a document under `docs/` that the project owns — an existing project document whose subject fits, or a new file. An architectural decision fits an ADR under `docs/decisions/` (`AGENTS.md` § Decision Log). Prefer a file the project created: a file the installer ships under `docs/` keeps local edits across `--update`, but a fresh `install.sh` run without `--update` overwrites it.

Tier 2 is **not** content the harness **renders**. Never promote into the root `AGENTS.md` or `CLAUDE.md`, or anything under `.claude/`, `.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/`, `.cline/` or `.clinerules/`, including the skill files there. A promotion written there is lost at the next update. Agents still *read* `AGENTS.md` for the harness's conventions (see § Memory Retrieval Strategy); they never write memory into it.

**In the emage.code repository itself**, promote into the root `docs/`, not `implementation/docs/`, which ships to every installed project. If an entry belongs in the shipped conventions (`implementation/AGENTS.md`) or in a shipped skill under `implementation/knowledge/`, do not edit those while managing memory: promote it to `docs/` and propose a separate task for the knowledge-base change.

A document under `docs/` is not loaded into agent context automatically. Name each promotion target wherever it will be needed — `/consolidate-memory` does so in its step 6 report.

### Tier Characteristics

```
MCP Memory (fast, volatile)
    │
    ▼  promote if frequently referenced — confirm the write before removing the entry
Project documents under docs/ (permanent, project-owned)
    │
    ▼  progress state captured periodically
Checkpoints (semi-permanent, compressed over time)
```

## Procedures

### 1. Persist a Key Decision

When a significant decision is made:

1. **Immediately:** Record in MCP Memory with tag `decision`:
   ```
   [decision] Use PostgreSQL over MongoDB for structured data — better relational support for the entity model.
   ```

2. **At next checkpoint:** Include in the "Key Decisions" section of the checkpoint.

3. **If the decision is a lasting convention:** Promote it to a Tier 2 document per § 3 and § 4 — an architectural decision fits an ADR under `docs/decisions/`.

### 2. Persist a Recurring Pattern

When a pattern is observed multiple times:

1. Record the first occurrence in MCP Memory.
2. On the second occurrence, flag it for promotion.
3. Promote it as a convention into a Tier 2 document (for example, a project-created `docs/conventions.md`) per § 3:
   ```markdown
   ## Conventions
   - All API endpoints return `{ data, error, meta }` envelope format
   ```

### 3. Consolidation Procedure

`/consolidate-memory` runs this procedure; the steps below restate it. Run consolidation periodically (every 2-3 checkpoints or when memory feels cluttered):

1. **Review MCP Memory entries.**
2. **Categorize each entry:**

   | Category | Action |
   |----------|--------|
   | **Keep** | Still relevant, still at the right tier |
   | **Promote** | Frequently referenced or broadly useful → write into a Tier 2 document |
   | **Demote** | Phase-specific → ensure captured in a checkpoint, then remove from MCP Memory |
   | **Prune** | Stale, obsolete, superseded, or duplicated → remove |

   `/consolidate-memory` uses three categories and presents a demotion as **Prune**: once its content is confirmed in a checkpoint, the entry is a duplicate.

3. **Present the recommendations and wait for user approval.** Never delete a memory entry without explicit user approval. For each Promote, name the proposed target file and section, so the user approves the destination together with the action.

4. **Execute the approved categorization:**
   - For promotions: Write the content into the approved target file, then re-read that file to confirm the content is present. Remove the entry from MCP Memory only if the target is a Tier 2 document (§ What Tier 2 Is — and Is Not) **and** the re-read confirms the write. Otherwise leave the entry in MCP Memory and report it as *promoted, retained*. If the user approved a target that is not Tier 2, explain why it is not durable and keep the memory entry.
   - For demotions: Verify captured in latest checkpoint, then remove from MCP Memory.
   - For prunes: Remove from MCP Memory.

5. **Record the consolidation**, naming each promotion target:
   ```
   [memory-consolidation] Reviewed N entries: K kept, P promoted (to <target files>), H promoted but retained, D demoted, R pruned.
   ```

### 4. Promotion Rules

An entry should be promoted from MCP Memory to a Tier 2 document when:

- It has been referenced 3+ times across different tasks or sessions
- It represents a project-wide convention or standard
- It is an architectural decision that affects multiple components
- It records how this project applies an agent role, responsibility, or workflow (the role definitions themselves ship with the harness and are not edited here)

Where the promoted content goes, and when the memory entry may be removed, is fixed by § What Tier 2 Is — and Is Not and § 3 step 4.

### 5. Pruning Rules

An entry should be pruned (removed) when:

- The information is no longer accurate (superseded by a newer decision)
- The task or context it relates to has been completed and archived
- It duplicates information already in a Tier 2 document, in `AGENTS.md`, or in a checkpoint
- It has not been referenced in 2+ checkpoints

### 6. Setting Up Memory for a New Project

For an emage-installed project — the reader this skill addresses:

1. **Do not create or edit `AGENTS.md`.** `install.sh` renders it with the harness's conventions and re-renders it on every install and every `--update`.

2. Create a project-owned document under `docs/` for the project's own context — for example `docs/conventions.md` — with:
   - Project overview
   - Initial project-specific conventions and standards
   - File structure overview

   This is the first Tier 2 document and the default promotion target. Agent roles and responsibilities are defined by the harness and read from `AGENTS.md`; architectural decisions go to `docs/decisions/` as ADRs.

3. Initialize MCP Memory with:
   - Current phase and objectives
   - Key context from project kickoff
   - The path of each Tier 2 document, since `docs/` is not loaded into agent context automatically

4. Create `docs/checkpoints/` directory.
5. Write `checkpoint-001-<phase>.md` as the initial state snapshot (`AGENTS.md` § Checkpoint Protocol: `checkpoint-<SEQ>-<phase>.md`).

## Memory Retrieval Strategy

When an agent needs context, search in this order:

1. **MCP Memory** — for current session context and recent decisions
2. **Tier 2 documents under `docs/`** — for the project's promoted conventions and decisions (ADRs under `docs/decisions/`)
3. **`AGENTS.md`** — for the harness's conventions, roles, and standards (read-only: rendered by `install.sh`)
4. **Latest checkpoint** — for recent progress and active state
5. **Older checkpoints** — for historical decisions and completed work (check compressed versions first)

## Examples

### Consolidation Session

Before consolidation (MCP Memory):
```
[decision] Use JWT for API auth
[note] Frontend prefers Tailwind CSS
[temp] Current branch: feature/auth
[decision] All errors use RFC 7807 format
[note] Frontend prefers Tailwind CSS  (duplicate)
[stale] Sprint 1 deadline is March 15  (past)
```

After consolidation, with the user's approval of each action and target:
- **Promoted to `docs/conventions.md`:** JWT for API auth, RFC 7807 error format, Tailwind CSS — each re-read and confirmed in the file before its memory entry was removed
- **Pruned:** Duplicate Tailwind note, stale sprint deadline
- **Kept:** Current branch note (still relevant)

### Promotion Example

MCP Memory entry referenced in T005, T008, and T012:
```
[convention] All service classes use constructor injection for dependencies
```

Promote to the approved Tier 2 document, for example `docs/conventions.md`:
```markdown
## Code Conventions
- All service classes use constructor dependency injection.
```

Re-read `docs/conventions.md` to confirm the entry is present. Only then remove it from MCP Memory. Had the user approved `AGENTS.md` as the target instead, explain that it is regenerated at the next install or `--update`, and keep the memory entry.

## Guidelines

- MCP Memory is for **working state**. Do not let it become a permanent archive.
- Tier 2 documents under `docs/` are the **source of truth** for the project's own conventions. Keep them curated.
- `AGENTS.md`, `CLAUDE.md` and the platform folders are **generated**. Read them; never write memory into them.
- Checkpoints are **snapshots**. They do not replace structured memory — they supplement it.
- Consolidate proactively. Cluttered memory slows down context retrieval.
- When in doubt about tier, start in MCP Memory. It's easy to promote; hard to un-promote.
- Never remove a memory entry until its content is confirmed in a Tier 2 document.
- Never delete from a Tier 2 document without consensus — it's version-controlled for a reason.
