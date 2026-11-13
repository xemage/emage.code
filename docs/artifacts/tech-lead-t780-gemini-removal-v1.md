# Artifact: tech-lead-t780-gemini-removal-v1.md

- **Task**: T780 (code-review half), Tech Lead, read-only review
- **Date**: 2026-11-11
- **Reviewed**: branch `agent/technical-writer/T779` at `21922dcd` (MR !662, draft), commits `85362095`, `592f269e`, `ce1be51b`, `206f7f97`, `21922dcd` on top of `dca424cc` (develop `522b1bd0` included)
- **Based on**: `docs/decisions/ADR-014-drop-gemini-platform-support.md` (accepted 2026-11-07); `docs/artifacts/gemini-removal-inventory-v1.md`; precedent `docs/artifacts/tech-lead-t773-pi-removal-v1.md`. No `requirements-vN.md` exists for this work; the requirement is the user's decisions of 2026-11-07 as recorded in ADR-014 (Status, Requirements).
- **Decision IDs referenced**: ADR-014 (D1-D10), ADR-013 (D1, D5, D8, D10), ADR-010, ADR-002, ADR-011
- **Review mode**: read-only. No source file was changed; this artifact is the only file committed. Mutation runs were made on a throwaway `git archive` copy in the session scratchpad (held-out excluded), with `timeout 120` and a 3 GiB `ulimit -v`.

## Findings

| ID | Grade | Where | Finding and suggestion |
|---|---|---|---|
| TL-T780-01 | non-blocking now; **blocks T781 acceptance** | `tests/functional/test_mcp_package_pins.py` 873-876 | These lines are not root drift residue. They are permanent assertions that contain the word "Gemini": two `assertNotIn("on Gemini CLI ... does not restrict MCP tools")` absence guards and `assertIn("so its Pi and Gemini CLI rows are historical")`. After S3 they still match the D1 content grep, and they fit none of rows a-j. Row g covers only `test_gitlab_token_handling.py`, and row f covers only the doc clauses, not tests that pin them. So T781's acceptance check "D1 grep equals rows a-j exactly" fails. This is the TL-T773-01 lesson again: a guard that names the removed platform has to be a listed row. Fix before S3: the orchestrator records the lines as listed residue (a row-g-type absence guard plus a row-f pin) through the ADR-014 amendment route the orchestrator and solution-architect choose, since an accepted ADR is not edited in place. Alternatively, a developer rewords the guards so the literal does not appear (for example by building the needle from parts, which I do not recommend because it hides intent). |
| TL-T780-02 | non-blocking (condition for T781) | `test_mcp_package_pins.py` 829-833, 870-873 | `RAW_JOB_OUTPUT_PRE_T779` is accepted only while `AGENTS.md` is declared drift, which is correct and tightens itself. The `if label != "agents-root":` exemption at 873 is **unconditional**, though: after S3 the root `AGENTS.md` is still never checked for the absence of the Gemini clauses or for the history clause. At S3, delete `RAW_JOB_OUTPUT_PRE_T779` and the exemption, or tie the exemption to `_root_agents_md_is_declared_drift()` as line 870 already does. |
| TL-T780-03 | non-blocking (LOW debt, register v12) | `scripts/install.sh` 1284-1352 | There are now three near-identical `notice_previous_<platform>_install` functions (Cursor, Pi, Gemini). Each is under 50 lines and has at most 4 parameters, and ADR-014 D4.4 allows a third function, so this conforms. The detection half (directory and symlink test, manifest grep, sidecar `-e`/`-L` test) is copied three times, though. A shared `previous_install_detected <dir> <platform> <sidecar>` helper would remove that copying without touching the per-platform messages. Cursor uses `-f` for the sidecar while Pi and Gemini use `-e`; that is a pre-existing inconsistency and harmless (`-e` on a FIFO or directory never opens it). |
| TL-T780-04 | nit | `implementation/scripts/sync.mjs` 188 | The re-wrapped `denyTools` comment produced a 146-character line, while the lines around it stay within about 100. Re-wrap it. |
| TL-T780-05 | nit | `tests/functional/test_github_removal_notes.py` docstring 3-7 | The re-wrap leaves a ragged short line ("...so the notes must tell" / "them to use..."). Cosmetic only. |
| TL-T780-06 | nit | `test_install_removed_platform_v11.py` 548-565 | On a regression, the FIFO test ends in `TimeoutExpired` (the mutation below shows it does). The blocked grandchild (for example `head`) is left orphaned on the FIFO after `run()` kills `bash`. CI does not care, but a local run leaves a stuck process. Optional: start a process group and kill the group on timeout. |
| TL-T780-07 | nit (accepted deviation) | `tests/functional/test_mcp_server_denials.py` 627-628 | The reworded `ARTIFACT_UNSAFE_CONTEXTS` entry anchors the immutable artifact's removed-platform row with the generic `^\| [^|(]+\(.*"excludeTools": \["browser_run_code_unsafe"`. Deleting the entry would make the detector flag that immutable row as an "unanchored mention", so rewording was required. The looser anchor is limited to § 2 of one immutable file and to the `excludeTools` form, which no live generator writes any more. I accept it. |
| TL-T780-08 | observation (outside this diff) | `implementation/SECURITY.md:9` | Row h is confirmed: "emage.code v1 shipped with a broad list (git, ..., gemini, ...)" is a dated v1 statement and can stay. The next sentence, "v2 keeps the same defaults", is out of date regardless of Gemini, because the harness ships no `.vscode/settings.json` (only `mcp.json`). It belongs in register v12 as a doc item. It is not Gemini residue. |
| TL-T780-09 | observation (release plan) | `scripts/verify-release-docs.py` | The pointer gate requires a migration item only on install.sh lines that contain the word "Cursor". The Gemini notice's pointer (`docs/releases/v11.0.0.md`) is checked for existence (the narrowed skip of SEC-T773-01 covers it), not for a Gemini migration item. This is the same as for Pi, so it is not a regression. The v11.0.0 release plan has to carry Appendix A's item M-n by review, or add the Gemini/Pi item check that SEC-T773-01's planned tightening may include. `test_verify_release_docs` passes unchanged (213 tests OK), which settles ADR-014 D4's (unverified) point. |

