# T519 — Correct the two documents still stating the pre-`T517` placeholder syntax

**ID:** T519
**Owner:** Technical Writer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** —
**Created:** 2026-09-25
**Completed:** —
**Based on:** docs/plans/plan-069-t518-t519-carried-defects.md

> **You have no shell.** The Technical Writer agent type has no `Bash`, `Grep` or `Glob`. Do not
> attempt `git` commands, and do not treat that as a blocker: **write the files, leave them
> uncommitted, and report their paths.** The orchestrator commits and opens the MR. This is stated
> up front because a previous brief told a shell-less agent to commit and push, which cost a cycle.

## 1. Objective

`T517` changed the placeholder syntax emitted into the `claude-code` MCP projection from
`${env:VAR}` to `${VAR}`. Two documents still state the old syntax and are now wrong. Correct them.

## 2. The two sites

**A. `implementation/SECURITY.md` line 25** currently reads:

> Servers in `knowledge/mcp/servers.yaml` reference credentials via `${env:VAR}` (or `{env:VAR}` for
> Opencode). The sync engine emits these placeholders verbatim — secrets are never written to
> generated files.

Now incomplete: `claude-code` uses `${VAR}`. **The security claim itself is still true** — placeholders
are emitted verbatim and no secret is written to a generated file; that was independently verified
during `T517`. Only the enumeration of syntaxes is stale. Correct the enumeration without weakening
or restating the guarantee.

**B. `docs/artifacts/mcp-platform-contract-v1.md` line 87** currently reads:

> (`${env:VAR}` for claude-code/cline/cursor/gemini/vscode, `{env:VAR}` for opencode) via

Now wrong for `claude-code`, which must move out of that list into its own `${VAR}` case.

## 3. The versioning constraint — this is the substantive part

`mcp-platform-contract-v1.md` is a `-v1` artifact. `AGENTS.md` § Artifact Versioning states
revisions create new versions and never overwrite. So **B requires producing
`mcp-platform-contract-v2.md`**, with `-v1` keeping only a supersession banner.

Two worked precedents exist in this repository; follow their shape rather than inventing one:

- `docs/artifacts/maturity-promotion-criteria-v2.md` (`T516`)
- `docs/artifacts/mcp-header-url-templating-design-v2.md` (`T517`)

Both carry v1 forward verbatim except the metadata block, a "Changes from v1" section, the corrected
passages, and a `Consumed by` entry; both leave v1 with a short supersession block and nothing else.
In both cases the task's brief had said "update the v1 document" and the implementer correctly
refused. **`SECURITY.md` is not a versioned artifact** — edit it in place.

## 4. Source of truth

`docs/artifacts/mcp-header-url-templating-design-v2.md` is authoritative on the corrected syntax,
especially its §3 rendering rule and §9 evidence. Read it before writing. The short version, which
you should state accurately rather than paraphrase loosely:

| Platform(s) | Placeholder |
|---|---|
| `claude-code` | `${VAR}` (also `${VAR:-default}`) |
| `vscode`, `cursor` (and `pi`), `gemini`, `cline` | `${env:VAR}` |
| `opencode` | `{env:VAR}` |

Verify that table against `implementation/scripts/sync.mjs`'s `emitMcp()` by reading it — do not take
it from this brief. If the code and this table disagree, the code wins and the disagreement is a
finding worth reporting.

## 5. Scope

**In scope:** `implementation/SECURITY.md`, a new `docs/artifacts/mcp-platform-contract-v2.md`, and a
supersession banner on `-v1`.

**Out of scope:** `sync.mjs` and any generated projection — the code is already correct, only the
prose is stale. Any other document not named here; if you find a third site with the same staleness,
**report it, do not fix it** — silent scope growth in a documentation task is how unreviewed changes
land.

## 6. Acceptance criteria

- [ ] `SECURITY.md` line 25 correctly enumerates all three placeholder forms, with the security
      guarantee intact and not reworded into something weaker.
- [ ] `mcp-platform-contract-v2.md` exists, carries v1 forward faithfully, and has a "Changes from
      v1" section naming exactly what moved.
- [ ] `-v1` modified **only** by a supersession banner — no other line touched.
- [ ] The platform/placeholder table verified against `sync.mjs` rather than copied from this brief.
- [ ] No code, no generated file, and no other document changed.
- [ ] Any additional stale site found is reported, not fixed.

## 7. Hand-back

Leave your files uncommitted in the working tree and report: every path you created or modified, the
`sync.mjs` verification result, and anything you found but did not fix. Do not attempt git.

## 8. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate. "I have no shell" is **not** a blocker
for this task — §7 is the intended path.
