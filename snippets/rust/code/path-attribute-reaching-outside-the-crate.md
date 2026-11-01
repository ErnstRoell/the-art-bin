---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: maintainability
topic: imports
tags: [modules, workspaces, code-sharing]
keywords: ["#[path = \"../", "#[path =", "include!(\"../", "mod shared;"]
signature: "A path attribute or include macro compiles a source file from outside the crate into it, so the same code becomes separate, incompatible types in every crate that does this."
distinguish: "Fine for generated code included from OUT_DIR, or for a path attribute that only rearranges files inside the crate's own source tree."
added: 2026-09-23
source: jeremy-wayland
---

# Path attribute reaching outside the crate

## Smell

```rust
// api/src/main.rs and worker/src/main.rs both contain:
#[path = "../../shared/src/money.rs"]
mod money;

use money::Money;
```

## Why it's bad

- Each crate compiles its own copy of `money.rs`, so `api::money::Money` and `worker::money::Money` are two
  unrelated types. Passing one where the other is expected fails with "expected `Money`, found `Money`".
- Cargo sees no dependency between the crates, so `cargo tree`, publishing and per-package tooling know
  nothing about the shared code.
- The shared file's own imports resolve relative to whichever crate includes it, so it quietly depends on
  both crates having the same dependencies and module layout.

## Better

```rust
// shared/ is a library crate in the workspace, and each consumer's Cargo.toml has
//     shared = { path = "../shared" }
// so there is one Money type, compiled once.
use shared::money::Money;
```
