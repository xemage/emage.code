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
import os
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


def _required_unless_missing(condition: bool, reason: str):
    """`skipUnless` locally; under CI (env `CI` set) a missing dependency FAILS the test.

    The CI `unit-tests` job installs ripgrep and `mcp==2.2.0`, so these tests must run
    there; a silent skip would hide a broken job image (SEC-T675-04).
    """
    if os.environ.get("CI"):
        return lambda item: item
    return unittest.skipUnless(condition, reason)


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
                "--iglob", "!**/.env*", "--iglob", "!**/*.env", "--iglob", "!**/*.pem",
                "--iglob", "!**/*.key", "--iglob", "!**/id_rsa*", "--iglob", "!**/id_ed25519*",
                "--iglob", "!**/credentials.json", "--iglob", "!**/secrets.y*ml", "--iglob", "!**/.git",
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
        # edit. The filesystem/git entries carry the T638 corrected, pinned launchers
        # (docs/artifacts/mcp-server-packages-v1.md, audit SEC-002).
        fs = self.data["servers"]["filesystem"]
        self.assertEqual(fs["command"], "npx")
        self.assertEqual(fs["args"], ["-y", "@modelcontextprotocol/server-filesystem@1.0.0", "."])
        git = self.data["servers"]["git"]
        self.assertEqual(git["command"], "uvx")
        self.assertEqual(git["args"], ["mcp-server-git@2026.10.10", "--repository", "."])
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
        self.assertNotIn("mcp__fetch", tools)  # T655: the fetch server is removed

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

@_required_unless_missing(
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

    @_required_unless_missing(_which("rg"), "rg binary not installed in this environment")
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

    @_required_unless_missing(_which("rg"), "rg binary not installed in this environment")
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

    @_required_unless_missing(_which("rg"), "rg binary not installed in this environment")
    def test_extra_root_flag_lets_the_live_server_scan_a_worktree_but_not_its_env_file(self):
        """T675: a root given at launch (`--extra-root`) is searchable; its `.env` is not; a
        third directory is still rejected."""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        worktree = Path(self.tmp.name).resolve().parent / f"audit-worktree-{uuid.uuid4().hex}"
        worktree.mkdir()
        self.addCleanup(shutil.rmtree, worktree, True)
        (worktree / "code.txt").write_text("needle\n")
        (worktree / ".env").write_text("needle\n")
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "implementation.runtime.security.audit_server",
                  "--allowed-root", str(self.workspace), "--extra-root", str(worktree)],
            cwd=str(REPO_ROOT),
        )

        async def run():
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    ok = await session.call_tool(
                        "grep_content",
                        {"pattern": "needle", "path_glob": "**/*", "root_dir": str(worktree)})
                    denied = await session.call_tool(
                        "grep_content",
                        {"pattern": "needle", "path_glob": "**/*", "root_dir": "/etc"})
                    return ok, denied

        ok, denied = self._run(run)
        self.assertFalse(ok.is_error, msg=f"{ok}")
        stdout = _tool_result_dict(ok).get("stdout") or ""
        self.assertIn("code.txt", stdout)
        self.assertNotIn(".env", stdout)
        self.assertTrue(denied.is_error)

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


# ---------------------------------------------------------------------------
# 4. T675 (SEC-T650-05): extra roots for a git worktree, and no `.env*` search.
# ---------------------------------------------------------------------------

import json  # noqa: E402
import subprocess  # noqa: E402

from implementation.runtime.security import executor  # noqa: E402
from implementation.runtime.security.validation import (  # noqa: E402
    parse_extra_roots,
    parse_worktree_list,
)


def _rg_paths(argv: list[str]) -> set[str]:
    """Run the built `argv` for real and return the matched file names."""
    out = executor.run_fixed_argv(argv)
    names = set()
    for line in (out.get("stdout") or "").splitlines():
        event = json.loads(line)
        if event.get("type") == "match":
            names.add(Path(event["data"]["path"]["text"]).name)
    return names


