"""`security-audit` MCP server -- shared path-validation / allowed-root enforcement.

Every one of the four tools' filesystem-path parameters is resolved and validated through
`resolve_and_validate_path()` before it is ever substituted into a fixed `argv` list
(`commands.py`) or used as a subprocess `cwd` (`executor.py`). `allowed_root` is never a
per-call, caller-supplied value -- it is fixed once, at server startup
(`audit_server.py`'s `main()`), and threaded explicitly into every
`commands.build_*_argv()` call as an explicit keyword-only parameter (see `commands.py`'s
module docstring for why this is an explicit parameter rather than hidden module state).
This mirrors `security-engineer-audit-server-design-v1.md` §4.3's own framing: "even a
successfully-injection-free path parameter cannot be used to point any of the four tools
at a directory outside the agent's own workspace."

Implements the design's §4.3 code sketch essentially verbatim -- `PathValidationError` and
`resolve_and_validate_path()`'s signature/checks are unchanged from the sketch. See
`commands.py`'s module docstring for the two disclosed corrections to how this function is
*called* (not to this function's own implementation).
"""
from __future__ import annotations

from pathlib import Path


class PathValidationError(ValueError):
    """Raised when a caller-supplied path fails any requested validation check."""


def resolve_and_validate_path(
    candidate: str,
    *,
    allowed_root: Path,
    must_exist: bool = True,
    must_be_dir: bool = False,
    must_be_file: bool = False,
    must_contain: str | None = None,
    allowed_suffixes: set[str] | None = None,
) -> Path:
    """Resolve `candidate` to an absolute path and enforce every requested check.

    Containment inside `allowed_root` is checked first, before any existence/type/suffix
    check -- a `..`-traversal or an absolute path outside the workspace is rejected before
    this function reveals anything (via a different error message) about whether the
    target exists, is a file/directory, etc.

    Raises `PathValidationError` on any failure. Never raises any other exception type for
    an invalid-but-well-formed `candidate` string.
    """
    resolved = Path(candidate).resolve()
    resolved_root = allowed_root.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise PathValidationError(
            f"{candidate!r} resolves outside the allowed root ({resolved_root})"
        ) from exc
    if must_exist and not resolved.exists():
        raise PathValidationError(f"{candidate!r} does not exist")
    if must_be_dir and not resolved.is_dir():
        raise PathValidationError(f"{candidate!r} is not a directory")
    if must_be_file and not resolved.is_file():
        raise PathValidationError(f"{candidate!r} is not a file")
    if must_contain and not (resolved / must_contain).exists():
        raise PathValidationError(f"{candidate!r} does not contain {must_contain}")
    if allowed_suffixes and resolved.suffix not in allowed_suffixes:
        raise PathValidationError(
            f"{candidate!r} has an unsupported extension "
            f"(expected one of {sorted(allowed_suffixes)})"
        )
    return resolved
