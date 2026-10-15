# Artifact: release-v8-audit-v2.md

> Immutable once produced; revisions bump `<N>`. This is the addendum that `release-v8-audit-v1.md` announced (its header and §5 C-9). It does not edit v1.

**Based on:** `release-v8-audit-v1.md` (all of it; §3 Migration draft, §4 Known issues draft, §5 concerns C-1..C-9, §6 not verified); `docs/tasks/task-T641.md`; `docs/plans/plan-121-release-v8-wave-2.md`; the ledger rows T619..T640 of `docs/tasks/completed-tasks.md`; and the artifacts those rows name: `security-review-release-v8-v1.md`, `security-review-t619-release-job-v1.md`, `-t620-jwt-cost-v1.md`, `-t635-release-job-conditions-v1.md`, `-t636-symlink-guard-v1.md`, `-t638-mcp-packages-v1.md`, `-t640-release-body-v1.md`, `code-review-t619-v2.md`, `code-review-check-t625-v1.md`/`-v2.md`, `release-documents-ruling-v1.md`, `mcp-server-packages-v1.md`, `adr-008-status-and-severity-scales-v1.md`, `docs/decisions/ADR-009-adr-008-acceptance-record.md`, `promotion-and-golden-realignment-plan-v1.md`, `remaining-observations-ruling-v1.md`, `evaluator-hash-known-good-v21.json`.

**Author / mode:** Tech Lead, review mode (read-only). Only this file was written. No source, script, version, CHANGELOG, README, ledger or brief status line was changed. Commands run were read-only (`git`, `grep`, the gate scripts) plus scratch copies under the session scratchpad (a `git archive` of `origin/develop` with `tests/golden/held-out` excluded, a scratch install target, a scratch git repository for the drift gate). Nothing was pushed or merged. This is an inventory addendum, not a gate verdict, so no `VERDICT` block is issued. Decision IDs referenced: ADR-007, ADR-008, ADR-009. Requirements/architecture versions: not applicable.

**Basis marker:** **(V)** = verified (I read the file or the diff, or ran a command; the evidence says which). **(I)** = inferred (reason stated). **(unverified)** = not re-read, not run, or not checkable from here.

**Code state audited:** `origin/develop` = `ac63dbe` (2026-10-15 06:32 UTC), which is the base of this worktree (`be0fd70` adds only the T641 brief and ledger row). The local branch `develop` in the primary checkout is behind it (`bfd4ba7`); I used `origin/develop` as recorded by the last fetch. I did not fetch, so a commit on the remote after that fetch is **(unverified)**.

**Decisions that belong to others (not taken here):** the counting rule for the `RELEASE VERDICT` fields (release manager), the release version and the tag (user), whether `tests/golden/` joins the version-check exclusions (user; see D-1), and the first-use rehearsal of the release job (user: it publishes). Each is listed as open with a recommendation in §2 and §9.

---

## 1. Coverage and what changed since v1

### 1.1 Coverage

| Item | Value |
|---|---|
| Range | `v7.0.1..origin/develop`: 446 commits (`git rev-list --count`), 222 of them merges; v1 had 411 and 201 |
| Added since v1 | 35 commits, `5e07a6b..ac63dbe`, 17 first-parent merges (V) |
| Tree diff `v7.0.1..origin/develop` | 1195 files, +78,969 / -6,770; 382 under `implementation/`, 321 under `docs/`, 170 under `tests/`, 8 under `scripts/` (V, `git diff --shortstat` and `--numstat`) |
| Commit types in range (conventional prefix) | 136 `docs`, 27 `fix`, 20 `feat`, 20 `chore`, 16 `test`, 3 `ci` (V; v1 said 25 `fix`, 19 `feat` over a smaller range) |
| Structural facts | Still only three **added** installed files, `implementation/runtime/security/{git_executor,poc_audit_server,poc_scan}.py`; no file under `implementation/` deleted or renamed (V, `git diff --name-status v7.0.1 origin/develop -- implementation`). Since v1, no file under `implementation/` was added, deleted or renamed (V, same command from `5e07a6b`) |
| Last task covered | **T640** (merge `b9744bc`), T630 last in merge order (`ac63dbe`). **Not covered / still open:** T627 (`pending`, orchestrator, needs the user) and everything wave 3 |
| Method | Re-ran every gate and the C-1 measurement (§7, §3); read the ten review/ruling artifacts named above in full or in their verdict, finding and condition tables; read the diff of every file changed since `5e07a6b` under `implementation/` (non-projection), `scripts/`, `.gitlab-ci.yml`, `.gitlab/`, `CONTRIBUTING.md`, `README.md`, `AGENTS.md` (file list in V; text read for the adopter-facing ones: `install.sh` usage, `.mcp.json`, `servers.yaml` pins, the wiki migration section, `PREREQUISITES.md`, `publish-release.py`, `dry-run-publish-release.py`, `.gitlab-ci.yml` release jobs, `CONTRIBUTING.md` Releasing, the Release MR template, `_template.md`) |

### 1.2 What changed since v1: T619..T640 outcomes and merge commits

Merge = the merge commit on `origin/develop` that carries the work (first-parent history). "Rev." = review artifact and its verdict, as recorded in the ledger row and the artifact header (the verdict text of each artifact was read; the claims inside them are theirs unless marked V).

| Task | Outcome | Merge | Review / evidence |
|---|---|---|---|
| T619 | CI release job uses the single release document; no root `release-notes.md`; tag validation; `--end-of-options`; offline dry-run script | `3771781` | Security `CONDITIONAL_PASS` (5 LOW, 4 fixed; SEC-T619-05 token in argv tracked); Tech Lead `CONDITIONAL_PASS` (T625) |
| T620 | R-1 measured: jwt rule is linear (about 2 microseconds per byte, git 2.43.0/glibc/`LC_ALL=C`); no pattern change; 9 timing tests; contract v6 | `94bb3ff` | Security `PASS` (4 LOW, fixed) |
| T621 | Rulings for the remaining PoC/task-protocol observations (A1, B1, C1) | `4c5b43e` | `remaining-observations-ruling-v1.md` |
| T622 | Plan for re-evaluating and promoting `orchestrator`/`tech-lead`, golden realignment, baselines v21/v22 | `4c5b43e` | `promotion-and-golden-realignment-plan-v1.md` |
| T623 | Audit v1 | `4c5b43e` | `release-v8-audit-v1.md` |
| T624 | T621 rulings applied verbatim (6 fences, 5 files) | `5e49e37` | (I) ledger row; fences not re-diffed by me beyond the text quoted in §2.4 |
| T625 | Tech Lead `/code-review` of the T619 change: `CONDITIONAL_PASS` | `c0ea11d` | `code-review-t619-v1.md`, revised `-v2.md` (in `23d18c7`) |
| T626 | Independent QA check of the T625 artifact: round 1 FAIL, round 2 PASS (38 rows) | `23d18c7` | `code-review-check-t625-v1.md`, `-v2.md` (I: from ledger) |
| T627 | `/skillify` real run with the user plus template fix | **not merged** (`pending`) | active ledger |
| T628 | Golden realignment under grant G-1 items 1-10, 12; scorecard 34 cases / 28 pass | `edb2d5a` | (V) `scorecard.py --check` OK (§7) |
| T629 | Evaluator baseline v21 | `edb2d5a` | (V) `evaluator-hash-known-good-v21.json` matches the tree (§7) |
| T630 | `tech-lead` promoted to `stable`; registry regenerated | `ac63dbe` | (V) §7 maturity check: 79 components, 0 failing |
| T631 | Adopter documentation for `--projections-only`, the `--update` spares, `poc-security-audit` (audit C-7) | `5927157` | (V) grep, §2 C-7 |
| T632 | Ruling: release documents and tag/merge order | `30ef8ba` | `release-documents-ruling-v1.md` |
| T633 | Release-level Security Engineer audit: `CONDITIONAL_PASS`, 0 critical, 0 high, 3 medium, 12 low | `30ef8ba` | `security-review-release-v8-v1.md` |
| T634 | ADR-009 (accepted 2026-10-15) and a draft of the severity-scales reference | `30ef8ba`; acceptance in `23d18c7` | `ADR-009-...md`; `adr-008-status-and-severity-scales-v1.md` |
| T635 | T625 conditions C1-C3 and cheap items resolved (29 tests) | `e312a96` | Security `PASS` (4 LOW tracked) |
| T636 | SEC-001 fixed: installer and merge scripts refuse symlinked or escaping managed paths | `9fde23a` | Security `PASS` (7 LOW; L6, L7 accepted); (V) my reproduction, §2 C-6 |
| T637 | Research of every npx/uvx MCP package | `23d18c7` | `mcp-server-packages-v1.md` |
| T638 | SEC-002 fixed: four nonexistent entries replaced, all pins exact, `docker` and `postgresql` removed | `bfd4ba7`; root refresh 17 `49e7267` | Security `CONDITIONAL_PASS` (3 medium: M-1 root refresh met by `49e7267`, M-2 and M-3 fixed in the round; 8 LOW) |
| T639 | T632 amendments applied: release-document union, develop-first order, template and Release MR template rebuilt | `7fa60c1` | (V) text checked in §2 C-2, C-4 |
| T640 | Release body = the release document whole; commit list to `CHANGELOG.md` only, merges excluded | `b9744bc` | Security `PASS` (4 LOW tracked) |
| T641 | This addendum | (not merged) | — |

