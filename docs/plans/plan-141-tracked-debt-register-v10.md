# plan-141 — Tracked-debt register v10

**Created:** 2026-11-06
**Based on:** `docs/artifacts/tracked-debt-register-v9.md` (561 ids), `docs/plans/plan-140-batch-s-release-gate.md` § Outcome, and `docs/artifacts/security-review-t745-batch-s-v1.md`. The user's answer of 2026-11-06, verbatim: "1. Delete, 2. v10 go".
**Scopes:** `T746`.

## Goal

Plan-140 closed 13 ids of batch S and its review opened 11 new ones, which only the review record tracks. Since then the user deleted a CI/CD variable and a gate probe ran the tag gates for real. v10 takes all of that over, so the next fixing round and the next release start from one current list.

## Facts since plan-140 (the orchestrator's record)

These facts appear in no other artifact, so this section is their source.

**The variable (TD-T745-01).** The user's words, verbatim: "I deleted ANTHROPIC_API_KEY from Gitlab. The key was already revoked anyway." The orchestrator listed the project's CI/CD variables by name through the API on 2026-11-06: the only one left is `WIKI_TOKEN`, protected. The name stays in the `unset` line of `.gitlab-ci.yml` and in `GATE_CREDENTIALS`; that is harmless, and it can go at the next change to those lines.

**The two user actions.** Read through the API on 2026-11-06; no setting changed:
- A-17: `ci_pipeline_variables_minimum_override_role` is `no_one_allowed` and `restrict_user_defined_variables` is true.
- A-18: `v*` tags are protected and Maintainers may create them. A Maintainer can still tag a commit that never went through a merge request, so the merge guard's limit stands.

**The release candidate question.** The user said "rc go". The orchestrator had offered an RC as proof "without a real release", which was wrong: `CONTRIBUTING.md` § Pre-release tags says "There is no lighter path". An RC needs the content on `main`, creates a GitLab Release with no pre-release flag, and needs the four ADR-011 re-acceptances. Asked how to prove the untested steps, the user answered, verbatim: "Gate probe tag (Recommended)".

**The gate probe (2026-11-06).** Annotated tag `v9.0.0-gate.1` on `57612f29`, a commit on top of `615a7b0e` that was never merged and whose branch was never pushed. It changed only the three marker files and added a release document copied from v9.0.0. Pipeline 3037074733 ended `failed`, as designed:

| Job | Id | Result |
|---|---:|---|
| `release-docs-gate` | 17809865375 | success: the `unset` line ran, the hash-locked install passed, `verify-release-docs.py` passed |
| `main-develop-drift-gate` | 17809865376 | failed as designed: `apk`, both fetches and the drift check passed, then `check-release-tag-tree.py` refused the tag |
| `release` | 17809865377 | skipped; no GitLab Release was created |

Before the push, the orchestrator ran the docs gate, the drift check and the tree check locally on the tag: the first two passed and the tree check exited 1. `resolve_previous_tag` still returns `v9.0.0` for `v10.0.0` and `v9.0.1`, because a pre-release sorts below its core version.

What the probe does not prove:
- The `release` job did not run, and `scripts/publish-release.py` has changed since v9.0.0, so the `CHANGELOG.md` entry below `[Unreleased]` (D-T710-2) and the escaped references are still unobserved.
- The log shows the `unset` line ran, not that the variables were gone afterwards.
- The log reads "Fetching changes" and "Created fresh repository" on both gates. That is what a fresh runner might print under fetch as well **(unverified)**, so it shows the setting works with these jobs, not that it changed anything.
- The install is quiet, so the log does not name the parser's version; the hashes are what tie it to the lock.

**The tag's deletion.** The user approved it ("1. Delete"). `git push --delete` is refused: "GitLab: You can only delete protected tags using the web interface." The orchestrator did not try the API and handed the step to the user, so it is a user action until the tag is gone. The local tag is deleted. The tag sorts below `v9.0.0`; it does not change the previous-tag lookup.

## Task Decomposition

