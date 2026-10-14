# Artifact: release-documents-ruling-v1.md

> Filename: `release-documents-ruling-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T632 (P1, judgment tier, decision only; plan-121 item 9)
- **Created**: 2026-10-14
- **Based on:**
  - `docs/tasks/task-T632.md` (the brief, authoritative) and `docs/plans/plan-121-release-v8-wave-2.md`;
  - `docs/artifacts/release-v8-audit-v1.md` C-2, C-3, C-4 (and §2.5, §3, §4 as drafting inputs for `docs/releases/v8.0.0.md`);
  - `docs/artifacts/path-conventions-v3.md` §1 (the user's decision Q-P32b, verbatim label "One, at docs/releases/ (Recommended)": a release has one release-notes document, `docs/releases/v<VERSION>.md`);
  - `docs/artifacts/promotion-and-golden-realignment-plan-v1.md` §4.1 B2 and §6.3 items 3-6 (the golden path that will consume `docs/releases/v8.0.0.md`);
  - `docs/decisions/ADR-007-command-contract-authority.md` and `ADR-008-knowledge-document-authority.md` (both read in full; both Accepted);
  - live files read in this session (§1): `scripts/verify-release-docs.py`, `scripts/check-main-develop-drift.py`, `scripts/publish-release.py`, `scripts/dry-run-publish-release.py`, `scripts/check-version-consistency.py`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `.gitlab/merge_request_templates/Release.md`, `docs/releases/_template.md`, `docs/releases/v7.0.0.md`, `docs/releases/v7.0.1.md`, `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`, `docs/wiki/contributing-workflow.md`, `implementation/knowledge/skills/release-workflow/SKILL.md`, `implementation/knowledge/commands/prepare-release.md`, `implementation/knowledge/agents/orchestrator.md`, `implementation/knowledge/agents/release-manager.md`, `implementation/knowledge/instructions/{git-workflow,coding-standards}.md`, `tests/functional/{test_publish_release,test_check_main_develop_drift}.py`, and two open `/prepare-release` golden cases.
- **Requirements version**: none. This task has no `requirements-vN.md`; the user's recorded decisions are the requirement (§0 and the Based on list).
- **Decision references**: RD-1 to RD-8 (§3), RD-9 (§6, the body, a design question), RD-10 (§7.2 H-B2, the Release MR template). No new ADR: every ruling applies ADR-007 (branch 1, the P2 corollary) or ADR-008 (Steps A, C, D, P5).
- **Applies nothing.** Every edit below is held for the user (§7). Nothing in the repository other than this file and the brief's `**Status:**` line was written.

**Basis marker.** **V** = I read the live line in this session. **I** = inferred (reason stated). **(unverified)** = not re-read, not run, or not checkable without a shell.

## 0. Outcome summary (read this first)

1. **No conflict inside tier 1.** `AGENTS.md` and the four stable instructions say nothing about the content of the release document or the order of tag and merges. `git-workflow.md` is out of scope for release versioning by its own Rails (`:15-17`) and for CI configuration, but its protected-branch rule (`:48-68`) does decide one clause below (RD-6). No P5 escalation arises inside tier 1.
2. **Part (a), the release document.** The documents are jointly satisfiable: they list different things and none is exclusive. `docs/releases/v8.0.0.md` carries the **union** (11 sections, §4.2). Authority: `/prepare-release` governs the `## RELEASE VERDICT` block and the changelog group names (ADR-008 P2, and the skill concedes it in its own words); skill `release-workflow` § 4 supplies the other sections; `scripts/verify-release-docs.py` is the mechanical floor and stays unchanged; `docs/releases/_template.md` is only a scaffold and must be rebuilt from the union. Four documents are stale and are amended by pointer, not by copy (§7).
3. **Part (b), the ordering.** The documents do disagree, and no tier-1 text decides it. Two peer agents (`orchestrator`, `release-manager`) contradict each other, and CONTRIBUTING contradicts the drift gate. Under ADR-008 this is a P5 escalation to the user, with a recommendation: **merge the release branch to `develop`, then to `main`, both without squash, then tag the release-branch tip, which both branches contain.** The gate then sees `main` equal to `develop`. The back-merge after the tag disappears (it could not be pushed anyway, RD-6). The same rule covers hotfixes.
4. **Part (c), the GitLab Release body.** A design question held for the user (§6). Recommendation: **the body is the release document, whole, on every path** (CI, `glab release create -F`, the orchestrator preflight), and the commit-derived list stays in the `CHANGELOG.md` job artifact with merge commits excluded.
5. **One consolidated question** (§9): groups A, B, C; recommended answers A1 + B1 + C3.
6. **No protected-path grant and no evaluator baseline** is needed by any option (§8). Root drift: about 19 paths for the recommended set, 3 knowledge files (§8.2).
7. **Held-out coupling is unknown and was not checked.** I did not open `tests/golden/held-out/`.

## 1. Method and limits

- **No shell, no search tool.** I could use only file reads. Nothing was executed: not the test suite, not `verify-release-docs.py`, not `sync.mjs`, not `grep`, not `git`. Counts in §8 come from reading whole files and are **(unverified by grep)**.
- **Worktree.** `/home/emage/Code/emage/worktrees/agent-solution-architect-T632`, branch `agent/solution-architect/T632`. The orchestrator states it is `develop` `4c5b43e`; I could not run `git` to confirm **(unverified)**. The coordinator reports that `develop` has since moved (T619 and T625 merged). T619 was already in the files I read (`publish-release.py` writes only `CHANGELOG.md`; the test class `TestSingleReleaseDocument` is present); any later change to the files named in §7 is **(unverified)**, which is why every fence is applied by its Before text.
- **Not read.** `tests/golden/held-out/` (never opened). `.env*`, `.claude/settings.json` and `.vscode/mcp.json` of the user (never opened). `scripts/install.sh` beyond lines 1-160. `docs/wiki/quick-start.md`, `docs/wiki/agents-overview.md`, `implementation/SECURITY.md`. The complete `tests/` tree: I could not enumerate it, so tests that read the template, CONTRIBUTING or the preflight lines may exist **(unverified)**; I found no `test_verify_release_docs.py`, `test_release_docs_gate.py` or `test_release_workflow.py` by name.
- **Golden.** I read `case.yaml`, `brief.md` and `expect.py` of `prepare-release-real-verdict-missing`, and `case.yaml` of `prepare-release-conditional-pass-conditions-gap`; both have `tests/golden/open/` directories. The open brief of the first names a sibling `/prepare-release` case that has no directory under `tests/golden/open/`; I do not write its name. Other open cases were not searched for quotes of the lines in §7 **(unverified)**.
- **Hygiene.** The orchestrator must run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on this file before it is committed; I could not. It names no held-out id.

## 2. Facts re-read (live lines)

