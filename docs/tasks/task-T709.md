# T709 — Release-level security re-check v9.0.0

**ID:** T709
**Owner:** security-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T702, T705
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T709)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

Release-level security re-check (security-engineer, read-only): the delta since T650 (plan-123, T689 to T699, T701, T703) and T702's result; confirms SEC-T662-01 closed and that no `HIGH` or `CRITICAL` is open. *Acceptance:* a verdict; any `CRITICAL` or `HIGH` blocks.

**Condition from `security-review-t701-t703-wave1-v1.md` (SEC-T703-01):** check the content of the Cursor migration item in `docs/releases/v9.0.0.md` by hand against SEC-T662-01 before declaring it closed.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>` (release-manager tasks: on `release/v9.0.0` through the orchestrator); Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
