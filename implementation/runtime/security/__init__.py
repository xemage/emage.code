"""`security-audit` MCP server package (T497).

Implements `docs/artifacts/security-engineer-audit-server-design-v1.md` (T496, the sole
authoritative spec for this package) exactly: a `stdio`-transport MCP server exposing
exactly four fixed audit-command tools -- `run_npm_audit`, `run_pip_audit`,
`run_dotnet_list_vulnerable`, `grep_content` -- with no generic `run_command`/`execute`
tool anywhere. See `audit_server.py` for the server/tool registration, `commands.py` for
the pure `argv`-building functions, `executor.py` for the sole `subprocess.run` choke
point, and `validation.py` for shared path-validation/allowed-root enforcement.

Structural mirror of `implementation/runtime/memory/context_retriever_mcp_server/` (T495):
one module (`executor.py`) is the only place `subprocess.run` is ever called, exactly as
`context_retriever.py` has "no write method exists anywhere in the module" -- here, "no
function outside `executor.py` ever calls `subprocess.run`, and `executor.py` never
accepts a shell string."
"""
