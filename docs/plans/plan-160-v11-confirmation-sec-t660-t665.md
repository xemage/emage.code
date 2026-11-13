# plan-160 — v11.0.0 preparation, step 1: the Security Engineer's confirmation for SEC-T660-01 and SEC-T665-01

**Created:** 2026-11-13
**Based on:** `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md` (§ Decision, O-B, O-C, O-D); `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`; `implementation/knowledge/skills/validation-gates/SKILL.md` § Verdict Rules (rows D1, D2); `docs/plans/plan-155-v11-release-decisions.md` (§ User decisions 1); `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (Part 1, Q3); `docs/artifacts/tracked-debt-register-v16.md` (§ 2.3, § 6.2 items 2, 40, 41); `docs/artifacts/security-review-t806-adr-016-apply-v1.md` (note for the v11.0.0 release plan).
**Scopes:** `T812`.

## User decision (2026-11-13, verbatim)

After plan-159 merged, the orchestrator reported that the v11.0.0 release plan still needs the user's word, and that it begins with the Security Engineer's dated statement for SEC-T660-01 and SEC-T665-01, after which the user is asked again. The user answered:

> Continue with the next best step

The orchestrator reads this as the word for this first step only: the Security Engineer's confirmation, then the question to the user again. It is not the word for the release plan as a whole, and nothing here is a release, a tag, a release branch or a root refresh.

## Goal

The user accepted SEC-T660-01 and SEC-T665-01 for v11.0.0 on 2026-11-12 ("Accept for v11.0.0"), with a plan whose fix is "none possible in the harness". ADR-016, accepted afterwards, makes the Security Engineer's confirmation that no harness fix exists a fourth validity condition of such a plan. Under O-B that confirmation must come before the user is asked; under O-C an earlier review serves a later release only with the Security Engineer's dated statement that it still holds; under O-D the rule applies to the v11.0.0 verdict. The only review the orchestrator found that says no harness fix exists is T756's, written for v10.0.0 (plan-158 § Facts since v15). So:

1. A Security Engineer reviews both findings for v11.0.0 and either confirms, with a dated statement, that no harness fix exists (a new review or a statement that T756's still holds), or finds that a harness fix now exists.
2. The orchestrator then puts the acceptance question to the user again, citing that review (ADR-016 O-A).

## Task Decomposition

1. **T812** (security-engineer): `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md`. Brief: `docs/tasks/task-T812.md`.
2. **The orchestrator**, after T812: commits the review, asks the user (question dialog, citing T812 with its date), records the answer verbatim in § Outcome, and merges. If T812 finds a harness fix exists, the plan's fix changes and the user is asked about that instead.

## Constraints

- The reviewer is read-only: no token use, no GitLab call, no change to any setting, host or file.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's settings files.
- The user's earlier answer is not treated as carried over (ADR-016 O-B).

## T812 result (2026-11-13; the orchestrator's record)

- `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md`: **CONFIRMED no harness fix** for SEC-T660-01 and SEC-T665-01, both still `SECURITY:MEDIUM`, dated 2026-11-13 for v11.0.0 (a new review under O-C; it also states that T756's finding still holds). No new finding.
- **The orchestrator's check of the point T812 marked unverified** ("no commit in plans 146 to 159 changed the token handling"): `git diff v10.0.0 origin/develop` on `implementation/knowledge/mcp/servers.yaml` and `implementation/PREREQUISITES.md`, and `git log v10.0.0..origin/develop` on those files and `scripts/check-gitlab-token.py`. The only changes are the Pi and Gemini removals (`bed31f34`, `4d820f54`), plan-151 (`d69ecad0`, context-retriever) and wording. The `gitlab` entry's pin, token variables and `GITLAB_PERMISSION_MODE=modify` are unchanged, and `check-gitlab-token.py` is unchanged.
- **For the release document (T812 § SEC-T660-01):** the deadline that passed is the v8.0.0 plan's ("the sprint after v8.0.0", at the latest 2026-11-01). The Conditions line must name it and the release that acceptance was given for, separate from the 2027-01-28 review date. The deadline fits only if v11.0.0 ships before 2027-01-28.
- **Budget:** T812 used about 115k tokens against 60k.

## Outcome

**Done on 2026-11-13.** The question was put to the user after T812's review, citing that review (ADR-016 O-A, O-B).

- **Question** (question dialog, verbatim): "For release v11.0.0: SEC-T660-01 and SEC-T665-01 (both SECURITY:MEDIUM) — an agent shell running as you can read the GitLab token and so merge, tag, release or push. The Security Engineer's review docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md (2026-11-13, for v11.0.0) confirms no fix inside the harness exists; only an isolated OS user, container or VM that you set up closes them. Plan: owner you (isolation) and devops-engineer (documentation); fix: none possible in the harness; deadline: review at token renewal on 2027-01-28 (v11.0.0 must ship before then); for SEC-T660-01 the release document states that its old deadline ('the sprint after v8.0.0', at the latest 2026-11-01) has passed. Accept both for v11.0.0 only?"
- **Options shown:**
  - "Accept for v11.0.0 (Recommended)": both accepted for v11.0.0 only on the plan above, citing T812; a new acceptance is needed at the next release, or earlier if the 2027-01-28 review passes before v11.0.0 ships.
  - "Isolate first".
  - "Do not accept".
- **Answer** (verbatim): **"Accept for v11.0.0 (Recommended)"**.

**Status for register v17 and the v11.0.0 release document:**
- SEC-T660-01 and SEC-T665-01 are accepted `SECURITY:MEDIUM` for v11.0.0 only. The plan meets all four conditions of ADR-016:
  1. an outside closer: the user, by isolation;
  2. a plain statement that no harness fix exists;
  3. a review date: 2027-01-28;
  4. the Security Engineer's confirmation: T812, before the question.
- The acceptance of 2026-11-12 is superseded by this one.
- The release document's Conditions line must carry, per id:
  - the outside closer;
  - the statement that no harness fix exists, with T812 and its date;
  - the date of the question (2026-11-13);
  - the review date 2027-01-28;
  - for SEC-T660-01, that the v8.0.0 plan's deadline passed (at the latest 2026-11-01).
- If v11.0.0 does not ship before 2027-01-28, the user must accept again.

**Optional for the user** (T812, point 2): read-deny rules for the token file and the `glab` and git credentials in their own `.claude/settings.json`. This is hardening on one client, not verified live, and not a fix. The orchestrator does not edit the user's settings files.

**Budget:** T812 about 115k tokens against 60k.

**Next:** the v11.0.0 release plan as a whole, which needs the user's word.
