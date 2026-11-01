"""T676 (SEC-T655-07, SEC-T676-06) -- the `--blocked-origins` glob list of the `playwright` entry blocks what it claims.

`@playwright/mcp@0.0.83` turns each entry into the route glob `*://<entry>/**` (`originOrHostGlob`, which for an entry
that is not a URL with an origin falls through to that form) and the route glob into a regular expression
(`globToRegexPattern`), both in `playwright-core/lib/coreBundle.js`. This module holds a port of the second function, checked
against the vendor function on 2026-10-22, and runs the list against URLs that must be blocked and URLs that must stay
allowed. When the environment variable PLAYWRIGHT_CORE_BUNDLE names a `coreBundle.js` (for example
`<install dir>/node_modules/playwright-core/lib/coreBundle.js`) and `node` exists, the same samples also run through the
VENDOR functions and must agree with the port; otherwise that test is skipped. Re-run it with the variable set at every
Playwright pin bump (docs/wiki/mcp-pin-bump-checklist.md, section 1 step 6c).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.repo import repo_root

SERVERS_YAML = repo_root() / "implementation" / "knowledge" / "mcp" / "servers.yaml"
ESCAPED = set("$^+.*()|\\?{}[]")

MUST_BLOCK = [
    # added by T676 (SEC-T655-07)
    "http://metadata.google.internal/computeMetadata/v1/", "http://metadata.google.internal:80/x",
    "https://svc.cluster.internal:8443/", "http://printer.local/", "http://nas.local:5000/",
    "http://168.63.129.16/machine?comp=goalstate", "http://168.63.129.16:80/", "http://192.0.0.192/latest/",
    "http://198.18.0.1/", "http://198.19.255.254:8080/", "http://224.0.0.251/", "http://239.255.255.250:1900/",
    "http://[64:ff9b::7f00:1]/", "http://[64:ff9b::a9fe:a9fe]:80/", "http://[2002:7f00:1::]/",
    "http://[2002:a9fe:a9fe::1]:8080/", "http://127.0.0.1.nip.io/", "http://10.0.0.1.sslip.io:8080/",
    "https://anything.localtest.me/", "http://foo.lvh.me:3000/",
    # apex names of the loopback services (SEC-T676-06)
    "http://localtest.me/", "http://localtest.me:8080/", "http://lvh.me/", "http://lvh.me:3000/",
    # the earlier list must keep working
    "http://localhost:3000/", "http://169.254.169.254/latest/meta-data/", "http://10.1.2.3/", "http://[::1]:80/",
    "http://user:pw@example.com/", "http://172.20.0.1/", "http://100.100.100.200/", "http://192.168.1.1:8080/",
]
MUST_ALLOW = [
    "https://example.com/", "https://www.nip.io.example.org/", "https://internal.example.com/",
    "https://local.example.com/", "https://198.20.0.1/", "https://198.17.255.255/", "https://192.0.2.1/",
    "https://223.255.255.255/", "https://240.0.0.1/", "https://168.63.130.1/", "https://[2001:db8::1]/",
    "https://[2003::1]/", "https://[64:ff9c::1]/", "https://github.com/", "https://mynip.io/",
    "https://example.com/path.internal", "https://example.com/?u=a.local", "https://notlvh.me.example.org/",
    "https://mylocaltest.me/", "https://example.com/localtest.me",
]


def glob_to_regex(glob: str) -> str:
    """Port of playwright-core's globToRegexPattern for the characters these entries use."""
    out, in_group, i = ["^"], False, 0
    while i < len(glob):
        c = glob[i]
        if c == "\\" and i + 1 < len(glob):
            i += 1
            out.append("\\" + glob[i] if glob[i] in ESCAPED else glob[i])
        elif c == "*":
            count = 1
            while i + 1 < len(glob) and glob[i + 1] == "*":
                count += 1
                i += 1
            out.append("(.*)" if count > 1 else "([^/]*)")
        elif c == "{":
            if in_group:
                raise ValueError("nested group")
            in_group = True
            out.append("(")
        elif c == "}":
            if not in_group:
                raise ValueError("unmatched }")
            in_group = False
            out.append(")")
        elif c == "," and in_group:
            out.append("|")
        else:
            out.append("\\" + c if c in ESCAPED or c == "," else c)
        i += 1
    if in_group:
        raise ValueError("unmatched {")
    out.append("$")
    return "".join(out)


