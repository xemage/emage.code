---
name: package-update
description: "Update an installed knowledge pack from source or by existing pack id."
---

# package-update

## Usage

```bash
# update using explicit source
python3 implementation/scripts/package-v3.py update --root implementation --source <local-path-or-https-git-url>

# update from recorded source
python3 implementation/scripts/package-v3.py update --root implementation --pack-id <pack-id>
```

## Notes

- Update re-installs package content in-place.
- Index entry is replaced with latest metadata and timestamp.
