---
aliases: [type-equality-check, type-instead-of-isinstance]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: typing
tags: [type-checking, subclasses, dispatch]
keywords: ["type(", ") == dict", ") == list", ") is str", "type(value)"]
signature: "A type is checked with type and equality, so subclasses of the expected type fall through."
distinguish: "Fine when an exact type is genuinely required and a subclass must be rejected, which is worth a comment saying so."
added: 2026-09-04
source: ernst
---

# Type compared with equality

## Smell

```python
def render(value):
    if type(value) == dict:
        return render_mapping(value)
    return str(value)


render(collections.OrderedDict(a=1))
```

## Why it's bad

- `type(value)` is the exact class, so `OrderedDict`, `defaultdict`, `Counter`, and any local `dict` subclass
  all compare unequal and take the fallback branch.
- The fallback here is `str`, which succeeds, so the wrong branch produces output rather than an error.
- `isinstance` exists for this and additionally understands ABCs and protocols, so `isinstance(value, Mapping)`
  covers the types that behave like mappings without naming them.
- It presents as a function that works everywhere except the one code path that swapped in a `defaultdict` for
  convenience, three releases after this line was written.

## Better

```python
from collections.abc import Mapping


def render(value):
    if isinstance(value, Mapping):
        return render_mapping(value)
    return str(value)
```
