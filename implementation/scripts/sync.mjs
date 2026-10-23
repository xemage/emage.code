#!/usr/bin/env node
// emage.code sync engine (root-configurable, deterministic)
//
// Usage:
//   node scripts/sync.mjs [--platform=<name>] [--check]
//                            [--root=<abs-or-rel-path>]
//                            [--knowledge=<dir>] [--platforms=<dir>] [--extras=<dir>]
//
// Defaults:
//   --root=.. (implementation when run from scripts/)
//   --knowledge=knowledge --platforms=platforms --extras=_extras

import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function parseArgs(argv) {
  const parsed = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) continue;
    const body = token.replace(/^--/, '');
    if (body.includes('=')) {
      const [key, value] = body.split('=');
      parsed[key] = value;
      continue;
    }

    const next = argv[index + 1];
    if (next && !next.startsWith('--')) {
      parsed[body] = next;
      index += 1;
      continue;
    }

    parsed[body] = true;
  }
  return parsed;
}

const args = parseArgs(process.argv.slice(2));

const rootArg = args.root ? String(args.root) : null;
// path.resolve also normalises an absolute --root (".." segments, "//", a trailing "/"), which the
// startsWith(ROOT + sep) checks of assertUnderRoot rely on (T682 N-4).
const ROOT = rootArg
  ? path.resolve(process.cwd(), rootArg)
  : path.resolve(__dirname, '..');
const KNOWLEDGE = path.resolve(ROOT, String(args.knowledge || 'knowledge'));
const PLATFORMS = path.resolve(ROOT, String(args.platforms || 'platforms'));
const EXTRAS = path.resolve(ROOT, String(args.extras || '_extras'));

const MANIFEST_SCHEMA_FILE = '_manifest.schema.json';
const CHECK_ONLY = !!args.check;
const ONLY_PLATFORM = args.platform ? String(args.platform) : null;

function toPosixPath(p) {
  return p.split(path.sep).join('/');
}

function normalizeTextBuffer(buf) {
  return buf.toString('utf8').replace(/\r\n/g, '\n');
}

function parseFrontmatter(src) {
  if (!src.startsWith('---')) return { data: {}, body: src };
  const end = src.indexOf('\n---', 3);
  if (end === -1) return { data: {}, body: src };
  const yaml = src.slice(3, end).replace(/^\r?\n/, '');
  const body = src.slice(end + 4).replace(/^\r?\n/, '');
  return { data: parseYamlBlock(yaml), body };
}

function parseYamlBlock(yaml) {
  const out = {};
  const lines = yaml.split(/\r?\n/).map((l) => l.replace(/\r$/, ''));
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim() || line.trim().startsWith('#')) {
      i++;
      continue;
    }
    const m = line.match(/^([A-Za-z_][\w-]*)\s*:\s*(.*)$/);
    if (!m) {
      i++;
      continue;
    }
    const key = m[1];
    const rest = m[2];

    if (rest.startsWith('[') && rest.endsWith(']')) {
      out[key] = rest
        .slice(1, -1)
        .split(',')
        .map((s) => stripQuotes(s.trim()))
        .filter(Boolean);
      i++;
      continue;
    }

    if (rest !== '') {
      out[key] = parseScalar(stripQuotes(rest));
      i++;
      continue;
    }

    const block = {};
    i++;
    while (i < lines.length && /^\s+/.test(lines[i])) {
      const sub = lines[i].match(/^\s+([A-Za-z_][\w_-]*)\s*:\s*(.*)$/);
      if (sub) block[sub[1]] = parseScalar(stripQuotes(sub[2]));
      i++;
    }
    out[key] = block;
  }
  return out;
}

function stripQuotes(v) {
  if (typeof v !== 'string') return v;
  const s = v.trim();
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  return s;
}

function parseScalar(v) {
  if (v === 'true') return true;
  if (v === 'false') return false;
  if (/^-?\d+$/.test(v)) return Number(v);
  return v;
}