| # | Fact | Where | Basis |
|---|---|---|---|
| F1 | The gate requires, in the release document: `## Install`, `## Highlights`, `## RELEASE VERDICT`, `Latest release: <tag>`. The comment says the RELEASE VERDICT requirement is "declared by step 7 of implementation/knowledge/commands/prepare-release.md" and that "the field-level contract (11 fields, Status enum) is ... deliberately not duplicated in this gate" | `verify-release-docs.py:207-220` | V |
| F2 | The gate also requires `Latest release: <tag>` in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`; link-checks every required file including the release document and `_template.md`; runs `check-version-consistency.py` | `verify-release-docs.py:18-22`, `:222-225` | V |
| F3 | `check-version-consistency.py` excludes `docs/releases/` (and checkpoints, tasks, plans, artifacts, `CHANGELOG.md`). The release document may therefore cite `v7.0.1` freely | `check-version-consistency.py:64-72` | V |
| F4 | Skill § 4 prescribes `# Release Notes — v<VERSION>` with `## Summary`, `## Changelog`, `## Migration Guide`, `## Known Issues`, `## Gate Verdicts`, `## Rollback Plan`, but says: "Add the sections below, from `## Summary` on, to that document. When the release is prepared with `/prepare-release`, that command's steps govern the document, and these sections accompany them" | `release-workflow/SKILL.md:129-162` (sentence at `:131`) | V |
| F5 | `/prepare-release` step 2 groups the changelog "Features, Fixes, Breaking Changes, Internal"; step 7 puts the 11-field `## RELEASE VERDICT` in `docs/releases/v<version>.md`, issued by `@release-manager` | `prepare-release.md:16-19`, `:38-59` | V |
| F6 | The orchestrator preflight requires of the file: "Latest release: vX.Y.Z", "## Install", "## Highlights", "valid install instructions" (no RELEASE VERDICT), and says "Publish/update release notes from that file only: `glab release create ... -F docs/releases/vX.Y.Z.md`" | `orchestrator.md:131-136` | V |
| F7 | The template's install table lists Cursor, GitHub, Gemini, Opencode, Pi, All (no `claude-code`, no `cline`). Its manual-copy block copies five platform folders and `implementation/docs`, and no `.claude`, `.cline`, `.clinerules`, `.mcp.json` or `implementation/runtime/*` | `_template.md:20-52` | V |
| F8 | The installer accepts `cursor \| github \| gemini \| opencode \| pi \| claude-code \| cline \| all`; README's Install table lists exactly these eight | `install.sh:18`; `README.md:82-91` | V |
| F9 | The CI body is `# Release <tag>`, the whole release document (its first line removed only when it starts with `# Release <tag>`), `---`, then a `## Changelog` section built from commit subjects | `publish-release.py:190-201` | V |
| F10 | `update_changelog` skips every line that starts with `#` when it builds the `CHANGELOG.md` entry, so group headings are lost in `CHANGELOG.md` | `publish-release.py:214-217` | V |
| F11 | Only `bugfix/`, `feature/` and `release/` merge subjects are classified; every other `Merge branch '...' into '...'` falls to "Other". Audit: 201 of 411 subjects are merge commits | `publish-release.py:130-165`; audit C-3 | V (code); counts from the audit **(unverified)** |
| F12 | `CONTRIBUTING.md` step 8 says CI "Embeds **Install + Highlights**" and "Appends a **Changelog** section"; `_template.md:3-5` says the same; the manual repair command publishes the file only; the orchestrator and README say "from that file only" | `CONTRIBUTING.md:198-208`; `_template.md:3-5`; `README.md:192` | V |
| F13 | The drift gate reads the README marker on `origin/main` and `origin/develop`. It fails when `main` sorts AFTER `develop` ("invariant violation"), when either marker is not a known tag, or when `main` is more than 1 release behind. It deliberately does not use commit ancestry | `check-main-develop-drift.py:57-74`, `:99-112`, `:122-128`; docstring `:7-12` | V |
| F14 | `release` `needs` both `release-docs-gate` and `main-develop-drift-gate`; both run only on a tag push. The informational `main-develop-drift-check` runs on pushes to `develop`, `allow_failure: true` | `.gitlab-ci.yml:114-127`, `:169-195` | V |
| F15 | `CONTRIBUTING.md` step 5-7 order: MR `release/vX.Y.Z -> main`, merge, then on `main` tag and push, then `git checkout develop && git merge --no-ff main && git push` as the back-merge. The Release MR template repeats it | `CONTRIBUTING.md:165-194`; `Release.md:24-32` | V |
| F16 | `main` and `develop` are protected; "GitLab rejects any direct push to either branch, with no exceptions"; stable, `applyTo: "**"` | `git-workflow.md:4`, `:48-68` | V |
| F17 | The orchestrator preflight: "Tag creation happens AFTER MR is merged to develop" and "ensure tag commit is already in origin/develop". `release-manager`: "Merge release branch to `main`; Create Git tag; Create GitLab release; Merge back to `develop`" and the same order in its checklist | `orchestrator.md:139-141`; `release-manager.md:29-34`, `:145-151` | V |
| F18 | The drift documentation calls the grace window "the normal transient state between a release being tagged and its `release/vX.Y.Z -> main` sync MR landing" | `CONTRIBUTING.md:217-218`; `check-main-develop-drift.py:23-24` | V |
| F19 | The Release MR template says "CHANGELOG.md updated and committed", "Auto-generated by git-cliff in the release job", "none currently — the project is unversioned in source", and repeats Highlights / Breaking changes / Changelog sections | `Release.md:13-19` | V |
| F20 | The golden check reads `fixture/docs/checkpoints/*.md` today (retarget to `fixture/docs/releases` is planned in G-1 item 3). It requires exactly one `*.md` in that directory, takes the FIRST occurrence of the substring `## RELEASE VERDICT`, ends the section at the next H1 or H2 outside a fence, needs the 11 fields as `**Field**:`, a first `Status` token in `PASS`/`CONDITIONAL_PASS`/`FAIL`, and `Version` matching `^v\d+\.\d+\.\d+$` | `prepare-release-real-verdict-missing/expect.py:14-79`; `promotion-and-golden-realignment-plan-v1.md` §6.3 item 3 | V |
| F21 | Tests couple to the CI release job and the body: `assertIn("## Changelog", payload["description"])`; the `release` job's `needs`, artifact list `["CHANGELOG.md"]`, token and tag rule; `classify_subjects` cases for `bugfix/` merges and `release/v2.0.2`; `get_commit_subjects` git-call shape | `test_publish_release.py:42-56`, `:114`, `:190-210`, `:229-240` | V |
| F22 | The dry-run prints "changelog section" as the text after the last `---` of the description | `dry-run-publish-release.py:154` | V |
| F23 | `release-manager` requires "ALWAYS test rollback procedure before major releases". The audit's v8 rollback text is "suggested; not verified by running it" | `release-manager.md:227`; audit §3 | V |

## 3. Rulings (ADR-007 / ADR-008 records)

Per ADR-008 D5, each ruling states the subject, the clauses, the Step A analysis, the step that fired, the scope text relied on, the amendment and the file it falls on. **Maturity was not relied on in any ruling** (P4): `release-workflow`, `/prepare-release` and `orchestrator` are `experimental`, `release-manager` is `stable`, and nothing below depends on that.

### RD-1 Required contents of the release document (audit C-2, first bullet)

- **Subject:** the set of sections `docs/releases/v<VERSION>.md` carries.
- **Clauses:** the gate's four snippets (F1); skill § 4's six sections (F4); the preflight's three items (F6); the template's `## Install`, `## Highlights`, `## Breaking changes`, `## RELEASE VERDICT` (`_template.md:8-81`); `/prepare-release` step 7 (F5).
- **Step A:** none of the clauses is exclusive (no "only", "instead of", "replaces", no closed set); each adds sections that compete with none. They are jointly satisfiable by one document that holds the union. This is specialisation (D4), not contradiction. The preflight's list is incomplete (it omits `## RELEASE VERDICT`, which the gate requires), and the template's header text understates the document ("highlights + install"); an incomplete list is not a rival rule.
- **Step fired:** A. No rank is needed.
- **Authority, stated per subject** (what each document governs):

| Subject | Governs | Why |
|---|---|---|
| The `## RELEASE VERDICT` block (fields, enum, home, issuer) | `/prepare-release` step 7 | A command's declared output contract governs its output (ADR-008 P2). The skill concedes this in its own words ("that command's steps govern the document"), `release-manager.md:161` accompanies it, and the gate cites it (`verify-release-docs.py:211-215`) |
| The other prescribed sections (Summary, Changelog, Migration Guide, Known Issues, Gate Verdicts, Rollback Plan) | skill `release-workflow` § 4 | The command is silent on them; the skill supplies the method and accompanies the command |
| `## Install`, `## Highlights`, the `Latest release:` marker | `scripts/verify-release-docs.py` | No knowledge document declares them. The gate is a mechanical check, outside ADR-008's coverage; it is the floor and is not changed (ADR-007 §5: no check is weakened, and none is tightened by this ruling unless the user picks A2) |
| Pass or fail of the tag | the gate | It runs on the tag |
| The Install table's `--platform` values | `scripts/install.sh` usage (F8) | The installer defines what is accepted; README agrees; the template is a stale copy |
| Scaffold | `docs/releases/_template.md` | Derived from all of the above; governs nothing |

- **Amendment:** pointer edits, not copies (ADR-008 P3b remedy "by name and section"): H-A1 to H-A5 (§7), all held.
- **Scope text relied on (D2):** skill `description` and `:131`; command `description` and step 7; gate comment `:211-215`.

### RD-2 First line of the document (audit C-2, second bullet)

- **Subject:** the title.
- **Clauses:** skill § 4 block `# Release Notes — v<VERSION>`; template `# Release vX.Y.Z`; v7.0.0 and v7.0.1 notes `# v7.0.0`, `# v7.0.1`; `publish-release.py:197-198` removes a first line only if it starts with `# Release <tag>`.
- **Step A:** jointly satisfiable: the skill's own sentence adds the sections "from `## Summary` on", which excludes the title block. But a reader of the fenced block alone writes `# Release Notes — v8.0.0`, which the script does not strip, and the GitLab body then has two H1 lines (`# Release v8.0.0`, then `# Release Notes — v8.0.0`). The v7 notes have the same defect (`# v7.0.1` after the added `# Release v7.0.1`) **(I: from the code path, not from a rendered page)**.
- **Ruling:** the first line is `# Release v<VERSION>`. The skill states it (H-A3). No existing note is edited (releases are history).

### RD-3 Changelog groups (audit C-2, second bullet)

- **Subject:** the group names inside the document's changelog.
- **Clauses:** `/prepare-release` step 2 "Group by: Features, Fixes, Breaking Changes, Internal"; skill § 2 six groups at H2 (`Breaking Changes`, `New Features`, `Bug Fixes`, `Improvements`, `Documentation`, `Internal`); CI and `CONTRIBUTING.md:297-313` ten commit groups.
- **Step A:** the command's list is a named set for the same field the skill's list renames ("Features" against "New Features", "Fixes" against "Bug Fixes"), so one changelog cannot carry both heading texts. The CI and CONTRIBUTING groups describe a different artifact (a list generated from commit subjects) and do not compete; they are not ranked.
- **Step fired:** C (P2). The skill is applied under the command for this document, and says so itself (`:131`). The command governs; the skill is amended, scoped to "when the release is prepared with `/prepare-release`" (P2 remedy). The command is not amended.
- **Amendment:** H-A3. Inside the document the command's Breaking Changes group is the `## Breaking changes` section; `## Changelog` holds `### Features`, `### Fixes`, `### Internal`. An Improvements or Documentation task is placed by the release manager in one of these (the command does not say which; **left to the release manager and recorded in the Changelog preface, not ruled**).

