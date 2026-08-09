# Task T377 — Extend installer merge-safety to 5 remaining platforms

**ID:** T377
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-09
**Based on:** docs/plans/plan-033-mcp-settings-hardening.md (P033-01)

This brief is self-contained. You do not need to read plan-033 or any other task brief to execute
this task.

## Objective
`scripts/install.sh --update` currently merge-preserves hand-added MCP-server content for only two
of seven platforms — `.vscode/mcp.json` (`github`) and `.mcp.json` (`claude-code`) — via
`merge_or_copy_mcp_json()`/`scripts/merge-mcp-json.py`, fixed in plan-031 (T368-T372). The other
five platforms' single-file MCP/settings configs — `.cursor/mcp.json`, `.gemini/settings.json`,
`.opencode/opencode.json`, `.pi/mcp.json`, `.cline/mcp.json` — live *inside* a directory tree that
`install_tree_into()`/`sync_tree_into()` fully replaces on `--update` (`rsync -a --delete`), so any
hand-added MCP server entry a user adds to one of those five files is silently destroyed on the next
`--update`, with no merge, no warning beyond a generic directory-level notice. Fix this by excluding
each of the five files from its platform's whole-tree `rsync --delete` replace and routing it through
the existing, already-generic `merge_or_copy_mcp_json()` helper instead — exactly the pattern
`install_github()`/`install_claude_code()` already use for the two files plan-031 fixed. This is a
wiring change only; no new merge algorithm is needed.

## Inputs (exact paths, verified against the current file — re-verify if anything below doesn't
match what you see; see Blocker protocol)
The ONLY file you will edit: `/home/emage/Code/emage/emage.code/scripts/install.sh`

Read-only references (do not edit):
- `/home/emage/Code/emage/emage.code/scripts/merge-mcp-json.py` — the existing, format-agnostic
  recursive JSON merge already used by `merge_or_copy_mcp_json()`. It has no hardcoded knowledge of
  `mcpServers` vs `servers` vs `mcp` as a top-level key name, so it works unmodified on all five
  target files. Do not modify this script; T377 is a `scripts/install.sh` wiring change only.
- `/home/emage/Code/emage/emage.code/implementation/platforms/*.json` — confirms each platform's
  `mcp.outputFile` is a path *relative to that platform's own output directory* (not a sibling
  `../` path like `github`/`claude-code`): `cursor.json` → `mcp.json`; `gemini.json` →
  `settings.json`; `opencode.json` → `opencode.json`; `pi.json` → `mcp.json`; `cline.json` →
  `mcp.json`. Each of these basenames is confirmed unique within its own platform's tree (no other
  file of that basename exists anywhere else under `implementation/.cursor/`, `.gemini/`,
  `.opencode/`, `.pi/`, `.cline/` respectively — verified via `find <dir> -name <basename>` during
  planning, each returned exactly one hit, the top-level file itself).

## Current exact code (quoted verbatim — this is what you are changing)

**1. `sync_tree_into()` — lines 106-121:**
```bash
# Replace dest with source, removing files that no longer exist upstream.
sync_tree_into() {
  local src="$1"
  local dest="$2"
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      run rsync -a --delete --dry-run "$src/" "$dest/"
    else
      run rsync -a --delete "$src/" "$dest/"
    fi
  else
    run rm -rf "$dest"
    run mkdir -p "$dest"
    run cp -r "$src/." "$dest/"
  fi
}
```

**2. `install_tree_into()` — lines 141-149:**
```bash
install_tree_into() {
  local src="$1"
  local dest="$2"
  if [[ "$UPDATE" -eq 1 ]]; then
    sync_tree_into "$src" "$dest"
  else
    copy_tree_into "$src" "$dest"
  fi
}
```

**3. `validate_before_update()` — lines 186-196:**
```bash
validate_before_update() {
  # Pre-flight checks before --update to prevent propagating corrupted state.
  if [[ "$UPDATE" -eq 1 ]]; then
    for d in .github .cursor .gemini .opencode .pi .claude; do
      if [[ -d "$TARGET/$d" ]]; then
        echo "warning: --update replaces $TARGET/$d entirely (rsync --delete). Local edits there will be lost." >&2
      fi
    done
    validate_github_agents
  fi
}
```

