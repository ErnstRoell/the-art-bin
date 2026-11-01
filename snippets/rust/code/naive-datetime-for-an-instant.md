---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: typing
tags: [time, timezones, chrono, serialisation]
keywords: ["NaiveDateTime", "Local::now().naive_local()", ".naive_utc()", "Local::now()", "PrimitiveDateTime"]
signature: "A moment in time is stored as a NaiveDateTime or local time with no offset, so the value cannot say which instant it refers to."
distinguish: "Fine for wall-clock values that are meant to float with the reader's timezone, such as an alarm at seven or a shop's opening hours."
added: 2026-09-23
source: jeremy-wayland
---

# Naive datetime for an instant

## Smell

```rust
pub struct AuditEntry {
    pub action: String,
    pub at: chrono::NaiveDateTime,
}

pub fn record(action: &str) -> AuditEntry {
    AuditEntry { action: action.to_owned(), at: chrono::Local::now().naive_local() }
}
```

## Why it's bad

- `naive_local` drops the offset, so the stored value is a local wall-clock reading with no record of which
  local. Two servers in different zones write entries that sort in the wrong order.
- Around a daylight-saving change the same local hour happens twice, so the log cannot say which of two
  instants an entry belongs to.
- Serialised to JSON or a database it carries no offset, so every consumer decides for itself which zone it
  was in, and many guess UTC.

## Better

```rust
pub struct AuditEntry {
    pub action: String,
    pub at: chrono::DateTime<chrono::Utc>,
}

pub fn record(action: &str) -> AuditEntry {
    AuditEntry { action: action.to_owned(), at: chrono::Utc::now() }
}
```
