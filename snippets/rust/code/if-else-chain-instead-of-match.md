---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: control-flow
tags: [match, lookup-table, exhaustiveness]
keywords: ["} else if code ==", "} else if status ==", "if kind ==", "} else if", "== \""]
signature: "A chain of if and else-if branches tests one value for equality against constants, so a match or a table that states the mapping is written as control flow."
distinguish: "Fine when the branches test different values or ranges with genuinely different logic in each, which a match would not make clearer."
added: 2026-09-23
source: jeremy-wayland
---

# If-else chain instead of match

## Smell

```rust
pub fn status_text(code: u16) -> &'static str {
    let text;
    if code == 200 {
        text = "OK";
    } else if code == 404 {
        text = "Not Found";
    } else if code == 500 {
        text = "Internal Server Error";
    } else {
        text = "Unknown";
    }
    text
}
```

## Why it's bad

- The mapping is data, but it is written as control flow, so reading it means following each branch to see
  that every one only assigns `text`.
- A duplicated constant — two `code == 404` branches — compiles and the second is dead. A `match` reports it
  as an unreachable pattern.
- With an enum instead of a `u16`, a chain gives up exhaustiveness checking entirely, where a `match` would
  name the missing variant.

## Better

```rust
pub fn status_text(code: u16) -> &'static str {
    match code {
        200 => "OK",
        404 => "Not Found",
        500 => "Internal Server Error",
        _ => "Unknown",
    }
}
```
