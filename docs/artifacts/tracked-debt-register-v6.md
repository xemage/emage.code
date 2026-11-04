# Artifact: tracked-debt-register-v6.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v5.md` (500 ids; v5 stays the record for the text of every id that did not change, and, with v1 to v4, for every id that was `fixed` or `obsolete` there); `docs/plans/plan-132-tracked-debt-register-v6.md` and `docs/tasks/task-T733.md` (the user's "Register v6"); `docs/plans/plan-131-batch-g-release-tooling.md` (§ Task Decomposition, § Not changed in this plan, § Outcome); `docs/artifacts/security-review-t730-t732-batch-g-v1.md`; `docs/tasks/completed-tasks.md` (rows T730 to T732). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (Accepted 2026-11-01), DEC-T681-1, D-T700-1; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T733 (plan-132; the user's answer of 2026-11-04, verbatim: "Register v6"). **Date**: 2026-11-04.
- **Tree read**: branch `agent/tech-lead/T733` at `7e97b812` (develop `17dc1533` plus the plan-132 commit). The commits since v5's merge `3f420520` are `913a8de7` (batch G, squashed), its merge `17dc1533`, and `7e97b812`. No path under `implementation/` changed (`git diff --stat`). The CWSO repository was not read: every CWSO status carries over from v5.
- **Review mode**: read-only. A closure cites a completed-task row, a plan outcome, a review artifact or a grep on `7e97b812`. "Unchanged" means no task, review or plan outcome since v5 names the id, checked by searching the lines added in `3f420520..7e97b812` for every carried id. The code was not re-checked unless a grep is cited. Anything not traced is **(unverified)**.
- **Reviewed tree**: the final re-check read `c86c1781`; `git diff --stat c86c1781 913a8de7` lists only the review record, the plan, the ledger and the three briefs, so the reviewed code is the merged code.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`, the CWSO repository. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5.
- **Batch letters**: G is executed (plan-131). H, I, J, K, L, M, F and U keep their v5 scope. **N**, **P** and **Q** are new (section 5). O is skipped, so that it does not read as the ruling ids `O1` and `O-1` to `O-12`.

## 1. Summary

v6 holds **517 ids**: the 500 of v5 and **17 new**. After v6: **398 fixed**, **46 accepted**, **6 obsolete**, **1 open**, **66 tracked-LOW**.

- **Open above LOW: none.** The one open id is K-20 (live checks, user). All 17 new ids are LOW (review: 0 CRITICAL, 0 HIGH, 0 MEDIUM). The five accepted MEDIUMs (section 6.1) are accepted, not open; under ADR-011 four of them need the user's new acceptance at the next release (section 6.2, item 2).
- **Batch G's 14 ids**: 11 fixed, 1 accepted, 2 stay tracked with a new home (SEC-T702-08 in batch P, TD-T723-01 in batch Q). 11 + 1 + 2 = 14.
- **This register takes over the condition of the batch G review**: "the eleven remaining LOW findings be tracked as debt". They are batch N.

Arithmetic, from the v5 totals:

| Status | v5 | leaves | enters | v6 |
|---|---:|---|---|---:|
| fixed | 381 | | + 11 batch G + 6 new | **398** |
| accepted | 45 | | + 1 TL-T708-07 | **46** |
| obsolete | 6 | | | **6** |
| open | 1 | | | **1** |
| tracked-LOW | 67 | - 11 fixed - 1 accepted | + 11 new | **66** |
| **all** | **500** | | + 17 new ids | **517** |

Check: 398 + 46 + 6 + 1 + 66 = 517. Open or tracked: 66 + 1 = 67, the size of section 5.

### 1.1 Ids by v5 status and status now

| v5 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 67 | 11 | 1 | 0 | 0 | 55 |
| accepted | 45 | 0 | 45 | 0 | 0 | 0 |
| fixed | 381 | 381 | 0 | 0 | 0 | 0 |
| obsolete | 6 | 0 | 0 | 6 | 0 | 0 |
| **all v5 ids** | **500** | **392** | **46** | **6** | **1** | **55** |
| new in v6 | 17 | 6 | 0 | 0 | 0 | 11 |
| **all v6 ids** | **517** | **398** | **46** | **6** | **1** | **66** |

### 1.2 New ids by source

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t730-t732-batch-g-v1.md`, T730 | 6 | 3 | 3 |
| same, T731 | 9 | 3 | 6 |
| same, T732 | 2 | 0 | 2 |
| **All new** | **17** | **6** | **11** |

