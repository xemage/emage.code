# T708 — Tech Lead review by area v9.0.0

**ID:** T708
**Owner:** tech-lead
**Status:** in_progress
**Priority:** P1
**Tier:** standard
**Depends on:** T705
**Affects:** —
**Created:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T708)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

Tech Lead review by area (tech-lead, read-only): installer and generator; knowledge text and rulings; CI and release job; documentation. *Acceptance:* a verdict per area.

**Gate order (orchestrator, 2026-11-01, under `release-manager.md` § Release Gate Policy item 5):** T706 to T709 run first and do not edit `docs/releases/v9.0.0.md`. Then the release-manager fills the `## Gate Verdicts` lines except `Release:`; then the top-level session checks the document independently at that commit and records the check (the policy's "top-level session's own verification"); then T710 changes only the `## RELEASE VERDICT` section and the `Release:` line.

T708 also reviews T704's test change `2f2cd4db` (the v8.0.0 gate tests run with the marker check patched out) and reads the release document for technical accuracy by area; it is not the Policy item 5 check.

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
