# Artifact: poc-security-engineer-tool-scoping-v2.md

> Immutable once produced; revisions bump `<N>`. **Supersedes `poc-security-engineer-tool-scoping-v1.md`**, which stays
> unchanged as the historical record. Where they differ, v2 governs. v2 alone is the implementation input.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T602 follow-up (decision recorded, specification final)
- **Created**: 2026-10-09
- **Based on**:
  - `docs/artifacts/poc-security-engineer-tool-scoping-v1.md` (v1), read on `develop` `63e3d5e`; its quotes and line numbers
    are carried over unchanged and not re-read in this follow-up except where §6 says so;
  - the user's decisions of 2026-10-09, relayed verbatim by the orchestrator (§1);
  - the Security Engineer review of v1, **CONDITIONAL_PASS** (0 critical, 0 high, 8 medium F-1..F-8, 4 low F-9..F-12), relayed
    by the orchestrator, who will record it as `docs/artifacts/security-review-poc-security-engineer-tool-scoping-v1.md`. I did
    not read that record. All twelve findings are adopted; none is rejected;
  - the orchestrator's verification of v1: 19 of 23 quotes verbatim, the other 4 checked by hand; F1 holds
    (`test_audit_server.py:485`); the two golden mentions of the agent are frozen fixtures, so no live coupling.
- **Decision references**: ADR-008 P4 (maturity never ranks) and D5; the two user decisions below. No new ADR is minted.

## 0. What this document does

It records the user's decisions and turns Option 1 into a final specification, with exact held edits. **It changes no agent,
grant, runtime code, test, projection, registry entry or golden case.** The edits in §4 are applied by a separate
implementation task, after a Security Engineer review of the amendments. I have no shell and opened nothing under
`tests/golden/`.

## 1. Decisions

| Question | User's answer (verbatim label) | Effect |
|---|---|---|
| Tool grant | **"New 2-tool server (Recommended)"** | Option 1 of v1 §6 is chosen: a new `poc-security-audit` server with `scan_secrets` and `ref_containment`, then drop `execute` |
| `grep_content` | **"Keep, record residual (Recommended)"** | `grep_content` stays in the grant (E1-a). Its unredacted output is a named, accepted residual (§8, R-1) |

- **Dropped:** Option 2 (one tool, push status from the orchestrator) and Option 3 (keep `execute`). No edit to
  `poc-orchestrator.md` is made. v1's E2-b and E2-c are void.
- **Still not offered:** the four existing tools only (v1 §3.1, F1).
- **Maturity** is not relied on for any decision here (ADR-008 P4).

## 2. Change log against v1

| # | v1 | v2 | Source |
|---|---|---|---|
| 1 | Options 1, 2, 3 open | Option 1 chosen; 2 and 3 dropped; `grep_content` kept with a residual | User decisions |
| 2 | §7 contract, no isolation fields | Git-config isolation is a contract field (`git -C <root> -c core.fsmonitor=false -c core.pager=cat -c core.hooksPath=/dev/null`; `--no-textconv --no-ext-diff` on `git log`; explicit subprocess env) | F-1 |
| 3 | `root_dir` only inside `allowed_root` | `root_dir` must equal `git rev-parse --show-toplevel` | F-2 |
| 4 | Output "discards matched text" | `git grep -z` parsing; the rule table also applies to paths, ref names and tag names; `%H` only; no stderr, no argv, including on timeout | F-3 |
| 5 | `pushed` boolean | `pushed` is `true` or `"unknown"`, never `false`; `last_fetch_time` added | F-4 |
| 6 | E1-c named an orchestrator confirmation no document writes | E1-c reworded: the reviewer reports "unknown (unconfirmed against the remote)" and names no actor | F-5 (resolution in §4.3) |
| 7 | §5 item 5 and "Security gain" claimed the value never reaches the agent | Narrowed: true for `scan_secrets` only; `grep_content` and `read` are a named residual | F-6 |
| 8 | "timeout and a cap" | Aggregate per-call deadline, ref and stash caps, bounded streaming reads, `truncated` and `complete` fields | F-7 |
| 9 | `:25` untouched | New edit F-8 on `poc-security-engineer.md:25`: an incomplete scan is `FAIL` | F-8 |
| 10 | `allowed_root` unspecified | Narrowest common parent; sibling projects share it | F-9 |
| 11 | `rev_range` for `history` and `worktree` | `history` only; enumerated with `git rev-list`, never passed to `git grep`; `--end-of-options` before caller values | F-10 |
| 12 | History scan described as `-e` per rule for `git log` | `git log -G` takes one pattern, so one call per rule; the limits of the history scan are stated | F-11 |
| 13 | Exfiltration not mentioned | `read` plus `web` path recorded as a residual, out of scope | F-12 |
| 14 | Rollout implicit | Rollout, manual permission step, smoke test, no-`execute` test (§6) | Orchestrator |
| 15 | Hit-count summary mixed breaking and non-breaking | Corrected table (§7) | Orchestrator |

