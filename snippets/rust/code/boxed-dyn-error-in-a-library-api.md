---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: exceptions
tags: [error-handling, api-design, library]
keywords: ["Box<dyn Error>", "Box<dyn std::error::Error>", "anyhow::Result", "Result<(), Box<dyn", "downcast_ref::<"]
signature: "A library's public functions return a boxed dynamic error, so callers can only match on its failure modes by downcasting to types the library never promised."
distinguish: "Fine in binaries, scripts, tests and main, where errors are only reported and never matched on, which is what anyhow is for."
added: 2026-09-23
source: jeremy-wayland
---

# Boxed dyn Error in a library API

## Smell

```rust
pub fn fetch_invoice(id: u64) -> Result<Invoice, Box<dyn std::error::Error>> {
    let body = http_get(&format!("/invoices/{id}"))?;
    let invoice = serde_json::from_str(&body)?;
    Ok(invoice)
}

// caller, trying to retry only on network errors:
// if err.downcast_ref::<reqwest::Error>().is_some() { retry() }
```

## Why it's bad

- The signature says "something failed". Whether that was a timeout, a 404 or malformed JSON is knowable
  only by downcasting to concrete types, which makes the library's private dependencies part of its public
  API.
- Swapping `reqwest` for another client silently breaks every caller's downcast, because the compiler has no
  way to know they depended on it.
- As written it is not `Send + Sync`, so a future that holds one across an `.await` cannot be handed to
  `tokio::spawn`, and callers end up re-boxing it to get past the compiler.

## Better

```rust
#[derive(Debug, thiserror::Error)]
pub enum InvoiceError {
    #[error("invoice service unreachable")]
    Network(#[source] reqwest::Error),
    #[error("invoice {0} not found")]
    NotFound(u64),
    #[error("invoice service returned malformed JSON")]
    Malformed(#[from] serde_json::Error),
}

pub fn fetch_invoice(id: u64) -> Result<Invoice, InvoiceError> {
    // ...
}
```
