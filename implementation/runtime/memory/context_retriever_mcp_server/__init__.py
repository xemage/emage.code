"""T495 -- dedicated single-tool `stdio` MCP server wrapping `ContextRetriever.query()`.

Implements `docs/artifacts/scoped-execution-primitive-v1.md` Section 1.4's recommendation
(design pass, T457) and closes `docs/tasks/task-T457.md` Expected Outputs items 2-3 for
`@context-retriever` only. See `server.py` for the actual server/tool definition and this
package's own module docstring there for the full "why a new small package" reasoning.
"""
