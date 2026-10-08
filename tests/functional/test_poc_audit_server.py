"""T603 -- tests for the `poc-security-audit` MCP server implementing
`docs/artifacts/poc-security-engineer-tool-scoping-v2.md` (§3 contract, §6.2 test list).

Tiers (mirrors `test_audit_server.py`):

1. Behaviour tests against real fixture git repositories (needs only `git`).
2. Static AST / registry / agent-grant / text tests (no subprocess, no MCP SDK).
3. A live stdio smoke test (needs the optional `mcp` SDK; skips when absent).

Secret-shaped strings are assembled at run time so this file never contains a literal
that a scanner (including this server) would flag.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from tests._helpers.frontmatter import parse_file  # noqa: E402
from tests._helpers.repo import implementation_root, knowledge_root  # noqa: E402

from implementation.runtime.security import git_executor, poc_scan  # noqa: E402
from implementation.runtime.security.git_executor import Deadline, git_env, run_git  # noqa: E402
from implementation.runtime.security.poc_scan import PocAuditConfig  # noqa: E402

PKG = implementation_root() / "runtime" / "security"
SERVER_PY = PKG / "poc_audit_server.py"
SCAN_PY = PKG / "poc_scan.py"
EXEC_PY = PKG / "git_executor.py"
SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"
SOURCE_AGENT = knowledge_root() / "agents" / "poc-security-engineer.md"
PROJECTED_AGENT = implementation_root() / ".claude" / "agents" / "poc-security-engineer.md"

# Secret-shaped samples, one per rule, assembled at run time.
AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
GHP = "ghp_" + "a1B2c3D4e5" * 4
SAMPLES = {
    "private-key-header": "-----BEGIN RSA " + "PRIVATE KEY-----",
    "aws-access-key-id": "id = " + AWS,
    "github-token": "t = " + GHP,
    "gitlab-token": "t = glpat-" + "A" * 24,
    "slack-token": "t = xoxb-" + "1234567890" * 2,
    "stripe-live-key": "k = sk_live_" + "a" * 20,
    "google-api-key": "k = AIza" + "B" * 35,
    "bearer-token": "Authorization: Bearer " + "Z" * 24,
    "credential-assignment": 'db_password = "hunter2hunter2"',
    "pgp-private-key-block": "-----BEGIN PGP " + "PRIVATE KEY BLOCK-----",
    "github-fine-grained-pat": "t = github_pat_" + "A1b2C3d4E5" * 3,
    "sk-api-key": "k = sk-ant-" + "a1B2" * 6,
    "url-embedded-credentials": "u = postgres://admin:" + "s3cretpw" + "@db.example.invalid/x",
}
CREDENTIAL_VARIANTS = (
    '"password": "hunter2hunter2"', "api-key: 'abcdefgh1234'", "pwd = 'abcdefgh'",
    'access_key = "abcdefgh12"', 'private-key: "abcdefgh12"', "'client_secret': 'abcdefgh12'",
)
PLACEHOLDERS = (
    'password = "${DB_PASSWORD}"', "token = '<set-me>'", '"password": "${PW}"', "api-key: '{{ key }}'",
    "u = postgres://user:${PASS}@host/db", "u = postgres://user:<pw>@host/db",
    "u = http://localhost:8080/x", "see risk-assessment-for-the-quarterly-planning-doc",
    "task-management-planning-document-for-everyone",
)


def _which_git() -> str:
    return shutil.which("git") or "git"


def _git(cwd: Path, *args: str) -> str:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": str(cwd), "GIT_CONFIG_GLOBAL": "/dev/null",
           "GIT_CONFIG_NOSYSTEM": "1"}
    out = subprocess.run(
        ["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args],
        check=True, capture_output=True, text=True, env=env)
    return out.stdout.strip()


class RepoCase(unittest.TestCase):
    """Base: a temp directory acting as `allowed_root` plus a helper to make repos."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()
        self.cfg = PocAuditConfig(allowed_root=self.base)

    def make_repo(self, name: str = "repo", files: dict[str, str] | None = None) -> Path:
        root = self.base / name
        root.mkdir()
        _git(root, "init", "-q", "-b", "main")
        for rel, text in (files or {"README.md": "hello\n"}).items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text)
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "init")
        return root

    def commit_file(self, root: Path, rel: str, text: str) -> str:
        (root / rel).write_text(text)
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", f"add {len(rel)}")
        return _git(root, "rev-parse", "HEAD")

    def scan(self, root: Path, scope: str, rev_range: str | None = None, cfg=None) -> dict:
        return poc_scan.scan_secrets(str(root), scope, rev_range, cfg or self.cfg)

    def capture(self):
        calls: list[list[str]] = []
        real = poc_scan.run_git

        def spy(argv, deadline, max_bytes, ok_codes=(0,)):
            calls.append(list(argv))
            return real(argv, deadline, max_bytes, ok_codes)

        return calls, mock.patch.object(poc_scan, "run_git", spy)


EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
PREFIX = [f"--attr-source={EMPTY_TREE}",
          "-c", "core.fsmonitor=false", "-c", "core.pager=cat", "-c", "core.hooksPath=/dev/null",
          "-c", "color.ui=false", "-c", "color.grep=false",
          "-c", "log.showSignature=false", "-c", "gpg.program=/bin/false"]
SUB = 3 + len(PREFIX)  # index of the git subcommand in an argv


