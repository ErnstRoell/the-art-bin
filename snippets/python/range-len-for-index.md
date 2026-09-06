---
aliases: [range-len-loop, index-loop-over-sequence]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: control-flow
tags: [loops, iteration, enumerate]
keywords: ["range(len(", "for i in range(len", "[i]", "[index]"]
signature: "A loop iterates over range of len only in order to index the sequence it is already walking."
distinguish: "Fine when the loop assigns back into the sequence by index, or steps over it with a stride or a partial range."
added: 2026-09-04
source: ernst
---

# Range over len to index a sequence

## Smell

```python
def total(prices):
    result = 0
    for i in range(len(prices)):
        result += prices[i]
    return result
```

## Why it's bad

- Three concepts — a counter, a length, and a subscript — are spent to express one: visiting each element.
- The index is not used for anything except retrieving the element, so it is pure overhead that the reader must
  nonetheless verify for off-by-one errors.
- It only works on sequences, so the function silently refuses generators, sets, and file handles that
  iterating directly would have accepted for free.
- The form also invites the mistakes it appears to guard against — `range(len(prices) - 1)` and
  `range(1, len(prices))` both look deliberate, and one of them is usually wrong.

## Better

```python
def total(prices):
    result = 0
    for price in prices:
        result += price
    return result
```
