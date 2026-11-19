# Artifact: mcp-agent-denials-evidence-v3.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T855 (plan-175, SEC-T844-01, SEC-T842-02; SEC-T837-02 for the version range). **Owner**: devops-engineer. **Date**: 2026-11-19.
- Based on: mcp-agent-denials-evidence-v2.md (the method, repeated unchanged), security-review-t837-opencode-permission-v1.md, security-review-t842-opencode-deny-v1.md, security-review-t844-opencode-task-v1.md, plan-175-batch-aa-opencode-and-td-t849-01.md, and the generated `implementation/.opencode/agents/*.md` and `implementation/.opencode/opencode.json` of branch `agent/devops-engineer/T855` (develop `70a279cf` plus the plan-175 commit `be4ecbe0` plus the T855 generator change).
- **What this is**: the raw output of the real Opencode binary's agent-resolution command for the generated agent files after T855 added two pattern-valued keys (a `task` map for the two delegating agents, a deny-only `read` map for the 13 agents without `execute`), stored verbatim, plus a scripted comparison with the generated maps and my own last-match readings. **No tool call was made** (no model, API key, login or MCP server), so a launched or refused subagent and a refused read are **not observed (unverified, K-20)**. The last-match readings are my computation over the resolved lists with a re-implementation of the vendor `Wildcard.match` and `evaluate` (sources below), not Opencode output.
- **Version**: npm package `opencode-ai@1.19.2`, installed with `npm install opencode-ai@1.19.2` into an empty scratch directory; npm did not run the `postinstall` script (npm `allow-scripts` policy). `node_modules/.bin/opencode` links to `opencode-ai/bin/opencode.exe`, sha256 `8d6e8464a306e14429bad028cb06d05cd8aacd75c1bc811b3b816dc64d509122`, the same binary as evidence v2. `opencode --version` printed `1.19.2`. `~/.opencode/bin` was not used and the user's Opencode configuration was not read.
- **Environment**: as v2. Every `opencode` command ran under `env -i` with only `PATH=/usr/bin:/bin` and `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `XDG_STATE_HOME`, each an empty scratch directory. No token path, API key or `OPENCODE_*` variable was passed. No token file or token directory was read; the token paths below are strings in rules and in my readings only.
- **Raw files** (verbatim stdout; the `prompt` field is the agent body; `external_directory` patterns contain the scratch paths of this run): `docs/artifacts/mcp-agent-denials-evidence-v3/`; sha256 in § 5.

## 1. Commands

Project A (hostile global, as v1 and v2): a scratch project holding an unchanged copy of the regenerated `implementation/.opencode/agents/` (28 files) and one `.opencode/opencode.json`, the generated file without `mcp` and `instructions`, with v1's hostile global `permission` written first and the six generated server-level denies after it (the same 11 keys, in the same order, as v2 § 1).

```
opencode --version                          # 1.19.2
opencode debug agent "Orchestrator"       > raw-orchestrator.json
opencode debug agent "PoC Orchestrator"   > raw-poc-orchestrator.json
opencode debug agent "Demo Agent"         > raw-demo-agent.json
opencode debug agent "Context Retriever"  > raw-context-retriever.json
opencode debug agent "Tech Lead"          > raw-tech-lead.json          # control: holds execute, unchanged
opencode debug agent "tech-lead"          > slug-tech-lead.txt 2>&1     # exit 1: the file slug is not a key
```

Project B (no hostile rule): the same agents and the generated `opencode.json` without `mcp` and `instructions` and with nothing added, to show the `.env` defaults deciding.

```
opencode debug agent "Demo Agent"         > plain-raw-demo-agent.json
opencode debug agent "Context Retriever"  > plain-raw-context-retriever.json
```

Every command exited 0 with empty stderr, except the slug probe, which exited 1 with `Agent tech-lead not found, run 'opencode.exe agent list' to get an agent list` (stored).

Segments of every Project A list, as in v2: rules 0-11 Opencode's built-in defaults, 12-22 the global config, 23 up to the last-but-one rule the agent's own rules in file order, and a final built-in `external_directory` allow.

## 2. Vendor sources read (1.x syntax)

All at tag `v1.19.2` of `github.com/sst/opencode`, `packages/opencode/src/`, unless stated:

- `config/agent.ts`: a markdown agent's config is `{ name: <file slug>, ...frontmatter, prompt }` and is stored under `result[config.name]`, so a frontmatter `name` ("Tech Lead") replaces the slug as the key. The slug probe in § 1 confirms it.
- `agent/agent.ts`: `get(agent)` returns `agents[agent]`; an agent's rules are `merge(defaults, user, fromConfig(agent.permission))`; the built-in agents are `build`, `plan`, `general`, `explore`, `compaction`, `title`, `summary`.
- `tool/task.ts`: `ctx.ask({ permission: "task", patterns: [params.subagent_type] })`, then `agent.get(params.subagent_type)`; so the `task` pattern is matched against the agent key, the frontmatter `name`.
- `tool/registry.ts` `describeTask`: the task tool lists only non-primary agents for which `evaluate("task", item.name, agent.permission)` is not `deny`. The list itself is built per model call and is not printed by `debug agent`; my reading of it is in § 3.
- `permission/index.ts`: `fromConfig` turns a string value into one rule with pattern `*` and a map value into one rule per `pattern: action` entry, in key order (`~/` and `$HOME` are expanded); `evaluate` is `findLast(rule => Wildcard.match(permission, rule.permission) && Wildcard.match(pattern, rule.pattern))`, default `ask`; `disabled` hides a tool only when its last rule has pattern `*` and is a deny.
- `util/wildcard.ts` `match`: regex-escape, `*` -> `.*`, `?` -> `.`, anchored, flag `s` (so `*` matches `/`), case-sensitive on Linux.
- `tool/read.ts`: after the `external_directory` check, `ctx.ask({ permission: "read", patterns: [path.relative(instance.worktree, filepath)] })`. At tag `v1.0.224` the pattern was the absolute `filepath`. `tool/grep.ts` and `tool/glob.ts` ask `grep`/`glob` with the search pattern, not the path.
- Floor of the supported range (SEC-T837-02): `permission/next.ts` with the same `findLast`/`Wildcard.match` evaluation, `agent/agent.ts` using `PermissionNext.fromConfig`, and `config/config.ts` with a `Permission` schema that has `.catchall(PermissionRule)` (any key, string or pattern map; `task` a `PermissionRule`) all exist at tag `v1.0.224` (commit `d60393835c`, 2026-01-02; npm publish 2026-01-02T03:04:58Z) and `permission/next.ts` is absent at `v1.0.223`, `v1.0.222`, `v1.0.220`, `v1.0.215`, `v1.0.210`, `v1.0.200`, `v1.0.100` and `v1.0.0` (HTTP 404). Not run on 1.0.224.
- Docs (ctx7 `/anomalyco/opencode/v1.0.224`, `agents.mdx` and `permissions.mdx`): a markdown agent `permission:` map with a pattern map under a key (`bash: { "git diff": allow, "*": ask }`) is documented at 1.0.224.

## 3. Scripted comparison and last-match readings

Script `compare.py` (scratch, sha256 `d22734bf13a5fba0a2bcd18076b69552230d79ea8bf05186097f05982471453c`; run with `python3 -I compare.py <worktree> <raw dir>`), faithful summary:

- Reads each raw file's `permission` array as `(permission, action, pattern)` and replaces non-`*` `external_directory` patterns with `<path>`.
- Parses the generated agent file's frontmatter with `yaml.safe_load` into ordered `(key, action, pattern)` triples: a string value is `(key, value, "*")`, a map value one triple per entry in order (the `fromConfig` rule above, derived independently of `sync.mjs`).
- **(a)** Agent segment `[23:-1]` must equal the generated triples exactly (key, action, pattern, order); the final rule must be `external_directory allow <path>`.
- **(c)** For the agents of v2, rules 0-22 must equal v2's (same built-ins, same global segment).
- **(b)** For the agents of v2, `difflib.SequenceMatcher` over v2's and v3's agent segments; every non-equal opcode is printed.
- Last-match readings with the § 2 `match`/`evaluate`, over the whole resolved list.

Result (verbatim, the readings of Context Retriever, Tech Lead and PoC Orchestrator shortened to the lines that differ in kind):

```
== context-retriever: rules=50 agent_segment=26 generated=26 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 identical to v2: True
   (b) insert: v2[22:22]=[] -> v3[22:26]=[('read', 'deny', 'gitlab-mcp'), ('read', 'deny', 'gitlab-mcp/*'), ('read', 'deny', '*/gitlab-mcp'), ('read', 'deny', '*/gitlab-mcp/*')]
   read '../../../../../run/user/1000/gitlab-mcp/token': last match rule 48 ('read', 'deny', '*/gitlab-mcp/*')
   read '../../../../dev/shm/gitlab-mcp/token': last match rule 48 ('read', 'deny', '*/gitlab-mcp/*')
   read '.env': last match rule 12 ('*', 'allow', '*')
