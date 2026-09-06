---
aliases: [type-suffix-lies, misleading-name]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: naming
tags: [naming, types]
keywords: ["_list", "_dict", "_str", "_array", ".items()"]
signature: "An identifier carries a type suffix that the value does not actually have."
distinguish: "Fine when the suffix is accurate, though a plural noun usually carries the same information better."
added: 2026-09-04
source: ernst
---

# Name lies about the type

## Smell

```python
def summarise(user_list):
    for name, user in user_list.items():
        yield name, user.age
```

## Why it's bad

- The name asserts a list and the body requires a mapping, so the reader must check the implementation to learn
  what a caller has to pass.
- A wrong name is worse than a vague one, because it is trusted rather than questioned.
- Type suffixes survive the refactor that changes the type, so this is where they come from and why they
  accumulate.

## Better

```python
def summarise(users_by_name):
    for name, user in users_by_name.items():
        yield name, user.age
```
