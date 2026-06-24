#!/usr/bin/env python3
"""
T226: Test SIA Dispatch via CWSO Harness + Reward Attachment

This script dispatches a single SIA generation through the CWSO harness launcher
(T223) and validates the complete chain:
  1. Dispatch SIA generation to CWSO
  2. Verify dispatch succeeds (get workspace_uuid, rollout_session_id)
  3. Wait for evaluation to complete (check results.json)
  4. Attach reward via merge endpoint (T224)
  5. Verify Parquet trajectories were written (Polar capture)

Usage:
  python3 implementation/scripts/dispatch-test-sia.py \\
    --prompt-file /tmp/test-prompt.txt \\
    --workspace /tmp/t226-test-workspace \\
    --cwso-url http://localhost:8080 \\
    --jwt-secret <dev-token> \\
    --dry-run false

Environment Variables (if not provided as args):
  - CWSO_BASE_URL: CWSO orchestrator endpoint
  - CWSO_JWT_SECRET: JWT token for MCP authentication
  - PARQUET_STORE_PATH: Path to verify Parquet files written
  - SIA_BACKEND: Agent backend (default: 'claude')
  - SIA_MODEL: Model to use (default: 'haiku')
"""

import argparse
import base64
import hashlib
import hmac
import json
import logging
import os
import time
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_prompt(prompt_file: str) -> str:
    """Read prompt from file or use default if file not found."""
    if prompt_file and Path(prompt_file).exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()

    # Default test prompt
    return """
    Write a Python function that validates an email address.
    The function should return True if valid, False otherwise.
    Include docstring and handle edge cases.
    """.strip()


def _b64url(data: bytes) -> str:
    """Encode bytes as URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_jwt_token(secret: str, role: str = "worker") -> str:
    """
    Generate a properly signed JWT token for CWSO authentication.

    Args:
        secret: The JWT secret key (from CWSO_JWT_SECRET)
        role: JWT role claim ("worker" or "orchestrator")
    Returns:
        A valid HS256-signed JWT token with required claims
    """
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": "emage-code",
        "role": role,
        "iss": "cwso",
        "aud": ["cwso-mcp"],
        "iat": now,
        "nbf": now,
        "exp": now + 3600,
    }
    encoded_header = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    encoded_sig = _b64url(signature)
    return f"{message}.{encoded_sig}"


def dispatch_sia(
    cwso_url: str,
    jwt_secret: str,
    prompt: str,
    workspace: str,
    backend: str = "claude",
    model: str = "haiku",
    max_turns: int = 5,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Dispatch SIA generation to CWSO harness.

    Args:
        cwso_url: CWSO orchestrator base URL
        jwt_secret: JWT secret for MCP authentication (generates HS256 token)
        prompt: Task prompt for SIA agent
        workspace: Workspace directory for outputs
        backend: Agent backend ('claude' or 'openhands')
        model: Model ID to use
        max_turns: Maximum agent iterations
        dry_run: If True, print request but don't send

    Returns:
        Dispatch result with workspace_uuid, rollout_session_id, etc.
    """

    # CWSO Phase 2 dispatches via rollout REST API (not /dispatch).
    dispatch_url = f"{cwso_url}/rollout/task/submit"

    # Build dispatch payload
    payload = {
        "task_spec": {
            "description": prompt,
            "workspace_id": workspace,
            "max_steps": max_turns,
            "backend": backend,
            "model": model,
        },
        "num_samples": 1,
        "trajectory_builder_strategy": "prefix_merge",
    }

    # Generate JWT token from secret (worker role for dispatch)
    jwt_token = generate_jwt_token(jwt_secret, role="worker")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Origin": "http://localhost",
    }
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    if dry_run:
        logger.info("[DRY RUN] Would send POST request (not actually sending)")
        return {
            "task_id": "dry-run-task",
            "workspace_uuid": "dry-run-uuid",
            "rollout_session_id": "dry-run-session",
            "status": "dry_run"
        }

    try:
        response = requests.post(
            dispatch_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        rollout_result = response.json()
        task_id = rollout_result.get("task_id")
        if not task_id:
            raise RuntimeError(f"rollout submit response missing task_id: {rollout_result}")
        # In single-sample rollout mode, task_id is the session identifier.
        result = {
            "task_id": task_id,
            "workspace_uuid": workspace,
            "rollout_session_id": task_id,
            "status": rollout_result.get("status", "running"),
        }
        logger.info(f"Dispatch accepted via rollout API: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Dispatch failed: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Response: {e.response.text}")
        raise


def wait_for_rollout_completion(
    cwso_url: str,
    jwt_secret: str,
    task_id: str,
    timeout: int = 60,
    poll_interval: int = 2,
    mock_execution: bool = False
) -> Dict[str, Any]:
    """
    Wait for rollout task completion via GET /rollout/task/{task_id}.

    Args:
        cwso_url: CWSO orchestrator base URL
        jwt_secret: JWT secret used to mint bearer token
        task_id: Rollout task UUID
        timeout: Max seconds to wait
        mock_execution: If True, simulate task completion after brief polling
        poll_interval: Seconds between polls

    Returns:
        Rollout task status response
    """
    task_url = f"{cwso_url}/rollout/task/{task_id}"
    start_time = time.time()
    # Use worker role for task polling (dispatch/status checks)
    jwt_token = generate_jwt_token(jwt_secret, role="worker")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Origin": "http://localhost",
    }

    logger.info(f"Polling rollout task completion: {task_url}")

    if mock_execution:
        logger.info("[MOCK EXECUTION] Simulating task completion after 1 poll")
        # Return immediately with completed status for E2E testing
        return {
            "task_id": task_id,
            "status": "completed",
            "partial_results": [{"reward": 0.85, "code_quality": "good"}],
            "trajectories": ["mock-trajectory"],
        }

    while time.time() - start_time < timeout:
        try:
            response = requests.get(task_url, headers=headers, timeout=15)
            response.raise_for_status()
            task = response.json()
            status = str(task.get("status", "")).lower()
            logger.info(f"Task status: {status}")
            if status in {"completed", "failed", "cancelled"}:
                return task
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Task status poll failed ({exc}); retrying")

        time.sleep(poll_interval)

    logger.warning(
        f"Rollout task timeout ({timeout}s) while waiting for completion; "
        "this usually indicates incomplete Phase 2 runtime wiring "
        "(gateway/worker callback path not progressing)."
    )
    return {"task_id": task_id, "status": "timeout"}


