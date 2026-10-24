# T690 — Generate security-audit and poc-security-audit for GitHub Copilot (K-3, D-4)

**ID:** T690
**Owner:** devops-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T687
**Affects:** —
**Created:** 2026-10-24
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-24: T690)
- The user's decisions of 2026-10-24 (replies to the decision list of `docs/artifacts/tracked-debt-register-v2.md` section 5.2): "D-4-b" (option (b), generate the two servers for Copilot, over the recommended (a))
- `docs/artifacts/tracked-debt-register-v2.md` (D-4, K-3)

## 1. What and why

Today the `github` platform manifest (`implementation/platforms/github.json`, `mcp.tags: ["core"]`) emits only the core servers into `.vscode/mcp.json`, so the PoC security scan cannot complete on GitHub Copilot and the agent rule makes that a FAIL. Generate the two servers `security-audit` and `poc-security-audit` for the `github` platform: opt the manifest in for those two servers (a tag or a per-server platform list, whichever fits the existing `extended` and `skipFormats` mechanisms of `servers.yaml` and `sync.mjs`; do not turn on every extended server: `cwso`, `filesystem`, `git`, `supabase`, `hf-mcp-server`, `context-retriever`, `toolradar` stay as they are), check how the other platforms reference the two local Python servers (paths, launcher, the `mcp==2.2.0` requirement) and mirror it in the VS Code format (`${workspaceFolder}`-style paths are the VS Code convention: verify against `implementation/.vscode/mcp.json` conventions and the documentation), make sure the Copilot agent files list the tools in the platform's tool-name form (`frontmatter.agents.mcpToolNames`, slash style) for the security agents that hold them, and update the per-platform tests (platform conformance, projections, tool-name mapping, grant pins, `test_mcp_agent_denials`), the documentation (the K-3 limitation sentences in `README.md`, `AGENTS.md`, `implementation/AGENTS.md` (the `extended` tag row), `implementation/PREREQUISITES.md`, `docs/wiki/mcp-servers.md`, the security agents' text) and the counts they pin. The result must keep every control: the two servers keep their secret-path denials and worktree roots; the Copilot config contains placeholders only. Declare the root drift; do not refresh the root install. *Acceptance:* `.vscode/mcp.json` carries the two servers; the Copilot security agents hold their tools; the K-3 limitation is gone from the live docs; all gates and the suite pass; a Security Engineer review follows.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. Agents without a shell (solution-architect, technical-writer) write their artifact text for the orchestrator to commit.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`check_evaluator_hash()`, no drift unless the brief says otherwise), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths plus one comment line starting `Declared <date> by <task> (`); do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere; only T668 may modify `tests/golden/**` (grant G-2). No `.env*` or credential files (the primary checkout has an untracked local `.env` that must not be read or grepped); do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol


Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
