# T540 — `validate-tasks.py` detects neither self-dependency nor cycles

**ID:** T540
**Owner:** Backend Developer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** T537 (merged 2026-09-26)
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-077-parallel-round-findings.md` §3; `docs/tasks/task-T537.md`.

## 1. The two gaps

`T537` delivered `C12` — every ID in an active row's `Depends on` must exist in some ledger — and
named three things it deliberately did not do. Two are yours:

1. **Self-dependency passes.** A row declaring `Depends on: <its own ID>` resolves, because its own ID
   is in `active_ids`. Verified.
2. **Cycles are not detected.** `/sprint-status` builds a DAG from these edges and a cycle breaks it.

## 2. The third gap is deliberately excluded — do not fix it

**A dependency on a `cancelled` task resolves**, because cancelled rows live in `completed-tasks.md`
and `C12` checks the union.

`T537` was right that this is a **policy question, not a defect**: depending on cancelled work may be
legitimate during a transition. Deciding it needs a rule first, and **inventing one inside a validator
patch is how contracts get made by accident.** If you think it should be flagged, say so and why — but
do not implement it.

## 3. Design calls that are yours

- **Self-dependency inside `C12`, or its own code?** It is the same cell and the same resolution pass,
  so extending `C12` is defensible; a distinct code gives a clearer message. Pick one and say why.
- **Cycles almost certainly want their own code** — different failure semantics, and the message needs
  to name the cycle rather than one row. Your call, argued.

Read `C12` and the surrounding checks first and match the house style: the numbered scheme, the
`add_fail` convention, and the explanatory comment block `C11` and `C12` both carry.

**Note `C12` already occupies the next number after `C11`**, so read the file to find what is free
rather than assuming.

## 4. The trap that binds hardest — restated from `T537` because it has not changed

**A false positive in `validate-tasks.py` blocks every ledger edit in this repo and runs in CI's
`validation-super-gate`.** If your checks misfire, nothing can merge.

- **The real ledger must stay `PASS`.** Run it against the live tree before and after. If it reports
  violations on rows that are actually fine, **the check is wrong, not the ledger.**
- **There are two copies held at byte parity by an existing test.**
  `implementation/docs/tasks/validate-tasks.py` is the copy installed into target repos, and
  `tests/functional/test_validate_tasks_affects.py::test_shipped_copy_matches_the_repo_copy` asserts
  equality. **Patch both.** `T537`'s brief named only one path and the implementer caught it; this one
  tells you up front.
- **The dependency cell has five historical shapes**, surveyed by `T537` across 80 revisions: the `—`
  placeholder, the words `None`/`none`, a bare ID, comma-separated IDs with `(status)` annotations, and
  free prose embedding real IDs. `C12` handles this by extracting `\bT\d{3,}\b` tokens and ignoring
  everything else. **Reuse that token extraction rather than writing a second parser** — two parsers
  for one cell is a drift source.

## 5. Prove both directions

For **each** new check, with verbatim output:

1. Against the **real** ledgers → `PASS`, unchanged.
2. Against a synthetic row that should trip it → fires.
3. Against a synthetic row that should **not** → does not fire. For cycles, include a genuine
   multi-row chain (`A → B → C → A`), not just a two-row pair.

Build fixtures in a temp directory, **never** in the repo's ledgers.

## 6. Scope

In scope: both copies of `validate-tasks.py`, a test under `tests/functional/`, and this brief's
`**Status:**`.

Out of scope: anything under `tests/golden/**`; `scripts/scorecard.py`; any `maturity:` field;
`docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` content — **archival is
orchestrator-only, so move no row.** Note `T537`'s check found one golden fixture's excerpt ledger
gains a `C12` line; if your checks add more there, **report it and do not touch the fixture.**

## 7. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it yourself
python3 docs/tasks/validate-tasks.py  # must still be PASS on the real ledgers
python3 scripts/scorecard.py --check  # READ-ONLY. Never the write mode as a check.
python3 implementation/scripts/check-maturity.py --root implementation
node implementation/scripts/sync.mjs --check
git status --porcelain
```

**Measure the baseline yourself** — four figures have circulated in this phase's briefs and all were
wrong at some point. It should currently be **806 / OK / 23 skipped**, plus your new tests.

## 8. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch
`agent/backend-developer/T540`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with the `glab auth git-credential: "erase" is an invalid operation` /
`HTTP Basic: Access denied` pair: known environment transient, not your fault, credentials are not
broken, and you must not touch any `glab` or `git config credential.*` setting. Retry two or three
times, then report that the commit is on the local branch.

Blockers: type and severity; max 2 retries. Report anything the brief got wrong — briefs in this phase
have been wrong seven times and every time the implementer caught it.
