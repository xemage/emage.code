# Security Review T842: Opencode deny-unless-granted built-ins (T841, SEC-T840-01, SEC-T840-02)

- **Date:** 2026-11-14
- **Task:** T842. The user's decision, verbatim: "Fix now, then refresh (Recommended)"
- **Reviewer:** security-engineer (read-only)
- **Based on:**
  - Worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T836`, commits `496ac559` and `a51a14dc` on `62c5b9a0`.
  - `t842-diff.patch` (scratchpad): wiki, `implementation/AGENTS.md`, `PREREQUISITES.md`, schema, `opencode.json`, `sync.mjs`, tests.
  - Regenerated `security-engineer.md`, compared with its T840 copy.
  - My earlier reviews T837 and T840.
  - The Opencode permissions docs (current V2 page, fetched 2026-11-14).
  - The 1.19.2 resolved rule lists in `docs/artifacts/mcp-agent-denials-evidence-v1.md`.
- **Method limits:** I have no shell, so I did not diff all 28 files, run the tests or run Opencode.
  - The developer reports that a script found 0 changes in earlier entries, the counts bash 13 / edit 8 / webfetch 6 / websearch 6, and that the mutations fail as intended. Those are their claims.
  - The orchestrator reports its own check of scrum-master, security-engineer and product-owner, and that the 15 agents without `bash: deny` are exactly those whose source line holds `execute`.
  - Not observed in a live Opencode run **(unverified live)**.

## Answers

1. **Is SEC-T840-01 fixed?** It is **reduced, not closed**.
   - **What is closed:** the direct path. On Opencode, every generated agent without `execute` now gets `bash: deny`, every agent without `edit` gets `edit: deny`, and every agent without `web` gets `webfetch: deny` and `websearch: deny`.
   - **Placement:** these denies are written only as denies, after every allow, and after the user's global rules. Last match wins, so nothing later in the agent and nothing in the global config re-allows them. A hostile global `*: allow` or `bash: allow` loses, as the rule-model test checks.
   - **Holders are unchanged:** an agent that holds the generic name gets no entry, so Opencode's default and the user's own global `ask` still apply to it. The fix writes no new allow.
   - **What stays open:** an indirect path through `task`, recorded as SEC-T842-01 (MEDIUM). That is why SEC-T840-01 is reduced and not fixed.
2. **Is SEC-T840-02 fixed?** Yes. The wiki now gives the observed 1.19.2 value (`*.env` and `*.env.*` **ask**, `*.env.example` allowed) next to the 1.18.35 documented value (**deny**), and marks the documented value as not observed.
3. **Was any entry lost or changed?** None found.
   - In `security-engineer.md`, entries 1 to 20 of the map are identical to the T840 copy. `bash: deny` and `edit: deny` are appended as the last two entries. It holds `web`, so it gets no web deny, which is correct.
   - `builtinDenials()` refuses any key that is also granted, so a name is never both allowed and denied.
   - `validateDenyUnlessGranted()` refuses non-object maps, empty key lists and non-plain names. `validatePermissionKeys()` refuses `bash`, `webfetch` and `websearch` as allows. The mutation cases cover each of these (not re-run by me).
   - Non-Opencode platforms are untouched: the map exists only in `opencode.json`, and the validators require `tools: "permission"`.
4. **Does `edit` cover `write` and `apply_patch`?** For practical purposes, yes.
   - The current permissions docs say the `edit` resource is the "Target path for `edit`, `write`, and `patch`".
   - The docs page I read does not mention `apply_patch`. The developer reads the 1.18.35 tools docs as covering it. I did not verify that on 1.19.2 **(unverified)**.
   - `edit: deny` also blocks writes outside the project. The edit rule matches before any `external_directory` decision, by docs reading **(unverified live)**.
5. **Residual risks.**
   - **Agents with `execute`** (15 of 28, tech-lead included) still have a shell, and through it the `gitlab` token. This is by design and inside SEC-T660-01.
   - **`task`:** see SEC-T842-01.
   - **`external_directory` and `read`:** see SEC-T842-02.
   - **Built-in agents and the user's own agent files** get no per-agent deny. This is documented, and it is the user's decision of 2026-10-16.
   - **Other built-in tools** (`glob`, `grep`, `list`, `lsp`, `skill`, `todowrite`) neither execute nor write. I record no finding for them.
6. **SEC-T660-01 scope on Opencode after T841.**
   - **Direct shell:** only the 15 generated agents whose source holds `execute`, plus the built-in agents and the user's own agents. This is the same set as on Claude Code, plus the built-ins.
   - **Indirect shell:** any generated agent that can call `task` can still reach a shell through a subagent that has one (SEC-T842-01). Until that is closed, the honest scope statement is "every generated Opencode agent that can call `task`", not only the 15.
   - **Acceptance:** the ADR-011 acceptance of SEC-T660-01 for v11.0.0 should state this Opencode scope.

## Findings

| ID | Severity | Category | Location | Description | Remediation | Owner / status |
|----|----------|----------|----------|-------------|-------------|----------------|
| SEC-T840-01 | SECURITY:MEDIUM → reduced | A01 / A04 | `sync.mjs` `builtinDenials`; `opencode.json` `permissionDenyUnlessGranted` | Generated Opencode agents had `bash`, `edit` and web access by default. | The direct path is closed by T841. The rest moves to SEC-T842-01. | **Reduced** (direct path fixed). Close it together with SEC-T842-01. |
| SEC-T840-02 | SECURITY:LOW | A05 | `docs/wiki/mcp-servers.md` | The wiki did not say which default read rules apply. | It now gives the observed and the documented value. | **Fixed** |
| SEC-T842-01 | **SECURITY:MEDIUM** | A01 / A04 | all `.opencode/agents/*.md` (no `task` entry); `opencode.json` `permissionDenyUnlessGranted` | Opencode allows `task` (`subagent` in V2) by default. The V2 permissions docs say "A custom subagent uses its own permissions, not a subset of its parent's permissions"; I assume the same for 1.x **(unverified)**. An agent with `bash: deny`, such as security-engineer, scrum-master or product-owner, can therefore launch a generated agent that keeps a shell (for example backend-developer) or the built-in `build` or `general` agent, and run commands through it, including reading the `gitlab` token. The precondition is the same as for SEC-T840-01: a prompt injection, or a model that decides to delegate. One delegation step is enough. | (a) Add the generic `agent` to the map: `"agent": ["task"]`, deny-only, so every agent whose source line has no `agent` gets `task: deny`. Check first which source lines hold `agent`; the orchestrators should, because they must delegate. On V2 the key is `subagent` (see SEC-T837-02). (b) Alternatively, or in addition, deny launching any agent that has a shell: emit `task` rules by target name in the map form (`task: { "*": deny, "<allowed-target>": allow }`) **(1.x syntax unverified)**. (c) Add tests and mutations as for T841. (d) Observe `opencode debug agent` on 1.19.2, and observe a refused `task` call **(unverified)**. | devops-engineer (fix); **user** (fix before the root refresh, or accept under ADR-011); deadline proposed: before v11.0.0 is tagged |
| SEC-T842-02 | SECURITY:LOW | A01 | Opencode `read` and `external_directory` defaults; `PREREQUISITES.md` § GitLab token | An agent with `bash: deny` can still use the `read` tool. The default token file lives outside the project (`$XDG_RUNTIME_DIR` or `/dev/shm`), so `external_directory` decides. On 1.19.2 the observed default for that is **ask** (evidence rule 2), so the user would be prompted. The V2 docs say "The default policy allows `external_directory`", so on 2.x the token file would be readable without a prompt. 2.x is not supported (SEC-T837-02). | Document in PREREQUISITES that on Opencode the `external_directory` prompt is the only guard between the `read` tool and the token file, and that the user should answer "no" to it. Optionally emit a deny-only `read` rule for the token file's directory pattern for agents without `execute` **(pattern syntax unverified; must not re-allow `.env`, so deny entries only)**. Re-check this when 2.x support is decided. | devops-engineer; tracked LOW |

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 2 (SEC-T840-01, SEC-T842-01) | 0 (SEC-T840-01 reduced) | 2 (SEC-T840-01 closes with SEC-T842-01) |
| LOW | 2 (SEC-T840-02, SEC-T842-02) | 1 | 1 |

### Justification
T841 is a strict improvement. It adds only deny entries, in the position where they win. It loses no earlier entry, and it is guarded by validators and by tests that the developer reports were mutation-checked. SEC-T840-02 is fixed.

SEC-T840-01 is only partly closed, because `task` lets an agent without a shell delegate to an agent with one (SEC-T842-01, MEDIUM). Under the security-gate rules a remaining MEDIUM needs an owner and a remediation plan before merge, so the verdict is CONDITIONAL_PASS and not PASS.

No CRITICAL or HIGH finding remains. No Immutable Security Constraint is breached. On the reading I gave in T840, no required control is weakened: `security-guidelines.md` assigns enforcement of permission boundaries to the Orchestrator.

**For the user, plainly:** SEC-T842-01 is MEDIUM. With T841 merged as it is, a generated Opencode agent that has no shell of its own can still get one by launching another agent through `task`.

### Conditions
- SEC-T842-01: owner=@devops-engineer (fix) and the user (decision). Remediation: deny-only `task` for agents that do not hold `agent`, with tests, plus a live check. Deadline: before v11.0.0 is tagged, or a user acceptance under ADR-011.
- SEC-T842-02: owner=@devops-engineer. Remediation: a PREREQUISITES note, and optionally a deny-only read pattern. Deadline: next register (tracked LOW).

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 3 (SEC-T840-01 reduced, SEC-T842-01, SEC-T842-02) |
| A02: Cryptographic Failures | Yes (n/a) | 0 |
| A03: Injection | Yes (manifest values validated `^[a-z_]+$`) | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T842-01, shared) |
| A05: Security Misconfiguration | Yes | 1 (SEC-T840-02, fixed) |
| A06: Vulnerable Components | Yes (version range: SEC-T837-02, unchanged) | 0 |
| A07: Auth Failures | Yes (token reach, SEC-T660-01 scope) | 0 new |
| A08: Data Integrity Failures | Yes (drift goes to root refresh T838) | 0 |
| A09: Logging & Monitoring | Yes (n/a) | 0 |
| A10: SSRF | Yes (`webfetch`/`websearch` denied for non-`web` agents) | 0 |

Sources: [Opencode permissions docs](https://opencode.ai/docs/permissions/)
