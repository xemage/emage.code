# T700 — Release-level audit of v8.0.0..develop

**ID:** T700
**Owner:** tech-lead
**Status:** in_progress
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T700)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

Release-level audit of `v8.0.0..develop` (tech-lead, read-only, one artifact `docs/artifacts/release-v9-audit-v1.md`): breaking and behaviour changes; the Migration items (ADR-010 Appendix A with SEC-T662-01 and SEC-T678-03; T672 plain install merges; T676 GitHub server removed; T680 Pi placeholders; and, per decision D-13, T688 qa-engineer 20 to 19 GitLab tools, T689 the token file in memory by default, T690 two code-launching servers added to `.vscode/mcp.json` on `--update` (SEV-T690-07), T693 the release-gate input); Known issues (the v8.0.0 K-items still true and the register v3 items an adopter must know); the version markers and stale counts; the release job's readiness on `CI_JOB_TOKEN` (SEC-T686-03, SEC-T686-06). *Acceptance:* every merged task since v8.0.0 is classified (breaking / behaviour / internal), with file and line evidence or (unverified).

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
