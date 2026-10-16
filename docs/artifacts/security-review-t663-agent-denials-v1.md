# Artifact: security-review-t663-agent-denials-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell; the reviewer ran no test, no gate and no `opencode` binary; vendor sources were fetched through a summarising tool, not read verbatim; 9 of the 28 generated Opencode agent files were read). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-16.
- **Target**: T663, commits `3e7fd53` and `cb205e3` (reviewed), then `793cd60` (the review's conditions) and `6c271ed` (the user's decisions of 2026-10-16) on `agent/devops-engineer/T663` (from develop `6b0f8f2`): per-agent tool denies on Opencode.
- **Based on**: `docs/tasks/task-T663.md`, `docs/artifacts/mcp-agent-denials-v1.md`, `mcp-agent-denials-evidence-v1.md`, `mcp-server-denials-v1.md`, `security-review-t658-server-denials-v1.md`, `security-review-t657-tool-name-mapping-v1.md`.
- **Orchestrator checks**: the developer reports 1340 tests OK (skipped 23) and all gates after the last commit; the orchestrator re-ran the agent-denials, root-parity and package-pin tests (109 OK), `sync.mjs --check` (no drift across 584 files), confirmed the root drift baseline equals `--print-drift` (28 paths), and read the generated `tech-lead` and `orchestrator` files.

## Verdict: CONDITIONAL_PASS (conditions met in `793cd60` and `6c271ed`)

0 critical, 0 high, 1 medium (SEC-T663-01), 6 low at the review. No Immutable Security Constraint is breached; the change only adds denials. The mechanism does what is claimed per the vendor documentation, the vendor source and the resolved rule list recorded from `opencode-ai@1.19.2`: a non-holder cannot call any GitLab tool, a named holder (qa-engineer, scrum-master) can call only its named tools, no agent can call the six denied Playwright tools, and a user's own global allow does not override any of this. A refused tool call was not observed (no model in the environment).

## Findings and dispositions

| ID | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T663-01 | SECURITY:MEDIUM (SEC-T658-01 narrowed and carried) | Only `gitlab` carried the per-agent deny; `memory`, `sequential-thinking`, `security-audit`, `poc-security-audit`, `context-retriever`, `brave`, `context7`, `hindsight`, the extended servers and the Playwright tools an agent holds none of stayed callable by agents that do not hold them; the wiki list was incomplete; Opencode's built-in agents carry no deny | Fixed in `793cd60` (`denyUnlessGranted` on every server, holders pinned by tests, unknown keys rejected) and refined by the user's decision of 2026-10-16, "Exempt the read/search servers (Recommended)": brave, context7, hindsight, cwso, hf-mcp-server and toolradar carry `denyUnlessGranted: false`; the other 11 servers keep the per-agent deny. Built-in agents: the user decided "No, document the gap only (Recommended)": no global deny, the gap is documented and tracked |
| SEC-T663-02 | LOW | The mechanism rests on the legacy `tools:` frontmatter map, which the Opencode docs mark deprecated and for which they state no key order; the order is established by source and by the 1.19.2 resolver; the artifact said "verified (docs, ...)" | Wording corrected in `793cd60`; tracked debt: migrate to a frontmatter `permission:` block; add a release-checklist item (`opencode debug agent "Tech Lead"`) and a refused-call check to K-20 |
| SEC-T663-03 | LOW | The SEC-T657-04 override (the generated `x: true` entries override a user's own `ask`/`deny` for held tools) was not in either `AGENTS.md` and not pinned; no GitLab example, no workaround named | Fixed in `793cd60`: the sentence with the `gitlab_merge_merge_request` example is in both `AGENTS.md`, the wiki and PREREQUISITES and pinned by a test; the developer's resolver test shows no supported user-level way to keep a prompt (only `OPENCODE_CONFIG_CONTENT`, and the managed configuration by source reading) and the documents say so |
| SEC-T663-04 | LOW | User-facing documents omitted the `gitlab_*` over-match with a user server starting with `gitlab_`, saved "always" approvals, built-in agents, and said "Nothing unverified is shipped"; "Used by" rows listed servers no agent holds | Fixed in `793cd60` (sentences added, wording corrected, rows corrected) |
| SEC-T663-05 | LOW | Weak documentation assertions; regression-only absence tests; evaluation model default differed from the recorded behaviour; the model is the author's own | Fixed in `793cd60`: anchored to the T663 paragraph, marked regression-only, deny assertions run under both defaults, module docstring says the evaluation is a model |
| SEC-T663-06 | LOW | A misspelled flag key was silently ignored; manifests validated inside the write loop | Fixed in `793cd60`: unknown keys stop the run; all manifests validated before the first write (closes SEC-T658-07(b)) |
| SEC-T663-07 | LOW | The resolver evidence was prose with rule numbers; raw output not stored | Fixed in `793cd60` and refreshed in `6c271ed`: `docs/artifacts/mcp-agent-denials-evidence-v1.md` with six raw files and their sha256 values, checked by a test |

## Residuals (disclosed in the documents, tracked)

A later config source, a user-owned agent file in `.opencode/agents/` (replaced by `--update`, pre-existing), a plugin `permission.evaluate` hook (unverified) or a managed policy can override the generated rules; Opencode's built-in agents; the `tools:`-to-`permission:` migration; the 2.x runtime was read, not run; Gemini CLI is unchanged (every agent can still call every tool of every configured server, including the GitLab write tools); Pi is partly open; a user server whose cleaned name starts with a denied prefix is denied for non-holders. Non-holders lose the GitLab read tools on Opencode, which matches the other platforms (no non-holder role needs GitLab; confirmed for the 18 of 21 non-holders whose sources the reviewer read).

## Suggested release-note wording (reviewer; the shipped qualifiers are mandatory)

> On Opencode the generated agent files deny the six unsafe Playwright tools for every agent and deny the tools of the write-capable and project-reaching servers (`gitlab`, `playwright`, `memory`, `sequential-thinking`, `security-audit`, `poc-security-audit`, `context-retriever`, `filesystem`, `github`, `git`, `supabase`) for every agent that holds none of that server's tools; `qa-engineer` and `scrum-master` can call only their named GitLab tools. The search and memory servers (`brave`, `context7`, `hindsight`, `cwso`, `hf-mcp-server`, `toolradar`) are exempt. This follows the Opencode documentation and vendor source and the resolved rule list observed with `opencode-ai@1.19.2`; a refused tool call has not been observed. It uses the `tools` frontmatter map, which Opencode documents as deprecated. It does not cover an agent file or configuration source of your own that allows these names later, Opencode's built-in agents, or Gemini CLI, where every agent can still call every tool of every configured server. A global `ask` or `deny` you write for a tool an agent holds is overridden for that agent. This is a behaviour change for Opencode adopters.

## Limits

L-1 no shell (no test, gate or `opencode` run by the reviewer); L-2 the grep tool failed, so full reads were used, and not all 28 agent bodies and skills were searched for GitLab use; L-3 vendor files were fetched through a summarising tool, the 2.x core was read not run, `opencode-ai@1.19.2` was run by the developer only; L-4 nine of 28 generated files read; L-5 `root-install-drift.json` and the registry were not read; L-6 no held-out, `.env*` or credential file opened.
