# T518 — Stop `install.sh --update` destroying local settings and ledger prose

**ID:** T518
**Owner:** DevOps Engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-09-25
**Completed:** 2026-09-25
**Based on:** docs/plans/plan-069-t518-t519-carried-defects.md

## 1. Objective

`scripts/install.sh --update` destroys two things in every target project on every run. Both were
first recorded in `T512` (2026-09-19), recurred verbatim during `T517`'s post-merge sync
(2026-09-25), and were caught both times only because a pre-snapshot was taken by hand. The root
cause has never been fixed.

Fix both, so an `--update` is non-destructive to project-local state.

## 2. Defect A — `.claude/settings.json` is deleted

`sync_tree_into()` uses `rsync -a --delete`. `implementation/.claude/` contains only `agents`,
`commands`, `rules` and `skills` — there is no `settings.json` in the source tree — so `--delete`
removes the target's `settings.json`. That file is project-local state (a host's Bash-permission
allowlist); it is not harness content and has no `implementation/` counterpart by design.

**The fix mechanism already exists in this script.** Compare the two call sites:

```
line 393:  install_tree_into "$IMPLEMENTATION/.gemini" "$TARGET/.gemini" "settings.json" "settings.json.provenance.json"
line 408:  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude"
```

`.gemini` already excludes its `settings.json` from the delete sweep. `.claude` does not. Decide
whether `settings.local.json` needs the same protection and say why either way.

Check the other platform trees for the same exposure rather than fixing only the one that was
reported. If another platform has project-local files with no source counterpart, they have the
same bug and should be covered by the same change.

## 3. Defect B — `active-tasks.md` loses all prose and gains a false claim

`merge-task-docs.py` preserves ledger table **rows** but discards the surrounding **prose**,
substituting the template's. Reproduced directly against the current repository state:

```
BEFORE  active-tasks.md:     65 lines, 0 rows, 0 occurrences of "ledger starts EMPTY"
AFTER   active-tasks.md:     11 lines, 0 rows, 1 occurrence of "ledger starts EMPTY"
        completed-tasks.md:  316 rows -> 316 rows   (preserved correctly)
```

So row preservation works; prose preservation does not exist. The consequence is worse than data
loss: the template asserts that the ledger starts empty and the first real task is `T001`, which is
**actively false** in a repository with 316 completed tasks, and `active-tasks.md` is exactly the
file a cold session reads first and trusts literally.

The failure is at its worst precisely when the ledger is healthy — with **zero** active rows, which
is the normal state after archiving completed work, there is nothing to preserve and the template
wins outright. That is the state this repository is in right now.

`install.sh:17` advertises "preserves task rows in `docs/tasks/*.md`". Note that the current
behaviour matches that sentence literally while still being wrong. Part of this task is deciding
what the contract *should* be and making the help text say it.

## 4. Scope

**In scope:** `scripts/install.sh`, `scripts/merge-task-docs.py`, their tests
(`tests/functional/test_install_script.py`, `tests/functional/test_merge_task_docs.py`), and the
`--update` help text.

**Out of scope:**

- `merge-mcp-json.py` and the MCP projections. That path already merges correctly — verified during
  `T517`, where it preserved a user's hand-edit rather than overwriting it.
- The template files themselves (`implementation/docs/tasks/*.md`). They are correct *as templates
  for a fresh install*; the defect is that `--update` applies them as if the target were fresh. Do
  not fix this by softening the template's wording — that hides the bug and leaves a fresh install
  with weaker guidance.
- Any change to ledger content in this repository.

## 5. Constraints

1. **A fresh install must still work.** Both defects are `--update`-specific. Do not fix `--update`
   by breaking the fresh-install path, and test both.
2. **Reproduce before fixing.** Both defects have exact reproductions in §2 and §3. Reproduce each
   one yourself first and paste the output, so the fix is demonstrably tied to the cause.
3. **Do not weaken a test to pass.** If an existing test asserts the current destructive behaviour,
   that test encodes the bug — correct it and say so explicitly.
4. Do not change any component's `maturity:` value. Do not write to `tests/golden/**` or
   `scripts/scorecard.py` (protected paths; this task is not authorized there).
5. `set -e` hazard, learned the hard way in `T513`: a bare `[[ cond ]] && cmd` as a function's last
   statement makes the *function's* exit status that of the failed test, killing the script under
   `set -e`. Use `if`/`fi` blocks. That bug passed every local test and only failed in CI's
   `python:3.12-alpine` image, which has no `rsync` — so exercise the **no-rsync fallback path** too,
   not just the rsync path.

## 6. Verification

```
python3 implementation/scripts/check-maturity.py     # 79 components, 0 failing
python3 docs/tasks/validate-tasks.py                 # PASS (0 active, 316 completed)
python3 -m pytest tests/functional -q                # baseline 722 passed, 23 skipped
node implementation/scripts/sync.mjs --root implementation --check
```

Test count must not go down. Beyond the suite, demonstrate the real thing: run
`install.sh --target <throwaway> --platform all --update` against a copy of a realistic target that
has both a `.claude/settings.json` and a populated `active-tasks.md` with **zero** active rows, and
show that both survive byte-identical. Do this with rsync available **and** with rsync hidden from
`PATH`.

## 7. Acceptance criteria

- [ ] Both defects reproduced before the fix, with output pasted.
- [ ] `.claude/settings.json` survives `--update`; other platform trees checked for the same
      exposure and the finding stated either way.
- [ ] `active-tasks.md`'s prose survives `--update`, and no false "ledger starts EMPTY" text is ever
      written into a populated target.
- [ ] `completed-tasks.md` still preserved (it already is — do not regress it).
- [ ] Fresh install still produces correct scaffolding, tested.
- [ ] Both the rsync and no-rsync paths exercised.
- [ ] `--update` help text matches the actual contract.
- [ ] Tests added that fail against the current implementation — verify this by running them against
      the pre-fix tree and say so.

## 8. Working agreement

Branch from `develop` in a worktree, named per the agent-worktree convention in the Git Workflow
rules under `.claude/rules/`. Do not work in the primary checkout. Conventional Commits. Do not merge
your own branch and do not push to `develop` or `main` — hand the branch back; the orchestrator opens
the MR. There is no "it's a small script fix" exception.

`git push` is hitting a known GitLab-side transient (`"erase" is an invalid operation`, or
`HTTP Basic: Access denied`) that clears with elapsed time, not retries — observed up to ~45 minutes.
Do not run `glab auth` anything and do not change any `git config credential.*` setting. If it keeps
failing, commit everything and hand back an `external` blocker.

## 9. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate.

If the right fix for Defect B turns out to be a contract change rather than a code change — for
example that `--update` should not touch `active-tasks.md` at all — report that with your reasoning
before implementing it. That is a design decision worth confirming, not something to improvise.
