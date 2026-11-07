"""T766 (SEC-T756-02): scripts/check-ca-chains.sh, run for real with openssl on the vendored chains.

The stores are built from the fixtures themselves, so the result does not depend on the host's trust store:
- the trust anchor of the control is `Sectigo Public Server Authentication Root R46` as cross-signed in the control
  chain (accepted as an anchor because the check verifies with -partial_chain, as libcurl does);
- the mutations add the disclosure's roots, or one compromised intermediate, to that store, or drop the anchor.
With CI set a missing openssl CLI FAILS the test (the unit-tests job installs it); outside CI the test skips.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.repo import repo_root

ROOT = repo_root()
SCRIPT = ROOT / "scripts" / "check-ca-chains.sh"
FIXTURES = ROOT / "tests" / "fixtures" / "ca-chains"
CERT_RE = re.compile(r"-----BEGIN CERTIFICATE-----\n.*?-----END CERTIFICATE-----\n?", re.S)
ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8"}


def certs(path: Path) -> list[str]:
    return [c if c.endswith("\n") else c + "\n" for c in CERT_RE.findall(path.read_text(encoding="ascii"))]


def run(mode: str, store: Path, fixtures: Path = FIXTURES) -> subprocess.CompletedProcess:
    return subprocess.run(["sh", str(SCRIPT), mode, str(store), str(fixtures)], env=ENV,
                          capture_output=True, text=True, timeout=120, check=False)


class CaChainCheckBase(unittest.TestCase):
    def setUp(self):
        if shutil.which("openssl") is None:
            if os.environ.get("CI"):
                self.fail("openssl CLI missing although CI is set: the unit-tests job installs 'openssl~=3.5'")
            self.skipTest("openssl CLI not installed (outside CI only; CI fails here)")
        self.tmp = Path(tempfile.mkdtemp(prefix="t766-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.anchor = certs(FIXTURES / "control" / "gitlab.com.chain")[-1]
        self.roots = certs(FIXTURES / "disclosure-roots.certs")

    def store(self, *pems: str) -> Path:
        path = self.tmp / f"store-{len(list(self.tmp.iterdir()))}.crt"
        path.write_text("".join(pems), encoding="ascii")
        return path

    def assertCheck(self, result: subprocess.CompletedProcess, code: int, *needles: str) -> None:
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        for needle in needles:
            self.assertIn(needle, result.stdout + result.stderr)


class TestTheCheckOnGoodAndBadStores(CaChainCheckBase):
    def test_a_store_with_the_control_anchor_only_passes(self):
        result = run("--cafile", self.store(self.anchor))
        self.assertCheck(result, 0, "compromised chains and certificates validating: 0 of 19; controls validating: 1 of 1",
                         "store certificates on a compromised key: 0 of 1", "RESULT: PASS")
        self.assertEqual(result.stdout.count("ok   refused: "), 19)

    def test_the_hashed_directory_mode_passes_too(self):
        directory = self.tmp / "capath"
        directory.mkdir()
        (directory / "anchor.pem").write_text(self.anchor, encoding="ascii")
        subprocess.run(["openssl", "rehash", str(directory)], env=ENV, check=True, capture_output=True, timeout=60)
        self.assertCheck(run("--capath", directory), 0, "RESULT: PASS")

    def test_adding_emsign_ecc_root_g3_fails_with_eight_chains(self):
        ecc = [c for c in self.roots if self.subject(c).startswith("CN=emSign ECC Root CA - G3,")]
        self.assertEqual(len(ecc), 1)
        self.assertCheck(run("--cafile", self.store(self.anchor, *ecc)), 1,
                         "validating: 10 of 19", "on a compromised key: 1 of 2", "RESULT: FAIL")

    def test_adding_all_disclosure_roots_fails_with_sixteen_chains(self):
        self.assertCheck(run("--cafile", self.store(self.anchor, *self.roots)), 1,
                         "validating: 19 of 19", "on a compromised key: 4 of 5", "RESULT: FAIL")

    def test_adding_one_compromised_intermediate_without_its_root_fails(self):
        """-partial_chain: libcurl trusts an intermediate in the store, so the check must too."""
        intermediate = certs(FIXTURES / "compromised" / "regular--dv-g3b.chain")[1]
        self.assertTrue(self.subject(intermediate).startswith("CN=EM DV TLS CA - G3B,"), self.subject(intermediate))
        self.assertCheck(run("--cafile", self.store(self.anchor, intermediate)), 1,
                         "VALIDATES against the store: regular--dv-g3b",
                         "holds a certificate on a compromised key", "RESULT: FAIL")

    def test_removing_the_control_anchor_fails(self):
        unrelated = certs(FIXTURES / "compromised" / "regular--dv-g3b.chain")[0]  # a leaf: anchors nothing else
        self.assertCheck(run("--cafile", self.store(unrelated)), 1,
                         "control does NOT validate against the store: gitlab.com", "controls validating: 0 of 1")

    def test_a_resigned_intermediate_is_caught_by_its_key(self):
        """T767: crt.sh holds a second EM DV TLS CA - G3B, same key and TBS, other signature and hash."""
        second = certs(FIXTURES / "extra" / "crtsh-30002976010--em-dv-tls-ca-g3b-second-signature.cert")
        self.assertCheck(run("--cafile", self.store(self.anchor, *second)), 1,
                         "VALIDATES against the store: crtsh-30002976010", "on a compromised key: 1 of 2")

    def test_the_key_scan_reads_every_hashed_entry_of_a_directory(self):
        directory = self.tmp / "capath-bad"
        directory.mkdir()
        (directory / "anchor.pem").write_text(self.anchor, encoding="ascii")
        (directory / "aaa.pem").write_text(self.roots[2], encoding="ascii")
        subprocess.run(["openssl", "rehash", str(directory)], env=ENV, check=True, capture_output=True, timeout=60)
        self.assertCheck(run("--capath", directory), 1, "CN=AAA Certificate Services,O=Comodo CA Limited,",
                         "on a compromised key: 1 of 2")

    @staticmethod
    def subject(pem: str) -> str:
        """The subject in RFC 2253 form (most specific RDN first, `CN=...,O=...`), without the `subject=` prefix.
        An explicit -nameopt: OpenSSL's default name format differs between 3.0 and 3.5 (pipeline 3040148068)."""
        out = subprocess.run(["openssl", "x509", "-noout", "-subject", "-nameopt", "RFC2253"], input=pem, env=ENV,
                             capture_output=True, text=True, check=True, timeout=60).stdout.strip()
        return out.removeprefix("subject=")


