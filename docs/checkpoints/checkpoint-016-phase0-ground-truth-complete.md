# Checkpoint 016 — Phase 0 (Ground Truth) complete

> Written by the orchestrator at the Phase 0 → Phase 1 boundary of
> `docs/plans/plan-035-roadmap-v7-ground-up.md`.

## Phase summary

Phase 0 (Ground Truth) closed Gate G0: every published statement about the repo's
version is now true, and a CI-enforced script exists to keep it that way. T400–T406
all landed via MR !182 (squash commit `90efdf5`, merge commit `bab6540`), after QA
Engineer independently PASSed all 5 Phase 0 acceptance criteria plus the 6-item
verification bar, and Tech Lead independently reviewed the full diff and issued
VERDICT: PASS with no conditions. All acceptance criteria from plan-035 §2.4 Phase 0
are met.

## Completed tasks (this phase)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T400 | `scripts/check-version-consistency.py` (Gate G0 enforcement) | devops-engineer | Done — widened exclusions (`docs/tasks/`, `docs/plans/`, `docs/artifacts/`) + context gate eliminate ~840 false positives while catching all 4 genuine drift points |
| T401 | Fix 4 confirmed stale version references | technical-writer | Done — `README.md`, `implementation/README.md`, `docs/wiki/implementation-guide.md` all corrected to v6.10.0 |
| T402 | End-user vs. contributor doc split | technical-writer | Done — removed 1 leaked contributor snippet from `quick-start.md`, added 1 cross-link each direction |
| T403 | Relocate 6 CWSO deployment guides | technical-writer | Done — moved to `docs/archiv/cwso-deployment-guides-pending-t473-handoff/`, `docs/deployment/README.md` rewritten usage-only, pending CWSO repo T473 |
| T404 | Wire version-consistency check into release gate | release-manager | Done — `scripts/verify-release-docs.py` fails loudly on drift or missing script |
| T405 | Plan-precondition hardening | tech-lead | Done — `/plan` output now a hard precondition for task creation; `test_every_active_task_has_a_plan` hardened from `skipTest` to a real failure |
| T406 | Validation gate + merge | qa-engineer, tech-lead | Done — PASS/PASS, MR !182 merged to `develop` |

## Open / carried over

| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| T417 | Install Harbor; verify oracle smoke run | devops-engineer | blocked | Pulled forward from Phase 1 per plan-035 §2.9 "first 30 days." Docker daemon unreachable — host RAM/swap exhaustion from concurrent sessions, re-confirmed 2026-08-13 (~927Mi available, ~90% swap used). Not required for Phase 0's own completion. Retry once host resource pressure clears; Harbor itself (v0.21.0) is installed and verified, diagnostic writeup committed on `feature/T417-harbor-install-oracle-smoke` (commit `bbf645c`), not yet merged. |

## Key decisions

- T400/T401 scope addendum (`9e7c2f4`, MR !181, addenda to `task-T400.md`/`task-T401.md`): widened the version-consistency script's exclusion list to match AGENTS.md's own append-only/immutable record classes, and added a narrow context gate rather than a full NLP rewrite. Surfaced a genuine 4th drift file (`docs/wiki/implementation-guide.md`) the original plan-035 audit missed.
- T403: CWSO deployment guides moved, not deleted, and staged under an explicit `pending-t473-handoff` path per plan-035 §2.5's coupling constraint — T403 must not land before CWSO repo task T473 is ready to receive them. They remain in this repo's `docs/archiv/` until that handoff happens.
- T406 merge: the initial `glab mr merge` attempt was denied twice by the Claude Code auto-mode permission classifier when run from a background agent context (no live user available to approve). The user explicitly approved via AskUserQuestion, then the merge was executed directly in the interactive foreground session (where a live permission prompt is possible) rather than treating a relayed chat message as sufficient authorization for a background agent to bypass its own denial.

## Artifacts produced

- `docs/plans/plan-035-roadmap-v7-ground-up.md` (MR !179)
- `scripts/check-version-consistency.py` + `tests/functional/test_check_version_consistency.py`
- `docs/tasks/task-T400.md` through `task-T406.md`
- `docs/benchmarks/environment.md` (T417, on its own unmerged branch)

## Blockers (active)

| ID | Type | Severity | Owner | Reported | Status |
|----|------|----------|-------|----------|--------|
| T417 | external | critical | devops-engineer | 2026-08-12 | Open — host resource exhaustion (Docker daemon unreachable); see `docs/tasks/active-tasks.md` header note |

## Token usage

| Phase | Budget | Spent | % |
|-------|--------|-------|---|
| Phase 0 — Ground Truth | 100k | ~95k (across 3 orchestrator run segments + 5 delegated agents) | ~95% |

## Next steps

- Gate G0 is closed. Phase 1 (Trustworthy Signal) and Phase 2 (MCP Conformance) task
  briefs may now be authored **once** the two open questions from plan-035's Approval
  section are resolved by the user:
  1. Which agent is Arm A for the Terminal-Bench two-arm delta harness (`claude-code`,
     `codex`, or `gemini-cli`)?
  2. What does a null/negative Terminal-Bench delta mean, committed in writing before
     T41A runs?
- T417 may be retried independently of Phase 1's start, once host resource pressure
  clears — it has no dependency on the two open questions above (it only needs Docker).
- Tasks: none yet authored beyond T400–T406/T417 per plan-035's own scope guard.
- Inputs to delegate forward: this checkpoint, `docs/plans/plan-035-roadmap-v7-ground-up.md`.

## Compression note

This checkpoint is the canonical handoff for Phase 1/2 planning. Subsequent agents
receive **only**: this checkpoint + their task brief + `plan-035-roadmap-v7-ground-up.md`
— not the full T400–T406 execution history.
