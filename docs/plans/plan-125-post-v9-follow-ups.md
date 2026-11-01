# plan-125 — Post-v9.0.0 follow-ups: debt register v4 and the token-docs batch C

**Created:** 2026-11-01
**Based on:** `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v3.md`; the orchestrator's overview of 2026-11-01 (register v4 and the deferred LOW batches A to F); the user's answer of 2026-11-01, verbatim: "v4 + C go".
**Scopes:** `T713`, `T714`.

## Goal

One current debt list after v9.0.0 (register v4), and the token-documentation and security-runtime LOW items that adopters copy from or rely on (batch C).

## Task Decomposition

1. **T713** (tech-lead): `docs/artifacts/tracked-debt-register-v4.md`, a delta on v3 (398 ids): the status now of every v3 id that is `open`, `tracked-LOW` or `accepted`; the closures of plan-124 (SEC-T662-01, SEC-T678-03, SEV-T690-07, SEC-T702-07, SEC-T712-01 to -04 and -06, SEC-T689-01/-03/-06, SEC-T699-01, SEC-T689-02 in part, TD-T697-08 ruled LOW); one row per new id from the plan-124 reviews and gates (T700 audit, T701/T703 review, T702 grading, T712 review, T707 QA gate, T708 Tech Lead review, T709 security re-check, T710 decisions); SEC-T686-03 and SEC-T686-06 from the tag pipeline (checkpoint-040 § 4); the user's decisions since v3; the LOW batches A to F as the open-items structure; T714 is in flight and treated as open. *Acceptance:* every v3 id that was open, tracked-LOW or accepted is accounted for; every new id has a row; status claims traceable or (unverified); the validators and link and team-health tests pass.
2. **T714** (devops-engineer): batch C. SEC-T701-01 (hibernation note at `implementation/PREREQUISITES.md:155-156`), SEC-T701-02 (where an environment-mode `.env` may live: outside every project directory, never committed, or drop `.env`), SEC-T701-03 (the gpg/keyring variant shows the full chain with `rm -f --`), SEC-T689-04 (`scripts/check-gitlab-token.py` must not end "ok" when the storage check could not run), SEC-T689-05 (path resolution vs the open descriptor; mount-namespace note), SEV-T690-02 (a trust-boundary paragraph in `implementation/SECURITY.md`), SEV-T690-04 (`implementation/runtime/security/executor.py`: an allowlisted child environment, `root_is_too_broad` for `allowed_root`, the missing credential-file names). *Acceptance:* every item fixed or reported with a reason; tests for the code changes; all gates and the suite pass; a Security Engineer review follows.

T713 and T714 run in parallel (no file overlap). The correction of the immutable record `security-review-t665-token-handling-v2.md` (part of SEC-T701-01) is a later version written by the orchestrator at closure.

## Constraints

- Subagents never merge, tag or release; the orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`; no `.env*` or credential files; never print a secret value.
- A root refresh, if T714 changes a projection, needs the user's explicit approval.
