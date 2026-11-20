# Artifact: tracked-debt-register-v27.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v26.md` (750 ids; v26 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-185-tracked-debt-register-v27.md` (§ User decision, § Facts since v26, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T886.md` (the user's "v27 go"); `docs/plans/plan-184-batch-v-release-gate.md` (Outcome); `docs/artifacts/security-review-t885-batch-v-v1.md` (per-id table, new findings, the tag-pipeline list, the orchestrator's addendum); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T886 (plan-185; the user's answer of 2026-11-20, verbatim: "v27 go"). **Date**: 2026-11-20.
- **Tree read**: branch `agent/tech-lead/T886` at `013a69df` (develop `fb577765` plus the plan-185 commit; `fb577765` is an ancestor, read here). The range for "lines added since v26" is `23884e50..013a69df` (plan-185 § Facts names `23884e50..fb577765`, 12 files, 1078 lines added; the one extra commit is plan-185's own plan, brief and ledger row): 15 files, 1177 lines added and 102 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `013a69df`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v25 only by grep (v11 to v19 § 5 rows for batch V's membership). Code files were read only as added lines, except `.gitlab-ci.yml:25` and `:359` (line read). No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **V** shrinks to its residual (SEC-T751-08) and takes **SEC-T885-01, -02, -03** (my suggestion), so 17 becomes 4. **X** loses SEC-T768-04 (fixed) and takes **SEC-T885-04** (my suggestion), so stays 6. No new letter.

## 1. Summary

v27 holds **754 ids**: the 750 of v26 and **4 new**. After v27: **592 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **103 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. T885: "0 CRITICAL, 0 HIGH, 0 MEDIUM". The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v26, from tracked-LOW (17)**: 16 of batch V and SEC-T768-04 of batch X (section 2.2).
- **Partly fixed, stays tracked-LOW (1)**: SEC-T751-08 (batch V; section 2.2).
- **New and tracked-LOW (4)**: SEC-T885-01, -02, -03 (batch V), SEC-T885-04 (batch X) (section 3; batches my suggestion).
- **Next-release checklist**: 35 numbers carried, 1 new (item 52: T885's seven tag-pipeline points, with the user's variable check) (section 6.2). **Dates**: as v26 (section 6.3). **User actions**: v26's, plus the variable check (section 7).

Arithmetic, from the v26 totals:

| Status | v26 | leaves | enters | v27 |
|---|---:|---|---|---:|
| fixed | 575 | | + 17 tracked-LOW (16 of V, SEC-T768-04 of X) | **592** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 116 | - 17 fixed | + 4 new (SEC-T885-01 to -04) | **103** |
| **all** | **750** | | + 4 new ids | **754** |

Check: 592 + 46 + 12 + 1 + 103 = 754. Open or tracked: 103 + 1 = 104, the size of section 5.

### 1.1 Ids by v26 status and status now

