# checkpoint-041 — Release v10.0.0 published

**Phase:** release (`plan-145`): v10.0.0 audited, prepared, gated and published
**Written:** 2026-11-07
**Author:** orchestrator
**Based on:** `checkpoint-040`; `docs/plans/plan-145-release-v10.md`; `docs/releases/v10.0.0.md`; `docs/artifacts/release-v10-audit-v1.md`; `docs/artifacts/tracked-debt-register-v11.md` § 6.2; MRs !653 to !655
**Ledger at this checkpoint:** **0 active, 562 completed** (checkpoint-040: 0 active, 510 completed)

## Phase summary

Release **v10.0.0** (MAJOR: `install.sh --update` and `--projections-only` delete the authoring-only command `/prepare-release` from target projects, T725, with T722 and T714 also breaking a target, per audit T753) is published. The order was the one in `CONTRIBUTING.md` § Cutting a release, and the user approved each step at its moment on 2026-11-07:

1. MR !654 merged `release/v10.0.0` into `develop`, unsquashed (merge commit `c8f538d6`).
2. MR !655 merged it into `main`, unsquashed (merge commit `623eea7c`). `verify-main-sync-merge.py` passed, and `main^2` is the release tip. `main`'s pipeline 3039866416 passed all five jobs.
3. The annotated tag `v10.0.0` (tag object `ba4abfc1`) went on the release tip `d593aeb3`. Before tagging, these were checked again: the tip is `origin/main^2`, it is an ancestor of `origin/develop` and `origin/main`, its tree equals `origin/main`'s, and no `v10*` tag existed.

Tag pipeline 3039977704 passed `release-docs-gate`, `main-develop-drift-gate` and `release`. The `release` job created the GitLab Release v10.0.0 on commit `d593aeb3`. Its description equals `docs/releases/v10.0.0.md` at the tag, compared exactly (56,774 characters). `main` did not move between the tag and the tree check (still `623eea7c`, TL-T761-12). After the tag, `check-main-develop-drift.py` reports `main=v10.0.0 develop=v10.0.0 releases_behind=0`, and `/validate-tasks` passed.

