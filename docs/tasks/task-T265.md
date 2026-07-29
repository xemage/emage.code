# Task T265 — W4-04 Warn before `--update` overwrites local platform edits (D17)

**ID:** T265
**Owner:** backend-developer
**Status:** done
**Priority:** P1
**Depends on:** T264
**Created:** 2026-07-27
**Completed:** 2026-07-28
**Based on:** docs/plans/plan-014-task-ledger-hardening.md § WAVE 4 / W4-04

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `scripts/install.sh`
- **Warn only. Do NOT block, prompt, or exit non-zero.** `--update` must keep working
  exactly as before.
- **R5** If `validate_before_update()` is not present, STOP and report
  `PRECONDITION FAILED: T265`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tasks): T265 warn that --update replaces platform dirs`

## Why this matters (do not skip)
`--update` uses `rsync --ignore-existing` for `docs/` but `rsync --delete` for the
platform trees. Local edits under `.github/`, `.cursor/`, etc. are destroyed without
notice while `docs/tasks/` keeps old-format data — the two halves drift apart.

## Edit — insert a warning loop

Current function (lines 186–191):
```bash
validate_before_update() {
  # Pre-flight checks before --update to prevent propagating corrupted state.
  if [[ "$UPDATE" -eq 1 ]]; then
    validate_github_agents
  fi
}
```

REPLACE WITH:
```bash
validate_before_update() {
  # Pre-flight checks before --update to prevent propagating corrupted state.
  if [[ "$UPDATE" -eq 1 ]]; then
    for d in .github .cursor .gemini .opencode .pi; do
      if [[ -d "$TARGET/$d" ]]; then
        echo "warning: --update replaces $TARGET/$d entirely (rsync --delete). Local edits there will be lost." >&2
      fi
    done
    validate_github_agents
  fi
}
```

The warning loop must run **before** `validate_github_agents`.

## Expected outputs
- `scripts/install.sh` modified.
- Nothing else changed.

## Acceptance criteria
1. Verify command:
   ```bash
   bash -n scripts/install.sh && echo OK
   ```
   Expected output: `OK`
2. Verify command:
   ```bash
   grep -c "rsync --delete). Local edits there will be lost." scripts/install.sh
   ```
   Expected output: `1`
3. Verify command — the warning does not break a real update:
   ```bash
   rm -rf /tmp/emage-t265
   bash scripts/install.sh --target /tmp/emage-t265 --platform github
   bash scripts/install.sh --target /tmp/emage-t265 --platform github --update
   echo "exit=$?"
   ```
   Expected: `exit=0`, and the second run prints the warning for `.github` on stderr.
4. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any verify command fails:
```bash
git checkout -- scripts/install.sh
```
then STOP and report.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Implemented the warning loop in `validate_before_update()` in `scripts/install.sh`
before `validate_github_agents`, with no behavior change other than stderr warning.

Verification results:

```bash
$ bash -n scripts/install.sh && echo OK
OK

$ grep -c "rsync --delete). Local edits there will be lost." scripts/install.sh
1

$ rm -rf /tmp/emage-t265
$ bash scripts/install.sh --target /tmp/emage-t265 --platform github
Installed emage.code (github) into /tmp/emage-t265

$ bash scripts/install.sh --target /tmp/emage-t265 --platform github --update
warning: --update replaces /tmp/emage-t265/.github entirely (rsync --delete). Local edits there will be lost.
merge ledger /tmp/emage-t265/docs/tasks/active-tasks.md
merge ledger /tmp/emage-t265/docs/tasks/completed-tasks.md
Updated emage.code (github) in /tmp/emage-t265

$ echo "exit=$?"
exit=0

$ git status --porcelain
 M scripts/install.sh
```

Outcome: PASS.