**4. The five target platform functions — lines 273-304 (note: `install_github` at lines 277-281
and `install_claude_code` at lines 295-299 are the already-correct reference pattern; do not modify
them):**
```bash
install_cursor() {
  install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor"
}

install_github() {
  install_tree_into "$IMPLEMENTATION/.github" "$TARGET/.github"
  run mkdir -p "$TARGET/.vscode"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.vscode/mcp.json" "$TARGET/.vscode/mcp.json"
}

install_gemini() {
  install_tree_into "$IMPLEMENTATION/.gemini" "$TARGET/.gemini"
}

install_opencode() {
  install_tree_into "$IMPLEMENTATION/.opencode" "$TARGET/.opencode"
}

install_pi() {
  install_tree_into "$IMPLEMENTATION/.pi" "$TARGET/.pi"
}

install_claude_code() {
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.mcp.json" "$TARGET/.mcp.json"
  run cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"
}

install_cline() {
  install_tree_into "$IMPLEMENTATION/.cline" "$TARGET/.cline"
  install_tree_into "$IMPLEMENTATION/.clinerules" "$TARGET/.clinerules"
}
```

`merge_or_copy_mcp_json()` itself (lines 221-233, already correct, read-only reference, do not
modify):
```bash
merge_or_copy_mcp_json() {
  local src="$1"
  local dest="$2"
  if [[ "$UPDATE" -eq 1 && -f "$dest" ]]; then
    local args=("$REPO_ROOT/scripts/merge-mcp-json.py" --source "$src" --dest "$dest")
    if [[ "$DRY_RUN" -eq 1 ]]; then
      args+=(--dry-run)
    fi
    run python3 "${args[@]}"
  else
    run cp "$src" "$dest"
  fi
}
```

## Allow-list (files/sections you may touch)
- `scripts/install.sh`, and within it ONLY:
  1. `sync_tree_into()` (lines 106-121)
  2. `install_tree_into()` (lines 141-149)
  3. `validate_before_update()` (lines 186-196)
  4. `install_cursor()`, `install_gemini()`, `install_opencode()`, `install_pi()`, `install_cline()`
     bodies (within the lines 273-304 range)
- Nothing else in this file, and no other file.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `install_github()` or `install_claude_code()` — already correct (plan-031), and their
  output must remain byte-for-byte identical before/after your change.
- Do NOT edit `merge_or_copy_mcp_json()`, `copy_tree_into()`, `merge_tree_preserve_existing()`,
  `install_docs()`, `install_agents_doc()`, `install_common()`, `require_existing_install()`,
  `validate_github_agents()`, the argument-parsing block, or the final `case "$PLATFORM"` dispatch
  block.
- Do NOT edit `scripts/merge-mcp-json.py` — confirmed already format-agnostic and correct as-is.
- Do NOT edit any test file — test coverage is a separate task, T378, blocked by this one.
- Do NOT edit any doc file (`README.md`, `CONTRIBUTING.md`, `AGENTS.md`) — separate tasks (T379,
  T380).
- Do NOT add `.cline` to the `for d in .github .cursor .gemini .opencode .pi .claude` loop in
  `validate_before_update()` — `.cline` was never in that loop to begin with (a separate,
  pre-existing gap unrelated to this bug); adding it is out of scope for this task.
- Do NOT create any new file.
- Do NOT run `node implementation/scripts/sync.mjs` without `--check` — omitting `--check` WRITES
  hundreds of files to disk. Only ever run it as
  `node implementation/scripts/sync.mjs --root implementation --check` (verify-only mode).
- Do NOT push to `develop` or `main`. Do NOT open a merge request. Do NOT merge anything. Stop after
  a local commit on your feature branch (see Git workflow below) — T378, T379, and T380 will stack
  further commits on the same branch, and T381 performs the push/MR/merge.

## Exact target implementation