@_required_unless_missing(_which("rg"), "rg binary not installed in this environment")
class GrepContentNeverSearchesEnvFilesTests(unittest.TestCase):
    """The deny globs keep every `.env*` file out of `grep_content`, whatever `path_glob` says."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / "sub").mkdir()
        (self.root / ".gitignore").write_text(".env*\n")  # ignored, like a local .env
        for name in (".env", ".env.local", "sub/.ENV", "sub/.env.production", "sub/ok.txt"):
            (self.root / name).write_text("MARKER=1\n")
        (self.root / ".envdir").mkdir()
        (self.root / ".envdir" / "inside.txt").write_text("MARKER=1\n")

    def _grep(self, glob: str) -> set[str]:
        argv, _ = commands.build_grep_content_argv("MARKER", glob, str(self.root), allowed_root=self.root)
        return _rg_paths(argv)

    def test_wildcard_glob_finds_only_the_non_env_file(self):
        for glob in ("**/*", "*", ".env*", ".env", "**/.env.*", "!nothing"):
            with self.subTest(glob=glob):
                self.assertEqual(self._grep(glob) - {"ok.txt"}, set())

    def test_the_search_itself_works(self):
        self.assertEqual(self._grep("**/*"), {"ok.txt"})

    def test_deny_globs_come_after_the_callers_glob(self):
        argv, _ = commands.build_grep_content_argv("x", "**/*", str(self.root), allowed_root=self.root)
        self.assertGreater(argv.index("--iglob"), argv.index("--glob"))
        self.assertEqual(argv[-1], str(self.root))


class ExtraRootsTests(unittest.TestCase):
    """Launch-time extra roots (a worktree) are accepted; escapes from any root are not."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.root = base / "primary"
        self.worktree = base / "worktrees" / "agent-x"
        self.other = base / "elsewhere"
        for d in (self.root, self.worktree, self.other):
            d.mkdir(parents=True)

    def test_a_directory_outside_the_primary_root_is_rejected_without_extra_roots(self):
        with self.assertRaises(PathValidationError):
            commands.build_grep_content_argv("x", "*", str(self.worktree), allowed_root=self.root)

    def test_a_worktree_extra_root_is_accepted(self):
        argv, cwd = commands.build_grep_content_argv(
            "x", "*", str(self.worktree), allowed_root=self.root, extra_roots=[self.worktree]
        )
        self.assertEqual(Path(cwd), self.worktree)
        self.assertEqual(argv[-1], str(self.worktree))

    def test_a_sibling_of_the_extra_root_is_still_rejected(self):
        with self.assertRaises(PathValidationError):
            commands.build_grep_content_argv(
                "x", "*", str(self.other), allowed_root=self.root, extra_roots=[self.worktree]
            )

    def test_traversal_and_symlink_escapes_from_an_extra_root_are_rejected(self):
        with self.assertRaises(PathValidationError):
            commands.build_grep_content_argv(
                "x", "*", str(self.worktree / ".." / "elsewhere"),
                allowed_root=self.root, extra_roots=[self.worktree],
            )
        (self.worktree / "link").symlink_to(self.other)
        with self.assertRaises(PathValidationError):
            commands.build_grep_content_argv(
                "x", "*", str(self.worktree / "link"), allowed_root=self.root, extra_roots=[self.worktree],
            )

    def test_the_other_three_builders_accept_the_extra_root_too(self):
        (self.worktree / "package.json").write_text("{}")
        (self.worktree / "r.txt").write_text("")
        (self.worktree / "a.csproj").write_text("")
        kwargs = {"allowed_root": self.root, "extra_roots": [self.worktree]}
        self.assertEqual(commands.build_npm_audit_argv(str(self.worktree), **kwargs)[1], str(self.worktree))
        self.assertIn(str(self.worktree / "r.txt"), commands.build_pip_audit_argv(str(self.worktree / "r.txt"), **kwargs))
        self.assertIn(
            str(self.worktree / "a.csproj"),
            commands.build_dotnet_list_vulnerable_argv(str(self.worktree / "a.csproj"), **kwargs),
        )

    def test_parse_extra_roots_refuses_the_filesystem_root_and_missing_directories(self):
        self.assertEqual(parse_extra_roots([str(self.worktree), ""]), [self.worktree])
        for bad in ("/", str(self.worktree / "missing")):
            with self.subTest(root=bad), self.assertRaises(PathValidationError):
                parse_extra_roots([bad])

    def test_parse_worktree_list_keeps_only_existing_absolute_directories(self):
        porcelain = (
            f"worktree {self.root}\nHEAD abc\nbranch refs/heads/develop\n\n"
            f"worktree {self.worktree}\nHEAD def\ndetached\n\n"
            f"worktree {self.root / 'gone'}\nHEAD 000\nprunable gitdir file points to non-existent location\n\n"
            'worktree "/odd\\nname"\n\nworktree relative/path\n'
        )
        self.assertEqual(parse_worktree_list(porcelain), [self.root, self.worktree])


