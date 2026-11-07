# Artifact: tracked-debt-register-v8.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v7.md` (528 ids; v7, v6 and v5 stay the record for the text of every id that did not change, and, with v1 to v4, for every id that was `fixed` or `obsolete` there); `docs/plans/plan-137-tracked-debt-register-v8.md` and `docs/tasks/task-T740.md` (the user's "v8 go"); `docs/plans/plan-135-batch-n-two-gate-fixes.md`; `docs/plans/plan-136-release-gate-markdown-parser.md`; `docs/artifacts/security-review-t738-batch-n-two-v1.md`; `docs/artifacts/security-review-t739-gate-parser-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01, superseded in part), ADR-012 (Accepted 2026-11-04), as v7 cites them, not re-read; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T740 (plan-137; the user's answer of 2026-11-05, verbatim: "v8 go"). **Date**: 2026-11-05.
- **Tree read**: branch `agent/tech-lead/T740` at `8292c1bb` (develop `b79ee2d1` plus the plan commit, which adds plan-137, the brief and a ledger row). Commits since v7's merge `ecea7b5c`: `6e724383` (T738, squashed), `4112006d`, `9e43d135` (T739, squashed), `b79ee2d1`, `8292c1bb`. Nothing under `implementation/`, `docs/releases/`, `docs/decisions/`, `ci/js/`, or in `scripts/install.sh`, `scripts/publish-release.py`, `scripts/check-release-tag-tree.py`, `ci/requirements-ci.in` or `ci/requirements-ci.txt` changed since v7's tree `a4c3c7b3` (`git diff --name-only`), so v7's lines in those paths stand. The CWSO repository was not read: every CWSO status carries over from v7.
- **Review mode**: read-only. A closure cites plan-135, plan-136 or one of the two reviews. "Unchanged" means no task, review or plan outcome since v7 names the id with a change of status, checked by searching the lines added in `ecea7b5c..8292c1bb` for every carried id (section 8). The code was not re-checked unless a line is cited. Anything not traced is **(unverified)**.
- **Reviewed trees**: review T738 read `921c0871`; review T739 read `ce546409`. Between `ce546409` and `b79ee2d1` the only code change is three lines in `tests/functional/test_verify_release_docs.py` (`git diff`): the timing limit from 1.0 to 5.0 and its comment. The reviewer did not see them. `scripts/verify-release-docs.py`, `.gitlab-ci.yml`, `ci/` and `tests/functional/test_ci_hash_pins.py` are identical there, so review T739's lines in them hold. `CONTRIBUTING.md` is identical too, but the review cites its lines "on `develop`" before T739; section 3 gives the current ones.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository, registers v1 to v6. One read beyond the brief's list: `docs/artifacts/security-review-t730-t732-batch-g-v1.md`, by grep, for what the eight batch N ids cite. It is not a register. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5.
- **Batch letters**: I, J, K, L, M, P, Q, R, F and U keep their v7 scope. N loses three ids. **S** and **T** are new (section 5).

## 1. Summary

v8 holds **544 ids**: the 528 of v7 and **16 new**. After v8: **421 fixed**, **46 accepted**, **6 obsolete**, **1 open**, **70 tracked-LOW**.

- **Open above LOW: none**, with one qualification. The one open id is K-20 (live checks, user). Of the 16 new ids, 15 are graded LOW by the reviews (both: 0 CRITICAL, 0 HIGH, 0 MEDIUM). **TD-T739-01 has no reviewer's grade**: it is the orchestrator's id, tracked as debt by plan-136 § Outcome, which gives no severity word; plan-137 files it as tracked-LOW, and this register follows. The five accepted MEDIUMs (section 6.1) are accepted, not open; under ADR-011 four of them need the user's new acceptance at the next release (section 6.2, item 2).
- **Batch N's 3 changed ids**: all 3 fixed (SEC-T731-07, -08, -09). The other 8 are unchanged.
- **Stale citations in batch N: none.** The rewrite removed nothing the 8 ids cite. Four of them cite lines that have moved: three in the gate script, one in `publish-release.py` (section 5).
- **Due before the next release**: as in v7, SEC-T735-08 and SEC-T735-09 (section 6.2, items 2 and 10). Batch S has no such date: review T739 § 4 says "next sprint", and no source binds it to a release.