**1. `sync_tree_into()` — add an optional third parameter, the relative path (within `dest`) of a
single file to exclude from the whole-tree replace. `rsync`'s own `--exclude=PATTERN` flag already
protects an excluded file from `--delete` by default (no `--delete-excluded` flag is passed, so this
is safe and requires no extra flag). The no-rsync fallback has no native exclude mechanism, so
preserve the excluded file manually across the `rm -rf`/`cp -r` replace:**
```bash
# Replace dest with source, removing files that no longer exist upstream.
# If $3 (a path relative to dest) is given, that one file is left untouched
# by this whole-tree replace — neither deleted nor overwritten — so a
# separate merge step (merge_or_copy_mcp_json) can update it afterward
# without losing any hand-added content it may hold.
sync_tree_into() {
  local src="$1"
  local dest="$2"
  local exclude_rel="${3:-}"
  if command -v rsync >/dev/null 2>&1; then
    run mkdir -p "$dest"
    local rsync_args=(-a --delete)
    if [[ -n "$exclude_rel" ]]; then
      rsync_args+=(--exclude="$exclude_rel")
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
      run rsync "${rsync_args[@]}" --dry-run "$src/" "$dest/"
    else
      run rsync "${rsync_args[@]}" "$src/" "$dest/"
    fi
  else
    local backup=""
    if [[ -n "$exclude_rel" && -f "$dest/$exclude_rel" ]]; then
      backup="$(mktemp)"
      cp "$dest/$exclude_rel" "$backup"
    fi
    run rm -rf "$dest"
    run mkdir -p "$dest"
    run cp -r "$src/." "$dest/"
    if [[ -n "$backup" ]]; then
      run mkdir -p "$(dirname "$dest/$exclude_rel")"
      run cp "$backup" "$dest/$exclude_rel"
      rm -f "$backup"
    fi
  fi
}
```

