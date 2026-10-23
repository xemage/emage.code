"""T676 -- docs/wiki/mcp-pin-bump-checklist.md is the maintained checklist for the register items it names.

The document must name every register id it closes, point only at files that exist, be linked from the short
policies (PREREQUISITES.md, mcp-servers.md, servers.yaml) and keep the two unverified live-check sections.
Each rule has a mutation proof on the checker's input.
"""
from __future__ import annotations

import re
import unittest

from tests._helpers.repo import repo_root

ROOT = repo_root()
DOC = ROOT / "docs" / "wiki" / "mcp-pin-bump-checklist.md"
IDS = ("SEC-T646-03", "SEC-T646-04", "SEC-T646-05", "SEC-T646-06", "SEC-T655-06", "SEC-T655-07", "SEC-T658-02",
       "SEC-014", "T638-L-2", "T638-L-8", "K-17", "K-20", "SEC-T675-03", "SEC-T675-09")
GHSA = ("GHSA-6qxp-vccf-f47h", "GHSA-22jm-h49p-29qw", "GHSA-6prh-2h8m-c8cw", "GHSA-46jr-4wx8-v453", "GHSA-rvq5-wwqv-78pq")
EXPIRY = "2026-11-21"
WARNING = "Never run `opencode debug config` with your real home"
REQUIRED_PHRASES = ("audit-mcp-pins.py audit", "audit-mcp-pins.py provenance", "--generate-hashes", "--require-hashes",
                    "Browser security version", "Blocked-origins re-check", "One-time live checks", "excludeTools",
                    "opencode agent list", "(unverified)", WARNING, "ci_images_reviewed_on", "--only-binary=:all:", "--exclude-newer",
                    "brave-audit-acceptance-v2.md", "SEC-T676-11", "SEC-T676-14", "seven days before")
LINKS = {
    "implementation/PREREQUISITES.md": "docs/wiki/mcp-pin-bump-checklist.md",
    "docs/wiki/mcp-servers.md": "mcp-pin-bump-checklist",
    "implementation/knowledge/mcp/servers.yaml": "docs/wiki/mcp-pin-bump-checklist.md",
}


def brave_pin() -> str:
    """The pinned brave package@version of servers.yaml: the gate command must name exactly this one (SEC-T676-11)."""
    spec = re.search(r"@brave/brave-search-mcp-server@\d+\.\d+\.\d+", (ROOT / "implementation/knowledge/mcp/servers.yaml").read_text(encoding="utf-8"))
    assert spec, "brave pin not found in servers.yaml"
    return spec.group(0)


def gate_problems(text: str) -> list[str]:
    """The release gate command accepts exactly the five brave advisories, each with the artifact's expiry date and
    scoped to the pinned brave package (an unscoped `GHSA:DATE` is the old, global form and is refused)."""
    found = re.findall(r"--accept (GHSA-[a-z0-9-]+):(\d{4}-\d{2}-\d{2}):(\S+?)(?=[\s`]|$)", text)
    out = []
    if sorted(i for i, _, _ in found) != sorted(GHSA):
        out.append(f"the release gate accepts {sorted(i for i, _, _ in found)}, expected exactly {sorted(GHSA)}")
    if len(re.findall(r"--accept GHSA-(?!xxxx)", text)) != len(found):  # GHSA-xxxx-... is the syntax placeholder
        out.append("an --accept in the text lacks the :<package>@<version> scope")
    out += [f"{i} expires {d}, expected {EXPIRY}" for i, d, _ in found if d != EXPIRY]
    out += [f"{i} is scoped to {pkg}, expected {brave_pin()}" for i, _, pkg in found if pkg != brave_pin()]
    return out


