#!/usr/bin/env bash
# emage.code installer — copy platform outputs into a target project.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPLEMENTATION="${REPO_ROOT}/implementation"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh --target <dir> [--platform <name>|all] [--update]

Install emage.code into an existing or new project directory.

Options:
  --target <dir>       Destination project root (created if missing)
  --platform <name>    cursor | github | gemini | opencode | pi | claude-code | cline | all (default: all)
  -u, --update         Update an existing install (replaces platform trees; preserves task rows in docs/tasks/*.md)
  -n, --dry-run        Print actions without copying
  -h, --help           Show this help

Examples:
  scripts/install.sh --target ~/projects/my-app --platform cursor
  scripts/install.sh --target ~/projects/my-app --platform pi --update
  scripts/install.sh --target . --platform all

After install, set MCP env vars from the generated mcp.json, then run:
  /discover-skills "start new project"
  /new-project "My application"
EOF
}

PLATFORM="all"
TARGET=""
DRY_RUN=0
UPDATE=0

TARGET_ABS=""

resolve_abs_path() {
  local path="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$path"
  elif command -v realpath >/dev/null 2>&1; then
    realpath "$path"
  else
    echo "$path"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    -u|--update) UPDATE=1; shift ;;
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

TARGET_ABS="$(resolve_abs_path "$TARGET")"

if [[ "$TARGET_ABS" == "$REPO_ROOT" ]]; then
  if [[ "$UPDATE" -eq 1 ]]; then
    echo "warning: updating in-place at repository root; templates will be merged without overwriting existing docs files." >&2
  else
    echo "error: refusing to install into the emage.code source repository root:" >&2
    echo "  $REPO_ROOT" >&2
    echo "reason: install mode can overwrite curated repository files." >&2
    echo "use one of the following instead:" >&2
    echo "  - For repo maintenance: git pull && make sync && make verify" >&2
    echo "  - For installation testing: scripts/install.sh --target /tmp/emage-test --platform all" >&2
    exit 1
  fi
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

# Merge source tree into dest without nesting when dest already exists.
# `cp -r src dest` creates dest/srcname when dest is present; this copies contents.
# $3/$4 (optional, relative to dest): paths never copied from src, even if
# present there — for a source dir that may carry the installer's own local,
# gitignored build artifacts (e.g. implementation/runtime/memory/_index/,
# per-project generated content that must never leak into a fresh target).
copy_tree_into() {
  local src="$1"
  local dest="$2"
  local exclude_rel="${3:-}"
  local exclude_rel_2="${4:-}"
  run mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    local rsync_args=(-a)
    if [[ -n "$exclude_rel" ]]; then rsync_args+=(--exclude="$exclude_rel"); fi
    if [[ -n "$exclude_rel_2" ]]; then rsync_args+=(--exclude="$exclude_rel_2"); fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
      run rsync "${rsync_args[@]}" --dry-run "$src/" "$dest/"
    else
      run rsync "${rsync_args[@]}" "$src/" "$dest/"
    fi
  else
    run cp -r "$src/." "$dest/"
    # Bare `[[ cond ]] && cmd` as a function's own last statement(s) would
    # make the *function's* exit status that of the failed `[[ ]]` test
    # whenever cond is false (a real bug hit and fixed here, not a
    # hypothetical: it silently killed every install.sh run under `set -e`
    # on any host without rsync, since $exclude_rel/$exclude_rel_2 are empty
    # for most callers) — real `if` blocks instead, so a false condition
    # never becomes this function's own return code.
    if [[ -n "$exclude_rel" ]]; then run rm -rf "$dest/$exclude_rel"; fi
    if [[ -n "$exclude_rel_2" ]]; then run rm -rf "$dest/$exclude_rel_2"; fi
  fi
}

# Replace dest with source, removing files that no longer exist upstream.
# If $3 (a path relative to dest) is given, that one file is left untouched
# by this whole-tree replace — neither deleted nor overwritten — so a
# separate merge step (merge_or_copy_mcp_json) can update it afterward
# without losing any hand-added content it may hold. If $4 (also relative to
# dest) is given, that second file — the MCP file's provenance sidecar — gets
# the same untouched treatment, for the identical reason.
sync_tree_into() {
  local src="$1"
  local dest="$2"
  local exclude_rel="${3:-}"
  local exclude_rel_2="${4:-}"
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    local rsync_args=(-a --delete)
    if [[ -n "$exclude_rel" ]]; then
      rsync_args+=(--exclude="$exclude_rel")
    fi
    if [[ -n "$exclude_rel_2" ]]; then
      rsync_args+=(--exclude="$exclude_rel_2")
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
      run rsync "${rsync_args[@]}" --dry-run "$src/" "$dest/"
    else
      run rsync "${rsync_args[@]}" "$src/" "$dest/"
    fi
  else
    local backup=""
    local backup_2=""
    # -r here (not plain cp) so $exclude_rel/$exclude_rel_2 may name either a
    # file (the original mcp.json/provenance use case) or a directory (e.g.
    # a per-target-project generated index dir) without a separate code path.
    if [[ -n "$exclude_rel" && -e "$dest/$exclude_rel" ]]; then
      backup="$(mktemp -d)"
      cp -r "$dest/$exclude_rel" "$backup/payload"
    fi
    if [[ -n "$exclude_rel_2" && -e "$dest/$exclude_rel_2" ]]; then
      backup_2="$(mktemp -d)"
      cp -r "$dest/$exclude_rel_2" "$backup_2/payload"
    fi
    run rm -rf "$dest"
    run mkdir -p "$dest"
    run cp -r "$src/." "$dest/"
    if [[ -n "$backup" ]]; then
      run mkdir -p "$(dirname "$dest/$exclude_rel")"
      run rm -rf "$dest/$exclude_rel"
      run cp -r "$backup/payload" "$dest/$exclude_rel"
      rm -rf "$backup"
    fi
    if [[ -n "$backup_2" ]]; then
      run mkdir -p "$(dirname "$dest/$exclude_rel_2")"
      run rm -rf "$dest/$exclude_rel_2"
      run cp -r "$backup_2/payload" "$dest/$exclude_rel_2"
      rm -rf "$backup_2"
    fi
  fi
}

# Merge source tree into dest while preserving existing dest files.
# Used by --update for docs templates so local/project docs are never overwritten.
merge_tree_preserve_existing() {
  local src="$1"
  local dest="$2"
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      run rsync -a --ignore-existing --dry-run "$src/" "$dest/"
    else
      run rsync -a --ignore-existing "$src/" "$dest/"
    fi
  else
    run mkdir -p "$dest"
    run cp -rn "$src/." "$dest/"
  fi
}

install_tree_into() {
  local src="$1"
  local dest="$2"
  local exclude_rel="${3:-}"
  local exclude_rel_2="${4:-}"
  if [[ "$UPDATE" -eq 1 ]]; then
    sync_tree_into "$src" "$dest" "$exclude_rel" "$exclude_rel_2"
  else
    copy_tree_into "$src" "$dest" "$exclude_rel" "$exclude_rel_2"
  fi
}

require_existing_install() {
  if [[ ! -f "$TARGET/AGENTS.md" ]]; then
    echo "error: --update requires an existing emage.code install (missing $TARGET/AGENTS.md)" >&2
    exit 1
  fi
}

validate_github_agents() {
  # Guard: --update must not propagate corrupted subagent aliases (v6.0.5 contract).
  # GitHub agents must omit `name:` (use slug aliases) and orchestrators must use kebab-case.
  local github_agents="$IMPLEMENTATION/.github/agents"
  if [[ ! -d "$github_agents" ]]; then
    return 0
  fi

  # Check that no agent file has a `name:` key (they should omit it for slug aliasing).
  if rg -q '^name:' "$github_agents" 2>/dev/null; then
    echo "error: source .github/agents have corrupted 'name:' keys (violates v6.0.5 contract)." >&2
    echo "  Run 'make sync' in the emage.code repo to regenerate projections." >&2
    exit 1
  fi

  # Check that orchestrator agents: lists use kebab-case slugs, not display names.
  for orch in orchestrator poc-orchestrator; do
    local file="$github_agents/${orch}.agent.md"
    if [[ -f "$file" ]]; then
      if grep -q '^agents: \[.*[A-Z]' "$file"; then
        echo "error: $file has display-name aliases (not kebab-case slugs)." >&2
        echo "  Run 'make sync' in the emage.code repo to regenerate projections." >&2
        exit 1
      fi
    fi
  done
}

validate_before_update() {
  # Pre-flight checks before --update to prevent propagating corrupted state.
  if [[ "$UPDATE" -eq 1 ]]; then
    for d in .github .cursor .gemini .opencode .pi .claude; do
      if [[ -d "$TARGET/$d" ]]; then
        local exception=""
        case "$d" in
          .cursor) exception=" (except $d/mcp.json, which is merged, not overwritten)" ;;
          .gemini) exception=" (except $d/settings.json, which is merged, not overwritten)" ;;
          .opencode) exception=" (except $d/opencode.json, which is merged, not overwritten)" ;;
          .pi) exception=" (except $d/mcp.json, which is merged, not overwritten)" ;;
        esac
        echo "warning: --update replaces $TARGET/$d entirely (rsync --delete)${exception}. Other local edits there will be lost." >&2
      fi
    done
    validate_github_agents
  fi
}

mkdir -p "$TARGET"

if [[ "$UPDATE" -eq 1 ]]; then
  require_existing_install
  validate_before_update
fi

merge_task_docs() {
  local args=(
    "$REPO_ROOT/scripts/merge-task-docs.py"
    --template-dir "$IMPLEMENTATION/docs/tasks"
    --dest-dir "$TARGET/docs/tasks"
  )
  if [[ "$DRY_RUN" -eq 1 ]]; then
    args+=(--dry-run)
  fi
  run python3 "${args[@]}"
}

# Copy a generated single-file MCP config into target, preserving any
# hand-added keys (e.g. a locally-added MCP server or `inputs` block) when
# updating an existing install. Falls back to a plain copy on fresh installs
# or when the dest file doesn't exist yet. The MCP file's provenance sidecar
# (<mcpfile>.provenance.json, ADR-002) is carried alongside it: merged runs
# pass it to merge-mcp-json.py for diff-based pruning and to refresh the
# dest-side sidecar; fresh-install/no-dest runs plain-copy it too.
merge_or_copy_mcp_json() {
  local src="$1"
  local dest="$2"
  local src_sidecar="${src}.provenance.json"
  local dest_sidecar="${dest}.provenance.json"
  if [[ "$UPDATE" -eq 1 && -f "$dest" ]]; then
    local args=("$REPO_ROOT/scripts/merge-mcp-json.py" --source "$src" --dest "$dest")
    if [[ -f "$src_sidecar" ]]; then
      args+=(--old-sidecar "$dest_sidecar" --new-sidecar "$src_sidecar")
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
      args+=(--dry-run)
    fi
    run python3 "${args[@]}"
  else
    run cp "$src" "$dest"
    if [[ -f "$src_sidecar" ]]; then
      run cp "$src_sidecar" "$dest_sidecar"
    fi
  fi
}

install_docs() {
  run mkdir -p "$TARGET/docs"
  if [[ "$UPDATE" -eq 1 ]]; then
    for sub in "$IMPLEMENTATION/docs"/*/; do
      [[ -d "$sub" ]] || continue
      name="$(basename "$sub")"
      if [[ "$name" == "tasks" ]]; then
        merge_task_docs
      else
        merge_tree_preserve_existing "$sub" "$TARGET/docs/$name"
      fi
    done
  else
    copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs"
  fi
}

  install_agents_doc() {
    local src="$IMPLEMENTATION/AGENTS.md"
    local dest="$TARGET/AGENTS.md"

    local args=(
    "$REPO_ROOT/scripts/render_installed_agents.py"
    --source "$src"
    --dest "$dest"
    --platform "$PLATFORM"
    )
    if [[ "$DRY_RUN" -eq 1 ]]; then
    args+=(--dry-run)
    fi
    run python3 "${args[@]}"
  }

  # Copies the Python source these two MCP servers actually import at
  # runtime (implementation/runtime/memory/, implementation/runtime/security/)
  # into the target project. Config generation alone (.mcp.json etc.) is not
  # enough — the config just tells the client to run
  # `python3 -m implementation.runtime.memory...`, and outside the emage.code
  # source repo itself, no such module exists to run until this step copies
  # it there. `_index/` (context-retriever's per-project, locally-built
  # search index) is deliberately excluded from being overwritten/deleted on
  # `--update` — it is never present in $IMPLEMENTATION (gitignored, build.py
  # output) and, once a target project has built its own, that is
  # project-specific generated content this installer must not touch.
  install_mcp_server_runtime() {
    run mkdir -p "$TARGET/implementation"
    if [[ ! -f "$TARGET/implementation/__init__.py" ]]; then
      run touch "$TARGET/implementation/__init__.py"
    fi
    run mkdir -p "$TARGET/implementation/runtime"
    install_tree_into "$IMPLEMENTATION/runtime/memory" "$TARGET/implementation/runtime/memory" "_index" "__pycache__"
    install_tree_into "$IMPLEMENTATION/runtime/security" "$TARGET/implementation/runtime/security" "__pycache__"
  }

