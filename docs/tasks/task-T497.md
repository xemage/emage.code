# Task T497 — `@security-engineer` Option C implementation: audit-command MCP server

**ID:** T497
**Owner:** backend-developer
**Status:** done

Implementation landed, independently verified (diff scope, byte-level `servers.yaml`/`.mcp.json`
isolation, full test suite, adversarial injection-safety proof re-run fresh in a separate
orchestrator-owned venv, `sync.mjs --check`/`generate-registry.py --check`/`check-maturity.py` all
clean). See `completed-tasks.md` for the full closure record.
**Priority:** P1
**Depends on:** None structurally blocking. Builds directly from `docs/artifacts/
security-engineer-audit-server-design-v1.md` (T496, design-completion pass, delivered and merged
to `develop` at `9827d0c` — status stays `blocked`, not `done`, per that task's own brief; see
"Ledger note" below). Independent of `T456`, `T458`, `T483`.
**Created:** 2026-09-17
**Completed:** 2026-09-17
**Based on:**
- `docs/artifacts/security-engineer-audit-server-design-v1.md` (T496) — the sole authoritative
  spec for this task. Read in full this session. Implement exactly what it specifies (file layout
  §4.1, `commands.py`/`executor.py`/`validation.py`/`audit_server.py` sketches §4.2–4.4, the four
  tools' exact argv shapes §2.1–2.4, the `servers.yaml` entry §3, the Claude Code grant §3). Do
  **not** re-derive or second-guess the design's own settled decisions (§5). Do **not** silently
  resolve §6's explicitly-undecided items as if they were fully specified — treat them as
  starting points per that section's own instruction (see "Explicitly open per §6" below).
- `implementation/runtime/memory/context_retriever_mcp_server/` (T495) — the direct structural
  precedent this task mirrors: a dedicated `stdio` MCP server package, one module as the sole
  I/O/subprocess choke point, `servers.yaml` entry conventions, platform-projection regeneration,
  and a live adversarial subprocess-over-stdio test suite proving scoping (`tests/functional/
  test_context_retriever_mcp_server.py`'s `AdversarialToolScopingProbeTests` is the pattern to
  adapt, not re-derive from scratch).
- `implementation/knowledge/agents/security-engineer.md` — current `tools:` grant
  (`[read, search, execute, web, mcp__fetch]`), to be changed per the design's §3 illustrative
  grant.
- `implementation/knowledge/mcp/servers.yaml` — registry format; add the `security-audit` entry
  per the design's §3 YAML sketch exactly (tag `extended`, `stdio`, `command: python3`, no `env:`).

## Objective

Implement the `security-audit` MCP server exactly as specified in
`security-engineer-audit-server-design-v1.md`: a new `implementation/runtime/security/`
subpackage (`audit_server.py`, `commands.py`, `executor.py`, `validation.py`) registering exactly
four tools (`run_npm_audit`, `run_pip_audit`, `run_dotnet_list_vulnerable`, `grep_content`) and no
others; a new `security-audit` entry in `servers.yaml`; regenerated platform projections; and
`security-engineer.md`'s `tools:` grant changed from including `execute` to the four exact
`mcp__security-audit__*` tokens (Claude Code only — per-platform grant syntax for other platforms
remains the same open, disclosed gap the design's §6 item 7 left open; do not attempt to resolve
it here). Back this with a live adversarial test suite proving (a) each tool's real argv
construction matches the design, unit-testable without the real external binaries; (b) a
malicious parameter value (e.g. `pattern` or a path containing `; rm -rf /`-style shell
metacharacters) reaches the underlying command as one literal argv element, never shell-
interpreted — via real subprocess-over-stdio, mirroring T495's own adversarial proof, not just
argv-construction unit tests; (c) no tool outside the four named ones is ever registered or
callable (no generic `run_command`/`execute`).

## Constraints

- **Never touch `feature/T475-codex-platform-integration`.** This worktree is isolated on its own
  branch (`agent/backend-developer/T497`, branched from `origin/develop` at `9827d0c`) — do not
  fetch, merge, or reference that branch for any reason.
- **Never edit** `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`,
  `docs/benchmarks/tb-subset.md`.
- **`T456`, `T458`, `T483` are untouched by this task.**
- **No new paid/metered API usage.** The `mcp` Python SDK (`pip install mcp`) is the same
  open-source, one-time local dependency T495 already used — install into an isolated throwaway
  location (e.g. a scratch venv), never into the repo's tracked manifest as a new committed
  runtime dependency unless the design or T495's own precedent already requires it there (check
  `implementation/runtime/memory/requirements-mcp-server.txt` for precedent before adding a new
  requirements file).
- **Do not fix the two disclosed, unrelated `servers.yaml` registry defects** (`filesystem`/`git`
  package names) as a drive-by. Leave them disclosed, not fixed — this task's own scope
  (`security-audit`, a new, separate entry) does not require touching those entries.
