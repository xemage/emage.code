#!/usr/bin/env bash
# emage.code installer — copy platform outputs into a target project.
set -euo pipefail

# SEC-005 (T672): nothing this installer creates is group- or world-writable, whatever the
# source tree's modes or the caller's umask: the mask only ever gets stricter (OR 022).
# rsync -a copies source modes verbatim and is held to the same rule by --chmod=go-w.
ORIG_UMASK="$(umask)"
umask "$(printf '%04o' $(( 8#$(umask) | 8#022 )))"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPLEMENTATION="${REPO_ROOT}/implementation"

# The one list of platforms this installer supports (SEC-T662-03). The usage text, the early
# --platform validation, the `all` expansion, list_managed_paths and the dispatch below are all
# derived from it; a test compares it with the outputDir-bearing manifests in
# implementation/platforms/*.json. Adding a platform means adding it here, to
# platform_managed_paths, platform_mcp_config and an install_<name> function (dashes as
# underscores) -- a missing piece fails closed (exit 70), it is never skipped.
SUPPORTED_PLATFORMS=(github gemini opencode pi claude-code cline)

# Prints $@ joined with " | " (for usage) -- bash has no join builtin.
join_bar() {
  local out="$1"
  shift
  local item
  for item in "$@"; do out="$out | $item"; done
  printf '%s' "$out"
}

# Prints $@ joined with ", " (for messages).
join_comma() {
  local out="$1"
  shift
  local item
  for item in "$@"; do out="$out, $item"; done
  printf '%s' "$out"
}

usage() {
  cat <<'EOF'
Usage: scripts/install.sh --target <dir> [--platform <name>|all] [--update | --projections-only]

Install emage.code into an existing or new project directory.

Options:
  --target <dir>       Destination project root (created if missing). Not the emage.code
                       repository: its root accepts only --projections-only, and any
                       directory below its root is refused in every mode.
EOF
  printf '  --platform <name>    %s (default: all)\n' "$(join_bar "${SUPPORTED_PLATFORMS[@]}" all)"
  cat <<'EOF'
  -u, --update         Update an existing install. Replaces the platform trees, EXCEPT
                       project-local files the harness never ships and therefore does not
                       own: each platform's MCP/settings config, .claude/settings.json and
                       .claude/settings.local.json, and .github's workflows, issue/PR
                       templates, CODEOWNERS, dependabot.yml, FUNDING.yml and
                       copilot-instructions.md. In docs/tasks/, each existing task ledger
                       (active-tasks.md, completed-tasks.md) is always rewritten: rows of
                       its task table that are not T<NNN> task rows are dropped (with a
                       warning), line endings become LF and a missing final newline is
                       added. Prose around the table is kept -- it is the project's own
                       record -- but a ledger with no task table at all is replaced by the
                       template, keeping only its task rows. Every other docs/ file is
                       seeded when missing and otherwise left alone.
                       Refused at the emage.code repository root; use --projections-only.
  --projections-only   Refresh ONLY the derived harness of an existing install: the platform
                       trees (with the same project-local exceptions as --update), their
                       MCP configs (merged, as --update does), AGENTS.md and CLAUDE.md. It
                       never writes or deletes anything under the target's docs/ -- the
                       task ledgers included -- or its implementation/. Mutually exclusive
                       with --update. The only mode permitted at the emage.code repository
                       root, and there only with --platform all.
  -n, --dry-run        Print actions without copying
  -h, --help           Show this help

MCP/settings configs (.vscode/mcp.json, .gemini/settings.json, .opencode/opencode.json,
.pi/mcp.json, .mcp.json, .cline/mcp.json): an existing one is MERGED in every mode, a plain
install included, never overwritten -- your own servers, keys and rules are kept, generator-owned
keys are refreshed, and the generated Playwright permission/excludeTools denials are put back.
A note on stderr names exactly: a permission rule or hooks value of yours that was replaced, a
key of yours kept inside a generator-owned server's env/headers, a file whose top level was not a
JSON object, and your servers kept when no provenance sidecar could prune a retired entry; other
generator-owned values (command, args, url ...) are refreshed silently. A config that is not
valid JSON, or that cannot be replaced (file or directory not writable), is refused up front,
naming the file, before anything is written.

Symlinks: any symlink at a managed target path, or at one of its parent directories
(.claude, docs, implementation, implementation/runtime, .vscode, .mcp.json, CLAUDE.md,
a task ledger, ...), is refused before anything is written -- even one that points
inside the target. Do not run the installer as root into a directory that other users
can write to: a link planted between the check and the write is not detected. Do not install
into such a directory at all: --update replaces a tree by building a sibling next to it
(<tree>.emage-new.<pid>) and renaming it over the old one, which another user could race.

Examples:
  scripts/install.sh --target ~/projects/my-app --platform claude-code
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

# $1 for an error message, byte-wise: in the C locale every byte outside printable
# ASCII (controls, ESC, newline, and each byte of a multi-byte character such as the
# bidi override U+202E) becomes `?`, whatever locale the caller runs in.
ascii_printable() {
  local LC_ALL=C
  printf '%s' "${1//[^ -~]/?}"
}

# $1 quoted for a shell (`printf %q`) in the C locale: every byte outside printable ASCII
# (a newline, ESC, each byte of the bidi override U+202E) becomes an octal escape inside
# $'...', whatever locale the caller runs in. A UTF-8 locale would print a "printable"
# multi-byte character raw, which a reader cannot tell from a look-alike (T684, SEC-T682-03).
shell_quote_ascii() {
  local LC_ALL=C
  printf '%q' "$1"
}

# $1 is an option that takes a value, $2 its value: refuse a missing one (a bare
# `$2` under `set -u` is an unbound-variable error) and a value that starts with `-`
# (it would be taken for an option by mkdir, find, rsync ...; write ./-name instead).
require_option_value() {
  if [[ $# -lt 2 ]]; then
    echo "error: $1 requires a value." >&2
    echo "  Usage: scripts/install.sh --target <dir> [--platform <name>|all] [--update | --projections-only]. Nothing was written." >&2
    exit 1
  fi
  case "$2" in
    -*)
      echo "error: $1 requires a value, but got '$(ascii_printable "$2")', which starts with '-' and would be read as an option." >&2
      if [[ "$1" == "--target" ]]; then
        echo "  For a path that really starts with '-', write it as ./$(ascii_printable "$2"). Nothing was written." >&2
      else
        echo "  Nothing was written." >&2
      fi
      exit 1
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) require_option_value "$@"; TARGET="$2"; shift 2 ;;
    --platform) require_option_value "$@"; PLATFORM="$2"; shift 2 ;;
    -u|--update) UPDATE=1; shift ;;
    --projections-only) PROJECTIONS_ONLY=1; shift ;;
    -n|--dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# Validate --platform before anything is resolved, created or written (ADR-010 D3):
# a typo or the removed value must not create $TARGET or reach any guard first.
# The removed value is matched in any letter case.
is_supported_platform() {
  local p
  for p in "${SUPPORTED_PLATFORMS[@]}"; do
    if [[ "$p" == "$1" ]]; then return 0; fi
  done
  return 1
}

if [[ "$PLATFORM" != "all" ]] && ! is_supported_platform "$PLATFORM"; then
  case "$PLATFORM" in
    [Cc][Uu][Rr][Ss][Oo][Rr])
      echo "error: platform 'cursor' was removed in v9.0.0 (see the Cursor migration item in docs/releases/v9.0.0.md; the v8.x releases are the last that support it)." >&2
      echo "  Existing .cursor/ files in your project are not touched. Nothing was written." >&2
      exit 1
      ;;
    *)
      echo "error: unknown platform '$(ascii_printable "$PLATFORM")'" >&2
      echo "  supported: $(join_comma "${SUPPORTED_PLATFORMS[@]}" all). Nothing was written." >&2
      exit 1
      ;;
  esac
fi

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

# True when the target is this repository's own root. The string comparison
# alone misses every alias of the root -- a symlink to it, a bind mount, a path
# through a symlinked parent -- because resolve_abs_path does not resolve
# symlinks, so `-ef` (same device and inode) is checked too. A target that does
# not exist yet cannot be the root, and `-ef` is false for it.
target_is_repo_root() {
  [[ "$TARGET_ABS" == "$REPO_ROOT" || "$TARGET_ABS" -ef "$REPO_ROOT" ]]
}