install_common() {
    install_agents_doc
  install_docs
  install_mcp_server_runtime
}

install_cursor() {
  install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor" "mcp.json" "mcp.json.provenance.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cursor/mcp.json" "$TARGET/.cursor/mcp.json"
}

install_github() {
  install_tree_into "$IMPLEMENTATION/.github" "$TARGET/.github"
  run mkdir -p "$TARGET/.vscode"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.vscode/mcp.json" "$TARGET/.vscode/mcp.json"
}

install_gemini() {
  install_tree_into "$IMPLEMENTATION/.gemini" "$TARGET/.gemini" "settings.json" "settings.json.provenance.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.gemini/settings.json" "$TARGET/.gemini/settings.json"
}

install_opencode() {
  install_tree_into "$IMPLEMENTATION/.opencode" "$TARGET/.opencode" "opencode.json" "opencode.json.provenance.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.opencode/opencode.json" "$TARGET/.opencode/opencode.json"
}

install_pi() {
  install_tree_into "$IMPLEMENTATION/.pi" "$TARGET/.pi" "mcp.json" "mcp.json.provenance.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.pi/mcp.json" "$TARGET/.pi/mcp.json"
}

install_claude_code() {
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.mcp.json" "$TARGET/.mcp.json"
  run cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"
}

install_cline() {
  install_tree_into "$IMPLEMENTATION/.cline" "$TARGET/.cline" "mcp.json" "mcp.json.provenance.json"
  install_tree_into "$IMPLEMENTATION/.clinerules" "$TARGET/.clinerules"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cline/mcp.json" "$TARGET/.cline/mcp.json"
}

