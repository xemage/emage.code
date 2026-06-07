---
name: package-install
description: "Install a knowledge pack from a local path or HTTPS git source."
---

# package-install

## Usage

```bash
python3 implementation/scripts/package-v3.py install --root implementation --source <local-path-or-https-git-url>
```

## Notes

- Source may be a local folder containing `pack.json`.
- Source may be an HTTPS git repository ending with `.git`.
- Metadata is validated against `implementation/registry/package.schema.json`.