def problems(text: str) -> list[str]:
    out = [f"missing id {i}" for i in IDS if i not in text]
    out += [f"missing phrase {p!r}" for p in REQUIRED_PHRASES if p not in text]
    if re.search(r"HOME=\$\(mktemp[^\n]*\$HOME/", text) or re.search(r"HOME=\$\(mktemp", text):
        out.append("the isolated opencode command expands $HOME in the calling shell (SEC-T676-01): use t=$(mktemp -d) first")
    out += gate_problems(text)
    for path in set(re.findall(r"`((?:scripts|ci|tests|implementation|docs)/[A-Za-z0-9_./*<>-]+)`", text)):
        if "*" in path or "<" in path or path.endswith("/"):
            continue
        if not (ROOT / path.rstrip(".,")).exists():
            out.append(f"referenced path does not exist: {path}")
    return out


def secret_findings(text: str) -> list[str]:
    patterns = (r"glpat-", r"ctx7sk-", r"ghp_", r"sk-[A-Za-z0-9]{10,}", r"Bearer ", r"(?i)authorization:", r"\b[0-9a-f]{32,}\b")
    return [p for p in patterns if re.search(p, text)]


class TestChecklist(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")

    def test_the_document_is_complete_and_its_paths_exist(self):
        self.assertEqual(problems(self.text), [])

    def test_it_is_linked_from_the_short_policies(self):
        for rel, needle in LINKS.items():
            with self.subTest(rel=rel):
                self.assertIn(needle, (ROOT / rel).read_text(encoding="utf-8"))

    def test_it_has_no_secret_looking_value(self):
        self.assertEqual(secret_findings(self.text), [])
        for artifact in (ROOT / "docs/artifacts/brave-audit-acceptance-v1.md", ROOT / "docs/artifacts/brave-audit-acceptance-v2.md"):
            self.assertEqual(secret_findings(artifact.read_text(encoding="utf-8")), [])

    def test_the_secret_check_catches_each_shape(self):
        for sample in ("glpat-abcdefghijklmnopqrst", "ctx7sk-0000", "ghp_" + "a" * 20, "Authorization: Bearer abc",
                       "Bearer ctx7", "authorization: x", "sk-" + "A" * 12, "0123456789abcdef" * 3):
            with self.subTest(sample=sample):
                self.assertTrue(secret_findings("text " + sample + " more"), sample)
        self.assertEqual(secret_findings("sha256:06d7adf3... GHSA-6qxp-vccf-f47h `Bearer`-less prose"), [])

    def test_the_acceptance_artifact_matches_the_gate_command_and_the_decision(self):
        artifact = (ROOT / "docs/artifacts/brave-audit-acceptance-v2.md").read_text(encoding="utf-8")
        self.assertEqual(gate_problems(artifact), [])
        for needle in GHSA + (EXPIRY, "Accept with conditions (Recommended)", "BRAVE_MCP_TRANSPORT=http", "GHSA-46jr-4wx8-v453",
                              "**Based on**", "devops-engineer"):
            self.assertIn(needle, artifact)
        pattern = r"--accept (GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}:\d{4}-\d{2}-\d{2}:\S+?)(?=[\s`]|$)"
        self.assertEqual(re.findall(pattern, artifact), re.findall(pattern, self.text))

    def test_the_acceptance_artifact_expiry_is_within_ninety_days_of_the_decision(self):
        """SEC-T676-11: the script refuses a date more than 90 days out; the recorded decision must respect the same bound."""
        import datetime as dt
        artifact = (ROOT / "docs/artifacts/brave-audit-acceptance-v2.md").read_text(encoding="utf-8")
        decision = dt.date.fromisoformat(re.search(r"\*\*Date\*\*: (\d{4}-\d{2}-\d{2})", artifact).group(1))
        expiry = dt.date.fromisoformat(EXPIRY)
        self.assertLessEqual((expiry - decision).days, 90)
        self.assertGreater(expiry, decision)

    def test_the_gate_command_names_the_current_brave_pin_and_the_script_accepts_it(self):
        """The documented command parses with the real parser and every package@version it names is a current pin."""
        import datetime as dt
        import importlib.util
        import sys
        spec = importlib.util.spec_from_file_location("audit_mcp_pins_chk", ROOT / "scripts" / "audit-mcp-pins.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["audit_mcp_pins_chk"] = mod
        spec.loader.exec_module(mod)
        specs = [m for m in re.findall(r"--accept (GHSA-(?!xxxx)\S+?(?=[\s`]|$))", self.text)]
        self.assertEqual(len(specs), len(GHSA))
        parsed = [mod.parse_accept(s) for s in specs]
        pins = mod.load_pins(mod.SERVERS_YAML)
        keyed = mod.check_acceptances(parsed, pins, parsed[0].until - dt.timedelta(days=30))
        self.assertEqual({k[0] for k in keyed}, set(GHSA))

    def test_mutation_an_unscoped_or_wrongly_scoped_gate_is_detected(self):
        unscoped = self.text.replace("--accept GHSA-rvq5-wwqv-78pq:2026-11-21:@brave/brave-search-mcp-server@2.1.4", "--accept GHSA-rvq5-wwqv-78pq:2026-11-21")
        self.assertNotEqual(unscoped, self.text)
        self.assertTrue(any("lacks the" in p for p in problems(unscoped)))
        stale = self.text.replace("GHSA-46jr-4wx8-v453:2026-11-21:@brave/brave-search-mcp-server@2.1.4", "GHSA-46jr-4wx8-v453:2026-11-21:@brave/brave-search-mcp-server@2.1.3")
        self.assertTrue(any("is scoped to" in p for p in problems(stale)))
        other = self.text.replace("GHSA-46jr-4wx8-v453:2026-11-21:@brave/brave-search-mcp-server@2.1.4", "GHSA-46jr-4wx8-v453:2026-11-21:left-pad@1.3.0")
        self.assertTrue(any("is scoped to" in p for p in problems(other)))

    def test_the_opencode_warning_and_the_safe_command_are_present(self):
        self.assertIn(WARNING, self.text)
        self.assertIn('t=$(mktemp -d); env -i PATH="$PATH" HOME="$t" XDG_CONFIG_HOME="$t/.config"', self.text)
        self.assertEqual(problems(self.text), [])

    def test_mutation_the_leaky_opencode_command_is_detected(self):
        bad = self.text.replace('t=$(mktemp -d); env -i PATH="$PATH" HOME="$t" XDG_CONFIG_HOME="$t/.config"',
                                'env -i PATH="$PATH" HOME=$(mktemp -d) XDG_CONFIG_HOME=$HOME/.config')
        self.assertNotEqual(bad, self.text)
        self.assertTrue(any("SEC-T676-01" in p for p in problems(bad)))

    def test_mutation_a_missing_warning_or_a_wider_gate_is_detected(self):
        self.assertTrue(any("missing phrase" in p for p in problems(self.text.replace(WARNING, "Be careful"))))
        wider = self.text.replace("--accept GHSA-rvq5-wwqv-78pq:2026-11-21", "--accept GHSA-rvq5-wwqv-78pq:2026-11-21 --accept GHSA-xxxx-yyyy-zzzz:2026-11-21")
        self.assertTrue(any("accepts" in p for p in problems(wider)))
        self.assertTrue(any("expires" in p for p in problems(self.text.replace("GHSA-46jr-4wx8-v453:2026-11-21", "GHSA-46jr-4wx8-v453:2027-01-01"))))

    def test_mutation_a_dropped_id_is_detected(self):
        self.assertIn("missing id SEC-T655-07", problems(self.text.replace("SEC-T655-07", "SEC-T655-0x")))

    def test_mutation_a_dead_path_is_detected(self):
        bad = self.text.replace("`ci/requirements-ci.in`", "`ci/requirements-cx.in`")
        self.assertNotEqual(bad, self.text)
        self.assertTrue(any("does not exist" in p for p in problems(bad)))

    def test_mutation_a_dropped_section_is_detected(self):
        self.assertTrue(problems(self.text.replace("One-time live checks", "Checks")))


if __name__ == "__main__":
    unittest.main()
