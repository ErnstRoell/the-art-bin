---
aliases: [numpy-view-mutation, slice-is-a-view]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: numerics
tags: [numpy, aliasing, views, in-place]
keywords: ["[:count]", "-=", "+=", ".copy()", "signal[", "np.ndarray"]
signature: "A slice of an array is modified in place, so the write reaches the original array through the view."
distinguish: "Fine when fancy or boolean indexing produced the slice, which copies, or when mutating the original really is the intent."
added: 2026-09-04
source: ernst
---

# Array view mutated as if it were a copy

## Smell

```python
def centre_head(signal, count):
    window = signal[:count]
    window -= window.mean()
    return window
```

## Why it's bad

- Basic slicing returns a *view* that shares the original buffer, unlike list slicing, which copies — so the
  name `window` is a second handle on `signal`, not a new array.
- `window -= ...` is in-place, so the first `count` samples of the caller's `signal` are overwritten, and any
  code that reads `signal` afterwards sees centred data where it expected raw.
- The rule is not memorable from the call site: `signal[mask]` and `signal[[0, 1, 2]]` copy, while `signal[:3]`
  and `signal[..., 0]` do not, so two adjacent lines can behave oppositely.
- It presents as data that changes between two reads with no assignment in between, usually blamed on the
  loader or on caching rather than on a function that was believed to be pure.

## Better

```python
def centre_head(signal, count):
    window = signal[:count].copy()
    window -= window.mean()
    return window
```
