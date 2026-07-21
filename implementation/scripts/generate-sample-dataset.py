#!/usr/bin/env python3
"""Generate sample Parquet dataset mimicking T230 trainer-bridge output.

This script creates sample trajectory data for PoC fine-tuning.
In production, this would come from actual rollout trajectories via T230.

POC-DEBT: This is a synthetic dataset for testing. Production will use
actual trajectory data from the rollout capture pipeline (T226).
"""

import json
import logging
import pathlib
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Sample code generation prompts and completions (realistic examples)
SAMPLE_PROMPTS = [
    "def fibonacci(n):\n    # Generate",
    "def sort_array(arr):\n    # Sort",
    "def is_prime(n):\n    # Check if",
    "def reverse_string(s):\n    # Reverse",
    "def binary_search(arr, target):\n    # Find",
]

SAMPLE_COMPLETIONS = [
    "fibonacci numbers up to n\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    result = [0, 1]\n    for i in range(2, n):\n        result.append(result[-1] + result[-2])\n    return result",
    "using quicksort algorithm\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[0]\n    left = [x for x in arr[1:] if x < pivot]\n    right = [x for x in arr[1:] if x >= pivot]\n    return sort_array(left) + [pivot] + sort_array(right)",
    "a number is prime\n    if n < 2:\n        return False\n    for i in range(2, int(n ** 0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
    "a string by reversing characters\n    return s[::-1]",
    "an element in a sorted array\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
]

SAMPLE_REWARDS = [0.8, 0.9, 0.7, 0.85, 0.75, 0.6, -0.1, 0.5, 0.95, 0.4]


def create_token_ids(text: str, max_tokens: int = 50) -> list[int]:
    """Create synthetic token IDs from text (using hash-based approach for PoC)."""
    # POC-DEBT: In production, use actual tokenizer. This is synthetic for testing.
    tokens = []
    for i, char in enumerate(text[:max_tokens]):
        # Simple hash to get "token ID" (100-200 range)
        token_id = 100 + (ord(char) + i) % 100
        tokens.append(token_id)
    return tokens


def generate_sample_trajectories(
    output_path: str,
    num_records: int = 50,
    num_files: int = 3,
) -> dict[str, Any]:
    """Generate sample trajectory data in Parquet format.

    Args:
        output_path: Directory to write Parquet files
        num_records: Total number of trajectory records
        num_files: Number of Parquet shards to create

    Returns:
        Dictionary with generation stats
    """
    out_dir = pathlib.Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    records_per_file = max(1, num_records // num_files)
    total_written = 0

    for file_idx in range(num_files):
        rows = []
        start_idx = file_idx * records_per_file
        end_idx = start_idx + records_per_file
        if file_idx == num_files - 1:
            # Last file gets any remainder
            end_idx = num_records

        for record_idx in range(start_idx, end_idx):
            prompt_idx = record_idx % len(SAMPLE_PROMPTS)
            completion_idx = record_idx % len(SAMPLE_COMPLETIONS)
            reward_idx = record_idx % len(SAMPLE_REWARDS)

            prompt_text = SAMPLE_PROMPTS[prompt_idx]
            completion_text = SAMPLE_COMPLETIONS[completion_idx]
            reward = SAMPLE_REWARDS[reward_idx]

            row = {
                "workspace_uuid": f"ws-{file_idx:03d}",
                "rollout_session_id": f"sess-{record_idx:06d}",
                "prompt_token_ids": create_token_ids(prompt_text, 20),
                "sampled_token_ids": create_token_ids(completion_text, 40),
                "logprobs": [-0.1 - (i * 0.05) for i in range(5)],
                "finish_reason": "stop" if reward > 0.5 else "length",
                "timestamp_ns": 1_000_000_000 + record_idx * 100_000_000,
                "shaped_reward": reward,
                "evaluation_reward": reward + 0.05,  # Slightly higher
            }
            rows.append(row)

        # Write to Parquet
        if rows:
            table = pa.table({
                k: pa.array([row[k] for row in rows])
                for k in rows[0].keys()
            })
            pq_path = out_dir / f"trajectories-shard-{file_idx:02d}.parquet"
            pq.write_table(table, str(pq_path))
            logger.info(f"Wrote {len(rows)} records to {pq_path.name}")
            total_written += len(rows)

    logger.info(f"✓ Generated {total_written} trajectories across {num_files} files")
    return {
        "total_records": total_written,
        "num_files": num_files,
        "output_path": str(out_dir),
    }


if __name__ == "__main__":
    import sys

    output_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t226-parquet-store"
    num_records = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    result = generate_sample_trajectories(output_path, num_records=num_records)
    print(json.dumps(result, indent=2))
