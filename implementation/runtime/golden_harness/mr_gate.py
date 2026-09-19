"""Human MR gate (T505, `plan-035` nominal `T464`, `plan-055` `T464-equiv`).

## What this module is, and the one property that matters most

`meta_improver.py` (T503) proves it is architecturally incapable of ever
writing to a real, tracked repository file. `promotion.py` (T504) turns
control/treatment trial data into a `PromotionResult`, and its own
`apply_proposal_to_scratch` only ever writes to an isolated scratch
directory, never a git worktree, never the real tracked file. **This module
is the first point in the entire closed-loop pipeline where a proposal's
content is ever allowed to touch a real, tracked repository file** -- via a
real branch, a real commit, a real push, and a real merge request. That
capability makes this module's own safety property the highest-stakes one in
Phase 6 so far, and it is a different property from T503's/T504's "never
writes":

**This module can write a proposal to a real branch and open a real merge
request against `develop` -- but it can never merge, approve, or otherwise
land that change without a human going through the ordinary MR review flow.**
Not "it doesn't currently call a merge function" -- there is no call
anywhere in this module's source, under any parameter or code path, that
merges an MR, approves an MR, or pushes directly to `develop`/`main`.
`tests/functional/test_golden_harness_mr_gate.py`'s
`TestNoAutoMergePath` class proves this the same two independent ways T503's
`TestNoFilesystemMutation` proves its own guarantee: a static AST scan of
this module's own real source (`find_auto_merge_calls`), and adversarial
per-banned-shape synthetic-violation tests proving the scanner is a real
detector, not a no-op. See `docs/artifacts/mr-gate-v1.md` for the full
design write-up and the complete banned-call-shape list; this docstring
states the load-bearing guarantee only.

## The refusal gate

`open_promotion_mr` takes a `promotion.PromotionResult` as an explicit,
required input and raises `PromotionNotApproved` -- before any git or
`glab` call of any kind -- if `promotion_result.promote is not True`. A
rejected or unevaluated proposal can never produce a branch, a commit, a
push, or an MR under any code path through this module.

## Plain importable module, not a registered subagent

Mirrors `meta_improver.py`'s and `promotion.py`'s own "plain Python module,
not a registered subagent" convention exactly, for the same reason: proving
"this module's own source never merges/approves/pushes-to-protected" is a
static, mechanical AST question for a plain library, in a way it could not
be for a registered agent definition whose safety would depend on a
`tools:` YAML grant never being loosened later.
"""
from __future__ import annotations

import ast
import hashlib
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import NamedTuple

from implementation.runtime.golden_harness.promotion import PromotionResult
from implementation.runtime.meta_improver import DiffProposal

# implementation/runtime/golden_harness/mr_gate.py -> golden_harness ->
# runtime -> implementation -> repo root. Mirrors promotion.py's own
# REPO_ROOT derivation exactly (same package depth).
REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_BASE_BRANCH = "develop"
DEFAULT_REMOTE = "origin"

# Branch-naming scheme (Objective point 3): `agent/<agent-name>/<task-id>`
# (`.claude/rules/git-workflow.md` "Agent Worktree Branch Naming") adapted
# for an automatically-generated proposal, which has neither a human agent
# name nor a task ID. `meta-improver/<target-path-slug>-<digest>` is
# deterministic from `proposal.target_path` and `proposal.based_on[0]` (see
# `compute_branch_name`), so re-running this function against the same
# proposal produces the same, recognizable branch name rather than a random
# one each time -- see `docs/artifacts/mr-gate-v1.md` SS2 for the full
# rationale.
BRANCH_PREFIX = "meta-improver/"


class PromotionNotApproved(RuntimeError):
    """Raised by `open_promotion_mr` when `promotion_result.promote is not
    True`. Raised before any git/`glab` call is attempted -- see
    `open_promotion_mr`'s own docstring and
    `tests/functional/test_golden_harness_mr_gate.py`'s
    `TestRefusalGate.test_refusal_makes_zero_subprocess_calls`."""


class MrGateResult(NamedTuple):
    """The result of a successful `open_promotion_mr` call. Never a bare
    URL string -- reports the branch name, commit message, and MR
    title/description actually used, alongside the MR URL, so a caller (or a
    test) can assert on the exact content produced without re-deriving it."""

    branch_name: str
    commit_message: str
    mr_title: str
    mr_description: str
    mr_url: str


