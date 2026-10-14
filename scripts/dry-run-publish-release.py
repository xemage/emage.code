#!/usr/bin/env python3
"""Offline rehearsal of scripts/publish-release.py main() (T619).

Needs no network, no tag, no push and no credential. It copies the release
document ``docs/releases/<tag>.md`` (and ``CHANGELOG.md`` when present) into a
temporary directory, points the module's ``ROOT`` there, replaces ``run_git``
and ``gitlab_request`` with in-process fakes, makes ``urllib`` refuse to open
any URL, and runs the real ``main()`` without ``--skip-api``. It then reports
what a tag run would write and what it would send as the Release description.
The repository tree is never written.

Usage: python3 scripts/dry-run-publish-release.py [--tag v7.0.1]
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
PLACEHOLDER_TOKEN = "DRY-RUN-PLACEHOLDER"  # not a credential; never sent anywhere
SAMPLE_SUBJECTS = [
    "feat(release): single release document",
    "fix(ci): drop the root release-notes artifact",
    "docs: update release runbook",
]


def load_publish_release(repo: Path = REPO) -> Any:
    path = repo / "scripts" / "publish-release.py"
    spec = importlib.util.spec_from_file_location("publish_release", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load publish-release module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_run_git(tag: str, previous_tag: str):
    def run_git(args: list[str]) -> str:
        if args[:1] == ["tag"]:
            return f"{tag}\n{previous_tag}"
        if args[:1] == ["rev-parse"]:
            return "false"
        if args[:1] == ["merge-base"]:
            return "0" * 40
        if args[:1] == ["rev-list"]:
            return str(len(SAMPLE_SUBJECTS))
        if args[:1] == ["log"]:
            return "\n".join(SAMPLE_SUBJECTS)
        return ""  # fetch and anything else: no-op

    return run_git


def _refuse_network(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("dry run attempted network access")


def resolve_release_source(module: Any, tag: str, source_dir: Path) -> Path:
    """Validate ``tag`` against the CI tag rule and keep the source under ``source_dir``."""
    module.validate_tag(tag)
    base = source_dir.resolve()
    source = (base / f"{tag}.md").resolve()
    if not source.is_relative_to(base):
        raise module.ReleasePublishError(f"release document escapes {base}: {source}")
    if not source.is_file():
        raise module.ReleasePublishError(f"missing release document: {source}")
    return source


def run_dry_run(
    tag: str,
    work: Path,
    repo: Path = REPO,
    source_dir: Path | None = None,
    copy_changelog: bool = True,
) -> dict[str, Any]:
    """Run publish-release main() inside ``work``; return what it produced.

    ``source_dir`` defaults to ``<repo>/docs/releases``; ``copy_changelog`` copies
    the repo CHANGELOG.md into ``work`` first (set False for fixture runs).
    """
    module = load_publish_release(repo)
    source = resolve_release_source(module, tag, source_dir or repo / "docs" / "releases")
    target = work / "docs" / "releases"
    target.mkdir(parents=True)
    shutil.copyfile(source, target / f"{tag}.md")
    if copy_changelog and (repo / "CHANGELOG.md").is_file():
        shutil.copyfile(repo / "CHANGELOG.md", work / "CHANGELOG.md")

    sent: list[dict[str, Any]] = []

    def fake_gitlab_request(method, url, token, payload=None):
        sent.append({"method": method, "url": url, "payload": payload})
        if method == "GET":
            raise module.ReleasePublishError(f"GitLab API GET {url} failed: 404 fake")
        return {"tag_name": tag}

    module.ROOT = work
    module.run_git = _fake_run_git(tag, "v0.0.0")
    module.gitlab_request = fake_gitlab_request
    original_urlopen = urllib.request.urlopen
    urllib.request.urlopen = _refuse_network
    argv = sys.argv
    sys.argv = [
        "publish-release.py", "--tag", tag,
        "--api-v4-url", "https://gitlab.invalid/api/v4",
        "--project-id", "0", "--token", PLACEHOLDER_TOKEN,
    ]
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = module.main()
    finally:
        sys.argv = argv
        urllib.request.urlopen = original_urlopen
    files = sorted(p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file())
    return {"exit": code, "stdout": out.getvalue(), "files": files, "sent": sent, "work": work}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="v7.0.1")
    args = parser.parse_args()
    try:
        load_publish_release().validate_tag(args.tag)
    except Exception as exc:  # ReleasePublishError from the loaded module
        print(f"dry run refused: {exc}")
        return 2
    with tempfile.TemporaryDirectory(prefix="dry-run-publish-release-") as tmp:
        result = run_dry_run(args.tag, Path(tmp))
        work: Path = result["work"]
        print(f"exit code: {result['exit']}")
        print("script output:\n  " + result["stdout"].strip().replace("\n", "\n  "))
        print("files in the temp root after the run:")
        for name in result["files"]:
            print(f"  {name}")
        print(f"root release-notes.md written: {'release-notes.md' in result['files']}")
        for call in result["sent"]:
            desc = (call["payload"] or {}).get("description")
            print(f"fake GitLab call: {call['method']} {call['url']}")
            if desc is not None:
                print(f"  description: {len(desc)} chars, {len(desc.splitlines())} lines")
                print("  first lines:\n    " + "\n    ".join(desc.splitlines()[:3]))
                print("  changelog section:\n    " + "\n    ".join(desc.split("---")[-1].strip().splitlines()))
        print("CHANGELOG.md head:\n  " + "\n  ".join((work / "CHANGELOG.md").read_text().splitlines()[:4]))
        ok = result["exit"] == 0 and "release-notes.md" not in result["files"]
        print("DRY RUN " + ("OK" if ok else "FAILED"))
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
