# Artifact: mcp-agent-denials-evidence-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Task**: T663 (SEC-T663-07, SEC-T663-03). **Owner**: devops-engineer. **Date**: 2026-10-16.
- Based on: mcp-agent-denials-v1.md
- **What this is**: the raw output of the real Opencode binary's agent-resolution command, stored verbatim, plus an indexed reading of it. It shows which ordered permission rules Opencode builds for a generated agent file. **No tool call was made** (no model was available): the claim "the last matching rule wins" is source-read (`packages/core/src/permission.ts` `evaluate` = `findLast`; legacy `permission/index.ts`), and the evaluation lines below are my own last-match computation over the resolved lists, not Opencode output.
- **Version**: npm package `opencode-ai@1.19.2` (npm `latest` on 2026-10-16; `opencode --version` printed `1.19.2`), installed with `npm install opencode-ai@1.19.2` into an empty scratch directory (linux-x64 binary).
- **Environment**: `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME` and `XDG_STATE_HOME` pointed at empty scratch directories so that no user configuration was read; the working directory was a scratch project holding a copy of `implementation/.opencode/agents/` (unchanged, from the tree of the commit that exempts the read/search servers; refreshed after the user's exemption decision of 2026-10-16: the resolved lists no longer carry entries for brave, context7, hindsight, cwso, hf-mcp-server and toolradar) and one `.opencode/opencode.json`.
- **Raw files** (verbatim stdout of the command, unmodified; the `prompt` field is the agent body): `docs/artifacts/mcp-agent-denials-evidence-v1/raw-<name>.json`; sha256 below.

## 1. Commands

```
opencode debug agent "Tech Lead"      > raw-tech-lead.json
opencode debug agent "QA Engineer"    > raw-qa-engineer.json
opencode debug agent "Demo Agent"     > raw-demo-agent.json
opencode debug agent "Orchestrator"   > raw-orchestrator.json
```

The agent name is the frontmatter `name`. The scratch `.opencode/opencode.json` is the generated `implementation/.opencode/opencode.json` without its `mcp` and `instructions` keys (so no MCP server is started and nothing is fetched), with a **hostile global `permission`** written first, as an install merge would keep the user's keys first and the generated denies last:

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

Segments of every resolved list below: rules 0-11 are Opencode's built-in defaults, 12-22 the global config (the user's five rules, then the six generated server-level denies), 23 onwards the agent's own rules in the order of the generated file, and a final built-in `external_directory` rule.

## Tech Lead (non-holder of every server)

`raw-tech-lead.json`, sha256 `bef0feb6a2c3c1e9a2e55cac99b6d839b7d7ddac79bca14f416cfe86a4cbb559`, 46 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  <path>
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
 23  read  allow  *
 24  search  allow  *
 25  edit  allow  *
 26  execute  allow  *
 27  web  allow  *
 28  gitlab_*  deny  *
 29  playwright_*  deny  *
 30  playwright_browser_run_code_unsafe  deny  *
 31  playwright_browser_evaluate  deny  *
 32  playwright_browser_file_upload  deny  *
 33  playwright_browser_drag  deny  *
 34  playwright_browser_drop  deny  *
 35  playwright_browser_network_request  deny  *
 36  memory_*  deny  *
 37  sequential-thinking_*  deny  *
 38  context-retriever_*  deny  *
 39  security-audit_*  deny  *
 40  poc-security-audit_*  deny  *
 41  filesystem_*  deny  *
 42  github_*  deny  *
 43  git_*  deny  *
 44  supabase_*  deny  *
 45  external_directory  allow  <path>
