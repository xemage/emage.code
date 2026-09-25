# T533 — Settle and fix the committed golden scorecard artifact

**ID:** T533
**Owner:** DevOps Engineer
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-075-scorecard-artifact-staleness.md`; `scripts/scorecard.py`;
`docs/artifacts/protected-paths-v1.md` §5; `docs/artifacts/golden-suite-format-v1.md`.

## 1. The defect

`docs/benchmarks/scorecard-v6.12.0.{json,md}` is committed at `total_cases: 20`, `total_pass: 11`,
`tracked_defect: 6`. A fresh `python3 scripts/scorecard.py` on the current tree produces
**24 / 16 / `tracked_defect: 4`**.

It has **one commit** in its history — `b16b382`, the original `T410`–`T415` landing — and **nothing
validates it**: no test under `tests/functional/` or `tests/performance/`, no `.gitlab-ci.yml` job.
Meanwhile `scorecard.py`'s own docstring says `content` "is a pure function of the golden suite tree's
on-disk bytes". A pure function of the tree that nothing checks rots silently, and did.

**Three implementers hit this independently** (`T525`, `T531`, `T521`) and each had to revert
`docs/benchmarks/` by hand, because every `scorecard.py` run rewrites it. **"Expect a clean
`git status`" is unreachable in any brief until this is fixed** — that instruction has now misfired
three times.

## 2. Your decision

Choose **one** of `plan-075` §2's options and state why. Do not hedge.

`plan-075` recommends **A — track it and gate it**, on the precedent that this repo already gates its
other generated artifacts: `implementation/registry/` via `check.py --registry`, the platform
projections via `sync-no-diff`. Both exist because a generated file nothing checks drifts.

**You may choose differently, but if you choose B (regenerate once, no gate), you must say what will
catch the next drift** — B is the status quo and is what produced this defect.

## 3. Two traps — read before designing anything

1. **`run_metadata.generated_at` differs on every run by design.** A drift gate comparing whole files
   would be red on every pipeline. Compare **the `content` key only** — the boundary the script's own
   docstring already draws. A permanently-red gate is worse than no gate, because it gets disabled.
2. **`scripts/scorecard.py` is a protected path.** See §4.

## 4. PROTECTED-PATH AUTHORIZATION — narrow and conditional

**This task is authorized to modify `scripts/scorecard.py`, citing `protected-paths-v1.md` §5.2, and
the authorization covers exactly one kind of change:**

| Path | Permitted change |
|---|---|
| `scripts/scorecard.py` | **an additive check/verify mode only** (e.g. a `--check` flag that compares the committed `content` against a fresh computation and exits non-zero on drift) |

**Explicitly NOT authorized:** any change to what the script *measures*, how it classifies cases, its
discovery logic, its redaction behaviour, or its output schema. If your chosen option needs any of
those, **stop and report a blocker.** §5.1 forbids you extending your own grant; `T520`, `T523`,
`T525`, `T527` and `T531` all hit this boundary and all five refused.

**`tests/golden/**` is not authorized at all.** Do not touch any case. `docs/benchmarks/` is **not**
protected — regenerating those artifacts needs no authorization.

## 5. Held-out redaction must not regress

`scorecard.py` deliberately keeps held-out **case identities** out of its output artifacts: those
files live outside `tests/golden/`, so `test_golden_held_out_isolation.py` **Check B** applies to
them, and a descriptive case ID would reveal what a held-out case tests. The output carries held-out
**aggregate** health only.

A regenerated artifact must preserve that. **If `pytest tests/functional/test_golden_held_out_isolation.py`
fails, that is a `critical` blocker, not a detail to work around.** Verify it explicitly and report
the result.

## 6. Evaluator-hash

If you touch **only** `scripts/scorecard.py` and `docs/benchmarks/`, the `tests_golden` digest does
**not** move — but **`scripts_scorecard` will**, and that digest has been byte-identical across v1–v5,
which has been used as evidence in five closure records that the script was untouched.

So: **recompute both digests read-only** via `golden_harness.evaluator_hash.compute_current_digests(Path('.'))`,
report them, and **do not write a new baseline.** That refresh needs explicit human authorization and
is out of your scope — five agents running have respected this and one noted it could have argued
`docs/artifacts/` was unprotected and declined anyway. Expect the two evaluator-hash tests to go red
if and only if you change the script; say which digest moved and why.

## 7. Verification

```
python3 tests/run.py       # BASELINE FIRST: 774 tests, OK, 23 skipped
python3 -m pytest tests/functional/test_golden_held_out_isolation.py -q
python3 scripts/scorecard.py
python3 implementation/scripts/check-maturity.py --root implementation
python3 implementation/scripts/check.py --registry --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Full 774-test `tests/run.py`, not `pytest tests/functional` (734).** Measure the baseline yourself
first. **`check-maturity.py` must stay `79 components checked, 0 failing` with an unchanged
distribution** — this task promotes nothing, and if the numbers move something has gone wrong.

If you add a CI job, state plainly **when it runs** and **what it does to an existing pipeline** — a
previous task in this phase added a gate that silently changed release-tag behaviour, and disclosing
that up front is what made it reviewable.

## 8. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch
`agent/devops-engineer/T533`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`: known environment transient, not your fault, credentials are not broken,
and you must not touch any `glab` or `git config credential.*` setting. Retry two or three times,
then report that the commit is on the local branch.

Blockers: type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Max 2 retries. Never widen §4 — report instead.
