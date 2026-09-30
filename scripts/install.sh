#!/usr/bin/env bash
# emage.code installer — copy platform outputs into a target project.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPLEMENTATION="${REPO_ROOT}/implementation"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh --target <dir> [--platform <name>|all] [--update | --projections-only]

Install emage.code into an existing or new project directory.

Options:
  --target <dir>       Destination project root (created if missing)
  --platform <name>    cursor | github | gemini | opencode | pi | claude-code | cline | all (default: all)
  -u, --update         Update an existing install. Replaces the platform trees, EXCEPT
                       project-local files the harness never ships and therefore does not
                       own: each platform's MCP/settings config, .claude/settings.json and
                       .claude/settings.local.json, and .github's workflows, issue/PR
                       templates, CODEOWNERS, dependabot.yml, FUNDING.yml and
                       copilot-instructions.md. In docs/tasks/, an existing ledger is never
                       rewritten beyond its task rows — its surrounding prose is the
                       project's own record, not the template's. Missing files are seeded.
  --projections-only   Refresh ONLY the derived harness of an existing install: the platform
                       trees (with the same project-local exceptions as --update), their
                       MCP configs (merged, as --update does), AGENTS.md and CLAUDE.md. It
                       never writes or deletes anything under the target's docs/ -- the
                       task ledgers included -- or its implementation/. Mutually exclusive
                       with --update. The one mode besides --update permitted at the emage.code
                       repository root, and there only with --platform all.
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
PROJECTIONS_ONLY=0
# The user-facing flag that selected refresh semantics, for messages only.
MODE_FLAG="--update"

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
    --projections-only) PROJECTIONS_ONLY=1; shift ;;
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

if [[ "$PROJECTIONS_ONLY" -eq 1 && "$UPDATE" -eq 1 ]]; then
  echo "error: --projections-only and --update are mutually exclusive." >&2
  echo "  --update is the full refresh (it also merges docs/ and copies the MCP server runtime);" >&2
  echo "  --projections-only refreshes the harness projections and nothing the project owns." >&2
  exit 1
fi

TARGET_ABS="$(resolve_abs_path "$TARGET")"

if [[ "$TARGET_ABS" == "$REPO_ROOT" ]]; then
  if [[ "$PROJECTIONS_ONLY" -eq 1 ]]; then
    # The refusal below exists because a plain install writes docs/ (the
    # curated task ledgers) and implementation/ (which, here, is the source
    # the installer reads). --projections-only writes neither, so it does not
    # engage that reason. The root hosts every platform and the T543 parity
    # gate compares it with a --platform all install, so a single-platform
    # refresh -- which would also re-render AGENTS.md for one platform only --
    # is refused here.
    if [[ "$PLATFORM" != "all" ]]; then
      echo "error: at the emage.code repository root, --projections-only requires --platform all" >&2
      echo "  (the root hosts every platform; got --platform $PLATFORM)." >&2
      exit 1
    fi
    echo "warning: refreshing the harness projections in-place at the repository root; docs/ and implementation/ are not touched." >&2
  elif [[ "$UPDATE" -eq 1 ]]; then
    echo "warning: updating in-place at repository root; templates will be merged without overwriting existing docs files." >&2
  else
    echo "error: refusing to install into the emage.code source repository root:" >&2
    echo "  $REPO_ROOT" >&2
    echo "reason: install mode can overwrite curated repository files." >&2
    echo "use one of the following instead:" >&2
    echo "  - For repo maintenance: git pull && make sync && make verify" >&2
    echo "    (these regenerate and check implementation/.<platform>/ only; they do not write the root)" >&2
    echo "  - To refresh the root's own harness projections: scripts/install.sh --target . --platform all --projections-only" >&2
    echo "  - For installation testing: scripts/install.sh --target /tmp/emage-test --platform all" >&2
    exit 1
  fi
fi