| v26 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 116 | 17 | 0 | 0 | 0 | 99 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 575 | 575 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v26 ids** | **750** | **592** | **46** | **12** | **1** | **99** |
| new in v27 | 4 | 0 | 0 | 0 | 0 | 4 |
| **all v27 ids** | **754** | **592** | **46** | **12** | **1** | **103** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t885-batch-v-v1.md` § New findings: SEC-T885-01, -02, -03, -04 | 4 | 0 | 0 | 4 |
| **All new** | **4** | **0** | **0** | **4** |

**Ids minted in the range beyond the plan's list: none.** A search of the 1177 added lines in `23884e50..013a69df` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (32 distinct tokens), set against the text of registers v1 to v26, finds as in no register exactly SEC-T885-01, -02, -03, -04. The two non-id matches are `ISO-8601` and `UTF-8`. The bare form `SEC-T885` occurs only as the prefix of those four.

**Ids named with no change of status** (in the range; statuses carried and not re-traced id by id beyond the grep): SEC-T745-03, SEC-T745-05, SEC-T745-06 (fixed, v11), SEC-T748-02 (fixed, v11), TL-T649-12 (fixed, v2), SEC-T660-01, SEC-T665-01 (accepted, v26), K-20 (open), SEC-T751-08 (tracked-LOW; partly fixed, section 2.2). **Ids named with a change** are those of sections 2 and 3. This register mints no id.

## 2. v26 ids re-checked

Every v26 `open`, `tracked-LOW` and `accepted` id (163) is covered: the changed ones have a row here, the rest are unchanged and carried. The v26 `fixed` and `obsolete` ids stay as v26 records them.

### 2.1 v26 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v26 `tracked-LOW` (116)

**Batch V's membership, traced** (v26 § 5 says "as v25 § 5", back through v18 to v17 § 5): v11 § 5 SEC-T748-03, -04, -05, -06, -07, -08, -09, -12, SEC-T751-01, -05, -06, -07, -08, -09 (14); v12 § 5 adds SEC-T773-01 (15); v17 § 5 adds SEC-T811-03 and TL-T819-05 (17) (read here). All 17 are in T885's per-id table.

**Changed to fixed (17).** Status and basis are T885's per-id table (reviewer's words shortened); the fix commits are plan-184 § Outcome's (T883 `a63d4f76`; T884 `74a1a54b`, cherry-picked as `c4b53aba`; MR !712, develop `fb577765`).

| Id | v26 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T748-03 | V | **fixed** (T883) | `_heading_problems` reports a section end heading that is setext or `# `; tests for `Text\n---`, `Text\n===`, `# Next` |
| SEC-T748-04 (rest) | V | **fixed** (T883) | `stray_heading_lines` refuses the exact heading line outside a heading, closed fence or HTML block. **Remainder, documented as planned, not a new id**: indented copies inside a `~~~` fence and the wrapper case |
| SEC-T748-05 | V | **fixed** (T883) | `look_alike_heading_lines` folds format characters, fillers, white space and case. Homoglyphs are not folded: SEC-T885-02 (new) |
| SEC-T748-06 | V | **fixed** (T883) | Field markers `+`, `1.`, `1)`, `>`; empty field takes its sub-items; otherwise "field has no value" (fails closed) |
| SEC-T748-07 | V | **fixed** (T883) | Docstring "Tested on the locked version"; a closing fence must end with the opening markup |
| SEC-T748-08 | V | **fixed** (T883) | Help text and docstring corrected; the help test asserts the new phrases and the absence of the old |
| SEC-T748-09 | V | **fixed** (T883) | `## Install`, `## Highlights` found through `section_heading_indexes`; comment, code, `###`, blockquote forms refused |
| SEC-T748-12 | V | **fixed** (T883) | `is_visible_char` is an allowlist; punctuation-, symbol- or emoji-only headings count as empty (fails closed) |
| SEC-T751-01 | V | **fixed, runtime unproven** (T884) | `rm -rf "${CI_PROJECT_DIR}.tmp"` after the last fetch, pinned and mutation-tested. **Runtime proof**: item 52 point 3 and 6 |
| SEC-T751-05 | V | **fixed, control on the user side** (T884) | The precedence clause names project, group and instance level and `CI_PROJECT_DIR`; `CONTRIBUTING.md` asks the user to check the three settings pages; no test can read them. **The check itself**: item 52 point 7, section 7 |
| SEC-T751-06 | V | **fixed** (T883) | A refused document is not link-checked; `LINK_RE` text part linear (plan-184 § Outcome: worst case 7.62 s before, 0.001 s after). The tail is still quadratic: SEC-T885-01 (new) |
| SEC-T751-07 | V | **fixed** (T884) | Every Python child of the two gates runs `python3 -I` (4 children, each mutated); AST test: no gate script imports a sibling. The `release` job is outside this id's scope: SEC-T885-03 (new) |
| SEC-T751-09 | V | **fixed** (T883) | `<tech-lead` added to `PLACEHOLDER_MARKERS`, with a test. **The optional part (exact `_template.md` placeholders outside code) was not taken**; per T885, recorded as not taken, **not open, no id** |
| SEC-T773-01 | V | **fixed** (T883) | The UTF-8 test skips at most one missing pointer, only the next major, minor or patch after the newest document; 11 negative cases |
| SEC-T811-03 | V | **fixed** (T884) | `untagged_route_problems` refuses `trigger` and `inherit` on every job; outside the tag jobs `tags` must be a non-empty list of literals; 8 mutation shapes refused. File-level `include` is refused by `REFUSED_TOP_LEVEL` (`tests/functional/test_ci_hash_pins.py:154`; T885 addendum, not re-read here **(unverified)**) |
| TL-T819-05 | V | **fixed** (T884) | The comment rests on a reading of the GitLab Runner v19.5.3 source (credential in `$CI_PROJECT_DIR.tmp/.gitlab-runner.ext.conf`, or a credential helper with `FF_GIT_URLS_WITHOUT_TOKENS`); marked as source reading |
| SEC-T768-04 | X | **fixed, runtime unproven** (T884) | The drift gate runs the four store checks of `ca-chain-check-python` plus `--ca-release` before the fetches; `release-docs-gate` and `release` run `--ca-release`. No image digest or runner tag changed. **Runtime proof**: item 52 points 2 to 4. That the drift gate shares `ca-chain-check-python`'s image is true today (T885 addendum: all four jobs name the same `python:3.12-alpine` digest) but not pinned: SEC-T885-04 (new) |

