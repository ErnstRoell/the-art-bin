---
aliases: [exhausted-generator, iterator-reused]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: control-flow
tags: [generators, iterators, exhaustion]
keywords: ["(row for row in", "map(", "filter(", "sum(", "max(", "zip("]
signature: "A generator is iterated a second time after being exhausted, so the second pass sees nothing."
distinguish: "Fine when the source is a list, tuple, or other re-iterable sequence rather than a generator, map, or filter object."
added: 2026-09-04
source: ernst
---

# Generator consumed twice

## Smell

```python
def summarise(rows):
    scores = (row["score"] for row in rows)
    best = max(scores)
    mean = sum(scores) / len(rows)
    return best, mean
```

## Why it's bad

- A generator is an iterator over itself: `max` drives it to exhaustion, and the object that remains is a valid
  but empty iterable.
- `sum` of nothing is `0`, so `mean` comes back as exactly `0.0` — no exception, no warning, just a wrong
  number in a plausible position.
- The same shape appears with `map`, `filter`, `zip`, `csv.reader`, and open file handles, and it only misfires
  when someone adds a *second* use to a function that had one.
- It presents as a statistic pinned to zero, or in the `min`/`max` case as a `ValueError` on an empty sequence
  raised against an input that visibly has rows.

## Better

```python
def summarise(rows):
    scores = [row["score"] for row in rows]
    return max(scores), sum(scores) / len(scores)
```
