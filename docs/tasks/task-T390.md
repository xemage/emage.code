# Task T390 — Implement provenance sidecar + pruning + bootstrap bridge

**ID:** T390
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T389
**Created:** 2026-08-10
**Based on:** docs/plans/plan-034-mcp-provenance-tracking.md (P034-02)

This brief is self-contained for context, but its actual implementation content is governed by
`docs/decisions/ADR-002-mcp-merge-provenance-tracking.md`, which T389 must have already committed to
this task's branch before you start. **You MUST read ADR-002's "Decision" section in full and
implement exactly what it specifies.** Everything below that describes concrete code is a *reference
sketch* of the design ADR-002 was scaffolded to produce — if ADR-002's actual, committed Decision text
differs from this sketch in any specific (an exact flag name, an exact file-naming convention, an
exact pruning-algorithm step), **ADR-002's text governs, not this brief's sketch.** Do not silently
implement the sketch below if it conflicts with what ADR-002 actually says; if you find a conflict,
follow ADR-002 and note the deviation from this brief in your completion report (this is expected,
not a blocker, unless ADR-002 itself is internally ambiguous — see Blocker protocol).

## Objective
Implement ADR-002's provenance-tracking mechanism in the three confirmed hook-point files:
`implementation/scripts/sync.mjs` (emit the sidecar), `scripts/merge-mcp-json.py` (consume old+new
sidecars for diff-based pruning; accept the one-time bridge flag), and `scripts/install.sh` (wire the
sidecar into the exclude list and call sites).

## Step 0 — Read ADR-002 first, extract a conformance checklist
```
cat docs/decisions/ADR-002-mcp-merge-provenance-tracking.md
```
Before writing any code, write down (for your own use, not a deliverable) the exact answers ADR-002
gives to each of: (1) sidecar file naming/location for all 7 platforms, (2) sidecar JSON schema, (3)
`merge-mcp-json.py`'s exact new CLI flags and their exact names, (4) the exact pruning algorithm as an
ordered rule, (5) the exact `install.sh` exclude-list change, (6) the exact `--force-prune-keys`
error behavior on a non-dest-only named key, (7) whether `--force-prune-keys` is a permanent capability
or scoped for later removal (informational only — does not change what you implement now). Implement
against these seven answers, not against your own preferences or this brief's sketch, wherever they
differ.

## Inputs — exact current code (verbatim, verified fresh against the live repo just now; T389's branch
should not have touched any of these three files, since T389 is docs-only — re-verify this assumption
yourself with `git log` before proceeding; see Blocker protocol)

### 1. `scripts/merge-mcp-json.py` (current, full file, 83 lines)
```python
#!/usr/bin/env python3
"""Merge a generated MCP JSON config into an existing target MCP JSON config.

Used by `scripts/install.sh --update` for `.vscode/mcp.json` and `.mcp.json`,
which are single generated files (not directory trees) and therefore not
covered by `merge_tree_preserve_existing`/`sync_tree_into`. A plain overwrite
would silently drop any hand-added, non-generator content in the target file
(e.g. a locally-added MCP server entry or an `inputs` prompt block).

Merge algorithm (recursive, JSON-key-preserving):
  - Keys present in both `dest` and `source`, where both values are JSON
    objects: recurse.
  - Keys present in both, where at least one value is not an object (a
    scalar or array leaf, e.g. "url", "type", "args", "env"): `source` wins.
  - Keys present only in `dest`: preserved as-is.
  - Keys present only in `source`: added.

This script never reads or interpolates real environment variable values —
it only moves JSON data between the two files. Placeholder strings such as
`${env:VAR}` / `${input:...}` are left untouched.
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

### 2. `scripts/install.sh` — relevant current functions (verbatim)
`sync_tree_into()` (lines 110-140):
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
`install_tree_into()` (lines 160-169):
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
`merge_or_copy_mcp_json()` (lines 248-260):
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
The seven `install_<platform>()` functions (lines 300-336), unchanged shape for all seven, shown for
`cursor` and `claude_code` as the two structural variants:
```bash
install_cursor() {
  install_tree_into "$IMPLEMENTATION/.cursor" "$TARGET/.cursor" "mcp.json"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.cursor/mcp.json" "$TARGET/.cursor/mcp.json"
}