class ArgvTests(RepoCase):
    def test_every_argv_starts_with_hardening_prefix_and_scope_shapes(self):
        root = self.make_repo()
        _git(root, "tag", "-a", "v1", "-m", "t")
        rid, pat = poc_scan.RULES[0]
        expected_grep = {
            "worktree": ["grep", "--no-color", "--untracked", "--no-exclude-standard", "-a", "-n",
                         "-z", "-E", "-e", pat, "--"],
            "index": ["grep", "--no-color", "--cached", "-a", "-n", "-z", "-E", "-e", pat, "--"],
        }
        for scope, grep in expected_grep.items():
            calls, patch = self.capture()
            with patch:
                self.scan(root, scope)
            for argv in calls:
                self.assertEqual(argv[:3], ["git", "-C", str(root)])
                self.assertEqual(argv[3:SUB], PREFIX)
            self.assertEqual(calls[1][SUB:], grep)
            self.assertEqual(calls[0][SUB:], ["rev-parse", "--show-toplevel"])

    def test_history_log_argv_has_no_textconv_no_ext_diff_and_only_percent_h(self):
        root = self.make_repo()
        calls, patch = self.capture()
        with patch:
            self.scan(root, "history")
        logs = [a for a in calls if a[SUB] == "log"]
        self.assertEqual(len(logs), len(poc_scan.RULES), "one git log per rule (F-11)")
        for argv in logs:
            self.assertEqual(argv[:SUB], ["git", "-C", str(root), *PREFIX])
            self.assertIn("--no-textconv", argv)
            self.assertIn("--no-ext-diff", argv)
            self.assertIn("--no-show-signature", argv)
            self.assertIn("--text", argv)
            self.assertIn("--format=%H", argv)
            self.assertEqual(argv[-1], "--")
            self.assertEqual(sum(a.startswith("-G") for a in argv), 1)
            self.assertFalse(any(a in ("-p", "--patch", "%s", "%b") for a in argv))

    def test_ref_containment_exact_argv(self):
        root = self.make_repo()
        sha = _git(root, "rev-parse", "HEAD")
        calls, patch = self.capture()
        with patch:
            poc_scan.ref_containment(str(root), sha, self.cfg)
        self.assertEqual(calls[1], ["git", "-C", str(root), *PREFIX, "for-each-ref", "--contains", sha,
                                    f"--count={self.cfg.max_refs + 1}", "--format=%(refname)",
                                    "refs/remotes", "refs/tags", "refs/heads"])

    def test_malicious_commit_and_range_never_reach_a_process(self):
        root = self.make_repo()
        calls, patch = self.capture()
        with patch:
            for bad in ("abc; touch x", "--upload-pack=x", "-1", "A" * 40, "g" * 40, "a" * 39):
                res = poc_scan.ref_containment(str(root), bad, self.cfg)
                self.assertEqual(res["errors"], ["bad_rev"])
                self.assertIsNone(res["commit"])
            for bad in ("-x", "--output=/tmp/x", "main; touch x", "a..b..c", "$(id)", "x" * 200, ""):
                res = self.scan(root, "history", bad)
                self.assertEqual(res["errors"], ["bad_rev"], bad)
        self.assertEqual(calls, [])

    def test_rev_range_sits_after_end_of_options_and_never_reaches_grep(self):
        root = self.make_repo()
        calls, patch = self.capture()
        with patch:
            res = self.scan(root, "history", "main")
        self.assertEqual(res["errors"], [])
        for argv in calls[1:]:
            sub = argv[SUB]
            if sub == "grep":
                self.assertNotIn("main", argv[SUB + 1:], "range string must never reach git grep")
            if sub in ("rev-list", "log"):
                at = argv.index("--end-of-options")
                self.assertEqual(argv[at + 1:at + 3], ["main", "--"])

    def test_rev_range_only_valid_for_history(self):
        root = self.make_repo()
        for scope in ("worktree", "index", "stashes", "tracked_names"):
            self.assertEqual(self.scan(root, scope, "main")["errors"], ["bad_scope"])
        for scope in ("bogus", "", None, "history;ls"):
            self.assertEqual(self.scan(root, scope)["errors"], ["bad_scope"])
        first = _git(root, "rev-parse", "--short=7", "HEAD")
        self.commit_file(root, "second.txt", AWS + "\n")
        last = _git(root, "rev-parse", "--short=7", "HEAD")
        res = self.scan(root, "history", f"{first}..{last}")
        self.assertEqual(res["errors"], [])
        self.assertTrue(res["hits"], "a non-empty range must actually be scanned")


class EnvironmentTests(unittest.TestCase):
    def test_env_is_exactly_the_listed_set(self):
        self.assertEqual(set(git_env()), {"PATH", "HOME", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL",
                                          "GIT_TERMINAL_PROMPT", "LC_ALL"})
        env = git_env()
        self.assertEqual((env["HOME"], env["GIT_CONFIG_NOSYSTEM"], env["GIT_CONFIG_GLOBAL"],
                          env["GIT_TERMINAL_PROMPT"], env["LC_ALL"]),
                         ("/nonexistent", "1", "/dev/null", "0", "C"))

    def test_subprocess_really_receives_only_that_environment(self):
        with mock.patch.dict(os.environ, {"T603_CANARY": "leak", "GIT_DIR": "/elsewhere"}):
            res = run_git(["/usr/bin/env"], Deadline(10), 100_000)
        got = dict(line.split("=", 1) for line in res.stdout.decode().splitlines())
        self.assertEqual(set(got), set(git_env()))
        self.assertNotIn("T603_CANARY", got)


class ConfigIsolationTests(RepoCase):
    """F-1: a core.fsmonitor command planted in the repository's own config must not run."""

    def _planted(self) -> tuple[Path, Path]:
        root = self.make_repo(files={"a.txt": "nothing\n"})
        marker = self.base / "pwned-marker"
        with open(root / ".git" / "config", "a") as fh:
            fh.write(f"[core]\n\tfsmonitor = touch {marker} #\n")
        return root, marker

    def test_plain_git_grep_does_run_the_planted_command(self):
        """Control: the plant works against un-hardened git, so the next test can fail."""
        root, marker = self._planted()
        env = {"PATH": os.environ["PATH"], "HOME": "/nonexistent", "GIT_CONFIG_GLOBAL": "/dev/null",
               "GIT_CONFIG_NOSYSTEM": "1"}
        subprocess.run(["git", "-C", str(root), "grep", "-e", "nothing"], env=env,
                       capture_output=True, check=False)
        self.assertTrue(marker.exists(), "planting technique no longer triggers fsmonitor")

    def test_hardened_scans_never_run_the_planted_command(self):
        root, marker = self._planted()
        for scope in poc_scan.SCOPES:
            res = self.scan(root, scope)
            self.assertEqual(res["errors"], [], scope)
        head = _git(root, "rev-parse", "HEAD")
        res = poc_scan.ref_containment(str(root), head, self.cfg)
        self.assertEqual((res["errors"], res["local_branches"]), ([], ["refs/heads/main"]))
        self.assertFalse(marker.exists(), "planted core.fsmonitor command ran under a scan")

    def test_unhardened_variant_is_detected_by_the_same_probe(self):
        """Sensitivity: with the hardening prefix removed, the probe sees the marker."""
        root, marker = self._planted()
        with mock.patch.object(git_executor, "HARDENING", ()):
            self.scan(root, "index")  # --cached / ls-files consult fsmonitor; --untracked does not
        self.assertTrue(marker.exists(), "probe would not catch an un-hardened executor")


