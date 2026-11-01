---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: naming
tags: [identifiers, types, refactoring-residue]
keywords: ["_vec", "_list", "_map", "_str", "_arr", "_ms"]
signature: "An identifier carries a type or unit suffix that the value does not have, usually left over from before a refactor."
distinguish: "Fine when the suffix is accurate and adds something the type does not say, such as a unit on a plain integer."
added: 2026-09-23
source: jeremy-wayland
---

# Type suffix contradicts the value

## Smell

```rust
pub struct Registry {
    users_vec: HashMap<UserId, User>,
    timeout_ms: Duration,
    name_str: Option<String>,
}

pub fn active_list(registry: &Registry) -> impl Iterator<Item = &User> {
    registry.users_vec.values().filter(|user| user.active)
}
```

## Why it's bad

- `users_vec` is a map and `active_list` returns an iterator, so a reader who trusts the name reaches for
  indexing and `len` and gets a compile error, or worse, reasons about order that does not exist.
- `timeout_ms` is a `Duration`, which already carries its unit, so the suffix invites someone to pass it to an
  API expecting a bare millisecond count after an `as_secs()` they misread.
- Suffixes rot silently, because the compiler checks types and never names.

## Better

```rust
pub struct Registry {
    users: HashMap<UserId, User>,
    timeout: Duration,
    name: Option<String>,
}

pub fn active_users(registry: &Registry) -> impl Iterator<Item = &User> {
    registry.users.values().filter(|user| user.active)
}
```
