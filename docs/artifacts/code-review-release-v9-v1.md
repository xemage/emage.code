# Artifact: code-review-release-v9-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Executor**: tech-lead (read-only review mode; no source file was changed). Worktree `agent/tech-lead/T708`, created from `origin/release/v9.0.0`. Installer probes and a rollback simulation ran in the session scratchpad on throwaway targets; the `v8.0.0` installer used there came from `git archive v8.0.0` with `tests/golden/held-out` excluded.
- **Gate**: code review by area (T708), the `validation-gates` Implementation gate for the release. **Date**: 2026-11-01.
- **Target**: `release/v9.0.0` at `ca11bb6e`; range `v8.0.0..ca11bb6e` (49 non-merge commits, 674 files changed). The ADR bodies were not re-read; ADR-010 was checked only through `release-v9-audit-v1.md` and the code (unverified).
- **Based on**: `docs/tasks/task-T708.md` (including its "Gate order" paragraph), `docs/plans/plan-124-release-v9.md` (both addenda), `docs/artifacts/release-v9-audit-v1.md`, `docs/releases/v9.0.0.md` at `efc67ab6` (unchanged at `ca11bb6e`), `docs/artifacts/brave-audit-acceptance-v3.md`, `docs/artifacts/tracked-debt-register-v3.md`, `docs/artifacts/code-review-release-v8-v1.md` (format and the TL-T649 items), `CONTRIBUTING.md` "Releasing".
- **Decision IDs referenced**: ADR-010; D-T700-1, D-T700-2, D-T700-3, D-T700-5 (`release-v9-audit-v1.md` §6); D-11, D-13 (register v3); DEC-T681-1; the user's answers of 2026-11-01 quoted in plan-124 and task-T708.

## Scope and gate order

T708 is one of T706 to T709, which run first and do not edit `docs/releases/v9.0.0.md` (task-T708 §1). This review reads that document for technical accuracy by area. It is **not** the independent check of Release Gate Policy item 5 (`release-manager.md:46`); the top-level session does that check later, at the commit the release manager gives it. Condition C-2 below therefore has to be applied by the release manager **before** that check, so that the check covers the corrected text.

## Verdict: CONDITIONAL_PASS

