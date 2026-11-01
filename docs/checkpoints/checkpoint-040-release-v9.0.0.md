# checkpoint-040 — Release v9.0.0 published

**Phase:** release (`plan-124`): v9.0.0 audited, prepared, gated and published
**Written:** 2026-11-01
**Author:** orchestrator
**Based on:** `checkpoint-039`; `docs/plans/plan-124-release-v9.md` (with its addenda of 2026-11-01); `docs/releases/v9.0.0.md`; `docs/artifacts/release-v9-audit-v1.md`; MRs !628 to !631
**Ledger at this checkpoint:** **0 active, 510 completed** (checkpoint-039: 0 active, 497 completed)

## 1. Phase summary

Release **v9.0.0** (MAJOR: Cursor support removed under ADR-010) is published. The order was B1 (`CONTRIBUTING.md`, release steps 5 to 7; the user approved each step on 2026-11-01): MR !630 `release/v9.0.0` into `develop` (merge commit `fc46dc0a`), MR !631 `release/v9.0.0` into `main` (merge commit `3510b0e9`, `verify-main-sync-merge.py` PASS, `main^2` = the release tip), then the annotated tag `v9.0.0` on the release tip `e4c7e7d4`. Tag pipeline 3014698085: `release-docs-gate`, `main-develop-drift-gate` and `release` all succeeded. The GitLab Release v9.0.0 was created by the job with a description equal to `docs/releases/v9.0.0.md` at the tag (61,186 characters, compared exactly); the `CHANGELOG.md` artifact was uploaded. After the tag, `check-main-develop-drift.py` reports `main=v9.0.0 develop=v9.0.0 releases_behind=0` (QA-T707-03 condition met) and `git describe` finds `v9.0.0` on both branches.

The release verdict is **CONDITIONAL_PASS** with 0 open blockers: QA (T707), Tech Lead by area (T708) and the release-level security re-check (T709) were CONDITIONAL_PASS with 0 critical and 0 high; the top-level session checked the release document independently at `a47d982d` (Release Gate Policy item 5); SEC-T662-01 (MEDIUM) is closed; SEC-T702-09 (MEDIUM, Brave 2.1.4) ships accepted by the user's decision recorded in the verdict.

## 2. Completed tasks (this phase)

T700 (release-level audit), T701 (token-docs batch), T702 (pin audit without `--accept`), T703 (release gate checks the migration pointer), T712 (Brave forced to stdio, acceptance v3, root refresh 22), T704 (release tree, version markers), T705 (release document), T706 (release job rehearsal in the CI image), T707 to T709 (the gates), T710 (verdict), T711 (publish, this checkpoint).

## 3. Open / carried over

No ledger row is open. Items for the next register version (v4) and later work:

| Item | Source | Owner |
|---|---|---|
| SEC-T702-09 (MEDIUM, accepted): Brave 2.1.4 advisories; re-audit at any Brave release above 2.1.4; acceptance v3 ends 2027-01-30 | T702, T712, `brave-audit-acceptance-v3.md` | devops-engineer; the user renews |
| Tracked LOW: QA-T707-01 (false Opencode "differs" note), TL-T708-03 to -07, D-T710-2 (CHANGELOG entry order in the job artifact), SEC-T701-01 to -03, SEC-T703-01 to -03, SEC-T712-05, SEC-T702-08, SEC-T709 (all applied) | the gate and task reviews | per the reviews |
| SEC-T686-03 and SEC-T686-06: see section 4 | T686, T709 | orchestrator; close in register v4 |
| User actions UA-T699-1 to -3 (plaintext `.env` files of other projects, the JWT secret file on the CWSO server, the stored Context7 CLI key); renew the GitLab token (2027-01-28) and the CWSO bearer token (2027-01-29) | register v3, review T697-T699 | user |
| Release Gate Policy item 2 and user-accepted MEDIUM findings: the policy text says a MEDIUM is fixed before a release ships; v8.0.0 and v9.0.0 both shipped one by the user's recorded decision. Consider a ruling that aligns the text with practice | T710 | orchestrator, then the user |

## 4. Tag pipeline observations (T709 § What T711 must observe)

- **Before the tag**: Brave `latest` 2.1.4; the seven-entry v3 gate command exit 0 (on `e4c7e7d4`); protected tag `v*` create access Maintainers only; no `v9*` tag existed.
- **SEC-T686-06 (runner and clone)**: `gitlab-runner 19.5.2`, Docker executor, the pinned `python:3.12-alpine` digest; the source step "Fetching changes" reused the runner's repository. The `git fetch` calls inside `publish-release.py` ran under the filtered environment and succeeded (the job created the release). Whether the runner passes its credential through a credential helper or the remote URL is not visible in the log: the fail-closed path was not exercised. Status: the job works on this runner; the clone method stays undetermined (LOW).
- **SEC-T686-03 (job-token exposure)**: the `release` job log (95 lines) contains no job-token value: 0 occurrences of the job-token prefix, 0 `gitlab-ci-token:` credentials with a value, 0 `[MASKED]` (the script never printed the token, so masking was not exercised). `JOB-TOKEN` and `WIKI_TOKEN` appear once each, as names in the job's command text. Status: no exposure observed.
- **Releases API with `JOB-TOKEN`** on a protected tag: accepted (release created, body equal to the document).

## 5. Key decisions (the user's, 2026-11-01, recorded verbatim in plan-124, the briefs and the release verdict)

- plan-124 approved; the token-docs batch in v9.0.0; the Brave decision after T702; the release job rehearsal.
- Brave: "Grade, then renew (Recommended)", then "Renew + force stdio (Recommended)" (acceptance v3); the user's live check UA-T712-1 confirmed that `--transport stdio` overrides `BRAVE_MCP_TRANSPORT`.
- "Exclude docs/decisions/ (Recommended)"; "Fix in T704 (Recommended)".
- "Ship with it accepted (Recommended)" for SEC-T702-09 under Release Gate Policy item 2.
- The three publishing steps, each approved at its moment.

## 6. Maturity distribution

Unchanged since checkpoint-039: 80 components, 53 stable, 27 experimental, 0 failing (`check-maturity.py`).

## 7. Blockers (active)

None.

## 8. Token usage

Not measured per phase. Recorded overruns of agents against their brief budgets: T700 (about 219k against 120k), T705 (about 197k against 130k), T712 (about 151k against 90k), T708 (about 178k against 120k). Several agents were interrupted once by the account's usage limit and resumed from their saved state.

## 9. Next steps

- The tracked-debt register v4 (the LOW items above, SEC-T686-03/-06 status, the v9.0.0 closures).
- The LOW batches of register v3 (the knowledge batch, the CWSO hardening batch) when the user chooses.
- The user actions in section 3.

## Compression note

This checkpoint is the canonical handoff after v9.0.0. Subsequent agents receive only this checkpoint, their task brief and the referenced artifact versions.
