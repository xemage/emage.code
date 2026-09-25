# T528 — Golden-case coverage wave 2: five thin-corpus commands

**ID:** T528
**Owner:** QA Engineer
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T525 (merged 2026-09-25)
**Created:** 2026-09-25
**Based on:** `docs/plans/plan-072-phase9-golden-case-coverage.md` §1/§3;
`docs/plans/plan-073-skillify-adjudication-and-wave2.md` §3/§4;
`docs/tasks/task-T525.md`; `docs/artifacts/golden-suite-format-v1.md` §2;
`docs/artifacts/protected-paths-v1.md` §5; `docs/decisions/ADR-007-command-contract-authority.md` §5.

## 1. PROTECTED-PATH AUTHORIZATION — read first

**Authorized to create new case directories under `tests/golden/open/`, citing
`docs/artifacts/protected-paths-v1.md` §5.2.** Scoped to **exactly five new directories**, one per
command — `/consolidate-memory`, `/bug-report`, `/batch`, `/new-project`, `/sprint-status` — each
containing only `case.yaml`, `brief.md`, `expect.py` and `fixture/`.

**Not authorized:** `scripts/scorecard.py`; anything under `tests/golden/held-out/`; **any existing
case directory**; any file under `implementation/knowledge/commands/`; any `maturity:` field.

§5.1 forbids you extending this grant. If more seems needed, **stop and report a blocker** — do not
edit this table. `T520`, `T523` and `T525` all hit this boundary and all three refused. That is the
standard.

## 2. The hazard — this is why the task is shaped as it is

Each of these five commands is blocked from `stable` **solely** because no golden case exists. So a
trivially-passing case immediately unblocks a promotion, and a green board with five new cases looks
like progress. **You are not measured on how many pass.**

Wave 1 is the precedent, and it is worth stating concretely: its four cases were **all** flipped to
`stable` together to measure, and the one `known_failing` case blocked exactly one component while
the other three passed clean. **The same authoring pass that earned three promotions also cost
one.** An implementer optimising for a green board would not have produced that distribution — and
that distribution is why wave 1's greens were believed.

Three rules, all from `plan-072` §1, all validated by wave 1:

1. **Quote the clause first.** Before writing any `expect.py`, find and quote verbatim — with phase
   and step number — the specific clause of `implementation/knowledge/commands/<name>.md` the case
   tests, into `brief.md`'s `## What this checks`. **Do this before designing the check, not after.**
   In wave 1 this ordering is what surfaced the `/skillify` contract conflict: the implementer went
   looking for a checkable clause, found one, and the corpus said no. If no specific checkable
   clause exists for a command, **report that as a blocker** and author the others — a vague
   contract is a more valuable finding than a vague case.
2. **A `known_failing` case is a correct outcome.** Ship it red with `known_failing_category` and a
   `known_failing_reason` stating the survey you actually ran. That command then does not promote,
   and that is the right answer. `ADR-007` §5 — never resolve by relaxing a check — binds authoring
   exactly as it binds fixing.
3. **Five green is a suspicious result, not a target.** If all five pass, your report must
   explicitly argue why that is genuine rather than an artifact of weak checks.

## 3. Mandatory deliverable: a mutation harness

`T525`'s implementer built one unprompted; wave 2 requires it. Copy each case to a temp directory,
damage the fixture in a realistic way, re-run `check()`. **A check that cannot be made to fail is
vacuous.**

Report a mutation table: for each case, at least three distinct realistic mutations and the boolean
each produced. Every `expected_pass` case must flip to `False` under every mutation; every
`known_failing` case must flip to `True` when given a genuinely conforming artifact.

Wave 1 showed this cuts both ways — it caught a **mis-designed mutation** twice, once by the
implementer and once by the orchestrator. **If a mutation does not flip, work out whether the check
is weak or the mutation was wrong before concluding either.** Report that reasoning; do not quietly
drop the mutation.

## 4. Format

Read `golden-suite-format-v1.md` §2 and at least three existing cases in full first.
`expect.py` must expose `check(case_dir: Path) -> bool` and be a **pure function of `case_dir`** —
no `__file__` anchoring, no absolute paths, no network, no subprocess, and **never a live model
call**. Where no real corpus exists, hand-author and say so in `## Provenance`, including the survey
command you ran and its result.

## 5. The evaluator-hash baseline — expected to fail, NOT yours to fix

Your five new directories will drift the `tests_golden` digest and turn these two red:

```
tests/functional/test_golden_harness_evaluator_hash.py::TestBuildKnownGoodPayload::test_matches_the_real_committed_known_good_reference
tests/functional/test_golden_harness_evaluator_hash.py::TestRealRepoNoDrift::test_no_drift_against_real_current_repo_state
```

Expected; stated up front so you need not discover it. **Do not fix it.** `docs/artifacts/` is not
protected, so you could argue the refresh is in scope — it is not. Recompute read-only via
`golden_harness.evaluator_hash.compute_current_digests(Path('.'))`, report both digests and how each
differs from `evaluator-hash-known-good-v4.json`, and stop. `scripts_scorecard` must come back
byte-identical to v4; if it does not, you touched something you should not have — say so.

Note: the digest hashes **git-tracked files only**, so `tests_golden` moves only once your new files
are committed. Compute it post-commit.

## 6. Verification

```
python3 tests/run.py                 # BASELINE FIRST, before any change
python3 scripts/scorecard.py         # read it; do not modify it
python3 -m pytest tests/functional/test_golden_held_out_isolation.py -q
python3 implementation/scripts/check-maturity.py --root implementation
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Full 774-test `tests/run.py`, not `pytest tests/functional` (734)** — the difference contains
guards that have already broken one MR in this phase. Expected after your change: exactly the two
evaluator-hash failures and **nothing else**; any third is yours to explain. `check-maturity.py`
must still be `79 components checked, 0 failing` with an **unchanged distribution** — this task
promotes nothing.

Call each new `check()` directly against its own fixture and report the boolean, rather than
inferring it from the scorecard.

## 7. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; do not move any ledger row — archival is
orchestrator-only. Branch `agent/qa-engineer/T528`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge — no exceptions, however green.**

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`: known environment transient, not your fault, credentials are not
broken. Do **not** touch any `glab` or `git config credential.*` setting. Retry two or three times,
then report that the commit is on the local branch.

Blockers: type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Max 2 retries, then escalate. Never widen §1.

## 8. Your final report

Per case: directory name, `status`, the **exact clause quoted** and its source, whether the fixture
is real or hand-authored, and the boolean `check()` returned. Plus the mutation table from §3, the
verbatim output of every §6 command including the baseline, both recomputed digests, the commit SHA,
and whether the push succeeded. If all five pass, the §2 rule 3 argument. And anything the brief got
wrong — briefs in this phase have been wrong twice and both times the implementer caught it.
