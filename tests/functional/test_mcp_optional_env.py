"""T680 (SEC-T665-09) -- the `optional` key of a templated `env` value, generator side.

Moved from the T680 test file by ADR-013 D4 (T771): the classes of the removed platform were deleted; `optional`
stays because the claude-code format reads it. This file pins:

- `sync.mjs` accepts `optional: true` on an `env` value (a boolean; the default absent or ""; never on a `url`
  or a `headers` value) and refuses a misspelled key or a bad value before anything is written;
- claude-code renders an optional variable as `${VAR:-}`, and the four other formats render exactly what they
  rendered before.

Local `node` runs on temporary directories; no network, no token.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root

IMPL = implementation_root()
SYNC = IMPL / "scripts" / "sync.mjs"

FILES = {
    "claude-code": ".mcp.json",
    "vscode": ".vscode/mcp.json",
    "opencode": ".opencode/opencode.json",
    "cline": ".cline/mcp.json",
}
UNCHANGED = ("vscode", "opencode", "cline")


def _scratch_root(servers_text: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="t680-sync-"))
    (tmp / "platforms").mkdir()
    for path in (IMPL / "platforms").glob("*.json"):
        shutil.copy(path, tmp / "platforms" / path.name)
    shutil.copytree(IMPL / "_extras", tmp / "_extras")
    for kind in ("mcp", "agents", "commands", "instructions", "skills"):
        (tmp / "knowledge" / kind).mkdir(parents=True)
    (tmp / "knowledge" / "mcp" / "servers.yaml").write_text(servers_text, encoding="utf-8")
    return tmp


STDIO = (
    "servers:\n  probe:\n    tags: [core]\n    transport: stdio\n    command: npx\n"
    "    args: [\"-y\", \"x@1.0.0\"]\n    env:\n{env}"
)
REMOTE = (
    "servers:\n  probe:\n    tags: [core]\n    transport: remote\n    url: { fromEnv: URLVAR }\n"
    "    headers:\n@@HEADERS@@"
)


class _SyncCase(unittest.TestCase):
    def run_sync(self, servers_text: str) -> tuple[Path, subprocess.CompletedProcess]:
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        root = _scratch_root(servers_text)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        proc = subprocess.run(["node", str(SYNC), "--root", str(root)], capture_output=True, text=True, check=False)
        return root, proc

    def generated(self, root: Path, platform: str) -> dict:
        data = json.loads((root / FILES[platform]).read_text(encoding="utf-8"))
        for wrapper in ("mcpServers", "servers", "mcp"):
            if wrapper in data:
                return data[wrapper]["probe"]
        raise AssertionError(platform)


class OptionalRenderingTests(_SyncCase):
    ENV = (
        "      A: { fromEnv: AAA, optional: true }\n"
        "      B: { fromEnv: BBB, secret: true, default: \"\", optional: true }\n"
        "      C: { fromEnv: CCC }\n"
        "      D: { fromEnv: DDD, default: \"fallback\" }\n"
        "      E: literal\n"
    )

    def test_each_format_renders_an_optional_value_in_its_own_way(self):
        root, proc = self.run_sync(STDIO.format(env=self.ENV))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.generated(root, "claude-code")["env"],
                         {"A": "${AAA:-}", "B": "${BBB:-}", "C": "${CCC}", "D": "${DDD:-fallback}", "E": "literal"})

    def test_the_other_four_formats_are_unaffected_by_optional(self):
        plain = self.ENV.replace(", optional: true", "")
        with_optional, p1 = self.run_sync(STDIO.format(env=self.ENV))
        without, p2 = self.run_sync(STDIO.format(env=plain))
        self.assertEqual((p1.returncode, p2.returncode), (0, 0))
        for platform in UNCHANGED:
            with self.subTest(platform=platform):
                self.assertEqual((with_optional / FILES[platform]).read_bytes(), (without / FILES[platform]).read_bytes())

    def test_regeneration_is_deterministic(self):
        first, _ = self.run_sync(STDIO.format(env=self.ENV))
        second, _ = self.run_sync(STDIO.format(env=self.ENV))
        for rel in FILES.values():
            self.assertEqual((first / rel).read_bytes(), (second / rel).read_bytes(), rel)


class OptionalValidationTests(_SyncCase):
    def test_bad_optional_specs_stop_the_run_before_anything_is_written(self):
        bad = {
            "string instead of a boolean": STDIO.format(env="      A: { fromEnv: AAA, optional: yes }\n"),
            "number instead of a boolean": STDIO.format(env="      A: { fromEnv: AAA, optional: 1 }\n"),
            "misspelled key": STDIO.format(env="      A: { fromEnv: AAA, optionl: true }\n"),
            "optional with a non-empty default": STDIO.format(env="      A: { fromEnv: AAA, optional: true, default: \"x\" }\n"),
            "optional url": REMOTE.replace("{ fromEnv: URLVAR }", "{ fromEnv: URLVAR, optional: true }").replace(
                "@@HEADERS@@", "      X: fixed\n"),
            # SEC-T680-02: only an env value may be left unset
            "optional header": REMOTE.replace("@@HEADERS@@", "      Origin: { fromEnv: ORG, optional: true }\n"),
            "optional secret header": REMOTE.replace(
                "@@HEADERS@@", "      Authorization: { fromEnv: TOK, secret: true, wrap: \"Bearer {VAR}\", optional: true }\n"),
        }
        for label, text in bad.items():
            with self.subTest(case=label):
                root, proc = self.run_sync(text)
                self.assertNotEqual(proc.returncode, 0, label)
                self.assertIn("servers.yaml", proc.stderr)
                for folder in (".mcp.json", ".vscode", ".opencode", ".cline"):
                    self.assertFalse((root / folder).exists(), f"{label}: {folder} was written")

    def test_optional_false_is_accepted_and_changes_nothing(self):
        root, proc = self.run_sync(STDIO.format(env="      A: { fromEnv: AAA, optional: false }\n"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.generated(root, "claude-code")["env"], {"A": "${AAA}"})


if __name__ == "__main__":
    unittest.main()
