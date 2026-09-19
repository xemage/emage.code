# Plan 054 — OpenAI Codex Platform Integration (post-v7.0 feature)

**Author:** top-level session (planning only — no task briefs opened, no implementation dispatched)
**Date:** 2026-09-18
**Status:** proposed — deliberately sequenced after `plan-035`'s v7.0 roadmap finishes, not before

## Why this is sequenced after v7.0, explicitly

`plan-035-roadmap-v7-ground-up.md`'s Phase 6 (Closed Loop, v7.0.0) is this repository's actual
final target for the currently-approved roadmap — it is now reachable at the gate level (Gate G3
closed, per `docs/checkpoints/checkpoint-033-phase4-phase5-complete-gate-g3-closed.md`) but not yet
planned to execution-ready detail or started. Codex platform integration is real, substantial,
already-gated work (see "Current state" below) that predates and is entirely independent of
`plan-035`'s own task-ID range (`T400`–`T474`; Codex used `T475`–`T482`, the next free range at the
time) — it was never part of the v7.0 roadmap's own scope. Per the user's explicit instruction,
this plan schedules it as separate, later work rather than interleaving it with Phase 6, and
documents the branch's real current state now so that later work does not have to rediscover it
from scratch.

**This plan does not open, dispatch, or authorize any task.** It is a scoping and state-capture
document only, mirroring how `plan-035` §2.4 Phase 6 itself is currently "sketched, not planned to
execution-ready detail" — the same posture, applied here.

## Current state of `feature/T475-codex-platform-integration` (verified directly, 2026-09-18)

