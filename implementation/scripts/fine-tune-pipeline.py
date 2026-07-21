#!/usr/bin/env python3
"""T231 Orchestration: Full pipeline execution.

Runs all 5 steps of the fine-tuning pipeline end-to-end:
  1. Generate/Load T230 dataset
  2. Validate and prepare dataset (fine-tune-setup.py)
  3. Run LoRA fine-tuning (fine-tune-lora.py)
  4. Merge adapter (merge-lora.py)
  5. Deploy via vLLM (deploy-vllm.py)

Tracks progress and hyperparameters for reproducibility.

Output: Logs to fine-tune-pipeline.log
  Artifacts: implementation/datasets/, implementation/models/, models/fine-tuned-v1/
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_step(
    step_num: int,
    step_name: str,
    command: list[str],
    check: bool = True,
):
    """Execute a pipeline step."""
    logger.info(f"\n{'=' * 70}")
    logger.info(f"STEP {step_num}: {step_name}")
    logger.info(f"{'=' * 70}")
    logger.info(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=False,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"✗ Step {step_num} failed with code {result.returncode}")
            return False

        logger.info(f"✓ Step {step_num} complete")
        return True
    except Exception as e:
        logger.error(f"✗ Step {step_num} failed: {e}")
        return False


def run_pipeline(
    dataset_path: str = "/tmp/t226-parquet-store",
    output_dir: str = "implementation/datasets",
    model_id: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    skip_deploy: bool = False,
    generate_sample_data: bool = False,
):
    """Execute full fine-tuning pipeline."""

    # Record start time
    start_time = datetime.utcnow()

    logger.info("T231 FINE-TUNING PIPELINE")
    logger.info(f"Started: {start_time.isoformat()}")
    logger.info(f"Dataset path: {dataset_path}")
    logger.info(f"Model ID: {model_id}")

    steps_completed = []

    # Step 0: Generate sample data if requested
    if generate_sample_data:
        logger.info("\nGenerating sample dataset...")
        cmd = [
            "python3",
            "implementation/scripts/generate-sample-dataset.py",
            dataset_path,
            "50",
        ]
        if not run_step(0, "Generate Sample Data", cmd):
            return {"status": "failed", "step": 0}
        steps_completed.append("generate-sample-data")

    # Step 1: Load and validate dataset
    cmd = [
        "python3",
        "implementation/scripts/fine-tune-setup.py",
        "--store-path", dataset_path,
        "--output-path", output_dir,
        "--dataset-type", "grpo",
    ]
    if not run_step(1, "Load & Validate Dataset", cmd):
        return {"status": "failed", "step": 1}
    steps_completed.append("fine-tune-setup")

    # Step 2: Run LoRA fine-tuning
    dataset_file = Path(output_dir) / "t231-dataset.jsonl"
    cmd = [
        "python3",
        "implementation/scripts/fine-tune-lora.py",
        "--dataset-path", str(dataset_file),
        "--model-id", model_id,
        "--epochs", "2",  # Reduced for PoC
        "--batch-size", "4",
    ]
    if not run_step(2, "Fine-tune with LoRA", cmd):
        return {"status": "failed", "step": 2}
    steps_completed.append("fine-tune-lora")

    # Step 3: Merge adapter
    cmd = [
        "python3",
        "implementation/scripts/merge-lora.py",
        "--model-id", model_id,
        "--adapter-path", "implementation/models/fine-tune-output/lora-adapter",
        "--output-dir", "models/fine-tuned-v1",
    ]
    if not run_step(3, "Merge LoRA Adapter", cmd):
        return {"status": "failed", "step": 3}
    steps_completed.append("merge-lora")

    # Step 4: Deploy via vLLM (optional)
    if not skip_deploy:
        cmd = [
            "python3",
            "implementation/scripts/deploy-vllm.py",
            "--model-path", "models/fine-tuned-v1",
            "--port", "8000",
            "--no-wait",  # Don't wait for startup in pipeline
        ]
        if not run_step(4, "Deploy via vLLM", cmd, check=False):
            logger.warning("⚠ Deployment step failed or not available (vLLM may not be installed)")
        steps_completed.append("deploy-vllm")

    # Record completion time
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()

    result = {
        "status": "success",
        "started": start_time.isoformat(),
        "completed": end_time.isoformat(),
        "duration_seconds": duration,
        "steps_completed": steps_completed,
        "output_directory": output_dir,
        "model_directory": "models/fine-tuned-v1",
    }

    logger.info(f"\n{'=' * 70}")
    logger.info("PIPELINE COMPLETE")
    logger.info(f"{'=' * 70}")
    logger.info(f"Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")
    logger.info(f"Steps completed: {len(steps_completed)}")
    logger.info(f"Output: models/fine-tuned-v1/")
    logger.info(f"Next: Deploy model or run E2E tests")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T231: Full fine-tuning pipeline")
    parser.add_argument(
        "--dataset-path",
        default="/tmp/t226-parquet-store",
        help="Path to T230 dataset store",
    )
    parser.add_argument(
        "--output-dir",
        default="implementation/datasets",
        help="Output directory for prepared datasets",
    )
    parser.add_argument(
        "--model-id",
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        help="Base model ID",
    )
    parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="Skip deployment step",
    )
    parser.add_argument(
        "--generate-sample-data",
        action="store_true",
        help="Generate synthetic sample data (for PoC)",
    )

    args = parser.parse_args()

    result = run_pipeline(
        dataset_path=args.dataset_path,
        output_dir=args.output_dir,
        model_id=args.model_id,
        skip_deploy=args.skip_deploy,
        generate_sample_data=args.generate_sample_data,
    )

    print("\n" + json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "success" else 1)
