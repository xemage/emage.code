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