if [[ "$PROJECTIONS_ONLY" -eq 1 ]]; then
  # --projections-only reuses --update's semantics for everything it runs:
  # trees are replaced with stale-file deletion (sync_tree_into, honouring the
  # project-local excludes) and MCP configs are merged, not overwritten
  # (merge_or_copy_mcp_json). What it does NOT run is decided in
  # install_common, and enforced again inside install_docs and
  # install_mcp_server_runtime.
  UPDATE=1
  MODE_FLAG="--projections-only"
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
# $3.. (optional, relative to dest, variadic): protected paths. The installer
# neither writes nor deletes these, for two distinct reasons that share one
# mechanism:
#   1. Source-side build artifacts that must not leak into a target (e.g.
#      implementation/runtime/memory/_index/, __pycache__/).
#   2. Target-side project-local state the harness does not ship and therefore
#      does not own (e.g. .claude/settings.json, .github/workflows/). These have
#      no counterpart in $IMPLEMENTATION by design — see sync_tree_into, where
#      omitting them made `rsync --delete` destroy them on every --update.
copy_tree_into() {
  local src="$1"
  local dest="$2"
  local excludes=("${@:3}")
  run mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    local rsync_args=(-a)
    local e
    for e in ${excludes[@]+"${excludes[@]}"}; do
      if [[ -n "$e" ]]; then rsync_args+=(--exclude="$e"); fi
    done
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
    # on any host without rsync, since the exclude list is empty for most
    # callers) — real `if` blocks instead, so a false condition never becomes
    # this function's own return code.
    #
    # The `-e "$src/$e"` guard makes this fallback match rsync --exclude
    # exactly: undo only what the copy above actually placed. Without it the
    # fallback deleted pre-existing *dest* content that was never in src —
    # which is the whole point of an exclude like settings.json or _index/.
    local e
    for e in ${excludes[@]+"${excludes[@]}"}; do
      if [[ -n "$e" && -e "$src/$e" ]]; then run rm -rf "$dest/$e"; fi
    done
  fi
}

# Replace dest with source, removing files that no longer exist upstream.
# Every path in $3.. (relative to dest, variadic) is left untouched by this
# whole-tree replace — neither deleted nor overwritten. Two kinds of path need
# that, for two different reasons:
#   - Config files that a later merge step owns (merge_or_copy_mcp_json and its
#     provenance sidecar), so hand-added content in them is not lost.
#   - Project-local state the harness never ships, so it has no counterpart in
#     $IMPLEMENTATION and `rsync --delete` would sweep it: .claude/settings.json
#     (a host's Bash-permission allowlist) and .github/workflows/ (the target
#     project's own CI) are the two real cases. This is not hypothetical — it
#     destroyed .claude/settings.json on every --update until T518.
# rsync --exclude already protects an excluded path from --delete (we never pass
# --delete-excluded); the no-rsync fallback below reproduces that by hand.
sync_tree_into() {
  local src="$1"
  local dest="$2"
  local excludes=("${@:3}")
  local e
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    local rsync_args=(-a --delete)
    for e in ${excludes[@]+"${excludes[@]}"}; do
      if [[ -n "$e" ]]; then
        rsync_args+=(--exclude="$e")
      fi
    done
    if [[ "$DRY_RUN" -eq 1 ]]; then
      run rsync "${rsync_args[@]}" --dry-run "$src/" "$dest/"
    else
      run rsync "${rsync_args[@]}" "$src/" "$dest/"
    fi
  else
    # Parallel arrays, one entry per protected path that actually exists in
    # dest: backup_paths[i] is the relative path, backup_dirs[i] the mktemp -d
    # holding its saved copy. Paths absent from dest are simply not recorded.
    local backup_paths=()
    local backup_dirs=()
    # -r here (not plain cp) so an excluded path may name either a file (the
    # original mcp.json/provenance use case) or a directory (a generated index
    # dir, .github/workflows/) without a separate code path.
    for e in ${excludes[@]+"${excludes[@]}"}; do
      if [[ -n "$e" && -e "$dest/$e" ]]; then
        local backup_dir
        backup_dir="$(mktemp -d)"
        cp -r "$dest/$e" "$backup_dir/payload"
        backup_paths+=("$e")
        backup_dirs+=("$backup_dir")
      fi
    done
    run rm -rf "$dest"
    run mkdir -p "$dest"
    run cp -r "$src/." "$dest/"
    # `"${!arr[@]}"` on an empty array trips `set -u` on bash < 4.4, which the
    # no-rsync CI images are exactly the kind of host to ship — count first.
    local i
    for ((i = 0; i < ${#backup_paths[@]}; i++)); do
      local rel="${backup_paths[$i]}"
      local dir="${backup_dirs[$i]}"
      run mkdir -p "$(dirname "$dest/$rel")"
      run rm -rf "$dest/$rel"
      run cp -r "$dir/payload" "$dest/$rel"
      rm -rf "$dir"
    done
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

# $3.. are protected paths relative to dest, passed through verbatim.
install_tree_into() {
  local src="$1"
  local dest="$2"
  local excludes=("${@:3}")
  if [[ "$UPDATE" -eq 1 ]]; then
    sync_tree_into "$src" "$dest" ${excludes[@]+"${excludes[@]}"}
  else
    copy_tree_into "$src" "$dest" ${excludes[@]+"${excludes[@]}"}
  fi
}

# Project-local paths inside .claude/ that the harness never generates and must
# therefore never delete. settings.json is the shared, checked-in project
# settings file (a Bash-permission allowlist among other things);
# settings.local.json is Claude Code's own per-developer, gitignored override of
# it. They are the same class of file, created by the client rather than by this
# repo, and were destroyed by the same single `rsync --delete` sweep — protecting
# only the one that happened to be reported would leave the identical defect in
# place for the file Claude Code itself recommends for host-specific permissions.
CLAUDE_LOCAL_PATHS=(settings.json settings.local.json)

# Project-local paths inside .github/ — GitHub's own reserved, fixed names. The
# harness ships only agents/, hooks/, instructions/, prompts/, skills/ and
# .generated-manifest.json there, so everything below belongs to the target
# project and was being swept by --update. .github/workflows/ is the severe one:
# an --update silently deleted the target project's entire CI configuration.
GITHUB_LOCAL_PATHS=(
  workflows
  ISSUE_TEMPLATE
  PULL_REQUEST_TEMPLATE.md
  PULL_REQUEST_TEMPLATE
  CODEOWNERS
  dependabot.yml
  dependabot.yaml
  FUNDING.yml
  copilot-instructions.md
)

require_existing_install() {
  if [[ ! -f "$TARGET/AGENTS.md" ]]; then
    echo "error: $MODE_FLAG requires an existing emage.code install (missing $TARGET/AGENTS.md)" >&2
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
    for d in .github .cursor .gemini .opencode .pi .claude .cline .clinerules; do
      if [[ -d "$TARGET/$d" ]]; then
        local exception=""
        case "$d" in
          .cursor) exception=" (except $d/mcp.json, which is merged, not overwritten)" ;;
          .gemini) exception=" (except $d/settings.json, which is merged, not overwritten)" ;;
          .opencode) exception=" (except $d/opencode.json, which is merged, not overwritten)" ;;
          .pi) exception=" (except $d/mcp.json, which is merged, not overwritten)" ;;
          .cline) exception=" (except $d/mcp.json, which is merged, not overwritten)" ;;
          .claude) exception=" (except $d/settings.json and $d/settings.local.json, which are project-local and left untouched)" ;;
          .github) exception=" (except workflows/, ISSUE_TEMPLATE/, PULL_REQUEST_TEMPLATE*, CODEOWNERS, dependabot.y*ml, FUNDING.yml and copilot-instructions.md, which are project-local and left untouched)" ;;
        esac
        echo "warning: $MODE_FLAG replaces $TARGET/$d entirely (rsync --delete)${exception}. Other local edits there will be lost." >&2
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
  refuse_in_projections_only merge_task_docs "$TARGET/docs/tasks"
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

