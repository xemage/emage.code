"""SIA runtime utilities for real LLM-backed harness execution."""

import asyncio
import json
import logging
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

DEFAULT_ANTHROPIC_MODEL = "claude-3-haiku-20240307"
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_MAX_OUTPUT_TOKENS = 900


def _resolve_runtime_model(requested_model: str) -> str:
    """Map rollout labels to concrete runtime model identifiers."""
    model = (requested_model or "").strip()
    normalized = model.lower()
    if normalized in {"baseline", "haiku", "claude-haiku"}:
        return os.getenv("SIA_BASELINE_MODEL", DEFAULT_ANTHROPIC_MODEL).strip()
    if normalized in {"v1-ft", "v1_ft", "fine-tuned", "finetuned"}:
        return os.getenv(
            "SIA_FINE_TUNED_MODEL",
            os.getenv("SIA_BASELINE_MODEL", DEFAULT_ANTHROPIC_MODEL),
        ).strip()
    return model or os.getenv("SIA_BASELINE_MODEL", DEFAULT_ANTHROPIC_MODEL).strip()


def _build_messages_url(base_url: str) -> str:
    """Construct Anthropic messages endpoint URL from a base URL."""
    root = (base_url or "https://api.anthropic.com").strip().rstrip("/")
    if root.endswith("/v1"):
        return f"{root}/messages"
    return f"{root}/v1/messages"


def _extract_text_blocks(payload: Dict[str, Any]) -> str:
    """Extract assistant text from Anthropic response payload."""
    blocks = payload.get("content")
    if not isinstance(blocks, list):
        return ""
    text_parts: List[str] = []
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                text_parts.append(text)
    return "\n".join(text_parts).strip()


def _extract_code_block(text: str) -> str:
    """Prefer fenced python code blocks; fall back to full assistant text."""
    if not text:
        return ""
    match = re.search(r"```python\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        match = re.search(r"```\s*(.*?)```", text, flags=re.DOTALL)
    if match:
        code = match.group(1).strip()
        if code:
            return code
    return text.strip()


def _call_anthropic_messages(
    *,
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    timeout_seconds: int,
    max_output_tokens: int,
) -> Dict[str, Any]:
    """Perform a single Anthropic messages call via HTTPS endpoint."""
    url = _build_messages_url(base_url)
    body = {
        "model": model,
        "max_tokens": max_output_tokens,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Solve the task and return executable Python code in a fenced code block.\n\n"
                    f"Task:\n{prompt}"
                ),
            }
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
        raise RuntimeError(f"Anthropic request failed ({exc.code}): {details[:400]}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Anthropic response was not valid JSON") from exc


def _write_generated_code(workspace: str, generated_code: str) -> str:
    """Persist generated code artifact for downstream evaluator ingestion."""
    solution_path = Path(workspace) / "solution.py"
    solution_path.write_text(generated_code, encoding="utf-8")
    return str(solution_path)


async def run_agent(
    model_name: str,
    max_turns: int,
    prompt: str,
    agent_working_directory: str,
    backend: str,
) -> Dict[str, Any]:
    """Execute one real LLM-backed generation and emit trajectory metadata."""
    runtime_model = _resolve_runtime_model(model_name)
    timeout_seconds = int(os.getenv("SIA_LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    max_output_tokens = int(os.getenv("SIA_LLM_MAX_OUTPUT_TOKENS", str(DEFAULT_MAX_OUTPUT_TOKENS)))
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    if backend != "claude":
        raise ValueError(f"Unsupported backend for Option A runtime: {backend}")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required for real LLM execution")

    logger.info(
        "run_agent real call: backend=%s requested_model=%s runtime_model=%s max_turns=%s",
        backend,
        model_name,
        runtime_model,
        max_turns,
    )

    response_payload = await asyncio.to_thread(
        _call_anthropic_messages,
        api_key=api_key,
        base_url=base_url,
        model=runtime_model,
        prompt=prompt,
        timeout_seconds=timeout_seconds,
        max_output_tokens=max_output_tokens,
    )
    assistant_text = _extract_text_blocks(response_payload)
    if not assistant_text:
        raise RuntimeError("Anthropic response did not include text content")

    generated_code = _extract_code_block(assistant_text)
    artifact_path = _write_generated_code(agent_working_directory, generated_code)
    usage = response_payload.get("usage") if isinstance(response_payload.get("usage"), dict) else {}

    trajectory = [
        {"turn": 1, "action": "prompt", "content": prompt[:2000]},
        {
            "turn": 2,
            "action": "llm_response",
            "model": runtime_model,
            "content": assistant_text[:6000],
            "artifact": artifact_path,
            "usage": usage,
        },
    ]

    return {
        "trajectory": trajectory,
        "status": "success",
        "backend": backend,
        "model": runtime_model,
        "turns": 1,
        "generated_code": generated_code,
        "artifact_path": artifact_path,
        "usage": usage,
    }

