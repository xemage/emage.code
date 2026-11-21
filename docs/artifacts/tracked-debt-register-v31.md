# Artifact: tracked-debt-register-v31.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v30.md` (764 ids; v30 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/artifacts/tracked-debt-register-v29.md` (§ 5 and § 2.3: the batch rows and the accepted list that v30 carries by reference); `docs/artifacts/tracked-debt-register-v26.md`, `-v24.md` and `-v15.md` (the precedents for counting an id minted before merge); `docs/plans/plan-193-tracked-debt-register-v31.md` (§ User decision, § Facts since v30, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T898.md` (the user's "v31 go"); `docs/plans/plan-192-batch-x-small-round.md` (Outcome, Addendum 1); `docs/artifacts/security-review-t897-batch-x-v1.md` (per-id table, new findings, the orchestrator's addendum); `docs/artifacts/security-review-t891-batch-x-v1.md` (by reference, text of SEC-T891-01 and -02). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T898 (plan-193; the user's answer of 2026-11-21, verbatim: "v31 go"). **Date**: 2026-11-21.
- **Tree read**: branch `agent/tech-lead/T898` (develop `b04ec271` plus the plan-193 commit `2595ea80`). The range for "lines added since v30" is `a0c375e6..b04ec271` (plan-193 § Facts): 12 files, 631 lines added and 8 removed (read here: `git diff --shortstat`). Code in four files: `scripts/audit-mcp-pins.py`, `docs/wiki/mcp-pin-bump-checklist.md`, `tests/functional/test_audit_mcp_pins_hardening.py`, `tests/functional/test_ci_hash_pins.py` (the stat shows 3 + 27 + 31 lines changed in the three scripts and tests and 1 in the checklist). Neither `tests/golden/` nor `.vscode/` has a diff in the range. The plan-193 commit is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v29 only by grep (the token scan). The code was not read beyond what T897 reports. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **X** drops SEC-T891-01 and SEC-T891-02 (fixed) and gains SEC-T897-01 (new), so 4 stays at **3** (4 - 2 + 1). No other batch changes; no new letter, no letter ends.

## 1. Summary

v31 holds **765 ids**: the 764 of v30 and **1 new** (SEC-T897-01, found by T897 in the review of MR !720). After v31: **606 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **100 tracked-LOW**.

- **Open above LOW: nothing.** T897: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 1 LOW. The one open id is K-20 (live checks, the user; no grade). TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v30, from tracked-LOW (2)**: SEC-T891-01 and SEC-T891-02 (batch X; section 2.2).
- **New, tracked-LOW (1)**: SEC-T897-01 (batch X; section 3). Its wording gap (the checklist does not say `--allow-young` cannot override the future-time refusal) is tracked with it, not as an id of its own.
- **SEC-T881-02 stays tracked-LOW, now with the user's decision on record**: "Keep the lock (Recommended)", 2026-11-21 (plan-192 Addendum 1). It is no longer an open user action (sections 2.2, 4.1, 7).
- **SEC-T756-02 stays tracked-LOW**, untouched.
- **Next-release checklist**: 36 numbers carried, none new; the wording gap goes with SEC-T897-01 (section 6.2). **Dates**: as v30 (section 6.3). **User actions**: v30's, with the SEC-T881-02 choice recorded as decided (section 7).

Arithmetic, from the v30 totals:

| Status | v30 | leaves | enters | v31 |
|---|---:|---|---|---:|
| fixed | 604 | | + 2 tracked-LOW (SEC-T891-01, SEC-T891-02) | **606** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 101 | - 2 fixed (SEC-T891-01, SEC-T891-02) | + 1 new (SEC-T897-01) | **100** |
| **all** | **764** | | + 1 new id | **765** |

Check: 606 + 46 + 12 + 1 + 100 = 765. Open or tracked: 100 + 1 = 101, the size of section 5.

### 1.1 Ids by v30 status and status now

