# checkpoint-038 — Release v8.0.0 published

**Phase:** release (`plan-120`, `plan-121`, `plan-122`): v8.0.0 prepared, gated and published
**Written:** 2026-10-16
**Author:** orchestrator
**Based on:** `checkpoint-037`; `docs/releases/v8.0.0.md`; `docs/artifacts/release-v8-audit-v2.md`; MRs !558 to !590
**Ledger at this checkpoint:** **0 active, 458 completed** (checkpoint-037: 0 active, 354 completed)

## 1. Phase summary

Release **v8.0.0** is published: tag `v8.0.0` (annotated) on the release-branch tip `6630dd0`, `main` at `8f829a6` (merge commit; `main^2` is `6630dd0`; the trees of `main`, the release branch and `develop` are equal), GitLab Release created by the tag pipeline with `docs/releases/v8.0.0.md` as its description (66,745 characters, byte for byte), all three tag jobs green. The release verdict in the document is **CONDITIONAL_PASS** with 0 open blockers: the QA gate (T648), the Tech Lead review by area (T649) and the security re-check (T650) were all CONDITIONAL_PASS with 0 critical and 0 high findings, and every SECURITY:MEDIUM finding was either fixed or explicitly accepted by the user. The final tree was checked before the first push: suite 1273 tests OK (skipped 23), scorecard 34 cases / 28 pass / 0 regressions, `sync.mjs --check` and registry check clean, `check-maturity.py` 80 components / 0 failing, evaluator hash no drift against baseline v21, `verify-release-docs.py` and `check-version-consistency.py` pass, publish dry run OK.

The release path found one thing the plan did not foresee: `main` (v7.0.1) was not an ancestor of the release branch (34 commits on `main` that `develop` never received, because the pre-B1 flow did not back-merge), so merging the release branch into `main` conflicted. The documented "ancestry restore" (merge `origin/main` into the release branch with `-s ours`, tree unchanged) was used with the user's approval. `develop` was already merged and does not contain that ancestry commit; `git describe` on `develop` will not find `v8.0.0` until `develop` receives it (a content-empty merge, not done because the user chose B1, "develop, then main, then tag", with no back-merge).

## 2. Completed tasks (this phase)

Generated from `docs/tasks/completed-tasks.md` (the ledger is the source of truth). Since checkpoint-037 about 104 tasks closed. Highlights by theme:

- **Rulings and ADRs.** The ADR-007/008 workflow rulings (T576 to T618 and the T621/T632/T634 decisions), ADR-009 (accepting ADR-008, T634), the release-documents ruling (T632: the union contract, B1 order, document-only release body).
- **Promotions and the evaluator.** Golden realignment under grant G-1 (T628: items 1-10 and 12; item 11 deferred), evaluator baseline v21 (T629), `tech-lead` promoted to `stable` with the orchestrator's independent re-run (T630). `orchestrator` stays `experimental`.
- **Security fixes.** SEC-001 (installer followed symlinks and `--update` deleted files outside the target, T636), SEC-002 (the `@anthropic/mcp-filesystem` package, graded HIGH, T637/T638), SEC-T646-01 (fetch server SSRF, T653 evidence, T655 removal), the PoC scanner hardening (T603 to T620).
- **MCP surface.** Corrected and pinned server entries (T638), the fetch server removed and the Playwright entry hardened with a blocked-origins list (T654, T655), per-platform MCP tool-name mapping (T657), named non-"unsafe" Playwright grants for four agents, server-level denials of six Playwright tools on Opencode and Gemini CLI (T658), named GitLab tools for qa-engineer and scrum-master (T660), the quote-aware inline-array reader (T655, T656).
- **Release tooling.** The CI release job hardening and the document-whole release body (T619, T635, T640), the version-check exclusion of `tests/golden/` (T642), the single release document (T639).
- **Release preparation and gates.** T641 audit addendum, T643 and the root refreshes 17 to 20, T644 to T651, T652 (this publish).
- **Skill.** `gitlab-api-push-fallback` created by a real `/skillify` run with the user (T627).

## 3. Open / carried over

No ledger row is open. Follow-ups, tracked here and in the release document's Known issues (no task rows yet):

