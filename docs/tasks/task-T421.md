# Task T421 — Re-verify and close the `.claude`/`.github` MCP config gap

**ID:** T421
**Owner:** backend-developer
**Status:** pending
**Priority:** P1
**Depends on:** T420 (needs the finalized per-platform contract to check against)
**Created:** 2026-09-08
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 2 (T421 row; "re-verify this
gap still exists before starting; plan-033/034 may have already closed it"); `docs/plans/plan-037-
phase2-phase5-sequencing.md` ("Phase 2 kickoff finding" section).

This brief is self-contained. **Wait for `docs/artifacts/mcp-platform-contract-v1.md` (T420) to
exist before starting** — it is your primary input.

## Objective

Determine, with direct evidence, whether any real MCP-config projection gap currently exists for
the `.claude` or `.github` platform targets, and close it — either by fixing a genuine gap, or by
formally verifying and recording that no gap exists. Either outcome is an acceptable, complete
result for this task; do not manufacture a fix if your own independent check finds nothing broken.

## Context — this task's premise has already changed once before dispatch

plan-035 originally scoped T421 as "close the `.claude/` and `.github/` gaps identified in the
audit (no projected MCP config present)," with its own caveat that plan-033/034 might have already
closed this. plan-037 (the plan that dispatched this phase) went further and claimed a *specific*
live gap: that `.vscode/mcp.json` (the `github` platform's projection target) incorrectly includes
`brave` and `context7` because they're `extended`-tagged servers that shouldn't reach the `github`
platform.

**The orchestrator independently re-checked this claim before dispatching T421 and found it to be
wrong**, not merely already-fixed: `servers.yaml` tags `brave` and `context7` as `[core]` (not
`extended`), `implementation/platforms/github.json`'s manifest scopes `mcp.tags` to `["core"]`
(correctly), and `node scripts/sync.mjs --check` reports zero drift across all 7 platforms (557
files) on `develop` right now. The `cwso` entry also present in `.vscode/mcp.json` is intentional,
ADR-002-documented hand-added-key preservation (`scripts/merge-mcp-json.py`), not a gap. Full
detail is in `docs/tasks/active-tasks.md`'s Phase 2 dispatch note and in `task-T420.md`.

**Do not treat this as settled.** The orchestrator's check was a pre-dispatch sanity pass, not a
substitute for this task. Your job is to independently re-derive the same conclusion (or find that
it's wrong) using T420's finished contract doc as your reference, and to check breadth the
orchestrator's spot-check did not fully cover — specifically:

1. Does a genuine gap exist for **any** of the 7 platforms (not just `github`) between what
   `servers.yaml` says should be projected and what's actually in the checked-in projection file,
   right now on `develop`?
2. Does `.claude/` specifically have any gap — plan-035's original T421 wording named both
   `.claude/` and `.github/`, but plan-037's re-check only directly addressed `.vscode/mcp.json`
   (the `github` target). Check `.mcp.json` (the `claude-code` target, per `claude-code.json`'s
   manifest: `outputFile: "../.mcp.json"`, `tags: ["core", "extended"]`) with the same rigor.
3. Is there anything in the *provenance sidecar* mechanism (`*.provenance.json`, ADR-002) that
   could mask a real gap — e.g. a server retired from `servers.yaml` that should have been pruned
   from a projection but wasn't, or vice versa?

## Inputs

- `docs/artifacts/mcp-platform-contract-v1.md` (T420 output) — the authoritative per-platform
  contract; use this as your primary reference for "what should be true"
- `implementation/knowledge/mcp/servers.yaml`, `implementation/platforms/*.json`,
  `implementation/scripts/sync.mjs`, `scripts/merge-mcp-json.py` — same primary sources T420 used;
  re-derive independently rather than trusting T420's summary alone for anything you're about to
  change
- Live commands: `node implementation/scripts/sync.mjs --check` (unscoped and per-`--platform`),
  run from a clean `develop` checkout in your own worktree
- `docs/tasks/active-tasks.md` Phase 2 dispatch note (orchestrator's pre-check) and this brief's
  "Context" section above

## Expected outputs

One of two outcomes, both acceptable:

- **If a genuine gap is found:** the fix itself (likely in `servers.yaml`, a `platforms/*.json`
  manifest, or `sync.mjs`), plus regenerated projections via `node scripts/sync.mjs` (not
  `--check`) to materialize the fix, plus a written note in your completion report describing the
  gap, the fix, and the before/after `sync.mjs --check` evidence.
- **If no genuine gap is found:** a short verify-and-close note (can live in your MR description
  and completion report; no new artifact file is required) stating what was checked, what commands
  were run, and confirming zero drift with cited command output — i.e. do the same category of
  check `test_platform_projections.py`'s `test_platform_mcp_configs_have_expected_shape` and
  `test_remote_mcp_transport_shape_for_previously_uncovered_platforms` already do at unit-test
  granularity, but as a direct, evidence-cited manual confirmation for this task's closure.

## Acceptance criteria

- [ ] Both `.claude`/`.mcp.json` and `.github`/`.vscode/mcp.json` explicitly checked, with command
      output cited, not just one
- [ ] If a fix was made: `node scripts/sync.mjs --check` passes cleanly afterward (zero drift), and
      `python3 tests/functional/test_mcp_secret_guard.py` (or `python3 -m pytest
      tests/functional/test_mcp_secret_guard.py`) still passes — no literal secrets introduced
- [ ] If no fix was needed: the completion report states this plainly and cites the evidence,
      rather than silently closing with no explanation
- [ ] Report explicitly confirms or corrects the orchestrator's pre-dispatch finding (don't just
      cite it as already-settled)

## Constraints

- Token budget: part of Phase 2's 100k total (plan-035 §2.8).
- File ownership: `servers.yaml`, `implementation/platforms/*.json`, `implementation/scripts/
  sync.mjs`, `scripts/merge-mcp-json.py`, and any generated platform projection files, only if a
  genuine fix is needed. Do not touch `docs/artifacts/mcp-platform-contract-v1.md` (T420 owns it) —
  if you find it's wrong, flag it in your report rather than editing it directly.
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`.
- Do not touch branch `feature/T475-codex-platform-integration` — note that this branch has its own
  uncommitted local `.mcp.json` change (adding a `hindsight` server) which is unrelated to this
  task and out of scope; do not interact with it.
- Work in your own worktree/branch (`agent/backend-developer/T421` from `develop`); open an MR
  rather than self-merging.

## Blocker protocol

Report blockers with type and severity per `AGENTS.md`. Max 2 retries before escalating.
