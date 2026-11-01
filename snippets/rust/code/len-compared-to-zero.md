---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: control-flow
tags: [collections, idiom, clippy]
keywords: [".len() == 0", ".len() > 0", ".len() != 0", ".len() >= 1", "len_zero"]
signature: "Emptiness is tested by comparing len against zero instead of calling is_empty."
distinguish: "Fine when the comparison is to a count that happens to be written as a variable or constant, such as len at least a required minimum."
added: 2026-09-23
source: jeremy-wayland
---

# Len compared to zero

## Smell

```rust
pub fn summary(order: &Order) -> String {
    if order.lines.len() == 0 {
        return "empty order".to_owned();
    }
    if order.notes.len() > 0 {
        return format!("{} lines, with notes", order.lines.len());
    }
    format!("{} lines", order.lines.len())
}
```

## Why it's bad

- The question is "is it empty", and `is_empty` says that; `len() == 0` asks for a number and makes the reader
  compare it.
- `len() > 0` versus `len() >= 1` versus `len() != 0` are three spellings of one test, so readers pause over
  whether the difference means something.
- Not every collection's `len` is cheap. Some iterators and custom types compute it, where `is_empty` can stop
  at the first element.

## Better

```rust
pub fn summary(order: &Order) -> String {
    if order.lines.is_empty() {
        return "empty order".to_owned();
    }
    if !order.notes.is_empty() {
        return format!("{} lines, with notes", order.lines.len());
    }
    format!("{} lines", order.lines.len())
}
```
