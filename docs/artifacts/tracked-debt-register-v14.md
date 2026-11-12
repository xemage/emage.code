# Artifact: tracked-debt-register-v14.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v13.md` (675 ids; v13 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-152-tracked-debt-register-v14.md` (§ Facts since v13, § Task Decomposition) and `docs/tasks/task-T794.md` (the user's "v14 go"); `docs/plans/plan-150-pin-checklist-no-docker.md` (§ Outcome); `docs/artifacts/security-review-t789-pin-checklist-v1.md`; `docs/plans/plan-151-context-retriever-code-residue.md` (§ Outcome); `docs/artifacts/security-review-t791-context-retriever-v1.md`; `docs/artifacts/qa-recheck-t792-context-retriever-v1.md`; the ledger rows T788 to T793 in `docs/tasks/completed-tasks.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011 (only the user accepts a MEDIUM, for one release), as v13 cites it; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T794 (plan-152; the user's answer of 2026-11-12, verbatim: "v14 go"). **Date**: 2026-11-12.
- **Tree read**: branch `agent/tech-lead/T794` at `9c0e5a5d` (develop `325aebb4` plus the plan commit). The range for "lines added since v13" is `713a14c6..325aebb4`: 6 commits, 28 files, 1056 lines added and 36 removed, outside `tests/golden/` (which has no diff in the range). Outside the new review, plan and brief files and the ledger, the changed files are `docs/wiki/mcp-pin-bump-checklist.md` (T788), `scripts/install.sh`, `implementation/runtime/memory/{build.py,context_retriever.py,README.md}`, `implementation/knowledge/mcp/servers.yaml`, `implementation/scripts/sync.mjs`, the generated and root `.cline/mcp.json` and `.opencode/opencode.json`, `tests/_baselines/root-install-drift.json` and four test files (T790, T793). `.gitlab-ci.yml`, `implementation/PREREQUISITES.md`, `tests/functional/test_ci_hash_pins.py`, `CONTRIBUTING.md`, `docs/releases/_template.md` and the release scripts show no diff in the range, so v13's citations into them stand. The CWSO repository was not read: every CWSO status carries over from v13.
- **Review mode**: read-only. "Unchanged" means no task, review, plan outcome or ledger row since v13 names the id with a change of status, checked by searching the lines added in `713a14c6..325aebb4`, outside `tests/golden/`, for every id-like token that v13 holds (section 8). A status taken from a review is the latest source's. "Read here" means a grep, line read or `git` query on `9c0e5a5d`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository. Registers v1 to v11 were not re-read, except one grep of v12 § 6.2 and v11 § 6.2 for citations into the files changed in the range (section 6.2). No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v13.
- **Batch letters**: **Z ends** (its three open ids are fixed). **O is new** (the `context-retriever` LOW residue after T790; section 3). All other v13 letters keep their scope.

## 1. Summary

v14 holds **680 ids**: the 675 of v13 and **5 new**. After v14: **504 fixed**, **49 accepted**, **9 obsolete**, **1 open**, **117 tracked-LOW**.

- **Open above LOW: nothing.** No open id carries a `SECURITY:*` grade above LOW, and with QA-T760-01 to -03 fixed no open id carries QA's `Medium` either. The one open id is K-20 (live checks, user; no grade). TD-T774-01 and the new TD-T789-01 have no reviewer's grade; QA-T792-1 is `Low` on QA's scale. The accepted MEDIUMs (SEC-T660-01, SEC-T665-01, SEC-T702-09, TD-T697-07) are accepted, not open, and unchanged; the first three still need a fix or a new acceptance before v11.0.0 (section 6.2 item 2).
- **Plan-150 fixed SEC-T786-02** (T788, confirmed by T789 PASS) and minted **TD-T789-01** (the orchestrator's id; batch Y).
- **Plan-151 fixed QA-T760-01, -02 and -03** (T790, confirmed by T791 PASS and T792 PASS); **batch Z ends** and § 6.2 item 36's code part is done. It minted **SEC-T791-01, -02, -03** (SECURITY:LOW) and **QA-T792-1** (QA Low).
- **Due before v11.0.0** (section 6.2): as v13, plus **item 39, SEC-T791-01's migration note** (the platform identity change for Cline and Opencode). Item 36 now names what the release document reports as fixed (K-35 and M-2's caveats).
- **Not checked since v13**: SEC-T786-01's trigger (Alpine `nodejs` 24.22.3 in a `unit-tests` log). No one has read a `unit-tests` log for it since T786 **(unverified)**; plan-152 § Facts.
- **Open for the user**: as v13. A-20, A-21 and A-22; the route of SEC-T735-06 and -07; the SEC-T762-04 questions; any batch before the next tag.

