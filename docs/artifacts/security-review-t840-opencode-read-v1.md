# Security Review T840: Opencode generic tool names / `read` (T839, SEC-T837-03)

- **Date:** 2026-11-14
- **Task:** T840. The user's words: "SEC-T837-03: fix before root refresh."
- **Reviewer:** security-engineer (read-only)
- **Based on:**
  - Worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T836`, commits `9d2f3e7d` and `b1072317` on `b161d4c4`.
  - `t840-diff.patch` (scratchpad): wiki, `AGENTS.md`, `PREREQUISITES.md`, schema, `opencode.json`, `sync.mjs`, tests.
  - Regenerated files I read: `security-engineer.md`, `scrum-master.md`, and the `tech-lead` tail pinned by the test.
  - My T837 review: the same files before T839 for `devops-engineer`, `backend-developer` and `qa-engineer`.
  - `docs/artifacts/mcp-agent-denials-evidence-v1.md` (the 1.19.2 resolved rule lists).
- **Method limits:** I have no shell and could not read git objects, so I did not diff the 28 files myself. The developer reports a script check: only the removed generic-name lines differ, and every MCP allow and deny is identical and in the same order. That is their claim. I checked it on two files against the T837 copies I had read, and it held. The tests and mutations were not re-run by me. There was no live Opencode run **(unverified live)**.

## Answers

1. **Is SEC-T837-03 fixed?** Yes, by reading.
   - `permissionTools()` keeps every MCP token and keeps only those non-MCP names that are listed in `permissionKeys`. The list is `["edit"]`, so an unlisted name fails closed.
   - `validatePermissionKeys()` refuses `read`. It also refuses non-plain names and any use without `tools: "permission"`.
   - Without `read: allow`, Opencode's default read rules apply again. In the 1.19.2 evidence those are `read ask *.env` and `read ask *.env.*`; the 1.18.35 docs, as the developer reports them, say `deny`. Either value protects `.env` files.
   - A new test fails if `read`, `search`, `execute`, `web`, `agent`, `todo`, `bash` or `webfetch` is written again.
   - Non-Opencode platforms are not touched: the filter runs only for `tools === 'permission'`.

2. **Did any denial or allow change besides the removed lines?** None that I found.
   - In `security-engineer.md` the leading block is still `security-audit_*` deny followed by its four named allows. Then follow `gitlab_*`, `playwright_*`, the six Playwright names and the server wildcards, in the T663 order.
   - In `scrum-master.md`, `gitlab_*: deny` still comes first, followed by its named allows.
   - `edit: allow` remains wherever it was before. The `tech-lead` tail pinned by the test is `permission:`, `edit: allow`, then the same denials.
   - The test changes are correct for the new edge case of an agent with no allow at all (`default=` in `min`/`max`, and `lead` reset to 0). They do not loosen the order checks for agents that do have allows.
   - The emitter guard `block.length > 1` only drops an empty `permission:` header, and every agent has denials anyway.

3. **Is the default shell on Opencode a finding?** Yes. I grade it **MEDIUM**, so it goes to the user. It is SEC-T840-01 below. It existed before T839 and was not introduced by it; T839 is the change that documents it.

## Findings

| ID | Severity | Category | Location | Description | Remediation | Owner / status |
|----|----------|----------|----------|-------------|-------------|----------------|
| SEC-T837-03 | SECURITY:LOW | A01 / A05 | `sync.mjs`, `platforms/opencode.json` | `read: allow` re-allowed reading `.env` files | `read` and the inert names are no longer written; a validator and a test guard against their return | **Fixed** by T839 (verified by reading; live **unverified**) |
| SEC-T840-01 | **SECURITY:MEDIUM** (existed before T839) | A01 / A04 | Opencode agent generation (`sync.mjs` `permissionTools`, `opencode.json` `permissionKeys`); all 28 `.opencode/agents/*.md` | On Opencode the generated agent files restrict only MCP tools. Opencode's default rule `* allow *` (rule 0 in the 1.19.2 evidence) gives every generated agent `bash`, `edit`/`write` and web access. That includes the read-only roles of `security-guidelines.md` § Agent Permission Classification (security-engineer, product-owner, and tech-lead during review) and scrum-master, whose source line has no `execute`. The read-only and no-shell boundaries are therefore not enforced on Opencode. A prompt injection in reviewed content could run commands or edit code. Through a shell, every agent can read the `gitlab` token. This widens the exposure of SEC-T660-01 from "six of seven GitLab roles" to all 28 agents on Opencode. | (a) Generate **denies only, never allows**, so a user's own global `ask` keeps working: write `bash: deny` for every agent whose source line has no `execute`, `edit: deny` for every agent without `edit`, and `webfetch: deny` and `websearch: deny` for every agent without `web`, in the trailing deny block. Holders stay on Opencode's default. (b) Add tests and mutations for each class. (c) Have the user rule whether the SEC-T660-01 acceptance for v11.0.0 (ADR-011) covers the Opencode scope of "every agent has a shell", or needs a new acceptance. (d) Observe the result with `opencode debug agent` on 1.19.2 **(unverified)**. | devops-engineer (fix); **user** (decide: fix before the root refresh or the release, or accept under ADR-011); deadline proposed: before v11.0.0 is tagged |
| SEC-T840-02 | SECURITY:LOW | A05 | `docs/wiki/mcp-servers.md` (T839 bullet) | The bullet says "the default read rules apply" but not which ones. The 1.18.35 docs say `deny` for `*.env`, while the observed 1.19.2 rule list says `ask`. | State the observed 1.19.2 value (`ask`, with `*.env.example` allowed) and the documented value side by side, and mark the docs value as not observed. | technical-writer or devops-engineer; tracked LOW |

**Note on grading SEC-T840-01.** `security-guidelines.md` assigns enforcement of permission boundaries to the Orchestrator ("Permission boundaries are enforced by the Orchestrator before task assignment"). It does not require a platform config control. I therefore do not treat this as a required control that the change omits or weakens, and the FAIL rule does not fire. If the orchestrator or the user reads § Agent Permission Classification or Immutable Constraint 5 as requiring a technical control, this becomes a blocking item.

Evidence for the shell claim: the 1.19.2 rule lists show `* allow *` at index 0 and no `bash` rule in any generated agent. This comes from the rule list; a shell call has not been observed **(unverified live)**.

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 (SEC-T840-01) | 0 | 1 |
| LOW | 2 (SEC-T837-03, SEC-T840-02) | 1 | 1 |

### Justification
T839 fixes SEC-T837-03 and keeps every MCP allow and deny in place and in order (checked on two files by reading, and claimed by the developer's script for all 28). It makes no new grant: it only removes lines, and the one remaining non-MCP key, `edit`, was held before. A MEDIUM finding remains, SEC-T840-01. It existed before T839 and lives in the same generator mapping. Under the security-gate rules a MEDIUM needs an owner and a remediation plan before merge, so this cannot be a PASS.

### Conditions
- SEC-T840-01: owner=@devops-engineer (fix) and the user (decision). Remediation: deny-only `bash`/`edit`/`webfetch`/`websearch` entries for agents that do not hold the matching source tool, with tests. Deadline: before v11.0.0 is tagged, or a user acceptance under ADR-011 that also settles the SEC-T660-01 scope.
- SEC-T840-02: owner=@technical-writer. Remediation: correct the wording. Deadline: next register (tracked LOW).

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 2 (SEC-T837-03 fixed, SEC-T840-01) |
| A02: Cryptographic Failures | Yes (n/a) | 0 |
| A03: Injection | Yes (fixed strings; `permissionKeys` validated `^[a-z_]+$`) | 0 |
| A04: Insecure Design | Yes | 1 (SEC-T840-01, shared) |
| A05: Security Misconfiguration | Yes | 1 (SEC-T840-02) |
| A06: Vulnerable Components | Yes (n/a) | 0 |
| A07: Auth Failures | Yes (token exposure, see SEC-T840-01) | 0 |
| A08: Data Integrity Failures | Yes (drift goes to root refresh T838) | 0 |
| A09: Logging & Monitoring | Yes (n/a) | 0 |
| A10: SSRF | Yes (n/a) | 0 |
