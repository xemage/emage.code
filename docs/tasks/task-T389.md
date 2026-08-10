# Task T389 — Design MCP merge provenance-tracking mechanism (ADR-002)

**ID:** T389
**Owner:** solution-architect
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-10
**Based on:** docs/plans/plan-034-mcp-provenance-tracking.md (P034-01)

This brief is self-contained. You do not need to read plan-034 or any other task brief to execute
this task — every finding, option, and constraint plan-034 established is restated in full below.

## Objective
This is a **design task, not an implementation task**. Produce
`docs/decisions/ADR-002-mcp-merge-provenance-tracking.md`, a concrete, implementable decision record
that resolves exactly how `scripts/merge-mcp-json.py`'s recursive JSON merge (used by
`scripts/install.sh --update` for all 7 platforms' MCP/settings files) will safely distinguish
"previously generator-owned, now retired from the source registry — prunable" from "hand-added by a
human — preserve forever." You do not write or modify any implementation code in this task —
`scripts/merge-mcp-json.py`, `implementation/scripts/sync.mjs`, and `scripts/install.sh` are
read-only reference material here (quoted in full below); T390 implements what you decide.

## Background — the problem, verified against the live repo (2026-08-10)

### The merge algorithm today (`scripts/merge-mcp-json.py`, current content, 82 lines, quoted in
full — read-only reference)
```python
#!/usr/bin/env python3
"""Merge a generated MCP JSON config into an existing target MCP JSON config.
...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def merge_json(dest: Any, source: Any) -> Any:
    """Recursively merge `source` into `dest`, per the module-level algorithm."""
    if not isinstance(dest, dict) or not isinstance(source, dict):
        return source

    merged: dict[str, Any] = dict(dest)
    for key, source_value in source.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(source_value, dict):
            merged[key] = merge_json(merged[key], source_value)
        else:
            merged[key] = source_value
    return merged


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_json(data: Any) -> str:
    return json.dumps(data, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Generated JSON file (wins on conflict)")
    parser.add_argument("--dest", type=Path, required=True, help="Existing target JSON file to merge into")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dest.is_file():
        print(f"merge-mcp-json: dest does not exist, nothing to merge: {args.dest}", file=sys.stderr)
        return 1
    if not args.source.is_file():
        print(f"merge-mcp-json: missing source file {args.source}", file=sys.stderr)
        return 1

    dest_data = load_json(args.dest)
    source_data = load_json(args.source)
    merged = merge_json(dest_data, source_data)
    rendered = render_json(merged)

    prefix = "DRY-RUN: " if args.dry_run else ""
    print(f"{prefix}merge {args.source} -> {args.dest}")
    if not args.dry_run:
        args.dest.write_text(rendered, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```
Its rule for a key present only in `dest` is: preserved as-is, unconditionally, no exceptions (see
`merge_json`'s `else: merged[key] = source_value` branch — note it only fires for keys **present in
`source`**; keys absent from `source` are never touched at all, so they survive via the initial
`merged: dict[str, Any] = dict(dest)` copy). There is no third input anywhere in the current call
graph that could carry "what did the generator emit last time." The hook point for a provenance-aware
pruning rule is exactly this "key only in `dest`" case: it must become "preserved, UNLESS confirmed
by independent evidence to have been previously generator-owned and now retired." Your design supplies
that independent evidence.

