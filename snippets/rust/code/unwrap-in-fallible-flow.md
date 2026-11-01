---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: exceptions
tags: [error-handling, panic, result]
keywords: [".unwrap()", '.expect("', "parse::<", "panicked at", "called `Result::unwrap()` on an `Err` value"]
signature: "A Result or Option that depends on input, the environment or the network is unwrapped, so an ordinary failure becomes a panic."
distinguish: "Fine in tests, in examples, and where an invariant established a few lines earlier guarantees success and an expect message states that invariant."
added: 2026-09-23
source: jeremy-wayland
---

# Unwrap in fallible flow

## Smell

```rust
pub fn parse_port(value: &str) -> u16 {
    value.trim().parse().unwrap()
}

pub fn read_port() -> u16 {
    parse_port(&std::env::var("PORT").unwrap())
}
```

## Why it's bad

- A missing or mistyped environment variable is an expected condition, and this turns it into a panic with the
  message `called Result::unwrap() on an Err value: ParseIntError { kind: InvalidDigit }` and no mention of
  `PORT`.
- The signature says `u16`, so callers are told this cannot fail and have no way to recover or to report a
  better message.
- In a server a panic unwinds the task or thread; with `panic = "abort"` it takes the whole process down over
  one bad request.

## Better

```rust
#[derive(Debug, thiserror::Error)]
pub enum PortError {
    #[error("PORT is not set")]
    Missing(#[from] std::env::VarError),
    #[error("PORT is not a port number")]
    Invalid(#[from] std::num::ParseIntError),
}

pub fn read_port() -> Result<u16, PortError> {
    Ok(std::env::var("PORT")?.trim().parse()?)
}
```