- **Explicitly open per the design's §6 — adjust with justification, disclosed, not silent:**
  timeout (`DEFAULT_TIMEOUT_SECONDS = 30`), `MAX_PATTERN_LENGTH = 512`, `MAX_GLOB_LENGTH = 256`,
  and stdout/stderr truncation policy are starting points, not fixed specs. `rg`/`npm`/
  `pip-audit`/`dotnet` availability is **not** guaranteed in every runtime — this session's own
  environment has `rg`, `npm`, and `dotnet` but **not** `pip-audit` (independently confirmed via
  `command -v` before this dispatch). Handle absence gracefully: a tool invocation against a
  missing binary must surface a clear, structured error (e.g. `FileNotFoundError` caught and
  reported as a normal tool-result error, not an unhandled crash) — do not skip implementing
  `run_pip_audit` just because the binary isn't installed here; write it exactly like the other
  three, and let the adversarial/argv-construction tests that don't need the real binary cover it,
  while any live-subprocess test needing the real `pip-audit` binary skips with a clear reason
  (mirroring how T495's own test suite skipped gracefully without the `mcp` SDK).
- **Per-platform grant syntax for platforms other than Claude Code is not resolved by this task**
  — scope the `tools:` grant change to Claude Code's exact-tool-name form only, same as T495,
  with the same gap disclosed in your completion report.
- File ownership: this task owns the new `implementation/runtime/security/` package, the new
  `servers.yaml` entry, `security-engineer.md`'s `tools:` line + regenerated platform projections,
  and the new test file(s). Do not modify unrelated files.

## Expected Outputs

1. `implementation/runtime/security/__init__.py`, `commands.py`, `executor.py`, `validation.py`,
   `audit_server.py` — per the design's §4.1–§4.4.
2. `implementation/knowledge/mcp/servers.yaml` — new `security-audit` entry per §3.
3. `implementation/knowledge/agents/security-engineer.md` — `tools:` line updated per §3's
   illustrative grant; all platform projections + provenance sidecars regenerated via `sync.mjs`.
4. New test file(s) under `tests/functional/` (e.g. `test_audit_server.py` or similar, mirroring
   `test_context_retriever_mcp_server.py`'s naming) with:
   - Pure unit tests of each `build_*_argv()` function in `commands.py` (no subprocess, no I/O) —
     confirms exact argv shape per §2.1–2.4's code sketches.
   - A live adversarial subprocess-over-stdio test class proving fabricated/malicious parameter
     values never reach a shell as syntax (e.g. `pattern="; rm -rf /tmp/proof-marker"` or similar,
     with a concrete check that no such side effect occurred), and that no tool outside the four
     named ones is registered/callable.
   - Graceful skip (not failure, not fabricated pass) for any sub-test that needs a real binary
     this environment lacks (`pip-audit` confirmed absent) or the optional `mcp` SDK if not
     installed in the ambient environment.
5. A brief completion report disclosing: any place the design's own sketches turned out to be
   wrong or incomplete once real code was written (mirroring T491's real-gap disclosure); which
   of the four external tools were actually exercised end-to-end vs. unit-tested only, in this
   environment; confirmation of `sync.mjs --check` clean; full `python3 tests/run.py` result
   before/after, with any pre-existing failures independently distinguished from regressions this
   branch introduced (do not assume "pre-existing" without independently confirming against plain
   `origin/develop` in a complete environment, per T495's own corrected self-report lesson).

## Acceptance Criteria

- Exactly four tools registered in `audit_server.py` — no `run_command`/`execute`/other generic
  tool. Verifiable by reading the module directly (structural, not just a claim).
- `executor.py` is the only module calling `subprocess.run`; `shell=False` appears in exactly one
  place; `check=False` is used (non-zero exit is a valid finding, not a failure).
- Each `build_*_argv()` function returns the exact argv shape specified in §2.1–2.4 (verified by
  unit test, not just code review).
- The adversarial test suite actually runs (not just exists) and passes, proving a malicious
  `pattern`/path value is delivered as one literal argv element via a real subprocess call, never
  shell-interpreted.
- `servers.yaml`'s new `security-audit` entry matches §3 exactly; no other entry in the file is
  touched (byte-level diff must show only the new entry added).
- `security-engineer.md`'s `tools:` line matches §3's illustrative grant exactly (four
  `mcp__security-audit__*` tokens replacing `execute`; `read, search, web, mcp__fetch` retained).
- All platform projections regenerated and `sync.mjs --check` reports no drift.
- `python3 tests/run.py` passes with zero regressions (pre-existing failures, if any, independently
  reconfirmed against plain `origin/develop`, not assumed).
- Missing `pip-audit` binary in this environment does not block completion — `run_pip_audit` is
  fully implemented and unit-tested; any test requiring the real binary skips with a clear reason.

## Ledger note (read before reporting completion)

`task-T496.md`'s own Status field states explicitly: *"blocked — design-completion artifact
delivered... real implementation gap remains open, mirroring T457's own 'design delivered, row
stays blocked' posture. Not `done`."* This is the established, documented policy for T496 — it is
a design-tracking row, not an implementation row, and per `T457`'s own precedent (T495 succeeding
did not close T457), T496 is not expected to transition to `done` merely because a downstream
implementation task (this one) succeeds. Do not treat this task's own success as authorization to
recharacterize T496 — that is an orchestrator/ledger decision, out of scope for this brief.

## Blocker Protocol

Report blockers with `type` (`technical` | `dependency` | `unclear_requirements` | `external`) and
`severity` (`critical` | `major` | `minor`). Max 2 retries before escalation. If the design's own
sketches are wrong once real code is written, report it plainly as a disclosed correction, not a
silent fix — mirroring how T491's implementation found and fixed one real gap T483's design didn't
anticipate.
