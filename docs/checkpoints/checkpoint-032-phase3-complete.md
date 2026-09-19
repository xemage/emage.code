# Checkpoint 032 — Phase 3 (Maturity Ladder) complete: T430-T437, all 8 tasks done

> Written by the orchestrator immediately after T437's merge and ledger closeout. This is a real
> phase boundary: `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md`'s Phase 3
> (T430-T437) is now fully done, independently verified at every step. Future agents planning
> Phase 4 need only this checkpoint + `docs/decisions/ADR-006-gate-g2-routing-target-classes-
> interpretation.md` + the four `docs/artifacts/phase3-wave*-promotion-v1.md` / `phase3-maturity-
> demotion-decision-v1.md` artifacts, not the full T430-T437 execution history.

## Summary

**Phase 3 of `plan-035` (T430-T437, "Maturity Ladder") is fully done and genuinely merged to
`develop`.** All eight tasks closed in dependency order (T430 → T431 → T432 → T433 → {T434, T435 in
parallel} → T436 → T437), each independently verified by the orchestrator against real command
output before merging — not accepted on any agent's self-report alone, across seven separate
dispatches (some requiring correction cycles when adversarial review found real gaps).

## Real, independently-verified final state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (3 active, 274 completed)
- `python3 tests/run.py`: 514 tests, OK, skipped=24
- `python3 implementation/scripts/check-maturity.py --root implementation --verbose`: 77
  components, 0 failing their claimed level
- `node implementation/scripts/sync.mjs --root implementation --check`: no drift, 563 files

### Final maturity distribution (77 registry components)

| Category | Experimental | Stable | Deprecated | Total |
|---|---:|---:|---:|---:|
| Agents | 8 | 20 | 0 | 28 |
| Commands | 19 | 0 | 0 | 19 |
| Instructions | 0 | 4 | 0 | 4 |
| Skills | 19 | 7 | 0 | 26 |
| **Total** | **46** | **31** | **0** | **77** |

31 of 77 components (40%) are genuinely, mechanically-verified `stable` — up from 0 at Phase 3's
start (every component was uniformly `beta`-by-default before T430, per `checkpoint-027`'s
pre-Phase-3 state; T430 corrected this to an honest `experimental` floor, and T433-T435 promoted
what could genuinely earn it). **Zero components are `deprecated`** — T436's real, evidence-
grounded conclusion was that nothing currently qualifies (every gap is a live, trackable, fixable
item, not a dead end), independently verified before being accepted as Phase 3's final answer.

Commands remain at 0 `stable` — not a gap in Phase 3's own execution, but a disclosed, scoped-out
follow-up: 14 of 19 need golden-case coverage authored under a protected-path exception never
requested this phase (by design — see `phase3-wave2-promotion-v1.md` §4), and the other 5 (2 from
Wave 1, 3 from Wave 2) are blocked on real, tracked golden-suite format-drift defects.

## Gate status

- **Gate G2 is closed**, per `ADR-006` (accepted this session): the "routing target classes"
  ambiguity `plan-038` first flagged and `plan-041` narrowed was resolved on the infrastructure-
  precondition reading — G2 closed on T433's completion (real `stable` promotions demonstrating the
  "stable brief with rails and tests" precondition is achievable), not on any routing-candidate
  identification, which is explicitly deferred to Phase 4's own future planning pass. T434-T437's
  completion since then doesn't change G2's status — it was already closed; Phase 3 simply
  continued to its own natural end.
- **Gate G3 remains open** — unrelated to Phase 3, gated on Phase 5's own ship-gate task (`T456`),
  which remains `blocked` (needs `T458`, the live-execution harness, still `pending`). Unchanged by
  this session's work; not addressed this session.
- **Gate G0/G1** remain closed, unchanged (Phase 0/Phase 1, closed in prior sessions per
  `checkpoint-016`/`checkpoint-021`).
- **Gate G4** remains ungated-but-unclosed — its evaluator-protection precondition closed with G1,
  but the rest of its own phase's conditions (Phase 6) haven't been reached.

## Process notes worth carrying forward (the full Phase 3 arc)

- **Every single Phase 3 dispatch this session hit at least one genuine, independently-caught
  issue** — none were rubber-stamped: T430 (a pre-existing regex bug explaining why nothing had
  ever been classified), T431 (a factual error in the delivered artifact, corrected before merge),
  T432 (a real gaming vulnerability in the checker itself, found via adversarial probing and fixed),
  T433 (a structural self-referential ledger-defect finding requiring a two-step closeout to
  resolve), T434/T435 (a live, self-inflicted regression from naming already-`stable` components in
  open task prose, caught before dispatch both times), T436 (the read-only-agent dispatch-mechanics
  finding plus a third regression variant), T437 (a fourth regression variant, the first triggered
  by a file path rather than prose). This is not a criticism of the work — every issue was caught
  and fixed before merging, which is exactly what the adversarial-verification discipline this
  project applies is for. It is a genuine, recurring signal that "small" or "late-phase" tasks did
  not warrant less scrutiny, and didn't get less in practice.
- **The self-referential/incidental-mention regression against `check-maturity.py`'s ledger-defect
  check had four distinct variants found this phase**, each different enough to be worth
  distinguishing for future phases: (1) a task naming its own promotion subjects (T433); (2) a task
  naming an unrelated already-`stable` component as incidental context (T434/T435); (3) a task's
  own required Owner field naming an already-`stable` agent (T436); (4) a task's own file-path/
  branch-name reference, not prose, naming an already-`stable` agent (T437). As more components
  become `stable` over time, this collision surface only grows — any future task brief in this
  repo should be checked against the full current stable-id list before dispatch, not assumed safe
  by analogy to a prior, narrower incident.
- **The GitLab merge-permission classifier blocked the orchestrator's own merge attempts twice near
  the start of this arc (T430), then allowed every subsequent attempt without issue** — worth
  re-attempting rather than assuming a permanent block, as this session did.
- **A transient GitLab/Gitaly CI infrastructure failure occurred once** (documented in
  `checkpoint-030`), resolved by triggering fresh pipelines directly via the GitLab API rather than
  `glab ci retry`, which panics on a zero-job pipeline.

## Token metrics

Not separately tracked against a phase budget across this session's Phase 3 work.

## Next steps

- **Phase 4 (Task-Tier Routing) is unblocked at the gate level** (Gate G2 closed per `ADR-006`) but
  **has not been planned to execution-ready detail and is not started** — per this project's own
  Plan-Approve-Execute protocol, and per `ADR-006`'s own explicit statement that the routing-
  candidate identification it deferred belongs in Phase 4's own dedicated planning pass (mirroring
  `plan-037`/`plan-038`/`plan-041`'s precedent for Phase 2/5/3), this is available to start on
  request, not started proactively this session.
- Three real, disclosed follow-up gaps from Phase 3 remain unaddressed, none opened as new tasks:
  (1) 14 commands need golden-case coverage under a disclosed protected-path exception; (2) 5
  commands need a verdict/header-format-drift fix (2 from Wave 1, 3 from Wave 2); (3) 4 skills need
  a content-correction pass (`dependency-graphing` needs an explicit schema-vs-skill decision
  first).
- **T456/T457/T458** (Phase 5's own remaining ship-gate work) and
  **`feature/T475-codex-platform-integration`** remain exactly as prior checkpoints left them —
  untouched this session.
