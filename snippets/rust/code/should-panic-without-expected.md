---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: testability
topic: exceptions
tags: [testing, panic, assertions]
keywords: ["#[should_panic]", "#[test]", "is_err()", "assert!(result.is_err())"]
signature: "A test marked should_panic names no expected message, or asserts only is_err, so any failure inside it passes including a mistake in the test itself."
distinguish: "Fine when should_panic carries an expected substring, or the test matches on the specific error variant it is about."
added: 2026-09-23
source: jeremy-wayland
---

# Should panic without expected

## Smell

```rust
#[test]
#[should_panic]
fn rejects_negative_quantity() {
    let order = Order::new(vec![]);
    order.add_line("sku-1", -3);
}

#[test]
fn rejects_unknown_currency() {
    assert!(parse_price("12 XYZ").is_err());
}
```

## Why it's bad

- An empty `vec![]` that the constructor rejects, an index out of bounds, or an `unwrap` on the fixture all
  panic too, so the first test passes whether or not `add_line` checks the sign.
- `is_err()` is the same hole for `Result`: a typo in the input that fails parsing for a different reason
  satisfies it.
- The test stays green after the check it guards is deleted, which is the only thing it existed to catch.

## Better

```rust
#[test]
#[should_panic(expected = "quantity must be positive")]
fn rejects_negative_quantity() {
    Order::new(vec![line("sku-0", 1)]).add_line("sku-1", -3);
}

#[test]
fn rejects_unknown_currency() {
    assert!(matches!(parse_price("12 XYZ"), Err(PriceError::UnknownCurrency(c)) if c == "XYZ"));
}
```
