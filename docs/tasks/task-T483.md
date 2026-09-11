# Task T483 — Register `hindsight` and `cwso` as managed MCP servers across all platforms

**ID:** T483
**Owner:** solution-architect (design first — the header/env-templating schema extension below is
a real design decision, not a data-entry choice; implementation owner once design lands is most
likely `backend-developer`, matching this repo's own T421 precedent for `sync.mjs`/`emitMcp()`
changes, with the QA Engineer role for the secret-guard/conformance test extensions, matching T422 —
display name used deliberately here rather than the registry id, per this repo's own established
self-referential-mention fix pattern, since that id is itself an already-`stable` component)
**Status:** pending — recorded this session, **not dispatched this session** (see "Why this is
recorded, not executed" below)
**Priority:** P1 (real, disclosed gap — two live MCP servers bypass this repo's own declarative
MCP-management pipeline entirely — but neither server being un-registered here blocks anything
currently on a critical path; Claude Code already has working config for both via the just-merged
manual fix)
**Depends on:** None structurally. Practically benefits from being scoped by whoever picks it up
re-reading `docs/artifacts/mcp-platform-contract-v1.md` (T420) first, since that document is the
authoritative source this task must extend, not just consult.
**Created:** 2026-09-11
**Completed:** —
**Based on:** `implementation/knowledge/mcp/servers.yaml` (canonical registry, read in full this
session — confirmed `hindsight`/`cwso` are genuinely absent, 15 entries only: 7 `core` + 8
`extended`); root `.mcp.json` on `origin/develop` as of commit `b542921` (post MR !279, read
directly — the concrete target shape both new registry entries must reproduce); `implementation/
scripts/sync.mjs`'s `emitMcp()` and `mapEnv()` (read in full this session, all 6 format branches);
`tests/functional/test_mcp_secret_guard.py` (`find_literal_env_values()`, read in full);
`tests/functional/test_mcp_schema_validation.py` and its two vendored fixtures (`tests/fixtures/
mcp-schemas/gemini-cli-settings.schema.json`, `.../opencode-config.schema.json`, both grepped for
`headers` support this session); `tests/functional/test_mcp_platform_conformance.py` (T422, read in
full — its round-trip design and isolation mechanism); `docs/artifacts/mcp-platform-contract-v1.md`
(T420, the authoritative per-platform contract this task's own new entries must be reconciled
into, not left as a silent gap); `docs/checkpoints/handoff-725b7925-6b66-47d2-b05b-b7c2e25a3bfb.md`
(prior session's note that `cwso`'s bearer token was, as of that handoff, failing live with
`AUTH_HEADER_REJECTED` (403) — status as of this task's creation unconfirmed, flagged below, not
silently assumed fixed just because the `.mcp.json` syntax fix merged).

## Objective

Bring `hindsight` and `cwso` — currently hand-added to the root `.mcp.json` only, bypassing
`servers.yaml`/`sync.mjs` entirely — into this repo's declarative MCP-server-management pipeline,
so they propagate correctly to every platform projection the same way all 15 existing servers do,
with the same secret-safety guarantees.

## Why this is recorded, not executed this session

The user's instruction asked for an honest assessment of whether this is "genuinely mechanical,
well-precedented work" (like T420-T423, Phase 2) that could be dispatched and executed in the same
turn, or work that needs the same "record now, execute later" treatment as T457/T458. Direct
inspection this session found it is **not** mechanical data entry — it requires real generator and
schema changes:

1. **`emitMcp()` has zero support for a `headers` field on remote-transport servers, in any of its
   6 format branches** (`vscode`/`cursor`, `gemini`, `opencode`, `claude-code`, `cline`; `pi` reuses
   the `cursor` branch — confirmed by comparing generated-file byte hashes). `cwso`'s real
   `.mcp.json` entry needs two custom headers (`Authorization: Bearer ${env:CWSO_BEARER_TOKEN}`,
   `Origin: ${env:CWSO_ORIGIN}`) that every remote-transport branch today emits only `{url}` (or
   `{httpUrl}`/`{type, url}` per format) for — `s.headers` is not read anywhere in `sync.mjs`.
   Adding it is real code, not a YAML row.
2. **Remote-transport `url` values are always emitted as a literal string today** (`s.url`, no
   `fromEnv`/templating pass) — every existing `remote`-tagged server (`context7`, `hf-mcp-server`)
   uses a hardcoded public URL. `hindsight`'s real value is `${env:HINDSIGHT_MCP_URL}` — an
   env-templated remote URL, a shape `servers.yaml`/`sync.mjs` has never had to represent before.
   The per-platform placeholder syntax already differs by format (`${env:VAR}` vs. `{env:VAR}` for
   `opencode`, per `mapEnv()`'s existing `template` parameter) — the same substitution needs to
   apply to `url` (and, for `cwso`, to `headers` values too), which `mapEnv()` doesn't do today; it
   is only ever called on `env` blocks, never on `url`/`headers`.
3. **`test_mcp_secret_guard.py`'s `find_literal_env_values()` only recurses into dict keys literally
   named `env`** (confirmed by reading the function body). It does not, and today has no reason to,
   walk a `headers` block. If `cwso`'s bearer token were added to a generated platform file in a
   naive implementation, this test — the one the acceptance criteria below require to "still
   pass" — would not actually catch a literal leaked token sitting in `headers`, only in `env`. The
   guard itself must be extended to cover `headers` before this task's own deliverable can honestly
   claim the secret guard protects it.
4. **Whether every platform's *real* remote-MCP-client implementation supports custom headers is
   not fully resolved by this session's evidence, only partially de-risked.** Both platforms this
   repo has a genuine, live-fetched, vendored official schema for (`gemini-cli-settings.schema.json`,
   `opencode-config.schema.json` — the only 2 of 7 with citable official schemas per T384/`test_mcp_
   schema_validation.py`'s own documented scope) do define a `headers` property on their remote-
   server config shape (grepped directly, confirmed this session: gemini schema lines ~4049/4147,
   opencode schema lines ~543/660) — so the two platforms this repo can actually schema-validate
   against are compatible. The other 5 platforms (`claude-code`, `cline`, `cursor`/`pi`, `github`/
   `vscode`) have no citable official schema in this repo's evidence base at all (T384's own finding,
   unchanged) — whether their real clients honor a `headers` field on an HTTP-transport MCP entry is
   unverified either way, same evidentiary gap `mcp-platform-contract-v1.md` already discloses for
   everything else about those 5 platforms.
5. **`cwso`'s live connectivity is independently in question, separate from the config-shape work
   above**: the last session-visible status (prior handoff, 2026-09-11) recorded the bearer token
   failing live with `AUTH_HEADER_REJECTED` (403). The user's own fix (MR !279) corrected the
   `.mcp.json` *syntax* (moving a literal value to `${env:...}` interpolation) — it is not evidence
   the underlying auth itself now succeeds. Whoever picks up implementation should re-check current
   live status rather than assume the syntax fix also fixed auth, and should not block this task's
   *registration* work on that (a server can be correctly registered and still be down/misconfigured
   at the network layer — those are separate failure modes).

None of this is undispatchable the way T457 is (T457 is blocked by a since-lifted session
constraint on touching `.mcp.json` at all) — there is no hard blocker here. It is recorded rather
than executed because it is real design-plus-implementation work comparable in shape to T420-T423
as a *phase*, not a single mechanical step, and deserves its own dispatch turn with a design owner
who can make the header/templating schema decision deliberately rather than as a rushed side effect
of a ledger-formatting task.

## Tag recommendation (for the eventual design owner to confirm or override)

- **`hindsight`** — recommend `core`. It is a memory/knowledge retrieval server, directly parallel
  in role to the existing `core`-tagged `memory` server (`@modelcontextprotocol/server-memory`).
  Whether it is a *replacement* for that server or a *complementary* one (both currently coexist in
  the live `.mcp.json`) is a real open question the design owner should resolve explicitly, not
  leave implicit — do not silently assume either answer.
- **`cwso`** — recommend `extended`. It is a specialized orchestration-coordination server (shadow
  workspaces, worker/orchestrator role tiers per `docs/artifacts/role-mapping-cwso-v1.md` and the
  `cwso-awareness` skill), not a general-purpose capability every platform/agent needs by default —
  closer in shape to `supabase`/`docker`/`postgresql` (infra-specific, opt-in) than to `gitlab`/
  `memory` (universally useful). Confirm against `cwso-awareness`'s own worker/orchestrator
  permission-tier split before finalizing, since that skill already describes which agent roles are
  meant to hold CWSO tool access.

## Inputs

- `implementation/knowledge/mcp/servers.yaml` — target file for the two new entries.
- `implementation/scripts/sync.mjs` — `emitMcp()` (all 6 format branches) and `mapEnv()` need
  extending; `implementation/scripts/sync.mjs --check` is the acceptance mechanism.
- Root `.mcp.json` on `origin/develop` (post MR !279) — the exact reference shape both entries must
  reproduce byte-for-byte for the `claude-code` format branch specifically (already correct there;
  every other platform currently has neither server at all).
- `tests/functional/test_mcp_secret_guard.py`, `test_mcp_schema_validation.py`,
  `test_mcp_platform_conformance.py` — existing suite to extend/re-run.
- `docs/artifacts/mcp-platform-contract-v1.md` — authoritative contract doc; its "15 servers total,
  7 core + 8 extended" summary (§2) and per-platform table (§3) both become stale the moment this
  task's `servers.yaml` change lands, and must be updated in the same change, not left to drift the
  way `servers.yaml`'s own header comment already drifted (noted in that doc's own §2).
- `docs/decisions/` — if the header/URL-templating schema extension is judged significant enough to
  warrant one, an ADR recording the decision (design owner's call).

## Constraints

- No literal secret values anywhere in `servers.yaml` or any generated file — `${env:VARNAME}` /
  `{env:VARNAME}` references only, matching the pattern MR !279 already established.
- Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`.
- Do not touch `.mcp.json` by hand — it may only change as `sync.mjs`'s regenerated output.
- Do not touch `feature/T475-codex-platform-integration` (separate, untouched, disclosed-stale
  branch with its own independent task numbering — see "Numbering note" below).

## Expected outputs

- `implementation/knowledge/mcp/servers.yaml` — new `hindsight` and `cwso` entries, correctly
  tagged, with an env/URL/headers templating shape `sync.mjs` actually supports.
- `implementation/scripts/sync.mjs` — `emitMcp()` extended to emit `headers` (where the target
  format supports it) and to template `url` the same way `env` values are already templated.
- All 7 (or 8, if `feature/T475-codex-platform-integration`'s Codex work has merged to `develop` by
  the time this is picked up — re-check `develop` for `.codex/config.toml` before assuming still 7)
  platform projection files regenerated via `node implementation/scripts/sync.mjs`.
- `tests/functional/test_mcp_secret_guard.py` extended so `find_literal_env_values()` (or an
  equivalent new check) also walks `headers` blocks, not only `env` blocks.
- `docs/artifacts/mcp-platform-contract-v1.md` updated: server count (15 → 17), tag lists, and — if
  any platform cannot represent `headers` — an explicit disclosed limitation per platform, not a
  silent gap.
- Optionally, an ADR if the design owner judges the header/URL-templating schema extension
  significant enough to warrant one (design owner's call, not mandated here).

## Acceptance criteria

1. `hindsight` and `cwso` appear in `servers.yaml` with correct tags, no literal secrets, and a
   templating shape `sync.mjs` genuinely implements (not aspirational YAML the generator ignores).
2. `node implementation/scripts/sync.mjs --check` is clean (no drift) across all platforms after
   regeneration.
3. The regenerated `.mcp.json` (claude-code) content for `hindsight`/`cwso` matches the current,
   already-merged `origin/develop` `.mcp.json` content for those two entries byte-for-byte — this
   task must not silently change Claude Code's already-correct, already-merged behavior.
4. `hindsight`/`cwso` appear correctly (per whatever shape each target platform's format branch
   newly supports) in every other platform's regenerated projection — verified directly, not
   asserted from the diff alone.
5. `python3 -m pytest tests/functional/test_mcp_secret_guard.py tests/functional/
   test_mcp_schema_validation.py tests/functional/test_mcp_platform_conformance.py -v` all pass,
   including the newly extended `headers`-coverage case in the secret guard.
6. `docs/artifacts/mcp-platform-contract-v1.md` reflects the new 17-server registry accurately.
7. Full `python3 tests/run.py` shows no regressions against the pre-task baseline.
8. Standard branch-and-MR discipline (per `AGENTS.md`'s Git Workflow rules): `agent/<owner>/T483`
   branch(es) from `develop`, MR(s) referencing T483, orchestrator independent verification before
   merge, no self-merge.

## Numbering note (disclosed, not silently resolved)

`feature/T475-codex-platform-integration` — the separate, untouched branch this and prior sessions
were explicitly told never to touch — has its own independent task-ID lineage that has already used
`T476` through `T482` (confirmed by listing `docs/tasks/task-T4*.md` in that branch's working tree
this session; `T476` there is `"Codex manifest and sync transforms," status: done`, unrelated to
this task). `origin/develop`'s own real ledger only reaches `T475`. This task is numbered `T483` —
deliberately past both lineages' current maximum — specifically to avoid a second collision on top
of the one the prior handoff already flagged as "a real ledger merge conflict overdue" for that
branch. Whoever eventually reconciles that branch into `develop` will need to renumber one lineage's
`T47x`-and-up IDs; this task's `T483` was chosen with that future renumbering in mind, not because
`T476` was unavailable in `develop`'s own ledger.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`) per `AGENTS.md`. Max 2 retries before escalating to the
orchestrator/user.
