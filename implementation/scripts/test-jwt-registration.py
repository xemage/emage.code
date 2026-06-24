#!/usr/bin/env python3
"""Diagnostic script to test JWT generation and registration with CWSO."""

import json
import base64
import hashlib
import hmac
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

def generate_jwt_token(jwt_secret: str, role: str = "worker", sub: str = "sia-executor-1") -> str:
    """Generate HS256 JWT token (stdlib implementation)."""
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
        "sub": sub,
    }

    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")

    message = f"{header_b64}.{payload_b64}".encode()
    signature = base64.urlsafe_b64encode(
        hmac.new(
            jwt_secret.encode(),
            message,
            hashlib.sha256,
        ).digest()
    ).decode().rstrip("=")

    token = f"{header_b64}.{payload_b64}.{signature}"
    return token

def test_jwt_format(token: str):
    """Decode and display JWT token structure."""
    parts = token.split(".")
    if len(parts) != 3:
        print("ERROR: Invalid JWT format (not 3 parts)")
        return

    for i, part in enumerate(parts):
        # Add padding if needed
        padding = 4 - (len(part) % 4)
        part_padded = part + "=" * padding

        try:
            if i == 0:
                print("Header:", json.loads(base64.urlsafe_b64decode(part_padded)))
            elif i == 1:
                print("Payload:", json.loads(base64.urlsafe_b64decode(part_padded)))
            else:
                print("Signature (hex):", base64.urlsafe_b64decode(part_padded).hex())
        except Exception as e:
            print(f"ERROR decoding part {i}: {e}")

def test_registration(cwso_url: str, jwt_token: str):
    """Test node registration with CWSO."""
    url = f"{cwso_url}/nodes/register"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    payload = {"node_id": "test-executor-1"}

    print(f"\n📋 Registration Request:")
    print(f"  URL: {url}")
    print(f"  Headers: {headers}")
    print(f"  Body: {payload}")

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
            print(f"\n✅ Registration succeeded!")
            print(f"  Response: {result}")
            return True
    except urllib.error.HTTPError as e:
        print(f"\n❌ Registration failed: HTTP {e.code} {e.reason}")
        try:
            error_body = json.loads(e.read().decode())
            print(f"  Error body: {error_body}")
        except:
            print(f"  Error body: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"\n❌ Registration error: {e}")
        return False

def main():
    jwt_secret = "ci-ephemeral-secret-not-used-in-prod-ci-only"
    cwso_url = "http://localhost:8080"

    print("=== CWSO JWT Registration Test ===\n")

    # Generate token
    print("🔐 Generating JWT token...")
    token = generate_jwt_token(jwt_secret, role="worker", sub="sia-executor-1")
    print(f"Token: {token[:50]}...")

    # Decode token structure
    print("\n🔍 JWT Structure:")
    test_jwt_format(token)

    # Test registration
    print("\n📤 Testing node registration...")
    success = test_registration(cwso_url, token)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