**Partly fixed, stays tracked-LOW (1).**

| Id | Batch | Changed note | Source |
|---|---|---|---|
| SEC-T751-08 | V | T883 refuses one code span holding both `\|` and `<` in a paragraph that may be a table (the literal rule failed `v8.0.0.md:104` and 18 older published documents). **Residual bypass**: `` \| `a\|` `<b>` \| `` (two spans; GitLab's GFM table split leaves `<b>` live). **Follow-up**: run `live_html_line` a second time on a parse with the GFM table rule enabled (`MarkdownIt("commonmark", ...).enable("table")`), and show that all 19 published documents keep their result. LOW: committer-only, reviewed in an MR, GitLab's sanitiser applies | T885 § Ruling on SEC-T751-08; plan-184 § Outcome |

**Unchanged (99 tracked-LOW; v26 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, X 5 (SEC-T756-02, TL-T761-11, SEC-T867-01 with TL-T876-04, SEC-T867-02 with TL-T876-04's date print, SEC-T881-02), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 3. 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 5 + 11 + 2 + 5 + 3 = 98; with SEC-T751-08 (changed note), 99 carried; with the 4 new, 103 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v26 and not recounted id by id; V and X were traced.)

### 2.3 v26 `accepted` (46)

**Unchanged (46)**, with their v26 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. The range names SEC-T660-01 and SEC-T665-01 only in plan-185's restatement of § 6.1.

## 3. New ids

Grades are the reviewer's own (T885 § New findings). Owner devops-engineer for all four (the surfaces of batches V and X; the orchestrator assigns).

| Id | Grade | Short description | Status | Remediation (T885) | Batch |
|---|---|---|---|---|---|
| SEC-T885-01 | SECURITY:LOW (A04, resource use) | `scripts/verify-release-docs.py` `LINK_RE` tail `\(([^)]+)\)` still quadratic on repeated `[a](` with no `)` (seconds per document at the 131072-character cap, not measured); committer-only, bounded by the job timeout | **tracked-LOW** | `\[[^\[\]]+\]\(([^()\s]+)\)` (or `[^()\n]+`); show the real documents give the same links; timing test for the `[a](` shape | V |
| SEC-T885-02 | SECURITY:LOW (A04) | `folded` / `look_alike_heading_lines` do not fold confusables: `## RELEASE VЕRDICT` (Cyrillic Е) ends the real section, its body unchecked | **tracked-LOW** | NFKC plus a wildcard for each non-ASCII letter (or a UTS #39 skeleton); a Cyrillic or Greek test | V |
| SEC-T885-03 | SECURITY:LOW (A08) | `release` job runs `python3 scripts/publish-release.py` without `-I` in the one job holding `CI_JOB_TOKEN` (`.gitlab-ci.yml:359`, read here); a committed shadow module would run with the token | **tracked-LOW** | `python3 -I`, after an AST check of sibling imports; update `RELEASE_COMMAND`; extend `python_child_problems` to `release`; a mutation. T885 recommendation 2 (ahead of -01, -02, -04) | V |
| SEC-T885-04 | SECURITY:LOW (A05) | No pin that `main-develop-drift-gate`'s `image` and `openssl` constraint equal `ca-chain-check-python`'s; the new CA lines assume it (true today, T885 addendum) | **tracked-LOW** | A pin comparing both jobs' `image` and `apk add` `openssl` constraint | X |

**Why V for SEC-T885-01, -02, -03.** All three are the release gate that V covers: -01 and -02 sit in `verify-release-docs.py` next to the V fixes they follow (SEC-T751-06, SEC-T748-05), and -03 is SEC-T751-07's hazard in the third tag job. Same owner, same tests (`test_verify_release_docs`, `test_ci_hash_pins`), same trigger (the next release-gate change).

**Why X for SEC-T885-04.** It pins the CA control (SEC-T768-04's surface, X until now) to the CI image, and its trigger is X's: the next tag-job or image change. A new letter for one id would split the CI surface (v12 Metadata).

## 4. Decisions since v26

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-20 | "V go"; plan approval "Approve (Recommended)" | Batch V (plan-184) | T885 header; plan-184 |
| 2026-11-20 | "v27 go" | This register | plan-185 § User decision; T886 brief |

I did not verify the words beyond those records **(unverified)**.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T751-08 narrow rule (literal rule failed 19 published documents) | Partly fixed; residual tracked LOW | T883, T885; the orchestrator | plan-184 § Outcome |
| SEC-T751-09 optional part | Not taken, not open | T885; the orchestrator | T885 per-id table; plan-184 § Outcome |
| Plan-142's ruling 5 (misspelt `## Gate verdicts` passes) | Replaced by SEC-T748-05's look-alike error | T885 question 5 | T885 |
| T885's two assumptions | Checked: one image digest; top-level `include` refused | the orchestrator | T885 addendum |
| Batches of the four new ids | V (-01, -02, -03), X (-04) | **mine** (suggestion) | section 3, section 5 |
| SEC-T751-01, SEC-T768-04 "runtime unproven", SEC-T751-05 "control on the user side" counted `fixed` | As T885's per-id status; the proof goes to item 52 | **mine** | section 2.2 |
| Merges, pipelines, ledger | As plan-185 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** 754 ids; fixed 575 + 17 = 592; tracked-LOW 116 - 17 + 4 = 103; open 1 (K-20); V 17 → 1 before the new ids, X 6 → 5. The placement of the new ids is mine: V 1 + 3 = 4, X 5 + 1 = 6, batch total 104.
- **Plan-184 § Outcome wording.** "For register v27: Fixed: the 17 ids above and SEC-T768-04 (batch X)" reads as 18; the ids above are 11 (T883) + 6 (T884, SEC-T768-04 among them) = 17, and T885's table gives 17 resolved. 17 is right; a wording slip only.
- **The commit range.** Plan-185 § Facts names `23884e50..fb577765`; this register searched `23884e50..013a69df`, adding plan-185's own commit, which mints no id.
- **SEC-T751-01, SEC-T768-04 "runtime unproven".** Counted `fixed` as T885 grades them; if the first `v*` tag pipeline does not show item 52 points 3 to 6, they reopen.
- **Ledger.** Plan-185 § Facts: "0 active, 682 completed". Read here: `completed-tasks.md` holds 682 task rows and `active-tasks.md` one (T886, added by the plan-185 commit). No difference.

## 5. Open items by LOW batch

Carried from v26 § 5; V shrinks to its residual and takes three new ids; X changes members, not size.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v26 § 5 | 24 | as v26 | as v26 |
| K | Security runtime | as v26 § 5 | 8 | as v26 | as v26 |
| L | CWSO helper scripts in emage.code | as v26 § 5 | 5 | as v26 | as v26 |
| M | CWSO repository | as v26 § 5 | 12 | as v26 | as v26 |
| N | Release tooling, second round | as v26 § 5 | 10 | as v26 | as v26 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v26 | as v26 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v26 | each release's preparation |
| R | Release-gate text, second round | as v26 § 5 | 7 | as v26 | as v26 |
| **V** | Release gate, third round (after plan-184) | SEC-T751-08 (residual); **new:** SEC-T885-01, SEC-T885-02, SEC-T885-03. **Left (fixed):** SEC-T748-03, -04, -05, -06, -07, -08, -09, -12, SEC-T751-01, -05, -06, -07, -09, SEC-T773-01, SEC-T811-03, TL-T819-05 | 4 | devops-engineer | the next change to `scripts/verify-release-docs.py` or the tag jobs; SEC-T885-03 first (T885 recommendation 2), then SEC-T751-08's GFM-table check (recommendation 1) |
| **X** | CI images, the CA control, the CI locks and the pin-age check | SEC-T756-02, TL-T761-11, SEC-T867-01 (with TL-T876-04), SEC-T867-02 (with TL-T876-04's date print), SEC-T881-02; **new:** SEC-T885-04. **Left:** SEC-T768-04 (fixed) | 6 | devops-engineer | SEC-T885-04 at the next tag-job or CI image change; the others as v26 |
| Y | Shipped text and records | as v26 § 5 | 11 | as v26 | as v26 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v26 | as v26 |
| U | Live checks and user | as v26 § 5 | 6 | as v26 | as v26 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v26 | as v26 |

Total 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 6 + 11 + 2 + 6 + 3 = **104** = 103 tracked-LOW + 1 open (K-20). Against v26's 117: V - 16 + 3, X - 1 + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Rows changed against v26: V and X.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v26 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range; T885 accepted none.

### 6.2 Next release checklist (the release after v12.0.0)

v26 § 6.2 stands with its numbers and text (35 numbers: 26 rules, item 8 open, items 43, 44, 46 to 49 carried, items 50 and 51). Changes:

- **Item 8** stays open: no tag pipeline ran in the range.
- **Item 17** (rule): unchanged; SEC-T881-02 stays in X.

**New (1):**

52. **The first `v*` tag pipeline after plan-184 must show** (T885 § What the first `v*` tag pipeline after this change must show; the proof for SEC-T751-01, SEC-T751-05 and SEC-T768-04, section 2.2):
    1. All three tag jobs ran on the dedicated runner (tag `release-gate`), no other job ran on the tag, no child pipeline started, and no included file added jobs.
    2. `release-docs-gate`: `--ca-release` passed before pip; pip ran as `python3 -I -m pip`; `verify-release-docs.py` ran as `python3 -I` and its version check reported no import error; the checkout lines name `CI_PROJECT_DIR` as GitLab sets it, with `GIT_STRATEGY` `clone`.
    3. `main-develop-drift-gate`: the copy of the shipped store worked; `--ca-release` passed before and after `apk add`; `apk add 'openssl~=3.5' 'git~=2.54'` succeeded; `sha256sum -c` passed; the four store runs each ended in `RESULT: PASS`; both fetches worked with `--keep CI_JOB_TOKEN`; `rm -rf "${CI_PROJECT_DIR}.tmp"` ran after the second fetch; both scripts after it passed as `python3 -I`.
    4. `release`: `--ca-release` passed before `publish-release.py`, and the Release was created.
    5. No job log shows the job token (masked as `[MASKED]`), and no line of these jobs echoes an expanded variable.
    6. The runner's cleanup stage finished without a failure caused by the missing `.tmp` directory (a warning is acceptable; record it).
    7. **The user's check, recorded**: no CI/CD variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists at project, group or instance level (section 7).

    If points 3 to 6 fail, SEC-T751-01 and SEC-T768-04 reopen; if point 7 finds such a variable, SEC-T751-05 reopens. Point 1 also re-checks item 44's runner rule.

Count: 35 carried + 1 new = 36 numbers.

### 6.3 Dates

Unchanged from v26 § 6.3 (all still ahead on 2026-11-20): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml:25`, read here; no change to that line in the range), 2027-03-19 the last passing day.

## 7. User actions

v26 § 7 stands, with one addition:

- **New: the CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists (`CONTRIBUTING.md` rehearsal item, plan-184). Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).

## 8. Method, limits and validation

- **Carried statuses**: v26's rows and lists, plus the sources in Based on. Plan-185 § Facts and plan-184 § Outcome are the only sources for the merges (!711, !712), the pinned sha `0356d308`, the clean suite (2859 OK, skipped=25) and the pipelines (3093169686, 3093169620). `docs/tasks/completed-tasks.md` holds 682 task rows and `active-tasks.md` one (T886) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 1177 lines added in `23884e50..013a69df` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v26; the result is section 1.2.
- **Counting**: 4 ids new, 4 counted; 17 status changes into `fixed` from tracked-LOW; 1 changed note (SEC-T751-08). Section 5 expands to 104 ids; the sizes of unchanged batches are v26's, not recounted id by id; V was traced through v11, v12 and v17 § 5, X from v26 § 5.
- **Still unverified**:
  - Carried from v26 § 8.
  - The T883/T884 code beyond the added lines and T885's reading of it; `test_ci_hash_pins.py:154` (the addendum's `REFUSED_TOP_LEVEL`).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v26 § 5", and the statuses of the ids named with no change in section 1.2.
- **Not run here**: the suite, the pipelines, `verify-release-docs.py`, the generator.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v26.md`; registers v11, v12, v17 (§ 5, batch V) and v1 to v25 (the token scan, by grep); `plan-185-tracked-debt-register-v27.md`; `docs/tasks/task-T886.md`; `plan-184-batch-v-release-gate.md` (Outcome); `security-review-t885-batch-v-v1.md` (all sections, addendum); `checkpoint-044-release-v12.0.0.md` (by reference);
  - by line read: `.gitlab-ci.yml:25`, `:359`; `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md` (row counts);
  - `git diff --shortstat`, `--stat` and `-U0` of `23884e50..013a69df`; `git merge-base --is-ancestor fb577765 013a69df`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
