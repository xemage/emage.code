"""`poc-security-audit` MCP server (T603) -- `stdio` entrypoint.

Implements `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` §3. A SEPARATE server
from `audit_server.py` (`security-audit`, exactly four tools, unchanged). Registers
**exactly two tools** -- `scan_secrets` and `ref_containment` -- and no generic command
tool. Each handler only calls the matching function in `poc_scan.py`, which builds fixed
argv lists and runs them through `git_executor.run_git()`.

`allowed_root` is fixed at start-up by the required `--allowed-root` argument (v2 §3.1,
F-9: the narrowest common parent of the repositories the reviewer may scan; sibling
projects under it are reachable -- recorded limit R-6). It is never a tool parameter.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from implementation.runtime.security import poc_scan
from implementation.runtime.security.poc_scan import PocAuditConfig

SERVER_NAME = "poc-security-audit"


def build_server(cfg: PocAuditConfig) -> MCPServer:
    """Construct the MCP server with exactly its two tools registered. This is the ONLY
    function in this package that registers a `poc-security-audit` tool."""
    server = MCPServer(
        name=SERVER_NAME,
        instructions=(
            "Fixed-command PoC security-scan tools (T603). Exposes exactly two tools -- "
            "scan_secrets and ref_containment. Results never contain matched text, "
            "stderr or argv. A clean result means no match for the fixed rule set at the "
            "scanned refs, not absence of secrets. No free-form command tool exists."
        ),
    )

    @server.tool()
    def scan_secrets(root_dir: str, scope: str, rev_range: str | None = None) -> dict:
        """Scan a git repository (root_dir must be its top level) for secret-shaped
        content with a fixed rule table. scope: worktree | index | stashes | history |
        tracked_names. rev_range is valid for history only. Returns rule ids, paths
        (redacted when they match a rule), line numbers and commits -- never matched text.
        Check `complete` and `truncated`: an incomplete scan proves nothing. A hit of the rule
        `credential-assignment` or `unquoted-credential-assignment` in worktree or index scope
        may carry `value_shape` (`template-ref` with `template_shape`, or `bare-dollar-name`)
        only when every match of that rule on its line has the SAME exact shape and the line
        ends right after the value (only spaces, tabs or a carriage return follow); a missing
        label may also mean the end-of-line check degraded. Other rules, URL hits, stash and
        history hits never carry a label, and a label never removes or uncounts a hit.
        Returned names have control, format (bidi, zero width) and line/paragraph separator
        characters removed and are cut at 200 characters.
        Limits: `history` uses `git log -G`, which does not diff merge commits (L-4); a
        range over `max_refs` commits is flagged `truncated` although fully covered (L-5);
        a `.git` file may point to a gitdir outside the allowed root (L-6); `worktree` also
        reports untracked secret-looking FILE NAMES (rule `untracked-secret-file-name`)."""
        return poc_scan.scan_secrets(root_dir, scope, rev_range, cfg)

    @server.tool()
    def ref_containment(root_dir: str, commit: str) -> dict:
        """List the remote-tracking refs, tags and local branches that contain a
        40-hex commit. `pushed` is true only if a remote-tracking ref contains it,
        otherwise "unknown" (never false): a remote-tracking ref is as fresh as
        `last_fetch_time` and does not prove the project's main remote holds the commit."""
        return poc_scan.ref_containment(root_dir, commit, cfg)

    return server


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="poc-security-audit-mcp-server",
        description="stdio MCP server exposing exactly two fixed git-scan tools "
                     "(scan_secrets, ref_containment). No flag configures a free-form "
                     "execute capability.",
    )
    parser.add_argument(
        "--allowed-root", type=Path, required=True,
        help="directory every root_dir must resolve inside (fixed at launch).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    build_server(PocAuditConfig(allowed_root=args.allowed_root.resolve())).run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
