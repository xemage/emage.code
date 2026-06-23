"""Functional tests for Task T224: Reward Attachment via Merge."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add implementation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "implementation" / "adapters"))

# Import from reward_attachment module
import importlib.util
reward_attachment_path = (
    Path(__file__).parent.parent.parent
    / "implementation" / "adapters" / "sia-target" / "reward_attachment.py"
)
spec = importlib.util.spec_from_file_location("reward_attachment", reward_attachment_path)
reward_attachment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reward_attachment)

# Register in sys.modules for patching
sys.modules['reward_attachment'] = reward_attachment

# Extract functions
read_evaluation_result = reward_attachment.read_evaluation_result
build_merge_request = reward_attachment.build_merge_request
attach_reward_via_merge = reward_attachment.attach_reward_via_merge
attach_reward_to_job = reward_attachment.attach_reward_to_job


class TestEvaluationReading(unittest.TestCase):
    """Test suite for reading and validating evaluation results."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_read_evaluation_result_valid_submission(self) -> None:
        """Successfully read valid evaluation results."""
        results_json = {
            "overall_score": 0.95,
            "passed": True,
            "diagnostics_count": 0,
            "primary_metric": 0.95,
            "metrics": {"schema_validity": 1.0, "content_completeness": 0.9},
            "diagnostics": []
        }
        results_path = self.workspace_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results_json, f)

        result = read_evaluation_result(str(self.workspace_path))

        self.assertEqual(result["overall_score"], 0.95)
        self.assertTrue(result["passed"])
        self.assertEqual(result["diagnostics_count"], 0)

    def test_read_evaluation_result_failing_submission(self) -> None:
        """Successfully read failing evaluation results."""
        results_json = {
            "overall_score": 0.35,
            "passed": False,
            "diagnostics_count": 5,
            "diagnostics": [
                "missing top-level field: tasks",
                "invalid schema"
            ]
        }
        results_path = self.workspace_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results_json, f)

        result = read_evaluation_result(str(self.workspace_path))

        self.assertEqual(result["overall_score"], 0.35)
        self.assertFalse(result["passed"])
        self.assertEqual(result["diagnostics_count"], 5)

    def test_read_evaluation_result_file_not_found(self) -> None:
        """Raise FileNotFoundError when results.json missing."""
        with self.assertRaises(FileNotFoundError) as cm:
            read_evaluation_result(str(self.workspace_path))

        self.assertIn("results.json not found", str(cm.exception))

    def test_read_evaluation_result_malformed_json(self) -> None:
        """Raise JSONDecodeError when results.json is malformed."""
        results_path = self.workspace_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        with self.assertRaises(json.JSONDecodeError):
            read_evaluation_result(str(self.workspace_path))

    def test_read_evaluation_result_missing_required_fields(self) -> None:
        """Raise ValueError when required fields are missing."""
        results_json = {
            "overall_score": 0.95,
            # Missing 'passed' field
        }
        results_path = self.workspace_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results_json, f)

        with self.assertRaises(ValueError) as cm:
            read_evaluation_result(str(self.workspace_path))

        self.assertIn("missing required fields", str(cm.exception))
        self.assertIn("passed", str(cm.exception))


