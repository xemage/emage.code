#!/usr/bin/env python3
"""Generate v3 knowledge registry from canonical metadata (compat mode supported)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\\s*\\n(.*?\\n)---\\s*\\n", re.DOTALL)
SEMVER = "3.0.0"
CATEGORY_DIRS = {
    "agent": "agents",
    "command": "commands",
    "instruction": "instructions",
    "skill": "skills",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--source-knowledge-root", default="")
    parser.add_argument("--out", default="")
    parser.add_argument("--summary-out", default="")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def _parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError(f"invalid frontmatter mapping: {path}")
    return frontmatter, text


def _maturity(frontmatter: dict) -> str:
    raw = str(frontmatter.get("maturity") or frontmatter.get("stability") or "beta").lower()
    mapping = {"experimental": "draft", "stable": "ga", "deprecated": "deprecated", "draft": "draft", "beta": "beta", "ga": "ga"}
    return mapping.get(raw, "beta")


def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _entry_from_file(category: str, path: Path, source_root: Path, platforms: list[str]) -> dict:
    frontmatter, text = _parse_frontmatter(path)
    rel_path = path.relative_to(source_root).as_posix()
    default_id = path.parent.name if category == "skill" else path.stem
    item_id = str(frontmatter.get("id") or default_id)
    name = str(frontmatter.get("name") or default_id)
    return {
        "id": item_id,
        "category": category,
        "name": name,
        "path": rel_path,
        "checksum": _checksum(text),
        "maturity": _maturity(frontmatter),
        "compatibility": {
            "supportedPlatforms": platforms,
            "projectionStatus": {platform: "pass" for platform in platforms},
        },
    }


def _collect_entries(source_root: Path, platforms: list[str]) -> list[dict]:
    entries: list[dict] = []
    for category, folder in CATEGORY_DIRS.items():
        base = source_root / folder
        if not base.is_dir():
            continue
        if category == "skill":
            for skill_dir in sorted([item for item in base.iterdir() if item.is_dir()]):
                skill_file = skill_dir / "SKILL.md"
                if skill_file.is_file():
                    entries.append(_entry_from_file(category, skill_file, source_root, platforms))
            continue
        for file_path in sorted(base.glob("*.md")):
            entries.append(_entry_from_file(category, file_path, source_root, platforms))
    return entries


def _detect_platforms(repo_root: Path) -> list[str]:
    platform_dir = repo_root / "v2" / "implementation" / "platforms"
    if not platform_dir.is_dir():
        return ["github", "gemini", "opencode", "cursor"]
    return sorted([item.stem for item in platform_dir.glob("*.json")])


def _summary_markdown(entries: list[dict], source_root: Path) -> str:
    counts = {category: 0 for category in CATEGORY_DIRS}
    for entry in entries:
        counts[entry["category"]] += 1

    lines = [
        "# v3 Registry Summary",
        "",
        f"Generated from: {source_root}",
        "",
        "## Counts",
        "",
        f"- agents: {counts['agent']}",
        f"- commands: {counts['command']}",
        f"- instructions: {counts['instruction']}",
        f"- skills: {counts['skill']}",
        "",
        "## Entries",
        "",
        "| ID | Category | Maturity | Path |",
        "|---|---|---|---|",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['id']} | {entry['category']} | {entry['maturity']} | {entry['path']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _registry_payload(entries: list[dict], source_root: Path, platforms: list[str], repo_root: Path) -> dict:
    try:
        source_root_value = source_root.relative_to(repo_root).as_posix()
    except ValueError:
        source_root_value = source_root.as_posix()

    return {
        "schemaVersion": SEMVER,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceRoot": source_root_value,
        "platforms": platforms,
        "entries": sorted(entries, key=lambda item: (item["category"], item["id"])),
    }


def _determine_source(root: Path, override: str) -> Path:
    if override:
        return Path(override).resolve()
    preferred = root / "knowledge"
    if preferred.is_dir():
        return preferred
    compat = root.parents[1] / "v2" / "implementation" / "knowledge"
    return compat


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    repo_root = root.parents[1]
    source_root = _determine_source(root, args.source_knowledge_root)
    out_path = Path(args.out).resolve() if args.out else root / "registry" / "index.json"
    summary_path = Path(args.summary_out).resolve() if args.summary_out else root / "registry" / "summary.md"

    platforms = _detect_platforms(repo_root)
    entries = _collect_entries(source_root, platforms)
    payload = _registry_payload(entries, source_root, platforms, repo_root)
    summary = _summary_markdown(payload["entries"], source_root)

    out_text = json.dumps(payload, indent=2) + "\n"
    if args.check:
        current_index = out_path.read_text(encoding="utf-8") if out_path.is_file() else ""
        current_summary = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
        normalized_current = ""
        if current_index:
            data = json.loads(current_index)
            data["generatedAt"] = payload["generatedAt"]
            normalized_current = json.dumps(data, indent=2) + "\n"
        if normalized_current != out_text or current_summary.rstrip("\n") != summary.rstrip("\n"):
            print("registry drift detected; run generate-registry-v3.py")
            return 1
        print("registry is up to date")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text, encoding="utf-8")
    summary_path.write_text(summary + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
