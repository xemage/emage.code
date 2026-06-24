#!/usr/bin/env python3
"""
SIA executor service — Phase 3.2: Executor Delivery with heartbeat and retry.

This service:
1. Connects to CWSO orchestrator gateway
2. Registers as an executor node
3. Polls /nodes/{node_id}/tasks for assigned work (with retry/backoff)
4. Sends heartbeat to /nodes/{node_id}/heartbeat every ~30s (daemon thread)
5. Simulates SIA execution (mock LLM call — Phase 3.3 wires real harness)
6. Reports results via /callbacks/session_result

Phase 3.2 additions over Phase 3.1:
- Exponential backoff with jitter on transient HTTP errors
- Background heartbeat loop keeps node liveness signal alive
- Graceful shutdown stops heartbeat thread and waits for in-flight sessions
"""

import json
import logging
import math
import os
import random
import subprocess
import threading
import time
import argparse
import signal
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)


_RETRY_BASE_DELAY = 0.5   # seconds — first backoff interval
_RETRY_MAX_DELAY  = 30.0  # seconds — cap on backoff
_RETRY_MAX_TRIES  = 4     # attempts before giving up
HEARTBEAT_INTERVAL = 30.0 # seconds between heartbeats (Phase 3.2)
STALE_NODE_TIMEOUT = 90.0 # seconds — orchestrator reaps nodes silent longer than this
DEFAULT_EXECUTION_TIMEOUT = 120.0
MAX_TEXT_PREVIEW_CHARS = 4000
MAX_STEP_TOKENS = 512


def _truncate_text(value: Optional[str], limit: int = MAX_TEXT_PREVIEW_CHARS) -> str:
    """Return a bounded preview safe for logs and rollout metadata."""
    if not value:
        return ""
    if len(value) <= limit:
        return value
    return f"{value[:limit]}...<truncated {len(value) - limit} chars>"


def _stringify_metadata(value: Any) -> str:
    """Serialize rollout metadata values to strings for CWSO callbacks."""
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, str):
        return _truncate_text(value)
    return _truncate_text(json.dumps(value, ensure_ascii=True, sort_keys=True))


def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    """Read a JSON file if present and decodable."""
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _coerce_positive_int(value: Any, default: int) -> int:
    """Convert optional numeric input into a positive integer fallback."""
    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return default
    return candidate if candidate > 0 else default


def _text_to_token_ids(value: str, limit: int = MAX_STEP_TOKENS) -> List[int]:
    """Create a compact token-like representation for rollout steps."""
    raw = value.encode("utf-8", errors="ignore")[:limit]
    return [int(byte) for byte in raw]


def _infer_model_label_from_workspace(workspace_id: str) -> str:
    """Infer rollout model label from workspace naming when model is omitted."""
    normalized = (workspace_id or "").strip().lower()
    if not normalized:
        return ""
    if any(token in normalized for token in ("finetuned", "fine-tuned", "v1-ft", "v1_ft", "candidate")):
        return "v1-ft"
    if "baseline" in normalized:
        return "baseline"
    return ""


def _preview_workspace_file(path: Path) -> Optional[str]:
    """Return a small preview for likely text artifacts."""
    if path.suffix.lower() not in {".py", ".js", ".ts", ".json", ".md", ".txt", ".yaml", ".yml"}:
        return None
    try:
        return _truncate_text(path.read_text(encoding="utf-8", errors="ignore"), 1200)
    except OSError:
        return None


