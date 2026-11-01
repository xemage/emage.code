# T686 — Release job on CI_JOB_TOKEN (WIKI_TOKEN only for wiki-sync)

**ID:** T686
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T685
**Affects:** —
**Created:** 2026-10-23
**Completed:** 2026-10-23
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-23: T686)
- `docs/artifacts/security-review-t685-supply-chain-residuals-v1.md` (the WIKI_TOKEN section)
- The user's decision of 2026-10-23 (AskUserQuestion, label verbatim): "Yes, create a task to switch (Recommended)"

## 1. What and why

Switch the release job to the GitLab job token (`docs/artifacts/security-review-t685-supply-chain-residuals-v1.md`, the WIKI_TOKEN section): `scripts/publish-release.py` gets a `--token-header` option with a fixed allowlist (`PRIVATE-TOKEN`, `JOB-TOKEN`; default `PRIVATE-TOKEN`) and `CI_JOB_TOKEN` is added to the names withheld from child processes; the host pin, the redirect refusal, the control-character check and the withheld-environment logic stay; `.gitlab-ci.yml`: the `release` job uses `--token-env CI_JOB_TOKEN --token-header JOB-TOKEN`; `WIKI_TOKEN` stays only for `wiki-sync`; tests with mutation proofs (the header name sent, the allowlist, no token in argv or logs, `CI_JOB_TOKEN` withheld from child processes); `CONTRIBUTING.md` and the pin-bump or release checklist: document that the pushing user needs the Developer role and permission to create the tag, that protected `v*` tags should be restricted to Maintainers, that `WIKI_TOKEN` must be a protected, masked variable with the minimum role, and keep the manual `glab release create` fallback until a real tag pipeline has confirmed the job token (unverified: whether job tokens work in tag pipelines on protected tags in this instance; the user rehearses it in a real tag pipeline). Do not change any token value or GitLab setting (those are the user\'s). *Acceptance:* the code and tests; all gates and the suite pass; a Security Engineer delta review follows.

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
