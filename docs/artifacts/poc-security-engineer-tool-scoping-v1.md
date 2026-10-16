# Artifact: poc-security-engineer-tool-scoping-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T602 (P2, decision only), plan-113
- **Created**: 2026-10-08
- **Commit read**: worktree `agent-solution-architect-T602` on `develop` `63e3d5e`. All line numbers are on this commit.
- **Based on**:
  - `docs/tasks/task-T602.md` and `docs/plans/plan-113-poc-security-engineer-tool-scoping.md`;
  - `docs/artifacts/poc-security-reviewer-blocking-v3.md` §12 X5 (`:555`: "**X5 (L4, parked):** replace
    `poc-security-engineer`'s `execute` tool with a fixed-command scanner.");
  - `docs/artifacts/security-engineer-audit-server-design-v1.md` (the four-tool fixed-argv design);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and `docs/decisions/ADR-007-command-contract-authority.md`
    (Accepted);
  - the user's instruction of 2026-10-08, "Continue with the next best step", and the standing ADR-008 review decision Q1,
    "Self-placement only".
- **Decision references**: ADR-008 P4 (maturity never ranks), D5 (ruling record). No new ADR is minted. No P34b ranking is used.

## 0. What this document is, and what it did not do

It is a decision record plus one user question. **It changed no agent, tool grant, runtime code, test, projection, registry
entry or golden case.** Every edit below is a **held option**, applied only after the user decides, and a Security Engineer
reviews every amendment. The only other file touched is the `**Status:**` line of the brief.

**Method and limits.** I had no shell, no Grep and no Glob. Every cited line was re-read by `Read` on this commit. Anything I
could not read is marked **(unverified)** and collected in §10. I opened nothing under `tests/golden/`.

## 1. Verdict in brief

1. **`execute` should go from `poc-security-engineer`, but not before its replacement exists.** The four existing
   `mcp__security-audit__*` tools alone cannot carry the agent's own text. They cannot supply commit and push status. They also
   print matched lines, which breaks the "redacted output" rule at `poc-security-engineer.md:24` and `poc-orchestrator.md:70`.
2. **Recommended: Option 1.** Add a separate fixed-argv server with two tools (a redacting secret scanner and a ref-containment
   lookup), then swap the grant. The agent's blocking classes and secret-reporting duty stay verbatim.
3. **Removing `execute` is a security gain with a real basis.** `security-guidelines.md:102` classes the Security Engineer as
   "read-only during audit phase", and the unrestricted `execute` grant (`Bash`) cannot enforce that.

## 2. Execution-dependent statements (answers T602 (b))

"Execution-dependent" means the statement can only be carried out with a command. All quotes were re-read on `63e3d5e`.

### 2.1 `implementation/knowledge/agents/poc-security-engineer.md`

| ID | Line | Verbatim | Needs | Breaks if `execute` goes with no replacement? |
|---|---|---|---|---|
| R1 | `:4` | `tools: [read, search, execute, web]` | The grant itself | It is the grant being changed |
| R2 | `:22` | "…it stays open until its fix is re-checked and confirmed" | A re-scan, including history (see `poc-orchestrator.md:75`) | **Yes**, for the history part |
| R3 | `:24` | "**Exposed secret:** report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it." | `git log` / ref containment for "commits" and "whether they were pushed" | **Yes** |
| R4 | `:24` | "Never reproduce the value, including in a search pattern or any other tool argument; scan by pattern, with redacted output." | A scanner whose output omits matched text | **Yes** (see §2.3, finding F1) |
| R5 | `:24` | "…and the secret is removed from git history with the user's explicit approval, or declined under the conditions in `poc-orchestrator` § Security Findings, which also covers a secret not yet committed." | A history scan to confirm removal | **Yes** |
| R6 | `:24` | "Never revoke or rotate credentials, rewrite history or force-push yourself" | Nothing. It is a prohibition | No. Removing `execute` enforces it structurally (today it is prose only) |
| N1 | `:11` | "Perform a pragmatic PoC security scan." | A scanner, loosely | No (`grep_content` or a new scan tool suffices) |
| N2 | `:15`–`:17` | "- Surface secrets exposure risks" / "- Identify major auth or injection concerns" / "…This is a presence check, not a full OWASP-style audit" | Reading and content search | No, **but** in Claude Code `search` maps to `Read` only (`implementation/platforms/claude-code.json:18`: `"search": "Read"`). The agent then has no Grep or Glob, so `grep_content` (or a new tool) is its only content search and its only way to find files |

Not execution-dependent: `:20` (grading), `:21` (severity floor), `:22` (blocking classes and report-as-blocker), `:23`, `:25`
(verdict), `:51`–`:52` (Rails). Option 1 and Option 2 keep all of these byte-identical.

**Hit counts, `poc-security-engineer.md`:** the token `execute` appears on 1 line (`:4`), 1 occurrence. Execution-dependent
statements: 6 on 3 lines (`:4`, `:22`, `:24`: R1–R6) plus 2 non-breaking mentions on 2 line-ranges (N1, N2).

### 2.2 `implementation/knowledge/agents/poc-orchestrator.md` § Security Findings and its dependants

The orchestrator keeps its own `execute` (`:4`). These statements break only where the work is the **reviewer's**.

| ID | Line | Verbatim | Needs | Breaks for a reviewer without `execute`? |
|---|---|---|---|---|
| O1 | `:51` | "…before every push that carries a delegated agent's commits not yet checked, and before every merge… check the change for committed secrets, hardcoded credentials, tracked secret-bearing files (identified by name, never opened) and real PII." | A commit range, and `git ls-files` for "tracked" | **Yes** ("tracked" and "the change" are git facts) |
| O2 | `:66` | "Delegate the fix, then have `@poc-security-engineer` re-check it." and "That task stays in `active-tasks.md` until `@poc-security-engineer` confirms the finding resolved." | The re-scan in O4/O5 | **Yes**, same as R2 |
| O3 | `:70` | "Scan with pattern-based secret detection, never by its literal value, with the scanner's output redacted so that no value is printed. Identify committed secret files such as `.env` or `*.key` by name; do not open them (`security-guidelines.md` § Agent Safety Guards)." | A redacting scanner; `git ls-files` for "committed… by name" | **Yes** (F1 and F2) |
| O4 | `:74` | "List, by location only, every copy the project controls that may hold the secret (branches, tags, agent worktrees, CI job logs, artifacts and caches, images or packages built from the affected commits, merge-request diffs)" | `git branch`, `git tag`, `git worktree list`, GitLab | No: this is the orchestrator's own work, and it holds `execute` and `mcp__gitlab` |
| O5 | `:75` | "…a pattern-based secret scan of all branches and tags, never by the literal value, finds no occurrence (in their history, or only at their tips if step 3 was declined under the conditions below)" | A history scan over every ref | **Yes** |
| O6 | `:77` | "For this case, the step 4 scan also covers the working tree, index and stashes of every worktree that held the value." | `git grep --cached`, stash enumeration | **Yes** |

**Hit counts, `poc-orchestrator.md`:** the tool token `execute` appears once as a grant (`:4`), and that grant is untouched.
Execution-dependent statements: 6 on 6 lines (`:51`, `:66`, `:70`, `:74`, `:75`, `:77`). Five of them break for a reviewer
without a replacement (O1, O2, O3, O5, O6).

### 2.3 Findings that change the options

- **F1. The four existing tools cannot give "redacted output".** `grep_content` runs `rg --json …` (design v1 §2.4; argv shape
  asserted at `tests/functional/test_audit_server.py:160`–`:172`). A live test asserts that the returned `stdout` contains the
  matched text: `self.assertIn("hello", inner.get("stdout") or "")` (`test_audit_server.py:485`). A secret match would therefore
  put the value into the agent's context. `poc-orchestrator.md:70` says the scanner's output must be redacted "so that no value
  is printed". The agent could avoid repeating the value, but the tool would still print it. Reading that sentence as "the agent
  does not repeat it" would weaken it, and the constraints forbid weakening.
- **F2. The existing scanner probably skips the files that matter.** The pinned argv has no `--hidden` and no `--no-ignore`
  (`test_audit_server.py:164`–`:172`). ripgrep skips dotfiles and `.gitignore`d paths by default (general ripgrep behaviour;
  **unverified** against the implemented `commands.py`, which I did not read). A committed `.env` is exactly what `:70` asks to
  find "by name".
- **F3. "Pushed" is only knowable up to the last fetch.** No tool here touches the network. Any local tool reports containment in
  the remote-tracking refs as of the last fetch. The orchestrator's `mcp__gitlab` can confirm against the remote. This limit
  exists today and is not made worse.
- **F4. The registered `git` MCP server is not a base to build on.** `servers.yaml:121`–`:125` registers
  `@modelcontextprotocol/mcp-git`, and a test comment at `test_audit_server.py:314`–`:315` calls this one of "the disclosed
  filesystem/git package-name defects". Its tool surface is also unread by me **(unverified)**, and may include mutating tools.

## 3. D5 records

### 3.1 (a) Should `execute` go, and what replaces it

- **Subject (D3):** the tool grant of `poc-security-engineer` (a configuration value, not a document clause).
- **Clauses:**
  - `poc-security-engineer.md:4`: `tools: [read, search, execute, web]`.
  - `security-guidelines.md:102`: "**Security Engineer** — read-only during audit phase (can only flag issues, annotate, and
    create findings)".
  - `security-guidelines.md:17`–`:20` (Rails): it "does not grant any agent authority to disable a security control
    "temporarily," even in PoC or development mode".
  - `security-guidelines.md:159` (Constraint 5): "No privilege escalation paths — No agent or service may grant itself elevated
    permissions."
  - `security-engineer.md:4` (production): `tools: [read, search, mcp__security-audit__run_npm_audit, mcp__security-audit__run_pip_audit, mcp__security-audit__run_dotnet_list_vulnerable, mcp__security-audit__grep_content, web, mcp__fetch]`.
