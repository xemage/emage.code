#!/usr/bin/env bash
# emage.code installer — copy platform outputs into a target project.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPLEMENTATION="${REPO_ROOT}/implementation"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh --target <dir> [--platform <name>|all]

Install emage.code into an existing or new project directory.

Options:
  --target <dir>       Destination project root (created if missing)
  --platform <name>    cursor | github | gemini | opencode | pi | all (default: all)
  -n, --dry-run        Print actions without copying
  -h, --help           Show this help

Examples:
  scripts/install.sh --target ~/projects/my-app --platform cursor
  scripts/install.sh --target . --platform all

After install, set MCP env vars from the generated mcp.json, then run:
  /discover-skills "start new project"
  /new-project "My application"
EOF
}

PLATFORM="all"
TARGET=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    -n|--dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "error: --target is required" >&2
  usage >&2
  exit 1
fi

if [[ ! -d "$IMPLEMENTATION" ]]; then
  echo "error: implementation tree not found at $IMPLEMENTATION" >&2
  exit 1
fi

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "DRY-RUN: $*"
  else
    "$@"
  fi
}

mkdir -p "$TARGET"

install_common() {
  run cp "$IMPLEMENTATION/AGENTS.md" "$TARGET/AGENTS.md"
  run cp -r "$IMPLEMENTATION/docs" "$TARGET/docs"
}

install_cursor() {
  run cp -r "$IMPLEMENTATION/.cursor" "$TARGET/.cursor"
}

install_github() {
  run cp -r "$IMPLEMENTATION/.github" "$TARGET/.github"
  run mkdir -p "$TARGET/.vscode"
  run cp "$IMPLEMENTATION/.vscode/mcp.json" "$TARGET/.vscode/mcp.json"
}

install_gemini() {
  run cp -r "$IMPLEMENTATION/.gemini" "$TARGET/.gemini"
}

install_opencode() {
  run cp -r "$IMPLEMENTATION/.opencode" "$TARGET/.opencode"
}

install_pi() {
  run cp -r "$IMPLEMENTATION/.pi" "$TARGET/.pi"
}

case "$PLATFORM" in
  cursor) install_common; install_cursor ;;
  github) install_common; install_github ;;
  gemini) install_common; install_gemini ;;
  opencode) install_common; install_opencode ;;
  pi) install_common; install_pi ;;
  all)
    install_common
    install_cursor
    install_github
    install_gemini
    install_opencode
    install_pi
    ;;
  *)
    echo "error: unknown platform '$PLATFORM'" >&2
    exit 1
    ;;
esac

echo "Installed emage.code ($PLATFORM) into $TARGET"
echo "Next: configure MCP env vars, then invoke /new-project in your assistant."