| v30 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 101 | 2 | 0 | 0 | 0 | 99 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 604 | 604 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v30 ids** | **764** | **606** | **46** | **12** | **1** | **99** |
| new in v31 | 1 | 0 | 0 | 0 | 0 | 1 |
| **all v31 ids** | **765** | **606** | **46** | **12** | **1** | **100** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t897-batch-x-v1.md` § New findings: SEC-T897-01 | 1 | 0 | 0 | 1 |
| **All new** | **1** | **0** | **0** | **1** |

**Ids minted in the range beyond T897's list: none.** A search of the 631 lines added in `a0c375e6..b04ec271` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (45 distinct tokens; the register v30 itself is among the added files), set against the text of registers v1 to v30, finds as in no register exactly **SEC-T897-01**. The other 44 id tokens are in earlier registers, among them SEC-T891-01, -02, SEC-T881-02, SEC-T756-02, SEC-T885-04, SEC-T888-01 to -04, SEC-T894-01 to -03, ADR-011, ADR-015, ADR-016. The non-id matches are file-name tokens (`plan-189`, `plan-190`, `plan-191`, `plan-192`, `task-T894`, `task-T895`, `task-T897`, `engineer-T893`, `checkpoint-044-release-v12`). Most of the added lines are register v30, plan-191, plan-192, the review document and the task briefs; the code changes are in section 2.2.

**Duplicates: none.** SEC-T897-01 restates no earlier id: SEC-T891-01 was the gap "only openssl is compared", which T896 closed; SEC-T897-01 is a different residue (the lines the selector does not recognise). It is counted as an id of its own, as T897 names it.

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): SEC-T885-04, SEC-T888-01 to -04, SEC-T894-01 to -03 and the rest of the 44 (named in the review text or in register v30 only). **Ids named with a change** are those of sections 2 and 3.

## 2. v30 ids re-checked

Every v30 `open`, `tracked-LOW` and `accepted` id (148) is covered: the changed ones have a row here, the rest are unchanged and carried. The v30 `fixed` and `obsolete` ids stay as v30 records them.

### 2.1 v30 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v30 `tracked-LOW` (101)

**Changed to fixed (2).** Status and basis are T897's per-id table; fix commits `44da9174` (SEC-T891-01) and `887b6bcc` (SEC-T891-02) (plan-192 Outcome; MR !720, develop `b04ec271`, pinned `da98b53f`; pipelines 3096950812 and 3096950796; clean suite 2876 OK, skipped=25, per plan-193 § Facts).

| Id | v30 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T891-01 | X | **fixed** (T896, `44da9174`; reviewed by T897 at `887b6bcc`) | `ca_job_pairing_problems` in `tests/functional/test_ci_hash_pins.py` now compares the whole ordered `apk add` argument list of `main-develop-drift-gate` and `ca-chain-check-python` (wrapper dropped, `before_script` then `script`); both lists are identical today (`apk add --no-cache 'openssl~=3.5' 'git~=2.54'`). Eight mutation cases are added (a changed `git~=` constraint, an added package, a dropped package, a reordered list, once per job); the old openssl-only case stays; the orchestrator read the changed test lines and found no assertion dropped (plan-192 Outcome). T897 reasoned, did not run. **Residue** in matching form: SEC-T897-01 (section 3) |
| SEC-T891-02 | X | **fixed** (T896, `887b6bcc`) | `command_age` in `scripts/audit-mcp-pins.py` raises `AuditError` for a publication time later than `now`, before the age line and before `--allow-young` is consulted, so an exception cannot cover it. A time exactly at `now` stays age 0, young, as before (`>`, not `>=`; the test pins it). The orchestrator confirmed `AuditError` ends in exit 2 (`audit-mcp-pins.py:613-615`; the reviewer could not). The checklist § 1 sentence matches the code; the wording gap is tracked with SEC-T897-01 |

**Unchanged, with the decision on record (1, stays tracked-LOW).**

| Id | batch | status | What the range says |
|---|---|---|---|
| SEC-T881-02 | X | **tracked-LOW, unchanged; decided by the user** | On 2026-11-21 the user answered "Keep the lock (Recommended)" (plan-192 Addendum 1). That option read: "The security reviewer's advice: no lock change; header lines 3-6 stay the record; the one-cut-off rebuild waits for the next full regeneration with the 14-day review, or an advisory on one of the six pins." The lock and header lines 3-6 are untouched in the range. The six pins a fresh rebuild would move are certifi, pycparser, pydantic, pydantic-core, sse-starlette, starlette (v30 § 2.2). The id stays tracked-LOW as the remainder (the header fix waits for item 17 of section 6.2). The decision is the user's |

**Unchanged, tracked-LOW (SEC-T756-02 named here, 98 in all other batches; v30 and earlier stay the record of their text).**

| Id | batch | status | What the range says |
|---|---|---|---|
| SEC-T756-02 | X | **tracked-LOW, unchanged** | Untouched by plan-192 (its remaining action is a rule for later image bumps) |

**Unchanged (99 tracked-LOW in all, plus the new SEC-T897-01 makes 100)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 3 (SEC-T888-01, SEC-T888-02 (b), SEC-T888-03), X 2 here (SEC-T756-02, SEC-T881-02), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 3. 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 2 + 11 + 2 + 5 + 3 = 99 = the 101 of v30 less SEC-T891-01 and -02. (The sizes of unchanged batches are carried from v30 and not recounted id by id; X was traced through v30 § 5, T897 and plan-192 Outcome.)

### 2.3 v30 `accepted` (46)

**Unchanged (46)**, with their v30 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01 other than as carried text.

## 3. New ids

The grade is the reviewer's own (T897 § New findings). Owner devops-engineer (the surface of batch X).

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T897-01 | SECURITY:LOW (A08) | The pairing check in `tests/functional/test_ci_hash_pins.py` (`ca_job_pairing_problems` / `apk_adds`, about lines 1477-1480) selects only lines whose words start with exactly `apk add` (`"apk add" in line and words[:2] == ["apk","add"]`). An extra install written as `apk --no-cache add pkg`, `apk  add` (two spaces), `env X=1 apk add pkg`, `sh -c 'apk add pkg'` (also under the `run-allowlisted` wrapper, which only the wrapper strip handles), `command apk add` or after a `;` or `&&`, in one job only, is silently ignored while the standard `apk add` line stays equal. **No current exposure**: nothing uses those forms and both lists are equal. If both jobs use such a form for the same install, both lists are empty and the check fires (fail-closed). Residues of the same kind, graded LOW by T897: a package given as a variable (`$PKGS`) is compared as a literal word; the position of the `apk add` against the other lines is not compared, and a line moved between `before_script` and `script` still passes. **Wording gap, tracked with it**: `docs/wiki/mcp-pin-bump-checklist.md` § 1 does not say that `--allow-young` cannot override the future-time refusal (SEC-T891-02); the code and the test do (T897 question 3; its addendum tracks it with this id rather than editing it) | **tracked-LOW** (new) | Select every line whose unwrapped words, or the `sh -c` payload re-split with shlex, contain the token `apk`, and treat any such line that is not exactly `apk add ...` as a problem (fail closed), or compare all lines after the first `apk` token. Add a mutation case each for `apk --no-cache add x` and `sh -c 'apk add x'` in one job. Add one sentence to checklist § 1 that `--allow-young` does not override the future-time refusal. Reasoned by T897, not run | X |

**Why batch X.** It is the surface of the CA control and the pin-age check (SEC-T891-01 and -02 sat there). T897 names the "batch X remainder". Trigger: the next change to `test_ci_hash_pins.py` (as SEC-T891-01 had it); the wording sentence with the next edit of the checklist.

## 4. Decisions since v30

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-21 | "X go"; plan approval "Approve (Recommended)" | Batch X small round (plan-192): SEC-T891-01 and -02 in T896, then the review T897; no pin, lock or CI file change | plan-192 § User decision, Addendum 1 |
| 2026-11-21 | "Keep the lock (Recommended)" | **SEC-T881-02 decided**: no lock change; header lines 3-6 stay the record; the one-cut-off rebuild waits for the next full regeneration with the 14-day review, or an advisory on one of the six pins | plan-192 Addendum 1; plan-193 § Facts |
| 2026-11-21 | "v31 go" | This register | plan-193 § User decision; T898 brief |

I did not verify the words beyond those records **(unverified)**. Plan-192's own "Approved by the user" checkbox is left unticked in the plan; the answers are in its Addendum 1.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| Exit 2 for a future publication time | Confirmed from `audit-mcp-pins.py:613-615` (the reviewer could not) | the orchestrator | T897 addendum; plan-192 Outcome |
| Wording gap tracked with SEC-T897-01 | No id of its own; no edit to the checklist in plan-192 | the orchestrator | T897 addendum; plan-192 Outcome |
| SEC-T897-01 counted as 1 new, tracked-LOW | Not a duplicate of SEC-T891-01 (a residue of a different shape) | **mine** | section 1.2, section 3 |
| SEC-T881-02 recorded as decided, still tracked-LOW | The decision is "keep", the remainder stays | **mine**, following plan-193 | section 2.2, section 7 |
| Wording gap not given a checklist number | No new number in section 6.2 (it is an edit to the pin-bump checklist, not a release-checklist item) | **mine** | section 6.2 |
| Merges, pipelines, ledger | As plan-193 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none.** Ids (765), fixed (604 + 2 = 606), accepted 46, obsolete 12, open 1, tracked-LOW (101 - 2 + 1 = 100), section 5 of 101 and batch X of 3 all agree, and the check 606 + 46 + 12 + 1 + 100 = 765 holds. The changed set (SEC-T891-01 and -02 fixed; SEC-T897-01 new; SEC-T881-02 and SEC-T756-02 unchanged) agrees.
- **Ledger.** Plan-193 § Facts: "0 active, 694 completed". Read here: `completed-tasks.md` holds 694 task rows and `active-tasks.md` one (T898, added by the plan-193 commit). No difference.
- **Budgets.** T896 about 73k tokens against 50k, T897 about 67k against 30k (plan-192 § Outcome); noted, not a debt id.

## 5. Open items by LOW batch

Carried from v30 § 5; X changes members (SEC-T891-01 and -02 leave, SEC-T897-01 joins; size 4 to 3: 4 - 2 + 1 = 3); all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---|---|---|
| I | Installer and generator | as v30 § 5 (includes TD-T888-01) | 25 | as v30 | as v30 |
| K | Security runtime | as v30 § 5 | 8 | as v30 | as v30 |
| L | CWSO helper scripts in emage.code | as v30 § 5 | 5 | as v30 | as v30 |
| M | CWSO repository | as v30 § 5 | 12 | as v30 | as v30 |
| N | Release tooling, second round | as v30 § 5 | 10 | as v30 | as v30 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v30 | as v30 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v30 | each release's preparation |
| R | Release-gate text, second round | as v30 § 5 | 7 | as v30 | as v30 |
| V | Release gate, third round | SEC-T888-01, SEC-T888-02 (part (b) only), SEC-T888-03 | 3 | devops-engineer | as v30 |
| **X** | CI images, the CA control, the CI locks and the pin-age check | SEC-T756-02, SEC-T881-02 (decided "Keep the lock", 2026-11-21), **new:** SEC-T897-01. **Left (fixed):** SEC-T891-01, SEC-T891-02 | 3 | devops-engineer | SEC-T881-02 at the next full regeneration of `ci/requirements-ci.txt` (item 17), sooner only if an advisory names one of the six committed pins; SEC-T897-01 with the next change to `test_ci_hash_pins.py` (and the checklist sentence with the next edit of `mcp-pin-bump-checklist.md`); SEC-T756-02 as v30 |
| Y | Shipped text and records | as v30 § 5 | 11 | as v30 | as v30 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v30 | as v30 |
| U | Live checks and user | as v30 § 5 | 6 | as v30 | as v30 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v30 | as v30 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 11 + 2 + 6 + 3 = **101** = 100 tracked-LOW + 1 open (K-20). Against v30's 102: X - 1 (4 to 3). **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v30: X only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v30 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range; T897 accepted none. The user's "Keep the lock" for SEC-T881-02 is a decision on a LOW id, not an acceptance of a risk under ADR-011.

### 6.2 Next release checklist (the release after v12.0.0)

v30 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29; item 52 with 14 points). Change:

- **Item 17 reads as v29 amended it, now on the user's decision.** The one-cut-off regeneration of `ci/requirements-ci.txt` moves the six pins (certifi, pycparser, pydantic, pydantic-core, sse-starlette, starlette), needs the checklist's 14-day review and an advisory audit of the result, and the header fix (SEC-T881-02) waits for it, with header lines 3-6 as the record until then. The user chose "Keep the lock" on 2026-11-21; the "regenerate now" option of v30 § 7 is closed.
- **Pin-bump checklist § 1 wording** (not a release-checklist number): add that `--allow-young` cannot override the refusal of a publication time later than now (SEC-T891-02; tracked with SEC-T897-01). Do it with the next edit of `docs/wiki/mcp-pin-bump-checklist.md`.
- **Item 8** stays open: no tag pipeline ran in the range. Items 43, 44, 46 to 52: as v30; points 1 to 14 of item 52: as v30.

Count: 36 numbers carried, 0 new; item 52 has 14 points.

### 6.3 Dates

Unchanged from v30 § 6.3 (all still ahead on 2026-11-21 except the first two, which are at hand): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml:25`; the range does not change `.gitlab-ci.yml`, plan-192 and T897), 2027-03-19 the last passing day.