The release verdict is **CONDITIONAL_PASS** with 0 open blockers:
- QA (T760), the Tech Lead's review by area (T761) and the release-level security re-check (T762) were each CONDITIONAL_PASS, with 0 critical and 0 high open.
- SEC-T756-01 (HIGH, CVE-2026-115557 in the CI image's Python) was fixed by T765 (Python 3.12.16) and closed by T762.
- The release manager issued the verdict (T763) at `cd803b28`. The independent check there was PASS (`docs/artifacts/independent-check-t763-v1.md`).
- Five MEDIUM findings ship accepted by the user for v10.0.0 only, under ADR-011 and ADR-012: SEC-T660-01, SEC-T665-01, the remainder of SEC-T657-01/SEC-T658-01, SEC-T702-09 and SEC-T756-02. The record is the Conditions block of the release document.

## Completed tasks (this phase)

T753 (release-level audit), T754 (the flaky temp-name test, batch W), T755 (MCP pin audit), T756 (re-grade of the accepted MEDIUMs), T765 (Python image 3.12.16, the CA check, the installer note), T757 (release branch, version markers), T758 (release document), T759 (release job rehearsal in the CI image), T760 to T762 (the gates), T763 (verdict and independent check), T764 (publish, this checkpoint).

## Open / carried over

No ledger row is open. Items for tracked-debt register v12 and later work:

| Item | Source | Owner |
|---|---|---|
| The five MEDIUMs accepted for v10.0.0 only (ADR-011): each needs a fix or a new acceptance before the next release | release document, Conditions | the user; orchestrator tracks |
| Brave 2.1.4 acceptance ends 2027-01-30 or at the first Brave release above 2.1.4 | SEC-T702-09, T755 | devops-engineer; the user renews |
| CI image review date goes stale on 2027-02-19 | `ci_images_reviewed_on: 2026-11-06` | devops-engineer |
| Node image bump after the advisory due on 2026-11-11, with T765's CA check first | T762, T765 | devops-engineer |
| SEC-T762-04: two rule questions for the user | T762 | the user |
| New ids for register v12: SEC-T756-xx, SEC-T762-01 to -05, TL-T753-05 to -07, TL-T761-xx, TL-T763-01/02, QA-T760-xx, the correction to § 6.2 item 19; A-19 closed (both probe tags deleted by the user) | the gate reviews | orchestrator |
| TL-T761-03 (the `--projections-only` warning in README and wiki) was decided by the orchestrator, not the user | T761 | orchestrator; the user may overrule |
| The tracked batches of register v11 (I, J, K, L, M, N, P, Q, R, S, V, F, U), SEC-T741-17's runner, the route of SEC-T735-06 and -07 | register v11 | the user chooses |
| User actions UA-T699-1 to -3, A-20; renew the GitLab token (2027-01-28) and the CWSO bearer token (2027-01-29) | registers v3 to v11 | user |

## Key decisions

The user's, recorded verbatim in plan-145, the briefs and the release document:

- "release go"; AskUserQuestion: "v10.0.0, MAJOR (Recommended)", "Add batch W only (Recommended)", "Docker, this rehearsal only (Recommended)", "Approve (Recommended)" (plan-145).
- "Approve both (Recommended)": the new `python:3.12-alpine` digest, and the `_ssl` check in the rehearsal.
- "Accept for v10.0.0 (Recommended)" for each of SEC-T660-01 and SEC-T665-01, the SEC-T657-01/SEC-T658-01 remainder, SEC-T702-09 and SEC-T756-02.
- The three publishing steps, each approved at its moment: "develop go", "main go", "tag go".

## Tag pipeline observations

These close register v11 § 6.2 items 6, 14 and 28 and the first-tag rehearsal list in `CONTRIBUTING.md`:

- **Runner and image:** all three jobs ran on `gitlab-runner 19.5.3 (33227fd4)`, Docker executor, on the pinned `python:3.12-alpine@sha256:e064671c…`. The runner was 19.5.2 at the probes, and nothing in the logs differs because of that.
- **`release` job (the first real run of the changed `publish-release.py`):**
  - "Fetching changes" initialized an empty repository ("Created fresh repository"), so `GIT_STRATEGY: clone` took effect.
  - The script's `git` calls ran under the allowlisted environment and worked. The `CHANGELOG.md` artifact holds the `## [v10.0.0] - 2026-11-07` entry below `## [Unreleased]`, with the line "_Commits since v9.0.0._". D-T710-2 is now observed.
  - The Releases API accepted `JOB-TOKEN` on the protected tag. No 401 or 403 appears in any job log.
- **Job token:** in all three job logs, 0 occurrences of the job-token prefix, 0 `gitlab-ci-token:` credentials with a value, and 0 `[MASKED]`. `JOB-TOKEN` appears once, as a header name in the `release` job's command text.
- **`release-docs-gate`:** ran `rm -rf .git "${CI_PROJECT_DIR}.tmp"`, then pip and `verify-release-docs.py` through `scripts/run-allowlisted.py`. The runner's later stage, cleanup of file variables, ran without error. The 10-minute `timeout` was not reached. As at the probe, the log shows that the removal ran, not that the credential file was there to remove (SEC-T751-05 stays as recorded).
- **`main-develop-drift-gate`:** ran `apk`, both fetches with `--keep CI_JOB_TOKEN`, the drift check and the tag tree check through `scripts/run-allowlisted.py`. Both fetches worked, and the tree check passed (tree `caad9aa2ccdd`). The project is public, so the fetches still do not prove that the job token was used (item 28's limit holds).
- **Rendering (item 8):** GitLab's rendered Release holds 0 merge-request, issue, user-mention, commit, label, milestone or snippet reference links. The escaped references and the `@user` text in code spans stayed literal. Item 8's npm step does not run in a tag pipeline (no npm job matches the tag rule), so it remains covered by the merge request pipelines only.

## Maturity distribution

Unchanged since checkpoint-040. `check-maturity.py` checked 80 components, 0 of them failing their claimed level.

| Category | Stable | Experimental | Deprecated | Total |
|----------|-------:|-------------:|-----------:|------:|
| Agents | 28 | 0 | 0 | 28 |
| Commands | 14 | 5 | 0 | 19 |
| Instructions | 4 | 2 | 0 | 6 |
| Skills | 7 | 20 | 0 | 27 |
| **Total** | **53** | **27** | **0** | **80** |

## Artifacts produced

`docs/releases/v10.0.0.md`; `docs/artifacts/release-v10-audit-v1.md`, `mcp-pin-audit-v10-v1.md`, `security-review-t756-accepted-mediums-v1.md`, `ca-check-t765-v1.md`, `release-rehearsal-t759-v1.md`, `qa-release-v10-v1.md`, `tech-lead-release-v10-v1.md`, `security-review-release-v10-v1.md`, `independent-check-t763-v1.md`; the GitLab Release v10.0.0 and the `CHANGELOG.md` artifact of job 17831135514; this checkpoint.

## Blockers (active)

None.

## Token usage

Not measured per phase. As in checkpoint-040, the gate agents used well above their brief budgets by the harness's count (160k to 230k against 60k to 120k), as plan-145's risk assessment expected. The top-level session's context was compacted during the release and resumed from its summary.

## Next steps

- Tracked-debt register v12 (the ids in the table above, the v10.0.0 closures, D-T710-2 observed).
- The user's two rule questions from SEC-T762-04.
- The Node image bump after 2026-11-11, with the CA check first.
- The tracked batches when the user chooses; the user actions in the table above.

## Compression note

This checkpoint is the canonical handoff after v10.0.0. Subsequent agents receive only this checkpoint, their task brief and the referenced artifact versions.
