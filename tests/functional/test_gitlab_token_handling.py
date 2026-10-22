"""T665 (SEC-T660-01) -- the generator side of the GitLab token handling.

Based on docs/artifacts/gitlab-token-handling-design-v1.md (decisions DEC-T664-1 to -6, the user's
decision of 2026-10-16). This file pins:

- servers.yaml: the `gitlab` entry carries the token-file variable (a path, not a secret), the optional
  `default: ""` on both credential entries, the literal `GITLAB_PERMISSION_MODE: modify`, and the launcher
  pin unchanged;
- `sync.mjs` (`mapTemplatedValue`, `validateTemplatedSpecs`): the `default` is rendered as `${VAR:-}` for
  the claude-code format ONLY; an unknown key in a templated value, a `default` on a secret that is not the
  empty string, and an unsafe default stop the run before anything is written;
- the placeholder-form check (design finding F-3) as far as it changed a template: Gemini CLI renders
  `${VAR}`; Cline, VS Code and Opencode are pinned as they were, with the verification status in the
  generator comment and in docs/wiki/mcp-servers.md; Pi renders `${VAR}` and leaves an `optional` variable
  out (T680, observed on four releases (0.99.0, 1.0.0, 1.3.0, 1.4.0); see tests/functional/test_pi_optional_variables.py);
- `scripts/merge-mcp-json.py` on the gitlab entry: the user's own env keys survive, a user's value for the
  file variable is replaced by the generated placeholder (generated values win), and the merge is a fixed
  point;
- the documentation of the token section (PREREQUISITES.md, wiki), anchored to the paragraph each statement
  protects.

Static inspection plus local `node` and `python3` runs on temporary directories; no network, no token.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.repo import implementation_root, knowledge_root, repo_root

REPO = repo_root()
IMPL = implementation_root()
SYNC = IMPL / "scripts" / "sync.mjs"
MERGER = REPO / "scripts" / "merge-mcp-json.py"
SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"

TOKEN = "GITLAB_PERSONAL_ACCESS_TOKEN"
TOKEN_FILE = "GITLAB_PERSONAL_ACCESS_TOKEN_FILE"

# (platform, generated file relative to implementation/, JSON path to the gitlab env, expected template)
GITLAB_ENV_FILES = {
    "claude-code": (".mcp.json", ("mcpServers", "gitlab", "env"), "${VAR}"),
    "vscode": (".vscode/mcp.json", ("servers", "gitlab", "env"), "${env:VAR}"),
    "gemini": (".gemini/settings.json", ("mcpServers", "gitlab", "env"), "${VAR}"),
    "pi": (".pi/mcp.json", ("mcpServers", "gitlab", "env"), "${VAR}"),
    "cline": (".cline/mcp.json", ("mcpServers", "gitlab", "env"), "${env:VAR}"),
    "opencode": (".opencode/opencode.json", ("mcp", "gitlab", "environment"), "{env:VAR}"),
}


def _gitlab_env(platform: str) -> dict:
    rel, path, _ = GITLAB_ENV_FILES[platform]
    node = json.loads((IMPL / rel).read_text(encoding="utf-8"))
    for key in path:
        node = node[key]
    return node


def _shipped_gitlab() -> dict:
    return yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]["gitlab"]


class ServersYamlTests(unittest.TestCase):
    def test_the_gitlab_entry_declares_the_token_file_and_the_defaults(self):
        env = _shipped_gitlab()["env"]
        # T680: both are also `optional`, so Pi (which fails a server for an unset variable) leaves them out
        self.assertEqual(env[TOKEN], {"fromEnv": TOKEN, "secret": True, "default": "", "optional": True})
        # a PATH, not a secret: it must not be marked secret
        self.assertEqual(env[TOKEN_FILE], {"fromEnv": TOKEN_FILE, "default": "", "optional": True})
        self.assertEqual(env["GITLAB_API_URL"], {"fromEnv": "GITLAB_API_URL"})
        self.assertEqual(env["GITLAB_PERMISSION_MODE"], "modify")

    def test_the_launcher_pin_is_unchanged(self):
        gitlab = _shipped_gitlab()
        self.assertEqual((gitlab["command"], gitlab["args"]), ("npx", ["-y", "@zereight/mcp-gitlab@2.2.5"]))

    def test_only_the_two_credential_entries_carry_a_default(self):
        servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]
        with_default = []
        for name, server in servers.items():
            values = list((server.get("env") or {}).items()) + list((server.get("headers") or {}).items())
            values.append(("url", server.get("url")))
            with_default += [(name, key) for key, spec in values if isinstance(spec, dict) and "default" in spec]
        self.assertEqual(sorted(with_default), [("gitlab", TOKEN), ("gitlab", TOKEN_FILE)])

    def test_no_secret_value_has_a_non_empty_default(self):
        servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]
        for name, server in servers.items():
            for key, spec in {**(server.get("env") or {}), **(server.get("headers") or {})}.items():
                if isinstance(spec, dict) and spec.get("secret"):
                    self.assertIn(spec.get("default", ""), ("",), f"{name}.{key}")


class ShippedOutputTests(unittest.TestCase):
    def test_every_platform_renders_the_token_file_variable_in_its_own_placeholder_form(self):
        for platform, (_, _, template) in GITLAB_ENV_FILES.items():
            with self.subTest(platform=platform):
                env = _gitlab_env(platform)
                # claude-code is the only platform that renders the optional empty default
                suffix = ":-" if platform == "claude-code" else ""
                if platform == "pi":
                    # T680: Pi throws for an unset or empty variable, so an optional one is left out
                    self.assertNotIn(TOKEN_FILE, env)
                    self.assertNotIn(TOKEN, env)
                else:
                    self.assertEqual(env[TOKEN_FILE], template.replace("VAR", TOKEN_FILE + suffix))
                    self.assertEqual(env[TOKEN], template.replace("VAR", TOKEN + suffix))
                self.assertEqual(env["GITLAB_API_URL"], template.replace("VAR", "GITLAB_API_URL"))
                self.assertEqual(env["GITLAB_PERMISSION_MODE"], "modify")
                expected = [TOKEN, TOKEN_FILE, "GITLAB_API_URL", "GITLAB_PERMISSION_MODE"]
                if platform == "pi":
                    expected = expected[2:]   # T680: the two optional variables are left out
                self.assertEqual(list(env), expected)

    def test_only_claude_code_carries_a_default_anywhere(self):
        for platform, (rel, _, _) in GITLAB_ENV_FILES.items():
            text = (IMPL / rel).read_text(encoding="utf-8")
            with self.subTest(platform=platform):
                if platform == "claude-code":
                    self.assertEqual(sorted(set(re.findall(r"\$\{[A-Z_]+:-\}", text))),
                                     ["${GITLAB_PERSONAL_ACCESS_TOKEN:-}", "${GITLAB_PERSONAL_ACCESS_TOKEN_FILE:-}"])
                else:
                    self.assertNotIn(":-", text)

    def test_no_generated_config_holds_a_token_shaped_literal(self):
        for platform, (rel, _, _) in GITLAB_ENV_FILES.items():
            text = (IMPL / rel).read_text(encoding="utf-8")
            with self.subTest(platform=platform):
                self.assertIsNone(re.search(r"glpat-|glft-|gldt-|glrt-", text))

    def test_gemini_renders_the_documented_form_everywhere_and_the_others_keep_theirs(self):
        # Gemini CLI documents `$VAR` and `${VAR}`; its resolver treats `${env:VAR}` as a variable NAMED
        # `env:VAR`, which exists nowhere (envVarResolver.ts, read 2026-10-16, not run).
        gemini = (IMPL / ".gemini" / "settings.json").read_text(encoding="utf-8")
        self.assertNotIn("${env:", gemini)
        self.assertIn("${HINDSIGHT_MCP_URL}", gemini)
        self.assertIn("Bearer ${CWSO_BEARER_TOKEN}", gemini)
        # Cline and VS Code (documented / source-verified) are unchanged; Pi moved to `${VAR}` in T680
        for rel in (".cline/mcp.json", ".vscode/mcp.json"):
            self.assertIn("${env:", (IMPL / rel).read_text(encoding="utf-8"), rel)
        self.assertNotIn("${env:", (IMPL / ".pi" / "mcp.json").read_text(encoding="utf-8"))


def _scratch_root(servers_text: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="t665-sync-"))
    (tmp / "platforms").mkdir()
    for path in (IMPL / "platforms").glob("*.json"):
        shutil.copy(path, tmp / "platforms" / path.name)
    shutil.copytree(IMPL / "_extras", tmp / "_extras")
    for kind in ("mcp", "agents", "commands", "instructions", "skills"):
        (tmp / "knowledge" / kind).mkdir(parents=True)
    (tmp / "knowledge" / "mcp" / "servers.yaml").write_text(servers_text, encoding="utf-8")
    return tmp


def _entry(env_lines: str, extra: str = "") -> str:
    return (
        "servers:\n"
        "  probe:\n"
        "    tags: [core]\n"
        "    transport: stdio\n"
        "    command: npx\n"
        "    args: [\"-y\", \"x@1.0.0\"]\n"
        f"{extra}"
        "    env:\n"
        f"{env_lines}"
    )


class GeneratorDefaultTests(unittest.TestCase):
    def run_sync(self, servers_text: str) -> tuple[Path, subprocess.CompletedProcess]:
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        root = _scratch_root(servers_text)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        proc = subprocess.run(["node", str(SYNC), "--root", str(root)], capture_output=True, text=True, check=False)
        return root, proc

    def probe_env(self, root: Path, platform: str) -> dict:
        rel, path, _ = GITLAB_ENV_FILES[platform]
        node = json.loads((root / rel).read_text(encoding="utf-8"))
        for key in (k if k != "gitlab" else "probe" for k in path):
            node = node[key]
        return node

    def test_the_default_is_rendered_on_claude_code_only(self):
        env = (
            "      A: { fromEnv: AAA, default: \"\" }\n"
            "      B: { fromEnv: BBB, secret: true, default: \"\" }\n"
            "      C: { fromEnv: CCC, default: \"fallback\" }\n"
            "      D: { fromEnv: DDD }\n"
            "      E: literal\n"
        )
        root, proc = self.run_sync(_entry(env))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.probe_env(root, "claude-code"),
                         {"A": "${AAA:-}", "B": "${BBB:-}", "C": "${CCC:-fallback}", "D": "${DDD}", "E": "literal"})
        for platform, template in (("vscode", "${env:VAR}"), ("gemini", "${VAR}"), ("pi", "${VAR}"),
                                   ("cline", "${env:VAR}"), ("opencode", "{env:VAR}")):
            with self.subTest(platform=platform):
                self.assertEqual(self.probe_env(root, platform),
                                 {"A": template.replace("VAR", "AAA"), "B": template.replace("VAR", "BBB"),
                                  "C": template.replace("VAR", "CCC"), "D": template.replace("VAR", "DDD"),
                                  "E": "literal"})

    def test_the_default_is_rendered_inside_a_wrap_and_in_headers_and_urls_on_claude_code(self):
        servers = (
            "servers:\n"
            "  probe:\n"
            "    tags: [core]\n"
            "    transport: remote\n"
            "    url: { fromEnv: URLVAR, default: \"\" }\n"
            "    headers:\n"
            "      Authorization: { fromEnv: TOK, secret: true, wrap: \"Bearer {VAR}\", default: \"\" }\n"
        )
        root, proc = self.run_sync(servers)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        claude = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["probe"]
        self.assertEqual(claude, {"type": "http", "url": "${URLVAR:-}",
                                  "headers": {"Authorization": "Bearer ${TOK:-}"}})
        gemini = json.loads((root / ".gemini" / "settings.json").read_text(encoding="utf-8"))["mcpServers"]["probe"]
        self.assertEqual(gemini, {"httpUrl": "${URLVAR}", "headers": {"Authorization": "Bearer ${TOK}"}})

    def test_unsafe_or_unknown_spec_content_stops_the_run_before_anything_is_written(self):
        bad_lines = {
            "misspelled default": "      A: { fromEnv: AAA, defualt: \"\" }\n",
            "misspelled secret": "      A: { fromEnv: AAA, Secret: true }\n",
            "unknown key": "      A: { fromEnv: AAA, note: x }\n",
            "secret with a default": "      A: { fromEnv: AAA, secret: true, default: \"glpat-FAKE\" }\n",
            "default with a brace": "      A: { fromEnv: AAA, default: \"a}b\" }\n",
            "default with a dollar": "      A: { fromEnv: AAA, default: \"$(x)\" }\n",
            "no variable name": "      A: { secret: true, default: \"\" }\n",
            "bad variable name": "      A: { fromEnv: \"A-B\" }\n",
            "secret not a boolean": "      A: { fromEnv: AAA, secret: yes }\n",
            "secret a number": "      A: { fromEnv: AAA, secret: 1 }\n",
            "wrap without a placeholder": "      A: { fromEnv: AAA, wrap: \"Bearer\" }\n",
            "wrap with two placeholders": "      A: { fromEnv: AAA, wrap: \"{VAR}{VAR}\" }\n",
            "wrap with a shell character": "      A: { fromEnv: AAA, wrap: \"a;b {VAR}\" }\n",
            "wrap with a dollar": "      A: { fromEnv: AAA, wrap: \"$X {VAR}\" }\n",
        }
        for label, line in bad_lines.items():
            with self.subTest(case=label):
                root, proc = self.run_sync(_entry(line))
                self.assertNotEqual(proc.returncode, 0, "must stop: " + label)
                self.assertIn("servers.yaml", proc.stderr)
                for folder in (".mcp.json", ".vscode", ".gemini", ".opencode", ".pi", ".cline"):
                    self.assertFalse((root / folder).exists(), f"{label}: {folder} was written")

    def test_a_default_in_a_header_or_url_is_validated_too(self):
        servers = (
            "servers:\n"
            "  probe:\n"
            "    tags: [core]\n"
            "    transport: remote\n"
            "    url: { fromEnv: URLVAR, defualt: \"\" }\n"
        )
        _, proc = self.run_sync(servers)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unknown key", proc.stderr)

    def test_the_shipped_servers_yaml_passes_the_spec_check(self):
        proc = subprocess.run(["node", str(SYNC), "--root", str(IMPL), "--check"], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_regeneration_is_deterministic(self):
        env = "      A: { fromEnv: AAA, default: \"\" }\n"
        first, p1 = self.run_sync(_entry(env))
        second, p2 = self.run_sync(_entry(env))
        self.assertEqual((p1.returncode, p2.returncode), (0, 0))
        for rel, _, _ in GITLAB_ENV_FILES.values():
            self.assertEqual((first / rel).read_bytes(), (second / rel).read_bytes(), rel)


def _run_merge(source: Path, dest: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(MERGER), "--source", str(source), "--dest", str(dest)],
                          capture_output=True, text=True, check=False)


class MergeBehaviourTests(unittest.TestCase):
    """`install.sh --update` rewrites the gitlab entry of an existing `.mcp.json` through merge-mcp-json.py."""

    V8_GITLAB = {
        "command": "npx",
        "args": ["-y", "@zereight/mcp-gitlab@2.2.5"],
        "env": {TOKEN: "${GITLAB_PERSONAL_ACCESS_TOKEN}", "GITLAB_API_URL": "${GITLAB_API_URL}"},
    }

    def merge(self, dest_data: dict) -> tuple[dict, bytes]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dest = Path(tmp.name) / ".mcp.json"
        dest.write_text(json.dumps(dest_data, indent=2) + "\n", encoding="utf-8")
        result = _run_merge(IMPL / ".mcp.json", dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        first = dest.read_bytes()
        again = _run_merge(IMPL / ".mcp.json", dest)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(dest.read_bytes(), first, "a second merge changed the file (not idempotent)")
        return json.loads(first.decode("utf-8")), first

    def test_a_v8_install_gains_the_file_variable_and_the_default_once(self):
        merged, raw = self.merge({"mcpServers": {"gitlab": json.loads(json.dumps(self.V8_GITLAB))}})
        env = merged["mcpServers"]["gitlab"]["env"]
        self.assertEqual(env, _gitlab_env("claude-code"))
        self.assertEqual(raw.decode("utf-8").count(f'"{TOKEN_FILE}"'), 1)

    def test_the_users_own_env_keys_and_servers_survive(self):
        gitlab = json.loads(json.dumps(self.V8_GITLAB))
        gitlab["env"]["GITLAB_TOOLS"] = "list_issues,get_issue"
        gitlab["env"]["GITLAB_DENIED_TOOLS_REGEX"] = "^merge"
        dest = {"mcpServers": {"gitlab": gitlab, "mine": {"command": "x", "env": {"MY_KEY": "${MY_KEY}"}}}}
        merged, _ = self.merge(dest)
        env = merged["mcpServers"]["gitlab"]["env"]
        self.assertEqual(env["GITLAB_TOOLS"], "list_issues,get_issue")
        self.assertEqual(env["GITLAB_DENIED_TOOLS_REGEX"], "^merge")
        self.assertEqual(env[TOKEN_FILE], "${GITLAB_PERSONAL_ACCESS_TOKEN_FILE:-}")
        self.assertEqual(merged["mcpServers"]["mine"], dest["mcpServers"]["mine"])

    def test_a_users_literal_value_for_the_file_variable_is_replaced_by_the_generated_placeholder(self):
        # Generated leaf values win in merge-mcp-json.py (documented in its module docstring). The
        # supported way to name the file is the environment variable, not an edit of the generated entry.
        gitlab = json.loads(json.dumps(self.V8_GITLAB))
        gitlab["env"][TOKEN_FILE] = "/home/user/.config/gitlab-mcp/token"
        merged, _ = self.merge({"mcpServers": {"gitlab": gitlab}})
        self.assertEqual(merged["mcpServers"]["gitlab"]["env"][TOKEN_FILE], "${GITLAB_PERSONAL_ACCESS_TOKEN_FILE:-}")

    def test_a_literal_token_typed_into_the_file_is_replaced_by_the_placeholder(self):
        # The stale-key case of design section 8.1 item 4: documentation tells the user; the merge does
        # not keep a literal credential in a generated entry.
        gitlab = json.loads(json.dumps(self.V8_GITLAB))
        gitlab["env"][TOKEN] = "glpat-FAKEVALUEFORTESTONLYNOTREAL"
        merged, raw = self.merge({"mcpServers": {"gitlab": gitlab}})
        self.assertEqual(merged["mcpServers"]["gitlab"]["env"][TOKEN], "${GITLAB_PERSONAL_ACCESS_TOKEN:-}")
        self.assertNotIn(b"glpat-", raw)

    def merge_pi(self, dest_data: dict) -> tuple[dict, subprocess.CompletedProcess]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dest = Path(tmp.name) / "mcp.json"
        dest.write_text(json.dumps(dest_data, indent=2) + "\n", encoding="utf-8")
        result = _run_merge(IMPL / ".pi" / "mcp.json", dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(dest.read_text(encoding="utf-8")), result

    def test_a_literal_token_typed_into_the_pi_file_is_kept_but_warned_about_by_name(self):
        # SEC-T680-01: on Pi the generator no longer ships the two token keys, so the merge cannot replace a
        # literal; it keeps the user's key (the merge never deletes one) and says so loudly, naming the key only.
        fake = "glpat-FAKEVALUEFORTESTONLYNOTREAL"
        pi = json.loads((IMPL / ".pi" / "mcp.json").read_text(encoding="utf-8"))
        pi["mcpServers"]["gitlab"]["env"][TOKEN] = fake
        pi["mcpServers"]["gitlab"]["env"]["MY_API_KEY"] = "${MY_API_KEY}"
        pi["mcpServers"]["gitlab"]["env"]["MY_PASSWORD_CMD"] = "!pass show x"
        pi["mcpServers"]["gitlab"]["env"]["GITLAB_TOOLS"] = "list_issues"
        merged, result = self.merge_pi(pi)
        self.assertEqual(merged["mcpServers"]["gitlab"]["env"][TOKEN], fake, "the key is kept, not deleted")
        warnings = [l for l in result.stderr.splitlines() if "WARNING" in l]
        self.assertEqual(len(warnings), 1, result.stderr)
        self.assertIn(f"mcpServers.gitlab.env.{TOKEN} holds a literal value; remove it from the file and revoke the token",
                      warnings[0])
        self.assertNotIn(fake, result.stderr + result.stdout)
        self.assertNotIn("glpat-", result.stderr + result.stdout)

    def test_a_literal_credential_header_is_warned_about_on_any_platform(self):
        source = {"mcpServers": {"srv": {"url": "https://x.invalid/mcp", "headers": {"Origin": "o"}}}}
        dest = {"mcpServers": {"srv": {"url": "https://x.invalid/mcp", "headers": {"Authorization": "Bearer abc-literal"}}}}
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        s, d = Path(tmp.name) / "s.json", Path(tmp.name) / "d.json"
        s.write_text(json.dumps(source), encoding="utf-8")
        d.write_text(json.dumps(dest), encoding="utf-8")
        result = _run_merge(s, d)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("mcpServers.srv.headers.Authorization holds a literal value", result.stderr)
        self.assertNotIn("abc-literal", result.stderr + result.stdout)

    def test_a_placeholder_or_a_non_credential_name_is_not_warned_about(self):
        pi = json.loads((IMPL / ".pi" / "mcp.json").read_text(encoding="utf-8"))
        env = pi["mcpServers"]["gitlab"]["env"]
        env.update({"MY_API_KEY": "${MY_API_KEY}", "OTHER_TOKEN": "$OTHER_TOKEN", "THIRD_SECRET": "{env:THIRD_SECRET}",
                    "GITLAB_TOOLS": "list_issues", "EMPTY_KEY": ""})
        _, result = self.merge_pi(pi)
        self.assertNotIn("WARNING", result.stderr)

    def test_an_already_current_file_is_left_byte_identical(self):
        current = (IMPL / ".mcp.json").read_bytes()
        merged, raw = self.merge(json.loads(current.decode("utf-8")))
        self.assertEqual(raw, current)
        self.assertEqual(merged, json.loads(current.decode("utf-8")))


# ---------------------------------------------------------------------------- documentation ----

PREREQUISITES = IMPL / "PREREQUISITES.md"
WIKI = REPO / "docs" / "wiki" / "mcp-servers.md"


def _section(text: str, heading: str) -> str:
    """The text of `heading` up to the next heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
    assert match, f"heading not found: {heading}"
    rest = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.M)
    return rest[: end.start()] if end else rest


