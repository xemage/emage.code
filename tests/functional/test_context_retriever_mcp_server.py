"""T495 -- live adversarial test proving `@context-retriever`'s new MCP tool-scoping grant
(`mcp__context-retriever__retrieve` in place of `execute`) genuinely cannot write.

Mirrors `tests/functional/test_context_retriever.py::EndToEndAdversarialWriteProbeTests`'s
discipline one layer out: that class proves T454's module-level API-absence control (layer
2 of ADR-005 Decision 3's three-place `ALLOW_WRITE=false` assertion); this file proves
T495's *tool-scoping* control -- the new dedicated single-tool `stdio` MCP server plus the
new exact-MCP-tool-name grant -- by attempting to call a fabricated write-shaped tool
through the real, un-mocked server process and confirming rejection, and by directly
inspecting the regenerated Claude Code projection.

Covers `docs/tasks/task-T495.md`'s Expected Output 6 / Acceptance Criterion 1:

1. The new server has exactly one callable tool, and that tool has no write/mutate path --
   verified live, not merely asserted (`AdversarialToolScopingProbeTests`).
2. The regenerated Claude Code projection's `tools:` frontmatter no longer contains `Bash`
   anywhere, only the new MCP grant (`ProjectedClaudeCodeAgentGrantTests`).

Runs in two tiers, mirroring this repo's `fastembed`-optional convention
(`tests/functional/test_memory_indexing_pipeline.py`'s own docstring):
`ProjectedClaudeCodeAgentGrantTests` always runs (static file inspection only, no MCP SDK
needed). `AdversarialToolScopingProbeTests` requires the optional `mcp` Python SDK
(`implementation/runtime/memory/requirements-mcp-server.txt`) and skips gracefully when it
is not installed, exactly like `test_memory_indexing_pipeline.py` skips its fastembed-only
cases -- so `python3 tests/run.py` stays runnable with only this repo's stdlib+PyYAML
baseline.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.frontmatter import parse_file  # noqa: E402
from tests._helpers.repo import implementation_root  # noqa: E402
from tests.functional.test_context_retriever import (  # noqa: E402
    _chunk,
    _init_git_repo,
    _write_generated_manifest,
    _write_index_dir,
)

PROJECTED_CLAUDE_AGENT = implementation_root() / ".claude" / "agents" / "context-retriever.md"
SOURCE_AGENT = implementation_root() / "knowledge" / "agents" / "context-retriever.md"
TEST_SERVER_HARNESS = REPO_ROOT / "tests" / "_helpers" / "context_retriever_mcp_test_server.py"
FABRICATED_WRITE_TOOLS = ("write", "execute", "shell", "delete", "save")


def _mcp_sdk_available() -> bool:
    try:
        import mcp  # noqa: F401
        from mcp.server.mcpserver import MCPServer  # noqa: F401
    except ImportError:
        return False
    return True


MCP_AVAILABLE = _mcp_sdk_available()


class ProjectedClaudeCodeAgentGrantTests(unittest.TestCase):
    """Expected Output 6(c) -- direct inspection of the regenerated Claude Code
    projection. No MCP SDK required; always runs.
    """

    def test_projected_agent_exists(self):
        self.assertTrue(PROJECTED_CLAUDE_AGENT.is_file(),
                         msg=f"{PROJECTED_CLAUDE_AGENT} missing -- run `node implementation/"
                             "scripts/sync.mjs --root implementation`")

    def test_projected_tools_frontmatter_has_no_bash_anywhere(self):
        fm, _ = parse_file(PROJECTED_CLAUDE_AGENT)
        tools = {t.strip() for t in (fm.get("tools") or "").split(",") if t.strip()}
        self.assertNotIn("Bash", tools, msg=f"projected agent still grants Bash: {tools}")

    def test_projected_tools_frontmatter_has_the_new_exact_tool_grant(self):
        fm, _ = parse_file(PROJECTED_CLAUDE_AGENT)
        tools = {t.strip() for t in (fm.get("tools") or "").split(",") if t.strip()}
        self.assertIn("mcp__context-retriever__retrieve", tools,
                      msg=f"projected agent missing the new exact-tool-name grant: {tools}")
        self.assertIn("Read", tools)

    def test_source_agent_tools_list_has_no_execute_token(self):
        fm, _ = parse_file(SOURCE_AGENT)
        tools = set(fm.get("tools") or [])
        self.assertNotIn("execute", tools, msg=f"source still grants execute: {tools}")
        self.assertIn("mcp__context-retriever__retrieve", tools)


@unittest.skipUnless(
    MCP_AVAILABLE,
    "mcp SDK not installed -- see implementation/runtime/memory/requirements-mcp-server.txt",
)
class AdversarialToolScopingProbeTests(unittest.TestCase):
    """Acceptance Criterion 1 -- a real subprocess speaking the real MCP `stdio` protocol,
    not a mocked call-argument assertion."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        self.index_dir = self.tmp_path / "index"
        self.workspace = self.tmp_path / "workspace"
        self.platform_root = self.tmp_path / ".claude"
        _write_index_dir(self.index_dir, [_chunk()])
        _init_git_repo(self.workspace, "git@gitlab.com:fixture-org/repo.git")
        _write_generated_manifest(self.platform_root, "claude-code")

    def _server_params(self):
        from mcp import StdioServerParameters
        return StdioServerParameters(
            command=sys.executable,
            args=[str(TEST_SERVER_HARNESS),
                  "--index-dir", str(self.index_dir),
                  "--workspace-root", str(self.workspace),
                  "--platform-root", str(self.platform_root)],
            cwd=str(REPO_ROOT),
        )

    def _run(self, coro_factory):
        import anyio
        return anyio.run(coro_factory)

    def test_server_exposes_exactly_one_tool_named_retrieve(self):
        """(a) start the new server as a real subprocess over stdio."""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    listed = await session.list_tools()
                    return [t.name for t in listed.tools]

        names = self._run(run)
        self.assertEqual(names, ["retrieve"], msg=f"server exposes unexpected tool(s): {names}")

    def test_fabricated_write_shaped_tool_calls_are_rejected(self):
        """(b) attempt to call a tool name other than `retrieve` and confirm the server has
        no such tool and rejects the call."""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            results = {}
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    for verb in FABRICATED_WRITE_TOOLS:
                        results[verb] = await session.call_tool(
                            verb, {"path": "implementation/knowledge/memory/general/pwned.md",
                                   "content": "PWNED", "command": "rm -rf /"})
            return results

        results = self._run(run)
        for verb, result in results.items():
            with self.subTest(fabricated_tool=verb):
                self.assertTrue(result.is_error,
                                 msg=f"fabricated '{verb}' tool call was NOT rejected as an error")
                text = " ".join(getattr(c, "text", "") for c in (result.content or []))
                self.assertIn("Unknown tool", text, msg=f"unexpected rejection reason: {text!r}")

    def test_fabricated_write_tool_calls_produce_zero_filesystem_side_effects(self):
        before = self._snapshot(self.tmp_path)
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    for verb in FABRICATED_WRITE_TOOLS:
                        await session.call_tool(
                            verb, {"path": "implementation/knowledge/memory/general/pwned.md",
                                   "content": "PWNED", "command": "rm -rf /"})

        self._run(run)
        after = self._snapshot(self.tmp_path)
        self.assertEqual(before, after,
                          "filesystem state changed after fabricated write-tool-name calls "
                          "through the real server process")

    def test_the_one_real_tool_still_answers_a_real_query(self):
        """Sanity check: the rejections above are real tool-name scoping, not the server
        being broken outright -- the one real tool still answers a real query end to end."""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool("retrieve", {"query": "generic chunk",
                                                                   "top_k": 5})

        result = self._run(run)
        self.assertFalse(result.is_error, msg=f"real retrieve tool call failed: {result}")
        payload = (result.structured_content or {}).get("result")
        self.assertTrue(payload, "expected at least one result from the fixture chunk")
        self.assertEqual(payload[0]["chunk_id"], "fixture::chunk0")

    @staticmethod
    def _snapshot(root: Path) -> dict:
        return {
            str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file()
        }


