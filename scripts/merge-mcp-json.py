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

Notes on stderr (T672, SEC-T658-05 c, SEC-007; one line each, key names only, never a value).
Exactly these are noted; every other generator-owned value (`command`, `args`, `url`, `type` ...)
is refreshed silently, because refreshing them is what an update is for:
  - a permission key of yours that the generator owns was replaced (the generated `deny`
    entries win over a user `allow`), or a user `hooks` value was replaced by the generated one;
  - a key of yours inside a generator-owned server's `env`, `environment` or `headers` was kept;
  - the top level of your file is not a JSON object, so the whole file was replaced;
  - there is no provenance sidecar, so no retired generator entry could be pruned: your servers
    that the generated config lacks are named, with a pointer to `--force-prune-keys`.

Writes are atomic (SEC-006): the merged file is written next to the destination and moved over
it with os.replace, so an interrupt leaves the old file or the new one, never a half-written
one. The provenance sidecar is replaced after the destination (a crash in between is repaired
by the next run, which prunes again from the older sidecar). `--validate-only` checks that the
destination (and its sidecar) parse as JSON and writes nothing; install.sh runs it before the
first write so a broken config is refused up front instead of after the platform tree was
replaced.

This script never reads or interpolates real environment variable values —
it only moves JSON data between the two files. Placeholder strings such as
`${env:VAR}` / `${input:...}` are left untouched.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

# The `env` / `headers` objects of a server entry: user-added keys inside them are kept, which is
# the documented merge design, but the user is told their names (SEC-007).
KEPT_KEY_PARENTS = frozenset({"env", "environment", "headers"})


def merge_exclude_tools(dest_value: Any, source_value: Any) -> Any:
    """Union of two `excludeTools` lists, dest elements first; anything else: source wins."""
    if not isinstance(dest_value, list) or not isinstance(source_value, list):
        return source_value
    union = list(dest_value)
    union += [item for item in source_value if item not in union]
    return union


def merge_permission(dest_value: Any, source_value: Any, notes: list[tuple[str, str]] | None = None) -> Any:
    """Opencode top-level `permission`: keep the user's rules, put generated rules last.

    A user rule for a generator-owned key with a different value is replaced; its key is
    appended to `notes` (SEC-T658-05 c)."""
    if not isinstance(source_value, dict):
        return source_value
    if isinstance(dest_value, str):
        dest_value = {"*": dest_value}
    if not isinstance(dest_value, dict):
        return source_value
    if notes is not None:
        notes.extend(
            ("replaced", f"permission.{key}") for key, value in source_value.items()
            if key in dest_value and dest_value[key] != value
        )
    merged = {key: value for key, value in dest_value.items() if key not in source_value}
    merged.update(source_value)
    return merged


def _note_kept_keys(path: tuple[str, ...], dest: dict, source: dict, notes: list[tuple[str, str]] | None) -> None:
    """SEC-007: a user key kept inside a generator-owned server's env/headers goes into `notes`."""
    if notes is None or not path or path[-1] not in KEPT_KEY_PARENTS or len(path) < 3:
        return
    notes.extend(("kept", f"{'.'.join(path)}.{key}") for key in dest if key not in source)


def merge_json(dest: Any, source: Any, _top: bool = True, notes: list[tuple[str, str]] | None = None,
               _path: tuple[str, ...] = ()) -> Any:
    """Recursively merge `source` into `dest`, per the module-level algorithm.

    `notes` (optional) collects (kind, name) pairs, kind "replaced" or "kept", for user content
    the merge replaced or kept in a generator-owned place; it never holds a value, only names."""
    if not isinstance(dest, dict) or not isinstance(source, dict):
        return source

    merged: dict[str, Any] = dict(dest)
    for key, source_value in source.items():
        if key == "excludeTools" and key in merged:
            merged[key] = merge_exclude_tools(merged[key], source_value)
        elif key == "permission" and _top and key in merged:
            merged[key] = merge_permission(merged[key], source_value, notes)
        elif key in merged and isinstance(merged[key], dict) and isinstance(source_value, dict):
            _note_kept_keys(_path + (key,), merged[key], source_value, notes)
            merged[key] = merge_json(merged[key], source_value, _top=False, notes=notes,
                                     _path=_path + (key,))
        else:
            if notes is not None and _path[:1] == ("hooks",) and key in merged and merged[key] != source_value:
                notes.append(("replaced", ".".join(_path + (key,))))
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