if target_is_repo_root; then
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
    # Refused since T552. At the root, --update did two harmful things and no
    # useful one that --projections-only does not also do:
    #   - merge_task_docs rewrites both task ledgers (dropping non-conforming
    #     rows); that path took active-tasks.md from 2460 lines to 11 in fee245a.
    #   - install_mcp_server_runtime copies implementation/runtime/* onto itself.
    #     Without rsync, sync_tree_into's fallback deleted the source first
    #     (implementation/runtime/memory/: 22 files to 0, measured by T550).
    # The refusal comes before anything is written, dry-run included.
    echo "error: refusing --update at the emage.code source repository root:" >&2
    echo "  $REPO_ROOT" >&2
    echo "reason: --update rewrites the task ledgers in docs/tasks/, seeds template files into docs/," >&2
    echo "  and copies implementation/runtime/ onto itself -- here docs/ is the repository's own record" >&2
    echo "  and implementation/ is the source the installer reads." >&2
    echo "use one of the following instead:" >&2
    echo "  - To refresh the root's own harness projections: scripts/install.sh --target . --platform all --projections-only" >&2
    echo "  - For repo maintenance: git pull && make sync && make verify" >&2
    echo "    (these regenerate and check implementation/.<platform>/ only; they do not write the root)" >&2
    exit 1
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

# $1 with every character that is not printable replaced by `?`, for messages:
# a path component or a link target comes from the target tree, so it may hold
# newlines or terminal escape sequences (T636).
printable() {
  printf '%s' "${1//[^[:print:]]/?}"
}

# The physical path of $1 -- every symlink on it resolved -- for a path that
# need not exist yet: its deepest existing ancestor is resolved with `cd -P`,
# and the components below that are appended as given.
physical_path() {
  local path="$1"
  local rest=""
  local parent base
  while [[ ! -d "$path" ]]; do
    parent="$(dirname -- "$path")"
    if [[ "$parent" == "$path" ]]; then break; fi
    rest="/$(basename -- "$path")$rest"
    path="$parent"
  done
  # Fails closed (T636): if the deepest existing ancestor cannot be entered
  # (no search permission, vanished), return 1 instead of printing a bare "$rest",
  # which a caller could take for a real path.
  if ! base="$(CDPATH='' cd -P -- "$path" && pwd -P)"; then
    echo "error: cannot resolve the physical path of: $(printable "$path")" >&2
    return 1
  fi
  printf '%s%s\n' "$base" "$rest"
}

# True when path $1 is directory $2 or lies anywhere below it. Each ancestor of
# $1's physical path is compared with $2 by `-ef` (same device and inode), as
# target_is_repo_root does, so neither a symlink anywhere on the way nor a bind
# mount of $2 hides the overlap; a plain string prefix would miss both.
path_within() {
  local path
  local parent
  path="$(physical_path "$1")"
  while :; do
    if [[ -e "$path" && "$path" -ef "$2" ]]; then return 0; fi
    parent="$(dirname -- "$path")"
    if [[ "$parent" == "$path" ]]; then return 1; fi
    path="$parent"
  done
}

# Refused since T559: every target strictly inside this repository, in every
# mode, dry-run included, before anything is written. The root itself is
# handled above. Two cases, for two reasons:
#   - implementation/ and anything below it is the source the installer reads,
#     so the install is written from itself. Measured on the pre-T559 script:
#     --update re-rendered AGENTS.md over its own source, created
#     implementation/implementation/ and exited 1 at the CLAUDE.md self-copy;
#     --target implementation/.<platform> (a generated tree) under rsync copied
#     the tree into its own subdirectory, several levels deep; --target implementation/new-dir
#     exited 0 after writing a second harness into the source tree.
#   - Anywhere else in the repository, an install writes a second copy of the
#     harness (AGENTS.md, CLAUDE.md, the platform trees, docs/ with its task
#     ledgers, implementation/runtime/) into the repository's own working tree.
#     No script, Makefile target or document installs inside the repository;
#     every recorded install targets a directory outside it.
if ! target_is_repo_root && path_within "$TARGET_ABS" "$REPO_ROOT"; then
  if path_within "$TARGET_ABS" "$IMPLEMENTATION"; then
    echo "error: refusing to install into the emage.code source tree:" >&2
    echo "  $TARGET_ABS" >&2
    echo "  is, or is inside, $IMPLEMENTATION" >&2
    echo "reason: implementation/ is the source the installer reads; a target there would be" >&2
    echo "  written from itself (AGENTS.md rendered over its own source, implementation/ nested in" >&2
    echo "  implementation/, platform trees copied into their own subdirectories)." >&2
  else
    echo "error: refusing to install inside the emage.code source repository:" >&2
    echo "  $TARGET_ABS" >&2
    echo "  is inside $REPO_ROOT" >&2
    echo "reason: an install writes a second copy of the harness (AGENTS.md, CLAUDE.md, the platform" >&2
    echo "  trees, docs/ and implementation/runtime/) into the repository's own working tree." >&2
  fi
  echo "use one of the following instead:" >&2
  echo "  - For installation testing: scripts/install.sh --target /tmp/emage-test --platform all" >&2
  echo "  - To refresh the root's own harness projections: scripts/install.sh --target . --platform all --projections-only" >&2
  exit 1
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

