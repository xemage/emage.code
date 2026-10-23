#!/usr/bin/env python3
"""Merge or seed docs/tasks/ ledgers and support files during install --update.

Ledger files (active-tasks.md, completed-tasks.md) that already exist in dest:
normalise the task table's rows in place and leave every other line byte-for-byte
alone. The template contributes nothing to an existing ledger.

That last point is the T518 fix, and it is deliberate. A template's prose is
fresh-install guidance -- active-tasks.md's says "This ledger starts EMPTY [...]
The first real task is `T001`" -- while an existing ledger's prose is the
project's own record of what has happened. They are not two versions of the same
content, so there is no correct way to merge them; substituting the former for
the latter (which is what this script did until T518) does not just lose text, it
writes an assertion that is actively false into the one file a cold session reads
first and trusts literally. It was worst when the ledger was healthy: with zero
active rows there was nothing to preserve and the template won outright.

Ledger files missing from dest, and every other file in the template directory
(templates, the shipped validator script, etc.): copied from the template only
when absent. This applies regardless of extension, so a pre-existing target that
predates a new support file (e.g. validate-tasks.py) still picks it up on the
next --update, and a fresh install still gets the full template text.
"""
from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

LEDGER_FILES = frozenset({"active-tasks.md", "completed-tasks.md"})
SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
TASK_ROW_RE = re.compile(r"^\|\s*T\d{3,}\s*\|")
EXAMPLE_ROW_RE = re.compile(r"_Example:")
# The ledger's own header row: its first two cells are `ID` and `Title` (both ledgers).
HEADER_RE = re.compile(r"^\|\s*ID\s*\|\s*Title\s*\|")


def _separator_index(lines: list[str]) -> int | None:
    """Index of the separator line of the ledger's task table (T672, TL-T649-08).

    The table is the one whose header row is `| ID | Title | ...` (the separator is the line
    right after it), so a legend table before the ledger can no longer be taken for it. A text
    with no such header keeps the old meaning: its first markdown separator, or None."""
    for i, line in enumerate(lines[:-1]):
        if HEADER_RE.match(line.strip()) and SEPARATOR_RE.match(lines[i + 1].strip()):
            return i + 1
    return next((i for i, line in enumerate(lines) if SEPARATOR_RE.match(line.strip())), None)


def _extract_task_rows(text: str, dropped: list[str] | None = None) -> list[str]:
    rows: list[str] = []
    for line in text.splitlines():
        if TASK_ROW_RE.match(line) and not EXAMPLE_ROW_RE.search(line):
            rows.append(line)
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if SEPARATOR_RE.match(stripped):
            continue
        if EXAMPLE_ROW_RE.search(line):
            continue
        first_cell = stripped.split("|")[1].strip() if stripped.count("|") > 1 else ""
        if first_cell == "ID":
            continue
        print(
            f"warning: dropping non-conforming task row (ID must match T<NNN>): {line}",
            file=sys.stderr,
        )
        if dropped is not None:
            dropped.append(line)
    return rows


