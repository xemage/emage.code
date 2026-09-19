# Checkpoint 017 — T417 (Harbor install + oracle smoke run) complete

> Written by the orchestrator after closing the one item carried over from
> `checkpoint-016-phase0-ground-truth-complete.md`. Phase 0 (Gate G0) itself was already fully
> closed at checkpoint 016; this checkpoint only concerns T417, which was pulled forward from
> Phase 1 per `plan-035-roadmap-v7-ground-up.md` §2.9 and tracked independently of Gate G0.

## Summary

T417 retried cleanly after the 2026-08-12 Docker-daemon-unreachable blocker (host resource
exhaustion, swap 100% full at every reading that session). Host conditions measurably improved by
2026-08-13 (swap ~55% used vs. 100%, `docker ps` instant) and the retry was executed in the
existing worktree/venv from the prior attempt (Harbor 0.21.0 already installed).

- **Required 5-task oracle smoke** (`terminal-bench/terminal-bench-2-1 -a oracle -l 5`): **5/5 =
  100% PASS**, 0 exceptions, Docker healthy/responsive throughout. Satisfies the task's minimum
  acceptance bar; the 2026-08-12 blocker does not reproduce.
- **Extended 25-task run** (`terminal-bench/terminal-bench-2 -a oracle -l 25`, substituted for the
  full 89-task set per the brief's own time-budget fallback): **17/25 = 68%**, not 100%. Reported
  honestly, not conflated with the 2026-08-12 blocker:
  - 4/8 failures: transient Docker Hub registry OAuth-token 500 error (external, local daemon
    confirmed healthy throughout, including at the tightest resource-pressure point of the run).
  - 4/8 failures: genuine task-level oracle non-passes (`caffe-cifar-10`, `crack-7z-hash` —
    `AgentTimeoutError`; `install-windows-3-11`, `rstan-to-pystan` — explicit 0.0 reward, no
    exception, root cause not further investigated in this session).
- Surfaced a genuine internal conflict in the task brief between Criterion 5 ("100% ... 5-task
  minimum") and Criterion 7's literal "any scope attempted" text. Tech Lead review independently
  reached the same reading as the orchestrator (`VERDICT: CONDITIONAL_PASS`): the brief's own
  Blocker Protocol section only gates on the 5-task set, making it the binding acceptance floor.
  Reconciliation recorded as an addendum in `docs/tasks/task-T417.md`.
- MR !184 (squash commit `936b2d4`, merge commit `4f8bf20`) merged to `develop`; CI green (5/5
  jobs: sync-no-diff, validation-super-gate, verify-knowledge-drift, unit-tests, markdown-links).
  Worktree `t417-harbor` and branch `feature/T417-harbor-install-oracle-smoke` cleaned up
  (local + remote) per the Worktree Lifecycle protocol.

## Completed tasks (this checkpoint)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T417 | Install Harbor; verify with oracle smoke run | devops-engineer, tech-lead | Done — 5-task oracle gate 100% pass; 25-task extended run 68% (2 distinct root causes, tracked as follow-up, not blockers) |

## Open / carried over

None from this checkpoint. Phase 0 (Gate G0, checkpoint-016) and T417 (this checkpoint) are both
now closed. `docs/tasks/active-tasks.md` is empty (0 active tasks).

## Key decisions

- **Criterion 5/7 reconciliation** (`task-T417.md` addendum, commit on `feature/T417-harbor-install-oracle-smoke`):
  the 5-task oracle smoke gate (100% pass required) is the binding acceptance floor for T417, not
  the literal "any scope attempted" reading of Criterion 7. This follows the brief's own Blocker
  Protocol section, which explicitly gates only on the 5-task set and treats the full/extended run
  purely as a time/disk budget question. Confirmed independently by Tech Lead review before this
  was adopted, not decided unilaterally by the orchestrator alone.
- **No new task opened for the 25-task extended-run findings.** Follow-up items (retry 4
  registry-affected tasks once Docker Hub recovers; investigate 2 unexplained 0.0-reward tasks;
  investigate 2 `AgentTimeoutError` tasks) are recorded in `completed-tasks.md`'s T417 entry and
  `task-T417.md`'s addendum, to be picked up by whichever future task first relies on `-l 25`+-scale
  unattended runs (expected T418) — not authored now, per this session's guardrail against
  authoring Phase 1+ work while the plan's two open questions remain unresolved.

## Artifacts produced

- `docs/benchmarks/environment.md` (Harbor/Docker versions, host resources, full run output for
  both the 2026-08-12 blocked attempt and the 2026-08-13 retry, preserved together)
- `docs/tasks/task-T417.md` (addendum reconciling Criterion 5/7)
- `docs/tasks/active-tasks.md` / `docs/tasks/completed-tasks.md` (T417 archived)
- MR !184 (squash commit `936b2d4`, merge commit `4f8bf20`)

## Blockers (active)

None. T417's `type: external, severity: critical` blocker from 2026-08-12 is resolved (did not
reproduce on retry).

## Token usage

| Phase | Budget | Spent | % |
|-------|--------|-------|---|
| T417 (Phase 1 budget, pulled forward per §2.9) | 20k (task-level, per `task-T417.md`) | ~119k (DevOps Engineer execution ~70k + Tech Lead review ~49k, across this retry session; substantially over the original 20k task-level estimate due to the extended 25-task run's added diagnostic work and the Criterion 5/7 reconciliation cycle) | ~595% of task estimate |

## Next steps

- `active-tasks.md` is now empty. No further task may be authored until either:
  1. The user resolves plan-035's two open Phase 1 questions (Arm A agent selection; null/negative
     delta interpretation), unblocking T418+; or
  2. The user requests unrelated new work.
- Recommended (not authorized) follow-ups for whenever T418 is eventually scoped: retry the 4
  Docker-Hub-registry-affected oracle tasks; investigate `install-windows-3-11` and
  `rstan-to-pystan`'s unexplained 0.0-reward outcomes; investigate whether `caffe-cifar-10` and
  `crack-7z-hash`'s `AgentTimeoutError`s are compute-bound or resource-timing-sensitive.

## Compression note

This checkpoint plus `checkpoint-016-phase0-ground-truth-complete.md` together are the canonical
handoff for any future Phase 1/2 planning. Subsequent agents receive **only**: both checkpoints +
their task brief + `plan-035-roadmap-v7-ground-up.md` — not the full T417 retry execution history.