- **Step A (joint satisfiability):** No clause says an agent MUST hold `execute`, and none says it MUST NOT. `:102` classes a
  role's behaviour. An agent holding `Bash` can also behave read-only. So one action satisfies both, and **there is no
  contradiction**. This is a design choice on the merits, not a ruling that any clause is defective.
- **Step that fired:** **Step A**. No conflict exists, so nothing is ranked. P1 (tier 1) does not fire because it needs
  Step A to fail (P1 test (c)). P3b and P5 are not reached.
- **Declared scope relied on (P1–P3):** none.
- **Merits (not authority):** `execute` makes the read-only classification unenforceable. It lets the agent rewrite history,
  force-push, or edit code, all of which `poc-security-engineer.md:24` forbids only in prose. Dropping it turns that prose
  prohibition into a structural one.
- **The three candidates, evaluated:**

| Candidate | Carries R3 (commits, pushed) | R4/O3 (redaction) | R2/O5/O6 (history, index, stashes re-scan) | Verdict |
|---|---|---|---|---|
| (i) the four existing tools only | No | **No** (F1) | No | Cannot meet the reviewer's own text. **Not offered** |
| (ii) the four plus `search`/`read`, commits and pushes delegated to an agent with git | Partly: the orchestrator supplies it | **No** (F1) | Only if the orchestrator runs the scan and the reviewer "confirms" evidence it did not produce | The redaction gap remains, and the confirmation is no longer independent. Closing the gap needs a new scanner, which is candidate (iii). **Not offered as a standalone option** |
| (iii) the existing tools plus new fixed-argv tool(s) | Yes, with the stated F3 limit | Yes, by design | Yes | **Offered** as Options 1 and 2 |

