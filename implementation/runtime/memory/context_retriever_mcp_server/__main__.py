"""Enables `python3 -m implementation.runtime.memory.context_retriever_mcp_server ...`
(the exact invocation form `implementation/knowledge/mcp/servers.yaml`'s new
`context-retriever` entry uses as its `args`). Delegates to `server.main()` -- no logic
lives in this file.
"""
from implementation.runtime.memory.context_retriever_mcp_server.server import main

if __name__ == "__main__":
    raise SystemExit(main())
