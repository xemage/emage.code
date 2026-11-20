# Artifact: tracked-debt-register-v29.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v28.md` (759 ids; v28 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/artifacts/tracked-debt-register-v26.md` (§ 1.2 and § 2-3: the precedent for a duplicate id and for TL-T876-04); `docs/plans/plan-189-tracked-debt-register-v29.md` (§ User decision, § Facts since v28, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T892.md` (the user's "v29 go"); `docs/plans/plan-188-batch-x-round.md` (Outcome); `docs/artifacts/security-review-t891-batch-x-v1.md` (per-id table, new findings, the SEC-T881-02 count and recommendation, the orchestrator's addendum); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T892 (plan-189; the user's answer of 2026-11-20, verbatim: "v29 go"). **Date**: 2026-11-20.
- **Tree read**: branch `agent/tech-lead/T892` (develop `54d240ed` plus the plan-189 commit `3ee180d9`). The range for "lines added since v28" is `d524f90e..54d240ed` (plan-189 § Facts): 12 files, 420 lines added and 19 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range. The plan-189 commit itself is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v28 only by grep (v26 § 1.2, § 2.2 and § 5 by line read for the precedent). Code files were not read beyond what T891 reports; the diff was read as added lines only. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **X** drops its four fixed ids and takes **SEC-T891-01** and **SEC-T891-02** (my suggestion), so 6 becomes 4. No other batch changes; no new letter, no letter ends.

## 1. Summary

v29 holds **761 ids**: the 759 of v28 and **2 new**. After v29: **600 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **102 tracked-LOW**.

- **Open above LOW: nothing.** T891: "0 CRITICAL, 0 HIGH, 0 MEDIUM". The one open id is K-20 (live checks, the user; no grade). TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v28, from tracked-LOW (4)**: SEC-T885-04, SEC-T867-01, SEC-T867-02, TL-T761-11, all batch X (section 2.2). TL-T876-04 is counted with SEC-T867-01 and -02 (no id of its own, as v26 has it).
- **New and tracked-LOW (2)**: SEC-T891-01, SEC-T891-02 (batch X) (section 3). **SEC-T891-03 is not counted**: it restates SEC-T881-02 with the count of 6 pins (section 1.2, section 4.3).
- **SEC-T881-02 stays tracked-LOW, not fixed.** The user has **not** answered the choice (section 7). T891's recommendation is the standing position, not a decision.
- **Next-release checklist**: 36 numbers carried, none new; **item 17 is amended** (section 6.2). **Dates**: as v28 (section 6.3). **User actions**: v28's plus the SEC-T881-02 choice (section 7).

Arithmetic, from the v28 totals:

| Status | v28 | leaves | enters | v29 |
|---|---:|---|---|---:|
| fixed | 596 | | + 4 tracked-LOW (SEC-T885-04, SEC-T867-01, SEC-T867-02, TL-T761-11) | **600** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 104 | - 4 fixed | + 2 new (SEC-T891-01, -02) | **102** |
| **all** | **759** | | + 2 new ids | **761** |

Check: 600 + 46 + 12 + 1 + 102 = 761. Open or tracked: 102 + 1 = 103, the size of section 5.

### 1.1 Ids by v28 status and status now

