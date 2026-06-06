---
name: package-uninstall
description: "Uninstall a v3 knowledge pack and remove it from the installed index."
---

# package-uninstall

## Usage

```bash
python3 v3/implementation/scripts/package-v3.py uninstall --root v3/implementation --pack-id <pack-id>
```

## Notes

- Removes package directory from `v3/implementation/packs/installed/<pack-id>`.
- Removes package record from `v3/implementation/packs/installed/index.json`.
