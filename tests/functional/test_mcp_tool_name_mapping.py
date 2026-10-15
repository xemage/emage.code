"""T657 (SEC-T655-01) -- per-platform rendering of MCP tool names in the agent tool lines.

The agent sources keep one form: `mcp__<server>` (a whole server) and `mcp__<server>__<tool>`.
`implementation/scripts/sync.mjs` renders it per platform through the manifest key
`frontmatter.agents.mcpToolNames`. The accepted forms, with their sources, are recorded in
docs/artifacts/mcp-tool-name-mapping-v1.md. This file pins:

- the manifest opt-in per platform (a platform whose naming is unverified must not opt in);
- the rendering, with an independent Python re-implementation checked against literal examples
  and against the generator run on a fixture root;
- every generated agent file of the four mapped platforms against the mapping of its source.

Static inspection plus a local `node` run on a temporary root; no network.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import implementation_root, knowledge_root, repo_root

PLATFORMS_DIR = implementation_root() / "platforms"
ARTIFACT = repo_root() / "docs" / "artifacts" / "mcp-tool-name-mapping-v1.md"

# platform -> mcpToolNames in the manifest. Gemini drops the tools line, Cline has no agent
# files, so neither can carry the key; Cursor and Claude Code render verbatim.
EXPECTED_STYLE = {
    "claude-code": "verbatim",
    "cursor": "verbatim",
    "github": "slash",
    "opencode": "underscore",
    "pi": "pi",
}
NO_AGENT_TOOL_RENDERING = ("gemini", "cline")


def expected_name(style: str, token: str) -> str:
    """Independent re-implementation of the documented rules (not a copy of the JavaScript)."""
    if style == "verbatim" or not token.startswith("mcp__"):
        return token
    rest = token[len("mcp__"):]
    server, sep, tool = rest.partition("__")
    if not sep:
        tool = "*"
    if style == "slash":
        server = re.sub(r"\s+", "-", server.lower())
        return f"{server}/*" if tool == "*" else f"{server}/{tool.replace('.', '_')}"
    if style == "underscore":
        clean = lambda s: re.sub(r"[^a-zA-Z0-9_-]", "_", s)  # noqa: E731
        return f"{clean(server)}_*" if tool == "*" else f"{clean(server)}_{clean(tool)}"
    if style == "pi":
        clean = lambda s: re.sub(r"[^a-zA-Z0-9_]", "_", s)  # noqa: E731
        return f"mcp__{clean(server)}__" + ("*" if tool == "*" else clean(tool))
    raise AssertionError(style)


def _manifest(platform: str) -> dict:
    return json.loads((PLATFORMS_DIR / f"{platform}.json").read_text(encoding="utf-8"))


def _source_tools(slug: str) -> list[str]:
    fm, _ = parse_file(knowledge_root() / "agents" / f"{slug}.md")
    return list(fm.get("tools") or [])


def _projected_tools(platform: str, slug: str) -> list[str]:
    root = implementation_root()
    if platform == "github":
        fm, _ = parse_file(root / ".github" / "agents" / f"{slug}.agent.md")
        return list(fm["tools"])
    if platform == "pi":
        fm, _ = parse_file(root / ".pi" / "agents" / f"{slug}.md")
        return list(fm["tools"])
    if platform == "opencode":
        fm, _ = parse_file(root / ".opencode" / "agents" / f"{slug}.md")
        return list(fm["tools"])
    raise AssertionError(platform)


class ManifestOptInTests(unittest.TestCase):
    def test_each_platform_declares_the_documented_style(self):
        for platform, style in EXPECTED_STYLE.items():
            with self.subTest(platform=platform):
                cfg = _manifest(platform)["frontmatter"]["agents"]
                self.assertEqual(cfg.get("mcpToolNames"), style)

    def test_platforms_without_a_tools_line_do_not_opt_in(self):
        for platform in NO_AGENT_TOOL_RENDERING:
            with self.subTest(platform=platform):
                manifest = _manifest(platform)
                cfg = manifest["frontmatter"].get("agents", {})
                self.assertNotIn("mcpToolNames", cfg)
                if platform == "gemini":
                    self.assertEqual(cfg.get("tools"), "drop")
                else:
                    self.assertNotIn("agents", manifest["fileMap"])

    def test_every_manifest_is_accounted_for(self):
        found = {p.stem for p in PLATFORMS_DIR.glob("*.json") if not p.name.startswith("_")}
        self.assertEqual(found, set(EXPECTED_STYLE) | set(NO_AGENT_TOOL_RENDERING))


class RenderingRuleTests(unittest.TestCase):
    """Literal examples taken from the vendor documentation quoted in the artifact."""

    CASES = {
        "slash": {
            "mcp__playwright__browser_navigate": "playwright/browser_navigate",
            "mcp__gitlab": "gitlab/*",
            "mcp__security-audit__run_npm_audit": "security-audit/run_npm_audit",
            "mcp__poc-security-audit__scan_secrets": "poc-security-audit/scan_secrets",
            "mcp__srv__*": "srv/*",
            "read": "read",
        },
        "underscore": {
            "mcp__playwright__browser_navigate": "playwright_browser_navigate",
            "mcp__gitlab": "gitlab_*",
            "mcp__sequential-thinking": "sequential-thinking_*",
            "mcp__security-audit__grep_content": "security-audit_grep_content",
            "read": "read",
        },
        "pi": {
            "mcp__playwright__browser_navigate": "mcp__playwright__browser_navigate",
            "mcp__gitlab": "mcp__gitlab__*",
            "mcp__sequential-thinking": "mcp__sequential_thinking__*",
            "mcp__security-audit__grep_content": "mcp__security_audit__grep_content",
            "mcp__poc-security-audit__ref_containment": "mcp__poc_security_audit__ref_containment",
            "read": "read",
        },
        "verbatim": {
            "mcp__playwright__browser_navigate": "mcp__playwright__browser_navigate",
            "mcp__gitlab": "mcp__gitlab",
            "read": "read",
        },
    }

    def test_documented_examples(self):
        for style, cases in self.CASES.items():
            for source, rendered in cases.items():
                with self.subTest(style=style, source=source):
                    self.assertEqual(expected_name(style, source), rendered)


class GeneratorRunTests(unittest.TestCase):
    """Run the real generator on a fixture root and compare with the independent rules."""

    TOOLS = ["read", "mcp__playwright__browser_click", "mcp__playwright", "mcp__security-audit__run_npm_audit",
             "mcp__my.server__tool.name", "mcp__srv__*"]

    @classmethod
    def setUpClass(cls):
        if shutil.which("node") is None:
            raise unittest.SkipTest("node is not installed")
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        cls._build(cls.root)
        cls.result = subprocess.run(["node", str(implementation_root() / "scripts" / "sync.mjs"),
                                     "--root", str(cls.root)], capture_output=True, text=True, check=False)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def _build(cls, root: Path) -> None:
        (root / "platforms").mkdir()
        for path in PLATFORMS_DIR.glob("*.json"):
            shutil.copy(path, root / "platforms" / path.name)
        shutil.copytree(implementation_root() / "_extras", root / "_extras")
        (root / "knowledge" / "mcp").mkdir(parents=True)
        shutil.copy(knowledge_root() / "mcp" / "servers.yaml", root / "knowledge" / "mcp" / "servers.yaml")
        for kind in ("commands", "instructions", "skills"):
            (root / "knowledge" / kind).mkdir()
        agents = root / "knowledge" / "agents"
        agents.mkdir()
        (agents / "fx.md").write_text(
            "---\nname: \"Fixture\"\ndescription: \"fixture\"\ntools: [" + ", ".join(cls.TOOLS) + "]\n---\n\nbody\n",
            encoding="utf-8")

    def _tools(self, rel: str) -> list[str]:
        fm, _ = parse_file(self.root / rel)
        tools = fm["tools"]
        if isinstance(tools, str):
            return [t.strip() for t in tools.split(",")]
        return list(tools)

    def test_generator_succeeded(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)

    def test_rendering_per_platform(self):
        cases = {
            "github": (".github/agents/fx.agent.md", "slash"),
            "opencode": (".opencode/agents/fx.md", "underscore"),
            "pi": (".pi/agents/fx.md", "pi"),
            "cursor": (".cursor/agents/fx.mdc", "verbatim"),
        }
        for platform, (rel, style) in cases.items():
            with self.subTest(platform=platform):
                self.assertEqual(self._tools(rel), [expected_name(style, t) for t in self.TOOLS])

    def test_claude_code_keeps_the_source_form(self):
        rendered = self._tools(".claude/agents/fx.md")
        self.assertEqual(rendered, ["Read"] + self.TOOLS[1:])

    def test_gemini_still_drops_the_tools_line(self):
        fm, _ = parse_file(self.root / ".gemini" / "agents" / "fx.md")
        self.assertNotIn("tools", fm)

    def test_an_unknown_style_fails_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._build(root)
            manifest = root / "platforms" / "github.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["frontmatter"]["agents"]["mcpToolNames"] = "colon"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(["node", str(implementation_root() / "scripts" / "sync.mjs"),
                                     "--root", str(root), "--platform=github"],
                                    capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown mcpToolNames style", result.stderr)


class ProjectedAgentTests(unittest.TestCase):
    """Every shipped agent file of a mapped platform equals the mapping of its source."""

    def test_projected_tools_equal_the_mapping_of_the_source(self):
        for platform in ("github", "opencode", "pi"):
            style = EXPECTED_STYLE[platform]
            for source in sorted((knowledge_root() / "agents").glob("*.md")):
                slug = source.stem
                with self.subTest(platform=platform, agent=slug):
                    want = [expected_name(style, t) for t in _source_tools(slug)]
                    got = _projected_tools(platform, slug)
                    self.assertEqual(got, list(dict.fromkeys(want)))

    def test_no_mapped_platform_ships_a_source_form_mcp_name_that_it_does_not_honour(self):
        for platform in ("github", "opencode"):
            for source in sorted((knowledge_root() / "agents").glob("*.md")):
                with self.subTest(platform=platform, agent=source.stem):
                    for name in _projected_tools(platform, source.stem):
                        self.assertFalse(name.startswith("mcp__"), name)

    def test_no_projection_names_the_unsafe_tool(self):
        for path in implementation_root().glob(".*/agents/*"):
            self.assertNotIn("browser_run_code_unsafe", path.read_text(encoding="utf-8"), str(path))


class ArtifactTests(unittest.TestCase):
    def test_artifact_exists_and_records_every_platform(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertIn("Based on: security-review-t655-fetch-removal-v1.md", text)
        for platform in ("Claude Code", "GitHub Copilot", "Opencode", "Gemini CLI", "Cursor", "Cline", "Pi"):
            self.assertIn(platform, text)
        self.assertRegex(text, r"(?i)verified")
        self.assertRegex(text, r"(?i)unverified")

    def test_artifact_never_recommends_the_unsafe_tool(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "browser_run_code_unsafe" in line:
                self.assertRegex(line, r"(?i)(never|not|excluded|without|removable|unsafe|host)", line)


if __name__ == "__main__":
    unittest.main()
