---
aliases: [shallow-copy-nested, dict-copy-shares-inner]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [aliasing, defaults, configuration]
keywords: ["dict(", ".copy()", "copy.copy", "[:]", ".update("]
signature: "A nested structure is copied with dict or copy, so the inner containers are still shared with the original."
distinguish: "Fine when every nested value is immutable, or when the copy is only ever read."
added: 2026-09-04
source: ernst
---

# Shallow copy of nested data

## Smell

```python
DEFAULTS = {"limits": {"steps": 1000}, "name": "run"}


def with_overrides(overrides):
    config = dict(DEFAULTS)
    config["limits"].update(overrides)
    return config
```

## Why it's bad

- `dict(DEFAULTS)` copies one level: the new mapping has its own `limits` *key*, bound to the very same inner
  dict as the original.
- `config["limits"].update(...)` therefore writes into `DEFAULTS`, so the defaults are permanently rewritten by
  the first caller who overrides anything.
- The top level behaves exactly as intended, which is what makes it a trap — assigning `config["name"]` is
  correctly isolated, so the copy looks like it works.
- It presents as configuration that drifts over the life of a process: the second run inherits the first run's
  overrides, and restarting the process fixes it.

## Better

```python
import copy

DEFAULTS = {"limits": {"steps": 1000}, "name": "run"}


def with_overrides(overrides):
    config = copy.deepcopy(DEFAULTS)
    config["limits"].update(overrides)
    return config
```
