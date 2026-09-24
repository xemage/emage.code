# T517 — Emit Claude Code's own env-placeholder syntax in the generated MCP config

**ID:** T517
**Owner:** DevOps Engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-09-24
**Completed:** —
**Based on:** docs/plans/plan-068-t517-claude-code-mcp-placeholder-syntax.md

> **`**Affects:**` is `—` deliberately.** This is a defect in a build script, not in any registry
> component, so it indicts no agent, command, instruction or skill. The field is declared anyway for
> forward-compatibility with `T516`; if `T516` has not merged when you read this, the field is inert
> and harmless.

## 1. Objective

`implementation/scripts/sync.mjs` renders env-variable references into each platform's generated MCP
config using a per-platform placeholder template. The `claude-code` branch passes VS Code's
`${env:VAR}` template. Claude Code does not expand that form — it expands `${VAR}` and
`${VAR:-default}` from the live process environment — so the generated `.mcp.json` ships literal,
unexpanded placeholder strings.

Fix the emitted syntax, regenerate the projections, and correct the tests and design artifact that
currently encode the wrong value.

## 2. Evidence

Observed in a live session on this repository, with `HINDSIGHT_MCP_URL` genuinely set in the
environment (48 chars, `http` scheme):

```
hindsight (INVALID_CONFIG): "'url' is not a valid URL. Update the server's config and reconnect."
cwso      (INVALID_CONFIG): "'url' is not a valid URL. Update the server's config and reconnect."
```

`.mcp.json` contains `"url": "${env:HINDSIGHT_MCP_URL}"`. The client received that string literally.

A natural experiment across the same file isolates the variable — one factor, controls on both sides:

| Servers | `${env:}` appears in | Result |
|---|---|---|
| `brave`, `toolradar` | `env` | connects |
| `context7`, `hf-mcp-server` | nowhere (literal URL) | connects |
| `hindsight`, `cwso` | **`url`** | **fails, URL invalid** |

The offending line is `sync.mjs:379` (and `:380`, `:383` for `headers` and `env`):

```js
if (format === 'claude-code') {
  mcpServers[name] = { type: 'http', url: mapTemplatedValue(s.url, '${env:VAR}') };
```

The mechanism is already per-platform and correct in design — `mapTemplatedValue`'s own contract
comment says *"the platform's own placeholder pattern"*, and the `opencode` branch already passes a
different one (`{env:VAR}`, single braces). Only the `claude-code` constant is wrong. This should be
a small change.

## 3. Blast radius — larger than the two visible failures

Five servers in `servers.yaml` use `fromEnv`, and all five are mis-rendered for this platform:

| Server | `fromEnv` in | Tag | Symptom |
|---|---|---|---|
| `hindsight` | `url` | core | hard fail at connect, visible |
| `cwso` | `url`, `headers` | extended | hard fail at connect, visible |
| `gitlab` | `env` | core | **silent** — literal string passed as a credential |
| `brave` | `env` | core | **silent** |
| `toolradar` | `env` | extended | **silent** |

The `env` cases are the more dangerous half: the server process starts, the client reports a healthy
connection, and the failure only appears later as an authentication error from the upstream service.
Three of the five are `core`, i.e. emitted into **every** project that installs this platform.

**Hypothesis worth testing, not a finding:** `gitlab` currently fails with `CONNECTION_CLOSED` rather
than an auth error. It is plausible that it receives the literal placeholder as its token and exits
during startup. Check it; if true, say so. If `gitlab` still fails after the fix, that is a separate
defect and should be reported as such, not folded into this task.

## 4. Why it survived

Source, generator and tests all agree with each other and all disagree with Claude Code:

- `docs/artifacts/mcp-header-url-templating-design-v1.md` specifies the `${env:VAR}` template for
  this branch, and its line 14 names `.mcp.json` as *"the exact claude-code target shape for
  `hindsight`/`cwso`"* — the two servers now broken. This document is the origin of the defect.
- `tests/functional/test_mcp_secret_guard.py:19` lists `claude-code` among the `${env:VAR}` platforms.
- `tests/functional/test_platform_projections.py:82` defaults to that template.

So the test suite pins the bug. Expect to change tests; that is correct here, not a smell — but see
§6.2 before you touch them.

## 5. Scope