# --- Managed-path guard (T636, audit SEC-001) --------------------------------
#
# rsync -a, rsync --delete, cp and the Python writers all follow a symlink at a
# managed target path. With <target>/.claude a symlink to a directory outside the
# target, `--update` deleted that directory's files and wrote the harness into
# it. The same holds for docs, implementation, .vscode and every single-file write
# (.mcp.json, CLAUDE.md, AGENTS.md, the ledgers, the MCP/settings configs).
#
# refuse_unsafe_path is the one check. It takes a path at or below $TARGET and
# exits 1, before writing anything, when
#   - any component of it below $TARGET (so the managed ancestors docs,
#     implementation, implementation/runtime and .vscode, and the path itself)
#     is a symlink, existing or dangling; or
#   - its physical path (every symlink resolved) is not the physical $TARGET or
#     inside it; or
#   - it is not under $TARGET lexically at all, or names `..` (an internal error,
#     exit 70: the guard fails closed).
# $TARGET itself may be a symlink: the caller chose it, and containment is
# measured against its physical path. A path that does not exist yet passes (its
# deepest existing ancestor is checked). Called at the top of every tree writer,
# before every single-file write, and, for every managed path of the selected
# platform(s), once up front (guard_managed_paths) so that a refusal leaves
# nothing half-written.
refuse_unsafe_path() {
  local path="$1"
  local rel cur comp phys_target phys
  case "$path" in
    "$TARGET") return 0 ;;
    "$TARGET"/*) rel="${path#"$TARGET"/}" ;;
    *)
      echo "error: internal: managed path '$(printable "$path")' is not below the target '$(printable "$TARGET")'; nothing written." >&2
      exit 70
      ;;
  esac
  cur="$TARGET"
  while [[ -n "$rel" ]]; do
    comp="${rel%%/*}"
    if [[ "$rel" == */* ]]; then rel="${rel#*/}"; else rel=""; fi
    if [[ -z "$comp" || "$comp" == "." ]]; then continue; fi
    if [[ "$comp" == ".." ]]; then
      echo "error: internal: managed path '$(printable "$path")' contains '..'; nothing written." >&2
      exit 70
    fi
    cur="$cur/$comp"
    if [[ -L "$cur" ]]; then
      echo "error: refusing to write through a symlink: $(printable "$cur")" >&2
      echo "  It is a managed path of the install (or one of its parent directories) and is a symbolic" >&2
      echo "  link to $(printable "$(readlink -- "$cur" || echo '?')")." >&2
      echo "  rsync, cp and the merge scripts would write, and under --update delete, files at its" >&2
      echo "  destination, which may lie outside the target. Nothing was written." >&2
      echo "  Replace the link with a real directory or file, or point --target at the directory it" >&2
      echo "  resolves to, and re-run." >&2
      exit 1
    fi
  done
  phys_target="$(physical_path "$TARGET")" || exit 1
  phys="$(physical_path "$path")" || exit 1
  phys_target="${phys_target%/}"
  if [[ "$phys" != "$phys_target" && "$phys" != "$phys_target"/* ]]; then
    echo "error: refusing a managed path that resolves outside the target: $(printable "$path")" >&2
    echo "  resolves to: $(printable "$phys")" >&2
    echo "  target:      $(printable "$phys_target")" >&2
    echo "  Nothing was written." >&2
    exit 1
  fi
}

# Names never shipped from $IMPLEMENTATION/docs, at any depth (T559). Python
# writes __pycache__/ beside any script it imports, and docs/tasks/ ships one
# (validate-tasks.py): an authoring checkout that has run it has a gitignored
# implementation/docs/tasks/__pycache__/, which every fresh install copied, with
# and without rsync. On --update, docs/tasks/ goes through merge_task_docs,
# which copies top-level files only; every other docs/ subdirectory honours
# these names too. (Defined before the guard, which lists docs/ entries.)
DOCS_EXCLUDES=(__pycache__)

# refuse_unsafe_path for each of $1.. (paths relative to $TARGET).
refuse_unsafe_paths() {
  local rel
  for rel in "$@"; do refuse_unsafe_path "$TARGET/$rel"; done
}

# Prints, one per line and relative to $TARGET, the managed paths of platform
# $1: its tree(s) and every single file written into or beside them (the
# MCP/settings config and its provenance sidecar, CLAUDE.md). The one list the
# guard and the tests both use.
platform_managed_paths() {
  case "$1" in
    github) printf '%s\n' .github .vscode .vscode/mcp.json .vscode/mcp.json.provenance.json ;;
    gemini) printf '%s\n' .gemini .gemini/settings.json .gemini/settings.json.provenance.json ;;
    opencode) printf '%s\n' .opencode .opencode/opencode.json .opencode/opencode.json.provenance.json ;;
    pi) printf '%s\n' .pi .pi/mcp.json .pi/mcp.json.provenance.json ;;
    claude-code) printf '%s\n' .claude .mcp.json .mcp.json.provenance.json CLAUDE.md ;;
    cline) printf '%s\n' .cline .clinerules .cline/mcp.json .cline/mcp.json.provenance.json ;;
    *) internal_unknown_platform "$1" ;;
  esac
}

# Prints the platform $1's single-file MCP/settings config, relative to $TARGET (and to
# $IMPLEMENTATION for the generated copy). One map for the merge, the up-front JSON check and
# the Playwright notice.
platform_mcp_config() {
  case "$1" in
    github) printf '%s\n' .vscode/mcp.json ;;
    gemini) printf '%s\n' .gemini/settings.json ;;
    opencode) printf '%s\n' .opencode/opencode.json ;;
    pi) printf '%s\n' .pi/mcp.json ;;
    claude-code) printf '%s\n' .mcp.json ;;
    cline) printf '%s\n' .cline/mcp.json ;;
    *) internal_unknown_platform "$1" ;;
  esac
}

# A platform in SUPPORTED_PLATFORMS that one of the per-platform maps does not know is an
# installer bug, never a reason to skip it silently.
internal_unknown_platform() {
  echo "error: internal: platform '$(printable "$1")' is in SUPPORTED_PLATFORMS but a per-platform map of install.sh does not know it; nothing written." >&2
  exit 70
}

# Prints the platforms the run selected, one per line (--platform all expands to the list).
selected_platforms() {
  if [[ "$PLATFORM" == "all" ]]; then
    printf '%s\n' "${SUPPORTED_PLATFORMS[@]}"
  else
    printf '%s\n' "$PLATFORM"
  fi
}

# Prints the target-side docs/ paths a plain install or --update writes besides
# the fixed ones: every entry of $IMPLEMENTATION/docs (a merge_tree_preserve_existing
# or copy_tree_into destination, or a top-level file), minus DOCS_EXCLUDES, and
# every file of docs/tasks (the ledgers and support files merge_task_docs seeds).
docs_managed_paths() {
  local p t name e skip
  for p in "$IMPLEMENTATION/docs"/* "$IMPLEMENTATION/docs"/.[!.]*; do
    [[ -e "$p" ]] || continue
    name="${p##*/}"
    skip=0
    for e in "${DOCS_EXCLUDES[@]}"; do
      if [[ "$name" == "$e" ]]; then skip=1; fi
    done
    if [[ "$skip" -eq 1 ]]; then continue; fi
    printf 'docs/%s\n' "$name"
    if [[ "$name" == "tasks" && -d "$p" ]]; then
      for t in "$p"/* "$p"/.[!.]*; do
        if [[ -f "$t" ]]; then printf 'docs/tasks/%s\n' "${t##*/}"; fi
      done
    fi
  done
  return 0
}

# Prints every managed path of the selected platform(s) (PLATFORM, PROJECTIONS_ONLY).
# --projections-only never touches docs/ or implementation/, so it does not insist
# on them.
list_managed_paths() {
  local p
  printf '%s\n' AGENTS.md
  if [[ "$PROJECTIONS_ONLY" -ne 1 ]]; then
    printf '%s\n' docs docs/tasks docs/tasks/active-tasks.md docs/tasks/completed-tasks.md \
      implementation implementation/__init__.py implementation/runtime \
      implementation/runtime/memory implementation/runtime/security implementation/runtime/handoff
    docs_managed_paths
  fi
  while IFS= read -r p; do platform_managed_paths "$p"; done < <(selected_platforms)
}

# Runs before the first write of any mode (plain install, --update,
# --projections-only, and --dry-run, which reports the same refusal): checks every
# managed path of the selected platform(s) so a symlink at the last one cannot
# leave the first ones already written.
guard_managed_paths() {
  local rel
  while IFS= read -r rel; do
    refuse_unsafe_path "$TARGET/$rel"
  done < <(list_managed_paths)
}

# T682 (N-7): a run killed (SIGKILL, power loss) between the two renames of replace_tree_by_swap leaves
# the user's previous tree as <dest>.emage-old.<pid> and no <dest> at all; one killed during the copy
# leaves <dest>.emage-new.<pid>. The names carry the dead run's pid, so the per-run check of the next
# swap never sees them. Left alone, the next run would install a fresh tree and carry over none of the
# project-local files the old one held (a .claude/settings.json), and a later sweep or a hand-run `rm`
# could remove the only copy. A stale sibling is therefore REFUSED, not warned about: nothing is written
# (dry-run included), nothing is adopted or deleted, and the message says what each one is and what to do.
# T684 (SEC-T682-03): the names are shown with the byte-wise ascii_printable (the locale-dependent printable
# let a bidi override through in a UTF-8 locale), and the restore hint is `[ ! -e DEST ] && mv -- OLD DEST`
# with both paths quoted by shell_quote_ascii: pasted after DEST was recreated it does nothing, and a hostile
# name is data, never code.
guard_stale_swap_siblings() {
  local rel sibling found=0
  while IFS= read -r rel; do
    for sibling in "$TARGET/$rel".emage-old.* "$TARGET/$rel".emage-new.*; do
      if [[ ! -e "$sibling" && ! -L "$sibling" ]]; then continue; fi
      if [[ "$found" -eq 0 ]]; then
        echo "error: a previous update of this target was interrupted and left a temporary tree behind:" >&2
      fi
      found=1
      if [[ "$sibling" == *.emage-old.* ]]; then
        echo "  $(ascii_printable "$sibling")" >&2
        echo "    the tree this update was replacing. If $(ascii_printable "$TARGET/$rel") is missing it is your only copy:" >&2
        echo "      [ ! -e $(shell_quote_ascii "$TARGET/$rel") ] && mv -- $(shell_quote_ascii "$sibling") $(shell_quote_ascii "$TARGET/$rel")" >&2
        echo "    otherwise, after checking nothing in it is needed, remove it." >&2
      else
        echo "  $(ascii_printable "$sibling")" >&2
        echo "    the unfinished new tree of an interrupted update; remove it." >&2
      fi
    done
  done < <(list_managed_paths)
  if [[ "$found" -eq 1 ]]; then
    echo "Nothing was written and nothing was removed. Resolve the above and re-run." >&2
    exit 1
  fi
}

# True when src and dest are one and the same directory, however each is
# spelled (`-ef`: same device and inode, so symlinks, `.`, relative paths and
# bind mounts all resolve). The three tree writers below return early in that
# case: dest already IS src, so "make dest match src" is already true.
#
# That is exactly what rsync does with such a call (a self-sync is a no-op); it
# is the hand-rolled fallbacks that were destructive. sync_tree_into's fallback
# runs `rm -rf "$dest"` before copying from "$src" -- with src == dest it
# deleted the source and then failed to copy from it (T552: at the repository
# root, `--update` took implementation/runtime/memory/ from 22 files to 0).
# copy_tree_into's fallback removes each exclude "the copy placed" in dest --
# with src == dest that is the source's own _index/. Guarding the primitives,
# not one call site, fixes the class at any target: the repository root, an
# alias of it, or a target whose implementation/runtime/ is a symlink back to
# this repository's.
same_tree() {
  local src="$1"
  local dest="$2"
  if [[ -d "$src" && -d "$dest" && "$src" -ef "$dest" ]]; then
    echo "note: $dest is $src itself; nothing to copy." >&2
    return 0
  fi
  return 1
}

