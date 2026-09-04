---
aliases: [sys-path-hack, sys-path-append]
language: python
python: ">=3.0"
severity: trap
category: maintainability
topic: imports
tags: [packaging, import-path, scripts]
keywords: ["sys.path.append", "sys.path.insert", "os.path.dirname(__file__)", "../src"]
signature: "A module edits sys.path at import time so that a directory outside the package becomes importable."
distinguish: "Fine in a deliberately standalone script that must run without installation, where the path is derived from __file__ and the reason is documented."
added: 2026-09-04
source: ernst
---

# Sys.path mutated to find modules

## Smell

```python
import sys

sys.path.insert(0, "../src")

from mypkg import train


def main():
    train()
```

## Why it's bad

- The path is relative to the *working directory*, not to this file, so the import works when run from one
  directory and fails from anywhere else — including from a test runner.
- Inserting at position zero puts the directory ahead of everything, so a local `json.py` or `types.py` now
  shadows the standard library for the whole process.
- It hides the real problem, which is that the project is not installed. Once the hack exists there is no
  pressure to fix the packaging, and the next module copies it.
- It presents as an `ImportError` that depends on where the command was typed, and as a second copy of the
  package being imported under a different name, so `isinstance` checks against it start failing.

## Better

```python
from mypkg import train


def main():
    train()
```
