---
aliases: [boolean-trap, flag-argument]
language: python
python: ">=3.0"
severity: taste
category: readability
topic: functions
tags: [api-design, parameters]
keywords: ["True)", "False)", "if flag:", "as_csv", "def export"]
signature: "A boolean parameter picks between two behaviours, so the call site reads as a bare True or False."
distinguish: "Fine when the flag toggles one detail rather than selecting a behaviour, and is keyword-only at the call site."
added: 2026-09-04
source: ernst
---

# Boolean parameter selects the behaviour

## Smell

```python
def export(rows, as_csv):
    if as_csv:
        return to_csv(rows)
    return to_json(rows)


export(rows, True)
```

## Why it's bad

- `export(rows, True)` carries no meaning at the call site, so reading the caller requires opening the callee.
- One function now owns two behaviours that share nothing but a name, and the body is a switch rather than a
  procedure.
- The pattern invites a second flag, at which point half the argument combinations are meaningless and none of
  them are rejected.

## Better

```python
def export_csv(rows):
    return to_csv(rows)


def export_json(rows):
    return to_json(rows)


export_csv(rows)
```
