#!/usr/bin/env python3
"""Render platform-aware AGENTS.md for installer targets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLATFORM_MAP = {
    "github": {
        "skills": ".github/skills/",
        "standards": ".github/instructions/coding-standards.instructions.md",
        "security": ".github/instructions/security-guidelines.instructions.md",
        "mcp": ".vscode/mcp.json",
    },
    "gemini": {
        "skills": ".gemini/skills/",
        "standards": ".gemini/instructions/coding-standards.md",
        "security": ".gemini/instructions/security-guidelines.md",
        "mcp": ".gemini/settings.json",
    },
    "opencode": {
        "skills": ".opencode/skills/",
        "standards": ".opencode/instructions/coding-standards.md",
        "security": ".opencode/instructions/security-guidelines.md",
        "mcp": ".opencode/opencode.json",
    },
    "pi": {
        "skills": ".pi/skills/",
        "standards": ".pi/instructions/coding-standards.md",
        "security": ".pi/instructions/security-guidelines.md",
        "mcp": ".pi/mcp.json",
    },
    "claude-code": {
        "skills": ".claude/skills/",
        "standards": ".claude/rules/coding-standards.md",
        "security": ".claude/rules/security-guidelines.md",
        "mcp": ".mcp.json",
    },
    "cline": {
        "skills": ".cline/skills/",
        "standards": ".clinerules/coding-standards.md",
        "security": ".clinerules/security-guidelines.md",
        "mcp": ".cline/mcp.json",
    },
}


def _replace_one(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count == 0:
        raise ValueError(f"pattern not found for replacement: {pattern}")
    return updated


def _refs_for_all() -> dict[str, str]:
    """The replacement texts that list every platform's paths (T677: split out of render)."""
    skills_paths = [cfg["skills"] for cfg in PLATFORM_MAP.values()]
    skills_ref = (
        "MUST check applicable skills in the active platform projection ("
        + ", ".join(f"`{p}`" for p in skills_paths)
        + ") (or invoke `/discover-skills`)."
    )

    standards_paths = [cfg["standards"] for cfg in PLATFORM_MAP.values()]
    code_ref = (
        "- See platform instruction projections: "
        + ", ".join(f"`{p}`" for p in standards_paths)
        + "."
    )

    security_paths = [cfg["security"] for cfg in PLATFORM_MAP.values()]
    sec_ref = (
        "- See platform security instruction projections: "
        + ", ".join(f"`{p}`" for p in security_paths)
        + ", and `implementation/SECURITY.md`."
    )

    roots: list[str] = []
    for cfg in PLATFORM_MAP.values():
        for field in ("skills", "standards", "security"):
            root = cfg[field].split("/")[0] + "/"
            if root not in roots:
                roots.append(root)
    readme_ref = (
        "- Use the installed platform folders ("
        + ", ".join(f"`{r}`" for r in roots)
        + ") as runtime references in this target project."
    )

    mcp_paths = [cfg["mcp"] for cfg in PLATFORM_MAP.values()]
    mcp_ref = (
        "Declared in platform MCP configs ("
        + ", ".join(f"`{p}`" for p in mcp_paths)
        + "). Each server is tagged:"
    )
    return {"skills": skills_ref, "code": code_ref, "sec": sec_ref, "readme": readme_ref, "mcp": mcp_ref}


def _refs_for_platform(platform: str) -> dict[str, str]:
    """The replacement texts that name one platform's paths."""
    if platform not in PLATFORM_MAP:
        raise ValueError(f"unsupported platform for AGENTS rewrite: {platform}")
    cfg = PLATFORM_MAP[platform]
    return {
        "skills": f"MUST check applicable skills in `{cfg['skills']}` (or invoke `/discover-skills`).",
        "code": f"- See `{cfg['standards']}` for coding standards projected for this platform.",
        "sec": f"- See `{cfg['security']}` and `implementation/SECURITY.md`.",
        "readme": (
            f"- See installed platform projection roots (`{cfg['skills'].split('/')[0]}/`) "
            "for runtime authoring references in this target project."
        ),
        "mcp": f"Declared in [`{cfg['mcp']}`]({cfg['mcp']}). Each server is tagged:",
    }


def render(source_text: str, platform: str) -> str:
    refs = _refs_for_all() if platform == "all" else _refs_for_platform(platform)

    kb_ref = (
        "- Source knowledge lives in the emage.code repository under "
        "`implementation/knowledge/`; this target uses installed platform projections."
    )

    replacements = (
        (r"MUST check applicable skills in `[^`]+` \(or invoke `/discover-skills`\)\.", refs["skills"]),
        (r"- See `[^`]*coding-standards[^`]*`[^\n]*", refs["code"]),
        (r"- See `[^`]*security-guidelines[^`]*`[^\n]*", refs["sec"]),
        (r"- The single source of truth for agents, skills, commands, and instructions is `[^`]+`\.", kb_ref),
        (r"- See \[`[^`]*README\.md`\]\([^)]+\) for authoring rules\.", refs["readme"]),
        (r"Declared in \[`[^`]+`\]\([^)]+\)\. Each server is tagged:", refs["mcp"]),
    )
    text = source_text
    for pattern, replacement in replacements:
        text = _replace_one(text, pattern, replacement)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--platform", required=True, choices=["github", "gemini", "opencode", "pi", "claude-code", "cline", "all"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.source)
    dest = Path(args.dest)
    # SEC-001 (T636): never write through a symlink, dry-run included.
    if dest.is_symlink():
        print(f"render_installed_agents: refusing to write through a symlink: {dest}", file=sys.stderr)
        return 1
    rendered = render(src.read_text(encoding="utf-8"), args.platform)

    if args.dry_run:
        print(f"DRY-RUN: render platform-aware AGENTS.md ({args.platform}) -> {dest}")
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
