# T631 — Adopter documentation for the new surface (audit C-7)

**ID:** T631
**Owner:** technical-writer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T631)
- `docs/artifacts/release-v8-audit-v1.md` §3 (the drafted Migration section) and C-7; `scripts/install.sh` (`--help` text and post-install notices), `implementation/knowledge/mcp/servers.yaml`
- `README.md`, `docs/wiki/*`, `implementation/README.md`, `implementation/SECURITY.md`
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Document, once and consistently, the surface that adopters now meet and that no adopter document mentions: the installer's `--projections-only` and the `--update` behaviour that now spares client-owned files (`.claude/settings.json`, `.github/workflows` and the others the installer lists), the `poc-security-audit` MCP server (two tools, what a clean result means), the client-owned allow rule `mcp__poc-security-audit__*` that the installer never writes and that adopters add to `.claude/settings.json`, the Python `mcp` dependency and `git >= 2.40` requirement and that the server must run from the project root, and the environment variables the `.mcp.json` now expects. Verify every claim against `install.sh`, the MCP config and the contract (`poc-security-engineer-tool-scoping-v4.md` to `-v6.md`); do not invent behaviour. Do not change any version marker or any `Latest release` line (the release task does that). Do not edit generated platform folders by hand.

## 2. Output

Edits to the documents above, with a short claim-to-source table in your report. Because you have no shell, return the changes in the files and a list of every file touched; the orchestrator commits and runs the gates.

## 3. Constraints

- You have no shell (or only read-only commands where the brief says so). Do not commit, push or merge; the orchestrator does. Do not edit `.claude/`, `.github/` or other derived platform folders.
- **Write access:** the documents named in §1 and this brief's `**Status:**` line (set it to `in_review`).
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Each new flag, server and requirement is documented exactly once per document and consistently across documents.
2. Every claim cites its source (file:line) in the report.
3. No version marker changed.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
