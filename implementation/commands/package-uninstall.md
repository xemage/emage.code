---
name: package-uninstall
description: "Uninstall a knowledge pack and remove it from the installed index."
---

# package-uninstall

## Usage

```bash
python3 implementation/scripts/package-v3.py uninstall --root implementation --pack-id <pack-id>
```

## Notes

- Removes package directory from `implementation/packs/installed/<pack-id>`.
- Removes package record from `implementation/packs/installed/index.json`.
