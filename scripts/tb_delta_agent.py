"""Arm B agent for the Terminal-Bench delta harness (T419).

``EmageCodeClaudeCode`` is a **minimal** subclass of Harbor's built-in
``ClaudeCode`` agent (``harbor.agents.installed.claude_code.ClaudeCode``). It
overrides exactly one method -- ``setup()`` -- to copy this repo's
``.claude/`` projection tree (and top-level ``.mcp.json``) into the task
workspace (``/app``, Terminal-Bench's standard task ``WORKDIR`` -- see
``docs/benchmarks/tb-delta-runner.md`` for how this was confirmed) before the
stock agent's own ``setup()``/``run()`` do anything else.

Nothing else is overridden. ``run()`` (the actual `claude` CLI invocation,
its flags, its model resolution, its env-var handling) is inherited
byte-for-byte from ``ClaudeCode``. This is deliberate: the ONLY behavioral
difference between Arm A (``-a claude-code``) and Arm B
(``-a scripts.tb_delta_agent:EmageCodeClaudeCode``) is that Arm B's
workspace has the projection files present before the agent starts --
"Workspace: bare | emage.code projection applied", per
``docs/plans/plan-035-roadmap-v7-ground-up.md`` §2.2.1's arm table. Everything
else (model, CLI flags, timeouts, resources, dataset, `-k`) is controlled
identically by ``scripts/tb-delta.sh`` for both arms and is not touched here.

Why subclassing rather than one of Harbor's ``--skill``/``--mcp-config``
flags: those flags exist and were considered, but they only cover two of the
projection's five parts (Claude Code Skills and MCP servers) -- they have no
mechanism for project-scoped subagents (``.claude/agents/``), slash commands
(``.claude/commands/``), or path-scoped rules (``.claude/rules/``). Custom
agent subclassing is Harbor's own documented mechanism for exactly this case
(``BaseInstalledAgent``/``BaseAgent`` subclassing, cited in plan-035 §2.2.1
and confirmed against the installed Harbor 0.21.0 source at
``harbor/agents/installed/base.py`` and ``harbor/agents/base.py`` -- see the
runner doc for the full research trail). It also has the useful property that
the *only* CLI-visible difference between the two arms' ``harbor run``
invocations is the ``--agent`` value itself, which keeps
``scripts/tb-delta.sh``'s config-diff proof (criterion 2) simple to reason
about.

Docker layer used to place the files: ``BaseEnvironment.upload_dir`` /
``upload_file`` (the same primitives Harbor's own skill-injection path uses
internally, see ``harbor/trial/trial.py::_upload_injected_skills``) -- not a
shell hack, not a modified task Dockerfile, not a bind mount. The task's own
``environment/Dockerfile`` is never read or modified by this module.
"""

from __future__ import annotations

from pathlib import Path

from harbor.agents.installed.claude_code import ClaudeCode
from harbor.environments.base import BaseEnvironment

# This file lives at <repo-root>/scripts/tb_delta_agent.py; the projection
# lives at <repo-root>/.claude and <repo-root>/.mcp.json.
_REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTION_SOURCE_DIR = _REPO_ROOT / ".claude"
MCP_SOURCE_FILE = _REPO_ROOT / ".mcp.json"

# Terminal-Bench task images consistently set `WORKDIR /app` (verified across
# the local task cache at ~/.cache/harbor/tasks/packages/terminal-bench/*/
# environment/Dockerfile, per T417/T418's prior work; also the `cwd` Claude
# Code itself records in its session transcripts, per
# harbor/agents/installed/claude_code.py's `"-app"` project-dir slug). This is
# the task's own workspace, not a Harbor-internal path -- copying into it adds
# files an agent operating in that workspace would see, exactly the
# "workspace: bare | projection applied" difference plan-035 §2.2.1 specifies.
WORKSPACE_PROJECTION_TARGET = "/app/.claude"
WORKSPACE_MCP_TARGET = "/app/.mcp.json"


class EmageCodeClaudeCode(ClaudeCode):
    """Stock ``claude-code`` + the emage.code projection copied into /app.

    See module docstring for what is (and is not) overridden and why.
    """

    @staticmethod
    def name() -> str:
        return "emage-code-claude-code"

    async def setup(self, environment: BaseEnvironment) -> None:
        # Stock install/version-detection behavior, unmodified.
        await super().setup(environment)

        if not PROJECTION_SOURCE_DIR.is_dir():
            raise FileNotFoundError(
                f"emage.code projection not found at {PROJECTION_SOURCE_DIR} "
                "-- Arm B cannot run without it. This is a runner defect, "
                "not a task-level failure; do not silently fall back to "
                "running Arm B without the projection."
            )
        await environment.upload_dir(
            PROJECTION_SOURCE_DIR, WORKSPACE_PROJECTION_TARGET
        )

        if MCP_SOURCE_FILE.is_file():
            await environment.upload_file(MCP_SOURCE_FILE, WORKSPACE_MCP_TARGET)
