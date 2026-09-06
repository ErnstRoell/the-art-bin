---
aliases: [missing-prototype, clone-by-listing-attributes]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [prototype, copying, aliasing, drift]
keywords: ["copy.copy", "deepcopy", "Config(", "= base.", "replace(", "vars(self)"]
signature: "A copy of an object is built by listing its fields at the call site, so a field added later is dropped or shared by every copy written that way."
distinguish: "Fine when the result is deliberately a different thing built from a few of the original's values, rather than a copy of it."
added: 2026-09-06
source: refactoring.guru
---

# Copy written field by field

## Smell

```python
class Simulation:
    def __init__(self, steps, seed, solver, tolerance):
        self.steps = steps
        self.seed = seed
        self.solver = solver
        self.tolerance = tolerance
        self.history = []


def with_seed(base, seed):
    return Simulation(base.steps, seed, base.solver, base.tolerance)


def restarted(base):
    clone = Simulation(base.steps, base.seed, base.solver, 1e-6)  # not base.tolerance
    clone.history = base.history                                  # the same list, not a copy
    return clone
```

## Why it's bad

- Copying is a fact about the class, written at the call sites. Two call sites, two different answers about
  what a copy is: one carries the tolerance, the other resets it to a literal that was the default when it was
  written.
- A field added to `Simulation` is copied by neither. The new field takes its constructor default in every
  clone, so the copy is quietly a different object than the original. It presents as a sweep of runs where one
  parameter mysteriously has no effect.
- `restarted` shares `history` rather than copying it, so appending to the clone's history extends the
  original's. This is `shallow-copy-of-nested-data` arrived at by hand, without even the `copy.copy` call that
  would have made it searchable.
- Nothing can be tested. There is no `clone` to assert against, so "copies are complete" is not a property the
  code has anywhere to state.

## Better

```python
@dataclass
class Simulation:
    steps: int
    seed: int
    solver: str
    tolerance: float
    history: list = field(default_factory=list)

    def clone(self, **changes):
        """The one place that knows what copying a Simulation means."""
        return replace(self, history=list(self.history), **changes)


def with_seed(base, seed):
    return base.clone(seed=seed)


def restarted(base):
    return base.clone(history=[])
```

`replace` copies every field the dataclass has, including ones added next year, and the single override of
`history` is the one considered decision about a mutable field. Both call sites become a sentence about what
differs.