# ---------------------------------------------------------------------------
# Branch/commit/MR content construction -- pure functions, no I/O.
# ---------------------------------------------------------------------------


def compute_branch_name(proposal: DiffProposal) -> str:
    """Deterministic branch name for `proposal`: `meta-improver/<slug>-
    <digest>`, where `<slug>` is `proposal.target_path`'s filename stem
    (lowercased, underscores replaced with hyphens) and `<digest>` is a
    12-hex-character SHA-256 digest of `f"{target_path}:{based_on[0]}"`.
    Re-running this function against an unchanged proposal always produces
    the same branch name; a proposal whose target path or triggering case
    ids change produces a different one. Pure computation -- no I/O, no git
    call, so a caller/test can compute the expected branch name without
    running this module's git side effects at all."""
    slug_source = f"{proposal.target_path}:{proposal.based_on[0]}"
    digest = hashlib.sha256(slug_source.encode("utf-8")).hexdigest()[:12]
    stem = PurePosixPath(proposal.target_path).stem.lower().replace("_", "-")
    return f"{BRANCH_PREFIX}{stem}-{digest}"


def build_commit_message(proposal: DiffProposal) -> str:
    """A real Conventional Commit message (`.claude/rules/git-workflow.md`
    "Commit Messages") citing `proposal.based_on` and `proposal.rationale`,
    so the commit message alone carries enough context to understand *why*
    without needing the MR description. Pure computation, no I/O."""
    based_on = ", ".join(proposal.based_on)
    return (
        f"feat(harness): apply meta-improver proposal for {proposal.target_path}\n"
        "\n"
        f"{proposal.rationale}\n"
        "\n"
        f"Refs: {based_on}"
    )


def build_mr_title(proposal: DiffProposal) -> str:
    """Pure computation, no I/O."""
    return f"meta-improver: proposal for {proposal.target_path}"


def build_mr_description(proposal: DiffProposal, promotion_result: PromotionResult) -> str:
    """The MR description: `proposal.rationale` and `proposal.diff_text()`
    verbatim (Objective point 6), plus the promotion decision's own `reason`
    for a reviewer's convenience. Pure computation over data the two input
    objects already hold -- no I/O."""
    return (
        "## Rationale\n"
        "\n"
        f"{proposal.rationale}\n"
        "\n"
        "## Promotion decision\n"
        "\n"
        f"{promotion_result.reason}\n"
        "\n"
        "## Diff\n"
        "\n"
        "```diff\n"
        f"{proposal.diff_text()}"
        "```\n"
    )


# ---------------------------------------------------------------------------
# The MR-gate function itself.
# ---------------------------------------------------------------------------


def _run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    """Thin wrapper around `subprocess.run` for the two external CLIs this
    module calls (`git`, `glab`). Every real call site in this module passes
    its own full, literal argv, including the leading `"git"`/`"glab"`
    program name -- this keeps each call site's argv fully visible to
    `find_auto_merge_calls`'s static scan directly at the call site, rather
    than hiding it behind a partially-applied wrapper that would only ever
    see a generic, already-merged argument list."""
    return subprocess.run(argv, cwd=cwd, check=True, capture_output=True, text=True)


