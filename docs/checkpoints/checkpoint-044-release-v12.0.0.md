# checkpoint-044 — Release v12.0.0 published

**Phase:** release (`plan-182`): v12.0.0 audited, prepared, gated and published
**Written:** 2026-11-20
**Author:** orchestrator
**Based on:**
- `checkpoint-043`;
- `docs/plans/plan-182-next-release.md`;
- `docs/releases/v12.0.0.md`;
- `docs/artifacts/release-next-audit-v1.md`;
- `docs/artifacts/tracked-debt-register-v25.md` § 6.2;
- plans 162 to 181;
- MRs !707 to !709.

**Ledger at this checkpoint:** **0 active, 678 completed** after this closeout (checkpoint-043: 0 active, 623 completed).

## Phase summary

Release **v12.0.0** is MAJOR.
- The Opencode-generated agents lose permissions they had in v11.0.0. Agents without the grant are denied the shell, edit, web and delegation. The orchestrators can launch only their own 14 named subagents.
- The supported Opencode range is now 1.0.224 to 1.x.
- The manifest contract changed for fork authors.
- `build.py` refuses a `--project-id` that does not match the `origin` remote.

The release also fixes:
- **SEC-T702-09** (MEDIUM), with Brave 2.1.5. Its v11.0.0 acceptance ended on 2026-11-17.
- **SEC-T840-01**, which v11.0.0 shipped and nobody accepted.

It also ships `server-filesystem` 2.4.0, the hardened CA control, `sync-wiki` refusing redirects, the pin-age rule, and the CI-lock fix (`opentelemetry-api` 1.45.2).

Publishing ran in four steps. The user approved each at the moment it ran; the answers are quoted verbatim:

1. **Merge to `develop`.** MR !708 merged `release/v12.0.0`, unsquashed: merge commit `fb116f1f`, pipelines 3091255008 and 3091433730. The tree equals the verified tip `514503b0`. Approval: "Yes, merge to develop (Recommended)".
2. **Merge to `main`.** MR !709 merged it unsquashed: merge commit `ba17bda6`, pipeline 3092480187. The tree of `main` equals `514503b0`. Approval: "Yes, merge to main (Recommended)".
3. **The tag.** The annotated tag `v12.0.0` (tag object `e11e9a9f`) went on `514503b0`, pushed as `refs/tags/v12.0.0` only. The user first deleted the probe tag `v12.0.0-gate.1` in the web UI ("v12.0.0-gate.1 deleted"), and `git ls-remote --tags origin` then showed no `gate` ref (C-3). Approval: "Yes, push the tag (Recommended)".
   - **The tag-day dates:** the UTC date was 2026-11-20, before 2027-01-28 (C-2). The tag came before about 2026-11-24/25, while the two recorded young-pin exceptions still applied (C-5).
4. **The tag pipeline.** Pipeline 3092574856 passed `release-docs-gate`, `main-develop-drift-gate` and `release`. **All three ran on runner #59129270.** It is the first time the `release` job has run on this runner. The v12.0.0 probe's job log ties the runner to the user's host: "via gitlab-runner-16028".
   - The `release` job created the GitLab Release v12.0.0 (2026-11-20T05:22:16Z) on `514503b0`. Its description equals `docs/releases/v12.0.0.md` at the tag, by byte comparison.
   - `check-main-develop-drift.py`: main=v12.0.0, develop=v12.0.0, `releases_behind=0`, PASS.

**The release verdict is CONDITIONAL_PASS**, issued at `e0e3b355` with 0 open blockers:
- QA (T875), the Tech Lead's review by area (T876) and the release-level security re-check (T877) were each CONDITIONAL_PASS, with 0 critical and 0 high open.
- The independent check by tech-lead was PASS at `e0e3b355` (`docs/artifacts/independent-check-t878-v1.md`).
- **Two MEDIUM findings ship**, accepted by the user for v12.0.0 only: SEC-T660-01 and SEC-T665-01. The Security Engineer's dated confirmation T871 (2026-11-19) came first; the question that cited it followed, and the user answered "Accept for v12.0.0 (Recommended)". Their review is on 2027-01-28.

