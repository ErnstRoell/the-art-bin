---
aliases: [try-import-except-pass, silent-optional-import]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: imports
tags: [optional-dependencies, silent-failure, error-messages]
keywords: ["except ImportError", "try:", "import matplotlib", "pass", "NameError"]
signature: "An optional import is wrapped in try and except ImportError with no fallback, so the name is simply absent later."
distinguish: "Fine when the except branch binds a working fallback or sets a flag that callers check before use."
added: 2026-09-04
source: ernst
---

# Optional import swallowed

## Smell

```python
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass


def plot_losses(losses):
    plt.plot(losses)
    plt.savefig("loss.png")
```

## Why it's bad

- The `except` branch leaves `plt` unbound, so the missing dependency is converted from a clear `ImportError`
  at startup into a `NameError` at an arbitrary later moment.
- `NameError: name 'plt' is not defined` names a local variable, not a package, so the reader's first thought
  is a typo rather than an uninstalled extra.
- The delay is the real cost: the failure lands after the training run, at the point where results are being
  written, which is the most expensive place to discover a packaging problem.
- The two honest options are both cheap — fail at import with a message naming the extra, or bind a fallback —
  and `pass` is neither.

## Better

```python
try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise ImportError("plotting requires the [plot] extra") from exc


def plot_losses(losses):
    plt.plot(losses)
    plt.savefig("loss.png")
```
