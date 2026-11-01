# T712 — Brave: force stdio and acceptance v3

**ID:** T712
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T702
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-124-release-v9.md` (task T712, Addendum of 2026-11-01)
- The user's answers of 2026-11-01 (AskUserQuestion, verbatim option labels): "Approve (Recommended)"; "Yes, in v9.0.0 (Recommended)"; "Decide after T702 (Recommended)"; "Yes, rehearse (Recommended)"
- `docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

**T712** (devops-engineer): add `--transport stdio` to the shipped `brave` launch arguments, with the pin test requiring exactly that form; regenerate the mirrors and the registry and declare the root drift; write `docs/artifacts/brave-audit-acceptance-v3.md` (the seven advisories, the user's words, expiry, conditions, the gate command); update the gate command in `docs/wiki/mcp-pin-bump-checklist.md` and its test. *Acceptance:* `audit-mcp-pins.py audit --audit-level high` with exactly the seven v3 `--accept` entries passes; all gates and the suite pass; a Security Engineer review follows.

The user's words for the acceptance (AskUserQuestion of 2026-11-01, verbatim option label and its description): "Renew + force stdio (Recommended)" — "Accept as stated AND add '--transport stdio' to the shipped brave launch args (with its test) in v9.0.0, so no env var or .env file can switch it to HTTP. Changes the generated configs (one more root refresh before the release branch)." The question stated the scope: "all 7 advisories of @brave/brave-search-mcp-server@2.1.4 (6qxp, 22jm, 6prh, 46jr, rvq5, f897, mrhx), none reachable harmfully in stdio mode (Security Engineer). Expiry: the first Brave release above 2.1.4 or 2027-01-30, whichever is first (the script allows at most 90 days). Condition: stdio only, never the HTTP transport."

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
