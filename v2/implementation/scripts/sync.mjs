#!/usr/bin/env node
// emage.code v2 — sync engine
// Reads knowledge/ + platforms/<name>.json and (re)generates each platform folder.
//
// No external dependencies. Frontmatter is parsed with a small inline parser
// that supports the subset emage.code uses (scalars, arrays, applyTo, globs).
//
// Usage:  node scripts/sync.mjs [--platform=<name>] [--check]
//   --platform=<name>  Sync only one platform (github|gemini|opencode|cursor).
//   --check            Don't write; instead diff against existing files and
//                      exit 1 if any drift is detected. Used in CI by verify.mjs.

import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const ROOT       = path.resolve(__dirname, '..');
const KNOWLEDGE  = path.join(ROOT, 'knowledge');
const PLATFORMS  = path.join(ROOT, 'platforms');
const EXTRAS     = path.join(ROOT, '_extras');

const args = Object.fromEntries(
  process.argv.slice(2).map(a => {
    const [k, v] = a.replace(/^--/, '').split('=');
    return [k, v ?? true];
  })
);
const CHECK_ONLY = !!args.check;
const ONLY_PLATFORM = args.platform || null;

// ---------- minimal YAML frontmatter parser (subset) ----------
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
  const lines = yaml.split(/\r?\n/).map(l => l.replace(/\r$/, ''));
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim() || line.trim().startsWith('#')) { i++; continue; }
    const m = line.match(/^([A-Za-z_][\w-]*)\s*:\s*(.*)$/);
    if (!m) { i++; continue; }
    const key = m[1];
    let rest = m[2];
    // inline array: key: [a, b, c]
    if (rest.startsWith('[') && rest.endsWith(']')) {
      out[key] = rest.slice(1, -1).split(',').map(s => stripQuotes(s.trim())).filter(Boolean);
      i++; continue;
    }
    // inline scalar
    if (rest !== '') {
      out[key] = stripQuotes(rest);
      i++; continue;
    }
    // empty rest → nested block (object with `key: value` children) — Opencode tools:
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
  v = v.trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1);
  }
  return v;
}

function parseScalar(v) {
  if (v === 'true') return true;
  if (v === 'false') return false;
  if (/^-?\d+$/.test(v)) return Number(v);
  return v;
}

