# Task T251 — W2-01 Fix `/bug-report` ledger corruption (D11)

**ID:** T251
**Owner:** technical-writer
**Status:** done
**Priority:** P0
**Depends on:** T250
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 2 / W2-01

## STOP-RULES (read before touching anything)
- **R1** NEVER edit anything under `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`.
- **R2** This task touches **EXACTLY ONE FILE**:
  `implementation/knowledge/commands/bug-report.md`
- **R5** If the FIND text is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T251`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T251 stop bug-report writing non-conforming ledger rows`

## Why this matters (do not skip)
`/bug-report` currently tells agents to write a **6-cell** row with a `BUG-` prefix into
a **7-column** table. On the next `install.sh --update`, `scripts/merge-task-docs.py`
matches only `T<NNN>` rows and **silently deletes every `BUG-` row**. This is live
customer data loss.

## Edit — replace one line with five lines

FIND (exact, currently line 48, note the **three leading spaces**):
```
   - Format: `| BUG-<id> | <title> | pending | <owner> | <severity> | <blocker-ids> |`
```

REPLACE WITH (exact, preserve the three-space indentation on every line):
```
   - Use the NEXT sequential `T<NNN>` ID. NEVER invent a `BUG-` prefix — non-`T` rows are silently deleted by `install.sh --update`.
   - Format (7 columns, exact order):
     `| T<NNN> | BUG: <title> | <owner-slug> | pending | P0\|P1\|P2 | <dep-ids or —> | YYYY-MM-DD |`
   - Map severity → priority: critical→P0, high→P0, medium→P1, low→P2
```

## Expected outputs
- `implementation/knowledge/commands/bug-report.md` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   grep -c "BUG-<id>" implementation/knowledge/commands/bug-report.md
   ```
   Expected output: `0`
2. Verify command:
   ```bash
   grep -c "NEVER invent a" implementation/knowledge/commands/bug-report.md
   ```
   Expected output: `1`
3. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- implementation/knowledge/commands/bug-report.md
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Replaced the legacy `BUG-<id>` ledger format guidance in
`implementation/knowledge/commands/bug-report.md` with canonical `T<NNN>`
task creation rules, 7-column row format, and severity→priority mapping.

Verification results:

```bash
$ grep -c "BUG-<id>" implementation/knowledge/commands/bug-report.md
0
$ grep -c "NEVER invent a" implementation/knowledge/commands/bug-report.md
1
$ git status --porcelain
 M implementation/knowledge/commands/bug-report.md
```

Outcome: PASS.