class ToplevelTests(RepoCase):
    def test_subdirectory_of_repo_rejected(self):
        root = self.make_repo(files={"sub/f.txt": "x\n"})
        self.assertEqual(self.scan(root / "sub", "worktree")["errors"], ["not_a_toplevel"])
        sha = _git(root, "rev-parse", "HEAD")
        self.assertEqual(poc_scan.ref_containment(str(root / "sub"), sha, self.cfg)["errors"],
                         ["not_a_toplevel"])

    def test_non_repository_rejected(self):
        plain = self.base / "plain"
        plain.mkdir()
        self.assertEqual(self.scan(plain, "index")["errors"], ["not_a_toplevel"])

    def test_outside_allowed_root_and_odd_values_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            other_root = Path(other).resolve()
            _git(other_root, "init", "-q")
            self.assertEqual(self.scan(other_root, "index")["errors"], ["not_a_toplevel"])
        for bad in ("", "/nonexistent-t603", "a\0b", None):
            res = poc_scan.scan_secrets(bad, "index", None, self.cfg)
            self.assertEqual(res["errors"], ["not_a_toplevel"])

    def test_toplevel_repo_accepted(self):
        root = self.make_repo()
        res = self.scan(root, "index")
        self.assertEqual((res["errors"], res["complete"]), ([], True))


class ParsingTests(RepoCase):
    def test_z_layout_against_installed_git(self):
        root = self.make_repo(files={"we:12:ird.txt": "a\nX needle\n"})
        out = subprocess.run(["git", "-C", str(root), "grep", "-z", "-n", "-e", "needle"],
                             capture_output=True, check=True).stdout
        self.assertEqual(out, b"we:12:ird.txt\x002\x00X needle\n")
        sha = _git(root, "rev-parse", "HEAD")
        out = subprocess.run(["git", "-C", str(root), "grep", "-z", "-n", "-e", "needle", sha, "--"],
                             capture_output=True, check=True).stdout
        self.assertEqual(out, sha.encode() + b":we:12:ird.txt\x002\x00X needle\n")
        self.assertEqual(poc_scan.parse_grep_z(b"a b\x007\x00text\nnext\x001\x00t\n"),
                         ([(b"a b", 7), (b"next", 1)], False))
        self.assertEqual(poc_scan.parse_grep_z(b"cut\x007\x00par"), ([], True))
        self.assertEqual(poc_scan.parse_grep_z(b""), ([], False))
        # ANSI-coloured output (not -z shaped) is malformed, not "no hits".
        self.assertEqual(poc_scan.parse_grep_z(b"\x1b[35mf.txt\x1b[m\x1b[36m:\x1b[m1:x\n")[1], True)

    def test_awkward_names_and_secret_text_never_returned(self):
        files = {"we:12:ird.txt": f"x\n{SAMPLES['aws-access-key-id']}\n",
                 "has space.txt": f"{SAMPLES['github-token']}\n",
                 "new\nline.txt": f"{SAMPLES['stripe-live-key']}\n"}
        root = self.make_repo(files=files)
        for scope in ("worktree", "index"):
            res = self.scan(root, scope)
            self.assertEqual(res["errors"], [])
            by_path = {h["path_or_redacted"]: h for h in res["hits"]}
            self.assertEqual(by_path["we:12:ird.txt"]["line"], 2)
            self.assertEqual(by_path["we:12:ird.txt"]["rule_id"], "aws-access-key-id")
            self.assertEqual(by_path["has space.txt"]["line"], 1)
            self.assertEqual(by_path["new\nline.txt"]["rule_id"], "stripe-live-key")
            dump = json.dumps(res)
            for secret in (AWS, GHP, "sk_live_"):
                self.assertNotIn(secret, dump)
            self.assertNotIn("text", {k for h in res["hits"] for k in h})

    def test_every_rule_matches_in_git_and_is_counted(self):
        root = self.make_repo(files={f"{i}.txt": s + "\n" for i, s in enumerate(SAMPLES.values())})
        res = self.scan(root, "index")
        self.assertEqual(res["errors"], [])
        self.assertEqual(set(res["counts"]), {rid for rid, _ in poc_scan.RULES})
        self.assertEqual(res["rules_version"], poc_scan.RULES_VERSION)
        self.assertEqual(set(SAMPLES), {rid for rid, _ in poc_scan.RULES})

    def test_credential_keyword_variants_all_match(self):
        root = self.make_repo(files={f"v{i}.txt": v + "\n" for i, v in enumerate(CREDENTIAL_VARIANTS)})
        res = self.scan(root, "index")
        self.assertEqual(res["counts"], {"credential-assignment": len(CREDENTIAL_VARIANTS)})

    def test_placeholders_and_clean_repo_give_no_hits(self):
        root = self.make_repo(files={f"p{i}.txt": v + "\n" for i, v in enumerate(PLACEHOLDERS)})
        res = self.scan(root, "worktree")
        self.assertEqual((res["hits"], res["complete"]), ([], True))
        root = self.make_repo("r2", files={"c.txt": 'password = "${DB_PASSWORD}"\ntoken = "<set-me>"\n'})
        res = self.scan(root, "worktree")
        self.assertEqual((res["hits"], res["complete"]), ([], True))

    def test_worktree_covers_untracked_and_ignored(self):
        root = self.make_repo(files={".gitignore": "ign.txt\n"})
        (root / "ign.txt").write_text(AWS + "\n")
        (root / "new.txt").write_text(GHP + "\n")
        paths = {h["path_or_redacted"] for h in self.scan(root, "worktree")["hits"]}
        self.assertEqual(paths, {"ign.txt", "new.txt"})
        self.assertEqual(self.scan(root, "index")["hits"], [])

    def test_tracked_names_allowlist_names_only(self):
        root = self.make_repo(files={".env": "A=1\n", ".env.local": "B=2\n", "x/id_rsa": "k\n",
                                     "c.pem": "p\n", "ok.txt": "fine\n", "dir/secrets.yaml": "s\n"})
        res = self.scan(root, "tracked_names")
        self.assertEqual({h["path_or_redacted"] for h in res["hits"]},
                         {".env", ".env.local", "x/id_rsa", "c.pem", "dir/secrets.yaml"})
        self.assertEqual({h["rule_id"] for h in res["hits"]}, {poc_scan.TRACKED_NAME_RULE})
        self.assertNotIn("A=1", json.dumps(res))


