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
# files, so neither can carry the key; Claude Code renders verbatim.
EXPECTED_STYLE = {
    "claude-code": "verbatim",
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
        # T663: the map also carries generated `false` entries (per-agent denials); the grant list is
        # the `true` entries, in order.
        return [name for name, value in fm["tools"].items() if value is True]
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
        if isinstance(tools, dict):
            # T663: Opencode's map also carries generated `false` entries (the per-agent denials)
            return [name for name, value in tools.items() if value is True]
        return list(tools)

    def test_generator_succeeded(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)

    def test_rendering_per_platform(self):
        cases = {
            "github": (".github/agents/fx.agent.md", "slash"),
            "opencode": (".opencode/agents/fx.md", "underscore"),
            "pi": (".pi/agents/fx.md", "pi"),
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


class ManifestAndTokenValidationTests(unittest.TestCase):
    """T658 (SEC-T657-09): the style is validated at manifest load, a non-terminal `*` stops the run."""

    SYNC = implementation_root() / "scripts" / "sync.mjs"

    def _run(self, platform: str, edit=None, tools: list[str] | None = None) -> subprocess.CompletedProcess:
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            GeneratorRunTests._build(root)
            if tools is not None:
                fx = root / "knowledge" / "agents" / "fx.md"
                fx.write_text("---\nname: \"Fixture\"\ndescription: \"fixture\"\ntools: [" + ", ".join(tools) + "]\n---\n\nbody\n",
                              encoding="utf-8")
            manifest = root / "platforms" / f"{platform}.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if edit:
                edit(data)
            manifest.write_text(json.dumps(data), encoding="utf-8")
            return subprocess.run(["node", str(self.SYNC), "--root", str(root), f"--platform={platform}"],
                                  capture_output=True, text=True, check=False)

    def test_unknown_style_fails_even_when_the_platform_drops_the_tools_line(self):
        # Gemini drops `tools`; before T658 the style was never read there, so a typo passed silently.
        result = self._run("gemini", lambda d: d["frontmatter"]["agents"].__setitem__("mcpToolNames", "colon"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown mcpToolNames style", result.stderr)

    def test_falsy_and_non_string_styles_fail(self):
        for bad in ("", None, 0, ["slash"], {"a": 1}):
            with self.subTest(style=bad):
                result = self._run("github", lambda d, v=bad: d["frontmatter"]["agents"].__setitem__("mcpToolNames", v))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unknown mcpToolNames style", result.stderr)

    def test_a_style_on_a_platform_without_agent_files_is_still_validated(self):
        result = self._run("cline", lambda d: d["frontmatter"].setdefault("agents", {}).__setitem__("mcpToolNames", "nope"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown mcpToolNames style", result.stderr)

    def test_prototype_names_are_not_styles(self):
        result = self._run("github", lambda d: d["frontmatter"]["agents"].__setitem__("mcpToolNames", "__proto__"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown mcpToolNames style", result.stderr)

    def test_a_star_that_is_not_the_whole_tool_part_stops_the_run(self):
        for token in ("mcp__srv__foo*", "mcp__srv__*foo", "mcp__srv__fo*o", "mcp__s*rv__tool", "mcp__s*rv", "mcp__srv*"):
            for platform in ("github", "opencode", "pi"):
                with self.subTest(platform=platform, token=token):
                    result = self._run(platform, tools=["read", token])
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Non-terminal '*'", result.stderr)

    def test_a_star_as_the_whole_tool_part_is_still_accepted(self):
        for platform in ("github", "opencode", "pi"):
            with self.subTest(platform=platform):
                result = self._run(platform, tools=["read", "mcp__srv__*", "mcp__srv"])
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


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

    # T690 (K-3, D-4 b): `<server>/<tool>` tokens in a Copilot agent file name a server that the generated
    # `.vscode/mcp.json` carries. `context-retriever` is the one server an agent lists that Copilot does not
    # carry (an `extended` server outside T690's scope: the config for it is generated for the other platforms
    # only); it is pinned here so that a second gap cannot appear unnoticed.
    COPILOT_SERVERS_NOT_IN_VSCODE_CONFIG = {"context-retriever"}

    def test_every_server_a_copilot_agent_lists_is_in_the_generated_vscode_config(self):
        config = json.loads((implementation_root() / ".vscode" / "mcp.json").read_text(encoding="utf-8"))["servers"]
        missing = set()
        for source in sorted((knowledge_root() / "agents").glob("*.md")):
            for name in _projected_tools("github", source.stem):
                if "/" in name and name.split("/", 1)[0] not in config:
                    missing.add(name.split("/", 1)[0])
        self.assertEqual(missing, self.COPILOT_SERVERS_NOT_IN_VSCODE_CONFIG)
        for server in ("security-audit", "poc-security-audit"):
            self.assertIn(server, config)

    def test_no_projection_names_the_unsafe_tool(self):
        # T658 (SEC-T657-07): a file-count floor, so an empty glob (a renamed directory) cannot pass
        # vacuously. Five platforms project agent files (Cline has none); every source agent is projected.
        files = [p for p in implementation_root().glob(".*/agents/*") if p.is_file()]
        sources = len(list((knowledge_root() / "agents").glob("*.md")))
        self.assertGreaterEqual(len(files), sources * 5)
        for path in files:
            text = path.read_text(encoding="utf-8")
            if path.parent.parent.name == ".opencode":
                # T663: an Opencode agent file names it only as the generated per-agent deny
                for line in text.splitlines():
                    if "browser_run_code_unsafe" in line:
                        self.assertEqual(line, "  playwright_browser_run_code_unsafe: false", str(path))
            else:
                self.assertNotIn("browser_run_code_unsafe", text, str(path))


# --- T673 (SEC-T658-06): artifact assertions anchored to the section and row they protect ---------------------
#
# The earlier `assertRegex(text, "(?i)verified")` was satisfied by the word "unverified" alone, the platform names
# by any mention anywhere, and the unsafe-tool check by the word "not" anywhere in a long line. The checks below
# read one section, one table row or one sentence, and `ArtifactAnchorTests` breaks each on an in-memory copy.

PLATFORM_ROW_STATUS = {  # row prefix in section 2 -> what its Status cell must start with
    "Claude Code (": "**verified**",
    "GitHub Copilot, VS Code (": "**verified**",
    "Opencode (": "**verified**",
    "Gemini CLI (": "**verified**",
    "Cline (": "**verified",
    "Pi (": "**verified**",
}
UNSAFE_SENTENCE_PREFIX = "**Excluded from every set**: `browser_run_code_unsafe`"


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(heading):
            body = [line]
            for nxt in lines[i + 1:]:
                if nxt.startswith("## "):
                    break
                body.append(nxt)
            return "\n".join(body)
    return ""


def platform_row_findings(text: str) -> list[str]:
    table = _section(text, "## 2. Per-platform result")
    found = []
    if "Based on: security-review-t655-fetch-removal-v1.md" not in _section(text, "## Metadata"):
        found.append("the Metadata section does not carry the Based-on line")
    for prefix, status in PLATFORM_ROW_STATUS.items():
        rows = [l for l in table.splitlines() if l.startswith("| " + prefix)]
        if len(rows) != 1:
            found.append(f"section 2 has {len(rows)} rows for {prefix!r}")
            continue
        cell = rows[0].split("|")[2].strip()
        if not cell.startswith(status):
            found.append(f"the {prefix!r} row has status {cell!r}")
    if not any(l.split("|")[2].strip().startswith("**unverified") for l in table.splitlines() if l.startswith("| ")):
        found.append("no row of section 2 is marked unverified")
    return found


def unsafe_tool_findings(text: str) -> list[str]:
    """The artifact names the tool in one sentence of section 4, as the first item of its exclusion list."""
    found = []
    named = [(n, l) for n, l in enumerate(text.splitlines()) if "browser_run_code_unsafe" in l]
    if len(named) != 1:
        return [f"expected one line that names the tool, found {len(named)}"]
    section4 = _section(text, "## 4. The four Playwright grant sets")
    if named[0][1] not in section4.splitlines():
        found.append("the line that names the tool is not in section 4")
    if UNSAFE_SENTENCE_PREFIX not in named[0][1]:
        found.append("the tool is not named as the first item of the 'Excluded from every set' list")
    if re.search(r"(?i)\b(grant|recommend\w*|enable|give)\b", named[0][1].replace("granted", "")):
        found.append("the line that names the tool also recommends or grants it")
    return found


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.text = ARTIFACT.read_text(encoding="utf-8")

    def test_artifact_exists_and_records_every_platform(self):
        self.assertEqual(platform_row_findings(self.text), [])

    def test_artifact_never_recommends_the_unsafe_tool(self):
        # T673: the one line that names the tool is the 'Excluded from every set' sentence of section 4. The
        # earlier test accepted any line holding the word "not" or "no" next to the name (and had a self-check
        # for a pattern, not for the artifact).
        self.assertEqual(unsafe_tool_findings(self.text), [])


class ArtifactAnchorTests(unittest.TestCase):
    def setUp(self):
        self.text = ARTIFACT.read_text(encoding="utf-8")

    def test_unverified_alone_no_longer_stands_for_verified(self):
        # every row's Status cell says verified or unverified; the whole-file regex `(?i)verified` was satisfied
        # by "unverified" in any one of them
        flipped = self.text
        for prefix, status in PLATFORM_ROW_STATUS.items():
            row = next(l for l in self.text.splitlines() if l.startswith("| " + prefix))
            flipped = flipped.replace(row, row.replace(status, "**unverified**", 1), 1)
        self.assertRegex(flipped, r"(?i)verified")  # the old assertion still passes
        self.assertEqual(len(platform_row_findings(flipped)), len(PLATFORM_ROW_STATUS))

    def test_a_platform_named_only_outside_its_row_is_noticed(self):
        for prefix in PLATFORM_ROW_STATUS:
            row = next(l for l in self.text.splitlines() if l.startswith("| " + prefix))
            name = prefix.split(" (")[0]
            moved = self.text.replace(row, "| somebody else " + row[2 + len(prefix):], 1) + f"\n{name} is mentioned here.\n"
            with self.subTest(platform=name):
                self.assertIn(name, moved)  # the old assertIn(platform, text) still passes
                self.assertTrue(platform_row_findings(moved))

    def test_a_missing_based_on_line_is_noticed(self):
        moved = self.text.replace("- Based on: security-review-t655-fetch-removal-v1.md", "- Based on: x")
        moved += "\nBased on: security-review-t655-fetch-removal-v1.md\n"
        self.assertTrue(platform_row_findings(moved))

    def test_a_recommendation_or_a_second_mention_of_the_unsafe_tool_is_noticed(self):
        line = next(l for l in self.text.splitlines() if "browser_run_code_unsafe" in l)
        rec = self.text.replace(line, line + " Grant `browser_run_code_unsafe` to the QA agent, no questions asked.", 1)
        self.assertTrue(unsafe_tool_findings(rec))
        extra = self.text + "\nGrant `browser_run_code_unsafe` to the QA agent; this is not a problem.\n"
        self.assertTrue(unsafe_tool_findings(extra))
        # the old check: a name-less remainder containing 'not' or 'no' passed
        self.assertRegex(extra.splitlines()[-1].replace("browser_run_code_unsafe", ""), r"(?i)\b(never|excluded|not|no)\b")

    def test_the_tool_moved_out_of_the_exclusion_sentence_is_noticed(self):
        moved = self.text.replace(UNSAFE_SENTENCE_PREFIX, "**Excluded from every set**: `browser_evaluate`", 1)
        moved += "\n- not even `browser_run_code_unsafe` is wanted here\n"
        self.assertTrue(unsafe_tool_findings(moved))


if __name__ == "__main__":
    unittest.main()
