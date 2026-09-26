# T532 — Adjudicate `/skillify`'s declared output path

**ID:** T532
**Owner:** Solution Architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T531
**Created:** 2026-09-25
**Based on:** `docs/plans/plan-074-skillify-followups.md` §2;
`docs/artifacts/skillify-contract-resolution-v1.md` §5.5; `AGENTS.md` § Knowledge Base;
`docs/decisions/ADR-007-command-contract-authority.md`.

## 1. Owner has no shell — hand back uncommitted

`implementation/knowledge/agents/solution-architect.md` declares
`tools: [read, search, edit, web, todo, ...]` — **no `execute`**. Do not attempt or claim to run any
command. Write your files and **hand back uncommitted**; the orchestrator runs every gate and
commits, and will say publicly that it did. This is stated here rather than discovered at dispatch,
because three briefs in this phase got it wrong.

## 2. The defect

`implementation/knowledge/commands/skillify.md` declares its output at
`.github/skills/<name>/SKILL.md`. Two real problems:

1. **`AGENTS.md` § Knowledge Base states `.github/` is generated** by `scripts/sync.mjs` and must not
   be edited by hand. A `/skillify` output written there **in this repo** is destroyed by the next
   sync.
2. It **hardcodes one platform of seven** — the repo also projects to `.claude/`, `.cursor/`,
   `.gemini/`, `.opencode/`, `.pi/` and `.cline/`.

## 3. The question is not "which path"

The path is **correct for an installed target project**, where platform folders are the runtime
reference and there is no `implementation/knowledge/` source tree — and **wrong for this repo**,
where the source of truth is `implementation/knowledge/skills/`.

So the real question is: **does this command's contract address the authoring repo, the target
project, or both — and does it say so anywhere?** Survey the other commands: several are written for
target projects and several for this repo, and whether that distinction is declared or merely
assumed is the thing to establish. If it is undeclared across the board, that is a larger finding
than this one command and worth saying so.

`AGENTS.md` is a higher-authority document than a command file, so **`ADR-007` branch 1 may genuinely
fire here** — unlike in `T527`, where it did not. Check it properly rather than assuming either way.

## 4. Deliverables

1. `docs/artifacts/skillify-output-path-resolution-v1.md` — the adjudication, following
   `command-contract-resolution-v1.md`'s shape.
2. The execution, if your verdict amends `implementation/knowledge/commands/skillify.md`.
3. Set this brief's `**Status:**` to `in_review`. No ledger rows.

## 5. Scope boundary — `expect.py` is NOT yours

Resolving the path **changes the fixture glob in `expect.py`**, which is why this task depends on
`T531` and must not run beside it. **You hold no `tests/golden/**` authorization at all.** If your
verdict requires a checker change, **report it as a blocker with an exact spec** — exactly as `T527`
did for this same file — and it becomes a separate authorized task.

## 6. Blockers

Type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Max 2 retries. Never widen a grant — report instead.