class RedactionTests(RepoCase):
    def test_path_branch_and_tag_names_are_redacted(self):
        secret_name = f"{AWS}.txt"
        root = self.make_repo(files={secret_name: AWS + "\n", "k.txt": AWS + "\n"})
        branch, tag = GHP, "xoxb-" + "1234567890" * 2
        _git(root, "branch", branch)
        _git(root, "tag", tag)
        for scope in ("index", "tracked_names"):
            dump = json.dumps(self.scan(root, scope))
            self.assertNotIn(AWS, dump)
        idx = self.scan(root, "index")
        redacted = [h for h in idx["hits"] if h["path_or_redacted"].startswith("<redacted-by-rule:")]
        self.assertEqual(redacted[0]["path_or_redacted"], "<redacted-by-rule:aws-access-key-id>")
        self.assertEqual(redacted[0]["path_index"], 1)
        hist = self.scan(root, "history")
        self.assertNotIn(GHP, json.dumps(hist))
        self.assertNotIn(tag, json.dumps(hist))
        self.assertIn("<redacted-by-rule:github-token>", {h.get("ref") for h in hist["hits"]})
        sha = _git(root, "rev-parse", "HEAD")
        out = poc_scan.ref_containment(str(root), sha, self.cfg)
        self.assertTrue(any(b.startswith("<redacted-by-rule:github-token>") for b in out["local_branches"]))
        self.assertTrue(any(t.startswith("<redacted-by-rule:slack-token>") for t in out["tags"]))
        dump = json.dumps(out)
        self.assertNotIn(GHP, dump)
        self.assertNotIn("xoxb-", dump)

    def test_redact_name_helper(self):
        self.assertEqual(poc_scan.redact_name("src/app.py"), ("src/app.py", None))
        self.assertEqual(poc_scan.redact_name(AWS)[1], "aws-access-key-id")


class NoLeakTests(RepoCase):
    def _assert_clean(self, res: dict):
        dump = json.dumps(res)
        for needle in ("fatal", "error:", "usage:", "bad revision", "unknown revision", "-c core.",
                       "fsmonitor", "--end-of-options", "git -C"):
            self.assertNotIn(needle, dump)
        for key in ("stderr", "argv", "stdout"):
            self.assertNotIn(key, res)

    def test_failing_git_returns_code_only(self):
        root = self.make_repo()
        res = self.scan(root, "history", "1234567..abcdef0")
        self.assertEqual(res["errors"], ["git_failed"])
        self.assertFalse(res["complete"])
        self._assert_clean(res)
        res = poc_scan.ref_containment(str(root), "0" * 40, self.cfg)
        self.assertEqual(res["errors"], ["git_failed"])
        self.assertEqual(res["pushed"], "unknown")
        self._assert_clean(res)

    def _fake_git(self, body: str) -> Path:
        d = self.base / "fakebin"
        d.mkdir(exist_ok=True)
        script = d / "git"
        script.write_text("#!/bin/sh\n" + body)
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return d

    def test_timeout_path_returns_no_stderr_and_kills_process(self):
        root = self.make_repo()
        fake = self._fake_git("echo 'fatal: leaked " + AWS + "' >&2\nsleep 30\n")
        cfg = PocAuditConfig(allowed_root=self.base, deadline_seconds=0.6)
        t0 = time.monotonic()
        with mock.patch.dict(os.environ, {"PATH": f"{fake}:{os.environ['PATH']}"}):
            res = poc_scan.scan_secrets(str(root), "index", None, cfg)
        self.assertLess(time.monotonic() - t0, 25)
        self.assertEqual(res["errors"], ["timeout"])
        self.assertTrue(res["truncated"])
        self.assertFalse(res["complete"])
        self.assertNotIn(AWS, json.dumps(res))
        self._assert_clean(res)

    def test_git_missing_is_a_code(self):
        root = self.make_repo()
        with mock.patch.dict(os.environ, {"PATH": str(self.base / "empty")}):
            res = poc_scan.scan_secrets(str(root), "index", None, self.cfg)
        self.assertEqual(res["errors"], ["git_missing"])
        self._assert_clean(res)