class SIAExecutor:
    """SIA executor — Phase 3.2: real task polling, heartbeat, retry/backoff."""

    def __init__(
        self,
        cwso_url: str,
        node_id: str,
        jwt_secret: str,
        mock_delay: float = 2.0,
        heartbeat_interval: float = HEARTBEAT_INTERVAL,
        execution_timeout: float = DEFAULT_EXECUTION_TIMEOUT,
        harness_entrypoint: Optional[str] = None,
    ):
        self.cwso_url = cwso_url.rstrip("/")
        self.node_id = node_id
        self.jwt_secret = jwt_secret
        self.mock_delay = mock_delay
        self.heartbeat_interval = heartbeat_interval
        self.execution_timeout = execution_timeout
        self.harness_entrypoint = Path(harness_entrypoint) if harness_entrypoint else (
            Path(__file__).resolve().parent.parent
            / "adapters"
            / "sia-target"
            / "harness-entrypoint.py"
        )
        self.running = True
        self.session_count = 0
        self._heartbeat_thread: Optional[threading.Thread] = None

    def _snapshot_workspace(self, workspace_path: Path) -> Dict[str, int]:
        """Capture file mtimes before harness execution for artifact diffing."""
        snapshot: Dict[str, int] = {}
        if not workspace_path.exists():
            return snapshot
        for path in workspace_path.rglob("*"):
            if not path.is_file():
                continue
            try:
                snapshot[str(path.relative_to(workspace_path))] = path.stat().st_mtime_ns
            except OSError:
                continue
        return snapshot

    def _collect_workspace_artifacts(
        self,
        workspace_path: Path,
        before_snapshot: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """Return files created or modified by the harness run."""
        artifacts: List[Dict[str, Any]] = []
        if not workspace_path.exists():
            return artifacts
        for path in sorted(workspace_path.rglob("*")):
            if not path.is_file():
                continue
            try:
                relative = str(path.relative_to(workspace_path))
                stat = path.stat()
            except OSError:
                continue
            previous_mtime = before_snapshot.get(relative)
            if previous_mtime is not None and stat.st_mtime_ns <= previous_mtime:
                continue
            artifact: Dict[str, Any] = {
                "path": str(path),
                "relative_path": relative,
                "size_bytes": stat.st_size,
            }
            preview = _preview_workspace_file(path)
            if preview:
                artifact["preview"] = preview
            artifacts.append(artifact)
        return artifacts

    def _extract_generated_code(
        self,
        output_payload: Optional[Dict[str, Any]],
        artifacts: List[Dict[str, Any]],
    ) -> str:
        """Best-effort extraction of generated code or artifact preview."""
        if isinstance(output_payload, dict):
            for key in ("generated_code", "code", "output", "result"):
                value = output_payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        for artifact in artifacts:
            relative_path = str(artifact.get("relative_path", ""))
            if relative_path.endswith((".py", ".js", ".ts", ".go", ".java", ".rb", ".php", ".rs")):
                preview = artifact.get("preview")
                if isinstance(preview, str) and preview.strip():
                    return preview
        return ""

    def _build_partial_result_summary(
        self,
        execution_status: str,
        evaluation_payload: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a compact partial-result summary for rollout task status."""
        reward = 0.0
        if isinstance(evaluation_payload, dict) and "overall_score" in evaluation_payload:
            try:
                reward = float(evaluation_payload["overall_score"])
            except (TypeError, ValueError):
                reward = 0.0
        return {
            "step": 0,
            "reward": reward,
            "merge_outcome": execution_status,
        }

    def _build_trajectory_group(
        self,
        session_id: str,
        task_spec: Dict[str, Any],
        generated_code: str,
        harness_output: Optional[Dict[str, Any]],
        evaluation_output: Optional[Dict[str, Any]],
        artifacts: List[Dict[str, Any]],
        partial_result: Dict[str, Any],
        execution_status: str,
        error_payload: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Convert harness output into the CWSO trajectory callback shape."""
        prompt = str(task_spec.get("description") or task_spec.get("prompt") or "")
        step_text = generated_code or _stringify_metadata(harness_output) or _stringify_metadata(error_payload)
        step_tokens = _text_to_token_ids(step_text or execution_status)
        reward_value = partial_result.get("reward")
        rewards = []
        if isinstance(reward_value, (int, float)):
            rewards = [float(reward_value)]
        chain_metadata = {
            "execution_status": execution_status,
            "workspace_id": str(task_spec.get("workspace_id", "")),
            "harness_output": _stringify_metadata(harness_output),
            "evaluation_output": _stringify_metadata(evaluation_output),
        }
        group_metadata = {
            "execution_status": execution_status,
            "description": prompt,
            "partial_result": _stringify_metadata(partial_result),
            "generated_artifacts": _stringify_metadata(artifacts),
            "error": _stringify_metadata(error_payload),
        }
        return {
            "session_id": session_id,
            "chains": [
                {
                    "chain_id": f"{session_id}-harness",
                    "prefix_token_ids": _text_to_token_ids(prompt),
                    "steps": [
                        {
                            "token_ids": step_tokens,
                            "loss_mask": [1] * len(step_tokens),
                            "logprobs": [0.0] * len(step_tokens),
                        }
                    ],
                    "metadata": {key: value for key, value in chain_metadata.items() if value},
                }
            ],
            "rewards": rewards,
            "metadata": {key: value for key, value in group_metadata.items() if value},
        }

    def _build_harness_environment(
        self,
        task_spec: Dict[str, Any],
        workspace_path: Path,
        session_id: str,
    ) -> Dict[str, str]:
        """Prepare environment variables expected by the SIA harness entrypoint."""
        prompt = str(task_spec.get("description") or task_spec.get("prompt") or "").strip()
        max_turns = str(_coerce_positive_int(task_spec.get("max_steps"), 10))
        dispatch_result = {
            "workspace_uuid": str(workspace_path),
            "rollout_session_id": session_id,
        }
        env = os.environ.copy()
        env.update(
            {
                "CWSO_HARNESS_PROMPT": prompt,
                "CWSO_HARNESS_WORKSPACE": str(workspace_path),
                "CWSO_DISPATCH_RESULT": json.dumps(dispatch_result),
                "SIA_MAX_TURNS": max_turns,
            }
        )
        backend = str(task_spec.get("backend") or "").strip()
        model = str(task_spec.get("model") or "").strip()
        if not model:
            model = _infer_model_label_from_workspace(str(task_spec.get("workspace_id") or workspace_path))
        if backend:
            env["SIA_BACKEND"] = backend
        if model:
            env["SIA_MODEL"] = model
        return env

    def _write_stream_artifact(self, path: Path, value: Optional[str]) -> None:
        """Persist subprocess stdout/stderr artifacts for later inspection."""
        try:
            path.write_text(value or "", encoding="utf-8")
        except OSError as exc:
            log.warning(f"Could not write stream artifact {path}: {exc}")

    def generate_jwt_token(self, role: str = "worker") -> str:
        """Generate HS256 JWT token for CWSO authentication."""
        import base64
        import hashlib
        import hmac
        import json as json_lib
        from datetime import datetime, timedelta

        now = int(datetime.now(timezone.utc).timestamp())
        exp = now + 3600  # 1 hour expiration

        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": "cwso",
            "aud": ["cwso-mcp"],
            "role": role,
            "exp": exp,
            "nbf": now,
            "iat": now,
            "sub": self.node_id,
        }

        header_b64 = base64.urlsafe_b64encode(
            json_lib.dumps(header, separators=(",", ":")).encode()
        ).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(
            json_lib.dumps(payload, separators=(",", ":")).encode()
        ).decode().rstrip("=")

        message = f"{header_b64}.{payload_b64}".encode()
        signature = base64.urlsafe_b64encode(
            hmac.new(
                self.jwt_secret.encode() if isinstance(self.jwt_secret, str) else self.jwt_secret,
                message,
                hashlib.sha256,
            ).digest()
        ).decode().rstrip("=")

        return f"{header_b64}.{payload_b64}.{signature}"

    # ------------------------------------------------------------------ #
    # Internal HTTP helper with exponential backoff + jitter (Phase 3.2)  #
    # ------------------------------------------------------------------ #

    def _http_request_with_retry(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        timeout: float = 5.0,
        max_tries: int = _RETRY_MAX_TRIES,
    ) -> Optional[bytes]:
        """
        Execute an HTTP request with exponential backoff for transient failures.

        Returns response bytes on success, None after max_tries failures.
        Non-retryable errors (4xx) are raised immediately.
        """
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt < max_tries:
            try:
                req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read()
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    # Client errors are not transient — propagate immediately
                    raise
                last_exc = e
            except (urllib.error.URLError, OSError) as e:
                last_exc = e

            delay = min(_RETRY_MAX_DELAY, _RETRY_BASE_DELAY * (2 ** attempt))
            # Add ±20 % jitter to avoid thundering-herd on reconnect
            delay *= 1 + random.uniform(-0.2, 0.2)
            attempt += 1
            if attempt < max_tries:
                log.debug(
                    f"HTTP {method} {url} failed (attempt {attempt}/{max_tries}): "
                    f"{last_exc} — retrying in {delay:.1f}s"
                )
                time.sleep(delay)

        log.warning(
            f"HTTP {method} {url} gave up after {max_tries} attempts: {last_exc}"
        )
        return None

    # ------------------------------------------------------------------ #
    # Heartbeat (Phase 3.2)                                               #
    # ------------------------------------------------------------------ #

    def send_heartbeat(self) -> bool:
        """POST /nodes/{node_id}/heartbeat to signal liveness."""
        url = f"{self.cwso_url}/nodes/{self.node_id}/heartbeat"
        token = self.generate_jwt_token("worker")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            resp = self._http_request_with_retry(
                url, method="POST", headers=headers, body=b"{}", timeout=5.0, max_tries=2
            )
            if resp is not None:
                log.debug(f"Heartbeat OK (node={self.node_id})")
                return True
        except Exception as e:
            log.warning(f"Heartbeat failed: {e}")
        return False

    def _heartbeat_loop(self) -> None:
        """Daemon thread: sends heartbeat every heartbeat_interval seconds."""
        log.info(
            f"Heartbeat loop started (interval={self.heartbeat_interval:.0f}s, "
            f"stale_timeout={STALE_NODE_TIMEOUT:.0f}s)"
        )
        # Use a sleep chunk that is fine enough to react quickly to running=False
        # while still avoiding busy-spin for long intervals.
        sleep_chunk = min(1.0, self.heartbeat_interval / 4)
        while self.running:
            self.send_heartbeat()
            elapsed = 0.0
            while elapsed < self.heartbeat_interval and self.running:
                time.sleep(sleep_chunk)
                elapsed += sleep_chunk
        log.info("Heartbeat loop stopped")


    def register_node(self) -> bool:
        """Register this executor as a node with the gateway."""
        url = f"{self.cwso_url}/nodes/register"
        token = self.generate_jwt_token("worker")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "node_id": self.node_id,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                log.info(f"✓ Registered node {self.node_id} with gateway")
                return True
        except Exception as e:
            log.error(f"✗ Node registration failed: {e}")
            return False

    def get_ready_sessions(self) -> List[Dict[str, Any]]:
        """Poll gateway for tasks assigned to this node (Phase 3.1/3.2)."""
        url = f"{self.cwso_url}/nodes/{self.node_id}/tasks"
        token = self.generate_jwt_token("worker")
        headers = {"Authorization": f"Bearer {token}"}

        try:
            raw = self._http_request_with_retry(url, method="GET", headers=headers, timeout=5.0)
            if raw is None:
                return []
            data = json.loads(raw.decode())
            assigned_tasks = data.get("assigned_tasks", [])

            sessions = []
            for task in assigned_tasks:
                sessions.append({
                    "task_id": task.get("task_id"),
                    "session_id": task.get("session_id"),
                    "task_spec": task.get("task_spec", {}),
                })

            if sessions:
                log.info(f"Fetched {len(sessions)} assigned task(s) from orchestrator")
            else:
                log.debug("No assigned tasks for this node")
            return sessions
        except urllib.error.HTTPError as e:
            log.warning(f"get_ready_sessions HTTP error {e.code}: {e}")
            return []
        except Exception as e:
            log.debug(f"Could not fetch assigned tasks: {e}")
            return []

    def execute_session(self, session_id: str, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the real SIA harness and map its artifacts to rollout payloads."""
        description = str(task_spec.get("description") or task_spec.get("prompt") or "").strip()
        workspace_id = str(task_spec.get("workspace_id") or "").strip()
        workspace_path = Path(workspace_id).expanduser() if workspace_id else Path()
        output_path = workspace_path / "output.json" if workspace_id else Path("output.json")
        results_path = workspace_path / "results.json" if workspace_id else Path("results.json")
        stdout_path = workspace_path / f"{session_id}.harness.stdout.log" if workspace_id else Path(f"{session_id}.harness.stdout.log")
        stderr_path = workspace_path / f"{session_id}.harness.stderr.log" if workspace_id else Path(f"{session_id}.harness.stderr.log")

        if not description or not workspace_id:
            error_payload = {
                "kind": "invalid_task_spec",
                "message": "task_spec.description and task_spec.workspace_id are required",
            }
            partial_result = self._build_partial_result_summary("failed", None)
            trajectory = self._build_trajectory_group(
                session_id,
                task_spec,
                "",
                None,
                None,
                [],
                partial_result,
                "failed",
                error_payload,
            )
            return {
                "status": "failed",
                "partial_results": {
                    "execution_status": "failed",
                    "description": description,
                    "workspace_id": workspace_id,
                    "error": error_payload,
                    "artifacts": {},
                },
                "trajectories": [trajectory],
            }

        workspace_path.mkdir(parents=True, exist_ok=True)
        if not self.harness_entrypoint.exists():
            error_payload = {
                "kind": "missing_harness_entrypoint",
                "message": f"Harness entrypoint not found: {self.harness_entrypoint}",
            }
            partial_result = self._build_partial_result_summary("failed", None)
            trajectory = self._build_trajectory_group(
                session_id,
                task_spec,
                "",
                None,
                None,
                [],
                partial_result,
                "failed",
                error_payload,
            )
            return {
                "status": "failed",
                "partial_results": {
                    "execution_status": "failed",
                    "description": description,
                    "workspace_id": str(workspace_path),
                    "error": error_payload,
                    "artifacts": {},
                },
                "trajectories": [trajectory],
            }

        log.info(f"[{session_id}] Starting real SIA harness execution...")
        started_at = time.monotonic()
        before_snapshot = self._snapshot_workspace(workspace_path)
        command = [sys.executable, str(self.harness_entrypoint)]
        env = self._build_harness_environment(task_spec, workspace_path, session_id)
        harness_output: Optional[Dict[str, Any]] = None
        evaluation_output: Optional[Dict[str, Any]] = None
        error_payload: Optional[Dict[str, Any]] = None
        execution_status = "completed"
        stdout_text = ""
        stderr_text = ""

        try:
            completed = subprocess.run(
                command,
                cwd=str(self.harness_entrypoint.parent),
                env=env,
                capture_output=True,
                text=True,
                timeout=self.execution_timeout,
                check=False,
            )
            stdout_text = completed.stdout or ""
            stderr_text = completed.stderr or ""
            self._write_stream_artifact(stdout_path, stdout_text)
            self._write_stream_artifact(stderr_path, stderr_text)
            harness_output = _safe_read_json(output_path)
            evaluation_output = _safe_read_json(results_path)
            if completed.returncode != 0 or (harness_output or {}).get("status") == "error":
                execution_status = "failed"
                error_payload = {
                    "kind": "harness_error",
                    "message": (harness_output or {}).get("error") or _truncate_text(stderr_text) or "Harness returned a non-zero exit code",
                    "exit_code": completed.returncode,
                }
        except subprocess.TimeoutExpired as exc:
            execution_status = "timeout"
            stdout_text = exc.stdout or ""
            stderr_text = exc.stderr or ""
            self._write_stream_artifact(stdout_path, stdout_text)
            self._write_stream_artifact(stderr_path, stderr_text)
            harness_output = _safe_read_json(output_path)
            evaluation_output = _safe_read_json(results_path)
            error_payload = {
                "kind": "timeout",
                "message": f"Harness exceeded timeout of {self.execution_timeout:.0f}s",
                "timeout_seconds": self.execution_timeout,
            }

        execution_time_ms = int((time.monotonic() - started_at) * 1000)
        artifacts = self._collect_workspace_artifacts(workspace_path, before_snapshot)
        generated_code = self._extract_generated_code(harness_output, artifacts)
        partial_result = self._build_partial_result_summary(execution_status, evaluation_output)
        trajectory = self._build_trajectory_group(
            session_id,
            task_spec,
            generated_code,
            harness_output,
            evaluation_output,
            artifacts,
            partial_result,
            execution_status,
            error_payload,
        )
        partial_results = {
            "execution_status": execution_status,
            "description": description,
            "workspace_id": str(workspace_path),
            "max_steps": _coerce_positive_int(task_spec.get("max_steps"), 10),
            "execution_time_ms": execution_time_ms,
            "generated_code": generated_code,
            "harness_output": harness_output,
            "evaluation_output": evaluation_output,
            "generated_artifacts": artifacts,
            "artifacts": {
                "output_json": str(output_path) if output_path.exists() else "",
                "results_json": str(results_path) if results_path.exists() else "",
                "stdout_log": str(stdout_path),
                "stderr_log": str(stderr_path),
            },
            "error": error_payload,
            "trace": (harness_output or {}).get("trajectory"),
        }
        if evaluation_output and "overall_score" in evaluation_output:
            partial_results["reward"] = partial_result["reward"]

        if execution_status == "completed":
            log.info(f"[{session_id}] ✓ Real SIA harness execution complete")
        else:
            log.warning(f"[{session_id}] Harness finished with status={execution_status}")
        return {
            "status": execution_status,
            "partial_results": partial_results,
            "trajectories": [trajectory],
        }

    def report_session_result(
        self,
        task_id: str,
        session_id: str,
        execution_result: Dict[str, Any],
    ) -> bool:
        """Report session completion back to gateway via /callbacks/session_result endpoint."""
        url = f"{self.cwso_url}/callbacks/session_result"
        token = self.generate_jwt_token("worker")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        partial_results = execution_result.get("partial_results", {})
        trajectories = execution_result.get("trajectories") or [
            {
                "session_id": session_id,
                "chains": [],
                "metadata": {
                    "execution_status": execution_result.get("status", "completed"),
                    "partial_results": json.dumps(partial_results),
                },
            }
        ]
        payload = {
            "task_id": task_id,
            "session_id": session_id,
            "trajectories": trajectories,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                log.info(
                    f"[{session_id}] ✓ Result reported "
                    f"(status={execution_result.get('status', 'completed')})"
                )
                self.session_count += 1
                return True
        except Exception as e:
            log.error(f"[{session_id}] ✗ Result reporting failed: {e}")
            return False

    def run_loop(self, poll_interval: float = 2.0):
        """Main executor loop: register, start heartbeat, poll, execute, report."""
        log.info(f"Starting SIA executor loop (node_id={self.node_id})...")

        # Register node with gateway
        if not self.register_node():
            log.error("Failed to register node; exiting")
            return

        # Phase 3.2: start background heartbeat thread immediately after registration
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, name="heartbeat", daemon=True
        )
        self._heartbeat_thread.start()

        # Main loop: poll for sessions and execute
        while self.running:
            try:
                sessions = self.get_ready_sessions()
                for session in sessions:
                    task_id = session.get("task_id")
                    session_id = session.get("session_id")
                    task_spec = session.get("task_spec", {})

                    log.info(f"[{session_id}] Accepted session from gateway (task={task_id})")

                    # Execute the session
                    execution_result = self.execute_session(session_id, task_spec)

                    # Report results back (include task_id for tracking)
                    self.report_session_result(task_id, session_id, execution_result)

                # Poll interval between checks
                time.sleep(poll_interval)

            except KeyboardInterrupt:
                log.info("Interrupted; shutting down...")
                break
            except Exception as e:
                log.error(f"Error in execution loop: {e}")
                time.sleep(poll_interval)

        # Signal heartbeat thread to stop and wait briefly
        self.running = False
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=5.0)

        log.info(f"SIA executor stopped (processed {self.session_count} sessions)")


def main():
    parser = argparse.ArgumentParser(
        description="SIA executor — Phase 3.2 with real task polling and heartbeat"
    )
    parser.add_argument(
        "--cwso-url", default="http://localhost:8080", help="CWSO orchestrator URL"
    )
    parser.add_argument("--node-id", default="sia-executor-1", help="Executor node ID")
    parser.add_argument("--jwt-secret", required=False, help="CWSO JWT secret")
    parser.add_argument(
        "--mock-delay", type=float, default=2.0, help="Mock execution delay (seconds)"
    )
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Poll interval (seconds)")
    parser.add_argument(
        "--heartbeat-interval",
        type=float,
        default=HEARTBEAT_INTERVAL,
        help="Heartbeat interval in seconds (default 30)",
    )
    parser.add_argument(
        "--execution-timeout",
        type=float,
        default=DEFAULT_EXECUTION_TIMEOUT,
        help="Harness execution timeout in seconds (default 120)",
    )
    args = parser.parse_args()

    # Read JWT secret from file if not provided
    jwt_secret = args.jwt_secret
    if not jwt_secret:
        secret_file = Path("/home/emage/Code/emage/CWSO/.env.jwt.dev")
        if secret_file.exists():
            jwt_secret = secret_file.read_text().strip()
        else:
            log.error("JWT secret not provided and .env.jwt.dev not found")
            sys.exit(1)

    # Create and run executor
    executor = SIAExecutor(
        cwso_url=args.cwso_url,
        node_id=args.node_id,
        jwt_secret=jwt_secret,
        mock_delay=args.mock_delay,
        heartbeat_interval=args.heartbeat_interval,
        execution_timeout=args.execution_timeout,
    )

    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        log.info("Received shutdown signal...")
        executor.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the executor loop
    executor.run_loop(poll_interval=args.poll_interval)


if __name__ == "__main__":
    main()