## 3. Final implementation spec for the two tools (no code)

Style follows `security-engineer-audit-server-design-v1.md`. Implementation is a separate task, and the agent grant swap is its
**last** step.

### 3.1 Server and shared rules

- **Server.** `poc-security-audit`; tags `[extended]`; transport stdio; no `env` block; module
  `implementation.runtime.security.poc_audit_server` plus a new `git_executor.py` in the same package. It registers exactly two
  tools and no generic command tool. The existing `audit_server.py`, `commands.py`, `executor.py` and `validation.py` are
  **not changed**, so `test_audit_server.py` is unaffected (v1 §4.4).
- **Argv.** Every command is a Python `list[str]` built from constants plus validated data, run with `shell=False`. Every git
  argv begins:
  `git -C <root> -c core.fsmonitor=false -c core.pager=cat -c core.hooksPath=/dev/null` (F-1).
  `git log` additionally carries `--no-textconv --no-ext-diff`. Caller-controlled values come after `--end-of-options` where the
  subcommand accepts it, and after `--` for pathspecs (F-10).
- **Environment (F-1).** The subprocess gets an explicit env and nothing inherited: `PATH`, `HOME=/nonexistent`,
  `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_TERMINAL_PROMPT=0`, `LC_ALL=C`.
- **Root check (F-2).** `root_dir` is resolved and must lie inside `allowed_root`. It must also equal the resolved output of
  `git -C <root> <hardening flags> rev-parse --show-toplevel`; otherwise the call is rejected with a coded error. (Alternative
  the implementer may use instead: run every command with the `:/` pathspec. One of the two must be present.)
- **`allowed_root` (F-9).** Fixed at server start by a `--allowed-root` argument, set to the narrowest common parent of the
  repositories the reviewer may scan: the PoC root when the PoC has its own repository, otherwise the workspace root.
  **Sibling projects under that parent are reachable** (for example agent worktrees under `../worktrees/`). The F-2 toplevel
  check, not `allowed_root`, is what prevents scanning a sub-directory of the wrong repository. This is a recorded limit
  (R-6), not a boundary against sibling repositories.
- **Executor (`git_executor.py`, F-3, F-7).**
  - It is the only new module that spawns a process. It uses `subprocess.Popen` with `shell=False`, never
    `capture_output`, and reads stdout through a bounded streaming loop (a maximum byte count and a maximum hit count).
  - One **aggregate deadline per tool call** covers every loop iteration, not one deadline per subprocess. On expiry it kills
    the process group and returns `complete: false, truncated: true, error: "timeout"`.
  - Caps: refs scanned (default 200), stashes scanned (default 50), hits returned (default 500), per-subprocess bytes. These
    defaults are starting points; the implementer sets them and records them.
  - **Nothing from stderr, and no argv, is ever returned**, on any path including timeout and non-zero exit. Errors are coded
    (`not_a_toplevel`, `bad_scope`, `bad_rev`, `timeout`, `git_missing`, `git_failed`).
- **Redaction (F-3).** The server holds a constant `rule_id` to regex table (private-key headers, well-known provider key
  prefixes, credential assignments, bearer tokens and similar). **The caller supplies no pattern.** The table is reviewed by a
  Security Engineer and carries a `rules_version` that every result echoes. The table is applied to matched content, and also to
  **paths, ref names and tag names** before they are returned. A path or ref that matches is returned as
  `"<redacted-by-rule:RULE_ID>"` with a stable index, never as the name.

### 3.2 `scan_secrets(root_dir, scope, rev_range?)`

