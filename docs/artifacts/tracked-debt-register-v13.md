# Artifact: tracked-debt-register-v13.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v12.md` (672 ids; v12 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-149-tracked-debt-register-v13.md` (§ Facts since v12, § Task Decomposition) and `docs/tasks/task-T787.md` (the user's "v13 go"); `docs/plans/plan-148-node-image-bump.md` (§ Facts, § Progress, § Outcome); `docs/artifacts/security-review-t784-node-advisory-v1.md`; `docs/artifacts/security-review-t786-node-bump-v1.md`; `docs/artifacts/security-review-t768-ca-control-v1.md` (the SEC-T756-02 re-grade and its conditions, SEC-T768-03, SEC-T768-06); `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md`; the ledger rows T784 to T786 in `docs/tasks/completed-tasks.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (only the user accepts a MEDIUM, for one release), as v12 cites it; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T787 (plan-149; the user's answer of 2026-11-12, verbatim: "v13 go"). **Date**: 2026-11-12.
- **Tree read**: branch `agent/tech-lead/T787` at `dcc948d2` (develop `fa33912c` plus the plan commit). The range for "lines added since v12" is `b45f400e..fa33912c`: 4 commits, 10 files, 596 lines added and 8 removed. Outside the new review, plan and brief files, the changed files are `.gitlab-ci.yml` (15 lines), `docs/wiki/mcp-pin-bump-checklist.md` (one line, line 30), `tests/functional/test_pin_bump_checklist.py` (one line, line 97) and `docs/tasks/completed-tasks.md` (rows T784 to T786). `tests/functional/test_ci_hash_pins.py`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/install.sh` and the release scripts show no diff in the range, so v12's citations into them stand. The CWSO repository was not read: every CWSO status carries over from v12.
- **Review mode**: read-only. "Unchanged" means no task, review, plan outcome or ledger row since v12 names the id with a change of status, checked by searching the lines added in `b45f400e..fa33912c`, outside `tests/golden/`, for every id that v12 holds (section 8). A status taken from a review is the latest source's. "Read here" means a grep or line read on `dcc948d2`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository. Registers v1 to v11 were not re-read, except one grep of v11 § 6.2 for `.gitlab-ci.yml` citations (section 6.2). No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v12.
- **Batch letters**: all v12 letters keep their scope. No letter is new or ends.

## 1. Summary

v13 holds **675 ids**: the 672 of v12 and **3 new**. After v13: **500 fixed**, **49 accepted**, **9 obsolete**, **4 open**, **113 tracked-LOW**.

- **Open above LOW: no `SECURITY:*` grade above LOW is open.** The three open ids QA-T760-01, -02 and -03 still carry QA's `Medium` (QA's own scale, batch Z, "next release"), as in v12. The fourth open id is K-20 (live checks, user). TD-T774-01 still has no reviewer's grade. The accepted MEDIUMs (SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07) are accepted, not open, and are unchanged.
- **Plan-148, the CI Node image bump, closed three ids.** SEC-T756-05 and SEC-T756-06 are fixed (T785, confirmed by T786 § 2). **SEC-T768-06 is fixed too, by my reading**: T785's edit of `docs/wiki/mcp-pin-bump-checklist.md:30` replaced the stale Python digest that the finding names. No review names this closure (section 2.2).
- **Three new tracked-LOW ids**: SEC-T784-01 (user-side Node for the `npx` entries, batch Q), SEC-T786-01 (Alpine's `nodejs` 24.22.1 in `unit-tests`, batch X) and SEC-T786-02 (the pin checklist tells the reader to run the image, batch Y).
- **T786's condition.** Its CONDITIONAL_PASS is met when this register carries SEC-T784-01, SEC-T786-01, SEC-T786-02 and SEC-T768-03 as tracked debt. All four are tracked-LOW here (sections 2.2 and 3).
- **SEC-T756-02 stays tracked-LOW** in batch X. The bump satisfied the "before any earlier image bump" clause of its plan, and A-21 remains its condition (section 2.2).
- **The CI image review date moved.** `ci_images_reviewed_on: 2026-11-11` (`.gitlab-ci.yml:21`, read here). The last passing day is **2027-03-11**, and the test fails from **2027-03-12** (section 6.3).
- **Due before v11.0.0** (section 6.2): as v12, less the Node bump, which is done. New: SEC-T786-01's check at release preparation (item 37) and SEC-T784-01's Node minimums (item 38).
- **Open for the user**: as v12. A-20, A-21 and A-22; the route of SEC-T735-06 and -07; the SEC-T762-04 questions; any batch before the next tag.

Arithmetic, from the v12 totals:

| Status | v12 | leaves | enters | v13 |
|---|---:|---|---|---:|
| fixed | 497 | | + 3 (SEC-T756-05, SEC-T756-06, SEC-T768-06) | **500** |
| accepted | 49 | | | **49** |
| obsolete | 9 | | | **9** |
| open | 4 | | | **4** |
| tracked-LOW | 113 | - 3 fixed | + 3 new | **113** |
| **all** | **672** | | + 3 new ids | **675** |

Check: 500 + 49 + 9 + 4 + 113 = 675. Open or tracked: 113 + 4 = 117, the size of section 5.

**If the orchestrator keeps SEC-T768-06 tracked** until a reviewer confirms it, the totals become 499 fixed and 114 tracked-LOW, and batch X holds 11 (section 5 total 118).

### 1.1 Ids by v12 status and status now

| v12 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 4 | 0 | 0 | 0 | 4 | 0 |
| tracked-LOW | 113 | 3 | 0 | 0 | 0 | 110 |
| accepted | 49 | 0 | 49 | 0 | 0 | 0 |
| fixed | 497 | 497 | 0 | 0 | 0 | 0 |
| obsolete | 9 | 0 | 0 | 9 | 0 | 0 |
| **all v12 ids** | **672** | **500** | **49** | **9** | **4** | **110** |
| new in v13 | 3 | 0 | 0 | 0 | 0 | 3 |
| **all v13 ids** | **675** | **500** | **49** | **9** | **4** | **113** |

### 1.2 New ids by source and final status

| Source | new | fixed | accepted | obsolete | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| `security-review-t784-node-advisory-v1.md` § 6: SEC-T784-01 | 1 | 0 | 0 | 0 | 0 | 1 |
| `security-review-t786-node-bump-v1.md` § 3: SEC-T786-01, SEC-T786-02 | 2 | 0 | 0 | 0 | 0 | 2 |
| **All new** | **3** | **0** | **0** | **0** | **0** | **3** |

**Other ids in the added lines.** A search of the lines added in `b45f400e..fa33912c`, outside `tests/golden/`, for any `<PREFIX>-T<nnn>-<n>` id finds SEC-T756-02, -05, -06, SEC-T768-03, -06, SEC-T784-01, SEC-T786-01, -02, and the blocker records **BLK-T784-01** and **BLK-T784-02**. Nothing else is minted. I treat both blocker records as blockers, not debt ids, as v12 did with BLK-T756-01 to -04, BLK-T762-01, -02 and BLK-T768-01. They get no row and no count:
- **BLK-T784-01** (`grep_content` failed for T784; `technical`, `minor`) is answered. T786 § Blockers: `grep_content` "worked in this review with `root_dir "."` on the main checkout, so the T784 failure was a scoping limit". Plan-148 § Progress gives the reviewer's separate worktree as the probable cause **(unverified)**. What T784 could not grep was covered by the orchestrator's greps (plan-148 § Progress) and the orchestrator's old-digest sweep for T786.
- **BLK-T784-02** (no official image with 24.22.3; `external`, `minor`) ended when the registry watch saw `24-alpine` at `116b800c…` on 2026-11-11T23:42Z (plan-148 § Outcome).

This register mints no id.

## 2. v12 ids re-checked

Every v12 `open`, `tracked-LOW` and `accepted` id (166) has a row or a list entry here: 4 + 113 + 49. The v12 `fixed` and `obsolete` ids stay as v12 records them.

### 2.1 v12 `open` (4)

**Unchanged**: K-20 (batch U, A-7); QA-T760-01, QA-T760-02, QA-T760-03 (QA Medium, batch Z). No plan-148 source names them.

### 2.2 v12 `tracked-LOW` (113)

**Changed (3).**

| Id | v12 | now | Evidence |
|---|---|---|---|
| SEC-T756-05 | tracked-LOW, batch X (provisional LOW) | **fixed** | T784 § 3 made it final LOW, closing "when T785 lands the 24.22.3 image and T786 confirms it". T786 § 2: "Fixed: closes". `ca-chain-check-node`, `verify-knowledge-drift` and `sync-no-diff` run Node 24.22.3 (T786 obligations 1, 2, 6). The `unit-tests` residual moves to SEC-T786-01. Ledger row T786. The pin `node:24-alpine@sha256:116b800c…` is at `.gitlab-ci.yml:43` (read here) |
| SEC-T756-06 | tracked-LOW, batch X (provisional LOW) | **fixed** | T784 § 3: closes "when T786 confirms the new Node base is 3.24.4 or later". T786 § 2: "Fixed: closes" (obligation 3: minirootfs 3.24.4; apk-tools 3.0.9-r0 from T785's layer read). Ledger row T786. The record says Alpine 3.24.4 at `.gitlab-ci.yml:17` (read here) |
| SEC-T768-06 | tracked-LOW, batch X | **fixed (my reading; no review names the closure)** | The finding: `mcp-pin-bump-checklist.md:30` "still names `python:3.12-alpine sha256:92abd2ba...` (2026-10-22)"; remediation "Update digest, date and version line" (T768 findings table). T785's commit `4b7d5c5d` rewrote that line. It now gives `python:3.12-alpine` `sha256:e064671c...` read 2026-11-06 (T765; Alpine 3.24.4, Python 3.12.16), which matches the pin at `.gitlab-ci.yml:54` and the record at `:16` (read here). `92abd2ba` now occurs only in immutable artifacts (grep, read here). T786 read the line ("a record, not a pin", obligation 7) but does not rule on SEC-T768-06. The same line still carries SEC-T786-02's "run the image" text |

**Named since v12 with no change of status (2 rows).**

| Id | What the sources say | Status |
|---|---|---|
| SEC-T768-03 | T786 § 2: "Open, tracked-LOW (unchanged); its trigger did not fire". At `116b800c…` the image is still bundle-only, before and after `apk add`: `--ca-release` lists only `ca-certificates-bundle 20261020-r0`, and the shipped and live `sha256sum` are equal (obligation 5). "Nothing yet guards a future index state." Remediation unchanged: a guarded `--capath` run when hashed entries exist. The `--cafile`-only runs are now `.gitlab-ci.yml:193-194` (read here; T768 cited `:184-189`) | tracked-LOW, batch X. **Part of T786's condition** |
| SEC-T756-02 | See the ruling below | tracked-LOW, batch X; not re-graded |

**SEC-T756-02: what the image bump settles and what it leaves (my ruling; no re-grade).**
- **The sources.** The plan shown to the user at MEDIUM: "Fix: add the check as a step at every image bump, and settle the open points. deadline=2027-02-19, and before any earlier image bump" (`docs/releases/v10.0.0.md:300`; `security-review-t756-accepted-mediums-v1.md:197`). T768 re-graded it LOW, effective when MR !658 merged with both CA jobs passing. Its conditions were "Any later image bump must also pass both jobs" (T768 § Conditions, line 85), and A-21 for keeping LOW (T768 § Re-grade). Its residual LOW: "unlogged cross-signs, no live connection test, non-amd64 images not read, helper image pinned by tag only".
- **What the bump settles.**
  - **The clause "before any earlier image bump" is met.** The check was in place as a blocking MR step (T766, MR !658, pipeline 3040148068; ledger T766, T768) before the first image bump since then, T785.
  - **T768's condition held at that bump.** Both CA-chain jobs passed on the new digest, with the outputs T768 requires (T786 obligation 5). Those outputs: `0 of 19; controls validating: 1 of 1`, `RESULT: PASS`, `--ca-release` PASS before and after `apk add`, and equal shipped and live hashes. Pipeline 3056919066 on `50520592`; the merged state's pipeline 3056985425 is green (plan-149 § Facts).
  - **"Non-amd64 images not read" is answered for the runner that ran.** Its jobs log an x86-64 CPU, so the amd64 manifest is the one that runs (T786 obligation 1: jobs 17951936902, -899 and -903; plan-149 § Facts says every job of 3056919066). The arm64/v8 and s390x manifests stay unread and are not used by that runner (T786 § 6 item 4).
- **What it leaves.**
  - **A-21 is still open, and it is the condition for keeping LOW.** A listed CA variable, or an unchecked `helper_image`, returns the grade to MEDIUM; `GIT_SSL_NO_VERIFY` set is HIGH, as a separate finding (T768). It is due before the next tag or by 2027-02-19, whichever is first.
  - **The clause is not used up.** "Any later image bump must also pass both jobs" applies to every later bump, and to an `apk add` pin that can pull in a newer `ca-certificates` (`docs/wiki/mcp-pin-bump-checklist.md` § 3, read here).
  - **The other residuals stand.** Unlogged cross-signs, no live connection test, the helper image pinned by tag only. The missing CA check in tag pipelines is SEC-T768-04, a separate id.
  - **2027-02-19 is now only A-21's date for this id** (section 6.3).

**Unchanged (108 tracked-LOW; v12 and earlier stay the record of their text)**

| Batch | Ids | n |
|---|---|---:|
| I | SEC-T722-01, SEC-T722-02, SEC-T722-03, SEC-T722-04, SEC-T722-05, SEC-T725-01, SEC-T725-02, SEC-T725-03, SEC-T724-01, TD-T724-01, TD-T774-01, SEC-T762-05, TL-T753-06, SEC-T780-03, SEC-T780-04, SEC-T780-07, TL-T780-03, TL-T780-04, TL-T780-05, TL-T780-06, TL-T773-02, TL-T773-03, TL-T773-04 | 23 |
| J | SEC-T663-02 | 1 |
| K | SEC-T714-02, SEC-T714-04, SEC-T714-06, SEC-T714-08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 |
| L | SEC-T726-01, SEC-T726-02, SEC-T726-03, TD-T726-01, TD-T726-02 | 5 |
| M | SEC-T727-01, SEC-T727-02, SEC-T727-03, SEC-T727-04, SEC-T727-05, SEC-T728-01, SEC-T728-02, SEC-T728-03, TD-T728-01, TD-T728-02, TD-T728-03, SEC-T696-07 | 12 |
| N | SEC-T730-03, SEC-T730-04, SEC-T730-06, SEC-T731-03, SEC-T731-04, SEC-T731-05, SEC-T732-01, SEC-T732-02 | 8 |
| P | SEC-T702-08 | 1 |
| Q | TD-T723-01, SEC-T735-08, SEC-T735-09, SEC-T773-02, SEC-T780-05, TL-T780-09, SEC-T762-04, TL-T761-10 | 8 |
| R | SEC-T735-06, SEC-T735-07, SEC-T736-01, SEC-T693-07 | 4 |
| S | SEC-T741-17 (the rest; A-20) | 1 |
| V | SEC-T748-03, SEC-T748-04, SEC-T748-05, SEC-T748-06, SEC-T748-07, SEC-T748-08, SEC-T748-09, SEC-T748-12, SEC-T751-01, SEC-T751-05, SEC-T751-06, SEC-T751-07, SEC-T751-08, SEC-T751-09, SEC-T773-01 | 15 |
| X | SEC-T756-07, SEC-T756-08, SEC-T768-01, SEC-T768-02, SEC-T768-04, SEC-T768-05, TL-T761-11 | 7 |
| Y | TL-T753-05, TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T763-01, TL-T763-02, TL-T780-08 | 8 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06, SEC-T780-06 | 6 |

Total 108; with the 3 changed and the 2 named, 113. Two notes that change no status:
- **TL-T761-08**: the CI header's bump recipe still omits the test constants. It is now `.gitlab-ci.yml:26-30` (read here; v12 cited `:25-29`).
- **SEC-T756-07**: SEC-T784-01 also concerns the `npx` entries, including `server-filesystem`. It is a separate finding about the user's Node, not about that package's advisories.

### 2.3 v12 `accepted` (49)

**Unchanged (49)**; no plan-148 source names any of them, and none has a new acceptance:
- The five rows of v12 § 2.3 with their v12 qualifiers. SEC-T660-01, SEC-T665-01 and SEC-T702-09 are accepted MEDIUM for v10.0.0 only, and each needs a fix or a new acceptance before v11.0.0. SEC-T657-01 / SEC-T658-01 (counted as one) and K-15 are accepted and close by removal at v11.0.0, unless the Opencode live check fails.
- TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29).
- The 40 LOW or INFO ids K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06, TL-T708-07.
- The orchestrator-accepted residues TL-T773-01, TL-T780-01, TL-T780-07.

5 + 1 + 40 + 3 = 49.

## 3. New ids

Grades are the reviewers' own (`SECURITY:*`). "Read here" means a line read on `dcc948d2`.

| Id | Grade | Short description | Status | Evidence, what stays | Batch |
|---|---|---|---|---|---|
| SEC-T784-01 | SECURITY:LOW (A06) | The eight `npx` MCP entries (`implementation/knowledge/mcp/servers.yaml`, lines as T784 § 6) run on the user's own Node, outside every pin here. On an unpatched Node 22, 24 or 26, CVE-2026-123871 can write a proxy credential into an error message, if the user turns on Node's built-in env proxy with credentials. CVE-2026-123877 and the undici and llhttp fixes are client-side | **tracked-LOW (open, unchanged by T785)** | T784 § 6; T786 § 2: "Open, tracked-LOW (unchanged)". Remediation: state the fixed minimums (≥ 22.23.5, ≥ 24.22.3, ≥ 26.13.1) in `PREREQUISITES.md` and in the v11.0.0 release document. **It includes replacing the end-of-life "Node.js 18+" floor at `implementation/PREREQUISITES.md:4` and `node --version  # ≥ 18` at `:227`** (plan-148 § Progress; both read here). Owner technical-writer; deadline the v11.0.0 release document (T786 Conditions). Do not add a version check to the generated entries (T784 § 6). **Part of T786's condition** | Q |
| SEC-T786-01 | SECURITY:LOW (A06) | `unit-tests` runs Alpine's `nodejs` 24.22.1-r1, which carries the November 2026 Node CVEs until Alpine v3.24 ships 24.22.3. The job binds the host Docker socket. No server-side CVE is reached; the client-side items are reachable only through `npm ci` against a TLS-protected, integrity-locked registry | **tracked-LOW** | T786 § 3; job log 17951936898 `Installing nodejs (24.22.1-r1)` (as T786 quotes it; not read here). The pins `'nodejs~=24'` and `npm ci` are at `.gitlab-ci.yml:102`, `:108-109` (read here). No code change needed: the fuzzy pin takes the fixed package. **Closes when** a `unit-tests` log shows `Installing nodejs (24.22.3-*)` or later. **Check at v11.0.0 preparation**: if Alpine still has no fixed package then, record it in the release document and re-grade. Raise it if the v24.22.3 notes show an llhttp or undici client memory-safety bug on a path `npm ci` takes. Do not move `npm ci` out of the socket job only for this (T786). Owner devops-engineer. **Part of T786's condition** | X |
| SEC-T786-02 | SECURITY:LOW (A05) | The image-bump procedure says "run the image to read its Alpine and runtime versions" (`docs/wiki/mcp-pin-bump-checklist.md:30`), against the rule of no `docker` in agent work (the configured Docker host is a remote production host). It also keeps a stale "(unverified until it runs)" note, and § 2 has a `docker run` musl check against "a remote Docker host" (`:26`) | **tracked-LOW** | T786 § 3. Line 30 still says "run the image to read its Alpine and runtime versions" (read here). Docs change only: read `/etc/alpine-release`, `/lib/apk/db/installed` and the config `Env` from the registry layers; name `verify-knowledge-drift`'s `node --version` line as the runtime proof; drop the stale note; mark the § 2 `docker run` as a maintainer-only step on a non-production host. Owner technical-writer; window next sprint (T786 Conditions). **Part of T786's condition** | Y |

