# plan-148 — Node image bump after the November 2026 Node security release

**Created:** 2026-11-11
**Based on:** `docs/artifacts/tracked-debt-register-v12.md` (batch X: SEC-T756-05, SEC-T756-06; § 6.2; § 6.3); `docs/artifacts/security-review-t756-accepted-mediums-v1.md`; `docs/artifacts/security-review-t768-ca-control-v1.md`; `.gitlab-ci.yml` lines 13-20 and 42. The user's answer of 2026-11-11, verbatim: "Re-grade now, bump later (Recommended)", to the question that offered "Security Engineer re-grades SEC-T756-05/-06 against the published advisory now (docs only). I watch Docker Hub; once 24.22.3-alpine exists, DevOps bumps the digest, the APK pins and the review date, both CA-chain jobs must pass, security reviews, I merge on green." The request before it, verbatim: "Continue with the next best step".
**Scopes:** `T784`, `T785`, `T786`.

## Facts on 2026-11-11 (the orchestrator's record)

These were read on 2026-11-11 through public endpoints. Each was read once and is not re-hashed here.

- **The Node release.** `https://nodejs.org/dist/index.json` lists `v24.22.3`, dated 2026-11-10 and flagged `security`. The advisory, "Wednesday, November 11, 2026 Security Releases" (`https://nodejs.org/en/blog/vulnerability/november-2026-security-releases`), lists 7 HIGH, 6 MEDIUM and 3 LOW CVEs, plus dependency updates of llhttp, undici and sqlite. Nearly all the HIGH ones are in Node's HTTP/2 and TLS server code.
- **The image.** Docker Hub's `node:24-alpine` was last updated 2026-11-05T23:39Z, at digest `sha256:a34ab6d7f6f4813f4d0c5469d74685604b962fbdbf5793a7bc7b4998ecb867c8`. `docker-library/official-images` `library/node` tags `24-alpine` as `24.22.2-alpine3.24`. **No official image carries 24.22.3 yet.**
- **The pin.** `.gitlab-ci.yml:42` pins `node:24-alpine@sha256:06d7adf3…` (read 2026-10-22: Alpine 3.24.3, Node 24.22.1).
- **What runs on the Node image.** `ca-chain-check-node` pins it explicitly. `verify-knowledge-drift` and `sync-no-diff` get it as the default image and run `node implementation/scripts/verify.mjs` and `sync.mjs`. `unit-tests` runs on the Python image and installs Alpine's own `nodejs~=24` package. No tag job uses Node. The orchestrator found no job that starts a Node server; T784 checks this.

## Task Decomposition

1. **T784** (security-engineer, read-only). Re-grade SEC-T756-05 and SEC-T756-06 against the published advisory and Alpine 3.24.4's notes.
   - **For each CVE:** say whether any CI job, or anything this repository ships, reaches the affected code. That covers the CI jobs above, and the generated MCP entries that start Node on a user's machine through `npx`.
   - **Grade** each id, with its reason.
   - **Rule on the bump:** must it wait for 24.22.3, or is there a reason to take 24.22.2 earlier?
   - **Say what T785 must prove.**
   - The orchestrator commits the review as `docs/artifacts/security-review-t784-node-advisory-v1.md`.
2. **T785** (devops-engineer). Starts only once an official `node:24-alpine` image carries Node 24.22.3. The orchestrator checks Docker Hub; it is a dependency of type `external`.
   - **Bump the pin:**
     - Re-read the multi-arch index digest, and re-hash its body.
     - Read the Alpine version of the base layer, and re-read the `apk` package versions in that branch's APKINDEX.
     - Change the digest, the `nodejs` and `npm` pins and the comment at `.gitlab-ci.yml:13-20` together. Set `ci_images_reviewed_on` to the day of reading, as the comment describes.
   - **Check whether Alpine's `nodejs` package** for `unit-tests` already has 24.22.3. Report it, and do not wait for it.
   - **The tests that guard the pins must pass,** for example `test_ci_hash_pins` and `test_publish_release`.
   - **Acceptance:** both `ca-chain-check-python` and `ca-chain-check-node` pass in the MR pipeline, on the new digest.
3. **T786** (security-engineer, read-only). Review T785's diff and its pipeline. Close SEC-T756-05 and SEC-T756-06, or say what remains.
4. **Merge** (orchestrator): once T786 passes, the pipeline is green and the full suite has passed in a clean worktree. The merge is pinned to the verified sha, then the ledger is closed.

## Constraints

- Security agents are read-only.
- No `docker` command in any brief. Read digests through the registry API.
- Do not change a runner, CI variable or project setting.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file, and not the user's settings files.
- Subagents never merge, tag or release.

## Progress (2026-11-11)

**T784 is done: CONDITIONAL_PASS** (`docs/artifacts/security-review-t784-node-advisory-v1.md`).
- **The re-grade.**
  - SEC-T756-05 is final `SECURITY:LOW`. No CI job reaches any of the 16 CVEs.
  - SEC-T756-06 is final `SECURITY:LOW`. The only Alpine 3.24.4 fix that touches CI is a fail-closed crash in apk-tools.
  - Both close when T786 confirms the bump.
- **The bump waits for 24.22.3.** 24.22.2 is not a security release (`index.json`: `security: false`).
- **New: SEC-T784-01** (`SECURITY:LOW`, A06). The `npx` MCP entries run on the user's own Node. The condition: record it as tracked-LOW in the next register, and name the fixed Node minimums in `PREREQUISITES.md` and the v11.0.0 release document.

**The orchestrator's checks of the review's unverified points** (read on `f6c9dffb`'s tree, 2026-11-11):
- `implementation/scripts/sync.mjs` has three imports, `node:fs`, `node:path` and `node:url`. `sync.mjs` and `verify.mjs` hold no `http`, `https`, `http2`, `tls`, `net`, `zlib` or `sqlite` import, no `fetch(` and no dynamic `import(`.
- No `.js` or `.mjs` file under `tests/` (excluding `held-out` and `node_modules`) holds `createServer`, `http2.`, `node:https` or `fetch(`.
- Alpine's v3.24 `nodejs` package is still `24.22.1-r1`.
- **`implementation/PREREQUISITES.md:4` asks for "Node.js 18+"**, and line 227 for `node --version  # ≥ 18`. Node 18 and Node 20 are past end of life. This belongs to SEC-T784-01's remediation, and the orchestrator adds it to that id's row in the next register. It changes no grade.
- **BLK-T784-01 is a scoping limit, not a broken server.** `grep_content` worked for the orchestrator with `root_dir: "."` (the main checkout). The reviewer worked in a separate worktree, outside the server's root, which is the probable cause **(unverified)**. For T786, the orchestrator runs the old-digest sweep and passes on the result.

**The orchestrator's rulings (not the user's).**
- **Proof obligation 7, "the old digest nowhere".** It applies to the live files: `.gitlab-ci.yml`, `docs/wiki/mcp-pin-bump-checklist.md` and the tests. Immutable records keep the digest as history: `docs/artifacts/ca-check-t765-v1.md`, `ca-check-t767-v1.md`, `mcp-pin-audit-v10-v1.md` and this plan. `tests/functional/test_pin_bump_checklist.py:97` uses the digest only as a sample string for a secret scanner. T785 decides whether to change that line, and says why.
- **The upper bound on the wait.** If no official image carries 24.22.3 by **2026-12-11**, or by the start of v11.0.0 preparation if that comes first, the orchestrator asks the user. The hard limit is the image-review test: it fails from **2027-03-07**.
- **T785 stays `blocked`** (external, minor) until an official image carries 24.22.3. The orchestrator watches `docker-library/official-images`.