== demo-agent: rules=59 agent_segment=35 generated=35 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 identical to v2: True
   (b) insert: v2[31:31]=[] -> v3[31:35]=[('read', 'deny', 'gitlab-mcp'), ('read', 'deny', 'gitlab-mcp/*'), ('read', 'deny', '*/gitlab-mcp'), ('read', 'deny', '*/gitlab-mcp/*')]
   read '../../../../../run/user/1000/gitlab-mcp/token': last match rule 57 ('read', 'deny', '*/gitlab-mcp/*')
   read '../../../../dev/shm/gitlab-mcp/token': last match rule 57 ('read', 'deny', '*/gitlab-mcp/*')
   read '/run/user/1000/gitlab-mcp/token': last match rule 57 ('read', 'deny', '*/gitlab-mcp/*')
   read '/dev/shm/gitlab-mcp/token': last match rule 57 ('read', 'deny', '*/gitlab-mcp/*')
   read '../../dev/shm/gitlab-mcp': last match rule 56 ('read', 'deny', '*/gitlab-mcp')
   read 'gitlab-mcp/token': last match rule 55 ('read', 'deny', 'gitlab-mcp/*')
   read '.env': last match rule 12 ('*', 'allow', '*')
   read 'config/.env': last match rule 12 ('*', 'allow', '*')
   read '.env.local': last match rule 12 ('*', 'allow', '*')
   read 'tests/_baselines/gitlab-mcp-tool-names.json': last match rule 12 ('*', 'allow', '*')
   read 'src/main.py': last match rule 12 ('*', 'allow', '*')
