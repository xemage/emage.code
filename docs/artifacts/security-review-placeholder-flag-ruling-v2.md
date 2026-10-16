# Artifact: security-review-placeholder-flag-ruling-v2.md

> Immutable once produced; revisions bump `<N>`. Continues `security-review-placeholder-flag-ruling-v1.md`.

## Metadata

- **Reviewer**: security-engineer (read-only; no write tool). Recorded by the orchestrator from the reviewer's report.
- **Task**: T606 (plan-114). **Reviewed**: `placeholder-flag-ruling-v2.md`.
- **Date**: 2026-10-09
- **Not read**: `placeholder-flag-ruling-v1.md`, the tests, `poc-security-engineer-tool-scoping-v2.md`. `poc_scan.py`,
  `poc-security-engineer.md` (in full) and `poc-orchestrator.md:40-114` were read.

## Verdict: FAIL (narrow, curable in v3)

All v1 conditions (SEC-1..SEC-7, N-1) are met in substance; SEC-1 is fixed everywhere and not reintroduced. The FAIL rests
on one new HIGH in the scanner spec of the option v2 recommends for Question 2. 0 critical, 1 high, 4 medium, 4 low.
No option is asked to be dropped.

| ID | Grade | Concern | Fix |
|---|---|---|---|
| V2-1 | **HIGH** | E-S2 (Question 2 Option A) omits E-S1's all-matches and scope rules. One hit is kept per rule, path and line (`poc_scan.py:300-304`), so a hostile line such as `password: "<placeholder>" # old_password: "RealSecret123"` could be labelled `template-ref` and graded non-blocking while hiding the real value. It also labels `log`/`commit` hits that name no single value. | Copy E-S1's rules into E-S2: label only if every match of the rule on the line is an exact shape (the dedup must not discard a second match first); label only `worktree` and `index` scope, never `log`, stash/history tree hits or redacted paths; compare in memory, never return matched text; add tests (mixed line gets no label, `log` hit gets no label); repeat the all-matches condition in the agent grading text. |
| V2-2 | MEDIUM | Hit versus finding is circular: E-P1 says a hit "is a blocking finding until a flag covers it" and a flag is void "if the hit belongs to an open blocking finding", so every flag is void as written. Missing: what runs when the user declines or the value proves real. | Separate "unresolved hit" (awaiting the user) from "open blocking finding" (classified as a real secret). A placeholder-looking hit follows the flag path; if declined or proven real, the exposed-secret steps start; a withdrawn flag on a real value reopens from the first commit. Say a covered hit is not a blocking finding. |
| V2-3 | MEDIUM | The register schema lacks `scope`, `commit`, `via` and `source`; a worktree flag could cover an index/stash/history hit of the same rule and path; count basis ambiguous; E-P1 does not say only `status: active` flags count. | Add the fields; define `hit_count` per rule, path, scope and commit in one scan call; honour only `active` flags in the named version. |
| V2-4 | MEDIUM | Option A grades three shapes non-blocking from a label alone, against the ruling's own constraint 13 ("no label is authority by itself"). The label `template-ref` on a bare `$NAME` that blocks is confusing. | Say choosing Option A is the user's standing decision for those exact shapes only; amend constraint 13 and E-P1 sentence 1 with that one named exception; label the bare shape differently (for example `template_shape: bare`); keep the three non-blocking shapes listed and counted. |
| V2-5 | MEDIUM | RA-7 and the shape set are understated: `<word>` as `[a-z][a-z0-9 _-]{1,30}` accepts `<hunter2>`; the accidental case (a developer replaces the words in `<your-password>` and leaves the brackets) is silent. | Require at least one separator between lowercase words and no digits (`<set-me>` passes, `<hunter2>` does not). Rewrite RA-7 and the Option A consequences (mixed line, scope limits, bracket-left-on, multi-word bracketed passphrase still not caught). |
| V2-6 | LOW | Register chain: `ref_containment` proves ancestry of some local ref, not content at that sha; `last_fetch_time` is the `FETCH_HEAD` mtime; the protected ref is not named. | Name `refs/remotes/origin/develop`; add a prompt-level check that the register path is not among the paths the reviewed branch changed against `develop`; add the local-ref point to RA-6. |
| V2-7 | LOW | `changeme`/`placeholder`/`00000000` are classic default credentials; the user is asked about a rule and path, not the line; a "verbatim" user quote may contain the value. | The proposal text says "classic default value; confirm no service accepts it, local ones included". Quote the user with any value replaced by `[value omitted]`. |
| V2-8 | LOW | The blind-spot list is incomplete (`poc_scan.py:99-101`, `:127`): unquoted values containing `(` or a quote, quoted values with the other quote kind or shorter than 8 characters, and leaders `(`, `=`, tab and quote. Replacing E-P2 under Option A would drop the remaining blind-spot statement. | List them in Question 2's Fact and in E-P2; state in E-S2 which leaders stay excluded and why; keep the remaining blind spots in the replacement text. |
| V2-9 | LOW | `poc-orchestrator.md:77` keeps "ephemeral local instance" for the revocation step in the same file as E-O1. | Add to E-O1: this does not change the step 1 skip condition, which concerns a real, uncommitted secret and keeps that finding blocking. |

## Recommendation (reviewer)

- **Question 1: Option 1** (user confirms each flag, no code). Fix V2-2, V2-3 and V2-7 in the E-P1/E-O1 text first.
- **Question 2: Option A, amended** with V2-1, V2-4, V2-5 required. If they are not accepted, Option B. Option C only as an interim, with E-P2 (extended per V2-8). No option removes the whole blind spot.

## Conditions for CONDITIONAL_PASS (owner: solution-architect, v3)

V2-1 fixed in E-S2 (mandatory); V2-2..V2-5 written into the edits or into Question 2's plain-words text; V2-6..V2-9 written in or listed as residuals; the Security Engineer re-reviews v3.
