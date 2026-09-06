---
aliases: [kwargs-passthrough, opaque-kwargs]
language: python
python: ">=3.0"
severity: trap
category: maintainability
topic: functions
tags: [signatures, api-design, indirection]
keywords: ["**kwargs", "**config", "def train(**", "(**kwargs)"]
signature: "A function accepts kwargs only to forward them to another function, so no layer states what it accepts."
distinguish: "Fine for a thin decorator or wrapper that must pass an arbitrary signature through unchanged."
added: 2026-09-04
source: ernst
---

# Kwargs forwarded through layers

## Smell

```python
def train(**kwargs):
    model = build(**kwargs)
    return fit(model, **kwargs)


def build(hidden=64, **kwargs):
    return Net(hidden)
```

## Why it's bad

- The real signature of `train` is the union of two other signatures, computed by reading both of them — so the
  question "what can I pass here" has no local answer.
- Misspelling an argument is not an error: `hiden=128` is swallowed by `build`'s own `**kwargs` and silently
  ignored, so the model is built with the default and the run looks successful.
- Every parameter is now shared. `build` and `fit` cannot both have a `lr` that means different things, and
  adding one to either changes the other's contract.
- It presents as a configuration key that has no effect, discovered weeks later when someone finally diffs two
  runs that should have differed.

## Better

```python
def train(*, hidden=64, epochs=10, lr=1e-3):
    model = build(hidden=hidden)
    return fit(model, epochs=epochs, lr=lr)
```
