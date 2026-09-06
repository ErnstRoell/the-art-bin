---
aliases: [mutates-caller-argument, in-place-and-returns]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: mutability
tags: [side-effects, aliasing, api-design]
keywords: ["def", "[index] =", ".append(", "return rows", "enumerate"]
signature: "A function rewrites the container it was passed and also returns it, so callers cannot tell the argument was consumed."
distinguish: "Fine when in-place mutation is the function's stated purpose and it returns None, the way list.sort does."
added: 2026-09-04
source: ernst
---

# Argument mutated in place and returned

## Smell

```python
def normalise(names):
    for index, name in enumerate(names):
        names[index] = name.strip().lower()
    return names


cleaned = normalise(raw_names)
```

## Why it's bad

- Returning the list advertises a pure transformation, so the call site reads as though `raw_names` survives
  untouched — and it does not.
- `cleaned` and `raw_names` are the same object, so a later change through either name is visible through both,
  and any code that wanted the originals for comparison or logging has already lost them.
- The two conventions in the standard library are deliberate and opposite: `sorted` returns a new list,
  `list.sort` returns `None`. Doing both at once means neither signal is available.
- It presents as a value that was correct a moment ago and is now normalised, at a call site that never
  assigned to it.

## Better

```python
def normalise(names):
    return [name.strip().lower() for name in names]


cleaned = normalise(raw_names)
```
