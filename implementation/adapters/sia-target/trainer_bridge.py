#!/usr/bin/env python3
"""
Trainer bridge: Parquet trajectory store → GRPO/SFT dataset.

Reads CompletionRecord rows from Parquet, joins shaped rewards,
and emits dataset manifests for fine-tuning.

T230: Trainer Bridge — Parquet Trajectories → GRPO/SFT Dataset

Environment Variables:
- CWSO_ROLLOUT_TRAJECTORY_STORE_PATH: override default store path
"""

import json
import logging
import math
import os
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema constants — standardised field names after normalisation
# ---------------------------------------------------------------------------
_FIELD_WORKSPACE_UUID = "workspace_uuid"
_FIELD_SESSION_ID = "rollout_session_id"
_FIELD_PROMPT_TOKEN_IDS = "prompt_token_ids"
_FIELD_SAMPLED_TOKEN_IDS = "sampled_token_ids"
_FIELD_LOGPROBS = "logprobs"
_FIELD_FINISH_REASON = "finish_reason"
_FIELD_TIMESTAMP_NS = "timestamp_ns"
_FIELD_EVALUATION_REWARD = "evaluation_reward"
_FIELD_SHAPED_REWARD = "shaped_reward"

_ALL_FIELDS = [
    _FIELD_WORKSPACE_UUID,
    _FIELD_SESSION_ID,
    _FIELD_PROMPT_TOKEN_IDS,
    _FIELD_SAMPLED_TOKEN_IDS,
    _FIELD_LOGPROBS,
    _FIELD_FINISH_REASON,
    _FIELD_TIMESTAMP_NS,
    _FIELD_EVALUATION_REWARD,
    _FIELD_SHAPED_REWARD,
]


# ---------------------------------------------------------------------------
# Path safety helper
# ---------------------------------------------------------------------------

def _assert_safe_path(candidate: str, root: str) -> pathlib.Path:
    """
    Resolve ``candidate`` and verify it does not escape ``root``.

    Raises ValueError on path traversal attempt.
    """
    root_path = pathlib.Path(root).resolve()
    resolved = pathlib.Path(candidate).resolve()
    try:
        resolved.relative_to(root_path)
    except ValueError as exc:
        raise ValueError(
            f"Path traversal detected: {candidate!r} escapes root {root!r}"
        ) from exc
    return resolved


# ---------------------------------------------------------------------------
# Reward resolution helper
# ---------------------------------------------------------------------------

def _resolve_reward(record: Dict[str, Any]) -> Optional[float]:
    """
    Return the best available reward from a trajectory record.

    Preference order: shaped_reward → evaluation_reward → None.
    Non-finite values are treated as missing.
    """
    for field in (_FIELD_SHAPED_REWARD, _FIELD_EVALUATION_REWARD):
        raw = record.get(field)
        if raw is None:
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            return value
    return None


# ---------------------------------------------------------------------------
# 1. read_trajectories
# ---------------------------------------------------------------------------

def read_trajectories(store_path: str) -> List[Dict[str, Any]]:
    """
    Read all .parquet files under ``store_path`` and return normalised records.

    Missing columns default to None. Returns [] when the path does not exist
    or contains no Parquet files.

    Args:
        store_path: Directory to scan recursively for .parquet files.

    Returns:
        List of trajectory dicts with standardised field names.
    """
    root = pathlib.Path(store_path)
    if not root.exists():
        logger.info("store_path %r does not exist; returning empty list", store_path)
        return []

    # POC-DEBT: single-node glob — no distributed/S3 support; production should
    # use a partitioned reader with predicate push-down.
    parquet_files = sorted(root.rglob("*.parquet"))
    if not parquet_files:
        logger.info("No .parquet files found under %r", store_path)
        return []

    try:
        import pyarrow.parquet as pq  # local import — optional dep
    except ModuleNotFoundError as exc:
        raise ImportError(
            "pyarrow is required for reading Parquet files. "
            "Install with: pip install pyarrow"
        ) from exc

    records: List[Dict[str, Any]] = []
    for pq_file in parquet_files:
        try:
            table = pq.read_table(str(pq_file))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to read %s: %s", pq_file, exc)
            continue

        present_cols = set(table.column_names)
        for row_idx in range(table.num_rows):
            row: Dict[str, Any] = {}
            for field in _ALL_FIELDS:
                if field in present_cols:
                    raw = table.column(field)[row_idx].as_py()
                    row[field] = raw
                else:
                    row[field] = None
            records.append(row)

    logger.info("read_trajectories: loaded %d records from %d file(s)", len(records), len(parquet_files))
    return records


# ---------------------------------------------------------------------------
# 2. build_grpo_dataset
# ---------------------------------------------------------------------------