# --- Excluded paths: one meaning under both copiers -------------------------
#
# The tree writers take a list of excluded names. With rsync each becomes
# `--exclude=<name>`; without rsync a hand-rolled cp fallback must mean exactly
# the same thing, or the two copiers ship different trees. For a pattern with no
# `/` and no wildcard -- the only kind this script passes, and enforced below --
# rsync's meaning is:
#   1. it matches a file or directory of that name at ANY depth (an rsync
#      pattern without a `/` is compared with the last path component only);
#   2. a matching source path is never transferred, nor anything under it;
#   3. a matching destination path is never deleted or overwritten, even under
#      --delete (we never pass --delete-excluded) -- and a directory that
#      disappeared upstream is kept if it still holds one ("cannot delete
#      non-empty directory"; rsync still exits 0).
# Before T555 the cp fallbacks honoured none of 1-3 fully: they looked at the
# top level only, sync_tree_into's copied the SOURCE's excluded paths into
# every target that lacked its own (under --update without rsync, an authoring
# checkout's populated, gitignored runtime/memory/_index/ -- a search index of
# this repository -- was copied into client projects), and copy_tree_into's
# deleted a target's own top-level _index/ whenever the source had one too.
# exclude_hits, copy_contents_excluding and the two fallbacks below implement
# 1-3 by hand.

