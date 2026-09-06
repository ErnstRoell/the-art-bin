---
aliases: [loop-variable-closure, late-binding-lambda]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: functions
tags: [closures, loops, scope]
keywords: ["lambda", "for factor in", ".append(lambda", "def inner", "functools.partial"]
signature: "A function defined in a loop closes over the loop variable, so every closure sees the final value."
distinguish: "Fine when the loop variable is bound at creation time, through a default argument or functools.partial."
added: 2026-09-04
source: ernst
---

# Late binding closure in a loop

## Smell

```python
def make_scalers(factors):
    scalers = []
    for factor in factors:
        scalers.append(lambda value: value * factor)
    return scalers


doubler, tripler = make_scalers([2, 3])
```

## Why it's bad

- A closure captures the *variable* `factor`, not the value it held when the lambda was created, and `factor`
  lives in one cell for the whole loop.
- By the time any scaler is called the loop has finished, so all of them multiply by the last factor —
  `doubler(10)` returns `30`.
- Nothing is raised and the list has the right length, so the object graph looks correct under inspection; only
  the results are wrong.
- It presents as a set of handlers, callbacks, or partial functions that all behave identically, which sends
  people looking for a registration bug rather than at the loop that built them.

## Better

```python
import functools


def make_scalers(factors):
    return [functools.partial(lambda f, value: value * f, factor) for factor in factors]
```