A search of the lines added in `3f420520..7e97b812` finds no other new id: plan-131, briefs T730 to T732, `ci/js/README.md` and the changed code and tests mint none. This register mints none.

## 2. v5 ids re-checked

Every v5 `open`, `tracked-LOW` and `accepted` id (113) has a row or a list entry here: 1 + 67 + 45. The v5 `fixed` and `obsolete` ids stay as v5 records them.

### 2.1 v5 `open` (1)

K-20: **Unchanged**, open, batch U (A-7).

### 2.2 v5 `tracked-LOW` (67)

**Changed or re-homed (14, batch G; plan-131; rows T730 to T732; "review" is `security-review-t730-t732-batch-g-v1.md`)**

| Id | v5 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-T716-01 | tracked-LOW | **fixed** | - | T730: exact refs, read by object id; review § 1 "Correct"; `check-main-develop-drift.py:68` (grep); shadowing-tag test in `test_check_main_develop_drift.py`. |
| SEC-T716-02 | tracked-LOW | **fixed** | - | T730: reserved Default_Ignorable ranges by number; review § 1 "Correct and complete for Unicode 15.0"; Unicode version asserted, `test_publish_release_t730.py:77` (grep). |
| SEC-T716-03 | tracked-LOW | **fixed** | - | T730: sigils escaped, URL-shaped tokens in code spans; review § 1 "Correct for CommonMark". Live GitLab **(unverified)**. Documented residual without an id: an e-mail address can still autolink as `mailto:` (`publish-release.py:442`; review, Correction). Residual SEC-T730-06. |
| SEC-T716-04 | tracked-LOW | **fixed** | - | T730: `ApiCredential` is a `__slots__` class (`publish-release.py:629, 637`, grep); review § 1 "Effective for every form tested". Residual SEC-T730-03. |
| SEC-T716-05 | tracked-LOW | **fixed** | - | T730: markdown-it-py 4.2.0 in the CI lock (`ci/requirements-ci.txt:405`, grep); the CommonMark test fails under CI. Resolves v5's **(unverified)** on the CI install. |
| SEC-T715-01 | tracked-LOW | **fixed** | - | T731: more pointer forms fail. Residuals SEC-T731-03, -04. |
| SEC-T715-02 | tracked-LOW | **fixed** | - | T731: a prose pointer on a Cursor line needs the item (docstring, `verify-release-docs.py:430-433`). `--tag v9.0.0` passes on `7e97b812` (run). |
| SEC-T715-03 | tracked-LOW | **fixed** | - | T731: raw HTML blocks blanked; review § 1. Residual SEC-T731-09. |
| SEC-T715-04 | tracked-LOW | **fixed** | - | T731: printed lines sanitised (`verify-release-docs.py:581-582`, grep). Residual SEC-T731-05. |
| SEC-T676-14 | tracked-LOW | **fixed** | - | T730: `--exclude-newer 2026-10-22T12:00:00Z`, generated 2026-11-02, so an 11-day cooldown (`ci/requirements-ci.txt:2-4`, grep; review § 1). Residual SEC-T730-04. |
| SEC-T677-01 | tracked-LOW (narrowed) | **fixed** (JavaScript) | - | T732: JavaScript measured with acorn 8.19.0; review § 1 "acorn supply chain". **Bash is still measured line by line, and its two gaps stay in the guard's docstring** (`tests/functional/test_function_size.py`, grep): a body that is a subshell, `name() ( ... )`, and a closing brace at another indentation than its header (that one fails closed as unclosed). They have no id. Residuals SEC-T732-01, -02. |
| TL-T708-07 | tracked-LOW | **accepted** | - | The user, 2026-11-02: "Accept as is (Recommended)"; basis D-T700-1 "Exclude docs/decisions/ (Recommended)" (plan-131 § Not changed, § Outcome). Grade LOW; no end date set. This records the basis v5 asked for. |
| SEC-T702-08 | tracked-LOW | tracked-LOW | **P** | The user, 2026-11-02: "Keep it tracked" (plan-131). Resolves v5's **(unverified)** on the user's answer. Upstream code: no timeout or size cap on the Brave API fetches. Not covered by acceptance v3, which names it as a "Separate upstream finding" (`brave-audit-acceptance-v3.md:47`). |
| TD-T723-01 | tracked-LOW | tracked-LOW | **Q** | Plan-131 § Outcome: "For the next release document". Owner release-manager. `install.sh` did not change in batch G (`git show --stat 913a8de7`). See section 6.2, item 4. |