### What "generator-owned" means structurally (`implementation/scripts/sync.mjs`'s `emitMcp()`,
lines 293-379, quoted in full — read-only reference)
```javascript
function emitMcp(servers, tags, format) {
  const filtered = Object.fromEntries(
    Object.entries(servers).filter(([, s]) => (s.tags || []).some((t) => tags.includes(t)))
  );

  if (format === 'vscode' || format === 'cursor') {
    const out = { servers: format === 'vscode' ? {} : undefined, mcpServers: format === 'cursor' ? {} : undefined };
    const target = format === 'vscode' ? out.servers : out.mcpServers;
    for (const [name, s] of Object.entries(filtered)) {
      if (s.transport === 'remote') {
        target[name] = format === 'vscode' ? { type: 'http', url: s.url } : { url: s.url };
      } else {
        target[name] = { command: s.command, args: s.args || [] };
        if (s.env) target[name].env = mapEnv(s.env, '${env:VAR}');
      }
    }
    return JSON.stringify(format === 'vscode' ? { servers: target } : { mcpServers: target }, null, 2) + '\n';
  }
  // ... gemini / opencode / claude-code / cline branches, all structurally identical: iterate
  // `filtered` once, emit exactly one top-level output key per surviving `servers.yaml` entry name,
  // unmodified. No key-splitting, flattening, or renaming in any branch.
  throw new Error(`Unknown MCP format: ${format}`);
}
```
`filtered` (computed once, before any format branch) is the exact, format-independent set of
generator-owned top-level keys for that platform at that generation — this is your provenance source
of truth; you do not need per-format logic to compute it.

**Real hand-edit precedent (not hypothetical) confirming coarse per-key-name granularity is
sufficient:** this repo's own `.vscode/mcp.json` has exactly two hand-added elements — a `cwso` key
under `servers` (sibling to every generator-owned key, never present in `servers.yaml`, added whole as
its own top-level key) and a top-level `inputs` array (a key `emitMcp()`'s `vscode` branch never emits
at all). Neither is a hand-edited *field inside* a generator-owned entry — both are whole extra
top-level keys. Your design must never put either of these two keys at risk of pruning under any
input, including the one-time bridge flag (see below) when neither is named in its list.

### The 7 platforms' MCP output locations (`implementation/platforms/*.json`, confirmed by direct read
just now)
| Manifest | `outputDir` | `mcp.outputFile` | Resulting absolute file (inside `implementation/`) |
|---|---|---|---|
| `github.json` | `.github` | `../.vscode/mcp.json` | `implementation/.vscode/mcp.json` (escapes `.github/`) |
| `cursor.json` | `.cursor` | `mcp.json` | `implementation/.cursor/mcp.json` (inside `.cursor/`) |
| `gemini.json` | `.gemini` | `settings.json` | `implementation/.gemini/settings.json` (inside `.gemini/`) |
| `opencode.json` | `.opencode` | `opencode.json` | `implementation/.opencode/opencode.json` (inside `.opencode/`) |
| `pi.json` | `.pi` | `mcp.json` | `implementation/.pi/mcp.json` (inside `.pi/`) |
| `claude-code.json` | `.claude` | `../.mcp.json` | `implementation/.mcp.json` (escapes `.claude/`, repo-root-level) |
| `cline.json` | `.cline` | `mcp.json` | `implementation/.cline/mcp.json` (inside `.cline/`) |

Two files (`.vscode/mcp.json`, `.mcp.json`) live **outside** their platform's `outputDir` entirely —
they have no `.generated-manifest.json` sidecar today (that manifest is written per-`outRoot`, inside
`.github/`/`.claude/` respectively, never next to these two escaped files). The other five live
**inside** their `outputDir`, which `install.sh`'s `sync_tree_into()` fully replaces via
`rsync -a --delete` on every `--update`, except for one already-excluded file (the MCP file itself,
via the `exclude_rel` parameter T377 added — see below).

### `install.sh`'s current exact wiring (all quoted in full below — read-only reference; T390 will
edit these functions per your Decision, not you)

`sync_tree_into()` (current lines 110-140):
```bash
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
Note `exclude_rel` is currently a single string, passed to a single `--exclude=`. If your design needs
a second file (a sidecar) excluded alongside the MCP file itself, T390 must decide how to extend this
signature (e.g. an array, or a second parameter) — flag this explicitly as a required implementation
change in your Decision section rather than leaving it implicit.

`install_cursor()`/`install_gemini()`/`install_opencode()`/`install_pi()`/`install_cline()` (current,
the five tree-based platforms — pattern identical across all five, shown for `cursor`):
```bash
install_cursor() {
  install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor" "mcp.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cursor/mcp.json" "$TARGET/.cursor/mcp.json"
}
```

`install_github()`/`install_claude_code()` (current, the two standalone-file platforms):
```bash
install_github() {
  install_tree_into "$IMPLEMENTATION/.github" "$TARGET/.github"
  run mkdir -p "$TARGET/.vscode"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.vscode/mcp.json" "$TARGET/.vscode/mcp.json"
}

