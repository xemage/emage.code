# Artifact: tracked-debt-register-v24.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v23.md` (732 ids; v23 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-179-tracked-debt-register-v24.md` (§ User decision, § Facts since v23, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T865.md` (the user's "v24go"); `docs/plans/plan-177-batch-x-ci-images-ca-runner.md` (§ Outcome); `docs/plans/plan-178-batch-ab-opencode-third-round.md` (§ Outcome); `docs/artifacts/security-review-t860-batch-x-v1.md` (CONDITIONAL_PASS, condition met); `docs/artifacts/security-review-t862-batch-ab-v1.md` (PASS); `docs/artifacts/ca-check-t767-v2.md`; `docs/wiki/mcp-pin-bump-checklist.md`; `.gitlab-ci.yml` (`ci_images_reviewed_on`). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T865 (plan-179; the user's answer of 2026-11-19, verbatim: "v24go"). **Date**: 2026-11-19.
- **Tree read**: branch `agent/tech-lead/T865` at `4ad619a1` (develop `a66444c4` plus the plan-179 commit). The range for "lines added since v23" is `aedc43f0..4ad619a1` (plan-179 § Facts names `aedc43f0..a66444c4`; the one extra commit is plan-179's own plan, brief and ledger row): 75 files, 3569 lines added and 66 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range, so the search set outside them is the same 75 files and 3569 added lines (read here).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `4ad619a1`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v22 only by grep. The raw JSON files under `docs/artifacts/mcp-agent-denials-evidence-v4/` were scanned only as added lines (section 1.2), not read. `/tmp/evidence-run` was checked only for existence. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v23.
- **Batch letters**: **X shrinks** from 10 to 4 (six ids fixed) and takes **SEC-T860-01** and **SEC-T860-02** (my suggestion), so 6. **AB shrinks** from 3 to 1 (two ids fixed) and takes **SEC-T862-02** (my suggestion), so 2. No new letter.

## 1. Summary

v24 holds **737 ids**: the 732 of v23 and **5 new**. After v24: **565 fixed**, **46 accepted**, **10 obsolete**, **1 open**, **115 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 have no reviewer's grade (the orchestrator's ids, called LOW). The only MEDIUMs still accepted for v11.0.0 are SEC-T660-01 and SEC-T665-01 (accepted, not open).
- **Fixed since v23 (8 tracked-LOW)**: SEC-T756-07, SEC-T756-08, SEC-T768-01, SEC-T768-02, SEC-T768-03, SEC-T768-05 (batch X; T859, confirmed by T860) and SEC-T856-01, SEC-T856-03 (batch AB; T861, confirmed by T862) (section 2.2).
- **New, minted and fixed (2)**: SEC-T860-03 (the orchestrator, `17f16d36`) and SEC-T862-01 (the orchestrator, `f9f3a86b`) (section 3).
- **New and tracked-LOW (3)**: SEC-T860-01, SEC-T860-02 (batch X) and SEC-T862-02 (batch AB) (section 3; batches my suggestion).
- **Tracked-LOW with a changed note (5)**: SEC-T856-02 (narrowed), SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05 (section 2.2).
- **Accepted risks**: unchanged. **Next-release checklist**: item 49 (d) restated from T862 § 4 (section 6.2). **Dates**: the CI image review now fails from **2027-03-20**; the others unchanged (section 6.3). **User actions**: SEC-T811-05 with SEC-T860-02, and the optional removal of `/tmp/evidence-run` (section 7).

Arithmetic, from the v23 totals:

| Status | v23 | leaves | enters | v24 |
|---|---:|---|---|---:|
| fixed | 555 | | + 8 tracked-LOW (SEC-T756-07, SEC-T756-08, SEC-T768-01, -02, -03, -05, SEC-T856-01, -03) + 2 new (SEC-T860-03, SEC-T862-01) | **565** |
| accepted | 46 | | | **46** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 120 | - 8 fixed | + 3 new (SEC-T860-01, -02, SEC-T862-02) | **115** |
| **all** | **732** | | + 5 new ids | **737** |

Check: 565 + 46 + 10 + 1 + 115 = 737. Open or tracked: 115 + 1 = 116, the size of section 5.

### 1.1 Ids by v23 status and status now

