# T521 — Execute ADR-007 verdict C: give `## RELEASE VERDICT` a declared home

**ID:** T521
**Owner:** Release Manager
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-09-25
**Completed:** 2026-09-26
**Based on:** docs/plans/plan-070-t520-t521-adr-007-execution.md

## 1. Objective

`ADR-007` verdict **C** on `prepare-release-real-verdict-missing` is **fix the corpus** (branch 3b):
the contract stands, the corpus failed to discharge it. But the resolution artifact also found a
**real under-specification** worth closing: `prepare-release.md` step 7 mandates a
`## RELEASE VERDICT` block with 11 fields and never says *where* it goes — and the two golden cases
for that clause disagree, one checking a release-notes file and one a release checkpoint.

Declare the home and add the slot. This is a **clarification that adds no requirement**: the 11
fields and the `Status` enum are unchanged.

## 2. Why this is separate from `T520`

Verdict C touches **no protected path**, so it needs no `protected-paths-v1.md` §5 authorization.
`T520` carries a file-scoped authorization for `tests/golden/**`; keeping C out of it keeps that
authorization as narrow as possible. The two tasks are independent and may run in either order.

## 3. The recommended resolution, and the reasoning behind it

Declare **`docs/releases/v<version>.md`** the home, and add the section to
`docs/releases/_template.md`. The resolution artifact's three reasons:

1. It matches what the paired golden sibling already encodes.
2. `docs/checkpoints/_template.md` is the generic every-phase template; a release-only section does
   not belong in it.
3. `scripts/verify-release-docs.py` already governs release-notes sections, so the gate has somewhere
   to enforce it.

You may reach a different conclusion, but if you do, **say why against those three reasons** rather
than substituting a preference.

## 4. Scope

**In scope:** `implementation/knowledge/commands/prepare-release.md` (step 7, the placement sentence
only); `docs/releases/_template.md` (add the section); optionally `scripts/verify-release-docs.py`
and its tests, if enforcing the new section there is the right call — decide and justify.

**Out of scope, explicitly:**

- **Anything under `tests/golden/**`.** This task has **no** protected-path authorization. The golden
  case stays `known_failing` and untouched. If you think a golden change is needed, stop and report.
- The 11 fields and the `Status` enum. Do not add, remove or rename one.
- `docs/checkpoints/_template.md`.
- Retro-editing any shipped release document. The fixture is a frozen copy of
  `checkpoint-release-v6.4.1.md` and is immutable.

## 5. The case stays red, and that is correct

`prepare-release-real-verdict-missing` **remains `known_failing` after this task**, indefinitely as
currently fixtured. Its fixture is a verbatim copy of a shipped release checkpoint that cannot be
retro-edited and, under the recommended placement, is also the wrong artifact class.

The recorded exit is to **emit a conforming `## RELEASE VERDICT` in the next real release, then
re-fixture the case against it** — promotion is earned by producing conforming output, not by editing
the test. Do not attempt to close the gap by any other route, and do not treat the case remaining red
as this task failing.

`/prepare-release` and `orchestrator` therefore stay blocked. That is expected.

## 6. Verification

```
python3 implementation/scripts/check-maturity.py     # 79 components, 0 failing
python3 docs/tasks/validate-tasks.py                 # PASS
python3 -m pytest tests/functional -q                # baseline 722 passed, 23 skipped
node implementation/scripts/sync.mjs --root implementation --check
```

If you touch `verify-release-docs.py`, run it against the existing real release documents and report
what it says — several predate the clarified contract and may not carry the section. **Do not
retro-edit them to pass**; report the count and leave them.

## 7. Acceptance criteria

- [ ] Step 7 names the home for the block; the 11 fields and `Status` enum unchanged.
- [ ] `docs/releases/_template.md` carries the section.
- [ ] The gate decision (`verify-release-docs.py` or not) made and justified either way.
- [ ] Nothing under `tests/golden/**` modified.
- [ ] No shipped release document retro-edited; any non-conforming ones reported, not fixed.
- [ ] Test count not reduced.

## 8. Working agreement

Branch from `develop` in a worktree, named per the agent-worktree convention in the Git Workflow
rules under `.claude/rules/`. Do not work in the primary checkout. Conventional Commits. **Do not
merge your own branch and do not push to `develop` or `main`** — no exception for a docs-shaped
change. Hand the branch back; the orchestrator opens the MR.

`git push` is hitting a known GitLab-side transient that clears with elapsed time, not retries
(observed up to ~45 minutes). Do not run `glab auth` anything and do not change any
`git config credential.*` setting. If it keeps failing, commit and hand back an `external` blocker.

## 9. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate.
