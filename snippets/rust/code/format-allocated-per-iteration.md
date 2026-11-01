---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: performance
topic: strings
tags: [allocation, formatting, strings]
keywords: ["push_str(&format!(", "+= &format!(", "out = out +", "s = format!(\"{}{}\", s,", ".to_string() +"]
signature: "A string is grown inside a loop by formatting each piece into a temporary String, so every iteration allocates and copies a value that is immediately thrown away."
distinguish: "Fine outside hot paths and loops, where one format call reads more clearly than write and the allocation is irrelevant."
added: 2026-09-23
source: jeremy-wayland
---

# Format allocated per iteration

## Smell

```rust
pub fn to_csv(rows: &[Row]) -> String {
    let mut out = String::new();
    for row in rows {
        out.push_str(&format!("{},{},{}\n", row.id, row.name, row.amount));
    }
    out
}

pub fn joined(ids: &[u64]) -> String {
    let mut s = String::new();
    for id in ids {
        s = format!("{s}{id},");
    }
    s
}
```

## Why it's bad

- `format!` returns a fresh `String`. In `to_csv` each row allocates one only to copy it into `out` and free
  it, so the loop does twice the allocation work it needs.
- `joined` is worse: it rebuilds the whole accumulated string on every step, so the total work is quadratic in
  the output length.
- Both hide a trailing separator problem, which the manual loop then has to patch up afterwards.

## Better

```rust
use std::fmt::Write;

pub fn to_csv(rows: &[Row]) -> String {
    let mut out = String::new();
    for row in rows {
        writeln!(out, "{},{},{}", row.id, row.name, row.amount).unwrap(); // writing to a String cannot fail
    }
    out
}

pub fn joined(ids: &[u64]) -> String {
    ids.iter().map(u64::to_string).collect::<Vec<_>>().join(",")
}
```
