# plan-150 — Take `docker` out of the image-bump checklist (SEC-T786-02)

**Created:** 2026-11-12
**Based on:** `docs/artifacts/security-review-t786-node-bump-v1.md` (§ 3, SEC-T786-02, its remediation and example wording); `docs/artifacts/tracked-debt-register-v13.md` (SEC-T786-02, batch Y); `docs/plans/plan-148-node-image-bump.md` (§ Constraints, § Outcome); `docs/artifacts/ca-check-t765-v1.md` (the registry-layer method). The user's instruction of 2026-11-12, verbatim: "Fix SEC-T786-02".
**Scopes:** `T788`, `T789`.

## Goal

`docs/wiki/mcp-pin-bump-checklist.md` is the image-bump procedure. Two places in it tell the reader to start a container:
- **§ 3 (line 30):** "run the image to read its Alpine and runtime versions";
- **§ 2 (line 26):** the musl install check `tar c ci | docker run --rm -i python:3.12-alpine@sha256:<pinned digest> …` against "a remote Docker host".

The project's configured Docker host is a remote production host. An agent that follows the checklist could start a container there. T785 bumped the Node image without Docker, and § 3 already names that method for the CA check, so the checklist can say the same for the version read. § 3 also ends with a stale note, "the first real pipeline is still the proof **(unverified until it runs)**", although pipelines have run these jobs since. SEC-T786-02 (SECURITY:LOW, A05, batch Y) asks for a docs fix.

## Task Decomposition

1. **T788** (technical-writer): edit `docs/wiki/mcp-pin-bump-checklist.md` only.
   - **§ 3:** replace "run the image to read its Alpine and runtime versions" with reading, from the registry, without Docker:
     - the index, the `linux/amd64` manifest and its config blob, each body hashed against its digest;
     - the runtime version from the config's `Env` (`NODE_VERSION`, `PYTHON_VERSION`);
     - the Alpine version from the config history (`alpine-minirootfs-<version>-x86_64.tar.gz`) or from `/etc/alpine-release` in the base layer;
     - `apk-tools` and other installed packages from `/lib/apk/db/installed` in the top-most layer that holds it, listed or read with a tar reader and nothing extracted or run (method: `docs/artifacts/ca-check-t765-v1.md`).
   - Name the MR pipeline's `node --version` line in `verify-knowledge-drift` as the proof of the Node that ran. It is `.gitlab-ci.yml:134` today; cite it by job name, not by line. Python has no such line; say that the `unit-tests` log's own output is the evidence there only if it is, and otherwise say nothing about a Python runtime proof.
   - Replace the stale note with what is true:
     - the jobs have run in pipelines since;
     - the CA-chain jobs (the next paragraph) and the Node line are the per-bump proof.
   - **§ 2:** mark the `docker run` musl install check as a **maintainer-only** step, on a Docker host that is not production. It is never an agent step. The MR pipeline's `unit-tests`, `validation-super-gate` and (on a tag) `release-docs-gate` jobs install the locks in the pinned image anyway, which is the routine proof. Keep the command itself for the maintainer.
   - Keep every phrase that `tests/functional/test_pin_bump_checklist.py` requires (`REQUIRED_PHRASES` and `IDS`, lines 16-27). In particular, `(unverified)` must stay somewhere in the page (line 5 has it), and `ci_images_reviewed_on`, `--only-binary=:all:` and `--exclude-newer` must stay. Every backticked repository path must exist.
   - Cite SEC-T786-02 where the text changes.
   - *Acceptance:*
     - the page has no instruction for an agent to run `docker`, and no "run the image";
     - the method is complete enough to repeat;
     - the test passes;
     - no other file changes.
2. **T789** (security-engineer): review T788's diff against SEC-T786-02's remediation (T786 § 3). Give the id its final status and a verdict. Read-only.
3. **The orchestrator:**
   - runs the gates and the full suite in a clean worktree, and the MR pipeline;
   - commits the review as `docs/artifacts/security-review-t789-pin-checklist-v1.md`;
   - closes T788 and T789, and merges on green.
   - SEC-T786-02's new status goes into the next register (v14), through this plan's Outcome.

## Constraints

- Docs only: no code, no test change, no CI change.
- No `docker` command anywhere in this plan's work.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- The technical writer has no shell: the orchestrator commits, runs the tests and pushes.
- Subagents never merge.

## Outcome (2026-11-12)

- **T788 is done** (commit `dad17100`). `docs/wiki/mcp-pin-bump-checklist.md` changed in § 2 and § 3 only:
  - § 3 now reads the image versions from the registry and the layers without Docker, with every body hashed and nothing extracted or run;
  - it names the `node --version` line of `verify-knowledge-drift` as the runtime proof;
  - the stale "(unverified until it runs)" note is replaced;
  - § 2 marks the `docker run` musl check as maintainer-only on a non-production host, never an agent step.

  The orchestrator kept the writer's two added registry API details (the `Accept` media types and the `/blobs/<digest>` endpoint). They are the request shape T785 and the orchestrator used for the plan-148 reads.
- **T789 is done: PASS** (`docs/artifacts/security-review-t789-pin-checklist-v1.md`). **SEC-T786-02 is fixed**, closing on this merge. There are no new findings. For register v14: SEC-T786-02 is fixed by T788 and reviewed by T789, and batch Y drops to 8.
- **The orchestrator's checks:**
  - only the page changed, 2 lines;
  - no "run the image" and no "unverified until it runs" remain;
  - `test_pin_bump_checklist`, `test_link_integrity` and the ledger validator pass;
  - the full suite and the MR pipeline run before the merge.
- **T789 § 6 item 5, settled.**
  - In the v10.0.0 tag pipeline 3039977704, job 17831135512 (`release-docs-gate`) ran the hash-locked `ci/requirements-release.txt` install and succeeded on 2026-11-07.
  - The lock last changed in `9e43d135` (2026-11-05, T739), before the tag commit `d593aeb3` (2026-11-07), so that run installed today's lock.
- **TD-T789-01** (the orchestrator's id, no `SECURITY:*` grade; for register v14, batch Y): the next edit of the checklist page takes up T789's optional observations:
  - **O-1:** make the maintainer `docker run` command name a non-production `docker --context`, or check `docker context show` and `DOCKER_HOST` first, so a copy-paste fails safe;
  - **O-2:** name the per-platform manifest media types in § 3 step (c);
  - **flag 3:** § 2's "watch it in the next release" for `release-docs-gate` gets the v10.0.0 observation above and becomes "after a change of this lock, watch it at the next release or release candidate".
