---
aliases: [missing-super-init, base-class-uninitialised]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: classes
tags: [inheritance, construction, pytorch]
keywords: ["def __init__", "super().__init__", "nn.Module", "class ", "self.layer ="]
signature: "A subclass __init__ never calls super().__init__, so the base class is left uninitialised."
distinguish: "Fine when the base class has no __init__ of its own and the subclass documents that it fully replaces construction."
added: 2026-09-04
source: ernst
---

# Subclass never calls super().__init__

## Smell

```python
class Encoder(nn.Module):
    def __init__(self, width):
        self.layer = nn.Linear(width, width)

    def forward(self, x):
        return self.layer(x)
```

## Why it's bad

- The base class's own setup never runs, so whatever invariants it establishes do not exist — for `nn.Module`
  that is the parameter, buffer, and submodule registries.
- The immediate symptom is an `AttributeError` on the assignment itself, because `nn.Module.__setattr__` looks
  for the registry dict that `__init__` was supposed to create.
- When the base is more forgiving the failure is worse: construction succeeds and the object is subtly hollow,
  so `.parameters()` comes back empty and the optimiser trains nothing at all.
- It presents as a model whose loss never moves, with no error anywhere, which is among the most expensive
  classes of bug to find.

## Better

```python
class Encoder(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.layer = nn.Linear(width, width)

    def forward(self, x):
        return self.layer(x)
```
