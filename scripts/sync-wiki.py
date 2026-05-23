#!/usr/bin/env python3
"""
Sync docs/wiki/*.md to the GitLab project Wiki via REST API.

- Filename → slug:  'quick-start.md' → 'quick-start'
- Title:
    * If the file starts with YAML frontmatter containing `title: …`, use that.
    * Otherwise derive from slug: 'quick-start' → 'Quick Start'.
  Frontmatter is stripped before upload.
- 'README.md' is skipped (it's our internal contributor doc, not a wiki page).
- For each file: tries PUT to update an existing page, falls back to POST to
  create. Failures on individual pages do not abort the sync.

Required environment:
  CI_API_V4_URL    e.g. https://gitlab.com/api/v4    (set by GitLab CI)
  CI_PROJECT_ID    numeric project id                (set by GitLab CI)
  WIKI_TOKEN       project access token, scope `api` (CI/CD variable)

Run locally with:
  CI_API_V4_URL=https://gitlab.com/api/v4 \\
  CI_PROJECT_ID=82070979 \\
  WIKI_TOKEN=glpat-... \\
    python3 scripts/sync-wiki.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

WIKI_DIR = Path(__file__).resolve().parent.parent / "docs" / "wiki"
SKIP_FILES = {"README.md"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
TITLE_LINE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)


def slug_from_filename(name: str) -> str:
    return name.removesuffix(".md")


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("_", "-").split("-"))


def parse_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (title-or-None, body-without-frontmatter)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    block = m.group(1)
    body = text[m.end():]
    title_match = TITLE_LINE_RE.search(block)
    title = title_match.group(1).strip().strip('"').strip("'") if title_match else None
    return title, body


def request(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, dict | None]:
    data = None
    headers = {"PRIVATE-TOKEN": token}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8") or "null")
        except Exception:
            payload = None
        return e.code, payload


def upsert_page(api: str, project_id: str, token: str, slug: str, title: str, content: str) -> bool:
    base = f"{api}/projects/{project_id}/wikis"
    update_url = f"{base}/{urllib.parse.quote(slug, safe='')}"
    body = {"title": title, "content": content, "format": "markdown"}

    code, payload = request("PUT", update_url, token, body)
    if code == 200 and payload and payload.get("slug"):
        print(f"  [updated] {slug}")
        return True

    code, payload = request("POST", base, token, body)
    if code in (200, 201) and payload and payload.get("slug"):
        print(f"  [created] {slug}")
        return True

    print(f"  [FAIL] {slug}: HTTP {code} payload={payload}")
    return False


def main() -> int:
    api = os.environ.get("CI_API_V4_URL", "https://gitlab.com/api/v4")
    project_id = os.environ.get("CI_PROJECT_ID")
    token = os.environ.get("WIKI_TOKEN")

    if not project_id:
        print("ERROR: CI_PROJECT_ID is not set.", file=sys.stderr)
        return 2
    if not token:
        print("ERROR: WIKI_TOKEN is not set.", file=sys.stderr)
        return 2
    if not WIKI_DIR.is_dir():
        print(f"ERROR: wiki directory not found: {WIKI_DIR}", file=sys.stderr)
        return 2

    files = sorted(p for p in WIKI_DIR.glob("*.md") if p.name not in SKIP_FILES)
    if not files:
        print("No wiki pages to sync.")
        return 0

    print(f"Syncing {len(files)} wiki page(s) to project {project_id} via {api}")
    failures = 0
    for path in files:
        slug = slug_from_filename(path.name)
        raw = path.read_text(encoding="utf-8")
        explicit_title, content = parse_frontmatter(raw)
        title = explicit_title or title_from_slug(slug)
        if not upsert_page(api, project_id, token, slug, title, content):
            failures += 1

    print(f"Done. {len(files) - failures} ok, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