class TestMergeRequestBuilding(unittest.TestCase):
    """Test suite for building MergeRequest payloads."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.dispatch_result = {
            "workspace_uuid": "workspace-123-456-789",
            "rollout_session_id": "session-abc-def-ghi",
        }

    def test_build_merge_request_good_submission(self) -> None:
        """Build valid merge request from passing submission."""
        evaluation = {
            "overall_score": 0.95,
            "passed": True,
            "diagnostics_count": 0,
        }

        merge_req = build_merge_request(self.dispatch_result, evaluation)

        self.assertEqual(merge_req["workspace_uuid"], "workspace-123-456-789")
        self.assertEqual(merge_req["rollout_session_id"], "session-abc-def-ghi")
        self.assertEqual(merge_req["evaluation_reward"], 0.95)
        self.assertTrue(merge_req["evaluation_passed"])
        self.assertEqual(merge_req["finish_reason"], "success")
        self.assertEqual(merge_req["diagnostics_count"], 0)
        self.assertIn("T", merge_req["attach_timestamp"])  # ISO8601 format check
        self.assertTrue(merge_req["attach_timestamp"].endswith("Z"))

    def test_build_merge_request_failing_submission(self) -> None:
        """Build valid merge request from failing submission."""
        evaluation = {
            "overall_score": 0.25,
            "passed": False,
            "diagnostics_count": 8,
        }

        merge_req = build_merge_request(self.dispatch_result, evaluation)

        self.assertEqual(merge_req["evaluation_reward"], 0.25)
        self.assertFalse(merge_req["evaluation_passed"])
        self.assertEqual(merge_req["finish_reason"], "failure")
        self.assertEqual(merge_req["diagnostics_count"], 8)

    def test_build_merge_request_edge_case_zero_score(self) -> None:
        """Handle zero evaluation score correctly."""
        evaluation = {
            "overall_score": 0.0,
            "passed": False,
            "diagnostics_count": 10,
        }

        merge_req = build_merge_request(self.dispatch_result, evaluation)

        self.assertEqual(merge_req["evaluation_reward"], 0.0)
        self.assertFalse(merge_req["evaluation_passed"])

    def test_build_merge_request_edge_case_perfect_score(self) -> None:
        """Handle perfect (1.0) evaluation score correctly."""
        evaluation = {
            "overall_score": 1.0,
            "passed": True,
            "diagnostics_count": 0,
        }

        merge_req = build_merge_request(self.dispatch_result, evaluation)

        self.assertEqual(merge_req["evaluation_reward"], 1.0)
        self.assertTrue(merge_req["evaluation_passed"])

    def test_build_merge_request_clamps_out_of_range_score(self) -> None:
        """Clamp out-of-range scores to [0, 1]."""
        # Test clamping > 1.0
        evaluation = {
            "overall_score": 1.5,
            "passed": True,
            "diagnostics_count": 0,
        }

        merge_req = build_merge_request(self.dispatch_result, evaluation)
        self.assertEqual(merge_req["evaluation_reward"], 1.0)

        # Test clamping < 0.0
        evaluation["overall_score"] = -0.5
        merge_req = build_merge_request(self.dispatch_result, evaluation)
        self.assertEqual(merge_req["evaluation_reward"], 0.0)

    def test_build_merge_request_missing_dispatch_field(self) -> None:
        """Raise KeyError when dispatch_result missing required fields."""
        bad_dispatch = {
            "workspace_uuid": "workspace-123",
            # Missing 'rollout_session_id'
        }
        evaluation = {
            "overall_score": 0.95,
            "passed": True,
        }

        with self.assertRaises(KeyError):
            build_merge_request(bad_dispatch, evaluation)

    def test_build_merge_request_optional_diagnostics_count(self) -> None:
        """Handle missing diagnostics_count gracefully (default to 0)."""
        evaluation = {
            "overall_score": 0.85,
            "passed": True,
            # diagnostics_count omitted
        }

        merge_req = build_merge_request(self.dispatch_result, evaluation)

        self.assertEqual(merge_req["diagnostics_count"], 0)


class TestCwsoIntegration(unittest.TestCase):
    """Test suite for CWSO merge endpoint integration."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.merge_request = {
            "workspace_uuid": "workspace-123",
            "rollout_session_id": "session-abc",
            "evaluation_reward": 0.95,
            "evaluation_passed": True,
            "finish_reason": "success",
            "diagnostics_count": 0,
            "attach_timestamp": "2026-06-23T12:00:00Z",
        }
        self.cwso_base_url = "http://localhost:8080"
        self.jwt_token = "jwt-test-token-123"

    @patch("reward_attachment.requests.post")
    def test_attach_reward_via_merge_success(self, mock_post: Mock) -> None:
        """Successfully attach reward with valid CWSO response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "merged": True,
            "conflict_resolution_strategy": "ast_semantic_only",
            "trajectory_id": "traj-001-uuid"
        }
        mock_post.return_value = mock_response

        result = attach_reward_via_merge(
            self.merge_request,
            self.cwso_base_url,
            self.jwt_token
        )

        self.assertTrue(result["merged"])
        self.assertEqual(result["trajectory_id"], "traj-001-uuid")
        mock_post.assert_called_once()

        # Verify request payload
        call_args = mock_post.call_args
        self.assertEqual(call_args.kwargs["json"], self.merge_request)
        self.assertIn("Authorization", call_args.kwargs["headers"])
        self.assertIn("jwt-test-token", call_args.kwargs["headers"]["Authorization"])

    @patch("reward_attachment.requests.post")
    def test_attach_reward_via_merge_connection_error(self, mock_post: Mock) -> None:
        """Raise ConnectionError when CWSO is unavailable."""
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with self.assertRaises(ConnectionError) as cm:
            attach_reward_via_merge(
                self.merge_request,
                self.cwso_base_url,
                self.jwt_token
            )

        self.assertIn("Failed to connect", str(cm.exception))

    @patch("reward_attachment.requests.post")
    def test_attach_reward_via_merge_timeout(self, mock_post: Mock) -> None:
        """Raise ConnectionError when merge request times out."""
        import requests

        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        with self.assertRaises(ConnectionError) as cm:
            attach_reward_via_merge(
                self.merge_request,
                self.cwso_base_url,
                self.jwt_token,
                timeout=5
            )

        self.assertIn("timed out", str(cm.exception))

    @patch("reward_attachment.requests.post")
    def test_attach_reward_via_merge_http_error(self, mock_post: Mock) -> None:
        """Raise ConnectionError on HTTP error response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_post.return_value = mock_response

        with self.assertRaises(ConnectionError):
            attach_reward_via_merge(
                self.merge_request,
                self.cwso_base_url,
                self.jwt_token
            )

    @patch("reward_attachment.requests.post")
    def test_attach_reward_via_merge_invalid_json(self, mock_post: Mock) -> None:
        """Raise ValueError when CWSO response is not valid JSON."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as cm:
            attach_reward_via_merge(
                self.merge_request,
                self.cwso_base_url,
                self.jwt_token
            )

        self.assertIn("not valid JSON", str(cm.exception))


class TestOrchestration(unittest.TestCase):
    """Test suite for full reward attachment orchestration."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name)

        # Create a valid results.json
        self.results_json = {
            "overall_score": 0.92,
            "passed": True,
            "diagnostics_count": 1,
            "diagnostics": ["minor issue"]
        }
        results_path = self.workspace_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(self.results_json, f)

        self.dispatch_result = {
            "workspace_uuid": "workspace-123-456",
            "rollout_session_id": "session-xyz-789",
        }

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    @patch("reward_attachment.attach_reward_via_merge")
    def test_attach_reward_to_job_end_to_end(
        self, mock_merge: Mock
    ) -> None:
        """Full orchestration: read evaluation → build merge → attach."""
        mock_merge.return_value = {
            "merged": True,
            "trajectory_id": "traj-e2e-001"
        }

        result = attach_reward_to_job(
            self.dispatch_result,
            str(self.workspace_path),
            cwso_base_url="http://localhost:8080",
            cwso_jwt="jwt-token-123"
        )

        self.assertIn("Reward attached", result)
        self.assertIn("session-xyz-789", result)
        self.assertIn("0.92", result)
        self.assertIn("True", result)
        mock_merge.assert_called_once()

    def test_attach_reward_to_job_missing_jwt_testing_mode(self) -> None:
        """Skip merge attachment when JWT not set (testing mode)."""
        result = attach_reward_to_job(
            self.dispatch_result,
            str(self.workspace_path),
            cwso_base_url="http://localhost:8080",
            cwso_jwt=""  # Empty JWT triggers testing mode
        )

        self.assertIn("mock", result)
        self.assertIn("session-xyz-789", result)

    @patch("reward_attachment.attach_reward_via_merge")
    def test_attach_reward_to_job_graceful_failure(
        self, mock_merge: Mock
    ) -> None:
        """Gracefully handle merge failure when fail_gracefully=True."""
        mock_merge.side_effect = ConnectionError("CWSO unavailable")

        result = attach_reward_to_job(
            self.dispatch_result,
            str(self.workspace_path),
            cwso_base_url="http://localhost:8080",
            cwso_jwt="jwt-token-123",
            fail_gracefully=True
        )

        self.assertIn("skipped", result)
        self.assertIn("ConnectionError", result)

    @patch("reward_attachment.attach_reward_via_merge")
    def test_attach_reward_to_job_hard_failure(
        self, mock_merge: Mock
    ) -> None:
        """Raise RuntimeError when fail_gracefully=False and merge fails."""
        mock_merge.side_effect = ConnectionError("CWSO unavailable")

        with self.assertRaises(RuntimeError) as cm:
            attach_reward_to_job(
                self.dispatch_result,
                str(self.workspace_path),
                cwso_base_url="http://localhost:8080",
                cwso_jwt="jwt-token-123",
                fail_gracefully=False
            )

        self.assertIn("Reward attachment failed", str(cm.exception))

    def test_attach_reward_to_job_missing_results_json(self) -> None:
        """Raise RuntimeError when results.json not found and fail_gracefully=False."""
        empty_workspace = tempfile.TemporaryDirectory()
        empty_path = Path(empty_workspace.name)

        with self.assertRaises(RuntimeError) as cm:
            attach_reward_to_job(
                self.dispatch_result,
                str(empty_path),
                cwso_base_url="http://localhost:8080",
                cwso_jwt="jwt-token-123",
                fail_gracefully=False
            )

        self.assertIn("Reward attachment failed", str(cm.exception))
        empty_workspace.cleanup()


