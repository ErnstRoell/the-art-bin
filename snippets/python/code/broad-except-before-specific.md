---
aliases: [unreachable-except-clause, bad-except-order]
language: python
python: ">=3.0"
severity: bug
category: correctness
topic: exceptions
tags: [error-handling, dead-code, ordering]
keywords: ["except Exception:", "except ValueError:", "try:", "except OSError"]
signature: "A broad except clause is listed before a narrower one, so the narrower handler can never run."
distinguish: "Fine when the broad clause comes last, after every specific type it is meant to backstop."
added: 2026-09-04
source: ernst
---

# Broad except listed before the specific one

## Smell

```python
def parse_port(raw):
    try:
        return int(raw)
    except Exception:
        return DEFAULT_PORT
    except ValueError:
        raise ConfigError("port must be a number")
```

## Why it's bad

- Except clauses are tested top to bottom and the first match wins, so `except ValueError` is dead code that
  the interpreter will never enter.
- `ValueError` is a subclass of `Exception`, which means the clause the author cared about is precisely the one
  that is shadowed.
- The intended behaviour and the actual behaviour are opposites: the author wanted bad input to be loud, and it
  is now silently replaced with a default.
- It reads as though both cases are handled, so the file passes review — the code has the shape of care without
  the effect of it.

## Better

```python
def parse_port(raw):
    try:
        return int(raw)
    except ValueError:
        raise ConfigError("port must be a number")
    except Exception:
        return DEFAULT_PORT
```