class DefaultIndexDirTests(unittest.TestCase):
    """T722 (TD-T671-K5): the index directory is derived from the workspace's own project, not hard-coded."""

    def test_the_directory_follows_the_workspace_remote(self):
        from implementation.runtime.memory.context_retriever import default_index_dir
        cases = {
            "https://gitlab.com/em-age/emage.code.git": "em-age-emage.code",
            "git@gitlab.com:Some-Org/Other.Repo.git": "some-org-other.repo",
            "https://gitlab.example/group/sub/proj_x.git": "sub-proj_x",
        }
        for remote, slug in cases.items():
            with self.subTest(remote=remote), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _init_git_repo(root, remote)
                self.assertEqual(default_index_dir(root),
                                 root / "implementation" / "runtime" / "memory" / "_index" / slug)

    def test_a_workspace_without_a_usable_remote_is_refused(self):
        from implementation.runtime.memory.context_retriever import RemoteResolutionError, default_index_dir
        for remote in (None, "https://gitlab.com/org/re%2Fpo.git", "https://gitlab.com/../repo.git"):
            with self.subTest(remote=remote), tempfile.TemporaryDirectory() as tmp:
                _init_git_repo(Path(tmp), remote)
                with self.assertRaises(RemoteResolutionError):
                    default_index_dir(Path(tmp))

    def test_the_shipped_entry_passes_no_index_dir_and_names_no_project(self):
        import yaml
        servers = yaml.safe_load((implementation_root() / "knowledge" / "mcp" / "servers.yaml").read_text(encoding="utf-8"))
        args = servers["servers"]["context-retriever"]["args"]
        self.assertNotIn("--index-dir", args)
        self.assertNotIn("em-age", " ".join(args))
        for rel in (".mcp.json", ".cline/mcp.json"):
            with self.subTest(file=rel):
                self.assertNotIn("em-age-emage.code", (implementation_root() / rel).read_text(encoding="utf-8"))

    @unittest.skipUnless(MCP_AVAILABLE, "mcp SDK not installed")
    def test_the_server_parser_accepts_a_missing_index_dir(self):
        from implementation.runtime.memory.context_retriever_mcp_server.server import _build_arg_parser
        args = _build_arg_parser().parse_args(["--workspace-root", ".", "--platform-root", ".claude"])
        self.assertIsNone(args.index_dir)


