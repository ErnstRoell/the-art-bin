---
aliases: []
language: rust
rust: ">=1.0"
severity: trap
category: correctness
topic: classes
tags: [prototype, clone, struct-update, defaults]
keywords: ["..Default::default()", "name: base.name.clone(),", "retries: base.retries,", "Config {", "fn copy_of(", "fn with_"]
signature: "A copy of a struct is built by listing its fields with a Default fill for the rest, so a field added later silently takes its default instead of the original's value."
distinguish: "Fine when the struct derives Clone and the copy uses struct update syntax from the original, or when resetting unlisted fields to their defaults is the intent."
added: 2026-09-23
source: refactoring.guru
---

# Struct copied by listing its fields

## Smell

```rust
#[derive(Default)]
pub struct RequestConfig {
    pub base_url: String,
    pub timeout: Duration,
    pub retries: u32,
    pub headers: HeaderMap,
    pub proxy: Option<Url>,          // added last month
}

pub fn for_tenant(base: &RequestConfig, tenant: &str) -> RequestConfig {
    let mut headers = base.headers.clone();
    headers.insert("x-tenant", tenant.parse().unwrap());
    RequestConfig {
        base_url: base.base_url.clone(),
        timeout: base.timeout,
        retries: base.retries,
        headers,
        ..Default::default()
    }
}

pub fn with_long_timeout(base: &RequestConfig) -> RequestConfig {
    RequestConfig {
        base_url: base.base_url.clone(),
        timeout: Duration::from_secs(120),
        headers: base.headers.clone(),
        ..Default::default()
    }
}
```

## Why it's bad

- Rust normally rejects a struct literal with a missing field, which is exactly what `..Default::default()`
  switches off. `proxy` was added after these functions, so both quietly drop it, and tenant traffic bypasses
  the proxy.
- `with_long_timeout` also forgot `retries`, so a config meant to be more patient gives up after zero retries.
  Nothing in the code signals the omission.
- Every "copy with a change" re-enumerates the struct, so the number of places that must learn about a new
  field grows with each helper.

## Better

```rust
#[derive(Clone, Default)]
pub struct RequestConfig {
    pub base_url: String,
    pub timeout: Duration,
    pub retries: u32,
    pub headers: HeaderMap,
    pub proxy: Option<Url>,
}

pub fn for_tenant(base: &RequestConfig, tenant: &str) -> RequestConfig {
    let mut config = base.clone();
    config.headers.insert("x-tenant", tenant.parse().unwrap());
    config
}

pub fn with_long_timeout(base: &RequestConfig) -> RequestConfig {
    RequestConfig { timeout: Duration::from_secs(120), ..base.clone() }
}
```

`..base.clone()` fills the remaining fields from the original, so a new field is carried across everywhere
without anyone listing it.
