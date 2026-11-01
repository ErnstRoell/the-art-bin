---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: control-flow
tags: [iteration, indexing, bounds-checks]
keywords: ["for i in 0..", ".len() {", "[i]", "[i + 1]", "needless_range_loop"]
signature: "A loop ranges over zero to len only to index the slice it is already walking, so every access is a bounds-checked lookup instead of an iterator."
distinguish: "Fine when the index itself is the data, or when the loop reads several positions at once in a way windows, chunks or zip do not express."
added: 2026-09-23
source: jeremy-wayland
---

# Range over len for indexing

## Smell

```rust
pub fn total_weight(items: &[Item], quantities: &[u32]) -> u64 {
    let mut total = 0;
    for i in 0..items.len() {
        total += items[i].weight as u64 * quantities[i] as u64;
    }
    total
}
```

## Why it's bad

- The reader has to check that `i` is only used to index, and that `quantities` is at least as long as `items`,
  before they know what the loop does.
- If `quantities` is shorter, this panics with an index out of bounds rather than stating the length
  requirement anywhere.
- Every `[i]` is a bounds check the optimiser may or may not remove, where an iterator has none to remove.

## Better

```rust
pub fn total_weight(items: &[Item], quantities: &[u32]) -> u64 {
    assert_eq!(items.len(), quantities.len(), "one quantity per item");
    items.iter().zip(quantities).map(|(item, &qty)| item.weight as u64 * qty as u64).sum()
}
```