**Unchanged (53 tracked-LOW; v5 §§ 2 and 3 stay the record of their text)**

| Batch | Ids | n |
|---|---|---:|
| H | SEC-T720-02, SEC-T720-03, SEC-T720-04, SEC-T720-05, SEC-T720-06, SEC-T720-07, SEC-T720-08, TD-T720-01, TD-T725-01, TD-T671-legacy, SEC-T693-07 | 11 |
| I | SEC-T722-01, SEC-T722-02, SEC-T722-03, SEC-T722-04, SEC-T722-05, SEC-T725-01, SEC-T725-02, SEC-T725-03, SEC-T724-01, TD-T724-01 | 10 |
| J | SEC-T663-02 | 1 |
| K | SEC-T714-02, SEC-T714-04, SEC-T714-06, SEC-T714-08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 |
| L | SEC-T726-01, SEC-T726-02, SEC-T726-03, TD-T726-01, TD-T726-02 | 5 |
| M | SEC-T727-01, SEC-T727-02, SEC-T727-03, SEC-T727-04, SEC-T727-05, SEC-T728-01, SEC-T728-02, SEC-T728-03, TD-T728-01, TD-T728-02, TD-T728-03, SEC-T696-07 | 12 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 5 |

Total 53; with the 14 above, 67. TD-T728-02 is named since v5 only for its date, by plan-132 (section 6.3).

### 2.3 v5 `accepted` (45)

**All unchanged**; basis as in v5 § 2.3. The one mention since v5 is TD-T671-FN2, in the scope line of the rewritten docstring of `test_function_size.py`, which changes nothing.

- **MEDIUM (5)**: SEC-T657-01 / SEC-T658-01 (one id), SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07.
- **LOW or INFO (40)**: K-2b, TD-T687-01, SEC-014, RO621-N-1, TD-T671-FN2, SEC-T657-04, K-15, SEC-T660-05, SEC-T650-03, T636-L6, T636-L7, TD-T671-K7, R-1, K-4 limits, CR619-N5, K-10, GOLDEN_VERSION_LABEL, T638-L-1, K-13, K-19, RO621-N-4, RO621-N-5, RO621-O1b, RO621-O5c, TL-T649-09, SIGNOFF-CR649, K-14, K-21, SEC-T662-05, SEC-T667-03, SEC-T667-06, SEC-T686-05, TD-T697-01, TD-T697-02, SEC-T702-01, SEC-T702-02, SEC-T702-03, SEC-T702-04, SEC-T702-05, SEC-T702-06.

## 3. New ids

