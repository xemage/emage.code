"""T676 (SEC-T646-03, -05, -06, K-17) -- scripts/audit-mcp-pins.py.

The script turns the exact pins of servers.yaml into a throwaway package.json so that `npm audit` can run, asks
the npm registry about provenance and prints a manual-read notice for the three reference servers. These tests
never reach the network and never run npm: the npm runner and the registry fetcher are injected fakes. Every main
guard has a mutation proof: the guard is removed from a copy of the source, the copy is loaded, and the matching
test condition must then FAIL.

Guards under mutation proof: exact-pin parsing, `--ignore-scripts`, secret-looking variables dropped from the npm
environment, the audit-level threshold, the registry host pin, the manual-read notice, the two-versions conflict,
the provenance requirement.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

import yaml

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "audit-mcp-pins.py"
SERVERS = repo_root() / "implementation" / "knowledge" / "mcp" / "servers.yaml"


def load_module(source: str | None = None, name: str = "audit_mcp_pins") -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8") if source is None else source
    module = types.ModuleType(name)
    module.__file__ = str(SCRIPT)
    sys.modules[name] = module  # dataclasses looks the defining module up by name
    exec(compile(text, str(SCRIPT), "exec"), module.__dict__)  # noqa: S102 -- our own script / a mutation of it
    return module


def mutated(old: str, new: str) -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"mutation anchor must occur exactly once: {old!r}"
    return load_module(text.replace(old, new), "audit_mcp_pins_mutant")


M = load_module()


def servers_file(tmp: str, servers: dict) -> Path:
    path = Path(tmp) / "servers.yaml"
    path.write_text(yaml.safe_dump({"servers": servers}), encoding="utf-8")
    return path


def npx(spec: str) -> dict:
    return {"command": "npx", "args": ["-y", spec]}


class FakeNpm:
    """A runner that records argv and cwd and replays canned replies."""

    def __init__(self, audit: dict | None = None, install_rc: int = 0, audit_stdout: str | None = None, sig_rc: int = 0):
        self.calls: list[list[str]] = []
        self.files: list[set[str]] = []
        self.audit = audit if audit is not None else {"vulnerabilities": {}, "metadata": {}}
        self.install_rc, self.audit_stdout, self.sig_rc = install_rc, audit_stdout, sig_rc

    def __call__(self, argv, cwd):
        self.calls.append(list(argv))
        self.files.append({p.name for p in Path(cwd).iterdir()})
        done = subprocess.CompletedProcess(argv, 0, "", "")
        if argv[0] == "install":
            done.returncode = self.install_rc
        elif argv[:2] == ["audit", "--json"]:
            done.stdout = self.audit_stdout if self.audit_stdout is not None else json.dumps(self.audit)
            done.returncode = 1 if self.audit.get("vulnerabilities") else 0
        elif argv[:2] == ["audit", "signatures"]:
            done.returncode, done.stdout = self.sig_rc, "audited 9 packages\n9 packages have verified attestations\n"
        return done


HIGH = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": {"severity": "high", "isDirect": False, "via": [
    {"title": "an advisory", "range": "<1.32.0", "url": "https://github.com/advisories/GHSA-x"}]}}}
LOW = {"metadata": {}, "vulnerabilities": {"left-pad": {"severity": "low", "isDirect": True, "via": ["other"]}}}


TODAY = dt.date(2026, 10, 22)


def run_audit(servers: Path, runner, level: str = "low", signatures: bool = False, accept=()) -> tuple[int, str]:
    args = argparse.Namespace(servers=str(servers), audit_level=level, signatures=signatures,
                              accept=[M.parse_accept(a) for a in accept])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        return M.command_audit(args, runner, TODAY), out.getvalue()


class TestPins(unittest.TestCase):
    def test_the_real_servers_yaml_yields_the_approved_npm_pins(self):
        from tests.functional.test_mcp_package_pins import APPROVED_NPX_PINS
        pins = {p.server: f"{p.name}@{p.version}" for p in M.load_pins(SERVERS) if p.kind == "npm"}
        self.assertEqual(pins, APPROVED_NPX_PINS)

    def test_the_other_kinds_are_listed_not_audited_by_npm(self):
        kinds = {p.server: p.kind for p in M.load_pins(SERVERS)}
        self.assertEqual(kinds["git"], "pypi")
        self.assertNotIn("docker", kinds.values())  # the github container was removed in v9.0.0 (T676)
        with tempfile.TemporaryDirectory() as tmp:  # the script still understands a digest-pinned container
            digest = "sha256:" + "ab" * 32
            entry = {"command": "docker", "args": ["run", "-i", f"ghcr.io/x/y@{digest}"]}
            pin = M.load_pins(servers_file(tmp, {"c": entry}))[0]
        self.assertEqual((pin.kind, pin.name, pin.version), ("docker", "ghcr.io/x/y", digest))
        manifest = M.build_package_json(M.load_pins(SERVERS))
        self.assertNotIn("mcp-server-git", manifest["dependencies"])
        self.assertTrue(all(v[0].isdigit() for v in manifest["dependencies"].values()))

    def test_manifest_is_private_exact_and_sorted(self):
        manifest = M.build_package_json(M.load_pins(SERVERS))
        self.assertIs(manifest["private"], True)
        self.assertEqual(list(manifest["dependencies"]), sorted(manifest["dependencies"]))
        for version in manifest["dependencies"].values():
            self.assertRegex(version, r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")

    def test_a_floating_or_missing_version_is_refused(self):
        for spec in ("pkg@latest", "pkg@^1.2.3", "pkg@~1.2.3", "pkg@1.x", "pkg@1.2", "pkg", "@scope/pkg@>=1.0.0",
                     "pkg@1.2.3 || 2.0.0", "pkg@file:../x", "PKG@1.2.3", "pkg@1.2.3/../x"):
            with self.subTest(spec=spec), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(M.AuditError):
                    M.load_pins(servers_file(tmp, {"s": npx(spec)}))

    def test_a_prerelease_scoped_pin_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = M.load_pins(servers_file(tmp, {"s": npx("@scope/pkg@1.2.3-beta.4")}))
        self.assertEqual((pins[0].name, pins[0].version), ("@scope/pkg", "1.2.3-beta.4"))

    def test_one_package_at_two_versions_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = M.load_pins(servers_file(tmp, {"a": npx("pkg@1.0.0"), "b": npx("pkg@2.0.0")}))
        with self.assertRaises(M.AuditError):
            M.build_package_json(pins)

    def test_no_npm_pin_is_an_error_and_a_bad_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(M.AuditError):
                M.build_package_json(M.load_pins(servers_file(tmp, {"a": {"command": "python3", "args": []}})))
            empty = Path(tmp) / "e.yaml"
            empty.write_text("servers: {}\n", encoding="utf-8")
            with self.assertRaises(M.AuditError):
                M.load_pins(empty)

    def test_generate_writes_the_manifest_and_the_pypi_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(M.main(["--servers", str(SERVERS), "generate", str(Path(tmp) / "out")]), 0)
            manifest = json.loads((Path(tmp) / "out" / "package.json").read_text(encoding="utf-8"))
            requirements = (Path(tmp) / "out" / "requirements-uvx.txt").read_text(encoding="utf-8")
        self.assertIn("@zereight/mcp-gitlab", manifest["dependencies"])
        self.assertRegex(requirements, r"(?m)^mcp-server-git==\d")

    def test_mutation_accepting_a_range_is_detected(self):
        mutant = mutated(r'@(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)$"', r'@(?P<version>[^ ]+)$"')
        with tempfile.TemporaryDirectory() as tmp:
            path = servers_file(tmp, {"s": npx("pkg@^1.2.3")})
            with self.assertRaises(M.AuditError):
                M.load_pins(path)
            self.assertEqual(mutant.load_pins(path)[0].version, "^1.2.3")  # the mutant lets it through

    def test_mutation_two_versions_of_one_package_is_detected(self):
        mutant = mutated("if deps.setdefault(pin.name, pin.version) != pin.version:",
                         "deps.setdefault(pin.name, pin.version)\n        if False:")
        with tempfile.TemporaryDirectory() as tmp:
            pins = mutant.load_pins(servers_file(tmp, {"a": npx("pkg@1.0.0"), "b": npx("pkg@2.0.0")}))
        self.assertEqual(mutant.build_package_json(pins)["dependencies"]["pkg"], "1.0.0")


class TestAudit(unittest.TestCase):
    def test_install_and_audit_never_run_scripts_and_see_the_manifest(self):
        runner = FakeNpm()
        code, out = run_audit(SERVERS, runner)
        self.assertEqual(code, 0, out)
        self.assertEqual(runner.calls[0][:2], ["install", "--package-lock-only"])
        for argv in runner.calls:
            if argv[0] == "install":
                self.assertIn("--ignore-scripts", argv)
        self.assertIn("package.json", runner.files[0])
        self.assertEqual(runner.calls[1], ["audit", "--json"])
        self.assertIn("no known vulnerabilities", out)

    def test_a_finding_at_the_level_exits_one_and_is_printed(self):
        code, out = run_audit(SERVERS, FakeNpm(HIGH), level="high")
        self.assertEqual(code, 1)
        self.assertIn("@modelcontextprotocol/sdk", out)
        self.assertIn("GHSA-x", out)
        self.assertIn("result: FINDINGS", out)

    def test_a_finding_below_the_level_is_printed_but_does_not_fail(self):
        code, out = run_audit(SERVERS, FakeNpm(LOW), level="high")
        self.assertEqual(code, 0)
        self.assertIn("left-pad", out)
        self.assertEqual(run_audit(SERVERS, FakeNpm(LOW), level="low")[0], 1)

    def test_signatures_mode_does_a_full_install_and_fails_on_a_bad_signature(self):
        runner = FakeNpm(sig_rc=1)
        code, out = run_audit(SERVERS, runner, signatures=True)
        self.assertEqual(code, 1)
        self.assertNotIn("--package-lock-only", runner.calls[0])
        self.assertEqual(runner.calls[-1], ["audit", "signatures"])
        self.assertIn("npm audit signatures: FAILED", out)
        self.assertEqual(run_audit(SERVERS, FakeNpm(), signatures=True)[0], 0)

    def test_install_failure_and_unreadable_audit_are_errors_not_clean_results(self):
        for runner in (FakeNpm(install_rc=1), FakeNpm(audit_stdout="not json"), FakeNpm(audit_stdout="[]"),
                       FakeNpm(audit_stdout=json.dumps({"error": {"code": "ENOTFOUND"}}))):
            with self.subTest(runner=runner.__dict__), self.assertRaises(M.AuditError):
                run_audit(SERVERS, runner)

    def test_the_manual_read_notice_names_the_three_reference_servers(self):
        _, out = run_audit(SERVERS, FakeNpm())
        self.assertIn("MANUAL ADVISORY READ (SEC-T646-06)", out)
        for name in M.CALENDAR_VERSION_PACKAGES:
            self.assertIn(f"- {name}@", out)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(M.manual_read_notice(M.load_pins(servers_file(tmp, {"s": npx("pkg@1.0.0")}))), [])

    def test_the_throwaway_directory_is_removed(self):
        seen = []

        class Spy(FakeNpm):
            def __call__(self, argv, cwd):
                seen.append(Path(cwd))
                return super().__call__(argv, cwd)

        run_audit(SERVERS, Spy())
        self.assertTrue(seen and not seen[0].exists())

    def test_the_npm_environment_drops_anything_secret_looking(self):
        env = M.clean_env({"PATH": "/usr/bin", "HOME": "/h", "WIKI_TOKEN": "x", "GITLAB_PERSONAL_ACCESS_TOKEN": "x",
                           "BRAVE_API_KEY": "x", "npm_config__auth": "x", "AWS_SECRET_ACCESS_KEY": "x",
                           "NPM_PASSWORD": "x", "http_proxy": "http://p:3128"})
        self.assertEqual(sorted(env), ["HOME", "PATH", "http_proxy"])

    def test_the_runner_uses_a_fixed_argv_without_a_shell(self):
        import ast
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "run"
                 and getattr(getattr(n.func, "value", None), "id", "") == "subprocess"]
        self.assertEqual(len(calls), 1)
        keywords = {k.arg: k.value for k in calls[0].keywords}
        self.assertIs(keywords["shell"].value, False)
        self.assertNotIn("os.system", SCRIPT.read_text(encoding="utf-8"))

    def test_mutation_dropping_ignore_scripts_is_detected(self):
        mutant = mutated('base = ["install", "--ignore-scripts", "--no-audit", "--no-fund"]',
                         'base = ["install", "--no-audit", "--no-fund"]')
        self.assertNotIn("--ignore-scripts", mutant.npm_install_args(False))
        self.assertNotIn("--ignore-scripts", mutant.npm_install_args(True))
        self.assertIn("--ignore-scripts", M.npm_install_args(False))
        self.assertIn("--ignore-scripts", M.npm_install_args(True))

    def test_mutation_passing_secrets_to_npm_is_detected(self):
        mutant = mutated("return {k: v for k, v in environ.items() if not SECRET_NAME.search(k)}",
                         "return dict(environ)")
        env = {"WIKI_TOKEN": "x", "PATH": "/bin"}
        self.assertEqual(M.clean_env(env), {"PATH": "/bin"})
        self.assertIn("WIKI_TOKEN", mutant.clean_env(env))

    def test_mutation_the_audit_level_threshold_is_detected(self):
        mutant = mutated("hits += 1 if (not done and severity_index(vuln.get(\"severity\")) >= floor) else 0", "hits += 1")
        self.assertEqual(M.summarise_audit(LOW, "high")[1], 0)
        self.assertEqual(mutant.summarise_audit(LOW, "high")[1], 1)

    def test_mutation_a_failed_signature_check_is_detected(self):
        mutant = mutated("hits += 1 if sig.returncode != 0 else 0", "hits += 0")
        args = argparse.Namespace(servers=str(SERVERS), audit_level="low", signatures=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mutant.command_audit(args, FakeNpm(sig_rc=1)), 0)  # mutant: silently passes
            self.assertEqual(M.command_audit(args, FakeNpm(sig_rc=1)), 1)

    def test_mutation_removing_the_manual_read_notice_is_detected(self):
        mutant = mutated("    if not due:\n        return []\n    return [", "    return [")
        with tempfile.TemporaryDirectory() as tmp:
            pins = M.load_pins(servers_file(tmp, {"s": npx("pkg@1.0.0")}))
        self.assertEqual(M.manual_read_notice(pins), [])
        self.assertTrue(mutant.manual_read_notice(pins))  # the mutant prints a notice with nothing to read

    def test_mutation_swallowing_an_install_failure_is_detected(self):
        mutant = mutated("    if install.returncode != 0:\n        raise AuditError", "    if False:\n        raise AuditError")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(M.AuditError):
                M.audit_directory(Path(tmp), "low", FakeNpm(install_rc=1), {})
            lines, hits = mutant.audit_directory(Path(tmp), "low", FakeNpm(install_rc=1), {})
            self.assertEqual((lines, hits), ([], 0))  # the mutant reports a clean audit after a failed install


class TestProvenance(unittest.TestCase):
    @staticmethod
    def fetcher(provenance_for: set[str], latest: str = "9.9.9"):
        urls: list[str] = []

        def fetch(url: str) -> dict:
            urls.append(url)
            name, version = url.split("registry.npmjs.org/", 1)[1].rsplit("/", 1)
            meta = {"version": latest if version == "latest" else version, "dist": {}}
            if name in provenance_for:
                meta["dist"]["attestations"] = {"provenance": {"predicateType": "https://slsa.dev/provenance/v1"}}
            return meta

        fetch.urls = urls
        return fetch

    def report(self, fetch, require: bool = False) -> tuple[int, str]:
        args = argparse.Namespace(servers=str(SERVERS), require=require)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            return M.command_provenance(args, fetch), out.getvalue()

    def test_report_marks_missing_provenance_and_exits_zero_unless_required(self):
        code, out = self.report(self.fetcher({"@zereight%2Fmcp-gitlab"}))
        self.assertEqual(code, 0)
        self.assertIn("@zereight/mcp-gitlab@2.2.5: provenance yes", out)
        self.assertIn("toolradar-mcp@2.1.0: provenance NO", out)
        self.assertEqual(self.report(self.fetcher(set()), require=True)[0], 1)
        self.assertEqual(self.report(self.fetcher({"x"}), require=False)[0], 0)

    def test_every_npm_pin_and_its_latest_are_asked_for(self):
        fetch = self.fetcher(set())
        self.report(fetch)
        self.assertEqual(len(fetch.urls), 16)
        self.assertIn("https://registry.npmjs.org/@zereight%2Fmcp-gitlab/2.2.5", fetch.urls)
        self.assertIn("https://registry.npmjs.org/@zereight%2Fmcp-gitlab/latest", fetch.urls)
        self.assertTrue(all(u.startswith("https://registry.npmjs.org/") for u in fetch.urls))

    def test_has_provenance_needs_a_provenance_attestation(self):
        self.assertTrue(M.has_provenance({"dist": {"attestations": {"provenance": {"predicateType": "x"}}}}))
        self.assertFalse(M.has_provenance({"dist": {"attestations": {"url": "u"}}}))
        self.assertFalse(M.has_provenance({"dist": {}}))
        self.assertFalse(M.has_provenance({}))
        self.assertFalse(M.has_provenance({"dist": {"attestations": "yes"}}))

    def test_the_registry_fetcher_refuses_other_hosts_schemes_and_queries(self):
        for url in ("http://registry.npmjs.org/x/1.0.0", "https://evil.example/x/1.0.0",
                    "https://registry.npmjs.org.evil.example/x", "https://u@registry.npmjs.org/x",
                    "https://registry.npmjs.org/x?token=1", "file:///etc/passwd", "ftp://registry.npmjs.org/x"):
            with self.subTest(url=url), self.assertRaises(M.AuditError):
                M.fetch_registry_json(url)

    def test_registry_url_encodes_scoped_names(self):
        self.assertEqual(M.registry_url("@scope/pkg", "1.2.3"), "https://registry.npmjs.org/@scope%2Fpkg/1.2.3")
        self.assertEqual(M.registry_url("pkg", "latest"), "https://registry.npmjs.org/pkg/latest")

    def test_mutation_dropping_the_host_pin_is_detected(self):
        mutant = mutated('or parsed.hostname != REGISTRY_HOST', 'or False')
        with self.assertRaises(M.AuditError):
            M.fetch_registry_json("https://evil.example/x")
        with self.assertRaises(Exception) as caught:  # the mutant tries the network instead of refusing
            mutant.fetch_registry_json("https://invalid.invalid/x")
        self.assertNotIsInstance(caught.exception, M.AuditError)
        self.assertNotIsInstance(caught.exception, mutant.AuditError)

    def test_mutation_ignoring_require_is_detected(self):
        mutant = mutated("return 1 if (args.require and missing) else 0", "return 0")
        args = argparse.Namespace(servers=str(SERVERS), require=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(M.command_provenance(args, self.fetcher(set())), 1)
            self.assertEqual(mutant.command_provenance(args, self.fetcher(set())), 0)


class TestCli(unittest.TestCase):
    def test_list_prints_every_pin(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(M.main(["list"]), 0)
        self.assertEqual(len(out.getvalue().strip().splitlines()), len(M.load_pins(SERVERS)))

    def test_a_usage_error_exits_two_without_a_traceback(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(M.main(["--servers", "/nonexistent/servers.yaml", "list"]), 2)
        self.assertNotIn("Traceback", err.getvalue())
        self.assertNotIn("/nonexistent", err.getvalue())

    def test_the_script_runs_as_a_program(self):
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "list"], capture_output=True, text=True, check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("npm\tgitlab\t@zereight/mcp-gitlab\t2.2.5", done.stdout)


if __name__ == "__main__":
    unittest.main()
