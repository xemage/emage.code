"""Test-only `stdio` entrypoint for T495's `@context-retriever` MCP server.

Used exclusively by `tests/functional/test_context_retriever_mcp_server.py`'s real
subprocess-over-stdio adversarial test. This is NOT part of the production server package
(`implementation/runtime/memory/context_retriever_mcp_server/`), is not referenced by
`servers.yaml`, and is never what this repo's actual `context-retriever` MCP server runs as.

Why this harness exists rather than spawning `context_retriever_mcp_server.server`'s own
`main()` directly: that production CLI constructs a real `LocalEmbedder`
(`implementation/runtime/memory/embed.py`), which requires the optional `fastembed`
dependency and a downloaded model -- exactly mirroring `context_retriever.py`'s own CLI
discipline of never exposing a test-only embedder override on its public argument parser
(see that module's docstring). This harness calls the real, unmodified `build_server()`
function directly with a `FakeEmbedder` stand-in (the same deterministic double
`tests/functional/test_context_retriever.py::FakeEmbedder` already uses) so the adversarial
test can exercise the real MCP protocol / tool-registration / tool-dispatch machinery -- the
layer that test exists to prove -- without requiring `fastembed` installed or any model
weights downloaded. Only the retrieval backend is swapped; server construction, tool
registration, and the `stdio` transport are 100% the production `build_server()` code path.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from implementation.runtime.memory.context_retriever_mcp_server.server import build_server  # noqa: E402


class FakeEmbedder:
    """Deterministic stand-in for `LocalEmbedder` -- same convention as
    `tests/functional/test_context_retriever.py::FakeEmbedder`."""

    def __init__(self, vector: tuple[float, ...] = (1.0, 0.0)) -> None:
        self.vector = vector
        self.model_name = "fake-test-embedder"

    def embed_texts(self, texts: list[str]) -> list[tuple[float, ...]]:
        return [self.vector for _ in texts]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="context-retriever-mcp-test-harness")
    parser.add_argument("--index-dir", required=True, type=Path)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--platform-root", required=True, type=Path)
    args = parser.parse_args(argv)
    server = build_server(args.index_dir, args.workspace_root, args.platform_root,
                           embedder=FakeEmbedder())
    server.run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
