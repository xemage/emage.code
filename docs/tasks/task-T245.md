# Task T245 — W1-02 Replace the invented table schema with the real one (D2, D3, D5)

**ID:** T245
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T244
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 1 / W1-02

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/skills/task-management/SKILL.md`
- **R5** If the section boundaries below are not found, STOP and report
  `PRECONDITION FAILED: T245`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T245 replace task table schema with real 7/5 column format`

## Objective
The skill teaches a fabricated 8-column schema with `TASK-NNN` IDs, `Blocks`/`BlockedBy`
columns, and `critical/high/medium/low` priorities. None of that exists in the real
ledgers. Replace the section with the actual schema.

## Edit — replace one whole section

DELETE everything from the line:
```
## Task Table Format
```
down to **but NOT including** the line:
```
## Status Lifecycle
```

(This removes the `## Task Table Format` heading, the fake markdown table, the
`### Field Definitions` sub-section, and its table.)

INSERT in its place, **exactly** this content:

````markdown
## Task Table Format

### active-tasks.md — 7 columns, in this exact order
| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T042 | Add rate limiting | backend-developer | in_progress | P1 | T040 | 2026-07-27 |

### completed-tasks.md — 5 columns, in this exact order
| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
| T042 | Add rate limiting | backend-developer | 2026-07-27 | src/mw/ratelimit.ts; docs/tasks/task-T042.md |

### Field rules
| Field | Rule |
|-------|------|
| ID | `T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `TASK-001`. NEVER `BUG-7`. |
| Owner | Exact agent slug, kebab-case, from the installed agents folder. |
| Status | `pending` \| `in_progress` \| `blocked` \| `in_review` \| `done` \| `cancelled` |
| Priority | `P0` \| `P1` \| `P2`. NEVER `critical`/`high`/`medium`/`low`. |
| Depends on | Comma-separated task IDs, or `—` |
| Last update / Done on | `YYYY-MM-DD`, a real date |

### Field mapping when archiving
| active column | goes to |
|---------------|---------|
| ID, Title, Owner | copied as-is |
| Status | DROPPED (implied `done`) |
| Priority | DROPPED |
| Depends on | DROPPED |
| Last update | becomes `Done on` |
| — | new `Outcome / artifact`: semicolon-separated paths, MUST include `docs/tasks/task-<ID>.md` |
````

Keep exactly one blank line before `## Status Lifecycle`.

## Expected outputs
- `implementation/knowledge/skills/task-management/SKILL.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "TASK-00" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `0`
   > Note: if this is still non-zero because of the `## Examples` section further down,
   > that is handled by T246/T273 — but this task must at minimum remove every
   > `TASK-00` occurrence **inside the section you replaced**. If matches remain
   > outside that section, record their line numbers in Execution notes and continue.
2. Verify command:
   ```bash
   grep -c "BlockedBy" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output must be **lower** than before the edit; record both numbers.
3. Verify command:
   ```bash
   grep -c "Last update / Done on" implementation/knowledge/skills/task-management/SKILL.md
   ```
   Expected output: `1`
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/skills/task-management/SKILL.md
```
then STOP and report. **Warning:** this also reverts T244. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Replaced the entire section from `## Task Table Format` up to (but excluding)
`## Status Lifecycle` with the canonical 7/5-column schema and field mapping,
exactly as specified.

Verification evidence:

```bash
pre_TASK00=1
pre_BlockedBy=7
pre_LastUpdateDoneOn=0

post_TASK00=1
post_BlockedBy=5
post_LastUpdateDoneOn=1
```

Residual `TASK-00` occurrence after edit:

```bash
$ grep -n 'TASK-00' implementation/knowledge/skills/task-management/SKILL.md
47:| ID | `T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `TASK-001`. NEVER `BUG-7`. |
```

This residual is from the exact replacement text required by the task itself.

Outcome: PASS.
