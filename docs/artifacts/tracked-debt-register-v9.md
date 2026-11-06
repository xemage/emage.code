# Artifact: tracked-debt-register-v9.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v8.md` (544 ids; v8, v7, v6 and v5 stay the record for the text of every id that did not change, and, with v1 to v4, for every id that was `fixed` or `obsolete` there); `docs/plans/plan-139-tracked-debt-register-v9.md` and `docs/tasks/task-T742.md` (the user's "v9 go"); `docs/plans/plan-138-gate-pin-and-strict-read.md`; `docs/artifacts/security-review-t741-gate-pin-v1.md`; `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4, for the text of the SEC-T739 ids. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01, superseded in part), ADR-012 (Accepted 2026-11-04), as v8 cites them, not re-read; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T742 (plan-139; the user's answer of 2026-11-06, verbatim: "v9 go"). **Date**: 2026-11-06.
- **Tree read**: branch `agent/tech-lead/T742` at `544166c1` (develop `80578802` plus the plan commit, which adds plan-139, the brief and a ledger row). Commits since v8's merge `c1ae6afe`: `41df4020` (T741, squashed, merge request !646), `80578802` (its merge), `544166c1`. `git diff --name-only 8292c1bb 544166c1` lists, outside `docs/artifacts/`, `docs/plans/` and `docs/tasks/`, only `scripts/verify-release-docs.py` and the test files `test_ci_hash_pins.py`, `test_knowledge_template_images.py`, `test_publish_release.py` and `test_verify_release_docs.py`. So nothing under `implementation/`, `docs/releases/`, `docs/decisions/` or `ci/`, and nothing in `.gitlab-ci.yml`, `CONTRIBUTING.md`, `scripts/install.sh`, `scripts/publish-release.py` or `scripts/check-release-tag-tree.py` changed since v8's tree, and v8's lines in those paths stand. The CWSO repository was not read: every CWSO status carries over from v8.
- **Review mode**: read-only. A closure cites plan-138 or review T741. "Unchanged" means no task, review or plan outcome since v8 names the id with a change of status, checked by searching the lines added in `c1ae6afe..544166c1` (section 8). The code was not re-checked unless a line is cited. Anything not traced is **(unverified)**.
- **Reviewed tree**: review T741's last round read `68a70735`. `git diff 68a70735 41df4020` holds only docs (the review, plan-138, the ledger and the T741 brief), so its code is the merged code. The branch's own commits (`b9b62187`, `201f2954`, `b23c756f`, `ec2ea70b`, `036b4e47`, `68a70735`) are named in the review's Metadata and in plan-138; the commits citable on `develop` are `41df4020` and `80578802`.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository, registers v1 to v7. Read beyond the brief's list, by grep or line range: `tests/functional/test_verify_release_docs.py`, `scripts/check-version-consistency.py`, `scripts/dry-run-publish-release.py`, `docs/tasks/task-T741.md`, rows T740 and T741 of `completed-tasks.md`, and plan-137 for ids. None is a register. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5.
- **Batch letters**: I, J, K, L, M, N, P, Q, R, T, F and U keep their v8 scope. **S** loses two ids and takes six (section 5).

## 1. Summary

v9 holds **561 ids**: the 544 of v8 and **17 new**. After v9: **434 fixed**, **46 accepted**, **6 obsolete**, **1 open**, **74 tracked-LOW**.

- **Open above LOW: none**, with the qualification v8 made. The one open id is K-20 (live checks, user). All 7 MEDIUM findings of review T741 are resolved, and the review counts 0 CRITICAL, 0 HIGH and 0 MEDIUM remaining. **TD-T739-01 still has no reviewer's grade**: v8 files it as tracked-LOW, and this register follows. The five accepted MEDIUMs (section 6.1) are accepted, not open; under ADR-011 four of them need the user's new acceptance at the next release (section 6.2, item 2).
- **Batch S's 2 changed ids**: both fixed (SEC-T739-05, SEC-T739-01). The other 9 are unchanged and 6 new ones join, which gives 15.
- **Stale ids: none.** T741 moved the lines of batch S and of three batch N ids, and no finding lost its subject (section 5). Two finding texts now read loosely, without a change of status: SEC-T738-02 says `read_text`, and the code is `read_strict`; SEC-T739-06's fix now needs a pin edit, as the review's fix already said.
- **Due before the next release**: as in v8, SEC-T735-08 and SEC-T735-09 (section 6.2, items 2 and 10). **Any of batch S before the next tag stays open for the user**: no source binds it to a release.

Arithmetic, from the v8 totals:

| Status | v8 | leaves | enters | v9 |
|---|---:|---|---|---:|
| fixed | 421 | | + 2 batch S + 11 new | **434** |
| accepted | 46 | | | **46** |
| obsolete | 6 | | | **6** |
| open | 1 | | | **1** |
| tracked-LOW | 70 | - 2 fixed | + 6 new | **74** |
| **all** | **544** | | + 17 new ids | **561** |

Check: 434 + 46 + 6 + 1 + 74 = 561. Open or tracked: 74 + 1 = 75, the size of section 5.

### 1.1 Ids by v8 status and status now

| v8 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 70 | 2 | 0 | 0 | 0 | 68 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 421 | 421 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v8 ids** | **544** | **423** | **46** | **6** | **1** | **68** |
| new in v9 | 17 | 11 | 0 | 0 | 0 | 6 |
| **all v9 ids** | **561** | **434** | **46** | **6** | **1** | **74** |

### 1.2 New ids by source and grade

| Source | new | MEDIUM, fixed | LOW, fixed | LOW, tracked |
|---|---:|---:|---:|---:|
| `security-review-t741-gate-pin-v1.md`, SEC-T741 | 17 | 7 | 4 | 6 |
| **All new** | **17** | **7** | **4** | **6** |

A search of the lines added in `c1ae6afe..80578802`, outside the held-out set, finds no other new id; a search of plan-137 finds only ids that v8 holds, and plan-139 mints none. The carried ids a literal search of `c1ae6afe..544166c1` finds are SEC-T738-02, -04, -06, SEC-T739-01, -02, -05, -06, -07, -09, TD-T739-01 and SEC-T735-06 (the last and SEC-T739-06 in plan-139 only): apart from SEC-T739-05 and -01, each appears as "not changed" or "stays", as a code comment, or as plan-139's carried instruction, with no change of status. A range such as "SEC-T739-01 to -09" would not match literally; plan-138's own list of what it did not change uses "-03, -04" forms, and I read that list. `M-3` is an example heading in a test. This register mints no debt id. A-17 and A-18 in section 7 are user-action numbers.

