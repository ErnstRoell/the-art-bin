---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: functions
tags: [borrowing, api-design, slices, clippy]
keywords: ["&String", "&Vec<", "&PathBuf", "&Box<", ": &String)", "ptr_arg"]
signature: "A function takes a reference to String, Vec or PathBuf when it only reads, so callers holding a str, slice, array or Path must allocate an owned value just to call it."
distinguish: "Fine when the function needs the owned type's own API, such as Vec capacity, and the parameter is mutable."
added: 2026-09-23
source: jeremy-wayland
---

# Reference to owned container parameter

## Smell

```rust
pub fn is_valid_sku(sku: &String) -> bool {
    sku.len() == 8 && sku.chars().all(|c| c.is_ascii_alphanumeric())
}

pub fn average(values: &Vec<f64>) -> f64 {
    values.iter().sum::<f64>() / values.len() as f64
}

is_valid_sku(&"AB12CD34".to_string());   // allocation only to satisfy the type
average(&[1.0, 2.0, 3.0].to_vec());
```

## Why it's bad

- `&String` offers nothing `&str` does not, since it is immutable, but it rejects string literals, slices of
  larger strings and `Cow<str>` unless the caller allocates.
- `&Vec<f64>` likewise refuses arrays, sub-slices and data from other containers, so callers write
  `.to_vec()` to call a function that only reads.
- The signature overstates what the function depends on, which is the opposite of what a borrowed parameter
  is for.

## Better

```rust
pub fn is_valid_sku(sku: &str) -> bool {
    sku.len() == 8 && sku.chars().all(|c| c.is_ascii_alphanumeric())
}

pub fn average(values: &[f64]) -> f64 {
    values.iter().sum::<f64>() / values.len() as f64
}

is_valid_sku("AB12CD34");
average(&[1.0, 2.0, 3.0]);
```
