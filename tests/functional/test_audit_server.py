"""T497 -- tests for the `security-audit` MCP server implementing
`docs/artifacts/security-engineer-audit-server-design-v1.md` (T496).

Mirrors `tests/functional/test_context_retriever_mcp_server.py`'s (T495) discipline and
runs in three tiers:

1. `CommandsArgvUnitTests` -- pure unit tests of each `commands.build_*_argv()` function.
   No subprocess, no MCP SDK, always runs. Proves the exact `argv` shape per §2.1-§2.4 and
   that a malicious `pattern`/path value occupies exactly one list element (a
   construction-level proof, not yet a real-subprocess proof).
2. `StructuralInvariantTests` / `ServersYamlEntryTests` / `ProjectedClaudeCodeAgentGrantTests`
   -- static file/text inspection, no subprocess, no MCP SDK, always runs. Proves the
   acceptance criteria that are "verifiable by reading the module directly" rather than by
   a live call: exactly four `@server.tool()` registrations, `executor.py` as the sole
   `subprocess.run` call site with `shell=False` appearing exactly once package-wide, the
   registry entry, and the regenerated Claude Code projection.
3. `AdversarialToolScopingProbeTests` -- a real subprocess speaking the real MCP `stdio`
   protocol against the real, unmodified `audit_server.build_server()`/`main()` code path.
   Requires the optional `mcp` Python SDK (`implementation/runtime/security/
   requirements-mcp-server.txt`) and skips gracefully when it is not installed, exactly
   like T495's own adversarial test class. Individual sub-tests that additionally need a
   real external binary this environment lacks (`pip-audit`, confirmed absent this
   session) skip with a clear reason rather than fabricating a pass; sub-tests exercising
   `rg`/`npm`/`dotnet` (confirmed present this session) run for real.
"""
from __future__ import annotations

import ast
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from tests._helpers.frontmatter import parse_file  # noqa: E402
from tests._helpers.repo import implementation_root, knowledge_root  # noqa: E402

from implementation.runtime.security import commands  # noqa: E402
from implementation.runtime.security.validation import PathValidationError  # noqa: E402

SECURITY_PKG_DIR = implementation_root() / "runtime" / "security"
AUDIT_SERVER_PY = SECURITY_PKG_DIR / "audit_server.py"
COMMANDS_PY = SECURITY_PKG_DIR / "commands.py"
EXECUTOR_PY = SECURITY_PKG_DIR / "executor.py"
VALIDATION_PY = SECURITY_PKG_DIR / "validation.py"

SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"
SOURCE_AGENT = knowledge_root() / "agents" / "security-engineer.md"
PROJECTED_CLAUDE_AGENT = implementation_root() / ".claude" / "agents" / "security-engineer.md"

EXPECTED_TOOL_NAMES = (
    "run_npm_audit",
    "run_pip_audit",
    "run_dotnet_list_vulnerable",
    "grep_content",
)
FABRICATED_TOOLS = ("execute", "run_command", "shell", "eval", "bash")


def _which(binary: str) -> bool:
    return shutil.which(binary) is not None


def _tool_result_dict(result) -> dict:
    """Extract the tool's returned dict from an MCP `CallToolResult`.

    This SDK version (`mcp==2.2.0`) does not populate `structured_content` for a plain
    `dict`-returning tool function -- the result comes back as a single `TextContent`
    block whose `.text` is the JSON-serialized dict. Verified directly against a real
    call this session, not assumed from documentation.
    """
    import json

    texts = [getattr(c, "text", None) for c in (result.content or [])]
    texts = [t for t in texts if t is not None]
    assert texts, f"expected at least one text content block, got: {result}"
    return json.loads(texts[0])


def _mcp_sdk_available() -> bool:
    try:
        import mcp  # noqa: F401
        from mcp.server.mcpserver import MCPServer  # noqa: F401
    except ImportError:
        return False
    return True


MCP_AVAILABLE = _mcp_sdk_available()


# ---------------------------------------------------------------------------
# 1. Pure argv-construction unit tests -- no subprocess, no I/O beyond path stat.
# ---------------------------------------------------------------------------

