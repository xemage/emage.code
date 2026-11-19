# plan-177 — Batch X: CI images, the CA control and runner settings

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v23.md` (§ 5 batch X; § 6.3, where the CI image review fails from 2027-03-12);
- `docs/artifacts/security-review-t768-ca-control-v1.md` (SEC-T768-01 to -05; SEC-T756-02 re-graded LOW);
- `docs/artifacts/security-review-release-v10-v1.md` and the T756 reviews (SEC-T756-02, -07, -08);
- `docs/artifacts/tech-lead-release-v10-v1.md` (TL-T761-11);
- `docs/artifacts/security-review-t811-release-gate-runner-v1.md` (SEC-T811-05);
- `docs/wiki/mcp-pin-bump-checklist.md` (§ 1 and § 3).

**Scopes:** `T859`, `T860`, `T864` (the root refresh, added with the user's approval). AB runs in parallel as plan-178.

## User decision (2026-11-19, verbatim)

> X + AB go

## Task Decomposition

1. **T859** (devops-engineer), one branch with separate commits:
   - **(a) The CI image review** (checklist § 3, read from the Docker Hub registry API only, without Docker):
     - Re-read the current digests of `node:24-alpine` and `python:3.12-alpine` and their versions.
     - Bump each image that has a newer digest, with both CA jobs passing.
     - Set `ci_images_reviewed_on` to the review date only after a real review.
     - **If the `python:3.12-alpine` digest changes,** the release-gate runner's `allowed_images` (user side, gitlab-runner-16028) must be updated before the next tag. Write the exact user step; do not touch the runner.
   - **(b) The CA control:**
     - **SEC-T768-01:** match `BEGIN (TRUSTED |X509 )?CERTIFICATE`, fail on any other `BEGIN` type, and assert that the certificates read equal the PEM blocks.
     - **SEC-T768-02:** cross-check the fixtures (every root and non-leaf SPKI listed; counts per directory), and run `sha256sum -c` in both jobs.
     - **SEC-T768-03:** a guarded `--capath /etc/ssl/certs` run when hashed entries exist.
     - **SEC-T768-05:** re-count, and issue `ca-check-t767-v2.md` or fix the expected count.
   - **(c) SEC-T756-08:** `scripts/sync-wiki.py` must refuse redirects, as `publish-release.py` does.
   - **(d) SEC-T756-07:** the `server-filesystem` moderates (`glob` GHSA-3g3m-2fjr-6pw4, `minimatch` GHSA-g3hv-75wg-m249). Bump the pin if a release fixes them, following checklist § 1, and declare the root drift. Otherwise record that no fix exists.
   - **(e) Tag-job items** (SEC-T768-04, TL-T761-11). The tag jobs are frozen, so change them only if (a) forces a tag-job edit. Otherwise record "trigger not reached" and add TL-T761-11's note beside the `FF_GIT_URLS_WITHOUT_TOKENS` open point.
   - **(f) SEC-T811-05:** write the exact user-side runner hardening steps: restrict services with the option names verified for the installed runner version, patching cadence, and nothing else in the LXC. **The user applies them.** No server change by any agent.
   - **(g) SEC-T756-02:** re-check whether anything in (a) or (b) closes it, or whether it stays LOW-tracked.
   - **For every change:** tests and mutations.
2. **T860** (security-engineer, read-only): review T859, with a status per id.

## Constraints

- No `docker` (`DOCKER_HOST` is the user's production host).
- No runner, host, project-setting or CI-variable change.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`.
- A root refresh, if (d) bumps a pin, needs the user's approval at that moment.

## Outcome

**Done on 2026-11-19.**

**T859** (devops-engineer), commits `71d8b2ae`, `d8e24104`, `71afeec9`, `6f793834` and `108a1215`:
- **(a) The CI image review, read through the registry API without Docker.**
  - `node:24-alpine`: no newer digest.
  - `python:3.12-alpine`: the tag now resolves to `sha256:c5ba3dee…`. Only its `linux/riscv64` entry differs; the `linux/amd64` manifest `sha256:a61cbd76…` is byte-identical.
  - **The pin is kept.** This is the orchestrator's ruling after an independent registry check, and the user confirmed it: "Refresh, keep python pin (Recommended)". So no tag-job edit and no runner `allowed_images` change.
  - `ci_images_reviewed_on` is now **2026-11-19**, which moves the failure date from 2027-03-12 to 2027-03-20.
  - Alpine 3.24 now ships `nodejs` 24.22.3, which covers SEC-T786-01.
