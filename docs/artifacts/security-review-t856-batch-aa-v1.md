# Artifact: security-review-t856-batch-aa-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T856 (plan-175 § Task Decomposition item 2). **Owner**: security-engineer. **Date**: 2026-11-19. **Mode**: read-only. I made no edits and ran no shell.
- **Gate**: security.
- **Based on**:
  - `plan-175-batch-aa-opencode-and-td-t849-01.md`
  - `task-T856.md`
  - `mcp-agent-denials-evidence-v3.md`
  - the generated `implementation/.opencode/agents/orchestrator.md` and `demo-agent.md` on branch `agent/devops-engineer/T855` (commits `22a294ff`, `fccdaeeb` and `a0fc4880`, on top of `be4ecbe0`)
  - the vendor `tool/grep.ts` at Opencode 1.19.2 (a copy in the main checkout, read for the grep/glob residual)
  - the orchestrator's own checks, as reported in the T856 brief
- **The user's decision, verbatim**: "AA + TD-T849-01 go". **LOW policy, verbatim**: "Track LOW items as debt, stop chasing (Recommended)".

## 1. Scope

I reviewed four items:
- **SEC-T837-02**: the supported Opencode version range.
- **SEC-T844-01**: a `task` pattern map for the two orchestrators.
- **SEC-T842-02**: a deny-only `read` map for the 13 agents without `execute`.
- **TD-T849-01**: the temp-name pid assertion.

I also looked for any widening, restated the Opencode scope of SEC-T660-01, graded T855's residuals, and ruled on the privacy question.

## 2. Assessment

**Not verified by me:**
- `sync.mjs` validators: I could not search the worktree (`grep_content` failed outside the main checkout), so I did not read them. Which inputs the generator refuses is taken from T855's report and the 14 killed mutations **(unverified)**.
- The TD-T849-01 test line **(unverified)**.
- The `PREREQUISITES.md` row and `mcp-servers.md` **(unverified)**.
- Whether `PREREQUISITES.md` or `mcp-servers.md` say that the `read` denies are not a boundary **(unverified)**.
- The raw JSON files: I did not open them **(unverified)**.

### 2.1 `task` map (SEC-T844-01)

`orchestrator.md` lines 38-53 contain:
- `task: {"*": deny}`, then 14 named allows;
- every name is the frontmatter `name` of an entry in its `agents:` list (line 54);
- no built-in name and no wildcard allow.

In evidence v3 § 3, `task` for `general`, `build`, `plan`, `explore`, `Orchestrator`, `PoC Orchestrator`, `Demo Agent` and the slug `tech-lead` ends on `task * deny`. `Tech Lead` ends on its named allow. The PoC Orchestrator reads the same way for its own 14 agents. The `debug agent tech-lead` slug probe exits 1, which supports matching by frontmatter `name`.

Not observed: a subagent being launched or refused (K-20).

**Not widened.** Before T855, the orchestrators' `task` was a whole-key allow, so the map narrows it.

### 2.2 `read` map (SEC-T842-02)

`demo-agent.md` lines 36-40 contain the four deny patterns and no `read` allow. The orchestrator also checked that all 13 holders carry them, that no shell holder does, and that no agent has a `read` allow.

Because `*` becomes `.*` with flag `s`, `*/gitlab-mcp/*` matches both the relative form (`../../../../dev/shm/gitlab-mcp/token`) and the absolute form.

`.env` handling:
- **Project B (no hostile rule):** `.env` and `config/.env` end on `read ask *.env`, `.env.local` ends on `ask *.env.*`, and `.env.example` ends on `allow`. The agent's denies match none of these paths, so they cannot make a `.env` path stop resolving to ask.
- **Project A:** the user's own global `"*": allow` decides `.env` both before and after T855, so T855 changes nothing there.

The `tools` field still shows `read: true`, so the tool is not hidden.

**Not widened.**

A side effect, informational only: any directory named `gitlab-mcp` inside a project, such as `src/gitlab-mcp/x`, is also denied for these 13 agents. This fails closed. `tests/_baselines/gitlab-mcp-tool-names.json` is a file, not a directory, and stays allowed (evidence § 3).

### 2.3 The grep/glob residual (traced)

In vendor `grep.ts`, `ctx.ask({permission: "grep", patterns: [params.pattern]})` uses the regex as the pattern, not the path. The path is checked only by `assertExternalDirectoryEffect(ctx, requested, …)`. Ripgrep then returns the matching lines, so `grep` with pattern `.` and path `/dev/shm/gitlab-mcp` would return the token's contents.

- **Default config:** `external_directory` is `ask` outside the worktree, so the user sees a prompt that names the directory.
- **A config that allows `external_directory`** (for example a global `"*": allow`, as in Project A): the `read` deny can be bypassed with `grep`.
- **`glob`:** lists names only, not contents.

So the `read` denies are defense in depth, not a boundary. The documentation must not present them as one; that is SEC-T856-02.

I did not read `external-directory.ts`. So T855's claim that an `external_directory` deny map would change the tool-output allow is **(unverified)**. Evidence § 1 shows the built-in `external_directory` allow as the **last** rule, after the agent's rules. That suggests a deny-only `external_directory` map scoped to `*/gitlab-mcp*` might be possible without touching the tool-output allow. This is a lead for the debt item, not a requirement **(unverified)**.

### 2.4 Version range (SEC-T837-02)

- **Floor 1.0.224:** read from the vendor source and confirmed by ctx7 docs, but not run.
- **Tested:** 1.19.2.
- **2.x:** not supported.

