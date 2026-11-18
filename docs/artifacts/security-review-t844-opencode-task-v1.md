# Security Review T844: Opencode `task` denied unless granted (T843, SEC-T842-01)

- **Date:** 2026-11-14
- **Task:** T844. The user's decision, verbatim: "Fix now, then refresh (Recommended)"
- **Reviewer:** security-engineer (read-only)
- **Based on:**
  - Worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T836`, commits `7a981340` and `77c49d3c` on `db554b3c`.
  - `t844-diff.patch` (scratchpad): wiki, `implementation/AGENTS.md`, `PREREQUISITES.md`, `opencode.json`, tests.
  - Regenerated `scrum-master.md` (tail), compared with its T842-state entries.
  - My earlier reviews T837, T840 and T842.
  - The Opencode permissions docs (V2 page, read in T842).
- **Method limits:** I have no shell, so I did not diff all 28 files, run the tests or run Opencode.
  - The developer reports a 28-file check with 0 differences beyond the trailing deny, `task: deny` in 26 files, and mutations V1 to V5 failing as intended. These are their claims.
  - The orchestrator reports its own check: only `orchestrator.md` and `poc-orchestrator.md` lack `task: deny`.
  - That `task` is the 1.x permission key comes from the developer's reading of the 1.18.35 docs (agents.mdx "Task permissions", permissions.mdx). I did not re-read those pages.
  - Not observed in a live Opencode run **(unverified live)**.

## Answers

1. **Is SEC-T842-01 fixed?** Yes, by reading, for the generated agents.
   - The only code change is the manifest entry `"agent": ["task"]`, which feeds the generic deny path that I reviewed in T842. The validator refuses `task` as an allow, and mutation "task allow" checks that.
   - Every generated agent whose source line has no `agent` gets `task: deny` as its very last entry. In `scrum-master.md` it comes after `bash: deny` and `edit: deny`, and the earlier entries are unchanged.
   - Under last-match-wins, nothing in the agent and nothing in the global config (`task: allow`, `*: allow`) re-allows it. The rule-model test covers both hostile cases.
   - A test pins that only `orchestrator` and `poc-orchestrator` hold `agent` in their source.
   - The V2 key `subagent` is not written. 2.x is unsupported, which is already tracked in SEC-T837-02.
2. **Does SEC-T840-01 now close?** Yes, as **fixed** (live check outstanding under SEC-T837-01). For the generated agents without `execute`, both the direct shell path (T841) and the delegation path (T843) are closed. The remaining paths are covered elsewhere:
   - `read` on files outside the project, behind the `external_directory` prompt: SEC-T842-02, LOW.
   - Built-in agents and the user's own agent files: the user's decision of 2026-10-16 (K-23).
   - Neither of these belongs to SEC-T840-01.
3. **Is SEC-T842-02's note adequate?** Yes. It stays **LOW, tracked**.
   - The PREREQUISITES note names the path (`read` on the token file outside the project), names the only guard (the `external_directory` prompt, `ask` in 1.x) and tells the user what to do ("answer 'no'").
   - It states that 2.x allows this by default according to its docs, not observed, and that 2.x is unsupported.
   - It remains open because the guard depends on the user's answer and on the version. Re-check it when 2.x support is decided, or when a deny-only `read` pattern for the token directory is designed.
4. **Was any entry lost or changed?** None found. The diff changes only the manifest, the tests and the docs, with no generator code. In the file I read, the only addition is the trailing `task: deny`. The fixture tests confirm the per-class tails, and the delegating fixture `deleg` gets no `task` entry.
5. **Residual: the orchestrators can delegate.** This is by design, because orchestrators must delegate. It is graded LOW as SEC-T844-01.
   - Both orchestrators hold `execute`, so they already have a shell and can reach the token. Delegating to a generated subagent adds nothing beyond that, and the subagent runs with its own, narrower map.
   - The one real gap: with Opencode's default `task` permission, an orchestrator can also launch the **built-in** agents (`general`, `build`). Those carry no per-agent MCP denials, so they can call the GitLab write tools (for example `gitlab_merge_merge_request`) that the orchestrators' own maps deny. That bypasses the GitLab tool narrowing through a tool call instead of through the shell. The capability is not new (the shell plus the token already reaches it under the accepted SEC-T660-01), but it makes the bypass a single, ordinary tool call.
6. **SEC-T660-01 scope on Opencode after T843.**
   - **Direct shell, and so the token:** the 15 generated agents whose source line holds `execute`, Opencode's built-in agents, and the user's own agent files.
   - **Delegation:** only `orchestrator` and `poc-orchestrator`, which hold a shell themselves.
   - **The other 13 generated agents:** no shell and no delegation. Their only path to the token file is `read` behind the `external_directory` prompt (SEC-T842-02).
   - This matches the Claude Code statement ("every agent with `execute`") plus the built-ins and the user's own agents. The ADR-011 acceptance text for v11.0.0 can quote it.

## Findings

| ID | Severity | Category | Location | Description | Remediation | Owner / status |
|----|----------|----------|----------|-------------|-------------|----------------|
| SEC-T842-01 | SECURITY:MEDIUM | A01 / A04 | `platforms/opencode.json` `permissionDenyUnlessGranted` | An agent with `bash: deny` could launch an agent that has a shell through `task`. | `"agent": ["task"]` gives `task: deny` to 26 agents, refused as an allow, with tests and mutations. | **Fixed** (live **unverified**) |
| SEC-T840-01 | SECURITY:MEDIUM | A01 / A04 | as above | Generated Opencode agents had a shell, edit and web access by default. | Closed by T841 and T843. | **Fixed** (live **unverified**; live check under SEC-T837-01) |
| SEC-T842-02 | SECURITY:LOW | A01 | `PREREQUISITES.md` § GitLab token | `read` can reach the token file, guarded only by the `external_directory` prompt. | The note has been added. | **Open, tracked LOW** (mitigated by documentation) |
| SEC-T844-01 | SECURITY:LOW | A01 | `orchestrator.md`, `poc-orchestrator.md` (no `task` entry) | With the default `task` permission, an orchestrator can launch the built-in `general` and `build` agents. Those have no per-agent MCP denials, so the GitLab tools the orchestrator's own map denies, such as `gitlab_merge_merge_request`, are reachable in one tool call. There is no new capability, because the orchestrators already hold a shell and the token (SEC-T660-01, accepted). The narrowing is still bypassable through an ordinary tool call. | For the two delegators, emit a pattern rule that allows only the generated agents: `task: { "*": deny, "<generated-agent-name>": allow, ... }`. It must contain deny and named allows only, and never `task: allow` as a whole. First verify that the 1.x map-valued `task` syntax and the matching on agent names work **(unverified)**. Add tests and a mutation. Alternatively, document the gap next to K-23. | devops-engineer; tracked LOW |

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 2 (SEC-T840-01, SEC-T842-01) | 2 | 0 |
| LOW | 2 (SEC-T842-02, SEC-T844-01) | 0 | 2 (tracked as technical debt) |

### Justification
T843 closes the delegation bypass of SEC-T842-01. It does so by adding deny entries only, in the position where they win, with no generator code change and no entry lost (by my reading of one file, the developer's 28-file script and the orchestrator's check). Together with T841, this closes SEC-T840-01. No CRITICAL, HIGH or MEDIUM finding remains. No Immutable Security Constraint is breached, and no required control is weakened. The remaining LOW findings (SEC-T842-02, SEC-T844-01, and SEC-T837-01/-02 from T837) are tracked as technical debt. Live confirmation on opencode-ai 1.19.2 is still outstanding under SEC-T837-01.

### Conditions
None for PASS. For the next register:
- SEC-T842-02: tracked LOW.
- SEC-T844-01: tracked LOW, owner devops-engineer.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 4 (2 fixed, SEC-T842-02, SEC-T844-01) |
| A02: Cryptographic Failures | Yes (n/a) | 0 |
| A03: Injection | Yes (manifest values validated) | 0 |
| A04: Insecure Design | Yes | 0 new |
| A05: Security Misconfiguration | Yes | 0 new |
| A06: Vulnerable Components | Yes (2.x `subagent` key: SEC-T837-02, unchanged) | 0 new |
| A07: Auth Failures | Yes (SEC-T660-01 scope restated) | 0 new |
| A08: Data Integrity Failures | Yes (drift goes to root refresh T838) | 0 |
| A09: Logging & Monitoring | Yes (n/a) | 0 |
| A10: SSRF | Yes (n/a) | 0 |
