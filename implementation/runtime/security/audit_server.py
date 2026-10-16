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

## Scanning a git worktree (T675, SEC-T650-05)

Worktrees of this repository usually live outside the launch directory, so they fail the
`allowed_root` containment check. Three launch-time options widen the set of roots; all
are fixed when the process starts and none is a tool parameter:

* `--extra-root PATH` (repeatable) and the environment variable
  `SECURITY_AUDIT_EXTRA_ROOTS` (`os.pathsep`-separated): explicit extra roots. Whether a
  given MCP client passes its own environment to a stdio server is client-specific
  (unverified here); the flag is the sure route.
* `--allow-git-worktrees`: also accept the worktrees `git worktree list --porcelain`
  reports for `allowed_root`'s repository, read on every call through
  `executor.run_fixed_argv` (fixed argv, no shell). Off by default: the worktree list is
  repository state, so it is only trusted when the launcher opts in.

Containment is still checked on the resolved path (`..` and symlink escapes from any
root are rejected), `grep_content` still never searches `.env*` files
(`commands.DENY_GLOBS`), and the four-tool surface is unchanged.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from implementation.runtime.security import commands, executor
from implementation.runtime.security.validation import parse_extra_roots, parse_worktree_list

SERVER_NAME = "security-audit"
EXTRA_ROOTS_ENV = "SECURITY_AUDIT_EXTRA_ROOTS"
WORKTREE_LIST_TIMEOUT_SECONDS = 10


def git_worktree_roots(allowed_root: Path) -> list[Path]:
    """The worktrees of `allowed_root`'s repository (fixed argv through the executor)."""
    result = executor.run_fixed_argv(
        ["git", "-C", str(allowed_root), "worktree", "list", "--porcelain"],
        timeout=WORKTREE_LIST_TIMEOUT_SECONDS,
    )
    if result.get("exit_code") != 0:
        return []
    return parse_worktree_list(result.get("stdout") or "", allowed_root)


def build_server(
    allowed_root: Path,
    extra_roots: tuple[Path, ...] = (),
    allow_git_worktrees: bool = False,
) -> MCPServer:
    """Construct the MCP server with exactly its four tools registered.

    This is the ONLY function in this module that registers a tool. No fifth
    `@server.tool()` call exists anywhere else in this file or this package.
    `extra_roots` / `allow_git_worktrees` are launch-time options (module docstring).
    """
    allowed_root = allowed_root.resolve()

    def roots() -> tuple[Path, ...]:
        found = list(extra_roots)
        if allow_git_worktrees:
            found.extend(git_worktree_roots(allowed_root))
        return tuple(found)

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
        argv, cwd = commands.build_npm_audit_argv(
            package_json_dir, allowed_root=allowed_root, extra_roots=roots()
        )
        return executor.run_fixed_argv(argv, cwd=cwd)

    @server.tool()
    def run_pip_audit(requirements_path: str) -> dict:
        """Run `pip-audit --format json -r <requirements_path>`. A06 dependency-audit
        check."""
        argv = commands.build_pip_audit_argv(
            requirements_path, allowed_root=allowed_root, extra_roots=roots()
        )
        return executor.run_fixed_argv(argv)

    @server.tool()
    def run_dotnet_list_vulnerable(project_or_solution_path: str) -> dict:
        """Run `dotnet list <path> package --vulnerable --format json`. A06
        dependency-audit check."""
        argv = commands.build_dotnet_list_vulnerable_argv(
            project_or_solution_path, allowed_root=allowed_root, extra_roots=roots()
        )
        return executor.run_fixed_argv(argv)

    @server.tool()
    def grep_content(pattern: str, path_glob: str, root_dir: str = ".") -> dict:
        """Run `rg --json -e <pattern> --glob <path_glob> <root_dir>` (plus safety
        flags; `.env*` files are never searched). Backs A02/A03/A09 content-search
        checklist items (hardcoded secrets, injection patterns, log-injection review)."""
        argv, cwd = commands.build_grep_content_argv(
            pattern, path_glob, root_dir, allowed_root=allowed_root, extra_roots=roots()
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
    parser.add_argument(
        "--extra-root",
        action="append",
        default=[],
        metavar="PATH",
        help="an additional root (repeatable; also $" + EXTRA_ROOTS_ENV + ", os.pathsep-"
             "separated), for example a git worktree. Fixed at launch; never a tool parameter.",
    )
    parser.add_argument(
        "--allow-git-worktrees",
        action="store_true",
        help="also accept the worktrees `git worktree list` reports for the allowed root's "
             "repository (read on every call; off by default).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint: `python3 -m implementation.runtime.security.audit_server`
    (`implementation/knowledge/mcp/servers.yaml`'s exact `security-audit` entry `args`,
    with zero extra flags -- `--allowed-root` defaults to the launch-time cwd). Runs the
    server over `stdio` until the client disconnects.
    """
    args = _build_arg_parser().parse_args(argv)
    raw_roots = [*args.extra_root, *os.environ.get(EXTRA_ROOTS_ENV, "").split(os.pathsep)]
    server = build_server(
        args.allowed_root,
        extra_roots=tuple(parse_extra_roots(raw_roots, args.allowed_root)),
        allow_git_worktrees=args.allow_git_worktrees,
    )
    server.run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
