# MCP Header/URL Templating Design — v2

> Filename: `mcp-header-url-templating-design-v2.md`. Immutable once produced; revisions bump `<N>`.

## v2 metadata
- **Producer agent**: devops-engineer
- **Task**: T517
- **Created**: 2026-09-25
- **Based on**: `docs/artifacts/mcp-header-url-templating-design-v1.md` (T483 — carried forward
  verbatim except for the passages listed in "Changes from v1" below, the new §9, and this
  metadata block);
  `docs/tasks/task-T517.md`; `docs/plans/plan-068-t517-claude-code-mcp-placeholder-syntax.md`;
  Claude Code's own MCP documentation, §"Environment variable expansion in `.mcp.json`"
  (<https://code.claude.com/docs/en/mcp>, read 2026-09-25). v1's own basis is unchanged and still
  applies — it is reproduced verbatim in the `**Based on:**` block below.
- **Supersedes**: `mcp-header-url-templating-design-v1.md`

## Changes from v1 (the only substantive change is the `claude-code` placeholder template)

v1 specified `${env:VAR}` — VS Code's placeholder syntax — for the `claude-code` branch of
`emitMcp()`. **Claude Code does not recognise that form.** It expands `${VAR}` and
`${VAR:-default}` from the live process environment, in `command`, `args`, `env`, `url` and
`headers` alike, and passes any other brace expression through as literal text. The generated
`.mcp.json` therefore shipped unexpanded placeholder strings: `hindsight` and `cwso` failed at
connect with `'url' is not a valid URL`, and `gitlab`/`brave`/`toolradar` received the literal
placeholder text where a credential was intended.

v2 changes that one constant to `${VAR}`. No other platform's template changes: `${env:VAR}` is
correct for at least VS Code, and no evidence was found that `cursor`, `pi`, `gemini`, `opencode`
or `cline` is also wrong. The architecture is unchanged — `mapTemplatedValue()` already took the
template as a per-platform parameter, and `opencode` already passed a different one.

| Passage | v1 | v2 |
|---|---|---|
| §3 rendering rule + `wrap` note | two placeholder families | three families; `claude-code` renders `"Bearer ${CWSO_BEARER_TOKEN}"` |
| §5.1 `mapTemplatedValue()` doc comment | "`${env:VAR}` or `{env:VAR}`" | names all three families and their platforms |
| §5.2 `claude-code` branch | `'${env:VAR}'` | `'${VAR}'`, and the `env` (stdio) call site is shown too |
| §5.3 evidence table, `claude-code` row | "Empirically verified" from the hand-added `.mcp.json` | corrected: that entry verified the *field shape*, not the placeholder syntax |
| §6 hand-trace | traced against `${env:…}` output | traced per placeholder family, with the `claude-code` column corrected |
| §7 QA guidance | two placeholder families in the guard regex | three families, with the non-weakening argument |
| §9 (new) | — | T517 evidence: documentation, live differential probe, and the `gitlab` startup probe |

Everything else below is v1 verbatim, including the `**Status:**`/`**Owner:**`/`**Task:**`/
`**Based on:**` block and the "Ratification note" section — those describe v1's own authorship and
ratification pass and are carried forward unchanged for provenance, not re-asserted by v2.

---

**Status:** Final (ratified this session — independently re-verified, one citation correction
applied; see "Ratification note" below).
**Owner:** solution-architect
**Task:** T483
**Based on:**
- `docs/tasks/task-T483.md` (full brief, read in full this session)
- `docs/plans/plan-042-t483-mcp-hindsight-cwso-followup.md` (backing plan, read in full)
- `implementation/knowledge/mcp/servers.yaml` (canonical registry, 15 entries, read in full)
- `implementation/scripts/sync.mjs` — `parseServersYaml()` (lines 170–238), `emitMcp()`/`mapEnv()`
  (lines 293–388), read in full this session (not just the ~293–388 range the brief pointed at —
  see §0, a finding beyond the brief's original framing)
- Root `.mcp.json` (read directly, the exact claude-code target shape for `hindsight`/`cwso`)
- `.vscode/mcp.json` (read directly — the existing dest-only, hand-added `cwso` entry and its
  `inputs` array)
- `tests/functional/test_mcp_secret_guard.py` (read in full)
- `tests/functional/test_mcp_schema_validation.py` (read in full — the two vendored schemas'
  documented scope: gemini and opencode only)
- `docs/artifacts/mcp-platform-contract-v1.md` (T420, read in full — §3.1 wire-shape table, §4
  merge-target/provenance discussion)
- `scripts/merge-mcp-json.py` (read in full — `merge_json`'s recursive leaf-wins-on-source rule)
- `implementation/platforms/github.json` (tags: `["core"]` only, confirmed)
- `docs/artifacts/role-mapping-cwso-v1.md` and
  `implementation/knowledge/skills/cwso-awareness/SKILL.md` (cwso is worker/orchestrator-tier
  specialized tooling, not a universal capability)
- `docs/checkpoints/handoff-725b7925-6b66-47d2-b05b-b7c2e25a3bfb.md` (cwso's last known
  `AUTH_HEADER_REJECTED` 403 status; hindsight's real operational role as a durable, shared,
  network-hosted memory service at `http://10.10.160.11:8888/mcp/emage.memory.coding`)
- `AGENTS.md` §"MCP Servers" (cross-checked, not treated as primary source)

**Consumers:** `backend-developer` (implements `servers.yaml` + `sync.mjs` changes),
`qa-engineer` (extends `tests/functional/test_mcp_secret_guard.py` for `headers` coverage).

---

## Ratification note (this session)

This is a review/ratification pass on the author's own prior draft, not a from-scratch
re-investigation. Independently re-read, in full, in this worktree, on top of `origin/develop`:
`implementation/scripts/sync.mjs` (all of `parseServersYaml`, `parseInlineObject`, `emitMcp`,
`mapEnv`), `implementation/knowledge/mcp/servers.yaml` (all 15 entries), root `.mcp.json`,
`.vscode/mcp.json`, `implementation/platforms/github.json`, `implementation/platforms/pi.json`,
`scripts/merge-mcp-json.py`, `tests/functional/test_mcp_secret_guard.py`,
`tests/functional/test_mcp_schema_validation.py`, and — going one level past the draft's own
citation — the two vendored schema fixtures (`tests/fixtures/mcp-schemas/gemini-cli-settings
.schema.json`, `.../opencode-config.schema.json`) at the specific line ranges the draft cites, to
hand-verify the `headers` property claims rather than take the draft's own line numbers on faith.

**Every claim in §0–§6 checked out against the real, current source and is ratified as originally
written**, with one correction:

- **Correction (minor, citation-only, not a design defect):** §5.3's evidence table cites the
  opencode `headers` property at "lines ~543/660." Direct inspection found line 660 is correct and
  load-bearing — it sits inside `$defs.mcp`'s `McpRemoteConfig` (`{type: "remote", url, headers,
  ...}`), the exact shape this design's `opencode` branch emits. Line ~543, however, is a
  **different, unrelated `headers` property** inside a model-provider config schema block (sibling
  keys `npm`/`api`/`variants`/`cost`/`limit`/`modalities` — a model-catalog shape, not
  `$defs.mcp`), reached by matching a bare "headers" grep hit rather than one scoped to
  `$defs.mcp`. It does not evidence MCP header support and should not have been cited. This does
  **not** change the row's `Schema-verified` classification — line 660 alone is a correct, precise,
  sufficient, independently confirmed citation for opencode's official schema defining `headers` on
  the remote-MCP-server shape. Fixed in §5.3 below (citation now reads "line ~660" only).

No other correction was needed. In particular, independently confirmed byte-for-byte, not just
re-asserted: `parseServersYaml()`'s `env`-only block-key check and absent scalar-level inline-object
branch (§0); the exact `mapEnv()` body and all 6 `emitMcp()` format branches (§5.1–5.2) as the real,
current, unmodified functions being extended; `github.json`'s `"tags": ["core"]`-only manifest and
`pi.json`'s `"format": "cursor"` (§2, §5.2); the real `.vscode/mcp.json` dest-only `cwso` entry using
`${input:cwso_jwt_token}` plus a `password: true` `inputs` array entry (§2); `merge-mcp-json.py`'s
`merge_json` leaf-wins-on-source recursion (§2); the real root `.mcp.json` `hindsight`/`cwso` shapes,
confirmed byte-identical to this design's hand-traced output (§6); and the exact quoted handoff
sentence about Hindsight's operational role (§1).

---

## 0. A finding beyond the brief's original framing: `parseServersYaml()` also needs extending

The brief's investigation (and its decision list, point 5) scopes the required code change to
`emitMcp()`/`mapEnv()`. Reading `sync.mjs` in full surfaced a prerequisite the brief did not
name: **`servers.yaml` is not parsed by a real YAML library — it is parsed by a hand-rolled,
regex-based parser (`parseServersYaml()`, lines 170–225, plus `parseInlineObject()`, lines
227–238) that only understands a fixed, narrow grammar.** Specifically, today:

- The only block-typed (multi-line, nested) key it recognizes at all is `env:` (hardcoded literal
  string match, `key === 'env'`, line 208). A new `headers:` block is **not** parsed by the
  current code — it would silently fall through to the scalar branch and corrupt the data.
- A 4-space top-level key's value (`url:`, `command:`, `transport:`, etc.) is only ever parsed as
  a scalar (`parseScalar(stripQuotes(rest))`) or an array (`[...]`). There is **no** branch that
  recognizes an inline object (`{ fromEnv: ... }`) at this level — only 6-space sub-keys *inside*
  an already-open `env:` block get that treatment (via `parseInlineObject`, line 197).

This means the schema extension this design proposes (an env-templated `url:` scalar, and a
`headers:` block) is unparseable by the current `sync.mjs` without a parser change, independent of
and prior to any `emitMcp()`/`mapEnv()` change. §5 below specifies both changes together, since
neither is useful without the other.

---

## 1. Decision: `hindsight` tag — `core`, and it is **complementary** to `memory`, not a replacement

**Tag: `core`.**

**Complementary, not a replacement — stated explicitly, not dodged:**

- Both `hindsight` and `memory` (`@modelcontextprotocol/server-memory`) currently coexist as
  separate top-level keys in the live, hand-merged root `.mcp.json` (confirmed by direct read).
  No task, plan, or artifact in this repo's evidence base proposes deprecating `memory`.
- They are operationally different in kind, not just in name:
  - `memory` is a `transport: stdio` server, spawned per-session via `npx
    @modelcontextprotocol/server-memory`, with **no** persistence path or mounted volume
    configured anywhere in `servers.yaml`. Absent that configuration, its knowledge graph does not
    outlive the local process/session — "Persistent knowledge graph" in `AGENTS.md`'s core-server
    table is a label describing the *tool's* nominal capability, not a verified claim about this
    repo's actual deployment of it.
  - `hindsight` is a `transport: remote` server backed by a real, independently-running, shared
    network service. Per `handoff-725b7925-6b66-47d2-b05b-b7c2e25a3bfb.md`: "Hindsight MCP
    (`http://10.10.160.11:8888/mcp/emage.memory.coding`) worked throughout this session and holds
    durable memory of exactly this kind of operational fact — recall from it before assuming
    anything here is still accurate." That is direct, recent, operational evidence of durable,
    cross-session, cross-worktree memory — a different infrastructure tier than a per-process
    stdio server.
- Given both are already wired into production config and nothing in this repo's record directs
  sunsetting `memory`, this design keeps both and tags `hindsight` `core`, parallel to `memory`'s
  existing `core` tag (same rationale the task brief itself proposed).
- **Not decided here, explicitly out of scope:** whether `memory` should eventually be deprecated
  once `hindsight`'s role is fully documented org-wide. That is a product/operational decision,
  not a schema-extension design decision, and this task's evidence base (one handoff note) is not
  sufficient to make that call. Flagged as a candidate follow-up, not resolved here.

## 2. Decision: `cwso` tag — `extended` (hard constraint, confirmed from `merge-mcp-json.py`)

**Tag: `extended`.** Two independent, both-sufficient reasons:

**(a) Hard regression-avoidance constraint (the decisive one).** `implementation/platforms/
github.json` scopes its `mcp` block to `"tags": ["core"]` only (confirmed by direct read). If
`cwso` were tagged `core`, `sync.mjs` would start emitting a `cwso` key into the generated
`implementation/.vscode/mcp.json`, which `scripts/install.sh --update` then merges into the real,
single-file `.vscode/mcp.json` via `scripts/merge-mcp-json.py`. Reading that script's `merge_json`
function directly: "Keys present in both `dest` and `source`, where at least one value is not an
object (a scalar or array leaf, e.g. `url`, `type`, `args`, `env`): `source` wins." The existing
dest-only `.vscode/mcp.json` `cwso` entry uses a literal local IP URL and, critically, VS Code's
native secure-prompt mechanism (`"Authorization": "Bearer ${input:cwso_jwt_token}"`, backed by a
top-level `inputs` array entry with `"password": true`) — a materially nicer UX than a plain env
var, since VS Code prompts and stores it via its own secret input flow rather than requiring the
user to export an env var. If `cwso` became a generator-owned key, every leaf under
`servers.cwso` (`url`, `type`, and, once this design lands, `headers.Authorization`/
`headers.Origin`) is present in both dest and source and is a scalar — so `source` (the generic
`${env:CWSO_BEARER_TOKEN}` shape) would silently overwrite the dest-only `${input:...}` shape on
the next `--update`, destroying already-accepted, working, more secure content. Tagging `cwso`
`extended` means the `github` platform's `core`-only manifest never includes it in `source` at
all, so this key is never touched by the merge (falls under "keys present only in `dest`:
preserved as-is").
- Note for precision: `.mcp.json` (claude-code) is *also* a merge target, but is unaffected either
  way here, because claude-code's manifest already includes both `core` and `extended` tags (all
  15 servers today), and its dest content for `hindsight`/`cwso` already matches what this design
  produces byte-for-byte (see §6) — there is no divergent dest-only content to protect there. The
  regression risk is specific to `github`/`.vscode/mcp.json`, because that is the one platform
  manifest that filters by tag.

**(b) Audience/role-tier fit (secondary, also true).** Per `docs/artifacts/role-mapping-cwso-v1.md`
and the `cwso-awareness` skill, `cwso` gates its 11 tools behind a `worker`/`orchestrator`
permission-tier split that only a subset of emage.code agent roles hold (`read`-tier roles like
`tech-lead`, `security-engineer`, `product-owner`, `solution-architect` do not use it at all). It
is specialized orchestration-coordination infrastructure for Pattern A concurrent editing, not a
capability every agent/platform needs by default — closer in shape to `supabase`/`docker`/
`postgresql` (`extended`, opt-in, infra-specific) than to `gitlab`/`memory` (`core`, universally
useful). This independently supports `extended`, but (a) above is the hard constraint that makes
`extended` mandatory regardless of this secondary framing.

## 3. Decision: `headers` schema shape in `servers.yaml`

Introduce a **"templated value" spec** — a small object shape reused identically for `url` (§4)
and for each individual `headers.<Name>` entry:

```yaml
# Pure single-env-var substitution (no wrapping literal text) — reuses the exact object shape
# already established by servers.yaml's existing env: sub-entries (e.g. GITLAB_API_URL: { fromEnv: GITLAB_API_URL }):
SomeHeader: { fromEnv: SOME_ENV_VAR }

# Env-var substitution embedded inside fixed literal text (e.g. "Bearer <token>") — adds one new
# optional key, `wrap`, to the same shape. `wrap`'s value is an author-facing literal string
# containing exactly one `{VAR}` placeholder token (single braces, no `$`, chosen deliberately
# distinct from all three platform placeholder syntaxes — `${env:VAR}`, `{env:VAR}` and, since
# T517, claude-code's `${VAR}` — so it can never be confused with, or accidentally matched by,
# the per-platform substitution pass in §5):
SomeHeader: { fromEnv: SOME_ENV_VAR, secret: true, wrap: "Bearer {VAR}" }
```

Rendering rule (see §5 for the exact function): compute the platform's own rendered env
reference first (`${env:SOME_ENV_VAR}`, `{env:SOME_ENV_VAR}` or — for `claude-code`, per T517 —
`${SOME_ENV_VAR}`, depending on target format), then, if `wrap` is present, substitute that
rendered reference into `wrap`'s `{VAR}` slot; if `wrap` is absent, use the rendered reference
directly. This is why `Origin: { fromEnv: CWSO_ORIGIN }` (no `wrap`) renders to exactly
`"${env:CWSO_ORIGIN}"` on the VS Code-family platforms and to `"${CWSO_ORIGIN}"` on `claude-code`,
while `Authorization: { fromEnv: CWSO_BEARER_TOKEN, secret: true, wrap: "Bearer {VAR}" }` renders
to exactly `"Bearer ${env:CWSO_BEARER_TOKEN}"` and `"Bearer ${CWSO_BEARER_TOKEN}"` respectively —
verified by hand-tracing in §6. (v1 asserted the `${env:…}` rendering matched the real target
`.mcp.json` shape, input #4. That was the defect: input #4 was a hand-written file that had never
been read by a running Claude Code client, so it attested to the *field shape* only. See §9.)

`secret: true`/`false` is carried through as inert authorial/audit metadata, exactly matching how
the pre-existing `env:` block's `secret` flag already works today (it is not read anywhere in
`mapEnv()`/`emitMcp()` currently, only documentary). §7 explains why this metadata still matters
for the QA follow-up even though `sync.mjs` itself does not branch on it.

A `headers:` block itself is a new top-level, per-server key, structurally parallel to the
existing `env:` block (same 4-space-key/6-space-sub-key nesting), containing one or more `Name: {
templated-value-spec }` entries. A plain literal string is also a valid header value (e.g. a
future static `"Content-Type": "application/json"` header, with no env dependency at all) —
`mapTemplatedValue()` (§5) falls back to returning any non-object value unchanged, so this is
supported for free without extra schema.

## 4. Decision: `url` templating shape for `transport: remote` servers

Reuse the **same templated-value spec** from §3, applied to the scalar `url:` field directly (no
`wrap` needed for either of this task's two servers, since both URLs are pure single-env-var
substitutions):

```yaml
url: { fromEnv: HINDSIGHT_MCP_URL }
```

This is a strict superset of the current shape — `mapTemplatedValue()` (§5) treats any plain
string `url` value (e.g. `context7`'s `"https://mcp.context7.com/mcp"`,
`hf-mcp-server`'s `"https://huggingface.co/mcp?login"`) as a literal and returns it unchanged, so
**both existing `remote`-tagged entries need zero changes and their generated output is
byte-identical to today.** This is a load-bearing constraint: the brief is explicit that this
schema extension must not disturb `context7`/`hf-mcp-server`, and this design achieves that by
construction (same function, object-vs-literal branch), not by special-casing.

## 5. Decision: `emitMcp()`/`mapEnv()` (and `parseServersYaml()`) extension design

### 5.0 Parser change (prerequisite, see §0)

In `parseServersYaml()`:

1. **Generalize the single-purpose `envBlock` variable into a named "open block" tracker** that
   recognizes two block-typed keys instead of one. Replace the `env`-only check (current line 208,
   `if (key === 'env' && rest === '')`) with a check against a small allowlist:
   ```js
   const BLOCK_KEYS = new Set(['env', 'headers']);
   ...
   if (BLOCK_KEYS.has(key) && rest === '') {
     servers[current][key] = {};
     openBlockKey = key;           // was: envBlock = {}; servers[current].env = envBlock;
   }
   ```
   and update the sub-key consumption loop (current lines 194–202) to write into
   `servers[current][openBlockKey]` instead of the `env`-specific `envBlock` variable. No other
   behavior of the sub-key loop changes — it already calls `parseInlineObject()` per sub-value,
   which is exactly what `headers` sub-entries need too.
2. **Widen the sub-key regex** from `^      ([A-Za-z0-9_]+):\s*(.*)$` to
   `^      ([A-Za-z0-9_-]+):\s*(.*)$` (allow hyphens) so future header names like `X-Api-Key` are
   parseable. Not required for this task's two header names (`Authorization`, `Origin`, both
   pure-alpha), but recommended now while touching this line, to avoid a second parser patch the
   first time a hyphenated header is registered.
3. **Add an inline-object branch for scalar (non-block) top-level keys**, so `url: { fromEnv: ...
   }` parses correctly instead of falling into the plain-scalar branch. In the existing
   `if (current)` block (lines 204–219), add a branch before the final `else`:
   ```js
   } else if (rest.startsWith('{') && rest.endsWith('}')) {
     servers[current][key] = parseInlineObject(rest);
   } else {
     servers[current][key] = parseScalar(stripQuotes(rest));
   }
   ```
   `parseInlineObject()` itself needs **no change** — it already handles multi-key inline objects
   with colon-containing values (rejoins after the first `:` split) and comma-separated fields;
   verified by hand-trace against `{ fromEnv: CWSO_BEARER_TOKEN, secret: true, wrap: "Bearer
   {VAR}" }` in §6.

### 5.1 Core primitive: `mapTemplatedValue()`

Add one new function and refactor `mapEnv()` to use it (this is an internal refactor —
`mapEnv()`'s existing signature, `mapEnv(envSpec, template)`, and all ~30 existing call sites
across the 6 format branches, are unchanged):

```js
// Renders one templated-value spec (see §3/§4) against a platform's own env-placeholder pattern.
//   spec: a plain literal (string/number/bool) -> returned unchanged (String(spec))
//         OR { fromEnv: VAR }                   -> template.replace('VAR', VAR)
//         OR { fromEnv: VAR, wrap: "X{VAR}Y" }   -> wrap.replace('{VAR}', <rendered above>)
//   template: the platform's own placeholder pattern: '${env:VAR}' (vscode/cursor/gemini/pi/
//             cline), '{env:VAR}' (opencode) or '${VAR}' (claude-code, T517)
//             (same `template` parameter mapEnv() already takes today — unrenamed, no collision,
//             since the author-facing field is named `wrap`, not `template`)
function mapTemplatedValue(spec, template) {
  if (spec && typeof spec === 'object' && spec.fromEnv) {
    const rendered = template.replace('VAR', spec.fromEnv);
    return spec.wrap ? spec.wrap.replace('{VAR}', rendered) : rendered;
  }
  return String(spec);
}

function mapEnv(envSpec, template) {
  const out = {};
  for (const [k, v] of Object.entries(envSpec)) out[k] = mapTemplatedValue(v, template);
  return out;
}
```

`mapEnv()` is now a thin per-key wrapper around `mapTemplatedValue()`. Because `headers` is
structurally identical to `env` (a flat dict of templated-value specs), **`mapEnv()` itself is
reused verbatim for `headers` — no new "mapHeaders" function is needed.** `url` is a single scalar,
not a dict, so its call sites use `mapTemplatedValue()` directly.

### 5.2 Per-format-branch changes

All 6 `format` branches gain: (a) `mapTemplatedValue(s.url, template)` in place of the current raw
`s.url`, and (b) `if (s.headers) { ...headers: mapEnv(s.headers, template) }` appended **after**
`url` (and after `type`, where present) to match the real target key order in `.mcp.json` (input
#4: `type`, `url`, `headers`). Note on branch count: there are 5 `if` blocks in `emitMcp()` today
handling 6 distinct `format` string values (`vscode`/`cursor` share one `if` block), covering all
7 platforms because `pi.json`'s manifest declares `"format": "cursor"` and reuses that branch
verbatim (confirmed in `mcp-platform-contract-v1.md` §3, table row for `pi`).

**`vscode`/`cursor` branch** (covers `vscode`, `cursor`, `pi`):
```js
if (s.transport === 'remote') {
  const url = mapTemplatedValue(s.url, '${env:VAR}');
  if (format === 'vscode') {
    target[name] = { type: 'http', url };
    if (s.headers) target[name].headers = mapEnv(s.headers, '${env:VAR}');
  } else {
    target[name] = { url };
    if (s.headers) target[name].headers = mapEnv(s.headers, '${env:VAR}');
  }
}
```

**`gemini` branch:**
```js
if (s.transport === 'remote') {
  mcpServers[name] = { httpUrl: mapTemplatedValue(s.url, '${env:VAR}') };
  if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${env:VAR}');
}
```

**`opencode` branch** (note the distinct `{env:VAR}` placeholder, single braces):
```js
if (s.transport === 'remote') {
  mcp[name] = { type: 'remote', url: mapTemplatedValue(s.url, '{env:VAR}') };
  if (s.headers) mcp[name].headers = mapEnv(s.headers, '{env:VAR}');
}
```

**`claude-code` branch** (note the distinct `${VAR}` placeholder — no `env:` segment — corrected
in T517; the `env` call site on the stdio side of the same branch takes the same template, since
Claude Code expands the same syntax in `command`, `args`, `env`, `url` and `headers` alike):
```js
if (s.transport === 'remote') {
  mcpServers[name] = { type: 'http', url: mapTemplatedValue(s.url, '${VAR}') };
  if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${VAR}');
} else {
  mcpServers[name] = { command: s.command, args: s.args || [] };
  if (s.env) mcpServers[name].env = mapEnv(s.env, '${VAR}');
}
```

**`cline` branch:**
```js
if (s.transport === 'remote') {
  mcpServers[name] = { type: 'streamableHttp', url: mapTemplatedValue(s.url, '${env:VAR}') };
  if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${env:VAR}');
}
```

### 5.3 Per-platform evidence disclosure for `headers` support (required, not implicit)

| Platform | `headers` support evidence | Class |
|---|---|---|
| `gemini` | Vendored official schema (`tests/fixtures/mcp-schemas/gemini-cli-settings.schema.json`), `$defs.MCPServerConfig` defines a `headers` property (T384, cited at lines ~4049/4147 per task brief) | **Schema-verified** |
| `opencode` | Vendored official schema (`tests/fixtures/mcp-schemas/opencode-config.schema.json`), `$defs.mcp`'s `McpRemoteConfig` defines a `headers` property (independently confirmed this session at line ~660; the task brief's "~543" companion citation was checked and found to be a different, unrelated `headers` property in a model-provider config block, not `$defs.mcp` — dropped, not cited) | **Schema-verified** |
| `claude-code` | No official schema exists for this platform (T384's own finding). The real root `.mcp.json` (input #4) contained a hand-added `cwso` entry with exactly this `{type, url, headers}` shape, which is direct evidence that Claude Code accepts a `headers` object on an `http`-type entry. **T517 correction:** that entry was *hand-written and never read by a running Claude Code client*, so it attested to the field shape only and not to the placeholder syntax inside those fields — v1 over-read it as evidence for both, which is how `${env:VAR}` reached this branch. The placeholder syntax is now independently verified: official documentation plus a live differential probe (§9) | **Empirically verified** (field shape: production evidence; placeholder syntax: documentation + live probe, §9) |
| `github` (vscode) | No official schema. But `.vscode/mcp.json`'s existing dest-only `cwso` entry (`url`, `headers.Authorization`, `headers.Origin`, `type`) is real, currently-preserved, hand-added content — direct proof VS Code's actual MCP client accepts a `headers` object on an `http`-type entry, even though the *values* in that dest entry differ from what this design's generator would produce (see §2(a)) | **Empirically verified** (via dest-only content, not generator output) |
| `cline` | No official schema. No hand-added or otherwise-observed `cline` MCP config anywhere in this repo's evidence base | **Unverified — disclosed extension** |
| `cursor` | No official schema. No hand-added or otherwise-observed `cursor` MCP config anywhere in this repo's evidence base | **Unverified — disclosed extension** |
| `pi` | Reuses the `cursor` format verbatim; same evidentiary gap as `cursor` | **Unverified — disclosed extension** |

This mirrors the disclosure style `mcp-platform-contract-v1.md` already uses elsewhere in this
repo (state the evidence class per platform rather than assuming uniform support). The three
"unverified" platforms are lower-risk in practice here because `cwso` (the only entry that
actually uses `headers`) is tagged `extended`, and none of `cline`/`cursor`/`pi` currently has any
known consumer wiring an MCP client against the generated file with real credentials the way
claude-code does — but this is disclosed, not silently assumed safe.

## 6. Decision: exact final `servers.yaml` YAML snippets

Insert as two new top-level entries under `servers:` (position: anywhere; alphabetical placement
after `github`/before `hf-mcp-server`... — no ordering constraint is enforced by the parser or
`emitMcp()`, so exact insertion point is a `backend-developer` style choice, not a functional one):

```yaml
  hindsight:
    tags: [core]
    transport: remote
    url: { fromEnv: HINDSIGHT_MCP_URL }

  cwso:
    tags: [extended]
    transport: remote
    url: { fromEnv: CWSO_MCP_URL }
    headers:
      Authorization: { fromEnv: CWSO_BEARER_TOKEN, secret: true, wrap: "Bearer {VAR}" }
      Origin: { fromEnv: CWSO_ORIGIN }
```

**Hand-traced verification (v2: traced per placeholder family, since the target shape is not the
same on every platform — this is exactly the distinction v1 collapsed):**

On the `${env:VAR}` family (`vscode`/`cursor`/`pi`/`gemini`/`cline`):

- `hindsight.url` = `{fromEnv: 'HINDSIGHT_MCP_URL'}` → `mapTemplatedValue(..., '${env:VAR}')` →
  `'${env:VAR}'.replace('VAR','HINDSIGHT_MCP_URL')` → `"${env:HINDSIGHT_MCP_URL}"`.
- `cwso.url` = `{fromEnv: 'CWSO_MCP_URL'}` → `"${env:CWSO_MCP_URL}"`.
- `cwso.headers.Authorization` = `{fromEnv: 'CWSO_BEARER_TOKEN', secret: true, wrap: 'Bearer
  {VAR}'}` → rendered = `"${env:CWSO_BEARER_TOKEN}"` → `wrap.replace('{VAR}', rendered)` =
  `"Bearer ${env:CWSO_BEARER_TOKEN}"`.
- `cwso.headers.Origin` = `{fromEnv: 'CWSO_ORIGIN'}` (no `wrap`) → `"${env:CWSO_ORIGIN}"`.

On `claude-code` (`${VAR}`, T517) — this is the generated root/`implementation` `.mcp.json`:

- `hindsight.url` → `'${VAR}'.replace('VAR','HINDSIGHT_MCP_URL')` → `"${HINDSIGHT_MCP_URL}"`,
  which Claude Code expands from the live process environment at startup.
- `cwso.url` → `"${CWSO_MCP_URL}"`.
- `cwso.headers.Authorization` → rendered = `"${CWSO_BEARER_TOKEN}"` →
  `'Bearer {VAR}'.replace('{VAR}', '${CWSO_BEARER_TOKEN}')` = `"Bearer ${CWSO_BEARER_TOKEN}"`.
  Note `wrap`'s own `{VAR}` token is still unambiguous against the rendered `${CWSO_BEARER_TOKEN}`:
  `String.replace` matches the first literal `{VAR}` occurrence, and the rendered reference never
  contains one.
- `cwso.headers.Origin` → `"${CWSO_ORIGIN}"`.
- On the stdio side of the same branch, `gitlab`/`brave`/`toolradar` `env` values render the same
  way, e.g. `"${GITLAB_PERSONAL_ACCESS_TOKEN}"`.

v1's byte-for-byte claim against input #4 no longer holds for `claude-code`, and should not: input
#4 encoded the defect. The `merge_json` no-op argument below is likewise superseded for this one
file — the `--update` merge now legitimately rewrites those five servers' placeholder values, which
is the fix landing, not drift.
- Key insertion order in the claude-code branch (`{ type, url, headers? }`, headers assigned last)
  matches the real target's `type`/`url`/`headers` order exactly, so `JSON.stringify` produces the
  same field order as the existing hand-added dest content, and since dest already has identical
  values, `merge_json`'s recursive leaf-update on `--update` is a no-op — output is byte-identical
  before and after this change lands.

**Parser hand-trace (§5.0), confirming the YAML above is actually parseable by the extended
`parseServersYaml()`:** the top-level `url:` line for both servers has `rest = "{ fromEnv:
HINDSIGHT_MCP_URL }"` (or the `CWSO_MCP_URL` equivalent), which starts with `{` and ends with `}`,
so it hits the new inline-object branch and calls `parseInlineObject()`, which correctly splits on
the single top-level `:` and returns `{fromEnv: 'HINDSIGHT_MCP_URL'}`. The `headers:` line has
`rest === ''`, so it opens a block exactly like `env:` does today (now via the generalized
`BLOCK_KEYS` check). Its two sub-lines are each matched by the (widened) 6-space sub-key regex and
passed to `parseInlineObject()`; the `Authorization` line's inline object
(`{ fromEnv: CWSO_BEARER_TOKEN, secret: true, wrap: "Bearer {VAR}" }`) splits correctly on its two
top-level commas (none occur inside `"Bearer {VAR}"`), and the `wrap` field's value correctly
survives `stripQuotes()` (`"Bearer {VAR}"` → `Bearer {VAR}`) because the embedded `{VAR}` sits in
the *middle* of the string, not at its very first/last character, so it is untouched by the outer
object's own `slice(1, -1)` brace-stripping.

## 7. Guidance for the QA follow-up (`tests/functional/test_mcp_secret_guard.py`)

Not implemented here (out of role scope), but specified precisely so `qa-engineer` does not need
to ask follow-up questions:

- `find_literal_env_values()`'s `walk()` function only recurses into dict keys literally named
  `"env"` (line 48: `if key == "env" and isinstance(value, dict)`). It must gain a **second**
  branch for `key == "headers"`, structurally identical to the `env` branch, but validated against
  a **different** regex than `ALLOWED_ENV_VALUE_RE`, because header values are not always a pure
  placeholder — some are a fixed literal wrapped around one (per §3/§6, e.g. `"Bearer
  ${env:CWSO_BEARER_TOKEN}"`).
- Recommended pattern for the new header-value check (**v2: three** platform placeholder families,
  matching the `${env:VAR}` / `{env:VAR}` / `${VAR}` distinction encoded in `ALLOWED_ENV_VALUE_RE`):
  a header value is acceptable if it contains **exactly one** well-formed placeholder token
  (`\$\{env:[A-Z][A-Z0-9_]*\}`, `\{env:[A-Z][A-Z0-9_]*\}` or `\$\{[A-Z][A-Z0-9_]*\}`) and the remaining literal text outside
  that token contains **no** `$` and no unmatched `{`/`}` characters — i.e., reject any header
  value that either has zero placeholder tokens (a bare literal, which is exactly the leak class
  the guard exists to catch) or has residual `${`/`{` sequences outside the one recognized token
  (a defense-in-depth signal that something odd, possibly a second unexpected interpolation or a
  malformed template, is present).
- This check should run against **every** `headers` value uniformly, regardless of the
  authoring-time `secret: true/false` flag — mirroring how `find_literal_env_values()` already
  checks every `env` value uniformly today (e.g. non-secret `GITLAB_API_URL` is checked exactly
  like secret `GITLAB_PERSONAL_ACCESS_TOKEN`). The `secret` flag remains inert in `sync.mjs`
  generation logic (§3); it is authorial/audit metadata only, not a signal the guard should use to
  skip values.
- `test_guard_allows_placeholder_syntax` and `test_guard_detects_injected_literal_secret` should
  each gain a `headers`-shaped fixture case analogous to their existing `env`-shaped ones (a
  `"Bearer ${env:CWSO_BEARER_TOKEN}"`-style positive case; a literal-token-shaped negative case,
  e.g. `"Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"`).

## 8. Disclosed non-blocking status note

Per `docs/checkpoints/handoff-725b7925-6b66-47d2-b05b-b7c2e25a3bfb.md`, `cwso`'s bearer token was,
as of that handoff (2026-09-11), failing live with `AUTH_HEADER_REJECTED` (403). This design's
scope is **registration** (making `hindsight`/`cwso` generator-managed with the correct shape) —
registration correctness and live auth success are separate failure modes. Whoever implements this
design should re-check current live status independently rather than assume the syntax fix (MR
!279) also fixed the underlying 403; this design does not depend on or block on that being
resolved.

## 9. What this design does not touch (compliance with role scope)

This document is the only file written by this task. `implementation/knowledge/mcp/servers.yaml`,
`implementation/scripts/sync.mjs`, `.mcp.json`, `.vscode/mcp.json`, and every generated platform
file remain unmodified — all changes above are specified for `backend-developer` to implement, per
this repo's own `security-guidelines.md` Agent Permission Classification ("Architect — read-only
for implementation code; write access limited to architecture docs and decision records").

## 10. ADR — deliberately not created this session (disclosed, not silently skipped)

The brief left an ADR optional ("your call"). This design is significant enough that one would
normally be warranted. It was **not** created in this session because determining the next
available ADR number safely requires directory-listing/enumeration tooling this session was not
granted (`Read`/`Edit`/`Write`/`WebFetch`/`WebSearch`/`sequential-thinking`/`fetch` only, no
`Bash`/`Glob`). `docs/decisions/ADR-001-cwso-sia-integration.md` was confirmed to exist by direct
read; a sibling ADR referenced in `sync.mjs`'s own comments as "ADR-002" and one referenced in a
handoff as "ADR-004" could not be located at any filename this session guessed (both a plausible
`ADR-002-mcp-provenance-sidecar.md` and `ADR-004-t407-inconclusive.md` returned "file does not
exist" — meaning either a different slug is in use, or my guesses were simply wrong), and without
directory listing there is no safe way to enumerate `docs/decisions/` to find the true next number
without risking a collision on an already-used number with a different slug. Rather than guess and
risk writing a numerically-colliding ADR, this decision content is instead captured in full in
this design document (§1–§7), and the ADR itself is deferred — flagged as a blocker below for the
orchestrator to resolve (trivial once a shell/`ls docs/decisions/` is available) and dispatch as a
follow-up if still wanted once the number is confirmed.

## 9. T517 evidence for the `claude-code` placeholder template (new in v2)

### 9.1 Documentation

Claude Code's MCP documentation, §"Environment variable expansion in `.mcp.json`"
(<https://code.claude.com/docs/en/mcp>, read 2026-09-25), states:

- Supported syntax: `${VAR}` expands to the value of environment variable `VAR`;
  `${VAR:-default}` expands to `VAR` if set, otherwise the default.
- Expansion locations: `command`, `args`, `env`, `url` (HTTP server types) and `headers`.
- Unset variable with no default: the config still loads, a missing-variable warning is reported in
  `claude mcp list`, and the unexpanded `${VAR}` text is used as-is.

No `${env:…}` form is documented anywhere for this platform.

### 9.2 Live differential probe (the decisive check)

Run in an isolated throwaway project directory with an isolated `CLAUDE_CONFIG_DIR`, so neither
this repository's config nor the user's own `~/.claude.json` was touched (confirmed unchanged by
checksum before and after). `HINDSIGHT_MCP_URL` was set in the environment throughout;
`T517_UNSET_PROBE_VAR` was never set.

| Probe `url` | Variable set? | `claude mcp list` result |
|---|---|---|
| `${HINDSIGHT_MCP_URL}` | yes | **✔ Connected** |
| `${env:HINDSIGHT_MCP_URL}` | yes | **✘ Failed to connect — `'url' is not a valid URL`** |
| `${T517_UNSET_PROBE_VAR}` | no | `Missing environment variables: T517_UNSET_PROBE_VAR` |
| `${env:T517_UNSET_PROBE_VAR}` | no | *no warning at all* |

The last two rows are the control that identifies the mechanism rather than merely the symptom:
with the *same* unset variable, only the bare form is recognised as a variable reference. The
`env:` form produces no missing-variable warning because Claude Code never parses it as a reference
— it is inert literal text, which is precisely why it reached the HTTP client as a malformed URL.

### 9.3 `gitlab` startup probe (the silent half)

`@zereight/mcp-gitlab` was launched directly over stdio with an MCP `initialize` request, once with
the literal pre-fix placeholder text as its configuration and once with the expanded values:

- Literal `${env:GITLAB_API_URL}` / `${env:GITLAB_PERSONAL_ACCESS_TOKEN}` → exit code 1 during
  startup, `Configuration validation failed: GITLAB_API_URL contains an invalid URL`, no handshake.
- Expanded values → `Configuration validation passed`, `initialize` handshake completed.

This confirms the plan's stated hypothesis: `gitlab`'s `CONNECTION_CLOSED` was the server exiting
during startup on the literal placeholder, not a transport or credential problem.

### 9.4 Effect on the secret guard

`tests/functional/test_mcp_secret_guard.py` now admits a third placeholder family. This is a
widening of an allowlist, so the non-weakening argument must be explicit: the added alternative is
`^\$\{[A-Z][A-Z0-9_]*\}$` — a bare, fully upper-snake-case variable name between `${` and `}`, with
nothing else in the value. No credential shape can satisfy it (`tr_live_…`, `glpat-…`, `eyJhbGc…`
all fail on the required leading `${`), and neither can a partially-interpolated value such as
`prefix-${REAL_VAR}` or a lowercase brace expression. A regression test asserts exactly that.

Deliberately **not** admitted: the documented `${VAR:-default}` form. The generator never emits a
default, and accepting `:-…` would let arbitrary literal text sit inside an accepted token. If a
future `servers.yaml` entry needs a default, the guard must be widened for it deliberately, with
its own adversarial test.

### 9.5 Constraint to carry forward: credential names that never expand toward a remote server

The same documentation records that in a *remote* server's `url` and `headers`, Claude Code reads
certain variable names as empty rather than expanding them — its own credentials
(`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`), cloud-provider credentials
(`AWS_BEARER_TOKEN_BEDROCK`), and others the environment carries (`HTTPS_PROXY`, `NPM_TOKEN`). A
`:-default` fallback on such a name is ignored. No `fromEnv` name currently in `servers.yaml` is in
that set — the two remote servers reference `HINDSIGHT_MCP_URL`, `CWSO_MCP_URL`, `CWSO_BEARER_TOKEN`
and `CWSO_ORIGIN`, and the three stdio servers reference `GITLAB_PERSONAL_ACCESS_TOKEN`,
`GITLAB_API_URL`, `BRAVE_API_KEY` and `TOOLRADAR_API_KEY` (the `env` block is not subject to this
rule in any case) — so none is affected today. Any
future remote-server `url`/`headers` entry must avoid those names, and the symptom to look for is a
`401` from the server rather than a config error.
