# plan-068 — T517: Claude Code's env-placeholder syntax in generated MCP config

**Status: scoped 2026-09-24, awaiting approval to dispatch.**
Based on: `docs/artifacts/mcp-header-url-templating-design-v1.md`, `implementation/knowledge/mcp/servers.yaml`.

## 0. Origin

Found from a user report that the `hindsight` MCP server was unavailable. It is not a configuration
mistake on the user's side: the environment variable is set correctly and the generated config is
wrong. The defect is in this repository's own generator, in shipped output.

## 1. The defect

`sync.mjs`'s `emitMcp()` renders env references per platform. The `claude-code` branch passes
`${env:VAR}` — VS Code's placeholder syntax. Claude Code expands `${VAR}` / `${VAR:-default}` from
the live process environment and does not recognise the `env:` form, so `.mcp.json` ships literal
placeholder text.

The design is otherwise sound: `mapTemplatedValue()` already takes the template as a parameter
documented as *"the platform's own placeholder pattern"*, and `opencode` already passes a different
one. One constant is wrong, not the architecture.

## 2. Severity: the visible half is the smaller half

Two servers fail loudly (`hindsight`, `cwso` — both use `fromEnv` in `url`, which produces an invalid
URL at connect time). Three more fail **silently**: `gitlab`, `brave` and `toolradar` use `fromEnv`
in `env`, so the process starts, the client reports a healthy connection, and the literal string
`${env:BRAVE_API_KEY}` is handed over as a credential. The failure surfaces later as an
authentication error from the upstream service, with nothing pointing back at the config.

Three of the five are `core`-tagged, so they are emitted into **every** project that installs this
platform — this is not limited to this repository.

`P1` is assigned on that basis: shipped, user-visible, affects every downstream install of one
platform, and silently corrupts credentials. It is not `P0` only because a workaround exists (write
literal values into the projection) and because it blocks nothing on the v8 roadmap's critical path.

## 3. Why the test suite did not catch it

Because the suite agrees with the bug. `test_mcp_secret_guard.py:19` lists `claude-code` among the
`${env:VAR}` platforms and `test_platform_projections.py:82` defaults to that template. Both trace
to `mcp-header-url-templating-design-v1.md`, which specifies the template — and whose line 14 names
`.mcp.json` as *"the exact claude-code target shape for `hindsight`/`cwso`"*, the two servers now
broken. The design document is the origin of the defect, and the tests faithfully encode it.

This is the general hazard of generated output: a projection is only ever compared against what the
generator was told to produce, never against what the consumer actually accepts. Nothing in the
pipeline reads `.mcp.json` the way Claude Code reads it. The brief therefore makes a **live
reconnect** the decisive acceptance criterion; a green suite would prove only that the generator
still matches the tests.

## 4. Scope discipline

Six emitters exist (`vscode` — also used by `github`; `cursor` — also used by `pi`; `gemini`;
`opencode`; `claude-code`; `cline`). **Only `claude-code` is proven wrong**, and `${env:VAR}` is
correct for at least VS Code, so the brief explicitly forbids "fixing" the others to match.
Generalising one verified bug across six platforms is how a contained fix becomes an outage. If
evidence emerges that another platform is also wrong, it gets its own task.

Likewise out of scope: the `CONNECTION_CLOSED` failures of `git`, `github`, `filesystem`, `supabase`,
`docker` and `postgresql` — a different symptom with no established relationship. The one connected
hypothesis, that `gitlab` exits at startup because it receives a literal placeholder as its token, is
stated in the brief **as a hypothesis to test and report**, not as a finding.

## 5. Confidence, stated honestly in the brief

Two halves with different evidential weight:

- **`${env:VAR}` is not expanded** — proven. Two servers fail with the variable demonstrably set, and
  servers with literal URLs in the same file connect.
- **`${VAR}` is the right replacement** — documented behaviour plus consistent controls, but not yet
  demonstrated in this repository.

The brief says so and assigns the implementer the job of demonstrating the second half, rather than
presenting the whole thing as settled. If a live reconnect contradicts it, that is a design question
and the brief directs the implementer to stop rather than improvise.

## 6. Artifact versioning

`mcp-header-url-templating-design-v1.md` declares itself immutable and `AGENTS.md` requires revisions
to create new versions. A `-v2` is required, with v1 keeping only a supersession banner. `T516` hit
exactly this rule — its brief said "update §3.5 of `…-v1.md`" and the implementer correctly refused,
producing a v2 and flagging the deviation. That handling is the pattern to copy, and this brief says
so up front so the same correction does not have to be rediscovered.
