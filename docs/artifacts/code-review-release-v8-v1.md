# Artifact: code-review-release-v8-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: tech-lead (read-only; scratch copy made with `git archive` for test runs). Recorded by the orchestrator from the executor's report.
- **Gate**: code review by area (T649). **Date**: 2026-10-15.
- **Target**: `release/v8.0.0` at `57d0107`. The reviewer's checks of ADR-007/008/009 went through the rulings and the knowledge text only (the ADR files were not re-read, unverified).
- **Based on**: `docs/tasks/task-T649.md`, `docs/plans/plan-122-release-v8-wave-3.md` (all addenda), `docs/releases/v8.0.0.md`, `docs/artifacts/release-v8-audit-v2.md`, `release-documents-ruling-v1.md`, the MCP artifacts and the security reviews of T635 to T658.

## Sign-off conflict disclosure (audit v2 §8)

`tech-lead` is promoted to `stable` in this release (T630) and authored the exit review of that promotion (T625, `code-review-t619-v2.md`) and is the reviewer here. `qa-engineer` independently checked T625 (T626; round 1 failed on form gaps, round 2 passed); the orchestrator independently re-ran `check-maturity.py` in T630. The reviewer's own re-run (80 components, 0 failing; agents 27 stable and 1 experimental) is not independent evidence. Nothing in the four area verdicts rests on the promotion.

## Verdict: CONDITIONAL_PASS

| Area | Verdict |
|---|---|
| A. Installer and tooling | CONDITIONAL_PASS |
| B. Knowledge text and rulings | PASS |
| C. CI and release job | CONDITIONAL_PASS |
| D. Documentation | CONDITIONAL_PASS |

The code, tooling, knowledge text and CI are acceptable to ship; the tag is not authorised until MUST-1 to MUST-4 are closed.

## What was run

263 targeted functional tests OK; a full `tests/run.py` on a copy without `.git` and `held-out` showed 13 artefact failures (the QA gate owns the real full-suite verdict, unverified here); `verify.mjs` no drift across 584 files; `check.py` 258 checks, 0 errors; `check-version-consistency.py` PASS; `verify-release-docs.py` PASS; `check-maturity.py` 0 failing; the drift script fails offline with "develop marker version v8.0.0 is not a known git tag" (expected before the tag); the dry run prints `DRY RUN OK` in all three modes; installer probes: plain install and `--update` exit 0, a symlinked `.claude`, a symlinked `CLAUDE.md`, a dangling `.mcp.json` link and a symlink under `--dry-run` all refused with exit 1 and nothing written outside the target, the real ledgers merge idempotently, the Opencode `permission` merge keeps a user `playwright_*: allow` and puts the generated denies last, a non-dict `permission` is replaced. `v7.0.1..release` has 239 non-merge commits (475 with merges).

## Findings

