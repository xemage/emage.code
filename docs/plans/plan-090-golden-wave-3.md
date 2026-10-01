# plan-090 — Golden wave 3

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-072-phase9-golden-case-coverage.md` §3 (wave 3, left unscoped on purpose);
`docs/checkpoints/checkpoint-037-phase9-queue-empty-root-refreshed.md` §8.
**Scopes:** `T561`.

`plan-072` deliberately left wave 3 unscoped until waves 1 and 2 had tested the approach. Both did what the
plan hoped: each produced exactly one honest red case that blocked exactly one promotion while the greens passed
clean. Wave 3 covers the last five commands with no golden case — `/team-status`, `/validate-workflow`,
`/new-poc`, `/poc-demo`, `/evaluate-poc`, all `experimental`.

It is the weakest-grounded wave by design: the PoC three have no corpus at all (ADR-007 branch 4), and two parked
findings bear directly on it — **P9** (`/validate-workflow` likely always FAILs) and **P12** (the PoC debt
scorecard specified in two places). The brief tells the implementer to **report** both, not resolve them, and
says plainly that a red case here is a correct outcome.

After the wave: one baseline authorization from the user (v13), then — separately — a promotion run for whichever
of the five pass. P9 and P12 may become rows depending on what the cases show.

## 2. Outcome, and what it found

**Four green, one red** — `/validate-workflow` is the honest red, confirming P9. It is the third wave in a row with
exactly one red case. Every one of the 19 commands now has at least one golden case. Baseline v13.

**The PoC greens certify clause content only, not output paths.** Every output path `/new-poc` declares is
contradicted by another document, so the three PoC cases deliberately assert content (hypothesis format, evidence
gaps, debt reconciliation) and not where artifacts are written. A promotion task must say so rather than read
these greens as path conformance.

| # | Item | Trigger |
|---|---|---|
| P28 | **P9 confirmed** — `/validate-workflow` step 6 requires every gate to emit a VERDICT, but plan approval emits Approve/Revise/Reject and the architecture briefing declares no output. ADR-007 branch 1. Candidate exits: scope step 6 to the four verdict gates; cite the orchestrator's ARCHITECTURE GATE (which does emit a VERDICT) instead of the briefing; or give both workflow steps verdicts. | the wave-3 promotion run (it blocks `/validate-workflow` only) |
| P29 | **P12 wider than recorded** — the PoC debt scorecard has **three** homes (`docs/decisions/poc-debt-<slug>.md` in `/new-poc` step 11 and `/poc-demo` step 7; `POC-DEBT-SCORECARD.md` in `poc-guidelines`; `TECHNICAL-DEBT.md` in `poc-orchestrator` and `technical-debt-narrator`), with differing formats (S/M/L and three tiers vs S/M/L/XL and four severities). | a PoC-track adjudication task (with P30, P31, P11) |
| P30 | **N1** — `/new-poc` step 14 writes `docs/checkpoints/checkpoint-poc-<gate>.md`, contradicting `AGENTS.md`'s `checkpoint-<SEQ>-<phase>.md`; ADR-007 already ruled on this defect class for `/new-feature`. `/poc-demo` step 7 links the same path. | same |
| P31 | **N2** — `/evaluate-poc`'s failure mode prescribes INCONCLUSIVE for weak evidence; `poc-guidelines` (stable) Rules 3–4 make the outcome binary, and its scorecard allows only VALIDATED / INVALIDATED. | same |

P11 (plan filenames) is confirmed and belongs with P29–P31: the protocol `/new-poc` step 1 cites writes
`docs/plans/plan-<ID>.md`, not `docs/plans/poc-<slug>.md`.