class TriStateTests(RepoCase):
    def test_pushed_true_or_unknown_never_false_and_fetch_time(self):
        origin = self.make_repo("origin")
        clone = self.base / "clone"
        _git(self.base, "clone", "-q", str(origin), str(clone))
        pushed_sha = _git(clone, "rev-parse", "HEAD")
        res = poc_scan.ref_containment(str(clone), pushed_sha, self.cfg)
        self.assertIs(res["pushed"], True)
        self.assertTrue(res["remote_refs"])
        self.assertTrue(res["as_of_last_fetch"])
        self.assertTrue(res["complete"])
        # last_fetch_time follows FETCH_HEAD.
        fh = clone / ".git" / "FETCH_HEAD"
        _git(clone, "fetch", "-q")
        os.utime(fh, (1_700_000_000, 1_700_000_000))
        res = poc_scan.ref_containment(str(clone), pushed_sha, self.cfg)
        self.assertEqual(res["last_fetch_time"], "2023-11-14T22:13:20+00:00")
        fh.unlink()
        res = poc_scan.ref_containment(str(clone), pushed_sha, self.cfg)
        self.assertIsNone(res["last_fetch_time"])
        # Unpushed commit: "unknown", never False.
        local_sha = self.commit_file(clone, "new.txt", "local only\n")
        res = poc_scan.ref_containment(str(clone), local_sha, self.cfg)
        self.assertEqual(res["pushed"], "unknown")
        self.assertIsNot(res["pushed"], False)
        self.assertEqual(res["remote_refs"], [])
        self.assertTrue(res["local_branches"])

    def test_pushed_is_never_false_in_any_result(self):
        root = self.make_repo()
        for commit in (_git(root, "rev-parse", "HEAD"), "0" * 40, "nope"):
            self.assertIsNot(poc_scan.ref_containment(str(root), commit, self.cfg)["pushed"], False)


class BoundsTests(RepoCase):
    def test_stdout_is_read_through_a_bound(self):
        t0 = time.monotonic()
        res = run_git([sys.executable, "-c", "import sys; sys.stdout.write('x' * 50_000_000)"],
                      Deadline(20), max_bytes=1000)
        self.assertEqual((len(res.stdout), res.truncated, res.error), (1000, True, None))
        self.assertLess(time.monotonic() - t0, 40)

    def test_deadline_is_aggregate_across_calls(self):
        deadline = Deadline(2.0)
        t0 = time.monotonic()
        first = run_git(["sleep", "1.2"], deadline, 100)
        second = run_git(["sleep", "1.2"], deadline, 100)
        third = run_git(["sleep", "1.2"], deadline, 100)
        self.assertIsNone(first.error)
        self.assertEqual((second.error, third.error), ("timeout", "timeout"))
        self.assertLess(time.monotonic() - t0, 15)

    def test_deadline_enforced_across_scan_loop_iterations(self):
        root = self.make_repo()
        d = self.base / "slowbin"
        d.mkdir()
        (d / "git").write_text(f"#!/bin/sh\nsleep 0.3\nexec {_which_git()} \"$@\"\n")
        (d / "git").chmod(0o755)
        cfg = PocAuditConfig(allowed_root=self.base, deadline_seconds=1.2)
        t0 = time.monotonic()
        with mock.patch.dict(os.environ, {"PATH": f"{d}:{os.environ['PATH']}"}):
            res = poc_scan.scan_secrets(str(root), "history", None, cfg)
        self.assertLess(time.monotonic() - t0, 25)
        self.assertIn("timeout", res["errors"])
        self.assertEqual((res["truncated"], res["complete"]), (True, False))

    def test_ref_and_stash_and_hit_caps_flag_truncation(self):
        root = self.make_repo(files={"s.txt": AWS + "\n", "t.txt": GHP + "\n"})
        for i in range(6):
            _git(root, "branch", f"b{i}")
        cfg = PocAuditConfig(allowed_root=self.base, max_refs=3)
        res = self.scan(root, "history", cfg=cfg)
        self.assertEqual((res["truncated"], res["complete"]), (True, False))
        for i in range(3):
            (root / "s.txt").write_text(f"{AWS}\nchange {i}\n")
            _git(root, "stash", "-q")
        res = self.scan(root, "stashes", cfg=PocAuditConfig(allowed_root=self.base, max_stashes=1))
        self.assertEqual((res["truncated"], res["complete"]), (True, False))
        self.assertEqual({h["commit"] for h in res["hits"]}.__len__(), 1)
        res = self.scan(root, "index", cfg=PocAuditConfig(allowed_root=self.base, max_hits=1))
        self.assertEqual((len(res["hits"]), res["truncated"], res["complete"]), (1, True, False))

    def test_output_byte_cap_flags_truncation(self):
        root = self.make_repo(files={f"f{i}.txt": AWS + "\n" for i in range(40)})
        res = self.scan(root, "index", cfg=PocAuditConfig(allowed_root=self.base, max_bytes=100))
        self.assertEqual((res["truncated"], res["complete"]), (True, False))


class ScopeTests(RepoCase):
    def test_stashes_found(self):
        root = self.make_repo(files={"s.txt": "clean\n"})
        (root / "s.txt").write_text(AWS + "\n")
        _git(root, "stash", "-q")
        res = self.scan(root, "stashes")
        self.assertEqual([h["rule_id"] for h in res["hits"]], ["aws-access-key-id"])
        self.assertEqual(self.scan(root, "worktree")["hits"], [])

    def test_no_stash_is_clean_not_an_error(self):
        res = self.scan(self.make_repo(), "stashes")
        self.assertEqual((res["errors"], res["complete"]), ([], True))

    def test_history_tip_and_removed_secret_found_by_right_mechanism(self):
        root = self.make_repo(files={"a.txt": "clean\n"})
        removed = self.commit_file(root, "old.txt", AWS + "\n")
        _git(root, "rm", "-q", "old.txt")
        _git(root, "commit", "-q", "-m", "remove")
        removal = _git(root, "rev-parse", "HEAD")
        tip = self.commit_file(root, "b.txt", GHP + "\n")
        res = self.scan(root, "history")
        self.assertEqual(res["errors"], [])
        tips = [h for h in res["hits"] if h.get("via") != "log"]
        logs = [h for h in res["hits"] if h.get("via") == "log"]
        self.assertEqual([(h["path_or_redacted"], h["commit"]) for h in tips], [("b.txt", tip)])
        self.assertEqual({(h["rule_id"], h["commit"]) for h in logs},
                         {("aws-access-key-id", removed), ("aws-access-key-id", removal),
                          ("github-token", tip)})
        # the removed secret is NOT visible at any tip: only `git log -G` supplies it.
        self.assertFalse([h for h in tips if h["rule_id"] == "aws-access-key-id"])
        self.assertNotIn(AWS, json.dumps(res))

    def test_reflog_only_secret_is_an_expected_miss(self):
        root = self.make_repo()
        lost = self.commit_file(root, "gone.txt", AWS + "\n")
        _git(root, "reset", "-q", "--hard", "HEAD~1")
        self.assertEqual(_git(root, "cat-file", "-t", lost), "commit")
        res = self.scan(root, "history")
        self.assertEqual((res["hits"], res["complete"]), ([], True))  # documented limit R-3

    def test_rev_range_enumerates_commits(self):
        root = self.make_repo()
        c1 = self.commit_file(root, "k.txt", AWS + "\n")
        res = self.scan(root, "history", "main")
        self.assertIn(c1, {h["commit"] for h in res["hits"]})


