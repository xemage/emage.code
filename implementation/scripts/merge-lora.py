#!/usr/bin/env python3
"""T231 Step 3: Merge LoRA adapter into base model for deployment.

Loads base model, applies LoRA adapter, merges weights, and saves
the final merged model ready for deployment via HAL/vLLM.

Output: Merged model saved to models/fine-tuned-v1/
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_base_model_and_adapter(
    model_id: str,
    adapter_path: str,
):
    """Load base model and apply LoRA adapter."""
    logger.info(f"Loading base model: {model_id}")

    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="cpu",  # Use CPU for merging to avoid OOM
        trust_remote_code=True,
    )

    logger.info(f"Loading LoRA adapter from {adapter_path}")
    model = PeftModel.from_pretrained(base_model, adapter_path)

    logger.info("✓ Model and adapter loaded")
    return model


def merge_adapter(model):
    """Merge adapter into base model."""
    logger.info("Merging LoRA adapter into base model...")

    merged_model = model.merge_and_unload()

    logger.info("✓ Adapter merged")
    return merged_model


def save_merged_model(
    model,
    tokenizer,
    output_dir: str,
    model_version: str = "v1-ft",
):
    """Save merged model and tokenizer."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving merged model to {output_path}")

    model.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    # Save model metadata
    metadata = {
        "model_version": model_version,
        "model_type": "causal-lm",
        "fine_tuning_method": "lora",
        "merged": True,
        "ready_for_deployment": True,
    }

    metadata_file = output_path / "model-metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"✓ Merged model saved to {output_path}")
    logger.info(f"✓ Metadata saved to {metadata_file}")

    return output_path


def validate_merged_model(model_path: str):
    """Quick validation that merged model loads correctly."""
    logger.info(f"Validating merged model...")

    try:
        # Try to load the model
        AutoModelForCausalLM.from_pretrained(model_path)
        AutoTokenizer.from_pretrained(model_path)
        logger.info("✓ Model validation passed")
        return True
    except Exception as e:
        logger.error(f"✗ Model validation failed: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge LoRA adapter into base model")
    parser.add_argument(
        "--adapter-path",
        default="implementation/models/fine-tune-output/lora-adapter",
        help="Path to LoRA adapter (default: implementation/models/fine-tune-output/lora-adapter)",
    )
    parser.add_argument(
        "--model-id",
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        help="Base model ID to merge with (default: TinyLlama/TinyLlama-1.1B-Chat-v1.0)",
    )
    parser.add_argument(
        "--output-dir",
        default="models/fine-tuned-v1",
        help="Output directory for merged model (default: models/fine-tuned-v1)",
    )
    parser.add_argument(
        "--version",
        default="v1-ft",
        help="Model version tag (default: v1-ft)",
    )

    args = parser.parse_args()

    # Check adapter exists
    adapter_path = Path(args.adapter_path)
    if not adapter_path.exists():
        logger.error(f"Adapter not found: {args.adapter_path}")
        sys.exit(1)

    # Load and merge
    model = load_base_model_and_adapter(args.model_id, args.adapter_path)
    merged_model = merge_adapter(model)

    # Load tokenizer separately (needed for save)
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)

    # Save
    output_path = save_merged_model(
        merged_model,
        tokenizer,
        args.output_dir,
        model_version=args.version,
    )

    # Validate
    is_valid = validate_merged_model(str(output_path))

    result = {
        "status": "success" if is_valid else "validation_failed",
        "output_dir": str(output_path),
        "model_version": args.version,
    }

    print(json.dumps(result, indent=2))
    sys.exit(0 if is_valid else 1)