- **Amendment:** held for the user (§6, Options 1 and 2). Falls on `poc-security-engineer.md` (frontmatter and `:24`) and, for
  Option 2, on `poc-orchestrator.md:70`.
- **Maturity:** not relied on (ADR-008 P4).

### 3.2 (b) Execution-dependent statements

- **Subject:** statements in the two agents that assume command execution (§2).
- **Clauses:** §2.1 and §2.2, each quoted with file and line.
- **Step A:** the pairs are statement against grant. Under Option 3 (no change) every statement stays satisfiable. Under a
  grant without `execute` and without new tools, R2–R5 and O1–O3, O5, O6 become unsatisfiable (§2). Under Options 1 and 2 they
  stay satisfiable with the text unchanged, apart from the small edits in §6.
- **Step that fired:** not a cross-document conflict. This is same-file and same-section coherence between a grant and the
  duties that rely on it, which ADR-008 § Scope excludes ("A document that contradicts itself… resolved by same-file
  coherence"). Nothing is ranked.
- **Amendment:** the fix is to supply the capability (Options 1 and 2), not to rewrite the duties. The only rewrites proposed are
  limited to making the new tool dependency and the F3 limit explicit (E1-b, E1-c, E2-b, E2-c). None removes a duty.
- **Maturity:** not relied on.

### 3.3 (c) Contract tests and projections

- **Subject:** whether a tool-grant change interacts with any test or projection.
- **Clauses:** the four test files in §4, quoted by line.
- **Step A:** an edit to the `tools:` line is jointly satisfiable with every test **only if the platform mirrors are regenerated
  in the same MR**. Otherwise `test_opencode_agents_use_tools_object` and `test_claude_code_agents_use_tools_string` fail.
  Adding a fifth tool to the existing `security-audit` server is **not** jointly satisfiable with
  `test_audit_server.py:257`–`:264` and `:391`–`:404`.
- **Step that fired:** Step A. No ranking.
- **Amendment:** a **separate** server for the new tools (Options 1 and 2) leaves `test_audit_server.py` untouched. Held for the
  user.
- **Maturity:** not relied on.

### 3.4 (d) Maturity

- **Subject:** what a tool-grant change does to `poc-security-engineer`'s `stable` evidence.
- **Clauses:**
  - `poc-security-engineer.md:6`: `maturity: stable`.
  - `implementation/scripts/check-maturity.py:644`–`:649`, `AGENT_STABLE_CRITERIA`: criterion 4 "beta->stable evidence
    (golden/tag/ledger)", 5 "cross-referenced by a command or another agent", 6 "documented in docs/wiki/**", 7 "no open P0
    or P1 defect". The beta criteria (`:567`–`:571`) add schema validity, `## Rails`, and no open P0 defect.
- **Step A analysis:** no criterion reads the `tools:` value.
  - Criterion 4 is met by the tag `# maturity-evidence: agent/poc-security-engineer` at
    `tests/functional/test_agent_escalation_consistency.py:12` (`_has_evidence_tag`, `check-maturity.py:259`–`:264`). Editing
    `tools:` does not touch it.
  - Schema validity: `mcp__<server>__<tool>` tokens are already in a `stable` agent's `tools:` (`security-engineer.md:4`, `:6`).
    I did not read `agent.schema.json` **(unverified)**.
  - Criterion 7 is the only live risk. An open P0 or P1 task whose `**Affects:**` names `agent/poc-security-engineer` fails
    it (`_ledger_defect`, `check-maturity.py:501`–`:517`). T602 is P2 with `**Affects:** —`. If the implementation task is P2
    and declares `—` or another component, `stable` holds. If the orchestrator makes it P1 and declares this agent, the agent
    drops out of `stable`, as `poc-security-reviewer-blocking-v3.md:416`–`:457` records for FU-1 and FU-2. Which to declare is
    the orchestrator's call, and an enhancement is not obviously "a defect indicted".
- **Step that fired:** none. This is a factual check.
- **Amendment:** none. Held for the user only as a task-priority choice in §6.
- **Maturity was not relied on** as a reason for any ruling (ADR-008 P4). It is reported only to say whether `check-maturity`
  stays green.

## 4. Test and projection coupling (answers T602 (c))

No open golden case cites `poc-security-engineer`. The orchestrator checked this with held-out pruned; I did not repeat it
(I have no search tool and may not open held-out) **(unverified by me)**. I name no golden case.

### 4.1 `tests/functional/test_platform_projections.py`

Scope: `_TARGET_PLATFORMS = ("github", "gemini", "opencode", "claude-code")` (`:26`). All tests run over **every** agent. None
names `poc-security-engineer`.

| Lines | Test | What it asserts about tools |
|---|---|---|
| `:207`–`:227` | `test_opencode_agents_use_tools_object` | The projected `tools` is a non-empty dict (`:217`–`:218`); `set(projected_tools) == set(source_tools)` (`:219`–`:223`, "tools keys must match source tools list"); every value is `True` (`:224`–`:227`) |
| `:236`–`:273` | `test_claude_code_agents_use_tools_string` | The projected `tools` is a string equal to the source list translated through `toolMap` and de-duplicated, in order (`:254`–`:267`). A token not in `toolMap` passes through literally (`:256`: `if t in tool_map else [t]`). The abstract names `read`, `search`, `edit`, `execute`, `todo` must not appear untranslated (`:268`–`:273`) |
| `:200`–`:205` | `test_gemini_agents_drop_tools_field` | Gemini projections have no `tools` key |
| `:184`–`:198` | `test_projection_preserves_non_frontmatter_content` | Body text equals source on all platforms (`:193`); frontmatter keys equal source except `tools` and `user-invocable` (`:195`–`:198`) |
| `:168`–`:182` | `test_projection_frontmatter_keys_match_manifest_contract` | No unexpected frontmatter keys |

**Consequence:** any source edit passes only if `implementation/.<platform>/agents/poc-security-engineer.*` is regenerated in the
same MR (`node implementation/scripts/sync.mjs --root implementation`). The `mcp__…` tokens translate without a `toolMap` entry.
Removing `execute` also removes `Bash` from the Claude Code string.

### 4.2 `tests/functional/test_agent_escalation_consistency.py`

No assertion about tools. `poc-security-engineer` is in `POC_TRACK_AGENTS` (`:73`) and carries the evidence tag (`:12`). Asserted:
- it is in `poc-orchestrator.md`'s `agents:` roster (`:93`–`:100`);
- its text contains `"The PoC orchestrator will handle escalation"` (`:102`–`:110`, string at `:107`);
- `poc-orchestrator`'s `## PoC Workflow` section (regex `## PoC Workflow\n(.*?)\n## `, `:139` and `:158`) mentions at least 10
  `@`-agents, all registered, all in the roster (`:137`–`:169`).

**Consequence:** a tool edit does not affect it. Any wording edit must keep that escalation sentence. An orchestrator edit
inside `## PoC Workflow` (for example `:51`) must not add an `@`-mention of a non-agent. Edits in `## Security Findings` fall
outside the regex window.

### 4.3 `tests/performance/test_tool_use_complexity.py`

No assertion about any agent's tool list. It reads only `tests/fixtures/benchmarks/tool_use_cases.json` and
`tests/_baselines/benchmark-thresholds-v1.json` (`:11`–`:12`, `:72`–`:73`). It scores the fixture's own `expected_tools` against
its own `candidate_steps` (`:84`–`:86`) and compares to thresholds (`:122`–`:141`). The fixture's tool names are generic
(`read_file`, `list_dir`, `grep_search`, as seen at `tool_use_cases.json:13`, `:36`, `:66`). **Unaffected by any option.** I read
only the first 80 lines of the fixture **(unverified beyond that)**.

### 4.4 `tests/functional/test_audit_server.py`

Concerns `security-engineer`, **not** the PoC agent (`SOURCE_AGENT = …/security-engineer.md`, `:55`).

| Lines | Asserts |
|---|---|
| `:112`–`:205` | Exact argv for each of the four `build_*_argv()` functions; `grep_content` argv at `:164`–`:172` |
| `:257`–`:264` | `audit_server.py` registers **exactly** the four named tools, no `run_command`, no `execute` |
| `:266`–`:278` | Only `executor.py` calls `subprocess.run`, once; `audit_server.py`, `commands.py`, `validation.py` do not import `subprocess` |
| `:280`–`:289` | That one call sets `shell=False` and `check=False` as literals |
| `:291`–`:296` | No `*.py` in `runtime/security/` sets `shell=True` (glob, so a new module there is covered) |
| `:305`–`:311` | The `security-audit` `servers.yaml` entry is exactly `tags: [extended]`, stdio, `python3`, `-m implementation.runtime.security.audit_server`, no `env` |
| `:313`–`:321` | Sample entries (`filesystem`, `git`, `context-retriever`) are untouched |
| `:328`–`:355` | `security-engineer`'s source tools have no `execute` and the four `mcp__security-audit__*` tools; its Claude projection has no `Bash` |
| `:391`–`:404`, `:406`–`:426` | Live: the server lists exactly the four tools; fabricated `execute`/`run_command`/`shell`/`eval`/`bash` calls are rejected with "Unknown tool" |

**Consequences:**
- **A fifth tool in `audit_server.py` breaks `:257`–`:264` and `:391`–`:404`.** Hence the separate server in Options 1 and 2.
- A new module in `runtime/security/` is covered by `:291`–`:296` and must meet the same rules. The implementation should add AST
  tests for it that mirror `:266`–`:289`.
- **Gap:** no test asserts that `poc-security-engineer` lacks `execute` or `Bash`. The implementation should add one, mirroring
  `ProjectedClaudeCodeAgentGrantTests` (`:324`–`:355`).

## 5. Constraints this decision keeps

1. Nothing weakens any rule in `security-guidelines.md` or any Immutable Security Constraint (`:151`–`:160`). Every option keeps
   `poc-security-engineer.md` `:20`–`:25` and `:51`–`:52` byte-identical, with two clarifying additions (E1-b, E1-c) that only
   narrow what the agent may do or state a limit honestly.
2. The agent keeps every blocking class it has today: Immutable Constraint breaches, omitted/removed/disabled/weakened controls,
   and `SECURITY:CRITICAL`/`SECURITY:HIGH`. The severity floor at `:21` and the verdict at `:25` are untouched.
3. The secret-reporting duty (`file, line, commits, pushed, type, issuer, environment variable`) is kept in full in Option 1. In
   Option 2 one datum (pushed) is obtained from the orchestrator but stays part of the reviewer's report.
4. No option leaves the agent unable to detect or report an exposed secret. Options 1 and 2 add a dedicated redacting scanner.
   Option 3 changes nothing.
5. The never-reproduce-the-value rule (`:24`) is met by the tool's design, not just by the agent's discipline: the new scanner
   takes no caller-supplied pattern and returns no matched text.

## 6. The user question (one round)

**Question.** `poc-security-engineer` holds an unrestricted `execute` tool (`Bash`). The production `security-engineer` holds only
fixed-argv audit tools. How should the PoC reviewer's tools change? Whichever you choose, every blocking class and the
exposed-secret reporting duty stay as they are, and no tool or agent edit is applied until you choose.

**Recommendation: Option 1.**

### Option 1 (Recommended). New two-tool server, then drop `execute`

- **What.** Build a new stdio server, `poc-security-audit` (module `implementation/runtime/security/poc_audit_server.py`), as a
  **separate implementation task**. It has two fixed-argv tools, and the agent's grant swaps to them after they exist and pass
  their tests.
- **Security gain.** The agent can no longer run arbitrary commands, rewrite history, or edit code, so the read-only
  classification (`security-guidelines.md:102`) becomes real. The scanner is redacting by construction (fixes F1) and covers
  dotfiles and tracked-by-name files (fixes F2). No secret can appear in a tool argument, because the caller supplies no pattern.
- **Capability lost.** Free-form commands. "Pushed" is reported as of the last fetch (F3).
- **New implementation work.** One new module with a contract of two tools (see §7), a `servers.yaml` entry, tests (AST
  invariants plus a live adversarial probe, as in `test_audit_server.py`), and a Security Engineer review of the new tool.
- **Test and projection impact.** `test_audit_server.py` unchanged (separate server). Platform mirrors regenerated for the agent.
  `servers.yaml` adds an `extended` stdio entry, which projects into the MCP config of every platform except `github`
  (`AGENTS.md` § MCP Servers table).
- **Root-drift paths.** The agent file in each platform that renders `tools` (verified present in `implementation/` for `.claude`,
  `.github`, `.opencode`, `.pi`; `.gemini` drops `tools`, so a frontmatter-only edit does not change it; `.cursor` has a `.mdc`
  file I did not open; `.cline` path not found) and its root counterparts. Plus the MCP configs: `.mcp.json`,
  `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json`. The exact list is
  whatever `python3 -m tests.functional.test_root_install_parity --print-drift` reports (baseline `drift` is `[]` today,
  `tests/_baselines/root-install-drift.json:18`). I did not read that test **(unverified)**.
- **Registry.** The agent file's checksum in `implementation/registry/index.json` changes
  (`generate-registry.py --check`) **(that the registry holds it is unverified)**.
- **Golden impact.** None expected. The frontmatter line is not on the `blocking-v3` §7 search list. Confirmed by the
  orchestrator only.
- **Maturity.** `stable` holds unless the task is P0/P1 and declares this agent (§3.4).

### Option 2. One new tool, push status from the orchestrator

- **What.** Build only the redacting scanner (`scan_secrets`, including its history scope, which returns commit SHAs). The
  orchestrator, which already holds `mcp__gitlab`, answers "were these commits pushed?" from the remote.
- **Security gain.** Same as Option 1, and the remote answer is better than a local one (F3).
- **Capability lost.** The reviewer cannot answer "pushed" alone. Its report needs the orchestrator, which adds a round trip.
- **New implementation work.** One tool instead of two, plus the two prose edits E2-b and E2-c.
- **Test and projection impact.** As Option 1, plus `poc-orchestrator.md` (stable) is edited: three projections more per platform.
  `test_agent_escalation_consistency.py` is unaffected if the edit stays in `## Security Findings` (§4.2).
- **Root-drift paths.** As Option 1, plus `poc-orchestrator` in each platform.
- **Golden impact.** The `poc-orchestrator` edit is a text site. It is on no known list, but the orchestrator should search
  `tests/golden/` (held-out pruned) for the E2-c Before text first.
- **Maturity.** Same as Option 1; also two stable agents are edited.

### Option 3. Keep `execute`, close X5 as accepted

- **What.** No change. X5 is closed as "accepted risk, `Bash` retained", with the reasons recorded.
- **Security gain.** None.
- **Capability lost.** None.
- **New implementation work.** None.
- **Test, projection, drift, golden impact.** None.
- **Residual risk.** The reviewer's read-only classification (`security-guidelines.md:102`) stays unenforceable. The "never rewrite
  history or force-push" rule at `poc-security-engineer.md:24` stays prose only. Redaction depends on the agent piping its own
  output.

### Not offered, with reasons

- **The four existing tools only,** and **the four plus delegated commit and push lookup.** Both leave F1: matched lines are
  printed, which breaks `poc-security-engineer.md:24` and `poc-orchestrator.md:70` as written. Making them compliant means
  either rewording those sentences to "the agent does not repeat the value" (a weakening, forbidden) or changing the production
  `grep_content` (it would break `test_audit_server.py:160`–`:172` and `:485`). They also cannot do the history, index and stash
  re-scan (O5, O6), and moving that scan to the orchestrator removes the reviewer's independent confirmation.
- **Extending the existing `security-audit` server.** It breaks `test_audit_server.py:257`–`:264` and `:391`–`:404`, and it would
  expose the new tools to the production `security-engineer` unless filtered by grant only.
- **The registered `git` MCP server** (F4).

## 7. Contract of the recommended new tools (no code; implementation is a separate task)

Style follows `security-engineer-audit-server-design-v1.md`. All commands are Python `argv: list[str]` run by a single executor
with `shell=False`. No caller input is ever concatenated into a string. Path inputs are validated against a server-startup
`allowed_root`, as in design v1 §4.3.

**Server.** `poc-security-audit`, tags `[extended]`, transport stdio, no `env`, module
`implementation.runtime.security.poc_audit_server` **(proposed)**. It registers exactly its tools and no generic command tool.

### 7.1 `scan_secrets(root_dir, scope, rev_range?)`

- **Inputs.**
  - `root_dir`: a path inside `allowed_root`, must be a git work tree.
  - `scope`: a closed enum `worktree | index | stashes | history | tracked_names`.
  - `rev_range` (optional, `history` and `worktree` only): either a ref name matching `^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$` or
    `<sha>..<sha>` with each side `^[0-9a-f]{7,40}$`. A leading `-` is rejected.
- **No caller-supplied pattern.** The rules (`rule_id` to regex) are a constant table in the server: private-key headers,
  well-known provider key prefixes, credential assignments, bearer tokens, and similar. The table is reviewed by a Security
  Engineer. This is what lets the agent obey "never… in a search pattern or any other tool argument".
- **Fixed argv, per scope** (rule patterns inserted as `-e <pattern>` elements from the constant table, never from the caller):
  - `worktree`: `git grep --untracked --no-exclude-standard -I -n -E … --`, so untracked and ignored files are covered, which
    answers O6's "not yet committed" case;
  - `index`: `git grep --cached -I -n -E … --`;
  - `stashes`: enumerate with `git rev-list -g refs/stash`, then `git grep -I -n -E … <sha> --` per stash commit;
  - `history`: enumerate refs with `git for-each-ref --format=%(objectname) refs/heads refs/remotes refs/tags` (or the validated
    `rev_range`), then `git grep -I -n -E … <sha> --` per commit tip, plus `git log -G<pattern> --format=%H -- ` for commits that
    introduced a match;
  - `tracked_names`: `git ls-files -z`, filtered **inside the server** by a fixed name allowlist taken from
    `security-guidelines.md:134` (`.env`, `.env.*`, `credentials.json`, `*.pem`, `*.key`, `id_rsa`, `secrets.yaml`). It returns
    names only and never opens a file.
- **Output (redacted by construction).** A list of `{rule_id, path, line, commit?, scope}`, a `truncated` flag and a hit cap. The
  server parses git's output, **discards the matched text**, and returns neither matched lines nor raw stderr. Errors are coded,
  not echoed.
- **Residual and review items.** git-config hardening for an untrusted repository (for example fixing `-c core.fsmonitor=false`
  and a clean config environment) belongs in the Security review. History scans over large repositories need a timeout and a cap.
  Both are implementation details I do not fix here.

### 7.2 `ref_containment(root_dir, commit)` (Option 1 only)

- **Inputs.** `root_dir` as above; `commit` matching `^[0-9a-f]{40}$`.
- **Fixed argv.** `git -C <root> for-each-ref --contains <commit> --format=%(refname) refs/remotes refs/tags refs/heads`.
- **Output.** Lists of ref names split into `remote_refs`, `tags`, `local_branches`; `pushed` is true if `remote_refs` is non-empty;
  `as_of_last_fetch: true` always. It never reads commit content and never contacts the network.
- **Limit (F3).** A commit pushed after the last fetch looks unpushed. The reviewer's report must say so, and the orchestrator
  can confirm through `mcp__gitlab`.

**Implementation is a separate task** and is not dispatched by this document. It needs a Security Engineer review of the tool
and its rule table, a live adversarial test as in `test_audit_server.py:432`–`:461`, and the agent grant swap as the **last**
step so that no merge leaves the reviewer without git capability.

## 8. Held edits (verbatim Before/After)

All are **held**. None is applied. Apply each by its exact `Before:` text, never by line number. Line numbers are on `63e3d5e`.
Each Before was seen once in its file on this commit; confirm uniqueness at dispatch.

### E1-a (Options 1 and 2). `poc-security-engineer.md:4`, the grant

Option 1:

````
Before:
tools: [read, search, execute, web]

After:
tools: [read, search, mcp__security-audit__grep_content, mcp__poc-security-audit__scan_secrets, mcp__poc-security-audit__ref_containment, web]
````

Option 2:

````
Before:
tools: [read, search, execute, web]

After:
tools: [read, search, mcp__security-audit__grep_content, mcp__poc-security-audit__scan_secrets, web]
````

`grep_content` is kept for injection and authorization presence checks, since `search` maps to `Read` only in Claude Code. The
three dependency-audit tools are left out because the PoC scope is "not a full OWASP-style audit" (`:17`). The user may add
them. They are fixed-argv, but `npm audit` and `pip-audit` use the network.

### E1-b (Options 1 and 2). `poc-security-engineer.md:24`, bind the redaction rule to the tool

````
Before:
scan by pattern, with redacted output. Deleting the secret from the code does not resolve the finding.

After:
scan by pattern, with redacted output, using the secret-scan tool whose output omits matched text, never a tool that prints matched lines. Deleting the secret from the code does not resolve the finding.
````

This only narrows what the agent may do.

### E1-c (Option 1). `poc-security-engineer.md:24`, state the push limit

````
Before:
report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it.

After:
report the file, line, commits, whether they were pushed (as far as the fetched remote-tracking refs show; the PoC orchestrator confirms against the remote), the credential's type and issuer, and the environment variable that should replace it.
````

### E2-b (Option 2). `poc-security-engineer.md:24`, push status from the orchestrator

````
Before:
report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it.

After:
report the file, line, commits, the credential's type and issuer, and the environment variable that should replace it, and obtain from the PoC orchestrator, which holds remote access, whether those commits were pushed, and include that in the report.
````

### E2-c (Option 2). `poc-orchestrator.md:70`, the orchestrator's side

````
Before:
Identify committed secret files such as `.env` or `*.key` by name; do not open them (`security-guidelines.md` § Agent Safety Guards).

After:
Identify committed secret files such as `.env` or `*.key` by name; do not open them (`security-guidelines.md` § Agent Safety Guards). When `@poc-security-engineer` asks whether a secret's commits were pushed, answer from the remote (for example `mcp__gitlab`), by commit and branch name only.
````

### Option 3

No edit.

### Task-handling note (all options)

If Option 1 or 2 is chosen, the implementation task should be `P2` with an `**Affects:**` line that does not name
`agent/poc-security-engineer` as defective, or the orchestrator accepts a temporary drop from `stable` (§3.4). Either way
`check-maturity` is judged on its criteria, not on rank (ADR-008 P4).

## 9. Summary table

| Item | Result |
|---|---|
| Execution-dependent statements | 8 in `poc-security-engineer.md` (6 breaking or granting, 2 non-breaking; `:4`, `:11`, `:15`–`:17`, `:22`, `:24` ×4); 6 in `poc-orchestrator.md` (`:51`, `:66`, `:70`, `:74`, `:75`, `:77`), 5 of them break for a reviewer without a replacement |
| Hit counts | `execute` token in `poc-security-engineer.md`: 1 line, 1 occurrence (`:4`). In `poc-orchestrator.md`: 1 occurrence as a grant (`:4`), untouched |
| Tests asserting tool lists | `test_platform_projections.py:207`–`:227`, `:236`–`:273`, `:200`–`:205`; `test_audit_server.py:257`–`:264`, `:328`–`:355`, `:391`–`:404` (all for `security-engineer` or the audit server). `test_agent_escalation_consistency.py` and `test_tool_use_complexity.py` assert none |
| Test that pins the PoC agent lacking `execute` | None exists (gap) |
| Option 1 (Recommended) | Two-tool new server, then drop `execute`. Keeps all duties. Most work; best security |
| Option 2 | One-tool new server; push status via orchestrator. Edits two stable agents |
| Option 3 | No change; X5 closed as accepted |
| Maturity | `stable` holds unless a P0/P1 task declares this agent. No criterion reads `tools:` |
| Golden | No known case cites the agent (orchestrator's check). None named here |

## 10. Unverified claims

1. No open golden case cites `poc-security-engineer`: taken from the orchestrator. I have no search tool and may not open
   held-out.
2. `tests/functional/test_root_install_parity.py` was not read; drift behaviour is taken from the baseline's `_comment` lines
   (`root-install-drift.json:3`–`:4`, `:7`).
3. Platform paths: I confirmed the agent file and its `tools` line in `implementation/.claude`, `.github`, `.gemini`, `.opencode`
   and `.pi`, and the root `.claude/agents/poc-security-engineer.md`. `implementation/.cursor/agents/` has a
   `poc-security-engineer.mdc` (the read tool suggested it; contents not opened). `implementation/.cline/agents/poc-security-engineer.md`
   does not exist; the Cline path is not determined. Other root paths were not read.
4. The implemented `commands.py`, `executor.py` and `audit_server.py` were not read. F1 and F2 rest on the tests' pinned argv and
   assertions (`test_audit_server.py:160`–`:172`, `:485`). That ripgrep skips hidden and ignored files by default is general
   behaviour, not checked against this repo.
5. `agent.schema.json` was not read. `registry/index.json` content was not read.
6. `tests/fixtures/benchmarks/tool_use_cases.json` was read only to line 80.
7. `docs/wiki/**` was not searched for documentation of the tool grant.
8. The registered `git` MCP server's tool list is unread (F4).
9. `git for-each-ref --contains`, `git grep --cached`, and `git rev-list -g` behave as described in §7. I wrote them from
   knowledge of git, not from running them.
10. The performance and git-config hardening of the proposed history scan are not designed here.

## 11. Blockers

None. One minor design limit is carried as F3 (push status is only as fresh as the last fetch). It is not an
`unclear_requirements` blocker, because the orchestrator's `mcp__gitlab` covers it.
