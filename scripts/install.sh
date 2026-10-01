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
  --target <dir>       Destination project root (created if missing). Not the emage.code
                       repository: its root accepts only --projections-only, and any
                       directory below its root is refused in every mode.
  --platform <name>    cursor | github | gemini | opencode | pi | claude-code | cline | all (default: all)
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

# The physical path of $1 -- every symlink on it resolved -- for a path that
# need not exist yet: its deepest existing ancestor is resolved with `cd -P`,
# and the components below that are appended as given.
physical_path() {
  local path="$1"
  local rest=""
  local parent
  while [[ ! -d "$path" ]]; do
    parent="$(dirname -- "$path")"
    if [[ "$parent" == "$path" ]]; then break; fi
    rest="/$(basename -- "$path")$rest"
    path="$parent"
  done
  printf '%s%s\n' "$(CDPATH='' cd -P -- "$path" && pwd -P)" "$rest"
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
#     --target implementation/.cursor under rsync copied .cursor into its own
#     subdirectory, several levels deep; --target implementation/new-dir
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
  list="$(mktemp)"
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
  local saved_shopt
  saved_shopt="$(shopt -p dotglob nullglob || true)"
  shopt -s dotglob nullglob
  local entries=("$src"/*)
  eval "$saved_shopt"
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
  local saved_shopt
  saved_shopt="$(shopt -p dotglob nullglob || true)"
  shopt -s dotglob nullglob
  local entries=("$1"/*)
  eval "$saved_shopt"
  [[ ${#entries[@]} -eq 0 ]]
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
  list="$(mktemp)"
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
  if same_tree "$src" "$dest"; then return 0; fi
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
  if same_tree "$src" "$dest"; then return 0; fi
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
    # Parallel arrays, one entry per kept path: backup_paths[i] is the relative
    # path, backup_dirs[i] the mktemp -d holding its saved copy.
    local backup_paths=()
    local backup_dirs=()
    local rel
    # -r here (not plain cp) so an excluded path may name either a file (the
    # original mcp.json/provenance use case) or a directory (a generated index
    # dir, .github/workflows/) without a separate code path.
    for rel in ${keep[@]+"${keep[@]}"}; do
      local backup_dir
      backup_dir="$(mktemp -d)"
      cp -r "$dest/$rel" "$backup_dir/payload"
      backup_paths+=("$rel")
      backup_dirs+=("$backup_dir")
    done
    run rm -rf "$dest"
    run mkdir -p "$dest"
    copy_contents_excluding -r "$src" "$dest" ${src_hits[@]+"${src_hits[@]}"}
    # `"${!arr[@]}"` on an empty array trips `set -u` on bash < 4.4, which the
    # no-rsync CI images are exactly the kind of host to ship — count first.
    local i
    for ((i = 0; i < ${#backup_paths[@]}; i++)); do
      rel="${backup_paths[$i]}"
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
# $3.. (optional, variadic): excluded names, with the meaning described under
# "Excluded paths" above. A path so named is never copied from source; dest's
# own is never touched here anyway, since nothing existing is overwritten.
merge_tree_preserve_existing() {
  local src="$1"
  local dest="$2"
  local excludes=("${@:3}")
  check_exclude_names ${excludes[@]+"${excludes[@]}"}
  if same_tree "$src" "$dest"; then return 0; fi
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    local rsync_args=(-a --ignore-existing)
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

# Names never shipped from $IMPLEMENTATION/docs, at any depth (T559). Python
# writes __pycache__/ beside any script it imports, and docs/tasks/ ships one
# (validate-tasks.py): an authoring checkout that has run it has a gitignored
# implementation/docs/tasks/__pycache__/, which every fresh install copied, with
# and without rsync. On --update, docs/tasks/ goes through merge_task_docs,
# which copies top-level files only; every other docs/ subdirectory honours
# these names too.
DOCS_EXCLUDES=(__pycache__)

install_docs() {
  refuse_in_projections_only install_docs "$TARGET/docs"
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