This is enough to close the finding, provided the not-run status of the floor is stated where the range is published.

### 2.5 TD-T849-01

`assertNotIn(str(os.getpid()), re.split(r"[.-]", name))` still catches a pid that forms a whole field. It no longer fails on a pid embedded inside a field (the forced `a<pid>b` case). This matches the debt item's intent.

## 3. Per-finding status

| ID | Before | Status at T856 | Remainder |
|---|---|---|---|
| SEC-T837-02 | LOW | **Fixed** | The floor 1.0.224 is source-read, not run. That must stay stated next to the range. If it is not stated in `PREREQUISITES.md` today, adding the words is a doc condition, not a new finding. |
| SEC-T844-01 | open | **Fixed** (rule lists) | Not observed in a launch (K-20). Built-in agents and the user's own agents still get no per-agent rule (K-23, already tracked). |
| SEC-T842-02 | open | **Fixed** for the `read` tool at the default token paths | Residuals tracked as SEC-T856-02 (grep/glob) and SEC-T856-03 (non-default path, symlink). |
| TD-T849-01 | LOW debt | **Fixed** | None. |

## 4. SEC-T660-01: restated Opencode scope (register v22 § 6.2 item 49, for the review due 2027-01-28)

On Opencode, these can still read the GitLab token:
- (a) every generated agent that holds `execute`, through its shell;
- (b) Opencode's built-in agents (`build` has a shell) and agent files of the user's own (K-23);
- (c) the two orchestrators, indirectly: they can launch only their 14 named subagents each, but those include shell holders such as Backend Developer and DevOps Engineer;
- (d) the 13 generated agents without `execute`:
  - their `read` is denied for any `gitlab-mcp` directory;
  - `grep` and `glob` on the token directory are guarded only by `external_directory` (default `ask`; `allow` under a broad user rule);
  - a token at a non-default path, or a symlink to it inside the project, is not covered.

No fix is possible in the harness for (a) and (b). The finding stays a user-accepted MEDIUM under ADR-011. The scope is narrower than before, not closed.

## 5. Findings

| ID | Severity | OWASP | Location | Description | Remediation |
|---|---|---|---|---|---|
| SEC-T856-01 | SECURITY:LOW | A05 (information exposure) | `docs/artifacts/mcp-agent-denials-evidence-v2/` and `-v3/` raw JSON, `external_directory` patterns | Scratch paths that include the local username sit in a public repository. The username is already public as the repository owner and git user, so the extra exposure is small (machine layout, uid 1000). Exact content is from the brief **(unverified)**. | Do not rewrite the immutable v2/v3 files; their hashes are recorded. In future evidence runs, use a neutral scratch root or redact the path to `<path>` before storing, and record the redaction. Track as debt. |
| SEC-T856-02 | SECURITY:LOW | A01 | Opencode `grep`/`glob` for the 13 agents without `execute` | The `read` deny can be bypassed with `grep`, which returns content, wherever `external_directory` resolves to allow. Without a broad user rule it resolves to `ask` (traced in vendor `grep.ts`). | Make the docs say the `read` denies are defense in depth, not a boundary. Optionally test a deny-only `external_directory` map for `*/gitlab-mcp*` against the tool-output allow (§ 2.3). Track as debt. |
| SEC-T856-03 | SECURITY:LOW | A01 | The `read` deny patterns | A token at a non-default path, or a symlink to it inside the project (read under the link's own path), is not denied. | Document that only the default directory name is covered and that a token must not be linked into a project. Track as debt. |

**Residual (iv)**, no `external_directory` rules added: this is part of SEC-T856-02, not a separate item.

None of the residuals needs more than LOW. Each sits on top of the accepted SEC-T660-01 MEDIUM, and in the default config each is gated by an `ask` prompt or needs a non-default setup.

**Widening check:** none found.
- No `task` allow beyond the named agents, and none for `general`, `build`, `plan` or `explore`.
- No `read` allow.
- No `.env` path stops resolving to the default ask (Project B).
- Claude Code, Cline and GitHub outputs are sha256-identical (T855 and the orchestrator).

## 6. OWASP coverage

| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | Yes | 2 (SEC-T856-02, -03) |
| A02 Cryptographic Failures | N/A (no crypto change) | 0 |
| A03 Injection | Yes (the generator refuses `*`, `~` and `$` patterns, per T855, unverified) | 0 |
| A04 Insecure Design | Yes | 0 |
| A05 Security Misconfiguration | Yes | 1 (SEC-T856-01) |
| A06 Vulnerable Components | Yes (version range) | 0 |
| A07 Auth Failures | N/A | 0 |
| A08 Data Integrity | Yes (evidence hashes) | 0 |
| A09 Logging & Monitoring | N/A | 0 |
| A10 SSRF | N/A | 0 |

## 7. Verdict

## VERDICT: PASS

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 new + 2 prior (SEC-T837-02, TD-T849-01) | 2 | 3 (tracked as debt) |

**Justification:**
- No CRITICAL, HIGH or MEDIUM finding.
- No Immutable Security Constraint is breached.
- No required control is removed or weakened; both new keys narrow access.
- The three new LOWs go to register v23 as tracked debt under the user's LOW policy.

**Conditions:** none blocking.

**Notes for the orchestrator:**
- Wherever the 1.0.224 floor is published, it must be marked source-read, not run.
- Root refresh T857 needs the user's approval.

## Gate Verdict
**Gate:** security. **Verdict:** PASS.
