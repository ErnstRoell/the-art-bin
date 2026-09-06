---
aliases: [strip-as-suffix-removal, multi-character-strip]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: strings
tags: [suffixes, character-sets, filenames]
keywords: [".strip(", ".lstrip(", ".rstrip(", '.strip(".txt")', "removesuffix"]
signature: "A multi-character argument to strip is written as though it removed a suffix, when it removes a set of characters."
distinguish: "Fine when a character set really is intended, as in stripping whitespace and punctuation from both ends."
added: 2026-09-04
source: ernst
---

# Strip used to remove a suffix

## Smell

```python
def stem(filename):
    return filename.rstrip(".txt")


print(stem("train.txt"))
print(stem("dataset.txt"))
```

## Why it's bad

- `rstrip(".txt")` takes a *set* of characters — `.`, `t`, `x` — and removes any of them from the end,
  repeatedly, until it meets something else.
- So `"train.txt"` yields `"train"` and looks correct, while `"dataset.txt"` yields `"datase"`, because the `t`
  that ends the stem is also in the set.
- The bug is data-dependent and therefore survives every test whose fixtures happen not to end in those
  letters, which is most of them.
- It presents as a handful of records with names truncated by one or two characters, which reads like an
  encoding or database column-width problem rather than a string call.

## Better

```python
def stem(filename):
    return filename.removesuffix(".txt")


print(stem("train.txt"))
print(stem("dataset.txt"))
```
