---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: mutability
tags: [memento, undo, snapshots, clone]
keywords: ["let saved_", "let old_", "self.balance = saved", "rollback", "restore(", "#[derive(Clone)]"]
signature: "A caller saves a struct's state for rollback by copying out the fields it happens to know about, so a field added later is never restored."
distinguish: "Fine when the rollback is deliberately partial and says so, such as restoring only the cursor after a failed search."
added: 2026-09-23
source: refactoring.guru
---

# Rollback by saving selected fields

## Smell

```rust
pub struct Account {
    pub balance: Money,
    pub holds: Vec<Hold>,
    pub last_activity: DateTime<Utc>,
    pub daily_withdrawn: Money,        // added for the daily limit
}

pub fn transfer(from: &mut Account, to: &mut Account, amount: Money) -> Result<(), TransferError> {
    let saved_from = (from.balance, from.holds.clone());
    let saved_to = (to.balance, to.holds.clone());

    from.withdraw(amount)?;
    if let Err(e) = to.deposit(amount) {
        (from.balance, from.holds) = saved_from;
        (to.balance, to.holds) = saved_to;
        return Err(e.into());
    }
    Ok(())
}
```

## Why it's bad

- `withdraw` also updates `daily_withdrawn` and `last_activity`, which the rollback does not know exist. After a
  failed transfer the balance is restored and the daily limit still counts money that never left.
- Every caller that wants rollback reimplements it with its own list of fields, and each list goes stale
  independently as `Account` grows.
- It reaches into fields the type would otherwise keep private, so `Account` cannot tighten its encapsulation
  without breaking every rollback.

## Better

```rust
#[derive(Clone)]
pub struct Account {
    balance: Money,
    holds: Vec<Hold>,
    last_activity: DateTime<Utc>,
    daily_withdrawn: Money,
}

pub fn transfer(from: &mut Account, to: &mut Account, amount: Money) -> Result<(), TransferError> {
    let (before_from, before_to) = (from.clone(), to.clone());
    let result = from.withdraw(amount).and_then(|()| to.deposit(amount));
    if result.is_err() {
        *from = before_from;   // the whole state, including fields added later
        *to = before_to;
    }
    result.map_err(Into::into)
}
```

Better still, compute the new states without mutating and assign them only on success, so there is nothing to
roll back.
