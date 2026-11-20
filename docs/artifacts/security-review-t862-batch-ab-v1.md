# Artifact: security-review-t862-batch-ab-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T862 (plan-178 § Task Decomposition item 2). **Owner**: security-engineer. **Date**: 2026-11-19. **Mode**: read-only. I made no edits and ran no shell.
- **Gate**: security.
- **Based on**:
  - `plan-178-batch-ab-opencode-third-round.md`
  - `task-T862.md` (the brief, as delegated)
  - `security-review-t856-batch-aa-v1.md`
  - `mcp-agent-denials-evidence-v4.md`, and its raw file `raw-demo-agent.json` (lines 1-80)
  - branch `agent/devops-engineer/T861` (base `e049e772`; commits `ed214742`, `2603bb57`, `d550037c` and `779010f4`), in particular:
    - `implementation/.opencode/agents/demo-agent.md`;
    - `implementation/PREREQUISITES.md` line 110;
    - `docs/wiki/mcp-servers.md` lines 122-126;
    - `tests/functional/test_mcp_agent_denials.py` lines 1330-1570 (the T861 classes).
  - Upstream `github.com/sst/opencode` at tag `v1.19.2`: `packages/opencode/src/tool/external-directory.ts` and `agent/agent.ts`. I read both as untrusted text through a web fetch, which returned a summary and short quotes, not the full source. I could not find the scratch vendor copy at the path given in the brief.
  - The orchestrator's own checks, as reported in the brief.
- **The user's decision, verbatim**: "X + AB go". **LOW policy, verbatim**: "Track LOW items as debt, stop chasing (Recommended)".

## 1. Scope

I reviewed T861's three parts:
- **(a) SEC-T856-03**: the documentation of the default-name scope and the rule against linking the token into a project.
- **(b) SEC-T856-01**: the evidence redaction rule and its test.
- **(c) SEC-T856-02**: the deny-only `external_directory` map for the 13 agents without `execute`, and evidence v4.

