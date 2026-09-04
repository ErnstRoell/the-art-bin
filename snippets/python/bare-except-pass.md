---
aliases: [swallowed-exception]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: exceptions
tags: [error-handling, silent-failure]
keywords: ["except:", "except Exception", "pass", "try"]
signature: "An except clause with no type and an empty body discards every error silently."
distinguish: "Fine when the handler names the exceptions it expects and either recovers from them or re-raises."
added: 2026-09-04
source: ernst
---

# Bare except that passes

## Smell

```python
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        pass
```

## Why it's bad

- A bare `except` catches everything, including `KeyboardInterrupt` and `MemoryError`, which were never yours
  to handle.
- The function returns `None` on failure without saying so, pushing the error to whoever uses the result.
- Nothing is logged, so the only evidence is a downstream `AttributeError` on `None` in unrelated code.

## Better

```python
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("could not load config %s: %s", path, exc)
        raise ConfigError(path) from exc
```
