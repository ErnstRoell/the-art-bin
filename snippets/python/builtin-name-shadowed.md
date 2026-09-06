---
aliases: [shadows-builtin, assigning-to-builtin]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: naming
tags: [shadowing, scope, builtins]
keywords: ["list =", "dict =", "id =", "type =", "input =", "str ="]
signature: "A local or module name reuses a builtin such as list, dict, or id, so the builtin is unreachable in that scope."
distinguish: "Fine for a keyword argument that must match an external API, where the shadowing is confined to the signature."
added: 2026-09-04
source: ernst
---

# Builtin name shadowed

## Smell

```python
def tally(items):
    dict = {}
    for item in items:
        dict[item] = dict.get(item, 0) + 1
    return dict(sorted(dict.items()))
```

## Why it's bad

- The name `dict` is rebound for the whole function, so the constructor is gone from the moment of assignment
  onward, not just at the point of use.
- Every line up to the last one works perfectly, which is the trap: the failure arrives whenever someone edits
  this function and needs the builtin, and it arrives as `TypeError: 'dict' object is not callable`.
- The error message names the shadowed builtin, so it reads like a type confusion in the data rather than a
  naming choice six lines up.
- The same applies to `id`, `type`, `input`, `list`, and `str` — all short, all tempting, all things a later
  reader assumes are the builtins.

## Better

```python
def tally(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return dict(sorted(counts.items()))
```
