---
aliases: [magic-string-parameter, stringly-typed]
language: python
python: ">=3.4"
severity: trap
category: maintainability
topic: typing
tags: [enums, api-design, magic-values]
keywords: ['== "train"', '== "val"', 'split=', 'mode=', 'raise ValueError']
signature: "A parameter selects behaviour from a set of magic strings, so a typo is only caught at runtime if at all."
distinguish: "Fine when the string is genuinely open-ended data such as a filename or a user-supplied label."
added: 2026-09-04
source: ernst
---

# Stringly typed mode parameter

## Smell

```python
def load_split(name, split):
    if split == "train":
        return read(name, shuffle=True)
    if split == "val":
        return read(name, shuffle=False)
    raise ValueError(split)


loader = load_split("cifar", "vaL")
```

## Why it's bad

- The set of valid values exists only as a sequence of `==` comparisons, so nothing — not the type checker, not
  the editor, not `grep` — can enumerate it.
- `"vaL"` is accepted by the signature and rejected at the bottom of the body, which is the latest possible
  moment and often inside a long-running job.
- Callers cannot discover the options without reading the implementation, and the third caller invariably
  invents a fourth spelling such as `"valid"`.
- It presents as a crash after several minutes of setup, or worse, as a silent fall-through when a later edit
  replaces the `raise` with a default.

## Better

```python
import enum


class Split(enum.Enum):
    TRAIN = "train"
    VAL = "val"


def load_split(name, split: Split):
    return read(name, shuffle=split is Split.TRAIN)
```