class InvalidJson(Exception):
    """A config file that cannot be read as JSON; the message names the file (one line)."""


def _reject_constant(name: str) -> Any:
    """json.load accepts NaN, Infinity and -Infinity by default; no config file may hold them."""
    raise ValueError(f"the constant {name} is not valid JSON")


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f, parse_constant=_reject_constant)
    # JSONDecodeError and UnicodeDecodeError are ValueErrors; a deeply nested file is a RecursionError
    except (ValueError, OSError, RecursionError) as exc:
        reason = " ".join(str(exc).split())
        raise InvalidJson(
            f"merge-mcp-json: {path} is not valid JSON ({reason}); nothing was written. "
            f"Fix or remove the file and re-run."
        ) from exc


def load_sidecar_keys(path: Path) -> set[str]:
    """The `generatorOwnedKeys` of a provenance sidecar; a sidecar of another shape is refused."""
    data = load_json(path)
    keys = data.get("generatorOwnedKeys", []) if isinstance(data, dict) else None
    if not isinstance(keys, list) or not all(isinstance(key, str) for key in keys):
        raise InvalidJson(
            f"merge-mcp-json: {path} is not a provenance sidecar (a JSON object whose "
            f"generatorOwnedKeys is a list of names); nothing was written. Fix or remove the file and re-run."
        )
    return set(keys)


def atomic_write_text(path: Path, text: str) -> None:
    """Write `text` to `path` through a random-named temp file in the same directory and os.replace.

    The temp file is created 0600 by mkstemp and given the mode of the file it replaces (0666 minus
    the umask for a new file) BEFORE any content is written, so the content is never readable by
    anyone who could not read the old file (SEC-T672-01). The temp file is removed on any failure."""
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def print_notes(dest: Path, notes: list[tuple[str, str]]) -> None:
    """One stderr line per kind: which user content was replaced / kept (names, never values)."""
    if ("top", "level") in notes:
        print(f"merge-mcp-json: note: {dest}: the top level of your file is not a JSON object, so the whole "
              f"file was replaced by the generated config", file=sys.stderr)
    for kind, text in (("replaced", "replaced your value for"), ("kept", "kept your key")):
        names = sorted({name for note_kind, name in notes if note_kind == kind})
        if names:
            print(f"merge-mcp-json: note: {dest}: {text} {', '.join(names)}", file=sys.stderr)


def render_json(data: Any) -> str:
    return json.dumps(data, indent=2) + "\n"


# The keys under which every platform lists its servers (`servers`, `mcpServers`, `mcp`).
SERVER_WRAPPERS = ("mcpServers", "servers", "mcp")


def dest_only_servers(dest_data: Any, source_data: Any) -> list[str]:
    """Names of the servers `dest_data` lists that the generated `source_data` does not (sorted)."""
    names: set[str] = set()
    if isinstance(dest_data, dict) and isinstance(source_data, dict):
        for wrapper in SERVER_WRAPPERS:
            dest_servers, source_servers = dest_data.get(wrapper), source_data.get(wrapper)
            if isinstance(dest_servers, dict) and isinstance(source_servers, dict):
                names.update(name for name in dest_servers if name not in source_servers)
    return sorted(names)


