#!/usr/bin/env python3
"""expect.py for skillify-skill-file-template-drift.

Contract under test: implementation/knowledge/commands/skillify.md, `### Generate the Skill
File` -- "After the 4-round interview, generate the `SKILL.md` at the path chosen above, with
this structure." followed by a template declaring `# <Skill Name>`, `## When to Use`, `## Inputs`,
`## Procedure`, `## Success Criteria` and `## Examples`.

"The path chosen above" is `### Choose the Output Path`, amended at `T532` from a single
hardcoded `.github/skills/<name>/SKILL.md` to one rule with a precondition -- "exactly one row
applies to any given project, decided by whether `implementation/knowledge/skills/` exists":

  | `implementation/knowledge/skills/` -- an emage.code authoring checkout
    -> `implementation/knowledge/skills/<name>/SKILL.md`
  | no `implementation/knowledge/` -- an installed target project
    -> `<platform>/skills/<name>/SKILL.md` in every installed platform folder that exists:
       `.github/`, `.claude/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/`

The fixture exercises the **installed-target row**: it has no `implementation/knowledge/`, and
`.github/` is the only platform folder in it, so "every installed platform folder that exists" is
that one folder (`skillify-output-path-resolution-v1.md` SS4.4, property 3).

Fixture discovery takes option (i) of `skillify-output-path-resolution-v1.md` SS7: search the
whole declared set -- the authoring row's source directory and all seven platform `skills/`
directories. The rule, as revised under orchestrator review of `T548`:

  - at least one declared directory exists (the `is_dir()` guard);
  - **at most one** `<name>/SKILL.md` per declared directory -- two skills in one directory leave
    it ambiguous which one the run generated, so uniqueness is kept, scoped to a directory;
  - **at least one** candidate across the whole set; and
  - **every** candidate satisfies the template -- a copy that does not is a non-conforming output
    in that platform folder, whatever the others hold.

Uniqueness is per directory, not across the set, because the installed-target row requires the
skill in *every* installed platform folder that exists: a correct output for a target with two or
more platforms has two or more copies, and a set-wide "exactly one" guard would reject it. Option
(ii), relocating the fixture to the authoring row, would move a file under `fixture/`, which `T548`
was not authorized to do. Not asserted, deliberately: that the skill exists in all seven platform
folders (SS7's out-of-scope row); which row's precondition the fixture meets; and that copies in
different directories are byte-identical or share one `<name>` -- the command declares neither.

Expected to return False, and not because of the path: a corpus survey of all 26 real SKILL.md
files (both the implementation/knowledge/skills/ sources and their .github/skills/ projections)
found 0/26 satisfying this template. See brief.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = (
    "## When to Use",
    "## Inputs",
    "## Procedure",
    "## Success Criteria",
    "## Examples",
)
TITLE_RE = re.compile(r"^#\s+\S.*$", re.MULTILINE)
# `### Choose the Output Path`'s declared set, in the command's own order: the authoring row's
# source directory, then the installed-target row's seven platform folders.
DECLARED_SKILL_ROOTS = (
    ("implementation", "knowledge", "skills"),
    (".github", "skills"),
    (".claude", "skills"),
    (".cursor", "skills"),
    (".gemini", "skills"),
    (".opencode", "skills"),
    (".pi", "skills"),
    (".cline", "skills"),
)


def _satisfies_template(text: str) -> bool:
    if not TITLE_RE.search(text):
        return False
    return all(section in text for section in REQUIRED_SECTIONS)


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    skills_roots = [fixture.joinpath(*parts) for parts in DECLARED_SKILL_ROOTS]
    existing_roots = [root for root in skills_roots if root.is_dir()]
    if not existing_roots:
        return False
    candidates: list[Path] = []
    for root in existing_roots:
        in_root = sorted(root.glob("*/SKILL.md"))
        if len(in_root) > 1:
            return False  # two skills in one declared directory: ambiguous
        candidates.extend(in_root)
    if not candidates:
        return False
    return all(_satisfies_template(path.read_text(encoding="utf-8")) for path in candidates)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