Arithmetic, from the v7 totals:

| Status | v7 | leaves | enters | v8 |
|---|---:|---|---|---:|
| fixed | 414 | | + 3 batch N + 4 new | **421** |
| accepted | 46 | | | **46** |
| obsolete | 6 | | | **6** |
| open | 1 | | | **1** |
| tracked-LOW | 61 | - 3 fixed | + 12 new | **70** |
| **all** | **528** | | + 16 new ids | **544** |

Check: 421 + 46 + 6 + 1 + 70 = 544. Open or tracked: 70 + 1 = 71, the size of section 5.

### 1.1 Ids by v7 status and status now

| v7 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 61 | 3 | 0 | 0 | 0 | 58 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 414 | 414 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v7 ids** | **528** | **417** | **46** | **6** | **1** | **58** |
| new in v8 | 16 | 4 | 0 | 0 | 0 | 12 |
| **all v8 ids** | **544** | **421** | **46** | **6** | **1** | **70** |

### 1.2 New ids by source

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t738-batch-n-two-v1.md`, SEC-T738 | 6 | 4 | 2 |
| `security-review-t739-gate-parser-v1.md`, SEC-T739 | 9 | 0 | 9 |
| plan-136 § Outcome, TD-T739-01 (not in either review's count) | 1 | 0 | 1 |
| **All new** | **16** | **4** | **12** |

A search of the lines added in `ecea7b5c..8292c1bb`, outside the held-out set, finds no other new id. The carried ids it finds are SEC-T731-07, -08, -09 and SEC-T735-06 (plan-137 only); SEC-T676-14, SEC-T703-01, SEC-T715-03 and SEC-T731-02, none of them an open, tracked-LOW or accepted id of v7, appear as code comments and help text with no change of status. `M-3` is an example heading in the gate's help. This register mints none.

### 1.3 How the reviews' counts map to ids

The reviews count findings, this register counts ids, so their numbers do not add up directly.

| Review | Its LOW count | Resolved | Remaining | As ids |
|---|---:|---:|---:|---|
| T738 | 9 | 3 (SEC-T731-07, SEC-T731-09(a), SEC-T738-05) | 6 (SEC-T731-09(b), SEC-T738-01 to -04, -06) | SEC-T731-09 is counted twice there, as (a) and (b), and stays one id here |
| T739 | 16 | 5 (SEC-T731-09(b), SEC-T738-01, -03, -04, SEC-T731-08) | 11 (SEC-T739-01 to -09, SEC-T738-02, -06) | 9 of the 16 are new ids; the other 7 were already counted. TD-T739-01 is not one of the 16 |

## 2. v7 ids re-checked

Every v7 `open`, `tracked-LOW` and `accepted` id (108) has a row or a list entry here: 1 + 61 + 46. The v7 `fixed` and `obsolete` ids stay as v7 records them.

### 2.1 v7 `open` (1)

K-20: **Unchanged**, open, batch U (A-7).

### 2.2 v7 `tracked-LOW` (61)

**Changed (3, batch N)**

| Id | v7 | now | Evidence |
|---|---|---|---|
| SEC-T731-07 | tracked-LOW | **fixed** | T738 (branch commit `31aae510`, squash `6e724383`). `verify-release-docs.py:622` now passes `INSTALL_SH` to `check_line_breaks`. Review T738 § 1 "SEC-T731-07 is closed", § 2. The user: "N two go". |
| SEC-T731-08 | tracked-LOW | **fixed** | T739 (squash `9e43d135`). `migration_section_tokens`, `verify-release-docs.py:503-516`. Review T739 § 2 "Closed as written. `section_text` remains for the verdict check; see SEC-T739-07". The user: "parser go". |
| SEC-T731-09 | tracked-LOW | **fixed** (one id, two parts) | Part (a): T738 (branch commit `c781c16f`, squash `6e724383`), review T738 § 1 "SEC-T731-09(a) is closed", the user: "N two go". Part (b): T739 (`9e43d135`), review T739 § 2 "Closed. Both forms are False", the user: "parser go". The code it sat on is gone: `html_block_opening` and `strip_hidden_markdown` have 0 hits in the script. |

**Unchanged (58 tracked-LOW; v7, v6 and v5 stay the record of their text)**

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

Total 58; with the 3 above, 61. SEC-T736-01 is "the rest" as v7 § 3 defines it.

### 2.3 v7 `accepted` (46)

**All unchanged**; basis as in v5 § 2.3, v6 § 6.1 and v7 § 2.3. None has a new acceptance.

- **MEDIUM (5)**: SEC-T657-01 / SEC-T658-01 (one id), SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07.
- **LOW or INFO (41)**: K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, K-15, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07.

## 3. New ids

Source: the two reviews (T738 § 2 and § 4; T739 § 2 and § 4; the reviewer's fix for each id is there) and plan-136 § Outcome. Owner per the heading of § 4 of each review: devops-engineer, "next sprint". Lines are current, read on `8292c1bb`, in `scripts/verify-release-docs.py` unless the path says otherwise.

| Id | Grade | Location now (as the review cited it) | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T738-01 | LOW | Code removed (`:488-489` on `921c0871`) | A wrongly opened type 7 block hid a fence or `<?` line that CommonMark keeps live. | fixed by T739 (`9e43d135`); review T739 § 2 "Closed" | - | - |
| SEC-T738-02 | LOW | `:548` and `:432` (`:437, 564` on `921c0871`); `scripts/install.sh:1295-1297`; `--help` `:213-215` | `read_text` translates a CR in `install.sh` to a newline, so the line splits and the Cursor requirement drops, though bash does not end a line there. | tracked-LOW. The plain-newline part is now documented in `--help` (review T739 § 4); the CR part stays open (plan-136 § Not changed) | devops-engineer | S |
| SEC-T738-03 | LOW | Code removed (`:155, 501` on `921c0871`) | `HTML_COMMENT_RE` hid too much: a false FAIL, and a false PASS for a visible anchor in the wrong section. | fixed by T739; review T739 § 2 "Closed. It is gone from this path, and both shapes are tested" | - | - |
| SEC-T738-04 | LOW | Text rewritten (`:153, 218-220, 501` on `921c0871`) | Three older claims contradicted the corrected docstrings. | fixed by T739; review T739 § 2 "Closed. One label stays misleading (SEC-T739-09)" | - | - |
| SEC-T738-05 | LOW | Code removed (`html_block_opening`, `has_cursor_migration_item` docstring on `921c0871`) | The new docstrings read as sufficient and complete. | fixed by the orchestrator's edit after the review, **not re-reviewed** (plan-135 § Outcome; review T738 § 2). Traceable: `git diff 921c0871 6e724383` on the script changes exactly those two sentences. That the words are the reviewer's is the record's statement; the review does not quote them **(unverified)**. T739 then removed `html_block_opening` and rewrote the docstring, so the text no longer exists. Review T739 does not name this id | - | - |
| SEC-T738-06 | LOW | `tests/functional/test_verify_release_docs.py:944` | `LineBreakCharacterTests.CHARS` holds raw U+2028 and U+2029, which render as spaces. The same file holds them raw at `:494` and `:989` too, which the review does not name (tech-lead's check; whether they need the same fix is not judged). | tracked-LOW | devops-engineer | S |
| SEC-T739-01 | LOW | `:566`; claim at `:20` | `errors="ignore"` drops invalid bytes before parsing, so a comment can close here that a renderer replacing the byte keeps open, and a hidden anchor counts. Older than T739. | tracked-LOW | devops-engineer | S |
| SEC-T739-02 | LOW | `inline_text`, `:470-482`; `--help` `:206-207` | Text between inline HTML tags counts, as in `**<span hidden>Cursor</span>**`. | tracked-LOW | devops-engineer | S |
| SEC-T739-03 | LOW | `:211-213` | Stated residual: `<div hidden>`, a blank line, then an anchor gives True. | tracked-LOW | devops-engineer | S |
| SEC-T739-04 | LOW | `:210-211` | Stated residual: a document opening and closing with `---` around the section reads as live here and may be front matter on GitLab **(unverified)**. | tracked-LOW | devops-engineer | S |
| SEC-T739-05 | LOW | `tests/functional/test_ci_hash_pins.py:180-188`, `release_gate_job_problems` | The pins do not catch `allow_failure: true`, `when: manual`, or an `exit 0` line before the gate; the script check is only membership. | tracked-LOW | devops-engineer | S |
| SEC-T739-06 | LOW | `.gitlab-ci.yml:196-206` | pip and `markdown_it` see `CI_JOB_TOKEN` and probably `WIKI_TOKEN` **(unverified: project settings)**. The `release` job filters its environment; this job does not. | tracked-LOW | devops-engineer | S |
| SEC-T739-07 | LOW | `section_text`, `:251-263`; `verdict_placeholder_problems`, `:266-277` | The verdict's placeholder check stays on line rules, and three crafted shapes pass with `- Status: pending` in place. Older than T739; plan-136 kept it on purpose. | tracked-LOW; "needs its own plan" (review T739 § 4) | devops-engineer | T |
| SEC-T739-08 | LOW | `docs/releases/_template.md:3`; `:569`; `CONTRIBUTING.md:408, 439` (`405, 436` "on `develop`", before T739) | "A line that starts with a bold lead" is looser than the parser: a false FAIL with a clear error. The two `CONTRIBUTING.md` lines do not point to step 4's install. | tracked-LOW | devops-engineer | S |
| SEC-T739-09 | LOW | `--help` `:210`; docstring `:20` | The nesting limit is neither stated nor tested. "What stays open (SEC-T738-04)" cites a closed id. Some shapes have no fixture. | tracked-LOW | devops-engineer | S |
| TD-T739-01 | **none** (the orchestrator's id; no reviewer graded it) | `has_cursor_migration_item`, `:526` | The parser scales worse than linearly on a line of many attributes, on 3.0.0: 0.059 s to 1.423 s from 10000 to 80000 repeats. Only a crafted document reaches it; the cost is job time, not a false PASS. A fix would be a limit on line or document length. The locked 4.2.0 was not measured (plan-136 § Outcome). | tracked-LOW | no source sets one. Suggested (tech-lead): devops-engineer, with the rest of S | S |

## 4. Decisions since v7

### 4.1 The user's (words verbatim as recorded)

Each row claims only what the plan records it asked. The questions as shown to the user were not verified beyond those records **(unverified)**.

| Date | Words | What the question asked, and the effect | Source |
|---|---|---|---|
| 2026-11-05 | "N two go" | The question named SEC-T731-07 and SEC-T731-09(a), the two small fixes the tech lead advised before the next tag. Run T738. It did not cover the other nine ids of batch N. v7's recommendation is overtaken | plan-135 Based on, § Not changed |
| 2026-11-05 | "parser go" | Whether the release gate should use `markdown-it-py`, which would close the false-pass group at the cost of a gate dependency. This settles what plan-135 § Outcome left open for the user. Run T739 | plan-136 Based on; plan-135 § Outcome |
| 2026-11-05 | "v8 go" | plan-137, T740 (this register) | plan-137 Based on |

### 4.2 Other decisions (not the user's)

| Id or item | Decision | By | Effect |
|---|---|---|---|
| SEC-T738-05 | Applied with the reviewer's wording, because it corrects claims the change wrote; not re-reviewed | the orchestrator (plan-135 § Outcome) | section 3 |
| Characterisation test | `test_the_known_false_passes_named_in_the_docstrings` stays, as the review allows | the orchestrator (plan-135 § Outcome) | T739 replaced it: the name has 0 hits in the test file now, as plan-136 asked |
| Plan-135's acceptance sentence | "each new test fails on the old code" is read as the review reads it: the tests that guard a fix | the orchestrator (plan-135 § Outcome) | none on status |
| Order in `main()` | "first, on every run" means gate runs; the parser check follows `parse_arguments` (`:599-603`). The review agrees | the orchestrator (plan-136 § Outcome) | `--help` and a bad argument run without the parser |
| `parse_arguments` | Extracted to keep `main` under the limit; stands | the orchestrator (plan-136 § Outcome) | `:584` |
| Knowledge text | No edit: the bare gate commands are not false, and the gate names the install; no root refresh | the orchestrator (plan-136 § Outcome) | `CONTRIBUTING.md` lines are in SEC-T739-08 |
| Timing limit | `test_a_long_tag_line_does_not_slow_the_gate` raised from 1.0 s to 5.0 s after pipeline 3031259271 failed at 1.23 s; not skipped, inputs unchanged; the reviewer did not see it | the orchestrator (plan-136 § Outcome) | `tests/functional/test_verify_release_docs.py:701-702` |
| TD-T739-01 | Minted, tracked until this register | the orchestrator (plan-136 § Outcome) | section 3 |
| Batches N, S and T | N loses three ids; S and T are new; SEC-T739-07 alone in T | plan-137 | section 5 |
| SEC-T731-07, SEC-T731-09(a) | v7's "fix before the next tag" was the tech lead's advice only | overtaken by the user's "N two go" | fixed |

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. Batch N's mark went with SEC-T731-09. I, J, K, L, M, P, Q, R, F and U are carried from v7 without change; in those rows "review" and "review § 4" mean the batch H review.

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
| **S** (new) | Release gate after the parser | SEC-T739-05, SEC-T739-01, SEC-T739-02, SEC-T739-04, SEC-T739-06, SEC-T739-08, SEC-T739-09, SEC-T739-03, SEC-T738-02, SEC-T738-06, TD-T739-01 | 11 | devops-engineer (review T739 § 4; TD-T739-01 is the tech lead's suggestion) | **open**: review T739 § 4 says "next sprint", and no source binds it to a release |
| **T** (new) | Verdict placeholder check on the token stream | SEC-T739-07 | 1 | devops-engineer (review T739 § 4) | none set: review T739 § 4 says only that it needs its own plan, and plan-136 § Outcome agrees |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 10 + 1 + 7 + 5 + 12 + 8 + 1 + 3 + 4 + 11 + 1 + 2 + 6 = 71 = 70 tracked-LOW + 1 open. No open item is above LOW, with the qualification on TD-T739-01 in section 1.

**Batch N, re-read on `8292c1bb`.** The rewrite of `verify-release-docs.py` removed the Cursor logic only, so **no id is stale**. The behaviour each finding describes still stands where a line is given; I did not re-run any. The reviewer's lines are at `3a4bfd4c`.

| Id | Review's citation | Now | Reading |
|---|---|---|---|
| SEC-T730-03 | `publish-release.py:562-586, 683` | `ApiCredential` at `:629`; `token` in `main()` at `:750` | Moved before v7's tree; file unchanged since. No `def __getstate__`, `__copy__` or `__deepcopy__` by grep |
| SEC-T730-04 | `ci/requirements-ci.in`, `ci/requirements-ci.txt:2-4` | same | `test_ci_hash_pins.py` has no `generated-on`, cooldown or gap check by grep. The new `ci/requirements-release.txt:3-4` has the same kind of prose header (tech-lead's observation; no source says so) |
| SEC-T730-06 | `publish-release.py`, "the fallback after the re-parse" | no line given; not located here | File unchanged since v7, so the rewrite cannot have touched it. The code was not re-read **(unverified)** |
| SEC-T731-03 | `verify-release-docs.py:142, 146` | `:160, 164` | `POINTER_LIKE_RE` text unchanged, moved. The new long-line test, `test_verify_release_docs.py:696`, drives `has_cursor_migration_item`; a grep finds no timing test on this regex, so the reviewer's test is still undone |
| SEC-T731-04 | `verify-release-docs.py:141-148` | `:159-166` | Same regex, moved |
| SEC-T731-05 | `verify-release-docs.py:183`, `check-release-tag-tree.py:48` | `:185`; `:48` | `UNSAFE_RE` text unchanged, moved. The equality test is at `test_verify_release_docs.py:1056` |
| SEC-T732-01 | `.gitlab-ci.yml:93-104` | same | Unchanged: `npm ci` at `:104`, `DOCKER_HOST` at `:97` |
| SEC-T732-02 | `ci/js/README.md:39-43` | same | Directory unchanged |

**Batch S, in short.** The order is review T739 § 4's, with SEC-T739-07 taken out to T. That order does not rank SEC-T738-02 and -06, which it names only in its opening sentence, or TD-T739-01; placing them last is my suggestion, and no source sets it. Review T738's own order put SEC-T738-02 and -06 first in that round.

- **SEC-T739-05 first**: it is the pin that would catch `allow_failure` on the job (section 6.2, item 15).
- **So the false-pass group is smaller, not gone** (plan-136 § Outcome): SEC-T739-01 to -04 remain for the Cursor check. Each needs a crafted file that survives merge request review.

**Batch T, in short.** SEC-T739-07 is the same class as batch S in another check. The orchestrator confirmed the three shapes on the commit (review T739 Metadata). The reviewer's fix reads these sections from the token stream, or at least refuses a second occurrence of the heading. Plan-136's design scope kept this check on line rules, so a fix extends the parser's use beyond what "parser go" asked **(tech-lead's reading; no source says so)**.

**Batch R, in short.** Carried from v7. **The route of SEC-T735-06 and -07 is still to be settled before batch R.**

- **SEC-T735-07: confirm the route first.** The reviewer's fix, "An acceptance covers", changes ADR-011's A1 text, and accepted ADRs are immutable (ADR-012 Status). The route is not settled; the review says only to confirm it.
- **SEC-T735-06** has the same question (tech-lead's reading, no source says so): its fix, that `mitigation` cites where the plan was shown, changes the Conditions line, which is ADR-012's row B3. The top-level session's comparison would be a new duty too.
- **SEC-T736-01 (the rest)** needs pins and mutations only, in the style of T736, and no knowledge text.
- **SEC-T693-07 has no text fix**: "the independent check is a duty in the role text, not an enforced control" (plan-133), and the residual is accepted by ruling with no edit. Batch R must not edit for it. It closes only if an enforced control is built, and nothing here proposes one.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 § 6.1 and v6 § 6.1 stand unchanged and stay the record, with v7 § 6.1. Plans 135 and 136 add and renew no acceptance. ADR-012 replaces rows A1, A8 and A12 of ADR-011 in part; the rest of ADR-011 stands: only the user accepts, one release only.

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 pin audit **2027-01-30 or the first Brave release above 2.1.4**; SEC-T702-09, SEC-T660-01, SEC-T665-01 and the SEC-T657-01/SEC-T658-01 remainder: **the next release needs the user's new acceptance** (ADR-011, ADR-012).

### 6.2 Next release checklist

Carried from v7 § 6.2, with its numbers. Item 7's second and third bullets are rewritten. Items 14 to 17 are new. Items 1 to 6 and 8 to 13 are v7's text; their lines were read on `a4c3c7b3`, under `implementation/knowledge/` unless the path starts at `docs/` or `scripts/`, and those paths have not changed since. Item 4's and item 13's `install.sh` lines were read again on `8292c1bb` and hold. In those items "review" means the batch H review.

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
   - **The blank-line rule is gone, and `## Migration Guide <!-- x -->` now counts** (plan-136 § Outcome). The gate reads the document with `markdown-it-py`'s CommonMark parser (`verify-release-docs.py:186-220` is the `--help` text, `:503-537` the code). The section is the first top-level level 2 heading whose text is exactly `Migration Guide`, in ATX or setext form, up to the next top-level level 1 or 2 heading in either form; a heading inside a blockquote or a list neither opens nor ends it. The Cursor item is, in that section, with the case-sensitive word `Cursor` in its text, either a top-level heading of level 3 to 6, or a paragraph, top-level or with only list containers around it, that opens with a `**` strong span, and only the text inside that span counts. Text means text and inline code, with a line break read as a space; an image's alt text and inline HTML never count. `__bold__`, an anchor in a blockquote and a heading in a list do not count.
   - **What still follows from that rule:** a bold lead must open its own paragraph. `Some text` followed on the next line by `**Cursor**` is one paragraph, so it does not count, and a blank line is still what a release author needs there. A heading does not need one. Run here on the local `markdown-it-py` 3.0.0; the orchestrator ran the same shapes on the locked 4.2.0 with the same results (plan-137 § Outcome). The error at `:569` says "lead line", which is looser than this (SEC-T739-08).
   - **Checked files may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`.** They are the tag's release document, the three marker files and now `scripts/install.sh` (SEC-T731-07) (`verify-release-docs.py:177`, `:622`). The error names the file, the line and the code point.
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
15. **The job must stay without `allow_failure`** (review T739 § 1): a PyPI outage fails the job closed, and that outage is when someone will be tempted to add it. `needs` in `release` does not stop a release after an allowed failure, and no test catches this yet (SEC-T739-05).
16. **A local gate run needs the parser.** Without it, every gate run exits 1 and prints the install command, which is the one to use, in a virtual environment (`verify-release-docs.py:144-150`; `CONTRIBUTING.md:164-167`): `python3 -m pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt`. A developer's system package may be another version; the job's locked run decides (plan-136 § Design).
17. **A regeneration of `ci/requirements-ci.txt` needs `ci/requirements-release.txt` too**: `test_the_release_lock_matches_the_ci_lock` (`tests/functional/test_ci_hash_pins.py:404`) enforces the versions and hashes (plan-136 § Outcome).

### 6.3 Dates

Carried from v7 § 6.3. Plans 135 and 136 add none.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced; CWSO not read **(unverified)** | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v6 and v7, which did not re-read them; nor did I **(unverified)**.

## 7. User actions

Carried from v7 § 7. Plans 135 and 136 add none and close none; I did not re-check any state.

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
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open (unchanged since v4; not re-checked) | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open (same) | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open (same) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- **Carried statuses**: v7 rows and lists, plus plan-135, plan-136 and the two reviews. Greps on `8292c1bb` where cited.
- **Counting**: a script takes the 108 carried ids from v7 §§ 2.1 to 2.3 and 3, checks that each occurs in sections 2.1 to 2.3 of this register, counts the rows of sections 2.2 and 3 by status, and expands section 5 to 71 distinct ids, equal to the carried ids still open or tracked plus the 12 new. Plan-137's expected counts were derived by the orchestrator; this check was run separately and they match: 544, 421, 46, 6, 1, 70, and all 13 batch sizes.
- **Where the sources differ or leave a gap** (none changes a status):
  - **The blank-line rule.** Plan-136 § Outcome and plan-137 say it is gone. As a rule of the gate it is. A bold lead directly after a text line still fails, because CommonMark continues the paragraph (section 6.2, item 7). `Some text` followed by a `###` heading now counts.
  - **`CONTRIBUTING.md` lines.** Review T739 and plan-136 § Outcome say 405 and 436; on this tree they are 408 and 439, because T739 added lines above them.
  - **Item 7's old citation** `verify-release-docs.py:41-45` is stale; the regex is at `:177`.
  - **SEC-T738-05.** The status rests on the plan's and the review's record. T739's review does not name the id, and the code is gone, so no later review confirms it.
  - **TD-T739-01** has no grade and is not in the reviews' counts. "tracked-LOW" here follows plan-137 and is not a reviewer's finding.
  - **Batch S's owner** comes from the heading of § 4 of the reviews, which also say "next sprint". No source has scheduled a sprint for it.
