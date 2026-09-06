---
aliases: [tensor-cat-in-loop, quadratic-concatenation]
language: python
python: ">=3.0"
severity: taste
category: performance
topic: numerics
tags: [numpy, pytorch, allocation, accumulation]
keywords: ["torch.cat", "np.concatenate", "np.append", "torch.empty(0", "out = torch.cat"]
signature: "An array or tensor grows by concatenation inside a loop, so every step reallocates and copies everything accumulated so far."
distinguish: "Fine when the loop runs a handful of times, or when the pieces must be combined pairwise for a reason other than accumulation."
added: 2026-09-04
source: ernst
---

# Array concatenated in a loop

## Smell

```python
def collect(loader, model):
    out = torch.empty(0, 128)
    for batch in loader:
        out = torch.cat([out, model(batch)])
    return out
```

## Why it's bad

- Neither `torch.cat` nor `np.concatenate` can extend an existing buffer, so each iteration allocates a fresh
  array and copies the entire accumulation into it.
- Total work is quadratic in the number of steps: a thousand batches of the same size perform about five
  hundred times as much copying as a single concatenation would.
- Peak memory is also roughly double the result, since the old and new buffers coexist during the copy — and on
  a GPU that is where it fails rather than merely slows.
- It presents as a collection pass that costs more than the forward pass that produced the data, and that gets
  disproportionately worse as the dataset grows, which reads as an I/O problem.

## Better

```python
def collect(loader, model):
    chunks = [model(batch) for batch in loader]
    return torch.cat(chunks)
```
