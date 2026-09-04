---
aliases: [log-str-of-exception, stringified-exception]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: exceptions
tags: [logging, tracebacks, diagnosability]
keywords: ["str(exc)", "str(e)", "logger.error", "except", "{e}"]
signature: "An except block logs the exception as a string, so its type and traceback never reach the log."
distinguish: "Fine when the log call is logger.exception or passes exc_info, which records the traceback alongside the message."
added: 2026-09-04
source: ernst
---

# Exception logged as a string

## Smell

```python
def sync(records):
    try:
        push(records)
    except HTTPError as exc:
        logger.error(f"sync failed: {exc}")
        return False
```

## Why it's bad

- `str(exc)` is only the message argument, so the log loses the type, the chained cause, and every frame of the
  traceback — the three things you actually need.
- Plenty of exceptions stringify to almost nothing: a `KeyError` gives the bare key, and an exception raised
  with no arguments gives an empty string, so the log line reads `sync failed: `.
- The failure presents as a log file full of entries that confirm something broke and cannot say where, which
  sends the investigation to reproducing rather than reading.
- `logger.exception` takes the same message and attaches the active traceback automatically, so the fix removes
  code rather than adding it.

## Better

```python
def sync(records):
    try:
        push(records)
    except HTTPError:
        logger.exception("sync failed")
        return False
```
