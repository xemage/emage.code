# plan-149 — Tracked-debt register v13

**Created:** 2026-11-12
**Based on:** `docs/artifacts/tracked-debt-register-v12.md` (672 ids); `docs/plans/plan-148-node-image-bump.md` (§ Progress, § Outcome); `docs/artifacts/security-review-t784-node-advisory-v1.md`; `docs/artifacts/security-review-t786-node-bump-v1.md`; `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md`. The user's answer of 2026-11-12, verbatim: "v13 go".
**Scopes:** `T787`.

## Goal

plan-148 (the Node image bump, MR !666 and MR !667) closed two ids and opened three. Its reviews also changed one open point and one date. Their review records are the only place these changes are tracked. T786's CONDITIONAL_PASS is met only when the register carries SEC-T784-01, SEC-T786-01, SEC-T786-02 and SEC-T768-03. v13 takes all of this over, so the v11.0.0 release plan starts from one current list.

## Facts since v12 that no artifact records (the orchestrator's record)

This section is the source for these facts.

- **The new image review date.**
  - `.gitlab-ci.yml` now carries `# ci_images_reviewed_on: 2026-11-11` (T785, MR !667).
  - With `MAX_REVIEW_AGE_DAYS = 120` (`tests/functional/test_ci_hash_pins.py:1255`), and the test's own boundary check at lines 1288-1290 (120 days pass, 121 fail), **2027-03-11 is the last passing day, and the test fails from 2027-03-12.** This is by reading and date arithmetic, not by a run on that date.
  - This replaces v12 § 6.3's 2027-03-06 and 2027-03-07.
- **plan-148's merges.**
  - MR !666 (develop `7918b9af`): the plan and T784.
  - MR !667 (squash `4b7d5c5d`, merge `fa33912c`): T785, T786 and the plan Outcome. Verified at `ff488f64`: pipeline 3056985425 green, and the full suite in a clean worktree, 2707 tests OK.
- **Ledger:** 0 active, 583 completed after !667.

## Task Decomposition

1. **T787** (tech-lead): write `docs/artifacts/tracked-debt-register-v13.md`, a delta on v12, as v12 was on v11. Keep v12's section numbering where a section still applies. Do not repeat a row for an id that did not change; v12 and earlier stay the record of its text.
   - **Ids that changed since v12**, one row each with its citation:
     - **SEC-T756-05 and SEC-T756-06:** fixed by T785, confirmed by T786. They leave batch X.
     - **SEC-T768-03:** stays tracked-LOW. T786 § 2 records that its trigger did not fire at `116b800c…`. Note that, and keep the id in batch X.
     - **SEC-T756-02** (tracked-LOW, batch X): v12 § 6.3 shows its deadline as "2027-02-19 and before any earlier image bump".
       - An image bump has now happened, and both CA-chain jobs passed on it (T786 obligation 5).
       - A-21 is still open.
       - Re-read T768's condition and v12's row, and say, with the citation, what the bump settles for this id and what it leaves. Do not re-grade it.
     - Search the lines added in `b45f400e..fa33912c` for every v12 id, and give a row to any other v12 id whose status a plan-148 source changed.
   - **New ids**, one row each, with the review record's grade and final status:
     - SEC-T784-01, from `security-review-t784-node-advisory-v1.md`, as T786 § 2 carries it: open, tracked-LOW. Its remediation includes the "Node.js 18+" floor at `implementation/PREREQUISITES.md:4` and `:227` (plan-148 § Progress).
     - SEC-T786-01 and SEC-T786-02, from `security-review-t786-node-bump-v1.md` § 3.
     - Search the lines added in `b45f400e..fa33912c` for any other id an artifact mints, and say what you find. The blocker id BLK-T784-01 is answered (T786 § Blockers). It is a blocker, not a debt id, so say how you treat it.
   - **Ids that did not change:** account for every other v12 `open`, `tracked-LOW` and `accepted` id compactly, as "Unchanged". Do not re-rule them.
   - **The user's decisions since v12, quoted verbatim:**
     - "Re-grade now, bump later (Recommended)" (plan-148). The question it answered and the request before it, "Continue with the next best step", are quoted in plan-148's Based on line.
     - "v13 go".
     - Each row claims only what these sources record.
   - **The orchestrator's rulings since v12, marked as not the user's:**
     - plan-148 § Progress: obligation 7 applies to live files only; the upper bound on the wait (2026-12-11); T785 blocked until the image existed.
     - plan-148 § Outcome: the line-range fix in the pin checklist, and the python re-read that backs `.gitlab-ci.yml:19`.
   - **The open items as batches:**
     - Batch X loses SEC-T756-05 and -06, gains SEC-T786-01, and gets a new trigger (Alpine's `nodejs` 24.22.3 in a `unit-tests` log; check at v11.0.0 preparation).
     - Put SEC-T784-01 and SEC-T786-02 where T786 suggests (batch Q or Y). Choose one each, and say why.
     - Carry every other batch unchanged.
     - Update the size table and the total.
     - Mark any order you give as your suggestion.
   - **Next release checklist (v11.0.0, MAJOR):** carry v12 § 6.2, and change only what plan-148 changed.
     - The item that the CA-chain jobs must pass after the Node image bump is now observed (pipelines 3056919066 and 3056985425). Say what it still leaves for the tag.
     - Add: SEC-T786-01's check at v11.0.0 preparation. If Alpine still has no fixed `nodejs` then, record it in the release document and re-grade.
     - Add: SEC-T784-01's Node minimums in the release document and in `PREREQUISITES.md`.
     - Re-read every line citation in § 6.2 that points into `.gitlab-ci.yml`. Its image record grew by one line (the default image moved from line 42 to 43), and `verify-knowledge-drift` gained one line.
   - **Dates:** carry v12 § 6.3, and update:
     - the 2026-11-11 Node advisory row (done; MR !667);
     - the image review date: last pass 2027-03-11, fails from 2027-03-12 (§ Facts above);
     - SEC-T756-02's row, as you rule above.
   - **User actions:** carry v12 § 7 unchanged unless a plan-148 source changes one. A-21 is still open.
   - **What stays unverified:** carry v12 § 8.
     - Drop the "non-amd64 images" point for the runner. Every job of pipeline 3056919066 logs an x86-64 CPU (T786 obligation 1).
     - Add T786 § 6's list.
     - Keep separate what a real job proved, what GitLab's APIs proved, and what is hand trace.
   - *Acceptance:*
     - Every v12 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row.
     - Each status claim can be traced, or is marked **(unverified)**.
     - The counts add up, and the register states whether any open item is above LOW.
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T787 writes only the artifact.
- No `docker` command. Do not read the CWSO repository; its statuses carry over from v12.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Run no mutation and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-12)

