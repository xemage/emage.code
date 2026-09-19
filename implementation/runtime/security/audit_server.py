"""`security-audit` MCP server (T497) -- `stdio` entrypoint.

Implements `docs/artifacts/security-engineer-audit-server-design-v1.md` §4.4's tool-
registration sketch, fully wired against the official `mcp` Python SDK (the design's own
§4.4 explicitly deferred exact SDK call shapes to "implementation-phase work" -- this
module is that implementation, following the same SDK surface
`implementation/runtime/memory/context_retriever_mcp_server/server.py` (T495) already
verified this session: `mcp.server.mcpserver.MCPServer`, its `.tool()` decorator, and
`.run("stdio")`).

Registers **exactly four tools** -- `run_npm_audit`, `run_pip_audit`,
`run_dotnet_list_vulnerable`, `grep_content` -- and no others. There is no fifth
`@server.tool()` call anywhere in this file, and no generic `run_command`/`execute` tool
is ever exposed. Each tool handler does nothing but: accept MCP-typed parameters, call one
`commands.build_*_argv()` function (which validates every path parameter against this
server process's own fixed `allowed_root` -- never caller-supplied), then call
`executor.run_fixed_argv()`, then return the result dict. See
`tests/functional/test_audit_server.py`'s `AdversarialToolScopingProbeTests` for the live,
subprocess-over-stdio proof that no tool outside these four is ever registered or
callable, and that a malicious `pattern`/path value is delivered as one literal `argv`
element, never shell-interpreted.

## `allowed_root`: fixed once at server startup, never a tool parameter

Per §4.3's "trust boundary is launch-time configuration, not caller-editable input"
requirement: `allowed_root` is resolved once in `main()` (default: this process's own
working directory at launch -- i.e. the workspace root `servers.yaml`'s `stdio` entry
launches this process from) and threaded explicitly into every `commands.build_*_argv()`
call via `build_server()`'s closure. No MCP tool parameter on any of the four tools below
can ever change it.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from implementation.runtime.security import commands, executor

SERVER_NAME = "security-audit"


def build_server(allowed_root: Path) -> MCPServer:
    """Construct the MCP server with exactly its four tools registered.

    This is the ONLY function in this module that registers a tool. No fifth
    `@server.tool()` call exists anywhere else in this file or this package.
    """
    allowed_root = allowed_root.resolve()
    server = MCPServer(
        name=SERVER_NAME,
        instructions=(
            "Fixed-command security-audit tools for @security-engineer (T496/T497). "
            "Exposes exactly four tools -- run_npm_audit, run_pip_audit, "
            "run_dotnet_list_vulnerable, grep_content -- each a fixed argv shape with "
            "caller input substituted into one pre-determined element, never a shell "
            "string. No free-form command-execution tool exists on this server."
        ),
    )

    @server.tool()
    def run_npm_audit(package_json_dir: str) -> dict:
        """Run `npm audit --json` against `package_json_dir` (must contain
        `package.json`). A06 dependency-audit check."""
        argv, cwd = commands.build_npm_audit_argv(package_json_dir, allowed_root=allowed_root)
        return executor.run_fixed_argv(argv, cwd=cwd)

    @server.tool()
    def run_pip_audit(requirements_path: str) -> dict:
        """Run `pip-audit --format json -r <requirements_path>`. A06 dependency-audit
        check."""
        argv = commands.build_pip_audit_argv(requirements_path, allowed_root=allowed_root)
        return executor.run_fixed_argv(argv)

    @server.tool()
    def run_dotnet_list_vulnerable(project_or_solution_path: str) -> dict:
        """Run `dotnet list <path> package --vulnerable --format json`. A06
        dependency-audit check."""
        argv = commands.build_dotnet_list_vulnerable_argv(
            project_or_solution_path, allowed_root=allowed_root
        )
        return executor.run_fixed_argv(argv)

    @server.tool()
    def grep_content(pattern: str, path_glob: str, root_dir: str = ".") -> dict:
        """Run `rg --json -e <pattern> --glob <path_glob> <root_dir>` (plus safety
        flags). Backs A02/A03/A09 content-search checklist items (hardcoded secrets,
        injection patterns, log-injection review)."""
        argv, cwd = commands.build_grep_content_argv(
            pattern, path_glob, root_dir, allowed_root=allowed_root
        )
        return executor.run_fixed_argv(argv, cwd=cwd)

    return server


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="security-audit-mcp-server",
        description="stdio-transport MCP server exposing exactly four fixed audit-command "
                     "tools (run_npm_audit, run_pip_audit, run_dotnet_list_vulnerable, "
                     "grep_content). No flag on this parser configures a free-form "
                     "execute/shell capability.",
    )
    parser.add_argument(
        "--allowed-root",
        type=Path,
        default=Path.cwd(),
        help="filesystem root every path parameter must resolve inside (default: this "
             "process's own working directory at launch -- the workspace root "
             "servers.yaml's stdio entry launches this process from; not a caller-"
             "supplied per-call value).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint: `python3 -m implementation.runtime.security.audit_server`
    (`implementation/knowledge/mcp/servers.yaml`'s exact `security-audit` entry `args`,
    with zero extra flags -- `--allowed-root` defaults to the launch-time cwd). Runs the
    server over `stdio` until the client disconnects.
    """
    args = _build_arg_parser().parse_args(argv)
    server = build_server(args.allowed_root)
    server.run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
