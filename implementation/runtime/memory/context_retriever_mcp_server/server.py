"""`@context-retriever`'s dedicated `stdio` MCP server (T495).

`docs/artifacts/scoped-execution-primitive-v1.md` Section 1.4 recommends a small, dedicated
`stdio`-transport MCP server that imports `ContextRetriever` and exposes exactly one tool --
`retrieve(query, top_k)` -- with no other capability, so that `@context-retriever`'s
Claude Code `tools:` grant can name `mcp__context-retriever__retrieve` in place of `execute`
(unrestricted `Bash`). This module is that server.

## Why a new small package, not a script

`implementation/runtime/memory/context_retriever.py` already has a CLI entrypoint
(`main()`), but that CLI speaks argv-in/stdout-JSON-out, not the MCP `stdio` JSON-RPC
protocol an MCP client (an agent's platform runtime) actually understands. This module is a
thin protocol adapter over the *same* `ContextRetriever.query()` call `context_retriever.py`'s
own CLI makes -- it does not re-derive or duplicate any retrieval/scope-filtering logic (see
`ContextRetriever.query()`'s own docstring for that discipline; this module only adds a
transport).

## Why the safety property is structural, not a runtime check

This server's public surface (`build_server()`'s returned `MCPServer` instance) has exactly
one registered tool: `retrieve`. There is no `write`, `save`, `delete`, or any other tool
registered anywhere in this module -- an MCP client asking for any tool name other than
`retrieve` gets "Unknown tool: <name>" back from the SDK's own tool-dispatch machinery
(`MCPServer.call_tool()`), because no other tool was ever added, not because a guard
intercepted the call. This mirrors `context_retriever.py`'s own "no write method exists, not
a guarded one" discipline at the next layer out (the MCP protocol surface, rather than the
Python class surface). See `tests/functional/test_context_retriever_mcp_server.py`'s
`AdversarialToolScopingProbeTests` for the live, subprocess-over-stdio proof.

## Why `query`/`top_k` are the only caller-supplied values

`ContextRetriever.query()` also takes `workspace_root` and `platform_root`, which derive
`project_id`/`platform` for T453's mandatory query-time scope filter
(`context_retriever.py`'s own module docstring: "never a free-text argument you could be
asked to override"). Neither is exposed as an MCP tool *parameter* here, for the same
non-spoofability reason `context_retriever.py` itself never accepts them from `query_text`:
both are server *startup* configuration (this module's own CLI flags, resolved once when the
server process is launched from `servers.yaml`'s `args`), never something an MCP tool caller
can set per-call. A caller can only ever influence `query` (free text) and `top_k` (an
integer bound); the trusted workspace/platform identity is fixed for the lifetime of the
server process, exactly as `context_retriever.py`'s CLI already fixes it once per invocation.

## Official SDK, not a hand-rolled protocol

Uses the official `mcp` Python SDK (`pip install mcp`; see
`implementation/runtime/memory/requirements-mcp-server.txt` for the pinned, documented
dependency -- an open-source, free, one-time local install, not a paid/metered service).
This session verified against the SDK's current PyPI release (`mcp==2.2.0`,
`https://github.com/modelcontextprotocol/python-sdk`): the convenience server class in this
version is `mcp.server.mcpserver.MCPServer` (the `FastMCP` name from SDK v1.x was renamed in
the v2 line; `MCPServer.tool()`/`MCPServer.run("stdio")` are the direct v2 successors of
`FastMCP.tool()`/`FastMCP.run()` and were exercised directly in this session, not assumed
from v1-era documentation).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from implementation.runtime.memory.context_retriever import ContextRetriever

SERVER_NAME = "context-retriever"


def build_server(index_dir: Path, workspace_root: Path, platform_root: Path,
                  embedder=None) -> MCPServer:
    """Construct the MCP server with its one tool registered.

    `embedder` is a test-only override (mirrors `ContextRetriever.__init__`'s own optional
    `embedder` parameter) so this server stays exercisable in tests without the optional
    `fastembed` dependency installed -- never used to bypass or duplicate scope filtering.

    This is the ONLY function in this module that registers a tool. No second `@server.tool()`
    call exists anywhere else in this file or package.
    """
    retriever = ContextRetriever(index_dir, embedder=embedder)
    server = MCPServer(
        name=SERVER_NAME,
        instructions=(
            "Read-only hybrid-retrieval query over a T452-built memory index (T454/T495). "
            "Exposes exactly one tool, retrieve(query, top_k). No write/mutate tool exists "
            "on this server."
        ),
    )

    @server.tool()
    def retrieve(query: str, top_k: int = 10) -> list[dict]:
        """Query the memory index and return ranked result summaries.

        `query`: natural-language question or symbol name.
        `top_k`: maximum number of results to return (default 10).

        Passed through unmodified to `ContextRetriever.query()`, scoped to this server
        process's own fixed `workspace_root`/`platform_root` (never caller-supplied) --
        see module docstring. This is the only tool this server exposes.
        """
        return retriever.query(query, workspace_root, platform_root, top_k=top_k)

    return server


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="context-retriever-mcp-server",
        description="stdio-transport MCP server exposing exactly one tool, "
                     "retrieve(query, top_k), wrapping ContextRetriever.query(). "
                     "No flag on this parser configures a write/mutate capability.",
    )
    parser.add_argument("--index-dir", required=True, type=Path,
                         help="T452-built index directory")
    parser.add_argument("--workspace-root", required=True, type=Path,
                         help="session workspace root -- its git remote derives project_id "
                              "for every call this server process ever makes")
    parser.add_argument("--platform-root", required=True, type=Path,
                         help="platform's projected output dir (e.g. .claude) -- its "
                              ".generated-manifest.json derives platform for every call this "
                              "server process ever makes")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint: `python3 -m implementation.runtime.memory.context_retriever_mcp_server
    --index-dir ... --workspace-root ... --platform-root ...`. Runs the server over `stdio`
    until the client disconnects. This function and `build_server()` are the only two ways to
    start this server; neither accepts a write/mutate operation of any kind.
    """
    args = _build_arg_parser().parse_args(argv)
    server = build_server(args.index_dir, args.workspace_root, args.platform_root)
    server.run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
