---
scope: project
project_id: fixture-org/repo-p2
title: "Fixture: P2's own project-scope entry (with code, for tree-sitter path)"
tags: [fixture, t452]
---

## Overview

This fixture entry exercises the tree-sitter code-chunking path
(acceptance criterion 1) via the fenced Python block below, and the
section-aware prose-chunking path via this paragraph itself.

## Example helper

```python
import json


def load_config(path):
    with open(path) as handle:
        return json.load(handle)


class ConfigCache:
    def get(self, key):
        return self._data.get(key)
```

Trailing prose after the code block, in the same section.
