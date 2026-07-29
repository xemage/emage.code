# Task T256 — W3-01 Create the task brief template (D13)

**ID:** T256
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Depends on:** T255
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 3 / W3-01

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task creates **EXACTLY ONE NEW FILE**:
  `implementation/docs/tasks/_template.md`
- If that file already exists, STOP and report `PRECONDITION FAILED: T256`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `feat(tasks): T256 add task brief template for target projects`

## Why this matters (do not skip)
`docs/tasks/` is the only shipped docs folder without a `_template.md`. `plans/`,
`checkpoints/`, `artifacts/`, and `decisions/` all have one. Without it, every target
project improvises its own brief structure.

## Action — create the file with EXACTLY this content

````markdown
# Task <ID> — <Title>

**ID:** T<NNN>
**Owner:** <agent-slug>
**Status:** pending
**Priority:** P0 | P1 | P2
**Depends on:** <IDs or —>
**Created:** YYYY-MM-DD
**Completed:** —
**Based on:** docs/plans/plan-<NNN>-<slug>.md

## Objective
<one paragraph>

## Inputs
- <artifact-vN.md paths>

## Expected outputs
- <artifact paths this task must produce>

## Acceptance criteria
1. <specific, testable>

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Created `implementation/docs/tasks/_template.md` with the exact required content.

Verification results:

```bash
$ test -f implementation/docs/tasks/_template.md && echo OK
OK
$ head -1 implementation/docs/tasks/_template.md
# Task <ID> — <Title>
$ git status --porcelain
?? implementation/docs/tasks/_template.md
```

Outcome: PASS.
````

> Write the content **between** the outer ```` ```` ```` fences. Do not include the
> outer fences themselves in the file.

## Expected outputs
- `implementation/docs/tasks/_template.md` created.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   test -f implementation/docs/tasks/_template.md && echo OK
   ```
   Expected output: `OK`
2. Verify command:
   ```bash
   head -1 implementation/docs/tasks/_template.md
   ```
   Expected output: `# Task <ID> — <Title>`
3. `git status --porcelain` lists exactly one new untracked/added file.

## Revert rule
If any verify command fails:
```bash
rm -f implementation/docs/tasks/_template.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
