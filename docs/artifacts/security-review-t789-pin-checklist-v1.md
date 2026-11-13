# Artifact: security-review-t789-pin-checklist-v1.md

> Immutable once produced; revisions bump <N>.

Based on:
- `docs/artifacts/security-review-t786-node-bump-v1.md` § 3 (SEC-T786-02: text, remediation, example wording)
- `docs/plans/plan-150-pin-checklist-no-docker.md` (task T788, its acceptance items, § Constraints)
- `docs/tasks/task-T789.md`
- `docs/wiki/mcp-pin-bump-checklist.md` at `dad17100` on `agent/technical-writer/T788`: read whole in the worktree, with § 2 at line 26 and § 3 at lines 28-32
- The orchestrator's word diff of that file (`t788.diff`, one hunk, lines 23-33 of the page)
- `docs/artifacts/ca-check-t765-v1.md` lines 1-40 (§ Method, the method cited)
- `.gitlab-ci.yml` on develop (main checkout; per the orchestrator, T788 does not change it): job headers, `image:` keys, `pip install` lines, rules, and the `node --version` line
- `docs/checkpoints/checkpoint-041-release-v10.0.0.md` line 17, and `docs/artifacts/tracked-debt-register-v10.md` / `-v11.md` item 14 (only for the writer's flag 3; found by grep on develop)
- Latest checkpoint: `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md` (not re-read; nothing here depends on it)

Task: T789 (plan-150). The user's instruction, verbatim: "Fix SEC-T786-02". Producer: security-engineer, read-only. I changed no file.

## Summary
- **Risk level**: LOW
- **Findings**: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW open. The one LOW in scope, SEC-T786-02, is resolved. There are no new findings.
- **Status**: PASS

All four parts of the remediation are met. After the change, the page tells no agent to run `docker`:
- **§ 3** gives a complete registry-only method. Every blob is hash-checked, and layers are read in memory with nothing extracted or executed.
- **§ 3** names the `node --version` line of `verify-knowledge-drift` as the runtime proof. It cites the job by name and makes no claim about a Python runtime proof.
- **§ 3** replaces the stale note with an accurate statement of what the per-bump proof is.
- **§ 2** now makes the `docker run` musl check a maintainer-only step on a non-production host. It also says agents run no `docker` for any step of the page, which goes further than the remediation asked.

No security control is removed or weakened. The change moves the routine proof onto the merge request pipeline, which already enforces it.

## 1. The remediation checked against the diff

| # | Part of the SEC-T786-02 remediation (T786 § 3) | Result | Evidence |
|---|---|---|---|
| 1 | **§ 3: read the versions from the registry layers with no Docker**, in place of "run the image to read its Alpine and runtime versions" | **Met** | Line 30 removes "run the image…". It adds "read everything from the Docker Hub registry API, with no Docker: nothing is pulled into a container, extracted or run (SEC-T786-02; the method of `docs/artifacts/ca-check-t765-v1.md`…)". Steps (a)-(f) cover all three items the remediation named:<br>- runtime version from the config's `Env` (`NODE_VERSION`, `PYTHON_VERSION`): step (d);<br>- Alpine version from the config `history` (`alpine-minirootfs-<version>-x86_64.tar.gz`) or `/etc/alpine-release`: step (e);<br>- `apk-tools` and the other packages from `/lib/apk/db/installed` in the top-most layer that holds it: step (f).<br>Integrity matches the T765 method (`ca-check-t765-v1.md:20`). The index body must hash to the pinned digest (b), and the amd64 manifest, the config and every layer are each hashed against their digest (c). The tar handling is stricter than T765's: T765 extracted one member with `filter="data"`, and the new text says "extract nothing and execute nothing". The anonymous pull token carries no secret. The method can be repeated as written (observation O-2 is a convenience only). |
| 2 | **Name the `node --version` line of `verify-knowledge-drift` as the runtime proof** | **Met** | Line 30: "The proof of the Node that actually ran is the merge request pipeline's `verify-knowledge-drift` log: its `node --version` line must print the config's `NODE_VERSION` (T785: `v24.22.3`)". The line is cited by job name, as plan-150 asked. `.gitlab-ci.yml:131` (job header) and `:134` (`- node --version  # the Node that ran…`) confirm it is in that job. `v24.22.3` matches the T786 obligation 2 evidence. The text claims no Python runtime proof, which follows plan-150's "otherwise say nothing". |
| 3 | **Drop the stale "(unverified until it runs)" note** | **Met** | Line 30 removes "the first real pipeline is still the proof **(unverified until it runs)**". It adds "since then the pipelines have run these jobs, so that one-off run is history, not the proof. The per-bump proof is the merge request pipeline on the new digest: the two CA-chain jobs of the next paragraph and the `node --version` line of `verify-knowledge-drift` (SEC-T786-02)". This matches the jobs at `.gitlab-ci.yml:160`, `:181` and `:131`. The page-level "(unverified)" marker on line 5, which the test requires, is kept. |
| 4 | **§ 2: mark the `docker run` musl check as maintainer-only on a non-production Docker host, never an agent step** | **Met** | Line 26: "An install check before pushing is a **maintainer-only step, on a Docker host that is not production, and never an agent step** (SEC-T786-02): the project's configured Docker host is a remote production host, so an agent does not run `docker` for this or for any other step of this page." The command is kept for the maintainer, as plan-150 asked. The routine proof it names is accurate:<br>- `unit-tests` installs `ci/requirements-ci.txt` (`.gitlab-ci.yml:95` image, `:119`) on the merge request rule (`:128`);<br>- `validation-super-gate` installs `ci/requirements-gate.txt` (`:142`, `:144`, `:148`);<br>- `release-docs-gate` installs `ci/requirements-release.txt` (`:254`, `:270`) only on the tag rule (`:274`);<br>- all three use `--require-hashes --only-binary=:all:` in the pinned `python:3.12-alpine@sha256:e064671c…` image. |
| — | **No other `docker` instruction left on the page** | **Met** | I read the whole page. The only `docker` command left is the maintainer-only one in § 2. The CA paragraph (line 32) already said "no Docker". Line 34 ("On 2026-11-02 the install ran in the pinned `python:3.12-alpine` image") is a record of a past run, not an instruction. |

## 2. Final status

| Id | Grade | Final status | Reason |
|---|---|---|---|
| **SEC-T786-02** | SECURITY:LOW (A05) | **Fixed: closes** when T788 (`dad17100`) merges to `develop` | All four parts are met (§ 1). The hazard is gone: no step of the page directs an agent to start a container, and the page now forbids it outright. The two version-read instructions now use the safe registry method that the T785 bump actually used. Record it in register v14 through plan-150's Outcome, as fixed by T788 and reviewed by T789. |

## 3. New findings

None. The observations below carry no SECURITY:* grade and no id. Each one says why.

- **O-1. The maintainer command does not pick its Docker host.** Line 26's `tar c ci | docker run …` targets whatever host the shell is set to use. In this devcontainer, that is the production host. The bold instruction just before the command, "on a Docker host that is not production", covers this. The person acting is the host's owner, not an agent, so this is not a gap in the SEC-T786-02 fix.
  - **Optional hardening at the next edit:** write `docker --context <non-production context> run …`, or add "check `docker context show` and `DOCKER_HOST` first". A copy-paste would then fail safe.
  - **Why no id:** the remaining risk needs a person to ignore an explicit instruction placed right before the command.
- **O-2. Step (c) does not name the media types for the per-platform manifest.** Fetching by digest may need `application/vnd.oci.image.manifest.v1+json` or `application/vnd.docker.distribution.manifest.v2+json` in `Accept`. A reader who leaves them out gets a registry error, not a wrong result, because every body is hash-checked. This is about repeatability, not security.
- **O-3. "the runner is x86-64" (writer's flag 2).** This rests on the `AMD Ryzen 7 2700X` CPU lines, read in T786 (obligation 1) and in the orchestrator's 14 job logs. It does not rest on the runner's configured platform (A-21). If a different runner is ever used, the `node --version` line and the CA jobs would still show which image ran. No change is needed.
- **Writer's flag 1 (media types in (b), `/blobs/<digest>` in (c)):** these are correct registry API facts. They are the OCI image index and Docker manifest-list types, and the blob endpoint is standard. They agree with the T765 method.

## 4. Writer's flag 3: `release-docs-gate` in § 2 (out of scope)

The sentence is: "`release-docs-gate` runs only in a tag pipeline, so no merge request pipeline proves this install: watch it in the next release or release candidate."

- **First half: current.** The job's only rule is the tag rule (`.gitlab-ci.yml:274`), and no merge request pipeline runs `:270`.
- **Second half: stale as a status, still valid as an instruction.**
  - It has been watched three times: the probe pipelines 3037074733 and 3038460622 (registers v10 and v11, item 14), and the v10.0.0 tag pipeline 3039977704, which "passed `release-docs-gate`, `main-develop-drift-gate` and `release`" (checkpoint-041 line 17).
  - Read as a step after any change to `ci/requirements-release.txt`, it is still right: such a change is first proven at the next tag.
  - The exposure is small. The lock's versions and hashes must equal those in `ci/requirements-ci.txt`, which `unit-tests` installs in every merge request pipeline. So the only part a merge request does not prove is the job's own install line.
- **My view:** this is a documentation-accuracy point with no security grade, so no SEC id. If the orchestrator wants it tracked, a TD or TL id fits better. Suggested wording for the next edit: "…so no merge request pipeline proves this install (observed in the v10.0.0 tag pipeline 3039977704); after a change of this lock, watch it at the next release or release candidate."

## 5. Verdict

## Gate Verdict
**Gate:** security
**Status:** PASS

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 1 | 1 | 0 |

### Justification
- All four parts of SEC-T786-02's remediation are met against the diff and the page at `dad17100` (§ 1). SEC-T786-02 closes on merge (§ 2).
- No CRITICAL, HIGH or MEDIUM finding, and no new finding.
- No Immutable Security Constraint is breached:
  - no secret (the token request is anonymous);
  - no PII;
  - no check bypassed;
  - no new input path;
  - no privilege change;
  - no data at rest.
- No required control is omitted, removed or weakened. This change edits docs only. It moves the routine lock and runtime proof onto merge request jobs that already enforce `--require-hashes --only-binary=:all:`, the digest pins and the CA-chain checks. It also forbids agent `docker` use on the whole page.
- PASS rather than CONDITIONAL_PASS, because no MEDIUM finding remains and the review raises no new LOW. The other LOW items of T786 are already in register v13 and outside this scope. O-1 to O-3 and flag 3 have no grade.

### Conditions (if CONDITIONAL_PASS)
Not applicable.

### Blockers (if FAIL)
Not applicable.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (out of scope) | 0 |
| A02: Cryptographic Failures | Partial (digest and blob hash verification in the method) | 0 |
| A03: Injection | Partial (the maintainer command takes no user input) | 0 |
| A04: Insecure Design | Partial (agent and production-host boundary in the procedure) | 0 |
| A05: Security Misconfiguration | Yes (procedure text) | 1 resolved (SEC-T786-02) |
| A06: Vulnerable Components | Partial (version-read method for image bumps) | 0 |
| A07: Auth Failures | No | 0 |
| A08: Data Integrity Failures | Yes (content-addressed reads, hash-locked installs named as proof) | 0 |
| A09: Logging & Monitoring | Partial (the `node --version` log line as evidence) | 0 |
| A10: SSRF | No | 0 |

### Compliance Checklist (scope: T789 only)
- [ ] OWASP Top 10 reviewed: partial, see the table above
- [x] Secrets management verified for the change: no secret added; the token request is anonymous
- [x] Dependencies audited: not applicable (no pin changed); the method for future audits is reviewed
- [ ] Authentication, authorization, input validation, headers: not in scope

## 6. Not verified **(unverified)**
1. **Which files changed.** I relied on the orchestrator's check that only the page changed (2 lines). I have no git tool. I read `.gitlab-ci.yml` on develop in the main checkout, not in the worktree.
2. **`tests.functional.test_pin_bump_checklist`, `test_link_integrity` and the ledger validator.** I did not run them; the orchestrator reports them passing.
3. **Docker Hub's handling of a per-platform manifest fetched without a matching `Accept` header (O-2).** Not tried live.
4. **The `AMD Ryzen 7 2700X` CPU lines.** These come from T786's evidence and the orchestrator's log reads; I read no job logs. The runner's configured platform is still not read (A-21).
5. **That `release-docs-gate` ran the current `ci/requirements-release.txt` in pipeline 3039977704.** This rests on checkpoint-041's text. I did not check that the lock is unchanged since then.

## Blockers
None.

## Task completion
- **Artifact:** this text, committed by the orchestrator as `docs/artifacts/security-review-t789-pin-checklist-v1.md`. The reviewer changed no file.
- **Acceptance criteria (`task-T789.md` § 4):**
  - Each part of the remediation is checked against the diff: met (§ 1).
  - SEC-T786-02 has its final status, fixed and closing on merge: met (§ 2).
- **Follow-ups (optional, none blocking):**
  - O-1: name a non-production `--context` in the maintainer command;
  - O-2: name the manifest media types in step (c);
  - flag 3: record the tag-pipeline observation in § 2. If tracked, give it a TD or TL id, not a SEC id.
- **Next step:** SEC-T786-02 goes to register v14 as fixed (T788, reviewed in T789) through plan-150's Outcome.