// ---------- minimal YAML emitter ----------
function emitFrontmatter(obj, opts = { toolsFormat: 'array' }) {
  const lines = ['---'];
  for (const [key, val] of Object.entries(obj)) {
    if (val === undefined || val === null) continue;
    if (key === 'tools' && opts.toolsFormat === 'object' && Array.isArray(val)) {
      lines.push('tools:');
      for (const t of val) lines.push(`  ${t}: true`);
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
    // string — quote if contains special chars
    const needsQuote = /[:#&*!|>%@`]/.test(val) || val.includes('\n');
    lines.push(`${key}: ${needsQuote ? JSON.stringify(val) : `"${val}"`}`);
  }
  lines.push('---', '');
  return lines.join('\n');
}

// ---------- minimal YAML reader for servers.yaml ----------
async function readServersYaml() {
  const raw = await fs.readFile(path.join(KNOWLEDGE, 'mcp', 'servers.yaml'), 'utf8');
  return parseServersYaml(raw);
}

function parseServersYaml(raw) {
  // Very narrow parser tailored to the structure we author. Top-level
  // `servers:` then 2-space indented server names, each with 4-space indented
  // properties; `env:` uses 6-space indented mapping with inline objects.
  const lines = raw.split(/\r?\n/);
  const servers = {};
  let i = 0;
  while (i < lines.length && !lines[i].trim().startsWith('servers:')) i++;
  i++;
  let current = null;
  let envBlock = null;
  while (i < lines.length) {
    const ln = lines[i];
    if (!ln.trim() || ln.trim().startsWith('#')) { i++; continue; }
    const m2 = ln.match(/^  ([A-Za-z0-9._-]+):\s*$/);
    if (m2) { current = m2[1]; servers[current] = {}; envBlock = null; i++; continue; }
    if (current && envBlock !== null) {
      const me = ln.match(/^      ([A-Za-z0-9_]+):\s*(.*)$/);
      if (me) {
        envBlock[me[1]] = parseInlineObject(me[2]);
        i++; continue;
      } else {
        envBlock = null;
      }
    }
    if (current) {
      const me2 = ln.match(/^    ([A-Za-z0-9_-]+):\s*(.*)$/);
      if (me2) {
        const [, key, rest] = me2;
        if (key === 'env' && rest === '') {
          envBlock = {};
          servers[current].env = envBlock;
        } else if (rest.startsWith('[') && rest.endsWith(']')) {
          servers[current][key] = rest.slice(1, -1).split(',').map(s => stripQuotes(s.trim()));
        } else {
          servers[current][key] = parseScalar(stripQuotes(rest));
        }
        i++; continue;
      }
    }
    i++;
  }
  return servers;
}

function parseInlineObject(s) {
  s = s.trim();
  if (!s.startsWith('{')) return stripQuotes(s);
  s = s.slice(1, -1);
  const out = {};
  for (const part of s.split(',')) {
    const [k, ...rest] = part.split(':');
    if (!k) continue;
    out[k.trim()] = parseScalar(stripQuotes(rest.join(':').trim()));
  }
  return out;
}

// ---------- transformation helpers ----------
function applyAgentFrontmatter(data, name, frontmatterCfg) {
  const out = {};
  for (const k of frontmatterCfg.keepKeys || Object.keys(data)) {
    if (data[k] !== undefined) out[k] = data[k];
  }
  // Normalize `tools` to canonical array first if it came in as object
  let tools = data.tools;
  if (tools && !Array.isArray(tools) && typeof tools === 'object') {
    tools = Object.entries(tools).filter(([, v]) => v).map(([k]) => k);
  }
  if (frontmatterCfg.tools === 'drop') {
    delete out.tools;
  } else if (frontmatterCfg.tools === 'object') {
    if (Array.isArray(tools)) out.tools = tools; // emitter will format
  } else {
    if (Array.isArray(tools)) out.tools = tools;
  }
  if (frontmatterCfg.addToOrchestrators && (frontmatterCfg.orchestratorNames || []).includes(name)) {
    Object.assign(out, frontmatterCfg.addToOrchestrators);
  }
  return out;
}

function applyGenericFrontmatter(data, frontmatterCfg) {
  const out = {};
  const renamed = { ...data };
  for (const [from, to] of Object.entries(frontmatterCfg.renameKeys || {})) {
    if (renamed[from] !== undefined) {
      renamed[to] = renamed[from];
      delete renamed[from];
    }
  }
  for (const k of frontmatterCfg.keepKeys || Object.keys(renamed)) {
    if (renamed[k] !== undefined) out[k] = renamed[k];
  }
  return out;
}

// ---------- MCP config emitters ----------
function emitMcp(servers, tags, format) {
  const filtered = Object.fromEntries(
    Object.entries(servers).filter(([, s]) => (s.tags || []).some(t => tags.includes(t)))
  );

  if (format === 'vscode' || format === 'cursor') {
    const out = { servers: format === 'vscode' ? {} : undefined, mcpServers: format === 'cursor' ? {} : undefined };
    const target = format === 'vscode' ? out.servers : out.mcpServers;
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') target[name] = { url: s.url };
      else {
        target[name] = { command: s.command, args: s.args || [] };
        if (s.env) target[name].env = mapEnv(s.env, '${env:VAR}');
      }
    }
    return JSON.stringify(format === 'vscode' ? { servers: target } : { mcpServers: target }, null, 2) + '\n';
  }

  if (format === 'gemini') {
    const mcpServers = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') mcpServers[name] = { url: s.url };
      else {
        mcpServers[name] = { command: s.command, args: s.args || [] };
        if (s.env) mcpServers[name].env = mapEnv(s.env, '${env:VAR}');
      }
    }
    const cfg = {
      hooks: {
        AfterTool: [{
          matcher: 'replace|write_file',
          hooks: [{
            name: 'post-edit-reminder',
            type: 'command',
            command: "echo '{\"systemMessage\": \"Reminder: Ensure code follows coding standards (naming, error handling, security). Run lint before committing.\"}'"
          }]
        }]
      },
      mcpServers
    };
    return JSON.stringify(cfg, null, 2) + '\n';
  }

  if (format === 'opencode') {
    const mcp = {};
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') mcp[name] = { type: 'remote', url: s.url };
      else {
        mcp[name] = { type: 'local', command: [s.command, ...(s.args || [])] };
        if (s.env) mcp[name].environment = mapEnv(s.env, '{env:VAR}');
      }
    }
    return { __mcpObject: mcp };
  }

  throw new Error(`Unknown MCP format: ${format}`);
}

function mapEnv(envSpec, template) {
  const out = {};
  for (const [k, v] of Object.entries(envSpec)) {
    if (v && typeof v === 'object' && v.fromEnv) {
      out[k] = template.replace('VAR', v.fromEnv);
    } else {
      out[k] = String(v);
    }
  }
  return out;
}

// ---------- file walking ----------
async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const results = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) results.push(...await walk(full));
    else results.push(full);
  }
  return results;
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
    try { existing = await fs.readFile(absPath); } catch { /* missing */ }
    if (!existing || !existing.equals(expected)) driftReports.push(absPath);
    return;
  }
  await writeFile(absPath, content);
}