No blocking finding against the S1+S2 diff itself.

## 1. ADR conformance (D1-D10)

| Decision | Result |
|---|---|
| D1 scope | Conforms. `gemini.json`, both trees (`git ls-files .gemini implementation/.gemini`: 0 paths), installer items, renderer map and choices, `merge-mcp-json.py` rules, `Makefile:13`, the `check.py` "Gemini" marker, schemas, pack fixture and vendored schema are all removed. History paths are untouched. Grep classification is in § 3; TL-T780-01 is the one gap for S3. |
| D2 generator | Conforms. `emitMcpGemini`, `GEMINI_POST_EDIT_HOOKS`, the `MCP_EMITTERS` entry and the `tools === 'drop'` branch are deleted, and `"drop"` is gone from the `tools` enum. `denyTools`, its validation and both Opencode consumers stay. Comments 186-192 and 838 are reworded (nit TL-T780-04). Negative tests are present: `test_retired_gemini_format_value_fails_closed` (`Unknown MCP format: gemini`) and `test_the_removed_gemini_values_are_refused` (schema rejects `mcp.format: gemini`, `tools: drop` and a pack listing `gemini`). |
| D3 merge | Conforms. `merge_exclude_tools`, its docstring bullet and its call are deleted, along with the `hooks` "replaced" note; `merge_permission` and the SEC-T680 guards stay. The non-MCP sibling-key assertion moved to `test_opencode_opencode_json_merge_on_update` (`theme`), and `$schema`/`instructions` are kept there too. **Deviation, accepted**: `test_merge_mcp_json_robustness.py` was converted, not deleted. `test_a_hooks_value_is_merged_like_any_other_key_without_a_note` now pins the generic semantics (source wins on a leaf, a dest-only sibling is kept, no note), and the printable-name guard moved onto a `permission` key. Both are better than deleting. |
| D4 adopter | Conforms. There is an early case for `[Gg][Ee][Mm][Ii][Nn][Ii]` with the exact message. The notice runs from `validate_before_update`, and `--projections-only` sets `UPDATE=1` (line 368). It tests only the directory, the manifest (`-f`, `! -L`, then `grep`) and the sidecar (`-e`, `! -L`), and never opens `settings.json` or `.env`. Nothing is deleted. **Deviation, accepted**: a third function instead of a table-driven one, which D4.4 allows (debt TL-T780-03). |
| D5 trees | Conforms: both trees are deleted in `592f269e`, and `.gemini` is in `REMOVED_PLATFORM_DIRS` with a named case and a regrown-tree case. I did not reproduce the D5 key pre-check or the untracked-name report **(unverified; T778's report)**. |
| D6 registry | Conforms: `_manifest.schema.json`, `package.schema.json:23`, the `generate-registry.py` fallback, the pack fixture and the vendored schema are changed or removed, and `index.json` is regenerated (`--check` OK). |
| D7 tests | Conforms. Fixtures are re-hosted on `opencode` in commit 1 (`85362095`). The parity stale-leaf uses option A (`d["mcp"]["gitlab"]["command"] = ["stale"]` on `opencode.json`), and my mutation confirms it (§ 4). The floors are changed. **Deviation, accepted**: two floors the ADR missed were also corrected: `test_manifest_schema.py:33` (`>= 4`) and `test_mcp_platform_conformance.py:176` (`== 4`). The ADR's list was incomplete, the change follows its intent, and without it the suite would fail. `test_github_removal_notes.py` uses option A, dropping `task-T679.md` from `DOCS`. **Deviation, conditionally accepted**: `test_mcp_package_pins.py` accepts the old root `AGENTS.md` sentence only while `AGENTS.md` is declared drift. That is consistent with D7's rule that G19 tests reading root projections change with S3, but see TL-T780-01 and TL-T780-02. |
| D8 version | Not part of this MR (release plan). `check-version-consistency.py` passes with canonical v10.0.0. |
| D9 security | This is the security engineer's half. From the code side, the notice reads only the two markers, skips symlinks and opens neither `.env` nor `settings.json` (both the source scan and the FIFO test show this, and the FIFO mutation in § 4 confirms it). |
| D10 golden | Conforms: `git diff --stat 522b1bd0 21922dcd -- tests/golden scripts/scorecard.py` is empty, and `scorecard.py --check` is OK (34 cases, 30 pass, 0 regressions). |

## 2. Byte equality (reproduced)

Commands (scratch copies, session scratchpad `bytes/`):

```bash
for sha in dca424cc 592f269e; do git archive $sha implementation | tar -x -C bytes/$sha; done
# cross: dca424cc scripts and platforms with the 592f269e knowledge/
git archive dca424cc implementation | tar -x -C bytes/cross; rm -rf bytes/cross/implementation/knowledge
git archive 592f269e implementation/knowledge | tar -x -C bytes/cross
(cd bytes/<d> && node implementation/scripts/sync.mjs --root implementation)          # exit 0 for all three
(cd bytes/<d>/implementation && find .github .vscode .opencode .claude .cline .clinerules \
   .mcp.json .mcp.json.provenance.json -type f -print0 | sort -z | xargs -0 sha256sum)
```

Result: 318 files each, and the list hash `b8e0d2532efad4c5870b0145c8bb8424a36ef896c9a2bd1728b54edc3c0dadaf` is identical for base, S1 and cross (`cmp` equal). The two generated `.opencode` trees are equal under `diff -r`. The Opencode denials are byte-identical: `jq -S .permission .opencode/opencode.json | sha256sum` gives `8a49102a…8e63` for both, and the per-agent `: false` lines (`find .opencode/agents -name '*.md' -print0 | LC_ALL=C sort -z | xargs -0 grep -H ': false' | sha256sum`) give `361951f7…5344` for both (443 lines, 28 agent files). Method note: a first run with an unsorted shell glob gave different hashes only because the file order differed, not the content. Sort the file list explicitly.

S2: base→tip changes 20 generated files, and every one of them is a mirror of the 6 projected knowledge files that `ce1be51b` changed (context-retriever, consolidate-memory, discover-skills, skillify command and skill, memory-management; `knowledge/README.md` does not project). Those 20 files plus `AGENTS.md` are exactly the 21 declared drift paths.

## 3. Completeness (acceptance grep on `21922dcd`)

The file-name check returns nothing. The content grep (inv. § 12, ADR-014 D1) returns **211 lines in 37 files**:

| Class | Hits |
|---|---|
| Row a (provider, false positives) | `sia-target/README.md:97`, `harness-entrypoint.py` 18, 19, 61, 73, `registry-entry.go:29`, `test_t223_sia_harness_capture.py:330` (7) |
| Row b (removal message, notice, tests) | `scripts/install.sh` 14 (196, 1330-1351, 1359); `test_install_removed_platform_v11.py` 117 |
| Row c (orphan guard) | `test_platform_tree_ownership.py` 11 (docstrings 12, 16, 113; tuple 31; cases 108-109, 147-153) |
| Row d (negative tests) | `test_mcp_platform_conformance.py` 280-286 (6); `test_manifest_schema.py` 143-161 (6) |
| Row e (README migration paragraph) | `README.md` 68-74 (6) |
| Row f (history clause only; checked per occurrence) | `implementation/AGENTS.md` 116, 118; `implementation/PREREQUISITES.md` 44, 45; `docs/wiki/mcp-servers.md` 106, 130, 139 |
| Row g (posture guard) | `test_gitlab_token_handling.py:464` |
| Row h (dated) | `implementation/SECURITY.md` 9 (confirmed dated, TL-T780-08) and 39. `test_mcp_schema_validation.py:3` no longer contains the word (its sentence says "seven platforms" without naming Gemini), so it is no hit |
| Row i | empty: `test_github_security_servers.py` sample reworded |
| Row j (user-owned) | `.vscode/settings.json:13`, `.claude/settings.json:9` (`Bash(gemini:*)`, a permission allow entry, seen only as the grep line) |
| Root projections awaiting S3 | `AGENTS.md` 9 lines (60, 74, 80, 88, 93, 97, 102, 116, 118) and 17 files under `.claude/`, `.cline/`, `.github/`, `.opencode/`, 1 line each. All 18 are in the declared drift list |
| Test pins of root projections (S3-coupled, D7) | `test_mcp_package_pins.py` 829, 832 (transient, remove at S3) and **873-876 (permanent, unlisted: TL-T780-01)** |

Every other hit is in a listed row. **Count words**: four manifests remain (`claude-code`, `cline`, `github`, `opencode`), and `SUPPORTED_PLATFORMS` has 4 entries. Floors and counts are correct in the live trees (`test_manifests.py`, `test_manifest_schema.py` 33/50, `test_mcp_platform_conformance.py` 136/176/189, `test_mcp_tool_name_mapping.py:341` `sources * 3`, `test_root_install_parity.py` 3/173, `context-retriever` "other 3 platforms", `skillify` "other three"). The remaining "other 4" and "other four" are only in the 21 declared root drift files. The sweep found no other wrong count in live text.

## 4. Tests

- **Counts**: the `def test_` name diff 522b1bd0→21922dcd gives 26 removed and 29 added names (2827 → 2830). That is 19 deleted, **7** renamed or converted (`..._opencode_denials`, `..._on_opencode_only`, `..._all_four_platforms`, `a_permission_key_elsewhere`, `no_doc_claims..._on_opencode`, `without_any_deny_list..._permission_key`, and the `hooks` conversion) and 22 added (18 Gemini cases in `test_install_removed_platform_v11.py`, 2 orphan-guard, 2 negative). The brief's "6 renamed" leaves out the `hooks` conversion; it is not a defect.
- **Opencode coverage**: the denial tests named for Opencode in the three denial files number 17 before and 17 after, and `test_mcp_agent_denials.py` has 69 before and 69 after.
- **Deleted tests whose generic half survives**: the stale-tree, fresh-copy and sibling-key assertions live on in `test_opencode_opencode_json_merge_on_update`. "Unknown style fails" lives on in `test_an_unknown_style_fails_the_run`. The `permission` half of the "key elsewhere" test is kept.
- **Re-hosting keeps intent**: the projections-only, symlink, sentinel, corrupt-config and sibling fixtures moved to `.opencode`, the only tree with the same shape. **Mutation B** (lambda replaced by `pass`): `test_mcp_config_follows_merge_semantics` FAILS and names `.opencode/opencode.json`. Baseline OK, mutated run 5 tests / 1 failure. This confirms T778's report.
- **FIFO test**: **Mutation A** inserts `head -c1 "$dir/settings.json"` into the notice after detection. Both subtests (`--update`, `--projections-only`) end in `TimeoutExpired`, against a 6-test baseline OK. I lowered the test's own timeout from 120 s to 20 s in the throwaway copy only. So the test does prove that `settings.json` is never opened, and by the same mechanism `.env`. The source-scan test adds a static check (no `.env` in the function body, no read except of the manifest). Caveat: TL-T780-06.
- The v10.0.0-tag class runs the `.env` and user-key scenario under rsync and cp. I did not run it in isolation; the orchestrator's full suite covers it **(unverified by me)**.

## 5. Code quality

The new function is 21 lines with no parameters and uses early returns. No dead code is left: no `drop`, `excludeTools`, `hooks` note, `install_gemini` or Gemini map entry remains in the scripts (grep over `implementation/scripts`, `scripts`, `tests/functional`). Comments describing Gemini are gone from the live code, except the intentional notice comment (row b). Findings TL-T780-03, -04, -05 apply.

## 6. Gates (run in worktree `agent-tech-lead-T780` at `21922dcd`)

| Gate | Result |
|---|---|
| `node implementation/scripts/sync.mjs --root implementation --check` | OK, no drift across 314 files |
| `python3 implementation/scripts/generate-registry.py --check` | registry is up to date |
| `python3 implementation/scripts/check-maturity.py --root implementation` | exit 0 (`scripts/check-maturity.py` does not exist at the root; the script lives under `implementation/scripts/`) |
| `python3 scripts/check-version-consistency.py` | PASS (v10.0.0) |
| `python3 docs/tasks/validate-tasks.py` | PASS (7 active, 572 completed) |
| `python3 scripts/scorecard.py --check` | OK, 34 cases, 30 pass, 0 regressions, wrote nothing |
| `python3 -m unittest tests.functional.test_golden_held_out_isolation` | 8 tests OK |
| `python3 -m tests.functional.test_root_install_parity --print-drift` | exactly the 21 declared paths (20 mirrors + `AGENTS.md`), equal to the baseline `drift` list |
| `python3 -m unittest tests.functional.test_verify_release_docs` (extra, D4 pointer) | 213 tests OK |

I did not run the full suite; the orchestrator runs it separately.

## VERDICT: CONDITIONAL_PASS

### Reviewed Artifacts
- Implementation: branch `agent/technical-writer/T779` at `21922dcd` (MR !662)
- Against requirements: none (`requirements-vN.md` does not exist; user decisions of 2026-11-07 as recorded in ADR-014)
- Against architecture: `ADR-014-drop-gemini-platform-support.md` (accepted), `gemini-removal-inventory-v1.md`

### Decision IDs Referenced
- ADR-014 D1-D10, ADR-013 D1/D5/D8/D10, ADR-010, ADR-002, ADR-011

### Conditions (for CONDITIONAL_PASS)
- [ ] C1 (TL-T780-01): owner orchestrator, with solution-architect if an ADR-014 amendment is chosen. Before T781's acceptance, record `test_mcp_package_pins.py` 873-876 as listed D1 residue, or have them reworded so they do not match the grep. Otherwise S3's "rows a-j exactly" check fails.
- [ ] C2 (TL-T780-02): owner orchestrator (T781). In the S3 commit, remove `RAW_JOB_OUTPUT_PRE_T779` and the unconditional `label != "agents-root"` exemption, or tie the exemption to `_root_agents_md_is_declared_drift()`, so that the root `AGENTS.md` is checked for the absence of the Gemini clauses after the refresh.
- Tracked, not conditions: TL-T780-03 (LOW debt, register v12), TL-T780-08 and TL-T780-09 (register v12 and the v11.0.0 release plan), nits TL-T780-04 to -07.

### Blocking Issues (for FAIL)
- none

### Merge Authorization
- Merge permitted: Yes, with conditions tracked. C1 and C2 attach to T781, the next gate. This verdict does not replace the security half of T780, and a FAIL there still blocks S3.
- Reviewed by: Tech Lead
- Review mode: read-only (no modifications made to source)

## Gate Verdict
**Gate:** implementation
**Verdict:** CONDITIONAL_PASS

[VERDICT] gate=code-review verdict=CONDITIONAL_PASS task=T780 artifact=tech-lead-t780-gemini-removal-v1.md