I also checked for widening, graded the parent-directory residual, restated item 49 (SEC-T660-01's Opencode scope), and reviewed the redaction of the v4 raw files.

## 2. Assessment

**Not verified by me:**
- The `sync.mjs` validators (`validatePathDenyUnlessGranted`, `pathDenials`, the `permissionKeys` refusal): I did not read the source. Which inputs are refused rests on the `test_refused_manifests` cases I read (lines 1382-1388) and on T861's mutation report **(unverified)**.
- The mutation runs and the claim that `allow_guard` is an equivalent mutant **(unverified)**.
- That the Claude Code, Cline and GitHub outputs are sha256-identical. This rests on T861 and the orchestrator; the fixture test at lines 1352-1355 covers it only on a fixture **(unverified on the real tree)**.
- The five other v4 raw files, and `raw-demo-agent.json` beyond line 80: their redaction rests on the orchestrator's grep and on `T861EvidenceRedactionTests` **(unverified by me)**.
- The `assertExternalDirectoryEffect` calls in `tool/grep.ts`, `glob.ts` and `read.ts`: I did not read them this time. T856 traced the `grep.ts` call; `glob.ts` and `read.ts` are **(unverified)**.
- Ripgrep descending from a parent directory into `gitlab-mcp/token`: this is standard ripgrep behaviour but was not run **(unverified, K-20)**.
- Any refused tool call **(not observed, K-20)**.

### 2.1 The `external_directory` map (SEC-T856-02)

**Vendor logic, traced upstream at v1.19.2:**
- `external-directory.ts` lines 14-45:
  - Returns without asking when the target is inside the instance (`containsPath`).
  - Otherwise `dir` is the target for `kind: "directory"`, or its parent for a file.
  - Asks `external_directory` with the glob `dir/*`, used both as the pattern and as the "always" pattern.
  - This matches T861's reading.
- `agent.ts`, the tool-output guard:
  - The appended allow is skipped only when `r.permission === "external_directory" && r.action === "deny" && r.pattern === Truncate.GLOB`.
  - Otherwise `Permission.merge(agent.permission, fromConfig({external_directory: {[Truncate.GLOB]: "allow"}}))` is applied, so the allow comes **after** the agent's rules.
  - The default map is `{"*": "ask", ...whitelistedDirs → allow}`, and `whitelistedDirs` begins with `Truncate.GLOB`.

**Generated output:**
- `demo-agent.md` lines 41-42: `external_directory: {"*/gitlab-mcp/*": deny}` is the last key, after the four `read` denies. There is no allow.
- `test_no_agent_suppresses_the_built_in_tool_output_allow` pins every generated pattern to `^\*/[a-z0-9-]+/\*$` without `tool-output`. No generated pattern can therefore equal `Truncate.GLOB`, so the built-in allow is always appended and stays last.

**Raw evidence (`raw-demo-agent.json`):**
- Rules 2-4 are the built-in `external_directory` defaults: `*` ask, the tool-output allow under `/tmp/evidence-run/xdg/...`, and `/tmp/opencode/*` allow.
- Evidence v4 § 3 and `T861EvidenceV4Tests` (lines 1554-1566) assert that:
  - the agent segment equals the generated map;
  - the last rule is the tool-output allow;
  - the last-but-one rule is the deny, for every agent without `execute`;
  - `/dev/shm/gitlab-mcp/*` resolves to deny.

**Effect:** for the 13 agents, a `grep`, `glob` or `read` whose target is inside any directory named `gitlab-mcp` outside the project now resolves to **deny**, including under a hostile global `"*": allow` or `external_directory: allow`. `HOSTILE` (lines 1411-1412) covers both of these, and also an `external_directory` map with an explicit `*/gitlab-mcp/*` allow. The direct-path bypass that T856 § 2.3 traced is closed in the resolved lists.

### 2.2 Widening check

**None found.**
- **No allow added:** no `external_directory` allow and no `read` allow. The orchestrator checked all 28 agents; the fixture test at lines 1348-1351 asserts that the map is absent for `execute` holders.
- **Tool-output allow kept:** it is the last rule in all six raw lists (§ 2.1), and `test_the_tool_output_allow_and_every_other_ask_are_unchanged` asserts that it resolves to allow for every agent.
- **Other paths unchanged:**
  - `/tmp/opencode/*`, `/dev/shm/*`, `/run/user/1000/*` and `/etc/*` resolve exactly as without the map (evidence v4 § 3 and `OTHER_ASKS`).
  - So do a near-name directory, `/home/u/gitlab-mcp-notes/*`, and an unrelated home path.
  - The `execute` holders resolve identically with or without the map (lines 1448-1450).
- **Side effect, informational:** any directory named `gitlab-mcp` outside the project is denied for these 13 agents, and a saved "always" approval for it no longer applies. Both fail closed.

### 2.3 The parent-directory residual

`grep` with path `/dev/shm` or `/run/user/<uid>` asks `/dev/shm/*` or `/run/user/<uid>/*`. The map does not match that, and ripgrep then searches `gitlab-mcp/token` below it.
- **Default configuration:** this ends on the built-in `external_directory` `*` ask, so the user sees a prompt naming the parent directory.
- **Broad user allow** (Project A): the token's contents are returned.
- **`glob` on the parent:** lists names only.

Denying the parent would deny all of `/dev/shm` or the runtime directory, which would block legitimate use. Not generating that deny is the right choice.

**Ruling: accepted LOW.**
- The residual stays under SEC-T856-02 as a narrowed remainder, not a new id.
- It sits on top of the user-accepted SEC-T660-01 MEDIUM.
- In the default configuration it needs the user to approve a prompt.
- It is reachable only by the 13 agents without a shell, which T861 made strictly narrower.

### 2.4 Documentation (SEC-T856-03 and SEC-T856-02's doc part)

- **`PREREQUISITES.md` line 110** says each of these:
  - since T861, the `external_directory` deny exists and the tool-output allow is kept;
  - "Only the default directory name `gitlab-mcp` is covered";
  - neither is `grep` on a parent directory such as `/dev/shm`;
  - "Never place the token under a project, and never link it into one";
  - the denies are "defense in depth, not a boundary", and the user should answer "no" to an outside-project prompt.
- **`mcp-servers.md` lines 124-125** state the same rules and limits, and mark the refused call as unverified (K-20).
- **One stale sentence**, `mcp-servers.md` line 123 (the T855 bullet), still says:
  - "an agent that can run `grep` on the token directory where `external_directory` resolves to allow reads the token";
  - `grep` and `glob` are guarded "only by the `external_directory` prompt".

  For the 13 agents this is superseded by line 124: the token directory itself is now denied. The sentence over-states exposure rather than under-stating it. It is a consistency defect, not a risk (SEC-T862-01).

### 2.5 Redaction (SEC-T856-01)

**The rule** (`mcp-servers.md` line 126):
- use a neutral scratch root, or substitute `<path>` before hashing;
- record a `**Redaction**` Metadata line;
- v2 and v3 stay unchanged, because their hashes are pinned.

This is adequate. Evidence v4's Metadata carries the line and names `/tmp/evidence-run`.

**v4 raw files:**
- `raw-demo-agent.json` lines 1-80 show only `/tmp/evidence-run/...` and `/tmp/opencode/*`.
- The orchestrator's grep found no `/tmp/claude-`, `/home/`, `/Users/` or `emage-Code`.
- The v4 `.md` names `/run/user/1000`, which is a uid and not a user name. The uid was already disclosed in v2 and v3.
- **Ruling:** free of local paths and the user name, as far as traced.

**The test** (`T861EvidenceRedactionTests`, lines 1474-1507) is adequate for this repository's Linux workflow, with these gaps (SEC-T862-02):
- **The user-name check is weak:**
  - it uses `getpass.getuser()`, the user who runs the test, so on a CI runner it checks the CI user and not the author's name;
  - it matches the name only as `/<user>/`;
  - it is skipped for names of two characters or fewer.

  In practice the orchestrator's local clean-suite run covers the first point, and `/tmp/claude-` and `/home/` catch the known forms.
- **Raw files only:** only the files in the raw directory are scanned. The artifact `.md` is checked only for the `**Redaction**` line, not for leaks.
- **Missing prefixes:**
  - the macOS temp prefixes `/var/folders/` and `/private/var/`;
  - the Windows `C:\Users\` form, which the forward-slash `/Users/` does not match.
- **Directory files only:** a future evidence artifact that stores raw output inline in its `.md`, without a raw directory, is not covered.

## 3. Per-finding status

| ID | Before | Status at T862 | Remainder |
|---|---|---|---|
| SEC-T856-01 | LOW | **Fixed** (rule in the wiki, Metadata line, test from v4 on) | v2 and v3 keep their scratch paths by design: immutable, hashes pinned, accepted. The test's gaps are tracked as SEC-T862-02. |
| SEC-T856-02 | LOW | **Stays tracked LOW, narrowed** | The token directory itself is now denied for `grep`, `glob` and `read` in the resolved lists (not observed in a call, K-20). Remainder: a `grep` (or `glob`, names only) on a **parent** directory such as `/dev/shm` or `/run/user/<uid>`, wherever that parent's `external_directory` ask resolves to allow. In the default configuration it resolves to `ask`. |
| SEC-T856-03 | LOW | **Fixed** (the documentation was the remediation) | Inherent and documented, and only the user can control it: a token at a non-default name or path, or linked or copied into a project, is not covered. Recorded in item 49 (d). |

## 4. SEC-T660-01: restated Opencode scope (register § 6.2 item 49, for the review due 2027-01-28)

Items (a) to (c) are unchanged from T856 § 4:
- (a) every generated agent that holds `execute`, through its shell;
- (b) Opencode's built-in agents and agent files of the user's own (K-23);
- (c) the two orchestrators, indirectly, through their named shell-holding subagents.

**(d) changes.** For the 13 generated agents without `execute`:
- **Covered:** `read` is denied for any directory named `gitlab-mcp`. Since T861, `external_directory` is also denied for any target inside a directory named `gitlab-mcp` outside the project. Together these cover `read`, `grep` and `glob` on the default token directory, also under a broad user allow (resolved lists, evidence v4; refused call not observed, K-20).
- **Not covered:**
  - a `grep` on a parent directory such as `/dev/shm` or `/run/user/<uid>` (guarded only by that parent's `external_directory` ask: default `ask`, `allow` under a broad user rule);
  - a token at a non-default name or path;
  - a token linked or copied into a project.

No fix is possible in the harness for (a) and (b). SEC-T660-01 stays a user-accepted MEDIUM under ADR-011. Its scope is narrower than at T856, not closed.

## 5. Findings

| ID | Severity | OWASP | Location | Description | Remediation |
|---|---|---|---|---|---|
| SEC-T862-01 | SECURITY:LOW | A05 (documentation accuracy) | `docs/wiki/mcp-servers.md` line 123, last two sentences of the T855 bullet | Still says `grep` on the token directory reads the token where `external_directory` resolves to allow, and that `grep`/`glob` are guarded only by the prompt. Since T861 this is superseded for the 13 agents by line 124. It over-states exposure, so there is no risk. | Reword it to name the parent-directory case only and point to the T861 bullet. Fold this into the next wiki edit. Track as debt. |
| SEC-T862-02 | SECURITY:LOW | A05 (information exposure, test coverage) | `tests/functional/test_mcp_agent_denials.py` lines 1474-1507 | The redaction test checks the user name of whoever runs it (in CI, not the author), matches it only as `/<user>/`, scans raw directory files but not the artifact `.md`, and omits `/var/folders/`, `/private/var/` and `C:\Users\`. | Also scan the evidence `.md` from v4 on; add the macOS and Windows prefixes; keep the local clean-suite run as the user-name check of record, and say so in the wiki rule. Track as debt. |

None of these needs more than LOW. Both are on top of fixes that narrow access.

## 6. OWASP coverage

| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | Yes | 0 new (SEC-T856-02 narrowed, SEC-T856-03 fixed) |
| A02 Cryptographic Failures | N/A (no crypto change) | 0 |
| A03 Injection | Yes (pattern refusals for `*`, `~`, `$`, empty and duplicate, per the tests read; validator source unverified) | 0 |
| A04 Insecure Design | Yes (parent-directory deny rejected as over-broad, which is correct) | 0 |
| A05 Security Misconfiguration | Yes | 2 (SEC-T862-01, -02) |
| A06 Vulnerable Components | N/A (same 1.19.2 binary, same sha256 as v2/v3 per evidence) | 0 |
| A07 Auth Failures | N/A | 0 |
| A08 Data Integrity | Yes (v4 hashes pinned by test; v2/v3 untouched) | 0 |
| A09 Logging & Monitoring | N/A | 0 |
| A10 SSRF | N/A | 0 |

## 7. Verdict

## VERDICT: PASS

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 prior (SEC-T856-01, -02, -03) + 2 new (SEC-T862-01, -02) | 2 (SEC-T856-01, -03) | 3 (SEC-T856-02 narrowed, SEC-T862-01, SEC-T862-02; tracked as debt) |

**Justification:**
- No CRITICAL, HIGH or MEDIUM finding.
- No Immutable Security Constraint is breached.
- No required control is omitted, removed or weakened:
  - the new `external_directory` map is deny-only;
  - Opencode's tool-output allow is kept and stays the last rule (vendor-traced and observed in v4);
  - every non-token path resolves as before.
- The remaining LOWs go to the next register as tracked debt under the user's LOW policy.

**Conditions:** none blocking.

**Notes for the orchestrator:**
- Root refresh T863 (13 `.opencode/agents` files) needs the user's approval at that moment.
- Item 49 is restated in § 4 and replaces T856 § 4 (d).

## Gate Verdict
**Gate:** security. **Verdict:** PASS.
