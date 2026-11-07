# Artifact: tech-lead-release-v10-v1.md

> Immutable once produced; a revision is `tech-lead-release-v10-v2.md`.

## Metadata

- **Executor**: tech-lead, read-only review mode. No source or release file was changed. Only this file was written. Worktree branch `agent/tech-lead/T761`.
- **Gate**: code review by area (T761), the `validation-gates` Implementation gate for the release. **Date**: 2026-11-07.
- **Target**: `release/v10.0.0` at `3641abfb`; range `v9.0.0..3641abfb` (392 files, +20801 / -1175).
- **Based on**: `docs/tasks/task-T761.md`; `docs/plans/plan-145-release-v10.md`; `docs/releases/v10.0.0.md`; `docs/artifacts/release-v10-audit-v1.md`; `docs/artifacts/tracked-debt-register-v11.md` (§ 6.2, § 6.3); `docs/artifacts/release-rehearsal-t759-v1.md`; `docs/artifacts/code-review-release-v9-v1.md` (shape only). No `requirements-vN.md` or `architecture-vN.md` applies to this release; the plan and the audit are the inputs.
- **Decision IDs referenced**: ADR-011, ADR-012.
- **Basis marker**: **(V)** read or run here. **(read)** read, not run. **(unverified)** neither.

## Verdict: CONDITIONAL_PASS

No finding blocks the release on code. The installer, the generator, the CI file and the release script are sound as far as they can be proved before a tag. The release document is honest and its citations hold. Three short text edits and one ordering rule are needed before the independent check at T763 (section "Before the tag"). The other findings are LOW and can be tracked.

| Area | Result |
|---|---|
| 1. Installer and generator | PASS |
| 2. Knowledge text and rulings | PASS, with TL-T761-04 and TL-T761-10 |
| 3. CI and the release job | PASS, with the unproved lines below |
| 4. The release document | CONDITIONAL_PASS |
| 5. Register v11 § 6.2 | PASS, table below |

## What was run

- `python3 -m unittest` on `test_ci_hash_pins`, `test_run_allowlisted`, `test_install_command_audience`, `test_publish_release_t730`, under `timeout`: 151 tests, OK (V). Not the full suite: that is T760's.
- An install of this tree with `--platform claude-code` into a throwaway git repository with `origin` `https://example.invalid/acme/widget.git` (rc 0), since deleted. **M-2's rebuild command, as printed, in that target: rc 0** (`wrote 0 chunks`, because the target holds no memory entries). No index was built by T753, so this is new evidence.
- `build_server` called with `default_index_dir` in that target (V): it starts with that index; `FileNotFoundError` on `_index/acme-widget/manifest.json` when the directory is renamed away; a remote `git@...:Group/Sub/Widget.git` gives `_index/sub-widget`.
- `scripts/check-maturity.py` (V): the skill and instruction counts of K-1 hold. No mutation, no `docker`, no push.

## Area 1. Installer and generator: PASS

Sampled: the whole `scripts/install.sh` diff; the added function names of `sync.mjs` (`commandAudience`, `assertMcpOutputFile`, `assertMcpFilesApart`, `withEmittedMcpTools`), not their bodies; each manifest's `authoringOnly`.

- **T725, the audience filter (V).** 19 commands: 18 `both`, 1 `authoring`. The five manifests name the five paths of M-1, and `.cline` names none. `.clinerules` has no manifest, and `authoring_only_paths` returns nothing for it.
- **The deletion path (read).** `withhold_authoring_only` removes after the copy, as its comment explains: an rsync `--exclude` would protect a stale copy. Each entry is held to `[A-Za-z0-9._-]+(/...)*` with no `..`, `refuse_unsafe_path` runs before the `rm -f --`, and the removal goes through `run`, so a dry run prints it. `verify_authoring_only_lists` stops a bad list before the first write. An authoring checkout is told by `implementation/registry/index.json`, the rule `/discover-skills` uses.
- **T722 (V).** No generated config holds `--index-dir` (root configs grepped). `install_mcp_server_runtime` excludes `_index`, so a v9 index survives `--update` and can be moved or rebuilt beside it. `default_index_dir` refuses a slug outside `[a-z0-9._-]`.
- **T723 (read).** `printable` delegates to `ascii_printable`, and the usage text no longer needs a command substitution. The Cursor lines are one case per line.

