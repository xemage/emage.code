# plan-126 — LOW batch B: release tooling and CI

**Created:** 2026-11-01
**Based on:** `docs/artifacts/tracked-debt-register-v4.md` § 5 (batch B, 20 ids); `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; the user's answer of 2026-11-01, verbatim: "B go".
**Scopes:** `T715`, `T716`, `T717`.

## Goal

Close the release-tooling LOW items before the next release: the release-docs gate, the release script, the tag-tree check, the function-size and version guards, and the release documentation in `CONTRIBUTING.md`. SEC-T703-02 and SEC-T703-03 are due before the next release (register v4 § 5).

## Task Decomposition

1. **T715** (devops-engineer): the release-docs gate and the repository guards.
   - SEC-T703-01: `scripts/verify-release-docs.py:129-131,341-347`; the anchor check tests presence, not content, so an anchor inside a code fence or an HTML comment passes. Check the anchor outside fences and comments.
   - SEC-T703-02: `verify-release-docs.py:127,314-321`; a migration pointer in another form passes vacuously. Fail on a pointer-like line the pattern does not parse.
   - SEC-T703-03: `verify-release-docs.py:333-338,357-358`; a pointer to a newer version than the current one is skipped silently. Report it.
   - SEC-T677-02: no test pins the `check_section_requirements` call in `verify-release-docs.py` `main`, and none pins that the `SWAP_*` variables in the `install.sh` swap helper are set before the first rename. Add both tests.
   - SEC-T677-01: `tests/functional/test_function_size.py` misses some function shapes (Bash `function name {` and a brace on the next line; JS arrows, methods, nested functions; a column-0 `}` inside a heredoc; redefined Python names). Close what a line-based guard can close; report the rest with a reason.
   - TL-T708-04: `tests/functional/test_verify_release_docs.py:194-203` became weaker with the version bump. Make it independent of the current version.
   - TL-T708-05: `test_verify_release_docs.py:256-260` is always skipped. Make it run, or remove it and say why.
   - TL-T708-07: `scripts/check-version-consistency.py:68-82`; the exclusion is wider than its rationale (Proposed ADRs). Narrow it, or record why not (the reviewer found it acceptable as is).
   - SEC-T685-03, code part: the `verify-release-docs.py:15-17` docstring still says the main duty is enforced "within its grace window". Correct it.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. A deliberately broken fixture shows each new check failing. All gates and the suite pass.
2. **T716** (devops-engineer): the release script, the tag-tree check and the pin audit.
   - SEC-T685-01: `scripts/check-release-tag-tree.py` resolves `origin/main` by git's short-name search, so a tag named `origin/main` shadows it. Resolve `refs/remotes/origin/main`, and add a test with such a tag.
   - SEC-T685-02: the unsafe class for subjects in `scripts/publish-release.py` still misses default-ignorable code points (U+180B-180F, U+206A-206F, U+FFF0-FFF8 and others). Use a Unicode category test (`Cc`, `Cf`, `Zl`, `Zp`, `Co`, `Cn`) plus the explicit `Mn`/`Lo` list.
   - SEC-T675-10: Markdown escaping of commit subjects beyond control characters is not traced. Escape the subjects, or show they are already safe in the release body.
   - SEC-T675-08: several release-tooling controls are pinned only by redundant checks, or are untested. List them and add the missing tests.
   - SEC-T686-07: the child-process allowlist in `publish-release.py` passes `GIT_EXEC_PATH`, `GIT_ASKPASS`, `GIT_CONFIG_*` and the proxy variables without a stated reason. State the reason for each, or drop it.
   - SEC-T686-08: Python and the bootstrap differ on the `LC_` name pattern. Make them the same, and add a test.
   - TL-T708-06: `publish-release.py:433-435,463-466` has functions with 5 and 7 parameters (the limit is 4). Reduce them.
   - SEC-T712-05: add tests for `via` cycles and odd `via` shapes to `tests/functional/test_audit_mcp_pins_hardening.py`.
   - D-T710-2: in the release job's `CHANGELOG.md` artifact, `## [Unreleased]` follows the new entry (T706 O-1, K-10). Place the entry below `## [Unreleased]`, as Keep a Changelog orders it, and add a test.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. All gates and the suite pass. `.gitlab-ci.yml`, if changed, still passes the CI lint (`validate_project_ci_lint`).
3. **T717** (technical-writer): SEC-T685-03, documentation part. `CONTRIBUTING.md` is silent on three release cases: pre-release tags, the retag procedure, and a hotfix during a release. Document them, consistent with the B1 order (CONTRIBUTING steps 5-7) and with `docs/wiki/` where it covers releases. Retagging is a destructive operation and needs the user's approval; say so. *Acceptance:* the three cases are documented. Each statement matches the scripts (`check-release-tag-tree.py`, `verify-main-sync-merge.py`, `publish-release.py`) or is marked **(unverified)**. The orchestrator runs the gates.

T715 and T716 run in parallel; they share no file. T717 runs in parallel with both; it edits only `CONTRIBUTING.md` (and a `docs/wiki/` page if one needs a pointer). A Security Engineer reviews T715 and T716 together after both are merged into the plan branch.

## Not in this plan

- **SEC-T676-14** (INFO): the lock `--exclude-newer` value. It is due at the next lock regeneration, and no regeneration is planned here. It stays tracked.
- **SEC-T702-08**: Brave API fetches have no timeout or size cap. This is upstream code: the fix is a report to the Brave project, which is an outward-facing action. The orchestrator offers the user a draft of the report; the user files it, or decides not to. It stays tracked until then.

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file. Never print a secret value.
- No change under `implementation/` is expected. If one becomes necessary, declare the root drift; a root refresh needs the user's explicit approval.

## Outcome (2026-11-01)

- **Tasks.** T715, T716 and T717 are done. Of the 20 batch-B ids:
  - 17 are closed;
  - SEC-T677-01 is partly closed; its residual shapes are listed in the guard's docstring;
  - TL-T708-07 is unchanged by the user's T704 decision;
  - SEC-T676-14 and SEC-T702-08 stay tracked (see "Not in this plan").
- **Added scope.** T717 found three gaps, T717-D1 to -D3, and T715 and T716 fixed them.
- **Security review.** `docs/artifacts/security-review-t715-t716-batch-b-v1.md` gives PASS. Its nine new LOWs, SEC-T715-01 to -04 and SEC-T716-01 to -05, are tracked for the next register version. SEC-T716-01, the drift script's short-name refs, is recommended first.
- **Token overruns** against the brief budgets:
  - T715 about 154k (100k);
  - T716 about 235k (100k);
  - T717 about 113k (50k);
  - the security review about 169k (60k).
