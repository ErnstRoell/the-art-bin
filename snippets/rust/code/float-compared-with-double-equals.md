---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: numerics
tags: [floating-point, equality, money]
keywords: ["== 0.0", "== 1.0", "!= 0.0", "f64::EPSILON", "assert_eq!(", "as f64 =="]
signature: "Two floating point values that come out of arithmetic are compared with double equals, so representation error decides the answer."
distinguish: "Fine for comparing against a value that was assigned rather than computed, such as a sentinel zero, or when exact bitwise equality is the point, such as in a hash or a cache key."
added: 2026-09-23
source: jeremy-wayland
---

# Float compared with double equals

## Smell

```rust
pub fn is_fully_paid(invoice: &Invoice) -> bool {
    let paid: f64 = invoice.payments.iter().map(|p| p.amount).sum();
    paid == invoice.total
}

#[test]
fn split_three_ways() {
    assert_eq!(split(0.3, 3), 0.1);
}
```

## Why it's bad

- `0.1 + 0.2` is `0.30000000000000004`. Three payments that add up on paper can differ from the total in the
  last bit, and the invoice stays unpaid forever.
- The same arithmetic in a different order can round differently, so the result also depends on the order
  the payments were stored in.
- `f64::EPSILON` is the usual patch and is wrong for any value much larger than one, where the gap between
  neighbouring floats is far bigger than it.

## Better

```rust
pub fn is_fully_paid(invoice: &Invoice) -> bool {
    let paid: i64 = invoice.payments.iter().map(|p| p.amount_cents).sum();
    paid >= invoice.total_cents  // money in integer cents, compared exactly
}

#[test]
fn split_three_ways() {
    assert!((split(0.3, 3) - 0.1).abs() < 1e-12);
}
```
