# T725 — Batch A: implement audience for commands (TD-T671-P5)

**ID:** T725
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T723
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-128-batch-a-installer-generator.md` (task T725)
- The user's answer of 2026-11-02, verbatim: "A go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch A rows; descriptions in v1 to v3)

## 1. What and why

(devops-engineer), **TD-T671-P5**: implement `audience:` for commands. Today one command, `/prepare-release`, declares `audience: authoring`; 18 declare `both`. A target project should not receive an authoring-only command.
   - Design the filter first, and state it in the closing report. Where does it apply: the generator, the installer, or both? How is an authoring checkout recognised? The existing test `tests/functional/test_command_audience_paths.py` and the `/discover-skills` rule already use the presence of the registry file. What happens to an existing installed copy on `--update`? What happens in the root install of this repository, which is an authoring checkout?
   - Implement it with tests, and record the user-visible change (targets no longer receive `/prepare-release`) as a migration item for the next release document. Depends on T723, because both change `install.sh`.
   - *Acceptance:* a target install has no authoring-only command on any platform; the root install keeps it; `--update` removes a stale copy (or the report says why not); all gates and the suite pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

A target install has no authoring-only command on any platform; the root install keeps it; `--update` removes a stale copy (or the report says why not); all gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
