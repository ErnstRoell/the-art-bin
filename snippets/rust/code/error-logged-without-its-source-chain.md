---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: exceptions
tags: [error-handling, logging, observability]
keywords: ['error!("{}", e)', 'error!("failed: {e}")', "e.to_string()", 'format!("{}", err)', "Err(e) =>"]
signature: "An error is logged through its Display text alone, so its source chain never reaches the log."
distinguish: "Fine when the error type has no source, or when it is formatted by something that walks the chain, such as anyhow's alternate format or a tracing field that records the error."
added: 2026-09-23
source: jeremy-wayland
---

# Error logged without its source chain

## Smell

```rust
match sync_account(&client, id).await {
    Ok(()) => {}
    Err(e) => log::error!("sync failed: {}", e),
}
```

## Why it's bad

- `Display` on a well-designed error prints only its own layer — "sync failed: request failed" — and leaves
  the causes to `source()`. Formatting with `{}` stops at the first layer by design.
- The log then says something went wrong without saying what: no DNS failure, no status code, no timeout.
  Diagnosing it means reproducing it.
- The failure presents as a wall of identical one-line errors in production logs, each true and none useful.

## Better

```rust
match sync_account(&client, id).await {
    Ok(()) => {}
    // anyhow::Error: `{:#}` prints the whole chain on one line.
    Err(e) => log::error!("sync failed for {id}: {e:#}"),
}
```