```

Last-match evaluation over the list above (my computation, not Opencode output; `brave_*` is exempt from the per-agent deny and the hostile global config allows it, `hindsight_recall` is exempt and matches only the hostile config's `*: allow`; without a user `*` rule it would match no rule and depend on the default behaviour, ask in the current core): `gitlab_get_issue` deny, `gitlab_create_issue` deny, `gitlab_merge_merge_request` deny, `gitlab_push_files` deny, `gitlab_gitlab_api_request` deny, `gitlab_execute_graphql` deny, `brave_brave_web_search` allow, `hindsight_recall` allow, `filesystem_write_file` deny, `playwright_browser_click` deny, `playwright_browser_evaluate` deny, `playwright_browser_network_request` deny, `playwright_browser_network_requests` deny, `memory_create_entities` deny.

## QA Engineer (named-only holder of `gitlab` and `playwright`)

`raw-qa-engineer.json`, sha256 `923de985e6ddad5b326dfd082f0e3439907084eb00106490ec5dee2e486ecadb`, 84 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  <path>
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
 25  read  allow  *
 26  search  allow  *
 27  edit  allow  *
 28  execute  allow  *
 29  web  allow  *
 30  playwright_browser_navigate  allow  *
 31  playwright_browser_navigate_back  allow  *
 32  playwright_browser_snapshot  allow  *
 33  playwright_browser_find  allow  *
 34  playwright_browser_take_screenshot  allow  *
 35  playwright_browser_click  allow  *
 36  playwright_browser_type  allow  *
 37  playwright_browser_fill_form  allow  *
 38  playwright_browser_select_option  allow  *
 39  playwright_browser_press_key  allow  *
 40  playwright_browser_hover  allow  *
 41  playwright_browser_handle_dialog  allow  *
 42  playwright_browser_wait_for  allow  *
 43  playwright_browser_console_messages  allow  *
 44  playwright_browser_network_requests  allow  *
 45  playwright_browser_resize  allow  *
 46  playwright_browser_tabs  allow  *
 47  playwright_browser_close  allow  *
 48  gitlab_create_issue  allow  *
 49  gitlab_create_issue_note  allow  *
 50  gitlab_get_issue  allow  *
 51  gitlab_list_issues  allow  *
 52  gitlab_list_issue_discussions  allow  *
 53  gitlab_list_labels  allow  *
 54  gitlab_list_merge_requests  allow  *
 55  gitlab_get_merge_request  allow  *
 56  gitlab_list_merge_request_changed_files  allow  *
 57  gitlab_get_merge_request_file_diff  allow  *
 58  gitlab_mr_discussions  allow  *
 59  gitlab_list_merge_request_pipelines  allow  *
 60  gitlab_list_pipelines  allow  *
 61  gitlab_get_pipeline  allow  *
 62  gitlab_list_pipeline_jobs  allow  *
 63  gitlab_get_pipeline_job  allow  *
 64  gitlab_get_pipeline_job_output  allow  *
 65  gitlab_get_pipeline_test_report  allow  *
 66  gitlab_get_pipeline_test_report_summary  allow  *
 67  gitlab_discover_tools  allow  *
 68  playwright_browser_run_code_unsafe  deny  *
 69  playwright_browser_evaluate  deny  *
 70  playwright_browser_file_upload  deny  *
 71  playwright_browser_drag  deny  *
 72  playwright_browser_drop  deny  *
 73  playwright_browser_network_request  deny  *
 74  memory_*  deny  *
 75  sequential-thinking_*  deny  *
 76  context-retriever_*  deny  *
 77  security-audit_*  deny  *
 78  poc-security-audit_*  deny  *
 79  filesystem_*  deny  *
 80  github_*  deny  *
 81  git_*  deny  *
 82  supabase_*  deny  *
 83  external_directory  allow  <path>
```