install_claude_code() {
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.mcp.json" "$TARGET/.mcp.json"
  run cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"
}
```
Note these two never call `install_tree_into` on the MCP file's own directory at all (`.vscode/` is
only ever touched via `mkdir -p` + `merge_or_copy_mcp_json`; `.mcp.json` sits at target root, entirely
outside any `install_tree_into` call) — so a sidecar file colocated with these two MCP files needs
**no** exclude-list wiring; it is structurally never at risk from `rsync --delete` regardless of your
design, since nothing ever whole-tree-replaces the directory it lives in.

`merge_or_copy_mcp_json()` (current lines 248-260):
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

### Reusable existing pattern found, and why it is NOT to be reused directly:
`sync.mjs`'s `syncPlatform()` already writes a `.generated-manifest.json` sidecar into every
platform's `outRoot` (current lines 524-535):
```javascript
  const manifestPath = path.join(outRoot, '.generated-manifest.json');
  const manifestContent = JSON.stringify(
    {
      generatedFrom: path.relative(ROOT, KNOWLEDGE) + '/',
      platform: manifest.platform,
      generatedAt: '<deterministic>',
      files: filesWritten.map((f) => toPosixPath(path.relative(outRoot, f))).sort(),
    },
    null,
    2
  ) + '\n';
  await emitFile(manifestPath, manifestContent);