class TestTheCheckRefusesWeakInputs(CaChainCheckBase):
    def copy_fixtures(self) -> Path:
        target = self.tmp / "fixtures"
        shutil.copytree(FIXTURES, target)
        return target

    def test_a_missing_compromised_chain_fails(self):
        fixtures = self.copy_fixtures()
        (fixtures / "compromised" / "regular--ov-g3c.chain").unlink()
        self.assertCheck(run("--cafile", self.store(self.anchor), fixtures), 1, "expected 16 compromised chains and 3 extra certificates, found 18")

    def test_a_chain_that_no_longer_reaches_its_root_is_not_counted_as_refused(self):
        """Without its intermediates the chain cannot validate anywhere: a refusal would prove nothing."""
        fixtures = self.copy_fixtures()
        chain = fixtures / "compromised" / "regular--dv-g3b.chain"
        chain.write_text(certs(chain)[0], encoding="ascii")
        self.assertCheck(run("--cafile", self.store(self.anchor), fixtures), 1,
                         "fixture does not validate against the disclosure roots", "RESULT: FAIL")

    def test_no_control_chain_fails(self):
        fixtures = self.copy_fixtures()
        shutil.rmtree(fixtures / "control")
        self.assertCheck(run("--cafile", self.store(self.anchor), fixtures), 1, "FAIL no control chain")

    def test_usage_errors_exit_2(self):
        empty = self.store()
        cases = [("--cafile", self.tmp / "missing.crt"), ("--cafile", empty), ("--capath", self.tmp),
                 ("--other", empty)]
        for mode, store in cases:
            with self.subTest(mode=mode, store=store.name):
                self.assertCheck(run(mode, store), 2, "usage:")


