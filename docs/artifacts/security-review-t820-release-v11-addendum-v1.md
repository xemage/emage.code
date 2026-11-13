# Artifact: security-review-t820-release-v11-addendum-v1.md

> Immutable once produced; revisions bump `<N>`.

# Security Review T820, addendum: QA and Tech Lead findings, and the T826 document fixes (v11.0.0)

## Metadata

- **Date:** 2026-11-13.
- **Reviewer:** security-engineer. Read-only, with no shell and no write tool.
- **Addendum to:** `docs/artifacts/security-review-t820-release-v11-v1.md`. That review was read at `67222765`.
- **Inputs:**
  - `docs/artifacts/qa-gate-release-v11-v1.md` (T818). I read it in the worktree on `release/v11.0.0`. It is not on develop, so `grep_content` could not search it.
  - The T826 diff `t826-diff.patch` (commit `17158753`). It touches only `docs/releases/v11.0.0.md`.
  - The files cited in my first review.
- **Not read:**
  - The T819 artifact. I have only the TL-T819-01 reference in the diff.
  - `scripts/install.sh:925-934` and `:974-983` (the `rsync -a` calls), `implementation/runtime/memory/build.py:51-61`, `scripts/publish-release.py:289-316` and `scripts/check-main-develop-drift.py:90-96`. For these I rely on QA's quotes and runs.
- **Not run:** anything.

## 1. TD-T774-01 / QA-T818-01: `rsync -a` skips an equal-size file whose mtime falls in the same second

**Grade: `SECURITY:LOW`** (A08, integrity of the update channel). It may ship with the document mitigation. It is tracked as LOW debt under the user's LOW policy, and the user does not need to decide.

**Why LOW:**
- **What it can miss in this release:** delivery of a fix that is itself `SECURITY:LOW` (SEC-T814-01). That is an availability-only ReDoS, reachable only from the user's own MCP client over stdio (T825 § 2). A missed delivery cannot be worse than that finding.
- **No attacker controls the trigger.** It needs the target's file and the clone's file to carry mtimes in the same second. `rsync -a` copies the source mtime, so the target's mtime is the mtime of the previous clone's checkout.
  - The person path in the Migration Guide is `git fetch && git checkout v11.0.0` in an existing clone. It gives changed files a new mtime, so a person almost never meets the trigger.
  - Automation that checks out both versions, or clones and installs in the same second, can meet it. QA reproduced it this way.
  - Anyone able to set the target's mtimes can edit the file directly.
- **No required control is removed or weakened.** This is a pre-existing installer defect (TD-T774-01, known since T774). It is not a change in this release, and the release adds no code to it.
- **Mitigation:** M-6 now has a check that detects the lock case and a workaround that refreshes every source mtime.

**Regrade trigger, for the register:**
- At any later release whose fix for a `SECURITY:MEDIUM` or higher finding changes a file without changing its size, this finding takes at least that fix's grade.
- A same-length version-pin bump is a common example.
- The code fix (`--checksum`, or a compare after the copy) must then land before that release, or that release must carry a verified check for that file.
- Owner: backend-developer, through the orchestrator.

**New, LOW: SEC-T820-02 (accuracy of K-39 and M-6).**
- K-39 says "In this release that hits the two runtime lock files."
- QA saw that only in its 33-file case. In its 30-file case, five files were skipped, and QA did not name the other three **(unverified which)**.
- Those three could be any of the changed paths QA lists: the knowledge-text files of M-9, the three memory runtime files of M-5 (which carry SEC-T791-02, SEC-T791-03 and SEC-T796-01), `AGENTS.md` or the two merged configs of M-4.
- The `grep` check in M-6 detects only the lock files.
- The workaround itself covers every file: `touch` the clone, then `--update` again.

Remediation, before T821 if the Release Manager agrees:
- **K-39:** say "at least the two runtime lock files; in one QA run three more files were skipped, not identified".
- **K-39:** replace "its grade is the Security Engineer's, pending at writing" with "`SECURITY:LOW` (T820 addendum)".
- **M-6:** add that automation that clones and installs in one job should run the `touch` step before every `--update`.

If this is not done, track it as LOW.

## 2. QA-T818-03: `build.py` checks only the lower-case form of `--project-id`

**Grade: `SECURITY:LOW`** (A04: the input check is narrower than its text says).

- **It fails closed.** A wrong lower-case id gives an index that the server, which derives its id from the remote, filters to nothing, so `retrieve` returns empty.
- **No data crosses to another project, and no privilege boundary is involved.** The server's own remote-derived filter still decides, and SEC-T791-02 names every foreign `project_id` on stderr. These are QA's run and my reading of M-5. I did not read `build.py`.
- **The harm is a silent functional failure and a printed note that overstates the check.** The note at `scripts/install.sh:1746` says "the build refuses any other".
- M-5 now states the limit correctly.
- Tracked as LOW. The remediation is an equality check against the remote plus a corrected note, owner backend-developer, next release.

## 3. QA-T818-04: the probe tag is taken as the previous release

**K-32's handling is sufficient, with one addition.**

