# plan-098 — Stop the PoC track modelling forbidden security shortcuts (P42)

**Created:** 2026-10-02
**Based on:** `docs/artifacts/poc-skill-command-overlaps-v1.md` §13 (O1) and §16.3 (P42).
**Scopes:** `T576`; follow-up `T577` (§4).

## 1. Why P42 next

Two documents set out the `POC-DEBT` model examples that PoC agents copy: the stable `poc-guidelines.md` instruction
and the `rapid-prototyping` skill. Both include "No input validation". `rapid-prototyping` adds "disabled security"
and "CORS allow-all". These contradict the Immutable Security Constraints in the stable `security-guidelines.md`, which
forbid them "even in development or PoC mode" and state that they supersede `poc-guidelines`.

The guidance ships to every installed client project. It is also loaded into this repository's own sessions through
`.claude/rules/`. A security contradiction in shipped guidance outranks the remaining editorial items.

## 2. Sequence

1. **`T576`** (Solution Architect, judgment, decision only). It rules on each example and placement rule, says
   whether a positive rule should be added, and recommends a priority. Output:
   `docs/artifacts/poc-security-shortcut-examples-v1.md`. The precedence is stated by both instructions themselves,
   so no P34b ranking is needed.
2. **Security review.** Before implementation, a Security Engineer reviews the artifact's ruling read-only and
   reports back. That agent has no write tools.
3. **Implementation.** Amend `poc-guidelines.md` (stable) and `rapid-prototyping`, regenerate, and declare root
   drift. Priority is P1 or P2, decided by the user.

T576 is **P2**. It is a decision and declares no `Affects`, so it holds nothing back.

## 3. Parked items carried

- P39, P34b, P40 and P43, which wait on the user.
- P32, P33, P41 and P44.
- The `new-poc` docstring.
- Root drift, which the user approves at refresh time.

## 4. T576's decision, the security review, and the follow-up

`poc-security-shortcut-examples-v1.md` ruled every site. A read-only Security Engineer review returned **CONDITIONAL_PASS** (`security-review-poc-security-shortcuts-v1.md`), with two MEDIUM conditions:

- F1: widen the new rule from the Immutable Constraints to every `security-guidelines` control.
- F2: use `sslmode=verify-full`, not `require`.

There were also five LOW items. **v2** (`poc-security-shortcut-examples-v2.md`) meets all of them and supersedes v1. v1 is kept as the record.

In v2 §13 the orchestrator confirmed that all 11 edits apply uniquely on develop `7da064a`, and accepted v2.

| Task | Covers | Protected paths? | Owner | Priority |
|---|---|---|---|---|
| `T577` | FU-1: v2 R1–R11 in `poc-guidelines` and `rapid-prototyping`, regenerate, declare root drift | No | Backend Developer | **P2** (user, 2026-10-02) |

**O1 is re-rated SECURITY:HIGH by the reviewer.** The stable `poc-security-engineer` routes exposed secrets and injection/auth gaps to debt instead of blocking. By the user's decision of 2026-10-02 it gets its **own task at P1**, scoped next (plan-099). It is not parked.

## 5. Outcome (2026-10-02)

P42 is fixed by T577 (!474). The shipped PoC guidance no longer teaches forbidden security shortcuts, and it now states that every `security-guidelines` control applies to PoC code. The repo-root copies stay stale (61 declared drift paths) until the next root refresh the user approves. O1 continues in plan-099 (T578, P1).
