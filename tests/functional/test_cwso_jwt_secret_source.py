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
contacts the network, Docker or Proxmox.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import hmac
import importlib.util
import io
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
        for argv in (["--secret", SYNTHETIC], ["--secret-f", SYNTHETIC]):
            with self.subTest(argv=argv[0]):
                res = _run([sys.executable, str(MINT), *argv], _env())
                self.assertEqual(res.returncode, 2)
                self.assertNotIn(SYNTHETIC, res.stdout + res.stderr)


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

    def test_export_with_explicit_secret_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            secret_file = Path(tmp) / "jwt-secret"
            secret_file.write_text(SYNTHETIC + "\n", encoding="utf-8")
            res = _run([BASH, str(HELPER), "export", "--secret-file", str(secret_file)], _env())
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn(f"export CWSO_JWT_SECRET={SYNTHETIC}", res.stdout)

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

    def test_secret_reaches_container_over_stdin_not_argv(self):
        text = PROXMOX.read_text(encoding="utf-8")
        self.assertIn("| pct exec $CTID -- sh -c 'cat >> /opt/cwso/repo/.env'", text)
        self.assertNotIn("deploy/.env.jwt", text)

    def test_env_line_is_the_one_compose_reads(self):
        # SEC-T694-02: the line written to the compose project .env is
        # CWSO_JWT_SECRET=..., the variable the jwt_secret secret is sourced
        # from; the unused JWT_SECRET= line is gone.
        text = PROXMOX.read_text(encoding="utf-8")
        self.assertIn("""printf '%s=%s\\n' "$SECRET_ENV_VAR" """, text)
        self.assertNotIn("JWT_SECRET=%s", text)


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

    def test_explicit_option_wins(self):
        with mock.patch.dict(os.environ, {ENV_VAR: "from-env"}):
            self.assertEqual(self.mod.resolve_jwt_secret("explicit"), "explicit")

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