// ---------- main per-platform sync ----------
async function syncPlatform(manifest, servers) {
  const outRoot = path.join(ROOT, manifest.outputDir);
  const filesWritten = [];

  // Wipe outputDir first when not in check mode (so removed files disappear).
  if (!CHECK_ONLY) {
    await fs.rm(outRoot, { recursive: true, force: true });
  }

  // ---- agents ----
  const agentMap = manifest.fileMap.agents;
  const agentCfg = manifest.frontmatter.agents;
  for (const file of await walk(path.join(KNOWLEDGE, 'agents'))) {
    if (!file.endsWith('.md')) continue;
    const baseName = path.basename(file, '.md');
    const raw = await fs.readFile(file, 'utf8');
    const { data, body } = parseFrontmatter(raw);
    const newData = applyAgentFrontmatter(data, baseName, agentCfg);
    const fm = emitFrontmatter(newData, {
      toolsFormat: agentCfg.tools === 'object' ? 'object' : 'array'
    });
    const outPath = path.join(outRoot, agentMap.dir, baseName + agentMap.ext);
    await emitFile(outPath, fm + body);
    filesWritten.push(outPath);
  }

  // ---- commands ----
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

  // ---- instructions ----
  const insMap = manifest.fileMap.instructions;
  for (const file of await walk(path.join(KNOWLEDGE, 'instructions'))) {
    if (!file.endsWith('.md')) continue;
    const baseName = path.basename(file, '.md');
    const raw = await fs.readFile(file, 'utf8');
    const { data, body } = parseFrontmatter(raw);
    const newData = applyGenericFrontmatter(data, manifest.frontmatter.instructions);
    const outPath = path.join(outRoot, insMap.dir, baseName + insMap.ext);
    await emitFile(outPath, emitFrontmatter(newData) + body);
    filesWritten.push(outPath);
  }

  // ---- skills (preserve tree, copy verbatim with optional frontmatter trim) ----
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

  // ---- MCP config ----
  if (manifest.mcp) {
    const mcpResult = emitMcp(servers, manifest.mcp.tags, manifest.mcp.format);
    let outPath = path.isAbsolute(manifest.mcp.outputFile)
      ? manifest.mcp.outputFile
      : path.resolve(outRoot, manifest.mcp.outputFile);

    if (manifest.mcp.format === 'opencode') {
      const cfg = { ...(manifest.mcp.extraFields || {}), mcp: mcpResult.__mcpObject };
      await emitFile(outPath, JSON.stringify(cfg, null, 2) + '\n');
    } else {
      await emitFile(outPath, mcpResult);
    }
    filesWritten.push(outPath);
  }

  // ---- extras ----
  for (const e of manifest.extras || []) {
    const src = path.resolve(ROOT, e.from.replace(/^_extras\//, '_extras/'));
    const dst = path.join(outRoot, e.to);
    const content = await fs.readFile(src);
    await emitFile(dst, content);
    filesWritten.push(dst);
  }

  // ---- generated manifest ----
  const manifestPath = path.join(outRoot, '.generated-manifest.json');
  const manifestContent = JSON.stringify({
    generatedFrom: 'knowledge/',
    platform: manifest.platform,
    generatedAt: '<deterministic>',
    files: filesWritten.map(f => path.relative(outRoot, f)).sort()
  }, null, 2) + '\n';
  await emitFile(manifestPath, manifestContent);

  return filesWritten.length;
}

// ---------- entry ----------
async function main() {
  const platformFiles = (await fs.readdir(PLATFORMS))
    .filter(f => f.endsWith('.json') && !f.startsWith('_'));

  const servers = await readServersYaml();
  let total = 0;
  for (const f of platformFiles) {
    const manifest = JSON.parse(await fs.readFile(path.join(PLATFORMS, f), 'utf8'));
    if (ONLY_PLATFORM && manifest.platform !== ONLY_PLATFORM) continue;
    const count = await syncPlatform(manifest, servers);
    console.log(`[${manifest.platform}] ${CHECK_ONLY ? 'checked' : 'wrote'} ${count} files → ${manifest.outputDir}`);
    total += count;
  }

  if (CHECK_ONLY) {
    if (driftReports.length) {
      console.error(`\nDRIFT DETECTED in ${driftReports.length} file(s):`);
      for (const f of driftReports) console.error(`  - ${path.relative(ROOT, f)}`);
      console.error(`\nRun \`node scripts/sync.mjs\` to regenerate.`);
      process.exit(1);
    }
    console.log(`\nOK — no drift across ${total} files.`);
  } else {
    console.log(`\nDone — ${total} files written.`);
  }
}

main().catch(err => { console.error(err); process.exit(1); });
