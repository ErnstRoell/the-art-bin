---
aliases: [datetime-now-without-timezone]
language: python
python: ">=3.2"
severity: trap
category: correctness
topic: stdlib-misuse
tags: [datetime, timezones, comparison]
keywords: ["datetime.now()", "utcnow()", "datetime.today()", "last_seen"]
signature: "A moment in time is recorded with datetime.now() and no timezone, producing a naive local timestamp."
distinguish: "Fine when the value is genuinely a local wall-clock date such as a birthday, and never compared across zones."
added: 2026-09-04
source: ernst
---

# Naive datetime for a moment in time

## Smell

```python
from datetime import datetime


def mark_seen(user):
    user.last_seen = datetime.now()


def is_stale(user, cutoff):
    return user.last_seen < cutoff
```

## Why it's bad

- `datetime.now()` returns the local wall clock with no offset attached, so the value does not identify a moment
  in time on its own.
- Two machines in different zones write timestamps that compare as though they were the same clock.
- Comparing a naive value against an aware one raises `TypeError`, so the bug surfaces later, at whichever call
  site first does it properly.
- Around a daylight-saving change the local clock repeats an hour, making ordering wrong rather than merely
  offset.

## Better

```python
from datetime import datetime, timezone


def mark_seen(user):
    user.last_seen = datetime.now(timezone.utc)


def is_stale(user, cutoff):
    return user.last_seen < cutoff
```
