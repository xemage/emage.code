# Checkpoint 003 — Agent-Team Test Suite

**Date:** 2025-11-24
**Phase:** Quality Assurance — automated framework integrity & team-health monitoring
**Branch landed on:** `develop` (MR !2, squash-merged)
**Pipeline:** [#2515111140](https://gitlab.com/em-age/emage.code/-/pipelines/2515111140) — all 4 jobs green

## Goal

Build a test suite that detects two distinct classes of regression:

1. **Structural regressions** — broken schemas, dead cross-references, sync determinism, link rot, accidentally-committed secrets.
2. **Agent-team-health drift** — symptoms of the orchestrator losing the big picture: tasks that don't trace to plans, lifecycle-state violations, missing checkpoints, decay in commit-message discipline.

## Delivered

### Test scaffolding (`tests/`)
- Stdlib `unittest` only — no pytest (PEP 668 blocks pip on system Python). Single entry point: `python3 tests/run.py [--suite functional|performance] [-v]`.
- `tests/_helpers/`: `repo.py` (path helpers + canonical lists of agents/skills/commands/manifests), `frontmatter.py` (YAML frontmatter parsing without PyYAML dep), `tokens.py` (4-chars-per-token estimator).
- `tests/_baselines/sync-timings.json`: configurable budgets (sync ≤10s, verify ≤5s, agent ≤32k chars / ≤8k est. tokens, skill ≤24k / ≤6k, conventional-commit ratio threshold 0.6).

### Functional suite (`tests/functional/`) — hard CI gates
- **`test_schemas.py`** — every agent/skill/command/instruction validates against its JSON schema; agent name slug == filename; skill name == directory.
- **`test_cross_references.py`** — `agents:` lists resolve; `mcp__<server>` tool refs map to `mcp/servers.yaml`; orchestrator delegates to every must-know specialist; no orphan agents.
- **`test_manifests.py`** — every platform manifest has the required keys; `outputDir` is relative; `extras[].from` paths exist.
- **`test_sync_determinism.py`** — runs `sync.mjs` twice in a temp copy and asserts byte-identical output (catches non-deterministic ordering / timestamps).
- **`test_secret_scan.py`** — `git ls-files` scan for GitLab/GitHub/AWS/OpenAI/Slack/Google/private-key patterns. Allowlist for known false positives.
- **`test_link_integrity.py`** — same logic as the existing CI lint stage but as a unit test (so failures land in the test stage, not in `allow_failure: true` lint).

### Performance / team-health suite (`tests/performance/`)
- **`test_sync_perf.py`** — wall-clock budgets for `sync.mjs` and `verify.mjs`.
- **`test_agent_token_budget.py`** — per-agent and per-skill char/token caps. Prints a top-5 size profile every run so prompt bloat is visible in CI logs.
- **`test_team_health.py`** — four early-warning checks:
  - **Lifecycle integrity** (hard) — task statuses ∈ `{pending,in_progress,blocked,in_review,done,cancelled}`; priorities ∈ `{P0,P1,P2}`; no `done` tasks left in active queue; owners are real agents; IDs unique and well-formed.
  - **Plan coverage** (hard) — every active task ID must appear in some `docs/plans/plan-*.md`. The signal we explicitly want: orchestrator improvising tasks without writing them down.
  - **Checkpoint cadence** (warning) — flags when active tasks exist but `docs/checkpoints/` is empty.
  - **Conventional-commit ratio** (warning) — `git log -n 20`, prints offending subjects when ratio drops below threshold.

### Wire-up
- **`Makefile`** — `make test`, `test-functional`, `test-performance`, `sync`, `verify`, `wiki-sync`.
- **`.gitlab-ci.yml`** — new `test` stage between `lint` and `verify`; `unit-tests` job runs `python3 tests/run.py` on `python:3.12-alpine` with `nodejs git pyyaml jsonschema`.

## Real findings the suite caught (and fixed in the same MR)

1. **`agent.schema.json` gap** — 25 of 27 agents declared a `user-invocable: false` field, but the schema's `additionalProperties: false` rejected it. Field added to the schema as an optional boolean.
2. **`technology-scout` name mismatch** — frontmatter `name:` was `"Technology Scouting Agent"` (slug `technology-scouting-agent`) but the filename and every cross-reference used `technology-scout`. Renamed; mirrors regenerated.
3. **v1 secret-scan false positive** — `v1/implementation/.opencode/QUICKSTART.md` contains a placeholder `glpat-xxxxxxxxxxxxxxxxxxxx` example. Allowlisted with rationale (v1 is frozen).

## Test results

```
Ran 32 tests in 2.7s
OK (skipped=1)
```

The single skip is the **plan-coverage** test, which is correctly waiting for the first real (non-template) task to land in `docs/tasks/active-tasks.md`. As soon as the orchestrator starts a real workstream, the test will start enforcing that every active task ID is referenced in `docs/plans/plan-*.md`.

### Size profile (current top 5)
| Agent | chars | est. tokens |
|---|---:|---:|
| orchestrator | 9,144 | 2,286 |
| security-engineer | 7,881 | 1,970 |
| devops-engineer | 7,176 | 1,794 |
| release-manager | 7,133 | 1,783 |
| ux-designer | 6,762 | 1,690 |

All comfortably inside the 32k-char / 8k-token budget.

### Conventional-commit ratio
`5/7 (71%)` of the last 7 commits — above the 60% threshold.

## What this gives the orchestrator

A **test stage** that fails the pipeline when:
- Someone edits an agent file in a way that breaks schema or cross-references.
- Someone marks a task `done` in `active-tasks.md` instead of moving it.
- Someone assigns a task to a non-existent agent.
- Someone writes an active task without recording the plan that owns it.
- Someone introduces an undeclared `mcp__<server>` tool reference.
- Someone accidentally commits a real-looking token.
- An agent prompt grows beyond its budget.

…plus warnings (in CI logs) for checkpoint cadence and commit-format decay.

## Next steps (open)

- When a real workstream begins, write `docs/plans/plan-001-*.md` first, then add tasks. Plan-coverage test will start enforcing automatically.
- Consider raising `min_conventional_commit_ratio` from 0.6 → 0.8 once the contribution rhythm is established.
- Consider splitting `orchestrator.md` (longest at 9.1k chars) if it approaches the 32k budget after future feature additions.

## Files added/modified

- New: `tests/` (16 files), `Makefile`
- Modified: `.gitlab-ci.yml` (added `test` stage), `v2/implementation/knowledge/schemas/agent.schema.json` (+ `user-invocable`), `v2/implementation/knowledge/agents/technology-scout.md` (name fix), 4 platform mirrors regenerated.
