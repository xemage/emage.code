# Artifact: mcp-agent-denials-evidence-v2.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T846 (plan-170, SEC-T837-01). **Owner**: devops-engineer. **Date**: 2026-11-19.
- Based on: mcp-agent-denials-evidence-v1.md, security-review-t837-opencode-permission-v1.md, plan-168-batch-j-opencode-permission.md (§ Outcome), and the generated `implementation/.opencode/agents/*.md` and `implementation/.opencode/opencode.json` at `f32100bc` (develop `c764005a` plus the plan-170 commit).
- **What this is**: the raw output of the real Opencode binary's agent-resolution command for the generated agent files in their current `permission:` form (T836, narrowed by T839, T841 and T843), stored verbatim, plus an indexed reading and a scripted comparison. It repeats the method of evidence v1. **No tool call was made** (no model, API key, login or MCP server was used), so a refused tool call is still **not observed (unverified, K-20)**. The last-match readings below are my own computation over the resolved lists, not Opencode output; that Opencode evaluates by last match is source-read (evidence v1, Metadata), not observed here.
- **Version**: npm package `opencode-ai@1.19.2`, installed with `npm install opencode-ai@1.19.2` into an empty scratch directory. npm did not run the package's `postinstall` script (npm `allow-scripts` policy); `node_modules/.bin/opencode` links to `opencode-ai/bin/opencode.exe`, an x86-64 ELF binary byte-identical to `opencode-linux-x64/bin/opencode` (sha256 `8d6e8464a306e14429bad028cb06d05cd8aacd75c1bc811b3b816dc64d509122`). `opencode --version` printed `1.19.2`. The binary at `~/.opencode/bin` (1.18.31) was not used.
- **Environment**: every `opencode` command ran under `env -i` with only `PATH=/usr/bin:/bin` and `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `XDG_STATE_HOME`, each an empty scratch directory. No other variable was passed (no token path, API key, `OPENCODE_*` variable or user configuration). The working directory was a scratch project holding an unchanged copy of `implementation/.opencode/agents/` (28 files) and one `.opencode/opencode.json` (below). Nothing was written to stderr; every command exited 0.
- **Raw files** (verbatim stdout, unmodified; the `prompt` field is the agent body; the `external_directory` patterns contain the scratch paths of this run): `docs/artifacts/mcp-agent-denials-evidence-v2/raw-<name>.json`; sha256 at the end.

## 1. Commands

```
opencode --version                         # 1.19.2
opencode debug agent "Tech Lead"         > raw-tech-lead.json
opencode debug agent "QA Engineer"       > raw-qa-engineer.json
opencode debug agent "Demo Agent"        > raw-demo-agent.json
opencode debug agent "Orchestrator"      > raw-orchestrator.json
opencode debug agent "Context Retriever" > raw-context-retriever.json
```

The scratch `.opencode/opencode.json` is the generated `implementation/.opencode/opencode.json` without its `mcp` and `instructions` keys (so no MCP server is started and nothing is fetched), with the same **hostile global `permission`** as v1 written first; the generated six server-level denies follow (they already appear in the hostile block, so the object keeps them in that position, as in v1):

```
"permission": {
  "*": "allow",
  "gitlab_*": "allow",
  "brave_*": "allow",
  "playwright_browser_click": "deny",
  "gitlab_merge_merge_request": "ask",
  "playwright_browser_run_code_unsafe": "deny", "playwright_browser_evaluate": "deny",
  "playwright_browser_file_upload": "deny", "playwright_browser_drag": "deny",
  "playwright_browser_drop": "deny", "playwright_browser_network_request": "deny"
}
```

Segments of every resolved list, as in v1: rules 0-11 are Opencode's built-in defaults, 12-22 the global config (the user's five rules, then the six generated server-level denies), 23 up to the last-but-one rule the agent's own rules in the order of the generated file, and a final built-in `external_directory` allow. Machine-specific `external_directory` paths are shown as `<path>`.

## 2. Scripted comparison

Script `compare.py` (scratch; run with `python3 -I compare.py <worktree> <scratch>`), faithful summary:

- Reads each raw file's `permission` array as `(permission, action, pattern)` tuples and replaces non-`*` `external_directory` patterns with `<path>`.
- Parses the generated agent file's frontmatter `permission:` block into ordered `(name, action)` pairs.
- **(a)** Agent segment = rules `[23 : -1]`. PASS when its `(permission, action)` sequence equals the generated map exactly (same names, actions, order) and every pattern is `*`; also checks that the final rule is `external_directory allow <path>`.
- **(b)** For the four v1 agents, `difflib.SequenceMatcher` over the `(permission, action)` sequences of the v1 agent segment and the v2 agent segment; every non-equal opcode is printed.
- **(c)** For the four v1 agents, rules 0-22 and the final rule must be identical to v1 (after the `<path>` normalisation).

Result (verbatim script output, hashes omitted):

```
== tech-lead: rules=42 agent_segment=18 generated=18 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 + final rule identical to v1: True
   (b) delete: v1[0:2]=[('read', 'allow'), ('search', 'allow')] -> v2[0:0]=[]
   (b) delete: v1[3:5]=[('execute', 'allow'), ('web', 'allow')] -> v2[1:1]=[]
   (b) delete: v1[19:20]=[('github_*', 'deny')] -> v2[15:15]=[]
   (b) insert: v1[22:22]=[] -> v2[17:18]=[('task', 'deny')]