class CommandsArgvUnitTests(unittest.TestCase):
    """§2.1-§2.4: exact `argv` shape, and injection-hazard proof at the
    construction level (a malicious value occupies exactly one list element)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_build_npm_audit_argv_exact_shape(self):
        pkg_dir = self.root / "svc"
        pkg_dir.mkdir()
        (pkg_dir / "package.json").write_text("{}")
        argv, cwd = commands.build_npm_audit_argv(str(pkg_dir), allowed_root=self.root)
        self.assertEqual(argv, ["npm", "audit", "--json"])
        self.assertEqual(Path(cwd), pkg_dir.resolve())
        # package_json_dir never enters argv at all.
        self.assertNotIn(str(pkg_dir), argv)

    def test_build_npm_audit_argv_rejects_missing_package_json(self):
        pkg_dir = self.root / "no-pkg"
        pkg_dir.mkdir()
        with self.assertRaises(PathValidationError):
            commands.build_npm_audit_argv(str(pkg_dir), allowed_root=self.root)

    def test_build_npm_audit_argv_rejects_path_outside_allowed_root(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        (outside / "package.json").write_text("{}")
        with self.assertRaises(PathValidationError):
            commands.build_npm_audit_argv(str(outside), allowed_root=self.root)

    def test_build_pip_audit_argv_exact_shape(self):
        req = self.root / "requirements.txt"
        req.write_text("flask==3.0.0\n")
        argv = commands.build_pip_audit_argv(str(req), allowed_root=self.root)
        self.assertEqual(argv, ["pip-audit", "--format", "json", "-r", str(req.resolve())])

    def test_build_pip_audit_argv_rejects_directory(self):
        with self.assertRaises(PathValidationError):
            commands.build_pip_audit_argv(str(self.root), allowed_root=self.root)

    def test_build_dotnet_list_vulnerable_argv_exact_shape(self):
        sln = self.root / "app.sln"
        sln.write_text("")
        argv = commands.build_dotnet_list_vulnerable_argv(str(sln), allowed_root=self.root)
        self.assertEqual(
            argv,
            ["dotnet", "list", str(sln.resolve()), "package", "--vulnerable", "--format", "json"],
        )

    def test_build_dotnet_list_vulnerable_argv_rejects_bad_extension(self):
        bad = self.root / "notes.txt"
        bad.write_text("")
        with self.assertRaises(PathValidationError):
            commands.build_dotnet_list_vulnerable_argv(str(bad), allowed_root=self.root)

    def test_build_grep_content_argv_exact_shape(self):
        argv, cwd = commands.build_grep_content_argv(
            "TODO", "*.py", str(self.root), allowed_root=self.root
        )
        self.assertEqual(
            argv,
            [
                "rg", "--json", "--no-follow", "--max-filesize", "5M",
                "-e", "TODO",
                "--glob", "*.py",
                str(self.root.resolve()),
            ],
        )
        self.assertEqual(Path(cwd), self.root.resolve())

    def test_build_grep_content_argv_malicious_pattern_is_one_literal_argv_element(self):
        """Construction-level proof (see `AdversarialToolScopingProbeTests` below for the
        real-subprocess proof): a shell-metacharacter-laden pattern occupies exactly one
        `argv` element -- it is never split, concatenated, or interpreted."""
        malicious = "; rm -rf / #"
        argv, _ = commands.build_grep_content_argv(
            malicious, "*.py", str(self.root), allowed_root=self.root
        )
        self.assertIn(malicious, argv)
        self.assertEqual(argv.count(malicious), 1)
        self.assertEqual(len([a for a in argv if ";" in a]), 1)

    def test_build_grep_content_argv_rejects_oversized_pattern(self):
        with self.assertRaises(ValueError):
            commands.build_grep_content_argv(
                "x" * (commands.MAX_PATTERN_LENGTH + 1), "*.py", str(self.root),
                allowed_root=self.root,
            )

    def test_build_grep_content_argv_rejects_oversized_glob(self):
        with self.assertRaises(ValueError):
            commands.build_grep_content_argv(
                "TODO", "x" * (commands.MAX_GLOB_LENGTH + 1), str(self.root),
                allowed_root=self.root,
            )

    def test_build_grep_content_argv_rejects_root_dir_traversal(self):
        with self.assertRaises(PathValidationError):
            commands.build_grep_content_argv(
                "TODO", "*.py", str(self.root / ".." / ".." / "etc"), allowed_root=self.root,
            )


# ---------------------------------------------------------------------------
# 2. Static structural invariants -- no subprocess, no MCP SDK, always runs.
#
# These use `ast` (not substring/text scanning) specifically so a prose mention of
# "subprocess.run(" or "shell=True" inside a docstring (this package's own module
# docstrings discuss both, by design, to explain the invariants) can never masquerade as
# or hide real code -- only actual AST `Call`/decorator nodes are counted.
# ---------------------------------------------------------------------------

def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _tool_decorated_function_names(tree: ast.Module) -> list[str]:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Call)
                        and isinstance(dec.func, ast.Attribute)
                        and dec.func.attr == "tool"):
                    names.append(node.name)
    return names


def _subprocess_run_calls(tree: ast.Module) -> list[ast.Call]:
    calls = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"):
            calls.append(node)
    return calls


def _kwarg_bool_values(call_node: ast.Call, kwarg_name: str) -> list[bool]:
    values = []
    for kw in call_node.keywords:
        if kw.arg == kwarg_name and isinstance(kw.value, ast.Constant):
            values.append(kw.value.value)
    return values


class StructuralInvariantTests(unittest.TestCase):
    """Acceptance criteria verifiable "by reading the module directly (structural, not
    just a claim)"."""

    def test_audit_server_registers_exactly_four_tools_and_no_generic_execute(self):
        tree = _parse(AUDIT_SERVER_PY)
        tool_names = _tool_decorated_function_names(tree)
        self.assertEqual(sorted(tool_names), sorted(EXPECTED_TOOL_NAMES),
                          msg=f"audit_server.py must register exactly the four named "
                              f"tools, no more, no fewer (found {sorted(tool_names)})")
        self.assertNotIn("run_command", tool_names)
        self.assertNotIn("execute", tool_names)

    def test_only_executor_calls_subprocess_run(self):
        for path in (AUDIT_SERVER_PY, COMMANDS_PY, VALIDATION_PY):
            tree = _parse(path)
            calls = _subprocess_run_calls(tree)
            self.assertEqual(calls, [], msg=f"{path} must never call subprocess.run directly")
            imports_subprocess = any(
                isinstance(n, ast.Import) and any(a.name == "subprocess" for a in n.names)
                for n in ast.walk(tree)
            )
            self.assertFalse(imports_subprocess, msg=f"{path} must not import subprocess at all")
        executor_calls = _subprocess_run_calls(_parse(EXECUTOR_PY))
        self.assertEqual(len(executor_calls), 1,
                          msg="executor.py must call subprocess.run exactly once")

    def test_executor_subprocess_run_call_has_shell_false_and_check_false(self):
        executor_calls = _subprocess_run_calls(_parse(EXECUTOR_PY))
        self.assertEqual(len(executor_calls), 1)
        call = executor_calls[0]
        self.assertEqual(_kwarg_bool_values(call, "shell"), [False],
                          msg="the one subprocess.run call must set shell=False as a "
                              "literal keyword argument")
        self.assertEqual(_kwarg_bool_values(call, "check"), [False],
                          msg="the one subprocess.run call must set check=False as a "
                              "literal keyword argument (non-zero exit is a valid finding)")

    def test_no_call_anywhere_in_package_sets_shell_true(self):
        for path in SECURITY_PKG_DIR.glob("*.py"):
            for node in ast.walk(_parse(path)):
                if isinstance(node, ast.Call):
                    self.assertNotIn(True, _kwarg_bool_values(node, "shell"),
                                      msg=f"{path} has a call setting shell=True")


