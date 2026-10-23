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

BRAVE_PIN = next(f"{p.name}@{p.version}" for p in M.load_pins(SERVERS) if p.name == "@brave/brave-search-mcp-server")
MEMORY_PIN = next(f"{p.name}@{p.version}" for p in M.load_pins(SERVERS) if p.name == "@modelcontextprotocol/server-memory")
SDK = {"severity": "high", "isDirect": False, "effects": ["@brave/brave-search-mcp-server"], "via": [
    {"title": "adv one", "range": "<1.32.0", "url": "https://github.com/advisories/GHSA-aaaa-bbbb-cccc"},
    {"title": "adv two", "range": "<1.32.0", "url": "https://github.com/advisories/GHSA-dddd-eeee-ffff"}]}
BRAVE = {"severity": "high", "isDirect": True, "effects": [], "via": ["@modelcontextprotocol/sdk"]}
CHAIN = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": SDK, "@brave/brave-search-mcp-server": BRAVE}}
# SEC-T676-11: a SECOND pinned package (server-memory) also pulls the vulnerable sdk
SDK_TWO = {**SDK, "effects": ["@brave/brave-search-mcp-server", "@modelcontextprotocol/server-memory"]}
MEMORY = {"severity": "high", "isDirect": True, "effects": [], "via": ["@modelcontextprotocol/sdk"]}
TWO_PINS = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": SDK_TWO, "@brave/brave-search-mcp-server": BRAVE,
                                                 "@modelcontextprotocol/server-memory": MEMORY}}
BOTH = [f"GHSA-aaaa-bbbb-cccc:2026-11-21:{BRAVE_PIN}", f"GHSA-dddd-eeee-ffff:2026-11-21:{BRAVE_PIN}"]
DAY1 = dt.timedelta(days=1)


