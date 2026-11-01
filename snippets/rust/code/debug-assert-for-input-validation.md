---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: control-flow
tags: [validation, release-build, assertions]
keywords: ["debug_assert!(", "debug_assert_eq!(", "debug_assert_ne!(", "--release"]
signature: "A debug_assert checks caller input or external data, so the check vanishes from release builds and bad values flow on unchecked."
distinguish: "Fine for internal invariants that only a bug in this crate could break, where the check is too expensive for release and a release violation would be caught elsewhere."
added: 2026-09-23
source: jeremy-wayland
---

# Debug assert for input validation

## Smell

```rust
pub fn withdraw(account: &mut Account, amount: i64) {
    debug_assert!(amount > 0, "amount must be positive");
    debug_assert!(amount <= account.balance, "insufficient funds");
    account.balance -= amount;
}
```

## Why it's bad

- `debug_assert!` compiles to nothing when `debug-assertions` is off, which is every `--release` build. The
  tests pass and production accepts a negative withdrawal, which is a deposit.
- Even the debug build panics rather than returning an error, so an invalid request from a user crashes the
  handler instead of producing a response.
- The code reads as validated, so a reviewer skims past exactly the lines that do nothing in production.

## Better

```rust
pub fn withdraw(account: &mut Account, amount: i64) -> Result<(), WithdrawError> {
    if amount <= 0 {
        return Err(WithdrawError::NonPositive(amount));
    }
    if amount > account.balance {
        return Err(WithdrawError::InsufficientFunds { balance: account.balance, amount });
    }
    account.balance -= amount;
    Ok(())
}
```
