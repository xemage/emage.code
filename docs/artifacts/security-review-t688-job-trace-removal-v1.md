# Artifact: security-review-t688-job-trace-removal-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test or mutation run; the `grep_content` tool errors on the worktree path, files read directly). Recorded by the orchestrator from the reviewer's report. The fix round `40746e4c` was verified by the developer's tests and the orchestrator's suite run, not re-read by the reviewer.
- **Gate**: security. **Date**: 2026-10-23.
- **Target**: T688, branch `agent/devops-engineer/T688` (from develop `44386f56`), commits `c0ce232d` (reviewed) and `40746e4c` (fixes): `mcp__gitlab__get_pipeline_job_output` removed from `qa-engineer` (20 to 19 GitLab tools), a Constraints bullet and a Bug Report template line in `qa-engineer.md`, counts and sentences in `AGENTS.md`, `implementation/AGENTS.md`, `implementation/PREREQUISITES.md` and `docs/wiki/mcp-servers.md`, tests in `test_mcp_package_pins.py` and `test_mcp_grant_pins.py`.
- **Based on**: `docs/tasks/task-T688.md`, `docs/artifacts/tracked-debt-register-v2.md` (SEC-T660-02, decision D-1). The user decided on 2026-10-23 (AskUserQuestion, label verbatim): "Drop the tool from qa-engineer (Recommended)".
- **Orchestrator checks**: the full suite on the final tree is recorded in the task outcome; the developer's mutation log (`scratchpad/mutations-t688.txt`: 14 + 9 mutations, all killed) was judged real by the reviewer for the first 14, not re-run.

## Verdict: CONDITIONAL_PASS (0 critical, 0 high, 1 medium, 4 LOW)

The tool is gone from the source and all five `implementation/.*` projections (the Opencode `gitlab_*: false` first-wildcard denies it; Gemini has no tools line), no other agent holds it, and the remaining 19 qa-engineer tools are least-privilege (two pinned writes, `create_issue` and `create_issue_note`; sixteen reads; no merge, approve, push, trigger, retry, cancel, variable, environment, download or artifact tool). No Immutable Security Constraint breached; a grant is narrowed.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T688-01 | MEDIUM | "no agent reads raw job output" overclaimed: on Gemini CLI the tool list does not restrict MCP tools, six of seven roles hold `execute` and `glab ci trace` stays reachable, the main session and Opencode built-ins are unaffected | fixed in `40746e4c`: "no agent of these seven holds a tool that reads raw job output (T688, SEC-T660-02): a shell can still run `glab ci trace`, and on Gemini CLI the tool list does not restrict MCP tools"; the test anchor updated; CLOSED |
| SEC-T688-02 | LOW | the repo-root projections still grant the tool and lack the body bullet (derived copies, refreshed by the root refresh; the tests inspect only `implementation/.*`) | closed by T679 (the root refresh); SEC-T660-02 is recorded closed for installed copies only after it |
| SEC-T688-03 | LOW | `get_pipeline_test_report` can carry `system_output` and `stack_trace` text (unmasked, attacker-influenced) and the body rule did not say so | fixed: the bullet forbids copying them verbatim; the residual is named in `PREREQUISITES.md` and marked (unverified) for the pinned server's exact payload; the tool stays; CLOSED |
| SEC-T688-04 | LOW | the body bullet was self-contradictory (do not ask for traces / ask for an excerpt) and did not name the shell, `/raw` URL and browser routes; the Bug Report template said "Evidence: logs" | fixed (bullet rewritten, template line "a user-checked log excerpt (never a raw CI trace)", projections regenerated); CLOSED |
| SEC-T688-05 | LOW | `GITLAB_FORBIDDEN_NAME` (`job_output`) did not match `trace`/`log`/artifact-file style names | fixed (`job_(output|trace|log)|job_artifact`, catch-test names added); CLOSED |

## Residuals

qa-engineer holds `execute`, `web` and Playwright, so a trace can still be fetched by `glab ci trace`, `curl` with the token or a job `/raw` URL: the removal narrows the MCP route, the body rule is a prompt-level control (exposed to prompt injection from test output and MR text), and the docs call the whole thing a tool-list narrowing and a policy, not an enforcement. `get_pipeline_job` metadata is assumed to contain no trace body (unverified: the Jobs API page was not fetched; the pinned server may add fields). `get_pipeline_test_report_summary` returns counts only (confirmed against the GitLab documentation).

## Unverified

The root-drift declaration for the four root qa-engineer paths in the reviewed commit (the orchestrator's gates pass with the declared list); job-object contents in the Jobs API and what the pinned server adds; the output content of `wait_for_job`; runtime behaviour on any platform (nothing was observed live).
