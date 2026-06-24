"""
Unit tests for sia-executor.py Phase 3.2 additions:
- Retry/backoff on transient HTTP errors
- Heartbeat loop start/stop
- get_ready_sessions returns real tasks
- send_heartbeat returns True on success, False on failure
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Load sia-executor module without executing main()
# ---------------------------------------------------------------------------

_EXECUTOR_PATH = (
    Path(__file__).parent.parent.parent
    / "implementation" / "scripts" / "sia-executor.py"
)


def _load_executor():
    spec = importlib.util.spec_from_file_location("sia_executor", _EXECUTOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_executor()
SIAExecutor = _mod.SIAExecutor
_RETRY_MAX_TRIES = _mod._RETRY_MAX_TRIES
HEARTBEAT_INTERVAL = _mod.HEARTBEAT_INTERVAL


def _make_executor(**kwargs):
    defaults = dict(
        cwso_url="http://localhost:8080",
        node_id="test-node-1",
        jwt_secret="test-secret",
        mock_delay=0.0,
        heartbeat_interval=0.5,  # short interval for tests
    )
    defaults.update(kwargs)
    return SIAExecutor(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRetryHelper(unittest.TestCase):
    """_http_request_with_retry retries transient 5xx errors and gives up."""

    def test_succeeds_on_first_attempt(self):
        executor = _make_executor()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"ok": true}'

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            result = executor._http_request_with_retry(
                "http://localhost:8080/test", method="GET", max_tries=3
            )
        self.assertEqual(result, b'{"ok": true}')
        self.assertEqual(mock_open.call_count, 1)

    def test_retries_on_500_then_succeeds(self):
        executor = _make_executor()
        server_error = urllib.error.HTTPError(
            url="http://localhost/test", code=500, msg="Internal Server Error",
            hdrs=None, fp=None
        )
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b"data"

        call_count = {"n": 0}
        def urlopen_side_effect(req, timeout=None):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise server_error
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=urlopen_side_effect):
            with patch("time.sleep"):  # skip real sleep in retry backoff
                result = executor._http_request_with_retry(
                    "http://localhost:8080/test", max_tries=3
                )
        self.assertEqual(result, b"data")
        self.assertEqual(call_count["n"], 2)

    def test_gives_up_after_max_tries(self):
        executor = _make_executor()
        url_error = urllib.error.URLError("connection refused")

        with patch("urllib.request.urlopen", side_effect=url_error):
            with patch("time.sleep"):
                result = executor._http_request_with_retry(
                    "http://localhost:8080/test", max_tries=_RETRY_MAX_TRIES
                )
        self.assertIsNone(result)

    def test_does_not_retry_4xx(self):
        executor = _make_executor()
        client_error = urllib.error.HTTPError(
            url="http://localhost/test", code=404, msg="Not Found",
            hdrs=None, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=client_error):
            with self.assertRaises(urllib.error.HTTPError):
                executor._http_request_with_retry("http://localhost/test", max_tries=3)


class TestSendHeartbeat(unittest.TestCase):
    """send_heartbeat() returns True on success, False on failure."""

    def test_returns_true_on_success(self):
        executor = _make_executor()
        with patch.object(executor, "_http_request_with_retry", return_value=b'{"status":"ok"}'):
            self.assertTrue(executor.send_heartbeat())

    def test_returns_false_on_none(self):
        executor = _make_executor()
        with patch.object(executor, "_http_request_with_retry", return_value=None):
            self.assertFalse(executor.send_heartbeat())

    def test_returns_false_on_exception(self):
        executor = _make_executor()
        with patch.object(
            executor, "_http_request_with_retry", side_effect=Exception("network down")
        ):
            self.assertFalse(executor.send_heartbeat())

    def test_calls_correct_endpoint(self):
        executor = _make_executor()
        captured = {}

        def fake_retry(url, **kwargs):
            captured["url"] = url
            return b'{"status":"ok"}'

        with patch.object(executor, "_http_request_with_retry", side_effect=fake_retry):
            executor.send_heartbeat()

        self.assertIn("/nodes/test-node-1/heartbeat", captured["url"])


class TestHeartbeatLoop(unittest.TestCase):
    """Heartbeat daemon thread starts, fires, and stops when running=False."""

    def test_heartbeat_fires_and_stops(self):
        executor = _make_executor(heartbeat_interval=0.2)
        heartbeat_calls = []

        def fake_heartbeat():
            heartbeat_calls.append(time.monotonic())
            return True

        with patch.object(executor, "send_heartbeat", side_effect=fake_heartbeat):
            t = threading.Thread(target=executor._heartbeat_loop, daemon=True)
            t.start()
            time.sleep(0.7)          # allow ~3 heartbeat fires
            executor.running = False
            t.join(timeout=2.0)

        self.assertGreaterEqual(len(heartbeat_calls), 2, "expected ≥2 heartbeats during 0.7s")
        self.assertFalse(t.is_alive(), "heartbeat thread did not stop")


class TestRegisterNode(unittest.TestCase):
    """register_node() posts to the orchestrator register endpoint."""

    def test_register_node_returns_true_on_success(self):
        executor = _make_executor()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            self.assertTrue(executor.register_node())

        request = mock_open.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:8080/nodes/register")
        self.assertEqual(request.get_method(), "POST")

    def test_register_node_returns_false_on_failure(self):
        executor = _make_executor()

        with patch("urllib.request.urlopen", side_effect=OSError("boom")):
            self.assertFalse(executor.register_node())


class TestGetReadySessions(unittest.TestCase):
    """get_ready_sessions() returns mapped sessions from orchestrator response."""

    def test_returns_sessions_from_response(self):
        executor = _make_executor()
        mock_payload = json.dumps({
            "assigned_tasks": [
                {
                    "task_id": "task-abc",
                    "session_id": "sess-123",
                    "task_spec": {"description": "write code", "workspace_id": "ws-1"},
                    "assigned_at": "2026-06-23T10:00:00Z",
                }
            ]
        }).encode()

        with patch.object(executor, "_http_request_with_retry", return_value=mock_payload):
            sessions = executor.get_ready_sessions()

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["task_id"], "task-abc")
        self.assertEqual(sessions[0]["session_id"], "sess-123")
        self.assertEqual(sessions[0]["task_spec"]["description"], "write code")

    def test_returns_empty_on_no_tasks(self):
        executor = _make_executor()
        with patch.object(
            executor, "_http_request_with_retry",
            return_value=b'{"assigned_tasks":[]}'
        ):
            sessions = executor.get_ready_sessions()
        self.assertEqual(sessions, [])

    def test_returns_empty_on_network_failure(self):
        executor = _make_executor()
        with patch.object(executor, "_http_request_with_retry", return_value=None):
            sessions = executor.get_ready_sessions()
        self.assertEqual(sessions, [])

    def test_returns_empty_on_4xx(self):
        executor = _make_executor()
        http_err = urllib.error.HTTPError(
            url="http://localhost/nodes/test/tasks", code=403, msg="Forbidden",
            hdrs=None, fp=None
        )
        with patch.object(executor, "_http_request_with_retry", side_effect=http_err):
            sessions = executor.get_ready_sessions()
        self.assertEqual(sessions, [])


class TestExecuteSessionPhase33(unittest.TestCase):
    """execute_session() invokes the real harness entrypoint contract."""

    def test_harness_environment_includes_task_model_and_backend(self):
        executor = _make_executor()

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            env = executor._build_harness_environment(
                {
                    "description": "implement email validator",
                    "workspace_id": str(workspace),
                    "max_steps": 7,
                    "backend": "openhands",
                    "model": "v1-ft",
                },
                workspace,
                "sess-1",
            )

        self.assertEqual(env["SIA_BACKEND"], "openhands")
        self.assertEqual(env["SIA_MODEL"], "v1-ft")

    def test_maps_harness_outputs_into_executor_result(self):
        executor = _make_executor(execution_timeout=5.0)

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            def fake_run(command, cwd, env, capture_output, text, timeout, check):
                self.assertEqual(command[1], str(executor.harness_entrypoint))
                self.assertEqual(env["CWSO_HARNESS_PROMPT"], "implement email validator")
                self.assertEqual(env["CWSO_HARNESS_WORKSPACE"], str(workspace))
                self.assertEqual(env["SIA_MAX_TURNS"], "7")
                self.assertEqual(env["SIA_BACKEND"], "claude")
                self.assertEqual(env["SIA_MODEL"], "baseline")
                (workspace / "output.json").write_text(
                    json.dumps(
                        {
                            "status": "success",
                            "generated_code": "def solve():\n    return 42\n",
                            "trajectory": {"steps": 2},
                        }
                    ),
                    encoding="utf-8",
                )
                (workspace / "results.json").write_text(
                    json.dumps({"overall_score": 0.91, "passed": True}),
                    encoding="utf-8",
                )
                (workspace / "solution.py").write_text(
                    "def solve():\n    return 42\n",
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            with patch("subprocess.run", side_effect=fake_run):
                result = executor.execute_session(
                    "sess-1",
                    {
                        "description": "implement email validator",
                        "workspace_id": str(workspace),
                        "max_steps": 7,
                        "backend": "claude",
                        "model": "baseline",
                    },
                )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["partial_results"]["execution_status"], "completed")
        self.assertEqual(result["partial_results"]["reward"], 0.91)
        self.assertIn("generated_code", result["partial_results"])
        self.assertIn("def solve", result["partial_results"]["generated_code"])
        self.assertEqual(len(result["trajectories"]), 1)
        trajectory = result["trajectories"][0]
        self.assertEqual(trajectory["metadata"]["execution_status"], "completed")
        self.assertEqual(trajectory["rewards"], [0.91])

    def test_returns_structured_timeout_payload(self):
        executor = _make_executor(execution_timeout=1.0)

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            with patch(
                "subprocess.run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=[sys.executable, str(executor.harness_entrypoint)],
                    timeout=1.0,
                    output="partial stdout",
                    stderr="partial stderr",
                ),
            ):
                result = executor.execute_session(
                    "sess-timeout",
                    {
                        "description": "slow task",
                        "workspace_id": str(workspace),
                        "max_steps": 3,
                    },
                )

            stdout_log = Path(result["partial_results"]["artifacts"]["stdout_log"])
            stderr_log = Path(result["partial_results"]["artifacts"]["stderr_log"])

            self.assertTrue(stdout_log.exists())
            self.assertTrue(stderr_log.exists())

        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["partial_results"]["error"]["kind"], "timeout")
        self.assertEqual(result["trajectories"][0]["metadata"]["execution_status"], "timeout")


class TestReportSessionResultPhase33(unittest.TestCase):
    """report_session_result() forwards the real trajectory payload."""

    def test_uses_execution_result_trajectories(self):
        executor = _make_executor()
        captured = {}

        class _Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(req, timeout=None):
            captured["payload"] = json.loads(req.data.decode("utf-8"))
            return _Response()

        execution_result = {
            "status": "failed",
            "partial_results": {"execution_status": "failed"},
            "trajectories": [
                {
                    "session_id": "sess-9",
                    "chains": [],
                    "metadata": {"execution_status": "failed", "error": "boom"},
                }
            ],
        }

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            reported = executor.report_session_result("task-1", "sess-9", execution_result)

        self.assertTrue(reported)
        self.assertEqual(captured["payload"]["task_id"], "task-1")
        self.assertEqual(captured["payload"]["session_id"], "sess-9")
        self.assertEqual(
            captured["payload"]["trajectories"][0]["metadata"]["execution_status"],
            "failed",
        )


if __name__ == "__main__":
    unittest.main()