def open_promotion_mr(
    proposal: DiffProposal,
    promotion_result: PromotionResult,
    *,
    repo_root: Path | None = None,
    base_branch: str = DEFAULT_BASE_BRANCH,
    remote: str = DEFAULT_REMOTE,
) -> MrGateResult:
    """Open a real merge request against `base_branch` (default `develop`)
    carrying `proposal.proposed_content`, gated on `promotion_result`.

    1. **Refuses first.** Raises `PromotionNotApproved` -- before any git or
       `glab` call is attempted -- if `promotion_result.promote is not
       True`. A rejected or unevaluated proposal never produces a branch or
       MR under any code path through this function.
    2. Creates a real branch off `f"{remote}/{base_branch}"`
       (`compute_branch_name`).
    3. Commits `proposal.proposed_content` to `proposal.target_path`, and
       only that path, using a real Conventional Commit message
       (`build_commit_message`).
    4. Pushes the branch to `remote`. This function's only `git push` call
       always targets the branch this function itself just created --
       `branch_name` is computed internally by `compute_branch_name` and is
       never accepted as a caller-supplied parameter, so there is no flag,
       parameter, or code path by which this call could push to
       `base_branch`/`develop`/`main` directly. See
       `docs/artifacts/mr-gate-v1.md` SS4 for the full "no such parameter
       exists" proof.
    5. Opens a real MR against `base_branch` via `glab mr create`, with a
       description containing `proposal.rationale` and `proposal.diff_text()`
       verbatim (`build_mr_description`).
    6. **Then stops.** No further action of any kind is taken on the MR --
       there is no call anywhere in this module that merges, approves, or
       auto-accepts an MR. See this module's own docstring and
       `docs/artifacts/mr-gate-v1.md` for the full proof.

    `repo_root` defaults to this module's own resolved repo root
    (`REPO_ROOT`) but is caller-overridable, mirroring
    `meta_improver.generate_proposal`'s own convention -- useful for tests.
    """
    if promotion_result.promote is not True:
        raise PromotionNotApproved(
            "refusing to open a merge request for a non-promoted proposal "
            f"(promotion_result.promote={promotion_result.promote!r}): {promotion_result.reason}"
        )

    root = repo_root if repo_root is not None else REPO_ROOT
    branch_name = compute_branch_name(proposal)
    commit_message = build_commit_message(proposal)
    mr_title = build_mr_title(proposal)
    mr_description = build_mr_description(proposal, promotion_result)

    with tempfile.TemporaryDirectory(prefix="mr-gate-worktree-") as tmp:
        worktree_dir = Path(tmp) / "worktree"
        _run(["git", "fetch", remote, base_branch], cwd=root)
        _run(
            ["git", "worktree", "add", str(worktree_dir), "-b", branch_name, f"{remote}/{base_branch}"],
            cwd=root,
        )
        try:
            target = worktree_dir / PurePosixPath(proposal.target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(proposal.proposed_content, encoding="utf-8")

            _run(["git", "add", "--", proposal.target_path], cwd=worktree_dir)
            _run(["git", "commit", "-m", commit_message], cwd=worktree_dir)
            _run(["git", "push", remote, branch_name], cwd=worktree_dir)
        finally:
            _run(["git", "worktree", "remove", "--force", str(worktree_dir)], cwd=root)

    mr_result = _run(
        [
            "glab",
            "mr",
            "create",
            "--source-branch",
            branch_name,
            "--target-branch",
            base_branch,
            "--title",
            mr_title,
            "--description",
            mr_description,
            "--yes",
        ],
        cwd=root,
    )
    mr_url = _extract_mr_url(mr_result.stdout)

    return MrGateResult(
        branch_name=branch_name,
        commit_message=commit_message,
        mr_title=mr_title,
        mr_description=mr_description,
        mr_url=mr_url,
    )


def _extract_mr_url(glab_stdout: str) -> str:
    """`glab mr create` prints the new MR's URL as (or on) its last
    non-empty output line. Pure string parsing -- no I/O."""
    lines = [line.strip() for line in glab_stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


# ---------------------------------------------------------------------------
# The "no auto-merge path" static AST scan.
# ---------------------------------------------------------------------------

# Function names this module itself uses to shell out (Objective point 1's
# scanner must see the real call shape this module actually uses, not just
# a hypothetical bare `subprocess.*`/`os.system` call -- see this module's
# `_run` wrapper above). Treated identically to a raw `subprocess.*` call:
# its first positional argument is the literal argv this module intends to
# run.
_WRAPPER_CALL_NAMES = {"_run"}

_SUBPROCESS_ATTRS = {"run", "call", "check_call", "check_output", "Popen"}

# A literal `git push` argument list is flagged as targeting a protected
# branch directly if it contains any of these tokens verbatim.
_GIT_PUSH_PROTECTED_REFS = {"develop", "main", "origin/develop", "origin/main"}

_DYNAMIC = "\x00dynamic\x00"

_HTTP_VERB_ATTRS = {"post", "put", "patch"}
_MERGE_REQUEST_URL_MARKER = "merge_requests"
_MERGE_OR_APPROVE_ENDPOINT_SUFFIXES = ("/merge", "/approve")

# Representative MCP-gitlab-style tool-call names this scanner also flags
# directly, in case a future edit switches from `glab` to the `mcp__gitlab`
# MCP server's own merge/approve tools (task brief's own explicit call-out).
_NAMED_MERGE_OR_APPROVE_TOOL_CALLS = {
    "merge_merge_request",
    "approve_merge_request",
    "gitlab_merge_merge_request",
    "gitlab_approve_merge_request",
}


def _call_target(call: ast.Call) -> tuple[str | None, str | None]:
    """`(root_name, attr_or_name)` for a Call node's callee, e.g.
    `subprocess.run(...)` -> `("subprocess", "run")`; a bare name call
    `_run(...)` -> `(None, "_run")`; `mr.merge(...)` -> `("mr", "merge")`."""
    func = call.func
    if isinstance(func, ast.Attribute):
        root = func.value
        while isinstance(root, ast.Attribute):
            root = root.value
        root_name = root.id if isinstance(root, ast.Name) else None
        return root_name, func.attr
    if isinstance(func, ast.Name):
        return None, func.id
    return None, None


def _receiver_identifier_tokens(node: ast.expr) -> list[str]:
    """Every `Name`/`Attribute` identifier appearing anywhere within a
    `.merge()`/`.approve()` call's receiver expression (e.g.
    `client.merge_requests.get(1)` -> `["client", "merge_requests", "get"]`)
    -- a full subtree walk rather than a strict linear dotted-chain
    resolution, so an intermediate method call in the chain (like
    `.get(1)` above) does not hide an otherwise-visible `merge_request(s)`
    identifier from this check. Used only to decide whether a bare
    `.merge()`/`.approve()` call's receiver plausibly refers to a
    merge-request object."""
    return [sub.id.lower() if isinstance(sub, ast.Name) else sub.attr.lower() for sub in ast.walk(node) if isinstance(sub, (ast.Name, ast.Attribute))]


def _string_tokens_from_argv(call: ast.Call) -> list[str] | None:
    """Best-effort extraction of a CLI call's argv as a lowercased token
    list, from a literal list/tuple of string constants, or a single
    literal shell-style command string. Any non-literal element (a
    variable, an f-string, an attribute access) becomes the `_DYNAMIC`
    placeholder rather than being resolved -- this module's own real argv
    elements for branch names, commit messages, and file paths are always
    such non-literal expressions, so they never spuriously match a banned
    literal token (`"merge"`, `"approve"`, `"--force"`, `"-f"`,
    `"develop"`, `"main"`). Returns `None` if the first argument is neither
    a list/tuple literal nor a single string constant (this module never
    needs a fully dynamic argv, so such a call is simply not
    argv-analyzable -- out of scope for this scanner, which only reasons
    about this module's own real, literal-list call shapes)."""
    if not call.args:
        return None
    first = call.args[0]
    if isinstance(first, (ast.List, ast.Tuple)):
        tokens: list[str] = []
        for element in first.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                tokens.append(element.value.lower())
            else:
                tokens.append(_DYNAMIC)
        return tokens
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return [token.lower() for token in first.value.split()]
    return None


def _check_cli_argv(tokens: list[str], lineno: int) -> list[str]:
    """Apply the CLI-shaped banned-call rules to one already-extracted argv
    token list. See module docstring / `docs/artifacts/mr-gate-v1.md` for
    the full banned-shape list this implements."""
    violations: list[str] = []
    joined = " ".join(tokens)

    if "mr" in tokens and "merge" in tokens:
        violations.append(f"line {lineno}: 'glab mr merge'-shaped call (argv {tokens!r})")
    elif "mr merge" in joined:
        violations.append(f"line {lineno}: 'mr merge' substring in a shell-style command string")

    if "mr" in tokens and "approve" in tokens:
        violations.append(f"line {lineno}: 'glab mr approve'-shaped call (argv {tokens!r})")
    elif "mr approve" in joined:
        violations.append(f"line {lineno}: 'mr approve' substring in a shell-style command string")

    if tokens[:1] == ["git"] and "merge" in tokens[1:]:
        violations.append(f"line {lineno}: 'git merge' call (argv {tokens!r})")

    if tokens[:1] == ["git"] and "push" in tokens:
        if "--force" in tokens or "-f" in tokens:
            violations.append(f"line {lineno}: 'git push --force'/'-f' call (argv {tokens!r})")
        if any(token in _GIT_PUSH_PROTECTED_REFS for token in tokens):
            violations.append(f"line {lineno}: 'git push' targeting develop/main directly (argv {tokens!r})")

    return violations


def _string_constant_args(call: ast.Call) -> list[str]:
    values: list[str] = []
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            values.append(arg.value)
    for keyword in call.keywords:
        if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            values.append(keyword.value.value)
    return values


def _check_api_or_tool_call(node: ast.Call, root_name: str | None, attr: str | None) -> str | None:
    """GitLab REST/GraphQL API merge/approve endpoint shapes, and named
    merge/approve tool-call shapes (the `mcp__gitlab`-style call-out in the
    task brief). See module docstring for the full list this covers."""
    if attr in _HTTP_VERB_ATTRS:
        for value in _string_constant_args(node):
            lowered = value.lower().rstrip("/")
            if _MERGE_REQUEST_URL_MARKER in lowered and any(
                lowered.endswith(suffix) for suffix in _MERGE_OR_APPROVE_ENDPOINT_SUFFIXES
            ):
                return f"line {node.lineno}: HTTP .{attr}() call to a merge_requests .../merge|approve endpoint"

    name = attr or ""
    lowered_name = name.lower()

    if lowered_name in {"merge", "approve"} and isinstance(node.func, ast.Attribute):
        tokens = _receiver_identifier_tokens(node.func.value)
        if "mr" in tokens or any("merge_request" in token for token in tokens):
            return f"line {node.lineno}: .{name}() called on a merge-request-shaped receiver (tokens {tokens!r})"

    if lowered_name in _NAMED_MERGE_OR_APPROVE_TOOL_CALLS:
        return f"line {node.lineno}: call to {name}() -- a named merge/approve MR tool call"

    return None


def find_auto_merge_calls(source: str) -> list[str]:
    """Walk every `ast.Call` node in `source` and return a list of
    human-readable descriptions of any call shape that could merge, approve,
    or auto-accept a merge request, or push/merge directly to
    `develop`/`main`. Empty list means clean. Pure static analysis -- never
    executes `source`. Mirrors
    `tests/functional/test_meta_improver.py`'s
    `find_filesystem_mutation_calls`'s own AST-walk-and-flag shape exactly.

    Flags, at minimum (see `docs/artifacts/mr-gate-v1.md` for the full,
    authoritative list with examples):
      - `glab mr merge` / `glab mr approve` -- a `subprocess.*`/`os.system`/
        `_run` call whose literal argv contains both `"mr"` and `"merge"`
        (or `"approve"`), or the literal substring `"mr merge"`/
        `"mr approve"` in a shell-style command string.
      - `git merge` -- a literal argv `["git", ..., "merge", ...]`.
      - `git push --force`/`-f` -- a literal `git push` argv also containing
        `"--force"` or `"-f"`.
      - `git push` with a literal `develop`/`main`/`origin/develop`/
        `origin/main` ref token.
      - A GitLab REST API call (`.post()`/`.put()`/`.patch()`) whose URL
        string argument contains `"merge_requests"` and ends with
        `"/merge"` or `"/approve"`.
      - `.merge()`/`.approve()` called on a receiver whose own dotted name
        plausibly refers to a merge-request object, or a direct call to a
        named merge/approve MR tool function (e.g. `merge_merge_request`).
    """
    tree = ast.parse(source)
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        root_name, attr = _call_target(node)

        is_subprocess_call = root_name == "subprocess" and attr in _SUBPROCESS_ATTRS
        is_system_call = root_name == "os" and attr == "system"
        is_wrapper_call = root_name is None and attr in _WRAPPER_CALL_NAMES

        if is_subprocess_call or is_system_call or is_wrapper_call:
            tokens = _string_tokens_from_argv(node)
            if tokens is not None:
                violations.extend(_check_cli_argv(tokens, node.lineno))
            continue

        api_or_tool_violation = _check_api_or_tool_call(node, root_name, attr)
        if api_or_tool_violation:
            violations.append(api_or_tool_violation)

    return violations