== orchestrator: rules=72 agent_segment=48 generated=48 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 identical to v2: True
   (b) insert: v2[33:33]=[] -> v3[33:48]=[('task', 'deny', '*'), ('task', 'allow', 'Product Owner'), ('task', 'allow', 'Solution Architect'), ('task', 'allow', 'Scrum Master'), ('task', 'allow', 'Tech Lead'), ('task', 'allow', 'Backend Developer'), ('task', 'allow', 'Frontend Developer'), ('task', 'allow', 'Database Engineer'), ('task', 'allow', 'QA Engineer'), ('task', 'allow', 'Security Engineer'), ('task', 'allow', 'DevOps Engineer'), ('task', 'allow', 'Release Manager'), ('task', 'allow', 'Technical Writer'), ('task', 'allow', 'UX Designer'), ('task', 'allow', 'Context Retriever')]
   task 'general': last match rule 56 ('task', 'deny', '*')
   task 'build': last match rule 56 ('task', 'deny', '*')
   task 'plan': last match rule 56 ('task', 'deny', '*')
   task 'explore': last match rule 56 ('task', 'deny', '*')
   task 'Tech Lead': last match rule 60 ('task', 'allow', 'Tech Lead')
   task 'Demo Agent': last match rule 56 ('task', 'deny', '*')
   task 'Orchestrator': last match rule 56 ('task', 'deny', '*')
   task 'PoC Orchestrator': last match rule 56 ('task', 'deny', '*')
   task 'tech-lead': last match rule 56 ('task', 'deny', '*')
== poc-orchestrator: rules=64 agent_segment=40 generated=40 (a)=PASS final_rule_external_directory=True
   task 'general': last match rule 48 ('task', 'deny', '*')
   task 'Tech Lead': last match rule 48 ('task', 'deny', '*')
   task 'Demo Agent': last match rule 54 ('task', 'allow', 'Demo Agent')
== tech-lead: rules=42 agent_segment=18 generated=18 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 identical to v2: True
   read '../../../../dev/shm/gitlab-mcp/token': last match rule 12 ('*', 'allow', '*')
