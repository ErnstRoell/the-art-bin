---
aliases: [missing-raise-from, exception-chaining-omitted]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: exceptions
tags: [error-handling, tracebacks, chaining]
keywords: ["except", "raise", "from exc", "as exc", "During handling"]
signature: "An exception is raised inside an except block without from, so the traceback reads as a failure in the handler itself."
distinguish: "Fine with from None when the original exception is deliberately hidden as an implementation detail."
added: 2026-09-04
source: ernst
---

# Raise inside except without from

## Smell

```python
def load_config(path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        raise ConfigError(f"{path} is not valid config")
```

## Why it's bad

- Python still chains the exceptions implicitly, but it labels the result *During handling of the above
  exception, another exception occurred*, which describes a handler that crashed rather than an error that was
  deliberately translated.
- A reader debugging the traceback cannot tell whether `ConfigError` is the intended reply to bad JSON or a
  second, unrelated fault in the error path.
- `raise ... from exc` produces *The above exception was the direct cause*, which is the sentence that is
  actually true, and it costs five characters.
- The habit matters most where translation is layered, because three implicit chains in one traceback are
  indistinguishable from three bugs.

## Better

```python
def load_config(path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{path} is not valid config") from exc
```
