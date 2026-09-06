---
aliases: [global-keyword-cache, module-level-mutable-state]
language: python
python: ">=3.0"
severity: trap
category: testability
topic: mutability
tags: [global-state, caching, hidden-dependencies]
keywords: ["global ", "_CACHE", "is None:", "_MODEL", "= None"]
signature: "A function uses the global statement to cache or share state, so its result depends on what ran before it."
distinguish: "Fine when the module-level value is a constant that is bound once at import and never rebound."
added: 2026-09-04
source: ernst
---

# Global statement for shared state

## Smell

```python
_MODEL = None


def predict(batch):
    global _MODEL
    if _MODEL is None:
        _MODEL = load_model("checkpoint.pt")
    return _MODEL(batch)
```

## Why it's bad

- The dependency on a loaded model is invisible in the signature, so nothing at the call site says that the
  first call costs a disk read and the rest do not.
- Tests become order-dependent: whichever test runs first fixes the model for the whole session, and a test
  that wants a stub has to reach into the module and reassign a private name.
- Two callers that want different checkpoints cannot both be served, and the second one silently gets the
  first one's model rather than an error.
- It presents as a test suite that passes file by file and fails when run together, or in a different order —
  the failure is in the harness, so the diagnosis starts in the wrong place.

## Better

```python
class Predictor:
    def __init__(self, checkpoint):
        self._checkpoint = checkpoint

    @functools.cached_property
    def model(self):
        return load_model(self._checkpoint)

    def predict(self, batch):
        return self.model(batch)
```
