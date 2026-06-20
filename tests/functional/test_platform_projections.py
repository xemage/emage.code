"""Cross-platform projection integrity checks.

These tests ensure the generated outputs for GitHub Copilot, Gemini, and
Opencode stay consistent with canonical knowledge and manifest contracts.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import (
    implementation_root,
    knowledge_root,
    list_agents,
    list_commands,
    list_instructions,
    list_skills,
)

_TARGET_PLATFORMS = ("github", "gemini", "opencode")


def _load_manifest(platform: str) -> dict:
    path = implementation_root() / "platforms" / f"{platform}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _generated_root(platform: str) -> Path:
    manifest = _load_manifest(platform)
    return implementation_root() / manifest["outputDir"]


def _source_files(kind: str) -> list[Path]:
    if kind == "agents":
        return list_agents()
    if kind == "commands":
        return list_commands()
    if kind == "instructions":
        return list_instructions()
    if kind == "skills":
        return list_skills()
    raise ValueError(f"unknown projection kind: {kind}")


def _generated_relpath(platform: str, kind: str, source_path: Path) -> str:
    m = _load_manifest(platform)["fileMap"][kind]
    out_dir = m["dir"]
    if kind == "skills":
        return f"{out_dir}/{source_path.parent.name}/SKILL.md"
    ext = m.get("ext", ".md")
    return f"{out_dir}/{source_path.stem}{ext}"


def _expected_generated_relpaths(platform: str) -> set[str]:
    relpaths: set[str] = set()
    for kind in ("agents", "commands", "instructions", "skills"):
        for source_path in _source_files(kind):
            relpaths.add(_generated_relpath(platform, kind, source_path))
    return relpaths


def _expected_frontmatter_keys(platform: str, kind: str, slug: str) -> set[str]:
    manifest = _load_manifest(platform)
    frontmatter = manifest["frontmatter"][kind]
    keys = set(frontmatter.get("keepKeys", []))
    if kind == "agents":
        additions = frontmatter.get("addToOrchestrators")
        orchestrators = set(frontmatter.get("orchestratorNames", []))
        if additions and slug in orchestrators:
            keys.update(additions.keys())
    return keys


class TestPlatformProjections(unittest.TestCase):
    def test_expected_files_exist_for_all_target_platforms(self):
        for platform in _TARGET_PLATFORMS:
            with self.subTest(platform=platform):
                root = _generated_root(platform)
                self.assertTrue(root.exists(), f"missing generated root: {root}")
                expected = _expected_generated_relpaths(platform)
                missing = [p for p in sorted(expected) if not (root / p).exists()]
                self.assertFalse(
                    missing,
                    msg=f"{platform}: missing generated files:\n  " + "\n  ".join(missing),
                )

    def test_generated_manifest_covers_expected_files(self):
        for platform in _TARGET_PLATFORMS:
            with self.subTest(platform=platform):
                root = _generated_root(platform)
                generated_manifest = json.loads(
                    (root / ".generated-manifest.json").read_text(encoding="utf-8")
                )
                listed = set(generated_manifest.get("files", []))
                expected = _expected_generated_relpaths(platform)
                missing_in_manifest = sorted(expected - listed)
                self.assertFalse(
                    missing_in_manifest,
                    msg=(
                        f"{platform}: expected files absent from .generated-manifest.json:\n  "
                        + "\n  ".join(missing_in_manifest)
                    ),
                )

    def test_projection_frontmatter_keys_match_manifest_contract(self):
        for platform in _TARGET_PLATFORMS:
            root = _generated_root(platform)
            for kind in ("agents", "commands", "instructions", "skills"):
                for source_path in _source_files(kind):
                    relpath = _generated_relpath(platform, kind, source_path)
                    target_path = root / relpath
                    fm, _ = parse_file(target_path)
                    expected_keys = _expected_frontmatter_keys(platform, kind, source_path.stem)
                    with self.subTest(platform=platform, kind=kind, file=relpath):
                        unknown_keys = set(fm) - expected_keys
                        self.assertFalse(
                            unknown_keys,
                            f"{platform}/{relpath}: unexpected frontmatter keys {sorted(unknown_keys)}",
                        )

    def test_projection_preserves_non_frontmatter_content(self):
        for platform in _TARGET_PLATFORMS:
            root = _generated_root(platform)
            for kind in ("agents", "commands", "instructions", "skills"):
                for source_path in _source_files(kind):
                    source_fm, source_body = parse_file(source_path)
                    relpath = _generated_relpath(platform, kind, source_path)
                    target_fm, target_body = parse_file(root / relpath)
                    with self.subTest(platform=platform, kind=kind, file=relpath):
                        self.assertEqual(target_body, source_body)
                        for key in _expected_frontmatter_keys(platform, kind, source_path.stem):
                            if key in ("tools", "user-invocable"):
                                continue
                            if key in source_fm:
                                self.assertEqual(target_fm.get(key), source_fm[key])

    def test_gemini_agents_drop_tools_field(self):
        gemini_agents = _generated_root("gemini") / "agents"
        for path in sorted(gemini_agents.glob("*.md")):
            fm, _ = parse_file(path)
            with self.subTest(agent=path.stem):
                self.assertNotIn("tools", fm, f"{path.name}: Gemini should drop tools")

    def test_opencode_agents_use_tools_object(self):
        opencode_agents = _generated_root("opencode") / "agents"
        source_agents_dir = knowledge_root() / "agents"

        for path in sorted(opencode_agents.glob("*.md")):
            source_fm, _ = parse_file(source_agents_dir / f"{path.stem}.md")
            projected_fm, _ = parse_file(path)
            source_tools = source_fm.get("tools", [])
            projected_tools = projected_fm.get("tools")
            with self.subTest(agent=path.stem):
                self.assertIsInstance(projected_tools, dict, f"{path.name}: tools should be object")
                self.assertTrue(projected_tools, f"{path.name}: tools object should not be empty")
                self.assertEqual(
                    set(projected_tools),
                    set(source_tools),
                    f"{path.name}: tools keys must match source tools list",
                )
                self.assertTrue(
                    all(value is True for value in projected_tools.values()),
                    f"{path.name}: all tool values should be true",
                )

        for orchestrator in ("orchestrator", "poc-orchestrator"):
            fm, _ = parse_file(opencode_agents / f"{orchestrator}.md")
            self.assertTrue(
                fm.get("user-invocable") is True,
                f"{orchestrator}.md: user-invocable must be true in Opencode projection",
            )

    def test_github_agent_aliases_match_filename_slugs(self):
        """GitHub Copilot resolves subagents by filename slug when `name` is omitted.

        Orchestrator `agents:` lists use kebab-case slugs; projecting display names
        into `name` breaks runSubagent delegation (alias not registered).
        """
        github_agents = _generated_root("github") / "agents"
        for path in sorted(github_agents.glob("*.agent.md")):
            slug = path.name.replace(".agent.md", "")
            fm, _ = parse_file(path)
            with self.subTest(agent=slug):
                self.assertNotIn(
                    "name",
                    fm,
                    f"{path.name}: GitHub projection must omit `name` so Copilot uses slug {slug!r}",
                )

    def test_github_orchestrator_agents_list_matches_slug_aliases(self):
        github_agents = _generated_root("github") / "agents"
        for orchestrator in ("orchestrator", "poc-orchestrator"):
            fm, _ = parse_file(github_agents / f"{orchestrator}.agent.md")
            delegated = fm.get("agents") or []
            with self.subTest(orchestrator=orchestrator):
                for ref in delegated:
                    agent_path = github_agents / f"{ref}.agent.md"
                    self.assertTrue(
                        agent_path.exists(),
                        f"{orchestrator} delegates to {ref!r} but {agent_path.name} is missing",
                    )
                    sub_fm, _ = parse_file(agent_path)
                    self.assertNotIn(
                        "name",
                        sub_fm,
                        f"{agent_path.name}: subagent must register under slug {ref!r}",
                    )

    def test_github_orchestrators_are_user_invocable(self):
        github_agents = _generated_root("github") / "agents"
        for orchestrator in ("orchestrator", "poc-orchestrator"):
            fm, _ = parse_file(github_agents / f"{orchestrator}.agent.md")
            self.assertTrue(
                fm.get("user-invocable") is True,
                f"{orchestrator}.agent.md: user-invocable must be true for GitHub Copilot",
            )

    def test_github_prompt_agent_references_resolve(self):
        github_prompts = _generated_root("github") / "prompts"
        agent_slugs = {p.stem for p in list_agents()}
        for path in sorted(github_prompts.glob("*.prompt.md")):
            fm, _ = parse_file(path)
            with self.subTest(prompt=path.name):
                if "agent" in fm:
                    self.assertIn(
                        fm["agent"],
                        agent_slugs,
                        f"{path.name}: unknown agent reference {fm['agent']!r}",
                    )

    def test_platform_mcp_configs_have_expected_shape(self):
        gemini_settings = json.loads(
            (_generated_root("gemini") / "settings.json").read_text(encoding="utf-8")
        )
        self.assertIn("mcpServers", gemini_settings)
        self.assertIn("gitlab", gemini_settings["mcpServers"])
        self.assertIn("context7", gemini_settings["mcpServers"])

        opencode_config = json.loads(
            (_generated_root("opencode") / "opencode.json").read_text(encoding="utf-8")
        )
        self.assertIn("mcp", opencode_config)
        self.assertIn("gitlab", opencode_config["mcp"])
        self.assertIn("context7", opencode_config["mcp"])
        self.assertEqual(
            opencode_config.get("instructions"),
            [
                "instructions/coding-standards.md",
                "instructions/git-workflow.md",
                "instructions/security-guidelines.md",
                "instructions/poc-guidelines.md",
            ],
        )

        vscode_mcp = json.loads(
            (implementation_root() / ".vscode" / "mcp.json").read_text(encoding="utf-8")
        )
        self.assertIn("servers", vscode_mcp)
        self.assertIn("gitlab", vscode_mcp["servers"])
        self.assertIn("context7", vscode_mcp["servers"])


if __name__ == "__main__":
    unittest.main()
