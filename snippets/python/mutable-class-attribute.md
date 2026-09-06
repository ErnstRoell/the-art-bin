---
aliases: [class-level-mutable-default, shared-class-attribute]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [shared-state, classes, defaults]
keywords: ["= []", "= {}", "class", "self.items.append", "cls."]
signature: "A list or dict is assigned in the class body, so every instance shares one object."
distinguish: "Fine when the attribute is immutable, or is genuinely class-wide state that all instances are meant to share."
added: 2026-09-04
source: ernst
---

# Mutable class attribute

## Smell

```python
class Batch:
    items = []

    def add(self, item):
        self.items.append(item)
```

## Why it's bad

- The list is created once, when the class body executes, and it belongs to the class rather than to any
  instance.
- `self.items.append` resolves `items` on the class and mutates it in place, so two `Batch` objects that were
  never introduced accumulate into the same list.
- Assignment behaves differently from mutation — `self.items = []` would quietly create a genuine instance
  attribute — so the class works or does not depending on which methods a caller happens to use.
- It presents as leakage between objects that should be independent: a second run of a job sees the first run's
  contents, and the count is always the running total.

## Better

```python
class Batch:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
```
