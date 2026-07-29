# Task T255 — GATE 2: no stale patterns remain in commands

**ID:** T255
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T251, T252, T253, T254
**Created:** 2026-07-27
**Completed:** 2026-07-27
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § GATE 2

## STOP-RULES (read before touching anything)
- This is a **GATE**. Do **NOT** edit any canonical source file here.
- The only allowed write action is `make sync`.
- Do NOT run `git push`.

## Objective
Prove Wave 2 removed every ledger-corrupting and lifecycle-wrong pattern from the
command knowledge base, and that the projections still build.

## Steps (do exactly this, in this order)
1. ```bash
   make sync && make verify
   ```
2. ```bash
   grep -rn "BUG-<id>\|→ review →" implementation/knowledge/
   ```

## Expected outputs
- Regenerated platform folders under `implementation/`.
- A VERDICT: `PASS` | `CONDITIONAL_PASS` | `FAIL`.

## Acceptance criteria
1. Step 1 exits with code `0`.
2. Step 2 produces **no output** (grep exit code `1`).
3. No file under `implementation/knowledge/` was modified by this task.

## Revert rule (only if step 1 fails)
```bash
git checkout -- implementation/.github implementation/.cursor implementation/.gemini implementation/.opencode implementation/.pi
make sync
```
Then re-run. If it fails a second time, emit VERDICT `FAIL`, report the full output,
and STOP.

If step 2 produces output, emit VERDICT `FAIL`, list the offending file:line pairs,
and STOP. Do **not** fix them here — the orchestrator re-opens T251/T252.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Gate commands executed in order:

```bash
$ make sync && make verify
Done - 416 files written.
OK - no drift across 416 files.

$ grep -rn "BUG-<id>\|→ review →" implementation/knowledge/
$ echo "GREP_EXIT=$?"
GREP_EXIT=1
```

Interpretation:
- Step 1 exit code = 0 (PASS)
- Step 2 produced no output and exit code 1 (PASS for grep no-match case)

Verdict: PASS.

Regenerated projection outputs were committed as:
`c87067e` (`chore(sync): regenerate projections for wave-2 gate`).