### 1.3 Inventory re-run: entries of v1 §2 that changed or were added

v1 §2 entries not named here are unchanged (V: no file under `implementation/knowledge/` they cite changed since `5e07a6b`, except those listed). Net changes:

| ID | Change | Breaking | Basis |
|---|---|---|---|
| **A-22 (new)** | **MCP server launchers replaced and pinned (T638).** `filesystem`: `npx -y @anthropic/mcp-filesystem` becomes `npx -y @modelcontextprotocol/server-filesystem@1.0.0 .`. `github`: `npx -y @github/mcp-github` becomes `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server@sha256:ffced0d7...97796` (token env var `GITHUB_PERSONAL_ACCESS_TOKEN`). `git`: `npx -y @modelcontextprotocol/mcp-git` becomes `uvx mcp-server-git@2026.10.10 --repository .`. `supabase`: `npx -y @supabase/mcp` becomes `npx -y @supabase/mcp-server-supabase@0.13.0 --read-only` (token env var `SUPABASE_ACCESS_TOKEN`). `docker` and `postgresql` entries removed. Every other `npx` entry pinned: `@zereight/mcp-gitlab@2.2.5`, `@playwright/mcp@0.0.83`, `mcp-fetch-server@1.1.2`, the two reference servers `@1.0.0`, `@brave/brave-search-mcp-server@2.1.4`, `toolradar-mcp@2.1.0`. New runtime prerequisites: `uv` (git server), Docker daemon (github server). Pin-bump policy in `servers.yaml`, `PREREQUISITES.md`, wiki. Evidence: `git diff 5e07a6b origin/develop -- implementation/.mcp.json` (read), `mcp-server-packages-v1.md`, `security-review-t638-...-v1.md`. | **yes** (what a server starts changes; two servers disappear; two new tools required; new env vars) | V |
| **A-23 (new)** | **Installer refuses symlinks at managed paths (T636).** Any symlink at a managed target path or at one of its parents (`.claude`, `docs`, `implementation`, `implementation/runtime`, `.vscode`, `.mcp.json`, `CLAUDE.md`, a task ledger, about 60 paths) is refused with exit 1 before anything is written, in every mode, even when the link points inside the target. Before: rsync/cp followed it. `--help` documents it and says not to run the installer as root into a directory others can write to. The three Python merge scripts refuse a symlinked destination. | **yes** for anyone who symlinks a managed path (for example `CLAUDE.md -> AGENTS.md`); no for others | V (usage text read; reproduction, §2 C-6) |
| **A-24 (new)** | **Release procedure and release job for maintainers (T639, T619, T640).** Order: `release/*` to `develop`, then to `main`, both merge commits without squash, then tag the release-branch tip; the direct-push back-merge is removed (`CONTRIBUTING.md` step 5-7, Release MR template, `release-manager`, `orchestrator` preflight, skill). The release document carries 11 sections, first line `# Release v<VERSION>` (`_template.md` rebuilt, eight platform values). CI `release` job: GitLab description = the release document byte for byte; commit list (`--no-merges`) only in `CHANGELOG.md`, which stays a job artifact. | no for adopters; **yes** for maintainers of the source repository (counted like A-10, A-21) | V |
| A-13 (extended) | The `${VAR}` placeholder list now also contains `GITHUB_PERSONAL_ACCESS_TOKEN` and `SUPABASE_ACCESS_TOKEN` (from A-22). | unchanged (unclear) | V |
| A-02 (note) | Scanner contract is now v6 (T620: R-1 stated as an accepted fail-closed residual). The only code change in `poc_scan.py` since v1 is a docstring (V, file list; diff not re-read in full). | unchanged | I |
| B-07 (changed) | Maturity: `tech-lead` is now `stable` (T630). **`orchestrator` is the only agent still `experimental`.** Counts from `check-maturity.py`: agents 27 stable / 1 experimental, commands 14 / 5, instructions 4 / 2, skills 7 / 19; 79 components, 0 failing (V, §7). | no (`maturity` is not projected) | V |
| B-06 (changed) | Golden suite: 34 cases, 28 pass, 6 `known_failing` (2 `tracked_defect`, 4 `capability_gap`), 0 regressions; evaluator baseline v21. | no | V |
| **B-10 (new)** | `scripts/dry-run-publish-release.py`: offline rehearsal of the release job (`--tag`, `--template-shaped`), no network, no tag, no repo writes. Maintainers only. | no | V (ran it, §7) |
| **C-17 (new fix)** | SEC-001: installer followed symlinks at managed paths and wrote or deleted outside the target (T636). | — | V |
| **C-18 (new fix)** | SEC-002: four launcher names did not exist on npm (since `v5.0.0`, V below), one under a scope owned by an unrelated individual (graded HIGH by the user); unpinned `npx -y` everywhere (T638). | — | V |
| **C-19 (new fix)** | Release job wrote a third root `release-notes.md`, embedded the whole document under an extra title, and listed merge commits under "Other" (T619, T640). | — | V |
| **C-20 (new fix)** | ADR-008's header contradicted itself (accepted, but "no ruling may cite it"): ADR-009 records that ADR-008 is accepted and the draft-era bullets have no force; ADR-008 itself is untouched. | — | V (ADR-009 read; ADR-008 header not re-read) |
| **C-21 (new fix)** | Release procedure documents contradicted each other and the drift gate; the back-merge could not be pushed to a protected branch (T632 ruling, T639). | — | V |
| §2.4 additions | T624 (PoC-track knowledge text, not breaking): `gitlab-management` gains a priority-label mapping `priority::critical`/`high` to `P0`, `medium` to `P1`, `low` to `P2` as an agreement rule; `technical-debt-tracking` now scans every text file under the PoC root and skips `.git`, `node_modules` and the registers (`POC-DEBT-SCORECARD.md`, `TECHNICAL-DEBT.md`, `debt-ledger-v*.md`); `poc-evaluation` states that `/evaluate-poc` severities come from the debt ledger or the scorecard; `technical-debt-narrator` exempts its two unversioned deliverables from the `-vN` rule; `orchestrator` Implementation-gate timing wording. Docs (T631, T638): adopter documentation of the new surface. | no | V (diff read for the first four; the orchestrator wording is I) |

### 1.4 Count summary for the `RELEASE VERDICT` fields (basis only; the release manager decides the counting rule, `release-documents-ruling-v1.md` RD-5)

| Measure | v1 | v2 |
|---|---|---|
| Entries in §2.1 | 21 | **24** (A-22, A-23, A-24 added) |
| Breaking = `yes` | 14 | **17** (A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08, A-10, A-12, A-14, A-16, A-19, A-21 and A-22, A-23, A-24) |
| Breaking = `unclear` | 4 | 4 (A-13, A-15, A-18, A-20) |
| Breaking = `no` | 3 | 3 (A-09, A-11, A-17) |
| Breaking-candidate entries (`yes` + `unclear`) | 18 | **21** |
| Of the candidates: V / I | 17 / 1 | **20 / 1** (A-04 stays I) |
| Of the `yes`: adopter-affecting only (excluding the maintainer-only A-10, A-21, A-24) | 12 | 14 |
| Features / fixes | 9 / 16 | **10 / 21** (B-10; C-17..C-21) |

---

## 2. Dispositions of the open concerns C-1..C-9 of v1

