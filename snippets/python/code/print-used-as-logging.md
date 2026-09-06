---
aliases: [print-debugging-left-in, print-instead-of-logger]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: io
tags: [logging, observability, output]
keywords: ["print(", 'print("step"', "print(f", "flush=True"]
signature: "A library or long-running job reports progress with print, so the output carries no level, timestamp, or destination."
distinguish: "Fine in a script or command-line entry point whose actual product is text on standard output."
added: 2026-09-04
source: ernst
---

# Print used as logging

## Smell

```python
def train(loader):
    print("starting training")
    for step, batch in enumerate(loader):
        loss = train_step(batch)
        print("step", step, "loss", loss)
    print("done")
```

## Why it's bad

- There is no level, so the per-step line cannot be turned off separately from the two that matter, and the
  only volume control available is deleting code.
- There is no destination either: everything goes to stdout, mixed in with whatever the program is actually
  meant to emit, so piping the useful output to a file drags the progress noise along with it.
- No timestamps and no logger name means a captured run cannot answer "when" or "from where", which are the two
  questions asked of every job log.
- It presents as a caller who wants to silence the library and cannot, and as CI output where the interesting
  failure is buried under fifty thousand step lines.

## Better

```python
import logging

logger = logging.getLogger(__name__)


def train(loader):
    logger.info("starting training")
    for step, batch in enumerate(loader):
        loss = train_step(batch)
        logger.debug("step %s loss %s", step, loss)
    logger.info("done")
```
