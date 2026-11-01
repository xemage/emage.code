# T688 — qa-engineer no longer reads raw CI job traces (SEC-T660-02)

**ID:** T688
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T687
**Affects:** —
**Created:** 2026-10-23
**Completed:** 2026-10-23
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-23: T688)
- `docs/artifacts/tracked-debt-register-v2.md` (SEC-T660-02, decision D-1), `docs/artifacts/security-review-t660-gitlab-grants-v1.md`
- The user's decision of 2026-10-23 (AskUserQuestion, label verbatim): "Drop the tool from qa-engineer (Recommended)"

## 1. What and why

Drop `mcp__gitlab__get_pipeline_job_output` (the last 1000 lines of a raw CI job trace; SEC-T660-02: traces can hold unmasked secrets and attacker-influenced text that the model may copy into a bug issue) from `qa-engineer`. `qa-engineer` goes from 20 to 19 GitLab tools; it was the only agent that read raw job output. Edit the knowledge source `implementation/knowledge/agents/qa-engineer.md` (the tools line, and a body line telling QA not to ask for or paste raw job traces: ask the user for the failing job's relevant log excerpt, after the user has checked it for secrets, and never copy trace text into an issue verbatim), regenerate (`node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py`), and update everything that pins the count or the name: `tests/functional/test_mcp_package_pins.py` (the qa-engineer grant set and any "only qa-engineer reads raw job output" assertion), `tests/functional/test_mcp_grant_pins.py`, `tests/functional/test_gitlab_*` documentation tests, the documented counts and sentences in `AGENTS.md`, `implementation/AGENTS.md`, `implementation/PREREQUISITES.md` and `docs/wiki/mcp-servers.md` ("qa-engineer (20 tools ...)" becomes 19, the sentence "only qa-engineer reads raw job output" is replaced by "no agent reads raw job output (T688)"; keep the pinned structure of those paragraphs, each GitLab-grants paragraph stays one line), the GitLab tool snapshot `tests/_baselines/gitlab-mcp-tool-names.json` only if it lists grants (it lists the server's 275 tool names: do not change it). Declare the root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared 2026-10-23 by T688 (`); do NOT refresh the root install (T679 does, afterwards). Historical records (artifacts, checkpoints, releases, ADRs, completed briefs) stay untouched. *Acceptance:* the tool is gone from every projection of qa-engineer, the counts are consistent everywhere, all gates and the suite pass, a Security Engineer read follows.

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
