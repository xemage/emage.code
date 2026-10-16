# T525 — Golden-case coverage wave 1: four well-grounded commands

**ID:** T525
**Owner:** QA Engineer
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-09-25
**Completed:** 2026-09-25
**Based on:** `docs/plans/plan-072-phase9-golden-case-coverage.md`;
`docs/artifacts/golden-suite-format-v1.md` §2;
`docs/artifacts/command-promotion-readiness-v1.md` §3.2;
`docs/artifacts/protected-paths-v1.md` §5;
`docs/decisions/ADR-007-command-contract-authority.md` §5.

## 1. PROTECTED-PATH AUTHORIZATION — read first

**This task is explicitly authorized to create new case directories under `tests/golden/open/`, and
cites `docs/artifacts/protected-paths-v1.md` §5.2 as the reason that authorization is required.**

The authorization is **scoped to creation of exactly four new case directories**, one per command
below, each containing only `case.yaml`, `brief.md`, `expect.py` and `fixture/`:

| Command | May create |
|---|---|
| `/handoff` | one new directory under `tests/golden/open/` |
| `/validate-tasks` | one new directory under `tests/golden/open/` |
| `/discover-skills` | one new directory under `tests/golden/open/` |
| `/skillify` | one new directory under `tests/golden/open/` |

**Not authorized, and must not be touched:** `scripts/scorecard.py`; anything under
`tests/golden/held-out/`; **any existing case directory** under `tests/golden/open/`; any command
file under `implementation/knowledge/commands/`; any `maturity:` field.

`protected-paths-v1.md` §5.1 forbids you from extending this grant. If you conclude more is needed,
**stop and report a blocker** — do not edit this table. `T520` and `T523` both hit that boundary and
both correctly refused; that is the standard.

## 2. The evaluator-hash baseline — expected to fail, and NOT yours to fix

**Your change will drift the `tests_golden` evaluator-hash digest and turn exactly two tests red:**

```
tests/functional/test_golden_harness_evaluator_hash.py::TestBuildKnownGoodPayload::test_matches_the_real_committed_known_good_reference
tests/functional/test_golden_harness_evaluator_hash.py::TestRealRepoNoDrift::test_no_drift_against_real_current_repo_state
```

This is a **known, expected consequence of any authorized `tests/golden/**` change** — it happened
in `T520` and again in `T523`. It is stated here so you do not have to discover it.

**Do not fix it.** `docs/artifacts/` is not a protected path, so you could argue the refresh is in
scope. It is not. Refreshing a tamper-evidence baseline is the one action that control exists to
stop an actor doing to itself. Instead:

1. Recompute the digests read-only — `golden_harness.evaluator_hash.compute_current_digests(Path('.'))`
   performs no writes.
2. Report both values, and the value each differs from in `evaluator-hash-known-good-v3.json`.
3. Stop. The orchestrator surfaces it and the user authorizes the new baseline.

`scripts_scorecard` must come back **byte-identical** to v3. If it does not, you touched something
you should not have — say so plainly.

## 3. What to author

One case per command, four total. Each is a directory under `tests/golden/open/` named
`<command>-<what-it-checks>`, matching the existing naming convention, containing:

- **`case.yaml`** — `id`, `command`, `status`, `tags`. Read three existing `case.yaml` files first.
- **`brief.md`** — follow the shape of `tests/golden/open/new-feature-plan-doc-compliant/brief.md`:
  `## Command under test`, `## Brief (illustrative — not executed live)`, `## What this checks`,
  `## Pass condition`, `## Provenance`.
- **`expect.py`** — a `check(case_dir: Path) -> bool` plus a `main()`, matching the existing files.
  **It must be a pure function of `case_dir`**: no `__file__` anchoring, no hardcoded absolute
  paths, no network, and **never a live model call** (`golden-suite-format-v1.md` §2.2).
- **`fixture/`** — the repo state the check runs against.

### Grounding, per command

