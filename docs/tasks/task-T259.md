# Task T259 — W3-04 Create the `/validate-tasks` command (D18)

**ID:** T259
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T258
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 3 / W3-04

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task creates **EXACTLY ONE NEW FILE**:
  `implementation/knowledge/commands/validate-tasks.md`
- If that file already exists, STOP and report `PRECONDITION FAILED: T259`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(tasks): T259 add validate-tasks command`

## Action — create the file with EXACTLY this content

````markdown
---
description: "Validate task ledger integrity. Run before every checkpoint, before every release, and after every install --update."
agent: "orchestrator"
---

Run `python3 docs/tasks/validate-tasks.py` from the project root.

- Exit 0 → report "TASK LEDGER: PASS".
- Exit 1 → report every `FAIL C<n>` line verbatim, then propose one fix per
  violation. Do NOT auto-fix C5, C6, or C8 — ask the user which ledger is correct.

Run this command:
1. Before writing any checkpoint
2. Before `/prepare-release`
3. Immediately after `install.sh --update`
````

> Write the content **between** the outer ```` ```` ```` fences. Do not include the
> outer fences themselves in the file. The YAML frontmatter (`---` delimited) must be
> the first three-plus lines of the file.

## Expected outputs
- `implementation/knowledge/commands/validate-tasks.md` created.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   test -f implementation/knowledge/commands/validate-tasks.md && echo OK
   ```
   Expected output: `OK`
2. Verify command:
   ```bash
   head -1 implementation/knowledge/commands/validate-tasks.md
   ```
   Expected output: `---`
3. Verify command:
   ```bash
   grep -c "validate-tasks.py" implementation/knowledge/commands/validate-tasks.md
   ```
   Expected output: `1`
4. `git status --porcelain` lists exactly one new file.

## Revert rule
If any verify command fails:
```bash
rm -f implementation/knowledge/commands/validate-tasks.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Created `implementation/knowledge/commands/validate-tasks.md` with exact required
frontmatter and command guidance text.

Verification results:

```bash
$ test -f implementation/knowledge/commands/validate-tasks.md && echo OK
OK
$ head -1 implementation/knowledge/commands/validate-tasks.md
---
$ grep -c "validate-tasks.py" implementation/knowledge/commands/validate-tasks.md
1
$ git status --porcelain
?? implementation/knowledge/commands/validate-tasks.md
```

Outcome: PASS.
