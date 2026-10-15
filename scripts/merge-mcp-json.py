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

Two server-level denial lists are merged, not replaced (T658, SEC-T657-01), with or
without a provenance sidecar (the rule never reads one):
  - `excludeTools` (Gemini CLI, `mcpServers.<name>.excludeTools`): when both
    sides hold a list, the result is the union, the user's elements first in
    their order, then the generated elements the user's list lacks. A user's own
    entry is never dropped. An element the generator no longer ships stays until
    the user removes it (fail closed). A non-list user value is replaced.
  - top-level `permission` (Opencode): a user string shorthand (`"allow"`) is
    kept as `{"*": "allow"}`; the user's other keys are kept in their order; each
    generated key is set to the generated value and moved to the end, because
    Opencode applies the LAST matching rule, so the generated `deny` entries must
    come after any user wildcard such as `"playwright_*": "allow"` in the same
    file. A user's own `deny`, `ask` or `allow` for other keys is untouched.

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


def merge_exclude_tools(dest_value: Any, source_value: Any) -> Any:
    """Union of two `excludeTools` lists, dest elements first; anything else: source wins."""
    if not isinstance(dest_value, list) or not isinstance(source_value, list):
        return source_value
    union = list(dest_value)
    union += [item for item in source_value if item not in union]
    return union


def merge_permission(dest_value: Any, source_value: Any) -> Any:
    """Opencode top-level `permission`: keep the user's rules, put generated rules last."""
    if not isinstance(source_value, dict):
        return source_value
    if isinstance(dest_value, str):
        dest_value = {"*": dest_value}
    if not isinstance(dest_value, dict):
        return source_value
    merged = {key: value for key, value in dest_value.items() if key not in source_value}
    merged.update(source_value)
    return merged


def merge_json(dest: Any, source: Any, _top: bool = True) -> Any:
    """Recursively merge `source` into `dest`, per the module-level algorithm."""
    if not isinstance(dest, dict) or not isinstance(source, dict):
        return source

    merged: dict[str, Any] = dict(dest)
    for key, source_value in source.items():
        if key == "excludeTools" and key in merged:
            merged[key] = merge_exclude_tools(merged[key], source_value)
        elif key == "permission" and _top and key in merged:
            merged[key] = merge_permission(merged[key], source_value)
        elif key in merged and isinstance(merged[key], dict) and isinstance(source_value, dict):
            merged[key] = merge_json(merged[key], source_value, _top=False)
        else:
            merged[key] = source_value
    return merged


def prune_names_recursive(merged_node: Any, source_node: Any, names: set[str]) -> None:
    """Recursively prune `names` from `merged_node` wherever they are dest-only.

    Walks `merged_node`/`source_node` in parallel at every dict level (not
    only the top level), since every platform nests server names one level
    inside a per-format wrapper key (`servers`/`mcpServers`/`mcp`). A key is
    pruned at a given path only if it is present in `merged_node` at that
    path and absent from `source_node` at that same path.
    """
    if not isinstance(merged_node, dict):
        return

    source_dict = source_node if isinstance(source_node, dict) else {}

    for name in names:
        if name in merged_node and name not in source_dict:
            del merged_node[name]

    for key, value in list(merged_node.items()):
        if isinstance(value, dict):
            prune_names_recursive(value, source_dict.get(key), names)


def check_prune_names_recursive(merged_node: Any, source_node: Any, names: set[str], found: set[str]) -> None:
    """Check-only counterpart to `prune_names_recursive`.

    Populates `found` with every name in `names` that matches at least one
    path anywhere in `merged_node` where it would actually be pruned (present
    in `merged_node` at that path, absent from `source_node` at that same
    path). Performs no deletion.
    """
    if not isinstance(merged_node, dict):
        return

    source_dict = source_node if isinstance(source_node, dict) else {}

    for name in names:
        if name in merged_node and name not in source_dict:
            found.add(name)

    for key, value in merged_node.items():
        if isinstance(value, dict):
            check_prune_names_recursive(value, source_dict.get(key), names, found)


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
    parser.add_argument("--old-sidecar", type=Path, default=None,
                         help="Dest-side provenance sidecar (read before merge; missing = bootstrap)")
    parser.add_argument("--new-sidecar", type=Path, default=None,
                         help="Source-side provenance sidecar (must be paired with --old-sidecar)")
    parser.add_argument("--force-prune-keys", type=str, default=None,
                         help="Comma-separated dest-only key names to prune exactly once, explicitly")
    args = parser.parse_args()

    # SEC-001 (T636): never write through a symlink, whatever it points at. The
    # sidecar is written too, so it is held to the same rule.
    for written in (args.dest, args.old_sidecar):
        if written is not None and written.is_symlink():
            print(f"merge-mcp-json: refusing to write through a symlink: {written}", file=sys.stderr)
            return 1
    if not args.dest.is_file():
        print(f"merge-mcp-json: dest does not exist, nothing to merge: {args.dest}", file=sys.stderr)
        return 1
    if not args.source.is_file():
        print(f"merge-mcp-json: missing source file {args.source}", file=sys.stderr)
        return 1
    if bool(args.old_sidecar) != bool(args.new_sidecar):
        print("merge-mcp-json: --old-sidecar and --new-sidecar must be given together", file=sys.stderr)
        return 1

    dest_data = load_json(args.dest)
    source_data = load_json(args.source)
    merged = merge_json(dest_data, source_data)

    if args.old_sidecar and args.new_sidecar and args.old_sidecar.is_file():
        old_keys = set(load_json(args.old_sidecar).get("generatorOwnedKeys", []))
        new_keys = set(load_json(args.new_sidecar).get("generatorOwnedKeys", []))
        retired = old_keys - new_keys
        prune_names_recursive(merged, source_data, retired)

    if args.force_prune_keys:
        force_prune_names = {n.strip() for n in args.force_prune_keys.split(",") if n.strip()}

        found: set[str] = set()
        check_prune_names_recursive(merged, source_data, force_prune_names, found)
        missing = force_prune_names - found
        if missing:
            offenders = ", ".join(sorted(missing))
            print(f"merge-mcp-json: --force-prune-keys named '{offenders}', which is not a dest-only key "
                  f"(missing, or still present in source) — refusing to proceed", file=sys.stderr)
            return 1

        prune_names_recursive(merged, source_data, force_prune_names)

    rendered = render_json(merged)

    prefix = "DRY-RUN: " if args.dry_run else ""
    print(f"{prefix}merge {args.source} -> {args.dest}")
    if not args.dry_run:
        args.dest.write_text(rendered, encoding="utf-8")
        if args.new_sidecar and args.old_sidecar:
            args.old_sidecar.write_text(args.new_sidecar.read_text(encoding="utf-8"), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
