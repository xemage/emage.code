#!/usr/bin/env bash
# Regenerate platform mirrors from canonical knowledge (v3 sync engine).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/.." && pwd)"
exec node "$here/sync-v3.mjs" --root "$root" "$@"
