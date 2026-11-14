# plan-162 — Tracked-debt register v17

**Created:** 2026-11-14
**Based on:**
- `docs/artifacts/tracked-debt-register-v16.md` (690 ids)
- `docs/plans/plan-159-release-gate-runner-tag.md`, `docs/plans/plan-160-v11-confirmation-sec-t660-t665.md`, `docs/plans/plan-161-release-v11.md` (each § Outcome and Addenda)
- `docs/checkpoints/checkpoint-043-release-v11.0.0.md`
- `docs/releases/v11.0.0.md`
- the review and gate artifacts of T811, T812, T813, T814, T818, T819, T820 (with its addendum), T821 (independent check) and T825

**Scopes:** `T827`.

## User decision (2026-11-14, verbatim)

After the v11.0.0 closeout merged, the orchestrator offered tracked-debt register v17 ("Say "v17 go" when you want it"). The user answered:

> v17 go

## Goal

Since register v16, plans 159 to 161 closed, fixed or minted ids, and v11.0.0 shipped. v17 takes these over, and resets the next-release checklist for the release after v11.0.0, so later work starts from one current list.

## Facts since v16 that no artifact records (the orchestrator's record)

- **Merges**, each pinned to the verified commit, after the full suite in a clean worktree and green pipelines:

  | MR | Content | Resulting commit |
  |---|---|---|
  | !680 | plan-158 | develop `bbe3b8af` |
  | !681 | plan-159 | develop `5de6fbb7` |
  | !682 | plan-160 | develop `9acf84dc` |
  | !683 | plan-161 wave 1 | develop `81520c31` |
  | !684 | release into develop, unsquashed | `6c52ae12` |
  | !685 | release into main, unsquashed | `2bb487ef` |
  | !686 | closeout | develop `42e30d02` |

  The tag `v11.0.0` (`e5645616`) is on `3118924a`. Tag pipeline 3067005699 ran all three jobs on runner #59129270. The Release body equals the document.
- **The commit range for this register:** `bbe3b8af..42e30d02`.
- **Ledger:** 0 active, 623 completed after !686.
- **The orchestrator's ids from plan-161:**
  - SEC-T814-01 was minted from T814's finding. T825 graded it LOW, and T824 fixed it.
  - SEC-T825-02 was fixed by the orchestrator, and T820 reviewed the fix: PASS.
- **Grades given in the T820 addendum:**
  - TD-T774-01 / QA-T818-01: `SECURITY:LOW`, with a regrade trigger.
  - QA-T818-03: LOW.
  - SEC-T820-02: LOW; T821 applied the fix to the document.
- **User reports, not verified by the orchestrator:**
  - plan-159 (runner): "Already done", "Yes, both".
  - The probe tag was deleted in the web UI. `ls-remote` showed no `gate` ref before or after the tag push.

## Task Decomposition

1. **T827** (tech-lead): write `docs/artifacts/tracked-debt-register-v17.md`, a delta on v16, as v16 was on v15. Keep v16's section numbering. Brief: `docs/tasks/task-T827.md`. The register must cover:
   - **Closed, fixed or minted in the range:**
     - SEC-T741-17: fixed, both halves (T810, T811, and tag pipeline 3067005699).
     - A-20: closed.
     - SEC-T811-01 to -05: -01 and -02 resolved by the user, as reported; -04 fixed; -03 and -05 LOW, tracked.
     - SEC-T814-01: minted and fixed.
     - SEC-T784-01: fixed.
     - SEC-T825-01: part (a) LOW, tracked; part (b) done in the document.
     - SEC-T825-02: fixed.
     - SEC-T820-01: fixed.
     - SEC-T820-02: the document part is done in T821; state whether anything is left.
     - TD-T774-01: graded LOW, with the trigger.
     - QA-T818-01 to -04: -02 fixed in the document; -01 is TD-T774-01; -03 LOW; -04 settled at the tag.
     - TL-T819-01 to -05: -01 and -02 fixed; -03 to -05 LOW.
     - TL-T821-01: LOW.
     - K-15 / SEC-T657-01 / SEC-T658-01: closed by removal at v11.0.0, with the reopen condition.
     - SEC-T786-01: its trigger (a `unit-tests` log showing Alpine `nodejs` 24.22.3) is **(unverified)** unless the register's author reads a job log.
   - **The accepted MEDIUMs:**
     - SEC-T660-01, SEC-T665-01 and SEC-T702-09 were accepted for v11.0.0 only and shipped.
     - Each needs a fix or a new acceptance before the next release.
     - For SEC-T660-01 and SEC-T665-01, the review on 2027-01-28 is due (ADR-015 O3, W1).
   - **§ 6.2, a new next-release checklist** for the release after v11.0.0:
     - carry the items that stay open;
     - drop those done at v11.0.0;
     - add the new ones: the runner's `allowed_images` at an image bump; the TD-T774-01 regrade trigger; the dates.
   - **§ 6.3 dates:** 2027-01-28, 2027-01-29 (TD-T697-07), 2027-01-30, 2027-03-12.
   - **§ 7 user actions:** A-20 closed; A-21, A-22, K-20 and A-7 as they stand.
   - **Counts:**
     - a status table that adds up from v16's 690 ids;
     - the batch table and its total;
     - whether any open id is above LOW.

