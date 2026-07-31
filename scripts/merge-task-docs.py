#!/usr/bin/env python3
"""Merge or seed docs/tasks/ ledgers and support files during install --update.

Ledger files (active-tasks.md, completed-tasks.md): refresh header/footer from
the template but keep existing task table rows.

All other files in the template directory (templates, the shipped validator
script, etc.): copy only when missing in dest. This applies regardless of
extension, so a pre-existing target that predates a new support file (e.g.
validate-tasks.py) still picks it up on the next --update.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

LEDGER_FILES = frozenset({"active-tasks.md", "completed-tasks.md"})
SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
TASK_ROW_RE = re.compile(r"^\|\s*T\d{3,}\s*\|")
EXAMPLE_ROW_RE = re.compile(r"_Example:")


def _extract_task_rows(text: str) -> list[str]:
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
    return rows


def _split_template(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    sep_idx = next((i for i, line in enumerate(lines) if SEPARATOR_RE.match(line)), None)
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


def merge_ledger(template_text: str, existing_text: str) -> str:
    preamble, postamble = _split_template(template_text)
    rows = _extract_task_rows(existing_text)
    parts = [*preamble, *rows]
    if postamble:
        if rows:
            parts.append("")
        parts.extend(postamble)
    return "\n".join(parts) + "\n"


def sync_task_docs(template_dir: Path, dest_dir: Path, dry_run: bool = False) -> list[str]:
    actions: list[str] = []
    dest_dir.mkdir(parents=True, exist_ok=True)

    for template_path in sorted(p for p in template_dir.iterdir() if p.is_file()):
        dest_path = dest_dir / template_path.name
        if template_path.name in LEDGER_FILES and dest_path.is_file():
            merged = merge_ledger(
                template_path.read_text(encoding="utf-8"),
                dest_path.read_text(encoding="utf-8"),
            )
            actions.append(f"merge ledger {dest_path}")
            if not dry_run:
                dest_path.write_text(merged, encoding="utf-8")
        elif not dest_path.exists():
            actions.append(f"seed {dest_path}")
            if not dry_run:
                shutil.copy2(template_path, dest_path)

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

    for action in sync_task_docs(args.template_dir, args.dest_dir, dry_run=args.dry_run):
        prefix = "DRY-RUN: " if args.dry_run else ""
        print(f"{prefix}{action}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
