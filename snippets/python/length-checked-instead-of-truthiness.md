---
aliases: [len-greater-than-zero, explicit-length-check]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: control-flow
tags: [conditionals, truthiness, emptiness]
keywords: ["len(", "> 0", "== 0", "if len(rows)", "!= 0"]
signature: "Emptiness is tested by comparing len against zero rather than by the object's own truthiness."
distinguish: "Fine when the object has no usable truth value, such as a numpy array, where an explicit len or size test is the only safe form."
added: 2026-09-04
source: ernst
---

# Length compared to zero instead of truthiness

## Smell

```python
def report(rows):
    if len(rows) > 0:
        print(summarise(rows))
    if len(rows) == 0:
        print("no rows")
```

## Why it's bad

- Every container in the language is already falsy when empty, so `if rows:` states the condition directly
  while `len(rows) > 0` states an arithmetic consequence of it.
- The comparison invites variants that are not equivalent — `>= 1`, `!= 0`, `> 0` — and reviewers have to check
  each one instead of recognising a single idiom.
- `len()` demands a sized object, so the check rejects generators and iterators that `if` would have handled,
  narrowing the function for no benefit.
- The negative form is the tell: `if len(rows) == 0` is three tokens away from `if not rows`, and the second one
  is the sentence the author would say out loud.

## Better

```python
def report(rows):
    if rows:
        print(summarise(rows))
    else:
        print("no rows")
```
