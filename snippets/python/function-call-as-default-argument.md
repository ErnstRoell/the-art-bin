---
aliases: [call-in-default-argument, evaluated-default]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: functions
tags: [defaults, import-time, datetime]
keywords: ["=datetime.now()", "=[]", "=dict()", "def ", "=time.time()"]
signature: "A default argument is a function call, so it is evaluated once at definition time and frozen for the life of the process."
distinguish: "Fine in frameworks such as FastAPI where a call in the default is the documented way to declare a dependency."
added: 2026-09-04
source: ernst
---

# Function call as a default argument

## Smell

```python
from datetime import datetime, timezone


def record(name, started=datetime.now(timezone.utc)):
    return {"name": name, "started": started}
```

## Why it's bad

- Defaults are evaluated once, when the `def` statement runs at import, not on each call — so `started` is the
  moment the module was first imported.
- Every record written by a long-lived process therefore carries the same timestamp, and the value is *nearly*
  right, which is why it survives review and testing.
- The error scales with uptime: in a test run the import and the call are milliseconds apart, and in production
  they are days.
- It presents as timestamps that cluster impossibly, all equal to a deploy time, which looks like a clock or a
  database problem rather than a signature.

## Better

```python
from datetime import datetime, timezone


def record(name, started=None):
    started = datetime.now(timezone.utc) if started is None else started
    return {"name": name, "started": started}
```