- **Real, substantial, already-implemented work**: 2 commits (`84c4d7d` "feat: add OpenAI Codex
  platform support", `4683e59` "docs: record Codex validation gate condition"), both dated
  2026-09-01. Diff against the branch's own merge-base with `develop`: **228 files changed, 14,319
  insertions, 94 deletions** — a real eighth platform projection, not a stub.
- **Backing plan**: `docs/plans/plan-036-add-openai-codex-as-a-supported-platform.md` (approved,
  384 lines) — Codex as an eighth supported platform via repository-native surfaces: root
  `AGENTS.md` for durable instructions, `.codex/agents/*.toml` for custom agents,
  `.agents/skills/*/SKILL.md` for skills (command workflows projected as `$skill-name` invocations,
  not native `/` slash commands — Codex does not consume repository-scoped slash-command files),
  `.codex/config.toml` for project-scoped MCP configuration (managed only inside a marker-delimited
  block, preserving user edits outside it).
- **Backing decision**: `docs/decisions/ADR-003-codex-native-projection.md` (accepted) — the same
  scope, plus explicit safety constraints: never write to global Codex configuration
  (`~/.codex`/`$CODEX_HOME`), never emit credentials, never set project model/approval/reasoning/
  writable-sandbox defaults, canonical `tools` metadata expressed as policy instructions and
  conservative read-only defaults, never treated as a native Codex tool allowlist.
- **Task breakdown, all on this branch** (`docs/tasks/task-T475.md` through `task-T482.md`):

  | Task | Owner | Status | What it covers |
  |---|---|---|---|
  | T475 | solution-architect | `done` | Projection contract + ADR-003 |
  | T476 | backend-developer | `done` | Manifest + deterministic sync transforms |
  | T477 | backend-developer | `done` | Safe installation/update merge helpers (no destructive overwrite of user `.codex` settings) |
  | T478 | backend-developer | `done` | Generated artifacts + registry refresh |
  | T479 | qa-engineer | `done` | Automated test coverage (projection, TOML, merge, installer, path-safety, registry, determinism, secret-guard) |
  | T480 | technical-writer | `done` | Documentation (README, contributor guidance, wiki, setup docs) |
  | **T481** | tech-lead | **`in_progress`** | Runtime/quality gates — **blocked, see below** |
  | T482 | release-manager | `pending` | Release + checkpoint closeout — blocked on T481 |

- **The one real blocker (T481, unchanged since 2026-09-01, re-confirmed today)**: every static,
  projection, installer, secret-guard, registry, and full-suite check passes
  (`docs/checkpoints/checkpoint-020-codex-platform-implementation.md`:
  `make verify` zero drift across 643 files/8 platforms at the time, `make test` 384 tests with 3
  expected live-integration skips, `implementation/scripts/check.py` 250 checks PASS). The **only**
  outstanding condition is a live, trusted-project Codex CLI smoke test —
  `docs/artifacts/gate-codex-implementation-2026-09-01.md` recorded a `CONDITIONAL_PASS` verdict for
  exactly this reason: the only `codex` executable available at implementation time was a Windows
  npm shim missing its `@openai/codex-linux-x64` optional dependency, so a real trusted-project
  smoke test (confirming `AGENTS.md`, skills, custom agents, and MCP actually work end-to-end
  against a genuine Codex host) has never been run. **Re-confirmed today**: `codex` is still not
  installed/available on this host (`command not found`). This is a real, external, environmental
  prerequisite — not a code defect — and has not changed in either direction since 2026-09-01.

## Why this cannot simply be merged as-is when the time comes

- **227 commits behind `develop` as of this plan** (growing every day this stays unmerged) — this
  branch forked before nearly this entire session's worth of work: Phase 2 (MCP conformance),
  Phase 3 (Maturity Ladder), Phase 4 (Task-Tier Routing), and all of Phase 5 (Persistent
  Memory/RAG, including the `T457`/`T495`–`T497` tool-scoping side-quest and the `T458`/`T456`/
  `T498`/`T499` ship-gate arc) happened entirely after this branch's fork point.
- **Concrete, disclosed drift already identified**: `plan-036`'s own stated baseline was "seven
  manifests generate 557 files with zero drift." `develop` currently generates **577 files** across
  the same seven platforms (`sync.mjs --root implementation --check`, verified today) — the
  platform-projection baseline itself has moved. More concretely: `develop`'s
  `implementation/knowledge/mcp/servers.yaml` now has **23 registered MCP servers** (verified
  today: `gitlab`, `playwright`, `fetch`, `memory`, `sequential-thinking`, `brave`, `context7`,
  `hindsight`, `cwso`, `hf-mcp-server`, `context-retriever`, `security-audit`, `filesystem`,
  `github`, `git`, `supabase`, `docker`, `postgresql`, `toolradar`, plus others) — at least
  `hindsight`, `cwso`, `context-retriever`, and `security-audit` were added after this branch's
  fork (`T483`/`T491` and `T495`/`T497` respectively), and the Codex branch's own `.codex/
  config.toml` projection logic and marker-managed MCP block have never seen any of them. A direct
  merge would either silently omit these servers from Codex's own projection or need the
  `emitMcp()`/`sync.mjs` Codex-format branch re-validated against the current, larger server set
  before trusting it produces correct TOML for all 23.
- **Agent/skill/instruction set has also grown**: 20 agents were `stable` at Phase 3's close
  (`checkpoint-032`); more knowledge-base content exists now than when `T476`'s manifest/sync
  transforms were written and tested. The Codex projection's own generation logic is very likely
  still structurally correct (it walks the current knowledge base, not a hardcoded list — this
  should be verified directly, not assumed) but has not been exercised against the current, larger
  corpus even once.
- **Root self-install drift, a separate, known, pre-existing repo characteristic** (see
  `docs/tasks/completed-tasks.md`'s `T382`/`T403`/`T406` precedent, and this session's own
  independent finding during `T457`/`T495`–`T497`'s closure): this repo's root-level self-install
  mirror (`.codex/`, `.agents/skills/`, etc., if this branch's own root copy is ever compared
  against a freshly-generated one) is refreshed only by `scripts/install.sh --update`, never by CI
  — a separate, already-understood axis of drift, not specific to Codex, but worth re-running once
  this branch is revived.

## Recommended integration approach, once this work is greenlit (not authorized by this plan)

1. **Do not attempt a direct `git merge`/fast-forward of the stale branch.** Given 227+ commits of
   divergence, the lowest-risk path is very likely a fresh re-application: check out a new branch
   from current `develop`, and either (a) cherry-pick/re-apply the two Codex commits and resolve
   whatever conflicts surface directly (likely concentrated in `implementation/scripts/sync.mjs`,
   `implementation/knowledge/mcp/servers.yaml`, and `implementation/platforms/*.json`, the exact
   files this session's own parallel work has touched most), or (b) treat `plan-036`/`ADR-003` as
   the authoritative design (both are re-usable, platform-agnostic, and unaffected by drift) and
   re-implement the sync/installer changes fresh against current `develop`, using the stale
   branch's own diff as a detailed reference rather than a literal patch. Decide which of (a)/(b)
   is cheaper only after actually attempting the cherry-pick and seeing the real conflict surface —
   don't assume either is cheaper without evidence.
2. **Re-verify the full test/sync/maturity bar fresh** on top of current `develop` before trusting
   anything from the stale branch — this repo's own conventions (`sync.mjs --check`,
   `check-maturity.py`, `validate-tasks.py`, `tests/run.py`) have all evolved since 2026-09-01 and
   the Codex work has never been checked against any of them.
3. **T481's actual blocker still needs a real Codex CLI host** — this has not changed and this plan
   does not resolve it. Whoever picks this up needs either a working `codex` installation
   (`@openai/codex-linux-x64` or the equivalent for the host OS) or an explicit decision to accept
   a narrower validation (e.g., structural/TOML-parsing validation only, with the interactive
   trusted-project smoke test tracked as a separate, disclosed follow-up) — that is a real decision
   for whoever re-opens this work, not pre-decided here.
4. **Re-open `T481`/`T482` as fresh, re-scoped tasks** (or genuinely resume them, if the ledger
   mechanics allow it cleanly) once the above is done — do not silently mark them `done` on the
   strength of 2026-09-01's evidence alone, since the surface they're validating has moved.
5. **Confirm the next free task-ID range and plan number at that time** — this plan is `plan-054`;
   by the time this work resumes, `develop`'s own numbering will have advanced further.

## What this plan explicitly does not do

- Does not open `T475`–`T482` as fresh ledger rows, does not change their `Status` fields on the
  stale branch, and does not touch `feature/T475-codex-platform-integration` in any way — that
  branch is left exactly as it is, a real, recoverable, already-gated body of work.
- Does not attempt to rebase, cherry-pick, or merge anything.
- Does not install or attempt to acquire a working Codex CLI on this or any host.
- Does not commit to a specific future date or session — "after `plan-035`'s v7.0 roadmap
  finishes" is the only sequencing constraint this plan asserts, per the user's own instruction.

## Acceptance criteria for this plan document itself

- [x] Current branch state (commits, diff scope, task/plan/ADR/checkpoint references) verified
      directly against the real branch content, not recalled from memory.
- [x] The real blocker (T481's external Codex-host prerequisite) confirmed still present, not
      assumed unchanged.
- [x] Concrete, verified drift since fork (commit count, file count, MCP server count) documented
      with real numbers, not estimated.
- [x] No task dispatched, no branch touched, no implementation started.