- **Unverified**, carried from v7: the source of the "do first" flags other than the fixed SEC-T716-01; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates; which three gaps "Fix now in this batch (Recommended)" covered (v6 § 8); live GitLab rendering (SEC-T716-03); the npm step in a tag pipeline; the lock on the musl image beyond the MR pipeline; whether the orchestrator's draft of the upstream report was ever shown to the user; adoption of Trivy 0.76.1; the questions shown to the user beyond ADR-012 and plan-133; each carried plan's actual deadline; whether the gate tolerates the leftover pointer sentence; whether targets receive the gate script and the template.
- **Unverified**, new:
  - the install of `ci/requirements-release.txt` in a tag pipeline (T739 reports the install and the gate in the pinned image under Docker; the orchestrator did not re-run that, plan-136 § Outcome);
  - GitLab's rendering of front matter, invalid bytes and sanitized attributes (review T739 § 5, SEC-T739-01, -02, -04);
  - the flags on `WIKI_TOKEN` (SEC-T739-06), tag protection, and which runner holds the Docker socket (review T739 § 5);
  - `pip-audit`, which did not run; the reviewer used PyPI's data (review T739 Metadata);
  - 4.2.0 for TD-T739-01, which measured 3.0.0 only (plan-136 § Outcome);
  - the merged commit's two later changes, the timing limit and its comment, which the reviewer did not see (Metadata above);
  - the source of `markdown-it-py` 4.2.0, which the reviewer did not read, and of 3.0.0 beyond two files (review T739 § 5);
  - GitLab's real rendering and bash's behaviour on the eight characters and CR (review T738 § 5);
  - the wording of SEC-T738-05 against the reviewer's report (section 3);
  - the questions shown to the user for "N two go" and "parser go" beyond the plans (section 4.1);
  - SEC-T730-06's code location (section 5).
- **Not re-run here**: the implementers' mutation runs, the suite and the gates, which the orchestrator ran before the merges (reviews § 5; plans' § Outcome). The reviewers' own unverified lists stand as written in their artifacts.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v7.md`; `plan-135-batch-n-two-gate-fixes.md`; `plan-136-release-gate-markdown-parser.md`; `plan-137-tracked-debt-register-v8.md`; `docs/tasks/task-T740.md`; `security-review-t738-batch-n-two-v1.md`; `security-review-t739-gate-parser-v1.md`; rows T738 and T739 of `completed-tasks.md` by grep; by grep or line range, `security-review-t730-t732-batch-g-v1.md`, `scripts/verify-release-docs.py`, `.gitlab-ci.yml`, `ci/requirements-release.txt`, `ci/requirements-ci.txt`, `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_verify_release_docs.py`, `docs/releases/_template.md`, `CONTRIBUTING.md`, `scripts/install.sh`, `scripts/publish-release.py`, `scripts/check-release-tag-tree.py`, `ci/js/README.md`. Decision IDs: ADR-011, ADR-012, as v7 cites them, not read here.