== qa-engineer: rules=79 agent_segment=55 generated=55 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 + final rule identical to v1: True
   (b) delete: v1[2:4]=[('read', 'allow'), ('search', 'allow')] -> v2[2:2]=[]
   (b) delete: v1[5:7]=[('execute', 'allow'), ('web', 'allow')] -> v2[3:3]=[]
   (b) delete: v1[41:42]=[('gitlab_get_pipeline_job_output', 'allow')] -> v2[37:37]=[]
   (b) delete: v1[57:58]=[('github_*', 'deny')] -> v2[52:52]=[]
   (b) insert: v1[60:60]=[] -> v2[54:55]=[('task', 'deny')]
== demo-agent: rules=55 agent_segment=31 generated=31 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 + final rule identical to v1: True
   (b) delete: v1[1:3]=[('read', 'allow'), ('search', 'allow')] -> v2[1:1]=[]
   (b) delete: v1[4:5]=[('web', 'allow')] -> v2[2:2]=[]
   (b) delete: v1[30:31]=[('github_*', 'deny')] -> v2[27:27]=[]
   (b) insert: v1[33:33]=[] -> v2[29:31]=[('bash', 'deny'), ('task', 'deny')]
== orchestrator: rules=57 agent_segment=33 generated=33 (a)=PASS final_rule_external_directory=True
   (c) built-in 0-11 + global 12-22 + final rule identical to v1: True
   (b) replace: v1[0:2]=[('read', 'allow'), ('search', 'allow')] -> v2[0:1]=[('gitlab_*', 'deny')]
   (b) replace: v1[3:8]=[('execute', 'allow'), ('agent', 'allow'), ('web', 'allow'), ('todo', 'allow'), ('gitlab_*', 'allow')] -> v2[2:18]=[('gitlab_get_issue', 'allow'), ('gitlab_list_issues', 'allow'), ('gitlab_list_issue_discussions', 'allow'), ('gitlab_create_merge_request', 'allow'), ('gitlab_get_merge_request', 'allow'), ('gitlab_list_merge_requests', 'allow'), ('gitlab_get_merge_request_approval_state', 'allow'), ('gitlab_list_merge_request_changed_files', 'allow'), ('gitlab_mr_discussions', 'allow'), ('gitlab_list_merge_request_pipelines', 'allow'), ('gitlab_list_pipelines', 'allow'), ('gitlab_get_pipeline', 'allow'), ('gitlab_list_pipeline_jobs', 'allow'), ('gitlab_get_branch', 'allow'), ('gitlab_list_branches', 'allow'), ('gitlab_discover_tools', 'allow')]
   (b) delete: v1[21:22]=[('github_*', 'deny')] -> v2[31:31]=[]
