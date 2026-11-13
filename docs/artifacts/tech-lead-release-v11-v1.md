# Artifact: tech-lead-release-v11-v1.md

> Immutable once produced; a revision is `tech-lead-release-v11-v2.md`.

## Metadata

- **Executor**: tech-lead, read-only review mode. No source or release file was changed; only this file was written. Worktree branch `agent/tech-lead/T819`.
- **Gate**: code review by area (T819, plan-161 § Task Decomposition item 7), the `validation-gates` Implementation gate for the release. **Date**: 2026-11-13.
- **Target**: `release/v11.0.0` at `67222765`; range `v10.0.0..67222765` (654 files, +14697 / -50098; most of the deletions are the removed `.pi/` and `.gemini/` trees and their mirrors).
- **Based on**: `docs/tasks/task-T819.md`; `docs/plans/plan-161-release-v11.md` (item 7, Addenda 1 to 3); `docs/releases/v11.0.0.md` (T816); `docs/artifacts/release-v11-audit-v1.md` (T813); `docs/artifacts/tech-lead-release-v10-v1.md` (shape); ADR-013, ADR-014 (Appendix A), ADR-015 and ADR-016 (§ Decision, rows D1 to D4, W1 to W3); `docs/plans/plan-160-v11-confirmation-sec-t660-t665.md` § Outcome; `docs/artifacts/security-review-t812-v11-no-harness-fix-v1.md` (lines 67, 70, 98, 132); `docs/artifacts/brave-audit-acceptance-v4.md` (§ Metadata, the advisory table); `docs/plans/plan-159-release-gate-runner-tag.md` (lines 24 to 49); `docs/releases/v8.0.0.md:261`, `docs/releases/v9.0.0.md:232`, `docs/releases/v10.0.0.md:297`.
- **The user's words** (2026-11-13, option labels verbatim): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)".
- **Decision IDs referenced**: ADR-011, ADR-012, ADR-013, ADR-014, ADR-015, ADR-016.
- **Basis marker**: **(V)** read or run here. **(read)** read, not run. **(unverified)** neither.

## Verdict: CONDITIONAL_PASS

No blocker. Areas 1 to 3 pass. Area 4 passes on one condition: the release document's two probe-tag items, K-36 and K-32, were written before T817 ran and do not yet report its result (TL-T819-01). The other findings are Minor or LOW. They are wording, or tracked items for the next register.

## What was run

- `node implementation/scripts/sync.mjs --root implementation --check`: "OK - no drift across 314 files." **(V)**
- `python3 implementation/scripts/generate-registry.py --check`: "registry is up to date". **(V)**
- `scripts/install.sh --target <scratchpad>/tgt --platform Pi`, `GEMINI` and `pi`: each exit 1, with the removed-platform message, and the target directory was not created. **(V)**
- No suite, no golden suite, no full install, no pipeline: QA runs them (T818).
- **Disclosure:** one `grep -n platform-root` over the generated configs also named the root `.vscode/mcp.json`, which the brief forbids reading. The grep printed no line for that file, so none of its content was seen. No other user settings file was touched.

## Area 1. Installer and generator: PASS