def build_grpo_dataset(trajectories: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
    """
    Build a GRPO dataset from trajectory records.

    Groups by rollout_session_id; keeps the record with the best reward per
    session. Writes output_path/grpo_dataset.jsonl.

    Args:
        trajectories: Normalised trajectory records from read_trajectories().
        output_path: Directory to write grpo_dataset.jsonl.

    Returns:
        {"count": N, "path": str, "reward_stats": {"min": f, "max": f, "mean": f}}
    """
    out_dir = pathlib.Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Group by session: keep record with the best (highest) reward.
    best: Dict[str, Dict[str, Any]] = {}
    for record in trajectories:
        reward = _resolve_reward(record)
        if reward is None:
            continue
        session_id = record.get(_FIELD_SESSION_ID) or ""
        existing = best.get(session_id)
        if existing is None or reward > _resolve_reward(existing):  # type: ignore[operator]
            best[session_id] = {**record, "__reward": reward}

    grpo_records = []
    for session_id, record in best.items():
        reward = record["__reward"]
        grpo_records.append({
            "prompt_token_ids": record.get(_FIELD_PROMPT_TOKEN_IDS) or [],
            "completion_token_ids": record.get(_FIELD_SAMPLED_TOKEN_IDS) or [],
            "reward": reward,
            "session_id": session_id,
        })

    out_file = out_dir / "grpo_dataset.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for entry in grpo_records:
            fh.write(json.dumps(entry) + "\n")

    reward_stats = _compute_reward_stats([r["reward"] for r in grpo_records])
    result = {
        "count": len(grpo_records),
        "path": str(out_file),
        "reward_stats": reward_stats,
    }
    logger.info("build_grpo_dataset: wrote %d entries to %s", len(grpo_records), out_file)
    return result


# ---------------------------------------------------------------------------
# 3. build_sft_dataset
# ---------------------------------------------------------------------------

def build_sft_dataset(
    trajectories: List[Dict[str, Any]],
    output_path: str,
    min_reward: float = 0.0,
) -> Dict[str, Any]:
    """
    Build an SFT dataset from trajectory records with reward >= min_reward.

    Args:
        trajectories: Normalised trajectory records from read_trajectories().
        output_path: Directory to write sft_dataset.jsonl.
        min_reward: Minimum shaped reward to include (default 0.0).

    Returns:
        {"count": N, "path": str, "reward_threshold": min_reward}
    """
    out_dir = pathlib.Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    sft_records = []
    for record in trajectories:
        reward = _resolve_reward(record)
        if reward is None or reward < min_reward:
            continue
        session_id = record.get(_FIELD_SESSION_ID) or ""
        sft_records.append({
            "input_token_ids": record.get(_FIELD_PROMPT_TOKEN_IDS) or [],
            "output_token_ids": record.get(_FIELD_SAMPLED_TOKEN_IDS) or [],
            "session_id": session_id,
        })

    out_file = out_dir / "sft_dataset.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for entry in sft_records:
            fh.write(json.dumps(entry) + "\n")

    result = {
        "count": len(sft_records),
        "path": str(out_file),
        "reward_threshold": min_reward,
    }
    logger.info("build_sft_dataset: wrote %d entries to %s (min_reward=%.3f)", len(sft_records), out_file, min_reward)
    return result


# ---------------------------------------------------------------------------
# 4. build_dataset (orchestrator)
# ---------------------------------------------------------------------------

def build_dataset(store_path: str, output_path: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Orchestrate the full pipeline: read → GRPO → SFT → manifest.

    Reads all trajectories from store_path, calls both builders, and writes
    output_path/dataset_manifest.json with combined stats and provenance.

    Args:
        store_path: Parquet store directory path.
        output_path: Output directory for dataset files and manifest.
        **kwargs: Forwarded to build_sft_dataset (e.g. min_reward=0.5).

    Returns:
        {"grpo": {...}, "sft": {...}, "total_trajectories": N, "manifest_path": str}
    """
    out_dir = pathlib.Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    trajectories = read_trajectories(store_path)

    # POC-DEBT: no deduplication across files; production should deduplicate
    # by (workspace_uuid, rollout_session_id) to handle reprocessing.
    grpo_result = build_grpo_dataset(trajectories, output_path)
    sft_result = build_sft_dataset(trajectories, output_path, **kwargs)

    manifest = {
        "grpo": grpo_result,
        "sft": sft_result,
        "total_trajectories": len(trajectories),
        "provenance": {
            "store_path": str(pathlib.Path(store_path).resolve()),
            "output_path": str(out_dir.resolve()),
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        },
    }

    manifest_file = out_dir / "dataset_manifest.json"
    with manifest_file.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    manifest["manifest_path"] = str(manifest_file)
    logger.info(
        "build_dataset: %d trajectories → %d GRPO, %d SFT records; manifest at %s",
        len(trajectories),
        grpo_result["count"],
        sft_result["count"],
        manifest_file,
    )
    return manifest


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_reward_stats(rewards: List[float]) -> Dict[str, Any]:
    """Return min/max/mean stats dict for a list of rewards."""
    if not rewards:
        return {"min": None, "max": None, "mean": None}
    return {
        "min": min(rewards),
        "max": max(rewards),
        "mean": sum(rewards) / len(rewards),
    }