| ID | Severity (Must / Should / Nice) | Security scale | Where | Finding |
|---|---|---|---|---|
| TL-T649-01 | Should Fix | none | `sync.mjs:451 emitMcp` (117 lines), `:625 syncPlatform` (130), `:203 parseServersYaml` (62); `install.sh:771 sync_tree_into` (76); `merge-mcp-json.py:139 main` (63); `verify-release-docs.py:175 main` (60) | Functions exceed the 50-line standard; T658 grew two of them. Tracked debt; split per format and extract prune/validate steps |
| TL-T649-02 | Should Fix | none | `merge-mcp-json.py:168-170` | Invalid JSON in a user's config gives a raw traceback after `install.sh` has replaced the platform tree (half-applied `--update`, fails closed); same as SEC-T658-05(b). Tracked debt |
| TL-T649-03 | Should Fix | none | `sync.mjs:772-775` | `validateMcpToolNamesStyle` runs inside the per-manifest write loop; the comment at `:369-370` says "before any file is written" (SEC-T658-07(b)). Tracked debt |
| TL-T649-04 | Nice to Have | none | `sync.mjs splitInlineArray` | Does not refuse a trailing comma, `[]`, `a: b` items or `{}` items (author-error hazard; shipped entries are covered by the parity test) |
| TL-T649-05 | Nice to Have | none | `dry-run-publish-release.py:227` | Default `--tag` is `v7.0.1`; default to the current marker or require `--tag` |
| TL-T649-06 | Nice to Have | none | `install.sh:1086-1146`, `:83` | Mixed indentation; a missing `--target`/`--platform` value fails with an unbound-variable error |
| TL-T649-07 | Nice to Have | none | `publish-release.py:245-253` | A socket timeout during `read()` is a traceback, not `ReleasePublishError` (still fails closed) |
| TL-T649-08 | Nice to Have | none | `merge-task-docs.py:107-113` | The table bound is the first markdown separator; a ledger with an earlier legend table would drop rows (theoretical; real ledgers round-trip) |
| TL-T649-09 | Nice to Have | none | `tech-lead.md:4` | `edit` and `execute` while the role is read-only during review: by design, policy not tooling |
| TL-T649-10 | Nice to Have | none | `skills/release-workflow/SKILL.md` §4 | The skill's template still shows `# Release Notes — v<VERSION>` while RD-2 declares `# Release v<VERSION>` |
| TL-T649-11 | **Must Fix (procedural, before the tag)** | none | plan-122 T652 text vs `CONTRIBUTING.md:166-203` and the ruling §5.3 | T652 said "MR develop to main" and "tag on the verified main tip"; the user chose B1 (`release/v8.0.0` to `develop`, then `release/v8.0.0` to `main`, tag on the release-branch tip `origin/main^2`). Corrected in the T652 brief (plans are immutable) |
| TL-T649-12 | Should Fix | none | `verify-release-docs.py:207-220` | The gate checks only that `## RELEASE VERDICT` exists; it passes with `Status: pending` and `YYYY-MM-DD` rows. T652 carries an explicit tag-readiness grep; add it to the gate afterwards |
| TL-T649-13 | Should Fix | none | `.gitlab-ci.yml:179-191`, `GRACE_RELEASES = 1` | A tag pushed while `main` is one release behind passes the gate; "main merged before the tag" is a procedure duty in T652 |
| TL-T649-14 | Nice to Have | none | `.gitlab-ci.yml:196-202` | Floating `python:3.12-alpine` and unpinned `apk add git` (K-12) |
| TL-T649-15 | Nice to Have | none | release document K-10 | "Size not measured": measured 239 non-merge commits (475 with merges). Fixed by the T645 amendment |
| TL-T649-16 | Should Fix | none | `implementation/PREREQUISITES.md` | Lists Git 2.30+; the `poc-security-audit` requirements (git 2.40+, `mcp==2.2.0`) are missing. Fixed by the T645 amendment |
| TL-T649-17 | Should Fix | none | `README.md:186-194` | "Prunes nothing; pruning starts at the second run" contradicts the v7.0.1-sidecar case. Fixed by the T645 amendment |
| TL-T649-18 to -20 | Nice to Have | none | release document M-8, A-24, Highlights | `--source <generated file>` path; "11 sections" counts the title; the extended servers are on by default on non-Copilot platforms. Fixed by the T645 amendment |

No security finding was raised by the reviewer in area A; `poc_scan.py` (857 lines) was reviewed structurally only (unverified: full scanner logic).

## Items before the tag

| # | Item | Owner |
|---|---|---|
| MUST-1 | The open SECURITY:MEDIUM findings SEC-T658-01 and SEC-T657-02 (the Release gate rule: fixed before the release ships, or the user decides) | T650, T651, user. Outcome: SEC-T657-02 is fixed by T660; SEC-T658-01's unfixable remainder is accepted by the user on 2026-10-15 ("Accept the unfixable remainder; fix the rest after v8.0.0 (Recommended)") |
| MUST-2 | Audit decision D-4: `WIKI_TOKEN` Protected and Masked, `v*` tags protected | user |
| MUST-3 | No `pending` or `YYYY-MM-DD` left in the release document; real `Status`, counts, `Open blockers`, `Blocker IDs`, `Timestamp`; the `Release` line equals the `Status` | T651 |
| MUST-4 | TL-T649-11: the T652 procedure is the B1 order | orchestrator (done in the T652 brief) |
| MUST-5 | `verify-release-docs.py --tag v8.0.0` and `check-version-consistency.py` on the final tree after any edit, and the held-out isolation test on every artifact committed | whoever edits |

## Gate rows for the release document

Architecture: CONDITIONAL_PASS (the order B1, the single-sourced `denyTools` and the pinned MCP set are respected; MUST-4 is the condition). Implementation: CONDITIONAL_PASS (conditions C-A1 and C-A2: TL-T649-01 to -03 are tracked debt). Combined: CONDITIONAL_PASS; merge authorisation for `release/v8.0.0` is "yes, with conditions tracked"; the tag is not authorised until MUST-1 to MUST-4 are closed.

## Not checked

A line-by-line read of every one of the 62 changed knowledge files (greps, the diffs of the release/gate/tech-lead documents, `check.py` and `check-maturity` were used); ADR-007/008/009 bodies; live runs on musl/BSD hosts and Windows; a rollback after a partial update failure; the GitLab API half of the job, the runner's fetch settings and the description size limit.
