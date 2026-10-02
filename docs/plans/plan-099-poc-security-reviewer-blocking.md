# plan-099 — Make the PoC security reviewer block on critical findings (O1, SECURITY:HIGH)

**Created:** 2026-10-02
**Based on:** `docs/artifacts/security-review-poc-security-shortcuts-v1.md` § O1; `docs/artifacts/poc-security-shortcut-examples-v2.md` §13.2;
the user's decision of 2026-10-02 ("Scope it next as P1").
**Scopes:** `T578`.

## 1. Why, and why P1

The stable `poc-security-engineer` agent, backed by `poc-orchestrator`, routes critical PoC findings into debt
handoff instead of blocking. That includes an exposed secret or an obvious injection or authorization gap. It
contradicts `security-guidelines`' Immutable Constraint 1 and its rule that "CRITICAL and HIGH findings block merge".
The Security Engineer rated this **SECURITY:HIGH** and asked for a dedicated task, with any release that ships the
current text blocked.

**The user chose P1.** The defect row declares `agent/poc-security-engineer`, so `check-maturity` counts an open P1
defect against it. A `stable` claim would therefore fail. A dry run on `develop` showed that holding the agent at
**`beta`** passes: agents become 25 stable, 1 beta and 2 experimental, with 0 failing. **This scoping MR does both**:

- it adds the P1 row;
- it changes `maturity: stable` to `maturity: beta` in `agents/poc-security-engineer.md`;
- it regenerates the registry (`maturity` is source-only, so no projection changes);
- it updates the snapshot in `tests/functional/test_check_maturity.py`.

The agent returns to `stable` by a normal promotion after the fix merges and the P1 row closes.

## 2. Sequence

1. **`T578`** (Solution Architect, P1, decision only). It writes the exact amendments to `poc-security-engineer`,
   `poc-orchestrator` and the `rapid-prototyping` enforcement line. It also defines a secret-exposure procedure:
   revoke or rotate, and remove from history. History rewriting needs user approval under `security-guidelines` §
   Agent Safety Guards. Output: `docs/artifacts/poc-security-reviewer-blocking-v1.md`.
2. **Security Engineer review** of the ruling (read-only, recorded by the orchestrator).
3. **Implementation** (Backend Developer, P1, same `Affects`). It keeps the "The PoC orchestrator will handle
   escalation" sentence that `test_agent_escalation_consistency` requires.
4. **Re-promotion** of `poc-security-engineer` to `stable` once the P1 rows are closed.

## 3. Release note

Until this closes, no release should ship with the current text of `poc-security-engineer` and `poc-orchestrator`.
The Security Engineer recommended this. It is recorded here for the release manager.
