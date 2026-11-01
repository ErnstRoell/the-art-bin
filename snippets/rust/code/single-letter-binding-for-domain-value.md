---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: naming
tags: [identifiers, domain-language]
keywords: ["let p =", "let c =", "let d =", "let a =", "|x|", "(a, b)"]
signature: "A single letter names a domain value rather than an index or a generic parameter, so the code cannot be read without its definition."
distinguish: "Fine for loop indices, type parameters such as T, conventional mathematics such as x and y coordinates, and one-line closures whose meaning is obvious from the method they are passed to."
added: 2026-09-23
source: jeremy-wayland
---

# Single-letter binding for domain value

## Smell

```rust
pub fn apply_discount(o: &mut Order, c: &Customer) {
    let d = c.tier.discount();
    let t = o.subtotal();
    let p = if t > THRESHOLD { d + 0.05 } else { d };
    o.total = t * (1.0 - p);
}
```

## Why it's bad

- Each letter is a question the reader answers by scrolling up: `d` is a discount, `t` is a subtotal and `p`
  is also a discount, but a percentage one.
- Search does not help. Looking for where the discount is computed finds every `d` in the file.
- The one line that matters, the final assignment, is unreadable on its own, and that line is what shows up
  in a diff.

## Better

```rust
pub fn apply_discount(order: &mut Order, customer: &Customer) {
    let subtotal = order.subtotal();
    let bulk_bonus = if subtotal > BULK_THRESHOLD { 0.05 } else { 0.0 };
    let discount_rate = customer.tier.discount() + bulk_bonus;
    order.total = subtotal * (1.0 - discount_rate);
}
```
