# T550 — `install.sh` has no projections-only refresh mode for the repo root

**ID:** T550
**Owner:** DevOps Engineer
**Status:** pending
**Priority:** P1
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-09-30
**Based on:** `docs/plans/plan-082-root-refresh-and-followups.md` §1;
`docs/artifacts/root-projection-resolution-v1.md` §5–§6; `docs/tasks/task-T543.md`;
`scripts/install.sh`; `tests/functional/test_root_install_parity.py`.

## 1. Why this is P1

The repo-root platform trees are the live runtime of every agent in this repository, and they are
stale. Two consequences are verified and live **today**:

- Root `.claude/agents/orchestrator.md` lines 96–97 still say *"Docs (docs) → commit directly to
  develop (docs-only changes exempt)"* and the same for chore. T542 removed that from source on
  2026-09-26. **`@orchestrator` run in this repo reads an instruction to push to a protected branch.**
- Root `/consolidate-memory` projections still carry the step 5 that T549 (MR !419) removed from
  source: *append to `AGENTS.md`, then remove from memory* — the data-loss instruction.

T543 added a gate that **detects** this drift (declared list in
`tests/_baselines/root-install-drift.json`). It deliberately does not **cure** it, because the cure
needs a root refresh, and **the only refresh path `install.sh` permits at the repository root is
`--update`**, which runs the full install including the `docs/tasks` ledger merge.

That is not a theoretical risk. **The most recent root refresh, `fee245a` on 2026-09-19, took
`docs/tasks/active-tasks.md` from 2460 lines to 11** (2451 deletions); `e44c98a` repaired it the same
day. Both commits verified by the orchestrator.

`**Affects:** —` is correct: `install.sh` is not a registry component, so this P1 row blocks no
promotion and cannot turn `check.py --maturity` red. (Verified empirically in `plan-081` §1: a P1 row
naming a `stable` component exits 1 and blocks every merge; `—` does not.)

## 2. What to build

An **opt-in** mode of `scripts/install.sh` that refreshes **only the derived harness** — the platform
projection trees, and whatever else a fresh `--platform all` install renders into the root that the
T543 parity gate compares — and touches **nothing the project owns**.

It must **never**:

- write, merge or normalise anything under `docs/` — in particular `docs/tasks/active-tasks.md` and
  `docs/tasks/completed-tasks.md`;
- delete `.claude/settings.json` or `.claude/settings.local.json`, or any other path in
  `CLAUDE_LOCAL_PATHS`, `GITHUB_LOCAL_PATHS`, or the per-platform MCP carve-outs;
- change the behaviour of any **existing** invocation. The default install and `--update` must stay
  byte-for-byte the same in what they write. Every installed target uses this script.

Decide, and argue in the artifact:

1. **The flag's name and contract** (e.g. `--projections-only`). Whether it is permitted at the
   repository root without `--update` — the refusal at `install.sh` lines ~76–88 exists for a reason;
   state what that reason is and why the new mode does or does not violate it.
2. **Exactly which install functions it runs and which it skips.** Enumerate them by name. Read
   `install_common`, `install_docs`, the ledger-merge path, `install_mcp_server_runtime`,
   `install_agents_doc`, and every `install_<platform>` before deciding.
3. **Whether `AGENTS.md`, `CLAUDE.md` and the MCP configs are in scope.** The T543 gate compares them;
   T543 measured 0 drift in all of them today. Decide whether the mode refreshes them and say why.

## 3. How to prove it — against copies, never the real root

**Do not run the new mode, or `--update`, against this repository's root.** Not to test, not in a
dry run you then "just confirm". The refresh of the real root is a **separate, human-approved step**
the orchestrator performs after this task merges (see `plan-082` §2).

Build the proof in `tests/functional/` against temporary directories, in the style of
`test_root_install_parity.py` and `test_install_agents_mapping.py`:

- Construct a synthetic stale root: a fresh install, then mutate some projections, **plus** a
  non-trivial `docs/tasks/active-tasks.md`, a `docs/tasks/completed-tasks.md`, a
  `.claude/settings.json`, a `.claude/settings.local.json`, and a `.github/workflows/` file.
- Run the new mode against it.
- Assert: every project-owned file is **byte-identical** afterwards; every mutated projection now
  matches a fresh install; the T543 comparison (`compute_drift`) reports **zero** drift.
- Assert the ledger survives **specifically**. It is the failure that already happened once.

CI's `unit-tests` job is `python:3.12-alpine` with `apk add bash` and **no `rsync`**, so `install.sh`
takes its `cp` fallback there. Test both paths — the T543 implementer hid `rsync` from `PATH` to do it.

## 4. Constraints

- **Write scope:** `scripts/install.sh`, new files under `tests/functional/`, and
  `docs/artifacts/root-refresh-mode-v1.md` (the decision artifact). Nothing else.
- **Do not edit `tests/_baselines/root-install-drift.json`.** This task changes no knowledge and no
  projection, so the declared list must not move. If it does, something is wrong — report it.
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** No authorization.
- **`implementation/**` is out of scope.** If the right design needs a change there, report it.
- Hand back **uncommitted**. The orchestrator verifies independently and commits.

## 5. Verification — run all, report real output

Measure every figure yourself.

- `python3 tests/run.py` — a `unittest` wrapper. The signal is the **exit code** plus the `Ran N`
  / `OK` lines on stderr. Redirect to a file; **do not pipe to `tail` and read `$?`.**
- `python3 -m tests.functional.test_root_install_parity --print-drift` — must be unchanged from the
  committed list.
- `python3 docs/tasks/validate-tasks.py`
- `python3 implementation/scripts/check-maturity.py --root implementation`
- `node implementation/scripts/sync.mjs --root implementation --check`
- `python3 implementation/scripts/generate-registry.py --check`
- `python3 scripts/scorecard.py --check` — never without `--check`.
- `git status` of **this worktree and the main checkout** before and after the full suite — both must
  be unchanged. The orchestrator will re-check this.

## 6. Acceptance criteria

1. The new mode exists, is opt-in, and every existing invocation is unchanged in what it writes.
2. §2's three decisions are argued in the artifact with functions named.
3. A test proves the ledger and every project-owned path survive the mode byte-for-byte, and that
   drift goes to zero, against a synthetic root — under both `rsync` and the `cp` fallback.
4. The real repository root was never refreshed by this task.
5. All §5 gates green, with real output.

## 7. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate. **Never silently fail.**

**If anything in this brief is wrong, report it rather than working around it.** Thirteen consecutive
tasks have found a defect in their brief. §2's function list and §3's claim about CI's `rsync` are the
likeliest places for the fourteenth.
