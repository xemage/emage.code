"""`security-audit` MCP server -- pure `argv`-building functions.

Every function in this module takes validated data in and returns a Python list literal
(`argv: list[str]`), never a string -- per
`docs/artifacts/security-engineer-audit-server-design-v1.md` §2's shared framing: "every
wrapped tool's underlying command is a Python list literal ... constructed by this
server's own code, never a string." No function in this module ever calls
`subprocess.run` (that is `executor.py`'s exclusive job -- see its module docstring); this
module's only I/O is the read-only filesystem metadata check inside
`validation.resolve_and_validate_path()` (existence/type/suffix checks), never a
subprocess call.

## Two disclosed corrections to the design's own §2.1-§2.4 code sketches

Both were found while writing real code against `validation.py`'s actual signature, not
style preferences -- reported per `task-T497.md`'s own instruction to disclose, not
silently fix, a real gap in the design document:

1. **`allowed_root` was missing from every sketch's `resolve_and_validate_path(...)` call
   entirely.** `validation.py` §4.3's own sketch declares `allowed_root: Path` as a
   required keyword-only parameter with no default -- every one of §2.1-§2.4's own
   `commands.py` code sketches calls `resolve_and_validate_path(...)` without it, which
   would raise `TypeError: resolve_and_validate_path() missing 1 required keyword-only
   argument: 'allowed_root'` if run literally as sketched. This module resolves the gap by
   adding `allowed_root: Path` as an explicit keyword-only parameter on every
   `build_*_argv()` function below, threaded through from `audit_server.py`'s own
   server-startup configuration (§4.3's "fixed once, at server startup" requirement) --
   chosen over a hidden module-level global specifically so these functions stay pure
   (deterministic given their arguments, easily unit-testable with a `tmp_path` fixture,
   no import-order-sensitive global state), consistent with this module's own "pure
   functions" framing in `docs/tasks/task-T497.md`'s Expected Output 1.
2. **Two of the four sketches under-specified their own validation table.** §2.1's
   validation table lists "(b) be a directory" for `run_npm_audit`'s `package_json_dir`,
   but its own §4.2 code sketch omits `must_be_dir=True` from the call. §2.3's validation
   table lists "is a file" for `run_dotnet_list_vulnerable`'s
   `project_or_solution_path`, but its own code sketch omits `must_be_file=True`. Both are
   restored below so the code matches each tool's own documented validation table, not
   just its code sketch.
"""
from __future__ import annotations

from pathlib import Path

from implementation.runtime.security.validation import resolve_and_validate_path

MAX_PATTERN_LENGTH = 512
MAX_GLOB_LENGTH = 256


def build_npm_audit_argv(
    package_json_dir: str, *, allowed_root: Path
) -> tuple[list[str], str]:
    """§2.1: `npm audit --json`, run with `cwd=<validated package_json_dir>`.

    `package_json_dir` never enters `argv` at all -- it is returned separately and
    consumed only as `cwd` by `executor.run_fixed_argv()`. Even a maximally adversarial
    value for this parameter can only change *which directory* the fixed, three-element
    `argv` runs in (and only after passing existence/directory/containment/`package.json`
    checks); it can never alter the command being run.
    """
    validated_dir = resolve_and_validate_path(
        package_json_dir,
        allowed_root=allowed_root,
        must_be_dir=True,
        must_contain="package.json",
    )
    argv = ["npm", "audit", "--json"]
    return argv, str(validated_dir)


def build_pip_audit_argv(requirements_path: str, *, allowed_root: Path) -> list[str]:
    """§2.2: `pip-audit --format json -r <requirements_path>`.

    `requirements_path` occupies exactly the fifth element of this five-element `argv`
    list, after passing path validation.
    """
    validated_path = resolve_and_validate_path(
        requirements_path,
        allowed_root=allowed_root,
        must_be_file=True,
    )
    return ["pip-audit", "--format", "json", "-r", str(validated_path)]


def build_dotnet_list_vulnerable_argv(
    project_or_solution_path: str, *, allowed_root: Path
) -> list[str]:
    """§2.3: `dotnet list <path> package --vulnerable --format json`.

    `project_or_solution_path` occupies exactly index 2 of this seven-element fixed
    `argv` list.
    """
    validated_path = resolve_and_validate_path(
        project_or_solution_path,
        allowed_root=allowed_root,
        must_be_file=True,
        allowed_suffixes={".csproj", ".fsproj", ".vbproj", ".sln"},
    )
    return ["dotnet", "list", str(validated_path), "package", "--vulnerable", "--format", "json"]


def build_grep_content_argv(
    pattern: str,
    path_glob: str,
    root_dir: str = ".",
    *,
    allowed_root: Path,
) -> tuple[list[str], str]:
    """§2.4: `rg --json --no-follow --max-filesize 5M -e <pattern> --glob <path_glob>
    <root_dir>`.

    `pattern` and `path_glob` each occupy exactly one `argv` element (following the `-e`
    and `--glob` flags respectively) -- neither is ever concatenated into a string later
    handed to a shell; each is one distinct element of a list handed directly to
    `execve`. A value like `pattern = "; rm -rf /"` is passed to `rg` as a single literal
    regex to search *for* (matched literally, or rejected by `rg`'s own regex parser if
    invalid) -- never interpreted as a second shell command, because no shell is ever
    invoked to parse it (`executor.py` calls `subprocess.run(argv, shell=False, ...)`).
    """
    if len(pattern) > MAX_PATTERN_LENGTH:
        raise ValueError(f"pattern exceeds maximum length ({MAX_PATTERN_LENGTH})")
    if len(path_glob) > MAX_GLOB_LENGTH:
        raise ValueError(f"path_glob exceeds maximum length ({MAX_GLOB_LENGTH})")
    validated_dir = resolve_and_validate_path(
        root_dir,
        allowed_root=allowed_root,
        must_exist=True,
        must_be_dir=True,
    )
    argv = [
        "rg", "--json", "--no-follow", "--max-filesize", "5M",
        "-e", pattern,
        "--glob", path_glob,
        str(validated_dir),
    ]
    return argv, str(validated_dir)
