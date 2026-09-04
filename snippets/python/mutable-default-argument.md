---
aliases: [mutable-default-arg]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [defaults, shared-state]
keywords: ["=[]", "={}", "def", "default argument", "append"]
signature: "A function default is a list or dict, so one object is shared across every call."
distinguish: "Fine when the default is immutable, or when the shared object is the documented intent."
added: 2026-09-04
source: ernst
---

# Mutable default argument

## Smell

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket
```

## Why it's bad

- The list is created once, when the `def` is executed, not on each call.
- Every caller who omits `basket` mutates the same object, so results accumulate across unrelated calls.
- It presents as data from one request appearing in another, which sends people hunting through caches and
  globals rather than at this signature.

## Better

```python
def add_item(item, basket=None):
    basket = [] if basket is None else basket
    basket.append(item)
    return basket
```
