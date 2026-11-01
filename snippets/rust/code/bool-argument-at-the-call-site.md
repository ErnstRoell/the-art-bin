---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: readability
topic: functions
tags: [api-design, enums, call-sites]
keywords: [", true)", ", false)", "(true,", "(false,", ": bool) ->", ": bool) {"]
signature: "A bool parameter picks between two behaviours, so the call site reads as a bare true or false that means nothing without the signature."
distinguish: "Fine when the parameter is a plain value rather than a mode, such as set_visible taking visible, where the function name already says what true means."
added: 2026-09-23
source: jeremy-wayland
---

# Bool argument at the call site

## Smell

```rust
pub fn export(report: &Report, include_drafts: bool, compress: bool) -> Vec<u8> {
    // ...
}

let archive = export(&report, false, true);
```

## Why it's bad

- `export(&report, false, true)` cannot be read without opening the signature, and swapping the two literals
  still compiles.
- Rust has no named arguments, so the usual reader's crutch — `compress=True` — is unavailable; the only help is
  an editor's inlay hints, which a code review does not show.
- A third mode, such as drafts only, does not fit in a `bool` and forces a second parameter whose combinations
  with the first include nonsense.

## Better

```rust
pub enum Drafts { Include, Exclude }
pub enum Compression { None, Gzip }

pub fn export(report: &Report, drafts: Drafts, compression: Compression) -> Vec<u8> {
    // ...
}

let archive = export(&report, Drafts::Exclude, Compression::Gzip);
```