**My batch choices** (T786 leaves Q or Y open for SEC-T784-01 and SEC-T786-02):
- **SEC-T784-01 → batch Q.** Its deadline is the v11.0.0 release document (T784, T786 Conditions), and that is batch Q's trigger. Q already carries the other items that the v11.0.0 document must hold (items 2, 4, 10, 31, 33). The `PREREQUISITES.md` edit is part of the same release step (item 38).
- **SEC-T786-02 → batch Y.** It is a docs fix with a "next sprint" window and no release binding (T786 Conditions). That matches batch Y: shipped text and records, owner technical-writer, triggered by the next docs change.

## 4. Decisions since v12

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the questions beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-11 | "Re-grade now, bump later (Recommended)" | The answer to the question that offered "Security Engineer re-grades SEC-T756-05/-06 against the published advisory now (docs only). I watch Docker Hub; once 24.22.3-alpine exists, DevOps bumps the digest, the APK pins and the review date, both CA-chain jobs must pass, security reviews, I merge on green." The request before it, verbatim: "Continue with the next best step" | plan-148 Based on |
| 2026-11-12 | "v13 go" | Plan-149, T787, this register | plan-149 Based on; task-T787 |

**Still unruled, for the user (SEC-T762-04, with TL-T761-10):** as v12 § 4.1 (section 6.2, item 33).

