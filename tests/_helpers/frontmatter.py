"""YAML frontmatter parser shared by tests."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Raises ValueError if no frontmatter."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("no frontmatter found")
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict):
        raise ValueError(f"frontmatter is not a mapping: {type(fm).__name__}")
    return fm, text[m.end():]


def parse_file(path: Path) -> tuple[dict, str]:
    return parse(path.read_text(encoding="utf-8"))