class TestTheCaReleaseCheck(unittest.TestCase):
    """--ca-release: ca-certificates 20261020 removed emSign ECC Root CA - G3 (T767); older releases must fail."""

    DB = "P:musl\nV:1.2.5-r10\n\nP:ca-certificates-bundle\nV:{bundle}\n\nP:ca-certificates\nV:{full}\n\n"

    def check(self, text: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "installed"
            db.write_text(text, encoding="ascii")
            return subprocess.run(["sh", str(SCRIPT), "--ca-release", str(db)], env=ENV, capture_output=True,
                                  text=True, timeout=60, check=False)

    def test_current_and_newer_releases_pass(self):
        for bundle, full in (("20261020-r0", "20261020-r0"), ("20270115-r1", "20261020-r2")):
            with self.subTest(bundle=bundle):
                result = self.check(self.DB.format(bundle=bundle, full=full))
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn("RESULT: PASS", result.stdout)

    def test_older_releases_and_a_missing_bundle_fail(self):
        cases = {self.DB.format(bundle="20260909-r0", full="20261020-r0"): "ca-certificates-bundle 20260909-r0",
                 self.DB.format(bundle="20261020-r0", full="20260909-r0"): "ca-certificates 20260909-r0",
                 "P:ca-certificates\nV:20261020-r0\n": "ca-certificates-bundle is not installed",
                 self.DB.format(bundle="x-r0", full="20261020-r0"): "ca-certificates-bundle x-r0"}
        for text, needle in cases.items():
            with self.subTest(needle=needle):
                result = self.check(text)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(needle, result.stdout)


class TestFixturesAndPipeline(unittest.TestCase):
    def test_fixtures_match_their_checksums_and_hold_no_key(self):
        lines = (FIXTURES / "SHA256SUMS").read_text(encoding="ascii").splitlines()
        listed = {}
        for line in lines:
            digest, name = line.split("  ./", 1)
            listed[name] = digest
        present = {p.relative_to(FIXTURES).as_posix() for p in FIXTURES.rglob("*") if p.is_file()}
        self.assertEqual(present - {"SHA256SUMS", "README.md"}, set(listed))
        self.assertEqual(len([n for n in listed if n.startswith("compromised/")]), 16)
        self.assertEqual(len([n for n in listed if n.startswith("extra/")]), 3)
        for name, digest in listed.items():
            data = (FIXTURES / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest, name)
            self.assertNotIn(b"PRIVATE KEY", data, name)

    def test_both_images_run_the_check_on_branch_and_merge_request_rules_only(self):
        ci = yaml.safe_load((ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8"))
        python_image = ci["ca-chain-check-python"]["image"]
        self.assertEqual(python_image, ci["release"]["image"])  # the pinned python digest
        self.assertNotIn("image", ci["ca-chain-check-node"])  # the default image, node:24-alpine
        for name in ("ca-chain-check-python", "ca-chain-check-node"):
            job = ci[name]
            with self.subTest(job=name):
                self.assertEqual([r["if"] for r in job["rules"]],
                                 ['$CI_PIPELINE_SOURCE == "merge_request_event"', "$CI_COMMIT_BRANCH"])
                self.assertIn("sh scripts/check-ca-chains.sh --cafile /tmp/ca-shipped/cert.pem tests/fixtures/ca-chains",
                              job["script"])
                self.assertIn("cp -L /etc/ssl/cert.pem /tmp/ca-shipped/cert.pem", job["before_script"][0])
                self.assertEqual(job["before_script"][1], "sh scripts/check-ca-chains.sh --ca-release")
                self.assertIn("apk add", job["before_script"][2])  # the store is copied and checked before apk runs
                self.assertIn("sh scripts/check-ca-chains.sh --ca-release", job["script"])


if __name__ == "__main__":
    unittest.main()