**In scope:** the `claude-code` branch of `emitMcp()` in `sync.mjs`; regeneration of the affected
projection(s); the two test files above; a new version of the design artifact.

**Out of scope:**

- **The other five emitters.** `vscode`, `cursor` (also used by `pi`), `gemini`, `opencode` and
  `cline` are *not* proven wrong and `${env:VAR}` is correct for at least VS Code. Do not "fix" them
  to match. If you find positive evidence that another platform is also wrong, report it as a finding
  and let it be scoped separately — changing six platforms on the strength of one verified bug is how
  a small fix becomes an outage.
- Any `servers.yaml` entry. The source data is correct; only its rendering is wrong.
- The `CONNECTION_CLOSED` failures of `git`, `github`, `filesystem`, `supabase`, `docker`,
  `postgresql`. Different symptom, unproven relationship.

## 6. Constraints

1. **Do not hand-edit generated files.** `.mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json` and the
   rest are projections; per `AGENTS.md` they are produced by the sync script. Fix the generator and
   regenerate. A hand-edited projection is reverted by the next sync and is not a fix.
2. **The design artifact is immutable.** `mcp-header-url-templating-design-v1.md` declares itself so,
   and `AGENTS.md` says revisions create new versions rather than overwriting. Produce a `-v2` and
   leave v1 with a supersession banner. (`T516` hit this same rule and its handling is the pattern to
   copy.)
3. **Do not weaken a test to make it pass.** The two tests encode a wrong expectation and must be
   corrected to the right one — that is different from relaxing an assertion. The secret-guard test
   exists to prove no secret is ever written into a projection; that guarantee must still hold
   afterwards, and you should state how you confirmed it.
4. Do not change any component's `maturity:` value. Do not modify `tests/golden/**` or
   `scripts/scorecard.py` — both are protected paths and this task is not authorized to write there.

## 7. Verification

The mechanical checks are necessary but not sufficient:

```
python3 implementation/scripts/check-maturity.py     # 0 failing
python3 docs/tasks/validate-tasks.py                 # PASS
python3 -m pytest tests/functional -q                # no reduction in test count
node implementation/scripts/sync.mjs --check         # or the repo's own drift gate
```

**The decisive check is a real reconnect.** A green suite only proves the generator emits what the
tests now expect. Confirm the emitted `.mcp.json` actually resolves: with `HINDSIGHT_MCP_URL` set,
the `url` must expand to a real URL, and the server must connect where it previously reported
`INVALID_CONFIG`. If you cannot complete a live reconnect in your environment, say so plainly and
report what you *did* verify — do not describe a syntax change as a confirmed fix on the strength of
unit tests alone.

**Honest confidence split, so you test the weak half rather than assuming it:** that `${env:VAR}` is
not expanded is *proven* by the two failing servers with the variable set. That `${VAR}` is the right
replacement rests on documentation plus the working literal-URL controls — it is well-supported but
not yet demonstrated in this repo. Your job includes demonstrating it.

## 8. Acceptance criteria

- [ ] The `claude-code` emitter renders the placeholder form Claude Code actually expands, for `url`,
      `headers` and `env` alike.
- [ ] Generated projections regenerated from the fixed generator; no projection hand-edited.
- [ ] A live reconnect is demonstrated, or its absence is explicitly reported.
- [ ] The two tests assert the corrected syntax, and the secret-guard property still holds.
- [ ] Design artifact `-v2` created; v1 left intact apart from a supersession banner.
- [ ] No other platform's emitter changed, or any change to one is separately justified by evidence.
- [ ] `gitlab`'s post-fix behaviour reported (recovered / still failing / not determinable).
- [ ] No `maturity:` value changed; no protected path written.

## 9. Working agreement

Branch from `develop` in a worktree, named per the agent-worktree convention in the Git Workflow
rules under `.claude/rules/`. Do not work in the primary checkout. Conventional Commits. Do not merge
your own branch and do not push to `develop` or `main` — hand the branch back and the orchestrator
opens the MR.

## 10. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external`, with severity
`critical` | `major` | `minor`. Max 2 retries, then escalate.

If a live reconnect turns out to contradict §7's expectation — for example if `${VAR}` is also not
expanded in the `url` field — **stop and report that**. It would mean the correct fix is a literal
URL or a different mechanism entirely, which is a design decision, not something to improvise inside
this task.
