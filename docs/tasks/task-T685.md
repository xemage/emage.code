# T685 — Supply-chain residuals of the T676 review and register leftovers

**ID:** T685
**Owner:** devops-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T676
**Affects:** —
**Created:** 2026-10-22
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-22: T685)
- `docs/artifacts/security-review-t676-supply-chain-v1.md` (SEC-T676-11 to -14 and the open and unverified list), `docs/artifacts/brave-audit-acceptance-v1.md`
- The user's decisions of 2026-10-22 (AskUserQuestion, labels verbatim): "Accept with conditions (Recommended)" and "Remove GitHub MCP server"

## 1. What and why

Close the open items of the T676 review (`docs/artifacts/security-review-t676-supply-chain-v1.md`): SEC-T676-11 (`scripts/audit-mcp-pins.py --accept`: scope an acceptance to a package, `GHSA-...:YYYY-MM-DD:<package>@<version>` or a package-name check in `fully_accepted`, and reject a date more than 60 to 90 days from today; optionally read the id list and expiry from `docs/artifacts/brave-audit-acceptance-v1.md`), SEC-T676-12 (`test_publish_release_remainders.py`: `temp_repo` with two or three commits, one with a CR subject, asserting the exact list of subjects; consider U+034F and the Khmer inherent vowels U+17B4/17B5 in the unsafe class), SEC-T676-13 (two sentences in the `PREREQUISITES.md` and wiki upgrade note: a user-owned GitHub server is outside every generated denial on Opencode and Gemini CLI, so use a fine-grained read-only token; revoke or unset `GITHUB_PERSONAL_ACCESS_TOKEN` if you no longer use it), SEC-T676-14 (at the next lock regeneration use `--exclude-newer` seven days back), the ancestor check of the release tag (TL-T649-13 / QA-T648-03: compare the tag\'s tree with `origin/main`\'s tree, tested in a real tag pipeline; ancestry of the SHA gives false results for GitLab API merges and the gate fetches at depth 1), the `WIKI_TOKEN` question (report only: the release job could use `CI_JOB_TOKEN` with a `JOB-TOKEN` header option in `publish-release.py`; the Wiki API has no job-token support; the user decides before any change), and the knowledge templates that still show `node:20-alpine` and `alpine:3.19` as examples (`implementation/knowledge/agents/devops-engineer.md`, the ci-cd-pipeline skill: a knowledge edit, so the projections change). Every fix gets a test and a mutation proof. *Acceptance:* the items closed or reported; all gates and the suite pass; a Security Engineer delta review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
