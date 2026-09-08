# Task T420 — Define the per-platform MCP contract

**ID:** T420
**Owner:** solution-architect, orchestrator
**Status:** done
**Priority:** P1
**Depends on:** — (G1 closed; Phase 2 dispatched)
**Created:** 2026-09-08
**Completed:** 2026-09-08
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 2 (task table, unchanged);
`docs/plans/plan-037-phase2-phase5-sequencing.md` (execution sequencing: T420 first, gates T421/
T422/T423); `docs/checkpoints/checkpoint-021-phase1-complete-gate-g1-closed.md` (Gate G1 closure,
"Next steps").

This brief is self-contained.

## Objective

Produce `docs/artifacts/mcp-platform-contract-v1.md`: an authoritative, per-platform contract
documenting, for each of the 7 platforms this repo currently projects MCP config to, the exact
output file path, wire format, and which `servers.yaml` tags (`core` / `extended`) are included in
that platform's projection — derived directly from the sync engine's own source of truth, not from
prose summaries (including this brief's own summary below, which you must independently confirm,
not just cite).

## Context

Gate G1 closed 2026-09-08 (`checkpoint-021`). Phase 2 (T420-T423) is the first phase dispatched
after G1, per the user-approved `plan-037` sequencing recommendation (Phase 2 before Phase 5). T420
is deliberately first in the dependency chain: T421's re-scoping and T422's conformance test both
need this contract finalized before they can check anything against it — without T420, T422 cannot
define what "correct" looks like per platform, and T421 cannot adjudicate whether any given
discrepancy is a defect or intended behavior.

## Orchestrator pre-dispatch finding — read before starting, but re-verify independently

`plan-037` (the approved plan that dispatched this phase) itself contains a kickoff finding that
turned out to be **wrong**, caught by the orchestrator during pre-dispatch verification, not by
you. Do not propagate it into the contract doc without confirming it yourself first:

- **plan-037's claim:** `.vscode/mcp.json` (the `github` platform's projection target)
  over-includes `brave` and `context7` because they are tagged `extended` in `servers.yaml`, which
  `AGENTS.md`'s tag table says should be excluded from the `github` platform.
- **What the orchestrator found on direct re-check, 2026-09-08:** this is false.
  `implementation/knowledge/mcp/servers.yaml` tags both `brave` (line 51) and `context7` (line 59)
  as `[core]`, not `extended` — matching `AGENTS.md`'s own "Core servers (always available)" table,
  which lists both by name. `implementation/platforms/github.json`'s own manifest declares
  `"mcp": {"tags": ["core"], ...}` — i.e. the `github` platform is already correctly scoped to
  `core`-only by the sync engine's own config, and `brave`/`context7` being `core`-tagged means they
  are *supposed* to appear there. A live run of `node scripts/sync.mjs --check` (from
  `implementation/`), both `--platform=github` alone and unscoped across all 7 platforms, reported
  **zero drift across 557 files** on `develop` at dispatch time. Separately, the `cwso` entry also
  present in `.vscode/mcp.json` (not in `servers.yaml` at all) is intentional, documented behavior —
  `scripts/merge-mcp-json.py`'s docstring (ADR-002) explicitly describes preserving hand-added,
  non-generator dest-only keys like `cwso` by design, so it does not belong in this contract doc as
  a defect either.
- **What this means for you:** do not take either the orchestrator's correction above or the
  original plan-037 claim on faith. Independently re-derive the full picture yourself — read
  `servers.yaml`, read all 7 files in `implementation/platforms/*.json`, run
  `node scripts/sync.mjs --check` yourself from a clean checkout, and read `scripts/
  merge-mcp-json.py` — before writing the contract doc. If your own independent check disagrees
  with the orchestrator's finding above in any respect, say so explicitly in your completion report
  rather than silently reconciling it.

## Inputs

- `implementation/knowledge/mcp/servers.yaml` — canonical server registry (source of truth for
  tags, transport, command/args/env per server)