# T790 (QA-T760-03): generated config -> (wrapper key, the platform folder the entry must pass, its platform).
PLATFORM_ROOT_PER_CONFIG = {
    ".mcp.json": ("mcpServers", ".claude", "claude-code"),
    ".cline/mcp.json": ("mcpServers", ".cline", "cline"),
    ".opencode/opencode.json": ("mcp", ".opencode", "opencode"),
}


def _generated_args(rel: str, wrapper: str) -> list[str]:
    import json
    entry = json.loads((implementation_root() / rel).read_text(encoding="utf-8"))[wrapper]["context-retriever"]
    return entry["args"] if "args" in entry else entry["command"][1:]


class PlatformRootPerPlatformTests(unittest.TestCase):
    """T790 (QA-T760-03): every generated entry passed `--platform-root .claude`, so on an install without
    `.claude/` the server started and `retrieve` failed at the first query."""

    def test_each_generated_entry_passes_its_own_platform_folder(self):
        from implementation.runtime.memory.context_retriever import resolve_platform
        for rel, (wrapper, folder, platform) in PLATFORM_ROOT_PER_CONFIG.items():
            with self.subTest(config=rel):
                args = _generated_args(rel, wrapper)
                self.assertEqual(args.count("--platform-root"), 1)
                self.assertEqual(args[args.index("--platform-root") + 1], folder)
                self.assertNotIn("{{", " ".join(args))
                self.assertEqual(resolve_platform(implementation_root() / folder), platform)

    def test_the_source_names_no_platform_folder(self):
        import yaml
        servers = yaml.safe_load((implementation_root() / "knowledge" / "mcp" / "servers.yaml").read_text(encoding="utf-8"))
        args = servers["servers"]["context-retriever"]["args"]
        self.assertEqual(args[args.index("--platform-root") + 1], "{{platformDir}}")

    def test_a_platform_folder_without_a_manifest_still_fails_closed(self):
        import implementation.runtime.memory.context_retriever as cr
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _init_git_repo(workspace, "git@gitlab.com:fixture-org/repo.git")
            _write_generated_manifest(workspace / ".claude", "claude-code")
            (workspace / ".cline").mkdir()
            with self.assertRaises(cr.PlatformResolutionError):
                cr.resolve_platform(workspace / ".cline")
            with self.assertRaises(cr.PlatformResolutionError):
                cr.derive_requesting_context(workspace, workspace / ".cline")
            with self.assertRaises(cr.PlatformResolutionError):
                cr.derive_requesting_context(workspace, workspace / ".opencode")