# Tripwire for --projections-only. install_common already skips the two steps
# that write project-owned content (docs/, incl. the task ledgers) or the MCP
# server runtime (implementation/, which at the repository root is the source
# itself). This makes any future call path that reaches them in that mode fail
# before writing anything, instead of silently doing what the mode promises not
# to do.
refuse_in_projections_only() {
  if [[ "$PROJECTIONS_ONLY" -eq 1 ]]; then
    echo "error: internal: $1 must never run under --projections-only; nothing under $2 was written." >&2
    exit 70
  fi
}

install_docs() {
  refuse_in_projections_only install_docs "$TARGET/docs"
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
    refuse_in_projections_only install_mcp_server_runtime "$TARGET/implementation"
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
  if [[ "$PROJECTIONS_ONLY" -eq 1 ]]; then
    # Harness-only refresh: AGENTS.md is rendered above; docs/ (project-owned
    # once installed) and implementation/runtime/ (not a projection) are skipped.
    return 0
  fi
  install_docs
  install_mcp_server_runtime
}

install_cursor() {
  install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor" "mcp.json" "mcp.json.provenance.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cursor/mcp.json" "$TARGET/.cursor/mcp.json"
}

install_github() {
  install_tree_into "$IMPLEMENTATION/.github" "$TARGET/.github" "${GITHUB_LOCAL_PATHS[@]}"
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
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude" "${CLAUDE_LOCAL_PATHS[@]}"
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

if [[ "$PROJECTIONS_ONLY" -eq 1 ]]; then
  # The MCP-dependency and search-index notices below describe the runtime
  # install, which this mode deliberately did not perform.
  echo "Refreshed emage.code harness projections ($PLATFORM) in $TARGET; docs/ and implementation/ were not touched."
  exit 0
fi

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