class ServersYamlEntryTests(unittest.TestCase):
    """§3: the new `security-audit` entry, and non-interference with other entries."""

    def setUp(self):
        self.data = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))

    def test_security_audit_entry_matches_design_exactly(self):
        entry = self.data["servers"]["security-audit"]
        self.assertEqual(entry["tags"], ["extended"])
        self.assertEqual(entry["transport"], "stdio")
        self.assertEqual(entry["command"], "python3")
        self.assertEqual(entry["args"], ["-m", "implementation.runtime.security.audit_server"])
        self.assertNotIn("env", entry)

    def test_other_entries_untouched_sample(self):
        # Spot-check a couple of pre-existing entries to catch an accidental drive-by
        # edit (the disclosed filesystem/git package-name defects must remain as-is).
        fs = self.data["servers"]["filesystem"]
        self.assertEqual(fs["args"], ["-y", "@anthropic/mcp-filesystem"])
        git = self.data["servers"]["git"]
        self.assertEqual(git["args"], ["-y", "@modelcontextprotocol/mcp-git"])
        ctx = self.data["servers"]["context-retriever"]
        self.assertEqual(ctx["command"], "python3")


class ProjectedClaudeCodeAgentGrantTests(unittest.TestCase):
    """§3's illustrative Claude Code grant, applied to `security-engineer.md`, and its
    regenerated projection. No MCP SDK required; always runs."""

    def test_source_agent_tools_list_has_no_execute_token(self):
        fm, _ = parse_file(SOURCE_AGENT)
        tools = set(fm.get("tools") or [])
        self.assertNotIn("execute", tools, msg=f"source still grants execute: {tools}")
        for tool_name in EXPECTED_TOOL_NAMES:
            self.assertIn(f"mcp__security-audit__{tool_name}", tools)
        self.assertIn("read", tools)
        self.assertIn("search", tools)
        self.assertIn("web", tools)
        self.assertIn("mcp__fetch", tools)

    def test_projected_agent_exists(self):
        self.assertTrue(PROJECTED_CLAUDE_AGENT.is_file(),
                         msg=f"{PROJECTED_CLAUDE_AGENT} missing -- run `node implementation/"
                             "scripts/sync.mjs --root implementation`")

    def test_projected_tools_frontmatter_has_no_bash_anywhere(self):
        fm, _ = parse_file(PROJECTED_CLAUDE_AGENT)
        tools = {t.strip() for t in (fm.get("tools") or "").split(",") if t.strip()}
        self.assertNotIn("Bash", tools, msg=f"projected agent still grants Bash: {tools}")

    def test_projected_tools_frontmatter_has_the_four_exact_tool_grants(self):
        fm, _ = parse_file(PROJECTED_CLAUDE_AGENT)
        tools = {t.strip() for t in (fm.get("tools") or "").split(",") if t.strip()}
        for tool_name in EXPECTED_TOOL_NAMES:
            self.assertIn(f"mcp__security-audit__{tool_name}", tools,
                          msg=f"projected agent missing {tool_name} grant: {tools}")
        self.assertIn("Read", tools)


