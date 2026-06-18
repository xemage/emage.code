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
    const needsQuote = /[:#&*!|>%@`]/.test(val) || val.includes('\n');
    lines.push(`${key}: ${needsQuote ? JSON.stringify(val) : `"${val}"`}`);
  }
  lines.push('---', '');
  return lines.join('\n');
}

async function readServersYaml() {
  const file = path.join(KNOWLEDGE, 'mcp', 'servers.yaml');
  const raw = await fs.readFile(file, 'utf8');
  return parseServersYaml(raw);
}

function parseServersYaml(raw) {
  const lines = raw.split(/\r?\n/);
  const servers = {};
  let i = 0;
  while (i < lines.length && !lines[i].trim().startsWith('servers:')) i++;
  i++;
  let current = null;
  let envBlock = null;

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
      envBlock = null;
      i++;
      continue;
    }

    if (current && envBlock !== null) {
      const me = ln.match(/^      ([A-Za-z0-9_]+):\s*(.*)$/);
      if (me) {
        envBlock[me[1]] = parseInlineObject(me[2]);
        i++;
        continue;
      }
      envBlock = null;
    }

    if (current) {
      const me2 = ln.match(/^    ([A-Za-z0-9_-]+):\s*(.*)$/);
      if (me2) {
        const [, key, rest] = me2;
        if (key === 'env' && rest === '') {
          envBlock = {};
          servers[current].env = envBlock;
        } else if (rest.startsWith('[') && rest.endsWith(']')) {
          servers[current][key] = rest.slice(1, -1).split(',').map((s) => stripQuotes(s.trim()));
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
  } else {
    if (Array.isArray(tools)) out.tools = tools;
  }

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
    if (v && typeof v === 'object' && v.fromEnv) out[k] = template.replace('VAR', v.fromEnv);
    else out[k] = String(v);
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

async function syncPlatform(manifest, servers) {
  const outRoot = path.resolve(ROOT, manifest.outputDir);
  const filesWritten = [];

  if (!CHECK_ONLY) {
    await fs.rm(outRoot, { recursive: true, force: true });
  }

  const agentMap = manifest.fileMap.agents;
  const agentCfg = manifest.frontmatter.agents;
  for (const file of await walk(path.join(KNOWLEDGE, 'agents'))) {
    if (!file.endsWith('.md')) continue;
    const baseName = path.basename(file, '.md');
    const raw = await fs.readFile(file, 'utf8');
    const { data, body } = parseFrontmatter(raw);
    const newData = applyAgentFrontmatter(data, baseName, agentCfg);
    const fm = emitFrontmatter(newData, {
      toolsFormat: agentCfg.tools === 'object' ? 'object' : 'array',
    });
    const outPath = path.join(outRoot, agentMap.dir, baseName + agentMap.ext);
    await emitFile(outPath, fm + body);
    filesWritten.push(outPath);
  }

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
      await emitFile(outPath, JSON.stringify(cfg, null, 2) + '\n');
    } else {
      await emitFile(outPath, mcpResult);
    }
    filesWritten.push(outPath);
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

  for (const file of platformFiles) {
    const manifest = JSON.parse(await fs.readFile(path.join(PLATFORMS, file), 'utf8'));
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