class DocumentationTests(unittest.TestCase):
    """Each assertion is anchored to the section it protects, so deleting the statement fails it."""

    @classmethod
    def setUpClass(cls):
        cls.prereq = PREREQUISITES.read_text(encoding="utf-8")
        cls.wiki = WIKI.read_text(encoding="utf-8")
        cls.prereq_token = _section(cls.prereq, "### GitLab token")
        cls.wiki_token = _section(cls.wiki, "## GitLab token")

    def test_the_wrong_scope_lists_are_gone_from_both_documents(self):
        for text, name in ((self.prereq, "PREREQUISITES.md"), (self.wiki, "mcp-servers.md")):
            self.assertNotIn("read_api, write_repository, read_user", text, name)
            self.assertNotIn("api, read_repository, write_repository", text, name)

    def test_prerequisites_holds_the_one_scope_and_role_table(self):
        table = _section(self.prereq_token, "#### Scope and role")
        self.assertRegex(table, r"\|\s*Use\s*\|")
        self.assertIn("`api`", table)
        self.assertIn("`read_api`", table)
        # the reason the old text was wrong, stated next to the table it replaces
        self.assertRegex(table, r"read_api.{0,80}read-only")
        self.assertRegex(table, r"write_repository.{0,120}(not|cannot|never)")
        self.assertRegex(table, r"never\s+Maintainer", )
        self.assertRegex(table, r"at most 90 days")

    def test_the_wiki_points_at_the_table_instead_of_repeating_a_scope_list(self):
        self.assertIn("PREREQUISITES.md", self.wiki_token)
        self.assertEqual(len(re.findall(r"\|\s*Use\s*\|", self.wiki)), 0, "the scope table must appear once")
        self.assertEqual(len(re.findall(r"\|\s*Use\s*\|", self.prereq)), 1)

    def test_the_token_type_order_does_not_lead_with_the_unverified_fine_grained_token(self):
        order = _section(self.prereq_token, "#### Token type")
        first_item = re.search(r"^1\. (.+)$", order, re.M)
        self.assertIsNotNone(first_item)
        self.assertNotRegex(first_item.group(1).lower(), r"fine-grained")
        self.assertRegex(order, r"(?i)fine-grained[^\n]{0,600}unverified")
        self.assertIn("once the user has run live check 1", order)

    def test_file_mode_steps_and_the_claude_code_default_rule(self):
        steps = _section(self.prereq_token, "#### File mode")
        for needle in ("umask 077", "GITLAB_PERSONAL_ACCESS_TOKEN_FILE", "outside", "${GITLAB_PERSONAL_ACCESS_TOKEN:-}",
                       "remove the old export", "scripts/check-gitlab-token.py"):
            self.assertIn(needle, steps, needle)
        self.assertRegex(steps, r"(?i)non-empty.{0,80}(wins|beats|takes precedence)")

    def test_the_posture_table_labels_every_row_and_only_pi_says_observed(self):
        posture = _section(self.prereq_token, "#### Per-client posture")
        for client in ("Claude Code", "GitHub Copilot", "Opencode", "Gemini CLI", "Pi", "Cline"):
            self.assertRegex(posture, rf"\|\s*{client}", client)
        self.assertIn("unverified", posture)
        rows = [line for line in posture.splitlines() if line.startswith("| ") and "Client" not in line and "---" not in line]
        self.assertEqual(len(rows), 6)
        for row in rows:
            status = row.rstrip(" |").rsplit("|", 1)[1].strip().lower()
            self.assertRegex(status, r"documented|unverified", row[:30])
        # the rows whose behaviour is NOT established must say so in their status cell
        by_client = {row.split("|")[1].strip(): row for row in rows}
        self.assertIn("observed", by_client["Pi"].lower())   # T680: run on Pi, not only read
        for client, row in by_client.items():   # the Status cell (last column) only: other cells say "not observed"
            status = row.rstrip(" |").rsplit("|", 1)[1].lower()
            if client != "Pi":
                self.assertNotRegex(status, r"(?<!not )\bobserved\b", f"{client}: only the Pi row (T680) is a run")
        self.assertIn("unverified live", by_client["Claude Code"].lower())
        self.assertIn("cli unverified", by_client["Cline"].lower())
        self.assertIn("other releases unverified", by_client["Pi"])
        self.assertIn("1.4.0", by_client["Pi"])
        self.assertIn("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB", posture)

    def test_the_residual_is_stated_in_plain_words(self):
        residual = _section(self.prereq_token, "#### What this does not protect")
        self.assertRegex(residual, r"(?i)same user")
        self.assertRegex(residual, r"(?i)mitigated, not closed")
        self.assertIn("glab", residual)
        self.assertIn("SEC-T660-01", residual)
        self.assertIn("2026-10-16", residual)

    def test_migration_for_v8_installs_and_the_live_checks_are_present(self):
        migration = _section(self.prereq_token, "#### Migration from v8.0.0")
        for needle in ("install.sh --update", "revoke", "remove the old export"):
            self.assertIn(needle, migration, needle)
        checks = _section(self.prereq_token, "#### Live checks (run by the user)")
        self.assertEqual(len(re.findall(r"^- \[ \] ", checks, re.M)), 3)
        self.assertIn("throwaway", checks)
        self.assertIn("scratch project", checks)
        self.assertIn("unverified until run", checks)

    def test_file_creation_snippet_and_placement_advice(self):
        steps = _section(self.prereq_token, "#### File mode")
        self.assertIn('( umask 077; mkdir -p "$HOME/.config/gitlab-mcp"; : > "$HOME/.config/gitlab-mcp/token"; chmod 600', steps)
        self.assertRegex(steps, r"(?i)full-disk encryption")
        self.assertIn("$XDG_RUNTIME_DIR", steps)
        self.assertRegex(steps, r"(?i)the harness stores nothing")
        self.assertRegex(steps, r"(?i)keyring")
        self.assertRegex(steps, r"(?i)run the checker afterwards")

    def test_placement_advice_does_not_overclaim_tmpfs(self):
        steps = _section(self.prereq_token, "#### File mode")
        self.assertNotIn("nothing is written to disk", steps)
        self.assertRegex(steps, r"nothing is written to the file system \(tmpfs can still be swapped unless swap is encrypted\)")
        self.assertIn("unless lingering is on", steps)

    def test_the_documented_accepted_scopes_match_the_checker(self):
        # SEC: the doc says read_user is not to be added; the checker must warn on it
        rules = _section(self.prereq_token, "#### Scope and role")
        self.assertIn("`read_user` or any other scope", rules)
        self.assertNotRegex(rules, r"beyond `api`, `read_api`, `read_user`")
        self.assertRegex(rules, r"beyond `api`, `read_api`")
        script = (REPO / "scripts" / "check-gitlab-token.py").read_text(encoding="utf-8")
        self.assertIn('ACCEPTED_SCOPES = frozenset({"api", "read_api"})', script)

    def test_the_check_script_documentation_does_not_claim_the_role(self):
        steps = _section(self.prereq_token, "#### File mode")
        self.assertIn("role: NOT checked", steps)
        self.assertIn("the role was not verified", steps)
        self.assertIn("Members page", steps)

    def test_the_server_side_default_is_documented_with_its_limit(self):
        modify = _section(self.prereq_token, "#### Server-side limits")
        self.assertIn("GITLAB_PERMISSION_MODE", modify)
        self.assertIn("modify", modify)
        self.assertRegex(modify, r"(?i)does not (stop|protect|prevent)")


if __name__ == "__main__":
    unittest.main()
