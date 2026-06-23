#!/usr/bin/env python3
"""
T224: Reward Attachment via Merge

This module implements reward attachment in the CWSO merge orchestration layer.
When a SIA generation completes via the harness launcher, the evaluator produces
a results.json with overall_score and passed fields. This module sends that reward
signal to the CWSO merge engine via merge_concurrent_results, which attaches the
evaluation result to the trajectory record captured in the Parquet store.

Environment Variables:
- CWSO_BASE_URL (default: http://localhost:8080): CWSO endpoint base URL
- CWSO_JWT_SECRET: JWT token for CWSO authentication
"""

import json
import logging
import os
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


def read_evaluation_result(workspace_path: str) -> Dict[str, Any]:
    """
    Read results.json from completed job workspace.

    The results.json file is produced by the T222 evaluator and contains
    the overall_score, passed flag, and diagnostics for the job execution.

    Args:
        workspace_path: Path to job workspace (from DispatchResult)

    Returns:
        Dictionary with evaluation results including:
        - overall_score: float [0, 1]
        - passed: bool
        - diagnostics_count: int
        - (and any other evaluator-produced fields)

    Raises:
        FileNotFoundError: If results.json not found in workspace
        json.JSONDecodeError: If results.json is malformed
        ValueError: If required fields are missing
    """
    results_path = Path(workspace_path) / "results.json"

    if not results_path.exists():
        raise FileNotFoundError(
            f"results.json not found in {workspace_path}. "
            "Ensure evaluator has completed before calling reward attachment."
        )

    try:
        with open(results_path, encoding="utf-8") as f:
            results = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to parse results.json: {e.msg}",
            e.doc,
            e.pos
        )

    # Validate required fields
    required = ["overall_score", "passed"]
    missing = [k for k in required if k not in results]
    if missing:
        raise ValueError(
            f"results.json missing required fields: {missing}. "
            f"Present fields: {list(results.keys())}"
        )

    logger.info(
        f"Evaluation result read: score={results['overall_score']:.2f}, "
        f"passed={results['passed']}"
    )
    return results


