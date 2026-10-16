# T603 — Implement the fixed-command PoC security scanner and drop `execute` from `poc-security-engineer` (L4/X5)

**ID:** T603
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** T602
**Created:** 2026-10-09
**Based on:**
- `docs/artifacts/poc-security-engineer-tool-scoping-v2.md`: **the single implementation input.** It holds the
  contract of the two tools, the held edits (E1-a, E1-b, E1-c and F-8) and the rollout and test list.
- `docs/artifacts/security-review-poc-security-engineer-tool-scoping-v1.md`. Its findings are all in v2's spec.
- `docs/artifacts/security-engineer-audit-server-design-v1.md` and `implementation/runtime/security/`: the existing
  fixed-command server whose pattern you follow.
- The user's decisions of 2026-10-09: "New 2-tool server (Recommended)" and "Keep, record residual (Recommended)".

**Maturity note:** this task's priority is P2 and its `**Affects:**` is `—` on purpose. A P0 or P1 task naming
`agent/poc-security-engineer` would drop the agent from `stable`.

## 1. What

Build and wire the server, then swap the grant. Follow v2 exactly:
1. **New module** `implementation/runtime/security/poc_audit_server.py`, with tools `scan_secrets` and
   `ref_containment`, as a **separate** server from the existing four-tool one. `test_audit_server.py` requires
   exactly four tools there, so do not touch it.
   - Reuse the existing `executor.py`/`validation.py` pattern, but only where v2 allows it. v2 requires an explicit
     subprocess environment, the hardened git argv, a bounded streaming read and an aggregate deadline, which the
     existing executor does not do. Implement those in the new module and do not change the existing executor's
     behaviour.
2. **Registration:** the `servers.yaml` entry and every platform's regenerated MCP config.
3. **Tests**, all from v2's list. They include:
   - the planting test for `core.fsmonitor`;
   - a root-must-equal-top-level test;
   - redaction of paths and refs, and `-z` parsing with a path containing `:12:`;
   - tri-state `pushed`;
   - truncation and deadline;
   - no `shell=True`;
   - a start-up smoke test (list the tools, one call against a fixture repository);
   - a test that `poc-security-engineer` has neither `execute` nor `Bash`, mirroring
     `ProjectedClaudeCodeAgentGrantTests`.
4. **Last step, the grant swap and held edits** (E1-a, E1-b, E1-c, F-8), applied verbatim from v2's fences with exact
   string replacement. The Before of each must occur exactly once.
5. **Regenerate and declare:** run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`. Declare exactly the paths that `--print-drift` prints in
   `tests/_baselines/root-install-drift.json`. Do not refresh the repo root.

## 2. Controls (report every result)

- **Security review:** the code is security tooling. Make the work reviewable: keep the new module small and
  readable, and list in your report every place that spawns a process, with its full argv.
- **Behaviour proof:** show that each v2 contract field is tested, including a failing run of the planting test
  against a deliberately un-hardened variant.
- **Gates:** `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`,
  `scripts/scorecard.py --check` (34 / 26 / 0), `validate-tasks.py`.
- **Golden:** no file under `tests/golden/` changes. The evaluator-hash tests stay green against **v20**.
- **Suite:** run `python3 tests/run.py`, redirecting output to a file. Expect all tests to pass.

## 3. Constraints

- **Write scope:** `implementation/runtime/security/` (new module only), its tests under `tests/`, `servers.yaml`
  (the one entry), the regenerated platform MCP configs, `poc-security-engineer.md` (the held edits only), the
  regenerated mirrors and registry, the drift baseline, and this brief's `**Status:**` line.
- **Forbidden:**
  - `tests/golden/` (never open held-out);
  - `scripts/`;
  - `.claude/settings.json` and any other client-owned settings: never edit them;
  - `.env*`, credential or key files.
- **Commit:** one Conventional Commit, ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 4. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). If any v2 contract field cannot be implemented as written, stop and report it.
