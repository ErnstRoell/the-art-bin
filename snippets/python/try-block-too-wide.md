---
aliases: [wide-try-block, try-wraps-everything]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: exceptions
tags: [error-handling, scope, attribution]
keywords: ["try:", "except (", "except KeyError", "return None", "json.loads"]
signature: "A try block wraps several unrelated operations, so one handler answers for every failure inside it."
distinguish: "Fine when every statement in the block fails for the same reason and the handler's response is correct for all of them."
added: 2026-09-04
source: ernst
---

# Try block covers too much

## Smell

```python
def load_profile(path):
    try:
        data = json.loads(path.read_text())
        record = data["user"]
        return User(name=record["name"], age=int(record["age"]))
    except (KeyError, ValueError):
        return None
```

## Why it's bad

- The handler was written for one anticipated failure — an absent `user` key — but it now stands behind four
  operations, so a malformed file, a non-numeric age, and a renamed field all produce the same `None`.
- `int()` raises `ValueError` and `json.loads` raises a `ValueError` subclass, so genuinely corrupt input is
  reported as an ordinary missing profile.
- It presents as a caller that keeps receiving `None` for records that visibly exist on disk, and the search
  starts at the caller rather than at the four candidate statements in here.
- Widening a `try` is also how handlers rot: a statement added later inherits a handler that was never
  considered for it.

## Better

```python
def load_profile(path):
    data = json.loads(path.read_text())
    try:
        record = data["user"]
    except KeyError:
        return None
    return User(name=record["name"], age=int(record["age"]))
```