def build_merge_request(
    dispatch_result: Dict[str, str],
    evaluation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build MergeRequest payload for CWSO merge_concurrent_results endpoint.

    Transforms the dispatch result and evaluation into the schema required
    by the CWSO merge orchestration layer. The merge request includes:
    - Identifiers linking to the trajectory record
    - Evaluation reward signal (0..1 range)
    - Outcome flags (passed/failed)
    - Diagnostic metadata

    Args:
        dispatch_result: From harness dispatch_concurrent_jobs, containing:
            - workspace_uuid: str (unique identifier)
            - rollout_session_id: str (links to trajectory record)
        evaluation: From read_evaluation_result(), containing:
            - overall_score: float [0, 1]
            - passed: bool
            - diagnostics_count: int (optional)

    Returns:
        MergeRequest dictionary with schema:
        {
            "workspace_uuid": str,
            "rollout_session_id": str,
            "evaluation_reward": float [0, 1],
            "evaluation_passed": bool,
            "finish_reason": str ("success" or "failure"),
            "diagnostics_count": int,
            "attach_timestamp": str (ISO8601 with Z suffix)
        }

    Raises:
        KeyError: If dispatch_result missing required fields
        TypeError: If evaluation fields have unexpected types
    """
    try:
        overall_score = float(evaluation["overall_score"])
        if not 0.0 <= overall_score <= 1.0:
            logger.warning(
                f"overall_score {overall_score} outside [0, 1] range; clamping"
            )
            overall_score = max(0.0, min(1.0, overall_score))

        passed = bool(evaluation["passed"])
        diagnostics_count = int(evaluation.get("diagnostics_count", 0))

    except (KeyError, TypeError, ValueError) as e:
        raise TypeError(f"Invalid evaluation data type: {e}")

    merge_request = {
        "workspace_uuid": dispatch_result["workspace_uuid"],
        "rollout_session_id": dispatch_result["rollout_session_id"],
        "evaluation_reward": overall_score,
        "evaluation_passed": passed,
        "finish_reason": "success" if passed else "failure",
        "diagnostics_count": diagnostics_count,
        "attach_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    logger.info(
        f"Built merge request: workspace={merge_request['workspace_uuid'][:8]}..., "
        f"rollout_session={merge_request['rollout_session_id']}, "
        f"reward={merge_request['evaluation_reward']}, "
        f"passed={merge_request['evaluation_passed']}"
    )
    return merge_request


def attach_reward_via_merge(
    merge_request: Dict[str, Any],
    cwso_base_url: str,
    jwt_token: str,
    timeout: int = 5
) -> Dict[str, Any]:
    """
    Call CWSO merge_concurrent_results endpoint with evaluation reward.

    Sends the reward signal to the CWSO orchestration layer, which embeds
    the evaluation result into the trajectory record for future training
    and analysis.

    Args:
        merge_request: Payload from build_merge_request()
        cwso_base_url: CWSO endpoint base URL (e.g., "http://localhost:8080")
        jwt_token: CWSO JWT authentication token
        timeout: Request timeout in seconds (default: 5)

    Returns:
        MergeResult dictionary with schema:
        {
            "merged": bool,
            "conflict_resolution_strategy": str,
            "trajectory_id": str
        }

    Raises:
        ConnectionError: If CWSO is unavailable or request fails
        ValueError: If response is invalid JSON or missing required fields
    """
    url = f"{cwso_base_url}/mcp/merge_concurrent_results"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    logger.info(f"Calling CWSO merge endpoint: POST {url}")

    try:
        response = requests.post(
            url,
            json=merge_request,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()

        merge_result = response.json()
        logger.info(
            f"Merge succeeded: trajectory_id={merge_result.get('trajectory_id', 'N/A')}, "
            f"merged={merge_result.get('merged', False)}"
        )
        return merge_result

    except requests.exceptions.Timeout as e:
        raise ConnectionError(
            f"CWSO merge request timed out after {timeout}s: {e}"
        )
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Failed to connect to CWSO endpoint: {e}")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(
            f"CWSO merge endpoint returned HTTP {response.status_code}: {response.text}"
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"CWSO response is not valid JSON: {e}")
    except Exception as e:
        raise ConnectionError(f"Unexpected error during merge: {e}")


def attach_reward_to_job(
    dispatch_result: Dict[str, str],
    workspace_path: str,
    cwso_base_url: Optional[str] = None,
    cwso_jwt: Optional[str] = None,
    fail_gracefully: bool = True
) -> str:
    """
    Orchestrate reward attachment for completed job.

    This is the main entry point for T224. It coordinates all steps:
    1. Read evaluation result from job workspace
    2. Build merge request with reward signal
    3. Attach reward to trajectory via CWSO merge orchestration
    4. Log the result and return status message

    Args:
        dispatch_result: From harness dispatch_concurrent_jobs containing:
            - workspace_uuid: str
            - rollout_session_id: str
        workspace_path: Path to job workspace (where results.json is located)
        cwso_base_url: CWSO endpoint (default: $CWSO_BASE_URL or http://localhost:8080)
        cwso_jwt: CWSO JWT token (default: $CWSO_JWT_SECRET)
        fail_gracefully: If True, log errors but don't fail job; if False, raise on error

    Returns:
        log_message: Status string with format:
        "Reward attached: rollout_session_id={id}, score={score}, passed={passed}"

    Raises:
        RuntimeError: If fail_gracefully=False and any step fails
        FileNotFoundError: If results.json not found
        ValueError: If required fields are missing
    """
    cwso_base_url = cwso_base_url or os.getenv(
        "CWSO_BASE_URL", "http://localhost:8080"
    )
    cwso_jwt = cwso_jwt or os.getenv("CWSO_JWT_SECRET", "")

    try:
        # Step 1: Read evaluation result
        evaluation = read_evaluation_result(workspace_path)
        logger.info(
            f"Step 1/3 complete: Evaluation read "
            f"(score={evaluation['overall_score']}, passed={evaluation['passed']})"
        )

        # Step 2: Build merge request
        merge_req = build_merge_request(dispatch_result, evaluation)
        logger.info("Step 2/3 complete: Merge request built")

        # Step 3: Attach reward via CWSO merge
        if not cwso_jwt:
            logger.warning(
                "CWSO_JWT_SECRET not set; merge attachment skipped (testing mode)"
            )
            return (
                f"Reward attached (mock): "
                f"rollout_session_id={dispatch_result['rollout_session_id']}, "
                f"score={evaluation['overall_score']}, "
                f"passed={evaluation['passed']}"
            )

        merge_result = attach_reward_via_merge(merge_req, cwso_base_url, cwso_jwt)
        logger.info("Step 3/3 complete: Reward attached to trajectory")

        # Step 4: Log result
        log_msg = (
            f"Reward attached: "
            f"rollout_session_id={dispatch_result['rollout_session_id']}, "
            f"score={evaluation['overall_score']}, "
            f"passed={evaluation['passed']}, "
            f"trajectory_id={merge_result.get('trajectory_id', 'N/A')}"
        )
        logger.info(log_msg)
        return log_msg

    except Exception as e:
        error_msg = f"Reward attachment failed: {e}"
        logger.error(error_msg, exc_info=True)

        if fail_gracefully:
            logger.warning("Continuing despite error (fail_gracefully=True)")
            return (
                f"Reward attachment skipped due to error: {type(e).__name__} "
                f"(see logs for details)"
            )
        else:
            raise RuntimeError(error_msg) from e


if __name__ == "__main__":
    # Example usage (for testing/demonstration)
    import sys

    if len(sys.argv) < 3:
        print("Usage: python reward-attachment.py <workspace_path> <session_id>")
        print("\nExample:")
        print("  python reward-attachment.py /tmp/workspace uuid-123-456")
        sys.exit(1)

    workspace_path = sys.argv[1]
    session_id = sys.argv[2]

    dispatch_result = {
        "workspace_uuid": "workspace-uuid-placeholder",
        "rollout_session_id": session_id,
    }

    result = attach_reward_to_job(dispatch_result, workspace_path)
    print(result)