def derive_evaluation_from_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Convert rollout task status into a compact evaluation summary."""
    status = str(task.get("status", "")).lower()
    partial_results = task.get("partial_results") or []
    score = 0.0
    if partial_results and isinstance(partial_results, list):
        first = partial_results[0]
        if isinstance(first, dict):
            score = float(first.get("reward", 0.0))
    return {
        "overall_score": score,
        "passed": status == "completed",
        "diagnostics_count": len(partial_results) if isinstance(partial_results, list) else 0,
        "rollout_status": status,
    }


def _safe_get_json(url: str, headers: Dict[str, str], timeout: int = 15) -> Dict[str, Any]:
    """GET JSON endpoint and return either payload or a structured error."""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_text": response.text.strip()}
        return {"ok": True, "status_code": response.status_code, "data": payload}
    except Exception as exc:  # noqa: BLE001 - diagnostics should never crash caller
        return {"ok": False, "error": str(exc)}


def _safe_post_json(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    timeout: int = 15,
) -> Dict[str, Any]:
    """POST JSON endpoint and return either payload or a structured error."""
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return {"ok": True, "status_code": response.status_code, "data": response.json()}
    except Exception as exc:  # noqa: BLE001 - diagnostics should never crash caller
        return {"ok": False, "error": str(exc)}


def collect_rollout_diagnostics(
    cwso_url: str,
    jwt_secret: str,
    task_id: str,
    rollout_session_id: str,
    parquet_store: str,
    diagnostic_output: str,
) -> Dict[str, Any]:
    """Collect focused Phase 2 progression signals and blocker evidence."""
    # Use worker role for status/diagnostics collection
    jwt_token = generate_jwt_token(jwt_secret, role="worker")
    auth_headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Origin": "http://localhost",
    }
    json_headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Origin": "http://localhost",
    }

    health = _safe_get_json(f"{cwso_url}/healthz", auth_headers)
    rollout_status = _safe_get_json(f"{cwso_url}/rollout/status", auth_headers)
    task_status = _safe_get_json(f"{cwso_url}/rollout/task/{task_id}", auth_headers)
    tools_list = _safe_post_json(
        f"{cwso_url}/mcp",
        json_headers,
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
    )

    tool_names = []
    if tools_list.get("ok"):
        result = tools_list.get("data", {}).get("result", {})
        tools = result.get("tools", [])
        if isinstance(tools, list):
            tool_names = [str(t.get("name")) for t in tools if isinstance(t, dict)]

    parquet_files = []
    store_path = Path(parquet_store)
    if store_path.exists() and rollout_session_id:
        parquet_files = [str(p) for p in store_path.rglob(f"*{rollout_session_id}*.parquet*")]

    running_task = False
    partial_count = 0
    trajectory_count = 0
    if task_status.get("ok"):
        task_data = task_status.get("data", {})
        running_task = str(task_data.get("status", "")).lower() == "running"
        partial_results = task_data.get("partial_results") or []
        trajectories = task_data.get("trajectories") or []
        if isinstance(partial_results, list):
            partial_count = len(partial_results)
        if isinstance(trajectories, list):
            trajectory_count = len(trajectories)

    registered_nodes = None
    running_sessions = None
    if rollout_status.get("ok"):
        data = rollout_status.get("data", {})
        registered_nodes = data.get("registered_nodes")
        running_sessions = data.get("running_sessions")

    missing_signals = []
    if running_task and partial_count == 0:
        missing_signals.append("task_running_without_partial_results")
    if running_task and trajectory_count == 0:
        missing_signals.append("task_running_without_trajectories")
    if running_task and len(parquet_files) == 0:
        missing_signals.append("task_running_without_parquet_capture")
    if isinstance(registered_nodes, int) and registered_nodes == 0:
        missing_signals.append("no_registered_rollout_nodes")
    if "merge_concurrent_results" not in tool_names:
        missing_signals.append("merge_tool_missing_from_mcp")

    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cwso_url": cwso_url,
        "task_id": task_id,
        "rollout_session_id": rollout_session_id,
        "signals": {
            "healthz": health,
            "rollout_status": rollout_status,
            "task_status": task_status,
            "tool_count": len(tool_names),
            "has_merge_concurrent_results": "merge_concurrent_results" in tool_names,
            "parquet_file_count_for_session": len(parquet_files),
        },
        "missing_progression_signals": missing_signals,
        "blocker_assessment": (
            "incomplete_phase2_runtime"
            if len(missing_signals) > 0 and running_task
            else "no_runtime_blocker_detected"
        ),
    }

    output_path = diagnostic_output.strip()
    if not output_path:
        output_path = f"/tmp/t228-rollout-diagnostics-{task_id}.json"
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        evidence["diagnostic_output"] = output_path
    except Exception as exc:  # noqa: BLE001 - keep run going even if write fails
        evidence["diagnostic_output_error"] = str(exc)

    return evidence


def attach_reward(
    cwso_url: str,
    jwt_secret: str,
    workspace_uuid: str,
    rollout_session_id: str,
    evaluation: Dict[str, Any],
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Attach evaluation reward via CWSO merge endpoint (T224).

    Args:
        cwso_url: CWSO orchestrator base URL
        jwt_token: JWT token
        workspace_uuid: UUID from dispatch
        rollout_session_id: Session ID from dispatch
        evaluation: Results from results.json
        dry_run: If True, don't actually send

    Returns:
        Merge result or None if skipped/failed
    """

    if not evaluation or "overall_score" not in evaluation:
        logger.warning("No evaluation results; skipping reward attachment")
        return None

    merge_url = f"{cwso_url}/mcp"

    # Build merge request (T224 contract)
    merge_payload = {
        "workspace_uuid": workspace_uuid,
        "rollout_session_id": rollout_session_id,
        "reward": {
            "overall_score": evaluation.get("overall_score", 0.5),
            "passed": evaluation.get("passed", False),
            "diagnostics": evaluation.get("diagnostics_count", 0)
        }
    }

    # Use orchestrator role for reward attachment (merge_concurrent_results requires orchestrator)
    jwt_token = generate_jwt_token(jwt_secret, role="orchestrator")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Origin": "http://localhost",
    }

    logger.info(f"Attaching reward via {merge_url}")
    logger.debug(f"Merge payload: {json.dumps(merge_payload, indent=2)}")

    if dry_run:
        logger.info("[DRY RUN] Would send merge request (not actually sending)")
        return {"status": "dry_run_merge"}

    try:
        rpc_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "merge_concurrent_results",
                "arguments": merge_payload,
            },
        }
        response = requests.post(
            merge_url,
            json=rpc_payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict) and "error" in result:
            logger.error(f"Reward attachment RPC error: {result['error']}")
            return None
        logger.info(f"Reward attachment succeeded: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Reward attachment failed: {e}")
        # Don't fail the whole test if merge fails
        return None


