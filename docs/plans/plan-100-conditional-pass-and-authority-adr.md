# plan-100 — CONDITIONAL_PASS merge semantics (P39) and ADR-008 on document authority (P34b)

**Created:** 2026-10-02
**Based on:** the user's decisions of 2026-10-02 on P39 and P34b; `docs/artifacts/gate-verdict-consistency-v1.md` §13.3;
`docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md`.
**Scopes:** `T580`, `T581`. They run in parallel because they touch disjoint files.

## 1. The user's decisions (2026-10-02)

- **Root refresh:** "yes, please do it". Done in MR !479: 73 paths refreshed, drift is 0. This repo's own loaded
  rules now carry the P42 and O1 security fixes.
- **P39:** the user asked for a recommendation ("OK for PoC? PoC should be possible to implement something fast with
  debts left for production"). The user then adopted it:
  - CONDITIONAL_PASS allows a merge, with its conditions tracked. On production they close before the next gate; on a
    PoC they become debt due by the production handoff.
  - FAIL blocks.
  - Security HIGH/CRITICAL findings and constraint breaches never qualify for CONDITIONAL_PASS.
  - The experimental `/code-review` command and `tech-lead` agent are amended to match `AGENTS.md`.
- **P34b:** the user adopted the recommendation to draft **ADR-008, "Knowledge-document authority"**:
  - `AGENTS.md` and stable instructions come first.
  - A command's contract governs its output.
  - Conflicts between peers are resolved by joint satisfiability, and then the narrower scope wins.
  - Maturity never ranks.
  - Anything else is escalated.

  It is drafted as `proposed`, and the user accepts it before it is used.

## 2. Sequence

1. **`T580`** (Solution Architect, decision only). It turns the P39 rule into exact amendments for `tech-lead.md:97`
   and `commands/code-review.md:51`, plus the `validation-gates:67` security nuance. A Security Engineer reviews it,
   then a Backend Developer implements it. Held-out golden coupling is detected through `scorecard.py --check`, never
   by reading held-out cases.
2. **`T581`** (Solution Architect, decision only). It drafts `docs/decisions/ADR-008-knowledge-document-authority.md`
   as `proposed`, codified from six precedents, with P40 and P43 as worked examples. The user then accepts or amends
   it, and P40 and P43 become schedulable.

Both tasks are P2.

## 3. T581 outcome: ADR-008 accepted (2026-10-02)

The architect drafted `ADR-008-knowledge-document-authority.md`, codified from the precedents. The user then answered the three review questions:

- Q1: **"Self-placement only"**. Nesting alone never decides.
- Q2: **"Treat as peers (Recommended)"**. Experimental instructions are peers.
- Q3: **"Keep unranked (Recommended)"**. Between `AGENTS.md` and the stable instructions, an uncontested declared precedence holds; otherwise the conflict escalates. The orchestrator aligned the ADR's `AGENTS.md` sub-rule with the option text the user chose.

The user then **accepted ADR-008**.

Its order of application: A, joint satisfiability; B, tier 1 (`AGENTS.md` and stable instructions, within their declared scope); C, the command contract; D, peer self-placement; E, escalate. Maturity never ranks.

**P40 and P43 are now schedulable** under ADR-008. Slices that self-placement does not decide escalate to the user by design.

## 4. T580 outcome: P39 ruling v4 (2026-10-07)

`conditional-pass-semantics-v1.md` went through three Security Engineer reviews to reach **v4** (`security-review-conditional-pass-semantics-v1.md`):
- v1: FAIL as scoped. SEC-001 (HIGH): a Tech Lead waiver could override a security FAIL. SEC-002 (HIGH): `/security-audit` failed only on CRITICAL.
- v2: CONDITIONAL_PASS. SEC-012: the Release Manager's risk acceptance did not apply the Q4 security exclusion.
- v3: CONDITIONAL_PASS. SEC-018 (R5 grades) and SEC-019 (B1 adjacency).

v4 meets every condition. The orchestrator verified it in v4 §16, because the producing agent hit a usage limit before handing back.

**User decisions (2026-10-02):**
- Q1: keep the Tech Lead waiver, except for security.
- Q2: PoC conditions are recorded as debt by the handoff.
- Q3: the omitted, removed, disabled or weakened control class applies on both tracks.
- Q4: Release-gate conditions move to the next release cycle. Security is never a condition.
- Q7: a full-project audit treats the whole project as the code under review.
- Q8: a pre-existing security HIGH blocks unrelated merges.

| Task | Covers | Protected paths? | Owner |
|---|---|---|---|
| `T582` | FU-1: v4's 21 required edits plus C2, in 8 files (`tech-lead`, `release-manager`, `/code-review`, `/security-audit`, `/prepare-release`, `validation-gates`, `testing-strategy`, `code-review`); regenerate; declare drift | No | Backend Developer |

**Parked:**
- **FU-2**: refresh the stale quotes in three open golden cases. This is a protected path: it needs a grant and a v16 baseline authorized by the user. No results change.
- **FU-6**: the `security-engineer` SLA table and the `validation-gates:74` tiers.
- **FU-7**: `receiving-code-review:86`.
- **P40** slices S2–S4 and **P43**, both under ADR-008. Slice S1 is settled by T580.

## 5. Outcome (2026-10-07)

plan-100 is complete. ADR-008 was accepted (T581, !481). P39 was decided in T580 (!482) and applied in T582 (!483). CONDITIONAL_PASS semantics are now consistent across `AGENTS.md`, the orchestrator, `tech-lead`, `/code-review`, `validation-gates`, `code-review`, `testing-strategy`, `/security-audit`, `release-manager` and `/prepare-release`, and security findings never qualify. Root drift is 51 paths. FU-2 also covers the stale provenance note in the `validate-workflow-gate-verdict-sources` fixture (its copy of `validation-gates` no longer matches the live file; the result is unchanged).
