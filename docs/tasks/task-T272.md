# Task T272 — W6-04 Consolidate brief naming (D9) — **STOP FIRST**

**ID:** T272
**Owner:** orchestrator
**Status:** done
**Priority:** P2
**Depends on:** T271
**Created:** 2026-07-27
**Completed:** 2026-07-29
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 6 / W6-04

## ⛔ STOP FIRST — mandatory user confirmation
This task **deletes files**. Show the user the complete diff and the full content of
every file to be deleted, then ask:

> "Confirm I may merge these four files into their matching `task-T<ID>.md` briefs and
> then delete the originals."

**WAIT for the answer.** Do not delete on silence.

## STOP-RULES (read before touching anything)
- Files in scope — exactly these four:
  - `docs/tasks/brief-T202.md` → merge into `docs/tasks/task-T202.md`
  - `docs/tasks/brief-T210.md` → merge into `docs/tasks/task-T210.md`
  - `docs/tasks/brief-T211.md` → merge into `docs/tasks/task-T211.md`
  - `docs/tasks/task-T220-CONDITIONS.md` → merge into `docs/tasks/task-T220.md`
- If any target `task-T<ID>.md` does **not** exist, STOP for that pair and report.
  Do not create it and do not delete the source.
- **Never `rm -rf`.** Delete each file individually with `git rm <path>`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** One commit per pair. Commit message, exactly:
  `fix(tasks): T272 merge <source-file> into task-T<ID>.md`

## Action — repeat for each of the four pairs
1. Read the source file in full.
2. Append to the end of the target `task-T<ID>.md`:
   ```
   ## Additional brief content

   <verbatim content of the source file, minus its top-level `# ` heading>
   ```
3. Verify the target file still parses as valid markdown and its header block
   (`**ID:**`, `**Status:**`, …) is untouched.
4. `git rm docs/tasks/<source-file>`
5. Commit.

## Expected outputs
- Four source files deleted.
- Four target briefs extended with an `## Additional brief content` section.

## Acceptance criteria
1. Verify command:
   ```bash
   ls docs/tasks/brief-*.md 2>/dev/null | wc -l
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   ls docs/tasks/task-T220-CONDITIONS.md 2>/dev/null | wc -l
   ```
   Expected output: `0`
3. Verify command:
   ```bash
   grep -c "## Additional brief content" docs/tasks/task-T202.md docs/tasks/task-T210.md docs/tasks/task-T211.md docs/tasks/task-T220.md
   ```
   Expected: `1` for each of the four files.
4. No content from any source file was lost — confirm by diffing the appended block
   against `git show HEAD:docs/tasks/<source-file>`.

## Revert rule
```bash
git checkout -- docs/tasks/
git reset HEAD docs/tasks/
```
then STOP and report. **Warning:** this reverts earlier Wave 6 tasks. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Merged four auxiliary brief files (`brief-T202.md`, `brief-T210.md`, `brief-T211.md`, `task-T220-CONDITIONS.md`) into their matching `task-T<ID>.md` briefs and deleted originals with `git rm`.
User confirmed via prompt.

