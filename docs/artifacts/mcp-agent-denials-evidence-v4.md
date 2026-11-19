# Artifact: mcp-agent-denials-evidence-v4.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T861 (plan-178, batch AB: SEC-T856-02, with the SEC-T856-01 redaction rule applied). **Owner**: devops-engineer. **Date**: 2026-11-19.
- Based on: mcp-agent-denials-evidence-v3.md (the method, repeated with one change: the neutral scratch root), security-review-t856-batch-aa-v1.md (§ 2.3, § 5), plan-178-batch-ab-opencode-third-round.md, and the generated `implementation/.opencode/agents/*.md` and `implementation/.opencode/opencode.json` of branch `agent/devops-engineer/T861` (develop `aedc43f0` plus the plan-178 commit `e049e772` plus the T861 generator change).
- **What this is**: the raw output of the real Opencode binary's agent-resolution command after T861 added a deny-only `external_directory` map (`"*/gitlab-mcp/*": deny`) to the 13 agents without `execute`, stored verbatim, plus a scripted comparison with the generated maps and my own last-match readings. **No tool call was made** (no model, API key, login or MCP server), so a refused `grep`, `glob` or `read` is **not observed (unverified, K-20)**. The readings are my computation over the resolved lists with a re-implementation of the vendor `Wildcard.match` and `evaluate`, not Opencode output.
- **Version**: npm package `opencode-ai@1.19.2`, installed with `npm install --ignore-scripts opencode-ai@1.19.2` into an empty scratch directory. The platform binary `opencode-linux-x64/bin/opencode` (the file v3's `opencode.exe` link resolved to after `postinstall`) was copied and run directly: sha256 `8d6e8464a306e14429bad028cb06d05cd8aacd75c1bc811b3b816dc64d509122`, the same binary as evidence v2 and v3. `opencode --version` printed `1.19.2`. `~/.opencode/bin` was not used and the user's Opencode configuration was not read.
- **Environment**: as v3. Every `opencode` command ran under `env -i` with only `PATH=/usr/bin:/bin` and `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `XDG_STATE_HOME`, each an empty directory under the run root. No token path, API key or `OPENCODE_*` variable was passed. No token file or token directory was read; token paths below are strings only.
- **Redaction** (SEC-T856-01, rule in `docs/wiki/mcp-servers.md`, Opencode section): the run used the neutral scratch root `/tmp/evidence-run` (projects `a/` and `b/`, `home/`, `xdg/`, `bin/`, `out/`), so the raw files contain no scratch path that names the machine user or the session; the only absolute path Opencode printed is `/tmp/evidence-run/xdg/data/opencode/tool-output/*`. The raw files are therefore stored and hashed **unchanged** (no `<path>` substitution was needed). Checked before hashing: no `/tmp/claude-`, `/home/`, `/Users/`, `/root/`, `/tmp/tmp.` or `/<username>/` in any raw file (also enforced by `T861EvidenceRedactionTests`).
- **Raw files** (verbatim stdout; the `prompt` field is the agent body): `docs/artifacts/mcp-agent-denials-evidence-v4/`; sha256 in § 5.

## 1. Commands

Project A (hostile global, as v1 to v3): `/tmp/evidence-run/a`, an unchanged copy of the regenerated `implementation/.opencode/agents/` (28 files) and one `.opencode/opencode.json`, the generated file without `mcp` and `instructions`, with v1's hostile global `permission` (`"*": allow`, `gitlab_*: allow`, `brave_*: allow`, `playwright_browser_click: deny`, `gitlab_merge_merge_request: ask`) first and the six generated server-level denies after it.

```
opencode --version                          # 1.19.2
opencode debug agent "Demo Agent"         > raw-demo-agent.json
opencode debug agent "Context Retriever"  > raw-context-retriever.json
opencode debug agent "Orchestrator"       > raw-orchestrator.json      # control: holds execute
opencode debug agent "Tech Lead"          > raw-tech-lead.json         # control: holds execute
```

Project B (no hostile rule): `/tmp/evidence-run/b`, the same agents and the generated `opencode.json` without `mcp` and `instructions`.

```
opencode debug agent "Demo Agent"         > plain-raw-demo-agent.json
opencode debug agent "Context Retriever"  > plain-raw-context-retriever.json
```

Every command exited 0 with empty stderr. Segments: Project A rules 0-11 built-in defaults, 12-22 the global config, 23 up to the last-but-one rule the agent's own rules, and a final built-in `external_directory` allow; Project B the same with the global config at 12-17 (the six server-level denies).

## 2. Vendor sources read

At tag `v1.19.2` of `github.com/sst/opencode`, `packages/opencode/src/` (downloaded into the session scratchpad, not into the repository):

- `tool/external-directory.ts` `assertExternalDirectoryEffect` (lines 15-45): returns without asking when the target is inside the instance (`containsPath`); otherwise `dir` is the target itself for `kind: "directory"` and `path.dirname(target)` for a file, and it asks `ctx.ask({ permission: "external_directory", patterns: [path.join(dir, "*")], always: [path.join(dir, "*")] })`. So the asked pattern is **absolute** and always ends in `/*`: `/dev/shm/gitlab-mcp/*` for `/dev/shm/gitlab-mcp/token` or for the directory itself.
- `tool/grep.ts` (line 55), `tool/glob.ts` (line 44, `kind: "directory"`) and `tool/read.ts` (line 250) call it before their own `grep`/`glob`/`read` ask.
- `agent/agent.ts` lines 108-126: the built-in defaults hold `external_directory: { "*": ask, <Truncate.GLOB>: allow, <Global.Path.tmp>/*: allow, <skill dirs>/*: allow, <reference dirs>/*: allow }`. Lines 296-310: "Ensure Truncate.GLOB is allowed unless explicitly configured": for every agent, unless one of its rules is `external_directory` **deny** with pattern **exactly** `Truncate.GLOB` (`<data>/tool-output/*`, `tool/truncate.ts` line 17), `external_directory: { <Truncate.GLOB>: allow }` is merged **after** the agent's rules. A deny-only map of other patterns therefore keeps the tool-output allow, and it stays the last rule.
- `util/wildcard.ts` `match`: as v3 (`*` -> `.*`, flag `s`, anchored; a trailing ` *` is optional), so `*/gitlab-mcp/*` matches `/dev/shm/gitlab-mcp/*` and `/run/user/1000/gitlab-mcp/sub/*`, and does not match `/dev/shm/*` or `<data>/tool-output/*`.

Consequence for the generated pattern: only `*/gitlab-mcp/*` is emitted. `*/gitlab-mcp` (no trailing `/*`) can never equal an asked pattern, so it would be dead.

## 3. Scripted comparison and last-match readings

Script `compare.py` (scratch, sha256 `6f8e6c842161046f8049666570db1375ee9bc1cf8b7a1d00757f36c6351ab3b6`; `python3 -I compare.py <worktree> <raw dir>`):

- Reads each raw `permission` array as `(permission, action, pattern)` and replaces the tool-output pattern (v3's or v4's scratch root) with `<tool-output>`.
- Parses the generated agent frontmatter with `yaml.safe_load` into ordered triples (the `fromConfig` rule, independent of `sync.mjs`).
- **(a)** the agent segment must equal the generated triples exactly; **(c)** the built-in and global segments must equal v3's; **(b)** `difflib.SequenceMatcher` over v3's and v4's agent segments, every non-equal opcode printed.
- Last-match readings over the whole resolved list (the tool-output ask uses v4's path).

Result (verbatim for Demo Agent; the other lines summarised):

```
== plain-raw-context-retriever: rules=46 agent_segment=27 generated=27 (a)=PASS final_rule=('external_directory', 'allow', '<tool-output>')
   (c) rules 0-17 identical to v3: True
   (b) insert: v3[26:26]=[] -> v4[26:27]=[('external_directory', 'deny', '*/gitlab-mcp/*')]
== plain-raw-demo-agent: rules=55 agent_segment=36 generated=36 (a)=PASS final_rule=('external_directory', 'allow', '<tool-output>')
   (c) rules 0-17 identical to v3: True
   (b) insert: v3[35:35]=[] -> v4[35:36]=[('external_directory', 'deny', '*/gitlab-mcp/*')]
== raw-context-retriever: rules=51 agent_segment=27 generated=27 (a)=PASS final_rule=('external_directory', 'allow', '<tool-output>')
   (c) rules 0-22 identical to v3: True
   (b) insert: v3[26:26]=[] -> v4[26:27]=[('external_directory', 'deny', '*/gitlab-mcp/*')]
== raw-demo-agent: rules=60 agent_segment=36 generated=36 (a)=PASS final_rule=('external_directory', 'allow', '<tool-output>')
   (c) rules 0-22 identical to v3: True
   (b) insert: v3[35:35]=[] -> v4[35:36]=[('external_directory', 'deny', '*/gitlab-mcp/*')]
   external_directory '/dev/shm/gitlab-mcp/*': last match rule 58 ('external_directory', 'deny', '*/gitlab-mcp/*')
   external_directory '/run/user/1000/gitlab-mcp/*': last match rule 58 ('external_directory', 'deny', '*/gitlab-mcp/*')
   external_directory '/run/user/1000/gitlab-mcp/sub/*': last match rule 58 ('external_directory', 'deny', '*/gitlab-mcp/*')
   external_directory '/tmp/evidence-run/xdg/data/opencode/tool-output/*': last match rule 59 ('external_directory', 'allow', '<tool-output>')
   external_directory '/tmp/opencode/*': last match rule 12 ('*', 'allow', '*')
   external_directory '/dev/shm/*': last match rule 12 ('*', 'allow', '*')
   external_directory '/run/user/1000/*': last match rule 12 ('*', 'allow', '*')
   external_directory '/etc/*': last match rule 12 ('*', 'allow', '*')
   read '../../dev/shm/gitlab-mcp/token': last match rule 57 ('read', 'deny', '*/gitlab-mcp/*')
   read '.env': last match rule 12 ('*', 'allow', '*')
== raw-orchestrator: rules=72 agent_segment=48 generated=48 (a)=PASS final_rule=('external_directory', 'allow', '<tool-output>')
   (c) rules 0-22 identical to v3: True
== raw-tech-lead: rules=42 agent_segment=18 generated=18 (a)=PASS final_rule=('external_directory', 'allow', '<tool-output>')
   (c) rules 0-22 identical to v3: True
```

- The only change against v3 in every agent without `execute` is the one inserted `external_directory` deny, as the agent's last rule; the built-in and global segments are unchanged; the two `execute` controls are unchanged (no `(b)` opcode).
- **Token directory** (`grep` or `glob` with path `/dev/shm/gitlab-mcp` or a file in it, `read` of the token): the `external_directory` ask is `<dir>/*`, last match the agent's deny, in Project A (hostile `"*": allow`) and in Project B. Context Retriever: the same at rule 49 (A) and 44 (B).
- **Tool output** (`<data>/tool-output/*`): last match the final built-in allow in every list, so Opencode's built-in tool-output allow is kept.
- **Everything else** (`/tmp/opencode/*`, `/dev/shm/*`, `/run/user/1000/*`, `/etc/*`): unchanged, the global `"*": allow` in A and the default `ask` (rule 2) in B.

## 4. Residuals (not closed by this map)

- **A parent directory.** `grep` with path `/dev/shm` or `/run/user/1000` asks `/dev/shm/*` or `/run/user/1000/*`, which the map does not match; ripgrep then searches `gitlab-mcp/token` below it. Under a broad user allow that returns the token's contents. Denying the parent would deny all of `/dev/shm` or the runtime directory, so it is not generated. The denies stay **defense in depth, not a boundary** (SEC-T856-02 stays open as a residual).
- **A non-default directory name, or a link inside the project** (SEC-T856-03): a path inside the project is never asked as `external_directory` (`containsPath`), and only the name `gitlab-mcp` is matched.
- Not observed with a real tool call (K-20).

## 5. Hashes

```
f40066dce55b4b7dc674f3bbf69983a7fee76b550674feecab5dce0b92afe774  plain-raw-context-retriever.json
4869e57fb624e00571e745f1fc85cac67da379ea2c75df0cd99d2fd3e0aa5e2b  plain-raw-demo-agent.json
aad1f119dbe0cf236b8c862fe84d5eb6249c31f24d7bda264d949e8001c63592  raw-context-retriever.json
e348156d07c125c6950c5c90e0b57ea3f66fc5324cf65e34453c2f495dc9a4d1  raw-demo-agent.json
d3917cc23d236813adfb7e1ad12f7c0bfcb4ca1c7cd0ef5ad8e479a02095d74c  raw-orchestrator.json
94e4085886eb79e272b997afb80f04861f6b5ba3df6c10c9dd6a36f536b4e9eb  raw-tech-lead.json
```