== context-retriever: rules=46 agent_segment=22 generated=22 (a)=PASS final_rule_external_directory=True
OVERALL PASS
```

**Result: OVERALL PASS.** (a) passes for all five agents: each resolved agent segment equals the agent's generated `permission:` map, entry for entry, in order, with no entry missing, added, reordered or ignored, and no parse error. (c) passes for the four v1 agents: the built-in segment (0-11), the global segment (12-22) and the final `external_directory` rule are unchanged from v1. The agent segment therefore starts at index 23 in v1 and v2 alike.

## 3. Attribution of every difference from v1

v1 was taken on 2026-10-16 (T663). Between v1 and this run, more tasks than T836, T839, T841 and T843 changed the generated agent files on purpose. Every (b) difference is attributed below, by the commit that changed the generated file (`git log -S` on `implementation/.opencode/agents/`):

| Agent | Difference (v1 → v2) | Cause |
|---|---|---|
| all four | `read allow`, `search allow` removed | T839 (`read` no longer written; `search` an inert name) |
| Tech Lead, QA Engineer, Orchestrator | `execute allow` removed | T839 (inert name; these agents hold `execute`, so no `bash` deny is written and Opencode's default applies) |
| all four | `web allow` removed | T839 (inert name; these agents hold `web`, so no `webfetch`/`websearch` deny is written) |
| Orchestrator | `agent allow`, `todo allow` removed | T839 (inert names) |
| all four | `github_*: deny` removed | **T676** (commit `44c15b49`, the `github` MCP server removed from the server set), not one of T836/T839/T841/T843 |
| QA Engineer | `gitlab_get_pipeline_job_output allow` removed | **T688** (commit `d89f75f2`, SEC-T660-02: raw CI job traces dropped from qa-engineer), not one of T836/T839/T841/T843 |
| Orchestrator | `gitlab_*: allow` replaced by `gitlab_*: deny` first, then 16 named `gitlab_*` allows (`gitlab_get_issue` … `gitlab_discover_tools`) | **T666** (commit `58149964`, named GitLab tools for the orchestrators), not one of T836/T839/T841/T843 |
| Demo Agent | `bash deny` added (before `task`) | T841 (deny-only `bash` for an agent without `execute`) |
| Tech Lead, QA Engineer, Demo Agent | `task deny` added (last entry) | T843 (deny-only `task` for every agent except the two orchestrators) |
| Orchestrator | no `task` entry | T843 (the two orchestrators are exempt) |
| all four | the remaining entries keep their names, actions and relative order; the key `tools:` became `permission:` | T836 (form change; same names, same order) |

Context Retriever was not in v1; its segment (22 entries) ends with the five deny-only entries `bash`, `edit`, `webfetch`, `websearch` (T841) and `task` (T843), and (a) passes for it.

**Unexpected relative to the brief:** three differences come from T666, T676 and T688, which landed after v1 and before T836. They are intended changes, already shipped, and not a defect of the `permission:` form; v1 simply predates them.

## 4. Resolved lists and last-match readings

The last-match lines are **my computation, not Opencode output**: a rule matches when its permission wildcard (`*` = any characters) matches the name and its pattern is `*`; the result is the action of the last matching rule (index in brackets). `read` is not computed (its built-in `*.env` rules depend on the path). Note that rule 0, a built-in `*: allow`, matches every name, so a name that no later rule matches resolves to allow even without the hostile `*: allow` at 12 (my reading of the list; how Opencode treats a name with no rule beyond the list is not observed).

### Tech Lead (non-holder of every non-exempt server; holds `execute`, `edit`, `web`)

`raw-tech-lead.json`, sha256 `c687cc4cfeb271a11cbb286a2a46de03687d205a1c6c07e9eaf932147bb75952`, 42 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  *
  3  external_directory  allow  <path>
  4  external_directory  allow  <path>
  5  question  deny  *
  6  plan_enter  deny  *
  7  plan_exit  deny  *
  8  read  allow  *
  9  read  ask  *.env
 10  read  ask  *.env.*
 11  read  allow  *.env.example
 12  *  allow  *
 13  gitlab_*  allow  *
 14  brave_*  allow  *
 15  playwright_browser_click  deny  *
 16  gitlab_merge_merge_request  ask  *
 17  playwright_browser_run_code_unsafe  deny  *
 18  playwright_browser_evaluate  deny  *
 19  playwright_browser_file_upload  deny  *
 20  playwright_browser_drag  deny  *
 21  playwright_browser_drop  deny  *
 22  playwright_browser_network_request  deny  *
 23  edit  allow  *
 24  gitlab_*  deny  *
 25  playwright_*  deny  *
 26  playwright_browser_run_code_unsafe  deny  *
 27  playwright_browser_evaluate  deny  *
 28  playwright_browser_file_upload  deny  *
 29  playwright_browser_drag  deny  *
 30  playwright_browser_drop  deny  *
 31  playwright_browser_network_request  deny  *
 32  memory_*  deny  *
 33  sequential-thinking_*  deny  *
 34  context-retriever_*  deny  *
 35  security-audit_*  deny  *
 36  poc-security-audit_*  deny  *
 37  filesystem_*  deny  *
 38  git_*  deny  *
 39  supabase_*  deny  *
 40  task  deny  *
 41  external_directory  allow  <path>
```

