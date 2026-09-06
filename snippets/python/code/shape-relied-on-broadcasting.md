---
aliases: [accidental-broadcast, rank-mismatch-broadcast]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: numerics
tags: [numpy, pytorch, shapes, broadcasting]
keywords: ["squeeze(", "unsqueeze(", "reshape(-1", "(n, 1)", "predictions - targets"]
signature: "Two arrays of different rank are combined arithmetically, so broadcasting produces a larger result than intended."
distinguish: "Fine when the ranks differ deliberately and the broadcast axis is documented, as when a column vector is added to a matrix."
added: 2026-09-04
source: ernst
---

# Shape mismatch resolved by broadcasting

## Smell

```python
def mse(predictions, targets):
    return ((predictions - targets) ** 2).mean()


loss = mse(model(batch), targets)
```

## Why it's bad

- If `model(batch)` has shape `(32, 1)` and `targets` has shape `(32,)`, the subtraction broadcasts to
  `(32, 32)` — every prediction against every target — and `.mean()` reduces it to a single finite number.
- No exception is raised, because broadcasting is doing exactly what it promises; the mistake was in believing
  the two shapes matched.
- The result is a valid loss that is minimised by predicting the batch mean, so training converges to
  something, just not to the thing you asked for.
- It presents as a model that trains smoothly to a mediocre plateau, which is indistinguishable from a
  modelling problem and is why this bug survives for weeks.

## Better

```python
def mse(predictions, targets):
    if predictions.shape != targets.shape:
        raise ValueError(f"{predictions.shape} does not match {targets.shape}")
    return ((predictions - targets) ** 2).mean()
```