install_claude_code() {
  install_tree_into "$IMPLEMENTATION/.claude" "$TARGET/.claude"
  merge_or_copy_mcp_json "$IMPLEMENTATION/.mcp.json" "$TARGET/.mcp.json"
  run cp "$IMPLEMENTATION/CLAUDE.md" "$TARGET/CLAUDE.md"
}
```
(`install_github`, `install_gemini`, `install_opencode`, `install_pi`, `install_cline` follow the same
two shapes — tree-based five call `install_tree_into ... "<basename>"` then
`merge_or_copy_mcp_json`; the two standalone ones, `github`/`claude_code`, never pass an `exclude_rel`
to `install_tree_into` for the MCP file at all, since it lives outside that call's `dest`.)

### 3. `implementation/scripts/sync.mjs`'s `syncPlatform()` — the MCP-emission and manifest-writing
tail (current lines 504-538, verbatim; `emitMcp()` itself, lines 293-379, is read-only reference — do
not modify its per-format branches, only add sidecar-writing logic in `syncPlatform()`):
```javascript
  if (manifest.mcp) {
    const mcpResult = emitMcp(servers, manifest.mcp.tags, manifest.mcp.format);
    const outPath = path.resolve(outRoot, manifest.mcp.outputFile);
    if (manifest.mcp.format === 'opencode') {
      const cfg = { ...(manifest.mcp.extraFields || {}), mcp: mcpResult.__mcpObject };
      await emitFile(outPath, JSON.stringify(cfg, null, 2) + '\n');
    } else {
      await emitFile(outPath, mcpResult);
    }
    filesWritten.push(outPath);
  }

  for (const extra of manifest.extras || []) {
    const src = path.resolve(EXTRAS, extra.from.replace(/^_extras\//, ''));
    const dst = path.join(outRoot, extra.to);
    const content = await fs.readFile(src);
    await emitFile(dst, content);
    filesWritten.push(dst);
  }

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
Note `emitMcp()` computes `filtered` (the format-independent generator-owned server-name set) as its
very first statement, then discards that binding once it branches per-format — you will need either to
change `emitMcp()`'s return contract to also expose `filtered`'s keys, or to recompute the same filter
inline in `syncPlatform()` (identical one-line filter, cheap to duplicate: `Object.entries(servers)
.filter(([, s]) => (s.tags || []).some((t) => manifest.mcp.tags.includes(t)))`) — ADR-002 or your own
judgment decides which; prefer whichever keeps `emitMcp()`'s existing return type unchanged for the 5
already-passing call sites, since a return-shape change is a wider blast radius than necessary.

## Allow-list (files you may touch)
- `scripts/merge-mcp-json.py`
- `scripts/install.sh`
- `implementation/scripts/sync.mjs`
- Regenerated output under `implementation/` (the seven platform trees plus the two standalone files),
  but ONLY as a side effect of running the sanctioned `node implementation/scripts/sync.mjs --root
  implementation` regeneration command after your `sync.mjs` edit — never hand-edit any generated
  file directly.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` — read-only input, T389's
  scope, immutable once accepted per the Decision Log convention.
- Do NOT edit any test file (`tests/functional/test_install_script.py` or any other) — T391's scope,
  blocked by this task.
- Do NOT edit any doc file (`README.md`, `docs/wiki/mcp-servers.md`, either `AGENTS.md`) — T392's
  scope.
- Do NOT edit `implementation/knowledge/mcp/servers.yaml` — the registry content itself is unchanged
  by this task; you are only fixing the merge mechanism.
- Do NOT run `node implementation/scripts/sync.mjs` without `--root implementation` — wrong-root
  regeneration targets the wrong tree.
- Do NOT touch this repo's own root self-install mirror (`.cursor/`, `.gemini/`, `.mcp.json`, etc. at
  repo root, outside `implementation/`) — that is T382's later, separate scope.
- Do NOT push to `develop` or `main`. Do NOT open a merge request. Do NOT merge anything. Stop after a
  local commit on the branch T389 created (see Git workflow below) — T391 and T392 stack further
  commits on the same branch; T393 performs the push/MR/merge.

## Reference implementation sketch (consistent with ADR-002's anticipated Decision — governed by
ADR-002's actual text if it differs; see the warning at the top of this brief)

**`merge-mcp-json.py` additive CLI surface:**
```python
parser.add_argument("--old-sidecar", type=Path, default=None,
                     help="Dest-side provenance sidecar (read before merge; missing = bootstrap)")
parser.add_argument("--new-sidecar", type=Path, default=None,
                     help="Source-side provenance sidecar (must be paired with --old-sidecar)")
parser.add_argument("--force-prune-keys", type=str, default=None,
                     help="Comma-separated dest-only key names to prune exactly once, explicitly")
```
Pruning logic runs AFTER `merged = merge_json(dest_data, source_data)`, BEFORE `render_json(merged)`:
```python
if bool(args.old_sidecar) != bool(args.new_sidecar):
    print("merge-mcp-json: --old-sidecar and --new-sidecar must be given together", file=sys.stderr)
    return 1

if args.old_sidecar and args.new_sidecar and args.old_sidecar.is_file():
    old_keys = set(load_json(args.old_sidecar).get("generatorOwnedKeys", []))
    new_keys = set(load_json(args.new_sidecar).get("generatorOwnedKeys", []))
    for key in old_keys - new_keys:
        if key in merged and key not in source_data:
            del merged[key]

if args.force_prune_keys:
    for name in [n.strip() for n in args.force_prune_keys.split(",") if n.strip()]:
        if name in merged and name not in source_data:
            del merged[name]
        else:
            print(f"merge-mcp-json: --force-prune-keys named '{name}', which is not a dest-only key "
                  f"(missing, or still present in source) — refusing to proceed", file=sys.stderr)
            return 1
```
After a successful (non-dry-run) write of `merged` to `--dest`, also refresh the dest sidecar:
```python
if args.new_sidecar and args.old_sidecar and not args.dry_run:
    args.old_sidecar.write_text(args.new_sidecar.read_text(encoding="utf-8"), encoding="utf-8")
```

**`sync.mjs` sidecar emission**, added immediately after the existing `manifest.mcp` block in
`syncPlatform()` (same `if (manifest.mcp) { ... }` guard, sidecar path = MCP `outPath` with
`.provenance.json` appended to its basename):
```javascript
if (manifest.mcp) {
    // ... existing emitMcp()/outPath/filesWritten.push(outPath) block, unchanged ...
    const filteredKeys = Object.entries(servers)
      .filter(([, s]) => (s.tags || []).some((t) => manifest.mcp.tags.includes(t)))
      .map(([name]) => name)
      .sort();
    const sidecarPath = outPath + '.provenance.json';
    const sidecarContent = JSON.stringify({ schemaVersion: 1, generatorOwnedKeys: filteredKeys }, null, 2) + '\n';
    await emitFile(sidecarPath, sidecarContent);
    filesWritten.push(sidecarPath);
}
```

**`install.sh` wiring:**
- `sync_tree_into()`/`install_tree_into()`: extend to exclude both the MCP file and its sidecar for
  the 5 tree-based platforms — e.g. change `exclude_rel` from a single string to accept a
  space-separated or array-form set of two relative paths, adding a second `--exclude=` to
  `rsync_args` and a second backup/restore pass in the no-rsync fallback branch.
- `merge_or_copy_mcp_json()`: extend to accept the sidecar source/dest pair, pass
  `--old-sidecar`/`--new-sidecar` to `merge-mcp-json.py` when both exist as expected, and plain-`cp`
  the sidecar alongside the MCP file on fresh installs / when `UPDATE=0` (mirrors the existing MCP-file
  fresh-install fallback exactly).
- All seven `install_<platform>()` functions: pass the sidecar path pair through to the extended
  `merge_or_copy_mcp_json()` call.

## Step 1 — Implement per ADR-002 (using the sketch above only where ADR-002's text matches it)
Edit the three files. Run the regeneration command from repo root:
```
node implementation/scripts/sync.mjs --root implementation
git status --short
```
Confirm only files under `implementation/` (plus your three edited source files) changed.

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Syntax/lint checks:
   ```
   bash -n scripts/install.sh
   python3 -c "import ast; ast.parse(open('scripts/merge-mcp-json.py').read())"
   node --check implementation/scripts/sync.mjs
   ```
   PASS = all three exit 0, no output.

2. Drift check — regenerated `implementation/` trees match a fresh regeneration exactly (same check
   `.gitlab-ci.yml`'s `sync-no-diff` job runs, and the same check `make verify` runs):
   ```
   node implementation/scripts/sync.mjs --root implementation
   git diff --quiet -- implementation/ && echo "PASS: no post-regen drift"
   make verify
   ```
   PASS = `PASS: no post-regen drift` printed, `make verify` drift-free, both exit 0.

3. Bootstrap default — a fresh temp-dir install then a first `--update` with no prior sidecar
   preserves every dest-only key (proves non-negotiable property #1 end-to-end, using the real
   `install.sh`, not a unit test):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform cursor
   rm -f "$TMP"/.cursor/mcp.json.provenance.json   # simulate "no prior sidecar" bootstrap case even
                                                     # though a fresh install writes one — this proves
                                                     # the --old-sidecar-missing code path specifically
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
   print('PASS: bootstrap default preserved unknown key with no prior sidecar')
   "
   ```

4. Diff-based pruning — a synthetic retired-key scenario across two real `--update` runs (seeds a
   sidecar, then simulates a server retirement, then confirms pruning):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform cursor
   # simulate a server that WAS generator-owned (present in the seeded sidecar) but is dest-only now:
   python3 -c "
   import json
   p = '$TMP/.cursor/mcp.json'
   d = json.load(open(p)); d['mcpServers']['retiring-server'] = {'url': 'https://retiring.invalid/mcp'}
   json.dump(d, open(p, 'w'), indent=2)
   sp = '$TMP/.cursor/mcp.json.provenance.json'
   sc = json.load(open(sp)); sc['generatorOwnedKeys'] = sorted(set(sc['generatorOwnedKeys']) | {'retiring-server'})
   json.dump(sc, open(sp, 'w'), indent=2)
   "
   bash scripts/install.sh --target "$TMP" --platform cursor --update
   python3 -c "
   import json
   d = json.load(open('$TMP/.cursor/mcp.json'))
   assert 'retiring-server' not in d['mcpServers'], 'retiring-server should have been pruned'
   print('PASS: retired generator-owned key pruned once provenance existed')
   "
   ```

5. `--force-prune-keys` scoping — prunes only the named key(s), never `cwso`-style unrelated keys, and
   errors on a key that isn't actually dest-only (adapt exact CLI flag name/shape to ADR-002's final
   text if it differs from the sketch):
   ```
   TMP=$(mktemp -d)
   bash scripts/install.sh --target "$TMP" --platform github
   python3 -c "
   import json
   p = '$TMP/.vscode/mcp.json'
   d = json.load(open(p))
   d['servers']['cwso'] = {'url': 'http://127.0.0.1:8080/mcp'}
   d['servers']['to-be-force-pruned'] = {'url': 'https://retiring.invalid/mcp'}
   json.dump(d, open(p, 'w'), indent=2)
   "
   python3 scripts/merge-mcp-json.py --source implementation/.vscode/mcp.json --dest "$TMP/.vscode/mcp.json" --force-prune-keys to-be-force-pruned
   python3 -c "
   import json
   d = json.load(open('$TMP/.vscode/mcp.json'))
   assert 'to-be-force-pruned' not in d['servers'], d['servers'].keys()
   assert d['servers'].get('cwso') == {'url': 'http://127.0.0.1:8080/mcp'}, 'cwso must survive untouched'
   print('PASS: force-prune-keys pruned only the named key, cwso survived')
   "
   # error case: naming a key that is NOT dest-only (context7 is generator-owned, present in source)
   python3 scripts/merge-mcp-json.py --source implementation/.vscode/mcp.json --dest "$TMP/.vscode/mcp.json" --force-prune-keys context7; echo "exit=$?"
   ```
   PASS = both `PASS:` lines print; the final command's `exit=` is non-zero (not `0`) and no partial
   write occurred (re-read the dest file and confirm `context7` is still present, unchanged).

6. Full existing test suite baseline — capture your OWN current baseline before you start (do not
   assume a prior brief's stated count still holds):
   ```
   python3 tests/run.py
   ```
   Run once BEFORE your change, once AFTER. PASS = exits 0 both times, same or greater count, no new
   failures (T391 has not yet added its own tests on top of yours at this point — that's expected).

## Acceptance criteria (all must be true)
- [ ] Implementation conforms to ADR-002's Decision section — for every point where this brief's
      reference sketch differs from ADR-002's actual committed text, ADR-002's text was followed, and
      the deviation is noted in your completion report.
- [ ] Fresh (non-`--update`) installs unaffected — still a plain copy of the MCP file, sidecar written
      alongside it as a plain copy too.
- [ ] `--update` with no old sidecar present preserves every dest-only key exactly as today (test 3;
      bootstrap default, no regression).
- [ ] `--update` with an old sidecar present prunes a dest-only key only if it was in the old
      sidecar's generator-owned set and is absent from the new source's current key set (test 4).
- [ ] The force-prune flag prunes only the exact named keys, never inferred names, and errors (exit
      non-zero, no partial write) if a named key doesn't actually exist as a dest-only key (test 5).
- [ ] cwso-style keys (never in any sidecar) are never pruned under any code path, including the
      force-prune flag when cwso isn't named (test 5).
- [ ] No literal secret value is ever written by any new code path (inspect test 3/4/5 output by eye —
      only placeholder syntax, e.g. `${env:VAR}`, ever appears; no resolved credential).
- [ ] `git diff` (this task's own commit) touches exactly `scripts/merge-mcp-json.py`,
      `scripts/install.sh`, `implementation/scripts/sync.mjs`, plus regenerated files under
      `implementation/` produced only by the sanctioned regeneration command.
- [ ] Tests 1, 2, 3, 4, 5 all pass exactly as specified (or as adapted for ADR-002's final exact CLI
      surface, if it differs from the sketch — note any adaptation in your report).
- [ ] `python3 tests/run.py` exits 0 both before and after your change, count not reduced.

## Blocker protocol
STOP and report a blocker (do not improvise a different design) if:
- `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md` does not exist on your branch, or its
  "Decision" section is internally ambiguous / self-contradictory / missing one of the 7 conformance
  points listed in Step 0 → `type: dependency`, `severity: critical` — this task cannot proceed
  without an unambiguous decision to implement against; do not fill the gap with your own invented
  design.
- The actual current content of `scripts/merge-mcp-json.py`, `scripts/install.sh`'s quoted functions,
  or `sync.mjs`'s quoted `syncPlatform()` tail materially differs from what's quoted above (renamed,
  restructured in a way that invalidates ADR-002's assumptions) → `type: dependency`, `severity:
  major` — re-verify against the current file; note the discrepancy; if ADR-002's design is no longer
  implementable as written because of this drift, escalate rather than silently reinterpreting it.
- Any test in "Tests to run" fails after your change → `type: technical`, `severity: major`, include
  exact command output.
- `emitMcp()`'s five per-format branches would need to change to expose `filtered`'s keys in a way
  that risks altering their existing, already-tested output shape → `type: technical`, `severity:
  minor` — prefer the "recompute the filter inline in `syncPlatform()`" approach from the reference
  sketch to avoid this risk; report if ADR-002 specifically requires touching `emitMcp()`'s return
  contract anyway.

Max 2 retries before escalating to the orchestrator with full context (what was tried, exact
error/output, and which of ADR-002 vs. this brief's sketch you were following at the point of
failure).

## Git workflow
1. Check out the EXISTING branch `feature/T389-mcp-merge-provenance-tracking` (created by T389 — do
   NOT create a new branch, do NOT branch from `develop`).
2. Confirm T389's ADR-002 commit is present (`git log --oneline -3` should show it).
3. Make the change (Step 0-1); run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   feat(mcp): implement provenance sidecar + diff-based pruning + bootstrap bridge

   Implements ADR-002: sync.mjs now writes a <mcpfile>.provenance.json
   sidecar recording the generator-owned server-key set alongside every
   platform's MCP/settings output. merge-mcp-json.py consumes the old
   (dest-side) and new (source-side) sidecars to safely prune a dest-only
   key that was previously generator-owned and is now retired, defaulting
   to zero pruning whenever no prior sidecar exists (bootstrap-safe).
   install.sh wires the sidecar into the same exclude-then-merge treatment
   already applied to each platform's MCP file. Adds a one-time, explicit
   --force-prune-keys bridge for names with no sidecar history, used only
   by T382's already-reviewed e2b/redis/figma/notion bootstrap case.

   Refs T390
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of T389's ADR commit, same branch) and report completion (commit SHA,
   full test output, any noted deviation from this brief's sketch) back to the orchestrator. T391 and
   T392 will stack further commits on this same branch; T393 pushes it and opens the MR.

## Constraints
- Token budget: ≤35k tokens.
- File ownership: `scripts/merge-mcp-json.py`, `scripts/install.sh`,
  `implementation/scripts/sync.mjs`, plus sanctioned-regeneration output under `implementation/`.
- No unrelated refactor of any of the three files.
