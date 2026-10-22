"""T676 review follow-ups for scripts/audit-mcp-pins.py (SEC-T676-02, -03, -04): fail-closed audit, expiring
acceptances, an npm run that ignores the maintainer's .npmrc, no registry redirect, clean printed text.
Every guard has a mutation proof (the guard is removed from a copy of the source and the condition must then FAIL).
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import json
import os
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from tests.functional.test_audit_mcp_pins import M, SERVERS, TODAY, FakeNpm, mutated, run_audit

SDK = {"severity": "high", "isDirect": False, "via": [
    {"title": "adv one", "range": "<1.32.0", "url": "https://github.com/advisories/GHSA-aaaa-bbbb-cccc"},
    {"title": "adv two", "range": "<1.32.0", "url": "https://github.com/advisories/GHSA-dddd-eeee-ffff"}]}
BRAVE = {"severity": "high", "isDirect": True, "via": ["@modelcontextprotocol/sdk"]}
CHAIN = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": SDK, "@brave/brave-search-mcp-server": BRAVE}}
BOTH = ["GHSA-aaaa-bbbb-cccc:2026-11-21", "GHSA-dddd-eeee-ffff:2026-11-21"]
DAY1 = dt.timedelta(days=1)


class TestFailClosed(unittest.TestCase):
    def test_a_reply_without_vulnerabilities_and_metadata_is_an_error(self):
        for stdout in ("{}", json.dumps({"vulnerabilities": {}}), json.dumps({"metadata": {}}),
                       json.dumps({"vulnerabilities": [], "metadata": {}}),
                       json.dumps({"vulnerabilities": {}, "metadata": "x"})):
            with self.subTest(stdout=stdout), self.assertRaises(M.AuditError):
                run_audit(SERVERS, FakeNpm(audit_stdout=stdout))

    def test_the_minimal_clean_reply_is_a_clean_result(self):
        code, out = run_audit(SERVERS, FakeNpm(audit_stdout=json.dumps({"vulnerabilities": {}, "metadata": {}})))
        self.assertEqual(code, 0, out)

    def test_an_unknown_or_missing_severity_counts_as_critical(self):
        for severity in ("catastrophic", None, 7):
            report = {"metadata": {}, "vulnerabilities": {"p": {"severity": severity, "isDirect": True, "via": ["q"]}}}
            with self.subTest(severity=severity):
                self.assertEqual(M.summarise_audit(report, "critical")[1], 1)
        report = {"metadata": {}, "vulnerabilities": {"p": {"isDirect": True, "via": ["q"]}}}
        self.assertEqual(M.summarise_audit(report, "critical")[1], 1)

    def test_mutation_unknown_severity_as_info_is_detected(self):
        mutant = mutated("return LEVELS.index(severity) if severity in LEVELS else len(LEVELS) - 1",
                         "return LEVELS.index(severity) if severity in LEVELS else 0")
        report = {"metadata": {}, "vulnerabilities": {"p": {"severity": "catastrophic", "via": []}}}
        self.assertEqual(M.summarise_audit(report, "high")[1], 1)
        self.assertEqual(mutant.summarise_audit(report, "high")[1], 0)

    def test_mutation_accepting_a_reply_without_metadata_is_detected(self):
        mutant = mutated(' or not isinstance(report.get("metadata"), dict):', ":")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(M.AuditError):
                M.audit_directory(Path(tmp), "low", FakeNpm(audit_stdout='{"vulnerabilities": {}}'), {})
            result = mutant.audit_directory(Path(tmp), "low", FakeNpm(audit_stdout='{"vulnerabilities": {}}'), {})
        self.assertEqual(result, ([], 0))


class TestAcceptance(unittest.TestCase):
    def test_accepted_advisories_are_printed_as_accepted_and_not_counted(self):
        code, out = run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=BOTH)
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("ACCEPTED "), 2)  # the sdk and the package that depends on it
        self.assertIn("adv one", out)  # never hidden
        self.assertIn("accepted GHSA-aaaa-bbbb-cccc until 2026-11-21", out)

    def test_one_unaccepted_advisory_keeps_the_package_a_finding(self):
        code, out = run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=BOTH[:1])
        self.assertEqual(code, 1)
        self.assertNotIn("ACCEPTED high", out)

    def test_acceptance_of_an_unrelated_id_changes_nothing(self):
        self.assertEqual(run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=["GHSA-zzzz-zzzz-zzzz:2026-11-21"])[0], 1)

    def test_an_expired_acceptance_fails_even_when_it_matches(self):
        expired = [a.replace("2026-11-21", "2026-10-21") for a in BOTH]
        code, out = run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=expired)
        self.assertEqual(code, 1)
        self.assertIn("EXPIRED GHSA-aaaa-bbbb-cccc until 2026-10-21", out)
        self.assertNotIn("ACCEPTED high", out)

    def test_the_last_day_still_counts_and_the_day_after_does_not(self):
        accepted = {"GHSA-aaaa-bbbb-cccc": TODAY, "GHSA-dddd-eeee-ffff": TODAY}
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 0)
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY + DAY1)[1], 2)

    def test_an_expired_acceptance_with_no_matching_finding_still_fails(self):
        code, _ = run_audit(SERVERS, FakeNpm(), accept=["GHSA-aaaa-bbbb-cccc:2026-01-01"])
        self.assertEqual(code, 1)

    def test_the_expiry_date_is_mandatory_and_validated(self):
        for bad in ("GHSA-aaaa-bbbb-cccc", "GHSA-aaaa-bbbb-cccc:", "GHSA-aaaa-bbbb-cccc:2026-13-01",
                    "GHSA-aaaa-bbbb-cccc:20261121", "GHSA-aaaa-bbbb-cccc:2026-11-21:x", "CVE-2026-1:2026-11-21",
                    "GHSA-aaaa-bbbb:2026-11-21", ":2026-11-21"):
            with self.subTest(bad=bad), self.assertRaises(argparse.ArgumentTypeError):
                M.parse_accept(bad)
        self.assertEqual(M.parse_accept("GHSA-aaaa-bbbb-cccc:2026-11-21"),
                         ("GHSA-aaaa-bbbb-cccc", dt.date(2026, 11, 21)))

    def test_the_same_advisory_twice_is_an_error(self):
        with self.assertRaises(M.AuditError):
            run_audit(SERVERS, FakeNpm(CHAIN), accept=[BOTH[0], BOTH[0]])

    def test_the_cli_refuses_an_acceptance_without_a_date(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
            M.main(["audit", "--accept", "GHSA-aaaa-bbbb-cccc"])
        self.assertIn("expiry mandatory", err.getvalue())

    def test_mutation_ignoring_the_expiry_is_detected(self):
        mutant = mutated("active = {a for a, until in (accepted or {}).items() if until >= day}",
                         "active = set(accepted or {})")
        accepted = {"GHSA-aaaa-bbbb-cccc": TODAY, "GHSA-dddd-eeee-ffff": TODAY}
        late = TODAY + dt.timedelta(days=60)
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, late)[1], 2)
        self.assertEqual(mutant.summarise_audit(CHAIN, "high", accepted, late)[1], 0)

    def test_mutation_hiding_an_accepted_finding_is_detected(self):
        mutant = mutated("        lines.append(f\"  {'ACCEPTED ' if done else ''}{severity:<8}",
                         "        if not done:\n            lines.append(f\"  {severity:<8}")
        accepted = dict(M.parse_accept(a) for a in BOTH)
        self.assertEqual(len(M.summarise_audit(CHAIN, "high", accepted, TODAY)[0]), 2)
        self.assertEqual(len(mutant.summarise_audit(CHAIN, "high", accepted, TODAY)[0]), 0)  # the mutant hides them

    def test_mutation_counting_a_partly_accepted_package_as_accepted_is_detected(self):
        mutant = mutated("            if advisory_id(via) not in active:\n                return False", "            pass")
        accepted = {"GHSA-aaaa-bbbb-cccc": TODAY + 5 * DAY1}
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 2)
        self.assertEqual(mutant.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 0)

    def test_mutation_dropping_the_expired_failure_is_detected(self):
        mutant = mutated("        hits += expired\n", "        hits += 0\n")
        spec = dict(servers=str(SERVERS), audit_level="low", signatures=False,
                    accept=[M.parse_accept("GHSA-aaaa-bbbb-cccc:2026-01-01")])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(M.command_audit(argparse.Namespace(**spec), FakeNpm(), TODAY), 1)
            self.assertEqual(mutant.command_audit(argparse.Namespace(**spec), FakeNpm(), TODAY), 0)


class TestHardenedNpmAndOutput(unittest.TestCase):
    def run_npm(self, module):
        seen = {}

        def fake_run(argv, **kwargs):
            seen["argv"], seen["env"] = list(argv), kwargs["env"]
            if "--userconfig" in argv:
                seen["user_empty"] = Path(argv[argv.index("--userconfig") + 1]).read_text() == ""
                seen["global_empty"] = Path(argv[argv.index("--globalconfig") + 1]).read_text() == ""
            return subprocess.CompletedProcess(argv, 0, "{}", "")

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(module.shutil, "which", return_value="/usr/bin/npm"), \
                mock.patch.object(module.subprocess, "run", fake_run), \
                mock.patch.dict(os.environ, {"NPM_TOKEN": "x", "PATH": "/bin"}):
            module.run_npm(["audit", "--json"], Path(tmp))
        return seen

    def test_npm_runs_with_empty_user_and_global_config_and_the_pinned_registry(self):
        seen = self.run_npm(M)
        argv = seen["argv"]
        self.assertEqual(argv[argv.index("--registry") + 1], "https://registry.npmjs.org/")
        self.assertNotEqual(argv[argv.index("--userconfig") + 1], argv[argv.index("--globalconfig") + 1])
        self.assertTrue(seen["user_empty"] and seen["global_empty"])
        self.assertEqual(argv[-2:], ["audit", "--json"])
        self.assertNotIn("NPM_TOKEN", seen["env"])

    def test_mutation_dropping_the_registry_pin_or_the_config_override_is_detected(self):
        no_registry = mutated(', "--registry", REGISTRY + "/"]', "]")
        self.assertNotIn("--registry", self.run_npm(no_registry)["argv"])
        no_config = mutated('fixed = ["--userconfig", str(user), "--globalconfig", str(glob), ',
                            'fixed = [')
        self.assertNotIn("--userconfig", self.run_npm(no_config)["argv"])
        self.assertIn("--userconfig", self.run_npm(M)["argv"])

    def test_registry_redirects_are_refused(self):
        self.assertIsNone(M._RefuseRedirects().redirect_request(None, None, 302, "Found", {}, "https://evil.example/"))
        self.assertTrue(any(isinstance(h, M._RefuseRedirects) for h in M.OPENER.handlers))

    def test_mutation_following_registry_redirects_is_detected(self):
        mutant = mutated("        return None\n\n\nOPENER",
                         "        return super().redirect_request(req, fp, code, msg, headers, newurl)\n\n\nOPENER")
        request = urllib.request.Request("https://registry.npmjs.org/x")
        args = (request, io.BytesIO(b""), 302, "Found", {}, "https://evil.example/")
        self.assertIsNone(M._RefuseRedirects().redirect_request(*args))
        self.assertIsNotNone(mutant._RefuseRedirects().redirect_request(*args))

    def test_printed_registry_and_npm_text_loses_control_characters(self):
        nasty = "ti\x1b[31mtle\x07‮\x85end\r"
        report = {"metadata": {}, "vulnerabilities": {"pk\x1bg": {"severity": "high\x1b", "via": [
            {"title": nasty, "range": "<1\x00", "url": "https://github.com/advisories/GHSA-aaaa-bbbb-cccc\x1b[2J"}]}}}
        text = "\n".join(M.summarise_audit(report, "low")[0])
        self.assertNotRegex(text, "[\x00-\x08\x0b-\x1f\x7f-\x9f‮]")
        self.assertIn("tleend", text)

    def test_mutation_printing_raw_text_is_detected(self):
        mutant = mutated("def safe_text(value: object) -> str:",
                         "def safe_text(value: object) -> str:\n    return str(value)\n\n\ndef _unused(value: object) -> str:")
        report = {"metadata": {}, "vulnerabilities": {"p": {"severity": "high", "via": [
            {"title": "a\x1b[2Jb", "range": "r", "url": "u"}]}}}
        self.assertNotIn("\x1b", M.summarise_audit(report, "low")[0][0])
        self.assertIn("\x1b", mutant.summarise_audit(report, "low")[0][0])


if __name__ == "__main__":
    unittest.main()