def accepts(*specs: str) -> dict:
    """What check_acceptances hands to summarise_audit: (advisory, package) -> Acceptance."""
    parsed = [M.parse_accept(s) for s in specs]
    return {(a.advisory, a.package): a for a in parsed}


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
        self.assertIn(f"accepted GHSA-aaaa-bbbb-cccc until 2026-11-21 for {BRAVE_PIN}", out)

    def test_one_unaccepted_advisory_keeps_the_package_a_finding(self):
        code, out = run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=BOTH[:1])
        self.assertEqual(code, 1)
        self.assertNotIn("ACCEPTED high", out)

    def test_acceptance_of_an_unrelated_id_changes_nothing(self):
        self.assertEqual(run_audit(SERVERS, FakeNpm(CHAIN), level="high",
                                   accept=[f"GHSA-zzzz-zzzz-zzzz:2026-11-21:{BRAVE_PIN}"])[0], 1)

    def test_an_expired_acceptance_fails_even_when_it_matches(self):
        expired = [a.replace("2026-11-21", "2026-10-21") for a in BOTH]
        code, out = run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=expired)
        self.assertEqual(code, 1)
        self.assertIn("EXPIRED GHSA-aaaa-bbbb-cccc until 2026-10-21", out)
        self.assertNotIn("ACCEPTED high", out)

    def test_the_last_day_still_counts_and_the_day_after_does_not(self):
        accepted = accepts(f"GHSA-aaaa-bbbb-cccc:2026-10-22:{BRAVE_PIN}", f"GHSA-dddd-eeee-ffff:2026-10-22:{BRAVE_PIN}")
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 0)
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY + DAY1)[1], 2)

    def test_an_expired_acceptance_with_no_matching_finding_still_fails(self):
        code, _ = run_audit(SERVERS, FakeNpm(), accept=[f"GHSA-aaaa-bbbb-cccc:2026-01-01:{BRAVE_PIN}"])
        self.assertEqual(code, 1)

    def test_the_expiry_date_and_the_package_are_mandatory_and_validated(self):
        for bad in ("GHSA-aaaa-bbbb-cccc", "GHSA-aaaa-bbbb-cccc:", "GHSA-aaaa-bbbb-cccc:2026-11-21",
                    "GHSA-aaaa-bbbb-cccc:2026-11-21:", "GHSA-aaaa-bbbb-cccc:2026-11-21:pkg",
                    "GHSA-aaaa-bbbb-cccc:2026-11-21:pkg@latest", "GHSA-aaaa-bbbb-cccc:2026-11-21:pkg@^1.0.0",
                    "GHSA-aaaa-bbbb-cccc:2026-13-01:pkg@1.0.0", "GHSA-aaaa-bbbb-cccc:20261121:pkg@1.0.0",
                    "GHSA-aaaa-bbbb-cccc:pkg@1.0.0", "CVE-2026-1:2026-11-21:pkg@1.0.0",
                    "GHSA-aaaa-bbbb:2026-11-21:pkg@1.0.0", ":2026-11-21:pkg@1.0.0", "GHSA-aaaa-bbbb-cccc:2026-11-21:pkg@1.0.0:x"):
            with self.subTest(bad=bad), self.assertRaises(argparse.ArgumentTypeError):
                M.parse_accept(bad)
        self.assertEqual(M.parse_accept(f"GHSA-aaaa-bbbb-cccc:2026-11-21:{BRAVE_PIN}"),
                         M.Acceptance("GHSA-aaaa-bbbb-cccc", dt.date(2026, 11, 21), "@brave/brave-search-mcp-server",
                                      BRAVE_PIN.rsplit("@", 1)[1]))

    def test_the_same_advisory_twice_for_one_package_is_an_error(self):
        with self.assertRaises(M.AuditError):
            run_audit(SERVERS, FakeNpm(CHAIN), accept=[BOTH[0], BOTH[0]])

    def test_the_cli_refuses_an_acceptance_without_a_date_or_a_package(self):
        for spec in ("GHSA-aaaa-bbbb-cccc", "GHSA-aaaa-bbbb-cccc:2026-11-21"):
            err = io.StringIO()
            with self.subTest(spec=spec), contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                M.main(["audit", "--accept", spec])
            self.assertIn("expiry and package mandatory", err.getvalue())

    def test_mutation_ignoring_the_expiry_is_detected(self):
        mutant = mutated("active = {key for key, item in (accepted or {}).items() if item.until >= day}",
                         "active = set(accepted or {})")
        accepted = accepts(f"GHSA-aaaa-bbbb-cccc:2026-10-22:{BRAVE_PIN}", f"GHSA-dddd-eeee-ffff:2026-10-22:{BRAVE_PIN}")
        late = TODAY + dt.timedelta(days=60)
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, late)[1], 2)
        self.assertEqual(mutant.summarise_audit(CHAIN, "high", accepted, late)[1], 0)

    def test_mutation_hiding_an_accepted_finding_is_detected(self):
        mutant = mutated("        lines.append(f\"  {'ACCEPTED ' if done else ''}{severity:<8}",
                         "        if not done:\n            lines.append(f\"  {severity:<8}")
        accepted = accepts(*BOTH)
        self.assertEqual(len(M.summarise_audit(CHAIN, "high", accepted, TODAY)[0]), 2)
        self.assertEqual(len(mutant.summarise_audit(CHAIN, "high", accepted, TODAY)[0]), 0)  # the mutant hides them

    def test_mutation_counting_a_partly_accepted_package_as_accepted_is_detected(self):
        mutant = mutated("            if any((advisory_id(via), root) not in active for root in roots):\n                return False",
                         "            pass")
        accepted = accepts(f"GHSA-aaaa-bbbb-cccc:2026-10-27:{BRAVE_PIN}")
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 2)
        self.assertEqual(mutant.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 0)

    def test_mutation_dropping_the_expired_failure_is_detected(self):
        mutant = mutated("        hits += expired\n", "        hits += 0\n")
        spec = dict(servers=str(SERVERS), audit_level="low", signatures=False,
                    accept=[M.parse_accept(f"GHSA-aaaa-bbbb-cccc:2026-01-01:{BRAVE_PIN}")])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(M.command_audit(argparse.Namespace(**spec), FakeNpm(), TODAY), 1)
            self.assertEqual(mutant.command_audit(argparse.Namespace(**spec), FakeNpm(), TODAY), 0)


