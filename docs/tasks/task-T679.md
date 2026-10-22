# T679 — Cursor removal step S3: root refresh (ADR-010)

**ID:** T679
**Owner:** orchestrator
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T678
**Affects:** —
**Created:** 2026-10-16
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-16: T679)
- `docs/decisions/ADR-010-drop-cursor-platform-support.md` (accepted 2026-10-16), `docs/artifacts/cursor-removal-inventory-v1.md`
- The user's decisions of 2026-10-16 (AskUserQuestion, verbatim option labels): "v9.0.0 (MAJOR), no deprecation release (Recommended)", "B: error plus read-only notice, never delete (Recommended)", "Yes, delete both trees (Recommended)", "Accept all four defaults (Recommended)"

## 1. What and why

Step S3 of ADR-010: `scripts/install.sh --target <clean worktree> --platform all --projections-only` on the tip of T678 (touch the sources' mtimes first in a fresh worktree: rsync's quick check skips equal-size files), empty the drift list in `tests/_baselines/root-install-drift.json` and add the 'Emptied' line. Needs the user's explicit approval at that step. Acceptance: `python3 -m tests.functional.test_root_install_parity --print-drift` prints `[]`; the suite passes; `git status` shows no `.cursor` path; no file under `docs/` or `implementation/` changed by the refresh.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 3a. Carried from the T678 review

- SEC-T678-03: the v9.0.0 migration item must say that a leftover `.cursor/` in an adopter project is no longer updated and that its agents are not tool-restricted (every agent can call every tool of every configured server there).

- T672 (v9.0.0 migration item, SEC-T672-06): a plain install over an existing config now MERGES (as `--update` did) instead of overwriting; when there is no provenance sidecar the installer prints `merge-mcp-json: note: <dest>: there is no provenance sidecar at <old-sidecar>, so no retired generator entry could be pruned; kept your server(s) a, b, which the generated config does not contain. If one is a retired generator entry, remove it by hand or run scripts/merge-mcp-json.py with --force-prune-keys <name>.`; new on-disk names: `.<name>.<random>.tmp`, `<ledger>.bak`, `<tree>.emage-new.<pid>` / `.emage-old.<pid>`.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
