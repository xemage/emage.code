#!/usr/bin/env bash
# Cross-platform bash wrapper for emage.code sync.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec node "$here/sync.mjs" "$@"
