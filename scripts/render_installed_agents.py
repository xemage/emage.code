#!/usr/bin/env python3
"""Render platform-aware AGENTS.md for installer targets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PLATFORM_MAP = {
    "github": {
        "skills": ".github/skills/",
        "standards": ".github/instructions/coding-standards.instructions.md",
        "security": ".github/instructions/security-guidelines.instructions.md",
        "mcp": ".vscode/mcp.json",
    },
    "cursor": {
        "skills": ".cursor/skills/",
        "standards": ".cursor/rules/coding-standards.mdc",
        "security": ".cursor/rules/security-guidelines.mdc",
        "mcp": ".cursor/mcp.json",
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
}


def _replace_one(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count == 0:
        raise ValueError(f"pattern not found for replacement: {pattern}")
    return updated


def render(source_text: str, platform: str) -> str:
    if platform == "all":
        skills_ref = (
            "MUST check applicable skills in the active platform projection "
            "(`.github/skills/`, `.cursor/skills/`, `.gemini/skills/`, "
            "`.opencode/skills/`, `.pi/skills/`, `.claude/skills/`) "
            "(or invoke `/discover-skills`)."
        )
        code_ref = (
            "- See platform instruction projections: "
            "`.github/instructions/coding-standards.instructions.md`, "
            "`.cursor/rules/coding-standards.mdc`, "
            "`.gemini/instructions/coding-standards.md`, "
            "`.opencode/instructions/coding-standards.md`, "
            "`.pi/instructions/coding-standards.md`, "
            "`.claude/rules/coding-standards.md`."
        )
        sec_ref = (
            "- See platform security instruction projections: "
            "`.github/instructions/security-guidelines.instructions.md`, "
            "`.cursor/rules/security-guidelines.mdc`, "
            "`.gemini/instructions/security-guidelines.md`, "
            "`.opencode/instructions/security-guidelines.md`, "
            "`.pi/instructions/security-guidelines.md`, "
            "`.claude/rules/security-guidelines.md`, and `implementation/SECURITY.md`."
        )
        readme_ref = (
            "- Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, "
            "`.opencode/`, `.pi/`, `.claude/`) as runtime references in this target project."
        )
        mcp_ref = (
            "Declared in platform MCP configs "
            "(`.vscode/mcp.json`, `.cursor/mcp.json`, `.gemini/settings.json`, "
            "`.opencode/opencode.json`, `.pi/mcp.json`, `.mcp.json`). Each server is tagged:"
        )
    else:
        if platform not in PLATFORM_MAP:
            raise ValueError(f"unsupported platform for AGENTS rewrite: {platform}")
        cfg = PLATFORM_MAP[platform]
        skills_ref = f"MUST check applicable skills in `{cfg['skills']}` (or invoke `/discover-skills`)."
        code_ref = f"- See `{cfg['standards']}` for coding standards projected for this platform."
        sec_ref = f"- See `{cfg['security']}` and `implementation/SECURITY.md`."
        readme_ref = (
            f"- See installed platform projection roots (`{cfg['skills'].split('/')[0]}/`) "
            "for runtime authoring references in this target project."
        )
        mcp_ref = f"Declared in [`{cfg['mcp']}`]({cfg['mcp']}). Each server is tagged:"

    kb_ref = (
        "- Source knowledge lives in the emage.code repository under "
        "`implementation/knowledge/`; this target uses installed platform projections."
    )

    text = source_text
    text = _replace_one(
        text,
        r"MUST check applicable skills in `[^`]+` \(or invoke `/discover-skills`\)\.",
        skills_ref,
    )
    text = _replace_one(
        text,
        r"- See `[^`]*coding-standards[^`]*`[^\n]*",
        code_ref,
    )
    text = _replace_one(
        text,
        r"- See `[^`]*security-guidelines[^`]*`[^\n]*",
        sec_ref,
    )
    text = _replace_one(
        text,
        r"- The single source of truth for agents, skills, commands, and instructions is `[^`]+`\.",
        kb_ref,
    )
    text = _replace_one(
        text,
        r"- See \[`[^`]*README\.md`\]\([^)]+\) for authoring rules\.",
        readme_ref,
    )
    text = _replace_one(
        text,
        r"Declared in \[`[^`]+`\]\([^)]+\)\. Each server is tagged:",
        mcp_ref,
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--platform", required=True, choices=["github", "cursor", "gemini", "opencode", "pi", "claude-code", "all"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.source)
    dest = Path(args.dest)
    rendered = render(src.read_text(encoding="utf-8"), args.platform)

    if args.dry_run:
        print(f"DRY-RUN: render platform-aware AGENTS.md ({args.platform}) -> {dest}")
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