1. **T746** (tech-lead): write `docs/artifacts/tracked-debt-register-v10.md`, a delta on v9. Keep v9's section numbering where a section still applies. Do not repeat a row for an id that did not change: v9 and earlier stay the record of its text.
   - **Ids that changed since v9.** One row each, with the citation, from the T745 review record and plan-140 § Outcome. Closed by T743 and T744: SEC-T739-02, -03, -04, -06, -08, -09, SEC-T738-02, -06, SEC-T741-06, -07, -08, -12, -16. Open in part: TD-T739-01 (no total bound), SEC-T741-17 (a dedicated runner tag needs a runner).
   - **Ids that did not change.** Account for every other v9 `open`, `tracked-LOW` and `accepted` id, compactly, by batch or by list, as "Unchanged".
   - **One row for every new id, with the review record's grade:** SEC-T745-01 to -11, tracked-LOW. TD-T745-01: the orchestrator's id, never graded by a reviewer, closed by the user's deletion. Search the lines added in `c4ffff6f..615a7b0e` for any other id an artifact mints.
   - **The user's decisions since v9, quoted verbatim:** "S go"; "rc go"; the variable sentence above; "Gate probe tag (Recommended)"; "1. Delete, 2. v10 go". Each row claims only what this plan or plan-140 records.
   - **The orchestrator's rulings since v9**, marked as not the user's: plan-140 § Outcome, if it holds any. Also that `8ee1e2d3` was an orchestrator edit after the review and was not re-reviewed.
   - **The open items as batches.** Keep I, J, K, L, M, N, P, Q, R, T, F and U with their v9 scope.
     - **S** keeps TD-T739-01 and SEC-T741-17 and takes SEC-T745-01 to -11, which gives 13. Mark any order you give as your suggestion. Mark S as still open: no source binds it to a release.
     - The route of SEC-T735-06 and -07 is still to be settled before batch R; carry that.
     - Re-read the current lines of batch N and batch S ids that point into `scripts/verify-release-docs.py` and `tests/functional/test_ci_hash_pins.py`: plan-140 moved them. Do not re-rule them; report any id it made stale.
   - **Next release checklist:** carry v9 § 6.2 and change only what plan-140 and this plan changed.
     - **Item 14:** the probe ran the gate's install and the gate in a real job. Keep watching `release-docs-gate` at the next tag, and say what remains: the `release` job.
     - **Add:** a new CI/CD variable needs adding to `GATE_CREDENTIALS` and to the `unset` line; no test reads the project's variables.
     - **Add:** a release document may hold no HTML other than comments before its Cursor item.
     - **Add:** a change to the release script needs the same edit in `RELEASE_COMMAND`.
     - **Add:** an RC is a full release (`CONTRIBUTING.md` § Pre-release tags). A gate probe tag proves the gates without `main`, a Release or acceptances, not the `release` job; it needs the user's approval, and a protected tag can be deleted only in the web interface.
     - Re-read every line citation in § 6.2 that points into `scripts/verify-release-docs.py` or `tests/functional/test_ci_hash_pins.py`.
   - **Dates:** carry v9 § 6.3.
   - **User actions:** carry v9 § 7. Close A-17 and A-18 with the facts above, keeping the Maintainer limit. Close TD-T745-01's action. Add A-19: delete the tag `v9.0.0-gate.1` in the web interface.
   - **What stays unverified:** carry v9 § 8, drop what the probe proved, and add the four limits above and the T745 review's list. Keep separate what a real job proved, what GitLab's lint proved, and what is hand trace.
   - *Acceptance:*
     - every v9 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up and no open item is above LOW, or the register says so. Expected from the sources, to be checked and not assumed: 573 ids, 448 fixed, 46 accepted, 6 obsolete, 1 open, 72 tracked-LOW; batches I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 13, T 1, F 2, U 6, which is 73. Report any difference with the reason;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## Constraints

- The tech lead is read-only on source. T746 writes only the artifact.
- Do not read the CWSO repository. Its statuses carry over from v9.
- Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file.
- Run no mutation, and no full suite. A test run has a time limit.
- Subagents never merge. The orchestrator verifies the artifact and merges on a green pipeline.

## Outcome (2026-11-06)

- **T746 is done.** The register is `docs/artifacts/tracked-debt-register-v10.md`. It holds 573 ids, 561 from v9 and 12 new:

  | Status | Ids |
  |---|---:|
  | fixed | 448 |
  | accepted | 46 |
  | obsolete | 6 |
  | open | 1 (K-20) |
  | tracked-LOW | 72 |

- **Batches:** I 10, J 1, K 7, L 5, M 12, N 8, P 1, Q 3, R 4, S 13, T 1, F 2, U 6, which is 73. No open item is above LOW. The counts match this plan's expectation; the tech lead took the new ids from the review, not from this plan.
- **The orchestrator's check.**
  - A separate parser of the section 5 tables of v9 and v10 gives the same size for every batch other than S, and the sizes of S add up by hand. The 13 closed ids left S and SEC-T745-01 to -11 entered. SEC-T738-04, SEC-T739-01 and SEC-T739-05 also leave the section's text; they were closed before v9 and only mentioned there.
  - Each new id has one row in section 3.
  - 13 cited lines were checked on the tree: `verify-release-docs.py:149, 153, 475, 645`, `.gitlab-ci.yml:203, 209, 222, 246`, `test_ci_hash_pins.py:72`, `test_verify_release_docs.py:157, 1580`, `check-version-consistency.py:190, 221`.
- **Rulings on what the tech lead flagged.**
  - **TD-T739-01 is now graded LOW.** It stands: review T745 counts it among its LOWs.
  - **TD-T745-01 counts as `fixed`.** It stands: none of the five statuses fits better, and the row says the user closed it by deleting the variable.
  - **Item 23's "release script"** means the `script` line of the `release` job, as the tech lead read it. `RELEASE_COMMAND` pins that line.
  - **A correction to v9, SEC-T731-03.** v9 called `test_verify_release_docs.py:698` "the long-line test". That test times the parser, so the reviewer's timing test is still unwritten. The status does not change.
- **Open for the user, not ruled here.**
  - Whether any of batch S runs before the next tag. Plan-140 § Goal said to close S "before the next tag", and that sentence covered its 15 ids; no source applies it to the 13 now in S.
  - The route of SEC-T735-06 and -07, before batch R.
  - A-19: the tag `v9.0.0-gate.1` was still on the remote when this was written. The register is immutable, so the next register records its deletion.
- **Token use.** T746 used about 173k tokens (the harness's count, which includes context) against a budget of 120k.