### RD-4 Install section content (audit C-2, last bullets)

- **Subject:** which platforms and files `## Install` lists.
- **Clauses:** template (F7) against installer and README (F8) and against v7.0.0 and v7.0.1, which listed Claude Code and Cline.
- **Step A:** contradiction of fact: the template lists a subset of what the installer accepts, and its manual-copy block would give an adopter an install without `implementation/runtime/{memory,security,handoff}` (shipped by the installer since v7.0.1, T513 and T553) and without MCP config merging.
- **Ruling:** the installer defines the values. H-A1 lists all eight, keeps the `--update` sentence, and removes the manual-copy block (a second copy of the install procedure that drifted; `implementation/README.md:23-29` carries another and is outside this ruling, **observation O-3**). If the user prefers to keep a manual-copy block, it must list `.claude`, `.cline`, `.clinerules`, the MCP files and `implementation/runtime/*`; I recommend against it **(exact `implementation/` layout for Claude Code and Cline (unverified))**.

### RD-5 Composition rules that need no knowledge edit (audit C-2, remaining bullets)

- **Heading for the upgrade steps:** `## Migration Guide` (skill § 4, and its checklist item "Migration guide written", `SKILL.md:120`). "Migration section" in plan-120 and the audit is descriptive, not a heading.
- **Counts in the verdict** ("Features included", "Fixes included", "Breaking changes"): each equals the number of entries listed under the matching heading of the same document (Features, Fixes, and `## Breaking changes`). The audit's §2.5 gives a basis (14 `yes`, plus 4 `unclear`); the release manager decides whether `unclear` entries are listed as breaking and then counts what is listed.
- **`Release:` line equals `**Status**`:** already ruled in skill § 4; no action.
- **Exactly one `## RELEASE VERDICT`:** `release-manager.md:161` already says its own block "is not a second `## RELEASE VERDICT` section in that document". Keep it so (F20 reads the first occurrence).

### RD-6 Back-merge by direct push (audit C-4, tier-1 part)

- **Subject:** how release content reaches `develop`.
- **Clauses:** `CONTRIBUTING.md:193` and `Release.md:31`, `git checkout develop && git merge --no-ff main && git push`; against `git-workflow.md:48-61`: "`main` and `develop` are protected on the remote. GitLab rejects any direct push to either branch, with no exceptions".
- **Step A:** fails: no single action both pushes directly and does not.
- **Step fired:** P1 applied by analogy. The tier-1 text is quotable and within scope (it names merges and protected branches). CONTRIBUTING.md is not a knowledge document and is outside ADR-008's coverage, but the T542 precedent treats a document that contradicts a stable instruction on a protected-branch rule as defective, and the rule is also a fact of the remote: `CONTRIBUTING.md:265-267` records `push_access_levels: ['No one']` for `main`, identical to `develop`.
- **Ruling:** under every option of group B, the step-7 back-merge by direct push is removed. The release reaches `develop` by merge request.

### RD-7 Order of the tag and the merges (audit C-4)

- **Subject:** the order of three steps: merge to `develop`, merge to `main`, create the tag.
- **Clauses:** `release-manager.md:29-34` and `:145-151` (main, tag, develop); `CONTRIBUTING.md:165-194` and `Release.md:24-32` (main, tag, develop, by direct push); `orchestrator.md:139-141` (tag after the merge to `develop`; tag commit already in `origin/develop`); the drift gate (F13) and its documentation (F18: tag, then the `main` sync MR).
- **Step A:** fails. Lists with an order cannot both be followed: "tag, then merge back to develop" and "tag after the merge to develop" place the same step on opposite sides of the tag. The gate adds a fact: at the tag push the README marker of `main` must not sort after that of `develop`.
- **Tier 1 (Step B):** does not decide. `git-workflow.md` declares release versioning and CI configuration out of its scope (`:15-17`); it decides only RD-6.
- **Peers (Step D):** `orchestrator` and `release-manager` do not place the subject with one another. The orchestrator's text delegates "release preparation" to the release manager (`orchestrator.md:259`) but its preflight is "MANDATORY before cutting any release tag" in its own words; the release manager's Rails do not defer. Self-placement does not decide, and scope nesting is not a basis (user decision Q1 in ADR-008).
- **Step fired:** E (P5). Blocker type `unclear_requirements`, severity `major` (it blocks the v8.0.0 tag if unresolved). Routed to the user as group B. Until answered, no document is amended on this subject.
- **Gate evidence for the recommendation (F13, F14):** under the current CONTRIBUTING order, at the tag push `main` carries the new marker and `develop` still the old one, and the back-merge cannot even be pushed (RD-6): `evaluate` raises "main marker ... is AHEAD of develop marker" and the `release` job, which `needs` the gate, does not run. For the v7.0.1 tag the audit records tag at 08:54:39 and back-merge at 08:57:58 UTC; whether the v7.0.1 gate passed, and how, is **(unverified)** (no CI log).

### RD-8 Hotfix order (audit C-4, by extension)

- **Subject:** the same three steps for a `hotfix/*` branch.
- **Clauses:** `CONTRIBUTING.md:291-295` ("MR to `main` ... After merge: tag, then back-merge `main -> develop`"); skill § 5 steps 5-6 (release, then "Merge hotfix branch into main"); `release-manager.md:36-41` ("Merge to `main` AND `develop`. Tag and release"); `git-workflow.md:36` ("hotfix/* ... from main -> main + develop").
- **Ruling:** the same gate applies to a hotfix tag, so the same order does. The tier-1 line and `release-manager` already say "both"; CONTRIBUTING and the skill are amended to the group B answer. A decision on group B is a decision on this.

## 4. Part (a): what `docs/releases/v8.0.0.md` must contain

### 4.1 Which document is the authority

Per §3 RD-1: `/prepare-release` for the verdict block and the changelog group names; the skill for the remaining sections; the gate for pass or fail and for `## Install`, `## Highlights` and the marker; the installer for the platform list. No knowledge document is edited to rank another, and the command stays byte-unchanged.

### 4.2 The content contract (the union), in document order

| # | Section | Required by | Source for the v8.0.0 text |
|---|---|---|---|
| 1 | `# Release v8.0.0` (first line) | RD-2; `publish-release.py:197-198` | n/a |
| 2 | `## Summary` (1-3 sentences) | skill § 4 | audit §2 headline |
| 3 | `## Install`, with the line `Latest release: v8.0.0` | gate (F1); CONTRIBUTING step 3 | the eight `--platform` values (F8); `--update`; one pointer to the Migration Guide |
| 4 | `## Highlights` | gate (F1); template | audit §2.2, §2.3 |
| 5 | `## Breaking changes` | template; the command's Breaking Changes group | audit §2.1 (21 entries; 14 `yes`, 4 `unclear`) |
| 6 | `## Migration Guide` | skill § 4 and checklist | audit §3 (M-1 to M-7) |
| 7 | `## Changelog` with `### Features`, `### Fixes`, `### Internal`; task IDs and artifact versions | skill § 4; command step 2 | `docs/tasks/completed-tasks.md` rows since T514; audit §2 |
| 8 | `## Known Issues` | skill § 4 | audit §4 (K-1 to K-10), refreshed by `release-v8-audit-v2.md`; not copied from v1 (counts change after T628 to T630) |
| 9 | `## Gate Verdicts` (five lines; the `Release` line equals the verdict Status) | skill § 4 | the gate artifacts of wave 3 |
| 10 | `## RELEASE VERDICT` (11 fields) | gate (F1); command step 7 | `@release-manager` |
| 11 | `## Rollback Plan` | skill § 4 | audit §3 rollback paragraph. v8.0.0 is a MAJOR release, so `release-manager.md:227` asks for the rollback to be tested; the audit text is untested (F23). Either test it or state "not tested" in this section; do not leave the audit's wording unqualified |

### 4.3 Composition rules (checks the author runs; none edits a knowledge file)

