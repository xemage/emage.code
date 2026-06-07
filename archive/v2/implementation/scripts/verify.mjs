#!/usr/bin/env node
// emage.code v2 — drift verifier (CI-friendly).
// Re-runs sync in --check mode. Exits non-zero if generated platform folders
// are out of sync with knowledge/.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const r = spawnSync(process.execPath, [path.join(here, 'sync.mjs'), '--check'], { stdio: 'inherit' });
process.exit(r.status ?? 1);
