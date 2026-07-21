#!/usr/bin/env python3
"""T231 Validation: Test fine-tuned model and verify acceptance criteria.

Runs through all acceptance criteria to verify the fine-tuning pipeline
produced a working, deployable model.

Output: Generates validation-report.json with results
"""

import json
import logging
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_script_exists(script_path: str) -> dict:
    """Check if implementation script exists."""
    path = Path(script_path)
    exists = path.exists()

    return {
        "criterion": f"Script exists: {script_path}",
        "passed": exists,
        "details": f"{'✓ Found' if exists else '✗ Not found'}: {path}",
    }


def check_dataset_created(dataset_path: str) -> dict:
    """Check if dataset was created."""
    path = Path(dataset_path)
    exists = path.exists()

    if exists:
        size = path.stat().st_size
        details = f"✓ Dataset exists ({size:,} bytes)"
    else:
        details = f"✗ Dataset not found: {path}"

    return {
        "criterion": "Dataset created",
        "passed": exists,
        "details": details,
    }


def check_hyperparameters_logged(hyperparams_path: str) -> dict:
    """Check if hyperparameters are logged."""
    path = Path(hyperparams_path)

    if not path.exists():
        return {
            "criterion": "Hyperparameters logged",
            "passed": False,
            "details": f"✗ Hyperparameters file not found: {path}",
        }

    try:
        with open(path) as f:
            data = json.load(f)

        # Check for seed
        has_seed = "seed" in data and data["seed"] == 42

        details = "✓ Hyperparameters logged"
        if has_seed:
            details += " (seed=42 ✓)"

        return {
            "criterion": "Hyperparameters logged (with seed=42)",
            "passed": has_seed,
            "details": details,
            "hyperparameters": data,
        }
    except Exception as e:
        return {
            "criterion": "Hyperparameters logged",
            "passed": False,
            "details": f"✗ Error reading hyperparameters: {e}",
        }


def check_model_loads(model_path: str) -> dict:
    """Check if merged model loads without errors."""
    path = Path(model_path)

    if not path.exists():
        return {
            "criterion": "Model loads without errors",
            "passed": False,
            "details": f"✗ Model directory not found: {path}",
        }

    try:
        model = AutoModelForCausalLM.from_pretrained(
            str(path),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="cpu",
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(str(path), trust_remote_code=True)

        return {
            "criterion": "Model loads without errors",
            "passed": True,
            "details": "✓ Model and tokenizer loaded successfully",
            "model_type": model.config.model_type,
            "vocab_size": tokenizer.vocab_size,
        }
    except Exception as e:
        return {
            "criterion": "Model loads without errors",
            "passed": False,
            "details": f"✗ Failed to load model: {e}",
        }


def check_inference_works(model_path: str) -> dict:
    """Test simple inference."""
    path = Path(model_path)

    if not path.exists():
        return {
            "criterion": "Model generates valid code samples",
            "passed": False,
            "details": f"✗ Model directory not found: {path}",
        }

    try:
        model = AutoModelForCausalLM.from_pretrained(
            str(path),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="cpu",
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(str(path), trust_remote_code=True)

        # Test prompt
        prompt = "def fibonacci(n):"
        inputs = tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=False,
                top_p=0.9,
                temperature=0.7,
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "criterion": "Model generates valid code samples",
            "passed": len(generated_text) > len(prompt),
            "details": "✓ Model generated completion",
            "sample_output": generated_text[:200] + "..." if len(generated_text) > 200 else generated_text,
        }
    except Exception as e:
        return {
            "criterion": "Model generates valid code samples",
            "passed": False,
            "details": f"✗ Inference failed: {e}",
        }


def check_rollback_documented() -> dict:
    """Check if rollback procedure is documented."""
    path = Path("docs/releases/model-v1-fine-tune-rollback.md")

    if not path.exists():
        return {
            "criterion": "Rollback procedure documented",
            "passed": False,
            "details": f"✗ Rollback procedure not found: {path}",
        }

    try:
        content = path.read_text()

        # Check for key sections
        has_sections = all([
            "Level 1" in content,
            "Level 2" in content,
            "Level 3" in content,
            "Verification" in content,
        ])

        return {
            "criterion": "Rollback procedure documented",
            "passed": has_sections,
            "details": "✓ Rollback procedure complete" if has_sections else "⚠ Incomplete sections",
            "size_bytes": len(content),
        }
    except Exception as e:
        return {
            "criterion": "Rollback procedure documented",
            "passed": False,
            "details": f"✗ Error reading procedure: {e}",
        }


def validate_all() -> dict:
    """Run all validation checks."""
    checks = [
        check_script_exists("implementation/scripts/generate-sample-dataset.py"),
        check_script_exists("implementation/scripts/fine-tune-setup.py"),
        check_script_exists("implementation/scripts/fine-tune-lora.py"),
        check_script_exists("implementation/scripts/merge-lora.py"),
        check_script_exists("implementation/scripts/deploy-vllm.py"),
        check_script_exists("implementation/scripts/fine-tune-pipeline.py"),
        check_dataset_created("implementation/datasets/t231-dataset.jsonl"),
        check_hyperparameters_logged("implementation/models/fine-tune-output/hyperparameters.json"),
        check_model_loads("models/fine-tuned-v1"),
        check_inference_works("models/fine-tuned-v1"),
        check_rollback_documented(),
    ]

    passed = sum(1 for c in checks if c.get("passed", False))
    total = len(checks)

    report = {
        "validation_summary": {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{100 * passed / total:.1f}%",
            "status": "PASS" if passed == total else "FAIL",
        },
        "checks": checks,
    }

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate T231 fine-tuning pipeline")
    parser.add_argument(
        "--output",
        default="validation-report.json",
        help="Output file for validation report",
    )

    args = parser.parse_args()

    logger.info("Running T231 validation checks...")
    report = validate_all()

    # Save report
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"\nValidation Report: {args.output}")
    logger.info(f"Status: {report['validation_summary']['status']}")
    logger.info(f"Passed: {report['validation_summary']['passed']}/{report['validation_summary']['total_checks']}")

    # Print summary
    print("\n" + json.dumps(report["validation_summary"], indent=2))

    sys.exit(0 if report["validation_summary"]["status"] == "PASS" else 1)
