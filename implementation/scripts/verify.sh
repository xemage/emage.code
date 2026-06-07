#!/usr/bin/env bash
# Verify generated platform mirrors match canonical knowledge (no drift).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/.." && pwd)"
exec node "$here/verify.mjs" --root "$root" "$@"
