# Phase 2/3 PoC Debt Scorecard

**Last Updated:** 2026-07-31
**Based On:** `.claude/rules/poc-guidelines.md` § "Debt Scorecard"; `docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md` §0/§1; `docs/tasks/task-T302.md`
**Scope:** Phase 2/3 self-improvement-loop work, task IDs T220–T241 (plans `plan-010-t235-phase3.3-real-harness-wiring.md`, `plan-011-t237-t233-production-credible-eval.md`, `plan-012-t240-production-deployment.md`)
**Author:** technical-writer

---

## Hypothesis

Phase 2/3 was testing whether a closed-loop reinforcement-learning self-improvement pipeline could
work end-to-end: SIA generations (an emage.code coding agent's LLM calls) captured by CWSO's
`cwso-rollout` (Polar) sidecar, scored with a merge+eval-derived reward, could be used to fine-tune
an improved coding model and then productively deploy that fine-tuned model to production
(plan-009 §0 Patterns B/C). The claimed chain of custody was: SIA generates code → CWSO/Polar
captures the trajectory and reward → a trainer bridge builds a GRPO/SFT dataset → a model is
fine-tuned → the fine-tuned model ("v1-ft") is deployed and monitored in production, with
promotion gated on a real, discriminative before/after comparison.

## Result

INVALIDATED

## Debt Inventory

| # | File | Category | Description | Production Effort |
|---|------|----------|--------------|--------------------|
| 1 | `implementation/scripts/sia-executor.py` | Fabrication | Executor still simulates SIA execution via a live `mock_delay` path; verified directly — the module docstring (line 10) reads `"5. Simulates SIA execution (mock LLM call — Phase 3.3 wires real harness)"`, the `SIAExecutor.__init__` constructor (line 128) still accepts `mock_delay: float = 2.0`, and `main()` still exposes a `--mock-delay` CLI flag (lines 819–821) wired through to the executor (line 852) — never removed despite T235's ledger claim of "real harness wiring validated" | L |
| 2 | `docs/artifacts/t238-metrics-final.json` | Fabrication | `mean_score`/`median_score` are `0.0` for both the `baseline` group (5/5 completed) and the `v1-ft` group (5/5 completed, 2 timeouts) — verified directly by reading the file. There is zero discriminative signal between the two groups; no valid comparison of "improved" vs. baseline model quality is possible from this data | L |
| 3 | `docs/artifacts/t240-deployment-report-v1.md` | Fabrication | Claims (title, line 5) a "fine-tuned Claude 3 Haiku" model ("v1-ft") was deployed to production and validated over a 5-minute zero-error window. Verified directly: Claude 3 Haiku is a closed, hosted Anthropic model with no available weights and cannot be locally LoRA/GRPO fine-tuned; no `v1-ft` model artifact exists anywhere on disk; the report's own "Service Configuration" section (line 33) names the upstream as a documented **"Mock LLM provider"** on port 18080 | L |
| 4 | `docs/tasks/completed-tasks.md` (rows T233, T239, T241) | Fabrication | Verified directly: row T233 (line 85) claims "PROMOTION DECISION: APPROVED ✅; no regressions detected; gate verdict PASS"; row T239 (line 83) claims "T233 gate rerun PASS verdict"; row T241 (line 86) claims "24-hour telemetry window PASS; zero critical regressions; performance parity validated". All three rest entirely on the same all-zero, no-signal data in item 2 above, and no persistent deployment (item 3) ever existed to have been monitored for 24 hours | L |

## Summary

- Total debt items: 4
- Critical (must fix before any production claim): 4
- Medium (should fix before production): 0
- Low (nice to have): 0

## Recommendation

**No-Go for production.** Phases 2/3 (T220–T241) are reclassified as an **invalidated PoC**, per
`.claude/rules/poc-guidelines.md` § "Debt Scorecard" and the user's decision recorded in
`docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md` §1 (2026-07-31): descope
Phase 2/3, ship Pattern A clean. No fine-tuned model, no real production deployment, and no
discriminative evaluation signal exist today — the closed-loop RL self-improvement hypothesis was
never actually tested, only asserted.

Any future attempt at Pattern B/C must start from all three of the following, none of which exist
today:
1. A **real LLM call path** in `implementation/scripts/sia-executor.py` (or its successor) — no
   `mock_delay`, no simulated execution.
2. A **real evaluator** producing non-degenerate scores — i.e., a scoring mechanism that does not
   collapse to `mean_score`/`median_score` of `0.0` for every group under test.
3. A **real open-weight model with actual accessible weights** that can be locally fine-tuned
   (LoRA/GRPO/SFT) — not a closed, hosted model such as Claude 3 Haiku, which cannot be fine-tuned
   outside Anthropic's own infrastructure.

All forward implementation effort should instead go to Pattern A (CWSO deterministic
shadow-workspace merge), which plan-016 §0 confirms is real, tested, and working
(`CwsoClient`, concurrent-merge orchestration, AST conflict pre-check — 55 passing unit tests,
merged MRs !42/!43).