| v28 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 104 | 4 | 0 | 0 | 0 | 100 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 596 | 596 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v28 ids** | **759** | **600** | **46** | **12** | **1** | **100** |
| new in v29 | 2 | 0 | 0 | 0 | 0 | 2 |
| **all v29 ids** | **761** | **600** | **46** | **12** | **1** | **102** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t891-batch-x-v1.md` § New findings: SEC-T891-01, -02 (SEC-T891-03 not counted) | 2 | 0 | 0 | 2 |
| **All new** | **2** | **0** | **0** | **2** |

**Ids minted in the range beyond T891's list: none.** A search of the 420 added lines in `d524f90e..54d240ed` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (11 distinct id tokens), set against the text of registers v1 to v28, finds as in no register exactly SEC-T891-01, -02, -03. The other id tokens are in earlier registers: SEC-T756-02, SEC-T860-01, SEC-T867-01, SEC-T867-02, SEC-T881-02, SEC-T885-04, TL-T761-11, TL-T876-04. The non-id matches are file-name tokens (`checkpoint-044`, `lock-v1`, `plan-188`, `register-v28`, `release-v10`, `release-v12`, `review-t860`, `review-t867`, `review-t881`, `review-t885`, `review-t891`, `task-T891`, `text-v1`, `v-v1`, `x-v1`). Most of the added lines are the review document, plan-188 and the two task briefs; the code changes are in section 2.2.

**Duplicates, counted once** (v26 § 1.2: "TL-T876-04 is SEC-T867-01 ... so it adds no id"; v17 § 1.2 and § 4.2 for the same rule): **SEC-T891-03** is SEC-T881-02 (T891 itself writes "restates SEC-T881-02 with the count"; its "What stays open" tracks the two together; plan-188 Outcome: "restates SEC-T881-02 with the count of 6 pins"). It gets the status of SEC-T881-02, **tracked-LOW**, and adds no id; the count of 6 goes into SEC-T881-02's row (section 2.2). **TL-T876-04** stays counted with SEC-T867-01 (section 2.2).

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): SEC-T860-01 (fixed or tracked as v28 records it; named in T891's source list only), SEC-T756-02 (tracked-LOW, left alone), SEC-T881-02 (tracked-LOW, section 2.2). **Ids named with a change** are those of sections 2 and 3. This register mints no id.

## 2. v28 ids re-checked

Every v28 `open`, `tracked-LOW` and `accepted` id (151) is covered: the changed ones have a row here, the rest are unchanged and carried. The v28 `fixed` and `obsolete` ids stay as v28 records them.

### 2.1 v28 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v28 `tracked-LOW` (104)

**Changed to fixed (4).** Status and basis are T891's per-id table (reviewer's words shortened); the fix commits are plan-188 § Outcome's (T890 `38646d9b`, `f581e819`, `be9659dc`; MR !716, develop `54d240ed`, pinned `0a6f5fc6`; pipelines 3095116496 and 3095116436; clean suite 2872 OK, skipped=25, per plan-189 § Facts).

| Id | v28 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T885-04 | X | **fixed** (T890, `38646d9b`) | `ca_job_pairing_problems()` loads `.gitlab-ci.yml` with `yaml.safe_load`, pins that the drift gate's image equals `ca-chain-check-python`'s, and that the ordered `openssl` tokens on the `apk add` lines of both jobs' `before_script` are equal; five mutation subTests; bypass review in T891 (anchors, `extends`, mapping images, moved `apk add`, extra groups all refused or equal). It proves equality only, not that the pinned digest is the intended one. **Coverage gap, a new id**: SEC-T891-01 |
| SEC-T867-01 | X | **fixed** (T890, `f581e819`) | `--min-age-days` goes through `min_age_days()` (floor 7, argparse exit 2 below it; builds on `non_negative_int`, `\d{1,4}`); no environment variable or config file reaches it; the checklist sentence says the option may only raise the default and its test requires the phrase. Residual, unchanged: a trivial `--allow-young` reason is accepted (gated by the checklist's merge-request record; not a regression). **TL-T876-04 is counted here** (v26 § 1.2) |
| SEC-T867-02 | X | **fixed** (T890, `f581e819`) | Age is `now_utc - published_utc >= timedelta(days=N)` on aware UTC instants (exact 7 days passes, 6 days 23:59:59 is young; offset stamp tested); a duplicate `--allow-young` (`(package, version)` key) raises `AuditError` (exit 2); the publication time prints in UTC. **TL-T876-04's date-print half is counted here** (v26 § 2.2). **Fail-open residue, a new id**: SEC-T891-02 (a future publication time is young, not an error) |
| TL-T761-11 | X | **fixed (documentation)** (T890, `be9659dc`) | The note in `CONTRIBUTING.md` and two comment lines above the fetch in `scripts/publish-release.py` state that with `FF_GIT_URLS_WITHOUT_TOKENS` on, the `release` fetch has no credential, works while the project is public and fails closed if not, and that the allowlist must not be widened. Behaviour unchanged (comment-only in code). The runner flag is documented, not observed live; A-21 was closed on the user's report (checklist) |

**Standing, not fixed (2).**

| Id | batch | status | What the range says |
|---|---|---|---|
| SEC-T881-02 | X | **tracked-LOW, not fixed, by design** (plan-188) | A fresh single-cut-off compile of `ci/requirements-ci.txt` (uv 0.11.9, scratchpad only) differs from the committed lock in **6** pins, the same package set, versions only: certifi 2026.10.19 to 2026.10.23, pycparser 3.11 to 3.12, pydantic 2.14.1 to 2.14.2, pydantic-core 2.50.1 to 2.50.2, sse-starlette 3.5.0 to 3.6.0, starlette 1.9.0 to 1.10.0. T890 reported 7; T890's own pin lists and T891 show 6, and the orchestrator's `diff` agrees (plan-188 Outcome; T891 addendum). **T891 recommends keeping the lock, with header lines 3-6 as the record** (the header says honestly that line 2 alone does not reproduce the lock: a documentation precision risk, not a vulnerability), and doing the one-cut-off regeneration at the next full regeneration with the checklist's 14-day review and an advisory audit; sooner only if an advisory names one of the six committed pins. **The user has not answered the choice** (section 7). SEC-T891-03 is counted with this id (section 1.2). T891's ages (21 to 29 days on 2026-11-20) are the reviewer's own arithmetic **(unverified)**; `pip-audit` was not run (it errored on the lock path) |
| SEC-T756-02 | X | **tracked-LOW, unchanged** | Left alone, as planned (plan-188 Outcome) |

**Unchanged (100 tracked-LOW; v28 and earlier stay the record of their text)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 4, X 2 (SEC-T756-02, SEC-T881-02), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 3. 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 2 + 11 + 2 + 5 + 3 = 100; with the 2 new (SEC-T891-01, -02, batch X), 102 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v28 and not recounted id by id; X was traced through v28 § 5, T891's per-id table and plan-188 Outcome.)

### 2.3 v28 `accepted` (46)

**Unchanged (46)**, with their v28 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01.

## 3. New ids

Grades are the reviewer's own (T891 § New findings). Owner devops-engineer (the surface of batch X; the orchestrator assigns).

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T891-01 | SECURITY:LOW (A04 / A05) | `tests/functional/test_ci_hash_pins.py` `ca_job_pairing_problems`: the pairing check covers only the image and the `openssl` constraint, and only in `before_script`. The `git~=` constraint and the other tags and variables of the two jobs are not paired. Structural changes fail closed, so this is a coverage gap, not a bypass | **tracked-LOW** | Compare the whole ordered `apk add` argument list of both jobs (after dropping the `run-allowlisted.py --` wrapper) | X |
| SEC-T891-02 | SECURITY:LOW (A08) | `scripts/audit-mcp-pins.py` `command_age`: a publication time in the future is treated as young and printed as a negative day count. Fails closed, but an `--allow-young` exception would let an anomalous timestamp through silently | **tracked-LOW** | Treat `published > now` as an `AuditError` (exit 2); a test for it | X |

**Not an id: SEC-T891-03** (`ci/requirements-ci.txt:2-6`; grade SECURITY:LOW, A08). It restates SEC-T881-02 "with the count" (T891's own words); counted with SEC-T881-02, status tracked-LOW (section 1.2, section 2.2).

**Why X for SEC-T891-01 and -02.** Both are T891's findings on the code T890 changed: the CI-pin tests (`test_ci_hash_pins.py`, the surface of SEC-T885-04, already in X) and `audit-mcp-pins.py age` (the surface of SEC-T867-01 and -02, already in X); same owner, same tests, same trigger (the next change to either file). Batch X had four ids leave (fixed) and takes these two.

## 4. Decisions since v28

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-20 | "X go"; plan approval "Approve (Recommended)" | Batch X round (plan-188) | T891 header; plan-188 |
| 2026-11-20 | "v29 go" | This register | plan-189 § User decision; T892 brief |

I did not verify the words beyond those records **(unverified)**. **The user has not decided SEC-T881-02** (section 7).

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T881-02 not fixed, "by design" | No lock or header change; the choice goes to the user | the orchestrator | plan-188 Outcome |
| Pin count 6, not 7 | The orchestrator's `diff` and T891 stand | the orchestrator; T891 | plan-188 Outcome; T891 addendum |
| TL-T876-04 | Counted with SEC-T867-01 (and the date print with SEC-T867-02), as v26; no id | **mine**, following v26 | section 2.2 |
| SEC-T891-03 | Counted with SEC-T881-02, tracked-LOW, no new id (v26 duplicate precedent) | **mine**, following v26 | section 1.2 |
| SEC-T891-01, -02 in batch X | Suggestion | **mine** | section 3, section 5 |
| Merges, pipelines, ledger | As plan-189 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: one, in the totals.** Ids, fixed set (SEC-T885-04, SEC-T867-01, SEC-T867-02, TL-T761-11), TL-T876-04 (with SEC-T867-01 and -02), SEC-T881-02 and SEC-T756-02 (stay tracked-LOW), SEC-T891-01 and -02 (new) all agree. **The difference is SEC-T891-03**: the expected delta's totals count it as a new tracked-LOW id (762; tracked-LOW 104 - 4 + 3 = 103; section 5 of 104; batch X of 5). v26 counts a restated finding once (TL-T876-04 with SEC-T867-01; QA-T818-01 and TL-T819-01 earlier), and T891 and plan-188 both describe SEC-T891-03 as restating SEC-T881-02, so I count it with SEC-T881-02. My totals: **761 ids; fixed 600; accepted 46; obsolete 12; open 1; tracked-LOW 102; section 5 of 103; batch X of 4**. If the orchestrator rules SEC-T891-03 a separate id, the totals are the expected ones (762 / 103 / 104 / X 5) and nothing else changes.
- **Pin count.** T890's 7 against 6: 6 (section 2.2).
- **Ledger.** Plan-189 § Facts: "0 active, 688 completed". Read here: `completed-tasks.md` holds 688 task rows and `active-tasks.md` one (T892, added by the plan-189 commit). No difference.
- **Budgets.** T890 about 106k tokens against 100k, T891 about 70k against 50k (plan-188 § Outcome); noted, not a debt id.

## 5. Open items by LOW batch

Carried from v28 § 5; X changes members and size (6 to 4); all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v28 § 5 (includes TD-T888-01) | 25 | as v28 | as v28 |
| K | Security runtime | as v28 § 5 | 8 | as v28 | as v28 |
| L | CWSO helper scripts in emage.code | as v28 § 5 | 5 | as v28 | as v28 |
| M | CWSO repository | as v28 § 5 | 12 | as v28 | as v28 |
| N | Release tooling, second round | as v28 § 5 | 10 | as v28 | as v28 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v28 | as v28 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v28 | each release's preparation |
| R | Release-gate text, second round | as v28 § 5 | 7 | as v28 | as v28 |
| V | Release gate, third round | SEC-T888-01, SEC-T888-02, SEC-T888-03, SEC-T888-04 | 4 | devops-engineer | as v28 |
| **X** | CI images, the CA control, the CI locks and the pin-age check | SEC-T756-02, SEC-T881-02 (with SEC-T891-03); **new:** SEC-T891-01, SEC-T891-02. **Left (fixed):** SEC-T885-04, SEC-T867-01 (with TL-T876-04), SEC-T867-02, TL-T761-11 | 4 | devops-engineer | SEC-T881-02 at the next full regeneration of `ci/requirements-ci.txt` (item 17), sooner only if an advisory names one of the six committed pins; SEC-T891-01 with the next change to `test_ci_hash_pins.py`; SEC-T891-02 with the next change to `audit-mcp-pins.py age` or at the next `npx` pin bump; SEC-T756-02 as v28 |
| Y | Shipped text and records | as v28 § 5 | 11 | as v28 | as v28 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v28 | as v28 |
| U | Live checks and user | as v28 § 5 | 6 | as v28 | as v28 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v28 | as v28 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 4 + 11 + 2 + 6 + 3 = **103** = 102 tracked-LOW + 1 open (K-20). Against v28's 105: X - 2 (6 to 4: four leave, two enter). **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v28: X only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v28 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range; T891 accepted none.

### 6.2 Next release checklist (the release after v12.0.0)

v28 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 52 with 13 points). Change:

- **Item 17** (the next full regeneration of `ci/requirements-ci.txt`) now also says: the one-cut-off regeneration moves the **six pins** named in section 2.2 (certifi, pycparser, pydantic, pydantic-core, sse-starlette, starlette); it needs the checklist's **14-day review** and an **advisory audit** of the result before adoption; the **header fix (SEC-T881-02) waits for it**, with header lines 3-6 as the record until then; regenerate sooner only if an advisory names one of the six committed pins. If the user chooses regeneration now (section 7), item 17 is that regeneration.
- **Item 8** stays open: no tag pipeline ran in the range. Items 43, 44, 46 to 52: as v28.

Count: 36 numbers carried, 0 new; item 52 has 13 points.

### 6.3 Dates

Unchanged from v28 § 6.3 (all still ahead on 2026-11-20): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml:25`; the range does not change `.gitlab-ci.yml`, T891 and plan-188: `.gitlab-ci.yml` and `ci/` untouched), 2027-03-19 the last passing day.