- **Inputs.**
  - `root_dir`: as in §3.1.
  - `scope`: closed enum `worktree | index | stashes | history | tracked_names`. Anything else is `bad_scope`.
  - `rev_range` (optional): **valid for `history` only** (F-10), otherwise `bad_scope`. Either a ref name matching
    `^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$` or `<sha>..<sha>` with each side `^[0-9a-f]{7,40}$`. A leading `-` is rejected. A
    range is enumerated with `git ... rev-list --end-of-options <range>` into 40-hex SHAs. **The range string is never passed
    to `git grep`.**
- **Fixed commands, per scope** (rule patterns are inserted as `-e <pattern>` elements of `git grep` from the constant table;
  `-z` is always set):
  - `worktree`: `git grep --untracked --no-exclude-standard -I -n -z -E … --`. Covers untracked and ignored files, so it covers a
    secret not yet committed.
  - `index`: `git grep --cached -I -n -z -E … --`.
  - `stashes`: `git rev-list -g refs/stash` (capped), then `git grep -I -n -z -E … <sha> --` per stash commit.
  - `history`: `git for-each-ref --format=%(objectname) refs/heads refs/remotes refs/tags` (capped) or the enumerated range; then
    `git grep -I -n -z -E … <sha> --` per tip. Then, **one call per rule** (F-11, because `git log -G` takes one pattern):
    `git log -G<pattern> --no-textconv --no-ext-diff --format=%H <sha> --`. Only `%H` is ever requested, never `%s`, `%b` or `-p`.
  - `tracked_names`: `git ls-files -z`, filtered **inside the server** by a fixed allowlist from `security-guidelines.md:134`
    (`.env`, `.env.*`, `credentials.json`, `*.pem`, `*.key`, `id_rsa`, `secrets.yaml`). It returns names only and never opens a
    file.
- **Parsing (F-3).** With `git grep -z -n`, the filename is taken up to the first NUL and the line number up to the next NUL;
  **everything after is dropped unread into the result**. For a tree-ish search the leading `<sha>:` is split off the filename
  field. The implementer must confirm the exact `-z` field layout against the installed git in a test (§6), because I wrote it
  from knowledge of git, not by running it.
- **Output.** `{complete, truncated, rules_version, hits: [{rule_id, scope, path_or_redacted, path_index?, line, commit?, ref?}],
  counts, errors: []}`. No matched text, no stderr, no argv.
- **Limits of the history scan (F-11), stated in the result docs and in R-3.**
  - `git grep <sha>` per tip finds presence **at tips** only.
  - `git log -G` supplies the **introducing commits** for the rules it is run with.
  - Dangling objects and reflog-only commits are **invisible**.
  - A clean result means "no match for the fixed rule set at the scanned refs", not "no secret".

### 3.3 `ref_containment(root_dir, commit)`

- **Inputs.** `root_dir` as in §3.1; `commit` matching `^[0-9a-f]{40}$`.
- **Fixed command.**
  `git -C <root> <hardening flags> for-each-ref --contains <commit> --format=%(refname) refs/remotes refs/tags refs/heads`.
- **Output (F-4).**
  `{commit, remote_refs, tags, local_branches, pushed, last_fetch_time, as_of_last_fetch: true, complete, truncated}`.
  - `pushed` is **`true` or `"unknown"`, never `false`**. It is `true` only if `remote_refs` is non-empty. An empty result is
    `"unknown"`.
  - `last_fetch_time` is the mtime of `FETCH_HEAD` in the git directory, or `null` if it is absent.
  - A `refs/remotes` hit does not prove that the project's main remote holds the commit. The field description says so.
  - Ref and tag names go through the rule table (§3.1) before being returned.
- It never reads commit content and never contacts the network.

## 4. Held edits (exact Before/After)

All are **held** until the implementation task's grant-swap step, and a Security Engineer reviews each. Apply each by its exact
`Before:` text, never by line number. Line numbers are on `63e3d5e`. Confirm that each Before matches exactly once at dispatch.
Characters: `—` is U+2014.

### 4.1 E1-a. `poc-security-engineer.md:4`, the grant

````
Before:
tools: [read, search, execute, web]

After:
tools: [read, search, mcp__security-audit__grep_content, mcp__poc-security-audit__scan_secrets, mcp__poc-security-audit__ref_containment, web]
````

