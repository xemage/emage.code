# Task T273 — W7-01 Find and fix every stale `TASK-NNN` reference (D2)

**ID:** T273
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T272
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 7 / W7-01

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
  Only `implementation/knowledge/**` is canonical.
- **ONE FILE PER COMMIT.** Do not batch multiple files into one commit.
- Replace **only** the ID token. Do not rewrite surrounding prose.
- **R6** Do NOT run `make sync` between files. Run it once, at the end.
- Do NOT run `git push`.
- **R7** Commit message per file, exactly:
  `fix(tasks): T273 use T<NNN> ids in <filename>`

## Step 1 — enumerate
```bash
grep -rn "TASK-[0-9N]" implementation/knowledge/
```
Record the full list in `## Execution notes` **before** editing anything.

## Step 2 — replace, one file at a time
For each hit apply the token replacement:

| FIND | REPLACE |
|------|---------|
| `TASK-001` | `T001` |
| `TASK-002` | `T002` |
| `TASK-003` | `T003` |
| `TASK-012` | `T012` |
| `TASK-NNN` | `T<NNN>` |
| `TASK-<any 3 digits>` | `T<same 3 digits>` |

Known affected files (verify with Step 1; the list may differ):
- `implementation/knowledge/skills/gitlab-management/SKILL.md`
- `implementation/knowledge/skills/release-workflow/SKILL.md`
- `implementation/knowledge/skills/code-review/SKILL.md`
- `implementation/knowledge/skills/testing-strategy/SKILL.md`
- `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`
- `implementation/knowledge/skills/task-management/SKILL.md` (the `## Examples` section)
- `implementation/knowledge/commands/prepare-release.md`
- `implementation/knowledge/commands/handoff.md`
- `implementation/knowledge/commands/batch.md`
- `implementation/knowledge/commands/new-feature.md`

After **each** file:
```bash
grep -c "TASK-[0-9N]" <that file>
```
Expected output: `0`. Then commit that one file.

## Expected outputs
- One commit per modified file under `implementation/knowledge/`.
- Nothing outside `implementation/knowledge/` changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -rc "TASK-[0-9N]" implementation/knowledge/ | grep -v ":0"
   ```
   Expected: **no output**.
2. Verify command:
   ```bash
   make sync && make verify
   ```
   Expected: exit code `0`.
3. `git log --oneline` shows one commit per modified file, all prefixed
   `fix(tasks): T273`.

## Revert rule
If `make verify` fails, revert **only the last file you touched**:
```bash
git checkout -- <that file>
make sync
```
Re-run `make verify`. If it still fails, STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Found and fixed all stale `TASK-NNN` references across 13 knowledge files under `implementation/knowledge/`.
Committed each file individually with conventional message `fix(tasks): T273 use T<NNN> ids in <filename>`.
Ran `make sync` and `make verify` — 0 drift across 421 files.
Registry check and functional test suite passed successfully.

