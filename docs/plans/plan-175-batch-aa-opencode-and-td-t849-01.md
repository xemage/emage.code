# plan-175 — Batch AA (Opencode permission, second round) and TD-T849-01

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v22.md` (§ 5 batches AA and I; § 6.2 item 49);
- `docs/artifacts/security-review-t837-opencode-permission-v1.md` (SEC-T837-02);
- `docs/artifacts/security-review-t842-opencode-deny-v1.md` (SEC-T842-02);
- `docs/artifacts/security-review-t844-opencode-task-v1.md` (SEC-T844-01);
- `docs/artifacts/mcp-agent-denials-evidence-v2.md` (the live method);
- `docs/plans/plan-173-brave-2-1-5-pin-bump.md` (§ Outcome, TD-T849-01).

**Scopes:** `T855`, `T856`, `T857`.

## User decision (2026-11-19, verbatim)

> AA + TD-T849-01 go

## Why now

SEC-T660-01 and SEC-T665-01 (the GitLab token) are the only accepted MEDIUMs left. Their review is due 2027-01-28. AA's three ids lie on the Opencode paths to that token (register v22 § 6.2 item 49).

## Task Decomposition

1. **T855** (devops-engineer), one branch, with separate commits:
   - **(a) SEC-T837-02.** Declare the supported Opencode range in `implementation/PREREQUISITES.md`:
     - the floor, which is the first 1.x release with wildcard `permission` keys, established from the vendor changelog or source; otherwise say **(unverified)**;
     - the tested version, 1.19.2;
     - 2.x unsupported.

     Also state it next to the Opencode permission notes in `docs/wiki/mcp-servers.md`. No V2 generator variant is written.
   - **(b) SEC-T844-01.** For agents that hold `agent` (today `orchestrator` and `poc-orchestrator`), emit a map-valued `task` rule: `"*": deny`, followed by `allow` for each generated agent name the agent may launch. **Never `task: allow` as a whole.**
     - First establish the 1.x syntax and how agent names are matched, from the docs (ctx7) or the source.
     - Then observe it with the evidence v2 live method on opencode-ai 1.19.2.
     - If the syntax cannot be established, or the live resolution does not show the intended rules, do not ship it. Document the gap next to K-23 instead, and report.
   - **(c) SEC-T842-02.** For agents without `execute`, emit deny-only `read` rules for the default token directory, `${XDG_RUNTIME_DIR:-/dev/shm}/gitlab-mcp/`, for example a pattern covering any `gitlab-mcp` directory.
     - Deny entries only. Never an `allow`, and never re-allow `.env`.
     - Establish the 1.x pattern syntax first, and observe the result live as in (b).
     - If it cannot be made to work, keep the PREREQUISITES note and report.
   - **(d) TD-T849-01.** In `tests/functional/test_merge_task_docs.py`, `test_temp_file_has_the_old_mode_before_content_and_a_random_name` must compare the pid against whole name fields, as `test_merge_mcp_json_robustness.py` does (`re.split(r"[.-]", …)`).
   - **For (b) and (c):**
     - tests and mutations;
     - regenerate the mirrors and the registry;
     - declare the root drift;
     - `docs/artifacts/mcp-agent-denials-evidence-v3.md`, with the raw output for the changed agents.
2. **T856** (security-engineer, read-only): review T855.
   - Can SEC-T837-02, SEC-T842-02, SEC-T844-01 and TD-T849-01 each be closed?
   - Is anything widened? A `task` or `read` allow beyond the named agents would be a widening.
   - Restate item 49's scope if it changes.
3. **T857** (orchestrator): the root refresh. It **needs the user's approval at that moment.**

## Constraints

- No `docker`.
- No model or API key in the live run; `opencode debug agent` only, as for evidence v2.
- Never read secrets, the user's settings files or the user's real Opencode configuration.
- Never open `tests/golden/held-out/`.
- No change to the agents' MCP grants or to any other platform's output.

## Outcome

**Done on 2026-11-19.**

**T855** (devops-engineer):
- **(d) TD-T849-01, `22a294ff`.** The pid is checked against whole name fields, as in the sibling test. A forced `a<pid>b` name fails the old assertion and passes the new one. **Fixed.**
- **(a) SEC-T837-02, `fccdaeeb`.** The supported range is stated in PREREQUISITES and the wiki:
  - the floor is 1.0.224, read in the vendor source and not run;
  - tested on 1.19.2;
  - 2.x is not supported.

  **Fixed.**
- **(b) SEC-T844-01, `a0fc4880`.** Each orchestrator gets `task: {"*": deny, "<Name>": allow, …}`, with the names taken from its source `agents:` list (14 each). The generator refuses built-in names, wildcards and any wider allow. **Fixed** in the rule lists; a launch was not observed (K-20).
- **(c) SEC-T842-02, `a0fc4880`.** The 13 agents without `execute` get deny-only `read` patterns for any `gitlab-mcp` directory, which cover the relative form used by 1.19.2 and the absolute form used by 1.0.224. No `read` allow is written, so `.env` paths keep Opencode's default `ask`. **Fixed** for the `read` tool.
- **Evidence:** `docs/artifacts/mcp-agent-denials-evidence-v3.md`, from `opencode debug agent` on 1.19.2.
- **Tests:** 14 of 14 mutations killed. The Claude Code, Cline and GitHub outputs are byte-identical.

**T856** (security-engineer): `docs/artifacts/security-review-t856-batch-aa-v1.md`, **PASS**. Nothing is widened.
- **New, LOW, tracked:**
  - **SEC-T856-01:** scratch paths containing the local username are in the raw files of evidence v2 and v3. Future evidence runs redact them.
  - **SEC-T856-02:** `grep` and `glob` on the token directory are guarded only by `external_directory`, so the `read` denies are defense in depth, not a boundary. The orchestrator added that sentence to the wiki.
  - **SEC-T856-03:** a token at a non-default path, or a symlink to it inside the project, is not covered.
- **The SEC-T660-01 Opencode scope is restated** in the review, § 4:
  - The orchestrators can no longer launch the built-in agents. They can still reach the token through the shell-holding subagents on their lists.
  - The scope is narrower, not closed. It stays the user-accepted MEDIUM, with its review on 2027-01-28.

**T857** (orchestrator): the root refresh, with the user's approval at that moment (question dialog, option label verbatim: "Refresh now (Recommended)").
- `install.sh --projections-only` changed exactly the 15 declared `.opencode/agents/*.md` files.
- The drift baseline is emptied, and drift is `[]`.

**The orchestrator's own verification:**
- My own parser compared the resolved lists of the five v3 raw files with the generated maps, with nested maps expanded. All match, and only `external_directory` follows.
- The `task` names equal the orchestrator's `agents:` list.
- All 13 agents with `bash: deny` carry the `read` denies, no shell holder does, and no agent has a `read` allow.
- The gates, the full suite and the pipeline are recorded in the merge request.

**Disclosed:** during T855, two vendor source files (`tool_glob.ts`, `tool_grep.ts`) were written into the main checkout instead of the scratchpad. Both were untracked and never committed. The orchestrator moved them to the scratchpad.

**For register v23:**
- Fixed: SEC-T837-02, SEC-T842-02, SEC-T844-01 and TD-T849-01. Batch AA ends; batch I shrinks by one.
- New, LOW: SEC-T856-01, -02 and -03.
- Item 49 is restated from T856 § 4.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T855 | 110k | 120k |
| T856 | 30k | 50k |
| T857 | under 10k | 20k |