| Item | Source | Owner (proposed) |
|---|---|---|
| Opencode per-agent denies and a Cursor CLI deny list (the fixable parts of SEC-T658-01) | user: "Accept the unfixable remainder; fix the rest after v8.0.0" | devops-engineer, review tech-lead; right after the release |
| Token scope and environment handling for `GITLAB_PERSONAL_ACCESS_TOKEN` (SEC-T660-01) | user: "Accept the risk, plan after the release" | devops-engineer, review tech-lead; the sprint after the release |
| Named GitLab tool sets for orchestrator and poc-orchestrator, then devops-engineer and release-manager (SEC-T660-04) | T660 review | devops-engineer |
| G-2 and baseline v22: promote `orchestrator`, move the `/skillify` golden case (item 11) now that the `/skillify` run and the v8.0.0 release notes exist | plan-122 / promotion plan | orchestrator (needs a separate user approval) |
| Tracked LOW debt: SEC-T660-02..07, SEC-T658-02..07, SEC-T657-04/-07/-09, SEC-T655-06/-07, SEC-T650-03..05, SEC-T646-02..06, SEC-T635/T636/T640/T619 items, TL-T649-01..10 (function sizes, invalid-JSON traceback, manifest-validation order, dry-run default tag, ...), K-1..K-21 of the release document | reviews | per item |
| `develop` does not contain the ancestry-restore commit `6630dd0`, so `git describe` on `develop` does not see `v8.0.0` | B1 order | decide whether to add a content-empty `release/v8.0.0` -> `develop` MR |
| `install.sh` does not print the Playwright browser step; the `CHANGELOG.md` intro paragraph is placed inside the newest entry (pre-existing) | QA-T648-02, K-12 | devops-engineer |

## 4. Key decisions

- ADR-009 accepts ADR-008 (ADR-008 untouched); the release order B1 and the document-only release body (`docs/artifacts/release-documents-ruling-v1.md`).
- User risk acceptances of 2026-10-15 recorded in the release document: SEC-T658-01 unfixable remainder (Cursor IDE, Gemini per-agent scoping, Pi agents without `mcp__` entries), SEC-T660-01 (a token in the environment is reachable by an agent with a shell); sign-off conflict (`tech-lead` promoted and reviewing) acknowledged; audit decision D-4 (`WIKI_TOKEN` Protected and Masked, `v*` tags protected) stated by the user and not verifiable with the tools the agents have.
- Fetch server removed instead of replaced: the evaluation (T654) found the Playwright origin flags do not cover redirects, so Playwright is not a drop-in SSRF-safe fetch replacement; the agents keep the platform `web` tool.

## 5. Maturity distribution

From `implementation/registry/summary.md` (registry up to date): 80 components checked, 0 failing their claimed level.

| Category | Stable | Experimental | Deprecated | Total |
|----------|-------:|-------------:|-----------:|------:|
| Agents | 27 | 1 | 0 | 28 |
| Commands | 14 | 5 | 0 | 19 |
| Instructions | 4 | 2 | 0 | 6 |
| Skills | 7 | 20 | 0 | 27 |
| **Total** | 52 | 28 | 0 | 80 |

Change since the last release checkpoint: `tech-lead` moved from `experimental` to `stable` (T630, evaluator baseline v21, independent re-run by the top-level session); skill `gitlab-api-push-fallback` was added as `experimental`.

## 6. Artifacts produced (selection)

`docs/releases/v8.0.0.md`; `docs/artifacts/release-v8-audit-v1.md`, `release-v8-audit-v2.md`; `qa-gate-release-v8-v1.md`, `code-review-release-v8-v1.md`, `security-review-release-v8-v1.md`, `security-review-release-v8-v2.md`; the delta security reviews `security-review-t635-*`, `-t636-*`, `-t638-*`, `-t640-*`, `-t646-*`, `-t655-*`, `-t657-*`, `-t658-*`, `-t660-*`; `fetch-ssrf-test-t653-v1.md`, `fetch-replacement-evaluation-v1.md`, `mcp-tool-name-mapping-v1.md`, `mcp-server-denials-v1.md`, `mcp-server-packages-v1.md`, `release-rehearsal-t647-v1.md`; `evaluator-hash-known-good-v21.json`; ADR-009; plans `plan-120`, `plan-121`, `plan-122` (with six addenda).

## 7. Blockers (active)

None. (The release verdict carries conditions, not blockers: see section 3 and the release document.)

## 8. Token usage

Not measured in this session (the session ran across a context compaction and several agent rate-limit interruptions); the per-task budgets of `AGENTS.md` were not tracked. Recorded here as a gap, not as a pass.

## 9. Next steps

- Phase: post-release follow-up (see section 3).
- First tasks to create after the user chooses the order: the Opencode per-agent denies and the Cursor CLI deny list; the token-scope plan; the named GitLab sets.
- The user's side: the local primary checkout is still at `bfd4ba7` (it carries local changes to `.vscode/mcp.json` and `.claude/settings.json`); update it when convenient. A search tool once returned a line of the local untracked `.env` (a CWSO bearer token; the value is not recorded anywhere): consider whether it needs rotating.

## Compression note

This checkpoint is the canonical handoff for the post-release phase. Subsequent agents receive only this checkpoint, their task brief and the referenced artifact versions.
