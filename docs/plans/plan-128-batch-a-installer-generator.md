# plan-128 — LOW batch A: installer and generator

**Created:** 2026-11-02
**Based on:** `docs/artifacts/tracked-debt-register-v4.md` § 5 (batch A, 15 ids); registers v1 to v3 for the descriptions; `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; the user's answer of 2026-11-02, verbatim: "A go".
**Scopes:** `T722`, `T723`, `T724`, `T725`.

## Goal

Close the LOW items in the generator (`implementation/scripts/sync.mjs`), the installer (`scripts/install.sh`), `merge-task-docs.py` and `merge-mcp-json.py`. Also implement the `audience:` command field, which is declared but implemented nowhere (TD-T671-P5).

## Task Decomposition

1. **T722** (devops-engineer): generator and MCP server definitions.
   - **SEC-T684-01**: `physicalFolded` in `sync.mjs` (around line 944) follows a dangling link with a lexical `dirname`. Fix: `path.resolve(await fs.realpath(path.dirname(current)), link)`, with a test.
   - **SEC-T684-02**: `mcp.outputFile` is guarded only by a deny-list of inputs. Allow it only under the manifest's own `outputDir`, plus the two exact exceptions, with a test.
   - **SEV-T690-01**: `agentMcpDenials` selects servers by tags only and ignores `extraPlatforms`. Honour `extraPlatforms`, with a test.
   - **SEV-T690-05**: in the T690 tests, mutation M11 is killed only by an input the regex refuses first, and the assertions are superset-only. Add a direct kill and exact assertions.
   - **SEV-T690-06**: the Copilot agents list `context-retriever/retrieve`, but that extended server is not generated into `.vscode/mcp.json`. Drop the tool from the Copilot render, which is fail-closed and the smallest surface. Remove the exception pinned in `test_mcp_tool_name_mapping.py`.
   - **SEC-T663-02**: `implementation/.opencode/agents/*.md` use a `tools:` map and have no `permission:` block. Check the current Opencode agent schema with ctx7 or the vendor documentation. If `tools` is deprecated, or `permission` is the documented control, generate the denials in the documented form. If the current form is still documented and enforced, report that with the source.
   - **TD-T671-K5**: `implementation/knowledge/mcp/servers.yaml:201` hard-codes the `context-retriever` index directory as `em-age-emage.code` for every project. Derive it from the project, or, if the server's index layout requires a fixed name, document it in the setup text (`implementation/PREREQUISITES.md` or `docs/wiki/mcp-servers.md`) and report why.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. Projection changes are declared as root drift, with no root refresh. All gates and the suite pass.
2. **T723** (devops-engineer): the installer and `merge-task-docs.py`.
   - **SEC-T684-03**: `install.sh:279-281`, `printable`, depends on the locale; U+202E passes `[:print:]`. Fix: `printable() { ascii_printable "$1"; }`, with a test.
   - **SEC-T684-04**: `_atomic_write_bytes` in `merge-task-docs.py` does not `fsync` the temp file or the directory. Add both.
   - **SEC-T684-05**: in `merge-task-docs.py`, seeds published with `os.replace` can overwrite a file created between planning and writing, and `dest_dir.mkdir` runs before the dry-run guard. Use `os.link` or an exclusive create, and move the `mkdir` after the guard, with tests.
   - **SEC-T684-06**: tests. T04j is not strictly equivalent; there is no non-UTF-8 name test; bash 3.2 `%q` is unverified; one mode assertion cannot fail. Add the 41-link test and a non-UTF-8 name test, and use a ledger mode other than 0600.
   - **SEC-T677-03**: `install.sh` `usage` is allowlisted as "no logic" in the function-size guard but holds one command substitution. Remove the substitution, or correct the allowlist reason.
   - **TL-T708-03**: `install.sh:1300` puts two cases in one sentence, and a test pins it. Split the sentence and update the pin. T715 also checks this line for release-document pointers (SEC-T715-02), so keep a parsed `docs/releases/vX.Y.Z.md` path form, and run `verify-release-docs.py --tag v9.0.0`.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. All gates and the suite pass.
3. **T724** (backend-developer), **QA-T707-01**: `scripts/merge-mcp-json.py:112-128` prints a false "differs from the generated entry" note for an Opencode `{env:NAME}` value. Compare the Opencode form correctly, with a test. *Acceptance:* no false note for an equal entry, and a true note still printed for a real difference.
4. **T725** (devops-engineer), **TD-T671-P5**: implement `audience:` for commands. Today one command, `/prepare-release`, declares `audience: authoring`; 18 declare `both`. A target project should not receive an authoring-only command.
   - Design the filter first, and state it in the closing report. Where does it apply: the generator, the installer, or both? How is an authoring checkout recognised? The existing test `tests/functional/test_command_audience_paths.py` and the `/discover-skills` rule already use the presence of the registry file. What happens to an existing installed copy on `--update`? What happens in the root install of this repository, which is an authoring checkout?
   - Implement it with tests, and record the user-visible change (targets no longer receive `/prepare-release`) as a migration item for the next release document. Depends on T723, because both change `install.sh`.
   - *Acceptance:* a target install has no authoring-only command on any platform; the root install keeps it; `--update` removes a stale copy (or the report says why not); all gates and the suite pass.

T722, T723 and T724 run in parallel; they share no file. T725 starts after T723 is merged into the plan branch. A Security Engineer reviews T722 to T725 together.

## User decisions

- **Root refresh:** T722 changes `servers.yaml` and the Opencode and Copilot renders, and T725 may change installed commands. The root install is refreshed only with the user's explicit approval.

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file. Never print a secret value.
- Declare root drift in `tests/_baselines/root-install-drift.json`. Do not refresh the root install.

## Outcome (2026-11-02)

- **Tasks.** T722 to T725 are done. Of the 15 batch-A ids, 14 are closed. SEC-T663-02 is not done. The Opencode documentation (ctx7 `/websites/opencode_ai`; opencode.ai/docs/agents and /docs/permissions) now calls the agent `tools` map deprecated and prefers `permission`. Moving to it changes five test files, several documents and the recorded live evidence, so it stays tracked-LOW and needs its own task.
- **Security review.** `docs/artifacts/security-review-t722-t725-batch-a-v1.md` gives PASS: no MEDIUM or higher. Nine LOW findings are tracked: SEC-T722-01 to -05, SEC-T724-01, and SEC-T725-01 to -03.
- **New tracked LOW from the task reports:**
  - **TD-T725-01.** Knowledge text that ships to targets still names `/prepare-release`: `commands/validate-tasks.md`, `commands/validate-workflow.md`, `skills/testing-strategy/SKILL.md` and `skills/release-workflow/SKILL.md`.
  - **TD-T724-01.** `merge-mcp-json.py` treats any literal value in a generated `env` block, for example `GITLAB_PERMISSION_MODE: modify`, as hand-edited. It matters only if `gitlab` is retired.
  - **TD-T723-01.** `docs/releases/v9.0.0.md` cites `install.sh:1300`. The advice now starts near line 1297 and spans four lines. The published document stays unchanged.
- **Migration item for the next release document (T725, TD-T671-P5):**
  - Authoring-only commands are no longer installed into target projects.
  - Commands declare `audience: authoring | target | both`. `scripts/install.sh` withholds every `authoring` command from a target project on every platform. Today that is only `/prepare-release`: `.claude/commands/prepare-release.md`, `.gemini/commands/prepare-release.md`, `.opencode/commands/prepare-release.md`, `.pi/prompts/prepare-release.md` and `.github/prompts/prepare-release.prompt.md`.
  - On `install.sh --update` or `--projections-only`, an existing copy in a target is deleted. A dry run prints the `rm` it would run.
  - An authoring checkout keeps these commands. An authoring checkout is a directory with `implementation/registry/index.json`, such as the emage.code repository itself.
  - A target project that used `/prepare-release` should keep its own copy under a different file name.
  - Each generated tree's `.generated-manifest.json` gains an `authoringOnly` list.
  - The generator now refuses a command without a valid `audience:`.
- **Root drift.** 12 paths are declared. T722 adds 6: the MCP configs (the `--index-dir` argument dropped) and the Copilot `context-retriever` agent. T725 adds the 6 `.generated-manifest.json` files.
- **Token use against budget:**

  | Task | Used | Budget |
  |---|---|---|
  | T722 | about 180k | 100k |
  | T723 | about 168k | 100k |
  | T724 | about 64k | 50k |
  | T725 | about 130k | 100k |
  | Security review | about 177k | 70k |