Last-match evaluation over the list above (my computation, not Opencode output; `brave_*` is exempt from the per-agent deny and the hostile global config allows it, `hindsight_recall` is exempt and matches only the hostile config's `*: allow`; without a user `*` rule it would match no rule and depend on the default behaviour, ask in the current core): `gitlab_get_issue` allow, `gitlab_create_issue` allow, `gitlab_merge_merge_request` deny, `gitlab_push_files` deny, `gitlab_gitlab_api_request` deny, `gitlab_execute_graphql` deny, `brave_brave_web_search` allow, `hindsight_recall` allow, `filesystem_write_file` deny, `playwright_browser_click` allow, `playwright_browser_evaluate` deny, `playwright_browser_network_request` deny, `playwright_browser_network_requests` allow, `memory_create_entities` deny.

## Demo Agent (named-only holder of `playwright`; non-holder of the rest)

`raw-demo-agent.json`, sha256 `76863a8f2ad33efed98b9fc1cb97362e76e7c9ba108b738b8579261de70aaf49`, 57 rules.

```
idx  permission  action  pattern
  0  *  allow  *
  1  doom_loop  ask  *
  2  external_directory  ask  <path>
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
 24  read  allow  *
 25  search  allow  *
 26  edit  allow  *
 27  web  allow  *
 28  playwright_browser_navigate  allow  *
 29  playwright_browser_navigate_back  allow  *
 30  playwright_browser_snapshot  allow  *
 31  playwright_browser_take_screenshot  allow  *
 32  playwright_browser_click  allow  *
 33  playwright_browser_hover  allow  *
 34  playwright_browser_type  allow  *
 35  playwright_browser_fill_form  allow  *
 36  playwright_browser_press_key  allow  *
 37  playwright_browser_wait_for  allow  *
 38  playwright_browser_resize  allow  *
 39  playwright_browser_close  allow  *
 40  gitlab_*  deny  *
 41  playwright_browser_run_code_unsafe  deny  *
 42  playwright_browser_evaluate  deny  *
 43  playwright_browser_file_upload  deny  *
 44  playwright_browser_drag  deny  *
 45  playwright_browser_drop  deny  *
 46  playwright_browser_network_request  deny  *
 47  memory_*  deny  *
 48  sequential-thinking_*  deny  *
 49  context-retriever_*  deny  *
 50  security-audit_*  deny  *
 51  poc-security-audit_*  deny  *
 52  filesystem_*  deny  *
 53  github_*  deny  *
 54  git_*  deny  *
 55  supabase_*  deny  *
 56  external_directory  allow  <path>
```

Last-match evaluation over the list above (my computation, not Opencode output; `brave_*` is exempt from the per-agent deny and the hostile global config allows it, `hindsight_recall` is exempt and matches only the hostile config's `*: allow`; without a user `*` rule it would match no rule and depend on the default behaviour, ask in the current core): `gitlab_get_issue` deny, `gitlab_create_issue` deny, `gitlab_merge_merge_request` deny, `gitlab_push_files` deny, `gitlab_gitlab_api_request` deny, `gitlab_execute_graphql` deny, `brave_brave_web_search` allow, `hindsight_recall` allow, `filesystem_write_file` deny, `playwright_browser_click` allow, `playwright_browser_evaluate` deny, `playwright_browser_network_request` deny, `playwright_browser_network_requests` deny, `memory_create_entities` deny.

## SEC-T663-03: can a user keep a prompt on a held tool?

Question: the five whole-server GitLab holders carry `gitlab_*: true` in their own rules. Does a user's own `ask` (or `deny`) on `gitlab_merge_merge_request` survive? Three runs of `opencode debug agent "Orchestrator"` in the same scratch project (hostile global `gitlab_merge_merge_request: ask` as above):


| Run | sha256 (first 16) | Rules | GitLab rules (index, action) | Effective for `gitlab_merge_merge_request` (last match) |
|---|---|---|---|---|
| global config only (`raw-orchestrator.json`) | `7968b30aa7c55d69` | 48 | 13 `gitlab_*` allow; 16 `gitlab_merge_merge_request` ask; 30 `gitlab_*` allow | **allow** |
| plus `"agent": {"Orchestrator": {"permission": {"gitlab_merge_merge_request": "ask"}}}` in the project `.opencode/opencode.json` (`raw-orchestrator-with-user-agent-block.json`) | `28ade8d689c6788e` | 49 | 13 `gitlab_*` allow; 16 `gitlab_merge_merge_request` ask; 23 `gitlab_merge_merge_request` ask; 31 `gitlab_*` allow | **allow** |
| plus the environment variable `OPENCODE_CONFIG_CONTENT='{"agent":{"Orchestrator":{"permission":{"gitlab_merge_merge_request":"ask"}}}}'` (`raw-orchestrator-with-config-content.json`) | `3c242d2060fe6a83` | 49 | 13 `gitlab_*` allow; 16 `gitlab_merge_merge_request` ask; 30 `gitlab_*` allow; 47 `gitlab_merge_merge_request` ask | **ask** |

Reading: a user's global rule, and an `agent.<name>.permission` entry in the project config, both land BEFORE the agent file's `gitlab_*: allow` in the resolved list, so the allow wins and the `ask`/`deny` is silently overridden for the five whole-server holders. Only a source loaded after the agent files (here `OPENCODE_CONFIG_CONTENT`; by source reading also the managed configuration directory, not tested) appends its rule at the end and keeps the prompt. There is no supported way to keep a prompt through the files this repository generates or through the user's project or global configuration; it needs `OPENCODE_CONFIG_CONTENT` or a managed configuration. Observed in the resolved lists on `opencode-ai@1.19.2` only; the 2.x line was read in source, not run.

## Raw file hashes


- `raw-demo-agent.json`: `76863a8f2ad33efed98b9fc1cb97362e76e7c9ba108b738b8579261de70aaf49`
- `raw-orchestrator-with-config-content.json`: `3c242d2060fe6a83cba237bf49ee66969bf83dd8553249c9a2fb8883e00864b4`
- `raw-orchestrator-with-user-agent-block.json`: `28ade8d689c6788e054fd40826876d1782970065576aa4637e6c21ecdf1218a4`
- `raw-orchestrator.json`: `7968b30aa7c55d69918ccc1ec6b610e451f0fc1b0edaa6895b4876493636c767`
- `raw-qa-engineer.json`: `923de985e6ddad5b326dfd082f0e3439907084eb00106490ec5dee2e486ecadb`
- `raw-tech-lead.json`: `bef0feb6a2c3c1e9a2e55cac99b6d839b7d7ddac79bca14f416cfe86a4cbb559`