@_required_unless_missing(MCP_AVAILABLE and _which("git"), "needs the mcp SDK and git")
class GitWorktreeRootsTests(unittest.TestCase):
    """`--allow-git-worktrees` reads the worktree list of the allowed root's repository."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.repo = base / "repo"
        self.repo.mkdir()
        env_free = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
        for args in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", "init"]):
            subprocess.run([*env_free, "-C", str(self.repo), *args], check=True, capture_output=True)
        self.worktree = base / "worktrees" / "wt"
        subprocess.run(
            [*env_free, "-C", str(self.repo), "worktree", "add", "-q", "--detach", str(self.worktree)],
            check=True, capture_output=True,
        )

    def test_git_worktree_roots_lists_the_linked_worktree(self):
        from implementation.runtime.security import audit_server
        self.assertIn(self.worktree, audit_server.git_worktree_roots(self.repo))

    def test_a_subdirectory_as_allowed_root_does_not_admit_the_repository_root(self):
        """SEC-T675-02: the main worktree (an ancestor of the allowed root) is never a root."""
        from implementation.runtime.security import audit_server
        sub = self.repo / "sub"
        sub.mkdir()
        roots = audit_server.git_worktree_roots(sub)
        self.assertNotIn(self.repo, roots)
        self.assertIn(self.worktree, roots)

    def test_not_a_repository_yields_no_roots(self):
        from implementation.runtime.security import audit_server
        outside = Path(self.tmp.name).resolve() / "plain"
        outside.mkdir()
        self.assertEqual(audit_server.git_worktree_roots(outside), [])


# ---------------------------------------------------------------------------
# 5. T675 review round (SEC-T675-01, -02, -04): sensitive names, broad roots, server wiring.
# ---------------------------------------------------------------------------

from unittest import mock  # noqa: E402

from implementation.runtime.security.validation import (  # noqa: E402
    SENSITIVE_NAME_GLOBS,
    root_is_too_broad,
)

SENSITIVE_PATHS = (
    ".env", ".env.example", ".envs/.production", "prod.env", "keys/server.pem", "keys/tls.KEY",
    "ssh/id_rsa", "ssh/id_rsa.pub", "ssh/id_ed25519", "cloud/credentials.json", "cfg/secrets.yaml",
    "cfg/secrets.yml", ".git/config", ".ENV",
)


class SensitivePathTests(unittest.TestCase):
    """Every tool refuses a path that passes through a sensitive name below the matched root."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        for rel in SENSITIVE_PATHS:
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text("x\n")
        (self.root / ".envs" / ".production").unlink()
        (self.root / ".envs" / ".production").mkdir()
        (self.root / ".envs" / ".production" / "package.json").write_text("{}")
        (self.root / "ok").mkdir()
        (self.root / "ok" / "requirements.txt").write_text("")
        (self.root / "ok" / "package.json").write_text("{}")
        (self.root / "ok" / "app.csproj").write_text("")

    def test_the_globs_cover_the_documented_names(self):
        self.assertEqual(
            set(SENSITIVE_NAME_GLOBS),
            {".env*", "*.env", "*.pem", "*.key", "id_rsa*", "id_ed25519*",
             "credentials.json", "secrets.y*ml", ".git"},
        )

    def test_grep_root_dir_in_or_below_a_sensitive_directory_is_refused(self):
        for rel in (".envs", ".envs/.production", ".git"):
            with self.subTest(root_dir=rel), self.assertRaisesRegex(PathValidationError, "sensitive name"):
                commands.build_grep_content_argv("x", "*", str(self.root / rel), allowed_root=self.root)

    def test_the_envs_production_layout_is_refused_by_every_tool(self):
        production = self.root / ".envs" / ".production"
        kwargs = {"allowed_root": self.root}
        with self.assertRaisesRegex(PathValidationError, "sensitive name"):
            commands.build_npm_audit_argv(str(production), **kwargs)
        with self.assertRaisesRegex(PathValidationError, "sensitive name"):
            commands.build_pip_audit_argv(str(production / "package.json"), **kwargs)
        with self.assertRaisesRegex(PathValidationError, "sensitive name"):
            commands.build_dotnet_list_vulnerable_argv(str(production / "package.json"), **kwargs)

    def test_a_file_that_is_itself_sensitive_is_refused_by_the_file_tools(self):
        for rel in ("prod.env", "keys/server.pem", "cfg/secrets.yaml", "ssh/id_rsa"):
            with self.subTest(path=rel), self.assertRaisesRegex(PathValidationError, "sensitive name"):
                commands.build_pip_audit_argv(str(self.root / rel), allowed_root=self.root)

    def test_a_symlink_into_a_sensitive_directory_is_refused(self):
        (self.root / "innocent").symlink_to(self.root / ".envs")
        with self.assertRaisesRegex(PathValidationError, "sensitive name"):
            commands.build_grep_content_argv("x", "*", str(self.root / "innocent"), allowed_root=self.root)

    def test_the_match_is_case_blind(self):
        for rel in ("Keys", "ID_RSA_DIR", "Prod.ENV"):
            (self.root / rel).mkdir()
        (self.root / "Keys" / "TLS.PEM").write_text("x")
        for rel in ("Keys/TLS.PEM", "ID_RSA_DIR", "Prod.ENV"):
            with self.subTest(path=rel), self.assertRaisesRegex(PathValidationError, "sensitive name"):
                commands.build_pip_audit_argv(str(self.root / rel), allowed_root=self.root) if rel.endswith("PEM") \
                    else commands.build_grep_content_argv("x", "*", str(self.root / rel), allowed_root=self.root)

    def test_ordinary_paths_still_pass(self):
        kwargs = {"allowed_root": self.root}
        commands.build_grep_content_argv("x", "*", str(self.root / "ok"), **kwargs)
        commands.build_npm_audit_argv(str(self.root / "ok"), **kwargs)
        commands.build_pip_audit_argv(str(self.root / "ok" / "requirements.txt"), **kwargs)
        commands.build_dotnet_list_vulnerable_argv(str(self.root / "ok" / "app.csproj"), **kwargs)

    def test_only_components_below_the_matched_root_count(self):
        """A workspace that itself lives under a `.envs` or `.git` directory is not refused."""
        nested = self.root / ".envs" / "work"
        (nested / "src").mkdir(parents=True)
        commands.build_grep_content_argv("x", "*", str(nested / "src"), allowed_root=nested)
        with self.assertRaisesRegex(PathValidationError, "outside the allowed root"):
            commands.build_grep_content_argv("x", "*", str(self.root), allowed_root=nested)

    def test_an_extra_root_is_matched_before_the_check(self):
        extra = self.root / "ok"
        with self.assertRaisesRegex(PathValidationError, "sensitive name"):
            commands.build_grep_content_argv(
                "x", "*", str(self.root / ".envs"), allowed_root=self.root, extra_roots=[extra])