| Command | Grounding available |
|---|---|
| `/handoff` | **Strongest.** Two real `docs/checkpoints/handoff-*.{json,md}` pairs exist, plus `implementation/runtime/handoff/schema-v1.json` and a validator. Prefer a real artifact copied verbatim. |
| `/validate-tasks` | A real validator with deterministic output and a real ledger to run against. |
| `/discover-skills` | A real skills corpus under `implementation/knowledge/skills/`. |
| `/skillify` | Same corpus; real `SKILL.md` files to check shape against. |

## 4. The three rules that make a case real

1. **Quote the clause.** `brief.md`'s `## What this checks` must quote the **specific** step or
   clause of `implementation/knowledge/commands/<name>.md` under test — verbatim, with the phase
   and step number, exactly as the existing 14 cases do. A case that cannot name its clause is not
   a case; report a blocker instead of inventing one.
2. **A `known_failing` case is a correct outcome.** If the honest check against real corpus comes
   out red, ship it red with `status: known_failing`, a `known_failing_category` and a
   `known_failing_reason` stating the corpus survey. **That command then does not promote, and that
   is the right answer.** `ADR-007` §5 — never resolve by relaxing a check — binds authoring
   exactly as it binds fixing. Do not weaken a check to get a green.
3. **Four green is a suspicious result, not a target.** You are not being measured on how many
   pass. `T515` faced the same framing and its honest answer was 2 green of 6. If all four pass,
   say explicitly in your report why you believe that is genuine rather than an artifact of
   checks that are too weak to fail.

If a command's declared contract is too vague to check deterministically, **that is a finding worth
more than a case**: report it as a blocker with the specific ambiguity, and author the other three.

## 5. Verification

Run all of these from your worktree and report verbatim output:

```
python3 scripts/scorecard.py                    # read it first; do not modify it
python3 -m pytest tests/functional/test_golden_held_out_isolation.py -q
python3 tests/run.py
python3 implementation/scripts/check-maturity.py --root implementation
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Run `python3 tests/run.py` — the full suite, 774 tests — not `pytest tests/functional` (734).**
The 40-test difference contains guards that have already broken one MR in this phase.

Expected on `develop` @ `8a131a8`, so you can tell a regression from an expected consequence:
- `tests/run.py` → `774 tests`, `OK (skipped=23)` **before** your change; **after**, exactly the 2
  evaluator-hash failures from §2 and **nothing else**. Any third failure is yours to explain.
  Measure the baseline yourself first.
- `check-maturity.py` → `79 components checked, 0 failing`. **The distribution must not change** —
  new cases do not promote anything, and criterion 4 is evaluated against case files, so a new
  `expected_pass` case does not by itself move a component whose `maturity:` you have not touched.
- `validate-tasks.py` → `PASS`.

Also call each new `check()` directly against its own fixture and report the boolean, rather than
inferring it from the scorecard.

## 6. Ledger

Set this brief's `**Status:**` to `in_review`. **Do not** move any row to `completed-tasks.md` and
do not remove the `T525` row from `active-tasks.md` — archival is orchestrator-only.

## 7. Git

Branch `agent/qa-engineer/T525`, already created off `develop`. Conventional Commits message ending
with exactly:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

Push to `origin`. **If the push fails** with `glab auth git-credential: "erase" is an invalid
operation` and/or `HTTP Basic: Access denied`, that is a known recurring environment transient
affecting only the git-over-HTTPS credential path. It is **not your fault**, the credentials are
**not** broken, and you must **not** touch any `glab` or `git config credential.*` setting. Retry
two or three times, then report that the commit is on the local branch; the orchestrator has a
working fallback.

**Do not open a merge request and do not merge anything.** No self-merge, no exceptions.

## 8. Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). Max 2 retries, then escalate. Never widen the §1
authorization table — report instead. A brief that turns out to be wrong is a useful finding, and
briefs in this phase have been wrong twice; say so rather than working around it.
