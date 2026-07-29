# Task T274 — W7-02 Fix priority vocabulary in technical-debt-tracking (D3)

**ID:** T274
**Owner:** technical-writer
**Status:** done
**Priority:** P2
**Depends on:** T273
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 7 / W7-02

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T274`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T274 use P0 priority vocabulary in debt tracking`

## Objective
The debt-tracking skill tells agents to create a task "with priority `must`". The only
valid priority values are `P0`, `P1`, `P2`.

## Edit — replace one token in one line

FIND (exact substring, currently on line 105):
```
with priority `must`
```

REPLACE WITH (exact):
```
with priority `P0`
```

Leave the rest of that table row unchanged (`| \`must_fix_pre_prod\` | Create task in
\`docs/tasks/active-tasks.md\` … and target sprint = current or next |`).

## Expected outputs
- `implementation/knowledge/skills/technical-debt-tracking/SKILL.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "priority \`must\`" implementation/knowledge/skills/technical-debt-tracking/SKILL.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "with priority \`P0\`" implementation/knowledge/skills/technical-debt-tracking/SKILL.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
```bash
git checkout -- implementation/knowledge/skills/technical-debt-tracking/SKILL.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Replaced `must` priority vocabulary with `P0` in `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`.
Committed with exact message `fix(tasks): T274 use P0 priority vocabulary in debt tracking`.
Ran `make sync` and committed updated projections.

