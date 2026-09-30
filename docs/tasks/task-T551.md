# T551 — The `memory-management` skill repeats `/consolidate-memory`'s data-loss instruction

**ID:** T551
**Owner:** Technical Writer
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** skill/memory-management
**Depends on:** T549
**Created:** 2026-09-30
**Based on:** `docs/plans/plan-082-root-refresh-and-followups.md` §3; `docs/tasks/task-T549.md`;
`implementation/knowledge/commands/consolidate-memory.md` (as amended by T549, MR !419).

## 1. The defect

T549 removed a data-loss instruction from `/consolidate-memory`: *append promoted content to
`AGENTS.md`, then remove it from memory.* In an installed target, `$TARGET/AGENTS.md` is regenerated
unconditionally on every install and every `--update` (`install.sh:434` →
`render_installed_agents.py:174`), so the promotion is destroyed and its source already deleted.

**`implementation/knowledge/skills/memory-management/SKILL.md` carries the identical instruction**,
at line 83:

> For promotions: Add to `AGENTS.md`, remove from MCP Memory.

It is not one line. The whole skill models `AGENTS.md` as **"Tier 2"** of a three-tier memory
hierarchy — `AGENTS.md` appears at lines 3, 26, 35, 54, 62, 78, 83, 94, 107, 112, 130, 149, 160, 171
and 175, including §4 "Promotion Rules" (line 94: *"An entry should be promoted from MCP Memory to
`AGENTS.md` when…"*) and §6 "Setting Up Memory for a New Project" (line 112: *"Create `AGENTS.md`
with:"*).

**After T549, the command and this skill contradict each other.** An agent that loads the skill is
told to do exactly what the command now forbids. That is the two-contracts-for-one-artifact defect
T527 closed for `/skillify`.

## 2. The question to answer — it is a design question, not a line fix

**What is "Tier 2" in a project where `AGENTS.md` is generated?**

T549 answered the equivalent question for the command, and its answer is now authoritative in
`develop`: promote into a **project-owned document under `docs/`**, which `install.sh` never deletes
under either install mode; never remove a memory entry until its content is confirmed in a durable
target; and never write promotions into the root `AGENTS.md`, `CLAUDE.md` or any platform folder.
Read the command's `## Promotion Targets` section before starting.

Decide, and argue:

1. **Is Tier 2 "project-owned docs under `docs/`"**, matching the command? Or does the skill need a
   different framing — for instance, distinguishing what the project *authors* from what the harness
   *renders*?
2. **What §6 "Setting Up Memory for a New Project" should say.** "Create `AGENTS.md`" is wrong in an
   emage-installed target, where `AGENTS.md` is generated. It may be right for a project that does
   *not* use this harness — but this skill ships into installed targets, so say which reader it
   addresses.
3. **Which document is authoritative for the promotion rule.** The precedent is T532: the `skillify`
   skill now states that `commands/skillify.md` is authoritative for its output-path rule and "must
   not diverge from it". Consider doing the same here, so the two cannot drift apart again.

## 3. Verified by the orchestrator — rely on these

- The skill is `maturity: experimental`. It **has no golden case** — no `case.yaml` under
  `tests/golden/` names `memory-management`. So this task gates no promotion and turns no case red.
- It projects to **seven** platforms, `.cline/` included (skills, unlike commands, do reach `.cline/`):
  `.claude .cline .cursor .gemini .github .opencode .pi`.
- `install.sh:468` copies `CLAUDE.md` with a plain `cp` and no `--update` guard, so `CLAUDE.md` is not a
  durable target either. T549 found this; it is the same trap.

## 4. Constraints

- **Write scope: `implementation/knowledge/skills/memory-management/SKILL.md` only.**
- **Do not edit `implementation/knowledge/commands/consolidate-memory.md`.** It is the authority
  here. If you find it wrong, report it.
- **Do not touch `AGENTS.md` or `implementation/AGENTS.md`.** The root one is generated from the
  other, and both are out of scope.
- **You have no Bash.** You cannot run a generator, validator, test or grep. Say so where a claim
  would need one. **Hand back uncommitted** — the orchestrator runs both generators
  (`node implementation/scripts/sync.mjs --root implementation`,
  `python3 implementation/scripts/generate-registry.py`) and every gate.
- **Root-drift gate.** Once T543's parity gate (MR !420) is in `develop`, every change under
  `implementation/knowledge/` that does not refresh the repo root must add the affected root paths to
  `tests/_baselines/root-install-drift.json` **in the same MR**, or the pipeline goes red. For this
  skill that is up to seven paths. **You cannot run the tool that computes them; the orchestrator
  will.** Do not edit that file.
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** No authorization.
- Do not move any ledger row. You may set `**Status:**` in this brief to `in_review`, nothing else.

## 5. Acceptance criteria

1. No text in the skill instructs removing a memory entry before its content is confirmed in a
   durable target.
2. No text directs promotions into the root `AGENTS.md`, `CLAUDE.md` or a platform folder.
3. §2's three questions answered, with the reasoning in your hand-back.
4. The skill and `/consolidate-memory` no longer contradict each other on any promotion rule.
5. Only the one file changed.

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. **If anything in this brief is wrong, report it rather than working
around it.** Thirteen consecutive tasks have found a defect in their brief; §1's line numbers and §3's
projection count are the likeliest places for the fourteenth.
