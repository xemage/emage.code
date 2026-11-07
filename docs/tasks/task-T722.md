# T722 — Batch A: generator and MCP server definitions

**ID:** T722
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-128-batch-a-installer-generator.md` (task T722)
- The user's answer of 2026-11-02, verbatim: "A go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v4.md` (batch A rows; descriptions in v1 to v3)

## 1. What and why

(devops-engineer): generator and MCP server definitions.
   - **SEC-T684-01**: `physicalFolded` in `sync.mjs` (around line 944) follows a dangling link with a lexical `dirname`. Fix: `path.resolve(await fs.realpath(path.dirname(current)), link)`, with a test.
   - **SEC-T684-02**: `mcp.outputFile` is guarded only by a deny-list of inputs. Allow it only under the manifest's own `outputDir`, plus the two exact exceptions, with a test.
   - **SEV-T690-01**: `agentMcpDenials` selects servers by tags only and ignores `extraPlatforms`. Honour `extraPlatforms`, with a test.
   - **SEV-T690-05**: in the T690 tests, mutation M11 is killed only by an input the regex refuses first, and the assertions are superset-only. Add a direct kill and exact assertions.
   - **SEV-T690-06**: the Copilot agents list `context-retriever/retrieve`, but that extended server is not generated into `.vscode/mcp.json`. Drop the tool from the Copilot render, which is fail-closed and the smallest surface. Remove the exception pinned in `test_mcp_tool_name_mapping.py`.
   - **SEC-T663-02**: `implementation/.opencode/agents/*.md` use a `tools:` map and have no `permission:` block. Check the current Opencode agent schema with ctx7 or the vendor documentation. If `tools` is deprecated, or `permission` is the documented control, generate the denials in the documented form. If the current form is still documented and enforced, report that with the source.
   - **TD-T671-K5**: `implementation/knowledge/mcp/servers.yaml:201` hard-codes the `context-retriever` index directory as `em-age-emage.code` for every project. Derive it from the project, or, if the server's index layout requires a fixed name, document it in the setup text (`implementation/PREREQUISITES.md` or `docs/wiki/mcp-servers.md`) and report why.
   - *Acceptance:* each item is fixed with a test, or reported with a reason. Projection changes are declared as root drift, with no root refresh. All gates and the suite pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test that shows it) or not fixed (with the reason).

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with a test, or reported with a reason. Projection changes are declared as root drift, with no root refresh. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