## Area 2. Knowledge text and rulings: PASS

Sampled: ADR-012's decision and consequences; `agents/release-manager.md:46, 183`; `validation-gates/SKILL.md:70`; `commands/prepare-release.md` step list; `CONTRIBUTING.md` § Cutting a release and the first-tag rehearsal. Batch H's other text was not re-read **(unverified)**.

Does the text match how this release is run?

- **Merge order: yes.** Plan-145 T764, `CONTRIBUTING.md` step 5 and `release-manager.md:30-31` all say `develop` first, then `main`, no squash, then the tag on the release branch tip.
- **Who checks: yes.** `release-manager.md:46` names the `tech-lead` review by area, and T763 names `@tech-lead`. This review edits no release file, so it does not disqualify me.
- **The release checkpoint: yes.** `/prepare-release` step 6 holds it, as T764 says.
- **The closed list: a trap, TL-T761-04.**
- **ADR-012 and the passed deadlines: fair.** The release document's sentence (line 195) says the rules do not say whether a new acceptance cures a passed deadline. ADR-012 says a passed deadline "counts as moved later", and that moving later "needs the user's new acceptance", so a reader could take the new acceptance as the rule's answer. Stating it as open is the cautious reading, and it is the one the user was shown. No change.
- **"Fix: none possible": TL-T761-10.**

## Area 3. CI and the release job: PASS

Read in full: `.gitlab-ci.yml`, `scripts/run-allowlisted.py`. Read in part: `scripts/publish-release.py` (`main`, the outline, the child environment). Not read beyond the suite passing: most of `tests/functional/test_ci_hash_pins.py`.