`grep_content` is kept by the user's decision (§1) and is needed for injection and authorization presence checks, because
`search` maps to `Read` only in Claude Code. Its residual is R-1. The three dependency-audit tools are not granted.

### 4.2 E1-b. `poc-security-engineer.md:24`, bind redaction to the tool

````
Before:
scan by pattern, with redacted output. Deleting the secret from the code does not resolve the finding.

After:
scan by pattern, with redacted output, using the secret-scan tool whose output omits matched text, never a tool that prints matched lines. Deleting the secret from the code does not resolve the finding.
````

### 4.3 E1-c. `poc-security-engineer.md:24`, push status (F-4) and the F-5 resolution

**F-5 choice: I reworded E1-c so that it names no actor.** I did **not** add an E2-c to Option 1. Reason: no document tells the
orchestrator to confirm pushes, and adding one means editing a second stable agent for a datum that the reviewer can report
honestly as unconfirmed. The reviewer reports "unknown (unconfirmed against the remote)", and the secret is treated as exposed
either way, so the orchestrator's existing § Exposed secret steps run unchanged.

````
Before:
report the file, line, commits, whether they were pushed, the credential's type and issuer, and the environment variable that should replace it.

After:
report the file, line, commits, whether they were pushed (reported as pushed only when a fetched remote-tracking ref contains the commit, otherwise as unknown and unconfirmed against the remote, with the time of the last fetch; an unpushed result is reported as unknown, and the secret is treated as exposed either way), the credential's type and issuer, and the environment variable that should replace it.
````

### 4.4 F-8. `poc-security-engineer.md:25`, an incomplete scan fails

````
Before:
- End every scan with a verdict (`AGENTS.md` § Validation Gates): `FAIL` while any blocking finding is open, `CONDITIONAL_PASS` if `SECURITY:MEDIUM` findings remain with their remediation plans, otherwise `PASS`

After:
- End every scan with a verdict (`AGENTS.md` § Validation Gates): `FAIL` while any blocking finding is open, `CONDITIONAL_PASS` if `SECURITY:MEDIUM` findings remain with their remediation plans, otherwise `PASS`. A scan that did not complete (tool unavailable, error, timeout or `truncated`) is a blocker and the verdict is `FAIL`; it is never `PASS`. A clean scan means no match for the scan tool's fixed rule set only
````

The After deliberately ends without a final period to match the Before's ending (`PASS` has no period in the source); the
implementer may add one if the line's neighbours use one. I re-read `:25` on this commit before the first artifact; the Before is
that line byte for byte.

### 4.5 Not edited

`poc-orchestrator.md` is **not** edited (Option 2 dropped, F-5 resolved in E1-c). `security-guidelines.md`, `poc-guidelines.md`,
`AGENTS.md` and `tests/golden/**` are byte-unchanged.

### 4.6 Per-edit statements

| Edit | Not upward | No relaxation | Golden coupling | Security |
|---|---|---|---|---|
| E1-a | Edits an agent, not a tier-1 file or a command | Removes `Bash`; adds three fixed-argv tools. No rule, blocking class or duty is relaxed | None live (orchestrator: the two golden mentions of the agent are frozen fixtures). I name no case | Gain: read-only classification (`security-guidelines.md:102`) becomes enforceable. Narrowed claim: only `scan_secrets` is redacting by construction |
| E1-b | Same | Narrows what the agent may do | None known | Instructional, not structural (R-1) |
| E1-c | Same | Keeps the duty to report commits and push status; adds the honest limit and a conservative rule (unknown is treated as exposed) | None known | Prevents a false "not pushed" |
| F-8 | Same | Adds a fail-closed rule; no verdict becomes easier | None known | Closes a fail-open path when the tool is unavailable |

Maturity was not relied on for any of these (ADR-008 P4). Each change stays in `poc-security-engineer.md`, so the agent's
blocking classes at `:22` are untouched.

## 5. D5 note on what changed from v1

The v1 D5 records (a)–(d) stand. The subject, clauses and Step A analysis are unchanged: Step A fired with no conflict, so
nothing is ranked. The user's decision, not a ranking, selects the option.

## 6. Rollout and test list

### 6.1 Rollout (in order; the grant swap is last)

