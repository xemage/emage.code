# T705 — Write docs/releases/v9.0.0.md (closes SEC-T662-01)

**ID:** T705
**Owner:** release-manager
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T703, T704
**Affects:** —
**Created:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T705)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

Write `docs/releases/v9.0.0.md` from `docs/releases/_template.md` and T700 (release-manager): the Migration section with the Cursor item of ADR-010 Appendix A (M-9 steps, the v5.0.0 to v6.9.0 keys `e2b`, `redis`, `figma`, `notion` and `filesystem`, `--force-prune-keys` only from the `v8.0.0` tag, the Known Issue "a Cursor install left in a project is frozen and is not pruned", and SEC-T678-03: a leftover `.cursor/` is no longer updated and its agents are not tool-restricted) and every other item of T700; the restatement that the two Brave HIGH findings block the tag if their acceptance lapses (security review T697-T699). *Acceptance:* `verify-release-docs.py --tag v9.0.0` and the T703 check pass; SEC-T662-01 closed.

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