- **(b) The CA control.**
  - **SEC-T768-01:** fixed. The scan reads the `TRUSTED` and `X509` forms, fails on any other `BEGIN` type, and asserts the certificate count. A silent empty-hash bug in `spki_of` was also fixed.
  - **SEC-T768-02:** fixed.
    - The new fixture cross-check found two rollover keys of `EM DV TLS CA - G3B` that were not listed. They are added, so the list has 14 keys.
    - `sha256sum -c` now runs in both CI jobs.
  - **SEC-T768-03:** fixed, with a guarded `--capath` run.
  - **SEC-T768-05:** fixed in `ca-check-t767-v2.md` (3 extra certificates).
- **(c) SEC-T756-08:** fixed. `sync-wiki.py` refuses redirects.
- **(d) SEC-T756-07:** fixed. `server-filesystem` moves 1.0.0 → 2.4.0: its tree has no `glob`, and minimatch is 11.0.9. The audit is clean and it has provenance. Its HTTP transport is not reachable from our stdio launch line.
- **(e) SEC-T768-04:** trigger not reached. **TL-T761-11:** a note added beside A-21's flag point.
- **(f) SEC-T811-05:** user-side runner hardening steps written into checklist § 3. **The user applies them.**
- **(g) SEC-T756-02:** stays LOW.

**T860** (security-engineer): `docs/artifacts/security-review-t860-batch-x-v1.md`, **CONDITIONAL_PASS**.
- **The condition, SEC-T860-03:** the checklist said A-21's flag state was "still unreported". Register v18 closed A-21 on the user's report. **Met:** the orchestrator corrected the sentence in `17f16d36`.
- **New, LOW, tracked:**
  - **SEC-T860-01:** no minimum release age for `npx` pins. The 2.4.0 pin was one day old, which is acceptable here.
  - **SEC-T860-02:** the runner steps lack a check that `services_limit` takes effect, and an out-of-cycle patch trigger.
- **Statuses:**
  - **Fixed:** SEC-T756-07, SEC-T756-08 and SEC-T768-01, -02, -03, -05.
  - **Open, LOW:** SEC-T756-02, SEC-T768-04, TL-T761-11 and SEC-T811-05 (a user action).

**The merge with develop.** Batch AB (MR !702) merged first, so develop was merged into this branch (`dbf390db`). Two conflicts were resolved:
- the registry was regenerated;
- the drift baseline keeps both comments, with this branch's 3 paths.

**T864** (orchestrator): the root refresh, approved by the user ("Refresh, keep python pin (Recommended)").
- `install.sh --projections-only` changed exactly `.mcp.json`, `.cline/mcp.json` and `.opencode/opencode.json`: 3 pin lines, 1.0.0 → 2.4.0.
- The drift is `[]`.

**The orchestrator's own verification:**
- The registry API: the amd64 digest is identical under both python indexes.
- I recomputed the SPKI sha256 of every fixture certificate:
  - every non-leaf certificate in `compromised/` carries a listed key, including the three `EM DV TLS CA - G3B` keys;
  - the leaf certificates and `control/` are not listed;
  - `sha256sum -c` passes.
- The CI diff touches only the header and the two CA jobs.
- The main checkout holds only the user's own edits.
- The gates, the full suite and the pipeline are recorded in the merge request.

**User action (SEC-T811-05, with SEC-T860-02):** apply the runner steps in checklist § 3:
- set `services_limit = 0`;
- check the runner log for an unknown-key warning;
- keep Docker Engine, GitLab Runner and the kernel patched;
- run nothing else in that LXC.

**For register v24:**
- **Fixed:** SEC-T756-07, SEC-T756-08, SEC-T768-01, -02, -03, -05.
- **Minted and fixed:** SEC-T860-03.
- **New, LOW:** SEC-T860-01, -02.
- **The new date:** the CI image review fails from 2027-03-20 (2026-11-19 + 120 days).

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T859 | 115k | 120k |
| T860 | 40k | 50k |
| T864 | under 10k | — |
