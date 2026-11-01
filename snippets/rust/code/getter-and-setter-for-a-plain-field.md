---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: classes
tags: [encapsulation, accessors, structs]
keywords: ["pub fn get_", "pub fn set_", "fn set_name(&mut self", "self.name = name;", "&self.name"]
signature: "A struct inside one crate exposes a getter and a setter that only read and write one private field, so the ceremony protects no invariant."
distinguish: "Fine on a published crate's public API, where a field would freeze the representation, or where the setter validates or the getter returns a narrower type."
added: 2026-09-23
source: jeremy-wayland
---

# Getter and setter for a plain field

## Smell

```rust
pub(crate) struct RetryPolicy {
    max_attempts: u32,
}

impl RetryPolicy {
    pub(crate) fn get_max_attempts(&self) -> u32 {
        self.max_attempts
    }

    pub(crate) fn set_max_attempts(&mut self, max_attempts: u32) {
        self.max_attempts = max_attempts;
    }
}
```

## Why it's bad

- Both methods do exactly what field access does, so the field is public in everything but syntax, and every
  use is a method call a reader has to open to confirm.
- Inside one crate, `pub(crate)` on the field already decides who may touch it. The accessors add no boundary
  the module system does not, and `&mut self` setters borrow the whole struct where a field write would
  borrow one field.
- Rust convention names a getter after the field, not `get_`, so the style reads as imported from elsewhere.

## Better

```rust
pub(crate) struct RetryPolicy {
    pub(crate) max_attempts: u32,
}
```

When an invariant appears, such as `max_attempts` never being zero, make the field private and write the one
method that enforces it.
