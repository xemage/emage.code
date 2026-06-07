#!/usr/bin/env python3
"""Install, update, and uninstall knowledge packs from local paths or HTTPS git URLs."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

INDEX_FILE = "index.json"
METADATA_FILE = "pack.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "update", "uninstall", "list"])
    parser.add_argument("--source", default="", help="local path or HTTPS git URL")
    parser.add_argument("--pack-id", default="", help="pack id for update/uninstall")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.is_file():
        return {"schemaVersion": "1.0.0", "packages": []}
    data = _load_json(index_path)
    if not isinstance(data, dict) or "packages" not in data:
        raise ValueError(f"invalid package index: {index_path}")
    if not isinstance(data["packages"], list):
        raise ValueError(f"invalid package index packages list: {index_path}")
    return data


def _save_index(index_path: Path, index: dict[str, Any]) -> None:
    index["packages"] = sorted(index.get("packages", []), key=lambda item: item["packId"])
    _write_json(index_path, index)


def _resolve_source(source: str) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if source.startswith("https://") and source.endswith(".git"):
        tmp = tempfile.TemporaryDirectory()
        repo_path = Path(tmp.name) / "repo"
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", source, str(repo_path)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            tmp.cleanup()
            raise RuntimeError(f"git clone failed: {proc.stdout}\n{proc.stderr}")
        return repo_path, tmp

    source_path = Path(source).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"source does not exist: {source_path}")
    return source_path, None


def _load_package_metadata(source_root: Path, schema_path: Path) -> dict[str, Any]:
    metadata_path = source_root / METADATA_FILE
    if not metadata_path.is_file():
        raise FileNotFoundError(f"missing metadata file: {metadata_path}")
    metadata = _load_json(metadata_path)
    schema = _load_json(schema_path)
    jsonschema.validate(metadata, schema)
    content_path = source_root / metadata["contentPath"]
    if not content_path.is_dir():
        raise FileNotFoundError(f"missing package content directory: {content_path}")
    return metadata


def _install_from_source(root: Path, source: str, allow_update: bool) -> dict[str, Any]:
    schema_path = root / "registry" / "package.schema.json"
    source_path, temp_handle = _resolve_source(source)
    try:
        metadata = _load_package_metadata(source_path, schema_path)
        pack_id = metadata["packId"]
        content_path = (source_path / metadata["contentPath"]).resolve()

        install_root = root / "packs" / "installed"
        install_dir = install_root / pack_id
        index_path = install_root / INDEX_FILE
        index = _load_index(index_path)

        existing = next((item for item in index["packages"] if item["packId"] == pack_id), None)
        if existing and not allow_update:
            raise ValueError(f"package already installed: {pack_id}")

        if install_dir.exists():
            shutil.rmtree(install_dir)
        shutil.copytree(content_path, install_dir)

        record = {
            "packId": pack_id,
            "name": metadata["name"],
            "version": metadata["version"],
            "source": source,
            "installedAt": datetime.now(timezone.utc).isoformat(),
        }

        filtered = [item for item in index["packages"] if item["packId"] != pack_id]
        filtered.append(record)
        index["packages"] = filtered
        _save_index(index_path, index)
        return record
    finally:
        if temp_handle is not None:
            temp_handle.cleanup()


def action_install(root: Path, source: str) -> int:
    if not source:
        raise ValueError("--source is required for install")
    record = _install_from_source(root, source, allow_update=False)
    print(f"installed {record['packId']}@{record['version']}")
    return 0


def action_update(root: Path, source: str, pack_id: str) -> int:
    if source:
        record = _install_from_source(root, source, allow_update=True)
        print(f"updated {record['packId']}@{record['version']}")
        return 0

    if not pack_id:
        raise ValueError("--pack-id or --source is required for update")

    index_path = root / "packs" / "installed" / INDEX_FILE
    index = _load_index(index_path)
    existing = next((item for item in index["packages"] if item["packId"] == pack_id), None)
    if not existing:
        raise ValueError(f"package not installed: {pack_id}")

    record = _install_from_source(root, existing["source"], allow_update=True)
    print(f"updated {record['packId']}@{record['version']}")
    return 0


def action_uninstall(root: Path, pack_id: str) -> int:
    if not pack_id:
        raise ValueError("--pack-id is required for uninstall")

    install_root = root / "packs" / "installed"
    install_dir = install_root / pack_id
    index_path = install_root / INDEX_FILE
    index = _load_index(index_path)

    if install_dir.is_dir():
        shutil.rmtree(install_dir)

    filtered = [item for item in index["packages"] if item["packId"] != pack_id]
    if len(filtered) == len(index["packages"]):
        raise ValueError(f"package not installed: {pack_id}")

    index["packages"] = filtered
    _save_index(index_path, index)
    print(f"uninstalled {pack_id}")
    return 0


def action_list(root: Path) -> int:
    index_path = root / "packs" / "installed" / INDEX_FILE
    index = _load_index(index_path)
    for item in index["packages"]:
        print(f"{item['packId']} {item['version']} {item['source']}")
    return 0


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if args.action == "install":
        return action_install(root, args.source)
    if args.action == "update":
        return action_update(root, args.source, args.pack_id)
    if args.action == "uninstall":
        return action_uninstall(root, args.pack_id)
    return action_list(root)


if __name__ == "__main__":
    raise SystemExit(main())
