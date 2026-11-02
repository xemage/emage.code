# plan-130 — Tracked-debt register v5

**Created:** 2026-11-02
**Based on:** `docs/artifacts/tracked-debt-register-v4.md` (443 ids), plans 126 to 129 and their outcome sections, and the security reviews `security-review-t715-t716-batch-b-v1.md`, `security-review-t718-t720-batch-d-v1.md`, `security-review-t722-t725-batch-a-v1.md` and `security-review-t726-t728-batch-e-v1.md`. The user's answer of 2026-11-02, verbatim: "v5 go".
**Scopes:** `T729`.

## Goal

Batches B, D, A and E (plans 126 to 129) closed most of v4's tracked-LOW items. They also produced about 45 new ids. v5 collects all of this into one current debt list and groups the open items into batches, so that the next fixing round and the next release start from it.

## Task Decomposition

1. **T729** (tech-lead): write `docs/artifacts/tracked-debt-register-v5.md`, a delta on v4, in v4's structure.
   - **Every v4 id that is `open`, `tracked-LOW` or `accepted`:** give its status now. Cite the plan outcome, the completed-task row or the review that closed it, or write "Unchanged".
     - The plan outcome sections list the batch closures:
       - plan-126 (batch B: 17 closed; SEC-T677-01 partly closed; TL-T708-07 unchanged; SEC-T676-14 and SEC-T702-08 still tracked);
       - plan-127 (batch D, including the TD-T671-legacy re-read: P4 and P7 obsolete, P9, P11 and P12 fixed, P10 still open, P14, P15, T539 and T565 parked);
       - plan-128 (batch A: 14 closed, SEC-T663-02 not done);
       - plan-129 (batch E).
     - TD-T713-01 is decided by ADR-011 (Accepted).
     - SEC-T699-04 is decided ("Tie to the bearer (Recommended)").
   - **One row for every new id:**
     - from the four reviews: SEC-T715-01 to -04; SEC-T716-01 to -05; SEC-T720-01 (fixed) to -08; SEC-T722-01 to -05; SEC-T724-01; SEC-T725-01 to -03; SEC-T726-01 to -03; SEC-T727-01 to -05; SEC-T728-01 to -03;
     - from the plan outcomes: TD-T720-01; TD-T723-01; TD-T724-01; TD-T725-01; TD-T726-01 and -02; TD-T728-01 to -03;
     - any other id a plan-126 to plan-129 artifact mints.
   - **The user's decisions since v4, quoted verbatim:**
     - the four batch approvals: "B go", "D go", "A go", "E go";
     - ADR-011 with its end date;
     - O1;
     - root refreshes 23 and 24;
     - SEC-T699-04.
   - **Accepted risks:** apply ADR-011. Each accepted MEDIUM that a release ships needs the user's new acceptance at that release. TD-T697-07 is now tied to the bearer token: it ends 2027-01-29 and is renewed with each token.
   - **A "Next release" checklist:**
     - the T725 migration item (`/prepare-release` no longer installed into targets);
     - the ADR-011 re-acceptances of SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder and SEC-T702-09;
     - the new verdict fields "Issued at commit" and "Independent check".
   - **The open items as new LOW batches** (letters starting at G), each with a scope, owner and trigger. Name the ones a reviewer flagged as "do first": SEC-T716-01, SEC-T722-03, SEC-T725-02, SEC-T728-01, SEC-T727-01/-02. Keep SEC-T663-02 as its own item, and F (PoC scanner, 2 ids) as it is.
   - **Dates:**
     - GitLab token renewal 2027-01-28;
     - CWSO bearer renewal and the end of TD-T697-07 2027-01-29;
     - end of Brave acceptance v3 2027-01-30;
     - the `paste` review is closed;
     - Trivy 0.76.1 can be adopted from 2026-11-04.
   - **User actions:** A-2, A-7, A-10 to A-15, plus the new CWSO redeploy action (`CWSO_HTTP_PUBLISH_ADDR`, secret length, origins).
   - *Acceptance:*
     - every v4 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T729 writes only the artifact.
- Do not read the CWSO repository's secrets. CWSO statuses come from plan-129 and CWSO MR !218.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-02)

- **T729 is done.** The register is `docs/artifacts/tracked-debt-register-v5.md`. It holds 500 ids, 443 from v4 and 57 new:

  | Status | Ids |
  |---|---:|
  | fixed | 381 |
  | accepted | 45 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 67 |

- **No open item is above LOW.**
- **The 57 new ids** include T714's eight review ids (SEC-T714-01 to -08) and T717-D1 to -D3. v4 had treated batch C as in flight, so it did not count them.
- **The orchestrator's check.**
  - An independent count of the rows in sections 2 and 3 found no duplicates.
  - The counts are 67 tracked-LOW, 1 open and 45 accepted. Three of the accepted rows are multi-id rows.
  - SEC-T689-02 is listed again because the rest of it is now closed. v4 already counted it as fixed, so the totals add up.
- **Rulings the tech lead asked for.**
  - **Batch B count.** 16 ids are fully closed. SEC-T677-01 stays tracked-LOW for its residual shapes; plan-126's figure of 17 counted it as closed.
  - **TL-T708-07** stays tracked-LOW.
  - **TD-T720-01** now sits at `release-workflow/SKILL.md` lines 117 and 171, after the SEC-T720-01 insertion. The lines in plan-127 are the older ones.
- **Token use.** T729 used about 169k tokens against a budget of 120k.
