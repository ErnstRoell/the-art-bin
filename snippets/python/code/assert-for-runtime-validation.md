---
aliases: [assert-as-validation]
language: python
python: ">=3.0"
severity: trap
category: correctness
topic: control-flow
tags: [validation, invariants]
keywords: ["assert", "assert not", "-O", "AssertionError"]
signature: "An assert statement is used to validate caller input or external data."
distinguish: "Fine for invariants about internal state the programmer controls, rather than checks on untrusted input."
added: 2026-09-04
source: ernst
---

# Assert used for runtime validation

## Smell

```python
def withdraw(account, amount):
    assert amount > 0, "amount must be positive"
    assert account.balance >= amount
    account.balance -= amount
    return account.balance
```

## Why it's bad

- Running under `python -O` removes every assert, so the validation silently disappears in exactly the
  environment most likely to be production.
- `AssertionError` tells a caller a program invariant broke, not that their argument was wrong, so nobody can
  handle it meaningfully.
- The check reads as defensive code, which stops anyone from adding the real validation.

## Better

```python
def withdraw(account, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if account.balance < amount:
        raise InsufficientFunds(account, amount)
    account.balance -= amount
    return account.balance
```