1. The `## RELEASE VERDICT` heading text appears exactly once, as the heading, and not earlier in the file (F20 reads the first occurrence; F1 reads any).
2. Verdict fields are `- **Field**: value` for all 11 names in `prepare-release.md:48-58`; `Status` starts with one of `PASS`, `CONDITIONAL_PASS`, `FAIL`; `Version` is `v8.0.0`; the section contains no `#` or `##` heading (F20 ends it there).
3. Counts follow RD-5. `Open blockers` and `Blocker IDs` agree with `Status`.
4. `Gate Verdicts` `Release:` equals `Status` (skill § 4).
5. Repository files are cited as code spans or absolute URLs, not relative markdown links: the gate link-checks the document (`verify-release-docs.py:122-133`), and a relative link would not resolve from the GitLab Release page **(I: not tested)**.
6. `Latest release: v8.0.0` appears once, under `## Install`. The same marker must be present in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` (F2); that bump and the 11 stale claims of audit C-1 belong to wave 3.
7. The install table has exactly the eight values of F8.
8. The document is written on the `release/v8.0.0` branch and gated locally with `python3 scripts/verify-release-docs.py --tag v8.0.0` (the script reads files only; it does not need the tag) **(unverified: not run)**.

### 4.4 Golden consequence (no action here)

The planned Stage 2 of the golden realignment (G-2, baseline v22) copies this document byte-identically into `prepare-release-real-verdict-missing`. Rules 1 and 2 above are what keep that check satisfiable by an honest document; they do not aim the document at the check, they are the command's own step 7 contract. G-2 and v22 stay as planned and are not requested here.

## 5. Part (b): the ordering that the gates accept

### 5.1 What the gates require at the tag push

Both gates run on the tag pipeline and see the repository as it is at that moment (F14): `release-docs-gate` on the tagged tree; `main-develop-drift-gate` on `origin/main` and `origin/develop`. The drift gate passes when, in tag order, `develop`'s marker is at or after `main`'s and `main` is at most 1 release behind, and both markers are known tags (the tag being pushed counts). It compares README markers, never ancestry (F13).

### 5.2 Orderings tested against the gates

| Ordering | Steps | At the tag push: `main` / `develop` marker | Drift gate | Other documents contradicted |
|---|---|---|---|---|
| **Current** (CONTRIBUTING, Release template, `release-manager`) | MR to `main`; tag on `main`; back-merge by direct push | new / old | **FAIL** ("main AHEAD of develop") | `git-workflow.md` (the push); the orchestrator preflight |
| **B1 (recommended)** | MR to `develop`; MR to `main`; tag the release-branch tip | new / new | PASS (0 behind) | `release-manager`, CONTRIBUTING, Release template (amended); preflight needs a one-line edit |
| **B2** | as B1; tag the merge commit on `main` | new / new | PASS | as B1, and the preflight's "tag commit already in origin/develop" is false unless a `main -> develop` MR follows the tag |
| **B3** | MR to `develop`; tag the `develop` merge commit; MR to `main` later | old / new | PASS (1 behind, the grace window) | the tag is not on `main`; `release-manager`, CONTRIBUTING, Release template, README all change more; a second release before the `main` MR lands fails the gate |
| **B4** | keep the current order and change the gate to ignore "main ahead" | new / old | PASS only by removing an invariant | weakens a check (ADR-007 §5 applies by spirit); the back-merge still cannot be pushed (RD-6). Not recommended |

The current order passes only if `develop` already carries the new marker before the tag, that is, if the version bump was merged to `develop` ahead of the release branch. `CONTRIBUTING.md` step 2 bumps on the release branch, and what v7.0.1 did is **(unverified)**.

### 5.3 The recommended ordering (B1), as a procedure

1. Branch `release/vX.Y.Z` from `develop`.
2. On the branch only: bump the version markers (the audit C-1 list), write `docs/releases/vX.Y.Z.md` (§4), run `python3 scripts/verify-release-docs.py --tag vX.Y.Z`; CI green on the branch.
3. Open MR `release/vX.Y.Z -> develop` and MR `release/vX.Y.Z -> main` (Release template).
4. Merge the `develop` MR first, then the `main` MR, each with a merge commit and without squash (the PUT-first sequence of CONTRIBUTING step 6, whose `squash` handling this project needs); the `develop` MR does not delete the source branch, the `main` MR does. After the `main` merge, run `scripts/verify-main-sync-merge.py <iid>`; whether it can be run against the `develop` MR record is **(unverified: I read its description in CONTRIBUTING.md, not the script)**.
5. Tag the release-branch tip, which both branches now contain, after checking it. With a non-squash merge it is the second parent of `main`'s merge commit:
   - `sha=$(git rev-parse origin/main^2)`;
   - `git merge-base --is-ancestor "$sha" origin/develop` and `... origin/main` both succeed;
   - `git diff --exit-code "$sha" origin/main` is empty (same tree);
   - `git tag -a vX.Y.Z -m "Release vX.Y.Z" "$sha"` and `git push origin vX.Y.Z`.
   If a check fails because GitLab squashed the `main` merge, use the "ancestry restore" recovery already in CONTRIBUTING, then repeat. **(Unverified: none of these commands was run.)**
6. The tag push runs `release-docs-gate` and `main-develop-drift-gate` (equal markers), then `release`.

**Between steps 4 and 6**, the informational `main-develop-drift-check` on `develop` reports the new marker as "not a known git tag"; `allow_failure: true` makes this a warning, not a block. The release can be abandoned before the tag by reverting the `develop` merge by MR; this is the reason `develop` goes first (an abandoned release then never touched `main`).

**Effects of B1 beyond the gate.** (i) The tag commit is on both branches, which satisfies "ensure tag commit is already in origin/develop" in the preflight and "tag on `main`" in the Release template in one commit. (ii) `publish-release.py` resolves the range with `merge-base(previous_tag, current_tag)` (`:90-104`); with the previous tag in `develop`'s history the next range is exact. For v8.0.0 itself the audit's range quirk (411 subjects, including T512 and T513) remains, because the previous tag `v7.0.1` is on `main` and this ordering did not exist then; it is not caused or cured by this ruling. (iii) The grace window of the gate (F18) becomes a tolerance, not a step.

## 6. Part (c): how the GitLab Release body should be built (design question, held for the user)

### 6.1 Facts

- CI body: `# Release <tag>` + the whole release document + `---` + a `## Changelog` section from commit subjects (F9).
- The same body goes into `CHANGELOG.md`, with all `#` lines dropped (F10), so `CHANGELOG.md` entries lose their group headings and carry the whole document's prose. This is **observation O-1**, not decided here.
- Every other statement about the body says something different (F12): "Install + Highlights" embedded (CONTRIBUTING, template), "from that file only" (orchestrator, README, manual repair command).
- With the union document of §4, the body would contain two `## Changelog` headings (the curated one from the document, the generated one appended) and, for this range, about 201 merge-commit lines in "Other" (audit C-3, **(unverified)**).
- GitLab's limit on a release description was 1,000,000 characters when it was introduced (GitLab MR 60386, 2021); the current limit is **(unverified)**. The v8.0.0 body would be well below it either way **(I)**.

### 6.2 Options (design only; no code is written or held as a fence)

| Option | Body | Commit-derived list | Code surface | Notes |
|---|---|---|---|---|
| **C1. Keep** | whole document + unfiltered list | in body and `CHANGELOG.md` | none; text edits only (CONTRIBUTING step 8, template intro, preflight) | Two `## Changelog` headings and about 201 "Other" lines remain. The manual `glab -F` path publishes a different body than CI |
| **C2. Filter** | whole document + filtered list under a new heading | filtered, in body and `CHANGELOG.md` | `get_commit_subjects` (add `--no-merges`), `render_changelog_section` heading, tests | Filter F1 below. The manual `glab -F` path still differs from CI |
| **C3. Document only (recommended)** | the document, whole, starting `# Release vX.Y.Z` | filtered by F1, `CHANGELOG.md` only | `render_release_description`, `main`, `update_changelog` input, dry-run, tests | Same text on all three paths. The commit list is not on the release page |
| **C4. Excerpt** | Install + Highlights + Breaking changes + a link to the document in the repository, plus the filtered list | filtered, in body and `CHANGELOG.md` | a section extractor (new code), tests | Two sources of truth for the release text; the document must keep fixed headings. Not recommended |

**Filter F1 (applies to C2, C3, C4).** Exclude merge commits structurally: `git log --no-merges --pretty=%s --end-of-options <range>` instead of excluding by subject text. Reason: GitLab merge-commit subjects carry only a branch name; the content commits stay in the log (squash-merged feature branches contribute their conventional subject). With the audit's counts this leaves 210 of 411 subjects (128 `docs`, 25 `fix`, 19 `feat`, 19 `chore`, 14 `test`, 5 untyped; **(unverified)**). The `Merge branch` branches of `classify_subjects` become unused on the CI path and the two tests that exercise them keep passing unchanged (F21). Optional F2 for C2/C4: collapse `docs`, `test`, `ci`, `chore`, `refactor` to one line ("N internal commits; see `git log <previous>..<tag>`").

### 6.3 Recommendation and why

**C3.** (1) It carries out the user's decision of one release document to its end: the page, the repair command and the preflight all publish the same text, which is what the preflight's "do not pass ad-hoc `--notes`; it can drift" asks for. (2) The document already holds a curated, task-grouped changelog (skill § 4 makes it required), so a second, noisy list on the page adds duplication, not information. (3) It removes the heading collision and the size and noise questions. (4) The commit list is kept where it was always generated as an artifact (`CHANGELOG.md`), with F1 applied. Cost: the release page loses the commit list; `publish-release.py` is a security-reviewed script (T619 review), so the diff needs the same review.

**If the user picks C3**, the held text edits are H-C1 (CONTRIBUTING step 8) and the template intro already in H-A1. If the user picks C1, C2 or C4, those two sentences and the orchestrator line `:133-134` change as listed in §7.4; no new decision is needed.

## 7. Held amendments (nothing is applied)

Each Before must match exactly once at dispatch; apply by Before text, not by line number. Edits in knowledge files need `node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py`, both with `--check`, and a declared root drift (§8.2). Text is written for installed targets too: the three knowledge-file edits cite no `CONTRIBUTING.md` path, and the script and template paths they cite are already cited by installed text (audit K-6; **observation O-2**).

### 7.1 Group A (the document), recommended A1

