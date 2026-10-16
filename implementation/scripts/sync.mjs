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
const ROOT = rootArg
  ? (path.isAbsolute(rootArg) ? rootArg : path.resolve(process.cwd(), rootArg))
  : path.resolve(__dirname, '..');
const KNOWLEDGE = path.resolve(ROOT, String(args.knowledge || 'knowledge'));
const PLATFORMS = path.resolve(ROOT, String(args.platforms || 'platforms'));
const EXTRAS = path.resolve(ROOT, String(args.extras || '_extras'));

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
  'tags', 'transport', 'command', 'args', 'env', 'url', 'headers', 'denyTools', 'denyUnlessGranted',
]);

function validateDenyTools(servers) {
  for (const [name, server] of Object.entries(servers)) {
    const unknown = Object.keys(server).filter((k) => !SERVER_KEYS.has(k));
    if (unknown.length > 0) {
      throw new Error(`servers.yaml: ${name} has an unknown key: ${unknown.map((k) => k.slice(0, 40)).join(', ')}`);
    }
    if (server.denyUnlessGranted !== undefined && typeof server.denyUnlessGranted !== 'boolean') {
      throw new Error(`servers.yaml: ${name}.denyUnlessGranted must be the boolean true or false (or absent)`);
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

function parseServersYaml(raw) {
  const lines = raw.split(/\r?\n/);
  const servers = {};
  let i = 0;
  while (i < lines.length && !lines[i].trim().startsWith('servers:')) i++;
  i++;
  let current = null;
  let openBlock = null;
  let openBlockKey = null;

  while (i < lines.length) {
    const ln = lines[i];
    if (!ln.trim() || ln.trim().startsWith('#')) {
      i++;
      continue;
    }
    const m2 = ln.match(/^  ([A-Za-z0-9._-]+):\s*$/);
    if (m2) {
      current = m2[1];
      servers[current] = {};
      openBlock = null;
      openBlockKey = null;
      i++;
      continue;
    }

    if (current && openBlock !== null) {
      const me = ln.match(/^      ([A-Za-z0-9_-]+):\s*(.*)$/);
      if (me) {
        servers[current][openBlockKey][me[1]] = parseInlineObject(me[2]);
        i++;
        continue;
      }
      openBlock = null;
      openBlockKey = null;
    }

    if (current) {
      const me2 = ln.match(/^    ([A-Za-z0-9_-]+):\s*(.*)$/);
      if (me2) {
        const [, key, rest] = me2;
        if (BLOCK_KEYS.has(key) && rest === '') {
          openBlock = {};
          openBlockKey = key;
          servers[current][key] = openBlock;
        } else if (rest.startsWith('[') && rest.endsWith(']')) {
          servers[current][key] = splitInlineArray(rest.slice(1, -1)).map((s) => stripQuotes(s.trim()));
        } else if (rest.startsWith('{') && rest.endsWith('}')) {
          servers[current][key] = parseInlineObject(rest);
        } else {
          servers[current][key] = parseScalar(stripQuotes(rest));
        }
        i++;
        continue;
      }
    }

    i++;
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
  return parts;
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

function emitMcp(servers, tags, format) {
  const filtered = Object.fromEntries(
    Object.entries(servers).filter(([, s]) => (s.tags || []).some((t) => tags.includes(t)))
  );

  if (format === 'vscode' || format === 'pi') {
    const out = { servers: format === 'vscode' ? {} : undefined, mcpServers: format === 'pi' ? {} : undefined };
    const target = format === 'vscode' ? out.servers : out.mcpServers;
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') {
        const url = mapTemplatedValue(s.url, '${env:VAR}');
        if (format === 'vscode') {
          target[name] = { type: 'http', url };
          if (s.headers) target[name].headers = mapEnv(s.headers, '${env:VAR}');
        } else {
          target[name] = { url };
          if (s.headers) target[name].headers = mapEnv(s.headers, '${env:VAR}');
        }
      } else {
        target[name] = { command: s.command, args: s.args || [] };
        if (s.env) target[name].env = mapEnv(s.env, '${env:VAR}');
      }
    }
    return JSON.stringify(format === 'vscode' ? { servers: target } : { mcpServers: target }, null, 2) + '\n';
  }

  if (format === 'gemini') {
    const mcpServers = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') {
        mcpServers[name] = { httpUrl: mapTemplatedValue(s.url, '${env:VAR}') };
        if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${env:VAR}');
      } else {
        mcpServers[name] = { command: s.command, args: s.args || [] };
        if (s.env) mcpServers[name].env = mapEnv(s.env, '${env:VAR}');
      }
      // T658: documented per-server tool blocklist; applies to the main agent and to subagents
      // (docs/artifacts/mcp-server-denials-v1.md). Gemini matches the name the server reports.
      if (s.denyTools) mcpServers[name].excludeTools = [...s.denyTools];
    }
    const cfg = {
      hooks: {
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
      },
      mcpServers,
    };
    return JSON.stringify(cfg, null, 2) + '\n';
  }

  if (format === 'opencode') {
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

  if (format === 'claude-code') {
    // Claude Code expands `${VAR}` / `${VAR:-default}` from the live process environment in
    // `command`, `args`, `env`, `url` and `headers` — it does NOT recognise VS Code's
    // `${env:VAR}` form and passes such text through literally (T517; see
    // docs/artifacts/mcp-header-url-templating-design-v2.md §3 and
    // https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json).
    const mcpServers = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') {
        mcpServers[name] = { type: 'http', url: mapTemplatedValue(s.url, '${VAR}') };
        if (s.headers) mcpServers[name].headers = mapEnv(s.headers, '${VAR}');
      } else {
        mcpServers[name] = { command: s.command, args: s.args || [] };
        if (s.env) mcpServers[name].env = mapEnv(s.env, '${VAR}');
      }
    }
    return JSON.stringify({ mcpServers }, null, 2) + '\n';
  }

  if (format === 'cline') {
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

  throw new Error(`Unknown MCP format: ${format}`);
}

// Renders one templated-value spec (see design mcp-header-url-templating-design-v1.md §3/§4)
// against a platform's own env-placeholder pattern.
//   spec: a plain literal (string/number/bool) -> returned unchanged (String(spec))
//         OR { fromEnv: VAR }                   -> template.replace('VAR', VAR)
//         OR { fromEnv: VAR, wrap: "X{VAR}Y" }   -> wrap.replace('{VAR}', <rendered above>)
//   template: the platform's own placeholder pattern, e.g. '${env:VAR}' (vscode/gemini/
//             pi/cline), '{env:VAR}' (opencode) or '${VAR}' (claude-code)
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

async function syncPlatform(manifest, servers) {
  const outRoot = path.resolve(ROOT, manifest.outputDir);
  const filesWritten = [];

  if (!CHECK_ONLY) {
    await fs.rm(outRoot, { recursive: true, force: true });
  }

  if (manifest.fileMap.agents) {
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

  if (manifest.fileMap.commands) {
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

  const insMap = manifest.fileMap.instructions;
  const insRoot = insMap.rootRelative ? path.resolve(ROOT, insMap.dir) : path.join(outRoot, insMap.dir);
  if (insMap.rootRelative) {
    const rootWithSep = ROOT.endsWith(path.sep) ? ROOT : ROOT + path.sep;
    if (insRoot === ROOT || !insRoot.startsWith(rootWithSep)) {
      throw new Error(`Refusing rootRelative fileMap target outside or equal to ROOT: ${insRoot}`);
    }
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

  if (manifest.mcp) {
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
      .filter(([, s]) => (s.tags || []).some((t) => manifest.mcp.tags.includes(t)))
      .map(([name]) => name)
      .sort();
    const sidecarPath = outPath + '.provenance.json';
    const sidecarContent = JSON.stringify({ schemaVersion: 1, generatorOwnedKeys: filteredKeys }, null, 2) + '\n';
    await emitFile(sidecarPath, sidecarContent);
    filesWritten.push(sidecarPath);
  }

  for (const extra of manifest.extras || []) {
    const src = path.resolve(EXTRAS, extra.from.replace(/^_extras\//, ''));
    const dst = path.join(outRoot, extra.to);
    const content = await fs.readFile(src);
    await emitFile(dst, content);
    filesWritten.push(dst);
  }

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

  return filesWritten.length;
}

async function main() {
  try {
    await fs.access(KNOWLEDGE);
    await fs.access(PLATFORMS);
  } catch {
    console.error(`Missing required inputs under root ${ROOT}`);
    console.error(`Expected directories: ${KNOWLEDGE} and ${PLATFORMS}`);
    process.exit(1);
  }

  const platformFiles = (await fs.readdir(PLATFORMS))
    .filter((f) => f.endsWith('.json') && !f.startsWith('_'))
    .sort();

  const servers = await readServersYaml();
  let total = 0;

  // T663 (SEC-T658-07 b): every manifest is read and validated before the first file is written.
  const manifests = [];
  for (const file of platformFiles) {
    const manifest = JSON.parse(await fs.readFile(path.join(PLATFORMS, file), 'utf8'));
    validateMcpToolNamesStyle(manifest);
    manifests.push(manifest);
  }

  for (const manifest of manifests) {
    if (ONLY_PLATFORM && manifest.platform !== ONLY_PLATFORM) continue;
    const count = await syncPlatform(manifest, servers);
    console.log(`[${manifest.platform}] ${CHECK_ONLY ? 'checked' : 'wrote'} ${count} files -> ${manifest.outputDir}`);
    total += count;
  }

  if (CHECK_ONLY) {
    if (driftReports.length) {
      console.error(`\nDRIFT DETECTED in ${driftReports.length} file(s):`);
      for (const f of driftReports.sort()) {
        console.error(`  - ${path.relative(ROOT, f)}`);
      }
      console.error('\nRun `node scripts/sync.mjs` to regenerate.');
      process.exit(1);
    }
    console.log(`\nOK - no drift across ${total} files.`);
  } else {
    console.log(`\nDone - ${total} files written.`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