case "$PLATFORM" in
  cursor) install_common; install_cursor ;;
  github) install_common; install_github ;;
  gemini) install_common; install_gemini ;;
  opencode) install_common; install_opencode ;;
  pi) install_common; install_pi ;;
  claude-code) install_common; install_claude_code ;;
  cline) install_common; install_cline ;;
  all)
    install_common
    install_cursor
    install_github
    install_gemini
    install_opencode
    install_pi
    install_claude_code
    install_cline
    ;;
  *)
    echo "error: unknown platform '$PLATFORM'" >&2
    exit 1
    ;;
esac

if [[ "$UPDATE" -eq 1 ]]; then
  echo "Updated emage.code ($PLATFORM) in $TARGET"
else
  echo "Installed emage.code ($PLATFORM) into $TARGET"
fi
echo "Next: configure MCP env vars, then invoke /new-project in your assistant."

# Some MCP servers (context-retriever, security-audit) are plain Python stdio
# processes launched via `python3 -m ...` from the generated mcp.json/settings
# files, and need the third-party `mcp` SDK installed to actually run — this
# installer only copies config/knowledge/runtime-source files, it never
# installs Python packages into an arbitrary target environment's interpreter
# (that would be a real, risky side effect this script should not take
# silently). Without this notice, the first sign of the missing dependency is
# a generic, unhelpful "Connection closed" error from the MCP client days or
# weeks later, not an actionable message at install time.
mcp_server_reqs=()
while IFS= read -r -d '' req_file; do
  mcp_server_reqs+=("$req_file")
