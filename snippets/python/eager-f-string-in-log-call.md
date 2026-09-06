---
aliases: [f-string-logging, eager-log-formatting]
language: python
python: ">=3.6"
severity: taste
category: performance
topic: strings
tags: [logging, formatting, hot-path]
keywords: ["logger.debug(f", "logging.info(f", "logger.error(f", "%s", "{loss:.4f}"]
signature: "A log call formats an f-string argument, so the message is built even when that level is switched off."
distinguish: "Fine when the level is known to be enabled, or when the call sits outside any hot path and reads better as an f-string."
added: 2026-09-04
source: ernst
---

# Eager f-string in a log call

## Smell

```python
for step, batch in enumerate(loader):
    loss = train_step(batch)
    logger.debug(f"step {step} loss {loss:.4f} batch {batch!r}")
```

## Why it's bad

- The f-string is evaluated before `logger.debug` is called, so every `__format__` and `__repr__` runs at full
  cost and the result is then discarded by a level check.
- `{batch!r}` is the expensive part: repr of a batch may walk a large structure, and in a loop over a data
  loader that is once per step for output nobody will read.
- Passing `%s` placeholders and arguments defers formatting to the handler, which only formats if a handler
  actually wants the record — this is why the logging API takes arguments at all.
- It presents as a job that is measurably slower with `--verbose` even when nothing is written, and as a
  profile where `__repr__` is unaccountably hot.

## Better

```python
for step, batch in enumerate(loader):
    loss = train_step(batch)
    logger.debug("step %s loss %.4f batch %r", step, loss, batch)
```
