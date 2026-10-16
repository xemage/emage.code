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

import fnmatch
from collections.abc import Sequence
from pathlib import Path

# T675 (SEC-T675-01): a path with a component matching one of these (case-blind) globs, below
# the root it was accepted under, is refused by every tool, and `grep_content` hands the same
# globs to `rg` as deny globs (`commands.DENY_GLOBS`). The list covers environment files
# (`.env`, `.env.example`, `.envs/`, `prod.env`), private keys and certificates, credential
# files, and the `.git` directory. Deny by default: a legitimate `monkey.key` is also refused.
SENSITIVE_NAME_GLOBS = (
    ".env*", "*.env", "*.pem", "*.key", "id_rsa*", "id_ed25519*",
    "credentials.json", "secrets.y*ml", ".git",
)


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
    extra_roots: Sequence[Path] = (),
) -> Path:
    """Resolve `candidate` to an absolute path and enforce every requested check.

    `extra_roots` (T675, SEC-T650-05) are further roots, fixed at server launch (never
    caller-supplied), inside which a path is also accepted -- for example a git worktree
    of the same repository. Containment is checked against the resolved candidate, so a
    `..` or symlink escape from any of the roots is still rejected.

    Containment inside `allowed_root` is checked first, before any existence/type/suffix
    check -- a `..`-traversal or an absolute path outside the workspace is rejected before
    this function reveals anything (via a different error message) about whether the
    target exists, is a file/directory, etc.

    Raises `PathValidationError` on any failure. Never raises any other exception type for
    an invalid-but-well-formed `candidate` string.
    """
    resolved = Path(candidate).resolve()
    resolved_root = allowed_root.resolve()
    matched_root = next(
        (r.resolve() for r in (allowed_root, *extra_roots) if resolved.is_relative_to(r.resolve())), None
    )
    if matched_root is None:
        raise PathValidationError(
            f"{candidate!r} resolves outside the allowed root ({resolved_root})"
        )
    denied = sensitive_component(resolved.relative_to(matched_root))
    if denied:
        raise PathValidationError(f"{candidate!r} passes through a sensitive name ({denied!r}), which is never read")
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


def sensitive_component(relative: Path) -> str | None:
    """The first component of `relative` that matches `SENSITIVE_NAME_GLOBS` (case-blind), if any."""
    for part in relative.parts:
        if any(fnmatch.fnmatchcase(part.lower(), glob) for glob in SENSITIVE_NAME_GLOBS):
            return part
    return None


def root_is_too_broad(path: Path, allowed_root: Path | None) -> bool:
    """True for `/`, for `$HOME` and its ancestors, and for a strict ancestor of `allowed_root`."""
    path = path.resolve()
    if path == Path(path.anchor):
        return True
    home = Path.home().resolve()
    if path == home or path in home.parents:
        return True
    return allowed_root is not None and path in allowed_root.resolve().parents


def parse_worktree_list(porcelain: str, allowed_root: Path | None = None) -> list[Path]:
    """Existing directories named by `git worktree list --porcelain` output (pure parser).

    Only absolute `worktree <path>` lines count; quoted (odd-character) paths, entries that
    no longer exist and roots that are too broad (`root_is_too_broad`) are skipped, never
    guessed at.
    """
    found: list[Path] = []
    for line in porcelain.splitlines():
        if not line.startswith("worktree "):
            continue
        raw = line[len("worktree "):]
        path = Path(raw)
        if raw.startswith('"') or not path.is_absolute() or not path.is_dir():
            continue
        if root_is_too_broad(path, allowed_root):
            continue
        found.append(path.resolve())
    return found


def parse_extra_roots(raw_roots: Sequence[str], allowed_root: Path | None = None) -> list[Path]:
    """Resolve launch-time extra roots; each must be an existing directory that is not too broad."""
    roots: list[Path] = []
    for raw in raw_roots:
        if not raw:
            continue
        path = Path(raw).resolve()
        if not path.is_dir() or root_is_too_broad(path, allowed_root):
            raise PathValidationError(
                f"extra root {raw!r} must be an existing directory that is not /, $HOME, "
                "or an ancestor of $HOME or of the allowed root"
            )
        roots.append(path)
    return roots
