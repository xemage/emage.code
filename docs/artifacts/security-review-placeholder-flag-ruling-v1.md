# Artifact: security-review-placeholder-flag-ruling-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no write tool). The orchestrator recorded this from the reviewer's report.
- **Task**: T606 (plan-114). **Reviewed**: `placeholder-flag-ruling-v1.md`.
- **Date**: 2026-10-09
- **Not read by the reviewer**: `security-review-poc-security-audit-code-v2.md`, `poc-security-engineer-tool-scoping-v2.md` (relied on the ruling's quotations), the test files. No tests were run.

## Verdict: FAIL (narrow, curable in v2 of the ruling)

The design is sound: a flag in a register that the orchestrator names, created only by the user, is the right shape.
Option 1 is the right option, and it touches neither the scanner nor the F-8 text. The verdict rests on one HIGH
wording defect in the held edits.

| ID | Grade | Concern | Fix |
|---|---|---|---|
| SEC-1 | **HIGH** | E-P1, E-O1 and the user question say a flag records that the value authenticates nowhere "or only on an ephemeral local instance". That clause is R8's skip condition for the revocation step, not the definition of a placeholder (R1: "cannot authenticate anywhere"). A working local-instance password would become a non-blocking LOW although committed, which breaches Immutable Security Constraint 1. (Orchestrator checked: the clause is in the ruling's held edits at `:267`, `:278` and in the user question.) | Delete the clause in all three places. A placeholder authenticates nowhere. Add: a flag on a value that authenticates anywhere, including a local instance, is void and the hit is a blocking finding. Allowing committed local-dev credentials would be a separate decision to amend Constraint 1 at source. |
| SEC-2 | MEDIUM | Value swap on a flagged line is understated: a developer replacing the placeholder with the real key is the common, non-hostile case; "does not exceed `max_hits`" is too loose; for `via:log` the key is rule plus commit. | Void a flag when its file changes (record the flag-time commit; the orchestrator passes "paths modified since flag commit"). Use `max_hits` as an exact count. A user-attested flag on a `via:log` hit needs the user to attest the whole commit diff. A provider-token flag is valid only for a published example value. |
| SEC-3 | MEDIUM | The mechanical re-read is not mechanical: one hit per rule, path and line (`poc_scan.py:300-304`), so a line with a placeholder plus a real value counts once; the working tree is the wrong source for index, stash and history hits; the class decision is an LLM reading attacker-controlled text. | Mechanical-class matching only for `scope=worktree`, and every match of the rule on the line must fit the class; otherwise the flag is `user-attested`. Same all-matches rule in E-S1. |
| SEC-4 | MEDIUM | The authority chain is sound against hostile commits and developer agents, not against a compromised or misled orchestrator; "latest version" lets a branch add a higher-numbered register. | The brief names the exact register file and commit sha. The reviewer honours only a register already on protected `develop`. The orchestrator quotes the user's message verbatim with its date and the report echoes path, sha and quote. A flag never closes a hit that belongs to an open blocking finding (R2). State in the ruling that a compromised orchestrator is outside the defence. |
| SEC-5 | MEDIUM | Option 2's residual is understated: `changeme` and `00000000` are classic vendor default credentials (A07); `user:changeme@prod-host` is a url-embedded-credentials hit decided by the host; the reviewer self-flags without the user seeing the hit (self-granted exception against R10/R12); a standing attestation covers code the user has not seen. | Remove Option 2 (and E-P1'/E-O1'). If kept: exclude `url-embedded-credentials`, worktree scope only, and list the reviewer's self-flags for same-session user confirmation. |
| SEC-6 | MEDIUM | A name-only flag on `.env`, `.pgpass`, `*.p12`, `credentials.json` and similar hides a file whose contents the content rules largely miss; the reviewer must not open it (R11). | Name flags only for template names (`.env.example`, `.env.sample`, `.env.template`); never for key-bearing names. The proposal must say the reviewer has not opened the file. |
| SEC-7 | LOW | (i) E-P1 grades flagged hits SECURITY:LOW but also says a flag relaxes no severity floor (contradictory); (ii) "flag id" has no register field; (iii) flags outlive the PoC into production handoff; (iv) proposals for user-attested flags are authored from attacker-controlled text; (v) "never drop a flagged hit" is prompt-enforced only. | (i) Reword: a hit covered by a valid flag is not a finding of a secret; a flag never applies to a value that authenticates anywhere. (ii) Add a `flag-id` field. (iii) Flags expire at handoff and are listed in the debt handoff. (iv) Say "unverified by the reviewer". (v) Add the planned text-pin tests. |
| N-1 | MEDIUM | The live skip heuristic (values starting with `$`, `<`, `{` or a space, `poc_scan.py:23-25`, `:119-127`, plus the unquoted rule's exclusion of leading `$ < { ( = " '`) is silent: no hit, so nothing can be flagged, listed or counted. Contradicts "the scanner stays strict". Only the user can reverse it (a user decision). | Put it to the user as a separate question. Recommended outcome: remove the skip and make `${VAR}`, `$NAME` and `<word>` visible hits carrying an exact `template-ref` label (rides with Option 3 or a follow-up, with a `RULES_VERSION` bump). Until then, tell the agent text that a clean scan excludes values starting with those characters. |

## Conditions for CONDITIONAL_PASS (owner: solution-architect, v2 of the ruling, before any E-edit is applied)

- SEC-1 fixed in all three places (mandatory).
- SEC-2..SEC-6 written into E-P1, E-O1 and E-S1, or accepted by the user as residuals after being told in plain words.
- Option 2 removed or rewritten per SEC-5.
- The N-1 question put to the user.
- The Security Engineer re-reviews the v2 edits.

## Recommendation

Option 1, amended as above. Defer Option 3 as a follow-up (it would remove the reviewer re-read and is the vehicle for
the `template-ref` label). Do not adopt Option 2 as written.
