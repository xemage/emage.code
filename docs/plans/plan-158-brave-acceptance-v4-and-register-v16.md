# plan-158 — Brave acceptance record v4 and tracked-debt register v16

**Created:** 2026-11-13
**Based on:** `docs/artifacts/brave-audit-acceptance-v3.md`; `docs/plans/plan-155-v11-release-decisions.md` (§ User decisions item 2, § Addendum item 5); `docs/artifacts/brave-replacement-scouting-v1.md`; `docs/artifacts/tracked-debt-register-v15.md` (681 ids); `docs/plans/plan-156-apply-adr-015.md`; `docs/plans/plan-157-confirmation-as-validity-condition.md`; `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`; `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`; `docs/artifacts/security-review-t802-adr-015-apply-v1.md`; `docs/artifacts/security-review-t806-adr-016-apply-v1.md`.
**Scopes:** `T808`, `T809`.

## User decision (2026-11-13, verbatim)

The orchestrator listed the next steps as: "1. **Brave acceptance record:** a new version carrying your "Keep the acceptance" decision for v11.0.0. 2. **Register v16:** records SEC-T762-04, TL-T761-10 and SEC-T802-01 to -04 as fixed, and SEC-T806-01 to -03 as new LOW items. 3. **v11.0.0 release plan:** it starts with the Security Engineer's dated statement for SEC-T660-01 and SEC-T665-01, after which I ask you about those two again." The user's answer, verbatim:

> 1. Keep the acceptance
> 2. v16 go

The orchestrator reads this as the word for steps 1 and 2 only. Step 3 was not answered and is not started. Nothing here is a release, a tag or a root refresh.

## Goal

1. The user's acceptance of SEC-T702-09 for v11.0.0 (2026-11-12, "Keep the acceptance (Recommended)") lives only in plan-155. The gate script and the pin-bump checklist read the acceptance record `brave-audit-acceptance-v<N>.md`, whose v3 records the decision for v9.0.0. v4 records the decision for v11.0.0 with the user's words.
2. Since register v15, plan-155, plan-156 and plan-157 changed statuses and minted ids. v16 takes them over, so the v11.0.0 release plan starts from one current list.

## Facts since v15 that no artifact records (the orchestrator's record)

This section is the source for these facts.

- **Merges** (each pinned to the verified commit, full suite in a clean worktree and both pipelines green):
  - MR !674 (develop `30f409df`): register v15 (plan-154).
  - MR !675 (squash `7e7a4761`, develop `2731ab3a`): plan-155, T799 and T800. Verified at `6488503b`: suite 2731 OK (skipped=25); pipelines 3061077836 and 3061077686.
  - MR !676 (squash `f20de1ec`, develop `babddbd0`): plan-156, T801 and T802. Verified at `5fd5dbbb`: suite 2732 OK (skipped=25); pipelines 3061443774 and 3061443096.
  - MR !677 (squash `ce49d32f`, develop `db2299b3`): T803 root refresh. Verified at `d3352ead`: suite 2732 OK (skipped=25); pipelines 3061580882 and 3061580823.
  - MR !678 (squash `018777cb`, develop `b8dba5dc`): plan-157, T804 to T806. Verified at `fc5161dc`: suite 2736 OK (skipped=25); pipelines 3061827833 and 3061827783.
  - MR !679 (squash `8e68b3fe`, develop `c4b3f6cf`): T807 root refresh. Verified at `d473bd6c`: suite 2736 OK (skipped=25); pipelines 3062884004 and 3062883982. `--print-drift` gives `[]`.
- **The user's words since v15, verbatim**, each in the plan that records its question: plan-155 § User decisions and § Addendum ("Accept for v11.0.0"; "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0"; "Yes, with conditions (Recommended)"; "Yes, a new acceptance cures it (Recommended)"; "Keep the acceptance (Recommended)"; the acceptance of ADR-015); plan-156 ("Continue"; "Root refresh approved"); plan-157 ("confirmation should become a fourth validity condition"; "Accept with all recommendations (Recommended)"; "W1 (SEC-T802-01),W2 (SEC-T802-02),W3 (SEC-T802-04)"; "Approving root refresh"); this plan § User decision.
- **Ledger:** 0 active, 604 completed after !679.
- **SEC-T660-01 and SEC-T665-01 under ADR-016 (O-B, O-C, O-D).** The user answered "Accept for v11.0.0" on 2026-11-12, before ADR-016 was accepted. The only Security Engineer review the orchestrator found that says no harness fix exists is `docs/artifacts/security-review-t756-accepted-mediums-v1.md`, written for v10.0.0 (a grep over `docs/artifacts/security-review-*.md`, not a full reading). No dated statement for v11.0.0 exists. The orchestrator told the user on 2026-11-12 and 2026-11-13 that the v11.0.0 release plan will commission that statement first and then ask again, and that the earlier answer is not treated as carried over. The user has not yet answered on the release plan.
- **Not checked since v15:** SEC-T786-01's trigger (Alpine `nodejs` 24.22.3 in a `unit-tests` log) **(unverified)**; whether a Brave release above 2.1.4 exists today (T808 checks it).

