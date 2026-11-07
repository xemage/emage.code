# Artifact: tracked-debt-register-v10.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v9.md` (561 ids; v9 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-141-tracked-debt-register-v10.md` and `docs/tasks/task-T746.md` (the user's "1. Delete, 2. v10 go"); `docs/plans/plan-140-batch-s-release-gate.md`; `docs/artifacts/security-review-t745-batch-s-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01, superseded in part), ADR-012 (Accepted 2026-11-04), as v9 cites them, not re-read; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T746 (plan-141; the user's answer of 2026-11-06, verbatim: "1. Delete, 2. v10 go"). **Date**: 2026-11-06.
- **Tree read**: branch `agent/tech-lead/T746` at `0fee4505` (develop `615a7b0e` plus the plan commit, which adds plan-141, the brief and a ledger row). Commits since v9's merge `c4ffff6f`: `7e02cba5` (T743 and T744, squashed), `615a7b0e` (its merge), `0fee4505`. `git diff --stat c4ffff6f 0fee4505` lists, outside `docs/artifacts/`, `docs/plans/` and `docs/tasks/`, only `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/check-version-consistency.py`, `scripts/dry-run-publish-release.py`, `scripts/verify-release-docs.py` and the test files `test_check_version_consistency.py`, `test_ci_hash_pins.py`, `test_publish_release.py`, `test_publish_release_job_token.py` and `test_verify_release_docs.py`. So nothing under `implementation/`, `docs/decisions/` or `ci/`, and nothing in `scripts/install.sh`, `scripts/publish-release.py` or `scripts/check-release-tag-tree.py` changed since v9's tree, and v9's lines in those paths stand. The CI file's hunks start at line 198, and `CONTRIBUTING.md`'s at line 400; `docs/releases/_template.md` changed on line 3 only. The CWSO repository was not read: every CWSO status carries over from v9.
- **Review mode**: read-only. A closure cites plan-140 or review T745. "Unchanged" means no task, review or plan outcome since v9 names the id with a change of status, checked by searching the lines added in `c4ffff6f..0fee4505` (section 1.2). The code was not re-checked unless a line is cited. Anything not traced is **(unverified)**.
- **Reviewed tree**: review T745 read `8a1334a7`. `8ee1e2d3` came after it and changes `.gitlab-ci.yml` and `tests/functional/test_ci_hash_pins.py` only (`git diff --stat`). `git diff 8ee1e2d3 7e02cba5` holds only docs (the review, plan-140, the ledger and the T744 brief), and `.gitlab-ci.yml`, `scripts/` and `tests/functional/` compare equal, so the merged code is `8ee1e2d3`'s. Neither commit is an ancestor of `develop`; the commits citable there are `7e02cba5` and `615a7b0e`.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository, registers v1 to v8. Read beyond the brief's list, by grep or line range: `scripts/verify-release-docs.py`, `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_verify_release_docs.py`, `tests/functional/test_publish_release_job_token.py`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/check-version-consistency.py`, `scripts/dry-run-publish-release.py`, and `security-review-t730-t732-batch-g-v1.md` and `security-review-t734-t736-batch-h-v1.md` for the text of batch N and of SEC-T736-01. None is a register. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5.
- **Batch letters**: I, J, K, L, M, N, P, Q, R, T, F and U keep their v9 scope. **S** loses 13 ids, keeps 2 in part and takes 11 (section 5).

## 1. Summary

v10 holds **573 ids**: the 561 of v9 and **12 new**. After v10: **448 fixed**, **46 accepted**, **6 obsolete**, **1 open**, **72 tracked-LOW**.

- **Open above LOW: none.** The one open id is K-20 (live checks, user). Review T745 counts 0 CRITICAL, 0 HIGH and 0 MEDIUM. **v9's qualification on TD-T739-01 ends:** review T745 counts it among its 26 LOWs and tracks its rest as LOW (Verdict, § 4), which is the first reviewer's grade it has had. The one ungraded id, TD-T745-01, is closed. The five accepted MEDIUMs (section 6.1) are accepted, not open; under ADR-011 four of them need the user's new acceptance at the next release (section 6.2, item 2).
- **Batch S's 15 ids in v9**: 13 fixed, 2 open in part (TD-T739-01, SEC-T741-17). With the 11 new ones, S holds 13. **S stays open: no source binds it to a release.**
- **Every id the review closes was in batch S in v9.** All 15 of review T745 § 1 are in v9 § 5's row S, and none is in batch N. SEC-T738-02 and SEC-T738-06 came from the batch N two review, but v9 counts them in S.
- **Stale ids: none.** T743 and T744 moved the lines of three batch N ids and of batch T, and no finding lost its subject (section 5).
- **Project state since v9.** `ANTHROPIC_API_KEY` is deleted, A-17 and A-18 are closed by a read of the settings, and a gate probe ran the two gates in a real tag pipeline. The `release` job has still never run this code (section 8).
- **Due before the next release**: as in v9, SEC-T735-08 and SEC-T735-09 (section 6.2, items 2 and 10). **Any of batch S before the next tag stays open for the user.**
- **Open for the user now**: A-19, the probe tag, still on the remote when this register was written (section 7).

Arithmetic, from the v9 totals:

| Status | v9 | leaves | enters | v10 |
|---|---:|---|---|---:|
| fixed | 434 | | + 13 batch S + 1 new | **448** |
| accepted | 46 | | | **46** |
| obsolete | 6 | | | **6** |
| open | 1 | | | **1** |
| tracked-LOW | 74 | - 13 fixed | + 11 new | **72** |
| **all** | **561** | | + 12 new ids | **573** |

Check: 448 + 46 + 6 + 1 + 72 = 573. Open or tracked: 72 + 1 = 73, the size of section 5.

### 1.1 Ids by v9 status and status now

| v9 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 74 | 13 | 0 | 0 | 0 | 61 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 434 | 434 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v9 ids** | **561** | **447** | **46** | **6** | **1** | **61** |
| new in v10 | 12 | 1 | 0 | 0 | 0 | 11 |
| **all v10 ids** | **573** | **448** | **46** | **6** | **1** | **72** |

### 1.2 New ids by source and grade

| Source | new | LOW, tracked | Ungraded, closed |
|---|---:|---:|---:|
| `security-review-t745-batch-s-v1.md` § 4, SEC-T745 | 11 | 11 | 0 |
| The same file, "Not graded by a reviewer": TD-T745-01, the orchestrator's id | 1 | 0 | 1 |
| **All new** | **12** | **11** | **1** |

TD-T745-01 counts as `fixed` because v9's five statuses hold no other closed one that fits: its subject was removed, not overtaken; plan-141 says "closed by the user's deletion".

A search of the lines added in `c4ffff6f..0fee4505`, outside `tests/golden/`, for any `<PREFIX>-T<nnn>` id and any `<letter>-<n>` id, finds no other new id. `SEC-T745` and `SEC-T745-NN` are the review's and plan-140's way of naming the series. SEC-T703-01 and SEC-T715-03 are older ids in a moved `--help` line (`scripts/verify-release-docs.py:223`; the script already held them at `c4ffff6f`). The other carried ids it finds, SEC-T716-03, SEC-T735-06, SEC-T738-04, SEC-T739-07 and D-T710-2, appear as "stays open", "not changed", a test's forbidden phrase or plan-141's carried instruction, with no change of status. `M-3` is an example heading in a test. A-17 and A-18 are user-action numbers and A-19 is plan-141's new one. This register mints no debt id.

### 1.3 How the review's counts map to ids

| Grade | Review T745's count | Resolved | Remaining | As ids |
|---|---:|---:|---:|---|
| LOW | 26 | 13 | 13 | Resolved: the 13 changed ids of section 2.2. Remaining: SEC-T745-01 to -11, and the rest of TD-T739-01 and SEC-T741-17 |

"The 26 are the 15 ids of batch S and 11 new ones" (review Verdict). TD-T745-01 is not in the count.

## 2. v9 ids re-checked

Every v9 `open`, `tracked-LOW` and `accepted` id (121) has a row or a list entry here: 1 + 74 + 46. The v9 `fixed` and `obsolete` ids stay as v9 records them.

### 2.1 v9 `open` (1)

K-20: **Unchanged**, open, batch U (A-7).

### 2.2 v9 `tracked-LOW` (74)

**Changed (15, all batch S).** Rulings: review T745 § 1. Code: squash `7e02cba5`, merge `615a7b0e`. The user: "S go". Lines are current, read on `0fee4505`, in `scripts/verify-release-docs.py` unless the path says otherwise; "pins" means `tests/functional/test_ci_hash_pins.py`.

| Id | v9 | now | Evidence |
|---|---|---|---|
| SEC-T739-02 | tracked-LOW | **fixed** | An anchor holding HTML other than a comment does not count, on either side of the word and in a link: `anchor_text` `:586-594`; `--help` `:230-233`. Widened by the orchestrator's ruling (section 4.2) |
| SEC-T739-03 | tracked-LOW | **fixed, by refusal** | The first live HTML from the start of the document ends the search, at any depth: `holds_live_html` `:632-642`, the walk `:663-665`, `--help` `:225-230`. The review finds the widening sound. After the anchor: SEC-T745-03 |
| SEC-T739-04 | tracked-LOW | **fixed** | `FRONT_MATTER_OPENING_RE` `:150-153`; the refusal `:486-490`. A superset of GitLab's opening. Whether the Release description uses front matter stays **(unverified)** (review § 1). Its cost: SEC-T745-02 |
| SEC-T739-06 | tracked-LOW | **fixed, as asked** | The `unset` line opens the docs gate's `before_script`: `.gitlab-ci.yml:209`; `RELEASE_GATE_UNSET` and the pin, pins `:72-74, 87-88`. Residuals: SEC-T745-04, -05. The clone credential in `.git/config` stays, as the job's comment (`.gitlab-ci.yml:205-208`) and contract 6 (pins `:24-25`) say |
| SEC-T739-08 | tracked-LOW | **fixed** | `docs/releases/_template.md:3`; the error `:699-703`; `CONTRIBUTING.md:403` and `:439-440` point at step 4's install |
| SEC-T739-09 | tracked-LOW | **fixed** | `--help` `:234-236`, docstring `:20-21`; the label is now "What stays open" (`:246`, section 4.2), with the fixtures the review names |
| SEC-T738-02 | tracked-LOW | **fixed** | A CR in `scripts/install.sh` is refused, naming the line: `install_sh_cr_problem` `:679-688`, its read `:714-718`, `--help` `:243-245`. CRLF Markdown stays allowed (`read_strict`, `:289`) |
| SEC-T738-06 | tracked-LOW | **fixed** | Escapes, and a byte-level guard test (review § 1). `tests/functional/test_verify_release_docs.py` holds no raw U+2028 or U+2029 (counted on `0fee4505`) |
| SEC-T741-06 | tracked-LOW | **fixed** | `read_strict`, `scripts/check-version-consistency.py:120-126`, its calls `:178, 207`; `scripts/dry-run-publish-release.py:199`. `.gitlab-ci.yml:67`, the informational `markdown-links` job, stays lenient, as the plan says. A committed non-UTF-8 `.md` outside the exclusions now blocks the release (review § 2; section 6.2, item 20). Local side effect: SEC-T745-09 |
| SEC-T741-07 | tracked-LOW | **fixed, by a clause** | `--help` `:249-251`, with a test (review § 1). The behaviour stands: such a document is checked for existence only |
| SEC-T741-08 | tracked-LOW | **fixed** | The AST walk, `_read_route_problems`, `tests/functional/test_verify_release_docs.py:157`, used at `:1541`. Its limits: SEC-T745-08 |
| SEC-T741-12 | tracked-LOW | **fixed** | Exact values: `RELEASE_COMMAND`, `RELEASE_ARTIFACTS`, pins `:75-78`, in `PINNED_JOBS` `:104-108`; `DEFAULT_TAGS` `:115`, read at `:366`; `default.interruptible`, `:368`. The review: "Edits inside `release.before_script`'s Python string are not seen, and they do not skip a gate" (§ 2) |
| SEC-T741-16 | tracked-LOW | **fixed on this project** | The clause in contract 6, pins `:27-29`, plus the setting `ci_pipeline_variables_minimum_override_role` = `no_one_allowed` (plan-140 § Facts; plan-141 § Facts). It rests on a setting no test reads, as contract 6 says, and it holds while the setting stands |
| TD-T739-01 | tracked-LOW, ungraded | **tracked-LOW, open in part; now graded LOW** | Done: a document with a line over 65536 characters is refused before parsing: `MAX_LINE_CHARS` `:149`, `long_line_number` `:467-472`, `document_refusal` `:480-485`. Not done: a total bound. "A line limit does not bound parse time" (plan-140 § Outcome). Same fix as SEC-T745-01 (review § 4) |
| SEC-T741-17 | tracked-LOW | **tracked-LOW, open in part** | Done: `GIT_STRATEGY: clone` on both gates, `.gitlab-ci.yml:203, 222`, pinned, pins `:87, 94`. Not done: the dedicated runner tag, which needs a runner, so the Docker socket route stays **(unverified, runner-dependent)** (review § 1, § 4). `release` keeps `fetch`: SEC-T745-07 |

**Unchanged (59 tracked-LOW; v9 and earlier stay the record of their text)**

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
| T | SEC-T739-07 | 1 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 5 |

Total 59; with the 15 above, 74.

### 2.3 v9 `accepted` (46)

**All unchanged**; basis as in v5 § 2.3, v6 § 6.1 and v7 § 2.3. None has a new acceptance.

- **MEDIUM (5)**: SEC-T657-01 / SEC-T658-01 (one id), SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07.
- **LOW or INFO (41)**: K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, K-15, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07.

## 3. New ids

Source: review T745 § 4, where each id's fix is. The reviewer read `8a1334a7`; the names below were found again on `0fee4505`. Owner of the tracked ids per review § 4's heading: devops-engineer, "proposed"; "next sprint". Lines are current, in `scripts/verify-release-docs.py` unless the path says otherwise; the review gives names only, so each line here is my reading.

| Id | Grade | Location now | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T745-01 | LOW | `MAX_LINE_CHARS`, `:149`; `document_refusal`, `:475` | Unclosed `<!-- `, `<? ` and `<![CDATA[ ` are quadratic in the **paragraph**, and lines join, so the line limit does not bound it. Measured: about 10 s for 65 KB, over 90 s (stopped) for 200 KB. Worst case, the job stalls until the 3600 s timeout and fails closed. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-02 | LOW | `FRONT_MATTER_OPENING_RE`, `:153` | Polynomial on a first line of `coding:` repeats plus a long blank run. 12.75 s measured on 165 KB. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-03 | LOW | `has_cursor_migration_item`, `:645`; `--help`, `:229-230` | `<style>h3{display:none}</style>` after the anchor gives True (the orchestrator confirmed it) and hides the anchor in a browser. GitLab's sanitizer should strip it **(unverified, from memory)**. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-04 | LOW | `main-develop-drift-gate`, `.gitlab-ci.yml:216-232` | `apk add` and the scripts see every credential, while `release` filters `apk`'s environment. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-05 | LOW | `release-docs-gate`, the `unset` line, `.gitlab-ci.yml:209` | A denylist: a later project variable stays visible, as `ANTHROPIC_API_KEY` was. The credential's location varies by runner mode. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-06 | LOW | Contract 6, `tests/functional/test_ci_hash_pins.py:16-32`; `.gitlab-ci.yml:203, 222` | Project variables outrank job `variables` **(from memory)**, so a project-level `GIT_STRATEGY` beats the pin with every test green. The project has none today (plan-141 § Facts: the only variable left is `WIKI_TOKEN`). | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-07 | LOW | `release`, `.gitlab-ci.yml:234-252` | The job that publishes with the token stays on `fetch`. The runner cleans `.git/config` and hooks there on non-shell executors, so the risk is small. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-08 | LOW | `_read_route_problems`, `tests/functional/test_verify_release_docs.py:157`; `test_the_parser_has_one_call_site`, `:1580` | `str(raw, "utf-8", "ignore")` inside `read_strict` passes the walk. A module-level `PARSER = MarkdownIt(...)` or an alias passes the second test. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-09 | LOW | `find_markdown_files`, `scripts/check-version-consistency.py:190` | A non-UTF-8 `.md` in `ci/js/node_modules` or an in-tree virtual environment now fails a local run. No effect in CI. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-10 | LOW | `evaluate`, `scripts/check-version-consistency.py:221` | Drift lines print the path unescaped in a standalone run. | tracked-LOW | devops-engineer (proposed) | S |
| SEC-T745-11 | LOW | `document_refusal` docstring, `:476` | "before reading it for anything else" is loose: `check_line_breaks` runs before it and `check_links` after it on the tag's own document. | tracked-LOW | devops-engineer (proposed) | S |
| TD-T745-01 | none: the orchestrator's id, never graded by a reviewer | The project's CI/CD variables; the name in `.gitlab-ci.yml:208-209` and `GATE_CREDENTIALS`, `tests/functional/test_ci_hash_pins.py:72` | `ANTHROPIC_API_KEY` was a project variable, masked and not protected, so it reached every job on every branch, and no job named it. | **fixed**: closed by the user's deletion. The orchestrator listed the names through the API on 2026-11-06: the only one left is `WIKI_TOKEN`, protected (plan-141 § Facts; not re-read here). The user says the key "was already revoked anyway"; its value was never read, so no one else has checked that **(unverified)**. The name left in the two lines is harmless and can go at the next change to them | the user | - |

## 4. Decisions since v9

### 4.1 The user's (words verbatim as recorded)

Each row claims only what plan-140 or plan-141 records. The questions as shown to the user were not verified beyond those records **(unverified)**. Plan-141 dates only the last and the probe: the other undated rows fall on 2026-11-06 by the order of events the plans give (my reading).

| Date | Words | What the question asked, and the effect | Source |
|---|---|---|---|
| 2026-11-06 | "S go" | Plan-140, T743 and T744, on batch S | plan-140 Based on |
| not dated | "rc go" | The orchestrator had offered a release candidate as proof "without a real release", which was wrong: `CONTRIBUTING.md` § Pre-release tags says "There is no lighter path". Neither plan records a release candidate cut on this answer. The question recorded next on how to prove the untested steps is the "Gate probe tag" row | plan-141 § Facts |
| not dated | "I deleted ANTHROPIC_API_KEY from Gitlab. The key was already revoked anyway." | Closes TD-T745-01, whose decision the review and plan-140 left to the user | plan-141 § Facts |
| not dated | "Gate probe tag (Recommended)" | Asked how to prove the untested steps. The orchestrator ran the probe on 2026-11-06 | plan-141 § Facts |
| 2026-11-06 | "1. Delete, 2. v10 go" | Approves deleting the probe tag (now A-19) and runs T746 (this register) | plan-141 Based on, § Facts |

### 4.2 Other decisions (not the user's)

| Id or item | Decision | By | Effect |
|---|---|---|---|
| SEC-T739-02, -03 | T743's first report left three routes open (inline HTML in an earlier paragraph, raw HTML above the section, a hidden section title). Confirmed on 4.2.0 and ruled into one rule, "because listing places was the mistake T741 made three times". The reviewer finds the widening sound | the orchestrator (plan-140 § Outcome) | section 2.2; section 6.2, item 22 |
| `exit 0` in `release.before_script` | T744's report said it passes. The reviewer corrected that, and the orchestrator confirmed it on a copy: `test_the_bootstrap_is_the_exact_text_that_yaml_parses_to` (`tests/functional/test_publish_release_job_token.py:431`) catches it, and `ci_pin_problems` itself does not | the orchestrator (plan-140 § Outcome; review Metadata) | none on status |
| The `--help` label | "What stays open" stands, as T743 chose | the orchestrator (plan-140 § Outcome) | SEC-T739-09 |
| SEC-T745-01 to -11 | Stay tracked under the user's policy, and none is folded in | the orchestrator (plan-140 § Outcome) | section 3 |
| `8ee1e2d3` | Adds `ANTHROPIC_API_KEY` to the docs gate's `unset` line and pin. **An orchestrator edit after the review, and not re-reviewed** | the orchestrator (plan-140 § Outcome; review Metadata, § 5) | section 8. It ran in the probe's real job, on `57612f29`'s tree |
| "Well under a second" | Plan-140's figure for a document at the limit was wrong; the line limit does not bound parse time | the orchestrator (plan-140 § Outcome) | SEC-T745-01 |
| The release candidate offer | "Without a real release" was wrong, and the orchestrator says so | the orchestrator (plan-141 § Facts) | section 6.2, item 24 |
| The tag's deletion | `git push --delete` was refused. The orchestrator did not try the API and handed the step to the user | the orchestrator (plan-141 § Facts) | A-19 |
| Batch S | Keeps two ids and takes the 11 tracked ones; stays open | plan-141 | section 5 |

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. I, J, K, L, M, N, P, Q, R, T, F and U are carried from v9 without change; in those rows "review" and "review § 4" mean the batch H review, except where a row names another.

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
| **S** | Release gate: what the batch S review left | SEC-T745-01, TD-T739-01 (the rest), SEC-T745-02, SEC-T745-03, SEC-T745-04, SEC-T745-05, SEC-T745-06, SEC-T745-07, SEC-T741-17 (the rest), SEC-T745-08, SEC-T745-09, SEC-T745-10, SEC-T745-11 | 13 | devops-engineer (review T745 § 4, "proposed"); SEC-T741-17's runner is the user's to provide | **open, for the user**: review T745 § 4 says "next sprint", no sprint is scheduled, and no source binds S to a release |
| T | Verdict placeholder check on the token stream | SEC-T739-07 | 1 | devops-engineer (review T739 § 4) | none set: review T739 § 4 says only that it needs its own plan, and plan-136 § Outcome agrees. Plan-140 § Not changed confirms it stays out |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 10 + 1 + 7 + 5 + 12 + 8 + 1 + 3 + 4 + 13 + 1 + 2 + 6 = 73 = 72 tracked-LOW + 1 open. No open item is above LOW.

**Batch N, re-read on `0fee4505`.** T743 moved the gate script's regexes by ten lines, and **no id is stale**: `sed` shows the regex block unchanged, and the new line limit reaches release documents only, not the `install.sh` lines these regexes read. Plan-140 § Not changed kept these regexes out. The other five ids sit in files or lines T743 and T744 did not change; I did not re-run any.

| Id | v9's line | Now | Reading |
|---|---|---|---|
| SEC-T730-03 | `publish-release.py:629, 750` | same | File unchanged |
| SEC-T730-04 | `ci/requirements-ci.in`, `ci/requirements-ci.txt:2-4` | same | `test_ci_hash_pins.py` still has no `generated-on` or cooldown check, by grep |
| SEC-T730-06 | not located | not located | File unchanged. **(unverified)**, as in v9 |
| SEC-T731-03 | `verify-release-docs.py:165, 169` | `:175, 179` | `POINTER_LIKE_RE`, `:174-181`, unchanged, moved. **v9's "long-line test" is not this regex's:** `test_a_long_tag_line_does_not_slow_the_gate`, now `test_verify_release_docs.py:752`, times the parser, and that file does not name `POINTER_LIKE_RE`. So the reviewer's timing test is still to write |
| SEC-T731-04 | `verify-release-docs.py:164-171` | `:174-181` | Same regex, moved |
| SEC-T731-05 | `verify-release-docs.py:190`, `check-release-tag-tree.py:48` | `:200`; `:48` | `UNSAFE_RE`, moved. The equality test is at `test_verify_release_docs.py:1768` |
| SEC-T732-01 | `.gitlab-ci.yml:93-104` | same | The CI file's hunks start at `:198` |
| SEC-T732-02 | `ci/js/README.md:39-43` | same | Directory unchanged |

**Batch S and T, re-read on `0fee4505`.** The text of each id stays in review T745 § 4 and, for SEC-T739-07, in v8 § 3 and review T739 § 4. The SEC-T745 lines are in section 3.

| Id | v9's line | Now | Reading |
|---|---|---|---|
| TD-T739-01 (rest) | `has_cursor_migration_item`, `:552`, the parse at `:559` | `:645`, the parse at `:657`; the guard `:655-656` | Subject now the total bound (section 2.2). The figure is measured on 4.2.0: worse than linear (plan-140 § Facts) |
| SEC-T741-17 (rest) | `.gitlab-ci.yml:196-206, 208`; `:97`; pins `PINNED_JOBS`, `:67-91` | `.gitlab-ci.yml:196-214, 216-232`; `:97`; pins `:84-109` | Subject now the runner tag. `unit-tests` has `tags: [dind]` (`.gitlab-ci.yml:93-94`) and the gates inherit `DEFAULT_TAGS`, `docker` (pins `:115`). Whether one runner holds both is **(unverified)** |
| SEC-T739-07 (T) | `section_text`, `:284-296`; `verdict_placeholder_problems`, `:299-310` | `:316-328`; `:331-342` | Moved; both function bodies compare equal |

**Batch S, in short.** Review T745 § 4's id order is by number. **The order above is my suggestion; no source sets it.**

- **SEC-T745-01 and TD-T739-01 first (suggestion):** the review gives them one fix, a job `timeout`, a total size cap and the bound stated in `--help`, and "a cap alone is not enough". `GATE_KEYS` (pins `:82`) and the job's `keys` hold no `timeout`, so the pin changes with it (my reading of the pin). SEC-T745-02 is the same class in the same refusal.
- **SEC-T745-03 next (suggestion):** on a CommonMark render it is "the only route found" for a crafted document that passes while a reader cannot see the anchor (review § 2).
- **SEC-T745-04 to -07 and SEC-T741-17 together (suggestion):** each edits the tag jobs and their pins in one file. SEC-T745-06 is a clause in contract 6 and a rule for the project's variables. SEC-T741-17 last of them, because it needs a runner, which is the user's.
- **SEC-T745-08 to -11 last (suggestion):** tests, a local run, a log line and a docstring.
- **Plan-140's goal** said to close batch S "before the next tag". That sentence covered the 15 ids it took; no source applies it to these 13, so the question stays with the user (section 8).

**Batch T, in short.** Carried from v9. SEC-T739-07 is the same class as batch S in another check. The orchestrator confirmed the three shapes on the commit (review T739 Metadata). The reviewer's fix reads these sections from the token stream, or at least refuses a second occurrence of the heading. Plan-136's design scope kept this check on line rules, so a fix extends the parser's use beyond what "parser go" asked **(tech-lead's reading in v8; no source says so)**.

**Batch R, in short.** Carried from v9. **The route of SEC-T735-06 and -07 is still to be settled before batch R.**

- **SEC-T735-07: confirm the route first.** The reviewer's fix, "An acceptance covers", changes ADR-011's A1 text, and accepted ADRs are immutable (ADR-012 Status). The route is not settled; the review says only to confirm it.
- **SEC-T735-06** has the same question (tech-lead's reading in v8, no source says so): its fix, that `mitigation` cites where the plan was shown, changes the Conditions line, which is ADR-012's row B3. The top-level session's comparison would be a new duty too.
- **SEC-T736-01 (the rest)** needs pins and mutations only, in the style of T736, and no knowledge text.
- **SEC-T693-07 has no text fix**: "the independent check is a duty in the role text, not an enforced control" (plan-133), and the residual is accepted by ruling with no edit. Batch R must not edit for it. It closes only if an enforced control is built, and nothing here proposes one.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 § 6.1 and v6 § 6.1 stand unchanged and stay the record, with v7, v8 and v9 § 6.1. Plan-140 adds and renews no acceptance: review T745 found no MEDIUM. ADR-012 replaces rows A1, A8 and A12 of ADR-011 in part; the rest of ADR-011 stands: only the user accepts, one release only.

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 pin audit **2027-01-30 or the first Brave release above 2.1.4**; SEC-T702-09, SEC-T660-01, SEC-T665-01 and the SEC-T657-01/SEC-T658-01 remainder: **the next release needs the user's new acceptance** (ADR-011, ADR-012).

### 6.2 Next release checklist

Carried from v9 § 6.2, with its numbers. Items 7, 14 and 20 are rewritten where plan-140 or plan-141 changed them, items 6 and 8 each gain one clause on the probe, and items 21 to 24 are new. Every line that points into `scripts/verify-release-docs.py` or `tests/functional/test_ci_hash_pins.py` was read again on `0fee4505` (items 7, 15, 16, 17, 18, 19, 20). Items 1 to 6 and 8 to 13 are otherwise v9's text: their paths did not change, or changed elsewhere in the file (see Metadata), and their lines were read on `a4c3c7b3` or `8292c1bb`, under `implementation/knowledge/` unless the path starts at `docs/` or `scripts/`. In those items "review" means the batch H review.

1. **Migration item T725 (TD-T671-P5)** in the release document: authoring-only commands are no longer installed into target projects; commands declare `audience: authoring | target | both`; today only `/prepare-release` (five platform paths listed in plan-128 § Outcome); `--update`/`--projections-only` deletes an existing copy (a dry run prints the `rm`); an authoring checkout (`implementation/registry/index.json`) keeps them; a target that used `/prepare-release` keeps its own copy under another file name; `.generated-manifest.json` gains `authoringOnly`; the generator refuses a command without a valid `audience:`.
2. **ADR-011 re-acceptances**: the Release Gate input lists every MEDIUM an earlier release shipped under the user's acceptance and not yet fixed (SEC-T720-01 fix, `validation-gates/SKILL.md`): **SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09**. Each one is fixed, or the user accepts it again for this release, verbatim and dated, with its remediation plan (owner, fix, deadline). No agent grants or carries one over.
   - **When asking the user to re-accept any of these four (SEC-T735-08; ADR-012): name the release, record the plan as shown, and show a deadline still ahead.** The rule text does not say whether a new acceptance cures a deadline that has already passed, so do not put that case to the user as if it were settled.
   - Each carried plan's actual deadline was not verified by the reviewer (review § 5) or here **(unverified)**: read it before asking.
3. **New verdict fields** (R4, R10): `Issued at commit` and `Independent check` (`docs/releases/_template.md:87-88`; `commands/prepare-release.md:59-60`). The independent check row must be present, current and not FAIL (SEC-T693-02).
4. **TD-T723-01 (batch Q)**: the release document cites current `install.sh` lines. `docs/releases/v9.0.0.md:86` cites `install.sh:1300`, and `:75` cites `install.sh:1285-1302`, which v5 did not mention. On `a4c3c7b3` the advice is `scripts/install.sh:1297-1300` and the pointer is `:1301`; re-read them when the document is written.
5. **Brave**: if the release falls after 2027-01-30 or after a Brave release above 2.1.4, the pin audit needs a new acceptance version or the bump first.
6. **D-T710-2**: confirm in the release job that the `CHANGELOG.md` entry lands below `[Unreleased]` (fixed in code by T716; not yet observed in a tag pipeline; the gate probe's `release` job was skipped).
7. **Visible changes of batch G** (plan-131 § Outcome) **and batch S** (plan-140 § Outcome), for the release document and its author:
   - `CHANGELOG.md` entries now show `\#42`, `\@user` and URLs in backticks in their source, and `(#42)` no longer links to the issue.
   - **The blank-line rule is gone, and `## Migration Guide <!-- x -->` now counts** (plan-136 § Outcome). The gate reads the document with `markdown-it-py`'s CommonMark parser (`verify-release-docs.py:212-245` is the `--help` text, `:566-676` the code). The section is the first top-level level 2 heading whose text is exactly `Migration Guide`, in ATX or setext form, up to the next top-level level 1 or 2 heading in either form; a heading inside a blockquote or a list neither opens nor ends it. The Cursor item is, in that section, with the case-sensitive word `Cursor` in its text, either a top-level heading of level 3 to 6, or a paragraph, top-level or with only list containers around it, that opens with a `**` strong span, and only the text inside that span counts. Text means text and inline code, with a line break read as a space; an image's alt text never counts, and an anchor holding HTML other than a comment does not count at all (item 22). `__bold__`, an anchor in a blockquote and a heading in a list do not count.
   - **What still follows from that rule:** a bold lead must open its own paragraph. `Some text` followed on the next line by `**Cursor**` is one paragraph, so it does not count, and a blank line is still what a release author needs there. A heading does not need one. Run in v8 on the local `markdown-it-py` 3.0.0; the orchestrator ran the same shapes on the locked 4.2.0 with the same results (plan-137 § Outcome). The error at `:699-703` now says "a paragraph that opens with a '**' span holding the word, optionally in a list" (SEC-T739-08).
   - **Checked files may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`.** They are the tag's release document, the three marker files and now `scripts/install.sh` (SEC-T731-07) (`verify-release-docs.py:192`, `:782`). The error names the file, the line and the code point.
   - **New refusals (batch S).** A release document the gate reads is refused, naming its path, if it opens with `---`, `+++` or `;;;`, optionally after a BOM, white space or a `coding:` line (SEC-T739-04), or if a line is longer than 65536 characters (TD-T739-01) (`--help` `:237-242`; `document_refusal`, `:475-491`). `scripts/install.sh` may hold no CR, CRLF included (SEC-T738-02; `--help` `:243-245`). CRLF in a release document stays allowed.
8. **Not verified live in plan-131; watch these in the release**:
   - how GitLab renders the escaped references and code spans;
   - the npm step (`npm ci --ignore-scripts --prefix ci/js`) in a tag pipeline;
   - the lock on the musl image beyond the MR pipeline. The gate probe's install covers `ci/requirements-release.txt` on the `python:3.12-alpine` image only; I read this item as being about the CI lock, and no source says which (my reading).
9. **The Conditions block** (`agents/release-manager.md:183`, ADR-012 B3): an accepted `SECURITY:MEDIUM` fills `risk_accepted_by=` with the user's words verbatim and the date, `grade=`, `release=` (the version the user was asked about), and `mitigation=` with the plan as shown to the user, its owner and fix, and the current owner if it has changed; `deadline=` holds the plan's deadline.
10. **The template's pointer sentence** (`docs/releases/_template.md:90`; SEC-T735-09): remove it before the independent check, or leave it. Deleting it after the check makes the check stale. That the gate tolerates the leftover sentence is T736's report; the reviewer did not verify it (review § 5).
11. **The independent checker** (`agents/release-manager.md:46`): "The checker has not authored or edited the release files for this release; if the checker has, the row counts as missing." The orchestrator or the top-level session will often be ineligible, so `@tech-lead` is the practical default (review § 1; plan-133 § Outcome). If the checker edited the files, another eligible checker re-runs it.
12. **Batch H changes a release author sees**:
    - after the check, only the closed list in `agents/release-manager.md:46` may change ("No other text may be added after the check"); it includes "Changelog Preview (a summary of the checked changelog, nothing new)";
    - hotfix eligibility (`skills/release-workflow/SKILL.md:171`): the issue is present in the released version, and is graded critical or high on its own scale, or, whatever its grade, is a breach of an Immutable Security Constraint or a required control omitted, removed, disabled or weakened, which `@security-engineer` confirms. A fix with design impact does not take the fast track (`:202`).
13. **Not verified in batch H**: whether targets receive `scripts/verify-release-docs.py` and `docs/releases/_template.md` (review § 1). The migration note must not assume that they do. A grep of `scripts/install.sh` finds no `rsync` or `cp` line naming `scripts` or `docs`, and its one mention of the gate script is a comment (`:1296`). That is a grep and not an install, so the question stays **(unverified)**.
14. **Keep watching `release-docs-gate` at the next tag** (`.gitlab-ci.yml:196-214`; the job's rule is the tag rule; plan-140 § Not verifiable before the next tag). No merge request pipeline runs its install. The gate probe ran the job's `unset` line, the gate's hash-locked install and the gate in a real job (pipeline 3037074733, job 17809865375; plan-141 § Facts). Its document was a copy of v9.0.0's. **What remains is the `release` job**, skipped in the probe: `scripts/publish-release.py` has changed since v9.0.0, so the `CHANGELOG.md` entry below `[Unreleased]` (item 6) and the escaped references (item 8) are still unobserved. Each publishing step needs the user's approval. The probe's other limits are in section 8.
15. **The job must stay without `allow_failure`** (review T739 § 1; plan-138 § Outcome). `allow_failure` on any tag job now fails a test (`pinned_job_problems`, `tests/functional/test_ci_hash_pins.py:327-347`; SEC-T739-05, SEC-T741-02). The job must still stay without it: a PyPI outage fails the job closed, that outage is when someone will be tempted to add it, and `needs` in `release` does not stop a release after an allowed failure.
16. **A local gate run needs the parser.** Without it, every gate run exits 1 and prints the install command, which is the one to use, in a virtual environment (`verify-release-docs.py:159-165`; `CONTRIBUTING.md:164-167`): `python3 -m pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt`. A developer's system package may be another version; the job's locked run decides (plan-136 § Design).
17. **A regeneration of `ci/requirements-ci.txt` needs `ci/requirements-release.txt` too**: `test_the_release_lock_matches_the_ci_lock` (`tests/functional/test_ci_hash_pins.py:653`) enforces the versions and hashes (plan-136 § Outcome).
18. **A new job in `.gitlab-ci.yml` needs an `if` from `NOT_TAG_CONDITIONS`** (`tests/functional/test_ci_hash_pins.py:117-122`; `tag_runnable_job_problems`, `:373-391`; plan-138 § Outcome). Adding a condition is a visible test edit and means checking that it is false on a tag: `$CI_PIPELINE_SOURCE == "schedule"` alone would not be, because a schedule can run on a tag ref (review T741 § 1, the reviewer's memory).
19. **A digest bump across all jobs passes; an `apk` pin or a Python minor bump needs a test constant edit** (plan-138 § Outcome; review T741 § 1: "with a clear message"). The constants I read are `PINNED_IMAGE` (`tests/functional/test_ci_hash_pins.py:80`) and the drift gate's `before_script` (`:95`). **The CI header's bump recipe does not say so yet** (`.gitlab-ci.yml:23-26`). This is a fact for whoever bumps an image; fixing the header is not scheduled.
20. **A checked file must be valid UTF-8, and the gate names the path and offset** (SEC-T739-01; `verify-release-docs.py:273-289`), never the content. The rule covers what the gate reads in this process (`:28-32, 257-262`). **The child `scripts/check-version-consistency.py` now reads strictly too** (SEC-T741-06; `:120-126`), so a committed non-UTF-8 `.md` outside its exclusions now blocks the release (review § 2). A pointed document on an `install.sh` line without "Cursor" is checked for existence only (SEC-T741-07; `--help` `:249-251`). Plan-140 records the real tree's `--tag v9.0.0` run as its acceptance; it was not re-run here.
21. **A new CI/CD variable needs adding to `GATE_CREDENTIALS` and to the `unset` line** (`tests/functional/test_ci_hash_pins.py:72-74`; `.gitlab-ci.yml:209`; plan-140 § Outcome). No test reads the project's variables, so nothing fails if this is missed (SEC-T745-05). The name `ANTHROPIC_API_KEY` stays in both lines; that is harmless, and it can go at the next change to them (plan-141 § Facts).
22. **A release document may hold no HTML other than comments before its Cursor item** (plan-140 § Outcome; `has_cursor_migration_item`, `verify-release-docs.py:663-665`; `--help` `:225-233`). This holds anywhere from the start of the document, at any depth, even if the tag closes itself, and the document then fails the gate. HTML after the anchor does not matter (see SEC-T745-03). None of the 33 documents holds such HTML (plan-140 § Outcome).
23. **A change to the release script needs the same edit in `RELEASE_COMMAND`** (plan-140 § Outcome; `tests/functional/test_ci_hash_pins.py:75-77`). I read "release script" as the `script` line of the `release` job (`.gitlab-ci.yml:246`), which the pin compares exactly, and not the body of `scripts/publish-release.py` (my reading of the pin).
24. **A release candidate is a full release** (`CONTRIBUTING.md` § Pre-release tags, "There is no lighter path"; plan-141 § Facts): it needs the content on `main`, creates a GitLab Release with no pre-release flag, and needs the four ADR-011 re-acceptances (item 2). **A gate probe tag** proves the gates without `main`, a Release or acceptances; it does not prove the `release` job, and the drift gate's tree check refuses it, by design. It needs the user's approval, and a protected tag can be deleted only in the web interface. Plan-140's two sentences that a release candidate "would prove" these steps first are read with this item.

### 6.3 Dates

Carried from v9 § 6.3. Plan-140 and plan-141 add none.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced; CWSO not read **(unverified)** | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v6, v7, v8 and v9, which did not re-read them; nor did I **(unverified)**.

Not a debt date, carried from v9's note: `.gitlab-ci.yml:18` holds `ci_images_reviewed_on: 2026-10-22`, and `MAX_REVIEW_AGE_DAYS = 120` (`tests/functional/test_ci_hash_pins.py:1194`) is what `test_the_review_date_is_present_and_fresh` (`:1222`) enforces. By reading, not by running it, the test starts to fail after 2027-02-19.

## 7. User actions

Carried from v9 § 7. A-17, A-18 and TD-T745-01's action close, and A-19 is new. I did not re-check any other state.

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
| A-17 | Set the project's minimum role for pipeline variables above Developer (SEC-T741-16) | **closed**: read through the API on 2026-11-06, no setting changed: `ci_pipeline_variables_minimum_override_role` is `no_one_allowed` and `restrict_user_defined_variables` is true, which is stricter than A-17 asked (plan-140 § Facts; plan-141 § Facts; not re-read here) | - |
| A-18 | Check that the release tags are protected | **closed**: `v*` tags are protected and Maintainers may create them (same read). **The limit stands:** a Maintainer can still tag a commit that never went through a merge request, so the merge guard does not cover that tag (contract 6, `tests/functional/test_ci_hash_pins.py:30-32`) | - |
| A-19 | **Delete the tag `v9.0.0-gate.1` in the web interface.** The user approved it ("1. Delete"). `git push --delete` is refused: "GitLab: You can only delete protected tags using the web interface." The local tag is deleted. The tag sorts below `v9.0.0` and does not change the previous-tag lookup (plan-141 § Facts) | **open**: `git ls-remote --tags origin` still listed it when this register was written, 2026-11-06 (my read) | - |
| TD-T745-01's action | Delete the variable if unused, or protect it; rotate if in doubt (review T745 § 4) | **closed**: the user deleted it (section 3) | - |
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open (unchanged since v4; not re-checked) | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open (same) | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open (same) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- **Carried statuses**: v9 rows and lists, plus plan-140, plan-141 and review T745. Greps and line reads on `0fee4505` where cited. Plan-141 § Facts is the only source for the variable, the two settings and the probe: I did not call the API.
- **Counting**: a script takes the 121 carried ids from v9 §§ 2.1 to 2.3 and 3, and the new ids from review T745 § 4 rather than from plan-141. It checks that each carried id occurs in section 2 of this register, and expands section 5 to 73 distinct ids, equal to the carried ids still open or tracked plus the 11 new. Plan-141's expected counts were derived by the orchestrator; this check was run separately and they match: 573, 448, 46, 6, 1, 72, and all 13 batch sizes. All 15 ids of review T745 § 1 are in v9's row S.
- **Where the sources differ or leave a gap** (none changes a status):
  - **Plan-140 § Goal and batch S.** Plan-140 says "Close batch S before the next tag". Plan-141 says no source binds S to a release. Plan-140's sentence came with its 15 ids; its Outcome and the review give the remaining 13 no such date, so I follow plan-141 and flag it for the user.
  - **The `unset` list.** Plan-140 names four variables. The merged line holds seven: T744 added `CI_DEPENDENCY_PROXY_PASSWORD` and `CI_DEPLOY_PASSWORD` after checking GitLab's documentation (pins `:70-73`), and `8ee1e2d3` added `ANTHROPIC_API_KEY`. Plan-140 asked for that check, so it is within the plan.
  - **TD-T739-01's grade.** v8 and v9 file it without a reviewer's grade. Review T745 counts it in its 26 LOWs and lists its rest under "tracked as LOW debt". I read that as its grade.
  - **SEC-T741-16.** The review says "Closed on this project". It counts here as `fixed`, with the condition in section 2.2.
  - **SEC-T731-03.** v9 called `test_verify_release_docs.py:698` "the long-line test"; it times the parser, not this regex (section 5). The status does not change.
  - **Review T745 § 4's locations** are names, without lines; the lines in section 3 are my reading.
  - **Plan-140's "A release candidate would prove them first"** (§ Not verifiable, § Outcome; review § 2) predates plan-141's correction; section 6.2, item 24 holds.
- **What a real job proved** (pipeline 3037074733, tag `v9.0.0-gate.1` on `57612f29`, 2026-11-06; plan-141 § Facts; jobs not re-read here). `git show --stat 57612f29` confirms its parent is `615a7b0e` and that it changes the three marker files and adds a release document; no local or remote-tracking branch contains it.
  - `release-docs-gate` (job 17809865375), success: the `unset` line ran, the hash-locked install passed, and `verify-release-docs.py` passed.
  - `main-develop-drift-gate` (job 17809865376), failed as designed: `apk`, both fetches under `GIT_STRATEGY: clone` and the drift check passed, then `check-release-tag-tree.py` refused the tag.
  - `release` (job 17809865377), skipped; no GitLab Release was created. So `needs` held on a failed gate in a real pipeline (my reading of the skip).
- **What the probe does not prove** (plan-141 § Facts):
  - the `release` job did not run, and `scripts/publish-release.py` has changed since v9.0.0, so the `CHANGELOG.md` entry below `[Unreleased]` (D-T710-2) and the escaped references are still unobserved;
  - the log shows the `unset` line ran, not that the variables were gone afterwards;
  - the log reads "Fetching changes" and "Created fresh repository" on both gates, which a fresh runner might print under fetch as well **(unverified)**, so it shows the setting works with these jobs, not that it changed anything;
  - the install is quiet, so the log does not name the parser's version; the hashes are what tie it to the lock.
- **What was run locally on the tag** (the orchestrator, plan-141 § Facts; not re-run here): the docs gate and the drift check passed and the tree check exited 1. `resolve_previous_tag` still returns `v9.0.0` for `v10.0.0` and `v9.0.1`.
- **What GitLab's lint proved** (the orchestrator, live, read-only; not re-run here; the deployed version is unknown to the reviewers).
  - At `8a1334a7`, review T745 Metadata: the real `.gitlab-ci.yml` is valid with no warnings; a dry run on `v9.0.0` runs exactly the three pinned jobs and on `develop` the other seven; the merged YAML shows `GIT_STRATEGY: clone` on both gates and the `unset` line first. `8ee1e2d3` came after this lint.
  - At `68a70735`, v9 § 8 stands for the T741 edits: job selection only.
  - The lint shows what would run, not what a job does.
- **What is a hand trace** (the reviewers, read-only, no shell, no code run; review T745 Metadata and § 5; v9 § 8 for review T741).
  - Review T745's rulings are hand traces, apart from the orchestrator's checks in its Metadata. `markdown-it-py` 4.2.0's source was not read. GitLab's `front_matter.rb` and the runner's `shells/abstract.go` are master, read through a summarising fetch, not the deployed versions. Docker executor details and variable precedence are from memory.
  - The routes that "fail" in review § 2 (reference definitions, images, entities, setext headings, paragraph continuation, breaks, HTML in link text) are hand traces.
  - The orchestrator's live shapes and timings on 4.2.0 are in review T745 Metadata, measured with the full suite running on the same machine.
- **Reported, not re-run here**: T743's 83 of 83 mutations caught, after one real gap was closed; T744's "all caught", after one real gap was closed and an equivalent mutant led to a simpler read; the orchestrator's re-run of about 30 shapes and 8 pin edits, not the harnesses (plan-140 § Outcome); v9's list of T741's mutations and of its final verification. Plan-140 records no test count for the merged commit. No mutation and no full suite ran for this register.
- **Unverified**, carried from v9: the source of the "do first" flags other than the fixed SEC-T716-01; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates; which three gaps "Fix now in this batch (Recommended)" covered (v6 § 8); live GitLab rendering (SEC-T716-03); the npm step in a tag pipeline; the lock on the musl image beyond the MR pipeline (section 6.2, item 8); whether the orchestrator's draft of the upstream report was ever shown to the user; adoption of Trivy 0.76.1; the questions shown to the user beyond ADR-012 and plan-133; each carried plan's actual deadline; whether the gate tolerates the leftover pointer sentence; whether targets receive the gate script and the template; GitLab's rendering of front matter and sanitized attributes (SEC-T739-02 and -04 are closed, and a refusal does not depend on it); which runner holds the Docker socket; `pip-audit`, which did not run for T739 either; the merged commit's two later changes in T739, which its reviewer did not see; the source of `markdown-it-py` 4.2.0, and of 3.0.0 beyond two files; GitLab's real rendering and bash's behaviour on the eight characters (a CR is now refused); the wording of SEC-T738-05 against the reviewer's report; the questions shown to the user for "N two go" and "parser go" beyond the plans; SEC-T730-06's code location; the deployed GitLab version; delivery of artifacts from a `pages` job to the gates, not observed; `parallel:matrix` on a tag, not run live, which the pin refuses anyway; the configured CI file path; that the crash of 2026-11-05 came from the "no seen-set" mutation, an inference (plan-138 § Outcome); the skip count on plan-138's trees (plan-138 § Outcome); SEC-T741-16's route itself, which the setting closes without its being tried; SEC-T741-17's state on a reused runner; what "review go" answered (v9 § 4.1).
- **Dropped from v9's list, each with what settled it**:
  - **The install of `ci/requirements-release.txt` in a tag pipeline**: proved by the probe's real job. The parser's version is tied by the hashes, not named in the log.
  - **The flags on `WIKI_TOKEN`**: protected (plan-140 § Outcome; plan-141 § Facts, API read).
  - **Tag protection and the minimum role for pipeline variables**: read through the API (A-17, A-18). The merge guard's limit stays a stated limit, not an unknown (A-18).
  - **4.2.0 for TD-T739-01**: measured (plan-140 § Facts; review T745 Metadata).
- **Unverified**, new, from review T745 § 5 and plan-141:
  - real rendering, the sanitizer and the Release description were not seen, and whether that description uses front matter stays open;
  - the reviewer read `test_ci_hash_pins.py` and `test_publish_release_job_token.py` only partly outside the diff, and `.gitlab-ci.yml` between lines 70 and 185 only partly;
  - `8ee1e2d3` was not reviewed;
  - no dependency changed and no audit ran for T745;
  - the value of `ANTHROPIC_API_KEY` was not read: "already revoked" is the user's statement;
  - the four limits of the probe, above.
- **Noted, with no id minted**: review T745 § 2 says `test_publish_release_job_token`'s PyYAML `skipTest` is now dead code, and without PyYAML the module errors, which fails closed.
- **Not re-run here**: the suite and the gates, which the orchestrator ran before the merge (review T745 Metadata; plan-140 § Outcome). The reviewers' own unverified lists stand as written in their artifacts.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`, each with a time limit where it runs tests.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v9.md`; `plan-140-batch-s-release-gate.md`; `plan-141-tracked-debt-register-v10.md`; `docs/tasks/task-T746.md`; `security-review-t745-batch-s-v1.md`; by grep or line range, the files named under Metadata, "Not opened". Decision IDs: ADR-011, ADR-012, as v9 cites them, not read here.