Disposition values: **closed** (evidence given), **open** (owner and closing step), **moved to release preparation** (wave 3; needs the user's approval for outward steps per `plan-121`).

| Concern | Disposition | One-line reason |
|---|---|---|
| C-1 stale version claims | **moved to release preparation**, with **open decision D-1** (new: golden-fixture hits) | Re-measured; the list grew from 11 to 18 findings; 7 of them sit in a protected path |
| C-2 three release-note documents disagree | **closed** for the contradiction; the document itself and two decisions **moved to release preparation** | T632 ruling + T639 applied (V) |
| C-3 CI release job | **closed** in code; first real use **moved to release preparation** | T619, T635, T640 (V: tests, dry runs) |
| C-4 tag / back-merge ordering vs drift gate | **closed** in documents; the tag step **moved to release preparation** | New order passes the gate (V, scratch repo) |
| C-5 scripts and tests on a major bump | **closed** | Re-grepped; two cosmetic residuals unchanged |
| C-6 no Security Engineer review of the installer | **closed** with two open items | T633 + T636 + T638; SEC-003 flags unverified; no automated A06 |
| C-7 adopter documents silent on the new surface | **closed** (new surface), residual stale facts recorded | T631, T638 (V grep) |
| C-8 internal inconsistencies | **closed** except the severity-scales reference page (open, not release-blocking); the conflict disclosure is in §8 | ADR-009; T624 |
| C-9 addendum trigger | **closed** by this file | Produced after T619-T640, before the gates |

### C-1. Stale version claims (Gate G0 and the `release-docs-gate` on the tag)

**Disposition: moved to release preparation; D-1 open.**

Method (V): `git archive origin/develop -- . ':(exclude)tests/golden/held-out'` into the scratchpad (`git archive --exclude` is not supported by this git, so the pathspec form was used), changed only `README.md:14` from `Latest release: v7.0.1` to `Latest release: v8.0.0`, ran `python3 -I scripts/check-version-consistency.py` in the copy: **FAIL, 18 findings at 14 locations** (some lines are reported twice).

The exact list (V, from that run; line numbers on `ac63dbe`):

| # | File : line | Content class | Action at the bump |
|---|---|---|---|
| 1 | `README.md:14` | the canonical marker `Latest release: v7.0.1` | bump (also required by `verify-release-docs.py`) |
| 2 | `docs/wiki/README.md:6` | marker | bump (required by `verify-release-docs.py`) |
| 3 | `docs/wiki/home.md:5` | marker | bump (required by `verify-release-docs.py`) |
| 4 | `implementation/README.md:6` | marker `Latest release: v7.0.1` | bump (flagged by the check; not required by the gate) |
| 5 | `README.md:201` | link to `docs/releases/v7.0.1.md` (reported twice) | point at `v8.0.0.md` |
| 6 | `docs/wiki/implementation-guide.md:5` | "current release: v7.0.1" | bump |
| 7 | `docs/wiki/implementation-guide.md:41` | link to `docs/releases/v7.0.1.md` (reported twice) | point at `v8.0.0.md` |
| 8 | `implementation/README.md:4` | `(**v7.0.1**)` | bump |
| 9 | `implementation/README.md:56` | "Per-release notes" link (reported twice) | point at `v8.0.0.md` |
| 10 | `tests/golden/open/prepare-release-real-verdict-missing/brief.md:9, :21, :24, :54` | history text naming the v7.0.1 fixture | **protected path (see D-1)** |
| 11 | `tests/golden/open/prepare-release-real-verdict-missing/fixture/docs/releases/v7.0.1.md:1, :3` | frozen byte-identical copy of the v7.0.1 release document (`# v7.0.1`, `Latest release: v7.0.1`) | **protected path (see D-1)** |

Rows 1-9 are the same files as v1 (line numbers moved: `README.md:131` is now `:201`, `docs/wiki/implementation-guide.md:33` is now `:41`, `implementation/README.md:31` is now `:56` after T631). Row 10 and 11 are **new since v1**: T628 retargeted the case to a copy of `docs/releases/v7.0.1.md` (V: `git log` of the case directory shows `d675149`). `docs/wiki/README.md:36` and `implementation/docs/wiki/*.md` carry only the placeholder `vX.Y.Z`. No `package.json`, `VERSION` or version manifest is tracked (V, `git ls-files`); `deployment-config.json` has only a model version.

After rows 1-9 are fixed in the scratch copy, and the `prepare-release-real-verdict-missing` case directory is moved aside, `python3 scripts/verify-release-docs.py --tag v8.0.0` prints `all documentation checks passed` and `verified marker 'Latest release: v8.0.0'` (V, with a release document made from `docs/releases/_template.md` by replacing `vX.Y.Z`; the document itself is a placeholder, not the real notes). With the case directory in place the same command **fails**, because `verify-release-docs.py` runs `check-version-consistency.py` itself (V). So rows 10-11 block **both** `release-docs-gate` on the tag **and** Gate G0.

**D-1 (decision for the user, not taken here; blocker, type `technical`, severity `major`, solvable before the tag).** The frozen fixture and the brief legitimately name v7.0.1. Options:
1. Add `tests/golden/` to `EXCLUDED_PREFIXES` in `scripts/check-version-consistency.py` (not a protected path; `docs/releases/`, `docs/checkpoints/`, `docs/artifacts/` are already excluded as historical records; a test in `tests/functional/test_check_version_consistency.py` would pin it). It narrows what the check scans, so ADR-007 section 5 ("no check is weakened") asks for a recorded decision. **Recommended**, because fixtures are frozen evidence by design and the golden suite is protected from edits.
2. Edit the protected fixture and brief: needs an exception under `protected-paths-v1.md` section 5 and a new baseline (v22), and the promotion plan places that step (G-2, the retarget to `docs/releases/v8.0.0.md`) after the tag (S8/S9). It would also be circular: the tag gate needs the edit, the edit needs the release document.
3. Reword nothing and accept a red G0: not possible, the `release` job `needs` the gate.

Other bump-time items (V): `README.md:263` and `docs/wiki/README.md:36` are format descriptions with `vX.Y.Z`; `scripts/dry-run-publish-release.py` and `tests/functional/test_publish_release.py` default to the **v7.0.1** document, which stays in `docs/releases/` (the test would fail if that file were removed); `scripts/scorecard.py` `GOLDEN_VERSION_LABEL = "v6.12.0"` and `docs/benchmarks/scorecard-v6.12.0.*` carry an old-looking label that the check does not flag (cosmetic, protected script).

### C-2. Release document versus the three documents that did not match

**Disposition: closed for the contradiction; v8.0.0 document, counting rule and rollback wording moved to release preparation.**

Evidence (V):
- `docs/releases/_template.md` now has the union: `# Release vX.Y.Z` (line 1), `## Summary`, `## Install` with the `Latest release:` marker, `## Highlights`, `## Breaking changes`, `## Migration Guide`, `## Changelog` (`### Features`, `### Fixes`, `### Internal`), `## Known Issues`, `## Gate Verdicts`, `## RELEASE VERDICT`, `## Rollback Plan` (11 sections, per `release-documents-ruling-v1.md` section 4.2).
- The orchestrator preflight (`orchestrator.md:135`) now lists `Latest release`, `## Install`, `## Highlights`, `## RELEASE VERDICT` and the `release-workflow` section 4 sections.
- A document made from the template passes `verify-release-docs.py --tag v8.0.0` once the markers are bumped and rows 10-11 of C-1 do not interfere (previous section).
- `python3 scripts/verify-release-docs.py --tag v7.0.1` and `--tag v7.0.0` exit 1 (missing `## RELEASE VERDICT`; v7.0.0 also lacks markers). This is history: the gate runs only for the tag being pushed.

Open for release preparation: (a) write `docs/releases/v8.0.0.md` from §3-§5 of this file; (b) the counting rule for "Features included", "Fixes included", "Breaking changes" (RD-5: each equals the entries listed under its heading; whether `unclear` entries are listed as breaking is the release manager's call; basis in §1.4); (c) `release-manager.md:227` asks for the rollback of a MAJOR release to be tested: the rollback paragraph in §3 is **untested**, so either test it or state "not tested" in `## Rollback Plan`; (d) use code spans or absolute URLs for repository files in the document, because the gate link-checks relative links (ruling section 4.3 rule 5; the ruling marks the GitLab rendering of a relative link as not tested).

### C-3. CI release job

**Disposition: closed in code and tests; first run on a real tag moved to release preparation.**

Evidence (V): `python3 -m unittest tests.functional.test_publish_release`: `Ran 37 tests ... OK`. `python3 scripts/dry-run-publish-release.py`: `DRY RUN OK`, `root release-notes.md written: False`, `description equals the release document byte-for-byte: True`, the files in the temp root are `CHANGELOG.md` and `docs/releases/v7.0.1.md`. `--template-shaped`: `DRY RUN OK`. `.gitlab-ci.yml` `release` job: `artifacts.paths` is `CHANGELOG.md` only (read, lines 193-208). `publish-release.py` `update_changelog` keeps `###` groups and drops H1/H2 (read). The default dry run after the real v8.0.0 document exists is **still to be repeated** (T635 note).

Open (moved to release preparation): (1) T635 recommends one run of the release job's git commands on the real CI image (`python:3.12-alpine`, unpinned `apk add git`) or on a `-rc` tag, to confirm `git log --no-merges --pretty=%s --end-of-options <range> --`; the git version in that image is **(unverified)**. A `-rc` tag matches the CI tag rule and would publish a GitLab Release, so it is the user's call. (2) GitLab's current description size limit is **(unverified)**; with the document alone as the body, the size is the document's (the v7.0.1 document is 3,716 characters, V from the dry run).
New small defect (V, dry-run output; pre-existing logic in `update_changelog`): the new section is inserted directly under the `# Changelog` line, so the file's introductory paragraph ("All notable changes ...") ends up **below** the newest entry and moves down with each release. Cosmetic, job artifact only; tracked in §6 as debt.

### C-4. Tag and merge ordering versus the main-develop drift gate

**Disposition: closed in documents; the tag step moved to release preparation.**

Evidence (V): the order `develop` MR, `main` MR (both merge commits, no squash), then tag the release-branch tip appears consistently in `CONTRIBUTING.md` steps 5-7 and the hotfix steps (line 307-308), `.gitlab/merge_request_templates/Release.md`, `release-manager.md:30-31`, `release-workflow` hotfix step, and `orchestrator.md:141` ("tag commit is already in origin/develop and in origin/main"). A grep for `back-merge` outside historical records finds only `CONTRIBUTING.md:196` ("There is no separate back-merge"). Gate behaviour, tested in a scratch git repository with the real `scripts/check-main-develop-drift.py`: both branches carrying `Latest release: v8.0.0` with the tag on the release tip, `main-develop-drift: PASS (main=v8.0.0 develop=v8.0.0, releases_behind=0)`; the old order (`main` new, `develop` old): `main marker (v8.0.0) is AHEAD of develop marker (v7.0.1) -- invariant violation`, exit 1.

Residuals (all release preparation): (a) the step-7 check that `git rev-parse origin/main^2` is the release tip needs a **non-squash** merge of the `main` MR; if GitLab squashes, CONTRIBUTING's "ancestry restore" recovery applies (ruling section 5.3; commands **(unverified)**, never run); (b) whether `scripts/verify-main-sync-merge.py` can be run against the `develop` MR is **(unverified)**; (c) between the `develop` merge and the tag, the informational `main-develop-drift-check` on `develop` will warn (`allow_failure: true`); (d) the previous tag `v7.0.1` is only on `main`, so the commit range for v8.0.0 keeps the T512/T513 quirk of v1 section 1; the generated `CHANGELOG.md` artifact for this one release may list commits already in v7.0.1 (not measured).

### C-5. Scripts and tests on a major bump

**Disposition: closed.** Re-grepped `scripts/`, `implementation/scripts/`, `Makefile`, `.gitlab-ci.yml`, `tests/` for hard-coded `6.x`/`7.x` (V): the only hits are the dry-run default tag `v7.0.1` and tests that read `docs/releases/v7.0.1.md`, the `v6.0.5` installer contract comment, docstrings, and `GOLDEN_VERSION_LABEL`. None asserts the current README marker. The sprint-status fixture mention of `verify-release-docs.py --tag v7.0.1` that v1 noted is not in the findings of the bumped run (V); the new hits in C-1 rows 10-11 show that the scan does reach golden markdown.

### C-6. Security review of the installer and the PoC scanner stack

**Disposition: closed, with two open items for release preparation.**

Evidence: T633 (`security-review-release-v8-v1.md`, `CONDITIONAL_PASS`: 0 critical, 0 high, 3 medium, 12 low) covered `install.sh`, the three merge scripts, `publish-release.py`, the dry run, the release job, the three `runtime/security` modules and shipped MCP configs (static, no shell).
- SEC-001 (symlinks): **fixed (T636)**. My own reproduction on `ac63dbe` (V): scratch target whose `.claude` links to a directory holding a canary file; `scripts/install.sh --target <t> --platform claude-code --update` exits 1 with "refusing to write through a symlink", "Nothing was written", the canary intact and the target empty apart from the link.
- SEC-002 (MCP packages): **fixed (T638)**. V: all four nonexistent names are gone from every tracked file outside records (`git ls-files | xargs grep`; the only hits are the wiki migration note, a benchmark narrative, and the pin test `tests/functional/test_mcp_package_pins.py`); the root `.mcp.json` carries the new pins (`@modelcontextprotocol/server-filesystem@1.0.0`, `ghcr.io/...@sha256:ffced0d7...`, `uvx mcp-server-git@2026.10.10`, `@supabase/mcp-server-supabase@0.13.0 --read-only`); T638 condition M-1 (root refresh before the tag) is met by `49e7267`; `python3 -m unittest tests.functional.test_root_install_parity` OK (7 tests, drift baseline `{"drift": 0}`). The user regraded the `@anthropic/mcp-filesystem` entry to HIGH (T637 section 3.1). **That name is present in every local tag from `v5.0.0` through `v7.0.1`** (V, `git grep` over `git tag`), so every published install since `v5.0.0` that enabled the extended profile can resolve whatever the `anthropic` npm account publishes. The fix reaches adopters only when they `--update`; see Migration M-9 (out-of-band note).
- SEC-003 (token in argv, `WIKI_TOKEN` also used for releases): LOW **only on the user's statement** that `WIKI_TOKEN` is Protected and Masked and the `v*` tag pattern is protected; the orchestrator had not verified those GitLab settings (T633 record). **Open, owner: user or release manager, before the tag:** confirm both settings in GitLab (I cannot: no API access). If not set, SEC-003 returns to MEDIUM and blocks (`validation-gates` Verdict Rules).
- No automated A06 result exists. T633 and T640 record that the Security Engineer's `grep_content` failed on every call and `run_pip_audit` failed to run; I could not test that tool from here. **Open, owner: devops-engineer or security-engineer, before the Release gate:** run `run_npm_audit`/`run_pip_audit` (or the equivalent) once on the pinned set, or record that none ran. I did not run an audit tool (`pip-audit`/`npm audit` availability **(unverified)**).
- Whether the per-MR Tech Lead OWASP run (T589) happened for T550-T559 stays **(unverified)**; the release-level audit supersedes the need for it.

### C-7. Adopter documents

**Disposition: closed for the new surface; residual stale facts recorded.** V (grep): `--projections-only` appears in `README.md`, `docs/wiki/{quick-start,implementation-guide,mcp-servers}.md`, `implementation/{README,SECURITY}.md`; `poc-security-audit` and the allow rule `mcp__poc-security-audit__*` in README, wiki, `implementation/README.md`, `implementation/SECURITY.md`; `git` 2.40 in README, wiki, `implementation/README.md`; `mcp==2.2.0` in README and `mcp-servers.md`; the SEC-002 migration note in `docs/wiki/mcp-servers.md` ("Migrating an existing install from v7.x") and `implementation/PREREQUISITES.md` ("Upgrading from v7.x", pin-bump policy). Residual wrong or stale facts that T631 reported and that **still exist** (V grep), none blocking: component counts (`docs/wiki/home.md:17` and `agents-overview.md:3` say 27 agents, the registry has 28; `README.md:286` and `cline-setup.md:33` say 18 commands, `architecture.md:9` says 16, the registry has 19); `docs/wiki/mcp-servers.md:193` says two servers use `transport: remote`, `servers.yaml` has four; the manual-copy tables (`quick-start.md:43-52`, `implementation/README.md:48-53`) omit `implementation/runtime/`. The `GITHUB_TOKEN`/`SUPABASE_ACCESS_TOKEN` env-table problem T631 reported was fixed by T638 (V, `mcp-servers.md:51`). These belong in the release preparation task list as documentation fixes, or in Known issues.

### C-8. Internal inconsistencies

**Disposition: closed for the three items below; the scales reference stays open; disclosure in §8.**
- ADR-008 Status block: **closed by ADR-009** (accepted 2026-10-15). ADR-008 remains byte-unchanged and still shows the draft-era bullets; ADR-009 says line 5 governs. The release document should cite ADR-009 when it mentions ADR-008 (V: ADR-009 read in full).
- `plan-120` header (`007e8fa`) and its O-8 wording: the plan is immutable; O-8 was ruled by T621 and applied by T624 as the `gitlab-management` mapping (V, diff). Closed.
- Coexisting severity and grade scales: T634 produced a **draft** reference (seven scales, 11 pair relations) with the proposed home `docs/wiki/severity-and-grade-scales.md`; that file **does not exist** on `origin/develop` (V, `ls`). **Open, owner: user decision then technical-writer (T-new); not release-blocking.** The Migration table M-6 still serves as the interim reference.
- The committed `.claude/settings.json` has no `mcp__` rule (V: `git show origin/develop:.claude/settings.json | grep -c mcp__` = 0); the user's local file was not read.
- Release sign-off conflict (Tech Lead component promoted in this release): recorded in §8.

### C-9. Addendum trigger

**Disposition: closed.** This file is produced after T619-T640 (except T627) and before the gates. A root refresh is not expected to be needed again for the audited state (V: root parity test OK, drift baseline 0); T627, the release preparation and the user's D-1 choice may add changes; if any touch `implementation/`, run the parity test and write `release-v8-audit-v3.md` or record the delta in the release checkpoint.

---

## 3. Migration section for `docs/releases/v8.0.0.md` (draft text, v2; supersedes v1 §3; the release manager owns the final wording)

> Use the heading `## Migration Guide` (`release-documents-ruling-v1.md` RD-5; skill `release-workflow` section 4). Repository files are written as code spans or absolute URLs, because the release gate link-checks relative links.

**Migration from v7.0.1 to v8.0.0**

v8.0.0 changes what some agents may do, adds one MCP server, replaces and pins the extended MCP servers, tightens gate and PoC rules, makes the installer refuse symlinked managed paths, and renames several file conventions. Nothing already in your project is renamed or deleted by the installer except the platform trees it owns. Do the steps in this order.

**M-1. Update the installer and run `--update` once per project.**
```bash
git -C <emage.code clone> pull        # or check out the v8.0.0 tag
scripts/install.sh --target <your-project> --platform <name>|all --update
```
`<name>` is one of `cursor`, `github`, `gemini`, `opencode`, `pi`, `claude-code`, `cline`.
- `--update` replaces each platform tree it owns (`.claude/`, `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/`, `.clinerules/`) and re-renders `AGENTS.md` and `CLAUDE.md`. Hand-written files inside those trees are deleted; put project-specific content in `docs/`.
- It no longer touches `.claude/settings.json`, `.claude/settings.local.json`, or `.github/{workflows, ISSUE_TEMPLATE, PULL_REQUEST_TEMPLATE*, CODEOWNERS, dependabot.y*ml, FUNDING.yml, copilot-instructions.md}`. If an earlier `--update` removed any of them, restore them from version control.
- **The installer now refuses to write through a symlink.** If any managed path, or a parent of one (`.claude`, `docs`, `implementation`, `implementation/runtime`, `.vscode`, `.mcp.json`, `CLAUDE.md`, a task ledger, and others), is a symbolic link, even one that points inside your project, the run stops with exit 1 before anything is written. Replace the link with a real file or directory, or point the installer at the real path. Do not run the installer as root into a directory other users can write to.
- MCP configs (`.mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json`) are merged: generated values win, your extra servers are kept. See M-8 for the changed entries.
- Both task ledgers are rewritten: your prose is kept, rows that are not `T<NNN>` are dropped with a warning, line endings become LF.
- New runtime files appear under `implementation/runtime/security/` (three) and `implementation/runtime/handoff/` (new directory).
- Maintainers of the emage.code checkout: `--update` and any `--target` inside the repository are refused; use `scripts/install.sh --target . --platform all --projections-only` (refreshes the platform trees, MCP configs, `AGENTS.md` and `CLAUDE.md`; never touches `docs/` or `implementation/`).

**M-2. Client settings (the installer never writes them).**
- Claude Code: add to `.claude/settings.json` under `permissions.allow`: `"mcp__poc-security-audit__*"`. If you use `@security-engineer` or `@context-retriever`, the same pattern applies to `"mcp__security-audit__*"` and `"mcp__context-retriever__*"`. On first start approve the project-scoped servers when Claude Code prompts (it prompts again for the changed entries of M-8).
- Claude Code `.mcp.json` uses `${VAR}` (not `${env:VAR}`). Export the variables for the servers you use in the environment that starts the client: `HINDSIGHT_MCP_URL`, `CWSO_MCP_URL`, `CWSO_BEARER_TOKEN`, `CWSO_ORIGIN`, `GITLAB_PERSONAL_ACCESS_TOKEN`, `GITLAB_API_URL`, `BRAVE_API_KEY`, `TOOLRADAR_API_KEY`, and, new in v8.0.0, `GITHUB_PERSONAL_ACCESS_TOKEN` (`github`) and `SUPABASE_ACCESS_TOKEN` (`supabase`). An unset variable is reported by `claude mcp list` and the literal `${VAR}` text is used; an unset token stops only that server.
- Other platforms: grant the platform's equivalent permission for `poc-security-audit` if it asks for one. **GitHub Copilot:** the extended servers are not emitted to `.vscode/mcp.json`, so the PoC security scan cannot run there (Known issue K-3).

**M-3. Dependencies.**
- Python package `mcp==2.2.0`: `python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && pip install -r implementation/runtime/security/requirements-mcp-server.txt` (the installer prints this). The MCP client must start `python3` from that environment, from the project root (the server runs with `--allowed-root .`).
- `git >= 2.40` on `PATH` for `poc-security-audit` (older git: every call fails closed as `git_failed`). POSIX host assumed (paths such as `/dev/null`, `/usr/bin`; Windows not verified).
- For the extended MCP servers (M-8): Node.js with `npx` for the `npx` servers, `uv` (`uvx`) for `git`, and a running Docker daemon that can pull from `ghcr.io` for `github`.
- `@context-retriever` still needs its one-time index build (unchanged since v7.0.1).

**M-4. Project files `--update` will not refresh.** `docs/tasks/validate-tasks.py`, `docs/tasks/_template.md` and `docs/plans/_template.md` are copied only when missing. To adopt the new validator (checks C11 `**Affects:**` on P0/P1 briefs, C12 existing `Depends on` IDs, C13 no self-dependency, C14 no cycles), the `Affects` field and the `plan-<ID>` plan template, delete the old copies and re-run `--update`, or copy them from `implementation/docs/`.

**M-5. Renamed conventions.** Existing files are not renamed; new files follow the new forms.

| Item | Before | Now |
|---|---|---|
| Plan | `<slug>-plan.md`, `feature-<slug>.md`, `plan-<project-slug>.md`, `poc-<slug>.md`, `plan-vN.md` | `docs/plans/plan-<ID>.md`; `<ID>` = three-digit number, hyphen, slug (lowercase letters, digits, hyphens, dots), next unused number; a revision is a new plan |
| Checkpoint | `checkpoint-feature-<slug>.md`, `checkpoint-<phase>.md`, `checkpoint-poc-<gate>.md`, `checkpoint-<N>.md`, `checkpoint-release-v<version>.md` | `checkpoint-<SEQ>-<phase>.md`; release: `checkpoint-<SEQ>-release-v<version>.md` |
| Decision record | `decision-vN.md`, PoC debt in `docs/decisions/poc-debt-<slug>.md` | `ADR-<NNN>-<slug>.md`; PoC debt scorecard `POC-DEBT-SCORECARD.md` in the PoC root |
| Versioned artifact | `<name>-v<major>.<minor>.md` | `<name>-v<N>.md` |
| Release notes | `docs/artifacts/release-notes-v<VERSION>.md` (skill text) | `docs/releases/v<VERSION>.md`, one document, first line `# Release v<VERSION>`, with a `## RELEASE VERDICT` section |
| `/batch` branch | `batch/<slug>/<unit>-<desc>` | `agent/<agent-name>/<task-id>`; manifest in the plan document, units are `T<NNN>` ledger rows |
| Skill file (`/skillify`) | `.github/skills/<name>/SKILL.md`, `## Trigger`/`## Steps` | authoring checkout: `implementation/knowledge/skills/<name>/SKILL.md`; installed target: every installed `<platform>/skills/<name>/SKILL.md`; `## When to Use`/`## Inputs`/`## Procedure`/`## Success Criteria` |

**M-6. Severity, verdict and status vocabulary.**

| Scale | Before | Now |
|---|---|---|
| Review / gate verdict (Tech Lead, code-review) | `Approved \| Changes Requested \| Needs Discussion` | `PASS \| CONDITIONAL_PASS \| FAIL` |
| `CONDITIONAL_PASS` | merge blocked until conditions resolved (Tech Lead) | merge permitted with tracked conditions; closed before the next gate (production), carried to the next release cycle at the Release gate, recorded as debt (PoC). Never for a security finding graded `SECURITY:CRITICAL`/`HIGH`, an Immutable Constraint breach, or an omitted/weakened required control |
| Security | `/security-audit`: FAIL only on CRITICAL | FAIL on CRITICAL or HIGH, constraint breach, omitted/weakened required control; MEDIUM needs a remediation plan before merge and blocks a release until fixed |
| Blocker severity | `critical \| high \| medium \| low` | `critical \| major \| minor` (`AGENTS.md` Blocker Protocol) |
| PoC debt severity / effort | `critical/high/medium/low`; `XS..XL` | `critical/medium/low`; `S/M/L` |
| PoC verdict | `Validated \| Invalidated \| Inconclusive` | `Validated \| Invalidated` (weak or untested evidence is `Invalidated` with `Evidence strength: weak`); progress report `verdict=in_progress` only at a milestone |
| Task status values in skill examples | `in-progress`, `review` | `in_progress`, `in_review` (as `AGENTS.md`) |
| Task fields in skill examples | `Assignee`, `BlockedBy`/`Blocks`, `high/medium/low`, `must/should/could` | `Owner`, `Depends on` (blocks are derived), `P0/P1/P2` |
| GitLab `priority::` label to ledger priority | no mapping in the skill | `priority::critical` and `high` agree with `P0`, `medium` with `P1`, `low` with `P2` (`gitlab-management`); the mapping does not reverse |

`/bug-report` still uses its own four-level bug severity and maps it to `P0/P1/P2`.

**M-7. Behaviour changes to brief your team on.**
- The orchestrator opens a branch and a merge request for every change, docs and ledger edits included.
- Only orchestrators write `active-tasks.md`; the Scrum Master and skills propose rows.
- `/consolidate-memory` writes to project-owned `docs/` files, never to `AGENTS.md`/`CLAUDE.md`/platform folders, and keeps a memory entry until the write is re-read.
- The PoC security reviewer blocks the PoC on critical/high findings, exposed secrets, constraint breaches and omitted controls; it cannot be waived or recorded as debt. Placeholder flags are created only by the user.
- The PoC debt scan covers every text file under the PoC root (skipping `.git`, `node_modules` and the debt registers).
- Handoff JSON: `constraints.writablePaths` must list at least one path; entries must be non-empty strings; at most 128 per list.
- Command authors in the source repository: every command needs `audience: authoring | target | both`.
- `tech-lead` is now maturity `stable`; `orchestrator` is still `experimental`. Maturity is not projected into installed files, so installed agents are unchanged by this.

**M-8. MCP server entries changed (audit finding SEC-002).** The extended profile of v7.x launched four packages that do not exist on npm and left every `npx` server unpinned. v8.0.0 changes this; after `--update`:

| Server | v7.x launcher | v8.0.0 launcher | You need |
|---|---|---|---|
| `filesystem` | `npx -y @anthropic/mcp-filesystem` (nonexistent; the `anthropic` npm account is not Anthropic PBC) | `npx -y @modelcontextprotocol/server-filesystem@1.0.0 .` | start the assistant from the project root; the server can read every file under it, including `.env*` and `.git` |
| `git` | `npx -y @modelcontextprotocol/mcp-git` (nonexistent) | `uvx mcp-server-git@2026.10.10 --repository .` | `uv`; exposes write tools |
| `github` | `npx -y @github/mcp-github` (nonexistent) | `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server@sha256:ffced0d7...` (pinned by digest) | Docker; `GITHUB_PERSONAL_ACCESS_TOKEN` in the environment |
| `supabase` | `npx -y @supabase/mcp` (nonexistent) | `npx -y @supabase/mcp-server-supabase@0.13.0 --read-only` | `SUPABASE_ACCESS_TOKEN` in the environment |
| `docker`, `postgresql` | `npx -y docker-mcp`, `npx -y postgres-mcp` | **removed** | nothing; see below |
| every other `npx` server | unpinned (`@playwright/mcp@latest` for one) | exact versions: `@zereight/mcp-gitlab@2.2.5`, `@playwright/mcp@0.0.83`, `mcp-fetch-server@1.1.2`, `@modelcontextprotocol/server-memory@1.0.0`, `@modelcontextprotocol/server-sequential-thinking@1.0.0`, `@brave/brave-search-mcp-server@2.1.4`, `toolradar-mcp@2.1.0` | nothing |

- `filesystem`, `git`, `github` and `supabase` are overwritten in place; a key you added inside one of those entries is kept. Your own entries with other names are kept.
- `docker` and `postgresql` are removed only if the installed file's `<file>.provenance.json` sidecar lists them. If the install has no sidecar, or the sidecar no longer lists them, remove both server objects from every installed MCP config by hand (Cline's real configuration is global), or run once per file: `python3 scripts/merge-mcp-json.py --source <generated file> --dest <your file> --force-prune-keys docker,postgresql`. `install.sh` does not pass this option. An entry of your own named `docker` or `postgresql` is removed as well when the old sidecar lists those names; re-add it under another name.
- Pins are exact and are bumped by the maintainers at every release and at least monthly (`servers.yaml`, `implementation/PREREQUISITES.md`); do not replace a pin with `@latest` or a range.

**M-9. Do this now if you run a v7.x or older install and have not updated yet (out-of-band note).** Every release from `v5.0.0` through `v7.0.1` ships a `filesystem` server entry that runs `npx -y @anthropic/mcp-filesystem`. That package does not exist on npm today. The `anthropic` scope belongs to an unrelated individual account, so that account could publish a package of that name at any time, and the next launch of your assistant would run it with access to your files. You do not need to wait for v8.0.0: remove the `filesystem` server object from `.mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json` and `.cline/mcp.json` (and Cline's global MCP file), or replace it with `@modelcontextprotocol/server-filesystem@1.0.0 <dir>`. The other three nonexistent names (`@github/mcp-github`, `@modelcontextprotocol/mcp-git`, `@supabase/mcp`) are under vendor organisation scopes that only the vendor can publish to; replace or remove them as well. Release channel for this note (advisory in the repository, release text of v8.0.0, pinned wiki page) is the release manager's and the user's decision **(open)**.

**Rollback (suggested; not verified by running it).** Check out the `v7.0.1` tag of the installer and run `--update` on the project. The files added by v8 under `implementation/runtime/security/` and `implementation/runtime/handoff/`, and any allow rule you added, stay behind and are harmless; remove them by hand if wanted. Notes: (a) v7.0.1's `--update` deletes `.claude/settings.json` and `.github/workflows/`, so commit those first; (b) it merges the v7.0.1 MCP entries back in, which restores the four nonexistent launchers and the unpinned servers (I: from the merge rule "generated values win"), so remove the `filesystem` entry again after a rollback (M-9); (c) a rollback does not undo a symlink you replaced for M-1.

**For maintainers of the source repository (release procedure, new in v8.0.0).** Cut a release with `release/vX.Y.Z` from `develop`: bump the version markers, write `docs/releases/vX.Y.Z.md` (11 sections, first line `# Release vX.Y.Z`), run `python3 scripts/verify-release-docs.py --tag vX.Y.Z`; open the MR to `develop` and the MR to `main`; merge `develop` first, then `main`, both as merge commits without squash; tag the release-branch tip (it is in both branches); the tag push runs `release-docs-gate`, `main-develop-drift-gate` and `release`. There is no back-merge. The `release` job publishes the release document as the GitLab Release description and regenerates `CHANGELOG.md` as a job artifact (commit subjects without merge commits). Rehearse the job offline with `python3 scripts/dry-run-publish-release.py [--template-shaped]`.

---

## 4. Known issues (draft list, v2, for `docs/releases/v8.0.0.md`; supersedes v1 §4)

| ID | Issue | Basis |
|---|---|---|
| K-1 | `orchestrator` is still `experimental` (agents 27 stable / 1 experimental); 5 of 19 commands, 19 of 26 skills and 2 of 6 instructions are `experimental`. Its promotion is staged: after the v8.0.0 notes exist, with a separate baseline v22 that needs its own user approval, and a real `/skillify` run (T627, pending). The release is cut by components of which `orchestrator` is still experimental. | V (`check-maturity.py`, registry; plan sections 6.4, 13) |
| K-2 | Golden suite: 34 cases, 28 pass, 6 `known_failing` (2 `tracked_defect`, 4 `capability_gap`), 0 regressions (`scorecard-v6.12.0.md`, generated 2026-10-15T05:39:15Z; the file name still says `v6.12.0`). Open `known_failing` cases: `security-audit-critical-not-fail`, `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap` (all `capability_gap`), `prepare-release-real-verdict-missing` (`tracked_defect`; exits after G-2/baseline v22), `skillify-skill-file-template-drift` (`tracked_defect`; exits with the T627 template fix). One more `capability_gap` case sits in the held-out set (counts only, from the scorecard). | V (`case.yaml`, scorecard counts) |
| K-3 | GitHub Copilot: no `security-audit` / `poc-security-audit` server in `.vscode/mcp.json`; the PoC security scan cannot complete there and the agent's rule makes that a `FAIL`. | I (A-04) |
| K-4 | `poc-security-audit` documented limits: `history` uses `git log -G` (merge commits not diffed, L-4); a range over `max_refs` commits is flagged `truncated` although covered (L-5); a `.git` file may point outside the allowed root (L-6); sibling projects under `--allowed-root` are reachable (R-6); a clean result means "no match for the fixed rule set only"; documented blind spots for short or unusual credential values. **R-1 (jwt rule on aperiodic `eyJ`-dense input) is measured and accepted**: linear, about 2 microseconds per byte on git 2.43.0/glibc under `LC_ALL=C`, reaching the 60 s deadline at about 30 MB for one file (extrapolated; history and stashes multiply it); it fails closed (`timeout`, `complete: false`); other locales and regex libraries were not measured. T611-2/T611-3 are closed (T612: altered paths cannot be flagged; a startup self-test reports `regex_unsupported` on hosts whose regex library cannot compile the bounded rules, for example a low `RE_DUP_MAX`). | V (security-review t611/t612/t620 headers and tables) |
| K-5 | `context-retriever` index directory name is hard-coded as `em-age-emage.code` for every project in `servers.yaml` and `.mcp.json`. | V (grep) |
| K-6 | `/prepare-release` (`audience: authoring`) is still installed into every target and names paths a target does not have (`scripts/verify-release-docs.py`, `docs/releases/_template.md`). | V (`implementation/docs/` has no `releases/`) |
| K-7 | Existing installs keep their old `validate-tasks.py` and templates until the files are replaced (M-4). | V |
| K-8 | The parked items of v1 K-8 are ruled and applied (T621, T624): P41 O4, P33 O1, O2, O5, O6, O-8. By decision not applied: O1-b and O5-c. New observations N-1..N-5 of `remaining-observations-ruling-v1.md` section 8 are recorded and not ruled (for example the narrator still lists the legacy `DEBT:` format as input; the Scrum Master's label list omits `priority::critical`). Other items of plan-112 section 2 were not re-read. | V (ruling read) / **(unverified)** for plan-112 |
| K-9 | **Closed** (was: release job writes a third root `release-notes.md` and embeds extra material). Replaced by K-12. | V |
| K-10 | `CHANGELOG.md` in the repository holds only `[Unreleased]`; the CI job regenerates it as a job artifact and does not commit it. For v8.0.0 the range is computed from the merge base of `v7.0.1` and the new tag; because `v7.0.1` is only on `main`, the generated list can include commits whose content is already in v7.0.1 (the T512/T513 quirk of v1 section 1). Its size was not measured. | V |
| K-11 | `docs/wiki` and README carry stale facts: component counts (27 agents / 18 or 16 commands against 28 / 19), "two servers use `transport: remote`" (four do), manual-copy tables that omit `implementation/runtime/`. The seven severity and grade scales have no single reference page (draft in `adr-008-status-and-severity-scales-v1.md`; Migration table M-6 is the interim reference). | V (grep, `ls`) |
| K-12 | `CHANGELOG.md` generation: the introductory paragraph ends up below the newest entry and moves down with each release (pre-existing `update_changelog` placement). The release job's git commands and the `apk add git` step were not run on the real CI image (`--end-of-options` needs git 2.24 or newer). | V (dry run) / **(unverified)** (image) |
| K-13 | MCP pins are exact and fresh (a few days old for several); transitive dependencies float; the `github` container runs with the default toolset (writes included), no signature or attestation verification, and an unpatched availability-only advisory (GHSA-w4q6-qw23-4rg7); `SUPABASE_ACCESS_TOKEN` is account-wide (`--read-only` limits tools, not the token); single-maintainer upstreams (`@zereight/mcp-gitlab`, `mcp-fetch-server`, `toolradar-mcp`). No automated bump scheduler exists; the pin-bump policy is a manual duty of the devops-engineer. | V (`security-review-t638-...-v1.md` L-1..L-4, L-8; `mcp-server-packages-v1.md`) |
| K-14 | Installer: a symlink guard covers the shell and the three merge scripts, but the Python checks are final-component only (ancestors are covered by `install.sh`), and a link planted between the check and the write is not detected (documented: do not run as root into a shared tree). A symlink at a managed path is refused even if it points inside the target. | V (`security-review-t636-...-v1.md` L6, L7; usage text) |

---

## 5. Out-of-band items for the release manager and the user (not decided here)

| ID | Item | Recommendation | Owner |
|---|---|---|---|
| D-1 | Golden fixture hits break G0 and `release-docs-gate` (C-1) | Option 1 of C-1, an MR before the release branch is cut, with a test | user (decision), backend-developer or devops-engineer (change), tech-lead (review) |
| D-2 | Counting rule for the three count fields of `RELEASE VERDICT` | List only `yes` entries as "Breaking changes" and put the 4 `unclear` ones under Migration only, or list all 21; either way count what is listed (RD-5). Basis: §1.4 | release-manager |
| D-3 | Channel for the M-9 out-of-band note (existing v7.x installs of a name that could be registered by a third party) | Publish the note before the tag if that can be done without the release (an advisory page in the repository and the wiki), because the exposure exists today | user |
| D-4 | `WIKI_TOKEN` Protected+Masked and `v*` tag protection (SEC-003 is LOW only on the user's statement) | Check both in GitLab before the tag and record the result in the release document's Gate Verdicts | user |
| D-5 | Rehearsal of the release job on the real CI image or on a `-rc` tag | Do it (T635 recommendation); a `-rc` tag publishes a GitLab Release, so it is the user's call; the alternative is an image run of the git commands without publishing | user, devops-engineer |
| D-6 | Test or label the Rollback Plan (MAJOR release) | Run the suggested rollback once on a scratch project, or write "not tested" | release-manager |
| D-7 | Run an automated dependency audit on the pinned MCP set and the `mcp==2.2.0` requirement (no A06 result exists) | Do it before the Release gate | security-engineer |

---

## 6. Tracked debt list for Known issues (by reference; nothing here is a security finding graded CRITICAL or HIGH)

The ledger rule is that these are tracked, not blocking (`validation-gates`, `security-guidelines.md` Security Review Workflow): LOW findings are technical debt. Item IDs are those of the named records; text is theirs.

| Source | Items | State |
|---|---|---|
| `security-review-release-v8-v1.md` (T633) | SEC-004..SEC-015 (12 LOW): no-rsync `--update` fallback without cleanup (004); `rsync -a` copies permission bits (005); merge scripts write non-atomically, MCP sidecar written before validation, ledger rows dropped without backup (006); MCP merge keeps dest-only keys in generator-owned server objects, gemini `hooks` replaced wholesale (007); plain install overwrites existing MCP configs and `CLAUDE.md`, `--dry-run` has side effects, `--platform` validated late (008); copy-paste hints print unsanitised paths (009); `eval "$saved_shopt"` hygiene (010); `re.match` with `$` accepts a trailing newline in ref validators (011); Python-`re` credential rules on attacker-controlled names, unbounded (012); scanner limits undocumented, submodules not scanned, `--allowed-root .` depends on launch directory (013); no hash pinning of `mcp==2.2.0`, no installer integrity check (014); release-script hygiene and leading-dash `--target` (015) | tracked debt (V, table read); several overlap later work (T636 covers part of 006/008 for symlinks only) |
| T633 SEC-003 | token in argv; `WIKI_TOKEN` reused | LOW on the user's statement; see D-4. Same item as SEC-T619-05, SEC-T635-02, SEC-T640-04 |
| `security-review-t619-release-job-v1.md` | SEC-T619-05 (token in argv) | tracked; SEC-T619-01..04 fixed |
| `security-review-t635-release-job-conditions-v1.md` | SEC-T635-01 (`validate_api_target` is a prefix check), -02 (redirects re-send `PRIVATE-TOKEN`), -03 (`os.chdir` before `try` in the dry run), -04 (test hygiene) | tracked debt |
| `security-review-t640-release-body-v1.md` | SEC-T640-01 (symlinked release document followed), -02 (`UnicodeDecodeError` uncaught), -03 (commit subjects and `previous_tag` unescaped in `CHANGELOG.md`), -04 (merged with the token items) | tracked debt |
| `security-review-t636-symlink-guard-v1.md` | L6 (Python checks final-component only), L7 (TOCTOU, accepted residual); L1-L5 fixed | accepted / documented |
| `security-review-t638-mcp-packages-v1.md` | L-1 fresh pins, L-2 floating transitive dependencies, L-3 GitHub container toolset and no signature check, L-4 account-wide Supabase token, L-8 single-maintainer upstreams; M-1, M-2, M-3, L-5, L-6, L-7 fixed or met | tracked debt (K-13) |
| `security-review-t620-jwt-cost-v1.md` / `poc-security-engineer-tool-scoping-v6.md` | R-1 accepted fail-closed residual; measurements for one git/libc/locale; 30 MB extrapolated | documented (K-4) |
| `code-review-t619-v2.md` | S1-S3, N1-N4 resolved by T635; N5 (ledger and Status edits inside the code commit; `Completed:` blank on close) remains a process remark | process remark |
| Other | `update_changelog` preamble placement (K-12); `GOLDEN_VERSION_LABEL` label (cosmetic, protected script); stale wiki facts (K-11); severity-scales reference page (C-8) | tracked debt |

Production-track rule applied: a `CONDITIONAL_PASS` condition is closed before the next gate; the Release gate is the next gate for the T625 conditions, which T635 closed (V: 29 tests, now 37 with T640).

---

## 7. Gate numbers (re-run on the T641 worktree, `be0fd70` = `ac63dbe` + the brief commit)

| Gate | Command | Result |
|---|---|---|
| Full suite | `python3 tests/run.py > file` | `Ran 1163 tests in 561.320s`, `FAILED (failures=1, skipped=23)`: 1139 pass, 23 skipped, **1 failure**: `tests.performance.test_team_health.TestPlanCoverage.test_every_active_task_has_a_plan`, `Active tasks not referenced by any plan in docs/plans/: ['T641']`. Cause (V): the orchestrator's brief commit `be0fd70` added the active-ledger row T641, and no file under `docs/plans/` mentions T641 (`grep -rl T641 docs/plans` is empty). It is an in-flight artifact of this task, not a defect of `ac63dbe` (the base ledger holds only T627, which `plan-121` names). It clears when T641 is archived or `plan-121` gains a reference; the orchestrator owns that edit. The plan-120 figure of 1087 tests is superseded (T629 row and the T640 review record 1163 tests) |
| Scorecard drift | `python3 scripts/scorecard.py --check` | `OK -- committed content matches a fresh run (34 cases, 28 pass, 0 regressions)` |
| Maturity | `python3 implementation/scripts/check-maturity.py --root implementation` | `79 components checked, 0 failing their claimed level` (agents 27 stable / 1 experimental; commands 14 / 5; instructions 4 / 2; skills 7 / 19) |
| Projections | `node implementation/scripts/sync.mjs --root implementation --check` | `OK - no drift across 577 files` |
| Registry | `python3 implementation/scripts/generate-registry.py --check` | `registry is up to date` |
| Task ledger | `python3 docs/tasks/validate-tasks.py` | `TASK LEDGER: PASS (2 active, 437 completed)` (before this task's own edits; I wrote no ledger) |
| Root install parity | `python3 -m unittest tests.functional.test_root_install_parity` | 7 tests OK; `tests/_baselines/root-install-drift.json` has `"drift": 0` |
| Version consistency (current state) | `python3 scripts/check-version-consistency.py` | PASS, canonical v7.0.1 |
| Version consistency (marker bumped, scratch) | same, in the scratch archive copy | FAIL, 18 findings (C-1) |
| Main-develop drift (local refs) | `python3 scripts/check-main-develop-drift.py --main-ref origin/main --develop-ref origin/develop` | `main=v7.0.1 develop=v7.0.1 releases_behind=0`, PASS (local tracking refs, no fetch) |
| Evaluator hash | `check_evaluator_hash()` against `evaluator-hash-known-good-v21.json` | no drift: `tests_golden` `7b58d5b1...fd22`, `scripts_scorecard` `45346c17...92d6` (known-good commit `cc0b411`) |
| Release job | `python3 -m unittest tests.functional.test_publish_release` | 37 tests OK; both dry runs `DRY RUN OK` |
| Release documents (v7.0.1 / v7.0.0) | `python3 scripts/verify-release-docs.py --tag vX` | exit 1 for both (no `## RELEASE VERDICT`; v7.0.0 also no markers); expected, history |
| Release documents (v8.0.0 shape, scratch) | same in the scratch copy | passes only after C-1 rows 1-9 are fixed and the golden case directory is moved aside (C-1) |
| Held-out isolation | `python3 -m unittest tests.functional.test_golden_held_out_isolation` | `Ran 8 tests ... OK`, run with this artifact in the worktree before the commit |
| Installer symlink guard | scratch reproduction of SEC-001 | exit 1, "refusing to write through a symlink", canary intact |
| Drift gate with the new order | scratch repository, real script | PASS with both markers v8.0.0; FAIL in the old order |
| CI status (`check-ci-green.py`, `make ci-gate`) | needs network and the GitLab API | **not run (unverified)**; the CI state of `ac63dbe` is unknown to me |

Pytest output was redirected to a file; only the summary line is quoted.

---

## 8. Release sign-off conflict disclosure (requirement (f))

- `tech-lead` is the agent that executes the Tech Lead review of this release (this audit, the T625 `/code-review`, the wave 3 Tech Lead gate). **It was itself promoted to `stable` in this release (T630)**, and the exit artifact of its promotion path is its own review, `code-review-t619-v1.md`/`-v2.md` (T625). The same component also wrote audit v1, this addendum, and earlier implementation tasks (T514, T536, T542, T545; v1 C-8).
- Mitigations on record (I: from ledger rows, not re-read): T626 was an independent QA check by `qa-engineer` of the T625 artifact against the command text and `validation-gates`; round 1 FAILED on form gaps, round 2 PASSED (38 rows); T630's promotion was independently re-run by the top-level session (PG-9: 79 components, 0 failing; V by me in §7). Baseline v21 was computed by two methods (T629 row).
- Residual: the independence of the reviewer from its own promotion rests on those two checks; the review of the release itself is performed by the same component. `orchestrator`, which coordinates the release, remains `experimental`.
- Recommendation: state this in the release document's `## Gate Verdicts` / `## RELEASE VERDICT` rationale; ask the user to acknowledge it, or to assign the Tech Lead gate verdict of wave 3 to a second reviewer (the user's choice; not decided here).

---

## 9. Recommended release-preparation order (wave 3, after the user's approval of the plan)

1. D-1 decision and change (MR, test) so that G0 and `release-docs-gate` can pass.
2. T627 (`/skillify` with the user) if the user wants `skillify-skill-file-template-drift` to exit before the tag; otherwise leave it in K-2.
3. Open `release/v8.0.0` from `develop`; bump the four markers and fix the five other stale lines (C-1 rows 1-9); write `docs/releases/v8.0.0.md` from §3-§6 here, with the counting rule (D-2) and the rollback label (D-6); run `verify-release-docs.py --tag v8.0.0` and `check-version-consistency.py`.
4. D-4, D-7, D-5 (rehearsal), D-3 (note), then the Security, QA and Release gates; record the sign-off disclosure (§8).
5. MR to `develop`, MR to `main` (merge commits, no squash), tag the release-branch tip, watch the three tag jobs; then record the checkpoint `checkpoint-<SEQ>-release-v8.0.0.md`.

---

## 10. What I did not verify

- **CI and remote:** no pipeline logs, no GitLab API, no `git fetch`; `origin/*` refs are the local tracking refs. CI status of `ac63dbe`, `WIKI_TOKEN` and tag-protection settings, the real image's git version, the description size limit, and whether a squash could be forced on the `main` MR are **(unverified)**.
- **Code bodies:** `poc_scan.py` (only the file list and the review claims; not re-read for T620), `git_executor.py`, `poc_audit_server.py`, `install.sh` beyond its usage text and the one reproduction, the merge scripts, `check-maturity.py`; the 29/37 test bodies of `test_publish_release.py` (I ran them, did not read them); the T636 matrix tests; the T638 pin test.
- **Review artifacts:** I read the verdict, metadata, finding and condition tables of the reviews and rulings listed under "Based on"; I did not re-derive their technical claims (for example the cp/rsync semantics, the registry data in `mcp-server-packages-v1.md`, the advisory data, the gitlab package's history). Registry facts (package ownership, versions) are as of 2026-10-14 in that artifact, not re-queried.
- **Projections:** `sync.mjs --check` passes (577 files), but I did not read the projected copies of the files changed since v1; the root parity test passes.
- **Held-out set:** `tests/golden/held-out/` was not opened and no held-out case is named; counts come from the scorecard summary (I printed only its summary table). The held-out isolation test result is in §7.
- **Plans, ADR bodies:** `plan-112` section 2 (parked notes) and ADR-007/008 bodies were not re-read; ADR-009 was read in full.
- **Platform behaviour:** how Claude Code treats a subagent call to an MCP tool with no allow rule; Copilot's resolution of `mcp__` tool names; Cursor/Gemini/Opencode/Pi/Cline permission behaviour for the new server; Windows; the minimum Python version; unchanged from v1 §6.
- **Tools:** no dependency audit was run (D-7). The wiki rendering of relative links on the GitLab Release page is untested (ruling note).
- **Local private files:** `.claude/settings*.json` (working copies) and `.vscode/mcp.json` were not read; only `git show origin/develop:.claude/settings.json | grep -c mcp__` (count) was taken.
- **Completeness:** 35 new commits since v1 were not each read; entries rest on the ledger rows (T619-T640 read in full), the review artifacts, and the diffs listed in §1.1. A change in neither (for example a doc-only commit tied to no task) could be missing.
- **Blockers reported:** D-1 (technical, major), and the unverified CI/GitLab items above (external, minor to major until the user checks them).