- **`scripts/run-allowlisted.py` (§ 6.2 item 26): sound.** `os.execvpe` keeps pid, signals and exit code. `--keep` is checked against a name pattern. An empty secret is ignored, so it cannot match every value. The message names the command only. It does what its docstring says and claims no more.
- **Job list and rules.** No job was added or removed since v9.0.0 (V, diff). Outside the three tag jobs, every rule is false on a tag (V, read). No tag job has `allow_failure` (V, read and test).
- **The digest.** Eight `python:3.12-alpine` lines, one digest (V). `git~=2.54` resolves on Alpine 3.24.4 (T759).
- **Failure mode.** Every tag job fails closed. The script writes `CHANGELOG.md` before the API call (T759 s5), and a failed job uploads no artifact by default (read, GitLab's default on_success).

### The unproved lines of the tag jobs

Nothing below is expected to fail on what I read. Each one has run nowhere that would prove it. "Probe" is `v9.0.0-gate.2`, pipeline 3038460622, which used the earlier digest.

| Line | Text | Proved so far | Not proved |
|---|---|---|---|
| `.gitlab-ci.yml:206` | `timeout: 10 minutes` | Parsed by the probe | Never reached; a runner's lower limit would win |
| `:208`, `:228`, `:251` | `GIT_STRATEGY: clone` | The gates, in the probe | **`release`: never run.** A project variable of that name would beat it (§ 6.2 item 21) |
| `:214` | `rm -rf .git "${CI_PROJECT_DIR}.tmp"` | Ran, and cleanup showed no error | That it hit the right path, on source reading only (K-30). The flag `FF_GIT_URLS_WITHOUT_TOKENS` on this runner is unknown |
| `:216` | pip through the wrapper | Probe, earlier digest | **On the new digest, in a job.** The install is quiet, so the version rests on the hashes |
| `:218` | the gate through the wrapper | Probe, with a copy of v9.0.0's document | **The real v10.0.0 document with its verdict filled, in a job.** T760 runs it locally |
| `:234` | `apk add` through the wrapper | Probe, earlier digest | New digest in this job. T759 ran the same package under `release`'s line |
| `:236-237` | the fetches with `--keep CI_JOB_TOKEN` | Ran; the project is public, so perhaps anonymously | That the credential is needed or works |
| `:238` | the drift check through the wrapper | Probe, on the probe's own state | A real `main` and `develop` after this release's merges |
| `:240` | the tag tree check through the wrapper | **Only its refusal, in the probe, by design.** At v9.0.0 it passed, without the wrapper | **Its passing path under the wrapper** |
| `:253` | `release`'s `before_script` | Verbatim in T759; in v9.0.0's job on the old digest | Real network path on the new digest |
| `:258` | `publish-release.py` | Verbatim in T759 against a double, no stub | **All of it against real GitLab:** this code, `git fetch --tags --force` with the real clone credential, the job token on `GET` and `POST` releases, TLS to GitLab from the new image's bundle, the real commit range's escaping, and how GitLab renders it |
| `publish-release.py:755` | `git fetch` with `CI_JOB_TOKEN` withheld | At v9.0.0, on a default-strategy checkout | **With the flag on, this fetch has no credential:** the gate's comment (`:231-233`) says the helper reads that variable, and `release` withholds it. It works while the project is public. TL-T761-11 |
| `:259-262` | the `CHANGELOG.md` artifact | At v9.0.0, with the old insert | The entry below `[Unreleased]` in the real artifact (§ 6.2 items 6, 14) |

**Why I do not expect a surprise.** The docs gate needs no git: the image has none. Under `clone` in one volume the next job re-clones, so the removal does not reach `release`. Both the helper and the job run as root, so git's ownership check does not bite (read, not observed under `clone` in `release`). The tag regex takes `v10.0.0`, the sort is numeric, and T759 got `_Commits since v9.0.0._` with the gate tags present.

**A rule for T764.** Nothing may land on `main` between the tag and the end of `main-develop-drift-gate`: line 240 compares the tag's tree with `origin/main` (TL-T761-12). `develop` may move: the drift check at line 238 compares the `README.md` markers (`scripts/check-main-develop-drift.py`, docstring), so the release checkpoint on `develop` does no harm. The list at `CONTRIBUTING.md:279-292` does not say so; the orchestrator should hold it.

## Area 4. The release document, read as a reader from v9: CONDITIONAL_PASS

**Migration items.**

- **M-1 (V):** the correction is in, in full, and matches the audit. **M-2's warning (V):** at the top of the guide, in the Summary, and in M-2. M-3's own note repeats the point for `implementation/runtime/`.
- **Order.** Before, then update, then after is right, with one gap: **TL-T761-01**. M-3's check comes before, and its action after, which is correct.
- **M-2's command (V):** it is exactly what `scripts/install.sh:1745-1747` prints, it exits 0, and the server starts on the result. Two reader traps remain: TL-T761-02 and TL-T761-06.
- **`--projections-only`.** The release document is firm, but `README.md:144-147` and `docs/wiki/implementation-guide.md:36` offer that mode with no warning: **TL-T761-03**.
- **The rollback (read):** consistent with M-1 to M-3, and it says what was observed and what was not.

**Placeholders, by eye (§ 6.2 item 27; SEC-T751-09).** Every angle-bracket token in the document, by line:

| Token | Lines | Reading |
|---|---|---|
| `<your-project>`, `<name>` | 16, 65, 281 | The reader's value, in a command. Line 140 is a literal example of the rule |
| `<emage.code clone>` | 63 | The reader's value |
| `<org>`, `<repo>` | 87, 93, 94, 284 | The reader's value |
| `<path>` | 125, 126 | An option's value |
| `<server>` | 121 | Literal generator pattern, `mcp__<server>__` |
| `<!-- x -->` | 137 | Literal, in a code span, describing the rule |

**None is an unfilled template placeholder.** No `[list ...]`, `YYYY-MM-DD`, `vX.Y.Z`, `TBD` or `TODO` is left. `pending` appears in lines 251-255 and 263-270, 272-274, which are the deliberate values, and in line 217, prose about an italic `pending` in K-31, which is not a value. The template's pointer sentence (`_template.md:90`) is gone, so § 6.2 item 10 is settled. Line 260, "fill in every field before the tag is cut", is the template's and will be published: harmless, and it may go at T763, as the opening paragraph is on the closed list.

**Known Issues.**

- **The accepted MEDIUMs (read):** K-15, K-16 (two ids), K-28 and K-29 each say in bold what can go wrong, then give owner, fix and date, and match the plan's table. The five agree with line 41.
- **"Mitigated":** one use in the document, line 197, as "mitigated, not closed" (V).
- **TD-T697-07:** line 202 says it is not an acceptance, and neither accepted nor renewed (V).
- **Tag pipeline and `release` job:** K-30 and K-34 claim nothing beyond what happened. K-26's closure is v9.0.0's only. X-06 says "Rehearsal only". M-7's rendering is **(unverified)**.
- **One soft sentence:** TL-T761-07.

**Citations (V).** `scripts/install.sh:187, 1297-1300, 1301, 1745-1747` hold, and no `install.sh` line names v10. K-33's lines hold on the tree (`orchestrator.md:130, 133, 134`, `verification-before-completion/SKILL.md:85`) and on a target's seeded wiki (`home.md:24`, `README.md:15`). All 68 repository file references in code spans exist; the 8 that do not resolve are target-side or example paths. `CONTRIBUTING.md` § Releasing, § Hotfixes and § Moving or deleting a pushed tag (retag) exist. `CHANGELOG.md` has no diff in the range. `SECURITY.md` § 4.2, `--print-secret` and `dispatch-test-sia.py`'s `--jwt-secret` hold. K-18's counts add up to 596. Not checked: K-29's and K-34's technical claims (T762's), the count of 14 in K-31 **(unverified)**.

## Area 5. Register v11 § 6.2

**The audit's assignments to T761 are marked `*`.** "T763" and "T764" mean that the item is for that later task, and nothing here shows it unmet.

| # | Result at `3641abfb` |
|---|---|
| 1 | Done: M-1, A-01, with the audit's correction in place of the item's advice |
| 2 | Asked and recorded in plan-145; the verdict's record is T763's. The document's K-items match the plan's table |
| 3 | Fields present, `pending`. T763 |
| 4 | Done, citations verified above |
| 5 | Done at T755 (K-28); the orchestrator re-checks at T764 |
| 6 | Rehearsed in T759 (holds); the real artifact is T764's |
| 7* | Done: M-7 carries it. Sampled against the item: the Cursor rule, refused documents, the verdict check. They agree |
| 8 | T764. K-30 states it |
| 9 | T763 |
| 10 | Done: the sentence was removed before the check |
| 11 | T763. See TL-T761-04 |
| 12 | M-8 carries the hotfix text. The closed list is T763's: TL-T761-04 |
| 13 | Settled by the audit; line 72 applies it |
| 14 | T764. K-30 states it |
| 15* | Holds (read, test) |
| 16 | T758, T760: the document's M-7 states it |
| 17 | The lock test passes (V) |
| 18* | Holds: no new job (V) |
| 19* | The bump was made and the test passes. The header gap at `.gitlab-ci.yml:25-28` remains: TL-T761-08 |
| 20 | M-7 states it; T760 runs it |
| 21* | Holds: no new variable in a gate command, and `--keep` names only `CI_JOB_TOKEN`, twice. Project variables are T764's |
| 22, 25 | M-7 states them; T760 runs the gate |
| 23* | Holds: the pin test passes (V), and the line is unchanged |
| 24 | No candidate, no probe, in plan-145 |
| 26* | Reviewed, Area 3 |
| 27* | Done by eye, Area 4 |
| 28 | T764 |
| 29 | Holds for this task |
| 30 | One real `RELEASE VERDICT` heading (line 257). T760 runs it |

**Stale text, known and for register v12 (TL-T761-08):** item 1's advice; § 6.3's note that the test fails after 2027-02-19 (it now fails after 2027-03-06, because `ci_images_reviewed_on` reads 2026-11-06 and the test allows 120 days); plan-145's risk line, the same. SEC-T756-02's deadline of 2027-02-19 stays as shown to the user.

## Findings

Severity is `Important` or `Minor` for the code review, and `LOW` where a tracked debt id is proposed. No security finding is graded here: those are T762's.

| ID | Severity | Location | Finding | Suggested fix | When |
|---|---|---|---|---|---|
| TL-T761-01 | Important | `docs/releases/v10.0.0.md:59` | The ordered steps never say to commit or back up first, though `--update` replaces each platform tree and M-1 shows it deleting a file with no log line. The advice exists only in the Rollback Plan (line 280), which a reader upgrading may not read until too late. **Any file of the reader's own in `.claude/commands/` and the like goes the same way.** Not new in v10, but this list is where it belongs | In step 1, first: "Commit or back up your project, including any file you keep inside a platform tree: `--update` replaces those trees." | Before the tag |
| TL-T761-02 | Important | `docs/releases/v10.0.0.md:89-94` | `--project-id <org>/<repo>`: the document says lower case only of the directory. The server compares `chunk.project_id == context.project_id` exactly (`scope_filter.py:52`), and the context is lower-cased (`context_retriever.py:105`). So `--project-id Acme/Widget` builds an index whose project-scope entries **silently never match** (read, not run). Not new in v10, but M-2 now sends every index owner through this command | After the command: "Use lower case in both values." | Before the tag |
| TL-T761-03 | Important | `README.md:144-147`, `docs/wiki/implementation-guide.md:36` | Both offer `--projections-only` as the refresh, with no word on v9 to v10. A reader who follows the README and not the release document gets a dead `context-retriever`, the failure M-2 warns of | One sentence at each: "Not for an upgrade across a release that changes `implementation/runtime/`, such as v9 to v10: use `--update`." If the user prefers not to touch them, track it; the release document's warning stands | Before the tag, the user's call |
| TL-T761-04 | Important | `implementation/knowledge/agents/release-manager.md:46`; `docs/releases/v10.0.0.md:251-254, 264-266` | **Ordering trap at T763.** The closed list covers only the `Release:` line and some verdict values. `Architecture`, `Implementation`, `Integration`, `Security`, `Features included`, `Fixes included` and `Breaking changes` are not on it, and all are `pending` today. Filling them after the check makes it stale | T763 fills those seven first, then asks for the check on that commit, then changes only the closed list. Plan-145 T763 does not spell this out. **So this review cannot itself be the independent check row:** T763 needs a new one | Before the check |
| TL-T761-05 | Minor | `docs/releases/v10.0.0.md:36` | The Highlight says every install mode deletes it, "and a renamed copy inside a platform tree goes too". M-1 is right: a plain install leaves the renamed copy. It errs on the safe side | "...and `--update` or `--projections-only` also deletes a renamed copy inside a platform tree" | Track, or with the others |
| TL-T761-06 | Minor | `docs/releases/v10.0.0.md:87`, `scripts/install.sh:1747` | `<org>` is the immediate parent. On a GitLab subgroup, `Group/Sub/Widget` gives `_index/sub-widget` (V). The error names the path, so a reader can recover | Add "(on a subgroup, the last two parts of the path)" | Track |
| TL-T761-07 | Minor | `docs/releases/v10.0.0.md:239` | K-18, "Nothing open in it is above LOW", is true of the register's `open` status, and sits below five MEDIUMs that ship unfixed | Add "(the accepted MEDIUMs are under § Accepted for v10.0.0 only)" | Track, or with the others |
| TL-T761-08 | LOW | `docs/artifacts/tracked-debt-register-v11.md:290, 348`; `docs/plans/plan-145-release-v10.md:101`; `.gitlab-ci.yml:25-28` | Stale notes (section above), and the bump recipe still omits the test constants | Carry to register v12. These are immutable records: correct them there | Track |
| TL-T761-09 | Minor | `docs/releases/v10.0.0.md:81` | "Copy it back after each `--update` or `--projections-only`": a plain install also deletes a copy under the original name (line 79) | "after each install" | Track, or with the others |
| TL-T761-10 | LOW | `implementation/knowledge/skills/validation-gates/SKILL.md:70`; `docs/releases/v10.0.0.md:197` | The rule requires a plan with owner, fix and deadline. K-16's is "Fix: none possible", with a review date that is not a fix date. The document and the question put to the user both say so plainly, so nothing is hidden, but the rule has no such case, and the finding will return at every release | A ruling for register v12: does a no-fix plan satisfy the rule? For the user, not an agent | Track |
| TL-T761-11 | LOW | `scripts/publish-release.py:755`; `.gitlab-ci.yml:231-233` | On a runner with `FF_GIT_URLS_WITHOUT_TOKENS` on, `release`'s fetch would have no credential: it works while the project is public, and fails closed if it is not. `CONTRIBUTING.md`'s rule is right: do not widen the allowlist | Note it beside the flag's open point | Track |
| TL-T761-12 | Minor | `CONTRIBUTING.md:279-292`; `.gitlab-ci.yml:240` | The first-tag list does not say that `main` must not move before the tree check ends | The orchestrator holds it at T764. Add to `CONTRIBUTING.md` after the release | T764 by practice; text tracked |
| TL-T761-13 | LOW | `implementation/runtime/memory/README.md:52, 74` | Ships to every target with this repository's own `em-age-emage.code` path as the example. Copied as is, the server does not find the index. The error names the path | Use `<org>-<repo>` there | Track |

## Before the tag

**What must change (all text; none needs a code change, all before the independent check, or they make it stale):**

1. TL-T761-01: one sentence in step 1.
2. TL-T761-02: one sentence in M-2.
3. TL-T761-04: T763's order.
4. TL-T761-03: the user's call. I recommend the fix, because a reader upgrading through the README is the likeliest route into M-2's failure.

Since a commit is being made anyway, TL-T761-05, -07 and -09 can go with it. They are one clause each.

**What can be tracked:** TL-T761-05 to -13, as the user's policy has it. **Who should care when upgrading:** only -01, -02 and -03 change what happens on a real project. The rest are wording, or for maintainers.

## Gate rows for the release document

Architecture: this review found no breach of ADR-011 or ADR-012 and no new accepted design outside them; no separate architect's gate ran in plan-145. Implementation: CONDITIONAL_PASS on 2026-11-07, with conditions C-1 and C-2 below. **T763 owns both lines.**

## Gate Verdict: Implementation Review

**Gate:** implementation
**Executor:** tech-lead
**Date:** 2026-11-07
**Target:** v10.0.0 release (`release/v10.0.0` at `3641abfb`)

### Verdict: CONDITIONAL_PASS

Findings: the table above (TL-T761-01 to -13: four Important, five Minor, four LOW; no blocker). Conditions: C-1 and C-2.

## VERDICT: CONDITIONAL_PASS

### Reviewed Artifacts

- Implementation: `release/v10.0.0` at `3641abfb`, range `v9.0.0..3641abfb`
- Against requirements: none applies; `docs/plans/plan-145-release-v10.md`, `docs/artifacts/release-v10-audit-v1.md`
- Against architecture: none applies; ADR-011, ADR-012

### Decision IDs Referenced

- ADR-011, ADR-012

### Conditions (for CONDITIONAL_PASS)

- [ ] **C-1** TL-T761-01 and TL-T761-02 are fixed in `docs/releases/v10.0.0.md`, and the user has decided TL-T761-03. Owner release-manager; due before T763's independent check.
- [ ] **C-2** T763 fills the seven lines outside the closed list before the check, and the check runs on that commit (TL-T761-04). Owner release-manager; due at T763.

### Blocking Issues (for FAIL)

- None.

### Merge Authorization

- Merge permitted: Yes, with conditions tracked. Nothing is merged by this review, and the tag and the Release keep the user's approval.
- Reviewed by: Tech Lead
- Review mode: read-only (no modifications made to source)

## Not checked (unverified)

1. All tag-pipeline behaviour: section "The unproved lines". Nothing was published.
2. A retrieval on v10 with real chunks. My index had 0 chunks, so the server's start is shown and a query is not. The moved-index case is shown only for an empty index, and only as far as the start.
3. TL-T761-02's silent mismatch: read through `build.py`, `scanner` and `scope_filter.py`, not run.
4. Most of `tests/functional/test_ci_hash_pins.py`, and most of `scripts/publish-release.py` below `main`: covered by their tests and T759, not read line by line.
5. The bodies of the new `sync.mjs` functions: names and T753's tests only.
6. Batch H's text beyond the lines listed in Area 2; knowledge text elsewhere in the diff.
7. K-1's agent and command counts beyond the tail of the checker's output, K-31's count of 14, and all of K-29's and K-34's technical claims (T762).
8. That merge request pipelines on `develop` ran the new digest green: not read here.
9. CWSO: not read.

[VERDICT] gate=code-review | result=CONDITIONAL_PASS | reviewer=tech-lead | artifact_ref=tech-lead-release-v10-v1.md | date=2026-11-07