class FollowUpHardeningTests(RepoCase):
    """Security-review follow-up (P-1..P-12)."""

    def _fake_git(self, body: str) -> str:
        d = self.base / "fakebin2"
        d.mkdir(exist_ok=True)
        (d / "git").write_text("#!/bin/sh\n" + body)
        (d / "git").chmod(0o755)
        return f"{d}:{os.environ['PATH']}"

    # -- P-1: signature program (did NOT reproduce on git 2.43.0; defence in depth) ----
    def test_planted_gpg_program_never_runs_during_scans(self):
        root = self.make_repo(files={"a.txt": AWS + "\n"})
        marker = self.base / "gpg-marker"
        prog = self.base / "fake-gpg.sh"
        prog.write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
        prog.chmod(0o755)
        with open(root / ".git" / "config", "a") as fh:
            fh.write(f"[gpg]\n\tprogram = {prog}\n[log]\n\tshowSignature = true\n")
        tree = _git(root, "rev-parse", "HEAD^{tree}")
        parent = _git(root, "rev-parse", "HEAD")
        raw = (f"tree {tree}\nparent {parent}\nauthor a <a@e.invalid> 1700000000 +0000\n"
               "committer a <a@e.invalid> 1700000000 +0000\n"
               "gpgsig -----BEGIN PGP SIGNATURE-----\n \n abcd\n -----END PGP SIGNATURE-----\n\nsigned\n")
        env = {"PATH": os.environ["PATH"], "HOME": str(self.base), "GIT_CONFIG_GLOBAL": "/dev/null"}
        sha = subprocess.run(["git", "-C", str(root), "hash-object", "-t", "commit", "-w", "--stdin"],
                             input=raw, text=True, capture_output=True, check=True, env=env).stdout.strip()
        _git(root, "update-ref", "refs/heads/main", sha)
        # Control: an explicit --show-signature DOES run the planted program.
        subprocess.run(["git", "-C", str(root), "log", "--show-signature", "-1"], env=env,
                       capture_output=True, check=False)
        self.assertTrue(marker.exists(), "control: explicit --show-signature must fire the marker")
        marker.unlink()
        for scope in poc_scan.SCOPES:
            self.assertEqual(self.scan(root, scope)["errors"], [], scope)
        self.assertFalse(marker.exists(), "planted gpg.program ran during a scan")

    # -- P-2: colour config ------------------------------------------------------------
    def test_color_always_config_does_not_hide_secrets(self):
        root = self.make_repo(files={"s.txt": AWS + "\n"})
        with open(root / ".git" / "config", "a") as fh:
            fh.write("[color]\n\tui = always\n\tgrep = always\n")
        for scope in ("worktree", "index", "history"):
            res = self.scan(root, scope)
            self.assertEqual(res["errors"], [], scope)
            self.assertTrue(res["complete"])
            self.assertIn("s.txt", {h.get("path_or_redacted") for h in res["hits"]}, scope)

    def test_unparseable_untruncated_grep_output_fails_closed(self):
        root = self.make_repo(files={"s.txt": AWS + "\n"})
        real = poc_scan.run_git

        def garbled(argv, deadline, max_bytes, ok_codes=(0,)):
            if argv[SUB] == "grep":
                return git_executor.GitResult(b"\x1b[35ms.txt\x1b[m:1:x\n", False, None)
            return real(argv, deadline, max_bytes, ok_codes)

        with mock.patch.object(poc_scan, "run_git", garbled):
            res = self.scan(root, "index")
        self.assertEqual((res["hits"], res["complete"], res["errors"]), ([], False, ["git_failed"]))

    # -- P-3: attributes ---------------------------------------------------------------
    def test_committed_gitattributes_minus_diff_does_not_hide_secrets(self):
        root = self.make_repo(files={".gitattributes": "* -diff\n", "s.txt": AWS + "\n"})
        for scope in ("worktree", "index", "history"):
            res = self.scan(root, scope)
            self.assertIn("s.txt", {h.get("path_or_redacted") for h in res["hits"]}, scope)
        hist = self.scan(root, "history")
        self.assertTrue([h for h in hist["hits"] if h.get("via") == "log"], "git log -G blind")
        self.assertTrue([h for h in hist["hits"] if h.get("via") != "log"], "tree grep blind")

    def test_info_attributes_not_covered_by_attr_source_but_covered_by_text_flag(self):
        """Finding: --attr-source does NOT neutralise .git/info/attributes (git 2.43.0);
        `-a` / `--text` does."""
        root = self.make_repo(files={"s.txt": AWS + "\n"})
        (root / ".git" / "info").mkdir(exist_ok=True)
        (root / ".git" / "info" / "attributes").write_text("* -diff -text binary\n")
        env = {"PATH": os.environ["PATH"], "HOME": "/nonexistent", "GIT_CONFIG_GLOBAL": "/dev/null",
               "GIT_CONFIG_NOSYSTEM": "1"}
        blind = subprocess.run(["git", f"--attr-source={EMPTY_TREE}", "-C", str(root), "grep", "-I", "-l",
                                "AKIA"], env=env, capture_output=True, text=True).stdout
        self.assertEqual(blind, "", "git changed: --attr-source now covers info/attributes?")
        for scope in ("worktree", "index", "history"):
            res = self.scan(root, scope)
            self.assertIn("s.txt", {h.get("path_or_redacted") for h in res["hits"]}, scope)
        self.assertTrue([h for h in self.scan(root, "history")["hits"] if h.get("via") == "log"])

    def test_git_without_attr_source_fails_closed(self):
        root = self.make_repo(files={"s.txt": AWS + "\n"})
        real = _which_git()
        path = self._fake_git(f'case "$*" in *--attr-source*) exit 129;; esac\nexec {real} "$@"\n')
        with mock.patch.dict(os.environ, {"PATH": path}):
            for scope in poc_scan.SCOPES:
                res = self.scan(root, scope)
                self.assertEqual((res["hits"], res["complete"]), ([], False), scope)
                self.assertTrue(res["errors"], scope)
            ref = poc_scan.ref_containment(str(root), _git(root, "rev-parse", "HEAD"), self.cfg)
            self.assertEqual((ref["complete"], ref["pushed"]), (False, "unknown"))

    # -- P-5: catch-all ----------------------------------------------------------------
    def test_unexpected_exception_becomes_internal_error_without_trace(self):
        root = self.make_repo()
        boom = RuntimeError("secret-" + AWS)
        with mock.patch.object(poc_scan, "resolve_root", side_effect=boom):
            res = self.scan(root, "index")
            ref = poc_scan.ref_containment(str(root), "a" * 40, self.cfg)
        with mock.patch.object(poc_scan._Scan, "scan_tracked_names", side_effect=boom):
            res2 = self.scan(root, "tracked_names")
        for out in (res, ref, res2):
            self.assertEqual((out["errors"], out["complete"]), (["internal_error"], False))
            self.assertNotIn("secret-", json.dumps(out))
            self.assertNotIn(AWS, json.dumps(out))

    # -- P-6/P-7: the whole process group is gone after a timeout ----------------------
    def test_timeout_kills_leader_and_child(self):
        root = self.make_repo()
        pidfile = self.base / "pids"
        path = self._fake_git(f"sleep 60 &\necho $! > {pidfile}\necho $$ >> {pidfile}\nwait\n")
        cfg = PocAuditConfig(allowed_root=self.base, deadline_seconds=1.0)
        with mock.patch.dict(os.environ, {"PATH": path}):
            res = poc_scan.scan_secrets(str(root), "index", None, cfg)
        self.assertEqual(res["errors"], ["timeout"])
        pids = [int(x) for x in pidfile.read_text().split()]
        self.assertEqual(len(pids), 2)
        for pid in pids:
            for _ in range(60):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.1)
            else:
                self.fail(f"process {pid} survived the timeout")

    # -- P-8 ---------------------------------------------------------------------------
    def test_symlinked_fetch_head_is_ignored(self):
        origin = self.make_repo("origin")
        clone = self.base / "clone"
        _git(self.base, "clone", "-q", str(origin), str(clone))
        sha = _git(clone, "rev-parse", "HEAD")
        target = self.base / "elsewhere"
        target.write_text("x")
        fh = clone / ".git" / "FETCH_HEAD"
        if fh.exists() or fh.is_symlink():
            fh.unlink()
        fh.symlink_to(target)
        self.assertIsNone(poc_scan.ref_containment(str(clone), sha, self.cfg)["last_fetch_time"])

    # -- P-9 / P-10 --------------------------------------------------------------------
    def test_worktree_file_named_like_tree_prefix_is_not_split(self):
        name = "a" * 40 + ":name.txt"
        root = self.make_repo(files={name: AWS + "\n"})
        self.assertEqual([h["path_or_redacted"] for h in self.scan(root, "worktree")["hits"]], [name])
        self.assertNotIn("commit", self.scan(root, "worktree")["hits"][0])

    def test_range_named_like_a_file_is_not_ambiguous(self):
        root = self.make_repo(files={"main": "just a file\n"})
        res = self.scan(root, "history", "main")
        self.assertEqual((res["errors"], res["complete"]), ([], True))

    # -- P-11 --------------------------------------------------------------------------
    def test_tracked_names_case_insensitive_and_extended(self):
        names = [".ENV", "X/ID_RSA", "Key.PEM", "id_ed25519", "a.p12", "b.PFX", ".npmrc", ".pgpass",
                 "SECRETS.YAML"]
        root = self.make_repo(files={n: "x\n" for n in names + ["fine.txt"]})
        got = {h["path_or_redacted"] for h in self.scan(root, "tracked_names")["hits"]}
        self.assertEqual(got, set(names))

    # -- P-12: F-2 escapes -------------------------------------------------------------
    def test_symlink_and_dotdot_escape_from_allowed_root_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other).resolve()
            _git(outside, "init", "-q")
            link = self.base / "link"
            link.symlink_to(outside)
            self.assertEqual(self.scan(link, "index")["errors"], ["not_a_toplevel"])
            rel = os.path.relpath(outside, self.base)
            dotdot = f"{self.base}/{rel}"
            self.assertIn("..", dotdot)
            res = poc_scan.scan_secrets(dotdot, "index", None, self.cfg)
            self.assertEqual(res["errors"], ["not_a_toplevel"])
            sha = "a" * 40
            self.assertEqual(poc_scan.ref_containment(dotdot, sha, self.cfg)["errors"],
                             ["not_a_toplevel"])


