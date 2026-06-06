"""Functional tests for v3 trigger framework prototype."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import current_implementation_root, repo_root


class TestV3TriggerFramework(unittest.TestCase):
    def test_schedule_trigger_executes_and_audits(self):
        runner = current_implementation_root() / "runtime" / "triggers" / "runner.py"
        trigger = (
            current_implementation_root()
            / "triggers"
            / "examples"
            / "schedule-daily.json"
        )
        policy = (
            current_implementation_root()
            / "triggers"
            / "examples"
            / "policy-default.json"
        )

        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.json"
            audit = Path(tmp) / "audit.log"

            proc = subprocess.run(
                [
                    "python3",
                    str(runner),
                    "--trigger",
                    str(trigger),
                    "--policy",
                    str(policy),
                    "--queue",
                    str(queue),
                    "--audit-log",
                    str(audit),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            queue_payload = json.loads(queue.read_text(encoding="utf-8"))
            self.assertEqual(len(queue_payload["events"]), 1)
            self.assertEqual(queue_payload["events"][0]["triggerId"], "schedule-daily-health-check")

            lines = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
            statuses = [item["status"] for item in lines]
            self.assertIn("pass", statuses)
            self.assertIn("success", statuses)

    def test_event_trigger_retries_then_succeeds(self):
        runner = current_implementation_root() / "runtime" / "triggers" / "runner.py"
        trigger = (
            current_implementation_root()
            / "triggers"
            / "examples"
            / "event-webhook.json"
        )
        policy = (
            current_implementation_root()
            / "triggers"
            / "examples"
            / "policy-default.json"
        )

        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.json"
            audit = Path(tmp) / "audit.log"

            proc = subprocess.run(
                [
                    "python3",
                    str(runner),
                    "--trigger",
                    str(trigger),
                    "--policy",
                    str(policy),
                    "--queue",
                    str(queue),
                    "--audit-log",
                    str(audit),
                    "--simulate-failures",
                    "1",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            lines = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
            retries = [item for item in lines if item["status"] == "retry"]
            self.assertEqual(len(retries), 1)

    def test_trigger_policy_denies_unknown_source(self):
        runner = current_implementation_root() / "runtime" / "triggers" / "runner.py"
        policy = (
            current_implementation_root()
            / "triggers"
            / "examples"
            / "policy-default.json"
        )

        with tempfile.TemporaryDirectory() as tmp:
            trigger = Path(tmp) / "bad-trigger.json"
            queue = Path(tmp) / "queue.json"
            audit = Path(tmp) / "audit.log"
            trigger.write_text(
                json.dumps(
                    {
                        "triggerId": "event-bad-source",
                        "type": "event",
                        "source": "unknown.source",
                        "event": {"name": "issue.opened"},
                        "steeringInput": {"taskId": "T019", "intent": "x"},
                        "retryPolicy": {"maxAttempts": 2, "backoffSeconds": 1},
                    }
                ),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    "python3",
                    str(runner),
                    "--trigger",
                    str(trigger),
                    "--policy",
                    str(policy),
                    "--queue",
                    str(queue),
                    "--audit-log",
                    str(audit),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)
            self.assertIn("policy_denied", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
