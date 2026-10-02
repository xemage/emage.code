# Security delta re-review of `poc-security-reviewer-blocking-v2.md` (T578 / O1)

> Filename: `security-review-poc-security-reviewer-blocking-v2.md`. Immutable once produced. Revisions bump `<N>`.
> This file is the delta re-review. The first review is `security-review-poc-security-reviewer-blocking-v1.md`.

## Metadata

- **Reviewer**: security-engineer. Read-only delta review of the changed After texts.
- **Recorded by**: orchestrator, who transcribed the reviewer's hand-back on 2026-10-02.
- **Reviewed**: `docs/artifacts/poc-security-reviewer-blocking-v2.md` against the v1 conditions, `security-guidelines.md`
  and GitLab's documentation on removing sensitive data.
- **Outcome applied in**: `docs/artifacts/poc-security-reviewer-blocking-v3.md`.
- **Reviewer's limitation**: the reviewer could not byte-compare against its own original wording, because the v1
  review record had not been written to disk yet. It checked v2 against v2's change log, the substance of each
  condition, and the authority text instead. Every `security-guidelines` line that v2 cites is correct.

## Verdict: CONDITIONAL_PASS

v2 meets every v1 condition. Two are met by equivalents the reviewer accepted:
- **M3**: v2 adds "Apart from the timebox verdict below,", which repairs a contradiction in the reviewer's own wording.
- **M5**: v2 adds a tip-only scan that applies only on the user-decided declined path.

The reviewer found no CRITICAL or HIGH issue in the changed texts read together. The checks covered:
- the declined-rewrite path, which no agent can reach on its own decision;
- the "not yet committed" path;
- the durable `blocked` task, which complies with `AGENTS.md`'s archival invariant because `blocked` is not
  terminal;
- the scan coverage.

| Condition | Status |
|---|---|
| M1, M2, M4, M6, M7, L1, L2, L3, L5 | Met |
| M3, M5 | Met-equivalent (accepted) |
| L4 | Parked as X5; not a condition |

## New findings

- **R2-6 (MEDIUM): omitted controls have no detection duty.** M1 makes an omitted required control blocking, but
  § Scope only asks the reviewer to "flag obvious high-risk issues". So M1's blocking class would rest on chance.
  - **Fix:** new edit E2a, a Scope bullet: check that the controls `security-guidelines.md` requires for the code
    the PoC contains are present and enforced. "This is a presence check, not a full OWASP-style audit."
  - **Disclosure the reviewer asked to be made**: PoCs will block more often.
  - **User decision, 2026-10-02**: "Accept the presence check (Recommended)".
- **R2-1 (LOW):** step 4's closure conditions are adjusted for the not-yet-committed path. The step 1 skip is
  confirmed, "not applicable" is defined, and the scan also covers the working tree, index and stashes.
- **R2-2 (LOW):** the declined path requires an explicit decline. With no access or audit logs, condition (b) is not
  met.
  - The reviewer raised **QD** for the user: should an ephemeral-local secret satisfy (b) without logs?
  - **User decision, 2026-10-02**: "No, keep it strict (Recommended)".
- **R2-3 (LOW):** the E6 phrase "first pushed" is replaced by "every push that carries a delegated agent's commits not
  yet checked".
- **R2-4 (LOW):** scanner output must be redacted so that no value is printed.
- **R2-5 (LOW):** wording consistency. E1 now includes "omitted". E4 gets an explicit antecedent.
- **R2-7 (LOW):** the surviving task is P1 or higher. Its owner is `poc-orchestrator`, with "awaiting user: step 1"
  in the title, while the user's step 1 is pending, because ledger owners must be agent names. It needs a brief
  (C7) and `**Affects:** —` (C11).
- **R2-8 (LOW):** GitLab roles are corrected. Remove blobs and Redact text require the project **Owner** role.
  Repository cleanup requires Maintainer or Owner.

## Answers to the ruling's v2 questions

- **QA: yes.** Add the presence-check Scope bullet (R2-6).
- **QB: owner.** Use `poc-orchestrator` with "awaiting user: step 1" in the title (R2-7).
- **QC: confirmed; no edit needed.** On timebox expiry the PoC records the Rule 3 verdict and stays open and
  `blocked`. Remediation may continue. A stop triggers the separate-task rule.

## Conditions before FU-1

- v3 adopts R2-6 together with the user-accepted disclosure.
- v3 adopts R2-1 to R2-5, R2-7 and R2-8.
- If v3 adopts these After texts verbatim, no further review is needed. The orchestrator's phrase check is
  sufficient.
- The release block on the current text of `poc-security-engineer` and `poc-orchestrator` stands until FU-1 merges.
