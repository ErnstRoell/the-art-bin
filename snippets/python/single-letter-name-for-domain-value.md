---
aliases: [one-letter-variable, single-character-name]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: naming
tags: [naming, scope, house-style]
keywords: ["def f(", "for x in", "m =", "d =", "p =", "t ="]
signature: "A single letter names a domain value rather than a loop index, so the code cannot be read without its definition."
distinguish: "Fine for a loop index, a comprehension variable, or a symbol that matches the notation of the paper being implemented."
added: 2026-09-04
source: ernst
---

# Single letter name for a domain value

## Smell

```python
def score(m, d, t):
    p = m(d)
    return (p > t).float().mean()
```

## Why it's bad

- The signature carries no information at all, so calling this function correctly requires reading its body,
  and reading its body requires guessing what `m` and `t` are.
- Single letters are unsearchable. `grep` for `t` finds nothing useful, so the blast radius of a change to this
  function cannot be established mechanically.
- The scope is what makes it wrong rather than the length: `i` inside three lines is fine because its meaning
  is bounded, and a parameter's meaning is not.
- It presents as a function nobody dares to modify, and as a wrapper written next to it whose only job is to
  give the arguments names.

## Better

```python
def accuracy_above(model, batch, threshold):
    probabilities = model(batch)
    return (probabilities > threshold).float().mean()
```
