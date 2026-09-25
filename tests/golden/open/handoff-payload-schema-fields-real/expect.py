#!/usr/bin/env python3
"""expect.py for handoff-payload-schema-fields-real.

Contract under test: implementation/knowledge/commands/handoff.md `## Instructions` step 3
("Draft handoff payload conforming to implementation/runtime/handoff/schema-v1.json" + the
fromAgent/toAgent/taskId/intent/payload/constraints/trace field list), step 4 ("Write
artifacts: JSON docs/checkpoints/handoff-<handoffId>.json, Human summary
docs/checkpoints/handoff-<handoffId>.md"), and `## Security` ("Never include secrets, tokens,
or .env contents in handoff payloads").

The schema is shipped in the fixture and the structural checks are read out of it, rather than
restated here -- step 3's own bullet list is a strict subset of the schema's `required` set.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Mirrors implementation/runtime/handoff/validator.py's SECRET_KEY_RE exactly.
SECRET_KEY_RE = re.compile(r"(token|password|api[_-]?key|authorization|secret)", re.IGNORECASE)
# The field list step 3 spells out by name, checked in addition to the schema's `required`.
STEP3_TOP_FIELDS = ("fromAgent", "toAgent", "taskId", "intent", "payload", "constraints", "trace")
STEP3_CONSTRAINT_FIELDS = ("writablePaths", "forbiddenActions", "maxToolCalls", "deadlineUtc")
STEP3_TRACE_FIELDS = ("checkpointRef", "correlationId")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _contains_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            SECRET_KEY_RE.search(str(k)) or _contains_secret_key(v) for k, v in value.items()
        )
    if isinstance(value, list):
        return any(_contains_secret_key(item) for item in value)
    return False


def _object_matches_schema(obj: Any, node: dict[str, Any]) -> bool:
    """Check `obj` against the subset of JSON-Schema this case relies on: `required`,
    `additionalProperties: false`, `enum`, `pattern`, and nested object `properties`."""
    if not isinstance(obj, dict):
        return False
    props: dict[str, Any] = node.get("properties", {})
    if any(key not in obj for key in node.get("required", [])):
        return False
    if node.get("additionalProperties") is False and any(k not in props for k in obj):
        return False
    for key, subschema in props.items():
        if key not in obj:
            continue
        value = obj[key]
        enum = subschema.get("enum")
        if enum is not None and value not in enum:
            return False
        pattern = subschema.get("pattern")
        if pattern is not None and not (
            isinstance(value, str) and re.match(pattern, value)
        ):
            return False
        if subschema.get("type") == "object" and "properties" in subschema:
            if not _object_matches_schema(value, subschema):
                return False
    return True


def _check_declared_fields(payload: dict[str, Any]) -> bool:
    if any(f not in payload for f in STEP3_TOP_FIELDS):
        return False
    constraints, trace = payload.get("constraints"), payload.get("trace")
    if not isinstance(constraints, dict) or not isinstance(trace, dict):
        return False
    if any(f not in constraints for f in STEP3_CONSTRAINT_FIELDS):
        return False
    return all(f in trace for f in STEP3_TRACE_FIELDS)


def check(case_dir: Path) -> bool:
    fixture = case_dir / "fixture"
    checkpoints = fixture / "docs" / "checkpoints"
    schema_path = fixture / "implementation" / "runtime" / "handoff" / "schema-v1.json"
    if not checkpoints.is_dir():
        return False

    json_files = sorted(checkpoints.glob("handoff-*.json"))
    if len(json_files) != 1:
        return False
    json_path = json_files[0]

    payload = _load_json(json_path)
    schema = _load_json(schema_path)
    if not isinstance(payload, dict) or not isinstance(schema, dict):
        return False

    # Step 4: the <handoffId> in the filename is the payload's own handoffId, and the
    # human-summary sibling exists.
    handoff_id = json_path.stem[len("handoff-"):]
    if payload.get("handoffId") != handoff_id:
        return False
    md_path = checkpoints / f"handoff-{handoff_id}.md"
    if not md_path.is_file() or not md_path.read_text(encoding="utf-8").strip():
        return False

    if not _check_declared_fields(payload):
        return False
    if not _object_matches_schema(payload, schema):
        return False
    # Security: never include secrets, tokens, or .env contents in handoff payloads.
    return not _contains_secret_key(payload.get("payload"))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <case_dir>", file=sys.stderr)
        return 2
    return 0 if check(Path(sys.argv[1]).resolve()) else 1


if __name__ == "__main__":
    sys.exit(main())
