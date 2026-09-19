# Checkpoint 030 — Phase 3: T434/T435 done, 31/77 components genuinely `stable`

> Written by the orchestrator after T434/T435's closure and the Wave 2/3 flip follow-up, all
> independently verified. Future agents resuming this thread need only this checkpoint +
> `docs/artifacts/phase3-wave2-promotion-v1.md` + `docs/artifacts/phase3-wave3-promotion-v1.md`,
> not the full T434/T435 execution history.

## Summary

**T434 (Wave 2) and T435 (Wave 3) are both done, merged to `develop`, and independently verified.**
Combined with T433 (Wave 1, `checkpoint-029`), Phase 3's promotion waves have now produced real,
mechanically-verified `stable` status for **31 of 77 registry components** (20 agents, 4
instructions, 7 skills — 0 commands yet, blocked on a real, disclosed golden-case coverage gap).

**T434's central, independently-reproduced finding: T433's self-referential ledger-defect blocker
does not universally apply.** It was specific to T433's own brief necessarily naming its own
promotion targets. T434/T435 were deliberately drafted to never name an in-scope component by id,
and this was verified (both by the implementer and independently by the orchestrator, grepping
each brief against the real registry id list) to genuinely prevent the blocker — 28 components
report a clean `PASS` today with their promoting tasks' rows *already closed*, not merely "would
pass once archived."

**A live, self-inflicted regression was caught and fixed before dispatch, not after.** An early
draft of both T434/T435 briefs named the 3 already-`stable` Wave 1 components as context —
distinct from *promoting* them, but the shared defect-check can't tell the difference, and this
spuriously regressed all 3 the moment the draft became an open ledger row. Caught by running
`python3 tests/run.py` before committing the dispatch (this session's own standing discipline for
every ledger edit), fixed by removing the literal mentions, re-verified clean.

**A real, anticipated, purely mechanical merge conflict** (`implementation/registry/index.json`,
from T434 and T435 both regenerating the registry independently from the same `develop` tip) was
resolved by rebasing T435 onto T434's already-merged state and regenerating fresh — not
hand-editing JSON — independently confirmed clean before merging.

## Completed this session (this checkpoint's covered work)

| Item | Outcome |
|------|---------|
| T434 (Wave 2 evidence) | Done. 19/23 agents + 0/17 commands (14/17 blocked solely on golden-case gap) genuinely evidence-complete, with T434's own row still open. `docs/artifacts/phase3-wave2-promotion-v1.md`. MR !266 (dispatch), !267 (evidence). |
| T435 (Wave 3 evidence) | Done. 10/28 genuinely evidence-complete (4 instructions + 6 skills), 9 of 10 unblocked. `docs/artifacts/phase3-wave3-promotion-v1.md`. MR !266 (dispatch), !268 (evidence, rebased onto T434). |
| T434/T435 closeout | MR !269. Ledger closed, both briefs' status flipped to `done`. |
| Wave 2/3 flip | MR !270. 28 components (19 agents + 4 instructions + 5 skills) genuinely promoted to `stable`, independently verified via direct diff review, fresh `check-maturity.py`, and two fresh adversarial probes (false-claim on the still-blocked `task-management`; Rails-removal on a newly-`stable` `product-owner`) — both caught correctly. |

## Real, independently-verified current state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (3 active, 272 completed)
- `python3 tests/run.py`: 514 tests, OK, skipped=24
- `python3 implementation/scripts/check-maturity.py --root implementation --verbose`: 77
  components, 0 failing — `agent/stable: 20`, `instruction/stable: 4`, `skill/stable: 7`,
  `command/stable: 0` (all 19 commands remain `experimental`, per the disclosed golden-case gap)
- `node implementation/scripts/sync.mjs --root implementation --check`: no drift, 563 files
- `python3 implementation/scripts/generate-registry.py --root implementation --check`: up to date
- A transient GitLab/Gitaly CI infrastructure failure occurred once this session (pipeline
  `2838058734`/`2838059475`, "CI configuration fetch from Gitaly timed out") — confirmed via
  `WebFetch` on the pipeline page as a genuine infrastructure issue, not a content problem; resolved
  by re-triggering fresh pipelines via the GitLab API (`POST /pipeline`,
  `POST /merge_requests/:iid/pipelines`), both of which succeeded on retry — recorded here in case
  the pattern recurs.

## Process notes worth carrying forward

- **The "avoid naming already-processed components in open task prose" discipline, established this
  round, should be treated as standing practice for any future Phase 3/4+ task brief**, not a
  one-off fix — any task brief that names a real registry component id, for any reason, while that
  brief is an open P0/P1 row, risks either (a) blocking that component's own future promotion
  (harmless if it's not currently `stable`) or (b) regressing it (harmful if it already is). Prefer
  pointing to artifacts/ledger rows over repeating ids in new prose.
- **`glab ci retry` panics when a pipeline has zero jobs** (e.g. after a Gitaly config-fetch
  timeout, since no jobs were ever created to retry) — use the GitLab API directly
  (`POST /projects/:id/pipeline` or `POST /merge_requests/:iid/pipelines`) to trigger a fresh
  pipeline instead of relying on `glab ci retry` in that specific failure mode.

## Token metrics

Not separately tracked against a phase budget this session.

## Next steps

- **T436 (honest demotion pass)** depends on both T434 and T435 (now done) — not recorded or
  dispatched this session. Per `plan-035`'s own framing, this needs both waves' actual outcomes
  first (now available in their closure artifacts) before deciding what, if anything, gets
  demoted to `experimental`/`deprecated` rather than left as an aspirational `beta`.
- **Two real, disclosed follow-up gaps remain, neither dispatched this session:** (1) 14 commands
  need golden-case coverage authored under a disclosed protected-path exception before they can
  reach `stable` (`docs/artifacts/phase3-wave2-promotion-v1.md` §4); (2) 18 of Wave 3's 24 skills
  remain genuinely untouched, with 4 flagged as having real, pre-existing content defects
  (`docs/artifacts/phase3-wave3-promotion-v1.md` §4) that should be fixed before a future wave
  attempts their promotion evidence.
- **T456/T457/T458** (Phase 5 follow-ups) and **`feature/T475-codex-platform-integration`** remain
  exactly as prior checkpoints left them — untouched this session.
