#!/usr/bin/env python3
"""expect.py for discover-skills-registry-grounded-recommendation.

Contract under test: implementation/knowledge/commands/discover-skills.md --
  step 1 "Enumerate skills", a two-row rule on whether `implementation/registry/index.json`
  exists: present -> the authoring repository, whose skills are
  `implementation/knowledge/skills/*/SKILL.md`, with the registry's `category: skill` entries as
  an optional accelerator over that tree; absent -> an installed target, whose skills are
  `.<platform>/skills/*/SKILL.md`,
  step 3 "Recommend skills -- return a ranked table: | Skill | Why | Mandatory? |",
  step 4 "Apply mandatory rules ... Implementation -> verification-before-completion before
  done claims",
  and the `## Output format` block's four headings.

The load-bearing assertion is step 1's: every skill the output names must resolve to a skill that
step 1 actually enumerates -- in BOTH rows. The fixture carries one recommendation and two
repository roots: `fixture/` itself (the registry is present -> authoring row) and
`fixture/installed-target/` (no registry -> target row). The same recommendation must ground in
each, and each root must land in the row it is there to exercise.
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

# Step 1's discriminator, verbatim: the registry FILE, never `implementation/` -- install.sh
# creates `implementation/runtime/` in target projects, so testing the parent would invert the rule.
REGISTRY_REL = Path("implementation", "registry", "index.json")
KNOWLEDGE_SKILLS_REL = Path("implementation", "knowledge", "skills")
# The `outputDir` of each of the seven implementation/platforms/*.json manifests, every one of
# which declares `fileMap.skills` as `{"dir": "skills"}`. A fixed list, not a `.*` glob: a
# dot-directory that is not a platform projection is not a skills tree.
PLATFORM_DIRS = (".claude", ".cline", ".cursor", ".gemini", ".github", ".opencode", ".pi")
ROW_AUTHORING = "authoring"
ROW_TARGET = "target"
# Each fixture root and the row it exists to exercise.
ROOTS = ((Path("."), ROW_AUTHORING), (Path("installed-target"), ROW_TARGET))


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


def _tree_skill_names(skills_dir: Path) -> set[str]:
    """A skill is a directory holding a `SKILL.md` file -- nothing else counts."""
    if not skills_dir.is_dir():
        return set()
    return {child.name for child in skills_dir.iterdir() if (child / "SKILL.md").is_file()}


def _authoring_skills(root: Path) -> set[str]:
    """The tree is the enumeration; the registry is the accelerator step 1 permits reading
    instead. Where a root carries the tree, the tree decides -- step 1's "where the two disagree,
    the tree wins", so a stale registry can neither add a skill the tree lacks nor hide one it has;
    where a root carries only the registry, its `category: skill` entries stand in for the tree
    they index."""
    tree = root / KNOWLEDGE_SKILLS_REL
    if tree.is_dir():
        return _tree_skill_names(tree)
    return _registry_skill_ids(root / REGISTRY_REL)


def _target_skills(root: Path) -> set[str]:
    skills: set[str] = set()
    for platform_dir in PLATFORM_DIRS:
        skills |= _tree_skill_names(root / platform_dir / "skills")
    return skills


def enumerate_skills(root: Path) -> tuple[str, set[str]]:
    """Step 1, both rows: which row `root` is in, and the skills that row enumerates there."""
    if (root / REGISTRY_REL).exists():
        return ROW_AUTHORING, _authoring_skills(root)
    return ROW_TARGET, _target_skills(root)


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


def _grounded_in_every_row(fixture: Path, cited: list[str]) -> bool:
    for rel, expected_row in ROOTS:
        row, skills = enumerate_skills(fixture / rel)
        if row != expected_row:
            return False  # the fixture no longer exercises the row this root is for
        if not skills:
            return False  # nothing enumerated -- step 1 could not have been satisfied
        if any(name not in skills for name in cited):
            return False
    return True


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    recommendation = fixture / "recommendation.md"
    if not recommendation.is_file():
        return False
    text = recommendation.read_text(encoding="utf-8")

    if any(heading not in text for heading in REQUIRED_HEADINGS):
        return False
    if not TABLE_HEADER_RE.search(text):
        return False

    cited = _cited_skill_names(text)
    if not cited:
        return False  # an empty table is not a recommendation
    if not _grounded_in_every_row(fixture, cited):
        return False

    return MANDATORY_ON_IMPLEMENTATION in _mandatory_section(text)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