Source: `security-review-t730-t732-batch-g-v1.md` (§ 2 resolved, § 4 tracked; the reviewer's fix for each is in § 4). All LOW. Line numbers are the reviewer's. Where the review gives them at `3a4bfd4c`, the current line is added from a grep on `7e97b812`.

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T730-01 | LOW | `publish-release.py:450-451, 506-531` | Two URL shapes in commit subjects stayed bare. | fixed (`c3004758`) | - | - |
| SEC-T730-02 | LOW | `publish-release.py:451, 457-469, 496` | `URL_TOKEN_RE` was quadratic. | fixed (`c3004758`) | - | - |
| SEC-T730-03 | LOW | `publish-release.py:562-586, 683` at `3a4bfd4c`; now `:629` (class), `:750` (token in `main()`) | `object.__getstate__()` and `copyreg` or `dispatch_table` registrations still expose the token; `main()` keeps it in a plain local, shown by a traceback that captures locals. All need deliberate in-process calls. | tracked-LOW | devops-engineer | N |
| SEC-T730-04 | LOW | `ci/requirements-ci.in`, `ci/requirements-ci.txt:2-4` | No test enforces the 7-day cooldown or the 14-day minimum age. | tracked-LOW | devops-engineer | N |
| SEC-T730-05 | LOW | `publish-release.py:447, 480, 498` | Over-long backtick runs were kept as code spans. | fixed (`8de05af1`) | - | - |
| SEC-T730-06 | LOW | `publish-release.py`, fallback after the re-parse (now `:537-538`) | The fallback leaves a bare URL rather than failing closed, and a test expects that. No input that reaches it is known. | tracked-LOW | devops-engineer | N |
| SEC-T731-01 | LOW | `verify-release-docs.py:485` | A type 7 HTML block was not blanked after a non-paragraph line. | fixed (`55974ffe`, `15807302`) | - | - |
| SEC-T731-02 | LOW | `verify-release-docs.py:260, 506, 537`; refusal `:384-402` | `str.splitlines()` split at more characters than CommonMark. | fixed (`55974ffe`, `55e663ee`) | - | - |
| SEC-T731-03 | LOW | `verify-release-docs.py:142, 146` at `3a4bfd4c` | Two `POINTER_LIKE_RE` alternatives are quadratic on long lines. The input is the reviewed `install.sh`. | tracked-LOW | devops-engineer | N |
| SEC-T731-04 | LOW | `verify-release-docs.py:141-148` at `3a4bfd4c` | False negatives: variable-built names, `9.0.0.md` without a `v`, `rel-notes`, `/-/tags/` URLs, `CHANGELOG`/`NEWS`, homoglyphs. | tracked-LOW | devops-engineer | N |
| SEC-T731-05 | LOW | `verify-release-docs.py:183` at `3a4bfd4c`, now `:198`; `check-release-tag-tree.py:48` | `UNSAFE_RE` misses U+00AD, U+180E, U+FFF9-FFFB, the tag characters and unassigned code points. | tracked-LOW | devops-engineer | N |
| SEC-T731-06 | LOW | `verify-release-docs.py:490-492, 525, 536-543` | An anchor inside a multi-line inline construct counted. | fixed (`15807302`) | - | - |
| SEC-T731-07 | LOW | `verify-release-docs.py:435` (read: `text.splitlines()`); list at `:622` holds no `install.sh` | `install.sh` is outside the line-separator refusal, so a U+2028 between a pointer and the word Cursor drops the Cursor requirement. | tracked-LOW | devops-engineer | N |
| SEC-T731-08 | LOW | `verify-release-docs.py:265` (read) | The section ends only at a line starting `## `; a setext heading, ` ## Next` or `##\tNext` does not end it, so an anchor in the next section counts. Visible, in the wrong section. Older than this batch. | tracked-LOW | devops-engineer | N |
| SEC-T731-09 | LOW | `verify-release-docs.py:522, 156-157`; claims at `:479, 534` | A false PASS is still possible when the gate hides too much: (a) a comment or processing instruction that CommonMark closes on its first line stays open in the gate; (b) the gate pairs two fences that CommonMark does not. The "never a false PASS" claims are not strictly true. | tracked-LOW | devops-engineer | N |
| SEC-T732-01 | LOW | `.gitlab-ci.yml:93-104` at `3a4bfd4c` (`npm ci` still `:104`, socket `:97`) | npm and acorn run in `unit-tests`, the job that binds the host Docker socket. The package is bound by sha512, but npm is pinned to a major version only and acorn has no provenance attestation. | tracked-LOW | devops-engineer | N |
| SEC-T732-02 | LOW | `ci/js/README.md:39-43` | The 14-day minimum age for acorn is only a manual rule. | tracked-LOW | devops-engineer | N |

## 4. Decisions since v5

### 4.1 The user's (words verbatim as recorded)

| Date | Words | Effect | Source |
|---|---|---|---|
| 2026-11-02 | "G go" | plan-131 (T730 to T732) | plan-131 Based on |
| 2026-11-02 | SEC-T702-08: "Keep it tracked" | Stays tracked-LOW; batch P | same; § Not changed |
| 2026-11-02 | TL-T708-07: "Accept as is (Recommended)" | Accepted; basis D-T700-1 | same |
| 2026-11-02 | SEC-T677-01: "Add a JS parser" | T732, acorn | same; § Task Decomposition |
| 2026-11-02 | "Fix now in this batch (Recommended)" | The three gaps the first review named were fixed in batch G. Which ids they are: section 8 | plan-131 § Outcome; row T730 |
| 2026-11-04 | "Allow its reads (Recommended)" | The reviewer's refused reads went ahead in the final re-check; the cause of the first refusal was not established | plan-131 § Outcome; review Metadata |
| 2026-11-04 | "Fix the three now (Recommended)" | SEC-T731-01, SEC-T731-06, SEC-T730-05 fixed | plan-131 § Outcome |
| 2026-11-04 | "Register v6" | plan-132, T733 (this register) | plan-132 Based on |

### 4.2 Other decisions (not the user's)

| Id | Decision | By | Effect |
|---|---|---|---|
| TD-T723-01 | Handled in the next release document | plan-131 § Not changed | batch Q |
| Batch N | The 11 tracked batch G findings form a new batch | plan-132 | section 5 |
| Batches P and Q | SEC-T702-08 and TD-T723-01 get a batch each, because their owners and triggers differ and H to U keep their v5 scope | tech-lead (T733) | section 5 |

## 5. Open items by LOW batch

"Do first" as in v5; for SEC-T722-03, SEC-T725-02, SEC-T727-01/-02 and SEC-T728-01 the flag's source stays **(unverified)**, as v5 § 5 says. SEC-T716-01, the one v5 traced, is fixed. H, I, J, K, L, M, F and U are carried from v5 without change, except that TD-T728-02's date has now been reached.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| H | Release-gate knowledge text and ADR-011 follow-ups | SEC-T720-02 to -08, TD-T720-01, TD-T725-01, TD-T671-legacy (P10; parked P14, P15, T539, T565), SEC-T693-07 | 11 | orchestrator routes; solution-architect or the user (SEC-T720-02, -03: superseding ADR); technical-writer; devops-engineer (re-pins of `test_release_self_review_text.py`) | before the next release for SEC-T720-02 to -05, -08 and TD-T725-01 (they shape that release's gate and migration note); the parked TD-T671-legacy items need a protected-path grant |
| I | Installer and generator | **SEC-T722-03 (do first)**, **SEC-T725-02 (do first)**, SEC-T722-01, -02, -04, -05, SEC-T725-01, -03, SEC-T724-01, TD-T724-01 | 10 | devops-engineer; backend-developer (SEC-T724-01, TD-T724-01) | next installer or generator change; SEC-T725-02 before the release that ships T725 (recommendation) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | devops-engineer | its own task (five test files, documents and live evidence change; plan-128) |
| K | Security runtime (`security-audit` servers) | SEC-T714-02, -04, -06, -08, SEV-T690-02 (pinned runtime package), SEV-T690-04 ((d) Copilot), SEC-T665-07 (if reopened) | 7 | devops-engineer; technical-writer (wiki residual of SEC-T714-06) | next change to `implementation/runtime/security/`; SEC-T665-07 on its reopening conditions |
| L | CWSO helper scripts in emage.code | SEC-T726-01 to -03, TD-T726-01, TD-T726-02 | 5 | devops-engineer | next change to the CWSO helper scripts; TD-T726-02 before the next Proxmox setup |
| M | CWSO repository | **SEC-T728-01 (do first)**, **SEC-T727-01, -02 (do first)**, SEC-T727-03 to -05, SEC-T728-02, -03, TD-T728-01 to -03, SEC-T696-07 ((b) fuel/epoch) | 12 | devops-engineer (CWSO; agent branch from CWSO `origin/develop`, MR into CWSO `develop`) | next CWSO change; TD-T728-02 adoptable since **2026-11-04**; TD-T728-01 in the next CWSO release notes; SEC-T696-07(b) before untrusted modules are accepted |
| **N** (new) | Release tooling, second round (`publish-release.py`, `verify-release-docs.py`, CI locks and the npm step) | **SEC-T731-09**, SEC-T730-03, -04, -06, SEC-T731-03, -04, -05, -07, -08, SEC-T732-01, -02 | 11 | devops-engineer (review § 4) | next fixing round (review § 4: "next sprint"); no source binds it to a release; see below |
| **P** (new) | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines; the orchestrator offers the draft (plan-126) | when the user reopens it: "Keep it tracked" sets no date. The natural next look is the Brave review of section 6.3 (tech-lead's suggestion; no source sets it) |
| **Q** (new) | Next release document | TD-T723-01 | 1 | release-manager | the next release document (section 6.2, item 4) |
| F | PoC scanner (unchanged) | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06 | 6 | the user or an authorised live session; orchestrator (process rule) | A-2, A-7, A-11, A-15 |

Total 11 + 10 + 1 + 7 + 5 + 12 + 11 + 1 + 1 + 2 + 6 = 67 = 66 tracked-LOW + 1 open. No open item is above LOW.

**Batch N, in short.**

- **SEC-T731-09(a) is the one-line fix the reviewer gave**: at `verify-release-docs.py:522` change `block[0].search(line, block[1])` to `block[0].search(line)` (line read on `7e97b812`; the fix is not run here). Its false PASS needs a **crafted release document**, one that holds such a comment together with an anchor. Part (b) needs `markdown-it-py` in the gate or a documented residual, and the two claims at `:479, 534` need correcting either way.
- **SEC-T731-07**: the reviewer's fix is one more entry in the `check_line_breaks` list. It too needs a crafted file, here a crafted `install.sh`.
- **Recommendation (tech-lead, no source sets this)**: do SEC-T731-07 and SEC-T731-09(a) before the next tag, because both are small and the next release runs this gate. It is not a condition; the review passed with them tracked.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 § 6.1 stands unchanged and stays the record, including its reading of ADR-011 and the note on what the v9.0.0 verdict names. One row is added:

| Item | Grade | Words, date | Until |
|---|---|---|---|
| TL-T708-07 | LOW | "Accept as is (Recommended)", 2026-11-02; basis D-T700-1 "Exclude docs/decisions/ (Recommended)" | no end date set (plan-131). ADR-011 concerns MEDIUM findings, so it does not apply |

The MEDIUM end dates: TD-T697-07 **2027-01-29**; SEC-T702-09 pin audit **2027-01-30 or the first Brave release above 2.1.4**; SEC-T702-09, SEC-T660-01, SEC-T665-01 and the SEC-T657-01/SEC-T658-01 remainder: **the next release needs the user's new acceptance** (ADR-011).

### 6.2 Next release checklist

Items 1 to 3 and 5 to 7 are carried from v5 § 6.2. Item 4 loses what batch G did: SEC-T716-01 and SEC-T715-01/-02 are fixed. Items 8 and 9 are new.

1. **Migration item T725 (TD-T671-P5)** in the release document: authoring-only commands are no longer installed into target projects; commands declare `audience: authoring | target | both`; today only `/prepare-release` (five platform paths listed in plan-128 § Outcome); `--update`/`--projections-only` deletes an existing copy (a dry run prints the `rm`); an authoring checkout (`implementation/registry/index.json`) keeps them; a target that used `/prepare-release` keeps its own copy under another file name; `.generated-manifest.json` gains `authoringOnly`; the generator refuses a command without a valid `audience:`. Fix TD-T725-01 with it.
2. **ADR-011 re-acceptances**: the Release Gate input lists every MEDIUM an earlier release shipped under the user's acceptance and not yet fixed (SEC-T720-01 fix, `validation-gates/SKILL.md`): **SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09**. Each one is fixed, or the user accepts it again for this release, verbatim and dated, with its remediation plan (owner, fix, deadline). No agent grants or carries one over.
3. **New verdict fields** (R4, R10): `Issued at commit` and `Independent check` (`docs/releases/_template.md:87-88`; `prepare-release.md:59-60`). The independent check row must be present, current and not FAIL (SEC-T693-02).
4. **TD-T723-01 (batch Q)**: the release document cites current `install.sh` lines. `docs/releases/v9.0.0.md:86` cites `install.sh:1300`, and `:75` cites `install.sh:1285-1302`, which v5 did not mention. On `7e97b812` the advice is `scripts/install.sh:1297-1300` and the pointer is `:1301`; re-read them when the document is written.
5. **Batch H items that shape the gate**: SEC-T720-02, -03 (need the user or a superseding ADR), -04, -05, -08, if they are to apply to this release.
6. **Brave**: if the release falls after 2027-01-30 or after a Brave release above 2.1.4, the pin audit needs a new acceptance version or the bump first.
7. **D-T710-2**: confirm in the release job that the `CHANGELOG.md` entry lands below `[Unreleased]` (fixed in code by T716; not yet observed in a tag pipeline).
8. **Visible changes of batch G** (plan-131 § Outcome), for the release document and its author:
   - `CHANGELOG.md` entries now show `\#42`, `\@user` and URLs in backticks in their source, and `(#42)` no longer links to the issue.
   - Release documents need a blank line or an ATX heading before the Cursor item, and no trailing comment on `## Migration Guide`. Those shapes are deliberate false FAILs. The "lacks its Cursor migration item" message does not mention the blank-line rule; `--help` does (review § 1).
   - Checked documents may not contain `\v \f \x1c-\x1e \x85 U+2028 U+2029`. They are the tag's release document and the three marker files (`verify-release-docs.py:41-45, 622`).
9. **Not verified live in plan-131; watch these in the release**:
   - how GitLab renders the escaped references and code spans;
   - the npm step (`npm ci --ignore-scripts --prefix ci/js`) in a tag pipeline;
   - the lock on the musl image beyond the MR pipeline.

### 6.3 Dates

| Date | What | Ids, action |
|---|---|---|
| **2026-11-04** (today) | Trivy 0.76.1 can be adopted in CWSO CI. Adoption not traced; CWSO not read **(unverified)** | TD-T728-02 (batch M) |
| **2027-01-28** | GitLab token renewal | A-13 |
| **2027-01-29** | CWSO bearer renewal; **end of TD-T697-07** (renewed with the new token by the user) | A-13, TD-T697-07 |
| **2027-01-30** | End of Brave acceptance v3 (or the first Brave release above 2.1.4) | SEC-T702-09, SEC-T702-01 to -06 |
| ~~2027-01-31~~ | CWSO `paste` review: **closed** (`paste` removed by T728) | SEC-T696-06 fixed |

The token dates repeat v5, which did not re-read them; nor did I **(unverified)**.

## 7. User actions

Carried from v5 § 7. Plan-131 adds none and closes none; I did not re-check any state.

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

- **Carried statuses**: v5 rows plus plan-131, rows T730 to T732 and the batch G review. Greps on `7e97b812` where cited. A script reproduced v5's 67 tracked-LOW, 45 accepted and 1 open from its rows, and took the carried id list from them.
- **Counting**: a script checks that each of those 113 ids occurs in sections 2.1 to 2.3 of this register, counts the rows of sections 2.2 and 3 by status, and expands section 5 to 67 distinct ids, equal to the carried ids still open or tracked plus the 11 new.
- **Where the sources differ or leave a gap** (none changes a status):
  - Plan-131 § Outcome does not name "the three gaps the first review named". Row T730 puts SEC-T730-01, -02 and -05 under the two answers together; `55974ffe` closes SEC-T731-01 and -02 in the same round, and `15807302` closes "SEC-T731-01 rest" after "Fix the three now (Recommended)". Which three ids the first answer covered is **(unverified)**.
  - The review's lines marked "at `3a4bfd4c`" have moved in part (section 3 adds the current ones). SEC-T731-09's `:522` is exact on `7e97b812`.
  - Review § 5 says `main()` of `verify-release-docs.py` rests on the exported diff; the `check_line_breaks` call is at `:622` on `7e97b812` (grep).
  - Review § 4 gives the trigger "next sprint". Batch N reads that as the next fixing round.
- **Residuals without an id** (not minted here; no plan-131 artifact mints them, and the parents are recorded fixed): the `mailto:` autolink (SEC-T716-03) and the two Bash gaps (SEC-T677-01). The missing blank-line hint is in section 6.2, item 8. The review also records that pip-audit did not run on the CI lock; the reviewer compared markdown-it-py and mdurl with PyPI's hashes and vulnerability data instead.
- **Unverified**, carried from v5: the T547 remark of TD-T671-legacy; the source of the "do first" flags other than SEC-T716-01; whether the runner sets a variable T716 drops; D-T710-2 in a real release job; Docker 29.9.2 on Ubuntu 20.04 (TD-T726-02); the Go 1.26 CA backport (TD-T728-02); the user's Docker Engine version (SEC-T727-04); the image digests (SEC-T696-04); other hosts for A-11; R-1's acceptor; the token dates.
- **Unverified**, new: the three gaps above; live GitLab rendering (SEC-T716-03; section 6.2, item 9); the npm step in a tag pipeline; the lock on the musl image beyond the MR pipeline; whether the orchestrator's draft of the upstream report was ever shown to the user (plan-131 records only the answer); adoption of Trivy 0.76.1. The reviewers' own unverified lists stand as written in their artifacts.
- **Resolved since v5**: the user's answer on SEC-T702-08; markdown-it-py in CI (SEC-T716-05).
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v5.md`; `plan-131-batch-g-release-tooling.md`; `plan-132-tracked-debt-register-v6.md`; `docs/tasks/task-T733.md`; `completed-tasks.md` rows T730 to T732; `security-review-t730-t732-batch-g-v1.md`; `brave-audit-acceptance-v3.md` line 47 and the SEC-T702-08 lines of plan-126 (by grep). v1 to v4 were not re-read. Decision IDs: ADR-011, DEC-T681-1, D-T700-1.
