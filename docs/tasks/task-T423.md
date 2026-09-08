# Task T423 — Verify/close the manual runtime-verification checklist

**ID:** T423
**Owner:** technical-writer
**Status:** pending
**Priority:** P2
**Depends on:** T420 (needs the finalized contract to confirm the checklist covers the right server
set); independent of T421/T422 — may run in parallel with them
**Created:** 2026-09-08
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 2 (T423 row: "Re-verify
against T384 (plan-033, `done`), which already added a per-platform runtime verification checklist
to `docs/wiki/mcp-servers.md` — this task may already be substantially or fully complete.")

This brief is self-contained. Wait for `docs/artifacts/mcp-platform-contract-v1.md` (T420) to exist
before starting.

## Objective

Confirm whether `docs/wiki/mcp-servers.md`'s existing runtime-verification checklist (added by
T384, `done` 2026-08-10 per `completed-tasks.md`) is complete and accurate against T420's finalized
per-platform contract, and close this task accordingly — either as a verify-and-close (most likely,
per plan-035's own expectation) or with the specific gap fixed if one is found.

## Context

`docs/wiki/mcp-servers.md` already has a "Runtime verification checklist" section (currently around
line 118, with "Automated (schema-backed)" and "Documented manual check" subsections around lines
142 and 163) — this is T384's prior work, already merged and `done`. plan-035 itself flags this as
the one Phase 2 task most likely to already be substantially or fully complete. Your job is not to
rewrite it from scratch; it's to check it against T420's contract doc and close the gap between
"documented" and "verified accurate as of today."

## Inputs

- `docs/artifacts/mcp-platform-contract-v1.md` (T420 output) — authoritative per-platform contract
  to check the existing checklist against
- `docs/wiki/mcp-servers.md` — existing document, all sections, not just the runtime-verification
  one (the "Tag system," "Core servers," "Extended servers," and "Per-platform output" sections
  earlier in the same file may also need a small correction if T420 found anything T384 didn't
  know at the time — e.g. re-confirm this file's own core/extended lists agree with T420's)
- `docs/tasks/completed-tasks.md` T384 row — for exact scope/date of the prior work
- `docs/tasks/active-tasks.md` Phase 2 dispatch note — the orchestrator's pre-dispatch finding
  about `brave`/`context7`/`cwso`, relevant if `docs/wiki/mcp-servers.md` documents those servers'
  tags anywhere

## Expected outputs

- Either: no changes needed, with a completion report stating exactly what was checked and
  confirming accuracy (cite specific line ranges / sections reviewed against T420's contract) — or
- A small, targeted edit to `docs/wiki/mcp-servers.md` fixing whatever specific inaccuracy or gap
  was found (e.g. a stale server list, a platform missing from the checklist, a tag
  misclassification), with the fix described in your completion report

## Acceptance criteria

- [ ] Every section of `docs/wiki/mcp-servers.md` that references server tags, platform counts, or
      per-platform output paths is checked against T420's contract doc, not just the runtime
      checklist section by name
- [ ] Completion report states explicitly which outcome applies (verify-and-close vs. fix-applied)
      and cites what was checked
- [ ] If edited, the edit is minimal and scoped to the specific inaccuracy found — this is not a
      rewrite task

## Constraints

- Token budget: part of Phase 2's 100k total (plan-035 §2.8); this is the smallest task in the
  phase (`small` scope) — keep it proportionate.
- File ownership: `docs/wiki/mcp-servers.md` only.
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`.
- Do not touch branch `feature/T475-codex-platform-integration`.
- Work in your own worktree/branch (`agent/technical-writer/T423` from `develop`); open an MR
  rather than self-merging, even for a small or no-op change — the branch/MR discipline applies
  regardless of diff size per `git-workflow.md`.

## Blocker protocol

Report blockers with type and severity per `AGENTS.md`. Max 2 retries before escalating.
