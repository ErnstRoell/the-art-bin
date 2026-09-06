---
aliases: [star-import]
language: python
python: ">=3.0"
severity: trap
category: maintainability
topic: imports
tags: [namespace, shadowing]
keywords: ["import *", "from os.path import *", "__all__"]
signature: "A module is imported with a wildcard, dumping unknown names into the local namespace."
distinguish: "Fine in an __init__.py that deliberately re-exports a curated __all__, or in an interactive session."
added: 2026-09-04
source: ernst
---

# Wildcard import

## Smell

```python
from os.path import *
from mymodule.helpers import *


def build(name):
    return join(base_dir(), name)
```

## Why it's bad

- Nothing at the call site says where `join` came from, so a reader has to go looking through every wildcard.
- Two wildcards can define the same name, and the later import wins silently.
- The set of imported names changes when the upstream module adds one, so an unrelated release can shadow a
  local function without a single line changing here.
- Linters and type checkers lose track of origins, so tooling stops catching typos in imported names.

## Better

```python
from os.path import join
from mymodule.helpers import base_dir


def build(name):
    return join(base_dir(), name)
```
