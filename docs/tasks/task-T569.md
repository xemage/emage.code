# T569 — Promote `/validate-workflow` to `stable` (T566 FU-3)

**ID:** T569
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T568
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-093-validate-workflow-repair.md`; `implementation/scripts/check-maturity.py`; T562's
recipe (`docs/tasks/task-T562.md` §2).

## 1. What and why

After T568, `/validate-workflow`'s only golden case is `expected_pass`. Before this task is dispatched, the
orchestrator re-runs a dry run on `develop`: flip the maturity line and run `check-maturity`. **Dispatch only if
that dry run passes every `stable` criterion.** If it fails, this brief is revised first.

## 2. The change: three linked edits (T562's recipe)

1. In `implementation/knowledge/commands/validate-workflow.md`, change `maturity: experimental` to
   `maturity: stable`. Nothing else in the file changes.
2. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`. `maturity` exists only in the source, so **no projection
   may change**. Confirm that.
3. In `tests/functional/test_check_maturity.py`, update the command distribution assertions to **14 stable /
   5 experimental**. Find every hardcoded count.

## 3. Verify, don't assume

- `check-maturity.py --root implementation`: 79 components, 0 failing, command 14/5.
- `--print-drift` unchanged, audience lint passes, `sync.mjs --check` no drift, `generate-registry.py --check` up to
  date, `scorecard.py --check` OK, v15 still matches.
- `python3 tests/run.py`: report the exit code. Redirect output to a file; never pipe it to `tail`.

## 4. Constraints

- **Write scope:**
  - the one maturity line;
  - the regenerated `implementation/registry/` (`index.json`, and `summary.md` if it changes);
  - the distribution assertions in `tests/functional/test_check_maturity.py`;
  - this brief's `**Status:**` line.
- No `tests/golden/**` and no `scripts/scorecard.py`.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API.**

## 5. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`.