| v23 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 120 | 8 | 0 | 0 | 0 | 112 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 555 | 555 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v23 ids** | **732** | **563** | **46** | **10** | **1** | **112** |
| new in v24 | 5 | 2 | 0 | 0 | 0 | 3 |
| **all v24 ids** | **737** | **565** | **46** | **10** | **1** | **115** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t860-batch-x-v1.md` § Findings: SEC-T860-01, SEC-T860-02, SEC-T860-03 | 3 | 1 (SEC-T860-03) | 2 |
| `security-review-t862-batch-ab-v1.md` § 5: SEC-T862-01, SEC-T862-02 | 2 | 1 (SEC-T862-01) | 1 |
| **All new** | **5** | **2** | **3** |

**Ids minted in the range beyond the plan's list: none.** A search of the 3569 added lines in `aedc43f0..4ad619a1`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `L-<n>`), and separately for a bare `<PREFIX>-T<nnn>` not followed by a suffix, finds exactly: A-21, ADR-001, ADR-003, ADR-005, ADR-011, CVE-2026 (from `CVE-2026-115557`), K-20, K-23, SEC-T660-01, SEC-T677-01, SEC-T741-17, SEC-T756-02, SEC-T756-07, SEC-T756-08, SEC-T768-01 to -05, SEC-T786-01, SEC-T811-04, SEC-T811-05, SEC-T837-01, SEC-T842-02, SEC-T856-01 to -03, SEC-T860-01 to -03, SEC-T862-01, SEC-T862-02, `SHA-256`, TL-T761-11 (read here). No bare form occurs.

**Non-debt tokens.** The raw evidence JSON added in the range (`docs/artifacts/mcp-agent-denials-evidence-v4/*.json`) stores each agent's resolved rules together with its prompt text. ADR-001, ADR-003 and ADR-005 occur only in those files (the Tech Lead and Context Retriever prompts; read here, by the file headers of the matching hunks). `CVE-2026-115557` is the advisory named in the CA-check paragraph of the checklist, and `SHA-256` is a hash name. None is a debt id, and nothing in the raw files is read as a status change.

Set against registers v1 to v23, only SEC-T860-01 to -03 and SEC-T862-01, -02 are in no register (read here, by grep). Beside them:
- **Ids named with a change of status**: the 8 fixed ids of section 2.2.
- **Ids named with a changed note and no change of status**: SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05, SEC-T856-02 (section 2.2).
- **Ids named with no change of status**: SEC-T660-01 (accepted for v11.0.0; T862 § 4); K-23 (as v12 to v23 record it; T862 § 4); K-20 (open); A-21 (closed in v18; named in the checklist and T860 § 5); SEC-T786-01 (fixed in v17; plan-177 § Outcome says Alpine 3.24's `nodejs` 24.22.3 "covers" it, which matches v17); SEC-T677-01, SEC-T741-17, SEC-T811-04, SEC-T837-01, SEC-T842-02 (fixed in v6, v17, v17, v21 and v23; named in context lines of the checklist and the wiki); ADR-011 (named, not amended).
- This register mints no id.

## 2. v23 ids re-checked

Every v23 `open`, `tracked-LOW` and `accepted` id (167) is covered: the changed ones have a row here, the rest are unchanged and carried. The v23 `fixed` and `obsolete` ids stay as v23 records them.

### 2.1 v23 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). T861 observed resolved rule lists on Opencode 1.19.2 (evidence v4); a refused call, a launch and a refused read were not observed (T862 § 3, § 4). K-20 keeps them.

### 2.2 v23 `tracked-LOW` (120)

**Changed to fixed (8).**

| Id | v23 | now | Evidence and remainder |
|---|---|---|---|
| SEC-T756-07 | tracked-LOW, batch X | **fixed** | T859: `server-filesystem` 1.0.0 → 2.4.0, no `glob` in its tree, minimatch 11.0.9, audit clean, provenance; its HTTP transport is unreachable from the stdio launch line (plan-177 § Outcome (d)). T860 § 3 and § Per-finding statuses: **Fixed in source**; the root half came with T864's refresh (3 pin lines, drift `[]`, plan-177 § Outcome). **Remainder**: SEC-T860-01 (the pin was one day old; no cooldown rule) |
| SEC-T756-08 | tracked-LOW, batch X | **fixed** | T859: `sync-wiki.py` refuses redirects; T860: `_RefuseRedirects.redirect_request` returns `None`, so `PRIVATE-TOKEN` is never re-sent. T860's tests are **(unverified)** by T860; not re-run here |
| SEC-T768-01 | tracked-LOW, batch X | **fixed** | T859: the scan reads the `TRUSTED` and `X509` forms, fails on any other `BEGIN`, asserts the count; a silent empty-hash bug in `spki_of` fixed too (plan-177 § Outcome (b)). T860: **Fixed** |
| SEC-T768-02 | tracked-LOW, batch X | **fixed** | T859: fixture cross-check added; it found two unlisted rollover keys of `EM DV TLS CA - G3B`, now listed (14 keys); `sha256sum -c` in both CI jobs. T860 § 2: **Fixed**; the old gap was real but narrow. The orchestrator recomputed every fixture SPKI (plan-177 § Outcome; not re-run here) |
| SEC-T768-03 | tracked-LOW, batch X | **fixed** | T859: guarded `--capath` run (Python job unconditional, fails closed with exit 2 on no hashed entries; Node job guarded). T860: **Fixed** |
| SEC-T768-05 | tracked-LOW, batch X | **fixed** | T859: `ca-check-t767-v2.md` says 3 extra certificates, matching `EXPECTED_EXTRA=3`. T860: **Fixed** per T859, v2 itself not read by T860 **(unverified)** there; not re-read in full here |
| SEC-T856-01 | tracked-LOW, batch AB | **fixed** | T861 `d550037c`: wiki rule (neutral scratch root or `<path>`, a `**Redaction**` Metadata line); `T861EvidenceRedactionTests` enforces it from v4 on; v4 taken from `/tmp/evidence-run`. T862 § 3: **Fixed**. **Remainder**: v2 and v3 keep their paths by design (immutable, hashes pinned, accepted by T862); the test's gaps are SEC-T862-02 |
| SEC-T856-03 | tracked-LOW, batch AB | **fixed** | T861 `ed214742`: PREREQUISITES and the wiki say only the default `gitlab-mcp` directory name is covered and that the token must never be placed under or linked into a project. T862 § 3: **Fixed** (documentation was the remediation). **Remainder**: inherent, user-controlled, recorded in item 49 (d) |

**Tracked-LOW with a changed note (5).**

| Id | Batch | Changed note | Source |
|---|---|---|---|
| SEC-T856-02 | AB | **Narrowed.** T861 `2603bb57` emits `external_directory: {"*/gitlab-mcp/*": deny}` for the 13 agents without `execute`; with the `read` map this covers `read`, `grep` and `glob` on the default token directory in the resolved lists (evidence v4; a refused call not observed, K-20). **What remains**: a `grep` (or `glob`, names only) on a **parent** directory such as `/dev/shm` or `/run/user/<uid>`, guarded only by that parent's `external_directory` rule (default `ask`; `allow` under a broad user rule). T862 § 2.3 rules not denying the parent the right choice | T862 § 2.3, § 3; plan-178 § Outcome |
| SEC-T756-02 | X | **Stays LOW.** T859's CA work strengthens the control (three certificate forms, fixture cross-check, two more keys, `--capath` runs) but does not close it. A-21 was closed in **register v18** on the user's report, not in v17; T860 corrects the brief's citation | T860 § 5, § Per-finding statuses |
| SEC-T768-04 | X | **Trigger not reached**: no tag-job edit in the range. T860 relied on the header comment and did not read the tag-job bodies **(unverified)** | T860 § Per-finding statuses; plan-177 § Outcome (e) |
| TL-T761-11 | X | **The note was added** beside A-21's flag point, `docs/wiki/mcp-pin-bump-checklist.md` line 38 (read here). Per v18 the flag is absent, so `release`'s fetch keeps its current behaviour. The note's first wording ("still unreported") was SEC-T860-03, corrected | T860 § Per-finding statuses; read here |
| SEC-T811-05 | X | **The steps are written** in checklist § 3, "Release-gate runner hardening" (read here, line 36): (1) services, (2) patching, (3) nothing else in that LXC. **It is now a user action** (section 7); SEC-T860-02 adds two points the text still lacks | T860 § 4; plan-177 § Outcome (f) |

**Unchanged (107 tracked-LOW; v23 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, Y 11, F 2, U 5 (U's sixth id is K-20, open). 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 11 + 2 + 5 = 107; with the 5 changed-note ids, 112 carried; with the 3 new, 115 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v23 and not recounted id by id here. X's members were traced here: v16 § 5's ten less SEC-T786-01 plus SEC-T811-05, as v17 § 5 records.)

### 2.3 v23 `accepted` (46)

**Unchanged (46)**, with their v17 qualifiers (v17 section 2.3) and v22's removal of SEC-T702-09. SEC-T660-01 is named in the range: T862 § 4 narrows its Opencode scope with no change of status (section 6.2, item 49). SEC-T665-01 is not changed by any source in the range.

## 3. New ids

The grade is the reviewer's own (T860 § Findings, T862 § 5).

| Id | Grade | Short description | Status | Evidence and remediation | Batch |
|---|---|---|---|---|---|
| SEC-T860-01 | SECURITY:LOW (A06/A08) | No minimum release age for an `npx` pin bump in `docs/wiki/mcp-pin-bump-checklist.md` § 1; the 2.4.0 pin was one day old (acceptable here, T860). Read here: the checklist's cooldown text covers the Python locks (`--exclude-newer`, 7 and 14 days), not `npx` pins | **tracked-LOW** | Add a cooldown, for example 7 days after publication; a younger pin needs a recorded exception naming provenance, audit and diff review. Owner devops-engineer | X |
| SEC-T860-02 | SECURITY:LOW (A05) | Checklist § 3 runner steps: (a) no check that `services_limit` takes effect on the runner's unrecorded version; (b) patching only at the 120-day review, no out-of-cycle trigger. Read here: line 36 has neither | **tracked-LOW** | (a) After the restart, check the runner log for an unknown-key warning and record `gitlab-runner --version` in § 5; (b) patch at once for a critical runc, Docker Engine or kernel escape advisory, 120 days as the ceiling. Owner devops-engineer (text); the user applies | X |
| SEC-T860-03 | SECURITY:LOW (A09, record accuracy) | Checklist § 3 line 38 said the `FF_GIT_URLS_WITHOUT_TOKENS` state "is still unreported", though register v18 closed A-21 | **fixed** | The orchestrator in `17f16d36` (T860's condition, before merge). Read here: line 38 now says "A-21 is closed: by the user's report the flag is absent … (register v18)"; no "unreported" remains in the checklist, `docs/wiki/` or `ca-check-t767-v2.md` | - |
| SEC-T862-01 | SECURITY:LOW (A05, documentation accuracy) | `docs/wiki/mcp-servers.md` line 123 still said `grep` on the token directory reads the token where `external_directory` resolves to allow; superseded by T861 for the 13 agents | **fixed** | The orchestrator in `f9f3a86b` (one line changed in that bullet, read here by `git show`) | - |
| SEC-T862-02 | SECURITY:LOW (A05) | `tests/functional/test_mcp_agent_denials.py` lines 1474-1507 (per T862): the redaction test checks the runner's own user name, only as `/<user>/`, scans the raw files but not the evidence `.md`, and lacks `/var/folders/`, `/private/var/` and `C:\Users\` | **tracked-LOW** | Scan the evidence `.md` from v4 on; add the macOS and Windows prefixes; keep the local clean-suite run as the user-name check of record and say so in the wiki rule | AB |

`17f16d36` and `f9f3a86b` are branch commits: neither is an ancestor of `4ad619a1` (read here), because the MRs were squash-merged; their content is in `9023641c` and `f1378000` (the lines were read on `4ad619a1`).

## 4. Decisions since v23

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-19 | "Refresh now (Recommended)" | T863 root refresh (batch AB) | plan-178 § Outcome |
| 2026-11-19 | "Refresh, keep python pin (Recommended)" | T864 root refresh; the `python:3.12-alpine` pin kept | plan-177 § Outcome (a), T864 |
| 2026-11-19 | "v24go" | This register | plan-179 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| The six batch X ids | Fixed | T860 (CONDITIONAL_PASS); the orchestrator | T860; plan-177 § Outcome |
| SEC-T856-01, -03 | Fixed; SEC-T856-02 narrowed | T862 (PASS); the orchestrator | T862 § 3; plan-178 § Outcome |
| The python pin | Kept: the `linux/amd64` manifest is byte-identical under both indexes; only `linux/riscv64` differs | the orchestrator's ruling after its own registry check; the user confirmed | plan-177 § Outcome (a) |
| SEC-T860-03, SEC-T862-01 | Minted LOW, fixed before merge | T860, T862; the orchestrator | section 3 |
| SEC-T860-01, -02, SEC-T862-02 | Minted LOW, tracked under the LOW policy | T860, T862; the orchestrator | plan-177, plan-178 § Outcome |
| Batches of the three new ids | X, X, AB | me (suggestion) | section 5 |
| Merges, pipelines, suite, ledger | As plan-179 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** My reading gives the same 8 fixed, 2 minted and fixed, 3 new tracked-LOW, 5 changed notes, 737 ids (565 / 46 / 10 / 1 / 115) and a batch total of 116. What I add: the batches of the three new ids, the non-debt tokens of section 1.2, and the points below.
- **The commit range.** Plan-179 § Facts names `aedc43f0..a66444c4`; this register searched `aedc43f0..4ad619a1`, which adds plan-179's own commit. That commit mints no id.
- **The fix commits.** `17f16d36` and `f9f3a86b` are not on develop's first-parent history (squash merges, section 3); the fixed text is.
- **The review date arithmetic.** "2026-11-19 + 120 days" is 2027-03-19, the **last passing day**: `test_ci_hash_pins.py` fails when the age is more than 120 days (`(today - reviewed).days > 120`; the test asserts no problem at +120 and a problem at +121; read here). So it **fails from 2027-03-20** (+121), consistent with earlier registers' 2027-03-12 for 2026-11-11 (+121). The plan's date is right; its "+ 120 days" is shorthand.
- **The user action steps.** Plan-177 § Outcome lists "check the runner log for an unknown-key warning" among the checklist § 3 steps. Read here: § 3 holds steps (1) to (3) only; the unknown-key check and the out-of-cycle trigger are SEC-T860-02's remediation, not yet written in the checklist. Section 7 names both, marked as such.
- **T860's citation correction.** T860 says the brief cited v17 for A-21's closure; v18 is right. This register cites v18.
- **Ledger.** Plan-179 § Facts: "0 active, 661 completed". Read here: `completed-tasks.md` holds 661 task rows and `active-tasks.md` one (T865, added by the plan-179 commit). No difference.

## 5. Open items by LOW batch

Carried from v23 § 5; X and AB change.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v23 § 5 | 24 | as v23 | as v23 |
| K | Security runtime | as v23 § 5 | 8 | as v23 | as v23 |
| L | CWSO helper scripts in emage.code | as v23 § 5 | 5 | as v23 | as v23 |
| M | CWSO repository | as v23 § 5 | 12 | as v23 | as v23 |
| N | Release tooling, second round | as v23 § 5 | 10 | as v23 | as v23 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v23 | as v23 |
| Q | Next release document and its gate rulings | as v23 § 5 | 5 | as v23 | as v23 |
| R | Release-gate text, second round | as v23 § 5 | 7 | as v23 | as v23 |
| V | Release gate after plans 142, 143 and 146 | as v23 § 5 | 17 | as v23 | as v23 |
| **X** | CI images, the CA control and runner settings | SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05; **new:** SEC-T860-01, SEC-T860-02. **Left:** SEC-T756-07, SEC-T756-08, SEC-T768-01, -02, -03, -05 (fixed) | 6 | devops-engineer (text); the user for SEC-T811-05 and SEC-T860-02's steps | SEC-T768-04 at the next tag-job change; SEC-T860-01 at the next `npx` pin bump; SEC-T860-02 with the next edit of checklist § 3, applied by the user with SEC-T811-05 at the next runner maintenance; SEC-T756-02 and TL-T761-11 as v23 (every image bump passes both CA jobs, item 35) |
| Y | Shipped text and records | as v23 § 5 | 11 | as v23 | as v23 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v23 | as v23 |
| U | Live checks and user | as v23 § 5 | 6 | as v23 | as v23 (K-20 keeps the refused-call, launch and refused-read checks) |
| **AB** | Opencode permission, third round: the T855 residuals and their evidence runs | SEC-T856-02 (narrowed); **new:** SEC-T862-02. **Left:** SEC-T856-01, SEC-T856-03 (fixed) | 2 | devops-engineer (generator, tests and docs; the orchestrator assigns) | the next change to the Opencode permission generator or its docs, or the next `mcp-agent-denials-evidence` run, whichever comes first; check at next-release preparation with item 49 |

Total 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 6 + 11 + 2 + 6 + 2 = **116** = 115 tracked-LOW + 1 open (K-20). Against v23's 121: X - 6 + 2, AB - 2 + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Why X for SEC-T860-01 and SEC-T860-02.** Both sit in `docs/wiki/mcp-pin-bump-checklist.md`, the document batch X's ids already live in and that T859 just edited: -02 is an addition to the very runner steps of SEC-T811-05 (X) and is applied by the user together with them; -01 is a rule for the pin bump that fixed SEC-T756-07 (X), with the same owner and the same review cadence. Y is for shipped text in general; keeping them in X keeps one owner and one trigger for the checklist.

**Why AB for SEC-T862-02.** It is a gap in `T861EvidenceRedactionTests`, the test that fixed SEC-T856-01 (AB), and its trigger is the next evidence run, which is AB's trigger. Letters are not reused, and a new letter for one id would split one surface (v12 Metadata).

**Order, my suggestion only.** v23 § 5 stands, with these changes: in X, SEC-T860-02's two sentences first (cheap, and the user's runner steps are incomplete without them), then SEC-T860-01 before the next `npx` pin bump; in AB, SEC-T862-02 with the next evidence run, SEC-T856-02's remainder stays accepted as T862 § 2.3 rules.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v23 § 6.1 stand and stay the record, unchanged. **The MEDIUMs accepted for v11.0.0 only are SEC-T660-01 and SEC-T665-01**, review **2027-01-28** (token renewal). None accepted since v23. No agent accepted a risk.

**The python pin decision (not a risk acceptance).** `python:3.12-alpine` now resolves to a new index whose only changed entry is `linux/riscv64`; the `linux/amd64` manifest is byte-identical, and all CI jobs are x86-64 (v13). The pin is kept: the orchestrator's ruling after its own registry check, confirmed by the user, "Refresh, keep python pin (Recommended)" (plan-177 § Outcome (a)). The registry checks were not re-run here **(unverified)**.

### 6.2 Next release checklist (the release after v11.0.0)

v23 § 6.2 (through it v22 to v17 § 6.2) stands, with one change in item 49:

- **Item 49 (restated from T862 § 4; narrower, not closed): SEC-T660-01's scope on Opencode for the acceptance at the next release.** It stays the user-accepted MEDIUM under ADR-011, with its review on **2027-01-28**. On Opencode, these can still read the GitLab token:
  - (a) every generated agent that holds `execute` (15), through its shell (unchanged);
  - (b) Opencode's built-in agents and agent files of the user's own (K-23) (unchanged);
  - (c) the two orchestrators, indirectly, through their named shell-holding subagents (unchanged);
  - (d) **changed**: for the 13 generated agents without `execute`, **covered**: `read` is denied for any directory named `gitlab-mcp`, and since T861 `external_directory` is denied for any target inside a directory named `gitlab-mcp` outside the project; together they cover `read`, `grep` and `glob` on the default token directory, also under a broad user allow (resolved lists, evidence v4; a refused call not observed, K-20). **Not covered**: a `grep` on a parent directory such as `/dev/shm` or `/run/user/<uid>` (guarded only by that parent's `external_directory` rule: default `ask`, `allow` under a broad user rule; SEC-T856-02); a token at a non-default name or path; a token linked or copied into a project.

  No fix is possible in the harness for (a) and (b). The counts stay as v20 checked them: 15 with `execute`, 13 without. The acceptance question at item 43 uses this scope.

Count: the numbers of v23 stand; item 49 keeps its number with a narrower (d).

### 6.3 Dates

- **2027-01-28**: SEC-T660-01 and SEC-T665-01 review (token renewal). Unchanged.
- **2027-01-29**: TD-T697-07 ends. Unchanged.
- **2027-03-20**: the CI image review date fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml` line 25, read here; the test fails at an age of more than 120 days, so 2027-03-19 is the last passing day). **Changed** from 2027-03-12 (section 4.3). Re-review the digests before it.

## 7. User actions

v23 § 7 stands, with these additions:

- **SEC-T811-05 with SEC-T860-02: harden the release-gate runner** (checklist § 3, "Release-gate runner hardening"; an agent changes nothing on the runner or its host). Read `gitlab-runner --version` first and check the option names in that version's documentation. Then:
  1. **Services** (written, step 1): in `[runners.docker]` add `services_limit = 0`; keep `privileged = false`; set no `allowed_privileged_services`; restart the runner and check that the next tag pipeline's three jobs still start.
  2. **Check that it takes effect** (SEC-T860-02 (a); **not yet written** in the checklist): after the restart, check the runner log for an unknown-key warning, and record the runner version in the image-review row of checklist § 5.
  3. **Patching** (written, step 2): at every CI image review, update Docker Engine and GitLab Runner inside the LXC and the Proxmox VE kernel on the host (then reboot), and record the three versions in § 5. **Out-of-cycle** (SEC-T860-02 (b); **not yet written**): patch at once for a critical runc, Docker Engine or kernel container-escape advisory, with 120 days as the ceiling.
  4. **Nothing else in that LXC** (written, step 3): no other runner, service, cron job or user.
- **Optional: remove `/tmp/evidence-run`**, the neutral evidence root T861 created (scratch copies and the Opencode binary; plan-178 § Outcome). It still exists (read here, existence only).

K-20 / A-7 stays open.

## 8. Method, limits and validation

- **Carried statuses**: v23's rows and lists, plus the sources in Based on. Plan-179 § Facts is the only source for the merges (!701, !702, !703), the suites (2799 OK at `c6f65f43`, 2815 OK at `9f1b46cd`, skipped=25), the pipelines, the root refreshes T863 and T864 (drift `[]`) and the ledger count. `docs/tasks/completed-tasks.md` holds 661 task rows and `active-tasks.md` one (T865) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 3569 lines added in `aedc43f0..4ad619a1` outside `tests/golden/` and `.vscode/` (there is no diff in either), and set against the text of registers v1 to v23; the result is section 1.2. Tokens inside the raw evidence prompt text were classified by the hunk's file, not by reading the files.
- **Counting**: 5 new ids, 10 status changes into `fixed` (8 tracked-LOW, 2 new). Section 5 expands to 116 ids; the sizes of unchanged batches are v23's, not recounted id by id here; X was traced.
- **Still unverified**:
  - Carried from v23 § 8.
  - The orchestrator's registry check of the python indexes and its SPKI recomputation (plan-177 § Outcome; not re-run here).
  - T861's evidence v4 and the orchestrator's parser comparison (plan-178 § Outcome).
  - SEC-T862-02's line numbers (T862's; the test file was not opened here).
  - The orchestrator's suites and pipelines (plan-179 § Facts; not re-run here).
  - The batch membership behind "as v23 § 5".
- **Not run here**: the suite, the pipelines, the generator, Opencode, the CA jobs.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v23.md`; `plan-179-tracked-debt-register-v24.md`; `docs/tasks/task-T865.md`; `plan-177-batch-x-ci-images-ca-runner.md` and `plan-178-batch-ab-opencode-third-round.md` (§ Outcome); `security-review-t860-batch-x-v1.md` (§ 4, § 5, § Per-finding statuses, § Findings); `security-review-t862-batch-ab-v1.md` (§ 2.3, § 3, § 4, § 5);
  - by grep or line read: `docs/wiki/mcp-pin-bump-checklist.md` (lines 24, 26, 36, 38); `docs/wiki/mcp-servers.md` (the `f9f3a86b` hunk); `docs/artifacts/ca-check-t767-v2.md` (grep only); `.gitlab-ci.yml` line 25; `tests/functional/test_ci_hash_pins.py` (the age rule); registers v1 to v23 (the token scan, batch X history); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat` and `-U0` of `aedc43f0..4ad619a1` (added lines only, for the token scan); `git merge-base --is-ancestor` for `17f16d36` and `f9f3a86b`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
