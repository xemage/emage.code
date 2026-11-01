# T680 — Pi MCP placeholders: verify the adapter and support optional variables (SEC-T665-09)

**ID:** T680
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T665
**Affects:** —
**Created:** 2026-10-22
**Completed:** 2026-10-22
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T680)
- `docs/artifacts/security-review-t665-token-handling-v1.md` (SEC-T665-09), `implementation/PREREQUISITES.md` ("GitLab token", the Pi row)

## 1. What and why

The T665 review (SEC-T665-09) and the developer found that the generated Pi `gitlab` entry cannot work as generated: Pi (source read on main, commit 698a2d2, not run) throws for any unset or empty referenced variable and keeps `${env:VAR}` as literal text, and the new optional `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` placeholder adds to it. First establish, from the Pi adapter actually used by this project's Pi support (installed release, not main), which placeholder forms it expands and how it treats an unset or empty variable; do not rely on source reading alone where a run is possible and say what remains unverified. Then give the generator a capability to mark a variable optional (omit the entry or render the platform's optional form) and switch Pi to the verified form for every server; keep the other platforms unchanged. Update the Pi rows in `PREREQUISITES.md` and the wiki to the verified status. *Acceptance:* a verified-forms table for Pi in the docs; generator and install-merge tests; all gates and the suite pass; a Security Engineer review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; do not modify `tests/golden/**`. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never use or print a real token. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
