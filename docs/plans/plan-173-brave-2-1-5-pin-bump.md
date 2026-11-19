# plan-173 — Brave 2.1.5 pin bump (SEC-T702-09)

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v21.md` (§ 6.3: SEC-T702-09 "ends 2027-01-30, or at the first Brave release above 2.1.4");
- `docs/artifacts/brave-audit-acceptance-v4.md`;
- `docs/wiki/mcp-pin-bump-checklist.md`;
- `docs/plans/plan-172-batch-p-brave-upstream-report.md` (§ Outcome: 2.1.5 published 2026-11-17).

**Scopes:** `T851`, `T852`, `T853`.

## User decision (2026-11-19, verbatim)

> Brave 2.1.5 go

**The user's earlier decision on SEC-T702-09** (plan-155, quoted in the release record): "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0". The plan shown with it read: "owner devops-engineer; fix bump to first Brave release above 2.1.4; deadline 2027-01-30 or that release".

## Facts (the orchestrator's record)

- `@brave/brave-search-mcp-server@2.1.5` was published 2026-11-17T15:31:58Z, with `gitHead` `e08f5af0`.
- It depends on `@modelcontextprotocol/sdk` 1.32.2 and `zod` 4.6.7. These are the upstream fixes SEC-T702-09 waited for.
- `dist/BraveAPI/` is byte-identical to 2.1.4 (T849). SEC-T702-08, filed upstream as issue #377, is not fixed by 2.1.5.

## Task Decomposition

1. **T851** (devops-engineer): the bump, following `docs/wiki/mcp-pin-bump-checklist.md` § 1.
   1. **Extra review** for a package without provenance: maintainers, install scripts, dependencies, `npm diff` from 2.1.4 to 2.1.5 read for new network, process or file access, and the unpacked size.
   2. **The transport flag:** check that `--transport stdio` still overrides `BRAVE_MCP_TRANSPORT` in 2.1.5's `dist/config.js`.
   3. **Audit:** `audit-mcp-pins.py audit --audit-level low` with 2.1.5.
   4. **The pin:** edit it in `servers.yaml` and in the tests, then run `sync.mjs` and `generate-registry.py`.
   5. **The checklist:** update § 4's release-audit command. Drop the seven 2.1.4 acceptances if 2.1.5 audits clean; update `test_pin_bump_checklist.py` to match. Add a § 5 run record.
   6. **Declare the root drift.**

   **If 2.1.5 shows a new advisory at high or above,** stop and report.
2. **T852** (security-engineer, read-only): review T851.
   - Is SEC-T702-09 fixed by the bump?
   - Does the acceptance end?
   - Is anything new introduced?
3. **T853** (orchestrator): the root refresh. It **needs the user's approval at that moment.**

## Constraints

- Do not run the Brave server and do not use an API key.
- No `docker`.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`.
- Accepted ADRs and shipped release documents are not edited.

## Outcome

**Done on 2026-11-19.**

**T851** (devops-engineer, commit `bb9ccb37`): the `brave` pin is now `@brave/brave-search-mcp-server@2.1.5`, still launched with `--transport stdio`.
- **Provenance:** 2.1.5 has npm provenance (SLSA v1). 2.1.4 had none.
- **Extra review:**
  - no install script;
  - exact dependencies: sdk 1.32.2, zod 4.6.7, dotenv 17.3.1, express 5.2.1, commander 14.0.3;
  - `npm diff` read in full (24 files): no new network, process, file or env access, and no new endpoint;
  - the new `dist/docker.e2e.js` is test-only, named only by the `test:docker` script.
- **Transport:** `dist/config.js` is unchanged apart from the version, so the explicit flag still wins over `BRAVE_MCP_TRANSPORT`.
- **Audit:**
  - `--audit-level low`: only the 3 known moderates through `server-filesystem` (SEC-T756-07, tracked LOW).
  - The release gate `audit --audit-level high --signatures` with no `--accept`: exit 0.
  - An old 2.1.4 acceptance is refused as "not a current npm pin".
- **Other edits:**
  - the pin in `servers.yaml` and in the pin tests;
  - the mirrors and the registry, regenerated;
  - checklist § 1 step 2 (provenance note), § 1 step 3, § 4 (gate without `--accept`) and § 5 (run record);
  - `test_pin_bump_checklist.py` re-aimed: every `--accept` must name a current npm pin; the v3 and v4 records are checked as history;
  - the drift declared.
- **Mutations:** six, each caught.

**T852** (security-engineer): `docs/artifacts/security-review-t852-brave-2-1-5-v1.md`, **PASS**, with no new finding.
- **SEC-T702-09 (MEDIUM): fixed.** Its v11.0.0 acceptance has ended by its own terms: 2.1.5 is the first Brave release above 2.1.4. No acceptance or ADR-011 renewal is needed at the next release.
- **SEC-T702-07:** the forced stdio still holds.
- **SEC-T702-08:** unchanged (issue #377, batch P).
- **SEC-T756-07:** unchanged.
- **The test re-aim** keeps the gate coverage and makes it stronger.

**T853** (orchestrator): the root refresh, with the user's approval at that moment (question dialog, option label verbatim: "Refresh now (Recommended)").
- `bash scripts/install.sh --target <worktree> --platform all --projections-only` exited 0.
- It changed exactly the 4 declared paths: `.cline/mcp.json`, `.mcp.json`, `.opencode/opencode.json` and `.vscode/mcp.json`. Each is one line, the pin.
- The drift baseline is emptied. `--print-drift` gives `[]`.

**The orchestrator's own verification:**
- `npm view` provenance for 2.1.5 (present) and for 2.1.4 (none).
- The release audit, re-run in the worktree: "no finding at or above the audit level", exit 0.
- `docker.e2e` is named only by the README and `package.json`'s `test:docker`. `bin` is `dist/index.js`.
- The diff scope is as declared.
- The gates, the full suite and the pipeline are recorded in the merge request.

**For register v22:**
- SEC-T702-09 fixed. Its acceptance ended, so § 6.3's 2027-01-30 date and § 6.2 item 43's SEC-T702-09 part are gone.
- SEC-T702-08 is reported upstream (issue #377, filed by the user on 2026-11-19).
- TD-T849-01 (orchestrator id, LOW). `test_merge_task_docs` `test_temp_file_has_the_old_mode_before_content_and_a_random_name` can fail when the CI pid's digits occur in the random temp name: seen in pipeline 3087701714, passed on a retry. T754 fixed this pattern only in `test_merge_mcp_json_robustness.py`.
- SEC-T850-01 and -02, minted and fixed by draft v2 (plan-172).

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T851 | 60k | 80k |
| T852 | 35k | 40k |
| T853 | under 10k | 20k |
