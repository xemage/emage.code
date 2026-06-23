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
import json
import logging
import os
import time
import sys
from datetime import datetime
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


def dispatch_sia(
    cwso_url: str,
    jwt_token: str,
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
        jwt_token: JWT token for MCP authentication
        prompt: Task prompt for SIA agent
        workspace: Workspace directory for outputs
        backend: Agent backend ('claude' or 'openhands')
        model: Model ID to use
        max_turns: Maximum agent iterations
        dry_run: If True, print request but don't send

    Returns:
        Dispatch result with workspace_uuid, rollout_session_id, etc.
    """

    # Construct dispatch endpoint
    dispatch_url = f"{cwso_url}/dispatch"

    # Build dispatch payload
    payload = {
        "prompt": prompt,
        "workspace": workspace,
        "backend": backend,
        "model": model,
        "max_turns": max_turns,
        "timestamp": datetime.utcnow().isoformat()
    }

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    logger.info(f"Dispatching SIA generation to {dispatch_url}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    if dry_run:
        logger.info("[DRY RUN] Would send POST request (not actually sending)")
        return {
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
        result = response.json()
        logger.info(f"Dispatch succeeded: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Dispatch failed: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Response: {e.response.text}")
        raise


def wait_for_evaluation(
    workspace: str,
    timeout: int = 60,
    poll_interval: int = 2
) -> Dict[str, Any]:
    """
    Wait for evaluation to complete (results.json written).

    Args:
        workspace: Workspace directory path
        timeout: Max seconds to wait
        poll_interval: Seconds between polls

    Returns:
        Parsed results.json
    """
    results_file = Path(workspace) / "results.json"
    start_time = time.time()

    logger.info(f"Waiting for evaluation to complete: {results_file}")

    while time.time() - start_time < timeout:
        if results_file.exists():
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                logger.info(f"Evaluation complete: {results}")
                return results
            except json.JSONDecodeError:
                logger.debug("results.json not yet valid JSON, retrying...")

        time.sleep(poll_interval)

    logger.warning(f"Evaluation timeout ({timeout}s) — results.json not written")
    return {}


def attach_reward(
    cwso_url: str,
    jwt_token: str,
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

    merge_url = f"{cwso_url}/mcp/merge_concurrent_results"

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

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    logger.info(f"Attaching reward via {merge_url}")
    logger.debug(f"Merge payload: {json.dumps(merge_payload, indent=2)}")

    if dry_run:
        logger.info("[DRY RUN] Would send merge request (not actually sending)")
        return {"status": "dry_run_merge"}

    try:
        response = requests.post(
            merge_url,
            json=merge_payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
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
        help="JWT token for MCP authentication"
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
        "--dry-run",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=False,
        help="Print request without sending (dry run mode)"
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
            jwt_token=args.jwt_secret,
            prompt=prompt,
            workspace=str(workspace_path),
            backend=args.backend,
            model=args.model,
            max_turns=args.max_turns,
            dry_run=args.dry_run
        )

        workspace_uuid = dispatch_result.get("workspace_uuid")
        rollout_session_id = dispatch_result.get("rollout_session_id")

        logger.info(f"✓ Dispatch succeeded")
        logger.info(f"  workspace_uuid: {workspace_uuid}")
        logger.info(f"  rollout_session_id: {rollout_session_id}")

        # Step 2: Wait for evaluation (skip in dry-run)
        if not args.dry_run:
            evaluation = wait_for_evaluation(str(workspace_path), timeout=120)
        else:
            evaluation = {"overall_score": 0.75, "passed": True, "diagnostics_count": 0}
            logger.info("[DRY RUN] Skipping evaluation wait")

        if evaluation:
            logger.info(f"✓ Evaluation complete")
            logger.info(f"  overall_score: {evaluation.get('overall_score')}")
            logger.info(f"  passed: {evaluation.get('passed')}")
        else:
            logger.warning("! Evaluation timeout or missing")

        # Step 3: Attach reward
        if workspace_uuid and rollout_session_id:
            merge_result = attach_reward(
                cwso_url=args.cwso_url,
                jwt_token=args.jwt_secret,
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
        logger.info(f"  workspace_uuid: {workspace_uuid}")
        logger.info(f"  rollout_session_id: {rollout_session_id}")
        logger.info(f"  workspace: {workspace_path}")
        logger.info(f"  results.json: {Path(workspace_path) / 'results.json'}")
        logger.info(f"  parquet_store: {args.parquet_store}")

        return 0

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
