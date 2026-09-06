---
aliases: [sql-injection-by-concatenation, string-concatenated-sql]
language: python
python: ">=3.0"
severity: bug
category: security
topic: strings
tags: [sql, injection, database]
keywords: ["execute", "SELECT", "WHERE", "+ email", "f\"SELECT", "% (", ".format("]
signature: "A SQL statement is assembled by concatenating or interpolating values into the query text."
distinguish: "Fine when the statement text is a fixed literal and every value reaches the driver as a bound parameter."
added: 2026-09-04
source: ernst
---

# SQL built by string concatenation

## Smell

```python
def find_user(cursor, email):
    cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
    return cursor.fetchone()
```

## Why it's bad

- Any quote character in `email` ends the literal early, so the caller controls the statement rather than a
  value inside it.
- The driver never learns which parts are data, so it cannot escape anything on your behalf.
- It works perfectly for every well-behaved input, which is why it survives review and testing.

## Better

```python
def find_user(cursor, email):
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    return cursor.fetchone()
```
