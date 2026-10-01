# plan-094 — Align the three PoC skills with the T563 rulings (P35)

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-092-poc-contract-amendments.md` §4 (P35); `docs/artifacts/poc-contract-resolution-v1.md`.
**Scopes:** `T570`; follow-up `T571` (§4).

## 1. Why P35 next

Plan-093 left the queue empty. P35 is the smallest open item. It needs no protected path and no evaluator-hash
change: no golden case quotes the three skills, and all three are `experimental`, so maturity is unaffected. It
finishes what plan-092 started. The PoC commands and agents already follow T563's rulings, but these three skills
still teach the old vocabulary, and the skills are what PoC agents read.

## 2. Sequence

1. **`T570`** (Solution Architect, judgment, decision only): decide each skill's alignment. Output:
   `docs/artifacts/poc-skills-alignment-v1.md`.
   - `poc-evaluation` and `rapid-prototyping` are a direct application of P31.
   - `technical-debt-tracking` needs real judgment. It defines its own debt scorecard and ledger, which may rival
     `POC-DEBT-SCORECARD.md` (the P29a shape). It also uses four severity tiers and `XS…XL` effort (the P29b shape).
     Its promotion procedure creates task rows with a priority `should`, which `AGENTS.md` does not allow, in a
     format `AGENTS.md` does not use.
2. **Follow-up:** one implementation task, scoped from T570's artifact. A Backend Developer edits the source skills,
   then regenerates and declares root drift. No grant is needed.

The task is **P2**: it is experimental-skill wording with no maturity effect.

## 3. Parked items carried

- P32–P34 and P36–P37: unchanged (plan-092 §4, plan-093 §4).
- The 42-path root drift: clearing it needs your approval at the time.
- The `new-poc` `expect.py` docstring that still calls P11 "parked".

## 4. T570's decision and the follow-up

`poc-skills-alignment-v1.md` specifies edits E1–E14.

- `poc-evaluation` and `rapid-prototyping`: the outcome becomes binary. `rapid-prototyping`'s milestone markers keep `in_progress`.
- `technical-debt-tracking`:
  - (a) Its scorecard **is** `POC-DEBT-SCORECARD.md`.
  - (b) Scales change to `critical|medium|low` and `S|M|L`, with `critical` ⇒ `must_fix_pre_prod`.
  - (c) The debt ledger stays as a working register.
  - (d) Promotion now writes proposals that the orchestrator turns into tasks, with `should` → `P1`.

In §10 the orchestrator verified the artifact's unverified claims. Golden coupling was checked with `held-out` pruned: the `/discover-skills` fixture copies are checked for presence only. The orchestrator also approved the extension of the T542/FU-C precedent to skill files.

| Task | Covers | Protected paths? | Owner |
|---|---|---|---|
| `T571` | FU-1: E1–E14 in the three source skills, regeneration, and up to 21 root-drift declarations | No | Backend Developer |

**Parked (new):**
- **P38:** PoC skill/command duplication and checkpoint items (artifact §7: F1–F4, F6–F8).
- F5 joins **P33**.
