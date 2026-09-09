"""`@context-retriever` (T454) — read-only agent wrapper around T453's hybrid-retrieval API.

This is a wrapper module, not a new retrieval implementation. It imports and calls
`implementation.runtime.memory.retrieve.Retriever`/`MemoryIndex` and
`implementation.runtime.memory.scope_filter.RequestingContext` exactly as documented in
`docs/artifacts/hybrid-retrieval-v1.md` §7 — no fusion, ranking, or scope-filtering logic is
re-derived here. See `docs/artifacts/context-retriever-v1.md` for the full three-layer design.

## Layer 2 of ADR-005 Decision 3's three-place `ALLOW_WRITE=false` assertion

`ALLOW_WRITE = False` below is this module's own independent assertion point — independent in the
sense that matters (`plan-035`'s "one flag is not sufficient" requirement): this is not the same
mechanism as the agent definition's tools list (layer 1, `implementation/knowledge/agents/
context-retriever.md` — an LLM-facing, declarative control an agent *could* in principle ignore if
its tool grants were ever misconfigured) or the deployment manifest (layer 3,
`deploy/docker-compose-context-retriever.yml` — an infrastructure-level control that holds even if
this Python process were somehow invoked directly, bypassing the agent runtime entirely). This
layer's actual enforcement is structural, not the constant by itself: `ContextRetriever`'s public
API surface (this class, this module) has NO write/mutate function anywhere — not a guarded one,
an absent one. There is no `write()`, `save()`, `set_scope()`, `patch()`, `delete()`, `index()`, or
similarly-shaped method on this class or as a module-level function. `ALLOW_WRITE` documents that
absence explicitly and is asserted by `tests/functional/test_context_retriever.py`'s reflection-
based static check (enumerates every public callable in this module's namespace and on
`ContextRetriever`, fails if any matches a write-verb pattern) — the constant is a marker for that
test and for a human reader, not itself the enforcement (the enforcement is the absence of the
method, which no flag flip could re-enable).

## `RequestingContext` derivation (memory-scope-model-v1.md §9 point 2)

This module is the concrete implementation §9 point 2 deferred to T454:

- `project_id` — `derive_project_id()`, from `git -C <workspace_root> remote get-url origin`,
  normalized to a lowercase `<org>/<repo>` slug (§3's own normalization convention). Never taken
  from query text, a CLI `--project-id` string, or any other caller-editable input — the only input
  is the workspace's own trusted git configuration.
- `platform` — `resolve_platform()`, read from `<platform_root>/.generated-manifest.json`'s
  `platform` field, the same build artifact `implementation/scripts/sync.mjs`'s own `syncPlatform()`
  already writes for every platform projection (one `.generated-manifest.json` per `outputDir`,
  e.g. `.claude/.generated-manifest.json` carries `"platform": "claude-code"`). This is the
  "build-time-injected constant in each platform's own projected agent config" `hybrid-retrieval-
  v1.md` §7 and `memory-scope-model-v1.md` §9 point 2 both point to — never a free-text
  `--platform=<value>` argument a caller could set at query time.

`derive_requesting_context()` is the ONLY place either field is combined into a `RequestingContext`
— no second construction site exists anywhere in this module.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
from implementation.runtime.memory.scope_filter import RequestingContext

# Layer 2's own marker constant — see module docstring. The real enforcement is the
# absence of any write/mutate method on this module's public surface, not this flag.
ALLOW_WRITE = False


class RemoteResolutionError(RuntimeError):
    """Raised when `project_id` cannot be derived from the workspace's own git remote.

    Deliberately fails closed (raises) rather than falling back to an inferred or
    default project — `RequestingContext` has no permissive "no context" state
    (`scope_filter.py`'s own `__post_init__`), and this module does not invent one.
    """


class PlatformResolutionError(RuntimeError):
    """Raised when `platform` cannot be resolved from the platform root's own build
    manifest (`.generated-manifest.json`) — see module docstring."""


_REMOTE_RE = re.compile(
    r"""^(?:[a-zA-Z][\w+.-]*://)?      # optional scheme (https://, ssh://, git://, ...)
        (?:[^@/]+@)?                    # optional user@ (git@)
        [^:/]+                          # host
        [:/]                            # separator (':' scp-like, '/' URL-like)
        (?P<path>.+?)
        (?:\.git)?/?$                   # optional trailing .git and slash
    """,
    re.VERBOSE,
)


def normalize_remote_to_project_id(remote_url: str) -> str:
    """`git remote get-url origin` output -> lowercase `<org>/<repo>` slug.

    Pure function, no I/O. `memory-scope-model-v1.md` §3's own normalization example:
    both `git@gitlab.com:em-age/emage.code.git` and
    `https://gitlab.com/em-age/emage.code.git` normalize to `em-age/emage.code`.
    """
    remote_url = remote_url.strip()
    match = _REMOTE_RE.match(remote_url)
    if not match:
        raise RemoteResolutionError(f"unrecognized git remote URL shape: {remote_url!r}")
    path = match.group("path").strip("/")
    parts = [p for p in path.split("/") if p]
    if len(parts) < 2:
        raise RemoteResolutionError(f"git remote URL has no <org>/<repo> path: {remote_url!r}")
    org, repo = parts[-2], parts[-1]
    return f"{org}/{repo}".lower()


def derive_project_id(workspace_root: Path) -> str:
    """`project_id` from the calling session's own workspace git remote — the only input
    is `workspace_root`'s own trusted git configuration, never query text or a caller-
    supplied string (memory-scope-model-v1.md §9 point 2's own proposed resolution).
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace_root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        raise RemoteResolutionError(
            f"could not resolve a git remote for {workspace_root} — project_id must come "
            "from the workspace's own git remote (memory-scope-model-v1.md §3), not a "
            "caller-supplied value"
        ) from exc
    return normalize_remote_to_project_id(result.stdout)


def resolve_platform(platform_root: Path) -> str:
    """`platform` from `<platform_root>/.generated-manifest.json`'s `platform` field —
    see module docstring for why this satisfies "build-time-injected constant... never a
    runtime-settable parameter."
    """
    manifest_path = platform_root / ".generated-manifest.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlatformResolutionError(
            f"could not read platform build manifest at {manifest_path} — platform identity "
            "must come from sync.mjs's own build output, never a caller-supplied string"
        ) from exc
    platform = data.get("platform")
    if not platform or not isinstance(platform, str):
        raise PlatformResolutionError(f"{manifest_path} has no valid 'platform' field")
    return platform


def derive_requesting_context(workspace_root: Path, platform_root: Path) -> RequestingContext:
    """The sole construction site for `RequestingContext` in this module. Both fields
    come from trusted, non-user-editable session/build identity — never from query text.
    Reuses `scope_filter.RequestingContext` unmodified; no second context type.
    """
    project_id = derive_project_id(workspace_root)
    platform = resolve_platform(platform_root)
    return RequestingContext(project_id=project_id, platform=platform)


class ContextRetriever:
    """The `@context-retriever` callable surface. Construct once per long-lived process
    (`hybrid-retrieval-v1.md` §7's own guidance) — loads the index and warms the embedder
    exactly once via `Retriever`; `.query()` never re-constructs either.

    Public API surface: `query()` only. No write/save/persist/update/delete/index/mutate
    method exists anywhere on this class — see module docstring and the reflection-based
    static check in `tests/functional/test_context_retriever.py`.
    """

    def __init__(self, index_dir: Path, embedder=None) -> None:
        """`embedder` is an optional test-only override (mirrors `Retriever.__init__`'s own
        signature) so this class stays exercisable without the optional `fastembed`
        dependency installed — never used to bypass or duplicate scope filtering.
        """
        self._retriever = Retriever(MemoryIndex.load(index_dir), embedder=embedder)

    def query(self, query_text: str, workspace_root: Path, platform_root: Path,
              top_k: int = 10) -> list[dict]:
        """The only operation this class exposes. `requesting_context` is derived fresh
        each call from trusted session identity (never from `query_text`), then passed to
        T453's `Retriever.search()` unmodified — no second scope filter, no re-ranking.
        """
        context = derive_requesting_context(workspace_root, platform_root)
        results = self._retriever.search(query_text, context, top_k=top_k)
        return [r.to_summary() for r in results]


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="context-retriever",
        description="Read-only hybrid-retrieval query over a T452-built memory index (T454). "
                     "No flag on this parser performs a write of any kind.",
    )
    parser.add_argument("query_text", help="natural-language question or symbol name")
    parser.add_argument("--index-dir", required=True, type=Path, help="T452-built index directory")
    parser.add_argument("--workspace-root", required=True, type=Path,
                         help="session workspace root — its git remote derives project_id")
    parser.add_argument("--platform-root", required=True, type=Path,
                         help="platform's projected output dir (e.g. .claude) — "
                              "its .generated-manifest.json derives platform")
    parser.add_argument("--top-k", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint: `python3 -m implementation.runtime.memory.context_retriever ...`.
    Prints a JSON array of result summaries to stdout. This function and
    `ContextRetriever.query` are the only two ways to invoke this module's functionality;
    neither accepts a write/mutate operation of any kind.
    """
    args = _build_arg_parser().parse_args(argv)
    retriever = ContextRetriever(args.index_dir)
    results = retriever.query(args.query_text, args.workspace_root, args.platform_root,
                               top_k=args.top_k)
    print(json.dumps(results, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