class TextAndStructureTests(unittest.TestCase):
    @staticmethod
    def _tree(path: Path) -> ast.Module:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_exactly_two_tools_registered(self):
        names = []
        for node in ast.walk(self._tree(SERVER_PY)):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                            and dec.func.attr == "tool"):
                        names.append(node.name)
        self.assertEqual(sorted(names), ["ref_containment", "scan_secrets"])

    def test_only_git_executor_spawns_a_process(self):
        banned_attrs = {"run", "Popen", "call", "check_call", "check_output", "system", "popen",
                        "spawnv", "spawnvp", "execv", "execvp", "fork"}
        for path in (SERVER_PY, SCAN_PY):
            tree = self._tree(path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertNotIn("subprocess", [a.name for a in node.names], path.name)
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(node.module, "subprocess", path.name)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in ("os", "subprocess"):
                        self.assertNotIn(node.func.attr, banned_attrs, path.name)
        popens = [n for n in ast.walk(self._tree(EXEC_PY))
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr == "Popen"]
        self.assertEqual(len(popens), 1)
        kw = {k.arg: k.value for k in popens[0].keywords}
        self.assertIs(kw["shell"].value, False)
        self.assertNotIn("capture_output", kw)
        self.assertEqual(kw["stderr"].attr, "DEVNULL")
        self.assertIn("env", kw)

    def test_no_shell_true_and_no_capture_output_in_new_modules(self):
        for path in (SERVER_PY, SCAN_PY, EXEC_PY):
            for node in ast.walk(self._tree(path)):
                if isinstance(node, ast.Call):
                    for kw in node.keywords:
                        if kw.arg == "shell":
                            self.assertIs(getattr(kw.value, "value", None), False, path.name)
                        self.assertNotEqual(kw.arg, "capture_output", path.name)

    def test_existing_audit_server_files_untouched_in_tool_count(self):
        tree = self._tree(PKG / "audit_server.py")
        decorated = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                     and any(isinstance(d, ast.Call) and getattr(d.func, "attr", "") == "tool"
                             for d in n.decorator_list)]
        self.assertEqual(len(decorated), 4)

    def test_servers_yaml_entry_matches_spec_exactly(self):
        data = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))
        entry = data["servers"]["poc-security-audit"]
        self.assertEqual(entry["tags"], ["extended"])
        self.assertEqual(entry["transport"], "stdio")
        self.assertEqual(entry["command"], "python3")
        self.assertEqual(entry["args"], ["-m", "implementation.runtime.security.poc_audit_server",
                                         "--allowed-root", "."])
        self.assertNotIn("env", entry)
        self.assertIn("security-audit", data["servers"])  # the four-tool server is still there


