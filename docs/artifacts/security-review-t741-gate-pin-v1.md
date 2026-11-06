# Artifact: security-review-t741-gate-pin-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewers**: two security-engineer agents, read-only, with no shell. The orchestrator recorded this artifact from their reports.
  - **First review**, of `201f2954`: one agent.
  - **Second review**, of `ec2ea70b`, then two narrow re-checks of `036b4e47` and `68a70735`: a second agent, resumed on the user's decision. The narrow re-checks read only their round's diff.
- **Gate**: security. **Dates**: 2026-11-05 and 2026-11-06.
- **Target**: T741 (plan-138), `agent/devops-engineer/T741` at `68a707354425d141358df28982639de7a0eb0d09`.
- **Who wrote what**: a devops-engineer agent wrote `b9b62187`, `201f2954` and most of `b23c756f`. It stopped in a devcontainer reboot, so its second report does not exist. The orchestrator finished `b23c756f` on the user's "Finish T741 yourself" and wrote `ec2ea70b`, `036b4e47` and `68a70735`. The second reviewer was told this.
- **Based on**:
  - `docs/plans/plan-138-gate-pin-and-strict-read.md`
  - `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4
  - `scripts/verify-release-docs.py`, `tests/functional/test_ci_hash_pins.py`, `tests/functional/test_publish_release.py`, `tests/functional/test_verify_release_docs.py`, `tests/functional/test_knowledge_template_images.py`, `.gitlab-ci.yml`
- **Tools**: `grep_content` rejects a worktree path, so searches reflect `develop` and were combined with Read. No dependency changed, and no audit ran.
- **Orchestrator's checks**, run live, because the reviewers traced by hand:
  - **GitLab's CI lint** (read-only, `POST /projects/:id/ci/lint`, with `include_merged_yaml`; `dry_run` with a `ref` creates no pipeline), on the real file plus each edit. "Pin" is `ci_pin_problems` at `68a70735`, and "GitLab" is the effect on `release-docs-gate`:

    | Edit | Pin problems | GitLab |
    |---|---:|---|
    | A trailing `<<: {script: ["exit 0"]}`; a quoted `"<<"` | at least 1 | runs `exit 0` |
    | `:release-docs-gate:`, `!!null release-docs-gate:`, `!!binary PDw=:`, `? :release-docs-gate`, `!ruby/symbol ...`, `:"release-docs-gate":` | at least 1 | runs `exit 0` |
    | `? "release-docs-gate"`; the job duplicated later | 5 | runs `exit 0` (last wins) |
    | NEL, LS, PS or CR in a comment, then `allow_failure: true` | 1 | `allow_failure` set |
    | `:include:`, `!!binary aW5jbHVkZQ==:` | at least 1 | treated as `include` |
    | `:variables:` | 1 | a top-level variable |
    | `":release-docs-gate":`; the job duplicated earlier; a duplicate key before the real one; a BOM; a trailing `...` | 0 | not softened |
    | A `%YAML 1.1` directive | 0 | invalid |

  - **Every edit that softened the gate has at least one pin problem.**
  - **Dry run on the tag `v9.0.0`:**
    - The real file runs exactly `main-develop-drift-gate`, `release`, `release-docs-gate`. On `develop` it runs 7 jobs.
    - A job with `variables: {CI_COMMIT_BRANCH: y}` and `if: $CI_COMMIT_BRANCH` runs on the tag; a control without the variable does not.
    - A `pages` job, a job named `pages` and a plain job without rules run on the tag.
    - The lint does not show their artifacts, so delivery to the gates was **not observed**. The fix does not depend on it.
    - The reviewer's three cross-checks hold: `extends` with its own rules and a hidden `when: always` does not run; `if` with `when: always` and `exists` does not run; a hidden `only: [tags]` with `rules` is invalid.
  - **Mutations on a throwaway copy,** each run with a time limit and a memory cap:
    - 49 in the second round: 43 caught at first, 5 real gaps closed by new tests, and 1 equivalent (`fullmatch(str(image))` cannot change a result, as the reviewer also traced).
    - 15 and 8 in the later rounds: all caught.
    - The first round's 24 script mutations are the implementer's report. The orchestrator ran 7 script mutations and about 28 pin mutations of its own.

## Verdict: PASS

The second reviewer's last verdict, on `68a70735`, after CONDITIONAL_PASS on each earlier round. 0 CRITICAL, 0 HIGH, 0 MEDIUM remaining. No breach of an Immutable Security Constraint, and no required control removed or weakened. The six remaining LOW findings are tracked in section 4; the next register takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 7 | 7 | 0 |
| LOW | 10 | 4 | 6 (tracked, section 4) |

SEC-T739-05 and SEC-T739-01, this plan's two targets, were LOW in the T739 review, are resolved, and are not counted above.

**Why each MEDIUM.** Each route needs a CI file edit that survives merge request review, as the LOWs of T739 do. The reviewers graded them above those because the edit is small or looks harmless, and the effect is a gate that does not run. All are older than T741.

## 1. Rulings

- **SEC-T739-05 and SEC-T739-01** are resolved as the T739 review's fixes asked. All seven reads in the gate go through `read_strict`. The error holds the path and offset only. Nothing changes for SEC-T738-02, for a BOM or for `check_line_breaks`. The split into `run_checks` changes no path through the gate, and `return 0` needs every check to have run.
- **`merge_key_lines`, `spelling_problems`.** Correct for what they cover. `yaml.parse` and `yaml.compose` share one scanner and parser. Refusing every explicit tag and plain colon-led scalar is not too broad, because the real file has neither.
- **`predefined_variable_problems`.** `GITLAB_` and `RUNNER_` are not worth refusing, because `NOT_TAG_CONDITIONS` reads only `CI_` names. `rules:variables`, `services:variables`, `secrets` and dotenv are not routes (the first from the reviewer's memory of rule evaluation).
- **`tag_runnable_job_problems`.** Sound. Skipping hidden jobs is right, because a job extending one needs its own rules. Every name in `FILE_LEVEL_KEYS` is refused or pinned.
- **`eol_problems_of`.** Nothing with effect was lost when the digest tests moved to parsed values.
- **Cost, deliberate.** A new job needs an `if` from `NOT_TAG_CONDITIONS`, and adding one is a visible test edit. Whoever adds a condition must check that it is false on a tag: `$CI_PIPELINE_SOURCE == "schedule"` alone would not be, because a schedule can run on a tag ref (reviewer's memory). An `apk` pin or a Python minor bump needs a test constant edit, with a clear message.
- **A limit, not a finding.** No pin can stop what a job's script does on a branch. Contract 6 says so.

## 2. Resolved findings

| Id | Grade | Finding | Fix | Found at |
|---|---|---|---|---|
| SEC-T741-01 | MEDIUM | A `<<` overriding an allowed key passes the pin, because PyYAML and GitLab's parser disagree | Merge keys refused in the whole file, from the node tree | `201f2954` |
| SEC-T741-02 | MEDIUM | `release` could skip the gate: the `needs` pins were text checks a comment satisfied | Parsed allowlists on `release` and `main-develop-drift-gate` | `201f2954` |
| SEC-T741-03 | MEDIUM | File-level routes: `include`, top-level `variables`, `workflow`, `default`, an earlier job's artifacts | Top-level keys refused or pinned; replaced in part by the rule of SEC-T741-15 | `201f2954` |
| SEC-T741-04 | MEDIUM | The `image` value was unguarded, and the digest regex missed comment and mapping forms | The parsed value is pinned on the tag jobs; the digest tests walk parsed values | `201f2954` |
| SEC-T741-05 | LOW | Three overclaiming sentences | Reworded | `201f2954` |
| SEC-T741-09 | MEDIUM | Key spellings PyYAML keeps apart and GitLab folds: `:x`, `!!null`, `!!binary` | Explicit tags, plain colon-led scalars and non-string keys refused | `ec2ea70b` |
| SEC-T741-10 | MEDIUM | A job setting its own `CI_COMMIT_BRANCH` makes a branch condition true on a tag | `CI_` variables refused on any job, hidden ones included, and in `parallel:matrix` | `ec2ea70b` |
| SEC-T741-11 | LOW | A job without artifacts could run on a tag | Closed for the same pipeline by the rule of SEC-T741-15; across pipelines it is SEC-T741-17 | `ec2ea70b` |
| SEC-T741-13 | LOW | Contract 6 and the walker's wording | Reworded | `ec2ea70b` |
| SEC-T741-14 | LOW | The test's memory cap could fail under a lower hard limit | `min(hard, 2 GiB)`, with the hard limit unchanged | `ec2ea70b` |
| SEC-T741-15 | MEDIUM | A `pages` job makes artifacts without an `artifacts` key | Inverted: outside the three pinned jobs, no job may be able to run in a tag pipeline, whatever it does | `036b4e47` |

## 3. OWASP coverage

| Category | Findings (open) |
|---|---|
| A04 Insecure Design | SEC-T741-16 |
| A05 Security Misconfiguration | SEC-T741-12 |
| A08 Data Integrity | SEC-T741-06, -07, -08, -17 |
| A01, A02, A03, A06, A07, A09, A10 | 0. A06: no dependency changed, no audit ran |

## 4. Findings tracked as LOW debt (owner devops-engineer, proposed)

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T741-06 | `scripts/check-version-consistency.py:148, 177`; `scripts/dry-run-publish-release.py:255`; `.gitlab-ci.yml:67` | `errors="ignore"` is still used by the child process this gate runs, so `v8.0.0\xffabc` can hide a stale claim. The other two decide nothing here. | Read strictly and exit non-zero, after checking that no scanned file is invalid. |
| SEC-T741-07 | `check_migration_pointers`, `scripts/verify-release-docs.py` | A document on an `install.sh` line without "Cursor" is checked for existence only, so its bytes are not decoded. No result depends on them. | A clause in `--help`. |
| SEC-T741-08 | `test_the_script_has_one_way_to_read_a_file` | A narrow text match misses `open(path, errors="replace")`, `errors='ignore'` and `.decode("utf-8", "ignore")`. | Also refuse `open(` and count `.decode(`, or walk the AST. |
| SEC-T741-12 | `PINNED_JOBS`, `DEFAULT_KEYS` | `release.script` and `release.artifacts` have text checks or none, and a comment can satisfy them. The values of `default.tags` and `default.interruptible` are unpinned, and `tags` chooses the gates' runner. | Add them as exact values. |
| SEC-T741-16 | `NOT_TAG_CONDITIONS`; contract 6 | A person running a pipeline on a tag with `CI_COMMIT_BRANCH=x` should make a branch condition true, with no file edit **(unverified)**. Harm also needs a harmful job merged first. | A clause in contract 6, and the project's minimum role for pipeline variables above Developer, a project setting. |
| SEC-T741-17 | The gates' checkout | A branch job may leave state in a reused build directory or on the host, and `unit-tests` binds the Docker socket. A later gate on that runner might read it **(unverified, runner-dependent)**. | `GIT_STRATEGY: clone` and a dedicated runner tag on the gates, and pin both. |

## 5. Not verified

- **By the reviewers:** no code was run, so their results are hand traces plus fetched GitLab and Psych source on master. The deployed GitLab version is unknown. Psych's scalar handling for block forms, `deep_symbolize_keys`, `extends` array merging and rule evaluation are from memory, though the orchestrator's lint runs agree where it ran them.
- **The second reviewer's reading:** `t741-round2.diff` for the first two commits' tests, not all of `t741-all.diff`; `read_strict` rests on the first review, because round 2 changed only its wording.
- **Delivery of artifacts from a `pages` job to the gates:** not observed.
- **`parallel:matrix` on a tag:** not run live. The pin refuses it anyway.
- **Project settings:** protected tags, the configured CI file path, the flags on `WIKI_TOKEN`, which runner holds the Docker socket.
- **The merge guard's limit:** `unit-tests` runs on merge request and branch pipelines, so a tag cut from a commit that never went through them is not guarded.