**H-A1 `docs/releases/_template.md`: replace the whole file.** The intro states the C3 behaviour; if group C is not C3, see §7.4.

````
After (the complete new file):
# Release vX.Y.Z

Copy this file to `docs/releases/vX.Y.Z.md` on the `release/vX.Y.Z` branch before the tag is cut, and delete this paragraph. It is the release's one document: `scripts/verify-release-docs.py --tag vX.Y.Z` checks it, its sections follow skill `release-workflow` § 4, the release job publishes it whole as the GitLab Release description, and `/prepare-release` step 7 writes the release gate verdict into it. Keep the first line as `# Release vX.Y.Z`. Do not quote the verdict section's heading text above that section. Cite repository files as code spans or absolute URLs, not relative links.

## Summary

<1-3 sentences: what this release contains>

## Install

Latest release: vX.Y.Z

Install with the installer from a clone of this repository:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target <your-project> --platform <name>
```

| Platform | `--platform` value |
|----------|-------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| Claude Code | `claude-code` |
| Cline | `cline` |
| All platforms | `all` |

Update an existing install: add `--update`. `scripts/install.sh --help` lists every option.

Set the MCP environment variables named in the generated MCP config, then run
`/new-project "Your idea"` in your assistant.

## Highlights

- Feature one — what users get in this release
- Feature two — …

## Breaking changes

- None (or one entry per breaking change; the verdict count equals the number of entries)

## Migration Guide

<if applicable — steps to upgrade from the previous version>

## Changelog

<one line per entry: description, task ID, artifact version references>

### Features

### Fixes

### Internal

## Known Issues

- <any known issues shipping with this release>

## Gate Verdicts

- Architecture: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Implementation: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Integration: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Security: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD
- Release: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD (the same value as the Status below)

## RELEASE VERDICT

Release gate outcome for this version, per step 7 of `/prepare-release`. This document is the
declared home for the block; fill in every field before the tag is cut.

- **Version**: vX.Y.Z
- **Status**: PASS | CONDITIONAL_PASS | FAIL
- **Features included**: <count>
- **Fixes included**: <count>
- **Breaking changes**: <count>
- **Open blockers**: <count>
- **Quality gates passed**: [list gates: code-review, security-audit, test-coverage, ...]
- **Quality gates failed**: [list any failed gates]
- **Blocker IDs**: [if FAIL — list blocking issues with owners]
- **Release manager**: release-manager
- **Timestamp**: <ISO-8601>

## Rollback Plan

<steps to roll back if critical issues are discovered after the release; state whether they were tested>
````

The `## RELEASE VERDICT` section and its 11 field lines are byte-identical to the current template (`_template.md:66-81`).

**H-A2 `implementation/knowledge/agents/orchestrator.md:135`.**

````
Before:
   - File must include: "Latest release: vX.Y.Z", "## Install", "## Highlights", valid install instructions

After:
   - File must carry what `scripts/verify-release-docs.py` requires (`Latest release: vX.Y.Z`, `## Install`, `## Highlights`, `## RELEASE VERDICT`) and the sections skill `release-workflow` § 4 prescribes, with valid install instructions (`scripts/install.sh --help` lists the `--platform` values)
````

**H-A3 `implementation/knowledge/skills/release-workflow/SKILL.md:131`** (one line, the paragraph under `### 4. Create Release Artifact`).

````
Before:
The release notes are one document per release, `docs/releases/v<VERSION>.md`: the file the `orchestrator` agent § Release Workflow Preflights publishes, and the release notes document into which `/prepare-release` step 7 writes the `## RELEASE VERDICT` section. Add the sections below, from `## Summary` on, to that document. When the release is prepared with `/prepare-release`, that command's steps govern the document, and these sections accompany them. The `Release` line under `## Gate Verdicts` carries the same value as the `**Status**` of the `## RELEASE VERDICT` section.

After:
The release notes are one document per release, `docs/releases/v<VERSION>.md`: the file the `orchestrator` agent § Release Workflow Preflights publishes, and the release notes document into which `/prepare-release` step 7 writes the `## RELEASE VERDICT` section. Add the sections below, from `## Summary` on, to that document. When the release is prepared with `/prepare-release`, that command's steps govern the document, and these sections accompany them: its Breaking Changes group is the `## Breaking changes` section, and `## Changelog` holds its Features, Fixes and Internal groups (step 2) as `###` headings, not the six groups of § 2. The document's first line is `# Release v<VERSION>`, not the title in the block below, and it also carries the `## Install` and `## Highlights` sections that `scripts/verify-release-docs.py` requires (`docs/releases/_template.md` is the scaffold). The `Release` line under `## Gate Verdicts` carries the same value as the `**Status**` of the `## RELEASE VERDICT` section.
````

**H-A4 `CONTRIBUTING.md:155-159`** (step 3). The strings `release-docs-gate` and `verify-release-docs.py`, required by the gate in this file (`verify-release-docs.py:51-57`), are untouched elsewhere.

````
Before:
3. Create the per-release brief `docs/releases/vX.Y.Z.md` (copy
   `docs/releases/_template.md`) with **Install**, **Highlights** and **RELEASE VERDICT**
   sections. The `## RELEASE VERDICT` block is the release gate outcome required by step 7 of
   `/prepare-release`; the release notes document is its declared home, and step 4's gate below
   checks it is present.

After:
3. Create the per-release document `docs/releases/vX.Y.Z.md` (copy
   `docs/releases/_template.md`). It is the release's one document: it carries the **Install**,
   **Highlights** and **RELEASE VERDICT** sections that step 4's gate checks, and the sections
   skill `release-workflow` § 4 prescribes (Summary, Migration Guide, Changelog, Known Issues,
   Gate Verdicts, Rollback Plan). The `## RELEASE VERDICT` block is the release gate outcome
   required by step 7 of `/prepare-release`; the release notes document is its declared home.
````

**H-A5 two one-line wording edits.**

````
Before (README.md:191):
- Required per-release brief: `docs/releases/vX.Y.Z.md` (Install + Highlights)

After:
- Required per-release document: `docs/releases/vX.Y.Z.md` (Install, Highlights and RELEASE VERDICT, plus the sections skill `release-workflow` § 4 prescribes)
````

````
Before (docs/wiki/README.md:44):
- `docs/releases/vX.Y.Z.md` (Install + Highlights for the tagged version)

After:
- `docs/releases/vX.Y.Z.md` (Install, Highlights and RELEASE VERDICT for the tagged version)
````

### 7.2 Group B (the ordering), recommended B1

**H-B1 `CONTRIBUTING.md`, five fences (steps 5, 6, 7; drift paragraph; hotfixes).** Step numbers are kept so the references "step 6 above" at `:249` and `:280-281` stay valid.

````
Before (step 5, :165):
5. Open MR `release/vX.Y.Z → main` using the **Release** MR template

After:
5. Open two MRs from `release/vX.Y.Z`: first `release/vX.Y.Z → develop`, then
   `release/vX.Y.Z → main` using the **Release** MR template. Both are merged (step 6) before
   the tag is created, `develop` first, because the `main-develop-drift-gate` fails a tag push
   while `main` is ahead of `develop`.
````

````
Before (step 6, :166-168):
6. Merge it. For `release/*→main` merges specifically (not the generic squash-and-merge
   convention used for `feature/*`/`bugfix/* → develop` MRs elsewhere in this doc), use this
   PUT-first sequence as the standard merge step:

After:
6. Merge the `develop` MR first, then the `main` MR. Neither is squashed: use the PUT-first
   sequence below for both, with `should_remove_source_branch=false` on the `develop` MR (the
   `main` MR still needs the branch) and `true` on the `main` MR. For `release/*→main` merges
   specifically (not the generic squash-and-merge convention used for `feature/*`/`bugfix/* →
   develop` MRs elsewhere in this doc), use this PUT-first sequence as the standard merge step:
````

````
Before (step 7, :188-194):
7. After merge to `main`:
   ```bash
   git checkout main && git pull
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   git checkout develop && git merge --no-ff main && git push   # back-merge
   ```

After:
7. After both merges, tag the release branch's tip. It is an ancestor of `origin/develop` and
   of `origin/main` and has the same tree as `origin/main`; check that, then push the tag.
   There is no separate back-merge: `main` and `develop` are protected (`git-workflow.md`),
   and the release content reached `develop` in step 6.
   ```bash
   git fetch origin
   sha=$(git rev-parse origin/main^2)   # the release branch tip, when step 6 did not squash
   git merge-base --is-ancestor "$sha" origin/develop && git merge-base --is-ancestor "$sha" origin/main
   git diff --exit-code "$sha" origin/main
   git tag -a vX.Y.Z -m "Release vX.Y.Z" "$sha"
   git push origin vX.Y.Z
   ```
````

````
Before (Drift detection, :217-218):
- **Grace window:** `main` may lag `develop` by up to 1 release — the normal transient state
  between a release being tagged and its `release/vX.Y.Z → main` sync MR landing.

After:
- **Grace window:** `main` may lag `develop` by up to 1 release. In the order of "Cutting a
  release" both branches carry the release before the tag, so the window is a tolerance, not a
  step. `main` ahead of `develop` is always a failure.
````

