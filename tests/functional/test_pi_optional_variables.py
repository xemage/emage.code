"""T680 (SEC-T665-09) -- `optional` variables and the Pi placeholder form.

Based on docs/wiki/mcp-servers.md "Pi: verified forms" (observed on Pi 0.99.0, 1.0.0, 1.3.0 and 1.4.0:
`${VAR}` expands, `${env:VAR}` stays literal text, an unset or empty variable fails the server, a `url` is
never expanded, a stdio server inherits Pi's environment). This file pins the generator side:

- `sync.mjs` accepts `optional: true` on an `env` or `headers` value (a boolean; the default absent or "";
  never on a `url`) and refuses a misspelled key or a bad value before anything is written;
- claude-code renders an optional variable as `${VAR:-}`, Pi leaves it out of `env` / `headers` and renders
  every other value as `${VAR}`, and the four other formats render exactly what they rendered before;
- `optional` is refused on `headers` (SEC-T680-02: Pi would never send the header) and on `url`;
- `skipFormats: [pi]` leaves `hindsight` and `cwso` (templated url, rejected by Pi) out of the Pi config and
  its provenance sidecar only (SEC-T680-03);
- `scripts/merge-mcp-json.py --drop-env-form` (which install.sh passes for `.pi/mcp.json` only) migrates a
  Pi config that holds the old `${env:VAR}` entries without touching the user's own keys, prunes the retired
  Pi servers, and prints names, never values (SEC-T680-05, -06).

Local `node` and `python3` runs on temporary directories; no network, no token, no Pi.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, repo_root
from tests.functional.test_install_projections_only import run_installer

REPO = repo_root()
IMPL = implementation_root()
SYNC = IMPL / "scripts" / "sync.mjs"
MERGER = REPO / "scripts" / "merge-mcp-json.py"
INSTALL = REPO / "scripts" / "install.sh"

FILES = {
    "claude-code": ".mcp.json",
    "vscode": ".vscode/mcp.json",
    "gemini": ".gemini/settings.json",
    "opencode": ".opencode/opencode.json",
    "pi": ".pi/mcp.json",
    "cline": ".cline/mcp.json",
}
UNCHANGED = ("vscode", "gemini", "opencode", "cline")


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
        # Pi: the optional ones are left out; a default alone does NOT make a value optional on Pi
        self.assertEqual(self.generated(root, "pi")["env"], {"C": "${CCC}", "D": "${DDD}", "E": "literal"})

    def test_the_other_four_formats_are_unaffected_by_optional(self):
        plain = self.ENV.replace(", optional: true", "")
        with_optional, p1 = self.run_sync(STDIO.format(env=self.ENV))
        without, p2 = self.run_sync(STDIO.format(env=plain))
        self.assertEqual((p1.returncode, p2.returncode), (0, 0))
        for platform in UNCHANGED:
            with self.subTest(platform=platform):
                self.assertEqual((with_optional / FILES[platform]).read_bytes(), (without / FILES[platform]).read_bytes())

    def test_pi_renders_env_form_nowhere_and_drops_an_empty_env_block(self):
        env = "      A: { fromEnv: AAA, optional: true }\n"
        root, proc = self.run_sync(STDIO.format(env=env))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.generated(root, "pi"), {"command": "npx", "args": ["-y", "x@1.0.0"]})
        self.assertEqual(self.generated(root, "vscode")["env"], {"A": "${env:AAA}"})

    def test_pi_headers_wrap_and_url_render_as_dollar_brace(self):
        headers = (
            "      Authorization: { fromEnv: TOK, secret: true, wrap: \"Bearer {VAR}\" }\n"
            "      Origin: { fromEnv: ORG, default: \"\" }\n"
            "      X-Fixed: fixed\n"
        )
        root, proc = self.run_sync(REMOTE.replace("@@HEADERS@@", headers))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.generated(root, "pi"),
                         {"url": "${URLVAR}", "headers": {"Authorization": "Bearer ${TOK}", "Origin": "${ORG}",
                                                           "X-Fixed": "fixed"}})
        self.assertEqual(self.generated(root, "claude-code")["headers"]["Origin"], "${ORG:-}")
        self.assertEqual(self.generated(root, "vscode")["headers"]["Origin"], "${env:ORG}")

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
            # SEC-T680-02: an optional header would never be sent on Pi
            "optional header": REMOTE.replace("@@HEADERS@@", "      Origin: { fromEnv: ORG, optional: true }\n"),
            "optional secret header": REMOTE.replace(
                "@@HEADERS@@", "      Authorization: { fromEnv: TOK, secret: true, wrap: \"Bearer {VAR}\", optional: true }\n"),
        }
        for label, text in bad.items():
            with self.subTest(case=label):
                root, proc = self.run_sync(text)
                self.assertNotEqual(proc.returncode, 0, label)
                self.assertIn("servers.yaml", proc.stderr)
                for folder in (".mcp.json", ".vscode", ".gemini", ".opencode", ".pi", ".cline"):
                    self.assertFalse((root / folder).exists(), f"{label}: {folder} was written")

    def test_optional_false_is_accepted_and_changes_nothing(self):
        root, proc = self.run_sync(STDIO.format(env="      A: { fromEnv: AAA, optional: false }\n"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.generated(root, "pi")["env"], {"A": "${AAA}"})
        self.assertEqual(self.generated(root, "claude-code")["env"], {"A": "${AAA}"})


class ShippedPiOutputTests(unittest.TestCase):
    def setUp(self):
        self.text = (IMPL / ".pi" / "mcp.json").read_text(encoding="utf-8")
        self.servers = json.loads(self.text)["mcpServers"]

    def test_the_pi_file_holds_only_the_verified_form(self):
        self.assertNotIn("${env:", self.text)
        self.assertNotIn(":-", self.text)
        for placeholder in re.findall(r"\$\{[^}]*\}", self.text):
            self.assertRegex(placeholder, r"^\$\{[A-Z][A-Z0-9_]*\}$")

    def test_the_gitlab_entry_leaves_the_two_optional_variables_out(self):
        env = self.servers["gitlab"]["env"]
        self.assertEqual(env, {"GITLAB_API_URL": "${GITLAB_API_URL}", "GITLAB_PERMISSION_MODE": "modify"})

    def test_required_secrets_keep_a_placeholder(self):
        self.assertEqual(self.servers["brave"]["env"], {"BRAVE_API_KEY": "${BRAVE_API_KEY}"})

    def test_no_url_placeholder_and_no_templated_url_server_in_the_pi_file(self):
        # SEC-T680-03: Pi 1.x never expands a url and rejects a templated one (observed), so such servers are skipped
        for name, server in self.servers.items():
            self.assertNotIn("$", server.get("url", ""), name)
        self.assertNotIn("hindsight", self.servers)
        self.assertNotIn("cwso", self.servers)
        sidecar = json.loads((IMPL / ".pi" / "mcp.json.provenance.json").read_text(encoding="utf-8"))
        self.assertNotIn("hindsight", sidecar["generatorOwnedKeys"])
        self.assertNotIn("cwso", sidecar["generatorOwnedKeys"])
        self.assertIn("context7", sidecar["generatorOwnedKeys"])

    def test_the_other_platforms_still_hold_hindsight_and_cwso(self):
        for rel, wrapper in ((".mcp.json", "mcpServers"), (".vscode/mcp.json", "servers"),
                             (".gemini/settings.json", "mcpServers"), (".opencode/opencode.json", "mcp"),
                             (".cline/mcp.json", "mcpServers")):
            with self.subTest(file=rel):
                servers = json.loads((IMPL / rel).read_text(encoding="utf-8"))[wrapper]
                self.assertIn("hindsight", servers)
                if rel != ".vscode/mcp.json":   # cwso is an `extended` server; the github platform does not opt in
                    self.assertIn("cwso", servers)
        for rel in (".mcp.json.provenance.json", ".cline/mcp.json.provenance.json"):
            keys = json.loads((IMPL / rel).read_text(encoding="utf-8"))["generatorOwnedKeys"]
            self.assertIn("hindsight", keys)


class SkipFormatsTests(_SyncCase):
    SERVERS = (
        "servers:\n"
        "  keep:\n    tags: [core]\n    transport: stdio\n    command: npx\n    args: [\"-y\", \"x@1.0.0\"]\n"
        "  gone:\n    tags: [core]\n    skipFormats: SKIP\n    transport: remote\n    url: { fromEnv: URLVAR }\n"
    )

    def sidecar(self, root: Path, rel: str) -> list:
        return json.loads((root / (rel + ".provenance.json")).read_text(encoding="utf-8"))["generatorOwnedKeys"]

    def test_a_skipped_server_is_left_out_of_that_format_and_its_sidecar_only(self):
        root, proc = self.run_sync(self.SERVERS.replace("SKIP", "[pi]"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(list(json.loads((root / ".pi/mcp.json").read_text(encoding="utf-8"))["mcpServers"]), ["keep"])
        self.assertEqual(self.sidecar(root, ".pi/mcp.json"), ["keep"])
        for platform, rel in FILES.items():
            if platform == "pi":
                continue
            with self.subTest(platform=platform):
                text = (root / rel).read_text(encoding="utf-8")
                self.assertIn('"gone"', text)

    def test_other_formats_are_byte_identical_with_and_without_the_key(self):
        with_key, p1 = self.run_sync(self.SERVERS.replace("SKIP", "[pi]"))
        without, p2 = self.run_sync(self.SERVERS.replace("    skipFormats: SKIP\n", ""))
        self.assertEqual((p1.returncode, p2.returncode), (0, 0))
        for platform in ("claude-code",) + UNCHANGED:
            with self.subTest(platform=platform):
                self.assertEqual((with_key / FILES[platform]).read_bytes(), (without / FILES[platform]).read_bytes())

    def test_a_misspelled_or_unknown_skip_value_stops_the_run(self):
        for label, value in {"unknown format": "[pii]", "a string": "pi", "empty list": "[]",
                             "duplicate": "[pi, pi]", "number": "[1]"}.items():
            with self.subTest(case=label):
                root, proc = self.run_sync(self.SERVERS.replace("SKIP", value))
                self.assertNotEqual(proc.returncode, 0, label)
                self.assertIn("skipFormats", proc.stderr)
                self.assertFalse((root / ".pi").exists())

    def test_a_misspelled_key_is_an_unknown_key(self):
        _, proc = self.run_sync(self.SERVERS.replace("skipFormats", "skipFormat").replace("SKIP", "[pi]"))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unknown key", proc.stderr)


def _merge(source: Path, dest: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(MERGER), "--source", str(source), "--dest", str(dest), *flags],
                          capture_output=True, text=True, check=False)


class PiMigrationTests(unittest.TestCase):
    OLD_GITLAB = {
        "command": "npx",
        "args": ["-y", "@zereight/mcp-gitlab@2.2.5"],
        "env": {
            "GITLAB_PERSONAL_ACCESS_TOKEN": "${env:GITLAB_PERSONAL_ACCESS_TOKEN}",
            "GITLAB_PERSONAL_ACCESS_TOKEN_FILE": "${env:GITLAB_PERSONAL_ACCESS_TOKEN_FILE}",
            "GITLAB_API_URL": "${env:GITLAB_API_URL}",
            "GITLAB_PERMISSION_MODE": "modify",
        },
    }

    def merged(self, dest_data: dict, *flags: str) -> tuple[dict, subprocess.CompletedProcess]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dest = Path(tmp.name) / "mcp.json"
        dest.write_text(json.dumps(dest_data, indent=2) + "\n", encoding="utf-8")
        result = _merge(IMPL / ".pi" / "mcp.json", dest, *flags)
        self.assertEqual(result.returncode, 0, result.stderr)
        first = dest.read_bytes()
        again = _merge(IMPL / ".pi" / "mcp.json", dest, *flags)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(dest.read_bytes(), first, "a second merge changed the file (not idempotent)")
        return json.loads(first.decode("utf-8")), result

    def old_config(self) -> dict:
        return {"mcpServers": {"gitlab": json.loads(json.dumps(self.OLD_GITLAB)),
                               "brave": {"command": "npx", "args": ["-y", "x"],
                                         "env": {"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"}}}}

    def test_an_old_pi_config_is_migrated_to_the_new_form(self):
        merged, result = self.merged(self.old_config(), "--drop-env-form")
        self.assertEqual(merged["mcpServers"]["gitlab"]["env"],
                         {"GITLAB_API_URL": "${GITLAB_API_URL}", "GITLAB_PERMISSION_MODE": "modify"})
        self.assertEqual(merged["mcpServers"]["brave"]["env"], {"BRAVE_API_KEY": "${BRAVE_API_KEY}"})
        self.assertIn("dropped the retired `${env:` entry", result.stderr)
        self.assertIn("GITLAB_PERSONAL_ACCESS_TOKEN_FILE", result.stderr)
        self.assertIn("restore by hand", result.stderr)   # SEC-T680-05
        self.assertNotIn("${env:", json.dumps(merged))
        # a key the generator still ships is replaced, not "dropped"
        self.assertNotIn("GITLAB_API_URL", result.stderr)
        self.assertNotIn("BRAVE_API_KEY", result.stderr)

    def test_without_the_flag_the_stale_entries_survive(self):
        # the flag is what migrates; other platforms (Cline, VS Code) never get it
        merged, _ = self.merged(self.old_config())
        self.assertEqual(merged["mcpServers"]["gitlab"]["env"]["GITLAB_PERSONAL_ACCESS_TOKEN"],
                         "${env:GITLAB_PERSONAL_ACCESS_TOKEN}")

    def test_the_users_own_keys_and_servers_survive(self):
        data = self.old_config()
        data["mcpServers"]["gitlab"]["env"]["GITLAB_TOOLS"] = "list_issues"
        data["mcpServers"]["gitlab"]["env"]["MY_PASS_THROUGH"] = "${MY_PASS_THROUGH}"
        data["mcpServers"]["mine"] = {"command": "x", "env": {"K": "${env:K}"}}
        merged, _ = self.merged(data, "--drop-env-form")
        env = merged["mcpServers"]["gitlab"]["env"]
        self.assertEqual(env["GITLAB_TOOLS"], "list_issues")
        self.assertEqual(env["MY_PASS_THROUGH"], "${MY_PASS_THROUGH}")
        # a server the generated config does not list is the user's: untouched, even with the old form
        self.assertEqual(merged["mcpServers"]["mine"], {"command": "x", "env": {"K": "${env:K}"}})

    def test_an_already_current_file_is_left_byte_identical(self):
        current = (IMPL / ".pi" / "mcp.json").read_bytes()
        merged, result = self.merged(json.loads(current.decode("utf-8")), "--drop-env-form")
        self.assertEqual(json.dumps(merged, indent=2) + "\n", current.decode("utf-8"))
        self.assertNotIn("dropped", result.stderr)

    def merge_custom(self, source: dict, dest: dict, *flags: str) -> tuple[dict, subprocess.CompletedProcess]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        src, dst = Path(tmp.name) / "src.json", Path(tmp.name) / "mcp.json"
        src.write_text(json.dumps(source), encoding="utf-8")
        dst.write_text(json.dumps(dest), encoding="utf-8")
        result = _merge(src, dst, *flags)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return json.loads(dst.read_text(encoding="utf-8")), result

    def test_a_dropped_headers_entry_is_named_and_the_users_header_is_kept(self):
        source = {"mcpServers": {"srv": {"url": "https://x.invalid/mcp", "headers": {"Authorization": "Bearer ${TOK}"}}}}
        dest = {"mcpServers": {"srv": {"url": "https://x.invalid/mcp", "headers": {
            "Authorization": "Bearer ${env:TOK}", "X-Old": "${env:SENTINEL_HEADER_VALUE_QX}", "X-Mine": "mine"}}}}
        merged, result = self.merge_custom(source, dest, "--drop-env-form")
        self.assertEqual(merged["mcpServers"]["srv"]["headers"], {"Authorization": "Bearer ${TOK}", "X-Mine": "mine"})
        self.assertIn("mcpServers.srv.headers.X-Old", result.stderr)

    def test_the_dropped_note_names_keys_and_never_values(self):
        data = self.old_config()
        data["mcpServers"]["gitlab"]["env"]["GITLAB_PERSONAL_ACCESS_TOKEN"] = "${env:SENTINEL_VALUE_QWERTY}"
        _, result = self.merged_with_output(data)
        self.assertIn("GITLAB_PERSONAL_ACCESS_TOKEN", result.stderr)
        self.assertNotIn("SENTINEL_VALUE_QWERTY", result.stderr + result.stdout)

    def merged_with_output(self, dest_data: dict) -> tuple[dict, subprocess.CompletedProcess]:
        return self.merge_custom(json.loads((IMPL / ".pi" / "mcp.json").read_text(encoding="utf-8")), dest_data,
                                 "--drop-env-form")

    def test_hostile_structures_are_survived_and_kept(self):
        source = json.loads((IMPL / ".pi" / "mcp.json").read_text(encoding="utf-8"))
        cases = {
            "env is a list": {"mcpServers": {"gitlab": {"env": []}}},
            "headers is a string": {"mcpServers": {"gitlab": {"headers": "x"}}},
            "non-string values": {"mcpServers": {"brave": {"env": {"A": 1, "B": None, "C": {"x": "${env:Q}"},
                                                                    "D": ["${env:Q}"], "E": True}}}},
            "server is a list": {"mcpServers": {"gitlab": []}},
            "servers is a list": {"mcpServers": []},
            "server is a string": {"mcpServers": {"gitlab": "x"}},
        }
        for label, dest in cases.items():
            with self.subTest(case=label):
                merged, result = self.merge_custom(source, dest, "--drop-env-form")
                self.assertIsInstance(merged, dict)
                self.assertNotIn("dropped", result.stderr)
        merged, _ = self.merge_custom(source, {"mcpServers": {"brave": {"env": {"A": 1, "C": {"x": "${env:Q}"}}}}},
                                      "--drop-env-form")
        self.assertEqual(merged["mcpServers"]["brave"]["env"]["A"], 1)
        self.assertEqual(merged["mcpServers"]["brave"]["env"]["C"], {"x": "${env:Q}"})
        merged, _ = self.merge_custom(source, [], "--drop-env-form")
        self.assertEqual(merged, source)

    def test_retired_pi_servers_are_pruned_through_the_sidecar_and_the_users_are_not(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        source = IMPL / ".pi" / "mcp.json"
        dest = Path(tmp.name) / "mcp.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["mcpServers"]["hindsight"] = {"url": "${env:HINDSIGHT_MCP_URL}"}
        data["mcpServers"]["cwso"] = {"url": "${env:CWSO_MCP_URL}", "headers": {"Origin": "${env:CWSO_ORIGIN}"}}
        data["mcpServers"]["my-hindsight"] = {"url": "https://hindsight.invalid/mcp"}
        dest.write_text(json.dumps(data), encoding="utf-8")
        old_sidecar = Path(tmp.name) / "mcp.json.provenance.json"
        keys = json.loads((IMPL / ".pi" / "mcp.json.provenance.json").read_text(encoding="utf-8"))["generatorOwnedKeys"]
        old_sidecar.write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": sorted(keys + ["cwso", "hindsight"])}),
                               encoding="utf-8")
        result = _merge(source, dest, "--drop-env-form", "--old-sidecar", str(old_sidecar),
                        "--new-sidecar", str(IMPL / ".pi" / "mcp.json.provenance.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        servers = json.loads(dest.read_text(encoding="utf-8"))["mcpServers"]
        self.assertNotIn("hindsight", servers)
        self.assertNotIn("cwso", servers)
        self.assertEqual(servers["my-hindsight"], {"url": "https://hindsight.invalid/mcp"})
        self.assertIn("pruned the retired generator server cwso, hindsight", result.stderr)
        self.assertNotIn("invalid", result.stderr)
        self.assertEqual(json.loads(old_sidecar.read_text(encoding="utf-8")),
                         json.loads((IMPL / ".pi" / "mcp.json.provenance.json").read_text(encoding="utf-8")))

    def test_install_sh_migrates_an_old_pi_config_end_to_end(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        target = Path(tmp.name) / "project"
        first = run_installer(INSTALL, target, "--platform", "pi")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        config = target / ".pi" / "mcp.json"
        data = json.loads(config.read_text(encoding="utf-8"))
        data["mcpServers"]["gitlab"]["env"].update(self.OLD_GITLAB["env"])
        data["mcpServers"]["gitlab"]["env"]["GITLAB_TOOLS"] = "list_issues"
        config.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        second = run_installer(INSTALL, target, "--platform", "pi")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        env = json.loads(config.read_text(encoding="utf-8"))["mcpServers"]["gitlab"]["env"]
        self.assertEqual(env, {"GITLAB_API_URL": "${GITLAB_API_URL}", "GITLAB_PERMISSION_MODE": "modify",
                               "GITLAB_TOOLS": "list_issues"})
        self.assertIn("dropped the retired `${env:` entry", second.stderr)

    def test_install_passes_the_flag_for_pi_only(self):
        text = INSTALL.read_text(encoding="utf-8")
        calls = re.findall(r'^\s*merge_or_copy_mcp_json "[^"\n]+" "[^"\n]+"(.*)$', text, re.M)
        self.assertEqual(len(calls), 6)
        flagged = [line for line in text.splitlines() if "--drop-env-form" in line and "merge_or_copy_mcp_json" in line and ".pi/mcp.json" in line]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(sum("--drop-env-form" in c for c in calls), 1)


def _load_merger():
    spec = importlib.util.spec_from_file_location("merge_mcp_json_t680", MERGER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MERGER_MODULE = _load_merger()


class LiteralCredentialClassificationTests(unittest.TestCase):
    """SEC-T680-07, -08: what counts as a placeholder, and how the check is bounded."""

    def test_only_a_whole_single_reference_is_a_placeholder(self):
        placeholders = ["${A}", "$A", "{env:A}", "Bearer ${A}", "!pass show x", "", "${A_1}", "Basic $TOK"]
        for value in placeholders:
            with self.subTest(value=value):
                self.assertFalse(MERGER_MODULE.holds_literal_credential("MY_TOKEN", value))

    def test_bypass_attempts_are_literals(self):
        literals = ["${VAR:-glpat-FAKEFAKE}", "pa$word", "ab$cd", "$3cr3t-token", "$ecret-x9", "${A}${B}",
                    "${A} tail", "Bearer abc", "glpat-FAKE", "${A", "$", "${}", "{env:A}x",
                    "two words ${A}", "${A:-}", "$A$B"]
        for value in literals:
            with self.subTest(value=value):
                self.assertTrue(MERGER_MODULE.holds_literal_credential("MY_TOKEN", value))

    def test_the_credential_name_list(self):
        for name in ("MY_TOKEN", "api_key", "CLIENT_SECRET", "DB_PASSWORD", "DB_PASSWD", "Authorization", "X_AUTH",
                     "SESSION_COOKIE", "BEARER", "AWS_CREDENTIALS"):
            with self.subTest(name=name):
                self.assertTrue(MERGER_MODULE.holds_literal_credential(name, "abc-literal"))
        for name in ("GITLAB_TOOLS", "LOG_LEVEL", "HOME"):
            with self.subTest(name=name):
                self.assertFalse(MERGER_MODULE.holds_literal_credential(name, "abc-literal"))

    def test_a_long_value_is_a_literal_and_the_check_is_fast(self):
        self.assertTrue(MERGER_MODULE.holds_literal_credential("MY_TOKEN", "$" + "A" * 5000))
        for value in ("${" * 2_000_000, "$" * 4_000_000, "Bearer " * 600_000, "{env:" * 1_000_000 + "}"):
            started = time.monotonic()
            self.assertTrue(MERGER_MODULE.holds_literal_credential("MY_TOKEN", value))
            self.assertLess(time.monotonic() - started, 2.0)

    def test_a_multi_megabyte_value_through_the_whole_merge_is_fast(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        source, dest = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        source.write_text(json.dumps({"mcpServers": {"srv": {"env": {"A": "${A}"}}}}), encoding="utf-8")
        dest.write_text(json.dumps({"mcpServers": {"srv": {"env": {"MY_TOKEN": "${" * 2_000_000}}}}), encoding="utf-8")
        started = time.monotonic()
        result = _merge(source, dest)
        self.assertLess(time.monotonic() - started, 2.0)
        self.assertEqual(result.returncode, 0, result.stderr[:300])
        self.assertIn("WARNING", result.stderr)
        self.assertLess(len(result.stderr), 2000, "the value must not be echoed")


class LiteralPathTests(unittest.TestCase):
    def merge_env(self, extra: dict) -> subprocess.CompletedProcess:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        source, dest = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        source.write_text(json.dumps({"mcpServers": {"srv": {"env": {"A": "${A}"}}}}), encoding="utf-8")
        dest.write_text(json.dumps({"mcpServers": {"srv": {"env": {"A": "${A}", **extra}}}}), encoding="utf-8")
        result = _merge(source, dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_a_file_or_path_named_key_gets_the_non_alarming_note(self):
        for key in ("GITLAB_PERSONAL_ACCESS_TOKEN_FILE", "MY_TOKEN_PATH", "secret.file", "api-key-path"):
            with self.subTest(key=key):
                result = self.merge_env({key: "/home/user/.config/gitlab-mcp/token"})
                self.assertNotIn("WARNING", result.stderr)
                self.assertNotIn("revoke", result.stderr)
                self.assertIn(f"mcpServers.srv.env.{key} holds a literal path; fine, but it is read by the server "
                              f"only if the token variable is empty", result.stderr)
                self.assertNotIn(".config/gitlab-mcp", result.stderr)

    def test_other_names_still_warn(self):
        for key in ("MY_TOKEN_BACKUP", "MY_TOKENFILE", "FILE_TOKEN"):
            with self.subTest(key=key):
                result = self.merge_env({key: "abc-literal"})
                self.assertIn("WARNING", result.stderr)
                self.assertIn("revoke the token", result.stderr)


class TerminalSafeNamesTests(unittest.TestCase):
    """SEC-T680-05: every name sink goes through format_names -> printable (T682 N-1)."""

    EVIL = "x\x1b[31m\nforged: line\u202e"

    def run_merge(self, source: dict, dest: dict, *extra: str) -> subprocess.CompletedProcess:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        s, d = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        s.write_text(json.dumps(source), encoding="utf-8")
        d.write_text(json.dumps(dest), encoding="utf-8")
        self.sidecar_dir = Path(tmp.name)
        return subprocess.run([sys.executable, str(MERGER), "--source", str(s), "--dest", str(d), *extra],
                              capture_output=True, text=True, check=False)

    def assert_safe(self, err: str, escaped: str):
        self.assertIn(escaped, err)
        self.assertEqual([ch for ch in err if not (ch.isprintable() or ch == "\n")], [], repr(err))
        self.assertNotIn("\nforged: line", err)

    def test_dropped_literal_and_literal_path_notes(self):
        evil = self.EVIL
        source = {"mcpServers": {"srv": {"env": {"A": "${A}"}}}}
        dest = {"mcpServers": {"srv": {"env": {"A": "${A}", evil + "_TOKEN": "literal-x", evil + "_FILE": "/p",
                                               evil + "_OLD": "${env:OLD}"}}}}
        result = self.run_merge(source, dest, "--drop-env-form")
        self.assertEqual(result.returncode, 0, result.stderr)
        for suffix in ("_TOKEN", "_FILE", "_OLD"):
            self.assert_safe(result.stderr, ascii(f"mcpServers.srv.env.{evil}{suffix}"))

    def test_pruned_and_pruned_differs_notes(self):
        evil = self.EVIL
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "s.json").write_text(json.dumps({"mcpServers": {"keep": {}}}), encoding="utf-8")
        (root / "d.json").write_text(json.dumps({"mcpServers": {"keep": {}, evil: {"url": "https://x.invalid/mcp"}}}),
                                     encoding="utf-8")
        (root / "d.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep", evil]}), encoding="utf-8")
        (root / "s.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MERGER), "--source", str(root / "s.json"), "--dest", str(root / "d.json"),
                                 "--old-sidecar", str(root / "d.sc.json"), "--new-sidecar", str(root / "s.sc.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_safe(result.stderr, f"pruned the retired generator server {ascii(evil)}")
        self.assert_safe(result.stderr, f"{ascii(evil)} differs from the generated entry")

    def test_bootstrap_kept_note(self):
        evil = self.EVIL
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "s.json").write_text(json.dumps({"mcpServers": {"keep": {}}}), encoding="utf-8")
        (root / "d.json").write_text(json.dumps({"mcpServers": {"keep": {}, evil: {}}}), encoding="utf-8")
        (root / "s.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MERGER), "--source", str(root / "s.json"), "--dest", str(root / "d.json"),
                                 "--old-sidecar", str(root / "missing.sc.json"), "--new-sidecar", str(root / "s.sc.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_safe(result.stderr, f"kept your server(s) {ascii(evil)},")

    def test_force_prune_offenders(self):
        result = self.run_merge({"mcpServers": {"a": {}}}, {"mcpServers": {"a": {}}}, "--force-prune-keys", self.EVIL)
        self.assertEqual(result.returncode, 1)
        self.assert_safe(result.stderr, f"named '{ascii(self.EVIL)}'")

    def test_every_name_sink_uses_format_names(self):
        text = MERGER.read_text(encoding="utf-8")
        body = text[text.index("def print_notes"):]
        self.assertNotIn("printable(", body, "print_notes and main() must call format_names, not printable")
        self.assertNotIn("', '.join(", body)
        self.assertIn("printable(name) for name in sorted(set(names))", text)


class PrunedEntryTests(unittest.TestCase):
    """SEC-T680-09: a hand-edited entry under a pruned name is named, never printed."""

    def prune(self, entries: dict) -> subprocess.CompletedProcess:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "s.json").write_text(json.dumps({"mcpServers": {"keep": {}}}), encoding="utf-8")
        (root / "d.json").write_text(json.dumps({"mcpServers": {"keep": {}, **entries}}), encoding="utf-8")
        (root / "d.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep", *entries]}), encoding="utf-8")
        (root / "s.sc.json").write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["keep"]}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(MERGER), "--source", str(root / "s.json"), "--dest", str(root / "d.json"),
                                 "--old-sidecar", str(root / "d.sc.json"), "--new-sidecar", str(root / "s.sc.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(json.loads((root / "d.json").read_text(encoding="utf-8"))["mcpServers"]), ["keep"])
        return result

    def test_a_hand_edited_same_name_entry_is_named_and_its_content_is_not_printed(self):
        result = self.prune({
            "hindsight": {"url": "https://hindsight-secret-host.invalid/mcp"},
            "cwso": {"url": "${env:CWSO_MCP_URL}", "headers": {"Authorization": "Bearer ${env:CWSO_BEARER_TOKEN}"}},
        })
        self.assertIn("pruned the retired generator server cwso, hindsight", result.stderr)
        self.assertIn("hindsight differs from the generated entry; its old content is not kept", result.stderr)
        self.assertNotIn("cwso differs", result.stderr)
        self.assertNotIn("hindsight-secret-host", result.stderr + result.stdout)

    def test_a_header_edit_and_a_non_object_entry_count_as_edited(self):
        result = self.prune({"a": {"url": "${X}", "headers": {"Authorization": "Bearer literal-token"}},
                             "b": "not an object", "c": {"url": "${X}", "env": []}})
        self.assertIn("a, b, c differs from the generated entry", result.stderr)
        self.assertNotIn("literal-token", result.stderr)

    def test_an_unedited_entry_is_pruned_without_the_differs_note(self):
        result = self.prune({"hindsight": {"url": "${HINDSIGHT_MCP_URL}"}})
        self.assertIn("pruned the retired generator server hindsight", result.stderr)
        self.assertNotIn("differs", result.stderr)


def _section(text: str, heading: str) -> str:
    level = len(heading) - len(heading.lstrip("#"))
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
    assert match, f"heading not found: {heading}"
    rest = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.M)
    return rest[: end.start()] if end else rest


class PiDocumentationTests(unittest.TestCase):
    """The verified-forms table is anchored to its own heading; deleting a row or a label fails a test."""

    @classmethod
    def setUpClass(cls):
        wiki = (REPO / "docs" / "wiki" / "mcp-servers.md").read_text(encoding="utf-8")
        cls.forms = _section(wiki, "#### Pi: verified forms")
        cls.prereq = (IMPL / "PREREQUISITES.md").read_text(encoding="utf-8")

    def test_the_table_has_the_eight_forms_and_says_what_was_observed(self):
        rows = [r for r in self.forms.splitlines() if r.startswith("| ") and "---" not in r and "Form in" not in r]
        self.assertEqual(len(rows), 8)
        for needle in ("`${VAR}`", "`$VAR`", "`${env:VAR}`", "`${VAR:-}`", "unset or set but empty", "`url`", "omitted"):
            self.assertIn(needle, self.forms, needle)
        self.assertIn("**Observed**", self.forms)
        for release in ("0.99.0", "1.0.0", "1.3.0", "1.4.0"):
            self.assertIn(release, self.forms)

    def test_unverified_items_are_named(self):
        self.assertRegex(self.forms, r"(?i)unverified")
        self.assertIn("project-level `.pi/mcp.json`", self.forms)
        self.assertIn("only its `interpolateEnvVars` function was executed", self.forms)

    def test_the_url_limitation_is_stated(self):
        self.assertIn("url must be an http or https URL", self.forms)
        self.assertRegex(self.forms, r"`hindsight` and `cwso`")
        self.assertIn("`skipFormats: [pi]`", self.forms)
        self.assertIn("pruned the retired generator server", self.forms)
        self.assertIn("add an entry of your own with a literal URL", self.forms)

    def test_wording_four_releases_scrubbed_environment_and_the_untested_project_file(self):
        wiki = (REPO / "docs" / "wiki" / "mcp-servers.md").read_text(encoding="utf-8")
        row = next(l for l in self.prereq.splitlines() if l.startswith("| Pi | `${VAR}`"))
        wiki_row = next(l for l in wiki.splitlines() if l.startswith("| Pi | `${VAR}` since T680"))
        for text in (row, wiki_row, self.forms):
            self.assertIn("four releases", text)
            self.assertNotRegex(text, r"0\.99\.0 to 1\.4\.0")
        for status in (row.rstrip(" |").rsplit("|", 1)[1], wiki_row.rstrip(" |").rsplit("|", 1)[1]):
            self.assertIn("project-level `.pi/mcp.json` not tested", status)
        self.assertIn("env -i", self.forms)
        self.assertIn("no network beyond the package installation", self.forms)
        self.assertIn("Pi's own start-up calls were not checked", self.forms)

    def test_pi_has_no_per_server_environment_scoping_is_stated(self):
        residual = _section(self.prereq, "#### What this does not protect")
        self.assertIn("Pi has no per-server environment scoping", residual)
        self.assertIn("SEC-T660-01", residual)

    def test_the_in_place_edit_warning_and_the_scratch_note(self):
        migration = _section(self.prereq, "#### Migration from v8.0.0")
        self.assertIn("If you edited `hindsight` or `cwso` in place, copy the entry to another name before updating", migration)
        self.assertIn("the update removes those two names from `.pi/mcp.json`", migration)
        self.assertIn("differs from the generated entry; its old content is not kept", migration)
        self.assertIn("scratch merge files were deleted", self.forms)
        self.assertIn("T680 session scratchpad", self.forms)

    def test_no_comment_or_docstring_gives_a_range_of_releases(self):
        for path in (REPO / "implementation" / "knowledge" / "mcp" / "servers.yaml", MERGER, SYNC, Path(__file__),
                     REPO / "tests" / "functional" / "test_gitlab_token_handling.py"):
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"0\.99\.0 to\s+(?:#\s*)?1\.4\.0|0\.99-1\.4", path.name)

    def test_the_migration_text_no_longer_claims_a_literal_token_is_replaced_on_pi(self):
        migration = _section(self.prereq, "#### Migration from v8.0.0")
        self.assertIn("**not on Pi**", migration)
        self.assertIn("a token you pasted into `.pi/mcp.json` as a literal value", migration)
        self.assertIn("revoke that token", migration)

    def test_the_posture_row_and_the_migration_note_name_the_new_behaviour(self):
        self.assertIn("left out of the `gitlab` entry", self.prereq)
        self.assertIn("dropped the retired ${env: entry", self.prereq)


if __name__ == "__main__":
    unittest.main()
