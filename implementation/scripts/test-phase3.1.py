#!/usr/bin/env python3
"""
Quick verification test for Phase 3.1 task assignment mechanism.
Tests that the orchestrator can assign tasks and the executor can fetch them.
"""

import json
import sys
import subprocess
import time
import requests
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
CWSO_URL = "http://localhost:8080"
NODE_ID = "test-executor-1"
JWT_SECRET_FILE = Path("/home/emage/Code/emage/CWSO/.env.jwt.dev")

def generate_jwt_token(node_id: str, role: str = "worker") -> str:
    """Generate HS256 JWT token."""
    import base64
    import hashlib
    import hmac
    import json as json_lib
    from datetime import datetime, timezone

    jwt_secret = JWT_SECRET_FILE.read_text().strip()
    now = int(datetime.now(timezone.utc).timestamp())
    exp = now + 3600

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": "cwso",
        "aud": ["cwso-mcp"],
        "role": role,
        "exp": exp,
        "nbf": now,
        "iat": now,
        "sub": node_id,
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
            jwt_secret.encode(),
            message,
            hashlib.sha256,
        ).digest()
    ).decode().rstrip("=")

    return f"{header_b64}.{payload_b64}.{signature}"

def register_node() -> bool:
    """Register test node with orchestrator."""
    url = f"{CWSO_URL}/nodes/register"
    token = generate_jwt_token(NODE_ID)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"node_id": NODE_ID}

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
            print(f"✓ Node registered: {result}")
            return True
    except Exception as e:
        print(f"✗ Node registration failed: {e}")
        return False

def submit_task() -> str:
    """Submit a test task."""
    url = f"{CWSO_URL}/rollout/task/submit"
    payload = {
        "task_spec": {
            "description": "Test task for Phase 3.1",
            "workspace_id": "test-workspace",
            "max_steps": 5,
        },
        "num_samples": 1,
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
            task_id = result.get("task_id")
            print(f"✓ Task submitted: {task_id}")
            return task_id
    except Exception as e:
        print(f"✗ Task submission failed: {e}")
        return None

def get_assigned_tasks() -> list:
    """Fetch tasks assigned to our node."""
    url = f"{CWSO_URL}/nodes/{NODE_ID}/tasks"
    token = generate_jwt_token(NODE_ID)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
            tasks = result.get("assigned_tasks", [])
            print(f"✓ Retrieved {len(tasks)} assigned tasks")
            for task in tasks:
                print(f"  - Task: {task.get('task_id')}, Session: {task.get('session_id')}")
            return tasks
    except Exception as e:
        print(f"✗ Failed to fetch assigned tasks: {e}")
        return []

def verify_task_spec(tasks: list, task_id: str) -> bool:
    """Verify that task_spec is included in the response."""
    for task in tasks:
        if task.get("task_id") == task_id:
            spec = task.get("task_spec")
            if spec and spec.get("description"):
                print(f"✓ Task spec verified: {spec.get('description')}")
                return True
    print(f"✗ Task spec not found or missing description")
    return False

def main():
    print("=" * 60)
    print("Phase 3.1 Task Assignment Verification Test")
    print("=" * 60)

    # Step 1: Register node
    print("\n[1/4] Registering executor node...")
    if not register_node():
        print("✗ Failed to register node")
        return 1

    # Step 2: Submit task
    print("\n[2/4] Submitting test task...")
    task_id = submit_task()
    if not task_id:
        print("✗ Failed to submit task")
        return 1

    # Step 3: Wait for assignment
    print("\n[3/4] Waiting for task assignment...")
    time.sleep(2)

    # Step 4: Fetch assigned tasks
    print("\n[4/4] Fetching assigned tasks...")
    tasks = get_assigned_tasks()
    if not tasks:
        print("✗ No tasks assigned")
        return 1

    # Verify task details
    if not verify_task_spec(tasks, task_id):
        print("✗ Task spec validation failed")
        return 1

    print("\n" + "=" * 60)
    print("✅ All verification tests PASSED")
    print("=" * 60)
    print("\nPhase 3.1 Task Assignment Mechanism is working correctly!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n✗ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
