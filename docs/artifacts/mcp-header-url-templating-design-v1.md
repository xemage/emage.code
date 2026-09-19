# MCP Header/URL Templating Design — v1

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
# containing exactly one `{VAR}` placeholder token (single braces, chosen deliberately distinct
# from both platform placeholder syntaxes — `${env:VAR}` and `{env:VAR}` — so it can never be
# confused with, or accidentally matched by, the per-platform substitution pass in §5):
SomeHeader: { fromEnv: SOME_ENV_VAR, secret: true, wrap: "Bearer {VAR}" }
```

Rendering rule (see §5 for the exact function): compute the platform's own rendered env
reference first (`${env:SOME_ENV_VAR}` or `{env:SOME_ENV_VAR}` depending on target format), then,
if `wrap` is present, substitute that rendered reference into `wrap`'s `{VAR}` slot; if `wrap` is
absent, use the rendered reference directly. This is why `Origin: { fromEnv: CWSO_ORIGIN }` (no
`wrap`) renders to exactly `"${env:CWSO_ORIGIN}"`, while
`Authorization: { fromEnv: CWSO_BEARER_TOKEN, secret: true, wrap: "Bearer {VAR}" }` renders to
exactly `"Bearer ${env:CWSO_BEARER_TOKEN}"` — matching the real target `.mcp.json` shape (input
#4) exactly, verified by hand-tracing in §6.

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
//   template: the platform's own placeholder pattern, e.g. '${env:VAR}' or '{env:VAR}'
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

**`claude-code` branch:**
```js
if (s.transport === 'remote') {
  mcpServers[name] = { type: 'http', url: mapTemplatedValue(s.url, '${env:VAR}') };
  if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${env:VAR}');
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
| `claude-code` | No official schema exists for this platform (T384's own finding). However, the real, already-live, already-merged root `.mcp.json` (input #4) already contains a working `cwso` entry with exactly this `{type, url, headers}` shape, hand-added by the user and reported functioning for URL/header wiring (auth token itself separately reported failing — see §8) | **Empirically verified** (direct production evidence, stronger than a schema citation) |
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

**Hand-traced verification against the real target `.mcp.json` (claude-code), confirming
acceptance criterion 3 (byte-for-byte match) is satisfied by this exact YAML plus §5's exact code:**

- `hindsight.url` = `{fromEnv: 'HINDSIGHT_MCP_URL'}` → `mapTemplatedValue(..., '${env:VAR}')` →
  `'${env:VAR}'.replace('VAR','HINDSIGHT_MCP_URL')` → `"${env:HINDSIGHT_MCP_URL}"`. Matches input
  #4 exactly.
- `cwso.url` = `{fromEnv: 'CWSO_MCP_URL'}` → `"${env:CWSO_MCP_URL}"`. Matches.
- `cwso.headers.Authorization` = `{fromEnv: 'CWSO_BEARER_TOKEN', secret: true, wrap: 'Bearer
  {VAR}'}` → rendered = `"${env:CWSO_BEARER_TOKEN}"` → `wrap.replace('{VAR}', rendered)` =
  `'Bearer {VAR}'.replace('{VAR}', '${env:CWSO_BEARER_TOKEN}')` =
  `"Bearer ${env:CWSO_BEARER_TOKEN}"`. Matches input #4 exactly.
- `cwso.headers.Origin` = `{fromEnv: 'CWSO_ORIGIN'}` (no `wrap`) → `"${env:CWSO_ORIGIN}"`. Matches.
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
- Recommended pattern for the new header-value check (two platform placeholder families, matching
  the existing `${env:VAR}` / `{env:VAR}` distinction already encoded in `ALLOWED_ENV_VALUE_RE`):
  a header value is acceptable if it contains **exactly one** well-formed placeholder token
  (`\$\{env:[A-Z][A-Z0-9_]*\}` or `\{env:[A-Z][A-Z0-9_]*\}`) and the remaining literal text outside
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
