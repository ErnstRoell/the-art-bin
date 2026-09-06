---
aliases: [remove-during-iteration, mutate-while-looping]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: mutability
tags: [loops, aliasing, skipped-elements]
keywords: [".remove(", "del ", "for row in rows", ".pop(", "for item in items"]
signature: "Items are removed from a list while a for loop iterates it, so the cursor skips elements."
distinguish: "Fine when iterating a copy such as list(rows), or when appending to a different list than the one being read."
added: 2026-09-04
source: ernst
---

# List mutated while being iterated

## Smell

```python
def drop_empty(rows):
    for row in rows:
        if not row:
            rows.remove(row)
    return rows
```

## Why it's bad

- A list iterator holds an integer position, not a cursor into the elements. Removing an item shifts everything
  after it down one, while the position still advances.
- Every removal therefore skips the following element, so `drop_empty` leaves behind roughly half of a run of
  consecutive empties.
- No exception is raised — lists, unlike dicts, do not detect concurrent modification — so the result is a
  plausible-looking list that is quietly incomplete.
- It presents as a filter that works on the test fixture and fails on real data, because the fixture happens not
  to have two removable items in a row.

## Better

```python
def drop_empty(rows):
    return [row for row in rows if row]
```
