# Checkpoint 021 — Phase 1 complete, Gate G1 closed

> Written by the orchestrator immediately after T409's merge and ledger closeout. This is a real
> phase boundary: `docs/plans/plan-035-roadmap-v7-ground-up.md`'s Phase 1 (T410-T409, "Trustworthy
> Signal") is now fully done, and Gate G1 ("Signal" — no component may be promoted out of beta
> until an outcome eval exists that can fail it) is closed. Combined with `checkpoint-016`
> (Phase 0/Gate G0), `checkpoint-017` (T417), `checkpoint-018` (Phase 1 Layer 1 golden suite),
> and `checkpoint-019` (Layer 1 closed, Layer 2 pending), this is the canonical Phase 0 → Phase 1
> handoff. Future agents planning Phase 2/3/5 work need only these five checkpoints, not the full
> T400-T409 execution history.

## Summary

**Phase 1 of plan-035 (T410-T409) is fully done and genuinely merged to `develop`.** The last
open item, T409 ("Extend the T415 failure taxonomy to ingest Harbor trajectories"), closed
2026-09-08 after two independently-verified dispatch passes. All ten of Phase 1's
acceptance-criteria bullets (`plan-035` §2.4, immediately before "Gate G1 closes here") are now
independently confirmed met:

- `scripts/scorecard.py` runs the full golden suite from one command; deterministic re-runs
  produce identical output (T413).
- Golden baseline published with 9 recorded failures, clearing T411's ≥5 floor (T414).
- Held-out set never referenced outside `tests/golden/held-out/` (T412, three independent
  controls including T413's anonymization and T416's freeze).
- Every agent definition declares `tests/golden/**`/`scripts/scorecard.py` read-only (T416).
- Harbor oracle run passed 100% on the 5-task minimum (T417; a broader 25-task extended run came
  back 68%, reconciled by Tech Lead CONDITIONAL_PASS as non-blocking per the brief's own
  Criterion-5/7 reading).
- `scripts/tb-delta.sh` produces Arm A, Arm B, delta, and spread in one invocation (T419/T408);
  the two arms differ only in projection, proven by a programmatic config-diff on every
  invocation.
- Published delta states `k`, spread, model, and total cost (T407, `tb-delta-v6.12.0.md`).
- **Terminal-Bench and golden failures appear in one taxonomy** (T409, `failure-taxonomy-v1.md`
  §8) — this was the sole remaining unmet bullet as of `checkpoint-019`; it is now met.

**Gate G1 is closed.** Gate G4's evaluator-protection precondition, which `plan-035` states closes
at the same point as G1, is also closed (already satisfied by T416, confirmed untouched by T409's
own diff).

`docs/tasks/active-tasks.md`: 0 active rows. `docs/tasks/completed-tasks.md`: 256 rows, ledger
validator `PASS`.

## Completed tasks (this checkpoint)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T409 | Extend T415 failure taxonomy to ingest Harbor trajectories (one taxonomy, two sources) | devops-engineer, orchestrator | `docs/artifacts/failure-taxonomy-v1.md` §8 (new); 6 pattern files under `docs/benchmarks/failures/terminal-bench/`; combined `docs/benchmarks/failures/README.md` index; closes Gate G1 |

T407 (Terminal-Bench delta measurement, Inconclusive classification, ADR-004 guardrail demotion)
was already `done` as of the prior session (see `docs/decisions/ADR-004-tb-inconclusive-guardrail-
demotion.md`) — this checkpoint's contribution is exclusively T409 and the resulting Gate G1
closure, not new T407 work.

## G1 determination — how this was actually confirmed, not assumed

