"""Round-trip MCP platform-conformance test (T422, Phase 2 acceptance gate).

Every other MCP test in this suite reads *already-generated, already-committed*
output (`test_platform_projections.py`'s `test_platform_mcp_configs_have_expected_shape`
and `test_remote_mcp_transport_shape_for_previously_uncovered_platforms`,
`test_mcp_schema_validation.py`, `test_sync_determinism.py`'s idempotency check). None
of them ever mutate `servers.yaml` and re-run the generator — they can prove the
*current* committed state matches its own generated output, but they cannot prove the
generator itself actually propagates a registry change to all 7 platforms, or that a
platform silently dropping a server would be caught. That is the specific gap plan-035
Phase 2's acceptance criteria describe and this file closes, via two live round trips
against a temporary copy of `implementation/` (never the real `servers.yaml`):

1. Add a `core` server to a *copied* `servers.yaml`, run `node scripts/sync.mjs` for
   real, and assert the new server is present in all 7 generated platform outputs.
2. Delete a `core` server's entry from one platform's *generated* output file (simulating
   a regression) and assert the very same presence-checking helper used in (1) now
   raises — proving the assertion is load-bearing, not vacuous.

Acceptance criterion 3 (`test_mcp_secret_guard.py` still passes after this change) is a
repo-wide regression check, not new test content to add here — it was run explicitly
(`python3 tests/run.py` plus a scoped `unittest` invocation of that module) and the
transcript is cited in this task's completion report rather than re-encoded as a test in
this file, to avoid duplicating that module's own coverage.

Isolation mechanism: this reuses `test_sync_determinism.py`'s proven pattern — deep-copy
the whole `implementation/` tree into a `tempfile.TemporaryDirectory()` and invoke
`node scripts/sync.mjs` with `cwd` set to the copy. `sync.mjs`'s `ROOT` defaults to
`path.resolve(__dirname, '..')` (the script's own directory's parent), so running the
copied `scripts/sync.mjs` in place automatically confines every read and write —
`knowledge/`, `platforms/`, `_extras/`, and all 7 generated output paths — to the
temporary copy, with no `--root`/`--knowledge`/`--platforms` flags required. The task
brief anticipated explicit use of those flags, but `test_sync_determinism.py` (checked
first, per the brief's own instruction) establishes copy+cwd as the actual pattern
already in use in this suite; that pattern is reused here rather than inventing a
second, parallel isolation mechanism. The real repo's `servers.yaml` and generated
platform directories are never touched by this file.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root

# A server name guaranteed not to collide with any of the 15 real entries in
# implementation/knowledge/mcp/servers.yaml (7 core + 8 extended, per
# docs/artifacts/mcp-platform-contract-v1.md §2).
NEW_SERVER_NAME = "qa-conformance-probe"
NEW_SERVER_YAML_BLOCK = (
    f"\n  {NEW_SERVER_NAME}:\n"
    "    tags: [core]\n"
    "    transport: stdio\n"
    "    command: npx\n"
    '    args: ["-y", "qa-conformance-probe-mcp"]\n'
)

# A server already present in every committed servers.yaml core entry, used for the
# delete-and-assert-failure round trip so it does not depend on test 1's own mutation.
EXISTING_CORE_SERVER = "gitlab"

# format -> function extracting the {serverName: {...}} mapping from a parsed
# generated MCP/settings JSON document. Mirrors emitMcp()'s per-format wrapper key,
# per docs/artifacts/mcp-platform-contract-v1.md §3.1.
_SERVER_MAP_BY_FORMAT = {
    "claude-code": lambda doc: doc.get("mcpServers", {}),
    "cline": lambda doc: doc.get("mcpServers", {}),
    "cursor": lambda doc: doc.get("mcpServers", {}),
    "gemini": lambda doc: doc.get("mcpServers", {}),
    "vscode": lambda doc: doc.get("servers", {}),
    "opencode": lambda doc: doc.get("mcp", {}),
}


def _require_node() -> None:
    if not shutil.which("node"):
        raise unittest.SkipTest("node not available on PATH")


def _copy_implementation_tree(dest_parent: Path) -> Path:
    """Deep-copy implementation/ into a temp dir; never mutates the real tree."""
    dest = dest_parent / "impl"
    shutil.copytree(implementation_root(), dest, symlinks=False)
    return dest


def _append_core_server(impl_root: Path, block: str) -> None:
    servers_yaml = impl_root / "knowledge" / "mcp" / "servers.yaml"
    original = servers_yaml.read_text(encoding="utf-8")
    if not original.endswith("\n"):
        original += "\n"
    servers_yaml.write_text(original + block, encoding="utf-8")


def _run_sync(impl_root: Path) -> None:
    """Run the real generator (write mode, not --check) inside the temp copy."""
    proc = subprocess.run(
        ["node", "scripts/sync.mjs"],
        cwd=impl_root, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"node scripts/sync.mjs failed (exit {proc.returncode}):\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def _platform_manifests(impl_root: Path) -> list[dict]:
    manifests = []
    for path in sorted((impl_root / "platforms").glob("*.json")):
        if path.name.startswith("_"):
            continue
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    return manifests


def _mcp_output_path(impl_root: Path, manifest: dict) -> Path:
    out_root = impl_root / manifest["outputDir"]
    # manifest["mcp"]["outputFile"] may contain "../" segments (e.g. claude-code,
    # github) — resolve them exactly as sync.mjs's path.resolve(outRoot, outputFile)
    # does, lexically (os.path.normpath), without following symlinks (Path.resolve()
    # would also resolve symlinks, which is not what we want to compare against).
    combined = out_root / manifest["mcp"]["outputFile"]
    return Path(os.path.normpath(str(combined)))


def _assert_core_server_present_everywhere(impl_root: Path, server_name: str) -> None:
    """Re-run the same presence check test 1 relies on; used by test 2 to prove the
    check is load-bearing (raises AssertionError on a real, injected regression)."""
    manifests = _platform_manifests(impl_root)
    if len(manifests) != 7:
        raise AssertionError(f"expected 7 platform manifests, found {len(manifests)}")

    missing_from: list[str] = []
    for manifest in manifests:
        mcp = manifest.get("mcp")
        if not mcp or "core" not in mcp.get("tags", []):
            # Per docs/artifacts/mcp-platform-contract-v1.md §3, all 7 manifests'
            # mcp.tags include "core" — this branch should never trigger for the
            # real 7 manifests, but guards the helper against a future manifest
            # that legitimately excludes core servers.
            continue
        doc_path = _mcp_output_path(impl_root, manifest)
        if not doc_path.is_file():
            missing_from.append(f"{manifest['platform']} (no generated file at {doc_path})")
            continue
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        extractor = _SERVER_MAP_BY_FORMAT[manifest["mcp"]["format"]]
        servers = extractor(doc)
        if server_name not in servers:
            missing_from.append(manifest["platform"])

    if missing_from:
        raise AssertionError(
            f"core server {server_name!r} missing from: {', '.join(sorted(missing_from))}"
        )


class TestMcpPlatformConformance(unittest.TestCase):
    """Plan-035 Phase 2 acceptance criteria 1 and 2: live add/delete round trips."""

    def setUp(self):
        _require_node()

    def test_adding_core_server_and_syncing_propagates_to_all_seven_platforms(self):
        """Acceptance criterion 1: add-and-sync-and-assert round trip, not a static read."""
        with tempfile.TemporaryDirectory() as tmp:
            impl_root = _copy_implementation_tree(Path(tmp))

            # Sanity: the new server name must not already exist anywhere, so a false
            # positive can't hide a broken sync step.
            manifests_before = _platform_manifests(impl_root)
            self.assertEqual(len(manifests_before), 7)
            for manifest in manifests_before:
                doc_path = _mcp_output_path(impl_root, manifest)
                if doc_path.is_file():
                    doc = json.loads(doc_path.read_text(encoding="utf-8"))
                    extractor = _SERVER_MAP_BY_FORMAT[manifest["mcp"]["format"]]
                    self.assertNotIn(NEW_SERVER_NAME, extractor(doc))

            _append_core_server(impl_root, NEW_SERVER_YAML_BLOCK)
            _run_sync(impl_root)

            manifests = _platform_manifests(impl_root)
            self.assertEqual(len(manifests), 7, "expected exactly 7 platform manifests")

            missing: list[str] = []
            for manifest in manifests:
                doc_path = _mcp_output_path(impl_root, manifest)
                self.assertTrue(
                    doc_path.is_file(),
                    f"{manifest['platform']}: no generated MCP file at {doc_path} after sync",
                )
                doc = json.loads(doc_path.read_text(encoding="utf-8"))
                extractor = _SERVER_MAP_BY_FORMAT[manifest["mcp"]["format"]]
                servers = extractor(doc)
                with self.subTest(platform=manifest["platform"]):
                    self.assertIn(
                        NEW_SERVER_NAME, servers,
                        f"{manifest['platform']}: new core server not propagated by sync",
                    )
                    # Shape sanity (stdio server, no env block) — not a full per-format
                    # shape audit, which test_platform_projections.py already owns.
                    entry = servers[NEW_SERVER_NAME]
                    if manifest["mcp"]["format"] == "opencode":
                        self.assertEqual(entry.get("command"), ["npx", "-y", "qa-conformance-probe-mcp"])
                    else:
                        self.assertEqual(entry.get("command"), "npx")
                    # A pre-existing core server must still be present too — the sync
                    # step must add, not replace.
                    self.assertIn(EXISTING_CORE_SERVER, servers)
                if NEW_SERVER_NAME not in servers:
                    missing.append(manifest["platform"])

            self.assertFalse(missing, f"platforms missing new core server: {missing}")

    def test_deleting_server_from_one_platform_projection_fails_the_conformance_check(self):
        """Acceptance criterion 2: delete-and-assert-failure round trip.

        Proves `_assert_core_server_present_everywhere` (the same helper criterion 1's
        test relies on for its presence assertions) is load-bearing: it passes on an
        untouched sync, then genuinely raises once a real regression — one platform's
        projection silently losing a core server — is injected.
        """
        with tempfile.TemporaryDirectory() as tmp:
            impl_root = _copy_implementation_tree(Path(tmp))
            _run_sync(impl_root)

            # Baseline: must not raise before any mutation.
            _assert_core_server_present_everywhere(impl_root, EXISTING_CORE_SERVER)

            cursor_manifest = next(
                m for m in _platform_manifests(impl_root) if m["platform"] == "cursor"
            )
            doc_path = _mcp_output_path(impl_root, cursor_manifest)
            doc = json.loads(doc_path.read_text(encoding="utf-8"))
            self.assertIn(
                EXISTING_CORE_SERVER, doc["mcpServers"],
                "precondition failed: gitlab not present in cursor's generated output",
            )
            del doc["mcpServers"][EXISTING_CORE_SERVER]
            doc_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

            with self.assertRaises(AssertionError) as ctx:
                _assert_core_server_present_everywhere(impl_root, EXISTING_CORE_SERVER)
            self.assertIn("cursor", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