**The probe tag (T874):** pipeline 3090926673 proved the gates' routing to the hardened runner, which runs with `services_limit = 0` (the user's runner hardening, SEC-T811-05, is recorded in checklist § 5). It published nothing.

## Completed tasks (this phase: plans 162 to 182)

- **Registers:** v17 to v25.
- **Batches:**
  - I and J: plans 165, 167 and 168;
  - P: plan-172, the Brave report, filed by the user as issue #377;
  - AA, AB and X: plans 175, 177, 178 and 180.
- **The Brave 2.1.5 bump:** plan-173.
- **The SEC-T837-01 live check:** plan-170.
- **The release:** plan-182, tasks T869 to T881.

The details are in the plans' Outcomes and in `completed-tasks.md`.

## Key decisions (the user's words, verbatim)

- "release plan go"; "Approve (Recommended)"; "v12.0.0, MAJOR (Recommended)"; "Yes, probe first (Recommended)".
- SEC-T660-01 and SEC-T665-01: "Accept for v12.0.0 (Recommended)", after T871.
- "Yes, push the probe tag (Recommended)"; "Yes, merge to develop (Recommended)"; "Yes, merge to main (Recommended)"; "v12.0.0-gate.1 deleted"; "Yes, push the tag (Recommended)".
- Earlier in the phase: "Brave 2.1.5 go"; "Refresh, keep python pin (Recommended)"; "X + AB go"; "AA + TD-T849-01 go"; and the root-refresh approvals recorded in each plan.

## Open / carried over (for tracked-debt register v26)

| Item | Source | Owner |
|---|---|---|
| SEC-T660-01, SEC-T665-01: accepted for v12.0.0 only. Review on 2027-01-28, at the token renewal. A new acceptance is needed at the next release | release document, K-16 and Conditions | the user; devops-engineer documents |
| TD-T697-07 (MEDIUM, not shipped) ends 2027-01-29 | registers | as recorded |
| The CI image review fails from 2027-03-20 | `ci_images_reviewed_on: 2026-11-19` | devops-engineer |
| The young-pin exceptions (Brave 2.1.5, `server-filesystem` 2.4.0) lapse by themselves around 2026-11-24/25. Brave 2.2.0 (2026-11-19) is not pinned | checklist § 1; T870 | devops-engineer at the next bump |
| New LOW ids from the release gates: SEC-T877-01 (fixed in `e0e3b355`), QA-T875-01 (fixed), QA-T875-02 (fixed), TL-T876-01 (met), TL-T876-02, TL-T876-04, TL-T876-05 (applied); TL-T876-03 (dismissed); TL-T869-01 (fixed by T880), TL-T869-02 (info); SEC-T881-01 (fixed), SEC-T881-02 | gate artifacts | devops-engineer, through the orchestrator |
| `docs/wiki/mcp-servers.md:121` was corrected for `edit: allow` in `e0e3b355` | T878 | — |
| SEC-T702-08, the Brave upstream issue #377: closes when a fixed Brave release is pinned | batch P | the Brave project; devops-engineer |
| User actions: K-20 (live client checks); the optional removal of `/tmp/evidence-run` | register v25 § 7 | the user |

## Token metrics

These are the harness's counts for plan-182:

| Task | Count (about) |
|---|---|
| T869 | 128k |
| T870 | 88k |
| T871 | 138k |
| T880 | 90k |
| T881 | 82k |
| T872/T873 (release manager) | 171k |
| T875 | 143k |
| T876, with the independent check | 165k |
| T877 | 129k |
| T878 (release manager, two rounds) | 106k |

Several tasks ran over their budgets, by up to about 2 times.

## Next steps

Tracked-debt register v26, carrying plan-182 and its gate findings. Each further step needs the user's word.