class TestSchemaValidation(unittest.TestCase):
    """Test suite for MergeRequest schema compliance."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.dispatch_result = {
            "workspace_uuid": "workspace-123",
            "rollout_session_id": "session-abc",
        }
        self.evaluation = {
            "overall_score": 0.85,
            "passed": True,
            "diagnostics_count": 2,
        }

    def test_merge_request_has_all_required_fields(self) -> None:
        """Verify MergeRequest contains all required schema fields."""
        required_fields = {
            "workspace_uuid",
            "rollout_session_id",
            "evaluation_reward",
            "evaluation_passed",
            "finish_reason",
            "diagnostics_count",
            "attach_timestamp",
        }

        merge_req = build_merge_request(self.dispatch_result, self.evaluation)

        self.assertTrue(required_fields.issubset(merge_req.keys()))

    def test_merge_request_field_types(self) -> None:
        """Verify MergeRequest fields have correct types."""
        merge_req = build_merge_request(self.dispatch_result, self.evaluation)

        self.assertIsInstance(merge_req["workspace_uuid"], str)
        self.assertIsInstance(merge_req["rollout_session_id"], str)
        self.assertIsInstance(merge_req["evaluation_reward"], float)
        self.assertIsInstance(merge_req["evaluation_passed"], bool)
        self.assertIsInstance(merge_req["finish_reason"], str)
        self.assertIsInstance(merge_req["diagnostics_count"], int)
        self.assertIsInstance(merge_req["attach_timestamp"], str)

    def test_merge_request_evaluation_reward_in_valid_range(self) -> None:
        """Verify evaluation_reward is in [0, 1] range."""
        merge_req = build_merge_request(self.dispatch_result, self.evaluation)

        self.assertGreaterEqual(merge_req["evaluation_reward"], 0.0)
        self.assertLessEqual(merge_req["evaluation_reward"], 1.0)

    def test_merge_request_finish_reason_valid_values(self) -> None:
        """Verify finish_reason is either 'success' or 'failure'."""
        valid_reasons = {"success", "failure"}

        # Test success case
        merge_req = build_merge_request(self.dispatch_result, self.evaluation)
        self.assertIn(merge_req["finish_reason"], valid_reasons)

        # Test failure case
        self.evaluation["passed"] = False
        merge_req = build_merge_request(self.dispatch_result, self.evaluation)
        self.assertIn(merge_req["finish_reason"], valid_reasons)

    def test_merge_request_timestamp_iso8601_format(self) -> None:
        """Verify attach_timestamp is valid ISO8601 format."""
        merge_req = build_merge_request(self.dispatch_result, self.evaluation)
        timestamp = merge_req["attach_timestamp"]

        # Check ISO8601 format: 2026-06-23T12:00:00.000000Z
        self.assertRegex(
            timestamp,
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z"
        )
        self.assertTrue(timestamp.endswith("Z"))


if __name__ == "__main__":
    unittest.main()
