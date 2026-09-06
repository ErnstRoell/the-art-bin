---
aliases: [init-does-io, heavy-constructor]
language: python
python: ">=3.0"
severity: trap
category: testability
topic: classes
tags: [construction, side-effects, dependencies]
keywords: ["def __init__", "open(", ".read_text()", "torch.load", "requests.get", ".glob("]
signature: "A constructor reads files or opens connections, so the object cannot be created without its environment."
distinguish: "Fine when construction is deferred to a method or a cached property, or when the type exists precisely to own that resource."
added: 2026-09-04
source: ernst
---

# Constructor does I/O

## Smell

```python
class Dataset:
    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.files = sorted(self.root.glob("*.pt"))
        self.tensors = [torch.load(path) for path in self.files]
        self.stats = requests.get(f"{STATS_URL}/{root}").json()
```

## Why it's bad

- Constructing the object and using it are now the same event, so there is no way to test any method here
  without a populated directory and a reachable server.
- Failures surface as exceptions from `__init__`, which means a half-built object and a traceback that points
  at construction rather than at whichever piece of the environment was missing.
- It defeats every substitution point: a test cannot pass in three tensors, and a caller cannot construct the
  object cheaply to ask it one question about its `root`.
- It presents as a test suite that needs fixture files checked into the repository, and as import-time or
  startup-time slowness that nobody can attribute to a particular line.

## Better

```python
class Dataset:
    def __init__(self, root, tensors=None):
        self.root = pathlib.Path(root)
        self._tensors = tensors

    @property
    def tensors(self):
        if self._tensors is None:
            self._tensors = [torch.load(p) for p in sorted(self.root.glob("*.pt"))]
        return self._tensors
```
