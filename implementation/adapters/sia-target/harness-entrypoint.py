#!/usr/bin/env python3
"""
SIA Target Agent Harness Entrypoint

This script is the entrypoint for the SIA target agent container.
It reads configuration from environment variables, executes the SIA agent,
and writes the execution result to output.json with credential sanitization.

Environment Variables:
- CWSO_HARNESS_PROMPT (required): The task/prompt for the SIA agent
- SIA_BACKEND (default: "claude"): Agent backend ("claude" or "openhands")
- SIA_MODEL (default: "haiku"): Model ID to use
- SIA_MAX_TURNS (default: "10"): Maximum agent iterations
- ANTHROPIC_API_KEY: Anthropic API key (for Claude backend)
- ANTHROPIC_BASE_URL: Anthropic base URL (for proxy routing)
- OPENAI_API_KEY: OpenAI API key (for OpenAI models)
- OPENAI_BASE_URL: OpenAI base URL (for proxy routing)
- GEMINI_API_KEY: Gemini API key (for Gemini models)
- GOOGLE_API_KEY: Google API key (alternative for Gemini)
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# T224: Reward attachment integration
try:
    from reward_attachment import attach_reward_to_job
    HAS_REWARD_ATTACHMENT = True
except ImportError:
    HAS_REWARD_ATTACHMENT = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.debug("reward_attachment module not available (expected in container context)")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sanitize_credentials(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize credential patterns from data before output.

    This function removes known credential formats (API keys, passwords, secrets)
    from all string values in the data dictionary. The sanitization is applied
    to error messages, log messages, and any other string fields to prevent
    credential leakage into captured trajectories.

    Credential Patterns Scrubbed:
    - Anthropic keys: sk-ant-[a-zA-Z0-9]{20,}
    - OpenAI keys: sk-[a-zA-Z0-9]{20,}
    - Gemini keys: AIza[a-zA-Z0-9_-]{35}
    - Generic: api_key, password, secret fields

    Args:
        data: Dictionary potentially containing credential data

    Returns:
        Dictionary with credentials replaced with [REDACTED]
    """
    patterns = [
        r'sk-ant-[a-zA-Z0-9]{20,}',     # Anthropic keys
        r'sk-[a-zA-Z0-9]{20,}',          # OpenAI keys
        r'AIza[a-zA-Z0-9_-]{35}',        # Gemini keys
        r'(api[_-]?key|password|secret)["\']?\s*[=:]\s*["\']?[a-zA-Z0-9_\-]+["\']?',  # Generic patterns
    ]

    def scrub_value(v: Any) -> Any:
        """Apply sanitization patterns to a single value."""
        if not isinstance(v, str):
            return v

        sanitized = v
        for pattern in patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)

        return sanitized

    def sanitize_recursive(obj: Any) -> Any:
        """Recursively sanitize nested structures."""
        if isinstance(obj, dict):
            return {k: sanitize_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return scrub_value(obj)
        else:
            return obj

    sanitized = sanitize_recursive(data)

    # Count redactions for logging
    def count_redactions(text: str) -> int:
        if isinstance(text, str):
            return text.count('[REDACTED]')
        return 0

    redaction_count = 0
    for value in str(sanitized).split():
        if '[REDACTED]' in value:
            redaction_count += 1

    if redaction_count > 0:
        logger.info(f"Sanitized output (removed {redaction_count} credential patterns)")

    return sanitized


def validate_environment() -> Dict[str, str]:
    """
    Validate and extract environment variables.

    Raises:
        ValueError: If required environment variables are missing

    Returns:
        Dictionary of configuration values
    """
    # Required environment variables
    prompt = os.getenv("CWSO_HARNESS_PROMPT", "").strip()
    if not prompt:
        raise ValueError(
            "CWSO_HARNESS_PROMPT environment variable is required and must be non-empty"
        )

    # Workspace validation
    workspace = Path(os.getenv("CWSO_HARNESS_WORKSPACE", "/workspace")).expanduser()
    if not workspace.exists():
        raise ValueError(f"Workspace directory does not exist: {workspace}")

    if not workspace.is_dir():
        raise ValueError(f"Workspace path is not a directory: {workspace}")

    # Optional configuration with defaults
    config = {
        "prompt": prompt,
        "workspace": str(workspace),
        "backend": os.getenv("SIA_BACKEND", "claude"),
        "model": os.getenv("SIA_MODEL", "haiku"),
        "max_turns": os.getenv("SIA_MAX_TURNS", "10"),
    }

    # Validate backend
    if config["backend"] not in ("claude", "openhands"):
        raise ValueError(
            f"Invalid SIA_BACKEND: {config['backend']}. Must be 'claude' or 'openhands'"
        )

    # Validate max_turns is numeric
    try:
        int(config["max_turns"])
    except ValueError:
        raise ValueError(f"SIA_MAX_TURNS must be numeric, got: {config['max_turns']}")

    logger.info(f"Configuration: backend={config['backend']}, model={config['model']}, max_turns={config['max_turns']}")

    return config


async def run_sia_agent(
    backend: str,
    model: str,
    prompt: str,
    max_turns: int,
    workspace: str
) -> Dict[str, Any]:
    """
    Execute the SIA agent with the given configuration.

    Args:
        backend: Agent backend ("claude" or "openhands")
        model: Model ID to use
        prompt: Task prompt for the agent
        max_turns: Maximum iterations
        workspace: Working directory for agent

    Returns:
        Dictionary with execution result
    """
    try:
        # Import SIA modules
        try:
            from sia.util import run_agent
        except ImportError as e:
            logger.error(f"Failed to import SIA: {e}")
            return {
                "status": "error",
                "backend": backend,
                "model": model,
                "prompt": prompt,
                "workspace": workspace,
                "error": f"Failed to import SIA agent library: {e}",
                "trajectory": None,
            }

        logger.info(f"Starting SIA agent execution (backend={backend}, model={model})")

        # Execute agent
        # Note: This is a placeholder for the actual SIA API call
        # The actual implementation will depend on the SIA version and API
        result = await run_agent(
            model_name=model,
            max_turns=max_turns,
            prompt=prompt,
            agent_working_directory=workspace,
            backend=backend,
        )

        logger.info("SIA agent execution completed successfully")

        return {
            "status": "success",
            "backend": backend,
            "model": model,
            "prompt": prompt,
            "workspace": workspace,
            "error": None,
            "runtime_model": result.get("model") if isinstance(result, dict) else model,
            "generated_code": result.get("generated_code") if isinstance(result, dict) else None,
            "artifact_path": result.get("artifact_path") if isinstance(result, dict) else None,
            "usage": result.get("usage") if isinstance(result, dict) else None,
            "trajectory": result.get("trajectory") if isinstance(result, dict) else None,
        }

    except Exception as e:
        logger.error(f"SIA agent execution failed: {e}", exc_info=True)
        return {
            "status": "error",
            "backend": backend,
            "model": model,
            "prompt": prompt,
            "workspace": workspace,
            "error": str(e),
            "trajectory": None,
        }


def write_output(output_data: Dict[str, Any], workspace: str) -> None:
    """
    Write execution result to output.json with credential sanitization.

    Args:
        output_data: Execution result to write
        workspace: Workspace directory path
    """
    output_file = Path(workspace) / "output.json"

    # Sanitize credentials before writing
    sanitized_data = sanitize_credentials(output_data)

    try:
        with open(output_file, "w") as f:
            json.dump(sanitized_data, f, indent=2)
        logger.info(f"Output written to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}", exc_info=True)
        sys.exit(1)


def resolve_evaluator_script() -> Optional[Path]:
    """Resolve evaluator script path from env override or task default."""
    override = os.getenv("CWSO_EVALUATOR_SCRIPT", "").strip()
    if override:
        candidate = Path(override).expanduser()
        return candidate if candidate.exists() else None

    default = (
        Path(__file__).resolve().parent
        / "tasks"
        / "emage-agent-task-v1"
        / "data"
        / "public"
        / "evaluate.py"
    )
    return default if default.exists() else None


def run_evaluator(workspace: str) -> Dict[str, Any]:
    """Execute evaluator to materialize results.json for reward extraction."""
    evaluator_script = resolve_evaluator_script()
    if evaluator_script is None:
        return {
            "status": "skipped",
            "reason": "evaluator_script_not_found",
            "results_path": str(Path(workspace) / "results.json"),
        }

    results_path = Path(workspace) / "results.json"
    command = [
        sys.executable,
        str(evaluator_script),
        "--gen-dir",
        workspace,
        "--out",
        str(results_path),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "reason": "evaluator_timeout",
            "results_path": str(results_path),
        }

    if completed.returncode != 0:
        return {
            "status": "failed",
            "reason": "evaluator_nonzero_exit",
            "exit_code": completed.returncode,
            "stderr": (completed.stderr or "")[:500],
            "results_path": str(results_path),
        }

    if not results_path.exists():
        return {
            "status": "failed",
            "reason": "results_not_written",
            "results_path": str(results_path),
        }

    try:
        results = json.loads(results_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "failed",
            "reason": "results_parse_error",
            "error": str(exc),
            "results_path": str(results_path),
        }

    return {
        "status": "success",
        "results_path": str(results_path),
        "results": results,
    }


def attempt_reward_attachment(
    workspace: str,
    dispatch_result: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Attempt to attach reward to job if dispatch_result available.

    This is called post-job completion. The dispatch_result is typically
    injected by the CWSO harness launcher and contains workspace_uuid and
    rollout_session_id for trajectory linking.

    T224 Integration Point:
    - CWSO launcher calls harness with -e CWSO_DISPATCH_RESULT='{...json...}'
    - After job completes, this function is called
    - If successful, reward is attached to the trajectory record
    - If CWSO unavailable (development), graceful failure (logged but not fatal)

    Args:
        workspace: Path to workspace (where results.json is located)
        dispatch_result: Optional dispatch result from CWSO launcher

    Returns:
        True if reward attached successfully or skipped gracefully, False if error
    """
    if not HAS_REWARD_ATTACHMENT:
        logger.debug("Reward attachment skipped: module not available")
        return True

    # Check if dispatch result was injected
    if dispatch_result is None:
        dispatch_result_env = os.getenv("CWSO_DISPATCH_RESULT")
        if dispatch_result_env:
            try:
                dispatch_result = json.loads(dispatch_result_env)
            except json.JSONDecodeError as e:
                logger.warning(f"CWSO_DISPATCH_RESULT is not valid JSON: {e}")
                return True

    if not dispatch_result:
        logger.debug("No dispatch_result provided; reward attachment skipped")
        return True

    try:
        log_msg = attach_reward_to_job(
            dispatch_result,
            workspace,
            fail_gracefully=True  # Don't fail the job if CWSO is unavailable
        )
        logger.info(log_msg)
        return True
    except Exception as e:
        logger.error(f"Reward attachment error (non-fatal): {e}")
        return True  # Non-fatal: job succeeded even if reward attachment failed


async def main() -> None:
    """Main entrypoint."""
    try:
        # Validate environment and configuration
        config = validate_environment()

        # Run SIA agent
        result = await run_sia_agent(
            backend=config["backend"],
            model=config["model"],
            prompt=config["prompt"],
            max_turns=int(config["max_turns"]),
            workspace=config["workspace"],
        )

        evaluation_result = run_evaluator(config["workspace"])
        result["evaluation_status"] = evaluation_result.get("status")
        result["results_path"] = evaluation_result.get("results_path")
        if evaluation_result.get("status") == "success":
            result["evaluation"] = evaluation_result.get("results")
        else:
            result["evaluation_error"] = {
                key: value
                for key, value in evaluation_result.items()
                if key not in {"results"}
            }

        # Write output with sanitization
        write_output(result, config["workspace"])

        # T224: Attempt reward attachment post-job (graceful failure)
        if result["status"] == "success":
            attempt_reward_attachment(config["workspace"])

        # Exit with appropriate status
        if result["status"] == "success":
            logger.info("Harness execution completed successfully")
            sys.exit(0)
        else:
            logger.error(f"Harness execution failed: {result.get('error')}")
            sys.exit(1)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
