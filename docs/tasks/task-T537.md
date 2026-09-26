# T537 — `validate-tasks.py` silently accepts a dangling `Depends on`

**ID:** T537
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-09-26
**Completed:** 2026-09-26
**Based on:** `docs/plans/plan-076-wave2-findings.md` §3; `docs/tasks/task-T528.md`;
`AGENTS.md` § Task Protocol.

## 1. The defect

`docs/tasks/validate-tasks.py:203` destructures an active row as:

```python
task_id, _, _, status, priority, _, last_update = row.cells
```

**The sixth cell — `Depends on` — is discarded into `_` and never read.** No check in the validator's
inventory resolves a dependency against the known ID set.

So a row whose `Depends on` names a task existing in **neither** ledger passes `TASK LEDGER: PASS`
silently. Found by wave 2's implementer while authoring the `/bug-report` case, and confirmed by
reading the line.

This matters more than it looks: those edges are what `/sprint-status` reconstructs its DAG from, and
`plan-074` §3's queue ordering leaned on them. **An unvalidated edge is a dependency nobody is
checking.**

## 2. Add the check — and two traps to verify, not assume

Add a new numbered check consistent with the existing `C<n>` scheme (the emittable codes today are
`C2 C3 C4 C5 C7 C10 C11`; read the file and pick the next free number rather than guessing).

**Trap 1 — a satisfied dependency points into `completed-tasks.md`.** That is the *normal* case:
`T532` currently declares `Depends on: T531`, and `T531` is completed. **Resolving only against
`active-tasks.md` would flag every satisfied dependency as dangling** and make the check useless.
Resolve against the union of both ledgers.

**Trap 2 — it must not fire on the real ledger.** Run the validator against the live tree before and
after. If it reports violations on rows that are actually fine, **the check is wrong, not the
ledger** — say so and fix the check. The existing state must stay `PASS`.

Also handle the `—` em-dash placeholder that means "no dependency", and the comma-separated
multi-dependency form if the corpus uses it — **check what the real rows actually contain** rather
than assuming a shape.

## 3. Prove it in both directions

A check that cannot fail is worth nothing. Demonstrate, with output in your report:

1. Against the **real** ledgers → `PASS`, unchanged.
2. Against a **synthetic** row whose `Depends on` names a nonexistent ID → your new `C<n>` fires.
3. Against a synthetic row depending on a **completed** task → does **not** fire (trap 1).

Build the synthetic fixtures in a temp directory, not in the repo's ledgers.

## 4. Scope

| In scope | Out of scope |
|---|---|
| `docs/tasks/validate-tasks.py` | anything under `tests/golden/**` |
| a test under `tests/functional/` if you judge one warranted | `scripts/scorecard.py` |
| this brief's `**Status:**` | any `maturity:` field |
| — | `active-tasks.md`, `completed-tasks.md` content |

`docs/tasks/validate-tasks.py` is **not** a protected path — no authorization needed. But it is
load-bearing: it gates every ledger edit in this repo and runs in CI's `validation-super-gate`. **A
false positive here blocks all work**, which is why §2 trap 2 is not optional.

## 5. Verification

```
python3 tests/run.py                  # BASELINE FIRST; measure it yourself
python3 docs/tasks/validate-tasks.py  # must still be PASS on the real ledgers
python3 scripts/scorecard.py --check  # READ-ONLY. Never the write mode as a check.
python3 implementation/scripts/check-maturity.py --root implementation
node implementation/scripts/sync.mjs --check
git status --porcelain
```

Expected: `validate-tasks.py` → `PASS` unchanged; `tests/run.py` → **792 / OK / 23 skipped** plus any
test you add; evaluator-hash unchanged; `git status` clean after commit. **Measure the baseline
yourself** — three figures have circulated in this phase's briefs and all three were wrong at some
point.

## 6. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch
`agent/backend-developer/T537`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`: known environment transient, not your fault, credentials are not broken,
and you must not touch any `glab` or `git config credential.*` setting. Retry two or three times,
then report that the commit is on the local branch.

Blockers: type and severity; max 2 retries. Report anything the brief got wrong — briefs in this
phase have been wrong six times and every time the implementer caught it.
