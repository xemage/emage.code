# T563 — Adjudicate the PoC-track contract conflicts (P11, P29, P30, P31)

**ID:** T563
**Owner:** Solution Architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T561
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-091-wave-3-promotion-and-poc-conflicts.md` §2; `docs/plans/plan-090-golden-wave-3.md` §2;
`docs/plans/plan-084-round-close-and-fired-triggers.md` §4 (P11, P12); `docs/decisions/ADR-007-command-contract-authority.md`;
`docs/artifacts/command-contract-resolution-v1.md` §B.

## 1. What and why

Golden wave 3 found that the PoC track's documents disagree on **where its artifacts go and what its outcomes
are**. The wave's cases deliberately asserted content only, so the disagreement is unresolved. Decide each conflict
under ADR-007 and write the decisions down. **Decision only** — do not edit any command, agent, instruction or
golden case; implementation is a follow-up sized by your artifact.

## 2. The four conflicts — verified by the orchestrator on `develop`

| # | Conflict | Sites |
|---|---|---|
| **P11** | **PoC plan filename.** `/new-poc` step 1 writes `docs/plans/poc-<slug>.md`; `/poc-demo` step 7 links the same. But the protocol `/new-poc` step 1 itself cites — `poc-orchestrator` PLAN PHASE — writes `docs/plans/plan-<ID>.md`, and `orchestrator.md` requires a `plan-<ID>.md` before any task row exists. | `new-poc.md:17`, `poc-demo.md:25`, `poc-orchestrator.md`, `orchestrator.md` |
| **P29** | **Debt scorecard — three homes, two formats.** `docs/decisions/poc-debt-<slug>.md` (`/new-poc` step 11, `/poc-demo` step 7); `POC-DEBT-SCORECARD.md` in the PoC root (`poc-guidelines`, **stable**); `TECHNICAL-DEBT.md` (`poc-orchestrator`, `technical-debt-narrator`, and `poc-guidelines`' legacy section). Formats differ: `poc-guidelines` uses effort S/M/L with three severity tiers; `/evaluate-poc` step 11 uses S/M/L/XL and CRITICAL/HIGH/MEDIUM/LOW. | `new-poc.md:37`, `poc-demo.md:27`, `poc-guidelines.md:103`, `evaluate-poc.md:59` |
| **P30** | **Checkpoint path (N1).** `/new-poc` step 14 writes `docs/checkpoints/checkpoint-poc-<gate>.md`; `AGENTS.md` § Checkpoint Protocol says `checkpoint-<SEQ>-<phase>.md`. **This defect class was already adjudicated for `/new-feature`** — not in ADR-007 itself, but in its application, `docs/artifacts/command-contract-resolution-v1.md` §B (`new-feature-real-checkpoint-format-drift`, T515). Read that ruling first. *(Corrected by the orchestrator before dispatch: the QA hand-back said "ADR-007 already ruled"; ADR-007 contains no mention of checkpoints.)* `/poc-demo` step 7 links the same path. | `new-poc.md:46`, `poc-demo.md:26`, `AGENTS.md` |
| **P31** | **Outcome vocabulary (N2).** `/evaluate-poc`'s Status allows `VALIDATED \| INVALIDATED \| INCONCLUSIVE`, and its failure mode prescribes `INCONCLUSIVE` for weak evidence. `poc-guidelines` (stable) Rule 4 says the outcome is **binary**, and its scorecard allows only `VALIDATED / INVALIDATED`. | `evaluate-poc.md:31,65`, `poc-guidelines.md:56,112` |

## 3. What to decide, per conflict

Apply ADR-007's ordered branches and **name the branch that fires**. In particular, establish from ADR-007 (and
`AGENTS.md`) **which document is the higher authority** in each pair — a `stable` instruction versus a command, an
agent definition versus a command, `AGENTS.md` versus a command. Do not assume; quote.

For each: the decision, the branch, the authority relied on, the exact files a follow-up would edit, and the
**golden coupling**. Four commands just became (or are becoming) `stable` on golden cases that assert content, not
paths (`team-status-dag-colour-code`, `new-poc-plan-hypothesis-format`, `poc-demo-hypothesis-status-evidence-gaps`,
`evaluate-poc-verdict-debt-reconciliation`). Say for each decision whether a case's quoted clause would change —
**you may read those four cases' `brief.md` and `expect.py` (read-only)**, which is a grant extension specifically
for this task. P31 in particular touches `/evaluate-poc`'s Status line, which its case quotes.

## 4. Output

`docs/artifacts/poc-contract-resolution-v1.md`: one section per conflict, then a follow-up table — task, files,
and whether it needs a protected-path grant (i.e. touches `tests/golden/**`).

## 5. Constraints

- **You have no Bash.** Say where a claim would need one; mark unverified claims as such.
- **Write exactly one file:** the artifact. Hand back uncommitted. Do not edit this brief.
- **Read-only** on everything else; `tests/golden/held-out/` must not be opened.
- A Backend Developer runs in parallel on the four command files' `maturity:` lines (T562). It does not change
  their bodies, so your quotes stay valid.

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If anything in this
brief is wrong — including the line numbers — report it.
