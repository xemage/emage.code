# Artifact: tracked-debt-register-v11.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v10.md` (573 ids; v10 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-144-tracked-debt-register-v11.md` and `docs/tasks/task-T752.md` (the user's "\"v11 go"); `docs/plans/plan-142-verdict-check-tokens.md`; `docs/plans/plan-143-batch-s-rest.md`; `docs/artifacts/security-review-t748-batch-t-v1.md`; `docs/artifacts/security-review-t751-batch-s-rest-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01, superseded in part), ADR-012 (Accepted 2026-11-04), as v10 cites them, not re-read; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T752 (plan-144; the user's answer of 2026-11-06, verbatim: "\"v11 go"). **Date**: 2026-11-06.
- **Tree read**: branch `agent/tech-lead/T752` at `8d4f1ea0` (develop `9c7f2fad` plus the plan commit). Commits since v10's merge `06b903aa`: `bae5c4df` (T747, T748, squashed), `d989ecb7` (its merge), `999e0ef0` (T749 to T751, squashed), `9c7f2fad` (its merge), `8d4f1ea0`. `git diff --stat 06b903aa 8d4f1ea0` lists, outside `docs/artifacts/`, `docs/plans/` and `docs/tasks/`, only `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/check-version-consistency.py`, `scripts/run-allowlisted.py` (new), `scripts/verify-release-docs.py` and the test files `test_check_version_consistency.py`, `test_ci_hash_pins.py`, `test_publish_release.py`, `test_publish_release_job_token.py`, `test_run_allowlisted.py` (new) and `test_verify_release_docs.py`. So nothing under `implementation/`, `docs/decisions/` or `ci/`, and nothing in `scripts/install.sh`, `scripts/publish-release.py` or `scripts/check-release-tag-tree.py`, changed since v10's tree, and v10's lines in those paths stand. `docs/releases/_template.md` changed on line 3 only. The CWSO repository was not read: every CWSO status carries over from v10.
- **Review mode**: read-only. A closure cites plan-142, plan-143, or a review. "Unchanged" means no task, review or plan outcome since v10 names the id with a change of status, checked by searching the lines added in `06b903aa..8d4f1ea0` (section 1.2). Code was not re-checked unless a line or a run is cited. Anything not traced is **(unverified)**.
- **Reviewed trees**: review T748 read `d400b851`, then the diffs of its two fixes, up to `99bfa0bc`. Review T751 read `0e7a24ac`. `6c58244b` came after it, and the reviewer did not re-read it. In its diff against `0e7a24ac`, `scripts/verify-release-docs.py` and `.gitlab-ci.yml` change one message and one comment (read here), so plan-143's "not gate logic" holds for those two files. `git diff` of `.gitlab-ci.yml`, `scripts`, `tests/functional`, `CONTRIBUTING.md` and `docs/releases` between `6c58244b` and `999e0ef0` is empty, as is `scripts` and `tests/functional` between `99bfa0bc` and `bae5c4df`. None of those review-time commits is an ancestor of `develop`; the commits citable there are the four above.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository, registers v1 to v9. Read beyond the brief's list, by grep or line range: `scripts/verify-release-docs.py`, `scripts/check-version-consistency.py`, `scripts/run-allowlisted.py`, `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_verify_release_docs.py`, `tests/functional/test_run_allowlisted.py`, `tests/functional/test_merge_mcp_json_robustness.py`, `.gitlab-ci.yml`, `CONTRIBUTING.md`, `docs/releases/_template.md`, and `security-review-t730-t732-batch-g-v1.md` for the text of batch N. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5.
- **Batch letters**: I, J, K, L, M, N, P, Q, R, F and U keep their v10 scope. **T ends. S** keeps SEC-T741-17 only. **V and W are new** (section 5).

## 1. Summary

v11 holds **596 ids**: the 573 of v10 and **23 new**. After v11: **469 fixed**, **46 accepted**, **6 obsolete**, **1 open**, **74 tracked-LOW**. These are the plan's expected numbers, counted separately (section 8).

- **Open above LOW: none, with one qualification.** The one open id is K-20 (live checks, user). Reviews T748 and T751 each count 0 CRITICAL, 0 HIGH and 0 MEDIUM. **TD-T746-01 is filed as tracked-LOW without a reviewer's grade:** it is the orchestrator's id for a flaky test and carries no security claim. The five accepted MEDIUMs (section 6.1) are accepted, not open; under ADR-011 four of them need the user's new acceptance at the next release (section 6.2, item 2).
- **Batch T ends:** SEC-T739-07 is closed. **Batch S's 13 ids:** 12 closed, and SEC-T741-17 stays open in part, waiting on the user's runner.
- **Every id that left S and T was tracked-LOW in v10:** v10's own rows give SEC-T745-01 to -11 and SEC-T739-07 that status, and TD-T739-01 "tracked-LOW, open in part; now graded LOW". TD-T745-01 was already `fixed` in v10 and is not counted again.
- **SEC-T748-02 and -13 count as `fixed`, but not for the same reason** (section 3). -02's reported shapes are closed on a direct call as well, and what it leaves moved to -12. -13 is closed on the gate's route only: a direct call keeps the old behaviour, and nothing but the gate's route calls that function outside its tests. If the orchestrator wants a direct call to count, -13 returns to tracked-LOW and the totals become 468 and 75; no source asks for that.
- **Stale ids: none.** Plans 142 and 143 moved the lines of three batch N ids, and no finding lost its subject (section 5).
- **SEC-T751-06 reproduces.** The orchestrator's run did not show the hold. A whole gate run here, on a copy, does (section 5, batch V). It fails closed, and the grade stays.
- **Project state since v10.** A second gate probe ran the two gates' new lines in a real tag pipeline. The `release` job has still never run this code (section 8). Agents used the user's remote Docker host unasked, and later briefs forbid it (section 4.3).
- **Due before the next release**: as in v10, SEC-T735-08 and SEC-T735-09 (section 6.2, items 2 and 10). **No source binds batch V to a release; any of it before the next tag is open for the user.**
- **Open for the user now**: A-19, both probe tags, still on the remote when this register was written (section 7); a dedicated runner (A-20); the route of SEC-T735-06 and -07.

Arithmetic, from the v10 totals:

| Status | v10 | leaves | enters | v11 |
|---|---:|---|---|---:|
| fixed | 448 | | + 12 batch S + 1 batch T + 8 new | **469** |
| accepted | 46 | | | **46** |
| obsolete | 6 | | | **6** |
| open | 1 | | | **1** |
| tracked-LOW | 72 | - 13 fixed | + 15 new | **74** |
| **all** | **573** | | + 23 new ids | **596** |

Check: 469 + 46 + 6 + 1 + 74 = 596. Open or tracked: 74 + 1 = 75, the size of section 5.

### 1.1 Ids by v10 status and status now

| v10 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 72 | 13 | 0 | 0 | 0 | 59 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 448 | 448 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v10 ids** | **573** | **461** | **46** | **6** | **1** | **59** |
| new in v11 | 23 | 8 | 0 | 0 | 0 | 15 |
| **all v11 ids** | **596** | **469** | **46** | **6** | **1** | **74** |

### 1.2 New ids by source and grade

| Source | new | Fixed | LOW, tracked | Ungraded, tracked |
|---|---:|---:|---:|---:|
| `security-review-t748-batch-t-v1.md` § 3, § 9, § 10: SEC-T748 | 13 | 5 | 8 | 0 |
| `security-review-t751-batch-s-rest-v1.md` § Findings: SEC-T751 | 9 | 3 | 6 | 0 |
| `plan-144` § Facts: TD-T746-01, the orchestrator's id | 1 | 0 | 0 | 1 |
| **All new** | **23** | **8** | **14** | **1** |

