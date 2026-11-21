# Security Review: T904 — plan-196 batch Y (T902 shipped text, T903 CI header comment)

**Based on:** `docs/plans/plan-196-batch-y-shipped-text.md` (read, in the T902 worktree); the diff `t902-t903.diff`; the orchestrator's `t904-evidence.md`; the style of `security-review-t900-batch-v-v1.md`. I also read `.gitlab-ci.yml`, `tests/functional/test_ci_hash_pins.py`, `docs/wiki/mcp-pin-bump-checklist.md` and `mcp-agent-denials-evidence-v2.md` through the grep tool, as on develop (grep reads the main checkout, not the worktree; the claims were checked against that).
**Reviewer:** security-engineer (read-only; no shell, so every claim is reasoned, none run).
**Date:** 2026-11-21.

## Summary
- **Risk Level:** LOW
- **Findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 LOW (new)
- **Status:** PASS (the 3 LOW are to be tracked as technical debt, as the gate protocol requires)

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| TL-T761-12 | fixed | CONTRIBUTING.md now says that `main` must not move between the tag and the end of `main-develop-drift-gate`. The last line of that job is `check-release-tag-tree.py --tag ... --main-ref origin/main` (`.gitlab-ci.yml` line 336, inside the job that starts at line 303). That line compares the tag tree with `origin/main`, so the stated mechanism and the window match the code. The claim "the drift check beside it compares only the README markers" and "develop may move" I could not verify (I did not read the script). |
| TL-T819-03 | fixed | The three tag jobs carry `tags: ["release-gate"]` (lines 270, 306, 344). The `allowed_images` coupling and the fail-closed outcome agree with checklist § 3 ("Release-gate runner at every bump"). The text points to the checklist and does not repeat the step, as the plan asked. It says an agent does not change the runner. One small gap: the checklist adds that a digest whose `linux/amd64` manifest is unchanged needs no `allowed_images` change, and CONTRIBUTING says "if a release changes the digest". That is consistent, since a changed pin is what matters. |
| TL-T761-13 | fixed | The example uses `<org>/<repo>` and `<org>-<repo>`, with a sentence that gives the substitution rule. The rule matches the old example, `em-age/emage.code` to `em-age-emage.code`. |
| TL-T780-08 | fixed | The claim "the harness ships no `.vscode/settings.json`, only `.vscode/mcp.json`" matches the orchestrator's check of `implementation/.vscode`. The hardening advice stays and is now framed for a v1-style list, so no control is weakened. It holds for installs; this checkout has its own user-owned `.vscode/settings.json`, which I did not read. |
| TD-T789-01 | partly fixed | O-2 is fixed: § 3 step (c) names the per-platform manifest media types and says the hash check still guards the result. Flag 3 is fixed and is honest: it says it was observed in tag pipeline 3039977704 and that no log was re-read. O-1 is partly fixed: see SEC-T904-01. |
| SEC-T847-01 | fixed | mcp-servers.md says evidence v2 § 4 supersedes v1 on the unmatched-name case, that the built-in rule 0 is `*: allow`, and that the reading is computed, not observed. Evidence v2 line 109 says exactly that, and it also says that how Opencode treats a name with no rule beyond the list "is not observed". The shipped text keeps "a refused or allowed tool call was not observed". Evidence v1 is untouched. K-20 stays marked unverified. |
| TL-T761-08 | fixed | The three constants exist in `tests/functional/test_ci_hash_pins.py`: `EOL_TABLE_DATE` (line 1401), `PINNED_IMAGE` (line 123) and `DRIFT_GATE_APK` (line 97, `openssl~=3.5` and `git~=2.54`). The comment's descriptions agree with the code. See SEC-T904-03 for a naming detail. |

## Dispositions you stated (not fixed in this batch)

| Id | Disposition right? | Basis |
|----|--------------------|-------|
| TL-T763-01 | Yes, if the fix lives only in a published release document or an immutable artifact (plan-196 forbids editing both). The register should say "cannot fix there" or obsolete, and name the document. | Taken from the evidence file; I did not read the source review. |
| TL-T763-02 | Conditional. The plan says the M-2 to K-35 pointer belongs in the current document that holds M-2, if one exists. The evidence says only "register to say obsolete or cannot-fix-there". It does not say that a search for a current M-2 document was done. | Not verified. If one exists, the id stays open. If none does, "cannot fix there" is right. |
| TL-T753-05 | Yes, open and deferred. The fix is in knowledge sources, so it needs mirror regeneration and a root refresh, and a root refresh needs the user's approval. It must not be recorded as fixed. | Taken from the evidence file. |
| TL-T753-07 | Yes. The T745 completed-tasks row and brief are record-only additions, and the ledger files are outside the supplied diff. | I did not read the row. The orchestrator's `validate-tasks` result (exit 0) is the only proof. |

## Answers to the probes