1. Implement `poc_audit_server.py` and `git_executor.py` per §3, in `implementation/runtime/security/`.
2. Add the `poc-security-audit` entry to `implementation/knowledge/mcp/servers.yaml` (`tags: [extended]`, `transport: stdio`,
   `command: python3`, `args: ["-m", "implementation.runtime.security.poc_audit_server", "--allowed-root", …]`, no `env`).
3. Regenerate every platform MCP config (`node implementation/scripts/sync.mjs --root implementation`), and refresh the root
   self-install or declare the drift paths exactly as `--print-drift` reports.
4. **Start-up smoke test:** the server starts, lists exactly its two tools, and answers one call against a fixture repository.
5. **Manual step (documented, never auto-applied):** the `.claude/settings.json` permission for `mcp__poc-security-audit__*`.
   That file is client-owned. The implementation documents the line to add and does not edit it.
6. Security Engineer review of the new tools and the rule table.
7. **Last:** apply E1-a, E1-b, E1-c and F-8; regenerate mirrors and registry (`generate-registry.py`), then the verification
   gates.

### 6.2 Tests the implementation must add

Mirror `test_audit_server.py`'s three tiers.

- **Argv unit tests:** exact argv per scope, with the F-1 prefix and `--no-textconv --no-ext-diff` on `git log`; caller values sit
  after `--end-of-options` or `--`; a malicious `rev_range` or `commit` occupies one element or is rejected.
- **Env test (F-1):** the subprocess environment is exactly the listed set.
- **Config-isolation probe (F-1):** a fixture repository whose `.git/config` plants a `core.fsmonitor` command that would create a
  marker file; a scan runs; the marker must not exist.
- **Toplevel test (F-2):** a sub-directory of a repository and a non-repository are both rejected.
- **Parsing tests (F-3):** a file whose name contains a colon, space or newline; a match line containing a secret-shaped
  string; the result contains neither text. The `-z` layout is asserted against the installed git.
- **Name-redaction tests (F-3):** a path, a branch name and a tag name that match the rule table come back as
  `<redacted-by-rule:RULE_ID>`.
- **No-leak tests (F-3):** no stderr and no argv in any result, including the timeout path and a failing git.
- **Tri-state test (F-4):** `pushed` is `true` or `"unknown"` and never `false`; `last_fetch_time` follows `FETCH_HEAD`; a missing
  `FETCH_HEAD` gives `null`.
- **Bounds tests (F-7):** a repository with more refs and stashes than the caps returns `truncated: true, complete: false`; an
  aggregate deadline is enforced across loop iterations; stdout is read through a bound.
- **Scope test (F-10):** `rev_range` with any scope other than `history` is rejected; the range string never reaches `git grep`.
- **History tests (F-11):** a secret present at a tip and one introduced and later removed are both found by the right
  mechanism; a dangling or reflog-only secret is documented as not found (an expected miss).
- **Structural AST tests:** only `git_executor.py` spawns a process; `shell=False` literal; no `shell=True` anywhere in the
  package (the existing glob at `test_audit_server.py:291`–`:296` already covers new modules); exactly two tools registered; a
  fabricated `execute`/`run_command`/`bash` call is rejected live.
- **Registry/`servers.yaml` test:** the new entry matches the spec exactly.
- **Agent-grant test (new, mirrors `ProjectedClaudeCodeAgentGrantTests`, `test_audit_server.py:324`–`:355`):** the source
  `poc-security-engineer.md` has no `execute`; its projected Claude Code `tools` has no `Bash`; it contains the three expected
  `mcp__…` tokens.
- **Text tests:** the three edits' After texts exist exactly once; "The PoC orchestrator will handle escalation" is still present
  (`test_agent_escalation_consistency.py:107`).
- **Existing suites** (`test_platform_projections.py:207`–`:273`, `test_audit_server.py`, `test_agent_escalation_consistency.py`,
  `test_tool_use_complexity.py`) stay green; the first needs regenerated mirrors.

**Task handling.** If the implementation task is P0/P1 and its `**Affects:**` names `agent/poc-security-engineer`, the agent
leaves `stable` (`check-maturity.py:501`–`:517`). A P2 task, or an `**Affects:**` that does not name it, avoids that. That is
the orchestrator's call.

## 7. Corrected hit-count table