- **T787 is done.** The register is `docs/artifacts/tracked-debt-register-v13.md`. It holds 675 ids: v12's 672 and 3 new (SEC-T784-01, SEC-T786-01, SEC-T786-02).

  | Status | Ids |
  |---|---:|
  | fixed | 500 |
  | accepted | 49 |
  | obsolete | 9 |
  | open | 4 (K-20; QA-T760-01 to -03) |
  | tracked-LOW | 113 |

- **Batches:** I 23, J 1, K 7, L 5, M 12, N 8, P 1, Q 9, R 4, S 1, V 15, X 10, Y 9, Z 3, F 2, U 7, for a total of 117. No open item carries a `SECURITY:*` grade above LOW.
- **T786's condition is met.** SEC-T784-01, SEC-T786-01, SEC-T786-02 and SEC-T768-03 are tracked-LOW in v13.
- **The orchestrator's check:**
  - A separate parser of the section 5 tables of v12 and v13 shows that v13's 117 unique batch ids equal v12's set, less SEC-T756-05, SEC-T756-06 and SEC-T768-06, plus the three new ids. Nothing is missing and nothing is extra.
  - X, Q and Y differ from v12 by exactly those ids, and every batch size equals its list.
  - Section 2.2 names every v12 tracked-LOW id.
  - The parser reads 24 entries in batch I because SEC-T762-05 is also cited inside SEC-T725-02's note. Batch I holds 23 unique ids, as the register says.
- **The orchestrator's rulings (not the user's):**
  - **SEC-T768-06 is fixed, as T787 proposes.** The finding's remediation is "Update digest, date and version line" (`security-review-t768-ca-control-v1.md:40`). T785 rewrote `docs/wiki/mcp-pin-bump-checklist.md:30` to name `python:3.12-alpine` `e064671c…` (2026-11-06, Python 3.12.16). The old `92abd2ba` now appears only in immutable artifacts (orchestrator's grep). It is LOW, and the change it asks for is on develop, so no further review is needed.
  - **v13 § 8, settled here:** every job of pipelines 3056919066 and 3056985425, 14 in all, logs `Running on CPU: AMD Ryzen 7 2700X Eight-Core Processor` (read by the orchestrator from the job logs).
  - **v13 § 8, the python re-read's day:**
    - The orchestrator's read was at 2026-11-12T00:15Z, in UTC (`date -u`).
    - T785 reported a read at 2026-11-11T23:45:36Z, but that rests on the agent's report only.
    - Both reads give the pinned `e064671c…`. That backs the digest at `.gitlab-ci.yml:19`. The 2026-11-11 day rests on T785's report.
