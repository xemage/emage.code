#!/usr/bin/env python3
"""expect.py for discover-skills-registry-grounded-recommendation.

Contract under test: implementation/knowledge/commands/discover-skills.md --
  step 1 "Read registry -- load implementation/registry/index.json",
  step 3 "Recommend skills -- return a ranked table: | Skill | Why | Mandatory? |",
  step 4 "Apply mandatory rules ... Implementation -> verification-before-completion before
  done claims",
  and the `## Output format` block's four headings.

The load-bearing assertion is step 1's: every skill the output names must resolve to a real
`category: skill` entry in the registry shipped in the fixture.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "## Recommended skills for:",
    "### Mandatory",
    "### Suggested",
    "### Next command",
)
TABLE_HEADER_RE = re.compile(r"^\|\s*Skill\s*\|\s*Why\s*\|\s*Mandatory\?\s*\|\s*$", re.MULTILINE)
SEPARATOR_ROW_RE = re.compile(r"^[\s|:-]+$")
MANDATORY_ON_IMPLEMENTATION = "verification-before-completion"


def _registry_skill_ids(registry_path: Path) -> set[str]:
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {
        entry["id"]
        for entry in data.get("entries", [])
        if isinstance(entry, dict) and entry.get("category") == "skill" and entry.get("id")
    }


def _cited_skill_names(text: str) -> list[str]:
    """First cell of every table row that is not a header or separator row."""
    names: list[str] = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if TABLE_HEADER_RE.match(stripped):
            in_table = True
            continue
        if not stripped.startswith("|"):
            in_table = False
            continue
        if not in_table or SEPARATOR_ROW_RE.match(stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and cells[0]:
            names.append(cells[0].strip("`").strip())
    return names


def _mandatory_section(text: str) -> str:
    start = text.find("### Mandatory")
    if start == -1:
        return ""
    nxt = text.find("### ", start + len("### Mandatory"))
    return text[start:] if nxt == -1 else text[start:nxt]


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    recommendation = fixture / "recommendation.md"
    registry = fixture / "implementation" / "registry" / "index.json"
    if not recommendation.is_file():
        return False
    text = recommendation.read_text(encoding="utf-8")

    if any(heading not in text for heading in REQUIRED_HEADINGS):
        return False
    if not TABLE_HEADER_RE.search(text):
        return False

    skill_ids = _registry_skill_ids(registry)
    if not skill_ids:
        return False  # registry unreadable or empty -- step 1 could not have been satisfied

    cited = _cited_skill_names(text)
    if not cited:
        return False  # an empty table is not a recommendation
    if any(name not in skill_ids for name in cited):
        return False

    return MANDATORY_ON_IMPLEMENTATION in _mandatory_section(text)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
