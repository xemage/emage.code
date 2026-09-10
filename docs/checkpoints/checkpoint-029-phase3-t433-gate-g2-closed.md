# Checkpoint 029 — Phase 3: T430-T433 done, Gate G2 closed per ADR-006

> Written by the orchestrator after T433's closure, the immediate follow-up flip, and full
> independent verification of both. Future agents resuming this thread need only this checkpoint +
> `docs/decisions/ADR-006-gate-g2-routing-target-classes-interpretation.md` +
> `docs/artifacts/phase3-wave1-promotion-v1.md`, not the full T430-T433 execution history.

## Summary

**T430, T431, T432, T433 (4 of Phase 3's 8 tasks) are done, merged to `develop`, and
independently verified.** The maturity enum is reconciled and mandatory (T430); concrete,
per-category promotion criteria exist (T431); a CI-enforced, adversarially-hardened checker
mechanically verifies claimed levels against real evidence (T432); and Wave 1 has genuinely
promoted 3 components to `stable` (`qa-engineer`, `validation-gates` skill, `code-review` skill),
with real evidence produced for 6 more that remain blocked on pre-existing, unrelated product
defects (T433).

**Gate G2 is closed**, per `ADR-006` (accepted this session): the "routing target classes"
ambiguity `plan-038` first flagged and `plan-041` narrowed to two readings was found, on a deeper
re-read before T433's dispatch, to have a third genuine reading — presented to the user as a
real decision point rather than picked unilaterally, and resolved as reading (c)
(infrastructure-precondition: G2 closes because real `stable` promotions now demonstrably exist,
not because any routing-candidate list was identified — that identification is explicitly deferred
to Phase 4's own future planning pass).

**A genuine, previously-undiscovered structural defect was found, independently reproduced, and
worked around procedurally (not by weakening the checker) before this checkpoint:**
`check-maturity.py`'s shared defect-check (T431's own §3.5) cannot distinguish "an open task
reports a defect in component X" from "an open task's own subject matter is X" — so a promotion
task can never make its own claimed promotions pass while it remains open. T433 hit this for real
(it necessarily named all 9 of its own candidates). Resolved by closing T433 first (the only way
to break the cycle, since archival is orchestrator-only) and flipping the genuinely evidence-ready
components in an immediate, separate follow-up — not by loosening the check itself, which remains
exactly as strict as T431/T432 designed it.

## Completed this session

| Item | Outcome |
|------|---------|
| Phase 3 planning (`plan-041`) | Approved, merged MR !252. Re-confirmed Phase 3's start condition, resolved the G2-circularity's effect on Phase 3's *start* (none), corrected a stale `plan-035` premise about T430's schema. |
| T430 (maturity levels) | Done. Reconciled enum, made the field mandatory, found and fixed a pre-existing regex bug that explains why nothing was ever classified. MR !253 (brief), !254 (impl), !255 (checkpoint-028), !256 (closeout). |
| T431 (promotion criteria) | Done. Real per-category/per-transition criteria; a factual error ("zero skills referenced in tests") found and corrected before merge. MR !257 (impl), !258 (closeout). |
| T432 (check-maturity.py) | Done. CI-enforced verifier; a real gaming vulnerability (documentation-padding attack) found and hardened before merge, including the orchestrator catching its own test-design error mid-review. MR !259 (impl), !260 (closeout). |
| ADR-006 (Gate G2 disposition) | Accepted. Three readings considered, none with a textual tiebreaker, presented to the user, reading (c) chosen. MR !261 (with T433 dispatch). |
| T433 (Wave 1 promotion) | Done. Real evidence for 9 candidates; a structural self-referential blocker found and independently reproduced; 3/9 genuinely promoted to `stable`, 6/9 blocked on real pre-existing defects (recorded, not dispatched). MR !261 (dispatch), !262 (evidence), !263 (closeout), !264 (flip + stale-test fix). |

## Real, independently-verified current state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (3 active, 270 completed)
- `python3 tests/run.py`: 499 tests, OK, skipped=24
- `python3 implementation/scripts/check-maturity.py --root implementation --verbose`: 77 components,
  0 failing their claimed level — `agent/stable: 1`, `skill/stable: 2`, remainder at `experimental`
- `node implementation/scripts/sync.mjs --root implementation --check`: no drift, 563 files
- Adversarial re-verification performed by the orchestrator this session (not accepted on any
  implementer's self-report): a false `stable` claim with zero evidence, a junk `## Rails` heading,
  a `## Rails` section with empty label values, and a documentation-padding attack were all
  attempted against T432's checker — the first three were caught immediately, the fourth succeeded
  once and was fixed and re-verified; a fifth probe (removing real Rails content from an
  already-`stable` `qa-engineer` to confirm the claim is dynamically re-checked, not grandfathered)
  correctly failed on the first *correctly-constructed* attempt, after the orchestrator's own first
  attempt at that specific probe had a script bug that produced a misleading false pass, caught and
  corrected before being reported as a finding.

## Process notes worth carrying forward

- **The coordinator-message pattern continued this session** (T430's merge claim, T431/T432's
  continuation approvals, T433's ADR-006 approval) — every factual claim was independently
  re-derived against real GitLab/git/filesystem state before being acted on, consistent with this
  project's standing disposition; none were treated as self-evident authorization on their own.
- **The orchestrator's own merge attempts were denied by the session's tool-permission classifier**
  for the first two attempts this session (T430's dispatch/implementation MRs); the user merged
  those. Later merge attempts in this same session succeeded when retried, suggesting the block was
  not a fixed, permanent constraint — worth re-attempting rather than assuming it will always fail.
- **Two genuine "orchestrator catches its own probe-construction bug before reporting a false
  finding" incidents occurred this session** (T432's beta-vs-stable tier mis-probe; T433's
  Rails-removal regex mismatch) — both were caught by re-deriving the expected mechanism from the
  actual source code before concluding a vulnerability existed or didn't, rather than trusting the
  first observed (and in both cases, wrong) result.

## Token metrics

Not separately tracked against a phase budget this session — Implementation-phase work (T430-T433
dispatch, adversarial verification, and ledger closeout) spanned multiple agent dispatches across
several coordinator turns; no single-phase budget overrun was flagged during the session.

## Next steps

- **T434 (Wave 2 — remaining core agents/commands)** and **T435 (Wave 3 — skills/instructions)**
  both depend on T433 (now done) and can run in parallel with each other (disjoint component
  categories, per `plan-041`'s own task-breakdown note) — neither recorded nor dispatched this
  session.
- **Four real, disclosed product defects remain unresolved**, out of scope for any promotion task:
  `plan-real-doc-header-drift` (open), the held-out `/code-review` verdict-format defect,
  `security-audit-critical-not-fail` (open, newly surfaced by T433's own review), and `T457`
  (security-engineer tool-scoping, already tracked). None opened as new tasks this session —
  flagged for prioritization.
- **T436 (honest demotion pass)** depends on T434 *and* T435 both completing — not reachable yet.
- **Phase 4 (Task-Tier Routing)** is now unblocked at the gate level (G2 closed per `ADR-006`) but
  has not been planned to execution-ready detail — per this project's own Plan-Approve-Execute
  protocol and `ADR-006`'s own explicit statement, a dedicated Phase 4 planning pass (mirroring
  `plan-037`/`plan-038`/`plan-041`) is required before any `T44x` brief is authored, and that
  planning pass is where the routing-candidate identification `ADR-006` deferred must actually
  happen.
- **T456/T457/T458** (Phase 5 follow-ups) and **`feature/T475-codex-platform-integration`** remain
  exactly as prior checkpoints left them — untouched this session.