At the start of this session, `docs/tasks/active-tasks.md` (as last written) already recorded T407
as `done` and T409 as unblocked-but-undispatched. Before dispatching anything, the orchestrator
re-read `plan-035` §2.4 Phase 1's acceptance-criteria checklist against real evidence for every
bullet, rather than assuming "T407 done" implied "G1 closed." Nine of ten bullets were
independently verifiable as met from already-merged artifacts. The tenth —
"Terminal-Bench and golden failures appear in one taxonomy" — was confirmed unmet by reading
`docs/artifacts/failure-taxonomy-v1.md` §7 ("Reuse notes for T409") directly: that section, written
by T415, explicitly names T409 as the pending extension, and no such extension existed in the
repo at session start. ADR-004 independently corroborated this ("T409 ... remains a separate
dispatch decision not made by this ADR"). This determination — not an assumption that closing T407
alone closed the gate — is what led to authoring and dispatching `task-T409.md`.

## T409 dispatch and verification detail (two passes, not one)

**First pass (MR !215, commit `2535a54`).** Dispatched `devops-engineer` combined T407's two
Harbor trajectory sources (local k=3 run and remote Design A's 3 successful passes, the latter
read via read-only SSH from `10.10.160.11`, never copied into the repo) and classified genuine
Terminal-Bench task-level failures into T415's three-axis scheme. The orchestrator independently
re-derived the same extraction method (`exception_info is None and reward == 0.0`) directly
against raw `result.json` files on both hosts rather than trusting the agent's own counts — most
of the self-report held up exactly (157 genuine failures, 57 infra-exclusions, two spot-checked
verbatim evidence citations byte-for-byte correct against raw verifier output) — but this
independent check also found a real, undisclosed gap: the headline "17 distinct task names" was
the **local-source-only** count, not the true union across both sources (**21**, computed directly
from raw data). Three genuine, non-infra failing task names present only in the remote source
(`caffe-cifar-10`, `rstan-to-pystan`, `train-fasttext`; 6 trials) were absent from every pattern
file and every summary count, with no exclusion note anywhere. A smaller arithmetic slip was also
found (§8.3 stated "45 local passes," the real figure is 41). **Not merged.**

**Second pass (same MR !215, commit `2f7927a`).** Sent back to the same agent on the same
branch/MR (not a new one) with the exact three trials and the orchestrator's own independent read
of their raw verifier output. The agent independently re-verified each flagged trial via SSH
before acting, correctly split `train-fasttext`'s 4 failing trials across two distinct existing
patterns rather than forcing one fit (3 `FileNotFoundError` cases vs. 1 loadable-but-wrong-value
case), and created a 6th pattern file (`verifier-crashes-on-missing-dependency.md`, new
`behavior`/`mechanism` axis pair) for `caffe-cifar-10`'s fatal in-process `SIGABRT` crash, with a
documented "why this fits none of the other 5" argument. Corrected every headline count and the
arithmetic slip; added a new §8.6 documenting the gap and fix rather than silently rewriting the
original narrative.

**Orchestrator's independent re-verification of the fix (not trusting the second self-report
either):** re-checked the `train-fasttext` split and the new pattern file directly against raw
data on the remote host (exact match); independently re-derived the 17/20/21 local/remote/union
task-name arithmetic from raw data (exact match); confirmed the 5→6 pattern and 65→71
cited-trial-hash counts arithmetically; `python3 tests/run.py` fresh after both commits (377
tests, exit 0 each); `tests/functional/test_golden_held_out_isolation.py` after both commits
(8/8 each); `git diff` against `develop` for `tests/golden/**`/`scripts/scorecard.py` empty after
both commits (T416's protected paths untouched throughout); `docker ps -a`/`docker images`
checked directly on the remote host — nothing dated after 2026-08-25, confirming no new
Terminal-Bench trial, Docker run, or paid-API activity from either dispatch pass, per this
session's hard scope constraint on T409 (local/remote-read-only analysis, no new real-cost
activity). CI green on both pushes; MR !215 squash-merged to `develop` (squash commit `b96d1b9`,
merge commit `24781c1`).

## Key decisions

- **T409 did not require a separate real-external-cost confirmation gate**, unlike T407's
  Terminal-Bench trial dispatches. It classifies data T407 already produced; no new trial,
  container run, or paid API call was made or needed, and this was independently confirmed (not
  merely asserted) at both dispatch passes.