# The one internal invariant the cp fallbacks rely on: every exclude is a single
# literal path component, so `find -name` and a string compare both mean what
# rsync means. A `/` or a wildcard would make rsync match differently; refusing
# such a caller is cheaper than emulating rsync's full pattern language.
check_exclude_names() {
  local e
  for e in "$@"; do
    case "$e" in
      */* | *'*'* | *'?'* | *'['*)
        echo "error: internal: exclude '$e' must be one literal path component (no '/', '*', '?' or '[')." >&2
        exit 70
        ;;
    esac
  done
}

# Sets EXCLUDE_HITS to every path under $1 (relative to $1) whose own name is
# one of $2.., without descending into a hit: exactly the paths rsync would
# leave alone. A global, because bash functions cannot return arrays; each
# caller copies it out before the next call. The scan goes through a file, not
# a pipe, so a failed find stops the run instead of reading as "no hits".
# Scratch files this run created (the path lists of the scans), removed by swap_cleanup on any exit
# so an interrupt cannot leave them behind. make_temp_file sets MADE_TEMP (a global: a command
# substitution would lose the registration).
TEMP_FILES=()
MADE_TEMP=""
make_temp_file() {
  MADE_TEMP="$(mktemp)"
  TEMP_FILES+=("$MADE_TEMP")
}

EXCLUDE_HITS=()
exclude_hits() {
  local root="$1"
  shift
  EXCLUDE_HITS=()
  local expr=()
  local e
  for e in "$@"; do
    if [[ -z "$e" ]]; then continue; fi
    if [[ ${#expr[@]} -gt 0 ]]; then expr+=(-o); fi
    expr+=(-name "$e")
  done
  if [[ ${#expr[@]} -eq 0 || ! -d "$root" ]]; then return 0; fi
  local list
  make_temp_file
  list="$MADE_TEMP"
  # "$root/." rather than "$root": find does not follow a starting point that
  # is itself a symlink, and a symlinked .claude/ must be scanned like a real one.
  if ! find "$root/." -mindepth 1 \( "${expr[@]}" \) -prune -print0 >"$list"; then
    rm -f "$list"
    echo "error: could not scan $root for excluded paths; refusing to copy it unchecked." >&2
    exit 1
  fi
  local p
  while IFS= read -r -d '' p; do
    EXCLUDE_HITS+=("${p#"$root/./"}")
  done <"$list"
  rm -f "$list"
}

# Sets DIR_ENTRIES to every entry of directory $1, dotfiles included (none: an empty array).
# A global, like EXCLUDE_HITS. dotglob and nullglob are switched on for the one glob and put
# back exactly as they were found (SEC-010): shopt -q reads the state, no eval of builtin output.
DIR_ENTRIES=()
list_dir_entries() {
  local had_dotglob=0
  local had_nullglob=0
  if shopt -q dotglob; then had_dotglob=1; fi
  if shopt -q nullglob; then had_nullglob=1; fi
  shopt -s dotglob nullglob
  DIR_ENTRIES=("$1"/*)
  if [[ "$had_dotglob" -eq 0 ]]; then shopt -u dotglob; fi
  if [[ "$had_nullglob" -eq 0 ]]; then shopt -u nullglob; fi
}

# `cp $1 "$src/." "$dest/"` ($1 is -r, or -rn for a no-clobber merge), minus
# the relative paths in $4.. (hits from exclude_hits "$src"), which are never
# copied -- not copied and then removed. With no hits it runs exactly that
# single cp, as before T555. Otherwise it copies entry by entry, descending only
# into directories that contain a hit, so a whole subtree without one still
# goes in a single cp.
copy_contents_excluding() {
  local cp_opt="$1"
  local src="$2"
  local dest="$3"
  shift 3
  if [[ $# -eq 0 ]]; then
    run cp "$cp_opt" "$src/." "$dest/"
    return 0
  fi
  list_dir_entries "$src"
  local entries=(${DIR_ENTRIES[@]+"${DIR_ENTRIES[@]}"})
  local entry name h skip below
  for entry in ${entries[@]+"${entries[@]}"}; do
    name="${entry##*/}"
    skip=0
    below=()
    for h in "$@"; do
      if [[ "$h" == "$name" ]]; then skip=1; fi
      if [[ "$h" == "$name/"* ]]; then below+=("${h#"$name/"}"); fi
    done
    if [[ "$skip" -eq 1 ]]; then continue; fi
    if [[ ${#below[@]} -gt 0 ]]; then
      run mkdir -p "$dest/$name"
      copy_contents_excluding "$cp_opt" "$entry" "$dest/$name" "${below[@]}"
    else
      run cp "$cp_opt" "$entry" "$dest/"
    fi
  done
}

# --- Type conflicts: one meaning under both copiers (T559) -------------------
#
# A path can be one type in src and another in dest: a file where dest has a
# directory, a directory where dest has a file or a symlink. `rsync -a` (no
# --delete, no --force; measured with 3.2.7) resolves each such path:
#   1. src directory, dest non-directory (a file, or any symlink -- even one to
#      a directory): dest's path is removed and the directory created.
#   2. src non-directory, dest an EMPTY directory: the directory is removed.
#   3. src non-directory, dest a NON-EMPTY directory (excluded content counts):
#      refused -- "could not make way for new regular file", exit 23, after
#      transferring everything else. --dry-run fails the same way.
#   4. src file or symlink over a dest symlink, or src symlink over a dest
#      file: dest's path is replaced. A symlink is never written through.
# `cp -r` does none of this. It exits 1 ("cannot overwrite directory") for 1-3,
# and for a file over a symlink to a file it writes THROUGH the link, into
# wherever the link points (T555 §8.2). make_way_for_source gives the cp
# fallback rsync's results: it removes what rsync would remove, and refuses
# what rsync refuses -- before writing anything, naming every such path,
# rather than after a partial copy as rsync does. sync_tree_into's fallback
# empties dest before copying, so only rule 3 can arise there, at the
# ancestors of a kept (excluded) path: refuse_kept_paths_under_source_nondirs.

# True when directory $1 has no entries at all, dotfiles included.
dir_is_empty() {
  list_dir_entries "$1"
  [[ ${#DIR_ENTRIES[@]} -eq 0 ]]
}

# Rule 3, for either fallback: exit 1, naming each dest path ($3..) that is a
# non-empty directory where src ($1) has a file or symlink. Called before the
# fallback has written anything.
refuse_blocked_paths() {
  local src="$1"
  local dest="$2"
  shift 2
  echo "error: cannot copy $src into $dest: where the source has a file or symlink," >&2
  echo "  the target has a directory that is not empty:" >&2
  local rel
  for rel in "$@"; do echo "    $dest/$rel" >&2; done
  echo "  rsync refuses this too (\"could not make way\"). Nothing was written to $dest;" >&2
  echo "  move or remove the directory and re-run." >&2
  exit 1
}

# Rule 3 for sync_tree_into's fallback. Each kept path $3.. (an excluded dest
# path, relative to dest $2) survives the replace inside its ancestors, which
# therefore stay non-empty directories. Where src $1 has a file or symlink at
# one of those ancestors, rsync refuses to make way for it, and so does this --
# before the fallback's `rm -rf "$dest"`. Before T559 the fallback ran that rm
# first and then either failed at `mkdir -p` (the target's kept path deleted,
# its backup left in a temp directory) or restored the kept path THROUGH a
# symlink shipped by src, writing outside dest, and exited 0.
refuse_kept_paths_under_source_nondirs() {
  local src="$1"
  local dest="$2"
  shift 2
  local blocked=()
  local h anc rest b dup
  for h in "$@"; do
    anc=""
    rest="$h"
    while [[ "$rest" == */* ]]; do
      anc="${anc:+$anc/}${rest%%/*}"
      rest="${rest#*/}"
      if [[ -L "$src/$anc" || ( -e "$src/$anc" && ! -d "$src/$anc" ) ]]; then
        dup=0
        for b in ${blocked[@]+"${blocked[@]}"}; do
          if [[ "$b" == "$anc" ]]; then dup=1; fi
        done
        if [[ "$dup" -eq 0 ]]; then blocked+=("$anc"); fi
        break
      fi
    done
  done
  if [[ ${#blocked[@]} -gt 0 ]]; then refuse_blocked_paths "$src" "$dest" "${blocked[@]}"; fi
}

# Writes every path under $1, NUL-separated and pre-order, to file $2 --
# without descending into a path named by one of $3.. (the excluded names,
# which are never copied, so never compared). Through a file, not a pipe, so
# a failed find stops the run instead of reading as "no paths".
list_source_paths() {
  local src="$1"
  local list="$2"
  shift 2
  local expr=()
  local e
  for e in "$@"; do
    if [[ -z "$e" ]]; then continue; fi
    if [[ ${#expr[@]} -gt 0 ]]; then expr+=(-o); fi
    expr+=(-name "$e")
  done
  if [[ ${#expr[@]} -gt 0 ]]; then expr=(\( "${expr[@]}" \) -prune -o); fi
  if ! find "$src/." -mindepth 1 ${expr[@]+"${expr[@]}"} -print0 >"$list"; then
    rm -f "$list"
    echo "error: could not scan $src; refusing to copy it unchecked." >&2
    exit 1
  fi
}

# Compares every path of $1 (minus the excluded names $3..) with the same path
# under $2, then removes each dest path rsync would replace (rules 1, 2, 4), or
# exits 1 with nothing written if any path is rule 3.
make_way_for_source() {
  local src="$1"
  local dest="$2"
  shift 2
  if [[ ! -d "$dest" ]]; then return 0; fi
  local list
  make_temp_file
  list="$MADE_TEMP"
  list_source_paths "$src" "$list" "$@"
  local remove=()
  local blocked=()
  local gone=()
  local p rel s d g below
  while IFS= read -r -d '' p; do
    rel="${p#"$src/./"}"
    below=0
    for g in ${gone[@]+"${gone[@]}"}; do
      if [[ "$rel" == "$g/"* ]]; then below=1; fi
    done
    if [[ "$below" -eq 1 ]]; then continue; fi
    s="$src/$rel"
    d="$dest/$rel"
    if [[ ! -e "$d" && ! -L "$d" ]]; then continue; fi
    if [[ -d "$s" && ! -L "$s" ]]; then
      if [[ -d "$d" && ! -L "$d" ]]; then continue; fi
      remove+=("$rel")
      gone+=("$rel")
    elif [[ -d "$d" && ! -L "$d" ]]; then
      if dir_is_empty "$d"; then remove+=("$rel"); else blocked+=("$rel"); fi
      gone+=("$rel")
    elif [[ -L "$d" || -L "$s" ]]; then
      remove+=("$rel")
    fi
  done <"$list"
  rm -f "$list"
  if [[ ${#blocked[@]} -gt 0 ]]; then refuse_blocked_paths "$src" "$dest" "${blocked[@]}"; fi
  for rel in ${remove[@]+"${remove[@]}"}; do
    if [[ -d "$dest/$rel" && ! -L "$dest/$rel" ]]; then
      run rmdir "$dest/$rel"
    else
      run rm -f "$dest/$rel"
    fi
  done
}

# Merge source tree into dest without nesting when dest already exists.
# `cp -r src dest` creates dest/srcname when dest is present; this copies contents.
# $3.. (optional, variadic): excluded names -- see "Excluded paths" above for
# their exact meaning, which is rsync's. The installer neither writes nor
# deletes a path so named, at any depth, for two distinct reasons that share one
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
  check_exclude_names ${excludes[@]+"${excludes[@]}"}
  refuse_unsafe_path "$dest"
  if same_tree "$src" "$dest"; then return 0; fi
  run mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    local rsync_args=(-a --chmod=go-w)
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
    # Never copies a source path that rsync --exclude would skip, so it never
    # has to delete one afterwards. The pre-T555 fallback copied everything and
    # then ran `rm -rf "$dest/$e"` for each top-level exclude the source had:
    # that removed the target's OWN copy along with the source's (a plain
    # re-install deleted a target's built _index/), and missed every nested
    # one (runtime/memory/context_retriever_mcp_server/__pycache__/ shipped).
    # Type conflicts are resolved first, as rsync resolves them (see "Type
    # conflicts" above): before T559 each one made cp exit 1 part-way through,
    # or write through a symlink in the target.
    exclude_hits "$src" ${excludes[@]+"${excludes[@]}"}
    make_way_for_source "$src" "$dest" ${excludes[@]+"${excludes[@]}"}
    copy_contents_excluding -r "$src" "$dest" ${EXCLUDE_HITS[@]+"${EXCLUDE_HITS[@]}"}
  fi
}

# Replace dest with source, removing files that no longer exist upstream.
# Every path named in $3.. (variadic; see "Excluded paths" above -- a name
# matches at any depth) is left untouched by this whole-tree replace: neither
# deleted nor overwritten, and never copied from source. Two kinds of path need
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
  check_exclude_names ${excludes[@]+"${excludes[@]}"}
  refuse_unsafe_path "$dest"
  if same_tree "$src" "$dest"; then return 0; fi
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    local rsync_args=(-a --chmod=go-w --delete)
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
    # Which of dest's own paths to keep: every excluded name, at any depth.
    # Top-level ones first, in the caller's order (the pre-T555 fallback's
    # order, so its output is unchanged where nothing nested is involved), then
    # nested ones -- which the pre-T555 fallback deleted, and rsync keeps.
    exclude_hits "$dest" ${excludes[@]+"${excludes[@]}"}
    local dest_hits=(${EXCLUDE_HITS[@]+"${EXCLUDE_HITS[@]}"})
    local keep=()
    local h
    for e in ${excludes[@]+"${excludes[@]}"}; do
      for h in ${dest_hits[@]+"${dest_hits[@]}"}; do
        if [[ "$h" == "$e" ]]; then keep+=("$h"); fi
      done
    done
    for h in ${dest_hits[@]+"${dest_hits[@]}"}; do
      if [[ "$h" == */* ]]; then keep+=("$h"); fi
    done
    refuse_kept_paths_under_source_nondirs "$src" "$dest" ${keep[@]+"${keep[@]}"}
    # Which of src's paths never to copy: the same names, at any depth. Before
    # T555 nothing was skipped here -- the whole source was copied, and only
    # the paths dest already had were put back -- so a target without its own
    # _index/ or __pycache__/ received the installer's.
    exclude_hits "$src" ${excludes[@]+"${excludes[@]}"}
    local src_hits=(${EXCLUDE_HITS[@]+"${EXCLUDE_HITS[@]}"})
    replace_tree_by_swap "$src" "$dest" "${#src_hits[@]}" ${src_hits[@]+"${src_hits[@]}"} ${keep[@]+"${keep[@]}"}
  fi
}

# Directories replace_tree_by_swap has built or moved aside and not yet finished with, for
# swap_cleanup (EXIT, and INT/TERM through `exit`). SWAP_BUILD is the sibling being built;
# SWAP_OLD/SWAP_DEST are set only between the two renames of the swap.
SWAP_BUILD=""
SWAP_OLD=""
SWAP_DEST=""
# 1 only once BOTH renames of the swap have succeeded (T682 SEC-T682-02): swap_cleanup must not infer
# "the swap completed" from dest existing, which a failed second rename can also leave behind.
SWAP_DONE=0
# Removes a moved-aside old tree. Its top directory may be read-only or not searchable (the mode the
# user chose, T682 N-2), which would make `rm -rf` fail after the swap had succeeded: give the owner
# back write and search first (best effort; the tree is garbage from here on). Never through a symlink:
# chmod follows a link given as its own argument, and the target is not ours (SEC-T682-05).
discard_old_tree() {
  if [[ "$DRY_RUN" -eq 0 && -d "$1" && ! -L "$1" ]]; then chmod -R u+rwX -- "$1" 2>/dev/null || true; fi
  run rm -rf -- "$1"
}

# MV_T is (-T) where `mv` is GNU, else empty. `mv -T src dst` treats dst as the final name, never as a
# directory to move src into: a directory someone creates at dst between our checks and the rename makes
# the rename fail (or replace an empty one) instead of nesting our tree inside theirs (T682 N-3b).
# Detected, not assumed: BSD and busybox `mv` either lack -T or differ, and keep the plain rename.
MV_T=()
detect_mv_flags() {
  local version
  MV_T=()
  version="$(mv --version 2>/dev/null || true)"
  if [[ "$version" == *"GNU coreutils"* ]]; then MV_T=(-T); fi
}
detect_mv_flags

swap_cleanup() {
  # A second signal while the cleanup runs (a repeated Ctrl-C, a supervisor's TERM after HUP) would
  # re-enter the signal traps below, whose `exit` cuts the cleanup short and leaves the sibling trees
  # behind (T682 N-3): ignore them until the cleanup is done. Must stay the first command.
  trap '' HUP INT QUIT TERM
  local f
  # SWAP_OLD is set from before the first rename until the swap is finished. Three states (T682
  # SEC-T682-02): both renames succeeded (SWAP_DONE=1, interrupted before the delete): the old tree is
  # garbage. Not done and dest is missing: the old tree is the only copy, put it back. Anything else
  # (the second rename failed and dest was recreated, or SWAP_OLD is not ours): leave BOTH alone.
  if [[ -n "$SWAP_OLD" && ( -e "$SWAP_OLD" || -L "$SWAP_OLD" ) ]]; then
    if [[ "$SWAP_DONE" -eq 1 ]]; then
      discard_old_tree "$SWAP_OLD" || true
    elif [[ ! -e "$SWAP_DEST" && ! -L "$SWAP_DEST" ]]; then
      mv ${MV_T[@]+"${MV_T[@]}"} -- "$SWAP_OLD" "$SWAP_DEST" || true
    else
      echo "note: the update did not finish; $(printable "$SWAP_OLD") and $(printable "$SWAP_DEST") were both left in place; check them." >&2
    fi
  fi
  # The build tree may have been given a read-only mode already (T682 N-2): give the owner access back
  # first, or the rm cannot empty it (SEC-T682-01). Never through a symlink.
  if [[ -n "$SWAP_BUILD" && -d "$SWAP_BUILD" && ! -L "$SWAP_BUILD" ]]; then
    chmod -R u+rwX -- "$SWAP_BUILD" 2>/dev/null || true
  fi
  if [[ -n "$SWAP_BUILD" && -d "$SWAP_BUILD" ]]; then rm -rf -- "$SWAP_BUILD" || true; fi
  for f in ${TEMP_FILES[@]+"${TEMP_FILES[@]}"}; do rm -f -- "$f" || true; done
  return 0
}
trap swap_cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 131' QUIT
trap 'exit 143' TERM

# The last step of replace_tree_by_swap (T677: split out of it): the finished tree $1 takes the place of
# $2; an existing $2 is first moved aside to $3 and discarded after the swap (SWAP_OLD/SWAP_DEST/SWAP_DONE
# tell swap_cleanup which state an interrupt found).
swap_build_into_place() {
  local build="$1"
  local dest="$2"
  local old="$3"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$DRY_RUN" -eq 0 && ( -e "$old" || -L "$old" ) ]]; then
      echo "error: $(printable "$old") appeared while the new tree was built; remove it and re-run. $(printable "$dest") was not touched." >&2
      exit 1
    fi
    if [[ "$DRY_RUN" -eq 0 ]]; then SWAP_OLD="$old"; SWAP_DEST="$dest"; fi
    run mv ${MV_T[@]+"${MV_T[@]}"} -- "$dest" "$old"
    run mv ${MV_T[@]+"${MV_T[@]}"} -- "$build" "$dest"
    SWAP_DONE=1
    discard_old_tree "$old"
  else
    run mv ${MV_T[@]+"${MV_T[@]}"} -- "$build" "$dest"
  fi
}

# The no-rsync half of sync_tree_into (SEC-004): make $2 hold exactly $1's tree (minus its
# excluded paths) plus $2's own kept paths, without ever leaving $2 half-deleted. The new tree is
# built in a sibling directory of $2 -- same filesystem, so the swap is two renames -- and only a
# finished tree replaces the old one. A failure or an interrupt before the swap leaves $2 exactly
# as it was (swap_cleanup removes the sibling); before SEC-004 `rm -rf "$dest"` ran first, and the
# project-local files it was meant to keep sat in a /tmp backup until the restore, if there was one.
# $3 is the number of source hits ($4..), then come the kept dest paths (relative to $2).
replace_tree_by_swap() {
  local src="$1"
  local dest="$2"
  local n_src_hits="$3"
  shift 3
  local src_hits=("${@:1:$n_src_hits}")
  local keep=("${@:$((n_src_hits + 1))}")
  local build="$dest.emage-new.$$"
  local old="$dest.emage-old.$$"
  local rel mode
  # Both siblings are checked for a symlink or a foreign leftover BEFORE anything is created, and
  # the build directory is created with a plain `mkdir` (no -p): it fails if the name appeared in
  # between, so a directory or link planted by someone else is never adopted or deleted.
  refuse_unsafe_path "$build"
  refuse_unsafe_path "$old"
  if [[ "$DRY_RUN" -eq 0 && ( -e "$build" || -L "$build" || -e "$old" || -L "$old" ) ]]; then
    echo "error: $(printable "$build") or $(printable "$old") already exists; remove it and re-run. Nothing was written." >&2
    exit 1
  fi
  run mkdir -- "$build"
  if [[ "$DRY_RUN" -eq 0 ]]; then SWAP_BUILD="$build"; fi
  copy_contents_excluding -r "$src" "$build" ${src_hits[@]+"${src_hits[@]}"}
  for rel in ${keep[@]+"${keep[@]}"}; do
    run mkdir -p "$(dirname "$build/$rel")"
    run rm -rf "$build/$rel"
    run copy_kept_path "$dest/$rel" "$build/$rel"
  done
  # The new top directory gets the old one's mode (group/world write stripped, SEC-005), not mkdir's
  # default -- AFTER the copy (T682 N-2): a 555/500/600 old tree would otherwise make the copy into
  # the read-only (or non-searchable) build directory fail, and the update with it.
  if [[ -d "$dest" ]]; then
    mode="$(stat -c '%a' -- "$dest" 2>/dev/null || stat -f '%Lp' -- "$dest" 2>/dev/null || true)"
    if [[ -n "$mode" ]]; then run chmod "$mode" "$build"; fi
    run chmod go-w "$build"
  fi
  swap_build_into_place "$build" "$dest" "$old"
  SWAP_BUILD=""
  SWAP_OLD=""
  SWAP_DEST=""
  SWAP_DONE=0
}

# cp -r of a project-local path the harness keeps ($1 -> $2) under the CALLER's umask, not the
# tightened one: the file is the project's own, so its group bits are not ours to strip.
copy_kept_path() {
  (umask "$ORIG_UMASK" && cp -r -- "$1" "$2")
}

# Merge source tree into dest while preserving existing dest files.
# Used by --update for docs templates so local/project docs are never overwritten.
# $3.. (optional, variadic): excluded names, with the meaning described under
# "Excluded paths" above. A path so named is never copied from source; dest's
# own is never touched here anyway, since nothing existing is overwritten.
merge_tree_preserve_existing() {
  local src="$1"
  local dest="$2"
  local excludes=("${@:3}")
  check_exclude_names ${excludes[@]+"${excludes[@]}"}
  refuse_unsafe_path "$dest"
  if same_tree "$src" "$dest"; then return 0; fi
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    local rsync_args=(-a --chmod=go-w --ignore-existing)
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
    run mkdir -p "$dest"
    exclude_hits "$src" ${excludes[@]+"${excludes[@]}"}
    copy_contents_excluding -rn "$src" "$dest" ${EXCLUDE_HITS[@]+"${EXCLUDE_HITS[@]}"}
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

# grep -rq with its three outcomes kept apart: 0 = a line matches, 1 = no line
# matches, anything else = the scan itself failed (missing tool, unreadable
# file). Inside a bare `if grep ...` a failed scan reads as "no match" and the
# guard passes without having checked anything. That is how the `name:` check
# below was skipped on every host without ripgrep -- CI's python:3.12-alpine
# image among them -- while it still called `rg` (T552). grep is POSIX and in
# busybox, so it is present wherever this script can run at all.
source_matches() {
  local pattern="$1"
  local path="$2"
  local status=0
  grep -rq -e "$pattern" "$path" || status=$?
  if [[ "$status" -eq 0 ]]; then return 0; fi
  if [[ "$status" -eq 1 ]]; then return 1; fi
  echo "error: could not scan $path for '$pattern' (grep exit $status); refusing to run $MODE_FLAG unchecked." >&2
  exit 1
}

validate_github_agents() {
  # Guard: --update must not propagate corrupted subagent aliases (v6.0.5 contract).
  # GitHub agents must omit `name:` (use slug aliases) and orchestrators must use kebab-case.
  local github_agents="$IMPLEMENTATION/.github/agents"
  if [[ ! -d "$github_agents" ]]; then
    return 0
  fi

  # Check that no agent file has a `name:` key (they should omit it for slug aliasing).
  if source_matches '^name:' "$github_agents"; then
    echo "error: source .github/agents have corrupted 'name:' keys (violates v6.0.5 contract)." >&2
    echo "  Run 'make sync' in the emage.code repo to regenerate projections." >&2
    exit 1
  fi

  # Check that orchestrator agents: lists use kebab-case slugs, not display names.
  for orch in orchestrator poc-orchestrator; do
    local file="$github_agents/${orch}.agent.md"
    if [[ -f "$file" ]]; then
      if source_matches '^agents: \[.*[A-Z]' "$file"; then
        echo "error: $file has display-name aliases (not kebab-case slugs)." >&2
        echo "  Run 'make sync' in the emage.code repo to regenerate projections." >&2
        exit 1
      fi
    fi
  done
}

# Read-only notice (ADR-010 D3): Cursor support was removed in v9.0.0, so a
# .cursor/ that an earlier release generated is no longer written, pruned or
# checked here -- and is never deleted. Detection looks at, and never writes,
# the generator's own markers; a symlinked .cursor or marker is not read.
notice_previous_cursor_install() {
  local dir="$TARGET/.cursor"
  local found=0
  if [[ ! -d "$dir" || -L "$dir" ]]; then return 0; fi
  if [[ -f "$dir/.generated-manifest.json" && ! -L "$dir/.generated-manifest.json" ]] \
     && grep -Eq '"platform"[[:space:]]*:[[:space:]]*"cursor"' "$dir/.generated-manifest.json"; then
    found=1
  elif [[ -f "$dir/mcp.json.provenance.json" && ! -L "$dir/mcp.json.provenance.json" ]]; then
    found=1
  fi
  if [[ "$found" -ne 1 ]]; then return 0; fi
  echo "warning: $(printable "$dir") holds a Cursor install written by an earlier emage.code release." >&2
  echo "  Cursor support was removed in v9.0.0: that folder is no longer updated, pruned or checked, and this installer does not delete it." >&2
  echo "  Its MCP server versions are frozen at the version that wrote it, and nothing prunes it." >&2
  echo "  An install from v7.x or older can still contain unpinned or non-existent launchers (for example 'npx -y @anthropic/mcp-filesystem', see M-9 of the v8.0.0 release notes)." >&2
  echo "  Open .cursor/mcp.json and remove the 'filesystem' entry if it runs @anthropic/mcp-filesystem, and the keys e2b, redis, figma and notion if present (M-9 of the v8.0.0 release notes). --force-prune-keys exists only in the v8.0.0 installer." >&2
  echo "  Remove the folder or edit it by hand; see the Cursor migration item in docs/releases/v9.0.0.md." >&2
}

validate_before_update() {
  # Pre-flight checks before --update to prevent propagating corrupted state.
  if [[ "$UPDATE" -eq 1 ]]; then
    notice_previous_cursor_install
    for d in .github .gemini .opencode .pi .claude .cline .clinerules; do
      if [[ -d "$TARGET/$d" ]]; then
        local exception=""
        case "$d" in
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

# True when the platform's source (generated) MCP config in $IMPLEMENTATION names the
# Playwright server; $1 is the platform.
platform_ships_playwright() {
  local config
  config="$IMPLEMENTATION/$(platform_mcp_config "$1")"
  [[ -f "$config" ]] && grep -q '"playwright"' "$config"
}

# Before the first write of any mode (T672, SEC-T658-05 b): every existing MCP/settings config of
# the selected platform(s) -- and its provenance sidecar -- must be valid JSON. The merge would
# otherwise die with a traceback AFTER the platform tree was replaced. One line naming the file,
# exit 1, nothing written.
validate_existing_mcp_configs() {
  local p rel
  while IFS= read -r p; do
    rel="$(platform_mcp_config "$p")"
    if [[ -f "$TARGET/$rel" ]]; then
      python3 -I "$REPO_ROOT/scripts/merge-mcp-json.py" --validate-only \
        --dest "$TARGET/$rel" --old-sidecar "$TARGET/$rel.provenance.json" || exit 1
    fi
  done < <(selected_platforms)
}

# Every selected platform must be known to ALL the per-platform pieces before anything is written
# (SEC-T672-04): an install_<name> function, platform_managed_paths and platform_mcp_config. Each
# map is probed in a subshell, because an unknown name makes it `exit 70`. Without this check a
# missing piece surfaced halfway through an `all` install, after earlier platforms were written.
verify_platform_maps() {
  local p
  while IFS= read -r p; do
    if ! declare -F "install_${p//-/_}" >/dev/null \
       || ! (platform_managed_paths "$p") >/dev/null 2>&1 \
       || ! (platform_mcp_config "$p") >/dev/null 2>&1; then
      internal_unknown_platform "$p"
    fi
  done < <(selected_platforms)
}

merge_task_docs() {
  refuse_in_projections_only merge_task_docs "$TARGET/docs/tasks"
  refuse_unsafe_paths docs docs/tasks docs/tasks/active-tasks.md docs/tasks/completed-tasks.md
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
# the dest file already exists (plain install, --update and --projections-only
# alike). Falls back to a plain copy when the dest file doesn't exist yet. The MCP file's provenance sidecar
# (<mcpfile>.provenance.json, ADR-002) is carried alongside it: merged runs
# pass it to merge-mcp-json.py for diff-based pruning and to refresh the
# dest-side sidecar; fresh-install/no-dest runs plain-copy it too.
merge_or_copy_mcp_json() {
  local src="$1"
  local dest="$2"
  local extra_flag="${3:-}"   # T680: --drop-env-form for .pi/mcp.json only
  local src_sidecar="${src}.provenance.json"
  local dest_sidecar="${dest}.provenance.json"
  refuse_unsafe_path "$dest"
  refuse_unsafe_path "$dest_sidecar"
  # Merge into an existing config in EVERY mode (SEC-T658-05 a): a plain install used to
  # overwrite it wholesale, user permission/excludeTools rules and servers included. Merging is
  # what --update does, so a re-run of the same command line never loses the user's content.
  if [[ -f "$dest" ]]; then
    local args=("$REPO_ROOT/scripts/merge-mcp-json.py" --source "$src" --dest "$dest")
    if [[ -f "$src_sidecar" ]]; then
      args+=(--old-sidecar "$dest_sidecar" --new-sidecar "$src_sidecar")
    fi
    if [[ -n "$extra_flag" ]]; then
      args+=("$extra_flag")
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
  refuse_unsafe_paths docs
  run mkdir -p "$TARGET/docs"
  if [[ "$UPDATE" -eq 1 ]]; then
    local e skip
    for sub in "$IMPLEMENTATION/docs"/*/; do
      [[ -d "$sub" ]] || continue
      name="$(basename "$sub")"
      skip=0
      for e in "${DOCS_EXCLUDES[@]}"; do
        if [[ "$name" == "$e" ]]; then skip=1; fi
      done
      if [[ "$skip" -eq 1 ]]; then continue; fi
      if [[ "$name" == "tasks" ]]; then
        merge_task_docs
      else
        merge_tree_preserve_existing "$sub" "$TARGET/docs/$name" "${DOCS_EXCLUDES[@]}"
      fi
    done
  else
    copy_tree_into "$IMPLEMENTATION/docs" "$TARGET/docs" "${DOCS_EXCLUDES[@]}"
  fi
}

install_agents_doc() {
  local src="$IMPLEMENTATION/AGENTS.md"
  local dest="$TARGET/AGENTS.md"
  refuse_unsafe_path "$dest"

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
# search index) is excluded in both directions, at any depth: never copied
# from $IMPLEMENTATION, and never overwritten or deleted in the target.
# Being gitignored (build.py output) only keeps it out of git -- this
# installer reads the working tree, and in an authoring checkout
# $IMPLEMENTATION/runtime/memory/_index/ holds an index of THIS repository,
# which must never reach a client project (T555). A target's own _index/ is
# project-specific generated content this installer must not touch.
install_mcp_server_runtime() {
  refuse_in_projections_only install_mcp_server_runtime "$TARGET/implementation"
  refuse_unsafe_paths implementation implementation/__init__.py implementation/runtime
  run mkdir -p "$TARGET/implementation"
  if [[ ! -f "$TARGET/implementation/__init__.py" ]]; then
    run touch "$TARGET/implementation/__init__.py"
  fi
  run mkdir -p "$TARGET/implementation/runtime"
  install_tree_into "$IMPLEMENTATION/runtime/memory" "$TARGET/implementation/runtime/memory" "_index" "__pycache__"
  install_tree_into "$IMPLEMENTATION/runtime/security" "$TARGET/implementation/runtime/security" "__pycache__"
  # Not an MCP server, but runtime source a shipped command names by path:
  # /handoff step 3 drafts its payload against
  # implementation/runtime/handoff/schema-v1.json, and the security
  # guidelines require handoff JSON to pass runtime/handoff/validator.py.
  # The whole tree ships (schema, validator, worked example) so
  # both references resolve in an installed project exactly as they do here
  # (T553). __pycache__/ is excluded for the same reason as above.
  install_tree_into "$IMPLEMENTATION/runtime/handoff" "$TARGET/implementation/runtime/handoff" "__pycache__"
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

install_github() {
  install_tree_into "$IMPLEMENTATION/.github" "$TARGET/.github" "${GITHUB_LOCAL_PATHS[@]}"
  refuse_unsafe_paths .vscode
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
  merge_or_copy_mcp_json "$IMPLEMENTATION/.pi/mcp.json" "$TARGET/.pi/mcp.json" --drop-env-form
}

install_claude_code() {
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude" "${CLAUDE_LOCAL_PATHS[@]}"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.mcp.json" "$TARGET/.mcp.json"
  refuse_unsafe_paths CLAUDE.md
  # CLAUDE.md is generator-owned and replaced in every mode; say so when that discards a file of the
  # project's own (SEC-008 a), so the replacement is never silent.
  if [[ -f "$TARGET/CLAUDE.md" ]] && ! cmp -s "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"; then
    echo "note: replacing the existing $(printable "$TARGET/CLAUDE.md") with the generated one; its previous content is not kept." >&2
  fi
  run cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"
}

install_cline() {
  install_tree_into "$IMPLEMENTATION/.cline" "$TARGET/.cline" "mcp.json" "mcp.json.provenance.json"
  install_tree_into "$IMPLEMENTATION/.clinerules" "$TARGET/.clinerules"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cline/mcp.json" "$TARGET/.cline/mcp.json"
}

# --- Main flow: every function above is defined; nothing is written before the checks below. ---
# Before the first write of any mode, dry-run included (T636, SEC-001).
verify_platform_maps
guard_managed_paths
guard_stale_swap_siblings
validate_existing_mcp_configs

# --dry-run creates nothing, the target directory included (SEC-008 b).
run mkdir -p "$TARGET"

if [[ "$UPDATE" -eq 1 ]]; then
  require_existing_install
  validate_before_update
fi

# Runs the install_<platform> function of platform $1 (dashes become underscores). A supported
# platform without one is an installer bug: fail closed, never skip.
install_platform() {
  local fn="install_${1//-/_}"
  if ! declare -F "$fn" >/dev/null; then internal_unknown_platform "$1"; fi
  "$fn"
}

install_common
while IFS= read -r selected; do install_platform "$selected"; done < <(selected_platforms)

# The Playwright MCP server needs a browser that neither npx nor the installer fetches, and writes
# its output to .playwright-mcp/ in the launch directory, which the installer does not put in the
# project's .gitignore (QA-T648-02). Printed when a selected platform's config ships the server;
# the commands are those of implementation/PREREQUISITES.md ("Browser for the `playwright`
# server"), the version read from the generated config so a pin bump cannot leave this stale.
print_playwright_notice() {
  local p config pin=""
  while IFS= read -r p; do
    if platform_ships_playwright "$p"; then
      config="$IMPLEMENTATION/$(platform_mcp_config "$p")"
      pin="$(grep -o '@playwright/mcp@[0-9A-Za-z.+-]*' "$config" | head -n 1 || true)"
      echo ""
      echo "Note: this install includes the Playwright MCP server. It does not bundle or download a"
      echo "browser, so its first browser tool call fails until you install one (once, about 670 MB):"
      echo "  npx -y ${pin:-@playwright/mcp} install-browser chrome-for-testing"
      echo "Its output (page snapshots, downloads) goes to .playwright-mcp/ under the directory your"
      echo "assistant starts from, and this installer does not edit your .gitignore: add"
      echo "  .playwright-mcp/"
      echo "to your project's .gitignore, otherwise page content can be committed by accident."
      echo "(Details: implementation/PREREQUISITES.md, section \"Browser for the \`playwright\` server\".)"
      return 0
    fi
  done < <(selected_platforms)
}

if [[ "$PROJECTIONS_ONLY" -eq 1 ]]; then
  # The MCP-dependency and search-index notices below describe the runtime
  # install, which this mode deliberately did not perform.
  echo "Refreshed emage.code harness projections ($PLATFORM) in $TARGET; docs/ and implementation/ were not touched."
  print_playwright_notice
  exit 0
fi

if [[ "$UPDATE" -eq 1 ]]; then
  echo "Updated emage.code ($PLATFORM) in $TARGET"
else
  echo "Installed emage.code ($PLATFORM) into $TARGET"
fi
echo "Next: configure MCP env vars, then invoke /new-project in your assistant."
print_playwright_notice

# Some MCP servers (context-retriever, security-audit) are plain Python stdio
# processes launched via `python3 -m ...` from the generated mcp.json/settings
# files, and need the third-party `mcp` SDK installed to actually run — this
# installer only copies config/knowledge/runtime-source files, it never
# installs Python packages into an arbitrary target environment's interpreter
# (that would be a real, risky side effect this script should not take
# silently). Without this notice, the first sign of the missing dependency is
# a generic, unhelpful "Connection closed" error from the MCP client days or
# weeks later, not an actionable message at install time.
# Only the three runtime directories this installer ships are searched (SEC-009), not whatever
# else sits under the target's implementation/runtime.
mcp_server_reqs=()
runtime_dirs=()
for runtime_name in memory security handoff; do
  if [[ -d "$TARGET/implementation/runtime/$runtime_name" ]]; then
    runtime_dirs+=("$TARGET/implementation/runtime/$runtime_name")
  fi
done
if [[ "${#runtime_dirs[@]}" -gt 0 ]]; then
  while IFS= read -r -d '' req_file; do
    mcp_server_reqs+=("$req_file")
  done < <(find "${runtime_dirs[@]}" -name "requirements-mcp-server.txt" -print0 2>/dev/null | sort -z)
fi

if [[ "${#mcp_server_reqs[@]}" -gt 0 ]]; then
  echo ""
  echo "Note: this install includes MCP server(s) that need one extra, one-time local"
  echo "dependency install before they will actually run (their config is generated"
  echo "either way, but the server process will fail with 'Connection closed' in your"
  # Paths are printed shell-quoted (%q): a copy-pasted line must not run a name in the path (SEC-009).
  printf 'assistant until this is done). Run from %q:\n' "$TARGET"
  for req_file in "${mcp_server_reqs[@]}"; do
    req_rel="${req_file#"$TARGET"/}"
    printf '  python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && pip install -r %q\n' "$req_rel"
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
  printf 'dependency install above, before it can answer real queries. Run from %q:\n' "$TARGET"
  echo "  python3 -m implementation.runtime.memory.build \\"
  echo "      --project-id <org>/<repo> --own-repo-root . --general-repo-root . \\"
  echo "      --output-dir implementation/runtime/memory/_index/<org-repo-slug>"
  echo "  (see implementation/runtime/memory/README.md for the full option reference,"
  echo "  including --shared-source-root for cross-repo shared-scope indexing, and match"
  echo "  --output-dir to the --index-dir already set in the generated mcp.json for this project)"
fi
