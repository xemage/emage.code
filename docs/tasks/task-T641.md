# T641 — Release audit addendum v2 for v8.0.0 (audit C-9)

**ID:** T641
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** judgment
**Depends on:** T630, T631, T632, T633, T634, T635, T639, T640
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (dependency graph: node A2 "audit addendum release-v8-audit-v2"; wave 3 follows)
- `docs/artifacts/release-v8-audit-v1.md` (§5 open concerns C-1..C-9, §3 Migration draft, §4 Known issues draft, §6 what was not verified)
- The merged results of wave 1 and wave 2 on `develop` (`ac63dbe`): the artifacts listed in the ledger rows of T619-T640 in `docs/tasks/completed-tasks.md`

## 1. What and why

Produce the immutable artifact `docs/artifacts/release-v8-audit-v2.md` ("Based on: release-v8-audit-v1.md"). It re-runs the inventory against `develop` as it is now and resolves each open concern of v1 §5 (C-1..C-9) as `closed` (with evidence: file, command and result), `open` (with the owner and the step that closes it) or `moved to release preparation`. It must also: (a) list what changed since v1 (T619-T640 outcomes, in one table with the merge commit); (b) update the Migration section draft (v1 §3) and the Known issues draft (v1 §4) with the changes since v1: the MCP server entry changes (T638: filesystem, git, supabase, github replaced, docker and postgresql removed, pins and the pin-bump policy), the SEC-002 `@anthropic/mcp-filesystem` finding and an out-of-band fix note for existing v7.x installs, the `tech-lead` maturity change (experimental to stable; `orchestrator` remains experimental), the single release document and release order (T639), the release job change (T640: description = the release document; commit list to CHANGELOG.md only), the `--projections-only` installer flag and symlink guard (T636); (c) list the exact files that carry stale version claims for the marker bump (v1 C-1), re-measured by copying `git archive origin/develop` to the scratchpad (held-out excluded), bumping only the README marker, and running `scripts/check-version-consistency.py`; (d) state the tracked debt list that goes to Known issues (SEC-004..015 of T633, SEC-T6xx items, T636 L6/L7, T620 residuals, the update_changelog preamble placement) by reference to the security-review records; (e) re-run and record the gate numbers: `python3 tests/run.py` (redirected to a file), `scorecard.py --check`, `check-maturity.py --root implementation`, `sync.mjs --check`, `generate-registry.py --check`, `docs/tasks/validate-tasks.py`, `check-main-develop-drift.py`/`check-version-consistency.py` where runnable offline, evaluator hash; (f) record, as the release-sign-off conflict disclosure, that `tech-lead` (the Tech Lead review's executor) was itself promoted in this release and authored its own exit review (T625).

## 2. Output

`docs/artifacts/release-v8-audit-v2.md`; one local commit.

## 3. Constraints

- Work in your own worktree/branch (`agent/tech-lead/T641`); one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit ledgers, any brief's Status line, any file other than the one artifact. Read-only otherwise (you may run read-only commands and scratchpad copies).
- Do not decide anything that belongs to the user or the release manager (the counting rule for RELEASE VERDICT, the release version, the tag). Record such items as open with a recommendation.
- Never open `tests/golden/held-out/`; never write a held-out case id; run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on the artifact before the commit. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**; verified claims **(V)** with evidence.

## 4. Acceptance criteria

1. Every concern C-1..C-9 of v1 has a disposition with evidence.
2. The updated Migration and Known issues drafts are complete enough to paste into `docs/releases/v8.0.0.md`.
3. The artifact names the stale-version file list measured on current `develop`.
4. No held-out id; the isolation test passes.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
