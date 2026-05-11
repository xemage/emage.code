# Agent-Team Tests

Functional and performance tests for the emage.code multi-agent framework.
Designed to detect:

- **Schema drift** — agent/skill/command/instruction frontmatter no longer matches the JSON schemas
- **Cross-reference rot** — orchestrator delegating to non-existent agents, agents requesting MCP tools that aren't registered
- **Sync regressions** — non-deterministic generator output, missing platform mirrors, drift from `knowledge/`
- **Secret leaks** — committed PATs, AWS keys, etc.
- **Performance regressions** — sync engine slowing down past baseline
- **Agent context bloat** — individual agent prompts growing past the token budget
- **Plan drift** — tasks appearing without a corresponding plan; tasks losing trace back to the big-picture goal
- **Lifecycle violations** — invalid task statuses, completed tasks left in active queue
- **Process erosion** — phase boundaries crossed without checkpoints; commits not following Conventional Commits

> **No external dependencies.** Tests use `unittest` from the stdlib plus
> `PyYAML` and `jsonschema` (both Python-stdlib-adjacent and pre-installed in
> the CI image). This keeps the test job to a single `python3 tests/run.py`.

## Layout

```
tests/
├── README.md                       (this file)
├── run.py                          ← single entry point used by CI and Make
├── _baselines/                     ← performance baselines (committed)
│   └── sync-timings.json
├── _helpers/                       ← shared test utilities
│   ├── __init__.py
│   ├── frontmatter.py              parse/validate YAML frontmatter
│   ├── tokens.py                   rough character→token estimator
│   └── repo.py                     repo-root discovery, file walkers
├── functional/
│   ├── test_schemas.py             frontmatter ↔ JSON schema
│   ├── test_cross_references.py    agents/tools/MCP-server references resolve
│   ├── test_manifests.py           platform manifests are valid
│   ├── test_sync_determinism.py    sync.mjs is idempotent (already covered by CI; quick local check)
│   ├── test_secret_scan.py         no secrets in tracked files
│   └── test_link_integrity.py      no broken intra-repo markdown links
└── performance/
    ├── test_sync_perf.py           sync.mjs and verify.mjs runtime budgets
    ├── test_agent_token_budget.py  per-agent body fits in context budget
    └── test_team_health.py         plan-drift, lifecycle, checkpoint cadence
```

## Running

```bash
# All tests
make test
# or
python3 tests/run.py

# Just functional
python3 tests/run.py --suite functional

# Just performance
python3 tests/run.py --suite performance

# Verbose
python3 tests/run.py -v

# Single test file
python3 -m unittest tests.functional.test_schemas
```

## CI

The `test` stage in [`.gitlab-ci.yml`](../.gitlab-ci.yml) runs `python3 tests/run.py`
in parallel with `verify-knowledge-drift`. A failure blocks the pipeline.

## Performance baselines

`tests/_baselines/sync-timings.json` stores expected timing budgets:

```json
{
  "sync_max_seconds": 5.0,
  "verify_max_seconds": 2.0,
  "agent_max_chars": 32000,
  "agent_max_estimated_tokens": 8000
}
```

Adjust these (with justification in the MR description) when intentional growth
makes the previous budget too tight.

## What "agent-team health" means here

We **cannot** unit-test an LLM agent's reasoning quality. What we *can* test is
the scaffolding that prevents the team from drifting:

1. **Plan-drift detection** — every active task ID must trace back to a plan
   document under `docs/plans/` (or be tagged `hotfix`/`adhoc` in its row).
   If tasks appear without a plan, the orchestrator is improvising — that's a
   leading indicator of "lost the big picture".
2. **Lifecycle integrity** — task statuses are bounded by the documented set;
   no task transitions backwards (`done → in_progress`); no `done` task left
   in `active-tasks.md`.
3. **Checkpoint cadence** — at least one `docs/checkpoints/checkpoint-*.md`
   exists per phase boundary observed in the plan/task history (warning, not
   failure).
4. **Conventional-commit ratio** — % of last N commits that parse as
   Conventional Commits. Drops below the threshold = team has stopped using
   the agreed format = process erosion (warning, not failure).

These are deliberate **early warnings**, not pass/fail correctness checks.
