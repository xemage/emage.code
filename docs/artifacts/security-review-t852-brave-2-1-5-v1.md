# Security Review T852: Brave MCP pin bump 2.1.4 to 2.1.5 (T851)

## Metadata
- **Task:** T852 (plan-173), security-engineer, read-only
- **Date:** 2026-11-19
- **Reviewed:** branch `agent/devops-engineer/T851`, commit `bb9ccb37` on `7f8cd4ee` (develop `4cf82a0b` + the plan-173 commit), worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T851`
- **Based on:** `docs/plans/plan-173-brave-2-1-5-pin-bump.md`; `docs/tasks/task-T852.md`; `docs/artifacts/brave-audit-acceptance-v4.md`; `docs/artifacts/security-review-t702-brave-reachability-v1.md`; `docs/wiki/mcp-pin-bump-checklist.md`; `scripts/audit-mcp-pins.py`; `docs/artifacts/tracked-debt-register-v21.md` (§ 6.2 items 43 and 49, § 6.3); `docs/artifacts/mcp-pin-audit-v11-v1.md`; `docs/artifacts/security-review-t756-accepted-mediums-v1.md`; the extracted 2.1.5 package (`x215`), read as text only
- **User decision (verbatim):** "Brave 2.1.5 go". **Earlier decision on SEC-T702-09 (verbatim):** "If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0". The plan shown with it read: "fix bump to first Brave release above 2.1.4".
- **Method:** files read in the worktree and the scratch package. Nothing was run and no shell was used. `git diff` was not available, so each changed file was read at its new state and compared with the main checkout (develop) where that mattered. Claims I took from T851's or the orchestrator's runs without tracing them myself are marked **(unverified)**.

## Scope
These are the 10 files the orchestrator listed:
- `implementation/knowledge/mcp/servers.yaml`
- the 4 generated MCP mirrors under `implementation/.<platform>/`
- `implementation/registry/index.json`
- `tests/functional/test_pin_bump_checklist.py`
- a second test file (the pin test, not read here)
- `docs/wiki/mcp-pin-bump-checklist.md`
- `tests/_baselines/root-install-drift.json`

I read in full or in part: `servers.yaml` (the brave entry), the test, the checklist (§ 1 item 3, § 4 and § 5), the drift baseline, and from the 2.1.5 package `package.json`, `dist/config.js` and `dist/index.js`. I did not read the 4 mirrors, the registry or the second test file. For those I rely on the orchestrator's report that every gate, including `sync.mjs --check` and `generate-registry.py --check`, exits 0 **(unverified)**.

## Assessment

### 1. The pin and the transport
- **The pin (`servers.yaml:143`):** the entry now reads `args: ["-y", "@brave/brave-search-mcp-server@2.1.5", "--transport", "stdio"]`. It keeps `--transport stdio`. The comment above it records that T851 compared `dist/config.js` (lines 139-142).
- **The transport, read in 2.1.5's `dist/config.js`:** line 40 is `.option('--transport <stdio|http>', 'transport type', process.env.BRAVE_MCP_TRANSPORT ?? 'stdio')`. The environment value is only the commander default, so an explicit `--transport stdio` on the command line wins over it. Lines 66-69 accept only `stdio` and `http`.
- **`dist/index.js`:** it imports only `./config.js` and `./protocols/index.js`. It starts the HTTP server only when `options.transport === 'http'`. So the SEC-T702-07 control (forced stdio) holds in 2.1.5.
- **The `.env` file:** `dotenv.config()` at line 6 still loads a `.env` from the launch directory. This is not new, and it was already covered by the SEC-T702-07 analysis. A `.env` cannot override the explicit flag.

### 2. Dependencies and audit
- **Exact dependencies in 2.1.5's `package.json`:** `@modelcontextprotocol/sdk` 1.32.2, `zod` 4.6.7, `commander` 14.0.3, `dotenv` 17.3.1 and `express` 5.2.1.
- **No install hooks:** there is no `preinstall`, `install` or `postinstall` script. `prepare` runs only from a git checkout, not from a registry tarball install (npm behaviour; not traced here). The audit script installs with `--ignore-scripts` anyway.
- **T851's results:**
  - At `--audit-level low`, 2.1.4 gave 4 high (brave, sdk 1.30.0 with six advisories, zod 4.3.6) and 3 moderate. 2.1.5 gives only the 3 moderate, all through `@modelcontextprotocol/server-filesystem` (`glob` GHSA-3g3m-2fjr-6pw4, `minimatch` GHSA-g3hv-75wg-m249).
  - With `--signatures` and no `--accept`, the high audit exits 0. 196 packages have verified signatures and 38 have verified attestations **(unverified: T851's and the orchestrator's runs, not repeated)**.
- **The 3 moderates are not new.** Since v10 they are graded SEC-T756-07, `SECURITY:LOW`, tracked (`mcp-pin-audit-v11-v1.md:18`, `security-review-t756-accepted-mediums-v1.md:44`). The bump does not change them.

### 3. Provenance
- 2.1.5 has npm provenance (SLSA provenance v1). 2.1.4 had none (the orchestrator's `npm view … dist.attestations` **(unverified)**; also T851's § 5 run record).
- This is a gain: the published tarball can now be tied to a build from the `brave/brave-search-mcp-server` repository.
- It does not by itself show that the source is benign, so the `npm diff` read is still the main evidence.
- `toolradar-mcp` is still published without provenance. That is unchanged and outside this scope.

### 4. Code changes in 2.1.5
- **T851's `npm diff` read (24 files):** the runtime changes are tool annotations, output schemas, optional place-search fields, the `ja` and `el` language codes, a warning when the HTTP transport binds past loopback, and the new sdk and zod versions. It reports no new network, process, file or environment access and no new endpoint. `dist/BraveAPI/` is byte-identical to 2.1.4 **(unverified by me beyond `config.js` and `index.js`; T851 and T849 read the rest)**.
- **`dist/docker.e2e.js`:**
  - It uses `child_process` to run `docker`.
  - The only things that point at it are the `test:docker` script in `package.json` (`docker build … && node --import tsx --test src/docker.e2e.ts`, which runs the TypeScript source, not the shipped `dist` file) and the README.
  - `bin` is `dist/index.js`, and its imports chain does not include it. The orchestrator also found that no runtime module imports it. I traced `index.js` but not every module under `protocols/` **(partly unverified)**.
  - `npx` runs only the `bin`.
  - Result: dead code in the tarball at runtime. No finding.
- **Package size:** about 168 KB to 196 KB, mostly new test files. Plausible, and no finding.

### 5. The test re-aim (`tests/functional/test_pin_bump_checklist.py`)

**Before (develop):** the test required exactly the seven `--accept` entries scoped to `@2.1.4`. It ran them through the real `parse_accept` and `check_acceptances`.

**After (worktree).** Each rule and where the test enforces it:
- **The gate accepts exactly `CURRENT_ACCEPTS`, which is now empty.** `gate_problems` and `accept_problems` run a global `findall` over the whole checklist, so an `--accept` anywhere in the document is counted, not only in § 4.
- **Every `--accept` must be scoped as `GHSA:date:package@version`.** An unscoped one is reported as "lacks the … scope".
- **Every scoped package@version must be a current npm pin.** `current_npm_pins()` reads them through the script's own `load_pins`, so the test and the script use one source of truth.
- **An `@brave/` spec must equal `brave_pin()`.** `test_the_checklist_accepts_only_current_pins_and_no_void_acceptance` checks this. It also asserts that `HISTORICAL_PIN` is no longer a pin, so a silent revert to 2.1.4 fails.
- **The real script must refuse the seven void acceptances of v4.** `assertRaisesRegex(mod.AuditError, "is not a current npm pin")` checks this, with a fixed `today` of 2026-11-19. Because the date is fixed, the refusal is tested on the pin rule and not on expiry.
- **New: dropping `--signatures` from the gate is detected.** `test_mutation_a_weakened_gate_command_is_detected` covers it.
- **Mutation proofs:** they cover an unscoped acceptance, a void one (2.1.4), a stale one (2.1.3), a foreign package (`left-pad`), an unlisted acceptance on the current pin, a wrong expiry and a wrong scope.
- **The historical artifacts v3 and v4** are still checked as records scoped to `HISTORICAL_PIN`. Moving an expiry or re-scoping to the new pin is detected. Both records stay immutable.

**Ruling:** the re-aim keeps the release-audit coverage and makes it stronger.
- The rule that no `--accept` may name a version other than the current pin is now enforced in two places: in the document test (for any package, not only brave) and by the real script (exit 2).
- The weakened-gate mutation is new coverage.

**Notes. These are not findings, and both cases fail closed:**
- (a) The test's `--accept` regex recognises only lower-case `GHSA-` ids and skips `GHSA-xxxx…` as a placeholder. Any other form is invisible to the test, but `parse_accept` refuses it (`GHSA_RE.fullmatch`), so the gate fails closed. This is not new: develop had the same lookahead.
- (b) `GATE` must appear verbatim with its closing backtick. A future acceptance therefore needs `GATE`, `CURRENT_ACCEPTS` and the checklist edited together. This also fails closed, and the test comment covers it in part.
- (c) That dropping `--transport stdio` from `servers.yaml` is detected rests on T851's mutation run and another test file that I did not read **(unverified)**.

### 6. The checklist edits
- **§ 1 item 3** now says no acceptance is needed and records that the seven ended with the bump and that the script refuses them.
- **§ 4** is the gate with no `--accept`, and it keeps "the `brave` entry must keep `--transport stdio`". It also states the process for any new acceptance: the user's decision, a new artifact, scoping to a current pin, and the test listing it.
- **§ 5** adds the T851 run record.
- The edits contain no secret-shaped values (the test enforces this, and I read the text).

### 7. The drift baseline
- The edit adds one `_comment` line and exactly 4 `drift` paths: `.cline/mcp.json`, `.mcp.json`, `.opencode/opencode.json` and `.vscode/mcp.json`.
- This follows the file's own rule: declare in the merge request that makes the knowledge change without refreshing the root.
- `test_root_install_parity.py` fails on both undeclared drift and declared drift that does not exist, so the declaration cannot hide an extra path.
- No other entry changed.

## Finding statuses
- **SEC-T702-09 (MEDIUM, A06; accepted for v11.0.0 only): FIXED by this change once it merges.**
  - The vulnerable `@modelcontextprotocol/sdk` 1.30.0 and `zod` 4.3.6 are replaced by exact 1.32.2 and 4.6.7.
  - The audit at `low` shows no finding on the brave tree **(the audit run is T851's and the orchestrator's, unverified by me)**.
  - **Its acceptance has ENDED.** Its own end condition, "the first Brave release above 2.1.4", was met when 2.1.5 was published on 2026-11-17. The bump also voids it mechanically: the script refuses all seven acceptances as "not a current npm pin".
  - No new acceptance and no ADR-011 renewal is needed at the next release.
  - **Residual:** this checkout's own root self-install still launches 2.1.4 until T853, the root refresh, which needs the user's approval. That drift is declared and gate-tracked. v11.0.0 shipped 2.1.4 under the valid acceptance, and its record stays as it is.
- **SEC-T702-07 (forced stdio): holds in 2.1.5** (§ 1).
- **SEC-T702-08 (upstream issue #377, batch P): unchanged, still open as tracked.** `dist/BraveAPI/` is byte-identical **(per T849)**.
- **SEC-T756-07 (LOW, server-filesystem moderates): unchanged and tracked.** Not affected by this change.

## Findings

| ID | Severity | Category | Location | Description | Status |
|----|----------|----------|----------|-------------|--------|
| (none) | - | - | - | This review mints no new `SEC-T852-NN` id. | - |

## OWASP coverage

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01 Broken Access Control | Yes (no access-control surface changed; the agent grants and mirrors were not read, but the gates pass (unverified)) | 0 |
| A02 Cryptographic Failures | Yes (no secrets in the edits; `BRAVE_API_KEY` stays `fromEnv`, `secret: true`) | 0 |
| A03 Injection | Yes (`docker.e2e.js` uses `child_process` but is test-only and not reachable from `bin`) | 0 |
| A04 Insecure Design | Yes (the bump voids acceptances; the gate stays fail-closed) | 0 |
| A05 Security Misconfiguration | Yes (`--transport stdio` kept; HTTP is off) | 0 |
| A06 Vulnerable Components | Yes (SEC-T702-09 fixed; SEC-T756-07 LOW unchanged) | 0 new |
| A07 Auth Failures | Yes (the HTTP/OAuth paths are still unused under stdio) | 0 |
| A08 Data Integrity Failures | Yes (2.1.5 gains SLSA provenance; `--signatures` stays in the gate and its removal is tested) | 0 |
| A09 Logging & Monitoring | Yes (no logging change of note; 2.1.5 adds a non-loopback bind warning) | 0 |
| A10 SSRF | Yes (no new endpoint or outbound call reported; `BraveAPI` identical (per T849)) | 0 |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 (SEC-T702-09) | 1 (on merge) | 0 |
| LOW | 0 new | 0 | 0 new (SEC-T756-07 stays tracked) |

### Justification
- The bump removes every high advisory on the brave tree and fixes SEC-T702-09. That finding's acceptance has ended by its own terms, and the script enforces the end.
- The forced-stdio control holds.
- 2.1.5 adds provenance and no reachable new capability.
- The test re-aim makes the release-gate coverage stronger, including the current-pin rule for every `--accept`.
- The drift declaration is exact and gate-checked.
- No Immutable Security Constraint is breached, and no required control is weakened.

### Conditions
None.

**Follow-up, not a condition:** T853, the root refresh, needs the user's approval at that moment. Until it runs, this checkout's own sessions launch 2.1.4.