# ---------------------------------------------------------------------------
# 3. Live adversarial subprocess-over-stdio proof.
# ---------------------------------------------------------------------------

@unittest.skipUnless(
    MCP_AVAILABLE,
    "mcp SDK not installed -- see implementation/runtime/security/requirements-mcp-server.txt",
)
class AdversarialToolScopingProbeTests(unittest.TestCase):
    """Acceptance criteria requiring a real subprocess speaking the real MCP `stdio`
    protocol against the real, unmodified `audit_server` entrypoint -- not a mocked
    call-argument assertion."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name).resolve()

    def _server_params(self):
        from mcp import StdioServerParameters
        return StdioServerParameters(
            command=sys.executable,
            args=["-m", "implementation.runtime.security.audit_server",
                  "--allowed-root", str(self.workspace)],
            cwd=str(REPO_ROOT),
        )

    def _run(self, coro_factory):
        import anyio
        return anyio.run(coro_factory)

    # -- (c) exactly the four named tools are registered/callable, nothing else. --

    def test_server_exposes_exactly_the_four_named_tools(self):
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    listed = await session.list_tools()
                    return sorted(t.name for t in listed.tools)

        names = self._run(run)
        self.assertEqual(names, sorted(EXPECTED_TOOL_NAMES),
                          msg=f"server exposes unexpected tool(s): {names}")

    def test_fabricated_generic_tool_calls_are_rejected(self):
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            results = {}
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    for verb in FABRICATED_TOOLS:
                        results[verb] = await session.call_tool(
                            verb, {"command": "rm -rf /", "pattern": ".*"})
            return results

        results = self._run(run)
        for verb, result in results.items():
            with self.subTest(fabricated_tool=verb):
                self.assertTrue(result.is_error,
                                 msg=f"fabricated '{verb}' tool call was NOT rejected")
                text = " ".join(getattr(c, "text", "") for c in (result.content or []))
                self.assertIn("Unknown tool", text, msg=f"unexpected rejection reason: {text!r}")

    # -- (b) a malicious parameter value reaches the real command as one literal argv
    #    element, never shell-interpreted -- proved via a real rg subprocess. --

    @unittest.skipUnless(_which("rg"), "rg binary not installed in this environment")
    def test_malicious_grep_pattern_never_shell_interpreted(self):
        (self.workspace / "f.txt").write_text("hello world\n")
        marker = Path(tempfile.gettempdir()) / f"t497-proof-marker-{uuid.uuid4().hex}.txt"
        self.addCleanup(lambda: marker.exists() and marker.unlink())
        self.assertFalse(marker.exists())
        # If this string were ever handed to a shell, the command substitution / chained
        # command below would create `marker`. Delivered as one literal argv element to
        # `rg` (shell=False), it is only ever a regex to search FOR.
        payload = f"nomatch$(touch {marker})nomatch; touch {marker} #"

        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "grep_content",
                        {"pattern": payload, "path_glob": "*.txt",
                         "root_dir": str(self.workspace)})

        result = self._run(run)
        self.assertFalse(marker.exists(),
                          "malicious pattern reached a shell and created the proof marker "
                          "-- command injection succeeded")
        # rg ran (found no match for this bizarre pattern) rather than crashing; the
        # tool call itself is not an MCP-protocol error.
        self.assertFalse(result.is_error, msg=f"grep_content call unexpectedly errored: "
                                               f"{result}")

    @unittest.skipUnless(_which("rg"), "rg binary not installed in this environment")
    def test_grep_content_still_answers_a_real_legitimate_query(self):
        """Sanity check: the rejections/non-injection above are real scoping/safety
        behavior, not the server being broken outright."""
        (self.workspace / "f.txt").write_text("hello world\n")

        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "grep_content",
                        {"pattern": "hello", "path_glob": "*.txt",
                         "root_dir": str(self.workspace)})

        result = self._run(run)
        self.assertFalse(result.is_error, msg=f"real grep_content call failed: {result}")
        inner = _tool_result_dict(result)
        self.assertEqual(inner.get("exit_code"), 0)
        self.assertIn("hello", inner.get("stdout") or "")

    def test_grep_content_root_dir_traversal_is_rejected_live(self):
        """Live proof that path-validation, not just argv-construction, actually runs
        inside the real server process for a real caller-supplied traversal attempt."""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "grep_content",
                        {"pattern": "root", "path_glob": "*", "root_dir": "/etc"})

        result = self._run(run)
        self.assertTrue(result.is_error,
                         msg="root_dir='/etc' (outside allowed_root) was NOT rejected")

    # -- Real end-to-end exercise of the other three tools where binaries are present. --

    @unittest.skipUnless(_which("npm"), "npm binary not installed in this environment")
    def test_run_npm_audit_end_to_end(self):
        pkg_dir = self.workspace / "svc"
        pkg_dir.mkdir()
        (pkg_dir / "package.json").write_text('{"name": "t497-fixture", "version": "1.0.0"}')

        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "run_npm_audit", {"package_json_dir": str(pkg_dir)})

        result = self._run(run)
        self.assertFalse(result.is_error, msg=f"run_npm_audit call failed: {result}")

    @unittest.skipUnless(_which("dotnet"), "dotnet binary not installed in this environment")
    def test_run_dotnet_list_vulnerable_end_to_end(self):
        proj = self.workspace / "app.csproj"
        proj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
            '<TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>'
        )

        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "run_dotnet_list_vulnerable", {"project_or_solution_path": str(proj)})

        result = self._run(run)
        self.assertFalse(result.is_error, msg=f"run_dotnet_list_vulnerable call failed: "
                                               f"{result}")

    @unittest.skipUnless(_which("pip-audit"), "pip-audit binary not installed in this "
                                               "environment (confirmed absent T497 session)")
    def test_run_pip_audit_end_to_end(self):  # pragma: no cover - skipped this session
        req = self.workspace / "requirements.txt"
        req.write_text("requests==2.31.0\n")

        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "run_pip_audit", {"requirements_path": str(req)})

        result = self._run(run)
        self.assertFalse(result.is_error, msg=f"run_pip_audit call failed: {result}")

    def test_run_pip_audit_missing_binary_surfaces_structured_error_not_a_crash(self):
        """`pip-audit` is confirmed absent in this session's environment -- this proves
        the FileNotFoundError-handling addition in `executor.py` (disclosed in that
        module's docstring) for real, rather than skipping `run_pip_audit` coverage
        entirely just because the binary isn't installed here."""
        if _which("pip-audit"):
            self.skipTest("pip-audit IS installed in this environment -- this test only "
                           "proves the missing-binary path, see test_run_pip_audit_end_to_end")
        req = self.workspace / "requirements.txt"
        req.write_text("requests==2.31.0\n")

        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        async def run():
            async with stdio_client(self._server_params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "run_pip_audit", {"requirements_path": str(req)})

        result = self._run(run)
        # A missing binary must surface as a normal, structured tool result (not an
        # MCP-protocol error / unhandled crash).
        self.assertFalse(result.is_error,
                          msg=f"missing-binary case crashed instead of a structured "
                              f"error result: {result}")
        inner = _tool_result_dict(result)
        self.assertIn("error", inner)
        self.assertIn("executable not found", inner.get("error") or "")


if __name__ == "__main__":
    unittest.main()