@_required_unless_missing(_which("rg"), "rg binary not installed in this environment")
class GrepDenyGlobsLiveTests(unittest.TestCase):
    """The rg deny globs hide every sensitive name even when the validation sees only the root."""

    def test_no_sensitive_file_is_ever_matched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for rel in SENSITIVE_PATHS:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("MARKER\n")
            (root / "visible.txt").write_text("MARKER\n")
            for glob in ("**/*", "*", "!nothing", ".env*", "**/.git/**"):
                with self.subTest(glob=glob):
                    argv, _ = commands.build_grep_content_argv("MARKER", glob, str(root), allowed_root=root)
                    self.assertEqual(_rg_paths(argv) - {"visible.txt"}, set())
            argv, _ = commands.build_grep_content_argv("MARKER", "**/*", str(root), allowed_root=root)
            self.assertEqual(_rg_paths(argv), {"visible.txt"})


class BroadRootTests(unittest.TestCase):
    """SEC-T675-02: `/`, `$HOME`, its ancestors and ancestors of the allowed root are never extra roots."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.home = self.base / "home" / "user"
        self.allowed = self.home / "code" / "repo"
        self.sibling = self.home / "code" / "worktrees" / "wt"
        for d in (self.allowed, self.sibling):
            d.mkdir(parents=True)
        patcher = mock.patch.object(Path, "home", return_value=self.home)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_root_is_too_broad(self):
        for broad in (Path("/"), self.home, self.home.parent, self.base, self.allowed.parent):
            with self.subTest(path=str(broad)):
                self.assertTrue(root_is_too_broad(broad, self.allowed))
        for fine in (self.allowed, self.sibling, self.home / "code" / "worktrees"):
            with self.subTest(path=str(fine)):
                self.assertFalse(root_is_too_broad(fine, self.allowed))

    def test_home_and_the_filesystem_root_are_broad_whatever_the_allowed_root(self):
        elsewhere = self.base / "elsewhere" / "repo"
        elsewhere.mkdir(parents=True)
        for broad in (Path("/"), self.home, self.home.parent):
            with self.subTest(path=str(broad)):
                self.assertTrue(root_is_too_broad(broad, elsewhere))
                self.assertTrue(root_is_too_broad(broad, None))
        self.assertFalse(root_is_too_broad(self.sibling, elsewhere))

    def test_parse_extra_roots_refuses_broad_roots(self):
        for broad in (self.home, self.home.parent, self.allowed.parent, "/"):
            with self.subTest(root=str(broad)), self.assertRaisesRegex(PathValidationError, "not /, \\$HOME"):
                parse_extra_roots([str(broad)], self.allowed)
        self.assertEqual(parse_extra_roots([str(self.sibling)], self.allowed), [self.sibling])

    def test_parse_worktree_list_skips_broad_roots(self):
        porcelain = "".join(f"worktree {p}\nHEAD abc\n\n" for p in (self.allowed.parent, self.home, self.sibling))
        self.assertEqual(parse_worktree_list(porcelain, self.allowed), [self.sibling])

    def test_a_worktree_list_naming_an_ancestor_does_not_widen_the_server(self):
        """The end-to-end shape of the finding: git reports `/`-like roots, grep_content still refuses."""
        porcelain = f"worktree {self.allowed.parent}\nHEAD abc\n\nworktree {self.sibling}\nHEAD def\n\n"
        roots = parse_worktree_list(porcelain, self.allowed)
        with self.assertRaises(PathValidationError):
            commands.build_grep_content_argv("x", "*", str(self.allowed.parent), allowed_root=self.allowed, extra_roots=roots)
        commands.build_grep_content_argv("x", "*", str(self.sibling), allowed_root=self.allowed, extra_roots=roots)


@_required_unless_missing(MCP_AVAILABLE and _which("git") and _which("rg"), "needs the mcp SDK, git and rg")
class ServerWiringTests(unittest.TestCase):
    """A real server process: `--allow-git-worktrees` and `SECURITY_AUDIT_EXTRA_ROOTS` take effect."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.repo = base / "repo"
        self.repo.mkdir()
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-C", str(self.repo)]
        for args in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", "init"]):
            subprocess.run([*git, *args], check=True, capture_output=True)
        self.worktree = base / "worktrees" / "wt"
        subprocess.run([*git, "worktree", "add", "-q", "--detach", str(self.worktree)], check=True, capture_output=True)
        (self.worktree / "code.txt").write_text("needle\n")
        (self.worktree / ".env").write_text("needle\n")
        self.plain = base / "plain"
        self.plain.mkdir()
        (self.plain / "code.txt").write_text("needle\n")

    def _call(self, extra_args: list[str], root_dir: Path, env: dict[str, str] | None = None):
        import anyio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "implementation.runtime.security.audit_server", "--allowed-root", str(self.repo), *extra_args],
            cwd=str(REPO_ROOT),
            env={**os.environ, **(env or {})},
        )

        async def run():
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "grep_content", {"pattern": "needle", "path_glob": "**/*", "root_dir": str(root_dir)})

        return anyio.run(run)

    def test_without_options_a_worktree_is_refused(self):
        self.assertTrue(self._call([], self.worktree).is_error)

    def test_allow_git_worktrees_accepts_the_worktree_but_not_an_unlisted_directory(self):
        ok = self._call(["--allow-git-worktrees"], self.worktree)
        self.assertFalse(ok.is_error, msg=str(ok))
        stdout = _tool_result_dict(ok).get("stdout") or ""
        self.assertIn("code.txt", stdout)
        self.assertNotIn(".env", stdout)
        self.assertTrue(self._call(["--allow-git-worktrees"], self.plain).is_error)

    def test_the_repository_root_above_a_subdirectory_allowed_root_is_not_admitted(self):
        sub = self.repo / "sub"
        sub.mkdir()
        (self.repo / "top.txt").write_text("needle\n")
        import anyio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "implementation.runtime.security.audit_server", "--allowed-root", str(sub),
                  "--allow-git-worktrees"],
            cwd=str(REPO_ROOT),
        )

        async def run():
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(
                        "grep_content", {"pattern": "needle", "path_glob": "**/*", "root_dir": str(self.repo)})

        self.assertTrue(anyio.run(run).is_error)

    def test_the_environment_variable_adds_a_root(self):
        env = {"SECURITY_AUDIT_EXTRA_ROOTS": os.pathsep.join(["", str(self.plain)])}
        ok = self._call([], self.plain, env)
        self.assertFalse(ok.is_error, msg=str(ok))
        self.assertIn("code.txt", _tool_result_dict(ok).get("stdout") or "")
        self.assertTrue(self._call([], self.worktree, env).is_error)  # only the listed root was added

    def test_an_environment_root_that_is_too_broad_stops_the_server_at_launch(self):
        for broad in ("/", str(self.repo.parent)):
            with self.subTest(root=broad):
                done = subprocess.run(
                    [sys.executable, "-m", "implementation.runtime.security.audit_server",
                     "--allowed-root", str(self.repo)],
                    cwd=str(REPO_ROOT), env={**os.environ, "SECURITY_AUDIT_EXTRA_ROOTS": broad},
                    input="", capture_output=True, text=True, timeout=60,
                )
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("PathValidationError", done.stderr)


class CiFailsInsteadOfSkippingTests(unittest.TestCase):
    def test_under_ci_a_missing_dependency_is_not_a_skip(self):
        with mock.patch.dict(os.environ, {"CI": "true"}):
            decorated = _required_unless_missing(False, "missing")(lambda: None)
        self.assertFalse(getattr(decorated, "__unittest_skip__", False))
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CI", None)
            skipped = _required_unless_missing(False, "missing")(lambda: None)
        self.assertTrue(getattr(skipped, "__unittest_skip__", False))


if __name__ == "__main__":
    unittest.main()
