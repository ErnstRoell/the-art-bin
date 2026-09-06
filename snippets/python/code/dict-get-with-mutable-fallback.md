---
aliases: [get-default-discarded, append-to-get-default]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: stdlib-misuse
tags: [dictionaries, defaults, grouping]
keywords: [".get(key, [])", ".get(", ").append(", "setdefault", "defaultdict"]
signature: "A value is appended to the fallback object returned by dict.get, so the new item is dropped instead of stored."
distinguish: "Fine when the fallback is only read, as in a lookup that returns an empty list to its caller."
added: 2026-09-04
source: ernst
---

# Append to a dict.get fallback

## Smell

```python
def group(pairs):
    buckets = {}
    for key, value in pairs:
        buckets.get(key, []).append(value)
    return buckets
```

## Why it's bad

- `get` returns the fallback without storing it, so the freshly created list is appended to and then
  immediately garbage collected.
- `buckets` therefore stays empty for every key, and because no key is ever inserted the fallback branch is
  taken every single time — the function is a no-op that returns `{}`.
- There is no error, and the shape of the code is exactly right, so it reads as correct grouping; only the
  return value disagrees.
- It presents as an empty result from a function that visibly iterated its input, which sends people to check
  whether `pairs` was empty rather than to the `get` call.

## Better

```python
import collections


def group(pairs):
    buckets = collections.defaultdict(list)
    for key, value in pairs:
        buckets[key].append(value)
    return dict(buckets)
```
