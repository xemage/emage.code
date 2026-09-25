"""Guard against literal (non-placeholder) secret values in generated MCP output.

Defense-in-depth for the class of leak recorded in
implementation/knowledge/mcp/servers.yaml's toolradar entry (v1 leaked a live
TOOLRADAR_API_KEY value directly into three generated files before the fix to
env-var placeholder syntax). This test asserts every credential-bearing `env`
block value in every generated MCP/settings output file is the generator's
own placeholder syntax, never a literal string.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

# Three generator placeholder families, one per platform group (T517):
#   ${env:VAR}  vscode/cursor/gemini/pi/cline
#   {env:VAR}   opencode
#   ${VAR}      claude-code -- it expands `${VAR}` / `${VAR:-default}` from the live
#               process environment and passes the `env:` form through as literal text.
# This is an allowlist of exactly the forms the generator emits, not a general pattern for
# "anything placeholder-shaped": the `${VAR}` alternative still requires a bare, fully
# upper-snake-case variable name between `${` and `}`, so no credential-shaped literal
# (`tr_live_...`, `glpat-...`, `eyJhbGc...`) can satisfy it.
ALLOWED_ENV_VALUE_RE = re.compile(
    r"^(?:\$?\{env:[A-Z][A-Z0-9_]*\}|\$\{[A-Z][A-Z0-9_]*\})$"
)

# A single well-formed placeholder token, any of the three platform families. Used to
# validate `headers` values, which (unlike `env` values) may wrap a placeholder in fixed
# literal text, e.g. "Bearer ${env:CWSO_BEARER_TOKEN}" or "Bearer ${CWSO_BEARER_TOKEN}".
HEADER_PLACEHOLDER_TOKEN_RE = re.compile(
    r"\$\{env:[A-Z][A-Z0-9_]*\}|\{env:[A-Z][A-Z0-9_]*\}|\$\{[A-Z][A-Z0-9_]*\}"
)


def is_allowed_header_value(value: str) -> bool:
    """A header value is acceptable if it contains exactly one well-formed placeholder
    token, and the remaining literal text outside that token contains no stray `$` and no
    unmatched `{`/`}` characters. Zero placeholder tokens (a bare literal) is rejected —
    that is exactly the leak class this guard exists to catch."""
    matches = list(HEADER_PLACEHOLDER_TOKEN_RE.finditer(value))
    if len(matches) != 1:
        return False
    match = matches[0]
    remainder = value[: match.start()] + value[match.end() :]
    return "$" not in remainder and "{" not in remainder and "}" not in remainder


# Scoped, explicit, documented exception for one known-good (file, header, value) triple.
# This is an allowlist, not a broadening of the accepted-placeholder-family logic above:
# it does not make `${input:...}` generally accepted, and it does not make bare literals
# generally accepted anywhere else. It matches by *exact* value, not just by file+header
# key, so if this entry's value is ever overwritten with a real credential, the guard
# still flags it.
#
# Root .vscode/mcp.json's `cwso` server entry is hand-preserved (the generator never
# rewrites it — see design doc T483 §2(a)) to use two values that are intentionally *not*
# the generator's `${env:VAR}` placeholder syntax:
#
#   - Authorization: "Bearer ${input:cwso_jwt_token}" uses VS Code's own native
#     `${input:...}` secure-prompt mechanism (paired with the `inputs` block's
#     `"password": true` promptString below it in the same file). VS Code resolves this
#     via an interactive prompt and never persists the resolved secret to disk — a
#     stronger guarantee than an `${env:VAR}` environment reference, which is why this
#     entry deliberately diverges from the generator's usual output.
#   - Origin: "http://localhost" is a plain literal, but it is not a secret: it identifies
#     the CWSO shadow-workspace client as a local, non-remote origin. It is a
#     publicly-known, non-sensitive constant — not a member of the leak class (real
#     credential values) this guard exists to catch.
HEADER_VALUE_ALLOWLIST: dict[tuple[str, str], str] = {
    (".vscode/mcp.json", "Authorization"): "Bearer ${input:cwso_jwt_token}",
    (".vscode/mcp.json", "Origin"): "http://localhost",
}


GENERATED_MCP_FILES = [
    "implementation/.vscode/mcp.json",
    "implementation/.cursor/mcp.json",
    "implementation/.gemini/settings.json",
    "implementation/.opencode/opencode.json",
    "implementation/.pi/mcp.json",
    "implementation/.cline/mcp.json",
    "implementation/.mcp.json",
    ".vscode/mcp.json",
    ".cursor/mcp.json",
    ".gemini/settings.json",
    ".opencode/opencode.json",
    ".pi/mcp.json",
    ".cline/mcp.json",
    ".mcp.json",
]


def find_literal_env_values(data, rel_path: str | None = None) -> list[tuple[str, str]]:
    """Recursively find (key, value) pairs inside any 'env' or 'headers' dict whose value
    is not the generator's placeholder syntax. Returns a list of violations.

    `rel_path` is the scanned file's path relative to the repo root. It is only used to
    check `HEADER_VALUE_ALLOWLIST` — an exact (rel_path, header_key) -> expected_value
    match is required before a header value skips the normal placeholder check. Fixture
    based tests that pass no `rel_path` never consult the allowlist, keeping it isolated
    from the guard's general-purpose behavior."""
    violations: list[tuple[str, str]] = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "env" and isinstance(value, dict):
                    for env_key, env_value in value.items():
                        if isinstance(env_value, str) and not ALLOWED_ENV_VALUE_RE.match(env_value):
                            violations.append((env_key, env_value))
                elif key == "headers" and isinstance(value, dict):
                    for header_key, header_value in value.items():
                        if not isinstance(header_value, str):
                            continue
                        if (
                            rel_path is not None
                            and HEADER_VALUE_ALLOWLIST.get((rel_path, header_key)) == header_value
                        ):
                            continue
                        if not is_allowed_header_value(header_value):
                            violations.append((header_key, header_value))
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return violations


