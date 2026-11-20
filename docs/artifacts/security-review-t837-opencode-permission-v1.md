# Security Review T837: Opencode agent `permission:` map (T836, SEC-T663-02)

- **Date:** 2026-11-14
- **Task:** T837 (plan-168, LOW batch J). The user's word: "J go"
- **Reviewer:** security-engineer (read-only)
- **Based on:** worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T836` (commits `956c9d1c`, `00538942` on `a8cfc6e4`); non-generated diff `t837-diff.patch` (scratchpad); regenerated `implementation/.opencode/agents/*.md` compared with develop `2ad398a2`; `docs/artifacts/security-review-t663-agent-denials-v1.md` (SEC-T663-02); `docs/artifacts/mcp-agent-denials-evidence-v1.md` (1.19.2 resolved rule lists); Opencode docs: opencode.ai/docs/agents (current, V2) and opencode.ai/v2/migrate-v1.md, both fetched 2026-11-14.
- **Method limits:** I had no shell. `grep_content` refused the worktree and the scratchpad. So I compared files by reading them: `backend-developer` (holds no server), `devops-engineer` (named GitLab holder) and `qa-engineer` (named GitLab and Playwright holder), each line by line against develop. I read the generator, schema, manifest and test hunks of the diff. The developer reports a script that found 0 differences in all 28 files beyond the true→allow / false→deny mapping, and that the mutation tests pass. Both are their claims, and I did not re-run either. No Opencode run was made **(unverified live)**.

## Answers

1. **Lost, widened or reordered denials, or added allows.** None found. In the three files I compared, the names are identical, the order is identical, and each `true` became `allow` and each `false` became `deny`, one for one. The only change in the generator (`sync.mjs`) is that `permissionLines()` emits the same three blocks in the same order as before: `denyFirst` (deny), then the allows, then `denyTools` (deny). The `tools: []` fallback for agents that have only denials is unchanged. `keepKeys` still drops any `permission` key from a source agent, so a source file cannot inject an allow. The tests now fail if a `tools:` line comes back, if a key is duplicated, if a name is both allowed and denied, if the order of a holder class is wrong, or if a `permission:` block appears on a non-Opencode platform. For the other 25 files I rely on the developer's script and on these tests (not re-run by me).

2. **V1 `permission` map compared with the V2 list.** The V1 map is the right choice for the version the project has observed (1.19.2), and it is better founded than `tools:`. The 1.x permission docs (as the developer reports them) describe wildcard keys and "last matching rule wins, catch-all first", which means key order counts. The T663 review recorded that the docs stated no key order for the deprecated `tools` map. The T663 evidence from 1.19.2 shows that the `tools` map was already resolved into `allow`/`deny` rules in file order (for example the Demo/QA lists, rules 23 to 82). That makes the `permission` map the form the resolver produces, but no `debug agent` run has been made on the new form **(unverified)**.
   - **Risk on 2.x:** The current docs say that V1 agent frontmatter "is deprecated but still translated automatically". They do not say how a frontmatter `permission` map is translated, whether `server_*` MCP wildcard keys survive, or whether key order is kept **(unverified)**. If the translation drops or reorders entries, the per-agent denials fail open. Only the global six Playwright denials would then remain, and only if the JSON translation keeps them.
   - **Why not V2 now:** Writing the V2 list would silently lose every denial on 1.x, because 1.x does not know `permissions:` and a file with a V2 key has its V1 `permission` ignored. Mixing the two forms is therefore not possible.
   - Recorded as SEC-T837-02.

3. **Dropping `tools:`.** This is safe for any release that reads the agent `permission` map with tool-name and MCP wildcard keys. A third-party changelog summary and the V1 docs say `tools` was folded into `permission` in v1.1.1 **(unverified against the vendor changelog)**. A release before that, or any 0.x release, would probably ignore unknown `permission` keys and lose every per-agent denial **(unverified)**. No supported minimum version is stated. This is part of SEC-T837-02.

4. **`search` / `execute` / `web` naming.** This needs a finding, but not because of a widening.
   - `search`, `execute` and `web` are not Opencode permission keys (those are `grep`/`glob`, `bash` (`shell` on V2) and `webfetch`/`websearch`), so they neither grant nor deny anything.
   - `read` is a real key. `read: allow` comes after Opencode's default `read: ask` on `*.env` and `*.env.*` (T663 evidence: rule 25 after rules 9 and 10). Because the last match wins, all 28 generated agents can read `.env` files without a prompt.
   - This existed before T836 in the `tools` form, and T836 keeps it exactly. Recorded as SEC-T837-03.

5. **SEC-T663-02.** It closes as fixed, as far as possible without a live run. The tracked debt was "migrate to a frontmatter `permission:` block", and that is done. The wiki now says the stored evidence was taken with the `tools:` form and that a run on the new form is unverified. The live-check part is still open (the release-checklist item `opencode debug agent "Tech Lead"` and the refused-call check under K-20), and SEC-T837-01 carries it.

## Findings

| ID | Severity | Category | Location | Description | Remediation | Owner / status |
|----|----------|----------|----------|-------------|-------------|----------------|
| SEC-T837-01 | SECURITY:LOW | A05 | `docs/wiki/mcp-servers.md` Status line; `docs/artifacts/mcp-agent-denials-evidence-v1.md` | The stored 1.19.2 rule lists were taken with the `tools:` form. Nobody has observed `opencode debug agent` resolving the `permission:` form to the same ordered rule list **(unverified)**. | Re-run `opencode debug agent` for Tech Lead, QA Engineer, Demo Agent and Orchestrator on opencode-ai 1.19.2 against the T836 output. Diff the result with the stored lists (expected: identical) and store it as an evidence v2. Keep the refused-call check under K-20. | devops-engineer; open, tracked LOW (release-checklist item) |
| SEC-T837-02 | SECURITY:LOW | A05 / A06 | `implementation/PREREQUISITES.md`, `implementation/platforms/opencode.json` | No supported Opencode version range is declared. On a release before about 1.1.1 **(unverified)** the `permission` map with MCP keys may be ignored. On 2.x the translation of the V1 frontmatter `permission` map (whether `server_*` wildcards survive, key order, the `bash`→`shell` rename) is undocumented. In both cases the per-agent denials could fail open. | State the tested range in PREREQUISITES (floor: the first 1.x release with wildcard `permission` keys; tested: 1.19.2; 2.x: unsupported or unverified). Before claiming 2.x support, add a V2 generator variant (an ordered `permissions:` list) and observe its rule list live. | devops-engineer; open, tracked LOW |
| SEC-T837-03 | SECURITY:LOW (pre-existing; T836 does not change it) | A01 / A05 | generator mapping of the generic tool names; all 28 `.opencode/agents/*.md` (`read: allow`) | `search`, `execute` and `web` are not Opencode permission keys and have no effect. `read` is a real key, and `read: allow` placed after Opencode's default `read: ask` for `*.env` and `*.env.*` re-allows reading `.env` without a prompt (T663 evidence, rule 25 against rules 9 and 10). Graded LOW because Opencode allows `bash` by default, so the default prompt was only a speed bump. I treat the "Envsitter" rule in `security-guidelines.md` as a rule on agent behaviour, not a config control that it requires; the orchestrator may rule otherwise. | Do not emit `read` in the Opencode `permission` map, so the vendor default with the `.env` prompt applies. Alternatively emit `read: { "*": allow, "*.env": ask, "*.env.*": ask, "*.env.example": allow }`. Map or drop the inert names, and correct any doc text that says `execute` grants a shell. | devops-engineer; open, tracked LOW |
| SEC-T663-02 | SECURITY:LOW | A05 | — | The legacy `tools:` map has been migrated to `permission:`. | — | **Fixed** by T836. The live-check part moves to SEC-T837-01. |

## Compliance Checklist
- [x] OWASP Top 10 reviewed (relevant: A01, A05, A06)
- [x] Authorization enforced: the denial set is unchanged
- [x] Secrets management: no secrets in the diff, none read
- [ ] Live confirmation (SEC-T837-01)

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 (SEC-T663-02, SEC-T837-01..03) | 1 (SEC-T663-02) | 3 |

### Justification
No denial is lost, widened or reordered, and no allow is added: I compared three files by reading them, and the developer's script and the tests cover all 28. No Immutable Security Constraint is breached, and no required control is weakened by the change. The three remaining findings are LOW and are tracked as technical debt. SEC-T837-03 existed before T836 and keeps the same meaning.

### Conditions
None. The LOW findings are recorded as tracked debt for the next register: SEC-T837-01 for the release checklist, SEC-T837-02 and SEC-T837-03 for devops-engineer.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes | 1 (SEC-T837-03) |
| A02: Cryptographic Failures | Yes (n/a) | 0 |
| A03: Injection | Yes (generator emits fixed strings; keepKeys filters source keys) | 0 |
| A04: Insecure Design | Yes | 0 |
| A05: Security Misconfiguration | Yes | 3 (SEC-T837-01..03) |
| A06: Vulnerable Components | Yes (version range) | 1 (SEC-T837-02, shared) |
| A07: Auth Failures | Yes (n/a) | 0 |
| A08: Data Integrity Failures | Yes (drift: 28 agent files + `AGENTS.md` for root refresh T838) | 0 |
| A09: Logging & Monitoring | Yes (n/a) | 0 |
| A10: SSRF | Yes (n/a) | 0 |

Sources: [Opencode agents docs](https://opencode.ai/docs/agents/), [Opencode V2 migrate-v1](https://opencode.ai/v2/migrate-v1.md), [V1 permissions docs](https://opencode.ai/en/docs/permissions), [learnopencode changelog v1.1.1 (third-party)](https://learnopencode.com/en/changelog/v1.1.1.html)