**2. `install_tree_into()` — thread the optional third parameter through:**
```bash
install_tree_into() {
  local src="$1"
  local dest="$2"
  local exclude_rel="${3:-}"
  if [[ "$UPDATE" -eq 1 ]]; then
    sync_tree_into "$src" "$dest" "$exclude_rel"
  else
    copy_tree_into "$src" "$dest"
  fi
}
```
Note: fresh installs (`copy_tree_into`) deliberately ignore `exclude_rel` — a fresh install has no
existing dest file to preserve, so it must remain a plain full-tree copy (AC #1).

**3. The five platform functions — exclude the MCP file from the tree copy, then merge it
separately, in that order (exclude-then-merge, matching `install_github`'s exclude-implicit /
merge-after-tree-copy structure exactly):**
```bash
install_cursor() {
  install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor" "mcp.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cursor/mcp.json" "$TARGET/.cursor/mcp.json"
}

install_gemini() {
  install_tree_into "$IMPLEMENTATION/.gemini" "$TARGET/.gemini" "settings.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.gemini/settings.json" "$TARGET/.gemini/settings.json"
}

install_opencode() {
  install_tree_into "$IMPLEMENTATION/.opencode" "$TARGET/.opencode" "opencode.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.opencode/opencode.json" "$TARGET/.opencode/opencode.json"
}

install_pi() {
  install_tree_into "$IMPLEMENTATION/.pi" "$TARGET/.pi" "mcp.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.pi/mcp.json" "$TARGET/.pi/mcp.json"
}

install_cline() {
  install_tree_into "$IMPLEMENTATION/.cline" "$TARGET/.cline" "mcp.json"
  install_tree_into "$IMPLEMENTATION/.clinerules" "$TARGET/.clinerules"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cline/mcp.json" "$TARGET/.cline/mcp.json"
}
```
Note on ordering and fresh-install correctness: on a fresh (non-`--update`) install,
`install_tree_into` calls `copy_tree_into`, which already copies the MCP file as part of the plain
full-tree copy; the subsequent `merge_or_copy_mcp_json` call then runs with `UPDATE=0`, so its own
`if [[ "$UPDATE" -eq 1 && -f "$dest" ]]` branch is false and it falls through to `cp "$src" "$dest"`
— a harmless, idempotent re-copy of the same file. This is the exact same (already-working) pattern
`install_github()`/`install_claude_code()` use today; do not "optimize" it away.

**4. `validate_before_update()` — required change (the current directory-level warning becomes
misleading for `.cursor`/`.gemini`/`.opencode`/`.pi`, whose one MCP file is no longer destroyed by
the tree replace; `.github`/`.claude` are unaffected by this since their MCP file already lived
*outside* the looped directory, so the existing wording stays accurate for them unchanged):**
```bash
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
```
This is a required change (not optional) — the current wording is objectively inaccurate for these
four directories after your fix lands, so leaving it unchanged would misinform users. Do not add a
`.cline` entry to the `for d in ...` list itself (see Deny-list).

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Syntax check:
   ```
   bash -n scripts/install.sh
   ```
   PASS = exits 0, no output.

2. Fresh (non-`--update`) install still a plain copy, for all five platforms (repeat per platform,
   `<plat>` ∈ `cursor gemini opencode pi cline`, `<file>` per the mapping above —
   `.cursor/mcp.json`, `.gemini/settings.json`, `.opencode/opencode.json`, `.pi/mcp.json`,
   `.cline/mcp.json`):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform cursor
   diff "$TMP/.cursor/mcp.json" implementation/.cursor/mcp.json
   ```
   PASS = empty diff, exit 0, for each of the five platforms with their respective file.

3. `--update` preserves an unknown hand-added key (repeat per platform; example shown for `cursor`,
   whose file shape is `{"mcpServers": {...}}` — for `gemini` add the synthetic key under
   `mcpServers` too but note `gemini`'s file also has a sibling non-MCP `hooks` key you must NOT
   touch or corrupt; for `opencode` the top-level MCP key is `mcp`, not `mcpServers`, and there are
   sibling non-MCP `$schema`/`instructions` keys):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform cursor
   python3 -c "
   import json
   p = '$TMP/.cursor/mcp.json'
   d = json.load(open(p))
   d['mcpServers']['my-custom-server'] = {'url': 'https://example.invalid/mcp'}
   json.dump(d, open(p, 'w'), indent=2)
   "
   bash scripts/install.sh --target "$TMP" --platform cursor --update
   python3 -c "
   import json
   d = json.load(open('$TMP/.cursor/mcp.json'))
   assert d['mcpServers'].get('my-custom-server') == {'url': 'https://example.invalid/mcp'}, d
   print('PASS: unknown key survived')
   "
   ```
   PASS = prints `PASS: unknown key survived` for all five platforms (adapting the top-level key
   name and any sibling-key check per platform as noted above).

4. `--update` refreshes a generator-known key (corrupt `context7` — present in every platform's MCP
   output since it is a `core`-tagged server — then confirm `--update` restores it to match the
   generated source, proving the merge actually refreshes rather than leaving dest untouched):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform cursor
   python3 -c "
   import json
   p = '$TMP/.cursor/mcp.json'
   d = json.load(open(p))
   d['mcpServers']['context7'] = {'url': 'https://stale.example.invalid/mcp'}
   json.dump(d, open(p, 'w'), indent=2)
   "
   bash scripts/install.sh --target "$TMP" --platform cursor --update
   python3 -c "
   import json
   updated = json.load(open('$TMP/.cursor/mcp.json'))['mcpServers']['context7']
   source = json.load(open('implementation/.cursor/mcp.json'))['mcpServers']['context7']
   assert updated == source, (updated, source)
   print('PASS: context7 refreshed')
   "
   ```
   PASS = prints `PASS: context7 refreshed` for all five platforms (adjust top-level key name per
   platform: `mcpServers` for cursor/gemini/pi/cline, `mcp` for opencode).

5. Non-MCP file elsewhere in the same tree is still correctly stale-cleaned (proves the exclude is
   scoped to exactly the one file, not the whole tree):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform cursor
   touch "$TMP/.cursor/stale-agent-that-should-be-deleted.md"
   bash scripts/install.sh --target "$TMP" --platform cursor --update
   test ! -f "$TMP/.cursor/stale-agent-that-should-be-deleted.md" && echo "PASS: stale file removed"
   ```
   PASS = prints `PASS: stale file removed`, for all five platforms.

6. `gemini`'s non-MCP `hooks` key and `opencode`'s non-MCP `$schema`/`instructions` keys survive
   `--update` unaffected:
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform gemini
   python3 -c "
   import json
   d = json.load(open('$TMP/.gemini/settings.json'))
   assert 'hooks' in d, d.keys()
   "
   bash scripts/install.sh --target "$TMP" --platform gemini --update
   python3 -c "
   import json
   before = json.load(open('implementation/.gemini/settings.json'))
   after = json.load(open('$TMP/.gemini/settings.json'))
   assert after.get('hooks') == before.get('hooks'), (after.get('hooks'), before.get('hooks'))
   print('PASS: gemini hooks key intact')
   "
   ```
   Repeat the equivalent check for `opencode`'s `$schema` and `instructions` keys against
   `implementation/.opencode/opencode.json`.

7. Full existing test suite baseline — capture your OWN current baseline before you start (do not
   assume a prior brief's stated count still holds; the suite has grown since T373-T376's "299
   tests" baseline as later plans have landed):
   ```
   python3 tests/run.py
   ```
   Run this once BEFORE your change to record the current pass/skip counts, and again AFTER your
   change. PASS = exits 0 both times, with the same or greater test count and no new failures.

## Acceptance criteria (all must be true)
- [ ] `git diff` shows changes in exactly one file: `scripts/install.sh`.
- [ ] Fresh (non-`--update`) install of each of the five platforms is still a byte-identical plain
      copy (test 2).
- [ ] `--update` install of each platform: a pre-existing unknown key survives (test 3); a
      generator-known key (`context7`) is refreshed to current generated content (test 4); a stale
      non-MCP file elsewhere in the same tree is still deleted (test 5).
- [ ] `gemini`'s `hooks` key and `opencode`'s `$schema`/`instructions` keys are unaffected by the
      merge (test 6).
- [ ] No literal secret value is ever written — the merge only moves JSON structure, never resolves
      `${env:VAR}`/`{env:VAR}` placeholders (this is inherent to `merge-mcp-json.py`, unchanged by
      this task; confirm no placeholder syntax was altered by eyeballing test 3/4 output).
- [ ] `validate_before_update()`'s warning text is updated per the exact target above.
- [ ] `bash -n scripts/install.sh` exits 0.
- [ ] `python3 tests/run.py` exits 0 both before and after your change, count not reduced.
- [ ] `install_github()` and `install_claude_code()` are byte-for-byte unchanged in the diff.

## Blocker protocol
STOP and report a blocker (do not improvise a different fix) if:
- The actual current `scripts/install.sh` content doesn't match the verbatim code quoted above
  (functions renamed, line numbers shifted materially, `merge_or_copy_mcp_json()` signature
  changed) → `type: dependency`, `severity: major` — re-verify against `develop`'s current tip
  before proceeding.
- `rsync`'s `--exclude` does not behave as documented in your test environment (excluded file still
  gets deleted, or the exclude pattern matches more than the single intended file) → `type:
  technical`, `severity: major` — do not silently fall back to a different exclusion mechanism
  without reporting this first; the `--exclude`-without-`--delete-excluded` behavior is a
  documented, stable `rsync` guarantee, but confirm your local `rsync` version's `man rsync` output
  agrees before assuming a discrepancy is a real bug versus a local environment issue.
- Any test in "Tests to run" fails after your change → `type: technical`, `severity: major`, include
  exact command output.
- You find a sixth file elsewhere in any of the five platform trees that also needs the same
  treatment (e.g. a second generated JSON settings file you weren't told about) → `type:
  unclear_requirements`, `severity: minor` — this task's scope is exactly the five named MCP/settings
  files; report the finding rather than silently expanding scope.

Max 2 retries before escalating to the orchestrator with full context (what was tried, exact
error/output).

## Git workflow
1. Create branch `bugfix/T377-install-mcp-merge-all-platforms` from the current tip of `develop`.
2. Make the change; run all tests above; confirm all pass.
3. Commit with a Conventional Commit message, e.g.:
   ```
   fix(install): extend MCP merge-safety to cursor/gemini/opencode/pi/cline

   scripts/install.sh --update only merge-preserved hand-added content for
   .vscode/mcp.json and .mcp.json (plan-031). The other five platforms'
   single-file MCP/settings configs lived inside a directory tree fully
   replaced by rsync --delete on --update, silently destroying any
   hand-added MCP server entry. Exclude each platform's one MCP file from
   its tree replace (sync_tree_into's new optional exclude parameter) and
   route it through the existing merge_or_copy_mcp_json() helper instead,
   mirroring the plan-031 pattern for the remaining five platforms.

   Refs T377
   ```
4. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit and report completion (branch name, commit SHA, full test output) back to the
   orchestrator. T378, T379, and T380 will check out this same branch and stack their own commits on
   top of it — do not delete or rename the branch.

## Constraints
- Token budget: ≤30k tokens.
- File ownership: `scripts/install.sh` only, scoped to the four functions/blocks named above.
- No unrelated refactor of this file or any other.