## 7. User actions

v30 § 7 stands, with one change:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).

**Decided, no longer an open action: the SEC-T881-02 choice.** The user answered "Keep the lock (Recommended)" on 2026-11-21 (plan-192 Addendum 1): no lock change, header lines 3-6 stay the record; the one-cut-off regeneration waits for the next full regeneration (item 17) with the 14-day review and the advisory audit, or for an advisory that names one of the six committed pins. Nothing remains for the user on it.

## 8. Method, limits and validation

- **Carried statuses**: v30's rows and lists, plus the sources in Based on. Plan-193 § Facts and plan-192 § Outcome are the only sources for the merges (!719, !720), the pinned sha `da98b53f`, the pipelines (3096950812, 3096950796) and the clean suite (2876 OK, skipped=25). `docs/tasks/completed-tasks.md` holds 694 task rows and `active-tasks.md` one (T898) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 631 lines added in `a0c375e6..b04ec271` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v30; the result is section 1.2.
- **Counting**: 1 id named new by T897, 1 counted (not a duplicate), tracked-LOW; 2 status changes into `fixed` from tracked-LOW (SEC-T891-01, -02). Section 5 expands to 101 ids; the sizes of unchanged batches are v30's, not recounted id by id; X was traced through v30 § 5, T897 and plan-192.
- **Still unverified**:
  - Carried from v30 § 8.
  - T896's code beyond the added lines and T897's reading of it (T897 had no shell; its review is reasoned from the code; the agent's own run results were not re-run by the reviewer). The orchestrator read the changed test lines and checked the exit code.
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v30 § 5".
- **Not run here**: the suite, the pipelines, the mutations.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v30.md`; `tracked-debt-register-v29.md` (§ 5, § 2.3); `tracked-debt-register-v26.md`, `-v24.md`, `-v15.md` (precedents); registers v1 to v30 (the token scan, by grep); `plan-193-tracked-debt-register-v31.md`; `plan-192-batch-x-small-round.md` (Outcome, Addendum 1); `security-review-t897-batch-x-v1.md` (all sections, addendum);
  - `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md` (row counts);
  - `git diff --shortstat`, `--stat` and `-U0` of `a0c375e6..b04ec271`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