class TestMcpSecretGuard(unittest.TestCase):
    def test_no_literal_secrets_in_generated_mcp_output(self):
        for rel_path in GENERATED_MCP_FILES:
            path = repo_root() / rel_path
            if not path.is_file():
                self.fail(f"expected generated MCP file missing: {rel_path}")
            with self.subTest(file=rel_path):
                data = json.loads(path.read_text(encoding="utf-8"))
                violations = find_literal_env_values(data, rel_path=rel_path)
                self.assertEqual(
                    violations, [],
                    msg=f"{rel_path} has literal (non-placeholder) env value(s): {violations}",
                )

    def test_guard_detects_injected_literal_secret(self):
        fixture = {
            "mcpServers": {
                "toolradar": {
                    "command": "npx",
                    "args": ["-y", "toolradar-mcp"],
                    "env": {"TOOLRADAR_API_KEY": "tr_live_FAKEVALUEFORTESTONLYNOTREAL"},
                },
                "cwso": {
                    "type": "http",
                    "url": "${env:CWSO_MCP_URL}",
                    "headers": {"Authorization": "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"},
                },
            }
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(
            violations,
            [
                ("TOOLRADAR_API_KEY", "tr_live_FAKEVALUEFORTESTONLYNOTREAL"),
                ("Authorization", "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"),
            ],
            msg="guard must detect a deliberately-injected literal secret-shaped value",
        )

    def test_guard_allows_placeholder_syntax(self):
        fixture = {
            "mcpServers": {
                "gitlab": {"env": {"GITLAB_PERSONAL_ACCESS_TOKEN": "${env:GITLAB_PERSONAL_ACCESS_TOKEN}"}},
                "brave": {"env": {"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"}},
                "cwso": {
                    "type": "http",
                    "url": "${env:CWSO_MCP_URL}",
                    "headers": {
                        "Authorization": "Bearer ${env:CWSO_BEARER_TOKEN}",
                        "Origin": "${env:CWSO_ORIGIN}",
                    },
                },
            },
            "mcp": {
                "toolradar": {"env": {"TOOLRADAR_API_KEY": "{env:TOOLRADAR_API_KEY}"}},
            },
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(violations, [], msg="legitimate placeholder syntax must not false-positive")

    def test_guard_allows_claude_code_bare_placeholder_syntax(self):
        """T517: claude-code's own `${VAR}` family (no `env:` segment) is legitimate
        generator output and must not false-positive, in `env` and in `headers` alike."""
        fixture = {
            "mcpServers": {
                "gitlab": {"env": {"GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}"}},
                "brave": {"env": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"}},
                "cwso": {
                    "type": "http",
                    "url": "${CWSO_MCP_URL}",
                    "headers": {
                        "Authorization": "Bearer ${CWSO_BEARER_TOKEN}",
                        "Origin": "${CWSO_ORIGIN}",
                    },
                },
            }
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(
            violations, [], msg="claude-code's ${VAR} placeholder family must not false-positive"
        )

    def test_bare_placeholder_family_does_not_weaken_literal_detection(self):
        """T517 admitted a third placeholder family (`${VAR}`) to the allowlist. Confirm
        that widening cannot be used to smuggle a literal credential past the guard: a
        real-secret-shaped value, a lowercase/mixed-case brace expression, and a
        multi-token header value are all still flagged."""
        fixture = {
            "mcpServers": {
                # Real-credential shapes -- none of them can satisfy `^\\$\\{[A-Z][A-Z0-9_]*\\}$`.
                "a": {"env": {"TOOLRADAR_API_KEY": "tr_live_FAKEVALUEFORTESTONLYNOTREAL"}},
                "b": {"env": {"GITLAB_PERSONAL_ACCESS_TOKEN": "glpat-FAKEVALUEFORTESTONLYNOTREAL"}},
                # Brace-shaped but not the generator's syntax: lowercase name, and a
                # partially-interpolated value with literal text glued onto the token.
                "c": {"env": {"LOWER": "${lowercase_name}"}},
                "d": {"env": {"PARTIAL": "prefix-${REAL_VAR}"}},
                # Header carrying a bare literal secret, plus one carrying two tokens.
                "e": {"headers": {"Authorization": "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"}},
                "f": {"headers": {"X-Two": "${ONE}${TWO}"}},
            }
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(
            violations,
            [
                ("TOOLRADAR_API_KEY", "tr_live_FAKEVALUEFORTESTONLYNOTREAL"),
                ("GITLAB_PERSONAL_ACCESS_TOKEN", "glpat-FAKEVALUEFORTESTONLYNOTREAL"),
                ("LOWER", "${lowercase_name}"),
                ("PARTIAL", "prefix-${REAL_VAR}"),
                ("Authorization", "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"),
                ("X-Two", "${ONE}${TWO}"),
            ],
            msg="admitting the ${VAR} family must not weaken literal-secret detection",
        )

    def test_allowlist_permits_known_good_vscode_cwso_entry(self):
        """The exact, documented .vscode/mcp.json `cwso` entry passes: VS Code's
        `${input:...}` secure-prompt Authorization value and the non-secret literal
        Origin value (see HEADER_VALUE_ALLOWLIST for the rationale)."""
        fixture = {
            "servers": {
                "cwso": {
                    "url": "http://127.0.0.1:8080/mcp",
                    "headers": {
                        "Authorization": "Bearer ${input:cwso_jwt_token}",
                        "Origin": "http://localhost",
                    },
                    "type": "http",
                }
            }
        }
        violations = find_literal_env_values(fixture, rel_path=".vscode/mcp.json")
        self.assertEqual(violations, [], msg="documented allowlisted cwso entry must pass")

    def test_allowlist_does_not_broaden_guard_coverage(self):
        """The .vscode/mcp.json allowlist entries are scoped to one exact
        (file, header, value) triple each. Confirm the allowlist cannot be used to
        smuggle a real secret past the guard via a neighboring file, header, or value."""
        # Same header key/value shape as the allowlisted entry, but a *different* file —
        # must still be flagged. The allowlist must not apply repo-wide.
        other_file_fixture = {
            "mcpServers": {"cwso": {"headers": {"Authorization": "Bearer ${input:cwso_jwt_token}"}}}
        }
        violations = find_literal_env_values(other_file_fixture, rel_path=".cursor/mcp.json")
        self.assertEqual(
            violations,
            [("Authorization", "Bearer ${input:cwso_jwt_token}")],
            msg="allowlist must be scoped to .vscode/mcp.json only, not any file",
        )

        # Same file, same header key, but a real-secret-shaped value instead of the
        # allowlisted exact value — must still be flagged. The allowlist matches by
        # exact value, not merely by (file, header key).
        tampered_fixture = {
            "mcpServers": {
                "cwso": {"headers": {"Authorization": "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL"}}
            }
        }
        violations = find_literal_env_values(tampered_fixture, rel_path=".vscode/mcp.json")
        self.assertEqual(
            violations,
            [("Authorization", "Bearer sk_live_FAKEVALUEFORTESTONLYNOTREAL")],
            msg="allowlist must match by exact value, not just by file+header key",
        )

        # Same allowlisted file, but an unrelated header carrying a literal secret —
        # must still be flagged. The allowlist must not broaden to other headers in the
        # same file.
        unrelated_header_fixture = {
            "mcpServers": {
                "other": {"headers": {"X-Api-Key": "sk_live_FAKEVALUEFORTESTONLYNOTREAL"}}
            }
        }
        violations = find_literal_env_values(unrelated_header_fixture, rel_path=".vscode/mcp.json")
        self.assertEqual(
            violations,
            [("X-Api-Key", "sk_live_FAKEVALUEFORTESTONLYNOTREAL")],
            msg="allowlist must not broaden to other headers in the same file",
        )


if __name__ == "__main__":
    unittest.main()
