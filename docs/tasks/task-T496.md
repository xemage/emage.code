# Task T496 — `@security-engineer` Option C design-completion pass (T457 §2.3, Track 2)

**ID:** T496
**Owner:** solution-architect
**Status:** blocked — design-completion artifact delivered (`docs/artifacts/
security-engineer-audit-server-design-v1.md`); real implementation gap remains open, mirroring
T457's own "design delivered, row stays blocked" posture. Not `done`.
**Priority:** P1
**Depends on:** None structurally. Deepens `docs/artifacts/scoped-execution-primitive-v1.md` §2.3
(Option C), which T457's design pass deliberately left with its exact scope open. Does **not**
depend on Track 1 (`T495`) and must not be serialized behind it.
**Created:** 2026-09-17
**Completed:** —
**Based on:**
- `docs/artifacts/scoped-execution-primitive-v1.md` — read in full; specifically §2 (`@security-
  engineer`'s three-option framing), §2.3 (Option C's own working-out) and §2.4 (the labeled,
  non-binding recommendation). §2.3 explicitly names the one open question this task exists to
  resolve: *"which exact commands make the fixed list — do `pip-audit`, `dotnet list package
  --vulnerable`, and per-language linters all need their own wrapped tool, or a smaller curated
  subset?"* — and names the design hazard this task must design against for every wrapped tool:
  *"if `run_npm_audit`'s `package_json_dir` parameter were naively string-concatenated into a shell
  command rather than passed as a subprocess argument list element, this server would reintroduce
  exactly the injection risk it exists to close."*
- `implementation/knowledge/agents/security-engineer.md` — the agent's own current OWASP/audit
  checklist (A01–A10 sections). Ground the fixed command list in this file's *actual* stated
  workload, not in commands that sound plausible but aren't named anywhere in it.
- `docs/artifacts/mcp-header-url-templating-design-v1.md` (T483) — the structural/rigor precedent
  this document should mirror: explicit alternatives, explicit trade-offs, explicit citations, an
  exact code-level design concrete enough for a subsequent implementation task to build verbatim
  from (§5/§7 of that document is what T491 later implemented almost line-for-line — match that
  level of concreteness here).
- `implementation/knowledge/mcp/servers.yaml` (read-only reference — registry format/conventions
  only; do not edit).
- `docs/artifacts/mcp-platform-contract-v1.md` (T420) — the per-platform MCP contract any eventual
  server registration must conform to.

## Objective

Produce a design-completion artifact that resolves Option C's currently-open scope: (a) a concrete,
fixed list of audit commands, each justified by direct citation to `security-engineer.md`'s own
checklist content — not invented; (b) each wrapped tool's exact parameter surface, with explicit,
per-tool attention to the injection-risk hazard already named in §2.3 (subprocess argument-list
construction, never shell string-concatenation); (c) a concrete `servers.yaml` entry design plus a
server-code structure sketch, detailed enough that a subsequent implementation task can build from it
directly — mirroring how T483's design phase preceded T491's implementation. This document's own
implementation is **explicitly not dispatched this round** — only this design-completion pass.

## Constraints

- **Design-only. Do not edit `.mcp.json`, `servers.yaml`, any agent `tools:` grant, or
  `sync.mjs`. Do not run `sync.mjs`. Do not run any live test. Do not write server code** — a
  sketch/structure description in the design document is the deliverable, not a working module.
  (You do not have `execute`/`edit`-to-code tools for this role regardless — this constraint
  restates the boundary explicitly so it's not discovered mid-task.)
- **Never touch `feature/T475-codex-platform-integration`.** This worktree is already isolated on
  its own branch (`agent/solution-architect/T496`, branched from `origin/develop` at `7885989`) —
  do not fetch, merge, or reference that branch for any reason.
- **Never edit** `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`,
  `docs/benchmarks/tb-subset.md`.
- **`T456`, `T458`, `T483` are untouched by this task.** Track 1 (`T495`) is a sibling, independent
  task — do not reference it as a dependency or wait on it.
- **Do not invent commands `security-engineer.md` doesn't actually call for.** Survey the file's
  real A01–A10 checklist content first; every proposed wrapped tool must trace to a specific,
  quoted line or section of that file (or be explicitly flagged as "not currently in the checklist,
  proposed as a gap-fill, needs sign-off from the product owner role" if you find a genuine case
  for one that isn't — don't silently add commands beyond what the real workload calls for).
- **Address the injection hazard for every single wrapped tool individually** — a general statement
  that "parameters are passed as argument-list elements" at the top of the document is not
  sufficient; each tool's own parameter table must state this explicitly.
- **Git workflow (mandatory, zero exceptions):** you are already on branch
  `agent/solution-architect/T496` in this worktree (`/home/emage/Code/emage/worktrees/
  agent-solution-architect-T496`), branched from `origin/develop`. Commit your artifact here. Do
  **not** commit to `develop`/`main` directly, and do **not** merge your own MR — open it against
  `develop` and leave it unmerged for the orchestrator/user to merge. Conventional Commits format
  (`docs(artifacts): ...`).

## Expected Outputs

1. A new artifact, `docs/artifacts/security-engineer-audit-server-design-v1.md`, with a `Based on:`
   line citing `docs/artifacts/scoped-execution-primitive-v1.md` §2.3 per this repo's Artifact
   Versioning convention (revisions/extensions create new versions/documents, never overwrite the
   original).
2. A fixed command table: one row per wrapped tool, columns for (tool name, underlying command,
   which `security-engineer.md` OWASP section it serves — quoted, not paraphrased, with a line
   reference — and why a fixed/pre-approved shape is sufficient for that command's legitimate use).
3. A parameter-surface section per tool: exact parameter names/types, and an explicit statement of
   how each parameter reaches the underlying subprocess call — a concrete code sketch (e.g. a
   `subprocess.run([...], ...)` call shape with the parameter as a distinct list element) is
   preferred over prose alone, mirroring `context_retriever.py`'s own "`query_text` as a data
   argument to a fixed Python call, never as a shell string" pattern already cited by §2.3.
4. A concrete `servers.yaml` entry design (the actual YAML block, not just a description) plus a
   server module structure sketch (file layout, key function signatures) — detailed enough that
   `T495`'s implementation pattern (a small `stdio` server, `servers.yaml` registration, exact-tool-
   name grant on `security-engineer.md`) could be repeated for this server by a future implementation
   task without re-deriving the design from scratch.
5. Explicit "What this document does NOT decide" and "Blockers" sections, per this repo's
   established convention (mirror `scoped-execution-primitive-v1.md` §5/§6's own structure) —
   including an explicit statement that implementation is out of scope for this task and remains a
   separate, future, not-yet-dispatched task.

## Acceptance Criteria

1. Every wrapped tool in the fixed command list traces to an actual, quoted line in
   `security-engineer.md`'s checklist — no invented commands without an explicit, separately-flagged
   "gap-fill, needs sign-off" disclosure.
2. Every wrapped tool's parameter surface explicitly and individually addresses the
   subprocess-argument-list-not-shell-interpolation hazard — checkable by a reviewer reading each
   tool's own subsection independently, not just the document's intro.
3. The `servers.yaml` entry design and server-code sketch are concrete enough that a future
   implementation task's brief could reference this document's own code blocks directly, the same
   way `T491`'s brief referenced `mcp-header-url-templating-design-v1.md` §5/§7 directly.
4. Zero edits to `.mcp.json`, `servers.yaml`, any agent `tools:` grant, or `sync.mjs` — confirmed by
   `git diff --stat` against `origin/develop` showing only the one new artifact file (plus this
   task-brief/ledger commit).
5. A self-referential ledger-defect sweep performed on this artifact and this brief against the
   current real `stable`-tier component id list — report the result (zero hits expected; report a
   blocker if not).
6. Branch `agent/solution-architect/T496` pushed to `origin`, MR opened against `develop`
   (`glab mr create`), CI polled to completion and reported green — **left unmerged**.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` | `external`)
and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`. Max 2 retries before escalating to
the orchestrator. If you cannot ground a command `security-engineer.md`'s workload plausibly needs
(e.g. dependency-vulnerability scanning for a language ecosystem this repo's checklist implies but
doesn't name a specific tool for) in an exact citation, report `type: unclear_requirements`,
`severity: minor` and propose your best-justified choice rather than blocking entirely — this
mirrors how `plan-049`/`scoped-execution-primitive-v1.md` itself handled genuinely unresolved
per-platform questions (disclosed, not silently resolved by assumption).