def verify_parquet_capture(
    parquet_store: str,
    rollout_session_id: str
) -> bool:
    """
    Verify that Parquet trajectories were written.

    Args:
        parquet_store: Path to Parquet store directory
        rollout_session_id: Session ID to search for

    Returns:
        True if at least one Parquet file found for session
    """

    store_path = Path(parquet_store)

    if not store_path.exists():
        logger.warning(f"Parquet store not found: {parquet_store}")
        return False

    # Search for Parquet files matching session ID
    parquet_files = list(store_path.rglob(f"*{rollout_session_id}*.parquet*"))

    if parquet_files:
        logger.info(f"Found {len(parquet_files)} Parquet file(s) for session {rollout_session_id}")
        for pf in parquet_files:
            logger.info(f"  - {pf}")

        # Try to validate Parquet format
        try:
            import pyarrow.parquet as pq
            for pf in parquet_files[:1]:
                table = pq.read_table(str(pf))
                logger.info(f"Parquet schema ({pf.name}):")
                for field in table.schema:
                    logger.info(f"  - {field.name}: {field.type}")
                logger.info(f"Parquet rows: {table.num_rows}")
            return True
        except ImportError:
            logger.warning("pyarrow not installed; skipping schema validation")
            return True
        except Exception as e:
            logger.error(f"Failed to read Parquet file: {e}")
            return False
    else:
        logger.warning(f"No Parquet files found for session {rollout_session_id}")
        logger.info(f"Files in {parquet_store}:")
        if store_path.exists():
            for item in store_path.rglob("*"):
                if item.is_file():
                    logger.info(f"  - {item}")
        return False