## Constraints

- The register is the only file that changes. No source, ledger, plan or brief edits by the author.
- No `docker` command. Never open `tests/golden/held-out/`. Never read secrets or the user's settings files.

## Outcome

**Done on 2026-11-14.** `docs/artifacts/tracked-debt-register-v17.md` is written by T827 (tech-lead) in commits `ef1680a0` and `45ee9b3d`. It holds **708 ids**:

| Status | Ids |
|---|---:|
| fixed | 531 |
| accepted | 47 |
| obsolete | 10 |
| open (K-20) | 1 |
| tracked-LOW | 119 |
| **Total** | **708** |

Nothing open or tracked is above LOW on any scale.

**Batches** (total 120; S ended):

| I | J | K | L | M | N | P | Q | R | V | X | Y | F | U |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 1 | 8 | 5 | 12 | 10 | 1 | 5 | 7 | 17 | 10 | 10 | 2 | 7 |

**Status changes:**
- **Fixed** (all from v16's tracked-LOW unless noted):
  - SEC-T741-17
  - SEC-T784-01
  - SEC-T786-01: on the orchestrator's observation of the `unit-tests` logs in pipelines 3066902202 (before the tag) and 3067048242
  - SEC-T773-02, SEC-T780-05, SEC-T791-01: the Tech Lead's ruling
  - SEC-T657-01/SEC-T658-01 and K-15: from accepted, closed by removal
- **Obsolete:** TD-T808-02.
- **New:** 18 ids. 9 are fixed and 9 are tracked-LOW.
- **Accepted for v11.0.0 only, shipped:** SEC-T660-01, SEC-T665-01, SEC-T702-09. Each needs a fix or a new acceptance before the next release.

**§ 6.2** is reset for the release after v11.0.0: 26 items stay as rules, 14 were done at v11.0.0, 2 stay open (8, 34), and items 43 to 48 are new.

**The orchestrator's own verification:**
- The rebuilt parser (scratchpad `regparse.py`) compared the § 5 batch tables of v16 and v17. Removed: SEC-T741-17, SEC-T773-02, SEC-T780-05, SEC-T784-01, SEC-T791-01, TD-T808-02. Added: the nine new tracked-LOW ids. SEC-T786-01 leaves batch X. The sizes add up to 120.
- The status counts add up to 708.
- The gates exit 0, and the root drift list is `[]`.
- The full suite and the pipeline are recorded in the merge request.

**Disclosures (the orchestrator's):**
- The v11.0.0 verdict listed two conditions "before the tag" that the orchestrator did not confirm before pushing the tag:
  - SEC-T786-01's log check. The logs read afterwards show it was met before the tag: pipeline 3066902202 at 22:46Z, the tag at about 23:29Z.
  - A-21, which stayed open at the tag. SEC-T756-02 stays LOW only while A-21 finds none of the listed CI variables. The user was asked to check them.
- Checkpoint-043 speaks of four publishing steps but quotes three approvals. The fourth step, watching the tag pipeline, needed no approval.
- T827 used about 159k tokens (the harness's count) against 80k.
- No Security Engineer review of the register: the orchestrator's ruling. It is a list of statuses.

**Next, each needing the user's word:** A-21, A-22, and any LOW batch.
