---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: performance
topic: control-flow
tags: [iterators, allocation, laziness]
keywords: [".collect::<Vec<_>>()", ".collect::<Vec<", ").into_iter()", ".collect();", ".len() > 0"]
signature: "An iterator is collected into a Vec only to be iterated, counted or searched once, so the code allocates a whole intermediate collection it never keeps."
distinguish: "Fine when the collection is iterated more than once, must outlive a borrow the iterator holds, or is needed to release a lock or file before continuing."
added: 2026-09-23
source: jeremy-wayland
---

# Needless collect before iterating

## Smell

```rust
pub fn has_overdue(invoices: &[Invoice], today: Date) -> bool {
    let overdue: Vec<&Invoice> = invoices.iter().filter(|i| i.due < today).collect();
    overdue.len() > 0
}

pub fn total_paid(invoices: &[Invoice]) -> Money {
    let paid = invoices.iter().filter(|i| i.paid).collect::<Vec<_>>();
    paid.into_iter().map(|i| i.amount).sum()
}
```

## Why it's bad

- The `Vec` is built, used once, and dropped. It costs an allocation proportional to the matches, where the
  question needs none.
- `has_overdue` visits every invoice to count them, when the answer is known at the first overdue one.
- The intermediate names suggest the collection matters for something later, so a reader looks for a second
  use that is not there.

## Better

```rust
pub fn has_overdue(invoices: &[Invoice], today: Date) -> bool {
    invoices.iter().any(|i| i.due < today)
}

pub fn total_paid(invoices: &[Invoice]) -> Money {
    invoices.iter().filter(|i| i.paid).map(|i| i.amount).sum()
}
```