- **Pi and Gemini refusal** (`scripts/install.sh:191-198`) **(V)**. The case arms come after `is_supported_platform` fails, so they match any letter case. They exit 1 before `run mkdir -p "$TARGET"` (`:1673`), and I saw the same at run time. `SUPPORTED_PLATFORMS` (`:20`), `platform_managed_paths`, `platform_mcp_config` and `install_<name>` no longer name either platform. The only other `pi` or `gemini` strings in the installer are the two notices.
- **Notices, never deleting** (`:1308-1351`, called at `:1358-1359` from `validate_before_update`) **(V)**. Each notice returns early on a missing or symlinked directory, and reads only an unlinked `.generated-manifest.json` (a `grep` for its own platform) or tests that the unlinked provenance sidecar exists. Nothing writes to, prunes or deletes `.pi/` or `.gemini/`: the `--update` loop (`:1360`) lists only the four remaining trees and `.clinerules`, and every `rm -rf` in the installer runs on a platform tree's swap build or on a named destination. `--projections-only` sets `UPDATE=1` (`:368`), so the notice also runs in that mode. That makes the "`--update` and `--projections-only`" wording of M-1 and M-2 correct.
- **Generator** (`implementation/scripts/sync.mjs`) **(V)**:
  - `skipFormats` is gone from `SERVER_KEYS`, so a leftover key stops the run through the unknown-key check (comment `:208`).
  - `emittedFor` became `selectedFor` at all three call sites.
  - The Pi and Gemini emitters, `mapEnvOmitOptional` and the `pi` tool-name style are removed. `emitMcpVscode` writes what `emitMcpVscodePi` wrote for `vscode`.
  - The manifest and pack schema enums lose `pi`, `gemini` and `drop`. `generate-registry.py` lists four platforms, and `render_installed_agents.py --platform` lists four plus `all`. Both drift gates pass (above).
- **context-retriever** (plan-151, plan-153) **(V)**:
  - `servers.yaml:196` passes `--platform-root {{platformDir}}`. The mirrors carry `.claude`, `.cline` and `.opencode` (`implementation/.mcp.json:86`, `.cline/mcp.json:86`, `.opencode/opencode.json:99`), and each folder's `.generated-manifest.json` names `claude-code`, `cline` and `opencode`, which `resolve_platform` reads. That is SEC-T791-01's behaviour change as M-4 states it.
  - `context_retriever.py` adds dot-segment refusal and userinfo redaction (`_redacted`, at most 200 characters), and `is_derived_project_id` is now total.
- **`{{...}}` refusal (U-1)** (`sync.mjs:231-250`, `:1284-1290`) **(V)**. `validateArgPlaceholders` refuses any `args` string that contains `{{` or `}}`, except the whole `{{platformDir}}`. `validatePlatformDirs` runs before the first write and fails closed on an `outputDir` that is not one plain dot-folder name. The check covers `args` only (TL-T819-04, LOW). A-06 and M-7 state that scope correctly.
- `merge-mcp-json.py`: the `excludeTools` union, the `hooks` note and `--drop-env-form` are removed. The installer no longer passes the flag **(read)**. T773 and T780 reviewed these removals in depth. I did not re-review them.

## Area 2. Knowledge text and rulings: PASS