## Task Decomposition

1. **T808** (devops-engineer): write `docs/artifacts/brave-audit-acceptance-v4.md` and move the references that must name the current record. Brief: `docs/tasks/task-T808.md`.
2. **T809** (tech-lead), after T808: write `docs/artifacts/tracked-debt-register-v16.md`, a delta on v15, as v15 was on v14. Keep v15's section numbering where a section still applies. Do not repeat a row for an id that did not change.
   - **Ids that changed since v15**, one row each with its citation:
     - **SEC-T762-04, TL-T761-10:** ruled by the user (plan-155), recorded in ADR-015, applied by T801, confirmed by T802 (plan-156 § Outcome).
     - **SEC-T660-01, SEC-T665-01:** the user's words of 2026-11-12 and what ADR-016 O-D makes of them (§ Facts above). Record what the sources say; do not rule whether the acceptance holds. State what must happen before the v11.0.0 gate.
     - **SEC-T702-09:** accepted for v11.0.0 only; the record is `brave-audit-acceptance-v4.md` (T808).
     - Search the lines added in `30f409df..c4b3f6cf` for every v15 id, and give a row to any other v15 id whose status a source in that range changed.
   - **New ids**, one row each, with the source's grade and final status:
     - **SEC-T802-01 to -04** (LOW; minted by T802; fixed by plan-157: -01 by W1, -02 by W2, -03 by ADR-016 rows D1 and D2, -04 by W3; confirmed by T806).
     - **SEC-T806-01 to -03** (LOW; tracked; assign each to a batch or a new one, and say whether -01 or -02 needs the user's word, as T806 suggests).
     - Any id T808 mints.
     - Search the lines added in `30f409df..c4b3f6cf` for any other id an artifact mints (for example in the scouting record, ADR-015 or ADR-016), and say what you find.
   - **Ids that did not change:** account for every other v15 `open`, `tracked-LOW` and `accepted` id compactly, as "Unchanged". Do not re-rule them.
   - **The user's decisions since v15**, quoted verbatim from the plans named in § Facts. Each row claims only what its source records.
   - **The orchestrator's rulings since v15, marked as not the user's:** the reading of "Continue" as the word for plan-156; folding W1 to W3 into T805 after the user included them; no Security Engineer review of the v4 record or of this register (the release security review reads both); the reading of the user's answer in this plan.
   - **The open items as batches:** update the size table and the total; mark any order you give as your suggestion.
   - **Next release checklist (v11.0.0, MAJOR):** carry v15 § 6.2 and change only what the range changed: items 2 and 33 (answered; say what is left), the ADR-015 and ADR-016 record duties for the release document (outside closer, the plain statement, the confirming review before the user is asked, the dated statement for a later release, the review date 2027-01-28, the passed deadline of SEC-T660-01), the note of the T806 review (items 1 to 7), and the Brave record v4. Re-read every line citation in § 6.2 that points into a file changed in the range (`implementation/knowledge/skills/validation-gates/SKILL.md` and `implementation/knowledge/agents/release-manager.md` changed).
   - **Dates:** carry v15 § 6.3 and add or change what the range changed (the review date 2027-01-28; the Brave expiry from v4).
   - **User actions:** carry v15 § 7 unchanged unless a source changes one (A-21 and A-22 stay open as far as the orchestrator knows).
   - **What stays unverified:** carry v15 § 8, add the limits T802 and T806 list, and keep separate what a real job or run proved, what GitLab's APIs proved, and what is reading only.
   - *Acceptance:*
     - every v15 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up, and the register states whether any open item is above LOW;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## T808 result (2026-11-13; the orchestrator's record, input for T809)

- **T808 is done** (commits `f9e1e5b2`, `68e5f332`): `docs/artifacts/brave-audit-acceptance-v4.md` records the acceptance of SEC-T702-09 for v11.0.0 only, with the user's words from plan-155 and this plan. No pin, launch argument, gate logic, advisory or expiry changed; the expiry stays 2027-01-30 or the first Brave release above 2.1.4. The current-record references moved to v4: `scripts/audit-mcp-pins.py` (usage text), `docs/wiki/mcp-pin-bump-checklist.md` (two places), `tests/functional/test_pin_bump_checklist.py` (v3 stays checked as the prior record; two new tests). Nothing under `implementation/knowledge/` changed, so there is no root drift.
- **Checked on 2026-11-13** by T808 and again by the orchestrator: npm's newest `@brave/brave-search-mcp-server` is 2.1.4. By T808 (logs in its report): the audit without `--accept` exits 1 with exactly v3's seven advisories at or above `high` on the pin, and with the seven `--accept` entries exits 0. The orchestrator compared the advisory ids of v4 and v3 (equal) and the user's quotations in v4 with plan-155 (present character for character), and re-ran the gates and the three pin test files (exit 0).
- **v10.0.0's acceptance** of SEC-T702-09 is in `docs/releases/v10.0.0.md` (§ RELEASE VERDICT, Conditions), not in any version of the Brave record.
- **Ids the orchestrator mints from T808's suggestions, both LOW, tracked:**
  - **TD-T808-01:** `scripts/audit-mcp-pins.py` names the acceptance record by version in its usage text, so each new record version needs a script edit; the new test catches a stale name.
  - **TD-T808-02:** v4 does not extend the acceptance in time. If v11.0.0 is tagged after 2027-01-30, or after a Brave release above 2.1.4, the gate fails and the user must decide again (a date for register § 6.3).
- **For the v11.0.0 release document** (T808's note): ADR-011 asks for the per-release acceptance in the release document's own form as well as the pin-audit record.
- **Budget:** T808 used about 104k tokens against 60k (a repository-wide reference search and the loaded context).

## Constraints

- T808 changes only what its brief names. The tech lead is read-only on source; T809 writes only the artifact.
- No `docker` command. Do not read the CWSO repository; its statuses carry over from v15.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Run no mutation and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies both outputs and merges on a green pipeline.

## Outcome

**Done on 2026-11-13.** Both steps the user named ("1. Keep the acceptance / 2. v16 go") are done. The v11.0.0 release plan was not part of that word and is not started.

- **T808** (devops-engineer), commits `f9e1e5b2` and `68e5f332`: `docs/artifacts/brave-audit-acceptance-v4.md`; see § T808 result.
- **T809** (tech-lead), commit `9fe2ffeb`: `docs/artifacts/tracked-debt-register-v16.md`. **690 ids** (v15: 681): 514 fixed, 49 accepted, 9 obsolete, 1 open (K-20), 117 tracked-LOW. Nothing open or tracked is above LOW on any scale.
  - **Fixed since v15:** SEC-T762-04 and TL-T761-10 (plans 155 and 156); SEC-T802-01 to -04 (minted by T802, fixed by plan-157).
  - **New, LOW, tracked:** SEC-T806-01, -02, -03 (batch R) and TD-T808-01 (batch N), TD-T808-02 (batch Q).
  - **Batches:** I 23, J 1, K 7, L 5, M 12, N 9, P 1, Q 9, R 7, S 1, V 15, X 10, Y 9, F 2, U 7 = 118 (117 tracked-LOW + 1 open).
  - **Accepted, with a changed qualifier:** SEC-T702-09 is accepted for v11.0.0 only (record v4). For SEC-T660-01 and SEC-T665-01 the register records the user's "Accept for v11.0.0" of 2026-11-12 and ADR-016, and does not rule whether that acceptance holds; its § 2.3 and § 6.2 item 2 say what must happen before the v11.0.0 gate (the Security Engineer's dated statement first, then the question to the user again).
  - **§ 6.2:** items 2 and 33 changed; items 40 (ADR-015 and ADR-016 record duties), 41 (the T806 note, items 1 to 7) and 42 (Brave record v4 and its expiry) are new. **§ 6.3:** the 2027-01-28 and 2027-01-30 rows gained the review date and TD-T808-02.
  - **The Tech Lead's view (register § 3.1):** SEC-T806-01 and -02 need no word from the user to be tracked or for v11.0.0; changing their text would need a superseding ADR that the user accepts.

**The orchestrator's own verification:** the batch tables of v16 and v15 compared with an own parser and by reading the three changed rows (Q 10 - 2 + 1 = 9, R 4 + 3 = 7, N 8 + 1 = 9; no other row changed); the status table adds up (514 + 49 + 9 + 1 + 117 = 690); each of the nine new ids and the two fixed ids has a row; the user's quotations in the register are those of plans 155 to 158; the gates (validate-tasks, link integrity, team health, scorecard, sync `--check`, registry `--check`) exit 0 and the root drift list is `[]`. The full suite in a clean worktree and the pipeline at the merged commit are recorded in the merge request.

**Disclosures.**
- **No Security Engineer review** of the Brave record v4 or of the register: the orchestrator's ruling. Neither changes a control, a pin, a gate or shipped text; v4 records a decision the user made, and the register is a list of statuses. The acceptance of SEC-T702-09 for v11.0.0 is still to be written in the release document's own form (ADR-011), where the release gate reviews it.
- **Budgets:** T808 about 104k tokens against 60k; T809 about 123k against 80k (loaded context, v15 read whole, one over-wide search).
- **The register's own limits** are in its § 8; among them, the membership of unchanged batches is carried from v15 and not recounted, and SEC-T786-01's trigger and A-22's state are **(unverified)**.
- **Differences on the record** (register § 4.3), ruled by nobody here: plan-156's Outcome calls SEC-T802-01 to -04 "tracked" and plan-157 calls them fixed (the register follows the later one); plan-155's Outcome reads "accepted MEDIUM for v11.0.0 only" for SEC-T660-01 and SEC-T665-01 and predates ADR-016.

**No root drift:** nothing under `implementation/knowledge/` changed.

**Next, each needing the user's word:** the v11.0.0 release plan (it begins with the Security Engineer's dated statement for SEC-T660-01 and SEC-T665-01, then the question to the user again); user actions A-20, A-21, A-22.