````
Before (Hotfixes, :293-295):
1. Branch from `main`: `hotfix/vX.Y.Z+1`
2. Fix, test, MR to `main`
3. After merge: tag `vX.Y.Z+1`, then back-merge `main → develop`

After:
1. Branch from `main`: `hotfix/vX.Y.Z+1`
2. Fix, test; bump the `Latest release:` marker and write `docs/releases/vX.Y.Z+1.md`
3. MR to `develop` first, then MR to `main`, merged as in "Cutting a release" step 6
4. Tag `vX.Y.Z+1` as in step 7 (the same gates run: `main` must not be ahead of `develop`)
````

**H-B2 `.gitlab/merge_request_templates/Release.md`: replace the whole file.** (Depends on group C only in its last sentence, written for C3.)

````
After (the complete new file):
## Release `vX.Y.Z`

> Created from `release/vX.Y.Z` → `main`. The twin MR `release/vX.Y.Z` → `develop` is merged
> first, then this one. After both merge, tag `vX.Y.Z` as `CONTRIBUTING.md` § Releasing, step 7
> describes.

## Release document
- [ ] `docs/releases/vX.Y.Z.md` is on the branch and `python3 scripts/verify-release-docs.py --tag vX.Y.Z` passes
- RELEASE VERDICT Status: <PASS | CONDITIONAL_PASS | FAIL>

Highlights, breaking changes and the changelog live in that document, not in this description.

## Pre-merge checklist
- [ ] All CI checks green on `release/vX.Y.Z`
- [ ] The `develop` MR of this release is merged (merge commit, no squash)
- [ ] `Latest release: vX.Y.Z` is set in every file `scripts/verify-release-docs.py` checks, and `python3 scripts/check-version-consistency.py` passes
- [ ] No `WIP` / `TODO` / `FIXME` introduced by this release
- [ ] Wiki updated if user-facing behaviour changed (`docs/wiki/`)

## Post-merge actions
After this MR merges to `main`, tag the release branch's tip (`CONTRIBUTING.md` § Releasing, step 7).
There is no direct push to `develop`.

The tag push triggers the `release` stage of `.gitlab-ci.yml`, which:
1. Checks the release document, the markers and the `main`/`develop` drift
2. Publishes `docs/releases/vX.Y.Z.md` as the GitLab Release description
3. Regenerates `CHANGELOG.md` as a job artifact (it is not committed)

/label ~"release"
````

**H-B3 `implementation/knowledge/agents/orchestrator.md:140-141`.**

````
Before:
   - Tag creation happens AFTER MR is merged to develop
   - Never tag ahead of a commit; ensure tag commit is already in origin/develop

After:
   - The release branch is merged to `develop` first and to `main` second, by merge request and without squash; tag creation happens AFTER both merges, because the drift gate fails a tag push while `main` is ahead of `develop`
   - Never tag ahead of a commit; ensure the tag commit is already in origin/develop and in origin/main
````

**H-B4 `implementation/knowledge/agents/release-manager.md`, two fences.**

````
Before (:29-34):
3. **Release**
   - Merge release branch to `main`
   - Create Git tag: `vX.Y.Z`
   - Create GitLab release with changelog
   - Merge back to `develop`
   - Announce release

After:
3. **Release**
   - Merge release branch to `develop`, then to `main` (merge requests, no squash)
   - Create Git tag: `vX.Y.Z` on the release branch tip, which both branches now contain, only after both merges (the drift gate fails a tag push while `main` is ahead of `develop`)
   - Create the GitLab release from `docs/releases/vX.Y.Z.md`
   - Announce release
````

````
Before (:145-151):
### Release
- [ ] Release branch merged to main
- [ ] Git tag created (vX.Y.Z)
- [ ] GitLab release created with changelog
- [ ] Production deployment successful
- [ ] Health checks passing
- [ ] Release branch merged back to develop

After:
### Release
- [ ] Release branch merged to develop
- [ ] Release branch merged to main
- [ ] Git tag created (vX.Y.Z), after both merges
- [ ] GitLab release created from `docs/releases/vX.Y.Z.md`
- [ ] Production deployment successful
- [ ] Health checks passing
````

**H-B5 `implementation/knowledge/skills/release-workflow/SKILL.md:187-195`** (hotfix steps 5 and 6).

````
Before:
5. RELEASE
   ├── Increment PATCH version: v1.2.0 → v1.2.1
   ├── Generate hotfix changelog entry
   ├── Create release artifact
   └── Deploy

6. MERGE BACK
   ├── Merge hotfix branch into main
   └── Ensure the fix is included in future releases

After:
5. RELEASE PREPARATION
   ├── Increment PATCH version: v1.2.0 → v1.2.1
   ├── Generate hotfix changelog entry
   └── Create release artifact

6. MERGE, TAG, DEPLOY
   ├── Merge the hotfix branch into develop, then into main (merge requests), so the fix is included in future releases
   ├── Tag the hotfix branch tip, after both merges
   └── Deploy
````

**H-B6 two wording edits outside the knowledge tree.**