- **`validation-gates/SKILL.md:70`** **(V)**. ADR-016 row D1 is applied word for word. It names the four conditions and says the review confirms "before the user is asked". The citing duty comes after the semicolon, outside both "only when" clauses (O-A). The consequence sentence says "these four".
  - D2 (the dated statement at a later release) stands after the consequence sentence, as the ADR places it.
  - The W1 and W2 texts are applied, and so is ADR-015 Rule 2 with O5 and O6 ("after an earlier release or before this one ships"; the Conditions line names the old deadline's date and the release it was given for).
  - O1 to O3 and O7 are present: the review date is the deadline, with no limit other than still being ahead, the owner records the outcome, and the closer "may be the user".
- **`validation-gates/SKILL.md:120`** carries W3 ("and its plan's deadline") **(V)**.
- **`release-manager.md:183`**: the `mitigation=` and `deadline=` slots carry ADR-015 C2 **(V)**. ADR-016 D3 rules that no change is needed, and none was made.
- The O-D transition rule is in no knowledge file, as D4 decides. It was met for v11.0.0 by T812 before the question (plan-160 § Outcome) **(read)**.
- `implementation/knowledge/` holds no `gemini`, `.pi/` or Pi-platform word after the removals (case-insensitive grep, `api`/`pip` excluded) **(V)**.

## Area 3. CI and the release job: PASS

- **The three `allow_failure: true` lines (§ 6.2 item 15, left to me by T813)** **(V)**. None of them is a tag job:
  - `:55` is `markdown-links`, with rules `merge_request_event` or `$CI_COMMIT_BRANCH`. A tag pipeline has no `CI_COMMIT_BRANCH`.
  - `:210` is `main-develop-drift-check`, which runs on a `push` to `develop` only.
  - `:250` is `wiki-sync`, which runs on `$CI_COMMIT_BRANCH == "develop"` only.

  `release-docs-gate` (`:252-277`), `main-develop-drift-gate` (`:279-300`) and `release` (`:302-324`) have no `allow_failure` key. Their only rule is the `v` + SemVer tag regex.
- **Release-gate runner tag (plan-159)** **(V)**. `tags: ["release-gate"]` is set at `:255`, `:282` and `:306`. A job-level `tags` replaces `default.tags: [docker]`. `runner_tag_problems` (`tests/functional/test_ci_hash_pins.py:420-438`) refuses the name anywhere outside the three jobs, a `$` in any other job's `tags`, and an `extends` of a tag job. That the runner has "Run untagged jobs" off and is protected rests on the user's answer "Yes, both" (plan-159:49) **(unverified)** by me.
- **Node image bump** **(V)**. `default.image` is `node:24-alpine@sha256:116b800c…` (`:43`), and `verify-knowledge-drift` prints `node --version` (`:134`). `ca-chain-check-node` has no `image:`, so it follows the default digest.
- **CA-chain jobs (§ 6.2 item 18)** **(V)**. `:160` and `:181` have only the MR and branch rules, so neither runs on a tag. The image's own store is copied before `apk add`, and both the shipped and the live stores are checked.
- **`unit-tests` (U-4)** **(V)**: `openssl~=3.5` (`:104`), the `v10.0.0` tag fetch (`:116`), and `nodejs~=24` unpinned (`:102`). This is consistent with K-38. That a log shows 24.22.3 is **(unverified)**.
- **The release scripts**: `verify-release-docs.py`, `publish-release.py`, `check-release-tag-tree.py`, `run-allowlisted.py` and `ci/` have no diff since `v10.0.0` **(V)**. The `release` job's `script` line (`:318`) is unchanged.
- **TL-T780-09, the Pi and Gemini migration items checked by hand**. I compared M-1 and M-2 sentence by sentence with ADR-013 and ADR-014 Appendix A:
  - **(V)** Every Appendix A bullet is present: cleanup by `files` and `generatorOwnedKeys`, "do not delete" (Gemini) and "unless you know nothing else" (Pi), the frozen state, automation, and rollback.
  - **(V)** They add SEC-T773-02's "a `.pi/` without a generator marker gets no notice", and the same for `.gemini/`.
  - **(V)** The installer's pointers resolve: `:192` and `:196` name `docs/releases/v11.0.0.md`, `:1327` names "the Pi migration item" (M-1), and `:1351` names "the Gemini CLI migration item" (M-2).
  - The gate checks only Cursor lines, so this hand check is the only check. No new check is added in this release (plan-161 § Not in scope).

## Area 4. The release document, read against the sources: CONDITIONAL_PASS

**Citations on this branch** **(V)**. Every citation I re-read holds at `67222765`:

| Group | Citations |
|---|---|
| `install.sh`, Cursor | `:187`, `:1301` (names M-9 of v8.0.0), `:1305` |
| `install.sh`, Pi and Gemini | `:191-194`, `:195-198`, `:1313-1327`, `:1336-1351`, `:1358`, `:1359` |
| `install.sh`, memory notice | `:1735`, `:1739-1741` |
| `.gitlab-ci.yml` | `:104`, `:116`, `:160`, `:181`, `:255`, `:282`, `:306` |
| `sync.mjs` | `:208`, `:231-250`, `:1284-1290` |
| Other files | `servers.yaml:184-196`; `PREREQUISITES.md:4`, `:227`; the 1.45.2 pin at line 244 of both lock files, which are byte-identical (`cmp`); `v8.0.0.md:261` |

TD-T723-01 (§ 6.2 item 4) is met.

**Claims** **(V)** unless marked:
- The Breaking-changes count (six entries, B-1 to B-6) matches T813 § 1.
- The SEC-T735-09 pointer sentence of `_template.md:88` is not in the document.
- No `<placeholder>` is left outside the pending verdict fields and the user-facing `<your-project>`, `<name>`, `<org>/<repo>` and `<emage.code clone>`.
- "`verify-release-docs.py` has no change since v10.0.0" is true.
- The target receives `implementation/runtime/{memory,security,handoff}` (`install.sh:1607-1616`), so M-6's lock-file lines are paths that exist in the target.

**Migration items** are complete against T813 § 2 (MI-1 to MI-8 map to M-1 to M-8) and § 7 (U-1 in M-7, U-2 in M-9, U-3 in M-8 and K-36, U-4 in M-8). Each item names an action, or says that none is needed.

**K-16 (SEC-T660-01, SEC-T665-01)**, against plan-160 § Outcome and T812 **(V)**:
- The user's words and date are correct, and the answer of 2026-11-12 is marked as superseded.
- The outside closer, the no-harness-fix statement and T812 with its date (2026-11-13, a new review for v11.0.0) are present.
- The order is right: the review came before the question, and the question cited it.
- "T806 is not the confirming review" is stated, and so is the review date 2027-01-28 as the plan's deadline, still ahead.
- For SEC-T660-01 only, the passed deadline "the sprint after v8.0.0" (at the latest 2026-11-01) is given, with the acceptance it belonged to (v8.0.0, `v8.0.0.md:261`).
- That v9.0.0 carried the same deadline is correctly marked **(unverified)**. `v9.0.0.md:232` names the acceptance only in K-16 text and not in a Conditions line, so it cannot be settled from that document.
- SEC-T665-01 has no earlier deadline (T812:98).
- The text matches the v10.0.0 plan (`v10.0.0.md:297`).

**K-28 (SEC-T702-09)**, against `brave-audit-acceptance-v4.md` **(V)**:
- The three answers are verbatim and dated.
- "five graded high" matches the v4 table, which has five `high` rows.
- The plan is a bump, so the ADR-016 conditions do not apply.
- The expiry is 2027-01-30 or the first release above 2.1.4.
- The statement that the release is blocked if the acceptance lapses is correct.

**`PREREQUISITES.md` Node wording (SEC-T825-02)**: read, not re-reviewed, as the brief says. `:4` and `:227` name the three minimums. M-6 and the Install line agree with them.

**Findings in this area**: TL-T819-01 (the condition), TL-T819-02 and TL-T819-03.

## Findings

| ID | Severity | Location | Finding | Fix |
|---|---|---|---|---|
| TL-T819-01 | Important | `docs/releases/v11.0.0.md:220` (K-36), `:222` (K-32) | Both items were written at `46528d6a`, before T817 ran (plan-161 Addendum 3), and are stale now. K-36 says a probe "can show the two gates only". Tag pipeline 3066689514 has since run both gates on runner #59129270, with the pinned digest that `allowed_images` accepts, and `release` was skipped. K-32 still says "if one is pushed". | **Correct K-36 and K-32 before the independent check (condition C-1).** K-36: state what the probe showed and what it does not prove: the `release` job, the credential path of the drift gate's fetches (the project is public), and that system ID `s_7371c6d24bcc` is `gitlab-runner-16028` **(unverified)**. K-32: name `v11.0.0-gate.1` on `01fe29e4`, and keep its deletion by the user **(unverified)**. |
| TL-T819-02 | Minor | `docs/releases/v11.0.0.md:38` (Highlights) | "`--update` leaves an existing `.pi/` or `.gemini/` alone, with a notice". The notice comes only for a tree with a generator marker (`install.sh:1316-1323`, `:1339-1346`; M-1, M-2, SEC-T773-02). | Write "with a notice when it carries the generator's marker". Can go in the same edit as C-1. |
| TL-T819-03 | LOW | `CONTRIBUTING.md` § Cutting a release, first-tag checklist (`:280-293`) | The dedicated `release-gate` runner is not mentioned: without it the three tag jobs stay pending. The digest and `allowed_images` coupling is not mentioned either. Release doc M-8 and `docs/wiki/mcp-pin-bump-checklist.md:34` cover these, but the release doc is not the place a later release author reads. § 6.2 item 28 adds the runner check only to T822's watch. | Track for register v17. Add the prerequisite and a "the three tag jobs ran on the dedicated runner" checkbox after the release. |
| TL-T819-04 | LOW | `implementation/scripts/sync.mjs:231-238` | `validateArgPlaceholders` covers `args` only. A `{{...}}` in `command`, `env`, `url` or `headers` is emitted as literal text. A-06 and M-7 describe the scope correctly, and no shipped entry has one. | Track. Extend the refusal to every string value of a server entry, or document the scope next to `ARG_PLACEHOLDERS`. |
| TL-T819-05 | LOW | `.gitlab-ci.yml:267-271` (comment and line in `release-docs-gate`) | The reasoning for `rm -rf .git "${CI_PROJECT_DIR}.tmp"` names GitLab Runner 19.5.2: the clone credential sits in `.gitlab-runner.ext.conf` until cleanup. The dedicated runner is 19.5.3 (Addendum 3). The probe shows the line ran and the job continued. Whether the credential is still in that file on 19.5.3 is **(unverified)**. | Track for T820 to weigh. Re-read the runner source for 19.5.3 at the next runner bump, and update the comment. Nothing changes for this release. |

## Before the tag

1. C-1 (TL-T819-01) is applied by the release manager before the independent check of T821, ideally with TL-T819-02. I am that independent checker, so I will confirm it there.
2. T818 re-shows the installs, version consistency and the CA-chain jobs on the release commit. T820 re-checks the release-level security delta, TL-T819-05 included.
3. TL-T819-03 to -05 go to register v17 as tracked LOW, under the user's LOW policy.

## Gate Verdict: Implementation Review

**Gate:** implementation
**Executor:** tech-lead
**Date:** 2026-11-13
**Target:** v11.0.0 release (`release/v11.0.0` at `67222765`)

### Verdict: CONDITIONAL_PASS

Findings: TL-T819-01 to -05 (one Important, one Minor, three LOW; no blocker, and no security finding graded above LOW). Condition: C-1.

## VERDICT: CONDITIONAL_PASS

### Reviewed Artifacts

- Implementation: `release/v11.0.0` at `67222765`, range `v10.0.0..67222765`
- Against requirements: none applies; `docs/plans/plan-161-release-v11.md`, `docs/artifacts/release-v11-audit-v1.md`
- Against architecture: none applies; ADR-013, ADR-014, ADR-015, ADR-016 (with ADR-011, ADR-012)

### Decision IDs Referenced

- ADR-011, ADR-012, ADR-013, ADR-014, ADR-015, ADR-016

### Conditions (for CONDITIONAL_PASS)

- [ ] **C-1** TL-T819-01: correct K-36 and K-32 in `docs/releases/v11.0.0.md` with T817's result and its limits. Owner release-manager; due before T821's independent check (production track: before the next gate).

### Blocking Issues (for FAIL)

- None.

### Merge Authorization

- Merge permitted: Yes, with conditions tracked. This review merges nothing, and the merges, the tag and the Release each keep the user's approval.
- Reviewed by: Tech Lead
- Review mode: read-only (no modifications made to source)

## Not checked (unverified)

- The behaviour of a live client: Cline or Opencode identity, Opencode denials (K-20).
- Any job log, including SEC-T786-01's Node 24.22.3 in `unit-tests`.
- The throwaway-target observations of the release manager (35 files, rollback).
- The runner settings, which rest on the user's report (SEC-T811-01, -02).
- Whether A-21 and A-22 are done.
- The `merge-mcp-json.py` removals beyond the diff read.
- The mirrors file by file (covered only by the drift gates).
- `tests/golden/`, which was not opened.

[VERDICT] gate=code-review status=CONDITIONAL_PASS target=release/v11.0.0@67222765 findings=TL-T819-01..05 conditions=C-1