- `implementation/platforms/*.json` — one manifest per platform (`claude-code.json`, `cline.json`,
  `cursor.json`, `gemini.json`, `github.json`, `opencode.json`, `pi.json`); each has an `mcp` block
  with `tags`, `outputFile`, `format`
- `implementation/scripts/sync.mjs` — the sync engine; `emitMcp()` (around line 293) shows how tags
  select servers per format; the `manifest.mcp` handling block (around line 504) shows how
  `outputFile` and provenance sidecars are written
- `scripts/merge-mcp-json.py` — merge algorithm for single-file MCP configs (`.vscode/mcp.json`,
  `.mcp.json`) that preserves hand-added dest-only keys; read the module docstring and
  `prune_names_recursive` for how retired generator-owned keys are distinguished from hand-added
  ones
- `AGENTS.md` §"MCP Servers" — the human-facing summary table (core servers, extended servers,
  tag-emission rule); treat this as a summary to cross-check against the machine sources above, not
  as the primary source
- `docs/wiki/mcp-servers.md` — existing manual runtime-verification checklist (T384, plan-033);
  relevant context for what T423 will check against, not this task's direct output, but worth
  reading so your contract doc's platform list and file paths agree with it

## Expected outputs

`docs/artifacts/mcp-platform-contract-v1.md`, containing, at minimum:

- A table with one row per platform (7 rows: `claude-code`, `cline`, `cursor`, `gemini`, `github`,
  `opencode`, `pi`) with columns: platform name, output file path (relative to repo root), wire
  format (`vscode` / `cursor` / `claude-code` / `gemini` / `opencode` / etc. — whatever
  `emitMcp()`/the manifest actually names it), and which tags (`core` only, or `core` + `extended`)
  are included per that platform's own manifest.
- An explicit statement, per platform, of exactly which servers (by name) currently appear in that
  platform's live projection, cross-checked against `servers.yaml`'s tag for each — i.e. do the
  actual enumeration, not just "core servers appear everywhere."
- A short "known non-generator content" subsection documenting the `merge-mcp-json.py` preservation
  behavior for `.vscode/mcp.json` and `.mcp.json` (single-file targets), including the `cwso`
  precedent, so T421/T422 don't re-flag it as a gap.
- A conclusion section explicitly adjudicating the plan-037 finding above: state plainly whether it
  is confirmed a non-issue (per the orchestrator's pre-check) or whether your own independent check
  found something the orchestrator's check missed.

## Acceptance criteria

- [ ] All 7 platforms enumerated with correct output path, format, and tag-scope, verified against
      `implementation/platforms/*.json` directly (not assumed from this brief)
- [ ] Live `node scripts/sync.mjs --check` output (or equivalent evidence) cited to support any
      claim of drift or no-drift — not asserted without a command run
- [ ] The plan-037 `brave`/`context7`/`cwso` finding is explicitly adjudicated (confirmed or
      corrected further) with your own evidence, not merely restated from this brief
- [ ] Document references its inputs per this repo's Artifact Versioning convention (`Based on:
      servers.yaml`, `platforms/*.json`, etc.)

## Constraints

- Token budget: this task is part of Phase 2's 100k total budget (plan-035 §2.8); keep this task
  itself well under half that.
- File ownership: write only `docs/artifacts/mcp-platform-contract-v1.md`. Do not modify
  `servers.yaml`, `platforms/*.json`, or any generated platform projection — this is a
  documentation task, not a fix task (T421 owns fixes, if any turn out to be needed).
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`
  (frozen, unrelated to this task anyway).
- Do not touch branch `feature/T475-codex-platform-integration`.
- Work in your own worktree/branch per `git-workflow.md` (`agent/solution-architect/T420` from
  `develop`); open an MR to `develop` rather than self-merging. The orchestrator will independently
  verify before merging.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). Max 2 retries before escalating to the orchestrator.