Last-match reading (my computation, not Opencode output): `bash` allow (#12), `edit` allow (#23), `webfetch` allow (#12), `websearch` allow (#12), `task` deny (#40), `gitlab_get_issue` deny (#24), `gitlab_create_merge_request` deny (#24), `gitlab_merge_merge_request` deny (#24), `gitlab_push_files` deny (#24), `playwright_browser_click` deny (#25), `playwright_browser_evaluate` deny (#27), `memory_create_entities` deny (#32), `brave_brave_web_search` allow (#14), `context-retriever_retrieve` deny (#34).

### QA Engineer (named-only holder of `gitlab` and `playwright`)

`raw-qa-engineer.json`, sha256 `d9e6833200397c2faceed9d3c1ee6eba3bf3f19b8d5309c4e23f9f5e142b0b04`, 79 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  *
  3  external_directory  allow  <path>
  4  external_directory  allow  <path>
  5  question  deny  *
  6  plan_enter  deny  *
  7  plan_exit  deny  *
  8  read  allow  *
  9  read  ask  *.env
 10  read  ask  *.env.*
 11  read  allow  *.env.example
 12  *  allow  *
 13  gitlab_*  allow  *
 14  brave_*  allow  *
 15  playwright_browser_click  deny  *
 16  gitlab_merge_merge_request  ask  *
 17  playwright_browser_run_code_unsafe  deny  *
 18  playwright_browser_evaluate  deny  *
 19  playwright_browser_file_upload  deny  *
 20  playwright_browser_drag  deny  *
 21  playwright_browser_drop  deny  *
 22  playwright_browser_network_request  deny  *
 23  gitlab_*  deny  *
 24  playwright_*  deny  *
 25  edit  allow  *
 26  playwright_browser_navigate  allow  *
 27  playwright_browser_navigate_back  allow  *
 28  playwright_browser_snapshot  allow  *
 29  playwright_browser_find  allow  *
 30  playwright_browser_take_screenshot  allow  *
 31  playwright_browser_click  allow  *
 32  playwright_browser_type  allow  *
 33  playwright_browser_fill_form  allow  *
 34  playwright_browser_select_option  allow  *
 35  playwright_browser_press_key  allow  *
 36  playwright_browser_hover  allow  *
 37  playwright_browser_handle_dialog  allow  *
 38  playwright_browser_wait_for  allow  *
 39  playwright_browser_console_messages  allow  *
 40  playwright_browser_network_requests  allow  *
 41  playwright_browser_resize  allow  *
 42  playwright_browser_tabs  allow  *
 43  playwright_browser_close  allow  *
 44  gitlab_create_issue  allow  *
 45  gitlab_create_issue_note  allow  *
 46  gitlab_get_issue  allow  *
 47  gitlab_list_issues  allow  *
 48  gitlab_list_issue_discussions  allow  *
 49  gitlab_list_labels  allow  *
 50  gitlab_list_merge_requests  allow  *
 51  gitlab_get_merge_request  allow  *
 52  gitlab_list_merge_request_changed_files  allow  *
 53  gitlab_get_merge_request_file_diff  allow  *
 54  gitlab_mr_discussions  allow  *
 55  gitlab_list_merge_request_pipelines  allow  *
 56  gitlab_list_pipelines  allow  *
 57  gitlab_get_pipeline  allow  *
 58  gitlab_list_pipeline_jobs  allow  *
 59  gitlab_get_pipeline_job  allow  *
 60  gitlab_get_pipeline_test_report  allow  *
 61  gitlab_get_pipeline_test_report_summary  allow  *
 62  gitlab_discover_tools  allow  *
 63  playwright_browser_run_code_unsafe  deny  *
 64  playwright_browser_evaluate  deny  *
 65  playwright_browser_file_upload  deny  *
 66  playwright_browser_drag  deny  *
 67  playwright_browser_drop  deny  *
 68  playwright_browser_network_request  deny  *
 69  memory_*  deny  *
 70  sequential-thinking_*  deny  *
 71  context-retriever_*  deny  *
 72  security-audit_*  deny  *
 73  poc-security-audit_*  deny  *
 74  filesystem_*  deny  *
 75  git_*  deny  *
 76  supabase_*  deny  *
 77  task  deny  *
 78  external_directory  allow  <path>
```

Last-match reading (my computation, not Opencode output): `bash` allow (#12), `edit` allow (#25), `webfetch` allow (#12), `websearch` allow (#12), `task` deny (#77), `gitlab_get_issue` allow (#46), `gitlab_create_merge_request` deny (#23), `gitlab_merge_merge_request` deny (#23), `gitlab_push_files` deny (#23), `playwright_browser_click` allow (#31), `playwright_browser_evaluate` deny (#64), `memory_create_entities` deny (#69), `brave_brave_web_search` allow (#14), `context-retriever_retrieve` deny (#71).

### Demo Agent (named-only holder of `playwright`; no `execute`)

`raw-demo-agent.json`, sha256 `0526702fb3bbf0eb26423c75375dabd62ba908136362f9d7d29adb92265ddb21`, 55 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  *
  3  external_directory  allow  <path>
  4  external_directory  allow  <path>
  5  question  deny  *
  6  plan_enter  deny  *
  7  plan_exit  deny  *
  8  read  allow  *
  9  read  ask  *.env
 10  read  ask  *.env.*
 11  read  allow  *.env.example
 12  *  allow  *
 13  gitlab_*  allow  *
 14  brave_*  allow  *
 15  playwright_browser_click  deny  *
 16  gitlab_merge_merge_request  ask  *
 17  playwright_browser_run_code_unsafe  deny  *
 18  playwright_browser_evaluate  deny  *
 19  playwright_browser_file_upload  deny  *
 20  playwright_browser_drag  deny  *
 21  playwright_browser_drop  deny  *
 22  playwright_browser_network_request  deny  *
 23  playwright_*  deny  *
 24  edit  allow  *
 25  playwright_browser_navigate  allow  *
 26  playwright_browser_navigate_back  allow  *
 27  playwright_browser_snapshot  allow  *
 28  playwright_browser_take_screenshot  allow  *
 29  playwright_browser_click  allow  *
 30  playwright_browser_hover  allow  *
 31  playwright_browser_type  allow  *
 32  playwright_browser_fill_form  allow  *
 33  playwright_browser_press_key  allow  *
 34  playwright_browser_wait_for  allow  *
 35  playwright_browser_resize  allow  *
 36  playwright_browser_close  allow  *
 37  gitlab_*  deny  *
 38  playwright_browser_run_code_unsafe  deny  *
 39  playwright_browser_evaluate  deny  *
 40  playwright_browser_file_upload  deny  *
 41  playwright_browser_drag  deny  *
 42  playwright_browser_drop  deny  *
 43  playwright_browser_network_request  deny  *
 44  memory_*  deny  *
 45  sequential-thinking_*  deny  *
 46  context-retriever_*  deny  *
 47  security-audit_*  deny  *
 48  poc-security-audit_*  deny  *
 49  filesystem_*  deny  *
 50  git_*  deny  *
 51  supabase_*  deny  *
 52  bash  deny  *
 53  task  deny  *
 54  external_directory  allow  <path>
```

Last-match reading (my computation, not Opencode output): `bash` deny (#52), `edit` allow (#24), `webfetch` allow (#12), `websearch` allow (#12), `task` deny (#53), `gitlab_get_issue` deny (#37), `gitlab_create_merge_request` deny (#37), `gitlab_merge_merge_request` deny (#37), `gitlab_push_files` deny (#37), `playwright_browser_click` allow (#29), `playwright_browser_evaluate` deny (#39), `memory_create_entities` deny (#44), `brave_brave_web_search` allow (#14), `context-retriever_retrieve` deny (#46).

### Orchestrator (named-only holder of `gitlab`; holder of `memory` and `sequential-thinking`; exempt from the `task` deny)

`raw-orchestrator.json`, sha256 `9ce28b76cd43d6bc9b2e151c6ff5ecd0aa0921571616dab7a1df6db8e5ed3e6a`, 57 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  *
  3  external_directory  allow  <path>
  4  external_directory  allow  <path>
  5  question  deny  *
  6  plan_enter  deny  *
  7  plan_exit  deny  *
  8  read  allow  *
  9  read  ask  *.env
 10  read  ask  *.env.*
 11  read  allow  *.env.example
 12  *  allow  *
 13  gitlab_*  allow  *
 14  brave_*  allow  *
 15  playwright_browser_click  deny  *
 16  gitlab_merge_merge_request  ask  *
 17  playwright_browser_run_code_unsafe  deny  *
 18  playwright_browser_evaluate  deny  *
 19  playwright_browser_file_upload  deny  *
 20  playwright_browser_drag  deny  *
 21  playwright_browser_drop  deny  *
 22  playwright_browser_network_request  deny  *
 23  gitlab_*  deny  *
 24  edit  allow  *
 25  gitlab_get_issue  allow  *
 26  gitlab_list_issues  allow  *
 27  gitlab_list_issue_discussions  allow  *
 28  gitlab_create_merge_request  allow  *
 29  gitlab_get_merge_request  allow  *
 30  gitlab_list_merge_requests  allow  *
 31  gitlab_get_merge_request_approval_state  allow  *
 32  gitlab_list_merge_request_changed_files  allow  *
 33  gitlab_mr_discussions  allow  *
 34  gitlab_list_merge_request_pipelines  allow  *
 35  gitlab_list_pipelines  allow  *
 36  gitlab_get_pipeline  allow  *
 37  gitlab_list_pipeline_jobs  allow  *
 38  gitlab_get_branch  allow  *
 39  gitlab_list_branches  allow  *
 40  gitlab_discover_tools  allow  *
 41  memory_*  allow  *
 42  sequential-thinking_*  allow  *
 43  playwright_*  deny  *
 44  playwright_browser_run_code_unsafe  deny  *
 45  playwright_browser_evaluate  deny  *
 46  playwright_browser_file_upload  deny  *
 47  playwright_browser_drag  deny  *
 48  playwright_browser_drop  deny  *
 49  playwright_browser_network_request  deny  *
 50  context-retriever_*  deny  *
 51  security-audit_*  deny  *
 52  poc-security-audit_*  deny  *
 53  filesystem_*  deny  *
 54  git_*  deny  *
 55  supabase_*  deny  *
 56  external_directory  allow  <path>
```

Last-match reading (my computation, not Opencode output): `bash` allow (#12), `edit` allow (#24), `webfetch` allow (#12), `websearch` allow (#12), `task` allow (#12), `gitlab_get_issue` allow (#25), `gitlab_create_merge_request` allow (#28), `gitlab_merge_merge_request` deny (#23), `gitlab_push_files` deny (#23), `playwright_browser_click` deny (#43), `playwright_browser_evaluate` deny (#45), `memory_create_entities` allow (#41), `brave_brave_web_search` allow (#14), `context-retriever_retrieve` deny (#50).

### Context Retriever (holder of `context-retriever`; no `execute`, `edit`, `web` or delegation)

`raw-context-retriever.json`, sha256 `73666d7d19a333f98853cd3aa4841c2c204e56ee47fbfcfcc5c73d8627e84a15`, 46 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  *
  3  external_directory  allow  <path>
  4  external_directory  allow  <path>
  5  question  deny  *
  6  plan_enter  deny  *
  7  plan_exit  deny  *
  8  read  allow  *
  9  read  ask  *.env
 10  read  ask  *.env.*
 11  read  allow  *.env.example
 12  *  allow  *
 13  gitlab_*  allow  *
 14  brave_*  allow  *
 15  playwright_browser_click  deny  *
 16  gitlab_merge_merge_request  ask  *
 17  playwright_browser_run_code_unsafe  deny  *
 18  playwright_browser_evaluate  deny  *
 19  playwright_browser_file_upload  deny  *
 20  playwright_browser_drag  deny  *
 21  playwright_browser_drop  deny  *
 22  playwright_browser_network_request  deny  *
 23  context-retriever_*  deny  *
 24  context-retriever_retrieve  allow  *
 25  gitlab_*  deny  *
 26  playwright_*  deny  *
 27  playwright_browser_run_code_unsafe  deny  *
 28  playwright_browser_evaluate  deny  *
 29  playwright_browser_file_upload  deny  *
 30  playwright_browser_drag  deny  *
 31  playwright_browser_drop  deny  *
 32  playwright_browser_network_request  deny  *
 33  memory_*  deny  *
 34  sequential-thinking_*  deny  *
 35  security-audit_*  deny  *
 36  poc-security-audit_*  deny  *
 37  filesystem_*  deny  *
 38  git_*  deny  *
 39  supabase_*  deny  *
 40  bash  deny  *
 41  edit  deny  *
 42  webfetch  deny  *
 43  websearch  deny  *
 44  task  deny  *
 45  external_directory  allow  <path>
```

Last-match reading (my computation, not Opencode output): `bash` deny (#40), `edit` deny (#41), `webfetch` deny (#42), `websearch` deny (#43), `task` deny (#44), `gitlab_get_issue` deny (#25), `gitlab_create_merge_request` deny (#25), `gitlab_merge_merge_request` deny (#25), `gitlab_push_files` deny (#25), `playwright_browser_click` deny (#26), `playwright_browser_evaluate` deny (#28), `memory_create_entities` deny (#33), `brave_brave_web_search` allow (#14), `context-retriever_retrieve` allow (#24).

Reading of these lines (my computation): every agent's `gitlab_merge_merge_request` resolves to deny through its own `gitlab_*: deny`, which overrides the hostile global `gitlab_*: allow` (13) and `gitlab_merge_merge_request: ask` (16); the Orchestrator's named GitLab tools resolve to allow. `bash` resolves to deny only where T841 wrote it (Demo Agent, Context Retriever); for the holders it falls through to `*: allow`. `task` resolves to deny for every agent here except the Orchestrator. The exempt server `brave` resolves to allow everywhere through the hostile `brave_*: allow` (14).

## 5. Not observed (unverified)

- A refused tool call: no model was run, so no tool call was attempted (K-20).
- That the runtime applies these lists by last match: source-read only.
- How Opencode maps the `edit`, `bash`, `webfetch`, `websearch` and `task` permission names onto its built-in tools at call time.
- Opencode 2.x: not run.
- The SEC-T663-03 runs of v1 (`agent.<name>.permission`, `OPENCODE_CONFIG_CONTENT`) were not repeated.

## Raw file hashes

- `raw-context-retriever.json`: `73666d7d19a333f98853cd3aa4841c2c204e56ee47fbfcfcc5c73d8627e84a15`
- `raw-demo-agent.json`: `0526702fb3bbf0eb26423c75375dabd62ba908136362f9d7d29adb92265ddb21`
- `raw-orchestrator.json`: `9ce28b76cd43d6bc9b2e151c6ff5ecd0aa0921571616dab7a1df6db8e5ed3e6a`
- `raw-qa-engineer.json`: `d9e6833200397c2faceed9d3c1ee6eba3bf3f19b8d5309c4e23f9f5e142b0b04`
- `raw-tech-lead.json`: `c687cc4cfeb271a11cbb286a2a46de03687d205a1c6c07e9eaf932147bb75952`
