---
aliases: [string-plus-equals-in-loop]
language: python
python: ">=3.0"
severity: taste
category: performance
topic: strings
tags: [accumulation, join]
keywords: ["+=", "out = \"\"", "result = ''", "for row in"]
signature: "A string is accumulated with += inside a loop instead of being joined at the end."
distinguish: "Fine for a couple of fixed pieces, where join would be more noise than the concatenation it replaces."
added: 2026-09-04
source: ernst
---

# String concatenation in a loop

## Smell

```python
def render(rows):
    out = ""
    for row in rows:
        out += format_row(row) + "\n"
    return out
```

## Why it's bad

- Strings are immutable, so each iteration builds a new object and copies everything accumulated so far.
- CPython has an in-place optimisation that hides the cost, and it silently stops applying as soon as anything
  else holds a reference to the string, so performance depends on details far from this loop.
- It states the mechanism rather than the intent, where `join` says "one string from many parts" directly.

## Better

```python
def render(rows):
    return "\n".join(format_row(row) for row in rows) + "\n"
```