- **A defective first pass was sent back rather than accepted with a caveat.** Given T409's role as
  the literal artifact closing Gate G1's last acceptance bullet, an inaccurate headline count in
  that artifact was treated as a real defect requiring a fix-and-reverify cycle, not a cosmetic
  nit to note and move past — consistent with this whole phase's established practice of not
  letting self-report drift stand once caught (T407's cost-figure correction, T419's "valid" claim
  correction, T415's held-out narrative fix, etc.).
- **Gate G1 closure is recorded in the plan's own gating language, not just the task ledger** —
  `active-tasks.md`'s closure note explicitly states which acceptance-criteria bullets are met and
  cites the specific artifacts, so a future reader does not need to re-derive the determination
  from scratch.

## Artifacts produced (this checkpoint)

- `docs/artifacts/failure-taxonomy-v1.md` §8 (new) — Terminal-Bench/Harbor trajectory extension
- `docs/benchmarks/failures/terminal-bench/*.md` (6 pattern files)
- `docs/benchmarks/failures/README.md` (combined golden-suite + Terminal-Bench index)
- `docs/tasks/task-T409.md` (brief + Completion addendum)
- MR !214 (`docs/phase1-t409-dispatch` → `develop`, T409 dispatch/brief authoring)
- MR !215 (`feature/T409-tb-harbor-taxonomy` → `develop`, T409 implementation, two commits
  `2535a54`+`2f7927a`, squash commit `b96d1b9`, merge commit `24781c1`)
- MR !216 (`docs/phase1-t409-closeout` → `develop`, ledger closeout + Gate G1 closure record)

`develop` HEAD is now `4dfda40`.

## Blockers (active)

None. Phase 1 is fully closed with no open items.

## Open questions / risks flagged, not yet resolved

None new this checkpoint. Carried forward from `checkpoint-019`/ADR-004: Terminal-Bench's role for
future releases is now a **no-harm guardrail** (subsequent releases must not show a delta below
−4pp), not an improvement signal — the golden suite is the sole load-bearing progress signal until
Phase 6 exists. This does not affect Phase 1's own closure, which is complete regardless of T407's
classification outcome per ADR-004's own reasoning.

## Token usage

| Phase | Budget | Spent (this session: T409 dispatch, 2 verification passes, 1 re-dispatch, ledger closeout, checkpoint) | % |
|-------|--------|----------------------|---|
| Phase 1 closeout (T409 authoring/dispatch/2-pass verification/re-dispatch/merge, ledger closeout, checkpoint) | ~30k (task-level estimate consistent with T415/T416's own scope) + independent-verification overhead (raw SSH data reads on 2 hosts, twice) | Not separately metered this session; qualitative note: the independent-verification overhead (re-deriving extraction stats from raw data on both hosts, twice, once per dispatch pass) is the same recurring pattern `checkpoint-018`/`checkpoint-019` already flagged — "ledger done" claims cost more to confirm than their nominal task-level estimate, and this session's second verification pass caught a real gap the first one would have missed | — |

## Next steps — what Phase 1's closure unlocks

Per the phase graph (`plan-035` §2.3):

1. **Phase 3 (Maturity Ladder, v6.13.0-v6.15.0) is gated on G1 *and* G2** (Phase 2, MCP
   Conformance). G1 is now closed, but **Phase 2 (T420-T423) has not been dispatched or started —
   confirmed by grepping `completed-tasks.md`/`active-tasks.md` for T420-T423, zero matches.**
   Phase 3 is therefore **not** yet startable; Phase 2 would need to be proposed and approved
   first. Phase 2's own status block already flags it needs re-scoping at kickoff (T421/T423 may
   be partially or fully subsumed by `plan-033`/`plan-034`'s already-done MCP hardening work —
   re-verify before treating either as fresh scope).
2. **Phase 5 (Persistent Memory/RAG, v6.17.0) is gated on G0 only**, already closed since Phase 0.
   Confirmed no Phase 5 work exists yet (`completed-tasks.md`/`active-tasks.md` grepped for
   T450-T456, zero matches) — Phase 5 is independently startable now, in parallel with a
   prospective Phase 2, without waiting on G1 (it never needed G1) or on Phase 2/3 at all.
3. Neither Phase 2 nor Phase 5 has been proposed to the user this session — this checkpoint records
   what is *unlocked*, not a decision to start either. That remains the user's call, consistent
   with this repo's Plan-Approve-Execute protocol (no task brief is authored for either phase on
   the strength of this checkpoint alone).
4. Phase 4 (Task-Tier Routing) remains gated on G2, itself gated on Phase 3's Wave 1 — still several
   steps out.
5. Phase 6 (Closed Loop, v7.0.0) remains gated on G3 (Phase 5) and G4 (already-satisfied
   evaluator-protection precondition, but G4 also requires the rest of its own phase's conditions
   per `plan-035` §2.2) — not yet startable.

## Compression note

This checkpoint plus `checkpoint-016-phase0-ground-truth-complete.md`,
`checkpoint-017-t417-harbor-oracle-smoke-complete.md`,
`checkpoint-018-phase1-layer1-golden-suite-complete.md`, and
`checkpoint-019-phase1-layer1-closed-layer2-pending.md` together are the canonical Phase 0 → Phase
1 handoff. Subsequent agents planning Phase 2, Phase 3, or Phase 5 work receive **only**: these
five checkpoints + their own task brief + the relevant `plan-035-roadmap-v7-ground-up.md` phase
section — not the full T400-T409 execution history.
