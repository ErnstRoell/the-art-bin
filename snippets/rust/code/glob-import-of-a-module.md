---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: maintainability
topic: imports
tags: [modules, namespaces, glob-imports]
keywords: ["use crate::", "::*;", "use super::*;", "use models::*;", "wildcard_imports"]
signature: "Ordinary modules are imported with a glob, so nothing in the file says where a name comes from and a new public item upstream can make an existing name ambiguous."
distinguish: "Fine for a prelude designed for glob import, for use super star inside a tests module, and for bringing an enum's variants into scope next to the match that uses them."
added: 2026-09-23
source: jeremy-wayland
---

# Glob import of a module

## Smell

```rust
use crate::billing::*;
use crate::inventory::*;
use crate::shipping::*;

pub fn checkout(cart: &Cart) -> Result<Receipt, CheckoutError> {
    reserve(cart)?;
    let quote = estimate(cart)?;
    charge(cart, quote)
}
```

## Why it's bad

- `reserve`, `estimate` and `charge` could come from any of three modules. Without an editor the reader has to
  grep all three, and a code review has no editor.
- When `shipping` later adds its own `pub fn estimate`, this file stops compiling with an ambiguity error, in a
  crate the author of that change may never have opened.
- Globs also pull in every public type and trait, so method resolution can change when an upstream module
  starts exporting a new trait.

## Better

```rust
use crate::billing::charge;
use crate::inventory::reserve;
use crate::shipping;

pub fn checkout(cart: &Cart) -> Result<Receipt, CheckoutError> {
    reserve(cart)?;
    let quote = shipping::estimate(cart)?;
    charge(cart, quote)
}
```