## 7. User actions

v28 § 7 stands, unchanged:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).

**New, open: the SEC-T881-02 choice.** The user has not answered. Options:
1. **Keep the lock and header lines 3-6 as the record** (T891's recommendation, **the standing position**): no change now; the one-cut-off regeneration at the next full regeneration (item 17), with the 14-day review and the advisory audit; sooner only if an advisory names one of the six committed pins.
2. **Regenerate now** with the 14-day review: moves the six pins (certifi, pycparser, pydantic, pydantic-core, sse-starlette, starlette) and needs the review, provenance where available, an advisory audit with hashes and a diff read.

## 8. Method, limits and validation

- **Carried statuses**: v28's rows and lists, plus the sources in Based on. Plan-189 § Facts and plan-188 § Outcome are the only sources for the merges (!715, !716), the pinned sha `0a6f5fc6`, the pipelines (3095116496, 3095116436) and the clean suite (2872 OK, skipped=25). `docs/tasks/completed-tasks.md` holds 688 task rows and `active-tasks.md` one (T892) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 420 lines added in `d524f90e..54d240ed` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v28; the result is section 1.2.
- **Counting**: 3 ids named new by T891, 2 counted (SEC-T891-03 with SEC-T881-02); TL-T876-04 stays with SEC-T867-01; 4 status changes into `fixed` from tracked-LOW. Section 5 expands to 103 ids; the sizes of unchanged batches are v28's, not recounted id by id; X was traced through T891 and plan-188.
- **Still unverified**:
  - Carried from v28 § 8.
  - T890's code beyond the added lines and T891's reading of it (T891 did not re-run the suite or `pip-audit`; the orchestrator re-derived the pin count with `diff`).
  - The reviewer's ages of the six fresh pins (21 to 29 days).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The `FF_GIT_URLS_WITHOUT_TOKENS` behaviour (documented, not observed live).
  - The batch membership behind "as v28 § 5", and the status of SEC-T860-01.
- **Not run here**: the suite, the pipelines, `audit-mcp-pins.py`, `uv`, `pip-audit`.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v28.md`; `tracked-debt-register-v26.md` (§ 1.2, § 2.2, § 4); registers v1 to v28 (the token scan, by grep); `plan-189-tracked-debt-register-v29.md`; `plan-188-batch-x-round.md` (Outcome); `security-review-t891-batch-x-v1.md` (all sections, addendum); `checkpoint-044-release-v12.0.0.md` (by reference);
  - `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md` (row counts);
  - `git diff --shortstat`, `--stat` and `-U0` of `d524f90e..54d240ed`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