```
Two independently-confirmed reasons this file must **not** be reused as this design's provenance
source:
1. **Ordering bug:** for the 5 tree-based platforms, `sync_tree_into()`'s `rsync -a --delete` runs
   BEFORE `merge_or_copy_mcp_json()`. `.generated-manifest.json` is not in the current `exclude_rel`
   list, so by the time any merge step could read it, it has already been overwritten with the *new*
   manifest — the "old" state needed for a diff is already gone. Reusing this file directly would
   require adding it to the exclude list too, but doing so would also change its own established,
   unrelated, already-tested purpose (file-path tracking) — safer to keep a dedicated file (see
   Decision requirement below).
2. **Path-vs-key mismatch:** `.generated-manifest.json`'s `files` array lists relative **file paths**
   written under `outRoot` (e.g. `mcp.json`, `agents/orchestrator.md`, …), not the **top-level JSON
   keys inside** the MCP file. It cannot answer "which servers did the generator emit last time"
   without also parsing the MCP file's own content, which defeats the purpose of a manifest.
3. It also doesn't exist at all for the two standalone-file platforms (`.vscode/mcp.json`,
   `.mcp.json`), since it's written per-`outRoot` and both files live outside their `outRoot`.

## Design options already evaluated (do not re-litigate from scratch — validate against these,
adjust only if you find a concrete flaw; if you deviate, your ADR's "Alternatives considered" section
must explain why)

**Option (a) — dedicated sidecar provenance manifest, diffed old-vs-new.** A new, separate-from-
`.generated-manifest.json` per-MCP-file sidecar recording the generator-owned top-level key set at
last generation. Safe on bootstrap (no old sidecar → no pruning), self-maintaining once seeded, but
cannot by itself solve the current `e2b`/`redis`/`figma`/`notion` bootstrap gap (no history exists
before this fix ships).

**Option (b) — in-file marker/comment convention. REJECTED, do not choose this.** Standard JSON has
no comment syntax. A sentinel data field (e.g. `"_meta": {...}`) pollutes the platform-native schema
every downstream tool (VS Code, Cursor, Gemini CLI, Opencode, Cline) parses directly, risking
validation warnings — a real, already-documented concern per `docs/wiki/mcp-servers.md`'s per-platform
runtime-verification checklist (added in T384). It also needs the identical diff logic as (a) anyway,
just relocated, with no architectural simplification. This option is closed; your ADR's "Alternatives
considered" table must still list it (for the record) with this exact rejection reasoning, but you are
not being asked to re-evaluate it.

**Option (c) — explicit, opt-in `--force-prune-keys <name1,name2,...>` flag.** Prunes exactly the
named dest-only keys, never inferred, never silent — a human-supplied, reviewed, one-time list. No
automatic mechanism for future retirements (weak as a *permanent, standalone* mechanism), but needs no
history, so it is the only option of the three that can close the pre-existing
`e2b`/`redis`/`figma`/`notion` bootstrap gap.

**Already-decided recommendation (yours to formalize, not re-derive): adopt (a) as the permanent
mechanism, plus (c) as a narrowly-scoped, one-time bootstrap bridge.** This is not open for
re-litigation in this task unless your investigation surfaces a concrete flaw in the combination
itself (not a restatement of trade-offs already listed above) — if you believe a different design is
required, you must document the specific new evidence in your ADR's Context section, not merely
prefer a different option on style grounds.

## A concrete strawman design to formalize (you MAY adjust field/flag names or minor mechanics, but
MUST preserve every safety property listed in "Non-negotiable properties" below; if you adjust
anything, your ADR's Decision section must state the final, exact form — not a range of options)

**Sidecar naming/location:** `<mcpfilename>.provenance.json`, always colocated in the exact same
directory as the MCP file it describes (never inside a different directory, never a single shared
file for multiple platforms). Concretely:
| MCP file | Sidecar file |
|---|---|
| `implementation/.cursor/mcp.json` | `implementation/.cursor/mcp.json.provenance.json` |
| `implementation/.gemini/settings.json` | `implementation/.gemini/settings.json.provenance.json` |
| `implementation/.opencode/opencode.json` | `implementation/.opencode/opencode.json.provenance.json` |
| `implementation/.pi/mcp.json` | `implementation/.pi/mcp.json.provenance.json` |
| `implementation/.cline/mcp.json` | `implementation/.cline/mcp.json.provenance.json` |
| `implementation/.vscode/mcp.json` | `implementation/.vscode/mcp.json.provenance.json` |
| `implementation/.mcp.json` | `implementation/.mcp.json.provenance.json` |

This convention makes the exclude-list problem trivial for the 5 tree-based platforms (both the MCP
file and its sidecar share a directory and a predictable name-plus-suffix relationship) and requires
**zero** new exclude wiring for the 2 standalone platforms (neither `.vscode/` nor repo-root `.mcp.json`
is ever whole-tree-replaced today, so nothing needs excluding there).

**Sidecar schema (schemaVersion 1):**
```json
{
  "schemaVersion": 1,
  "generatorOwnedKeys": ["gitlab", "playwright", "context7", "..."]
}
```
`generatorOwnedKeys` is exactly `Object.keys(filtered)` from `emitMcp()` (the format-independent,
pre-branch server-name set) — sorted, for deterministic, diff-friendly output (mirrors
`.generated-manifest.json`'s own `files.sort()` convention).

**`merge-mcp-json.py` CLI surface (additive, backward-compatible — no existing flag's behavior
changes):**
- `--old-sidecar <path>` (optional): the dest-side sidecar, read BEFORE merging. If the path doesn't
  exist on disk, treat as "no provenance history" (bootstrap case — see non-negotiable properties).
- `--new-sidecar <path>` (optional): the source-side sidecar (the freshly-generated one under
  `implementation/`), read for both the pruning diff and to refresh `--old-sidecar`'s path with the
  current generation's key set after a successful merge (seeding history for the *next* `--update`).
  Must be supplied together with `--old-sidecar` (both or neither) — error out if only one is given.
- `--force-prune-keys <comma-separated-names>` (optional, independent of the two sidecar flags —
  works with or without them present): prunes exactly the named keys from the merge result, if and
  only if each named key is present in `dest` and absent from `source` (i.e., genuinely dest-only).
  If a named key does NOT exist as a dest-only key (missing entirely, or still present in `source`),
  this is an **error** (non-zero exit, no partial write) — never a silent no-op, and never "prune it
  from source too."

**Pruning algorithm, applied after the existing `merge_json(dest, source)` produces `merged` (your ADR
must state this as the literal, unambiguous rule — this is the crux of the whole design):**
1. If `--old-sidecar`/`--new-sidecar` were both given and `--old-sidecar`'s file exists and parses:
   `retired = old_sidecar.generatorOwnedKeys − new_sidecar.generatorOwnedKeys` (set difference). For
   each `key` in `retired`: if `key` is present in `merged` AND `key` is absent from `source_data`
   (i.e., still genuinely dest-only after the ordinary merge — never delete a key `source` still
   emits), delete `key` from `merged`.
2. If `--old-sidecar` was given but its file does not exist (bootstrap case): step 1 is skipped
   entirely — zero keys pruned by the diff mechanism, unconditionally.
3. If `--force-prune-keys` was given: for each named key, if present in `merged` and absent from
   `source_data`, delete it from `merged`; else exit non-zero with an error identifying the exact
   key(s) that failed this check, before writing anything.
4. After all pruning: write `merged` to `--dest` (unchanged from today). If `--new-sidecar` was given
   (and not `--dry-run`), also write its exact content to `--old-sidecar`'s path, refreshing the dest
   sidecar for the next `--update` to diff against.

**`install.sh` wiring (T390 will implement; your ADR must confirm this shape or specify a corrected
one):**
- For the 5 tree-based platforms: extend `sync_tree_into()`'s exclude mechanism to also exclude the
  sidecar file (both the MCP file and `<mcpfile>.provenance.json` survive the `rsync --delete`
  replace); `merge_or_copy_mcp_json()` gains the two new `--old-sidecar`/`--new-sidecar` arguments,
  passed for these five; on fresh (non-`--update`) installs, the sidecar is plain-copied alongside the
  MCP file (mirrors the existing MCP-file fresh-install behavior).
- For the 2 standalone platforms: same `--old-sidecar`/`--new-sidecar` wiring, no exclude-list change
  needed (see above).

**One-time bootstrap bridge:** `--force-prune-keys` is invoked exactly once, explicitly, by
`docs/tasks/task-T382.md`'s Step 2 (already amended — see that brief), passing the literal string
`e2b,redis,figma,notion` — the same four names T386 already removed from `servers.yaml`. It is not a
standing default anywhere else in the codebase; document this explicitly as a documented, intentional,
narrow escape hatch, not a general "just pass whatever needs pruning" convention. Explicitly note in
your ADR's Decision section whether `--force-prune-keys` should remain a permanent CLI capability
after this bootstrap use, or be considered for future removal — this is an open question from
plan-034 you are expected to resolve, not defer further (a brief, reasoned "keep it, undocumented as
routine, for future one-off registry cleanups" is an acceptable resolution if you have no stronger
reason to remove it).

## Non-negotiable properties (your ADR's Decision must satisfy every one of these; state each as an
explicit, testable rule in the ADR text, not left implicit)
1. **Bootstrap-safe default:** when no old sidecar exists (every already-installed project, including
   this repo's own root, on the very first `--update` after this fix ships), the mechanism prunes
   **zero** dest-only keys — behavior is identical to today, no regression risk, no exceptions.
2. **Never infer a prune from absence alone:** a key is only ever pruned by the diff mechanism if it
   has **positive** historical evidence (present in an old sidecar's `generatorOwnedKeys`) AND is
   confirmed absent from the current source — never "unknown, so probably safe to remove."
3. **`--force-prune-keys` never prunes an unnamed key,** including `cwso` or `inputs` (the two real
   hand-added keys in this repo's own `.vscode/mcp.json`) — even when the flag is used with an
   unrelated list.
4. **A key `source` still emits is never pruned,** regardless of what any sidecar says — this is what
   prevents a currently-active server from ever being deleted by a stale-sidecar bug (test 3 in T391's
   scope will prove this directly).
5. **No literal secret value is ever written by any new code path** — this design only ever moves JSON
   structure and provenance metadata (server *names*, never values); placeholder syntax
   (`${env:VAR}`/`{env:VAR}`) is untouched by any part of this mechanism, matching the existing
   module-level guarantee in `merge-mcp-json.py`'s docstring.

## Allow-list (files you may create/edit)
- `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` — new file, this task's only output.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `scripts/merge-mcp-json.py`, `scripts/install.sh`, or
  `implementation/scripts/sync.mjs` — read-only reference material in this task; T390 implements.
- Do NOT edit `docs/plans/plan-034-mcp-provenance-tracking.md` — immutable per the Artifact
  Versioning convention (plans are not revised in place).
- Do NOT edit `docs/decisions/ADR-001-cwso-sia-integration.md` — read it only as a formatting
  reference if useful (this brief already gives you everything substantive you need).
- Do NOT edit any `docs/tasks/*.md` file, including `active-tasks.md` — task ledger changes are
  orchestrator-only.
- Do NOT create any file other than the one ADR named above.
- Do NOT push, open an MR, or merge — see Git workflow below.

## Confirm the ADR number before writing (do not assume)
```
ls docs/decisions/
```
As of this brief's authoring, only `ADR-001-cwso-sia-integration.md` and `_template.md` exist, making
`ADR-002` the next free sequential number. Re-run this command yourself before creating the file — if
an `ADR-002-*.md` already exists, STOP and report a blocker (see below) rather than silently picking
`ADR-003` or overwriting.

## ADR structure to follow (mirrors `docs/decisions/_template.md` and `ADR-001`'s established shape)
```markdown
# ADR-002 — <your concise decision title>

> Filename: `ADR-002-mcp-merge-provenance-tracking.md`

- **Status**: Accepted
- **Date**: 2026-08-10
- **Decider(s)**: solution-architect
- **Tasks**: T389 (this decision), T390 (implementation), T391 (tests), T392 (docs), T393 (gate)
- **Evidence**: docs/plans/plan-034-mcp-provenance-tracking.md; scripts/merge-mcp-json.py;
  implementation/scripts/sync.mjs `emitMcp()`/`syncPlatform()`; scripts/install.sh

## Context
<!-- restate the problem in your own words: the memoryless merge, the bootstrap gap, the real
     cwso/inputs precedent -->

## Decision
<!-- the exact, unambiguous, implementable design: sidecar file naming/location for all 7 platforms,
     exact JSON schema, exact merge-mcp-json.py CLI surface (both flags), exact pruning algorithm
     (steps 1-4 shape, or your corrected version), exact install.sh wiring shape, exact
     --force-prune-keys semantics including the error-on-missing-key behavior, and an explicit
     ruling on whether --force-prune-keys remains a permanent capability -->

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| (a) sidecar diff (chosen, permanent mechanism) | ... | ... | Chosen |
| (b) in-file marker/comment | ... | JSON has no comment syntax; sentinel field pollutes platform-native schemas | Rejected |
| (c) explicit --force-prune-keys only, no sidecar | ... | No automatic mechanism for future retirements | Chosen ONLY as one-time bootstrap bridge, not standalone |

## Consequences
- **Positive**: ...
- **Negative**: ...
- **Risks introduced**: ...
- **Follow-ups**: T390, T391, T392, T393

## Security constraints
<!-- restate non-negotiable property #5 (no literal secret ever written) explicitly -->

## Validation
<!-- how T391's tests will prove this decision correct: name the specific proof points -->
```

## Acceptance criteria (all must be true)
- [ ] `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` exists, following the structure above.
- [ ] Exact sidecar file name/path specified for all 7 platforms, including the two standalone files
      (`.vscode/mcp.json`, `.mcp.json`) that have no existing tree-level manifest.
- [ ] Exact sidecar JSON schema specified (at minimum: `generatorOwnedKeys`, the generator-owned key
      list at last generation).
- [ ] Exact exclude-list change specified so the sidecar's old (dest-side) content survives long
      enough to be read before being overwritten (Finding: the ordering nuance above), addressed
      explicitly, not silently.
- [ ] Exact `merge-mcp-json.py` CLI surface specified for both the diff-based pruning path
      (`--old-sidecar`/`--new-sidecar`) and the `--force-prune-keys` one-time bridge, including the
      exact pruning algorithm as an unambiguous, ordered rule.
- [ ] Explicit statement of the bootstrap-safe default (missing/absent old sidecar → preserve every
      dest-only key, no exceptions) as a testable, unambiguous rule (non-negotiable property #1).
- [ ] Design reviewed against the cwso/`inputs` real precedent — ADR text confirms neither is ever at
      risk under the new rule, including when `--force-prune-keys` is used with an unrelated list
      (non-negotiable property #3).
- [ ] `--force-prune-keys` behavior on a named key that is NOT actually dest-only is specified as an
      explicit error (non-zero exit, no partial write), not a silent no-op.
- [ ] An explicit ruling is given on whether `--force-prune-keys` remains a permanent CLI capability.
- [ ] "Alternatives considered" table includes option (b) with the exact rejection reasoning given
      above (JSON has no comment syntax; sentinel field pollutes platform-native schemas).
- [ ] "Security constraints" section restates non-negotiable property #5 (no literal secret ever
      written by any new code path).
- [ ] "Validation" section names the specific proof points T391 will need to test (mirrors the four
      proof classes plan-034 names: hand-added-key survival, retired-key pruning, bootstrap default,
      `--force-prune-keys` scoping).

## Blocker protocol
STOP and report a blocker (do not improvise a different resolution) if:
- `ls docs/decisions/` shows an `ADR-002-*.md` already exists → `type: dependency`, `severity:
  major` — do not overwrite it or silently pick a different number; report the actual current state.
- The actual current content of `scripts/merge-mcp-json.py`, `sync.mjs`'s `emitMcp()`/`syncPlatform()`,
  or `install.sh`'s quoted functions materially differs from what's quoted above (function renamed,
  logic changed in a way that invalidates a stated Finding) → `type: dependency`, `severity: major` —
  re-verify against the current file before writing the ADR; note the discrepancy in your report.
- You find a concrete, new flaw in the recommended (a)+(c) combination not already listed under
  "Design options already evaluated" → `type: technical`, `severity: minor` — document the specific
  new evidence in your ADR's Context section and propose a corrected design; do not silently choose a
  different option without this documentation.
- Any of the "Non-negotiable properties" cannot be satisfied by any design you can construct within
  this task's scope → `type: unclear_requirements`, `severity: major` — report which property and why
  before writing an ADR that fails to satisfy it.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Create branch `feature/T389-mcp-merge-provenance-tracking` from the current tip of `develop`.
2. Write `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` per the structure and acceptance
   criteria above.
3. Commit with a Conventional Commit message, e.g.:
   ```
   docs(decisions): add ADR-002 for MCP merge provenance tracking

   Designs the mechanism that lets scripts/install.sh --update safely
   distinguish previously generator-owned, now-retired MCP/settings keys
   (prunable) from hand-added keys like this repo's own .vscode/mcp.json
   cwso block (preserve forever). Adopts a dedicated per-file sidecar
   diffed old-vs-new as the permanent mechanism, plus a narrowly-scoped
   one-time --force-prune-keys bridge to close the pre-existing
   e2b/redis/figma/notion bootstrap gap for already-installed roots.

   Refs T389
   ```
4. Do NOT push. Do NOT open a merge request. Do NOT merge anything. Stop after the local commit and
   report completion (branch name, commit SHA) back to the orchestrator. T390 will check out this
   same branch and stack its implementation commit on top; T391 and T392 stack further; T393 performs
   the push/MR/merge.

## Constraints
- Token budget: ≤20k tokens.
- File ownership: `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` only.
- This is a design task — no code (Python, Bash, JavaScript, test) is written or modified in this
  task under any circumstance.