class TestAcceptanceIsScopedToAPackage(unittest.TestCase):
    """SEC-T676-11: the advisory id alone is not enough; the pinned package it was reviewed for must be the only one at risk."""

    def test_a_second_pin_that_pulls_the_same_library_stays_a_finding(self):
        code, out = run_audit(SERVERS, FakeNpm(TWO_PINS), level="high", accept=BOTH)
        self.assertEqual(code, 1, out)
        # nothing is accepted: the shared library is at risk for two pins, and the packages depending on it stay open too
        self.assertNotIn("ACCEPTED high", out)
        for name in ("@modelcontextprotocol/sdk", "@brave/brave-search-mcp-server", "@modelcontextprotocol/server-memory"):
            self.assertRegex(out, rf"(?m)^  high\s+{name} ")
        self.assertEqual(M.summarise_audit(TWO_PINS, "high", accepts(*BOTH), TODAY)[1], 3)

    def test_the_same_advisories_accepted_for_both_pins_pass(self):
        both_pins = BOTH + [a.replace(BRAVE_PIN, MEMORY_PIN) for a in BOTH]
        code, out = run_audit(SERVERS, FakeNpm(TWO_PINS), level="high", accept=both_pins)
        self.assertEqual(code, 0, out)

    def test_an_acceptance_for_another_pin_does_not_cover_the_library(self):
        other = [a.replace(BRAVE_PIN, MEMORY_PIN) for a in BOTH]
        code, out = run_audit(SERVERS, FakeNpm(CHAIN), level="high", accept=other)
        self.assertEqual(code, 1, out)
        self.assertNotIn("ACCEPTED high", out)

    def test_an_entry_that_reaches_no_direct_package_is_never_accepted(self):
        orphan = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": {**SDK, "effects": []}}}
        self.assertEqual(M.summarise_audit(orphan, "high", accepts(*BOTH), TODAY)[1], 1)
        no_key = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": {
            k: v for k, v in SDK.items() if k != "effects"}}}
        self.assertEqual(M.summarise_audit(no_key, "high", accepts(*BOTH), TODAY)[1], 1)

    def test_an_effects_cycle_terminates(self):
        loop = {"metadata": {}, "vulnerabilities": {
            "a": {"severity": "high", "isDirect": True, "effects": ["b"], "via": ["b"]},
            "b": {"severity": "high", "isDirect": False, "effects": ["a"], "via": ["a"]}}}
        self.assertEqual(M.summarise_audit(loop, "high", {}, TODAY)[1], 2)

    def test_the_version_must_be_the_current_pin(self):
        name, version = BRAVE_PIN.rsplit("@", 1)
        major, minor, patch = (int(x) for x in version.split("-")[0].split("."))
        for stale in (f"{name}@{major}.{minor}.{patch + 1}", f"{name}@{major + 1}.{minor}.{patch}"):
            with self.subTest(stale=stale), self.assertRaisesRegex(M.AuditError, "not a current npm pin"):
                run_audit(SERVERS, FakeNpm(CHAIN), accept=[f"GHSA-aaaa-bbbb-cccc:2026-11-21:{stale}"])

    def test_the_package_must_be_a_pin(self):
        with self.assertRaisesRegex(M.AuditError, "not a current npm pin"):
            run_audit(SERVERS, FakeNpm(CHAIN), accept=["GHSA-aaaa-bbbb-cccc:2026-11-21:left-pad@1.3.0"])

    def test_a_date_more_than_ninety_days_out_is_refused_and_ninety_is_allowed(self):
        far, limit = TODAY + dt.timedelta(days=91), TODAY + dt.timedelta(days=90)
        with self.assertRaisesRegex(M.AuditError, "more than 90 days"):
            run_audit(SERVERS, FakeNpm(CHAIN), accept=[f"GHSA-aaaa-bbbb-cccc:{far.isoformat()}:{BRAVE_PIN}"])
        code, _ = run_audit(SERVERS, FakeNpm(CHAIN), accept=[f"GHSA-aaaa-bbbb-cccc:{limit.isoformat()}:{BRAVE_PIN}"])
        self.assertEqual(code, 1)  # accepted by the date rule, still a finding (only one of the two advisories)

    def test_a_date_in_the_past_is_not_refused_by_the_bound_but_fails_as_expired(self):
        code, out = run_audit(SERVERS, FakeNpm(), accept=[f"GHSA-aaaa-bbbb-cccc:2020-01-01:{BRAVE_PIN}"])
        self.assertEqual((code, "EXPIRED" in out), (1, True))

    def test_the_cli_exits_two_for_a_refused_acceptance(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = M.main(["audit", "--accept", "GHSA-aaaa-bbbb-cccc:2999-01-01:" + BRAVE_PIN])
        self.assertEqual(code, 2)
        self.assertIn("more than 90 days", err.getvalue())

    def test_mutation_accepting_by_advisory_id_alone_is_detected(self):
        mutant = mutated("            if any((advisory_id(via), root) not in active for root in roots):",
                         "            if advisory_id(via) not in {a for a, _ in active}:")
        accepted = accepts(*BOTH)
        self.assertEqual(M.summarise_audit(TWO_PINS, "high", accepted, TODAY)[1], 3)  # the sdk and both pins stay findings
        self.assertEqual(mutant.summarise_audit(TWO_PINS, "high", accepted, TODAY)[1], 0)  # the mutant hides all three

    def test_mutation_accepting_an_entry_with_no_direct_root_is_detected(self):
        mutant = mutated("    if name in seen or not vias or not roots:", "    if name in seen or not vias:")
        orphan = {"metadata": {}, "vulnerabilities": {"@modelcontextprotocol/sdk": {**SDK, "effects": []}}}
        self.assertEqual(M.summarise_audit(orphan, "high", accepts(*BOTH), TODAY)[1], 1)
        self.assertEqual(mutant.summarise_audit(orphan, "high", accepts(*BOTH), TODAY)[1], 0)

    def test_mutation_not_following_effects_is_detected(self):
        mutant = mutated('    for effect in entry.get("effects") or []:', "    for effect in []:")
        accepted = accepts(*BOTH)
        self.assertEqual(M.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 0)
        self.assertEqual(mutant.summarise_audit(CHAIN, "high", accepted, TODAY)[1], 2)  # the sdk reaches no root, so nothing is accepted

    def test_mutation_dropping_the_date_bound_is_detected(self):
        mutant = mutated("        if (item.until - today).days > MAX_ACCEPT_DAYS:", "        if False:")
        far = M.parse_accept(f"GHSA-aaaa-bbbb-cccc:2999-01-01:{BRAVE_PIN}")
        with self.assertRaises(M.AuditError):
            M.check_acceptances([far], M.load_pins(SERVERS), TODAY)
        self.assertEqual(len(mutant.check_acceptances([far], M.load_pins(SERVERS), TODAY)), 1)

    def test_mutation_dropping_the_pin_check_is_detected(self):
        mutant = mutated("        if (item.package, item.version) not in npm_pins:", "        if False:")
        ghost = M.parse_accept("GHSA-aaaa-bbbb-cccc:2026-11-21:left-pad@1.3.0")
        with self.assertRaises(M.AuditError):
            M.check_acceptances([ghost], M.load_pins(SERVERS), TODAY)
        self.assertEqual(len(mutant.check_acceptances([ghost], M.load_pins(SERVERS), TODAY)), 1)

    def test_mutation_allowing_a_duplicate_is_detected(self):
        mutant = mutated('        if (item.advisory, item.package) in keyed:', "        if False:")
        one = M.parse_accept(BOTH[0])
        with self.assertRaises(M.AuditError):
            M.check_acceptances([one, one], M.load_pins(SERVERS), TODAY)
        self.assertEqual(len(mutant.check_acceptances([one, one], M.load_pins(SERVERS), TODAY)), 1)


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
