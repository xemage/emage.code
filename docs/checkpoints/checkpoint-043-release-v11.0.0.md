# checkpoint-043 — Release v11.0.0 published

**Phase:** release (`plan-161`): v11.0.0 audited, prepared, gated and published
**Written:** 2026-11-14
**Author:** orchestrator
**Based on:** `checkpoint-042`; `docs/plans/plan-161-release-v11.md`; `docs/releases/v11.0.0.md`; `docs/artifacts/release-v11-audit-v1.md`; `docs/artifacts/tracked-debt-register-v16.md` § 6.2; plans 158 to 160; MRs !680 to !685
**Ledger at this checkpoint:** **0 active, 623 completed** after this closeout (checkpoint-042: 0 active, 579 completed)

## Phase summary

Release **v11.0.0** is MAJOR. It removes the Pi platform (ADR-013) and the Gemini CLI platform (ADR-014) with no deprecation period, and SEC-T791-01 changes how a platform's identity is resolved.

Publishing ran in four steps, each approved by the user at the moment it ran (quoted verbatim):

1. MR !684 merged `release/v11.0.0` into `develop`, unsquashed: merge commit `6c52ae12`, pipeline 3066902202. Approval: "Yes, merge to develop".
2. MR !685 merged it into `main`, unsquashed: merge commit `2bb487ef`, pipeline 3066941826. The tree of `main` equals the release tip `3118924a`. Approval: "Yes, then merge to main".
3. The annotated tag `v11.0.0` (tag object `e5645616`) went on the release tip `3118924a`, pushed as `refs/tags/v11.0.0` only. Approval: "Probe deleted, push the tag".
   - The tag-day checks (T820 C-2) passed: the UTC date was 2026-11-13, before 2027-01-28; npm's newest Brave release was still 2.1.4; and `audit-mcp-pins.py audit --audit-level high` with the seven `--accept` entries of `brave-audit-acceptance-v4.md` exited 0.
   - `git ls-remote --tags origin` showed no `gate` ref before or after the push (C-4). The user deleted the probe tag `v11.0.0-gate.1` in the web UI, and the orchestrator deleted its local copy.
4. Tag pipeline 3067005699 passed `release-docs-gate`, `main-develop-drift-gate` and `release`. **All three ran on runner #59129270** (`emage-release-gate`, system ID `s_7371c6d24bcc`), which meets T820 C-3 and closes the runtime half of SEC-T741-17. That the system ID is `gitlab-runner-16028` rests on the user's report.
   - The `release` job created the GitLab Release v11.0.0 (2026-11-13T23:29:46Z). Its description equals `docs/releases/v11.0.0.md` at the tag (byte comparison).
   - The `CHANGELOG.md` artifact says "_Commits since v10.0.0._".
   - `check-main-develop-drift.py`: main=v11.0.0, develop=v11.0.0, `releases_behind=0`, PASS.

**The release verdict is CONDITIONAL_PASS**, issued at `4ca11fa3` with 0 open blockers:
- QA (T818), the Tech Lead's review by area (T819) and the release-level security re-check (T820, with its addendum) were each CONDITIONAL_PASS, with 0 critical and 0 high open.
- The independent check by tech-lead was PASS at `4ca11fa3` (`docs/artifacts/independent-check-t821-v1.md`).
- Three MEDIUM findings ship, each accepted by the user for v11.0.0 only:
  - SEC-T660-01 and SEC-T665-01: after the Security Engineer's dated confirmation T812 and the question that cited it (plan-160). All four ADR-016 conditions are met.
  - SEC-T702-09: record `brave-audit-acceptance-v4.md`.

## Completed tasks (this phase, plans 158 to 161)

- **Plans 158 to 160:**
  - T808 (Brave record v4)
  - T809 (register v16)
  - T810 and T811 (the release-gate runner tag; A-20)
  - T812 (the no-harness-fix confirmation)
- **Plan 161:**
  - T813 (audit), T814 (pin audit), T823 (Node floor), T824 (`opentelemetry-api` 1.45.2), T825 (security review)
  - T815 (version bump), T816 (release document), T817 (probe tag)
  - T818, T819 and T820 (gates), T826 (document fixes), T821 (verdict), T822 (publishing)

## Key decisions (the user's words, verbatim)

- "release plan go"
- At approval: "Approve (Recommended)", "v11.0.0, MAJOR (Recommended)", "Yes, probe first (Recommended)"
- "Yes, push the probe tag"
- "Accept for v11.0.0 (Recommended)" (SEC-T660-01 and SEC-T665-01, plan-160)
- "Already done" and "Yes, both" (runner, plan-159)
- The four publishing approvals above

## Open / carried over (for tracked-debt register v17)

| Item | Source | Owner |
|---|---|---|
| SEC-T660-01, SEC-T665-01: accepted for v11.0.0 only. Review on 2027-01-28 (token renewal): record whether a harness fix now exists and whether the outside closer is still right. A new acceptance is needed at the next release | release document, Conditions | the user; devops-engineer documents |
| SEC-T702-09: accepted for v11.0.0 only. Ends 2027-01-30, or earlier at the first Brave release above 2.1.4 | Brave v4 | devops-engineer; the user renews |
| TD-T697-07 (MEDIUM, not shipped) ends 2027-01-29 | register v16 | as v16 |
| CI image review date goes stale 2027-03-12 | `ci_images_reviewed_on: 2026-11-11` | devops-engineer |
| A bump of the tag jobs' image digest needs the runner's `allowed_images` updated (pin-bump checklist § 3) | plan-159 | the user |
| New LOW ids, tracked: SEC-T825-01 (a); TD-T774-01 / QA-T818-01 (rsync equal-size skip; regrade trigger in the T820 addendum); QA-T818-03; SEC-T820-02 (done in T821); TL-T819-03 to -05; TL-T821-01; SEC-T811-03, -05 | gate artifacts | backend-developer and devops-engineer, through the orchestrator |
| Fixed in this release: SEC-T814-01, SEC-T825-02, SEC-T784-01, SEC-T820-01, SEC-T741-17 (both halves), QA-T818-02 (document) | gate artifacts | — |
| SEC-T786-01: a `unit-tests` log showing Alpine `nodejs` 24.22.3 | T814 | orchestrator |
| User actions: A-21 (CI variables), A-22 (own settings files), K-20 / A-7 (live client checks) | register v16 § 7 | the user |

## Token metrics

Most tasks of plan-161 ran over their budgets by 1.1 to 2.4 times, by the harness's count (the counts are in plan-161 § Addenda 2 and the agents' reports). The largest were T820 (security, about 221k with its addendum), T816 to T826 (release manager, about 252k over four steps) and T819 with the independent check (tech-lead, about 202k).

## Next steps

Tracked-debt register v17, carrying plans 159 to 161. Each further step needs the user's word.