### 4.2 The orchestrator's rulings (not the user's)

| Item | Decision | Source | Effect |
|---|---|---|---|
| Proof obligation 7, "the old digest nowhere" | Applies to the live files (`.gitlab-ci.yml`, `docs/wiki/mcp-pin-bump-checklist.md`, the tests). Immutable records keep `06d7adf3` as history | plan-148 § Progress | T786 obligation 7 met on that basis |
| The upper bound on the wait | Ask the user if no official image carried 24.22.3 by 2026-12-11, or by the start of v11.0.0 preparation if earlier (T784 § 4 suggested it) | plan-148 § Progress | **Moot**: the image appeared 2026-11-11T23:42Z (plan-148 § Outcome) |
| T785 blocked | `blocked` (external, minor) until an official image carried 24.22.3 | plan-148 § Progress | BLK-T784-02 (section 1.2) |
| BLK-T784-01's cause | A scoping limit of `grep_content`, not a broken server; the worktree as cause is **(unverified)** | plan-148 § Progress | Answered (T786 § Blockers) |
| The pin checklist's line range | Fixed from 13-20 to 13-21 | plan-148 § Outcome | `mcp-pin-bump-checklist.md:30` names "lines 13-21" (read here) |
| The python re-read behind `.gitlab-ci.yml:19` | `python:3.12-alpine` re-read at 2026-11-12T00:15Z, still `e064671c…` (T786 Recommendation 3) | plan-148 § Outcome | Backs line 19's claim of the digest. Line 19 says "re-read the same day" (2026-11-11), which rests on T785's report. The orchestrator's read is timed 2026-11-12T00:15Z with no time zone given. Whether it fell on the same day is **(unverified)**; no grade depends on it (T786) |
| Batch choices for SEC-T784-01, SEC-T786-02, and SEC-T768-06 as fixed | **Mine** (section 3, section 2.2) | this register | section 5 |

