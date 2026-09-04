---
aliases: [import-time-side-effect, work-at-import]
language: python
python: ">=3.0"
severity: trap
category: maintainability
topic: imports
tags: [import-time, global-state, configuration]
keywords: ["torch.manual_seed", "logging.basicConfig", "np.random.seed", "DEVICE =", "warnings.filterwarnings"]
signature: "Importing the module seeds a generator, selects a device, or configures logging as a side effect."
distinguish: "Fine for binding constants and registering classes, which is work that only affects the module's own namespace."
added: 2026-09-04
source: ernst
---

# Side effect at import time

## Smell

```python
import logging

import torch

torch.manual_seed(0)
logging.basicConfig(level=logging.DEBUG)
DEVICE = torch.device("cuda")


def train(model):
    return model.to(DEVICE)
```

## Why it's bad

- These three statements reach outside the module: they reseed a process-wide generator, install a root log
  handler, and require a GPU — all as a consequence of the word `import`.
- Import order becomes semantically significant. Whoever imports first wins the logging configuration, and any
  module imported afterwards that reseeds will silently undo this one.
- `torch.device("cuda")` runs before anything can decide whether a GPU exists, so importing the module for a
  docstring or a type annotation fails on a laptop.
- It presents as behaviour that changes when an unrelated import is added or reordered, and as a test suite
  whose logging output depends on which test file was collected first.

## Better

```python
import logging

import torch

logger = logging.getLogger(__name__)


def train(model, device, seed=0):
    torch.manual_seed(seed)
    return model.to(device)
```