### 1.3 How the review's counts map to ids

| Grade | Review T741's count | Resolved | Remaining | As ids |
|---|---:|---:|---:|---|
| MEDIUM | 7 | 7 | 0 | SEC-T741-01 to -04, -09, -10, -15 |
| LOW | 10 | 4 | 6 | Resolved: SEC-T741-05, -11, -13, -14. Remaining: SEC-T741-06, -07, -08, -12, -16, -17 |

The two counts cover the 17 ids one to one. SEC-T739-05 and SEC-T739-01 are not in them: they were LOW in the T739 review (review T741, Verdict).

## 2. v8 ids re-checked

Every v8 `open`, `tracked-LOW` and `accepted` id (117) has a row or a list entry here: 1 + 70 + 46. The v8 `fixed` and `obsolete` ids stay as v8 records them.

### 2.1 v8 `open` (1)

K-20: **Unchanged**, open, batch U (A-7).

### 2.2 v8 `tracked-LOW` (70)

**Changed (2, batch S)**

| Id | v8 | now | Evidence |
|---|---|---|---|
| SEC-T739-05 | tracked-LOW | **fixed**, beyond what its reviewer asked | T741 (squash `41df4020`, merge `80578802`, merge request !646). The reviewer asked for `script` to equal the gate command, a refusal of `allow_failure`, `when` and `variables`, and `rules` asserted exactly. Plan-138 made it a key allowlist instead of a denylist, so `extends`, `after_script` and any key added later are refused too. In `tests/functional/test_ci_hash_pins.py`: `GATE_KEYS` `:65`, `PINNED_JOBS` `:68-72`, `pinned_job_problems` `:308-328`, `release_gate_job_problems` `:331`, `TestReleaseGateJobPin` `:687`. Review T741 § 1: "resolved as the T739 review's fixes asked". The user: "05 01 go". Limit: the pin guards a merge, not a tag cut from a commit that never went through `unit-tests` (contract 6, `:24-26`) |
| SEC-T739-01 | tracked-LOW | **fixed** | T741 (same commits). `read_strict`, `scripts/verify-release-docs.py:241-257`; all seven reads go through it (`:334, 400, 408, 424, 437, 581, 599`), and `errors="ignore"` has 0 hits in the script. The error holds the path and offset only (`:253-256`). A refusal ends the run (`:664-667`). Review T741 § 1. The user: "05 01 go". What the fix does not reach is tracked: SEC-T741-06 (the child process's reads), SEC-T741-07 (a pointed document that is not read), SEC-T741-08 (the narrow source test) |

**Unchanged (68 tracked-LOW; v8, v7, v6 and v5 stay the record of their text)**

| Batch | Ids | n |
|---|---|---:|
| I | SEC-T722-01, SEC-T722-02, SEC-T722-03, SEC-T722-04, SEC-T722-05, SEC-T725-01, SEC-T725-02, SEC-T725-03, SEC-T724-01, TD-T724-01 | 10 |
| J | SEC-T663-02 | 1 |
| K | SEC-T714-02, SEC-T714-04, SEC-T714-06, SEC-T714-08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 |
| L | SEC-T726-01, SEC-T726-02, SEC-T726-03, TD-T726-01, TD-T726-02 | 5 |
| M | SEC-T727-01, SEC-T727-02, SEC-T727-03, SEC-T727-04, SEC-T727-05, SEC-T728-01, SEC-T728-02, SEC-T728-03, TD-T728-01, TD-T728-02, TD-T728-03, SEC-T696-07 | 12 |
| N | SEC-T730-03, SEC-T730-04, SEC-T730-06, SEC-T731-03, SEC-T731-04, SEC-T731-05, SEC-T732-01, SEC-T732-02 | 8 |
| P | SEC-T702-08 | 1 |
| Q | TD-T723-01, SEC-T735-08, SEC-T735-09 | 3 |
| R | SEC-T735-06, SEC-T735-07, SEC-T736-01, SEC-T693-07 | 4 |
| S | SEC-T739-02, SEC-T739-03, SEC-T739-04, SEC-T739-06, SEC-T739-08, SEC-T739-09, SEC-T738-02, SEC-T738-06, TD-T739-01 | 9 |
| T | SEC-T739-07 | 1 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 5 |

Total 68; with the 2 above, 70.

### 2.3 v8 `accepted` (46)

**All unchanged**; basis as in v5 § 2.3, v6 § 6.1 and v7 § 2.3. None has a new acceptance.

- **MEDIUM (5)**: SEC-T657-01 / SEC-T658-01 (one id), SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07.
- **LOW or INFO (41)**: K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, K-15, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07.

## 3. New ids

Source: review T741 § 2 and § 4, where each id's fix is; plan-138 § Changes after the first and second security review, § Outcome. The code of all 17 is in squash `41df4020`. "Closed at" is the review round that closed the id, as plan-138 records it: `ec2ea70b` for SEC-T741-01 to -05, `036b4e47` for -09, -10, -13 and -14, `68a70735` for -11 and -15. Owner of the tracked ids per review § 4's heading: devops-engineer, "proposed". The review says all 7 MEDIUM routes are older than T741 (Verdict). Lines are current, read on `544166c1`, in `tests/functional/test_ci_hash_pins.py` unless the path says otherwise.

| Id | Grade | Location now | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T741-01 | MEDIUM | `merge_key_lines`, `:260`; `ci_pin_problems`, `:384` | A `<<` overriding an allowed key passes the pin, because PyYAML and GitLab's parser disagree. | fixed; closed at `ec2ea70b`. Merge keys refused in the whole file, from the node tree | - | - |
| SEC-T741-02 | MEDIUM | `PINNED_JOBS`, `:73-90`; `pinned_job_problems`, `:308` | `release` could skip the gate: the `needs` pins were text checks a comment satisfied. | fixed; closed at `ec2ea70b`. Parsed allowlists on `release` and `main-develop-drift-gate` | - | - |
| SEC-T741-03 | MEDIUM | `file_level_problems`, `:335`; `:93-97`; the artifacts part now in `tag_runnable_job_problems`, `:349` | File-level routes: `include`, top-level `variables`, `workflow`, `default`, an earlier job's artifacts. | fixed; closed at `ec2ea70b`. Top-level keys refused or pinned. **Its fix was replaced in part by SEC-T741-15's**: the rule on jobs with `artifacts` gave way to the rule on any job that can run on a tag (review § 2) | - | - |
| SEC-T741-04 | MEDIUM | `PINNED_IMAGE`, `:63`; `ci_images`, `:370`; `image_pin_problems`, `:377` | The `image` value was unguarded, and the digest regex missed comment and mapping forms. | fixed; closed at `ec2ea70b`. The parsed value is pinned on the tag jobs; the digest tests walk parsed values | - | - |
| SEC-T741-05 | LOW | Contract 6, `:16-26`; `scripts/verify-release-docs.py:28-31, 226-230` | Three overclaiming sentences. | fixed; closed at `ec2ea70b`. Reworded | - | - |
| SEC-T741-09 | MEDIUM | `spelling_problems`, `:271` | Key spellings PyYAML keeps apart and GitLab folds: `:x`, `!!null`, `!!binary`. | fixed; closed at `036b4e47`. Explicit tags, plain colon-led scalars and non-string keys refused | - | - |
| SEC-T741-10 | MEDIUM | `predefined_variable_problems`, `:300` | A job setting its own `CI_COMMIT_BRANCH` makes a branch condition true on a tag. | fixed; closed at `036b4e47`. `CI_` variables refused on any job, hidden ones included, and in `parallel:matrix` | - | - |
| SEC-T741-11 | LOW | `tag_runnable_job_problems`, `:349` | A job without artifacts could run on a tag. | fixed **for the same pipeline**, by the rule of SEC-T741-15; **its part across pipelines is SEC-T741-17**. The option of "Fix, narrow re-review (Recommended)" still said it stays tracked; the later rule closed it (review § 2; plan-138 § Outcome) | - | - |
| SEC-T741-13 | LOW | Contract 6, `:16-26`; the walker, `mapping_keys`, `:237` (the location is tech-lead's reading) | Contract 6 and the walker's wording. | fixed; closed at `036b4e47`. Reworded | - | - |
| SEC-T741-14 | LOW | `test_a_recursive_alias_ends`, `:799`; the cap at `:803-805` | The test's memory cap could fail under a lower hard limit. | fixed; closed at `036b4e47`. `min(hard, 2 GiB)`, with the hard limit unchanged | - | - |
| SEC-T741-15 | MEDIUM | `tag_runnable_job_problems`, `:349-367` | A `pages` job makes artifacts without an `artifacts` key. | fixed; closed at `68a70735`. Inverted: outside the three pinned jobs, no job may be able to run in a tag pipeline, whatever it does. That the artifacts reach the gates was not observed; the fix does not depend on it (review Metadata) | - | - |
| SEC-T741-06 | LOW | `scripts/check-version-consistency.py:148, 177`; `scripts/dry-run-publish-release.py:255`; `.gitlab-ci.yml:67` | `errors="ignore"` is still used by the child process this gate runs, so `v8.0.0\xffabc` can hide a stale claim. The other two decide nothing here. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T741-07 | LOW | `check_migration_pointers`, `scripts/verify-release-docs.py:573`; the read only under `needs_cursor`, `:599` | A document on an `install.sh` line without "Cursor" is checked for existence only, so its bytes are not decoded. No result depends on them. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T741-08 | LOW | `test_the_script_has_one_way_to_read_a_file`, `tests/functional/test_verify_release_docs.py:1278-1282` | A narrow text match misses `open(path, errors="replace")`, `errors='ignore'` and `.decode("utf-8", "ignore")`. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T741-12 | LOW | `PINNED_JOBS` `release`, `:86-90`; `DEFAULT_KEYS`, `:96`; stated in contract 6, `:22` | `release.script` and `release.artifacts` have text checks or none, and a comment can satisfy them. The values of `default.tags` and `default.interruptible` are unpinned, and `tags` chooses the gates' runner. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T741-16 | LOW | `NOT_TAG_CONDITIONS`, `:98-103`; contract 6, `:16-26` | A person running a pipeline on a tag with `CI_COMMIT_BRANCH=x` should make a branch condition true, with no file edit **(unverified)**. Harm also needs a harmful job merged first. | tracked-LOW. **Needs something outside a test**: the project's minimum role for pipeline variables above Developer, a project setting (A-17), as well as the clause in contract 6 | devops-engineer (proposed); the setting is the user's | S |
| SEC-T741-17 | LOW | The gates' checkout, `.gitlab-ci.yml:196-206, 208`; `unit-tests`' `DOCKER_HOST`, `.gitlab-ci.yml:97`; `PINNED_JOBS`, `:67-91` | A branch job may leave state in a reused build directory or on the host, and `unit-tests` binds the Docker socket. A later gate on that runner might read it **(unverified, runner-dependent)**. | tracked-LOW. **Needs something outside a test**: a `.gitlab-ci.yml` change, `GIT_STRATEGY: clone` and a dedicated runner tag on the gates, pinned too. `GATE_KEYS` (`:65`) holds neither `variables` nor `tags`, so the pin changes with it (tech-lead's reading of the pin) | devops-engineer (proposed) | S |

## 4. Decisions since v8

### 4.1 The user's (words verbatim as recorded)

Each row claims only what the plan records it asked. The questions as shown to the user were not verified beyond those records **(unverified)**. Plan-138 dates only the first and the outcome: the other undated rows fall on 2026-11-05 or 2026-11-06.

| Date | Words | What the question asked, and the effect | Source |
|---|---|---|---|
| 2026-11-05 | "05 01 go" | Named SEC-T739-05 and SEC-T739-01 only, the two the reviewer would take first in batch S. Run T741 | plan-138 Based on, § Goal |
| not dated | "Fix all four first (Recommended)" | When to fix the first review's four MEDIUM findings. The option said: add them to plan-138 with the overclaiming wording SEC-T741-05, then re-review and merge; tests only, no CI file change; the other three LOWs stay tracked | plan-138 § Changes after the first security review |
| not dated | "Finish T741 yourself" | The implementer stopped in a devcontainer reboot. The orchestrator finished `b23c756f` and wrote the later commits; the second reviewer was told so | plan-138 § Outcome, "Who wrote what"; review Metadata |
| 2026-11-06 | "review go" | The orchestrator asked whether to launch a new Security Engineer on T741's second round. The user's whole answer: "Launch a new Security Engineer on T741. review go". This is the decision the review's Metadata means by "a second agent". Plan-138 does not quote it (the orchestrator, plan-139 § Outcome) | plan-139 § Task Decomposition, § Outcome |
| not dated | "Fix, narrow re-review (Recommended)" | The second review's findings. The option said: fix -09 and -10, plus -13 and -14; the same reviewer checks only that new diff; merge after; -11 and -12 stay tracked as LOW | plan-138 § Changes after the second security review |
| not dated | "Invert the rule, then stop (Recommended)" | SEC-T741-15. The option said: any other job that could run on a tag is refused, whatever it does; the same reviewer checks that one diff; if it finds yet another route, the orchestrator records a remediation plan and merges unless it is HIGH or worse. **The stop clause was not used**, because no route above LOW was found | plan-138 § Changes after the second security review |
| 2026-11-06 | "v9 go" | plan-139, T742 (this register) | plan-139 Based on |

### 4.2 Other decisions (not the user's)

| Id or item | Decision | By | Effect |
|---|---|---|---|
| SEC-T741-05 | Folded in as claims this change wrote | the orchestrator (plan-138 § Outcome, "Rulings") | section 3 |
| SEC-T741-13, -14 | Folded in by the user's option; the ruling records it | the orchestrator (plan-138 § Outcome, "Rulings"); the option's answer is in section 4.1 | section 3 |
| Mutation "image without str check" | Stays uncaught: `fullmatch(str(image))` cannot change a result; the reviewer traced the same | the orchestrator (plan-138 § Outcome, "Rulings") | none on status |
| Plan-138's offset sentence | Its sentence that `UnicodeDecodeError.start` from `read_text` is chunk-relative was wrong for a whole-file read; the exact-offset test stays | the orchestrator (plan-138 § Changes after the first security review) | none on status |
| Batch S | Loses SEC-T739-05 and -01; takes the 6 tracked ids | plan-139 | section 5 |

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. I, J, K, L, M, N, P, Q, R, T, F and U are carried from v8 without change; in those rows "review" and "review § 4" mean the batch H review, except where a row names another.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | **SEC-T722-03 (do first)**, **SEC-T725-02 (do first)**, SEC-T722-01, -02, -04, -05, SEC-T725-01, -03, SEC-T724-01, TD-T724-01 | 10 | devops-engineer; backend-developer (SEC-T724-01, TD-T724-01) | next installer or generator change; SEC-T725-02 before the release that ships T725 (recommendation) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | devops-engineer | its own task (five test files, documents and live evidence change; plan-128) |
| K | Security runtime (`security-audit` servers) | SEC-T714-02, -04, -06, -08, SEV-T690-02 (pinned runtime package), SEV-T690-04 ((d) Copilot), SEC-T665-07 (if reopened) | 7 | devops-engineer; technical-writer (wiki residual of SEC-T714-06) | next change to `implementation/runtime/security/`; SEC-T665-07 on its reopening conditions |
| L | CWSO helper scripts in emage.code | SEC-T726-01 to -03, TD-T726-01, TD-T726-02 | 5 | devops-engineer | next change to the CWSO helper scripts; TD-T726-02 before the next Proxmox setup |
| M | CWSO repository | **SEC-T728-01 (do first)**, **SEC-T727-01, -02 (do first)**, SEC-T727-03 to -05, SEC-T728-02, -03, TD-T728-01 to -03, SEC-T696-07 ((b) fuel/epoch) | 12 | devops-engineer (CWSO; agent branch from CWSO `origin/develop`, MR into CWSO `develop`) | next CWSO change; TD-T728-02 adoptable since **2026-11-04**; TD-T728-01 in the next CWSO release notes; SEC-T696-07(b) before untrusted modules are accepted |
| N | Release tooling, second round (`publish-release.py`, `verify-release-docs.py`, CI locks and the npm step) | SEC-T730-03, -04, -06, SEC-T731-03, -04, -05, SEC-T732-01, -02 | 8 | devops-engineer (batch G review § 4) | next fixing round; no source binds it to a release |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines; the orchestrator offers the draft (plan-126) | when the user reopens it: "Keep it tracked" sets no date. The natural next look is the Brave review of section 6.3 (tech-lead's suggestion; no source sets it) |
| Q | Next release document | TD-T723-01, **SEC-T735-08**, **SEC-T735-09** | 3 | release-manager (TD-T723-01, v6); orchestrator routes the two SEC ids (review § 4). Suggested, no source sets it: release-manager, because they shape the release document | the next release document. **SEC-T735-08 and -09 before the next release starts** (review § 4; section 6.2, items 2 and 10); TD-T723-01: item 4 |
| R | Release-gate text, second round | SEC-T735-06, SEC-T735-07, SEC-T736-01 (the rest), SEC-T693-07 | 4 | orchestrator routes each (review § 4). Suggested, as in T735 and T736, no source sets it: technical-writer for text, devops-engineer for pins | none set: review § 4 dates only SEC-T735-08 and -09. Read here as the next change to the release-gate text; see below |
| **S** | Release gate after the parser, and what T741's reviews left | SEC-T739-02, SEC-T739-04, SEC-T739-06, SEC-T739-08, SEC-T739-09, SEC-T739-03, SEC-T738-02, SEC-T738-06, TD-T739-01, SEC-T741-06, SEC-T741-07, SEC-T741-08, SEC-T741-12, SEC-T741-16, SEC-T741-17 | 15 | devops-engineer (review T739 § 4; review T741 § 4, "proposed"; TD-T739-01 is the tech lead's suggestion from v8); SEC-T741-16's setting is the user's (A-17) | **open, for the user**: review T739 § 4 says "next sprint", review T741 sets no date, and no source binds S to a release |
| T | Verdict placeholder check on the token stream | SEC-T739-07 | 1 | devops-engineer (review T739 § 4) | none set: review T739 § 4 says only that it needs its own plan, and plan-136 § Outcome agrees |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 10 + 1 + 7 + 5 + 12 + 8 + 1 + 3 + 4 + 15 + 1 + 2 + 6 = 75 = 74 tracked-LOW + 1 open. No open item is above LOW, with the qualification on TD-T739-01 in section 1.

**Batch N, re-read on `544166c1`.** T741 moved the gate script's top by five lines, so **no id is stale**. `sed` shows the regex block unchanged: v8's `:159-166` is now `:164-171`. The other five ids sit in files T741 did not change, and v8's reading stands for them; I did not re-run any.

| Id | v8's line | Now | Reading |
|---|---|---|---|
| SEC-T730-03 | `publish-release.py:629, 750` | same | File unchanged |
| SEC-T730-04 | `ci/requirements-ci.in`, `ci/requirements-ci.txt:2-4` | same | Rewritten `test_ci_hash_pins.py` still has no `generated-on`, cooldown or gap check by grep |
| SEC-T730-06 | not located | not located | File unchanged. **(unverified)**, as in v8 |
| SEC-T731-03 | `verify-release-docs.py:160, 164` | `:165, 169` | `POINTER_LIKE_RE`, unchanged, moved. The long-line test is now `test_verify_release_docs.py:698` |
| SEC-T731-04 | `verify-release-docs.py:159-166` | `:164-171` | Same regex, moved |
| SEC-T731-05 | `verify-release-docs.py:185`, `check-release-tag-tree.py:48` | `:190`; `:48` | `UNSAFE_RE`, moved. The equality test is at `test_verify_release_docs.py:1304` |
| SEC-T732-01 | `.gitlab-ci.yml:93-104` | same | CI file unchanged |
| SEC-T732-02 | `ci/js/README.md:39-43` | same | Directory unchanged |

**Batch S and T, re-read on `544166c1`.** Lines are in `scripts/verify-release-docs.py` unless the path says otherwise. The text of each id stays in v8 § 3 and review T739 § 4. The order is the batch's.

| Id | v8's line | Now | Reading |
|---|---|---|---|
| SEC-T739-02 | `inline_text`, `:470-482`; `--help` `:206-207` | `:503-515`; `:211-212` | Moved |
| SEC-T739-04 | `:210-211` | `:215-216` | Moved |
| SEC-T739-06 | `.gitlab-ci.yml:196-206` | same; the install at `:202`; the pin at `tests/functional/test_ci_hash_pins.py:57-58, 70` | **`PINNED_JOBS` now pins this `before_script` exactly, so the fix, an `unset` line added to it, must change the constant `RELEASE_GATE_INSTALL` or the pin**, or a test fails. The reviewer's fix says "update the pin". The constant is the install command, and the tests also use it at `:609-614`, so a second list item at `:70` is the smaller edit (tech-lead's suggestion). Still to do: check the list against GitLab's documentation; the residual is the clone credential in `.git/config` (review T739 § 4) |
| SEC-T739-08 | `docs/releases/_template.md:3`; `:569`; `CONTRIBUTING.md:408, 439` | template same; `:602`; `CONTRIBUTING.md` same | Moved in the script |
| SEC-T739-09 | `--help` `:210`; docstring `:20` | `:215`; `:20` | The label "What stays open (SEC-T738-04)" stands, as plan-138 § Not changed said |
| SEC-T739-03 | `:211-213` | `:216-218` | Moved |
| SEC-T738-02 | `:548` and `:432`; `--help` `:213-215` | `:581` and `:465`; `--help` `:218-220`, and now `:228-229`; `scripts/install.sh:1295-1297` | The behaviour stands: T741 moved the CR translation from `read_text` into `read_strict`, `:257`, on purpose (`:245-246`; review T741 § 1, "Nothing changes for SEC-T738-02"). `test_verify_release_docs.py:1261` says fixing the id changes that test |
| SEC-T738-06 | `test_verify_release_docs.py:944`; raw too at `:494`, `:989` | `:946`; `:496`, `:991` | Moved. T741 added one more raw U+2028 at `:1240` (tech-lead's check; whether it needs the same fix is not judged) |
| TD-T739-01 | `has_cursor_migration_item`, `:526` | `:552`, the parse at `:559` | Moved. No source since v8 reports a measurement on 4.2.0 |
| SEC-T739-07 (T) | `section_text`, `:251-263`; `verdict_placeholder_problems`, `:266-277` | `:284-296`; `:299-310` | Moved |

**Batch S, in short.** The six T739 ids keep review T739 § 4's order, with SEC-T739-05 and -01 gone and SEC-T739-07 in T. **Everything after them is my suggestion; no source sets it:** SEC-T738-02, -06 and TD-T739-01 stay last of the older ids, as in v8, and the new ids follow by number.

- **SEC-T739-02 is now first.** The false-pass group is smaller again: review T739 § 1's SEC-T739-01 to -04 are now -02 to -04. Each needs a crafted file that survives merge request review.
- **SEC-T741-06 first among the new ids (suggestion):** it is the same class as the fixed SEC-T739-01, in the child process the gate trusts. **SEC-T741-16 and -17 last (suggestion),** because each needs something outside a test: a project setting, and a `.gitlab-ci.yml` change.
- **SEC-T739-06 and SEC-T741-17 both edit the gate jobs and `PINNED_JOBS`**, so one change could take them together (suggestion). `.gitlab-ci.yml` did not change in T741, so they would be the first edits to these jobs under the pin.
- **No pin is provably complete.** Three reviews found three new routes, all older than T741, because PyYAML checks a file that GitLab reads with another parser (plan-138 § Outcome). Contract 6 states the routes and limits.

**Batch T, in short.** SEC-T739-07 is the same class as batch S in another check. The orchestrator confirmed the three shapes on the commit (review T739 Metadata). The reviewer's fix reads these sections from the token stream, or at least refuses a second occurrence of the heading. Plan-136's design scope kept this check on line rules, so a fix extends the parser's use beyond what "parser go" asked **(tech-lead's reading in v8; no source says so)**.

**Batch R, in short.** Carried from v8. **The route of SEC-T735-06 and -07 is still to be settled before batch R.**

- **SEC-T735-07: confirm the route first.** The reviewer's fix, "An acceptance covers", changes ADR-011's A1 text, and accepted ADRs are immutable (ADR-012 Status). The route is not settled; the review says only to confirm it.
- **SEC-T735-06** has the same question (tech-lead's reading in v8, no source says so): its fix, that `mitigation` cites where the plan was shown, changes the Conditions line, which is ADR-012's row B3. The top-level session's comparison would be a new duty too.
- **SEC-T736-01 (the rest)** needs pins and mutations only, in the style of T736, and no knowledge text.
- **SEC-T693-07 has no text fix**: "the independent check is a duty in the role text, not an enforced control" (plan-133), and the residual is accepted by ruling with no edit. Batch R must not edit for it. It closes only if an enforced control is built, and nothing here proposes one.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 § 6.1 and v6 § 6.1 stand unchanged and stay the record, with v7 § 6.1 and v8 § 6.1. Plan-138 adds and renews no acceptance: all its MEDIUMs were fixed, and the stop clause that would have recorded a remediation plan was not used. ADR-012 replaces rows A1, A8 and A12 of ADR-011 in part; the rest of ADR-011 stands: only the user accepts, one release only.

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 pin audit **2027-01-30 or the first Brave release above 2.1.4**; SEC-T702-09, SEC-T660-01, SEC-T665-01 and the SEC-T657-01/SEC-T658-01 remainder: **the next release needs the user's new acceptance** (ADR-011, ADR-012).

### 6.2 Next release checklist

Carried from v8 § 6.2, with its numbers. Item 15 is rewritten, and items 18 to 20 are new. Every line that points into `scripts/verify-release-docs.py` or `tests/functional/test_ci_hash_pins.py` was read again on `544166c1` (items 7, 15, 16, 17); the wording of those items is otherwise v8's. Items 1 to 6, 8 to 14 are v8's text and their paths have not changed since v8: their lines were read on `a4c3c7b3` or `8292c1bb`, under `implementation/knowledge/` unless the path starts at `docs/` or `scripts/`. In those items "review" means the batch H review.

1. **Migration item T725 (TD-T671-P5)** in the release document: authoring-only commands are no longer installed into target projects; commands declare `audience: authoring | target | both`; today only `/prepare-release` (five platform paths listed in plan-128 § Outcome); `--update`/`--projections-only` deletes an existing copy (a dry run prints the `rm`); an authoring checkout (`implementation/registry/index.json`) keeps them; a target that used `/prepare-release` keeps its own copy under another file name; `.generated-manifest.json` gains `authoringOnly`; the generator refuses a command without a valid `audience:`.
2. **ADR-011 re-acceptances**: the Release Gate input lists every MEDIUM an earlier release shipped under the user's acceptance and not yet fixed (SEC-T720-01 fix, `validation-gates/SKILL.md`): **SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09**. Each one is fixed, or the user accepts it again for this release, verbatim and dated, with its remediation plan (owner, fix, deadline). No agent grants or carries one over.
   - **When asking the user to re-accept any of these four (SEC-T735-08; ADR-012): name the release, record the plan as shown, and show a deadline still ahead.** The rule text does not say whether a new acceptance cures a deadline that has already passed, so do not put that case to the user as if it were settled.
   - Each carried plan's actual deadline was not verified by the reviewer (review § 5) or here **(unverified)**: read it before asking.
3. **New verdict fields** (R4, R10): `Issued at commit` and `Independent check` (`docs/releases/_template.md:87-88`; `commands/prepare-release.md:59-60`). The independent check row must be present, current and not FAIL (SEC-T693-02).
4. **TD-T723-01 (batch Q)**: the release document cites current `install.sh` lines. `docs/releases/v9.0.0.md:86` cites `install.sh:1300`, and `:75` cites `install.sh:1285-1302`, which v5 did not mention. On `a4c3c7b3` the advice is `scripts/install.sh:1297-1300` and the pointer is `:1301`; re-read them when the document is written.
5. **Brave**: if the release falls after 2027-01-30 or after a Brave release above 2.1.4, the pin audit needs a new acceptance version or the bump first.
6. **D-T710-2**: confirm in the release job that the `CHANGELOG.md` entry lands below `[Unreleased]` (fixed in code by T716; not yet observed in a tag pipeline).
7. **Visible changes of batch G** (plan-131 § Outcome), for the release document and its author:
   - `CHANGELOG.md` entries now show `\#42`, `\@user` and URLs in backticks in their source, and `(#42)` no longer links to the issue.
   - **The blank-line rule is gone, and `## Migration Guide <!-- x -->` now counts** (plan-136 § Outcome). The gate reads the document with `markdown-it-py`'s CommonMark parser (`verify-release-docs.py:191-230` is the `--help` text, `:536-570` the code). The section is the first top-level level 2 heading whose text is exactly `Migration Guide`, in ATX or setext form, up to the next top-level level 1 or 2 heading in either form; a heading inside a blockquote or a list neither opens nor ends it. The Cursor item is, in that section, with the case-sensitive word `Cursor` in its text, either a top-level heading of level 3 to 6, or a paragraph, top-level or with only list containers around it, that opens with a `**` strong span, and only the text inside that span counts. Text means text and inline code, with a line break read as a space; an image's alt text and inline HTML never count. `__bold__`, an anchor in a blockquote and a heading in a list do not count.
   - **What still follows from that rule:** a bold lead must open its own paragraph. `Some text` followed on the next line by `**Cursor**` is one paragraph, so it does not count, and a blank line is still what a release author needs there. A heading does not need one. Run in v8 on the local `markdown-it-py` 3.0.0; the orchestrator ran the same shapes on the locked 4.2.0 with the same results (plan-137 § Outcome). The error at `:602` says "lead line", which is looser than this (SEC-T739-08).
   - **Checked files may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`.** They are the tag's release document, the three marker files and now `scripts/install.sh` (SEC-T731-07) (`verify-release-docs.py:182`, `:647`). The error names the file, the line and the code point.
8. **Not verified live in plan-131; watch these in the release**:
   - how GitLab renders the escaped references and code spans;
   - the npm step (`npm ci --ignore-scripts --prefix ci/js`) in a tag pipeline;
   - the lock on the musl image beyond the MR pipeline.
9. **The Conditions block** (`agents/release-manager.md:183`, ADR-012 B3): an accepted `SECURITY:MEDIUM` fills `risk_accepted_by=` with the user's words verbatim and the date, `grade=`, `release=` (the version the user was asked about), and `mitigation=` with the plan as shown to the user, its owner and fix, and the current owner if it has changed; `deadline=` holds the plan's deadline.
10. **The template's pointer sentence** (`docs/releases/_template.md:90`; SEC-T735-09): remove it before the independent check, or leave it. Deleting it after the check makes the check stale. That the gate tolerates the leftover sentence is T736's report; the reviewer did not verify it (review § 5).
11. **The independent checker** (`agents/release-manager.md:46`): "The checker has not authored or edited the release files for this release; if the checker has, the row counts as missing." The orchestrator or the top-level session will often be ineligible, so `@tech-lead` is the practical default (review § 1; plan-133 § Outcome). If the checker edited the files, another eligible checker re-runs it.
12. **Batch H changes a release author sees**:
    - after the check, only the closed list in `agents/release-manager.md:46` may change ("No other text may be added after the check"); it includes "Changelog Preview (a summary of the checked changelog, nothing new)";
    - hotfix eligibility (`skills/release-workflow/SKILL.md:171`): the issue is present in the released version, and is graded critical or high on its own scale, or, whatever its grade, is a breach of an Immutable Security Constraint or a required control omitted, removed, disabled or weakened, which `@security-engineer` confirms. A fix with design impact does not take the fast track (`:202`).
13. **Not verified in batch H**: whether targets receive `scripts/verify-release-docs.py` and `docs/releases/_template.md` (review § 1). The migration note must not assume that they do. A grep of `scripts/install.sh` finds no `rsync` or `cp` line naming `scripts` or `docs`, and its one mention of the gate script is a comment (`:1296`). That is a grep and not an install, so the question stays **(unverified)**.
14. **Watch `release-docs-gate` in the first tag pipeline** (plan-136 § Not verifiable before the next tag, § Outcome). No merge request pipeline runs its install (`.gitlab-ci.yml:196-206`; the job's rule is the tag rule). A release candidate would prove it first. Each publishing step needs the user's approval.
15. **The job must stay without `allow_failure`** (review T739 § 1; plan-138 § Outcome). `allow_failure` on any tag job now fails a test (`pinned_job_problems`, `tests/functional/test_ci_hash_pins.py:308-328`; SEC-T739-05, SEC-T741-02). The job must still stay without it: a PyPI outage fails the job closed, that outage is when someone will be tempted to add it, and `needs` in `release` does not stop a release after an allowed failure.
16. **A local gate run needs the parser.** Without it, every gate run exits 1 and prints the install command, which is the one to use, in a virtual environment (`verify-release-docs.py:149-155`; `CONTRIBUTING.md:164-167`): `python3 -m pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt`. A developer's system package may be another version; the job's locked run decides (plan-136 § Design).
17. **A regeneration of `ci/requirements-ci.txt` needs `ci/requirements-release.txt` too**: `test_the_release_lock_matches_the_ci_lock` (`tests/functional/test_ci_hash_pins.py:629`) enforces the versions and hashes (plan-136 § Outcome).
18. **A new job in `.gitlab-ci.yml` needs an `if` from `NOT_TAG_CONDITIONS`** (`tests/functional/test_ci_hash_pins.py:98-103`; `tag_runnable_job_problems`, `:349-367`; plan-138 § Outcome). Adding a condition is a visible test edit and means checking that it is false on a tag: `$CI_PIPELINE_SOURCE == "schedule"` alone would not be, because a schedule can run on a tag ref (review T741 § 1, the reviewer's memory).
19. **A digest bump across all jobs passes; an `apk` pin or a Python minor bump needs a test constant edit** (plan-138 § Outcome; review T741 § 1: "with a clear message"). The constants I read are `PINNED_IMAGE` (`tests/functional/test_ci_hash_pins.py:63`) and the drift gate's `before_script` (`:77`). **The CI header's bump recipe does not say so yet** (`.gitlab-ci.yml:23-26`). This is a fact for whoever bumps an image; fixing the header is not scheduled.
20. **A checked file must be valid UTF-8, and the gate names the path and offset** (SEC-T739-01; `verify-release-docs.py:241-257`), never the content. The rule covers what the gate reads in this process (`:28-31, 226-230`): the child `scripts/check-version-consistency.py` keeps its lenient reads (SEC-T741-06), and a pointed document on an `install.sh` line without "Cursor" is checked for existence only (SEC-T741-07). The real tree's `--tag v9.0.0` run was plan-138's acceptance; it was not re-run here.

### 6.3 Dates

Carried from v8 § 6.3. Plan-138 adds none.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced; CWSO not read **(unverified)** | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v6, v7 and v8, which did not re-read them; nor did I **(unverified)**.

Not a debt date and not from plan-138, noted by the tech lead while reading the CI header: `.gitlab-ci.yml:18` holds `ci_images_reviewed_on: 2026-10-22`, and `tests/functional/test_ci_hash_pins.py:1051` allows 120 days. By reading, not by running it, the test starts to fail after 2027-02-19.

## 7. User actions

Carried from v8 § 7. A-17 and A-18 are new, from review T741 and plan-138. Plan-138 closes none; I did not re-check any state.

| # | Action | State now | Due |
|---|---|---|---|
| A-2 | Remaining T665 live checks (TD-T697-03; design checks 4, 5) | open | - |
| A-7 | Live checks Gemini CLI, Opencode denials, VS Code T690 servers, Pi lists (K-20, SEC-T658-02) | open | - |
| A-10 | On every other install: empty `glab`'s stored login and revoke its OAuth authorization if `GITLAB_TOKEN` is used | open (done on the user's devcontainer, v3) | - |
| A-11 | Remove or recreate any `cwso-sia-executor` container from the old compose definition (SEC-T694-12) | open for other hosts; none on the CWSO server | - |
| A-12 | Optional: replace the CWSO server's local compose override with `CWSO_ALLOWED_ORIGINS` | open, optional; now also subject to the T727 origin checks (A-16) | - |
| A-13 | Renew the GitLab token and the CWSO bearer token; renew the TD-T697-07 acceptance with the new bearer | open | GitLab **2027-01-28**; CWSO bearer **2027-01-29** |
| A-14 | Recheck that the CWSO server runs the merged images after the next CWSO change | due again (v5): CWSO develop moved to `6630ecb` (MR !218); do it with A-16 | at the next redeploy |
| A-15 | Optional: purge local session transcripts that hold the dead CWSO secret (SEC-T694-10, SEC-T695-06) | open, optional | - |
| A-16 | **Before the next CWSO redeploy** (`git pull` plus `docker compose up -d`), or the server loses LAN access: set `CWSO_HTTP_PUBLISH_ADDR` to the all-interfaces address in `deploy/.env`, or add a `ports: !override` entry to the local override (exact text in plan-129 § Outcome); make sure the JWT secret is at least 32 bytes; make sure the `CWSO_ALLOWED_ORIGINS` entries pass the new checks. The loopback guarantee needs Docker Engine 28 or later (SEC-T727-04; the user's version **(unverified)**) | open | before the next CWSO redeploy |
| A-17 | Set the project's minimum role for pipeline variables above Developer (SEC-T741-16; review T741 § 4; plan-138 § Outcome). Not checked here; the current value is **(unverified)** | open | - |
| A-18 | Check that the release tags are protected. Review T741 § 5 lists tag protection as unverified, and the merge guard's limit depends on it (plan-139's reading): a tag cut from a commit that never went through `unit-tests` is not guarded (contract 6, `tests/functional/test_ci_hash_pins.py:24-26`) | open | - |
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open (unchanged since v4; not re-checked) | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open (same) | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open (same) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- **Carried statuses**: v8 rows and lists, plus plan-138 and review T741. Greps and line reads on `544166c1` where cited.
- **Counting**: a script takes the 117 carried ids from v8 §§ 2.1 to 2.3 and 3, and the new ids from review T741 §§ 2 and 4 rather than from plan-139. It checks that each carried id occurs in section 2 of this register, compares the status of the rows of section 3 with the review, and expands section 5 to 75 distinct ids, equal to the carried ids still open or tracked plus the 6 new. Plan-139's expected counts were derived by the orchestrator; this check was run separately and they match: 561, 434, 46, 6, 1, 74, and all 13 batch sizes.
- **Where the sources differ or leave a gap** (none changes a status):
  - **SEC-T739-05.** Review T741 § 1 says "as the T739 review's fixes asked". Plan-138 went further, with a key allowlist. Both hold: the allowlist refuses what the reviewer named and more.
  - **SEC-T741-11.** The option of "Fix, narrow re-review (Recommended)" said it stays tracked. The later rule of SEC-T741-15 closed it for the same pipeline (review § 2), and SEC-T741-17 holds the rest.
  - **SEC-T741-03.** Plan-138 specifies an artifacts rule that the merged code no longer has as such: review § 2 says "replaced in part". The file-level part stands (`file_level_problems`, `:335`).
  - **"review go".** See section 4.1: only plan-139 holds the words.
  - **SEC-T741-08** has no path in the review; the test is in `tests/functional/test_verify_release_docs.py`.
  - **SEC-T741-13's "walker"** is not located by the review; `mapping_keys` is my reading (section 3).
  - **TD-T739-01** still has no grade (v8 § 8).
  - **Batch S's owner** comes from the heading of § 4 of the two reviews; T739's says "next sprint", T741's says "proposed". No source has scheduled a sprint for it.
- **What GitLab's lint proved** (the orchestrator, live, read-only, review T741 Metadata; not re-run here; the deployed version is unknown to the reviewers). `ci_pin_problems` at `68a70735` against the real file plus each edit:
  - every edit that softened `release-docs-gate` in GitLab's lint has at least one pin problem;
  - on a dry run with the tag `v9.0.0`, the real file runs exactly `main-develop-drift-gate`, `release` and `release-docs-gate`, and on `develop` it runs 7 jobs;
  - a job with `variables: {CI_COMMIT_BRANCH: y}` and `if: $CI_COMMIT_BRANCH` runs on the tag, and a control without the variable does not; a `pages` job, a job named `pages` and a plain job without rules run on the tag;
  - `extends` with its own rules and a hidden `when: always` does not run; `if` with `when: always` and `exists` does not run; a hidden `only: [tags]` with `rules` is invalid.
  - The lint shows what would run, not what a job does. It does not prove the install of `ci/requirements-release.txt` or any job's run.
- **What is a hand trace** (the two reviewers, read-only, no shell, no code run; review T741 Metadata and § 5). Every ruling of review § 1, and the review's PASS, rest on fetched GitLab and Psych source on master and on reading. From the reviewers' memory: Psych's scalar handling for block forms, `deep_symbolize_keys`, `extends` array merging and rule evaluation, and the orchestrator's lint runs agree where it ran them; that `rules:variables` is not a route; that a schedule can run on a tag ref. The second reviewer read `t741-round2.diff` for the first two commits' tests, not all of `t741-all.diff`; `read_strict` rests on the first review.
- **Reported, not re-run here**: the orchestrator's mutations on a throwaway copy (49, then 15 and 8), the implementer's 24 script mutations, the orchestrator's 7 script and about 28 pin mutations, and the final verification at the merged commit (2543 tests OK, 24 skipped; review Metadata; plan-138 § Outcome). No mutation and no full suite ran for this register.
- **Unverified**, carried from v8: the source of the "do first" flags other than the fixed SEC-T716-01; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates; which three gaps "Fix now in this batch (Recommended)" covered (v6 § 8); live GitLab rendering (SEC-T716-03); the npm step in a tag pipeline; the lock on the musl image beyond the MR pipeline; whether the orchestrator's draft of the upstream report was ever shown to the user; adoption of Trivy 0.76.1; the questions shown to the user beyond ADR-012 and plan-133; each carried plan's actual deadline; whether the gate tolerates the leftover pointer sentence; whether targets receive the gate script and the template; the install of `ci/requirements-release.txt` in a tag pipeline; GitLab's rendering of front matter and sanitized attributes (SEC-T739-02, -04); the flags on `WIKI_TOKEN` (SEC-T739-06), tag protection, and which runner holds the Docker socket; `pip-audit`, which did not run for T739 either; 4.2.0 for TD-T739-01; the merged commit's two later changes in T739, which its reviewer did not see; the source of `markdown-it-py` 4.2.0, and of 3.0.0 beyond two files; GitLab's real rendering and bash's behaviour on the eight characters and CR; the wording of SEC-T738-05 against the reviewer's report; the questions shown to the user for "N two go" and "parser go" beyond the plans; SEC-T730-06's code location.
- **Dropped from v8's list**: GitLab's rendering of **invalid bytes**. It was not proved: the gate now refuses such a file, so no gate result depends on it (SEC-T739-01). **Nothing else on v8's list was proved by plan-138.** Its lint runs do not reach any item there: the tag dry run shows which jobs would run, not the install, and the project settings stay unverified.
- **Unverified**, new, from review T741 § 5 and plan-138:
  - the deployed GitLab version;
  - delivery of artifacts from a `pages` job to the gates, not observed;
  - `parallel:matrix` on a tag, not run live, which the pin refuses anyway;
  - the project settings: protected tags, the configured CI file path, the minimum role for pipeline variables;
  - the merge guard's limit: `unit-tests` runs on merge request and branch pipelines, so a tag cut from a commit that never went through them is not guarded;
  - that the crash of 2026-11-05 came from the "no seen-set" mutation, an inference, because no system logs were read (plan-138 § Outcome);
  - the skip count: runs on plan-138's trees reported 13, 24 and 25, and the difference was not traced (plan-138 § Outcome);
  - SEC-T741-16's route and SEC-T741-17's state on a reused runner (section 3);
  - what "review go" answered (section 4.1).
- **Not re-run here**: the suite and the gates, which the orchestrator ran before the merge (plan-138 § Outcome). The reviewers' own unverified lists stand as written in their artifacts.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`, each with a time limit where it runs tests.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v8.md`; `plan-138-gate-pin-and-strict-read.md`; `plan-139-tracked-debt-register-v9.md`; `docs/tasks/task-T742.md`; `security-review-t741-gate-pin-v1.md`; by grep or line range, `security-review-t739-gate-parser-v1.md`, `scripts/verify-release-docs.py`, `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_verify_release_docs.py`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/check-version-consistency.py`, `scripts/dry-run-publish-release.py`, `docs/tasks/task-T741.md`, `docs/tasks/completed-tasks.md`, plan-137. Decision IDs: ADR-011, ADR-012, as v8 cites them, not read here.
