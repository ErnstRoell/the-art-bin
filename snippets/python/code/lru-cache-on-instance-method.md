---
aliases: [cached-method-leak, lru-cache-holds-self]
language: python
python: ">=3.8"
severity: trap
category: performance
topic: stdlib-misuse
tags: [caching, memory, lifetimes]
keywords: ["@functools.lru_cache", "@lru_cache", "@cache", "def read(self", "cached_property"]
signature: "An lru_cache decorates a method, so the cache holds self as part of every key and keeps each instance alive for the life of the process."
distinguish: "Fine on a module-level function, or with cached_property, which stores the value on the instance and dies with it."
added: 2026-09-04
source: ernst
---

# Lru_cache on an instance method

## Smell

```python
class Loader:
    def __init__(self, root):
        self.root = pathlib.Path(root)

    @functools.lru_cache(maxsize=None)
    def read(self, name):
        return (self.root / name).read_bytes()
```

## Why it's bad

- The decorator wraps the function once, on the class, so there is a single cache shared by every instance and
  `self` is simply the first component of the key.
- That key is a strong reference, so no `Loader` can ever be collected: constructing one per request leaks one
  per request, along with every file body it read.
- `maxsize=None` removes the only bound, but a bounded cache is barely better here, since the eviction policy
  is over a key space that mixes instances and arguments.
- It presents as resident memory that grows linearly with request count and never falls, with the retained
  objects appearing to be held by `functools`, which is a confusing place for a heap dump to point.

## Better

```python
class Loader:
    def __init__(self, root):
        self.root = pathlib.Path(root)
        self._bodies = {}

    def read(self, name):
        if name not in self._bodies:
            self._bodies[name] = (self.root / name).read_bytes()
        return self._bodies[name]
```
