---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: maintainability
topic: control-flow
tags: [match, exhaustiveness, enums]
keywords: ["_ =>", "_ => {}", "_ => false", "_ => None", "_ => unreachable!()"]
signature: "A match over an enum the crate owns ends in a wildcard arm, so a variant added later is silently handled by the fallback instead of being flagged by the compiler."
distinguish: "Fine for foreign or non_exhaustive enums, for matches on integers and strings, and where the fallback is correct for every variant that could ever be added."
added: 2026-09-23
source: jeremy-wayland
---

# Wildcard arm on an owned enum

## Smell

```rust
pub enum Plan { Free, Pro, Team }

pub fn seat_limit(plan: &Plan) -> u32 {
    match plan {
        Plan::Team => 50,
        Plan::Pro => 5,
        _ => 1,
    }
}
```

## Why it's bad

- Exhaustive matching is the reason to model plans as an enum. The wildcard switches it off for this function.
- When `Plan::Enterprise` is added, every exhaustive `match` in the crate becomes a compile error pointing at
  work to do. This one compiles and gives enterprise customers one seat.
- The bug presents as a support ticket from the most valuable customer, filed against billing rather than this
  function.

## Better

```rust
pub enum Plan { Free, Pro, Team }

pub fn seat_limit(plan: &Plan) -> u32 {
    match plan {
        Plan::Team => 50,
        Plan::Pro => 5,
        Plan::Free => 1,
    }
}
```
