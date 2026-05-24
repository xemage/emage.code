#!/usr/bin/env node
// emage.code v3 - drift verifier (CI-friendly)
// Re-runs sync-v3 in --check mode. Exits non-zero if generated platform
// folders are out of sync with canonical knowledge.

import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const syncScript = path.join(here, 'sync-v3.mjs');

const cliArgs = process.argv.slice(2);
let rootValue = path.resolve(here, '..');
const normalizedArgs = [];

for (let index = 0; index < cliArgs.length; index += 1) {
  const arg = cliArgs[index];
  if (arg === '--check') {
    continue;
  }
  if (arg === '--root') {
    index += 1;
    if (index < cliArgs.length) {
      rootValue = cliArgs[index];
    }
    continue;
  }
  if (arg.startsWith('--root=')) {
    rootValue = arg.slice('--root='.length);
    continue;
  }
  normalizedArgs.push(arg);
}

const resolvedRoot = path.isAbsolute(rootValue) ? rootValue : path.resolve(process.cwd(), rootValue);

const result = spawnSync(process.execPath, [syncScript, '--check', `--root=${resolvedRoot}`, ...normalizedArgs], {
  stdio: 'inherit',
});

process.exit(result.status ?? 1);
