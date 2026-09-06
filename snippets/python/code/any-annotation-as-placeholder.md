---
aliases: [any-everywhere, annotated-any]
language: python
python: ">=3.5"
severity: taste
category: maintainability
topic: typing
tags: [annotations, type-checking, documentation]
keywords: [": Any", "-> Any", "from typing import Any", "Dict[str, Any]"]
signature: "Parameters are annotated Any where the concrete type is known, so the checker verifies nothing."
distinguish: "Fine when the value really is arbitrary, as in a serialiser that accepts any JSON-compatible object."
added: 2026-09-04
source: ernst
---

# Any used as a placeholder annotation

## Smell

```python
from typing import Any


def merge(base: Any, overrides: Any) -> Any:
    merged = dict(base)
    merged.update(overrides)
    return merged
```

## Why it's bad

- `Any` is not "unknown", it is "stop checking": it silences the checker at every call site and every use of
  the return value, including uses that are genuinely wrong.
- The body already states the real contract — `dict()` and `.update()` mean both arguments are mappings — so
  the annotation is strictly less informative than the code beneath it.
- `Any` is contagious. The return value flows onward unchecked, so one placeholder disables verification across
  a whole call chain rather than in one signature.
- It presents as a codebase that is annotated, passes `mypy`, and catches nothing, which is worse than being
  unannotated because the green check discourages anyone from looking.

## Better

```python
from collections.abc import Mapping


def merge(base: Mapping[str, int], overrides: Mapping[str, int]) -> dict[str, int]:
    merged = dict(base)
    merged.update(overrides)
    return merged
```