Lines are on `63e3d5e`. "Statements" counts distinct execution-dependent statements. Line spans count each source line once.

| File | Token or class | Lines | Occurrences / statements |
|---|---|---|---|
| `poc-security-engineer.md` | token `execute` | 1 (`:4`) | 1 |
| `poc-security-engineer.md` | all execution-dependent statements | 7 (`:4`, `:11`, `:15`–`:17`, `:22`, `:24`) | 8 (R1–R6, N1, N2) |
| `poc-security-engineer.md` | of those, breaking without a replacement | 2 (`:22`, `:24`) | 4 (R2, R3, R4, R5) |
| `poc-security-engineer.md` | the grant itself | 1 (`:4`) | 1 (R1) |
| `poc-security-engineer.md` | prohibition made structural | 1 (`:24`) | 1 (R6) |
| `poc-security-engineer.md` | non-breaking | 4 (`:11`, `:15`–`:17`) | 2 (N1, N2) |
| `poc-orchestrator.md` | token `execute` as a grant | 1 (`:4`) | 1, untouched |
| `poc-orchestrator.md` | all execution-dependent statements | 6 (`:51`, `:66`, `:70`, `:74`, `:75`, `:77`) | 6 (O1–O6) |
| `poc-orchestrator.md` | of those, breaking for a reviewer without a replacement | 5 (`:51`, `:66`, `:70`, `:75`, `:77`) | 5 (O1, O2, O3, O5, O6) |
| `poc-orchestrator.md` | non-breaking (orchestrator's own work) | 1 (`:74`) | 1 (O4) |

v1's summary row ("8 … 6 breaking or granting, 2 non-breaking") mixed R6 into "breaking". The table above supersedes it. With the
two new tools plus E1-b and F-8, all of R2–R5 and O1–O3, O5, O6 are satisfiable; the residuals in §8 qualify "satisfiable".

## 8. Summary table and parked residuals

| Item | Result |
|---|---|
| Decision | Option 1, `grep_content` kept with a recorded residual |
| Edits | E1-a, E1-b, E1-c, F-8, all in `poc-security-engineer.md`; none in `poc-orchestrator.md` |
| New code | `poc_audit_server.py`, `git_executor.py`, one `servers.yaml` entry, tests |
| Existing tests changed | None (mirrors regenerated) |
| Security review | CONDITIONAL_PASS; F-1..F-12 adopted |
| Golden | No live coupling (orchestrator) |
| Maturity | Not relied on; `stable` holds unless a P0/P1 task names the agent |

**Parked residuals (named, accepted, not fixed here):**

- **R-1 (F-6).** `grep_content` and `read` can print a secret's line into the reviewer's context. E1-b is instructional, not
  structural. Only `scan_secrets` is redacting by construction.
- **R-2 (F-12).** The `read` plus `web` pair is an exfiltration path for anything the agent reads. Out of scope.
- **R-3 (F-11).** The history scan finds tips and introducing commits for a fixed rule set only. Dangling objects and reflogs are
  invisible. A clean scan is not proof of absence.
- **R-4 (F-4).** `pushed` is as fresh as the last fetch and never asserts "not pushed".
- **R-5.** The rule table is incomplete by nature. A secret in an unlisted format is not detected by `scan_secrets`.
- **R-6 (F-9).** `allowed_root` is the narrowest common parent. Sibling projects under it are reachable.
- **R-7.** The `.claude/settings.json` permission is a manual step; until it is done the tools are denied, which fails closed.

## 9. Unverified

1. I did not read the Security Engineer review record. F-1..F-12 follow the orchestrator's relay.
2. The `git grep -z -n` field layout, the `git for-each-ref --contains` and `git rev-list -g` behaviours, and `FETCH_HEAD`
   semantics are written from knowledge of git, not run. §6.2 requires tests that confirm them.
3. Items in v1 §10 that I did not re-read stay unverified: root-parity test content, Cursor and Cline mirror paths, the
   implemented audit-server modules, `agent.schema.json`, the registry file.
4. I did not re-read `poc-security-engineer.md:4`, `:24`, `:25` in this follow-up; their text is from the read of this commit
   earlier in this task (same worktree, unchanged by me).
5. Whether the `.claude/settings.json` permission syntax is `mcp__poc-security-audit__*` is the orchestrator's relay.