A search of the lines added in `06b903aa..8d4f1ea0`, outside `tests/golden/`, for any `<PREFIX>-T<nnn>` id and any `<letter>-<n>` id finds no other new id. The carried ids it finds appear as "stays open", as a comment on code, or as plan-144's instruction, with no change of status: D-T710-2, SEC-T716-03, SEC-T731-02, SEC-T735-06, SEC-T739-02, -03, -04, -09, SEC-T741-12. `M-3` is an example heading, `UTF-8` is not an id, and A-19 is v10's. A-20 is a user-action number. This register mints no debt id.

### 1.3 How the reviews' counts map to ids

| Review | LOW | Resolved at the review | Later | Tracked now |
|---|---:|---|---|---|
| T748, final table | 13 | 4: -01, -02, -10, -11 | Plan-143 closes -13 on the gate's route, and narrows -04 and -12 | 8: -03, -04, -05, -06, -07, -08, -09, -12 |
| T751, Verdict | 9 | 0 | `6c58244b` fixes -02, -03, -04 (plan-143 § Outcome) | 6: -01, -05, -06, -07, -08, -09 |

**Review T748's "9 tracked" is one too many today.** Plan-143's list for this register has 8, and plan-142's has 9; review T751 § Q7 is the later source. SEC-T739-07 is not in T748's 13 (§ 10). Review T751's 12 closed ids and its open SEC-T741-17 are § Q1's.

## 2. v10 ids re-checked

Every v10 `open`, `tracked-LOW` and `accepted` id (119) has a row or a list entry here: 1 + 72 + 46. The v10 `fixed` and `obsolete` ids stay as v10 records them.

### 2.1 v10 `open` (1)

K-20: **Unchanged**, open, batch U (A-7).

### 2.2 v10 `tracked-LOW` (72)

**Changed (14: all of batches S and T).** Rulings: review T748 § 1 Q1 for SEC-T739-07, review T751 § Q1 for the rest. Code: `bae5c4df` and `999e0ef0`. The user: "T go" and "Sgo". Lines are current, read on `8d4f1ea0`, in `scripts/verify-release-docs.py` unless the path says otherwise; "pins" means `tests/functional/test_ci_hash_pins.py`.

| Id | v10 | now | Evidence | What stays |
|---|---|---|---|---|
| SEC-T739-07 | tracked-LOW | **fixed** | Sections come from the parser's tokens: `section_heading_indexes` `:379-385`, `section_text` `:446`, `verdict_placeholder_problems` `:484`, presence `:733` | Later reads: SEC-T748-03 to -09 and -12 |
| SEC-T745-01 | tracked-LOW | **fixed** | `MAX_DOCUMENT_CHARS` `:160`; `markdown_tokens` `:369`; refusal `:680-684`; `--help` `:264-268`; `timeout: 10 minutes`, `.gitlab-ci.yml:204` | Plan-142's note: the tag's own document is now always parsed. 48 s is one machine and 41 shapes, and `--help` says it is no bound. `check_links` is outside the cap: SEC-T751-06 |
| SEC-T745-02 | tracked-LOW | **fixed** | `opens_with_front_matter` `:641-647`; `FRONT_MATTER_BODY_RE` `:168` | Nothing (review) |
| SEC-T745-03 | tracked-LOW | **fixed, on the gate's route** | `live_html_line` `:650`; refusal `:703-709`; direct call `:875-877`. Markdown API: `<style>` is removed and its text displayed | Comments stay allowed. A document on a non-Cursor line is not read (`--help` `:275-277`). Table differential: SEC-T751-08 |
| SEC-T745-04 | tracked-LOW | **fixed, as asked** | `.gitlab-ci.yml:232-238`, pinned. Second probe: all ran through the script | Credential file: SEC-T751-01 |
| SEC-T745-05 | tracked-LOW | **fixed** | Allowlist and removal, `.gitlab-ci.yml:212-216`, pinned. Second probe: both ran | The job's shell keeps its variables. Nothing shows the removal hit the right path: SEC-T751-05 |
| SEC-T745-06 | tracked-LOW | **fixed, as asked** | The clause in contract 6, pins `:32-35` | Project level only: SEC-T751-05. It holds while the project has no such variable, and no test reads that |
| SEC-T745-07 | tracked-LOW | **fixed** | `GIT_STRATEGY: clone`, `.gitlab-ci.yml:249`, pinned | Unproved: the `release` job was skipped in both probes |
| SEC-T745-08 | tracked-LOW | **fixed, as asked** | `_read_route_problems`, `tests/functional/test_verify_release_docs.py:160`; `test_the_parser_has_one_call_site`, `:1972` | String routes such as `importlib` are not seen; crafted only. `codecs.decode` is **(unverified)** by the reviewer |
| SEC-T745-09 | tracked-LOW | **fixed** | `DEPENDENCY_TREES`, `scripts/check-version-consistency.py:80`; `:206` | Another virtual environment's name fails a local run. A committed file under the exact paths silences only itself |
| SEC-T745-10 | tracked-LOW | **fixed** | `ascii()`, `scripts/check-version-consistency.py:255` | Nothing; output now reads `'README.md':3:` |
| SEC-T745-11 | tracked-LOW | **fixed** | `document_refusal` docstring `:674-678` | Nothing |
| TD-T739-01 (rest) | tracked-LOW, graded LOW | **fixed** | As SEC-T745-01 | As SEC-T745-01 |
| SEC-T741-17 | tracked-LOW, open in part | **tracked-LOW, open in part: unchanged** | `.gitlab-ci.yml:223` says so | The dedicated runner tag needs a runner, which is the user's to provide (A-20). The Docker socket route stays **(unverified, runner-dependent)** |

v10's evidence for SEC-T739-03, SEC-T739-06 and TD-T745-01 describes code that plan-143 replaced: "the first HTML ends the search", the `unset` line, and the name left in two lines. Each stays `fixed`, and the replacement is stronger (review T751, Regressions).

**Unchanged (58 tracked-LOW; v10 and earlier stay the record of their text)**

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
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 5 |

Total 58; with the 14 above, 72.

### 2.3 v10 `accepted` (46)

**All unchanged**; basis as in v5 § 2.3, v6 § 6.1 and v7 § 2.3. None has a new acceptance.

- **MEDIUM (5)**: SEC-T657-01 / SEC-T658-01 (one id), SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07.
- **LOW or INFO (41)**: K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, K-15, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07.

## 3. New ids

Sources: review T748 § 3, § 9, § 10 and review T751 § Findings, where each id's fix is. Owner per their headings: devops-engineer, "proposed"; "next sprint". Every SEC id is `SECURITY:LOW`. Lines are current, read on `8d4f1ea0`, in `scripts/verify-release-docs.py` unless the path says otherwise; the reviews' own lines were at `d400b851` and `0e7a24ac`. "Run here" means section 8's read-only run, on the local parser 3.0.0, where "refused" is `document_refusal` and "direct" is `verdict_placeholder_problems` alone.

"On the gate's route" is exact: `run_checks` calls `check_release_brief` (`:1000`), which refuses first (`:716-719`) and only then reads presence (`:733`) and fields (`:736`). A search of `scripts/` and `.gitlab-ci.yml` finds no other caller of the gate's functions; the CI job runs the script (`.gitlab-ci.yml:216`).

