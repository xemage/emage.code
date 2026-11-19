# Artifact: independent-check-t878-v1.md

> Immutable once produced; revisions bump `<N>`.

Based on:
- `docs/releases/v12.0.0.md` and `docs/wiki/mcp-servers.md` at `e0e3b355` (the release manager's gate fixes, T878), and the verdict sections at `2be8301f`;
- `docs/plans/plan-182-next-release.md` § Addendum 4 (the probe tag T874 and the gates T875 to T877);
- `docs/artifacts/qa-gate-release-v12-v1.md` (T875: verdict, QA-T875-01, QA-T875-02, C1 to C3);
- `docs/artifacts/security-review-t877-release-v12-v1.md` (T877: verdict, C-1 to C-5, SEC-T877-01);
- my own review `docs/artifacts/tech-lead-release-v12-v1.md` (T876, `0c6be036`).

The shape follows `docs/artifacts/independent-check-t821-v1.md`. The user's words (2026-11-19, option labels verbatim): "release plan go", "Approve (Recommended)", "v12.0.0, MAJOR (Recommended)", "Yes, probe first (Recommended)", "Accept for v12.0.0 (Recommended)" and "Yes, push the probe tag (Recommended)".

**Result: PASS at `e0e3b355`.** Nothing has to change before the tag. I raise no new finding.

For the `Independent check` row: `PASS at e0e3b355, by tech-lead`. I have not written or edited any v12.0.0 release file: not the release document, not `docs/wiki/mcp-servers.md`, not the version marker files. My only v12.0.0 artifacts are the T876 review and this check.

### What I ran

Everything ran in my scratchpad subfolder `t878`. The worktree stayed clean, apart from this file, and HEAD stayed at `2be8301f`. I ran no `docker`, no install and no suite, and I read no job log.

| Run | Exit | Result |
|---|---|---|
| `pip install --require-hashes --only-binary=:all: -r ci/requirements-release.txt` in a fresh venv | 0 | |
| `verify-release-docs.py --tag v12.0.0` on that venv, at `2be8301f` | 0 | "all documentation checks passed"; "verified marker 'Latest release: v12.0.0'" |
| `scripts/check-version-consistency.py` | 0 | |
| Entry counts in the document | | F-01 to F-03 (3), X-01 to X-12 (12), A-01 to A-08 (8) |
| Counts in `implementation/.opencode/agents/` (28 files) | | `edit: allow` in 20 files, `edit: deny` in 8 |
| `git diff e0e3b355 2be8301f --stat` | | `docs/releases/v12.0.0.md` only, 52+ / 18-, a single hunk |

### Results by point

1. **The release files at `e0e3b355`, against T876** (`git diff 892d15f1 e0e3b355`; the commit changes `docs/releases/v12.0.0.md` and one line of `docs/wiki/mcp-servers.md`):
   - **TL-T876-01 is met.** K-36 now reports the probe: pipeline 3090926673; both gates on runner #59129270 ("via gitlab-runner-16028"), with the pinned python digest, under the hardened configuration; the docs gate failing on "missing required file: docs/releases/v12.0.0-gate.1.md", the drift gate on "RELEASE TAG TREE: FAIL" after "MAIN-DEVELOP DRIFT: PASS"; `release` skipped and nothing published. It also states the limit: the probe does not prove the `release` job on this runner. Each fact matches Addendum 4. K-32 says the tag was pushed on `51f03d38` and stays on `origin` until the user deletes it, and it keeps the `git ls-remote` check before and after the tag push. The probe results themselves come from the orchestrator's record; I did not see the pipeline **(unverified)**.
   - **TL-T876-05 is applied.** A-02 cites my re-count at `90124fb6` (13, 26, and 14 named allows per orchestrator).
   - **QA-T875-01 and SEC-T877-01 are fixed correctly.** M-1 now limits the "never written as an allow" sentence to `bash`, `webfetch`, `websearch` and `task`, and says that the 20 agents holding `edit` get `edit: allow`, which as the agent's own rule overrides your global or project `edit` rule. `docs/wiki/mcp-servers.md:121` says the same. The generated tree has 20 `edit: allow` files and 8 `edit: deny` files, and the 8 matches the wiki's own figure. No other occurrence of the old sentence remains in the document, the wiki page, `PREREQUISITES.md` or `AGENTS.md` (grep).
   - **QA-T875-02 is fixed correctly.** The paragraph now says the install writes `docs/wiki/README.md` and `docs/wiki/home.md` and no other wiki page, and does not write `implementation/PREREQUISITES.md`. That matches the installer: `install_docs` copies `implementation/docs/*`, whose only wiki files are `implementation/docs/wiki/README.md` and `home.md`, and `install.sh` names `PREREQUISITES.md` only in two notice texts (`:1706`, `:1722`).
   - **TL-T876-03: I accept the dismissal.** `ca-chain-check-python` already runs `--capath /tmp/ca-shipped/certs` and `--capath /etc/ssl/certs` unconditionally (`.gitlab-ci.yml:180`, `:182`). My T876 finding missed those two lines. The python job needs no guarded step.
2. **The verdict block at `2be8301f`:**
   - **The Gate Verdicts rows match their artifacts.**
     - Implementation, and Architecture by v11.0.0's mapping only: CONDITIONAL_PASS, which is T876's verdict.
     - Integration: CONDITIONAL_PASS, which is T875's verdict (`qa-gate-release-v12-v1.md:16`), with 2820 OK, skipped=13, and golden 173 OK, as Addendum 4 records them.
     - Security: CONDITIONAL_PASS, which is T877's verdict (`security-review-t877-release-v12-v1.md:204`), with 0 critical, 0 high and 2 accepted MEDIUM.
     - Release: CONDITIONAL_PASS, the same as Status.
     - The row texts record correctly that TL-T876-02 and -04 are tracked LOW, that TL-T876-03 was dismissed, and that C1 and C2 of QA were applied in `e0e3b355`.
   - **The counts and features match the document.** Features 3, Fixes 12 and Breaking changes 8 equal the entries listed. Open blockers 0. The Changelog Preview names only changes listed under Changelog and Breaking changes.
   - **The CONDITIONAL_PASS status follows from the rules.** Every gate is CONDITIONAL_PASS and none is FAIL. Two accepted `SECURITY:MEDIUM` findings ship, which caps the verdict at CONDITIONAL_PASS (`validation-gates` § Verdict Rules). No CRITICAL or HIGH is open.
   - **The Conditions are complete.**
     - T877 C-1: the two K-16 lines (`:191`, `:192`) and the verdict lines (`:285`, `:286`) are byte-identical. Each line occurs twice in the document, and each occurrence is the same text (`sort | uniq` gives one distinct line per id).
     - T877 C-2 (dates), C-3 together with QA C3 (probe tag, merge order, runner), and C-5 (young pins) are each listed with an owner, a mitigation and a deadline.
     - T877 C-4 and QA C1 are recorded as applied in `e0e3b355`, and so are QA C2 and my C-1. I confirmed each in point 1.
     - The independent check, the re-run on the final tree and the LOW list for register v26 are listed with owners.
   - **Nothing but the verdict sections changed after `e0e3b355`.** The diff is one hunk, from `## Gate Verdicts` to the line before `## Rollback Plan`. Every removed line is a `pending` placeholder or the old two-line introduction of the block.
   - **The `Independent check` field and the Gate Inputs row** still say "not yet issued", as they must before this check. Under Release Gate Policy item 5 they may be filled from this check without making the verdict stale.

### Findings

None. The one finding I raised at T876 that was not applied, TL-T876-03, I withdraw (point 1).

### What I marked (unverified)

- The probe pipeline, its runner and its log lines. They are the orchestrator's record in Addendum 4; I read no job log.
- QA's runs: the suite, the golden suite, the installs and the rollback.
- Any pipeline on `release/v12.0.0`. The Gate Inputs row says the same.
- Whether the acceptance lines match the dialog as it took place. I compared them with T877 and Addendum 2; I did not see the dialog.
- Whether the probe tag has been deleted on `origin`. Condition C-3 carries that.

[VERDICT] gate=independent-check status=PASS target=release/v12.0.0@e0e3b355 findings=none