Arithmetic, from the v13 totals:

| Status | v13 | leaves | enters | v14 |
|---|---:|---|---|---:|
| fixed | 500 | | + 4 (SEC-T786-02, QA-T760-01, QA-T760-02, QA-T760-03) | **504** |
| accepted | 49 | | | **49** |
| obsolete | 9 | | | **9** |
| open | 4 | - 3 fixed | | **1** |
| tracked-LOW | 113 | - 1 fixed | + 5 new | **117** |
| **all** | **675** | | + 5 new ids | **680** |

Check: 504 + 49 + 9 + 1 + 117 = 680. Open or tracked: 117 + 1 = 118, the size of section 5.

### 1.1 Ids by v13 status and status now

| v13 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 4 | 3 | 0 | 0 | 1 | 0 |
| tracked-LOW | 113 | 1 | 0 | 0 | 0 | 112 |
| accepted | 49 | 0 | 49 | 0 | 0 | 0 |
| fixed | 500 | 500 | 0 | 0 | 0 | 0 |
| obsolete | 9 | 0 | 0 | 9 | 0 | 0 |
| **all v13 ids** | **675** | **504** | **49** | **9** | **1** | **112** |
| new in v14 | 5 | 0 | 0 | 0 | 0 | 5 |
| **all v14 ids** | **680** | **504** | **49** | **9** | **1** | **117** |

### 1.2 New ids by source and final status

