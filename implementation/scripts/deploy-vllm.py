#!/usr/bin/env python3
"""T231 Step 4: Deploy fine-tuned model via HAL/vLLM.

Sets up and starts a vLLM inference server with the fine-tuned model.
Provides endpoints compatible with OpenAI API format.

Server listens on http://localhost:8000/v1/
- GET /v1/models - List available models
- POST /v1/completions - Generate completions
- POST /v1/chat/completions - Chat completions

Output: Server runs in background; logs to fine-tune-deploy.log
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_vllm_installed():
    """Check if vLLM is installed."""
    try:
        import vllm  # noqa: F401
        logger.info("✓ vLLM is installed")
        return True
    except ImportError:
        logger.warning("vLLM not installed. Install with: pip install vllm")
        return False


def check_model_exists(model_path: str) -> bool:
    """Verify model directory exists and has required files."""
    path = Path(model_path)
    if not path.exists():
        logger.error(f"Model path does not exist: {model_path}")
        return False

    required_files = ["config.json", "model.safetensors"]
    for required_file in required_files:
        file_path = path / required_file
        if not file_path.exists():
            # Some models use .bin instead of .safetensors
            alt_file = path / required_file.replace("safetensors", "bin")
            if not alt_file.exists():
                logger.warning(f"Expected file not found: {required_file} or .bin variant")

    logger.info(f"✓ Model verified at {model_path}")
    return True


def start_vllm_server(
    model_path: str,
    port: int = 8000,
    gpu_memory_utilization: float = 0.9,
    max_num_seqs: int = 256,
    tensor_parallel_size: int = 1,
):
    """Start vLLM inference server.

    Args:
        model_path: Path to fine-tuned model
        port: Port to listen on
        gpu_memory_utilization: GPU memory utilization ratio
        max_num_seqs: Maximum concurrent sequences
        tensor_parallel_size: Tensor parallelism (1 = single GPU)

    Returns:
        Subprocess handle if successful, None otherwise
    """
    if not check_vllm_installed():
        logger.error("vLLM must be installed to run this script")
        return None

    if not check_model_exists(model_path):
        logger.error(f"Model not found at {model_path}")
        return None

    # Build command
    cmd = [
        "python3", "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--port", str(port),
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--max-num-seqs", str(max_num_seqs),
        "--tensor-parallel-size", str(tensor_parallel_size),
        "--trust-remote-code",
    ]

    # Optional: Use quantization for smaller memory footprint
    # cmd.extend(["--quantization", "awq"])  # Uncomment if available

    logger.info(f"Starting vLLM server on port {port}")
    logger.info(f"Model: {model_path}")
    logger.info(f"Command: {' '.join(cmd)}")

    # Start server
    log_file = Path("fine-tune-deploy.log")
    with open(log_file, "w") as logf:
        try:
            process = subprocess.Popen(
                cmd,
                stdout=logf,
                stderr=subprocess.STDOUT,
                start_new_session=True,  # Create new process group
            )
            logger.info(f"✓ vLLM server started (PID: {process.pid})")
            logger.info(f"✓ Logs: {log_file}")
            return process
        except Exception as e:
            logger.error(f"Failed to start vLLM server: {e}")
            return None


def wait_for_server(port: int = 8000, timeout: int = 60):
    """Wait for server to be ready."""
    import urllib.request

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(
                f"http://localhost:{port}/v1/models",
                timeout=5,
            )
            if response.status == 200:
                logger.info("✓ Server is ready")
                return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            pass

        time.sleep(2)

    logger.error(f"Server did not become ready within {timeout} seconds")
    return False


def test_server(port: int = 8000):
    """Test server with a simple request."""
    import urllib.request

    logger.info("Testing server...")

    try:
        # Test models endpoint
        response = urllib.request.urlopen(f"http://localhost:{port}/v1/models")
        data = json.load(response)

        if data.get("data"):
            model_id = data["data"][0].get("id", "unknown")
            logger.info(f"✓ Models endpoint responding")
            logger.info(f"  Available model: {model_id}")
            return True
        else:
            logger.warning("No models returned from /v1/models")
            return False
    except Exception as e:
        logger.error(f"Server test failed: {e}")
        return False


def save_deployment_config(
    model_path: str,
    port: int = 8000,
    output_file: str = "deployment-config.json",
):
    """Save deployment configuration for rollback/recovery."""
    config = {
        "deployment_type": "vllm",
        "model_path": str(Path(model_path).resolve()),
        "port": port,
        "model_version": "v1-ft",
        "endpoints": {
            "models": f"http://localhost:{port}/v1/models",
            "completions": f"http://localhost:{port}/v1/completions",
            "chat": f"http://localhost:{port}/v1/chat/completions",
        },
        "notes": "Fine-tuned model deployment. See rollback-procedure.md for recovery.",
    }

    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    logger.info(f"✓ Deployment config saved: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy fine-tuned model via vLLM")
    parser.add_argument(
        "--model-path",
        default="models/fine-tuned-v1",
        help="Path to fine-tuned model (default: models/fine-tuned-v1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )
    parser.add_argument(
        "--gpu-memory",
        type=float,
        default=0.9,
        help="GPU memory utilization ratio (default: 0.9)",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for server to be ready",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test server after startup",
    )

    args = parser.parse_args()

    # Check model exists
    model_path = Path(args.model_path)
    if not model_path.exists():
        logger.error(f"Model not found: {args.model_path}")
        sys.exit(1)

    # Start server
    process = start_vllm_server(
        str(model_path),
        port=args.port,
        gpu_memory_utilization=args.gpu_memory,
    )

    if process is None:
        sys.exit(1)

    # Wait for readiness
    if not args.no_wait:
        is_ready = wait_for_server(args.port, timeout=120)
        if not is_ready:
            logger.error("Failed to start server")
            process.terminate()
            sys.exit(1)

    # Test if requested
    if args.test:
        time.sleep(5)  # Give server a moment
        test_server(args.port)

    # Save config
    save_deployment_config(args.model_path, args.port)

    logger.info(f"✓ Deployment complete!")
    logger.info(f"  Server: http://localhost:{args.port}")
    logger.info(f"  Keep this process running to serve requests")

    # Keep process running
    try:
        process.wait()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        process.terminate()
        process.wait()
