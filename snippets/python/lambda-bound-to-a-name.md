---
aliases: [named-lambda, lambda-assignment]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: functions
tags: [lambda, tracebacks, docstrings]
keywords: ["= lambda", "= lambda x:", "normalise = lambda"]
signature: "A lambda is assigned to a name, so the resulting function has no qualified name and cannot carry a docstring."
distinguish: "Fine when the lambda stays anonymous as an argument to sorted, map, or a callback parameter."
added: 2026-09-04
source: ernst
---

# Lambda bound to a name

## Smell

```python
area = lambda width, height: width * height
volume = lambda width, height, depth: area(width, height) * depth
```

## Why it's bad

- `def` and `lambda` produce the same kind of object, so the only difference here is what is given up: a
  `__name__`, a docstring, annotations, a default argument spelled readably, and a statement body if the
  function ever grows one.
- Tracebacks and profiler output show `<lambda>`, so a stack with three of these in it cannot be read — which
  is exactly the situation in which you are reading a stack.
- The form implies "too trivial to name", while the assignment proves otherwise; the reader is left wondering
  which signal to believe.
- `def` is the same number of lines and gives all of it back, so this is a preference with no cost attached to
  changing it.

## Better

```python
def area(width, height):
    return width * height


def volume(width, height, depth):
    return area(width, height) * depth
```
