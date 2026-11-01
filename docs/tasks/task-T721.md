# T721 — Batch D: pin the release-gate text (SEC-T693-08)

**ID:** T721
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T720
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-127-batch-d-knowledge-and-rulings.md` (task T721)
- The user's answer of 2026-11-01, verbatim: "D go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch D rows; descriptions in v1 to v3)

## 1. What and why

(devops-engineer), SEC-T693-08: `tests/functional/test_release_self_review_text.py` pins the release-gate text. It must also pin `release-manager.md:229` and `orchestrator.md:129` and the final T720 wording, and confirm the projection list. Depends on T720. *Acceptance:* the new pins fail on a broken copy of the text; all gates and the suite pass.

## 2. Output

The changes or artifacts stated in section 1, and a closing report: per id, done (file:line) or not done (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

The new pins fail on a broken copy of the text; all gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