def entries() -> list[str]:
    args = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]["playwright"]["args"]
    return args[args.index("--blocked-origins") + 1].split(";")


def blockers(url: str, patterns: list[str]) -> list[str]:
    return [e for e in patterns if re.search(glob_to_regex(f"*://{e}/**"), url)]


class TestBlockedOrigins(unittest.TestCase):
    def test_no_entry_is_a_url_with_an_origin(self):
        # such an entry would take the `new URL(...).origin` branch of originOrHostGlob instead of `*://<entry>/**`
        for entry in entries():
            self.assertNotRegex(entry, r"^https?://", entry)

    def test_every_sample_that_must_be_blocked_is_blocked(self):
        for url in MUST_BLOCK:
            with self.subTest(url=url):
                self.assertTrue(blockers(url, entries()))

    def test_every_sample_that_must_stay_allowed_is_allowed(self):
        for url in MUST_ALLOW:
            with self.subTest(url=url):
                self.assertEqual(blockers(url, entries()), [])

    def test_mutation_dropping_an_entry_unblocks_its_sample(self):
        for dropped, sample in (("*.internal", "http://metadata.google.internal/x"), ("lvh.me:*", "http://lvh.me:3000/"),
                                ("localtest.me", "http://localtest.me/"), ("[64:ff9b:*", "http://[64:ff9b::7f00:1]/")):
            kept = [e for e in entries() if e != dropped]
            self.assertEqual(len(kept), len(entries()) - 1)
            self.assertEqual(blockers(sample, kept), [], dropped)

    def test_mutation_a_greedy_apex_entry_would_over_block(self):
        self.assertTrue(blockers("https://mylocaltest.me/", ["*localtest.me"]))  # the shipped exact form does not
        self.assertEqual(blockers("https://mylocaltest.me/", entries()), [])

    @unittest.skipUnless(os.environ.get("PLAYWRIGHT_CORE_BUNDLE") and shutil.which("node"),
                         "set PLAYWRIGHT_CORE_BUNDLE to a playwright-core coreBundle.js to compare with the vendor matcher")
    def test_the_port_agrees_with_the_vendor_matcher(self):
        bundle = Path(os.environ["PLAYWRIGHT_CORE_BUNDLE"]).read_text(encoding="utf-8")
        start = bundle.index("function globToRegexPattern(glob)")
        glob_fn = bundle[start:bundle.index("\n}\n", start) + 3]
        start = bundle.index("function originOrHostGlob(originOrHost)")
        origin_fn = bundle[start:bundle.index("\n}\n", start) + 3]
        escaped = 'const escapedChars = new Set(["$","^","+",".","*","(",")","|","\\\\","?","{","}","[","]"]);\n'
        script = (escaped + glob_fn + origin_fn
                  + "const [es, us] = JSON.parse(process.argv[2]);"
                  + "console.log(JSON.stringify(us.map(u => es.filter(e => new RegExp(globToRegexPattern(originOrHostGlob(e))).test(u)))));")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "check.js"
            path.write_text(script, encoding="utf-8")
            done = subprocess.run(["node", str(path), json.dumps([entries(), MUST_BLOCK + MUST_ALLOW])],
                                  capture_output=True, text=True, check=False, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        vendor = json.loads(done.stdout)
        for url, hits in zip(MUST_BLOCK + MUST_ALLOW, vendor):
            with self.subTest(url=url):
                self.assertEqual(sorted(hits), sorted(blockers(url, entries())))
                self.assertEqual(bool(hits), url in MUST_BLOCK)


if __name__ == "__main__":
    unittest.main()
