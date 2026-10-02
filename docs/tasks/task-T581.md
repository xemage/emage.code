# T581 — Draft ADR-008, knowledge-document authority (P34b), per the user's decision

**ID:** T581
**Owner:** Solution Architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-02
**Based on:**
- `docs/plans/plan-100-conditional-pass-and-authority-adr.md`
- `docs/plans/plan-095-user-decisions-p34-p36-root-refresh.md` (P34b)
- `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- `docs/decisions/_template.md`

## 1. What and why

ADR-007 ranks command contracts against `AGENTS.md`, stable instructions and the command's own clauses. It does
**not** rank agent definitions or skills against each other, or against commands. This gap is P34b. Six rulings have
worked around it, each with a one-off precedent or approval.

The user has decided to codify the practice (2026-10-02, relayed verbatim). Asked to "draft ADR-008 'Knowledge-document
authority' (AGENTS.md and stable instructions first; the command contract governs its output; peers resolved by joint
satisfiability, then narrower scope wins; maturity never ranks; otherwise escalate)?", the user chose
**"Draft ADR-008 (Recommended)"**.

Draft it as **`proposed`**. The user accepts it before it is used.

## 2. The precedents to codify, not invent

Read each precedent and quote it. The ADR states what these rulings actually relied on.

| Ruling | Where | What it relied on |
|---|---|---|
| T542 (agent file vs `git-workflow`) | `docs/tasks/completed-tasks.md` (T542 row) | ADR-007 branch 1 applied by analogy to an agent file |
| T563 FU-C (agent vocabulary) | `docs/artifacts/poc-contract-resolution-v1.md` §1.4, §9.2 | agent self-subordination; T542 precedent |
| T570 (skill files) | `docs/artifacts/poc-skills-alignment-v1.md` §1, §10.2 | skills' own PoC self-descriptions; precedent extended to skills |
| T572 (rival verdict formats) | `docs/artifacts/gate-verdict-consistency-v1.md` §1 | joint satisfiability of MUSTs; one verdict per gate; declared scope |
| T574 (skill vs command overlaps) | `docs/artifacts/poc-skill-command-overlaps-v1.md` §1 | joint satisfiability; skill accompanies the command |
| T576/T578 (security examples, PoC reviewer) | `docs/artifacts/poc-security-shortcut-examples-v2.md` §1; `poc-security-reviewer-blocking-v3.md` §1 | instructions stating their own precedence; self-subordination |

## 3. What the ADR must decide

These are the user's five points. Make each one precise and testable.

1. **`AGENTS.md` and stable instructions outrank** every agent, skill and command. Define what "stable instruction"
   means, and say whether `AGENTS.md` and a stable instruction rank against each other. ADR-007 left that open.
2. **A command's declared output contract governs its output** (ADR-007). The skills and agents it invokes supply
   method. They may specialise the contract but may not override it.
3. **Peers** (skill vs skill, agent vs skill, agent vs agent):
   - First apply **joint satisfiability**: if both MUSTs can be met, there is no conflict.
   - If a real contradiction remains, the document whose **declared scope is narrower and more specific to the
     subject** wins, and the other is amended to point to it.
   - Define how "declared scope" is read: the description, the Rails, and `applyTo`.
4. **Maturity never ranks.**
5. **Otherwise escalate** to an ADR or to the user.

Also cover:
- **Relationship to ADR-007.** ADR-008 extends ADR-007 and supersedes nothing in it. Check that it does not
  contradict ADR-007's branches.
- **Worked examples, not rulings.** Show how ADR-008 would frame **P40** (verdict *criteria* that differ across
  `validation-gates`, `code-review`, `testing-strategy`, `qa-engineer` and `security-engineer`) and **P43** (two binary
  PoC verdicts: the prototyping `[CHECKPOINT]` and the evaluation). Do not decide them.
- **Consequences:** which past one-off approvals ADR-008 makes routine, and what new risk it introduces.
- **Validation:** how we will know the ADR works.

## 4. Output

`docs/decisions/ADR-008-knowledge-document-authority.md`, following `docs/decisions/_template.md`, with
**Status: proposed**. Also hand back a summary listing the precedent quotes you relied on.

## 5. Constraints

- **You have no Bash.** Mark unverified claims.
- Write exactly one file. Hand it back uncommitted. Do not edit this brief.
- Read-only. Do not open `tests/golden/` at all.
- T580 (CONDITIONAL_PASS) is being decided in parallel. Do not rule on P39.
- **Do NOT run `glab mr merge` or any merge/approve API, and do not commit or push.**

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity `critical` |
`major` | `minor`. If the precedents do not support one of the user's five points as stated, report it. Do not force it.
