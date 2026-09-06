---
aliases: [exact-float-comparison, float-equals]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: numerics
tags: [floating-point, comparison, tolerance]
keywords: ["== 1.0", "== 0.1", "!= 0.0", "math.isclose", "np.allclose", "sum("]
signature: "Two floating point values are compared for exact equality, so representation error decides the answer."
distinguish: "Fine when the values are exact by construction, such as small integers held as floats or a sentinel like 0.0 that was assigned literally."
added: 2026-09-04
source: ernst
---

# Floating point compared for equality

## Smell

```python
def is_normalised(weights):
    return sum(weights) == 1.0


print(is_normalised([0.57, 0.01, 0.42]))
print(is_normalised([0.30, 0.30, 0.40]))
```

## Why it's bad

- Almost no decimal fraction is representable in binary floating point, so the first sum is
  `0.9999999999999999` and the function rejects weights that are normalised.
- The second call returns `True`, because there the rounding errors happen to cancel — so the check is not
  merely strict, it is inconsistent between inputs that are equally valid.
- Whether it passes depends on the values, their order, and how many there are, none of which the caller
  controls or can reason about.
- Guarding with a hand-rolled `abs(x - y) < 0.0001` replaces one arbitrary judgement with another; `isclose`
  and `allclose` already scale the tolerance with magnitude, which a fixed epsilon does not.
- It presents as a validation error on data that is visibly correct, and as a test that passes with two
  elements and fails with ten.

## Better

```python
import math


def is_normalised(weights):
    return math.isclose(sum(weights), 1.0)
```
