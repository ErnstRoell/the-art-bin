---
aliases: [unstrict-zip, silent-zip-truncation]
language: python
python: ">=3.10"
severity: trap
category: correctness
topic: control-flow
tags: [iteration, silent-truncation, pairing]
keywords: ["zip(", "for x, y in zip", "strict=True", "zip(inputs, targets)"]
signature: "Two sequences are zipped without strict, so a length mismatch silently truncates to the shorter one."
distinguish: "Fine when one argument is deliberately unbounded or longer, as with itertools.count or a cycle."
added: 2026-09-04
source: ernst
---

# Zip without strict

## Smell

```python
def pair_up(inputs, targets):
    pairs = []
    for image, label in zip(inputs, targets):
        pairs.append((image, label))
    return pairs
```

## Why it's bad

- `zip` stops at the shortest argument and says nothing, so a missing label does not raise — it drops an image,
  and every image after it keeps its own label.
- If the two sequences came from separate sources, a mismatch usually means they are also *misaligned*, and
  truncation hides the far worse problem that the pairs are wrong.
- The result has a plausible length, so no assertion downstream catches it; the training run simply learns from
  fewer, and possibly mislabelled, examples.
- It presents as a metric that is slightly and inexplicably worse than the same code produced last month, which
  is a fault nobody looks for in a `zip`.

## Better

```python
def pair_up(inputs, targets):
    pairs = []
    for image, label in zip(inputs, targets, strict=True):
        pairs.append((image, label))
    return pairs
```
