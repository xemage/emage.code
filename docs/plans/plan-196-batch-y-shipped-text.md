# plan-196 — Batch Y: shipped text and records

**Created:** 2026-11-21
**Based on:**
- `docs/artifacts/tracked-debt-register-v32.md` (§ 5 batch Y, § 6.2);
- `docs/artifacts/tracked-debt-register-v14.md` § 5 (the batch's ids and their text), `-v17.md` (TL-T819-03) and `-v21.md` (SEC-T847-01);
- the source reviews named in each id's row (`release-v10-audit-v1.md`, `tech-lead-release-v11-v1.md`, the T761, T763, T780, T789 and T847 artifacts).

**Scopes:** `T902`, `T903`, `T904`.

## User decision (2026-11-21, verbatim)

> Y go

## Why

Batch Y (11 ids) is docs-only text and records. Its trigger is "before the next first-tag use of `CONTRIBUTING.md`", which is the next release. The orchestrator recommended it, and the user chose it.

## The 11 ids

TL-T753-05, TL-T753-07, TL-T761-08, TL-T761-12, TL-T761-13, TL-T763-01, TL-T763-02, TL-T780-08, TD-T789-01, TL-T819-03, SEC-T847-01.

## Task Decomposition

1. **T902** (technical-writer): the shipped-text ids. For each, first find the id's row in the register and its source review, re-read the current text, then fix it or say why it cannot be fixed. The writer has no shell, so it does not commit; the orchestrator commits and runs the gates.
   - **TL-T761-12 and TL-T819-03:** `CONTRIBUTING.md` § Cutting a release (the lines around 280-293). Say that `main` must not move before the tag-tree check ends, and name the `release-gate` runner and the coupling of the image digest to the runner's `allowed_images`. Read the pin-bump checklist § 3 first and point to it instead of repeating it.
   - **TL-T761-13:** `implementation/runtime/memory/README.md` (lines about 52 and 74): the example uses this repository's own index path; use a neutral example path.
   - **TL-T780-08:** `implementation/SECURITY.md` (line about 9): "v2 keeps the same defaults" is out of date. Read the file and say what is true now.
   - **TD-T789-01:** `docs/wiki/mcp-pin-bump-checklist.md`: O-1 (the maintainer `docker run` example names a non-production `docker --context`, or says to check `docker context show` and `DOCKER_HOST` first), O-2 (name the per-platform manifest media types in § 3 step (c)), flag 3 (§ 2's "watch it in the next release" for `release-docs-gate` becomes "after a change of this lock, watch it at the next release or release candidate"). Check the tests that pin this page (`tests/functional/test_pin_bump_checklist.py`) before and after; the orchestrator runs them.
   - **SEC-T847-01:** `docs/wiki/mcp-servers.md`, next to the evidence links: say that `mcp-agent-denials-evidence-v2.md` § 4 supersedes v1 on the unmatched-name claim (on opencode-ai 1.19.2 the built-in rule 0 is `*: allow`, so an unmatched name resolves to allow). Evidence v1 is immutable and stays untouched.
   - **TL-T763-01 and TL-T763-02, TL-T753-05:** find the document each names. If the fix is in a published `docs/releases/v*.md` or in an immutable versioned artifact, do not edit it: report "cannot fix there" and what the register should say instead. TL-T763-02 (a pointer from M-2 to K-35) goes in the current document that holds M-2, if one exists.
   - **Out of scope here:** `.gitlab-ci.yml` (T903), the ledger (the orchestrator), tests, and anything under `tests/golden/`.
   - If an edit under `implementation/` would make a derived platform copy (`.claude/`, `.cline/`, `.github/`, `.opencode/`) differ, say which file. Never edit the derived copies; the orchestrator declares the drift and a root refresh needs the user's approval.
2. **T903** (devops-engineer): **TL-T761-08** only. The comment header of `.gitlab-ci.yml` (lines about 25-29): the bump recipe omits the test constants. Read the checklist's list of test constants, add them to the recipe as a comment, change no job and no value. Update the tests that quote the header, if any (grep all tests with `--exclude-dir=held-out`). Lint with the GitLab CI lint at the head sha, and run `tests/functional/test_ci_hash_pins.py`.
3. **T904** (security-engineer, read-only): review T902 and T903, with a status per id. The orchestrator supplies the diffs and run evidence.
4. **TL-T753-07** is the orchestrator's: T745 has a review and no ledger row; the orchestrator adds a completed-tasks row (and a brief if the validator needs one) at closeout.

After T904: the orchestrator verifies (the gates, a clean-worktree full suite, the diff read), then one merge request, merged on a green pipeline.

## Constraints

- No `docker`.
- No runner, host, project-setting or CI-variable change. No image-digest change. No pin bump.
- No push, merge, tag or release by any agent.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`. Never edit `tests/golden/`, a published `docs/releases/v*.md`, an immutable `-vN` artifact, or a derived platform folder.
- Do not write a link-like text with a parenthesis in the target in prose (the release-document gate and the link test read it).
- Budgets: T902 70k, T903 30k, T904 40k.

## Approval

- [ ] Approved by the user

## Addendum 1 — the user's approval (2026-11-21, verbatim)

The approval line above is left for the user. In the question dialog, the user answered:

> Approve (Recommended)

That option read: "All 11 ids: T902 docs, T903 CI header comment, T904 security review."

## Outcome

**Done on 2026-11-21.**

**T902** (technical-writer, `4fb213db`; the orchestrator committed, since the writer has no shell): five files.
- **TL-T761-12 and TL-T819-03:** `CONTRIBUTING.md` says that `main` must not move before the tag-tree check ends, and names the `release-gate` runner and the digest and `allowed_images` coupling (pointing to checklist § 3).
- **TL-T761-13:** the memory README example uses `<org>/<repo>` placeholders.
- **TL-T780-08:** `implementation/SECURITY.md` says the v1 statement is dated and the harness ships no `.vscode/settings.json` (the orchestrator checked: `implementation/.vscode` holds only `mcp.json`).
- **TD-T789-01:** the checklist gets O-1, O-2 and flag 3. O-1 is partly fixed (SEC-T904-01).
- **SEC-T847-01:** the MCP wiki says evidence v2 § 4 supersedes v1 on the unmatched-name case.
- **Not fixed:** TL-T763-01 and TL-T763-02 (published or immutable documents; the orchestrator searched for a current M-2 and found none), TL-T753-05 (knowledge sources; needs mirror regeneration and a root refresh, which needs the user).

**T903** (devops-engineer, `b209e4f0`): TL-T761-08. Five comment lines in the `.gitlab-ci.yml` header name the three test constants (`EOL_TABLE_DATE`, `PINNED_IMAGE`, `DRIFT_GATE_APK`). No job, key, value or digest changed; the CI lint at the head sha is valid.

**TL-T753-07** (the orchestrator): the T745 completed-tasks row and a record-only brief were added.

**T904** (security-engineer): `docs/artifacts/security-review-t904-batch-y-v1.md`, **PASS**, three new LOW ids (SEC-T904-01 to -03), tracked.

**For register v33:**
- **Fixed:** TL-T761-12, TL-T819-03, TL-T761-13, TL-T780-08, SEC-T847-01, TL-T761-08, TL-T753-07; TD-T789-01 partly (SEC-T904-01 is its residue).
- **Cannot fix there / obsolete:** TL-T763-01, TL-T763-02.
- **Open:** TL-T753-05 (needs a root refresh and the user's approval).
- **New, tracked LOW:** SEC-T904-01, SEC-T904-03 (SEC-T904-02 was checked and closed in the artifact's addendum).
- **Batch Y** after this: TL-T753-05, TD-T789-01 (O-1 residue), SEC-T904-01, SEC-T904-03.

**Budgets:** T902 about 178k (budget 70k), T903 about 69k (30k), T904 about 88k (40k).