def main() -> int:
    """Run the merge; an I/O or recursion failure is one line, never a traceback (SEC-T672-07)."""
    try:
        return _main()
    except (OSError, RecursionError) as exc:
        reason = " ".join(f"{type(exc).__name__}: {exc}".split())
        print(f"merge-mcp-json: failed ({reason}); every file is either unchanged or fully replaced, "
              f"never partly written.", file=sys.stderr)
        return 1


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=None, help="Generated JSON file (wins on conflict)")
    parser.add_argument("--dest", type=Path, required=True, help="Existing target JSON file to merge into")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("--old-sidecar", type=Path, default=None,
                         help="Dest-side provenance sidecar (read before merge; missing = bootstrap)")
    parser.add_argument("--new-sidecar", type=Path, default=None,
                         help="Source-side provenance sidecar (must be paired with --old-sidecar)")
    parser.add_argument("--validate-only", action="store_true",
                         help="Only check that --dest (and --old-sidecar, if it exists) parse as JSON; write nothing")
    parser.add_argument("--force-prune-keys", type=str, default=None,
                         help="Comma-separated dest-only key names to prune exactly once, explicitly")
    args = parser.parse_args()

    if args.validate_only:
        return validate_only(args)
    if args.source is None:
        parser.error("--source is required unless --validate-only is given")

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

    notes: list[tuple[str, str]] = []
    try:
        dest_data = load_json(args.dest)
        source_data = load_json(args.source)
        if not isinstance(dest_data, dict):
            notes.append(("top", "level"))
        merged = merge_json(dest_data, source_data, notes=notes)
        use_sidecars = bool(args.old_sidecar and args.new_sidecar and args.old_sidecar.is_file())
        old_keys = load_sidecar_keys(args.old_sidecar) if use_sidecars else set()
        new_keys = load_sidecar_keys(args.new_sidecar) if use_sidecars else set()
    except InvalidJson as exc:
        print(exc, file=sys.stderr)
        return 1

    if use_sidecars:
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

    bootstrap_kept = (dest_only_servers(dest_data, source_data)
                      if args.old_sidecar and not args.old_sidecar.is_file() else [])

    prefix = "DRY-RUN: " if args.dry_run else ""
    print(f"{prefix}merge {args.source} -> {args.dest}")
    print_notes(args.dest, notes)
    if bootstrap_kept:
        print(f"merge-mcp-json: note: {args.dest}: there is no provenance sidecar at {args.old_sidecar}, so no "
              f"retired generator entry could be pruned; kept your server(s) {', '.join(bootstrap_kept)}, which "
              f"the generated config does not contain. If one is a retired generator entry, remove it by hand "
              f"or run scripts/merge-mcp-json.py with --force-prune-keys <name>.", file=sys.stderr)
    if not args.dry_run:
        # Sidecar text is read before the first write; destination first, sidecar second (SEC-006).
        sidecar_text = (args.new_sidecar.read_text(encoding="utf-8")
                        if args.new_sidecar and args.old_sidecar else None)
        atomic_write_text(args.dest, rendered)
        if sidecar_text is not None:
            atomic_write_text(args.old_sidecar, sidecar_text)

    return 0


def validate_only(args: argparse.Namespace) -> int:
    """--validate-only: exit 1 with one line naming the file when --dest or --old-sidecar is not JSON
    or cannot be replaced (file or directory not writable)."""
    try:
        load_json(args.dest)
        if args.old_sidecar is not None and args.old_sidecar.is_file():
            load_sidecar_keys(args.old_sidecar)
    except InvalidJson as exc:
        print(exc, file=sys.stderr)
        return 1
    # The merge replaces files through a temp file in their directory: it needs the directory and the
    # files to be writable. Better a one-line refusal now than a failure after the tree was replaced.
    for path in (args.dest, args.old_sidecar):
        if path is None or not path.exists():
            continue
        if not os.access(path, os.W_OK) or not os.access(path.parent, os.W_OK | os.X_OK):
            print(f"merge-mcp-json: {path} or its directory is not writable; nothing was written. "
                  f"Fix the permissions and re-run.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
