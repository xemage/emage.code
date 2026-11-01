# T704 — Open release/v9.0.0, version markers and stale lines

**ID:** T704
**Owner:** release-manager
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T700, T701, T712
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T704)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

Open `release/v9.0.0` from `develop` after wave 1 (a user-approved root refresh first if drift is not 0); bump the version markers and fix the stale lines and counts T700 lists (release-manager). *Acceptance:* `scripts/check-version-consistency.py` passes for v9.0.0.

The user's answers of 2026-11-01 on the T700 decisions (AskUserQuestion, verbatim option labels): D-T700-1 "Exclude docs/decisions/ (Recommended)" (add `docs/decisions/` to `EXCLUDED_PREFIXES` in `scripts/check-version-consistency.py`, with a test, as T642 did for `tests/golden/`); D-T700-2 "Fix in T704 (Recommended)" (correct the `--force-prune-keys` sentence at `scripts/install.sh:1300`, finding TL-T700-01, and its test pin at `tests/functional/test_install_cursor_removal.py:41-42`). Inputs: `docs/artifacts/release-v9-audit-v1.md` §4.

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