function emitFrontmatter(obj, opts = { toolsFormat: 'array' }) {
  const lines = ['---'];
  const anyDeny = (opts.denyTools || []).length + (opts.denyFirst || []).length > 0;
  if (opts.toolsFormat === 'object' && anyDeny && !Array.isArray(obj.tools)) {
    obj = { ...obj, tools: [] };
  }
  for (const [key, val] of Object.entries(obj)) {
    if (val === undefined || val === null) continue;
    if (key === 'tools' && opts.toolsFormat === 'object' && Array.isArray(val)) {
      lines.push('tools:');
      // T663: a server wildcard deny for an agent that holds only NAMED tools of that server goes
      // FIRST; the named allows after it are then the only tools of the server it can call.
      for (const t of opts.denyFirst || []) lines.push(`  ${t}: false`);
      for (const t of val) lines.push(`  ${t}: true`);
      // T663: per-agent denies come LAST. Opencode applies the last matching rule, so a deny written
      // after every allow survives any broader allow of the same agent (docs/artifacts/mcp-agent-denials-v1.md).
      for (const t of opts.denyTools || []) lines.push(`  ${t}: false`);
      continue;
    }
    if (key === 'tools' && opts.toolsFormat === 'string' && Array.isArray(val)) {
      lines.push(`tools: ${val.join(', ')}`);
      continue;
    }
    if (Array.isArray(val)) {
      lines.push(`${key}: [${val.join(', ')}]`);
      continue;
    }
    if (typeof val === 'boolean' || typeof val === 'number') {
      lines.push(`${key}: ${val}`);
      continue;
    }
    const needsQuote = /[:#&*!|>%@`]/.test(val) || val.includes('\n');
    lines.push(`${key}: ${needsQuote ? JSON.stringify(val) : `"${val}"`}`);
  }
  lines.push('---', '');
  return lines.join('\n');
}

async function readServersYaml() {
  const file = path.join(KNOWLEDGE, 'mcp', 'servers.yaml');
  const raw = await fs.readFile(file, 'utf8');
  const servers = parseServersYaml(raw);
  validateDenyTools(servers);
  validateTemplatedSpecs(servers);
  return servers;
}

// T658 (SEC-T657-01): a server may carry `denyTools: [<tool>, ...]`, the exact tool names, as the
// server itself reports them, that the platform must refuse for this server. This is the one source
// of truth for the server-level denial; emitMcp() renders it only for the two platforms whose
// documentation and vendor source show an enforcing mechanism (see
// docs/artifacts/mcp-server-denials-v1.md): Opencode (top-level `permission`) and Gemini CLI
// (`mcpServers.<name>.excludeTools`). Names are exact on purpose: a wildcard could silently deny
// (or, on Opencode, fail to deny) more than the list says.
const DENY_TOOL_NAME = /^[A-Za-z0-9_]+$/;

// T663 (SEC-T663-06): a server entry may carry only these keys. A misspelling of a security key
// (`denyUnlessGrant`, `denyTool`) used to be read as an unknown key and silently ignored, which
// leaves the denial out; it now stops the run.
const SERVER_KEYS = new Set([
  'tags', 'transport', 'command', 'args', 'env', 'url', 'headers', 'denyTools', 'denyUnlessGranted', 'skipFormats',
]);

// T680 (SEC-T680-03): `skipFormats: [<format>, ...]` leaves a server out of the MCP config of the named
// formats (the `mcp.format` of a platform manifest) because the client cannot use it, for example Pi 1.x
// rejects a templated `url`. The provenance sidecar leaves it out too, so `--update` prunes an entry that an
// older release generated. Only known format names are accepted: a misspelling would keep the entry.
const MCP_FORMATS = ['vscode', 'gemini', 'opencode', 'pi', 'claude-code', 'cline'];

function emittedFor(server, tags, format) {
  return (server.tags || []).some((t) => tags.includes(t)) && !(server.skipFormats || []).includes(format);
}

function validateDenyTools(servers) {
  for (const [name, server] of Object.entries(servers)) {
    const unknown = Object.keys(server).filter((k) => !SERVER_KEYS.has(k));
    if (unknown.length > 0) {
      throw new Error(`servers.yaml: ${name} has an unknown key: ${unknown.map((k) => k.slice(0, 40)).join(', ')}`);
    }
    if (server.denyUnlessGranted !== undefined && typeof server.denyUnlessGranted !== 'boolean') {
      throw new Error(`servers.yaml: ${name}.denyUnlessGranted must be the boolean true or false (or absent)`);
    }
    if (server.skipFormats !== undefined) {
      const formats = server.skipFormats;
      if (!Array.isArray(formats) || formats.length === 0 || formats.some((f) => !MCP_FORMATS.includes(f))
          || new Set(formats).size !== formats.length) {
        throw new Error(`servers.yaml: ${name}.skipFormats must be a non-empty array of distinct format names (${MCP_FORMATS.join(', ')})`);
      }
    }
    if (server.denyTools === undefined) continue;
    const list = server.denyTools;
    if (!Array.isArray(list) || list.length === 0) {
      throw new Error(`servers.yaml: ${name}.denyTools must be a non-empty array of tool names`);
    }
    for (const tool of list) {
      if (typeof tool !== 'string' || !DENY_TOOL_NAME.test(tool)) {
        throw new Error(`servers.yaml: ${name}.denyTools entry is not an exact tool name ([A-Za-z0-9_]+): ${String(tool).slice(0, 60)}`);
      }
    }
    if (new Set(list).size !== list.length) {
      throw new Error(`servers.yaml: ${name}.denyTools has a duplicate entry`);
    }
  }
}

// T665 (SEC-T660-01): a templated value (`url`, an `env` or a `headers` entry written as an inline
// object) may carry only these keys. As with SERVER_KEYS, an unknown key (a misspelled `default`,
// `secret` or `wrap`) stops the run instead of being ignored, because a dropped `secret` or `default`
// changes what is rendered into a credential entry. `default` is deliberate and new: it is rendered
// only for the claude-code format (see mapTemplatedValue). T680 adds `optional`: the `env` variable may be
// unset. claude-code renders the empty default `${VAR:-}`; pi (which throws for an unset or empty
// variable) leaves the entry out; the other formats render as before (see mapEnvOmitOptional).
const SPEC_KEYS = new Set(['fromEnv', 'secret', 'wrap', 'default', 'optional']);
const ENV_VAR_NAME = /^[A-Za-z_][A-Za-z0-9_]*$/;
// A default is literal text inside `${VAR:-<default>}`: no `$`, `{` or `}` that could end or nest the
// expansion, no control character.
const SPEC_WRAP = /^[A-Za-z0-9 _.:/-]*\{VAR\}[A-Za-z0-9 _.:/-]*$/;
const SPEC_DEFAULT = /^[^${}\u0000-\u001f]*$/;

function validateSpec(where, spec) {
  if (spec === null || typeof spec !== 'object') return;
  const unknown = Object.keys(spec).filter((k) => !SPEC_KEYS.has(k));
  if (unknown.length > 0) {
    throw new Error(`servers.yaml: ${where} has an unknown key: ${unknown.map((k) => k.slice(0, 40)).join(', ')}`);
  }
  if (typeof spec.fromEnv !== 'string' || !ENV_VAR_NAME.test(spec.fromEnv)) {
    throw new Error(`servers.yaml: ${where}.fromEnv must be an environment variable name`);
  }
  // SEC-T665-08: `secret` is read as a boolean guard (a string such as `yes` or `"false"` would be
  // truthy or ignored), and `wrap` is fixed text around exactly one `{VAR}`: nothing that could carry a
  // credential or a second placeholder.
  if (spec.secret !== undefined && typeof spec.secret !== 'boolean') {
    throw new Error(`servers.yaml: ${where}.secret must be the boolean true or false (or absent)`);
  }
  if (spec.wrap !== undefined && !SPEC_WRAP.test(spec.wrap)) {
    throw new Error(`servers.yaml: ${where}.wrap must contain exactly one {VAR} and otherwise only letters, digits, space and _ . : / -`);
  }
  // T680: `optional` is read as a boolean guard like `secret`; an optional variable has no value to
  // fall back to on the platforms that cannot express a default, so its default is absent or "".
  if (spec.optional !== undefined && typeof spec.optional !== 'boolean') {
    throw new Error(`servers.yaml: ${where}.optional must be the boolean true or false (or absent)`);
  }
  if (spec.optional === true && spec.default !== undefined && spec.default !== '') {
    throw new Error(`servers.yaml: ${where}.default of an optional value must be the empty string (or absent)`);
  }
  if (spec.default === undefined) return;
  if (typeof spec.default !== 'string' || !SPEC_DEFAULT.test(spec.default)) {
    throw new Error(`servers.yaml: ${where}.default must be a string without $, { or } or control characters`);
  }
  if (spec.secret === true && spec.default !== '') {
    throw new Error(`servers.yaml: ${where}.default of a secret value must be the empty string`);
  }
}

function validateTemplatedSpecs(servers) {
  for (const [name, server] of Object.entries(servers)) {
    validateSpec(`${name}.url`, server.url);
    if (server.url && server.url.optional === true) {
      throw new Error(`servers.yaml: ${name}.url cannot be optional: a remote server needs its address`);
    }
    for (const key of BLOCK_KEYS) {
      for (const [k, spec] of Object.entries(server[key] || {})) {
        validateSpec(`${name}.${key}.${k}`, spec);
        // SEC-T680-02: Pi does not pass a header through from its own environment (it does so for a stdio
        // `env`), so an optional header would never be sent there.
        if (key === 'headers' && spec && spec.optional === true) {
          throw new Error(`servers.yaml: ${name}.headers.${k} cannot be optional: only an env value can be left out`);
        }
      }
    }
  }
}

// T663 (SEC-T658-01): `denyUnlessGranted: true` on a server asks the Opencode projection for a
// per-agent `<server>_*: false` in every agent file whose tool list holds no token for that server
// (no `mcp__<server>` and no `mcp__<server>__<tool>`), and a leading one for an agent that holds only
// named tools of the server. `denyTools` (above) additionally yields one
// per-agent `<server>_<tool>: false` per listed tool in EVERY agent file. See
// docs/artifacts/mcp-agent-denials-v1.md. `false` is an explicit exemption (user decision 2026-10-16).
// Other platforms ignore both.

// Block-typed (multi-line, nested) top-level server keys. `env` is the original;
// `headers` (T491) reuses the identical block-parsing mechanism.
const BLOCK_KEYS = new Set(['env', 'headers']);

// The value of one `    key: rest` line of a server entry (T677: split out of parseServersYaml).
function parseServerValue(rest, serverName, key) {
  const arrayText = stripInlineArrayComment(rest);
  if (arrayText.startsWith('[') && arrayText.endsWith(']')) {
    try {
      return splitInlineArray(arrayText.slice(1, -1)).map((s) => stripQuotes(s.trim()));
    } catch (err) {
      // T672: name the server and the key, so a refused array is found without searching the file.
      throw new Error(`${err.message} (server ${serverName}, key ${key})`);
    }
  }
  if (rest.startsWith('{') && rest.endsWith('}')) return parseInlineObject(rest);
  return parseScalar(stripQuotes(rest));
}

// Stores one `    key: rest` line on the server; returns the key when it opens a block (`env`, `headers`), else null.
function parseServerKeyLine(server, serverName, key, rest) {
  if (BLOCK_KEYS.has(key) && rest === '') {
    server[key] = {};
    return key;
  }
  server[key] = parseServerValue(rest, serverName, key);
  return null;
}

function parseServersYaml(raw) {
  const lines = raw.split(/\r?\n/);
  const servers = {};
  let i = 0;
  while (i < lines.length && !lines[i].trim().startsWith('servers:')) i++;
  i++;
  let current = null;
  let openBlockKey = null;

  for (; i < lines.length; i++) {
    const ln = lines[i];
    if (!ln.trim() || ln.trim().startsWith('#')) continue;
    const m2 = ln.match(/^  ([A-Za-z0-9._-]+):\s*$/);
    if (m2) {
      current = m2[1];
      servers[current] = {};
      openBlockKey = null;
      continue;
    }
    if (current && openBlockKey !== null) {
      const me = ln.match(/^      ([A-Za-z0-9_-]+):\s*(.*)$/);
      if (me) {
        servers[current][openBlockKey][me[1]] = parseInlineObject(me[2]);
        continue;
      }
      openBlockKey = null;
    }
    const me2 = current ? ln.match(/^    ([A-Za-z0-9_-]+):\s*(.*)$/) : null;
    if (me2) openBlockKey = parseServerKeyLine(servers[current], current, me2[1], me2[2]);
  }

  return servers;
}

// Splits the inside of an inline YAML array on commas that are NOT inside a quoted item.
// T655: an item may itself contain commas, semicolons, `*`, `{}` or `[]` (the Playwright
// `--blocked-origins` value is one double-quoted argument with brace lists). Characters
// inside quotes are kept verbatim; nothing is expanded or escaped here.
// T656 (SEC-T655-04): this reader does not implement YAML escapes, so it refuses what it cannot
// read faithfully instead of silently diverging from YAML: a backslash inside a quoted item, a
// quote that is never closed, and text between a closing quote and the next comma. A quote opens
// a quoted item only at the start of an item (an apostrophe inside a plain item is plain text).
// T672 (TL-T649-04): it also refuses what YAML reads differently from this reader: an empty array
// (`[]`, YAML: an empty list; here one empty item), a trailing comma (YAML ignores it), an empty
// item between commas (YAML: an error), and a plain item that YAML would read as a mapping or a
// nested collection (`a: b`, `a:`, `{}`, `[x]`). A quoted item is always a string and is never refused.
function splitInlineArray(inner) {
  const parts = [];
  let cur = '';
  let quote = null;
  let closed = false;
  for (const ch of inner) {
    if (quote) {
      if (ch === '\\') {
        throw new Error(`servers.yaml: a backslash inside a quoted array item is not supported: ${inner.slice(0, 60)}`);
      }
      if (ch === quote) {
        quote = null;
        closed = true;
      }
      cur += ch;
    } else if (ch === ',') {
      parts.push(cur);
      cur = '';
      closed = false;
    } else if (closed && ch.trim() !== '') {
      throw new Error(`servers.yaml: text after the closing quote of an array item: ${inner.slice(0, 60)}`);
    } else if ((ch === '"' || ch === "'") && cur.trim() === '') {
      quote = ch;
      cur += ch;
    } else {
      cur += ch;
    }
  }
  if (quote) {
    throw new Error(`servers.yaml: unclosed quote in an array item: ${inner.slice(0, 60)}`);
  }
  parts.push(cur);
  checkInlineArrayItems(parts, inner);
  return parts;
}

// T672 (TL-T649-09): YAML ends a value at ` #` outside quotes, so `args: [a, b]  # note` is an array.
// Only an inline-array value (starting with `[`) is touched. A quote opens a quoted item only at the start of
// an item, as in splitInlineArray; text inside a quoted item, `#` included, is kept.
function stripInlineArrayComment(rest) {
  if (!rest.startsWith('[')) return rest;
  let quote = null;
  let prev = '[';
  let prevNonSpace = '[';
  for (let i = 0; i < rest.length; i++) {
    const ch = rest[i];
    if (quote) {
      if (ch === quote) quote = null;
    } else if ((ch === '"' || ch === "'") && (prevNonSpace === '[' || prevNonSpace === ',')) {
      quote = ch;
    } else if (ch === '#' && /\s/.test(prev)) {
      return rest.slice(0, i).trimEnd();
    }
    prev = ch;
    if (!/\s/.test(ch)) prevNonSpace = ch;
  }
  return rest;
}

function checkInlineArrayItems(parts, inner) {
  const shown = inner.slice(0, 60);
  if (parts.length === 1 && parts[0].trim() === '') {
    throw new Error(`servers.yaml: an empty inline array \`[]\` is not supported: [${shown}]`);
  }
  parts.forEach((part, index) => {
    const item = part.trim();
    if (item === '') {
      const kind = index === parts.length - 1 ? 'a trailing comma' : 'an empty item';
      throw new Error(`servers.yaml: ${kind} in an inline array is not supported: [${shown}]`);
    }
    if (item.startsWith('"') || item.startsWith("'")) return;
    // YAML indicators that start an alias, anchor, tag, block scalar, reserved or directive token.
    if (/^[*&!|>@%`]/.test(item)) {
      throw new Error(`servers.yaml: a plain array item may not start with a YAML indicator (${item.slice(0, 40)}); quote it: [${shown}]`);
    }
    if (/:($|\s)/.test(item) || item.startsWith('{') || item.startsWith('[')) {
      throw new Error(`servers.yaml: a plain array item that YAML reads as a mapping or collection (${item.slice(0, 40)}) is not supported; quote it: [${shown}]`);
    }
  });
}

function parseInlineObject(s) {
  const trimmed = s.trim();
  if (!trimmed.startsWith('{')) return stripQuotes(trimmed);
  const inner = trimmed.slice(1, -1);
  const out = {};
  for (const part of inner.split(',')) {
    const [k, ...rest] = part.split(':');
    if (!k) continue;
    out[k.trim()] = parseScalar(stripQuotes(rest.join(':').trim()));
  }
  return out;
}

// T657 (SEC-T655-01): per-platform rendering of an MCP tool name in an agent's tool list.
// The source form stays `mcp__<server>` (a whole server) and `mcp__<server>__<tool>` (one tool),
// with `*` allowed as the tool part. A platform opts in with `frontmatter.agents.mcpToolNames`;
// no key, or `verbatim`, keeps the source form. Each style is backed by vendor documentation or
// vendor source recorded in docs/artifacts/mcp-tool-name-mapping-v1.md; a platform whose naming
// is not verified must not opt in.
//   slash       Copilot / VS Code: `<server>/<tool>` and `<server>/*`
//               (server lower-cased, whitespace to `-`; `.` in the tool to `_`)
//   underscore  Opencode: `<server>_<tool>` and `<server>_*` (anything outside [A-Za-z0-9_-] to `_`)
//   pi          Pi: `mcp__<server>__<tool>` and `mcp__<server>__*` (anything outside [A-Za-z0-9_] to `_`)
const MCP_TOOL_PREFIX = 'mcp__';

// T658 (SEC-T657-09): `*` is accepted only as the whole tool part (`mcp__<server>__*`). A `*` anywhere
// else (`mcp__srv__foo*`, `mcp__sr*v__t`) used to degrade silently to `_` in the renderers, which
// fails closed but hides the author's mistake; it now stops the run.
function splitMcpToolName(token) {
  if (typeof token !== 'string' || !token.startsWith(MCP_TOOL_PREFIX)) return null;
  const rest = token.slice(MCP_TOOL_PREFIX.length);
  const sep = rest.indexOf('__');
  if (sep === -1) {
    if (rest.includes('*')) throw new Error(`Non-terminal '*' in MCP tool token: ${token}`);
    return rest ? { server: rest, tool: '*' } : null;
  }
  const server = rest.slice(0, sep);
  const tool = rest.slice(sep + 2);
  if (server.includes('*') || (tool !== '*' && tool.includes('*'))) {
    throw new Error(`Non-terminal '*' in MCP tool token: ${token}`);
  }
  return server && tool ? { server, tool } : null;
}

const MCP_TOOL_NAME_STYLES = {
  verbatim: null,
  slash: ({ server, tool }) => {
    const srv = server.toLowerCase().replace(/\s+/g, '-');
    return tool === '*' ? `${srv}/*` : `${srv}/${tool.replace(/\./g, '_')}`;
  },
  underscore: ({ server, tool }) => {
    const clean = (s) => s.replace(/[^a-zA-Z0-9_-]/g, '_');
    return tool === '*' ? `${clean(server)}_*` : `${clean(server)}_${clean(tool)}`;
  },
  pi: ({ server, tool }) => {
    const clean = (s) => s.replace(/[^a-zA-Z0-9_]/g, '_');
    return `mcp__${clean(server)}__${tool === '*' ? '*' : clean(tool)}`;
  },
};

// T658 (SEC-T657-09): the style is validated once, at manifest load, whether or not the platform
// has a tools line to render. An unknown or non-string value stops the run before any file is written.
function validateMcpToolNamesStyle(manifest) {
  const style = manifest.frontmatter && manifest.frontmatter.agents
    ? manifest.frontmatter.agents.mcpToolNames
    : undefined;
  const denies = manifest.frontmatter && manifest.frontmatter.agents
    ? manifest.frontmatter.agents.mcpAgentDenies
    : undefined;
  // T663: per-agent denies are written in the `underscore` form and only where the tools are an object
  if (denies !== undefined && (denies !== true || style !== 'underscore' || manifest.frontmatter.agents.tools !== 'object')) {
    throw new Error(`mcpAgentDenies needs true, mcpToolNames "underscore" and tools "object" (platform ${manifest.platform})`);
  }
  if (style === undefined) return;
  if (typeof style !== 'string' || !Object.prototype.hasOwnProperty.call(MCP_TOOL_NAME_STYLES, style)) {
    throw new Error(`Unknown mcpToolNames style: ${String(style)} (platform ${manifest.platform})`);
  }
}

// T663: names of the per-agent `false` entries for one agent, in the Opencode `underscore` form.
// `sourceTools` is the agent's tool list in the source form (`mcp__<server>[__<tool>]`);
// `renderedTools` is the list that will be written as `true`. Returns `{ first, last }`:
//   last   the exact denied names (`denyTools` of every server, for every agent), followed by the
//          server wildcard of every `denyUnlessGranted` server this agent holds no token for;
//          written AFTER every allow, so a deny survives any broader allow of the agent.
//   first  the server wildcard of every `denyUnlessGranted` server this agent holds only NAMED tools
//          of (`mcp__<server>__<tool>`, no bare `mcp__<server>`): written BEFORE the allows, so the
//          named allows that follow it are the only tools of the server the agent can call. Here the
//          file order, not a distinct name, is what makes the pair safe (last match wins).
// A holder of the whole server gets neither. Throws when the agent would hold an allow and a deny of
// the same name: the generator never writes both.
function agentMcpDenials(sourceTools, renderedTools, servers, tags) {
  const whole = new Set();
  const named = new Set();
  for (const token of Array.isArray(sourceTools) ? sourceTools : []) {
    const parts = splitMcpToolName(token);
    if (!parts) continue;
    (parts.tool === '*' ? whole : named).add(parts.server);
  }
  const first = [];
  const last = [];
  for (const [server, def] of Object.entries(servers)) {
    if (!(def.tags || []).some((t) => tags.includes(t))) continue;
    if (def.denyUnlessGranted === true && !whole.has(server)) {
      const wildcard = MCP_TOOL_NAME_STYLES.underscore({ server, tool: '*' });
      (named.has(server) ? first : last).push(wildcard);
    }
    for (const tool of def.denyTools || []) last.push(MCP_TOOL_NAME_STYLES.underscore({ server, tool }));
  }
  const result = { first: [...new Set(first)], last: [...new Set(last)] };
  const allowed = new Set(Array.isArray(renderedTools) ? renderedTools : []);
  const clash = [...result.first, ...result.last].find((d) => allowed.has(d));
  if (clash) throw new Error(`An agent tool list both grants and denies ${clash}`);
  return result;
}

function renderMcpToolName(token, style) {
  if (!style) return token;
  if (!Object.prototype.hasOwnProperty.call(MCP_TOOL_NAME_STYLES, style)) {
    throw new Error(`Unknown mcpToolNames style: ${style}`);
  }
  const render = MCP_TOOL_NAME_STYLES[style];
  const parts = render ? splitMcpToolName(token) : null;
  return parts ? render(parts) : token;
}

function renderMcpToolList(tools, style) {
  if (!Array.isArray(tools) || !style || style === 'verbatim') return tools;
  return [...new Set(tools.map((t) => renderMcpToolName(t, style)))];
}

// The agent's tool list in the source form, as an array of names (an object form keeps its true entries).
function sourceToolList(data) {
  const tools = data.tools;
  if (tools && !Array.isArray(tools) && typeof tools === 'object') {
    return Object.entries(tools).filter(([, v]) => v).map(([k]) => k);
  }
  return Array.isArray(tools) ? tools : [];
}

function applyAgentFrontmatter(data, name, cfg) {
  const out = {};
  for (const k of cfg.keepKeys || Object.keys(data)) {
    if (data[k] !== undefined) out[k] = data[k];
  }

  let tools = data.tools;
  if (tools && !Array.isArray(tools) && typeof tools === 'object') {
    tools = Object.entries(tools)
      .filter(([, v]) => v)
      .map(([k]) => k);
  }

  if (cfg.tools === 'drop') {
    delete out.tools;
  } else if (cfg.tools === 'object') {
    if (Array.isArray(tools)) out.tools = tools;
  } else if (cfg.tools === 'string') {
    if (Array.isArray(tools)) {
      const toolMap = cfg.toolMap || {};
      const expanded = tools.flatMap((t) =>
        Object.prototype.hasOwnProperty.call(toolMap, t)
          ? toolMap[t].split(',').map((s) => s.trim())
          : [t]
      );
      out.tools = [...new Set(expanded)];
    }
  } else {
    if (Array.isArray(tools)) out.tools = tools;
  }
  out.tools = renderMcpToolList(out.tools, cfg.mcpToolNames);
  if (out.tools === undefined) delete out.tools;

  if (cfg.addToOrchestrators && (cfg.orchestratorNames || []).includes(name)) {
    Object.assign(out, cfg.addToOrchestrators);
  }

  return out;
}

function applyGenericFrontmatter(data, cfg) {
  const out = {};
  const renamed = { ...data };
  for (const [from, to] of Object.entries(cfg.renameKeys || {})) {
    if (renamed[from] !== undefined) {
      renamed[to] = renamed[from];
      delete renamed[from];
    }
  }
  for (const k of cfg.keepKeys || Object.keys(renamed)) {
    if (renamed[k] !== undefined) out[k] = renamed[k];
  }
  return out;
}

// Per-format MCP config emitters (T677: emitMcp was one 134-line function; behaviour is unchanged).
// Each takes the servers already filtered for the platform's tags and the format name.
  // T665 placeholder-form check (the T664 token-handling design, finding F-3):
  //   vscode  `${env:VAR}` is documented through the MCP page's pointer to the variables reference
  //           and resolved by the shared configuration resolver; behaviour for an UNSET variable is unverified.
  //   pi      `${VAR}` (T680). Run on @earendil-works/pi-coding-agent 0.99.0, 1.0.0, 1.3.0 and 1.4.0
  //           (`pi mcp list --json`, a stdio server that recorded its environment): `${VAR}` and `$VAR` are
  //           expanded in `env` and `headers` values, `${env:VAR}` and `${VAR:-}` stay literal text, an unset
  //           or EMPTY variable fails the server (it is not started, a fail-closed error), a `url` is
  //           never expanded (a templated one is rejected as "url must be an http or https URL"), and a
  //           stdio server inherits Pi's own environment. So a variable marked `optional` is left out of
  //           `env` (the server still receives it when it is set); an optional `headers` value is refused. Documented in
  //           implementation/PREREQUISITES.md and docs/wiki/mcp-servers.md; the verified forms table is there.
  //   cline   `${env:VAR}` is expanded by the VS Code extension (McpHub.ts expandEnvironmentVariables);
  //           an unset variable stays literal; the CLI/SDK loader was not shown to expand it (unverified).
function emitMcpVscodePi(filtered, format) {
  // pi: `${VAR}` and optional variables are left out (see above); vscode: `${env:VAR}`, unchanged.
  const template = format === 'pi' ? '${VAR}' : '${env:VAR}';
  const mapEnvValues = (m) => (format === 'pi' ? mapEnvOmitOptional(m, template) : mapEnv(m, template));
  const out = { servers: format === 'vscode' ? {} : undefined, mcpServers: format === 'pi' ? {} : undefined };
  const target = format === 'vscode' ? out.servers : out.mcpServers;
  for (const [name, s] of Object.entries(filtered)) {
    if (s.transport === 'remote') {
      const url = mapTemplatedValue(s.url, template);
      target[name] = format === 'vscode' ? { type: 'http', url } : { url };
      if (s.headers) target[name].headers = mapEnv(s.headers, template);
    } else {
      target[name] = { command: s.command, args: s.args || [] };
      const env = s.env ? mapEnvValues(s.env) : undefined;
      if (env && (format === 'vscode' || Object.keys(env).length > 0)) target[name].env = env;
    }
  }
  return JSON.stringify(format === 'vscode' ? { servers: target } : { mcpServers: target }, null, 2) + '\n';
}

// The Gemini CLI hook block written next to its MCP servers.
const GEMINI_POST_EDIT_HOOKS = {
  AfterTool: [
    {
      matcher: 'replace|write_file',
      hooks: [
        {
          name: 'post-edit-reminder',
          type: 'command',
          command:
            "echo '{\"systemMessage\": \"Reminder: Ensure code follows coding standards (naming, error handling, security). Run lint before committing.\"}'",
        },
      ],
    },
  ],
};

function emitMcpGemini(filtered) {
  // T665 (SEC-T660-01, F-3): Gemini CLI documents `$VAR` and `${VAR}` (and `${VAR:-DEFAULT}`) and its
  // resolver (packages/cli/src/utils/envVarResolver.ts, read at main on 2026-10-16) looks the text
  // between the braces up as the variable NAME, so `${env:VAR}` is looked up as `env:VAR`, found
  // nowhere, left as text by the settings loader and then expanded to an empty string by the MCP
  // client (dotenv-expand). `${VAR}` is the documented form. Source read, not run.
  const mcpServers = {};
  for (const [name, s] of Object.entries(filtered)) {
    if (s.transport === 'remote') {
      mcpServers[name] = { httpUrl: mapTemplatedValue(s.url, '${VAR}') };
      if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${VAR}');
    } else {
      mcpServers[name] = { command: s.command, args: s.args || [] };
      if (s.env) mcpServers[name].env = mapEnv(s.env, '${VAR}');
    }
    // T658: documented per-server tool blocklist; applies to the main agent and to subagents
    // (docs/artifacts/mcp-server-denials-v1.md). Gemini matches the name the server reports.
    if (s.denyTools) mcpServers[name].excludeTools = [...s.denyTools];
  }
  return JSON.stringify({ hooks: GEMINI_POST_EDIT_HOOKS, mcpServers }, null, 2) + '\n';
}

function emitMcpOpencode(filtered) {
  const mcp = {};
  const permission = {};
  for (const [name, s] of Object.entries(filtered)) {
    // T658: Opencode checks a permission whose action is the registered tool name
    // `<server>_<tool>`; the same cleaning as the `underscore` tool-name style. Last match wins,
    // and the agent-level rules come after this global one (docs/artifacts/mcp-server-denials-v1.md).
    for (const tool of s.denyTools || []) {
      permission[MCP_TOOL_NAME_STYLES.underscore({ server: name, tool })] = 'deny';
    }
    if (s.transport === 'remote') {
      mcp[name] = { type: 'remote', url: mapTemplatedValue(s.url, '{env:VAR}') };
      if (s.headers) mcp[name].headers = mapEnv(s.headers, '{env:VAR}');
    } else {
      mcp[name] = { type: 'local', command: [s.command, ...(s.args || [])] };
      if (s.env) mcp[name].environment = mapEnv(s.env, '{env:VAR}');
    }
  }
  return { __mcpObject: mcp, __permission: permission };
}

function emitMcpClaudeCode(filtered) {
  // Claude Code expands `${VAR}` / `${VAR:-default}` from the live process environment in
  // `command`, `args`, `env`, `url` and `headers` — it does NOT recognise VS Code's
  // `${env:VAR}` form and passes such text through literally (T517; see
  // docs/artifacts/mcp-header-url-templating-design-v2.md §3 and
  // https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json).
  const mcpServers = {};
  for (const [name, s] of Object.entries(filtered)) {
    if (s.transport === 'remote') {
      mcpServers[name] = { type: 'http', url: mapTemplatedValue(s.url, '${VAR}', true) };
      if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${VAR}', true);
    } else {
      mcpServers[name] = { command: s.command, args: s.args || [] };
      if (s.env) mcpServers[name].env = mapEnv(s.env, '${VAR}', true);
    }
  }
  return JSON.stringify({ mcpServers }, null, 2) + '\n';
}

function emitMcpCline(filtered) {
  const mcpServers = {};
  for (const [name, s] of Object.entries(filtered)) {
    if (s.transport === 'remote') {
      mcpServers[name] = { type: 'streamableHttp', url: mapTemplatedValue(s.url, '${env:VAR}') };
      if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${env:VAR}');
    } else {
      mcpServers[name] = { command: s.command, args: s.args || [] };
      if (s.env) mcpServers[name].env = mapEnv(s.env, '${env:VAR}');
    }
  }
  return JSON.stringify({ mcpServers }, null, 2) + '\n';
}

const MCP_EMITTERS = new Map([
  ['vscode', emitMcpVscodePi],
  ['pi', emitMcpVscodePi],
  ['gemini', emitMcpGemini],
  ['opencode', emitMcpOpencode],
  ['claude-code', emitMcpClaudeCode],
  ['cline', emitMcpCline],
]);

function emitMcp(servers, tags, format) {
  const filtered = Object.fromEntries(
    Object.entries(servers).filter(([, s]) => emittedFor(s, tags, format))
  );
  const emitter = MCP_EMITTERS.get(format);
  if (!emitter) throw new Error(`Unknown MCP format: ${format}`);
  return emitter(filtered, format);
}

// Renders one templated-value spec (see design mcp-header-url-templating-design-v1.md §3/§4)
// against a platform's own env-placeholder pattern.
//   spec: a plain literal (string/number/bool) -> returned unchanged (String(spec))
//         OR { fromEnv: VAR }                   -> template.replace('VAR', VAR)
//         OR { fromEnv: VAR, wrap: "X{VAR}Y" }   -> wrap.replace('{VAR}', <rendered above>)
//         OR { fromEnv: VAR, default: "D" }      -> with `withDefault`: VAR becomes `VAR:-D`
//         OR { fromEnv: VAR, optional: true }    -> with `withDefault`: VAR becomes `VAR:-` (T680)
//   template: the platform's own placeholder pattern, e.g. '${env:VAR}' (vscode/pi/cline),
//             '{env:VAR}' (opencode) or '${VAR}' (claude-code, gemini)
//   withDefault: true only for the claude-code format (T665, SEC-T660-01): Claude Code passes an
//             unset `${VAR}` through as literal text and documents `${VAR:-default}`; no other
//             format is documented to honour a default, so those render as before.
function mapTemplatedValue(spec, template, withDefault = false) {
  if (spec && typeof spec === 'object' && spec.fromEnv) {
    const fallback = typeof spec.default === 'string' ? spec.default : spec.optional === true ? '' : undefined;
    const name = withDefault && fallback !== undefined ? `${spec.fromEnv}:-${fallback}` : spec.fromEnv;
    const rendered = template.replace('VAR', () => name);
    return spec.wrap ? spec.wrap.replace('{VAR}', () => rendered) : rendered;
  }
  return String(spec);
}

function mapEnv(envSpec, template, withDefault = false) {
  const out = {};
  for (const [k, v] of Object.entries(envSpec)) out[k] = mapTemplatedValue(v, template, withDefault);
  return out;
}

// T680: like mapEnv, but a value marked `optional: true` is left out (pi throws for an unset or empty
// variable, and a stdio server inherits Pi's environment, so a variable that is set still reaches it).
// Only `env` is rendered through this: an optional `headers` value is refused by validateTemplatedSpecs.
function mapEnvOmitOptional(envSpec, template) {
  const out = {};
  for (const [k, v] of Object.entries(envSpec)) {
    if (v && typeof v === 'object' && v.optional === true) continue;
    out[k] = mapTemplatedValue(v, template);
  }
  return out;
}

async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const results = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) results.push(...(await walk(full)));
    else results.push(full);
  }
  return results.sort();
}

async function writeFile(absPath, content) {
  await fs.mkdir(path.dirname(absPath), { recursive: true });
  await fs.writeFile(absPath, content);
}

const driftReports = [];
async function emitFile(absPath, content) {
  if (CHECK_ONLY) {
    const expected = Buffer.isBuffer(content) ? content : Buffer.from(content);
    let existing = null;
    try {
      existing = await fs.readFile(absPath);
    } catch {
      // missing file means drift
    }
    const matchesExactly = !!existing && existing.equals(expected);
    const matchesNormalizedText =
      !!existing && normalizeTextBuffer(existing) === normalizeTextBuffer(expected);
    if (!existing || (!matchesExactly && !matchesNormalizedText)) driftReports.push(absPath);
    return;
  }
  await writeFile(absPath, content);
}

// T672 (SEC-T672-08): every path a manifest names resolves strictly under ROOT (not ROOT itself): the
// generator `rm -rf`s outputDir and writes the rest, so a manifest with outputDir "." or "../x" must
// stop the run before the first write, like any other invalid manifest.
function assertUnderRoot(label, resolved) {
  const rootWithSep = ROOT.endsWith(path.sep) ? ROOT : ROOT + path.sep;
  if (resolved === ROOT || !resolved.startsWith(rootWithSep)) {
    throw new Error(`Refusing ${label} outside or equal to ROOT: ${resolved}`);
  }
}

function assertUnder(label, resolved, base) {
  const baseWithSep = base.endsWith(path.sep) ? base : base + path.sep;
  if (resolved === base || !resolved.startsWith(baseWithSep)) {
    throw new Error(`Refusing ${label} outside or equal to ${base}: ${resolved}`);
  }
}

// The directory a manifest's instructions are written to. A rootRelative target outside ROOT, or ROOT
// itself, is refused.
function instructionsRoot(manifest, outRoot) {
  const insMap = manifest.fileMap.instructions;
  const insRoot = insMap.rootRelative ? path.resolve(ROOT, insMap.dir) : path.resolve(outRoot, insMap.dir);
  if (insMap.rootRelative) {
    const rootWithSep = ROOT.endsWith(path.sep) ? ROOT : ROOT + path.sep;
    if (insRoot === ROOT || !insRoot.startsWith(rootWithSep)) {
      throw new Error(`Refusing rootRelative fileMap target outside or equal to ROOT: ${insRoot}`);
    }
  }
  return insRoot;
}

// Called from the validation pass of main(), before the first write.
function validateManifestPaths(manifest) {
  const outRoot = path.resolve(ROOT, manifest.outputDir);
  assertUnderRoot(`outputDir of ${manifest.platform}`, outRoot);
  instructionsRoot(manifest, outRoot);
  for (const [kind, map] of Object.entries(manifest.fileMap)) {
    if (kind === 'instructions' && map.rootRelative) continue;
    assertUnder(`fileMap.${kind}.dir of ${manifest.platform}`, path.resolve(outRoot, map.dir), outRoot);
  }
  if (manifest.mcp) {
    assertUnderRoot(`mcp.outputFile of ${manifest.platform}`, path.resolve(outRoot, manifest.mcp.outputFile));
  }
  for (const extra of manifest.extras || []) {
    assertUnder(`extras.to of ${manifest.platform}`, path.resolve(outRoot, extra.to), outRoot);
    assertUnder(`extras.from of ${manifest.platform}`, path.resolve(EXTRAS, extra.from.replace(/^_extras\//, '')), EXTRAS);
  }
}

function overlaps(a, b) {
  const aSep = a.endsWith(path.sep) ? a : a + path.sep;
  const bSep = b.endsWith(path.sep) ? b : b + path.sep;
  return a === b || a.startsWith(bSep) || b.startsWith(aSep);
}

// T682 (N-5): the directories a manifest makes the generator `rm -rf`: its outputDir and, for Cline,
// the rootRelative instructions directory.
function removalTargets(manifest) {
  const outRoot = path.resolve(ROOT, manifest.outputDir);
  const targets = [{ label: `outputDir of ${manifest.platform}`, dir: outRoot }];
  if (manifest.fileMap.instructions.rootRelative) {
    targets.push({ label: `fileMap.instructions.dir of ${manifest.platform}`, dir: instructionsRoot(manifest, outRoot) });
  }
  return targets;
}

// T684 (SEC-T682-04): the files a manifest's mcp block writes: the config and its provenance sidecar.
function mcpFiles(manifest) {
  if (!manifest.mcp) return [];
  const outPath = path.resolve(path.resolve(ROOT, manifest.outputDir), manifest.mcp.outputFile);
  return [
    { label: `mcp.outputFile of ${manifest.platform}`, dir: outPath, file: true },
    { label: `mcp.outputFile provenance of ${manifest.platform}`, dir: outPath + '.provenance.json', file: true },
  ];
}

// T684 (SEC-T682-04): the physical, case-folded form of a path that need not exist yet, for the overlap
// checks below: the nearest existing ancestor is resolved with fs.realpath and the components below it are
// appended as given; a dangling symlink is followed by hand (readlink), at most 40 hops (a defensive
// bound: realpath reports ELOOP for a cycle first). The result is
// NFC-normalised and lower-cased, so `Scripts` and `scripts` are one place on a case-insensitive file
// system; on a case-sensitive one that is a false positive, which only makes the check stricter.
// Remaining limits (documented, not closed): the check runs once before the first write, so a link
// swapped in afterwards (a race with another process) is not seen; hard links and bind mounts are not
// resolved; the folding is toLowerCase, not the file system's own table; a path that cannot be resolved
// for another reason (EACCES, ELOOP) is refused, never skipped.
async function physicalFolded(target) {
  let current = path.resolve(target);
  let rest = '';
  for (let hops = 0; hops < 40; ) {
    try {
      return (await fs.realpath(current) + rest).normalize('NFC').toLowerCase();
    } catch (error) {
      if (error.code !== 'ENOENT' && error.code !== 'ENOTDIR') {
        throw new Error(`Refusing ${target}: cannot resolve ${current} (${error.code || error.message})`);
      }
    }
    let link = null;
    try {
      link = await fs.readlink(current);
    } catch {
      // not a symlink: the component is simply missing
    }
    if (link !== null) {
      hops += 1;
      current = path.resolve(path.dirname(current), link);
      continue;
    }
    const parent = path.dirname(current);
    if (parent === current) return (current + rest).normalize('NFC').toLowerCase();
    rest = path.sep + path.basename(current) + rest;
    current = parent;
  }
  throw new Error(`Refusing ${target}: more than 40 symbolic links to follow`);
}

// T682 (N-5), T684 (SEC-T682-04): assertUnderRoot only keeps a path inside ROOT. A target that equals,
// contains or lies inside a generator input (knowledge, platforms, _extras, scripts, runtime, the
// generator's own directory) would be deleted before it is read, an mcp.outputFile (or its
// .provenance.json sidecar) that equals or lies inside one would overwrite it, and two manifests whose
// trees overlap would delete each other's output. Each pair is compared lexically and again in its
// physical, case-folded form (physicalFolded: a symlinked outputDir that leads into an input is caught).
// Called from the validation pass, over every manifest, before the first write.
async function assertNoOverlappingTargets(manifests) {
  const inputs = [KNOWLEDGE, PLATFORMS, EXTRAS, path.resolve(ROOT, 'scripts'), path.resolve(ROOT, 'runtime'), __dirname];
  const physicalInputs = await Promise.all(inputs.map(physicalFolded));
  const targets = manifests.flatMap(removalTargets);
  const files = manifests.flatMap(mcpFiles);
  const guarded = [...targets, ...files];
  for (const item of guarded) item.physical = await physicalFolded(item.dir);
  guarded.forEach((item, index) => {
    inputs.forEach((input, at) => {
      if (overlaps(item.dir, input) || overlaps(item.physical, physicalInputs[at])) {
        throw new Error(`Refusing ${item.label}: ${item.dir} overlaps the generator input ${input}`);
      }
    });
    if (item.file) return;
    for (const other of targets.slice(index + 1)) {
      if (overlaps(item.dir, other.dir) || overlaps(item.physical, other.physical)) {
        throw new Error(`Refusing ${item.label}: ${item.dir} overlaps ${other.label} (${other.dir})`);
      }
    }
  });
}

// T677: syncPlatform was one 131-line function; each step below is one section of it, in the same order.
// Every step appends the paths it emitted to `filesWritten`.
async function syncAgents(manifest, outRoot, servers, filesWritten) {
  const agentMap = manifest.fileMap.agents;
  const agentCfg = manifest.frontmatter.agents;
  for (const file of await walk(path.join(KNOWLEDGE, 'agents'))) {
    if (!file.endsWith('.md')) continue;
    const baseName = path.basename(file, '.md');
    const raw = await fs.readFile(file, 'utf8');
    const { data, body } = parseFrontmatter(raw);
    const newData = applyAgentFrontmatter(data, baseName, agentCfg);
    const denies = agentCfg.mcpAgentDenies === true && manifest.mcp
      ? agentMcpDenials(sourceToolList(data), newData.tools, servers, manifest.mcp.tags)
      : { first: [], last: [] };
    const fm = emitFrontmatter(newData, {
      toolsFormat: agentCfg.tools === 'object' ? 'object' : agentCfg.tools === 'string' ? 'string' : 'array',
      denyFirst: denies.first,
      denyTools: denies.last,
    });
    const outPath = path.join(outRoot, agentMap.dir, baseName + agentMap.ext);
    await emitFile(outPath, fm + body);
    filesWritten.push(outPath);
  }
}

async function syncCommands(manifest, outRoot, filesWritten) {
  const cmdMap = manifest.fileMap.commands;
  for (const file of await walk(path.join(KNOWLEDGE, 'commands'))) {
    if (!file.endsWith('.md')) continue;
    const baseName = path.basename(file, '.md');
    const raw = await fs.readFile(file, 'utf8');
    const { data, body } = parseFrontmatter(raw);
    const newData = applyGenericFrontmatter(data, manifest.frontmatter.commands);
    const outPath = path.join(outRoot, cmdMap.dir, baseName + cmdMap.ext);
    await emitFile(outPath, emitFrontmatter(newData) + body);
    filesWritten.push(outPath);
  }
}

async function syncInstructions(manifest, outRoot, filesWritten) {
  const insMap = manifest.fileMap.instructions;
  const insRoot = instructionsRoot(manifest, outRoot);
  if (insMap.rootRelative) {
    if (!CHECK_ONLY) {
      await fs.rm(insRoot, { recursive: true, force: true });
    }
  }
  for (const file of await walk(path.join(KNOWLEDGE, 'instructions'))) {
    if (!file.endsWith('.md')) continue;
    const baseName = path.basename(file, '.md');
    const raw = await fs.readFile(file, 'utf8');
    const { data, body } = parseFrontmatter(raw);
    const newData = applyGenericFrontmatter(data, manifest.frontmatter.instructions);
    const outPath = path.join(insRoot, baseName + insMap.ext);
    await emitFile(outPath, emitFrontmatter(newData) + body);
    filesWritten.push(outPath);
  }
}

async function syncSkills(manifest, outRoot, filesWritten) {
  const skillMap = manifest.fileMap.skills;
  const skillsRoot = path.join(KNOWLEDGE, 'skills');
  for (const file of await walk(skillsRoot)) {
    const rel = path.relative(skillsRoot, file);
    const outPath = path.join(outRoot, skillMap.dir, rel);
    if (file.endsWith('SKILL.md')) {
      const raw = await fs.readFile(file, 'utf8');
      const { data, body } = parseFrontmatter(raw);
      const newData = applyGenericFrontmatter(data, manifest.frontmatter.skills);
      await emitFile(outPath, emitFrontmatter(newData) + body);
    } else {
      const raw = await fs.readFile(file);
      await emitFile(outPath, raw);
    }
    filesWritten.push(outPath);
  }
}

async function syncMcp(manifest, outRoot, servers, filesWritten) {
  const mcpResult = emitMcp(servers, manifest.mcp.tags, manifest.mcp.format);
  const outPath = path.resolve(outRoot, manifest.mcp.outputFile);
  if (manifest.mcp.format === 'opencode') {
    const cfg = { ...(manifest.mcp.extraFields || {}), mcp: mcpResult.__mcpObject };
    if (Object.keys(mcpResult.__permission).length > 0) cfg.permission = mcpResult.__permission;
    await emitFile(outPath, JSON.stringify(cfg, null, 2) + '\n');
  } else {
    await emitFile(outPath, mcpResult);
  }
  filesWritten.push(outPath);

  // ADR-002: emit a <mcpfile>.provenance.json sidecar recording the
  // generator-owned server-key set, so merge-mcp-json.py can diff old vs.
  // new provenance and safely prune a retired dest-only key without ever
  // touching a hand-added one. Recomputed inline (rather than changed via
  // emitMcp()'s return contract) to keep the 5 already-passing call sites'
  // return shape untouched.
  const filteredKeys = Object.entries(servers)
    .filter(([, s]) => emittedFor(s, manifest.mcp.tags, manifest.mcp.format))
    .map(([name]) => name)
    .sort();
  const sidecarPath = outPath + '.provenance.json';
  const sidecarContent = JSON.stringify({ schemaVersion: 1, generatorOwnedKeys: filteredKeys }, null, 2) + '\n';
  await emitFile(sidecarPath, sidecarContent);
  filesWritten.push(sidecarPath);
}

async function syncExtras(manifest, outRoot, filesWritten) {
  for (const extra of manifest.extras || []) {
    const src = path.resolve(EXTRAS, extra.from.replace(/^_extras\//, ''));
    const dst = path.join(outRoot, extra.to);
    const content = await fs.readFile(src);
    await emitFile(dst, content);
    filesWritten.push(dst);
  }
}

async function writeGeneratedManifest(manifest, outRoot, filesWritten) {
  const manifestPath = path.join(outRoot, '.generated-manifest.json');
  const manifestContent = JSON.stringify(
    {
      generatedFrom: path.relative(ROOT, KNOWLEDGE) + '/',
      platform: manifest.platform,
      generatedAt: '<deterministic>',
      files: filesWritten.map((f) => toPosixPath(path.relative(outRoot, f))).sort(),
    },
    null,
    2
  ) + '\n';
  await emitFile(manifestPath, manifestContent);
}

async function syncPlatform(manifest, servers) {
  const outRoot = path.resolve(ROOT, manifest.outputDir);
  const filesWritten = [];

  if (!CHECK_ONLY) {
    await fs.rm(outRoot, { recursive: true, force: true });
  }

  if (manifest.fileMap.agents) await syncAgents(manifest, outRoot, servers, filesWritten);
  if (manifest.fileMap.commands) await syncCommands(manifest, outRoot, filesWritten);
  await syncInstructions(manifest, outRoot, filesWritten);
  await syncSkills(manifest, outRoot, filesWritten);
  if (manifest.mcp) await syncMcp(manifest, outRoot, servers, filesWritten);
  await syncExtras(manifest, outRoot, filesWritten);
  await writeGeneratedManifest(manifest, outRoot, filesWritten);

  return filesWritten.length;
}

async function listPlatformFiles() {
  try {
    await fs.access(KNOWLEDGE);
    await fs.access(PLATFORMS);
  } catch {
    console.error(`Missing required inputs under root ${ROOT}`);
    console.error(`Expected directories: ${KNOWLEDGE} and ${PLATFORMS}`);
    process.exit(1);
  }

  // Only the manifest schema is skipped; any other `_*.json` in platforms/ is a mistake and stops the run (T672).
  const platformFiles = (await fs.readdir(PLATFORMS))
    .filter((f) => f.endsWith('.json') && f !== MANIFEST_SCHEMA_FILE)
    .sort();
  const stray = platformFiles.filter((f) => f.startsWith('_'));
  if (stray.length > 0) {
    throw new Error(`platforms/ holds ${stray.join(', ')}: only ${MANIFEST_SCHEMA_FILE} may start with an underscore`);
  }
  return platformFiles;
}

// T663 (SEC-T658-07 b): every manifest is read and validated before the first file is written.
async function loadManifests(platformFiles) {
  const manifests = [];
  for (const file of platformFiles) {
    const manifest = JSON.parse(await fs.readFile(path.join(PLATFORMS, file), 'utf8'));
    validateMcpToolNamesStyle(manifest);
    validateManifestPaths(manifest);
    manifests.push(manifest);
  }
  await assertNoOverlappingTargets(manifests);
  return manifests;
}

function reportResult(total) {
  if (!CHECK_ONLY) {
    console.log(`\nDone - ${total} files written.`);
    return;
  }
  if (driftReports.length) {
    console.error(`\nDRIFT DETECTED in ${driftReports.length} file(s):`);
    for (const f of driftReports.sort()) {
      console.error(`  - ${path.relative(ROOT, f)}`);
    }
    console.error('\nRun `node scripts/sync.mjs` to regenerate.');
    process.exit(1);
  }
  console.log(`\nOK - no drift across ${total} files.`);
}

async function main() {
  const platformFiles = await listPlatformFiles();
  const servers = await readServersYaml();
  let total = 0;

  const manifests = await loadManifests(platformFiles);

  for (const manifest of manifests) {
    if (ONLY_PLATFORM && manifest.platform !== ONLY_PLATFORM) continue;
    const count = await syncPlatform(manifest, servers);
    console.log(`[${manifest.platform}] ${CHECK_ONLY ? 'checked' : 'wrote'} ${count} files -> ${manifest.outputDir}`);
    total += count;
  }

  reportResult(total);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