| Source | new | fixed | accepted | obsolete | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| `plan-150-pin-checklist-no-docker.md` § Outcome (the orchestrator's id): TD-T789-01 | 1 | 0 | 0 | 0 | 0 | 1 |
| `security-review-t791-context-retriever-v1.md` § Findings: SEC-T791-01, -02, -03 | 3 | 0 | 0 | 0 | 0 | 3 |
| `qa-recheck-t792-context-retriever-v1.md` § Observations: QA-T792-1 | 1 | 0 | 0 | 0 | 0 | 1 |
| **All new** | **5** | **0** | **0** | **0** | **0** | **5** |

**Other ids in the added lines.** A search of the lines added in `713a14c6..325aebb4`, outside `tests/golden/`, for `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `M-<n>`, `A-<n>` and `BLK-` tokens finds, besides the ids above: QA-T760-01 to -03, SEC-T786-02 and A-21 (all v13 ids; sections 2 and 7); **SEC-009** and **SEC-T676-14** (cited as the reason for an existing control, `%q` quoting and the lock cooldown; both were already in the moved checklist text; no change of status); **K-35** and **M-2** (the v10.0.0 release document's own items, cited by plan-151; not debt ids of this register); **O-1, O-2, O-3** (T789's unnumbered observations; O-1 and O-2 are parts of TD-T789-01, O-3 needs no change per T789 § 3); and `QA-T792-CANARY-*` (test body tokens in T792, not ids). No blocker record and nothing else is minted. This register mints no id.

## 2. v13 ids re-checked

Every v13 `open`, `tracked-LOW` and `accepted` id (166) has a row or a list entry here: 4 + 113 + 49. The v13 `fixed` and `obsolete` ids stay as v13 records them.

### 2.1 v13 `open` (4)

**Changed (3).**

| Id | v13 | now | Evidence |
|---|---|---|---|
| QA-T760-01 | open, QA Medium, batch Z | **fixed** | T790 (plan-151 § Outcome): `print_memory_index_notice` prints the install line for `implementation/runtime/memory/requirements.txt` before the build command, `%q`, nothing installed. T791 § Status: "fixed", `scripts/install.sh:1728-1745`. T792: the printed lines, run in order in a fresh target, exit 0 and the build exits 0; without the new line the build still fails with `ModuleNotFoundError: No module named 'yaml'` (negative check). The line is `scripts/install.sh:1735`, printed only when the file exists (`:1734`) (read here). Ledger T790 to T792 |
| QA-T760-02 | open, QA Medium, batch Z | **fixed** | T790: `build.py` refuses a `--project-id` that is not the derived lower-case `<org>/<repo>` (CLI exit 2; `BuildConfig` raises `ValueError`); `scope_filter.py` unchanged; a case-only mismatch is named on stderr, path only. T791 § Status: "fixed" (`build.py:223-224`, `context_retriever.py:134-144`). T792: `Acme/Widget` refused with exit 2 and no index written; `acme/widget` builds and `retrieve` returns the chunk over stdio. `is_derived_project_id` at `context_retriever.py:134` and its import at `build.py:31` (read here). The wider mismatch (not case-only) is SEC-T791-02 |
| QA-T760-03 | open, QA Medium, batch Z | **fixed** | T790: `servers.yaml` passes `--platform-root {{platformDir}}`, which `sync.mjs` writes per platform. T791 § Status: "fixed (in the generated tree; the root waits for its refresh)". T792: Cline-only and Opencode-only targets without `.claude/` answer `retrieve` with `isError = False`; with `.claude` the server still fails closed. T793 refreshed the root ("refresh"): root `.cline/mcp.json:122-123` passes `.cline`, `.opencode/opencode.json` passes `.opencode`, `.mcp.json` passes `.claude`, and `servers.yaml:196` holds `{{platformDir}}` (read here). The behaviour change is SEC-T791-01 |

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range names it.

### 2.2 v13 `tracked-LOW` (113)

**Changed (1).**

| Id | v13 | now | Evidence |
|---|---|---|---|
| SEC-T786-02 | tracked-LOW, batch Y | **fixed** | T788 (commit `dad17100`, squash `97491c37`) rewrote § 2 and § 3 of `docs/wiki/mcp-pin-bump-checklist.md`. T789 § 2: "Fixed: closes when T788 (`dad17100`) merges to `develop`"; all four parts of the remediation met (T789 § 1). Merged with MR !669 (plan-152 § Facts). "run the image" and "unverified until it runs" occur 0 times on the page (grep, read here). Ledger T788, T789 |

No other v13 tracked-LOW id occurs in the added lines (section 8). Two notes that change no status:
- **SEC-T756-02**: v13 cites `docs/wiki/mcp-pin-bump-checklist.md` § 3 for "any later image bump must also pass both jobs" and the `apk add` pin. T788 changed § 3, but the CA-chain paragraph (`:32`) and the `apk add` paragraph (`:34`) are still there (read here), so the citation stands.
- **SEC-T768-06** (fixed in v13 by my reading): v13 noted that the same line still carried SEC-T786-02's "run the image" text. That text is gone with T788.

**Unchanged (112 tracked-LOW; v13 and earlier stay the record of their text)**

| Batch | Ids | n |
|---|---|---:|
| I | SEC-T722-01, SEC-T722-02, SEC-T722-03, SEC-T722-04, SEC-T722-05, SEC-T725-01, SEC-T725-02, SEC-T725-03, SEC-T724-01, TD-T724-01, TD-T774-01, SEC-T762-05, TL-T753-06, SEC-T780-03, SEC-T780-04, SEC-T780-07, TL-T780-03, TL-T780-04, TL-T780-05, TL-T780-06, TL-T773-02, TL-T773-03, TL-T773-04 | 23 |
| J | SEC-T663-02 | 1 |
| K | SEC-T714-02, SEC-T714-04, SEC-T714-06, SEC-T714-08, SEV-T690-02, SEV-T690-04, SEC-T665-07 | 7 |
| L | SEC-T726-01, SEC-T726-02, SEC-T726-03, TD-T726-01, TD-T726-02 | 5 |
| M | SEC-T727-01, SEC-T727-02, SEC-T727-03, SEC-T727-04, SEC-T727-05, SEC-T728-01, SEC-T728-02, SEC-T728-03, TD-T728-01, TD-T728-02, TD-T728-03, SEC-T696-07 | 12 |
| N | SEC-T730-03, SEC-T730-04, SEC-T730-06, SEC-T731-03, SEC-T731-04, SEC-T731-05, SEC-T732-01, SEC-T732-02 | 8 |
| P | SEC-T702-08 | 1 |
| Q | TD-T723-01, SEC-T735-08, SEC-T735-09, SEC-T773-02, SEC-T780-05, TL-T780-09, SEC-T762-04, TL-T761-10, SEC-T784-01 | 9 |
| R | SEC-T735-06, SEC-T735-07, SEC-T736-01, SEC-T693-07 | 4 |
| S | SEC-T741-17 (the rest; A-20) | 1 |
| V | SEC-T748-03, SEC-T748-04, SEC-T748-05, SEC-T748-06, SEC-T748-07, SEC-T748-08, SEC-T748-09, SEC-T748-12, SEC-T751-01, SEC-T751-05, SEC-T751-06, SEC-T751-07, SEC-T751-08, SEC-T751-09, SEC-T773-01 | 15 |
| X | SEC-T756-02, SEC-T756-07, SEC-T756-08, SEC-T768-01, SEC-T768-02, SEC-T768-03, SEC-T768-04, SEC-T768-05, TL-T761-11, SEC-T786-01 | 10 |
| Y | TL-T753-05, TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T763-01, TL-T763-02, TL-T780-08 | 8 |
| F | SEC-011, SEC-T674-06 | 2 |
| U | SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06, SEC-T780-06 | 6 |

Total 112; with the 1 changed, 113. **SEC-T786-01's closing trigger was not checked** in the range (plan-152 § Facts; **(unverified)**); it stays tracked-LOW and its check stays at v11.0.0 preparation (item 37).

### 2.3 v13 `accepted` (49)

**Unchanged (49)**; no source in the range names any of them, and none has a new acceptance. As v13 § 2.3: the five rows of v12 § 2.3 with their qualifiers (SEC-T660-01, SEC-T665-01 and SEC-T702-09 accepted MEDIUM for v10.0.0 only; SEC-T657-01 / SEC-T658-01, counted as one, and K-15 close by removal at v11.0.0 unless the Opencode live check fails); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; the orchestrator-accepted residues TL-T773-01, TL-T780-01, TL-T780-07. 5 + 1 + 40 + 3 = 49.

## 3. New ids

Grades are the reviewers' own. "Read here" means a line read on `9c0e5a5d`.

| Id | Grade | Short description | Status | Evidence, what stays | Batch |
|---|---|---|---|---|---|
| TD-T789-01 | none (the orchestrator's id; no `SECURITY:*` grade) | The next edit of the image-bump checklist takes up T789's optional points: **O-1** the maintainer `docker run` names a non-production `docker --context`, or checks `docker context show` and `DOCKER_HOST` first, so a copy-paste fails safe; **O-2** name the per-platform manifest media types in § 3 step (c); **flag 3** § 2's "watch it in the next release" for `release-docs-gate` gets the v10.0.0 tag-pipeline observation and becomes "after a change of this lock, watch it at the next release or release candidate" | **tracked-LOW** | plan-150 § Outcome; T789 § 3, § 4 (T789 gives O-1 and O-2 no id and suggests a TD or TL id for flag 3). The § 2 sentence still reads "watch it in the next release or release candidate" (`docs/wiki/mcp-pin-bump-checklist.md`, read here). Owner: the next editor of the page, technical-writer (my suggestion; no source names one). Trigger: the next edit of the page | Y |
| SEC-T791-01 | SECURITY:LOW (A01) | On an install with `.claude/` beside other platform folders, Cline and Opencode sessions now resolve as `cline` and `opencode`, not `claude-code`. Shared-scope entries that name only `claude-code` are no longer returned to them; entries naming `cline` or `opencode` now are. A correction, not a widening (T791 point 2), but users see it | **tracked-LOW** | T791 § Findings. Remediation: a migration item in the v11.0.0 release notes: the platform is taken from each client's own folder; shared entries meant for every client list each platform or use `["*"]`; the root of a self-install changes only after its refresh (emage.code's own root changed with T793). Owner release-manager; **deadline the v11.0.0 release document, before the tag** | Q (item 39) |
| SEC-T791-02 | SECURITY:LOW (A09) | A project-scope entry of the own repo whose `project_id` differs from the derived id other than by case (a typo, `org/repo.git`, the top group of a nested path) is indexed and never returned, with no message. Fails closed; nothing exposed | **tracked-LOW** | T791 § Findings. `case_mismatched_paths` warns only on a case-only difference (`build.py:110-119`, read here). Remediation: warn by path for every project-scope entry whose `project_id` is not `config.project_id`, keeping the case-only wording. Owner backend-developer through the orchestrator; next sprint | O |
| SEC-T791-03 | SECURITY:LOW (A03) | `is_derived_project_id` accepts `a/..` and `a/.` and raises `AttributeError` on a non-string. Reaches no path (the slug is one directory name; `--output-dir` is separate); its only caller checks the type first | **tracked-LOW** | T791 § Findings, point 3. `context_retriever.py:134`; the caller's `isinstance` check at `build.py:53` (read here). Remediation: return False for non-strings; optionally refuse `.` and `..` segments here and in `normalize_remote_to_project_id`. Owner backend-developer through the orchestrator; next sprint | O |
| QA-T792-1 | Low (QA's scale) | Each printed install line starts with its own `python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && …`, and the printed build command has no `source` prefix. Run as separate commands, the build runs on the system `python3` (what happens then is **(unverified)**; likely the `yaml` error again) | **tracked-LOW** | T792 § Observations. The build line is `scripts/install.sh:1737`, after the venv line at `:1735` (read here). Suggestion: print one venv line, or prefix the build command with `source .venv-mcp/bin/activate &&`. Owner backend-developer through the orchestrator | O |

**My batch choices** (plan-152 leaves the letter for SEC-T791-02, -03 and QA-T792-1 to me):
- **A new batch O, not Z.** Z's scope was "`context-retriever` after M-2: code residue", bound by QA C1 to the next release. Its three open ids are fixed, and plan-151 § Outcome and plan-152 both say Z ends. Reusing Z for three LOW items with a "next sprint" window would carry a release binding they do not have. The three share one component (the memory build and its printed notes), one owner (backend-developer through the orchestrator) and one window, so they form one batch. **O** is the only single letter no register has used (grep of v1 to v13 for `batch <letter>`, read here). It is not T789's O-1 or O-2, which are parts of TD-T789-01 in batch Y.
- **Not batch I** for QA-T792-1, although it is installer text: it is the printed half of the same index-build path as SEC-T791-02, and a fix of either would be tested together.
- **TD-T789-01 → batch Y**, as plan-150 § Outcome says (shipped text and records, next docs change).
- **SEC-T791-01 → batch Q**, as plan-152 says: its deadline is the v11.0.0 release document, Q's trigger.

## 4. Decisions since v13

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-12 | "Fix SEC-T786-02" | Plan-150: T788 (writer) and T789 (security review) | plan-150; T789 header; plan-152 § Facts |
| 2026-11-12 | "Continue with the next best step" | Plan-151 (batch Z, T790 to T792). The reading as batch Z is the orchestrator's (section 4.2) | plan-151 Based on; plan-152 § Facts |
| 2026-11-12 | "resume" | The two reviews of plan-151 were resumed after a usage limit | plan-152 § Facts |
| 2026-11-12 | "refresh" | T793, the root refresh of the two declared paths | plan-151 § Outcome; ledger T793; plan-152 § Facts |
| 2026-11-12 | "v14 go" | Plan-152, T794, this register | plan-152 Based on; task-T794 |

**Still unruled, for the user (SEC-T762-04, with TL-T761-10):** as v12 § 4.1 (section 6.2, item 33).

### 4.2 The orchestrator's rulings (not the user's)

| Item | Decision | Source | Effect |
|---|---|---|---|
| The writer's two registry API details | Kept (the `Accept` media types and the `/blobs/<digest>` endpoint): they are the request shape T785 and the orchestrator used for the plan-148 reads | plan-150 § Outcome | T789 § 3 calls them correct registry API facts |
| TD-T789-01 and its three parts | The orchestrator mints TD-T789-01 (O-1, O-2, flag 3) for batch Y, with no `SECURITY:*` grade | plan-150 § Outcome | Section 3 |
| T789 § 6 item 5, the `release-docs-gate` observation | Settled: tag pipeline 3039977704, job 17831135512 ran the hash-locked install and succeeded on 2026-11-07; the lock last changed in `9e43d135` (2026-11-05), before the tag commit `d593aeb3` (2026-11-07) | plan-150 § Outcome | I confirmed the git half: `9e43d135` is the last commit to `ci/requirements-release.txt`, an ancestor of `d593aeb3`, and the lock has no diff from `d593aeb3` to `325aebb4` (read here). The job result is the orchestrator's read; I read no job log **(unverified here)** |
| The skip count | 24 skipped at `a4552400` against 25 elsewhere: `test_every_active_task_has_a_plan` skips only when the active queue is empty, and it held T790 to T792 then | plan-151 § Outcome | No status depends on it |
| The reading of "Continue with the next best step" | The word for batch Z, the first item of v13's suggested order; not approval of a release, a tag or a root refresh | plan-151 Based on; plan-152 § Facts | Plan-151. The root refresh had its own word ("refresh") |
| Batch O, and the placement of all five new ids | **Mine** (section 3) | this register | section 5 |

### 4.3 Differences on the record

These stay as the sources state them.
- **Batch Y's size.** Plan-150 § Outcome says "batch Y drops to 8". That is true without TD-T789-01; with it, Y holds 9 (section 5).
- **Two suite runs for plan-151.** Plan-151 § Outcome: 2719 OK (skipped=24) at `a4552400`. Plan-152 § Facts: 2719 OK (skipped=25) at `6c0bcdc4`, the verified merge state. The skip difference is explained in section 4.2.

## 5. Open items by LOW batch

"Do first" as in v5; the flag's source stays **(unverified)** as v5 § 5 says. Batches I, J, K, L, M, N, P, R, S, V, X, F and U are carried from v13 without change. **Q grows by one (SEC-T791-01). Y loses SEC-T786-02 and gains TD-T789-01. Z ends. O is new.**

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v13 § 5 | 23 | as v13 | as v13. **TD-T774-01 needs a grade first** (my suggestion) |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v13 | as v13 |
| K | Security runtime | as v13 § 5 | 7 | as v13 | as v13 |
| L | CWSO helper scripts in emage.code | as v13 § 5 | 5 | as v13 | as v13 |
| M | CWSO repository | as v13 § 5 | 12 | as v13 | as v13 |
| N | Release tooling, second round | as v13 § 5 | 8 | as v13 | as v13; the release scripts have no diff since v13 |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v13 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, SEC-T773-02, SEC-T780-05, TL-T780-09, SEC-T762-04, TL-T761-10, SEC-T784-01; **new:** SEC-T791-01 | 10 | release-manager (also SEC-T791-01); technical-writer for SEC-T784-01; the orchestrator routes; **the user rules on SEC-T762-04 and TL-T761-10** | **the v11.0.0 release** (items 2, 4, 10, 31, 33, 38, 39) |
| R | Release-gate text, second round | as v13 § 5 | 4 | orchestrator routes each | **the route of SEC-T735-06 and -07 is still to be settled before batch R** |
| S | Release gate: the runner tag | SEC-T741-17 (the rest) | 1 | the user (A-20) | waits on the user's runner |
| V | Release gate after plans 142, 143 and 146 | as v13 § 5 | 15 | devops-engineer | **open, for the user**: no source binds V to a release; SEC-T751-06 first (v11's suggestion) |
| X | CI images, the CA control and runner settings | as v13 § 5 | 10 | as v13 | as v13 (item 37 for SEC-T786-01, whose trigger is unchecked since T786; A-21; every later image bump must pass both CA jobs, item 35) |
| Y | Shipped text and records | TL-T753-05, TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T763-01, TL-T763-02, TL-T780-08; **new:** TD-T789-01. **Left:** SEC-T786-02 (fixed) | 9 | technical-writer; orchestrator for TL-T753-07 and TL-T761-12 (suggested; no source sets it) | the next docs change; TD-T789-01 at the next edit of the checklist page; TL-T761-12 before the next first-tag use of `CONTRIBUTING.md` |
| Z | `context-retriever` after M-2: code residue | **Ended.** QA-T760-01, -02, -03 fixed (T790, T791, T792) | 0 | — | — |
| O | `context-retriever` after T790: LOW residue | **new:** SEC-T791-02, SEC-T791-03, QA-T792-1 | 3 | backend-developer through the orchestrator | next sprint (T791 for -02 and -03; QA-T792-1 has no window, my suggestion: with the other two) |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v13 | as v13 |
| U | Live checks and user | K-20 (open), SEC-T658-02, TD-T697-03, SEC-T694-10, SEC-T694-12, SEC-T695-06, SEC-T780-06 | 7 | the user or an authorised live session | A-2, A-7, A-11, A-15, A-22 |

Total 23 + 1 + 7 + 5 + 12 + 8 + 1 + 10 + 4 + 1 + 15 + 10 + 9 + 0 + 3 + 2 + 7 = 118 = 117 tracked-LOW + 1 open. **No open item carries a grade above LOW** on any scale; K-20, TD-T774-01 and TD-T789-01 have no grade.

**Order, my suggestion only.** v13's items 1 (batch Z) and 3 (SEC-T786-02) are done.
1. At v11.0.0 preparation: Q, with SEC-T784-01 and SEC-T791-01, in the release document; item 2's ADR-011 re-acceptances; X's SEC-T786-01 check (item 37).
2. O's SEC-T791-02, next sprint: it is the same kind of silent failure as QA-T760-02; SEC-T791-03 and QA-T792-1 with it.
3. Y's TD-T789-01, at the next edit of the checklist page (at the latest the next image bump).
4. V's SEC-T751-06, as v11 suggests.
5. I's TD-T774-01, once graded.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v13 § 6.1 stand and stay the record. Nothing new since v13: plans 150 and 151 accepted no risk. The MEDIUM end dates are as v12 § 6.1.

### 6.2 Next release checklist (v11.0.0, MAJOR)

Carried from v13 § 6.2, with its numbers. **Item 36 changes and item 39 is new.** Items not named here keep v13's text (and, through v13, v12's).

**Citations re-read.** `scripts/install.sh` changed in the range, in two hunks starting at `:1713` and `:1766` (the memory notice, now `:1728-1745`). The `install.sh` citations of v12 § 6.2, which v13 carries, are items 4 (`:187`, `:1301-1304`, `:1305`, the Pi and Gemini notices at about `:1306-1352`), 13 (`:1300`) and 31 (the pointer to `docs/releases/v11.0.0.md`). All lie before `:1713` and **stand**: `:187` the Cursor error, `:1300` the gate comment, `:1301` the `.cursor/mcp.json` advice, `:1305` the pointer, Pi `:1308-1327`, Gemini `:1330-1351` (read here). v11 § 6.2, which v12 carries for its unnamed items, cites `install.sh` lines only in items 4 and 13, which v12 replaced (one grep, read here). `docs/wiki/mcp-pin-bump-checklist.md` changed: item 35's reference to its § 3 stands (section 2.2). No item cites `servers.yaml`, `sync.mjs` or the memory runtime. `.gitlab-ci.yml` and `implementation/PREREQUISITES.md` did not change, so items 14, 19, 21, 23, 35 and 38 stand.

36. **Done for the code.** Batch Z's code residue is fixed (T790; T791, T792; MR !670). The first sentence stands and was followed at T793: `--print-drift` gave `[]` after the root refresh (plan-151 § Outcome; plan-152 § Facts). **What the release document reports as fixed**: v13 § 6.2 and batch Q have no item for it, so it goes here. The v11.0.0 document closes **K-35** (QA-T760-03, by T790), keeping its id as v10.0.0 did with K-5, and states that **M-2's two caveats** no longer apply: the install note now prints the memory `requirements.txt` line (QA-T760-01), and the build refuses a non-lower-case `--project-id` (QA-T760-02). `docs/releases/v10.0.0.md` stays as published (plan-151 § Task Decomposition). The cited `install.sh:1745-1747` in v10.0.0 M-2 is now `:1737-1739`; the new document cites the current lines (read here).
39. **New. SEC-T791-01's migration note.** On an install with `.claude/` beside other platform folders, Cline and Opencode sessions now resolve as their own platform (`cline`, `opencode`), which changes which shared-scope entries they see: entries naming only `claude-code` are no longer returned to them, entries naming their platform now are. Shared entries meant for every client list each platform or use `["*"]`. A self-install's root changes only after its refresh (T791 § Findings). Owner release-manager; before the tag.

### 6.3 Dates

Carried from v13 § 6.3 unchanged. No source in the range changes a row; `.gitlab-ci.yml` has no diff, so `ci_images_reviewed_on: 2026-11-11` and its failing day **2027-03-12** stand (last passing day 2027-03-11).

## 7. User actions

Carried from v13 § 7 unchanged. No source in the range changes a user action. **A-21 is still open**: T789 § 3 O-3 and § 6 item 4 say the runner's configured platform is still not read. A-22's state is still **(unverified)**: the two settings files were not opened.

## 8. Method, limits and validation

- **Carried statuses**: v13's rows and lists, plus the sources in Based on. Plan-152 § Facts is the only source for the merges (!668 to !671), their pipelines and suite runs, the user's words, and the ledger count (0 active, 590 completed after !671). `docs/tasks/completed-tasks.md` holds 590 task rows, and `active-tasks.md` holds only T794 (read here). No network call was made.
- **The search for changes**: a script extracted every id-like token from v13 (172 distinct tokens, including user-action numbers) and searched the 1056 lines added in `713a14c6..325aebb4` outside `tests/golden/`. Only QA-T760-01, -02, -03, SEC-T786-02 and A-21 are named. Each hit was read in context. A-21 appears twice, in T789 § 3 O-3 and § 6 item 4, as a reference with no change. The same lines were searched for new ids (section 1.2).
- **Counting**: 5 new ids, from plan-150 § Outcome, T791 § Findings and T792 § Observations. Section 5 expands to 118 distinct ids: the 112 v13 tracked-LOW ids that remain, the 1 open id and the 5 new ids.
- **What real jobs and runs proved.** Source: plan-152 § Facts, plan-151 § Outcome and T792. I read no job log and ran no pipeline.
  - MR !669 at `d1b24341`: pipeline 3057685976 green; full suite in a clean worktree 2707 OK.
  - MR !670 at `6c0bcdc4`: pipeline 3058131011 green; full suite 2719 OK (skipped=25). Earlier at `a4552400`: 2719 OK (skipped=24), MR pipelines green.
  - MR !671 at `04401738`: pipeline 3058787632 green; full suite 2719 OK (skipped=25); `--print-drift` `[]` after the merge.
  - T792's own runs in temporary targets: the printed lines and builds with their exit codes, real stdio `initialize`, `tools/list` and `retrieve` calls on Cline and Opencode installs, and the three negative checks (T792 § Results, § Negative checks).
  - The orchestrator's checks for plan-150 and plan-151 (`sync.mjs --check`, `generate-registry.py --check`, `scorecard.py --check`, the ledger validator, `test_link_integrity`, `test_pin_bump_checklist`).
- **What GitLab's APIs proved.** Only the orchestrator's read of tag pipeline 3039977704, job 17831135512 (plan-150 § Outcome); how it was read is not recorded **(unverified)**. No registry API read is in the range.
- **What is reading only**:
  - T789 in full (the reviewer had no git tool and ran nothing; T789 § 6);
  - T791 in full ("No command was run"; T791 § Method and limits; its tests were read, not run);
  - my line reads and greps, and the `git` check of the release lock (section 4.2).
- **Dropped from v13's unverified list**: nothing. T789 § 6 item 5 (that `release-docs-gate` ran the current lock) was never on v13's list; it is settled by the orchestrator, with the git half confirmed here (section 4.2).
- **Still unverified**:
  - Carried from v13 § 8.
  - SEC-T786-01's trigger, unchecked since T786 (plan-152 § Facts).
  - New, from T789 § 6: item 3, Docker Hub's answer to a per-platform manifest fetched without a matching `Accept` header (O-2); item 4, the `AMD Ryzen 7 2700X` CPU lines (from T786 and the orchestrator's log reads; the runner's configured platform is A-21). Items 1 and 2 (the files changed; the tests) are covered by the orchestrator's checks and this register's diff stat.
  - New, from T791 § Method and limits: which working directory Cline and Opencode use when they start a stdio server (T791 point 2). T791's other two unverified points are settled: the suite and pipeline (plan-152 § Facts) and QA's reproductions (T792).
  - New, from T792 § Method and limits: a first run with an embedding-model download; `--platform claude-code`, `github` and `all` installs; the `--update` and `--projections-only` paths of the new notice; a nested-group remote end to end (only the form check ran); `--shared-source-root`; the server against an index built under a mixed-case id before T790; the wording of `docs/releases/*`; and QA-T792-1's outcome on the system `python3`.
- **Not run here**: the suite and the pipelines, which the orchestrator ran before each merge. No mutation and no full suite ran for this register.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v13.md`; `plan-152-tracked-debt-register-v14.md`; `docs/tasks/task-T794.md`; `plan-150-pin-checklist-no-docker.md` § Outcome; `security-review-t789-pin-checklist-v1.md`; `plan-151-context-retriever-code-residue.md`; `security-review-t791-context-retriever-v1.md`; `qa-recheck-t792-context-retriever-v1.md`; `docs/tasks/completed-tasks.md` rows T788 to T793;
  - by grep or line range: `scripts/install.sh`, `implementation/runtime/memory/build.py`, `implementation/runtime/memory/context_retriever.py`, `implementation/knowledge/mcp/servers.yaml`, the root `.mcp.json`, `.cline/mcp.json` and `.opencode/opencode.json`, `docs/wiki/mcp-pin-bump-checklist.md`, `docs/releases/v10.0.0.md` (M-2, K-35), v12 and v11 § 6.2 (one grep each), and the batch letters of v1 to v13 (one grep);
  - `git log` and `git diff 713a14c6..325aebb4`; `git log` and `git merge-base` for `ci/requirements-release.txt`.
- Decision IDs: ADR-011.
