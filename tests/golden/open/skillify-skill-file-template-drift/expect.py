#!/usr/bin/env python3
"""expect.py for skillify-skill-file-template-drift.

Contract under test: implementation/knowledge/commands/skillify.md, `### Generate the Skill
File` -- "After the 4-round interview, generate `.github/skills/<name>/SKILL.md` with this
structure:" followed by a template declaring `# <Skill Name>`, `## Trigger`, `## Inputs`,
`## Steps`, `## Success Criteria` and `## Examples`.

Expected to return False: a corpus survey of all 26 real SKILL.md files (both the
implementation/knowledge/skills/ sources and their .github/skills/ projections) found 0/26
satisfying this template. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = (
    "## Trigger",
    "## Inputs",
    "## Steps",
    "## Success Criteria",
    "## Examples",
)
TITLE_RE = re.compile(r"^#\s+\S.*$", re.MULTILINE)


def check(case_dir: Path) -> bool:
    skills_root = case_dir / "fixture" / ".github" / "skills"
    if not skills_root.is_dir():
        return False
    candidates = sorted(skills_root.glob("*/SKILL.md"))
    if len(candidates) != 1:
        return False
    text = candidates[0].read_text(encoding="utf-8")
    if not TITLE_RE.search(text):
        return False
    return all(section in text for section in REQUIRED_SECTIONS)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