def _split_template(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    sep_idx = _separator_index(lines)
    if sep_idx is None:
        return lines, []

    preamble = lines[: sep_idx + 1]
    rest = lines[sep_idx + 1 :]
    post_start = 0
    for i, line in enumerate(rest):
        if TASK_ROW_RE.match(line):
            continue
        if not line.strip():
            post_start = i + 1
            continue
        post_start = i
        break
    else:
        post_start = len(rest)

    return preamble, rest[post_start:]


def _table_bounds(lines: list[str]) -> tuple[int, int] | None:
    """Locate the ledger's task table: (separator index, index past last row).

    The table is the one under the `| ID | Title |` header row (a legend table before it is
    not mistaken for it); with no such header, the first markdown separator. Returns None when
    the text has no markdown table separator at all, i.e. there is no table to splice rows into.
    """
    sep_idx = _separator_index(lines)
    if sep_idx is None:
        return None
    end = sep_idx + 1
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    return sep_idx, end


def _seed_from_template(template_text: str, rows: list[str]) -> str:
    preamble, postamble = _split_template(template_text)
    parts = [*preamble, *rows]
    if postamble:
        if rows:
            parts.append("")
        parts.extend(postamble)
    return "\n".join(parts) + "\n"


def merge_ledger(template_text: str, existing_text: str, dropped: list[str] | None = None) -> str:
    """Return the existing ledger with only its task rows normalised.

    Everything outside the task table -- title, intro, legends, orchestrator
    notes, footer -- is carried across untouched, because it is the project's
    content and not the template's. `template_text` is used only when the
    existing file has no table at all to splice into, which means there is
    nothing there worth preserving and the template is the best available
    scaffold. `dropped` (optional) receives each row that was dropped.
    """
    existing_lines = existing_text.splitlines()
    bounds = _table_bounds(existing_lines)
    if bounds is None:
        return _seed_from_template(template_text, _extract_task_rows(existing_text, dropped))

    sep_idx, rows_end = bounds
    rows = _extract_task_rows("\n".join(existing_lines[sep_idx + 1 : rows_end]), dropped)
    merged = [*existing_lines[: sep_idx + 1], *rows, *existing_lines[rows_end:]]
    return "\n".join(merged) + "\n"


class SymlinkRefused(Exception):
    """A destination is a symlink; writing would follow it (audit SEC-001, T636)."""


def _refuse_symlink(path: Path) -> None:
    if path.is_symlink():
        raise SymlinkRefused(f"refusing to write through a symlink: {path}")


def _atomic_write_bytes(path: Path, data: bytes, mode: int | None = None) -> None:
    """Write through a random-named temp file next to `path` and os.replace (SEC-006).

    mkstemp creates it 0600; it gets `mode` -- by default the mode of the file it replaces (0666 minus
    the umask for a new file) -- BEFORE any content is written, so no content is ever more readable than
    the old file was (SEC-T672-01). An interrupt leaves the old file or the new one; the temp file is
    removed on failure. os.replace swaps the name, so a symlink at `path` is replaced, never followed."""
    if mode is None:
        try:
            mode = stat.S_IMODE(path.stat().st_mode)
        except FileNotFoundError:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(data)
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def _atomic_write_text(path: Path, text: str) -> None:
    _atomic_write_bytes(path, text.encode("utf-8"))


def _backup_path(ledger: Path) -> Path:
    """`<ledger>.bak`, or `.bak.2`, `.bak.3` ... when one exists: an earlier backup is never overwritten."""
    candidate = ledger.with_name(ledger.name + ".bak")
    n = 2
    while candidate.exists() or candidate.is_symlink():
        candidate = ledger.with_name(f"{ledger.name}.bak.{n}")
        n += 1
    return candidate


def _preflight(dest_dir: Path, dry_run: bool) -> None:
    """Fail before the first write when the directory cannot be written (T682 N-8). The files are
    decoded by _plan_task_docs, which runs first (T684)."""
    if not dry_run and dest_dir.exists() and not os.access(dest_dir, os.W_OK | os.X_OK):
        raise PermissionError(f"{dest_dir} is not writable")


# One write of the apply phase: (destination, bytes, mode or None for "the mode of the file it replaces").
WriteOp = tuple[Path, bytes, "int | None"]


def _plan_task_docs(templates: list[Path], dest_dir: Path) -> tuple[list[str], list[WriteOp]]:
    """Everything that can fail short of a write, computed before the first write (T684, SEC-T682-06):
    every file is read and decoded (first, so an undecodable ledger fails before any merge prints a
    warning), every ledger merged, every backup name chosen. Returns the action lines and the writes,
    a backup always ahead of the ledger it protects."""
    actions: list[str] = []
    ops: list[WriteOp] = []
    texts: dict[Path, tuple[bytes, str, str]] = {}
    for template_path in templates:
        dest_path = dest_dir / template_path.name
        if template_path.name in LEDGER_FILES and dest_path.is_file():
            existing_bytes = dest_path.read_bytes()
            texts[template_path] = (existing_bytes, existing_bytes.decode("utf-8"), template_path.read_text(encoding="utf-8"))
    for template_path in templates:
        dest_path = dest_dir / template_path.name
        if template_path in texts:
            existing_bytes, existing_text, template_text = texts[template_path]
            dropped: list[str] = []
            merged = merge_ledger(template_text, existing_text, dropped)
            actions.append(f"merge ledger {dest_path}")
            if dropped:
                # Rows are only ever dropped with a copy of the ledger as it was (SEC-006).
                backup = _backup_path(dest_path)
                actions.append(f"back up {dest_path} to {backup} ({len(dropped)} row(s) dropped)")
                ops.append((backup, existing_bytes, stat.S_IMODE(dest_path.stat().st_mode) & ~0o022))
            ops.append((dest_path, merged.encode("utf-8"), None))
        elif not dest_path.exists():
            actions.append(f"seed {dest_path}")
            # The template's mode without group/world write: nothing seeded is group/world-writable (SEC-005).
            ops.append((dest_path, template_path.read_bytes(), stat.S_IMODE(template_path.stat().st_mode) & ~0o022))
    return actions, ops


def sync_task_docs(template_dir: Path, dest_dir: Path, dry_run: bool = False) -> list[str]:
    # Every destination is checked before the first write, so a symlinked
    # ledger or support file cannot leave earlier files already written.
    _refuse_symlink(dest_dir)
    templates = sorted(p for p in template_dir.iterdir() if p.is_file())
    for template_path in templates:
        _refuse_symlink(dest_dir / template_path.name)
        if template_path.name in LEDGER_FILES:
            _refuse_symlink(dest_dir / (template_path.name + ".bak"))
    _preflight(dest_dir, dry_run)
    actions, ops = _plan_task_docs(templates, dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not dry_run:
        # Each write is atomic: a file is as it was or fully replaced (backups, ledgers and seeds alike).
        for path, data, mode in ops:
            _atomic_write_bytes(path, data, mode)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-dir", type=Path, required=True)
    parser.add_argument("--dest-dir", type=Path, required=True)
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.template_dir.is_dir():
        print(f"merge-task-docs: missing template dir {args.template_dir}", file=sys.stderr)
        return 1

    try:
        actions = sync_task_docs(args.template_dir, args.dest_dir, dry_run=args.dry_run)
    except SymlinkRefused as exc:
        print(f"merge-task-docs: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError, RecursionError) as exc:
        # An unreadable or non-UTF-8 file, a failed write, a file that is too deeply nested: one line,
        # never a traceback (T682 N-8). Everything that can fail short of a write runs before the first
        # write (T684), and each write is atomic, so every file is as it was or fully replaced -- but a
        # write failing late can leave an earlier ledger replaced and a later one unchanged.
        reason = " ".join(f"{type(exc).__name__}: {exc}".split())
        print(f"merge-task-docs: failed ({reason}); each ledger is either unchanged or fully replaced.", file=sys.stderr)
        return 1
    for action in actions:
        prefix = "DRY-RUN: " if args.dry_run else ""
        print(f"{prefix}{action}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
