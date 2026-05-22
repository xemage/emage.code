#!/usr/bin/env node
// emage.code v3 - drift verifier (CI-friendly)
// Re-runs sync-v3 in --check mode. Exits non-zero if generated platform
// folders are out of sync with canonical knowledge.

import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const syncScript = path.join(here, 'sync-v3.mjs');

const passthroughArgs = process.argv.slice(2).filter((arg) => arg !== '--check');
const result = spawnSync(process.execPath, [syncScript, '--check', ...passthroughArgs], {
  stdio: 'inherit',
});

process.exit(result.status ?? 1);
