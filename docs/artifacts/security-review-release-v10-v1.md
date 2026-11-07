# Artifact: security-review-release-v10-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T762: release-level re-check, v10.0.0

Based on: `docs/plans/plan-145-release-v10.md`; `docs/artifacts/security-review-release-v9-v1.md`; `docs/artifacts/security-review-t756-accepted-mediums-v1.md` (with "Re-grade after T765"); `docs/artifacts/ca-check-t765-v1.md`; `docs/artifacts/mcp-pin-audit-v10-v1.md`; `docs/artifacts/release-rehearsal-t759-v1.md`; `docs/artifacts/security-review-t751-batch-s-rest-v1.md`; `docs/artifacts/tracked-debt-register-v11.md` § 5, § 6.1; `docs/releases/v10.0.0.md`; `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; ADR-011, ADR-012 (grep lines); `.gitlab-ci.yml`, `scripts/run-allowlisted.py`, `scripts/publish-release.py` (by range). The tree is `/home/emage/Code/emage/worktrees/release-v10/` at `3641abfb`.

**How I read it.** No shell and no code run. `grep_content` errors on the worktree path, so its hits come from the primary checkout on `develop`, not from `3641abfb`. Those hits are marked below.

## Gate Verdict
**Gate:** security
**Status:** CONDITIONAL_PASS

## Summary
- **Risk level:** MEDIUM
- **Findings:** 0 CRITICAL open, 0 HIGH open (SEC-T756-01 closed), 5 MEDIUM accepted for v10.0.0, 5 new LOW.
- **Regressions against `v9.0.0`:** none found, within the sample in Q3.
- **Blocks:** nothing blocks. Three conditions apply to T763 and T764 (see "Conditions" below).

## Q1. Closure: SEC-T756-01 closes

Each condition I set is met:
- **The merge:** `d71002ca` merges `25e6caee`, per this session's git log.
- **The digest:** `e064671c…0fc7` is in all eight places at `3641abfb` (`.gitlab-ci.yml:53, 94, 136, 147, 182, 200, 224, 247`), and it is the digest T759 ran.
- **T759's check:** it found 3.12.16 and the raw hash once, with its controls behaving.

**Independent check:** I read `Modules/_ssl/distrusted_spki.h` at tag `v3.12.16` through a summarising fetch. Its first entry begins `43 bf fa 19 d6 ef`, is commented `CN=EM OV TLS CA - G3B`, and the array holds 8 entries. So T759 checked 1 of 8.

**What stays, none of it blocking:**
- A rejection was not observed, and "wired in" rests on the source and linked names. I did not make observing a rejection a closing condition. K-34 states this correctly and must keep saying it.
- Only x86_64 was read. The runner's architecture is **(unverified)**.
- The bump does not touch K-29, the runner's helper image, or an operator's own Python. K-34 says so.

**Record:** closed, `SECURITY:HIGH` as raised, with T765's note that the disclosed chains fail at both digests. SEC-T756-03 and -04 close with it. On -03, that the image uses the bundled Expat is only implied, and it no longer matters at 3.12.16.

## Q2. Node: not published, SEC-T756-05 stands

The page, read 2026-11-07, is still a pre-announcement. It has no CVE ids, no fixed versions and no list of issues. It says releases come "on, or shortly after, Wednesday, November 11, 2026" and "The highest severity issue fixed in the 24.x release line is HIGH."

- **LOW, still provisional.** Its reason does not depend on the content: no tag job uses Node. The default Node image and `unit-tests`' Alpine `nodejs` run only under `merge_request_event` or `$CI_COMMIT_BRANCH` rules (`.gitlab-ci.yml:92-132, 160-177`), and the three tag jobs set the Python image.
- **It still applies to branch and MR pipelines,** on repository content. Regrade it when the content is published.
- **If T764 runs after 2026-11-11,** read the advisory again first. It would change this grade only if it reached repository-content inputs, and that would not undo the tag jobs' independence from Node.
- **A Node digest bump is also an image bump.** SEC-T756-02's plan requires T765's check before it. The bump must not happen on the release branch without that check.

## Q3. The gate conclusions

**Confirmed for the release, within this sample:** no `SECURITY:CRITICAL` or `SECURITY:HIGH` is open, no Immutable Security Constraint is breached, and no required control is omitted, removed, disabled or weakened in `v9.0.0..3641abfb`.

| Area | What I sampled | Result |
|---|---|---|
| T714 | The review's verdict and rows; `validation.py:36, 107-123`, `executor.py:49-52, 90`, `poc_audit_server.py:93` (grep, `develop`) | Stricter. SEC-T714-01 (MEDIUM) fixed. The code matches M-3's lists. Residuals: SEC-T762-01 |
| T722, Copilot | `.github/agents/context-retriever.agent.md:3` at `3641abfb`: `tools: [read, search]`; review rows | Dropping a grant narrows privilege, so it is no weakening. A start failure fails closed |
| T725 | Review verdict ("stricter than before, or new and failing closed") and rows SEC-T725-01 to -03 | Not a security control. SEC-T762-05 |
| T750 | `run-allowlisted.py` in full; `.gitlab-ci.yml:198-264` | As I judged in T751. Pins and removal lines are as reviewed |
| T765 | `.gitlab-ci.yml:13-20` and the eight digests | Matches. The misquote I asked to change at line 17 is gone |
| `publish-release.py` | `:92-142`, `:612-719` | Redirects refused, header allowlisted, token out of argv, child environment allowlisted. T759 s3 to s13 agree |
| T726 | `allow_abbrev=False` at `sia-executor.py:881`, `--print-secret` at `cwso-deploy-helper.sh:264` (grep, `develop`) | Agrees with M-6. My grep for the removed option was inconclusive, so "removed" rests on the T726 review |

**Later reviews' summary tables** (grep of `docs/artifacts/security-review-t7*.md`, `develop`): rows with a non-zero MEDIUM or HIGH count are T714 (1, resolved), T718-T720 (1, resolved), T734-T736 (1, resolved), T741 (7, resolved) and T756. Register v11 § 5 and § 6.1 agree. A review written in another table format would not match this grep.

**Constraints:** constraint 1 was checked only in the documents I read in full. They hold no secret: T759's values are fake and its hash is public. I did not scan the range (shape 1).

**Not read in full:**
- `security-review-t748-batch-t-v1.md`, which I used through T751 Q7 and register v11; it matched no MEDIUM row.
- `release-v10-audit-v1.md`, of which I read lines 1-2, enough to show it exists at that path. So how T753 treated SEC-T725-02 is **(unverified)**.
- The T726-T732, T738, T739 and T745 reviews, beyond the grep above.
- Token budget: I stopped sampling near the 120k limit, so this is a sample by design.

## Q4. Every MEDIUM that ships

| Finding | State | Record in plan-145:36-45 | Deadline ahead? |
|---|---|---|---|
| SEC-T660-01, SEC-T665-01 | Not fixed, accepted | Present. Owner the user and devops-engineer. "None possible" | Review 2027-01-28, **not a fix date** |
| SEC-T657-01/SEC-T658-01 remainder | Not fixed, accepted | Present | 2027-01-31 |
| SEC-T702-09 | Not fixed, accepted | Present | 2027-01-30 or the first Brave release above 2.1.4 |
| SEC-T756-02 | Not fixed, accepted | Present | 2027-02-19, and before any earlier image bump |

**Other MEDIUMs shipped without an acceptance:** none found, with these limits:
- TD-T697-07 is not shipped, and K-section line 202 says so correctly.
- SEC-T756-07 and the moderates through `server-filesystem` are graded LOW, and that holds. A MEDIUM from T760 or T761 running beside me is unknown to me. T763 must check.

**"The user's words" rest on a record I cannot check.** plan-145 and your brief are the record; I have not seen the AskUserQuestion exchange. An agent's message is not the user's consent to me, and I treat these as a record for the top-level session to compare with what was actually asked.

**Does the answer settle the "fix" field?** **For v10.0.0, yes; for no other release, and only if the question really carried that sentence.**
- I said whether a "none possible" record satisfies ADR-011 is the user's ruling. Told that the rule asks for a fix and none exists, the user accepted. That is the ruling I said was needed.
- It does not amend ADR-011, and it sets no precedent. At the next release the question must be asked again (ADR-011, one release only).
- **plan-145:36 records only the passed-deadline sentence, not the "asks for a fix" sentence.** ADR-011's first validation item wants a reviewer to be able to check from the release document alone, so T763 must carry it. See SEC-T762-04.

**The passed deadlines.** ADR-012 counts a passed deadline as moved later, which needs a new acceptance. That acceptance was given, with new plans and dates ahead. Whether it "cures" the old deadline stays unruled, and I do not rule it here. For this gate the old plans are replaced, and the document says plainly that the point is open. This does not block.

**Is my wording usable as written? No. I made two errors, and the corrected text is below:**
1. I wrote "Current owner: the user". The plan as shown has two owners, the user for isolation and devops-engineer for documentation. ADR-012 B3 requires the plan as shown.
2. I put "A missed review counts as a passed deadline (ADR-012)" inside the record. plan-145:40 does not show that sentence to the user, so it cannot sit in a field labelled "as shown". It belongs in a separate reviewer's note, and it is my reading.

## Q5. The release document's security claims

**Accurate and not overclaimed:**
- **K-16:** "mitigated, not closed". It is the only "mitigated" I saw reading the document in full; "not a fix date"; T665 and T689 separate from the plan.
- **K-15, K-28, K-29:** plans and dates match plan-145. K-28's five high and two moderate match T755 § 3.4.
- **K-34:** one hash, rejection unobserved, what it does not fix.
- **K-17, K-26, K-30:** K-26 matches checkpoint-040:34-36. K-30 keeps every unproved line.
- **Line 41:** five findings, correct.
- **TD-T697-07:** correctly not a v10.0.0 acceptance.
- **M-3:** the listed names and refusals match the code I sampled.
- **M-6:** agrees with the two grep hits (Q3).

**Needs wording, LOW:** SEC-T762-01 (lines 38, 49, 168, 246), SEC-T762-02 (line 239), SEC-T762-03 (line 200).

**`Job-Token`: settled for the form on the wire and for GitLab accepting it, not for anything else.**
- The v10 request path adds the header with `request.add_header(credential.header, credential.token)` and sends it through urllib's opener (`publish-release.py:665-673`). The name is normalised by urllib, and header names are case-insensitive.
- v9.0.0 went through the same header name and urllib path (T686's comment at `:92-96` predates v9), and `checkpoint-040:36` records "Releases API with `JOB-TOKEN` on a protected tag: accepted (release created, body equal to the document)". I did not read v9's copy of the script; T716 and T730 changed the credential's wrapper around this code. So this is a strong inference, not a diff.
- So T759 § 11 O-1's "GitLab's acceptance stays unverified" is superseded on that point, unless the project's settings have changed since 2026-11-01 **(unverified)**.
- **It does not settle** the credential path for `git fetch` under T716's filtered environment, `GIT_STRATEGY: clone` on `release`, or the removal line. K-30 says those are unproved, and it is right.

## Q6. Dependencies, read 2026-11-07

- **Brave:** registry `latest` is 2.1.4, and its manifest declares `@modelcontextprotocol/sdk` 1.30.0 and `zod` 4.3.6.
- **Advisories:** GitHub Advisory Database returns exactly the six sdk ids for 1.30.0 and one for `zod` 4.3.6, the same seven as acceptance v3, none withdrawn. `GHSA-6prh` was updated on 2026-11-03, before T755.
- **Acceptance rule:** it holds, 84 days ahead, with condition (a) not reached.

**Could not check:**
- `npm audit` and `pip-audit` runs of my own; the other pins since 2026-11-06.
- That `--transport stdio` is still forced in every config (I rely on T755's 49 tests).
- Operators' `BRAVE_MCP_*` variables.
- Alpine 3.24.4's notes, not attempted, so SEC-T756-06 stays provisional.
- `@zereight/mcp-gitlab` and the remote servers, as in T755.

## Findings

| Id | Grade | OWASP | Location | Finding | Fix | Blocks? | Regression? |
|---|---|---|---|---|---|---|---|
| SEC-T762-01 | SECURITY:LOW | A05 | `docs/releases/v10.0.0.md:38, 49, 168, 246` | "Broad root" and K-25's "closed by T714 except its Copilot residual" omit the tracked residuals. Per SEC-T714-02, `/etc`, `/tmp`, `/dev/shm`, other homes and an empty or overridden `HOME` still pass. K-25 also leaves out SEC-T714-04, -06, -08. M-2 does not mention SEC-T722-04: an unrecognised remote's error holds the raw URL, which can carry userinfo, and that error can now reach the client log at start | In K-25, add: "T714 closes these cases with residuals, tracked: SEC-T714-02 (some broad paths and an overridden `HOME` still pass), -04, -06, -08." In M-2, add: "SEC-T722-04: the start error for an unrecognised remote prints the URL, so remove credentials from a remote URL." Edit before T763's freeze | No | No: these are residuals of a tightening |
| SEC-T762-02 | SECURITY:LOW | A05 | `docs/releases/v10.0.0.md:239` | "Nothing open in it is above LOW" uses the register's status word, and reads against five shipped MEDIUMs | "No item with the status open is above LOW; the MEDIUMs that ship are under Accepted for v10.0.0 only" | No | No |
| SEC-T762-03 | SECURITY:LOW | A02 | `docs/releases/v10.0.0.md:200`; `ca-check-t765-v1.md` § "Could not establish" 4 | K-29 lists the runner's executor as **(unverified)**, but `checkpoint-040:34` records `gitlab-runner 19.5.2`, Docker executor, from v9's job log. Also, by T765's table, with the flag on `unit-tests` and `main-develop-drift-check` are pinned, and the tag jobs are not | Say the executor was seen in v9's log on 2026-11-01 and that only the flag is unknown; say "git in the tag jobs". T764 records version and executor from the tag's log. This narrows an open point and does not change the fix, so it needs no new acceptance (my reading) | No | No |
| SEC-T762-04 | SECURITY:LOW | A04 | `docs/plans/plan-145-release-v10.md:36-45`; ADR-011; ADR-012 | Two points stay unruled: can a plan's fix be "none possible", and does a new acceptance cure a passed deadline. SEC-T660-01 and -T665-01 return at every release. The plan does not record the "asks for a fix" sentence | T763 carries that sentence. For the next register, put both questions to the user. Owner orchestrator, ruling the user, by the next release's gate | No | No |
| SEC-T762-05 | SECURITY:LOW | A05 | `install.sh:1492-1509` (review's lines); register v11 § 5, batch I | SEC-T725-02's recommended timing was "before the release that ships T725", and this release ships it unfixed. plan-145 scopes tracked batches out. Effect: a missing key or manifest reads as an empty list, so authoring-only commands stay in a target. The input is the trusted source | Keep it tracked, and tell the user the recommendation was not taken. It stays first in batch I | No | No |

Owner for -01 to -03 and -05: release-manager for the text, devops-engineer for -05 (proposed), next sprint or T763's edit.

Carried LOW, unchanged: SEC-T756-05, -06, -07, -08, batch V and the rest of register v11's tracked-LOW.

## Text for T763's Conditions block

Fill in nothing beyond this, and compare the question text and the words with the session before recording them. There is no angle bracket in it, so the gate's HTML rule does not apply.

```
- SEC-T660-01, SEC-T665-01: risk_accepted_by=@user, "Accept for v10.0.0 (Recommended)", 2026-11-07 (AskUserQuestion; the question stated that the acceptance rule asks for a fix and none exists in the harness, and that the rules do not say whether a new acceptance cures a passed deadline), grade=SECURITY:MEDIUM, release=v10.0.0, mitigation=plan as shown: owner the user (isolation), devops-engineer (documentation). Fix: none possible in the harness, none planned. Returns at every release until the agents are isolated. This plan does not end the finding: a same-user agent shell can read the GitLab token, and the exposure is mitigated, not closed. Done work, separate from this plan: T665, T689. deadline=plan as shown: a review by 2027-01-28, at the token renewal, not a fix date. A new acceptance by the user at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes.
- SEC-T657-01/SEC-T658-01 remainder: risk_accepted_by=@user, "Accept for v10.0.0 (Recommended)", 2026-11-07 (AskUserQuestion; the question stated that the rules do not say whether a new acceptance cures a passed deadline), grade=SECURITY:MEDIUM, release=v10.0.0, mitigation=plan as shown: owner devops-engineer, review tech-lead. Fix: re-check the vendors' per-agent scoping and evaluate a server-level GitLab deny on Gemini. deadline=2027-01-31. A new acceptance by the user at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes.
- SEC-T702-09: risk_accepted_by=@user, "Accept for v10.0.0 (Recommended)", 2026-11-07 (AskUserQuestion), grade=SECURITY:MEDIUM, release=v10.0.0, mitigation=plan as shown: owner devops-engineer. Fix: bump to the first Brave release above 2.1.4. deadline=2027-01-30 or that release, whichever comes first. A new acceptance by the user at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes.
- SEC-T756-02: risk_accepted_by=@user, "Accept for v10.0.0 (Recommended)", 2026-11-07 (AskUserQuestion), grade=SECURITY:MEDIUM, release=v10.0.0, mitigation=plan as shown: owner devops-engineer, review security-engineer. Fix: add the check as a step at every image bump, and settle the open points. deadline=2027-02-19, and before any earlier image bump. A new acceptance by the user at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes.
```

**Reviewer's note, not part of what was shown:** I read a missed review on 2027-01-28 as a passed deadline under ADR-012. Put this outside the Conditions block, or leave it out.

**Check before T763 uses the text:**
- Which questions actually carried which sentence. I took the passed-deadline attribution from plan-145:36 and T756's Q3 and Q4. The "asks for a fix" sentence comes from your brief alone.
- Whether plan-145's "at the token renewal" is the wording shown.

## Conditions

1. **T763** carries the block above, after the top-level session compares it with the questions asked. Any MEDIUM raised by T760 or T761 goes to the user, because no acceptance covers it.
2. **T764, immediately before the tag:**
   - `npm view @brave/brave-search-mcp-server version` still 2.1.4 and the date before 2027-01-30, or the Brave rule applies.
   - The seven-entry audit command exits 0.
   - The advisory re-read if the date is past 2026-11-11.
   - No image bump on the branch without T765's check.
   - The date before each deadline, or ADR-012 needs a new acceptance.
3. **T764, in the tag pipeline:** CONTRIBUTING's rehearsal list, plus runner version, executor and any `Job-Token` rejection from the job logs. A failure fails closed, and the tag is never moved without the user.

## Shapes for you to run

1. **Secret scan:** `poc-security-audit` `scan_secrets`, or your usual scanner, over `v9.0.0..3641abfb`. I did not scan, so constraint 1 rests on what I read.
2. **Search at `3641abfb`:** `git grep -n -i 'mitigat' docs/releases/v10.0.0.md`. I expect only K-16.
3. **Eight digests:** `git grep -c 'python:3.12-alpine@sha256:e064671c' 3641abfb -- .gitlab-ci.yml`. Expect 8, and 0 for `92abd2ba`.
4. **Identity of the files I grepped:** `git diff d71002ca 3641abfb --stat -- implementation/runtime/security/ scripts/cwso-deploy-helper.sh implementation/scripts/sia-executor.py`. Expect empty, which ties my `develop` greps to this commit.
5. **v9's request path:** `git diff v9.0.0 3641abfb -- scripts/publish-release.py`, on `gitlab_request` and `create_or_update_release`. Expect a wrapper change only. A change in how the header is sent reopens the Q5 inference.
6. **Stdio:** `python3 -m unittest tests.functional.test_mcp_package_pins`.

## Blockers

None for the verdict.

- `BLK-T762-01`: `grep_content` errors on the worktree path. Type `technical`, severity `minor`. Worked around by reading by range; shape 4 closes the gap.
- `BLK-T762-02`: the user's AskUserQuestion exchange is not available to me. Type `dependency`, severity `minor`. The top-level session compares it (condition 1).
- `BLK-T756-04`: the Node advisory is still unpublished. Type `external`, severity `minor`. It does not hold the tag.

## VERDICT: CONDITIONAL_PASS

### Findings Summary

Five carried and new MEDIUMs are counted as remaining, accepted. SEC-T756-01 is the resolved HIGH.

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 1 | 1 | 0 |
| MEDIUM | 5 | 0 | 5 (each accepted by the user for v10.0.0, per plan-145) |
| LOW (new here) | 5 | 0 | 5 |

### Justification

SEC-T756-01 closed on the merge and T759's check. No Constraint breach or weakened control was found in the sample. The five MEDIUMs have plans with deadlines ahead and the user's recorded words, which T763 must carry. The LOW items have owners and windows. It is not PASS because MEDIUMs remain.

### Conditions

- SEC-T660-01, SEC-T665-01, the remainder, SEC-T702-09, SEC-T756-02: the block above.
- SEC-T762-01 to -03, -05: owner=@release-manager, or @devops-engineer for -05 (proposed), remediation=as in the table, deadline=T763's edit or next sprint.
- SEC-T762-04: owner=@orchestrator, remediation=the user's ruling, deadline=the next release's gate.
- The three conditions above.

### Blockers

None for this verdict.

### OWASP Coverage

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes, by sample (T722 grant, carried token findings) | 0 new |
| A02: Cryptographic Failures | Yes | 1 (SEC-T762-03) |
| A03: Injection | Partial: release script and escaped entries through T759 | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T762-04) |
| A05: Security Misconfiguration | Yes | 3 (SEC-T762-01, -02, -05) |
| A06: Vulnerable Components | Yes (registry and advisory reads; no audit run by me) | 0 new |
| A07: Auth Failures | Yes, on the job token and GitLab token paths | 0 new |
| A08: Data Integrity Failures | Yes, CI pins and T751 | 0 new |
| A09: Logging & Monitoring | Partial: `publish-release.py` messages, SEC-T722-04 in SEC-T762-01 | 0 new |
| A10: SSRF | Partial: the host pin and redirect refusal (T759 s3, s4, s8) | 0 |

## Compliance Checklist

- [x] OWASP Top 10 reviewed: by sample, as in the table
- [x] Authentication secure: the two token paths were traced; K-16 is accepted, not closed
- [ ] Authorization enforced: not re-audited beyond the sample
- [ ] Input validation complete: not re-audited; T751 and T759 relied on
- [ ] Secrets management verified: documents read only; shape 1 is open
- [x] Dependencies audited: T755 plus today's reads
- [ ] Security headers configured: not applicable to this harness
- [x] Logging appropriate: within the sample

## Task completion

- **Artifact:** this text, for you to commit as `docs/artifacts/security-review-release-v10-v1.md`. No file was changed.
- **Acceptance:** all six questions are answered with evidence, findings are graded with location, fix and block status, and regressions are marked.
- **Token use:** about the 120k budget by my estimate; I cannot read the harness's count.
- **For the next register:** SEC-T762-01 to -05. Close SEC-T756-01, -03 and -04.

Sources:
- [Node.js November 2026 security releases](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases)
- [npm registry, Brave server latest](https://registry.npmjs.org/@brave/brave-search-mcp-server/latest)
- [GitHub Advisory Database, zod 4.3.6](https://api.github.com/advisories?affects=zod@4.3.6&ecosystem=npm)
- [GitHub Advisory Database, sdk 1.30.0](https://api.github.com/advisories?affects=@modelcontextprotocol/sdk@1.30.0&ecosystem=npm)
- [OSV GHSA-mrhx-c7xc-m3w5](https://api.osv.dev/v1/vulns/GHSA-mrhx-c7xc-m3w5)
- [CPython v3.12.16 distrusted_spki.h](https://raw.githubusercontent.com/python/cpython/v3.12.16/Modules/_ssl/distrusted_spki.h)

Key paths:
- `/home/emage/Code/emage/worktrees/release-v10/docs/releases/v10.0.0.md`
- `/home/emage/Code/emage/worktrees/release-v10/docs/plans/plan-145-release-v10.md`
- `/home/emage/Code/emage/worktrees/release-v10/.gitlab-ci.yml`
- `/home/emage/Code/emage/worktrees/release-v10/scripts/publish-release.py`
- `/home/emage/Code/emage/worktrees/release-v10/docs/checkpoints/checkpoint-040-release-v9.0.0.md`

## Orchestrator's record after this report

The reviewer ran no code. The orchestrator ran its shapes on `3641abfb`.

| Shape | Result |
|---|---|
| 1, secrets | `scan_secrets` on `v9.0.0..3641abfb`: `complete: false`, `truncated: true`, 500 hits of `gitlab-token` in 7 known files across 50 commits (test fixtures and docs), so **it proves nothing by itself**. Then every commit's added lines outside `tests/golden`, 21,472 lines, against token shapes (GitLab, Anthropic, AWS, GitHub, Slack, Hugging Face, JWT, private keys): **0 hits**. `tests/golden` and `scripts/scorecard.py` have no diff in the range |
| 2, `mitigat` | One line in the document, K-16 |
| 3, digests | 8 of the new, 0 of the old |
| 4, identity | No diff `d71002ca..3641abfb` in the files the reviewer grepped on `develop` |
| 5, request path | `add_header(token_header, token)` became `add_header(credential.header, credential.token)`: a wrapper change only, so the `Job-Token` inference stands |
| 6, stdio | `test_mcp_package_pins` OK |

**The Conditions text against the questions as asked.** The orchestrator compared it with its own questions. The token question carried both sentences, on the passed deadline and on the acceptance rule asking for a fix; the remainder question carried the passed-deadline sentence; the Brave and CI CA questions carried neither. "At the token renewal" is the wording shown. The attribution in the block above is right.