done < <(find "$TARGET/implementation/runtime" -name "requirements-mcp-server.txt" -print0 2>/dev/null | sort -z)

if [[ "${#mcp_server_reqs[@]}" -gt 0 ]]; then
  echo ""
  echo "Note: this install includes MCP server(s) that need one extra, one-time local"
  echo "dependency install before they will actually run (their config is generated"
  echo "either way, but the server process will fail with 'Connection closed' in your"
  echo "assistant until this is done). Run from $TARGET:"
  for req_file in "${mcp_server_reqs[@]}"; do
    req_rel="${req_file#"$TARGET"/}"
    echo "  python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && pip install -r $req_rel"
  done
fi

# context-retriever additionally needs a per-project search index built once
# (implementation/runtime/memory/build.py) before it can answer real queries
# -- this cannot be shipped pre-built (it indexes the target project's own
# content) or built automatically here (it needs implementation/runtime/
# memory/requirements.txt installed first, per the notice above, and can take
# a while on a large repo).
if [[ -d "$TARGET/implementation/runtime/memory" ]]; then
  echo ""
  echo "Note: @context-retriever also needs its search index built once, after the"
  echo "dependency install above, before it can answer real queries. Run from $TARGET:"
  echo "  python3 -m implementation.runtime.memory.build \\"
  echo "      --project-id <org>/<repo> --own-repo-root . --general-repo-root . \\"
  echo "      --output-dir implementation/runtime/memory/_index/<org-repo-slug>"
  echo "  (see implementation/runtime/memory/README.md for the full option reference,"
  echo "  including --shared-source-root for cross-repo shared-scope indexing, and match"
  echo "  --output-dir to the --index-dir already set in the generated mcp.json for this project)"
fi
