---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: control-flow
tags: [iterators, truncation, silent-failure]
keywords: [".zip(", "iter().zip(", "std::iter::zip(", "izip!("]
signature: "Two sequences that should have the same length are zipped without checking, so a mismatch silently truncates to the shorter one."
distinguish: "Fine when one side is deliberately infinite or longer, such as zipping with an unbounded range or a cycle, or when equal lengths were asserted just before."
added: 2026-09-23
source: jeremy-wayland
---

# Zip over unequal lengths

## Smell

```rust
pub fn label_rows(headers: &[String], values: &[String]) -> Vec<(String, String)> {
    headers.iter().cloned().zip(values.iter().cloned()).collect()
}
```

## Why it's bad

- `zip` stops at the shorter iterator and says nothing. A CSV row with a missing trailing field produces a
  record with one column fewer, not an error.
- The truncated record is well-formed, so the problem surfaces downstream as a missing key, far from the row
  that caused it.
- The equal-length assumption is real, and the code does not state it, so neither the compiler nor a reader
  can check it.

## Better

```rust
pub fn label_rows(headers: &[String], values: &[String]) -> Result<Vec<(String, String)>, RowError> {
    if headers.len() != values.len() {
        return Err(RowError::FieldCount { expected: headers.len(), found: values.len() });
    }
    Ok(headers.iter().cloned().zip(values.iter().cloned()).collect())
}
```