````
Before (README.md:289):
release/*    ← stabilize a release, MR to main + back-merge to develop

After:
release/*    ← stabilize a release, MR to develop, then to main, then tag
````

````
Before (docs/wiki/contributing-workflow.md:21-22):
release/*    ← from develop, MR to main + back-merge to develop
hotfix/*     ← from main, MR to main + back-merge to develop

After:
release/*    ← from develop, MR to develop, then to main, then tag
hotfix/*     ← from main, MR to develop, then to main, then tag
````

**H-B7 (optional, comment only) `scripts/check-main-develop-drift.py:23-24`.** No behaviour changes; `GRACE_RELEASES = 1` stays.

````
Before:
GRACE_RELEASES = 1  # main may lag develop by up to 1 release (the normal window between
                     # develop's tag and the release/*->main sync MR) before this is drift.

After:
GRACE_RELEASES = 1  # main may lag develop by up to 1 release (a tolerance, e.g. a release whose
                     # main MR is delayed; the normal order merges both before the tag) before this is drift.
````

### 7.3 Group C (the body), recommended C3

**H-C1 `CONTRIBUTING.md:198-200`** (step 8 bullets), written for C3. Lines `:196-197` (the `release-docs-gate` and implementation-surface bullets) and `:202-208` (manual repair) stay as they are.

````
Before:
   - Embeds **Install + Highlights** from `docs/releases/vX.Y.Z.md` in GitLab Release notes
   - Appends a **Changelog** section from Conventional Commits since the previous tag (full git history; `GIT_DEPTH: 0` on release job)
   - Regenerates [`CHANGELOG.md`](CHANGELOG.md) and creates a [GitLab Release](https://gitlab.com/em-age/emage.code/-/releases)

After:
   - Publishes `docs/releases/vX.Y.Z.md`, whole, as the GitLab Release description (the same text the `glab release create ... -F` command below publishes; the body starts with `# Release vX.Y.Z`)
   - Regenerates [`CHANGELOG.md`](CHANGELOG.md) as a job artifact (not committed) from Conventional Commits since the previous tag, merge commits excluded (full git history; `GIT_DEPTH: 0` on release job)
   - Creates the [GitLab Release](https://gitlab.com/em-age/emage.code/-/releases)
````

No fence is held for `scripts/publish-release.py`, `scripts/dry-run-publish-release.py` or `tests/functional/test_publish_release.py`: the code change is a design, specified in §6.2 and scoped as follows for an implementation task. C3: `render_release_description` returns `# Release <tag>` and the document only; `main` builds the generated section separately and passes it to `update_changelog`; `update_changelog` keeps `###` group headings (O-1); `get_commit_subjects` gains `--no-merges` (F1); `dry-run-publish-release.py:154` prints the CHANGELOG.md head instead of the text after the last `---`; `test_publish_release.py:114` becomes an assertion that the description equals `# Release <tag>` plus the document and contains no generated section, with one new test that the log call carries `--no-merges`. The module docstring (`:4-7`) changes with it.

### 7.4 What changes if the user answers differently

| Answer | Change to the held text |
|---|---|
| A2 (tighten the gate) | add a version-gated check to `verify-release-docs.py` for tags at or after v8.0.0 requiring `## Summary`, `## Changelog`, `## Known Issues`, `## Gate Verdicts`, `## Rollback Plan` (not `## Migration Guide`, which the skill makes conditional); a test; H-A4 states the requirement. Older tags are unaffected by the version gate (they already fail on `## RELEASE VERDICT`, audit C-2) |
| A3 (no amendment) | none of H-A1 to H-A5; v8.0.0 is written to §4 only; audit C-2 stays open as a documented difference |
| B2 | H-B1 step 7: tag `origin/main` instead of `origin/main^2`, and add a step 8 `main -> develop` MR (content-empty, for ancestry and `git describe`); H-B3 second bullet: "ensure the tag commit is already in origin/main and its content in origin/develop"; H-B4: "on `main`" |
| B3 | H-B1 steps 5-7 reordered (tag the `develop` merge commit, then the `main` MR); H-B2 post-merge text; H-B3 second bullet unchanged; H-B4 and H-B5 reordered; H-B1 grace paragraph kept as the normal state |
| B4 | not specified: it changes a check; a separate ruling would be needed |
| C1 | H-C1 becomes "Publishes the whole document, then appends a Changelog section of commit subjects"; H-A1 intro likewise; H-A2 and `orchestrator.md:133-134` say the manual path publishes the file only and the CI body adds the list |
| C2 | as C1 plus: the generated section is renamed (for example `## Commits since <previous tag>`), filter F1 (and F2 if chosen); `test_publish_release.py:114` follows the new heading |
| C4 | not recommended; a section extractor and fixed headings would be specified in a v2 of this ruling |

## 8. Hit counts, projected paths, coupling, grants

### 8.1 Hit counts (by reading, fixed strings; **(unverified by grep)**)

Scope: per file, lines / occurrences, before and after the recommended set (A1, B1, C3).

| # | File | Phrase | Before | After | Edit |
|---|---|---|---|---|---|
| 1 | `agents/orchestrator.md` | `File must include:` | 1 / 1 | **0 / 0** | H-A2 |
| 2 | same | `## RELEASE VERDICT` | 0 / 0 | 1 / 1 | H-A2 |
| 3 | same | `Tag creation happens AFTER MR is merged to develop` | 1 / 1 | **0 / 0** | H-B3 |
| 4 | same | `ensure tag commit is already in origin/develop` | 1 / 1 | **0 / 0** | H-B3 |
| 5 | same | `Publish/update release notes from that file only` (`:133`) | 1 / 1 | 1 / 1 | unchanged |
| 6 | `agents/release-manager.md` | `Merge back to \`develop\`` | 1 / 1 | **0 / 0** | H-B4 |
| 7 | same | `Release branch merged back to develop` | 1 / 1 | **0 / 0** | H-B4 |
| 8 | same | `GitLab release with changelog` / `GitLab release created with changelog` | 2 / 2 | **0 / 0** | H-B4 |
| 9 | same | `Merge to \`main\` AND \`develop\`` (hotfix, `:40`) | 1 / 1 | 1 / 1 | unchanged (already "both") |
| 10 | `skills/release-workflow/SKILL.md` | `6. MERGE BACK` | 1 / 1 | **0 / 0** | H-B5 |
| 11 | same | `from \`## Summary\` on` (`:131`) | 1 / 1 | 1 / 1 (sentence extended) | H-A3 |
| 12 | same | `# Release v<VERSION>` | 0 / 0 | 1 / 1 | H-A3 |
| 13 | `CONTRIBUTING.md` | `git checkout develop && git merge --no-ff main && git push` | 1 / 1 | **0 / 0** | H-B1 |
| 14 | same | `back-merge` | 2 / 2 (`:193`, `:295`) | 1 / 1 (the sentence "There is no separate back-merge") | H-B1 |
| 15 | same | `Embeds **Install + Highlights**` | 1 / 1 | **0 / 0** | H-C1 |
| 16 | same | `release-docs-gate` and `verify-release-docs.py` (gate-required snippets) | present | present | untouched (`:196`, `:162`) |
| 17 | `.gitlab/merge_request_templates/Release.md` | `git checkout develop && git merge --no-ff main && git push`; `git-cliff`; `unversioned in source`; `updated and committed` | 1 / 1 each | **0 / 0** each | H-B2 |
| 18 | `docs/releases/_template.md` | `Claude Code`, `Cline` | 0 / 0 | 1 / 1 each | H-A1 |
| 19 | same | `Always include` (manual-copy block) | 1 / 1 | **0 / 0** | H-A1 |
| 20 | same | `## Summary`, `## Migration Guide`, `## Known Issues`, `## Gate Verdicts`, `## Rollback Plan`, `## Changelog` | 0 / 0 each | 1 / 1 each | H-A1 |
| 21 | same | `## Install`, `## Highlights`, `## RELEASE VERDICT` (gate snippets) | 1 / 1 each | 1 / 1 each | kept |
| 22 | `README.md` | `Install + Highlights` | 1 / 1 | **0 / 0** | H-A5 |
| 23 | same | `back-merge to develop` | 1 / 1 | **0 / 0** | H-B6 |
| 24 | `docs/wiki/README.md` | `Install + Highlights` | 1 / 1 | **0 / 0** | H-A5 |
| 25 | `docs/wiki/contributing-workflow.md` | `back-merge to develop` | 2 / 2 | **0 / 0** | H-B6 |

Gate-required strings in the edited files stay present (`verify-release-docs.py:41-91`): README `docs/releases/`; CONTRIBUTING `## Releasing`, `### Cutting a release`, `release-docs-gate`, `verify-release-docs.py`; wiki README `## Release documentation contract`.

### 8.2 Projected paths and root drift

Edited knowledge files: 3 (`agents/orchestrator.md`, `agents/release-manager.md`, `skills/release-workflow/SKILL.md`). `commands/prepare-release.md` stays **byte-unchanged**.

| Source | Projected paths under `implementation/` | Root-drift paths | Basis |
|---|---|---|---|
| `orchestrator.md` | 6: `.claude/agents/orchestrator.md`, `.github/agents/orchestrator.agent.md`, `.cursor/agents/orchestrator.mdc`, `.gemini/agents/orchestrator.md`, `.opencode/agents/orchestrator.md`, `.pi/agents/orchestrator.md` | 6 | `.claude`, `.github`, `.gemini`, `.opencode`, `.pi` read; `.cursor` by the tool's file hint; Cline has no `agents/orchestrator.md` under `.cline/` or `.clinerules/`; whether it holds the agent under another name is **(unverified)** |
| `release-manager.md` | 6 (same layout) | 6 | **(unverified: not read)** |
| `release-workflow/SKILL.md` | 7: `.claude`, `.github`, `.cursor`, `.gemini`, `.opencode`, `.pi`, `.cline` under `skills/release-workflow/SKILL.md` | 7 | all seven read under `implementation/`; root counterpart read for `.claude` only |
| Registry | `implementation/registry/index.json` (3 checksums); `summary.md` unchanged (no maturity change) | n/a | **(I)** |

Total: **19** projected and about **19** root-drift paths for the recommended set; with only group A (orchestrator + skill) 13 and 13. The authoritative list is `node implementation/scripts/sync.mjs --print-drift` after the edits; declare exactly that. Docs-tree edits (CONTRIBUTING, Release template, `_template.md`, README, wiki, the script comment) have no projection and no root drift. **No root refresh is requested by this ruling.**

### 8.3 Coupling (open cases only; held-out coupling is unknown and not checked)

| Surface | Coupling | Effect |
|---|---|---|
| `prepare-release-real-verdict-missing` (open) | `check()` reads `fixture/docs/checkpoints` today and `fixture/docs/releases` after G-1 item 3; the fixture is a frozen copy | none from the edits above (no fixture or `expect.py` changes); §4.3 rules 1-2 keep the later v8.0.0 copy satisfiable |
| `prepare-release-conditional-pass-conditions-gap` (open) | `case.yaml` only read; `known_failing`, `capability_gap` | none |
| Other open cases | not searched for quotes of the changed lines **(unverified)**; the T622 and T595 plans list the cases that quote knowledge text, and none is named for release text | none expected |
| `tests/functional/test_publish_release.py` | line 114 and the git-call shape (F21) | only under C2, C3, C4 (§7.3) |
| `tests/functional/test_check_main_develop_drift.py` | tests the pure functions; no behaviour changes | none (H-B7 is a comment) |
| Tests that read the template, CONTRIBUTING, the preflight or the skill | could not be enumerated | **(unverified)**; the implementer runs the full suite and stops on a failure rather than editing a test to pass (as in T595) |
| `verify-release-docs.py` on `_template.md` | required file; link-checked; no links in the new text | pass **(unverified: not run)** |

### 8.4 Grants and baselines

**None.** No edit touches `tests/golden/**` or `scripts/scorecard.py`; no `evaluator-hash-known-good` change; no criterion, checker or schema change. The later G-2 and baseline v22 are already planned in `promotion-and-golden-realignment-plan-v1.md` §6.4 and are not requested here. Other tasks that touch the same files and may collide: T624 (five knowledge files; which ones is **(unverified)**) and T631 (`README.md`, `docs/wiki/*`); apply by Before text after they merge.

### 8.5 Per-edit statements

- **Upward edits (a tier-1 file changed to match a lower document):** none.
- **Command changes:** none. `/prepare-release` stays unchanged; nothing is amended on the strength of a skill or agent (ADR-008 P2).
- **Checks relaxed:** none. The gate is unchanged under A1; A2 would tighten it.
- **Security:** no security-relevant text. Any C2/C3/C4 code change touches `publish-release.py`, which holds a token and carries hardening from the T619 review (`validate_tag`, `--end-of-options`); that diff needs the same Tech Lead and Security Engineer look.
- **Maturity:** not relied on; no maturity changes; `check-maturity.py` unaffected.

## 9. Consolidated user question (one round)

**Subject.** v8.0.0 needs one release document that three gates and four documents can agree on, a tag order the drift gate accepts, and a GitLab Release body that does not contradict the document. The facts decide the content (A) only up to a choice about the gate, and decide nothing about the order (B) or the body (C): two peer agents disagree, and the body is a design question. Nothing is applied until you answer; implementation follows as a separate task.

### Group A. The release document

| Option | What happens | Consequences |
|---|---|---|
| **A1. One union contract (Recommended)** | `docs/releases/v8.0.0.md` carries the 11 sections of §4.2. `/prepare-release` governs the verdict block and changelog group names; the skill supplies the other sections; the gate stays unchanged. The template, the orchestrator preflight, CONTRIBUTING step 3 and two wording lines are corrected (H-A1 to H-A5) | Removes the audit C-2 differences without changing any check or command. Knowledge edits in two files; a root drift of about 13 paths |
| A2. A1, and tighten the gate | As A1, and `verify-release-docs.py` also requires the skill's sections for tags at or after v8.0.0 | The gate matches the skill, and a missing Summary or Rollback Plan fails the tag. A script and test change; ties the gate to section names |
| A3. Write v8.0.0 to §4, amend nothing | Only the document is composed | Fastest. The template still omits Claude Code and Cline, the preflight still omits the verdict, the title ambiguity stays; audit C-2 is left open |

**Recommendation: A1.** It is the smallest change that makes the documents agree, and it leaves every check as strict as it is.

### Group B. Tag and merge order

| Option | What happens | Consequences |
|---|---|---|
| **B1. Merge to `develop`, then `main`, then tag the release-branch tip (Recommended)** | The drift gate sees equal markers; no direct push and no back-merge after the tag. Same order for hotfixes. Edits H-B1 to H-B6 | One commit is the tag on `main` and in `develop`. CONTRIBUTING, the Release template, `release-manager`, the preflight and the skill's hotfix steps change. Before the tag, `develop` shows the new marker and the informational check warns |
| B2. As B1, tag the merge commit on `main` | Tag where it has always been | The tag is not in `develop` unless a content-empty `main -> develop` MR follows; the preflight line "tag commit already in origin/develop" must change |
| B3. Tag `develop` first, `main` MR afterwards | Uses the gate's grace window as the normal path | The tag is not on `main`; more documents change; a second release before the `main` MR lands fails the gate |
| B4. Keep the current order and change the gate | The gate stops failing on "main ahead" | Removes an invariant; a separate ruling; not recommended |

**Recommendation: B1.** It is the only order in which the gate passes with zero grace, the protected-branch rule is respected, and the preflight and the Release template stay true.

### Group C. The GitLab Release body (design)

| Option | What happens | Consequences |
|---|---|---|
| C1. Keep | Whole document plus the unfiltered commit list | Two `## Changelog` headings and about 201 merge-commit lines under "Other"; the manual repair command publishes a different body. Text edits only |
| C2. Filter | Add `--no-merges`; rename the appended heading | Useful list, still a second source; the manual path still differs. Script and test change |
| **C3. Document only (Recommended)** | The body is the document, the same on every path; the filtered commit list goes to `CHANGELOG.md` only | Loses the commit list on the release page; consistent with "one release document". Script, dry-run and test change; security-reviewed script, so a review is needed |
| C4. Excerpt | Install + Highlights + Breaking changes + link, plus the filtered list | New extractor code; two sources of truth. Not recommended |

**Recommendation: C3.**

**Default if you accept all recommendations: A1 + B1 + C3.** If you pick another C option, §7.4 lists the sentences that change; no new decision is needed.

## 10. Handoff packages

### IMPL-1 (provisional id; the orchestrator assigns the real `T`-id and declares `**Affects:** —`)

- **task_id:** to be assigned (suggested owner: `backend-developer`, shell needed for sync and registry).
- **definition:** apply the user's answers to groups A and B: the fences of §7.1 and §7.2 (with §7.4 deltas for non-recommended answers), then regenerate and verify.
- **constraints:** apply each Before exactly once; stop on a missing or non-unique anchor; `commands/prepare-release.md`, `AGENTS.md`, every instruction, `scripts/verify-release-docs.py` (unless A2), `.gitlab-ci.yml` and `tests/golden/**` byte-unchanged; no maturity change; no test edited to pass; keep gate-required strings (§8.1 note); run `python3 -m unittest tests.functional.test_golden_held_out_isolation` and the full suite to a file.
- **depends_on:** the user's answer to §9; T624 merged (re-anchor by Before text if it touched `orchestrator.md` or the skill); coordinate with T631 on `README.md` and `docs/wiki/*`.
- **input_artifacts:** `release-documents-ruling-v1.md` (this file), `release-v8-audit-v1.md`, `path-conventions-v3.md`.
- **expected_outputs:** edited files; `sync.mjs --check` and `generate-registry.py --check` clean; root drift declared exactly as `--print-drift` reports; a report with before and after counts of §8.1.
- **blocker_policy:** report type and severity per `AGENTS.md` § Blocker Protocol; a failing test that encodes the old text is a `dependency`/`major` blocker to the orchestrator, not an edit.

### IMPL-2 (only if the user picks C2, C3 or C4)

- **definition:** change `publish-release.py`, `dry-run-publish-release.py` and `test_publish_release.py` as specified in §6.2 and §7.3; apply H-C1 (or its §7.4 variant).
- **constraints:** keep `validate_tag`, `--end-of-options`, the fail-closed empty-document and no-commits behaviour, the artifact list `["CHANGELOG.md"]`, and the `release` job's `needs`; add a test for the log call's `--no-merges`; a Tech Lead and Security Engineer review of the diff.
- **depends_on:** the user's answer to group C; IMPL-1 for the shared text.
- **expected_outputs:** green suite; dry-run for `v7.0.1` passes (`test_dry_run_against_real_release_document` still reads `docs/releases/v7.0.1.md`).

### WAVE-3 note (not a task here)

`docs/releases/v8.0.0.md` is written by the release manager on the release branch to §4.2 and §4.3, after `release-v8-audit-v2.md`. The tag follows §5.3 once the user approves each outward-facing step (plan-121 Open Question 5).

## 11. Summary

| ID | Disagreement | Disposition | Authority / step | Held edit | Needs the user |
|---|---|---|---|---|---|
| RD-1 | Required sections: gate, skill § 4, preflight, template | Union; no conflict | A; P2 for the verdict; gate is the floor | H-A1, H-A2, H-A4, H-A5 | Group A |
| RD-2 | First line: skill block, template, v7 notes, strip rule | `# Release v<VERSION>` | A (skill's own "from Summary on") | H-A3 | Group A |
| RD-3 | Changelog groups: command 4, skill 6, CI 10 | Command's names inside the document; skill scoped | C (P2) | H-A3 | Group A |
| RD-4 | Install table and manual copy stale | Installer defines; all 8 values; manual block removed | fact (F8) | H-A1 | Group A |
| RD-5 | Heading name, verdict counts, one verdict heading | `## Migration Guide`; counts equal listed entries | skill § 4; composition rules | none | Group A (recorded) |
| RD-6 | Back-merge by direct push vs protected branches | Removed under every option | P1 by analogy (`git-workflow.md`) | H-B1, H-B2 | Group B |
| RD-7 | Tag order: CONTRIBUTING / `release-manager` vs `orchestrator` vs drift gate | Escalated; recommend merge `develop`, merge `main`, tag the tip | E (P5), blocker `unclear_requirements`/`major` | H-B1 to H-B7 | Group B |
| RD-8 | Hotfix order | Same as RD-7 | follows RD-7 | H-B1, H-B5 | Group B |
| RD-9 | Body: whole document, "Install + Highlights", "from that file only", duplicate `## Changelog`, merge-commit noise | Design question; recommend document-only body | design | H-C1; code per §7.3 | Group C |
| RD-10 | Release MR template: committed `CHANGELOG.md`, `git-cliff`, "unversioned", duplicated notes | Rebuilt | follows RD-1, RD-7 | H-B2 | with A and B |

**Observations parked (no decision here).** O-1: `CHANGELOG.md` entries lose group headings (`publish-release.py:214-217`). O-2: installed knowledge text cites authoring-only paths (audit K-6); the new text adds none beyond those already cited. O-3: `implementation/README.md:23-29` and the audit's other install copies carry a manual-copy block that may have drifted. O-4: `docs/wiki/contributing-workflow.md` still points at `v2/` paths. O-5: `docs/wiki/implementation-guide.md:35` lists five projections.

## 12. Not verified, and blockers

**Not verified.**
1. Nothing was run: no shell, no `grep`, no `git`, no tests. All counts are from reading; the worktree commit is as stated by the orchestrator.
2. The v7.0.1 drift-gate outcome and the order in which it ran (no CI log).
3. `verify-main-sync-merge.py` (read only as described in CONTRIBUTING) and whether it accepts a `develop` MR record; the MR record field that holds the source head; `git rev-parse origin/main^2` on a real merge.
4. `release-manager.md` projection paths; the Cline projection of the agents; root counterparts other than `.claude/skills`.
5. Tests that read the template, CONTRIBUTING, the skill or the preflight; open golden cases that quote them.
6. The current GitLab description limit; how the release page renders a second H1 and relative links.
7. The audit's counts (411, 201, 128, ...), quoted from `release-v8-audit-v1.md`.
8. Any held-out coupling: `tests/golden/held-out/` was not opened and is unknown.

**Blockers.**
- `unclear_requirements` / `major`: the order of the tag and the merges (RD-7) is a peer conflict that ADR-008 sends to the user (§9 group B). It blocks the v8.0.0 tag, not this task.
- `dependency` / `minor`: T624 and T631 may touch the same files; apply by Before text after they merge.
- None for this deliverable.