| Id | Location now | Short description | Status | What it still leaves | Batch |
|---|---|---|---|---|---|
| SEC-T748-01 | `section_is_empty`, `:464` | A section holding only `## &#32;` or `## <!-- x -->` passed as filled. A regression | **fixed** (review § 9, § 10). Run here: `## &#32;` gives 1 direct problem | The older shapes, `<!-- x -->`, a `&#8203;` paragraph and `### &#32;`, which pass on both old and new (run here: 0). They are tracked under SEC-T748-06 (§ 10; review T751 Q2, shapes 1, 2) | - |
| SEC-T748-02 | `heading_has_text` `:393-398`; `heading_is_visible` `:401-406` | A heading whose text is invisible ended the section | **fixed** (review T748 § 9; review T751 § Q7). **Not only on the gate's route:** run here, both `&#8203;\n---` and `## <span hidden>x</span>` followed by a pending field give 1 direct problem, and only the second is refused | Characters outside `Cf`: SEC-T748-12. The guard stays for a direct call | - |
| SEC-T748-03 | `section_line_span` `:409`; `--help` `:290-292` | Ruling 1. `Text\n---` under the verdict moves a pending field out of the section. Not necessarily crafted. Same for H1, ` ## ` and `##\t` | tracked-LOW. Run here: 0 direct, not refused | All of it | V |
| SEC-T748-04 | `html_block_holds_line` `:422`; refusal `:703-709` | Ruling 3 did not extend to non-comment HTML above a filled section | **tracked-LOW, narrowed** (plan-143; review T751 § Q7). `<div>` and `<div hidden>` wrappers are refused on the gate's route. Run here: both refused | A `~~~` fence above the section (displayed as code) and comments under ruling 3: run here, 0 direct, not refused. A multi-line reference title (hidden), per the reviewers' hand traces: **my one literal shape did not reproduce it** on 3.0.0 (the `##` line ended the title and became a real heading: 2 problems), and 4.2.0 was not run, so **(unverified)**. On a direct call, `<div hidden>` above a real heading still gives 0 | V |
| SEC-T748-05 | `section_heading_indexes` `:379-385` | Exact matching leaves near-duplicates: `## Release Verdict`, `## RELEASE&nbsp;VERDICT`, a misspelt optional heading (ruling 5). Same on old | tracked-LOW. Run here: 0 direct, not refused | All of it, and SEC-T748-13's pairing with it | V |
| SEC-T748-06 | `FIELD_RE` `:150`; `_line_problems` `:511` | Field logic: a visible unfilled value passes, as `- Status:\n  - pending` and `- Status: _pending_`. Same on old. Needs its own plan; check the golden contract first | tracked-LOW. Run here: 0 direct, not refused | All of it, plus SEC-T748-01's older shapes | V |
| SEC-T748-07 | `is_closed_backtick_fence` `:431` | Closure rests on the parser's numbers, and "Pinned on 3.0.0 and 4.2.0" overstates: CI runs only the locked version | tracked-LOW | All of it | V |
| SEC-T748-08 | `--help` `:297-304`; module docstring | Overclaims in the help, among them "a hidden 'pending' still fails" (`:299-300`), which holds only inside a section | tracked-LOW; review T751 Q8 item 6 says still open | All of it | V |
| SEC-T748-09 | `check_release_brief` `:722-727` | `## Install` and `## Highlights` are substring checks, so a comment satisfies them. Older than T747 | tracked-LOW | All of it | V |
| SEC-T748-10 | `section_text` `:446` | **A regression from the orchestrator's first fix:** blanking a non-ending heading hid markers that the old code read | **fixed** (`99bfa0bc`, in `bae5c4df`; review § 10) | Nothing named | - |
| SEC-T748-11 | `section_is_empty` `:464` | **A regression from the same fix:** a visible heading holding live HTML did not end the section, so an empty verdict passed | **fixed** (same; review § 10) | Nothing named | - |
| SEC-T748-12 | `heading_has_text` `:393-398` | Characters outside `Cf` that render as nothing still count as text: U+2800, U+3164, U+FFA0, U+115F, U+1160, U+034F, variation selectors. Old caught them | **tracked-LOW, narrowed** (plan-143; review T751 § Q7). The wrapper part is refused on the gate's route (run here: refused) | **Those characters, on the gate's route** (run here: `&#x2800;\n---` then a pending field: not refused, 0 direct). **Markdown API: renders as an `h2` with no visible text.** On a direct call the wrapper gives 0 too | V |
| SEC-T748-13 | `section_heading_indexes` `:379-385`; presence `:733` | `## <span hidden>RELEASE VERDICT</span>` counted as the real heading | **fixed, on the gate's route** (plan-143 § Outcome; review T751 § Q7). Run here: refused | **A direct call keeps it:** run here, `section_heading_indexes` still counts it, and `verdict_placeholder_problems` gives 0. No caller outside the gate's route and the tests. A new caller that skips `document_refusal` would get the old behaviour. The pairing with -05 stays under -05. Markdown API: `hidden` is stripped | - |
| SEC-T751-01 | `.gitlab-ci.yml:228-238` | The drift gate's credential file stays readable by `apk`, `git` and both scripts | tracked-LOW | All of it; the reviewer's one-line fix was not run | V |
| SEC-T751-02 | `tests/functional/test_run_allowlisted.py:107`; contract 6, pins `:29-31` | Every gate command runs through a file whose tests never used CI's variables | **fixed** (`6c58244b`, in `999e0ef0`; the reviewer did not re-read it). The orchestrator's mutation survived before and is caught after, with two variants (review, Orchestrator's record) | A careful edit: the test "only catches a careless one", and no pin reads the file (section 6.2, item 26) | - |
| SEC-T751-03 | `:706-708`; `docs/releases/_template.md:3`; `CONTRIBUTING.md:223-225` | An overclaim on placeholders, and a message that steered an unfilled one into a code span | **fixed** (as above; wording) | **`--help` `:244-245` still says of prose such as `<your-project>`: "put it in a code span".** The review did not list that line, and it is literal prose there, so I keep `fixed` and note it (my reading) | - |
| SEC-T751-04 | `.gitlab-ci.yml:210-211` | The stated reason for the removal's safety was wrong | **fixed** (as above; wording, read here) | Nothing named | - |
| SEC-T751-05 | Contract 6, pins `:32-35`; `.gitlab-ci.yml:206, 226, 249`; `CONTRIBUTING.md:288-292` | Group and instance variables also outrank job variables **(from memory of the docs)**, `CI_PROJECT_DIR` set at project level would miss the directory, and nothing shows the credential is gone | tracked-LOW | All of it. Second probe: the log shows the removal ran, not that it was the right path | V |
| SEC-T751-06 | `LINK_RE` `:308`; `check_links` `:531-542`; the loop `:1002-1003` | `LINK_RE` is quadratic on `[`, is outside the cap, and runs even on a refused document. Fails closed | tracked-LOW. The orchestrator's run did not reproduce it; a run here does (section 5) | All of it | V |
| SEC-T751-07 | `.gitlab-ci.yml:214, 216, 236, 238`; `:563` | The children run without `-I`, so a committed `scripts/markdown_it/` or root `pip/` shadows the real module with all tests green | tracked-LOW | All of it | V |
| SEC-T751-08 | `:371`; `holds_live_html` `:852-862` | The commonmark preset has no tables, so pipes in a code span can yield a live tag in a GFM table. Register with SEC-T716-03 | tracked-LOW. **Markdown API: GFM splits first, as suspected, and `hidden` is stripped,** so `<div></div>` is live and holds nothing hidden | The differential; a Release description **(unverified)** | V |
| SEC-T751-09 | `PLACEHOLDER_MARKERS` `:141-147`; `docs/releases/_template.md:7, 47, 51, 88, 94` | Template placeholders that are not HTML and hold no marker pass, one inside a verdict section | tracked-LOW. `<tech-lead` is not in the markers (run here) | All of it | V |
| TD-T746-01 | `test_temp_file_has_the_old_mode_before_any_content_is_written_and_a_random_name`, `tests/functional/test_merge_mcp_json_robustness.py:169` | Asserts that the process id is not in the temp file's name. In CI the id was `49` and the name `.dest.json._4498eko.tmp` held it, so `unit-tests` failed once on MR !649 (job 17812330179); a retry on the same commit passed. Measured: about 0.5% per run with a two-digit process id, over 20,000 `mkstemp` names. The MR changed only files under `docs/` (plan-144 § Facts; the job not re-read here) | tracked-LOW, **no reviewer's grade**: the orchestrator's id. Not a security finding | All of it | W |

## 4. Decisions since v10

### 4.1 The user's (words verbatim as recorded)

Each row claims only what these plans record. The questions as shown to the user were not verified beyond those records **(unverified)**.

| Date | Words | What the plan records | Source |
|---|---|---|---|
| 2026-11-06 | "T go" | Plan-142, T747 and T748, on batch T. It covers the wider use of the parser (plan-142 § Constraints) | plan-142 Based on |
| 2026-11-06 | "Sgo" | Plan-143, T749 to T751, on the rest of batch S | plan-143 Based on |
| 2026-11-06 | "probe go" | The second gate probe | plan-144 § Facts |
| 2026-11-06 | "\"v11 go" | Plan-144, T752, this register. The stray quote is the user's | plan-144 Based on; `docs/tasks/task-T752.md` |

### 4.2 The orchestrator's rulings (not the user's)

| Item | Decision | Source | Effect |
|---|---|---|---|
| Only closed ``` fences are skipped | Skipping every fence let a `~~~` fence, an unclosed fence and indented code pass. The implementer's closure test uses the parser's `map` and `content` | plan-142 § Outcome | SEC-T748-07 |
| Ruling 1 | A real heading with text ends the section. The reviewer accepts it for visible text | review T748 § Q3 | SEC-T748-03 |
| Ruling 2 | A field really inside a closed fence does not count. The reviewer agrees, no finding | same | none |
| Ruling 3 | A comment holding the heading and a pending field above a filled section passes. The reviewer agrees for comments only | same | SEC-T748-04 |
| Ruling 4 | `lru_cache(maxsize=None)` on `markdown_tokens`, in place of the plan's cache of one. The reviewer agrees, no finding | same | none |
| Ruling 5 | A misspelt optional heading stays. The reviewer accepts it as tracked debt, "not as correct" | same | SEC-T748-05 |
| Stopping T748's fix rounds | Under the user's LOW policy, told to the reviewer before the last read. The reviewer states that it changed no grade | plan-142 § Outcome | section 3 |
| Refusing HTML anywhere | In place of the reviewer's narrower options, because no real document needs HTML | plan-143 § Design | SEC-T745-03; SEC-T748-02, -04, -12, -13 |
| The exact skip paths | `ci/js/node_modules/`, `.venv/` and `venv/`, replacing the plan's `pyvenv.cfg` rule | plan-143 § Outcome | SEC-T745-09 |
| Refusing the nesting limit | Added on T749's finding: past the limit the rest of a list's document is not read, so "no HTML anywhere" did not hold | plan-143 § Outcome | section 6.2, item 25 |
| The temp directory in the removal | `${CI_PROJECT_DIR}.tmp` goes too | plan-143 § Outcome | SEC-T745-05; SEC-T751-05 |
| Stopping fix rounds on LOW | No fix round after T751 for a LOW that plan-143 did not introduce; `6c58244b` fixes the three it did | plan-143 § Constraints, § Outcome | section 3 |
| Batches V and W, and S's one id | plan-144 | plan-144 § Task Decomposition | section 5 |

### 4.3 The orchestrator's errors on the record

These stay as the plans state them.

- **Plan-142's design was wrong in one place.** Skipping every `fence` and `code_block` token broke the plan's own sentence, "Nothing the old check caught may start to pass". The orchestrator found it on `9b79c192`.
- **The orchestrator's first fix was wrong.** `3cb4f739` blanked heading lines on reasoning that holds only for `## ` at column 0. Its tests put no marker on such a line, so its 8 mutations could not show it. The reviewer found it, and it became SEC-T748-10 and -11. The orchestrator wrote the code of both fixes, so the reviewer's two reads are their only independent check (review T748 § 8).
- **Plan-142's list of what may stop counting was incomplete.** Its two grew to the list in § Outcome.
- **Plan-143's design was wrong in two places, and the implementers caught both.** `rm -rf .git` did not remove the clone credential on runner 19.5.2 (T750, source reading). The `pyvenv.cfg` skip let a committed file silence the version check for `docs/wiki` (T749).
- **An invalid run.** The first run of the 8 mutations had a failing baseline on a thin copy, so its "caught" meant nothing. It was redone (plan-142 § Outcome).
- **An unconfirmed run.** The orchestrator's attempt at shape (c) did not reproduce it, reporting 1 problem (plan-142). I read plan-144's "two invalid or unconfirmed runs" as these two (my reading).
- **SEC-T751-06's run did not show the hold.** The orchestrator said it had not traced why and kept the id tracked (review T751, Orchestrator's record). That was the right call, and section 5 has what I found.
- **Agents used the remote Docker host, unasked.** T750, as T728 did, ran containers through `docker`. `DOCKER_HOST` points at a remote host that also runs the user's `portainer` and `hindsight`. After T750 and after plan-143's merge only those two containers exist there. The orchestrator's brief did not forbid it, and it told the user (plan-143 § Outcome; plan-144 § Facts). Not re-checked here. See section 6.2, item 29.
- **Over budget.** T747 about 173k, T748 about 196k, T749 about 205k, T750 about 178k, T751 about 232k, against 120k (T749's 120k + 40k), by the harness's count, which includes context.

### 4.4 What GitLab's Markdown API observed

`POST /api/v4/markdown` with `gfm: true`, 2026-11-06, by the orchestrator (review T751, Orchestrator's record; not re-run here). **This is the Markdown API. A Release description stays (unverified).**

| Shape | Rendered | Touches |
|---|---|---|
| `<div hidden>x</div>` | `hidden` stripped | SEC-T748-04 |
| `## <span hidden>x</span>` | `hidden` stripped, in the heading | SEC-T748-02, SEC-T748-13 |
| `<style>h3{display:none}</style>` above `### h` | The tag is removed, its text displayed, the heading stays | SEC-T745-03 |
| A table row with `<div hidden>` or `<style>` in pipes inside code | GFM splits first, as suspected; `hidden` stripped; no `<style>` tag | SEC-T751-08 |
| `&#x2800;\n---` | An `h2` holding U+2800: a heading with no visible text | SEC-T748-12 |

So on this API the sanitizer strips what the hidden-HTML findings were about, and SEC-T748-12's character does render blank. The gate's refusals do not depend on it.

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. I, J, K, L, M, N, P, Q, R, F and U are carried from v10 without change; in those rows "review" and "review § 4" mean the batch H review, except where a row names another.

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
| **S** | Release gate: the runner tag | SEC-T741-17 (the rest) | 1 | the user provides the runner (A-20); devops-engineer sets the tag | waits on the user's runner |
| **V** | Release gate after plans 142 and 143 | SEC-T748-03, -04, -05, -06, -07, -08, -09, -12, SEC-T751-01, -05, -06, -07, -08, -09 | 14 | devops-engineer (both reviews' headings, "proposed") | **open, for the user:** the reviews say "next sprint", no sprint is scheduled, and no source binds V to a release |
| **W** | A flaky test | TD-T746-01 | 1 | none set. Suggested: devops-engineer or qa-engineer, routed by the orchestrator | none set |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 10 + 1 + 7 + 5 + 12 + 8 + 1 + 3 + 4 + 1 + 14 + 1 + 2 + 6 = 75 = 74 tracked-LOW + 1 open. No open item is above LOW; TD-T746-01 has no reviewer's grade (section 1).

**Batch T ends.** SEC-T739-07 is its one id, and it is closed.

**Batch N, re-read on `8d4f1ea0`.** Plans 142 and 143 moved the gate script's regexes by fifteen lines, and **no id is stale**: the diff does not touch `POINTER_LIKE_RE` or `UNSAFE_RE`, and the new caps reach release documents only, not the `install.sh` lines these regexes read. I did not re-rule any, and I re-ran none.

| Id | v10's line | Now | Reading |
|---|---|---|---|
| SEC-T730-03 | `publish-release.py:629, 750` | same | File unchanged |
| SEC-T730-04 | `ci/requirements-ci.in`, `ci/requirements-ci.txt:2-4` | same | `test_ci_hash_pins.py` still has no `generated-on` or cooldown check, by grep |
| SEC-T730-06 | not located | not located | File unchanged. **(unverified)**, as in v10 |
| SEC-T731-03 | `verify-release-docs.py:175, 179` | `:190, 194` | Moved. `test_a_long_tag_line_does_not_slow_the_gate`, now `test_verify_release_docs.py:1135`, times the parser, and that file still does not name `POINTER_LIKE_RE`, so the reviewer's timing test is still to write |
| SEC-T731-04 | `verify-release-docs.py:174-181` | `:189-196` | Same regex, moved |
| SEC-T731-05 | `verify-release-docs.py:200`, `check-release-tag-tree.py:48` | `:215`; `:48` | `UNSAFE_RE`, moved. The equality test is at `test_verify_release_docs.py:2409` |
| SEC-T732-01 | `.gitlab-ci.yml:93-104` | same | Read here |
| SEC-T732-02 | `ci/js/README.md:39-43` | same | Directory unchanged |

**Batch V, in short.** No source binds it to a release, and the reviews' order is by number. **The order below is my suggestion; no source sets it.**

- **SEC-T751-06 first (suggestion).** What the orchestrator's run says: `"[" * 131072`, `"[a](" * 32768` and 1 MiB of `[` each exited 1 in about 0.1 s, so the hold "did not reproduce on these shapes"; it did not trace why and kept the id tracked; T749's own `[` shapes took 2.63 s. **What I ran:** the whole gate, on a throwaway `git archive` copy without `tests/`, with a generated `docs/releases/v99.0.x.md`, under a time limit and a memory cap. `"[" * 131072` exited 1 in 8 s. **`"[" * 1048576` was still running at the 75 s limit.** `LINK_RE` alone took 0.01 s, 0.04 s and 0.17 s on 5,000, 10,000 and 20,000, four times per doubling, which is the reviewer's quadratic; carried to 1 MiB it is about 8 minutes (my extrapolation, not a measurement). So the reviewer's finding stands: a large document can hold the job up to its 10-minute timeout, and it fails closed. A likely reason for 0.1 s: `run_checks` returns before `check_links` on a missing file or a pointer error (`:994-995`), and my own first attempt, on a thinner copy, ended that way in under a second. Whether that is what happened to the orchestrator's run is **(unverified)**. The review's first fix is small: no `check_links` on a refused document.
- **SEC-T748-12 and SEC-T751-01 next (suggestion).** -12 is the one id here that the old check caught, that a real document's reader would see as a blank heading on the Markdown API, and that the gate does not refuse. -01 is one pinned line, and its proof needs a tag pipeline.
- **SEC-T748-03, -04 and -05 together (suggestion).** Each is about what counts as the section's heading. Re-run every document first, as the reviewer says.
- **SEC-T748-06 on its own (suggestion).** The review says it needs its own plan and a look at the golden contract.
- **SEC-T751-05, -07, -08 and -09 (suggestion).** The pins, the `-I` change (check first that no script imports a sibling), the table rule, the marker list.
- **SEC-T748-07, -08 and -09 last (suggestion).** Wording and two substring checks.

**Batch R, in short.** Carried from v10. **The route of SEC-T735-06 and -07 is still to be settled before batch R.**

- **SEC-T735-07: confirm the route first.** The reviewer's fix, "An acceptance covers", changes ADR-011's A1 text, and accepted ADRs are immutable (ADR-012 Status). The route is not settled; the review says only to confirm it.
- **SEC-T735-06** has the same question (tech-lead's reading in v8, no source says so): its fix, that `mitigation` cites where the plan was shown, changes the Conditions line, which is ADR-012's row B3. The top-level session's comparison would be a new duty too.
- **SEC-T736-01 (the rest)** needs pins and mutations only, in the style of T736, and no knowledge text.
- **SEC-T693-07 has no text fix**: "the independent check is a duty in the role text, not an enforced control" (plan-133), and the residual is accepted by ruling with no edit. Batch R must not edit for it. It closes only if an enforced control is built, and nothing here proposes one.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 § 6.1 and v6 § 6.1 stand unchanged and stay the record, with v7, v8, v9 and v10 § 6.1. Plans 142 and 143 add and renew no acceptance: reviews T748 and T751 found no MEDIUM. ADR-012 replaces rows A1, A8 and A12 of ADR-011 in part; the rest of ADR-011 stands: only the user accepts, one release only.

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 pin audit **2027-01-30 or the first Brave release above 2.1.4**; SEC-T702-09, SEC-T660-01, SEC-T665-01 and the SEC-T657-01/SEC-T658-01 remainder: **the next release needs the user's new acceptance** (ADR-011, ADR-012).

### 6.2 Next release checklist

Carried from v10 § 6.2, with its numbers. Items 6, 7, 8, 14, 20, 21 and 22 are rewritten where plans 142 to 144 changed them, and items 25 to 30 are new. Every line that points into `scripts/verify-release-docs.py`, `.gitlab-ci.yml` or `tests/functional/test_ci_hash_pins.py` was read again on `8d4f1ea0` (items 7, 14, 15, 16, 17, 18, 19, 20, 22, 23). Items 1 to 5 and 9 to 13 are otherwise v10's text: their paths did not change. In those items "review" means the batch H review.

1. **Migration item T725 (TD-T671-P5)** in the release document: authoring-only commands are no longer installed into target projects; commands declare `audience: authoring | target | both`; today only `/prepare-release` (five platform paths listed in plan-128 § Outcome); `--update`/`--projections-only` deletes an existing copy (a dry run prints the `rm`); an authoring checkout (`implementation/registry/index.json`) keeps them; a target that used `/prepare-release` keeps its own copy under another file name; `.generated-manifest.json` gains `authoringOnly`; the generator refuses a command without a valid `audience:`.
2. **ADR-011 re-acceptances**: the Release Gate input lists every MEDIUM an earlier release shipped under the user's acceptance and not yet fixed (SEC-T720-01 fix, `validation-gates/SKILL.md`): **SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09**. Each one is fixed, or the user accepts it again for this release, verbatim and dated, with its remediation plan (owner, fix, deadline). No agent grants or carries one over.
   - **When asking the user to re-accept any of these four (SEC-T735-08; ADR-012): name the release, record the plan as shown, and show a deadline still ahead.** The rule text does not say whether a new acceptance cures a deadline that has already passed, so do not put that case to the user as if it were settled.
   - Each carried plan's actual deadline was not verified by the reviewer (review § 5) or here **(unverified)**: read it before asking.
3. **New verdict fields** (R4, R10): `Issued at commit` and `Independent check` (`docs/releases/_template.md:87-88`; `commands/prepare-release.md:59-60`). The independent check row must be present, current and not FAIL (SEC-T693-02).
4. **TD-T723-01 (batch Q)**: the release document cites current `install.sh` lines. `docs/releases/v9.0.0.md:86` cites `install.sh:1300`, and `:75` cites `install.sh:1285-1302`, which v5 did not mention. On `a4c3c7b3` the advice is `scripts/install.sh:1297-1300` and the pointer is `:1301`; re-read them when the document is written.
5. **Brave**: if the release falls after 2027-01-30 or after a Brave release above 2.1.4, the pin audit needs a new acceptance version or the bump first.
6. **D-T710-2**: confirm in the release job that the `CHANGELOG.md` entry lands below `[Unreleased]` (fixed in code by T716; not yet observed in a tag pipeline; both gate probes skipped the `release` job).
7. **Visible changes of batch G** (plan-131 § Outcome), **batch S** (plan-140, plan-143 § Outcome) **and batch T** (plan-142 § Outcome), for the release document and its author:
   - `CHANGELOG.md` entries now show `\#42`, `\@user` and URLs in backticks in their source, and `(#42)` no longer links to the issue.
   - **The blank-line rule is gone, and `## Migration Guide <!-- x -->` now counts** (plan-136 § Outcome). The gate reads the document with `markdown-it-py`'s CommonMark parser (`verify-release-docs.py:227-248` is the `--help` text, `:786-892` the code). The section is the first top-level level 2 heading whose text is exactly `Migration Guide`, in ATX or setext form, up to the next top-level level 1 or 2 heading in either form; a heading inside a blockquote or a list neither opens nor ends it. The Cursor item is, in that section, with the case-sensitive word `Cursor` in its text, either a top-level heading of level 3 to 6, or a paragraph, top-level or with only list containers around it, that opens with a `**` strong span, and only the text inside that span counts. Text means text and inline code, with a line break read as a space; an image's alt text never counts, and an anchor holding HTML other than a comment does not count at all (item 22). `__bold__`, an anchor in a blockquote and a heading in a list do not count.
   - **What still follows from that rule:** a bold lead must open its own paragraph. `Some text` followed on the next line by `**Cursor**` is one paragraph, so it does not count, and a blank line is still what a release author needs there. A heading does not need one. Run in v8 on the local `markdown-it-py` 3.0.0; the orchestrator ran the same shapes on the locked 4.2.0 with the same results (plan-137 § Outcome). The error at `:915-919` now says "a paragraph that opens with a '**' span holding the word, optionally in a list" (SEC-T739-08).
   - **Checked files may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`.** They are the tag's release document, the three marker files and now `scripts/install.sh` (SEC-T731-07) (`verify-release-docs.py:207`; `check_line_breaks`, `:612`, called at `:998`). The error names the file, the line and the code point.
   - **Refusals (batch S).** A release document the gate reads is refused, naming its path, in this order: over 131072 characters; a line over 65536; a front matter opening, `---`, `+++` or `;;;`, optionally after a BOM, white space or a `coding:` line; the parser's nesting limit; HTML other than comments, anywhere (`--help` `:255-263`; `document_refusal`, `:671-710`; items 22, 25). `scripts/install.sh` may hold no CR, CRLF included (SEC-T738-02; `--help` `:269-271`). CRLF in a release document stays allowed.
   - **The verdict check reads the parser's tokens (batch T; `--help` `:289-304`).** `RELEASE VERDICT` must be a real top-level heading. A section ends at the next top-level level 1 or 2 heading with text, in either form, so `Text` above `---` ends it (SEC-T748-03). Only closed ``` fences are skipped. A second real heading of the name is an error (item 30).
8. **Not verified live in plan-131; watch these in the release**:
   - how GitLab renders the escaped references and code spans;
   - the npm step (`npm ci --ignore-scripts --prefix ci/js`) in a tag pipeline;
   - the lock on the musl image beyond the MR pipeline. The two gate probes' installs cover `ci/requirements-release.txt` on the `python:3.12-alpine` image only; I read this item as being about the CI lock, and no source says which (my reading).
9. **The Conditions block** (`agents/release-manager.md:183`, ADR-012 B3): an accepted `SECURITY:MEDIUM` fills `risk_accepted_by=` with the user's words verbatim and the date, `grade=`, `release=` (the version the user was asked about), and `mitigation=` with the plan as shown to the user, its owner and fix, and the current owner if it has changed; `deadline=` holds the plan's deadline.
10. **The template's pointer sentence** (`docs/releases/_template.md:90`; SEC-T735-09): remove it before the independent check, or leave it. Deleting it after the check makes the check stale. That the gate tolerates the leftover sentence is T736's report; the reviewer did not verify it (review § 5).
11. **The independent checker** (`agents/release-manager.md:46`): "The checker has not authored or edited the release files for this release; if the checker has, the row counts as missing." The orchestrator or the top-level session will often be ineligible, so `@tech-lead` is the practical default (review § 1; plan-133 § Outcome). If the checker edited the files, another eligible checker re-runs it.
12. **Batch H changes a release author sees**:
    - after the check, only the closed list in `agents/release-manager.md:46` may change ("No other text may be added after the check"); it includes "Changelog Preview (a summary of the checked changelog, nothing new)";
    - hotfix eligibility (`skills/release-workflow/SKILL.md:171`): the issue is present in the released version, and is graded critical or high on its own scale, or, whatever its grade, is a breach of an Immutable Security Constraint or a required control omitted, removed, disabled or weakened, which `@security-engineer` confirms. A fix with design impact does not take the fast track (`:202`).
13. **Not verified in batch H**: whether targets receive `scripts/verify-release-docs.py` and `docs/releases/_template.md` (review § 1). The migration note must not assume that they do. A grep of `scripts/install.sh` finds no `rsync` or `cp` line naming `scripts` or `docs`, and its one mention of the gate script is a comment (`:1296`). That is a grep and not an install, so the question stays **(unverified)**.
14. **Keep watching `release-docs-gate` at the next tag** (`.gitlab-ci.yml:196-218`; the job's rule is the tag rule). No merge request pipeline runs its install. The second gate probe ran the docs gate's new lines in a real job (pipeline 3038460622, job 17821516208; plan-144 § Facts): the removal, pip and the gate through `scripts/run-allowlisted.py`, and the runner's cleanup showed no error. Its document was a copy of v9.0.0's. **What remains:** the `timeout`, which was not reached; that the removal hit the right path (SEC-T751-05); and the `release` job and its clone setting, skipped: `scripts/publish-release.py` has changed since v9.0.0, so the `CHANGELOG.md` entry below `[Unreleased]` (item 6) and the escaped references (item 8) are still unobserved. Each publishing step needs the user's approval. The watch list is item 28, and the probe's other limits are in section 8.
15. **The job must stay without `allow_failure`** (review T739 § 1; plan-138 § Outcome). `allow_failure` on any tag job now fails a test (`pinned_job_problems`, `tests/functional/test_ci_hash_pins.py:335-356`; SEC-T739-05, SEC-T741-02). The job must still stay without it: a PyPI outage fails the job closed, that outage is when someone will be tempted to add it, and `needs` in `release` does not stop a release after an allowed failure.
16. **A local gate run needs the parser.** Without it, every gate run exits 1 and prints the install command, which is the one to use, in a virtual environment (`verify-release-docs.py:174-180`; `CONTRIBUTING.md:164-167`): `python3 -m pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt`. A developer's system package may be another version; the job's locked run decides (plan-136 § Design).
17. **A regeneration of `ci/requirements-ci.txt` needs `ci/requirements-release.txt` too**: `test_the_release_lock_matches_the_ci_lock` (`tests/functional/test_ci_hash_pins.py:661`) enforces the versions and hashes (plan-136 § Outcome).
18. **A new job in `.gitlab-ci.yml` needs an `if` from `NOT_TAG_CONDITIONS`** (`tests/functional/test_ci_hash_pins.py:125-130`; `tag_runnable_job_problems`, `:381-399`; plan-138 § Outcome). Adding a condition is a visible test edit and means checking that it is false on a tag: `$CI_PIPELINE_SOURCE == "schedule"` alone would not be, because a schedule can run on a tag ref (review T741 § 1, the reviewer's memory).
19. **A digest bump across all jobs passes; an `apk` pin or a Python minor bump needs a test constant edit** (plan-138 § Outcome; review T741 § 1: "with a clear message"). The constants I read are `PINNED_IMAGE` (`tests/functional/test_ci_hash_pins.py:93`) and the drift gate's `before_script` (`DRIFT_GATE_APK`, `:82`). **The CI header's bump recipe does not say so yet** (`.gitlab-ci.yml:23-26`). This is a fact for whoever bumps an image; fixing the header is not scheduled.
20. **A checked file must be valid UTF-8, and the gate names the path and offset** (SEC-T739-01; `verify-release-docs.py:311-331`), never the content. The rule covers what the gate reads in this process (`:33-37, 283-288`). **The child `scripts/check-version-consistency.py` now reads strictly too** (SEC-T741-06; `scripts/check-version-consistency.py:125-131`), so a committed non-UTF-8 `.md` outside its exclusions now blocks the release (review § 2); the exclusions now include the exact paths of `DEPENDENCY_TREES` (`:80`; SEC-T745-09). A pointed document on an `install.sh` line without "Cursor" is checked for existence only (SEC-T741-07; `--help` `:275-277`). Plan-140 records the real tree's `--tag v9.0.0` run as its acceptance; it was not re-run here.
21. **Retired, and what replaces it.** The `unset` line, `GATE_CREDENTIALS` and the name `ANTHROPIC_API_KEY` are gone (plan-143 § Outcome; a test holds that, `tests/functional/test_ci_hash_pins.py:1094-1095`). **A new CI/CD variable now stays out of every gate command, unless a command needs it, in which case it takes `--keep` and a pin edit.** The allowlist is in `scripts/run-allowlisted.py:31-35`, and `test_the_allowlist_is_the_one_of_the_release_job` (`tests/functional/test_run_allowlisted.py:61`) holds it equal to `release`'s `before_script`, so a change there needs both. The job's shell keeps its variables (`.gitlab-ci.yml:213`). A project variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` would beat the pin or miss the directory, and no test reads the project's variables (contract 6; SEC-T751-05).
22. **A release document may hold no HTML other than comments, anywhere** (plan-143 § Outcome; refusal `verify-release-docs.py:703-709`; `--help` `:240-248`). Not only before its Cursor item: at any depth, before or after an anchor, even if the tag closes itself. The document then fails the gate. None of the 33 `v*.md` documents holds such HTML (plan-143 § Outcome); `_template.md` does, by design, until its placeholders are replaced.
23. **A change to the release script needs the same edit in `RELEASE_COMMAND`** (plan-140 § Outcome; `tests/functional/test_ci_hash_pins.py:88-90`). I read "release script" as the `script` line of the `release` job (`.gitlab-ci.yml:256`), which the pin compares exactly, and not the body of `scripts/publish-release.py` (my reading of the pin).
24. **A release candidate is a full release** (`CONTRIBUTING.md` § Pre-release tags, "There is no lighter path"; plan-141 § Facts): it needs the content on `main`, creates a GitLab Release with no pre-release flag, and needs the four ADR-011 re-acceptances (item 2). **A gate probe tag** proves the gates without `main`, a Release or acceptances; it does not prove the `release` job, and the drift gate's tree check refuses it, by design. It needs the user's approval, and a protected tag can be deleted only in the web interface. Plan-140's two sentences that a release candidate "would prove" these steps first are read with this item.
25. **The gate's other limits** (plan-143 § Outcome; `--help` `:249-263`; `document_refusal`, `:671-710`). A document longer than **131072 characters** (`MAX_DOCUMENT_CHARS`, `:160`), or one reaching the parser's nesting limit of **20 levels**, where a list item counts as two (`MAX_NESTING`, `:163`), is refused. The largest real document is 66,745 characters, and the deepest reaches level 5.
26. **`scripts/run-allowlisted.py` is code that every gate command passes through, and no pin reads it,** so a change to it is for code review (contract 6, `tests/functional/test_ci_hash_pins.py:29-31`; SEC-T751-02). The test catches only a careless change.
27. **Placeholders** (`docs/releases/_template.md:3`; `CONTRIBUTING.md:223-225`). Prose such as `<your-project>` outside code is refused, because the parser decides what is HTML. **A placeholder in a code span passes, so replace it with its value;** a code span is for literal text that keeps its angle brackets. Other placeholders are not read at all (SEC-T751-09), so a reader must check them.
28. **The first real tag pipeline's watch list** is `CONTRIBUTING.md`'s first-tag rehearsal (`:279-292`), with these limits from the second probe (section 8): the fetches may have been anonymous, so they do not prove `--keep CI_JOB_TOKEN`; the log shows that the removal ran, not that the credential is gone; `timeout` and `release` are unobserved; and the install is quiet. Review T751's condition is the same: the first tag pipeline confirms the removal, the wrapper and the fetches.
29. **No `docker` in an agent's brief unless the user approved it** (plan-143 § Outcome; plan-144 § Facts). `DOCKER_HOST` points at a remote host that runs the user's own containers (section 4.3).
30. **A verdict section may hold a second heading of its name in neither a real heading nor displayed HTML** (plan-142 § Outcome, which asks for this item; plan-144's list does not name it, and I carry it from there). A second real heading is an error (`--help` `:296-297`), and displayed HTML is now refused anywhere (item 22). A comment or a `~~~` fence above the section does pass (SEC-T748-04).

### 6.3 Dates

Carried from v10 § 6.3. Plans 142 to 144 add none.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced; CWSO not read **(unverified)** | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v6, v7, v8 and v9, which did not re-read them; nor did I **(unverified)**.

Not a debt date, carried from v10's note: `.gitlab-ci.yml:18` holds `ci_images_reviewed_on: 2026-10-22`, and `MAX_REVIEW_AGE_DAYS = 120` (`tests/functional/test_ci_hash_pins.py:1255`) is what `test_the_review_date_is_present_and_fresh` (`:1283`) enforces. By reading, not by running it, the test starts to fail after 2027-02-19.

## 7. User actions

Carried from v10 § 7. A-19 widens to both probe tags, and A-20 is new. I did not re-check any other state.

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
| A-18 | Check that the release tags are protected | **closed**: `v*` tags are protected and Maintainers may create them (same read). **The limit stands:** a Maintainer can still tag a commit that never went through a merge request, so the merge guard does not cover that tag (contract 6, `tests/functional/test_ci_hash_pins.py:39-40`) | - |
| A-19 | **Delete the tags `v9.0.0-gate.1` and `v9.0.0-gate.2` in the web interface.** The user approved deleting the first ("1. Delete"); no source records an answer on the second **(unverified)**. `git push --delete` is refused for a protected tag. The local tags are deleted. A pre-release sorts below its core version, so `resolve_previous_tag` still returns `v9.0.0` for `v10.0.0` (plan-144 § Facts) | **open: both are on the remote.** `git ls-remote --tags origin`, 2026-11-06, my read: `v9.0.0-gate.1` peels to `57612f29`, `v9.0.0-gate.2` to `035bf433` | - |
| A-20 | Provide a dedicated runner, for SEC-T741-17's runner tag (plan-143 § Goal) | open | - |
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open (unchanged since v4; not re-checked) | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open (same) | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open (same) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- **Carried statuses**: v10 rows and lists, plus plans 142 to 144 and reviews T748 and T751. Greps and line reads on `8d4f1ea0` where cited. Plan-144 § Facts is the only source for the second probe, the flaky test and the Docker deviation. I called no API other than `git ls-remote`.
- **Counting**: a script takes the 119 carried ids from v10's sections 2.1 to 2.3 and 3, and the new ids from the reviews' finding tables rather than from plan-144. It checks that each carried id occurs in section 2 here, and expands section 5 to 75 distinct ids, equal to the carried ids still open or tracked plus the 15 new. Plan-144's expected counts were derived by the orchestrator; this check was run separately and they match: 596, 469, 46, 6, 1, 74, and all 14 batch sizes.
- **Where the sources differ or leave a gap** (none changes a status beyond what section 1 states):
  - **T748's 9 tracked and plan-142's list.** Review T751 § Q7 and plan-143 § Outcome are later; section 1.3.
  - **"Closed on the gate's route" for SEC-T748-02.** Plan-143 and review T751 file it next to -13, but its reported shapes are closed on a direct call too (section 3).
  - **The checklist item from plan-142.** Plan-144 does not list it; section 6.2, item 30 carries it.
  - **`--help` `:244-245`** keeps the steer that SEC-T751-03 removed elsewhere (section 3). I mint no id.
  - **The reference title under SEC-T748-04.** Plan-142, review T748 § 9 and review T751 § Q7 keep it, by hand trace; my one literal shape did not reproduce it (section 3).
  - **SEC-T751-06.** The orchestrator's run and mine differ (section 5).
  - **The second probe's tag** has no recorded approval for deletion (A-19).
- **What real jobs proved.**
  - **The second probe** (pipeline 3038460622, tag `v9.0.0-gate.2` on `035bf433`, runner 19.5.2, 2026-11-06; plan-144 § Facts; jobs not re-read here). `git show --stat 035bf433` confirms its parent is `9c7f2fad` and that it changes the three marker files and adds a release document; no local or remote-tracking branch contains it. `release-docs-gate` (job 17821516208), success in 9.7 s: the removal ran, pip and the gate ran through the script, and cleanup showed no error. `main-develop-drift-gate` (job 17821516209), failed as designed: `apk`, both fetches under `--keep CI_JOB_TOKEN` and the drift check passed through the script, then `check-release-tag-tree.py` refused the tag. `release` (job 17821516210), skipped; no GitLab Release was created.
  - **The first probe** ran the code before plans 142 and 143 (v10 § 8; pipeline 3037074733). It stands for `needs` holding on a failed gate, and for nothing about these plans.
- **What the second probe does not prove** (plan-144 § Facts):
  - **the credential path:** the project's visibility is `public` (read through the API on 2026-11-06), so the fetches may be anonymous. They show the allowlist does not break a fetch here, not that `--keep CI_JOB_TOKEN` is needed or works;
  - **that the credential is gone:** the log shows the removal ran. That it was the right path rests on source reading of the runner, and the flag `FF_GIT_URLS_WITHOUT_TOKENS` on this runner is unknown;
  - **the `timeout`,** which was not reached;
  - **the `release` job and its clone setting,** which did not run, so D-T710-2 and the escaped references are still unobserved;
  - **the parser's version:** the install is quiet, and the hashes are what tie it to the lock.
  - Carried from v10: the log's "Fetching changes" and "Created fresh repository" might also print under fetch **(unverified)**, so the clone setting works with these jobs, not that it changed anything.
- **What was run locally on the second tag** (the orchestrator, plan-144 § Facts; not re-run here): the docs gate and the drift check passed, and the tree check exited 1.
- **What GitLab's APIs proved** (the orchestrator, live, read-only; not re-run here; the deployed version is unknown to the reviewers).
  - **The Markdown API:** section 4.4. It shows that API only.
  - **The CI lint:** valid at T750, with only the 3 tag jobs on the tag route; review T751 calls this "your report", and plan-143 § Outcome does not repeat it **(unverified)** here. The lint shows what would run, not what a job does.
  - **The settings and variables** of v10 § 7 and § 3 were read on 2026-11-06 and not re-read.
- **What is a hand trace** (the reviewers, read-only, no shell, no code run). All rulings of reviews T748 and T751, apart from the orchestrator's runs in their records. T748 read `markdown_it` 3.0.0's `fence.py`, parts of `state_block.py`, `lheading.py` and `html_block.py`; 4.2.0's source was read by neither. T751's runner evidence is `shells/abstract.go`, `shells/bash.go`, `common/build.go` and `helpers/featureflags/flags.go` at v19.5.2 through a summarising fetch.
- **What I ran** (read-only, each under `timeout`, local `markdown-it-py` 3.0.0, nothing written in the worktree): 18 small documents through `document_refusal`, `section_heading_indexes` and `verdict_placeholder_problems` directly; `LINK_RE` timings; and the whole gate on `[` documents on a deleted scratch copy, under `ulimit -v`. These are checks on the rows above, not new rulings. The locked 4.2.0 was not run.
- **Reported, not re-run here**: 42 + 10 mutations on plan-142 and 43 + 21 + 36 + 3 on plan-143, with the limits plan-142 and plan-143 § Outcome state (the implementer's first-round mutations and the first 43 and 20 ran before later edits and were not repeated); all `v*.md` on both parser versions; T750's run of the jobs' commands in the pinned image against a `file://` origin, so no credential path ran; T749's 48.43 s. No mutation and no full suite ran for this register.
- **Unverified**, carried from v10: the source of the "do first" flags other than the fixed SEC-T716-01; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates; which three gaps "Fix now in this batch (Recommended)" covered (v6 § 8); GitLab's rendering in a Release description (SEC-T716-03); the npm step in a tag pipeline; the lock on the musl image beyond the MR pipeline (section 6.2, item 8); whether the orchestrator's draft of the upstream report was ever shown to the user; adoption of Trivy 0.76.1; the questions shown to the user beyond ADR-012 and plan-133; each carried plan's actual deadline; whether the gate tolerates the leftover pointer sentence; whether targets receive the gate script and the template; GitLab's rendering of front matter (SEC-T739-04 is closed, and a refusal does not depend on it); which runner holds the Docker socket; `pip-audit`, which did not run for T739 either; the merged commit's two later changes in T739, which its reviewer did not see; the source of `markdown-it-py` 4.2.0, and of 3.0.0 beyond the files named above; bash's behaviour on the eight characters; the wording of SEC-T738-05 against the reviewer's report; the questions shown to the user for "N two go" and "parser go" beyond the plans; SEC-T730-06's code location; the deployed GitLab version; delivery of artifacts from a `pages` job to the gates, not observed; `parallel:matrix` on a tag, not run live, which the pin refuses anyway; the configured CI file path; that the crash of 2026-11-05 came from the "no seen-set" mutation, an inference; the skip count on plan-138's trees; SEC-T741-16's route itself; SEC-T741-17's state on a reused runner; what "review go" answered; the reviewers' partial reads of `test_ci_hash_pins.py` and `test_publish_release_job_token.py`; the value of `ANTHROPIC_API_KEY`, whose "already revoked" is the user's statement.
- **Dropped from v10's list, each with what settled it**:
  - **Sanitized attributes, and `<style>`, on the Markdown API**: observed (section 4.4). Not for a Release description.
  - **The `unset` line's effect, and `8ee1e2d3` not being reviewed**: the line is gone, and review T751 read what replaced it.
  - **The eight-character rendering, in part**: nothing settled it, and it stays under "bash's behaviour" above; GitLab's rendering of those characters stays under SEC-T716-03.
- **Unverified**, new, from reviews T748 and T751, and plan-143:
  - no real job has run `timeout` or clone on `release`; `.git/config` and the external config as a real job leaves them are not observed;
  - the deployed runner's flag `FF_GIT_URLS_WITHOUT_TOKENS`, and the Docker executor's container environment;
  - variable precedence for `GIT_STRATEGY` and `CI_PROJECT_DIR` at group and instance level (from memory of the docs);
  - whether U+2800 and its like render blank for every font and renderer (the API shows U+2800 in an `h2`);
  - that `verdict_placeholder_problems` and `section_text` have no callers elsewhere: review T748 searched `develop`, and my search of `scripts/` and `.gitlab-ci.yml` on `8d4f1ea0` agrees;
  - `6c58244b`, which the reviewer did not re-read; `check-*.py` grepped on `develop`, not at `0e7a24ac`; `test_ci_hash_pins.py` read by the reviewer only through the diff; the new test of `99bfa0bc`, which the last read did not see;
  - no dependency changed and no audit ran for T747 to T751;
  - why the orchestrator's `[` run took 0.1 s (section 5); the reference title on 4.2.0 (section 3).
- **Not re-run here**: the suite and the gates, which the orchestrator ran before each merge (plan-142, plan-143 § Outcome). The reviewers' own unverified lists stand as written in their artifacts.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`, each with a time limit where it runs tests.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v10.md`; `plan-142-verdict-check-tokens.md`; `plan-143-batch-s-rest.md`; `plan-144-tracked-debt-register-v11.md`; `docs/tasks/task-T752.md`; `security-review-t748-batch-t-v1.md`; `security-review-t751-batch-s-rest-v1.md`; by grep or line range, the files named under Metadata, "Not opened". Decision IDs: ADR-011, ADR-012, as v10 cites them, not read here.