**1. Factual accuracy of the new claims**
- CONTRIBUTING.md: `check-release-tag-tree.py` runs last in `main-develop-drift-gate` (confirmed). The `release-gate` tag on all three tag jobs and the `allowed_images` coupling match the checklist (confirmed). The README-marker statement is not verified.
- SECURITY.md: the "no `.vscode/settings.json`" claim holds for the installed tree (orchestrator's check, taken as given).
- mcp-servers.md: rule 0 is `*: allow`, and the text says it is computed (confirmed against evidence v2 line 109).
- The CI header's three constants exist and the quoted values match (confirmed). The header says the `ca-chain-check-python` job must carry the same `apk add` list. The test refers to `DRIFT_GATE_APK` for the drift-gate job. I did not verify the ca-chain job's list.
- Checklist O-2: the two media types named are the standard per-platform ones. The statement "the registry may answer with an error without them" is hedged and I could not verify it.

**2. Does any text weaken a control or invite an unsafe action?**
- No control is weakened. The text still says no agent runs `docker`, that the configured Docker host is a production host, and that an agent does not change the runner.
- The `docker run` example is the weak point: SEC-T904-01.

**3. `.gitlab-ci.yml` is comment-only** (reasoned from the diff)
- The only change is five added lines, all starting with `#`, inside the header comment block. No job, key, value, digest or anchor is touched.
- A comment-only change cannot alter the image pin. The lint and `test_ci_hash_pins.py` runs are the orchestrator's.

**4. Immutable artifacts, releases, golden, derived folders**
- The diff touches six files: `.gitlab-ci.yml`, `CONTRIBUTING.md`, `implementation/runtime/memory/README.md`, `implementation/SECURITY.md`, `docs/wiki/mcp-pin-bump-checklist.md` and `docs/wiki/mcp-servers.md`. None is a published `docs/releases/v*.md`, an `-vN` artifact, `tests/golden` or a derived folder.
- The evidence says `--print-drift` prints `[]`, so there is no derived-copy drift from the two `implementation/` files (taken as given).
- The new T745 brief and ledger row are outside the diff.
- Link-like text: the new prose uses code spans and no parenthesised link target (reasoned from the diff; the orchestrator ran the link test).

## New findings

| Id | Severity | OWASP | Location | Scenario | Remediation |
|----|----------|-------|----------|----------|-------------|
| SEC-T904-01 | SECURITY:LOW | A05 | `docs/wiki/mcp-pin-bump-checklist.md` § 2, CI lock files bullet (TD-T789-01 O-1) | The command shown is still a plain `docker run`. The safe step is offered as "check `docker context show` and `DOCKER_HOST`, or add `--context`". So a copy-paste of the printed command still reaches the production host when `DOCKER_HOST` points at it. "Fails safe" is true only if the placeholder is replaced by a real context name. `docker context show` prints a name, not a host, so a maintainer may not see that it is production. Whether `--context` beats an exported `DOCKER_HOST` in the CLI version in use I could not verify. | Put `docker --context <non-production context> run ...` in the printed command itself, so the placeholder has to be filled in. Say "`docker context inspect <name>` shows the host". Keep the `DOCKER_HOST` check. |
| SEC-T904-02 | SECURITY:LOW | A09 (record accuracy) | register row for TL-T763-02 (to write) | If the register records "cannot fix there" without a search for a current document that holds M-2, the id is closed on an unchecked premise. | Before closing, search the current docs for M-2. If found, add the pointer to K-35 there and mark fixed. If not, say in the register row that none exists. |
| SEC-T904-03 | SECURITY:LOW | A05 (docs, drift risk) | `.gitlab-ci.yml` header comment | The header names `eol_problems_of`. The grep of the test file shows the comment `eol_image_problems` at line 1401 (`EOL_TABLE_DATE` is the day "the table in eol_image_problems was written"). The evidence says `eol_problems_of` exists as well. Two names for one table makes a maintainer's search miss. | Name the function that really holds the table, once, in both places, or say `eol_problems_of` calls it. |

## Reasoned versus not verified
- Reasoned: the diff text, the greps listed above, and the comment-only property.
- Not verified: the README-marker claim; the ca-chain job's `apk add` list; the `--context` versus `DOCKER_HOST` precedence; the T745 row; the TL-T763 documents; the orchestrator's test and lint runs.

## Recommendations (priority order)
1. Fix SEC-T904-01 in this MR if cheap (one command line). Otherwise track it as LOW debt.
2. Search for a current M-2 document before closing TL-T763-02 (SEC-T904-02).
3. Make the function name in the CI header exact (SEC-T904-03).
4. Keep TL-T753-05 open; it needs the user's approval for a root refresh.

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 | 0 | 3 |

### Justification
Of the seven ids, five are fixed (TL-T761-12, TL-T819-03, TL-T761-13, TL-T780-08, TL-T761-08) and TD-T789-01 is partly fixed (SEC-T904-01). SEC-T847-01 is fixed too. No claim I could check is wrong, no control is weakened, and the `.gitlab-ci.yml` change is comment-only. The three LOW findings are to be tracked as technical debt (gate protocol item 3).

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 0 |
| A02: Cryptographic Failures | Yes | 0 |
| A03: Injection | Yes | 0 |
| A04: Insecure Design | Yes | 0 |
| A05: Security Misconfiguration | Yes | 2 |
| A06: Vulnerable Components | Yes | 0 |
| A07: Auth Failures | Yes | 0 |
| A08: Data Integrity Failures | Yes | 0 |
| A09: Logging & Monitoring | Yes | 1 |
| A10: SSRF | Yes | 0 |

## Orchestrator's addendum (2026-11-21)

- **SEC-T904-02 checked:** the orchestrator searched the current documents for the M-2 that TL-T763-02 names. The only current `M-2` outside `docs/artifacts/` is the migration item of the v11.0.0 release notes (README line 68), which is unrelated to K-35. The release documents that mention K-35 are published (`docs/releases/v10.0.0.md`, `v11.0.0.md`, `v12.0.0.md`). So no current editable document holds that M-2: TL-T763-02 is "cannot fix there", and the register says so.
- **Run by the orchestrator:** the CI lint of `.gitlab-ci.yml` at `f9c089c5` is valid (no errors, no warnings). `validate-tasks`, `test_pin_bump_checklist`, `test_link_integrity`, `test_team_health*`, `scorecard --check` and `--print-drift` (prints `[]`) passed. The T904 ids SEC-T904-01 and -03 are tracked LOW (register v33); they were not fixed in this MR, so the suite and the pipelines are not re-run for a text change.