T785's change of the sample string at `tests/functional/test_pin_bump_checklist.py:97` was T785's own decision, which plan-148 left to it, not a ruling. T786 obligation 7 found that it keeps the assertion's strength.

### 4.3 Errors on the record

These stay as the sources state them.
- **The review date's failing day.** v12 § 4.3 and § 6.3 (fails from 2027-03-07) and T784 § 4 ("fails after 2027-03-06") were true for `2026-11-06`. They are superseded by the new date, not wrong (section 6.3).
- **Two counts of the CPU evidence.** T786 obligation 1 names three jobs that log the x86-64 CPU. Plan-149 § Facts and its Task Decomposition say every job of pipeline 3056919066. I read no job log, so the wider statement is the orchestrator's **(unverified here)**.

## 5. Open items by LOW batch

"Do first" as in v5; the flag's source stays **(unverified)** as v5 § 5 says. Batches I, J, K, L, M, N, P, R, S, V, Z, F and U are carried from v12 without change. **Q and Y grow by one each. X loses three and gains one, and gets a new trigger.**

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v12 § 5 | 23 | as v12 | as v12. **TD-T774-01 needs a grade first** (my suggestion) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v12 | as v12 |
| K | Security runtime | as v12 § 5 | 7 | as v12 | as v12 |
| L | CWSO helper scripts in emage.code | as v12 § 5 | 5 | as v12 | as v12 |
| M | CWSO repository | as v12 § 5 | 12 | as v12 | as v12 |
| N | Release tooling, second round | as v12 § 5 | 8 | as v12 | as v12; the release scripts have no diff since v12 |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v12 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, SEC-T773-02, SEC-T780-05, TL-T780-09, SEC-T762-04, TL-T761-10; **new:** SEC-T784-01 | 9 | release-manager; technical-writer for SEC-T784-01; the orchestrator routes; **the user rules on SEC-T762-04 and TL-T761-10** | **the v11.0.0 release** (items 2, 4, 10, 31, 33, 38) |
| R | Release-gate text, second round | as v12 § 5 | 4 | orchestrator routes each | **the route of SEC-T735-06 and -07 is still to be settled before batch R** |
| S | Release gate: the runner tag | SEC-T741-17 (the rest) | 1 | the user (A-20) | waits on the user's runner |
| V | Release gate after plans 142, 143 and 146 | as v12 § 5 | 15 | devops-engineer | **open, for the user**: no source binds V to a release; SEC-T751-06 first (v11's suggestion) |
| X | CI images, the CA control and runner settings | SEC-T756-02, SEC-T756-07, SEC-T756-08, SEC-T768-01, SEC-T768-02, SEC-T768-03, SEC-T768-04, SEC-T768-05, TL-T761-11; **new:** SEC-T786-01. **Left:** SEC-T756-05, SEC-T756-06, SEC-T768-06 (fixed) | 10 | devops-engineer (T768: "next sprint"; -04 at the next tag-job change) | **Alpine's `nodejs` 24.22.3 in a `unit-tests` log; check at v11.0.0 preparation** (SEC-T786-01, item 37); A-21 (SEC-T756-02, TL-T761-11); **every later image bump must pass both CA jobs** (SEC-T756-02, item 35) |
| Y | Shipped text and records | TL-T753-05, TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T763-01, TL-T763-02, TL-T780-08; **new:** SEC-T786-02 | 9 | technical-writer; orchestrator for TL-T753-07 and TL-T761-12 (suggested; no source sets it) | the next docs change ("next sprint" for SEC-T786-02); TL-T761-12 before the next first-tag use of `CONTRIBUTING.md` |
| Z | `context-retriever` after M-2: code residue | QA-T760-01, QA-T760-02, QA-T760-03 (**open, QA Medium**) | 3 | backend-developer through the orchestrator (QA C1) | **"next release"** (QA C1). Item 36 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v12 | as v12 |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06, SEC-T780-06 | 7 | the user or an authorised live session | A-2, A-7, A-11, A-15, A-22 |

Total 23 + 1 + 7 + 5 + 12 + 8 + 1 + 9 + 4 + 1 + 15 + 10 + 9 + 3 + 2 + 7 = 117 = 113 tracked-LOW + 4 open. **No open item carries a `SECURITY:*` grade above LOW.** Batch Z carries QA's Medium, and TD-T774-01 has no grade.

**Order, my suggestion only.**
1. Z, because QA binds it to the next release.
2. At v11.0.0 preparation: X's SEC-T786-01 check, and Q with SEC-T784-01, in the release document.
3. Y's SEC-T786-02, in the next docs change, so the next image bump follows a procedure without `docker`.
4. V's SEC-T751-06, as v11 suggests.
5. I's TD-T774-01, once graded.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v12 § 6.1 stand and stay the record. Nothing new since v12: plan-148 accepted no risk. The MEDIUM end dates are as v12 § 6.1.

### 6.2 Next release checklist (v11.0.0, MAJOR)

Carried from v12 § 6.2, with its numbers. **Items 14, 19, 21, 23 and 35 change, and items 37 and 38 are new.** Items not named here keep v12's text. I re-read every line citation into `.gitlab-ci.yml` in v12 § 6.2 (items 14, 19, 21, 23, 35). v11 § 6.2, which v12 carries for its unnamed items, cites `.gitlab-ci.yml` lines only in items 14, 19, 21 and 23 (one grep, read here). The file gained one line in the image record (the default image moved from `:42` to `:43`), one in `verify-knowledge-drift` (`:134`) and one comment line in `ca-chain-check-node` (`:191-192`). Citations into `tests/functional/test_ci_hash_pins.py`, `CONTRIBUTING.md`, `docs/releases/_template.md`, `scripts/install.sh` and the release scripts stand, because those files have no diff since v12.

14. As v12, with the lines now: `release-docs-gate` `.gitlab-ci.yml:252-274`, the removal `:268`, the `timeout` `:260`; the `release` job's `GIT_STRATEGY: clone` `:305` (read here).
19. As v12, with the CI header's recipe now at `.gitlab-ci.yml:26-30` (TL-T761-08; read here). The test lines (`test_ci_hash_pins.py:1287-1288`, `:82`, `:93`) are unchanged. This bump changed no `apk` pin and no Python minor (T786 obligation 4), so it needed no test edit, as v12 item 19 predicted.
21. As v12; the job shell's comment is now `.gitlab-ci.yml:269`.
23. As v12; the `release` job's `script` line is now `.gitlab-ci.yml:312`.
35. **Both CA-chain jobs** (`ca-chain-check-python` `.gitlab-ci.yml:160`, `ca-chain-check-node` `:181`; read here) must pass on the release commit. **The Node image bump is done and both jobs passed on it**: MR pipeline 3056919066 on `50520592` (T786 obligation 5) and pipeline 3056985425 on the merged state (plan-149 § Facts). **What it still leaves for the tag:**
    - the jobs must pass on the release commit itself, in its branch or MR pipeline, because tag pipelines run no CA check (SEC-T768-04);
    - any further image bump, or an `apk add` pin that can pull in a newer `ca-certificates`, before the tag must pass both jobs again;
    - A-21 (item 34).
37. **New. SEC-T786-01's check at v11.0.0 preparation.** Read a current `unit-tests` log for `Installing nodejs (24.22.3-*)` or later. If Alpine v3.24 still has no fixed `nodejs` then, record it in the release document and have it re-graded (T786 § 3, Conditions).
38. **New. SEC-T784-01's Node minimums.** The release document and `implementation/PREREQUISITES.md` name the fixed Node versions (≥ 22.23.5, ≥ 24.22.3, ≥ 26.13.1) as the minimum for the `npx` MCP entries. They replace the end-of-life "Node.js 18+" floor at `PREREQUISITES.md:4` and `≥ 18` at `:227` (T784 § 6; T786 Conditions; plan-148 § Progress).

### 6.3 Dates

Carried from v12 § 6.3, with three rows updated.

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced **(unverified)** | TD-T728-02 (batch M) |
| **2026-11-11** | **Done.** The Node security advisory was published, and the CI default image moved to Node 24.22.3 on Alpine 3.24.4. Both CA jobs passed on it (MR !667; T785, T786; plan-148 § Outcome). What stays: Alpine's `nodejs` in `unit-tests` (SEC-T786-01, item 37) | SEC-T756-05, -06 fixed |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; end of TD-T697-07 | A-13, TD-T697-07 |
| **2027-01-30** | End of the Brave acceptance (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| **2027-01-31** | SEC-T657-01/SEC-T658-01's shown deadline (T762 Q4); moot if v11.0.0 ships first | section 2.3 |
| **2027-02-19** | **A-21 due** (or before the next tag, if earlier). SEC-T756-02's shown deadline: its "and before any earlier image bump" clause was met at T785 (section 2.2), so the date remains as A-21's | SEC-T756-02, A-21 |
| **2027-03-11** | **The last day `test_the_review_date_is_present_and_fresh` passes.** `ci_images_reviewed_on: 2026-11-11` (`.gitlab-ci.yml:21`) plus `MAX_REVIEW_AGE_DAYS = 120` (`tests/functional/test_ci_hash_pins.py:1255`). The test's own boundary check (`:1288-1290`) passes at 120 days and fails at 121. **It fails from 2027-03-12.** By reading and date arithmetic, not a run on that date (plan-149 § Facts; read here). This replaces v12's 2027-03-06 and 2027-03-07 | the next image review |

The token dates repeat v6 to v12, which did not re-read them; nor did I **(unverified)**.

## 7. User actions

Carried from v12 § 7 unchanged. No plan-148 source changes a user action. **A-21 is still open** (T786 § 6 item 5; plan-148 § Constraints: no runner, CI variable or project setting was changed or read). A-22's state is still **(unverified)**: the two settings files were not opened.

## 8. Method, limits and validation

- **Carried statuses**: v12's rows and lists, plus the sources in Based on. Line reads and greps on `dcc948d2` where cited "read here". Plan-149 § Facts is the only source for pipeline 3056985425 on `ff488f64` and for the ledger count (0 active, 583 completed after !667). `docs/tasks/completed-tasks.md` holds 583 task rows (read here). No network call was made.
- **The search for changes**: a script extracted every id-like token from v12 (234 distinct tokens, including user-action numbers). It searched the 596 lines added in `b45f400e..fa33912c` outside `tests/golden/`. Only SEC-T756-02, -05, -06, SEC-T768-03 and -06, and A-21, are named. Each hit was read in context. A-21 appears only as a reference, with no change. SEC-T756-02 appears once, in T784 § 2's remark that the CA store question stays under the CA-chain jobs. SEC-T768-06 appears once, in T784 § 5's "compare SEC-T768-06". The edit of the line it names is what changed it (section 2.2). The same lines were searched for new `<PREFIX>-T<nnn>-<n>` ids (section 1.2).
- **Counting**: 3 new ids from the findings tables of T784 § 6 and T786 § 3. Section 5 expands to 117 distinct ids: the 110 v12 tracked-LOW ids that remain, the 4 open ids and the 3 new ids. I checked by hand that every id of v12 § 5 occurs in this artifact.
- **Where the sources differ or leave a gap** (none changes a status beyond section 1):
  - **SEC-T768-06's closure** is my reading; no reviewer rules on it (section 2.2; alternative totals in section 1).
  - **The CPU evidence**: three jobs per T786, every job per plan-149 (section 4.3).
  - **The python re-read's day** (section 4.2).
  - **QA's Medium** and **TD-T774-01's missing grade**, as v12.
- **What real jobs proved.** Source: T786 § 1, from the orchestrator's evidence file, and plan-148 § Outcome. I read no job log.
  - MR pipeline 3056919066 on `50520592`, 7 of 7 jobs. Each Node job pulled `116b800c…` by digest. `node --version` printed `v24.22.3` (job 17951936899).
  - Both CA jobs PASS: 0 of 19, controls 1 of 1, `--ca-release` before and after `apk add`. The Node job is bundle-only, with equal `sha256sum`.
  - `unit-tests` installed `nodejs (24.22.1-r1)` and `npm (11.12.1-r0)` (job 17951936898).
  - Drift and sync passed on 314 files. The runner CPU is x86-64.
  - Pipeline 3056985425 on `ff488f64` green (plan-149 § Facts).
  - The full suite in a clean worktree: 2707 tests OK, 24 skipped, at `50520592` (plan-148 § Outcome) and at `ff488f64` (plan-149 § Facts).
- **What registry and package APIs proved.** These are the orchestrator's and T785's reads, not re-run here.
  - Docker Hub: `24-alpine` = `24.22.3-alpine` = `24.22.3-alpine3.24` = `116b800c…`, with the index body re-hashed (the orchestrator recorded a prefix match; T785 reports full equality). The amd64 manifest is `d8d97e47…`, with config `NODE_VERSION=24.22.3` and minirootfs 3.24.4.
  - `python:3.12-alpine` is still `e064671c…` at 2026-11-12T00:15Z.
  - pkgs.alpinelinux.org: v3.24 `nodejs` is still `24.22.1-r1` (2026-11-11, plan-148 § Progress).
  - T784 read the Node advisory, `index.json` (to character 100,000) and the Alpine 3.24.4 announcement on 2026-11-11.
- **What is a hand trace**:
  - T784 § 1's per-CVE reachability mapping (source reading, partly from knowledge, as T784 marks);
  - T786's reasoning for SEC-T786-01's grade;
  - T785's layer reads (apk-tools 3.0.9-r0, `/etc/alpine-release`, no hashed `/etc/ssl/certs`);
  - the orchestrator's greps of `sync.mjs`, `verify.mjs` and `tests/` for Node network code (plan-148 § Progress);
  - my reading of `mcp-pin-bump-checklist.md:30` for SEC-T768-06;
  - the date arithmetic in section 6.3.
- **Dropped from v12's unverified list, each with what settled it**:
  - **"Non-amd64 images" for the runner.** The jobs log an x86-64 CPU (T786 obligation 1). The arm64/v8 and s390x manifests stay unread and unused (below).
  - **The Node advisory's content (SEC-T756-05)** and **Alpine 3.24.4's notes (SEC-T756-06).** T784 read both on 2026-11-11 (T784 Based on, § 1, § 2). Their unread parts are listed below.
- **Still unverified**:
  - Carried from v12 § 8 unless dropped above.
  - New, from T786 § 6:
    1. the git diff's file list, as the reviewer saw it (it had no git tool; the orchestrator's merge check covers it, and the diff stat is in Metadata here);
    2. apk-tools 3.0.9-r0, `/etc/alpine-release` and the absence of hashed `/etc/ssl/certs` entries, which come from T785's layer read (the CI log backs the last one);
    3. the full index body re-hash (a prefix match by the orchestrator);
    4. the arm64/v8 and s390x manifests;
    5. the runner's configured platform and the project or runner settings (A-21);
    6. the python re-read claim at `.gitlab-ci.yml:19`, now backed by the orchestrator's re-read, with its day open (section 4.2);
    7. the v24.22.3 notes for the llhttp, undici and sqlite updates (this bears on SEC-T786-01's raise trigger);
    8. when Alpine will ship `nodejs` 24.22.3 for v3.24.
  - Also still open from T784 § 8, not settled by T786 or the orchestrator's checks:
    - the Alpine git log behind "core components" (covered by the base move, T784 § 3);
    - `openssh-server` absent from both bases;
    - Node's env proxy being opt-in on 24.x, and npm not using `ProxyConfig`;
    - whether any pinned `npx` package uses `https.Agent` with `ca: []`, the built-in proxy, `zlib.params()` or `node:sqlite`, or opens a listening socket.
- **Not run here**: the suite and the pipelines, which the orchestrator ran before the merge. No mutation and no full suite ran for this register.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `timeout 300 python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v12.md`; `plan-149-tracked-debt-register-v13.md`; `docs/tasks/task-T787.md`; `plan-148-node-image-bump.md`; `security-review-t784-node-advisory-v1.md`; `security-review-t786-node-bump-v1.md`; `security-review-t768-ca-control-v1.md`; `checkpoint-042-plan-146-ca-pi-gemini.md`; `docs/tasks/completed-tasks.md` rows T784 to T786;
  - by grep or line range: `.gitlab-ci.yml`, `docs/wiki/mcp-pin-bump-checklist.md`, `implementation/PREREQUISITES.md`, `tests/functional/test_ci_hash_pins.py`, `docs/releases/v10.0.0.md`, `security-review-t756-accepted-mediums-v1.md`, and v11 § 6.2 (one grep);
  - `git log` and `git diff b45f400e..fa33912c`.
- Decision IDs: ADR-011.
