"""T694: the CWSO JWT secret comes from CWSO_JWT_SECRET only.

Covers the scripts that used to read a secret file by default
(`../CWSO/.env.jwt.dev` or an absolute path to it):

- scripts/mint-cwso-jwt.py
- scripts/cwso-deploy-helper.sh
- scripts/deploy/cwso-docker-desktop.sh
- scripts/deploy/cwso-proxmox-setup.sh
- implementation/scripts/sia-executor.py
- implementation/scripts/test-phase3.1.py
- implementation/scripts/test-jwt-registration.py (held a committed literal)
- implementation/runtime/cwso/mcp_client.py (SEC-T694-03)
- deploy/docker-compose-t226.yml (SEC-T694-01, SEC-T694-02)

Each script must fail with a message that names CWSO_JWT_SECRET when the
variable is missing, must never print the secret, and no file under
scripts/, implementation/scripts/, implementation/runtime/ or deploy/ may
name `.env.jwt.dev`.

Every test uses a synthetic value and removes any CWSO_JWT_SECRET that the
calling environment holds, so no real secret is read or printed. No test
contacts the network or Proxmox; `docker compose config` runs only where the
compose plugin is present, offline.

T726 adds (SEC-T694-04 to -09, -11): no secret on the sia-executor argv and
no abbreviation; error messages that never echo a value or a path; the
`export --print-secret` gate and the terminal refusal; one secret-file rule
in all four readers; the single-quoted compose `.env` line; pinned,
checksum-verified downloads into mktemp directories. Where a test compares
a secret, it compares sha256 digests, so a failure never prints a value.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import hmac
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_VAR = "CWSO_JWT_SECRET"
SYNTHETIC = "t694-synthetic-test-value-not-a-secret"

MINT = REPO_ROOT / "scripts" / "mint-cwso-jwt.py"
HELPER = REPO_ROOT / "scripts" / "cwso-deploy-helper.sh"
DOCKER_DESKTOP = REPO_ROOT / "scripts" / "deploy" / "cwso-docker-desktop.sh"
PROXMOX = REPO_ROOT / "scripts" / "deploy" / "cwso-proxmox-setup.sh"
SIA_EXECUTOR = REPO_ROOT / "implementation" / "scripts" / "sia-executor.py"
PHASE31 = REPO_ROOT / "implementation" / "scripts" / "test-phase3.1.py"
JWT_REGISTRATION = REPO_ROOT / "implementation" / "scripts" / "test-jwt-registration.py"

COMPOSE = REPO_ROOT / "deploy" / "docker-compose-t226.yml"

SCRIPT_DIRS = (
    REPO_ROOT / "scripts",
    REPO_ROOT / "implementation" / "scripts",
    REPO_ROOT / "implementation" / "runtime",
    REPO_ROOT / "deploy",
)
BASH = shutil.which("bash")


@functools.lru_cache(maxsize=1)
def _compose_available() -> bool:
    """True when `docker compose version` exits 0 (checked once, short timeout).

    A docker CLI without the compose plugin (as in the CI image) rejects
    `compose -f` with "unknown shorthand flag", so the plugin is probed first.
    """
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        res = subprocess.run(
            [docker, "compose", "version"], capture_output=True,
            timeout=15, stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return res.returncode == 0


sys.path.insert(0, str(REPO_ROOT / "implementation"))
from runtime.cwso.mcp_client import CwsoMcpClient  # noqa: E402


def _env(secret: str | None = None, **extra: str) -> dict[str, str]:
    """Return a copy of os.environ without CWSO_JWT_SECRET, optionally set to `secret`."""
    env = {k: v for k, v in os.environ.items() if k != ENV_VAR}
    if secret is not None:
        env[ENV_VAR] = secret
    env.update(extra)
    return env


def _run(argv: list[str], env: dict[str, str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        argv, env=env, cwd=str(cwd or REPO_ROOT), capture_output=True,
        text=True, timeout=60, stdin=subprocess.DEVNULL,
    )


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _b64url_decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def _digest(value: str | bytes) -> str:
    """sha256 hex of a value, so assertions compare digests and never print a value."""
    data = value.encode() if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def _absent(test: unittest.TestCase, needle: str, text: str, what: str) -> None:
    """Assert `needle` is not in `text` without printing either on failure."""
    test.assertTrue(needle not in text, f"{what}: a value or path was echoed (not shown)")


# Synthetic marker for values that must never be echoed (T726).
ECHO_MARKER = "t726-synthetic-echo-marker"


class NoSecretFileDefaultTest(unittest.TestCase):
    def test_no_script_names_env_jwt_dev(self):
        offenders = []
        for root in SCRIPT_DIRS:
            for path in sorted(root.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                if ".env.jwt.dev" in text:
                    offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(offenders, [], "no script, runtime or deploy file may name .env.jwt.dev")


class MintCwsoJwtTest(unittest.TestCase):
    def test_missing_variable_fails_and_names_it(self):
        res = _run([sys.executable, str(MINT)], _env())
        self.assertEqual(res.returncode, 1)
        self.assertIn(ENV_VAR, res.stderr)
        self.assertEqual(res.stdout, "")

    def test_env_secret_signs_token_and_is_not_printed(self):
        res = _run([sys.executable, str(MINT), "--role", "worker", "--sub", "t694"], _env(SYNTHETIC))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn(SYNTHETIC, res.stdout + res.stderr)
        header, payload, sig = res.stdout.strip().split(".")
        expected = hmac.new(SYNTHETIC.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        self.assertEqual(_b64url_decode(sig), expected)

    def test_explicit_secret_file_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "jwt-secret"
            secret_file.write_text("# comment\n" + SYNTHETIC + "\n", encoding="utf-8")
            res = _run([sys.executable, str(MINT), "--secret-file", str(secret_file)], _env())
        self.assertEqual(res.returncode, 0, res.stderr)
        header, payload, sig = res.stdout.strip().split(".")
        expected = hmac.new(SYNTHETIC.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        self.assertEqual(_b64url_decode(sig), expected)

    def test_command_line_secret_option_is_gone(self):
        # Neither the removed option nor an abbreviation of --secret-file may
        # echo the value (argparse prefix matching would otherwise do that).
        cases = (
            ["--secret", ECHO_MARKER], ["--secret-f", ECHO_MARKER],
            [f"--secret={ECHO_MARKER}"], [f"--secret-f={ECHO_MARKER}"], [ECHO_MARKER],
        )
        for argv in cases:
            with self.subTest(case=cases.index(argv)):
                res = _run([sys.executable, str(MINT), *argv], _env())
                self.assertEqual(res.returncode, 2)
                _absent(self, ECHO_MARKER, res.stdout + res.stderr, "minter unknown argument")
                self.assertIn("not shown", res.stderr)

    def test_invalid_option_values_are_not_echoed(self):
        # SEC-T694-05: argparse would print "invalid choice: '<value>'".
        for argv in (["--role", ECHO_MARKER], ["--ttl", ECHO_MARKER], ["--secret-file"]):
            with self.subTest(option=argv[0]):
                res = _run([sys.executable, str(MINT), *argv], _env())
                self.assertEqual(res.returncode, 2)
                _absent(self, ECHO_MARKER, res.stdout + res.stderr, "minter option error")
                self.assertIn(argv[0], res.stderr)
                self.assertIn("value not shown", res.stderr)

    def test_secret_file_errors_do_not_print_the_path(self):
        # SEC-T694-05: name the option, not the path.
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / ECHO_MARKER
            empty = Path(tmp) / f"{ECHO_MARKER}-empty"
            empty.write_text("# only a comment\n\n", encoding="utf-8")
            for path in (missing, empty):
                with self.subTest(exists=path.exists()):
                    res = _run([sys.executable, str(MINT), "--secret-file", str(path)], _env())
                    self.assertEqual(res.returncode, 1)
                    _absent(self, ECHO_MARKER, res.stdout + res.stderr, "minter file error")
                    self.assertIn("--secret-file", res.stderr)


@unittest.skipUnless(BASH, "bash not available")
class CwsoDeployHelperTest(unittest.TestCase):
    def test_export_without_variable_fails_and_names_it(self):
        res = _run([BASH, str(HELPER), "export"], _env())
        self.assertEqual(res.returncode, 1)
        self.assertIn(ENV_VAR, res.stderr)
        self.assertEqual(res.stdout, "")

    def test_export_with_variable_does_not_reprint_it(self):
        res = _run([BASH, str(HELPER), "export"], _env(SYNTHETIC))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn(SYNTHETIC, res.stdout + res.stderr)
        self.assertIn("export CWSO_BASE_URL=", res.stdout)
        self.assertNotIn("export CWSO_JWT_SECRET", res.stdout)

    def test_export_with_explicit_secret_file_needs_print_secret(self):
        # SEC-T694-06: without --print-secret nothing is printed.
        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "jwt-secret"
            secret_file.write_text(SYNTHETIC + "\n", encoding="utf-8")
            res = _run([BASH, str(HELPER), "export", "--secret-file", str(secret_file)], _env())
            ok = _run(
                [BASH, str(HELPER), "export", "--secret-file", str(secret_file), "--print-secret"],
                _env(),
            )
        self.assertEqual(res.returncode, 1)
        self.assertEqual(res.stdout, "")
        self.assertIn("--print-secret", res.stderr)
        self.assertEqual(ok.returncode, 0, "export --print-secret failed (stderr not shown)")
        first = ok.stdout.splitlines()[0]
        self.assertEqual(_digest(first), _digest(f"export CWSO_JWT_SECRET={SYNTHETIC}"))

    def test_export_print_secret_refuses_a_terminal(self):
        # SEC-T694-06: stdout is a pseudo-terminal here, as in an interactive shell.
        import pty  # Unix only; the helper is bash-only anyway.

        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "jwt-secret"
            secret_file.write_text(SYNTHETIC + "\n", encoding="utf-8")
            master, slave = pty.openpty()
            try:
                res = subprocess.run(
                    [BASH, str(HELPER), "export", "--secret-file", str(secret_file), "--print-secret"],
                    env=_env(), cwd=str(REPO_ROOT), stdout=slave, stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL, text=True, timeout=60,
                )
            finally:
                os.close(slave)
                os.close(master)
        self.assertEqual(res.returncode, 1)
        self.assertIn("refusing to print", res.stderr)

    def test_unknown_arguments_and_paths_are_not_echoed(self):
        # SEC-T694-05: only the option name is printed, never a value or a path.
        cases = (
            ["export", f"--secret={ECHO_MARKER}"], ["export", ECHO_MARKER],
            ["export", "--jwt-secret", ECHO_MARKER], ["export", "--secret-file"],
            ["export", "--secret-file", f"/nonexistent/{ECHO_MARKER}", "--print-secret"],
        )
        for argv in cases:
            with self.subTest(case=cases.index(argv)):
                res = _run([BASH, str(HELPER), *argv], _env())
                self.assertEqual(res.returncode, 1)
                _absent(self, ECHO_MARKER, res.stdout + res.stderr, "helper argument error")
                self.assertIn("ERROR:", res.stderr)

    def test_verify_without_variable_fails_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = _run(
                [BASH, str(HELPER), "verify", "--workspace", f"{tmp}/ws", "--diag", f"{tmp}/diag.json"],
                _env(),
            )
            self.assertFalse(Path(tmp, "ws").exists(), "verify must fail before creating the workspace")
        self.assertEqual(res.returncode, 1)
        self.assertIn(ENV_VAR, res.stderr)

    def test_secret_source_option_is_rejected(self):
        res = _run([BASH, str(HELPER), "export", "--secret-source", "file"], _env())
        self.assertEqual(res.returncode, 1)
        self.assertIn("--secret-source was removed", res.stderr)

    def test_verify_passes_secret_by_environment_not_argv(self):
        text = HELPER.read_text(encoding="utf-8")
        self.assertNotIn('--jwt-secret "$secret"', text)

    def test_verify_runtime_argv_and_mktemp_paths(self):
        # SEC-T694-09/-11: run verify against a python3 stub that records its
        # argv and the secret's digest; no fixed /tmp path, no secret on argv.
        with tempfile.TemporaryDirectory() as tmp:
            stub_dir = Path(tmp) / "bin"
            stub_dir.mkdir()
            stub = stub_dir / "python3"
            stub.write_text(
                '#!/bin/bash\nprintf \'%s\\n\' "$@" > "$STUB_ARGV"\n'
                'printf \'%s\' "$CWSO_JWT_SECRET" | sha256sum | cut -c1-64 > "$STUB_DIGEST"\n',
                encoding="utf-8",
            )
            stub.chmod(0o700)
            out = Path(tmp) / "out"
            out.mkdir()
            env = _env(SYNTHETIC, PATH=f"{stub_dir}:/usr/bin:/bin", TMPDIR=tmp,
                       STUB_ARGV=str(out / "argv"), STUB_DIGEST=str(out / "digest"))
            res = _run([BASH, str(HELPER), "verify"], env)
            argv = (out / "argv").read_text(encoding="utf-8")
            digest = (out / "digest").read_text(encoding="utf-8").strip()
        self.assertEqual(res.returncode, 0, "verify with stub failed (output not shown)")
        _absent(self, SYNTHETIC, argv + res.stdout + res.stderr, "verify argv/output")
        self.assertEqual(digest, _digest(SYNTHETIC))
        for option in ("--workspace", "--diagnostic-output", "--parquet-store"):
            lines = argv.splitlines()
            value = lines[lines.index(option) + 1]
            self.assertTrue(value.startswith(f"{tmp}/cwso-credcheck."), option)

    def test_no_fixed_tmp_paths(self):
        text = HELPER.read_text(encoding="utf-8")
        for fixed in ("/tmp/cwso-credcheck", "/tmp/t226-parquet-store"):
            self.assertNotIn(fixed, text)
        self.assertIn("mktemp -d", text)

    def test_up_and_reload_without_variable_fail_before_docker(self):
        for command in ("up", "reload"):
            with self.subTest(command=command):
                # PATH without docker: the secret check must come first.
                res = _run([BASH, str(HELPER), command], _env(PATH="/usr/bin:/bin"))
                self.assertEqual(res.returncode, 1)
                self.assertIn(ENV_VAR, res.stderr)
                self.assertNotIn("Required command not found", res.stderr)


@unittest.skipUnless(BASH, "bash not available")
class DockerDesktopScriptTest(unittest.TestCase):
    def test_setup_without_variable_fails_before_prerequisites(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = _run([BASH, str(DOCKER_DESKTOP)], _env(REPO_ROOT=tmp))
            self.assertFalse(Path(tmp, "deploy").exists())
        self.assertEqual(res.returncode, 1)
        self.assertIn(ENV_VAR, res.stdout + res.stderr)
        self.assertNotIn("Checking Prerequisites", res.stdout)

    def _copy_configuration(self, env: dict[str, str], tmp: str) -> subprocess.CompletedProcess:
        deploy = Path(tmp) / "deploy"
        (deploy / "local-dev").mkdir(parents=True)
        (deploy / "docker-compose-t226.yml").write_text("services: {}\n", encoding="utf-8")
        (deploy / "t226-phase2.env").write_text("EXAMPLE=1\n", encoding="utf-8")
        # Source the functions without running main, then call copy_configuration.
        snippet = 'source <(sed \'/^main "\\$@"$/d\' "$1") && copy_configuration'
        return _run([BASH, "-c", snippet, "bash", str(DOCKER_DESKTOP)], {**env, "REPO_ROOT": tmp})

    def test_copy_configuration_writes_no_secret_to_disk(self):
        # SEC-T694-02: compose reads CWSO_JWT_SECRET from the environment, so
        # the unused JWT_SECRET= line is no longer written anywhere.
        with tempfile.TemporaryDirectory() as tmp:
            res = self._copy_configuration(_env(SYNTHETIC), tmp)
            written = [p.read_text(encoding="utf-8") for p in Path(tmp).rglob("*") if p.is_file()]
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertFalse(any(SYNTHETIC in text for text in written))
        self.assertFalse(any("JWT_SECRET=" in text for text in written))
        self.assertNotIn(SYNTHETIC, res.stdout + res.stderr)
        self.assertIn("docker compose passes it to the services", res.stdout)

    def test_update_without_variable_fails_before_compose(self):
        res = _run([BASH, str(DOCKER_DESKTOP), "--update"], _env(PATH="/usr/bin:/bin"))
        self.assertEqual(res.returncode, 1)
        self.assertIn(ENV_VAR, res.stdout + res.stderr)
        self.assertNotIn("Pulling latest images", res.stdout)

    def test_compose_logs_are_tailed_and_named(self):
        # SEC-T694-01: no full `docker compose logs` dump.
        for path in (DOCKER_DESKTOP, PROXMOX):
            for line in path.read_text(encoding="utf-8").splitlines():
                code = line.strip()
                if re.match(r"(docker compose|docker-compose)\b.*\blogs\b", code):
                    with self.subTest(script=path.name, line=code):
                        self.assertIn("--tail=50", code)


@unittest.skipUnless(BASH, "bash not available")
class ProxmoxScriptTest(unittest.TestCase):
    def test_missing_variable_fails_before_proxmox_checks(self):
        res = _run([BASH, str(PROXMOX), "--auto"], _env())
        self.assertEqual(res.returncode, 1)
        self.assertIn(ENV_VAR, res.stdout + res.stderr)
        self.assertNotIn("Verifying Proxmox Environment", res.stdout)

    # Source the functions without running main, then run `call`.
    _SOURCE = 'source <(sed \'/^main "\\$@"$/d\' "$1") && '

    def _call(self, call: str, env: dict[str, str]) -> subprocess.CompletedProcess:
        return _run([BASH, "-c", self._SOURCE + call, "bash", str(PROXMOX)], env)

    def test_secret_reaches_container_over_stdin_not_argv(self):
        # SEC-T694-09: run deploy_cwso against a `pct` stub that records every
        # argv and the stdin of the .env write; compare digests only.
        value = SYNTHETIC + " $x #y"
        with tempfile.TemporaryDirectory() as tmp:
            stub_dir = Path(tmp) / "bin"
            stub_dir.mkdir()
            (stub_dir / "pct").write_text(
                '#!/bin/bash\nprintf \'%s\\n\' "$*" >> "$STUB_ARGV"\n'
                'case "$*" in *"cat >> /opt/cwso/repo/.env"*) cat > "$STUB_STDIN" ;; '
                '*) cat > /dev/null ;; esac\n',
                encoding="utf-8",
            )
            (stub_dir / "pct").chmod(0o700)
            env = _env(value, PATH=f"{stub_dir}:/usr/bin:/bin", STUB_ARGV=f"{tmp}/argv",
                       STUB_STDIN=f"{tmp}/stdin")
            res = self._call("deploy_cwso", env)
            argv = Path(tmp, "argv").read_text(encoding="utf-8")
            stdin = Path(tmp, "stdin").read_text(encoding="utf-8")
        self.assertEqual(res.returncode, 0, "deploy_cwso with stub failed (output not shown)")
        _absent(self, SYNTHETIC, argv + res.stdout + res.stderr, "pct argv/output")
        self.assertEqual(_digest(stdin), _digest(f"CWSO_JWT_SECRET='{value}'\n"))
        self.assertIn("chmod 600 /opt/cwso/repo/.env", argv)
        self.assertNotIn("deploy/.env.jwt", PROXMOX.read_text(encoding="utf-8"))

    def test_env_line_is_the_one_compose_reads(self):
        # SEC-T694-02/-08: the compose project .env line is CWSO_JWT_SECRET='...',
        # single-quoted so compose reads it literally; a quote is escaped.
        res = self._call("compose_env_line", _env("a'b $c"))
        self.assertEqual(res.returncode, 0)
        self.assertEqual(_digest(res.stdout), _digest("CWSO_JWT_SECRET='a\\'b $c'\n"))
        self.assertNotIn("JWT_SECRET=%s", PROXMOX.read_text(encoding="utf-8"))

    def test_env_line_refuses_backslash_without_echo(self):
        res = self._call("compose_env_line", _env(ECHO_MARKER + "\\x"))
        self.assertEqual(res.returncode, 1)
        _absent(self, ECHO_MARKER, res.stdout + res.stderr, "backslash refusal")
        self.assertIn(ENV_VAR, res.stderr)

    def test_compose_reads_env_line_literally(self):
        # SEC-T694-08: docker compose parses the written line back to the value.
        if not _compose_available():
            self.skipTest("docker compose plugin not available (`docker compose version` did not exit 0)")
        value = "syn'thetic \"q\" #h ${NOT_SET} $also end'"
        with tempfile.TemporaryDirectory() as tmp:
            line = self._call("compose_env_line", _env(value)).stdout
            Path(tmp, ".env").write_text(line, encoding="utf-8")
            Path(tmp, "compose.yml").write_text(
                "services:\n  s:\n    image: busybox:1.36\n"
                "    environment:\n      V: ${CWSO_JWT_SECRET}\n", encoding="utf-8",
            )
            res = _run(["docker", "compose", "config", "--format", "json"], _env(), cwd=Path(tmp))
        self.assertEqual(res.returncode, 0, "docker compose config failed (output not shown)")
        parsed = json.loads(res.stdout)["services"]["s"]["environment"]["V"]
        self.assertEqual(_digest(parsed.replace("$$", "$")), _digest(value))

    def test_downloads_are_pinned_and_verified(self):
        # SEC-T694-11: no unpinned source, a checksum check, no fixed /tmp file.
        text = PROXMOX.read_text(encoding="utf-8")
        for unpinned in ("https://get.docker.com", "releases/latest", "/tmp/get-docker.sh"):
            self.assertNotIn(unpinned, text)
        self.assertEqual(text.count("sha256sum -c -"), 2)
        self.assertEqual(text.count('dir="$(mktemp -d)"'), 2)
        for name in ("DOCKER_INSTALL_SHA256", "COMPOSE_SHA256_X86_64", "COMPOSE_SHA256_AARCH64"):
            self.assertRegex(text, rf'\n{name}="[0-9a-f]{{64}}"\n')
        self.assertRegex(text, r'docker-install/[0-9a-f]{40}/install\.sh')


class ComposeStackTest(unittest.TestCase):
    """deploy/docker-compose-t226.yml (SEC-T694-01, SEC-T694-02)."""

    @staticmethod
    def _sia_executor_script() -> str:
        """Return the sia-executor `command` block scalar, with compose `$$` unescaped."""
        lines = COMPOSE.read_text(encoding="utf-8").splitlines()
        start = lines.index("  sia-executor:")
        block_at = next(i for i in range(start, len(lines)) if lines[i].strip() == "- |")
        body = []
        for line in lines[block_at + 1:]:
            if line.strip() and not line.startswith(" " * 8):
                break
            body.append(line[8:])
        return "\n".join(body).replace("$$", "$")

    def test_secret_is_environment_sourced(self):
        text = COMPOSE.read_text(encoding="utf-8")
        stanza = text.split("\nsecrets:\n", 1)[1].split("\nservices:\n", 1)[0]
        self.assertIn("environment: CWSO_JWT_SECRET", stanza)
        self.assertNotIn("file:", stanza)

    def test_sia_executor_entrypoint_never_exposes_secret(self):
        script = self._sia_executor_script()
        self.assertNotIn("set -x", script)
        self.assertNotIn("--jwt-secret", script)
        self.assertNotIn("ERROR_NO_SECRET", script)
        self.assertIn("export CWSO_JWT_SECRET", script)

    @unittest.skipUnless(BASH, "bash not available")
    def test_sia_executor_entrypoint_runtime(self):
        script = self._sia_executor_script()
        head, _, _ = script.partition("exec python3 sia-executor.py")
        probe = 'exec python3 -c "import os; print(len(os.environ[\'CWSO_JWT_SECRET\']))"\n'
        with tempfile.TemporaryDirectory() as tmp:
            secret_path = Path(tmp) / "jwt_secret"
            runnable = head.replace("/run/secrets/jwt_secret", str(secret_path)) + probe
            env = _env(PYTHONPATH="")
            missing = _run([BASH, "-c", runnable], env, cwd=Path(tmp))
            secret_path.write_text("", encoding="utf-8")
            empty = _run([BASH, "-c", runnable], env, cwd=Path(tmp))
            secret_path.write_text(SYNTHETIC + "\n", encoding="utf-8")
            present = _run([BASH, "-c", runnable], env, cwd=Path(tmp))
        for res in (missing, empty):
            self.assertEqual(res.returncode, 1)
            self.assertIn("missing or empty", res.stderr)
        self.assertEqual(present.returncode, 0, present.stderr)
        self.assertEqual(present.stdout.strip().splitlines()[-1], str(len(SYNTHETIC)))
        self.assertNotIn(SYNTHETIC, present.stdout + present.stderr)

    def test_compose_config_accepts_environment_secret(self):
        if not _compose_available():
            self.skipTest("docker compose plugin not available (`docker compose version` did not exit 0)")
        res = _run(["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"], _env(SYNTHETIC))
        self.assertEqual(res.returncode, 0, res.stderr)


class McpClientFromEnvTest(unittest.TestCase):
    """SEC-T694-03: CwsoMcpClient.from_env() has no default secret file."""

    def test_missing_variable_raises_and_names_it(self):
        env = {k: v for k, v in _env().items() if k != "CWSO_JWT_SECRET_FILE"}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError) as ctx:
                CwsoMcpClient.from_env()
        self.assertIn(ENV_VAR, str(ctx.exception))

    def test_variable_is_used(self):
        with mock.patch.dict(os.environ, {ENV_VAR: SYNTHETIC}):
            client = CwsoMcpClient.from_env()
        self.assertEqual(client._secret, SYNTHETIC.encode())

    def test_explicit_secret_file_variable_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "jwt-secret"
            secret_file.write_text(SYNTHETIC + "\n", encoding="utf-8")
            env = {**_env(), "CWSO_JWT_SECRET_FILE": str(secret_file)}
            with mock.patch.dict(os.environ, env, clear=True):
                client = CwsoMcpClient.from_env()
        self.assertEqual(client._secret, SYNTHETIC.encode())


class SiaExecutorSecretTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load(SIA_EXECUTOR, "sia_executor_t694")

    def test_explicit_file_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "jwt-secret"
            secret_file.write_text(SYNTHETIC + "\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {ENV_VAR: "from-env"}):
                got = self.mod.resolve_jwt_secret(str(secret_file))
        self.assertEqual(_digest(got), _digest(SYNTHETIC))

    def test_parser_has_no_secret_option_and_no_abbreviation(self):
        # SEC-T694-04: the secret is never accepted on argv.
        parser = self.mod.build_parser()
        self.assertFalse(parser.allow_abbrev)
        options = {o for a in parser._actions for o in a.option_strings}
        self.assertNotIn("--jwt-secret", options)
        self.assertIn("--jwt-secret-file", options)

    def test_argv_secret_and_typos_are_not_echoed(self):
        cases = (
            ["--jwt-secret", ECHO_MARKER], [f"--jwt-secret={ECHO_MARKER}"],
            ["--jwt-secret-f", ECHO_MARKER], ["--jwt", ECHO_MARKER], [ECHO_MARKER],
            ["--poll-interval", ECHO_MARKER], ["--jwt-secret-file"],
        )
        for argv in cases:
            with self.subTest(case=cases.index(argv)):
                res = _run([sys.executable, str(SIA_EXECUTOR), *argv], _env())
                self.assertEqual(res.returncode, 2)
                _absent(self, ECHO_MARKER, res.stdout + res.stderr, "sia-executor argv error")
                self.assertIn("not shown", res.stderr)

    def test_secret_file_errors_do_not_print_the_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / ECHO_MARKER
            res = _run([sys.executable, str(SIA_EXECUTOR), "--jwt-secret-file", str(missing)], _env())
        self.assertEqual(res.returncode, 1)
        _absent(self, ECHO_MARKER, res.stdout + res.stderr, "sia-executor file error")
        self.assertIn("--jwt-secret-file", res.stderr)

    def test_environment_is_default(self):
        with mock.patch.dict(os.environ, {ENV_VAR: SYNTHETIC}):
            self.assertEqual(self.mod.resolve_jwt_secret(None), SYNTHETIC)

    def test_missing_variable_exits_and_names_it(self):
        with mock.patch.dict(os.environ, _env(), clear=True):
            with self.assertLogs(self.mod.log, level="ERROR") as logs:
                with self.assertRaises(SystemExit) as ctx:
                    self.mod.resolve_jwt_secret(None)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn(ENV_VAR, "\n".join(logs.output))


class SecretFileRuleTest(unittest.TestCase):
    """SEC-T694-07: the minter, the helper, sia-executor and mcp_client read a
    secret file by one rule: first non-empty line not starting with `#`, stripped."""

    LAYOUTS = (
        "# comment\n\n   {v}  \nsecond-line\n",
        "{v}\r\nsecond-line\r\n",
        "{v}",
        "\t {v}\t\n# trailing comment\n",
    )

    @classmethod
    def setUpClass(cls):
        cls.mint = _load(MINT, "mint_t726")
        cls.sia = _load(SIA_EXECUTOR, "sia_executor_t726")

    def _helper_secret(self, path: Path) -> str:
        script = 'eval "$("$1" export --secret-file "$2" --print-secret)" && printf %s "$CWSO_JWT_SECRET"'
        res = _run([BASH, "-c", script, "bash", str(HELPER), str(path)], _env())
        self.assertEqual(res.returncode, 0, "helper export failed (output not shown)")
        return res.stdout

    def _client_secret(self, path: Path) -> str:
        env = {**_env(), "CWSO_JWT_SECRET_FILE": str(path)}
        with mock.patch.dict(os.environ, env, clear=True):
            return CwsoMcpClient.from_env()._secret.decode()

    def _readers(self, path: Path) -> dict[str, str]:
        readers = {
            "mint": self.mint._load_secret_from_file(path),
            "sia-executor": self.sia.resolve_jwt_secret(str(path)),
            "mcp_client": self._client_secret(path),
        }
        if BASH:
            readers["helper"] = self._helper_secret(path)
        return readers

    def test_all_readers_agree(self):
        value = "t726 synthetic value"
        with tempfile.TemporaryDirectory() as tmp:
            for index, layout in enumerate(self.LAYOUTS):
                path = Path(tmp) / f"secret-{index}"
                path.write_text(layout.format(v=value), encoding="utf-8", newline="")
                digests = {k: _digest(v) for k, v in self._readers(path).items()}
                with self.subTest(layout=index):
                    self.assertEqual(set(digests.values()), {_digest(value)}, sorted(digests))

    def test_no_secret_line_fails_everywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no-secret"
            path.write_text("# only comments\n\n   \n", encoding="utf-8")
            with self.assertRaises(self.mint.SecretSourceError):
                self.mint._load_secret_from_file(path)
            with self.assertRaises(SystemExit), self.assertLogs(self.sia.log, level="ERROR"):
                self.sia.resolve_jwt_secret(str(path))
            if BASH:
                script = '"$1" export --secret-file "$2" --print-secret'
                res = _run([BASH, "-c", script, "bash", str(HELPER), str(path)], _env())
                self.assertEqual(res.returncode, 1)
                self.assertIn("no secret line", res.stderr)


class DiagnosticScriptsTest(unittest.TestCase):
    """test-phase3.1.py and test-jwt-registration.py read CWSO_JWT_SECRET only."""

    def test_scripts_fail_without_variable_before_network(self):
        for path in (PHASE31, JWT_REGISTRATION):
            with self.subTest(script=path.name):
                res = _run([sys.executable, str(path)], _env())
                self.assertEqual(res.returncode, 1)
                self.assertIn(ENV_VAR, res.stderr)
                self.assertNotIn("Registering", res.stdout)
                self.assertNotIn("Generating JWT", res.stdout)

    def test_load_jwt_secret_reads_environment(self):
        for path, name in ((PHASE31, "phase31_t694"), (JWT_REGISTRATION, "jwt_registration_t694")):
            with self.subTest(script=path.name):
                mod = _load(path, name)
                with mock.patch.dict(os.environ, {ENV_VAR: SYNTHETIC}):
                    self.assertEqual(mod.load_jwt_secret(), SYNTHETIC)

    def test_registration_output_redacts_token(self):
        mod = _load(JWT_REGISTRATION, "jwt_registration_t694_out")
        token = mod.generate_jwt_token(SYNTHETIC)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            mod.test_jwt_format(token)
            with mock.patch.object(mod.urllib.request, "urlopen", side_effect=OSError("offline")):
                mod.test_registration("http://127.0.0.1:9", token)
        out = buf.getvalue()
        self.assertNotIn(token, out)
        self.assertNotIn(token.split(".")[2], out)
        self.assertIn("Bearer <redacted>", out)


if __name__ == "__main__":
    unittest.main()
