# `tests/golden/` — practitioner guide

Full design rationale: `docs/artifacts/golden-suite-format-v1.md`. This file is the short,
task-oriented version for anyone adding or running a case.

## What this suite is

A directory-per-case suite that checks whether emage.code's five commands (`/new-feature`,
`/code-review`, `/plan`, `/security-audit`, `/prepare-release`) actually produce output that
respects their own declared contract — required sections, required VERDICT fields, protected-path
respect, artifact-versioning conventions. It is **not** a live-capability benchmark (that's
Terminal-Bench, see `docs/benchmarks/`) and it does **not** use an LLM to grade anything. Every
case is binary pass/fail, decided by a plain Python script.

## Adding a case

1. Pick a case id (short, kebab-case, unique within the suite) and create
   `tests/golden/<case-id>/`.
2. Add `brief.md` — the task/prompt a user or agent would be given. This documents intent; it is
   not executed live as part of the automated suite run.
3. Add `fixture/` — the starting repo/workspace state the case needs, and/or the pre-authored
   "correct end state" your `expect.py` will check against.
4. Add `expect.py` with a `check(case_dir: Path) -> bool` function (see the format spec §4 for the
   full contract and purity rules — no network calls, no live model calls, no time/env/random
   dependence, don't mutate the checked-in `fixture/`).
5. Add `case.yaml`:
   ```yaml
   id: <case-id>
   command: /new-feature   # or whichever of the five this case targets
   status: expected_pass   # or known_failing
   tags: []
   ```
6. Use `tests/golden/_example-scaffold/` as a minimal worked reference — it is not a real case and
   is excluded from discovery/scoring, but its `expect.py`/`case.yaml`/`brief.md`/`fixture/` shape
   is exactly what a real case's shape should be.

## How a case is scored

`scripts/scorecard.py` (T413, not yet built at the time this README was written) will discover
every case by recursively finding `expect.py` files under `tests/golden/` (excluding any path
component starting with `_`), import each one, and call `check(case_dir)`. The result is binary:
`True` = pass, `False` = fail. There is no partial credit and no model-judged score anywhere in
this suite.

You can run a single case's check manually while authoring it:

```bash
python3 tests/golden/<case-id>/expect.py tests/golden/<case-id>
# exits 0 on pass, 1 on fail
```

## What "known-failing" means and how to mark it

Set `status: known_failing` in `case.yaml` when a case is expected to fail *today* — i.e. you
authored it against the command's declared contract, ran it, and it currently fails. This is
different from a case that starts at `expected_pass` and later starts failing (that's a
regression, not a known-failing case). Two sub-flavors, set via `known_failing_category`:

- `tracked_defect` — a known, expected-to-be-fixed bug. Explain what's broken in
  `known_failing_reason` (and reference a task id if one exists).
- `capability_gap` — a deliberate demonstration that the command surface doesn't support
  something yet, not necessarily on a near-term fix path. Explain the gap in
  `known_failing_reason`.

T411 requires at least 5 `known_failing` cases across the 20-case suite at authoring time (a
20/20-passing baseline means the suite is too easy — see plan-035 §2.4 Phase 1's risk table).

## `open/` vs `held-out/`

Built by T412. Cases live under `tests/golden/open/<case-id>/` (14 cases) or
`tests/golden/held-out/<case-id>/` (6 cases) instead of directly under `tests/golden/<case-id>/` —
the per-case contract above (`brief.md`/`fixture/`/`expect.py`/`case.yaml`) did not change; only
the parent directory did (a pure directory move, verified byte-identical against the pre-move
commit). See `tests/golden/_manifest-t411.md`'s "`open`/`held-out` split (T412)" section for the
exact case list and the reasoning behind which 6 were held out.

`held-out/` cases must never be referenced — by path string, file read, import, or doc mention —
from any file outside `tests/golden/held-out/` itself. This is enforced by a static repo-wide
guard, `tests/functional/test_golden_held_out_isolation.py` (mirrors the pattern in
`tests/functional/test_link_integrity.py` and `tests/functional/test_check_version_consistency.py`).
`scripts/scorecard.py` (T413) is the one documented exception — it's expected to execute both
`open/` and `held-out/` cases as its whole job, so it's allowlisted by path in the guard. See that
test file's module docstring for the full allowlist rationale.

## Protected paths

Per plan-035 T416 (not yet executed at the time of writing), `tests/golden/` and
`scripts/scorecard.py` are intended to become protected/read-only paths for every agent
definition once the evaluator interface is frozen. Until T416 lands, treat this suite as
architecturally sensitive: changes to `expect.py` contracts or case pass conditions should not be
made casually, since they retroactively redefine what "passing" meant for prior scorecards.