- **Effects (QA's analysis; code not read by me):**
  - The release job's `CHANGELOG.md` artifact would list only the commits since `v11.0.0-gate.1`.
  - The develop-push drift job (`allow_failure: true`) would show FAIL.
  - The Release description and the tag pipeline's drift gate (main v11, develop v11) are not affected (QA table, row 2).
  - This affects the accuracy of an artifact. It opens no security path, and no gate fails open.
- **Deleting the tag in the web UI, then checking that `git ls-remote --tags origin` shows no `gate` ref before the push, removes the cause.**
- **Addition:** the probe tag also exists in the orchestrator's local clone. A `git push --tags`, or `--follow-tags` if the probe is annotated, would re-create it on the remote.
  - So either delete it locally (`git tag -d v11.0.0-gate.1`) or push only the named ref (`git push origin refs/tags/v11.0.0`).
  - Then re-run the `ls-remote` check right after the push.
  - This belongs in T822 (condition C-4 below). K-32 itself does not need to change.

## 4. The T826 lines

| Item | Ruling |
|---|---|
| K-36 | **Fixes SEC-T820-01.** It matches plan-161 Addendum 3 point by point: commit `01fe29e4`, the user's words, pipeline 3066689514, runner #59129270, system ID `s_7371c6d24bcc`, Runner 19.5.3, the pinned digest, the fresh clone, both expected failures, `release` skipped. It also lists what is not proven: the `release` job, the fetch credential path, and that the system ID is `gitlab-runner-16028`. The runner facts are the orchestrator's and **(unverified)** by me, and the line says so |
| K-32 | **Fixes the K-32 part of SEC-T820-01** and makes the probe tag's deletion a precondition. The "in any case" wording is gone. It is accurate to QA. The local-clone addition (§ 3) goes in T822, not in the document |
| M-1 and M-2 cleanup order | **Correct and safe.** The config is edited using the sidecar's `generatorOwnedKeys` first, and only then are the listed files, including the sidecar, deleted. The Gemini procedure keeps `.env`, the user's own keys and the user's files. No step deletes a whole tree. QA ran the order on a copy. One example is **(unverified)**: the text says `prompts/prepare-release.md` is under `files`, but QA places it under `authoringOnly`. Either way the clause "a path that is already missing is fine" makes it harmless |
| M-5 | **Accurate** to QA's runs (`acme/other` exits 0, `Acme/Widget` exits 2). It honestly says the install note at `:1746` overstates the check and that the code is unchanged. `build.py:51-61` was not read by me **(unverified)** |
| M-6 lock check and workaround | **Accurate and adequate for the lock files.** If both lines show `==1.45.2`, the hashed install delivers 1.45.2. The workaround is marked **(unverified)**. Its scope is narrower than K-39 implies (SEC-T820-02) |
| K-39 | Accurate except for the scope sentence and the "grade pending" clause (SEC-T820-02) |
| K-16, O-1 | **Matches my O-1 exactly.** The record stays complete. C-1 is unchanged |
| File count (Migration Guide) | "About 35; 35 where the target's files were older, 33 (or 30) in the same second" **matches QA** (35, 33 and 30 observed) |
| Highlights, notice wording | "with a notice when the folder carries the generator's marker" **matches M-1 and M-2** and QA's symlink run |

T826 changes no accepted-MEDIUM record other than the O-1 sentence. Every ruling in § 3 of my first review stands.

## 5. Verdict

**CONDITIONAL_PASS stands.**

- No CRITICAL or HIGH finding, no breach of an Immutable Security Constraint, and no required control omitted, removed, disabled or weakened.
- The new grades are all LOW: TD-T774-01/QA-T818-01, QA-T818-03 and SEC-T820-02. They are tracked as debt and are not conditions.
- SEC-T820-01 is **fixed** by T826.
- QA-T818-02 is a document finding without a security grade, and its fix is safe (§ 4).

**Conditions:**
- **C-1 stands** (T821): the Conditions lines of the three MEDIUMs, with the SEC-T660-01 passed-deadline statement in the Conditions line itself.
- **C-2 stands** (T822): tag before 2027-01-28, while Brave `latest` is still 2.1.4 and before 2027-01-30, with the audit command passing on the tag day.
- **C-3 stands** (T822): all three tag jobs, `release` included, must show runner #59129270, or SEC-T741-17 reopens.
- **C-4 is new** (T822, owner orchestrator, with the user's deletion in the web UI). This endorses QA C3:
  - `v11.0.0-gate.1` is deleted on the remote, and also locally or by pushing only `refs/tags/v11.0.0`;
  - `git ls-remote --tags origin` shows no `gate` ref before the tag push and again right after it;
  - deadline: the v11.0.0 tag push.

QA asks for the gates to be re-run on the final tree. This addendum covers only T826's diff of `docs/releases/v11.0.0.md`, not any later commit.

### Findings Summary (whole T820 record)

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 3, shipped and user-accepted for v11.0.0 only | 3 for this release | 0 unaccepted |
| LOW | 8: SEC-T814-01, SEC-T825-01, SEC-T825-02, SEC-T784-01, SEC-T820-01, SEC-T820-02, TD-T774-01/QA-T818-01, QA-T818-03 | 4: SEC-T814-01, SEC-T825-02, SEC-T784-01, SEC-T820-01 | 4, tracked: SEC-T825-01 (a), SEC-T820-02, TD-T774-01, QA-T818-03 |