OVERALL PASS
```

In Project A every `.env` reading ends on rule 12, the hostile global `"*": "allow"`, with or without the agent's `read` map: the map changes no `.env` outcome. Project B (`plain.py`, sha256 `98fc9c19740d6010b78d20d0922fb68496f378d79832ab6dc884930221d2cb50`), verbatim:

```
== raw-context-retriever rules 45
   read '../../../../dev/shm/gitlab-mcp/token': rule 43 ('read', 'deny', '*/gitlab-mcp/*')
   read '../../../../../run/user/1000/gitlab-mcp/token': rule 43 ('read', 'deny', '*/gitlab-mcp/*')
   read '.env': rule 9 ('read', 'ask', '*.env')
   read 'config/.env': rule 9 ('read', 'ask', '*.env')
   read '.env.local': rule 10 ('read', 'ask', '*.env.*')
   read '.env.example': rule 11 ('read', 'allow', '*.env.example')
   read 'src/main.py': rule 8 ('read', 'allow', '*')
== raw-demo-agent rules 54
   (same seven readings, rules 52, 52, 9, 9, 10, 11, 8)
```

So without a hostile rule the default `*.env` and `*.env.*` ask rules stay the last match for `.env` paths. The `tools` field of every raw file shows `read: true` (the `read` map does not hide the tool, as `disabled` predicts), `task: true` for both orchestrators and `task: false` for Demo Agent, Context Retriever and Tech Lead.

The PoC Orchestrator segment has no v2 counterpart; (a) compares it with its generated map: `"*": deny`, then 14 allows (Technology Scout through Frontend Developer, the source `agents:` order).

## 4. Differences from v2, attributed

| Agent | Difference | Cause |
|---|---|---|
| Orchestrator | 15 rules appended after `supabase_*: deny`: `task` `*` deny, then 14 named allows | T855 (SEC-T844-01), `permissionTaskAllowFromAgents` |
| PoC Orchestrator | not in v2; its last 15 rules are the same form with its own 14 agents | T855 (SEC-T844-01) |
| Demo Agent | 4 `read` deny rules appended after `task: deny` | T855 (SEC-T842-02), `permissionReadDenyUnlessGranted` |
| Context Retriever | the same 4 rules appended after `task: deny` | T855 (SEC-T842-02) |
| Tech Lead | none (holds `execute`, not `agent`) | control |
| all | rules 0-22 identical to v2; same binary | none |

QA Engineer was not re-run: it holds `execute` and not `agent`, and its generated file is unchanged by T855 (`git diff` empty).

## 5. Raw file hashes (sha256)

```
68583b8c224eaa8f2df968e51a928266aad571a4adddc94a715f61a3a33a163d  raw-context-retriever.json
1f92bb82a484311408c86146b7aad12e2af63c29b441c5e5881008a6bffdeca0  raw-demo-agent.json
347c3bbc6409a31c98e5dc6ec5258982d72496aafb4ada5007db02c91ccb46c3  raw-orchestrator.json
ed5e0f6e2361a59de3b5a78683402464f724abe40f3ece7fbc9f50004b71e909  raw-poc-orchestrator.json
8d9f5379ced29290091a77533e21932f21a4bd92ad7828cc4b153c7f707eb494  raw-tech-lead.json
433c0e9672cd7e3f223a3276500624075bc9e9254b1f25691738671461a5deb4  plain-raw-context-retriever.json
000383711bce5e293ca1003ed728942eb69e204c6b04dd12b1d6a16266a32317  plain-raw-demo-agent.json
99c37911271c30aa5fa5a18a2a319beb05fcd54fe7358e7af30cea6a4a430f07  slug-tech-lead.txt
```

## 6. Limits

- Rule lists only: no subagent was launched and no file was read (K-20).
- The `read` denies cover any directory named `gitlab-mcp`, so the default token directory. They do not cover a token file at another path, `grep`/`glob` on the directory (not path-scoped by `read`; only `external_directory` guards a path outside the project), or a link to the token inside the project (read under the link's own path).
- Built-in agents and agent files of your own still get no per-agent rule (K-23); the `task` map only stops the two orchestrators from launching them.
- The floor 1.0.224 is source-read, not run.