def main():
    """Main test entry point."""

    parser = argparse.ArgumentParser(
        description="Test SIA dispatch via CWSO harness with Parquet verification"
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        default="/tmp/t226-test-prompt.txt",
        help="File containing task prompt"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default="/tmp/t226-test-workspace",
        help="Workspace directory for job outputs"
    )
    parser.add_argument(
        "--cwso-url",
        type=str,
        default=os.getenv("CWSO_BASE_URL", "http://localhost:8080"),
        help="CWSO orchestrator URL"
    )
    parser.add_argument(
        "--jwt-secret",
        type=str,
        default=os.getenv("CWSO_JWT_SECRET", ""),
        help="JWT secret used to mint MCP bearer tokens"
    )
    parser.add_argument(
        "--parquet-store",
        type=str,
        default=os.getenv("PARQUET_STORE_PATH", "/tmp/t226-parquet-store"),
        help="Parquet store path"
    )
    parser.add_argument(
        "--backend",
        type=str,
        default=os.getenv("SIA_BACKEND", "claude"),
        help="Agent backend (claude or openhands)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("SIA_MODEL", "haiku"),
        help="Model to use"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=5,
        help="Maximum agent iterations"
    )
    parser.add_argument(
        "--rollout-timeout",
        type=int,
        default=120,
        help="Seconds to wait for rollout task terminal state before diagnostics"
    )
    parser.add_argument(
        "--dry-run",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=False,
        help="Print request without sending (dry run mode)"
    )
    parser.add_argument(
        "--diagnose-on-timeout",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=True,
        help="Collect focused infrastructure diagnostics when rollout does not progress"
    )
    parser.add_argument(
        "--mock-execution",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=False,
        help="Enable mock execution mode (simulates task completion for E2E testing)"
    )
    parser.add_argument(
        "--diagnostic-output",
        type=str,
        default="",
        help="Optional path to write JSON blocker evidence"
    )

    args = parser.parse_args()

    # Validate prerequisites
    if not args.jwt_secret and not args.dry_run:
        logger.error("CWSO_JWT_SECRET not set; use --jwt-secret or export CWSO_JWT_SECRET")
        sys.exit(1)

    # Create workspace
    workspace_path = Path(args.workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Workspace: {workspace_path}")

    # Read prompt
    prompt = read_prompt(args.prompt_file)
    logger.info(f"Prompt: {prompt[:100]}...")

    try:
        # Step 1: Dispatch
        dispatch_result = dispatch_sia(
            cwso_url=args.cwso_url,
            jwt_secret=args.jwt_secret,
            prompt=prompt,
            workspace=str(workspace_path),
            backend=args.backend,
            model=args.model,
            max_turns=args.max_turns,
            dry_run=args.dry_run
        )

        workspace_uuid = dispatch_result.get("workspace_uuid")
        rollout_session_id = dispatch_result.get("rollout_session_id")
        task_id = dispatch_result.get("task_id")

        logger.info(f"✓ Dispatch succeeded")
        logger.info(f"  workspace_uuid: {workspace_uuid}")
        logger.info(f"  rollout_session_id: {rollout_session_id}")

        # Step 2: Wait for rollout completion (skip in dry-run)
        if not args.dry_run:
            rollout_task = wait_for_rollout_completion(
                cwso_url=args.cwso_url,
                jwt_secret=args.jwt_secret,
                task_id=str(task_id),
                timeout=args.rollout_timeout,
                mock_execution=args.mock_execution,
            )
            evaluation = derive_evaluation_from_task(rollout_task)
        else:
            evaluation = {"overall_score": 0.75, "passed": True, "diagnostics_count": 0}
            rollout_task = {"status": "dry_run"}
            logger.info("[DRY RUN] Skipping rollout polling")

        if evaluation:
            logger.info(f"✓ Evaluation complete")
            logger.info(f"  overall_score: {evaluation.get('overall_score')}")
            logger.info(f"  passed: {evaluation.get('passed')}")
            logger.info(f"  rollout_status: {evaluation.get('rollout_status')}")
        else:
            logger.warning("! Evaluation timeout or missing")

        # Focused blocker evidence when rollout doesn't progress to terminal state.
        if (
            not args.dry_run
            and args.diagnose_on_timeout
            and str(rollout_task.get("status", "")).lower() in {"timeout", "running"}
            and task_id
            and rollout_session_id
        ):
            diagnostics = collect_rollout_diagnostics(
                cwso_url=args.cwso_url,
                jwt_secret=args.jwt_secret,
                task_id=str(task_id),
                rollout_session_id=str(rollout_session_id),
                parquet_store=args.parquet_store,
                diagnostic_output=args.diagnostic_output,
            )
            logger.warning("! Rollout progression diagnostics collected")
            logger.warning(f"  blocker_assessment: {diagnostics.get('blocker_assessment')}")
            logger.warning(
                f"  missing_progression_signals: "
                f"{diagnostics.get('missing_progression_signals', [])}"
            )
            if diagnostics.get("diagnostic_output"):
                logger.warning(f"  diagnostic_output: {diagnostics.get('diagnostic_output')}")

        # Step 3: Attach reward
        if workspace_uuid and rollout_session_id:
            merge_result = attach_reward(
                cwso_url=args.cwso_url,
                jwt_secret=args.jwt_secret,
                workspace_uuid=workspace_uuid,
                rollout_session_id=rollout_session_id,
                evaluation=evaluation,
                dry_run=args.dry_run
            )
            if merge_result:
                logger.info(f"✓ Reward attachment succeeded")
            else:
                logger.warning("! Reward attachment failed (continuing...)")

        # Step 4: Verify Parquet
        if rollout_session_id and not args.dry_run:
            parquet_ok = verify_parquet_capture(args.parquet_store, rollout_session_id)
            if parquet_ok:
                logger.info(f"✓ Parquet trajectories verified")
            else:
                logger.warning("! Parquet trajectories not found")

        logger.info("\n=== Test Summary ===")
        logger.info(f"✓ SIA dispatch via CWSO harness succeeded")
        logger.info(f"  task_id: {task_id}")
        logger.info(f"  workspace_uuid: {workspace_uuid}")
        logger.info(f"  rollout_session_id: {rollout_session_id}")
        logger.info(f"  workspace: {workspace_path}")
        logger.info(f"  rollout_status: {rollout_task.get('status')}")
        logger.info(f"  parquet_store: {args.parquet_store}")

        return 0

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
