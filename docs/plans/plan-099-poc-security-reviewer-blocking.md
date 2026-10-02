# plan-099 — Make the PoC security reviewer block on critical findings (O1, SECURITY:HIGH)

**Created:** 2026-10-02
**Based on:** `docs/artifacts/security-review-poc-security-shortcuts-v1.md` § O1; `docs/artifacts/poc-security-shortcut-examples-v2.md` §13.2;
the user's decision of 2026-10-02 ("Scope it next as P1").
**Scopes:** `T578`; follow-up `T579` (§4).

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

## 4. T578's decision, two security reviews, and the follow-up

`poc-security-reviewer-blocking-v1.md` → v2 → **v3**:

- **Review of v1:** CONDITIONAL_PASS (`security-review-poc-security-reviewer-blocking-v1.md`), with seven MEDIUM conditions:
  - M1: block on any omitted, removed or weakened control;
  - M2: severity floor, and secrets not yet committed;
  - M3: durable `blocked` task, so a stop or timeout can't bury a finding;
  - M4: issuer audit-log review, and an inventory of copies;
  - M5: GitLab purge, and a scan of all refs;
  - M6: scan before every push and merge;
  - M7: no waiver and no `accepted-risk` route.
- **Delta review of v2:** CONDITIONAL_PASS (`security-review-poc-security-reviewer-blocking-v2.md`), with one new MEDIUM (R2-6, a presence check for required controls) and seven LOW wording fixes. v3 adopts all of them verbatim.

**User decisions, 2026-10-02:**

- A declined history rewrite may close a finding only under strict conditions: revocation confirmed, no unrecognised use, not key material.
- The presence check is accepted, so PoCs will block more often.
- QD is kept strict: no audit logs means the finding stays open.

In v3 §16 the orchestrator verified that all 12 edits apply uniquely on develop `c523415` and that every reviewer phrase is present.

| Task | Covers | Protected paths? | Owner | Priority |
|---|---|---|---|---|
| `T579` | FU-1: v3's 12 edits in `poc-security-engineer`, `poc-orchestrator` and `rapid-prototyping`, then regenerate and declare drift | No | Backend Developer | **P1** (`Affects: agent/poc-security-engineer`; keeps the agent at `beta`) |

**Re-promotion** of `poc-security-engineer` to `stable` follows once T579 closes.

**Parked:**

- L4/X5: replace `execute` with a fixed-command scanner.
- A security carve-out for `code-review:150`'s Tech Lead waiver.
- X1–X6 (v3 §12).

## 5. Outcome (2026-10-02)

O1 is fixed. T579 (!477) applied v3. The archival MR closes T579's P1 row and **re-promotes `poc-security-engineer` to `stable`** (check-maturity: 79 components, 0 failing; agents 26 stable / 2 experimental). The Security Engineer's release block on the old text is lifted, because the fixed text is now on `develop`. The repo-root copies stay stale (73 declared drift paths) until a root refresh the user approves. Still parked: L4/X5 (replace `execute` with a fixed-command scanner), a security carve-out for `code-review:150`'s waiver, and X1–X6.
