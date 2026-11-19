"""T859 (SEC-T756-08): scripts/sync-wiki.py must not follow a redirect, which would re-send PRIVATE-TOKEN.

A local HTTP server answers the wiki PUT with a 302 to a second path on the same server; the test asserts that the
second path is never requested (so no token reaches it) and that the 302 reaches the caller as a failed request.
"""
from __future__ import annotations

import importlib.util
import threading
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "sync-wiki.py"
FAKE_TOKEN = "fake-token-for-the-redirect-test"


def load_sync_wiki():
    spec = importlib.util.spec_from_file_location("sync_wiki_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Handler(BaseHTTPRequestHandler):
    seen: list[tuple[str, str, str | None]] = []

    def _answer(self):
        type(self).seen.append((self.command, self.path, self.headers.get("PRIVATE-TOKEN")))
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        if self.path.startswith("/api/v4/"):
            self.send_response(302)
            self.send_header("Location", "/elsewhere/collect")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = b'{"slug": "stolen"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_PUT = do_POST = _answer

    def log_message(self, *args):  # keep the test output clean
        pass


class TestSyncWikiRefusesRedirects(unittest.TestCase):
    def setUp(self):
        _Handler.seen = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.api = f"http://127.0.0.1:{self.server.server_address[1]}/api/v4"
        self.module = load_sync_wiki()

    def test_a_redirect_is_not_followed_and_the_token_goes_nowhere_else(self):
        """POST: the method urllib's default handler does follow (as a GET with the same headers)."""
        code, _ = self.module.request("POST", f"{self.api}/projects/1/wikis/page", FAKE_TOKEN, {"title": "t"})
        self.assertEqual(code, 302)
        self.assertEqual([p for _, p, _ in _Handler.seen], ["/api/v4/projects/1/wikis/page"])
        self.assertFalse(any(p.startswith("/elsewhere") for _, p, _ in _Handler.seen))

    def test_upsert_page_fails_on_redirects(self):
        ok = self.module.upsert_page(self.api, "1", FAKE_TOKEN, "page", "Page", "body")
        self.assertFalse(ok)
        self.assertEqual(sorted(m for m, _, _ in _Handler.seen), ["POST", "PUT"])
        self.assertTrue(all(p.startswith("/api/v4/") for _, p, _ in _Handler.seen), _Handler.seen)

    def test_the_script_opens_urls_through_the_refusing_opener_only(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("urllib.request.urlopen(", text)
        self.assertIsInstance(self.module.OPENER, urllib.request.OpenerDirector)
        handlers = [type(h).__name__ for h in self.module.OPENER.handlers]
        self.assertIn("_RefuseRedirects", handlers)
        self.assertNotIn("HTTPRedirectHandler", handlers)


if __name__ == "__main__":
    unittest.main()