| Area | Verdict |
|---|---|
| 1. Installer and generator | PASS |
| 2. Knowledge text and rulings | PASS |
| 3. CI, release job and gates (with T704's test change `2f2cd4db`) | PASS |
| 4. Documentation (`docs/releases/v9.0.0.md`) | CONDITIONAL_PASS |

The overall verdict is CONDITIONAL_PASS. Area 4 is conditional on TL-T708-02. The publish procedure in the T711 brief, TL-T708-01, is also a condition: it is not inside any one area, but it decides how the release reaches `main`. You can ship the code, the generator output, the knowledge text and the CI. The tag is not authorised until C-1 and C-2 are closed.

## What was run

- **Release gates on `ca11bb6e`:**
  - `check-version-consistency.py`: PASS, canonical v9.0.0.
  - `verify-release-docs.py --tag v9.0.0`: exit 1. Its only errors are the unfilled `## Gate Verdicts` and `## RELEASE VERDICT` placeholders, which is expected before T710. No marker, section, link or migration-pointer error remains.
  - `sync.mjs --check`: no drift across 494 files.
  - `generate-registry.py --check`: up to date.
  - `check-maturity.py`: 0 failing.
  - `validate-tasks.py`: PASS (6 active, 504 completed).
- **Targeted unit tests:** 598 tests OK, 1 skip (see TL-T708-05).
  - 267 tests: `test_verify_release_docs`, `test_check_version_consistency`, `test_audit_mcp_pins_hardening`, `test_install_cursor_removal`, `test_mcp_package_pins`, `test_publish_release`, `test_link_integrity`.
  - 331 tests: `test_manifest_schema`, `test_manifests`, `test_mcp_agent_denials`, `test_mcp_grant_pins`, `test_mcp_server_denials`, `test_merge_mcp_json_robustness`, `test_pi_optional_variables`, `test_sync_determinism`, `test_sync_inline_array`, `test_sync_manifest_paths`, `test_gitlab_token_handling`, `test_pin_bump_checklist`.
- **Installer probes on scratch targets (observed):**
  - `--platform cursor` exits 1, prints the M-1 pointer and writes nothing.
  - `--platform all` plain install: exit 0.
  - `--update` with a synthetic harness-generated `.cursor/`: prints the six-line notice and leaves `.cursor/` untouched.
  - A user server added to `.mcp.json` survives both `--update` and a plain re-install, so a plain install merges (T672).
  - The plain install prints no Cursor notice. This matches TL-T700-03 and M-1.
  - An invalid `.mcp.json` stops a plain install with exit 1, names the file and leaves it unchanged. This closes TL-T649-02.
- **Rollback simulation (observed):** install with v9.0.0, then run the `v8.0.0` installer with `--update` on the same target, for `claude-code` and for `github`. See TL-T708-02.
- **Other checks:**
  - GitLab grants of the seven holder roles counted on line 4 of each agent file: 24, 19, 16, 17, 11, 8, 6. None of the listed tools merges, approves, pushes, deletes, writes a file, creates a branch, tag or release, controls a pipeline, reads CI variables or job output, or sends a raw API request.
  - Function size and parameter count were checked over the changed Python scripts. A rough brace scan of `sync.mjs` found no function over 50 lines.

## Area 1. Installer and generator: PASS

- **T662 Cursor removal (`install.sh:190-196`, `:1285-1301`, `:1306-1307`).** Fails closed before any write, case-insensitively. The notice reads only the generator's markers and does not follow symlinks (`-L` checks), and it runs only under the update flag. Correct.
- **T704 Cursor-notice fix (`install.sh:1300`).** The old claim that "`--force-prune-keys` exists only in the v8.0.0 installer" is gone. The new advice (edit by hand) is correct, and the facts behind it hold:
  - the `v8.0.0` Cursor file has a `filesystem` and a `github` key (verified, `git show v8.0.0:implementation/.cursor/mcp.json`);
  - `force_prune` refuses a key that is not dest-only (`merge-mcp-json.py:457-471`).

  One sentence still runs two cases together; see TL-T708-03. The wording is pinned by `test_install_cursor_removal.py:39-46`.
- **T672/T682/T684 merges, atomic writes, stale-swap detection.** Read only where the probes touched them (validate-first at `install.sh:1334-1345`, merge in every mode); the probes behaved as documented. The earlier v8 items are fixed:
  - TL-T649-01 (function size): fixed by T677, confirmed by the scan.
  - TL-T649-02 (traceback on invalid JSON): observed fixed.
  - TL-T649-03 (validation inside the write loop): `loadManifests` validates every manifest before the first write (`sync.mjs:1238-1248`).
- **Generator and manifests (T663, T680, T690, T712).**
  - The mirrors and the registry have no drift.
  - The `brave` entry carries `--transport stdio` in all six generated configs and in the root `.mcp.json` (verified). The `servers.yaml:147-149` comment cites the source of the override.
  - The Copilot config has nine servers, including the two security servers (verified in the probe).
  - `cursor.json` is removed, and `_manifest.schema.json` is new.
- Not verified: `--dry-run` writing nothing, the leading-dash refusal, the stale `.emage-old` sibling hint, and the Pi and Opencode generated outputs in a live client (unverified).

## Area 2. Knowledge text and rulings: PASS

16 knowledge files changed (`git diff --stat v8.0.0..HEAD -- implementation/knowledge/{agents,skills,instructions,commands}`).

- **T666/T667/T688 grants.** Counted (see above). No knowledge text still tells an agent that it merges, tags or publishes: grepping for `git tag`, `glab release create`, tag pushes and "merge the release" outside "top-level session" lines finds only `orchestrator.md:133`, which says the agent does *not* run it.
- **Release and tag order.**
  - `release-manager.md:30` (opens the merge requests to `develop` and to `main`; the top-level session merges and tags) and `orchestrator.md:140` give the same order: `develop` first, `main` second, tag on the release-branch tip after both merges.
  - The `release-workflow` skill uses the same order, and its template title is now `# Release v<VERSION>`, which closes TL-T649-10.
  - All three agree with `CONTRIBUTING.md:168-203`. The plan and the T711 brief do not; see TL-T708-01.
- **T693 (Release Gate Policy item 5).** The wording is clear and testable: who checked, which commit, and what may change afterwards. The orchestrator's preflight now points to it.
- **T692.** `TECHNICAL-DEBT.md` goes in the PoC root. This is consistent with the installed `poc-guidelines.md`.
- **T688.** The `qa-engineer` raw-trace prohibition is concrete: it names the routes, the excerpt rule and `system_output`.
- **`devops-engineer`.** The example images moved to `node:24-alpine`, with a pointer to pin the digest.
- No finding.

## Area 3. CI, release job and gates: PASS

- **`.gitlab-ci.yml`.**
  - Every image is digest-pinned and every `apk add` is version-pinned (closes TL-T649-14). CI Python is hash-locked.
  - `unit-tests` fetches the `v8.0.0` tag that the Cursor tests need.
  - `main-develop-drift-gate` adds `check-release-tag-tree.py` (closes TL-T649-13 by tree comparison).
  - The `release` job uses `--token-env CI_JOB_TOKEN --token-header JOB-TOKEN`, and an allowlisted environment for `apk`, mirrored in `CHILD_ENV_APK_NAMES` (`publish-release.py:87-90`).
- **`publish-release.py` (T686).**
  - `validate_token_header` takes only the two allowlisted header names.
  - `child_environment()` combines a name allowlist with a filter on secret values. This covers `CI_REGISTRY_PASSWORD` and the token embedded in `CI_REPOSITORY_URL`.
  - The deprecated `--token` value is withheld by value.
  - Read and timeout errors become `ReleasePublishError` (closes TL-T649-07).
  - `dry-run-publish-release.py` now defaults to the README marker (closes TL-T649-05).
  - The function signatures grew; see TL-T708-06. The runner's credential path stays unproven until the first real tag pipeline (K-26, SEC-T686-06; unverified here).
- **`verify-release-docs.py` (T703).**
  - The pointer extraction, version comparison and anchor rule are small and fail closed: an unparseable tag enforces every pointer.
  - The required files and pointers are checked before the content checks.
  - The tests cover the missing-document case, the missing-item cases (wrong heading, wrong section, fenced code, plain text) and the future-version case.
  - Verdict placeholders are now enforced (closes TL-T649-12). The rest of the gate produced no error on this tree.
- **`check-version-consistency.py` (T704, D-T700-1).**
  - The `docs/decisions/` prefix exclusion is added with a rationale comment that cites the user's decision, following the T642 precedent.
  - The tests prove it does not leak: a nested `implementation/docs/decisions/` path and a sibling `docs/decisions-draft/` are still scanned.
  - See TL-T708-07 for one scope remark.
- **`audit-mcp-pins.py` (T712, reverse-`via` scoping).**
  - `direct_roots` now also follows every entry that names the package as a string `via`. This can only **add** roots, so an acceptance never covers fewer pinned packages than npm reports, which is the safe direction. Recursion is bounded by `seen`.
  - The mutation test for the new loop discriminates (0 against 2 findings).
  - The old "not following `effects`" mutation test had to move to a fixture where `via` does not reach the root (`effects_only`). It still discriminates (1 against 2).
  - Sound.

### T704's test change `2f2cd4db`: sound

The two tests that ran `verify-release-docs.py --tag v8.0.0` against this tree now use `_run_past_release_without_markers` (`tests/functional/test_verify_release_docs.py:32-50`). The helper:

1. calls the real `check_markers` for the past tag and asserts that it reports **exactly** the three `MARKER_FILES`, and nothing else;
2. calls it for the tree's own `Latest release:` line and asserts no error;
3. only then runs `main()` with `check_markers` patched out.

Everything else in the gate still runs for v8.0.0: required files, migration pointers, required sections, the v8.0.0 document's own `Latest release: v8.0.0` line and its verdict placeholders (`check_release_brief`), and links. `check_version_consistency` was already patched out in `_run_main` before this change. The proof therefore ties the patch to the one check that fails by design after a bump, and the helper fails closed:

- a marker file with any other problem fails assertion 1;
- a tree whose own marker is broken fails assertion 2;
- a tree that still carries the v8.0.0 marker skips assertion 1, but then assertion 2 checks that same marker.

It also works unchanged at the next bump. One side effect that 2f2cd4db left alone is TL-T708-04, and a dead test is TL-T708-05.

## Area 4. Documentation: CONDITIONAL_PASS

Read for technical accuracy against the code: Summary, Highlights, Breaking changes A-01 to A-08, Migration Guide M-1 to M-12, Known Issues and the Rollback Plan.

- **Breaking changes.** The eight entries match the eight tasks the audit classifies as breaking (T662, T663, T665, T666, T667, T676, T680, T688). The counting rule is stated.
- **M-1.**
  - The exit-1 refusal, the notice on `--update`/`--projections-only` only (`install.sh:1306-1307`) and the line references are correct (`install.sh:1285-1302`, `merge-mcp-json.py:457-471`).
  - The hand-edit recipe matches D-T700-3.
  - The `--force-prune-keys` bullet has the same two-case conflation as the installer line (TL-T708-03).
- **M-2.** Matches `force_prune`: a name that is not dest-only is refused and nothing is written. The `<generated file>` list names the six current generated configs.
- **M-3, M-4.** Consistent with the probes and the audit (§2). The Pi details were not re-run (unverified).
- **M-5.** `GITLAB_PERMISSION_MODE=modify` and `GITLAB_PERSONAL_ACCESS_TOKEN_FILE` are present in the generated entry (observed in the probe). The README-based teardown list is correctly marked (unverified).
- **M-6.** Counts verified. "`create_merge_request` is the only write tool" holds for the named sets.
- **M-7, M-8, M-9, M-10, M-11.** Consistent with the code and knowledge text read in areas 1 to 3.
- **M-12.** The launch arguments are verified in every generated config. The seven GHSA ids equal the seven accepted in `brave-audit-acceptance-v3.md`; the two other ids in that artifact are the `server-filesystem` moderates, which are not accepted. The expiry 2027-01-30 is today + 90 days, the script's limit.
- **K-10.** "47 subjects at `3c101370`" verified (49 at `ca11bb6e`).
- **Rollback Plan.** Partly verified by simulation:
  - the `github` entry returns, `--transport stdio` is dropped, and the two Copilot security servers are removed from `.vscode/mcp.json` on rollback (observed);
  - but the `GITLAB_PERMISSION_MODE` bullet is wrong (TL-T708-02).

## Findings

| ID | Grade | Area | Where | Finding and recommendation |
|---|---|---|---|---|
| TL-T708-01 | major (procedural, before T711) | release procedure | `docs/tasks/task-T711.md:18`; `docs/plans/plan-124-release-v9.md:37` against `CONTRIBUTING.md:168-203`, `implementation/knowledge/agents/release-manager.md:30`, `orchestrator.md:140` | **Conflict.** T711 says "MR `release/v9.0.0` to `develop`; MR `develop` to `main` with a merge commit; tag `v9.0.0` on the verified `main` tip". The documented order (B1, used for v8.0.0) is: release to `develop`, then **release** to `main`, and the tag on the release-branch tip (`origin/main^2`). Merging `develop` to `main` also carries to `main` anything merged into `develop` after the branch was cut, none of which passed T706 to T709. It recurs TL-T649-11. Both orders pass `check-release-tag-tree.py` (tree comparison), so CI will not catch the difference. **Fix:** the orchestrator corrects the T711 brief to B1, or records the user's decision for the other order, before T711 starts. |
| TL-T708-02 | major (documentation accuracy, before the Policy item 5 check) | 4 | `docs/releases/v9.0.0.md:284` (Rollback Plan, step 3, the `GITLAB_PERMISSION_MODE` bullet); `:237` (K-21) | **Contradicted by a run.** The bullet says that after a rollback the two variables "are no longer generated: the server default for the mode is `full` … the generated entry no longer passes the file variable". **Observed:** the v8.0.0 merge is a recursive deep merge (`git show v8.0.0:scripts/merge-mcp-json.py`, `merge_json`) that keeps keys the source lacks. After v9.0.0 then `v8.0.0 --update` on a Claude Code target, the user's `.mcp.json` `gitlab.env` still holds `GITLAB_PERMISSION_MODE=modify` and `GITLAB_PERSONAL_ACCESS_TOKEN_FILE`. The same is expected on the other platforms (inferred, not run). The effect is safer than the text says, but an adopter is told the opposite of what happens. **Fix:** state that both keys stay in your file after a rollback until you remove them by hand, and that the server default applies only once `GITLAB_PERMISSION_MODE` is removed. Align K-21 ("restores the v8.0.0 MCP entries") with this. |
| TL-T708-03 | minor (track as LOW) | 1, 4 | `scripts/install.sh:1300`; `docs/releases/v9.0.0.md:86`; pinned by `tests/functional/test_install_cursor_removal.py:39-46` | **Two cases in one sentence.** "With that file it refuses to prune `filesystem` … and merges every entry of the file, `github` included, into yours" describes two different runs. A run that names `filesystem` exits 1 and writes nothing (`merge-mcp-json.py:526-529` returns before `report_and_write`). Only a run that does not name it merges every entry. Also, `install.sh:1300` says the file "exists only at the v8.0.0 tag"; the release document correctly adds "(and earlier tags)". The advice itself (edit by hand) is right. **Fix:** in a later release, reword both texts and the test together. Not needed for the tag. |
| TL-T708-04 | minor | 3 | `tests/functional/test_verify_release_docs.py:194-203` | **Weaker test since the bump.** `test_an_unfilled_verdict_fails_the_gate_with_a_clear_message` still runs `main()` for v8.0.0 with the real marker check. `code == 1` is now produced by the marker check alone, so only the `assertIn("still pending")` discriminates. **Fix:** patch `check_markers` there too, or assert that the placeholder error is the only one. |
| TL-T708-05 | minor | 3 | `tests/functional/test_verify_release_docs.py:256-260` | **Dead test.** `test_verifying_v9_fails_while_the_pointed_document_is_missing` now always skips, because `docs/releases/v9.0.0.md` exists; the synthetic test covers the rule. **Fix:** remove it, or point it at a synthetic future pointer. |
| TL-T708-06 | minor (tracked debt) | 3 | `scripts/publish-release.py:433-435` (`gitlab_request`, 5 parameters), `:463-466` (`create_or_update_release`, 7) | **Parameter limit.** Both functions exceed the 4-parameter standard; T686 added `token_header` (and `expected_host` came in earlier). **Fix:** a small `ApiTarget` value (URL, project, host, token, header). |
| TL-T708-07 | minor | 3 | `scripts/check-version-consistency.py:68-82` | **Wider than its rationale.** The exclusion covers all of `docs/decisions/`, but the rationale is that *accepted* ADRs are immutable. A future `Proposed` ADR, which can still change, would not be scanned. All 10 current ADRs are accepted or superseded (verified). **Fix:** acceptable as is; if a Proposed ADR ever carries a current-state claim, scan by status. |

No security finding was raised by this review (no `SECURITY:*` grade). Not observed: the security posture of the release job's runner credential (K-26).

## Items before the tag

| # | Item | Owner |
|---|---|---|
| C-1 | TL-T708-01: the T711 procedure is the B1 order of `CONTRIBUTING.md:168-203`, or the user's decision for the other order is recorded in the T711 brief | orchestrator (and the user, if the order changes) |
| C-2 | TL-T708-02: correct the Rollback Plan bullet and K-21 in `docs/releases/v9.0.0.md` **before** the top-level session's Policy item 5 check, so that the check covers the corrected commit. Re-run `verify-release-docs.py --tag v9.0.0` and `check-version-consistency.py` after the edit | release-manager |
| C-3 | TL-T708-03 to -07 are recorded as tracked LOW debt in the next register (not needed for the tag) | orchestrator |

## Gate rows for the release document

Architecture: CONDITIONAL_PASS. The removed Cursor platform, the single-sourced `denyUnlessGranted`/`denyTools`, the named GitLab sets and the pinned MCP set are respected; C-1 is the condition. Implementation: CONDITIONAL_PASS. The code, generator, knowledge text and CI pass; the documentation condition is C-2. Merge authorisation for `release/v9.0.0`: yes, with conditions tracked. The tag is not authorised until C-1 and C-2 are closed.

## Gate Verdict: Implementation Review

**Gate:** implementation
**Executor:** tech-lead
**Date:** 2026-11-01
**Target:** v9.0.0 release (`release/v9.0.0` at `ca11bb6e`)

### Verdict: CONDITIONAL_PASS

Findings: the table above (TL-T708-01 to -07; two major, five minor; no blocker). Conditions: C-1 and C-2.

## VERDICT: CONDITIONAL_PASS

### Reviewed Artifacts
- Implementation: `release/v9.0.0` at `ca11bb6e` (range `v8.0.0..ca11bb6e`)
- Against requirements: `docs/plans/plan-124-release-v9.md`, `docs/tasks/task-T708.md`
- Against architecture: ADR-010; `docs/artifacts/release-v9-audit-v1.md`

### Decision IDs Referenced
- ADR-010, D-T700-1, D-T700-2, D-T700-3, D-T700-5, D-11, D-13, DEC-T681-1

### Conditions (for CONDITIONAL_PASS)
- [ ] C-1, TL-T708-01: orchestrator; before T711 starts
- [ ] C-2, TL-T708-02: release-manager; before the top-level session's Policy item 5 check, and so before the tag

### Merge Authorization
- Merge permitted: Yes, with conditions tracked
- Reviewed by: Tech Lead
- Review mode: read-only (no modifications made to source)

[VERDICT] gate=code-review | result=CONDITIONAL_PASS | reviewer=tech-lead | artifact_ref=code-review-release-v9-v1.md | date=2026-11-01

## Not checked (unverified)

- **Full suite and evaluator:** the full `tests/run.py`, `scorecard.py --check`, the evaluator hash and the held-out isolation test. The QA gate T707 owns the full-suite verdict.
- **Not read line by line:** the `install.sh` diff (708 lines changed), the `sync.mjs` diff (952), the `merge-mcp-json.py` diff (431) and the knowledge files. Probes, targeted tests, greps and the earlier security reviews were used instead.
- **Installer paths not run:** `--dry-run` writing nothing, the leading-dash refusal, the stale `.emage-old`/`.emage-new` hint, a symlinked target.
- **Rollback beyond what was run:** only Claude Code and GitHub Copilot were simulated. On the other platforms, the claim that the GitLab env keys stay in the file is inferred. The rollback of `.cursor/` and Pi was not run.
- **Live behaviour:** the runner's clone credential, job-token masking, the Releases API with `JOB-TOKEN`, Opencode and Gemini CLI denials, and the Copilot server behaviour.
- **Taken from the plan addendum:** the Brave `--transport stdio` override of `BRAVE_MCP_TRANSPORT`, which the user observed; this review did not run it.
- **External facts in the release document, not re-checked:** Cursor reading `AGENTS.md`, the npm state of `@anthropic/mcp-filesystem`, the `e2b`, `redis`, `figma` and `notion` packages, and Pi version behaviour.
- **Later commits:** any commit on `origin/release/v9.0.0` after `ca11bb6e`.