class PocSecurityEngineerGrantTests(unittest.TestCase):
    """Mirrors `ProjectedClaudeCodeAgentGrantTests` for `poc-security-engineer`."""

    TOKENS = ("mcp__poc-security-audit__scan_secrets", "mcp__poc-security-audit__ref_containment",
              "mcp__security-audit__grep_content")

    def test_source_has_no_execute_and_the_expected_tokens(self):
        fm, _ = parse_file(SOURCE_AGENT)
        tools = set(fm.get("tools") or [])
        self.assertNotIn("execute", tools)
        for token in self.TOKENS:
            self.assertIn(token, tools)
        for keep in ("read", "search", "web"):
            self.assertIn(keep, tools)
        self.assertEqual(fm.get("maturity"), "stable")

    def test_projected_claude_agent_has_no_bash(self):
        self.assertTrue(PROJECTED_AGENT.is_file(), "run sync.mjs")
        fm, _ = parse_file(PROJECTED_AGENT)
        tools = {t.strip() for t in (fm.get("tools") or "").split(",") if t.strip()}
        self.assertNotIn("Bash", tools)
        for token in self.TOKENS:
            self.assertIn(token, tools)
        self.assertIn("Read", tools)

    def test_edit_after_texts_present_exactly_once_and_escalation_kept(self):
        text = SOURCE_AGENT.read_text(encoding="utf-8")
        for after in (
            "using the secret-scan tool whose output omits matched text, never a tool that prints matched lines.",
            "(reported as pushed only when a fetched remote-tracking ref contains the commit, otherwise as unknown and unconfirmed against the remote, with the time of the last fetch; an unpushed result is reported as unknown, and the secret is treated as exposed either way)",
            "A scan that did not complete (tool unavailable, error, timeout or `truncated`) is a blocker and the verdict is `FAIL`; it is never `PASS`. A clean scan means no match for the scan tool's fixed rule set only",
        ):
            self.assertEqual(text.count(after), 1, after[:40])
        self.assertIn("The PoC orchestrator will handle escalation", text)


# ---------------------------------------------------------------------------
# 3. Live stdio smoke test.
# ---------------------------------------------------------------------------

def _mcp_available() -> bool:
    try:
        import mcp  # noqa: F401
        from mcp.server.mcpserver import MCPServer  # noqa: F401
    except ImportError:
        return False
    return True


@unittest.skipUnless(_mcp_available(), "mcp SDK not installed")
class StartupSmokeTests(RepoCase):
    def _params(self):
        from mcp import StdioServerParameters
        return StdioServerParameters(
            command=sys.executable,
            args=["-m", "implementation.runtime.security.poc_audit_server",
                  "--allowed-root", str(self.base)],
            cwd=str(REPO_ROOT))

    @staticmethod
    def _dict(result) -> dict:
        texts = [getattr(c, "text", None) for c in (result.content or [])]
        return json.loads([t for t in texts if t is not None][0])

    def test_lists_exactly_two_tools_answers_one_call_and_rejects_fabricated(self):
        import anyio
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        root = self.make_repo(files={"k.txt": SAMPLES["aws-access-key-id"] + "\n"})
        sha = _git(root, "rev-parse", "HEAD")

        async def run():
            out = {}
            async with stdio_client(self._params()) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    out["tools"] = sorted(t.name for t in (await session.list_tools()).tools)
                    out["scan"] = await session.call_tool(
                        "scan_secrets", {"root_dir": str(root), "scope": "index"})
                    out["ref"] = await session.call_tool(
                        "ref_containment", {"root_dir": str(root), "commit": sha})
                    for verb in ("execute", "run_command", "bash", "shell", "eval"):
                        out[verb] = await session.call_tool(verb, {"command": "id"})
            return out

        out = anyio.run(run)
        self.assertEqual(out["tools"], ["ref_containment", "scan_secrets"])
        scan = self._dict(out["scan"])
        self.assertEqual([h["path_or_redacted"] for h in scan["hits"]], ["k.txt"])
        self.assertTrue(scan["complete"])
        self.assertNotIn(AWS, json.dumps(scan))
        ref = self._dict(out["ref"])
        self.assertEqual((ref["pushed"], ref["local_branches"]), ("unknown", ["refs/heads/main"]))
        for verb in ("execute", "run_command", "bash", "shell", "eval"):
            self.assertTrue(out[verb].is_error, verb)
            self.assertIn("Unknown tool", " ".join(getattr(c, "text", "") for c in out[verb].content))


if __name__ == "__main__":
    unittest.main()
