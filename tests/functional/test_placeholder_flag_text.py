"""T608 -- text pins for the placeholder-flag agent text (E-P1, E-O1, E-P2).

Implements `docs/artifacts/placeholder-flag-ruling-v3.md` §7 and the binding conditions V3-1, V3-3, V3-4,
V3-5 and V3-8 of `docs/artifacts/security-review-placeholder-flag-ruling-v3.md`. Pure text tests: no scanner,
no subprocess, no MCP SDK.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.frontmatter import parse_file  # noqa: E402
from tests._helpers.repo import implementation_root, knowledge_root  # noqa: E402

AGENTS = knowledge_root() / "agents"
SE_PATH = AGENTS / "poc-security-engineer.md"
OR_PATH = AGENTS / "poc-orchestrator.md"

SE_MIRRORS = (
    ".claude/agents/poc-security-engineer.md",
    ".cursor/agents/poc-security-engineer.mdc",
    ".gemini/agents/poc-security-engineer.md",
    ".github/agents/poc-security-engineer.agent.md",
    ".opencode/agents/poc-security-engineer.md",
    ".pi/agents/poc-security-engineer.md",
)
OR_MIRRORS = tuple(p.replace("poc-security-engineer", "poc-orchestrator") for p in SE_MIRRORS)

P1_HEAD = "- **Placeholder flags:** a scan hit is unresolved until a valid flag covers it or you classify it as a real secret."
P2_HEAD = "- **Scan blind spots:**"
O1_HEAD = "- **Placeholder flags**: when `@poc-security-engineer` reports an"
O1_BEFORE = "- **Other `SECURITY:LOW` findings**: record for debt handoff."

# Tools lists and the frozen F-8 / E1-b / E1-c texts (byte-identical to the T603/T604 state).
SE_TOOLS = ["read", "search", "mcp__security-audit__grep_content", "mcp__poc-security-audit__scan_secrets",
            "mcp__poc-security-audit__ref_containment", "web"]
OR_TOOLS = ["read", "search", "edit", "execute", "agent", "web", "todo", "mcp__gitlab", "mcp__memory",
            "mcp__sequential-thinking", "mcp__fetch"]
FROZEN = (
    "using the secret-scan tool whose output omits matched text, never a tool that prints matched lines.",
    "(reported as pushed only when a fetched remote-tracking ref contains the commit, otherwise as unknown and unconfirmed against the remote, with the time of the last fetch; an unpushed result is reported as unknown, and the secret is treated as exposed either way)",
    "A scan that did not complete (tool unavailable, error, timeout or `truncated`) is a blocker and the verdict is `FAIL`; it is never `PASS`. A clean scan means no match for the scan tool's fixed rule set only",
)


def _block(text: str, start: str, end: str | None) -> str:
    s = text.index(start)
    e = text.index(end, s + 1) if end else text.index("\n", s)
    return text[s:e]


def _p1(text: str) -> str:
    return _block(text, P1_HEAD, P2_HEAD)


def _o1(text: str) -> str:
    return _block(text, O1_HEAD, None)


class PlaceholderFlagTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.se = SE_PATH.read_text(encoding="utf-8")
        cls.orch = OR_PATH.read_text(encoding="utf-8")
        cls.p1 = _p1(cls.se)
        cls.o1 = _o1(cls.orch)

    # --- each After bullet occurs exactly once, in the right place -------------------------------------
    def test_after_bullets_occur_exactly_once(self):
        self.assertEqual(self.se.count(P1_HEAD), 1)
        self.assertEqual(self.se.count(P2_HEAD), 1)
        self.assertEqual(self.orch.count(O1_HEAD), 1)
        self.assertEqual(self.orch.count(O1_BEFORE), 1)

    def test_bullet_order(self):
        verdict = self.se.index("- End every scan with a verdict")
        self.assertLess(verdict, self.se.index(P1_HEAD))
        self.assertLess(self.se.index(P1_HEAD), self.se.index(P2_HEAD))
        self.assertEqual(self.orch.index(O1_BEFORE) + len(O1_BEFORE) + 1, self.orch.index(O1_HEAD))

    def test_e_p1_is_split_into_sub_bullets_with_each_pin_in_one_bullet(self):
        lines = self.p1.rstrip("\n").split("\n")
        self.assertEqual(lines[0], P1_HEAD + " An unresolved hit makes the verdict `FAIL`, and a flag never removes the hit from the report.")
        self.assertGreaterEqual(len(lines), 6)
        for sub in lines[1:]:
            self.assertTrue(sub.startswith("  - **"), sub[:40])
            self.assertLess(len(sub), 3500)
        # Every pinned phrase sits wholly inside one bullet (it cannot straddle a newline).
        for phrase in E_P1_PINS:
            self.assertEqual(self.p1.count(phrase), 1, phrase)
            self.assertEqual(sum(phrase in line for line in lines), 1, phrase)

    # --- v3 §7 pins ------------------------------------------------------------------------------------
    def test_e_p1_contains_pinned_phrases(self):
        for phrase in E_P1_PINS:
            self.assertEqual(self.p1.count(phrase), 1, phrase)
        for phrase in ("unresolved", "authenticates nowhere", "unverified by the reviewer"):
            self.assertIn(phrase, self.p1)

    def test_e_p1_negative_pin_ephemeral_local_instance(self):
        self.assertNotIn("ephemeral local instance", self.p1)
        # poc-orchestrator keeps its own, different use of the phrase (step 1 skip condition).
        self.assertIn("ephemeral local instance", self.orch)

    def test_e_o1_contains_pinned_phrases(self):
        for phrase in ("verbatim", "`[value omitted]`", "classic default value", "step 1 skip condition",
                       "`expired-at-handoff`", "never closes a hit that belongs to an open blocking finding"):
            self.assertEqual(self.o1.count(phrase), 1, phrase)

    # --- V3-1: unresolved hit has a progression route ---------------------------------------------------
    def test_v3_1_unresolved_hit_progression_control(self):
        for block in (self.p1, self.o1):
            self.assertIn("For progression control an unresolved hit is treated as an open blocking finding", block)
            self.assertIn("awaiting user: placeholder flag", block)
            self.assertIn("`blocked`", block)
            self.assertIn("continue, demo, evaluate or close", block)
            self.assertIn("start only when the hit is classified as a real secret or the user declines", block)
            self.assertIn("An unresolved hit left at the timebox, at escalation or at close becomes an open blocking finding", block)

    # --- V3-3: the modified-paths list ------------------------------------------------------------------
    def test_v3_3_modified_paths_definition_and_fail_closed(self):
        scope = "differ from `flag_commit` in committed, staged and working-tree state plus untracked files, with deletions and renames"
        self.assertEqual(self.p1.count(scope), 1)
        self.assertEqual(self.o1.count(scope), 1)
        self.assertIn("an unavailable or unstated list voids every flag (fail closed)", self.p1)
        self.assertIn("(if either list is unavailable, say so, and every flag is void)", self.o1)

    # --- V3-4: every register field is listed in E-O1 ---------------------------------------------------
    def test_v3_4_e_o1_names_every_register_field(self):
        for field in ("`flag-id`", "`rule_id`", "`path`", "`scope`", "`commit`", "`via`", "`hit_count`", "`class`",
                      "`flag_commit`", "`source`", "`status: active`", "`[value omitted]`"):
            self.assertIn(field, self.o1)
        self.assertIn("`hit_count`", self.o1)
        self.assertIn("`class`", self.o1)
        self.assertIn("the written reason", self.o1)
        self.assertIn("the user's message quoted verbatim", self.o1)

    # --- V3-5: criteria for "looks like a placeholder" --------------------------------------------------
    def test_v3_5_real_at_once_criteria(self):
        for block in (self.p1, self.o1):
            self.assertIn("only if it is key material", block)
            self.assertIn("A hit is a real secret at once", block)
            self.assertIn("a provider-token format for which the user has not stated a published vendor example value and its source", block)
            self.assertIn("or the user declines", block)
            self.assertIn("`user-attested`", block)
        self.assertIn("`private-key-header`, `pgp-private-key-block`", self.p1)
        self.assertIn("has a path shown as `<redacted-by-rule:…>`", self.p1)
        self.assertIn("has a redacted path", self.o1)

    # --- V3-7: the standing decision is NOT recorded here (Question 2 Option A is T609) -------------------
    def test_v3_7_no_standing_decision_text_yet(self):
        self.assertNotIn("template-ref", self.se)
        self.assertNotIn("standing decision", self.p1)
        self.assertIn("record it for debt handoff as `SECURITY:LOW`", self.p1)

    # --- V3-8 / E-P2 ------------------------------------------------------------------------------------
    def test_v3_8_e_p2_blind_spots_include_url_scheme_clause(self):
        p2 = _block(self.se, P2_HEAD, None)
        self.assertIn("or is shorter than three characters; a URL whose scheme is 32 or more characters long or in upper case; or a secret in a format", p2)
        for needle in ("A clean scan therefore excludes those values", "State this limit in every verdict",
                       "It does not make a skipped value safe and it cannot be flagged",
                       "a secret in a format the fixed rule table does not list"):
            self.assertEqual(p2.count(needle), 1, needle)
        self.assertNotIn("blocks", p2)

    # --- SEC-1: the branch-changed-paths list fails closed -----------------------------------------------
    def test_sec_1_branch_changed_paths_list_fails_closed(self):
        self.assertEqual(self.p1.count("and your brief lists the paths the reviewed branch changed against `develop` and the register path is not among them; if that list is unavailable or unstated, no flag exists"), 1)
        self.assertNotIn("otherwise no flag exists and every hit stays", self.p1)
        self.assertEqual(self.o1.count("(if either list is unavailable, say so, and every flag is void)"), 1)

    # --- SEC-2: more real-at-once cases; no "looks like a placeholder" wording ----------------------------
    def test_sec_2_real_at_once_cases_and_proposal_wording(self):
        name = "is a file-name hit for a name other than `.env.example`, `.env.sample` and `.env.template`"
        self.assertEqual(self.p1.count(name), 1)
        self.assertEqual(self.o1.count(name), 1)
        self.assertEqual(self.p1.count("is a hit whose line you have re-read and judge to be a real credential"), 1)
        self.assertEqual(self.o1.count("is a hit whose line the reviewer has re-read and judges to be a real credential"), 1)
        self.assertEqual(self.p1.count('"unresolved hit, proposed flag, unverified by the reviewer"'), 1)
        self.assertEqual(self.o1.count('"unresolved hit, proposed flag, unverified by the reviewer"'), 1)
        self.assertNotIn("looks like a placeholder", self.se)
        self.assertNotIn("looks like a placeholder", self.orch)
        self.assertNotIn("look like a placeholder", self.se)

    # --- SEC-3: provider-token rule ids listed once, and they are real scanner rule ids -------------------
    def test_sec_3_provider_token_rule_ids(self):
        listing = ("(the rules `aws-access-key-id`, `github-token`, `gitlab-token`, `slack-token`, `stripe-live-key`, "
                   "`google-api-key`, `github-fine-grained-pat`, `npm-token`, `sendgrid-api-key`, `sk-api-key` and `jwt`)")
        self.assertEqual(self.p1.count(listing), 1)
        self.assertEqual(self.o1.count(listing), 1)
        from implementation.runtime.security import poc_scan
        known = {rule_id for rule_id, _ in poc_scan.RULES}
        for rule_id in PROVIDER_RULE_IDS:
            self.assertIn(rule_id, known, rule_id)
            self.assertIn(f"`{rule_id}`", listing)

    # --- SEC-4: dummy-word limited to the two credential-assignment rules; E-P2 punctuation ---------------
    def test_sec_4_class_rules(self):
        self.assertEqual(self.p1.count("apply only to scope `worktree`; `dummy-word` applies only to the rules `credential-assignment` and `unquoted-credential-assignment`, and `repeated-char` only to those two rules and `bearer-token`"), 1)
        self.assertNotIn("`unquoted-credential-assignment` and `bearer-token`; re-read", self.p1)

    # --- SEC-5: authority, register, incomplete scan, progression wording ------------------------------
    def test_sec_5_authority_and_register_pins(self):
        self.assertEqual(self.p1.count("Only the user creates a flag"), 1)
        self.assertEqual(self.p1.count("you never create, widen, renew or revive one"), 1)
        self.assertEqual(self.o1.count("The orchestrator never creates one"), 1)
        self.assertEqual(self.o1.count("A register version counts only once it is on `develop` through the normal branch and merge-request flow"), 1)
        self.assertEqual(self.o1.count("never makes an incomplete scan pass"), 1)
        self.assertEqual(self.o1.count("a local instance included"), 1)
        self.assertEqual(self.p1.count("report it to the PoC orchestrator as a blocker"), 1)

    # --- unchanged texts --------------------------------------------------------------------------------
    def test_f8_e1b_e1c_after_texts_still_exactly_once(self):
        for after in FROZEN:
            self.assertEqual(self.se.count(after), 1, after[:40])
        self.assertIn("The PoC orchestrator will handle escalation", self.se)

    def test_tools_lists_byte_unchanged(self):
        se_fm, _ = parse_file(SE_PATH)
        or_fm, _ = parse_file(OR_PATH)
        self.assertEqual(se_fm["tools"], SE_TOOLS)
        self.assertEqual(or_fm["tools"], OR_TOOLS)
        self.assertEqual(se_fm["maturity"], "stable")
        self.assertEqual(or_fm["maturity"], "stable")

    # --- projection parity ------------------------------------------------------------------------------
    def test_mirrors_carry_the_same_bullets(self):
        root = implementation_root()
        for rel in SE_MIRRORS:
            text = (root / rel).read_text(encoding="utf-8")
            for line in self.p1.rstrip("\n").split("\n"):
                self.assertIn(line, text, rel)
            self.assertIn(_block(self.se, P2_HEAD, None), text, rel)
        for rel in OR_MIRRORS:
            text = (root / rel).read_text(encoding="utf-8")
            self.assertIn(self.o1, text, rel)


PROVIDER_RULE_IDS = ("aws-access-key-id", "github-token", "gitlab-token", "slack-token", "stripe-live-key",
                     "google-api-key", "github-fine-grained-pat", "npm-token", "sendgrid-api-key", "sk-api-key", "jwt")

E_P1_PINS = (
    "never removes", "classic default value", "exact path and commit sha",
    "`refs/remotes/origin/develop`", "`[value omitted]`", "whatever the flags say", "never drop a flagged hit",
    "`SECURITY:LOW`", "a local instance included",
)


if __name__ == "__main__":
    unittest.main()