class PlatformDirPlaceholderGeneratorTests(unittest.TestCase):
    """The generator mechanism behind it: a whole `{{platformDir}}` argument becomes the output folder of
    the platform being generated; anything else that looks like a placeholder stops the run."""

    SERVERS = "\n".join([
        "servers:",
        "  probe:", "    tags: [core]", "    transport: stdio", "    command: python3",
        '    args: ["-m", "probe", "--platform-root", "ARG", "100.{64,65}.*"]', "",
    ])
    OUTPUTS = {".mcp.json": ("mcpServers", ".claude"), ".cline/mcp.json": ("mcpServers", ".cline"),
               ".opencode/opencode.json": ("mcp", ".opencode"), ".vscode/mcp.json": ("servers", ".github")}

    def _run_sync(self, arg: str, edit_manifest=None):
        import json
        import shutil
        import subprocess
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        impl = implementation_root()
        root = Path(tempfile.mkdtemp(prefix="t790-sync-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        shutil.copytree(impl / "platforms", root / "platforms")
        shutil.copytree(impl / "_extras", root / "_extras")
        for kind in ("mcp", "agents", "commands", "instructions", "skills"):
            (root / "knowledge" / kind).mkdir(parents=True)
        (root / "knowledge" / "mcp" / "servers.yaml").write_text(self.SERVERS.replace("ARG", arg), encoding="utf-8")
        if edit_manifest:
            path = root / "platforms" / "cline.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            edit_manifest(manifest)
            path.write_text(json.dumps(manifest), encoding="utf-8")
        proc = subprocess.run(["node", str(impl / "scripts" / "sync.mjs"), "--root", str(root)],
                              capture_output=True, text=True, check=False)
        return root, proc

    def _assert_refused(self, root: Path, proc, needle: str) -> None:
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn(needle, proc.stderr)
        written = [p.name for p in root.iterdir() if p.name not in {"platforms", "_extras", "knowledge"}]
        self.assertEqual(written, [], "nothing may be written when the run is refused")

    def test_the_placeholder_becomes_the_output_folder_of_each_platform(self):
        import json
        root, proc = self._run_sync("{{platformDir}}")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for rel, (wrapper, folder) in self.OUTPUTS.items():
            with self.subTest(config=rel):
                entry = json.loads((root / rel).read_text(encoding="utf-8"))[wrapper]["probe"]
                args = entry["args"] if "args" in entry else entry["command"][1:]
                self.assertEqual(args, ["-m", "probe", "--platform-root", folder, "100.{64,65}.*"])
                self.assertTrue((root / folder / ".generated-manifest.json").is_file())

    def test_an_unknown_or_embedded_placeholder_is_refused_before_any_write(self):
        for arg in ("{{platformdir}}", "{{platformDir}}/x", "x{{platformDir}}", "{{outputDir}}", "{{platformDir}"):
            with self.subTest(arg=arg):
                root, proc = self._run_sync(arg)
                self._assert_refused(root, proc, "probe.args has an unknown placeholder")

    def test_an_output_folder_that_is_not_one_plain_dot_folder_is_refused(self):
        for bad in ("cline", ".cline/sub", ".Cline"):
            with self.subTest(output_dir=bad):
                root, proc = self._run_sync("{{platformDir}}", lambda m, bad=bad: m.update(outputDir=bad))
                self._assert_refused(root, proc, "is not one plain dot-folder name")


if __name__ == "__main__":
    unittest.main()
