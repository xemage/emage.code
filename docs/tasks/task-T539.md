# T539 — no guard in `tests/golden/**` detects array cardinality

**ID:** T539
**Owner:** QA Engineer
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T529 (merged 2026-09-26)
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-077-parallel-round-findings.md` §2; `docs/tasks/task-T529.md` §5;
`docs/artifacts/golden-suite-format-v1.md` §2; `docs/artifacts/protected-paths-v1.md` §5.

## 1. The gap

`tests/golden/open/handoff-payload-schema-fields-real/expect.py` embeds the real handoff schema and
checks payloads against it — but its `_object_matches_schema()` implements only `required`,
`additionalProperties`, `enum`, `pattern` and nested `properties`. It implements **zero array
keywords**: no `items`, no `minItems`, no `maxItems`. Verified independently.

**Consequence: no case in `tests/golden/**` can detect an empty or malformed array, at any schema
version.** `T529` proved this the hard way — emptying `writablePaths` left `check()` returning `True`
both before *and after* the schema gained `minItems: 1`.

It also means an earlier orchestrator conclusion was half wrong: a mutation that failed to flip was
diagnosed as merely "mis-designed", when there were **two** independent reasons it survived and only
one had been found. Write-scope cardinality is currently covered **solely** by `T529`'s five new
`tests/functional/` tests, not by the golden suite at all.

## 2. Choose a route, and argue it

`T529` offered two. **Pick one; do not attempt both.**

**Route A — extend `_object_matches_schema()` to array keywords.** Strengthens every present and future
case that embeds a schema. Larger, and it is a protected-path edit to a checker shared by one case
today and potentially more later.

**Route B — add a case whose oracle is `validator.py`**, which now genuinely enforces the constraint.
Narrower. **But check `golden-suite-format-v1.md` §2.2 first**: it requires `expect.py` to be a
deterministic, CI-safe, pure function of `case_dir` that never invokes a live model. Importing repo
runtime code is not a model call, but whether it satisfies "pure function of `case_dir`" is a real
question — a case whose verdict depends on `implementation/runtime/` changes meaning when that code
changes. **Read §2.2 and state whether Route B conforms. If it does not, say so and take Route A.**

## 3. The binding risk here is OVER-strengthening, not relaxing

Either route strengthens a check, so `ADR-007` §5's prohibition on relaxing is **not** what constrains
you. The mirror image is: **a guard that starts rejecting fixtures which legitimately conform is worse
than the gap it closes.** `T531` faced exactly this inversion and the instruction there holds here.

Concretely, if you take Route A:

- **Run the full suite before and after.** Any case that currently passes and then fails is a
  regression *you* introduced, not a latent defect you exposed — unless you can show the fixture
  genuinely violates the schema it embeds, in which case say so with evidence.
- **Implement the keywords faithfully, not stringently.** `minItems` absent means no lower bound;
  `items.minLength: 1` means non-empty strings, not non-blank ones. `T529` mirrored `minLength`
  literally rather than adding `.strip()` precisely so the two encodings could not drift — hold that
  line.

## 4. PROTECTED-PATH AUTHORIZATION — scoped to the route you choose

**Authorized under `protected-paths-v1.md` §5.2, and deliberately narrow.** The two routes need
different grants; issuing the union would be the widest grant in this phase for no reason.

| If you take | You may modify |
|---|---|
| **Route A** | `tests/golden/open/handoff-payload-schema-fields-real/expect.py` — the schema-matching helper only |
| **Route B** | create **one** new case directory under `tests/golden/open/` |

**Not authorized under either:** `scripts/scorecard.py`; anything under `tests/golden/held-out/`; any
*other* existing case directory; that case's `case.yaml`, `brief.md` or `fixture/` unless your route
requires it, in which case **state which and why before touching it**.

§5.1 forbids extending your own grant. If the route you choose needs more, **stop and report a
blocker.** Five tasks in this phase hit that boundary and all five refused.

## 5. The scorecard and the hash — both consequences of touching `tests/golden/**`

1. **Regenerating `docs/benchmarks/` is a required step**, not a forbidden one — `T533`'s gate asserts
   the committed artifact matches a fresh run, and Route B changes the case count. Run
   `python3 scripts/scorecard.py` (write mode) and **commit both files**. `docs/benchmarks/` is not
   protected. Verify held-out rows stay redacted as `held-out-case-<n>` / `<redacted>`.
2. **Two evaluator-hash tests will go red.** Expected. **Do not fix it.** `docs/artifacts/` is
   unprotected so you could argue the refresh is in scope — it is not. Recompute read-only via
   `golden_harness.evaluator_hash.compute_current_digests(Path('.'))`, report both digests and how each
   differs from `evaluator-hash-known-good-v9.json`, and stop. `scripts_scorecard` must come back
   byte-identical to v9. *(Corrected 2026-09-30: this brief said v7, which was two baselines stale.)* The digest hashes git-tracked files only, so compute it **post-commit**.

## 6. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it yourself
python3 scripts/scorecard.py          # WRITE mode, required by §5; commit the result
python3 scripts/scorecard.py --check  # must exit 0 once committed
python3 -m pytest tests/functional/test_golden_held_out_isolation.py tests/functional/test_scorecard_artifact_no_drift.py -q
python3 implementation/scripts/check-maturity.py --root implementation
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Measure the baseline yourself** — four figures have circulated in this phase's briefs and all were
wrong at some point. It should currently be **806 / OK / 23 skipped**, but verify. Expected after your
change: exactly the two evaluator-hash failures and nothing else. `check-maturity.py` must stay
`79 / 0` with an unchanged distribution — **this task promotes nothing.**

Also call `check()` directly against the affected case's fixture and report the boolean.

## 7. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch `agent/qa-engineer/T539`.
Commit message ends with exactly `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with the `glab auth git-credential: "erase" is an invalid operation` /
`HTTP Basic: Access denied` pair: known environment transient, not your fault, credentials are not
broken, and you must not touch any `glab` or `git config credential.*` setting. Retry two or three
times, then report that the commit is on the local branch.

Blockers: type and severity; max 2 retries. Never widen §4 — report instead.
