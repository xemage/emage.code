#!/usr/bin/env python3
"""T231 Step 1: Load T230 dataset and validate format.

Loads trajectories from /tmp/t226-parquet-store, builds GRPO or SFT datasets,
and validates the format is ready for fine-tuning.

Output: Saves dataset to implementation/datasets/t231-dataset.jsonl
"""

import json
import logging
import sys
from pathlib import Path

# Add trainer_bridge to path
sys.path.insert(0, str(Path(__file__).parent.parent / "adapters" / "sia-target"))

from trainer_bridge import read_trajectories, build_grpo_dataset, build_sft_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def validate_dataset(dataset: list[dict], dataset_type: str = "grpo") -> bool:
    """Validate dataset format before fine-tuning.

    Args:
        dataset: List of dataset examples
        dataset_type: 'grpo' or 'sft'

    Returns:
        True if valid, False otherwise
    """
    if not dataset:
        logger.error("Dataset is empty!")
        return False

    if dataset_type == "grpo":
        required_keys = {"prompt_token_ids", "completion_token_ids", "reward", "session_id"}
    elif dataset_type == "sft":
        required_keys = {"input_token_ids", "output_token_ids", "session_id"}
    else:
        logger.error(f"Unknown dataset type: {dataset_type}")
        return False

    # Validate first 5 examples
    for i, example in enumerate(dataset[:5]):
        missing = required_keys - set(example.keys())
        if missing:
            logger.error(f"Example {i} missing keys: {missing}")
            logger.error(f"Got: {example.keys()}")
            return False

        # Validate types
        if dataset_type == "grpo":
            if not isinstance(example["prompt_token_ids"], list):
                logger.error(f"Example {i}: prompt_token_ids is not a list")
                return False
            if not isinstance(example["completion_token_ids"], list):
                logger.error(f"Example {i}: completion_token_ids is not a list")
                return False
            if not isinstance(example["reward"], (int, float)):
                logger.error(f"Example {i}: reward is not numeric")
                return False

    logger.info(f"✓ Dataset validation passed ({len(dataset)} examples)")
    return True


def load_dataset(
    store_path: str = "/tmp/t226-parquet-store",
    output_path: str = "implementation/datasets",
    dataset_type: str = "grpo",
) -> dict:
    """Load and prepare dataset.

    Args:
        store_path: Path to T230 parquet store
        output_path: Where to save dataset files
        dataset_type: 'grpo' or 'sft'

    Returns:
        Dictionary with dataset stats and paths
    """
    logger.info(f"Loading trajectories from {store_path}...")
    trajectories = read_trajectories(store_path)

    if not trajectories:
        logger.error("No trajectories found in parquet store!")
        logger.error(f"Checked: {store_path}")
        return {"error": "No trajectories found", "store_path": store_path}

    logger.info(f"Loaded {len(trajectories)} trajectories")

    # Create output directory
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build dataset
    if dataset_type == "grpo":
        result = build_grpo_dataset(trajectories, str(out_dir))
        dataset_file = Path(result["path"])  # Already absolute path from trainer_bridge
    elif dataset_type == "sft":
        result = build_sft_dataset(trajectories, str(out_dir))
        dataset_file = Path(result["path"])  # Already absolute path from trainer_bridge
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    # Load the created dataset
    dataset = []
    with open(dataset_file) as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))

    # Validate
    is_valid = validate_dataset(dataset, dataset_type)
    if not is_valid:
        return {"error": "Dataset validation failed"}

    # Save merged dataset
    merged_path = out_dir / "t231-dataset.jsonl"
    with open(merged_path, "w") as f:
        for example in dataset:
            f.write(json.dumps(example) + "\n")

    return {
        "status": "success",
        "dataset_type": dataset_type,
        "num_examples": len(dataset),
        "dataset_file": str(merged_path),
        "stats": result,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load and validate T230 dataset")
    parser.add_argument(
        "--store-path",
        default="/tmp/t226-parquet-store",
        help="Path to T230 parquet store (default: /tmp/t226-parquet-store)",
    )
    parser.add_argument(
        "--output-path",
        default="implementation/datasets",
        help="Output directory for dataset (default: implementation/datasets)",
    )
    parser.add_argument(
        "--dataset-type",
        choices=["grpo", "sft"],
        default="grpo",
        help="Dataset type to build (default: grpo)",
    )

    args = parser.parse_args()

    result = load_dataset(
        store_path=args.store_path,
        output_path=args.output_path,
        dataset_type=args.dataset_type,
    )

    print(json.dumps(result, indent=2))

    # Exit with error if validation failed
    if "error" in result:
        sys.exit(1)
